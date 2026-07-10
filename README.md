# yxj-paper-os

`yxj-paper-os` is a lightweight Codex plugin for preparing traffic, computer-science, and AI paper projects before manuscript drafting. It combines a model-led cognitive kernel with reproducible target-journal/target-topic corpus statistics, optional academic lenses, sparse traceable records, and scoped writing handoffs. It never drafts the manuscript or executes downstream skills.

## Public contract

- one public skill: `skills/yxj-paper-os/SKILL.md`;
- exactly six workspace Markdown files;
- D00-D19 remains the stable diagnostic vocabulary;
- `00_DIMENSION_INDEX.md` keeps its public columns/status values and adds schema `0.2` plus a sparse Writing Scopes registry;
- optional lens, decision, material, claim, dependency, structure, and handoff tables appear only when they carry real information;
- generated internal artifacts are limited to `<workspace>/.yxj-paper-os/dashboard.html` and `<workspace>/.yxj-paper-os/template-analysis/`; neither path rewrites source Markdown or corpus inputs.

## Cognitive model

The skill synthesizes the whole situation, inspects and derives before asking, activates 0..N conditional lenses, records epistemic origin/support/resolution separately, rechecks declared dependents, and judges readiness per requested writing scope. It has no fixed scan order, global template gate, universal critical set, mandatory subagent stages, runtime graph, or semantic scorer.

Lens theory lives in `skills/yxj-paper-os/references/lenses/`; the canonical registry separates module files from activatable IDs. A `venue-template` lens affects only explicitly linked route/style surfaces. Template-derived distributions never support scientific claims or become mandatory venue rules.

## Template corpus statistics

The standard-library analyzer accepts a `template-corpus/1.0` manifest containing Markdown, semantic HTML, JATS XML, or TXT derivatives. Every manifest names the concrete `design_question` and the registry-backed `design_metric_ids` that operationalize it; optional `analysis_mode` defaults to `case_set` and records the requested maximum conclusion strength, not a guarantee that the measured corpus can support it. It measures document structure, section and paragraph distributions, explicit citation surfaces, figures, tables, equations, algorithms, captions, callouts, object order, and auditable lexical proxies. PDF bytes are rejected: supply publisher HTML/JATS or an owner-provided text derivative with provenance instead.

```json
{
  "schema": "template-corpus/1.0",
  "corpus_id": "target-journal-topic",
  "analysis_mode": "exploratory",
  "design_question": "How should section allocation and figure placement shape the target manuscript?",
  "design_metric_ids": [
    "structure.section_word_share",
    "structure.section_start_position_norm",
    "object.figure_position_norm",
    "sequence.object_type_order"
  ],
  "documents": [
    {
      "doc_id": "paper-001",
      "path": "corpus/paper-001.xml",
      "format": "jats",
      "partition": "primary_match",
      "venue": "Target Journal",
      "topic_tags": ["target topic"],
      "article_type": "research-article",
      "year": 2026,
      "language": "en"
    }
  ]
}
```

`analysis_mode` is requested; the effective conclusion can only stay at that
level or be weakened after inspecting valid observations, missingness,
uncertainty, and partition comparability for the declared `design_metric_ids`.
Ready but unrelated metrics never upgrade the answer. `sample_size_label` is descriptive
paper-count context, never a quality, representativeness, venue-fit, or
sufficiency gate. A document that needs an inclusion exception uses an
owner-grounded object rather than a free-text waiver:

```json
{
  "inclusion_exception": {
    "reason": "Retain this older article as the owner-confirmed historical comparator.",
    "origin": "owner-stated",
    "resolution": "confirmed",
    "decision_pointer": "00_PROJECT_ROUTE.md#Decision Records"
  }
}
```

The exception preserves its reason and decision pointer; it does not make the
document comparable or permit silent pooling.

```bash
python3 skills/yxj-paper-os/scripts/analyze_template_corpus.py \
  --manifest <workspace>/template-corpus.json
```

The analyzer writes deterministic JSON/JSONL plus an offline HTML report under `.yxj-paper-os/template-analysis/`. Aggregation treats each paper as the independent unit, preserves missingness separately from zero, and stratifies venue/topic partitions. Corpus observations become candidate soft bands only when the effective metric-level result supports them; otherwise they remain sequences, presence notes, or watch-only patterns. Only artifact-observed official guidance can become a hard constraint.

## Validation

```bash
python3 skills/yxj-paper-os/scripts/verify_dimension_rubric.py
python3 skills/yxj-paper-os/scripts/verify_design_pack.py <paper_project>
python3 skills/yxj-paper-os/scripts/verify_behavior_scenarios.py
python3 skills/yxj-paper-os/scripts/generate_dashboard.py <paper_project>
python3 -m unittest discover -s skills/yxj-paper-os/scripts -p 'test_*.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Validators check structure, typed references, declared provenance/readiness boundaries, policy-record conformance, deterministic extraction, and safe dashboard behavior. They do not prove academic truth, novelty, venue fit, prose quality, statistical correctness, acceptance probability, or research/manuscript/submission readiness.

`references/external/` contains pinned reference repositories only; they are not runtime dependencies and are never executed automatically.
