# Playbook 03 — Writing Structure

Use this playbook when `03_WRITING_STRUCTURE.md` is missing, when downstream writing lacks a clear structure, or when D09/D14/D15/D16/D17/D18 in `00_DIMENSION_INDEX.md` are unhandled.

## Schema 0.3 authoritative detailed-design contract

03 owns exactly these A-K surfaces: Section Map; Paragraph Map; Paragraph Payload and Boundary Map; Important Paragraph Register; Controlled Sentence Frames; Surface Language Contract; Visual Blueprint; Cross-Surface Traceability; Template Rule Projection; Grounded Soft Budgets; Scoped Writing Plan. 04 stores only counts and pointers.

Every writer-ready section owns ordered paragraphs; every paragraph has one function row and one payload/boundary row. Important-paragraph selection is qualitative and adaptive, with no score or fixed list. Each selected important paragraph owns ordered controlled frames that specify logical slots and constraints but stop before paste-ready prose.

The seven coverage keys are section_paragraph_map, surface_language_contract, visual_caption_blueprint, cross_surface_traceability, template_rule_provenance, soft_budgets, and important_paragraph_frames. Each is satisfied or grounded not_applicable per scope.

For a `semantic_dossier` rule, the hidden definition owns observation grounding, rule
kind, candidate transfer, suggested disposition, origin, limitation, and source
freshness. 03 owns affected scopes, surface, resolution, actual disposition, and
decision ID; the hidden application snapshot mirrors those applied fields. Any
disagreement blocks only linked scopes with `TEMPLATE_PROJECTION_MISMATCH`.
Official, semantic, quantitative, and generic-fallback compatibility is the shared
contract in `scripts/template_design_contract.py`; no mixed grounding or borrowed
hard constraint is allowed.

## Dimension rubric reference

For schema-0.3 sufficiency, question depth, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is the central internal rubric/reference. This file is one of five task playbooks, not a public workspace file; it translates rubric gaps into compact question cards and write landings without overriding the D00-D19 ladder.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D09 | `Exemplar language profile` | `03_WRITING_STRUCTURE.md#Template Rule Projection` |
| D14 | `Reader spine` | `03_WRITING_STRUCTURE.md#Paragraph Map` |
| D15 | `Manuscript outline` | `03_WRITING_STRUCTURE.md#Section Map` |
| D16 | `Object granularity` | Primary: `03_WRITING_STRUCTURE.md#Paragraph Payload and Boundary Map`; secondary claim-side detail may live in `02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity` |
| D17 | `Surface control` | Primary: `03_WRITING_STRUCTURE.md#Surface Language Contract`; secondary claim wording may live in `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording` |
| D18 | `Visual plan` | `03_WRITING_STRUCTURE.md#Visual Blueprint` |

After updating structure content, update the matching D09/D14-D18 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Question-depth translator guide

Use the central rubric to inspect the current Dxx record and scope readiness, then translate only the unresolved gap into the next compact card. Do not introduce another status vocabulary, public file, D ID, index column, manuscript prose, citation, source, result, evidence anchor, external skill execution, semantic score, or runtime orchestration.

