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
from verify_dimension_rubric import QUESTION_DEPTH_LADDER_FIELDS  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parents[2]
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"
GENERATOR = SCRIPT_DIR / "generate_dashboard.py"
VALIDATOR = SCRIPT_DIR / "verify_design_pack.py"
DIMENSION_RUBRIC_VALIDATOR = SCRIPT_DIR / "verify_dimension_rubric.py"

REQUIRED_FILES = [
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
]

DIMENSION_NAMES = [
    "Workspace metadata",
    "Owner decisions",
    "Stale/readiness flags",
    "Project brief",
    "Target route profile",
    "Material inventory",
    "Evidence inventory",
    "Source and citation bank",
    "Research dossier",
    "Exemplar language profile",
    "Contribution options",
    "Claim-evidence map",
    "Wording boundary",
    "Limitation and risk matrix",
    "Reader spine",
    "Manuscript outline",
    "Object granularity",
    "Surface control",
    "Visual plan",
    "Writing design pack",
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

    def run_dimension_rubric_validator(
        self,
        *,
        script: Path | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_python(["-B", str(script or DIMENSION_RUBRIC_VALIDATOR)], cwd=cwd or REPO_ROOT)

    def make_temp_skill_repo(self, parent: Path) -> tuple[Path, Path]:
        repo = parent / "repo"
        skill_copy = repo / "skills" / "yxj-paper-os"
        skill_copy.parent.mkdir(parents=True)
        shutil.copytree(
            SKILL_DIR,
            skill_copy,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".yxj-paper-os"),
        )
        return repo, skill_copy

    def run_temp_dimension_rubric_validator(self, skill_copy: Path, repo: Path) -> subprocess.CompletedProcess[str]:
        return self.run_dimension_rubric_validator(
            script=skill_copy / "scripts" / "verify_dimension_rubric.py",
            cwd=repo,
        )

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
                    "## Front Matter / Hook Route Constraints",
                    "",
                    "| Front-matter planning field | Constraint or handoff note | Owner state / linked dimensions |",
                    "|---|---|---|",
                    "| Title style / scope | dashboard route only, no manuscript title drafting | owner fixture / D04-D12 |",
                    "| Abstract type / promise level | structural smoke-test summary only | D10-D13 boundary |",
                    "| Keyword scope | local dashboard, planning workspace, structural validator | D04/D07 |",
                    "| Visual or graphical hook | FIG1 exists as manual QA handoff | D18/D19 |",
                    "| Forbidden front-matter routes or wording | no publication, acceptance, novelty, or semantic-readiness promise | D12/D17/D19 |",
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
                    "## Reporting, Statements, and Downstream Route Seed",
                    "",
                    "| Route seed | Planning constraint | D19 handoff |",
                    "|---|---|---|",
                    "| Reporting guideline or checklist need | structural validator checks only | Method / Reporting / Reproducibility Handoff |",
                    "| Availability or statement need | local files are the only material boundary | Statement Inventory |",
                    "| Data/code/material availability route constraint | generator code path is test-owned | Material Boundary |",
                    "| Downstream route matrix seed | recommend routes only, with no runtime invocation | Downstream Route Matrix |",
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
                    "## Citation Function and Related-Work Materials",
                    "",
                    "| Material role | Supplied location or explicit absence | Citation-function / related-work boundary |",
                    "|---|---|---|",
                    "| Background / context source role | local dashboard fixture | context only, not literature support |",
                    "| Gap / contrast / counterevidence role | absent by design | no novelty or authority claim |",
                    "| Method lineage or reporting-standard role | generator implementation fixture | method context only |",
                    "| Citation-function unresolved need | absent | no citation search or BibTeX completion |",
                    "",
                    "## Method / Reporting / Reproducibility Materials",
                    "",
                    "| Method/repro field | Location, artifact, or absence/defer note | Downstream consequence |",
                    "|---|---|---|",
                    "| Method/system/model implementation artifact | generate_dashboard.py local CLI | supports structural method handoff |",
                    "| Parameters / environment / random seed | stdlib temporary workspace | no experiment reproduction claim |",
                    "| Code/data/material availability | six Markdown files and generator script | availability statement remains structural |",
                    "| Baseline / metric / ablation material | source immutability and warning count | not a scientific result |",
                    "| Reporting statement need | validator gate listed in D19 | no compliance certification |",
                    "",
                    "## Results / Visual / Caption / Accessibility Materials",
                    "",
                    "| Result/visual material field | Location or explicit absence/defer note | Evidence / accessibility / handoff boundary |",
                    "|---|---|---|",
                    "| Result artifact | generated hidden dashboard HTML | structural smoke evidence only |",
                    "| Figure/table source | FIG1 manual visual QA plan | D18 handoff, not active claim evidence beyond E1 |",
                    "| Caption/legend facts available | dashboard labels and warnings | handoff only; no caption drafting |",
                    "| Accessibility or alt-text need | D00-D19 labels and warning center | manual QA handoff |",
                    "| Missing/deferred visual material | none for fixture | needed visuals cannot support active claims |",
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
                    "| The generator preserves Markdown bytes in this fixture | E1 | structural | semantic-readiness promise | active |",
                    "",
                    "## Claim Support Boundary Reminder",
                    "",
                    "D07, D08, D09, and D18 cannot strengthen active claims without E1-style evidence anchors.",
                    "",
                    "## Writing-Surface Claim Boundary Matrix",
                    "",
                    "| Writing surface | Allowed claim function | Required support | Boundary / forbidden escalation |",
                    "|---|---|---|---|",
                    "| Front matter / hook | constrain promise scope | owner-confirmed route plus E1 boundary | no manuscript-ready front matter |",
                    "| Introduction / related work | describe local problem context | D07/D08 fixture notes plus D11 map | no novelty or source-authority claim |",
                    "| Method / reporting / reproducibility | report structural generator behavior | E1 and implementation fixture | no reproducibility proof |",
                    "| Results / visuals / captions / tables | describe dashboard smoke output | E1 plus FIG1 status | captions and visuals do not create evidence |",
                    "",
                    "## Front-Matter and Caption Wording Constraints",
                    "",
                    "| Surface term | Allowed wording boundary | Forbidden wording boundary |",
                    "|---|---|---|",
                    "| Title / abstract / keyword planning | structural dashboard route only | no publication-ready wording |",
                    "| Graphical hook / caption planning | handoff note and accessibility constraint | no generated caption prose |",
                    "| Result or visual claim | must cite E1 if active | no visual-only support |",
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
                    "## Front-Matter / Hook Planning Brief",
                    "",
                    "| Front-matter unit | Planning function | Inputs / linked dimensions | Constraint or handoff note |",
                    "|---|---|---|---|",
                    "| Title scope | route-safe structural label | D04/D12 | no manuscript title drafting |",
                    "| Abstract promise | smoke-test behavior summary | D10-D13 | no semantic-readiness promise |",
                    "| Keyword boundary | local dashboard/tooling terms | D04/D07/D09 | no invented domain keywords |",
                    "| Visual hook | FIG1 manual QA route | D18/D19 | no graphical asset generation |",
                    "",
                    "## Reader Spine",
                    "",
                    "| Reader step | Reader persona / question | Expected answer | Linked claim / evidence / limitation | Transition rationale or forbidden question |",
                    "|---|---|---|---|---|",
                    "| 1 | Maintainer asks what changed | Only hidden dashboard file changed | E1 | no semantic scoring |",
                    "",
                    "## Introduction / Related-Work Move Sequence",
                    "",
                    "| Move | Planning job | Source/citation function | Claim/evidence boundary |",
                    "|---|---|---|---|",
                    "| Context | local dashboard workspace | background role only | no source authority claim |",
                    "| Gap / problem | source mutation and hidden malformed rows | gap candidate only | no novelty claim |",
                    "| Contribution preview | static structural dashboard | tied to E1 | no semantic paper-quality claim |",
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
                    "## Method / Reporting / Reproducibility Job Plan",
                    "",
                    "| Method/reporting unit | Planning job | Required material or artifact | Statement / limitation / handoff |",
                    "|---|---|---|---|",
                    "| Generator invocation | public CLI smoke path | generate_dashboard.py | no external runtime route |",
                    "| Source preservation | hash six Markdown files | E1 file-hash snapshot | structural only |",
                    "| Warning behavior | surface malformed input visibly | warning model | no scientific metric claim |",
                    "| Availability statement | local fixture boundaries | six workspace files | no reproducibility certification |",
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
                    "## Results Narrative / Caption / Accessibility Plan",
                    "",
                    "| Results surface | Narrative or display role | Evidence / visual status | Caption/table/accessibility handoff |",
                    "|---|---|---|---|",
                    "| Dashboard HTML output | show structural state | E1 available | labels must stay readable |",
                    "| Warning center | expose malformed Markdown | E1 available | no hidden row loss |",
                    "| Figure caption or legend job | manual QA describes FIG1 | FIG1 available as plan | no caption drafting |",
                    "| Accessibility note | D00-D19 labels and warning text | manual review | alt-text handoff only |",
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
                    "## Six-Track Coverage",
                    "",
                    "| Track | Input planning field locations | Design-pack output location | Boundary note |",
                    "|---|---|---|---|",
                    "| Front matter / hook | 00_PROJECT_ROUTE.md#Front Matter / Hook Route Constraints; 03_WRITING_STRUCTURE.md#Front-Matter / Hook Planning Brief | 04_WRITING_DESIGN_PACK.md#Front-Matter / Hook Planning Handoff | Planning-only title, abstract, keyword, and visual-hook constraints; no manuscript-ready prose. |",
                    "| Introduction / related work / citation function | 01_MATERIALS_INVENTORY.md#Citation Function and Related-Work Materials; 02_CLAIM_EVIDENCE_BOUNDARY.md#Writing-Surface Claim Boundary Matrix; 03_WRITING_STRUCTURE.md#Introduction / Related-Work Move Sequence | 04_WRITING_DESIGN_PACK.md#Introduction / Related-Work / Citation Function Handoff | Citation and related-work functions are handoff notes only; no citation truth or novelty claim. |",
                    "| Method / reporting / reproducibility | 00_PROJECT_ROUTE.md#Reporting, Statements, and Downstream Route Seed; 01_MATERIALS_INVENTORY.md#Method / Reporting / Reproducibility Materials; 03_WRITING_STRUCTURE.md#Method / Reporting / Reproducibility Job Plan | 04_WRITING_DESIGN_PACK.md#Method / Reporting / Reproducibility Handoff | Method/reporting/reproducibility checklist state is structural; no experiment or data invention. |",
                    "| Results / visual narrative / captions / tables / accessibility | 01_MATERIALS_INVENTORY.md#Results / Visual / Caption / Accessibility Materials; 03_WRITING_STRUCTURE.md#Results Narrative / Caption / Accessibility Plan | 04_WRITING_DESIGN_PACK.md#Results / Visual / Captions / Tables / Accessibility Handoff | Caption/table/accessibility planning cannot turn needed visuals into active evidence. |",
                    "| Downstream route matrix | 00_PROJECT_ROUTE.md#Reporting, Statements, and Downstream Route Seed; 04_WRITING_DESIGN_PACK.md#External Skill Handoff | 04_WRITING_DESIGN_PACK.md#Downstream Route Matrix | External routes are recommendations only and are not executed. |",
                    "| Templates + validators | 00_DIMENSION_INDEX.md#Dimension Status Index; 04_WRITING_DESIGN_PACK.md#Template and Mechanical Validator Notes; 04_WRITING_DESIGN_PACK.md#Validation Notes | 04_WRITING_DESIGN_PACK.md#Template and Mechanical Validator Notes | Validators check structure, phrases, pointers, placeholders, statuses, and columns only. |",
                    "",
                    "## Project Route",
                    "",
                    "Structural local dashboard route for yxj-paper-os planning workspaces.",
                    "",
                    "## Front-Matter / Hook Planning Handoff",
                    "",
                    "| Front-matter unit | Constraint / owner-gated input | Source dimensions | Downstream handoff note |",
                    "|---|---|---|---|",
                    "| Title scope | route-safe structural title constraints only | D04/D12 | downstream writing may draft later under this boundary |",
                    "| Abstract structure boundary | summary must stay tied to E1 support | D10-D13/D15 | no manuscript-ready abstract prose here |",
                    "| Keyword / controlled-term boundary | local dashboard/tooling terms only | D04/D07/D09 | no invented domain keyword list |",
                    "| Visual or graphical hook boundary | FIG1 manual QA route | D18/D19 | no graphical asset or caption generation |",
                    "",
                    "## Introduction / Related-Work / Citation Function Handoff",
                    "",
                    "| Handoff item | Source planning location | Required boundary | Downstream note |",
                    "|---|---|---|---|",
                    "| Introduction move sequence | 03_WRITING_STRUCTURE.md#Introduction / Related-Work Move Sequence | claim/evidence limits from D11-D13 | downstream writing receives moves, not prose |",
                    "| Related-work grouping or citation role | 01_MATERIALS_INVENTORY.md#Citation Function and Related-Work Materials | supplied fixture roles only | no citation search or source-authority claim |",
                    "| Gap / contrast / counterevidence note | 02_CLAIM_EVIDENCE_BOUNDARY.md#Writing-Surface Claim Boundary Matrix | no novelty proof | keep as structural risk note |",
                    "| Citation-function unresolved need | 01_MATERIALS_INVENTORY.md#Source and Citation Bank | no invented references | citation route remains recommendation only |",
                    "",
                    "## Method / Reporting / Reproducibility Handoff",
                    "",
                    "| Handoff item | Artifact / checklist state | Required statement or limitation | Downstream note |",
                    "|---|---|---|---|",
                    "| Method/system/model reporting | generate_dashboard.py local CLI | structural generator behavior only | no experiment invention |",
                    "| Protocol / parameter / environment reporting | stdlib temporary workspace | no random-seed or benchmark claim | method route may document invocation later |",
                    "| Data/code/material availability | six Markdown files plus generator script | source boundary is local | no reproducibility certification |",
                    "| Reproducibility package status | available for structural smoke only | checklist state is not proof | downstream note stays cautious |",
                    "| Reporting guideline / statement inventory | validator/test gate | no compliance certification | record as D19 statement inventory |",
                    "",
                    "## Results / Visual / Captions / Tables / Accessibility Handoff",
                    "",
                    "| Handoff item | Evidence or visual status | Caption/table/accessibility constraint | Downstream note |",
                    "|---|---|---|---|",
                    "| Results narrative path | E1 available | must cite structural evidence | no result-value invention |",
                    "| Figure / visual caption or legend | FIG1 available as manual QA plan | handoff only; no caption drafting | visual route may inspect later |",
                    "| Table / supplement display | dashboard source tables available | keep malformed-row warnings visible | no table fact invention |",
                    "| Statistic or metric display | warning count and hashes only | do not exceed support strength | structural QA metric only |",
                    "| Accessibility / alt-text / readability need | manual QA | D00-D19 labels must remain readable | alt-text handoff only |",
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
                    "## Downstream Route Matrix",
                    "",
                    "| Downstream route | Eligible input sections | Constraints to pass forward | Blocker / defer note |",
                    "|---|---|---|---|",
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | not executed; preserve claim/evidence boundaries | no blocker recorded |",
                    "| Citation / reference route | 04_WRITING_DESIGN_PACK.md#Source / Citation Boundary | not executed; no citation search or BibTeX completion here | no blocker recorded |",
                    "| Figure / visual route | 04_WRITING_DESIGN_PACK.md#Visual and Figure Storyline | not executed; receives visual plan, not evidence invention | manual QA handoff |",
                    "| Review / QA route | 04_WRITING_DESIGN_PACK.md#Validation Notes | not executed; structural risks only | no acceptance prediction |",
                    "| No external route / defer | 04_WRITING_DESIGN_PACK.md | not executed; owner may defer route | no route run by yxj-paper-os |",
                    "",
                    "## External Skill Handoff",
                    "",
                    "No external skill handoff is executed by this dashboard fixture.",
                    "",
                    "## Template and Mechanical Validator Notes",
                    "",
                    "| Check surface | Expected structural evidence | Boundary / non-goal |",
                    "|---|---|---|",
                    "| Six-template surface | exactly the six public Markdown files | no public file expansion |",
                    "| Dimension-index schema | existing columns and status values only | no public tier/status drift |",
                    "| Six-track handoff matrix | rows for all six tracks with canonical anchors | routing map only |",
                    "| Placeholder / stale gate | final pack has no placeholders and D02 risk is reconciled | freshness is not semantic adequacy |",
                    "| Claim/evidence/visual boundary | D06/D11 anchors and D18 status respected | needed visuals are not evidence |",
                    "",
                    "## Validation Notes",
                    "",
                    "Validation is structural against the six-file and 20-dimension contract only.",
                    "",
                    "Final yxj-paper-os handoff",
                    "",
                    "- Pack status: valid",
                    "- Ready for: downstream writing planning from 04_WRITING_DESIGN_PACK.md",
                    "- Not ready for: final citations, manuscript-ready prose, submission, publication, acceptance, or semantic adequacy claims",
                    "- Validation: python3 skills/yxj-paper-os/scripts/verify_design_pack.py <workspace> -> pass",
                    "- Remaining deferred/absent/rejected items: none",
                    "- Recommended downstream route(s): writing, citation, figure, review, or defer; recommendation only; no external route executed",
                    "- Next owner action if blocked: none for this fixture",
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

    def validator_errors(self, workspace: Path) -> str:
        return "\n".join(validate_workspace(workspace))

    def test_existing_validator_still_py_compiles(self) -> None:
        result = self.run_python(["-m", "py_compile", str(VALIDATOR)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_dimension_rubric_validator_accepts_current_repo(self) -> None:
        result = self.run_dimension_rubric_validator()
        combined = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, combined)
        self.assertIn("Dimension rubric structural validation passed", combined)

    def test_dimension_rubric_validator_rejects_missing_ladder_label_in_temp_copy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-rubric-missing-label-") as tmp:
            repo, skill_copy = self.make_temp_skill_repo(Path(tmp))
            rubric = skill_copy / "references" / "00-dimension-rubric.md"
            text = rubric.read_text(encoding="utf-8")
            target_line = (
                "- **Depth probe:** What provenance or intake-change note would prevent "
                "stale or wrong-project handoff?\n"
            )
            self.assertIn(target_line, text)
            rubric.write_text(text.replace(target_line, "", 1), encoding="utf-8")

            result = self.run_temp_dimension_rubric_validator(skill_copy, repo)
            combined = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("D00: question-depth ladder label 'Depth probe' must appear exactly once; found 0", combined)

    def test_dimension_rubric_validator_rejects_duplicate_dxx_heading_in_temp_copy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-rubric-duplicate-heading-") as tmp:
            repo, skill_copy = self.make_temp_skill_repo(Path(tmp))
            rubric = skill_copy / "references" / "00-dimension-rubric.md"
            text = rubric.read_text(encoding="utf-8")
            rubric.write_text(f"{text}\n\n### D05 — duplicate temporary heading\n\n- **ID:** D05\n", encoding="utf-8")

            result = self.run_temp_dimension_rubric_validator(skill_copy, repo)
            combined = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("D05: rubric heading must appear exactly once; found 2", combined)

    def test_dimension_rubric_validator_rejects_missing_playbook_translator_phrase_in_temp_copy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-playbook-missing-translator-") as tmp:
            repo, skill_copy = self.make_temp_skill_repo(Path(tmp))
            playbook = skill_copy / "references" / "00-project-route.md"
            text = playbook.read_text(encoding="utf-8")
            phrase = "The central rubric decides sufficiency and question-depth"
            self.assertIn(phrase, text)
            playbook.write_text(text.replace(phrase, "This file only holds local route examples", 1), encoding="utf-8")

            result = self.run_temp_dimension_rubric_validator(skill_copy, repo)
            combined = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn(
                "00-project-route.md: missing playbook translator/rubric-authority phrase: "
                "The central rubric decides sufficiency and question-depth",
                combined,
            )

    def test_dimension_rubric_validator_rejects_playbook_full_ladder_copy_in_temp_copy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-playbook-full-ladder-") as tmp:
            repo, skill_copy = self.make_temp_skill_repo(Path(tmp))
            playbook = skill_copy / "references" / "01-materials-inventory.md"
            text = playbook.read_text(encoding="utf-8")
            accidental_copy = "\n".join(f"- {label}: copied from central rubric" for label in QUESTION_DEPTH_LADDER_FIELDS)
            playbook.write_text(
                f"{text}\n\n## Accidental full ladder copy\n\n{accidental_copy}\n",
                encoding="utf-8",
            )

            result = self.run_temp_dimension_rubric_validator(skill_copy, repo)
            combined = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("01-materials-inventory.md: duplicates the complete eleven-label question-depth ladder", combined)

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

    def test_validator_rejects_missing_six_track_coverage_table(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-missing-six-track-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Six-Track Coverage",
                "Six tracks are described in prose only.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("Six-Track Coverage must contain a Markdown table", errors)

    def test_validator_rejects_missing_second_batch_source_section(self) -> None:
        cases = [
            ("00_PROJECT_ROUTE.md", "Front Matter / Hook Route Constraints"),
            ("01_MATERIALS_INVENTORY.md", "Method / Reporting / Reproducibility Materials"),
            ("03_WRITING_STRUCTURE.md", "Results Narrative / Caption / Accessibility Plan"),
            ("04_WRITING_DESIGN_PACK.md", "Front-Matter / Hook Planning Handoff"),
            ("04_WRITING_DESIGN_PACK.md", "Method / Reporting / Reproducibility Handoff"),
        ]
        for file_name, heading in cases:
            with self.subTest(file_name=file_name, heading=heading):
                with tempfile.TemporaryDirectory(prefix="yxj-paper-os-missing-track-section-") as tmp:
                    workspace = self.make_filled_workspace(Path(tmp))
                    self.replace_section_body(workspace, file_name, heading, "")

                    errors = self.validator_errors(workspace)

                    self.assertIn(f"{file_name}: section ## {heading} is empty", errors)

    def test_validator_rejects_missing_track_handoff_table(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-missing-track-table-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Results / Visual / Captions / Tables / Accessibility Handoff",
                "Result/caption/accessibility handoff described in prose only.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("Results / Visual / Captions / Tables / Accessibility Handoff must contain a Markdown table", errors)

    def test_validator_rejects_noncanonical_six_track_output_pointer(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-bad-track-output-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "04_WRITING_DESIGN_PACK.md#Front-Matter / Hook Planning Handoff",
                    "04_WRITING_DESIGN_PACK.md#Six-Track Coverage",
                    1,
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn(
                "Design-pack output location must include canonical pointer "
                "04_WRITING_DESIGN_PACK.md#Front-Matter / Hook Planning Handoff",
                errors,
            )

    def test_validator_rejects_missing_six_track_input_anchor(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-bad-track-input-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "01_MATERIALS_INVENTORY.md#Method / Reporting / Reproducibility Materials",
                    "01_MATERIALS_INVENTORY.md#Code / Implementation",
                    1,
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn(
                "Input planning field locations must include canonical pointer "
                "01_MATERIALS_INVENTORY.md#Method / Reporting / Reproducibility Materials",
                errors,
            )

    def test_validator_rejects_final_pack_placeholders(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-placeholder-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(workspace, "04_WRITING_DESIGN_PACK.md", "Validation Notes", "TODO")

            errors = self.validator_errors(workspace)

            self.assertIn("final handoff contains unresolved placeholder", errors)

    def test_validator_rejects_d07_filled_without_supplied_sources(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-d07-false-filled-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Source and Citation Bank",
                """
| Source/citation prompt | Supplied detail or explicit absence/defer note | Boundary or handoff |
|---|---|---|
| Source identity and locator/version | no sources supplied | downstream citation route asks owner |
| Source role and citation status | absent | do not invent references |
| Downstream citation handoff need | deferred | no citation task here |
""",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("D07 is marked filled", errors)
            self.assertIn("mark D07 absent or deferred", errors)

    def test_validator_allows_d07_absent_with_handoff(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-d07-absent-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            absence_handoff = "Handoff: no supplied sources; downstream citation route asks owner for source detail"
            for file_name, pattern in [
                (
                    "00_DIMENSION_INDEX.md",
                    r"(\| D07 \| Source and citation bank \| 01_MATERIALS_INVENTORY\.md \| )filled(\s*\| [^|]+\| )01_MATERIALS_INVENTORY\.md#Source and Citation Bank(\s*\| yes \|)",
                ),
                (
                    "04_WRITING_DESIGN_PACK.md",
                    r"(\| D07 \| )filled(\s*\| )01_MATERIALS_INVENTORY\.md#Source and Citation Bank(\s*\| yes \|)",
                ),
            ]:
                path = workspace / file_name
                text = path.read_text(encoding="utf-8")
                text = re.sub(pattern, rf"\1absent\2{absence_handoff}\3", text, count=1)
                path.write_text(text, encoding="utf-8")
            self.replace_section_body(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Source and Citation Bank",
                """
| Source/citation prompt | Supplied detail or explicit absence/defer note | Boundary or handoff |
|---|---|---|
| Source identity and locator/version | absent | do not invent external citations |
| Source role and citation status | absent | context only; no claim support |
| Downstream citation handoff need | deferred | downstream citation route asks owner |
""",
            )

            self.assertEqual([], validate_workspace(workspace))

    def test_validator_rejects_missing_final_handoff_card(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-missing-final-card-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Validation Notes",
                "Validation is structural against the six-file and 20-dimension contract only.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("final handoff card missing required boundary field", errors)

    def test_validator_rejects_retired_dimension_filename_label(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-retired-label-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            retired_label = "10_" + "research_dossier.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "| D08 | Research dossier |",
                    f"| D08 | {retired_label} |",
                    1,
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("contains retired dimension filename label", errors)
            self.assertIn("Dimension must be current semantic name 'Research dossier'", errors)

    def test_validator_rejects_retired_stage_token(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-retired-stage-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            route = workspace / "00_PROJECT_ROUTE.md"
            retired_stage = "S" + "10"
            route.write_text(
                route.read_text(encoding="utf-8").replace(
                    "Journal-style software paper route",
                    f"Retired {retired_stage} route should not appear in the current workflow.",
                    1,
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn(f"contains retired stage/governance token '{retired_stage}'", errors)

    def test_validator_rejects_dimension_status_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-status-drift-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            text = index.read_text(encoding="utf-8")
            text = text.replace(
                "| D05 | Material inventory | 01_MATERIALS_INVENTORY.md | filled |",
                "| D05 | Material inventory | 01_MATERIALS_INVENTORY.md | unknown |",
                1,
            )
            index.write_text(text, encoding="utf-8")

            errors = self.validator_errors(workspace)

            self.assertIn("invalid Status 'unknown'", errors)

    def test_validator_rejects_missing_pointer_or_handoff_reason(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-pointer-reason-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            text = index.read_text(encoding="utf-8")
            text = re.sub(
                r"(\| D06 \| Evidence inventory \| 01_MATERIALS_INVENTORY\.md \| filled \| )[^|]+(\| )[^|]+(\| yes \|)",
                r"\1TODO \2TODO \3",
                text,
                count=1,
            )
            index.write_text(text, encoding="utf-8")

            errors = self.validator_errors(workspace)

            self.assertIn("Reason / owner note is missing or placeholder", errors)
            self.assertIn("Pointer or handoff is missing or placeholder", errors)

    def test_validator_rejects_needed_visual_used_as_active_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-needed-visual-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            structure = workspace / "03_WRITING_STRUCTURE.md"
            structure.write_text(
                structure.read_text(encoding="utf-8").replace(
                    "| FIG1 | static existing dashboard screenshot | E1 | accessible labels for D00-D19 | manual QA |",
                    "| FIG1 | needed figure | E1 | accessible labels for D00-D19 | manual QA |",
                ),
                encoding="utf-8",
            )
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "| The dashboard writes only its hidden HTML output | E1 | structural | source files unchanged | semantic readiness | active |",
                    "| The dashboard writes only its hidden HTML output | FIG1 | structural | source files unchanged | semantic readiness | active |",
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("cannot support an active claim without available D06 evidence", errors)

    def test_validator_rejects_unresolved_stale_d19_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-stale-d19-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "| none | none | not applicable | no | owner accepted current fixture | no stale risk |",
                    "| D11 | Claim-Evidence Map | 2026-07-06 | yes | none | none |",
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("recompile is required but lacks an owner action or semantic-risk handoff", errors)

    def test_validator_rejects_external_skill_execution_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-external-exec-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | not executed; preserve claim/evidence boundaries | no blocker recorded |",
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | executed external writing skill | no blocker recorded |",
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("appears to claim an external skill was executed", errors)

    def test_validator_rejects_public_index_schema_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-schema-drift-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            text = index.read_text(encoding="utf-8").replace(
                "| ID | Dimension | Current home | Status | Reason / owner note | Pointer or handoff | Blocks design pack? |",
                "| ID | Dimension | Current home | Status | Tier | Reason / owner note | Pointer or handoff | Blocks design pack? |",
                1,
            )
            text = text.replace("|---|---|---|---|---|---|---|", "|---|---|---|---|---|---|---|---|", 1)
            text = text.replace(" | filled | Owner-filled", " | filled | standard | Owner-filled")
            index.write_text(text, encoding="utf-8")

            errors = self.validator_errors(workspace)

            self.assertIn("Dimension Status Index columns must be exactly", errors)

    def test_validator_rejects_forbidden_semantic_promise(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-semantic-promise-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Validation Notes",
                "This validator proves semantic adequacy for the paper.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("forbidden semantic scoring promise", errors)

    def test_validator_rejects_negation_bypassed_external_execution_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-negation-exec-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | not executed; preserve claim/evidence boundaries | no blocker recorded |",
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | not deferred; executed external writing skill | no blocker recorded |",
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("appears to claim an external skill was executed", errors)

    def test_validator_rejects_passive_external_execution_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-passive-exec-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            final = workspace / "04_WRITING_DESIGN_PACK.md"
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | not executed; preserve claim/evidence boundaries | no blocker recorded |",
                    "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | external writing skill was run | no blocker recorded |",
                ),
                encoding="utf-8",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("appears to claim an external skill was executed", errors)

    def test_validator_rejects_boundary_then_external_execution_same_line(self) -> None:
        cases = [
            "Do not execute external writing skill: external writing skill was run",
            "Do not execute external writing skill. external writing skill was run",
            "not executed, external writing skill was run",
            "not executed but external writing skill was run",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                with tempfile.TemporaryDirectory(prefix="yxj-paper-os-boundary-exec-") as tmp:
                    workspace = self.make_filled_workspace(Path(tmp))
                    final = workspace / "04_WRITING_DESIGN_PACK.md"
                    final.write_text(
                        final.read_text(encoding="utf-8").replace(
                            "| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | not executed; preserve claim/evidence boundaries | no blocker recorded |",
                            f"| Manuscript-writing route | 04_WRITING_DESIGN_PACK.md | {phrase} | no blocker recorded |",
                        ),
                        encoding="utf-8",
                    )

                    errors = self.validator_errors(workspace)

                    self.assertIn("appears to claim an external skill was executed", errors)

    def test_validator_rejects_negation_bypassed_semantic_promise(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-negation-semantic-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Validation Notes",
                "Not optional: validator proves semantic adequacy.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("forbidden semantic scoring promise", errors)

    def test_validator_rejects_semantic_promise_inflections(self) -> None:
        cases = [
            "This validator verifies semantic adequacy for the paper.",
            "This validator certifies semantic-readiness.",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                with tempfile.TemporaryDirectory(prefix="yxj-paper-os-semantic-inflection-") as tmp:
                    workspace = self.make_filled_workspace(Path(tmp))
                    self.replace_section_body(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "Validation Notes",
                        phrase,
                    )

                    errors = self.validator_errors(workspace)

                    self.assertIn("forbidden semantic scoring promise", errors)

    def test_validator_rejects_semantic_readiness_promise(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-semantic-readiness-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Validation Notes",
                "This validator proves semantic readiness.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("forbidden semantic scoring promise", errors)

    def test_validator_rejects_semantic_adequacy_approved_language(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-semantic-approved-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Validation Notes",
                "This pack says semantic adequacy approved.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("forbidden readiness promise", errors)

    def test_validator_rejects_boundary_then_semantic_promise_same_line(self) -> None:
        cases = [
            "Do not claim semantic adequacy: validator proves semantic adequacy.",
            "Do not claim semantic adequacy. validator proves semantic adequacy.",
            "does not prove semantic adequacy, but validates semantic readiness",
            "does not prove semantic adequacy but validates semantic readiness",
            "does not prove semantic adequacy, validates semantic readiness",
            "does not prove semantic adequacy and validates semantic readiness",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                with tempfile.TemporaryDirectory(prefix="yxj-paper-os-boundary-semantic-") as tmp:
                    workspace = self.make_filled_workspace(Path(tmp))
                    self.replace_section_body(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "Validation Notes",
                        phrase,
                    )

                    errors = self.validator_errors(workspace)

                    self.assertIn("forbidden semantic scoring promise", errors)

    def test_validator_rejects_claimed_semantic_readiness_promise(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-claims-readiness-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            self.replace_section_body(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "Validation Notes",
                "This validator claims semantic readiness.",
            )

            errors = self.validator_errors(workspace)

            self.assertIn("forbidden semantic scoring promise", errors)

    def test_malformed_table_cell_count_degrades_without_silent_row_loss(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yxj-paper-os-table-") as tmp:
            workspace = self.make_filled_workspace(Path(tmp))
            index = workspace / "00_DIMENSION_INDEX.md"
            lines = index.read_text(encoding="utf-8").splitlines()
            malformed = (
                "| D05 | Material inventory | 01_MATERIALS_INVENTORY.md | filled | "
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
