from __future__ import annotations

import unittest
from pathlib import Path

from verify_design_pack import parse_first_table, validate_workspace


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "assets" / "fixtures" / "design-pack"
LEGACY = FIXTURES / "legacy-section-ready-0.2"
DETAILED = FIXTURES / "detailed-ready-minimal-0.3"
PUBLIC_FILES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}


class Schema03CharacterizationTests(unittest.TestCase):
    def test_public_workspace_surface_remains_exactly_six_files(self) -> None:
        shipped = {path.name for path in (ROOT / "assets" / "templates").glob("*.md")}
        self.assertEqual(shipped, PUBLIC_FILES)
        for fixture in (LEGACY, DETAILED):
            self.assertEqual(
                {path.name for path in fixture.glob("*.md")},
                PUBLIC_FILES,
            )

    def test_minimal_detailed_fixture_has_declared_shape_and_no_hidden_analysis(
        self,
    ) -> None:
        writing = (DETAILED / "03_WRITING_STRUCTURE.md").read_text(encoding="utf-8")
        pack = (DETAILED / "04_WRITING_DESIGN_PACK.md").read_text(encoding="utf-8")
        self.assertEqual(len(parse_first_table(writing, "Section Map")[1]), 1)
        self.assertEqual(len(parse_first_table(writing, "Paragraph Map")[1]), 2)
        self.assertEqual(
            len(parse_first_table(writing, "Important Paragraph Register")[1]), 1
        )
        self.assertEqual(
            len(parse_first_table(writing, "Controlled Sentence Frames")[1]), 2
        )
        coverage = parse_first_table(pack, "Detailed Surface Coverage")[1]
        self.assertEqual(len(coverage), 7)
        handling = parse_first_table(pack, "Template Analysis Handling")[1]
        self.assertEqual(
            handling,
            [
                {
                    "Scope ID": "SCOPE-demo",
                    "Mode": "not_applicable",
                    "Semantic dossier pointer": "none",
                    "Quantitative analysis pointer(s)": "none",
                    "Generic fallback pointer(s)": "none",
                    "Firewall state": "design_only",
                    "Rationale": (
                        "Template design is irrelevant to this synthetic "
                        "route-neutral contract fixture"
                    ),
                    "Active blocker IDs": "none",
                }
            ],
        )
        self.assertFalse((DETAILED / ".yxj-paper-os").exists())

    def test_schema_0_2_writer_ready_is_downgraded_once(self) -> None:
        errors = validate_workspace(LEGACY, require_handoff=True)
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("SCHEMA_LEGACY_02:"), errors)
        self.assertNotIn("current detailed readiness", errors[0].lower())

    def test_schema_0_3_template_na_is_ready_without_dossier_or_analyzer(self) -> None:
        self.assertFalse((DETAILED / ".yxj-paper-os").exists())
        self.assertEqual(validate_workspace(DETAILED, require_handoff=True), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
