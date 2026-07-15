# 03 Writing Structure

> Authoritative detailed design records. Rows are functional constraints, not manuscript-ready text.

## Section Map

| Section ID | Scope ID | Sequence | Job | Reader state in | Reader state out | Input IDs | Output promise | Evidence/visual obligations | Forbidden content |
|---|---|---|---|---|---|---|---|---|---|
| SEC-method | SCOPE-demo | 1 | Establish the bounded method role then connect one qualified comparison | Reader knows only the planning scope | Reader can distinguish method input from supported comparison | M-method;M-evidence;C-demo;VIS-figure | Two ordered paragraph responsibilities with explicit boundaries | Ground comparison in M-evidence and link VIS-figure | No invented mechanism result or venue claim |

## Paragraph Map

| Paragraph ID | Scope ID | Section ID | Sequence | Function/job | Reader state in | Reader state out | Previous paragraph | Next paragraph |
|---|---|---|---|---|---|---|---|---|
| PAR-context | SCOPE-demo | SEC-method | 1 | Define the bounded method-design context and hand off to the comparison | Reader lacks the method role | Reader knows the method role and expects a bounded comparison | none | PAR-claim |
| PAR-claim | SCOPE-demo | SEC-method | 2 | Connect the evidence-grounded comparison to the visual while preserving limits | Reader expects the comparison | Reader sees the supported comparison and its limitation | PAR-context | none |

## Paragraph Payload and Boundary Map

| Paragraph ID | Claim IDs | Material/source/evidence IDs | Claim/citation boundary rationale | Citation function | Equation/algorithm/visual/table record IDs | Object relation/job | Required qualification/limitation | Output promise | Forbidden content/overclaim | Template rule IDs |
|---|---|---|---|---|---|---|---|---|---|---|
| PAR-context | none | M-method | Non-claim orientation uses the artifact only and creates no scientific commitment | not_applicable: no external citation role | none | not_applicable: this orientation paragraph introduces no equation algorithm visual or table | State that the role is bounded to the supplied artifact | Hand off one defined method role to PAR-claim | No mechanism efficacy or novelty claim | none |
| PAR-claim | C-demo | M-evidence | The comparison may not exceed C-demo or M-evidence | evidence support for the bounded comparison | VIS-figure | Call out the visual only as a representation of M-evidence | Preserve the synthetic-evidence and non-generality limits | Close the comparison with its explicit ceiling | No superiority generality or acceptance claim | none |

## Important Paragraph Register

| Paragraph ID | Qualitative selection rationale | Consequence/risk/dependency | Frame IDs | Gate category | Decision ID | Gate resolution | Owner-answer/grounding pointer |
|---|---|---|---|---|---|---|---|
| PAR-claim | Claim and visual interfaces create the highest local overclaim risk | Misreading would exceed C-demo and M-evidence | FRM-claim-1;FRM-claim-2 | not_applicable | none | not_applicable: evidence ceiling and clause roles are already fixed | none |

## Controlled Sentence Frames

| Frame ID | Paragraph ID | Order | Sentence function | Proposition/content target | Clause/relation order | Required payload IDs | Payload/boundary rationale | Language contract IDs | Local language constraint | Previous frame | Next frame | Forbidden realization |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FRM-claim-1 | PAR-claim | 1 | Evidence-bound comparison setup | Bind C-demo to M-evidence without adding magnitude or causality | [bounded comparison context] -> [M-evidence observation slot] -> [C-demo ceiling] | M-evidence;C-demo | Payload anchors the only scientific proposition slot | LANG-main | Use qualified comparison verbs and no causal verb | none | FRM-claim-2 | No complete paste-ready academic sentence |
| FRM-claim-2 | PAR-claim | 2 | Visual callout and limitation closure | Connect VIS-figure as representation then state the non-generality boundary | [VIS-figure callout role] -> [representation relation] -> [limitation slot] | VIS-figure;M-evidence | Visual and evidence IDs keep the closure grounded | LANG-main | End with an explicit scope limitation rather than a rhetorical claim | FRM-claim-1 | none | No caption prose or polished conclusion sentence |

## Surface Language Contract

| Contract ID | Scope ID | Surface | Terminology | Claim/verb strength | Hedge/modality | Tense/voice | Syntax/rhythm tendency | Forbidden patterns | Grounding IDs |
|---|---|---|---|---|---|---|---|---|---|
| LANG-main | SCOPE-demo | PAR-context;PAR-claim | Reuse method role bounded comparison and evidence ceiling consistently | Descriptive for M-method and qualified comparative for C-demo | Use explicit may or bounded-by modality where inference is limited | Present tense active voice for design roles | Short orientation followed by evidence-limitation closure | No proves guarantees novel optimal or venue-fit wording | M-method;M-evidence;C-demo |

## Visual Blueprint

| Visual ID | Scope ID | Paragraph IDs | Status | Evidence/data IDs | Story role | Panel/order/encoding | Caption/legend job | Body callout relation | Accessibility responsibility | Handoff/blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| VIS-figure | SCOPE-demo | PAR-claim | existing | M-evidence | Represent the bounded comparison without adding support | One panel with direct labels and no decorative encoding | Identify variables evidence boundary and limitation; do not draft caption text | PAR-claim calls out VIS-figure after the comparison slot | Preserve readable labels and a non-color-only distinction | Ready for downstream realization under M-evidence |

## Cross-Surface Traceability

| Edge ID | From record | Relation | To record | Closure surface | State/freshness | Consequence if stale |
|---|---|---|---|---|---|---|
| EDGE-claim-visual | PAR-claim | visualizes | VIS-figure | Comparison-to-visual handoff | current | Block PAR-claim and VIS-figure until M-evidence linkage is rechecked |

## Template Rule Projection

| Rule ID | Grounding kind | Grounding pointer(s) | Rule kind | Affected scope IDs | Surface | Candidate transfer | Suggested disposition | Origin | Resolution | Disposition | Decision ID | Limitation | Freshness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Grounded Soft Budgets

| Budget ID | Scope ID | Surface | Property | Basis kind | Grounding pointer | Soft band or ordering | Disposition | Adaptation rationale | Hard-constraint disclaimer |
|---|---|---|---|---|---|---|---|---|---|

## Scoped Writing Plan

| Scope ID | Reader / section job | Input record IDs | Output responsibility | Drafting boundary | Output pointer |
|---|---|---|---|---|---|
| SCOPE-demo | SEC-method with two ordered paragraph jobs | M-method;M-evidence;C-demo;LANG-main;VIS-figure | Realize the declared jobs frames language and visual callout | Do not invent content or turn frames into paste-ready prose | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |
