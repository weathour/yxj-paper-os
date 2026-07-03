#!/usr/bin/env python3
"""Verify RenderedManuscriptAuditGate docs, schema, and fixtures."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "RENDERED_MANUSCRIPT_AUDIT_GATE.md"
SCHEMA = ROOT / "schemas" / "ppg-rendered-manuscript-audit-gate.schema.json"
FIXTURE_DIR = ROOT / "examples" / "delivery"
LINKED_DOCS = [
    ROOT / "docs" / "TARGET_DELIVERY_CONTRACT.md",
    ROOT / "docs" / "RUNTIME_PROTOCOL.md",
    ROOT / "docs" / "VALIDATION_AND_TESTING.md",
    ROOT / "docs" / "stages" / "S16-export-handoff-package.md",
]
REQUIRED_TOP_LEVEL = [
    "schema_version",
    "gate_id",
    "target_binding",
    "input_refs",
    "rendered_inputs",
    "quality_checks",
    "severity_summary",
    "decision",
    "handoff_boundary",
    "feedback_route",
]
REQUIRED_INPUT_REFS = ["s16_export_handoff_package_ref", "output_pdf_ref", "rendered_text_ref", "file_hash_manifest_ref"]
SEVERITIES = ["BLOCKING", "MAJOR", "MINOR", "WATCH"]


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


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_gate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"E_RENDERED_GATE_FIELD_MISSING:{key}")
    if data.get("schema_version") != "ppg-rendered-manuscript-audit-gate/v0.1":
        errors.append("E_RENDERED_GATE_SCHEMA_VERSION")
    if data.get("gate_id") != "RenderedManuscriptAuditGate":
        errors.append("E_RENDERED_GATE_ID")

    target = data.get("target_binding")
    compiled_target = False
    if not isinstance(target, dict):
        errors.append("E_RENDERED_GATE_TARGET_BINDING")
    else:
        compiled_target = target.get("compiled_target") is True
        if not _non_empty_string(target.get("delivery_target_kind")) or not _non_empty_string(target.get("source")):
            errors.append("E_RENDERED_GATE_TARGET_BINDING")

    refs = data.get("input_refs")
    if not isinstance(refs, dict) or any(not _non_empty_string(refs.get(key)) for key in REQUIRED_INPUT_REFS):
        errors.append("E_RENDERED_GATE_S16_INPUTS")
    elif compiled_target and (not _non_empty_string(refs.get("source_writeback_evidence_ref")) or not _non_empty_string(refs.get("post_writeback_validation_ref"))):
        errors.append("E_RENDERED_GATE_S16_INPUTS")

    rendered = data.get("rendered_inputs")
    if not isinstance(rendered, dict):
        errors.append("E_RENDERED_GATE_RENDERED_INPUTS")
    else:
        for key in ["pdf_sha256", "rendered_text_sha256"]:
            if not _non_empty_string(rendered.get(key)):
                errors.append("E_RENDERED_GATE_RENDERED_INPUTS")
        if compiled_target and (rendered.get("template_only_detected") is True or re.search(r"Manuscript Not Started|template is intentionally blank|placeholder", str(rendered.get("rendered_text_excerpt", "")), re.I)):
            errors.append("E_RENDERED_GATE_TEMPLATE_ONLY_PASS")
        if rendered.get("internal_lexicon_detected") is True or rendered.get("unresolved_risk_leakage_detected") is True:
            errors.append("E_RENDERED_GATE_RENDERED_RISK_LEAKAGE")

    checks = data.get("quality_checks")
    unresolved_blocking_major = 0
    if not isinstance(checks, list) or not checks:
        errors.append("E_RENDERED_GATE_CHECKS")
    else:
        for item in checks:
            if not isinstance(item, dict):
                errors.append("E_RENDERED_GATE_CHECKS")
                break
            if not _non_empty_string(item.get("check_id")) or item.get("status") not in {"pass", "fail", "risk"} or item.get("severity") not in SEVERITIES or not _non_empty_string(item.get("evidence_ref")) or not _non_empty_string(item.get("nearest_responsible_stage")):
                errors.append("E_RENDERED_GATE_CHECKS")
                break
            if item.get("status") != "pass" and item.get("severity") in {"BLOCKING", "MAJOR"}:
                unresolved_blocking_major += 1

    summary = data.get("severity_summary")
    if not isinstance(summary, dict) or any(not isinstance(summary.get(level), int) or summary[level] < 0 for level in SEVERITIES):
        errors.append("E_RENDERED_GATE_SEVERITY_SUMMARY")
    else:
        unresolved_blocking_major += int(summary.get("BLOCKING", 0)) + int(summary.get("MAJOR", 0))

    decision = data.get("decision")
    status = None
    if not isinstance(decision, dict):
        errors.append("E_RENDERED_GATE_DECISION")
    else:
        status = decision.get("status")
        if status not in {"pass", "blocked"} or not _non_empty_string(decision.get("rationale")):
            errors.append("E_RENDERED_GATE_DECISION")
        if decision.get("submission_ready_claimed") is not False:
            errors.append("E_RENDERED_GATE_SUBMISSION_OVERCLAIM")
        if status == "pass" and unresolved_blocking_major > 0:
            errors.append("E_RENDERED_GATE_UNRESOLVED_BLOCKING_MAJOR")
        if status == "blocked" and unresolved_blocking_major == 0:
            errors.append("E_RENDERED_GATE_OVERSTRICT_MINOR_WATCH")

    boundary = data.get("handoff_boundary")
    if not isinstance(boundary, dict) or boundary.get("s16_export_is_input_not_quality_gate") is not True or boundary.get("submission_owner_gated") is not True or boundary.get("publication_claim_forbidden") is not True:
        errors.append("E_RENDERED_GATE_AUTHORITY_BOUNDARY")

    route = data.get("feedback_route")
    if not isinstance(route, list) or not route or not all(_non_empty_string(item) for item in route):
        errors.append("E_RENDERED_GATE_FEEDBACK_ROUTE")
    return errors


def main() -> None:
    for path in [DOC, SCHEMA, *LINKED_DOCS]:
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")
    doc_text = DOC.read_text(encoding="utf-8")
    for term in ["RenderedManuscriptAuditGate", "S16", "BLOCKING", "MAJOR", "MINOR", "WATCH", "owner-gated"]:
        if term not in doc_text:
            fail(f"docs/RENDERED_MANUSCRIPT_AUDIT_GATE.md missing {term}")
    for path in LINKED_DOCS:
        text = path.read_text(encoding="utf-8")
        if "RenderedManuscriptAuditGate" not in text or "verify_rendered_manuscript_audit_gate.py" not in text:
            fail(f"{path.relative_to(ROOT)} missing rendered gate link/verifier reference")

    schema = load_json(SCHEMA)
    missing_required = sorted(set(REQUIRED_TOP_LEVEL) - set(schema.get("required", [])))
    if missing_required:
        fail(f"schema missing required keys: {missing_required}")

    positive = load_json(FIXTURE_DIR / "rendered_manuscript_audit_gate.pass.json")
    errors = validate_gate(positive)
    if errors:
        fail(f"positive rendered gate failed: {errors}")

    for path in sorted(FIXTURE_DIR.glob("invalid-rendered-audit-*.json")):
        data = load_json(path)
        expected = data.get("expected_failure_code")
        if not _non_empty_string(expected):
            fail(f"{path.name} missing expected_failure_code")
        errors = validate_gate(data)
        if expected not in errors:
            fail(f"{path.name} expected {expected}, got {errors}")
    print("PPG_RENDERED_MANUSCRIPT_AUDIT_GATE_OK")


if __name__ == "__main__":
    main()
