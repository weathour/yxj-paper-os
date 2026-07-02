#!/usr/bin/env python3
"""Verify S06 object-granularity contract and fixtures."""
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
S06_PACKET = ROOT / "examples" / "packets" / "phase10_s06_object_granularity_design_packet.v1.yaml"
S06_MATERIAL = ROOT / "examples" / "materials" / "phase10_s06_object_granularity.yaml"
PUBLIC_CONSUMES = ["reader spine", "reviewer question map", "template profile", "claim visibility"]
PUBLIC_PRODUCES = ["object representation matrix", "section function budget", "load budget", "explanation ladder"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S06_object_inventory_coverage",
    "S06_mechanism_variable_coverage",
    "S06_object_cards_for_P0_P1_P2",
    "S06_mechanism_variable_cards",
    "S06_claim_object_mapping",
    "S06_reader_question_object_mapping",
    "S06_object_section_mapping",
    "S06_granularity_progression",
    "S06_section_function_budget",
    "S06_cognitive_load_budget",
    "S06_explanation_ladder",
    "S06_no_flat_repetition",
    "S06_coverage_ledger",
    "S06_unresolved_object_report",
    "S06_downstream_handoff",
    "S06_no_new_claims_or_final_prose",
    "S06_no_completion_overclaim",
}
REQUIRED_PACKET_PASSES = {
    "object_inventory_extraction",
    "mechanism_variable_inventory",
    "object_cards",
    "mechanism_variable_cards",
    "cross_maps",
    "granularity_and_load_design",
    "explanation_ladder",
    "repetition_and_completeness_check",
    "downstream_handoff",
    "independent_verifier_pass",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "object_inventory",
    "mechanism_variable_inventory",
    "object_cards",
    "mechanism_variable_cards",
    "cross_maps",
    "granularity_progression_map",
    "section_function_budget",
    "cognitive_load_budget",
    "explanation_ladder",
    "repetition_risk_register",
    "coverage_ledger",
    "unresolved_object_report",
    "handoff_to_s07",
    "handoff_to_s08",
    "handoff_to_s10",
    "coherence_and_boundary_audit",
    "candidate_return",
}
REQUIRED_SCHEMA_MODULES = REQUIRED_OUTPUT_MODULES | {"schema_version", "stage_id"}
REQUIRED_PHASE10_DIMENSIONS = {
    "s06_object_inventory_coverage",
    "s06_mechanism_variable_coverage",
    "s06_object_cards",
    "s06_mechanism_variable_cards",
    "s06_claim_object_mapping",
    "s06_reader_question_object_mapping",
    "s06_object_section_mapping",
    "s06_granularity_progression",
    "s06_section_function_budget",
    "s06_cognitive_load_budget",
    "s06_explanation_ladder",
    "s06_no_flat_repetition",
    "s06_coverage_ledger",
    "s06_unresolved_object_report",
    "s06_downstream_handoff_coverage",
    "s06_boundary_audit",
    "s06_nature_overlay",
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
    "s06_object_inventory_coverage",
    "s06_mechanism_variable_coverage",
    "s06_object_cards",
    "s06_mechanism_variable_cards",
    "s06_claim_object_mapping",
    "s06_reader_question_object_mapping",
    "s06_object_section_mapping",
    "s06_granularity_progression",
    "s06_section_function_budget",
    "s06_cognitive_load_budget",
    "s06_explanation_ladder",
    "s06_no_flat_repetition",
    "s06_coverage_ledger",
    "s06_unresolved_object_report",
    "s06_downstream_handoff_coverage",
    "s06_no_new_claims",
    "s06_no_final_prose",
    "s06_no_completion_overclaim",
}
REQUIRED_PACKET_VALIDATORS = {
    "validate_material:S06ObjectGranularity",
    "object_inventory_required:S06",
    "mechanism_variable_inventory_required:S06",
    "object_cards_required:S06",
    "mechanism_variable_cards_required:S06",
    "claim_object_mapping_required:S06",
    "reader_question_object_mapping_required:S06",
    "granularity_progression_required:S06",
    "section_function_budget_required:S06",
    "cognitive_load_budget_required:S06",
    "explanation_ladder_required:S06",
    "downstream_handoff_required:S06",
    "no_new_claims:S06",
    "no_final_prose:S06",
}
REQUIRED_INPUT_MATERIALS = {
    "phase10_s05_reader_spine",
    "phase10_s04_claim_admissibility",
    "phase10_s02_research_dossier",
    "claim_boundary_map_v2",
}
REQUIRED_READ_PATHS = {
    "examples/materials/phase10_s05_reader_spine.yaml",
    "examples/materials/phase10_s04_claim_admissibility.yaml",
    "examples/materials/phase10_s02_research_dossier.yaml",
    "examples/materials/claim_boundary_map.v2.yaml",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-object-inventory.yaml": "E_S06_OBJECT_INVENTORY_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-variable-inventory.yaml": "E_S06_MECHANISM_VARIABLE_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-object-cards.yaml": "E_S06_OBJECT_CARD_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-variable-cards.yaml": "E_S06_MECHANISM_VARIABLE_CARD_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-new-claim.yaml": "E_S06_NO_NEW_CLAIMS",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-reader-question-map.yaml": "E_S06_READER_QUESTION_OBJECT_MAP_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-granularity-map.yaml": "E_S06_GRANULARITY_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-section-budget.yaml": "E_S06_SECTION_FUNCTION_BUDGET_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-load-budget.yaml": "E_S06_COGNITIVE_LOAD_BUDGET_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-explanation-ladder.yaml": "E_S06_EXPLANATION_LADDER_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-coverage-ledger.yaml": "E_S06_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-missing-downstream-handoff.yaml": "E_S06_DOWNSTREAM_HANDOFF_REQUIRED",
    ROOT / "examples/materials/invalid-s06-object-granularity-final-prose.yaml": "E_S06_NO_FINAL_PROSE",
    ROOT / "examples/materials/invalid-s06-object-granularity-completion-overclaim.yaml": "E_S06_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s06-object-granularity-hidden-unresolved.yaml": "E_S06_BOUNDARY_AUDIT_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S06_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S06_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S06_YAML_LOAD", f"{path}: root must be a mapping")
    return data


