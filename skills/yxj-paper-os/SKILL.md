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
