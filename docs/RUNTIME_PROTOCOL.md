# Runtime Protocol — Main-Agent Control

## Main-agent identity

The main agent is the **Paper Production Graph Runtime Controller**. It owns process control, not route self-management.

## Runtime loop

```text
observe graph
  -> select next frontier node
  -> compile task packet
  -> dispatch specialist or run script
  -> collect candidate output
  -> validate
  -> commit / mark stale / create backflow
  -> repeat
```

## Graph state summary

The main agent maintains:

```yaml
GraphState:
  active_target:
  current_gate:
  committed_materials:
  candidate_materials:
  stale_materials:
  blocked_materials:
  owner_gated_materials:
  open_review_findings:
  next_frontier:
```

## Frontier queue priority

Default priority:

```text
owner_gated root decision
> stale upstream control material
> blocked validator/material prerequisite
> missing task packet for active manuscript unit
> candidate output awaiting validation
> review finding awaiting classification
> export/rendering blocker
> optional improvement
```

## Strict TaskPacket boundary

Subagents receive bounded context only. Phase 6 makes this boundary executable as a strict `TaskPacket`:

```yaml
TaskPacket:
  schema_version: ppg-task-packet/v0.1
  packet_id:
  status: planned
  task_kind:
  agent_type:
  mission:
  target_material:
  input_materials: []
  mandatory_controls: {}
  evidence_anchors: []
  forbidden_routes:
  allowed_actions:
  allowed_read_paths:
  allowed_write_paths:
  allowed_tools:
  output_artifact_path:
  expected_output_schema:
  validators:
  return_format:
  ingestion_target:
  stop_condition:
  failure_report_format: ppg-missing-material-report/v0.1
  worker_boot_clause:
  completion_forbidden: true
  no_recursive_orchestration: true
  owner_gate_required: false
```

The subagent returns a `CandidateArtifactReturn` plus a candidate artifact/evidence. It does not mark completion, recursively dispatch agents, change owner intent, or write outside `allowed_write_paths`.

Strict packet validation also enforces safe authority semantics for Phase 6 worker packets:

- strict packet `status` is exactly `planned`;
- unknown TaskPacket fields are rejected;
- required blocked routes include `mark_graph_complete`, `dispatch_subagents`, `write_outside_allowed_write_paths`, and `change_owner_intent`;
- allowed actions must exactly match the safe set `read_material_bundle`, `draft_candidate_artifact`, and `return_evidence`;
- allowed tools must be exactly `none`;
- allowed paths and return paths must be safe repo-relative file paths, with no absolute paths, root-like broad paths, home/drive-style prefixes, control characters, or `.` / `..` traversal components;
- allowed read paths are limited to current Phase 6 fixture evidence surfaces: `examples/materials/`, `examples/review_findings/`, and `examples/backflow_tasks/`;
- allowed write paths are limited to one exact output file under `examples/candidate-artifacts/` or `examples/materials/`.

If required materials are absent, the compiler must emit a `MissingMaterialReport` and no task packet. It must not guess missing controls.

Historical `examples/packets/intro_writing_packet.v1.yaml` is a stale fixture tied to stale `claim_boundary_map_v1`; Phase 6 strict validation starts with `intro_writing_packet.v2.yaml` and `claim_repair_packet.v1.yaml`.

## Phase 6 packet compiler

`scripts/compile_task_packet.py` compiles bounded packets from validated graph state:

```bash
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/intro_packet.yaml

python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target claim_boundary_map_candidate_v3 \
  --out /tmp/claim_repair_packet.yaml
```

Current supported targets:

- intro writing aliases: `section_draft_intro.v1`, `section_draft_intro.v2`, `intro_draft_v2`;
- claim-repair aliases: `claim_boundary_map_candidate_v3`, `claim_boundary_repair.v1`.

Unsupported targets fail with `E_TASK_TARGET_UNSUPPORTED` and write no packet. Missing materials fail with `E_TASK_MISSING_MATERIAL`; when `--missing-report-out` is supplied, the compiler writes a valid `ppg-missing-material-report/v0.1`.

At compile start, declared packet and missing-report output files are cleared so stale artifacts cannot survive a failed, unsupported, or successful compile branch.

## Candidate-return validation

Candidate returns are packet-aware:

```bash
python3 scripts/validate_candidate_return.py \
  --packet examples/packets/intro_writing_packet.v2.yaml \
  examples/candidate_returns/intro_candidate_return.v1.yaml
```

The validator compares the return `packet_id` and `output_artifact_path` against the originating packet. Worker self-certification is not sufficient: a return with `writes_outside_allowed_paths: false` still fails if the path is outside the packet's write boundary.

The return `output_artifact_path` must equal the originating packet's `output_artifact_path`; being merely inside a broader allowed-write directory is not sufficient. Unknown `CandidateArtifactReturn` fields are rejected so a worker cannot smuggle extra authority claims into the return object.

## Dispatch policy

Use scripts for deterministic tasks:

- schema validation;
- graph consistency;
- stale propagation;
- artifact indexing;
- internal-code scanning;
- rendered text scanning;
- hash/manifest generation.

Use subagents for semantic tasks:

- reader question design;
- contribution and claim boundary analysis;
- writing task packet drafting;
- section/caption drafting;
- adversarial review;
- reader experience review.

Do not run a real writer/verifier worker pilot in Phase 6. The Phase 6 deliverable is the deterministic compiler/contract layer; real subagent execution begins only after these packet boundaries are available.

Use hybrid mode for:

- claim-evidence matrix;
- terminology register;
- main text construction matrix;
- review finding classification;
- backflow task compilation.

## Main-agent subagent lane policy

The main agent now treats single-vs-double subagent use as an explicit stage contract, not an ad hoc choice. The source of truth is `runtime/stage_registry.json[*].subagent_lane_policy`, mirrored by every `examples/stage-contracts/*.stage-contract.json` and checked by `scripts/verify_stage_registry.py` plus `scripts/verify_stage_contracts.py`.

Decision order:

```text
read stage.subagent_lane_policy
  -> if policy == mandatory_double:
       dispatch producer lane + independent verifier lane
  -> if policy == conditional_double:
       dispatch one producer lane by default;
       add verifier lane when any escalate_to_double_when trigger is active
  -> if policy == single_with_deterministic_validation:
       keep one controller/script lane by default;
       rely on deterministic validators unless an audit trigger is active
  -> collect CandidateArtifactReturn / validator evidence
  -> controller alone accepts, rejects, or routes backflow
```

Current default classification:

- **Mandatory double:** S02, S03, S04, S05, S10, S12, S13, S15.
- **Conditional double:** S00, S01, S06, S07, S08, S11, S14, S16.
- **Single with deterministic validation:** S09A, S09B, G01, G02.

Phase 13 intentionally ran all canonical stages with producer + verifier lanes as a strict live-pilot QA mode. Production runtime is more selective: it keeps mandatory semantic/paper-facing stages double-lane, uses conditional verifier lanes at freezes or high-risk branch points, and keeps compiler/governance stages primarily script-validated.

## Commit protocol

```text
candidate exists
  -> validators pass
  -> provenance recorded
  -> stale impact checked
  -> graph status updated
  -> active version pointer updated
```

Only after this can a node become `committed`.

## Authority boundaries

- Owner intent changes require human decision evidence.
- Subagents cannot commit or close graph nodes.
- Reviewers produce findings, not direct whole-paper edits.
- Main agent can repair locally only inside existing owner-approved semantics.
