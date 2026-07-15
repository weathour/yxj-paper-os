from __future__ import annotations

import hashlib
import json
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verify_design_pack import validate_workspace, validate_workspace_report
from verify_semantic_dossier import rule_dependency_fingerprint


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path(__file__).resolve().with_name("verify_design_pack.py")
FIXTURES = ROOT / "assets" / "fixtures" / "design-pack"
DETAILED = FIXTURES / "detailed-ready-minimal-0.3"
LEGACY = FIXTURES / "legacy-section-ready-0.2"


def copy_fixture(source: Path, destination: Path) -> Path:
    workspace = destination / source.name
    shutil.copytree(source, workspace)
    return workspace


def replace(workspace: Path, filename: str, old: str, new: str) -> None:
    path = workspace / filename
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"mutation source not found in {filename}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def codes(errors: list[str]) -> set[str]:
    return {error.split(":", 1)[0] for error in errors}


def append_table_row(workspace: Path, filename: str, heading: str, row: str) -> None:
    path = workspace / filename
    text = path.read_text(encoding="utf-8")
    marker = f"## {heading}"
    start = text.index(marker)
    next_heading = text.find("\n## ", start + len(marker))
    if next_heading < 0:
        next_heading = len(text)
    body = text[start:next_heading].rstrip()
    path.write_text(
        text[:start] + body + "\n" + row + "\n\n" + text[next_heading:].lstrip("\n"),
        encoding="utf-8",
    )


def activate_rule_coverage(workspace: Path, count: int) -> None:
    replace(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "| template_rule_provenance | SCOPE-demo | not_applicable | 0 | none | Template design is irrelevant to this synthetic route-neutral contract fixture |",
        f"| template_rule_provenance | SCOPE-demo | satisfied | {count} | 03_WRITING_STRUCTURE.md#Template Rule Projection | Active design-only rule projections are declared |",
    )
    replace(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 0 | 0 |",
        f"| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 1 | {count} | 0 |",
    )


def activate_budget_coverage(workspace: Path, count: int) -> None:
    replace(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "| soft_budgets | SCOPE-demo | not_applicable | 0 | none | No grounded quantitative official semantic or fallback basis exists for a useful band |",
        f"| soft_budgets | SCOPE-demo | satisfied | {count} | 03_WRITING_STRUCTURE.md#Grounded Soft Budgets | Grounded design-only soft budgets are declared |",
    )
    summary_path = workspace / "04_WRITING_DESIGN_PACK.md"
    summary_text = summary_path.read_text(encoding="utf-8")
    for rule_count in (1, 0):
        old = f"| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 1 | {rule_count} | 0 |"
        if old in summary_text:
            summary_path.write_text(
                summary_text.replace(
                    old,
                    f"| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 1 | {rule_count} | {count} |",
                    1,
                ),
                encoding="utf-8",
            )
            return
    raise AssertionError("budget coverage summary mutation source not found")


def install_second_ready_scope(workspace: Path) -> None:
    append_table_row(
        workspace,
        "00_DIMENSION_INDEX.md",
        "Writing Scopes",
        "| SCOPE-other | Separate one-paragraph bounded surface | Controlled writing handoff | writer-ready | M-method;M-evidence | REQ-detailed | none | none | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage |",
    )
    replace(
        workspace,
        "00_DIMENSION_INDEX.md",
        "| SCOPE-demo |\n\n## Conditional Requirements",
        "| SCOPE-demo;SCOPE-other |\n\n## Conditional Requirements",
    )
    replace(
        workspace,
        "00_DIMENSION_INDEX.md",
        "| SCOPE-demo | satisfied |",
        "| SCOPE-demo;SCOPE-other | satisfied |",
    )
    replace(
        workspace,
        "00_PROJECT_ROUTE.md",
        "| SCOPE-demo | artifact-observed |",
        "| SCOPE-demo;SCOPE-other | artifact-observed |",
    )

    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Section Map",
        "| SEC-other | SCOPE-other | 1 | Receive the explicit cross-scope handoff | Reader has completed the first bounded surface | Reader understands the separate receiving job | M-method;M-evidence;C-demo | One bounded receiving paragraph | Preserve M-evidence and C-demo ceilings | No cross-scope paragraph adjacency or invented support |",
    )
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Paragraph Map",
        "| PAR-other | SCOPE-other | SEC-other | 1 | Receive the explicit handoff without joining paragraph sequences | Reader has completed SCOPE-demo | Reader sees the separate receiving responsibility | none | none |",
    )
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Paragraph Payload and Boundary Map",
        "| PAR-other | C-demo | M-evidence | Reuse only the bounded claim and evidence identifiers | evidence support for the bounded receiving job | none | not_applicable: this receiving paragraph introduces no equation algorithm visual or table | Preserve the synthetic-evidence limitation | Close only the receiving responsibility | No superiority novelty or generality claim | none |",
    )
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Surface Language Contract",
        "| LANG-other | SCOPE-other | PAR-other | Reuse bounded comparison and receiving job consistently | Qualified comparative only | Preserve explicit bounded-by modality | Present tense active voice for design roles | One short receiving job | No proves guarantees novel optimal or venue-fit wording | M-method;M-evidence;C-demo |",
    )
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Cross-Surface Traceability",
        "| EDGE-handoff | PAR-claim | hands_off_to | PAR-other | Explicit cross-scope handoff without paragraph adjacency | current | Recheck both scoped jobs if the handoff changes |",
    )
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Scoped Writing Plan",
        "| SCOPE-other | SEC-other with one receiving paragraph job | M-method;M-evidence;C-demo;LANG-other | Realize only the bounded receiving job | Do not merge paragraph sequences across scopes | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |",
    )

    for row in (
        "| section_paragraph_map | SCOPE-other | satisfied | 3 | 03_WRITING_STRUCTURE.md#Section Map | One section paragraph and payload row resolve |",
        "| important_paragraph_frames | SCOPE-other | not_applicable | 0 | none | No consequence-bearing paragraph needs sentence frames |",
        "| surface_language_contract | SCOPE-other | satisfied | 1 | 03_WRITING_STRUCTURE.md#Surface Language Contract | LANG-other governs the receiving paragraph |",
        "| visual_caption_blueprint | SCOPE-other | not_applicable | 0 | none | This receiving surface has no visual job |",
        "| cross_surface_traceability | SCOPE-other | satisfied | 1 | 03_WRITING_STRUCTURE.md#Cross-Surface Traceability | EDGE-handoff declares the cross-scope relation |",
        "| template_rule_provenance | SCOPE-other | not_applicable | 0 | none | No template design rule governs this synthetic surface |",
        "| soft_budgets | SCOPE-other | not_applicable | 0 | none | No grounded soft budget applies to this surface |",
    ):
        append_table_row(
            workspace, "04_WRITING_DESIGN_PACK.md", "Detailed Surface Coverage", row
        )
    replace(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "| cross_surface_traceability | SCOPE-demo | satisfied | 1 |",
        "| cross_surface_traceability | SCOPE-demo | satisfied | 2 |",
    )
    replace(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 0 | 0 |",
        "| SCOPE-demo | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 0 | 0 |",
    )
    append_table_row(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "Detailed Coverage Summary",
        "| SCOPE-other | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |",
    )
    append_table_row(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "Owner Gate Resolution Summary",
        "| SCOPE-other | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
    )
    append_table_row(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "Template Analysis Handling",
        "| SCOPE-other | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic receiving surface | none |",
    )
    append_table_row(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "Unresolved and Downstream Prohibitions",
        "| SCOPE-other | none | No unresolved record affects this scope | Preserve the separate receiving responsibility and evidence ceiling |",
    )
    append_table_row(
        workspace,
        "04_WRITING_DESIGN_PACK.md",
        "Scoped Handoff",
        "| SCOPE-other | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | Do not merge paragraph adjacency across scopes or invent support | Use EDGE-handoff as the only cross-scope relation |",
    )


