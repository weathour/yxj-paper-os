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
    "schema_version", "stage_id", "stage_name", "purpose", "execution_mode", "recommended_agent_type", "subagent_lane_policy", "requires_worker_task_packet", "consumes", "produces", "validators", "backflow_targets", "completion_gate", "activation_policy", "coverage_status", "registry_ref", "worker_authority_boundary", "worker_packet_coverage"
}
REQUIRED_FIELDS.add("stage_local_overlays")
EXECUTION_MODES = {"owner_gated", "script_generated", "agent_generated", "hybrid_generated"}
WORKER_COVERAGE = {"linked_strict_packet", "planned_with_blocker", "not_required"}
LANE_POLICIES = {"mandatory_double", "conditional_double", "single_with_deterministic_validation"}
MANDATORY_DOUBLE_STAGES = {"S02", "S03", "S04", "S05", "S10", "S12", "S13", "S15"}
CONDITIONAL_DOUBLE_STAGES = {"S00", "S01", "S06", "S07", "S08", "S11", "S14", "S16"}
SINGLE_WITH_VALIDATION_STAGES = {"S09A", "S09B", "G01", "G02"}
NEGATIVE_EXPECTATIONS = {
    "invalid-missing-completion-gate.json": "E_STAGE_CONTRACT_FIELD_MISSING",
    "invalid-execution-mode.json": "E_STAGE_CONTRACT_MODE",
    "invalid-owner-worker-packet.json": "E_STAGE_CONTRACT_FAKE_WORKER_PACKET",
    "invalid-missing-validators.json": "E_STAGE_CONTRACT_LIST_FIELD",
    "invalid-wrong-stage-packet.json": "E_STAGE_CONTRACT_PACKET_STAGE_BINDING",
    "invalid-missing-worker-packet.json": "E_STAGE_CONTRACT_WORKER_PACKET_MISSING",
    "invalid-absolute-worker-packet.json": "E_STAGE_CONTRACT_PACKET_REF_SCOPE",
    "invalid-traversal-worker-packet.json": "E_STAGE_CONTRACT_PACKET_REF_SCOPE",
    "invalid-return-contract-ref.json": "E_STAGE_CONTRACT_RETURN_CONTRACT_REF_SCOPE",
    "invalid-missing-stage-local-overlays.json": "E_STAGE_CONTRACT_FIELD_MISSING",
    "invalid-lane-policy.json": "E_STAGE_CONTRACT_LANE_POLICY",
}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


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
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != ROOT.parent):
        return None, [issue(code, f"{sid} {ref}")]
    return path, []


def validate_lane_policy(stage_id: Any, recommended_agent_type: Any, policy: Any) -> list[str]:
    sid = str(stage_id)
    errors: list[str] = []
    if not isinstance(policy, dict):
        return [issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid}.subagent_lane_policy must be object")]

    missing = sorted({
        "policy",
        "default_lane_count",
        "producer_agent_type",
        "verifier_agent_type",
        "escalate_to_double_when",
        "rationale",
    } - set(policy))
    if missing:
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid}.subagent_lane_policy missing {missing}"))

    lane_policy = policy.get("policy")
    if lane_policy not in LANE_POLICIES:
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid} invalid lane policy {lane_policy!r}"))
    if policy.get("default_lane_count") not in {1, 2}:
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid} invalid default_lane_count"))
    if policy.get("producer_agent_type") != recommended_agent_type:
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid} producer_agent_type must match recommended_agent_type"))
    verifier = policy.get("verifier_agent_type")
    if verifier is not None and (not isinstance(verifier, str) or not verifier.strip()):
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid} verifier_agent_type must be non-empty string or null"))
    triggers = policy.get("escalate_to_double_when")
    if not isinstance(triggers, list) or not triggers or not all(isinstance(item, str) and item.strip() for item in triggers):
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid} escalate_to_double_when must be non-empty string list"))
    if not isinstance(policy.get("rationale"), str) or not policy["rationale"].strip():
        errors.append(issue("E_STAGE_CONTRACT_LANE_POLICY", f"{sid} rationale is required"))

    if sid in MANDATORY_DOUBLE_STAGES:
        expected = ("mandatory_double", 2, "verifier")
    elif sid in CONDITIONAL_DOUBLE_STAGES:
        expected = ("conditional_double", 1, "verifier")
    elif sid in SINGLE_WITH_VALIDATION_STAGES:
        expected = ("single_with_deterministic_validation", 1, None)
    else:
        return errors

    expected_policy, expected_lanes, expected_verifier = expected
    if lane_policy != expected_policy or policy.get("default_lane_count") != expected_lanes or verifier != expected_verifier:
        errors.append(issue(
            "E_STAGE_CONTRACT_LANE_POLICY",
            f"{sid} expected policy={expected_policy} default_lane_count={expected_lanes} verifier_agent_type={expected_verifier!r}",
        ))
    return errors


