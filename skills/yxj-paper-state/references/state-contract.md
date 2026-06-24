# State contract

The state machine prevents false completion.

## Canonical pipeline

`compile -> execute -> collect -> validate -> ingest -> state_transition`

## Task statuses

| status | meaning | can be terminal |
| --- | --- | --- |
| draft | task idea exists | no |
| compiled | task packet has required fields | no |
| dispatched | subagent/team was requested | no |
| executing | worker is active | no |
| collected | expected output was collected | no |
| validated | validators passed and report exists | no |
| ingested | ledgers updated with validated artifact | no |
| complete | collected + validated + ingested + state transition | yes |
| blocked | needs user decision or unavailable authority | yes, non-success |
| failed | validator/runtime failure | yes, non-success |

## Completion proof

A task with `status: complete` must have all of:

- `collected_outputs[]` with existing artifact paths;
- `validator_evidence[]` with `status: pass` and validator refs;
- `state_ingestion.status: ingested` and `state_ingestion.ledger_path`;
- a valid owner lane;
- known validator refs.

`dispatched`, `executing`, `collected`, and `validated` are never equivalent to `complete`.

## Validator alias rule

`validator_refs` is canonical. `validators` is a legacy alias only when `validator_refs` is absent. If both fields exist, they must contain the same ordered values.

## PUA telemetry state rule

`pua_telemetry` records managed-agent pressure state for each compiled task. L0
means normal execution; L1-L4 represent escalating control requirements. L2+
requires `[PUA-REPORT]`; L3+ requires the seven-item checklist. The field is
useful for audit and retry decisions, but it never replaces validator evidence.
A task can still be `complete` only after collected outputs, passing validator
evidence, state ingestion, a valid owner lane, known validator refs, and the
canonical `compile -> execute -> collect -> validate -> ingest -> state_transition` path.


### PUA report semantic checks

At L2+ `pua_report.present:true` is mandatory and must exactly mirror failure count, failure mode, attempts, excluded causes, next hypothesis, and manager action from top-level `pua_telemetry`. At L3+ all seven checklist booleans must be true. L4 requires `failure_count >= 5`. These semantics are enforced by `validate_pua_telemetry` and covered by invalid fixtures.


### Explicit state transition fixture rule

Fixture-level validation mirrors `ledger_guard.py`: a task marked `complete` must include collected outputs, validator evidence, state ingestion, `pipeline_stage: state_transition`, and an explicit `state_transition` object with `from`, `to: complete`, and `at`. `pipeline_stage: state_transition` alone is not enough.
