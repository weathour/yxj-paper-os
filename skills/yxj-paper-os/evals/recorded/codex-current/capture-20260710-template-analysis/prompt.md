Behavior capture contract: behavior-prompt/1.3
Evaluate each model-visible scenario using the complete skill below. Return only one JSON object with exactly 20 response objects: {"responses":[...]}.
Each response must use this structural shape; empty arrays are permitted:
{"question": {"count": 0, "target": null}, "readiness_updates": [], "scenario_id": "B00", "selected_actions": [], "side_effects": [], "target_dimensions": [], "target_scopes": [], "updates": []}
Use exact case-sensitive selected_actions tokens from: ["ASK_OWNER", "COMPILE_SCOPED_HANDOFF", "DEPENDENCY_RECHECK", "DERIVE", "INITIALIZE_WORKSPACE", "INSPECT", "KEEP_CLAIM_INACTIVE", "PROPOSE", "RECONCILE", "RECORD_OBSERVATION"].
Use exact side_effects tokens from: ["external_execution", "full_scan", "pdf_pseudo_parse", "subagents", "template_analysis", "template_intake"]. target_dimensions may contain only D00-D19 IDs; target_scopes may contain only explicit SCOPE-* IDs from the scenario context. updates and readiness_updates must contain JSON objects, never prose strings. Each update object should name record_kind and operation plus the relevant changed field; each readiness object should name scope_id and readiness when applicable.
The output schema requires every update/readiness object key; use null or an empty grounding array for non-applicable values rather than omitting keys.
SKILL SHA-256: 1433160eb9d168219beff650689d3699e7d4b473e948cf305e4f2eac6ebce236
<!-- BEHAVIOR_CAPTURE_SKILL_START -->
---
name: yxj-paper-os
description: Prepare and inspect a paper-planning workspace with a sparse cognitive kernel, composable academic lenses, scoped writing handoffs, and optional target-journal/target-topic corpus statistics or template analysis.
---

# yxj-paper-os: thin cognitive kernel

This skill is model-led reasoning over one public skill and six Markdown workspace files. It is not a fixed workflow, state machine, form-completion score, or semantic judge. Read the whole situation, inspect/derive before asking, and use only the sparse records needed for the requested scope.

## Public contract

- Preserve the six filenames, D00-D19 index, public index columns/status values, and schema version `0.2`.
- Initialize only from `assets/templates/`; never create a seventh public workspace file.
- `04_WRITING_DESIGN_PACK.md` is a structural, scoped handoff. It never claims research, manuscript, submission, publication, or semantic readiness.
- Generated state may exist only below `<workspace>/.yxj-paper-os/`: the read-only dashboard at `dashboard.html` and, when `venue-template` analysis is genuinely requested, reproducible artifacts below `template-analysis/`. These hidden artifacts are not public workspace files or evidence anchors.

## Five kernel invariants

1. **Epistemic distinction:** substantive decision/material/claim records distinguish origin (`artifact-observed`, `owner-stated`, `model-derived`, `model-proposed`), claim support (`evidence-supported`, `evidence-partial`, `evidence-unsupported`, `not_applicable`), resolution, and grounding.
2. **Whole-situation synthesis:** consider all six files, available local artifacts, owner statements, active conflicts, changed records, and requested writing surface before choosing what to do.
3. **Qualitative highest-value action:** choose the action that most reduces consequential uncertainty or unlocks the requested surface. Do not use a numeric score, fixed scan order, or one-question script.
4. **Dependency recheck:** when a DEC/M/C record changes, update a parseable Dependency Recheck declaration for affected D IDs/scopes; recheck or mark only those dependents stale/candidate/blocked.
5. **Scoped writer-ready:** judge each requested `SCOPE-*` independently. A ready scope has declared inputs, satisfied/not-applicable requirements, no stale/candidate/blocked dependency, blocker=`none`, next action=`none`, and a resolvable output pointer. Other scopes remain partial, blocked, or deferred.

## Canonical action families

Use any zero or more of these unordered families in a turn:

`inspect`, `record-observation`, `derive`, `propose`, `reconcile`, `ask-owner`, `dependency-recheck`, `compile-scoped-handoff`, `keep-claim-inactive`, `initialize-workspace`.

Actions describe judgment, not runtime states. Simple metadata edits remain lightweight. Optional native subagents are allowed only when volume, ambiguity, or claim risk materially benefits; they never become mandatory stages and never ask the owner or execute downstream skills directly.

