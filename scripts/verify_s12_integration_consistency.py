#!/usr/bin/env python3
"""Verify S12 structured integration and consistency report."""

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
PACKET = ROOT / "examples/packets/phase10_s12_integration_consistency_packet.v1.yaml"
MATERIAL = ROOT / "examples/materials/phase10_s12_integration_report.json"
RETURN = ROOT / "examples/candidate_returns/phase10_s12_integration_report_return.json"
PUBLIC_CONSUMES = [
    "candidate text modules",
    "figures/captions",
    "section move plan",
    "terminology register",
    "claim visibility",
]
PUBLIC_PRODUCES = [
    "integrated manuscript candidate",
    "consistency findings",
    "validator report",
]
REQUIRED_SCHEMA = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary",
    "module_inventory",
    "assembly_manifest",
    "integrated_manuscript_candidate",
    "trace_index",
    "claim_boundary_audit",
    "promise_satisfaction_report",
    "cross_section_consistency_report",
    "terminology_consistency_report",
    "object_granularity_consistency_report",
    "figure_text_alignment_report",
    "surface_consistency_report",
    "stale_material_report",
    "integration_findings",
    "backflow_queue",
    "validator_report",
    "candidate_artifact_return",
    "remaining_risks",
}
REQUIRED_PACKET_FIELDS = {
    "s12_input_package",
    "s10_text_candidates",
    "s11_visual_candidates",
    "upstream_control_materials",
    "stale_material_policy",
}
REQUIRED_VALIDATORS = {
    "S12_module_inventory",
    "S12_assembly_manifest",
    "S12_integrated_candidate_package",
    "S12_trace_index",
    "S12_claim_boundary_audit",
    "S12_promise_satisfaction",
    "S12_cross_section_consistency",
    "S12_terminology_consistency",
    "S12_object_granularity_consistency",
    "S12_figure_text_alignment",
    "S12_surface_consistency",
    "S12_stale_material_report",
    "S12_integration_findings",
    "S12_backflow_queue",
    "S12_no_pdf_export",
    "S12_no_final_claim",
    "S12_no_untracked_rewrite",
    "S12_candidate_return_complete",
}
REQUIRED_DIMS = {
    "s12_module_inventory",
    "s12_assembly_manifest",
    "s12_integrated_candidate_package",
    "s12_trace_index",
    "s12_audit_suite",
    "s12_findings_backflow",
    "s12_no_pdf_final_rewrite",
    "s12_candidate_return",
    "s12_nature_overlay",
}
NEGATIVES = {
    "invalid-s12-integration-report-missing-module-inventory.json": "E_S12_MODULE_INVENTORY_REQUIRED",
    "invalid-s12-integration-report-final-pdf-claimed.json": "E_S12_AUTHORITY_BOUNDARY_REQUIRED",
    "invalid-s12-integration-report-ready-for-s16-export.json": "E_S12_NO_PDF_EXPORT",
    "invalid-s12-integration-report-untracked-rewrite.json": "E_S12_AUTHORITY_BOUNDARY_REQUIRED",
    "invalid-s12-integration-report-missing-trace-index.json": "E_S12_TRACE_INDEX_REQUIRED",
    "invalid-s12-integration-report-untraced-claim.json": "E_S12_CLAIM_BOUNDARY_AUDIT_REQUIRED",
    "invalid-s12-integration-report-overpromised.json": "E_S12_PROMISE_SATISFACTION_REQUIRED",
    "invalid-s12-integration-report-cross-section-fail.json": "E_S12_CROSS_SECTION_CONSISTENCY_REQUIRED",
    "invalid-s12-integration-report-stale-recompile.json": "E_S12_STALE_MATERIAL_REPORT_REQUIRED",
    "invalid-s12-integration-report-finding-missing-route.json": "E_S12_INTEGRATION_FINDINGS_REQUIRED",
    "invalid-s12-integration-report-backflow-invalid-stage.json": "E_S12_BACKFLOW_QUEUE_REQUIRED",
    "invalid-s12-integration-report-validator-blocks-s13.json": "E_S12_VALIDATOR_REPORT_REQUIRED",
    "invalid-s12-integration-report-bad-candidate-return.json": "E_S12_CANDIDATE_RETURN_REQUIRED",
    "invalid-s12-integration-report-completion-overclaim.json": "E_S12_NO_COMPLETION_OVERCLAIM",
}