| D ID(s) | Default card mode | Ask a depth follow-up when... | Reconcile or conflict-check when... | Write landing |
|---|---|---|---|---|
| D09 | `focused-question` for exemplar status; `candidate-confirmation` for supplied style constraints | a style rule affects route fit, claim strength, overclaim control, terminology, or forbidden imitation | exemplar/style handling conflicts with D07 source status, D12 wording, or D17 surface controls | `03_WRITING_STRUCTURE.md#Template Rule Projection`, then D09 row |
| D14 | `candidate-confirmation` from confirmed route/material/claim inputs | a hidden reviewer question, answer order, or transition tradeoff would change the argument path | reader spine conflicts with D04 audience, D10 contribution, D11 evidence, D15 outline, or D18 visuals | `03_WRITING_STRUCTURE.md#Paragraph Map`, then D14 row |
| D15 | `candidate-confirmation`; `focused-question` when route/type owner choice is missing | a section job prevents unsupported prose, omitted limitations, wrong paper type, or missing reporting input | outline jobs conflict with D04 route, D11 evidence, D13 limitations, D14 spine, or D18 visuals | `03_WRITING_STRUCTURE.md#Section Map`, then D15 row |
| D16/D17 primary | `reconciliation` when claim-side wording exists; otherwise `focused-question` | object level, term choice, tone, or wording surface controls claim scope, audience framing, or domain precision | primary structure notes conflict with claim-side D16/D17, D10-D12 boundaries, D09 style, or D04 route | `03_WRITING_STRUCTURE.md#Paragraph Payload and Boundary Map` and `#Surface Language Contract`, then D16/D17 rows or claim-side handoff |
| D18 | `candidate-confirmation` from confirmed materials; `focused-question` for one blocking visual/table | a visual, caption, table, statistic display, or accessibility constraint changes the evidence story or handoff | visual plan conflicts with D05 materials, D06 evidence, D11 claims, D14 spine, or D15 section jobs | `03_WRITING_STRUCTURE.md#Visual Blueprint`, then D18 row and D19 handoff if needed |

## Adaptive structure cards

`00-dimension-rubric.md` remains the source of truth. Use these as focused structure cards/pointers:

- **D09 style fingerprint:** record exemplar status/role, positive style rules, forbidden imitation, voice/tense, hedge strength, terminology density, banned patterns, and D12/D17 wording links. If an exemplar is cited as a source, route that fact through D07. Style never raises claim strength.
- **D14 reader spine:** record reader persona, question sequence, expected answers, linked claim/evidence/limitation, forbidden questions, and transition rationale. This is the reader path, not a section outline or manuscript prose.
- **D15 section-job matrix:** pair each section with job, input dimensions, output promise, required evidence, forbidden content, length or paragraph/function hints, and downstream constraints. Do not draft prose or let section jobs create unsupported claims.
- **D18 visual storyline/brief:** record visual id/type/status, story role, linked claim/evidence/reader step, data needed, panel order, legend job, accessibility check, and handoff. Existing visuals may point to evidence only through D06/D11; needed/deferred visuals remain plan items.
- Mechanical checks may require status/rationale, question-path shape, section/job pairing, visual status, and explicit no-visual/deferred rationale; they must not judge prose quality, rhetoric, visual quality, or figure correctness.

## Additional structure planning additions

Use these additions as structure and handoff prompts only. They may define jobs, constraints, move order, and checklist state; they must not draft title, abstract, keywords, introduction prose, methods prose, result prose, captions, table text, or graphical-hook copy.

- **Front matter / hook brief:** plan route-consistent title/abstract/keyword/hook constraints, evidence-safe promise level, hook asset status, visual dependency, and downstream handoff notes under D14/D15/D18/D19.
- **Intro / related-work move sequence:** plan reader moves such as problem setting, gap/context, source-role placement, contribution bridge, counterevidence/limitation placement, and transition rationale. Citation-function roles come from D07/D08 and claims remain bounded by D10-D13.
- **Method / reporting / reproducibility section jobs:** plan method/reporting section responsibilities, required material inputs, reproducibility checklist state, availability/supplement handoff, and forbidden promises.
- **Results / visual / caption / table / accessibility storyline:** plan result order, figure/table sequence, caption/legend jobs, statistic-display handoff, alt-text/accessibility constraints, and non-visual fallback notes.
- **Templates / validator handoff:** record where structure decisions should appear in `04_WRITING_DESIGN_PACK.md` and which checks are structural only; never imply semantic scoring, external execution, or finished manuscript readiness.

## Optional exemplar signals

When venue/template material can change a requested surface, state the design question and eligible roles, then use grounded model-semantic reading as the primary path. Project only located, scope-relevant rules into Template Rule Projection. Use the deterministic analyzer only for an explicit measurable question and preserve its metric, mode, partition, denominator, missingness, and artifact pointer. Semantic and quantitative rules remain separately typed.

Template analysis is conditional. A grounded not_applicable scope needs neither dossier nor analyzer. No template source or rule strengthens D06/D11 evidence, proves venue fit, or blocks an unrelated D19 scope.

## Required fields

