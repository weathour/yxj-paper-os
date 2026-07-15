# yxj-paper-os

`yxj-paper-os` is a schema-0.3 prewriting compiler for controlled academic writing.
It combines repository evidence, model-semantic reading of eligible template
literature, conditional academic lenses, and bounded owner decisions into a detailed
writing-design handoff. It stops before manuscript prose and never executes a
downstream writing, review, submission, or publication workflow.

## Product contract

The public workspace is exactly these six Markdown files:

1. `00_DIMENSION_INDEX.md`
2. `00_PROJECT_ROUTE.md`
3. `01_MATERIALS_INVENTORY.md`
4. `02_CLAIM_EVIDENCE_BOUNDARY.md`
5. `03_WRITING_STRUCTURE.md`
6. `04_WRITING_DESIGN_PACK.md`

D00-D19, the index columns, and the public status tokens remain stable. `00` is the
sole scope-readiness authority; `02` is the sole scientific claim/evidence/wording
ceiling; `03` owns the detailed design; `04` contains only counts, pointers, blockers,
prohibitions, and the handoff. No seventh public file is created.

A schema-0.3 `writer-ready` scope has functional design for every planned paragraph,
controlled placeholder frames for adaptively important paragraphs, and complete or
grounded-not-applicable handling of the seven surfaces:

- section/paragraph map;
- important-paragraph frames;
- surface language contract;
- visual/caption blueprint;
- cross-surface traceability;
- template-rule provenance; and
- grounded soft budgets.

This is declared structural readiness for a downstream writer, not manuscript,
submission, publication, scholarly, or semantic readiness.

## Evidence, template, and owner roles

- **Repository evidence** determines the scientific referent, available material,
  claims, uncertainty, limitations, and forbidden overclaim.
- **Template literature** determines grounded writing and presentation design. The
  primary path is model-semantic deep reading of full text or traceable derivatives,
  with locators, access state, fingerprints, freshness, and limitations in
  `.yxj-paper-os/template-analysis/semantic-dossier.json`.
- **Owner control** is reserved for four consequential gates:
  `scientific_commitment`, `argument_spine`, `material_local_tradeoff`, and
  `deliberate_divergence`. Routine grounded reversible design is agent-resolved
  without an unnecessary question.

Template records are always `design_only`. A publication used both as an exemplar and
as a scientific source receives separate `TPL-*` and `M-*` records. Metadata-only,
snippet-only, inaccessible, stale, or untraceable material is never represented as
full semantic reading.

## Template handling modes

Each scope declares exactly one handling mode:

- `semantic_primary`
- `semantic_plus_quantitative`
- `quantitative_only`
- `generic_fallback`
- `not_applicable`

Semantic-primary design can be writer-ready with no analyzer output. Generic fallback
or grounded `not_applicable` can also be valid when the scope does not need template
reading.

### Optional deterministic analyzer

The analyzer is non-default and answers only a declared measurable design question.
A `template-corpus/1.0` manifest declares registry-backed metric IDs, supported local
inputs, stable document IDs, partitions, and a requested maximum analysis mode.
Effective conclusions may only weaken after missingness, capability, uncertainty, and
comparability checks. Each paper remains the independent unit; missingness is not
zero; partitions are not silently pooled; PDF bytes are never pseudo-parsed.

```bash
python3 skills/yxj-paper-os/scripts/analyze_template_corpus.py \
  --manifest <workspace>/template-corpus.json
```

Fixed outputs stay below `.yxj-paper-os/template-analysis/`. They are design evidence
only and cannot increase D06/D11 support, prove novelty, venue fit, quality, or
acceptance likelihood.

## Schema-0.2 recompilation

Schema 0.2 is a legacy input, not current detailed readiness. Validation returns one
bounded `SCHEMA_LEGACY_02` diagnostic. Recompilation is agent-led and non-destructive:
preserve valid route/material/claim/evidence records, work on a copy or controlled
branch, populate schema-0.3 detailed surfaces from current evidence, and restore
`writer-ready` only after current validation. There is no automatic migration,
placeholder filling, or source-file rewrite by validators/dashboard.

## Validation boundary

```bash
python3 skills/yxj-paper-os/scripts/verify_dimension_rubric.py
python3 skills/yxj-paper-os/scripts/verify_semantic_dossier.py \
  <workspace>/.yxj-paper-os/template-analysis/semantic-dossier.json \
  --workspace <workspace>
python3 skills/yxj-paper-os/scripts/verify_design_pack.py <workspace>
python3 skills/yxj-paper-os/scripts/verify_behavior_scenarios.py
python3 skills/yxj-paper-os/scripts/generate_dashboard.py <workspace>
python3 -m unittest discover -s skills/yxj-paper-os/scripts -p 'test_*.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Validators and the dashboard check declared structure, types, identities, pointers,
provenance, freshness, authority separation, and readiness consequences. They do not
judge whether the agent selected every important paragraph, or prove academic truth,
semantic adequacy, novelty, statistical correctness, prose/visual quality, venue fit,
or acceptance.

`references/external/` contains pinned references only; they are not runtime
dependencies and are never executed automatically.
