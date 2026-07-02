#!/usr/bin/env python3
"""Verify S05 reader-spine contract, packet, fixtures, and Phase 10 gates."""
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
S05_PACKET = ROOT / "examples" / "packets" / "phase10_s05_paper_spine_synthesis_packet.v1.yaml"
S05_MATERIAL = ROOT / "examples" / "materials" / "phase10_s05_reader_spine.yaml"
PUBLIC_CONSUMES = ["motivation", "contribution options", "template profile", "claim materials"]
PUBLIC_PRODUCES = ["reader spine", "reviewer question map", "rationale matrix"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S05_admitted_claim_intake_ledger",
    "S05_reader_question_inventory",
    "S05_reader_question_coverage_ledger",
    "S05_reader_question_progression",
    "S05_claim_to_section_spine",
    "S05_claim_section_coverage_ledger",
    "S05_front_half_promise_coverage",
    "S05_reviewer_question_map",
    "S05_rationale_matrix",
    "S05_owner_decision_log",
    "S05_s06_s07_s08_handoff_coverage",
    "S05_coherence_overpromise_audit",
    "S05_no_new_claims_or_final_prose",
    "S05_no_completion_overclaim",
}
REQUIRED_PACKET_PASSES = {
    "s04_admitted_claim_intake",
    "reader_question_inventory",
    "reader_question_progression",
    "claim_to_section_mapping",
    "front_half_promise_payoff",
    "reviewer_question_mapping",
    "rationale_matrix",
    "owner_decision_surface",
    "s06_s07_s08_handoff",
    "coherence_overpromise_audit",
    "independent_verifier_pass",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "admitted_claim_intake_ledger",
    "reader_question_inventory",
    "reader_question_coverage_ledger",
    "reader_spine.reader_question_progression",
    "reader_spine.claim_to_section_spine",
    "reader_spine.front_half_promise_map",
    "reader_spine.story_arc_matrix",
    "reviewer_question_map",
    "rationale_matrix",
    "claim_section_coverage_ledger",
    "front_half_promise_coverage",
    "excluded_claim_or_question_register",
    "owner_decision_log",
    "s06_handoff",
    "s07_handoff",
    "s08_handoff",
    "s06_s07_s08_handoff_coverage",
    "coherence_overpromise_audit",
    "unresolved_backflow_register",
    "candidate_return",
}
REQUIRED_SCHEMA_MODULES = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "admitted_claim_intake_ledger",
    "reader_question_inventory",
    "reader_question_coverage_ledger",
    "reader_spine",
    "reviewer_question_map",
    "rationale_matrix",
    "claim_section_coverage_ledger",
    "front_half_promise_coverage",
    "excluded_claim_or_question_register",
    "owner_decision_log",
    "s06_handoff",
    "s07_handoff",
    "s08_handoff",
    "s06_s07_s08_handoff_coverage",
    "coherence_overpromise_audit",
    "unresolved_backflow_register",
    "candidate_return",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s05_admitted_claim_intake_ledger",
    "s05_reader_question_inventory",
    "s05_reader_question_coverage_ledger",
    "s05_reader_question_progression",
    "s05_claim_to_section_spine",
    "s05_claim_section_coverage_ledger",
    "s05_front_half_promise_payoff",
    "s05_reviewer_question_map",
    "s05_rationale_matrix",
    "s05_owner_decision_log",
    "s05_downstream_handoff_coverage",
    "s05_coherence_overpromise_audit",
    "s05_nature_overlay",
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
    "s05_admitted_claim_intake_ledger",
    "s05_reader_question_inventory",
    "s05_reader_question_coverage_ledger",
    "s05_reader_question_progression",
    "s05_claim_to_section_spine",
    "s05_claim_section_coverage_ledger",
    "s05_front_half_promise_payoff",
    "s05_reviewer_question_map",
    "s05_rationale_matrix",
    "s05_owner_decision_log",
    "s05_s06_s07_s08_handoff_coverage",
    "s05_coherence_overpromise_audit",
    "s05_no_new_claims",
    "s05_no_final_prose",
    "s05_no_completion_overclaim",
}
REQUIRED_PACKET_VALIDATORS = {
    "validate_material:S05ReaderSpine",
    "s04_admitted_claims_required:S05",
    "reader_question_progression_required:S05",
    "claim_to_section_spine_required:S05",
    "front_half_promise_required:S05",
    "reviewer_question_map_required:S05",
    "rationale_matrix_required:S05",
    "owner_decision_log_required:S05",
    "s06_s07_s08_handoff_required:S05",
    "no_new_claims:S05",
    "no_final_prose:S05",
}
REQUIRED_INPUT_MATERIALS = {
    "phase10_s02_research_dossier",
    "phase10_s03_contribution_options",
    "phase10_s04_claim_admissibility",
    "claim_boundary_map_v2",
}
REQUIRED_READ_PATHS = {
    "examples/materials/phase10_s02_research_dossier.yaml",
    "examples/materials/phase10_s03_contribution_options.yaml",
    "examples/materials/phase10_s04_claim_admissibility.yaml",
    "examples/materials/claim_boundary_map.v2.yaml",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-admitted-claim-intake.yaml": "E_S05_ADMITTED_CLAIM_INTAKE_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-reader-question-coverage.yaml": "E_S05_READER_QUESTION_COVERAGE_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-claim-section-spine.yaml": "E_S05_CLAIM_SECTION_SPINE_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-new-claim.yaml": "E_S05_NO_NEW_CLAIMS",
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-claim-section-coverage.yaml": "E_S05_CLAIM_SECTION_COVERAGE_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-front-half-payoff.yaml": "E_S05_FRONT_HALF_PROMISE_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-rationale.yaml": "E_S05_RATIONALE_MATRIX_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-missing-s06-s07-s08-handoff.yaml": "E_S05_DOWNSTREAM_HANDOFF_REQUIRED",
    ROOT / "examples/materials/invalid-s05-reader-spine-final-prose.yaml": "E_S05_NO_FINAL_PROSE",
    ROOT / "examples/materials/invalid-s05-reader-spine-completion-overclaim.yaml": "E_S05_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s05-reader-spine-hidden-owner-decision.yaml": "E_S05_COHERENCE_AUDIT_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S05_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S05_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S05_YAML_LOAD", f"{path}: root must be a mapping")
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
    result = _run(VALIDATE_MATERIAL, S05_MATERIAL)
    if result.returncode != 0:
        _fail("E_S05_POSITIVE_FIXTURE", f"{S05_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S05_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S05_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S05_SCHEMA", "schema properties mapping missing")
    spec = props.get("S05ReaderSpine")
    if not isinstance(spec, dict):
        _fail("E_S05_SCHEMA", "S05ReaderSpine schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S05_SCHEMA", "S05ReaderSpine properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s05-reader-spine/v0.1":
        _fail("E_S05_SCHEMA", "S05ReaderSpine.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S05":
        _fail("E_S05_SCHEMA", "S05ReaderSpine.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = REQUIRED_SCHEMA_MODULES - required
    if missing:
        _fail("E_S05_SCHEMA", f"S05ReaderSpine schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s05 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S05"), None)
    if not isinstance(s05, dict):
        _fail("E_S05_REGISTRY", "S05 missing from stage registry")
    if s05.get("requires_worker_task_packet") is not True:
        _fail("E_S05_REGISTRY", "S05 must keep requires_worker_task_packet=true")
    if s05.get("consumes") != PUBLIC_CONSUMES or s05.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S05_REGISTRY", "S05 public graph I/O changed")
    if s05.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S05_REGISTRY", "S05 must keep mandatory_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s05.get("validators", []))
    if missing:
        _fail("E_S05_REGISTRY", f"S05 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S05.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S05_CONTRACT", "S05 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S05_CONTRACT", "S05 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S05_CONTRACT", "S05 contract must keep mandatory_double lane policy")
    if set(contract.get("validators", [])) != set(s05.get("validators", [])):
        _fail("E_S05_CONTRACT", "S05 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S05_CONTRACT", "S05 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml":
        _fail("E_S05_CONTRACT", "S05 packet_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S05_CONTRACT", "S05 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S05_PACKET)
    if result.returncode != 0:
        _fail("E_S05_PACKET", f"S05 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S05_PACKET)
    if packet.get("target_material") != "phase10_s05_reader_spine":
        _fail("E_S05_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s05_reader_spine.yaml":
        _fail("E_S05_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s05_reader_spine.yaml"]:
        _fail("E_S05_PACKET", "allowed_write_paths must be exactly the S05 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S05ReaderSpine" or packet.get("expected_payload_schema") != "ppg-s05-reader-spine/v0.1":
        _fail("E_S05_PACKET", "expected schema/material binding mismatch")
    if not REQUIRED_INPUT_MATERIALS <= set(packet.get("input_materials", [])):
        _fail("E_S05_PACKET", "required S02/S03/S04/claim-boundary inputs missing")
    if not REQUIRED_READ_PATHS <= set(packet.get("allowed_read_paths", [])):
        _fail("E_S05_PACKET", "required S02/S03/S04/claim-boundary read paths missing")
    controls = packet.get("mandatory_controls")
    if not isinstance(controls, dict) or controls.get("s04_controls_claim_admission") is not True or controls.get("raw_s03_claim_use_forbidden") is not True:
        _fail("E_S05_PACKET", "S04 claim-admission controls missing")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S05_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "s04_admitted_claims_required", "no_new_claims", "no_strengthened_claims", "no_final_prose", "no_silent_omission", "raw_s03_claim_use_forbidden"):
        if protocol.get(key) is not True:
            _fail("E_S05_PACKET", f"internal_execution_protocol.{key} must be true")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S05_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S05_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S05ReaderSpine" or output_contract.get("payload_schema") != "ppg-s05-reader-spine/v0.1":
        _fail("E_S05_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S05_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    ledgers = set(packet.get("coverage_ledgers_required", [])) if isinstance(packet.get("coverage_ledgers_required"), list) else set()
    required_ledgers = {"admitted_claim_intake_ledger", "reader_question_coverage_ledger", "claim_section_coverage_ledger", "front_half_promise_coverage", "s06_s07_s08_handoff_coverage"}
    if not required_ledgers <= ledgers:
        _fail("E_S05_PACKET", f"coverage_ledgers_required missing {sorted(required_ledgers - ledgers)}")
    validators = set(packet.get("validators", [])) if isinstance(packet.get("validators"), list) else set()
    if not REQUIRED_PACKET_VALIDATORS <= validators:
        _fail("E_S05_PACKET", f"S05 material/spine validators missing {sorted(REQUIRED_PACKET_VALIDATORS - validators)}")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s05 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S05"), None)
    if not isinstance(s05, dict):
        _fail("E_S05_PHASE10", "S05 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s05.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S05_PHASE10", f"S05 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s05.get("required_checks", []))
    if missing_checks:
        _fail("E_S05_PHASE10", f"S05 phase10 checks missing {sorted(missing_checks)}")


def main() -> None:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S05_READER_SPINE_OK")


if __name__ == "__main__":
    main()
