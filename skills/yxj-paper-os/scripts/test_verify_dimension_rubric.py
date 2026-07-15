from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"
REFERENCES = ROOT / "references"
RUBRIC = REFERENCES / "00-dimension-rubric.md"
CHECKER = Path(__file__).with_name("verify_dimension_rubric.py")
DETAILED_FIXTURE = (
    ROOT / "assets" / "fixtures" / "design-pack" / "detailed-ready-minimal-0.3"
)
PUBLIC_FILES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}
INDEX_HEADER = [
    "ID",
    "Dimension",
    "Current home",
    "Status",
    "Reason / owner note",
    "Pointer or handoff",
    "Blocks design pack?",
]
DECISION_HEADER = [
    "Decision ID",
    "Gate category",
    "Issue / options / decision",
    "Affected scopes",
    "Origin",
    "Resolution",
    "Grounding / owner-answer pointer",
    "Recheck trigger",
]
TEMPLATE_SOURCE_HEADER = [
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
STRUCTURE_HEADERS = {
    "Section Map": [
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
    ],
    "Paragraph Map": [
        "Paragraph ID",
        "Scope ID",
        "Section ID",
        "Sequence",
        "Function/job",
        "Reader state in",
        "Reader state out",
        "Previous paragraph",
        "Next paragraph",
    ],
    "Paragraph Payload and Boundary Map": [
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
    ],
    "Important Paragraph Register": [
        "Paragraph ID",
        "Qualitative selection rationale",
        "Consequence/risk/dependency",
        "Frame IDs",
        "Gate category",
        "Decision ID",
        "Gate resolution",
        "Owner-answer/grounding pointer",
    ],
    "Controlled Sentence Frames": [
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
    ],
    "Surface Language Contract": [
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
    ],
    "Visual Blueprint": [
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
    ],
    "Cross-Surface Traceability": [
        "Edge ID",
        "From record",
        "Relation",
        "To record",
        "Closure surface",
        "State/freshness",
        "Consequence if stale",
    ],
    "Template Rule Projection": [
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
    ],
    "Grounded Soft Budgets": [
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
    ],
    "Scoped Writing Plan": [
        "Scope ID",
        "Reader / section job",
        "Input record IDs",
        "Output responsibility",
        "Drafting boundary",
        "Output pointer",
    ],
}
COVERAGE_HEADER = [
    "Surface",
    "Scope ID",
    "Handling (`satisfied&#124;not_applicable`)",
    "Record count",
    "Authoritative pointer",
    "Rationale/blocker",
]
TEMPLATE_HANDLING_HEADER = [
    "Scope ID",
    "Mode",
    "Semantic dossier pointer",
    "Quantitative analysis pointer(s)",
    "Generic fallback pointer(s)",
    "Firewall state",
    "Rationale",
    "Active blocker IDs",
]
HANDOFF_HEADER = [
    "Scope ID",
    "00 scope-row pointer",
    "Detailed coverage pointer",
    "Output pointer",
    "Active blocker IDs",
    "Downstream prohibitions",
    "Handoff note",
]
AUTHORITY_HEADER = ["Authority", "Required pointer", "Compiler note"]
REQUIRED_01_AUTHORITIES = {
    "Scientific materials": "01_MATERIALS_INVENTORY.md#Material Records",
    "Template design sources": "01_MATERIALS_INVENTORY.md#Template Design Sources",
}
SURFACE_KEYS = [
    "section_paragraph_map",
    "surface_language_contract",
    "visual_caption_blueprint",
    "cross_surface_traceability",
    "template_rule_provenance",
    "soft_budgets",
    "important_paragraph_frames",
]
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


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not match:
        raise AssertionError(f"missing heading: {heading}")
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.M)
    return tail[: next_heading.start()] if next_heading else tail


