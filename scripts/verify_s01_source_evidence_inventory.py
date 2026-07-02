#!/usr/bin/env python3
"""Verify S01 source/citation/evidence inventory contract and fixtures."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "scripts" / "validate_material.py"

POSITIVE_FIXTURES = [
    ROOT / "examples/materials/s01_inventory_input.v1.yaml",
    ROOT / "examples/materials/s01_source_evidence_inventory.v1.yaml",
]
NEGATIVE_FIXTURES = {
    ROOT / "examples/materials/invalid-s01-inventory-input-source-write-allowed.yaml": "E_S01_READ_ONLY_BOUNDARY",
    ROOT / "examples/materials/invalid-s01-source-evidence-inventory-missing-completion-boundary.yaml": "E_S01_COMPLETION_BOUNDARY",
    ROOT / "examples/materials/invalid-s01-source-evidence-inventory-claim-admissibility.yaml": "E_S01_NO_CLAIM_ADMISSIBILITY",
    ROOT / "examples/materials/invalid-s01-source-evidence-inventory-missing-privacy-boundary.yaml": "E_S01_PRIVACY_BOUNDARY",
    ROOT / "examples/materials/invalid-s01-source-evidence-inventory-missing-unresolved-register.yaml": "E_S01_LOCATOR_REQUIRED",
    ROOT / "examples/materials/invalid-s01-source-evidence-inventory-private-promoted.yaml": "E_S01_PRIVACY_BOUNDARY",
}
REQUIRED_REGISTRY_VALIDATORS = {
    "S01_read_only_boundary",
    "S01_root_coverage",
    "S01_source_locator_resolution",
    "S01_bibtex_key_coverage",
    "S01_evidence_artifact_locator",
    "S01_figure_source_data_locator",
    "S01_supplement_inventory",
    "S01_privacy_boundary",
    "S01_freshness_hash_report",
    "S01_no_claim_admissibility",
    "S01_unresolved_locator_register",
    "S01_no_completion_overclaim",
}
REQUIRED_PHASE10_DIMENSIONS = {
    "s01_source_locator_completeness",
    "s01_citation_bank_coverage",
    "s01_evidence_artifact_provenance",
    "s01_figure_data_supplement_inventory",
    "s01_privacy_boundary_report",
    "s01_unresolved_locator_register",
    "s01_freshness_hash_provenance",
    "s01_no_claim_admissibility",
    "s01_read_only_inventory_candidate",
    "s01_nature_overlay",
}
REQUIRED_PHASE10_CHECKS = {
    "source_or_material_trace",
    "completion_boundary_explicit",
    "controller_owned_status",
    "stage_overlay_binding",
    "controller_route_only",
    "source_locator_resolution",
    "citation_bank_trace",
    "evidence_artifact_path_check",
    "figure_source_data_inventory",
    "data_availability_supplement_inventory",
    "privacy_boundary_check",
    "unresolved_locator_register",
    "freshness_hash_provenance",
    "read_only_inventory_boundary",
    "no_claim_admissibility_decision",
    "no_completion_overclaim",
}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        _fail("E_S01_JSON_LOAD", f"{path}: {exc}")


def _run_validate(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE), str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _verify_fixtures() -> None:
    for path in POSITIVE_FIXTURES:
        result = _run_validate(path)
        if result.returncode != 0:
            _fail("E_S01_POSITIVE_FIXTURE", f"{path} should validate but failed:\n{result.stdout}")
    for path, expected_code in NEGATIVE_FIXTURES.items():
        result = _run_validate(path)
        if result.returncode == 0:
            _fail("E_S01_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code} but validated")
        if expected_code not in result.stdout:
            _fail("E_S01_NEGATIVE_FIXTURE", f"{path} should fail with {expected_code}; got:\n{result.stdout}")


def _verify_schema() -> None:
    schema = _load_json(ROOT / "schemas/ppg-material-payloads.schema.json")
    assert isinstance(schema, dict)
    props = schema.get("properties")
    if not isinstance(props, dict):
        _fail("E_S01_SCHEMA", "schema properties mapping missing")
    for material_type, expected_schema in {
        "S01InventoryInput": "ppg-s01-inventory-input/v0.1",
        "S01SourceEvidenceInventory": "ppg-s01-source-evidence-inventory/v0.1",
    }.items():
        spec = props.get(material_type)
        if not isinstance(spec, dict):
            _fail("E_S01_SCHEMA", f"{material_type} schema missing")
        nested_props = spec.get("properties")
        if not isinstance(nested_props, dict):
            _fail("E_S01_SCHEMA", f"{material_type} properties missing")
        schema_version = nested_props.get("schema_version")
        stage_id = nested_props.get("stage_id")
        if not isinstance(schema_version, dict) or schema_version.get("const") != expected_schema:
            _fail("E_S01_SCHEMA", f"{material_type}.schema_version const mismatch")
        if not isinstance(stage_id, dict) or stage_id.get("const") != "S01":
            _fail("E_S01_SCHEMA", f"{material_type}.stage_id const mismatch")


def _verify_stage_contracts() -> None:
    registry = _load_json(ROOT / "runtime/stage_registry.json")
    assert isinstance(registry, dict)
    s01 = next((stage for stage in registry.get("stages", []) if stage.get("stage_id") == "S01"), None)
    if not isinstance(s01, dict):
        _fail("E_S01_REGISTRY", "S01 missing from stage registry")
    if s01.get("requires_worker_task_packet") is not False:
        _fail("E_S01_REGISTRY", "S01 must keep requires_worker_task_packet=false")
    if s01.get("consumes") != ["initial files", "result dirs", "BibTeX", "source locators"]:
        _fail("E_S01_REGISTRY", "S01 consumes public graph I/O changed")
    if s01.get("produces") != ["source map", "citation bank", "evidence bank"]:
        _fail("E_S01_REGISTRY", "S01 produces public graph I/O changed")
    missing = REQUIRED_REGISTRY_VALIDATORS - set(s01.get("validators", []))
    if missing:
        _fail("E_S01_REGISTRY", f"S01 registry validators missing {sorted(missing)}")

    contract = _load_json(ROOT / "examples/stage-contracts/S01.stage-contract.json")
    assert isinstance(contract, dict)
    if contract.get("requires_worker_task_packet") is not False:
        _fail("E_S01_CONTRACT", "S01 stage contract must keep requires_worker_task_packet=false")
    packet = contract.get("worker_packet_coverage")
    if not isinstance(packet, dict) or packet.get("status") != "not_required":
        _fail("E_S01_CONTRACT", "S01 worker_packet_coverage.status must be not_required")
    authority = contract.get("worker_authority_boundary")
    if not isinstance(authority, dict) or authority.get("source_write_forbidden") is not True or authority.get("claim_admissibility_forbidden") is not True:
        _fail("E_S01_CONTRACT", "S01 worker authority must forbid source writes and claim admissibility")
    brief = contract.get("read_only_inventory_brief")
    if not isinstance(brief, dict) or brief.get("schema_version") != "ppg-readonly-inventory-task/v0.1":
        _fail("E_S01_CONTRACT", "S01 read-only inventory brief missing")


def _verify_phase10() -> None:
    phase = _load_json(ROOT / "runtime/phase10_content_validators.json")
    assert isinstance(phase, dict)
    s01 = next((item for item in phase.get("validators", []) if item.get("stage_id") == "S01"), None)
    if not isinstance(s01, dict):
        _fail("E_S01_PHASE10", "S01 phase10 validator missing")
    dimensions = {item.get("dimension_id") for item in s01.get("dimensions", []) if isinstance(item, dict)}
    missing_dimensions = REQUIRED_PHASE10_DIMENSIONS - dimensions
    if missing_dimensions:
        _fail("E_S01_PHASE10", f"S01 phase10 dimensions missing {sorted(missing_dimensions)}")
    missing_checks = REQUIRED_PHASE10_CHECKS - set(s01.get("required_checks", []))
    if missing_checks:
        _fail("E_S01_PHASE10", f"S01 phase10 checks missing {sorted(missing_checks)}")


def main() -> int:
    _verify_fixtures()
    _verify_schema()
    _verify_stage_contracts()
    _verify_phase10()
    print("PPG_S01_SOURCE_EVIDENCE_INVENTORY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
