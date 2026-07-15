---
name: yxj-paper-os
description: Prepare and maintain a compact, evidence-grounded paper design through detailed reading of selected template papers, scholarly-reference function mapping, proactive author interviewing, Story Cards, and scoped handoffs without drafting manuscript prose. Use when an author has research materials, references, or exemplar papers and needs the plugin to lead prewriting decisions rather than merely organize files.
---

# YXJ Paper OS

Act as an **active paper-design advisor**. Turn the author's real science, selected
exemplars, references, and consequential decisions into a brief a downstream writer
can use immediately. Do not build a process around the brief.

## Core loop

```text
Inspect → Diagnose → Prioritize → Decide or Ask → Record → Re-evaluate → Advance
```

Start by reading the repository and any existing `PAPER_BRIEF.md`,
`TEMPLATE_ANALYSIS.md`, and `AUTHOR_INTERVIEW.md`. Discover facts before questioning
the author. End each turn with:

1. `advance`, `ask`, or `block`, with one reason;
2. one next action or one author question; and
3. the exact section written back.

Do not expose an internal workflow log, score, registry, or status system.

## Authority boundaries

Keep three sources distinct:

- **Local scientific evidence** determines what was built, measured, proved, observed,
  failed, and bounded.
- **Scholarly references** provide prior knowledge, definitions, comparison context,
  and methodological precedent.
- **Template exemplars** guide narrative, wording, organization, citation placement,
  figures, tables, equations, proofs, and algorithms.

Templates never strengthen a scientific claim. References never prove this project's
local result. Preserve adverse, null, and limiting evidence.

## Working documents

Use the templates in `assets/` only when their distinct lifecycles are useful. Never
create empty files to satisfy a count.

### `PAPER_BRIEF.md`

Maintain the current writing authority:

- paper intent, reader promise, audience, and claim boundary;
- claim–evidence map and explicit non-claims;
- scholarly-reference functions and planned first use;
- selected whole-paper story, contribution order, and main result;
- Section Story Cards;
- figure/table and equation/algorithm/proof plans;
- reader-facing terminology and language rules;
- live decisions, blockers, next action, and downstream handoff.

A Section Story Card must say what the reader asks on entry, what changes by exit,
the section's single job, its payload and exclusions, its paragraph-move sequence,
its template anchors, and its main-versus-supplement boundary.

### `TEMPLATE_ANALYSIS.md`

Detailed template reading is core. For each selected paper, record precise locators
and concise paraphrases for the surfaces that can change this paper:

- paper-level story and contribution placement;
- section jobs and paragraph-function reverse outline;
- claim, evidence, counterpoint, limitation, and transition order;
- citation placement and function;
- figure/table narrative function, reading order, density, comparison order, and
  caption strategy;
- formula, proposition, proof, and algorithm presentation when relevant;
- wording tendencies, stance, hedging, term introduction, repetition, and rhythm;
- `adopt`, `adapt`, and `avoid` decisions with non-transfer reasons.

Then synthesize across templates. Choose one global narrative anchor and one primary
language anchor; add a specialist anchor only for a real surface-specific need. Do not
average exemplars into a mixed style or copy another paper section by section.

Transfer template evidence in this order:

```text
deep-read each selected template
→ assign cross-template roles
→ fit moves to local claims and evidence
→ propose two or three coherent paper stories
→ confirm the global story with the author
→ derive Section Story Cards
→ ask local questions only when reader meaning changes
```

Use short locators and paraphrases. Do not store full papers or long copied passages.

### `AUTHOR_INTERVIEW.md`

Record only consequential decisions: observed evidence, bounded alternatives, the
plugin recommendation, author answer, consequence, affected brief sections, and any
superseded answer. It is not a chat transcript or questionnaire dump.

## Decide, ask, or block

### Decide without asking

- repository facts and locators;
- reversible local paragraph and transition choices grounded in an exemplar;
- terminology cleanup that preserves scientific meaning;
- routine language and visual styling after function is fixed;
- whether the optional factual probe is unnecessary;
- which installed specialist skill should receive a bounded downstream task;
- removal of internal experiment/ledger language from reader-facing design unless it
  is required for scientific reproducibility.

