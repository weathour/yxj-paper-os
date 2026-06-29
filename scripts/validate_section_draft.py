#!/usr/bin/env python3
"""Validate Phase 7 packet-produced section draft markdown fixtures."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        issue,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        require_string_fields,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        issue,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        require_string_fields,
    )

REQUIRED_SOURCE_MATERIALS_BY_SECTION = {
    "intro": {"evidence_inventory_v1", "claim_boundary_map_v2", "reader_spine_v1"},
}
REQUIRED_EVIDENCE_ANCHORS_BY_SECTION = {
    "intro": {
        "examples/materials/evidence_inventory.v1.yaml",
        "examples/materials/claim_boundary_map.v2.yaml",
        "examples/materials/reader_spine.v1.yaml",
    },
}
FORBIDDEN_OVERCLAIM_PHRASES = (
    "guarantees universal safety",
    "guarantee universal safety",
    "universal safety guarantee",
    "universal safety under v2x authority loss",
    "always safe under v2x authority loss",
)
REQUIRED_BOUNDED_CLAIM_TERMS = ("bounded", "authority")


def _print_result(path: Path, errors: list[ValidationIssue]) -> int:
    if errors:
        print(f"INVALID {path}")
        for validation_issue in errors:
            print(f"- {validation_issue.code}: {validation_issue.message}")
        return 1
    print(f"VALID {path}")
    return 0


def _safe_repo_path(value: str) -> bool:
    if value.strip() != value or "\\" in value:
        return False
    if value.startswith("~") or (len(value) >= 2 and value[1] == ":"):
        return False
    parsed = PurePosixPath(value)
    if parsed.is_absolute():
        return False
    return not any(part in {"", ".", ".."} for part in value.split("/"))


def _split_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str, list[ValidationIssue]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, "", [issue("E_PARSE", f"cannot read section draft: {exc}")]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, [issue("E_SECTION_FRONTMATTER_REQUIRED", "section draft must start with YAML front matter delimiter ---")]
    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return None, text, [issue("E_SECTION_FRONTMATTER_REQUIRED", "section draft front matter closing delimiter is missing")]
    frontmatter_text = "\n".join(lines[1:closing_index]) + "\n"
    body = "\n".join(lines[closing_index + 1 :]).strip()
    tmp = path.with_suffix(path.suffix + ".frontmatter.tmp.yaml")
    try:
        tmp.write_text(frontmatter_text, encoding="utf-8")
        metadata, parse_errors = load_document(tmp)
    finally:
        tmp.unlink(missing_ok=True)
    if parse_errors:
        return None, body, parse_errors
    if not isinstance(metadata, dict):
        return None, body, [issue("E_SECTION_FRONTMATTER_REQUIRED", "section draft front matter must be a mapping")]
    return metadata, body, []


def validate(path: Path) -> list[ValidationIssue]:
    metadata, body, errors = _split_frontmatter(path)
    if errors:
        return errors
    assert isinstance(metadata, dict)

    errors.extend(require_string_fields(metadata, ["schema_version", "draft_id", "status", "section_id", "packet_id"], "E_SECTION_FIELD_REQUIRED"))
    if metadata.get("schema_version") and metadata.get("schema_version") != "ppg-section-draft/v0.1":
        errors.append(issue("E_SECTION_FIELD_REQUIRED", "schema_version must be ppg-section-draft/v0.1"))
    if metadata.get("status") and metadata.get("status") != "candidate":
        errors.append(issue("E_SECTION_STATUS_REQUIRED", "section draft status must be candidate"))
    if metadata.get("graph_completion_claimed") is not False:
        errors.append(issue("E_SECTION_COMPLETION_FORBIDDEN", "graph_completion_claimed must be false"))
    if metadata.get("recursive_dispatch_requested") is not False:
        errors.append(issue("E_SECTION_RECURSIVE_DISPATCH_FORBIDDEN", "recursive_dispatch_requested must be false"))

    source_materials = metadata.get("source_materials")
    if not is_non_empty_string_list(source_materials):
        errors.append(issue("E_SECTION_SOURCE_MATERIALS_REQUIRED", "source_materials must be a non-empty list of strings"))
        source_material_set: set[str] = set()
    else:
        source_material_set = {str(item) for item in source_materials}

    evidence_anchors = metadata.get("evidence_anchors")
    if not is_non_empty_string_list(evidence_anchors):
        errors.append(issue("E_SECTION_EVIDENCE_REQUIRED", "evidence_anchors must be a non-empty list of strings"))
        evidence_anchor_set: set[str] = set()
    else:
        evidence_anchor_set = {str(item) for item in evidence_anchors}
        for anchor in evidence_anchor_set:
            if not _safe_repo_path(anchor) or not anchor.startswith("examples/materials/"):
                errors.append(issue("E_SECTION_EVIDENCE_REQUIRED", f"evidence anchor must be a safe examples/materials path: {anchor}"))
            elif not Path(anchor).exists():
                errors.append(issue("E_SECTION_EVIDENCE_REQUIRED", f"evidence anchor does not exist: {anchor}"))

    section_id = str(metadata.get("section_id") or "")
    required_sources = REQUIRED_SOURCE_MATERIALS_BY_SECTION.get(section_id, set())
    missing_sources = sorted(required_sources - source_material_set)
    if missing_sources:
        errors.append(issue("E_SECTION_SOURCE_MATERIALS_REQUIRED", f"missing required source_materials for {section_id}: {', '.join(missing_sources)}"))
    required_anchors = REQUIRED_EVIDENCE_ANCHORS_BY_SECTION.get(section_id, set())
    missing_anchors = sorted(required_anchors - evidence_anchor_set)
    if missing_anchors:
        errors.append(issue("E_SECTION_EVIDENCE_REQUIRED", f"missing required evidence_anchors for {section_id}: {', '.join(missing_anchors)}"))

    if not is_non_empty_string(body):
        errors.append(issue("E_SECTION_BODY_REQUIRED", "section draft body must be non-empty"))
    lowered_body = body.lower()
    matched_overclaims = [phrase for phrase in FORBIDDEN_OVERCLAIM_PHRASES if phrase in lowered_body]
    if matched_overclaims:
        errors.append(issue("E_SECTION_FORBIDDEN_OVERCLAIM", f"section draft contains forbidden overclaim wording: {', '.join(matched_overclaims)}"))
    missing_terms = [term for term in REQUIRED_BOUNDED_CLAIM_TERMS if term not in lowered_body]
    if section_id == "intro" and missing_terms:
        errors.append(issue("E_SECTION_BOUNDED_CLAIM_REQUIRED", f"intro draft must preserve bounded authority framing; missing: {', '.join(missing_terms)}"))

    lint_payload = dict(metadata)
    lint_payload["draft_text"] = body
    errors.extend(lint_paper_facing_terms(lint_payload))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_section_draft.py <section-draft.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    return _print_result(path, validate(path))


if __name__ == "__main__":
    raise SystemExit(main())
