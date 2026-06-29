#!/usr/bin/env python3
"""Validate Phase 4 ReviewClosure and DeliveryGate fixtures."""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        as_sequence,
        issue,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        as_sequence,
        issue,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
    )


REVIEW_CLOSURE_STATUSES = {"validated", "committed", "blocked", "rejected"}
DELIVERY_GATE_STATUSES = {"pass", "fail", "blocked"}


def _validate_review_closure(data: dict[str, Any]) -> list[ValidationIssue]:
    errors = require_string_fields(data, ["schema_version", "closure_id", "status"], "E_ENVELOPE_REQUIRED")
    status = data.get("status")
    if status is not None and (not isinstance(status, str) or status not in REVIEW_CLOSURE_STATUSES):
        errors.append(issue("E_STATUS_INVALID", f"ReviewClosure.status is invalid: {status}"))
    errors.extend(require_string_fields(data, ["finding_id"], "E_CLOSURE_FINDING_REQUIRED"))
    if not is_non_empty_string_list(data.get("evidence")):
        errors.append(issue("E_CLOSURE_FINDING_REQUIRED", "review closure requires non-empty string evidence list"))
    return errors


def _validate_delivery_gate(data: dict[str, Any]) -> list[ValidationIssue]:
    errors = require_string_fields(data, ["schema_version", "gate_id", "status"], "E_ENVELOPE_REQUIRED")
    status = data.get("status")
    if status is not None and (not isinstance(status, str) or status not in DELIVERY_GATE_STATUSES):
        errors.append(issue("E_STATUS_INVALID", f"DeliveryGate.status is invalid: {status}"))
    raw_blockers = data.get("unresolved_blockers")
    blockers = as_sequence(raw_blockers)
    if raw_blockers is not None:
        if blockers is None or any(not isinstance(item, str) or not item for item in blockers):
            errors.append(issue("E_PAYLOAD_REQUIRED", "unresolved_blockers must be a list of non-empty strings when present"))
            blockers = []
    if status == "pass" and blockers:
        errors.append(issue("E_DELIVERY_GATE_BLOCKER", "delivery gate cannot pass with unresolved blockers"))
    closures = data.get("closures")
    if closures is not None and not is_non_empty_string_list(closures):
        errors.append(issue("E_PAYLOAD_REQUIRED", "closures must be a non-empty string list when present"))
    return errors


def validate(data: Any) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    schema_version = data.get("schema_version")
    if schema_version == "ppg-review-closure/v0.1":
        errors.extend(_validate_review_closure(data))
    elif schema_version == "ppg-delivery-gate/v0.1":
        errors.extend(_validate_delivery_gate(data))
    else:
        errors.append(issue("E_ENVELOPE_REQUIRED", "schema_version must be ppg-review-closure/v0.1 or ppg-delivery-gate/v0.1"))
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_delivery_gate.py <review-closure-or-delivery-gate.json|yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    return print_result(path, validate(data))


if __name__ == "__main__":
    raise SystemExit(main())
