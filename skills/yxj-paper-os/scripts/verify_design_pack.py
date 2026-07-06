#!/usr/bin/env python3
"""Lightweight yxj-paper-os design-pack validator.

Checks structural validity for the six-file workspace. It does not judge
semantic adequacy, search citations, run external skills, or model a runtime
graph. A pass is a mechanical handoff check, not manuscript readiness.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DIMENSION_INDEX = "00_DIMENSION_INDEX.md"
FINAL_PACK = "04_WRITING_DESIGN_PACK.md"

REQUIRED_FILES = [
    DIMENSION_INDEX,
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    FINAL_PACK,
]

REQUIRED_HEADINGS = {
    DIMENSION_INDEX: [
        "Workspace Metadata",
        "Dimension Status Index",
        "Readiness Gate",
        "Owner Notes",
    ],
    "00_PROJECT_ROUTE.md": [
        "Project Brief",
        "Target Route",
        "Topic and Positioning",
        "Audience and Reviewer Expectation",
        "Owner Decisions",
        "Forbidden Routes",
        "Route Readiness",
    ],
    "01_MATERIALS_INVENTORY.md": [
        "Results and Experiments",
        "Figures and Tables",
        "Data Sources",
        "Code / Implementation",
        "Baselines",
        "Metrics",
        "Evidence Inventory",
        "Source and Citation Bank",
        "Research Dossier",
        "Existing Text Fragments",
        "Explicit Absences",
    ],
    "02_CLAIM_EVIDENCE_BOUNDARY.md": [
        "Problem / Object / Contribution",
        "Contribution Options",
        "Object Granularity",
        "Claim-Evidence Map",
        "Allowed Wording",
        "Forbidden Wording",
        "Deferred or Rejected Claims",
        "Limitations and Risks",
    ],
    "03_WRITING_STRUCTURE.md": [
        "Exemplar Language Profile",
        "Reader Spine",
        "Manuscript Outline",
        "Section Jobs",
        "Object Granularity",
        "Surface Control",
        "Figure / Table Storyline",
        "Visual Plan",
        "Paragraph / Function Map",
        "Drafting Constraints",
    ],
    FINAL_PACK: [
        "Dimension Coverage Summary",
        "Project Route",
        "Submission Blueprint",
        "Material Boundary",
        "Source / Citation Boundary",
        "Research Dossier Notes",
        "Semantic-Risk and Unresolved-Risk Notes",
        "Core Contribution",
        "Statement Inventory",
        "Claim-Evidence Map",
        "Allowed Wording",
        "Forbidden Wording",
        "Limitations and Risks",
        "Reader Spine",
        "Writing Structure",
        "Visual and Figure Storyline",
        "D02 Stale Gate",
        "External Skill Handoff",
        "Validation Notes",
    ],
}

REQUIRED_DIMENSION_IDS = {f"D{i:02d}" for i in range(20)}
DIMENSION_COLUMNS = [
    "ID",
    "Dimension",
    "Current home",
    "Status",
    "Reason / owner note",
    "Pointer or handoff",
    "Blocks design pack?",
]
VALID_DIMENSION_STATUSES = {"filled", "not_applicable", "absent", "deferred", "rejected"}
VALID_BLOCKS_VALUES = {"yes", "no"}
FINAL_COVERAGE_COLUMNS = ["ID", "Status", "Pointer or handoff", "Blocks design pack?"]

PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|REPLACE_ME|UNKNOWN)\b|\[\s*\.\.\.\s*\]", re.IGNORECASE)
CLAIM_FILES = ("02_CLAIM_EVIDENCE_BOUNDARY.md", FINAL_PACK)
DEFER_STATUSES = {"deferred", "rejected", "not claimed", "not-claimed"}
UNAVAILABLE_VISUAL_STATUS_RE = re.compile(
    r"\b(?:needed|deferred|absent|planned|missing|not\s+available|to\s+be\s+created|pending)\b",
    re.IGNORECASE,
)
ACTIVE_VISUAL_EVIDENCE_RE = re.compile(
    r"\b(?:needed|deferred|absent|planned|missing)\b[^|\n]*(?:visual|figure|table)\b|"
    r"\b(?:visual|figure|table)\b[^|\n]*(?:needed|deferred|absent|planned|missing)\b",
    re.IGNORECASE,
)
STALE_SIGNAL_RE = re.compile(r"\b(?:stale|changed|recompile|out[-\s]?of[-\s]?date)\b", re.IGNORECASE)
RECOMPILE_REQUIRED_RE = re.compile(r"\b(?:yes|true|required|must|recompile|stale)\b", re.IGNORECASE)
RECOMPILE_NOT_REQUIRED_RE = re.compile(
    r"\b(?:no|false|none|n/a|na|not[_\s-]?applicable|not\s+required|no\s+recompile)\b",
    re.IGNORECASE,
)
STALE_ACTION_RE = re.compile(
    r"\b(?:recompile|defer|deferred|owner\s+accepted|accepted\s+risk|waive|waived|carry|carried|risk|block|blocked)\b",
    re.IGNORECASE,
)


def normalize_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug


def heading_pattern(level: str, heading: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(level)}\s+{re.escape(heading)}\s*$", re.MULTILINE)


def section_content(text: str, heading: str) -> str | None:
    pattern = heading_pattern("##", heading)
    match = pattern.search(text)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    content = text[start:end].strip()
    lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def level_two_heading_slugs(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE):
        heading = match.group(1).strip()
        result[slugify(heading)] = heading
    return result


def has_placeholder(text: str) -> bool:
    return bool(PLACEHOLDER_RE.search(text))


def parse_markdown_table(section: str) -> tuple[list[str], list[dict[str, str]]]:
    table_lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return [], []
    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return header, rows


def parse_optional_table(text: str, heading: str) -> tuple[list[str], list[dict[str, str]]]:
    section = section_content(text, heading)
    if section is None:
        return [], []
    return parse_markdown_table(section)


def normalize_table_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_anchor(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"^#+", "", value).strip()
    match = re.fullmatch(r"\[([^\]]+)\]\([^)]*\)", value)
    if match:
        value = match.group(1).strip()
    return value.strip().strip("`").strip()


def split_anchor_list(value: str) -> list[str]:
    cleaned = re.sub(r"<br\s*/?>", ",", value, flags=re.IGNORECASE)
    parts = re.split(r"[,;；，、\n]+", cleaned)
    return [anchor for part in parts if (anchor := normalize_anchor(part))]


def first_present(row: dict[str, str], names: list[str]) -> str:
    lowered = {normalize_heading(k): v for k, v in row.items()}
    for name in names:
        value = lowered.get(normalize_heading(name), "")
        if value:
            return value.strip()
    return ""


def status_is_unavailable(value: str) -> bool:
    normalized = normalize_table_value(value)
    if not normalized or RECOMPILE_NOT_REQUIRED_RE.search(normalized):
        return False
    return bool(UNAVAILABLE_VISUAL_STATUS_RE.search(normalized))


def requires_recompile(value: str) -> bool:
    normalized = normalize_table_value(value)
    if not normalized or RECOMPILE_NOT_REQUIRED_RE.search(normalized):
        return False
    return bool(RECOMPILE_REQUIRED_RE.search(normalized))


def row_has_real_values(row: dict[str, str]) -> bool:
    values = [normalize_table_value(value) for value in row.values()]
    return any(value and not has_placeholder(value) and not RECOMPILE_NOT_REQUIRED_RE.fullmatch(value) for value in values)


def validate_template_surface(errors: list[str]) -> None:
    template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    if not template_dir.is_dir():
        errors.append(f"template surface missing: {template_dir}")
        return
    actual = {path.name for path in template_dir.glob("*.md")}
    expected = set(REQUIRED_FILES)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"template surface missing required templates: {', '.join(missing)}")
    if extra:
        errors.append(f"template surface has unexpected public templates: {', '.join(extra)}")


def parse_anchor(pointer: str, contents: dict[str, str]) -> tuple[str | None, str | None, str | None]:
    for file_name in REQUIRED_FILES:
        if file_name not in pointer:
            continue
        after = pointer.split(file_name, 1)[1].strip()
        if not after.startswith("#"):
            return file_name, None, "missing #section anchor"
        raw_anchor = after[1:].strip().strip("#").strip("`")
        if not raw_anchor:
            return file_name, None, "empty section anchor"
        return file_name, slugify(raw_anchor), None
    return None, None, "missing workspace file reference"


def validate_filled_pointer(row_label: str, pointer: str, contents: dict[str, str], errors: list[str]) -> None:
    file_name, anchor_slug, error = parse_anchor(pointer, contents)
    if error:
        errors.append(f"{row_label}: filled pointer must name an existing workspace file plus #section anchor ({error})")
        return
    if file_name is None or file_name not in contents:
        errors.append(f"{row_label}: filled pointer references missing workspace file")
        return
    assert anchor_slug is not None
    slugs = level_two_heading_slugs(contents[file_name])
    heading = slugs.get(anchor_slug)
    if heading is None:
        errors.append(f"{row_label}: filled pointer section anchor must target an existing ## section in {file_name}: #{anchor_slug}")
        return
    content = section_content(contents[file_name], heading)
    if content is not None and (not content.strip() or has_placeholder(content)):
        errors.append(f"{row_label}: filled pointer target section is empty or placeholder: {file_name}#{anchor_slug}")


def validate_dimension_index(text: str, contents: dict[str, str], errors: list[str]) -> dict[str, dict[str, str]]:
    rows_by_id: dict[str, dict[str, str]] = {}
    section = section_content(text, "Dimension Status Index")
    if section is None:
        errors.append(f"{DIMENSION_INDEX}: missing ## Dimension Status Index")
        return rows_by_id
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{DIMENSION_INDEX}: Dimension Status Index must contain a Markdown table with D00-D19 rows")
        return rows_by_id
    if header != DIMENSION_COLUMNS:
        errors.append(
            f"{DIMENSION_INDEX}: Dimension Status Index columns must be exactly: "
            + " | ".join(DIMENSION_COLUMNS)
        )

    seen: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        label = f"{DIMENSION_INDEX}: Dimension Status Index row {idx}"
        dim_id = first_present(row, ["ID"])
        dimension = first_present(row, ["Dimension"])
        current_home = first_present(row, ["Current home"])
        status = first_present(row, ["Status"]).lower()
        reason = first_present(row, ["Reason / owner note"])
        pointer = first_present(row, ["Pointer or handoff"])
        blocks = first_present(row, ["Blocks design pack?"]).lower()

        if not dim_id:
            errors.append(f"{label}: ID is missing")
            continue
        if dim_id in seen:
            errors.append(f"{label}: duplicate dimension ID {dim_id}")
        seen.add(dim_id)
        rows_by_id[dim_id] = row
        if dim_id not in REQUIRED_DIMENSION_IDS:
            errors.append(f"{label}: unexpected dimension ID {dim_id}")
        if not dimension or has_placeholder(dimension):
            errors.append(f"{label}: Dimension is missing or placeholder")
        if not current_home or has_placeholder(current_home):
            errors.append(f"{label}: Current home is missing or placeholder")
        if status not in VALID_DIMENSION_STATUSES:
            errors.append(f"{label}: invalid Status {status!r}; expected one of {', '.join(sorted(VALID_DIMENSION_STATUSES))}")
        if not reason or has_placeholder(reason):
            errors.append(f"{label}: Reason / owner note is missing or placeholder")
        if not pointer or has_placeholder(pointer):
            errors.append(f"{label}: Pointer or handoff is missing or placeholder")
        if blocks not in VALID_BLOCKS_VALUES:
            errors.append(f"{label}: Blocks design pack? must be yes or no")
        if status == "filled" and pointer and not has_placeholder(pointer):
            validate_filled_pointer(label, pointer, contents, errors)

    missing = sorted(REQUIRED_DIMENSION_IDS - seen)
    if missing:
        errors.append(f"{DIMENSION_INDEX}: missing required dimension IDs: {', '.join(missing)}")
    return rows_by_id


def validate_evidence_inventory(text: str, errors: list[str]) -> tuple[set[str], set[str]]:
    file_name = "01_MATERIALS_INVENTORY.md"
    section = section_content(text, "Evidence Inventory")
    if section is None:
        errors.append(f"{file_name}: missing ## Evidence Inventory")
        return set(), set()
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{file_name}: Evidence Inventory must contain a Markdown table with evidence anchors")
        return set(), set()

    anchors: set[str] = set()
    unavailable_anchors: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        label = f"{file_name}: Evidence Inventory row {idx}"
        anchor = first_present(row, ["Evidence anchor", "Evidence anchors", "Anchor", "ID"])
        status = first_present(row, ["Status"])
        if not anchor or has_placeholder(anchor):
            errors.append(f"{label}: evidence anchor is missing or placeholder")
            continue
        normalized = normalize_anchor(anchor)
        if not normalized:
            errors.append(f"{label}: evidence anchor is empty after normalization")
            continue
        if normalized in anchors:
            errors.append(f"{label}: duplicate evidence anchor {normalized}")
        anchors.add(normalized)
        if not status or has_placeholder(status):
            errors.append(f"{label}: status is required and must not be placeholder")
        elif status_is_unavailable(status):
            unavailable_anchors.add(normalized)
    return anchors, unavailable_anchors


def validate_claim_table(
    file_name: str,
    text: str,
    evidence_anchors: set[str],
    unavailable_evidence_anchors: set[str],
    unavailable_visual_anchors: set[str],
    errors: list[str],
) -> None:
    section = section_content(text, "Claim-Evidence Map")
    if section is None:
        errors.append(f"{file_name}: missing ## Claim-Evidence Map")
        return
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{file_name}: Claim-Evidence Map must contain a Markdown table with at least one claim row")
        return

    for idx, row in enumerate(rows, start=1):
        claim = first_present(row, ["Claim"])
        evidence = first_present(row, ["Evidence anchors", "Evidence", "Evidence anchor"])
        support = first_present(row, ["Support strength", "Support"])
        forbidden = first_present(row, ["Forbidden wording", "Forbidden"])
        status = first_present(row, ["Status"])
        status_key = re.sub(r"\s+", " ", status.lower().strip())
        deferred = status_key in DEFER_STATUSES

        label = f"{file_name}: Claim-Evidence Map row {idx}"
        if not claim or has_placeholder(claim):
            errors.append(f"{label}: claim is missing or placeholder")
        if not deferred and (not evidence or has_placeholder(evidence)):
            errors.append(f"{label}: evidence anchor is required unless status is deferred/rejected")
        elif not deferred:
            if ACTIVE_VISUAL_EVIDENCE_RE.search(evidence):
                errors.append(
                    f"{label}: active claim evidence explicitly cites a needed/deferred/absent visual; "
                    "D18 visual plans are structural only until backed by an available D06 evidence anchor"
                )
            anchors = split_anchor_list(evidence)
            if not anchors:
                errors.append(f"{label}: evidence anchor is required unless status is deferred/rejected")
            for anchor in anchors:
                if anchor.lower() in {"n/a", "na", "none", "absent"}:
                    errors.append(f"{label}: evidence anchor {anchor!r} requires deferred/rejected status")
                elif anchor not in evidence_anchors:
                    errors.append(f"{label}: evidence anchor {anchor!r} is not listed in 01_MATERIALS_INVENTORY.md#Evidence Inventory")
                elif anchor in unavailable_evidence_anchors:
                    errors.append(
                        f"{label}: evidence anchor {anchor!r} is marked needed/deferred/absent/planned in "
                        "01_MATERIALS_INVENTORY.md#Evidence Inventory and cannot support an active claim"
                    )
                elif anchor in unavailable_visual_anchors:
                    errors.append(
                        f"{label}: evidence anchor {anchor!r} is a needed/deferred/absent visual in D18 and "
                        "cannot support an active claim without available D06 evidence"
                    )
        if not support or has_placeholder(support):
            errors.append(f"{label}: support strength is required and must not be placeholder")
        if not forbidden or has_placeholder(forbidden):
            errors.append(f"{label}: forbidden wording is required and must not be placeholder")
        if FINAL_PACK == file_name and (not status or has_placeholder(status)):
            errors.append(f"{label}: final design pack requires explicit status")


def validate_dimension_coverage_summary(text: str, index_rows: dict[str, dict[str, str]], errors: list[str]) -> None:
    section = section_content(text, "Dimension Coverage Summary")
    if section is None:
        errors.append(f"{FINAL_PACK}: missing ## Dimension Coverage Summary")
        return
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{FINAL_PACK}: Dimension Coverage Summary must contain a Markdown table with D00-D19 rows")
        return
    if header != FINAL_COVERAGE_COLUMNS:
        errors.append(
            f"{FINAL_PACK}: Dimension Coverage Summary columns must be exactly: "
            + " | ".join(FINAL_COVERAGE_COLUMNS)
        )

    seen: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        label = f"{FINAL_PACK}: Dimension Coverage Summary row {idx}"
        dim_id = first_present(row, ["ID"])
        status = first_present(row, ["Status"]).lower()
        pointer = first_present(row, ["Pointer or handoff"])
        blocks = first_present(row, ["Blocks design pack?"]).lower()

        if not dim_id:
            errors.append(f"{label}: ID is missing")
            continue
        if dim_id in seen:
            errors.append(f"{label}: duplicate dimension ID {dim_id}")
        seen.add(dim_id)
        if dim_id not in REQUIRED_DIMENSION_IDS:
            errors.append(f"{label}: unexpected dimension ID {dim_id}")
        if status not in VALID_DIMENSION_STATUSES:
            errors.append(f"{label}: invalid Status {status!r}; expected one of {', '.join(sorted(VALID_DIMENSION_STATUSES))}")
        if not pointer or has_placeholder(pointer):
            errors.append(f"{label}: Pointer or handoff is missing or placeholder")
        if blocks not in VALID_BLOCKS_VALUES:
            errors.append(f"{label}: Blocks design pack? must be yes or no")

        index_row = index_rows.get(dim_id)
        if index_row:
            index_status = first_present(index_row, ["Status"]).lower()
            index_pointer = first_present(index_row, ["Pointer or handoff"])
            index_blocks = first_present(index_row, ["Blocks design pack?"]).lower()
            if status and index_status and status != index_status:
                errors.append(f"{label}: Status does not match {DIMENSION_INDEX} ({status!r} != {index_status!r})")
            if pointer and index_pointer and normalize_table_value(pointer) != normalize_table_value(index_pointer):
                errors.append(f"{label}: Pointer or handoff does not match {DIMENSION_INDEX}")
            if blocks and index_blocks and blocks != index_blocks:
                errors.append(f"{label}: Blocks design pack? does not match {DIMENSION_INDEX} ({blocks!r} != {index_blocks!r})")

    missing = sorted(REQUIRED_DIMENSION_IDS - seen)
    if missing:
        errors.append(f"{FINAL_PACK}: Dimension Coverage Summary missing required dimension IDs: {', '.join(missing)}")


def collect_unavailable_visual_anchors(contents: dict[str, str]) -> set[str]:
    unavailable: set[str] = set()
    visual_sources = [
        ("03_WRITING_STRUCTURE.md", "Visual Plan"),
        ("03_WRITING_STRUCTURE.md", "Figure / Table Storyline"),
        (FINAL_PACK, "Visual and Figure Storyline"),
    ]
    for file_name, heading in visual_sources:
        text = contents.get(file_name)
        if not text:
            continue
        _, rows = parse_optional_table(text, heading)
        for row in rows:
            visual_id = first_present(
                row,
                [
                    "Visual id",
                    "Visual/table id",
                    "Visual",
                    "Figure",
                    "Table",
                    "ID",
                    "Story step",
                ],
            )
            status_text = " ".join(
                first_present(row, names)
                for names in [
                    ["Type and status", "Status"],
                    ["Evidence boundary"],
                    ["Data/evidence needed"],
                    ["Handoff"],
                ]
            )
            if visual_id and not has_placeholder(visual_id) and status_is_unavailable(status_text):
                unavailable.add(normalize_anchor(visual_id))
    return unavailable


def validate_d19_handoff_structure(text: str, errors: list[str]) -> None:
    lower_text = text.lower()
    required_structural_phrases = [
        ("submission blueprint", "submission blueprint"),
        ("semantic-risk", "semantic-risk note"),
        ("External Skill Handoff", "external handoff route"),
        ("Validation Notes", "validation notes"),
    ]
    for phrase, label in required_structural_phrases:
        if phrase.lower() not in lower_text:
            errors.append(f"{FINAL_PACK}: missing D19 structural {label}; validation is structural, not semantic adequacy")

    blueprint_header, blueprint_rows = parse_optional_table(text, "Submission Blueprint")
    if blueprint_header and blueprint_header != ["Blueprint prompt", "Planned note or handoff", "Risk or constraint"]:
        errors.append(f"{FINAL_PACK}: Submission Blueprint columns changed; found {blueprint_header}")
    if blueprint_header and not blueprint_rows:
        errors.append(f"{FINAL_PACK}: Submission Blueprint must contain at least one structural handoff row")

    risk_header, risk_rows = parse_optional_table(text, "Semantic-Risk and Unresolved-Risk Notes")
    if risk_header and risk_header != ["Risk area", "Unresolved dimension/source", "Consequence or handoff"]:
        errors.append(f"{FINAL_PACK}: Semantic-Risk and Unresolved-Risk Notes columns changed; found {risk_header}")
    if risk_header and not risk_rows:
        errors.append(f"{FINAL_PACK}: Semantic-Risk and Unresolved-Risk Notes must contain at least one structural risk row")


def validate_stale_d19_consistency(
    final_text: str,
    index_rows: dict[str, dict[str, str]],
    errors: list[str],
) -> None:
    d02_row = index_rows.get("D02", {})
    d19_row = index_rows.get("D19", {})
    d02_status = first_present(d02_row, ["Status"]).lower()
    d02_reason_pointer = " ".join(
        [
            first_present(d02_row, ["Reason / owner note"]),
            first_present(d02_row, ["Pointer or handoff"]),
        ]
    )
    d19_status = first_present(d19_row, ["Status"]).lower()
    risk_validation_text = " ".join(
        section_content(final_text, heading) or ""
        for heading in ["Semantic-Risk and Unresolved-Risk Notes", "Validation Notes"]
    )

    stale_header, stale_rows = parse_optional_table(final_text, "D02 Stale Gate")
    if stale_header and stale_header != [
        "Changed dimension",
        "Affected pack section",
        "Stale since",
        "Recompile required?",
        "Owner decision / required action",
        "Semantic-risk note",
    ]:
        errors.append(f"{FINAL_PACK}: D02 Stale Gate columns changed; found {stale_header}")

    explicit_stale_from_index = d02_status in {"deferred", "rejected"} or bool(STALE_SIGNAL_RE.search(d02_reason_pointer))
    explicit_stale_from_table = False
    unresolved_recompile = False
    stale_row_texts: list[str] = []
    for idx, row in enumerate(stale_rows, start=1):
        if not row_has_real_values(row):
            continue
        label = f"{FINAL_PACK}: D02 Stale Gate row {idx}"
        changed_dimension = first_present(row, ["Changed dimension"])
        affected_section = first_present(row, ["Affected pack section"])
        stale_since = first_present(row, ["Stale since"])
        recompile = first_present(row, ["Recompile required?"])
        action = first_present(row, ["Owner decision / required action"])
        risk_note = first_present(row, ["Semantic-risk note"])
        row_text = " ".join([changed_dimension, affected_section, stale_since, recompile, action, risk_note])

        if has_placeholder(row_text):
            continue
        stale_row_texts.append(row_text)
        if STALE_SIGNAL_RE.search(row_text) or requires_recompile(recompile):
            explicit_stale_from_table = True
        if requires_recompile(recompile) and not STALE_ACTION_RE.search(" ".join([action, risk_note])):
            unresolved_recompile = True
            errors.append(
                f"{label}: structured stale data says recompile is required but lacks an owner action or semantic-risk handoff"
            )

    carried_stale_text = " ".join(stale_row_texts + [risk_validation_text])
    if stale_rows and explicit_stale_from_table and not STALE_SIGNAL_RE.search(carried_stale_text):
        errors.append(
            f"{FINAL_PACK}: structured D02 stale data exists but D19 risk/validation sections do not carry a stale or recompile note"
        )

    if explicit_stale_from_index and d19_status == "filled" and not STALE_SIGNAL_RE.search(carried_stale_text):
        errors.append(
            f"{DIMENSION_INDEX}: D02 carries stale/recompile risk while D19 is filled; "
            f"{FINAL_PACK} must carry an explicit structural stale-risk or recompile handoff"
        )

    if unresolved_recompile and d19_status == "filled":
        errors.append(
            f"{DIMENSION_INDEX}: D19 is filled while D02 structured stale data has unresolved recompile-required state"
        )


def validate_workspace(workspace: Path) -> list[str]:
    errors: list[str] = []
    validate_template_surface(errors)

    if not workspace.exists():
        return [f"workspace does not exist: {workspace}"]
    if not workspace.is_dir():
        return [f"workspace is not a directory: {workspace}"]

    root_markdown = {path.name for path in workspace.glob("*.md")}
    unexpected_markdown = sorted(root_markdown - set(REQUIRED_FILES))
    if unexpected_markdown:
        errors.append(f"workspace has unexpected public Markdown files: {', '.join(unexpected_markdown)}")

    contents: dict[str, str] = {}
    for file_name in REQUIRED_FILES:
        path = workspace / file_name
        if not path.is_file():
            errors.append(f"missing required file: {file_name}")
            continue
        text = path.read_text(encoding="utf-8")
        contents[file_name] = text
        for heading in REQUIRED_HEADINGS[file_name]:
            content = section_content(text, heading)
            if content is None:
                errors.append(f"{file_name}: missing required heading ## {heading}")
            elif not content.strip():
                errors.append(f"{file_name}: section ## {heading} is empty")
            elif has_placeholder(content):
                errors.append(f"{file_name}: section ## {heading} contains unresolved placeholder")

    index_rows: dict[str, dict[str, str]] = {}
    if DIMENSION_INDEX in contents:
        index_rows = validate_dimension_index(contents[DIMENSION_INDEX], contents, errors)

    evidence_anchors: set[str] = set()
    unavailable_evidence_anchors: set[str] = set()
    if "01_MATERIALS_INVENTORY.md" in contents:
        evidence_anchors, unavailable_evidence_anchors = validate_evidence_inventory(
            contents["01_MATERIALS_INVENTORY.md"], errors
        )

    unavailable_visual_anchors = collect_unavailable_visual_anchors(contents)

    if FINAL_PACK in contents:
        validate_dimension_coverage_summary(contents[FINAL_PACK], index_rows, errors)
        validate_d19_handoff_structure(contents[FINAL_PACK], errors)
        validate_stale_d19_consistency(contents[FINAL_PACK], index_rows, errors)
        if has_placeholder(contents[FINAL_PACK]):
            errors.append(f"{FINAL_PACK}: final handoff contains unresolved placeholder")

    for file_name in CLAIM_FILES:
        if file_name in contents:
            validate_claim_table(
                file_name,
                contents[file_name],
                evidence_anchors,
                unavailable_evidence_anchors,
                unavailable_visual_anchors,
                errors,
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a yxj-paper-os six-file design-pack workspace.")
    parser.add_argument("workspace", type=Path, help="Directory containing the six yxj paper-planning Markdown files")
    args = parser.parse_args()

    errors = validate_workspace(args.workspace)
    if errors:
        print("Design pack validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Structural design-pack validation passed: {args.workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
