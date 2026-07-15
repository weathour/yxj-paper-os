# Playbook 01 — Materials Inventory

Use this playbook when `01_MATERIALS_INVENTORY.md` is missing or incomplete, or when D05/D06/D07/D08 in `00_DIMENSION_INDEX.md` are unhandled.

## Schema 0.3 material and template-source contract

Scientific materials, sources, and evidence continue to use M-* Material Records; do not add EVID-* or a parallel scientific-source registry. Template-design documents use separate TPL-* identities in Template Design Sources with exactly: Template source ID | Design role | Design question | Source/provenance pointer | Access state | Local derivative pointer | Source SHA-256 | Hidden dossier pointer | Design-only state | Scientific-source promotion pointer.

Access state is full_text&#124;owner_derivative&#124;metadata_only&#124;snippet_only&#124;inaccessible. TPL-* defaults to design_only. A dual-role publication uses distinct TPL-* and M-* records, and promotion is never inferred. A ready scope may ground template handling not_applicable and require neither dossier nor analyzer.

The hidden dossier owns detailed acquisition/provenance, copyright/access limits,
locator set, fingerprint/freshness, semantic eligibility, and optional analyzer
correlation. 01 mirrors only the exact public columns above; normalize surrounding
cell whitespace, POSIX relative paths, lowercase enums/SHA-256, and otherwise preserve
UTF-8 text. Correlation to analyzer state is valid only with explicit
`analysis_id` + `doc_id` + `source_sha256`; title/filename/order matching is forbidden.

## Dimension rubric reference

For schema-0.3 sufficiency, question depth, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is the central internal rubric/reference. This file is one of five task playbooks, not a public workspace file; it translates rubric gaps into compact question cards and write landings without overriding the D00-D19 ladder.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D05 | `Material inventory` | `01_MATERIALS_INVENTORY.md` |
| D06 | `Evidence inventory` | `01_MATERIALS_INVENTORY.md#Evidence Inventory` + `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map` |
| D07 | `Source and citation bank` | `01_MATERIALS_INVENTORY.md#Source and Citation Bank` |
| D08 | `Research dossier` | `01_MATERIALS_INVENTORY.md#Research Dossier`; 04 carries only a compact authority pointer |

After updating material content, update the matching D05-D08 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Question-depth translator guide

Use the central rubric to inspect the current Dxx record and scope readiness, then translate only the unresolved gap into the next compact card. Do not introduce another status vocabulary, public file, D ID, index column, manuscript prose, citation, source truth, result, evidence anchor, external skill execution, semantic score, or runtime orchestration.

| D ID(s) | Default card mode | Ask a depth follow-up when... | Reconcile or conflict-check when... | Write landing |
|---|---|---|---|---|
| D05 | `quick-form` for several low-risk locations; `focused-question` for one blocking artifact | planned vs completed material state, baseline/metric scope, artifact location, or absence consequence controls a claim or route | D05 material state conflicts with D06 anchors, D11 claims, or D18 visual/table needs | `01_MATERIALS_INVENTORY.md#Results and Experiments`, `#Figures and Tables`, or related material sections, then D05 row |
| D06 | `focused-question` | support strength, limitation, or cross-link is needed to prevent an unsupported claim | D11, D12, or D18 relies on a missing, vague, or mismatched evidence anchor | `01_MATERIALS_INVENTORY.md#Evidence Inventory` plus D11 handoff if needed, then D06 row |
| D07 | `focused-question` for source facts; `quick-form` for supplied source role labels | source role, citation status, locator/version, permission, limitation, or handoff need affects downstream writing | source role conflicts with D08 dossier notes, D06 evidence anchors, or D11 claim support | `01_MATERIALS_INVENTORY.md#Source and Citation Bank`, then D07 row |
| D08 | `candidate-confirmation` from supplied notes; otherwise `focused-question` | gap, conflict, counterevidence, or unresolved source need constrains contribution, risk, or reader path | dossier notes conflict with D07 sources, D10 contribution, D13 risks, or D14 spine | `01_MATERIALS_INVENTORY.md#Research Dossier` and any D19 dossier handoff, then D08 row |

## Adaptive D07/D08 source and dossier pointers

`00-dimension-rubric.md` remains the source of truth for D07/D08 sufficiency. Use this playbook only for focused intake and boundary cards:

