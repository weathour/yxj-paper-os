#!/usr/bin/env python3
"""Shared dependency-free validation helpers for PPG runtime fixtures.

The YAML reader intentionally supports only the small fixture subset used by
this repository: indentation-based mappings, lists, list-of-maps, scalars, and
simple inline arrays. Unsupported syntax is a validation error, not a hidden
PyYAML fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


ALLOWED_RUNTIME_STATUSES = {
    "planned",
    "candidate",
    "validated",
    "committed",
    "stale",
    "rejected",
    "blocked",
    "owner_gated",
}

PAPER_FACING_STRING_FIELDS = {
    "caption_text",
    "claim_text",
    "draft_text",
    "paragraph",
    "summary_for_reader",
}

CONTROL_OR_REGISTRY_FIELDS = {
    "blocked_terms",
    "forbidden_terms",
    "forbidden_claims",
    "stale_terms",
    "validator_metadata",
    "provenance",
    "schema_version",
    "material_id",
    "material_type",
    "version",
    "status",
}

FORBIDDEN_PAPER_FACING_TERMS = (
    "autonomous route",
    "unregistered-external-route",
    "unregistered external route",
    "external orchestration concepts",
    "PUA governance",
    ".omx/",
    ".omx",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


def issue(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message)


def is_non_empty(value: Any) -> bool:
    return value not in (None, "", [], {})


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(is_non_empty_string(item) for item in value)


def is_non_empty_mapping_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, dict) for item in value)


def as_mapping(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def as_sequence(value: Any) -> list[Any] | None:
    return value if isinstance(value, list) else None


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for idx, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            if idx == 0 or line[idx - 1].isspace():
                return line[:idx].rstrip()
    return line.rstrip()


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""
    if value in {"{}", "[]"}:
        return {} if value == "{}" else []
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") or value.endswith("]"):
        if not (value.startswith("[") and value.endswith("]")):
            raise ValueError("unsupported or malformed inline array")
        body = value[1:-1].strip()
        if not body:
            return []
        if "[" in body or "]" in body or "{" in body or "}" in body:
            raise ValueError("nested inline structures are unsupported")
        return [_scalar(part.strip()) for part in body.split(",")]
    if value.startswith("{") or value.endswith("}"):
        raise ValueError("inline mappings are unsupported")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _prepare_yaml_lines(text: str) -> list[tuple[int, str, int]]:
    prepared: list[tuple[int, str, int]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw:
            raise ValueError(f"tab indentation is unsupported at line {lineno}")
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError(f"indentation must use multiples of two spaces at line {lineno}")
        prepared.append((indent, line.strip(), lineno))
    return prepared


def _parse_key_value(content: str, lineno: int) -> tuple[str, str | None]:
    if ":" not in content:
        raise ValueError(f"expected key/value mapping at line {lineno}")
    key, raw_value = content.split(":", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"empty mapping key at line {lineno}")
    raw_value = raw_value.strip()
    return key, raw_value if raw_value != "" else None


def _parse_block(lines: list[tuple[int, str, int]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    current_indent, content, _lineno = lines[index]
    if current_indent < indent:
        return {}, index
    if current_indent > indent:
        raise ValueError(f"unexpected indentation at line {lines[index][2]}")
    if content.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_map(lines: list[tuple[int, str, int]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        line_indent, content, lineno = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ValueError(f"unexpected nested mapping line at {lineno}")
        if content.startswith("- "):
            break
        key, raw_value = _parse_key_value(content, lineno)
        if raw_value is None:
            next_index = index + 1
            if next_index < len(lines) and lines[next_index][0] > indent:
                value, index = _parse_block(lines, next_index, lines[next_index][0])
                result[key] = value
                continue
            result[key] = None
            index += 1
        else:
            result[key] = _scalar(raw_value)
            index += 1
    return result, index


def _parse_list(lines: list[tuple[int, str, int]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        line_indent, content, lineno = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ValueError(f"unexpected nested list line at {lineno}")
        if not content.startswith("- "):
            break
        item_text = content[2:].strip()
        index += 1
        if not item_text:
            if index < len(lines) and lines[index][0] > indent:
                item, index = _parse_block(lines, index, lines[index][0])
                result.append(item)
            else:
                result.append(None)
            continue
        if ":" in item_text and not item_text.startswith(('"', "'")):
            key, raw_value = _parse_key_value(item_text, lineno)
            item_map: dict[str, Any] = {key: _scalar(raw_value) if raw_value is not None else None}
            if index < len(lines) and lines[index][0] > indent:
                continuation, index = _parse_map(lines, index, lines[index][0])
                item_map.update(continuation)
            result.append(item_map)
        else:
            result.append(_scalar(item_text))
            if index < len(lines) and lines[index][0] > indent:
                raise ValueError(f"scalar list item cannot have nested block at line {lines[index][2]}")
    return result, index


def load_document(path: Path) -> tuple[Any | None, list[ValidationIssue]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [issue("E_PARSE", f"cannot read fixture: {exc}")]

    try:
        if path.suffix.lower() == ".json":
            return json.loads(text), []
        lines = _prepare_yaml_lines(text)
        if not lines:
            return {}, []
        data, index = _parse_block(lines, 0, lines[0][0])
        if index != len(lines):
            raise ValueError(f"unparsed trailing content at line {lines[index][2]}")
        return data, []
    except Exception as exc:  # noqa: BLE001 - normalized as validation output
        return None, [issue("E_PARSE", str(exc))]


def require_mapping_document(data: Any) -> list[ValidationIssue]:
    if not isinstance(data, dict):
        return [issue("E_ENVELOPE_REQUIRED", "top-level document must be a mapping")]
    return []


def require_fields(data: dict[str, Any], fields: list[str], code: str = "E_ENVELOPE_REQUIRED") -> list[ValidationIssue]:
    return [issue(code, f"{field} is required") for field in fields if not is_non_empty(data.get(field))]


def require_string_fields(data: dict[str, Any], fields: list[str], code: str = "E_ENVELOPE_REQUIRED") -> list[ValidationIssue]:
    return [issue(code, f"{field} must be a non-empty string") for field in fields if not is_non_empty_string(data.get(field))]


def validate_runtime_status(data: dict[str, Any]) -> list[ValidationIssue]:
    status = data.get("status")
    if status is not None and (not isinstance(status, str) or status not in ALLOWED_RUNTIME_STATUSES):
        return [issue("E_STATUS_INVALID", f"status is outside runtime vocabulary: {status}")]
    return []


def _scan_text(value: str, path: str) -> list[ValidationIssue]:
    lowered = value.lower()
    findings: list[ValidationIssue] = []
    for term in FORBIDDEN_PAPER_FACING_TERMS:
        if term.lower() in lowered:
            findings.append(issue("E_TERMINOLOGY_LEAK", f"paper-facing text at {path} contains internal term: {term}"))
    return findings


def lint_paper_facing_terms(value: Any, path: str = "$", inherited_paper_facing: bool = False) -> list[ValidationIssue]:
    findings: list[ValidationIssue] = []
    if isinstance(value, dict):
        local_paper_facing = inherited_paper_facing or value.get("paper_facing") is True
        for key in sorted(value):
            child = value[key]
            child_path = f"{path}.{key}"
            if key in CONTROL_OR_REGISTRY_FIELDS and not local_paper_facing:
                continue
            key_paper_facing = local_paper_facing or key in PAPER_FACING_STRING_FIELDS
            findings.extend(lint_paper_facing_terms(child, child_path, key_paper_facing))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            findings.extend(lint_paper_facing_terms(child, f"{path}[{idx}]", inherited_paper_facing))
    elif isinstance(value, str) and inherited_paper_facing:
        findings.extend(_scan_text(value, path))
    return findings


def print_result(path: Path, errors: list[ValidationIssue]) -> int:
    if not errors:
        print(f"VALID {path}")
        return 0
    print(f"INVALID {path}")
    for validation_issue in errors:
        print(f"- {validation_issue.code}: {validation_issue.message}")
    return 1
