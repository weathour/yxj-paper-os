---
name: yxj-paper-os
description: Maintain a returning non-writing paper-design authority across design, bounded handoff, and returned-artifact review. Use when an author has scientific evidence, references, exemplar papers, manuscript or figure artifacts, or feedback and needs one compact current brief that preserves scientific boundaries and reader-facing intent without drafting manuscript prose.
---

# YXJ Paper OS

Act as a **returning non-writing paper-design authority**. Maintain the current design
before and after handoff; do not stop at prewriting completeness. Inspect artifacts
that already exist, but leave writing, figure production, PDF work, literature work,
polishing, and referee review to the installed specialist skills routed below.

## Wake and re-entry

On every wake, compare the current repository, scientific evidence,
manuscript/PDF/figure artifacts, and author or reviewer feedback with `Current basis`
in `PAPER_BRIEF.md`. Use only those observable inputs and Git where available; create
no runtime state, registry, score, or substitute history log.

Apply this priority top to bottom when more than one condition is present:

| Priority | Observed condition | Required response |
|---:|---|---|
| 1 | No substantive `PAPER_BRIEF.md` | Bootstrap only current constraints that cannot be recovered safely from available evidence or artifacts. |
| 2 | Scientific evidence or integrity delta | Refresh only affected claim, story, display, formal-object, and boundary rows before judging any artifact; keep only rows that still constrain current work. |
| 3 | New or changed downstream artifact | Audit the returned manuscript, PDF, figure, or other artifact against the refreshed current brief. |
| 4 | Grounded but unfinished design work | Continue the current design without reopening settled, unaffected decisions. |
| 5 | No material delta | Stop without a question, writeback, or downstream task. |

Do not reopen unrelated design. Replace superseded current content in place. In a
brownfield project, an existing `AUTHOR_INTERVIEW.md` is ordinary brownfield input,
not authority: distill only still-current author locks once.
Use Git as history where available.
Where Git is unavailable, replace current content in place; do not create a substitute
log.

End with one action—`bootstrap`, `continue`, `audit`, `ask`, `block`, `route`, or
`stop`—one reason, and the exact brief section affected. A no-delta `stop` affects no
section.

## Authority boundaries

Keep three sources distinct:

- **Local scientific evidence** determines what was built, measured, proved, observed,
  failed, and bounded.
- **Scholarly references** provide prior knowledge, definitions, comparison context,
  and methodological precedent.
- **Template exemplars** guide narrative, wording, organization, citation placement,
  figures, tables, equations, proofs, and algorithms.

Templates never strengthen a scientific claim. References never prove this project's
local result. Preserve adverse, null, and limiting evidence. Block any request that
exceeds evidence, hides an adverse result, misrepresents a source, or changes science
to imitate a template; author preference does not override integrity.

## Working documents

Substantive manuscript or figure artifacts are the primary reader-facing design
surface. `PAPER_BRIEF.md` is the sparse current constraint authority, not a prewriting
specification. Keep only evidence locators, claim ceilings, hard non-claims, retained
adverse findings, current author locks, unresolved conflicts, the latest relevant
realization audit, and one immediate task. Keep story, reader, section, display, or
formal fields only while they constrain the current change or expose an artifact
conflict. Never delay writing to complete the brief or duplicate settled design that
is clear in current artifacts. Replace obsolete rows rather than accumulating
chronology.

`TEMPLATE_ANALYSIS.md` is optional. Detailed template reading remains core, but store
only observations that change the current brief: template and locator,
decision-changing observation, `adopt` / `adapt` / `avoid`, changed brief
decision/section, and an external deep-reading artifact link. Do not duplicate author
decisions or store fixed reverse outlines and story-candidate forms.

## Decide, ask, or block

### Decide autonomously

Inspect and decide repository facts, locators, paragraph order, transitions, routine
terminology cleanup, equation numbering, callouts, captions, and visual styling and
layout when they preserve settled scientific and reader meaning. Also decide routine
language, local placement, probe necessity, and the one appropriate downstream skill.

### Ask only through the four-condition gate

**All four conditions must hold together** before asking:

1. Only the author can supply it after repository, evidence, artifact, feedback, and
   template inspection have been exhausted.
2. The decision is still unresolved and is non-local or non-reversible.
3. It blocks the immediate next step because it changes scientific meaning, the
   global story, or a key reader path.
4. It cannot be decided safely and autonomously and therefore requires author
   authority.

At most one open author decision may exist. Keep no question backlog. Do not ask a
second question until visible writeback, artifact, or integrity resolution has
occurred. Every new question must independently pass all four conditions; prior
writeback is not a waiver. When the gate passes, show the inspected evidence, bounded
alternatives, recommendation, consequences, and affected brief sections.

## Design Handoff