def install_semantic_rule(workspace: Path) -> str:
    source = workspace / "sources" / "template.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Methods\n\nA bounded template passage.\n", encoding="utf-8")
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    design_question = (
        "How should the method explanation stage its bounded contribution?"
    )
    document = {
        "template_source_id": "TPL-method",
        "title": "Bounded method exemplar",
        "source_pointer": "sources/template.md",
        "acquisition_provenance": "owner-supplied local derivative",
        "role": "exemplar",
        "design_question": design_question,
        "design_relevance": "Method paragraph sequencing only.",
        "access_state": "owner_derivative",
        "local_derivative_pointer": "sources/template.md",
        "source_sha256": source_sha,
        "accessed_at": "2026-07-15T00:00:00Z",
        "access_copyright_limitation": "No full body is stored in the dossier.",
        "freshness": "verified_local_current",
        "semantic_reading_eligible": True,
        "design_only_state": "design_only",
    }
    observation = {
        "observation_id": "TOBS-method-order",
        "template_source_id": "TPL-method",
        "locator": {"kind": "paragraph", "value": "Methods paragraph 2"},
        "observed_pattern": "The paragraph states the bounded object before mechanism detail.",
        "semantic_interpretation": "Object-first ordering reduces referent ambiguity.",
        "uncertainty": "Observed in one eligible exemplar.",
        "non_transfer_note": "Do not copy wording or infer scientific authority.",
        "status": "model-derived",
    }
    transfer_rule = {
        "rule_id": "TRULE-method-order",
        "observation_ids": ["TOBS-method-order"],
        "grounding_kind": "semantic_dossier",
        "rule_kind": "candidate_pattern",
        "candidate_transfer": "Place the bounded object before mechanism detail.",
        "suggested_disposition": "adopted",
        "origin": "model-proposed",
        "limitation": "Applies only to SCOPE-demo method explanation.",
        "dependency_fingerprint": "",
        "source_freshness": "verified_local_current",
        "application_snapshot": {
            "affected_scope_ids": ["SCOPE-demo"],
            "surface": "method paragraph sequence",
            "resolution": "confirmed",
            "disposition": "adopted",
            "gate_category": "not_applicable",
            "decision_id": "none",
            "decision_pointer": "none",
            "public_projection_pointer": "03_WRITING_STRUCTURE.md#Template Rule Projection",
        },
    }
    transfer_rule["dependency_fingerprint"] = rule_dependency_fingerprint(
        transfer_rule["observation_ids"], [observation], [document]
    )
    payload = {
        "schema": "yxj-template-semantic-dossier/1.0",
        "dossier_id": "TSD-fixture",
        "workspace_schema": "0.3",
        "design_question": design_question,
        "scope_ids": ["SCOPE-demo"],
        "analysis_context": {
            "method": "model_semantic_deep_reading",
            "agent_identity": "codex-test-agent",
            "model_identity": "unavailable",
            "prompt_identity": "unavailable",
            "access_limitations": "Only the declared derivative was read.",
            "generic_knowledge_fallback": "not_used",
            "uncertainty_note": "Transfer remains a design proposal.",
        },
        "documents": [document],
        "observations": [observation],
        "transfer_rules": [transfer_rule],
        "updated_at": "2026-07-15T00:00:00Z",
    }
    hidden = workspace / ".yxj-paper-os" / "template-analysis"
    hidden.mkdir(parents=True)
    (hidden / "semantic-dossier.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    append_table_row(
        workspace,
        "01_MATERIALS_INVENTORY.md",
        "Template Design Sources",
        "| TPL-method | exemplar | How should the method explanation stage its bounded contribution? | sources/template.md | owner_derivative | sources/template.md | "
        + source_sha
        + " | .yxj-paper-os/template-analysis/semantic-dossier.json#TPL-method | design_only | none |",
    )
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Template Rule Projection",
        "| TRULE-method-order | semantic_dossier | .yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-method-order | candidate_pattern | SCOPE-demo | method paragraph sequence | Place the bounded object before mechanism detail. | adopted | model-proposed | confirmed | adopted | none | Applies only to SCOPE-demo method explanation. | verified_local_current |",
    )
    return ".yxj-paper-os/template-analysis/semantic-dossier.json#TPL-method"


