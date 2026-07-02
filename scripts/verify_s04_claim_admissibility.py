#!/usr/bin/env python3
"""Verify S04 claim admissibility contract and fixtures."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, NoReturn

try:
    from ppg_validate_common import load_document
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_MATERIAL = ROOT / "scripts" / "validate_material.py"
VALIDATE_PACKET = ROOT / "scripts" / "validate_packet.py"
S04_PACKET = ROOT / "examples" / "packets" / "phase10_s04_evidence_claim_admissibility_packet.v1.yaml"
S04_MATERIAL = ROOT / "examples" / "materials" / "phase10_s04_claim_admissibility.yaml"
PUBLIC_CONSUMES = ["evidence bank", "citation bank", "result artifacts", "contribution options"]
PUBLIC_PRODUCES = ["claim citation capsules", "result packages", "claim evidence visibility", "data availability plan"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S04_claim_queue",
    "S04_atomic_claim_register",
    "S04_claim_capsules",
    "S04_claim_coverage_ledger",
    "S04_support_strength_map",
    "S04_evidence_anchor_visibility",
    "S04_allowed_forbidden_wording",
    "S04_result_package_boundary",
    "S04_claim_transformation_log",
    "S04_downstream_handoff_coverage",
    "S04_no_final_prose_or_completion_overclaim",
}
REQUIRED_PACKET_PASSES = {
    "claim_bearing_unit_extraction",
    "atomic_claim_decomposition",
    "evidence_anchor_lookup",
    "support_strength_classification",
    "wording_boundary_derivation",
    "result_package_boundary_pass",
    "downstream_handoff_backflow_pass",
    "independent_verifier_pass",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "claim_queue",
    "claim_unit_decomposition",
    "atomic_claim_register",
    "claim_capsules",
    "support_strength_map",
    "evidence_anchor_map",
    "allowed_wording_map",
    "forbidden_wording_map",
    "result_package_boundary_matrix",
    "claim_transformation_log",
    "data_availability_plan",
    "downstream_handoffs",
    "claim_coverage_ledger",
    "unsupported_claim_backflow_register",
    "evidence_locator_coverage",
    "downstream_use_permission_matrix",
    "unresolved_backflow_register",
    "candidate_return",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s04_claim_queue",
    "s04_atomic_claim_register",
    "s04_claim_capsules",
    "s04_claim_coverage_ledger",
    "s04_support_strength_map",
    "s04_evidence_anchor_visibility",
    "s04_allowed_forbidden_wording",
    "s04_result_package_boundary",
    "s04_transformation_backflow",
    "s04_downstream_handoff_coverage",
    "s04_nature_overlay",
}
REQUIRED_PHASE10_CHECKS = {
    "source_or_material_trace",
    "completion_boundary_explicit",
    "controller_owned_status",
    "candidate_return_or_missing_material_path",
    "worker_authority_boundary",
    "stage_overlay_binding",
    "controller_route_only",
    "stage_overlay_packet_clause",
    "s04_claim_queue",
    "s04_atomic_claim_register",
    "s04_claim_capsules",
    "s04_claim_coverage_ledger",
    "s04_support_strength_map",
    "s04_evidence_anchor_visibility",
    "s04_allowed_forbidden_wording",
    "s04_result_package_boundary",
    "s04_claim_transformation_log",
    "s04_downstream_handoff_coverage",
    "s04_no_final_prose_or_completion_overclaim",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-claim-queue.yaml": "E_S04_CLAIM_QUEUE_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-evidence-anchor.yaml": "E_S04_EVIDENCE_ANCHOR_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-unsupported-admitted.yaml": "E_S04_UNSUPPORTED_ADMITTED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-allowed-wording.yaml": "E_S04_ALLOWED_WORDING_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-forbidden-wording.yaml": "E_S04_FORBIDDEN_WORDING_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-result-boundary.yaml": "E_S04_RESULT_BOUNDARY_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-transformation-log.yaml": "E_S04_TRANSFORMATION_LOG_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-downstream-handoff.yaml": "E_S04_DOWNSTREAM_HANDOFF_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-completion-overclaim.yaml": "E_S04_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-coverage-ledger.yaml": "E_S04_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-final-prose.yaml": "E_S04_NO_FINAL_PROSE",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-invalid-support-strength.yaml": "E_S04_SUPPORT_STRENGTH_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-downstream-permission.yaml": "E_S04_DOWNSTREAM_PERMISSION_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-unresolved-backflow.yaml": "E_S04_UNRESOLVED_BACKFLOW_REQUIRED",
    ROOT / "examples/materials/invalid-s04-claim-admissibility-missing-data-availability.yaml": "E_S04_DATA_AVAILABILITY_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S04_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S04_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S04_YAML_LOAD", f"{path}: root must be a mapping")
    return data


def _run(script: Path, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _verify_fixtures() -> None:
    result = _run(VALIDATE_MATERIAL, S04_MATERIAL)
    if result.returncode != 0:
        _fail("E_S04_POSITIVE_FIXTURE", f"{S04_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S04_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S04_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S04_SCHEMA", "schema properties mapping missing")
    spec = props.get("S04ClaimAdmissibility")
    if not isinstance(spec, dict):
        _fail("E_S04_SCHEMA", "S04ClaimAdmissibility schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S04_SCHEMA", "S04ClaimAdmissibility properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s04-claim-admissibility/v0.1":
        _fail("E_S04_SCHEMA", "S04ClaimAdmissibility.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S04":
        _fail("E_S04_SCHEMA", "S04ClaimAdmissibility.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = (REQUIRED_OUTPUT_MODULES | {"schema_version", "stage_id"}) - required
    if missing:
        _fail("E_S04_SCHEMA", f"S04ClaimAdmissibility schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s04 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S04"), None)
    if not isinstance(s04, dict):
        _fail("E_S04_REGISTRY", "S04 missing from stage registry")
    if s04.get("requires_worker_task_packet") is not True:
        _fail("E_S04_REGISTRY", "S04 must keep requires_worker_task_packet=true")
    if s04.get("consumes") != PUBLIC_CONSUMES or s04.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S04_REGISTRY", "S04 public graph I/O changed")
    if s04.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S04_REGISTRY", "S04 must keep mandatory_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s04.get("validators", []))
    if missing:
        _fail("E_S04_REGISTRY", f"S04 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S04.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S04_CONTRACT", "S04 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S04_CONTRACT", "S04 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S04_CONTRACT", "S04 contract must keep mandatory_double lane policy")
    if set(contract.get("validators", [])) != set(s04.get("validators", [])):
        _fail("E_S04_CONTRACT", "S04 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S04_CONTRACT", "S04 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml":
        _fail("E_S04_CONTRACT", "S04 packet_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S04_CONTRACT", "S04 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S04_PACKET)
    if result.returncode != 0:
        _fail("E_S04_PACKET", f"S04 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S04_PACKET)
    if packet.get("target_material") != "phase10_s04_claim_admissibility":
        _fail("E_S04_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s04_claim_admissibility.yaml":
        _fail("E_S04_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s04_claim_admissibility.yaml"]:
        _fail("E_S04_PACKET", "allowed_write_paths must be exactly the S04 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S04ClaimAdmissibility" or packet.get("expected_payload_schema") != "ppg-s04-claim-admissibility/v0.1":
        _fail("E_S04_PACKET", "expected schema/material binding mismatch")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S04_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "no_silent_omission", "no_final_prose"):
        if protocol.get(key) is not True:
            _fail("E_S04_PACKET", f"internal_execution_protocol.{key} must be true")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S04_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S04_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S04ClaimAdmissibility" or output_contract.get("payload_schema") != "ppg-s04-claim-admissibility/v0.1":
        _fail("E_S04_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S04_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    validators = set(packet.get("validators", [])) if isinstance(packet.get("validators"), list) else set()
    if not {"validate_material:S04ClaimAdmissibility", "claim_capsule_required:S04", "allowed_forbidden_wording_required:S04", "result_boundary_required:S04"} <= validators:
        _fail("E_S04_PACKET", "S04 material/admissibility validators missing")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s04 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S04"), None)
    if not isinstance(s04, dict):
        _fail("E_S04_PHASE10", "S04 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s04.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S04_PHASE10", f"S04 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s04.get("required_checks", []))
    if missing_checks:
        _fail("E_S04_PHASE10", f"S04 phase10 checks missing {sorted(missing_checks)}")


def main() -> None:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S04_CLAIM_ADMISSIBILITY_OK")


if __name__ == "__main__":
    main()