## Composable lenses

Load `references/lenses/README.md` and then only relevant modules. Lenses may compose from 0..N IDs; they are not exclusive paper types. The canonical registry maps module files to IDs, including method/system/benchmark forms in `contribution-evidence-forms.md` and the conditional `venue-template` lens. An inactive lens creates no empty requirement table and does not block unrelated scopes.

Every lens provides activation signals, theory/distinctions, sufficiency predicates, safe derivations, owner-only decisions, dependency invalidation, failure modes, workspace projection, and writer-ready consequences. Theory informs judgment; it never prescribes question order.

### Venue-template corpus analysis

Load `references/lenses/venue-template.md` as the authority when the requested writing surface materially benefits from analysis of supplied target-venue, target-topic, article-form, or exemplar documents. Keep the corpus vocabulary canonical: `documents` contain stable `doc_id` values and belong to an explicit `partition`; venue, topic, article form, time cohort, and exemplar role are separate axes.

Every manifest declares a non-empty `design_question` plus non-empty, unique
`design_metric_ids` from the versioned registry that operationalize that question. Its optional
`analysis_mode` (default `case_set`) records the weakest honest requested mode
that could answer it:

- `case_set`: one or more document profiles; no corpus norm or distribution claim;
- `exploratory`: descriptive patterns for the available, potentially heterogeneous documents, with values, denominators, missingness, and limitations visible;
- `distributional`: paper-level distributions within comparable declared partitions, without implying random sampling, causality, venue fit, or an optimal target.

The requested mode is an upper bound, not a guaranteed effective conclusion.
Read effective strength from each metric/profile entry's valid observations,
missingness, uncertainty, partition comparability, and `target_kind`; downgrade
to `watch_only`, `not_applicable`, exploratory language, or case comparison when
the measured output cannot support the requested mode. `sample_size_label` is
paper-count context only. It never decides quality, venue fit,
representativeness, corpus sufficiency, or design-rule adoption.
Compute effective strength only from the declared `design_metric_ids`; unrelated
ready metrics cannot upgrade a question whose selected metric is unavailable.

There is no universal corpus-size threshold. A missing or small corpus limits only the linked template-analysis/design scope. Supported local text/structure inputs may be analyzed mechanically; a PDF is metadata-only unless the owner supplies a traceable externally extracted derivative. Never decode, grep, OCR, or otherwise pretend to parse PDF bytes.

The analyzer may write only reproducible artifacts under `.yxj-paper-os/template-analysis/`, including `corpus-summary.json` and `design-profile.json`. Treat raw measurements as artifact observations and aggregations/comparisons as grounded derivations. Every corpus-derived design-profile entry remains `model-proposed/candidate`—including case-set `watch_only` outcomes, exploratory patterns, distributional `soft_band` rules, sequences, and presence rules. Running the analyzer, observing a stable distribution, or compiling a hidden profile never confirms or adopts such a rule. Only a new owner-grounded decision may accept, adapt, reject, or deliberately diverge from it. A writing scope whose necessary design choice is still an unresolved candidate is `partial`, not ready; an unrelated scope keeps its prior readiness. A template statistic can shape D09/D15/D17/D18 writing design, but it can never become D06 evidence, increase D11 support, prove source truth or novelty, or predict acceptance.

Use a workspace-root `template-corpus/1.0` JSON manifest when analysis is requested. It requires the concrete `design_question` and registry-backed `design_metric_ids`; optional `analysis_mode` records the requested ceiling and defaults to `case_set`. Its `documents` need `doc_id`, a manifest-relative `path`, `format` (`markdown|html|jats|txt`), and `partition` (`primary_match|venue_control|topic_control|exemplar`); retain venue, topic tags, article type, year, language, derivative provenance, and optional annotation path when known. A document that violates an inclusion rule may carry `inclusion_exception` only as an owner-grounded object with non-empty `reason`, `origin=owner-stated`, `resolution=confirmed`, and a resolvable `decision_pointer`. Free-text exceptions are invalid, and an exception authorizes inclusion without erasing non-comparability. Resolve the analyzer relative to this `SKILL.md`, then run:

```bash
python3 <this-skill-directory>/scripts/analyze_template_corpus.py --manifest <workspace>/template-corpus.json
```

