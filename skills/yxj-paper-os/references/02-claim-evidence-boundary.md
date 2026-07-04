# Playbook 02 — Claim Evidence Boundary

Use this playbook when `02_CLAIM_EVIDENCE_BOUNDARY.md` is missing or when claims lack evidence anchors.

## Required fields

- Problem statement.
- Research object: method, system, model, dataset, benchmark, application, or analysis object.
- One-sentence core contribution.
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
3. “List the core claims you want the paper to make.”
4. “For this claim, what result, figure, table, or artifact supports it?”
5. “Which stronger wording must be forbidden because evidence does not support it?”

## Hard blocker

Block design-pack compilation if:

- there is no one-sentence contribution;
- a core claim has no evidence anchor and is not explicitly deferred/rejected;
- support strength is unspecified;
- forbidden wording is missing.

## Output sections

Update `02_CLAIM_EVIDENCE_BOUNDARY.md` with:

- Problem / object / contribution;
- Claim-evidence map;
- Allowed wording;
- Forbidden wording;
- Deferred or rejected claims;
- Limitations and risks.

## Do not assume

- Do not strengthen claims beyond the listed evidence.
- Do not create citation or result anchors from memory.
- Do not hide weak evidence; mark it weak, deferred, or rejected.
