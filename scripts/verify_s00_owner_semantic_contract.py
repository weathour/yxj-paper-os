#!/usr/bin/env python3
"""Verify S00 owner-intake / owner-semantic-contract hard gates."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import load_document
    from validate_material import validate as validate_material
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402
    from validate_material import validate as validate_material  # type: ignore  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]

POSITIVE_MATERIALS = [
    "examples/materials/s00_owner_intake.v1.yaml",
    "examples/materials/s00_owner_semantic_contract.v1.yaml",
]

NEGATIVE_MATERIALS = {
    "examples/materials/invalid-s00-owner-intake-missing-original-request.yaml": "E_S00_OWNER_INTAKE_REQUIRED",
    "examples/materials/invalid-s00-owner-contract-submission-allowed.yaml": "E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY",
    "examples/materials/invalid-s00-owner-contract-missing-blocked-routes.yaml": "E_S00_OWNER_BLOCKED_ROUTES_REQUIRED",
}

REQUIRED_STAGE_VALIDATORS = {
    "owner confirmation",
    "blocked route check",
    "owner decision trace",
    "claim scope boundary",
    "source/privacy policy boundary",
    "external action boundary",
    "no worker semantic change",
    "downstream stale/backflow effects",
    "no completion or submission overclaim",
}

REQUIRED_PHASE10_CHECKS = {
    "source_or_material_trace",
    "completion_boundary_explicit",
    "controller_owned_status",
    "stage_overlay_binding",
    "controller_route_only",
    "owner_decision_trace",
    "claim_scope_boundary",
    "source_privacy_policy_boundary",
    "external_action_boundary",
    "blocked_route_register",
    "no_worker_semantic_change",
    "downstream_stale_policy",
    "no_completion_overclaim",
}

REQUIRED_STALE_TARGETS = {"S01", "S02", "S03", "S04", "S05", "S13", "S16"}
REQUIRED_OWNER_APPROVAL_ACTIONS = {
    "submission",
    "venue_route_change",
    "claim_strength_increase",
    "private_source_use",
    "public_release",
}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate_material_fixture(rel: str) -> list[str]:
    data, load_errors = load_document(ROOT / rel)
    if load_errors:
        return [issue("E_S00_FIXTURE_PARSE", f"{rel}: {load_errors[0].message}")]
    return [issue(error.code, f"{rel}: {error.message}") for error in validate_material(data)]


def find_stage(registry: dict[str, Any], stage_id: str) -> dict[str, Any] | None:
    for stage in registry.get("stages", []):
        if isinstance(stage, dict) and stage.get("stage_id") == stage_id:
            return stage
    return None


def find_validator(validators: dict[str, Any], stage_id: str) -> dict[str, Any] | None:
    for validator in validators.get("validators", []):
        if isinstance(validator, dict) and validator.get("stage_id") == stage_id:
            return validator
    return None


def verify_positive_and_negative_fixtures() -> list[str]:
    errors: list[str] = []
    for rel in POSITIVE_MATERIALS:
        fixture_errors = validate_material_fixture(rel)
        if fixture_errors:
            errors.extend(fixture_errors)
    for rel, expected_code in NEGATIVE_MATERIALS.items():
        fixture_errors = validate_material_fixture(rel)
        if not any(error.startswith(expected_code + ":") for error in fixture_errors):
            errors.append(issue("E_S00_NEGATIVE_FIXTURE", f"{rel} did not fail with {expected_code}: {fixture_errors}"))
    return errors


def verify_semantic_contract_fixture() -> list[str]:
    errors: list[str] = []
    data, load_errors = load_document(ROOT / "examples/materials/s00_owner_semantic_contract.v1.yaml")
    if load_errors or not isinstance(data, dict):
        return [issue("E_S00_FIXTURE_PARSE", "valid semantic contract fixture is not a mapping")]
    payload = data.get("payload")
    if not isinstance(payload, dict):
        return [issue("E_S00_FIXTURE_PARSE", "valid semantic contract payload is not a mapping")]
    external = payload.get("external_action_boundary")
    if not isinstance(external, dict):
        errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", "external_action_boundary missing"))
    else:
        if external.get("submission_allowed") is not False or external.get("public_release_allowed") is not False:
            errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", "submission/public release must be false"))
        actions = set(external.get("owner_approval_required_for", [])) if isinstance(external.get("owner_approval_required_for"), list) else set()
        missing_actions = sorted(REQUIRED_OWNER_APPROVAL_ACTIONS - actions)
        if missing_actions:
            errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", f"missing owner approval actions {missing_actions}"))
    downstream = payload.get("downstream_effects_if_changed")
    stale_targets = set(downstream.get("stages_to_mark_stale", [])) if isinstance(downstream, dict) and isinstance(downstream.get("stages_to_mark_stale"), list) else set()
    missing_stale = sorted(REQUIRED_STALE_TARGETS - stale_targets)
    if missing_stale:
        errors.append(issue("E_S00_OWNER_STALE_TARGETS_REQUIRED", f"missing stale targets {missing_stale}"))
    return errors


def verify_stage_and_validator_contracts() -> list[str]:
    errors: list[str] = []
    registry = load_json("runtime/stage_registry.json")
    stage = find_stage(registry, "S00")
    contract = load_json("examples/stage-contracts/S00.stage-contract.json")
    if not isinstance(stage, dict):
        return [issue("E_S00_STAGE_REGISTRY", "S00 missing from runtime/stage_registry.json")]
    for source_name, source in [("registry", stage), ("stage_contract", contract)]:
        if source.get("execution_mode") != "owner_gated":
            errors.append(issue("E_S00_OWNER_GATE", f"{source_name}.execution_mode must remain owner_gated"))
        if source.get("requires_worker_task_packet") is not False:
            errors.append(issue("E_S00_NO_WORKER_PACKET", f"{source_name}.requires_worker_task_packet must remain false"))
        validators = set(source.get("validators", [])) if isinstance(source.get("validators"), list) else set()
        missing = sorted(REQUIRED_STAGE_VALIDATORS - validators)
        if missing:
            errors.append(issue("E_S00_STAGE_VALIDATORS", f"{source_name} missing validators {missing}"))
    coverage = contract.get("worker_packet_coverage")
    if not isinstance(coverage, dict) or coverage.get("status") != "not_required" or coverage.get("packet_ref") is not None:
        errors.append(issue("E_S00_NO_WORKER_PACKET", "S00 worker_packet_coverage must remain not_required with null packet_ref"))

    validators_doc = load_json("runtime/phase10_content_validators.json")
    content_validator = find_validator(validators_doc, "S00")
    if not isinstance(content_validator, dict):
        errors.append(issue("E_S00_PHASE10_VALIDATOR", "S00 content validator missing"))
    else:
        checks = set(content_validator.get("required_checks", [])) if isinstance(content_validator.get("required_checks"), list) else set()
        missing_checks = sorted(REQUIRED_PHASE10_CHECKS - checks)
        if missing_checks:
            errors.append(issue("E_S00_PHASE10_VALIDATOR", f"missing required checks {missing_checks}"))
        dimensions = content_validator.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) < 8:
            errors.append(issue("E_S00_PHASE10_VALIDATOR", "S00 validator needs detailed dimensions"))
    return errors


def verify_payload_schema_vocab() -> list[str]:
    payloads = load_json("schemas/ppg-material-payloads.schema.json")
    props = payloads.get("properties") if isinstance(payloads, dict) else None
    if not isinstance(props, dict):
        return [issue("E_S00_PAYLOAD_SCHEMA", "payload schema properties missing")]
    errors: list[str] = []
    for name in ["OwnerIntake", "OwnerSemanticContract"]:
        schema = props.get(name)
        if not isinstance(schema, dict):
            errors.append(issue("E_S00_PAYLOAD_SCHEMA", f"{name} missing from ppg-material-payloads schema"))
            continue
        required = set(schema.get("required", [])) if isinstance(schema.get("required"), list) else set()
        if {"schema_version", "stage_id"} - required:
            errors.append(issue("E_S00_PAYLOAD_SCHEMA", f"{name} must require schema_version and stage_id"))
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(verify_positive_and_negative_fixtures())
    errors.extend(verify_semantic_contract_fixture())
    errors.extend(verify_stage_and_validator_contracts())
    errors.extend(verify_payload_schema_vocab())
    if errors:
        print("INVALID S00 owner semantic contract", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PPG_S00_OWNER_SEMANTIC_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