def table(text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    lines = [
        line.strip()
        for line in section(text, heading).splitlines()
        if line.strip().startswith("|")
    ]
    if len(lines) < 2:
        raise AssertionError(f"missing table: {heading}")

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    rows = [
        cells(line) for line in lines[2:] if not re.fullmatch(r"\|?[\s:|-]+\|?", line)
    ]
    return cells(lines[0]), rows


class Schema03PublicContractTests(unittest.TestCase):
    def assert_required_01_authorities_resolve(
        self, pack: str, workspace: Path
    ) -> None:
        header, rows = table(pack, "Authority Pointers")
        self.assertEqual(header, AUTHORITY_HEADER)
        pointers = {row[0]: row[1] for row in rows}
        for authority, expected in REQUIRED_01_AUTHORITIES.items():
            self.assertEqual(pointers.get(authority), expected)
            filename, heading = expected.split("#", 1)
            target = (workspace / filename).read_text(encoding="utf-8")
            self.assertTrue(section(target, heading).strip())

    def test_public_workspace_identity_index_and_status_vocabularies(self) -> None:
        self.assertEqual({path.name for path in TEMPLATES.glob("*.md")}, PUBLIC_FILES)
        index = read_template("00_DIMENSION_INDEX.md")
        self.assertIn("Workspace schema version: 0.3", index)
        header, rows = table(index, "Dimension Status Index")
        self.assertEqual(header, INDEX_HEADER)
        self.assertEqual([row[0] for row in rows], [f"D{i:02d}" for i in range(20)])
        self.assertIn(
            "filled&#124;not_applicable&#124;absent&#124;deferred&#124;rejected",
            index,
        )
        self.assertIn(
            "writer-ready&#124;partial&#124;blocked&#124;deferred",
            index,
        )
        self.assertNotIn("detailed-ready", index)

    def test_exact_route_material_structure_and_manifest_headers(self) -> None:
        route = read_template("00_PROJECT_ROUTE.md")
        materials = read_template("01_MATERIALS_INVENTORY.md")
        structure = read_template("03_WRITING_STRUCTURE.md")
        pack = read_template("04_WRITING_DESIGN_PACK.md")
        self.assertEqual(table(route, "Decision Records")[0], DECISION_HEADER)
        self.assertEqual(
            table(materials, "Template Design Sources")[0],
            TEMPLATE_SOURCE_HEADER,
        )
        for heading, expected in STRUCTURE_HEADERS.items():
            self.assertEqual(table(structure, heading)[0], expected, heading)
        self.assertEqual(table(pack, "Detailed Surface Coverage")[0], COVERAGE_HEADER)
        self.assertEqual(
            table(pack, "Template Analysis Handling")[0],
            TEMPLATE_HANDLING_HEADER,
        )
        handoff = table(pack, "Scoped Handoff")[0]
        self.assertEqual(handoff, HANDOFF_HEADER)
        self.assertNotIn("Readiness", handoff)

    def test_scientific_and_template_source_authorities_are_distinct_and_resolve(
        self,
    ) -> None:
        self.assert_required_01_authorities_resolve(
            read_template("04_WRITING_DESIGN_PACK.md"), TEMPLATES
        )
        self.assert_required_01_authorities_resolve(
            (DETAILED_FIXTURE / "04_WRITING_DESIGN_PACK.md").read_text(
                encoding="utf-8"
            ),
            DETAILED_FIXTURE,
        )

    def test_missing_or_wrong_template_source_authority_is_rejected(self) -> None:
        pack = read_template("04_WRITING_DESIGN_PACK.md")
        template_row = (
            "| Template design sources | "
            "01_MATERIALS_INVENTORY.md#Template Design Sources | "
            "Separate TPL-* design-only source/provenance authority |"
        )
        mutations = {
            "missing": pack.replace(template_row + "\n", ""),
            "wrong": pack.replace(
                "01_MATERIALS_INVENTORY.md#Template Design Sources",
                "01_MATERIALS_INVENTORY.md#Material Records",
                1,
            ),
        }
        for case, mutated in mutations.items():
            with self.subTest(case=case), self.assertRaises(AssertionError):
                self.assert_required_01_authorities_resolve(mutated, TEMPLATES)

    def test_rubric_freezes_seven_surfaces_and_canonical_grammar(self) -> None:
        rubric = RUBRIC.read_text(encoding="utf-8")
        canonical_ids = re.findall(r"^### (D(?:0[0-9]|1[0-9]))\s+—", rubric, re.M)
        self.assertEqual(canonical_ids, [f"D{i:02d}" for i in range(20)])
        _, surface_rows = table(rubric, "Canonical Detailed Surfaces")
        self.assertEqual([row[0] for row in surface_rows], SURFACE_KEYS)
        for key in SURFACE_KEYS:
            self.assertEqual(sum(row[0] == key for row in surface_rows), 1)
        for grammar in (
            "^D(?:0[0-9]&#124;1[0-9])$",
            "^SCOPE-[a-z0-9]+(?:-[a-z0-9]+)*$",
            "^REQ-[a-z0-9]+(?:-[a-z0-9]+)*$",
            "^DEC-[a-z0-9]+(?:-[a-z0-9]+)*$",
            "^M-[a-z0-9]+(?:-[a-z0-9]+)*$",
            "^C-[a-z0-9]+(?:-[a-z0-9]+)*$",
            "^(?:TSD&#124;TPL&#124;TOBS&#124;TRULE&#124;SEC&#124;PAR&#124;FRM&#124;LANG&#124;VIS&#124;EDGE&#124;BUD)-[a-z0-9]+(?:-[a-z0-9]+)*$",
        ):
            self.assertIn(grammar, rubric)
        for pointer in (
            "03_WRITING_STRUCTURE.md#Controlled Sentence Frames",
            ".yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-example",
            ".yxj-paper-os/template-analysis/design-profile.json#entries.example",
            "lens:argument-language-visual#sufficiency-predicates",
        ):
            self.assertIn(pointer, rubric)
        self.assertIn("&#124;", rubric)
        self.assertIn("<br>", rubric)
        self.assertIn("ASCII semicolon", rubric)
        self.assertIn("none;M-example", rubric)
        self.assertNotRegex(rubric, r"\^\(\?:[^\n]*(?:EVID|CLM)")
        relation_line = re.search(r"Direct edge relations:\s*([a-z_;]+)", rubric)
        self.assertIsNotNone(relation_line)
        assert relation_line is not None
        self.assertEqual(set(relation_line.group(1).split(";")), EDGE_RELATIONS)
        _, examples = table(rubric, "Grammar Examples")
        self.assertTrue(examples)
        self.assertTrue(all(len(row) == 4 and row[1] and row[2] for row in examples))

    def test_claim_ceiling_and_agent_led_legacy_recompilation_are_explicit(
        self,
    ) -> None:
        claims = read_template("02_CLAIM_EVIDENCE_BOUNDARY.md")
        compiler = (REFERENCES / "04-design-pack-compiler.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("sole scientific claim", claims.lower())
        self.assertIn("cannot increase", claims.lower())
        self.assertIn("agent-led", compiler)
        self.assertIn("non-destructive", compiler)
        self.assertIn("schema 0.2", compiler.lower())
        self.assertIn("schema 0.3", compiler.lower())
        self.assertIn("No prior writer-ready", compiler)
        self.assertIn("no automatic migration", compiler.lower())

    def test_rubric_checker_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
