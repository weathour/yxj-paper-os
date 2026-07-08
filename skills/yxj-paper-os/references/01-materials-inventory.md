# Playbook 01 — Materials Inventory

Use this playbook when `01_MATERIALS_INVENTORY.md` is missing or incomplete, or when D05/D06/D07/D08 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, question-depth, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is the central internal rubric/reference. The central rubric decides sufficiency and question-depth; this file is not a sixth task playbook and not a public workspace file. This playbook translates the current rubric gaps into compact question cards and write landings; it must not duplicate or override the central D00-D19 ladder.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D05 | `Material inventory` | `01_MATERIALS_INVENTORY.md` |
| D06 | `Evidence inventory` | `01_MATERIALS_INVENTORY.md#Evidence Inventory` + `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map` |
| D07 | `Source and citation bank` | `01_MATERIALS_INVENTORY.md#Source and Citation Bank` |
| D08 | `Research dossier` | `01_MATERIALS_INVENTORY.md#Research Dossier` + `04_WRITING_DESIGN_PACK.md#Research Dossier Notes` |

After updating material content, update the matching D05-D08 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Question-depth translator guide

Use the central rubric to judge whether the current Dxx answer is missing, minimum-only, standard-ready, deferred, absent, or rejected. Use this table only to translate that gap into the next compact card; do not add public files, D IDs, index columns/statuses, manuscript prose, citations, source truth, results, evidence anchors, external skill execution, semantic scoring, or runtime orchestration.

| D ID(s) | Default card mode | Ask a depth follow-up when... | Reconcile or conflict-check when... | Write landing |
|---|---|---|---|---|
| D05 | `quick-form` for several low-risk locations; `focused-question` for one blocking artifact | planned vs completed material state, baseline/metric scope, artifact location, or absence consequence controls a claim or route | D05 material state conflicts with D06 anchors, D11 claims, or D18 visual/table needs | `01_MATERIALS_INVENTORY.md#Results and Experiments`, `#Figures and Tables`, or related material sections, then D05 row |
| D06 | `focused-question` | support strength, limitation, or cross-link is needed to prevent an unsupported claim | D11, D12, or D18 relies on a missing, vague, or mismatched evidence anchor | `01_MATERIALS_INVENTORY.md#Evidence Inventory` plus D11 handoff if needed, then D06 row |
| D07 | `focused-question` for source facts; `quick-form` for supplied source role labels | source role, citation status, locator/version, permission, limitation, or handoff need affects downstream writing | source role conflicts with D08 dossier notes, D06 evidence anchors, or D11 claim support | `01_MATERIALS_INVENTORY.md#Source and Citation Bank`, then D07 row |
| D08 | `candidate-confirmation` from supplied notes; otherwise `focused-question` | gap, conflict, counterevidence, or unresolved source need constrains contribution, risk, or reader path | dossier notes conflict with D07 sources, D10 contribution, D13 risks, or D14 spine | `01_MATERIALS_INVENTORY.md#Research Dossier` and any D19 dossier handoff, then D08 row |

## First-batch D07/D08 source and dossier pointers

`00-dimension-rubric.md` remains the source of truth for D07/D08 sufficiency. Use this playbook only for focused intake and boundary cards:

- `source ≠ evidence ≠ claim`: a source list (D07) or dossier note (D08) cannot support or strengthen a claim unless a D06 evidence anchor exists and D11 maps the claim to that anchor.
- D07 should organize supplied source/citation candidates by category-family intent: source identity, source role, citation status, owner confirmation, locator/version or explicit absence, key use, limitation, reuse permission, and handoff need.
- D08 should organize research-context notes by category-family intent: research/context boundary, study notes, theme synthesis, conflict map, gap hypothesis, counterevidence, unresolved source needs, and downstream consequence.
- If no sources or dossier notes are supplied, record absence/defer status and risk; do not search, invent BibTeX, infer novelty, or imply related-work adequacy.
- Mechanical checks may require a table shape or explicit absent/deferred reason; they must not verify citation truth, source authority, novelty, or claim support.

## Second-batch material planning additions

Use these additions to inventory planning inputs for downstream writing surfaces. They do not create claims, citations, results, figures, tables, captions, or reproducibility proof.