- `source ≠ evidence ≠ claim`: a source list (D07) or dossier note (D08) cannot support or strengthen a claim unless a D06 evidence anchor exists and D11 maps the claim to that anchor.
- D07 should organize supplied source/citation candidates by category-family intent: source identity, source role, citation status, owner confirmation, locator/version or explicit absence, key use, limitation, reuse permission, and handoff need.
- D08 should organize research-context notes by category-family intent: research/context boundary, study notes, theme synthesis, conflict map, gap hypothesis, counterevidence, unresolved source needs, and downstream consequence.
- If no sources or dossier notes are supplied, record absence/defer status and risk; do not search, invent BibTeX, infer novelty, or imply related-work adequacy.
- Mechanical checks may require a table shape or explicit absent/deferred reason; they must not verify citation truth, source authority, novelty, or claim support.

## Additional material planning additions

Use these additions to inventory planning inputs for downstream writing surfaces. They do not create claims, citations, results, figures, tables, captions, or reproducibility proof.

- **Citation-function and related-work roles:** group supplied sources or dossier notes by intended function, such as background, contrast, baseline, method lineage, dataset/context, gap, counterevidence, limitation, or reviewer expectation. A citation-function role is a writing handoff, not evidence for a claim unless D06/D11 binds it.
- **Method/reporting/repro materials:** record the presence, location, absence, or deferral of protocol details, parameters, code/data, baselines, metrics, ablations, random seeds, environment notes, ethical/availability statements, and supplement material.
- **Results / visual / caption / table / accessibility materials:** record where result artifacts, figure/table source files, statistics displays, caption notes, alt-text/accessibility constraints, legends, units, and table schemas live, or why they are absent/deferred.
- **Front-matter material hooks:** record owner-supplied graphical hook assets, key result anchors, or visual-hook constraints only as inputs to D18/D19; do not draft title, abstract, keywords, hook copy, or captions.
- **Absent/deferred consequence language:** every missing source, method artifact, result, visual, caption, table, or accessibility input must state whether downstream writing can continue conservatively, must defer a claim, or must reject the route.

## Conditional template-design material intake

Activate intake only for a concrete writing-design question. Record TPL-* identity, eligible role, provenance/access state, local derivative/hash when available, design_only state, and affected scope. Grounded model-semantic reading is the primary interpretation path and projects through the hidden semantic dossier; metadata/snippets/inaccessible sources cannot support paragraph/object observations.

The deterministic analyzer is optional for a declared measurable question. If used, retain documents/doc_id/partition, selected metric, requested/effective mode, denominator, missingness, and current fixed-output pointers. There is no universal document-count gate. Missing analyzer output is neutral when scope handling is semantic-only, generic fallback, or grounded not_applicable.

PDF, scan, metadata-only, malformed, or unsupported records remain provenance but cannot be pseudo-parsed or represented as full-text reading. No template record is D06 evidence or citation truth.

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

Ask one focused question at a time. Choose the next question adaptively from the unresolved owner decision or highest-leverage dependency; the following prompts are unordered examples:

- “Where are the main results, tables, or experiment logs?”
- “Which figures/tables already exist, and where are they?”
- “What baselines and metrics support the core comparison?”
- “Which evidence anchor supports the strongest planned claim?”
- “Which sources or citation candidates are already known or supplied by you?”
- “Which related-work notes are absent and should be marked absent/deferred rather than invented?”
- “Which expected materials are absent and should be marked absent rather than invented?”

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
C. evidence anchor for a claim exists — assign an M-* Material Record and link it later to D11.
D. absent material — record explicit absence in #Explicit Absences and prevent supported claims that depend on it.
E. deferred material — record the missing artifact and consequence as a handoff; do not invent results or anchors.
Agent action after answer: update 01_MATERIALS_INVENTORY.md and the D05/D06 rows in 00_DIMENSION_INDEX.md; if a claim is affected, keep D11 deferred until anchored.
```

## Additional question-card seeds

Use these cards only when the matching material surface is the next blocker. Keep source/citation facts owner-supplied and separate from evidence anchors.

### Citation-function / related-work roles

```text
Current stage: Materials
Dimension / blocker: D07-D08 with D10/D13/D14 / intro-related citation-function roles
Why this matters: downstream introduction and related-work structure need source functions and conflict/gap notes without pretending they prove novelty or claims.
Mode chosen: focused-question only if source use triggers scientific_commitment; quick-form if supplied sources need low-risk role labels.
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
