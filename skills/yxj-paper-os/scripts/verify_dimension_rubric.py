#!/usr/bin/env python3
"""Validate the yxj-paper-os internal D00-D19 dimension rubric.

This is a structural development check. It does not judge academic adequacy,
search citations, execute external skills, or change the public workspace schema.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent
RUBRIC = ROOT / "references" / "00-dimension-rubric.md"
SKILL = ROOT / "SKILL.md"
TEMPLATES = ROOT / "assets" / "templates"
INDEX_TEMPLATE = TEMPLATES / "00_DIMENSION_INDEX.md"
VALIDATOR = ROOT / "scripts" / "verify_design_pack.py"
TASK_PLAYBOOKS = [
    ROOT / "references" / "00-project-route.md",
    ROOT / "references" / "01-materials-inventory.md",
    ROOT / "references" / "02-claim-evidence-boundary.md",
    ROOT / "references" / "03-writing-structure.md",
    ROOT / "references" / "04-design-pack-compiler.md",
]
EXPECTED_PLAYBOOK_NAMES = {path.name for path in TASK_PLAYBOOKS}
EXPECTED_REFERENCE_FILES = EXPECTED_PLAYBOOK_NAMES | {"00-dimension-rubric.md"}
EXPECTED_TEMPLATES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}
REQUIRED_IDS = [f"D{i:02d}" for i in range(20)]
CRITICAL_STANDARD = "D04,D05,D06,D10,D11,D12,D13,D14,D15,D16,D17,D18"
REQUIRED_FIELDS = [
    "ID",
    "Name / legacy label",
    "Dimension type",
    "Purpose",
    "Primary home / write target",
    "Owner/source of truth",
    "Minimum sufficiency",
    "Standard sufficiency",
    "Ideal sufficiency",
    "Agent may propose?",
    "Owner confirmation required?",
    "Ask prompts",
    "Candidate options pattern",
    "Status examples",
    "Stop / defer / reject rule",
    "Common failure modes",
    "Downstream handoff note",
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
EXPECTED_STATUS_SET = {"filled", "not_applicable", "absent", "deferred", "rejected"}
FORBIDDEN_PUBLIC_SCHEMA_TERMS = {
    "tier",
    "minimum",
    "standard",
    "ideal",
    "currently_blocking",
    "currently blocking",
}
FIRST_BATCH_DIMENSIONS = ["D04", "D07", "D08", "D09", "D14", "D15", "D18", "D19", "D00", "D02"]
FIRST_BATCH_FIELD_LABELS = [
    "First-batch upgraded goal",
    "Field-category families / table intent",
    "Mechanical gate intent",
    "Cross-dimension dependencies",
    "Non-goals",
    "User-burden tier",
]
FIRST_BATCH_DIMENSION_PHRASES = {
    "D00": [
        "project slug",
        "owner/project identity",
        "created/updated timestamps",
        "last source revision",
        "readiness state",
        "ambiguity note",
        "semantic-adequacy disclaimer",
        "must not treat recent timestamps or completed metadata as semantic freshness or adequacy",
    ],
    "D02": [
        "Changed dimension",
        "affected pack section",
        "stale since",
        "recompile required",
        "owner decision",
        "required action",
        "semantic risk note",
        "obvious D19 incompatibility when structured stale data exists",
        "stale=false does not prove",
    ],
    "D04": [
        "Venue family",
        "article type",
        "content-fit intent",
        "format-fit intent",
        "reporting-fit intent",
        "primary audience",
        "reviewer expectation",
        "hard constraints",
        "forbidden routes",
        "owner confirmation state",
        "must not judge actual venue fit",
    ],
    "D07": [
        "source identity",
        "source role",
        "citation status",
        "owner confirmation",
        "locator such as DOI/URL/page/section/version",
        "key use",
        "limitation",
        "reuse permission",
        "handoff need",
        "source-to-claim support routes through D06 evidence anchors and D11 claim mapping",
    ],
    "D08": [
        "research/context boundary",
        "study-level notes",
        "theme-level synthesis",
        "conflict map",
        "gap hypothesis",
        "counterevidence",
        "unresolved source needs",
        "downstream consequence",
        "must not infer novelty",
    ],
    "D09": [
        "Exemplar status",
        "exemplar role",
        "positive style rules",
        "forbidden imitation",
        "voice/tense",
        "hedge strength",
        "terminology density",
        "banned patterns",
        "D12/D17 wording links",
        "must not judge prose quality, style similarity",
        "must not raise claim strength",
    ],
    "D14": [
        "Reader persona",
        "question sequence",
        "expected answer",
        "linked claim",
        "linked evidence",
        "linked limitation",
        "forbidden question",
        "transition rationale",
        "must not judge argument persuasiveness",
    ],
    "D15": [
        "Section",
        "job",
        "input dimensions",
        "output promise",
        "required evidence",
        "forbidden content",
        "length hint",
        "paragraph/function map",
        "downstream constraint",
        "must not judge rhetorical optimality",
    ],
    "D18": [
        "Visual id",
        "status such as existing/needed/deferred/absent",
        "story role",
        "linked claim",
        "linked evidence",
        "linked reader step",
        "data needed",
        "panel order",
        "legend job",
        "accessibility check",
        "handoff",
        "Needed/deferred visuals cannot support active claims",
        "must not validate figure quality, visual correctness",
    ],
    "D19": [
        "Dimension coverage",
        "submission blueprint",
        "semantic-risk note",
        "statement inventory",
        "supplement boundary",
        "external handoff routes",
        "unresolved dimension consequences",
        "validation notes",
        "must not claim manuscript, publication, submission, acceptance, or semantic readiness",
    ],
}
FIRST_BATCH_PLAYBOOK_PHRASES = {
    "00-project-route.md": [
        "## First-batch D04 route/profile pointer",
        "Separate owner-confirmed route from agent-inferred audience or reviewer expectation",
        "venue family, article type, content/format/reporting fit, primary audience, reviewer expectation, hard constraints, forbidden routes, and owner confirmation state",
        "D14 reader path, D15 section jobs, D18 visual format/storyline, and D19 submission blueprint",
        "must not judge actual venue fit, novelty, or acceptance likelihood",
    ],
    "01-materials-inventory.md": [
        "## First-batch D07/D08 source and dossier pointers",
        "source ≠ evidence ≠ claim",
        "cannot support or strengthen a claim unless a D06 evidence anchor exists and D11 maps the claim to that anchor",
        "source identity, source role, citation status, owner confirmation, locator/version or explicit absence, key use, limitation, reuse permission, and handoff need",
        "research/context boundary, study notes, theme synthesis, conflict map, gap hypothesis, counterevidence, unresolved source needs, and downstream consequence",
        "must not verify citation truth, source authority, novelty, or claim support",
    ],
    "02-claim-evidence-boundary.md": [
        "## First-batch cross-boundary reminder",
        "Sources, citation candidates, research dossier notes, exemplar/style guidance, design-pack summaries, and visual plans are not evidence anchors by themselves",
        "A claim may be supported only when D06 identifies a locatable evidence anchor and D11 maps the active claim to that anchor",
        "D09 can constrain style and D17 surface control; it cannot raise claim strength",
        "D18 can plan visuals; needed/deferred/absent visuals cannot support active claims",
        "D19 can summarize the boundary as a structural handoff",
    ],
    "03-writing-structure.md": [
        "## First-batch structure cards",
        "D09 style fingerprint",
        "exemplar status/role, positive style rules, forbidden imitation, voice/tense, hedge strength, terminology density, banned patterns, and D12/D17 wording links",
        "D14 reader spine",
        "reader persona, question sequence, expected answers, linked claim/evidence/limitation, forbidden questions, and transition rationale",
        "D15 section-job matrix",
        "input dimensions, output promise, required evidence, forbidden content, length or paragraph/function hints, and downstream constraints",
        "D18 visual storyline/brief",
        "visual id/type/status, story role, linked claim/evidence/reader step, data needed, panel order, legend job, accessibility check, and handoff",
        "must not judge prose quality, rhetoric, visual quality, or figure correctness",
    ],
    "04-design-pack-compiler.md": [
        "## First-batch D19/D02 handoff pointers",
        "D19 is a structural handoff/submission blueprint plus semantic-risk note",
        "dimension coverage, submission blueprint, statement inventory, supplement boundary, external handoff routes, unresolved dimension consequences, and validation notes",
        "D19 must not claim manuscript readiness, submission readiness, publication readiness, acceptance likelihood, novelty, citation truth, prose quality, visual quality, or semantic adequacy",
        "D02 stale gate should name category-family intent for changed dimension, affected pack section, stale since, recompile required, owner decision, required action, and semantic risk note",
        "A fresh D00/D02 state does not prove semantic adequacy",
        "stale/D19 incompatibility when explicitly structured",
        "must not execute external writing/citation/figure skills or score semantic quality",
    ],
}
MECHANICAL_BOUNDARY_PHRASES = [
    "structural",
    "does not judge",
]
FORBIDDEN_VALIDATOR_PROMISE_PATTERNS = [
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+(?:actual\s+)?venue fit\b", re.IGNORECASE), "venue fit"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+novelty\b", re.IGNORECASE), "novelty"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+source authority\b", re.IGNORECASE), "source authority"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+citation truth\b", re.IGNORECASE), "citation truth"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+bibliography correctness\b", re.IGNORECASE), "bibliography correctness"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+argument persuasiveness\b", re.IGNORECASE), "argument persuasiveness"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+prose quality\b", re.IGNORECASE), "prose quality"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+style similarity\b", re.IGNORECASE), "style similarity"),
    (re.compile(r"\b(?:validate|verify|judge|score|certify|prove)s?\s+visual (?:correctness|quality)\b", re.IGNORECASE), "visual correctness/quality"),
    (re.compile(r"\b(?:manuscript|submission|publication|acceptance) readiness (?:passed|validated|verified|certified|approved)\b", re.IGNORECASE), "readiness promise"),
]
SKILL_INTERACTION_PHRASES = [
    "Wake-up identity",
    "I prepare your paper project as six planning files and one writing design pack.",
    "User-facing phases",
    "Route → Materials → Claim/Evidence → Writing Structure → Handoff",
    "Interaction modes",
    "focused-question",
    "quick-form",
    "candidate-confirmation",
    "reconciliation",
    "stale-alert",
    "Question cards",
    "Agent action after answer",
    "omx question --input",
    "Markdown question cards remain the standalone fallback",
]
PLAYBOOK_CARD_PHRASES = [
    "## Question card pattern",
    "Current stage:",
    "Dimension / blocker:",
    "Why this matters:",
    "Mode chosen:",
    "Options:",
    "Agent action after answer:",
]
COMPILER_GATE_PHRASES = [
    "## Compile decision table",
    "D00-D19 missing",
    "Invalid status or placeholder",
    "Non-critical dimension reaches minimum",
    "Critical-standard dimension only reaches minimum",
    "Owner-gated route/claim/evidence/source/forbidden wording unconfirmed",
    "D16/D17 primary and claim-side statements conflict",
    "D04 route deferred",
    "D18 no visuals",
    "Final pack contains TODO/TBD/UNKNOWN/REPLACE_ME",
    "External writing/citation skill not executed",
    "Blocks design pack? = yes",
    "readiness-critical if unhandled",
    "D16/D17 canonical write rule",
    "03_WRITING_STRUCTURE.md#Object Granularity",
    "03_WRITING_STRUCTURE.md#Surface Control",
    "02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity",
    "reconciliation",
]
RUBRIC_INTERACTION_PHRASES = [
    "Question-card interpretation",
    "focused-question",
    "quick-form",
    "candidate-confirmation",
    "reconciliation",
    "stale-alert",
    "final-route deferral",
    "no-visual rationale",
]


def section_for_id(text: str, dim_id: str) -> str:
    pattern = re.compile(rf"^### {re.escape(dim_id)}\b.*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    next_match = re.search(r"^### D\d{2}\b", text[match.end() :], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[start:end]


def parse_first_table_header(text: str, heading: str) -> list[str]:
    marker = f"## {heading}"
    pos = text.find(marker)
    if pos == -1:
        return []
    rest = text[pos + len(marker) :]
    for line in rest.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            return [cell.strip() for cell in stripped.strip("|").split("|")]
    return []


def require_phrases(label: str, text: str, phrases: list[str], errors: list[str]) -> None:
    for phrase in phrases:
        if phrase not in text:
            errors.append(f"{label}: missing required phrase: {phrase}")


def python_literal_assignment(source: str, name: str) -> object | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name:
                value = node.value
                if value is None:
                    return None
                try:
                    return ast.literal_eval(value)
                except (ValueError, TypeError):
                    return None
    return None


def validate_first_batch_rubric(rubric_text: str, errors: list[str]) -> None:
    for dim_id in FIRST_BATCH_DIMENSIONS:
        section = section_for_id(rubric_text, dim_id)
        if not section:
            errors.append(f"rubric missing first-batch dimension section: {dim_id}")
            continue
        for field in FIRST_BATCH_FIELD_LABELS:
            if f"**{field}:**" not in section:
                errors.append(f"{dim_id}: missing first-batch field label: {field}")
        require_phrases(f"{dim_id} first-batch coverage", section, FIRST_BATCH_DIMENSION_PHRASES[dim_id], errors)


def validate_mechanical_boundary(label: str, text: str, errors: list[str], *, scan_promises: bool = True) -> None:
    lower_text = text.lower()
    for phrase in MECHANICAL_BOUNDARY_PHRASES:
        if phrase not in lower_text:
            errors.append(f"{label}: missing mechanical-only boundary phrase: {phrase}")
    if not scan_promises:
        return
    for pattern, semantic_area in FORBIDDEN_VALIDATOR_PROMISE_PATTERNS:
        if pattern.search(text):
            errors.append(f"{label}: appears to promise semantic scoring for {semantic_area}")


def main() -> int:
    errors: list[str] = []

    if not RUBRIC.is_file():
        errors.append(f"missing rubric: {RUBRIC}")
        rubric_text = ""
    else:
        rubric_text = RUBRIC.read_text(encoding="utf-8")

    ids = re.findall(r"^### (D\d{2})\b", rubric_text, re.MULTILINE)
    if ids != REQUIRED_IDS:
        errors.append(f"rubric must contain headings D00-D19 exactly once and in order; found: {ids}")

    for dim_id in REQUIRED_IDS:
        section = section_for_id(rubric_text, dim_id)
        if not section:
            continue
        for field in REQUIRED_FIELDS:
            if f"**{field}:**" not in section:
                errors.append(f"{dim_id}: missing required field label: {field}")

    if CRITICAL_STANDARD not in rubric_text:
        errors.append(f"rubric missing exact critical-standard set: {CRITICAL_STANDARD}")
    for required_phrase in [
        "not a public skill, not a sixth task playbook",
        "Non-critical dimensions still require at least `minimum` handling",
        "`ideal` never blocks",
        "Owner-gated facts, route decisions, contribution choices, claims, evidence anchors, source/citation facts, and forbidden routes require owner confirmation",
        "Do not add `minimum`, `standard`, `ideal`, or `tier` columns/statuses",
    ]:
        if required_phrase not in rubric_text:
            errors.append(f"rubric missing required invariant phrase: {required_phrase}")
    require_phrases("rubric interaction guidance", rubric_text, RUBRIC_INTERACTION_PHRASES, errors)
    validate_first_batch_rubric(rubric_text, errors)

    if not SKILL.is_file():
        errors.append(f"missing skill: {SKILL}")
    else:
        skill_text = SKILL.read_text(encoding="utf-8")
        for phrase in [
            "references/00-dimension-rubric.md",
            CRITICAL_STANDARD,
            "Do not add tier columns or tier status values",
        ]:
            if phrase not in skill_text:
                errors.append(f"SKILL.md missing rubric wiring phrase: {phrase}")
        require_phrases("SKILL.md interaction guidance", skill_text, SKILL_INTERACTION_PHRASES, errors)

    references_dir = ROOT / "references"
    actual_reference_files = {path.name for path in references_dir.glob("*.md")}
    if actual_reference_files != EXPECTED_REFERENCE_FILES:
        errors.append(
            "internal reference surface changed; expected central rubric plus five playbooks "
            f"{sorted(EXPECTED_REFERENCE_FILES)}, found {sorted(actual_reference_files)}"
        )
    actual_playbooks = actual_reference_files - {"00-dimension-rubric.md"}
    if actual_playbooks != EXPECTED_PLAYBOOK_NAMES:
        errors.append(
            "internal playbook surface changed; expected exactly five playbooks "
            f"{sorted(EXPECTED_PLAYBOOK_NAMES)}, found {sorted(actual_playbooks)}"
        )

    for playbook in TASK_PLAYBOOKS:
        if not playbook.is_file():
            errors.append(f"missing task playbook: {playbook}")
            continue
        text = playbook.read_text(encoding="utf-8")
        if "00-dimension-rubric.md" not in text:
            errors.append(f"{playbook.name}: missing rubric reference")
        if "Do not duplicate its full D00-D19 rubric here" not in text:
            errors.append(f"{playbook.name}: missing no-duplication rule")
        require_phrases(f"{playbook.name} question-card guidance", text, PLAYBOOK_CARD_PHRASES, errors)
        require_phrases(f"{playbook.name} first-batch guidance", text, FIRST_BATCH_PLAYBOOK_PHRASES[playbook.name], errors)
        header = parse_first_table_header(text, "Dimension IDs covered")
        if header and header != ["ID", "Dimension", "Home"]:
            errors.append(f"{playbook.name}: Dimension IDs covered table columns changed; found {header}")

    compiler = ROOT / "references" / "04-design-pack-compiler.md"
    if compiler.is_file():
        require_phrases(
            "04-design-pack-compiler.md compile gate guidance",
            compiler.read_text(encoding="utf-8"),
            COMPILER_GATE_PHRASES,
            errors,
        )

    actual_templates = {path.name for path in TEMPLATES.glob("*.md")}
    if actual_templates != EXPECTED_TEMPLATES:
        errors.append(f"template surface changed; expected {sorted(EXPECTED_TEMPLATES)}, found {sorted(actual_templates)}")

    if INDEX_TEMPLATE.is_file():
        index_text = INDEX_TEMPLATE.read_text(encoding="utf-8")
        header = parse_first_table_header(index_text, "Dimension Status Index")
        if header != INDEX_COLUMNS:
            errors.append(f"00_DIMENSION_INDEX.md table columns changed; found {header}")
        for cell in header:
            normalized = cell.lower().replace("_", " ")
            if any(term == normalized for term in FORBIDDEN_PUBLIC_SCHEMA_TERMS):
                errors.append(f"00_DIMENSION_INDEX.md exposes forbidden public schema column: {cell}")
    else:
        errors.append(f"missing index template: {INDEX_TEMPLATE}")

    if VALIDATOR.is_file():
        validator_text = VALIDATOR.read_text(encoding="utf-8")
        status_set = python_literal_assignment(validator_text, "VALID_DIMENSION_STATUSES")
        if status_set != EXPECTED_STATUS_SET:
            errors.append(f"verify_design_pack.py valid status set changed unexpectedly: {status_set!r}")
        dimension_columns = python_literal_assignment(validator_text, "DIMENSION_COLUMNS")
        if dimension_columns != INDEX_COLUMNS:
            errors.append(f"verify_design_pack.py dimension index columns changed unexpectedly: {dimension_columns!r}")
        validate_mechanical_boundary("verify_design_pack.py", validator_text, errors)
        normalized_validator = re.sub(r"\s+", " ", validator_text.lower())
        if (
            "semantic adequacy" in normalized_validator
            and "does not prove semantic adequacy" not in normalized_validator
            and "does not judge semantic adequacy" not in normalized_validator
        ):
            errors.append("validator appears to claim semantic adequacy")
    else:
        errors.append(f"missing validator: {VALIDATOR}")

    self_text = Path(__file__).read_text(encoding="utf-8")
    validate_mechanical_boundary("verify_dimension_rubric.py", self_text, errors, scan_promises=False)

    public_skills = sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))
    if [p.parent.name for p in public_skills] != ["yxj-paper-os"]:
        errors.append(f"expected exactly one public skill yxj-paper-os; found {[str(p) for p in public_skills]}")

    if errors:
        print("Dimension rubric validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Dimension rubric structural validation passed: {RUBRIC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
