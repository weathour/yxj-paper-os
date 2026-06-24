---
name: yxj-paper-state
description: "Maintain yxj-paper-os paper state ledgers, task ledgers, artifact ledgers, decision ledgers, evidence ledgers, review ledgers, export ledgers, and state transitions. Use when inspecting, validating, or updating paper project state and completion claims."
---


# yxj-paper-state

Own the control plane under `<paper-root>/.omx/state/yxj-paper-os/`.

## Required ledgers

- `state.yaml`: current phase, active gate, blockers, next safe action.
- `task-ledger.yaml`: compiled tasks, route, `agent_type`, status, collection, validators, ingestion.
- `artifact-ledger.yaml`: artifact ids, owners, privacy policy, validators, hashes, status.
- `decision-ledger.yaml`: confirmed paper-owner choices versus assumptions.
- `evidence-ledger.yaml`: claims, evidence/citation/source anchors, unresolved support.
- `review-ledger.yaml`: review findings, owner lane, fix task, status.
- `export-ledger.yaml`: export readiness, build reports, validation evidence, residual risks.

## Transition invariant

Use `references/state-contract.md`. Do not mark a task complete unless collected output, validator evidence, and state ingestion are all present.

## Alias rule

`validator_refs` is canonical. If a legacy packet has `validators` and no `validator_refs`, normalize it to `validator_refs` before validation. If both exist, they must match exactly.


## Guard command

Use `../yxj-paper-index/scripts/ledger_guard.py check --root <paper-root>` after ledger edits. Use `stamp` for simple completed operation rows, and `snapshot` when `.omx/` is ignored but progress must remain reviewable in tracked notes.
