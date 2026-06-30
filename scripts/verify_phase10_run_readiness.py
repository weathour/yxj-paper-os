#!/usr/bin/env python3
"""Verify Phase10 real-subagent-run readiness artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import DEFAULT_PILOT, DEFAULT_RUN_ROOT, ROOT, RUN_ID, compute_source_snapshot, is_relative_to, load_json
    from ppg_validate_common import load_document
    from validate_packet import validate as validate_packet
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import DEFAULT_PILOT, DEFAULT_RUN_ROOT, ROOT, RUN_ID, compute_source_snapshot, is_relative_to, load_json  # type: ignore  # noqa: E402
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


def scoped_repo_path(ref: Any, prefix: str, code: str, sid: str) -> tuple[Path | None, list[str]]:
    if not isinstance(ref, str) or not ref.strip():
        return None, [issue(code, f"{sid} {ref}")]
    raw = Path(ref)
    if raw.is_absolute() or ref.startswith("~") or "\\" in ref or "\x00" in ref or any(part in {"", ".", ".."} for part in ref.split("/")):
        return None, [issue(code, f"{sid} {ref}")]
    raw_path = ROOT / ref
    if raw_path.is_symlink():
        return None, [issue(code, f"{sid} {ref}")]
    path = raw_path.resolve(strict=False)
    allowed_root = (ROOT / prefix).resolve(strict=True)
    if not is_relative_to(path, allowed_root):
        return None, [issue(code, f"{sid} {ref}")]
    if path.is_symlink():
        return None, [issue(code, f"{sid} {ref}")]
    return path, []


def safe_run_ref(run_root: Path, ref: Any, code: str, context: str) -> tuple[Path | None, list[str]]:
    if not isinstance(ref, str) or not ref.strip():
        return None, [issue(code, f"{context}={ref}")]
    raw = Path(ref)
    if raw.is_absolute() or ref.startswith("~") or "\\" in ref or "\x00" in ref or any(part in {"", ".", ".."} for part in ref.split("/")):
        return None, [issue(code, f"{context}={ref}")]
    path = run_root / ref
    if not inside_run_file(path, run_root):
        return None, [issue(code, f"{context}={ref}")]
    if path.is_symlink():
        return None, [issue(code, f"{context}={ref}")]
    return path, []


def validate_packet_binding(stage_id: str, contract_ref: str, packet_ref: str) -> list[str]:
    errors: list[str] = []
    packet_path, scope_errors = scoped_repo_path(packet_ref, "examples/packets", "E_PHASE10_PACKET_REF_SCOPE", stage_id)
    errors.extend(scope_errors)
    if packet_path is None:
        return errors
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
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("stage_id"), str):
            by_id[entry["stage_id"]] = entry
    actual_ids = sorted(by_id)
    if actual_ids != sorted(expected_ids):
        errors.append(issue("E_PHASE10_VALIDATORS_STAGE_SET", f"expected={expected_ids} actual={actual_ids}"))
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
            packet_path, scope_errors = scoped_repo_path(packet_ref, "examples/packets", "E_PHASE10_PACKET_REF_SCOPE", sid)
            errors.extend(scope_errors)
            return_ref, return_scope_errors = scoped_repo_path(coverage.get("return_contract_ref"), "schemas", "E_PHASE10_RETURN_CONTRACT_REF_SCOPE", sid)
            errors.extend(return_scope_errors)
            if return_ref is not None and return_ref.name != "ppg-candidate-return.schema.json":
                errors.append(issue("E_PHASE10_RETURN_CONTRACT_REF_SCOPE", f"{sid} {coverage.get('return_contract_ref')}"))
            if packet_path is None or not packet_path.is_file():
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


def validate_run_packet(run_root: Path, stage: dict[str, Any], contract: dict[str, Any], packet_ref: Any, candidate_ref: str) -> list[str]:
    sid = str(stage.get("stage_id"))
    packet_path, ref_errors = safe_run_ref(run_root, packet_ref, "E_PHASE10_RUN_PACKET_REF", f"{sid}.packet_ref")
    errors = list(ref_errors)
    if packet_path is None:
        return errors
    packet_data, packet_load_errors = load_document(packet_path)
    if packet_load_errors:
        return errors + [issue("E_PHASE10_RUN_PACKET_PARSE", f"{sid} {packet_ref}: {packet_load_errors[0].message}")]
    if not isinstance(packet_data, dict):
        return errors + [issue("E_PHASE10_RUN_PACKET_PARSE", f"{sid} {packet_ref}: packet must be mapping")]
    packet_errors = validate_packet(packet_data)
    if packet_errors:
        errors.append(issue("E_PHASE10_RUN_PACKET_INVALID", f"{sid} {packet_ref}: {packet_errors[0].code}"))
    contract_ref = f"examples/stage-contracts/{sid}.stage-contract.json"
    if packet_data.get("stage_id") != sid or packet_data.get("stage_contract_ref") != contract_ref:
        errors.append(issue("E_PHASE10_RUN_PACKET_STAGE_BINDING", f"{sid} packet stage_id={packet_data.get('stage_id')} stage_contract_ref={packet_data.get('stage_contract_ref')}"))
    expected_output = rel(run_root / candidate_ref)
    if packet_data.get("output_artifact_path") != expected_output or packet_data.get("allowed_write_paths") != [expected_output]:
        errors.append(issue("E_PHASE10_RUN_PACKET_OUTPUT_BOUNDARY", f"{sid} expected run-owned output {expected_output}"))
    output_path = ROOT / expected_output
    if not inside_run_file(output_path, run_root):
        errors.append(issue("E_PHASE10_RUN_PACKET_OUTPUT_BOUNDARY", f"{sid} output escapes run root"))
    if contract.get("requires_worker_task_packet") is not True:
        errors.append(issue("E_PHASE10_RUN_PACKET_UNEXPECTED", sid))
    return errors


def verify_stage_artifacts(run_root: Path, stage: dict[str, Any], registry_stage: dict[str, Any], contract: dict[str, Any], validator: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sid = str(stage.get("stage_id"))
    dispatch_path, dispatch_ref_errors = safe_run_ref(run_root, stage.get("dispatch_ref"), "E_PHASE10_RUN_REF", f"{sid}.dispatch_ref")
    validation_path, validation_ref_errors = safe_run_ref(run_root, stage.get("validation_ref"), "E_PHASE10_RUN_REF", f"{sid}.validation_ref")
    candidate_path, candidate_ref_errors = safe_run_ref(run_root, stage.get("candidate_ref"), "E_PHASE10_RUN_REF", f"{sid}.candidate_ref")
    errors.extend(dispatch_ref_errors)
    errors.extend(validation_ref_errors)
    errors.extend(candidate_ref_errors)
    dispatch = load_json_file(dispatch_path, errors, "E_PHASE10_DISPATCH_MISSING") if dispatch_path else None
    validation = load_json_file(validation_path, errors, "E_PHASE10_VALIDATION_MISSING") if validation_path else None
    candidate = load_json_file(candidate_path, errors, "E_PHASE10_CANDIDATE_MISSING") if candidate_path else None
    candidate_ref = str(stage.get("candidate_ref"))

    if isinstance(dispatch, dict):
        expected_dispatch = {
            "schema_version": "ppg-phase10-dispatch-record/v0.1",
            "run_id": RUN_ID,
            "stage_id": sid,
            "stage_name": registry_stage.get("stage_name"),
            "stage_contract_ref": stage.get("stage_contract_ref"),
            "content_validator_ref": "runtime/phase10_content_validators.json",
            "content_validator_id": validator.get("validator_id"),
            "source_read_only": True,
            "candidate_output_path": candidate_ref,
        }
        for key, expected in expected_dispatch.items():
            if dispatch.get(key) != expected:
                errors.append(issue("E_PHASE10_DISPATCH_CONTENT", f"{sid}.{key} expected={expected!r} actual={dispatch.get(key)!r}"))
        boundary = dispatch.get("worker_authority")
        if not isinstance(boundary, dict) or boundary.get("completion_forbidden") is not True or boundary.get("no_recursive_orchestration") is not True or boundary.get("controller_owned_completion") is not True:
            errors.append(issue("E_PHASE10_DISPATCH_WORKER_AUTHORITY", sid))
        errors.extend(check_no_overclaim(dispatch.get("completion_claim", ""), f"{sid}.dispatch.completion_claim"))
        if dispatch.get("packet_ref") != stage.get("packet_ref"):
            errors.append(issue("E_PHASE10_DISPATCH_PACKET_LINK", sid))
        if dispatch.get("packet_template_ref") != stage.get("packet_template_ref"):
            errors.append(issue("E_PHASE10_DISPATCH_PACKET_TEMPLATE_LINK", sid))

    if isinstance(validation, dict):
        expected_validation = {
            "schema_version": "ppg-phase10-stage-validation/v0.1",
            "run_id": RUN_ID,
            "stage_id": sid,
            "validator_id": validator.get("validator_id"),
            "dimension_count": len(validator.get("dimensions", [])),
            "required_checks": validator.get("required_checks", []),
            "status": "owner_gated" if sid == "G02" else "pass",
        }
        for key, expected in expected_validation.items():
            if validation.get(key) != expected:
                errors.append(issue("E_PHASE10_VALIDATION_CONTENT", f"{sid}.{key} expected={expected!r} actual={validation.get(key)!r}"))
        errors.extend(check_no_overclaim(validation.get("completion_boundary", ""), f"{sid}.validation.completion_boundary"))

    if isinstance(candidate, dict):
        expected_candidate = {
            "schema_version": "ppg-phase10-candidate-placeholder/v0.1",
            "stage_id": sid,
            "stage_name": registry_stage.get("stage_name"),
            "packet_ref": stage.get("packet_ref"),
            "validator_id": validator.get("validator_id"),
            "expected_outputs": registry_stage.get("produces", []),
        }
        for key, expected in expected_candidate.items():
            if candidate.get(key) != expected:
                errors.append(issue("E_PHASE10_CANDIDATE_CONTENT", f"{sid}.{key} expected={expected!r} actual={candidate.get(key)!r}"))
        errors.extend(check_no_overclaim(candidate.get("completion_boundary", ""), f"{sid}.candidate.completion_boundary"))

    if contract.get("requires_worker_task_packet"):
        errors.extend(validate_run_packet(run_root, stage, contract, stage.get("packet_ref"), candidate_ref))
    elif stage.get("packet_ref") is not None or stage.get("packet_template_ref") is not None:
        errors.append(issue("E_PHASE10_RUN_PACKET_UNEXPECTED", sid))
    return errors


def verify_run_fixture(run_root: Path, registry: dict[str, Any], validators: dict[str, Any], pilot_root: Path = DEFAULT_PILOT) -> list[str]:
    errors: list[str] = []
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    manifest = load_json_file(run_root / "manifest.json", errors, "E_PHASE10_RUN_MANIFEST_MISSING")
    run_state = load_json_file(run_root / "run_state.json", errors, "E_PHASE10_RUN_STATE_MISSING")
    ledger_path = run_root / "ledger.jsonl"
    if manifest is None or run_state is None:
        return errors
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    expected_source_root = Path(str(load_json(pilot_root / "manifest.json")["source_root"])).resolve(strict=True)
    try:
        source_root = Path(str(manifest.get("source_root", ""))).expanduser().resolve(strict=True)
    except Exception as exc:  # noqa: BLE001
        return errors + [issue("E_PHASE10_SOURCE_ROOT", f"invalid source_root {manifest.get('source_root')}: {exc}")]
    if source_root != expected_source_root or manifest.get("pilot_root") != rel(pilot_root):
        errors.append(issue("E_PHASE10_SOURCE_ROOT", f"expected source_root={expected_source_root} pilot_root={rel(pilot_root)}"))
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
    registry_by_id = {stage["stage_id"]: stage for stage in registry.get("stages", []) if isinstance(stage, dict) and "stage_id" in stage}
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
        if stage.get("content_validator_id") != by_validator.get(sid, {}).get("validator_id"):
            errors.append(issue("E_PHASE10_RUN_VALIDATOR_LINK", sid))
        contract = load_json(ROOT / str(stage.get("stage_contract_ref"))) if isinstance(stage.get("stage_contract_ref"), str) and (ROOT / str(stage.get("stage_contract_ref"))).is_file() else None
        if contract and sid in registry_by_id:
            errors.extend(verify_stage_artifacts(run_root, stage, registry_by_id[sid], contract, by_validator.get(sid, {})))
    if ledger_events:
        dispatch_count = sum(1 for event in ledger_events if event.get("event") == "stage_dispatch")
        validation_count = sum(1 for event in ledger_events if event.get("event") == "stage_validation")
        if dispatch_count != len(expected_ids) or validation_count != len(expected_ids):
            errors.append(issue("E_PHASE10_LEDGER_COUNTS", f"dispatch={dispatch_count} validation={validation_count}"))
        if len(ledger_events) != 2 * len(expected_ids) + 2:
            errors.append(issue("E_PHASE10_LEDGER_LENGTH", str(len(ledger_events))))
    return errors


def verify_run_readiness(run_root: Path = DEFAULT_RUN_ROOT, pilot_root: Path = DEFAULT_PILOT) -> list[str]:
    errors: list[str] = []
    registry = load_json(REGISTRY)
    validators = load_json(VALIDATORS)
    errors.extend(verify_validator_registry(registry, validators))
    errors.extend(verify_contracts_and_packets(registry))
    errors.extend(verify_run_fixture(run_root, registry, validators, pilot_root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Phase10 real-subagent-run readiness fixture.")
    parser.add_argument("run_root", nargs="?", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args(argv)
    errors = verify_run_readiness(args.run_root, args.pilot_root)
    if errors:
        print("INVALID Phase10 run readiness", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE10_RUN_READINESS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
