# YXJ Paper OS

YXJ Paper OS is a reader-first, evidence-bound Codex plugin for designing and revising
one academic paper from a creation baseline or current material delta through direct
writeback and canonical artifact verification.

Scientific integrity is the non-negotiable evidence boundary. Within that boundary, the
plugin makes the problem worth caring about, the central claim and contribution easy to
find, the evidence path coherent, and the result's useful consequences visible. Necessary
qualifications remain accurate, local, and proportionate, with central negative results
kept prominent. It verifies the reader-facing realization in the paper; an actual reader
effect still requires reader or reviewer evidence.

Paper design connects a recognizable research question with what existing knowledge
permits, what the work adds, and the evidence that supports that addition. Contributions
identify both the scholarly result and the understanding or capability it enables.
Explanatory space follows the difficult steps needed to understand and evaluate those
results; contribution count and a method--law--design sequence are not prescribed.

The skill aligns four skeletons when structure is at issue: scientific/theoretical
relations, the reader's path, section roles, and the story visible in headings and
displays. These are conditional diagnostic views, not four mandatory documents. Local
edits stay local unless a real dependency requires wider repair.

Independent sections may be reordered without being redundant. Optional/composable
routes, genuine conjunctions, scientific implications, and reader navigation retain
their different meanings. Displays are checked both individually and as a bundle;
semantic design and rendered visual acceptance are separate.

Positive writing leads with what the evidence establishes and why that matters,
including null results and impossibility boundaries. It does not impose a success story,
applications paragraph, rebuttal for every unit, or a blacklist of hedging words.

Authorial expression is part of ordinary drafting and substantive revision, not a final
"humanizer" filter. A dedicated
[Chinese-English style reference](skills/yxj-paper-os/references/authorial-style.md)
preserves author-approved choices, distinguishes contextual fit from model-frequency
patterns, and supports both useful edits and leaving sound prose unchanged. It loads
when prose or author voice is at issue, not for evidence-only or layout-only work.
Matched-venue calibration remains separate; no detector score or style profile is added.
It also checks disciplinary meaning when naming objects, headings, and figure labels,
before those choices spread through the paper. Consequential terms are checked against
definitions and relevant sources; valid technical usage is preserved.

The plugin retains repository-declared authority, creation-or-delta entry, stable author
directions, recurrence diagnosis, matched-venue functional calibration, cross-surface
closure, and current-source/canonical-artifact verification. It adds no runtime state,
instruction ledger, or compulsory record migration.

Revision includes justified content selection, diagnosis of incoming suggestions, and
checks whose requirements remain grounded in the adopted paper contract. Explicitly
deferred editions remain visible during staged work; task-affected factual handoffs are
kept current within repository permissions. Discussion remains read-only. Repeated
feedback prompts diagnosis rather than automatically becoming a lasting author rule.
Local edits require no tracking form; larger dependent revisions may use a temporary
list. Existing repository brief formats are retained.

It remains a skills-only plugin, not a standalone CLI, LaTeX builder, literature
database, deterministic paper generator, or workflow-state system. Results depend on
the available paper artifacts, tools, and host model following the skill contract.

## Use

Invoke the installed skill explicitly for predictable routing:

```text
$yxj-paper-os:yxj-paper-os Assess the paper's claim and contribution. Do not edit files.
$yxj-paper-os:yxj-paper-os Design a new paper argument from the current evidence. Do not create manuscript files.
$yxj-paper-os:yxj-paper-os Design a stronger reader-facing argument. Do not edit files.
$yxj-paper-os:yxj-paper-os Compare the scientific, reader, section, and visual skeletons; explain mismatches without editing files.
$yxj-paper-os:yxj-paper-os Rewrite this paragraph around its established result and useful consequence, preserving all material qualifications.
$yxj-paper-os:yxj-paper-os Revise the paper from reviewer.md, close every affected surface, build the canonical PDF, and verify the rendered result.
$yxj-paper-os:yxj-paper-os The same narrative issue remains after prior rounds. Audit the recurrence, repair its root cause, and verify the current PDF.
$yxj-paper-os:yxj-paper-os Compare this paper with same-journal Regular Papers on the same topic, then revise its wording, sentence patterns, and organization where the cohort supports a change.
```

Provide or identify the local scientific evidence and, when they exist, the manuscript,
rendered PDF, figures, references or exemplars, and author/reviewer feedback. Use an
explicit edit verb such as `draft`, `revise`, `rewrite`, `apply`, `fix`, or `update` when
writeback is intended.

| Mode | Effect |
|---|---|
| `assess` | Inspect and report; never edit. |
| `design` | Resolve the paper, argument, or display design without creating manuscript artifacts. |
| `revise` | Create or edit requested artifacts, close all affected surfaces, and verify. |
| `audit` | Inspect and report; repair only with explicit edit authorization. |

The bundled `skills/yxj-paper-os/assets/PAPER_BRIEF.md` is a read-only fallback. Use a
brief path declared by repository instructions; copy the template to the paper root only
when no canonical brief is declared and unrecoverable current state must persist. The
brief stores compact current basis, active constraints and stable directions, and open
work. Its prompts are optional; older tables remain readable without requiring conversion.
Completed work and temporary tracking are removed rather than retained as history.

Commit and push only when explicitly requested. Paper-local delivery must preserve
unrelated work and must not reset, recreate, or switch a shared main branch.

## Verify this plugin

```bash
python3 -m unittest discover -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

The automated checks cover package structure, resource resolution, and brief sections,
not model behavior. [Behavioral cases](tests/behavioral_cases.md) provide small realistic
requests for a separate forward pass. Give a fresh evaluator the skill and raw cases,
not an intended answer; inspect its actual outputs and file changes. A pass is bounded
evidence about those cases, not proof of reader comprehension or universal reliability.

Release or install from a clean export or clean clone. Do not package the developer
working tree with `.git/`, `.omx/`, caches, logs, or build outputs.
