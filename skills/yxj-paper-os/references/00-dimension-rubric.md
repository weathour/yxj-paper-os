# D00-D19 Dimension Rubric — Schema 0.3 Detailed Prewriting Contract

This rubric is the public vocabulary and structural sufficiency contract for a
six-file yxj-paper-os workspace. It does not score scholarly quality, semantic
adequacy, venue fit, novelty, prose, or acceptance likelihood.

## Schema and Public Status Vocabulary

- Workspace schema: 0.3.
- Public files: exactly the six shipped Markdown templates.
- Dimension status tokens: filled&#124;not_applicable&#124;absent&#124;deferred&#124;rejected.
- Scope readiness tokens: writer-ready&#124;partial&#124;blocked&#124;deferred.
- writer-ready means detailed scoped prewriting design is structurally complete;
  it does not mean manuscript, submission, publication, or semantic readiness.
- Index columns and D00-D19 identities remain unchanged.

## Canonical Identity Grammar

| Record | Grammar | Authority |
|---|---|---|
| Dimension | ^D(?:0[0-9]&#124;1[0-9])$ | Existing D00-D19 vocabulary |
| Scope | ^SCOPE-[a-z0-9]+(?:-[a-z0-9]+)*$ | Writing-scope identity |
| Requirement | ^REQ-[a-z0-9]+(?:-[a-z0-9]+)*$ | Conditional requirement |
| Decision or gate | ^DEC-[a-z0-9]+(?:-[a-z0-9]+)*$ | Ordinary decisions and the four owner-gate categories |
| Scientific material/source/evidence | ^M-[a-z0-9]+(?:-[a-z0-9]+)*$ | Reuse Material Records; EVID-* is forbidden |
| Scientific claim | ^C-[a-z0-9]+(?:-[a-z0-9]+)*$ | Reuse Claim Records; CLM-* is forbidden |
| Detailed planning/template record | ^(?:TSD&#124;TPL&#124;TOBS&#124;TRULE&#124;SEC&#124;PAR&#124;FRM&#124;LANG&#124;VIS&#124;EDGE&#124;BUD)-[a-z0-9]+(?:-[a-z0-9]+)*$ | Globally unique within one workspace/dossier |

## Cardinality and Ownership

- A writer-ready SCOPE-* owns at least one SEC-*.
- Each SEC-* belongs to exactly one scope and owns at least one ordered PAR-*.
- Each PAR-* belongs to exactly one section/scope and has exactly one payload and
  boundary row.
- A paragraph has zero or one important-paragraph row. A selected important
  paragraph owns at least one ordered FRM-*.
- Each FRM-* belongs to exactly one paragraph.
- LANG-*, VIS-*, EDGE-*, TRULE-*, and BUD-* cardinality follows the seven-surface
  handling for the scope.
- 04 owns exactly one coverage row per surface per scope, one Template Analysis
  Handling row per scope, and one Scoped Handoff row per scope. It never owns
  authoritative paragraph, frame, language, visual, edge, rule, or budget rows.

The hidden semantic dossier owns detailed `TPL-*` provenance/access/fingerprint and
located `TOBS-*` observations. For semantic rules it owns definition fields; 03 owns
applied scope/surface/resolution/disposition/decision fields, while the hidden
`application_snapshot` is only a synchronized shadow. A hidden/public disagreement is
`TEMPLATE_PROJECTION_MISMATCH` for linked scopes, never last-write-wins.

The four grounding rows are defined once in
`scripts/template_design_contract.py`. Official, semantic, quantitative, and generic
rules cannot exchange pointer kinds, hard-constraint authority, or freshness forms;
an incompatible combination is `TEMPLATE_RULE_INCOMPATIBLE`.

## Cell, Absence, Pointer, and Relation Grammar

- Typed ID lists use the ASCII semicolon ; only. none is the only empty-list token,
  and none cannot be combined with an ID.
- Literal vertical bars inside a cell use &#124;; intended in-cell line breaks use
  <br>; every table row remains one physical line.
- Blank, TODO, TBD, UNKNOWN, and REPLACE_ME are invalid in a writer-ready scope.
- not_applicable requires a substantive adjacent rationale and cannot contradict
  scoped records.
- Public heading pointer example: 03_WRITING_STRUCTURE.md#Controlled Sentence Frames.
- Public record pointers use one declared ID.
- Semantic pointer example:
  .yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-example.
- Quantitative pointer example:
  .yxj-paper-os/template-analysis/design-profile.json#entries.example.
- Generic fallback pointer example:
  lens:argument-language-visual#sufficiency-predicates.
- Pointer-list columns use the same semicolon list grammar.
- Direct edge relations: fulfills;qualifies;limits;introduces;calls_out;visualizes;depends_on;contrasts_with;hands_off_to.
- EDGE-* stores one declared direct relation only. There is no traversal,
  transitive closure, scheduler, watcher, or runtime graph.

## Grammar Examples

| Surface | Positive | Negative | Rule |
|---|---|---|---|
| Detailed ID | PAR-method-1 | PAR_Method | Lowercase hyphenated suffix |
| Public pointer | 03_WRITING_STRUCTURE.md#Controlled Sentence Frames | notes.md#Frames | One of the six public files and a real heading |
| Semantic pointer | .yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-example | semantic-dossier.json#0 | Typed hidden path and stable record ID |
| Quantitative pointer | .yxj-paper-os/template-analysis/design-profile.json#entries.example | report.html#entry | Existing fixed JSON output and artifact path |
| Generic fallback pointer | lens:argument-language-visual#sufficiency-predicates | lens:unknown#invented | Canonical lens ID and real H2/H3 slug |
| Typed list | M-example;C-example | M-example,C-example | ASCII semicolon separator only |
| Empty list | none | none;M-example | none is exclusive |
| Literal cell separator | A&#124;B | raw vertical-bar character | Encode the character as &#124; |
| In-cell line break | first<br>second | physical multi-line row | Use <br> |
| Direct edge | visualizes | schedules | Use the frozen direct-edge enum |

## Canonical Detailed Surfaces

| Surface key | Authority | Ready-scope requirement |
|---|---|---|
| section_paragraph_map | 03 Section Map, Paragraph Map, and Payload Map | satisfied with complete ownership and payload rows |
| surface_language_contract | 03 Surface Language Contract | satisfied or grounded not_applicable |
| visual_caption_blueprint | 03 Visual Blueprint | satisfied or grounded not_applicable |
| cross_surface_traceability | 03 Cross-Surface Traceability | satisfied or grounded not_applicable |
| template_rule_provenance | 03 Template Rule Projection | satisfied or grounded not_applicable |
| soft_budgets | 03 Grounded Soft Budgets | satisfied or grounded not_applicable |
| important_paragraph_frames | 03 Important Paragraph Register and Controlled Sentence Frames | satisfied for every selected important paragraph |

## Dimension Ladder

### D00 — Workspace metadata

Sufficiency: schema 0.3, six-file identity, metadata, and the unchanged dimension
index are explicit.

### D01 — Owner decisions

Sufficiency: only scientific_commitment, argument_spine,
material_local_tradeoff, and deliberate_divergence are mandatory owner-gate
categories. Routine grounded reversible design decisions use not_applicable.

### D02 — Stale and dependency state

Sufficiency: changed records name only affected D IDs/scopes/records. Schema-0.2
readiness is migration-blocked until non-destructive schema-0.3 recompilation.

### D03 — Project brief

Sufficiency: problem, object, objective, assumptions, and prohibitions are grounded
or explicitly absent/deferred.

### D04 — Target route profile

Sufficiency: route, paper type, audience, official presentation constraints,
eligible template roles, and forbidden routes are distinguished.

### D05 — Material inventory

Sufficiency: scientific M-* records and design-only TPL-* records remain separate,
locatable, and explicitly typed.

### D06 — Evidence inventory

Sufficiency: scientific support uses eligible M-* evidence only. Template sources,
rules, visuals, and planned artifacts cannot raise support.

### D07 — Source and citation bank

Sufficiency: scientific source role and template-design role are separate even for
the same publication; promotion is never inferred.

### D08 — Research dossier

Sufficiency: context, conflicts, counterevidence, and gap hypotheses remain bounded.
A template semantic dossier is design-only hidden state, not scientific evidence.

### D09 — Exemplar and language profile

Sufficiency: template handling is explicitly semantic, quantitative, fallback, or
not_applicable; the deterministic analyzer is optional.

### D10 — Contribution options

Sufficiency: contribution choices, alternatives, dependencies, and triggered owner
gates are explicit.

### D11 — Claim-evidence map

Sufficiency: claim, evidence IDs, warrant, conditions, uncertainty, support,
resolution, and wording boundaries resolve without template support inflation.

### D12 — Wording boundary

Sufficiency: allowed/forbidden wording and verb strength follow D11 and the surface
language contract without generating manuscript-ready prose.

### D13 — Limitations and risks

Sufficiency: limitations, counterevidence, stale dependencies, and consequences are
placed in the relevant paragraph/frame/visual handoff.

### D14 — Reader spine

Sufficiency: section and paragraph reader-state transitions, jobs, sequence, and
adjacency are explicit.

### D15 — Manuscript outline

Sufficiency: every ready section has a scope, job, input IDs, output promise,
evidence/visual obligations, and at least one paragraph.

### D16 — Object granularity

Sufficiency: section, paragraph, payload, frame, visual, and source ownership is
stable enough to prevent scope drift.

### D17 — Surface control

Sufficiency: every paragraph has a function and payload boundary; selected important
paragraphs have controlled frames; applicable language contracts resolve.

### D18 — Visual plan

Sufficiency: applicable visual, panel, encoding, caption/legend, body callout,
accessibility, evidence, and handoff responsibilities resolve.

### D19 — Scoped writing design pack

Sufficiency: 04 is a pointer-only compiled manifest with seven-surface coverage,
conditional template handling, blockers/prohibitions, and one handoff row per scope.
Section-only completion is insufficient.
