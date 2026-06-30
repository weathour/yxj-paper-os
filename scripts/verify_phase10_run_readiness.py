#!/usr/bin/env python3
"""Verify Phase10 real-subagent-run readiness artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import DEFAULT_RUN_ROOT, ROOT, compute_source_snapshot, is_relative_to, load_json
    from ppg_validate_common import load_document
    from validate_packet import validate as validate_packet
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import DEFAULT_RUN_ROOT, ROOT, compute_source_snapshot, is_relative_to, load_json  # type: ignore  # noqa: E402
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402
    from validate_packet import validate as validate_packet  # type: ignore  # noqa: E402

REGISTRY = ROOT / "runtime" / "stage_registry.json"
VALIDATORS = ROOT / "runtime" / "phase10_content_validators.json"
CONTRACT_DIR = ROOT / "examples" / "stage-contracts"
RUN_SCHEMA_VERSION = "ppg-run-state/v0.1"
BANNED_CLAIM_PHRASES = [
    "final paper complete",
    "final manuscript complete",
    "submission ready",
    "ready to submit",
    "publication ready",
]
BASE_REQUIRED_CHECKS = {"source_or_material_trace", "completion_boundary_explicit", "controller_owned_status"}
WORKER_REQUIRED_CHECKS = {"candidate_return_or_missing_material_path", "worker_authority_boundary"}
BACKFLOW_REQUIRED_CHECKS = {"local_backflow_route", "repair_locality"}
EXPORT_REQUIRED_CHECKS = {"owner_gate_or_export_hygiene"}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json_file(path: Path, errors: list[str], code: str) -> Any | None:
    if not path.is_file():
        errors.append(issue(code, rel(path)))
        return None
    try:
        return load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(issue("E_PHASE10_JSON_PARSE", f"{rel(path)}: {exc}"))
        return None


def validate_packet_binding(stage_id: str, contract_ref: str, packet_ref: str) -> list[str]:
    errors: list[str] = []
    packet_path = ROOT / packet_ref
    packet_data, packet_load_errors = load_document(packet_path)
    if packet_load_errors:
        errors.append(issue("E_PHASE10_PACKET_PARSE", f"{packet_ref}: {packet_load_errors[0].message}"))
        return errors
    if not isinstance(packet_data, dict):
        errors.append(issue("E_PHASE10_PACKET_PARSE", f"{packet_ref}: packet must be mapping"))
        return errors
    packet_errors = validate_packet(packet_data)
    if packet_errors:
        errors.append(issue("E_PHASE10_PACKET_INVALID", f"{packet_ref}: {packet_errors[0].code}"))
    if packet_data.get("stage_id") != stage_id or packet_data.get("stage_contract_ref") != contract_ref:
        errors.append(issue("E_PHASE10_PACKET_STAGE_BINDING", f"{stage_id} links {packet_ref} with packet stage_id={packet_data.get('stage_id')} stage_contract_ref={packet_data.get('stage_contract_ref')}"))
    return errors


def verify_validator_registry(registry: dict[str, Any], validators: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_ids = list(registry.get("canonical_stage_ids", []))
    if validators.get("schema_version") != "ppg-phase10-content-validators/v0.1":
        errors.append(issue("E_PHASE10_VALIDATORS_SCHEMA", str(validators.get("schema_version"))))
    if validators.get("canonical_stage_ids") != expected_ids:
        errors.append(issue("E_PHASE10_VALIDATORS_STAGE_SET", "canonical_stage_ids mismatch"))
    entries = validators.get("validators")
    if not isinstance(entries, list):
        return [issue("E_PHASE10_VALIDATORS_SHAPE", "validators must be a list")]
    by_id = {entry.get("stage_id"): entry for entry in entries if isinstance(entry, dict)}
    if sorted(by_id) != sorted(expected_ids):
        errors.append(issue("E_PHASE10_VALIDATORS_STAGE_SET", f"expected={expected_ids} actual={sorted(by_id)}"))
    stage_by_id = {stage["stage_id"]: stage for stage in registry.get("stages", [])}
    for sid in expected_ids:
        entry = by_id.get(sid)
        if not isinstance(entry, dict):
            continue
        dimensions = entry.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) < 3:
            errors.append(issue("E_PHASE10_VALIDATOR_DIMENSIONS", f"{sid} needs at least three dimensions"))
        elif not all(isinstance(item, dict) and item.get("dimension_id") and item.get("name") and item.get("required_evidence") for item in dimensions):
            errors.append(issue("E_PHASE10_VALIDATOR_DIMENSION_SHAPE", sid))
        checks = set(entry.get("required_checks", [])) if isinstance(entry.get("required_checks"), list) else set()
        missing = BASE_REQUIRED_CHECKS - checks
        if stage_by_id.get(sid, {}).get("requires_worker_task_packet"):
            missing |= WORKER_REQUIRED_CHECKS - checks
        if sid in {"S13", "S14", "S15"}:
            missing |= BACKFLOW_REQUIRED_CHECKS - checks
        if sid in {"S16", "G02"}:
            missing |= EXPORT_REQUIRED_CHECKS - checks
        if missing:
            errors.append(issue("E_PHASE10_VALIDATOR_CHECKS", f"{sid} missing {sorted(missing)}"))
    return errors


def verify_contracts_and_packets(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for stage in registry.get("stages", []):
        sid = stage["stage_id"]
        contract = load_json(ROOT / stage["contract_ref"])
        coverage = contract.get("worker_packet_coverage", {})
        status = coverage.get("status")
        if stage.get("requires_worker_task_packet"):
            if status != "linked_strict_packet":
                errors.append(issue("E_PHASE10_WORKER_PACKET_NOT_LINKED", f"{sid} status={status}"))
                continue
            packet_ref = coverage.get("packet_ref")
            if not isinstance(packet_ref, str) or not (ROOT / packet_ref).is_file():
                errors.append(issue("E_PHASE10_WORKER_PACKET_MISSING", f"{sid} {packet_ref}"))
                continue
            errors.extend(validate_packet_binding(sid, stage["contract_ref"], packet_ref))
        elif status != "not_required":
            errors.append(issue("E_PHASE10_FAKE_WORKER_PACKET", f"{sid} status={status}"))
    negative = load_json(CONTRACT_DIR / "invalid-wrong-stage-packet.json")
    neg_packet_ref = negative.get("worker_packet_coverage", {}).get("packet_ref")
    neg_errors = validate_packet_binding(str(negative.get("stage_id")), f"examples/stage-contracts/{negative.get('stage_id')}.stage-contract.json", str(neg_packet_ref))
    if not any("E_PHASE10_PACKET_STAGE_BINDING" in error for error in neg_errors):
        errors.append(issue("E_PHASE10_NEGATIVE_WRONG_STAGE_PACKET", f"wrong-stage negative did not fail: {neg_errors}"))
    return errors


def inside_run_file(path: Path, run_root: Path) -> bool:
    try:
        return path.resolve().relative_to(run_root.resolve()) is not None
    except ValueError:
        return False


def check_no_overclaim(text: Any, context: str) -> list[str]:
    lowered = str(text).lower()
    return [issue("E_PHASE10_COMPLETION_OVERCLAIM", f"{context} contains {phrase!r}") for phrase in BANNED_CLAIM_PHRASES if phrase in lowered]


def verify_run_fixture(run_root: Path, registry: dict[str, Any], validators: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    manifest = load_json_file(run_root / "manifest.json", errors, "E_PHASE10_RUN_MANIFEST_MISSING")
    run_state = load_json_file(run_root / "run_state.json", errors, "E_PHASE10_RUN_STATE_MISSING")
    ledger_path = run_root / "ledger.jsonl"
    if manifest is None or run_state is None:
        return errors
    source_root = Path(str(manifest.get("source_root", ""))).expanduser().resolve(strict=True)
    resolved_run = run_root.resolve(strict=True)
    if not is_relative_to(resolved_run, (ROOT / "runs").resolve(strict=True)):
        errors.append(issue("E_PHASE10_RUN_ROOT", f"run_root outside runtime runs: {run_root}"))
    if is_relative_to(resolved_run, source_root) or resolved_run == source_root:
        errors.append(issue("E_PHASE10_RUN_ROOT_UNDER_SOURCE", str(run_root)))
    if manifest.get("source_read_only") is not True or manifest.get("writes_to_source_allowed") is not False:
        errors.append(issue("E_PHASE10_SOURCE_READ_ONLY", "manifest source boundary must be read-only"))
    before = manifest.get("source_snapshot_before")
    after = manifest.get("source_snapshot_after")
    if before != after:
        errors.append(issue("E_PHASE10_SOURCE_SNAPSHOT_DRIFT", "manifest before/after source snapshots differ"))
    current = compute_source_snapshot(source_root)
    if current != after:
        changed: list[str] = []
        if isinstance(after, dict):
            before_entries = after.get("entries", {}) if isinstance(after.get("entries"), dict) else {}
            current_entries = current.get("entries", {})
            if isinstance(current_entries, dict):
                keys = sorted(set(before_entries) | set(current_entries))
                changed = [key for key in keys if before_entries.get(key) != current_entries.get(key)][:8]
        errors.append(issue("E_PHASE10_SOURCE_SNAPSHOT_CURRENT_DRIFT", f"current source snapshot differs; changed={changed}"))
    expected_ids = list(registry.get("canonical_stage_ids", []))
    if run_state.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append(issue("E_PHASE10_RUN_STATE_SCHEMA", str(run_state.get("schema_version"))))
    if run_state.get("canonical_stage_ids") != expected_ids:
        errors.append(issue("E_PHASE10_RUN_STAGE_IDS", "canonical_stage_ids mismatch"))
    if "S09" in run_state.get("canonical_stage_ids", []) or any(stage.get("stage_id") == "S09" for stage in run_state.get("stages", []) if isinstance(stage, dict)):
        errors.append(issue("E_PHASE10_BARE_S09", "bare S09 is forbidden"))
    errors.extend(check_no_overclaim(run_state.get("completion_boundary", ""), "run_state.completion_boundary"))
    stages = run_state.get("stages")
    if not isinstance(stages, list) or len(stages) != len(expected_ids):
        errors.append(issue("E_PHASE10_RUN_STAGE_COUNT", f"{len(stages) if isinstance(stages, list) else 'non-list'}"))
        return errors
    by_validator = {entry["stage_id"]: entry for entry in validators.get("validators", []) if isinstance(entry, dict) and "stage_id" in entry}
    stage_ids = [stage.get("stage_id") for stage in stages if isinstance(stage, dict)]
    if stage_ids != expected_ids:
        errors.append(issue("E_PHASE10_RUN_STAGE_ORDER", f"expected={expected_ids} actual={stage_ids}"))
    ledger_events: list[dict[str, Any]] = []
    if not ledger_path.is_file():
        errors.append(issue("E_PHASE10_LEDGER_MISSING", rel(ledger_path)))
    else:
        for lineno, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                ledger_events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append(issue("E_PHASE10_LEDGER_PARSE", f"line {lineno}: {exc}"))
    for stage in stages:
        if not isinstance(stage, dict):
            errors.append(issue("E_PHASE10_RUN_STAGE_SHAPE", "stage must be object"))
            continue
        sid = str(stage.get("stage_id"))
        errors.extend(check_no_overclaim(stage.get("completion_claim", ""), f"{sid}.completion_claim"))
        for ref_key in ["dispatch_ref", "validation_ref", "candidate_ref"]:
            ref = stage.get(ref_key)
            path = run_root / str(ref)
            if not isinstance(ref, str) or not inside_run_file(path, run_root) or not path.is_file():
                errors.append(issue("E_PHASE10_RUN_REF", f"{sid}.{ref_key}={ref}"))
        if stage.get("content_validator_id") != by_validator.get(sid, {}).get("validator_id"):
            errors.append(issue("E_PHASE10_RUN_VALIDATOR_LINK", sid))
        contract = load_json(ROOT / str(stage.get("stage_contract_ref"))) if isinstance(stage.get("stage_contract_ref"), str) and (ROOT / str(stage.get("stage_contract_ref"))).is_file() else None
        if contract and contract.get("requires_worker_task_packet"):
            if not stage.get("packet_ref"):
                errors.append(issue("E_PHASE10_RUN_PACKET_LINK", sid))
            elif validate_packet_binding(sid, str(stage.get("stage_contract_ref")), str(stage.get("packet_ref"))):
                errors.append(issue("E_PHASE10_RUN_PACKET_BINDING", sid))
    if ledger_events:
        dispatch_count = sum(1 for event in ledger_events if event.get("event") == "stage_dispatch")
        validation_count = sum(1 for event in ledger_events if event.get("event") == "stage_validation")
        if dispatch_count != len(expected_ids) or validation_count != len(expected_ids):
            errors.append(issue("E_PHASE10_LEDGER_COUNTS", f"dispatch={dispatch_count} validation={validation_count}"))
        if len(ledger_events) != 2 * len(expected_ids) + 2:
            errors.append(issue("E_PHASE10_LEDGER_LENGTH", str(len(ledger_events))))
    return errors


def verify_run_readiness(run_root: Path = DEFAULT_RUN_ROOT) -> list[str]:
    errors: list[str] = []
    registry = load_json(REGISTRY)
    validators = load_json(VALIDATORS)
    errors.extend(verify_validator_registry(registry, validators))
    errors.extend(verify_contracts_and_packets(registry))
    errors.extend(verify_run_fixture(run_root, registry, validators))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Phase10 real-subagent-run readiness fixture.")
    parser.add_argument("run_root", nargs="?", type=Path, default=DEFAULT_RUN_ROOT)
    args = parser.parse_args(argv)
    errors = verify_run_readiness(args.run_root)
    if errors:
        print("INVALID Phase10 run readiness", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE10_RUN_READINESS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
