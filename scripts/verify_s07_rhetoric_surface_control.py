#!/usr/bin/env python3
"""Verify S07 rhetoric/surface-control contract and fixtures."""
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
S07_PACKET = ROOT / "examples" / "packets" / "phase10_s07_rhetoric_surface_control_packet.v1.yaml"
S07_MATERIAL = ROOT / "examples" / "materials" / "phase10_s07_surface_control.yaml"
PUBLIC_CONSUMES = ["object representation", "claim visibility", "evidence wording"]
PUBLIC_PRODUCES = ["construction matrix", "rhetorical matrix", "terminology register", "surface rules"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S07_input_coverage",
    "S07_claim_surface_rule_map",
    "S07_terminology_surface_register",
    "S07_internal_id_ban_list",
    "S07_paragraph_job_map",
    "S07_rhetorical_move_matrix",
    "S07_language_flexibility_guard",
    "S07_surface_rules",
    "S07_forbidden_expression_list",
    "S07_coverage_ledger",
    "S07_unresolved_surface_control_report",
    "S07_downstream_handoff",
    "S07_no_new_claims_or_claim_strengthening",
    "S07_no_final_prose_or_completion_overclaim",
}
REQUIRED_PACKET_PASSES = {
    "input_boundary_and_coverage_check",
    "claim_surface_pass",
    "terminology_pass",
    "internal_id_leakage_pass",
    "paragraph_job_pass",
    "rhetorical_move_pass",
    "language_flexibility_guard",
    "forbidden_expression_audit",
    "coverage_and_downstream_handoff",
    "independent_verifier_pass",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "input_coverage_ledger",
    "claim_surface_rule_map",
    "terminology_surface_register",
    "internal_id_ban_list",
    "paragraph_job_map",
    "rhetorical_move_matrix",
    "flexible_language_control",
    "surface_rules",
    "forbidden_expression_list",
    "coverage_ledger",
    "unresolved_surface_control_report",
    "downstream_handoff",
    "surface_safety_audit",
    "candidate_return",
}
REQUIRED_SCHEMA_MODULES = REQUIRED_OUTPUT_MODULES | {"schema_version", "stage_id"}
REQUIRED_PHASE10_DIMENSIONS = {
    "s07_input_coverage",
    "s07_claim_surface_rule_map",
    "s07_terminology_surface_register",
    "s07_internal_id_ban_list",
    "s07_paragraph_job_map",
    "s07_rhetorical_move_matrix",
    "s07_language_flexibility_guard",
    "s07_surface_rules",
    "s07_forbidden_expression_list",
    "s07_coverage_ledger",
    "s07_unresolved_surface_control_report",
    "s07_downstream_handoff",
    "s07_surface_safety_audit",
    "s07_nature_overlay",
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
    "s07_input_coverage",
    "s07_claim_surface_rule_map",
    "s07_terminology_surface_register",
    "s07_internal_id_ban_list",
    "s07_paragraph_job_map",
    "s07_rhetorical_move_matrix",
    "s07_language_flexibility_guard",
    "s07_surface_rules",
    "s07_forbidden_expression_list",
    "s07_coverage_ledger",
    "s07_unresolved_surface_control_report",
    "s07_downstream_handoff",
    "s07_no_new_claims",
    "s07_no_claim_strengthening",
    "s07_no_final_prose",
    "s07_no_completion_overclaim",
    "s07_no_rigid_language_template",
    "s07_no_internal_id_leakage",
}
REQUIRED_PACKET_VALIDATORS = {
    "validate_material:S07RhetoricSurfaceControl",
    "input_coverage_required:S07",
    "claim_surface_rule_map_required:S07",
    "terminology_surface_register_required:S07",
    "internal_id_ban_list_required:S07",
    "paragraph_job_map_required:S07",
    "rhetorical_move_matrix_required:S07",
    "flexible_language_control_required:S07",
    "forbidden_expression_list_required:S07",
    "coverage_ledger_required:S07",
    "downstream_handoff_required:S07",
    "no_new_claims:S07",
    "no_claim_strengthening:S07",
    "no_final_prose:S07",
    "no_rigid_language_template:S07",
}
REQUIRED_INPUT_MATERIALS = {
    "phase10_s02_research_dossier",
    "phase10_s04_claim_admissibility",
    "phase10_s05_reader_spine",
    "phase10_s06_object_granularity",
    "terminology_register_v1",
}
REQUIRED_READ_PATHS = {
    "examples/materials/phase10_s02_research_dossier.yaml",
    "examples/materials/phase10_s04_claim_admissibility.yaml",
    "examples/materials/phase10_s05_reader_spine.yaml",
    "examples/materials/phase10_s06_object_granularity.yaml",
    "examples/materials/terminology_register.v1.yaml",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s07-surface-control-missing-input-coverage.yaml": "E_S07_INPUT_COVERAGE_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-claim-surface-rules.yaml": "E_S07_CLAIM_SURFACE_RULE_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-terminology.yaml": "E_S07_TERMINOLOGY_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-internal-id-ban.yaml": "E_S07_INTERNAL_ID_BAN_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-paragraph-jobs.yaml": "E_S07_PARAGRAPH_JOB_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-rhetorical-moves.yaml": "E_S07_RHETORICAL_MOVE_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-rigid-template.yaml": "E_S07_RIGID_TEMPLATE_FORBIDDEN",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-flexible-language.yaml": "E_S07_FLEXIBLE_LANGUAGE_CONTROL_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-rigid-language-rule.yaml": "E_S07_FLEXIBLE_LANGUAGE_CONTROL_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-forbidden-expressions.yaml": "E_S07_FORBIDDEN_EXPRESSION_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-coverage-ledger.yaml": "E_S07_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-missing-downstream-handoff.yaml": "E_S07_DOWNSTREAM_HANDOFF_REQUIRED",
    ROOT / "examples/materials/invalid-s07-surface-control-new-claim.yaml": "E_S07_NO_NEW_CLAIMS",
    ROOT / "examples/materials/invalid-s07-surface-control-final-prose.yaml": "E_S07_NO_FINAL_PROSE",
    ROOT / "examples/materials/invalid-s07-surface-control-completion-overclaim.yaml": "E_S07_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s07-surface-control-claim-strengthening.yaml": "E_S07_SURFACE_SAFETY_AUDIT_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S07_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S07_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S07_YAML_LOAD", f"{path}: root must be a mapping")
    return data


