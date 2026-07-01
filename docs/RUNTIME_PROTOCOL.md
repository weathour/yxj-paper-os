# Runtime Protocol — Main-Agent Control

The main agent is the **Paper Production Graph Runtime Controller**. It owns process control and graph authority.

## Runtime loop

```text
observe graph
  -> choose frontier or feedback item
  -> compile task/repair packet
  -> dispatch specialist or deterministic script
  -> collect candidate output
  -> validate
  -> commit / reject / mark stale / create backflow
  -> after full run, evaluate retrospective learning
```

## Graph state summary

```yaml
GraphState:
  active_target:
  current_gate:
  committed_materials:
  candidate_materials:
  stale_materials:
  blocked_materials:
  owner_gated_materials:
  open_feedback_packages:
  open_review_findings:
  open_backflow_tasks:
  proposed_stage_improvements:
  next_frontier:
```

A template-only LaTeX build proves template sanity, not S12 integration or manuscript readiness.

## Frontier priority

```text
owner-gated root decision
> blocked upstream material or validator prerequisite
> active feedback attribution or repair task
> stale downstream regeneration
> missing task packet for active manuscript unit
> candidate output awaiting validation
> review finding awaiting classification
> export/rendering blocker
> post-run stage improvement
> optional improvement
```

## TaskPacket boundary

Subagents receive bounded context only:

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
  forbidden_routes: []
  allowed_actions: []
  allowed_read_paths: []
  allowed_write_paths: []
  allowed_tools: []
  output_artifact_path:
  expected_output_schema:
  validators: []
  return_format:
  ingestion_target:
  stop_condition:
  failure_report_format:
  worker_boot_clause:
  completion_forbidden: true
  no_recursive_orchestration: true
  owner_gate_required: false
```

Workers return `CandidateArtifactReturn` plus candidate artifact/evidence. They do not mark completion, recursively dispatch agents, change owner intent, or write outside allowed paths.

## RepairTaskPacket boundary

Repair packets are scoped current-paper repair contracts. They wrap or point to strict TaskPackets/BackflowTasks and inherit the same authority restrictions:

- no completion authority;
- no recursive orchestration;
- no owner-intent changes;
- no whole-paper rewrite unless owner-gated;
- scoped read/write paths;
- explicit preserve and must-change clauses;
- downstream stale targets and validators.

## Dispatch policy

Use scripts for deterministic tasks:

- schema validation;
- graph consistency;
- stale propagation;
- artifact indexing;
- internal-code scanning;
- rendered text scanning;
- hash/manifest generation.

Use semantic agents for bounded tasks:

- field/SOTA analysis;
- contribution challenge;
- claim boundary analysis;
- paper spine and reader questions;
- writing and caption candidates;
- adversarial review;
- failure attribution review for high-risk findings.

## Main-agent lane policy

The stage registry controls single/double-lane use:

```text
read stage.subagent_lane_policy
  -> mandatory_double: producer + independent verifier
  -> conditional_double: producer, add verifier on listed triggers
  -> single_with_deterministic_validation: script/controller plus validators
  -> controller accepts, rejects, or routes backflow
```

## Commit protocol

```text
candidate exists
  -> validators pass
  -> provenance recorded
  -> stale impact checked
  -> graph status updated
  -> active version pointer updated
```

Only then can a node become `committed`.

## Retrospective protocol

After a full paper run or major review cycle:

```text
collect feedback/repair records
  -> group recurring failure patterns
  -> decide current-paper issue vs system issue
  -> propose StageImprovementRecord candidates
  -> add regression tests before changing prompts/task packets/validators
```

A StageImprovementRecord is a system-learning proposal. It does not directly edit the current manuscript.

## Authority boundaries

- Owner intent changes require owner decision evidence.
- Subagents cannot commit or close graph nodes.
- Reviewers produce findings, not whole-paper edits.
- Main agent can repair locally only inside existing owner-approved semantics.
- Optional orchestration tools are adapters, not Paper OS authority sources.
