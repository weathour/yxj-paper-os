#!/usr/bin/env python3
"""Verify S02 research-scene/SOTA/exemplar/language dossier contract and fixtures."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, NoReturn

try:
    from ppg_validate_common import load_document
except ImportError:  # pragma: no cover - script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_MATERIAL = ROOT / "scripts" / "validate_material.py"
VALIDATE_PACKET = ROOT / "scripts" / "validate_packet.py"
S02_PACKET = ROOT / "examples" / "packets" / "phase10_s02_sota_analysis_packet.v1.yaml"
S02_MATERIAL = ROOT / "examples" / "materials" / "phase10_s02_research_dossier.yaml"

S02_COMPLETION_BOUNDARY = "research_profile_only_no_contribution_freeze_no_claim_wording_no_graph_or_manuscript_completion"
PUBLIC_CONSUMES = ["source map", "citation bank", "venue route", "exemplar locators"]
PUBLIC_PRODUCES = ["research dossier", "reader package", "template profile", "citation verification report"]
REQUIRED_REGISTRY_VALIDATORS = {
    "S02_source_coverage_ledger",
    "S02_sota_family_coverage_ledger",
    "S02_template_language_profile",
    "S02_descriptive_not_prescriptive",
    "S02_template_copying_boundary",
    "S02_unresolved_backflow_register",
    "S02_downstream_handoff_coverage",
    "S02_no_claim_or_completion_freeze",
}
REQUIRED_PACKET_PASSES = {
    "source_citation_exemplar_inventory",
    "sota_family_mapping",
    "comparator_source_verification",
    "template_exemplar_structure_extraction",
    "language_rhetorical_profile_extraction",
    "downstream_handoff_backflow",
}
REQUIRED_OUTPUT_MODULES = {
    "completion_boundary",
    "research_scene_profile",
    "sota_comparator_map",
    "template_exemplar_profile",
    "template_language_profile",
    "descriptive_not_prescriptive_controls",
    "source_coverage_ledger",
    "exemplar_sample_register",
    "language_profile_sample_limits",
    "sota_family_coverage_ledger",
    "unresolved_source_report",
    "downstream_handoff_coverage",
    "misuse_guard",
    "citation_verification_report",
    "candidate_return",
}
REQUIRED_CONTROL_FLAGS = {
    "statistics_are_descriptive",
    "no_sentence_or_paragraph_rule_generation",
    "exemplar_copying_forbidden",
    "allow_deviation_when_claim_boundary_requires",
    "preserve_claim_boundary_over_metric_matching",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s02_source_exemplar_coverage",
    "s02_sota_family_coverage",
    "s02_template_exemplar_boundary",
    "s02_template_language_profile",
    "s02_descriptive_not_prescriptive_controls",
    "s02_unresolved_backflow_register",
    "s02_downstream_handoff_coverage",
    "s02_nature_overlay",
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
    "s02_source_coverage_ledger",
    "s02_sota_family_coverage_ledger",
    "s02_template_language_profile_present",
    "s02_statistics_descriptive_not_prescriptive",
    "s02_no_copyable_template_language",
    "s02_no_contribution_freeze",
    "s02_no_final_claim_wording",
    "s02_unresolved_backflow_register",
    "s02_downstream_handoff_coverage",
    "no_completion_overclaim",
}
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s02-research-dossier-missing-language-profile.yaml": "E_S02_TEMPLATE_LANGUAGE_PROFILE_REQUIRED",
    ROOT / "examples/materials/invalid-s02-research-dossier-prescriptive-metrics.yaml": "E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE",
    ROOT / "examples/materials/invalid-s02-research-dossier-template-copying.yaml": "E_S02_TEMPLATE_COPYING_BOUNDARY",
    ROOT / "examples/materials/invalid-s02-research-dossier-claim-freeze.yaml": "E_S02_NO_CONTRIBUTION_OR_CLAIM_FREEZE",
    ROOT / "examples/materials/invalid-s02-research-dossier-completion-overclaim.yaml": "E_S02_NO_COMPLETION_OVERCLAIM",
    ROOT / "examples/materials/invalid-s02-research-dossier-missing-coverage-ledger.yaml": "E_S02_COVERAGE_LEDGER_REQUIRED",
    ROOT / "examples/materials/invalid-s02-research-dossier-missing-unresolved-report.yaml": "E_S02_UNRESOLVED_BACKFLOW_REQUIRED",
    ROOT / "examples/materials/invalid-s02-research-dossier-missing-downstream-handoff.yaml": "E_S02_DOWNSTREAM_HANDOFF_REQUIRED",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        _fail("E_S02_JSON_LOAD", f"{path}: {exc}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        _fail("E_S02_YAML_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        _fail("E_S02_YAML_LOAD", f"{path}: root must be a mapping")
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
    result = _run(VALIDATE_MATERIAL, S02_MATERIAL)
    if result.returncode != 0:
        _fail("E_S02_POSITIVE_FIXTURE", f"{S02_MATERIAL} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run(VALIDATE_MATERIAL, path)
        if result.returncode == 0:
            _fail("E_S02_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S02_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        _fail("E_S02_SCHEMA", "schema properties mapping missing")
    spec = props.get("S02ResearchDossier")
    if not isinstance(spec, dict):
        _fail("E_S02_SCHEMA", "S02ResearchDossier schema missing")
    nested = spec.get("properties")
    if not isinstance(nested, dict):
        _fail("E_S02_SCHEMA", "S02ResearchDossier properties missing")
    if nested.get("schema_version", {}).get("const") != "ppg-s02-research-dossier/v0.1":
        _fail("E_S02_SCHEMA", "S02ResearchDossier.schema_version const mismatch")
    if nested.get("stage_id", {}).get("const") != "S02":
        _fail("E_S02_SCHEMA", "S02ResearchDossier.stage_id const mismatch")
    required = set(spec.get("required", [])) if isinstance(spec.get("required"), list) else set()
    missing = (REQUIRED_OUTPUT_MODULES | {"schema_version", "stage_id"}) - required
    if missing:
        _fail("E_S02_SCHEMA", f"S02ResearchDossier schema required fields missing {sorted(missing)}")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s02 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S02"), None)
    if not isinstance(s02, dict):
        _fail("E_S02_REGISTRY", "S02 missing from stage registry")
    if s02.get("requires_worker_task_packet") is not True:
        _fail("E_S02_REGISTRY", "S02 must keep requires_worker_task_packet=true")
    if s02.get("consumes") != PUBLIC_CONSUMES or s02.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S02_REGISTRY", "S02 public graph I/O changed")
    if s02.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S02_REGISTRY", "S02 must keep mandatory_double lane policy")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s02.get("validators", []))
    if missing:
        _fail("E_S02_REGISTRY", f"S02 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S02.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not True:
        _fail("E_S02_CONTRACT", "S02 stage contract must keep requires_worker_task_packet=true")
    if contract.get("consumes") != PUBLIC_CONSUMES or contract.get("produces") != PUBLIC_PRODUCES:
        _fail("E_S02_CONTRACT", "S02 contract public graph I/O changed")
    if contract.get("subagent_lane_policy", {}).get("policy") != "mandatory_double":
        _fail("E_S02_CONTRACT", "S02 contract must keep mandatory_double lane policy")
    if set(contract.get("validators", [])) != set(s02.get("validators", [])):
        _fail("E_S02_CONTRACT", "S02 registry/contract validator labels diverged")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "linked_strict_packet":
        _fail("E_S02_CONTRACT", "S02 worker_packet_coverage.status must be linked_strict_packet")
    if packet.get("packet_ref") != "examples/packets/phase10_s02_sota_analysis_packet.v1.yaml":
        _fail("E_S02_CONTRACT", "S02 packet_ref mismatch")
    if packet.get("return_contract_ref") != "schemas/ppg-candidate-return.schema.json":
        _fail("E_S02_CONTRACT", "S02 return_contract_ref mismatch")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("completion_forbidden") is not True or authority.get("controller_owned_completion") is not True or authority.get("no_recursive_orchestration") is not True:
        _fail("E_S02_CONTRACT", "S02 worker authority boundary weakened")


def _verify_packet() -> None:
    result = _run(VALIDATE_PACKET, S02_PACKET)
    if result.returncode != 0:
        _fail("E_S02_PACKET", f"S02 packet should validate but failed:\n{result.stdout}")
    packet = _load_yaml(S02_PACKET)
    if packet.get("target_material") != "phase10_s02_research_dossier":
        _fail("E_S02_PACKET", "target_material mismatch")
    if packet.get("output_artifact_path") != "examples/materials/phase10_s02_research_dossier.yaml":
        _fail("E_S02_PACKET", "output_artifact_path mismatch")
    if packet.get("allowed_write_paths") != ["examples/materials/phase10_s02_research_dossier.yaml"]:
        _fail("E_S02_PACKET", "allowed_write_paths must be exactly the S02 material fixture")
    if packet.get("expected_output_schema") != "ppg-material/v0.1" or packet.get("expected_material_type") != "S02ResearchDossier" or packet.get("expected_payload_schema") != "ppg-s02-research-dossier/v0.1":
        _fail("E_S02_PACKET", "expected schema/material binding mismatch")
    protocol = packet.get("internal_execution_protocol")
    if not isinstance(protocol, dict):
        _fail("E_S02_PACKET", "internal_execution_protocol missing")
    for key in ("work_queue_required", "coverage_ledger_required", "unresolved_register_required", "downstream_handoff_required", "no_silent_omission", "no_final_prose"):
        if protocol.get(key) is not True:
            _fail("E_S02_PACKET", f"internal_execution_protocol.{key} must be true")
    passes = {item.get("pass_id") for item in protocol.get("required_passes", []) if isinstance(item, dict)}
    missing_passes = REQUIRED_PACKET_PASSES - passes
    if missing_passes:
        _fail("E_S02_PACKET", f"internal_execution_protocol.required_passes missing {sorted(missing_passes)}")
    output_contract = packet.get("output_contract")
    if not isinstance(output_contract, dict):
        _fail("E_S02_PACKET", "output_contract missing")
    if output_contract.get("material_type") != "S02ResearchDossier" or output_contract.get("payload_schema") != "ppg-s02-research-dossier/v0.1":
        _fail("E_S02_PACKET", "output_contract material binding mismatch")
    modules = set(output_contract.get("required_modules", [])) if isinstance(output_contract.get("required_modules"), list) else set()
    missing_modules = REQUIRED_OUTPUT_MODULES - modules
    if missing_modules:
        _fail("E_S02_PACKET", f"output_contract.required_modules missing {sorted(missing_modules)}")
    controls = packet.get("descriptive_not_prescriptive_controls")
    if not isinstance(controls, dict):
        _fail("E_S02_PACKET", "descriptive_not_prescriptive_controls missing")
    for key in sorted(REQUIRED_CONTROL_FLAGS):
        if controls.get(key) is not True:
            _fail("E_S02_PACKET", f"descriptive_not_prescriptive_controls.{key} must be true")
    if "validate_material:S02ResearchDossier" not in packet.get("validators", []) or "descriptive_not_prescriptive:S02" not in packet.get("validators", []):
        _fail("E_S02_PACKET", "S02 material/descriptive validators missing")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s02 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S02"), None)
    if not isinstance(s02, dict):
        _fail("E_S02_PHASE10", "S02 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s02.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S02_PHASE10", f"S02 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s02.get("required_checks", []))
    if missing_checks:
        _fail("E_S02_PHASE10", f"S02 phase10 checks missing {sorted(missing_checks)}")


def main() -> int:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_packet()
    _verify_phase10()
    print("PPG_S02_RESEARCH_DOSSIER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
