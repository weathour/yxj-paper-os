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
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v2.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/overclaim_repair.v1.yaml
python3 scripts/validate_delivery_gate.py examples/delivery/review_closure.pass.yaml
```

`examples/packets/intro_writing_packet.v1.yaml` was the Phase 4/5 minimal packet fixture. After Phase 6 it is kept only as byte-preserved legacy provenance; strict packet validation uses `intro_writing_packet.v2.yaml`.

Semantic-negative fixtures prove that validation is not syntax-only:

- `examples/materials/claim_boundary_map.v1.yaml` -> `E_CLAIM_STRENGTH_INVALID`;
- `examples/materials/invalid-claim-boundary-missing-forbidden-wording.yaml` -> `E_FORBIDDEN_WORDING_REQUIRED`;
- `examples/materials/invalid-material-status-nonstring.yaml` -> `E_STATUS_INVALID`;
- `examples/materials/invalid-claim-boundary-status-nonstring-empty-claims.yaml` -> `E_STATUS_INVALID`;
- `examples/materials/invalid-claim-strength-nonstring.yaml` -> `E_CLAIM_STRENGTH_INVALID`;
- `examples/materials/invalid-reader-spine-missing-questions.yaml` -> `E_READER_QUESTION_REQUIRED`;
- `examples/materials/invalid-terminology-leak.yaml` -> `E_TERMINOLOGY_LEAK`;
- `examples/packets/invalid-missing-allowed-read-paths.yaml` -> `E_TASK_ALLOWED_READ_PATHS_REQUIRED`;
- `examples/packets/invalid-validator-shape.yaml` is historical; current strict packet shape failures are covered by the Phase 6 fixtures below;
- `examples/review_findings/invalid-missing-target.yaml` -> `E_FINDING_TARGET_REQUIRED`;
- `examples/backflow_tasks/invalid-missing-action.yaml` -> `E_BACKFLOW_ACTION_REQUIRED`;
- `examples/delivery/invalid-delivery-gate-blocker.yaml` -> `E_DELIVERY_GATE_BLOCKER`;
- `examples/delivery/invalid-review-closure-status.yaml`, `examples/delivery/invalid-delivery-gate-status.yaml`, and `examples/delivery/invalid-delivery-gate-status-nonstring.yaml` -> `E_STATUS_INVALID`;
- `examples/delivery/invalid-delivery-gate-scalar-blockers.yaml` -> `E_PAYLOAD_REQUIRED`.


Additional malformed-shape fixtures lock schema-declared field types:

- `examples/review_findings/invalid-target-shape.yaml` -> `E_FINDING_TARGET_REQUIRED`;
- `examples/backflow_tasks/invalid-action-shape.yaml` -> `E_BACKFLOW_ACTION_REQUIRED`;
- `examples/packets/invalid-missing-output-path.yaml` -> `E_TASK_OUTPUT_PATH_REQUIRED`;
- `examples/packets/invalid-input-material-shape.yaml` is historical; current strict packet input/authority failures are covered by the Phase 6 fixtures below;
- `examples/delivery/invalid-review-closure-evidence-shape.yaml` and `examples/delivery/invalid-review-closure-finding-shape.yaml` -> `E_CLOSURE_FINDING_REQUIRED`;
- `examples/materials/invalid-evidence-inventory-package-shape.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-claim-boundary-allowed-claims-scalar.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-claim-boundary-guardrails-scalar.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-claim-boundary-mixed-guardrails.yaml` -> `E_PAYLOAD_REQUIRED`;
- `examples/materials/invalid-reader-spine-questions-shape.yaml` -> `E_READER_QUESTION_REQUIRED`.

The YAML loader is a small stdlib subset parser in `scripts/ppg_validate_common.py`; Phase 4 intentionally forbids `import yaml` / `from yaml` so validation remains deterministic in a fresh Codex/plugin environment.

## Phase 6 strict task-packet and return-contract spine

Phase 6 upgrades `TaskPacket` from a loose context bundle to an authority boundary. The strict fixtures are:

- `examples/packets/intro_writing_packet.v2.yaml`;
- `examples/packets/claim_repair_packet.v1.yaml`.

The historical `examples/packets/intro_writing_packet.v1.yaml` remains a byte-preserved legacy fixture tied to stale graph provenance and is not used as Phase 6 strict-validation evidence.

Core compile/validate commands:

```bash
scripts/verify_phase6_task_packets.sh
```

Key individual commands covered by the script:

```bash
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/phase6-intro-packet.yaml
python3 scripts/validate_packet.py /tmp/phase6-intro-packet.yaml
cmp /tmp/phase6-intro-packet.yaml examples/packets/intro_writing_packet.v2.yaml