The fixed output contract is `manifest.json`, `metric-registry.json`, `paper-metrics.jsonl`, `objects.jsonl`, `corpus-summary.json`, `design-profile.json`, `extraction-warnings.json`, and `analysis-report.html` directly below `.yxj-paper-os/template-analysis/`. Never hand-edit those generated files; change inputs/annotations and rerun.

## Sparse recording rules

Only record a conditional table when it carries real information:

- `00_DIMENSION_INDEX.md`: `Writing Scopes` is the universal readiness registry; Active Lenses, Conditional Requirements, and Dependency Recheck are conditional.
- `00_PROJECT_ROUTE.md`: add Decision Records only for consequential choices/conflicts.
- `01_MATERIALS_INVENTORY.md`: add Material Records only for real artifacts/facts/results/evidence/source/governance/absence records.
- `02_CLAIM_EVIDENCE_BOUNDARY.md`: add Claim Records only for proposed, active, downgraded, deferred, or rejected claims.
- `03_WRITING_STRUCTURE.md`: add Scoped Writing Plan when designing a requested surface.
- `04_WRITING_DESIGN_PACK.md`: add Scoped Handoff when compiling D19.

Blank cells are invalid. Use literal `none` only where the table contract permits it. Free prose is not a foreign key. Preserve local artifact locators, hidden template-analysis pointers, and six-file `file#heading` pointers. `model-proposed` records remain candidate/unresolved/rejected; acceptance creates a new grounded record rather than mutating origin.

## Adaptive operating guidance

1. Inspect existing files, local materials, and the requested output surface; initialize missing files only when asked.
2. Synthesize all relevant dimensions and active lenses. Record direct observations and safe derivations before asking.
3. Ask one concise owner question only for an unresolved consequential commitment, authority conflict, evidence permission, or wording choice. State consequence and landing pointer; offer defer/absent when valid.
4. Write the answer/observation to its canonical sparse record, update the relevant D row, and declare dependent rechecks when a DEC/M/C record changes.
5. Compile or refresh only the affected scoped handoff. Keep unrelated scope blockers explicit.
6. If `venue-template` is active and supported documents are supplied, run the local template analyzer once, then inspect `corpus-summary.json` and `design-profile.json` and project only metric families relevant to the requested surface; do not project malformed, stale, unsupported, or ungrounded output.
7. Run `python3 skills/yxj-paper-os/scripts/verify_design_pack.py <workspace>` for structural lint, and add `--require-handoff` only when a scoped D19 handoff is requested.

## Question card (optional rendering)

```text
Decision / observation: <one answerable item>
Why it matters: <affected scope or dependency>
What is already observed/derived: <short grounded summary>
Owner choice if needed: A ...  B ...  C defer/absent
Write landing: <file#heading and D row>
```

## Boundaries

Do not draft manuscript prose, invent claims/evidence/sources/results, search citations by default, execute external skills, write outside the six workspace files except an owner-requested corpus input manifest and the bounded `.yxj-paper-os/dashboard.html` / `.yxj-paper-os/template-analysis/` generated surfaces, add runtime services, or claim scholarly quality. The manifest is analysis configuration, not a seventh public planning file. Do not copy hidden raw statistics wholesale into public Markdown. Mechanical validators check structure, declared relations, hashes, arithmetic, and supported input capabilities only; they do not prove academic truth, novelty, venue fit, statistical generalizability, prose/visual quality, or future model behavior.
<!-- BEHAVIOR_CAPTURE_SKILL_END -->
VENUE-TEMPLATE REFERENCE SHA-256: 5db40d223a2e27e64040308a34fd4f94c94fb3dff9ef190ec3396d7f3cf6389d
<!-- BEHAVIOR_CAPTURE_VENUE_TEMPLATE_START -->
# Venue-Template Corpus Analysis Lens

## Purpose and activation signals

This is the authority for statistical analysis of owner-supplied target-venue, target-topic, article-form, or exemplar documents when the result can change a requested writing surface. It remains inactive when generic writing guidance is sufficient. A known venue alone does not activate corpus intake, and absent templates never block unrelated scopes.

Activation is justified by at least one concrete design question, such as section allocation, rhetorical-move placement, citation density, sentence/paragraph rhythm, figure/table organization, caption/reference placement, or a deliberate departure from an observed convention.

## Theory and distinctions

### Corpus axes are not interchangeable

Use `documents` as the canonical collection, a stable `doc_id` for each source, and an explicit `partition` for every comparison. Keep these axes separate:

