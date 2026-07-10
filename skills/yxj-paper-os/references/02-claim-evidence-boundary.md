# Playbook 02 — Claim Evidence Boundary

Use this playbook when `02_CLAIM_EVIDENCE_BOUNDARY.md` is missing, when claims lack evidence anchors, or when D10/D11/D12/D13 or claim-side D16/D17 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, question-depth, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is the central internal rubric/reference. The central rubric decides sufficiency and question-depth; this file is not a sixth task playbook and not a public workspace file. This playbook translates the current rubric gaps into compact question cards and write landings; it must not duplicate or override the central D00-D19 ladder.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D10 | `Contribution options` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options` |
| D11 | `Claim-evidence map` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map` |
| D12 | `Wording boundary` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording` |
| D13 | `Limitation and risk matrix` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks` |
| D16 | `Object granularity` | Secondary: `02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity`; primary pointer normally lives in `03_WRITING_STRUCTURE.md#Object Granularity` |
| D17 | `Surface control` | Secondary: claim wording in `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording`; primary pointer normally lives in `03_WRITING_STRUCTURE.md#Surface Control` |

After updating claim content, update the matching dimension rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Question-depth translator guide

Use the central rubric to judge whether the current Dxx answer is missing, minimum-only, standard-ready, deferred, or rejected. Use this table only to translate that gap into the next compact card; do not add public files, D IDs, index columns/statuses, manuscript prose, citations, source truth, results, evidence anchors, external skill execution, semantic scoring, or runtime orchestration.

| D ID(s) | Default card mode | Ask a depth follow-up when... | Reconcile or conflict-check when... | Write landing |
|---|---|---|---|---|
| D10 | `focused-question`; `candidate-confirmation` only from confirmed upstream material | a contribution framing tradeoff changes paper type, route expectations, evidence burden, or rejected alternatives | contribution conflicts with D03 brief, D04 route, D11 evidence, or D16 object granularity | `02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options`, then D10 row |
| D11 | `focused-question` for a blocking claim/anchor; `candidate-confirmation` for bounded claim options | support strength suggests a claim should be split, downgraded, deferred, or rejected | a claim exceeds D06 evidence, D12 wording, D13 limitations, or D18 visual evidence | `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map`, then D11 row |
| D12 | `focused-question` | a tempting stronger phrase, front-matter promise, causal wording, superiority claim, or certainty term must be forbidden | D17 surface language or D11 claim wording exceeds D06 support | `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` and `#Forbidden Wording`, then D12 row |
| D13 | `focused-question` | a hidden limitation or material risk would change contribution, route, reader expectation, or downstream wording | risk notes contradict D11 claims, D12 wording, D14 reader path, or D19 handoff notes | `02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks`, then D13 row |
| D16/D17 claim-side | `reconciliation` when paired with structure-side text; otherwise `focused-question` | object scope, term choice, tone, or allowed wording changes claim scope or overclaim control | claim-side object/surface notes conflict with primary D16/D17 in `03_WRITING_STRUCTURE.md` or with D10-D12 | `#Object Granularity`, `#Allowed Wording`, and `#Forbidden Wording`, then D16/D17 rows or handoff to structure |

## Adaptive cross-boundary reminder

The central rubric owns the full D07/D08/D09/D18/D19 rules. In this claim/evidence playbook, enforce the shared boundary before allowing any claim to become active:

- Sources, citation candidates, research dossier notes, exemplar/style guidance, design-pack summaries, and visual plans are not evidence anchors by themselves.
- A claim may be supported only when D06 identifies a locatable evidence anchor and D11 maps the active claim to that anchor with support strength and wording boundaries.
- D07/D08 can explain context, citation needs, conflicts, gaps, or handoff risks; they cannot prove novelty, source truth, or claim truth.
- D09 can constrain style and D17 surface control; it cannot raise claim strength.
- D18 can plan visuals; needed/deferred/absent visuals cannot support active claims.
- D19 can summarize the boundary as a structural handoff; it cannot convert unresolved sources, visuals, or dossier notes into readiness.

## Additional claim-boundary additions

Use these additions to prevent writing-surface planning from becoming unsupported manuscript content.

- **Front matter / hook boundary:** title, abstract, keyword, and graphical-hook constraints may summarize confirmed route, contribution, evidence strength, and forbidden wording, but this playbook does not draft front matter or hook copy.
- **Introduction / related-work boundaries:** gap, motivation, novelty-adjacent, and citation-function moves require owner-confirmed claims and supplied source/context notes. D07/D08 roles can guide rhetorical placement but cannot prove novelty or strengthen D11 support.
- **Method/reporting/repro boundaries:** separate method claims from implementation facts, reporting facts, availability statements, and reproducibility promises. A method claim needs D06/D11 support; a reporting fact needs locatable D05 material or explicit absence/defer handling.
- **Results / visual / caption / table boundaries:** result claims must bind to evidence anchors; captions, tables, panels, legends, and accessibility notes may hand off what to explain but cannot create evidence or stronger claims.
- **Forbidden overclaim patterns:** record front-matter hype, introduction gap overreach, method/repro claims without artifacts, result/caption causal language, benchmark superiority claims, and visual-certainty language as D12 forbidden wording when evidence does not support them.

