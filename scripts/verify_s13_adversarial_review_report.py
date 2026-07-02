#!/usr/bin/env python3
"""Verify S13 adversarial review/loss-signal report."""
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
VALIDATE_RETURN = ROOT / "scripts" / "validate_candidate_return.py"
PACKET = ROOT / "examples/packets/phase10_s13_adversarial_review_packet.v1.yaml"
MATERIAL = ROOT / "examples/materials/phase10_s13_adversarial_review_report.json"
RETURN = ROOT / "examples/candidate_returns/phase10_s13_adversarial_review_report_return.json"
PUBLIC_CONSUMES = [
    "structured S12 integrated candidate package",
    "S12 trace and validator reports",
    "S10/S11 candidate traces",
    "S04-S08 upstream control materials",
]
PUBLIC_PRODUCES = [
    "adversarial review report",
    "severity-ranked review findings",
    "finding actionability report",
    "validator report",
]
REQUIRED_SCHEMA_FIELDS = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary",
    "review_scope",
    "review_object_inventory",
    "reviewer_panel_report",
    "desk_reject_risk_report",
    "reader_experience_report",
    "claim_evidence_review",
    "contribution_significance_review",
    "method_result_review",
    "figure_caption_review",
    "structure_argument_review",
    "surface_accessibility_review",
    "review_findings",
    "finding_actionability_report",
    "validator_report",
    "candidate_artifact_return",
    "verifier_evidence",
    "remaining_risks",
}
REQUIRED_PACKET_FIELDS = {
    "s13_review_input_package",
    "structured_s12_candidate",
    "reviewer_panel_profile",
    "adversarial_review_protocol",
    "finding_taxonomy",
    "local_backflow_routing_rules",
}
REQUIRED_REGISTRY_VALIDATORS = {
    "S13_review_object_inventory",
    "S13_review_scope",
    "S13_reviewer_panel_report",
    "S13_desk_reject_risk_report",
    "S13_reader_experience_report",
    "S13_claim_evidence_review",
    "S13_figure_caption_review",
    "S13_review_findings_schema",
    "S13_finding_actionability",
    "S13_backflow_target_validity",
    "S13_no_uncontrolled_rewrite",
    "S13_no_pdf_primary_review",
    "S13_candidate_return_complete",
    "S13_verifier_evidence",
}
REQUIRED_DIMS = {
    "s13_review_object_inventory",
    "s13_review_scope",
    "s13_loss_signal_reports",
    "s13_review_findings_schema",
    "s13_actionability_and_routing",
    "s13_no_pdf_rewrite_repair_completion",
    "s13_candidate_return_verifier",
    "s13_nature_overlay",
}
NEGATIVES = {
    "invalid-s13-adversarial-review-missing-object-inventory.json": "E_S13_REVIEW_OBJECT_INVENTORY_REQUIRED",
    "invalid-s13-adversarial-review-pdf-primary.json": "E_S13_NO_PDF_PRIMARY_REVIEW",
    "invalid-s13-adversarial-review-pdf-reviewed.json": "E_S13_AUTHORITY_BOUNDARY_REQUIRED",
    "invalid-s13-adversarial-review-rewrite-performed.json": "E_S13_AUTHORITY_BOUNDARY_REQUIRED",
    "invalid-s13-adversarial-review-missing-review-mode.json": "E_S13_REVIEW_SCOPE_REQUIRED",
    "invalid-s13-adversarial-review-missing-reviewer-role.json": "E_S13_REVIEWER_PANEL_REQUIRED",
    "invalid-s13-adversarial-review-finding-missing-evidence.json": "E_S13_REVIEW_FINDINGS_REQUIRED",
    "invalid-s13-adversarial-review-finding-missing-location.json": "E_S13_REVIEW_FINDINGS_REQUIRED",
    "invalid-s13-adversarial-review-invalid-severity.json": "E_S13_REVIEW_FINDINGS_REQUIRED",
    "invalid-s13-adversarial-review-invalid-nearest-stage.json": "E_S13_REVIEW_FINDINGS_REQUIRED",
    "invalid-s13-adversarial-review-bypasses-s14.json": "E_S13_BACKFLOW_TARGET_REQUIRED",
    "invalid-s13-adversarial-review-uncontrolled-rewrite-scope.json": "E_S13_NO_UNCONTROLLED_REWRITE",
    "invalid-s13-adversarial-review-actionability-missing-ready.json": "E_S13_ACTIONABILITY_REQUIRED",
    "invalid-s13-adversarial-review-bad-candidate-return.json": "E_S13_CANDIDATE_RETURN_REQUIRED",
    "invalid-s13-adversarial-review-missing-verifier-check.json": "E_S13_VERIFIER_EVIDENCE_REQUIRED",
    "invalid-s13-adversarial-review-completion-overclaim.json": "E_S13_NO_COMPLETION_OVERCLAIM",
}


def fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_doc(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        fail("E_S13_DOC_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        fail("E_S13_DOC_LOAD", f"{path}: root must be mapping")
    return data


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def verify_fixtures() -> None:
    for cmd in (
        [sys.executable, str(VALIDATE_PACKET), str(PACKET)],
        [sys.executable, str(VALIDATE_MATERIAL), str(MATERIAL)],
        [sys.executable, str(VALIDATE_RETURN), str(RETURN), "--packet", str(PACKET)],
    ):
        result = run(cmd)
        if result.returncode != 0:
            fail("E_S13_POSITIVE", f"{' '.join(cmd)}\n{result.stdout}")
    for name, expected_code in NEGATIVES.items():
        path = ROOT / "examples/materials" / name
        result = run([sys.executable, str(VALIDATE_MATERIAL), str(path)])
        if result.returncode == 0 or expected_code not in result.stdout:
            fail("E_S13_NEGATIVE", f"{name} expected {expected_code}, got\n{result.stdout}")


def verify_schema_packet_material() -> None:
    props = load_json(ROOT / "schemas/ppg-material-payloads.schema.json")["properties"]
    if "S13AdversarialReviewReport" not in props:
        fail("E_S13_SCHEMA", "missing S13AdversarialReviewReport")
    missing = REQUIRED_SCHEMA_FIELDS - set(props["S13AdversarialReviewReport"].get("required", []))
    if missing:
        fail("E_S13_SCHEMA", f"missing {sorted(missing)}")
    task_props = load_json(ROOT / "schemas/ppg-task-packet.schema.json").get("properties", {})
    missing_packet_schema = REQUIRED_PACKET_FIELDS - set(task_props)
    if missing_packet_schema:
        fail("E_S13_PACKET_SCHEMA", f"task schema missing {sorted(missing_packet_schema)}")
    packet = load_doc(PACKET)
    missing_packet = REQUIRED_PACKET_FIELDS - set(packet)
    if missing_packet:
        fail("E_S13_PACKET", f"packet missing {sorted(missing_packet)}")
    if packet.get("stage_id") != "S13" or packet.get("agent_type") != "critic":
        fail("E_S13_PACKET", "must bind S13 critic")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s13_adversarial_review_report.json"]:
        fail("E_S13_PACKET", "S13 packet must write exactly the S13 report material")
    material = load_json(MATERIAL)
    payload = material["payload"]
    if payload["candidate_artifact_return"] != load_json(RETURN):
        fail("E_S13_RETURN", "embedded return mismatch")
    if payload["review_object_inventory"].get("primary_object_is_pdf") is not False:
        fail("E_S13_PDF_BOUNDARY", "primary object must not be PDF")
    for finding in payload.get("review_findings", []):
        if finding.get("recommended_backflow_target") != "S14":
            fail("E_S13_ROUTING", "all findings must route through S14")
        if finding.get("repair_executed") is not False or finding.get("rewrite_requested") is not False:
            fail("E_S13_BOUNDARY", "S13 must not execute repair or request rewrite")


def verify_registry_phase() -> None:
    registry = load_json(ROOT / "runtime/stage_registry.json")
    s13 = {s["stage_id"]: s for s in registry["stages"]}["S13"]
    if s13["consumes"] != PUBLIC_CONSUMES or s13["produces"] != PUBLIC_PRODUCES:
        fail("E_S13_IO", "public IO drift")
    missing_validators = REQUIRED_REGISTRY_VALIDATORS - set(s13.get("validators", []))
    if missing_validators:
        fail("E_S13_VALIDATORS", f"missing {sorted(missing_validators)}")
    contract = load_json(ROOT / "examples/stage-contracts/S13.stage-contract.json")
    for key in ["consumes", "produces", "validators", "completion_gate", "coverage_status"]:
        if contract.get(key) != s13.get(key):
            fail("E_S13_CONTRACT", f"mismatch {key}")
    phase = load_json(ROOT / "runtime/phase10_content_validators.json")
    validator = {v["stage_id"]: v for v in phase["validators"]}["S13"]
    dims = {d["dimension_id"] for d in validator["dimensions"]}
    missing_dims = REQUIRED_DIMS - dims
    if missing_dims:
        fail("E_S13_PHASE", f"missing dims {sorted(missing_dims)}")
    checks = set(validator["required_checks"])
    missing_checks = {item.lower() for item in REQUIRED_REGISTRY_VALIDATORS} - checks
    if missing_checks:
        fail("E_S13_PHASE", f"missing checks {sorted(missing_checks)}")


def main() -> int:
    verify_fixtures()
    verify_schema_packet_material()
    verify_registry_phase()
    print("PPG_S13_ADVERSARIAL_REVIEW_REPORT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
