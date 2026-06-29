#!/usr/bin/env python3
"""Validate Phase 4 BackflowTask fixtures."""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        issue,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        issue,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )


def validate(data: Any) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    errors.extend(require_string_fields(data, ["schema_version", "backflow_id", "finding_id", "status"], "E_ENVELOPE_REQUIRED"))
    if data.get("schema_version") and data.get("schema_version") != "ppg-backflow-task/v0.1":
        errors.append(issue("E_ENVELOPE_REQUIRED", "schema_version must be ppg-backflow-task/v0.1"))
    errors.extend(validate_runtime_status(data))
    errors.extend(require_string_fields(data, ["target"], "E_BACKFLOW_TARGET_REQUIRED"))
    errors.extend(require_string_fields(data, ["action"], "E_BACKFLOW_ACTION_REQUIRED"))
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_backflow.py <backflow-task.json|yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    return print_result(path, validate(data))


if __name__ == "__main__":
    raise SystemExit(main())