## Optional Exemplar Analysis claim-design boundary

Use `Template Claim-Design Benchmark` only to compare a current `.yxj-paper-os/template-analysis/corpus-summary.json` / `design-profile.json` observation with claim **presentation**. The comparison may alter placement, emphasis, surface wording, or figure/table handoff, but it cannot strengthen claims, create D06 evidence anchors, change D11 support, verify source truth, or score semantic adequacy.

Template-corpus statistics and project-result statistics are different ontological domains. The former describe how supplied papers present text/figures/tables and belong to the `venue-template` lens; the latter describe this project's research results and remain governed by `evidence-results-statistics`, D06, and D11. Never substitute, pool, or cross-promote them. Source/similarity/partition rationale is a material/design record, not scientific claim support.

## Required fields

- Problem statement.
- Research object: method, system, model, dataset, benchmark, application, or analysis object.
- One-sentence core contribution.
- Contribution options: selected, rejected, or deferred options with reasons.
- Object granularity sufficient to avoid vague claims.
- Core claims.
- Evidence anchors for each claim.
- Support strength: strong, moderate, weak, deferred, rejected.
- Allowed wording.
- Forbidden wording.
- Limitations and risks.

## Ask when missing

Ask one focused question at a time. Choose the next question adaptively from the unresolved owner decision or highest-leverage dependency; the following prompts are unordered examples:

- “What is the one-sentence contribution without hype?”
- “What problem does this contribution solve?”
- “What is the exact research object: method, system, model, dataset, benchmark, application, or analysis object?”
- “Which contribution option is selected, and which tempting options should be rejected?”
- “List the core claims you want the paper to make.”
- “For this claim, what result, figure, table, or artifact supports it?”
- “Which stronger wording must be forbidden because evidence does not support it?”
- “What limitation or risk should downstream writing keep visible?”

## Question card pattern

Use this card when D10-D13 or the `claim-evidence` blocker is first unresolved.

```text
Current stage: Claim/Evidence
Dimension / blocker: D10-D13 / claim-evidence
Why this matters: downstream writing may only state claims that are selected, evidenced, bounded, and risk-aware.
Mode chosen: candidate-confirmation when candidate claims can be proposed from confirmed materials; focused-question when owner must choose a claim or evidence anchor.
Question: How should this core contribution or claim be handled?
Options:
A. selected contribution / active claim — write the owner-confirmed contribution or claim to #Contribution Options or #Claim-Evidence Map with evidence anchor and support strength.
B. conservative wording — write allowed wording and matching forbidden wording to #Allowed Wording and #Forbidden Wording.
C. limitation/risk — write the constraint to #Limitations and Risks and keep downstream wording conservative.
D. deferred claim — record why evidence is not ready; keep D11/D12 blocked for final design-pack compilation.
E. rejected overclaim — write it to #Deferred or Rejected Claims and forbid downstream writing from reviving it.
Agent action after answer: update 02_CLAIM_EVIDENCE_BOUNDARY.md, mirror any evidence-anchor dependency to D06 if needed, and update D10/D11/D12/D13 in 00_DIMENSION_INDEX.md.
```

## Additional question-card seeds

Use these cards when a writing-surface claim boundary is the current blocker. Keep all active claims owner-confirmed, evidence-anchored, and explicitly bounded.

### Front matter and hook claim boundary

```text
Current stage: Claim/Evidence
Dimension / blocker: D10-D13 with D04/D18/D19 / front-matter-hook claim boundary
Why this matters: titles, abstracts, keywords, and visual hooks can amplify overclaims unless their planning constraints mirror evidence strength and forbidden wording.
Mode chosen: focused-question, because front-matter promises and selected contribution wording are owner-gated.
Question: Which front-matter or hook claim boundary should I record?
Options:
A. conservative contribution promise — record allowed wording tied to evidence strength for downstream front-matter planning.
B. forbidden front-matter promise — record hype, novelty, causality, superiority, or generalization language that downstream writing must avoid.
C. hook depends on visual/result evidence — link the hook constraint to D06/D11/D18 and keep it inactive until evidence is locatable.
D. defer front-matter boundary — record unresolved risk and keep D19 handoff constrained.
E. reject hook claim — write the rejected claim to #Deferred or Rejected Claims and prevent downstream revival.
Agent action after answer: update 02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording, #Forbidden Wording, or #Deferred or Rejected Claims, then update D10/D11/D12/D13 and any D18/D19 handoff.
```

