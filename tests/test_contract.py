from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skills/yxj-paper-os"


def compact(text: str) -> str:
    return " ".join(text.split()).lower()


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker) + len(marker)
    end = text.find("\n## ", start)
    return compact(text[start:] if end == -1 else text[start:end])


class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.brief = (ROOT / "assets/PAPER_BRIEF.md").read_text(encoding="utf-8")
        cls.readme = (REPO / "README.md").read_text(encoding="utf-8")
        cls.manifest = json.loads(
            (REPO / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )

    def assert_phrases(self, text: str, *phrases: str) -> None:
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(compact(phrase), text)

    def test_plugin_layout_and_version(self) -> None:
        self.assertEqual(self.manifest["version"].split("+", 1)[0], "0.9.0")
        self.assertEqual(self.manifest["skills"], "./skills/")
        self.assertEqual(
            {
                path.relative_to(ROOT).as_posix()
                for path in ROOT.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            },
            {"SKILL.md", "assets/PAPER_BRIEF.md"},
        )

    def test_edit_authorization_is_explicit(self) -> None:
        intent = section(self.skill, "Honor the user's intent")
        self.assert_phrases(
            intent,
            "Assessment is not edit authorization",
            "`Start` or `continue` enters `revise` only when there is a nearest explicit pending revision",
            "It does not turn an exploratory question, rejected option, or old chat into an edit instruction",
            "obey its explicit edit verb and stated scope",
        )

    def test_repository_declares_current_authority(self) -> None:
        authority = section(self.skill, "Resolve current authority")
        self.assert_phrases(
            authority,
            "Read inherited repository instructions first",
            "repository-declared canonical paper root, variant, read order, and control documents",
            "Canonical authority does not imply write authority",
            "A repository-declared brief may be maintained during `design` or `revise` only when its repository contract permits it",
            "Change `AGENTS.md`, status, handoff, or another control document only when the user explicitly requests that change or the document itself explicitly requires agent writeback",
            "do not create a competing project-root brief",
            "Default to the project-root `PAPER_BRIEF.md` only when the repository declares no canonical brief",
            "project root means the resolved canonical paper root, not necessarily the repository root",
            "During `design` or `revise`, create or maintain this fallback brief when that condition holds",
            "it does not require a nonexistent repository brief contract",
            "Do not recursively ingest archives or every historical handoff",
        )

    def test_reentry_uses_delta_and_compacts_legacy_briefs(self) -> None:
        reentry = section(self.skill, "Re-enter by material delta")
        self.assert_phrases(
            reentry,
            "compare its recorded basis with the current commit, source, canonical rendered artifact, and feedback",
            "Inspect changed inputs and affected surfaces first",
            "If no material delta remains, stop",
            "normalize it in place",
            "Use Git for history; do not create a backup, journal, or production log",
        )

    def test_stable_author_directions_survive_completed_tasks(self) -> None:
        directions = section(self.skill, "Preserve stable author directions")
        self.assert_phrases(
            directions,
            "one-off task instruction",
            "stable author direction",
            "explicitly says `always`, `never`, or `remember`",
            "corrects the same direction at least twice",
            "Semantically deduplicate directions",
            "Only that explicit supersession or exception may alter a hard direction in the matching scope",
            "scientific evidence and integrity",
            "active hard author direction",
            "current explicit scoped instruction",
            "active default author direction",
            "current artifact, exemplar, or model inference",
            "A local instruction does not silently supersede a broader direction",
            "Only an explicitly cross-project direction belongs in existing inherited repository guidance",
            "Do not create a hidden user profile",
        )
        precedence = (
            "scientific evidence and integrity",
            "active hard author direction",
            "current explicit scoped instruction",
            "active default author direction",
            "current artifact, exemplar, or model inference",
        )
        self.assertEqual(
            [directions.index(phrase) for phrase in precedence],
            sorted(directions.index(phrase) for phrase in precedence),
        )

    def test_repeated_feedback_triggers_root_cause_audit(self) -> None:
        recurrence = section(self.skill, "Diagnose recurrence before editing again")
        self.assert_phrases(
            recurrence,
            "the same accepted finding returns",
            "`again`, `still`, or equivalent",
            "not applied",
            "local patch missed the structural cause",
            "regression",
            "stale artifact",
            "acceptance drift",
            "escalate from a local patch to the structural or root-cause repair",
            "Do not repeat synonym swaps",
        )

    def test_revision_closes_every_material_surface_once(self) -> None:
        revision = section(self.skill, "Revise in one coherent pass")
        self.assert_phrases(
            revision,
            "temporary impact-closure matrix",
            "title, abstract, introduction, result sequence, figures, captions, discussion, and conclusion",
            "claims, equations and proofs, experiments, tables, terminology, citations, and translations",
            "Routine paragraph order, transitions, terminology, equation numbering, cross-references, captions, and visual styling do not need author approval",
            "one coherent pass",
        )

    def test_scientific_authority_and_local_defense_remain_locked(self) -> None:
        authority = section(self.skill, "Preserve scientific authority")
        defense = section(self.skill, "Use minimal sufficient defense")
        self.assert_phrases(
            authority,
            "Local scientific evidence determines what this project built, measured, proved, observed, failed, and bounded",
            "Scholarly references provide prior knowledge",
            "Template exemplars guide narrative",
            "Preserve adverse, null, and limiting evidence",
            "Never edit measured data, computed results, or verification records to make them fit the prose",
        )
        self.assert_phrases(
            defense,
            "State a caveat once, at the nearest claim it qualifies",
            "Minimal sufficient defense protects trust without hiding the contribution",
        )

    def test_display_contract_precedes_nontrivial_drawing(self) -> None:
        displays = section(self.skill, "Produce claim-bearing displays")
        self.assert_phrases(
            displays,
            "one reader question and one-sentence takeaway",
            "authoritative evidence locators and the allowed claim",
            "a panel or component map with one distinct job per part",
            "exact versus schematic elements and their visual encodings",
            "canonical editable source or generator and its derived outputs",
            "intended final width and legibility floor",
        )

    def test_display_edits_follow_the_active_editable_source(self) -> None:
        displays = section(self.skill, "Produce claim-bearing displays")
        self.assert_phrases(
            displays,
            "a similar filename is not enough",
            "edit and regenerate that source rather than patching a derived PDF, PNG, or SVG",
            "Use the smallest matching repository-native backend",
            "neither project evidence nor final claim-bearing scientific artwork",
        )

    def test_display_acceptance_has_independent_scientific_and_visual_gates(self) -> None:
        displays = section(self.skill, "Produce claim-bearing displays")
        self.assert_phrases(
            displays,
            "Render standalone panels and any production parent or composite at the intended manuscript size",
            "Scientific gate",
            "Visual gate",
            "Neither gate substitutes for the other",
            "updating affected labels, subreferences, caption, body text, float layout, translations, and related tables",
            "rebuild the current-source manuscript",
            "inspect the affected page plus neighboring pages",
            "Compile success, a caption-only edit, or a new candidate PDF is not display acceptance",
            "Do not fix pagination by blindly shrinking the display",
            "Prefer deletion, combination, or simplification when a display or panel has no distinct reader job",
        )

    def test_author_question_is_a_last_resort(self) -> None:
        questions = section(self.skill, "Ask only when blocked by author authority")
        self.assert_phrases(
            questions,
            "Keep at most one open author question",
            "after available repository, evidence, artifact, feedback, reference, and exemplar inspection",
            "changes scientific meaning or the global reader path and blocks the immediate work",
            "Otherwise make the safe reversible choice and continue",
        )

    def test_verification_proves_current_artifact_and_reader_path(self) -> None:
        verification = section(self.skill, "Verify the current realization")
        self.assert_phrases(
            verification,
            "Inspect the post-edit diff",
            "rebuild the canonical rendered artifact",
            "prove that the inspected artifact came from the current source",
            "Render and inspect affected pages",
            "fresh non-writer review context",
            "fixed reader tasks",
            "An aggregate score alone is not acceptance evidence",
            "changed artifacts",
            "impact closure",
        )

    def test_delivery_does_not_rewrite_shared_history(self) -> None:
        delivery = section(self.skill, "Deliver without disturbing shared work")
        self.assert_phrases(
            delivery,
            "Commit or push only when explicitly requested",
            "branch, HEAD, dirty state, and upstream",
            "preserve unrelated work",
            "Never reset, recreate, or switch a shared main branch",
            "canonical source, canonical rendered artifact, and Git state",
            "named formal export is stale",
        )

    def test_brief_is_compact_current_state_not_a_log(self) -> None:
        brief = compact(self.brief)
        self.assertEqual(
            [line for line in self.brief.splitlines() if line.startswith("## ")],
            ["## Current basis", "## Current constraints", "## Open work"],
        )
        self.assertIn(
            "| ID | Scope | Strength | Active constraint or stable author direction | Source or locator | Supersedes |",
            self.brief,
        )
        self.assert_phrases(
            brief,
            "compact current state, not a chronology",
            "Scope",
            "Strength",
            "Supersedes",
            "`hard` or `default`",
            "Every retained row is active",
            "delete its old row",
            "stable author direction",
            "Impact closure",
            "Completed work is removed; active stable directions remain",
        )
        self.assertNotIn("instruction ledger", brief)
        self.assertNotIn("`active` or `superseded`", brief)

    def test_finish_preserves_declared_and_fallback_write_rules(self) -> None:
        finish = section(self.skill, "Finish and stop")
        self.assert_phrases(
            finish,
            "Update a repository-declared brief only when `design` or `revise` and its write contract authorize maintenance",
            "Update a fallback brief during `design` or `revise`",
            "Remove completed work, retain active stable directions",
        )

    def test_docs_and_manifest_advertise_the_new_contract(self) -> None:
        docs = compact(self.readme)
        interface = self.manifest["interface"]
        advertised = compact(
            self.manifest["description"]
            + interface["longDescription"]
            + " ".join(interface["capabilities"])
        )
        prompt = compact(interface["defaultPrompt"])
        self.assert_phrases(
            docs,
            "repository-declared authority",
            "stable author directions",
            "recurrence audit",
            "canonical rendered artifact",
            "Claim-bearing displays",
            "Commit and push only when explicitly requested",
            "$yxj-paper-os:yxj-paper-os",
        )
        self.assert_phrases(
            advertised,
            "delta re-entry",
            "recurrence root-cause repair",
            "stable author directions",
            "claim-bearing display production",
            "canonical artifact verification",
        )
        self.assert_phrases(
            prompt,
            "repository-declared authority",
            "current material delta",
            "Preserve active stable author directions",
            "If a finding recurs",
            "repair the root cause",
            "all claim-relevant evidence",
            "reader question",
            "editable source",
            "visual gate",
            "scientific gate",
            "explicitly authorized edits",
            "canonical artifact",
            "fixed cold-reader tasks",
            "impact closure",
        )

    def test_retired_contract_language_stays_absent(self) -> None:
        contract = compact(self.skill + self.readme + json.dumps(self.manifest))
        for retired in (
            "returning non-writing paper-design authority",
            "design handoff",
            "realization alignment",
            "downstream handoff",
            "verify the reader effect",
            "its priority order is",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, contract)


if __name__ == "__main__":
    unittest.main()