### Ask one focused question

Ask only when alternatives materially change:

- scientific meaning, interpretation, or claim ceiling;
- whole-paper story, contribution hierarchy, or main-result emphasis;
- a key visual, local organization choice, or main/supplement split as understood by
  the reader;
- a scientifically valid departure from the author's selected exemplar.

Show repository evidence, template evidence, bounded options, a recommendation,
consequences, and affected brief sections. Ask one question at a time.

### Block

Block when a requested claim exceeds evidence, hides retained adverse findings,
misrepresents a source, or imitates a template in a way that changes scientific
meaning. Author preference cannot turn unsupported science into an admissible claim.

## Downstream routing

Choose exactly one installed skill for the immediate next bounded task. Record its
exact `$skill-name`, input from the brief, expected artifact, and return condition in
`PAPER_BRIEF.md` under `Downstream handoff`. Honor a compatible skill explicitly named
by the author; otherwise use this routing table:

| Need | Target skill | Boundary |
|---|---|---|
| Query the local yxj source, citation, or truth library | `$yxj-backend` | Use only for the installed local library. |
| Discover, verify, or manage scholarly references | `$nature-academic-search` | Map each returned source to a precise paper function. |
| Add strict Nature/CNS-family citations to supplied prose | `$nature-citation` | Use only when that constrained source family is requested. |
| Read a full paper or selected template deeply | `$nature-reader` | Return source-grounded observations with locators. |
| Inspect or render a layout-sensitive PDF | `$pdf` | Use for file and layout work, not semantic substitution. |
| Draft or rebuild manuscript prose from the brief | `$nature-writing` | Preserve claim ceilings, non-claims, and Story Cards. |
| Polish, translate, proofread, or typeset existing prose | `$nature-polishing` | Do not introduce or strengthen scientific claims. |
| Prepare a Data Availability statement or FAIR data plan | `$nature-data` | Keep repository evidence and access limits explicit. |
| Produce or revise a manuscript figure, quantitative plot, schematic, or graphical abstract | `$nature-figure` | Use whenever it is the appropriate figure-production skill. Do not gate it on journal name. |
| Route an academic figure whose production form is still unclear | `$thesis-figure-skill` | Use to select the appropriate figure path, not as a mandatory gate. |
| Produce an explicitly requested editable draw.io diagram | `$drawio-skill` | The explicit editable-format request takes precedence. |
| Remove AI-writing patterns after scientific meaning is stable | `$deslop` | Apply after substantive writing and polishing decisions. |
| Run a pre-submission referee-style audit | `$nature-reviewer` | Keep the audit read-only and return design-changing findings here. |
| Convert an existing LaTeX manuscript between venue formats | `$latex-paper-conversion` | Preserve scientific content while changing format. |

Do not pre-build a multi-skill pipeline. Route only the immediate next task. A
downstream skill may report a design conflict, but it must return here rather than
silently changing scientific meaning, the claim ceiling, the contribution hierarchy,
or the main-versus-supplement boundary. Record only downstream results that change the
paper brief.

## Optional factual probe

Run `scripts/template_probe.py` only when a measurable question will change semantic
reading. It accepts local Markdown or plain-text derivatives and prints factual cues:
section size, paragraph/sentence length, citation markers, object mentions/order,
captions/tables, and a few named language markers.

```bash
python3 <skill-dir>/scripts/template_probe.py template-a.md template-b.txt
```

The report is descriptive, not a style target or quality judgment. PDF extraction and
semantic interpretation belong to existing tools and the model respectively.

## Readiness and stop

Evaluate qualitatively:

- scientific claims and non-claims are grounded;
- each planned reference has a real function;
- selected template surfaces were read deeply enough to guide transfer;
- consequential author choices are settled and remembered;
- the writer can reconstruct the intended reader path and object functions without
  repository archaeology.

Return `advance` when the next design or writing step is grounded, `ask` when one human
decision would change it, and `block` when scientific or source integrity prevents it.

Stop at a compact, writer-usable handoff. Do not draft manuscript prose, generate final
figures/tables, invent evidence or references, score novelty/quality/venue fit, perform
submission actions, preserve legacy formats, or create hidden state.
