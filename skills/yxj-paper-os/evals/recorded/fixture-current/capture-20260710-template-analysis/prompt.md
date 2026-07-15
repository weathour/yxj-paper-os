Behavior capture contract: behavior-prompt/2.1
Evaluate each model-visible scenario using the complete skill below. Return only one JSON object with exactly 15 response objects: {"responses":[...]}.
Each response must use this structural shape; empty arrays are permitted:
{"question": {"count": 0, "target": null}, "readiness_updates": [], "scenario_id": "B00", "selected_actions": [], "side_effects": [], "target_dimensions": [], "target_scopes": [], "updates": []}
Use exact case-sensitive selected_actions tokens from: ["ASK_OWNER", "DERIVE", "INSPECT", "PROJECT", "VALIDATE"].
Use exact side_effects tokens from: ["external_execution", "full_scan", "pdf_pseudo_parse", "subagents", "template_analysis", "template_intake"]. target_dimensions may contain only D00-D19 IDs; target_scopes may contain only explicit SCOPE-* IDs from the scenario context. updates and readiness_updates must contain JSON objects, never prose strings. Each update object should name record_kind and operation plus the relevant changed field; each readiness object should name scope_id and readiness when applicable. Controlled frames and captions must remain functional placeholder skeletons, never paste-ready manuscript prose.
The output schema requires every update/readiness object key; use null or an empty grounding array for non-applicable values rather than omitting keys.
SKILL SHA-256: 208cff025efb4c9c2c39f3cc0bcc4d44ee30c0bb3dc4df75b39c3148af339198
<!-- BEHAVIOR_CAPTURE_SKILL_START -->
---
name: yxj-paper-os
description: Prepare a controlled schema-0.3 prewriting design workspace through repository evidence, model-semantic template reading, composable academic lenses, and scoped handoffs without drafting manuscript prose.
---

# yxj-paper-os: evidence-grounded prewriting design

This skill is an adaptive reasoning contract over one public skill and six Markdown
workspace files. It is not a fixed pipeline, questionnaire, state machine, readiness
score, or manuscript writer. Inspect and derive before asking; stop when the requested
scope has a validated design handoff or an explicit blocker.

## Public and hidden contract

- Preserve exactly the six filenames, D00-D19 identities, index columns/statuses, and
  schema marker `0.3`; never create a seventh public workspace file.
- `00_DIMENSION_INDEX.md` is the sole scope-readiness authority. `03` owns detailed
  section/paragraph/frame/language/visual/edge/rule/budget design. `04` is a compact
  pointer/count/blocker/handoff manifest and never copies readiness.
- `02_CLAIM_EVIDENCE_BOUNDARY.md` is the sole scientific claim/support/uncertainty/
  wording ceiling. Template rules cannot increase it.
- Hidden state may exist only below `<workspace>/.yxj-paper-os/`: the read-only
  dashboard, the agent-authored `template-analysis/semantic-dossier.json`, accepted
  analyzer annotations, and optional fixed analyzer outputs. Hidden state is neither a
  seventh public file nor D06/D11 evidence.
- Schema-0.2 workspaces are legacy inputs. Preserve their scientific records and use
  the agent-led, non-destructive recompilation in `references/04-design-pack-compiler.md`;
  do not carry old `writer-ready` forward or auto-migrate placeholders.

## Wake contract: establish the target before process

From the request and repository, infer or state:

1. target outcome and requested writing `SCOPE-*`;
2. success criteria for the controlled handoff;
3. current scientific and design evidence;
4. boundaries, dependencies, and prohibited claims/actions;
5. expected six-file/hidden outputs; and
6. stop condition: validated handoff, grounded defer, or explicit blocker.

Inspect the six files, concrete repository artifacts, existing hidden state, and
changed dependencies before asking. Record direct observations and safe reversible
derivations first. Ask one focused question only when missing authority changes the
result through a four-category gate.

## Kernel invariants

1. **Epistemic identity:** preserve `artifact-observed`, `owner-stated`,
   `model-derived`, and `model-proposed`; resolution never rewrites origin.
