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
        "Front Matter / Hook Route Constraints",
        "Topic and Positioning",
        "Audience and Reviewer Expectation",
        "Owner Decisions",
        "Reporting, Statements, and Downstream Route Seed",
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
        "Citation Function and Related-Work Materials",
        "Method / Reporting / Reproducibility Materials",
        "Results / Visual / Caption / Accessibility Materials",
        "Existing Text Fragments",
        "Explicit Absences",
    ],
    "02_CLAIM_EVIDENCE_BOUNDARY.md": [
        "Problem / Object / Contribution",
        "Contribution Options",
        "Object Granularity",
        "Claim-Evidence Map",
        "Claim Support Boundary Reminder",
        "Writing-Surface Claim Boundary Matrix",
        "Front-Matter and Caption Wording Constraints",
        "Allowed Wording",
        "Forbidden Wording",
        "Deferred or Rejected Claims",
        "Limitations and Risks",
    ],
    "03_WRITING_STRUCTURE.md": [
        "Exemplar Language Profile",
        "Front-Matter / Hook Planning Brief",
        "Reader Spine",
        "Introduction / Related-Work Move Sequence",
        "Manuscript Outline",
        "Section Jobs",
        "Method / Reporting / Reproducibility Job Plan",
        "Object Granularity",
        "Surface Control",
        "Figure / Table Storyline",
        "Visual Plan",
        "Results Narrative / Caption / Accessibility Plan",
        "Paragraph / Function Map",
        "Drafting Constraints",
    ],
    FINAL_PACK: [
        "Dimension Coverage Summary",
        "Six-Track Coverage",
        "Project Route",
        "Front-Matter / Hook Planning Handoff",
        "Introduction / Related-Work / Citation Function Handoff",
        "Method / Reporting / Reproducibility Handoff",
        "Results / Visual / Captions / Tables / Accessibility Handoff",
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
        "Downstream Route Matrix",
        "External Skill Handoff",
        "Template and Mechanical Validator Notes",
        "Validation Notes",
    ],
}

