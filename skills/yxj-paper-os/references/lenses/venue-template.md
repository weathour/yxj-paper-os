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
