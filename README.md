# yxj-paper-os

`yxj-paper-os` is a lightweight Codex plugin for preparing traffic, computer-science, and AI paper projects before manuscript drafting. It uses a model-led cognitive kernel, optional academic lenses, sparse traceable records, and scoped writing handoffs. It never drafts the manuscript or executes downstream skills.

## Public contract

- one public skill: `skills/yxj-paper-os/SKILL.md`;
- exactly six workspace Markdown files;
- D00-D19 remains the stable diagnostic vocabulary;
- `00_DIMENSION_INDEX.md` keeps its public columns/status values and adds schema `0.2` plus a sparse Writing Scopes registry;
- optional lens, decision, material, claim, dependency, structure, and handoff tables appear only when they carry real information;
- dashboard output is only `<workspace>/.yxj-paper-os/dashboard.html` and never rewrites source Markdown.

## Cognitive model

The skill synthesizes the whole situation, inspects and derives before asking, activates 0..N conditional lenses, records epistemic origin/support/resolution separately, rechecks declared dependents, and judges readiness per requested writing scope. It has no fixed scan order, global template gate, universal critical set, mandatory subagent stages, runtime graph, or semantic scorer.

Lens theory lives in `skills/yxj-paper-os/references/lenses/`; the canonical registry separates module files from activatable IDs. A `venue-template` lens affects only explicitly linked route/style surfaces.

## Validation

```bash
python3 skills/yxj-paper-os/scripts/verify_dimension_rubric.py
python3 skills/yxj-paper-os/scripts/verify_design_pack.py <paper_project>
python3 skills/yxj-paper-os/scripts/verify_behavior_scenarios.py
python3 skills/yxj-paper-os/scripts/generate_dashboard.py <paper_project>
```

Validators check structure, typed references, declared provenance/readiness boundaries, policy-record conformance, and safe dashboard behavior. They do not prove academic truth, novelty, venue fit, prose quality, or research/manuscript/submission readiness.

`references/external/` contains pinned reference repositories only; they are not runtime dependencies and are never executed automatically.
