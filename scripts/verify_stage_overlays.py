#!/usr/bin/env python3
"""Verify PPG stage overlay registries and Nature overlay integration."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import load_document
    from validate_packet import validate as validate_packet
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402
    from validate_packet import validate as validate_packet  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "runtime" / "stage_registry.json"
OVERLAY_REGISTRY = ROOT / "runtime" / "stage_overlay_registry.json"
VALIDATORS = ROOT / "runtime" / "phase10_content_validators.json"
FIXTURE_DIR = ROOT / "examples" / "overlays"
SCHEMA_VERSION = "ppg-stage-overlay-registry/v0.1"
REQUIRED_OVERLAY_ID = "nature_expert_writing"
REQUIRED_AUTHORITY_FLAGS = {
    "stage_local_only",
    "no_new_department",
    "controller_owned_completion",
    "worker_completion_forbidden",
    "no_recursive_orchestration",
}
BINDING_STRENGTHS = {"primary", "support", "light", "governance", "derivative"}
BASE_OVERLAY_CHECKS = {"stage_overlay_binding", "no_department_route"}
WORKER_OVERLAY_CHECKS = {"stage_overlay_packet_clause"}
REQUIRED_NEGATIVE_CASES = {
    "invalid-unknown-stage.json": "E_STAGE_OVERLAY_UNKNOWN_STAGE",
    "invalid-bare-s09.json": "E_STAGE_OVERLAY_BARE_S09",
    "invalid-authority-expansion.json": "E_STAGE_OVERLAY_AUTHORITY",
    "invalid-packet-clause-transport.json": "E_STAGE_OVERLAY_PACKET_TRANSPORT",
    "invalid-missing-worker-packet-clause.json": "E_STAGE_OVERLAY_PACKET_CLAUSE",
    "invalid-missing-validator-coverage.json": "E_STAGE_OVERLAY_VALIDATOR_COVERAGE",
    "invalid-active-department-loop.json": "E_STAGE_OVERLAY_DEPARTMENT_ROUTE",
    "invalid-backflow-target.json": "E_STAGE_OVERLAY_BACKFLOW_TARGET",
    "invalid-missing-nature-overlay.json": "E_STAGE_OVERLAY_REQUIRED_OVERLAY",
    "invalid-missing-primary-stage-binding.json": "E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING",
    "invalid-duplicate-stage-binding.json": "E_STAGE_OVERLAY_DUPLICATE_BINDING",
    "invalid-primary-binding-mismatch.json": "E_STAGE_OVERLAY_PRIMARY_BINDING_MISMATCH",
}
POSITIVE_CASES = ["nature_stage_overlay.valid.json", "valid-doc-negation-not-department.json"]


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def canonical_stage_ids(stage_registry: dict[str, Any]) -> list[str]:
    return list(stage_registry.get("canonical_stage_ids", []))


def stage_by_id(stage_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {stage["stage_id"]: stage for stage in stage_registry.get("stages", []) if isinstance(stage, dict) and isinstance(stage.get("stage_id"), str)}


def validator_by_id(validators: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["stage_id"]: entry for entry in validators.get("validators", []) if isinstance(entry, dict) and isinstance(entry.get("stage_id"), str)}


def _active_department_route_detected(value: Any, key: str = "") -> bool:
    """Reject active self-managing route semantics without rejecting explanatory prose.

    Notes/descriptions may say "not a department". Active routing fields may not
    describe autonomous departments or self-certifying execution.
    """
    if isinstance(value, dict):
        if value.get("no_new_department") is False:
            return True
        if value.get("overlay_dispatch_allowed") is True:
            return True
        if value.get("worker_completion_forbidden") is False:
            return True
        if value.get("controller_owned_completion") is False:
            return True
        if value.get("completion_owner") in {"worker", "overlay", "department"}:
            return True
        for child_key, child_value in value.items():
            if _active_department_route_detected(child_value, str(child_key)):
                return True
    elif isinstance(value, list):
        return any(_active_department_route_detected(item, key) for item in value)
    elif isinstance(value, str):
        active_keys = {"route_kind", "dispatch_model", "active_route", "execution_model", "completion_owner"}
        lowered = value.lower()
        if key in active_keys and any(token in lowered for token in ("department_loop", "autonomous_department", "self_certifying", "self_managed_department")):
            return True
        if "$yxj-paper-os" in lowered or "$yxj-plugin-incubator" in lowered:
            return True
    return False


def _validate_overlay_binding_shape(binding: dict[str, Any], canonical: set[str], stage_map: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    sid = binding.get("stage_id")
    if sid == "S09":
        errors.append(issue("E_STAGE_OVERLAY_BARE_S09", "bare S09 is forbidden; use S09A/S09B"))
    if not isinstance(sid, str) or sid not in canonical:
        errors.append(issue("E_STAGE_OVERLAY_UNKNOWN_STAGE", str(sid)))
        return errors
    if binding.get("binding_strength") not in BINDING_STRENGTHS:
        errors.append(issue("E_STAGE_OVERLAY_BINDING_STRENGTH", f"{sid} {binding.get('binding_strength')}"))
    for field in ["input_controls", "output_materials", "packet_clauses", "validator_checks"]:
        if not is_non_empty_string_list(binding.get(field)):
            code = "E_STAGE_OVERLAY_PACKET_CLAUSE" if field == "packet_clauses" else "E_STAGE_OVERLAY_BINDING_FIELD"
            if field == "validator_checks":
                code = "E_STAGE_OVERLAY_VALIDATOR_COVERAGE"
            errors.append(issue(code, f"{sid}.{field} must be a non-empty string list"))
    targets = binding.get("backflow_targets")
    if not isinstance(targets, list) or not targets or not all(isinstance(target, str) and target.strip() for target in targets):
        errors.append(issue("E_STAGE_OVERLAY_BACKFLOW_TARGET", f"{sid}.backflow_targets must be a non-empty string list"))
    else:
        target_list = [str(target) for target in targets]
        if any(target not in canonical for target in target_list):
            errors.append(issue("E_STAGE_OVERLAY_BACKFLOW_TARGET", f"{sid} invalid targets={target_list}"))
    if sid == "G02" and binding.get("binding_strength") == "primary":
        errors.append(issue("E_STAGE_OVERLAY_DEPARTMENT_ROUTE", "G02 cannot become the main writing cognition route"))
    if sid == "S03" and binding.get("binding_strength") not in {"support", "light"}:
        errors.append(issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", "S03 must remain support/light and gated through S04"))
    if stage_map.get(sid, {}).get("requires_worker_task_packet"):
        clauses = binding.get("packet_clauses", []) if isinstance(binding.get("packet_clauses"), list) else []
        if not any(str(clause).startswith("nature_overlay_ref:") for clause in clauses) or not any(str(clause) == f"nature_stage_binding:{sid}" for clause in clauses):
            errors.append(issue("E_STAGE_OVERLAY_PACKET_CLAUSE", f"{sid} worker stage missing overlay packet clauses"))
    return errors


def _validate_packet_clause_transport(data: dict[str, Any]) -> list[str]:
    transport = data.get("packet_clause_transport")
    if not isinstance(transport, dict):
        return [issue("E_STAGE_OVERLAY_PACKET_TRANSPORT", "packet_clause_transport must be object")]
    expected_keys = ["nature_overlay_ref", "nature_overlay_stage_binding", "nature_overlay_packet_clauses"]
    errors: list[str] = []
    if transport.get("top_level_packet_fields_forbidden") is not True:
        errors.append(issue("E_STAGE_OVERLAY_PACKET_TRANSPORT", "top_level_packet_fields_forbidden must be true"))
    if transport.get("mandatory_controls_keys") != expected_keys:
        errors.append(issue("E_STAGE_OVERLAY_PACKET_TRANSPORT", f"mandatory_controls_keys must be {expected_keys}"))
    if transport.get("validator_prefix") != f"stage_overlay:{REQUIRED_OVERLAY_ID}:":
        errors.append(issue("E_STAGE_OVERLAY_PACKET_TRANSPORT", f"validator_prefix must be stage_overlay:{REQUIRED_OVERLAY_ID}:"))
    return errors


def validate_overlay_registry(data: Any, stage_registry: dict[str, Any] | None = None, validators: dict[str, Any] | None = None, *, check_repo_integration: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [issue("E_STAGE_OVERLAY_SHAPE", "overlay registry must be an object")]
    stage_registry_data: dict[str, Any] = stage_registry if stage_registry is not None else load_json(REGISTRY)
    validators_data: dict[str, Any] = validators if validators is not None else load_json(VALIDATORS)
    canonical = set(canonical_stage_ids(stage_registry_data))
    canonical_order = canonical_stage_ids(stage_registry_data)
    stage_map = stage_by_id(stage_registry_data)
    validator_map = validator_by_id(validators_data)

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(issue("E_STAGE_OVERLAY_SCHEMA", str(data.get("schema_version"))))
    if data.get("registry_ref") != "runtime/stage_registry.json":
        errors.append(issue("E_STAGE_OVERLAY_REGISTRY_REF", str(data.get("registry_ref"))))
    errors.extend(_validate_packet_clause_transport(data))
    overlays = data.get("overlays")
    if not isinstance(overlays, list) or not overlays:
        return errors + [issue("E_STAGE_OVERLAY_REQUIRED_OVERLAY", "overlays must include nature_expert_writing")]
    by_overlay = {overlay.get("overlay_id"): overlay for overlay in overlays if isinstance(overlay, dict)}
    overlay = by_overlay.get(REQUIRED_OVERLAY_ID)
    if not isinstance(overlay, dict):
        return errors + [issue("E_STAGE_OVERLAY_REQUIRED_OVERLAY", "nature_expert_writing overlay is required")]

    authority = overlay.get("authority_model")
    if not isinstance(authority, dict):
        errors.append(issue("E_STAGE_OVERLAY_AUTHORITY", "authority_model must be object"))
    else:
        for flag in REQUIRED_AUTHORITY_FLAGS:
            if authority.get(flag) is not True:
                errors.append(issue("E_STAGE_OVERLAY_AUTHORITY", f"{flag} must be true"))
        if authority.get("overlay_dispatch_allowed") is not False:
            errors.append(issue("E_STAGE_OVERLAY_AUTHORITY", "overlay_dispatch_allowed must be false"))
        if authority.get("route_kind") != "stage_local_overlay":
            errors.append(issue("E_STAGE_OVERLAY_DEPARTMENT_ROUTE", f"route_kind={authority.get('route_kind')}"))
    if _active_department_route_detected(data):
        errors.append(issue("E_STAGE_OVERLAY_DEPARTMENT_ROUTE", "active autonomous department/self-certifying route semantics are forbidden"))

    required_stage_bindings = overlay.get("required_stage_bindings")
    if required_stage_bindings != canonical_order:
        errors.append(issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", "required_stage_bindings must match canonical stage order"))
    primary = overlay.get("primary_stage_bindings")
    primary_list: list[str] = []
    if not isinstance(primary, list) or not primary or not all(isinstance(stage, str) and stage.strip() for stage in primary):
        errors.append(issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", "primary_stage_bindings must be non-empty"))
    else:
        primary_list = [str(stage) for stage in primary]
        if any(stage not in canonical for stage in primary_list):
            errors.append(issue("E_STAGE_OVERLAY_UNKNOWN_STAGE", f"primary_stage_bindings={primary_list}"))
    bindings = overlay.get("stage_bindings")
    if not isinstance(bindings, list) or not bindings:
        return errors + [issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", "stage_bindings required")]
    binding_by_id: dict[str, dict[str, Any]] = {}
    binding_order: list[str] = []
    seen_stage_ids: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict):
            errors.append(issue("E_STAGE_OVERLAY_BINDING_FIELD", "stage binding must be object"))
            continue
        sid = binding.get("stage_id")
        if isinstance(sid, str):
            if sid in seen_stage_ids:
                errors.append(issue("E_STAGE_OVERLAY_DUPLICATE_BINDING", f"duplicate stage binding {sid}"))
            seen_stage_ids.add(sid)
            binding_order.append(sid)
            binding_by_id[sid] = binding
        errors.extend(_validate_overlay_binding_shape(binding, canonical, stage_map))
    if binding_order != canonical_order:
        errors.append(issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", f"stage_bindings must match canonical order; actual={binding_order}"))
    missing_all = [sid for sid in canonical_order if sid not in binding_by_id]
    if missing_all:
        errors.append(issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", f"missing stage bindings={missing_all}"))
    if primary_list:
        missing_primary = [sid for sid in primary_list if sid not in binding_by_id]
        if missing_primary:
            errors.append(issue("E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING", f"missing primary stage bindings={missing_primary}"))
        derived_primary = [sid for sid in canonical_order if binding_by_id.get(sid, {}).get("binding_strength") == "primary"]
        if primary_list != derived_primary:
            errors.append(issue("E_STAGE_OVERLAY_PRIMARY_BINDING_MISMATCH", f"primary_stage_bindings={primary_list} derived={derived_primary}"))

    if check_repo_integration:
        for sid, stage in stage_map.items():
            binding = binding_by_id.get(sid)
            if not binding:
                continue
            contract_path = ROOT / str(stage.get("contract_ref"))
            contract = load_json(contract_path)
            overlays_meta = contract.get("stage_local_overlays")
            if not isinstance(overlays_meta, list) or not any(item.get("overlay_id") == REQUIRED_OVERLAY_ID and item.get("binding_strength") == binding.get("binding_strength") for item in overlays_meta if isinstance(item, dict)):
                errors.append(issue("E_STAGE_OVERLAY_CONTRACT_LINK", f"{sid} missing contract overlay metadata"))
            validator = validator_map.get(sid, {})
            checks = set(validator.get("required_checks", [])) if isinstance(validator.get("required_checks"), list) else set()
            missing_checks = BASE_OVERLAY_CHECKS - checks
            if stage.get("requires_worker_task_packet"):
                missing_checks |= WORKER_OVERLAY_CHECKS - checks
            if missing_checks:
                errors.append(issue("E_STAGE_OVERLAY_VALIDATOR_COVERAGE", f"{sid} missing validator checks={sorted(missing_checks)}"))
            packet_ref = contract.get("worker_packet_coverage", {}).get("packet_ref")
            if stage.get("requires_worker_task_packet") and packet_ref:
                packet_data, packet_errors = load_document(ROOT / str(packet_ref))
                if packet_errors or not isinstance(packet_data, dict):
                    detail = packet_errors[0].message if packet_errors else "packet must be mapping"
                    errors.append(issue("E_STAGE_OVERLAY_PACKET_CLAUSE", f"{sid} cannot load packet {packet_ref}: {detail}"))
                    continue
                packet_validate_errors = validate_packet(packet_data)
                if packet_validate_errors:
                    errors.append(issue("E_STAGE_OVERLAY_PACKET_CLAUSE", f"{sid} packet invalid: {packet_validate_errors[0].code}"))
                controls = packet_data.get("mandatory_controls")
                validators_list = packet_data.get("validators")
                if not isinstance(controls, dict) or controls.get("nature_overlay_ref") != "runtime/stage_overlay_registry.json#nature_expert_writing" or controls.get("nature_overlay_stage_binding") != sid:
                    errors.append(issue("E_STAGE_OVERLAY_PACKET_CLAUSE", f"{sid} missing mandatory_controls overlay refs"))
                expected_validator = f"stage_overlay:nature_expert_writing:{sid}"
                if not isinstance(validators_list, list) or expected_validator not in validators_list:
                    errors.append(issue("E_STAGE_OVERLAY_PACKET_CLAUSE", f"{sid} missing packet validator {expected_validator}"))
    return errors


def run_fixture_matrix(stage_registry: dict[str, Any], validators: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for filename in POSITIVE_CASES:
        path = FIXTURE_DIR / filename
        if not path.is_file():
            errors.append(issue("E_STAGE_OVERLAY_FIXTURE_MISSING", filename))
            continue
        fixture_errors = validate_overlay_registry(load_json(path), stage_registry, validators, check_repo_integration=False)
        if fixture_errors:
            errors.append(issue("E_STAGE_OVERLAY_POSITIVE_FIXTURE", f"{filename} failed: {fixture_errors}"))
    for filename, expected_code in REQUIRED_NEGATIVE_CASES.items():
        path = FIXTURE_DIR / filename
        if not path.is_file():
            errors.append(issue("E_STAGE_OVERLAY_FIXTURE_MISSING", filename))
            continue
        fixture_errors = validate_overlay_registry(load_json(path), stage_registry, validators, check_repo_integration=False)
        if not any(expected_code in error for error in fixture_errors):
            errors.append(issue("E_STAGE_OVERLAY_NEGATIVE_CASE", f"{filename} did not trigger {expected_code}: {fixture_errors}"))
    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    overlay_path = Path(args[0]) if args else OVERLAY_REGISTRY
    if not overlay_path.is_absolute():
        overlay_path = ROOT / overlay_path
    stage_registry = load_json(REGISTRY)
    validators = load_json(VALIDATORS)
    errors = validate_overlay_registry(load_json(overlay_path), stage_registry, validators, check_repo_integration=(overlay_path == OVERLAY_REGISTRY))
    if overlay_path == OVERLAY_REGISTRY:
        errors.extend(run_fixture_matrix(stage_registry, validators))
    if errors:
        print("INVALID runtime/stage_overlay_registry.json", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PPG_STAGE_OVERLAYS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
