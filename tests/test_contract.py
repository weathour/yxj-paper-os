"""Package invariants only; model behavior is exercised by behavioral_cases.md."""

import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skills/yxj-paper-os"


class PackageTest(unittest.TestCase):
    def test_manifest_resolves_the_single_skill(self):
        manifest = json.loads((REPO / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], ROOT.name)
        skill_dir = (REPO / manifest["skills"]).resolve()
        self.assertEqual(list(skill_dir.glob("*/SKILL.md")), [ROOT / "SKILL.md"])
        frontmatter = (ROOT / "SKILL.md").read_text().split("---", 2)[1]
        fields = dict(line.split(":", 1) for line in frontmatter.splitlines() if line)
        self.assertEqual(fields["name"].strip(), manifest["name"])
        self.assertTrue(fields["description"].strip())
        for runtime in ("mcpServers", "hooks", "apps"):
            self.assertNotIn(runtime, manifest)

    def test_bundled_resources_are_present_and_reachable(self):
        files = {path.resolve() for path in ROOT.rglob("*")
                 if path.is_file() and "__pycache__" not in path.parts}
        self.assertEqual(files, {
            ROOT / "SKILL.md",
            ROOT / "references/display-workflow.md",
            ROOT / "references/venue-calibration.md",
            ROOT / "references/authorial-style.md",
            ROOT / "assets/PAPER_BRIEF.md",
        })
        reachable = {ROOT / "SKILL.md"}
        for doc in (ROOT / "SKILL.md", *ROOT.glob("references/*.md")):
            # Check local Markdown links and backticked resource paths, not prose.
            targets = re.findall(r"\]\(([^)]+)\)", doc.read_text())
            targets += re.findall(r"`((?:assets|references)/[^`]+)`", doc.read_text())
            for target in targets:
                if target.startswith(("https://", "http://")):
                    continue  # Research citations are not bundled file dependencies.
                with self.subTest(document=doc.name, target=target):
                    resolved = (doc.parent / target).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.is_file())
                    reachable.add(resolved)
        self.assertEqual(reachable, files)

    def test_brief_keeps_current_state_sections(self):
        brief = (ROOT / "assets/PAPER_BRIEF.md").read_text()
        # Keep the information groups; row formats are optional, not an API.
        self.assertEqual(
            [line.removeprefix("## ") for line in brief.splitlines()
             if line.startswith("## ")],
            ["Current basis", "Current constraints", "Open work"],
        )


if __name__ == "__main__":
    unittest.main()
