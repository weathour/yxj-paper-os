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
            "assets/AUTHOR_INTERVIEW.md",
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
        manifest = json.loads(
            (REPO_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        combined = contract + json.dumps(manifest, ensure_ascii=False)
        self.assertIn("active paper-design advisor", combined)
        for retired in ("D00-D19", "schema-0.3", "six-file", "dashboard"):
            self.assertNotIn(retired, combined)

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

        brief = (SKILL_ROOT / "assets/PAPER_BRIEF.md").read_text(encoding="utf-8")
        self.assertIn("Exact target skill", brief)
        self.assertIn("Expected artifact and return condition", brief)

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
