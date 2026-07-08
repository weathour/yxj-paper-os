---
name: yxj-paper-os
description: Use for traffic, computer-science, or AI paper projects when Codex needs to initialize or inspect a lightweight six-file paper-planning workspace, guide the user through 20 required information dimensions, enforce claim-evidence boundaries, compile 04_WRITING_DESIGN_PACK.md, or validate a yxj writing design pack before handing off to downstream writing modules.
---

# yxj-paper-os

Operate `yxj-paper-os` as one public guided workflow with five task playbooks, one central internal dimension rubric, and one public dimension index.

Do not split the MVP into public subskills. Load the central internal rubric only when judging D00-D19 sufficiency, then load only the task playbook needed for the current missing area.

## Wake-up identity

On first use in a paper project, introduce the workflow in this compact form:

```text
I prepare your paper project as six planning files and one writing design pack.
I will not draft manuscript prose, invent citations, or execute external writing skills.
I will inspect or initialize the workspace, identify the first blocker, choose a question mode, explain why, and ask one answerable card or a low-risk quick form.
User-facing phases: Route → Materials → Claim/Evidence → Writing Structure → Handoff.
```

This is agent guidance, not a runtime system. Do not build a state machine, helper daemon, worker orchestration, or external UI dependency around it.

## Workspace contract

Use exactly these six project files:

```text
00_DIMENSION_INDEX.md
00_PROJECT_ROUTE.md
01_MATERIALS_INVENTORY.md
02_CLAIM_EVIDENCE_BOUNDARY.md
03_WRITING_STRUCTURE.md
04_WRITING_DESIGN_PACK.md
```

`00_DIMENSION_INDEX.md` is required and public. It is a status/pointer checklist for the 20 required dimensions, not a sixth content silo. The five other files hold the actual project information.

## Dashboard submode

Keep `yxj-paper-os` as one public skill. Do not create a separate public dashboard skill.

When the user asks for `yxj-paper-os dashboard`, `dashboard`, `维度 dashboard`, or an equivalent dashboard request while using this skill, enter dashboard mode instead of the normal initialize-and-fill workflow.

Dashboard mode runs the read-only static generator:

```bash
python3 skills/yxj-paper-os/scripts/generate_dashboard.py <paper_project>
```

The generator reads the six Markdown workspace files and may write only:

```text
<paper_project>/.yxj-paper-os/dashboard.html
```

Dashboard mode must never initialize a workspace, copy templates, create missing Markdown files, repair Markdown, write manuscript prose, run external skills, perform semantic scoring, prove paper readiness, start a runtime/server/watcher/graph, or add public workspace files. Missing or malformed source files become dashboard warnings or a bounded generator failure; they must not trigger template copying or source writeback.

The dashboard is structural visibility only. The six Markdown files remain the source of truth, and `scripts/verify_design_pack.py <paper_project>` remains the validator of record for the structural design-pack contract.

Outside dashboard mode, if files are missing, copy templates from `assets/templates/` before filling content.

## User-facing phases

Do not present D00-D19 as twenty user tasks at first contact. Use five phases for conversation and progress, while keeping D IDs in status/evidence reports:

| Phase | Internal dimensions | Purpose |
|---|---|---|
| Route | D01, D03, D04 | owner decisions, project brief, target route, paper type, audience |
| Materials | D05, D06, D07, D08 | real materials, evidence anchors, supplied sources, research notes |
| Claim/Evidence | D10, D11, D12, D13, claim-side D16/D17 | contribution, claims, support strength, wording boundary, limitations |
| Writing Structure | D09, D14, D15, primary D16/D17, D18 | exemplar status, reader spine, outline, object/surface control, visuals |
| Handoff | D00, D02, D19 | workspace metadata, stale flags, final design-pack compilation |

## Program-mode operating contract

Use this contract when an Autopilot/program-style agent is driving the skill. It is still agent guidance, not a runner or state machine.

Evaluator loop:

```text
Inspect → Evaluate → Classify missing information → Auto-fill safe gaps → Ask owner breakpoint when required → Update six files → Re-evaluate → Compile 04_WRITING_DESIGN_PACK.md → Validate → Handoff
```

Classify the current workspace into one state before asking or editing:

| State | Meaning | Next action |
|---|---|---|
| `inspect-needed` | Six-file workspace is missing or unread. | Initialize missing files from templates or read existing files. |
| `auto-fill-safe` | The gap is derivable bookkeeping or structure grounded in confirmed material. | Fill the target section and update the matching D row with rationale. |
| `owner-breakpoint` | The gap is owner-gated or changes route, claims, evidence, sources, or wording promises. | Stop with one human breakpoint card. |
| `reconcile-conflict` | Cross-file or cross-dimension statements conflict. | Ask one reconciliation breakpoint before final writing. |
| `compile-ready` | D00-D19 are handled and critical-standard dimensions are standard under the rubric. | Compile/update D19 from current upstream files. |
| `handoff-ready` | D19 is compiled, placeholder-free, bounded, and validator-clean. | Emit the final handoff card. |
| `blocked-invalid` | Validator or structural contract fails. | Report the concrete file/section/D-id and next repair action. |

