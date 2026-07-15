# 03 Writing Structure

> Authoritative schema-0.3 detailed design surface. Fill functional records and
> constraints only; do not write manuscript-ready sentences, captions, titles,
> abstracts, or paragraphs.

## Section Map

| Section ID | Scope ID | Sequence | Job | Reader state in | Reader state out | Input IDs | Output promise | Evidence/visual obligations | Forbidden content |
|---|---|---|---|---|---|---|---|---|---|
| SEC-01 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

A writer-ready scope owns at least one section. Each section belongs to exactly one
scope, has a unique sequence, and owns at least one paragraph.

## Paragraph Map

| Paragraph ID | Scope ID | Section ID | Sequence | Function/job | Reader state in | Reader state out | Previous paragraph | Next paragraph |
|---|---|---|---|---|---|---|---|---|
| PAR-01 | TODO | TODO | TODO | TODO | TODO | TODO | none | none |

Each paragraph belongs to exactly one section and scope. Previous/next pointers
express exact same-section adjacency; cross-scope handoff uses an EDGE-* relation.

## Paragraph Payload and Boundary Map

| Paragraph ID | Claim IDs | Material/source/evidence IDs | Claim/citation boundary rationale | Citation function | Equation/algorithm/visual/table record IDs | Object relation/job | Required qualification/limitation | Output promise | Forbidden content/overclaim | Template rule IDs |
|---|---|---|---|---|---|---|---|---|---|---|
| PAR-01 | none | none | TODO | TODO | none | TODO | TODO | TODO | TODO | none |

Every planned paragraph has exactly one payload/boundary row. Scientific claims and
evidence use C-* and M-* only; template rules cannot raise the 02 claim ceiling.

## Important Paragraph Register

| Paragraph ID | Qualitative selection rationale | Consequence/risk/dependency | Frame IDs | Gate category | Decision ID | Gate resolution | Owner-answer/grounding pointer |
|---|---|---|---|---|---|---|---|
| PAR-01 | TODO | TODO | FRM-01 | not_applicable | none | TODO | none |

Important-paragraph selection is qualitative and adaptive. Consider commitment,
uncertainty, argument load, misreading risk, template sensitivity, formula/citation/
visual interfaces, and cross-surface dependency; do not add an importance score or
a universal paragraph list. A selected paragraph owns one or more ordered frames.

## Controlled Sentence Frames

| Frame ID | Paragraph ID | Order | Sentence function | Proposition/content target | Clause/relation order | Required payload IDs | Payload/boundary rationale | Language contract IDs | Local language constraint | Previous frame | Next frame | Forbidden realization |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FRM-01 | PAR-01 | TODO | TODO | TODO | [bounded context] -> [grounded payload slot] -> [qualification slot] | none | TODO | LANG-01 | TODO | none | none | No polished sentence or cosmetic-fill template |

Frames specify functional slots, proposition targets, clause relations, payload,
language, and forbidden realization. They stop before paste-ready prose.

## Surface Language Contract

| Contract ID | Scope ID | Surface | Terminology | Claim/verb strength | Hedge/modality | Tense/voice | Syntax/rhythm tendency | Forbidden patterns | Grounding IDs |
|---|---|---|---|---|---|---|---|---|---|
| LANG-01 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

## Visual Blueprint

| Visual ID | Scope ID | Paragraph IDs | Status | Evidence/data IDs | Story role | Panel/order/encoding | Caption/legend job | Body callout relation | Accessibility responsibility | Handoff/blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| VIS-01 | TODO | TODO | TODO | none | TODO | TODO | TODO | TODO | TODO | TODO |

Visual status is existing&#124;needed&#124;deferred&#124;absent. A planned or absent
visual is not evidence. Caption/legend cells store jobs and constraints, not text.

## Cross-Surface Traceability

| Edge ID | From record | Relation | To record | Closure surface | State/freshness | Consequence if stale |
|---|---|---|---|---|---|---|
| EDGE-01 | TODO | TODO | TODO | TODO | TODO | TODO |

Relation is fulfills&#124;qualifies&#124;limits&#124;introduces&#124;calls_out&#124;visualizes&#124;depends_on&#124;contrasts_with&#124;hands_off_to. This is a sparse direct-edge table, not a runtime graph.

## Template Rule Projection

| Rule ID | Grounding kind | Grounding pointer(s) | Rule kind | Affected scope IDs | Surface | Candidate transfer | Suggested disposition | Origin | Resolution | Disposition | Decision ID | Limitation | Freshness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRULE-01 | TODO | TODO | TODO | TODO | TODO | TODO | none | model-proposed | candidate | candidate | none | TODO | TODO |

Grounding kind is official_constraint&#124;semantic_dossier&#124;quantitative_analysis&#124;generic_fallback. Each rule uses exactly one kind and its matching pointer, rule-kind, disposition, gate, and freshness contract. Analyzer candidate_action maps only to Suggested disposition; actual Disposition remains candidate until an explicit grounded design decision. Only a triggered four-category choice requires DEC-*.

## Grounded Soft Budgets

| Budget ID | Scope ID | Surface | Property | Basis kind | Grounding pointer | Soft band or ordering | Disposition | Adaptation rationale | Hard-constraint disclaimer |
|---|---|---|---|---|---|---|---|---|---|
| BUD-01 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | Descriptive planning aid; not a quality threshold |

Basis kind is official_constraint&#124;semantic_dossier&#124;quantitative_analysis&#124;repository_grounding&#124;generic_fallback. A soft band never becomes a quality or venue-fit score.

## Scoped Writing Plan

| Scope ID | Reader / section job | Input record IDs | Output responsibility | Drafting boundary | Output pointer |
|---|---|---|---|---|---|
| SCOPE-01 | TODO | TODO | TODO | TODO | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |
