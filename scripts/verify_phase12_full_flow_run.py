#!/usr/bin/env python3
"""Verify Phase12 formal full-flow runtime-test artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import stat
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import (
        NATURE_OVERLAY_ID,
        OVERLAY_REGISTRY,
        ROOT,
        compute_source_snapshot,
        is_relative_to,
        load_json,
        overlay_binding_by_stage,
        stage_overlay_summary,
    )
    from generate_phase12_full_flow_run import DEFAULT_PILOT, DEFAULT_RUN_ROOT, RUN_ID
    from ppg_validate_common import load_document
    from validate_packet import validate as validate_packet
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import (  # type: ignore  # noqa: E402
        NATURE_OVERLAY_ID,
        OVERLAY_REGISTRY,
        ROOT,
        compute_source_snapshot,
        is_relative_to,
        load_json,
        overlay_binding_by_stage,
        stage_overlay_summary,
    )
    from generate_phase12_full_flow_run import DEFAULT_PILOT, DEFAULT_RUN_ROOT, RUN_ID  # type: ignore  # noqa: E402
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402
    from validate_packet import validate as validate_packet  # type: ignore  # noqa: E402

REGISTRY = ROOT / "runtime" / "stage_registry.json"
VALIDATORS = ROOT / "runtime" / "phase10_content_validators.json"
RUN_SCHEMA_VERSION = "ppg-phase12-run-state/v0.1"
CANONICAL_BACKFLOW_EVENTS = [
    "review_finding_recorded",
    "backflow_task_compiled",
    "repair_candidate_recorded",
    "review_closure_recorded",
]
BANNED_CLAIMS = [
    "final manuscript complete",
    "final paper complete",
    "submission ready",
    "ready to submit",
    "publication ready",
]
POSITIVE_FORBIDDEN_BOUNDARY_PHRASES = [
    "live install enabled",
    "marketplace registration enabled",
    "cachebuster completed",
    "publish lifecycle completed",
    "$yxj-paper-os revived",
    "$yxj-plugin-incubator used as a design source",
]
EXPECTED_OVERLAY_AUTHORITY = {
    "stage_local_only": True,
    "no_new_department": True,
    "controller_owned_completion": True,
    "worker_completion_forbidden": True,
    "no_recursive_orchestration": True,
    "overlay_dispatch_allowed": False,
    "route_kind": "stage_local_overlay",
}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def is_regular_file_no_symlink(path: Path) -> bool:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return False
    return not path.is_symlink() and stat.S_ISREG(st.st_mode)


def load_json_file(path: Path, errors: list[str], code: str) -> Any | None:
    if not is_regular_file_no_symlink(path):
        errors.append(issue(code, rel(path)))
        return None
    try:
        return load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(issue("E_PHASE12_JSON_PARSE", f"{rel(path)}: {exc}"))
        return None


def jsonl_events(path: Path, errors: list[str], code: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not is_regular_file_no_symlink(path):
        errors.append(issue(code, rel(path)))
        return events
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(issue("E_PHASE12_JSONL_PARSE", f"{rel(path)} line {lineno}: {exc}"))
            continue
        if not isinstance(data, dict):
            errors.append(issue("E_PHASE12_JSONL_SHAPE", f"{rel(path)} line {lineno}"))
            continue
        for field in ["event_id", "event", "run_id"]:
            if not data.get(field):
                errors.append(issue("E_PHASE12_JSONL_FIELD", f"{rel(path)} line {lineno} missing {field}"))
        events.append(data)
    return events


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
        return None, [issue(code, f"{context}={ref}")]
    return path, []


def run_owned_existing_file(run_root: Path, ref: Any, code: str, context: str, errors: list[str]) -> Path | None:
    path, ref_errors = safe_run_ref(run_root, ref, code, context)
    errors.extend(ref_errors)
    if path is not None and not is_regular_file_no_symlink(path):
        errors.append(issue(code, f"{context} missing safe regular file {ref}"))
        return None
    return path


def validate_run_root_before_reads(run_root: Path, source_root: Path) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    if run_root.is_symlink():
        return None, [issue("E_PHASE12_RUN_ROOT", f"run root must not be a symlink: {run_root}")]
    try:
        st = run_root.lstat()
    except FileNotFoundError:
        return None, [issue("E_PHASE12_RUN_ROOT", f"missing {run_root}")]
    if not stat.S_ISDIR(st.st_mode):
        return None, [issue("E_PHASE12_RUN_ROOT", f"not a directory: {run_root}")]
    try:
        resolved_run = run_root.resolve(strict=True)
    except Exception as exc:  # noqa: BLE001
        return None, [issue("E_PHASE12_RUN_ROOT", f"invalid {run_root}: {exc}")]
    if not is_relative_to(resolved_run, (ROOT / "runs").resolve(strict=True)):
        errors.append(issue("E_PHASE12_RUN_ROOT", f"outside runs: {run_root}"))
    if is_relative_to(resolved_run, source_root) or resolved_run == source_root:
        errors.append(issue("E_PHASE12_RUN_ROOT_UNDER_SOURCE", str(run_root)))
    if errors:
        return None, errors
    return resolved_run, []


def check_no_overclaim(value: Any, context: str) -> list[str]:
    lowered = str(value).lower()
    return [issue("E_PHASE12_COMPLETION_OVERCLAIM", f"{context} contains {phrase!r}") for phrase in BANNED_CLAIMS if phrase in lowered]


def boundary_line_allowed(line: str, phrase: str) -> bool:
    lowered = line.lower()
    phrase_index = lowered.find(phrase)
    prefix = lowered[max(0, phrase_index - 80):phrase_index]
    allow_terms = ["no ", "not ", "does not ", "do not ", "without ", "forbidden", "non-goal", "not enabled", "not claimed", "unless", "do **not**"]
    return any(term in prefix for term in allow_terms)


def scan_text_boundary(text: str, context: str) -> list[str]:
    errors: list[str] = []
    phrases = BANNED_CLAIMS + POSITIVE_FORBIDDEN_BOUNDARY_PHRASES
    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for phrase in phrases:
            if phrase in lowered and not boundary_line_allowed(line, phrase):
                errors.append(issue("E_PHASE12_DOC_BOUNDARY", f"{context}:{lineno} contains unbounded {phrase!r}"))
    return errors


def scan_boundary_files(run_root: Path) -> list[str]:
    errors: list[str] = []
    paths = [
        ROOT / "README.md",
        ROOT / "skills/yxj-paper-ppg-runtime/SKILL.md",
        ROOT / "docs/VALIDATION_AND_TESTING.md",
        ROOT / "docs/phase-promotions/PHASE_12_FORMAL_FULL_FLOW_RUNTIME_TEST_2026-06-30.md",
    ]
    for path in paths:
        if path.exists():
            errors.extend(scan_text_boundary(path.read_text(encoding="utf-8", errors="ignore"), rel(path)))
    for path in run_root.rglob("*"):
        if path.suffix.lower() not in {".json", ".jsonl", ".md", ".txt"}:
            continue
        if path.is_symlink():
            errors.append(issue("E_PHASE12_RUN_REF", f"boundary scan symlink {rel(path)}"))
            continue
        if is_regular_file_no_symlink(path):
            errors.extend(scan_text_boundary(path.read_text(encoding="utf-8", errors="ignore"), rel(path)))
    return errors


def validate_overlay_authority(overlays: dict[str, Any]) -> list[str]:
    overlay = next((item for item in overlays.get("overlays", []) if isinstance(item, dict) and item.get("overlay_id") == NATURE_OVERLAY_ID), None)
    if not isinstance(overlay, dict):
        return [issue("E_PHASE12_STAGE_OVERLAY_LINK", f"missing {NATURE_OVERLAY_ID}")]
    authority = overlay.get("authority_model")
    if not isinstance(authority, dict):
        return [issue("E_PHASE12_OVERLAY_AUTHORITY", "authority_model missing")]
    errors: list[str] = []
    for key, expected in EXPECTED_OVERLAY_AUTHORITY.items():
        if authority.get(key) != expected:
            errors.append(issue("E_PHASE12_OVERLAY_AUTHORITY", f"{key} expected={expected!r} actual={authority.get(key)!r}"))
    return errors


def validate_stage_overlay_record(value: Any, sid: str, overlay_binding: dict[str, Any], context: str) -> list[str]:
    expected = [stage_overlay_summary(sid, overlay_binding)]
    if value != expected:
        return [issue("E_PHASE12_STAGE_OVERLAY_LINK", f"{context} expected={expected!r} actual={value!r}")]
    return []


def validate_candidate(candidate: dict[str, Any], sid: str, overlay_binding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version": "ppg-phase12-stage-candidate/v0.1",
        "run_id": RUN_ID,
        "stage_id": sid,
        "candidate_only": True,
        "controller_commit_required": True,
        "worker_completion_forbidden": True,
        "no_recursive_orchestration": True,
        "source_write_forbidden": True,
    }
    for key, expected in required.items():
        if candidate.get(key) != expected:
            if key == "candidate_only":
                errors.append(issue("E_PHASE12_CANDIDATE_AUTHORITY", f"{sid}.{key}"))
            elif key == "controller_commit_required":
                errors.append(issue("E_PHASE12_CONTROLLER_COMMIT_REQUIRED", sid))
            elif key == "worker_completion_forbidden":
                errors.append(issue("E_PHASE12_CANDIDATE_AUTHORITY", f"{sid}.{key}"))
            else:
                errors.append(issue("E_PHASE12_CANDIDATE_CONTENT", f"{sid}.{key} expected={expected!r} actual={candidate.get(key)!r}"))
    for field in ["consumed_materials", "produced_materials", "validator_refs"]:
        if not isinstance(candidate.get(field), list) or not candidate.get(field):
            errors.append(issue("E_PHASE12_CANDIDATE_CONTENT", f"{sid}.{field}"))
    errors.extend(check_no_overclaim(candidate.get("completion_boundary", ""), f"{sid}.candidate.completion_boundary"))
    errors.extend(validate_stage_overlay_record(candidate.get("active_stage_overlays"), sid, overlay_binding, f"{sid}.candidate.active_stage_overlays"))
    return errors


def validate_run_packet(run_root: Path, stage: dict[str, Any], packet_ref: Any, candidate_ref: str, overlay_binding: dict[str, Any]) -> list[str]:
    sid = str(stage.get("stage_id"))
    packet_path, ref_errors = safe_run_ref(run_root, packet_ref, "E_PHASE12_RUN_PACKET_REF", f"{sid}.packet_ref")
    errors = list(ref_errors)
    if packet_path is None:
        return errors
    packet_data, packet_load_errors = load_document(packet_path)
    if packet_load_errors:
        return errors + [issue("E_PHASE12_RUN_PACKET_PARSE", f"{sid} {packet_ref}: {packet_load_errors[0].message}")]
    if not isinstance(packet_data, dict):
        return errors + [issue("E_PHASE12_RUN_PACKET_PARSE", f"{sid} {packet_ref}: packet must be mapping")]
    packet_errors = validate_packet(packet_data)
    if packet_errors:
        errors.append(issue("E_PHASE12_RUN_PACKET_INVALID", f"{sid} {packet_ref}: {packet_errors[0].code}"))
    expected_contract = f"examples/stage-contracts/{sid}.stage-contract.json"
    if packet_data.get("stage_id") != sid or packet_data.get("stage_contract_ref") != expected_contract:
        errors.append(issue("E_PHASE12_RUN_PACKET_STAGE_BINDING", sid))
    expected_output = rel(run_root / candidate_ref)
    if packet_data.get("output_artifact_path") != expected_output or packet_data.get("allowed_write_paths") != [expected_output]:
        errors.append(issue("E_PHASE12_RUN_PACKET_OUTPUT_BOUNDARY", f"{sid} expected {expected_output}"))
    output_path = ROOT / str(packet_data.get("output_artifact_path", ""))
    try:
        output_path.resolve(strict=False).relative_to(run_root.resolve(strict=True))
    except Exception:  # noqa: BLE001
        errors.append(issue("E_PHASE12_RUN_PACKET_OUTPUT_BOUNDARY", f"{sid} output escapes run root"))
    if output_path.is_symlink():
        errors.append(issue("E_PHASE12_RUN_PACKET_OUTPUT_BOUNDARY", f"{sid} output is symlink"))
    controls = packet_data.get("mandatory_controls")
    if not isinstance(controls, dict) or controls.get("nature_overlay_ref") != f"runtime/stage_overlay_registry.json#{NATURE_OVERLAY_ID}" or controls.get("nature_overlay_stage_binding") != sid:
        errors.append(issue("E_PHASE12_STAGE_OVERLAY_LINK", f"{sid} run packet overlay controls"))
    clauses = controls.get("nature_overlay_packet_clauses") if isinstance(controls, dict) else None
    required_clauses = set(overlay_binding.get("packet_clauses", [])) if isinstance(overlay_binding.get("packet_clauses"), list) else set()
    if not isinstance(clauses, list) or required_clauses - {str(item) for item in clauses}:
        errors.append(issue("E_PHASE12_STAGE_OVERLAY_LINK", f"{sid} run packet overlay clauses"))
    expected_validator = f"stage_overlay:{NATURE_OVERLAY_ID}:{sid}"
    validators = packet_data.get("validators")
    if not isinstance(validators, list) or expected_validator not in validators:
        errors.append(issue("E_PHASE12_STAGE_OVERLAY_LINK", f"{sid} run packet overlay validator"))
    return errors


def validate_dispatch(dispatch: dict[str, Any], sid: str, overlay_binding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version": "ppg-phase12-dispatch-record/v0.1",
        "run_id": RUN_ID,
        "stage_id": sid,
        "source_read_only": True,
    }
    for key, expected in required.items():
        if dispatch.get(key) != expected:
            errors.append(issue("E_PHASE12_DISPATCH_CONTENT", f"{sid}.{key}"))
    authority = dispatch.get("worker_authority")
    if not isinstance(authority, dict):
        errors.append(issue("E_PHASE12_WORKER_COMPLETION_FORBIDDEN", f"{sid}.worker_authority"))
    else:
        for key in ["completion_forbidden", "no_recursive_orchestration", "controller_owned_completion", "source_write_forbidden"]:
            if authority.get(key) is not True:
                code = "E_PHASE12_WORKER_COMPLETION_FORBIDDEN" if key == "completion_forbidden" else "E_PHASE12_DISPATCH_WORKER_AUTHORITY"
                errors.append(issue(code, f"{sid}.{key}"))
    errors.extend(validate_stage_overlay_record(dispatch.get("active_stage_overlays"), sid, overlay_binding, f"{sid}.dispatch.active_stage_overlays"))
    errors.extend(check_no_overclaim(dispatch.get("completion_boundary", ""), f"{sid}.dispatch.completion_boundary"))
    return errors


def validate_validation_record(validation: dict[str, Any], sid: str, validator: dict[str, Any], overlay_binding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version": "ppg-phase12-stage-validation/v0.1",
        "run_id": RUN_ID,
        "stage_id": sid,
        "validator_id": validator.get("validator_id"),
    }
    for key, expected in required.items():
        if validation.get(key) != expected:
            errors.append(issue("E_PHASE12_VALIDATION_CONTENT", f"{sid}.{key}"))
    if validation.get("stage_overlay_checks") != overlay_binding.get("validator_checks", []):
        errors.append(issue("E_PHASE12_STAGE_OVERLAY_LINK", f"{sid}.validation.stage_overlay_checks"))
    if not isinstance(validation.get("required_checks"), list) or not validation.get("required_checks"):
        errors.append(issue("E_PHASE12_VALIDATION_CONTENT", f"{sid}.required_checks"))
    errors.extend(validate_stage_overlay_record(validation.get("active_stage_overlays"), sid, overlay_binding, f"{sid}.validation.active_stage_overlays"))
    errors.extend(check_no_overclaim(validation.get("completion_boundary", ""), f"{sid}.validation.completion_boundary"))
    return errors


def validate_backflow_chain(run_root: Path, delivery: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = jsonl_events(run_root / "backflow_ledger.jsonl", errors, "E_PHASE12_BACKFLOW_LEDGER_MISSING")
    sequence = [event.get("event") for event in events]
    if sequence != CANONICAL_BACKFLOW_EVENTS:
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", f"sequence={sequence}"))
        return errors
    first, second, third, fourth = events
    finding_ref = first.get("finding_ref")
    task_ref = second.get("backflow_task_ref")
    repair_ref = third.get("repair_candidate_ref")
    closure_ref = fourth.get("closure_ref")
    refs = [
        (finding_ref, "review-findings", "finding_ref"),
        (task_ref, "backflow-tasks", "backflow_task_ref"),
        (repair_ref, "repair-artifacts", "repair_candidate_ref"),
        (closure_ref, "closures", "closure_ref"),
    ]
    safe_paths: dict[str, Path] = {}
    for ref, prefix, context in refs:
        if not isinstance(ref, str) or not ref.startswith(f"{prefix}/"):
            errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", f"{context} must stay under {prefix}/"))
            continue
        path = run_owned_existing_file(run_root, ref, "E_PHASE12_BACKFLOW_CHAIN", context, errors)
        if path is not None:
            safe_paths[context] = path
    if second.get("source_finding_ref") != finding_ref:
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "task source_finding_ref mismatch"))
    if third.get("source_backflow_task_ref") != task_ref:
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "repair source_backflow_task_ref mismatch"))
    if fourth.get("source_finding_ref") != finding_ref or fourth.get("source_backflow_task_ref") != task_ref or fourth.get("repair_candidate_ref") != repair_ref:
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "closure refs mismatch"))
    consumed = delivery.get("consumed_closure_refs")
    if not isinstance(consumed, list) or closure_ref not in consumed:
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "delivery gate missing closure ref"))
    if len(safe_paths) != len(refs):
        return errors
    finding = load_json_file(safe_paths["finding_ref"], errors, "E_PHASE12_BACKFLOW_CHAIN")
    task = load_json_file(safe_paths["backflow_task_ref"], errors, "E_PHASE12_BACKFLOW_CHAIN")
    repair = load_json_file(safe_paths["repair_candidate_ref"], errors, "E_PHASE12_BACKFLOW_CHAIN")
    closure = load_json_file(safe_paths["closure_ref"], errors, "E_PHASE12_BACKFLOW_CHAIN")
    if isinstance(finding, dict) and finding.get("whole_paper_rewrite_authorized") is not False:
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "whole paper rewrite not forbidden"))
    if isinstance(task, dict):
        affected = task.get("affected_materials")
        unaffected = task.get("unaffected_materials")
        if not isinstance(affected, list) or not affected or not isinstance(unaffected, list) or not unaffected:
            errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "affected/unaffected locality missing"))
    if isinstance(repair, dict) and repair.get("candidate_only") is not True:
        errors.append(issue("E_PHASE12_CANDIDATE_AUTHORITY", "repair candidate_only"))
    if isinstance(closure, dict) and closure.get("status") != "closed_for_runtime_test":
        errors.append(issue("E_PHASE12_BACKFLOW_CHAIN", "closure status"))
    return errors


def validate_owner_ledger(run_root: Path) -> list[str]:
    errors: list[str] = []
    events = jsonl_events(run_root / "owner_decision_log.jsonl", errors, "E_PHASE12_OWNER_LEDGER_MISSING")
    event_names = {str(event.get("event")) for event in events if event.get("event") is not None}
    if "owner_boundary_assumption" not in event_names or "source_write_policy" not in event_names:
        errors.append(issue("E_PHASE12_OWNER_LEDGER_TAMPER", f"events={sorted(event_names)}"))
    for event in events:
        if event.get("writes_to_source_allowed") is not False:
            errors.append(issue("E_PHASE12_OWNER_LEDGER_TAMPER", f"{event.get('event_id')} authorizes source writes"))
    return errors


def validate_stage_status_and_materials(run_root: Path, expected_ids: list[str], run_state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status_doc = load_json_file(run_root / "stage_status.json", errors, "E_PHASE12_STAGE_STATUS_MISSING")
    material_doc = load_json_file(run_root / "material_inventory.json", errors, "E_PHASE12_MATERIAL_INVENTORY_MISSING")
    frontier = load_json_file(run_root / "frontier_queue.json", errors, "E_PHASE12_FRONTIER_MISSING")
    if isinstance(status_doc, dict):
        statuses = status_doc.get("stages")
        ids = [item.get("stage_id") for item in statuses] if isinstance(statuses, list) else []
        if ids != expected_ids:
            errors.append(issue("E_PHASE12_STAGE_STATUS", f"ids={ids}"))
        for item in statuses if isinstance(statuses, list) else []:
            for field in ["stage_id", "status", "ready_inputs", "produced_materials", "candidate_ref", "validation_ref", "stale_materials", "next_frontier_hint"]:
                if field not in item:
                    errors.append(issue("E_PHASE12_STAGE_STATUS", f"{item.get('stage_id')}.{field}"))
    if isinstance(material_doc, dict):
        materials = material_doc.get("materials")
        if not isinstance(materials, list) or len(materials) != len(expected_ids):
            errors.append(issue("E_PHASE12_MATERIAL_INVENTORY", "material count"))
        else:
            if not any(item.get("status") == "repaired" for item in materials if isinstance(item, dict)):
                errors.append(issue("E_PHASE12_MATERIAL_INVENTORY", "no repaired material"))
            stale_count = sum(1 for item in materials if isinstance(item, dict) and item.get("stale") is True)
            if stale_count >= len(materials):
                errors.append(issue("E_PHASE12_MATERIAL_INVENTORY", "all materials stale"))
            for item in materials:
                if not isinstance(item, dict):
                    continue
                for field in ["material_id", "material_type", "producer_stage", "version", "status", "candidate_ref", "validation_ref", "consumed_by", "support_strength", "stale"]:
                    if field not in item:
                        errors.append(issue("E_PHASE12_MATERIAL_INVENTORY", f"missing {field}"))
    if isinstance(frontier, dict):
        if frontier.get("selection_policy") != "dependency_topology_then_blocker_then_owner_gate_then_frontier":
            errors.append(issue("E_PHASE12_FRONTIER", "selection policy"))
        events = frontier.get("frontier_events")
        if not isinstance(events, list) or len(events) != len(expected_ids):
            errors.append(issue("E_PHASE12_FRONTIER", "event count"))
    return errors


def verify_phase12_run(run_root: Path = DEFAULT_RUN_ROOT, pilot_root: Path = DEFAULT_PILOT) -> list[str]:
    errors: list[str] = []
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    registry = load_json(REGISTRY)
    validators = load_json(VALIDATORS)
    overlays = load_json(OVERLAY_REGISTRY)
    by_validator = {entry["stage_id"]: entry for entry in validators.get("validators", []) if isinstance(entry, dict) and "stage_id" in entry}
    by_overlay_binding = overlay_binding_by_stage(overlays)
    errors.extend(validate_overlay_authority(overlays))

    expected_source_root = Path(str(load_json(pilot_root / "manifest.json")["source_root"])).resolve(strict=True)
    _resolved_run, root_errors = validate_run_root_before_reads(run_root, expected_source_root)
    errors.extend(root_errors)
    if root_errors:
        return errors
    manifest = load_json_file(run_root / "manifest.json", errors, "E_PHASE12_RUN_MANIFEST_MISSING")
    run_state = load_json_file(run_root / "run_state.json", errors, "E_PHASE12_RUN_STATE_MISSING")
    if manifest is None or run_state is None:
        return errors
    if manifest.get("source_snapshot_before") is not None or manifest.get("source_snapshot_after") is not None:
        errors.append(issue("E_PHASE12_SOURCE_SNAPSHOT_CONTRACT", "manifest must use refs, not embedded snapshots"))
    try:
        source_root = Path(str(manifest.get("source_root", ""))).expanduser().resolve(strict=True)
    except Exception as exc:  # noqa: BLE001
        return errors + [issue("E_PHASE12_SOURCE_ROOT", f"invalid source_root {manifest.get('source_root')}: {exc}")]
    if source_root != expected_source_root:
        errors.append(issue("E_PHASE12_SOURCE_ROOT", f"expected {expected_source_root}"))
    if manifest.get("schema_version") != "ppg-phase12-run-manifest/v0.1":
        errors.append(issue("E_PHASE12_MANIFEST_SCHEMA", str(manifest.get("schema_version"))))
    if manifest.get("run_id") != RUN_ID or run_state.get("run_id") != RUN_ID:
        errors.append(issue("E_PHASE12_RUN_ID", "run id mismatch"))
    if manifest.get("source_read_only") is not True or manifest.get("writes_to_source_allowed") is not False or run_state.get("source_read_only") is not True:
        errors.append(issue("E_PHASE12_SOURCE_READ_ONLY", "source boundary"))
    if manifest.get("stage_overlay_registry_ref") != "runtime/stage_overlay_registry.json" or manifest.get("active_stage_overlays") != [NATURE_OVERLAY_ID]:
        errors.append(issue("E_PHASE12_STAGE_OVERLAY_LINK", "manifest overlay link"))
    if run_state.get("stage_overlay_registry_ref") != "runtime/stage_overlay_registry.json" or run_state.get("active_stage_overlays") != [NATURE_OVERLAY_ID]:
        errors.append(issue("E_PHASE12_STAGE_OVERLAY_LINK", "run_state overlay link"))
    before_ref = manifest.get("source_snapshot_before_ref")
    after_ref = manifest.get("source_snapshot_after_ref")
    if before_ref != "source_snapshot.before.json" or after_ref != "source_snapshot.after.json":
        errors.append(issue("E_PHASE12_SOURCE_SNAPSHOT_CONTRACT", f"refs before={before_ref} after={after_ref}"))
    before_path = run_owned_existing_file(run_root, before_ref, "E_PHASE12_RUN_REF", "source_snapshot_before_ref", errors)
    after_path = run_owned_existing_file(run_root, after_ref, "E_PHASE12_RUN_REF", "source_snapshot_after_ref", errors)
    before = load_json_file(before_path, errors, "E_PHASE12_SOURCE_SNAPSHOT_MISSING") if before_path else None
    after = load_json_file(after_path, errors, "E_PHASE12_SOURCE_SNAPSHOT_MISSING") if after_path else None
    if before is not None and after is not None and before != after:
        errors.append(issue("E_PHASE12_SOURCE_SNAPSHOT_DRIFT", "before/after source snapshots differ"))
    if after is not None:
        current = compute_source_snapshot(source_root)
        if current != after:
            errors.append(issue("E_PHASE12_SOURCE_SNAPSHOT_CURRENT_DRIFT", "current source snapshot differs from referenced snapshot"))
    if run_state.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append(issue("E_PHASE12_RUN_STATE_SCHEMA", str(run_state.get("schema_version"))))
    expected_ids = list(registry.get("canonical_stage_ids", []))
    if run_state.get("canonical_stage_ids") != expected_ids:
        errors.append(issue("E_PHASE12_RUN_STAGE_IDS", "canonical_stage_ids mismatch"))
    if "S09" in run_state.get("canonical_stage_ids", []) or any(stage.get("stage_id") == "S09" for stage in run_state.get("stages", []) if isinstance(stage, dict)):
        errors.append(issue("E_PHASE12_BARE_S09", "bare S09 is forbidden"))
    errors.extend(check_no_overclaim(run_state.get("completion_boundary", ""), "run_state.completion_boundary"))
    stages = run_state.get("stages")
    if not isinstance(stages, list) or len(stages) != len(expected_ids):
        errors.append(issue("E_PHASE12_RUN_STAGE_COUNT", f"{len(stages) if isinstance(stages, list) else 'non-list'}"))
        return errors
    stage_ids = [stage.get("stage_id") for stage in stages if isinstance(stage, dict)]
    if stage_ids != expected_ids:
        errors.append(issue("E_PHASE12_RUN_STAGE_ORDER", f"expected={expected_ids} actual={stage_ids}"))
    registry_by_id = {stage["stage_id"]: stage for stage in registry.get("stages", []) if isinstance(stage, dict) and "stage_id" in stage}
    for stage in stages:
        if not isinstance(stage, dict):
            errors.append(issue("E_PHASE12_RUN_STAGE_SHAPE", "stage must be object"))
            continue
        sid = str(stage.get("stage_id"))
        registry_stage = registry_by_id.get(sid, {})
        overlay_binding = by_overlay_binding.get(sid, {})
        if stage.get("controller_owned_completion") is not True:
            errors.append(issue("E_PHASE12_RUN_STAGE_AUTHORITY", f"{sid}.controller_owned_completion"))
        if stage.get("worker_completion_forbidden") is not True:
            errors.append(issue("E_PHASE12_RUN_STAGE_AUTHORITY", f"{sid}.worker_completion_forbidden"))
        errors.extend(check_no_overclaim(stage.get("completion_boundary", ""), f"{sid}.completion_boundary"))
        errors.extend(validate_stage_overlay_record(stage.get("active_stage_overlays"), sid, overlay_binding, f"{sid}.run_state.active_stage_overlays"))
        candidate_path = run_owned_existing_file(run_root, stage.get("candidate_ref"), "E_PHASE12_RUN_REF", f"{sid}.candidate_ref", errors)
        dispatch_path = run_owned_existing_file(run_root, stage.get("dispatch_ref"), "E_PHASE12_RUN_REF", f"{sid}.dispatch_ref", errors)
        validation_path = run_owned_existing_file(run_root, stage.get("validation_ref"), "E_PHASE12_RUN_REF", f"{sid}.validation_ref", errors)
        candidate = load_json_file(candidate_path, errors, "E_PHASE12_CANDIDATE_MISSING") if candidate_path else None
        dispatch = load_json_file(dispatch_path, errors, "E_PHASE12_DISPATCH_MISSING") if dispatch_path else None
        validation = load_json_file(validation_path, errors, "E_PHASE12_VALIDATION_MISSING") if validation_path else None
        if isinstance(candidate, dict):
            errors.extend(validate_candidate(candidate, sid, overlay_binding))
        if isinstance(dispatch, dict):
            errors.extend(validate_dispatch(dispatch, sid, overlay_binding))
            if dispatch.get("candidate_output_path") != stage.get("candidate_ref"):
                errors.append(issue("E_PHASE12_DISPATCH_CONTENT", f"{sid}.candidate_output_path"))
        if isinstance(validation, dict):
            errors.extend(validate_validation_record(validation, sid, by_validator.get(sid, {}), overlay_binding))
            if validation.get("candidate_ref") != stage.get("candidate_ref"):
                errors.append(issue("E_PHASE12_VALIDATION_CONTENT", f"{sid}.candidate_ref"))
        if registry_stage.get("requires_worker_task_packet"):
            if not stage.get("packet_ref"):
                errors.append(issue("E_PHASE12_RUN_PACKET_MISSING", sid))
            else:
                errors.extend(validate_run_packet(run_root, stage, stage.get("packet_ref"), str(stage.get("candidate_ref")), overlay_binding))
        elif stage.get("packet_ref") is not None or stage.get("packet_template_ref") is not None:
            errors.append(issue("E_PHASE12_NON_WORKER_FAKE_PACKET", sid))
    errors.extend(validate_stage_status_and_materials(run_root, expected_ids, run_state))
    dispatch_events = jsonl_events(run_root / "dispatch_ledger.jsonl", errors, "E_PHASE12_DISPATCH_LEDGER_MISSING")
    validation_events = jsonl_events(run_root / "validation_ledger.jsonl", errors, "E_PHASE12_VALIDATION_LEDGER_MISSING")
    global_events = jsonl_events(run_root / "ledger.jsonl", errors, "E_PHASE12_LEDGER_MISSING")
    if sum(1 for event in dispatch_events if event.get("event") == "dispatch_recorded") != len(expected_ids):
        errors.append(issue("E_PHASE12_DISPATCH_LEDGER", "dispatch count"))
    if sum(1 for event in validation_events if event.get("event") == "validation_recorded") != len(expected_ids):
        errors.append(issue("E_PHASE12_VALIDATION_LEDGER", "validation count"))
    if not any(event.get("event") == "run_complete_runtime_test_only" for event in global_events):
        errors.append(issue("E_PHASE12_LEDGER", "missing runtime-test completion event"))
    delivery_path = run_owned_existing_file(run_root, run_state.get("delivery_gate_ref"), "E_PHASE12_RUN_REF", "delivery_gate_ref", errors)
    delivery = load_json_file(delivery_path, errors, "E_PHASE12_DELIVERY_GATE_MISSING") if delivery_path else None
    if isinstance(delivery, dict):
        expected_delivery = {
            "schema_version": "ppg-phase12-delivery-gate/v0.1",
            "run_id": RUN_ID,
            "verdict": "pass_for_runtime_test_only",
            "consumed_stage_count": len(expected_ids),
            "source_read_only_verified": True,
            "no_final_manuscript_claim": True,
            "no_submission_ready_claim": True,
        }
        for key, expected in expected_delivery.items():
            if delivery.get(key) != expected:
                errors.append(issue("E_PHASE12_DELIVERY_GATE", f"{key} expected={expected!r} actual={delivery.get(key)!r}"))
        if delivery.get("consumed_stage_ids") != expected_ids:
            errors.append(issue("E_PHASE12_DELIVERY_GATE", "consumed_stage_ids"))
        errors.extend(check_no_overclaim(delivery.get("completion_boundary", ""), "delivery.completion_boundary"))
        errors.extend(validate_backflow_chain(run_root, delivery))
    else:
        errors.append(issue("E_PHASE12_DELIVERY_GATE", "missing delivery gate"))
    errors.extend(validate_owner_ledger(run_root))
    errors.extend(scan_boundary_files(run_root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Phase12 formal full-flow runtime-test artifacts.")
    parser.add_argument("run_root", nargs="?", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args(argv)
    errors = verify_phase12_run(args.run_root, args.pilot_root)
    if errors:
        print("INVALID Phase12 full-flow run", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE12_FULL_FLOW_RUN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