2. **Scientific/design separation:** `M-*`/`C-*` own scientific material and claims;
   `TPL-*`/`TOBS-*`/semantic `TRULE-*` are design-only. Dual role requires separate IDs
   and an explicit scientific-source promotion decision.
3. **Whole-situation synthesis:** consider all relevant route, material, claim,
   limitation, template, and dependency evidence before choosing the next action.
4. **Selective invalidation:** recheck only linked scopes/records; never globally stale
   unrelated work or infer a runtime dependency graph.
5. **Detailed scoped readiness:** every paragraph is functionally designed; selected
   important paragraphs receive controlled frames; applicable companion surfaces are
   satisfied or grounded `not_applicable`; 04 resolves to current authorities.
6. **Design-only firewall:** official presentation constraints, exemplar patterns,
   semantic observations, analyzer outputs, and generic fallback never establish
   scientific truth, novelty, venue fit, acceptance likelihood, or claim support.

## Four owner gates

Only these categories require an owner question when triggered:

- `scientific_commitment`: evidence ceiling, scientific referent, or claim commitment;
- `argument_spine`: overall argument, contribution order, or primary-result narrative;
- `material_local_tradeoff`: a local choice with materially different reader meaning;
- `deliberate_divergence`: departure from a grounded template pattern.

Routine grounded template discovery, dossier organization, paragraph-function design,
important-paragraph selection, terminology repair, accessibility completion,
optional-analyzer use, and reversible rule adoption/adaptation/rejection do not require
confirmation. Preserve model origin when the agent resolves them.

## Adaptive reasoning obligations

Interleave or revisit these obligations as evidence changes; do not expose them as a
stage registry:

- inspect requested scope, repository, six-file state, and dependencies;
- derive safe decisions and activate only triggered lenses;
- separate scientific sources from template-design sources;
- state a concrete template design question before discovery/reading/analysis;
- semantically deep-read eligible documents and ground observations to locators;
- use the optional deterministic analyzer only for a declared measurable question;
- synthesize section/paragraph, payload, frame, language, visual, traceability,
  provenance, and soft-budget design;
- resolve only triggered four-gate questions;
- project compact decisions, recheck dependencies, compile 04, and validate.

Canonical action families remain unordered: `inspect`, `derive`, `project`, `ask`,
and `validate`. They describe the chosen action, not an exposed stage trace.

## Composable lenses

Read `references/lenses/README.md`, resolve the unique `Lens ID` to `Module path`, and
load only relevant modules. Lenses are conditional reasoning theories, not exclusive
paper types. Generic fallback is valid only as
`lens:<registered-id>#<real-h2-or-h3-slug>` with its installed lens fingerprint.

Each active lens provides activation/scope, substantive theory, repository inputs and
safe derivations, sufficiency predicates, four-gate mapping, invalidation, failures/
non-goals, six-file plus hidden projection, and detailed writer-ready consequences.

## Model-semantic template design: primary path

When template literature can materially change a requested surface:

1. state the design question and eligible roles
   (`official_venue|target_topic|article_form|time_cohort|control|exemplar`);
2. inspect local eligible sources first; when useful, use available agent
   search/research tools for external discovery and record query/date/URL/role/access
   provenance—this adds no runtime network dependency;
3. distinguish current official presentation constraints from descriptive exemplar or
   corpus patterns;
4. semantically deep-read full text or traceable derivatives, record precise locators,
   paraphrased observations, uncertainty/non-transfer notes, copyright/access limits,
   hashes, and freshness;
5. persist one hidden dossier at
   `.yxj-paper-os/template-analysis/semantic-dossier.json` using the documented
   `assets/template-analysis/semantic-dossier.schema.json` contract with
   `method=model_semantic_deep_reading`;
6. preserve one shared `TPL-*` identity between hidden document and 01, and one shared
   semantic `TRULE-*` identity between hidden definition/application snapshot and 03;
7. treat any disagreement as `TEMPLATE_PROJECTION_MISMATCH` for linked scopes—never
   choose a last writer; and