REQUIRED_DIMENSION_IDS = {f"D{i:02d}" for i in range(20)}
CURRENT_DIMENSION_NAMES = {
    "D00": "Workspace metadata",
    "D01": "Owner decisions",
    "D02": "Stale/readiness flags",
    "D03": "Project brief",
    "D04": "Target route profile",
    "D05": "Material inventory",
    "D06": "Evidence inventory",
    "D07": "Source and citation bank",
    "D08": "Research dossier",
    "D09": "Exemplar language profile",
    "D10": "Contribution options",
    "D11": "Claim-evidence map",
    "D12": "Wording boundary",
    "D13": "Limitation and risk matrix",
    "D14": "Reader spine",
    "D15": "Manuscript outline",
    "D16": "Object granularity",
    "D17": "Surface control",
    "D18": "Visual plan",
    "D19": "Writing design pack",
}
RETIRED_STAGE_RE = re.compile(r"\bS\d{2}\b|\bG0[12]\b", re.IGNORECASE)
RETIRED_DIMENSION_LABEL_RE = re.compile(
    r"\b(?:"
    r"(?:0[0-4]|1[0-5])_[a-z][A-Za-z0-9_]*"
    r"|2[0-5]_[A-Za-z][A-Za-z0-9_]*"
    r"|00_" + r"META"
    r"|" + r"OWNER_" + r"DECISIONS"
    r"|" + r"STALE_" + r"FLAGS"
    r")\.md\b"
)
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
SOURCE_ABSENCE_RE = re.compile(
    r"\b(?:no\s+(?:sources?|citations?|references?)\s+(?:supplied|provided|available|known)|"
    r"none\s+(?:supplied|provided|available|known)|not\s+(?:supplied|provided)|"
    r"absent|deferred|missing|unavailable|no\s+citation\s+task|no\s+source\s+detail)\b",
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
SIX_TRACK_KEYS = {
    "front_matter_hook": "Front matter / hook",
    "intro_related_citation": "Introduction / related work / citation function",
    "method_reporting_repro": "Method / reporting / reproducibility",
    "results_visual_caption_accessibility": "Results / visual narrative / captions / tables / accessibility",
    "downstream_route_matrix": "Downstream route matrix",
    "templates_validators": "Templates + validators",
}
SIX_TRACK_COLUMNS = [
    "Track",
    "Input planning field locations",
    "Design-pack output location",
    "Boundary note",
]
SIX_TRACK_EXPECTED_INPUTS = {
    "front_matter_hook": [
        "00_PROJECT_ROUTE.md#Front Matter / Hook Route Constraints",
        "03_WRITING_STRUCTURE.md#Front-Matter / Hook Planning Brief",
    ],
    "intro_related_citation": [
        "01_MATERIALS_INVENTORY.md#Citation Function and Related-Work Materials",
        "02_CLAIM_EVIDENCE_BOUNDARY.md#Writing-Surface Claim Boundary Matrix",
        "03_WRITING_STRUCTURE.md#Introduction / Related-Work Move Sequence",
    ],
    "method_reporting_repro": [
        "00_PROJECT_ROUTE.md#Reporting, Statements, and Downstream Route Seed",
        "01_MATERIALS_INVENTORY.md#Method / Reporting / Reproducibility Materials",
        "03_WRITING_STRUCTURE.md#Method / Reporting / Reproducibility Job Plan",
    ],
    "results_visual_caption_accessibility": [
        "01_MATERIALS_INVENTORY.md#Results / Visual / Caption / Accessibility Materials",
        "03_WRITING_STRUCTURE.md#Results Narrative / Caption / Accessibility Plan",
    ],
    "downstream_route_matrix": [
        "00_PROJECT_ROUTE.md#Reporting, Statements, and Downstream Route Seed",
        f"{FINAL_PACK}#External Skill Handoff",
    ],
    "templates_validators": [
        f"{DIMENSION_INDEX}#Dimension Status Index",
        f"{FINAL_PACK}#Template and Mechanical Validator Notes",
        f"{FINAL_PACK}#Validation Notes",
    ],
}
SIX_TRACK_EXPECTED_OUTPUTS = {
    "front_matter_hook": f"{FINAL_PACK}#Front-Matter / Hook Planning Handoff",
    "intro_related_citation": f"{FINAL_PACK}#Introduction / Related-Work / Citation Function Handoff",
    "method_reporting_repro": f"{FINAL_PACK}#Method / Reporting / Reproducibility Handoff",
    "results_visual_caption_accessibility": f"{FINAL_PACK}#Results / Visual / Captions / Tables / Accessibility Handoff",
    "downstream_route_matrix": f"{FINAL_PACK}#Downstream Route Matrix",
    "templates_validators": f"{FINAL_PACK}#Template and Mechanical Validator Notes",
}
FINAL_HANDOFF_TABLES = {
    "Front-Matter / Hook Planning Handoff": [
        "Front-matter unit",
        "Constraint / owner-gated input",
        "Source dimensions",
        "Downstream handoff note",
    ],
    "Introduction / Related-Work / Citation Function Handoff": [
        "Handoff item",
        "Source planning location",
        "Required boundary",
        "Downstream note",
    ],
    "Method / Reporting / Reproducibility Handoff": [
        "Handoff item",
        "Artifact / checklist state",
        "Required statement or limitation",
        "Downstream note",
    ],
    "Results / Visual / Captions / Tables / Accessibility Handoff": [
        "Handoff item",
        "Evidence or visual status",
        "Caption/table/accessibility constraint",
        "Downstream note",
    ],
    "Template and Mechanical Validator Notes": [
        "Check surface",
        "Expected structural evidence",
        "Boundary / non-goal",
    ],
}
DOWNSTREAM_ROUTE_COLUMNS = [
    "Downstream route",
    "Eligible input sections",
    "Constraints to pass forward",
    "Blocker / defer note",
]
DOWNSTREAM_ROUTE_CATEGORIES = {
    "writing",
    "citation",
    "figure",
    "review",
    "defer",
}
FINAL_HANDOFF_REQUIRED_PATTERNS = [
    (re.compile(r"\bfinal\s+yxj[-\s]+paper[-\s]+os\s+handoff\b", re.IGNORECASE), "Final yxj-paper-os handoff"),
    (re.compile(r"\bpack\s+status\s*:", re.IGNORECASE), "Pack status"),
    (
        re.compile(
            rf"\bready\s+for\s*:\s*downstream\s+writing\s+planning\b[^.\n]*\b{re.escape(FINAL_PACK)}\b",
            re.IGNORECASE,
        ),
        "Ready for downstream writing planning from 04_WRITING_DESIGN_PACK.md",
    ),
    (
        re.compile(
            r"\bnot\s+ready\s+for\s*:[^\n]*final\s+citations[^\n]*manuscript[-\s]+ready\s+prose"
            r"[^\n]*submission[^\n]*publication[^\n]*acceptance[^\n]*semantic\s+adequacy",
            re.IGNORECASE,
        ),
        "bounded Not ready for final citations/manuscript/submission/publication/acceptance/semantic adequacy",
    ),
    (re.compile(r"\bvalidation\s*:", re.IGNORECASE), "Validation"),
    (
        re.compile(r"\bremaining\s+deferred\s*/\s*absent\s*/\s*rejected\s+items\s*:", re.IGNORECASE),
        "Remaining deferred/absent/rejected items",
    ),
    (re.compile(r"\brecommended\s+downstream\s+route", re.IGNORECASE), "Recommended downstream route(s)"),
    (
        re.compile(
            r"\bno\s+external\s+(?:route|skill|handoff|module)\s+(?:executed|run|invoked)\b|"
            r"\bexternal\s+(?:route|skill|handoff|module)\s+(?:was\s+)?not\s+(?:executed|run|invoked)\b",
            re.IGNORECASE,
        ),
        "no external route executed boundary",
    ),
]
CLAUSE_SPLIT_RE = re.compile(r"[|;:：.。\n]+|\bbut\b", re.IGNORECASE)
NEGATED_EXTERNAL_EXECUTION_RE = re.compile(
    r"\b(?:not|never)\s+(?:executed|run|ran|invoked|called|launched|completed)\b|"
    r"\b(?:do|does|did|must|should|will)\s+not\s+(?:execute|run|invoke|call|launch|complete)\b|"
    r"\bwithout\s+(?:executing|running|invoking|calling|launching|completing)\b|"
    r"\bno\b[^|;:.\n]{0,80}?\b(?:executed|run|ran|invoked|called|launched|completed|execution)\b",
    re.IGNORECASE,
)
NEGATED_FORBIDDEN_PROMISE_RE = re.compile(
    r"\b(?:(?:do|does|did|must|should|will|can)\s+not|cannot|can't|never|without|forbid(?:s|den)?|forbidden)\b"
    r"[^|;:.\n]{0,80}?\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|"
    r"manuscript[-\s]+(?:quality|readiness)|actual\s+venue\s+fit|venue\s+fit|novelty|"
    r"source\s+authority|citation\s+truth|bibliography\s+correctness|argument\s+persuasiveness|"
    r"prose\s+quality|style\s+similarity|visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:not|never)\s+(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:do|does|did|must|should|will|can)\s+not\s+"
    r"(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:cannot|can't|without|avoid|forbid|forbids|forbidden|remove|reject|rejected)\b[^|;:.\n]{0,80}?"
    r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:no|without)\b[^|;:.\n]{0,80}?\b(?:semantic\s+scor(?:e|er|ing)|readiness\s+certification|"
    r"publication\s+readiness|submission\s+readiness|acceptance\s+prediction)\b",
    re.IGNORECASE,
)
EXTERNAL_SKILL_EXECUTION_RE = re.compile(
    r"\b(?:executed|execute|ran|run|invoked|invoke|called|call|launched|launch|completed|complete)\b"
    r"[^.\n|;:]{0,80}\b(?:external|downstream|writing|citation|figure|review|polish(?:ing)?|data|pdf|backend|library)\b"
    r"[^.\n|;:]{0,40}\b(?:skill|tool|route|module)\b|"
    r"\b(?:external|downstream|writing|citation|figure|review|polish(?:ing)?|data|pdf|backend|library)\b"
    r"[^.\n|;:]{0,60}\b(?:skill|tool|route|module)\b"
    r"[^.\n|;:]{0,80}\b(?:executed|ran|run|invoked|called|launched|completed)\b",
    re.IGNORECASE,
)
FORBIDDEN_SEMANTIC_PROMISE_PATTERNS = [
    (
        re.compile(
            r"\bclaim(?:s|ed|ing)?\s+(?:semantic[-\s]+adequacy|semantic[-\s]+readiness|paper\s+quality|"
            r"manuscript[-\s]+quality|manuscript[-\s]+readiness|actual\s+venue\s+fit|venue\s+fit|novelty|"
            r"source\s+authority|citation\s+truth|bibliography\s+correctness|argument\s+persuasiveness|"
            r"prose\s+quality|style\s+similarity|visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
            r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^.\n|;:]{0,60}"
            r"\b(?:semantic[-\s]+adequacy|paper\s+quality|manuscript[-\s]+quality|actual\s+venue\s+fit|venue\s+fit|"
            r"semantic[-\s]+readiness|manuscript[-\s]+readiness|novelty|source\s+authority|citation\s+truth|"
            r"bibliography\s+correctness|argument\s+persuasiveness|"
            r"prose\s+quality|style\s+similarity|visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b",
            re.IGNORECASE,
        ),
        "semantic scoring promise",
    ),
    (
        re.compile(
            r"\b(?:manuscript|submission|publication|acceptance|semantic)[-\s]+readiness\b"
            r"[^.\n|;:]{0,60}\b(?:passed|validated|verified|certified|approved|ready)\b|"
            r"\bsemantic[-\s]+adequacy\b[^.\n|;:]{0,60}\b(?:passed|validated|verified|certified|approved|ready)\b|"
            r"\b(?:ready\s+for\s+submission|publication\s+ready|acceptance\s+likely)\b",
            re.IGNORECASE,
        ),
        "readiness promise",
    ),
]


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