- official venue instructions: source constraints, not corpus distributions;
- target-venue/target-topic documents: joint matches;
- target-venue/topic-control documents: venue-oriented controls;
- venue-control/target-topic documents: topic-oriented controls;
- article/contribution form and time cohort: mandatory comparability labels when relevant;
- exemplars: cases that may inspire a design but never define a norm by themselves.

Published-document patterns are descriptive associations. They do not prove that a venue caused a pattern, that the pattern is optimal, or that following it predicts acceptance.

### Analysis modes

The manifest must state a concrete non-empty `design_question` and non-empty,
unique registry-backed `design_metric_ids` that operationalize it. Optional
`analysis_mode` defaults to `case_set`; when supplied, select the weakest
requested mode that could answer the question. No mode is a mandatory
progression and no universal document-count threshold exists.

| Mode | Permitted conclusion | Required boundary |
|---|---|---|
| `case_set` | per-document observations and contrasts | no corpus norm, prevalence, distribution, or venue-wide language |
| `exploratory` | descriptive patterns in the available possibly heterogeneous set | show document values, denominators, missingness, partitions, and selection limitations |
| `distributional` | paper-level distributions inside comparable declared partitions | no random-sample, causal, optimality, or venue-fit claim; incompatible forms/versions stay separate |

Corpus sufficiency is question-specific. A small set may answer a case-comparison question while being inadequate for a distributional design rule. Record a `watch_only` rule or `not_applicable` disposition rather than manufacturing precision.

`analysis_mode` is the requested ceiling, not an automatically effective mode.
Determine the effective conclusion separately for each metric and design
surface from valid observations, missingness, uncertainty, format/language
support, and partition comparability. Effective strength may stay at the
requested level or weaken; it must never be upgraded by a count label.
Only declared `design_metric_ids` contribute to the effective-mode decision;
unrelated ready metrics cannot rescue an unavailable question-specific metric.
`sample_size_label` is descriptive paper-count context only and is not a gate
for quality, representativeness, venue fit, corpus sufficiency, mode selection,
or adoption of a design rule.

An exceptional inclusion is valid only when the document carries an
owner-grounded object with `reason`, `origin=owner-stated`,
`resolution=confirmed`, and a resolvable `decision_pointer`. A free-text waiver
is invalid. The exception authorizes retention while preserving the reason and
non-comparability; it does not silently move the document into a comparable
partition.

### Measurement and aggregation boundary

Metric definitions and format capabilities are versioned by the analyzer. Use only registered metrics and preserve their numerator, denominator, analysis unit, extraction class, missingness, and grounding.

- **Mechanical:** hashes, explicitly tagged structure/objects/references, deterministic counts, positions, arithmetic, and schema relations.
- **Heuristic:** sentence splitting, free-text section normalization, citation-pattern inference, and other declared fallible rules. Keep method/version and warnings visible.
- **Model-derived:** topic/article-form classification, rhetorical moves, citation function, claim/visual role, and writing-design interpretation. Require object-level grounding and candidate/confirmed resolution.
- **Owner-only:** target route, corpus inclusion exceptions, adoption of a design rule, and an intentional deviation.

Treat the paper as the default independent unit. Reduce nested sentences/paragraphs/objects within each paper before aggregating papers. Report `n`, eligible/measured/missing/unsupported denominators, paper-level values, median/IQR/range or categorical counts as appropriate. Zero-inflated, compositional, and sequence data require their registered summaries; one pooled mean is not an adequate substitute.

Annotation states remain distinct: only current `accepted` annotations may enter the main annotated statistic; `candidate` and `stale` coverage stays visible as uncertainty/diagnostic output and cannot be silently promoted.

### Input capability and PDF boundary

Analyze only engine-supported local `markdown`, `html`, `jats`, or plain UTF-8 `txt` inputs; each format exposes different capabilities. PDF, scanned image, and every other format are metadata-only. Never decode, grep, OCR, shell out to, or infer structure from PDF bytes. An owner-supplied extraction from PDF may be analyzed only after it is supplied as one of the supported formats and labeled with extractor/source provenance; it is not silently equivalent to the original.

### Reproducible hidden artifacts

The analyzer may write only below `<workspace>/.yxj-paper-os/template-analysis/`. The stable public integration pointers are:

- `.yxj-paper-os/template-analysis/corpus-summary.json` for measured/aggregated observations;
- `.yxj-paper-os/template-analysis/design-profile.json` for grounded candidate constraints and design rules.

The directory may also contain manifest, registry snapshot, document/object records, warnings, or reports required for reproducibility. It is generated hidden state, not a seventh public workspace file. Source hashes, method/registry versions, `documents`/`doc_id`/`partition` relations, and dependency hashes determine freshness.

### Scientific-evidence firewall

Template-corpus statistics are evidence about writing and presentation patterns only. They may shape D09/D15/D17/D18 and a scoped D19 handoff. They are never D06 scientific evidence anchors, never increase D11 claim support, and never establish citation truth, novelty, research validity, visual correctness, venue fit, or acceptance probability. Project result statistics remain governed by `evidence-results-statistics`; do not pool the two domains.

## Sufficiency predicates

| Predicate | Required state |
|---|---|
| Design question and affected scope | explicit, or lens remains inactive |
| Requested/effective mode | requested `analysis_mode` is no stronger than the question requires; emitted conclusions are weakened whenever metric-level support or comparability is insufficient |
| Document identity | every included source has `doc_id`, locator/hash, capability, and `partition` |
| Effective-mode honesty | conclusion language and `target_kind` match metric-level support rather than inheriting the requested `analysis_mode` automatically |
| Metric traceability | registered metric/method version, unit/denominator, missingness, and grounding resolve |
| Partition comparability | article form/time/method/codebook incompatibilities separated or explicitly bounded |
| Summary freshness | dependencies and source hashes current; malformed/stale artifacts excluded |
| Design profile | every requested surface has a grounded rule or explicit `watch_only`/`not_applicable` outcome |
| Evidence boundary | template observations remain outside D06/D11 scientific support |

Unsupported or missing optional metrics do not block a scope. A requested surface is blocked only when its declared design responsibility depends on the unavailable analysis and no conservative `watch_only`/`not_applicable` handoff is acceptable.

## Safe derivations

The model may safely:

- record explicit source capabilities, partitions, per-document measurements, and analyzer warnings;
- preserve owner-grounded inclusion exceptions and keep the exceptional document separate or explicitly bounded in affected summaries;
- aggregate only compatible paper-level observations using the registered summary method;
- distinguish official constraints, venue-linked patterns, topic-linked patterns, article-form patterns, and exemplar cases;
- translate official constraints/profile observations into the canonical rule kinds `hard_constraint`, `soft_band`, `sequence`, `presence`, or `watch_only`, then select a design disposition `follow`, `adapt`, `deliberate_divergence`, or `not_applicable`;
- propose a scope-specific design rule with source summary/profile pointers and forbidden interpretations;
- preserve a current design that intentionally differs when the owner has confirmed the rationale.

A corpus tendency initially yields `model-proposed/candidate`, not an owner decision. `hard_constraint` requires an official source locator; corpus-derived ranges use `soft_band`. An accepted proposal creates a new owner-grounded decision record rather than changing the proposal's origin.

## Owner-only decisions

The owner controls target venue/topic, article form, corpus inclusion or exception, acceptable comparators, adoption/adaptation of `soft_band` rules, and `deliberate_divergence`. An inclusion exception must resolve to a confirmed owner decision through its `decision_pointer`; do not accept a bare string as authority. Ask only when one of these choices materially changes the requested surface and cannot be derived from an existing confirmed record. Do not ask for more documents merely to reach a fixed count.

## Dependencies and invalidation

- source bytes/hash, extraction capability, or parser/method version change: stale the affected document/object measurements and dependent summaries/profiles;
- `doc_id`, partition, article form, topic/venue relation, or time cohort change: recheck affected summaries and comparisons;
- metric semantic/codebook version change: do not silently mix versions; rederive only affected metrics;
- target route or requested scope change: re-evaluate the design profile and public projection, not unrelated raw measurements;
- owner adoption/rejection/deviation change: create or revise the corresponding decision and recheck D09/D15/D17/D18/D19.

Declare only affected D IDs/scopes in `Dependency Recheck`; do not build a public runtime graph.

## Failure modes