Auto-fill boundary:

| Category | Agent may auto-fill | Owner confirmation required |
|---|---|---|
| Metadata/bookkeeping | D00 slug/date/readiness notes when derivable; D02 file-state observations; D19 mechanical compile notes. | Ambiguous owner/project identity; accepting stale risk or waiving recompile. |
| Agent-designable structure | Candidate D09 style constraints, D14 reader spine, D15 section jobs, D16/D17 structure/surface controls, and D18 visual-plan organization when grounded in confirmed material. | Any route, claim, evidence, wording, or source choice that changes meaning or promise strength. |
| Owner-gated facts | None as final facts; the agent may normalize or propose candidates only. | D01, D03, D04, D05, D06, D07, D08 source/gap claims, D10, D11, D12, D13, and final-route/stale-risk choices. |
| Forbidden auto-fill | Never invent results, citations, sources, source truth, experiments, evidence anchors, claims, venue fit, novelty, publication/submission readiness, or external skill execution. | Always blocked unless the owner supplies the missing fact or decision. |

Human breakpoint card and resume protocol:

```text
Human breakpoint — <stage / Dxx / blocker>
Current state: <one sentence based on inspected files>
Why blocked: <owner-gated fact, conflict, or missing standard-critical detail>
Safe auto-fill already done: <none | files/sections updated>
Decision needed: <one answerable question>
Options:
A. <owner-confirmed path> — writes <file#section>, updates <Dxx>, consequence <...>
B. <defer/absence path> — writes handoff note, consequence <...>
C. <reject path> — marks rejected, consequence <...>
Resume action after answer: update <file#section> + Dxx row, then re-run evaluator loop.
Stop rule: do not compile final D19 until this blocker is handled.
```

Ask one breakpoint card at a time unless the workspace is empty enough for a short quick-form. `omx question` may render the same card when available; Markdown remains the fallback. Every breakpoint must name the write target and exact resume action.

Completion contract:

1. Exactly the six public Markdown workspace files exist.
2. `00_DIMENSION_INDEX.md` has D00-D19 exactly once, valid statuses, non-placeholder reasons, pointers/handoffs, and `Blocks design pack?` values.
3. All D00-D19 dimensions are handled as `filled`, `not_applicable`, `absent`, `deferred`, or `rejected` with rationale.
4. Critical-standard dimensions `D04,D05,D06,D10,D11,D12,D13,D14,D15,D16,D17,D18` have reached internal `standard`; non-critical dimensions have at least minimum handling.
5. No hard blocker remains for dimension index, project route, core materials, core contribution, claim/evidence boundary, writing structure, or external route.
6. `04_WRITING_DESIGN_PACK.md` is compiled from current upstream files and includes D19 sections, six-track coverage, downstream route matrix, stale gate, validation notes, and final handoff card.
7. No unresolved `TODO`, `TBD`, `REPLACE_ME`, `UNKNOWN`, or `[...]` placeholder remains in final workspace content.
8. `python3 skills/yxj-paper-os/scripts/verify_design_pack.py <paper_project>` passes.

Final response/handoff card:

```text
Final yxj-paper-os handoff
Pack status: valid / blocked
Ready for: downstream writing planning from 04_WRITING_DESIGN_PACK.md
Not ready for: final citations, manuscript-ready prose, submission, publication, acceptance, or semantic adequacy claims
Validation: <command> → <pass/fail>
Remaining deferred/absent/rejected items: <D IDs or none>
Recommended downstream route(s): <writing/citation/figure/review/defer>, recommendation only; no external route executed
Next owner action if blocked: <one concrete action>
```

## Native subagent acceleration policy

The leader remains the only user-facing question owner, final file writer, and handoff judge. Native subagents are acceleration aids for bounded evidence collection, challenge, drafting, or verification; they do not create a second public workflow and they must stay under this skill's claim/evidence and owner-confirmation boundaries.

Default subagent lanes:

| Workflow point | Default? | Role | Scope | Must not do |
|---|---:|---|---|---|
| After inspect/init | yes | `verifier` | Read the six files, audit D00-D19 structure/statuses, placeholder tokens, stale flags, and first blocker. | Write files, ask the owner, or decide owner-gated facts. |
| Materials scan | conditional default when local artifacts are numerous or unclear | `explore` | List candidate result/figure/table/data/code/baseline/metric/source-note artifacts from local files for owner confirmation. | Treat candidates as confirmed evidence or invent missing artifacts/outcomes. |
| Claim/Evidence pre-compile challenge | yes before D19 compile | `critic` | Challenge unsupported claims, missing evidence anchors, weak support labels, overclaims, absent forbidden wording, and hidden limitations. | Strengthen claims, add citations/results, or finalize claim/evidence facts. |
| Writing Structure proposal | yes after route/materials/claims are confirmed enough | `architect` or `writer` | Propose reader spine, section jobs, object granularity, surface controls, visual storyline, and paragraph/function map grounded in confirmed upstream material. | Add new claims, invent figures/exemplars, or draft manuscript prose. |
| Design-pack compilation | optional default when compile-ready | `writer` | Draft a structured D19 candidate from current upstream files and recorded constraints. | Resolve unresolved blockers, execute external skills, or hide deferred/absent/rejected items. |
| Post-compile validation | yes | `verifier` | Run/read structural validation, check final placeholders, D coverage, stale gate, and handoff readiness. | Claim semantic adequacy, submission readiness, acceptance, or publication completion. |

Trigger rules:

1. Use default lanes when they materially improve correctness or speed and the environment supports native subagents. If unavailable, perform the same checks in the leader lane and report that no subagent lane was used.
2. Outside active team/swarm mode, do not invoke `worker`; use the specific roles above.
3. Keep child prompts bounded and read-only unless the role is explicitly drafting a design-pack candidate for leader review.
4. Subagents must report findings upward with file paths, D IDs, blocker category, confidence, and evidence-vs-inference boundaries.
5. The leader integrates findings, decides the next interaction mode, writes Markdown updates, asks any owner breakpoint, and owns final verification.

Hard prohibitions for subagents are the same as for the leader, plus: they must not ask the user directly, mark owner-gated facts final, search citations by default, execute downstream writing skills, create public workspace files beyond the six-file contract, or modify project files without leader integration.

## Interaction modes

Choose the mode automatically from the first current blocker and state the reason.

| Mode | Use when | Rule |
|---|---|---|
| `focused-question` | one owner-gated answer determines the next branch | Default for route, claim, evidence, source, or forbidden wording blockers. |
| `quick-form` | empty workspace or several low-risk fields can be collected together | Use 8-12 concise fields at most; do not hide major owner decisions inside a long form. |
| `candidate-confirmation` | confirmed upstream material lets the agent propose options | Present candidates as non-final until the owner confirms owner-gated facts/claims/evidence/sources/wording. |
| `reconciliation` | cross-file or cross-dimension statements conflict | Show the conflict and ask which version is authoritative before compiling. |
| `stale-alert` | D02 indicates a downstream pack may be stale | Ask whether to recompile, defer handoff, or record owner-accepted risk. |

## Question cards

A question card is the canonical interaction layer:

```text
Current stage: <Route | Materials | Claim/Evidence | Writing Structure | Handoff>
Dimension / blocker: <Dxx or hard-blocker name>
Why this matters: <one sentence>
Mode chosen: focused-question | quick-form | candidate-confirmation | reconciliation | stale-alert
Question: <single answerable question or compact low-risk form>
Options:
A. <answer path> — <consequence / file write>
B. <answer path> — <consequence / file write>
C. defer — <what can continue / what remains blocked>
D. absent or rejected — <downstream limitation>
Agent action after answer: update <file#section> and the matching Dxx row in 00_DIMENSION_INDEX.md.
```

Keep cards short. Ask one card at a time unless `quick-form` is justified.

If an attached OMX question UI is available, the same card may be rendered with `omx question --input ... --json` using `type: "single-answerable"` or `type: "multi-answerable"`. `omx question` is only an optional renderer. Markdown question cards remain the standalone fallback and the public behavior of this plugin.

## Core workflow