def validate_retired_terms(file_name: str, text: str, errors: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        stage_match = RETIRED_STAGE_RE.search(line)
        if stage_match:
            errors.append(
                f"{file_name}: line {line_number} contains retired stage/governance token "
                f"{stage_match.group(0)!r}; use D00-D19 plus the five public phases instead"
            )
        label_match = RETIRED_DIMENSION_LABEL_RE.search(line)
        if label_match:
            errors.append(
                f"{file_name}: line {line_number} contains retired dimension filename label "
                f"{label_match.group(0)!r}; use the current semantic Dimension name instead"
            )


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
        elif dim_id in CURRENT_DIMENSION_NAMES and dimension != CURRENT_DIMENSION_NAMES[dim_id]:
            errors.append(
                f"{label}: Dimension must be current semantic name "
                f"{CURRENT_DIMENSION_NAMES[dim_id]!r}; found {dimension!r}"
            )
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


def is_supplied_source_detail(value: str) -> bool:
    normalized = normalize_table_value(value)
    if not normalized or has_placeholder(normalized):
        return False
    if RECOMPILE_NOT_REQUIRED_RE.fullmatch(normalized):
        return False
    return not bool(SOURCE_ABSENCE_RE.search(normalized))


def validate_d07_source_boundary(
    contents: dict[str, str],
    index_rows: dict[str, dict[str, str]],
    errors: list[str],
) -> None:
    d07_row = index_rows.get("D07")
    if not d07_row:
        return
    status = first_present(d07_row, ["Status"]).lower()
    if status != "filled":
        return

    inventory_text = contents.get("01_MATERIALS_INVENTORY.md", "")
    section = section_content(inventory_text, "Source and Citation Bank")
    if section is None:
        return

    header, rows = parse_markdown_table(section)
    detail_values: list[str] = []
    if header and rows:
        for row in rows:
            prompt = first_present(row, ["Source/citation prompt", "Prompt", "Source prompt", "Field"])
            detail = first_present(
                row,
                [
                    "Supplied detail or explicit absence/defer note",
                    "Source identity and locator/version",
                    "Source identity",
                    "Source",
                    "Citation",
                    "Reference",
                    "Locator",
                    "DOI",
                    "URL",
                ],
            )
            if prompt and not re.search(
                r"\b(?:source\s+identity|locator|candidate|reference|citation\s+candidate|known\s+source|supplied\s+source)\b",
                prompt,
                re.IGNORECASE,
            ):
                continue
            if detail:
                detail_values.append(detail)
    else:
        detail_values.append(section)

    if detail_values and any(is_supplied_source_detail(value) for value in detail_values):
        return

    errors.append(
        f"{DIMENSION_INDEX}: D07 is marked filled but "
        "01_MATERIALS_INVENTORY.md#Source and Citation Bank does not contain supplied source/citation detail; "
        "mark D07 absent or deferred with a no-invention handoff when no sources are supplied"
    )


def validate_final_handoff_card(text: str, errors: list[str]) -> None:
    validation_notes = section_content(text, "Validation Notes") or ""
    external_handoff = section_content(text, "External Skill Handoff") or ""
    search_text = "\n".join([validation_notes, external_handoff])
    for pattern, label in FINAL_HANDOFF_REQUIRED_PATTERNS:
        if not pattern.search(search_text):
            errors.append(f"{FINAL_PACK}: final handoff card missing required boundary field: {label}")


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

    validate_final_handoff_card(text, errors)


def claim_clauses(line: str) -> list[str]:
    return [clause.strip() for clause in CLAUSE_SPLIT_RE.split(line) if clause.strip()]


def has_unnegated_match(text: str, positive_pattern: re.Pattern[str], negated_pattern: re.Pattern[str]) -> bool:
    masked = list(text)
    for match in negated_pattern.finditer(text):
        start, end = match.span()
        masked[start:end] = " " * (end - start)
    return bool(positive_pattern.search("".join(masked)))


def contains_positive_external_execution(text: str) -> bool:
    for clause in claim_clauses(text):
        if has_unnegated_match(clause, EXTERNAL_SKILL_EXECUTION_RE, NEGATED_EXTERNAL_EXECUTION_RE):
            return True
    return False


def contains_positive_forbidden_promise(text: str, pattern: re.Pattern[str]) -> bool:
    for clause in claim_clauses(text):
        if has_unnegated_match(clause, pattern, NEGATED_FORBIDDEN_PROMISE_RE):
            return True
    return False


def validate_forbidden_claims(label: str, text: str, errors: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if contains_positive_external_execution(stripped):
            errors.append(
                f"{label}: line {line_number} appears to claim external/downstream skill execution; "
                "yxj-paper-os may recommend handoff routes only"
            )
        for pattern, promise_label in FORBIDDEN_SEMANTIC_PROMISE_PATTERNS:
            if contains_positive_forbidden_promise(stripped, pattern):
                errors.append(
                    f"{label}: line {line_number} appears to make a forbidden {promise_label}; "
                    "validation is mechanical only"
                )


def six_track_key(value: str) -> str | None:
    normalized = normalize_heading(value).replace("&", "and")
    if "front" in normalized and ("matter" in normalized or "hook" in normalized):
        return "front_matter_hook"
    if ("intro" in normalized or "introduction" in normalized) and (
        "related" in normalized or "citation" in normalized
    ):
        return "intro_related_citation"
    if "method" in normalized and ("report" in normalized or "repro" in normalized):
        return "method_reporting_repro"
    if "result" in normalized and (
        "visual" in normalized or "caption" in normalized or "table" in normalized or "accessibility" in normalized
    ):
        return "results_visual_caption_accessibility"
    if "downstream" in normalized and "route" in normalized:
        return "downstream_route_matrix"
    if "template" in normalized and "validator" in normalized:
        return "templates_validators"
    return None


def extract_dimension_ids(value: str) -> set[str]:
    return set(re.findall(r"\bD\d{2}\b", value))


def validate_expected_pointer(
    label: str,
    pointer: str,
    expected: str,
    contents: dict[str, str],
    errors: list[str],
    *,
    role: str,
) -> None:
    if expected not in pointer:
        errors.append(f"{label}: {role} must include canonical pointer {expected}")
        return
    validate_filled_pointer(label, expected, contents, errors)


def validate_final_handoff_tables(text: str, errors: list[str]) -> None:
    for heading, expected_header in FINAL_HANDOFF_TABLES.items():
        section = section_content(text, heading)
        if section is None:
            errors.append(f"{FINAL_PACK}: missing ## {heading}")
            continue
        header, rows = parse_markdown_table(section)
        if not header or not rows:
            errors.append(f"{FINAL_PACK}: {heading} must contain a Markdown table with structural handoff rows")
            continue
        if header != expected_header:
            errors.append(f"{FINAL_PACK}: {heading} columns must be exactly: " + " | ".join(expected_header))
        for idx, row in enumerate(rows, start=1):
            row_text = " ".join(row.values())
            if has_placeholder(row_text):
                errors.append(f"{FINAL_PACK}: {heading} row {idx} contains unresolved placeholder")
            if not row_has_real_values(row):
                errors.append(f"{FINAL_PACK}: {heading} row {idx} must contain at least one structural value")


def validate_six_track_coverage(text: str, contents: dict[str, str], errors: list[str]) -> None:
    section = section_content(text, "Six-Track Coverage")
    if section is None:
        errors.append(f"{FINAL_PACK}: missing ## Six-Track Coverage")
        return
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{FINAL_PACK}: Six-Track Coverage must contain a Markdown table with all six writing tracks")
        return
    if header != SIX_TRACK_COLUMNS:
        errors.append(f"{FINAL_PACK}: Six-Track Coverage columns must be exactly: " + " | ".join(SIX_TRACK_COLUMNS))

    seen: dict[str, int] = {}
    for idx, row in enumerate(rows, start=1):
        label = f"{FINAL_PACK}: Six-Track Coverage row {idx}"
        track = first_present(row, ["Track"])
        dims = first_present(row, ["Dimension IDs"])
        input_locations = first_present(row, ["Input planning field locations"])
        pointer = first_present(row, ["Design-pack output location", "Workspace/design-pack pointer", "Pointer or handoff"])
        boundary = first_present(row, ["Boundary note", "Boundary / non-goal", "Boundary"])

        if not track or has_placeholder(track):
            errors.append(f"{label}: Track is missing or placeholder")
            continue
        key = six_track_key(track)
        if key is None:
            errors.append(f"{label}: unknown six-track label {track!r}")
        elif key in seen:
            errors.append(f"{label}: duplicate six-track coverage row for {SIX_TRACK_KEYS[key]}")
        else:
            seen[key] = idx
            for expected in SIX_TRACK_EXPECTED_INPUTS[key]:
                validate_expected_pointer(
                    label,
                    input_locations,
                    expected,
                    contents,
                    errors,
                    role="Input planning field locations",
                )
            validate_expected_pointer(
                label,
                pointer,
                SIX_TRACK_EXPECTED_OUTPUTS[key],
                contents,
                errors,
                role="Design-pack output location",
            )

        if dims:
            dim_ids = extract_dimension_ids(dims)
            if not dim_ids:
                errors.append(f"{label}: Dimension IDs must name one or more D00-D19 IDs")
            unexpected = sorted(dim_ids - REQUIRED_DIMENSION_IDS)
            if unexpected:
                errors.append(f"{label}: Dimension IDs include unexpected IDs: {', '.join(unexpected)}")
        elif not input_locations or has_placeholder(input_locations):
            errors.append(f"{label}: Input planning field locations are missing or placeholder")
        if not pointer or has_placeholder(pointer):
            errors.append(f"{label}: Design-pack output location is missing or placeholder")
        else:
            validate_filled_pointer(label, pointer, contents, errors)
        if not boundary or has_placeholder(boundary):
            errors.append(f"{label}: Boundary / non-goal is missing or placeholder")

    missing = [name for key, name in SIX_TRACK_KEYS.items() if key not in seen]
    if missing:
        errors.append(f"{FINAL_PACK}: Six-Track Coverage missing required tracks: {', '.join(missing)}")


def validate_downstream_route_matrix(text: str, errors: list[str]) -> None:
    section = section_content(text, "Downstream Route Matrix")
    if section is None:
        errors.append(f"{FINAL_PACK}: missing ## Downstream Route Matrix")
        return
    header, rows = parse_markdown_table(section)
    if not header or not rows:
        errors.append(f"{FINAL_PACK}: Downstream Route Matrix must contain a Markdown table with handoff routes")
        return
    if header != DOWNSTREAM_ROUTE_COLUMNS:
        errors.append(f"{FINAL_PACK}: Downstream Route Matrix columns must be exactly: " + " | ".join(DOWNSTREAM_ROUTE_COLUMNS))

    seen_categories: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        label = f"{FINAL_PACK}: Downstream Route Matrix row {idx}"
        category = first_present(row, ["Downstream route", "External route category"])
        artifact = first_present(row, ["Eligible input sections", "Recommended handoff artifact"])
        execution = first_present(row, ["Constraints to pass forward", "Execution state"])
        boundary = first_present(row, ["Blocker / defer note", "Boundary / reason"])

        row_text = " ".join([category, artifact, execution, boundary])
        if has_placeholder(row_text):
            errors.append(f"{label}: downstream route matrix row contains unresolved placeholder")
        if not category:
            errors.append(f"{label}: Downstream route is required")
        if not artifact:
            errors.append(f"{label}: Eligible input sections are required")
        if not execution:
            errors.append(f"{label}: Constraints to pass forward are required")
        if not boundary:
            errors.append(f"{label}: Blocker / defer note is required")
        if contains_positive_external_execution(row_text):
            errors.append(f"{label}: Execution state appears to claim an external skill was executed")

        normalized = normalize_heading(category).replace("-", "/")
        if "writing" in normalized or "manuscript" in normalized or "polishing" in normalized:
            seen_categories.add("writing")
        if "citation" in normalized or "reference" in normalized:
            seen_categories.add("citation")
        if "figure" in normalized or "visual" in normalized:
            seen_categories.add("figure")
        if "review" in normalized or "qa" in normalized:
            seen_categories.add("review")
        if "defer" in normalized or "no external" in normalized or "no route" in normalized:
            seen_categories.add("defer")

    missing = sorted(DOWNSTREAM_ROUTE_CATEGORIES - seen_categories)
    if missing:
        errors.append(f"{FINAL_PACK}: Downstream Route Matrix missing route categories: {', '.join(missing)}")


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
        validate_retired_terms(file_name, text, errors)
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

    validate_d07_source_boundary(contents, index_rows, errors)

    unavailable_visual_anchors = collect_unavailable_visual_anchors(contents)

    if FINAL_PACK in contents:
        validate_dimension_coverage_summary(contents[FINAL_PACK], index_rows, errors)
        validate_d19_handoff_structure(contents[FINAL_PACK], errors)
        validate_six_track_coverage(contents[FINAL_PACK], contents, errors)
        validate_final_handoff_tables(contents[FINAL_PACK], errors)
        validate_stale_d19_consistency(contents[FINAL_PACK], index_rows, errors)
        validate_downstream_route_matrix(contents[FINAL_PACK], errors)
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

    for file_name, text in contents.items():
        validate_forbidden_claims(file_name, text, errors)

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