- imposing a universal minimum corpus size;
- treating `sample_size_label` as a quality, fit, representativeness, sufficiency, or mode gate;
- treating requested `analysis_mode` as effective when metric-level support requires a weaker conclusion;
- accepting a free-text inclusion exception or letting an exception erase partition non-comparability;
- calling a single case or heterogeneous convenience set a venue distribution;
- pooling article forms, time cohorts, metric versions, or nested sentence/paragraph rows without a declared compatible reduction;
- reporting an average without `n`, denominator, missingness, and paper-level grounding;
- treating an exemplar outlier as a norm or a corpus tendency as a hard venue rule;
- interpreting bootstrap/resampling as removal of selection bias;
- pseudo-parsing PDF or untraceable extracted text;
- letting malformed/stale hidden JSON become a public design rule;
- turning template statistics into D06/D11 evidence or venue/quality/acceptance scoring;
- dumping hidden raw measurements into public Markdown or creating a seventh public file.

## Workspace projection

Project sparsely and only when the lens carries real information:

| Home | Projection |
|---|---|
| `00_DIMENSION_INDEX.md` | active lens, affected scopes, conditional requirement only when analysis is readiness-relevant, and dependency recheck |
| `00_PROJECT_ROUTE.md` | target/partition owner decisions, official constraints, accepted corpus exceptions, `deliberate_divergence` decisions |
| `01_MATERIALS_INVENTORY.md` | compact manifest/summary/profile Material Records or explicit unsupported/absence state |
| `02_CLAIM_EVIDENCE_BOUNDARY.md` | explicit firewall: design influence only; no D06/D11 support |
| `03_WRITING_STRUCTURE.md` | scope-specific statistical design profile, rule type/resolution, and `deliberate_divergence` decisions |
| `04_WRITING_DESIGN_PACK.md` | compact current summary/profile pointers, adopted/candidate design consequences, blockers, and boundary |

Do not create one public row for every metric. Preserve the hidden pointers and summarize only decisions that change the requested writing design.

## Writer-ready consequences

A template-linked writing scope may be writer-ready when its declared profile/constraint inputs are current, every active requirement is satisfied or not applicable, every candidate requiring authority is resolved or explicitly bounded, and each relevant design surface has a rule or explicit `watch_only`/`not_applicable` outcome. Other writing scopes can remain ready even when template analysis is absent, unsupported, malformed, or blocked.

