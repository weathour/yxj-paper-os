#!/usr/bin/env python3
"""Dependency-free mechanical validator for yxj-paper-os schema-0.3 packs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable

from template_design_contract import (
    ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION,
    FOUR_GATES,
    validate_template_rule,
)
from verify_semantic_dossier import validate_semantic_dossier

REQUIRED_FILES = [
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
]
DIMENSION_INDEX = REQUIRED_FILES[0]
FINAL_PACK = REQUIRED_FILES[-1]
REQUIRED_DIMENSION_IDS = [f"D{i:02d}" for i in range(20)]
DIMENSION_COLUMNS = [
    "ID",
    "Dimension",
    "Current home",
    "Status",
    "Reason / owner note",
    "Pointer or handoff",
    "Blocks design pack?",
]
VALID_DIMENSION_STATUSES = {
    "filled",
    "not_applicable",
    "absent",
    "deferred",
    "rejected",
}
VALID_BLOCKS_VALUES = {"yes", "no"}
REQUIRED_HEADINGS = {name: [] for name in REQUIRED_FILES}

WRITING_SCOPE_COLUMNS = [
    "Scope ID",
    "Writing surface",
    "Intended output",
    "Readiness",
    "Available inputs",
    "Required requirement IDs",
    "Remaining blocker",
    "Next action",
    "Output pointer",
]
LENS_COLUMNS = ["Lens ID", "Activation basis", "Affected scopes"]
REQUIREMENT_COLUMNS = [
    "Requirement ID",
    "Lens ID",
    "Requirement",
    "Affected scopes",
    "Handling",
    "Evidence / decision pointer",
]
DEPENDENCY_COLUMNS = [
    "Changed record",
    "Affected D IDs / scopes",
    "Disposition",
    "Resolution or next action",
]
DECISION_COLUMNS = [
    "Decision ID",
    "Gate category",
    "Issue / options / decision",
    "Affected scopes",
    "Origin",
    "Resolution",
    "Grounding / owner-answer pointer",
    "Recheck trigger",
]
MATERIAL_COLUMNS = [
    "Record ID",
    "Kind",
    "Content / role",
    "Locator",
    "Scope / conditions",
    "Status",
    "Origin",
    "Resolution",
    "Grounding",
]
TEMPLATE_SOURCE_COLUMNS = [
    "Template source ID",
    "Design role",
    "Design question",
    "Source/provenance pointer",
    "Access state",
    "Local derivative pointer",
    "Source SHA-256",
    "Hidden dossier pointer",
    "Design-only state",
    "Scientific-source promotion pointer",
]
CLAIM_COLUMNS = [
    "Claim ID",
    "Claim",
    "Evidence record IDs",
    "Warrant / support relation",
    "Scope / conditions",
    "Directness",
    "Uncertainty / counterevidence",
    "Allowed wording",
    "Forbidden wording",
    "Status",
    "Origin",
    "Support",
    "Resolution",
    "Grounding",
]
SECTION_COLUMNS = [
    "Section ID",
    "Scope ID",
    "Sequence",
    "Job",
    "Reader state in",
    "Reader state out",
    "Input IDs",
    "Output promise",
    "Evidence/visual obligations",
    "Forbidden content",
]
PARAGRAPH_COLUMNS = [
    "Paragraph ID",
    "Scope ID",
    "Section ID",
    "Sequence",
    "Function/job",
    "Reader state in",
    "Reader state out",
    "Previous paragraph",
    "Next paragraph",
]
PAYLOAD_COLUMNS = [
    "Paragraph ID",
    "Claim IDs",
    "Material/source/evidence IDs",
    "Claim/citation boundary rationale",
    "Citation function",
    "Equation/algorithm/visual/table record IDs",
    "Object relation/job",
    "Required qualification/limitation",
    "Output promise",
    "Forbidden content/overclaim",
    "Template rule IDs",
]
IMPORTANT_COLUMNS = [
    "Paragraph ID",
    "Qualitative selection rationale",
    "Consequence/risk/dependency",
    "Frame IDs",
    "Gate category",
    "Decision ID",
    "Gate resolution",
    "Owner-answer/grounding pointer",
]
FRAME_COLUMNS = [
    "Frame ID",
    "Paragraph ID",
    "Order",
    "Sentence function",
    "Proposition/content target",
    "Clause/relation order",
    "Required payload IDs",
    "Payload/boundary rationale",
    "Language contract IDs",
    "Local language constraint",
    "Previous frame",
    "Next frame",
    "Forbidden realization",
]
LANGUAGE_COLUMNS = [
    "Contract ID",
    "Scope ID",
    "Surface",
    "Terminology",
    "Claim/verb strength",
    "Hedge/modality",
    "Tense/voice",
    "Syntax/rhythm tendency",
    "Forbidden patterns",
    "Grounding IDs",
]
VISUAL_COLUMNS = [
    "Visual ID",
    "Scope ID",
    "Paragraph IDs",
    "Status",
    "Evidence/data IDs",
    "Story role",
    "Panel/order/encoding",
    "Caption/legend job",
    "Body callout relation",
    "Accessibility responsibility",
    "Handoff/blocker",
]
EDGE_COLUMNS = [
    "Edge ID",
    "From record",
    "Relation",
    "To record",
    "Closure surface",
    "State/freshness",
    "Consequence if stale",
]
RULE_COLUMNS = [
    "Rule ID",
    "Grounding kind",
    "Grounding pointer(s)",
    "Rule kind",
    "Affected scope IDs",
    "Surface",
    "Candidate transfer",
    "Suggested disposition",
    "Origin",
    "Resolution",
    "Disposition",
    "Decision ID",
    "Limitation",
    "Freshness",
]
BUDGET_COLUMNS = [
    "Budget ID",
    "Scope ID",
    "Surface",
    "Property",
    "Basis kind",
    "Grounding pointer",
    "Soft band or ordering",
    "Disposition",
    "Adaptation rationale",
    "Hard-constraint disclaimer",
]
WRITING_PLAN_COLUMNS = [
    "Scope ID",
    "Reader / section job",
    "Input record IDs",
    "Output responsibility",
    "Drafting boundary",
    "Output pointer",
]
COVERAGE_COLUMNS = [
    "Surface",
    "Scope ID",
    "Handling (`satisfied&#124;not_applicable`)",
    "Record count",
    "Authoritative pointer",
    "Rationale/blocker",
]
AUTHORITY_COLUMNS = ["Authority", "Required pointer", "Compiler note"]
SUMMARY_COLUMNS = [
    "Scope ID",
    "Section count",
    "Paragraph count",
    "Important paragraph count",
    "Frame count",
    "Language count",
    "Visual count",
    "Edge count",
    "Rule count",
    "Budget count",
]
TEMPLATE_HANDLING_COLUMNS = [
    "Scope ID",
    "Mode",
    "Semantic dossier pointer",
    "Quantitative analysis pointer(s)",
    "Generic fallback pointer(s)",
    "Firewall state",
    "Rationale",
    "Active blocker IDs",
]
OWNER_GATE_SUMMARY_COLUMNS = [
    "Scope ID",
    "Gate category",
    "Decision ID",
    "Resolution",
    "Grounding / owner-answer pointer",
    "Active blocker IDs",
]
UNRESOLVED_COLUMNS = [
    "Scope ID",
    "Unresolved/stale/deferred record IDs",
    "Consequence",
    "Downstream prohibition",
]
HANDOFF_COLUMNS = [
    "Scope ID",
    "00 scope-row pointer",
    "Detailed coverage pointer",
    "Output pointer",
    "Active blocker IDs",
    "Downstream prohibitions",
    "Handoff note",
]

TABLE_CONTRACTS = {
    (DIMENSION_INDEX, "Writing Scopes"): WRITING_SCOPE_COLUMNS,
    (DIMENSION_INDEX, "Active Calibration Lenses"): LENS_COLUMNS,
    (DIMENSION_INDEX, "Conditional Requirements"): REQUIREMENT_COLUMNS,
    (DIMENSION_INDEX, "Dependency Recheck"): DEPENDENCY_COLUMNS,
    ("00_PROJECT_ROUTE.md", "Decision Records"): DECISION_COLUMNS,
    ("01_MATERIALS_INVENTORY.md", "Material Records"): MATERIAL_COLUMNS,
    ("01_MATERIALS_INVENTORY.md", "Template Design Sources"): TEMPLATE_SOURCE_COLUMNS,
    ("02_CLAIM_EVIDENCE_BOUNDARY.md", "Claim Records"): CLAIM_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Section Map"): SECTION_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Paragraph Map"): PARAGRAPH_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Paragraph Payload and Boundary Map"): PAYLOAD_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Important Paragraph Register"): IMPORTANT_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Controlled Sentence Frames"): FRAME_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Surface Language Contract"): LANGUAGE_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Visual Blueprint"): VISUAL_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Cross-Surface Traceability"): EDGE_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Template Rule Projection"): RULE_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Grounded Soft Budgets"): BUDGET_COLUMNS,
    ("03_WRITING_STRUCTURE.md", "Scoped Writing Plan"): WRITING_PLAN_COLUMNS,
    (FINAL_PACK, "Authority Pointers"): AUTHORITY_COLUMNS,
    (FINAL_PACK, "Detailed Surface Coverage"): COVERAGE_COLUMNS,
    (FINAL_PACK, "Detailed Coverage Summary"): SUMMARY_COLUMNS,
    (FINAL_PACK, "Owner Gate Resolution Summary"): OWNER_GATE_SUMMARY_COLUMNS,
    (FINAL_PACK, "Template Analysis Handling"): TEMPLATE_HANDLING_COLUMNS,
    (FINAL_PACK, "Unresolved and Downstream Prohibitions"): UNRESOLVED_COLUMNS,
    (FINAL_PACK, "Scoped Handoff"): HANDOFF_COLUMNS,
}
# Retained for callers that treated the old public constant as a table registry.
SPARSE_TABLES = {
    key: value
    for key, value in TABLE_CONTRACTS.items()
    if key[1]
    in {
        "Writing Scopes",
        "Active Calibration Lenses",
        "Conditional Requirements",
        "Dependency Recheck",
        "Decision Records",
        "Material Records",
        "Claim Records",
        "Scoped Writing Plan",
        "Scoped Handoff",
    }
}

READINESS = {"writer-ready", "partial", "blocked", "deferred"}
REQ_STATE = {"satisfied", "blocked", "deferred", "not_applicable"}
DISPOSITION = {
    "current",
    "rechecked",
    "stale",
    "candidate",
    "blocked",
    "not_applicable",
}
EDGE_STATES = {"current", "rechecked", "candidate", "stale", "unavailable", "blocked"}
MATERIAL_STATUS = {"available", "partial", "planned", "unavailable", "rejected"}
CLAIM_STATUS = {"active", "downgraded", "deferred", "rejected"}
ORIGIN = {"artifact-observed", "owner-stated", "model-derived", "model-proposed"}
SUPPORT = {
    "evidence-supported",
    "evidence-partial",
    "evidence-unsupported",
    "not_applicable",
}
RESOLUTION = {"confirmed", "candidate", "unresolved", "conflicted", "rejected"}
LENS_IDS = {
    "method-algorithm",
    "system-software",
    "benchmark-dataset-resource",
    "empirical-application",
    "survey-review",
    "theory-formal",
    "human-study-mixed-methods",
    "research-design-validity",
    "evidence-results-statistics",
    "literature-differentiation",
    "reproducibility-governance",
    "argument-language-visual",
    "venue-template",
}
GATE_CATEGORIES = FOUR_GATES | {"not_applicable"}
EDGE_RELATIONS = {
    "fulfills",
    "qualifies",
    "limits",
    "introduces",
    "calls_out",
    "visualizes",
    "depends_on",
    "contrasts_with",
    "hands_off_to",
}
CANONICAL_SURFACES = {
    "section_paragraph_map",
    "surface_language_contract",
    "visual_caption_blueprint",
    "cross_surface_traceability",
    "template_rule_provenance",
    "soft_budgets",
    "important_paragraph_frames",
}
TEMPLATE_MODES = {
    "semantic_primary",
    "semantic_plus_quantitative",
    "quantitative_only",
    "generic_fallback",
    "not_applicable",
}
ID_PREFIXES = (
    "SCOPE",
    "REQ",
    "DEC",
    "M",
    "C",
    "TPL",
    "TRULE",
    "SEC",
    "PAR",
    "FRM",
    "LANG",
    "VIS",
    "EDGE",
    "BUD",
)
ID_RE = re.compile(rf"^(?:{'|'.join(ID_PREFIXES)})-[a-z0-9]+(?:-[a-z0-9]+)*$")
D_RE = re.compile(r"^D(?:0[0-9]|1[0-9])$")
SCHEMA_VALUE_RE = re.compile(r"^[0-9]+\.[0-9]+$")
SCHEMA_MARKER_RE = re.compile(r"^\s*-\s*Workspace schema version:\s*(.*?)\s*$", re.M)
PLACEHOLDER_RE = re.compile(r"(?i)(?:^|\b)(?:TODO|TBD|UNKNOWN|REPLACE_ME)(?:\b|$)")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOSSIER_POINTER_RE = re.compile(
    r"^\.yxj-paper-os/template-analysis/semantic-dossier\.json#(?:TPL|TOBS|TRULE)-[a-z0-9]+(?:-[a-z0-9]+)*$"
)
QUANT_POINTER_RE = re.compile(
    r"^\.yxj-paper-os/template-analysis/([a-z0-9-]+\.(?:json|jsonl))#(.+)$"
)
GENERIC_POINTER_RE = re.compile(r"^lens:[a-z0-9]+(?:-[a-z0-9]+)*#[a-z0-9-]+$")
FREE_POINTER_TOKEN_RE = re.compile(r"^[^;\r\n]+$")
READINESS_CLAIM_RE = re.compile(
    r"(?ix)(?:"
    r"\bwriter-ready\b"
    r"|^\s*(?:partial|blocked|deferred)\s*$"
    r"|\b(?:scope|readiness|status)\b.{0,48}?(?:"
    r"(?:is|remains|stays|equals|continues\s+as|has\s+status|:)"
    r"(?:\s+(?:still|currently|in\s+a|a))*\s+(?:partial|blocked|deferred)(?:\s+state)?\b"
    r")"
    r")"
)
FINITE_PROPOSITION_RE = re.compile(
    r"(?ix)^\s*(?:the|this|these|those|we|our\s+[a-z0-9_-]+|"
    r"evidence|results?|analysis|method|figure\s+[a-z0-9_-]+|"
    r"table\s+[a-z0-9_-]+)\b.{0,160}\b(?:is|are|was|were|"
    r"shows?|establish(?:es|ed)?|demonstrates?|improves?|supports?|"
    r"indicates?|reveals?|provides?|confirms?)\b"
)
ANALYZER_SCHEMAS = {
    "metric-registry.json": "template-metric-registry/1.0",
    "paper-metrics.jsonl": "template-paper-metrics/1.0",
    "objects.jsonl": "template-object/1.0",
    "corpus-summary.json": "template-corpus-summary/1.0",
    "design-profile.json": "template-design-profile/1.0",
    "extraction-warnings.json": "template-extraction-warnings/1.0",
}
ANALYZER_GROUNDING_OUTPUTS = {"design-profile.json", "paper-metrics.jsonl"}


def _looks_like_realized_prose(value: str) -> bool:
    """Conservatively flag realized prose without turning design notes into errors."""

    text = value.strip()
    if not text or PLACEHOLDER_RE.search(text) or ("[" in text and "]" in text):
        return False
    sentence_marks = len(re.findall(r"[.!?。！？]", text))
    return bool(
        re.search(r"[.!?。！？]\s*$", text)
        or FINITE_PROPOSITION_RE.search(text)
        or sentence_marks >= 2
    )


AUTHORITATIVE_DETAIL_HEADINGS = {
    "Section Map",
    "Paragraph Map",
    "Paragraph Payload and Boundary Map",
    "Important Paragraph Register",
    "Controlled Sentence Frames",
    "Surface Language Contract",
    "Visual Blueprint",
    "Cross-Surface Traceability",
    "Template Rule Projection",
    "Grounded Soft Budgets",
}
REQUIRED_04_HEADINGS = {
    "Authority Pointers",
    "Detailed Surface Coverage",
    "Detailed Coverage Summary",
    "Owner Gate Resolution Summary",
    "Template Analysis Handling",
    "Template Source Firewall",
    "Unresolved and Downstream Prohibitions",
    "Scoped Handoff",
}


@dataclass(frozen=True)
class ValidationReport:
    errors: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class CanonicalReference:
    kind: str
    target: str | Path
    fragment: str = ""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def has_placeholder(text: str) -> bool:
    return bool(PLACEHOLDER_RE.search(text))


def level_two_heading_slugs(text: str) -> dict[str, str]:
    return {
        slugify(match.group(1)): match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.M)
    }


def section_content(text: str, heading: str) -> str | None:
    wanted = slugify(heading)
    for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.M):
        if slugify(match.group(1)) != wanted:
            continue
        tail = text[match.end() :]
        next_heading = re.search(r"^##\s+", tail, re.M)
        return tail[: next_heading.start()] if next_heading else tail
    return None


def _heading_cardinality(text: str, heading: str) -> int:
    wanted = slugify(heading)
    return sum(
        slugify(match.group(1)) == wanted
        for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.M)
    )


def parse_anchor(
    value: str, contents: dict[str, str] | None = None
) -> tuple[str, str, str | None]:
    if "#" not in value:
        return "", "", "pointer must use file#heading syntax"
    name, anchor = value.split("#", 1)
    if not name:
        return name, slugify(anchor), "pointer file name is missing"
    normalized = slugify(anchor)
    if not normalized:
        return name, normalized, "pointer heading is missing"
    if contents is not None and name in contents:
        if normalized not in level_two_heading_slugs(contents[name]):
            return name, normalized, "pointer heading does not resolve"
    return name, normalized, None


def first_present(*values):
    if (
        len(values) == 2
        and isinstance(values[1], (list, tuple))
        and isinstance(values[0], dict)
    ):
        return (
            next(
                (
                    values[0].get(key)
                    for key in values[1]
                    if values[0].get(key) not in (None, "")
                ),
                "",
            )
            or ""
        )
    return next((value for value in values if value not in (None, "")), "")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_divider(line: str) -> bool:
    cells = _cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _table(text: str, heading: str) -> tuple[list[str] | None, list[list[str]]]:
    section = section_content(text, heading)
    if section is None:
        return None, []
    lines = [
        line.strip() for line in section.splitlines() if line.strip().startswith("|")
    ]
    if len(lines) < 2:
        return None, []
    header = _cells(lines[0])
    rows = [_cells(line) for line in lines[1:] if not _is_divider(line)]
    return header, rows


def parse_first_table(text: str, heading: str):
    header, rows = _table(text, heading)
    header = header or []
    return header, [dict(zip(header, row)) for row in rows if len(row) == len(header)]


def _diagnostic(code: str, message: str) -> str:
    return f"{code}: {message}"


def _substantive(value: str) -> bool:
    stripped = value.strip()
    return (
        bool(stripped) and stripped.lower() != "none" and not has_placeholder(stripped)
    )


def _schema_diagnostic(index_text: str | None) -> str | None:
    if index_text is None:
        return _diagnostic(
            "SCHEMA_MISSING", "00_DIMENSION_INDEX.md or its schema marker is missing"
        )
    matches = SCHEMA_MARKER_RE.findall(index_text)
    mentions = re.findall(r"(?i)Workspace schema version\s*:", index_text)
    if not matches and not mentions:
        return _diagnostic(
            "SCHEMA_MISSING", "Workspace schema version marker is missing"
        )
    if len(matches) != 1 or len(mentions) != 1:
        return _diagnostic("SCHEMA_INVALID", "schema marker must appear exactly once")
    version = matches[0].strip()
    if not SCHEMA_VALUE_RE.fullmatch(version):
        return _diagnostic(
            "SCHEMA_INVALID", f"malformed workspace schema version {version!r}"
        )
    if version == "0.2":
        return _diagnostic(
            "SCHEMA_LEGACY_02",
            "schema 0.2 requires non-destructive detailed recompilation before writer-ready may be current",
        )
    if version != "0.3":
        return _diagnostic(
            "SCHEMA_UNSUPPORTED", f"unsupported workspace schema {version}"
        )
    return None


def _parse_table(
    contents: dict[str, str],
    filename: str,
    heading: str,
    expected: list[str],
    errors: list[str],
) -> list[dict[str, str]]:
    header, raw_rows = _table(contents.get(filename, ""), heading)
    if header is None:
        errors.append(_diagnostic("TABLE_CONTRACT", f"{filename}#{heading} is missing"))
        return []
    if heading == "Scoped Handoff" and "Readiness" in header:
        errors.append(
            _diagnostic(
                "HANDOFF_READINESS_DUPLICATED",
                f"{filename}#{heading} must not copy readiness",
            )
        )
    if header != expected:
        code = (
            "HANDOFF_READINESS_DUPLICATED"
            if heading == "Scoped Handoff" and "Readiness" in header
            else "TABLE_CONTRACT"
        )
        errors.append(
            _diagnostic(
                code,
                f"{filename}#{heading} columns must be exactly: {' | '.join(expected)}",
            )
        )
        return []
    rows: list[dict[str, str]] = []
    for index, raw in enumerate(raw_rows, 1):
        if len(raw) != len(expected):
            errors.append(
                _diagnostic(
                    "TABLE_CONTRACT",
                    f"{filename}#{heading} row {index} has {len(raw)} cells; expected {len(expected)}",
                )
            )
            continue
        if any(not cell or has_placeholder(cell) for cell in raw):
            errors.append(
                _diagnostic(
                    "PLACEHOLDER",
                    f"{filename}#{heading} row {index} contains blank or unresolved placeholder",
                )
            )
        rows.append(dict(zip(expected, raw)))
    return rows


def _public_pointer(value: str, contents: dict[str, str]) -> bool:
    if "#" not in value:
        return False
    filename, heading = value.split("#", 1)
    return (
        filename in contents
        and bool(slugify(heading))
        and _heading_cardinality(contents[filename], heading) == 1
        and slugify(heading) in level_two_heading_slugs(contents[filename])
    )


def _has_ascii_control(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def _reference_grammar(
    value: str,
    allow_none: bool = True,
) -> bool:
    if _has_ascii_control(value):
        return False
    if value == "none":
        return allow_none
    if ID_RE.fullmatch(value) or D_RE.fullmatch(value):
        return True
    if value.startswith("path:"):
        path_text = value[5:].split("#", 1)[0]
        pure = PurePosixPath(path_text)
        return (
            bool(path_text)
            and "\\" not in path_text
            and not pure.is_absolute()
            and ".." not in pure.parts
        )
    if "#" not in value:
        return False
    filename, heading = value.split("#", 1)
    return filename in REQUIRED_FILES and bool(slugify(heading))


def _canonical_reference(
    value: str,
    *,
    workspace: Path,
    contents: dict[str, str],
    owned_ids: set[str],
    allow_raw_contained_path: bool = False,
) -> CanonicalReference | None:
    """Return canonical target identity without conflating aliases with roles."""

    if not value or value == "none" or _has_ascii_control(value):
        return None
    if ID_RE.fullmatch(value) or D_RE.fullmatch(value):
        if value not in owned_ids:
            return None
        prefix = "dimension" if D_RE.fullmatch(value) else value.split("-", 1)[0]
        return CanonicalReference("record", value, prefix)
    dossier = DOSSIER_POINTER_RE.fullmatch(value)
    if dossier:
        return CanonicalReference(
            "dossier", "semantic-dossier.json", value.rsplit("#", 1)[-1]
        )
    analyzer = QUANT_POINTER_RE.fullmatch(value)
    if analyzer:
        return CanonicalReference("analyzer", analyzer.group(1), analyzer.group(2))
    lens = GENERIC_POINTER_RE.fullmatch(value)
    if lens:
        lens_id, heading = value[5:].split("#", 1)
        return CanonicalReference("lens", lens_id, slugify(heading))
    if value.startswith("path:"):
        path_value = value[5:].split("#", 1)[0]
        resolved = _contained_file(workspace, path_value)
        return CanonicalReference("path", resolved) if resolved is not None else None
    if _public_pointer(value, contents):
        filename, heading = value.split("#", 1)
        return CanonicalReference("public", filename, slugify(heading))
    if allow_raw_contained_path:
        resolved = _contained_file(workspace, value)
        return CanonicalReference("path", resolved) if resolved is not None else None
    return None


def _resolve_reference(
    value: str,
    *,
    workspace: Path,
    contents: dict[str, str],
    owned_ids: set[str],
    allow_none: bool,
) -> bool:
    """Resolve one public/path/record pointer without conflating syntax and existence."""
    if not _reference_grammar(value, allow_none):
        return False
    if value == "none":
        return allow_none
    return (
        _canonical_reference(
            value,
            workspace=workspace,
            contents=contents,
            owned_ids=owned_ids,
        )
        is not None
    )


def _typed_list(
    value: str,
    patterns: Iterable[re.Pattern[str]],
    *,
    allow_none: bool,
) -> tuple[list[str], str | None]:
    if value == "none":
        return ([], None) if allow_none else ([], "none is forbidden")
    if not value or value.startswith(";") or value.endswith(";") or ";;" in value:
        return [], "typed list has invalid semicolon grammar"
    tokens = [token.strip() for token in value.split(";")]
    if any(not token or token == "none" for token in tokens):
        return [], "none cannot be combined with IDs"
    if len(tokens) != len(set(tokens)):
        return tokens, "typed list contains duplicate IDs"
    allowed = tuple(patterns)
    if any(
        not any(pattern.fullmatch(token) for pattern in allowed) for token in tokens
    ):
        return tokens, "typed list contains an out-of-domain value"
    return tokens, None


def _id_pattern(*prefixes: str) -> re.Pattern[str]:
    return re.compile(
        rf"^(?:{'|'.join(map(re.escape, prefixes))})-[a-z0-9]+(?:-[a-z0-9]+)*$"
    )


def _contained_file(workspace: Path, value: str) -> Path | None:
    if not value or "\\" in value or _has_ascii_control(value):
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    candidate = workspace / pure
    try:
        resolved = candidate.resolve(strict=True)
        root = workspace.resolve(strict=True)
    except (OSError, ValueError):
        return None
    if candidate.is_symlink() or root not in resolved.parents or not resolved.is_file():
        return None
    return resolved


def _source_pointer_valid(workspace: Path, value: str) -> bool:
    if _has_ascii_control(value):
        return False
    if re.fullmatch(r"[a-z][a-z0-9+.-]*://\S+", value, re.I):
        return True
    if re.fullmatch(r"(?:doi|urn|isbn):\S+", value, re.I):
        return True
    return _contained_file(workspace, value) is not None


def _row_counts(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key, "")
        counts[value] = counts.get(value, 0) + 1
    return counts


def _unique_ids(
    rows: list[dict[str, str]],
    column: str,
    pattern: re.Pattern[str],
    code: str,
    errors: list[str],
) -> dict[str, dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        record_id = row.get(column, "")
        if not pattern.fullmatch(record_id):
            errors.append(_diagnostic(code, f"invalid {column} {record_id!r}"))
        elif record_id in by_id:
            errors.append(_diagnostic(code, f"duplicate {column} {record_id}"))
        else:
            by_id[record_id] = row
    return by_id


def _validate_dimension_index(text: str, errors: list[str]) -> None:
    header, rows = _table(text, "Dimension Status Index")
    if header != DIMENSION_COLUMNS:
        errors.append(
            _diagnostic(
                "DIMENSION_INDEX", "00_DIMENSION_INDEX.md public index columns changed"
            )
        )
        return
    seen: list[str] = []
    for row in rows:
        if len(row) != len(DIMENSION_COLUMNS):
            errors.append(
                _diagnostic("DIMENSION_INDEX", "dimension row has wrong cell count")
            )
            continue
        seen.append(row[0])
        if row[3] not in VALID_DIMENSION_STATUSES:
            errors.append(
                _diagnostic(
                    "DIMENSION_INDEX", f"{row[0]} has invalid status {row[3]!r}"
                )
            )
        if row[6] not in VALID_BLOCKS_VALUES:
            errors.append(
                _diagnostic(
                    "DIMENSION_INDEX", f"{row[0]} has invalid blocking value {row[6]!r}"
                )
            )
        if not _substantive(row[4]) or not _substantive(row[5]):
            errors.append(
                _diagnostic("DIMENSION_INDEX", f"{row[0]} lacks a reason or pointer")
            )
    if seen != REQUIRED_DIMENSION_IDS:
        errors.append(
            _diagnostic(
                "DIMENSION_INDEX", "D00-D19 must appear exactly once and in order"
            )
        )


def _load_dossier(workspace: Path) -> tuple[Any | None, str | None]:
    path = workspace / ".yxj-paper-os" / "template-analysis" / "semantic-dossier.json"
    if not path.is_file() or path.is_symlink():
        return None, "semantic dossier is missing or not a regular non-symlink file"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"semantic dossier is unreadable: {exc}"


def _dossier_ids(payload: Any) -> set[str]:
    if not isinstance(payload, dict):
        return set()
    ids = {str(payload.get("dossier_id", ""))}
    for collection, key in (
        ("documents", "template_source_id"),
        ("observations", "observation_id"),
        ("transfer_rules", "rule_id"),
    ):
        values = payload.get(collection)
        if isinstance(values, list):
            ids.update(
                str(item.get(key, "")) for item in values if isinstance(item, dict)
            )
    return {value for value in ids if value}


def _resolve_json_fragment(payload: Any, fragment: str) -> Any | None:
    current = payload
    for part in re.split(r"\.(?![^\[]*\])", fragment):
        if isinstance(current, list):
            if part == "rows":
                continue
            list_match = re.fullmatch(r"(?:rows)?\[?([0-9]+)\]?", part)
            if not list_match:
                return None
            index = int(list_match.group(1))
            if index >= len(current):
                return None
            current = current[index]
            continue
        match = re.fullmatch(r"([^\[]+)(?:\[([0-9]+)\])?", part)
        if not match or not isinstance(current, dict) or match.group(1) not in current:
            return None
        current = current[match.group(1)]
        if match.group(2) is not None:
            if not isinstance(current, list):
                return None
            index = int(match.group(2))
            if index >= len(current):
                return None
            current = current[index]
    return current


def _read_json_artifact(path: Path) -> Any:
    if path.suffix == ".jsonl":
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_quantitative_pointers(
    workspace: Path,
    pointers: list[str],
    expected_suggestion: str | None,
) -> list[str]:
    errors: list[str] = []
    analysis_dir = workspace / ".yxj-paper-os" / "template-analysis"
    manifest_path = analysis_dir / "manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        return ["current analyzer manifest.json is missing"]
    try:
        manifest = _read_json_artifact(manifest_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"analyzer manifest is unreadable: {exc}"]
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != "template-corpus-normalized/1.0"
    ):
        errors.append("analyzer manifest schema is invalid")
        return errors
    analysis_id = manifest.get("analysis_id")
    corpus_id = manifest.get("corpus_id")
    selected_metrics = manifest.get("design_metric_ids")
    effective_mode = manifest.get("effective_analysis_mode")
    if (
        not isinstance(analysis_id, str)
        or not analysis_id
        or not isinstance(corpus_id, str)
        or not corpus_id
    ):
        errors.append("analyzer identity is incomplete")
    if (
        not isinstance(selected_metrics, list)
        or not selected_metrics
        or not all(isinstance(item, str) and item for item in selected_metrics)
        or len(selected_metrics) != len(set(selected_metrics))
    ):
        errors.append("analyzer selected metric identity is missing")
        selected_metrics = []
    if effective_mode not in {"case_set", "exploratory", "distributional"}:
        errors.append("analyzer effective mode is invalid")

    def validate_candidate(
        candidate: Any, label: str, *, compare_suggestion: bool
    ) -> bool:
        required = {
            "valid_n",
            "missingness",
            "metric_ids",
            "partition",
            "uncertainty",
            "candidate_action",
        }
        if not isinstance(candidate, dict) or not required.issubset(candidate):
            errors.append(f"analyzer candidate state is incomplete: {label}")
            return False
        valid_n = candidate.get("valid_n")
        missingness = candidate.get("missingness")
        if (
            not isinstance(valid_n, int)
            or isinstance(valid_n, bool)
            or valid_n < 0
            or not isinstance(missingness, int)
            or isinstance(missingness, bool)
            or missingness < 0
            or valid_n + missingness <= 0
        ):
            errors.append(f"analyzer denominator/missingness is invalid: {label}")
        metric_ids = candidate.get("metric_ids")
        if (
            not isinstance(metric_ids, list)
            or not metric_ids
            or not all(isinstance(metric, str) and metric for metric in metric_ids)
            or len(metric_ids) != len(set(metric_ids))
            or not set(metric_ids).intersection(selected_metrics)
            or any(metric not in selected_metrics for metric in metric_ids)
        ):
            errors.append(f"analyzer rule uses an unselected metric: {label}")
        if (
            not isinstance(candidate.get("partition"), str)
            or not candidate.get("partition", "").strip()
        ):
            errors.append(f"analyzer partition identity is invalid: {label}")
        uncertainty = candidate.get("uncertainty")
        if isinstance(uncertainty, dict):
            item_mode = uncertainty.get("effective_analysis_mode")
            metric_mode = uncertainty.get("metric_effective_analysis_mode")
            allowed = {"case_set", "exploratory", "distributional"}
            if item_mode != effective_mode or metric_mode not in allowed:
                errors.append(f"analyzer effective-mode boundary is invalid: {label}")
            if uncertainty.get("comparable_stratum") is not True:
                errors.append(
                    f"analyzer pointer uses a mixed/non-comparable stratum: {label}"
                )
        else:
            errors.append(f"analyzer uncertainty boundary is missing: {label}")
        action = candidate.get("candidate_action")
        mapped = (
            ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION.get(action)
            if isinstance(action, str)
            else None
        )
        if mapped is None:
            errors.append(f"analyzer candidate action is missing or unknown: {label}")
        elif compare_suggestion and expected_suggestion != mapped:
            errors.append(f"analyzer suggestion mapping differs for {label}")
        return True

    for pointer in pointers:
        match = QUANT_POINTER_RE.fullmatch(pointer)
        if not match or match.group(1) not in ANALYZER_GROUNDING_OUTPUTS:
            errors.append(f"invalid fixed analyzer pointer {pointer}")
            continue
        filename, fragment = match.groups()
        artifact_path = analysis_dir / filename
        if not artifact_path.is_file() or artifact_path.is_symlink():
            errors.append(f"analyzer artifact is missing: {filename}")
            continue
        try:
            artifact = _read_json_artifact(artifact_path)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"analyzer artifact is unreadable: {filename}: {exc}")
            continue
        expected_schema = ANALYZER_SCHEMAS.get(filename)
        records = artifact if isinstance(artifact, list) else [artifact]
        if not records or any(not isinstance(record, dict) for record in records):
            errors.append(f"analyzer artifact has invalid record shape: {filename}")
            continue
        for index, record in enumerate(records):
            assert isinstance(record, dict)
            if expected_schema is None or record.get("schema") != expected_schema:
                errors.append(
                    f"analyzer artifact schema is invalid: {filename}[{index}]"
                )
            if (
                record.get("analysis_id") != analysis_id
                or record.get("corpus_id") != corpus_id
            ):
                errors.append(
                    f"mixed or missing analyzer identity in {filename}[{index}]"
                )
            if filename.endswith(".jsonl"):
                validate_candidate(
                    record, f"{filename}[{index}]", compare_suggestion=False
                )
        resolved = _resolve_json_fragment(artifact, fragment)
        if resolved is None:
            errors.append(f"analyzer pointer fragment does not resolve: {pointer}")
            continue
        candidates = resolved if isinstance(resolved, list) else [resolved]
        bounded_candidate_found = False
        for candidate in candidates:
            bounded_candidate_found = (
                validate_candidate(
                    candidate,
                    pointer,
                    compare_suggestion=expected_suggestion is not None,
                )
                or bounded_candidate_found
            )
        if not bounded_candidate_found:
            errors.append(
                f"analyzer pointer lacks selected-metric denominator/missingness state: {pointer}"
            )
    return errors


def _plugin_version() -> str:
    descriptor = Path(__file__).resolve().parents[3] / ".codex-plugin" / "plugin.json"
    try:
        value = json.loads(descriptor.read_text(encoding="utf-8")).get("version")
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "unavailable"
    return value if isinstance(value, str) else "unavailable"


def validate_workspace_report(
    workspace: Path, require_handoff: bool = False
) -> ValidationReport:
    workspace = Path(workspace)
    if not workspace.is_dir():
        return ValidationReport(
            [_diagnostic("WORKSPACE", f"workspace not found: {workspace}")], []
        )

    index_path = workspace / DIMENSION_INDEX
    index_text: str | None = None
    if index_path.is_file():
        try:
            index_text = index_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            index_text = None
    schema_error = _schema_diagnostic(index_text)
    if schema_error is not None:
        return ValidationReport([schema_error], [])

    errors: list[str] = []
    warnings: list[str] = []
    required = set(REQUIRED_FILES)
    present = {path.name for path in workspace.glob("*.md")}
    for name in sorted(present - required):
        errors.append(
            _diagnostic("PUBLIC_SURFACE", f"unexpected public Markdown file: {name}")
        )
    for name in sorted(required - present):
        errors.append(_diagnostic("PUBLIC_SURFACE", f"missing required file: {name}"))
    contents: dict[str, str] = {}
    for name in sorted(required & present):
        try:
            contents[name] = (workspace / name).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(_diagnostic("PUBLIC_SURFACE", f"cannot read {name}: {exc}"))
    if required - set(contents):
        return ValidationReport(errors, warnings)

    # Schema authority is exclusive to 00. Every normative table heading has one
    # and only one owning H2 so no first-copy/last-copy shadow authority exists.
    for name, text in contents.items():
        if name != DIMENSION_INDEX and re.search(
            r"(?im)^\s*-?\s*Workspace schema version\s*:", text
        ):
            errors.append(
                _diagnostic(
                    "SCHEMA_INVALID",
                    f"workspace schema marker is forbidden outside {DIMENSION_INDEX}: {name}",
                )
            )
    for filename, heading in TABLE_CONTRACTS:
        count = _heading_cardinality(contents[filename], heading)
        if count != 1:
            errors.append(
                _diagnostic(
                    "TABLE_CONTRACT",
                    f"{filename}#{heading} must occur exactly once; found {count}",
                )
            )

    _validate_dimension_index(contents[DIMENSION_INDEX], errors)
    tables = {
        key: _parse_table(contents, key[0], key[1], columns, errors)
        for key, columns in TABLE_CONTRACTS.items()
    }

    scopes = tables[(DIMENSION_INDEX, "Writing Scopes")]
    lenses = tables[(DIMENSION_INDEX, "Active Calibration Lenses")]
    requirements = tables[(DIMENSION_INDEX, "Conditional Requirements")]
    dependencies = tables[(DIMENSION_INDEX, "Dependency Recheck")]
    decisions = tables[("00_PROJECT_ROUTE.md", "Decision Records")]
    materials = tables[("01_MATERIALS_INVENTORY.md", "Material Records")]
    template_sources = tables[("01_MATERIALS_INVENTORY.md", "Template Design Sources")]
    claims = tables[("02_CLAIM_EVIDENCE_BOUNDARY.md", "Claim Records")]
    sections = tables[("03_WRITING_STRUCTURE.md", "Section Map")]
    paragraphs = tables[("03_WRITING_STRUCTURE.md", "Paragraph Map")]
    payloads = tables[("03_WRITING_STRUCTURE.md", "Paragraph Payload and Boundary Map")]
    important = tables[("03_WRITING_STRUCTURE.md", "Important Paragraph Register")]
    frames = tables[("03_WRITING_STRUCTURE.md", "Controlled Sentence Frames")]
    languages = tables[("03_WRITING_STRUCTURE.md", "Surface Language Contract")]
    visuals = tables[("03_WRITING_STRUCTURE.md", "Visual Blueprint")]
    edges = tables[("03_WRITING_STRUCTURE.md", "Cross-Surface Traceability")]
    rules = tables[("03_WRITING_STRUCTURE.md", "Template Rule Projection")]
    budgets = tables[("03_WRITING_STRUCTURE.md", "Grounded Soft Budgets")]
    writing_plans = tables[("03_WRITING_STRUCTURE.md", "Scoped Writing Plan")]
    authorities = tables[(FINAL_PACK, "Authority Pointers")]
    coverage = tables[(FINAL_PACK, "Detailed Surface Coverage")]
    summaries = tables[(FINAL_PACK, "Detailed Coverage Summary")]
    gate_summaries = tables[(FINAL_PACK, "Owner Gate Resolution Summary")]
    template_handling = tables[(FINAL_PACK, "Template Analysis Handling")]
    unresolved_rows = tables[(FINAL_PACK, "Unresolved and Downstream Prohibitions")]
    handoffs = tables[(FINAL_PACK, "Scoped Handoff")]

    scope_by_id = _unique_ids(
        scopes, "Scope ID", _id_pattern("SCOPE"), "SCOPE_CONTRACT", errors
    )
    req_by_id = _unique_ids(
        requirements,
        "Requirement ID",
        _id_pattern("REQ"),
        "REQUIREMENT_CONTRACT",
        errors,
    )
    decision_by_id = _unique_ids(
        decisions, "Decision ID", _id_pattern("DEC"), "OWNER_GATE", errors
    )
    material_by_id = _unique_ids(
        materials, "Record ID", _id_pattern("M"), "MATERIAL_CONTRACT", errors
    )
    template_by_id = _unique_ids(
        template_sources,
        "Template source ID",
        _id_pattern("TPL"),
        "TEMPLATE_FIREWALL",
        errors,
    )
    claim_by_id = _unique_ids(
        claims, "Claim ID", _id_pattern("C"), "CLAIM_CONTRACT", errors
    )
    section_by_id = _unique_ids(
        sections, "Section ID", _id_pattern("SEC"), "SECTION_OWNERSHIP", errors
    )
    paragraph_by_id = _unique_ids(
        paragraphs, "Paragraph ID", _id_pattern("PAR"), "PARAGRAPH_OWNERSHIP", errors
    )
    frame_by_id = _unique_ids(
        frames, "Frame ID", _id_pattern("FRM"), "FRAME_REFERENCE", errors
    )
    language_by_id = _unique_ids(
        languages, "Contract ID", _id_pattern("LANG"), "LANGUAGE_CONTRACT", errors
    )
    visual_by_id = _unique_ids(
        visuals, "Visual ID", _id_pattern("VIS"), "VISUAL_CONTRACT", errors
    )
    edge_by_id = _unique_ids(
        edges, "Edge ID", _id_pattern("EDGE"), "EDGE_REFERENCE", errors
    )
    rule_by_id = _unique_ids(
        rules, "Rule ID", _id_pattern("TRULE"), "TEMPLATE_RULE_INCOMPATIBLE", errors
    )
    budget_by_id = _unique_ids(
        budgets, "Budget ID", _id_pattern("BUD"), "BUDGET_CONTRACT", errors
    )

    owner_maps = [
        scope_by_id,
        req_by_id,
        decision_by_id,
        material_by_id,
        template_by_id,
        claim_by_id,
        section_by_id,
        paragraph_by_id,
        frame_by_id,
        language_by_id,
        visual_by_id,
        edge_by_id,
        rule_by_id,
        budget_by_id,
    ]
    all_owned_ids: set[str] = set(REQUIRED_DIMENSION_IDS)
    for mapping in owner_maps:
        overlap = all_owned_ids.intersection(mapping)
        for record_id in sorted(overlap):
            errors.append(
                _diagnostic(
                    "RECORD_ID", f"record ID is not globally unique: {record_id}"
                )
            )
        all_owned_ids.update(mapping)

    ready_scopes = {
        row["Scope ID"] for row in scopes if row.get("Readiness") == "writer-ready"
    }
    scope_blockers: dict[str, set[str]] = {}
    for row in scopes:
        scope_id = row["Scope ID"]
        if not _substantive(row["Writing surface"]) or not _substantive(
            row["Intended output"]
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{scope_id} lacks a substantive writing surface or output",
                )
            )
        if row["Readiness"] not in READINESS:
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT",
                    f"{scope_id} has invalid readiness {row['Readiness']!r}",
                )
            )
        input_ids, input_error = _typed_list(
            row["Available inputs"], (ID_RE, D_RE), allow_none=True
        )
        if input_error or any(item not in all_owned_ids for item in input_ids):
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT", f"{scope_id} has invalid available inputs"
                )
            )
        requirement_ids, req_error = _typed_list(
            row["Required requirement IDs"], (_id_pattern("REQ"),), allow_none=True
        )
        if req_error or any(item not in req_by_id for item in requirement_ids):
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT", f"{scope_id} references unknown requirements"
                )
            )
        blocker_ids, blocker_error = _typed_list(
            row["Remaining blocker"], (ID_RE, D_RE), allow_none=True
        )
        scope_blockers[scope_id] = set(blocker_ids)
        if blocker_error or any(item not in all_owned_ids for item in blocker_ids):
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT", f"{scope_id} has invalid remaining blocker IDs"
                )
            )
        if row["Readiness"] == "writer-ready":
            if not input_ids:
                errors.append(
                    _diagnostic(
                        "SCOPE_CONTRACT",
                        f"writer-ready {scope_id} requires available input IDs",
                    )
                )
            if (
                row["Remaining blocker"] != "none"
                or row["Next action"] != "none"
                or not _public_pointer(row["Output pointer"], contents)
            ):
                errors.append(
                    _diagnostic(
                        "SCOPE_CONTRACT",
                        f"writer-ready {scope_id} requires blocker/next none and a resolvable output pointer",
                    )
                )
            for requirement_id in requirement_ids:
                requirement = req_by_id.get(requirement_id)
                if requirement is not None and requirement["Handling"] not in {
                    "satisfied",
                    "not_applicable",
                }:
                    errors.append(
                        _diagnostic(
                            "SCOPE_CONTRACT",
                            f"writer-ready {scope_id} has unsatisfied {requirement_id}",
                        )
                    )
        elif not blocker_ids or row["Next action"] == "none":
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT",
                    f"non-ready {scope_id} requires blocker and next action",
                )
            )
        if row["Output pointer"] != "none" and not _public_pointer(
            row["Output pointer"], contents
        ):
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT", f"{scope_id} has an unresolved output pointer"
                )
            )

    active_lenses: set[str] = set()
    for row in lenses:
        if not _substantive(row["Activation basis"]):
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT",
                    f"lens {row['Lens ID']} lacks an activation basis",
                )
            )
        if row["Lens ID"] not in LENS_IDS:
            errors.append(
                _diagnostic("REQUIREMENT_CONTRACT", f"unknown lens ID {row['Lens ID']}")
            )
        else:
            active_lenses.add(row["Lens ID"])
        affected, list_error = _typed_list(
            row["Affected scopes"], (_id_pattern("SCOPE"),), allow_none=True
        )
        if list_error or any(item not in scope_by_id for item in affected):
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT",
                    f"lens {row['Lens ID']} has invalid affected scopes",
                )
            )
    for row in requirements:
        requirement_id = row["Requirement ID"]
        if not _substantive(row["Requirement"]):
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT",
                    f"{requirement_id} lacks substantive requirement text",
                )
            )
        affected, list_error = _typed_list(
            row["Affected scopes"], (_id_pattern("SCOPE"),), allow_none=True
        )
        if row["Lens ID"] not in active_lenses:
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT",
                    f"{requirement_id} references inactive lens {row['Lens ID']}",
                )
            )
        if row["Handling"] not in REQ_STATE:
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT", f"{requirement_id} has invalid handling"
                )
            )
        if list_error or any(item not in scope_by_id for item in affected):
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT",
                    f"{requirement_id} has invalid affected scopes",
                )
            )
        allow_none = row["Handling"] in {"deferred", "not_applicable"}
        if not _resolve_reference(
            row["Evidence / decision pointer"],
            workspace=workspace,
            contents=contents,
            owned_ids=all_owned_ids,
            allow_none=allow_none,
        ):
            errors.append(
                _diagnostic(
                    "REQUIREMENT_CONTRACT",
                    f"{requirement_id} has invalid evidence/decision pointer",
                )
            )

    template_only_public_targets = {
        "01_MATERIALS_INVENTORY.md#Template Design Sources",
        "03_WRITING_STRUCTURE.md#Template Rule Projection",
        "03_WRITING_STRUCTURE.md#Grounded Soft Budgets",
        "04_WRITING_DESIGN_PACK.md#Template Analysis Handling",
        "04_WRITING_DESIGN_PACK.md#Template Source Firewall",
    }

    def canonical_reference(
        value: str, *, allow_raw_contained_path: bool = False
    ) -> CanonicalReference | None:
        return _canonical_reference(
            value,
            workspace=workspace,
            contents=contents,
            owned_ids=all_owned_ids,
            allow_raw_contained_path=allow_raw_contained_path,
        )

    template_role_identities = {
        identity
        for identity in (
            *(
                canonical_reference(record_id)
                for record_id in (*template_by_id, *rule_by_id)
            ),
            *(canonical_reference(pointer) for pointer in template_only_public_targets),
            *(
                canonical_reference(value, allow_raw_contained_path=True)
                for row in template_sources
                for value in (
                    row["Source/provenance pointer"],
                    row["Local derivative pointer"],
                    row["Hidden dossier pointer"],
                )
                if value != "none"
            ),
        )
        if identity is not None
    }
    analysis_root = (workspace / ".yxj-paper-os" / "template-analysis").resolve(
        strict=False
    )

    def is_template_design_target(value: str) -> bool:
        identity = canonical_reference(value)
        if identity is None:
            return False
        if identity in template_role_identities or identity.kind in {
            "dossier",
            "analyzer",
            "lens",
        }:
            return True
        return (
            identity.kind == "path"
            and isinstance(identity.target, Path)
            and (
                identity.target == analysis_root
                or analysis_root in identity.target.parents
            )
        )

    for row in materials:
        record_id = row["Record ID"]
        if not _substantive(row["Kind"]) or not _substantive(row["Content / role"]):
            errors.append(
                _diagnostic(
                    "MATERIAL_CONTRACT",
                    f"{record_id} lacks kind or content/role",
                )
            )
        if (
            row["Status"] not in MATERIAL_STATUS
            or row["Origin"] not in ORIGIN
            or row["Resolution"] not in RESOLUTION
        ):
            errors.append(
                _diagnostic("MATERIAL_CONTRACT", f"{record_id} has an invalid enum")
            )
        if (
            row["Status"] in {"available", "partial"}
            and row["Kind"] in {"artifact", "result", "evidence"}
            and row["Locator"] == "none"
        ):
            errors.append(
                _diagnostic("MATERIAL_CONTRACT", f"{record_id} requires a locator")
            )
        if (
            row["Origin"] in {"model-derived", "model-proposed"}
            and row["Grounding"] == "none"
        ):
            errors.append(
                _diagnostic("MATERIAL_CONTRACT", f"{record_id} requires grounding")
            )
        for column in ("Locator", "Grounding"):
            if row[column] != "none":
                refs, refs_error = _typed_list(
                    row[column], (FREE_POINTER_TOKEN_RE,), allow_none=False
                )
                if refs_error or any(
                    not _resolve_reference(
                        item,
                        workspace=workspace,
                        contents=contents,
                        owned_ids=all_owned_ids,
                        allow_none=False,
                    )
                    for item in refs
                ):
                    errors.append(
                        _diagnostic(
                            "MATERIAL_CONTRACT",
                            f"{record_id} has invalid {column.lower()}",
                        )
                    )
                if any(is_template_design_target(item) for item in refs):
                    errors.append(
                        _diagnostic(
                            "TEMPLATE_FIREWALL",
                            f"{record_id} scientific material {column.lower()} crosses the design-only template firewall",
                        )
                    )

    template_tainted_materials: set[str] = set()
    changed = True
    while changed:
        changed = False
        for record_id, row in material_by_id.items():
            material_refs = [
                item
                for column in ("Locator", "Grounding")
                for item in _typed_list(
                    row[column], (FREE_POINTER_TOKEN_RE,), allow_none=True
                )[0]
            ]
            if record_id not in template_tainted_materials and any(
                is_template_design_target(item) or item in template_tainted_materials
                for item in material_refs
            ):
                template_tainted_materials.add(record_id)
                changed = True
    for record_id in sorted(template_tainted_materials):
        errors.append(
            _diagnostic(
                "TEMPLATE_FIREWALL",
                f"{record_id} is transitively grounded in a design-only template source",
            )
        )

    for row in claims:
        claim_id = row["Claim ID"]
        if not _substantive(row["Claim"]):
            errors.append(
                _diagnostic("CLAIM_CONTRACT", f"{claim_id} lacks claim content")
            )
        if (
            row["Status"] not in CLAIM_STATUS
            or row["Origin"] not in ORIGIN
            or row["Support"] not in SUPPORT
            or row["Resolution"] not in RESOLUTION
        ):
            errors.append(
                _diagnostic("CLAIM_CONTRACT", f"{claim_id} has an invalid enum")
            )
        evidence_ids, list_error = _typed_list(
            row["Evidence record IDs"], (_id_pattern("M"),), allow_none=True
        )
        if "TPL-" in row["Evidence record IDs"]:
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{claim_id} uses template-design material as scientific evidence",
                )
            )
        if list_error or any(item not in material_by_id for item in evidence_ids):
            errors.append(
                _diagnostic(
                    "CLAIM_CONTRACT",
                    f"{claim_id} references unknown scientific material",
                )
            )
        if row["Status"] in {"active", "downgraded"}:
            boundary_columns = (
                "Evidence record IDs",
                "Warrant / support relation",
                "Scope / conditions",
                "Directness",
                "Uncertainty / counterevidence",
                "Allowed wording",
                "Forbidden wording",
            )
            if any(row[column] == "none" for column in boundary_columns):
                errors.append(
                    _diagnostic(
                        "CLAIM_CONTRACT", f"{claim_id} lacks an evidence boundary"
                    )
                )
            if row["Support"] not in {"evidence-supported", "evidence-partial"} or row[
                "Resolution"
            ] in {"unresolved", "conflicted"}:
                errors.append(
                    _diagnostic(
                        "CLAIM_CONTRACT",
                        f"{claim_id} cannot remain active in its current state",
                    )
                )
            for material_id in evidence_ids:
                if material_by_id.get(material_id, {}).get("Status") not in {
                    "available",
                    "partial",
                }:
                    errors.append(
                        _diagnostic(
                            "CLAIM_CONTRACT",
                            f"{claim_id} uses unavailable {material_id}",
                        )
                    )
        if row["Origin"] == "model-proposed" and row["Status"] in {
            "active",
            "downgraded",
        }:
            errors.append(
                _diagnostic(
                    "CLAIM_CONTRACT",
                    f"{claim_id} model proposal must be superseded before activation",
                )
            )
        if (
            row["Origin"] in {"model-derived", "model-proposed"}
            and row["Grounding"] == "none"
        ):
            errors.append(
                _diagnostic(
                    "CLAIM_CONTRACT",
                    f"{claim_id} model-origin record requires grounding",
                )
            )
        if row["Grounding"] != "none":
            grounding, grounding_error = _typed_list(
                row["Grounding"], (FREE_POINTER_TOKEN_RE,), allow_none=False
            )
            if grounding_error or any(
                not _resolve_reference(
                    item,
                    workspace=workspace,
                    contents=contents,
                    owned_ids=all_owned_ids,
                    allow_none=False,
                )
                for item in grounding
            ):
                errors.append(
                    _diagnostic("CLAIM_CONTRACT", f"{claim_id} has invalid grounding")
                )
            if any(
                is_template_design_target(item) or item in template_tainted_materials
                for item in grounding
            ) or any(item in template_tainted_materials for item in evidence_ids):
                errors.append(
                    _diagnostic(
                        "TEMPLATE_FIREWALL",
                        f"{claim_id} scientific grounding directly or indirectly crosses the design-only template firewall",
                    )
                )

    for row in template_sources:
        source_id = row["Template source ID"]
        if row["Design role"] not in {
            "official_venue",
            "target_topic",
            "article_form",
            "time_cohort",
            "control",
            "exemplar",
        } or not _substantive(row["Design question"]):
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} has invalid role or design question",
                )
            )
        if row["Design-only state"] != "design_only":
            errors.append(
                _diagnostic("TEMPLATE_FIREWALL", f"{source_id} is not design_only")
            )
        if row["Access state"] not in {
            "full_text",
            "owner_derivative",
            "metadata_only",
            "snippet_only",
            "inaccessible",
        }:
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL", f"{source_id} has invalid access state"
                )
            )
        if not _source_pointer_valid(workspace, row["Source/provenance pointer"]):
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} lacks canonical URL/identifier/contained provenance",
                )
            )
        local = row["Local derivative pointer"]
        local_file = _contained_file(workspace, local) if local != "none" else None
        if local != "none" and local_file is None:
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} Local derivative pointer is not a contained file",
                )
            )
        if row["Access state"] == "owner_derivative" and local == "none":
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL", f"{source_id} owner derivative is unavailable"
                )
            )
        if (
            row["Access state"] in {"metadata_only", "snippet_only", "inaccessible"}
            and local != "none"
        ):
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} Local derivative pointer must be none for {row['Access state']}",
                )
            )
        sha = row["Source SHA-256"]
        if row["Access state"] in {
            "full_text",
            "owner_derivative",
        } and not SHA256_RE.fullmatch(sha):
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} readable source lacks lowercase SHA-256",
                )
            )
        if local != "none" and not SHA256_RE.fullmatch(sha):
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} Local derivative pointer requires lowercase SHA-256",
                )
            )
        if sha != "none" and not SHA256_RE.fullmatch(sha):
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL", f"{source_id} has malformed source SHA-256"
                )
            )
        if local_file is not None and SHA256_RE.fullmatch(sha):
            try:
                local_sha = hashlib.sha256(local_file.read_bytes()).hexdigest()
            except OSError:
                local_sha = ""
            if local_sha != sha:
                errors.append(
                    _diagnostic(
                        "TEMPLATE_FIREWALL",
                        f"{source_id} Local derivative pointer SHA-256 does not match",
                    )
                )
        pointer = row["Hidden dossier pointer"]
        if pointer != "none" and (
            not DOSSIER_POINTER_RE.fullmatch(pointer)
            or not pointer.endswith(f"#{source_id}")
        ):
            errors.append(
                _diagnostic(
                    "TEMPLATE_PROJECTION_MISMATCH",
                    f"{source_id} hidden pointer does not preserve identity",
                )
            )
        promotion = row["Scientific-source promotion pointer"]
        promoted_material = material_by_id.get(promotion)
        promotion_identity = canonical_reference(promotion)
        decision_record_identity = canonical_reference(
            "00_PROJECT_ROUTE.md#Decision Records"
        )
        valid_promotion = (
            promotion == "none"
            or (
                promoted_material is not None
                and promotion not in template_tainted_materials
                and promoted_material.get("Status") in {"available", "partial"}
                and promoted_material.get("Locator") != "none"
                and promotion_identity is not None
                and not is_template_design_target(promotion)
            )
            or (
                promotion_identity is not None
                and promotion_identity
                in {canonical_reference(decision_id) for decision_id in decision_by_id}
            )
            or (
                promotion_identity is not None
                and promotion_identity == decision_record_identity
            )
        )
        if not valid_promotion:
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{source_id} has invalid separate promotion pointer",
                )
            )

    for row in decisions:
        decision_id = row["Decision ID"]
        gate = row["Gate category"]
        affected, list_error = _typed_list(
            row["Affected scopes"],
            (_id_pattern("SCOPE"),),
            allow_none=gate == "not_applicable",
        )
        if (
            gate not in GATE_CATEGORIES
            or row["Origin"] not in ORIGIN
            or row["Resolution"] not in RESOLUTION
        ):
            errors.append(
                _diagnostic(
                    "OWNER_GATE", f"{decision_id} has an invalid gate or epistemic enum"
                )
            )
        if list_error or any(item not in scope_by_id for item in affected):
            errors.append(
                _diagnostic("OWNER_GATE", f"{decision_id} has invalid affected scopes")
            )
        if not _substantive(row["Issue / options / decision"]) or not _substantive(
            row["Recheck trigger"]
        ):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{decision_id} lacks substantive issue/options or recheck trigger",
                )
            )
        owner_pointer = row["Grounding / owner-answer pointer"]
        if not _resolve_reference(
            owner_pointer,
            workspace=workspace,
            contents=contents,
            owned_ids=all_owned_ids,
            allow_none=False,
        ):
            errors.append(
                _diagnostic("OWNER_GATE", f"{decision_id} lacks valid grounding")
            )
        if (
            gate in FOUR_GATES
            and any(scope in ready_scopes for scope in affected)
            and row["Resolution"] not in {"confirmed", "rejected"}
        ):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{decision_id} is unresolved for ready scope(s) {';'.join(affected)}",
                )
            )
        if row["Origin"] == "owner-stated" and row["Resolution"] == "candidate":
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{decision_id} candidate model proposal cannot be labeled owner-stated",
                )
            )
        if gate in FOUR_GATES:
            allowed_owner_authorities = {
                identity
                for identity in (
                    canonical_reference("00_DIMENSION_INDEX.md#Workspace Metadata"),
                    canonical_reference("00_PROJECT_ROUTE.md#Project Brief"),
                    canonical_reference("00_PROJECT_ROUTE.md#Target Route"),
                )
                if identity is not None
            }
            owner_identity = canonical_reference(owner_pointer)
            owner_material = material_by_id.get(owner_pointer)
            owner_surface = (
                owner_identity is not None
                and owner_material is not None
                and owner_material.get("Origin")
                in {"owner-stated", "artifact-observed"}
                and owner_material.get("Status") in {"available", "partial"}
                and owner_material.get("Resolution") in {"confirmed", "rejected"}
                and owner_pointer not in template_tainted_materials
                and not is_template_design_target(owner_pointer)
            ) or owner_identity in allowed_owner_authorities
            if not owner_surface:
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{decision_id} triggered gate lacks a distinct owner/route/material answer surface",
                    )
                )
        if gate != "not_applicable" and re.search(
            r"(?i)approve\s+(?:the\s+)?(?:whole|entire)\s+(?:design\s+)?pack",
            row["Issue / options / decision"],
        ):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{decision_id} is a ceremonial whole-pack approval gate",
                )
            )

    section_sequences: dict[str, list[tuple[int, str]]] = {}
    for row in sections:
        section_id = row["Section ID"]
        scope_id = row["Scope ID"]
        if scope_id not in scope_by_id:
            errors.append(
                _diagnostic(
                    "SECTION_OWNERSHIP", f"{section_id} references unknown {scope_id}"
                )
            )
        try:
            sequence = int(row["Sequence"])
            if sequence < 1:
                raise ValueError
        except ValueError:
            errors.append(
                _diagnostic("SECTION_OWNERSHIP", f"{section_id} has invalid sequence")
            )
            sequence = -1
        section_sequences.setdefault(scope_id, []).append((sequence, section_id))
        inputs, list_error = _typed_list(
            row["Input IDs"],
            (_id_pattern("M", "C", "REQ", "DEC", "TRULE", "VIS"), D_RE),
            allow_none=False,
        )
        if list_error or any(item not in all_owned_ids for item in inputs):
            errors.append(
                _diagnostic("SECTION_OWNERSHIP", f"{section_id} has invalid input IDs")
            )
        for column in (
            "Job",
            "Reader state in",
            "Reader state out",
            "Output promise",
            "Evidence/visual obligations",
            "Forbidden content",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{section_id} uses bare none/placeholder in {column}",
                    )
                )
    for scope_id, items in section_sequences.items():
        orders = [item[0] for item in items]
        if orders != list(range(1, len(items) + 1)) or len(orders) != len(set(orders)):
            errors.append(
                _diagnostic(
                    "SECTION_OWNERSHIP",
                    f"{scope_id} section sequence is not unique and contiguous",
                )
            )
    for scope_id in ready_scopes:
        if not section_sequences.get(scope_id):
            errors.append(
                _diagnostic(
                    "SECTION_OWNERSHIP", f"writer-ready {scope_id} has no section"
                )
            )

    paragraphs_by_section: dict[str, list[tuple[int, dict[str, str]]]] = {}
    for row in paragraphs:
        paragraph_id = row["Paragraph ID"]
        scope_id = row["Scope ID"]
        section = section_by_id.get(row["Section ID"])
        if (
            scope_id not in scope_by_id
            or section is None
            or section.get("Scope ID") != scope_id
        ):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_OWNERSHIP",
                    f"{paragraph_id} has unknown/cross-scope ownership",
                )
            )
        try:
            sequence = int(row["Sequence"])
            if sequence < 1:
                raise ValueError
        except ValueError:
            errors.append(
                _diagnostic(
                    "PARAGRAPH_SEQUENCE", f"{paragraph_id} has invalid sequence"
                )
            )
            sequence = -1
        paragraphs_by_section.setdefault(row["Section ID"], []).append((sequence, row))
        for column in ("Function/job", "Reader state in", "Reader state out"):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{paragraph_id} uses bare none/placeholder in {column}",
                    )
                )
    for section_id, items in paragraphs_by_section.items():
        ordered = sorted(items, key=lambda item: item[0])
        orders = [item[0] for item in ordered]
        if orders != list(range(1, len(items) + 1)) or len(orders) != len(set(orders)):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_SEQUENCE",
                    f"{section_id} paragraph sequence is not unique and contiguous",
                )
            )
        for index, (_, row) in enumerate(ordered):
            expected_previous = (
                "none" if index == 0 else ordered[index - 1][1]["Paragraph ID"]
            )
            expected_next = (
                "none"
                if index == len(ordered) - 1
                else ordered[index + 1][1]["Paragraph ID"]
            )
            if (
                row["Previous paragraph"] != expected_previous
                or row["Next paragraph"] != expected_next
            ):
                errors.append(
                    _diagnostic(
                        "PARAGRAPH_SEQUENCE",
                        f"{row['Paragraph ID']} adjacency differs from declared order",
                    )
                )
    for section_id, section in section_by_id.items():
        if section["Scope ID"] in ready_scopes and not paragraphs_by_section.get(
            section_id
        ):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_COVERAGE", f"ready {section_id} has no paragraphs"
                )
            )

    payload_counts = _row_counts(payloads, "Paragraph ID")
    for paragraph_id, paragraph in paragraph_by_id.items():
        if (
            paragraph["Scope ID"] in ready_scopes
            and payload_counts.get(paragraph_id) != 1
        ):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_COVERAGE",
                    f"{paragraph_id} requires exactly one payload row",
                )
            )
    for row in payloads:
        paragraph_id = row["Paragraph ID"]
        if paragraph_id not in paragraph_by_id:
            errors.append(
                _diagnostic("PARAGRAPH_COVERAGE", f"orphan payload row {paragraph_id}")
            )
        claim_ids, claim_error = _typed_list(
            row["Claim IDs"], (_id_pattern("C"),), allow_none=True
        )
        material_ids, material_error = _typed_list(
            row["Material/source/evidence IDs"], (_id_pattern("M"),), allow_none=True
        )
        if "TPL-" in row["Material/source/evidence IDs"]:
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{paragraph_id} uses TPL-* as scientific payload",
                )
            )
        if (
            claim_error
            or any(item not in claim_by_id for item in claim_ids)
            or material_error
            or any(item not in material_by_id for item in material_ids)
        ):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_REFERENCE",
                    f"{paragraph_id} has unresolved claim/material payload",
                )
            )
        if not claim_ids and not material_ids:
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{paragraph_id} must carry at least one claim or material payload",
                )
            )
        if row["Citation function"] == "none" and not re.search(
            r"(?i)(?:not_applicable|no (?:external )?citation)",
            row["Claim/citation boundary rationale"],
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{paragraph_id} lacks an explicit citation-absence rationale",
                )
            )
        object_ids, object_error = _typed_list(
            row["Equation/algorithm/visual/table record IDs"],
            (_id_pattern("M", "VIS"),),
            allow_none=True,
        )
        if object_error or any(
            item not in material_by_id and item not in visual_by_id
            for item in object_ids
        ):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_REFERENCE", f"{paragraph_id} has unresolved object IDs"
                )
            )
        for item in object_ids:
            if item in material_by_id and material_by_id[item]["Kind"] not in {
                "artifact",
                "result",
                "evidence",
            }:
                errors.append(
                    _diagnostic(
                        "PARAGRAPH_REFERENCE",
                        f"{paragraph_id} object material {item} has incompatible kind",
                    )
                )
        if not object_ids and not re.search(
            r"(?i)not_applicable|no (?:equation|algorithm|visual|table|object)",
            row["Object relation/job"],
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{paragraph_id} lacks an object non-applicability rationale",
                )
            )
        template_ids, template_error = _typed_list(
            row["Template rule IDs"], (_id_pattern("TRULE"),), allow_none=True
        )
        if template_error or any(item not in rule_by_id for item in template_ids):
            errors.append(
                _diagnostic(
                    "PARAGRAPH_REFERENCE",
                    f"{paragraph_id} has unresolved template-rule IDs",
                )
            )
        for column in (
            "Claim/citation boundary rationale",
            "Object relation/job",
            "Required qualification/limitation",
            "Output promise",
            "Forbidden content/overclaim",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{paragraph_id} uses bare none/placeholder in {column}",
                    )
                )

    important_counts = _row_counts(important, "Paragraph ID")
    for paragraph_id, count in important_counts.items():
        if count > 1:
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE",
                    f"{paragraph_id} appears more than once in important register",
                )
            )
    frames_by_paragraph: dict[str, list[tuple[int, dict[str, str]]]] = {}
    for row in frames:
        frame_id = row["Frame ID"]
        paragraph_id = row["Paragraph ID"]
        if paragraph_id not in paragraph_by_id:
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE", f"{frame_id} references unknown {paragraph_id}"
                )
            )
        try:
            order = int(row["Order"])
            if order < 1:
                raise ValueError
        except ValueError:
            errors.append(
                _diagnostic("FRAME_REFERENCE", f"{frame_id} has invalid order")
            )
            order = -1
        frames_by_paragraph.setdefault(paragraph_id, []).append((order, row))
        payload_ids, payload_error = _typed_list(
            row["Required payload IDs"],
            (_id_pattern("M", "C", "VIS"),),
            allow_none=True,
        )
        if payload_error or any(
            item not in material_by_id
            and item not in claim_by_id
            and item not in visual_by_id
            for item in payload_ids
        ):
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE", f"{frame_id} has unresolved required payload IDs"
                )
            )
        if not payload_ids and not re.search(
            r"(?i)(?:purely relational|transition)", row["Payload/boundary rationale"]
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{frame_id} lacks a relational-frame absence rationale",
                )
            )
        language_ids, language_error = _typed_list(
            row["Language contract IDs"], (_id_pattern("LANG"),), allow_none=False
        )
        if language_error or any(item not in language_by_id for item in language_ids):
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE", f"{frame_id} has unresolved language contracts"
                )
            )
        for column in (
            "Sentence function",
            "Proposition/content target",
            "Clause/relation order",
            "Payload/boundary rationale",
            "Local language constraint",
            "Forbidden realization",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{frame_id} uses bare none/placeholder in {column}",
                    )
                )
        clause = row["Clause/relation order"]
        if not ("[" in clause and "]" in clause):
            warnings.append(
                _diagnostic(
                    "PROSE_BOUNDARY_WARNING",
                    f"{frame_id} Clause/relation order lacks an explicit [slot] marker; manual design-only review required",
                )
            )
        for field in (
            "Proposition/content target",
            "Local language constraint",
            "Forbidden realization",
        ):
            value = row[field]
            if _looks_like_realized_prose(value):
                warnings.append(
                    _diagnostic(
                        "PROSE_BOUNDARY_WARNING",
                        f"{frame_id} {field} looks sentence-like; manual design-only review required",
                    )
                )
    for paragraph_id, items in frames_by_paragraph.items():
        ordered = sorted(items, key=lambda item: item[0])
        orders = [item[0] for item in ordered]
        if orders != list(range(1, len(items) + 1)) or len(orders) != len(set(orders)):
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE",
                    f"{paragraph_id} frame order is not unique and contiguous",
                )
            )
        for index, (_, row) in enumerate(ordered):
            expected_previous = (
                "none" if index == 0 else ordered[index - 1][1]["Frame ID"]
            )
            expected_next = (
                "none"
                if index == len(ordered) - 1
                else ordered[index + 1][1]["Frame ID"]
            )
            if (
                row["Previous frame"] != expected_previous
                or row["Next frame"] != expected_next
            ):
                errors.append(
                    _diagnostic(
                        "FRAME_REFERENCE",
                        f"{row['Frame ID']} adjacency differs from declared order",
                    )
                )
    for row in important:
        paragraph_id = row["Paragraph ID"]
        paragraph = paragraph_by_id.get(paragraph_id)
        if paragraph is None:
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE",
                    f"important register references unknown {paragraph_id}",
                )
            )
        frame_ids, frame_error = _typed_list(
            row["Frame IDs"], (_id_pattern("FRM"),), allow_none=False
        )
        actual = {
            item[1]["Frame ID"] for item in frames_by_paragraph.get(paragraph_id, [])
        }
        if frame_error or set(frame_ids) != actual or not actual:
            errors.append(
                _diagnostic(
                    "FRAME_REFERENCE",
                    f"{paragraph_id} frame register does not match ordered frames",
                )
            )
        gate = row["Gate category"]
        decision_id = row["Decision ID"]
        pointer = row["Owner-answer/grounding pointer"]
        if gate not in GATE_CATEGORIES:
            errors.append(
                _diagnostic("OWNER_GATE", f"{paragraph_id} has invalid gate category")
            )
        elif gate == "not_applicable":
            if decision_id != "none" or pointer != "none":
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"routine {paragraph_id} must not carry a ceremonial decision",
                    )
                )
        else:
            decision = decision_by_id.get(decision_id)
            decision_scopes, decision_scope_error = _typed_list(
                decision.get("Affected scopes", "") if decision else "",
                (_id_pattern("SCOPE"),),
                allow_none=False,
            )
            if (
                decision is None
                or decision_scope_error
                or decision.get("Gate category") != gate
                or paragraph is None
                or paragraph["Scope ID"] not in decision_scopes
                or pointer != decision.get("Grounding / owner-answer pointer")
                or not _resolve_reference(
                    pointer,
                    workspace=workspace,
                    contents=contents,
                    owned_ids=all_owned_ids,
                    allow_none=False,
                )
            ):
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{paragraph_id} triggered gate lacks matching resolved DEC-* grounding",
                    )
                )
            elif paragraph["Scope ID"] in ready_scopes and decision[
                "Resolution"
            ] not in {"confirmed", "rejected"}:
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{paragraph_id} gate is unresolved for ready scope",
                    )
                )
        for column in (
            "Qualitative selection rationale",
            "Consequence/risk/dependency",
            "Gate resolution",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{paragraph_id} important row uses bare none/placeholder in {column}",
                    )
                )

    for row in languages:
        contract_id = row["Contract ID"]
        if row["Scope ID"] not in scope_by_id:
            errors.append(
                _diagnostic(
                    "LANGUAGE_CONTRACT", f"{contract_id} references unknown scope"
                )
            )
        grounding, list_error = _typed_list(
            row["Grounding IDs"],
            (_id_pattern("M", "C", "REQ", "DEC", "TRULE"),),
            allow_none=False,
        )
        if list_error or any(item not in all_owned_ids for item in grounding):
            errors.append(
                _diagnostic(
                    "LANGUAGE_CONTRACT", f"{contract_id} has invalid grounding IDs"
                )
            )
        for column in LANGUAGE_COLUMNS[2:-1]:
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{contract_id} uses bare none/placeholder in {column}",
                    )
                )

    for row in visuals:
        visual_id = row["Visual ID"]
        scope_id = row["Scope ID"]
        if scope_id not in scope_by_id:
            errors.append(
                _diagnostic("VISUAL_CONTRACT", f"{visual_id} references unknown scope")
            )
        paragraph_ids, paragraph_error = _typed_list(
            row["Paragraph IDs"], (_id_pattern("PAR"),), allow_none=True
        )
        if paragraph_error or any(
            item not in paragraph_by_id or paragraph_by_id[item]["Scope ID"] != scope_id
            for item in paragraph_ids
        ):
            errors.append(
                _diagnostic(
                    "VISUAL_CONTRACT", f"{visual_id} has invalid paragraph ownership"
                )
            )
        if not paragraph_ids and not re.search(
            r"(?i)(?:front.?matter|non-body|landing)", row["Story role"]
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{visual_id} has no paragraph and no non-body landing rationale",
                )
            )
        if row["Status"] not in {"existing", "needed", "deferred", "absent"}:
            errors.append(
                _diagnostic("VISUAL_CONTRACT", f"{visual_id} has invalid status")
            )
        evidence_ids, evidence_error = _typed_list(
            row["Evidence/data IDs"],
            (_id_pattern("M"),),
            allow_none=row["Status"] != "existing",
        )
        if evidence_error or any(item not in material_by_id for item in evidence_ids):
            errors.append(
                _diagnostic(
                    "VISUAL_CONTRACT", f"{visual_id} has invalid evidence/data IDs"
                )
            )
        if (
            row["Status"] != "existing"
            and not evidence_ids
            and not _substantive(row["Handoff/blocker"])
        ):
            errors.append(
                _diagnostic(
                    "VISUAL_CONTRACT", f"{visual_id} lacks deferred/needed consequence"
                )
            )
        for column in (
            "Story role",
            "Panel/order/encoding",
            "Caption/legend job",
            "Body callout relation",
            "Accessibility responsibility",
            "Handoff/blocker",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{visual_id} uses bare none/placeholder in {column}",
                    )
                )
        if _looks_like_realized_prose(row["Caption/legend job"]):
            warnings.append(
                _diagnostic(
                    "PROSE_BOUNDARY_WARNING",
                    f"{visual_id} Caption/legend job looks like realized caption prose; manual design-only review required",
                )
            )

    record_to_scopes: dict[str, set[str]] = {
        scope_id: {scope_id} for scope_id in scope_by_id
    }
    for record_id, row in material_by_id.items():
        record_to_scopes[record_id] = {
            token
            for token in re.findall(
                r"SCOPE-[a-z0-9]+(?:-[a-z0-9]+)*", row["Scope / conditions"]
            )
            if token in scope_by_id
        }
    for record_id, row in claim_by_id.items():
        record_to_scopes[record_id] = {
            token
            for token in re.findall(
                r"SCOPE-[a-z0-9]+(?:-[a-z0-9]+)*", row["Scope / conditions"]
            )
            if token in scope_by_id
        }
    for mapping, key in (
        (req_by_id, "Affected scopes"),
        (decision_by_id, "Affected scopes"),
    ):
        for record_id, row in mapping.items():
            affected, _ = _typed_list(
                row[key], (_id_pattern("SCOPE"),), allow_none=True
            )
            record_to_scopes[record_id] = {
                scope for scope in affected if scope in scope_by_id
            }
    for section_id, row in section_by_id.items():
        record_to_scopes[section_id] = {row["Scope ID"]}
    for paragraph_id, row in paragraph_by_id.items():
        record_to_scopes[paragraph_id] = {row["Scope ID"]}
    for frame_id, row in frame_by_id.items():
        scope = paragraph_by_id.get(row["Paragraph ID"], {}).get("Scope ID")
        record_to_scopes[frame_id] = {scope} if scope else set()
    for mapping, key in (
        (language_by_id, "Scope ID"),
        (visual_by_id, "Scope ID"),
        (budget_by_id, "Scope ID"),
    ):
        for record_id, row in mapping.items():
            record_to_scopes[record_id] = {row[key]}
    for rule_id, row in rule_by_id.items():
        affected, _ = _typed_list(
            row["Affected scope IDs"], (_id_pattern("SCOPE"),), allow_none=False
        )
        record_to_scopes[rule_id] = set(affected)
    ownership_dossier, ownership_dossier_error = _load_dossier(workspace)
    ownership_observations: dict[str, str] = {}
    ownership_rules: list[dict[str, Any]] = []
    if isinstance(ownership_dossier, dict):
        raw_ownership_observations = ownership_dossier.get("observations")
        raw_ownership_rules = ownership_dossier.get("transfer_rules")
        ownership_observations = {
            str(item.get("observation_id")): str(item.get("template_source_id"))
            for item in (
                raw_ownership_observations
                if isinstance(raw_ownership_observations, list)
                else []
            )
            if isinstance(item, dict)
        }
        ownership_rules = (
            [item for item in raw_ownership_rules if isinstance(item, dict)]
            if isinstance(raw_ownership_rules, list)
            else []
        )
    for source_id in template_by_id:
        source_scopes: set[str] = set()
        source_observations = {
            observation_id
            for observation_id, linked_source in ownership_observations.items()
            if linked_source == source_id
        }
        for hidden_rule in ownership_rules:
            observation_ids = hidden_rule.get("observation_ids", [])
            snapshot = hidden_rule.get("application_snapshot", {})
            linked_observation_ids = (
                {item for item in observation_ids if isinstance(item, str)}
                if isinstance(observation_ids, list)
                else set()
            )
            if source_observations.intersection(linked_observation_ids) and isinstance(
                snapshot, dict
            ):
                raw_scopes = snapshot.get("affected_scope_ids", [])
                if isinstance(raw_scopes, list):
                    source_scopes.update(
                        scope
                        for scope in raw_scopes
                        if isinstance(scope, str) and scope in scope_by_id
                    )
        record_to_scopes[source_id] = source_scopes
    for row in dependencies:
        affected, _ = _typed_list(
            row["Affected D IDs / scopes"], (ID_RE, D_RE), allow_none=True
        )
        directly_affected_scopes = {item for item in affected if item in scope_by_id}
        for item in affected:
            if D_RE.fullmatch(item):
                record_to_scopes.setdefault(item, set()).update(
                    directly_affected_scopes
                )

    for row in edges:
        edge_id = row["Edge ID"]
        if (
            row["From record"] not in all_owned_ids
            or row["To record"] not in all_owned_ids
        ):
            errors.append(
                _diagnostic("EDGE_REFERENCE", f"{edge_id} has an unresolved endpoint")
            )
        if row["Relation"] not in EDGE_RELATIONS:
            errors.append(
                _diagnostic(
                    "EDGE_REFERENCE",
                    f"{edge_id} has invalid direct relation {row['Relation']!r}",
                )
            )
        scopes_for_edge = record_to_scopes.get(
            row["From record"], set()
        ) | record_to_scopes.get(row["To record"], set())
        record_to_scopes[edge_id] = scopes_for_edge
        if not scopes_for_edge:
            errors.append(
                _diagnostic(
                    "EDGE_REFERENCE",
                    f"{edge_id} cannot be assigned to a declared scope",
                )
            )
        if row["State/freshness"] not in EDGE_STATES:
            errors.append(
                _diagnostic(
                    "EDGE_REFERENCE",
                    f"{edge_id} has invalid state/freshness {row['State/freshness']!r}",
                )
            )
        if row["State/freshness"] in {"candidate", "stale", "unavailable", "blocked"}:
            for scope in sorted(scopes_for_edge):
                if scope in ready_scopes:
                    errors.append(
                        _diagnostic(
                            "DEPENDENCY_STALE",
                            f"{scope} is linked to {row['State/freshness']} edge {edge_id}",
                        )
                    )
                elif edge_id not in scope_blockers.get(scope, set()):
                    errors.append(
                        _diagnostic(
                            "DEPENDENCY_STALE",
                            f"{scope} must list {edge_id} as the authoritative blocker for its {row['State/freshness']} edge state",
                        )
                    )
        for column in ("Closure surface", "State/freshness", "Consequence if stale"):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{edge_id} uses bare none/placeholder in {column}",
                    )
                )

    registry_path = (
        Path(__file__).resolve().parents[1] / "references" / "lenses" / "README.md"
    )
    semantic_active = False
    quantitative_rule_pointers: dict[str, list[str]] = {}
    quantitative_rule_suggestions: dict[str, str] = {}
    generic_rules_by_scope: dict[str, list[dict[str, str]]] = {}
    semantic_rules_by_scope: dict[str, list[dict[str, str]]] = {}
    quantitative_rules_by_scope: dict[str, list[dict[str, str]]] = {}
    for row in rules:
        rule_id = row["Rule ID"]
        affected, affected_error = _typed_list(
            row["Affected scope IDs"], (_id_pattern("SCOPE"),), allow_none=False
        )
        pointers, pointer_error = _typed_list(
            row["Grounding pointer(s)"], (FREE_POINTER_TOKEN_RE,), allow_none=False
        )
        if affected_error or any(scope not in scope_by_id for scope in affected):
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{rule_id} has invalid affected scopes",
                )
            )
        if pointer_error:
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{rule_id} has invalid grounding-pointer list grammar",
                )
            )
        decision_id = row["Decision ID"]
        decision = decision_by_id.get(decision_id)
        gate = (
            decision.get("Gate category") if decision is not None else "not_applicable"
        )
        official_source = None
        if row["Grounding kind"] == "official_constraint" and len(pointers) == 1:
            material = material_by_id.get(pointers[0])
            if material is not None:
                official_source = {
                    "kind": material["Kind"],
                    "origin": material["Origin"],
                    "status": material["Status"],
                    "locator": material["Locator"],
                    "grounding": material["Grounding"],
                }
        contract_rule: dict[str, Any] = {
            "rule_id": rule_id,
            "grounding_kind": row["Grounding kind"],
            "grounding_pointers": pointers,
            "rule_kind": row["Rule kind"],
            "affected_scope_ids": affected,
            "suggested_disposition": row["Suggested disposition"],
            "origin": row["Origin"],
            "resolution": row["Resolution"],
            "disposition": row["Disposition"],
            "gate_category": gate,
            "decision_id": decision_id,
            "freshness": row["Freshness"],
        }
        if official_source is not None:
            contract_rule["official_source"] = official_source
        diagnostics = validate_template_rule(
            contract_rule,
            lens_registry_path=registry_path,
            plugin_version=_plugin_version(),
        )
        for item in diagnostics:
            scope_text = (
                ";".join(item.scopes) if item.scopes else ";".join(affected) or "none"
            )
            errors.append(
                _diagnostic(item.code, f"{rule_id} [{scope_text}] {item.message}")
            )
        if decision is not None:
            decision_scope_list, _ = _typed_list(
                decision["Affected scopes"],
                (_id_pattern("SCOPE"),),
                allow_none=True,
            )
            decision_scopes = set(decision_scope_list)
            if not set(affected).issubset(decision_scopes):
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{rule_id} decision {decision_id} does not cover all affected scopes",
                    )
                )
            if any(scope in ready_scopes for scope in affected) and decision[
                "Resolution"
            ] not in {"confirmed", "rejected"}:
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{rule_id} uses unresolved {decision_id} in a ready scope",
                    )
                )
        if row["Freshness"] in {"stale", "unavailable"}:
            for scope in affected:
                if scope in ready_scopes:
                    errors.append(
                        _diagnostic(
                            "TEMPLATE_RULE_INCOMPATIBLE",
                            f"{rule_id} [{scope}] stale/unavailable rule cannot govern a ready scope",
                        )
                    )
        if row["Grounding kind"] == "semantic_dossier":
            semantic_active = True
            for scope in affected:
                semantic_rules_by_scope.setdefault(scope, []).append(row)
        elif row["Grounding kind"] == "quantitative_analysis":
            quantitative_rule_pointers[rule_id] = pointers
            quantitative_rule_suggestions[rule_id] = row["Suggested disposition"]
            for scope in affected:
                quantitative_rules_by_scope.setdefault(scope, []).append(row)
        elif row["Grounding kind"] == "generic_fallback":
            for scope in affected:
                generic_rules_by_scope.setdefault(scope, []).append(row)
        if row["Disposition"] == "deliberate_divergence":
            if (
                decision is None
                or decision.get("Gate category") != "deliberate_divergence"
                or decision.get("Resolution") not in {"confirmed", "rejected"}
            ):
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{rule_id} deliberate divergence lacks resolved matching owner gate",
                    )
                )
        for column in ("Surface", "Candidate transfer", "Limitation"):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{rule_id} uses bare none/placeholder in {column}",
                    )
                )

    for rule_id, pointers in quantitative_rule_pointers.items():
        for message in _validate_quantitative_pointers(
            workspace, pointers, quantitative_rule_suggestions[rule_id]
        ):
            scopes_text = (
                ";".join(sorted(record_to_scopes.get(rule_id, set()))) or "none"
            )
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE", f"{rule_id} [{scopes_text}] {message}"
                )
            )

    dossier_payload: Any | None = None
    dossier_record_ids: set[str] = set()
    dossier_required_scopes = {
        scope
        for scope, rows_for_scope in semantic_rules_by_scope.items()
        if rows_for_scope
    }
    dossier_required_scopes.update(
        row["Scope ID"]
        for row in template_handling
        if row["Semantic dossier pointer"] != "none"
    )
    dossier_required = (
        semantic_active
        or any(row["Hidden dossier pointer"] != "none" for row in template_sources)
        or any(row["Basis kind"] == "semantic_dossier" for row in budgets)
        or bool(dossier_required_scopes)
    )
    if dossier_required:
        dossier_payload, dossier_error = ownership_dossier, ownership_dossier_error
        if dossier_error:
            scope_text = ";".join(sorted(dossier_required_scopes)) or "none"
            rule_text = (
                ";".join(
                    sorted(
                        row["Rule ID"]
                        for row in rules
                        if row["Grounding kind"] == "semantic_dossier"
                    )
                )
                or "none"
            )
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"semantic dossier required by {rule_text} [{scope_text}]: {dossier_error}",
                )
            )
        else:
            dossier_record_ids = _dossier_ids(dossier_payload)
            for item in validate_semantic_dossier(dossier_payload, workspace):
                scope_text = ";".join(item.scopes) if item.scopes else "none"
                errors.append(_diagnostic(item.code, f"[{scope_text}] {item.message}"))
    for row in template_sources:
        pointer = row["Hidden dossier pointer"]
        if pointer != "none" and (
            dossier_payload is None
            or pointer.rsplit("#", 1)[-1] not in dossier_record_ids
        ):
            errors.append(
                _diagnostic(
                    "TEMPLATE_PROJECTION_MISMATCH",
                    f"{row['Template source ID']} hidden dossier pointer does not resolve",
                )
            )
    for row in rules:
        if row["Grounding kind"] == "semantic_dossier":
            pointers, _ = _typed_list(
                row["Grounding pointer(s)"], (DOSSIER_POINTER_RE,), allow_none=False
            )
            if (
                not pointers
                or dossier_payload is None
                or any(
                    pointer.rsplit("#", 1)[-1] not in dossier_record_ids
                    for pointer in pointers
                )
            ):
                scope_text = row["Affected scope IDs"]
                errors.append(
                    _diagnostic(
                        "TEMPLATE_RULE_INCOMPATIBLE",
                        f"{row['Rule ID']} [{scope_text}] semantic grounding pointer does not resolve",
                    )
                )
    for hidden_rule in ownership_rules:
        snapshot = hidden_rule.get("application_snapshot")
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("gate_category") == "not_applicable"
        ):
            continue
        decision_id = snapshot.get("decision_id")
        decision = (
            decision_by_id.get(decision_id) if isinstance(decision_id, str) else None
        )
        if decision is None or snapshot.get("decision_pointer") != decision.get(
            "Grounding / owner-answer pointer"
        ):
            hidden_scopes = snapshot.get("affected_scope_ids")
            scope_text = (
                ";".join(
                    sorted(item for item in hidden_scopes if isinstance(item, str))
                )
                if isinstance(hidden_scopes, list)
                else "none"
            )
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{hidden_rule.get('rule_id', 'unknown')} [{scope_text}] hidden owner-answer pointer differs from authoritative DEC-*",
                )
            )

    for row in budgets:
        budget_id = row["Budget ID"]
        if row["Scope ID"] not in scope_by_id:
            errors.append(
                _diagnostic("BUDGET_CONTRACT", f"{budget_id} references unknown scope")
            )
        if row["Basis kind"] not in {
            "official_constraint",
            "semantic_dossier",
            "quantitative_analysis",
            "repository_grounding",
            "generic_fallback",
        }:
            errors.append(
                _diagnostic("BUDGET_CONTRACT", f"{budget_id} has invalid basis kind")
            )
        grounding_pointer = row["Grounding pointer"]
        if grounding_pointer == "none":
            errors.append(
                _diagnostic(
                    "BUDGET_CONTRACT", f"{budget_id} requires a grounding pointer"
                )
            )
        elif row["Basis kind"] == "official_constraint":
            official_material = material_by_id.get(grounding_pointer)
            if not (
                official_material is not None
                and official_material["Kind"] in {"source", "artifact"}
                and official_material["Origin"] == "artifact-observed"
                and official_material["Status"] == "available"
                and official_material["Locator"] != "none"
                and official_material["Grounding"] != "none"
                and grounding_pointer not in template_tainted_materials
            ):
                errors.append(
                    _diagnostic(
                        "BUDGET_CONTRACT",
                        f"{budget_id} official constraint requires one qualifying current artifact-observed M-*",
                    )
                )
        elif row[
            "Basis kind"
        ] == "semantic_dossier" and not DOSSIER_POINTER_RE.fullmatch(grounding_pointer):
            errors.append(
                _diagnostic(
                    "BUDGET_CONTRACT",
                    f"{budget_id} semantic budget requires a dossier pointer",
                )
            )
        elif row["Basis kind"] == "semantic_dossier" and (
            dossier_payload is None
            or grounding_pointer.rsplit("#", 1)[-1] not in dossier_record_ids
        ):
            errors.append(
                _diagnostic(
                    "BUDGET_CONTRACT",
                    f"{budget_id} semantic dossier pointer does not resolve",
                )
            )
        elif row[
            "Basis kind"
        ] == "quantitative_analysis" and not QUANT_POINTER_RE.fullmatch(
            grounding_pointer
        ):
            errors.append(
                _diagnostic(
                    "BUDGET_CONTRACT",
                    f"{budget_id} quantitative budget requires an analyzer pointer",
                )
            )
        elif row["Basis kind"] == "quantitative_analysis":
            for message in _validate_quantitative_pointers(
                workspace, [grounding_pointer], None
            ):
                errors.append(_diagnostic("BUDGET_CONTRACT", f"{budget_id} {message}"))
        elif row[
            "Basis kind"
        ] == "generic_fallback" and not GENERIC_POINTER_RE.fullmatch(grounding_pointer):
            errors.append(
                _diagnostic(
                    "BUDGET_CONTRACT",
                    f"{budget_id} fallback budget requires a lens pointer",
                )
            )
        elif row["Basis kind"] == "generic_fallback":
            lens_id, heading_slug = grounding_pointer[5:].split("#", 1)
            try:
                registry_text = registry_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                registry_text = ""
            registry_header, registry_rows = _table(registry_text, "Lens Registry")
            module = None
            if registry_header:
                for raw in registry_rows:
                    item = dict(zip(registry_header, raw))
                    if item.get("Lens ID") == lens_id:
                        module = registry_path.parent / item.get("Module path", "")
                        break
            try:
                module_text = module.read_text(encoding="utf-8") if module else ""
            except (OSError, UnicodeError):
                module_text = ""
            if not module_text or heading_slug not in {
                slugify(match.group(1))
                for match in re.finditer(r"^#{2,3}\s+(.+?)\s*$", module_text, re.M)
            }:
                errors.append(
                    _diagnostic(
                        "BUDGET_CONTRACT",
                        f"{budget_id} fallback lens pointer does not resolve",
                    )
                )
        elif row["Basis kind"] == "repository_grounding":
            repository_domain = bool(
                D_RE.fullmatch(grounding_pointer)
                or _id_pattern("M", "C", "REQ", "DEC").fullmatch(grounding_pointer)
                or grounding_pointer.startswith("path:")
                or "#" in grounding_pointer
            )
            if (
                not repository_domain
                or is_template_design_target(grounding_pointer)
                or not _resolve_reference(
                    grounding_pointer,
                    workspace=workspace,
                    contents=contents,
                    owned_ids=all_owned_ids,
                    allow_none=False,
                )
            ):
                errors.append(
                    _diagnostic(
                        "BUDGET_CONTRACT",
                        f"{budget_id} repository grounding pointer does not resolve in its declared domain",
                    )
                )
        if row["Disposition"] not in {
            "candidate",
            "adopted",
            "adapted",
            "rejected",
            "not_applicable",
        }:
            errors.append(
                _diagnostic("BUDGET_CONTRACT", f"{budget_id} has invalid disposition")
            )
        for column in (
            "Surface",
            "Property",
            "Soft band or ordering",
            "Disposition",
            "Adaptation rationale",
            "Hard-constraint disclaimer",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{budget_id} uses bare none/placeholder in {column}",
                    )
                )

    writing_plan_counts = _row_counts(writing_plans, "Scope ID")
    for scope_id in scope_by_id:
        if writing_plan_counts.get(scope_id) != 1:
            errors.append(
                _diagnostic(
                    "WRITING_PLAN",
                    f"{scope_id} must have exactly one compact Scoped Writing Plan row",
                )
            )
    for row in writing_plans:
        scope_id = row["Scope ID"]
        if scope_id not in scope_by_id:
            errors.append(
                _diagnostic(
                    "WRITING_PLAN", f"writing plan references unknown {scope_id}"
                )
            )
        inputs, list_error = _typed_list(
            row["Input record IDs"], (ID_RE, D_RE), allow_none=True
        )
        if list_error or any(item not in all_owned_ids for item in inputs):
            errors.append(
                _diagnostic(
                    "WRITING_PLAN", f"{scope_id} writing plan has invalid inputs"
                )
            )
        if row["Output pointer"] != "none" and not _public_pointer(
            row["Output pointer"], contents
        ):
            errors.append(
                _diagnostic(
                    "WRITING_PLAN",
                    f"{scope_id} writing plan has invalid output pointer",
                )
            )
        for column in (
            "Reader / section job",
            "Output responsibility",
            "Drafting boundary",
        ):
            if not _substantive(row[column]):
                errors.append(
                    _diagnostic(
                        "ABSENCE_CONTRACT",
                        f"{scope_id} writing plan uses bare none/placeholder in {column}",
                    )
                )

    # Dependency invalidation remains declarative and scope-local.
    for row in dependencies:
        changed = row["Changed record"]
        affected, list_error = _typed_list(
            row["Affected D IDs / scopes"], (ID_RE, D_RE), allow_none=True
        )
        if (
            changed not in all_owned_ids
            or list_error
            or any(item not in all_owned_ids for item in affected)
        ):
            errors.append(
                _diagnostic(
                    "DEPENDENCY_CONTRACT",
                    f"dependency row for {changed} has unknown IDs",
                )
            )
        if row["Disposition"] not in DISPOSITION:
            errors.append(
                _diagnostic(
                    "DEPENDENCY_CONTRACT",
                    f"dependency row for {changed} has invalid disposition",
                )
            )
        if row["Disposition"] in {"stale", "candidate", "blocked"} and not _substantive(
            row["Resolution or next action"]
        ):
            errors.append(
                _diagnostic(
                    "DEPENDENCY_CONTRACT",
                    f"dependency row for {changed} lacks next action",
                )
            )
        if row["Disposition"] in {"stale", "candidate", "blocked"}:
            affected_scopes: set[str] = set()
            for item in affected:
                if item in scope_by_id:
                    affected_scopes.add(item)
                affected_scopes.update(record_to_scopes.get(item, set()))
            for scope in sorted(affected_scopes & ready_scopes):
                errors.append(
                    _diagnostic(
                        "DEPENDENCY_STALE",
                        f"{scope} is linked to {row['Disposition']} dependency {changed}",
                    )
                )

    authority_expectations = {
        "Scope and readiness": "00_DIMENSION_INDEX.md#Writing Scopes",
        "Route and gates": "00_PROJECT_ROUTE.md#Decision Records",
        "Scientific materials": "01_MATERIALS_INVENTORY.md#Material Records",
        "Template design sources": "01_MATERIALS_INVENTORY.md#Template Design Sources",
        "Scientific claim ceiling": "02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records",
        "Detailed design": "03_WRITING_STRUCTURE.md#Section Map",
    }
    authority_counts = _row_counts(authorities, "Authority")
    if set(authority_counts) != set(authority_expectations) or any(
        count != 1 for count in authority_counts.values()
    ):
        errors.append(
            _diagnostic(
                "MANIFEST_AUTHORITY",
                "04 Authority Pointers must contain the six unique authority rows",
            )
        )
    for row in authorities:
        expected_pointer = authority_expectations.get(row["Authority"])
        if (
            expected_pointer is None
            or row["Required pointer"] != expected_pointer
            or not _public_pointer(row["Required pointer"], contents)
            or not _substantive(row["Compiler note"])
        ):
            errors.append(
                _diagnostic(
                    "MANIFEST_AUTHORITY",
                    f"04 authority row {row['Authority']!r} differs from 00-03",
                )
            )

    gate_summary_counts = _row_counts(gate_summaries, "Scope ID")
    for scope_id in scope_by_id:
        if not gate_summary_counts.get(scope_id):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{scope_id} lacks an Owner Gate Resolution Summary row",
                )
            )
    summarized_decisions: set[tuple[str, str]] = set()
    for row in gate_summaries:
        scope_id = row["Scope ID"]
        decision = decision_by_id.get(row["Decision ID"])
        summary_key = (scope_id, row["Decision ID"])
        if summary_key in summarized_decisions:
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"duplicate owner-gate summary key {scope_id}/{row['Decision ID']}",
                )
            )
        summarized_decisions.add(summary_key)
        decision_scopes, decision_scope_error = _typed_list(
            decision["Affected scopes"] if decision else "",
            (_id_pattern("SCOPE"),),
            allow_none=True,
        )
        if (
            scope_id not in scope_by_id
            or decision is None
            or decision_scope_error is not None
            or row["Gate category"] != decision["Gate category"]
            or row["Resolution"] != decision["Resolution"]
            or row["Grounding / owner-answer pointer"]
            != decision["Grounding / owner-answer pointer"]
            or scope_id not in decision_scopes
        ):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{scope_id}/{row['Decision ID']} summary differs from authoritative decision",
                )
            )
        blockers, blocker_error = _typed_list(
            row["Active blocker IDs"], (ID_RE, D_RE), allow_none=True
        )
        if blocker_error or any(item not in all_owned_ids for item in blockers):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{scope_id} owner-gate summary has invalid blockers",
                )
            )
        if set(blockers) != scope_blockers.get(scope_id, set()):
            errors.append(
                _diagnostic(
                    "OWNER_GATE",
                    f"{scope_id} owner-gate blockers differ from authoritative 00 scope row",
                )
            )
    for decision in decisions:
        affected_list, _ = _typed_list(
            decision["Affected scopes"],
            (_id_pattern("SCOPE"),),
            allow_none=True,
        )
        affected = set(affected_list)
        for scope_id in affected:
            if (scope_id, decision["Decision ID"]) not in summarized_decisions:
                errors.append(
                    _diagnostic(
                        "OWNER_GATE",
                        f"{scope_id}/{decision['Decision ID']} is absent from the 04 owner-gate summary",
                    )
                )

    unresolved_counts = _row_counts(unresolved_rows, "Scope ID")
    if any(unresolved_counts.get(scope_id) != 1 for scope_id in scope_by_id) or any(
        scope_id not in scope_by_id for scope_id in unresolved_counts
    ):
        errors.append(
            _diagnostic(
                "MANIFEST_UNRESOLVED",
                "04 unresolved/prohibition table must contain exactly one row per scope",
            )
        )
    for row in unresolved_rows:
        scope_id = row["Scope ID"]
        unresolved, unresolved_error = _typed_list(
            row["Unresolved/stale/deferred record IDs"],
            (ID_RE, D_RE),
            allow_none=True,
        )
        if unresolved_error or any(item not in all_owned_ids for item in unresolved):
            errors.append(
                _diagnostic(
                    "MANIFEST_UNRESOLVED",
                    f"{scope_id} has invalid unresolved record IDs",
                )
            )
        if set(unresolved) != scope_blockers.get(scope_id, set()):
            errors.append(
                _diagnostic(
                    "MANIFEST_UNRESOLVED",
                    f"{scope_id} unresolved IDs differ from authoritative 00 blockers",
                )
            )
        if not _substantive(row["Consequence"]) or not _substantive(
            row["Downstream prohibition"]
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{scope_id} unresolved row lacks consequence/prohibition",
                )
            )

    for heading in REQUIRED_04_HEADINGS:
        if section_content(contents[FINAL_PACK], heading) is None:
            errors.append(
                _diagnostic("TABLE_CONTRACT", f"04 missing required heading {heading}")
            )
    firewall_text = section_content(contents[FINAL_PACK], "Template Source Firewall")
    if firewall_text is None or not re.search(
        r"(?is)design[_-]only.*(?:cannot|must not|may not).*(?:claim|evidence|support)",
        firewall_text,
    ):
        errors.append(
            _diagnostic(
                "TEMPLATE_FIREWALL",
                "04 must declare the design-only template/scientific-source firewall",
            )
        )

    edge_scopes: dict[str, set[str]] = {
        edge_id: record_to_scopes.get(edge_id, set()) for edge_id in edge_by_id
    }
    actual_counts: dict[str, dict[str, int]] = {}
    for scope_id in scope_by_id:
        paragraph_ids = {
            key for key, row in paragraph_by_id.items() if row["Scope ID"] == scope_id
        }
        counts = {
            "section": sum(row["Scope ID"] == scope_id for row in sections),
            "paragraph": len(paragraph_ids),
            "payload": sum(row["Paragraph ID"] in paragraph_ids for row in payloads),
            "important": sum(row["Paragraph ID"] in paragraph_ids for row in important),
            "frame": sum(row["Paragraph ID"] in paragraph_ids for row in frames),
            "language": sum(row["Scope ID"] == scope_id for row in languages),
            "visual": sum(row["Scope ID"] == scope_id for row in visuals),
            "edge": sum(
                scope_id in scopes_for_edge for scopes_for_edge in edge_scopes.values()
            ),
            "rule": sum(
                scope_id in record_to_scopes.get(row["Rule ID"], set()) for row in rules
            ),
            "budget": sum(row["Scope ID"] == scope_id for row in budgets),
        }
        actual_counts[scope_id] = counts

    coverage_counts: dict[tuple[str, str], int] = {}
    expected_surface_counts = {
        "section_paragraph_map": lambda item: (
            item["section"] + item["paragraph"] + item["payload"]
        ),
        "important_paragraph_frames": lambda item: item["important"] + item["frame"],
        "surface_language_contract": lambda item: item["language"],
        "visual_caption_blueprint": lambda item: item["visual"],
        "cross_surface_traceability": lambda item: item["edge"],
        "template_rule_provenance": lambda item: item["rule"],
        "soft_budgets": lambda item: item["budget"],
    }
    surface_authorities = {
        "section_paragraph_map": "03_WRITING_STRUCTURE.md#Section Map",
        "important_paragraph_frames": "03_WRITING_STRUCTURE.md#Important Paragraph Register",
        "surface_language_contract": "03_WRITING_STRUCTURE.md#Surface Language Contract",
        "visual_caption_blueprint": "03_WRITING_STRUCTURE.md#Visual Blueprint",
        "cross_surface_traceability": "03_WRITING_STRUCTURE.md#Cross-Surface Traceability",
        "template_rule_provenance": "03_WRITING_STRUCTURE.md#Template Rule Projection",
        "soft_budgets": "03_WRITING_STRUCTURE.md#Grounded Soft Budgets",
    }
    for row in coverage:
        key = (row["Scope ID"], row["Surface"])
        coverage_counts[key] = coverage_counts.get(key, 0) + 1
        if (
            row["Scope ID"] not in scope_by_id
            or row["Surface"] not in CANONICAL_SURFACES
        ):
            errors.append(
                _diagnostic(
                    "DETAILED_SURFACE_COVERAGE", f"unknown scope/surface row {key}"
                )
            )
            continue
        try:
            declared_count = int(row["Record count"])
            if declared_count < 0:
                raise ValueError
        except ValueError:
            declared_count = -1
            errors.append(
                _diagnostic(
                    "DETAILED_SURFACE_COVERAGE", f"{key} has invalid record count"
                )
            )
        expected_count = expected_surface_counts[row["Surface"]](
            actual_counts[row["Scope ID"]]
        )
        if row["Handling (`satisfied&#124;not_applicable`)"] == "satisfied":
            if (
                declared_count <= 0
                or declared_count != expected_count
                or row["Authoritative pointer"] != surface_authorities[row["Surface"]]
                or not _public_pointer(row["Authoritative pointer"], contents)
                or not _substantive(row["Rationale/blocker"])
            ):
                errors.append(
                    _diagnostic(
                        "DETAILED_SURFACE_COVERAGE",
                        f"{key} satisfied declaration/count/pointer differs from 03",
                    )
                )
        elif row["Handling (`satisfied&#124;not_applicable`)"] == "not_applicable":
            if (
                declared_count != 0
                or expected_count != 0
                or row["Authoritative pointer"] != "none"
                or not _substantive(row["Rationale/blocker"])
            ):
                errors.append(
                    _diagnostic(
                        "DETAILED_SURFACE_COVERAGE",
                        f"{key} not_applicable is ungrounded or contradicted",
                    )
                )
        else:
            errors.append(
                _diagnostic("DETAILED_SURFACE_COVERAGE", f"{key} has invalid handling")
            )
    for scope_id in scope_by_id:
        for surface in CANONICAL_SURFACES:
            if coverage_counts.get((scope_id, surface)) != 1:
                errors.append(
                    _diagnostic(
                        "DETAILED_SURFACE_COVERAGE",
                        f"{scope_id}/{surface} must appear exactly once",
                    )
                )

    summary_counts = _row_counts(summaries, "Scope ID")
    summary_keys = [
        ("Section count", "section"),
        ("Paragraph count", "paragraph"),
        ("Important paragraph count", "important"),
        ("Frame count", "frame"),
        ("Language count", "language"),
        ("Visual count", "visual"),
        ("Edge count", "edge"),
        ("Rule count", "rule"),
        ("Budget count", "budget"),
    ]
    for scope_id in scope_by_id:
        if summary_counts.get(scope_id) != 1:
            errors.append(
                _diagnostic(
                    "DETAILED_SURFACE_COVERAGE",
                    f"{scope_id} detailed summary must appear exactly once",
                )
            )
    for row in summaries:
        scope_id = row["Scope ID"]
        if scope_id not in actual_counts:
            errors.append(
                _diagnostic(
                    "DETAILED_SURFACE_COVERAGE",
                    f"summary references unknown {scope_id}",
                )
            )
            continue
        for column, count_key in summary_keys:
            try:
                declared = int(row[column])
            except ValueError:
                declared = -1
            if declared != actual_counts[scope_id][count_key]:
                errors.append(
                    _diagnostic(
                        "DETAILED_SURFACE_COVERAGE",
                        f"{scope_id} {column} inflates/differs from 03",
                    )
                )

    for heading in AUTHORITATIVE_DETAIL_HEADINGS:
        if section_content(contents[FINAL_PACK], heading) is not None:
            errors.append(
                _diagnostic(
                    "DETAILED_SURFACE_COVERAGE",
                    f"04 duplicates authoritative 03 heading {heading}",
                )
            )

    handling_counts = _row_counts(template_handling, "Scope ID")
    if any(handling_counts.get(scope_id) != 1 for scope_id in scope_by_id) or any(
        scope_id not in scope_by_id for scope_id in handling_counts
    ):
        errors.append(
            _diagnostic(
                "TEMPLATE_HANDLING_CARDINALITY",
                "Template Analysis Handling must contain exactly one row per 00 scope",
            )
        )
    for row in template_handling:
        scope_id = row["Scope ID"]
        mode = row["Mode"]
        semantic_pointer = row["Semantic dossier pointer"]
        quantitative_pointer_text = row["Quantitative analysis pointer(s)"]
        generic_pointer_text = row["Generic fallback pointer(s)"]
        if row["Firewall state"] != "design_only":
            errors.append(
                _diagnostic(
                    "TEMPLATE_FIREWALL",
                    f"{scope_id} template handling is not design_only",
                )
            )
        if mode not in TEMPLATE_MODES or not _substantive(row["Rationale"]):
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} has invalid/unrationalized template mode",
                )
            )
            continue
        quantitative_pointers, quantitative_list_error = _typed_list(
            quantitative_pointer_text, (QUANT_POINTER_RE,), allow_none=True
        )
        generic_pointers, generic_list_error = _typed_list(
            generic_pointer_text, (GENERIC_POINTER_RE,), allow_none=True
        )
        semantic_rules = semantic_rules_by_scope.get(scope_id, [])
        quantitative_rules = quantitative_rules_by_scope.get(scope_id, [])
        generic_rules = generic_rules_by_scope.get(scope_id, [])
        active_kinds = {
            kind
            for kind, active in (
                ("semantic", bool(semantic_rules)),
                ("quantitative", bool(quantitative_rules)),
                ("generic", bool(generic_rules)),
            )
            if active
        }
        required_kinds = {
            "semantic_primary": {"semantic"},
            "semantic_plus_quantitative": {"semantic", "quantitative"},
            "quantitative_only": {"quantitative"},
            "generic_fallback": {"generic"},
            "not_applicable": set(),
        }[mode]
        allowed_kinds = set(required_kinds)
        if mode in {"semantic_primary", "semantic_plus_quantitative"}:
            allowed_kinds.add("generic")
        if not required_kinds.issubset(active_kinds) or not active_kinds.issubset(
            allowed_kinds
        ):
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} {mode} active rule kinds differ: {sorted(active_kinds)}",
                )
            )
        semantic_required = "semantic" in required_kinds
        if semantic_required:
            semantic_fragment = semantic_pointer.rsplit("#", 1)[-1]
            semantic_fragment_scopes: set[str] = set()
            if semantic_fragment.startswith("TPL-"):
                semantic_fragment_scopes.update(
                    record_to_scopes.get(semantic_fragment, set())
                )
            for hidden_rule in ownership_rules:
                snapshot = hidden_rule.get("application_snapshot", {})
                observation_ids = hidden_rule.get("observation_ids", [])
                if not isinstance(snapshot, dict):
                    continue
                raw_hidden_scopes = snapshot.get("affected_scope_ids", [])
                hidden_scopes = (
                    {item for item in raw_hidden_scopes if isinstance(item, str)}
                    if isinstance(raw_hidden_scopes, list)
                    else set()
                )
                if semantic_fragment == hidden_rule.get("rule_id") or (
                    isinstance(observation_ids, list)
                    and semantic_fragment in observation_ids
                ):
                    semantic_fragment_scopes.update(hidden_scopes)
            if (
                not DOSSIER_POINTER_RE.fullmatch(semantic_pointer)
                or dossier_payload is None
                or semantic_pointer.rsplit("#", 1)[-1] not in dossier_record_ids
                or scope_id not in semantic_fragment_scopes
            ):
                errors.append(
                    _diagnostic(
                        "TEMPLATE_RULE_INCOMPATIBLE",
                        f"{scope_id} {mode} requires one resolved semantic dossier pointer",
                    )
                )
        elif semantic_pointer != "none":
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} {mode} forbids semantic pointer",
                )
            )
        expected_quantitative_pointers = {
            pointer
            for rule in quantitative_rules
            for pointer in _typed_list(
                rule["Grounding pointer(s)"], (QUANT_POINTER_RE,), allow_none=False
            )[0]
        }
        if (
            quantitative_list_error
            or set(quantitative_pointers) != expected_quantitative_pointers
        ):
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} quantitative handling pointers must exactly match active same-scope rules",
                )
            )
        expected_generic_pointers = {
            pointer
            for rule in generic_rules
            for pointer in _typed_list(
                rule["Grounding pointer(s)"], (GENERIC_POINTER_RE,), allow_none=False
            )[0]
        }
        if generic_list_error or set(generic_pointers) != expected_generic_pointers:
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} generic handling pointers must exactly match active same-scope rules",
                )
            )
        if generic_rules and mode in {"semantic_primary", "semantic_plus_quantitative"}:
            rationale = row["Rationale"].lower()
            missing_surfaces = [
                rule["Surface"]
                for rule in generic_rules
                if rule["Surface"].lower() not in rationale
            ]
            if missing_surfaces:
                errors.append(
                    _diagnostic(
                        "TEMPLATE_RULE_INCOMPATIBLE",
                        f"{scope_id} semantic+generic rationale must name actual uncovered surface(s): {';'.join(missing_surfaces)}",
                    )
                )
        if mode == "semantic_plus_quantitative" and not re.search(
            r"(?i)primary|主要|优先", row["Rationale"]
        ):
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} combined mode must state semantic reading remains primary",
                )
            )
        blockers, blocker_error = _typed_list(
            row["Active blocker IDs"], (ID_RE, D_RE), allow_none=True
        )
        if blocker_error or any(item not in all_owned_ids for item in blockers):
            errors.append(
                _diagnostic(
                    "TEMPLATE_RULE_INCOMPATIBLE",
                    f"{scope_id} template handling has invalid blocker IDs",
                )
            )
        if set(blockers) != scope_blockers.get(scope_id, set()):
            errors.append(
                _diagnostic(
                    "SCOPE_CONTRACT",
                    f"{scope_id} template handling blockers differ from authoritative 00 scope row",
                )
            )

    handoff_counts = _row_counts(handoffs, "Scope ID")
    if any(handoff_counts.get(scope_id) != 1 for scope_id in scope_by_id) or any(
        scope_id not in scope_by_id for scope_id in handoff_counts
    ):
        errors.append(
            _diagnostic(
                "HANDOFF_SCOPE_CARDINALITY",
                "Scoped Handoff must contain exactly one row per 00 scope",
            )
        )
    for row in handoffs:
        scope_id = row["Scope ID"]
        source = scope_by_id.get(scope_id)
        if source is None:
            continue
        if (
            row["00 scope-row pointer"] != "00_DIMENSION_INDEX.md#Writing Scopes"
            or row["Detailed coverage pointer"]
            != "04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage"
        ):
            errors.append(
                _diagnostic(
                    "HANDOFF_SCOPE_CARDINALITY",
                    f"{scope_id} handoff authority pointers differ",
                )
            )
        blockers, blocker_error = _typed_list(
            row["Active blocker IDs"], (ID_RE, D_RE), allow_none=True
        )
        if blocker_error or any(item not in all_owned_ids for item in blockers):
            errors.append(
                _diagnostic(
                    "HANDOFF_SCOPE_CARDINALITY",
                    f"{scope_id} handoff blocker IDs are invalid",
                )
            )
        if source["Readiness"] == "writer-ready":
            if row["Output pointer"] != source["Output pointer"] or blockers:
                errors.append(
                    _diagnostic(
                        "HANDOFF_READINESS_DUPLICATED",
                        f"{scope_id} output/blockers disagree with authoritative writer-ready row",
                    )
                )
        else:
            if row["Output pointer"] == "none" and not _substantive(
                row["Handoff note"]
            ):
                errors.append(
                    _diagnostic(
                        "HANDOFF_SCOPE_CARDINALITY",
                        f"{scope_id} non-ready handoff needs a concrete note",
                    )
                )
            if row["Output pointer"] not in {"none", source["Output pointer"]}:
                errors.append(
                    _diagnostic(
                        "HANDOFF_SCOPE_CARDINALITY",
                        f"{scope_id} non-ready output must be none or the exact resolvable 00 output pointer",
                    )
                )
        if set(blockers) != scope_blockers.get(scope_id, set()):
            errors.append(
                _diagnostic(
                    "HANDOFF_SCOPE_CARDINALITY",
                    f"{scope_id} handoff blockers differ from authoritative 00 scope row",
                )
            )
        for column in ("Downstream prohibitions", "Handoff note"):
            if READINESS_CLAIM_RE.search(row[column]):
                errors.append(
                    _diagnostic(
                        "HANDOFF_READINESS_DUPLICATED",
                        f"{scope_id} handoff prose must not restate readiness",
                    )
                )
        if not _substantive(row["Downstream prohibitions"]) or not _substantive(
            row["Handoff note"]
        ):
            errors.append(
                _diagnostic(
                    "ABSENCE_CONTRACT",
                    f"{scope_id} handoff needs substantive prohibition and note",
                )
            )
    if require_handoff and not handoffs:
        errors.append(
            _diagnostic(
                "HANDOFF_SCOPE_CARDINALITY",
                "--require-handoff requires Scoped Handoff rows",
            )
        )

    # A deliberate-divergence gate must point to a rule that carries it.
    divergence_decisions = {
        row["Decision ID"]
        for row in decisions
        if row["Gate category"] == "deliberate_divergence"
    }
    used_decisions = {
        row["Decision ID"] for row in rules if row["Decision ID"] != "none"
    }
    for decision_id in sorted(divergence_decisions - used_decisions):
        errors.append(
            _diagnostic(
                "OWNER_GATE",
                f"{decision_id} deliberate divergence is not grounded by a TRULE-*",
            )
        )

    for filename, text in contents.items():
        if re.search(
            r"(?i)\b(?:claims?|promises?|provides?|ensures?|achieves?|guarantees?)\s+(?:research|manuscript|submission|publication|semantic)\s+readiness\b",
            text,
        ):
            errors.append(
                _diagnostic(
                    "PRODUCT_BOUNDARY",
                    f"{filename} contains a forbidden readiness promise",
                )
            )
        if re.search(r"(?i)external skill.{0,40}(?:executed|run|completed)", text):
            errors.append(
                _diagnostic(
                    "PRODUCT_BOUNDARY",
                    f"{filename} contains an external execution claim",
                )
            )

    return ValidationReport(errors, warnings)


def validate_workspace(workspace: Path, require_handoff: bool = False) -> list[str]:
    """Return validation failures only; warnings are available in the report API."""
    return validate_workspace_report(workspace, require_handoff).errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a schema-0.3 yxj-paper-os design pack without writeback"
    )
    parser.add_argument("workspace", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--require-handoff", action="store_true")
    args = parser.parse_args()
    report = validate_workspace_report(args.workspace, args.require_handoff)
    if report.warnings:
        print("Design pack validation warnings:", file=sys.stderr)
        print("\n".join("- " + warning for warning in report.warnings), file=sys.stderr)
    if report.errors:
        print("Design pack validation failed:", file=sys.stderr)
        print("\n".join("- " + error for error in report.errors), file=sys.stderr)
        return 1
    print(f"Structural design-pack validation passed: {args.workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