8. project only compact scope-relevant source/rule/handling pointers into 01/03/04.

The dossier stores no full copyrighted paper or long copied passage. Metadata-only,
snippet-only, inaccessible, stale, or untraceable sources cannot ground paragraph/
object semantic observations. A URL-only reading is at most `recorded_at_access`; the
validator never fetches remote content. `TPL-*` and analyzer `doc_id` correlate only
through explicit `analysis_id` + `doc_id` + `source_sha256`.

Validate a dossier read-only with:

```bash
python3 <this-skill-directory>/scripts/verify_semantic_dossier.py \
  <workspace>/.yxj-paper-os/template-analysis/semantic-dossier.json \
  --workspace <workspace>
```

## Optional deterministic analyzer

The analyzer is non-default, never a readiness prerequisite, and answers only a
concrete metric-backed design question. Semantic-only, generic-fallback, and grounded
template-`not_applicable` scopes require no analyzer artifact.

If used, a `template-corpus/1.0` manifest declares `design_question`, registry-backed
`design_metric_ids`, stable `doc_id`, supported local format, and explicit partition.
Requested `analysis_mode` (`case_set|exploratory|distributional`) is only a ceiling;
effective conclusions weaken with missingness, capability, uncertainty, or
non-comparability. No universal document-count threshold exists and
`sample_size_label` is never a quality/readiness/fit gate. PDF/scans remain
metadata-only unless a traceable supported derivative is supplied; never pseudo-parse
PDF bytes.

When the question concerns bibliography/citation layout, preserve per-paper reference
inventory, years/source forms, citation regions, candidate citation functions, shared-
work match method/confidence, denominators, missingness, and uncertainty. Exact counts
require explicit boundaries; citation function remains model-derived. These data may
shape D14/D15/D17 design but never establish source truth, relevance, importance,
novelty, or bibliography eligibility.

Run only when justified:

```bash
python3 <this-skill-directory>/scripts/analyze_template_corpus.py \
  --manifest <workspace>/template-corpus.json
```

Fixed outputs are `manifest.json`, `metric-registry.json`, `paper-metrics.jsonl`,
`objects.jsonl`, `corpus-summary.json`, `design-profile.json`,
`extraction-warnings.json`, and `analysis-report.html` below
`.yxj-paper-os/template-analysis/`. Never hand-edit them. `template-annotations/1.0`
remains a separate optional analyzer input. Analyzer writes preserve the semantic
dossier byte-for-byte; dossier writes preserve fixed outputs and accepted annotations.

Analyzer `candidate_action=follow|adapt|deliberate_divergence|not_applicable` maps only
to **suggested** disposition. Actual `Disposition` remains `candidate`,
`Origin=model-proposed`, and `Resolution=candidate` until a separate grounded design
decision. Compatibility across `official_constraint|semantic_dossier|quantitative_analysis|generic_fallback`
is defined once in `scripts/template_design_contract.py`; mixed grounding or borrowed
hard-constraint authority is invalid.

## Universal detailed design

Every planned paragraph receives functional design. For every requested paragraph,
define ownership, order/adjacency, function, reader
state in/out, claim/material/object payload boundary, qualification, output promise,
and forbidden overclaim. Select important paragraphs adaptively and qualitatively by
commitment, uncertainty/counterevidence, argument load, misreading cost, template
sensitivity, or formula/citation/visual dependency. Only selected paragraphs need one
or more ordered `FRM-*` controlled frames.

Frames define sentence function, proposition target, clause/relation order, required
payload IDs, language contract, and forbidden realization. They must not become
polished sentences requiring cosmetic edits. Complete applicable language, visual/
caption/accessibility, direct-edge traceability, template-rule provenance, and grounded
soft-budget surfaces without numeric readiness or importance scoring.

## Sparse projection and validation

