#!/usr/bin/env python3
"""Regression tests for the yxj-paper-os static dashboard generator.

The generator is required: tests fail normally if ``generate_dashboard.py`` is
missing, and exercise its public CLI against temporary six-file workspaces.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast

sys.dont_write_bytecode = True

# Keep bytecode disabled before importing the colocated validator helpers.
from verify_design_pack import validate_workspace  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parents[2]
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"
GENERATOR = SCRIPT_DIR / "generate_dashboard.py"
VALIDATOR = SCRIPT_DIR / "verify_design_pack.py"

REQUIRED_FILES = [
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
]

DIMENSION_NAMES = [
    "00_META.md",
    "OWNER_DECISIONS.md",
    "STALE_FLAGS.md",
    "00_project_brief.md",
    "01_target_journal_profile.md",
    "02_material_inventory.md",
    "03_evidence_inventory.md",
    "04_source_and_citation_bank.md",
    "10_research_dossier.md",
    "11_exemplar_language_profile.md",
    "12_contribution_options.md",
    "13_claim_evidence_map.md",
    "14_wording_boundary.md",
    "15_limitation_and_risk_matrix.md",
    "20_reader_spine.md",
    "21_manuscript_outline.md",
    "22_object_granularity.md",
    "23_surface_control.md",
    "24_visual_plan.md",
    "25_WRITING_DESIGN_PACK.md",
]

DIMENSION_POINTERS = [
    "00_DIMENSION_INDEX.md#Workspace Metadata",
    "00_PROJECT_ROUTE.md#Owner Decisions",
    "04_WRITING_DESIGN_PACK.md#D02 Stale Gate",
    "00_PROJECT_ROUTE.md#Project Brief",
    "00_PROJECT_ROUTE.md#Target Route",
    "01_MATERIALS_INVENTORY.md#Results and Experiments",
    "01_MATERIALS_INVENTORY.md#Evidence Inventory",
    "01_MATERIALS_INVENTORY.md#Source and Citation Bank",
    "01_MATERIALS_INVENTORY.md#Research Dossier",
    "03_WRITING_STRUCTURE.md#Exemplar Language Profile",
    "02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options",
    "02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map",
    "02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording",
    "02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks",
    "03_WRITING_STRUCTURE.md#Reader Spine",
    "03_WRITING_STRUCTURE.md#Manuscript Outline",
    "03_WRITING_STRUCTURE.md#Object Granularity",
    "03_WRITING_STRUCTURE.md#Surface Control",
    "03_WRITING_STRUCTURE.md#Visual Plan",
    "04_WRITING_DESIGN_PACK.md#Submission Blueprint",
]

SPECIAL_SENTINEL = 'SPECIAL_ESCAPING_SENTINEL <script>alert("x")</script> 中文 **raw markdown** `code` & chars'


class DashboardGeneratorTests(unittest.TestCase):
    maxDiff = None

    def run_python(self, args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Run Python with bytecode caches redirected outside the repository."""
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-pycache-") as cache_dir:
            env = os.environ.copy()
            env["PYTHONPYCACHEPREFIX"] = cache_dir
            return subprocess.run(
                [sys.executable, *args],
                cwd=str(cwd or REPO_ROOT),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

    def run_generator(self, workspace: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return self.run_python([str(GENERATOR), str(workspace), *extra_args])

    def make_template_workspace(self, parent: Path) -> Path:
        workspace = parent / "paper-workspace"
        workspace.mkdir()
        for file_name in REQUIRED_FILES:
            source = TEMPLATE_DIR / file_name
            self.assertTrue(source.is_file(), f"missing template fixture: {source}")
            shutil.copy2(source, workspace / file_name)
        return workspace

    def make_filled_workspace(self, parent: Path) -> Path:
        workspace = self.make_template_workspace(parent)
        self.write_filled_workspace(workspace)
        return workspace

    def write_filled_workspace(self, workspace: Path) -> None:
        index_rows = []
        coverage_rows = []
        for number, (dimension, pointer) in enumerate(zip(DIMENSION_NAMES, DIMENSION_POINTERS)):
            dim_id = f"D{number:02d}"
            block = "no" if dim_id in {"D08", "D09"} else "yes"
            note = f"Owner-filled structural note for {dim_id}; {SPECIAL_SENTINEL}"
            index_rows.append(
                f"| {dim_id} | {dimension} | {pointer.split('#', 1)[0]} | filled | {note} | {pointer} | {block} |"
            )
            coverage_rows.append(f"| {dim_id} | filled | {pointer} | {block} |")

        (workspace / "00_DIMENSION_INDEX.md").write_text(
            "\n".join(
                [
                    "# 00 Dimension Index",
                    "",
                    "## Workspace Metadata",
                    "",
                    "- Project slug: dashboard-regression-fixture",
                    "- Last updated: 2026-07-06",
                    "- Design-pack readiness: structural handoff only, not semantic readiness.",
                    "",
                    "## Dimension Status Index",
                    "",
                    "| ID | Dimension | Current home | Status | Reason / owner note | Pointer or handoff | Blocks design pack? |",
                    "|---|---|---|---|---|---|---|",
                    *index_rows,
                    "",
                    "## Readiness Gate",
                    "",
                    "- All D00-D19 handled: yes, structurally filled for dashboard tests.",
                    "- Remaining blocking dimensions: none recorded for this fixture.",
                    "- Final design pack can be compiled: yes, as a structural handoff only.",
                    "",
                    "## Owner Notes",
                    "",
                    f"Dashboard fixture owner note with escaping payload: {SPECIAL_SENTINEL}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        (workspace / "00_PROJECT_ROUTE.md").write_text(
            "\n".join(
                [
                    "# 00 Project Route",
                    "",
                    "## Project Brief",
                    "",
                    "- Project / paper slug: dashboard-regression-fixture",
                    "- Research topic: offline dashboard generation for yxj paper planning.",
                    "- Traffic / computer-science / AI positioning: structural tooling test fixture.",
                    "- Working thesis: the dashboard mirrors files without semantic scoring.",
                    "",
                    "## Target Route",
                    "",
                    "| Route/profile prompt | Planning note or explicit defer/absence | Owner state / downstream constraint |",
                    "|---|---|---|",
                    "| Venue family / target route | Journal-style software paper route | Owner supplied route family |",
                    "| Article or paper type | Technical report fixture | Keep wording bounded |",
                    "| Content / format / reporting fit intent | Offline static dashboard | No semantic score |",
                    "| Primary audience | Maintainers and reviewers | Structural audit only |",
                    "| Reviewer expectation | Traceability from D00-D19 | Candidate expectation |",
                    "| Hard constraints and forbidden routes | No external network, no template copy | Constrains D19 |",
                    "",
                    "## Topic and Positioning",
                    "",
                    "The fixture records a dashboard-generator task, including 中文 and raw Markdown markers.",
                    "",
                    "## Audience and Reviewer Expectation",
                    "",
                    "Reviewers need visible D00-D19 traceability and warnings for degraded source structure.",
                    "",
                    "## Owner Decisions",
                    "",
                    "- Required route constraints: read-only six-file source, hidden dashboard cache output.",
                    "- Owner-gated decisions: no external skill execution and no semantic scoring.",
                    "",
                    "## Forbidden Routes",
                    "",
                    "Do not copy missing Markdown templates or write outside .yxj-paper-os.",
                    "",
                    "## Route Readiness",
                    "",
                    "Status: structurally filled.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        (workspace / "01_MATERIALS_INVENTORY.md").write_text(
            "\n".join(
                [
                    "# 01 Materials Inventory",
                    "",
                    "## Results and Experiments",
                    "",
                    "The only result is a deterministic local dashboard smoke test.",
                    "",
                    "## Figures and Tables",
                    "",
                    "FIG1 is an existing static dashboard screenshot placeholder owned by downstream manual QA.",
                    "",
                    "## Data Sources",
                    "",
                    "Source data are the six Markdown planning files in this temporary workspace.",
                    "",
                    "## Code / Implementation",
                    "",
                    "Implementation under test is generate_dashboard.py invoked through its public CLI.",
                    "",
                    "## Baselines",
                    "",
                    "Baseline is source immutability plus exact hidden output path.",
                    "",
                    "## Metrics",
                    "",
                    "Metrics are structural warnings, D00-D19 coverage, and write-boundary conformance.",
                    "",
                    "## Evidence Inventory",
                    "",
                    "| Evidence anchor | Type | Location | Supports claim/dimension | Status |",
                    "|---|---|---|---|---|",
                    "| E1 | file-hash snapshot | temporary workspace | D00-D19 dashboard traceability | available |",
                    "| FIG1 | visual plan | 03_WRITING_STRUCTURE.md#Visual Plan | D18 only | available |",
                    "",
                    "## Source and Citation Bank",
                    "",
                    "| Source/citation prompt | Supplied detail or explicit absence/defer note | Boundary or handoff |",
                    "|---|---|---|",
                    "| Source identity and locator/version | local test fixture | Do not invent external citations |",
                    "| Source role and citation status | implementation fixture | Context only |",
                    "| Owner confirmation and reuse permission | owned by regression tests | Internal reuse permitted |",
                    "| Key use and limitation | checks write boundary | Not evidence of semantic quality |",
                    "| Downstream citation handoff need | absent | No citation task |",
                    "",
                    "## Research Dossier",
                    "",
                    "| Dossier / synthesis-gap prompt | Supplied note or explicit absence/defer note | Downstream consequence or risk |",
                    "|---|---|---|",
                    "| Research/context boundary | local fixture only | no literature claim |",
                    "| Study-level notes or theme synthesis | absent by design | no novelty judgment |",
                    "| Conflict map or counterevidence | none supplied | no semantic inference |",
                    "| Gap hypothesis | absent | candidate only |",
                    "| Unresolved source needs | absent | no source handoff |",
                    "",
                    "## Existing Text Fragments",
                    "",
                    f"Escaping fragment: {SPECIAL_SENTINEL}",
                    "",
                    "## Explicit Absences",
                    "",
                    "No browser, LLM, network, or subprocess-driven source mutation is part of the dashboard.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        (workspace / "02_CLAIM_EVIDENCE_BOUNDARY.md").write_text(
            "\n".join(
                [
                    "# 02 Claim Evidence Boundary",
                    "",
                    "## Problem / Object / Contribution",
                    "",
                    "- Problem: dashboards can accidentally mutate source or hide malformed rows.",
                    "- Object: the yxj-paper-os dashboard generator.",
                    "- One-sentence contribution: a local static dashboard mirrors structural state only.",
                    "",
                    "## Contribution Options",
                    "",
                    "| Option | Decision | Reason | Evidence / material dependency |",
                    "|---|---|---|---|",
                    "| Static dashboard | accepted | supports read-only review | E1 |",
                    "",
                    "## Object Granularity",
                    "",
                    "Generator output, warning model, and write boundary are separate objects.",
                    "",
                    "## Claim-Evidence Map",
                    "",
                    "| Claim | Evidence anchors | Support strength | Forbidden wording | Status |",
                    "|---|---|---|---|---|",
                    "| The generator preserves Markdown bytes in this fixture | E1 | structural | proves semantic readiness | active |",
                    "",
                    "## Claim Support Boundary Reminder",
                    "",
                    "D07, D08, D09, and D18 cannot strengthen active claims without E1-style evidence anchors.",
                    "",
                    "## Allowed Wording",
                    "",
                    "Use structural, read-only, warning, and handoff wording only.",
                    "",
                    "## Forbidden Wording",
                    "",
                    "Do not claim manuscript quality, publication readiness, or semantic adequacy.",
                    "",
                    "## Deferred or Rejected Claims",
                    "",
                    "Browser rendering quality is deferred to manual smoke testing.",
                    "",
                    "## Limitations and Risks",
                    "",
                    "Malformed Markdown must degrade with warnings rather than disappearing silently.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        (workspace / "03_WRITING_STRUCTURE.md").write_text(
            "\n".join(
                [
                    "# 03 Writing Structure",
                    "",
                    "## Exemplar Language Profile",
                    "",
                    "| Style fingerprint prompt | Status/rationale or supplied detail | Boundary / link |",
                    "|---|---|---|",
                    "| Exemplar status and role | absent for fixture | do not invent exemplars |",
                    "| Positive style rules | concise structural labels | link to D17 |",
                    "| Forbidden imitation or banned patterns | no source prose copying | style only |",
                    "| Voice / tense / hedge strength / terminology density | neutral dashboard copy | link to D12 |",
                    "",
                    "## Reader Spine",
                    "",
                    "| Reader step | Reader persona / question | Expected answer | Linked claim / evidence / limitation | Transition rationale or forbidden question |",
                    "|---|---|---|---|---|",
                    "| 1 | Maintainer asks what changed | Only hidden dashboard file changed | E1 | no semantic scoring |",
                    "",
                    "## Manuscript Outline",
                    "",
                    "| Sequence | Section or unit | Planning purpose | Route/type constraint |",
                    "|---|---|---|---|",
                    "| 1 | Dashboard overview | inspect D00-D19 | static local output |",
                    "",
                    "## Section Jobs",
                    "",
                    "| Section | Job | Input dimensions | Output promise | Required evidence / visual | Forbidden content or downstream constraint |",
                    "|---|---|---|---|---|---|",
                    "| Dashboard | Show structural details | D00-D19 | clickable detail model | E1 | no external fetch |",
                    "",
                    "## Object Granularity",
                    "",
                    "Rows, warnings, source excerpts, and output path guard are distinct dashboard concepts.",
                    "",
                    "## Surface Control",
                    "",
                    "Copy should say structural/read-only and avoid semantic scoring language.",
                    "",
                    "## Figure / Table Storyline",
                    "",
                    "| Story step | Visual/table id | Story role | Linked reader step / claim | Evidence boundary |",
                    "|---|---|---|---|---|",
                    "| 1 | FIG1 | dashboard visual handoff | Step 1 | existing structural fixture |",
                    "",
                    "## Visual Plan",
                    "",
                    "| Visual id | Type and status | Data/evidence needed | Panel / legend / accessibility prompt | Handoff |",
                    "|---|---|---|---|---|",
                    "| FIG1 | static existing dashboard screenshot | E1 | accessible labels for D00-D19 | manual QA |",
                    "",
                    "## Paragraph / Function Map",
                    "",
                    "Dashboard text maps every Dxx row to a detail card and warning context.",
                    "",
                    "## Drafting Constraints",
                    "",
                    "Keep output offline, self-contained, and transparent about warnings.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        (workspace / "04_WRITING_DESIGN_PACK.md").write_text(
            "\n".join(
                [
                    "# 04 Writing Design Pack",
                    "",
                    "## Dimension Coverage Summary",
                    "",
                    "| ID | Status | Pointer or handoff | Blocks design pack? |",
                    "|---|---|---|---|",
                    *coverage_rows,
                    "",
                    "## Project Route",
                    "",
                    "Structural local dashboard route for yxj-paper-os planning workspaces.",
                    "",
                    "## Submission Blueprint",
                    "",
                    "| Blueprint prompt | Planned note or handoff | Risk or constraint |",
                    "|---|---|---|",
                    "| Route/profile and paper type from D04 | static dashboard handoff | not publication readiness |",
                    "| Required statements or reporting constraints | report warnings visibly | structural only |",
                    "| Supplement / appendix boundary | not applicable | no extra files |",
                    "| External downstream route | absent | do not execute skills |",
                    "",
                    "## Material Boundary",
                    "",
                    "The material boundary is the six Markdown files and no generated Markdown copies.",
                    "",
                    "## Source / Citation Boundary",
                    "",
                    "No source truth or citation validation is performed by the dashboard.",
                    "",
                    "## Research Dossier Notes",
                    "",
                    "Research dossier content is absent for this local generator fixture.",
                    "",
                    "## Semantic-Risk and Unresolved-Risk Notes",
                    "",
                    "| Risk area | Unresolved dimension/source | Consequence or handoff |",
                    "|---|---|---|",
                    "| Source/citation boundary | none supplied | no semantic claim |",
                    "| Claim/evidence boundary | fixture only | structural smoke test |",
                    "| Visual/storyline boundary | manual visual QA | not automated here |",
                    "| Stale or deferred upstream content | none recorded | no recompile risk |",
                    "",
                    "## Core Contribution",
                    "",
                    "A self-contained HTML dashboard can expose structural warnings without editing source.",
                    "",
                    "## Statement Inventory",
                    "",
                    "| Statement / constraint type | Source dimension | Handoff note |",
                    "|---|---|---|",
                    "| Route or formatting statement | D04 | structural dashboard route |",
                    "| Claim wording statement | D11/D12 | read-only wording |",
                    "| Limitation or risk statement | D13 | warning degradation |",
                    "| Visual or supplement statement | D18/D19 | manual visual QA |",
                    "",
                    "## Claim-Evidence Map",
                    "",
                    "| Claim | Evidence anchors | Support strength | Allowed wording | Forbidden wording | Status |",
                    "|---|---|---|---|---|---|",
                    "| The dashboard writes only its hidden HTML output | E1 | structural | source files unchanged | semantic readiness | active |",
                    "",
                    "## Allowed Wording",
                    "",
                    "Read-only structural handoff, local warning center, and D00-D19 detail wording are allowed.",
                    "",
                    "## Forbidden Wording",
                    "",
                    "Publication readiness, semantic quality, and citation authority wording are forbidden.",
                    "",
                    "## Limitations and Risks",
                    "",
                    "Malformed Markdown may reduce display fidelity but must remain visible through warnings.",
                    "",
                    "## Reader Spine",
                    "",
                    "Readers inspect route, material, claim, writing, visual, and D19 handoff structure.",
                    "",
                    "## Writing Structure",
                    "",
                    "The dashboard supports cards, warning center, and clickable dimension detail panes.",
                    "",
                    "## Visual and Figure Storyline",
                    "",
                    "FIG1 remains a manual visual QA handoff, not evidence for active claims.",
                    "",
                    "## D02 Stale Gate",
                    "",
                    "| Changed dimension | Affected pack section | Stale since | Recompile required? | Owner decision / required action | Semantic-risk note |",
                    "|---|---|---|---|---|---|",
                    "| none | none | not applicable | no | owner accepted current fixture | no stale risk |",
                    "",
                    "## External Skill Handoff",
                    "",
                    "No external skill handoff is executed by this dashboard fixture.",
                    "",
                    "## Validation Notes",
                    "",
                    "Validation is structural against the six-file and 20-dimension contract only.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def markdown_hashes(self, workspace: Path) -> dict[str, str]:
        return {
            file_name: hashlib.sha256((workspace / file_name).read_bytes()).hexdigest()
            for file_name in REQUIRED_FILES
            if (workspace / file_name).exists()
        }

    def relative_files(self, workspace: Path) -> set[str]:
        return {path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()}

    def assert_successful_dashboard(self, result: subprocess.CompletedProcess[str], workspace: Path) -> str:
        combined = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, combined)
        dashboard = workspace / ".yxj-paper-os" / "dashboard.html"
        self.assertTrue(dashboard.is_file(), f"dashboard not generated; output was:\n{combined}")
        return dashboard.read_text(encoding="utf-8")

    def assert_no_external_refs(self, html: str) -> None:
        self.assertNotRegex(html, r"(?is)<script\s+[^>]*\bsrc\s*=", "dashboard must not load external scripts")
        self.assertNotRegex(html, r"(?is)\bhref\s*=\s*['\"]?https?://", "dashboard must not link HTTP(S) assets")
        self.assertNotRegex(html, r"(?is)\bsrc\s*=\s*['\"]?https?://", "dashboard must not load HTTP(S) assets")

    def dashboard_model(self, html: str) -> dict[str, Any]:
        match = re.search(r'<script id="dashboard-data" type="application/json">(.*?)</script>', html, re.DOTALL)
        assert match is not None, "dashboard model JSON script tag missing"
        return cast(dict[str, Any], json.loads(match.group(1)))

    def replace_section_body(self, workspace: Path, file_name: str, heading: str, body: str) -> None:
        path = workspace / file_name
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(rf"(^##\s+{re.escape(heading)}\s*$\n)(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
        self.assertRegex(text, pattern, f"missing section ## {heading} in {file_name}")

        def replacement(match: re.Match[str]) -> str:
            return f"{match.group(1)}\n{body.strip()}\n\n"

        path.write_text(pattern.sub(replacement, text, count=1), encoding="utf-8")

    def test_existing_validator_still_py_compiles(self) -> None:
        result = self.run_python(["-m", "py_compile", str(VALIDATOR)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_static_source_guard_for_offline_generator(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8").lower()
        forbidden = [
            "subprocess",
            "socket",
            "urllib",
            "requests",
            "http://",
            "https://",
            "cdn.jsdelivr",
            "unpkg",
            "cdnjs",
            "--output",
            "http.client",
            "openai",
            "anthropic",
            "browser",
            "selenium",
            "playwright",
        ]
        for token in forbidden:
            self.assertNotIn(token, source, f"generator must stay local/static; forbidden token: {token}")

    def test_public_cli_has_no_output_override_and_rejects_outside_path(self) -> None:
        help_result = self.run_python([str(GENERATOR), "--help"])
        help_text = help_result.stdout + help_result.stderr
        self.assertEqual(help_result.returncode, 0, help_text)
        self.assertNotIn("--output", help_text, "public CLI must not advertise an output-path override")

        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-cli-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            outside = Path(tmp) / "outside-dashboard.html"
            result = self.run_python([str(GENERATOR), str(workspace), "--output", str(outside)])
            self.assertNotEqual(result.returncode, 0, "public --output override must be absent or rejected")
            self.assertFalse(outside.exists(), "generator must not write an arbitrary outside output path")

    def test_template_workspace_smoke_preserves_source_and_writes_only_dashboard(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-template-") as tmp:
            workspace = self.make_template_workspace(Path(tmp))
            before_hashes = self.markdown_hashes(workspace)
            before_files = self.relative_files(workspace)

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)

            self.assertEqual(before_hashes, self.markdown_hashes(workspace), "source Markdown bytes changed")
            self.assertEqual(before_files | {".yxj-paper-os/dashboard.html"}, self.relative_files(workspace))
            self.assertTrue((workspace / ".yxj-paper-os").is_dir())
            self.assertIn("00_DIMENSION_INDEX.md", html)
            self.assertRegex((result.stdout + result.stderr + html).lower(), r"warning|placeholder|todo")

    def test_write_boundary_no_template_copy_and_no_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-boundary-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            before_hashes = self.markdown_hashes(workspace)
            before_files = self.relative_files(workspace)

            result = self.run_generator(workspace)
            self.assert_successful_dashboard(result, workspace)

            self.assertEqual(before_hashes, self.markdown_hashes(workspace), "source Markdown hashes changed")
            new_files = self.relative_files(workspace) - before_files
            self.assertEqual({".yxj-paper-os/dashboard.html"}, new_files)
            cache_contents = sorted(path.relative_to(workspace).as_posix() for path in (workspace / ".yxj-paper-os").rglob("*"))
            self.assertEqual([".yxj-paper-os/dashboard.html"], cache_contents)
            self.assertEqual(set(REQUIRED_FILES), {p.name for p in workspace.glob("*.md")})

    def test_write_dashboard_rejects_symlink_cache_dir_without_outside_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-cache-symlink-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            outside = Path(tmp) / "outside-cache"
            outside.mkdir()
            (workspace / ".yxj-paper-os").symlink_to(outside, target_is_directory=True)

            result = self.run_generator(workspace)
            combined = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("symlink", combined.lower())
            self.assertFalse((outside / "dashboard.html").exists(), "symlink cache dir must not receive dashboard output")

    def test_write_dashboard_rejects_symlink_dashboard_file_without_outside_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-output-symlink-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            cache = workspace / ".yxj-paper-os"
            cache.mkdir()
            outside = Path(tmp) / "outside-dashboard.html"
            outside.write_text("ORIGINAL", encoding="utf-8")
            (cache / "dashboard.html").symlink_to(outside)

            result = self.run_generator(workspace)
            combined = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("symlink", combined.lower())
            self.assertEqual("ORIGINAL", outside.read_text(encoding="utf-8"))

    def test_write_dashboard_replaces_hardlinked_dashboard_without_mutating_outside_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-output-hardlink-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            cache = workspace / ".yxj-paper-os"
            cache.mkdir()
            outside = Path(tmp) / "outside-dashboard.html"
            outside.write_text("ORIGINAL", encoding="utf-8")
            dashboard = cache / "dashboard.html"
            try:
                os.link(outside, dashboard)
            except OSError as exc:
                self.skipTest(f"hardlink creation unavailable for this filesystem: {exc}")
            self.assertTrue(os.path.samefile(outside, dashboard))

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)

            self.assertEqual("ORIGINAL", outside.read_text(encoding="utf-8"))
            self.assertIn("yxj-paper-os 结构仪表盘", html)
            self.assertFalse(os.path.samefile(outside, dashboard), "dashboard output must become an independent file")

    def test_dimension_html_click_detail_model_escaping_and_offline_refs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-html-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)

            for number in range(20):
                self.assertIn(f"D{number:02d}", html)
            self.assertRegex(html.lower(), r"addeventlistener|onclick|data-[a-z0-9_-]*dimension|detail")
            self.assertIn("SPECIAL_ESCAPING_SENTINEL", html)
            self.assertTrue("中文" in html or "\\u4e2d\\u6587" in html, "Chinese text should survive serialization")
            self.assertIn("**raw markdown**", html)
            self.assertNotIn('<script>alert("x")</script>', html, "source script payload must be escaped as text/data")
            self.assertRegex(html, r"&lt;script&gt;|\\u003cscript|&amp;lt;script")
            self.assert_no_external_refs(html)

    def test_missing_file_degrades_with_warning_without_copying_template(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-missing-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            missing = workspace / "03_WRITING_STRUCTURE.md"
            missing.unlink()
            before_files = self.relative_files(workspace)

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)
            combined = result.stdout + result.stderr + html

            self.assertFalse(missing.exists(), "dashboard generator must not copy missing Markdown templates")
            self.assertEqual(before_files | {".yxj-paper-os/dashboard.html"}, self.relative_files(workspace))
            self.assertRegex(combined.lower(), r"warning|missing")
            self.assertIn("03_WRITING_STRUCTURE.md", combined)

    def test_malformed_pointer_degrades_with_warning_and_still_generates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-pointer-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            text = index.read_text(encoding="utf-8")
            text = text.replace("00_PROJECT_ROUTE.md#Target Route", "00_PROJECT_ROUTE.md#Missing Dashboard Section")
            index.write_text(text, encoding="utf-8")

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)
            combined = result.stdout + result.stderr + html

            self.assertRegex(combined.lower(), r"warning|missing|unknown|section|pointer")
            self.assertIn("D04", combined)
            self.assertIn("Missing Dashboard Section", combined)
            self.assertIn("结构有警告", html)
            self.assertNotIn("结构状态：结构就绪", html)
            self.assertNotRegex(html, r"<h2[^>]*>\s*结构就绪\s*</h2>")

    def test_validator_mechanical_errors_render_as_nonblocking_warnings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-validator-warnings-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            route = workspace / "00_PROJECT_ROUTE.md"
            text = route.read_text(encoding="utf-8")
            text = text.replace("## Target Route", "## Target Route Removed", 1)
            text = text.replace("Status: structurally filled.", "Status: TODO", 1)
            route.write_text(text, encoding="utf-8")
            (workspace / "UNEXPECTED_PUBLIC.md").write_text("# unexpected", encoding="utf-8")

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)
            combined = result.stdout + result.stderr + html

            self.assertIn("validator: 00_PROJECT_ROUTE.md: missing required heading ## Target Route", combined)
            self.assertIn("validator: 00_PROJECT_ROUTE.md: section ## Route Readiness contains unresolved placeholder", combined)
            self.assertIn("validator: workspace has unexpected public Markdown files: UNEXPECTED_PUBLIC.md", combined)
            self.assertIn("结构有警告", html)

    def test_multiple_tables_in_one_section_remain_separate_and_reach_detail_model(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-multi-table-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "00_PROJECT_ROUTE.md",
                "Target Route",
                """First independent table.

| First key | First value |
|---|---|
| FIRST_TABLE_SENTINEL | Alpha |

Text between tables must split the blocks.

| Second key | Second value |
|---|---|
| SECOND_TABLE_SENTINEL | Beta |""",
            )

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)
            model = self.dashboard_model(html)
            route_sections = model["source_sections"]["00_PROJECT_ROUTE.md"]
            target_route = next(item for item in route_sections if item["heading"] == "Target Route")
            d04 = next(item for item in model["dimensions"] if item["id"] == "D04")
            serialized_tables = json.dumps(d04["source"]["tables"], ensure_ascii=False)

            self.assertEqual(2, len(target_route["tables"]))
            self.assertEqual(2, len(d04["source"]["tables"]))
            self.assertIn("FIRST_TABLE_SENTINEL", serialized_tables)
            self.assertIn("SECOND_TABLE_SENTINEL", serialized_tables)
            self.assertIn("指针源表格", html)
            self.assertIn("sourceTables(source.tables)", html)

    def test_validator_of_record_accepts_filled_fixture_without_errors(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-validator-clean-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.assertEqual([], validate_workspace(workspace))

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)
            model = self.dashboard_model(html)

            self.assertEqual([], [item for item in model["warnings"] if item["scope"] == "validator"])
            self.assertEqual("结构就绪", model["readiness"]["label"])

    def test_malformed_table_cell_count_degrades_without_silent_row_loss(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-table-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            lines = index.read_text(encoding="utf-8").splitlines()
            malformed = (
                "| D05 | 02_material_inventory.md | 01_MATERIALS_INVENTORY.md | filled | "
                "CELLCOUNT_SENTINEL malformed row with too many cells | "
                "01_MATERIALS_INVENTORY.md#Results and Experiments | yes | EXTRA_CELL |"
            )
            lines = [malformed if line.startswith("| D05 |") else line for line in lines]
            index.write_text("\n".join(lines) + "\n", encoding="utf-8")

            result = self.run_generator(workspace)
            html = self.assert_successful_dashboard(result, workspace)
            combined = result.stdout + result.stderr + html

            self.assertIn("D05", combined, "malformed dimension row must not vanish silently")
            self.assertIn("CELLCOUNT_SENTINEL", combined, "cell-count mismatch row should be surfaced in warning/detail data")
            self.assertRegex(combined.lower(), r"warning|malformed|cell|table")


if __name__ == "__main__":
    unittest.main(verbosity=2)