def fail(code: str, msg: str) -> NoReturn:
    print(f"{code}: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def load_doc(p: Path) -> dict[str, Any]:
    data, errors = load_document(p)
    if errors:
        fail("E_S12_DOC_LOAD", f"{p}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        fail("E_S12_DOC_LOAD", f"{p}: root must be mapping")
    return data


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def verify_fixtures() -> None:
    for cmd in (
        [sys.executable, str(VALIDATE_PACKET), str(PACKET)],
        [sys.executable, str(VALIDATE_MATERIAL), str(MATERIAL)],
        [sys.executable, str(VALIDATE_RETURN), str(RETURN), "--packet", str(PACKET)],
    ):
        r = run(cmd)
        if r.returncode != 0:
            fail("E_S12_POSITIVE", f"{' '.join(cmd)}\n{r.stdout}")
    for name, code in NEGATIVES.items():
        p = ROOT / "examples/materials" / name
        r = run([sys.executable, str(VALIDATE_MATERIAL), str(p)])
        if r.returncode == 0 or code not in r.stdout:
            fail("E_S12_NEGATIVE", f"{name} expected {code}, got\n{r.stdout}")


def verify_schema_packet() -> None:
    props = load_json(ROOT / "schemas/ppg-material-payloads.schema.json")["properties"]
    if "S12IntegrationConsistencyReport" not in props:
        fail("E_S12_SCHEMA", "missing S12IntegrationConsistencyReport")
    missing = REQUIRED_SCHEMA - set(
        props["S12IntegrationConsistencyReport"].get("required", [])
    )
    if missing:
        fail("E_S12_SCHEMA", f"missing {sorted(missing)}")
    packet = load_doc(PACKET)
    missing_packet = REQUIRED_PACKET_FIELDS - set(packet)
    if missing_packet:
        fail("E_S12_PACKET", f"missing {sorted(missing_packet)}")
    if packet.get("stage_id") != "S12" or packet.get("agent_type") != "verifier":
        fail("E_S12_PACKET", "must bind S12 verifier")
    material = load_json(MATERIAL)
    payload = material["payload"]
    if payload["integrated_manuscript_candidate"]["ready_for_s16_export"] is not False:
        fail("E_S12_BOUNDARY", "ready_for_s16_export must be false")
    if payload["candidate_artifact_return"] != load_json(RETURN):
        fail("E_S12_RETURN", "embedded return mismatch")


def verify_registry_phase() -> None:
    reg = load_json(ROOT / "runtime/stage_registry.json")
    s12 = {s["stage_id"]: s for s in reg["stages"]}["S12"]
    if s12["consumes"] != PUBLIC_CONSUMES or s12["produces"] != PUBLIC_PRODUCES:
        fail("E_S12_IO", "public IO drift")
    miss = REQUIRED_VALIDATORS - set(s12["validators"])
    if miss:
        fail("E_S12_VALIDATORS", f"missing {sorted(miss)}")
    contract = load_json(ROOT / "examples/stage-contracts/S12.stage-contract.json")
    for k in [
        "consumes",
        "produces",
        "validators",
        "completion_gate",
        "coverage_status",
    ]:
        if contract.get(k) != s12.get(k):
            fail("E_S12_CONTRACT", f"mismatch {k}")
    phase = load_json(ROOT / "runtime/phase10_content_validators.json")
    p = {v["stage_id"]: v for v in phase["validators"]}["S12"]
    dims = {d["dimension_id"] for d in p["dimensions"]}
    missd = REQUIRED_DIMS - dims
    if missd:
        fail("E_S12_PHASE", f"missing dims {sorted(missd)}")
    checks = set(p["required_checks"])
    missc = {c.lower() for c in REQUIRED_VALIDATORS} - checks
    if missc:
        fail("E_S12_PHASE", f"missing checks {sorted(missc)}")


def main() -> int:
    verify_fixtures()
    verify_schema_packet()
    verify_registry_phase()
    print("PPG_S12_INTEGRATION_CONSISTENCY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
