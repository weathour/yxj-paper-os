"""Package invariants only; model behavior is exercised by behavioral_cases.md."""

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skills/yxj-paper-os"
HOST_SKILLS = {
    "paper-topic-incubation", "paper-deep-research", "yxj-practice",
    "yxj-backend", "yxj-chinese-expression", "thesis-figure-skill",
}


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
        self.assertIn(ROOT / "SKILL.md", files)
        reachable = set()
        pending = [ROOT / "SKILL.md"]
        while pending:
            doc = pending.pop()
            if doc in reachable:
                continue
            reachable.add(doc)
            if doc.suffix != ".md":
                continue
            # Check local Markdown links and backticked resource paths, not prose.
            targets = re.findall(r"\]\(([^)]+)\)", doc.read_text())
            targets += re.findall(r"`((?:assets|references)/[^`]+)`", doc.read_text())
            for target in targets:
                target = target.strip().strip("<>")
                if target.startswith(("https://", "http://")):
                    continue  # Research citations are not bundled file dependencies.
                if target.startswith("/"):
                    continue  # Host skills, source handles and tools live outside the package.
                with self.subTest(document=doc.name, target=target):
                    resource, _, fragment = target.partition("#")
                    resource, fragment = unquote(resource), unquote(fragment)
                    resolved = (doc.parent / resource).resolve() if resource else doc
                    if not resolved.is_relative_to(ROOT):
                        host_skill = resolved.suffix == ".md" and any(
                            resolved.is_relative_to(ROOT.parent / name)
                            for name in HOST_SKILLS
                        )
                        source_handle = resource.startswith("../../../../文档/yxj-wiki/")
                        self.assertTrue(host_skill or source_handle,
                                        "Undeclared external resource path")
                        continue
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.is_file())
                    if fragment:
                        headings = re.findall(r"^#+ (.+)$", resolved.read_text(), re.M)
                        slugs = {re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                                 for heading in headings}
                        slugs.update(re.findall(r'<a\s+id="([^"]+)"', resolved.read_text()))
                        self.assertIn(fragment, slugs)
                    pending.append(resolved)
        self.assertEqual(reachable, files)


if __name__ == "__main__":
    unittest.main()