- 00: sole scope readiness, active lenses/requirements, selective dependency recheck;
- 00 route: discovery authority and resolved four-gate decisions;
- 01: separate scientific `M-*` and design-only `TPL-*` authorities;
- 02: sole scientific claim/support/wording ceiling;
- 03: authoritative A-K detailed design and applied `TRULE-*` state;
- 04: exactly seven coverage rows per scope, template mode, blockers/prohibitions, and
  pointer-only handoff.

Use `none` only where the table contract permits it. Keep typed references parseable,
origins stable, and hidden/public mirrors synchronized. Run the bounded structural
checks relevant to changed surfaces; mechanical validation never judges insight,
novelty, prose/visual quality, or acceptance.

## Focused question card

```text
Gate: <one of four categories>
Decision: <one answerable choice>
Why it matters: <scope and consequence>
Observed/derived: <grounded summary>
Options: A ...  B ...  C defer when valid
Write landing: <record and file#heading>
```

## Stop and safety boundary

Stop when the requested scope has current inputs, complete detailed functional design,
resolved triggered gates, synchronized hidden/public projections, no active linked
blocker, and a validated 04 handoff—or when a grounded defer/blocker is explicit.

Never draft manuscript/title/abstract/caption/table prose, invent claims/evidence/
sources/results/visuals, execute downstream writing/review/submission skills, perform
credentialed release actions, add a dependency/service/daemon/watcher/runtime graph,
auto-migrate 0.2, or claim scholarly/semantic quality. External discovery uses only
available agent tools with provenance and does not become plugin runtime behavior.
<!-- BEHAVIOR_CAPTURE_SKILL_END -->
VENUE-TEMPLATE REFERENCE SHA-256: a8d5d9c51d7e8d2b1262c4314809613800516d5aa6cc0722fd54aab9de58a832
<!-- BEHAVIOR_CAPTURE_VENUE_TEMPLATE_START -->
# Venue-Template Semantic Design Lens

## Purpose and activation signals

This is the authority for semantic-reading-first design from eligible target-venue, target-topic, article-form, control, or exemplar documents when the result can change a requested writing surface. It remains inactive when grounded repository design or labeled generic fallback is sufficient. A known venue alone does not activate template intake, and absent templates never block unrelated scopes.

Activation requires a concrete design question and affected `SCOPE-*`, such as section/paragraph responsibility, rhetorical-move placement, terminology/claim-verb control, citation layout, figure/table/caption organization, or a deliberate departure from an observed pattern. Inspect local materials first. When useful, the agent may use available external search/research tools to discover eligible documents, but it records query/date/URL/role/access provenance and never adds a runtime network dependency or upgrades metadata/snippets to semantic reading.

## Theory and distinctions

### Model-semantic deep reading is primary

State the design question before discovery or reading. For each eligible full-text or traceable derivative, assign one shared `TPL-*` identity, record provenance/access/copyright limits and fingerprint/freshness, locate observations as `TOBS-*`, and persist them in `.yxj-paper-os/template-analysis/semantic-dossier.json`. Project only scope-relevant `TRULE-*` rows into 03 and compact source/handling pointers into 01/04. The dossier is design-only hidden state, not an analyzer input, seventh public file, citation authority, or D06/D11 evidence.

Distinguish official presentation constraints from published-paper patterns. A current official artifact-observed rule may constrain presentation; an exemplar or corpus pattern is descriptive and adaptable. Routine grounded adoption/adaptation/rejection is agent-led. Ask only when `scientific_commitment`, `argument_spine`, `material_local_tradeoff`, or `deliberate_divergence` is triggered.

The deterministic analyzer is optional and non-default. Use it only when a declared measurable question benefits from reproducible counts, distributions, sequences, or presence checks. Semantic and quantitative rules remain separately typed; no mixed-grounding rule is permitted.

### Optional analyzer corpus axes are not interchangeable

Use `documents` as the canonical collection, a stable `doc_id` for each source, and an explicit `partition` for every comparison. Keep these axes separate:

- official venue instructions: source constraints, not corpus distributions;
- target-venue/target-topic documents: joint matches;
- target-venue/topic-control documents: venue-oriented controls;
- venue-control/target-topic documents: topic-oriented controls;
- article/contribution form and time cohort: mandatory comparability labels when relevant;
- exemplars: cases that may inspire a design but never define a norm by themselves.

Published-document patterns are descriptive associations. They do not prove that a venue caused a pattern, that the pattern is optimal, or that following it predicts acceptance.

### Optional analyzer modes

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
- **Owner-gated:** target route/inclusion authority and only the four consequence-bearing categories; routine grounded rule adoption/adaptation/rejection remains agent-led.

Treat the paper as the default independent unit. Reduce nested sentences/paragraphs/objects within each paper before aggregating papers. Report `n`, eligible/measured/missing/unsupported denominators, paper-level values, median/IQR/range or categorical counts as appropriate. Zero-inflated, compositional, and sequence data require their registered summaries; one pooled mean is not an adequate substitute.

Annotation states remain distinct: only current `accepted` annotations may enter the main annotated statistic; `candidate` and `stale` coverage stays visible as uncertainty/diagnostic output and cannot be silently promoted.

### Input capability and PDF boundary

Analyze only engine-supported local `markdown`, `html`, `jats`, or plain UTF-8 `txt` inputs; each format exposes different capabilities. PDF, scanned image, and every other format are metadata-only. Never decode, grep, OCR, shell out to, or infer structure from PDF bytes. An owner-supplied extraction from PDF may be analyzed only after it is supplied as one of the supported formats and labeled with extractor/source provenance; it is not silently equivalent to the original.

### Reproducible hidden artifacts

The analyzer may write only below `<workspace>/.yxj-paper-os/template-analysis/`. The stable public integration pointers are:

- `.yxj-paper-os/template-analysis/corpus-summary.json` for measured/aggregated observations;
- `.yxj-paper-os/template-analysis/design-profile.json` for grounded candidate constraints and design rules.

The same directory may also contain the agent-authored `semantic-dossier.json` and accepted `template-annotations/1.0` inputs. These remain separately typed: analyzer fixed-bundle writes preserve the dossier byte-for-byte, dossier writes preserve fixed outputs/annotations byte-for-byte, and `TPL-*` correlates to analyzer `doc_id` only through explicit `analysis_id` + `doc_id` + `source_sha256`. The directory is hidden state, not a seventh public workspace file. Source hashes, method/registry versions, `documents`/`doc_id`/`partition` relations, and dependency hashes determine freshness.

### Bibliography and citation-layout analysis

Treat bibliography structure as a conditional template-design surface, not as
automatic literature review or source validation. When activated by the design
question, keep five layers distinct:

1. **Reference-list inventory:** per-paper explicit entry count, publication-year
   distribution, missing/ambiguous years, and source-form composition. Call a
   count exact only when the reference region and entry boundaries are explicit.
2. **Citation layout:** paper-level citation events and unique targets reduced by
   normalized writing region (introduction, related work, method, results,
   discussion, limitations, conclusion, or unresolved). Extraction order and
   unsupported section structure remain visible.
3. **Citation function:** theory, method, dataset, software, comparator,
   application context, survey, or other roles are multi-label model-derived
   candidates grounded to an entry and/or in-text context. Keyword matches alone
   do not become semantic truth.
4. **Shared works:** match across papers by stable identifier first, then by a
   declared normalized-title/fuzzy method. Report participating `doc_id` values,
   match method, confidence, and unresolved collisions; author/year similarity
   alone is insufficient.
5. **Design transfer:** derive only candidate/watch-only consequences for
   bibliography balance, recency coverage, first-use citation, section placement,
   and explicit data/software provenance. Routine grounded adoption/adaptation/
   rejection is agent-led; only one of the four gates requires an owner question.

