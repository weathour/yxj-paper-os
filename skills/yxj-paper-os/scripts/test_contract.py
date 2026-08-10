from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


class ContractTest(unittest.TestCase):
    def test_minimal_v06_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        brief = (ROOT / "assets/PAPER_BRIEF.md").read_text(encoding="utf-8")
        manifest = json.loads(
            (REPO / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        product = " ".join((skill + brief).split()).lower()

        self.assertEqual(manifest["version"], "0.6.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(
            {
                path.relative_to(ROOT).as_posix()
                for path in ROOT.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            },
            {"SKILL.md", "assets/PAPER_BRIEF.md", "scripts/test_contract.py"},
        )
        for phrase in (
            "assessment is not edit authorization",
            "suggest or recommend improvements remains read-only",
            "exceeds or invents evidence",
            "never edit measured data",
            "a proposed change is not a result",
            "all affected surfaces are updated or shown unaffected",
            "impact closure:",
            "updated | unaffected -> check or evidence",
            "actual or rendered artifact",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, product)
        for retired in (
            "returning non-writing paper-design authority",
            "design handoff",
            "realization alignment",
            "downstream handoff",
        ):
            self.assertNotIn(retired, product)
        self.assertEqual(
            [line for line in brief.splitlines() if line.startswith("## ")],
            ["## Current basis", "## Current constraints", "## Open work"],
        )


if __name__ == "__main__":
    unittest.main()
