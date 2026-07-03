#!/usr/bin/env python3
"""Verify S10 packet-bounded candidate text production contract and fixtures."""
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
VALIDATE_SECTION = ROOT / "scripts" / "validate_section_draft.py"
VALIDATE_RETURN = ROOT / "scripts" / "validate_candidate_return.py"
S10_PACKET = ROOT / "examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml"
S10_DRAFT = ROOT / "examples/candidate-artifacts/phase10_intro_callout_candidate.md"
S10_RETURN = ROOT / "examples/candidate_returns/phase10_intro_callout_candidate_return.json"
S10_MATERIAL = ROOT / "examples/materials/phase10_s10_candidate_text_return.json"
PUBLIC_CONSUMES = ["S09B task packet", "S09B material read obligations", "construction matrix", "terminology register", "claim visibility"]
PUBLIC_PRODUCES = ["candidate text unit", "material hydration report", "material read receipt ledger", "CandidateArtifactReturn"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S10_packet_compliance",
    "S10_candidate_text_schema",
    "S10_allowed_write_path",
    "S10_material_hydration_report",
    "S10_material_read_receipt_ledger",
    "S10_blocked_output_on_missing_material",
    "S10_claim_evidence_trace",
    "S10_claim_boundary_preserved",
    "S10_no_new_claims",
    "S10_no_claim_strengthening",
    "S10_move_trace",
    "S10_terminology_trace",
    "S10_internal_id_leakage",
    "S10_object_granularity_trace",
    "S10_visual_callout_trace",
    "S10_forbidden_expression_scan",
    "S10_coverage_ledger",
    "S10_candidate_return_complete",
    "S10_writer_evidence",
    "S10_verifier_evidence",
    "S10_authority_boundary",
}
REQUIRED_SCHEMA_FIELDS = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary",
    "packet_compliance_report",
    "material_hydration_report",
    "material_read_receipt_ledger",
    "candidate_text_unit",
    "section_or_unit_skeleton",
    "move_trace",
    "claim_evidence_trace",
    "terminology_trace",
    "object_granularity_trace",
    "visual_callout_trace",
    "forbidden_expression_scan",
    "coverage_ledger",
    "candidate_artifact_return",
    "writer_execution_evidence",
    "verifier_evidence",
    "remaining_risks",
    "missing_material_report",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s10_packet_compliance",
    "s10_material_hydration_and_read_receipts",
    "s10_candidate_text_unit",
    "s10_claim_evidence_trace",
    "s10_move_trace",
    "s10_terminology_object_visual_trace",
    "s10_forbidden_expression_scan",
    "s10_coverage_ledger",
    "s10_candidate_return_and_double_lane",
    "s10_nature_overlay",
}
REQUIRED_PHASE10_CHECKS = {
    "s10_packet_compliance",
    "s10_candidate_text_schema",
    "s10_allowed_write_path",
    "s10_material_hydration_report",
    "s10_material_read_receipt_ledger",
    "s10_blocked_output_on_missing_material",
    "s10_claim_evidence_trace",
    "s10_claim_boundary_preserved",
    "s10_no_new_claims",
    "s10_no_claim_strengthening",
    "s10_move_trace",
    "s10_terminology_trace",
    "s10_internal_id_leakage",
    "s10_object_granularity_trace",
    "s10_visual_callout_trace",
    "s10_forbidden_expression_scan",
    "s10_coverage_ledger",
    "s10_candidate_return_complete",
    "s10_writer_evidence",
    "s10_verifier_evidence",
    "s10_authority_boundary",
}
REQUIRED_PACKET_FIELDS = {
    "hard_constraints",
    "local_context",
    "adjacent_context",
    "background_context_usage",
    "negative_controls",
    "section_or_unit_move_plan",
    "claim_boundary_controls",
    "object_granularity_controls",
    "terminology_surface_controls",
    "visual_formal_controls",
    "single_writer_lock",
    "packet_authority_boundary",
}
REQUIRED_FORBIDDEN_ROUTES = {
    "mark_graph_complete",
    "mark_manuscript_complete",
    "claim_submission_or_publication_readiness",
    "dispatch_subagents",
    "write_outside_allowed_write_paths",
    "change_owner_intent",
    "alter_unrelated_sections",
    "introduce_new_claims",
    "strengthen_claims_beyond_s04",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s10-candidate-text-return-missing-packet-compliance.json": "E_S10_PACKET_COMPLIANCE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-unsafe-write-path.json": "E_S10_ALLOWED_WRITE_PATH_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-completion-overclaim.json": "E_S10_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-forbidden-body.json": "E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-missing-claim-trace.json": "E_S10_CLAIM_EVIDENCE_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-internal-id-leakage.json": "E_S10_TERMINOLOGY_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-object-granularity.json": "E_S10_OBJECT_GRANULARITY_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-visual-misuse.json": "E_S10_VISUAL_CALLOUT_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-scan-not-clean.json": "E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-unresolved-coverage.json": "E_S10_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-bad-candidate-return.json": "E_S10_CANDIDATE_RETURN_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-missing-writer-evidence.json": "E_S10_WRITER_EVIDENCE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-missing-verifier-evidence.json": "E_S10_VERIFIER_EVIDENCE_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-blocked-missing-material.json": "E_S10_MISSING_MATERIAL_REPORT_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-final-acceptance.json": "E_S10_NO_FINAL_ACCEPTANCE",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-missing-material-hydration.json": "E_S10_MATERIAL_HYDRATION_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-missing-read-receipts.json": "E_S10_MATERIAL_READ_RECEIPT_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-candidate-output-with-missing-material.json": "E_S10_BLOCKED_OUTPUT_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-unread-required-selector.json": "E_S10_MATERIAL_READ_RECEIPT_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-underdeclared-material.json": "E_S10_MATERIAL_HYDRATION_REQUIRED",
    ROOT / "examples/materials/invalid-s10-candidate-text-return-underdeclared-selector.json": "E_S10_MATERIAL_HYDRATION_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S10_JSON_LOAD", f"{path}: {exc}")