### Introduction / related-work citation-function boundary

```text
Current stage: Claim/Evidence
Dimension / blocker: D07/D08 with D10-D13/D14 / intro-related claim boundary
Why this matters: introduction gaps and related-work roles must remain context unless claim evidence and owner-confirmed wording support them.
Mode chosen: candidate-confirmation when supplied dossier notes allow candidate moves; focused-question when owner must confirm a gap or limitation.
Question: How should the planned intro or related-work move be bounded?
Options:
A. owner-confirmed gap claim — record the gap claim with support strength, source-role handoff, and forbidden stronger wording.
B. context-only citation role — record that the source/dossier note may frame background or lineage but not support a core claim.
C. counterevidence or limitation — record risk in #Limitations and Risks and link it to D14 reader-spine planning.
D. deferred source/claim link — keep the move inactive until D07/D08 and D06/D11 are both handled.
E. rejected novelty/gap overclaim — record the overclaim as forbidden wording.
Agent action after answer: update 02_CLAIM_EVIDENCE_BOUNDARY.md and 00_DIMENSION_INDEX.md for D10-D13; hand off source-role updates to D07/D08 without inventing citations.
```

### Method / reporting / reproducibility claim boundary

```text
Current stage: Claim/Evidence
Dimension / blocker: D10-D13 with D05/D06/D15/D19 / method-reporting-repro boundary
Why this matters: downstream method sections must distinguish supported method claims from plain reporting facts and unavailable reproducibility promises.
Mode chosen: focused-question when one artifact or promise controls claim status; reconciliation if route constraints conflict with material availability.
Question: Which method, reporting, or reproducibility statement boundary should I record?
Options:
A. supported method claim — map claim to D06 evidence, support strength, and allowed wording.
B. reporting fact only — record it as an implementation/material fact and forbid claim-strength language.
C. availability or reproducibility promise — allow only if D05 material exists; otherwise mark deferred or forbidden.
D. limitation/risk — record missing artifact, baseline, metric, or environment note as a D13 limitation.
E. rejected method overclaim — write the unsupported method/repro claim to #Deferred or Rejected Claims.
Agent action after answer: update #Claim-Evidence Map, #Allowed Wording, #Forbidden Wording, and #Limitations and Risks, then update D10-D13 and hand off D05/D06/D15/D19 dependencies.
```

### Results / visual / caption / table overclaim boundary

```text
Current stage: Claim/Evidence
Dimension / blocker: D11-D13 with D18/D19 / results-visual-caption-table-accessibility boundary
Why this matters: result text, captions, tables, and visual handoffs must not imply evidence stronger than the mapped result anchor.
Mode chosen: focused-question when one visual/result supports a claim; reconciliation if visual notes conflict with claim strength.
Question: What boundary should govern the result, caption, table, or visual handoff?
Options:
A. active result claim — map it to a locatable result/table/figure anchor and support strength.
B. caption/table explanation only — record what the downstream caption/table may explain without creating a new claim.
C. accessibility/legend note — record accessibility, units, panel order, or legend job as D18/D19 handoff, not evidence.
D. deferred visual evidence — keep the claim inactive if the figure/table/result is needed but not locatable.
E. rejected result overclaim — forbid causal, universal, superiority, or certainty wording not supported by the evidence.
Agent action after answer: update D11-D13 claim boundaries, mirror any D18 visual handoff, and ensure D19 receives only structural risk notes.
```

## Hard blocker

Block design-pack compilation if:

- there is no one-sentence contribution;
- contribution options are not selected/rejected/deferred;
- object granularity is too vague to bind claims;
- a core claim has no evidence anchor and is not explicitly deferred/rejected;
- support strength is unspecified;
- forbidden wording is missing;
- limitations/risks are missing or falsely implied as absent.

## Output sections

Update `02_CLAIM_EVIDENCE_BOUNDARY.md` with:

- Problem / object / contribution;
- Contribution options;
- Object granularity;
- Claim-evidence map;
- Allowed wording;
- Forbidden wording;
- Deferred or rejected claims;
- Limitations and risks.

## Index update examples

- Filled claim map: `D11 | filled | core claims mapped to evidence | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map | yes`.
- Rejected overclaim: `D12 | filled | forbidden wording recorded | 02_CLAIM_EVIDENCE_BOUNDARY.md#Forbidden Wording | yes`.
- Deferred claim: `D11 | deferred | evidence anchor not available | Handoff: obtain result table before supporting claim | yes`.

## Do not assume

- Do not strengthen claims beyond the listed evidence.
- Do not create citation or result anchors from memory.
- Do not hide weak evidence; mark it weak, deferred, or rejected.
