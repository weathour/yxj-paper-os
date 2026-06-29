#!/usr/bin/env python3
"""Validate Phase 4 TaskPacket / writing packet fixtures."""
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
        validate_runtime_status,
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
        validate_runtime_status,
    )


def validate(data: Any) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    errors.extend(require_string_fields(data, ["schema_version", "packet_id", "status", "mission"], "E_ENVELOPE_REQUIRED"))
    if data.get("schema_version") and data.get("schema_version") != "ppg-task-packet/v0.1":
        errors.append(issue("E_ENVELOPE_REQUIRED", "schema_version must be ppg-task-packet/v0.1"))
    errors.extend(validate_runtime_status(data))
    if not is_non_empty_string_list(data.get("input_materials")):
        errors.append(issue("E_TASK_INPUTS_REQUIRED", "input_materials must be a non-empty list of string material handles"))
    errors.extend(require_string_fields(data, ["expected_output_schema"], "E_TASK_OUTPUT_SCHEMA_REQUIRED"))
    validators = data.get("validators")
    if validators is not None and not is_non_empty_string_list(validators):
        errors.append(issue("E_PAYLOAD_REQUIRED", "validators must be a non-empty list of string handles when present"))
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_packet.py <task-packet.json|yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    return print_result(path, validate(data))


if __name__ == "__main__":
    raise SystemExit(main())
