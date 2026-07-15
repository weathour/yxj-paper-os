# 04 Writing Design Pack

> Pointer-only schema-0.3 compiled manifest. 00 owns scope readiness; 01 owns
> materials; 02 owns scientific claim/support/wording ceilings; 03 owns detailed
> section, paragraph, frame, language, visual, edge, rule, and budget records.

## Authority Pointers

| Authority | Required pointer | Compiler note |
|---|---|---|
| Scope and readiness | 00_DIMENSION_INDEX.md#Writing Scopes | Select the unique SCOPE-* row; do not copy the status here |
| Route and gates | 00_PROJECT_ROUTE.md#Decision Records | Carry only compact resolved pointers and blockers |
| Scientific materials | 01_MATERIALS_INVENTORY.md#Material Records | M-* scientific material/source/evidence authority |
| Template design sources | 01_MATERIALS_INVENTORY.md#Template Design Sources | Separate TPL-* design-only source/provenance authority |
| Scientific claim ceiling | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | Template rules cannot raise support or wording |
| Detailed design | 03_WRITING_STRUCTURE.md#Section Map | Point to authoritative A-K records; do not duplicate them |

## Detailed Surface Coverage

| Surface | Scope ID | Handling (`satisfied&#124;not_applicable`) | Record count | Authoritative pointer | Rationale/blocker |
|---|---|---|---|---|---|
| section_paragraph_map | SCOPE-01 | TODO | TODO | TODO | TODO |
| surface_language_contract | SCOPE-01 | TODO | TODO | TODO | TODO |
| visual_caption_blueprint | SCOPE-01 | TODO | TODO | TODO | TODO |
| cross_surface_traceability | SCOPE-01 | TODO | TODO | TODO | TODO |
| template_rule_provenance | SCOPE-01 | TODO | TODO | TODO | TODO |
| soft_budgets | SCOPE-01 | TODO | TODO | TODO | TODO |
| important_paragraph_frames | SCOPE-01 | TODO | TODO | TODO | TODO |

Each unique scope in 00 has exactly one row for each of the seven surfaces. satisfied
requires a resolvable 03 pointer and applicable records. not_applicable requires a
substantive rationale, Authoritative pointer none, and no contradictory scoped record.
04 stores declared counts and pointers only.

## Detailed Coverage Summary

| Scope ID | Section count | Paragraph count | Important paragraph count | Frame count | Language count | Visual count | Edge count | Rule count | Budget count |
|---|---|---|---|---|---|---|---|---|---|
| SCOPE-01 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

Counts must equal the authoritative 03 records; they are structural coverage, not a
semantic or writing-quality score.

## Owner Gate Resolution Summary

| Scope ID | Gate category | Decision ID | Resolution | Grounding / owner-answer pointer | Active blocker IDs |
|---|---|---|---|---|---|
| SCOPE-01 | TODO | TODO | TODO | TODO | none |

Only scientific_commitment, argument_spine, material_local_tradeoff, and
deliberate_divergence are owner gates. Routine grounded decisions do not create
ceremonial questions.

## Template Analysis Mode Contract

| Mode | Semantic dossier pointer | Quantitative analysis pointer(s) | Generic fallback pointer(s) |
|---|---|---|---|
| semantic_primary | required | none | none, unless coupled to a same-scope generic-fallback TRULE-* for a named uncovered surface |
| semantic_plus_quantitative | required | required | none, unless coupled to the same named uncovered-surface rule |
| quantitative_only | none | required | none |
| generic_fallback | none | none | required |
| not_applicable | none | none | none |

semantic_plus_quantitative uses separately typed semantic and quantitative rules; it
never creates a mixed-grounding TRULE-* row. In semantic modes, an optional generic
pointer requires a same-scope generic-fallback rule and a rationale naming the
uncovered surface.

## Template Analysis Handling

| Scope ID | Mode | Semantic dossier pointer | Quantitative analysis pointer(s) | Generic fallback pointer(s) | Firewall state | Rationale | Active blocker IDs |
|---|---|---|---|---|---|---|---|
| SCOPE-01 | TODO | none | none | none | design_only | TODO | none |

This table has exactly one row per unique scope in 00, including partial, blocked, and
deferred scopes. Mode controls the three pointer columns exactly. Firewall state is
always design_only. A grounded not_applicable row requires no dossier or analyzer.

## Template Source Firewall

Template literature, semantic observations, analyzer outputs, and generic fallback
rules are writing-design inputs only. They cannot create M-* evidence, increase C-*
support, prove novelty or source truth, or silently promote a TPL-* source.

## Unresolved and Downstream Prohibitions

| Scope ID | Unresolved/stale/deferred record IDs | Consequence | Downstream prohibition |
|---|---|---|---|
| SCOPE-01 | TODO | TODO | Do not draft beyond the pointed claim, payload, and language boundaries |

## Scoped Handoff

| Scope ID | 00 scope-row pointer | Detailed coverage pointer | Output pointer | Active blocker IDs | Downstream prohibitions | Handoff note |
|---|---|---|---|---|---|---|
| SCOPE-01 | 00_DIMENSION_INDEX.md#Writing Scopes | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | TODO | TODO | TODO | TODO |

This table has exactly one row per unique scope in 00. The 00 scope row is the only
readiness authority. For writer-ready, Output pointer equals the 00 row output and
Active blocker IDs is none. Non-ready scopes may use Output pointer none only with a
concrete handoff note. This table never copies or infers a status.