def _load_doc(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S10_DOC_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S10_DOC_LOAD", f"{path}: root must be a mapping")
    return data


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _validate_material_cmd(path: Path) -> list[str]:
    return [sys.executable, str(VALIDATE_MATERIAL), str(path), "--packet", str(S10_PACKET)]


def _verify_positive_and_negative_fixtures() -> None:
    positive_commands = [
        [sys.executable, str(VALIDATE_PACKET), str(S10_PACKET)],
        [sys.executable, str(VALIDATE_SECTION), str(S10_DRAFT)],
        [sys.executable, str(VALIDATE_RETURN), str(S10_RETURN), "--packet", str(S10_PACKET)],
        _validate_material_cmd(S10_MATERIAL),
    ]
    for cmd in positive_commands:
        result = _run(cmd)
        if result.returncode != 0:
            _fail("E_S10_POSITIVE_FIXTURE", f"positive fixture failed: {' '.join(cmd)}\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(_validate_material_cmd(path))
        if result.returncode == 0:
            _fail("E_S10_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S10_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema_and_packet() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict) or "S10CandidateTextReturn" not in props:
        _fail("E_S10_SCHEMA", "S10CandidateTextReturn schema property missing")
    s10 = props["S10CandidateTextReturn"]
    required = set(s10.get("required", []))
    missing = sorted(REQUIRED_SCHEMA_FIELDS - required)
    if missing:
        _fail("E_S10_SCHEMA", f"S10CandidateTextReturn schema missing {missing}")
    packet_schema = _load_json(ROOT / "schemas/ppg-task-packet.schema.json")
    packet_props = packet_schema.get("properties", {})
    missing_packet_schema = sorted(REQUIRED_PACKET_FIELDS - set(packet_props))
    if missing_packet_schema:
        _fail("E_S10_PACKET_SCHEMA", f"ppg-task-packet schema missing S10 packet fields {missing_packet_schema}")

    packet = _load_doc(S10_PACKET)
    missing_packet_fields = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing_packet_fields:
        _fail("E_S10_PACKET_FIELDS", f"S10 packet missing {missing_packet_fields}")
    forbidden_routes = set(packet.get("forbidden_routes", []))
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_ROUTES - forbidden_routes)
    if missing_forbidden:
        _fail("E_S10_PACKET_FORBIDDEN_ROUTES", f"S10 packet forbidden_routes missing {missing_forbidden}")
    if packet.get("stage_id") != "S10" or packet.get("agent_type") != "writer":
        _fail("E_S10_PACKET_BINDING", "S10 packet must bind stage_id S10 and writer agent")
    if packet.get("allowed_write_paths") != ["examples/candidate-artifacts/phase10_intro_callout_candidate.md"]:
        _fail("E_S10_PACKET_WRITE_PATH", "S10 packet must have exactly one candidate-artifact write path")


def _verify_registry_contract_phase10() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    stages = {stage.get("stage_id"): stage for stage in registry.get("stages", []) if isinstance(stage, dict)}
    s10 = stages.get("S10")
    if not isinstance(s10, dict):
        _fail("E_S10_REGISTRY", "S10 registry stage missing")
    if s10.get("consumes") != PUBLIC_CONSUMES or s10.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S10_REGISTRY_IO", "S10 public graph I/O drifted")
    if s10.get("requires_worker_task_packet") is not True or s10.get("recommended_agent_type") != "writer":
        _fail("E_S10_REGISTRY", "S10 must require worker packet and writer producer")
    lane = s10.get("subagent_lane_policy")
    if not isinstance(lane, dict) or lane.get("policy") != "mandatory_double" or lane.get("verifier_agent_type") != "verifier":
        _fail("E_S10_REGISTRY", "S10 must keep mandatory writer/verifier double lane")
    missing_validators = sorted(REQUIRED_REGISTRY_VALIDATORS - set(s10.get("validators", [])))
    if missing_validators:
        _fail("E_S10_REGISTRY_VALIDATORS", f"S10 registry validators missing {missing_validators}")

    contract = _load_json(ROOT / "examples/stage-contracts/S10.stage-contract.json")
    for key in ("consumes", "produces", "validators", "completion_gate", "coverage_status", "subagent_lane_policy"):
        if contract.get(key) != s10.get(key):
            _fail("E_S10_CONTRACT", f"S10 contract/registry mismatch on {key}")
    coverage = contract.get("worker_packet_coverage")
    if not isinstance(coverage, dict) or coverage.get("packet_ref") != "examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml":
        _fail("E_S10_CONTRACT_PACKET", "S10 contract must link the strict S09B packet")

    phase10 = _load_json(ROOT / "runtime/phase10_content_validators.json")
    validators = {validator.get("stage_id"): validator for validator in phase10.get("validators", []) if isinstance(validator, dict)}
    phase_s10 = validators.get("S10")
    if not isinstance(phase_s10, dict):
        _fail("E_S10_PHASE10", "S10 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in phase_s10.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = sorted(REQUIRED_PHASE10_DIMENSIONS - dimensions)
    if missing_dimensions:
        _fail("E_S10_PHASE10_DIMENSIONS", f"S10 phase10 dimensions missing {missing_dimensions}")
    checks = set(phase_s10.get("required_checks", []))
    missing_checks = sorted(REQUIRED_PHASE10_CHECKS - checks)
    if missing_checks:
        _fail("E_S10_PHASE10_CHECKS", f"S10 phase10 checks missing {missing_checks}")


def _verify_material_cross_refs() -> None:
    material = _load_json(S10_MATERIAL)
    payload = material.get("payload", {})
    candidate_return = _load_json(S10_RETURN)
    if payload.get("candidate_artifact_return") != candidate_return:
        _fail("E_S10_RETURN_EMBED", "embedded CandidateArtifactReturn must match fixture")
    hydration = payload.get("material_hydration_report", {})
    receipts = payload.get("material_read_receipt_ledger", {})
    required_materials = set(hydration.get("required_materials", []))
    hydrated_materials = set(hydration.get("hydrated_materials", []))
    if not required_materials or required_materials != hydrated_materials or hydration.get("missing_materials") != []:
        _fail("E_S10_MATERIAL_HYDRATION", "S10 material hydration report must close every required material")
    receipt_materials = {receipt.get("material_ref") for receipt in receipts.get("receipts", []) if isinstance(receipt, dict)}
    if required_materials != receipt_materials or receipts.get("missing_receipts") != []:
        _fail("E_S10_MATERIAL_READ_RECEIPTS", "S10 read receipt ledger must cover every required material")
    if payload.get("candidate_text_unit", {}).get("output_artifact_path") != "examples/candidate-artifacts/phase10_intro_callout_candidate.md":
        _fail("E_S10_CANDIDATE_PATH", "candidate text unit path mismatch")
    if payload.get("verifier_evidence", {}).get("verification_status") not in {"pass", "pass_with_risks"}:
        _fail("E_S10_VERIFIER", "verifier evidence status must be pass/pass_with_risks")


def main() -> int:
    _verify_positive_and_negative_fixtures()
    _verify_schema_and_packet()
    _verify_registry_contract_phase10()
    _verify_material_cross_refs()
    print("PPG_S10_CANDIDATE_TEXT_RETURN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
