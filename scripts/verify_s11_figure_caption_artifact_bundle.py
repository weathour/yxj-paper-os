#!/usr/bin/env python3
"""Verify S11 contract-bound visual/formal artifact production."""
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
S11_PACKET = ROOT / "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml"
S11_RETURN = ROOT / "examples/candidate_returns/phase10_s11_figure_caption_bundle_return.json"
S11_MATERIAL = ROOT / "examples/materials/phase10_s11_figure_caption_artifact_bundle.json"
S11_ARTIFACT = ROOT / "examples/candidate-artifacts/phase10_s11_figure_caption_bundle.md"
PUBLIC_CONSUMES = ["figure contracts", "panel evidence packages", "source data locators", "caption brief"]
PUBLIC_PRODUCES = ["figure statistics", "image integrity record", "caption brief", "figure export bundle"]
REQUIRED_PACKET_FIELDS = {
    "authority_and_target",
    "s08_visual_formal_contract",
    "panel_evidence_package",
    "claim_boundary_controls",
    "source_data_package",
    "terminology_and_surface_controls",
    "visual_quality_profile",
    "visual_polish_policy",
}
REQUIRED_SCHEMA_FIELDS = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary",
    "packet_compliance_report",
    "figure_contract_compliance",
    "generated_artifacts",
    "editable_source_bundle",
    "source_data_trace",
    "panel_claim_trace",
    "caption_legend_draft",
    "caption_claim_trace",
    "image_integrity_record",
    "visual_polish_policy",
    "visual_polish_report",
    "figure_statistics",
    "accessibility_check",
    "export_manifest",
    "coverage_ledger",
    "candidate_artifact_return",
    "verifier_evidence",
    "remaining_risks",
    "missing_material_report",
}
REQUIRED_REGISTRY_VALIDATORS = {
    "S11_packet_compliance",
    "S11_figure_contract_compliance",
    "S11_source_data_provenance",
    "S11_panel_claim_trace",
    "S11_caption_claim_boundary",
    "S11_explanatory_vs_evidential_boundary",
    "S11_editable_source_present",
    "S11_render_or_render_plan_present",
    "S11_image_integrity_record",
    "S11_visual_polish_policy",
    "S11_visual_polish_report",
    "S11_accessibility_check",
    "S11_export_manifest",
    "S11_candidate_return_complete",
    "S11_verifier_evidence",
    "S11_authority_boundary",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s11_packet_compliance",
    "s11_figure_contract_compliance",
    "s11_source_data_provenance",
    "s11_panel_and_caption_claim_trace",
    "s11_render_integrity",
    "s11_visual_polish",
    "s11_accessibility",
    "s11_candidate_return",
    "s11_nature_overlay",
}
REQUIRED_PHASE10_CHECKS = {
    "s11_packet_compliance",
    "s11_figure_contract_compliance",
    "s11_source_data_provenance",
    "s11_panel_claim_trace",
    "s11_caption_claim_boundary",
    "s11_explanatory_vs_evidential_boundary",
    "s11_editable_source_present",
    "s11_render_or_render_plan_present",
    "s11_image_integrity_record",
    "s11_visual_polish_policy",
    "s11_visual_polish_report",
    "s11_accessibility_check",
    "s11_export_manifest",
    "s11_candidate_return_complete",
    "s11_verifier_evidence",
    "s11_authority_boundary",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-missing-contract.json": "E_S11_FIGURE_CONTRACT_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-proof-role-changed.json": "E_S11_FIGURE_CONTRACT_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-unsafe-path.json": "E_S11_ALLOWED_WRITE_PATH_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-missing-render-plan.json": "E_S11_RENDER_OR_PLAN_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-missing-source-trace.json": "E_S11_SOURCE_DATA_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-missing-panel-trace.json": "E_S11_PANEL_CLAIM_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-caption-claim-violation.json": "E_S11_CAPTION_CLAIM_TRACE_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-polish-meaning-change.json": "E_S11_VISUAL_POLISH_REPORT_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-polish-policy-gap.json": "E_S11_VISUAL_POLISH_POLICY_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-accessibility-fail.json": "E_S11_ACCESSIBILITY_CHECK_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-final-export-claimed.json": "E_S11_EXPORT_MANIFEST_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-unresolved-coverage.json": "E_S11_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-bad-candidate-return.json": "E_S11_CANDIDATE_RETURN_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-missing-verifier-evidence.json": "E_S11_VERIFIER_EVIDENCE_REQUIRED",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-completion-overclaim.json": "E_S11_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s11-figure-caption-artifact-blocked-missing-material.json": "E_S11_MISSING_MATERIAL_REPORT_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        _fail("E_S11_JSON_LOAD", f"{path}: {exc}")


def _load_doc(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S11_DOC_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S11_DOC_LOAD", f"{path}: root must be a mapping")
    return data


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _verify_fixtures() -> None:
    for cmd in (
        [sys.executable, str(VALIDATE_PACKET), str(S11_PACKET)],
        [sys.executable, str(VALIDATE_RETURN), str(S11_RETURN), "--packet", str(S11_PACKET)],
        [sys.executable, str(VALIDATE_MATERIAL), str(S11_MATERIAL)],
    ):
        result = _run(cmd)
        if result.returncode != 0:
            _fail("E_S11_POSITIVE_FIXTURE", f"positive fixture failed: {' '.join(cmd)}\n{result.stdout}")
    if not S11_ARTIFACT.is_file() or not S11_ARTIFACT.read_text(encoding="utf-8").strip():
        _fail("E_S11_ARTIFACT", "candidate artifact bundle markdown missing or empty")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run([sys.executable, str(VALIDATE_MATERIAL), str(path)])
        if result.returncode == 0:
            _fail("E_S11_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S11_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema_packet_and_material() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict) or "S11FigureCaptionArtifactBundle" not in props:
        _fail("E_S11_SCHEMA", "S11FigureCaptionArtifactBundle schema property missing")
    required = set(props["S11FigureCaptionArtifactBundle"].get("required", []))
    missing = sorted(REQUIRED_SCHEMA_FIELDS - required)
    if missing:
        _fail("E_S11_SCHEMA", f"S11 schema missing {missing}")
    task_schema = _load_json(ROOT / "schemas/ppg-task-packet.schema.json")
    task_props = task_schema.get("properties", {})
    missing_packet_schema = sorted(REQUIRED_PACKET_FIELDS - set(task_props))
    if missing_packet_schema:
        _fail("E_S11_PACKET_SCHEMA", f"task packet schema missing {missing_packet_schema}")

    packet = _load_doc(S11_PACKET)
    missing_packet = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing_packet:
        _fail("E_S11_PACKET_FIELDS", f"S11 packet missing {missing_packet}")
    if packet.get("stage_id") != "S11" or packet.get("agent_type") != "executor":
        _fail("E_S11_PACKET_BINDING", "S11 packet must bind S11 executor")
    if packet.get("allowed_write_paths") != ["examples/candidate-artifacts/phase10_s11_figure_caption_bundle.md"]:
        _fail("E_S11_PACKET_WRITE_PATH", "S11 packet must contain exactly one allowed write path")
    material = _load_json(S11_MATERIAL)
    payload = material.get("payload", {})
    if payload.get("candidate_artifact_return") != _load_json(S11_RETURN):
        _fail("E_S11_RETURN_EMBED", "embedded CandidateArtifactReturn must match fixture")
    if payload.get("figure_contract_compliance", {}).get("proof_role_preserved") is not True:
        _fail("E_S11_PROOF_ROLE", "proof role must be preserved")
    if payload.get("visual_polish_report", {}).get("changes_made", [{}])[0].get("claim_meaning_changed") is not False:
        _fail("E_S11_POLISH", "visual polish must not change claim meaning")


def _verify_registry_contract_phase10() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    stages = {stage.get("stage_id"): stage for stage in registry.get("stages", []) if isinstance(stage, dict)}
    s11 = stages.get("S11")
    if not isinstance(s11, dict):
        _fail("E_S11_REGISTRY", "S11 registry stage missing")
    if s11.get("consumes") != PUBLIC_CONSUMES or s11.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S11_REGISTRY_IO", "S11 public graph I/O drifted")
    if s11.get("requires_worker_task_packet") is not True or s11.get("recommended_agent_type") != "executor":
        _fail("E_S11_REGISTRY", "S11 must require worker packet and executor producer")
    missing_validators = sorted(REQUIRED_REGISTRY_VALIDATORS - set(s11.get("validators", [])))
    if missing_validators:
        _fail("E_S11_REGISTRY_VALIDATORS", f"S11 registry validators missing {missing_validators}")

    contract = _load_json(ROOT / "examples/stage-contracts/S11.stage-contract.json")
    for key in ("consumes", "produces", "validators", "completion_gate", "coverage_status", "subagent_lane_policy"):
        if contract.get(key) != s11.get(key):
            _fail("E_S11_CONTRACT", f"S11 contract/registry mismatch on {key}")
    coverage = contract.get("worker_packet_coverage")
    if not isinstance(coverage, dict) or coverage.get("packet_ref") != "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml":
        _fail("E_S11_CONTRACT_PACKET", "S11 contract must link strict S11 packet")

    phase10 = _load_json(ROOT / "runtime/phase10_content_validators.json")
    validators = {item.get("stage_id"): item for item in phase10.get("validators", []) if isinstance(item, dict)}
    phase_s11 = validators.get("S11")
    if not isinstance(phase_s11, dict):
        _fail("E_S11_PHASE10", "S11 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in phase_s11.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = sorted(REQUIRED_PHASE10_DIMENSIONS - dimensions)
    if missing_dimensions:
        _fail("E_S11_PHASE10_DIMENSIONS", f"S11 phase10 dimensions missing {missing_dimensions}")
    checks = set(phase_s11.get("required_checks", []))
    missing_checks = sorted(REQUIRED_PHASE10_CHECKS - checks)
    if missing_checks:
        _fail("E_S11_PHASE10_CHECKS", f"S11 phase10 checks missing {missing_checks}")


def main() -> int:
    _verify_fixtures()
    _verify_schema_packet_and_material()
    _verify_registry_contract_phase10()
    print("PPG_S11_FIGURE_CAPTION_ARTIFACT_BUNDLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
