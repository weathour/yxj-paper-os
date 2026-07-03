#!/usr/bin/env python3
"""Verify stage-quality contract doctrine, schema, and hostile fixtures."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "docs" / "STAGE_QUALITY_UPGRADE_TARGETS.md",
    ROOT / "docs" / "STAGE_QUALITY_CONTRACTS.md",
]
SCHEMA = ROOT / "schemas" / "ppg-stage-quality-contract.schema.json"
FIXTURE_DIR = ROOT / "examples" / "stage-quality"
REQUIRED_DOC_TERMS = [
    "StageQualityContract",
    "ProducerTaskPacketQualityContract",
    "AuditVerifierPacketQualityContract",
    "MustReadMaterialManifest",
    "ObligationExtractionLedger",
    "ObligationCoverageLedger",
    "RenderedManuscriptAuditGate",
    "unit_material_closure",
    "material_access_manifest",
    "material_read_obligations",
    "material_read_receipt_ledger",
    "BLOCKING",
    "MAJOR",
    "MINOR",
    "WATCH",
]
REQUIRED_CONTRACT_KEYS = [
    "schema_version",
    "stage_id",
    "active_profile_source",
    "must_read_materials",
    "required_extractions",
    "producer_return_obligations",
    "audit_verifier_obligations",
    "downstream_design_force",
    "failure_severity_policy",
    "nearest_responsible_stage_policy",
    "affected_downstream_nodes",
    "anti_over_strictness_boundary",
]
SEVERITIES = ["BLOCKING", "MAJOR", "MINOR", "WATCH"]
REQUIRED_STAGE_CONTRACT_IDS = ["S00", "S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09A", "S09B", "S10", "S11"]
STAGE_REQUIRED_TERMS = {
    "S09A": ["hard_constraints", "control_priority_map", "conflict_resolution_log", "downstream_packet_requirements"],
    "S09B": ["selected_controls", "unit_material_closure", "material_access_manifest", "material_read_obligations"],
    "S10": ["material_hydration_report", "material_read_receipt_ledger", "claim_evidence_trace", "verifier_evidence"],
    "S11": ["S10_text_callout_context", "current_latex_slots", "source_data_trace", "caption_claim_trace"],
}


def fail(message: str) -> NoReturn:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be object")
    return data


def non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def validate_contract(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_CONTRACT_KEYS:
        if key not in obj:
            errors.append(f"E_STAGE_QUALITY_FIELD_MISSING:{key}")
    if obj.get("schema_version") != "ppg-stage-quality-contract/v0.1":
        errors.append("E_STAGE_QUALITY_SCHEMA_VERSION")
    if not re.match(r"^(S(0[0-8]|09A|09B|1[0-6])|G0[12])$", str(obj.get("stage_id", ""))):
        errors.append("E_STAGE_QUALITY_STAGE_ID")
    materials = obj.get("must_read_materials")
    if not isinstance(materials, list) or not materials:
        errors.append("E_STAGE_QUALITY_MUST_READ_EMPTY")
    else:
        for item in materials:
            if not isinstance(item, dict) or not item.get("material_ref") or item.get("read_mode") not in {"full", "targeted", "locator_only"} or not non_empty_string_list(item.get("required_extractions")):
                errors.append("E_STAGE_QUALITY_MUST_READ_ITEM")
                break
    for key in ["required_extractions", "producer_return_obligations", "downstream_design_force", "affected_downstream_nodes"]:
        if not non_empty_string_list(obj.get(key)):
            errors.append(f"E_STAGE_QUALITY_LIST:{key}")
    audit = obj.get("audit_verifier_obligations")
    if not isinstance(audit, dict) or audit.get("inherits_all_producer_inputs") is not True:
        errors.append("E_STAGE_QUALITY_AUDIT_INHERITANCE")
    elif not non_empty_string_list(audit.get("checks")):
        errors.append("E_STAGE_QUALITY_AUDIT_CHECKS")
    severity = obj.get("failure_severity_policy")
    if not isinstance(severity, dict) or any(not isinstance(severity.get(level), str) or not severity[level].strip() for level in SEVERITIES):
        errors.append("E_STAGE_QUALITY_SEVERITY")
    text_obj = {key: value for key, value in obj.items() if key != "expected_failure_code"}
    text = json.dumps(text_obj, ensure_ascii=False)
    if re.search(r"All\s+yxj-paper-os\s+papers\s+must\s+use\s+KBS|KBS\s+as\s+the\s+default\s+profile", text, re.I):
        errors.append("E_STAGE_QUALITY_GLOBAL_PROFILE_DEFAULT")
    if re.search(r"Every\s+WATCH.*Every\s+MINOR.*block|WATCH.*MINOR.*force\s+a\s+full\s+rerun|MINOR.*WATCH.*must\s+block", text, re.I | re.S):
        errors.append("E_STAGE_QUALITY_OVERSTRICT_MINOR_WATCH")
    stage_id = str(obj.get("stage_id", ""))
    for term in STAGE_REQUIRED_TERMS.get(stage_id, []):
        if term not in text:
            errors.append(f"E_STAGE_QUALITY_STAGE_TERMS:{stage_id}:{term}")
    return errors


def main() -> None:
    for path in DOCS:
        if not path.is_file():
            fail(f"missing doc {path.relative_to(ROOT)}")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS)
    for term in REQUIRED_DOC_TERMS:
        if term not in combined:
            fail(f"missing required doc term: {term}")
    schema = load_json(SCHEMA)
    required = set(schema.get("required", []))
    missing_required = sorted(set(REQUIRED_CONTRACT_KEYS) - required)
    if missing_required:
        fail(f"schema missing required keys: {missing_required}")

    for positive_path in sorted(FIXTURE_DIR.glob("*.pass.json")):
        positive = load_json(positive_path)
        errors = validate_contract(positive)
        if errors:
            fail(f"{positive_path.name} positive fixture failed: {errors}")

    for sid in REQUIRED_STAGE_CONTRACT_IDS:
        contract_path = ROOT / "examples" / "stage-contracts" / f"{sid}.stage-contract.json"
        data = load_json(contract_path)
        sqc = data.get("stage_quality_contract")
        if not isinstance(sqc, dict):
            fail(f"{contract_path.name} missing stage_quality_contract")
        errors = validate_contract(sqc)
        if errors:
            fail(f"{contract_path.name} stage_quality_contract failed: {errors}")

    for path in sorted(FIXTURE_DIR.glob("invalid-*.json")):
        obj = load_json(path)
        expected = obj.get("expected_failure_code")
        if not isinstance(expected, str) or not expected:
            fail(f"{path.name} missing expected_failure_code")
        errors = validate_contract(obj)
        if expected not in errors:
            fail(f"{path.name} expected {expected}, got {errors}")

    print("PPG_STAGE_QUALITY_CONTRACTS_OK")


if __name__ == "__main__":
    main()
