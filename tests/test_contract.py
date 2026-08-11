from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skills/yxj-paper-os"


class MarkerSmokeTest(unittest.TestCase):
    def test_v07_contract_markers(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        brief = (ROOT / "assets/PAPER_BRIEF.md").read_text(encoding="utf-8")
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        manifest = json.loads(
            (REPO / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        runtime = " ".join((skill + json.dumps(manifest)).split()).lower()
        brief_contract = " ".join(brief.split()).lower()
        docs = " ".join(readme.split()).lower()

        self.assertEqual(manifest["version"].split("+", 1)[0], "0.7.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(
            {
                path.relative_to(ROOT).as_posix()
                for path in ROOT.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            },
            {"SKILL.md", "assets/PAPER_BRIEF.md"},
        )
        for phrase in (
            "serve the reader first",
            "non-negotiable evidence boundary",
            "within that boundary",
            "why this problem matters",
            "central claim",
            "strongest justified story",
            "all claim-relevant evidence",
            "reader takeaway",
            "reader-facing realization",
            "actual reader effect",
            "minimal sufficient defense",
            "state a caveat once",
            "nearest claim it qualifies",
            "reasonable intended reader",
            "materially qualify the central claim, its scope or applicability, or the main result",
            "project-root `paper_brief.md`",
            "read-only template",
            "assessment is not edit authorization",
            "suggest or recommend improvements remains read-only",
            "exceeds or invents evidence",
            "never edit measured data",
            "a proposed change is not a result",
            "update all materially affected surfaces",
            "non-obvious or required for consistency",
            "actual or rendered artifact",
            "title, abstract, introduction, results, figures, and conclusion",
            "if present, unresolved scientific risks",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, runtime)
        for phrase in (
            "impact closure:",
            "updated | unaffected -> check or evidence",
            "only materially affected surfaces",
            "non-obvious unaffected surfaces",
        ):
            with self.subTest(brief_phrase=phrase):
                self.assertIn(phrase, brief_contract)
        for phrase in (
            "non-negotiable evidence boundary",
            "within that boundary",
            "actual reader effect",
            "$yxj-paper-os:yxj-paper-os",
        ):
            with self.subTest(docs_phrase=phrase):
                self.assertIn(phrase, docs)
        for retired in (
            "returning non-writing paper-design authority",
            "design handoff",
            "realization alignment",
            "downstream handoff",
            "verify the reader effect",
            "its priority order is",
        ):
            self.assertNotIn(retired, runtime + docs)
        self.assertEqual(
            [line for line in brief.splitlines() if line.startswith("## ")],
            ["## Current basis", "## Current constraints", "## Open work"],
        )


if __name__ == "__main__":
    unittest.main()