- **Citation-function and related-work roles:** group supplied sources or dossier notes by intended function, such as background, contrast, baseline, method lineage, dataset/context, gap, counterevidence, limitation, or reviewer expectation. A citation-function role is a writing handoff, not evidence for a claim unless D06/D11 binds it.
- **Method/reporting/repro materials:** record the presence, location, absence, or deferral of protocol details, parameters, code/data, baselines, metrics, ablations, random seeds, environment notes, ethical/availability statements, and supplement material.
- **Results / visual / caption / table / accessibility materials:** record where result artifacts, figure/table source files, statistics displays, caption notes, alt-text/accessibility constraints, legends, units, and table schemas live, or why they are absent/deferred.
- **Front-matter material hooks:** record owner-supplied graphical hook assets, key result anchors, or visual-hook constraints only as inputs to D18/D19; do not draft title, abstract, keywords, hook copy, or captions.
- **Absent/deferred consequence language:** every missing source, method artifact, result, visual, caption, table, or accessibility input must state whether downstream writing can continue conservatively, must defer a claim, or must reject the route.

## Template Quantification Gate material intake

Use `Template Corpus / Quantification Basis` to ask for and record the required corpus: at least 3 parseable full-text templates with source/locator and source/similarity rationale when the gate applies. Citation-only, abstract-only, metadata-only, missing, or unparseable records are useful provenance but do not count toward the minimum. If fewer than 3 parseable full texts are available, ask the owner for the missing materials and carry blocked-not-valid-handoff.

Template statistics guide D09/D15/D17/D18 writing design only; they are not D06 evidence anchors and do not verify citation truth, source authority, novelty, or claim support.

## Required fields

- Experiment/result locations.
- Figure and table locations.
- Data locations.
- Code locations.
- Baselines or comparison methods.
- Metrics and evaluation dimensions.
- Evidence inventory: anchors, type, location, supported claim/dimension, status.
- User-provided source/citation candidates, if any.
- Existing related-work/research-dossier notes, if any.
- Existing draft fragments, if any.
- Explicitly absent materials and their consequences.

## Ask when missing

Ask one focused question at a time. Prefer this order:

1. “Where are the main results, tables, or experiment logs?”
2. “Which figures/tables already exist, and where are they?”
3. “What baselines and metrics support the core comparison?”
4. “Which evidence anchor supports the strongest planned claim?”
5. “Which sources or citation candidates are already known or supplied by you?”
6. “Which related-work notes are absent and should be marked absent/deferred rather than invented?”
7. “Which expected materials are absent and should be marked absent rather than invented?”

## Question card pattern

Use this card when D05/D06 or the `core-materials` blocker is first unresolved.

```text
Current stage: Materials
Dimension / blocker: D05-D06 / core-materials
Why this matters: claims cannot be planned until real materials and evidence anchors are locatable or explicitly absent.
Mode chosen: quick-form if the workspace is empty; focused-question if one evidence anchor is blocking a claim.
Question: Which material/evidence state should I record now?
Options:
A. results/figures/tables exist — record paths or labels in 01_MATERIALS_INVENTORY.md#Results and Experiments and #Figures and Tables.
B. data/code/baselines/metrics exist — record locations and categories in the matching material sections.
C. evidence anchor for a claim exists — assign an anchor such as E1 in #Evidence Inventory and link it later to D11.
D. absent material — record explicit absence in #Explicit Absences and prevent supported claims that depend on it.
E. deferred material — record the missing artifact and consequence as a handoff; do not invent results or anchors.
Agent action after answer: update 01_MATERIALS_INVENTORY.md and the D05/D06 rows in 00_DIMENSION_INDEX.md; if a claim is affected, keep D11 deferred until anchored.
```

## Second-batch question-card seeds

Use these cards only when the matching material surface is the next blocker. Keep source/citation facts owner-supplied and separate from evidence anchors.

### Citation-function / related-work roles

