# Playbook 02 — Claim Evidence Boundary

Use this playbook when `02_CLAIM_EVIDENCE_BOUNDARY.md` is missing, when claims lack evidence anchors, or when D10/D11/D12/D13 or claim-side D16/D17 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is a central internal rubric/reference, not a sixth task playbook and not a public workspace file. Do not duplicate its full D00-D19 rubric here.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D10 | `12_contribution_options.md` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options` |
| D11 | `13_claim_evidence_map.md` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map` |
| D12 | `14_wording_boundary.md` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording` |
| D13 | `15_limitation_and_risk_matrix.md` | `02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks` |
| D16 | `22_object_granularity.md` | Secondary: `02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity`; primary pointer normally lives in `03_WRITING_STRUCTURE.md#Object Granularity` |
| D17 | `23_surface_control.md` | Secondary: claim wording in `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording`; primary pointer normally lives in `03_WRITING_STRUCTURE.md#Surface Control` |

After updating claim content, update the matching dimension rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## First-batch cross-boundary reminder

The central rubric owns the full D07/D08/D09/D18/D19 rules. In this claim/evidence playbook, enforce the shared boundary before allowing any claim to become active:

- Sources, citation candidates, research dossier notes, exemplar/style guidance, design-pack summaries, and visual plans are not evidence anchors by themselves.
- A claim may be supported only when D06 identifies a locatable evidence anchor and D11 maps the active claim to that anchor with support strength and wording boundaries.
- D07/D08 can explain context, citation needs, conflicts, gaps, or handoff risks; they cannot prove novelty, source truth, or claim truth.
- D09 can constrain style and D17 surface control; it cannot raise claim strength.
- D18 can plan visuals; needed/deferred/absent visuals cannot support active claims.
- D19 can summarize the boundary as a structural handoff; it cannot convert unresolved sources, visuals, or dossier notes into readiness.

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

Ask one focused question at a time. Prefer this order:

1. “What is the one-sentence contribution without hype?”
2. “What problem does this contribution solve?”
3. “What is the exact research object: method, system, model, dataset, benchmark, application, or analysis object?”
4. “Which contribution option is selected, and which tempting options should be rejected?”
5. “List the core claims you want the paper to make.”
6. “For this claim, what result, figure, table, or artifact supports it?”
7. “Which stronger wording must be forbidden because evidence does not support it?”
8. “What limitation or risk should downstream writing keep visible?”

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
