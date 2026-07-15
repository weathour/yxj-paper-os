# yxj-paper-os Handoff

## Current architecture

The current product is one public skill and exactly six public schema-0.3 Markdown
files. It is a model-led prewriting compiler, not a questionnaire, fixed pipeline,
runtime graph, semantic scorer, or manuscript writer. D00-D19 remain diagnostic
vocabulary.

The compiler joins three authorities:

1. repository material fixes scientific meaning and claim ceilings;
2. model-semantic template reading fixes grounded writing/presentation design; and
3. the owner resolves only `scientific_commitment`, `argument_spine`,
   `material_local_tradeoff`, and `deliberate_divergence`.

`00_DIMENSION_INDEX.md` alone owns scope readiness. `02` alone owns scientific claim
support and wording ceilings. `03` owns paragraph, controlled-frame, language, visual,
traceability, template-rule, and soft-budget design. `04` is pointer/count/blocker only.
Template sources and rules are `design_only`; the deterministic analyzer is optional.

## Owned resources

- `skills/yxj-paper-os/SKILL.md` — adaptive reasoning and safety contract;
- five playbooks under `references/` and seven conditional lenses under
  `references/lenses/`;
- exactly six public templates under `assets/templates/`;
- semantic-dossier schema plus optional analyzer schemas/registries/fixtures under
  `assets/`;
- read-only validators, analyzer, dashboard, behavior capture, and tests under
  `scripts/`;
- oracle-free current behavior fixture under `evals/recorded/fixture-current/`.

## Compatibility and migration

Workspace schema is `0.3`. Public filenames, D00-D19 IDs, index columns, dimension
statuses, and the six-file boundary remain compatible. A 0.2 workspace receives one
`SCHEMA_LEGACY_02` diagnostic; prior section-level `writer-ready` is not current.
Recompile non-destructively on a copy/branch. No validator, dashboard, or migrator
silently changes source Markdown or invents missing detailed records.

## Verification

Run targeted suites first, then:

```bash
python3 skills/yxj-paper-os/scripts/verify_dimension_rubric.py
python3 skills/yxj-paper-os/scripts/verify_behavior_scenarios.py
python3 -m unittest discover -s skills/yxj-paper-os/scripts -p 'test_*.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q skills/yxj-paper-os/scripts tests
git diff --check -- .
```

For a workspace, also run `verify_semantic_dossier.py` when semantic template design
is active, `verify_design_pack.py`, and `generate_dashboard.py`. A current behavior
capture is accepted only when its full skill/reference prompt is byte-identical to the
canonical oracle-free prompt; its exact manifest labels and all required hashes match
current inputs; and every response passes the closed structural schema plus declared
scenario-oracle fields for action, scope, canonical identity, structured update values,
readiness consequences, exact cardinality, and question target. The raw response must
be one sole finite-number JSON document with no duplicate object keys. A scenario
authority is valid only when its deterministic closed-rule witness passes the same
runtime schema, negative-rule, cross-field, scope-identity, and global-ID checks.
Readiness scopes equal target scopes; writer-ready public-pointer anchors equal their
scope IDs. Rule-bound tokens, identifiers, locators, pointers, and grounding are exact;
`reason`, controlled `design_payload`, and live provenance labels must contain a
Unicode-visible code point, while prose fields remain semantically free text. The
prose-leak heuristic is warning/manual-review support, not semantic proof.
The offline fixture is reproducible policy evidence, not a claim that a model run
succeeded.

## Remaining non-goals

No manuscript/title/abstract/caption/table prose; no invented science, sources,
results, or visuals; no scientific support from template records; no PDF/OCR
pseudo-reading; no downstream skill execution; no automatic migration; no quality,
venue, acceptance, publication, or semantic-completeness score; no submission or
release action.