def install_quantitative_rule(workspace: Path) -> str:
    hidden = workspace / ".yxj-paper-os" / "template-analysis"
    hidden.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "template-corpus-normalized/1.0",
        "analysis_id": "analysis-fixture",
        "corpus_id": "corpus-fixture",
        "design_metric_ids": ["structure.paragraph_count"],
        "effective_analysis_mode": "case_set",
    }
    profile = {
        "schema": "template-design-profile/1.0",
        "analysis_id": "analysis-fixture",
        "corpus_id": "corpus-fixture",
        "entries": [
            {
                "profile_id": "corpus:structure.paragraph_count",
                "metric_ids": ["structure.paragraph_count"],
                "partition": "overall",
                "valid_n": 2,
                "missingness": 0,
                "candidate_action": "adapt",
                "uncertainty": {
                    "effective_analysis_mode": "case_set",
                    "metric_effective_analysis_mode": "case_set",
                    "comparable_stratum": True,
                },
            }
        ],
    }
    (hidden / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (hidden / "design-profile.json").write_text(json.dumps(profile), encoding="utf-8")
    pointer = ".yxj-paper-os/template-analysis/design-profile.json#entries[0]"
    append_table_row(
        workspace,
        "03_WRITING_STRUCTURE.md",
        "Template Rule Projection",
        f"| TRULE-quant | quantitative_analysis | {pointer} | soft_band | SCOPE-demo | paragraph rhythm | Preserve the declared case-set observation as a watch-only design input | adapted | model-proposed | candidate | candidate | none | The metric is descriptive and cannot imply semantic quality | verified_local_current |",
    )
    return pointer


class DetailedValidatorTests(unittest.TestCase):
    maxDiff = None

    def workspace(self, root: str, fixture: Path = DETAILED) -> Path:
        return copy_fixture(fixture, Path(root))

    def test_canonical_detailed_fixture_is_ready_without_hidden_analysis(self) -> None:
        self.assertEqual(validate_workspace(DETAILED, require_handoff=True), [])
        report = validate_workspace_report(DETAILED, require_handoff=True)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_schema_branches_are_single_bounded_diagnostics(self) -> None:
        cases = {
            "legacy": (LEGACY, None, "SCHEMA_LEGACY_02"),
            "missing": (
                DETAILED,
                ("- Workspace schema version: 0.3", "- Schema declaration omitted"),
                "SCHEMA_MISSING",
            ),
            "invalid": (
                DETAILED,
                ("Workspace schema version: 0.3", "Workspace schema version: 0.x"),
                "SCHEMA_INVALID",
            ),
            "unsupported": (
                DETAILED,
                ("Workspace schema version: 0.3", "Workspace schema version: 0.4"),
                "SCHEMA_UNSUPPORTED",
            ),
        }
        for name, (fixture, mutation, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp, fixture)
                if mutation:
                    replace(workspace, "00_DIMENSION_INDEX.md", *mutation)
                errors = validate_workspace(workspace, require_handoff=True)
                self.assertEqual(len(errors), 1, errors)
                self.assertTrue(errors[0].startswith(f"{expected}:"), errors)

    def test_validator_is_read_only_for_all_schema_branches(self) -> None:
        cases = {
            "current": (DETAILED, None),
            "legacy": (LEGACY, None),
            "missing": (
                DETAILED,
                ("- Workspace schema version: 0.3", "- Schema declaration omitted"),
            ),
            "unsupported": (
                DETAILED,
                ("Workspace schema version: 0.3", "Workspace schema version: 0.4"),
            ),
        }
        for name, (fixture, mutation) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp, fixture)
                if mutation:
                    replace(workspace, "00_DIMENSION_INDEX.md", *mutation)
                before = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                validate_workspace_report(workspace, require_handoff=True)
                after = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(after, before)

    def test_initialized_templates_cannot_pass_as_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "initialized"
            shutil.copytree(ROOT / "assets" / "templates", workspace)
            self.assertNotEqual(validate_workspace(workspace, require_handoff=True), [])

    def test_section_paragraph_ownership_and_adjacency_are_checked(self) -> None:
        cases = {
            "duplicate section": (
                "03_WRITING_STRUCTURE.md",
                "| SEC-method | SCOPE-demo | 1 |",
                "| SEC-method | SCOPE-demo | 1 |",
                "SECTION_OWNERSHIP",
                True,
            ),
            "unknown section": (
                "03_WRITING_STRUCTURE.md",
                "| PAR-claim | SCOPE-demo | SEC-method | 2 |",
                "| PAR-claim | SCOPE-demo | SEC-missing | 2 |",
                "PARAGRAPH_OWNERSHIP",
                False,
            ),
            "duplicate paragraph order": (
                "03_WRITING_STRUCTURE.md",
                "| PAR-claim | SCOPE-demo | SEC-method | 2 |",
                "| PAR-claim | SCOPE-demo | SEC-method | 1 |",
                "PARAGRAPH_SEQUENCE",
                False,
            ),
            "bad adjacency": (
                "03_WRITING_STRUCTURE.md",
                "| PAR-context | SCOPE-demo | SEC-method | 1 | Define",
                "| PAR-context | SCOPE-demo | SEC-method | 1 | Define",
                "PARAGRAPH_SEQUENCE",
                False,
            ),
        }
        for name, (filename, old, new, expected, append_duplicate) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                if name == "bad adjacency":
                    replace(
                        workspace, filename, "| none | PAR-claim |", "| none | none |"
                    )
                elif append_duplicate:
                    path = workspace / filename
                    text = path.read_text(encoding="utf-8")
                    line = next(
                        line for line in text.splitlines() if line.startswith(old)
                    )
                    anchor = "\n## Paragraph Map"
                    path.write_text(
                        text.replace(anchor, f"\n{line}{anchor}", 1), encoding="utf-8"
                    )
                else:
                    replace(workspace, filename, old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_payload_coverage_and_reference_domains_are_checked(self) -> None:
        cases = {
            "orphan": ("PAR-context", "PAR-orphan", "PARAGRAPH_COVERAGE"),
            "unknown claim": (
                "C-demo | M-evidence",
                "C-missing | M-evidence",
                "PARAGRAPH_REFERENCE",
            ),
            "template as evidence": (
                "M-evidence | The comparison",
                "TPL-evidence | The comparison",
                "TEMPLATE_FIREWALL",
            ),
            "bare none rationale": (
                "The comparison may not exceed C-demo or M-evidence",
                "none",
                "ABSENCE_CONTRACT",
            ),
        }
        for name, (old, new, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "03_WRITING_STRUCTURE.md", old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_important_paragraph_and_frame_relations_are_checked(self) -> None:
        cases = {
            "unknown paragraph": (
                "| PAR-claim | Claim and visual",
                "| PAR-missing | Claim and visual",
                "FRAME_REFERENCE",
            ),
            "unknown frame": (
                "FRM-claim-1;FRM-claim-2",
                "FRM-missing",
                "FRAME_REFERENCE",
            ),
            "duplicate order": (
                "| FRM-claim-2 | PAR-claim | 2 |",
                "| FRM-claim-2 | PAR-claim | 1 |",
                "FRAME_REFERENCE",
            ),
            "bad previous": (
                "| FRM-claim-1 | none | No caption",
                "| none | none | No caption",
                "FRAME_REFERENCE",
            ),
        }
        for name, (old, new, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "03_WRITING_STRUCTURE.md", old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_sentence_like_frame_is_warning_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "[bounded comparison context] -> [M-evidence observation slot] -> [C-demo ceiling]",
                "The evidence clearly establishes the bounded comparison and closes the argument.",
            )
            report = validate_workspace_report(workspace)
            self.assertEqual(report.errors, [])
            self.assertTrue(
                any(
                    item.startswith("PROSE_BOUNDARY_WARNING:")
                    for item in report.warnings
                )
            )
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(workspace)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Design pack validation warnings:", result.stderr)
            self.assertIn("Structural design-pack validation passed", result.stdout)

    def test_seven_surface_manifest_and_counts_match_authority(self) -> None:
        cases = {
            "missing surface": (
                "| soft_budgets | SCOPE-demo",
                "| extra_surface | SCOPE-demo",
                "DETAILED_SURFACE_COVERAGE",
            ),
            "inflated count": (
                "| surface_language_contract | SCOPE-demo | satisfied | 1 |",
                "| surface_language_contract | SCOPE-demo | satisfied | 2 |",
                "DETAILED_SURFACE_COVERAGE",
            ),
            "contradictory na": (
                "| visual_caption_blueprint | SCOPE-demo | satisfied | 1 | 03_WRITING_STRUCTURE.md#Visual Blueprint |",
                "| visual_caption_blueprint | SCOPE-demo | not_applicable | 0 | none |",
                "DETAILED_SURFACE_COVERAGE",
            ),
        }
        for name, (old, new, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "04_WRITING_DESIGN_PACK.md", old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_template_handling_truth_table_and_firewall(self) -> None:
        invalid_rows = {
            "unknown mode": "| SCOPE-demo | semantic_magic | none | none | none | design_only | rationale | none |",
            "quant with semantic": "| SCOPE-demo | quantitative_only | dossier#x | .yxj-paper-os/template-analysis/design-profile.json#entries | none | design_only | measurable question | none |",
            "na with pointer": "| SCOPE-demo | not_applicable | dossier#x | none | none | design_only | irrelevant | none |",
            "firewall": "| SCOPE-demo | not_applicable | none | none | none | scientific_evidence | irrelevant | none |",
        }
        original = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
        for name, row in invalid_rows.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "04_WRITING_DESIGN_PACK.md", original, row)
                expected = (
                    "TEMPLATE_FIREWALL"
                    if name == "firewall"
                    else "TEMPLATE_RULE_INCOMPATIBLE"
                )
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_template_handling_and_handoff_cardinality_are_exact(self) -> None:
        cases = {
            "template duplicate": (
                "## Template Source Firewall",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | duplicate | none |\n\n## Template Source Firewall",
                "TEMPLATE_HANDLING_CARDINALITY",
            ),
            "handoff duplicate": (None, None, "HANDOFF_SCOPE_CARDINALITY"),
        }
        for name, (old, new, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                path = workspace / "04_WRITING_DESIGN_PACK.md"
                if name == "handoff duplicate":
                    text = path.read_text(encoding="utf-8")
                    row = next(
                        line
                        for line in text.splitlines()
                        if line.startswith("| SCOPE-demo | 00_DIMENSION")
                    )
                    path.write_text(text + row + "\n", encoding="utf-8")
                else:
                    replace(workspace, path.name, old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_missing_and_extra_04_scope_rows_use_stable_cardinality_codes(self) -> None:
        template_row = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
        handoff_row = "| SCOPE-demo | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | Do not invent science exceed C-demo require template analysis or copy frames as manuscript sentences | Use 03 as the detailed authority and this row only as the compact handoff |"
        cases = (
            ("template-missing", template_row, "", "TEMPLATE_HANDLING_CARDINALITY"),
            (
                "template-extra",
                template_row,
                template_row
                + "\n| SCOPE-extra | not_applicable | none | none | none | design_only | extra scope | none |",
                "TEMPLATE_HANDLING_CARDINALITY",
            ),
            ("handoff-missing", handoff_row, "", "HANDOFF_SCOPE_CARDINALITY"),
            (
                "handoff-extra",
                handoff_row,
                handoff_row
                + "\n| SCOPE-extra | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | none | prohibit | note |",
                "HANDOFF_SCOPE_CARDINALITY",
            ),
        )
        for name, old, new, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "04_WRITING_DESIGN_PACK.md", old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_scoped_handoff_cannot_copy_or_disagree_on_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| Scope ID | 00 scope-row pointer | Detailed coverage pointer | Output pointer | Active blocker IDs | Downstream prohibitions | Handoff note |",
                "| Scope ID | Readiness | 00 scope-row pointer | Detailed coverage pointer | Output pointer | Active blocker IDs | Downstream prohibitions | Handoff note |",
            )
            self.assertIn(
                "HANDOFF_READINESS_DUPLICATED", codes(validate_workspace(workspace))
            )
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none |",
                "| SCOPE-demo | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | none |",
            )
            self.assertIn(
                "HANDOFF_READINESS_DUPLICATED", codes(validate_workspace(workspace))
            )

    def test_owner_gate_resolution_and_routine_no_decision_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | scientific_commitment |",
            )
            replace(workspace, "00_PROJECT_ROUTE.md", "| confirmed |", "| unresolved |")
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | argument_spine |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "Use the synthetic generic route for contract characterization",
                "Approve the whole design pack before any bounded work",
            )
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))

    def test_all_four_owner_gate_categories_block_when_unresolved(self) -> None:
        for gate in (
            "scientific_commitment",
            "argument_spine",
            "material_local_tradeoff",
            "deliberate_divergence",
        ):
            with self.subTest(gate=gate), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(
                    workspace,
                    "00_PROJECT_ROUTE.md",
                    "| DEC-route | not_applicable |",
                    f"| DEC-route | {gate} |",
                )
                replace(
                    workspace,
                    "00_PROJECT_ROUTE.md",
                    "| confirmed |",
                    "| unresolved |",
                )
                errors = validate_workspace(workspace)
                self.assertIn("OWNER_GATE", codes(errors), errors)

    def test_all_four_owner_gate_categories_accept_grounded_confirmed_state(
        self,
    ) -> None:
        for gate in (
            "scientific_commitment",
            "argument_spine",
            "material_local_tradeoff",
            "deliberate_divergence",
        ):
            with self.subTest(gate=gate), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(
                    workspace,
                    "00_PROJECT_ROUTE.md",
                    "| DEC-route | not_applicable |",
                    f"| DEC-route | {gate} |",
                )
                replace(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "| not_applicable | none | not_applicable: evidence ceiling and clause roles are already fixed | none |",
                    f"| {gate} | DEC-route | Owner-grounded decision is confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                )
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | DEC-route |",
                    f"| SCOPE-demo | {gate} | DEC-route |",
                )
                if gate == "deliberate_divergence":
                    append_table_row(
                        workspace,
                        "03_WRITING_STRUCTURE.md",
                        "Template Rule Projection",
                        "| TRULE-diverge | official_constraint | M-method | candidate_pattern | SCOPE-demo | presentation boundary | Deliberately diverge from the candidate presentation pattern | deliberate_divergence | artifact-observed | confirmed | deliberate_divergence | DEC-route | Applies only to the confirmed presentation tradeoff | verified_local_current |",
                    )
                    activate_rule_coverage(workspace, 1)
                self.assertEqual(validate_workspace(workspace), [])

    def test_semantic_primary_mode_validates_dossier_and_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            activate_rule_coverage(workspace, 1)
            original = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
            replacement = f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | none | design_only | Semantic reading answers the declared method-order question | none |"
            replace(workspace, "04_WRITING_DESIGN_PACK.md", original, replacement)
            self.assertEqual(validate_workspace(workspace), [])
            dossier = (
                workspace / ".yxj-paper-os/template-analysis/semantic-dossier.json"
            )
            payload = json.loads(dossier.read_text(encoding="utf-8"))
            payload["documents"][0]["design_only_state"] = "scientific_evidence"
            dossier.write_text(json.dumps(payload), encoding="utf-8")
            self.assertIn("DOSSIER_FIREWALL", codes(validate_workspace(workspace)))

    def test_quantitative_only_mode_validates_identity_metric_and_missingness(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            quantitative_pointer = install_quantitative_rule(workspace)
            activate_rule_coverage(workspace, 1)
            original = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
            replacement = f"| SCOPE-demo | quantitative_only | none | {quantitative_pointer} | none | design_only | Only the declared measurable paragraph-count question is used | none |"
            replace(workspace, "04_WRITING_DESIGN_PACK.md", original, replacement)
            self.assertEqual(validate_workspace(workspace), [])
            profile = workspace / ".yxj-paper-os/template-analysis/design-profile.json"
            payload = json.loads(profile.read_text(encoding="utf-8"))
            payload["analysis_id"] = "mixed-analysis"
            profile.write_text(json.dumps(payload), encoding="utf-8")
            errors = validate_workspace(workspace)
            self.assertIn("TEMPLATE_RULE_INCOMPATIBLE", codes(errors), errors)
            self.assertTrue(any("SCOPE-demo" in error for error in errors), errors)

    def test_semantic_plus_quantitative_requires_separate_typed_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            quantitative_pointer = install_quantitative_rule(workspace)
            activate_rule_coverage(workspace, 2)
            original = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
            replacement = f"| SCOPE-demo | semantic_plus_quantitative | {semantic_pointer} | {quantitative_pointer} | none | design_only | Semantic reading remains primary and the metric answers only paragraph count | none |"
            replace(workspace, "04_WRITING_DESIGN_PACK.md", original, replacement)
            self.assertEqual(validate_workspace(workspace), [])
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| TRULE-quant | quantitative_analysis |",
                "| TRULE-quant | semantic_dossier |",
            )
            self.assertIn(
                "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
            )

    def test_generic_fallback_mode_resolves_registry_heading_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            lens = ROOT / "references" / "lenses" / "argument-language-visual.md"
            version = "0.3.0+codex.test"
            freshness = (
                f"plugin:{version}@sha256:"
                + hashlib.sha256(lens.read_bytes()).hexdigest()
            )
            pointer = "lens:argument-language-visual#sufficiency-predicates"
            append_table_row(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Template Rule Projection",
                f"| TRULE-fallback | generic_fallback | {pointer} | candidate_pattern | SCOPE-demo | paragraph transition | Use the generic transition checklist only as labeled fallback guidance | none | model-proposed | candidate | candidate | none | No template observation is claimed | {freshness} |",
            )
            activate_rule_coverage(workspace, 1)
            original = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
            replacement = f"| SCOPE-demo | generic_fallback | none | none | {pointer} | design_only | Grounded template evidence is unavailable so labeled lens guidance is used | none |"
            replace(workspace, "04_WRITING_DESIGN_PACK.md", original, replacement)
            with patch("verify_design_pack._plugin_version", return_value=version):
                self.assertEqual(validate_workspace(workspace), [])
                replace(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    freshness,
                    freshness[:-1] + ("0" if freshness[-1] != "0" else "1"),
                )
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )

    def test_generic_fallback_rejects_identity_heading_and_version_drift(self) -> None:
        lens = ROOT / "references" / "lenses" / "argument-language-visual.md"
        version = "0.3.0+codex.test"
        digest = hashlib.sha256(lens.read_bytes()).hexdigest()
        cases = {
            "unknown lens": (
                "lens:not-a-real-lens#sufficiency-predicates",
                f"plugin:{version}@sha256:{digest}",
            ),
            "missing heading": (
                "lens:argument-language-visual#not-a-real-heading",
                f"plugin:{version}@sha256:{digest}",
            ),
            "h1 only": (
                "lens:argument-language-visual#argument-language-and-visual",
                f"plugin:{version}@sha256:{digest}",
            ),
            "version mismatch": (
                "lens:argument-language-visual#sufficiency-predicates",
                f"plugin:0.3.1+codex.other@sha256:{digest}",
            ),
        }
        for name, (pointer, freshness) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                append_table_row(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "Template Rule Projection",
                    f"| TRULE-fallback | generic_fallback | {pointer} | candidate_pattern | SCOPE-demo | paragraph transition | Use labeled fallback guidance | none | model-proposed | candidate | candidate | none | No template observation is claimed | {freshness} |",
                )
                activate_rule_coverage(workspace, 1)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    f"| SCOPE-demo | generic_fallback | none | none | {pointer} | design_only | Labeled fallback is the only active design input | none |",
                )
                with patch("verify_design_pack._plugin_version", return_value=version):
                    self.assertIn(
                        "TEMPLATE_RULE_INCOMPATIBLE",
                        codes(validate_workspace(workspace)),
                    )

    def test_official_constraint_grounding_uses_qualifying_material(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            append_table_row(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Template Rule Projection",
                "| TRULE-official | official_constraint | M-method | hard_constraint | SCOPE-demo | presentation boundary | Preserve the declared route-active presentation boundary | none | artifact-observed | confirmed | adopted | none | Applies only while the current route remains active | verified_local_current |",
            )
            activate_rule_coverage(workspace, 1)
            self.assertEqual(validate_workspace(workspace), [])
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| TRULE-official | official_constraint | M-method | hard_constraint |",
                "| TRULE-official | semantic_dossier | M-method | hard_constraint |",
            )
            self.assertIn(
                "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
            )

    def test_grounding_kind_compatibility_and_cross_kind_freshness(self) -> None:
        rows = {
            "official wrong pointer": "| TRULE-bad | official_constraint | .yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-x | hard_constraint | SCOPE-demo | route boundary | Preserve boundary | none | artifact-observed | confirmed | adopted | none | Bounded | verified_local_current |",
            "semantic hard constraint": "| TRULE-bad | semantic_dossier | .yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-x | hard_constraint | SCOPE-demo | paragraph order | Preserve order | none | model-proposed | candidate | candidate | none | Bounded | recorded_at_access |",
            "quantitative semantic pattern": "| TRULE-bad | quantitative_analysis | .yxj-paper-os/template-analysis/design-profile.json#entries[0] | candidate_pattern | SCOPE-demo | paragraph rhythm | Preserve rhythm | adapted | model-proposed | candidate | candidate | none | Bounded | verified_local_current |",
            "generic sequence ordinary freshness": "| TRULE-bad | generic_fallback | lens:argument-language-visual#sufficiency-predicates | sequence | SCOPE-demo | paragraph transition | Preserve transition | none | model-proposed | candidate | candidate | none | Bounded | verified_local_current |",
            "nonfallback plugin freshness": "| TRULE-bad | official_constraint | M-method | hard_constraint | SCOPE-demo | route boundary | Preserve boundary | none | artifact-observed | confirmed | adopted | none | Bounded | plugin:0.3.0@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |",
        }
        for name, row in rows.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                append_table_row(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "Template Rule Projection",
                    row,
                )
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )

    def test_semantic_modes_allow_generic_only_for_named_uncovered_surface(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            activate_rule_coverage(workspace, 1)
            original = "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |"
            replacement = f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | lens:argument-language-visual#sufficiency-predicates | design_only | Generic guidance is also useful | none |"
            replace(workspace, "04_WRITING_DESIGN_PACK.md", original, replacement)
            self.assertIn(
                "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
            )

    def test_selective_stale_diagnostic_names_only_affected_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            append_table_row(
                workspace,
                "00_DIMENSION_INDEX.md",
                "Writing Scopes",
                "| SCOPE-other | Unrelated deferred surface | Unrelated output | blocked | M-evidence | none | M-evidence | Recheck unrelated evidence | none |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| current | Block PAR-claim",
                "| stale | Block PAR-claim",
            )
            errors = validate_workspace(workspace)
            related = [
                error for error in errors if error.startswith("DEPENDENCY_STALE:")
            ]
            self.assertTrue(related, errors)
            self.assertTrue(all("SCOPE-demo" in error for error in related), related)
            self.assertTrue(
                all("SCOPE-other" not in error for error in related), related
            )

    def test_malformed_utf8_is_total_and_localized(self) -> None:
        cases = ("index", "public", "dossier", "analyzer")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                if case == "index":
                    target = workspace / "00_DIMENSION_INDEX.md"
                elif case == "public":
                    target = workspace / "03_WRITING_STRUCTURE.md"
                elif case == "dossier":
                    install_semantic_rule(workspace)
                    activate_rule_coverage(workspace, 1)
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                        "| SCOPE-demo | semantic_primary | .yxj-paper-os/template-analysis/semantic-dossier.json#TPL-method | none | none | design_only | Semantic evidence governs the method paragraph sequence | none |",
                    )
                    target = (
                        workspace
                        / ".yxj-paper-os/template-analysis/semantic-dossier.json"
                    )
                else:
                    pointer = install_quantitative_rule(workspace)
                    activate_rule_coverage(workspace, 1)
                    replace(
                        workspace,
                        "04_WRITING_DESIGN_PACK.md",
                        "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                        f"| SCOPE-demo | quantitative_only | none | {pointer} | none | design_only | Quantitative observation is the only active design input | none |",
                    )
                    target = (
                        workspace
                        / ".yxj-paper-os/template-analysis/design-profile.json"
                    )
                target.write_bytes(b"\xff\xfeinvalid")
                report = validate_workspace_report(workspace, require_handoff=True)
                self.assertTrue(report.errors)
                if case == "index":
                    self.assertEqual(len(report.errors), 1, report.errors)
                if case == "dossier":
                    self.assertTrue(
                        any(
                            "TRULE-method-order" in error and "SCOPE-demo" in error
                            for error in report.errors
                        ),
                        report.errors,
                    )
                result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(workspace),
                        "--require-handoff",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_malformed_active_json_shapes_return_diagnostics_not_exceptions(
        self,
    ) -> None:
        for case in ("null collections", "malformed nested ownership"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                semantic_pointer = install_semantic_rule(workspace)
                activate_rule_coverage(workspace, 1)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | none | design_only | Semantic reading governs method paragraph sequence | none |",
                )
                dossier_path = (
                    workspace / ".yxj-paper-os/template-analysis/semantic-dossier.json"
                )
                dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
                if case == "null collections":
                    dossier["observations"] = None
                    dossier["transfer_rules"] = None
                else:
                    dossier["transfer_rules"][0]["observation_ids"] = [{}]
                    dossier["transfer_rules"][0]["application_snapshot"][
                        "affected_scope_ids"
                    ] = None
                dossier_path.write_text(json.dumps(dossier), encoding="utf-8")
                report = validate_workspace_report(workspace)
                self.assertTrue(report.errors)
                self.assertIn("TEMPLATE_RULE_INCOMPATIBLE", codes(report.errors))

    def test_authoritative_heading_schema_and_owner_summary_cardinality(self) -> None:
        cases = {
            "duplicate heading": (
                "03_WRITING_STRUCTURE.md",
                "\n## Section Map\n| Section ID | Scope ID | Sequence | Job | Reader state in | Reader state out | Input IDs | Output promise | Evidence/visual obligations | Forbidden content |\n| SEC-shadow | SCOPE-demo | 1 | shadow | in | out | M-method | promise | obligation | forbidden |\n",
                "TABLE_CONTRACT",
            ),
            "copied schema": (
                "04_WRITING_DESIGN_PACK.md",
                "\n- Workspace schema version: 0.3\n",
                "SCHEMA_INVALID",
            ),
            "duplicate owner summary": (
                "04_WRITING_DESIGN_PACK.md",
                "\n| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |\n",
                "OWNER_GATE",
            ),
        }
        for name, (filename, addition, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                if name == "duplicate owner summary":
                    append_table_row(
                        workspace,
                        filename,
                        "Owner Gate Resolution Summary",
                        addition.strip(),
                    )
                else:
                    path = workspace / filename
                    path.write_text(
                        path.read_text(encoding="utf-8") + addition, encoding="utf-8"
                    )
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_record_and_hidden_pointer_resolution_and_scientific_firewall(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| confirmed | M-missing |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| confirmed | M-missing | none |",
            )
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "semantic-dossier.json#TPL-method",
                "semantic-dossier.json#TPL-ghost",
            )
            self.assertIn(
                "TEMPLATE_PROJECTION_MISMATCH", codes(validate_workspace(workspace))
            )
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory | SCOPE-demo | available | artifact-observed | confirmed | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory | SCOPE-demo | available | artifact-observed | confirmed | TPL-method |",
            )
            self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

    def test_budget_pointer_domains_resolve_not_just_match_grammar(self) -> None:
        cases = {
            "semantic": (
                "semantic_dossier",
                ".yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-missing",
            ),
            "quantitative": (
                "quantitative_analysis",
                ".yxj-paper-os/template-analysis/design-profile.json#entries[0]",
            ),
            "generic": ("generic_fallback", "lens:not-a-real-lens#missing-heading"),
            "repository": ("repository_grounding", "M-missing"),
        }
        for name, (kind, pointer) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                append_table_row(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "Grounded Soft Budgets",
                    f"| BUD-missing | SCOPE-demo | paragraph rhythm | bounded order | {kind} | {pointer} | watch-only ordering | candidate | Keep the basis explicitly bounded | This is not a hard constraint |",
                )
                self.assertIn("BUDGET_CONTRACT", codes(validate_workspace(workspace)))

    def test_typed_list_grammar_is_shared_by_rules_and_scope_lists(self) -> None:
        for malformed in (
            "M-method;",
            ";M-method",
            "M-method;;M-method",
            "M-method;M-method",
        ):
            with (
                self.subTest(malformed=malformed),
                tempfile.TemporaryDirectory() as temp,
            ):
                workspace = self.workspace(temp)
                append_table_row(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "Template Rule Projection",
                    f"| TRULE-official | official_constraint | {malformed} | hard_constraint | SCOPE-demo | route boundary | Preserve the bounded official constraint | none | artifact-observed | confirmed | adopted | none | Applies while route is current | verified_local_current |",
                )
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "M-method;M-evidence;C-demo;VIS-figure",
                "M-method; M-evidence; C-demo; VIS-figure",
            )
            self.assertEqual(validate_workspace(workspace), [])

    def test_edge_state_and_direct_endpoint_count_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| current | Block PAR-claim",
                "| stale | Block PAR-claim",
            )
            self.assertIn("DEPENDENCY_STALE", codes(validate_workspace(workspace)))
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            append_table_row(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Cross-Surface Traceability",
                "| EDGE-extra | M-evidence | qualifies | C-demo | Scientific evidence-to-claim closure | current | Block the claim until the direct evidence relation is rechecked |",
            )
            self.assertIn(
                "DETAILED_SURFACE_COVERAGE", codes(validate_workspace(workspace))
            )

    def test_language_and_visual_targets_resolve_in_declared_domains(self) -> None:
        cases = {
            "language grounding": (
                "No proves guarantees novel optimal or venue-fit wording | M-method;M-evidence;C-demo |",
                "No proves guarantees novel optimal or venue-fit wording | M-method;M-evidence;C-missing |",
                "LANGUAGE_CONTRACT",
            ),
            "visual paragraph": (
                "| VIS-figure | SCOPE-demo | PAR-claim |",
                "| VIS-figure | SCOPE-demo | PAR-missing |",
                "VISUAL_CONTRACT",
            ),
        }
        for name, (old, new, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "03_WRITING_STRUCTURE.md", old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_quantitative_artifact_fields_and_exact_action_mapping_are_required(
        self,
    ) -> None:
        mutations = {
            "analysis_id": lambda profile: profile.pop("analysis_id"),
            "corpus_id": lambda profile: profile.pop("corpus_id"),
            "metric_ids": lambda profile: profile["entries"][0].pop("metric_ids"),
            "unrelated metric": lambda profile: profile["entries"][0].update(
                metric_ids=["structure.unrelated"]
            ),
            "partition": lambda profile: profile["entries"][0].update(partition=""),
            "uncertainty": lambda profile: profile["entries"][0].pop("uncertainty"),
            "action": lambda profile: profile["entries"][0].update(
                candidate_action="magic"
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                pointer = install_quantitative_rule(workspace)
                activate_rule_coverage(workspace, 1)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    f"| SCOPE-demo | quantitative_only | none | {pointer} | none | design_only | Quantitative observation is the only active design input | none |",
                )
                profile_path = (
                    workspace / ".yxj-paper-os/template-analysis/design-profile.json"
                )
                profile = json.loads(profile_path.read_text(encoding="utf-8"))
                mutate(profile)
                profile_path.write_text(json.dumps(profile), encoding="utf-8")
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            pointer = install_quantitative_rule(workspace)
            activate_rule_coverage(workspace, 1)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | quantitative_only | none | {pointer} | none | design_only | Quantitative observation is the only active design input | none |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| adapted | model-proposed |",
                "| candidate | model-proposed |",
            )
            self.assertIn(
                "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
            )

    def test_all_analyzer_actions_project_exact_suggestions_only(self) -> None:
        mappings = {
            "follow": "adopted",
            "adapt": "adapted",
            "deliberate_divergence": "deliberate_divergence",
            "not_applicable": "not_applicable",
        }
        for action, suggestion in mappings.items():
            with self.subTest(action=action), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                pointer = install_quantitative_rule(workspace)
                activate_rule_coverage(workspace, 1)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    f"| SCOPE-demo | quantitative_only | none | {pointer} | none | design_only | Quantitative observation is the only active design input | none |",
                )
                profile_path = (
                    workspace / ".yxj-paper-os/template-analysis/design-profile.json"
                )
                profile = json.loads(profile_path.read_text(encoding="utf-8"))
                profile["entries"][0]["candidate_action"] = action
                profile_path.write_text(json.dumps(profile), encoding="utf-8")
                replace(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "| adapted | model-proposed |",
                    f"| {suggestion} | model-proposed |",
                )
                self.assertEqual(validate_workspace(workspace), [])

    def test_referenced_jsonl_validates_every_record_identity_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            old_pointer = install_quantitative_rule(workspace)
            new_pointer = ".yxj-paper-os/template-analysis/paper-metrics.jsonl#rows"
            activate_rule_coverage(workspace, 1)
            replace(workspace, "03_WRITING_STRUCTURE.md", old_pointer, new_pointer)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | quantitative_only | none | {new_pointer} | none | design_only | Quantitative observations are the only active design input | none |",
            )
            base = {
                "schema": "template-paper-metrics/1.0",
                "analysis_id": "analysis-fixture",
                "corpus_id": "corpus-fixture",
                "metric_ids": ["structure.paragraph_count"],
                "partition": "overall",
                "valid_n": 2,
                "missingness": 0,
                "candidate_action": "adapt",
                "uncertainty": {
                    "effective_analysis_mode": "case_set",
                    "metric_effective_analysis_mode": "case_set",
                    "comparable_stratum": True,
                },
            }
            jsonl = workspace / ".yxj-paper-os/template-analysis/paper-metrics.jsonl"
            jsonl.write_text(
                "\n".join(
                    json.dumps(item)
                    for item in (base, {**base, "analysis_id": "mixed"})
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertIn(
                "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
            )

    def test_modes_are_closed_over_same_scope_active_rule_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            pointer = install_quantitative_rule(workspace)
            activate_rule_coverage(workspace, 2)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | quantitative_only | none | {pointer} | none | design_only | Quantitative observation is the only declared input | none |",
            )
            self.assertIn(
                "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
            )

    def test_semantic_generic_mode_names_the_actual_generic_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            lens = ROOT / "references" / "lenses" / "argument-language-visual.md"
            version = "0.3.0+codex.test"
            freshness = f"plugin:{version}@sha256:{hashlib.sha256(lens.read_bytes()).hexdigest()}"
            pointer = "lens:argument-language-visual#sufficiency-predicates"
            append_table_row(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Template Rule Projection",
                f"| TRULE-fallback | generic_fallback | {pointer} | candidate_pattern | SCOPE-demo | paragraph transition | Use fallback guidance only for the uncovered paragraph transition | none | model-proposed | candidate | candidate | none | No semantic observation is claimed for this surface | {freshness} |",
            )
            activate_rule_coverage(workspace, 2)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | {pointer} | design_only | Semantic reading governs method order; paragraph transition is the uncovered generic surface | none |",
            )
            with patch("verify_design_pack._plugin_version", return_value=version):
                self.assertEqual(validate_workspace(workspace), [])
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "paragraph transition is the uncovered generic surface",
                    "an uncovered surface uses generic guidance",
                )
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )

    def test_triggered_owner_gate_rejects_model_projection_as_owner_answer(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | material_local_tradeoff |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| owner-stated | confirmed | 03_WRITING_STRUCTURE.md#Template Rule Projection |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| material_local_tradeoff | DEC-route | confirmed | 03_WRITING_STRUCTURE.md#Template Rule Projection |",
            )
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))

    def test_owner_resolution_does_not_relabel_model_proposed_rule_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            activate_rule_coverage(workspace, 1)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | none | design_only | Semantic reading governs method paragraph sequence | none |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | material_local_tradeoff |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| owner-stated | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| not_applicable | DEC-route | confirmed |",
                "| material_local_tradeoff | DEC-route | confirmed |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| adopted | none | Applies only to SCOPE-demo",
                "| adopted | DEC-route | Applies only to SCOPE-demo",
            )
            dossier_path = (
                workspace / ".yxj-paper-os/template-analysis/semantic-dossier.json"
            )
            dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
            snapshot = dossier["transfer_rules"][0]["application_snapshot"]
            snapshot.update(
                gate_category="material_local_tradeoff",
                decision_id="DEC-route",
                decision_pointer="00_PROJECT_ROUTE.md#Project Brief",
            )
            dossier_path.write_text(json.dumps(dossier), encoding="utf-8")
            self.assertEqual(validate_workspace(workspace), [])
            self.assertIn(
                "| model-proposed | confirmed |",
                (workspace / "03_WRITING_STRUCTURE.md").read_text(encoding="utf-8"),
            )

    def test_missing_payload_zero_paragraph_and_cross_scope_adjacency_fail(
        self,
    ) -> None:
        cases = (
            "duplicate paragraph",
            "missing payload",
            "zero paragraph",
            "cross-scope adjacency",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                path = workspace / "03_WRITING_STRUCTURE.md"
                text = path.read_text(encoding="utf-8")
                if case == "duplicate paragraph":
                    duplicate = next(
                        line
                        for line in text.splitlines()
                        if line.startswith("| PAR-context | SCOPE-demo | SEC-method |")
                    )
                    text = text.replace(
                        "\n## Paragraph Payload",
                        f"\n{duplicate}\n\n## Paragraph Payload",
                        1,
                    )
                    expected = "PARAGRAPH_OWNERSHIP"
                elif case == "missing payload":
                    text = (
                        "\n".join(
                            line
                            for line in text.splitlines()
                            if not line.startswith("| PAR-context | none | M-method |")
                        )
                        + "\n"
                    )
                    expected = "PARAGRAPH_COVERAGE"
                elif case == "zero paragraph":
                    text = (
                        "\n".join(
                            line
                            for line in text.splitlines()
                            if not line.startswith(
                                "| PAR-context | SCOPE-demo | SEC-method |"
                            )
                            and not line.startswith(
                                "| PAR-claim | SCOPE-demo | SEC-method |"
                            )
                        )
                        + "\n"
                    )
                    expected = "PARAGRAPH_COVERAGE"
                else:
                    text = text.replace(
                        "| none | PAR-claim |", "| none | PAR-other |", 1
                    )
                    text = text.replace(
                        "## Template Rule Projection",
                        "| EDGE-handoff | PAR-context | hands_off_to | PAR-other | Explicit cross-scope handoff | current | Recheck the declared handoff |\n\n## Template Rule Projection",
                        1,
                    )
                    expected = "PARAGRAPH_SEQUENCE"
                path.write_text(text, encoding="utf-8")
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_partial_scope_blockers_and_output_are_exactly_mirrored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_DIMENSION_INDEX.md",
                "| writer-ready | M-method;M-evidence;M-visual | REQ-detailed | none | none | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage |",
                "| partial | M-method;M-evidence;M-visual | REQ-detailed | M-evidence | Recheck the evidence boundary | none |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                "| confirmed | 00_PROJECT_ROUTE.md#Project Brief | M-evidence |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                "| design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | M-evidence |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | none | No unresolved record affects this scope |",
                "| SCOPE-demo | M-evidence | Evidence recheck remains active |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | Do not invent science",
                "| none | M-evidence | Do not invent science",
            )
            self.assertEqual(validate_workspace(workspace, require_handoff=True), [])
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| none | M-evidence | Do not invent science",
                "| M-missing | M-evidence | Do not invent science",
            )
            self.assertIn(
                "HANDOFF_SCOPE_CARDINALITY", codes(validate_workspace(workspace))
            )

    def test_all_nonready_states_share_the_same_authoritative_linkage(self) -> None:
        for readiness in ("partial", "blocked", "deferred"):
            with (
                self.subTest(readiness=readiness),
                tempfile.TemporaryDirectory() as temp,
            ):
                workspace = self.workspace(temp)
                replace(
                    workspace,
                    "00_DIMENSION_INDEX.md",
                    "| writer-ready | M-method;M-evidence;M-visual | REQ-detailed | none | none | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage |",
                    f"| {readiness} | M-method;M-evidence;M-visual | REQ-detailed | M-evidence | Recheck the evidence boundary | none |",
                )
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| confirmed | 00_PROJECT_ROUTE.md#Project Brief | none |",
                    "| confirmed | 00_PROJECT_ROUTE.md#Project Brief | M-evidence |",
                )
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    "| design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | M-evidence |",
                )
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | none | No unresolved record affects this scope |",
                    "| SCOPE-demo | M-evidence | Evidence recheck remains active |",
                )
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | none | Do not invent science",
                    "| none | M-evidence | Do not invent science",
                )
                self.assertEqual(
                    validate_workspace(workspace, require_handoff=True), []
                )

    def test_handoff_prose_cannot_embed_readiness_claims(self) -> None:
        for claim in (
            "This manifest declares the scope writer-ready for drafting",
            "This scope is partial and not ready for downstream drafting",
            "This scope remains blocked by evidence",
            "This scope is deferred until later",
        ):
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Use 03 as the detailed authority and this row only as the compact handoff",
                    claim,
                )
                self.assertIn(
                    "HANDOFF_READINESS_DUPLICATED", codes(validate_workspace(workspace))
                )

    def test_warning_matrix_is_warning_only(self) -> None:
        cases = {
            "short clause without slot": (
                "[bounded comparison context] -> [M-evidence observation slot] -> [C-demo ceiling]",
                "evidence then bounded claim",
            ),
            "polished proposition": (
                "Bind C-demo to M-evidence without adding magnitude or causality",
                "The evidence establishes the bounded comparison.",
            ),
            "polished local constraint": (
                "Use qualified comparison verbs and no causal verb",
                "Use qualified comparison verbs and avoid every causal verb.",
            ),
            "polished forbidden realization": (
                "No complete paste-ready academic sentence",
                "Do not write a complete paste-ready academic sentence.",
            ),
            "unpunctuated finite proposition": (
                "Bind C-demo to M-evidence without adding magnitude or causality",
                "The evidence establishes the bounded comparison",
            ),
            "realized caption": (
                "Identify variables evidence boundary and limitation; do not draft caption text",
                "Figure 1 shows the bounded comparison",
            ),
            "assembled paragraph": (
                "Bind C-demo to M-evidence without adding magnitude or causality",
                "Evidence is bounded. The comparison remains qualified. Scope is explicit.",
            ),
        }
        for name, (old, new) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(workspace, "03_WRITING_STRUCTURE.md", old, new)
                report = validate_workspace_report(workspace)
                self.assertEqual(report.errors, [])
                self.assertIn("PROSE_BOUNDARY_WARNING", codes(report.warnings))

    def test_warning_heuristic_avoids_placeholders_and_ambiguous_short_notes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Bind C-demo to M-evidence without adding magnitude or causality",
                "evidence then bounded claim",
            )
            report = validate_workspace_report(workspace)
            self.assertEqual(report.errors, [])
            self.assertEqual(report.warnings, [])
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Bind C-demo to M-evidence without adding magnitude or causality",
                "TODO",
            )
            report = validate_workspace_report(workspace)
            self.assertIn("ABSENCE_CONTRACT", codes(report.errors))
            self.assertNotIn("PROSE_BOUNDARY_WARNING", codes(report.warnings))

    def test_allowed_readiness_words_are_not_scope_readiness_assertions(self) -> None:
        for prose in (
            "Do not use partial evidence as a substitute for bounded support",
            "Do not cite blocked source paths as evidence",
            "Defer deferred citations to the citation pass",
            "This scope documents a blocked state transition in the controller",
            "This scope compares partial state observations from the artifact",
        ):
            with self.subTest(prose=prose), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Do not invent science exceed C-demo require template analysis or copy frames as manuscript sentences",
                    prose,
                )
                self.assertEqual(
                    validate_workspace(workspace, require_handoff=True), []
                )

    def test_totality_for_nul_paths_and_malformed_required_registries(self) -> None:
        path_cases = {
            "source": (
                "sources/template.md | owner_derivative",
                "bad\x00path | owner_derivative",
            ),
            "derivative": (
                "owner_derivative | sources/template.md |",
                "owner_derivative | bad\x00path |",
            ),
            "public path": (
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | path:bad\x00path |",
            ),
        }
        for name, (old, new) in path_cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                install_semantic_rule(workspace)
                replace(workspace, "01_MATERIALS_INVENTORY.md", old, new)
                before = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                report = validate_workspace_report(workspace, require_handoff=True)
                self.assertTrue(report.errors)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(workspace),
                        "--require-handoff",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                after = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(after, before)

        malformed_cases = {
            "missing requirement table": lambda workspace: replace(
                workspace,
                "00_DIMENSION_INDEX.md",
                "## Conditional Requirements",
                "## Conditional Requirementz",
            ),
            "unknown requirement": lambda workspace: replace(
                workspace,
                "00_DIMENSION_INDEX.md",
                "| REQ-detailed | none | none |",
                "| REQ-missing | none | none |",
            ),
            "invalid quantitative rule id": lambda workspace: (
                install_quantitative_rule(workspace),
                replace(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "| TRULE-quant |",
                    "| BAD-rule |",
                ),
            ),
        }
        for name, mutate in malformed_cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                mutate(workspace)
                report = validate_workspace_report(workspace, require_handoff=True)
                self.assertTrue(report.errors)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(workspace),
                        "--require-handoff",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_fixed_seed_valid_utf8_markdown_mutation_smoke_is_total_and_read_only(
        self,
    ) -> None:
        rng = random.Random(20260715)
        markdown_names = sorted(path.name for path in DETAILED.glob("*.md"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index in range(96):
                workspace = copy_fixture(DETAILED, root / str(index))
                target = workspace / rng.choice(markdown_names)
                text = target.read_text(encoding="utf-8")
                if index % 3 == 0:
                    lines = text.splitlines()
                    selected = rng.randrange(len(lines))
                    lines[selected] = lines[selected][
                        : rng.randrange(len(lines[selected]) + 1)
                    ]
                    mutated = "\n".join(lines) + "\n"
                elif index % 3 == 1:
                    position = rng.randrange(len(text) + 1)
                    mutated = (
                        text[:position]
                        + rng.choice(("表", "§", "\x00", "|"))
                        + text[position:]
                    )
                else:
                    mutated = text.replace("## ", "## Mutated ", 1)
                target.write_text(mutated, encoding="utf-8")
                before = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                validate_workspace_report(workspace, require_handoff=True)
                after = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(after, before)

    def test_exact_column_domains_surface_authorities_and_public_h2_cardinality(
        self,
    ) -> None:
        cases = {
            "section input domain": (
                "03_WRITING_STRUCTURE.md",
                "M-method;M-evidence;C-demo;VIS-figure",
                "M-method;M-evidence;C-demo;SCOPE-demo",
                None,
                "SECTION_OWNERSHIP",
            ),
            "surface authority": (
                "04_WRITING_DESIGN_PACK.md",
                "03_WRITING_STRUCTURE.md#Surface Language Contract | LANG-main",
                "00_PROJECT_ROUTE.md#Project Brief | LANG-main",
                None,
                "DETAILED_SURFACE_COVERAGE",
            ),
            "duplicate public authority": (
                "00_PROJECT_ROUTE.md",
                "",
                "",
                "\n## Project Brief\nConflicting public authority.\n",
                "OWNER_GATE",
            ),
        }
        for name, (filename, old, new, addition, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                if addition:
                    path = workspace / filename
                    path.write_text(
                        path.read_text(encoding="utf-8") + addition, encoding="utf-8"
                    )
                else:
                    replace(workspace, filename, old, new)
                self.assertIn(expected, codes(validate_workspace(workspace)))

    def test_two_ready_scopes_use_hands_off_to_without_cross_scope_adjacency(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_second_ready_scope(workspace)
            self.assertEqual(validate_workspace(workspace, require_handoff=True), [])
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| PAR-claim | SCOPE-demo | SEC-method | 2 | Connect the evidence-grounded comparison to the visual while preserving limits | Reader expects the comparison | Reader sees the supported comparison and its limitation | PAR-context | none |",
                "| PAR-claim | SCOPE-demo | SEC-method | 2 | Connect the evidence-grounded comparison to the visual while preserving limits | Reader expects the comparison | Reader sees the supported comparison and its limitation | PAR-context | PAR-other |",
            )
            self.assertIn("PARAGRAPH_SEQUENCE", codes(validate_workspace(workspace)))

    def test_quantitative_budget_action_is_structural_not_disposition_advice(
        self,
    ) -> None:
        for disposition in ("candidate", "adopted"):
            with (
                self.subTest(disposition=disposition),
                tempfile.TemporaryDirectory() as temp,
            ):
                workspace = self.workspace(temp)
                pointer = install_quantitative_rule(workspace)
                activate_rule_coverage(workspace, 1)
                append_table_row(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "Grounded Soft Budgets",
                    f"| BUD-quant | SCOPE-demo | paragraph rhythm | bounded order | quantitative_analysis | {pointer} | watch-only ordering | {disposition} | Keep the basis explicitly bounded | This is not a hard constraint |",
                )
                activate_budget_coverage(workspace, 1)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    f"| SCOPE-demo | quantitative_only | none | {pointer} | none | design_only | Quantitative observation is the only active design input | none |",
                )
                self.assertEqual(validate_workspace(workspace), [])

    def test_owner_gate_cannot_self_certify_or_disagree_across_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | scientific_commitment |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| confirmed | 00_PROJECT_ROUTE.md#Decision Records |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| not_applicable | none | not_applicable: evidence ceiling and clause roles are already fixed | none |",
                "| scientific_commitment | DEC-route | Owner-grounded decision is confirmed | 00_PROJECT_ROUTE.md#Decision Records |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| SCOPE-demo | scientific_commitment | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Decision Records |",
            )
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | argument_spine |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| not_applicable | none | not_applicable: evidence ceiling and clause roles are already fixed | none |",
                "| argument_spine | DEC-route | Owner-grounded decision is confirmed | 00_DIMENSION_INDEX.md#Workspace Metadata |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route |",
                "| SCOPE-demo | argument_spine | DEC-route |",
            )
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))

    def test_resolved_role_firewall_covers_alias_chains_and_all_template_surfaces(
        self,
    ) -> None:
        mutations = {
            "direct tpl locator": lambda workspace: replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | TPL-method |",
            ),
            "template public heading": lambda workspace: replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| confirmed | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| confirmed | 01_MATERIALS_INVENTORY.md#Template Design Sources |",
            ),
            "hidden analyzer path": lambda workspace: replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | path:.yxj-paper-os/template-analysis/semantic-dossier.json |",
            ),
            "registered derivative alias": lambda workspace: replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | path:sources/template.md |",
            ),
            "claim template authority": lambda workspace: replace(
                workspace,
                "02_CLAIM_EVIDENCE_BOUNDARY.md",
                "| confirmed | M-evidence |",
                "| confirmed | 03_WRITING_STRUCTURE.md#Template Rule Projection |",
            ),
            "promotion template authority": lambda workspace: replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| design_only | none |",
                "| design_only | 03_WRITING_STRUCTURE.md#Template Rule Projection |",
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                install_semantic_rule(workspace)
                mutate(workspace)
                self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Material Records",
                "| M-alias | evidence | Design-tainted alias | TPL-method | SCOPE-demo | available | artifact-observed | confirmed | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
            )
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Material Records",
                "| M-chain | evidence | Transitive design-tainted alias | M-alias | SCOPE-demo | available | artifact-observed | confirmed | M-alias |",
            )
            replace(
                workspace,
                "02_CLAIM_EVIDENCE_BOUNDARY.md",
                "| M-evidence | Evidence anchor constrains",
                "| M-chain | Evidence anchor constrains",
            )
            replace(
                workspace,
                "02_CLAIM_EVIDENCE_BOUNDARY.md",
                "| confirmed | M-evidence |",
                "| confirmed | M-chain |",
            )
            self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

    def test_separate_scientific_material_can_be_a_legitimate_promotion_target(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Material Records",
                "| M-scientific | evidence | Separately grounded scientific source | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory | SCOPE-demo | available | artifact-observed | confirmed | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
            )
            replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| design_only | none |",
                "| design_only | M-scientific |",
            )
            activate_rule_coverage(workspace, 1)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | none | design_only | Semantic reading governs method paragraph sequence | none |",
            )
            self.assertEqual(validate_workspace(workspace), [])

    def test_every_jsonl_row_must_have_complete_candidate_semantics(self) -> None:
        mutations = {
            "metric identity": lambda row: row.update(metric_ids=[]),
            "partition": lambda row: row.update(partition=""),
            "denominator": lambda row: row.update(valid_n=-1),
            "missingness": lambda row: row.update(missingness=-1),
            "uncertainty": lambda row: row.update(uncertainty={}),
            "action": lambda row: row.update(candidate_action="magic"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                old_pointer = install_quantitative_rule(workspace)
                new_pointer = (
                    ".yxj-paper-os/template-analysis/paper-metrics.jsonl#rows[0]"
                )
                activate_rule_coverage(workspace, 1)
                replace(workspace, "03_WRITING_STRUCTURE.md", old_pointer, new_pointer)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                    f"| SCOPE-demo | quantitative_only | none | {new_pointer} | none | design_only | Quantitative observations are the only active design input | none |",
                )
                base = {
                    "schema": "template-paper-metrics/1.0",
                    "analysis_id": "analysis-fixture",
                    "corpus_id": "corpus-fixture",
                    "metric_ids": ["structure.paragraph_count"],
                    "partition": "overall",
                    "valid_n": 2,
                    "missingness": 0,
                    "candidate_action": "adapt",
                    "uncertainty": {
                        "effective_analysis_mode": "case_set",
                        "metric_effective_analysis_mode": "case_set",
                        "comparable_stratum": True,
                    },
                }
                invalid = json.loads(json.dumps(base))
                mutate(invalid)
                jsonl = (
                    workspace / ".yxj-paper-os/template-analysis/paper-metrics.jsonl"
                )
                jsonl.write_text(
                    json.dumps(base) + "\n" + json.dumps(invalid) + "\n",
                    encoding="utf-8",
                )
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )

    def test_analyzer_virtual_outputs_are_not_quantitative_grounding_surfaces(
        self,
    ) -> None:
        for filename in ("manifest.json", "report.html", "corpus-summary.json"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                old_pointer = install_quantitative_rule(workspace)
                hidden = workspace / ".yxj-paper-os/template-analysis"
                if filename == "report.html":
                    (hidden / filename).write_text("<html></html>", encoding="utf-8")
                new_pointer = f".yxj-paper-os/template-analysis/{filename}#entries[0]"
                replace(workspace, "03_WRITING_STRUCTURE.md", old_pointer, new_pointer)
                self.assertIn(
                    "TEMPLATE_RULE_INCOMPATIBLE", codes(validate_workspace(workspace))
                )

    def test_budget_basis_kinds_use_typed_positive_and_negative_domains(self) -> None:
        positives = {
            "official": ("official_constraint", "M-method"),
            "repository": ("repository_grounding", "M-evidence"),
        }
        for name, (kind, pointer) in positives.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                append_table_row(
                    workspace,
                    "03_WRITING_STRUCTURE.md",
                    "Grounded Soft Budgets",
                    f"| BUD-{name} | SCOPE-demo | paragraph rhythm | bounded order | {kind} | {pointer} | watch-only ordering | candidate | Keep the basis explicitly bounded | This is not a hard constraint |",
                )
                activate_budget_coverage(workspace, 1)
                self.assertEqual(validate_workspace(workspace), [])
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            append_table_row(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Grounded Soft Budgets",
                "| BUD-official | SCOPE-demo | paragraph rhythm | bounded order | official_constraint | C-demo | watch-only ordering | candidate | Keep the basis explicitly bounded | This is not a hard constraint |",
            )
            activate_budget_coverage(workspace, 1)
            self.assertIn("BUDGET_CONTRACT", codes(validate_workspace(workspace)))

    def test_hidden_owner_snapshot_and_material_owner_answer_must_match_authority(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            semantic_pointer = install_semantic_rule(workspace)
            activate_rule_coverage(workspace, 1)
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | none | none | none | design_only | Template design is irrelevant to this synthetic route-neutral contract fixture | none |",
                f"| SCOPE-demo | semantic_primary | {semantic_pointer} | none | none | design_only | Semantic reading governs method paragraph sequence | none |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | material_local_tradeoff |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| owner-stated | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| not_applicable | none | not_applicable: evidence ceiling and clause roles are already fixed | none |",
                "| material_local_tradeoff | DEC-route | Owner-grounded decision is confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| adopted | none | Applies only to SCOPE-demo",
                "| adopted | DEC-route | Applies only to SCOPE-demo",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route |",
                "| SCOPE-demo | material_local_tradeoff | DEC-route |",
            )
            dossier_path = (
                workspace / ".yxj-paper-os/template-analysis/semantic-dossier.json"
            )
            dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
            dossier["transfer_rules"][0]["application_snapshot"].update(
                gate_category="material_local_tradeoff",
                decision_id="DEC-route",
                decision_pointer="00_DIMENSION_INDEX.md#Workspace Metadata",
            )
            dossier_path.write_text(json.dumps(dossier), encoding="utf-8")
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| DEC-route | not_applicable |",
                "| DEC-route | scientific_commitment |",
            )
            replace(
                workspace,
                "00_PROJECT_ROUTE.md",
                "| confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| confirmed | M-method |",
            )
            replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| SCOPE-demo | available | artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| SCOPE-demo | unavailable | artifact-observed | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
            )
            replace(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "| not_applicable | none | not_applicable: evidence ceiling and clause roles are already fixed | none |",
                "| scientific_commitment | DEC-route | Owner-grounded decision is confirmed | M-method |",
            )
            replace(
                workspace,
                "04_WRITING_DESIGN_PACK.md",
                "| SCOPE-demo | not_applicable | DEC-route | confirmed | 00_PROJECT_ROUTE.md#Project Brief |",
                "| SCOPE-demo | scientific_commitment | DEC-route | confirmed | M-method |",
            )
            self.assertIn("OWNER_GATE", codes(validate_workspace(workspace)))

    def test_canonical_template_role_identity_rejects_public_and_path_aliases(
        self,
    ) -> None:
        aliases = (
            "01_MATERIALS_INVENTORY.md#template-design-sources",
            "03_WRITING_STRUCTURE.md#Template---Rule_Projection",
            "04_WRITING_DESIGN_PACK.md#template_analysis_handling",
            "path:./sources/template.md",
            "path:sources//template.md",
        )
        for alias in aliases:
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                install_semantic_rule(workspace)
                replace(
                    workspace,
                    "01_MATERIALS_INVENTORY.md",
                    "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                    f"| M-evidence | evidence | Synthetic bounded evidence anchor | {alias} |",
                )
                self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            (workspace / "source-alias").symlink_to(
                workspace / "sources", target_is_directory=True
            )
            replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | 02_CLAIM_EVIDENCE_BOUNDARY.md#Evidence Inventory |",
                "| M-evidence | evidence | Synthetic bounded evidence anchor | path:source-alias/template.md |",
            )
            self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            replace(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "| design_only | none |",
                "| design_only | 03_WRITING_STRUCTURE.md#template-rule-projection |",
            )
            self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            install_semantic_rule(workspace)
            append_table_row(
                workspace,
                "03_WRITING_STRUCTURE.md",
                "Grounded Soft Budgets",
                "| BUD-alias | SCOPE-demo | paragraph rhythm | bounded order | repository_grounding | 01_MATERIALS_INVENTORY.md#template-design-sources | watch-only ordering | candidate | Keep the basis explicitly bounded | This is not a hard constraint |",
            )
            activate_budget_coverage(workspace, 1)
            self.assertIn("BUDGET_CONTRACT", codes(validate_workspace(workspace)))

    def test_readiness_detector_covers_explicit_modified_state_assertions_once(
        self,
    ) -> None:
        assertions = (
            "This scope is still partial for downstream drafting",
            "This scope remains currently blocked by evidence",
            "This scope stays blocked until evidence is added",
            "The readiness remains in a deferred state",
            "The status continues as currently partial",
            "This scope has status blocked",
        )
        for assertion in assertions:
            with (
                self.subTest(assertion=assertion),
                tempfile.TemporaryDirectory() as temp,
            ):
                workspace = self.workspace(temp)
                replace(
                    workspace,
                    "04_WRITING_DESIGN_PACK.md",
                    "Use 03 as the detailed authority and this row only as the compact handoff",
                    assertion,
                )
                errors = validate_workspace(workspace, require_handoff=True)
                readiness_errors = [
                    error
                    for error in errors
                    if error.startswith("HANDOFF_READINESS_DUPLICATED:")
                ]
                self.assertEqual(len(readiness_errors), 1, errors)

    def test_source_pointer_ascii_controls_are_bounded_read_only_diagnostics(
        self,
    ) -> None:
        source_pointers = (
            "https://example.org/\x00bad",
            "doi:10.1000/\x1fbad",
            "urn:example:\x7fbad",
            "isbn:978\tbad",
            "sources/\x00bad.md",
            "path:sources/\x00bad.md",
        )
        for pointer in source_pointers:
            with (
                self.subTest(pointer=repr(pointer)),
                tempfile.TemporaryDirectory() as temp,
            ):
                workspace = self.workspace(temp)
                append_table_row(
                    workspace,
                    "01_MATERIALS_INVENTORY.md",
                    "Template Design Sources",
                    f"| TPL-control | exemplar | How should metadata shape design? | {pointer} | metadata_only | none | none | none | design_only | none |",
                )
                before = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                errors = validate_workspace(workspace, require_handoff=True)
                self.assertTrue(
                    any(
                        error.startswith("TEMPLATE_FIREWALL:")
                        and "TPL-control" in error
                        for error in errors
                    ),
                    errors,
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(workspace),
                        "--require-handoff",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                after = {
                    path.relative_to(workspace): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in workspace.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(after, before)

    def test_template_local_derivative_domain_depends_on_owner_derivative_state(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Template Design Sources",
                "| TPL-meta | exemplar | How should metadata shape design? | https://example.invalid/meta | metadata_only | M-method | none | none | design_only | none |",
            )
            errors = validate_workspace(workspace, require_handoff=True)
            self.assertTrue(
                any(
                    error.startswith("TEMPLATE_FIREWALL:")
                    and "TPL-meta" in error
                    and "Local derivative pointer" in error
                    for error in errors
                ),
                errors,
            )

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            derivative = workspace / "sources" / "metadata.md"
            derivative.parent.mkdir(parents=True)
            derivative.write_text("Metadata copy.\n", encoding="utf-8")
            source_sha = hashlib.sha256(derivative.read_bytes()).hexdigest()
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Template Design Sources",
                f"| TPL-meta-path | exemplar | How should metadata shape design? | https://example.invalid/meta | metadata_only | sources/metadata.md | {source_sha} | none | design_only | none |",
            )
            self.assertIn("TEMPLATE_FIREWALL", codes(validate_workspace(workspace)))

        invalid_locals = (
            "missing",
            "symlink",
            "escape",
            "control",
            "sha-mismatch",
        )
        for case in invalid_locals:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                workspace = self.workspace(temp)
                sources = workspace / "sources"
                sources.mkdir(parents=True)
                source_sha = "a" * 64
                if case == "missing":
                    local = "sources/missing.md"
                elif case == "symlink":
                    target = sources / "target.md"
                    target.write_text("Target.\n", encoding="utf-8")
                    (sources / "alias.md").symlink_to(target)
                    local = "sources/alias.md"
                elif case == "escape":
                    outside = workspace.parent / "outside.md"
                    outside.write_text("Outside.\n", encoding="utf-8")
                    local = "../outside.md"
                elif case == "control":
                    local = "sources/bad\x00.md"
                else:
                    target = sources / "mismatch.md"
                    target.write_text("Mismatch.\n", encoding="utf-8")
                    local = "sources/mismatch.md"
                append_table_row(
                    workspace,
                    "01_MATERIALS_INVENTORY.md",
                    "Template Design Sources",
                    f"| TPL-bad-local | exemplar | How should the derivative guide design? | https://example.invalid/source | owner_derivative | {local} | {source_sha} | none | design_only | none |",
                )
                errors = validate_workspace(workspace, require_handoff=True)
                self.assertTrue(
                    any(
                        error.startswith("TEMPLATE_FIREWALL:")
                        and "TPL-bad-local" in error
                        for error in errors
                    ),
                    errors,
                )

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            derivative = workspace / "sources" / "owner.md"
            derivative.parent.mkdir(parents=True)
            derivative.write_text("Bounded owner derivative.\n", encoding="utf-8")
            source_sha = hashlib.sha256(derivative.read_bytes()).hexdigest()
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Template Design Sources",
                f"| TPL-owner | exemplar | How should the bounded derivative guide design? | sources/owner.md | owner_derivative | sources/owner.md | {source_sha} | none | design_only | none |",
            )
            self.assertEqual(validate_workspace(workspace, require_handoff=True), [])

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            derivative = workspace / "sources" / "full.md"
            derivative.parent.mkdir(parents=True)
            derivative.write_text("Bounded full text.\n", encoding="utf-8")
            source_sha = hashlib.sha256(derivative.read_bytes()).hexdigest()
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Template Design Sources",
                f"| TPL-full-local | exemplar | How should the bounded full text guide design? | https://example.invalid/full | full_text | sources/full.md | {source_sha} | none | design_only | none |",
            )
            self.assertEqual(validate_workspace(workspace, require_handoff=True), [])

        with tempfile.TemporaryDirectory() as temp:
            workspace = self.workspace(temp)
            append_table_row(
                workspace,
                "01_MATERIALS_INVENTORY.md",
                "Template Design Sources",
                f"| TPL-full-remote | exemplar | How should the remote full text guide design? | https://example.invalid/full | full_text | none | {'b' * 64} | none | design_only | none |",
            )
            self.assertEqual(validate_workspace(workspace, require_handoff=True), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
