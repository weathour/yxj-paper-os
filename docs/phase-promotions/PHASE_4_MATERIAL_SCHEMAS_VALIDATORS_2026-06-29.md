# Phase 4 Promotion — Material Schemas and Validators

Date: 2026-06-29
Repository: `yxj-paper-os`
Baseline: Phase 3 promoted in commit `ea698ba`.

## Promotion decision

Phase 4 is promoted as the first machine-checkable schema-and-validator spine for the PPG runtime. The promotion is tied to the commit that carries clean independent code-review and QA disposition evidence.

The runtime can now reject critical paper-production artifacts for semantic reasons, not only for missing files, malformed JSON/YAML, or graph-structure errors.

## Scope promoted

### P0 runtime objects

| Object | Schema | Validator | Primary semantic checks |
| --- | --- | --- | --- |
| `ReviewFinding` | `schemas/ppg-review-finding.schema.json` | `scripts/validate_review_finding.py` | `failure_type`, explicit `target` |
| `BackflowTask` | `schemas/ppg-backflow-task.schema.json` | `scripts/validate_backflow.py` | explicit `target`, explicit repair `action` |
| `ReviewClosure` | `schemas/ppg-review-closure.schema.json` | `scripts/validate_delivery_gate.py` | finding linkage and closure evidence |
| `DeliveryGate` | `schemas/ppg-delivery-gate.schema.json` | `scripts/validate_delivery_gate.py` | no pass with unresolved blockers |
| `TaskPacket` | `schemas/ppg-task-packet.schema.json` | `scripts/validate_packet.py` | non-empty input materials and expected output schema |

### P1 material payload subset

`schemas/ppg-material-payloads.schema.json` and `scripts/validate_material.py` cover the current vertical slice:

- `EvidenceInventory` requires non-empty evidence packages;
- `ClaimBoundaryMap` validates bounded claim-strength vocabulary and forbidden wording/claim guardrails;
- `ReaderSpine` requires reader questions;
- `TerminologyRegister` is treated as a registry material, so stale/blocked terms are allowed in registry fields.

`ClaimEvidenceVisibilityMap`, selected control bundles, section drafts, and figure contracts remain deferred until a later phase selects them as concrete writing/backflow targets.

## Failure code contract

| Code | Meaning |
| --- | --- |
| `E_PARSE` | fixture cannot be loaded by JSON/small-YAML loader |
| `E_ENVELOPE_REQUIRED` | required envelope field missing or wrong schema version |
| `E_STATUS_INVALID` | status is outside the runtime status vocabulary |
| `E_PAYLOAD_REQUIRED` | payload or required payload field missing |
| `E_CLAIM_STRENGTH_INVALID` | claim strength is outside the bounded vocabulary |
| `E_FORBIDDEN_WORDING_REQUIRED` | claim boundary lacks forbidden wording/claim guardrails |
| `E_READER_QUESTION_REQUIRED` | reader spine has no reader questions |
| `E_TERMINOLOGY_LEAK` | paper-facing text contains internal sidecar/runtime terms |
| `E_TASK_INPUTS_REQUIRED` | task packet lacks input materials |
| `E_TASK_OUTPUT_SCHEMA_REQUIRED` | task packet lacks expected output schema |
| `E_FINDING_FAILURE_TYPE_REQUIRED` | review finding lacks failure type |
| `E_FINDING_TARGET_REQUIRED` | review finding lacks target material/artifact |
| `E_BACKFLOW_TARGET_REQUIRED` | backflow task lacks explicit target |
| `E_BACKFLOW_ACTION_REQUIRED` | backflow task lacks repair action |
| `E_CLOSURE_FINDING_REQUIRED` | review closure lacks finding/evidence linkage |
| `E_DELIVERY_GATE_BLOCKER` | delivery gate claims pass with unresolved blockers |

## Fixtures added

Positive fixtures:

- `examples/review_findings/overclaim.v1.yaml`;
- `examples/packets/intro_writing_packet.v1.yaml`;
- `examples/backflow_tasks/overclaim_repair.v1.yaml`;
- `examples/delivery/review_closure.pass.yaml`;
- `examples/delivery/delivery_gate.pass.yaml`.

Semantic-negative fixtures:

- `examples/materials/claim_boundary_map.v1.yaml` intentionally fails material validation with `E_CLAIM_STRENGTH_INVALID` while remaining historical graph provenance;
- `examples/materials/invalid-claim-strength.yaml` -> `E_CLAIM_STRENGTH_INVALID`;
- `examples/materials/invalid-claim-boundary-missing-forbidden-wording.yaml` -> `E_FORBIDDEN_WORDING_REQUIRED`;
- `examples/materials/invalid-material-status-nonstring.yaml` -> `E_STATUS_INVALID`;
- `examples/materials/invalid-claim-boundary-status-nonstring-empty-claims.yaml` -> `E_STATUS_INVALID`;
- `examples/materials/invalid-claim-strength-nonstring.yaml` -> `E_CLAIM_STRENGTH_INVALID`;
- `examples/materials/invalid-reader-spine-missing-questions.yaml` -> `E_READER_QUESTION_REQUIRED`;
- `examples/materials/invalid-material-missing-payload.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-terminology-leak.yaml` -> `E_TERMINOLOGY_LEAK`;
- `examples/materials/invalid-yaml-syntax.yaml` -> `E_PARSE`;
- `examples/delivery/invalid-review-closure-status.yaml` -> `E_STATUS_INVALID`;
- `examples/delivery/invalid-delivery-gate-status.yaml` -> `E_STATUS_INVALID`;
- `examples/delivery/invalid-delivery-gate-status-nonstring.yaml` -> `E_STATUS_INVALID`;
- `examples/delivery/invalid-delivery-gate-scalar-blockers.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/packets/invalid-validator-shape.yaml` -> `E_PAYLOAD_REQUIRED`;
- P0 invalid fixtures under `examples/review_findings/`, `examples/packets/`, `examples/backflow_tasks/`, and `examples/delivery/` cover each P0 failure code.


Additional malformed-shape fixtures lock schema-declared field types:

- `examples/review_findings/invalid-target-shape.yaml` -> `E_FINDING_TARGET_REQUIRED`;
- `examples/backflow_tasks/invalid-action-shape.yaml` -> `E_BACKFLOW_ACTION_REQUIRED`;
- `examples/packets/invalid-output-schema-shape.yaml` -> `E_TASK_OUTPUT_SCHEMA_REQUIRED`;
- `examples/packets/invalid-input-material-shape.yaml` -> `E_TASK_INPUTS_REQUIRED`;
- `examples/delivery/invalid-review-closure-evidence-shape.yaml` and `examples/delivery/invalid-review-closure-finding-shape.yaml` -> `E_CLOSURE_FINDING_REQUIRED`;
- `examples/materials/invalid-evidence-inventory-package-shape.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-claim-boundary-allowed-claims-scalar.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-claim-boundary-guardrails-scalar.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-claim-boundary-mixed-guardrails.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-reader-spine-questions-shape.yaml` -> `E_READER_QUESTION_REQUIRED`.

## Validation evidence

Observed on 2026-06-29:

```bash
python3 -m py_compile scripts/validate_graph.py scripts/ppg_store.py scripts/ppg_validate_common.py scripts/validate_material.py scripts/validate_review_finding.py scripts/validate_packet.py scripts/validate_backflow.py scripts/validate_delivery_gate.py
python3 -m ruff check scripts/validate_graph.py scripts/ppg_store.py scripts/ppg_validate_common.py scripts/validate_material.py scripts/validate_review_finding.py scripts/validate_packet.py scripts/validate_backflow.py scripts/validate_delivery_gate.py
pyright scripts/validate_graph.py scripts/ppg_store.py scripts/ppg_validate_common.py scripts/validate_material.py scripts/validate_review_finding.py scripts/validate_packet.py scripts/validate_backflow.py scripts/validate_delivery_gate.py
```

Result: pass.

Additional observed checks:

- all `schemas/*.json` parsed with Python `json`;
- all P0/P1 positive fixtures returned `VALID`;
- all listed negative fixtures exited non-zero and emitted expected codes;
- Phase 2/3 graph/controller regression fixtures still pass;
- all `examples/runtime/invalid-*.json` still fail graph validation;
- no `import yaml` / `from yaml` exists in Phase 4 validators;
- repeated validation of `examples/materials/claim_boundary_map.v2.yaml` produced byte-identical output;
- plugin manifest validation passed;
- `git diff --check` passed.

## Review and QA disposition

- Ralplan consensus: Architect APPROVE/CLEAR followed by Critic APPROVE/CLEAR before implementation.
- Code-review gate: clean after rework; code-reviewer `019f1310-a5f2-7180-af27-0679f4915dfd` returned `APPROVE`, and architect `019f1311-399c-7691-94bc-ac133ab2b35c` returned `CLEAR`.
- UltraQA disposition: CLI/runtime QA substitute is sufficient because Phase 4 changes are deterministic schemas, validators, and fixtures rather than a human-facing UI flow.

## Known limits deferred to Phase 5+

- No stale propagation or backflow compiler is implemented in Phase 4.
- `BackflowTask` is validated as an explicit object; target inference is not implemented.
- `ClaimEvidenceVisibilityMap` is deferred unless Phase 5 selects it as the concrete overclaim backflow target.
- Real subagent dispatch remains future work; Phase 4 only validates packets and material objects.
- Frontend runtime-state display is not part of this phase.

## Next allowed starting state

Phase 5 may assume:

1. P0 review/backflow/delivery/task objects have stable schema files and validators;
2. current vertical-slice material payloads can be semantically accepted or rejected;
3. `claim_boundary_map.v1.yaml` is intentionally stale and materially invalid, while `claim_boundary_map.v2.yaml` is the active valid boundary;
4. sidecar pollution lint is scoped to paper-facing text, not internal registry/control fields.
