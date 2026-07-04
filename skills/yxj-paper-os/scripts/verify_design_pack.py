#!/usr/bin/env python3
"""Lightweight yxj-paper-os design-pack validator.

Checks structural readiness for the six-file workspace. It does not judge
writing quality, search citations, run external skills, or model a runtime
graph.
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
        "Drafting Constraints",
    ],
    FINAL_PACK: [
        "Dimension Coverage Summary",
        "Project Route",
        "Material Boundary",
        "Source / Citation Boundary",
        "Research Dossier Notes",
        "Core Contribution",
        "Claim-Evidence Map",
        "Allowed Wording",
        "Forbidden Wording",
        "Limitations and Risks",
        "Reader Spine",
        "Writing Structure",
        "Visual and Figure Storyline",
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

PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|REPLACE_ME|UNKNOWN)\b|\[\s*\.\.\.\s*\]", re.IGNORECASE)
CLAIM_FILES = ("02_CLAIM_EVIDENCE_BOUNDARY.md", FINAL_PACK)
DEFER_STATUSES = {"deferred", "rejected", "not claimed", "not-claimed"}


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


def first_present(row: dict[str, str], names: list[str]) -> str:
    lowered = {normalize_heading(k): v for k, v in row.items()}
    for name in names:
        value = lowered.get(normalize_heading(name), "")
        if value:
            return value.strip()
    return ""


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


def validate_dimension_index(text: str, contents: dict[str, str], errors: list[str]) -> None:
    section = section_content(text, "Dimension Status Index")
    if section is None:
        errors.append(f"{DIMENSION_INDEX}: missing ## Dimension Status Index")
        return
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{DIMENSION_INDEX}: Dimension Status Index must contain a Markdown table with D00-D19 rows")
        return
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


def validate_claim_table(file_name: str, text: str, errors: list[str]) -> None:
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
        if not support or has_placeholder(support):
            errors.append(f"{label}: support strength is required and must not be placeholder")
        if not forbidden or has_placeholder(forbidden):
            errors.append(f"{label}: forbidden wording is required and must not be placeholder")
        if FINAL_PACK == file_name and (not status or has_placeholder(status)):
            errors.append(f"{label}: final design pack requires explicit status")


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

    if DIMENSION_INDEX in contents:
        validate_dimension_index(contents[DIMENSION_INDEX], contents, errors)

    if FINAL_PACK in contents and has_placeholder(contents[FINAL_PACK]):
        errors.append(f"{FINAL_PACK}: final handoff contains unresolved placeholder")

    for file_name in CLAIM_FILES:
        if file_name in contents:
            validate_claim_table(file_name, contents[file_name], errors)

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
