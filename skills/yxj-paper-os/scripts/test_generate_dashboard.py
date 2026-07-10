#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
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

    def test_dashboard_reads_canonical_template_analysis_without_writeback(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            analysis = ws / ".yxj-paper-os" / "template-analysis"
            analysis.mkdir(parents=True)
            summary = {
                "schema": "template-corpus-summary/1.0",
                "analysis_id": "analysis-dashboard-fixture",
                "corpus_id": "corpus-dashboard-fixture",
                "analyzer_version": "test-fixture",
                "document_count": 2,
                "parsed_document_count": 2,
                "groups": {
                    "overall": {
                        "group_id": "overall",
                        "document_count": 2,
                        "parsed_document_count": 2,
                        "metrics": {
                            "text.body_words": {
                                "valid_n": 2,
                                "missingness": 0,
                                "median": 5100,
                                "p25": 4800,
                                "p75": 5400,
                            }
                        },
                    },
                    "by_partition": [],
                    "by_article_type": [],
                    "by_partition_article_type": [],
                },
                "sequences": {"by_document": [], "top_sequences": []},
                "transitions": {"expected_total": 0, "observed_total": 0},
                "lead_lag": {"valid_n": 0, "observation_n": 0},
            }
            profile = {
                "schema": "template-design-profile/1.0",
                "analysis_id": "analysis-dashboard-fixture",
                "corpus_id": "corpus-dashboard-fixture",
                "analyzer_version": "test-fixture",
                "entries": [
                    {
                        "design_surface": "manuscript-length",
                        "target_kind": "watch_only",
                        "candidate_action": "adapt",
                        "partition": "overall",
                        "source_type": "corpus",
                        "origin": "model-proposed",
                        "observation": "median 5100 words",
                        "valid_n": 2,
                        "missingness": 0,
                        "uncertainty": {
                            "analysis_mode": "exploratory",
                            "sample_size_label": "case_set",
                            "sample_size_label_is_gate": False,
                        },
                        "boundary": "writing design only",
                        "source_pointer": "corpus-summary.json#groups.overall",
                    }
                ],
            }
            (analysis / "corpus-summary.json").write_text(
                json.dumps(summary), encoding="utf-8"
            )
            (analysis / "design-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )
            before = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in ws.glob("*.md")
            }
            r = self.run_cmd(GEN, ws)
            self.assertEqual(r.returncode, 0, r.stderr)
            dashboard = (ws / ".yxj-paper-os" / "dashboard.html").read_text()
            self.assertIn("text.body_words", dashboard)
            self.assertIn("watch_only", dashboard)
            self.assertIn("available", dashboard)
            self.assertEqual(
                before,
                {
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in ws.glob("*.md")
                },
            )

    def test_dashboard_rejects_mixed_analysis_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            ws = make_workspace(Path(directory))
            analysis = ws / ".yxj-paper-os" / "template-analysis"
            analysis.mkdir(parents=True)
            summary = {
                "schema": "template-corpus-summary/1.0",
                "analysis_id": "analysis-new",
                "corpus_id": "corpus-a",
                "analyzer_version": "1.0.0",
                "groups": {"overall": {"metrics": {"text.body_words": {"median": 1}}}},
                "sequences": {},
                "transitions": {},
                "lead_lag": {},
            }
            profile = {
                "schema": "template-design-profile/1.0",
                "analysis_id": "analysis-old",
                "corpus_id": "corpus-a",
                "analyzer_version": "1.0.0",
                "entries": [{"target_kind": "soft_band"}],
            }
            (analysis / "corpus-summary.json").write_text(
                json.dumps(summary), encoding="utf-8"
            )
            (analysis / "design-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )
            result = self.run_cmd(GEN, ws)
            self.assertEqual(result.returncode, 0, result.stderr)
            dashboard = (ws / ".yxj-paper-os" / "dashboard.html").read_text()
            self.assertIn("identity mismatch", dashboard)
            self.assertIn("inconsistent", dashboard)
            self.assertNotIn("soft_band", dashboard)
            self.assertNotIn("text.body_words</td>", dashboard)

    def test_dashboard_renders_priority_metrics_for_every_group(self):
        with tempfile.TemporaryDirectory() as directory:
            ws = make_workspace(Path(directory))
            analysis = ws / ".yxj-paper-os" / "template-analysis"
            analysis.mkdir(parents=True)

            def group(group_id: str) -> dict:
                metrics = {
                    f"noise.metric_{index:02d}": {
                        "valid_n": 3,
                        "missingness": 0,
                        "median": index,
                    }
                    for index in range(80)
                }
                metrics["text.body_words"] = {
                    "valid_n": 3,
                    "missingness": 0,
                    "median": 5000,
                }
                metrics["object.figure_count"] = {
                    "valid_n": 3,
                    "missingness": 0,
                    "median": 6,
                }
                return {
                    "group_id": group_id,
                    "document_count": 3,
                    "parsed_document_count": 3,
                    "metrics": metrics,
                }

            summary = {
                "schema": "template-corpus-summary/1.0",
                "analysis_id": "analysis-groups",
                "corpus_id": "fixture-corpus",
                "analyzer_version": "1.0.0",
                "groups": {
                    "overall": group("overall"),
                    "by_partition": [group("partition:primary_match")],
                    "by_article_type": [group("article_type:research-article")],
                    "by_partition_article_type": [
                        group("partition:primary_match|article_type:research-article")
                    ],
                },
                "sequences": {},
                "transitions": {},
                "lead_lag": {},
            }
            profile = {
                "schema": "template-design-profile/1.0",
                "analysis_id": "analysis-groups",
                "corpus_id": "fixture-corpus",
                "analyzer_version": "1.0.0",
                "entries": [],
            }
            (analysis / "corpus-summary.json").write_text(
                json.dumps(summary), encoding="utf-8"
            )
            (analysis / "design-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )
            result = self.run_cmd(GEN, ws)
            self.assertEqual(result.returncode, 0, result.stderr)
            dashboard = (ws / ".yxj-paper-os" / "dashboard.html").read_text()
            for group_id in (
                "overall",
                "partition:primary_match",
                "article_type:research-article",
                "partition:primary_match|article_type:research-article",
            ):
                self.assertIn(f'data-analysis-group="{group_id}"', dashboard)
            self.assertEqual(dashboard.count("Priority metrics shown: 10"), 4)
            self.assertEqual(dashboard.count("additional metrics omitted: 72"), 4)
            self.assertGreaterEqual(dashboard.count("text.body_words</td>"), 4)
            self.assertGreaterEqual(dashboard.count("object.figure_count</td>"), 4)

    def test_dashboard_malformed_template_analysis_degrades_safely(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            analysis = ws / ".yxj-paper-os" / "template-analysis"
            analysis.mkdir(parents=True)
            (analysis / "corpus-summary.json").write_text(
                '{"schema":"template-corpus-summary/1.0","groups":{}}',
                encoding="utf-8",
            )
            r = self.run_cmd(GEN, ws)
            self.assertEqual(r.returncode, 0, r.stderr)
            dashboard = (ws / ".yxj-paper-os" / "dashboard.html").read_text()
            self.assertIn("malformed", dashboard)
            self.assertIn("template-analysis", dashboard)

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
