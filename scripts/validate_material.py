#!/usr/bin/env python3
"""Validate PPG material fixture envelopes and Phase 4 P1 payload semantics."""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        as_mapping,
        as_sequence,
        issue,
        is_non_empty_mapping_list,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )
except ImportError:  # pragma: no cover - script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        as_mapping,
        as_sequence,
        issue,
        is_non_empty_mapping_list,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )


ALLOWED_CLAIM_STRENGTHS = {
    "bounded",
    "bounded-method-evidence",
    "descriptive",
    "evidence_supported",
    "limited",
    "qualified",
}


def _payload(data: dict[str, Any], errors: list[ValidationIssue]) -> dict[str, Any] | None:
    payload = as_mapping(data.get("payload"))
    if payload is None:
        errors.append(issue("E_PAYLOAD_REQUIRED", "payload mapping is required"))
    return payload


def _validate_evidence_inventory(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    packages = payload.get("evidence_packages")
    if not is_non_empty_mapping_list(packages):
        errors.append(issue("E_PAYLOAD_REQUIRED", "EvidenceInventory.evidence_packages must be a non-empty list of mappings"))
        return
    assert isinstance(packages, list)
    for idx, package in enumerate(packages):
        assert isinstance(package, dict)
        if not is_non_empty_string(package.get("id")) or not is_non_empty_string(package.get("claim_strength")):
            errors.append(issue("E_PAYLOAD_REQUIRED", f"evidence_packages[{idx}] needs string id and claim_strength"))


def _valid_guardrail_list(payload: dict[str, Any], field: str, errors: list[ValidationIssue]) -> bool:
    if field not in payload:
        return False
    value = payload.get(field)
    if not is_non_empty_string_list(value):
        errors.append(issue("E_PAYLOAD_REQUIRED", f"ClaimBoundaryMap.{field} must be a non-empty list of strings"))
        return False
    return True


def _validate_claim_boundary_map(data: dict[str, Any], payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    raw_allowed_claims = payload.get("allowed_claims")
    allowed_claims = as_sequence(raw_allowed_claims)
    if raw_allowed_claims is not None and not is_non_empty_mapping_list(raw_allowed_claims):
        errors.append(issue("E_PAYLOAD_REQUIRED", "ClaimBoundaryMap.allowed_claims must be a non-empty list of mappings"))
        return
    if not allowed_claims:
        status = data.get("status")
        if isinstance(status, str) and status in {"committed", "stale"} and not data.get("candidate_for"):
            errors.append(issue("E_PAYLOAD_REQUIRED", "ClaimBoundaryMap.allowed_claims must be non-empty for committed/stale material"))
        return

    invalid_strength = False
    for idx, claim in enumerate(allowed_claims):
        if not isinstance(claim, dict):
            errors.append(issue("E_PAYLOAD_REQUIRED", f"allowed_claims[{idx}] must be a mapping"))
            continue
        if not is_non_empty_string(claim.get("id")):
            errors.append(issue("E_PAYLOAD_REQUIRED", f"allowed_claims[{idx}].id must be a non-empty string"))
        strength = claim.get("strength")
        if not isinstance(strength, str) or strength not in ALLOWED_CLAIM_STRENGTHS:
            invalid_strength = True
            errors.append(issue("E_CLAIM_STRENGTH_INVALID", f"allowed_claims[{idx}].strength is not bounded: {strength}"))

    valid_guardrails = False
    for field in ("forbidden_claims", "forbidden_wording", "forbidden_terms"):
        if _valid_guardrail_list(payload, field, errors):
            valid_guardrails = True
    if not invalid_strength and not valid_guardrails:
        errors.append(issue("E_FORBIDDEN_WORDING_REQUIRED", "ClaimBoundaryMap requires forbidden wording or forbidden claim guardrails"))


def _validate_reader_spine(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    if not is_non_empty_string_list(payload.get("questions")):
        errors.append(issue("E_READER_QUESTION_REQUIRED", "ReaderSpine.questions must be a non-empty list of strings"))


def _validate_material_payload(data: dict[str, Any], errors: list[ValidationIssue]) -> None:
    payload = _payload(data, errors)
    if payload is None:
        return
    material_type = data.get("material_type")
    if material_type == "EvidenceInventory":
        _validate_evidence_inventory(payload, errors)
    elif material_type == "ClaimBoundaryMap":
        _validate_claim_boundary_map(data, payload, errors)
    elif material_type == "ReaderSpine":
        _validate_reader_spine(payload, errors)
    elif material_type == "TerminologyRegister":
        return


def validate(data: Any) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    errors.extend(
        require_string_fields(
            data,
            ["schema_version", "material_id", "version", "status", "material_type"],
            "E_ENVELOPE_REQUIRED",
        )
    )
    if data.get("schema_version") and data.get("schema_version") != "ppg-material/v0.1":
        errors.append(issue("E_ENVELOPE_REQUIRED", "schema_version must be ppg-material/v0.1"))
    errors.extend(validate_runtime_status(data))
    _validate_material_payload(data, errors)
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_material.py <material.json|yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    return print_result(path, validate(data))


if __name__ == "__main__":
    raise SystemExit(main())
