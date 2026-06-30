#!/usr/bin/env python3
"""Verify Phase9 StageContract fixtures against the canonical registry."""
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
CONTRACT_DIR = ROOT / "examples" / "stage-contracts"
SCHEMA = ROOT / "schemas" / "ppg-stage-contract.schema.json"
REQUIRED_FIELDS = {
    "schema_version", "stage_id", "stage_name", "purpose", "execution_mode", "recommended_agent_type", "requires_worker_task_packet", "consumes", "produces", "validators", "backflow_targets", "completion_gate", "activation_policy", "coverage_status", "registry_ref", "worker_authority_boundary", "worker_packet_coverage"
}
EXECUTION_MODES = {"owner_gated", "script_generated", "agent_generated", "hybrid_generated"}
WORKER_COVERAGE = {"linked_strict_packet", "planned_with_blocker", "not_required"}
NEGATIVE_EXPECTATIONS = {
    "invalid-missing-completion-gate.json": "E_STAGE_CONTRACT_FIELD_MISSING",
    "invalid-execution-mode.json": "E_STAGE_CONTRACT_MODE",
    "invalid-owner-worker-packet.json": "E_STAGE_CONTRACT_FAKE_WORKER_PACKET",
    "invalid-missing-validators.json": "E_STAGE_CONTRACT_LIST_FIELD",
    "invalid-wrong-stage-packet.json": "E_STAGE_CONTRACT_PACKET_STAGE_BINDING",
}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(contract: dict[str, Any], registry_stage: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    sid = contract.get("stage_id", "<missing>")
    missing = sorted(REQUIRED_FIELDS - set(contract))
    if missing:
        errors.append(issue("E_STAGE_CONTRACT_FIELD_MISSING", f"{sid} missing {missing}"))
    if contract.get("schema_version") != "ppg-stage-contract/v0.1":
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA", f"{sid} bad schema_version"))
    if registry_stage is not None:
        for key in ["stage_id", "stage_name", "execution_mode", "requires_worker_task_packet", "completion_gate", "activation_policy", "coverage_status"]:
            if contract.get(key) != registry_stage.get(key):
                errors.append(issue("E_STAGE_CONTRACT_REGISTRY_MISMATCH", f"{sid}.{key}"))
    if contract.get("execution_mode") not in EXECUTION_MODES:
        errors.append(issue("E_STAGE_CONTRACT_MODE", f"{sid} invalid execution_mode"))
    for key in ["stage_name", "purpose", "recommended_agent_type", "completion_gate", "activation_policy", "coverage_status"]:
        if not isinstance(contract.get(key), str) or not contract[key].strip():
            errors.append(issue("E_STAGE_CONTRACT_EMPTY_FIELD", f"{sid}.{key}"))
    for key in ["consumes", "produces", "validators"]:
        value = contract.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(issue("E_STAGE_CONTRACT_LIST_FIELD", f"{sid}.{key}"))
    boundary = contract.get("worker_authority_boundary")
    if not isinstance(boundary, dict) or boundary.get("completion_forbidden") is not True or boundary.get("no_recursive_orchestration") is not True or boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_STAGE_CONTRACT_AUTHORITY_BOUNDARY", f"{sid} worker boundary must forbid completion and recursive orchestration"))
    coverage = contract.get("worker_packet_coverage")
    if not isinstance(coverage, dict) or coverage.get("status") not in WORKER_COVERAGE:
        errors.append(issue("E_STAGE_CONTRACT_WORKER_COVERAGE", f"{sid} invalid worker_packet_coverage"))
    else:
        mode = contract.get("execution_mode")
        requires = contract.get("requires_worker_task_packet")
        status = coverage.get("status")
        if mode in {"owner_gated", "script_generated"} and (requires is True or status != "not_required"):
            errors.append(issue("E_STAGE_CONTRACT_FAKE_WORKER_PACKET", f"{sid} non-worker stage cannot require/link worker packet"))
        if requires is True and status == "not_required":
            errors.append(issue("E_STAGE_CONTRACT_WORKER_PACKET_MISSING", f"{sid} requires worker coverage"))
        if status == "linked_strict_packet":
            packet_ref = coverage.get("packet_ref")
            packet_path = ROOT / str(packet_ref) if isinstance(packet_ref, str) else None
            if not isinstance(packet_ref, str) or packet_path is None or not packet_path.is_file():
                errors.append(issue("E_STAGE_CONTRACT_LINKED_PACKET_MISSING", f"{sid} {packet_ref}"))
            elif registry_stage is not None:
                packet_data, packet_load_errors = load_document(packet_path)
                if packet_load_errors:
                    errors.append(issue("E_STAGE_CONTRACT_PACKET_PARSE", f"{sid} {packet_ref}: {packet_load_errors[0].message}"))
                elif not isinstance(packet_data, dict):
                    errors.append(issue("E_STAGE_CONTRACT_PACKET_PARSE", f"{sid} {packet_ref}: packet must be a mapping"))
                else:
                    packet_errors = validate_packet(packet_data)
                    if packet_errors:
                        errors.append(issue("E_STAGE_CONTRACT_PACKET_INVALID", f"{sid} {packet_ref}: {packet_errors[0].code}"))
                    expected_contract_ref = f"examples/stage-contracts/{sid}.stage-contract.json"
                    if packet_data.get("stage_id") != sid or packet_data.get("stage_contract_ref") != expected_contract_ref:
                        errors.append(issue("E_STAGE_CONTRACT_PACKET_STAGE_BINDING", f"{sid} linked packet stage_id={packet_data.get('stage_id')} stage_contract_ref={packet_data.get('stage_contract_ref')}"))
        if status == "planned_with_blocker" and not coverage.get("blocker"):
            errors.append(issue("E_STAGE_CONTRACT_BLOCKER_MISSING", f"{sid} planned worker packet needs blocker rationale"))
    return errors


def validate_schema_contract(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = set(schema.get("required", []))
    missing = sorted(REQUIRED_FIELDS - required)
    if missing:
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_REQUIRED", f"schema missing required fields {missing}"))
    stage_id = schema.get("properties", {}).get("stage_id", {})
    if "09A" not in str(stage_id.get("pattern", "")) or "09B" not in str(stage_id.get("pattern", "")) or "S09)" in str(stage_id.get("pattern", "")):
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_STAGE_ID", "schema must encode canonical S09A/S09B and reject bare S09"))
    boundary = schema.get("properties", {}).get("worker_authority_boundary", {})
    boundary_required = set(boundary.get("required", []))
    expected_boundary = {"completion_forbidden", "no_recursive_orchestration", "controller_owned_completion"}
    if not expected_boundary.issubset(boundary_required):
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_BOUNDARY", "schema must require worker authority boundary fields"))
    coverage = schema.get("properties", {}).get("worker_packet_coverage", {})
    coverage_required = set(coverage.get("required", []))
    expected_coverage = {"status", "packet_ref", "return_contract_ref", "blocker"}
    if not expected_coverage.issubset(coverage_required):
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_WORKER_COVERAGE", "schema must require worker packet coverage fields"))
    coverage_statuses = set(coverage.get("properties", {}).get("status", {}).get("enum", []))
    if coverage_statuses != WORKER_COVERAGE:
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_WORKER_COVERAGE_ENUM", f"{sorted(coverage_statuses)}"))
    return errors


def main() -> int:
    registry = load_json(REGISTRY)
    errors: list[str] = []
    errors.extend(validate_schema_contract(load_json(SCHEMA)))
    stages = registry.get("stages", [])
    by_id = {stage["stage_id"]: stage for stage in stages}
    for sid, stage in by_id.items():
        path = CONTRACT_DIR / f"{sid}.stage-contract.json"
        if not path.is_file():
            errors.append(issue("E_STAGE_CONTRACT_MISSING", str(path.relative_to(ROOT))))
            continue
        errors.extend(validate_contract(load_json(path), stage))
    actual = sorted(p.name.removesuffix(".stage-contract.json") for p in CONTRACT_DIR.glob("*.stage-contract.json"))
    expected = sorted(by_id)
    if actual != expected:
        errors.append(issue("E_STAGE_CONTRACT_SET", f"expected {expected}, got {actual}"))
    for filename, expected_code in NEGATIVE_EXPECTATIONS.items():
        path = CONTRACT_DIR / filename
        if not path.is_file():
            errors.append(issue("E_STAGE_CONTRACT_NEGATIVE_MISSING", filename))
            continue
        negative_errors = validate_contract(load_json(path), by_id.get(load_json(path).get("stage_id", "")))
        if not any(expected_code in error for error in negative_errors):
            errors.append(issue("E_STAGE_CONTRACT_NEGATIVE_CASE", f"{filename} did not trigger {expected_code}: {negative_errors}"))
    if errors:
        print("INVALID examples/stage-contracts", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE9_STAGE_CONTRACTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
