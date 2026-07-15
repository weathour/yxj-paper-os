from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills/yxj-paper-os"
PUBLIC_FILES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}
FOUR_GATES = {
    "scientific_commitment",
    "argument_spine",
    "material_local_tradeoff",
    "deliberate_divergence",
}
FIVE_MODES = {
    "semantic_primary",
    "semantic_plus_quantitative",
    "quantitative_only",
    "generic_fallback",
    "not_applicable",
}
SEVEN_SURFACES = {
    "section_paragraph_map",
    "important_paragraph_frames",
    "surface_language_contract",
    "visual_caption_blueprint",
    "cross_surface_traceability",
    "template_rule_provenance",
    "soft_budgets",
}


class WP5ProductContractTests(unittest.TestCase):
    def test_public_contract_is_exactly_six_schema_03_templates(self):
        templates = SKILL_ROOT / "assets/templates"
        self.assertEqual({path.name for path in templates.glob("*.md")}, PUBLIC_FILES)
        index = (templates / "00_DIMENSION_INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Workspace schema version: 0.3", index)
        self.assertIn("schema-0.3", (templates / "03_WRITING_STRUCTURE.md").read_text())
        self.assertIn(
            "schema-0.3", (templates / "04_WRITING_DESIGN_PACK.md").read_text()
        )

    def test_skill_and_compiler_share_actions_gates_modes_and_surfaces(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        compiler = (SKILL_ROOT / "references/04-design-pack-compiler.md").read_text(
            encoding="utf-8"
        )
        rubric = (SKILL_ROOT / "references/00-dimension-rubric.md").read_text(
            encoding="utf-8"
        )
        combined = skill + "\n" + compiler + "\n" + rubric
        for token in FOUR_GATES | FIVE_MODES | SEVEN_SURFACES:
            self.assertIn(token, combined, token)
        self.assertIn("`inspect`, `derive`, `project`, `ask`", skill)
        self.assertNotIn("`inspect`, `record-observation`", skill)
        self.assertIn("`03` owns detailed", skill)
        self.assertIn("04", skill)
        self.assertIn("pointer", skill.casefold())

    def test_five_playbooks_and_seven_lenses_are_schema_03_aligned(self):
        playbooks = [
            SKILL_ROOT / f"references/{name}"
            for name in (
                "00-project-route.md",
                "01-materials-inventory.md",
                "02-claim-evidence-boundary.md",
                "03-writing-structure.md",
                "04-design-pack-compiler.md",
            )
        ]
        for path in playbooks:
            normalized = path.read_text(encoding="utf-8").casefold().replace("-", " ")
            self.assertIn("schema 0.3", normalized, path.name)
        lenses = sorted((SKILL_ROOT / "references/lenses").glob("*.md"))
        modules = [path for path in lenses if path.name != "README.md"]
        self.assertEqual(len(modules), 7)
        for path in modules:
            text = path.read_text(encoding="utf-8").casefold()
            for gate in FOUR_GATES:
                self.assertIn(gate, text, f"{path.name}: {gate}")
            self.assertIn("writer-ready", text, path.name)
        venue = (
            (SKILL_ROOT / "references/lenses/venue-template.md")
            .read_text(encoding="utf-8")
            .casefold()
        )
        self.assertIn("model-semantic", venue)
        self.assertIn("optional", venue.casefold())
        self.assertIn("analyzer", venue.casefold())
        self.assertIn("design-only", venue.casefold())

    def test_product_docs_lead_with_semantic_prewrite_compiler_not_statistics(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        handoff = (ROOT / "HANDOFF.md").read_text(encoding="utf-8")
        philosophy = (ROOT / "docs/BRANCH_PHILOSOPHY.md").read_text(encoding="utf-8")
        interaction = (ROOT / "docs/DIMENSION_INTERACTION_INTELLIGENCE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("schema-0.3 prewriting compiler", readme)
        self.assertIn("exactly these six Markdown files", readme)
        self.assertIn("Optional deterministic analyzer", readme)
        self.assertIn("SCHEMA_LEGACY_02", readme)
        self.assertIn("repository", philosophy.casefold())
        self.assertIn("template", philosophy.casefold())
        self.assertIn("owner", philosophy.casefold())
        self.assertIn("03", interaction)
        self.assertIn("04", interaction)
        self.assertIn("declared structural coverage", interaction)
        self.assertIn("schema is `0.3`", handoff)
        stale_defaults = (
            "reproducible target-journal/target-topic corpus statistics",
            "Workspace schema version is `0.2`",
            "mirrors the authoritative Writing Scopes registry",
        )
        for phrase in stale_defaults:
            self.assertNotIn(
                phrase, "\n".join((readme, handoff, philosophy, interaction))
            )

    def test_plugin_metadata_and_cli_help_expose_current_non_drafting_contract(self):
        plugin = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(plugin["version"], "0.3.0+codex.20260715")
        interface = plugin["interface"]
        identity = " ".join(
            [
                plugin["description"],
                interface["longDescription"],
                interface["defaultPrompt"],
            ]
        )
        self.assertIn("schema-0.3", identity.casefold())
        self.assertIn("model-semantic", identity.casefold())
        self.assertIn("without drafting manuscript prose", identity.casefold())
        self.assertIn(
            "Optional reproducible template analyzer", interface["capabilities"]
        )
        for script, phrase in (
            ("capture_behavior_actions.py", "schema-0.3 behavior capture"),
            ("verify_behavior_scenarios.py", "schema-0.3 behavior"),
            ("verify_design_pack.py", "schema-0.3 yxj-paper-os design pack"),
            ("generate_dashboard.py", "read-only static yxj-paper-os dashboard"),
        ):
            result = subprocess.run(
                [sys.executable, str(SKILL_ROOT / "scripts" / script), "--help"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(phrase, result.stdout, script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