Reference-list statistics describe how supplied papers present prior work. They
do not prove that a cited work is correct, authoritative, relevant to the target
claim, independently verified, or suitable for the manuscript. Shared citation
frequency is not importance, source-form proportions are not venue requirements,
and recentness is not quality. Keep template bibliography analysis outside D06
and D11; manuscript citation promotion still requires the source/truth workflow.

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
- project official constraints, semantic observations, optional analyzer outputs, and generic fallback through their exclusive grounding kinds and allowed rule types;
- map analyzer `follow|adapt|deliberate_divergence|not_applicable` only to **suggested** public dispositions while actual disposition remains `candidate` until an explicit agent design decision;
- propose a scope-specific design rule with source/dossier/profile pointers and forbidden interpretations;
- preserve a deliberate difference only through a resolved `deliberate_divergence` gate.

A template observation or analyzer tendency initially yields `model-derived` observation plus `model-proposed/candidate` rule, not an owner fact. `hard_constraint` requires a current official artifact locator; semantic/analyzer/generic rules cannot borrow that status. Routine reversible adoption, adaptation, rejection, and `not_applicable` resolution preserve model origin and need no owner confirmation.

## Four-gate mapping

Ask the owner only for: `scientific_commitment` when template transfer would alter a scientific referent/claim ceiling; `argument_spine` when it changes the overall contribution or primary-result order; `material_local_tradeoff` when two local realizations materially change reader interpretation; or `deliberate_divergence` when departing from a grounded pattern. Target route and true corpus-inclusion exceptions remain owner decisions when they carry those consequences. Routine discovery, role classification, dossier organization, observation recording, optional analyzer use, and grounded adoption/adaptation/rejection do not require confirmation. An inclusion exception still needs a confirmed owner decision pointer; do not ask for more documents merely to reach a count.

## Dependencies and invalidation

- source bytes/hash, extraction capability, or parser/method version change: stale the affected document/object measurements and dependent summaries/profiles;
- `doc_id`, partition, article form, topic/venue relation, or time cohort change: recheck affected summaries and comparisons;
- metric semantic/codebook version change: do not silently mix versions; rederive only affected metrics;
- target route or requested scope change: re-evaluate the design profile and public projection, not unrelated raw measurements;
- a resolved four-gate decision changes: revise the corresponding decision and recheck only linked D09/D15/D17/D18/D19 records.

Declare only affected D IDs/scopes in `Dependency Recheck`; do not build a public runtime graph.

## Failure modes

- imposing a universal minimum corpus size;
- treating `sample_size_label` as a quality, fit, representativeness, sufficiency, or mode gate;
- treating requested `analysis_mode` as effective when metric-level support requires a weaker conclusion;
- accepting a free-text inclusion exception or letting an exception erase partition non-comparability;
- calling a single case or heterogeneous convenience set a venue distribution;
- pooling article forms, time cohorts, metric versions, or nested sentence/paragraph rows without a declared compatible reduction;
- reporting an average without `n`, denominator, missingness, and paper-level grounding;
- calling inferred bibliography entries, years, source forms, citation functions,
  or fuzzy cross-paper matches exact without exposing capability and uncertainty;
- treating a shared or frequent template citation as automatically authoritative,
  relevant, or eligible for the manuscript bibliography;
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
| `00_DIMENSION_INDEX.md` | active lens, affected scopes, conditional requirement only when template design is readiness-relevant, and selective dependency recheck |
| `00_PROJECT_ROUTE.md` | discovery authority, target/role decisions, official constraints, exceptions, and triggered four-gate decisions |
| `01_MATERIALS_INVENTORY.md` | shared `TPL-*` source/provenance mirror, separate `M-*` role when dual-use, and explicit promotion boundary |
| `02_CLAIM_EVIDENCE_BOUNDARY.md` | explicit firewall: design influence only; no D06/D11 support inflation |
| `03_WRITING_STRUCTURE.md` | semantic/official/quantitative/fallback `TRULE-*` projections, affected surface, resolution, disposition, decision, and freshness |
| `04_WRITING_DESIGN_PACK.md` | compact semantic/analyzer/fallback mode pointers, source authority, blockers, and prohibitions |
| hidden dossier | detailed `TPL-*` provenance, located `TOBS-*`, semantic `TRULE-*` definitions, and synchronized application snapshots |

