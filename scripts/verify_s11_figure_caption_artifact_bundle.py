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
VERIFY_VENDOR = ROOT / "scripts" / "verify_s11_nature_figure_vendor.py"
S11_PACKET = ROOT / "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml"
S11_RETURN = ROOT / "examples/candidate_returns/phase10_s11_figure_caption_bundle_return.json"
S11_MATERIAL = ROOT / "examples/materials/phase10_s11_figure_caption_artifact_bundle.json"
S11_ARTIFACT = ROOT / "examples/candidate-artifacts/phase10_s11_figure_caption_bundle.md"
S11_ADAPTER = ROOT / "runtime/adapters/S11NatureFigureDirectCall.adapter.json"
S11_ALLOWED_WRITE_PATHS = [
    "examples/candidate-artifacts/phase10_s11_figure_caption_bundle.md",
    "figures/src/phase10_s11_authority_loss_reconfiguration.py",
    "figures/generated/phase10_s11_authority_loss_reconfiguration.svg",
    "figures/generated/phase10_s11_authority_loss_reconfiguration.pdf",
]
S11_NATURE_UPSTREAM_COMMIT = "c91df241a7a963ea151687ac669c5534404f53e5"
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
    "nature_figure_direct_call",
    "figure_backend",
    "render_execution_policy",
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
    "nature_figure_capability_report",
    "nature_figure_contract",
    "nature_figure_execution",
    "nature_figure_qa_report",
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
    "S11_nature_figure_vendor_present",
    "S11_nature_figure_parity_manifest",
    "S11_nature_figure_backend_gate",
    "S11_nature_figure_direct_call_mapping",
    "S11_no_cross_backend_rendering",
    "S11_no_mock_data_for_evidential_figure",
    "S11_exemplar_boundary_and_similarity_report",
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
    "s11_nature_figure_vendor_and_parity",
    "s11_nature_figure_backend_gate",
    "s11_nature_figure_execution_boundary",
    "s11_exemplar_similarity_boundary",
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
    "S11_nature_figure_vendor_present",
    "S11_nature_figure_parity_manifest",
    "S11_nature_figure_backend_gate",
    "S11_nature_figure_direct_call_mapping",
    "S11_no_cross_backend_rendering",
    "S11_no_mock_data_for_evidential_figure",
    "S11_exemplar_boundary_and_similarity_report",
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
    ROOT / "examples/materials/invalid-s11-nature-figure-missing-capability.json": "E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-bad-parity.json": "E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-missing-backend.json": "E_S11_NATURE_FIGURE_CONTRACT_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-cross-backend.json": "E_S11_NATURE_FIGURE_EXECUTION_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-mock-data.json": "E_S11_NATURE_FIGURE_EXECUTION_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-missing-s11-mapping.json": "E_S11_NATURE_FIGURE_QA_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-final-export-overclaim.json": "E_S11_NATURE_FIGURE_QA_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-exemplar-copy-risk.json": "E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-unsafe-planned-render-path.json": "E_S11_NATURE_FIGURE_PATH_REQUIRED",
    ROOT / "examples/materials/invalid-s11-nature-figure-bad-backend-fragment.json": "E_S11_NATURE_FIGURE_CONTRACT_REQUIRED",
}
NEGATIVE_PACKET_FIXTURES = {
    ROOT / "examples/packets/invalid-s11-nature-output-generated-packet.json": "E_TASK_OUTPUT_PATH_REQUIRED",
    ROOT / "examples/packets/invalid-non-s11-nature-fields-packet.json": "E_TASK_NATURE_FIGURE_DIRECT_CALL_FORBIDDEN",
    ROOT / "examples/packets/invalid-s11-nature-bad-backend-fragment-packet.json": "E_TASK_NATURE_FIGURE_BACKEND_REQUIRED",
    ROOT / "examples/packets/invalid-s11-nature-bad-upstream-commit-packet.json": "E_TASK_NATURE_FIGURE_DIRECT_CALL_REQUIRED",
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
        [sys.executable, str(VERIFY_VENDOR)],
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
    for path, expected_code in NEGATIVE_PACKET_FIXTURES.items():
        result = _run([sys.executable, str(VALIDATE_PACKET), str(path)])
        if result.returncode == 0:
            _fail("E_S11_NEGATIVE_PACKET_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S11_NEGATIVE_PACKET_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")
    extra_file = ROOT / "third_party/nature-figure/__unexpected_extra_file_for_negative_check.tmp"
    try:
        extra_file.write_text("unexpected extra file should fail parity verifier\n", encoding="utf-8")
        result = _run([sys.executable, str(VERIFY_VENDOR)])
        if result.returncode == 0:
            _fail("E_S11_NEGATIVE_VENDOR_EXTRA_FILE", "vendor verifier should reject unexpected extra files")
        if "E_S11_NATURE_VENDOR_EXTRA_FILE" not in result.stdout:
            _fail("E_S11_NEGATIVE_VENDOR_EXTRA_FILE", f"vendor extra-file probe should fail with E_S11_NATURE_VENDOR_EXTRA_FILE; got:\n{result.stdout}")
    finally:
        extra_file.unlink(missing_ok=True)


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
    schema_condition_text = json.dumps(task_schema.get("allOf", []), sort_keys=True)
    for required_text in (
        "examples/candidate-artifacts/",
        "nature_figure_direct_call",
        "figure_backend",
        "render_execution_policy",
        "figures/src",
        "figures/generated",
    ):
        if required_text not in schema_condition_text:
            _fail("E_S11_PACKET_SCHEMA", f"S11 task packet schema conditional guard missing {required_text}")

    packet = _load_doc(S11_PACKET)
    missing_packet = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing_packet:
        _fail("E_S11_PACKET_FIELDS", f"S11 packet missing {missing_packet}")
    if packet.get("stage_id") != "S11" or packet.get("agent_type") != "executor":
        _fail("E_S11_PACKET_BINDING", "S11 packet must bind S11 executor")
    if packet.get("allowed_write_paths") != S11_ALLOWED_WRITE_PATHS:
        _fail("E_S11_PACKET_WRITE_PATH", "S11 packet must contain the candidate artifact, figures/src, and figures/generated S11 nature write paths")
    if packet.get("allowed_tools") != ["python3"]:
        _fail("E_S11_PACKET_TOOL", "S11 nature direct-call packet must expose only the selected python backend tool")
    direct_call = packet.get("nature_figure_direct_call", {})
    if not isinstance(direct_call, dict) or direct_call.get("enabled") is not True:
        _fail("E_S11_PACKET_NATURE_DIRECT_CALL", "S11 packet must enable nature_figure_direct_call")
    if direct_call.get("parity_manifest_ref") != "third_party/nature-figure/PARITY_MANIFEST.json" or direct_call.get("upstream_commit") != S11_NATURE_UPSTREAM_COMMIT:
        _fail("E_S11_PACKET_NATURE_DIRECT_CALL", "S11 packet direct-call parity metadata drifted")
    backend = packet.get("figure_backend", {})
    if not isinstance(backend, dict) or backend.get("selected_backend") != "python" or backend.get("selected_tool") != "python3":
        _fail("E_S11_PACKET_BACKEND", "S11 packet must preselect the python backend/tool")
    if backend.get("backend_exclusive") is not True or backend.get("worker_may_ask_backend_question") is not False:
        _fail("E_S11_PACKET_BACKEND", "S11 packet backend must be exclusive and non-interactive for the worker")
    render_policy = packet.get("render_execution_policy", {})
    if not isinstance(render_policy, dict) or render_policy.get("mock_data_forbidden_for_evidential_figures") is not True:
        _fail("E_S11_PACKET_RENDER_POLICY", "S11 packet must forbid mock evidential data")

    material = _load_json(S11_MATERIAL)
    payload = material.get("payload", {})
    if payload.get("candidate_artifact_return") != _load_json(S11_RETURN):
        _fail("E_S11_RETURN_EMBED", "embedded CandidateArtifactReturn must match fixture")
    if payload.get("figure_contract_compliance", {}).get("proof_role_preserved") is not True:
        _fail("E_S11_PROOF_ROLE", "proof role must be preserved")
    if payload.get("visual_polish_report", {}).get("changes_made", [{}])[0].get("claim_meaning_changed") is not False:
        _fail("E_S11_POLISH", "visual polish must not change claim meaning")
    capability = payload.get("nature_figure_capability_report", {})
    if capability.get("vendor_path") != "third_party/nature-figure" or capability.get("upstream_commit") != S11_NATURE_UPSTREAM_COMMIT:
        _fail("E_S11_NATURE_CAPABILITY", "S11 material nature capability metadata drifted")
    execution = payload.get("nature_figure_execution", {})
    if execution.get("backend") != "python" or execution.get("selected_tool") != "python3":
        _fail("E_S11_NATURE_EXECUTION", "S11 material must map execution to selected python backend")
    if execution.get("cross_backend_used") is not False or execution.get("mock_data_used") is not False:
        _fail("E_S11_NATURE_EXECUTION", "S11 material must prohibit cross-backend rendering and mock evidential data")
    qa = payload.get("nature_figure_qa_report", {})
    for key in ("s11_mapping_complete", "cross_backend_rendering_absent", "mock_data_absent_or_non_evidential", "exemplar_boundary_preserved"):
        if qa.get(key) is not True:
            _fail("E_S11_NATURE_QA", f"S11 material nature QA missing {key}")
    if qa.get("final_export_claimed") is not False:
        _fail("E_S11_NATURE_QA", "S11 nature QA must not claim final export")


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
    adapters = s11.get("capability_adapters")
    if not isinstance(adapters, list) or not any(isinstance(item, dict) and item.get("adapter_id") == "S11NatureFigureDirectCall" for item in adapters):
        _fail("E_S11_REGISTRY_ADAPTER", "S11 registry must include S11NatureFigureDirectCall capability adapter")
    if not S11_ADAPTER.is_file():
        _fail("E_S11_ADAPTER", "S11 nature direct-call adapter file missing")

    contract = _load_json(ROOT / "examples/stage-contracts/S11.stage-contract.json")
    for key in ("consumes", "produces", "validators", "completion_gate", "coverage_status", "subagent_lane_policy"):
        if contract.get(key) != s11.get(key):
            _fail("E_S11_CONTRACT", f"S11 contract/registry mismatch on {key}")
    if contract.get("capability_adapters") != s11.get("capability_adapters"):
        _fail("E_S11_CONTRACT_ADAPTER", "S11 contract/registry capability adapter mismatch")
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