1. **Inspect / initialize.** Check whether the six files exist. If not, create them from `assets/templates/`.
2. **Read the dimension index first.** Confirm D00-D19 exist in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?` values.
3. **Use the central internal rubric for sufficiency.** Read `references/00-dimension-rubric.md` when deciding whether a dimension is only `minimum`, has reached `standard`, can remain deferred, or may allow design-pack compilation. The rubric is not a sixth task playbook and does not change the public index schema.
4. **Find the first blocker.** Read the current files and identify the first missing hard-blocker category, unhandled dimension, or critical dimension that has not reached `standard`.
5. **Load one task playbook.** Read the matching file under `references/`:
   - `00-project-route.md` for D01, D03, D04: owner decisions, project brief, target route, paper type, topic, and positioning.
   - `01-materials-inventory.md` for D05, D06, D07, D08: materials, evidence, user-provided sources, and research notes.
   - `02-claim-evidence-boundary.md` for D10, D11, D12, D13, and secondary claim-side D16/D17: contribution options, claims, evidence, wording, limitations, and risk.
   - `03-writing-structure.md` for D09, D14, D15, primary D16, primary D17, and D18: exemplar language, reader spine, outline, object granularity, surface control, and visuals.
   - `04-design-pack-compiler.md` for D00, D02, D19 and final handoff compilation.
6. **Ask one focused question when blocked.** If required information is missing, ask only the next highest-leverage question and wait for the answer. Do not batch many questions unless the user explicitly asks for a form to fill.
7. **Update the relevant Markdown file and the index.** Normalize the answer into the proper content file, then update the matching row in `00_DIMENSION_INDEX.md`. Preserve uncertainty as explicit `not_applicable`, `absent`, `deferred`, or `rejected` decisions with reasons instead of pretending completeness.
8. **Compile only when clear.** Generate or update `04_WRITING_DESIGN_PACK.md` only after all hard blockers are resolved, all 20 dimensions are handled, and every critical-standard dimension has reached `standard` under the internal rubric.
9. **Validate.** Run `scripts/verify_design_pack.py <paper_project>` when a design pack is ready.

## Internal dimension rubric

Use `references/00-dimension-rubric.md` as the central internal source for D00-D19 sufficiency. It defines `minimum`, `standard`, and `ideal` guidance, the critical-standard set, proposal/confirmation rules, write targets, and defer/reject behavior.

This rubric is not a public skill, not a sixth task playbook, and not a public workspace file. Do not add tier columns or tier status values to `00_DIMENSION_INDEX.md`; express the result through the existing `Status`, `Reason / owner note`, and `Pointer or handoff` fields.

Critical-standard dimensions that must reach `standard` before compiling the final design pack are exactly: `D04,D05,D06,D10,D11,D12,D13,D14,D15,D16,D17,D18`. Non-critical dimensions still require at least `minimum` handling; `ideal` never blocks.

Owner-gated facts, route decisions, contribution choices, claims, evidence anchors, source/citation facts, and forbidden routes require owner confirmation before final `filled`/standard handling. Agent-designable structural dimensions may be proposed and marked standard only when grounded in confirmed upstream material and rationale.

## Dimension handling gate

Each D00-D19 row in `00_DIMENSION_INDEX.md` must have:

| Field | Rule |
|---|---|
| `ID` | One of D00-D19, each exactly once |
| `Dimension` | Current semantic dimension name |
| `Current home` | The content file or index file that owns the information |
| `Status` | `filled`, `not_applicable`, `absent`, `deferred`, or `rejected` |
| `Reason / owner note` | Non-placeholder explanation |
| `Pointer or handoff` | Non-placeholder file+section pointer for `filled`, or a handoff note for non-filled statuses |
| `Blocks design pack?` | `yes` or `no`; means readiness-critical if unhandled, not currently blocking after it is handled |

A dimension is handled when it is substantively filled or explicitly marked `not_applicable`, `absent`, `deferred`, or `rejected` with a reason and pointer/handoff note. A structurally valid design pack proves this contract was checked; it does not prove semantic adequacy of the paper plan.

## Hard blockers

Block design-pack compilation and ask for missing information when any category below is incomplete:

| Blocker | Minimum required information |
|---|---|
| `dimension-index` | D00-D19 present with valid status, reason, pointer/handoff, and `Blocks design pack?` value |
| `project-route` | target venue/family, paper type, topic, traffic/computer positioning |
| `core-materials` | experiment/result/figure/table/data/code/baseline/metric locations or explicit absence decisions |
| `core-contribution` | problem, object, method/system/model, one-sentence contribution |
| `claim-evidence` | every core claim has evidence anchor, support strength, and forbidden wording boundary |
| `writing-structure` | reader spine, section jobs, figure storyline sufficient for downstream drafting |
| `external-route` | downstream writing route/skill category and handoff constraints |

A final `04_WRITING_DESIGN_PACK.md` with unresolved `TODO`, `TBD`, `REPLACE_ME`, or `UNKNOWN` is invalid.

## Boundaries

Do not:

- draft manuscript prose;
- execute external skills automatically;
- search for citations or invent BibTeX entries;
- invent experiments, data, baselines, metrics, results, sources, or evidence anchors;
- strengthen claims beyond evidence;
- build a runtime graph, stage registry, worker orchestration, backflow runtime, or large validator matrix;
- restore the old 20 public workspace files;
- claim submission, upload, publication, acceptance, or final-paper completion.

External writing tools may receive `04_WRITING_DESIGN_PACK.md`, but they cannot override claim/evidence/owner boundaries.

## Output discipline

When reporting progress, name:

- which of the six files changed;
- which hard blockers or dimension IDs remain unhandled;
- whether `04_WRITING_DESIGN_PACK.md` is valid or still blocked;
- which validation command was run and its result.
