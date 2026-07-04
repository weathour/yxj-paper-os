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