Do not create one public row for every metric. Preserve the hidden pointers and summarize only decisions that change the requested writing design.

## Writer-ready consequences

A template-linked writing scope may be writer-ready when its declared semantic/official/fallback inputs are current, hidden/public projections agree, every triggered gate is resolved, and each relevant design surface has a rule or grounded `not_applicable` outcome. The analyzer is never a default or readiness prerequisite: semantic-only, generic-fallback, and grounded template-not-applicable scopes can be ready without analyzer artifacts. Other scopes remain unaffected by a linked template failure.

Writer-ready here means only that downstream prose/visual planning can follow the declared structural constraints without inventing a convention. It does not mean the corpus is representative, the prose matches a venue, the research is valid, or the manuscript is submission-ready.
<!-- BEHAVIOR_CAPTURE_VENUE_TEMPLATE_END -->
The following projection is the entire model-visible scenario payload. Policy requirements and prohibited-answer oracle fields are intentionally absent.
<!-- MODEL_VISIBLE_SCENARIOS_START -->
{
  "scenarios": [
    {
      "context": {
        "design_need": "function, reader-state, payload boundary, qualification and output promise for every planned paragraph",
        "repository_evidence": "M-EXP-01, C-RES-01, LIM-01 and FIG-01 are locally traceable",
        "scope_ids": [
          "SCOPE-RESULTS"
        ]
      },
      "id": "B01",
      "situation": "evidence-rich repository input needs detailed paragraph/function design"
    },
    {
      "context": {
        "importance_basis": "counterevidence and high misreading cost",
        "paragraph_id": "P-DISC-03",
        "payload_ids": [
          "M-ROBUST-03",
          "C-BOUND-02"
        ],
        "scope_ids": [
          "SCOPE-DISCUSSION"
        ]
      },
      "id": "B02",
      "situation": "an important paragraph needs controlled sentence frames without manuscript prose"
    },
    {
      "context": {
        "adaptation": "retain rhetorical function but shorten the context span",
        "consequence": "Choosing the shorter pattern changes only local paragraph ordering",
        "grounding": "TPL-EXEMPLAR-01#Introduction paragraphs 2-4",
        "scope_ids": [
          "SCOPE-INTRO"
        ],
        "template_rule_id": "TRULE-INTRO-ORDER"
      },
      "id": "B03",
      "situation": "a grounded template adaptation affects only local paragraph ordering"
    },
    {
      "context": {
        "consequence": "changes the named scope and cannot be resolved as a routine reversible adaptation",
        "decision": "Whether C-SAFETY-02 remains a bounded association or becomes a causal claim",
        "scope_ids": [
          "SCOPE-CLAIM"
        ]
      },
      "id": "B04",
      "situation": "the owner proposes causal wording beyond the recorded evidence ceiling"
    },
    {
      "context": {
        "consequence": "changes the named scope and cannot be resolved as a routine reversible adaptation",
        "decision": "Whether mechanism or security-state evidence leads the contribution sequence",
        "scope_ids": [
          "SCOPE-PAPER"
        ]
      },
      "id": "B05",
      "situation": "two supported contribution orders imply different paper-level arguments"
    },
    {
      "context": {
        "consequence": "changes the named scope and cannot be resolved as a routine reversible adaptation",
        "decision": "Whether the adverse finding is framed before or after the aggregate benefit",
        "scope_ids": [
          "SCOPE-DISCUSSION"
        ]
      },
      "id": "B06",
      "situation": "a local paragraph choice materially changes reader interpretation"
    },
    {
      "context": {
        "consequence": "changes the named scope and cannot be resolved as a routine reversible adaptation",
        "decision": "Whether to retain the deliberate two-paragraph divergence from TRULE-INTRO-ORDER",
        "scope_ids": [
          "SCOPE-INTRO"
        ]
      },
      "id": "B07",
      "situation": "the proposed organization departs from a grounded template pattern"
    },
    {
      "context": {
        "access_state": "full_text",
        "claim_id": "C-NOVELTY-01",
        "discovered_source": "https://example.org/target-paper",
        "owner_request": "Use this publication as a writing exemplar and as support for C-NOVELTY-01",
        "role": "target_topic exemplar",
        "scope_ids": [
          "SCOPE-TEMPLATE-CLAIM"
        ]
      },
      "id": "B08",
      "situation": "the owner asks an externally discovered template source to support both writing design and a scientific claim"
    },
    {
      "context": {
        "dossier": "fresh semantic-dossier.json with traceable full-text locators",
        "projection": "TPL-SEM-01 and TRULE-SEM-01 agree across hidden and public records",
        "quantitative_question": null,
        "scope_ids": [
          "SCOPE-INTRO-SEMANTIC"
        ],
        "template_mode": "semantic_primary"
      },
      "id": "B09",
      "situation": "a fresh model-semantic dossier exists and no quantitative design question is declared"
    },
    {
      "context": {
        "analysis_mode": "distributional",
        "conclusion_ceiling": "descriptive writing-design distribution; no semantic, causal, venue-fit, or acceptance conclusion",
        "denominator": "15 eligible;13 valid;2 missing supported object locator",
        "design_question": "Where do comparable papers first place the primary result figure?",
        "metric_ids": [
          "object.figure_position_norm"
        ],
        "missingness": "2 missing supported object locator",
        "partition": "target_topic versus control",
        "scope_ids": [
          "SCOPE-RESULTS-QUANT"
        ],
        "semantic_dossier_state": "fresh"
      },
      "id": "B10",
      "situation": "a declared quantitative template-design question may invoke the optional analyzer"
    },
    {
      "context": {
        "affected_scope": "SCOPE-RESULT-A",
        "changed_record": "M-RESULT-A",
        "direct_links": [
          "P-RESULT-A2",
          "FRM-RESULT-A2-01",
          "VIS-RESULT-A",
          "TRULE-RESULT-A"
        ],
        "scope_ids": [
          "SCOPE-RESULT-A",
          "SCOPE-RESULT-B"
        ],
        "unaffected_scope": "SCOPE-RESULT-B",
        "unrelated_state": "SCOPE-RESULT-B is already writer-ready and has no declared link"
      },
      "id": "B11",
      "situation": "one evidence record changes while another ready scope has no declared link"
    },
    {
      "context": {
        "legacy_state": "section-level writer-ready",
        "schema_marker": "0.2",
        "scope_ids": [
          "SCOPE-LEGACY"
        ]
      },
      "id": "B12",
      "situation": "a schema-0.2 section-only writer-ready workspace is inspected"
    },
    {
      "context": {
        "schema_marker": "0.3",
        "scope_ids": [
          "SCOPE-FULL-03"
        ],
        "surface_states": {
          "controlled_frame": "satisfied",
          "cross_surface_traceability": "satisfied",
          "language_contract": "satisfied",
          "paragraph_function": "satisfied",
          "soft_budget": "satisfied",
          "template_rule_provenance": "satisfied",
          "visual_caption": "satisfied"
        },
        "template_mode": "semantic_primary"
      },
      "id": "B13",
      "situation": "all applicable schema-0.3 detailed surfaces are complete and current"
    },
    {
      "context": {
        "promotion_state": "scientific use is separately evaluated under 02",
        "publication": "doi:10.0000/example.14",
        "scientific_record": "M-PUB-14",
        "scope_ids": [
          "SCOPE-DUAL-ROLE"
        ],
        "template_record": "TPL-PUB-14"
      },
      "id": "B14",
      "situation": "one publication has both template-exemplar and scientific-source roles"
    },
    {
      "context": {
        "access_state": "metadata_only",
        "available_content": "title, authors, venue and URL only",
        "scope_ids": [
          "SCOPE-EXTERNAL-META"
        ],
        "source": "https://example.org/inaccessible-paper"
      },
      "id": "B15",
      "situation": "external material is metadata-only or inaccessible"
    }
  ]
}
<!-- MODEL_VISIBLE_SCENARIOS_END -->
