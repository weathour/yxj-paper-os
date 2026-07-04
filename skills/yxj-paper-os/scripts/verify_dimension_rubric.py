#!/usr/bin/env python3
"""Validate the yxj-paper-os internal D00-D19 dimension rubric.

This is a structural development check. It does not judge academic adequacy,
search citations, execute external skills, or change the public workspace schema.
"""

from __future__ import annotations

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
VALID_STATUSES_LITERAL = '{"filled", "not_applicable", "absent", "deferred", "rejected"}'


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

    for playbook in TASK_PLAYBOOKS:
        if not playbook.is_file():
            errors.append(f"missing task playbook: {playbook}")
            continue
        text = playbook.read_text(encoding="utf-8")
        if "00-dimension-rubric.md" not in text:
            errors.append(f"{playbook.name}: missing rubric reference")
        if "Do not duplicate its full D00-D19 rubric here" not in text:
            errors.append(f"{playbook.name}: missing no-duplication rule")

    actual_templates = {path.name for path in TEMPLATES.glob("*.md")}
    if actual_templates != EXPECTED_TEMPLATES:
        errors.append(f"template surface changed; expected {sorted(EXPECTED_TEMPLATES)}, found {sorted(actual_templates)}")

    if INDEX_TEMPLATE.is_file():
        index_text = INDEX_TEMPLATE.read_text(encoding="utf-8")
        header = parse_first_table_header(index_text, "Dimension Status Index")
        if header != INDEX_COLUMNS:
            errors.append(f"00_DIMENSION_INDEX.md table columns changed; found {header}")
    else:
        errors.append(f"missing index template: {INDEX_TEMPLATE}")

    if VALIDATOR.is_file():
        validator_text = VALIDATOR.read_text(encoding="utf-8")
        if VALID_STATUSES_LITERAL not in validator_text:
            errors.append("verify_design_pack.py valid status set changed unexpectedly")
        if "semantic adequacy" in validator_text.lower() and "does not prove semantic adequacy" not in validator_text:
            errors.append("validator appears to claim semantic adequacy")
    else:
        errors.append(f"missing validator: {VALIDATOR}")

    public_skills = list((REPO_ROOT / "skills").glob("*/SKILL.md"))
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