def _run(script: Path, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _verify_fixtures() -> None:
    result = _run(VALIDATE_MATERIAL, S06_MATERIAL)
    if result.returncode != 0:
        _fail("E_S06_POSITIVE_FIXTURE", f"{S06_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S06_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S06_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S06_SCHEMA", "schema properties mapping missing")
    spec = props.get("S06ObjectGranularity")
    if not isinstance(spec, dict):
        _fail("E_S06_SCHEMA", "S06ObjectGranularity schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S06_SCHEMA", "S06ObjectGranularity properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s06-object-granularity/v0.1":
        _fail("E_S06_SCHEMA", "S06ObjectGranularity.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S06":
        _fail("E_S06_SCHEMA", "S06ObjectGranularity.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = REQUIRED_SCHEMA_MODULES - required
    if missing:
        _fail("E_S06_SCHEMA", f"S06ObjectGranularity schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s06 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S06"), None)
    if not isinstance(s06, dict):
        _fail("E_S06_REGISTRY", "S06 missing from stage registry")
    if s06.get("requires_worker_task_packet") is not True:
        _fail("E_S06_REGISTRY", "S06 must keep requires_worker_task_packet=true")
    if s06.get("consumes") != PUBLIC_CONSUMES or s06.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S06_REGISTRY", "S06 public graph I/O changed")
    if s06.get("subagent_lane_policy", {}).get("policy") != "conditional_double":
        _fail("E_S06_REGISTRY", "S06 must keep conditional_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s06.get("validators", []))
    if missing:
        _fail("E_S06_REGISTRY", f"S06 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S06.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S06_CONTRACT", "S06 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S06_CONTRACT", "S06 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "conditional_double":
        _fail("E_S06_CONTRACT", "S06 contract must keep conditional_double lane policy")
    if set(contract.get("validators", [])) != set(s06.get("validators", [])):
        _fail("E_S06_CONTRACT", "S06 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S06_CONTRACT", "S06 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml":
        _fail("E_S06_CONTRACT", "S06 packet_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S06_CONTRACT", "S06 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S06_PACKET)
    if result.returncode != 0:
        _fail("E_S06_PACKET", f"S06 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S06_PACKET)
    if packet.get("target_material") != "phase10_s06_object_granularity":
        _fail("E_S06_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s06_object_granularity.yaml":
        _fail("E_S06_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s06_object_granularity.yaml"]:
        _fail("E_S06_PACKET", "allowed_write_paths must be exactly the S06 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S06ObjectGranularity" or packet.get("expected_payload_schema") != "ppg-s06-object-granularity/v0.1":
        _fail("E_S06_PACKET", "expected schema/material binding mismatch")
    if not REQUIRED_INPUT_MATERIALS <= set(packet.get("input_materials", [])):
        _fail("E_S06_PACKET", "required S05/S04/S02 inputs missing")
    if not REQUIRED_READ_PATHS <= set(packet.get("allowed_read_paths", [])):
        _fail("E_S06_PACKET", "required S05/S04/S02 read paths missing")
    controls = packet.get("mandatory_controls")
    if not isinstance(controls, dict) or controls.get("s04_claim_visibility_required") is not True or controls.get("s05_reader_spine_required") is not True or controls.get("no_silent_omission") is not True:
        _fail("E_S06_PACKET", "S04/S05/no-silent-omission controls missing")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S06_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "s04_claim_visibility_required", "s05_reader_spine_required", "no_silent_omission", "no_new_claims", "no_final_prose"):
        if protocol.get(key) is not True:
            _fail("E_S06_PACKET", f"internal_execution_protocol.{key} must be true")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S06_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S06_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S06ObjectGranularity" or output_contract.get("payload_schema") != "ppg-s06-object-granularity/v0.1":
        _fail("E_S06_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S06_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    validators = set(packet.get("validators", [])) if isinstance(packet.get("validators"), list) else set()
    if not REQUIRED_PACKET_VALIDATORS <= validators:
        _fail("E_S06_PACKET", f"S06 validators missing {sorted(REQUIRED_PACKET_VALIDATORS - validators)}")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s06 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S06"), None)
    if not isinstance(s06, dict):
        _fail("E_S06_PHASE10", "S06 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s06.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S06_PHASE10", f"S06 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s06.get("required_checks", []))
    if missing_checks:
        _fail("E_S06_PHASE10", f"S06 phase10 checks missing {sorted(missing_checks)}")


def main() -> None:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S06_OBJECT_GRANULARITY_OK")


if __name__ == "__main__":
    main()