- Section ownership, sequence, jobs, reader-state transitions, inputs, promises, obligations, and prohibitions.
- Paragraph ownership, order, adjacency, function, payload, claim/citation/object boundary, qualifications, and output promise.
- Qualitatively selected important paragraphs and their ordered controlled frames.
- Applicable language, visual/caption/accessibility, traceability, template-rule, and soft-budget records, or grounded not_applicable handling.
- Compact scoped writing-plan pointer for 04.

## Ask when missing

Ask one focused question at a time. Choose the next question adaptively from the unresolved owner decision or highest-leverage dependency; the following prompts are unordered examples:

- “What question should the reader ask first, and what answer should the paper give?”
- “What job should each major section perform?”
- “Which figures/tables carry the main story, and in what order?”
- “What object/variable/mechanism granularity should the writing preserve?”
- “Which terms, tone, or wording style should downstream writing control?”
- “Are there supplied exemplar papers or language profiles, or should that dimension be marked absent/deferred?”
- “Where should the paper be conservative because evidence is limited?”

## Question card pattern

Use this card when D14-D18 or the `writing-structure` blocker is first unresolved.

```text
Current stage: Writing Structure
Dimension / blocker: D14-D18 / writing-structure
Why this matters: downstream drafting needs an argument spine, section jobs, object granularity, surface controls, and figure storyline before prose is written.
Mode chosen: candidate-confirmation when route/materials/claims are confirmed enough for an outline proposal; reconciliation when D16/D17 disagree across files.
Question: Which structure decision should I record or reconcile?
Options:
A. reader spine — write the problem→object→method/result→limitation question path to 03_WRITING_STRUCTURE.md#Paragraph Map.
B. section jobs — write section-level responsibilities to #Section Map.
C. object/surface control — write primary D16/D17 guidance to #Paragraph Payload and Boundary Map and #Surface Language Contract.
D. visual storyline — write the figure-table sequence and object responsibilities to #Visual Blueprint.
E. D16/D17 conflict — run reconciliation and choose whether structure-side or claim-side wording is authoritative before compile.
F. no visuals / deferred visuals — record rationale and downstream limitation; pass only if no active claim depends on missing visual evidence.
Agent action after answer: update 03_WRITING_STRUCTURE.md and D14/D15/D16/D17/D18 rows in 00_DIMENSION_INDEX.md; if claim wording changes, update 02_CLAIM_EVIDENCE_BOUNDARY.md too.
```

## Additional question-card seeds

Use these cards when the writing surface, not the underlying evidence or route, is the current blocker. If a card exposes a triggered four-category gate, stop and route it to the owning playbook.

### Front matter / hook brief

```text
Current stage: Writing Structure
Dimension / blocker: D14-D15/D18 with D04/D09/D12/D19 / front-matter-hook brief
Why this matters: downstream front matter needs route-safe promise level, hook role, and visual dependency without receiving drafted title, abstract, keyword, or hook prose.
Mode chosen: candidate-confirmation when route/claim/evidence are confirmed; focused-question when owner must choose hook status or forbidden promise.
Question: What front-matter or hook planning brief should I record?
Options:
A. route-safe promise brief — record the allowed promise level, target audience, and forbidden wording links in #Paragraph Map or #Surface Language Contract.
B. abstract/keyword constraint brief — record function, scope, and route constraints without drafting text.
C. visual/graphical hook brief — record existing/needed/deferred/rejected hook status and link it to #Visual Blueprint.
D. defer front matter — record downstream risk and keep D19 front-matter handoff cautious.
E. reject hook route — record why the hook/front-matter promise should not be used.
Agent action after answer: update 03_WRITING_STRUCTURE.md#Paragraph Map, #Surface Language Contract, #Visual Blueprint, and D14/D15/D18 rows; hand off D19 constraints without drafting front matter.
```

### Introduction / related-work move sequence

