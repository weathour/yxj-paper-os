---
name: yxj-paper-review
description: "Run yxj-paper-os adversarial paper review, hostile reviewer panels, verifier gates, review independence checks, routed findings, and branch backflow. Use when drafts, outlines, motivation, evidence packages, or exports need independent review."
---


# yxj-paper-review

Use Sisyphus-like hostile reviewers and verifier gates, then route every accepted finding to an owner lane.

## Reviewer lenses

Theorist, empiricist, methodologist, skeptic, historian, competitor, pragmatist, ethicist, student, and dreamer.

## Backflow rule

No review is complete if an accepted finding lacks severity, evidence status, owner lane, fix task, and resolution status.

## Reader-facing surface review

Hostile review must include a surface-language pass, not only claim/evidence
correctness. The reviewer should read the rendered main artifact and flag any
place where the paper still sounds like an experiment notebook, internal ledger,
or implementation trace.

Accepted findings must route to a `NarrativeBackflowTask` or equivalent task
with owner lane `reader-narrative-governance` or `manuscript-owner` and
validators for internal-code removal, citation rendering, and PDF-text surface
quality.


## Authority and self-certification review

For paper-facing, export-facing, claim/evidence, or state-sensitive work, review must
check whether the manager directly produced, reviewed, verified, exported, or
transitioned the material. If so, require `ManagerDirectIntervention`, trusted actor
provenance, a distinct effective reviewer, and final-certifier separation before
accepting `complete`. A manager-authored summary or `present:false` field is not
enough.