```text
Current stage: Materials
Dimension / blocker: D07-D08 with D10/D13/D14 / intro-related citation-function roles
Why this matters: downstream introduction and related-work structure need source functions and conflict/gap notes without pretending they prove novelty or claims.
Mode chosen: focused-question if source facts are owner-gated; quick-form if several supplied sources need low-risk role labels.
Question: Which citation-function or related-work role should I record for supplied material?
Options:
A. background or method lineage — record the supplied source/note role in 01_MATERIALS_INVENTORY.md#Source and Citation Bank or #Research Dossier.
B. baseline or comparison context — record the role and locator, then require D06/D11 before it supports any claim.
C. gap, conflict, or counterevidence note — record the note as context and link downstream consequence to D13/D14.
D. no supplied sources — mark D07/D08 absent or deferred with a handoff; do not search or invent citations.
E. rejected citation role — record why the source/note must not be used for that function.
Agent action after answer: update D07/D08 sections and 00_DIMENSION_INDEX.md; if the role affects a claim or reader move, hand off to D10/D13/D14 without changing claim strength.
```

### Method / reporting / reproducibility checklist materials

```text
Current stage: Materials
Dimension / blocker: D05-D06 with D13/D15/D19 / method-reporting-repro checklist
Why this matters: method and reproducibility sections can only report artifacts that exist or are explicitly absent/deferred.
Mode chosen: quick-form when multiple low-risk artifact locations can be collected; focused-question when one artifact blocks a route or claim.
Question: Which method/reporting/repro material state should I record?
Options:
A. protocol or parameter material exists — record location, version, and section/job handoff in #Code / Implementation or #Results and Experiments.
B. data/code/baseline/metric material exists — record location and evidence-anchor candidate while keeping claim support routed through D06/D11.
C. availability, ethics, supplement, or environment note exists — record the statement category and handoff need without drafting statement prose.
D. absent/deferred artifact — record consequence for method claims, reproducibility wording, and D19 handoff.
E. rejected reproducibility claim — record forbidden wording so downstream writing cannot imply artifact availability.
Agent action after answer: update 01_MATERIALS_INVENTORY.md material sections, D05/D06 rows, and any D13/D15/D19 handoff note.
```

### Results / visual / caption / table / accessibility materials

```text
Current stage: Materials
Dimension / blocker: D05-D06 with D11/D18/D19 / results-visual-caption-table-accessibility handoff
Why this matters: result and visual planning needs locatable artifacts, caption/table inputs, and accessibility notes before downstream handoff.
Mode chosen: focused-question when a single figure/table/result blocks a claim; quick-form when several artifact paths are known.
Question: Which result or visual material state should I record?
Options:
A. result artifact exists — record path/label, metric/statistic display, and candidate evidence anchor in #Results and Experiments.
B. figure/table source exists — record file/location, panel/table schema, units, legend/caption notes, and D18 handoff in #Figures and Tables.
C. accessibility input exists — record alt-text need, color/contrast issue, table readability, or non-visual fallback as a D18/D19 handoff note.
D. visual/table/caption material absent or deferred — record downstream limitation; do not allow active claims to depend on it.
E. rejected visual evidence use — record that the visual/table cannot support the claim and keep D11 deferred or rejected.
Agent action after answer: update 01_MATERIALS_INVENTORY.md#Results and Experiments, #Figures and Tables, #Evidence Inventory, and D05/D06/D18/D19 rows as applicable.
```

## Hard blocker

Block design-pack compilation if materials are not locatable and no explicit absence/defer/reject decision exists for:

- results;
- figures/tables;
- data/code when they are relevant to the claimed contribution;
- baselines;
- metrics;
- evidence anchors for core claims;
- source/citation bank status.

## Output sections

Update `01_MATERIALS_INVENTORY.md` with:

- Results and experiments;
- Figures and tables;
- Data sources;
- Code / implementation;
- Baselines;
- Metrics;
- Evidence inventory;
- Source and citation bank;
- Research dossier;
- Existing text fragments;
- Explicit absences.

## Index update examples

- Filled materials: `D05 | filled | experiment locations provided | 01_MATERIALS_INVENTORY.md#Results and Experiments | yes`.
- Absent citation bank: `D07 | absent | owner has not supplied citation candidates; plugin must not search | Handoff: downstream writing may request sources from owner | yes`.

## Do not assume

- Do not invent experiment outcomes.
- Do not convert planned experiments into completed evidence.
- Do not treat “we can probably show” as evidence.
- Do not perform native citation search or invent BibTeX entries.