Writer-ready here means only that downstream prose/visual planning can follow the declared structural constraints without inventing a convention. It does not mean the corpus is representative, the prose matches a venue, the research is valid, or the manuscript is submission-ready.
<!-- BEHAVIOR_CAPTURE_VENUE_TEMPLATE_END -->
The following projection is the entire model-visible scenario payload. Policy requirements and prohibited-answer oracle fields are intentionally absent.
<!-- MODEL_VISIBLE_SCENARIOS_START -->
{
  "scenarios": [
    {
      "context": null,
      "id": "B01",
      "situation": "observable artifact"
    },
    {
      "context": null,
      "id": "B02",
      "situation": "explicit route"
    },
    {
      "context": null,
      "id": "B03",
      "situation": "owner-only tradeoff"
    },
    {
      "context": null,
      "id": "B04",
      "situation": "reconcile structure"
    },
    {
      "context": null,
      "id": "B05",
      "situation": "owner conflict"
    },
    {
      "context": null,
      "id": "B06",
      "situation": "method survey"
    },
    {
      "context": null,
      "id": "B07",
      "situation": "hybrid lenses"
    },
    {
      "context": {
        "owner_request": "Initialize the paper-planning workspace from canonical templates",
        "public_contract": "exactly the six canonical Markdown files; no seventh public file",
        "template_source": "assets/templates/",
        "workspace_state": "The six public files appear absent and must be checked before copying"
      },
      "id": "B08",
      "situation": "owner requests initialization of a missing paper-planning workspace"
    },
    {
      "context": null,
      "id": "B09",
      "situation": "venue template"
    },
    {
      "context": null,
      "id": "B10",
      "situation": "weak support"
    },
    {
      "context": null,
      "id": "B11",
      "situation": "changed evidence"
    },
    {
      "context": null,
      "id": "B12",
      "situation": "scoped readiness"
    },
    {
      "context": null,
      "id": "B13",
      "situation": "rich answer"
    },
    {
      "context": {
        "artifact_format": "PDF",
        "linked_writing_scope": null,
        "owner_request": "Record the existing PDF in the materials inventory only",
        "template_analysis_requested": false
      },
      "id": "B14",
      "situation": "inventory a PDF artifact as metadata only without activating template analysis"
    },
    {
      "context": {
        "analysis_action": "template_analysis",
        "corpus": "one supported primary-match Markdown derivative",
        "design_metric_ids": [
          "structure.section_word_share"
        ],
        "design_question": "How should section allocation be treated as a one-document case rather than a norm?",
        "linked_dimensions": [
          "D05",
          "D09"
        ],
        "owner_choice_id": "template-design-adoption",
        "readiness_condition": "The writing scope depends on the unresolved candidate design choice",
        "requested_analysis_mode": "case_set",
        "requested_output": "Reproducible analysis plus a candidate writing-design profile for owner review; no design rule has been owner-adopted",
        "scope_ids": [
          "SCOPE-TEMPLATE"
        ]
      },
      "id": "B15",
      "situation": "supported single-document template case set"
    },
    {
      "context": {
        "analysis_action": "template_analysis",
        "corpus": "heterogeneous owner-supplied papers with mixed venues or article forms",
        "design_metric_ids": [
          "structure.median_paragraph_words",
          "object.total_count"
        ],
        "design_question": "Which paragraph and object-density patterns are visible without claiming a norm?",
        "linked_dimensions": [
          "D05",
          "D09"
        ],
        "owner_choice_id": "template-design-adoption",
        "readiness_condition": "The writing scope depends on the unresolved candidate design choice",
        "requested_analysis_mode": "exploratory",
        "requested_output": "Reproducible analysis plus a candidate writing-design profile for owner review; no design rule has been owner-adopted",
        "scope_ids": [
          "SCOPE-TEMPLATE"
        ]
      },
      "id": "B16",
      "situation": "heterogeneous supplied corpus supports exploratory description only"
    },
    {
      "context": {
        "analysis_action": "template_analysis",
        "corpus": "at least five comparable primary-match papers with adequate coverage and uncertainty",
        "design_metric_ids": [
          "structure.section_word_share",
          "object.figure_position_norm"
        ],
        "design_question": "What section-allocation and figure-position bands describe comparable target papers?",
        "linked_dimensions": [
          "D09",
          "D15",
          "D18"
        ],
        "owner_choice_id": "template-design-adoption",
        "readiness_condition": "The writing scope depends on the unresolved candidate design choice",
        "requested_analysis_mode": "distributional",
        "requested_output": "Reproducible analysis plus a candidate writing-design profile for owner review; no design rule has been owner-adopted",
        "scope_ids": [
          "SCOPE-TEMPLATE"
        ]
      },
      "id": "B17",
      "situation": "comparable declared partitions support distributional template design"
    },
    {
      "context": {
        "corpus": "PDF bytes only; no traceable supported derivative",
        "design_metric_ids": [
          "structure.section_count",
          "sequence.object_type_order"
        ],
        "design_question": "What template organization should guide the manuscript?",
        "linked_dimensions": [
          "D05",
          "D09"
        ],
        "owner_choice_id": "supported-template-derivative",
        "scope_ids": [
          "SCOPE-TEMPLATE",
          "SCOPE-METHODS"
        ],
        "scope_state": {
          "SCOPE-METHODS": "already ready and has no declared dependency on the template corpus",
          "SCOPE-TEMPLATE": "depends on the unavailable template analysis"
        }
      },
      "id": "B18",
      "situation": "PDF-only template corpus is unsupported and unrelated Methods remains ready"
    },
    {
      "context": {
        "boundary": "template measurements describe writing/presentation only",
        "linked_dimensions": [
          "D06",
          "D09",
          "D11"
        ],
        "owner_choice_id": "independent-scientific-evidence-or-deferral",
        "owner_request": "Use a template frequency as support for a scientific claim",
        "scope_ids": [
          "SCOPE-CLAIM"
        ]
      },
      "id": "B19",
      "situation": "owner asks template corpus statistic to support a scientific claim"
    },
    {
      "context": {
        "decision": "Owner explicitly chooses a manuscript design outside a grounded soft band",
        "grounding": "existing candidate design-profile entry",
        "linked_dimensions": [
          "D01",
          "D09",
          "D15",
          "D18",
          "D19"
        ],
        "scope_ids": [
          "SCOPE-TEMPLATE"
        ]
      },
      "id": "B20",
      "situation": "owner confirms a deliberate divergence from a corpus-derived soft band"
    }
  ]
}
<!-- MODEL_VISIBLE_SCENARIOS_END -->
