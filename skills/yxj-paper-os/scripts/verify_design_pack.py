#!/usr/bin/env python3
"""Lightweight yxj-paper-os design-pack validator.

Checks only structural readiness. It does not judge writing quality, search
citations, run external skills, or model a runtime graph.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
]

REQUIRED_HEADINGS = {
    "00_PROJECT_ROUTE.md": [
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
        "Explicit Absences",
    ],
    "02_CLAIM_EVIDENCE_BOUNDARY.md": [
        "Problem / Object / Contribution",
        "Claim-Evidence Map",
        "Allowed Wording",
        "Forbidden Wording",
        "Deferred or Rejected Claims",
        "Limitations and Risks",
    ],
    "03_WRITING_STRUCTURE.md": [
        "Reader Spine",
        "Section Jobs",
        "Figure / Table Storyline",
        "Drafting Constraints",
    ],
    "04_WRITING_DESIGN_PACK.md": [
        "Project Route",
        "Material Boundary",
        "Core Contribution",
        "Claim-Evidence Map",
        "Allowed Wording",
        "Forbidden Wording",
        "Reader Spine",
        "Writing Structure",
        "Visual and Figure Storyline",
        "External Skill Handoff",
        "Validation Notes",
    ],
}

PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|REPLACE_ME|UNKNOWN)\b|\[\s*\.\.\.\s*\]", re.IGNORECASE)
FINAL_PACK = "04_WRITING_DESIGN_PACK.md"
CLAIM_FILES = ("02_CLAIM_EVIDENCE_BOUNDARY.md", "04_WRITING_DESIGN_PACK.md")
DEFER_STATUSES = {"deferred", "rejected", "not claimed", "not-claimed"}


def normalize_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


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
    if not workspace.exists():
        return [f"workspace does not exist: {workspace}"]
    if not workspace.is_dir():
        return [f"workspace is not a directory: {workspace}"]

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

    if FINAL_PACK in contents and has_placeholder(contents[FINAL_PACK]):
        errors.append(f"{FINAL_PACK}: final handoff contains unresolved placeholder")

    for file_name in CLAIM_FILES:
        if file_name in contents:
            validate_claim_table(file_name, contents[file_name], errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a yxj-paper-os design-pack workspace.")
    parser.add_argument("workspace", type=Path, help="Directory containing the five yxj paper-planning Markdown files")
    args = parser.parse_args()

    errors = validate_workspace(args.workspace)
    if errors:
        print("Design pack validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Design pack validation passed: {args.workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
