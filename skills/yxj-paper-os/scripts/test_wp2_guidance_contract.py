from __future__ import annotations

import re
import unittest
from pathlib import Path

from template_design_contract import load_lens_registry


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
LENSES = ROOT / "references" / "lenses"
FOUR_GATES = {
    "scientific_commitment",
    "argument_spine",
    "material_local_tradeoff",
    "deliberate_divergence",
}
GENERIC_LENSES = {
    "contribution-evidence-forms",
    "research-design-validity",
    "evidence-results-statistics",
    "literature-differentiation",
    "reproducibility-governance",
    "argument-language-visual",
}
GENERIC_HEADINGS = {
    "Activation and affected scopes",
    "Reasoning model",
    "Repository inputs and safe derivations",
    "Sufficiency predicates",
    "Four-gate mapping",
    "Invalidation and recheck",
    "Failure modes and non-goals",
    "Six-file and hidden projection",
    "Writer-ready consequences",
}


class WP2GuidanceContractTests(unittest.TestCase):
    def test_skill_wake_contract_and_design_boundary(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        for token in (
            "target outcome",
            "requested writing `SCOPE-*`",
            "success criteria",
            "current scientific and design evidence",
            "stop condition",
            "Inspect the six files",
            "model_semantic_deep_reading",
            "semantic-dossier.json",
            "available agent",
            "Every planned paragraph",
            "controlled frames",
            "design-only",
            "never a readiness prerequisite",
            "Never draft manuscript",
        ):
            self.assertIn(token, text)
        for gate in FOUR_GATES:
            self.assertIn(f"`{gate}`", text)
        self.assertNotRegex(
            text,
            r"(?i)only (?:a new )?owner[^\n]{0,100}(?:accept|adapt|reject|adopt)",
        )
        self.assertIn("bibliography/citation layout", text)
        self.assertIn("citation function remains model-derived", text)
        self.assertIn("template-annotations/1.0", text)

    def test_registry_and_six_generic_lenses_have_complete_distinct_contracts(
        self,
    ) -> None:
        registry, diagnostics = load_lens_registry(LENSES / "README.md")
        self.assertEqual(diagnostics, [])
        self.assertEqual(set(registry), GENERIC_LENSES | {"venue-template"})
        bodies = {}
        for lens_id in GENERIC_LENSES:
            text = (LENSES / registry[lens_id]).read_text(encoding="utf-8")
            bodies[lens_id] = text
            headings = set(re.findall(r"^##\s+(.+?)\s*$", text, re.M))
            self.assertTrue(headings >= GENERIC_HEADINGS, lens_id)
            for gate in FOUR_GATES:
                self.assertIn(f"`{gate}`", text, lens_id)
            self.assertIn("hidden", text.lower(), lens_id)
            self.assertIn("writer-ready", text.lower(), lens_id)
            self.assertRegex(text.lower(), r"do not|never")
        normalized = {re.sub(r"\s+", " ", body).strip() for body in bodies.values()}
        self.assertEqual(len(normalized), len(GENERIC_LENSES))

    def test_venue_lens_is_semantic_first_and_preserves_protected_boundaries(
        self,
    ) -> None:
        text = (LENSES / "venue-template.md").read_text(encoding="utf-8")
        for heading in (
            "Purpose and activation signals",
            "Theory and distinctions",
            "Sufficiency predicates",
            "Safe derivations",
            "Four-gate mapping",
            "Dependencies and invalidation",
            "Failure modes",
            "Workspace projection",
            "Writer-ready consequences",
        ):
            self.assertRegex(text, rf"(?m)^## {re.escape(heading)}$", heading)
        for token in (
            "Model-semantic deep reading is primary",
            "agent-authored `semantic-dossier.json`",
            "optional and non-default",
            "Bibliography and citation-layout analysis",
            "Reference-list inventory",
            "Citation layout",
            "Citation function",
            "Shared works",
            "Scientific-evidence firewall",
            "analyzer is never a default or readiness prerequisite",
        ):
            self.assertIn(token, text)
        for gate in FOUR_GATES:
            self.assertIn(f"`{gate}`", text)
        self.assertNotRegex(
            text,
            r"(?i)only (?:a new )?owner[^\n]{0,100}(?:accept|adapt|reject|adopt)",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
