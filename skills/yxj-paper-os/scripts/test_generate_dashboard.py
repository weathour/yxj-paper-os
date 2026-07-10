#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
TEMPLATES = ROOT / "assets" / "templates"
GEN = SCRIPT_DIR / "generate_dashboard.py"
PACK = SCRIPT_DIR / "verify_design_pack.py"
RUBRIC = SCRIPT_DIR / "verify_dimension_rubric.py"
FILES = sorted(p.name for p in TEMPLATES.glob("*.md"))


def make_workspace(tmp: Path, *, handoff=False) -> Path:
    ws = tmp / "workspace"
    ws.mkdir()
    for name in FILES:
        shutil.copy2(TEMPLATES / name, ws / name)
    for path in ws.glob("*.md"):
        lines = [
            line
            for line in path.read_text().splitlines()
            if not (
                line.startswith("|")
                and "TODO" in line
                and not (line.startswith("| D") and line[3:5].isdigit())
            )
        ]
        path.write_text("\n".join(lines) + "\n")
    idx = ws / "00_DIMENSION_INDEX.md"
    text = idx.read_text()
    import re

    def fill_dimension(match):
        cells = [c.strip() for c in match.group(0).strip().strip("|").split("|")]
        cells[3:6] = ["filled", "recorded", "none"]
        cells[6] = "no"
        return "| " + " | ".join(cells) + " |"

    text = re.sub(r"^\| D\d\d \|.*\|$", fill_dimension, text, flags=re.M)
    if handoff:
        text = text.replace(
            "| SCOPE-01 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |",
            "| SCOPE-01 | Methods | scoped handoff | writer-ready | M-01 | none | none | none | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |",
        )
    idx.write_text(text)
    if handoff:
        row = "| SCOPE-01 | Methods | scoped handoff | writer-ready | M-01 | none | none | none | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |"
        for name, heading in (
            ("00_DIMENSION_INDEX.md", "Writing Scopes"),
            ("04_WRITING_DESIGN_PACK.md", "Scoped Handoff"),
        ):
            p = ws / name
            t = p.read_text()
            marker = f"## {heading}"
            pos = t.find(marker)
            sep = t.find("\n", t.find("|---", pos))
            t = t[: sep + 1] + row + "\n" + t[sep + 1 :]
            p.write_text(t)
    return ws


class DashboardContractTests(unittest.TestCase):
    def run_cmd(self, *args):
        return subprocess.run(
            [sys.executable, *map(str, args)],
            cwd=SCRIPT_DIR,
            text=True,
            capture_output=True,
        )

    def test_dimension_rubric_validator_passes(self):
        r = self.run_cmd(RUBRIC)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_sparse_validator_accepts_initialized_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            r = self.run_cmd(PACK, ws)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_sparse_validator_requires_handoff_only_in_handoff_mode(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            r = self.run_cmd(PACK, "--require-handoff", ws)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("require-handoff", r.stderr)

    def test_sparse_validator_accepts_scoped_handoff(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d), handoff=True)
            r = self.run_cmd(PACK, "--require-handoff", ws)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_legacy_workspace_gets_one_normalization_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            p = ws / "00_DIMENSION_INDEX.md"
            p.write_text(
                p.read_text().replace(
                    "Workspace schema version: 0.2", "Schema version: 1"
                )
            )
            r = self.run_cmd(PACK, ws)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stderr.count("legacy workspace"), 1)

    def test_dashboard_is_offline_and_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            before = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in ws.glob("*.md")
            }
            r = self.run_cmd(GEN, ws)
            self.assertEqual(r.returncode, 0, r.stderr)
            html = (ws / ".yxj-paper-os" / "dashboard.html").read_text()
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)
            self.assertIn("structural", html.lower())
            after = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in ws.glob("*.md")
            }
            self.assertEqual(before, after)

    def test_dashboard_missing_file_warns_without_writeback(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            (ws / "03_WRITING_STRUCTURE.md").unlink()
            r = self.run_cmd(GEN, ws)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((ws / ".yxj-paper-os" / "dashboard.html").is_file())
            self.assertFalse((ws / "03_WRITING_STRUCTURE.md").exists())

    def test_dashboard_malformed_table_degrades_to_warning(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            p = ws / "00_DIMENSION_INDEX.md"
            p.write_text(p.read_text().replace("| D00 |", "| D00 | broken |"))
            r = self.run_cmd(GEN, ws)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Warnings", r.stdout)

    def test_public_surface_stays_six_templates(self):
        self.assertEqual(
            set(FILES),
            {
                "00_DIMENSION_INDEX.md",
                "00_PROJECT_ROUTE.md",
                "01_MATERIALS_INVENTORY.md",
                "02_CLAIM_EVIDENCE_BOUNDARY.md",
                "03_WRITING_STRUCTURE.md",
                "04_WRITING_DESIGN_PACK.md",
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