def validate_contract(contract: dict[str, Any], registry_stage: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    sid = contract.get("stage_id", "<missing>")
    missing = sorted(REQUIRED_FIELDS - set(contract))
    if missing:
        errors.append(issue("E_STAGE_CONTRACT_FIELD_MISSING", f"{sid} missing {missing}"))
    if contract.get("schema_version") != "ppg-stage-contract/v0.1":
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA", f"{sid} bad schema_version"))
    if registry_stage is not None:
        for key in ["stage_id", "stage_name", "execution_mode", "requires_worker_task_packet", "completion_gate", "activation_policy", "coverage_status", "subagent_lane_policy"]:
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
    errors.extend(validate_lane_policy(contract.get("stage_id"), contract.get("recommended_agent_type"), contract.get("subagent_lane_policy")))
    overlays = contract.get("stage_local_overlays")
    if not isinstance(overlays, list) or not overlays:
        errors.append(issue("E_STAGE_CONTRACT_STAGE_OVERLAY_LINK", f"{sid}.stage_local_overlays"))
    else:
        expected_validator = f"stage_overlay:nature_expert_writing:{sid}"
        if not any(
            isinstance(item, dict)
            and item.get("overlay_id") == "nature_expert_writing"
            and item.get("registry_ref") == "runtime/stage_overlay_registry.json"
            and item.get("packet_clause_validator") == expected_validator
            for item in overlays
        ):
            errors.append(issue("E_STAGE_CONTRACT_STAGE_OVERLAY_LINK", f"{sid} missing nature_expert_writing overlay link"))
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
            packet_path, scope_errors = scoped_repo_path(packet_ref, "examples/packets", "E_STAGE_CONTRACT_PACKET_REF_SCOPE", str(sid))
            errors.extend(scope_errors)
            return_contract_path, return_scope_errors = scoped_repo_path(coverage.get("return_contract_ref"), "schemas", "E_STAGE_CONTRACT_RETURN_CONTRACT_REF_SCOPE", str(sid))
            errors.extend(return_scope_errors)
            if return_contract_path and return_contract_path.name != "ppg-candidate-return.schema.json":
                errors.append(issue("E_STAGE_CONTRACT_RETURN_CONTRACT_REF_SCOPE", f"{sid} {coverage.get('return_contract_ref')}"))
            if packet_path is None or not packet_path.is_file():
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
    packet_ref_schema = str(coverage.get("properties", {}).get("packet_ref", {}))
    return_ref_schema = str(coverage.get("properties", {}).get("return_contract_ref", {}))
    if "examples/packets" not in packet_ref_schema:
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_WORKER_PACKET_REF", "packet_ref must be scoped to examples/packets"))
    if "schemas/ppg-candidate-return" not in return_ref_schema:
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_RETURN_CONTRACT_REF", "return_contract_ref must be scoped to candidate return schema"))
    lane_policy = schema.get("properties", {}).get("subagent_lane_policy", {})
    lane_required = set(lane_policy.get("required", []))
    expected_lane_required = {"policy", "default_lane_count", "producer_agent_type", "verifier_agent_type", "escalate_to_double_when", "rationale"}
    if not expected_lane_required.issubset(lane_required):
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_LANE_POLICY", "schema must require subagent lane policy fields"))
    lane_statuses = set(lane_policy.get("properties", {}).get("policy", {}).get("enum", []))
    if lane_statuses != LANE_POLICIES:
        errors.append(issue("E_STAGE_CONTRACT_SCHEMA_LANE_POLICY_ENUM", f"{sorted(lane_statuses)}"))
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
