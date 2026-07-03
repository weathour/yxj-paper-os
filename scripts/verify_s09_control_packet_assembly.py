#!/usr/bin/env python3
"""Verify S09A rich control selection and S09B strict task-packet assembly."""
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
S09A_MATERIAL = ROOT / "examples/materials/phase10_s09a_rich_control_bundle.yaml"
S09B_MATERIAL = ROOT / "examples/materials/phase10_s09b_task_packet_assembly.yaml"
S09B_PACKET = ROOT / "examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml"
S09A_PUBLIC_CONSUMES = ["claim controls", "spine controls", "granularity controls", "surface rules", "target unit"]
S09A_PUBLIC_PRODUCES = ["selected control bundle", "control priority map", "missing control report"]
S09B_PUBLIC_CONSUMES = ["selected control bundle", "evidence anchors", "target unit", "validator refs", "return format", "material closure obligations"]
S09B_PUBLIC_PRODUCES = ["task packet", "section move plan", "single-writer lock", "material closure manifest", "material read obligations", "missing material report"]
S09A_REQUIRED_VALIDATORS = {
    "S09A_target_unit_profile",
    "S09A_hard_constraints_present",
    "S09A_rich_context_layering",
    "S09A_claim_control_selection",
    "S09A_reader_context_selection",
    "S09A_object_context_selection",
    "S09A_surface_control_selection",
    "S09A_visual_formal_control_selection",
    "S09A_negative_controls",
    "S09A_conflict_resolution",
    "S09A_context_usage_instructions",
    "S09A_freshness_check",
    "S09A_missing_control_report",
    "S09A_coverage_ledger",
    "S09A_downstream_packet_requirements",
    "S09A_no_bare_S09",
    "S09A_no_task_packet_or_final_content",
}
S09B_REQUIRED_VALIDATORS = {
    "S09B_packet_identity",
    "S09B_allowed_read_paths",
    "S09B_allowed_write_paths",
    "S09B_forbidden_routes",
    "S09B_worker_boot_clause",
    "S09B_completion_forbidden",
    "S09B_no_recursive_orchestration",
    "S09B_single_writer_lock",
    "S09B_unit_move_plan",
    "S09B_selected_controls_propagated",
    "S09B_context_usage_preserved",
    "S09B_background_not_claim_authority",
    "S09B_control_digest_policy",
    "S09B_global_material_coverage",
    "S09B_unit_material_closure",
    "S09B_material_access_manifest",
    "S09B_material_read_obligations",
    "S09B_deferred_control_ledger",
    "S09B_section_specific_blockers",
    "S09B_return_format",
    "S09B_missing_material_report",
    "S09B_authority_boundary",
    "S09B_emitted_packet_validates",
    "S09B_no_bare_S09",
}
S09A_REQUIRED_SCHEMA = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary_audit",
    "target_unit_profile",
    "hard_constraints",
    "local_context",
    "adjacent_context",
    "global_orientation",
    "claim_control_bundle",
    "reader_context_bundle",
    "object_context_bundle",
    "surface_control_bundle",
    "visual_formal_control_bundle",
    "evidence_anchor_bundle",
    "negative_control_bundle",
    "conflict_resolution_log",
    "control_priority_map",
    "context_usage_instructions",
    "excluded_or_deferred_controls",
    "freshness_check",
    "missing_control_report",
    "coverage_ledger",
    "downstream_packet_requirements",
    "candidate_return",
}
S09B_REQUIRED_SCHEMA = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "packet_identity",
    "target_unit",
    "selected_control_bundle_ref",
    "control_digest",
    "control_digest_policy",
    "global_material_coverage",
    "unit_material_closure",
    "material_access_manifest",
    "material_read_obligations",
    "deferred_control_ledger",
    "section_specific_blockers",
    "task_mission",
    "allowed_read_paths",
    "allowed_write_paths",
    "forbidden_routes",
    "worker_boot_clause",
    "section_or_unit_move_plan",
    "claim_boundary_controls",
    "reader_spine_controls",
    "object_granularity_controls",
    "terminology_surface_controls",
    "visual_formal_controls",
    "negative_controls",
    "context_usage_instructions",
    "validators",
    "return_format",
    "single_writer_lock",
    "stale_material_policy",
    "missing_material_report",
    "packet_authority_boundary",
    "emitted_task_packet",
    "candidate_return",
}
S09B_MATERIAL_CLOSURE_FIELDS = {
    "control_digest_policy",
    "global_material_coverage",
    "unit_material_closure",
    "material_access_manifest",
    "material_read_obligations",
    "deferred_control_ledger",
    "section_specific_blockers",
}
S09A_REQUIRED_PHASE10_DIMENSIONS = {
    "s09a_target_unit_profile",
    "s09a_hard_constraints",
    "s09a_rich_context_layering",
    "s09a_claim_reader_object_surface_visual_controls",
    "s09a_negative_controls",
    "s09a_conflict_resolution",
    "s09a_context_usage",
    "s09a_freshness_missing_coverage",
    "s09a_downstream_packet_requirements",
    "s09a_nature_overlay",
}
S09B_REQUIRED_PHASE10_DIMENSIONS = {
    "s09b_packet_identity",
    "s09b_allowed_paths",
    "s09b_authority_boundary",
    "s09b_unit_move_plan",
    "s09b_selected_controls_propagated",
    "s09b_material_closure",
    "s09b_return_lock_stale",
    "s09b_emitted_packet_validates",
    "s09b_nature_overlay",
}
S09A_REQUIRED_PHASE10_CHECKS = {
    "s09a_target_unit_profile",
    "s09a_hard_constraints_present",
    "s09a_rich_context_layering",
    "s09a_claim_control_selection",
    "s09a_reader_context_selection",
    "s09a_object_context_selection",
    "s09a_surface_control_selection",
    "s09a_visual_formal_control_selection",
    "s09a_negative_controls",
    "s09a_conflict_resolution",
    "s09a_context_usage_instructions",
    "s09a_freshness_check",
    "s09a_missing_control_report",
    "s09a_coverage_ledger",
    "s09a_downstream_packet_requirements",
    "s09a_no_task_packet_compilation",
    "s09a_no_final_content",
    "s09a_no_completion_overclaim",
    "s09a_no_bare_s09",
}
S09B_REQUIRED_PHASE10_CHECKS = {
    "s09b_packet_identity",
    "s09b_allowed_read_paths",
    "s09b_allowed_write_paths",
    "s09b_forbidden_routes",
    "s09b_worker_boot_clause",
    "s09b_completion_forbidden",
    "s09b_no_recursive_orchestration",
    "s09b_single_writer_lock",
    "s09b_unit_move_plan",
    "s09b_selected_controls_propagated",
    "s09b_context_usage_preserved",
    "s09b_background_not_claim_authority",
    "s09b_control_digest_policy",
    "s09b_global_material_coverage",
    "s09b_unit_material_closure",
    "s09b_material_access_manifest",
    "s09b_material_read_obligations",
    "s09b_deferred_control_ledger",
    "s09b_section_specific_blockers",
    "s09b_return_format",
    "s09b_missing_material_report",
    "s09b_authority_boundary",
    "s09b_emitted_packet_validates",
    "s09b_no_candidate_content",
    "s09b_no_completion_overclaim",
    "s09b_no_bare_s09",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-target-unit.yaml": "E_S09A_TARGET_UNIT_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-hard-constraints.yaml": "E_S09A_HARD_CONSTRAINTS_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-local-context.yaml": "E_S09A_RICH_CONTEXT_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-visual-controls.yaml": "E_S09A_VISUAL_CONTROL_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-conflict-resolution.yaml": "E_S09A_CONFLICT_RESOLUTION_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-context-usage.yaml": "E_S09A_CONTEXT_USAGE_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-stale-freshness.yaml": "E_S09A_FRESHNESS_CHECK_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-missing-downstream-requirements.yaml": "E_S09A_DOWNSTREAM_PACKET_REQUIREMENTS_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-blocking-missing-control.yaml": "E_S09A_MISSING_CONTROL_REPORT_REQUIRED",
    ROOT / "examples/materials/invalid-s09a-rich-control-final-content.yaml": "E_S09A_NO_FINAL_CONTENT",
    ROOT / "examples/materials/invalid-s09a-rich-control-completion-overclaim.yaml": "E_S09A_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-identity.yaml": "E_S09B_PACKET_IDENTITY_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-unsafe-write-path.yaml": "E_S09B_ALLOWED_WRITE_PATHS_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-forbidden-route.yaml": "E_S09B_FORBIDDEN_ROUTES_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-weak-boot-clause.yaml": "E_S09B_WORKER_BOOT_CLAUSE_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-move-plan.yaml": "E_S09B_UNIT_MOVE_PLAN_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-context-usage.yaml": "E_S09B_CONTEXT_USAGE_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-return-format.yaml": "E_S09B_RETURN_FORMAT_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-single-writer-lock.yaml": "E_S09B_SINGLE_WRITER_LOCK_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-authority-expansion.yaml": "E_S09B_AUTHORITY_BOUNDARY_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-candidate-content.yaml": "E_S09B_NO_CANDIDATE_CONTENT",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-completion-overclaim.yaml": "E_S09B_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-emitted-packet.yaml": "E_S09B_EMITTED_PACKET_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-missing-material-closure.yaml": "E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-rejected-alias.yaml": "E_S09B_FORBIDDEN_ALIAS_FIELD",
    ROOT / "examples/materials/invalid-s09b-task-packet-assembly-selector-map-missing-material.yaml": "E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED",
}
NEGATIVE_PACKET_FIXTURES = {
    ROOT / "examples/packets/invalid-s09b-s10-missing-read-obligations.yaml": "E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED",
    ROOT / "examples/packets/invalid-s09b-s10-renamed-missing-closure.yaml": "E_S09B_CONTROL_DIGEST_POLICY_REQUIRED",
    ROOT / "examples/packets/invalid-s09b-s10-selector-map-missing-material.yaml": "E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S09_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S09_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S09_YAML_LOAD", f"{path}: root must be a mapping")
    return data


