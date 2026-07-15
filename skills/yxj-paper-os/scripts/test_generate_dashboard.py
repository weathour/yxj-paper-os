#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from test_verify_design_pack import (  # noqa: E402
    DETAILED,
    LEGACY,
    append_table_row,
    copy_fixture,
    install_second_ready_scope,
    install_semantic_rule,
    replace,
)
import generate_dashboard as dashboard_generator  # noqa: E402

ROOT = SCRIPT_DIR.parent
TEMPLATES = ROOT / "assets" / "templates"
TRUSTED_REGISTRY = ROOT / "assets" / "template-analysis" / "metric-registry.json"
TRUSTED_REGISTRY_SHA = hashlib.sha256(TRUSTED_REGISTRY.read_bytes()).hexdigest()
GEN = SCRIPT_DIR / "generate_dashboard.py"
ANALYZER = SCRIPT_DIR / "analyze_template_corpus.py"
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
    text = idx.read_text().replace(
        "Workspace schema version: 0.3",
        "Workspace schema version: 0.2",
    )
    # WP3 owns schema-0.3 semantic validation; legacy sparse tests stay explicit.
    import re

    def fill_dimension(match):
        cells = [c.strip() for c in match.group(0).strip().strip("|").split("|")]
        cells[3:6] = ["filled", "recorded", "none"]
        cells[6] = "no"
        return "| " + " | ".join(cells) + " |"

    text = re.sub(r"^\| D\d\d \|.*\|$", fill_dimension, text, flags=re.M)
    idx.write_text(text)
    if handoff:
        rows = (
            (
                "00_DIMENSION_INDEX.md",
                "Writing Scopes",
                "| SCOPE-01 | Methods | scoped handoff | writer-ready | M-01 | none | none | none | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage |",
            ),
            (
                "04_WRITING_DESIGN_PACK.md",
                "Scoped Handoff",
                "| SCOPE-01 | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | No external execution | Legacy sparse helper handoff |",
            ),
        )
        for name, heading, row in rows:
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

    def render(self, workspace: Path) -> str:
        result = self.run_cmd(GEN, workspace)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (workspace / ".yxj-paper-os" / "dashboard.html").read_text(
            encoding="utf-8"
        )

    def model(self, html_text: str) -> dict[str, Any]:
        match = re.search(
            r'<script id="dashboard-data" type="application/json">(.*?)</script>',
            html_text,
            re.S,
        )
        if match is None:
            self.fail("dashboard JSON model is missing")
        return json.loads(match.group(1))

    def assert_control_safe(self, value: Any) -> None:
        if isinstance(value, str):
            self.assertIsNone(dashboard_generator.CONTROL_CHAR_RE.search(value))
        elif isinstance(value, dict):
            for key, item in value.items():
                self.assert_control_safe(key)
                self.assert_control_safe(item)
        elif isinstance(value, list):
            for item in value:
                self.assert_control_safe(item)

    def install_analyzer(
        self,
        workspace: Path,
        *,
        analysis_id: str = "analysis-dashboard",
        profile_analysis_id: str | None = None,
        comparable: bool | None = True,
        action: str = "adapt",
        effective_mode: str = "case_set",
        actions: list[str] | None = None,
    ) -> Path:
        analysis = workspace / ".yxj-paper-os" / "template-analysis"
        analysis.mkdir(parents=True, exist_ok=True)
        identity = {
            "analysis_id": analysis_id,
            "corpus_id": "corpus-dashboard",
            "analyzer_version": "1.0.0",
        }
        metric_id = "text.body_words"
        manifest = {
            "schema": "template-corpus-normalized/1.0",
            **identity,
            "target": {},
            "analysis_mode": effective_mode,
            "requested_analysis_mode": effective_mode,
            "effective_analysis_mode": effective_mode,
            "analysis_mode_source": "manifest_declared",
            "design_question": "How should body length be treated as design input?",
            "design_metric_ids": [metric_id],
            "source_manifest_sha256": "a" * 64,
            "metric_registry_sha256": TRUSTED_REGISTRY_SHA,
            "documents": [],
            "official_constraints": [],
        }
        registry = {
            "schema": "template-metric-registry/1.0",
            **identity,
            "version": "1.0",
            "registry_version": "1.0",
            "metrics": [{"metric_id": metric_id}],
        }
        summary = {
            "schema": "template-corpus-summary/1.0",
            **identity,
            "analysis_unit": "paper",
            "analysis_mode": effective_mode,
            "requested_analysis_mode": effective_mode,
            "effective_analysis_mode": effective_mode,
            "design_question": manifest["design_question"],
            "design_metric_ids": [metric_id],
            "analysis_mode_source": "manifest_declared",
            "groups": {
                "overall": {
                    "group_id": "overall",
                    "metrics": {
                        metric_id: {
                            "valid_n": 2,
                            "eligible_n": 2,
                            "missingness": 0,
                            "sample_size_label": "case_set",
                            "sample_size_label_is_gate": False,
                            "median": 5100,
                            "p25": 4800,
                            "p75": 5400,
                        }
                    },
                }
            },
            "sequences": {},
            "transitions": {},
            "lead_lag": {},
        }
        requested_actions = actions or [action]
        entries = []
        for index, candidate_action in enumerate(requested_actions, 1):
            uncertainty: dict[str, object] = {
                "analysis_mode": effective_mode,
                "requested_analysis_mode": effective_mode,
                "effective_analysis_mode": effective_mode,
                "metric_effective_analysis_mode": effective_mode,
                "sample_size_label": "case_set",
                "sample_size_label_is_gate": False,
            }
            if comparable is not None:
                uncertainty["comparable_stratum"] = comparable
            entries.append(
                {
                    "profile_id": f"corpus:{metric_id}:{index}",
                    "source_type": "corpus",
                    "partition": "overall",
                    "metric_ids": [metric_id],
                    "observation": "available-paper median and quartiles",
                    "valid_n": 2,
                    "missingness": 0,
                    "uncertainty": uncertainty,
                    "design_surface": "manuscript-length",
                    "target_kind": "watch_only",
                    "candidate_action": candidate_action,
                    "affected_dimensions": ["D09"],
                    "affected_scopes": [],
                    "boundary": "Candidate descriptive writing-design pattern only.",
                    "source_pointer": "corpus-summary.json#groups.overall",
                    "origin": "model-proposed",
                    "resolution": "candidate",
                }
            )
        profile = {
            "schema": "template-design-profile/1.0",
            **identity,
            "analysis_id": profile_analysis_id or analysis_id,
            "design_question": manifest["design_question"],
            "design_metric_ids": [metric_id],
            "entries": entries,
            "forbidden_uses": ["No scientific authority."],
        }
        for name, payload in (
            ("manifest.json", manifest),
            ("metric-registry.json", registry),
            ("corpus-summary.json", summary),
            ("design-profile.json", profile),
        ):
            (analysis / name).write_text(json.dumps(payload), encoding="utf-8")
        return analysis

    def test_dimension_rubric_validator_passes(self):
        r = self.run_cmd(RUBRIC)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_legacy_initialized_workspace_is_downgraded_once(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            r = self.run_cmd(PACK, ws)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stderr.count("SCHEMA_LEGACY_02:"), 1)

    def test_legacy_schema_short_circuits_require_handoff_checks(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            r = self.run_cmd(PACK, "--require-handoff", ws)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stderr.count("SCHEMA_LEGACY_02:"), 1)
            self.assertNotIn("HANDOFF_SCOPE_CARDINALITY", r.stderr)

    def test_legacy_scoped_handoff_does_not_restore_current_readiness(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d), handoff=True)
            r = self.run_cmd(PACK, "--require-handoff", ws)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stderr.count("SCHEMA_LEGACY_02:"), 1)

    def test_missing_schema_marker_gets_one_primary_diagnostic(self):
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
            self.assertEqual(r.stderr.count("SCHEMA_MISSING:"), 1)

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

    def test_dashboard_reads_complete_allowlisted_analysis_without_writeback(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            self.install_analyzer(workspace)
            before = {
                str(path.relative_to(workspace)): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in workspace.rglob("*")
                if path.is_file()
            }
            dashboard = self.render(workspace)
            model = self.model(dashboard)
            analyzer = model["template_analysis"]
            self.assertEqual(analyzer["state"], "current")
            self.assertEqual(analyzer["selected_metric_ids"], ["text.body_words"])
            self.assertEqual(analyzer["metric_summaries"][0]["median"], 5100)
            self.assertEqual(
                model["analyzer_projection"]["candidate_actions"], ["adapt"]
            )
            self.assertNotIn("observation", analyzer["candidates"][0])
            self.assertNotIn("boundary", analyzer["candidates"][0])
            self.assertNotIn("data", analyzer)
            self.assertNotIn("preview", analyzer)
            after = {
                str(path.relative_to(workspace)): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in workspace.rglob("*")
                if path.is_file()
                and path != workspace / ".yxj-paper-os" / "dashboard.html"
            }
            self.assertEqual(before, after)

    def test_dashboard_rejects_mixed_analysis_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            analysis = self.install_analyzer(workspace)
            profile_path = analysis / "design-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["analysis_id"] = "analysis-old"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            dashboard = self.render(workspace)
            analyzer = self.model(dashboard)["template_analysis"]
            self.assertEqual(analyzer["state"], "mixed")
            self.assertIn("ANALYZER_MIXED_IDENTITY", analyzer["violations"])
            self.assertNotIn("analysis-old", dashboard)
            self.assertNotIn("text.body_words</td>", dashboard)

    def test_dashboard_projects_only_registered_selected_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            analysis = self.install_analyzer(workspace)
            summary_path = analysis / "corpus-summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["groups"]["overall"]["metrics"]["unselected.metric"] = {
                "valid_n": 2,
                "missingness": 0,
                "median": 991122,
            }
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            dashboard = self.render(workspace)
            analyzer = self.model(dashboard)["template_analysis"]
            self.assertEqual(analyzer["state"], "degraded")
            self.assertEqual(analyzer["selected_metric_ids"], ["text.body_words"])
            self.assertEqual(len(analyzer["metric_summaries"]), 1)
            self.assertEqual(
                analyzer["metric_summaries"][0]["metric_id"], "text.body_words"
            )
            self.assertNotIn("unselected.metric", dashboard)
            self.assertNotIn("991122", dashboard)

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
            analyzer = self.model(dashboard)["template_analysis"]
            self.assertEqual(analyzer["state"], "degraded")
            self.assertIn("ANALYZER_BUNDLE", analyzer["violations"])
            self.assertEqual(analyzer["artifacts"]["summary"]["state"], "validated")
            self.assertEqual(analyzer["artifacts"]["manifest"]["state"], "absent")

    def test_incomplete_two_file_analyzer_reproduction_never_leaks_or_scores(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            analysis = workspace / ".yxj-paper-os" / "template-analysis"
            analysis.mkdir(parents=True)
            identity = {
                "analysis_id": "analysis-minimal-reproduction",
                "corpus_id": "corpus-minimal-reproduction",
                "analyzer_version": "1.0.0",
            }
            summary_secret = "TOP_SECRET_ORACLE_SUMMARY_8f71"
            profile_secret = "TOP_SECRET_PROMPT_PROFILE_8f72"
            summary = {
                "schema": "template-corpus-summary/1.0",
                **identity,
                "oracle": summary_secret,
                "groups": {
                    "overall": {
                        "metrics": {
                            "paper.quality_score": {
                                "valid_n": 1,
                                "missingness": 0,
                                "median": 991177,
                            }
                        }
                    }
                },
                "sequences": {},
                "transitions": {},
                "lead_lag": {},
            }
            profile = {
                "schema": "template-design-profile/1.0",
                **identity,
                "entries": [
                    {
                        "design_surface": "claim-strength",
                        "target_kind": "semantic_adequacy_score",
                        "candidate_action": "adapt",
                        "observation": "The method is novel and scientifically adequate.",
                        "boundary": "scientific authority",
                        "prompt": profile_secret,
                        "uncertainty": {
                            "effective_analysis_mode": "case_set",
                            "comparable_stratum": True,
                        },
                    }
                ],
            }
            (analysis / "corpus-summary.json").write_text(
                json.dumps(summary), encoding="utf-8"
            )
            (analysis / "design-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )
            dashboard = self.render(workspace)
            analyzer = self.model(dashboard)["template_analysis"]
            self.assertEqual(analyzer["state"], "degraded")
            self.assertIn("ANALYZER_BUNDLE", analyzer["violations"])
            for forbidden in (
                summary_secret,
                profile_secret,
                "paper.quality_score",
                "semantic_adequacy_score",
                "991177",
            ):
                self.assertNotIn(forbidden, dashboard)
                self.assertNotIn(forbidden, json.dumps(analyzer))

    def test_canonical_detailed_projection_covers_all_control_surfaces(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            dashboard = self.render(workspace)
            model = self.model(dashboard)
            self.assertEqual(model["schema"]["state"], "current")
            self.assertIn("current detailed-ready", dashboard)
            self.assertIn("Declared structural coverage", dashboard)
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["scope_id"], "SCOPE-demo")
            self.assertEqual(scope["declared_readiness"], "writer-ready")
            self.assertTrue(scope["current_detailed_ready"])
            self.assertEqual(
                {row["Surface"] for row in scope["coverage"]},
                {
                    "section_paragraph_map",
                    "surface_language_contract",
                    "visual_caption_blueprint",
                    "cross_surface_traceability",
                    "template_rule_provenance",
                    "soft_budgets",
                    "important_paragraph_frames",
                },
            )
            self.assertEqual(scope["summary"]["Section count"], "1")
            self.assertEqual(scope["summary"]["Paragraph count"], "2")
            self.assertEqual(scope["summary"]["Important paragraph count"], "1")
            self.assertEqual(scope["summary"]["Frame count"], "2")
            self.assertEqual(
                set(model["design_pack"]["owner_gate_categories"]),
                {
                    "scientific_commitment",
                    "argument_spine",
                    "material_local_tradeoff",
                    "deliberate_divergence",
                },
            )
            self.assertEqual(
                model["design_pack"]["template_modes"],
                sorted(
                    [
                        "semantic_primary",
                        "semantic_plus_quantitative",
                        "quantitative_only",
                        "generic_fallback",
                        "not_applicable",
                    ]
                ),
            )
            self.assertIn("04 is a pointer-only non-authority", dashboard)
            self.assertNotIn("quality score", dashboard.lower())

    def test_legacy_fixture_requires_migration_and_never_projects_current_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(LEGACY, Path(directory))
            dashboard = self.render(workspace)
            model = self.model(dashboard)
            self.assertEqual(model["schema"]["state"], "legacy_migration_required")
            self.assertIn("Legacy detailed-readiness migration required", dashboard)
            self.assertNotIn("current detailed-ready", dashboard)
            self.assertTrue(
                all(
                    scope["dashboard_readiness"] == "migration_required"
                    for scope in model["design_pack"]["scopes"]
                )
            )

    def test_public_missing_malformed_and_invalid_utf8_degrade_locally(self):
        mutations = ("missing", "malformed", "invalid-utf8")
        for mutation in mutations:
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                path = workspace / "03_WRITING_STRUCTURE.md"
                if mutation == "missing":
                    path.unlink()
                elif mutation == "malformed":
                    path = workspace / "04_WRITING_DESIGN_PACK.md"
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| Surface | Scope ID | Handling (`satisfied&#124;not_applicable`) |",
                        "| Surface | broken | Scope ID | Handling (`satisfied&#124;not_applicable`) |",
                    )
                else:
                    path.write_bytes(b"\xff\xfeinvalid")
                dashboard = self.render(workspace)
                model = self.model(dashboard)
                self.assertGreater(model["warning_count"], 0)
                self.assertTrue(
                    any(
                        item["scope"] in {"03_WRITING_STRUCTURE.md", "validator"}
                        for item in model["warnings"]
                    )
                )
                if mutation == "missing":
                    self.assertFalse(path.exists())

    def test_semantic_dossier_absent_current_stale_and_projection_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            absent = copy_fixture(DETAILED, Path(directory) / "absent")
            absent_model = self.model(self.render(absent))
            self.assertEqual(absent_model["semantic_dossier"]["state"], "absent")
            self.assertEqual(absent_model["semantic_dossier"]["counts"]["rules"], 0)

            current = copy_fixture(DETAILED, Path(directory) / "current")
            install_semantic_rule(current)
            current_html = self.render(current)
            current_model = self.model(current_html)
            dossier = current_model["semantic_dossier"]
            self.assertEqual(dossier["state"], "current")
            self.assertEqual(
                dossier["counts"], {"documents": 1, "observations": 1, "rules": 1}
            )
            self.assertEqual(dossier["projection_state"], "current")
            self.assertIn("owner-supplied local derivative", current_html)
            self.assertIn("verified_local_current", current_html)
            self.assertNotIn("prompt_identity", current_html)
            self.assertNotIn("semantic_interpretation", current_html)

            stale = copy_fixture(DETAILED, Path(directory) / "stale")
            install_semantic_rule(stale)
            dossier_path = (
                stale / ".yxj-paper-os" / "template-analysis" / "semantic-dossier.json"
            )
            payload = json.loads(dossier_path.read_text(encoding="utf-8"))
            payload["documents"][0]["freshness"] = "stale"
            payload["transfer_rules"][0]["source_freshness"] = "stale"
            dossier_path.write_text(json.dumps(payload), encoding="utf-8")
            replace(
                stale,
                "03_WRITING_STRUCTURE.md",
                "| verified_local_current |",
                "| stale |",
            )
            self.assertEqual(
                self.model(self.render(stale))["semantic_dossier"]["state"], "stale"
            )

            mismatch = copy_fixture(DETAILED, Path(directory) / "mismatch")
            install_semantic_rule(mismatch)
            replace(
                mismatch,
                "03_WRITING_STRUCTURE.md",
                "Place the bounded object before mechanism detail.",
                "Project a deliberately mismatched public rule.",
            )
            mismatch_dossier = self.model(self.render(mismatch))["semantic_dossier"]
            self.assertEqual(mismatch_dossier["state"], "projection_mismatch")
            self.assertEqual(mismatch_dossier["projection_state"], "mismatch")

    def test_semantic_dossier_invalid_json_and_utf8_degrade_without_crash(self):
        for payload in (b'{"schema":', b"\xff\xfe"):
            with (
                self.subTest(payload=payload),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                hidden = workspace / ".yxj-paper-os" / "template-analysis"
                hidden.mkdir(parents=True)
                (hidden / "semantic-dossier.json").write_bytes(payload)
                model = self.model(self.render(workspace))
                self.assertEqual(model["semantic_dossier"]["state"], "malformed")
                self.assertTrue(model["semantic_dossier"]["diagnostics"])

    def test_analyzer_projection_states_are_explicit_and_neutral_when_absent(self):
        cases: tuple[tuple[str, dict[str, Any], str], ...] = (
            ("current", {}, "current"),
            ("mixed", {"profile_analysis_id": "analysis-other"}, "mixed"),
            ("incomparable", {"comparable": False}, "incomparable"),
            ("unknown-action", {"action": "invent"}, "unknown_action"),
        )
        with tempfile.TemporaryDirectory() as directory:
            absent = copy_fixture(DETAILED, Path(directory) / "absent")
            absent_model = self.model(self.render(absent))["analyzer_projection"]
            self.assertEqual(absent_model["state"], "absent")
            self.assertEqual(absent_model["comparability"], ["N/A"])
            self.assertEqual(absent_model["candidate_actions"], ["N/A"])
            for label, kwargs, expected in cases:
                with self.subTest(label=label):
                    workspace = copy_fixture(DETAILED, Path(directory) / label)
                    self.install_analyzer(workspace, **kwargs)
                    analyzer = self.model(self.render(workspace))["analyzer_projection"]
                    self.assertEqual(analyzer["state"], expected)
                    if expected == "current":
                        self.assertEqual(analyzer["effective_modes"], ["case_set"])
                        self.assertEqual(analyzer["comparability"], ["comparable"])
                        self.assertEqual(analyzer["candidate_actions"], ["adapt"])
                        self.assertEqual(
                            analyzer["identity"]["analysis_id"], "analysis-dashboard"
                        )
                    elif expected == "unknown_action":
                        self.assertEqual(analyzer["candidate_actions"], ["unknown"])
                        self.assertIn("ANALYZER_UNKNOWN_ACTION", analyzer["violations"])

    def test_complete_analyzer_bundle_preserves_all_four_candidate_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            actions = [
                "follow",
                "adapt",
                "deliberate_divergence",
                "not_applicable",
            ]
            self.install_analyzer(workspace, actions=actions)
            model = self.model(self.render(workspace))
            self.assertEqual(model["template_analysis"]["state"], "current")
            self.assertEqual(
                model["analyzer_projection"]["candidate_actions"], sorted(actions)
            )
            self.assertEqual(len(model["template_analysis"]["candidates"]), 4)

    def test_production_analyzer_bundle_is_a_current_positive_path(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            corpus = workspace / "corpus"
            corpus.mkdir()
            shutil.copy2(
                ROOT / "assets" / "fixtures" / "template-analysis" / "article.md",
                corpus / "article.md",
            )
            manifest = workspace / "template-corpus.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "template-corpus/1.0",
                        "corpus_id": "dashboard-production",
                        "analysis_mode": "case_set",
                        "design_question": "How should body length guide writing design?",
                        "design_metric_ids": ["text.body_words"],
                        "documents": [
                            {
                                "doc_id": "article",
                                "path": "corpus/article.md",
                                "format": "markdown",
                                "partition": "primary_match",
                                "venue": "Fixture Journal",
                                "topic_tags": ["transport"],
                                "article_type": "research-article",
                                "year": 2026,
                                "language": "en",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_cmd(ANALYZER, "--manifest", manifest)
            self.assertEqual(result.returncode, 0, result.stderr)
            analyzer = self.model(self.render(workspace))["template_analysis"]
            self.assertEqual(analyzer["state"], "current")
            self.assertEqual(analyzer["violations"], [])
            self.assertEqual(analyzer["selected_metric_ids"], ["text.body_words"])
            self.assertEqual(analyzer["candidates"][0]["candidate_action"], "adapt")

    def test_workspace_registry_cannot_invent_a_supported_metric(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            analysis = self.install_analyzer(workspace)
            invented = "paper.readiness_rating"

            manifest_path = analysis / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["design_metric_ids"] = [invented]
            manifest["metric_registry_sha256"] = TRUSTED_REGISTRY_SHA
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            registry_path = analysis / "metric-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["metrics"] = [{"metric_id": invented}]
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            summary_path = analysis / "corpus-summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["design_metric_ids"] = [invented]
            summary["groups"]["overall"]["metrics"] = {
                invented: {
                    "valid_n": 2,
                    "eligible_n": 2,
                    "missingness": 0,
                    "sample_size_label": "case_set",
                    "sample_size_label_is_gate": False,
                    "median": 99881,
                }
            }
            summary_path.write_text(json.dumps(summary), encoding="utf-8")

            profile_path = analysis / "design-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["design_metric_ids"] = [invented]
            profile["entries"][0]["profile_id"] = f"corpus:{invented}:1"
            profile["entries"][0]["metric_ids"] = [invented]
            profile_path.write_text(json.dumps(profile), encoding="utf-8")

            dashboard = self.render(workspace)
            model = self.model(dashboard)
            analyzer = model["template_analysis"]
            self.assertEqual(analyzer["state"], "degraded")
            self.assertIn("ANALYZER_UNSUPPORTED_METRIC", analyzer["violations"])
            self.assertEqual(analyzer["selected_metric_ids"], [])
            projection = json.dumps(
                {
                    "template_analysis": analyzer,
                    "analyzer_projection": model["analyzer_projection"],
                }
            )
            self.assertNotIn(invented, dashboard)
            self.assertNotIn(invented, projection)
            self.assertNotIn("99881", dashboard)
            self.assertNotIn("99881", projection)

    def test_analyzer_registry_digest_is_bound_to_shipped_registry_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            analysis = self.install_analyzer(workspace)
            manifest_path = analysis / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["metric_registry_sha256"] = "b" * 64
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            analyzer = self.model(self.render(workspace))["template_analysis"]
            self.assertEqual(analyzer["state"], "degraded")
            self.assertIn("ANALYZER_REGISTRY_DIGEST", analyzer["violations"])
            self.assertEqual(
                analyzer["provenance"]["metric_registry_sha256"], "unknown"
            )

    def test_analyzer_forbidden_fields_scores_and_secret_values_never_project(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            analysis = self.install_analyzer(workspace)
            sentinels = {
                "manifest": "SENTINEL_SECRET_MANIFEST_731",
                "registry": "SENTINEL_ORACLE_REGISTRY_732",
                "summary": "SENTINEL_COPIED_SUMMARY_733",
                "profile": "SENTINEL_PROMPT_PROFILE_734",
                "entry": "SENTINEL_SECRET_ENTRY_735",
                "uncertainty": "SENTINEL_ORACLE_UNCERTAINTY_736",
                "interval": "SENTINEL_SECRET_INTERVAL_737",
                "mode": "SENTINEL_SECRET_MODE_738",
                "candidate": "SENTINEL_SECRET_CANDIDATE_739",
                "partition": "SENTINEL_SECRET_PARTITION_740",
                "source_type": "SENTINEL_SECRET_SOURCE_TYPE_741",
            }

            manifest_path = analysis / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["prompt_identity"] = sentinels["manifest"]
            manifest["effective_analysis_mode"] = sentinels["mode"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            registry_path = analysis / "metric-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["oracle_body"] = sentinels["registry"]
            registry["metrics"].append(
                {
                    "metric_id": "paper.quality_score",
                    "paper_quality_score": 991122,
                }
            )
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            summary_path = analysis / "corpus-summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["copied_body"] = sentinels["summary"]
            summary["groups"]["overall"]["metrics"]["paper.venue_fit_score"] = {
                "valid_n": 2,
                "eligible_n": 2,
                "missingness": 0,
                "median": 992233,
            }
            for metric_id, value in (
                ("semantic_completeness_score", 99),
                ("paper_quality_score", 98),
                ("venue_fit_score", 97),
            ):
                summary["groups"]["overall"]["metrics"][metric_id] = {
                    "valid_n": 2,
                    "eligible_n": 2,
                    "missingness": 0,
                    "median": value,
                }
            summary["groups"]["overall"]["metrics"]["text.body_words"][
                "bootstrap_95_ci"
            ] = [sentinels["interval"], 5400]
            summary_path.write_text(json.dumps(summary), encoding="utf-8")

            profile_path = analysis / "design-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["secret"] = sentinels["profile"]
            profile["entries"][0]["oracle_body"] = sentinels["entry"]
            profile["entries"][0]["profile_id"] = sentinels["candidate"]
            profile["entries"][0]["partition"] = sentinels["partition"]
            profile["entries"][0]["source_type"] = sentinels["source_type"]
            profile["entries"][0]["semantic_completeness_score"] = 993344
            profile["entries"][0]["uncertainty"]["effective_analysis_mode"] = sentinels[
                "mode"
            ]
            profile["entries"][0]["uncertainty"]["metric_effective_analysis_mode"] = (
                sentinels["mode"]
            )
            profile["entries"][0]["uncertainty"]["prompt_identity"] = sentinels[
                "uncertainty"
            ]
            profile["entries"][0]["observation"] = (
                "This paper is scientifically adequate and predicts acceptance."
            )
            profile_path.write_text(json.dumps(profile), encoding="utf-8")

            dashboard = self.render(workspace)
            model = self.model(dashboard)
            analyzer = model["template_analysis"]
            self.assertEqual(analyzer["state"], "degraded")
            self.assertIn("ANALYZER_FORBIDDEN_FIELD", analyzer["violations"])
            self.assertIn("ANALYZER_FORBIDDEN_METRIC", analyzer["violations"])
            self.assertIn("ANALYZER_METRIC_VALUE", analyzer["violations"])
            self.assertIn("ANALYZER_SEMANTIC_CLAIM", analyzer["violations"])
            projection_text = json.dumps(
                {
                    "template_analysis": analyzer,
                    "analyzer_projection": model["analyzer_projection"],
                },
                ensure_ascii=False,
            )
            for sentinel in sentinels.values():
                self.assertNotIn(sentinel, dashboard)
                self.assertNotIn(sentinel, projection_text)
            for forbidden in (
                "paper.quality_score",
                "paper.venue_fit_score",
                "semantic_completeness_score",
                "paper_quality_score",
                "venue_fit_score",
                "991122",
                "992233",
                "993344",
            ):
                self.assertNotIn(forbidden, dashboard)
                self.assertNotIn(forbidden, projection_text)
            for forbidden_value in (99, 98, 97):
                self.assertNotIn(f'"median": {forbidden_value}', projection_text)
            for forbidden_key in (
                "data",
                "preview",
                "observation",
                "boundary",
                "target_kind",
                "source_pointer",
            ):
                self.assertNotIn(forbidden_key, analyzer["candidates"][0])

    def test_scope_blocker_projection_is_selective_across_scopes(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            install_second_ready_scope(workspace)
            replace(
                workspace,
                "00_DIMENSION_INDEX.md",
                "| SCOPE-demo | Synthetic two-paragraph method surface | Controlled writing handoff | writer-ready | M-method;M-evidence;M-visual | REQ-detailed | none | none |",
                "| SCOPE-demo | Synthetic two-paragraph method surface | Controlled writing handoff | partial | M-method;M-evidence;M-visual | REQ-detailed | M-evidence | Resolve evidence blocker |",
            )
            scopes = {
                item["scope_id"]: item
                for item in self.model(self.render(workspace))["design_pack"]["scopes"]
            }
            self.assertEqual(scopes["SCOPE-demo"]["declared_readiness"], "partial")
            self.assertIn("M-evidence", scopes["SCOPE-demo"]["blocker_ids"])
            self.assertNotIn("M-evidence", scopes["SCOPE-other"]["blocker_ids"])

    def test_scope_authority_ignores_orphan_scope_rows_from_04(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            append_table_row(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Template Analysis Handling",
                "| SCOPE-ghost | not_applicable | none | none | none | design_only | Orphan mirror row | none |",
            )
            model = self.model(self.render(workspace))
            scopes = model["design_pack"]["scopes"]
            self.assertEqual([item["scope_id"] for item in scopes], ["SCOPE-demo"])
            self.assertEqual(scopes[0]["dashboard_readiness"], "writer-ready")
            projection = model["design_pack"]["validation_projection"]
            self.assertEqual(projection["global_diagnostic_ids"], [])
            self.assertTrue(projection["orphan_diagnostic_ids"])
            self.assertTrue(
                any(
                    "orphan 04 mirror row" in item["message"]
                    for item in model["warnings"]
                )
            )

    def test_orphan_04_rows_cannot_borrow_real_record_ownership(self):
        mutations = (
            (
                "gate",
                "Owner Gate Resolution Summary",
                "| SCOPE-ghost | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
            ),
            (
                "unresolved",
                "Unresolved and Downstream Prohibitions",
                "| SCOPE-ghost | DEC-route;M-evidence | Ghost consequence | Ghost prohibition |",
            ),
        )
        for label, heading, row in mutations:
            with (
                self.subTest(label=label),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                append_table_row(workspace, "04_WRITING_DESIGN_PACK.md", heading, row)
                model = self.model(self.render(workspace))
                scope = model["design_pack"]["scopes"][0]
                self.assertEqual(scope["scope_id"], "SCOPE-demo")
                self.assertEqual(scope["dashboard_readiness"], "writer-ready")
                self.assertEqual(scope["mechanical_diagnostic_ids"], [])
                projection = model["design_pack"]["validation_projection"]
                self.assertEqual(projection["global_diagnostic_ids"], [])
                self.assertTrue(projection["orphan_diagnostic_ids"])
                for diagnostic in projection["diagnostics"]:
                    self.assertEqual(diagnostic["affected_scope_ids"], [])
                    self.assertIn("SCOPE-ghost", diagnostic["orphan_scope_ids"])

    def test_uppercase_malformed_scope_subject_cannot_borrow_decision_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            append_table_row(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Owner Gate Resolution Summary",
                "| SCOPE-GHOST | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
            )
            model = self.model(self.render(workspace))
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["dashboard_readiness"], "writer-ready")
            self.assertEqual(scope["mechanical_diagnostic_ids"], [])
            projection = model["design_pack"]["validation_projection"]
            self.assertEqual(projection["global_diagnostic_ids"], [])
            self.assertTrue(projection["orphan_diagnostic_ids"])
            self.assertEqual(
                projection["diagnostics"][0]["orphan_scope_ids"], ["SCOPE-GHOST"]
            )
            self.assertEqual(projection["diagnostics"][0]["affected_scope_ids"], [])

    def test_empty_suffix_and_prefixed_owner_gate_subjects_suppress_record_fallback(
        self,
    ):
        self.assertEqual(
            dashboard_generator.extract_scope_subjects(
                "SYNTHETIC: XSCOPE-demo/DEC-route"
            ),
            set(),
        )
        for raw_subject in (
            "SCOPE-",
            "XSCOPE-demo",
            "SCOPE-demo.",
            "SCOPE-demo:evil",
            "SCOPE-demo evil",
        ):
            with (
                self.subTest(raw_subject=raw_subject),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                append_table_row(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Owner Gate Resolution Summary",
                    f"| {raw_subject} | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                )
                model = self.model(self.render(workspace))
                scope = model["design_pack"]["scopes"][0]
                self.assertEqual(scope["dashboard_readiness"], "writer-ready")
                self.assertEqual(scope["mechanical_diagnostic_ids"], [])
                projection = model["design_pack"]["validation_projection"]
                self.assertEqual(projection["global_diagnostic_ids"], [])
                self.assertTrue(projection["orphan_diagnostic_ids"])
                diagnostic = projection["diagnostics"][0]
                self.assertEqual(diagnostic["affected_scope_ids"], [])
                self.assertEqual(diagnostic["orphan_scope_ids"], [raw_subject])

    def test_exact_declared_owner_gate_subject_remains_scope_local(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            contents, warnings = dashboard_generator.load_workspace(workspace)
            self.assertEqual(warnings, [])
            projection = dashboard_generator.build_validation_projection(
                [
                    "OWNER_GATE: SCOPE-demo/DEC-route summary differs from authoritative decision"
                ],
                contents,
                {"SCOPE-demo"},
                set(),
                {},
            )
            diagnostic = projection["diagnostics"][0]
            self.assertEqual(diagnostic["affected_scope_ids"], ["SCOPE-demo"])
            self.assertEqual(diagnostic["orphan_scope_ids"], [])
            self.assertFalse(diagnostic["global"])

        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable | Use the synthetic generic route for contract characterization | SCOPE-demo | artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief | Route or scope changes |",
                "| DEC-route | not_applicable | Use the synthetic generic route for contract characterization | SCOPE-demo | artifact-observed | confirmed | none | Route or scope changes |",
            )
            append_table_row(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Owner Gate Resolution Summary",
                "| DEC-route | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
            )
            model = self.model(self.render(workspace))
            projection = model["design_pack"]["validation_projection"]
            errors = model["validation"]["errors"]
            authoritative_index = next(
                index
                for index, message in enumerate(errors)
                if "DEC-route lacks valid grounding" in message
            )
            authoritative = projection["diagnostics"][authoritative_index]
            self.assertEqual(authoritative["affected_scope_ids"], ["SCOPE-demo"])
            self.assertEqual(authoritative["orphan_scope_ids"], [])
            mirror_index = next(
                index
                for index, message in enumerate(errors)
                if "DEC-route/DEC-route summary differs" in message
            )
            mirror = projection["diagnostics"][mirror_index]
            self.assertEqual(mirror["affected_scope_ids"], [])
            self.assertEqual(mirror["orphan_scope_ids"], ["DEC-route"])
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["dashboard_readiness"], "mechanically_blocked")
            self.assertIn(
                authoritative["diagnostic_id"], scope["mechanical_diagnostic_ids"]
            )
            self.assertTrue(
                any(
                    "orphan 04 mirror row ignored for undeclared scope DEC-route"
                    in item["message"]
                    for item in model["warnings"]
                )
            )

        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            orphan_row = "| DEC-route | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | M-fake |"
            for _ in range(2):
                append_table_row(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Owner Gate Resolution Summary",
                    orphan_row,
                )
            model = self.model(self.render(workspace))
            errors = model["validation"]["errors"]
            self.assertTrue(
                any(
                    "duplicate owner-gate summary key DEC-route/DEC-route" in item
                    for item in errors
                )
            )
            self.assertTrue(
                any(
                    "DEC-route owner-gate summary has invalid blockers" in item
                    for item in errors
                )
            )
            self.assertTrue(
                any(
                    "DEC-route owner-gate blockers differ from authoritative 00 scope row"
                    in item
                    for item in errors
                )
            )
            projection = model["design_pack"]["validation_projection"]
            self.assertTrue(projection["orphan_diagnostic_ids"])
            self.assertEqual(projection["global_diagnostic_ids"], [])
            for diagnostic in projection["diagnostics"]:
                self.assertEqual(diagnostic["affected_scope_ids"], [])
                self.assertEqual(diagnostic["orphan_scope_ids"], ["DEC-route"])
                self.assertFalse(diagnostic["global"])
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["dashboard_readiness"], "writer-ready")
            self.assertEqual(scope["mechanical_diagnostic_ids"], [])

        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | M-fake |",
            )
            model = self.model(self.render(workspace))
            errors = model["validation"]["errors"]
            relevant_indexes = [
                index
                for index, message in enumerate(errors)
                if "SCOPE-demo owner-gate" in message
            ]
            self.assertGreaterEqual(len(relevant_indexes), 2)
            projection = model["design_pack"]["validation_projection"]
            for index in relevant_indexes:
                diagnostic = projection["diagnostics"][index]
                self.assertEqual(diagnostic["affected_scope_ids"], ["SCOPE-demo"])
                self.assertEqual(diagnostic["orphan_scope_ids"], [])
                self.assertFalse(diagnostic["global"])
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["dashboard_readiness"], "mechanically_blocked")

        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            install_second_ready_scope(workspace)
            owner_row = "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |"
            path = workspace / "04_WRITING_DESIGN_PACK.md"
            text = path.read_text(encoding="utf-8")
            self.assertIn(owner_row + "\n", text)
            path.write_text(text.replace(owner_row + "\n", "", 1), encoding="utf-8")
            model = self.model(self.render(workspace))
            scopes = {item["scope_id"]: item for item in model["design_pack"]["scopes"]}
            self.assertEqual(
                scopes["SCOPE-demo"]["dashboard_readiness"],
                "mechanically_blocked",
            )
            self.assertEqual(
                scopes["SCOPE-other"]["dashboard_readiness"], "writer-ready"
            )
            self.assertEqual(scopes["SCOPE-other"]["mechanical_diagnostic_ids"], [])
            errors = model["validation"]["errors"]
            projection = model["design_pack"]["validation_projection"]
            expected_messages = (
                "SCOPE-demo lacks an Owner Gate Resolution Summary row",
                "SCOPE-demo/DEC-route is absent from the 04 owner-gate summary",
            )
            for expected in expected_messages:
                index = next(
                    index for index, message in enumerate(errors) if expected in message
                )
                diagnostic = projection["diagnostics"][index]
                self.assertEqual(diagnostic["affected_scope_ids"], ["SCOPE-demo"])
                self.assertEqual(diagnostic["orphan_scope_ids"], [])
                self.assertFalse(diagnostic["global"])

    def test_unresolved_raw_orphans_suppress_scope_and_record_fallback(self):
        for raw_subject in (
            "SCOPE-demo.",
            "SCOPE-demo:evil",
            "SCOPE-demo evil",
        ):
            with (
                self.subTest(raw_subject=raw_subject),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                append_table_row(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Unresolved and Downstream Prohibitions",
                    f"| {raw_subject} | DEC-route;M-evidence | Orphan consequence | Orphan downstream prohibition |",
                )
                model = self.model(self.render(workspace))
                scope = model["design_pack"]["scopes"][0]
                self.assertEqual(scope["dashboard_readiness"], "writer-ready")
                self.assertEqual(scope["mechanical_diagnostic_ids"], [])
                projection = model["design_pack"]["validation_projection"]
                self.assertEqual(projection["global_diagnostic_ids"], [])
                self.assertTrue(projection["orphan_diagnostic_ids"])
                self.assertTrue(
                    any(
                        raw_subject in item["orphan_scope_ids"]
                        for item in projection["diagnostics"]
                    )
                )
                for diagnostic in projection["diagnostics"]:
                    self.assertEqual(diagnostic["affected_scope_ids"], [])

    def test_raw_orphan_identity_is_reused_across_all_projected_04_tables(self):
        raw_subject = "SCOPE-demo."
        cases = (
            (
                "Detailed Surface Coverage",
                f"| template_rule_provenance | {raw_subject} | not_applicable | 0 | none | Orphan coverage mirror |",
            ),
            (
                "Detailed Coverage Summary",
                f"| {raw_subject} | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |",
            ),
            (
                "Owner Gate Resolution Summary",
                f"| {raw_subject} | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
            ),
            (
                "Template Analysis Handling",
                f"| {raw_subject} | not_applicable | none | none | none | design_only | Orphan template handling mirror | none |",
            ),
            (
                "Unresolved and Downstream Prohibitions",
                f"| {raw_subject} | DEC-route;M-evidence | Orphan consequence | Orphan downstream prohibition |",
            ),
            (
                "Scoped Handoff",
                f"| {raw_subject} | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | Orphan prohibition | Orphan handoff note |",
            ),
        )
        for heading, row in cases:
            with (
                self.subTest(heading=heading),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                append_table_row(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    heading,
                    row,
                )
                model = self.model(self.render(workspace))
                scope = model["design_pack"]["scopes"][0]
                self.assertEqual(scope["dashboard_readiness"], "writer-ready")
                self.assertEqual(scope["mechanical_diagnostic_ids"], [])
                projection = model["design_pack"]["validation_projection"]
                self.assertEqual(projection["global_diagnostic_ids"], [])
                self.assertTrue(projection["orphan_diagnostic_ids"])
                self.assertTrue(
                    any(
                        raw_subject in item["orphan_scope_ids"]
                        for item in projection["diagnostics"]
                    )
                )
                for diagnostic in projection["diagnostics"]:
                    self.assertEqual(diagnostic["affected_scope_ids"], [])

    def test_known_orphan_inventory_does_not_scan_ordinary_or_global_prose(self):
        owner_row_cases = (
            (
                "SCOPE-demo. owner-gate summary has invalid blockers",
                "SCOPE-demo.",
            ),
            (
                "SCOPE-demo:evil owner-gate blockers differ from authoritative 00 scope row",
                "SCOPE-demo:evil",
            ),
            (
                "duplicate owner-gate summary key SCOPE-demo evil/DEC-route",
                "SCOPE-demo evil",
            ),
        )
        for payload, expected in owner_row_cases:
            self.assertEqual(
                dashboard_generator.extract_04_row_subject("OWNER_GATE", payload),
                expected,
            )
        self.assertEqual(
            dashboard_generator.extract_04_row_subject(
                "OWNER_GATE",
                "SCOPE-demo summary evil/DEC-route summary differs from authoritative decision",
            ),
            "SCOPE-demo summary evil",
        )
        self.assertEqual(
            dashboard_generator.extract_04_row_subject(
                "OWNER_GATE", "DEC-route lacks valid grounding"
            ),
            None,
        )
        for payload in (
            "SCOPE-demo lacks an Owner Gate Resolution Summary row",
            "SCOPE-demo/DEC-route is absent from the 04 owner-gate summary",
        ):
            self.assertIsNone(
                dashboard_generator.extract_04_row_subject("OWNER_GATE", payload)
            )
        for payload in (
            "SCOPE-demo lacks an Owner Gate Resolution Summary row",
            "SCOPE-demo/DEC-route is absent from the 04 owner-gate summary",
        ):
            self.assertEqual(
                dashboard_generator.extract_owner_gate_declared_scope_subject(
                    payload, {"SCOPE-demo"}
                ),
                "SCOPE-demo",
            )
        self.assertIsNone(
            dashboard_generator.extract_owner_gate_declared_scope_subject(
                "SCOPE-ghost/DEC-route is absent from the 04 owner-gate summary",
                {"SCOPE-demo"},
            )
        )
        self.assertEqual(
            dashboard_generator.extract_04_row_subject(
                "MANIFEST_UNRESOLVED",
                "SCOPE-demo. unresolved IDs differ from authoritative 00 blockers",
            ),
            "SCOPE-demo.",
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            contents, warnings = dashboard_generator.load_workspace(workspace)
            self.assertEqual(warnings, [])
            projection = dashboard_generator.build_validation_projection(
                [
                    "SYNTHETIC_SCOPE: ordinary prose says SCOPE-demo needs attention",
                    "TABLE_CONTRACT: global attention is required",
                ],
                contents,
                {"SCOPE-demo"},
                {"SCOPE-demo.", "attention", "required"},
                {},
            )
            ordinary, global_diagnostic = projection["diagnostics"]
            self.assertEqual(ordinary["affected_scope_ids"], ["SCOPE-demo"])
            self.assertEqual(ordinary["orphan_scope_ids"], [])
            self.assertFalse(ordinary["global"])
            self.assertEqual(global_diagnostic["affected_scope_ids"], [])
            self.assertEqual(global_diagnostic["orphan_scope_ids"], [])
            self.assertTrue(global_diagnostic["global"])

    def test_control_sanitized_scope_subject_cannot_borrow_dec_or_material_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            source = workspace / "04_WRITING_DESIGN_PACK.md"
            append_table_row(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Unresolved and Downstream Prohibitions",
                "| SCOPE-ghost\x00BAD | DEC-route;M-evidence | Ghost consequence | Ghost prohibition |",
            )
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            dashboard = self.render(workspace)
            model = self.model(dashboard)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            self.assert_control_safe(dashboard)
            self.assert_control_safe(model)
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["dashboard_readiness"], "writer-ready")
            self.assertEqual(scope["mechanical_diagnostic_ids"], [])
            projection = model["design_pack"]["validation_projection"]
            self.assertEqual(projection["global_diagnostic_ids"], [])
            self.assertTrue(projection["orphan_diagnostic_ids"])
            for diagnostic in projection["diagnostics"]:
                self.assertEqual(diagnostic["affected_scope_ids"], [])
                self.assertIn("SCOPE-ghost�BAD", diagnostic["orphan_scope_ids"])

    def test_owner_gate_three_way_and_scope_free_record_attribution(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            contents, warnings = dashboard_generator.load_workspace(workspace)
            self.assertEqual(warnings, [])
            projection = dashboard_generator.build_validation_projection(
                [
                    "OWNER_GATE: DEC-route/DEC-route summary differs from authoritative decision",
                    "OWNER_GATE: SCOPE-demo/DEC-route is absent from the 04 owner-gate summary",
                    "OWNER_GATE: DEC-route lacks valid grounding",
                    "SYNTHETIC_RECORD: DEC-route requires attention",
                ],
                contents,
                {"SCOPE-demo"},
                {"DEC-route"},
                {},
            )
            row, declared, record, generic_record = projection["diagnostics"]
            self.assertEqual(row["affected_scope_ids"], [])
            self.assertEqual(row["orphan_scope_ids"], ["DEC-route"])
            self.assertFalse(row["global"])
            for diagnostic in (declared, record, generic_record):
                self.assertEqual(diagnostic["affected_scope_ids"], ["SCOPE-demo"])
                self.assertEqual(diagnostic["orphan_scope_ids"], [])
                self.assertFalse(diagnostic["global"])
            self.assertEqual(
                projection["by_scope"]["SCOPE-demo"],
                ["VDIAG-002", "VDIAG-003", "VDIAG-004"],
            )

    def test_per_scope_04_cardinality_is_local_or_orphan_and_missing_heading_global(
        self,
    ):
        cases = (
            (
                "handling",
                "Template Analysis Handling",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                "| SCOPE-ghost | not_applicable | none | none | none | design_only | Ghost handling mirror | M-evidence |",
            ),
            (
                "handoff",
                "Scoped Handoff",
                "| SCOPE-demo | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | Do not invent science exceed C-demo require template analysis or copy frames as manuscript sentences | Use 03 as the detailed authority and this row only as the compact handoff |",
                "| SCOPE-ghost | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | M-evidence | Ghost prohibition | Ghost handoff |",
            ),
            (
                "unresolved",
                "Unresolved and Downstream Prohibitions",
                "| SCOPE-demo | none | No unresolved record affects this scope | Preserve the claim ceiling frame boundary visual representation role and prohibition on paste-ready fixture prose |",
                "| SCOPE-ghost | DEC-route;M-evidence | Ghost consequence | Ghost prohibition |",
            ),
        )
        for label, heading, demo_row, ghost_row in cases:
            for mutation in ("missing", "duplicate", "orphan", "missing_heading"):
                with (
                    self.subTest(table=label, mutation=mutation),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    workspace = copy_fixture(DETAILED, Path(directory))
                    install_second_ready_scope(workspace)
                    path = workspace / "04_WRITING_DESIGN_PACK.md"
                    if mutation == "missing":
                        text = path.read_text(encoding="utf-8")
                        self.assertIn(demo_row + "\n", text)
                        path.write_text(
                            text.replace(demo_row + "\n", "", 1), encoding="utf-8"
                        )
                    elif mutation == "duplicate":
                        append_table_row(
                            workspace,
                            "04_WRITING_DESIGN_PACK.md",
                            heading,
                            demo_row,
                        )
                    elif mutation == "orphan":
                        append_table_row(
                            workspace,
                            "04_WRITING_DESIGN_PACK.md",
                            heading,
                            ghost_row,
                        )
                    else:
                        replace(
                            workspace,
                            "04_WRITING_DESIGN_PACK.md",
                            f"## {heading}",
                            f"## Missing {heading}",
                        )
                    model = self.model(self.render(workspace))
                    scopes = {
                        item["scope_id"]: item
                        for item in model["design_pack"]["scopes"]
                    }
                    projection = model["design_pack"]["validation_projection"]
                    if mutation in {"missing", "duplicate"}:
                        self.assertEqual(
                            scopes["SCOPE-demo"]["dashboard_readiness"],
                            "mechanically_blocked",
                        )
                        self.assertEqual(
                            scopes["SCOPE-other"]["dashboard_readiness"],
                            "writer-ready",
                        )
                        self.assertTrue(
                            scopes["SCOPE-demo"]["mechanical_diagnostic_ids"]
                        )
                        self.assertEqual(
                            scopes["SCOPE-other"]["mechanical_diagnostic_ids"], []
                        )
                    elif mutation == "orphan":
                        self.assertEqual(
                            scopes["SCOPE-demo"]["dashboard_readiness"], "writer-ready"
                        )
                        self.assertEqual(
                            scopes["SCOPE-other"]["dashboard_readiness"], "writer-ready"
                        )
                        self.assertEqual(projection["global_diagnostic_ids"], [])
                        self.assertTrue(projection["orphan_diagnostic_ids"])
                    else:
                        self.assertTrue(projection["global_diagnostic_ids"])
                        self.assertEqual(
                            scopes["SCOPE-demo"]["dashboard_readiness"],
                            "mechanically_blocked",
                        )
                        self.assertEqual(
                            scopes["SCOPE-other"]["dashboard_readiness"],
                            "mechanically_blocked",
                        )

    def test_wrong_04_gate_and_blocker_remain_invalid_non_authority_mirrors(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| SCOPE-demo | scientific_commitment | DEC-route | unresolved | 00_PROJECT_ROUTE.md#Project Brief | M-fake |",
            )
            model = self.model(self.render(workspace))
            scope = model["design_pack"]["scopes"][0]
            self.assertEqual(scope["blocker_ids"], [])
            self.assertEqual(scope["gates"][0]["Gate category"], "not_applicable")
            self.assertEqual(scope["gates"][0]["Resolution"], "confirmed")
            self.assertEqual(scope["gate_mirrors"][0]["Mirror state"], "invalid_mirror")
            gate_states = {
                item["category"]: item["state"]
                for item in model["design_pack"]["owner_gates"]
            }
            self.assertEqual(gate_states["scientific_commitment"], "not_declared")
            self.assertNotIn("M-fake", scope["blocker_ids"])
            self.assertTrue(
                any("invalid_mirror" in item["message"] for item in model["warnings"])
            )

    def test_local_mechanical_failures_block_only_the_affected_scope(self):
        mutations = ("count", "pointer", "stale", "owner_gate")
        for mutation in mutations:
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                install_second_ready_scope(workspace)
                if mutation == "count":
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 0 | 0 |",
                        "| SCOPE-demo | 1 | 9 | 1 | 2 | 1 | 1 | 2 | 0 | 0 |",
                    )
                elif mutation == "pointer":
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| section_paragraph_map | SCOPE-demo | satisfied | 5 | 03_WRITING_STRUCTURE.md#Section Map |",
                        "| section_paragraph_map | SCOPE-demo | satisfied | 5 | 03_WRITING_STRUCTURE.md#Missing Surface |",
                    )
                elif mutation == "stale":
                    semantic_pointer = install_semantic_rule(workspace)
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| template_rule_provenance | SCOPE-demo | not_applicable | 0 | none | Template design is irrelevant to this synthetic route-neutral contract fixture |",
                        "| template_rule_provenance | SCOPE-demo | satisfied | 1 | 03_WRITING_STRUCTURE.md#Template Rule Projection | Active design-only rule projections are declared |",
                    )
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 0 | 0 |",
                        "| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 0 |",
                    )
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                        f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | none | design_only | Semantic reading answers the declared method-order question | none |",
                    )
                    dossier_path = (
                        workspace
                        / ".yxj-paper-os"
                        / "template-analysis"
                        / "semantic-dossier.json"
                    )
                    dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
                    dossier["documents"][0]["freshness"] = "stale"
                    dossier["transfer_rules"][0]["source_freshness"] = "stale"
                    dossier_path.write_text(json.dumps(dossier), encoding="utf-8")
                    replace(
                        workspace,
                        "03_WRITING_STRUCTURE.md",
                        "| verified_local_current |",
                        "| stale |",
                    )
                else:
                    append_table_row(
                        workspace,
                        "00_PROJECT_ROUTE.md",
                        "Decision Records",
                        "| DEC-local | argument_spine | Select the local spine | SCOPE-demo | owner-confirmed | unresolved | 00_PROJECT_ROUTE.md#Project Brief | Owner answer changes |",
                    )
                    append_table_row(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "Owner Gate Resolution Summary",
                        "| SCOPE-demo | argument_spine | DEC-local | unresolved | 00_PROJECT_ROUTE.md#Project Brief | none |",
                    )
                scopes = {
                    item["scope_id"]: item
                    for item in self.model(self.render(workspace))["design_pack"][
                        "scopes"
                    ]
                }
                self.assertEqual(
                    scopes["SCOPE-demo"]["dashboard_readiness"],
                    "mechanically_blocked",
                )
                self.assertTrue(scopes["SCOPE-demo"]["mechanical_diagnostic_ids"])
                self.assertEqual(scopes["SCOPE-demo"]["blocker_ids"], [])
                self.assertEqual(
                    scopes["SCOPE-other"]["dashboard_readiness"], "writer-ready"
                )
                self.assertEqual(scopes["SCOPE-other"]["mechanical_diagnostic_ids"], [])

    def test_global_contract_failure_blocks_all_declared_scopes(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            install_second_ready_scope(workspace)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "## Decision Records",
                "## Missing Decision Records",
            )
            model = self.model(self.render(workspace))
            projection = model["design_pack"]["validation_projection"]
            self.assertTrue(projection["global_diagnostic_ids"])
            for scope in model["design_pack"]["scopes"]:
                self.assertEqual(scope["dashboard_readiness"], "mechanically_blocked")
                self.assertTrue(
                    set(projection["global_diagnostic_ids"]).issubset(
                        scope["mechanical_diagnostic_ids"]
                    )
                )

    def test_four_owner_gates_render_resolved_and_active_states(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable | Use the synthetic generic route for contract characterization | SCOPE-demo | artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief | Route or scope changes |",
                "| DEC-route | scientific_commitment | Use the synthetic generic route for contract characterization | SCOPE-demo | owner-confirmed | confirmed | 00_PROJECT_ROUTE.md#Project Brief | Route or scope changes |",
            )
            for row in (
                "| DEC-spine | argument_spine | Select the bounded argument spine | SCOPE-demo | owner-confirmed | unresolved | 00_PROJECT_ROUTE.md#Project Brief | New evidence |",
                "| DEC-tradeoff | material_local_tradeoff | Reject the alternate local tradeoff | SCOPE-demo | owner-confirmed | rejected | 00_PROJECT_ROUTE.md#Project Brief | New material |",
                "| DEC-divergence | deliberate_divergence | Confirm explicit divergence | SCOPE-demo | owner-confirmed | confirmed | 00_PROJECT_ROUTE.md#Project Brief | Template changes |",
            ):
                append_table_row(
                    workspace,
                    "00_PROJECT_ROUTE.md",
                    "Decision Records",
                    row,
                )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| SCOPE-demo | scientific_commitment | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
            )
            for row in (
                "| SCOPE-demo | argument_spine | DEC-spine | unresolved | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| SCOPE-demo | material_local_tradeoff | DEC-tradeoff | rejected | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| SCOPE-demo | deliberate_divergence | DEC-divergence | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
            ):
                append_table_row(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Owner Gate Resolution Summary",
                    row,
                )
            gates = {
                item["category"]: item["state"]
                for item in self.model(self.render(workspace))["design_pack"][
                    "owner_gates"
                ]
            }
            self.assertEqual(gates["argument_spine"], "active")
            self.assertEqual(gates["scientific_commitment"], "resolved")
            self.assertEqual(gates["material_local_tradeoff"], "resolved")
            self.assertEqual(gates["deliberate_divergence"], "resolved")

    def test_dashboard_escapes_injected_public_and_hidden_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            marker = '<script>alert("dashboard")</script>'
            replace(
                workspace,
                "00_DIMENSION_INDEX.md",
                "Synthetic two-paragraph method surface",
                marker,
            )
            install_semantic_rule(workspace)
            dossier_path = (
                workspace
                / ".yxj-paper-os"
                / "template-analysis"
                / "semantic-dossier.json"
            )
            payload = json.loads(dossier_path.read_text(encoding="utf-8"))
            payload["documents"][0]["acquisition_provenance"] = marker
            dossier_path.write_text(json.dumps(payload), encoding="utf-8")
            dashboard = self.render(workspace)
            self.assertNotIn(marker, dashboard)
            self.assertIn("&lt;script&gt;alert", dashboard)
            self.assertIn("\\u003cscript", dashboard)

    def test_dashboard_is_deterministic_and_changes_only_requested_output(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            install_semantic_rule(workspace)

            def hashes() -> dict[str, str]:
                return {
                    str(path.relative_to(workspace)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                    and path != workspace / ".yxj-paper-os" / "dashboard.html"
                }

            before = hashes()
            first = self.render(workspace)
            middle = hashes()
            second = self.render(workspace)
            after = hashes()
            self.assertEqual(before, middle)
            self.assertEqual(middle, after)
            self.assertEqual(
                hashlib.sha256(first.encode()).hexdigest(),
                hashlib.sha256(second.encode()).hexdigest(),
            )
            source = GEN.read_text(encoding="utf-8")
            for forbidden in ("urllib", "requests", "socket", "http.client"):
                self.assertNotIn(forbidden, source)
            self.assertNotRegex(first, r'(?i)(?:src|href)=["\']https?://')

    def test_analyzer_nonfinite_numbers_and_unsafe_json_text_degrade_totally(self):
        for token in ("1e9999", "NaN", "Infinity"):
            with (
                self.subTest(token=token),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                analysis = self.install_analyzer(workspace)
                summary_path = analysis / "corpus-summary.json"
                payload = summary_path.read_text(encoding="utf-8")
                self.assertIn('"median": 5100', payload)
                summary_path.write_text(
                    payload.replace('"median": 5100', f'"median": {token}', 1),
                    encoding="utf-8",
                )
                dashboard = self.render(workspace)
                model = self.model(dashboard)
                self.assertEqual(model["template_analysis"]["state"], "degraded")
                self.assertEqual(
                    model["template_analysis"]["artifacts"]["summary"]["state"],
                    "malformed",
                )
                self.assertFalse(
                    any(0xD800 <= ord(character) <= 0xDFFF for character in dashboard)
                )

        for label, unsafe in (("nul", "\x00"), ("surrogate", "\ud800")):
            with (
                self.subTest(label=label),
                tempfile.TemporaryDirectory() as directory,
            ):
                workspace = copy_fixture(DETAILED, Path(directory))
                analysis = self.install_analyzer(workspace)
                summary_path = analysis / "corpus-summary.json"
                payload = json.loads(summary_path.read_text(encoding="utf-8"))
                payload["safety_probe"] = unsafe
                summary_path.write_text(json.dumps(payload), encoding="utf-8")
                dashboard = self.render(workspace)
                model = self.model(dashboard)
                self.assertEqual(model["template_analysis"]["state"], "degraded")
                self.assertEqual(
                    model["template_analysis"]["artifacts"]["summary"]["state"],
                    "malformed",
                )
                self.assertNotIn("\x00", dashboard)
                self.assertFalse(
                    any(0xD800 <= ord(character) <= 0xDFFF for character in dashboard)
                )

    def test_public_control_characters_are_sanitized_in_memory_without_writeback(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            source = workspace / "00_DIMENSION_INDEX.md"
            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    "Synthetic two-paragraph method surface",
                    "Synthetic\x00two-paragraph method surface",
                    1,
                ),
                encoding="utf-8",
            )
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            dashboard = self.render(workspace)
            self.model(dashboard)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            self.assertIn("Synthetic�two-paragraph", dashboard)
            self.assertNotIn("\x00", dashboard)
            self.assertFalse(
                any(0xD800 <= ord(character) <= 0xDFFF for character in dashboard)
            )
            self.assertTrue(
                any(
                    "sanitized" in item["message"]
                    for item in self.model(dashboard)["warnings"]
                )
            )

    def test_validator_diagnostic_control_reentry_is_sanitized_without_writeback(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            source = workspace / "00_DIMENSION_INDEX.md"
            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    "SCOPE-demo", "SCOPE-demo\x00BAD", 1
                ),
                encoding="utf-8",
            )
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            dashboard = self.render(workspace)
            model = self.model(dashboard)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            self.assertNotIn(b"\x00", dashboard.encode("utf-8"))
            self.assert_control_safe(dashboard)
            self.assert_control_safe(model)
            self.assertTrue(
                any(
                    "writer-ready SCOPE-demo�BAD has no section" in item
                    for item in model["validation"]["errors"]
                )
            )
            self.assertTrue(
                any(
                    item["scope"] == "validator" and "sanitized" in item["message"]
                    for item in model["warnings"]
                )
            )

    def test_validator_warnings_and_defensive_exceptions_are_sanitized_at_ingress(self):
        report = mock.Mock(
            errors=["VALIDATOR_ERROR: bad\x00scope"],
            warnings=["VALIDATOR_WARNING: bad\ud800text"],
        )
        warnings: list[dict[str, str]] = []
        with mock.patch.object(
            dashboard_generator, "validate_workspace_report", return_value=report
        ):
            validation = dashboard_generator.add_validator_warnings(
                Path("unused"), warnings
            )
        self.assert_control_safe(validation)
        self.assert_control_safe(warnings)
        self.assertIn("bad�scope", validation["errors"][0])
        self.assertIn("bad�text", validation["warnings"][0])

        warnings = []
        with mock.patch.object(
            dashboard_generator,
            "validate_workspace_report",
            side_effect=RuntimeError("defensive\x00failure\ud800"),
        ):
            validation = dashboard_generator.add_validator_warnings(
                Path("unused"), warnings
            )
        self.assert_control_safe(validation)
        self.assert_control_safe(warnings)
        self.assertIn("defensive�failure�", validation["errors"][0])

    def test_bounded_huge_integer_remains_total_and_strictly_serializable(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            analysis = self.install_analyzer(workspace)
            summary_path = analysis / "corpus-summary.json"
            payload = summary_path.read_text(encoding="utf-8")
            huge_integer = "1" + "0" * 4000
            summary_path.write_text(
                payload.replace('"median": 5100', f'"median": {huge_integer}', 1),
                encoding="utf-8",
            )
            model = self.model(self.render(workspace))
            self.assertEqual(model["template_analysis"]["state"], "current")
            self.assertEqual(
                model["template_analysis"]["metric_summaries"][0]["median"],
                int(huge_integer),
            )

    def test_json_serialization_rejects_nonfinite_runtime_values(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                dashboard_generator.safe_json({"unsafe": value})

    def test_atomic_write_preserves_old_output_and_cleans_temps_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            cache = workspace / ".yxj-paper-os"
            cache.mkdir()
            target = cache / "dashboard.html"
            target.write_text("OLD-DASHBOARD", encoding="utf-8")
            with (
                mock.patch.object(
                    dashboard_generator.os,
                    "replace",
                    side_effect=OSError("injected replace failure"),
                ),
                self.assertRaises(RuntimeError),
            ):
                dashboard_generator.write_dashboard(workspace, "NEW-DASHBOARD")
            self.assertEqual(target.read_text(encoding="utf-8"), "OLD-DASHBOARD")
            self.assertEqual(list(cache.glob(".dashboard.html.*.tmp")), [])

            with self.assertRaises(RuntimeError):
                dashboard_generator.write_dashboard(workspace, "\ud800")
            self.assertEqual(target.read_text(encoding="utf-8"), "OLD-DASHBOARD")
            self.assertEqual(list(cache.glob(".dashboard.html.*.tmp")), [])

    def test_output_symlink_is_rejected_without_touching_target(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = copy_fixture(DETAILED, Path(directory))
            cache = workspace / ".yxj-paper-os"
            cache.mkdir()
            outside = Path(directory) / "outside.html"
            outside.write_text("OUTSIDE-OLD", encoding="utf-8")
            (cache / "dashboard.html").symlink_to(outside)
            with self.assertRaises(RuntimeError):
                dashboard_generator.write_dashboard(workspace, "ATTACK")
            self.assertEqual(outside.read_text(encoding="utf-8"), "OUTSIDE-OLD")
            self.assertEqual(list(cache.glob(".dashboard.html.*.tmp")), [])

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
