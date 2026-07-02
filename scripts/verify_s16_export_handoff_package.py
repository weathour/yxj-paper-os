#!/usr/bin/env python3
"""Verify S16 export/repository-hygiene/handoff package."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_MATERIAL = ROOT / "scripts" / "validate_material.py"
VERIFY_LIVE = ROOT / "scripts" / "verify_s16_live_export_evidence.py"
MATERIAL = ROOT / "examples/materials/phase10_s16_export_handoff_package.json"
COMPILED_MATERIAL = ROOT / "examples/materials/phase10_s16_compiled_initial_draft_package.json"
LIVE_COMPILED_MATERIAL = ROOT / "examples/materials/phase10_s16_compiled_live_export_package.json"
LIVE_TEMPLATE_TEXT_NEGATIVE = ROOT / "examples/materials/invalid-s16-live-export-template-pdf-text.json"
PUBLIC_CONSUMES = [
    "closed S12 integrated manuscript candidate",
    "S13 review closure evidence",
    "S14/S15 repair-complete status",
    "figures/captions/data availability bundle",
    "repository and build configuration state",
]
PUBLIC_PRODUCES = [
    "export handoff package",
    "human-readable PDF/export manifest",
    "repository hygiene report",
    "manager/owner handoff report",
]
REQUIRED_SCHEMA_FIELDS = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary",
    "evidence_mode",
    "live_export_verification",
    "delivery_target",
    "readiness_state_separation",
    "upstream_closure_check",
    "build_readiness_check",
    "build_run_report",
    "rendered_surface_check",
    "export_manifest",
    "file_hash_manifest",
    "figure_file_checklist",
    "data_availability_statement_check",
    "supplement_manifest",
    "repository_hygiene_report",
    "manager_handoff_report",
    "owner_gate_report",
    "human_feedback_intake_route",
    "validator_report",
    "remaining_risks",
}
REQUIRED_REGISTRY_VALIDATORS = {
    "S16_upstream_closure",
    "S16_readiness_state_separation",
    "S16_build_success",
    "S16_pdf_exists_and_surface",
    "S16_figures_captions_present",
    "S16_references_present",
    "S16_data_availability_alignment",
    "S16_export_manifest_hashes",
    "S16_dirty_worktree_classification",
    "S16_handoff_completeness",
    "S16_feedback_route_declared",
    "S16_projection_vs_live_export_boundary",
    "S16_delivery_target_declared",
    "S16_delivery_target_binding",
    "S16_compiled_pdf_target_gate",
    "S16_pdf_semantic_surface",
    "S16_template_only_handoff_boundary",
    "S16_no_submission_ready_overclaim",
}
REQUIRED_DIMS = {
    "s16_upstream_closure",
    "s16_readiness_state_separation",
    "s16_build_success",
    "s16_rendered_surface",
    "s16_manifest_hashes",
    "s16_repository_hygiene",
    "s16_handoff_and_feedback_route",
    "s16_projection_vs_live_export_boundary",
    "s16_delivery_target",
    "s16_target_binding",
    "s16_compiled_pdf_target_gate",
    "s16_pdf_semantic_surface",
    "s16_template_only_handoff_boundary",
    "s16_no_submission_publication_overclaim",
    "s16_nature_overlay",
}
NEGATIVES = {
    "invalid-s16-export-handoff-active-target-downcast.json": "E_S16_DELIVERY_TARGET_BINDING",
    "invalid-s16-export-handoff-compiled-target-missing-semantic-surface.json": "E_S16_PDF_SEMANTIC_SURFACE",
    "invalid-s16-export-handoff-compiled-target-missing-source-writeback.json": "E_S16_SOURCE_WRITEBACK_REQUIRED",
    "invalid-s16-export-handoff-compiled-target-template-only.json": "E_S16_PDF_SEMANTIC_SURFACE",
    "invalid-s16-export-handoff-compiled-target-content-blocked.json": "E_S16_COMPILED_TARGET_GATE",
    "invalid-s16-export-handoff-missing-delivery-target.json": "E_S16_DELIVERY_TARGET_REQUIRED",
    "invalid-s16-export-handoff-bad-readiness.json": "E_S16_READINESS_STATE_REQUIRED",
    "invalid-s16-export-handoff-unresolved-upstream.json": "E_S16_UPSTREAM_CLOSURE_REQUIRED",
    "invalid-s16-export-handoff-build-failed.json": "E_S16_BUILD_SUCCESS_REQUIRED",
    "invalid-s16-export-handoff-render-anomaly.json": "E_S16_RENDERED_SURFACE_REQUIRED",
    "invalid-s16-export-handoff-missing-hash.json": "E_S16_HASH_MANIFEST_REQUIRED",
    "invalid-s16-export-handoff-missing-handoff-manifest-entry.json": "E_S16_EXPORT_MANIFEST_REQUIRED",
    "invalid-s16-export-handoff-hash-mismatch.json": "E_S16_HASH_MANIFEST_REQUIRED",
    "invalid-s16-export-handoff-figure-failed.json": "E_S16_FIGURE_CAPTION_CHECK_REQUIRED",
    "invalid-s16-export-handoff-data-mismatch.json": "E_S16_DATA_AVAILABILITY_REQUIRED",
    "invalid-s16-export-handoff-unexpected-dirty.json": "E_S16_REPOSITORY_HYGIENE_REQUIRED",
    "invalid-s16-export-handoff-feedback-misrouted.json": "E_S16_FEEDBACK_ROUTE_REQUIRED",
    "invalid-s16-export-handoff-owner-authorized.json": "E_S16_OWNER_GATE_REQUIRED",
    "invalid-s16-export-handoff-submission-overclaim.json": "E_S16_NO_SUBMISSION_PUBLICATION_OVERCLAIM",
    "invalid-s16-export-handoff-narrative-overclaim.json": "E_S16_NO_SUBMISSION_PUBLICATION_OVERCLAIM",
    "invalid-s16-export-handoff-unrelated-negation-overclaim.json": "E_S16_NO_SUBMISSION_PUBLICATION_OVERCLAIM",
    "invalid-s16-export-handoff-negated-first-repeat-overclaim.json": "E_S16_NO_SUBMISSION_PUBLICATION_OVERCLAIM",
    "invalid-s16-export-handoff-authority-submitted.json": "E_S16_AUTHORITY_BOUNDARY_REQUIRED",
    "invalid-s16-export-handoff-live-claimed-in-fixture.json": "E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED",
    "invalid-s16-export-handoff-missing-verifier-check.json": "E_S16_VALIDATOR_REPORT_REQUIRED",
    "invalid-s16-export-handoff-missing-human-output.json": "E_S16_HANDOFF_COMPLETENESS_REQUIRED",
    "invalid-s16-export-handoff-unsafe-export-path.json": "E_S16_EXPORT_MANIFEST_REQUIRED",
}


def fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def verify_fixtures() -> None:
    result = run([sys.executable, str(VALIDATE_MATERIAL), str(MATERIAL)])
    if result.returncode != 0:
        fail("E_S16_POSITIVE", result.stdout)
    compiled_result = run([sys.executable, str(VALIDATE_MATERIAL), str(COMPILED_MATERIAL)])
    if compiled_result.returncode != 0:
        fail("E_S16_COMPILED_POSITIVE", compiled_result.stdout)
    result = run([sys.executable, str(VERIFY_LIVE), str(MATERIAL)])
    if result.returncode != 0 or "PPG_S16_LIVE_EXPORT_EVIDENCE_PROJECTION_OK" not in result.stdout:
        fail("E_S16_LIVE_PROJECTION", result.stdout)
    live_result = run([sys.executable, str(VERIFY_LIVE), str(LIVE_COMPILED_MATERIAL)])
    if live_result.returncode != 0 or "PPG_S16_LIVE_EXPORT_EVIDENCE_OK" not in live_result.stdout:
        fail("E_S16_LIVE_COMPILED", live_result.stdout)
    bad_live = run([sys.executable, str(VERIFY_LIVE), str(LIVE_TEMPLATE_TEXT_NEGATIVE)])
    if bad_live.returncode == 0 or "E_S16_LIVE_TEXT" not in bad_live.stdout:
        fail("E_S16_LIVE_TEMPLATE_TEXT_NEGATIVE", bad_live.stdout)
    for name, expected_code in NEGATIVES.items():
        result = run([sys.executable, str(VALIDATE_MATERIAL), str(ROOT / "examples/materials" / name)])
        if result.returncode == 0 or expected_code not in result.stdout:
            fail("E_S16_NEGATIVE", f"{name} expected {expected_code}, got\n{result.stdout}")


def verify_schema_material() -> None:
    props = load_json(ROOT / "schemas/ppg-material-payloads.schema.json")["properties"]
    if "S16ExportHandoffPackage" not in props:
        fail("E_S16_SCHEMA", "missing S16ExportHandoffPackage")
    missing = REQUIRED_SCHEMA_FIELDS - set(props["S16ExportHandoffPackage"].get("required", []))
    if missing:
        fail("E_S16_SCHEMA", f"missing {sorted(missing)}")
    material = load_json(MATERIAL)
    payload = material["payload"]
    if payload["authority_boundary"].get("external_submission_performed") is not False:
        fail("E_S16_AUTHORITY", "S16 must not perform external submission")
    if payload["owner_gate_report"].get("external_submission_authorized") is not False:
        fail("E_S16_OWNER_GATE", "S16 owner gate must remain false")
    if payload["readiness_state_separation"].get("submission_gated") is not True:
        fail("E_S16_READINESS", "submission_gated must be true")
    if payload["evidence_mode"].get("mode") != "fixture_projection":
        fail("E_S16_EVIDENCE_MODE", "contract fixture must be fixture_projection")
    if payload["live_export_verification"].get("physical_export_claimed") is not False:
        fail("E_S16_LIVE_EXPORT", "fixture must not claim physical live export")
    exported = {item["path"]: item["sha256"] for item in payload["export_manifest"]["exported_files"]}
    hashed = {item["path"]: item["sha256"] for item in payload["file_hash_manifest"]}
    if set(exported) - set(hashed):
        fail("E_S16_HASHES", f"missing hashes for {sorted(set(exported) - set(hashed))}")
    mismatch = sorted(path for path in exported if exported.get(path) != hashed.get(path))
    if mismatch:
        fail("E_S16_HASHES", f"hash mismatch for {mismatch}")
    if payload["human_feedback_intake_route"].get("if_content_feedback") != "route_to_S14":
        fail("E_S16_FEEDBACK_ROUTE", "content feedback must route to S14")
    clean_export = json.loads(json.dumps(material))
    clean_export["payload"]["repository_hygiene_report"]["dirty_worktree_classification"]["source_changes"] = []
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(clean_export, handle)
        temp_path = Path(handle.name)
    try:
        result = run([sys.executable, str(VALIDATE_MATERIAL), str(temp_path)])
        if result.returncode != 0:
            fail("E_S16_CLEAN_EXPORT_SOURCE_CHANGES", result.stdout)
    finally:
        temp_path.unlink(missing_ok=True)


def verify_registry_phase() -> None:
    registry = load_json(ROOT / "runtime/stage_registry.json")
    s16 = {s["stage_id"]: s for s in registry["stages"]}["S16"]
    if s16["requires_worker_task_packet"] is not False:
        fail("E_S16_WORKER_PACKET", "S16 must remain controller-owned/no-worker-packet")
    if s16["consumes"] != PUBLIC_CONSUMES or s16["produces"] != PUBLIC_PRODUCES:
        fail("E_S16_IO", "public IO drift")
    missing_validators = REQUIRED_REGISTRY_VALIDATORS - set(s16.get("validators", []))
    if missing_validators:
        fail("E_S16_VALIDATORS", f"missing {sorted(missing_validators)}")
    contract = load_json(ROOT / "examples/stage-contracts/S16.stage-contract.json")
    for key in ["consumes", "produces", "validators", "completion_gate", "coverage_status", "requires_worker_task_packet"]:
        if contract.get(key) != s16.get(key):
            fail("E_S16_CONTRACT", f"mismatch {key}")
    if contract.get("worker_packet_coverage", {}).get("status") != "not_required":
        fail("E_S16_CONTRACT", "S16 contract must not link a fake worker packet")
    phase = load_json(ROOT / "runtime/phase10_content_validators.json")
    validator = {v["stage_id"]: v for v in phase["validators"]}["S16"]
    dims = {d["dimension_id"] for d in validator["dimensions"]}
    missing_dims = REQUIRED_DIMS - dims
    if missing_dims:
        fail("E_S16_PHASE", f"missing dims {sorted(missing_dims)}")
    checks = set(validator["required_checks"])
    missing_checks = {item.lower() for item in REQUIRED_REGISTRY_VALIDATORS} - checks
    if missing_checks:
        fail("E_S16_PHASE", f"missing checks {sorted(missing_checks)}")


def main() -> int:
    verify_fixtures()
    verify_schema_material()
    verify_registry_phase()
    print("PPG_S16_EXPORT_HANDOFF_PACKAGE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
