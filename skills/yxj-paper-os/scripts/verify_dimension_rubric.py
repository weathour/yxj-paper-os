#!/usr/bin/env python3
"""Bounded static check for the schema-0.3 public planning contract."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"
TEMPLATES = ROOT / "assets" / "templates"
PUBLIC_FILES = [
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
]
REQUIRED_REFERENCES = [
    "00-dimension-rubric.md",
    "00-project-route.md",
    "01-materials-inventory.md",
    "02-claim-evidence-boundary.md",
    "03-writing-structure.md",
    "04-design-pack-compiler.md",
]
INDEX_COLUMNS = [
    "ID",
    "Dimension",
    "Current home",
    "Status",
    "Reason / owner note",
    "Pointer or handoff",
    "Blocks design pack?",
]
SURFACE_KEYS = [
    "section_paragraph_map",
    "surface_language_contract",
    "visual_caption_blueprint",
    "cross_surface_traceability",
    "template_rule_provenance",
    "soft_budgets",
    "important_paragraph_frames",
]
EXACT_HEADERS = {
    ("00_PROJECT_ROUTE.md", "Decision Records"): [
        "Decision ID",
        "Gate category",
        "Issue / options / decision",
        "Affected scopes",
        "Origin",
        "Resolution",
        "Grounding / owner-answer pointer",
        "Recheck trigger",
    ],
    ("01_MATERIALS_INVENTORY.md", "Template Design Sources"): [
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
    ],
    ("04_WRITING_DESIGN_PACK.md", "Template Analysis Handling"): [
        "Scope ID",
        "Mode",
        "Semantic dossier pointer",
        "Quantitative analysis pointer(s)",
        "Generic fallback pointer(s)",
        "Firewall state",
        "Rationale",
        "Active blocker IDs",
    ],
    ("04_WRITING_DESIGN_PACK.md", "Scoped Handoff"): [
        "Scope ID",
        "00 scope-row pointer",
        "Detailed coverage pointer",
        "Output pointer",
        "Active blocker IDs",
        "Downstream prohibitions",
        "Handoff note",
    ],
}
QUESTION_DEPTH_LADDER_FIELDS: list[str] = []


def section(text: str, heading: str) -> str | None:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return None
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.M)
    return tail[: next_heading.start()] if next_heading else tail


def table(text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    body = section(text, heading)
    if body is None:
        return [], []
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return [], []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    return cells(lines[0]), [cells(line) for line in lines[2:]]


def main() -> int:
    errors = [
        f"missing reference: {name}"
        for name in REQUIRED_REFERENCES
        if not (REF / name).is_file()
    ]
    present = sorted(path.name for path in TEMPLATES.glob("*.md"))
    if present != PUBLIC_FILES:
        errors.append("public templates must remain the exact six-file set")

    contents = {
        name: (TEMPLATES / name).read_text(encoding="utf-8")
        for name in PUBLIC_FILES
        if (TEMPLATES / name).is_file()
    }
    index = contents.get("00_DIMENSION_INDEX.md", "")
    if "Workspace schema version: 0.3" not in index:
        errors.append("workspace schema marker must be 0.3")
    header, rows = table(index, "Dimension Status Index")
    if header != INDEX_COLUMNS:
        errors.append("public dimension-index columns changed")
    if [row[0] for row in rows if row] != [f"D{i:02d}" for i in range(20)]:
        errors.append("D00-D19 must appear exactly once and in order")

    for (name, heading), expected in EXACT_HEADERS.items():
        actual, _ = table(contents.get(name, ""), heading)
        if actual != expected:
            errors.append(f"{name}#{heading}: exact columns changed")
    handoff = EXACT_HEADERS[("04_WRITING_DESIGN_PACK.md", "Scoped Handoff")]
    if "Readiness" in handoff:
        errors.append("04 Scoped Handoff must not copy Readiness")

    rubric = (
        (REF / "00-dimension-rubric.md").read_text(encoding="utf-8")
        if (REF / "00-dimension-rubric.md").is_file()
        else ""
    )
    rubric_ids = re.findall(r"^### (D(?:0[0-9]|1[0-9]))\s+—", rubric, re.M)
    if rubric_ids != [f"D{i:02d}" for i in range(20)]:
        errors.append("rubric canonical D00-D19 entries changed")
    _, surface_rows = table(rubric, "Canonical Detailed Surfaces")
    if [row[0] for row in surface_rows if row] != SURFACE_KEYS:
        errors.append("seven canonical detailed-surface keys changed")

    required_grammar = [
        "^D(?:0[0-9]&#124;1[0-9])$",
        "^M-[a-z0-9]+(?:-[a-z0-9]+)*$",
        "^C-[a-z0-9]+(?:-[a-z0-9]+)*$",
        "ASCII semicolon",
        "none;M-example",
        "03_WRITING_STRUCTURE.md#Controlled Sentence Frames",
        ".yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-example",
        ".yxj-paper-os/template-analysis/design-profile.json#entries.example",
        "lens:argument-language-visual#sufficiency-predicates",
        "fulfills;qualifies;limits;introduces;calls_out;visualizes;depends_on;contrasts_with;hands_off_to",
        "&#124;",
        "<br>",
    ]
    for token in required_grammar:
        if token not in rubric:
            errors.append(f"rubric grammar token missing: {token}")

    compiler = (
        (REF / "04-design-pack-compiler.md").read_text(encoding="utf-8").lower()
        if (REF / "04-design-pack-compiler.md").is_file()
        else ""
    )
    for token in (
        "schema 0.2",
        "schema 0.3",
        "agent-led",
        "non-destructive",
        "no automatic migration",
    ):
        if token not in compiler:
            errors.append(f"legacy recompilation contract missing: {token}")

    if errors:
        print(
            "Schema 0.3 rubric validation failed:",
            *[f"- {error}" for error in errors],
            sep="\n",
        )
        return 1
    print("Schema 0.3 rubric structural validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
