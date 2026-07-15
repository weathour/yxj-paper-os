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
