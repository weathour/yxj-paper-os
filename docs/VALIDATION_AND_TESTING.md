# Validation and Testing Plan

## Validator categories

### Graph validators

- all edge endpoints exist;
- node ids are unique;
- committed manuscript artifacts have writing task packets;
- review findings have backflow targets;
- stale nodes list a stale reason;
- owner intent changes have owner evidence.

### Material validators

- envelope fields present;
- typed payload required fields present;
- source inputs exist;
- validators are declared;
- invalidation policy exists.

### Manuscript validators

- no internal code leakage in main prose;
- no raw snake_case constraints;
- no bare citation keys in rendered output;
- claims obey evidence visibility limits;
- section units answer declared reader questions;
- terminology register is consumed.

### Backflow validators

- every finding has a failure type;
- every backflow task has a target node;
- stale propagation is scoped;
- unrelated downstream nodes remain unchanged;
- repaired nodes create new versions.

## Test levels

### Level 1 — Structural graph test

Run:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
```

### Level 2 — Single-node fixture test

Use a small material fixture and verify schema/envelope.

Examples:

- `ReviewerQuestionMap` fixture;
- `TerminologyRegister` fixture;
- `WritingTaskPacket` fixture.

### Level 3 — Local backflow fixture

Simulate:

```text
finding: claim overreach in Introduction paragraph
```

Expected:

- classify as `L3_claim_evidence`;
- target `ClaimEvidenceVisibilityMap` or `ClaimEvidenceMatrix`;
- mark affected introduction draft stale;
- do not mark unrelated related-work draft stale.

### Level 4 — Mock paper closed loop

Run a toy graph:

```text
intent -> analysis -> control materials -> writing task -> draft -> review -> backflow -> revised draft
```

### Level 5 — Real-paper single-section pilot

Apply the runtime to one section only, ideally Introduction contribution paragraph or one result interpretation paragraph.

Exit gate:

- graph shows all materials and affected dependencies;
- draft is produced from task packet;
- review finding triggers local backflow;
- unrelated nodes are not rewritten.

## Phase 4 executable validator spine

Phase 4 adds dependency-free validators for the current runtime-critical material objects.
All validators emit deterministic CLI output:

```text
VALID <path>
```

or:

```text
INVALID <path>
- CODE: message
```

Core commands:

```bash
python3 scripts/validate_material.py examples/materials/claim_boundary_map.v2.yaml
python3 scripts/validate_review_finding.py examples/review_findings/overclaim.v1.yaml
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v1.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/overclaim_repair.v1.yaml
python3 scripts/validate_delivery_gate.py examples/delivery/review_closure.pass.yaml
```

Semantic-negative fixtures prove that validation is not syntax-only:

- `examples/materials/claim_boundary_map.v1.yaml` -> `E_CLAIM_STRENGTH_INVALID`;
- `examples/materials/invalid-claim-boundary-missing-forbidden-wording.yaml` -> `E_FORBIDDEN_WORDING_REQUIRED`;
- `examples/materials/invalid-material-status-nonstring.yaml` -> `E_STATUS_INVALID`;
- `examples/materials/invalid-claim-boundary-status-nonstring-empty-claims.yaml` -> `E_STATUS_INVALID`;
- `examples/materials/invalid-claim-strength-nonstring.yaml` -> `E_CLAIM_STRENGTH_INVALID`;
- `examples/materials/invalid-reader-spine-missing-questions.yaml` -> `E_READER_QUESTION_REQUIRED`;
- `examples/materials/invalid-terminology-leak.yaml` -> `E_TERMINOLOGY_LEAK`;
- `examples/packets/invalid-missing-inputs.yaml` -> `E_TASK_INPUTS_REQUIRED`;
- `examples/packets/invalid-validator-shape.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/review_findings/invalid-missing-target.yaml` -> `E_FINDING_TARGET_REQUIRED`;
- `examples/backflow_tasks/invalid-missing-action.yaml` -> `E_BACKFLOW_ACTION_REQUIRED`;
- `examples/delivery/invalid-delivery-gate-blocker.yaml` -> `E_DELIVERY_GATE_BLOCKER`;
- `examples/delivery/invalid-review-closure-status.yaml`, `examples/delivery/invalid-delivery-gate-status.yaml`, and `examples/delivery/invalid-delivery-gate-status-nonstring.yaml` -> `E_STATUS_INVALID`;
- `examples/delivery/invalid-delivery-gate-scalar-blockers.yaml` -> `E_PAYLOAD_REQUIRED`.


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

The YAML loader is a small stdlib subset parser in `scripts/ppg_validate_common.py`; Phase 4 intentionally forbids `import yaml` / `from yaml` so validation remains deterministic in a fresh Codex/plugin environment.

