# YXJ Paper OS

YXJ Paper OS is a reader-first, evidence-bound Codex plugin for designing and revising
one academic paper from a creation baseline or current material delta through direct
writeback and canonical artifact verification.

Scientific integrity is the non-negotiable evidence boundary. Within that boundary, the
plugin makes the problem worth caring about, the central claim and contribution easy to
find, the evidence path coherent, and defensive prose accurate, local, and
proportionate. It verifies the reader-facing realization in the paper; an actual reader
effect still requires reader or reviewer evidence.

Version 0.10 reduces repeated author correction through seven small contracts:

1. **Repository-declared authority:** follow the paper root, variant, control documents,
   source, and output named by the repository instead of inventing a competing root
   brief.
2. **Creation-or-delta entry:** establish a new paper from current evidence without
   inventing old artifacts, or compare an existing paper with current source, feedback,
   Git state, and canonical rendered artifact.
3. **Stable author directions:** retain durable `always`/`never` rules and repeatedly
   corrected preferences after a one-off task is complete, without creating a hidden
   profile or instruction database.
4. **Reader-path diagnosis and recurrence audit:** recover the paper's actual argument,
   repair its earliest divergence, and inspect prior diffs and artifact provenance when
   the same accepted finding returns.
5. **Verified closure:** trace every affected paper surface, inspect the post-edit diff,
   rebuild and identify the canonical rendered artifact, and use a fixed cold-reader
   check for global story changes when a fresh context is available.
6. **Claim-bearing displays:** lock the reader question, evidence mapping, editable
   source, final-size visual and scientific gates, manuscript integration, and formal
   export instead of treating compilation as figure acceptance.
7. **Matched-venue writing calibration:** compare the same journal, article type,
   publication era, topic, manuscript locus, and sentence job; apply only locator-backed
   patterns while preserving scientific semantic invariants.

It remains a skills-only plugin, not a standalone CLI, LaTeX builder, literature
database, deterministic paper generator, or workflow-state system. Results depend on
the available paper artifacts, tools, and host model following the skill contract.

## Use

Invoke the installed skill explicitly for predictable routing:

```text
$yxj-paper-os:yxj-paper-os Assess the paper's claim and contribution. Do not edit files.
$yxj-paper-os:yxj-paper-os Design a new paper argument from the current evidence. Do not create manuscript files.
$yxj-paper-os:yxj-paper-os Design a stronger reader-facing argument. Do not edit files.
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
work—not conversation or production history.

Commit and push only when explicitly requested. Paper-local delivery must preserve
unrelated work and must not reset, recreate, or switch a shared main branch.

## Verify this plugin

```bash
python3 -m unittest discover -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Release or install from a clean export or clean clone. Do not package the developer
working tree with `.git/`, `.omx/`, caches, logs, or build outputs.