python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target claim_boundary_map_candidate_v3 \
  --out /tmp/phase6-claim-repair-packet.yaml
python3 scripts/validate_packet.py /tmp/phase6-claim-repair-packet.yaml
cmp /tmp/phase6-claim-repair-packet.yaml examples/packets/claim_repair_packet.v1.yaml
```

Strict packet negative fixtures lock the authority boundary:

- `examples/packets/invalid-missing-allowed-read-paths.yaml` -> `E_TASK_ALLOWED_READ_PATHS_REQUIRED`;
- `examples/packets/invalid-missing-allowed-write-paths.yaml` -> `E_TASK_ALLOWED_WRITE_PATHS_REQUIRED`;
- `examples/packets/invalid-missing-output-path.yaml` -> `E_TASK_OUTPUT_PATH_REQUIRED`;
- `examples/packets/invalid-missing-evidence-anchors.yaml` -> `E_TASK_EVIDENCE_ANCHORS_REQUIRED`;
- `examples/packets/invalid-completion-forbidden-false.yaml` -> `E_TASK_COMPLETION_FORBIDDEN_REQUIRED`;
- `examples/packets/invalid-recursive-orchestration-false.yaml` -> `E_TASK_NO_RECURSIVE_ORCHESTRATION_REQUIRED`;
- `examples/packets/invalid-output-outside-allowed-writes.yaml` -> `E_TASK_OUTPUT_OUTSIDE_ALLOWED_WRITES`;
- `examples/packets/invalid-owner-gate-required-true.yaml` -> `E_TASK_OWNER_GATE_FORBIDDEN`;
- `examples/packets/invalid-missing-owner-gate-required.yaml` -> `E_TASK_OWNER_GATE_REQUIRED`;
- `examples/packets/invalid-broad-allowed-read-path.yaml` and `examples/packets/invalid-broad-allowed-write-path.yaml` -> `E_TASK_ALLOWED_PATH_TOO_BROAD`;
- `examples/packets/invalid-missing-worker-boot-clause.yaml` and `examples/packets/invalid-weak-worker-boot-clause.yaml` -> `E_TASK_WORKER_BOOT_CLAUSE_REQUIRED`.
- `examples/packets/invalid-output-traversal.yaml` -> `E_TASK_OUTPUT_OUTSIDE_ALLOWED_WRITES`;
- `examples/packets/invalid-allowed-write-traversal.yaml` -> `E_TASK_ALLOWED_PATH_TOO_BROAD`;
- `examples/packets/invalid-missing-forbidden-route.yaml` -> `E_TASK_FORBIDDEN_ROUTES_REQUIRED`;
- `examples/packets/invalid-unsafe-allowed-action.yaml` -> `E_TASK_ALLOWED_ACTIONS_REQUIRED`;
- `examples/packets/invalid-unsafe-allowed-tool.yaml` -> `E_TASK_ALLOWED_TOOLS_REQUIRED`.
- `examples/packets/invalid-broad-material-read-dir.yaml` and `examples/packets/invalid-broad-candidate-write-dir.yaml` -> `E_TASK_ALLOWED_PATH_TOO_BROAD`;
- `examples/packets/invalid-tilde-read-path.yaml` and `examples/packets/invalid-drive-write-path.yaml` -> `E_TASK_ALLOWED_PATH_TOO_BROAD`;
- `examples/packets/invalid-duplicate-none-tool.yaml` -> `E_TASK_ALLOWED_TOOLS_REQUIRED`.
- `examples/packets/invalid-status-committed.yaml` -> `E_TASK_STATUS_PLANNED_REQUIRED`;
- `examples/packets/invalid-unknown-field.yaml` -> `E_TASK_UNKNOWN_FIELD`;
- `examples/packets/invalid-missing-safe-action.yaml` -> `E_TASK_ALLOWED_ACTIONS_REQUIRED`.

Blocked compilation uses `MissingMaterialReport` instead of guessed context:

```bash
python3 scripts/validate_missing_material_report.py \
  examples/missing_material_reports/intro_missing_reader_spine.v1.yaml

python3 scripts/compile_task_packet.py \
  --graph examples/runtime/phase6-missing-reader-spine.json \
  --target section_draft_intro.v2 \
  --out /tmp/should-not-exist-packet.yaml \
  --missing-report-out /tmp/phase6-missing-report.yaml
```

The compile command is expected to exit nonzero, write no packet, and write a valid report.
`examples/missing_material_reports/invalid-unknown-field.yaml` locks `E_REPORT_UNKNOWN_FIELD`.

Candidate returns are validated against their originating packet:

```bash
python3 scripts/validate_candidate_return.py \
  --packet examples/packets/intro_writing_packet.v2.yaml \
  examples/candidate_returns/intro_candidate_return.v1.yaml
```

Negative return fixtures prove no self-certification:

- `examples/candidate_returns/invalid-graph-completion-claimed.yaml` -> `E_RETURN_GRAPH_COMPLETION_FORBIDDEN`;
- `examples/candidate_returns/invalid-recursive-dispatch-requested.yaml` -> `E_RETURN_RECURSIVE_DISPATCH_FORBIDDEN`;
- `examples/candidate_returns/invalid-writes-outside-allowed.yaml` -> `E_RETURN_WRITE_ESCAPE_FORBIDDEN`;
- `examples/candidate_returns/invalid-outside-path-despite-claim.yaml` -> `E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES`;
- `examples/candidate_returns/invalid-path-traversal-despite-prefix.yaml` -> `E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES`;
- `examples/candidate_returns/invalid-output-path-mismatch.yaml` -> `E_RETURN_OUTPUT_PATH_MISMATCH`;
- `examples/candidate_returns/invalid-tilde-output-path.yaml` and `examples/candidate_returns/invalid-drive-output-path.yaml` -> `E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES`;
- `examples/candidate_returns/invalid-packet-id-mismatch.yaml` -> `E_RETURN_PACKET_ID_MISMATCH`;
- `examples/candidate_returns/invalid-missing-remaining-risks.yaml` -> `E_RETURN_REMAINING_RISKS_REQUIRED`.
- `examples/candidate_returns/invalid-unknown-field.yaml` -> `E_RETURN_UNKNOWN_FIELD`.

Phase 6 remains a compiler/contract phase. It intentionally does not run a real writer/verifier subagent pilot; that begins in Phase 7.

## Phase 11 stage-local overlay validation

Phase 11 absorbs Nature expert-writing practice as a registry-backed stage-local overlay.

Core commands:

```bash
python3 scripts/verify_stage_overlays.py
python3 scripts/generate_phase10_run_dry_run.py --check
python3 scripts/verify_phase10_run_readiness.py
```

The overlay validator proves:

- `nature_expert_writing` is present and bound to every canonical stage;
- bare `S09` is rejected in favor of `S09A/S09B`;
- S03 remains `support` or `light`, gated through S04 before writing;
- active department/self-certifying route semantics are rejected while documentation prose such as “not a department” is allowed;
- worker stages have overlay clauses under `mandatory_controls` and a `stage_overlay:nature_expert_writing:<stage_id>` validator;
- Phase10 content validators include `stage_overlay_binding`, `no_department_route`, and worker-stage `stage_overlay_packet_clause`;
- Phase10 dry-run dispatch, validation, candidate placeholder, run-state, manifest, and per-run TaskPackets all link back to `runtime/stage_overlay_registry.json`.

Negative fixtures under `examples/overlays/` lock the expected error codes:

- `invalid-unknown-stage.json` -> `E_STAGE_OVERLAY_UNKNOWN_STAGE`;
- `invalid-bare-s09.json` -> `E_STAGE_OVERLAY_BARE_S09`;
- `invalid-authority-expansion.json` -> `E_STAGE_OVERLAY_AUTHORITY`;
- `invalid-packet-clause-transport.json` -> `E_STAGE_OVERLAY_PACKET_TRANSPORT`;
- `invalid-missing-worker-packet-clause.json` -> `E_STAGE_OVERLAY_PACKET_CLAUSE`;
- `invalid-missing-validator-coverage.json` -> `E_STAGE_OVERLAY_VALIDATOR_COVERAGE`;
- `invalid-active-department-loop.json` -> `E_STAGE_OVERLAY_DEPARTMENT_ROUTE`;
- `invalid-backflow-target.json` -> `E_STAGE_OVERLAY_BACKFLOW_TARGET`;
- `invalid-missing-nature-overlay.json` -> `E_STAGE_OVERLAY_REQUIRED_OVERLAY`;
- `invalid-missing-primary-stage-binding.json` -> `E_STAGE_OVERLAY_REQUIRED_STAGE_BINDING`;
- `invalid-duplicate-stage-binding.json` -> `E_STAGE_OVERLAY_DUPLICATE_BINDING`;
- `invalid-primary-binding-mismatch.json` -> `E_STAGE_OVERLAY_PRIMARY_BINDING_MISMATCH`.