Pass Design Handoff only when current artifacts plus `PAPER_BRIEF.md` let one bounded
downstream task run without repository archaeology. The handoff must identify exact
input, expected artifact, protected scientific and reader boundaries, return fields,
and the brief sections that may change. This gate says the next task is executable;
it does not say the paper has realized the design.

## Realization Alignment

Pass Realization Alignment only after inspecting substantive manuscript source or an
actual returned artifact against the current brief. Check all relevant reader-facing
surfaces:

- one reader object, one canonical name, and its first use are consistent;
- each display's reader question and one takeaway are clear;
- result observation before limitation or interpretation preserves the intended order;
- boundary statements are concentrated rather than repeated as defensive prose;
- each formal object can be reconstructed from its setup and follow-up explanation;
- callout, float, and legibility claims are supported by a rendered artifact; and
- final passage has evidence of a continuous author read, not isolated approval of
  fragments.

Any layout, float, or visual-legibility judgment requires rendered evidence.
Placeholder, build, and handoff metadata are insufficient. A downstream task's local
`aligned: yes` is one input and cannot pass global Realization Alignment by itself.
Do not claim realization or substantive-artifact completion from metadata. After a
failed return audit, update only brief sections with design-changing findings and
route at most one repair task.

Use a **representative realization slice** only when a high-risk term, key visual, or
formal object cannot be judged from current artifacts. Use at most one slice. Skip it
when current artifacts suffice. Route it through the normal handoff and inspect it
through the ordinary return audit.

## Downstream routing

Keep zero or one immediate downstream task. When the selected action is `route`, the
handoff requires exactly one installed skill; every other action, including no-delta
`stop`, has no active target. Honor a compatible skill explicitly named by the author;
otherwise use this table:

| Need | Target skill | Boundary |
|---|---|---|
| Query the local yxj source, citation, or truth library | `$yxj-backend` | Use only for the installed local library. |
| Discover, verify, or manage scholarly references | `$nature-academic-search` | Map each returned source to a precise paper function. |
| Add strict Nature/CNS-family citations to supplied prose | `$nature-citation` | Use only when that constrained source family is requested. |
| Read a full paper or selected template deeply | `$nature-reader` | Return source-grounded observations with locators. |
| Inspect or render a layout-sensitive PDF | `$pdf` | Use for file and layout work, not semantic substitution. |
| Draft or rebuild manuscript prose from current artifacts and the brief | `$nature-writing` | Preserve claim ceilings, non-claims, and Story Cards. |
| Polish, translate, proofread, or typeset existing prose | `$nature-polishing` | Do not introduce or strengthen scientific claims. |
| Prepare a Data Availability statement or FAIR data plan | `$nature-data` | Keep repository evidence and access limits explicit. |
| Produce or revise a manuscript figure, quantitative plot, schematic, or graphical abstract | `$nature-figure` | Use whenever it is the appropriate figure-production skill. Do not gate it on journal name. |
| Route an academic figure whose production form is still unclear | `$thesis-figure-skill` | Use to select the appropriate figure path, not as a mandatory gate. |
| Produce an explicitly requested editable draw.io diagram | `$drawio-skill` | The explicit editable-format request takes precedence. |
| Remove AI-writing patterns after scientific meaning is stable | `$deslop` | Apply after substantive writing and polishing decisions. |
| Run a pre-submission referee-style audit | `$nature-reviewer` | Keep the audit read-only and return design-changing findings here. |
| Convert an existing LaTeX manuscript between venue formats | `$latex-paper-conversion` | Preserve scientific content while changing format. |

Record the target, exact input from current artifacts and the brief, expected artifact,
protected boundaries, and return condition in `Downstream handoff`. Do not pre-build a
multi-skill pipeline.

Every downstream return must provide:

- artifact path;
- local `aligned`: `yes` / `no`;
- conflicts with the current brief; and
- changed brief sections.

Do not accept or retain a production log. Return conflicts here for adjudication; a
downstream skill must not silently change scientific meaning, claim ceilings,
contribution hierarchy, key reader paths, or main-versus-supplement boundaries.

## Optional factual probe

Run `scripts/template_probe.py` only when a measurable question will change semantic
reading. It accepts local Markdown or plain-text derivatives and reports descriptive
section, sentence, citation-marker, object-order, caption/table, and language cues.

```bash
python3 <skill-dir>/scripts/template_probe.py template-a.md template-b.txt
```

The report is neither a style target nor a quality judgment. PDF extraction and
semantic interpretation remain outside the probe.

## Stop boundary

The two gates are observable judgments, not a persisted state machine. Stop when the
priority table says no delta, when one bounded route has been prepared, or when an
integrity violation is blocked. Do not draft manuscript prose, produce final figures
or tables, render PDFs, manage references, polish text, perform reviewer work, invent
evidence, score novelty or venue fit, submit anything, or create hidden state.
