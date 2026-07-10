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
