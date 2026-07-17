from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
SCRIPT = Path(__file__).with_name("template_probe.py")


class MinimalAdvisorContractTests(unittest.TestCase):
    def test_active_surface_is_minimal_and_clean_break(self) -> None:
        expected = {
            "SKILL.md",
            "assets/PAPER_BRIEF.md",
            "assets/TEMPLATE_ANALYSIS.md",
            "scripts/template_probe.py",
            "scripts/test_template_probe.py",
        }
        actual = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(actual, expected)

        contract = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract_normalized = " ".join(contract.split())
        manifest = json.loads(
            (REPO_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        brief = (SKILL_ROOT / "assets/PAPER_BRIEF.md").read_text(encoding="utf-8")
        template = (SKILL_ROOT / "assets/TEMPLATE_ANALYSIS.md").read_text(
            encoding="utf-8"
        )
        combined = contract + brief + template + json.dumps(manifest, ensure_ascii=False)
        self.assertIn("returning non-writing paper-design authority", combined.lower())
        for retired in ("D00-D19", "schema-0.3", "six-file", "dashboard"):
            self.assertNotIn(retired, combined)

        self.assertFalse((SKILL_ROOT / "assets/AUTHOR_INTERVIEW.md").exists())
        self.assertIn(
            "`PAPER_BRIEF.md` is the sole current authority", contract_normalized
        )
        self.assertIn("ordinary brownfield input", contract_normalized)
        self.assertIn("Use Git as history where available", contract_normalized)
        self.assertIn("replace current content in place", contract_normalized)
        self.assertIn("substitute log", contract_normalized)
        for append_instruction in (
            "Append only consequential decisions",
            "Record only consequential decisions",
        ):
            self.assertNotIn(append_instruction, combined)

        for target in (
            "$nature-writing",
            "$nature-polishing",
            "$nature-academic-search",
            "$nature-citation",
            "$nature-reader",
            "$nature-figure",
            "$thesis-figure-skill",
            "$drawio-skill",
            "$nature-reviewer",
        ):
            self.assertIn(target, contract)
        self.assertIn("Do not gate it on journal name", contract)

        for heading in (
            "## Current basis",
            "## Science contract",
            "## Reader contract",
            "## Story spine",
            "## Reader object map",
            "## Section jobs",
            "## Display and formal map",
            "## Current author locks",
            "## Latest realization audit",
            "## Downstream handoff",
        ):
            self.assertIn(heading, brief)
        for basis in ("Repository", "Scientific evidence", "Artifacts", "Feedback"):
            self.assertIn(basis, brief)
        self.assertIn("Open author decision (zero or one)", brief)
        self.assertIn(
            "Keep only the latest relevant audit and unresolved conflicts", brief
        )
        self.assertEqual(brief.count("## Downstream handoff"), 1)
        self.assertIn("Zero or one immediate task", brief)
        self.assertIn("Exact target skill", brief)
        self.assertIn("Expected artifact and return condition", brief)

    def test_reentry_questions_and_realization_contract(self) -> None:
        contract = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        brief = (SKILL_ROOT / "assets/PAPER_BRIEF.md").read_text(encoding="utf-8")
        template = (SKILL_ROOT / "assets/TEMPLATE_ANALYSIS.md").read_text(
            encoding="utf-8"
        )
        manifest = json.loads(
            (REPO_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        normalized = " ".join(contract.split()).lower()
        brief_normalized = " ".join(brief.split()).lower()
        template_normalized = " ".join(template.split()).lower()
        manifest_normalized = " ".join(
            json.dumps(manifest, ensure_ascii=False).split()
        ).lower()

        self.assertEqual(manifest["version"], "0.4.0")
        for identity_surface in (normalized, manifest_normalized):
            self.assertIn("returning non-writing paper-design authority", identity_surface)

        for basis in (
            "current repository",
            "scientific evidence",
            "manuscript/pdf/figure artifacts",
            "author or reviewer feedback",
            "`current basis`",
        ):
            self.assertIn(basis, normalized)
        wake_priority = (
            "no substantive `paper_brief.md`",
            "scientific evidence or integrity delta",
            "new or changed downstream artifact",
            "grounded but unfinished design work",
            "no material delta",
        )
        positions = [normalized.index(branch) for branch in wake_priority]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "only affected claim, story, display, formal-object, and boundary rows",
            normalized,
        )
        self.assertIn("do not reopen unrelated design", normalized)

        self.assertIn("all four conditions must hold together", normalized)
        for condition in (
            "only the author can supply it",
            "the decision is still unresolved",
            "it blocks the immediate next step",
            "it cannot be decided safely and autonomously",
        ):
            self.assertIn(condition, normalized)
        for autonomous in (
            "paragraph order",
            "transitions",
            "routine terminology cleanup",
            "equation numbering",
            "callouts",
            "captions",
            "visual styling and layout",
        ):
            self.assertIn(autonomous, normalized)
        for guard in (
            "at most one open author decision",
            "keep no question backlog",
            "visible writeback, artifact, or integrity resolution",
            "every new question must independently pass all four conditions",
            "prior writeback is not a waiver",
        ):
            self.assertIn(guard, normalized)
        self.assertNotIn("confirm the global story with the author", normalized)
        self.assertNotIn("ask local questions only when reader meaning changes", normalized)

        self.assertIn("## Design Handoff", contract)
        self.assertIn("## Realization Alignment", contract)
        self.assertIn("without repository archaeology", normalized)
        for realization_evidence in (
            "substantive manuscript source or an actual returned artifact",
            "layout, float, or visual-legibility",
            "rendered artifact",
            "placeholder, build, and handoff metadata",
            "local `aligned: yes`",
            "continuous author read",
        ):
            self.assertIn(realization_evidence, normalized)
        for reader_check in (
            "one reader object, one canonical name, and its first use",
            "each display's reader question and one takeaway",
            "result observation before limitation",
            "boundary statements are concentrated",
            "formal object can be reconstructed",
            "callout, float, and legibility",
        ):
            self.assertIn(reader_check, normalized)

        for slice_rule in (
            "representative realization slice",
            "at most one slice",
            "skip it when current artifacts suffice",
            "ordinary return audit",
        ):
            self.assertIn(slice_rule, normalized)

        self.assertIn("zero or one immediate downstream task", normalized)
        self.assertIn("action is `route`", normalized)
        self.assertIn("exactly one installed skill", normalized)
        for return_field in (
            "artifact path",
            "local `aligned`: `yes` / `no`",
            "conflicts",
            "changed brief sections",
        ):
            self.assertIn(return_field, brief_normalized)
        self.assertIn("production log", normalized)

        for template_field in (
            "template and precise locator",
            "decision-changing observation",
            "`adopt` / `adapt` / `avoid`",
            "changed brief decision/section",
            "external deep-reading artifact",
        ):
            self.assertIn(template_field, template_normalized)
        for removed_form in (
            "paper-level reverse outline",
            "candidate a",
            "candidate b",
            "recommendation and author decision",
        ):
            self.assertNotIn(removed_form, template_normalized)

    def test_probe_reports_only_reader_useful_facts(self) -> None:
        source = """# Example paper

## Introduction

We frame the problem carefully [1]. However, prior work leaves a gap.

Figure 1: System overview.

## Method

We propose a bounded method. It may improve robustness.

| Item | Role |
|---|---|
| A | Evidence |

Algorithm 1 describes the procedure. Equation (1) defines the objective.
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.md"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Template probe", result.stdout)
        self.assertIn("Introduction", result.stdout)
        self.assertIn("Method", result.stdout)
        self.assertIn("figure", result.stdout.lower())
        self.assertIn("algorithm", result.stdout.lower())
        self.assertIn("equation", result.stdout.lower())
        self.assertIn("hedge/modal", result.stdout.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
