#!/usr/bin/env python3
"""Verify Phase13 live native-subagent pilot artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import ROOT, compute_source_snapshot, is_relative_to, load_json, source_runtime_artifact_violations
    from generate_phase13_live_pilot import DEFAULT_PILOT, DEFAULT_RUN_ROOT, RUN_ID, REGISTRY
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import ROOT, compute_source_snapshot, is_relative_to, load_json, source_runtime_artifact_violations  # type: ignore  # noqa: E402
    from generate_phase13_live_pilot import DEFAULT_PILOT, DEFAULT_RUN_ROOT, RUN_ID, REGISTRY  # type: ignore  # noqa: E402

RUN_SCHEMA_VERSION = "ppg-phase13-run-state/v0.1"
VERDICTS = {"accept", "accept_with_limitations", "needs_repair", "reject"}
VERDICT_PARSE_ORDER = ["accept_with_limitations", "needs_repair", "reject", "accept"]
BANNED_CLAIMS = ["final manuscript complete", "final paper complete", "submission ready", "ready to submit", "publication ready"]
LEGACY_ACTIVE = ["legacy department yxj-paper-os route revived", "legacy department-loop yxj-paper-os route revived", "$yxj-plugin-incubator used", "$yxj-plugin-incubator revived"]
RECURSIVE_CLAIMS = ["i will dispatch", "i can dispatch", "spawn subagents", "mark this stage complete", "mark final completion", "controller completion authority"]
WEAK_GENERIC = ["looks good", "seems fine", "generic analysis", "no specific evidence", "not enough context but"]


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024, ), b""):
            h.update(chunk)
    return h.hexdigest()


def is_regular_file_no_symlink(path: Path) -> bool:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return False
    return not path.is_symlink() and stat.S_ISREG(st.st_mode)


def safe_run_ref(run_root: Path, ref: Any, code: str, context: str) -> tuple[Path | None, list[str]]:
    if not isinstance(ref, str) or not ref.strip():
        return None, [issue(code, f"{context}={ref}")]
    raw = Path(ref)
    if raw.is_absolute() or ref.startswith("~") or "\\" in ref or "\x00" in ref or any(part in {"", ".", ".."} for part in ref.split("/")):
        return None, [issue(code, f"{context}={ref}")]
    path = run_root / ref
    try:
        resolved = path.resolve(strict=False)
        resolved.relative_to(run_root.resolve(strict=True))
    except Exception:  # noqa: BLE001
        return None, [issue(code, f"{context}={ref}")]
    if path.is_symlink() or resolved.is_symlink():
        return None, [issue("E_PHASE13_UNSAFE_REF", f"{context} symlink {ref}")]
    return path, []


def existing_file(run_root: Path, ref: Any, code: str, context: str, errors: list[str]) -> Path | None:
    path, ref_errors = safe_run_ref(run_root, ref, code, context)
    errors.extend(ref_errors)
    if path is not None and not is_regular_file_no_symlink(path):
        errors.append(issue(code, f"{context} missing safe regular file {ref}"))
        return None
    return path


def load_json_file(path: Path | None, errors: list[str], code: str) -> Any | None:
    if path is None:
        return None
    if not is_regular_file_no_symlink(path):
        errors.append(issue(code, rel(path)))
        return None
    try:
        return load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(issue("E_PHASE13_JSON_PARSE", f"{rel(path)}: {exc}"))
        return None


def load_jsonl_file(path: Path | None, errors: list[str], code: str) -> list[dict[str, Any]] | None:
    if path is None:
        return None
    if not is_regular_file_no_symlink(path):
        errors.append(issue(code, rel(path)))
        return None
    records: list[dict[str, Any]] = []
    try:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                errors.append(issue("E_PHASE13_JSON_PARSE", f"{rel(path)}:{lineno} not object"))
                continue
            records.append(value)
    except Exception as exc:  # noqa: BLE001
        errors.append(issue("E_PHASE13_JSON_PARSE", f"{rel(path)}: {exc}"))
        return None
    return records


def thread_rows_by_stage_lane(threads: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("stage_id")), str(row.get("lane"))): row
        for row in threads
        if isinstance(row, dict)
    }


def validate_run_root_before_reads(run_root: Path, source_root: Path) -> list[str]:
    if run_root.is_symlink():
        return [issue("E_PHASE13_RUN_ROOT", f"run root must not be symlink: {run_root}")]
    try:
        st = run_root.lstat()
    except FileNotFoundError:
        return [issue("E_PHASE13_RUN_ROOT", f"missing {run_root}")]
    if not stat.S_ISDIR(st.st_mode):
        return [issue("E_PHASE13_RUN_ROOT", f"not directory {run_root}")]
    try:
        resolved = run_root.resolve(strict=True)
    except Exception as exc:  # noqa: BLE001
        return [issue("E_PHASE13_RUN_ROOT", f"invalid {run_root}: {exc}")]
    errors: list[str] = []
    if not is_relative_to(resolved, (ROOT / "runs").resolve(strict=True)):
        errors.append(issue("E_PHASE13_RUN_ROOT", f"outside runs {run_root}"))
    if is_relative_to(resolved, source_root) or resolved == source_root:
        errors.append(issue("E_PHASE13_RUN_ROOT", f"inside source {run_root}"))
    return errors


def boundary_line_allowed(line: str, phrase: str) -> bool:
    lowered = line.lower()
    idx = lowered.find(phrase)
    prefix = lowered[max(0, idx - 240):idx]
    return any(term in prefix for term in ["no ", "not ", "do not ", "does not ", "without ", "forbidden", "non-goal", "not claimed", "not a "])


def scan_text(text: str, context: str) -> list[str]:
    errors: list[str] = []
    lowered_all = text.lower()
    for phrase in WEAK_GENERIC:
        if phrase in lowered_all:
            errors.append(issue("E_PHASE13_WEAK_GENERIC_RETURN", f"{context} contains {phrase!r}"))
    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for phrase in LEGACY_ACTIVE:
            if phrase in lowered and not boundary_line_allowed(line, phrase):
                errors.append(issue("E_PHASE13_LEGACY_ROUTE_REVIVAL", f"{context}:{lineno} contains {phrase!r}"))
        for phrase in RECURSIVE_CLAIMS:
            if phrase in lowered and not boundary_line_allowed(line, phrase):
                errors.append(issue("E_PHASE13_RECURSIVE_ORCHESTRATION_CLAIM", f"{context}:{lineno} contains {phrase!r}"))
        for phrase in BANNED_CLAIMS:
            if phrase in lowered and not boundary_line_allowed(line, phrase):
                errors.append(issue("E_PHASE13_COMPLETION_OVERCLAIM", f"{context}:{lineno} contains {phrase!r}"))
    return errors


def verifier_verdict(text: str) -> str | None:
    lowered = text.lower()
    for verdict in VERDICT_PARSE_ORDER:
        if f"verdict: {verdict}" in lowered or f"verdict — {verdict}" in lowered or f"verdict - {verdict}" in lowered:
            return verdict
    return None


def approx_same(a: str, b: str) -> bool:
    if a.strip() == b.strip():
        return True
    aw = set(a.lower().split())
    bw = set(b.lower().split())
    if not aw or not bw:
        return False
    return len(aw & bw) / max(1, min(len(aw), len(bw))) > 0.92


def registry_non_worker_ids(registry: dict[str, Any]) -> set[str]:
    return {s["stage_id"] for s in registry.get("stages", []) if isinstance(s, dict) and not s.get("requires_worker_task_packet")}


def validate_thread_rows(run_root: Path, threads: list[dict[str, Any]], stages: list[dict[str, Any]], errors: list[str]) -> None:
    expected_pairs = {(str(stage["stage_id"]), lane) for stage in stages for lane in ["producer", "verifier"]}
    seen_pairs: dict[tuple[str, str], int] = {}
    if len(threads) != 40:
        errors.append(issue("E_PHASE13_THREAD_COUNT", f"count={len(threads)}"))
    ids = [row.get("thread_id") for row in threads]
    if any(not isinstance(tid, str) or not tid.strip() for tid in ids):
        errors.append(issue("E_PHASE13_PROVENANCE", "empty thread id"))
    if len(ids) != len(set(ids)):
        errors.append(issue("E_PHASE13_THREAD_GLOBAL_DUPLICATE", "duplicate thread ids"))
    by_stage: dict[str, dict[str, str]] = {}
    for row in threads:
        sid = str(row.get("stage_id"))
        lane = str(row.get("lane"))
        pair = (sid, lane)
        seen_pairs[pair] = seen_pairs.get(pair, 0) + 1
        if pair not in expected_pairs:
            errors.append(issue("E_PHASE13_THREAD_COVERAGE", f"unexpected {sid}.{lane}"))
        by_stage.setdefault(sid, {})[lane] = str(row.get("thread_id"))
        if row.get("agent_type") == "worker":
            errors.append(issue("E_PHASE13_WORKER_ROLE_MISUSE", f"{sid}.{lane}"))
        packet_path_for_role = existing_file(run_root, row.get("packet_ref"), "E_PHASE13_PROVENANCE", f"{sid}.{lane}.packet_ref", errors)
        packet_for_role = load_json_file(packet_path_for_role, errors, "E_PHASE13_PACKET_MISSING") if packet_path_for_role is not None else None
        if isinstance(packet_for_role, dict) and row.get("agent_type") != packet_for_role.get("agent_type"):
            errors.append(issue("E_PHASE13_AGENT_TYPE_MISMATCH", f"{sid}.{lane} expected={packet_for_role.get('agent_type')} actual={row.get('agent_type')}"))
        if row.get("native_subagent") is not True or row.get("leader_summary_only") is not False:
            errors.append(issue("E_PHASE13_PROVENANCE", f"{sid}.{lane} native/summary flags"))
        for field in ["started_at", "completed_at", "packet_ref", "packet_sha256", "dispatch_prompt_ref", "dispatch_prompt_sha256", "raw_return_ref", "raw_return_sha256", "source"]:
            if not row.get(field):
                errors.append(issue("E_PHASE13_PROVENANCE", f"{sid}.{lane} missing {field}"))
        for ref_field, hash_field in [("packet_ref", "packet_sha256"), ("dispatch_prompt_ref", "dispatch_prompt_sha256"), ("raw_return_ref", "raw_return_sha256")]:
            path = existing_file(run_root, row.get(ref_field), "E_PHASE13_PROVENANCE", f"{sid}.{lane}.{ref_field}", errors)
            if path is not None and row.get(hash_field) != sha256_file(path):
                errors.append(issue("E_PHASE13_PROVENANCE", f"{sid}.{lane}.{hash_field} mismatch"))
    for sid, lanes in by_stage.items():
        if lanes.get("producer") == lanes.get("verifier"):
            errors.append(issue("E_PHASE13_THREAD_INDEPENDENCE", sid))
    for sid, lane in sorted(expected_pairs):
        count = seen_pairs.get((sid, lane), 0)
        if count != 1:
            errors.append(issue("E_PHASE13_THREAD_COVERAGE", f"{sid}.{lane} count={count}"))


def validate_verifier_grounding(run_root: Path, stage: dict[str, Any], packet: dict[str, Any], prompt_text: str, producer_row: dict[str, Any] | None, verifier_text: str, errors: list[str]) -> None:
    sid = stage["stage_id"]
    prod_ref = stage["producer_return_ref"]
    prod_path = existing_file(run_root, prod_ref, "E_PHASE13_VERIFIER_GROUNDING", f"{sid}.producer_return_ref", errors)
    expected_sha = sha256_file(prod_path) if prod_path is not None else None
    expected_thread = producer_row.get("thread_id") if producer_row else None
    if not expected_thread:
        errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid} missing producer thread row"))
    if packet.get("producer_return_ref") != prod_ref:
        errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid} producer_return_ref"))
    if expected_sha and packet.get("producer_return_sha256") != expected_sha:
        errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid} producer_return_sha256"))
    if expected_thread and packet.get("producer_thread_id") != expected_thread:
        errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid} producer_thread_id"))
    for value, label in [(prod_ref, "producer_return_ref"), (expected_sha, "producer_return_sha256"), (expected_thread, "producer_thread_id")]:
        if value and str(value) not in prompt_text:
            errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid} prompt missing {label}"))
    if verifier_text and "producer return" not in verifier_text.lower():
        errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid} verifier did not discuss producer return"))


def validate_dispatch_ledgers(run_root: Path, state: dict[str, Any], threads_by: dict[tuple[str, str], dict[str, Any]], errors: list[str]) -> None:
    expected_events: list[str] = []
    dispatch_records: list[dict[str, Any]] = []
    for index, stage in enumerate(state.get("stages", []), start=1):
        sid = stage["stage_id"]
        for lane in ["producer", "verifier"]:
            expected_id = f"dispatch-{index:03d}-{sid}-{lane}"
            expected_events.append(expected_id)
            ref = f"dispatch/{lane}/{sid}.{lane}-dispatch.json"
            dispatch = load_json_file(existing_file(run_root, ref, "E_PHASE13_DISPATCH_MISSING", f"{sid}.{lane}.dispatch", errors), errors, "E_PHASE13_DISPATCH_MISSING")
            packet = load_json_file(existing_file(run_root, stage.get(f"{lane}_packet_ref"), "E_PHASE13_UNSAFE_REF", f"{sid}.{lane}.packet", errors), errors, "E_PHASE13_PACKET_MISSING")
            prompt_path = existing_file(run_root, stage.get(f"{lane}_prompt_ref"), "E_PHASE13_UNSAFE_REF", f"{sid}.{lane}.prompt", errors)
            if not isinstance(dispatch, dict):
                continue
            dispatch_records.append(dispatch)
            if dispatch.get("schema_version") != "ppg-phase13-dispatch/v0.1" or dispatch.get("run_id") != RUN_ID or dispatch.get("event_id") != expected_id or dispatch.get("event") != "dispatch_prepared":
                errors.append(issue("E_PHASE13_DISPATCH_RECORD", f"{sid}.{lane} identity"))
            for field, expected in [("stage_id", sid), ("lane", lane), ("packet_ref", stage.get(f"{lane}_packet_ref")), ("dispatch_prompt_ref", stage.get(f"{lane}_prompt_ref")), ("raw_return_ref", stage.get(f"{lane}_return_ref"))]:
                if dispatch.get(field) != expected:
                    errors.append(issue("E_PHASE13_DISPATCH_RECORD", f"{sid}.{lane}.{field}"))
            if isinstance(packet, dict) and dispatch.get("agent_type") != packet.get("agent_type"):
                errors.append(issue("E_PHASE13_AGENT_TYPE_MISMATCH", f"{sid}.{lane}.dispatch expected={packet.get('agent_type')} actual={dispatch.get('agent_type')}"))
            if isinstance(packet, dict) and dispatch.get("authority_mode") != packet.get("authority_mode"):
                errors.append(issue("E_PHASE13_AUTHORITY_MODE", f"{sid}.{lane}.dispatch expected={packet.get('authority_mode')} actual={dispatch.get('authority_mode')}"))
            packet_path = existing_file(run_root, stage.get(f"{lane}_packet_ref"), "E_PHASE13_UNSAFE_REF", f"{sid}.{lane}.packet_hash", errors)
            if packet_path is not None and dispatch.get("packet_sha256") != sha256_file(packet_path):
                errors.append(issue("E_PHASE13_DISPATCH_RECORD", f"{sid}.{lane}.packet_sha256"))
            if prompt_path is not None and dispatch.get("dispatch_prompt_sha256") != sha256_file(prompt_path):
                errors.append(issue("E_PHASE13_DISPATCH_RECORD", f"{sid}.{lane}.dispatch_prompt_sha256"))
            row = threads_by.get((sid, lane), {})
            if row and dispatch.get("agent_type") != row.get("agent_type"):
                errors.append(issue("E_PHASE13_AGENT_TYPE_MISMATCH", f"{sid}.{lane}.thread_dispatch"))
            if lane == "verifier":
                prod_row = threads_by.get((sid, "producer"), {})
                prod_path = existing_file(run_root, stage.get("producer_return_ref"), "E_PHASE13_VERIFIER_GROUNDING", f"{sid}.producer_return_for_dispatch", errors)
                prod_sha = sha256_file(prod_path) if prod_path is not None else None
                for field, expected in [("producer_return_ref", stage.get("producer_return_ref")), ("producer_return_sha256", prod_sha), ("producer_thread_id", prod_row.get("thread_id"))]:
                    if expected and dispatch.get(field) != expected:
                        errors.append(issue("E_PHASE13_VERIFIER_GROUNDING", f"{sid}.dispatch.{field}"))
    ledger = load_jsonl_file(existing_file(run_root, state.get("dispatch_ledger_ref"), "E_PHASE13_LEDGER_MISSING", "dispatch_ledger_ref", errors), errors, "E_PHASE13_LEDGER_MISSING")
    if ledger is not None:
        if len(ledger) != 40:
            errors.append(issue("E_PHASE13_LEDGER_COUNT", f"dispatch={len(ledger)}"))
        if [str(item.get("event_id")) for item in ledger] != expected_events:
            errors.append(issue("E_PHASE13_LEDGER_ORDER", "dispatch_ledger"))
        for item, dispatch in zip(ledger, dispatch_records, strict=False):
            if item != dispatch:
                errors.append(issue("E_PHASE13_LEDGER_CONTENT", f"dispatch {dispatch.get('event_id')}"))


def validate_validation_ledger(run_root: Path, state: dict[str, Any], raw_verdicts: dict[str, str], errors: list[str]) -> None:
    expected_events: list[str] = []
    for index, stage in enumerate(state.get("stages", []), start=1):
        expected_events.append(f"validation-{index:03d}-{stage['stage_id']}")
    ledger = load_jsonl_file(existing_file(run_root, state.get("validation_ledger_ref"), "E_PHASE13_LEDGER_MISSING", "validation_ledger_ref", errors), errors, "E_PHASE13_LEDGER_MISSING")
    if ledger is None:
        return
    if len(ledger) != 20:
        errors.append(issue("E_PHASE13_LEDGER_COUNT", f"validation={len(ledger)}"))
    if [str(item.get("event_id")) for item in ledger] != expected_events:
        errors.append(issue("E_PHASE13_LEDGER_ORDER", "validation_ledger"))
    stage_by_id = {stage["stage_id"]: stage for stage in state.get("stages", [])}
    for item in ledger:
        sid = str(item.get("stage_id"))
        stage = stage_by_id.get(sid)
        if not stage:
            errors.append(issue("E_PHASE13_LEDGER_ORDER", f"unknown validation stage {sid}"))
            continue
        if item.get("event") != "live_validation_recorded" or item.get("run_id") != RUN_ID:
            errors.append(issue("E_PHASE13_LEDGER_ORDER", f"{sid}.validation identity"))
        if item.get("validation_ref") != stage.get("validation_ref") or item.get("effect_ref") != stage.get("effect_ref"):
            errors.append(issue("E_PHASE13_LEDGER_ORDER", f"{sid}.validation refs"))
        if item.get("verdict") not in VERDICTS:
            errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid}.ledger verdict"))
        if raw_verdicts.get(sid) and item.get("verdict") != raw_verdicts[sid]:
            errors.append(issue("E_PHASE13_RAW_VERDICT_MISMATCH", f"{sid}.ledger verdict"))
        validation = load_json_file(existing_file(run_root, stage.get("validation_ref"), "E_PHASE13_VALIDATION_MISSING", f"{sid}.ledger.validation_ref", errors), errors, "E_PHASE13_VALIDATION_MISSING")
        effect = load_json_file(existing_file(run_root, stage.get("effect_ref"), "E_PHASE13_EFFECT_RECORD", f"{sid}.ledger.effect_ref", errors), errors, "E_PHASE13_EFFECT_RECORD")
        if isinstance(validation, dict):
            if item.get("verdict") != validation.get("verifier_verdict"):
                errors.append(issue("E_PHASE13_LEDGER_CONTENT", f"{sid}.validation verdict"))
            if item.get("validation_ref") != stage.get("validation_ref") or item.get("effect_ref") != validation.get("effect_ref"):
                errors.append(issue("E_PHASE13_LEDGER_CONTENT", f"{sid}.validation refs"))
        if isinstance(effect, dict):
            if item.get("verdict") != effect.get("verifier_verdict"):
                errors.append(issue("E_PHASE13_LEDGER_CONTENT", f"{sid}.effect verdict"))
            if item.get("effect_ref") != stage.get("effect_ref"):
                errors.append(issue("E_PHASE13_LEDGER_CONTENT", f"{sid}.effect ref"))


def validate_effect(effect: dict[str, Any], sid: str, non_worker: set[str], errors: list[str]) -> None:
    if effect.get("schema_version") != "ppg-phase13-stage-effect/v0.1" or effect.get("run_id") != RUN_ID or effect.get("stage_id") != sid:
        errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid} schema/run/stage"))
    authority = effect.get("authority_mode")
    if sid in non_worker and authority != "assessment_only":
        errors.append(issue("E_PHASE13_AUTHORITY_MODE", f"{sid} expected assessment_only actual={authority}"))
    dims = effect.get("dimensions")
    if not isinstance(dims, dict):
        errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid} dimensions"))
        return
    required = ["stage_specificity", "input_grounding", "downstream_usefulness", "boundary_compliance", "actionability"]
    values: list[int] = []
    for key in required:
        value = dims.get(key)
        if not isinstance(value, int) or not 0 <= value <= 5:
            errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid}.{key}={value}"))
        else:
            values.append(value)
    if len(values) == 5 and effect.get("effect_score") != round(sum(values) / 5):
        errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid} effect_score"))
    if dims.get("boundary_compliance") != 5:
        errors.append(issue("E_PHASE13_AUTHORITY_MODE", f"{sid} boundary compliance"))
    if effect.get("verifier_verdict") not in VERDICTS:
        errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid} verifier_verdict"))
    if effect.get("controller_acceptance") != effect.get("verifier_verdict"):
        errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid} controller_acceptance"))
    if effect.get("verifier_verdict") == "reject":
        errors.append(issue("E_PHASE13_STAGE_REJECTED", sid))
    if effect.get("repair_required") is True and not effect.get("repair_ref"):
        errors.append(issue("E_PHASE13_REPAIR_UNRESOLVED", sid))
    if effect.get("verifier_verdict") == "needs_repair" and not effect.get("repair_ref"):
        errors.append(issue("E_PHASE13_REPAIR_UNRESOLVED", sid))
    if effect.get("packet_citations_present") is not True:
        errors.append(issue("E_PHASE13_PACKET_CITATION_MISSING", sid))


def verify_phase13_run(run_root: Path = DEFAULT_RUN_ROOT, pilot_root: Path = DEFAULT_PILOT) -> list[str]:
    errors: list[str] = []
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    pilot_manifest = load_json(pilot_root / "manifest.json")
    source_root = Path(str(pilot_manifest["source_root"])).resolve(strict=True)
    root_errors = validate_run_root_before_reads(run_root, source_root)
    errors.extend(root_errors)
    if root_errors:
        return errors
    manifest = load_json_file(run_root / "manifest.json", errors, "E_PHASE13_MANIFEST_MISSING")
    state = load_json_file(run_root / "run_state.json", errors, "E_PHASE13_RUN_STATE_MISSING")
    if not isinstance(manifest, dict) or not isinstance(state, dict):
        return errors
    registry = load_json(REGISTRY)
    non_worker = registry_non_worker_ids(registry)
    expected_ids = list(registry.get("canonical_stage_ids", []))
    if manifest.get("run_id") != RUN_ID or state.get("run_id") != RUN_ID:
        errors.append(issue("E_PHASE13_RUN_ID", "mismatch"))
    if state.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append(issue("E_PHASE13_RUN_STATE_SCHEMA", str(state.get("schema_version"))))
    stages = state.get("stages")
    if not isinstance(stages, list) or [s.get("stage_id") for s in stages if isinstance(s, dict)] != expected_ids:
        errors.append(issue("E_PHASE13_STAGE_ORDER", "canonical stage order mismatch"))
        return errors
    before = load_json_file(existing_file(run_root, state.get("source_snapshot_before_ref"), "E_PHASE13_UNSAFE_REF", "source_snapshot_before_ref", errors), errors, "E_PHASE13_SOURCE_SNAPSHOT_MISSING")
    after = load_json_file(existing_file(run_root, state.get("source_snapshot_after_ref"), "E_PHASE13_UNSAFE_REF", "source_snapshot_after_ref", errors), errors, "E_PHASE13_SOURCE_SNAPSHOT_MISSING")
    for label, snapshot in [("before", before), ("after", after)]:
        if isinstance(snapshot, dict):
            violations = source_runtime_artifact_violations(snapshot)
            if violations:
                errors.append(issue("E_PHASE13_SOURCE_RUNTIME_ARTIFACT", f"{label}: {violations[:8]}"))
    if before is not None and after is not None and before != after:
        errors.append(issue("E_PHASE13_SOURCE_SNAPSHOT_DRIFT", "before/after differ"))
    if after is not None:
        current = compute_source_snapshot(source_root)
        violations = source_runtime_artifact_violations(current)
        if violations:
            errors.append(issue("E_PHASE13_SOURCE_RUNTIME_ARTIFACT", f"current: {violations[:8]}"))
        if current != after:
            errors.append(issue("E_PHASE13_SOURCE_SNAPSHOT_CURRENT_DRIFT", "current differs from after"))
    threads_doc = load_json_file(existing_file(run_root, state.get("subagent_threads_ref"), "E_PHASE13_UNSAFE_REF", "subagent_threads_ref", errors), errors, "E_PHASE13_THREADS_MISSING")
    threads = threads_doc.get("threads", []) if isinstance(threads_doc, dict) else []
    threads_by: dict[tuple[str, str], dict[str, Any]] = {}
    if isinstance(threads, list):
        validate_thread_rows(run_root, threads, stages, errors)
        threads_by = thread_rows_by_stage_lane(threads)
        validate_dispatch_ledgers(run_root, state, threads_by, errors)
    else:
        errors.append(issue("E_PHASE13_THREADS_MISSING", "threads not list"))
    raw_verdicts: dict[str, str] = {}
    for stage in stages:
        sid = stage["stage_id"]
        if sid in non_worker and stage.get("authority_mode") != "assessment_only":
            errors.append(issue("E_PHASE13_AUTHORITY_MODE", f"{sid} run_state"))
        producer_text = ""
        verifier_text = ""
        verifier_packet: dict[str, Any] | None = None
        verifier_prompt_text = ""
        for lane in ["producer", "verifier"]:
            packet = load_json_file(existing_file(run_root, stage.get(f"{lane}_packet_ref"), "E_PHASE13_UNSAFE_REF", f"{sid}.{lane}_packet_ref", errors), errors, "E_PHASE13_PACKET_MISSING")
            if isinstance(packet, dict):
                if sid in non_worker and packet.get("authority_mode") != "assessment_only":
                    errors.append(issue("E_PHASE13_AUTHORITY_MODE", f"{sid}.{lane}.packet"))
                if packet.get("agent_type") == "worker":
                    errors.append(issue("E_PHASE13_WORKER_ROLE_MISUSE", f"{sid}.{lane}.packet"))
                row = threads_by.get((sid, lane), {})
                if row and row.get("agent_type") != packet.get("agent_type"):
                    errors.append(issue("E_PHASE13_AGENT_TYPE_MISMATCH", f"{sid}.{lane} expected={packet.get('agent_type')} actual={row.get('agent_type')}"))
                if lane == "verifier":
                    verifier_packet = packet
                    prompt_path = existing_file(run_root, stage.get("verifier_prompt_ref"), "E_PHASE13_UNSAFE_REF", f"{sid}.verifier_prompt_ref", errors)
                    if prompt_path is not None:
                        verifier_prompt_text = prompt_path.read_text(encoding="utf-8", errors="ignore")
            return_path = existing_file(run_root, stage.get(f"{lane}_return_ref"), f"E_PHASE13_{lane.upper()}_RETURN_MISSING", f"{sid}.{lane}_return_ref", errors)
            if return_path is not None:
                text = return_path.read_text(encoding="utf-8", errors="ignore")
                if lane == "producer":
                    producer_text = text
                else:
                    verifier_text = text
                if len(text.strip()) < 300 or sid not in text or stage["stage_name"] not in text:
                    errors.append(issue("E_PHASE13_WEAK_GENERIC_RETURN", f"{sid}.{lane}"))
                if str(stage.get(f"{lane}_packet_ref")) not in text:
                    errors.append(issue("E_PHASE13_PACKET_CITATION_MISSING", f"{sid}.{lane}"))
                errors.extend(scan_text(text, f"{sid}.{lane}"))
        if verifier_packet is not None:
            validate_verifier_grounding(run_root, stage, verifier_packet, verifier_prompt_text, threads_by.get((sid, "producer")), verifier_text, errors)
        parsed_verdict = verifier_verdict(verifier_text) if verifier_text else None
        if verifier_text and parsed_verdict is None:
            errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid}.verifier verdict missing"))
        if parsed_verdict is not None:
            raw_verdicts[sid] = parsed_verdict
        if producer_text and verifier_text and approx_same(producer_text, verifier_text):
            errors.append(issue("E_PHASE13_VERIFIER_PARROTING", sid))
        effect = load_json_file(existing_file(run_root, stage.get("effect_ref"), "E_PHASE13_EFFECT_RECORD", f"{sid}.effect_ref", errors), errors, "E_PHASE13_EFFECT_RECORD")
        if isinstance(effect, dict):
            validate_effect(effect, sid, non_worker, errors)
            if parsed_verdict is not None and effect.get("verifier_verdict") != parsed_verdict:
                errors.append(issue("E_PHASE13_RAW_VERDICT_MISMATCH", f"{sid}.effect verdict"))
        validation = load_json_file(existing_file(run_root, stage.get("validation_ref"), "E_PHASE13_VALIDATION_MISSING", f"{sid}.validation_ref", errors), errors, "E_PHASE13_VALIDATION_MISSING")
        if isinstance(validation, dict):
            verdict = validation.get("verifier_verdict")
            if parsed_verdict is not None and verdict != parsed_verdict:
                errors.append(issue("E_PHASE13_RAW_VERDICT_MISMATCH", f"{sid}.validation verdict"))
            if verdict not in VERDICTS:
                errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid}.validation verifier_verdict"))
            else:
                expected_status = "pass" if verdict in {"accept", "accept_with_limitations"} else "needs_controller_repair"
                if validation.get("status") != expected_status:
                    errors.append(issue("E_PHASE13_VALIDATION_STATUS", f"{sid}.{validation.get('status')} expected={expected_status}"))
            if isinstance(effect, dict) and validation.get("verifier_verdict") != effect.get("verifier_verdict"):
                errors.append(issue("E_PHASE13_EFFECT_RECORD", f"{sid}.validation_effect verdict"))
    validate_validation_ledger(run_root, state, raw_verdicts, errors)
    delivery = load_json_file(existing_file(run_root, state.get("delivery_gate_ref"), "E_PHASE13_UNSAFE_REF", "delivery_gate_ref", errors), errors, "E_PHASE13_DELIVERY_GATE_MISSING")
    if isinstance(delivery, dict):
        if delivery.get("verdict") != "pass_for_live_runtime_pilot_only":
            errors.append(issue("E_PHASE13_DELIVERY_GATE", str(delivery.get("verdict"))))
        if delivery.get("rejected") != 0 or delivery.get("needs_repair") != 0:
            errors.append(issue("E_PHASE13_DELIVERY_GATE", "unresolved reject/repair"))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Phase13 live native-subagent pilot artifacts.")
    parser.add_argument("run_root", nargs="?", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args(argv)
    errors = verify_phase13_run(args.run_root, args.pilot_root)
    if errors:
        print("INVALID Phase13 live subagent pilot", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE13_LIVE_SUBAGENT_PILOT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
