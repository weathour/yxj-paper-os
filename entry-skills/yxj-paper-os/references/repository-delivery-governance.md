# Repository hygiene and delivery cleanliness governance

`yxj-paper-os` treats repository hygiene and delivery cleanliness as a first-class PMO gate. It is not an afterthought after writing or export.

## Scope

This contract applies when a paper task affects any of the following:

- final or pre-author-review handoff;
- export/readiness/package work;
- state or ledger closure;
- cross-paper workspace inspection;
- generated artifacts, temporary files, or untracked directories;
- any report that claims the paper is ready for an author, reviewer, or external venue.

## PMO responsibility

The Paper Orchestrator must distinguish:

- **content readiness**: manuscript/evidence/review/export quality;
- **repository hygiene**: whether the worktree is clean enough to hand off, commit, rollback, or reproduce;
- **delivery cleanliness**: whether the exported package contains only intended deliverables with provenance, hashes, build reports, and explicit external-submission boundary.

A paper can be evidence-ready while still delivery-dirty. Do not collapse these states.

## Required material object

Use `RepositoryHygieneReport` for the handoff gate.

Minimum evidence:

- `git status --short --untracked-files=all` or an explicit non-git workspace explanation;
- dirty entry counts split into current paper, parent/shared, and sibling paper paths;
- untracked, deleted, modified, generated/ephemeral, and disallowed entries;
- allowed dirty patterns with rationale;
- ledger/snapshot freshness result;
- export manifest hash/provenance result when export exists;
- external submission/upload boundary;
- owner decisions required for dirty or cross-root items;
- recommended cleanup, ignore, stage, archive, or block action.

## Status vocabulary

- `clean`: no dirty entries relevant to the active paper and no sibling/parent contamination.
- `dirty_allowed`: only declared generated/ephemeral or owner-approved dirty entries exist; handoff must name them.
- `dirty_blocked`: disallowed current-paper changes, sibling/parent contamination, deleted state, missing manifest hashes, stale snapshot, or ambiguous export package exists.
- `owner_gated`: cleanup, staging, commit, external submission, or cross-root action requires paper-owner decision.

## Closure rule

A final/pre-author-review/export task cannot be reported as fully clean unless:

```text
RepositoryHygieneReport.delivery_cleanliness_gate.status == pass
and disallowed_dirty_entries == []
and sibling_or_parent_contamination.status in {none, accepted_with_owner_decision}
and snapshot_freshness.status in {pass, not_required}
and export_manifest_hashes.status in {pass, not_required}
and external_submission.status clearly states not_performed_requires_explicit_confirmation or explicit_owner_confirmed
```

If this cannot be proven, report the paper state as content-validated but delivery-dirty or owner-gated.

## Department ownership

Primary owner: PMO / Paper Management, lane `repository-hygiene-owner`, agent type `verifier`.

Consumers:

- Review & Governance uses it before final quality gates.
- Export owner uses it before package readiness claims.
- State steward uses it before ledgers/snapshots are called closed.
- Paper owner uses it to decide cleanup, commit, archive, or external submission boundaries.

## Manager handoff requirement

Broad handoffs must include a dedicated repository hygiene line:

- dirty counts and scope;
- current-paper vs sibling/parent contamination;
- generated/ephemeral files;
- disallowed files;
- cleanup or owner-gated decisions;
- whether delivery cleanliness is `pass`, `blocked`, or `owner-gated`.

Raw `git status` logs may appear in the verification appendix, not as the main report.
