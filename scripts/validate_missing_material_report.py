#!/usr/bin/env python3
"""Validate Phase 6 MissingMaterialReport fixtures."""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
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
        issue,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
    )

ALLOWED_REPORT_FIELDS = {
    "schema_version",
    "report_id",
    "status",
    "packet_id",
    "missing_materials",
    "reason",
    "controller_action",
    "completion_forbidden",
    "no_recursive_orchestration",
}


def validate(data: Any) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    unknown_fields = sorted(set(data) - ALLOWED_REPORT_FIELDS)
    if unknown_fields:
        errors.append(issue("E_REPORT_UNKNOWN_FIELD", f"unknown MissingMaterialReport fields are not allowed: {', '.join(unknown_fields)}"))
    errors.extend(require_string_fields(data, ["schema_version", "report_id", "status", "packet_id", "reason", "controller_action"], "E_REPORT_FIELD_REQUIRED"))
    if data.get("schema_version") and data.get("schema_version") != "ppg-missing-material-report/v0.1":
        errors.append(issue("E_REPORT_FIELD_REQUIRED", "schema_version must be ppg-missing-material-report/v0.1"))
    if data.get("status") != "blocked":
        errors.append(issue("E_REPORT_STATUS_REQUIRED", "status must be blocked"))
    if not is_non_empty_string_list(data.get("missing_materials")):
        errors.append(issue("E_REPORT_MISSING_MATERIALS_REQUIRED", "missing_materials must be a non-empty list of strings"))
    if data.get("completion_forbidden") is not True:
        errors.append(issue("E_REPORT_COMPLETION_FORBIDDEN_REQUIRED", "completion_forbidden must be literal true"))
    if data.get("no_recursive_orchestration") is not True:
        errors.append(issue("E_REPORT_NO_RECURSIVE_ORCHESTRATION_REQUIRED", "no_recursive_orchestration must be literal true"))
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_missing_material_report.py <report.json|yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    return print_result(path, validate(data))


if __name__ == "__main__":
    raise SystemExit(main())
