# Playbook 03 — Writing Structure

Use this playbook when `03_WRITING_STRUCTURE.md` is missing, when downstream writing lacks a clear structure, or when D09/D14/D15/D16/D17/D18 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is a central internal rubric/reference, not a sixth task playbook and not a public workspace file. Do not duplicate its full D00-D19 rubric here.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D09 | `11_exemplar_language_profile.md` | `03_WRITING_STRUCTURE.md#Exemplar Language Profile` |
| D14 | `20_reader_spine.md` | `03_WRITING_STRUCTURE.md#Reader Spine` |
| D15 | `21_manuscript_outline.md` | `03_WRITING_STRUCTURE.md#Manuscript Outline` + `#Section Jobs` |
| D16 | `22_object_granularity.md` | Primary: `03_WRITING_STRUCTURE.md#Object Granularity`; secondary claim-side detail may live in `02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity` |
| D17 | `23_surface_control.md` | Primary: `03_WRITING_STRUCTURE.md#Surface Control`; secondary claim wording may live in `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording` |
| D18 | `24_visual_plan.md` | `03_WRITING_STRUCTURE.md#Visual Plan` + `#Figure / Table Storyline` |

After updating structure content, update the matching D09/D14-D18 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## First-batch structure cards

`00-dimension-rubric.md` remains the source of truth. Use these as focused structure cards/pointers:

- **D09 style fingerprint:** record exemplar status/role, positive style rules, forbidden imitation, voice/tense, hedge strength, terminology density, banned patterns, and D12/D17 wording links. If an exemplar is cited as a source, route that fact through D07. Style never raises claim strength.
- **D14 reader spine:** record reader persona, question sequence, expected answers, linked claim/evidence/limitation, forbidden questions, and transition rationale. This is the reader path, not a section outline or manuscript prose.
- **D15 section-job matrix:** pair each section with job, input dimensions, output promise, required evidence, forbidden content, length or paragraph/function hints, and downstream constraints. Do not draft prose or let section jobs create unsupported claims.
- **D18 visual storyline/brief:** record visual id/type/status, story role, linked claim/evidence/reader step, data needed, panel order, legend job, accessibility check, and handoff. Existing visuals may point to evidence only through D06/D11; needed/deferred visuals remain plan items.
- Mechanical checks may require status/rationale, question-path shape, section/job pairing, visual status, and explicit no-visual/deferred rationale; they must not judge prose quality, rhetoric, visual quality, or figure correctness.

## Required fields

- Exemplar language profile if user-supplied; otherwise explicit absent/deferred status.
- Reader spine: the question sequence the paper must answer.
- Manuscript outline and section jobs: what each section must accomplish.
- Object granularity at the planning/reader level.
- Surface control: terms, tone, syntax/wording constraints, and what not to say.
- Figure storyline and visual plan: how figures/tables support the argument.
- Paragraph/function map at planning level.
- Downstream drafting notes and constraints.

## Ask when missing

Ask one focused question at a time. Prefer this order:

1. “What question should the reader ask first, and what answer should the paper give?”
2. “What job should each major section perform?”
3. “Which figures/tables carry the main story, and in what order?”
4. “What object/variable/mechanism granularity should the writing preserve?”
5. “Which terms, tone, or wording style should downstream writing control?”
6. “Are there supplied exemplar papers or language profiles, or should that dimension be marked absent/deferred?”
7. “Where should the paper be conservative because evidence is limited?”

## Question card pattern

Use this card when D14-D18 or the `writing-structure` blocker is first unresolved.

```text
Current stage: Writing Structure
Dimension / blocker: D14-D18 / writing-structure
Why this matters: downstream drafting needs an argument spine, section jobs, object granularity, surface controls, and figure storyline before prose is written.
Mode chosen: candidate-confirmation when route/materials/claims are confirmed enough for an outline proposal; reconciliation when D16/D17 disagree across files.
Question: Which structure decision should I record or reconcile?
Options:
A. reader spine — write the problem→object→method/result→limitation question path to 03_WRITING_STRUCTURE.md#Reader Spine.
B. section jobs — write section-level responsibilities to #Manuscript Outline and #Section Jobs.
C. object/surface control — write primary D16/D17 guidance to #Object Granularity and #Surface Control.
D. visual storyline — write existing/needed figure-table sequence to #Figure / Table Storyline and #Visual Plan.
E. D16/D17 conflict — run reconciliation and choose whether structure-side or claim-side wording is authoritative before compile.
F. no visuals / deferred visuals — record rationale and downstream limitation; pass only if no active claim depends on missing visual evidence.
Agent action after answer: update 03_WRITING_STRUCTURE.md and D14/D15/D16/D17/D18 rows in 00_DIMENSION_INDEX.md; if claim wording changes, update 02_CLAIM_EVIDENCE_BOUNDARY.md too.
```

## Hard blocker

Block design-pack compilation if:

- reader spine is absent;
- manuscript outline or section jobs are absent;
- figure/table storyline is absent or explicitly irrelevant without explanation;
- object granularity is unhandled;
- surface control is unhandled;
- exemplar language profile is neither supplied nor explicitly absent/deferred.

## Output sections

Update `03_WRITING_STRUCTURE.md` with:

- Exemplar language profile;
- Reader spine;
- Manuscript outline;
- Section jobs;
- Object granularity;
- Surface control;
- Figure / table storyline;
- Visual plan;
- Paragraph/function map;
- Drafting constraints.

## Index update examples

- Filled reader spine: `D14 | filled | reader question sequence supplied | 03_WRITING_STRUCTURE.md#Reader Spine | yes`.
- Absent exemplar profile: `D09 | absent | owner supplied no exemplar papers; plugin must not invent style source | Handoff: downstream writer uses generic route constraints | no`.

## Do not assume

- Do not draft full manuscript prose.
- Do not add claims that were not approved in the claim-evidence boundary.
- Do not invent figures; mark missing figures as absent or needed.
- Do not invent exemplar papers or venue language profiles.