def _run(script: Path, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _verify_fixtures() -> None:
    for material in (S09A_MATERIAL, S09B_MATERIAL):
        result = _run(VALIDATE_MATERIAL, material)
        if result.returncode != 0:
            _fail("E_S09_POSITIVE_FIXTURE", f"{material} should validate but failed:\n{result.stdout}")
    result = _run(VALIDATE_PACKET, S09B_PACKET)
    if result.returncode != 0:
        _fail("E_S09_PACKET_FIXTURE", f"{S09B_PACKET} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S09_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S09_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")
    for path, expected_code in NEGATIVE_PACKET_FIXTURES.items():
        result = _run(VALIDATE_PACKET, path)
        if result.returncode == 0:
            _fail("E_S09_NEGATIVE_PACKET_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S09_NEGATIVE_PACKET_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S09_SCHEMA", "schema properties mapping missing")
    for name, version, stage_id, required_fields in (
        ("S09ARichControlBundle", "ppg-s09a-rich-control-selection/v0.1", "S09A", S09A_REQUIRED_SCHEMA),
        ("S09BTaskPacketAssembly", "ppg-s09b-task-packet-assembly/v0.1", "S09B", S09B_REQUIRED_SCHEMA),
    ):
        spec = props.get(name)
        if not isinstance(spec, dict):
            _fail("E_S09_SCHEMA", f"{name} schema missing")
        nested = spec.get("properties")
        if not isinstance(nested, dict):
            _fail("E_S09_SCHEMA", f"{name} properties missing")
        if nested.get("schema_version", {}).get("const") != version:
            _fail("E_S09_SCHEMA", f"{name}.schema_version const mismatch")
        if nested.get("stage_id", {}).get("const") != stage_id:
            _fail("E_S09_SCHEMA", f"{name}.stage_id const mismatch")
        required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
        missing = required_fields - required
        if missing:
            _fail("E_S09_SCHEMA", f"{name} required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    stages = {stage.get("stage_id"): stage for stage in registry.get("stages", []) if isinstance(stage, dict)}
    if "S09" in stages:
        _fail("E_S09_BARE_STAGE", "bare S09 must not exist")
    for sid, consumes, produces, required_validators in (
        ("S09A", S09A_PUBLIC_CONSUMES, S09A_PUBLIC_PRODUCES, S09A_REQUIRED_VALIDATORS),
        ("S09B", S09B_PUBLIC_CONSUMES, S09B_PUBLIC_PRODUCES, S09B_REQUIRED_VALIDATORS),
    ):
        stage = stages.get(sid)
        if not isinstance(stage, dict):
            _fail("E_S09_REGISTRY", f"{sid} missing from stage registry")
        if stage.get("requires_worker_task_packet") is not False:
            _fail("E_S09_REGISTRY", f"{sid} must keep requires_worker_task_packet=false")
        if stage.get("consumes") != consumes or stage.get("produces") != produces:
            _fail("E_S09_REGISTRY", f"{sid} public graph I/O changed")
        if stage.get("subagent_lane_policy", {}).get("policy") != "single_with_deterministic_validation":
            _fail("E_S09_REGISTRY", f"{sid} must keep deterministic single-lane policy")
        missing = required_validators - set(stage.get("validators", []))
        if missing:
            _fail("E_S09_REGISTRY", f"{sid} registry validators missing {sorted(missing)}")

        contract = _load_json(ROOT / f"examples/stage-contracts/{sid}.stage-contract.json")
        assert isinstance(contract, dict)
        if contract.get("requires_worker_task_packet") is not False:
            _fail("E_S09_CONTRACT", f"{sid} stage contract must keep requires_worker_task_packet=false")
        if contract.get("consumes") != consumes or contract.get("produces") != produces:
            _fail("E_S09_CONTRACT", f"{sid} contract public graph I/O changed")
        if set(contract.get("validators", [])) != set(stage.get("validators", [])):
            _fail("E_S09_CONTRACT", f"{sid} registry/contract validators diverged")
        packet = contract.get("worker_packet_coverage")
        if not isinstance(packet, dict) or packet.get("status") != "not_required" or packet.get("packet_ref") is not None:
            _fail("E_S09_CONTRACT", f"{sid} must not advertise fake worker packets")
        authority = contract.get("worker_authority_boundary")
        if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
            _fail("E_S09_CONTRACT", f"{sid} worker authority boundary weakened")


def _verify_s09b_packet() -> None:
    packet = _load_yaml(S09B_PACKET)
    if packet.get("stage_id") != "S10" or packet.get("stage_contract_ref") != "examples/stage-contracts/S10.stage-contract.json":
        _fail("E_S09_PACKET", "S09B emitted packet must target S10 with S10 stage contract")
    missing_closure_modules = S09B_MATERIAL_CLOSURE_FIELDS - set(packet)
    if missing_closure_modules:
        _fail("E_S09_PACKET", f"S09B emitted packet missing material-closure modules {sorted(missing_closure_modules)}")
    forbidden = set(packet.get("forbidden_routes", [])) if isinstance(packet.get("forbidden_routes"), list) else set()
    required_extra = {"mark_manuscript_complete", "claim_submission_or_publication_readiness", "alter_unrelated_sections", "introduce_new_claims", "strengthen_claims_beyond_s04"}
    missing = required_extra - forbidden
    if missing:
        _fail("E_S09_PACKET", f"S09B emitted packet missing strengthened forbidden routes {sorted(missing)}")
    if packet.get("completion_forbidden") is not True or packet.get("no_recursive_orchestration") is not True:
        _fail("E_S09_PACKET", "S09B emitted packet authority booleans missing")
    if packet.get("allowed_write_paths") != ["examples/candidate-artifacts/phase10_intro_callout_candidate.md"]:
        _fail("E_S09_PACKET", "S09B emitted packet must have exactly one allowed write path")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    by_stage = {item.get("stage_id"): item for item in phase.get("validators", []) if isinstance(item, dict)}
    for sid, required_dimensions, required_checks in (
        ("S09A", S09A_REQUIRED_PHASE10_DIMENSIONS, S09A_REQUIRED_PHASE10_CHECKS),
        ("S09B", S09B_REQUIRED_PHASE10_DIMENSIONS, S09B_REQUIRED_PHASE10_CHECKS),
    ):
        item = by_stage.get(sid)
        if not isinstance(item, dict):
            _fail("E_S09_PHASE10", f"{sid} phase10 validator missing")
        dimensions = {dim.get("dimension_id") for dim in item.get("dimensions", []) if isinstance(dim, dict)}
        missing_dimensions = required_dimensions - dimensions
        if missing_dimensions:
            _fail("E_S09_PHASE10", f"{sid} dimensions missing {sorted(missing_dimensions)}")
        missing_checks = required_checks - set(item.get("required_checks", []))
        if missing_checks:
            _fail("E_S09_PHASE10", f"{sid} checks missing {sorted(missing_checks)}")


def main() -> None:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_s09b_packet()
    _verify_phase10()
    print("PPG_S09_CONTROL_PACKET_ASSEMBLY_OK")


if __name__ == "__main__":
    main()
