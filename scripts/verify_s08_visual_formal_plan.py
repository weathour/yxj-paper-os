#!/usr/bin/env python3
"""Verify S08 visual/formal planning contract, packet, schema, and fixtures."""
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
S08_PACKET = ROOT / "examples" / "packets" / "phase10_s08_visual_formal_planning_packet.v1.yaml"
S08_MATERIAL = ROOT / "examples" / "materials" / "phase10_s08_visual_formal_plan.yaml"
PUBLIC_CONSUMES = ["reader spine", "section function budget", "claim evidence materials"]
PUBLIC_PRODUCES = ["visual budget", "figure contract", "panel evidence map", "backend route"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S08_input_coverage",
    "S08_visual_need_inventory",
    "S08_candidate_visual_object_queue",
    "S08_visual_budget",
    "S08_main_story_visual_path",
    "S08_figure_contract_schema",
    "S08_table_contract_schema",
    "S08_formal_object_contract_schema",
    "S08_panel_evidence_map",
    "S08_visual_claim_evidence_binding",
    "S08_explanatory_vs_evidential_boundary",
    "S08_main_supplement_split",
    "S08_backend_route_map",
    "S08_caption_boundary",
    "S08_accessibility_constraints",
    "S08_coverage_ledger",
    "S08_unresolved_visual_object_report",
    "S08_downstream_handoff",
    "S08_no_new_claims_or_completion_overclaim",
}
REQUIRED_PACKET_PASSES = {
    "boot_authority_boundary",
    "input_coverage_check",
    "claim_evidence_normalization",
    "reader_question_visual_need_extraction",
    "object_formalization_need_extraction",
    "source_data_backend_inventory",
    "candidate_visual_object_queue_generation",
    "visual_budget_and_main_story_path_design",
    "figure_contract_construction",
    "table_contract_construction",
    "formal_object_contract_construction",
    "panel_evidence_mapping",
    "visual_claim_evidence_binding_audit",
    "main_supplement_split",
    "backend_route_planning",
    "caption_legend_boundary",
    "accessibility_style_constraints",
    "coverage_ledger_and_unresolved_report",
    "downstream_handoff",
    "independent_verifier_pass",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "authority_boundary_audit",
    "input_coverage_ledger",
    "source_data_inventory_projection",
    "normalized_claim_evidence_table",
    "visual_need_inventory",
    "formal_visual_need_map",
    "candidate_visual_object_queue",
    "visual_budget",
    "main_story_visual_path",
    "figure_contracts",
    "table_contracts",
    "formal_object_contracts",
    "panel_evidence_map",
    "visual_claim_evidence_map",
    "backend_route_map",
    "main_supplement_split_plan",
    "caption_legend_brief",
    "accessibility_and_style_constraints",
    "coverage_ledger",
    "unresolved_visual_object_report",
    "downstream_handoff",
    "visual_safety_audit",
    "candidate_return",
}
REQUIRED_SCHEMA_MODULES = REQUIRED_OUTPUT_MODULES | {"schema_version", "stage_id"}
REQUIRED_PHASE10_DIMENSIONS = {
    "s08_input_coverage",
    "s08_visual_need_inventory",
    "s08_candidate_visual_object_queue",
    "s08_visual_budget",
    "s08_figure_contract_schema",
    "s08_table_contract_schema",
    "s08_formal_object_contract_schema",
    "s08_panel_evidence_map",
    "s08_visual_claim_evidence_binding",
    "s08_explanatory_vs_evidential_boundary",
    "s08_main_supplement_split",
    "s08_backend_route_map",
    "s08_caption_boundary",
    "s08_accessibility_constraints",
    "s08_coverage_ledger",
    "s08_downstream_handoff",
    "s08_visual_safety_audit",
    "s08_nature_overlay",
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
    "s08_input_coverage",
    "s08_visual_need_inventory",
    "s08_candidate_visual_object_queue",
    "s08_visual_budget",
    "s08_main_story_visual_path",
    "s08_figure_contract_schema",
    "s08_table_contract_schema",
    "s08_formal_object_contract_schema",
    "s08_panel_evidence_map",
    "s08_visual_claim_evidence_binding",
    "s08_explanatory_vs_evidential_boundary",
    "s08_main_supplement_split",
    "s08_backend_route_map",
    "s08_caption_boundary",
    "s08_accessibility_constraints",
    "s08_coverage_ledger",
    "s08_unresolved_visual_object_report",
    "s08_downstream_handoff",
    "s08_no_new_claims",
    "s08_no_claim_strengthening",
    "s08_no_final_figures",
    "s08_no_final_captions",
    "s08_no_schematic_as_empirical_evidence",
    "s08_no_completion_overclaim",
}
REQUIRED_PACKET_VALIDATORS = {
    "validate_material:S08VisualFormalPlan",
    "input_coverage_required:S08",
    "visual_need_inventory_required:S08",
    "candidate_visual_object_queue_required:S08",
    "visual_budget_required:S08",
    "figure_contract_schema_required:S08",
    "table_contract_schema_required:S08",
    "formal_object_contract_schema_required:S08",
    "panel_evidence_map_required:S08",
    "visual_claim_evidence_binding_required:S08",
    "backend_route_map_required:S08",
    "caption_boundary_required:S08",
    "accessibility_constraints_required:S08",
    "coverage_ledger_required:S08",
    "downstream_handoff_required:S08",
    "no_new_claims:S08",
    "no_claim_strengthening:S08",
    "no_final_figures:S08",
    "no_final_captions:S08",
    "no_schematic_as_empirical_evidence:S08",
}
REQUIRED_INPUT_MATERIALS = {
    "phase10_s04_claim_admissibility",
    "phase10_s05_reader_spine",
    "phase10_s06_object_granularity",
    "s01_source_evidence_inventory_v1",
    "evidence_inventory_v1",
    "terminology_register_v1",
}
REQUIRED_READ_PATHS = {
    "examples/materials/phase10_s04_claim_admissibility.yaml",
    "examples/materials/phase10_s05_reader_spine.yaml",
    "examples/materials/phase10_s06_object_granularity.yaml",
    "examples/materials/s01_source_evidence_inventory.v1.yaml",
    "examples/materials/evidence_inventory.v1.yaml",
    "examples/materials/terminology_register.v1.yaml",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-input-coverage.yaml": "E_S08_INPUT_COVERAGE_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-visual-needs.yaml": "E_S08_VISUAL_NEED_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-candidate-queue.yaml": "E_S08_CANDIDATE_QUEUE_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-visual-budget.yaml": "E_S08_VISUAL_BUDGET_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-figure-contract.yaml": "E_S08_FIGURE_CONTRACT_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-table-contract.yaml": "E_S08_TABLE_CONTRACT_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-formal-object-contract.yaml": "E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-panel-evidence.yaml": "E_S08_PANEL_EVIDENCE_MAP_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-visual-claim-binding.yaml": "E_S08_VISUAL_CLAIM_BINDING_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-backend-route.yaml": "E_S08_BACKEND_ROUTE_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-caption-boundary.yaml": "E_S08_CAPTION_BOUNDARY_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-accessibility.yaml": "E_S08_ACCESSIBILITY_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-missing-downstream-handoff.yaml": "E_S08_DOWNSTREAM_HANDOFF_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-hidden-unresolved.yaml": "E_S08_UNRESOLVED_VISUAL_OBJECT_REQUIRED",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-new-claim.yaml": "E_S08_NO_NEW_CLAIMS",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-schematic-as-evidence.yaml": "E_S08_EXPLANATORY_EVIDENTIAL_BOUNDARY",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-final-artifact.yaml": "E_S08_NO_FINAL_ARTIFACT",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-completion-overclaim.yaml": "E_S08_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s08-visual-formal-plan-claim-strengthening.yaml": "E_S08_VISUAL_SAFETY_AUDIT_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S08_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S08_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S08_YAML_LOAD", f"{path}: root must be a mapping")
    return data


def _run(script: Path, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _verify_fixtures() -> None:
    result = _run(VALIDATE_MATERIAL, S08_MATERIAL)
    if result.returncode != 0:
        _fail("E_S08_POSITIVE_FIXTURE", f"{S08_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S08_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S08_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S08_SCHEMA", "schema properties mapping missing")
    spec = props.get("S08VisualFormalPlan")
    if not isinstance(spec, dict):
        _fail("E_S08_SCHEMA", "S08VisualFormalPlan schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S08_SCHEMA", "S08VisualFormalPlan properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s08-visual-formal-plan/v0.1":
        _fail("E_S08_SCHEMA", "S08VisualFormalPlan.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S08":
        _fail("E_S08_SCHEMA", "S08VisualFormalPlan.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = REQUIRED_SCHEMA_MODULES - required
    if missing:
        _fail("E_S08_SCHEMA", f"S08VisualFormalPlan schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s08 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S08"), None)
    if not isinstance(s08, dict):
        _fail("E_S08_REGISTRY", "S08 missing from stage registry")
    if s08.get("requires_worker_task_packet") is not True:
        _fail("E_S08_REGISTRY", "S08 must keep requires_worker_task_packet=true")
    if s08.get("consumes") != PUBLIC_CONSUMES or s08.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S08_REGISTRY", "S08 public graph I/O changed")
    if s08.get("subagent_lane_policy", {}).get("policy") != "conditional_double":
        _fail("E_S08_REGISTRY", "S08 must keep conditional_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s08.get("validators", []))
    if missing:
        _fail("E_S08_REGISTRY", f"S08 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S08.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S08_CONTRACT", "S08 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S08_CONTRACT", "S08 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "conditional_double":
        _fail("E_S08_CONTRACT", "S08 contract must keep conditional_double lane policy")
    if set(contract.get("validators", [])) != set(s08.get("validators", [])):
        _fail("E_S08_CONTRACT", "S08 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S08_CONTRACT", "S08 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml":
        _fail("E_S08_CONTRACT", "S08 packet_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S08_CONTRACT", "S08 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S08_PACKET)
    if result.returncode != 0:
        _fail("E_S08_PACKET", f"S08 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S08_PACKET)
    if packet.get("target_material") != "phase10_s08_visual_formal_plan":
        _fail("E_S08_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s08_visual_formal_plan.yaml":
        _fail("E_S08_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s08_visual_formal_plan.yaml"]:
        _fail("E_S08_PACKET", "allowed_write_paths must be exactly the S08 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S08VisualFormalPlan" or packet.get("expected_payload_schema") != "ppg-s08-visual-formal-plan/v0.1":
        _fail("E_S08_PACKET", "expected schema/material binding mismatch")
    if not REQUIRED_INPUT_MATERIALS <= set(packet.get("input_materials", [])):
        _fail("E_S08_PACKET", "required S04/S05/S06/S01/evidence/terminology inputs missing")
    if not REQUIRED_READ_PATHS <= set(packet.get("allowed_read_paths", [])):
        _fail("E_S08_PACKET", "required read paths missing")
    controls = packet.get("mandatory_controls")
    if not isinstance(controls, dict) or controls.get("no_final_figures") is not True or controls.get("no_final_captions") is not True or controls.get("no_schematic_as_empirical_evidence") is not True:
        _fail("E_S08_PACKET", "final-artifact and schematic/evidence controls missing")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S08_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "no_silent_omission", "no_new_claims", "no_claim_strengthening", "no_final_figures", "no_final_captions"):
        if protocol.get(key) is not True:
            _fail("E_S08_PACKET", f"internal_execution_protocol.{key} must be true")
    if protocol.get("correct_order_required") != "need_to_candidate_to_contract_to_evidence_to_backend_to_caption_to_coverage":
        _fail("E_S08_PACKET", "S08 protocol must encode correct execution order")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S08_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S08_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S08VisualFormalPlan" or output_contract.get("payload_schema") != "ppg-s08-visual-formal-plan/v0.1":
        _fail("E_S08_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S08_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    validators = set(packet.get("validators", [])) if isinstance(packet.get("validators"), list) else set()
    if not REQUIRED_PACKET_VALIDATORS <= validators:
        _fail("E_S08_PACKET", f"S08 validators missing {sorted(REQUIRED_PACKET_VALIDATORS - validators)}")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s08 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S08"), None)
    if not isinstance(s08, dict):
        _fail("E_S08_PHASE10", "S08 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s08.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S08_PHASE10", f"S08 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s08.get("required_checks", []))
    if missing_checks:
        _fail("E_S08_PHASE10", f"S08 phase10 checks missing {sorted(missing_checks)}")


def main() -> None:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S08_VISUAL_FORMAL_PLAN_OK")


if __name__ == "__main__":
    main()