def _run(script: Path, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _verify_fixtures() -> None:
    result = _run(VALIDATE_MATERIAL, S07_MATERIAL)
    if result.returncode != 0:
        _fail("E_S07_POSITIVE_FIXTURE", f"{S07_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S07_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S07_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S07_SCHEMA", "schema properties mapping missing")
    spec = props.get("S07RhetoricSurfaceControl")
    if not isinstance(spec, dict):
        _fail("E_S07_SCHEMA", "S07RhetoricSurfaceControl schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S07_SCHEMA", "S07RhetoricSurfaceControl properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s07-rhetoric-surface-control/v0.1":
        _fail("E_S07_SCHEMA", "S07RhetoricSurfaceControl.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S07":
        _fail("E_S07_SCHEMA", "S07RhetoricSurfaceControl.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = REQUIRED_SCHEMA_MODULES - required
    if missing:
        _fail("E_S07_SCHEMA", f"S07RhetoricSurfaceControl schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s07 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S07"), None)
    if not isinstance(s07, dict):
        _fail("E_S07_REGISTRY", "S07 missing from stage registry")
    if s07.get("requires_worker_task_packet") is not True:
        _fail("E_S07_REGISTRY", "S07 must keep requires_worker_task_packet=true")
    if s07.get("consumes") != PUBLIC_CONSUMES or s07.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S07_REGISTRY", "S07 public graph I/O changed")
    if s07.get("subagent_lane_policy", {}).get("policy") != "conditional_double":
        _fail("E_S07_REGISTRY", "S07 must keep conditional_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s07.get("validators", []))
    if missing:
        _fail("E_S07_REGISTRY", f"S07 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S07.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S07_CONTRACT", "S07 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S07_CONTRACT", "S07 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "conditional_double":
        _fail("E_S07_CONTRACT", "S07 contract must keep conditional_double lane policy")
    if set(contract.get("validators", [])) != set(s07.get("validators", [])):
        _fail("E_S07_CONTRACT", "S07 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S07_CONTRACT", "S07 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml":
        _fail("E_S07_CONTRACT", "S07 packet_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S07_CONTRACT", "S07 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S07_PACKET)
    if result.returncode != 0:
        _fail("E_S07_PACKET", f"S07 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S07_PACKET)
    if packet.get("target_material") != "phase10_s07_surface_control":
        _fail("E_S07_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s07_surface_control.yaml":
        _fail("E_S07_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s07_surface_control.yaml"]:
        _fail("E_S07_PACKET", "allowed_write_paths must be exactly the S07 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S07RhetoricSurfaceControl" or packet.get("expected_payload_schema") != "ppg-s07-rhetoric-surface-control/v0.1":
        _fail("E_S07_PACKET", "expected schema/material binding mismatch")
    if not REQUIRED_INPUT_MATERIALS <= set(packet.get("input_materials", [])):
        _fail("E_S07_PACKET", "required S02/S04/S05/S06/terminology inputs missing")
    if not REQUIRED_READ_PATHS <= set(packet.get("allowed_read_paths", [])):
        _fail("E_S07_PACKET", "required read paths missing")
    controls = packet.get("mandatory_controls")
    if not isinstance(controls, dict) or controls.get("no_claim_strengthening") is not True or controls.get("no_rigid_language_template") is not True:
        _fail("E_S07_PACKET", "claim-strength/flexible-template controls missing")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S07_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "no_silent_omission", "no_new_claims", "no_claim_strengthening", "no_final_prose", "no_rigid_language_template"):
        if protocol.get(key) is not True:
            _fail("E_S07_PACKET", f"internal_execution_protocol.{key} must be true")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S07_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S07_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S07RhetoricSurfaceControl" or output_contract.get("payload_schema") != "ppg-s07-rhetoric-surface-control/v0.1":
        _fail("E_S07_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S07_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    validators = set(packet.get("validators", [])) if isinstance(packet.get("validators"), list) else set()
    if not REQUIRED_PACKET_VALIDATORS <= validators:
        _fail("E_S07_PACKET", f"S07 validators missing {sorted(REQUIRED_PACKET_VALIDATORS - validators)}")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s07 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S07"), None)
    if not isinstance(s07, dict):
        _fail("E_S07_PHASE10", "S07 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s07.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S07_PHASE10", f"S07 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s07.get("required_checks", []))
    if missing_checks:
        _fail("E_S07_PHASE10", f"S07 phase10 checks missing {sorted(missing_checks)}")


def main() -> None:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S07_RHETORIC_SURFACE_CONTROL_OK")


if __name__ == "__main__":
    main()
