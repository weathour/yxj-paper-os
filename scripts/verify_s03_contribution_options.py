#!/usr/bin/env python3
"""Verify S03 contribution option classifier contract and fixtures."""
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
S03_PACKET = ROOT / "examples" / "packets" / "phase10_s03_novelty_analysis_packet.v1.yaml"
S03_MATERIAL = ROOT / "examples" / "materials" / "phase10_s03_contribution_options.yaml"
PUBLIC_CONSUMES = ["research dossier", "evidence inventory", "motivation", "SOTA map"]
PUBLIC_PRODUCES = ["contribution options", "novelty readiness", "risk list"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S03_contribution_option_queue",
    "S03_option_coverage_ledger",
    "S03_sota_contrast_matrix",
    "S03_evidence_readiness_classifier",
    "S03_rejected_option_register",
    "S03_owner_gated_option_register",
    "S03_reviewer_attack_map",
    "S03_s04_handoff_coverage",
    "S03_no_claim_admissibility_or_final_wording",
    "S03_no_completion_overclaim",
}
REQUIRED_PACKET_PASSES = {
    "input_boundary_inventory",
    "candidate_contribution_generation",
    "sota_contrast_pass",
    "evidence_readiness_classification",
    "reviewer_attack_coherence_pass",
    "rejection_owner_gate_pass",
    "s04_handoff_pass",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "contribution_option_queue",
    "contribution_type_taxonomy",
    "sota_contrast_matrix",
    "evidence_readiness_score",
    "unsupported_claim_register",
    "rejected_option_register",
    "owner_gated_option_register",
    "owner_gated_semantic_shift_log",
    "reviewer_attack_map",
    "contribution_coherence",
    "option_coverage_ledger",
    "sota_contrast_coverage",
    "s04_handoff",
    "s04_handoff_coverage",
    "anti_rhetoric_guard",
    "unresolved_backflow_register",
    "candidate_return",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s03_contribution_option_queue",
    "s03_sota_contrast_matrix",
    "s03_evidence_readiness_score",
    "s03_rejected_and_owner_gated_registers",
    "s03_reviewer_attack_and_coherence",
    "s03_s04_handoff_coverage",
    "s03_anti_rhetoric_guard",
    "s03_nature_overlay",
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
    "s03_contribution_option_queue",
    "s03_option_coverage_ledger",
    "s03_sota_contrast_matrix",
    "s03_evidence_readiness_score",
    "s03_rejected_option_register",
    "s03_owner_gated_option_register",
    "s03_reviewer_attack_map",
    "s03_s04_handoff_coverage",
    "s03_anti_rhetoric_guard",
    "s03_no_claim_admissibility_or_final_wording",
    "no_completion_overclaim",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-option-queue.yaml": "E_S03_OPTION_CLASSIFICATION_REQUIRED",
    ROOT / "examples/materials/invalid-s03-contribution-options-invalid-status.yaml": "E_S03_STATUS_INVALID",
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-sota-contrast.yaml": "E_S03_SOTA_CONTRAST_REQUIRED",
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-rejected-register.yaml": "E_S03_REJECTED_OPTION_REGISTER_REQUIRED",
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-owner-gated-register.yaml": "E_S03_OWNER_GATED_REGISTER_REQUIRED",
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-s04-handoff.yaml": "E_S03_S04_HANDOFF_REQUIRED",
    ROOT / "examples/materials/invalid-s03-contribution-options-claim-admissibility.yaml": "E_S03_NO_CLAIM_ADMISSIBILITY",
    ROOT / "examples/materials/invalid-s03-contribution-options-completion-overclaim.yaml": "E_S03_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-coverage-ledger.yaml": "E_S03_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s03-contribution-options-missing-anti-rhetoric-guard.yaml": "E_S03_ANTI_RHETORIC_GUARD",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S03_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S03_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S03_YAML_LOAD", f"{path}: root must be a mapping")
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
    result = _run(VALIDATE_MATERIAL, S03_MATERIAL)
    if result.returncode != 0:
        _fail("E_S03_POSITIVE_FIXTURE", f"{S03_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S03_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S03_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S03_SCHEMA", "schema properties mapping missing")
    spec = props.get("S03ContributionOptions")
    if not isinstance(spec, dict):
        _fail("E_S03_SCHEMA", "S03ContributionOptions schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S03_SCHEMA", "S03ContributionOptions properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s03-contribution-options/v0.1":
        _fail("E_S03_SCHEMA", "S03ContributionOptions.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S03":
        _fail("E_S03_SCHEMA", "S03ContributionOptions.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = (REQUIRED_OUTPUT_MODULES | {"schema_version", "stage_id"}) - required
    if missing:
        _fail("E_S03_SCHEMA", f"S03ContributionOptions schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s03 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S03"), None)
    if not isinstance(s03, dict):
        _fail("E_S03_REGISTRY", "S03 missing from stage registry")
    if s03.get("requires_worker_task_packet") is not True:
        _fail("E_S03_REGISTRY", "S03 must keep requires_worker_task_packet=true")
    if s03.get("consumes") != PUBLIC_CONSUMES or s03.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S03_REGISTRY", "S03 public graph I/O changed")
    if s03.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S03_REGISTRY", "S03 must keep mandatory_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s03.get("validators", []))
    if missing:
        _fail("E_S03_REGISTRY", f"S03 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S03.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S03_CONTRACT", "S03 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S03_CONTRACT", "S03 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S03_CONTRACT", "S03 contract must keep mandatory_double lane policy")
    if set(contract.get("validators", [])) != set(s03.get("validators", [])):
        _fail("E_S03_CONTRACT", "S03 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S03_CONTRACT", "S03 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml":
        _fail("E_S03_CONTRACT", "S03 packet_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S03_CONTRACT", "S03 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S03_PACKET)
    if result.returncode != 0:
        _fail("E_S03_PACKET", f"S03 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S03_PACKET)
    if packet.get("target_material") != "phase10_s03_contribution_options":
        _fail("E_S03_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s03_contribution_options.yaml":
        _fail("E_S03_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s03_contribution_options.yaml"]:
        _fail("E_S03_PACKET", "allowed_write_paths must be exactly the S03 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S03ContributionOptions" or packet.get("expected_payload_schema") != "ppg-s03-contribution-options/v0.1":
        _fail("E_S03_PACKET", "expected schema/material binding mismatch")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S03_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "no_silent_omission", "no_final_prose"):
        if protocol.get(key) is not True:
            _fail("E_S03_PACKET", f"internal_execution_protocol.{key} must be true")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S03_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S03_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S03ContributionOptions" or output_contract.get("payload_schema") != "ppg-s03-contribution-options/v0.1":
        _fail("E_S03_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S03_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    validators = set(packet.get("validators", [])) if isinstance(packet.get("validators"), list) else set()
    if not {"validate_material:S03ContributionOptions", "s04_handoff_required:S03"} <= validators:
        _fail("E_S03_PACKET", "S03 material/S04 handoff validators missing")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s03 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S03"), None)
    if not isinstance(s03, dict):
        _fail("E_S03_PHASE10", "S03 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s03.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S03_PHASE10", f"S03 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s03.get("required_checks", []))
    if missing_checks:
        _fail("E_S03_PHASE10", f"S03 phase10 checks missing {sorted(missing_checks)}")


def main() -> int:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S03_CONTRIBUTION_OPTIONS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