```text
Current stage: Writing Structure
Dimension / blocker: D07/D08/D10-D14/D15 / intro-related move sequence
Why this matters: introduction and related-work planning needs a source-role and reader-move path that does not invent citations or unsupported novelty.
Mode chosen: candidate-confirmation when supplied sources and claims support a move sequence; reconciliation if source-role notes conflict with claim boundaries.
Question: Which intro/related-work move should I plan or constrain?
Options:
A. reader move sequence — record problem→gap/context→contribution→limitation or alternate route as #Paragraph Map.
B. citation-function placement — record where background, contrast, baseline, lineage, gap, or counterevidence roles should appear, using only D07/D08-supplied material.
C. bridge to contribution — record the transition job and required D10/D11 support without adding new claims.
D. defer move — record missing source, evidence, or owner decision and keep the move inactive.
E. reject unsupported gap/novelty move — record forbidden question or transition rationale.
Agent action after answer: update #Paragraph Map, #Section Map, and D14/D15 rows; hand off any source or claim gap to D07/D08/D10-D13.
```

### Method / reporting / reproducibility section jobs

```text
Current stage: Writing Structure
Dimension / blocker: D04/D05/D06/D13/D15/D19 / method-reporting-repro section jobs
Why this matters: method structure must expose reporting inputs, reproducibility gaps, and availability handoffs before downstream prose is attempted.
Mode chosen: candidate-confirmation when materials and route imply section jobs; focused-question when one artifact controls a required section.
Question: Which method/reporting/repro job should I add or defer?
Options:
A. method job — record section responsibility, required material input, and forbidden unsupported claim in #Section Map.
B. reproducibility checklist job — record code/data/baseline/metric/environment/availability state and D19 handoff.
C. limitation job — record where missing artifacts or risks must remain visible.
D. defer job — record missing material and keep the section job constrained.
E. reject reporting promise — record that downstream writing must not claim checklist/compliance/reproducibility beyond supplied material.
Agent action after answer: update #Section Map, #Section Map, #Paragraph Payload and Boundary Map, and D15/D19 pointers; hand off material gaps to D05/D06/D13.
```

### Results / visual / caption / table / accessibility handoff

```text
Current stage: Writing Structure
Dimension / blocker: D05/D06/D11/D14/D15/D18/D19 / results-visual-caption-table-accessibility handoff
Why this matters: results and visuals need a story order, caption/table jobs, and accessibility constraints tied to evidence anchors and reader steps.
Mode chosen: candidate-confirmation when result artifacts are confirmed; focused-question when one figure/table/caption handoff is blocking.
Question: Which result or visual structure should I record?
Options:
A. result narrative path — record result order, linked claim/evidence, and limitation in #Paragraph Map or #Visual Blueprint.
B. caption/table job — record what each caption, legend, or table must explain, including units/statistic-display handoff, without drafting caption/table prose.
C. accessibility handoff — record alt-text, color/contrast, table readability, or non-visual fallback requirement in #Visual Blueprint.
D. no/deferred visual — record rationale and prevent any active claim from depending on the missing visual.
E. reject visual-support use — record that the figure/table/storyline cannot support the claim.
Agent action after answer: update #Visual Blueprint and #Section Map, and D18/D19 pointers; reconcile with D11-D13 if claim strength changes.
```

## Hard blocker

Block schema-0.3 writer-ready when any ready section lacks a paragraph, any paragraph lacks its payload row, a selected important paragraph lacks frames, an applicable companion surface lacks records, a not_applicable surface lacks rationale, or a claim/payload/template pointer exceeds its authority.

## Output sections

Update only the authoritative A-K headings named in the schema-0.3 contract above. Do not recreate legacy reader-spine, outline, style-profile, visual-storyline, or statistics tables as parallel authorities; project their useful content into section, paragraph, frame, language, visual, rule, budget, and edge records.

## Index update examples

- Filled reader spine: `D14 | filled | reader question sequence supplied | 03_WRITING_STRUCTURE.md#Paragraph Map | yes`.
- Absent exemplar profile: `D09 | absent | owner supplied no exemplar papers; plugin must not invent style source | Handoff: downstream writer uses generic route constraints | no`.

## Do not assume

- Do not draft full manuscript prose.
- Do not add claims that were not approved in the claim-evidence boundary.
- Do not invent figures; mark missing figures as absent or needed.
- Do not invent exemplar papers or venue language profiles.
