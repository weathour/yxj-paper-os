# PPG Runtime Macro Execution Plan

Date: 2026-06-29  
Scope: macro推进目标、工程流程、实现参考、subagent task packet 设定、主 agent 调度原则。  
Baseline: stage/material taxonomy v0.2 has been accepted as a design baseline, but runnable runtime is not proven.

## 0. Executive decision

Continue in the new `yxj-paper-ppg-runtime` repository. Do not perform a large in-place rewrite of `$yxj-paper-os` yet.

The current stage graph is now a stable **human-facing transform taxonomy**. The next goal is to build an executable **versioned material graph runtime** under it.

```text
Do not keep rearranging S-nodes.
Build the runtime core that proves one vertical paper-production loop.
```

## 1. North-star runtime target

The target runtime is not a department manager and not a chatroom of agents. It is:

```text
Main Agent / Runtime Controller
  observes versioned material graph
  selects next frontier material or transform
  compiles a bounded TaskPacket + MaterialBundle
  dispatches one script or subagent
  collects candidate artifact
  validates candidate
  commits new material version or creates backflow
  propagates stale status locally
  reports state to human owner
```

The durable object is not the stage. The durable object is the material version:

```text
Material@vN
TransformTask
ValidatorReport
ReviewFinding
BackflowTask
ReviewClosure
DeliveryGate
```

The stage IDs `S00-S16` remain useful as transform families and viewer labels, but runtime completion must be proven by material state transitions.

## 2. Macro phases

### Phase 0 — Baseline freeze: stage/material taxonomy

Status: complete enough for now.

Accepted baseline:

- `S00-S16` stage taxonomy;
- `S09A -> S09B -> S10` writing ingress;
- `S06 -> S08` and `S01/S04 -> S11` figure evidence flow;
- `S13 -> S14 -> S15` review/backflow/repair split;
- `S12/S13/S15 -> S16` delivery entry paths;
- `G01/G02` as inert sidecars.

Do not spend more time optimizing the stage graph until executable material graph problems are solved.

Exit condition:

- viewer marks baseline as confirmed;
- strict review document exists;
- no current claim that runtime is live.

### Phase 1 — Executable material graph core

Goal: make the graph more than a diagram.

Deliverables:

- `schemas/ppg-material.schema.json`
- `schemas/ppg-transform-task.schema.json`
- `schemas/ppg-validator-report.schema.json`
- `scripts/ppg_store.py`
- `examples/materials/*.yaml`
- `examples/runtime/*.json`

Required behavior:

- load graph;
- resolve material by id and active version;
- list upstream/downstream;
- preserve old versions;
- represent `supersedes` explicitly;
- record candidates separately from committed material;
- reject invalid endpoint references.

Exit gate:

```bash
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map
python3 scripts/validate_graph.py examples/runtime/overclaim-loop.v1.json
```

### Phase 2 — Strong schemas and validators

Goal: turn material semantics into machine-checkable contracts.

P0 schemas:

- `ppg-review-finding.schema.json`
- `ppg-backflow-task.schema.json`
- `ppg-review-closure.schema.json`
- `ppg-delivery-gate.schema.json`
- `ppg-task-packet.schema.json`

P1 schemas:

- `ppg-owner-intent.schema.json`
- `ppg-owner-decision.schema.json`
- `ppg-evidence-inventory.schema.json`
- `ppg-claim-boundary-map.schema.json`
- `ppg-claim-evidence-visibility-map.schema.json`
- `ppg-reader-spine.schema.json`
- `ppg-terminology-register.schema.json`
- `ppg-selected-control-bundle.schema.json`
- `ppg-writing-task-packet.schema.json`
- `ppg-section-draft.schema.json`
- `ppg-figure-contract.schema.json`
- `ppg-panel-evidence-map.schema.json`
- `ppg-figure-export-bundle.schema.json`

Validator upgrades:

- artifact existence;
- payload schema validation;
- `supersedes` chain invariants;
- stale propagation invariants;
- review/backflow invariants;
- delivery gate conditions;
- sidecar pollution lint.

Exit gate examples:

```bash
python3 scripts/validate_material.py examples/materials/claim_boundary_map.v1.yaml
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v1.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/overclaim_repair.v1.yaml
python3 scripts/validate_delivery_gate.py examples/delivery/review_closure.pass.yaml
```

### Phase 3 — Stale propagation and local backflow

Goal: prove local reverse propagation.

Required executable pattern:

```text
ReviewFinding@v1
-> BackflowTask@v1
-> ClaimBoundaryMap@v2
--supersedes--> ClaimBoundaryMap@v1
-> WritingTaskPacket[intro]@v2
-> SectionDraft[intro]@v2
```

And scoped stale behavior:

```text
ClaimBoundaryMap@v1 -> stale
WritingTaskPacket[intro]@v1 -> stale
SectionDraft[intro]@v1 -> stale
UnrelatedSectionDraft@v1 -> remains valid
```

Deliverables:

- `scripts/propagate_stale.py`
- `scripts/compile_backflow.py`
- `examples/backflow/claim-overreach-before.json`
- `examples/backflow/claim-overreach-after.json`
- failure type mapping table.

MVP failure mappings:

| failure type | primary target | likely downstream |
| --- | --- | --- |
| `claim_overreach` | `ClaimBoundaryMap` / `ClaimEvidenceVisibilityMap` | writing packet, section draft |
| `evidence_missing` | `ClaimEvidenceMatrix` / `EvidenceInventory` | claim boundary, figure contract, draft |
| `terminology_leak` | `TerminologyRegister` | selected controls, writing packet, draft |
| `reader_question_gap` | `ReaderSpine` / `ReviewerQuestionMap` | section plan, writing packet |
| `rhetorical_function_gap` | `MainTextConstructionMatrix` / `RhetoricalMoveMatrix` | writing packet, draft |
| `figure_data_trace` | `PanelEvidenceMap` / `SourceDataLocator` | figure bundle, caption, integration |
| `export_render_failure` | `DeliveryManifest` / `ExportSurface` | delivery gate |
| `semantic_reset_required` | `OwnerDecisionRecord` | owner-gated upstream material |

Exit gate:

```bash
python3 scripts/compile_backflow.py examples/findings/overclaim.yaml \
  --graph examples/runtime/overclaim-loop.v1.json \
  --out /tmp/backflow.yaml
python3 scripts/propagate_stale.py examples/runtime/overclaim-loop.v1.json \
  --source claim_boundary_map.v2 \
  --out /tmp/overclaim-stale.json
python3 scripts/validate_backflow.py /tmp/backflow.yaml
```

### Phase 4 — Task packet compiler and subagent boundary

Goal: make subagent work bounded and non-self-certifying.

Deliverables:

- `scripts/compile_task_packet.py`
- `schemas/ppg-writing-task-packet.schema.json`
- `examples/packets/intro_writing_packet.v1.yaml`
- `examples/packets/claim_repair_packet.v2.yaml`

Task packet minimal schema:

```yaml
packet_id:
schema_version:
stage_family: S09B
agent_type:
target_material_id:
target_section_or_unit:
mission:
input_materials:
  required: []
  optional: []
mandatory_controls:
  claim_boundary:
  reader_spine:
  terminology:
  surface_rules:
evidence_anchors:
forbidden_routes:
allowed_read_paths:
allowed_write_paths:
allowed_tools:
output_artifact_path:
validators:
return_format:
single_writer_lock:
timeout_or_budget:
failure_report_format:
completion_forbidden: true
no_recursive_orchestration: true
owner_gate_required: false
```

Exit gate:

```bash
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/intro_packet.yaml
python3 scripts/validate_packet.py /tmp/intro_packet.yaml
```

### Phase 5 — Mock vertical slice before real subagents

Goal: prove graph semantics without paying agent orchestration cost.

Vertical slice:

```text
OwnerIntent@v1
-> EvidenceInventory@v1
-> ClaimBoundaryMap@v1
-> ClaimEvidenceVisibilityMap@v1
-> ReaderSpine@v1
-> TerminologyRegister@v1
-> SelectedControlBundle@v1
-> WritingTaskPacket[intro]@v1
-> SectionDraft[intro]@v1
-> ReviewFinding(overclaim)@v1
-> BackflowTask@v1
-> ClaimBoundaryMap@v2 --supersedes--> ClaimBoundaryMap@v1
-> WritingTaskPacket[intro]@v2
-> SectionDraft[intro]@v2
-> ReviewClosure@v1
-> DeliveryGate@pass
```

Use fixtures or mock scripts for writer/reviewer first:

- mock writer reads packet and writes a deterministic draft artifact;
- mock reviewer emits a known `claim_overreach` finding;
- backflow compiler maps finding to `ClaimBoundaryMap`;
- stale propagation marks only affected materials;
- revised packet/draft are produced;
- review closure passes;
- delivery gate passes.

Exit gate:

```bash
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
```

### Phase 6 — Real subagent pilots

Goal: introduce real native subagents only after packet and validators are hard.

Pilot order:

1. `verifier` or `critic` for ReviewFinding generation;
2. `planner` for BackflowTask classification if script confidence is low;
3. `writer` for SectionDraft generation from a strict packet;
4. `executor` only for artifact generation or scripted transformation;
5. `designer` only for figure/caption/formal artifacts after figure schemas exist.

Rules:

- no subagent receives raw whole-repo context by default;
- no subagent writes outside `allowed_write_paths`;
- no subagent marks graph completion;
- no recursive orchestration;
- every returned artifact is candidate until validators pass;
- repeated failures route back to task packet or material schema, not to broad rewriting.

Exit gate:

- one real section draft loop passes the same fixture suite as the mock loop;
- artifacts are committed as material versions;
- stale state clears only after validator-backed commit.

### Phase 7 — Plugin manager surface

Goal: wrap the proven runtime as a Plugin OS style manager.

Public model:

```text
one public manager entry
hidden internal runtime/workstream modules
state-first boot
manager-owned routing
validator-backed completion
owner-gated semantic decisions
```

Likely future layout:

```text
yxj-paper-ppg-runtime-plugin/
  .codex-plugin/plugin.json       # skills: ./entry-skills/
  entry-skills/yxj-paper-ppg-runtime/SKILL.md
  skills/graph-core/
  skills/task-packet/
  skills/backflow/
  skills/review/
  skills/delivery/
  schemas/
  scripts/
  fixtures/
```

Do not make every internal lane a public `$` skill. The user wakes the manager; the manager chooses internal routes.

## 3. Main agent principles

### P1. Main agent owns state, not prose

The main agent should always ask:

```text
What material version changed?
What validator proved it?
What downstream materials became stale?
What active pointer moved?
What owner gate remains open?
```

It should avoid broad claims such as “the writing is done” unless the material graph proves closure.

### P2. Dispatch is never completion

Completion lifecycle:

```text
planned -> dispatched -> executed -> collected -> validated -> ingested -> state_transitioned -> reviewed/handoff
```

Invalid completion signals:

- subagent ACK;
- task started;
- file generated without validation;
- validator invoked without result ingestion;
- PUA telemetry;
- review requested without closure.

### P3. Scripts before subagents for deterministic work

Use scripts for:

- schema validation;
- graph consistency;
- artifact existence;
- stale propagation;
- sidecar pollution lint;
- rendered/export checks;
- hash/manifest generation.

Use subagents for:

- semantic review;
- claim boundary analysis;
- reader spine and rhetorical design;
- section drafting from bounded packet;
- figure/caption qualitative judgment;
- ambiguous backflow classification.

### P4. Frontier queue is material-state driven

Default priority:

```text
owner-gated semantic decision
> invalid or stale upstream control material
> validator failure blocking commit
> review finding without backflow task
> missing task packet for active target
> candidate artifact awaiting validation
> export/delivery gate blocker
> optional improvement
```

### P5. Local repair beats global rewrite

A review finding must map to the nearest responsible material. Whole-paper rewrite is allowed only when the finding explicitly proves root spine/owner intent failure.

### P6. Owner decisions are material objects

When a change affects motivation, venue, contribution strength, source-use policy, or core claim semantics, create or require:

```text
OwnerDecisionQueue -> OwnerDecisionRecord
```

Do not hide owner decisions inside prose summaries.

### P7. Sidecars cannot pollute paper cognition

`G01/G02` materials may constrain permissions or derive post-paper outputs, but they must not enter writing packets unless explicitly authorized and tagged.

## 4. Subagent task package arrangement

### General packet envelope

All subagent packets should follow this structure:

```yaml
task_packet:
  packet_id:
  schema_version:
  task_kind:
  agent_type:
  pressure_level: L0
  mission:
  target_material:
  input_materials:
  local_context:
  mandatory_controls:
  evidence_anchors:
  forbidden_routes:
  allowed_actions:
  allowed_read_paths:
  allowed_write_paths:
  output_contract:
  validators:
  ingestion_target:
  stop_condition:
  failure_report_format:
  completion_forbidden: true
  no_recursive_orchestration: true
```

### Worker boot clause

Every bounded LLM subagent task should include:

```text
你只执行本任务包，不接管全局流程。
你可以返回 candidate artifact 和 evidence，但不能宣布 graph node complete。
不能递归调度其他 agent。
不能修改 allowed_write_paths 以外的文件。
如果材料不足，输出 MissingMaterialReport，而不是猜。
完成必须给出 changed/created artifact、validator expectation、remaining risk。
```

For repeated failures, use internal PUA telemetry for LLM agents only:

```text
[PUA-DIAGNOSIS] 问题是 ___；证据是 ___；下一步动作是 ___。
```

At L2+:

```text
[PUA-REPORT]
failure_count:
failure_mode:
attempts:
excluded:
next_hypothesis:
manager_action:
```

PUA telemetry is never completion evidence.

## 5. Specific subagent packet families

### 5.1 Claim boundary analyst packet

Purpose: create or revise claim boundaries.

Agent type: `planner`, `verifier`, or `critic` depending on task.

Inputs:

- `EvidenceInventory`
- `ClaimEvidenceMatrix`
- `ReviewFinding` when repair-driven
- owner-approved contribution scope

Outputs:

- `ClaimBoundaryMap@vN`
- `ClaimEvidenceVisibilityMap@vN`
- risk notes

Validators:

- every claim has evidence anchor;
- claim strength not above evidence strength;
- unsupported claims are hidden or downgraded;
- if repair, new version supersedes old.

### 5.2 Reader spine / section design packet

Purpose: decide what the reader must learn in a section.

Agent type: `planner` or `writer` for design only.

Inputs:

- `OwnerIntent`
- `ClaimBoundaryMap`
- venue/template profile
- `ReviewerQuestionMap`

Outputs:

- `ReaderSpine`
- `SectionMovePlan`
- `MainTextConstructionMatrix`

Validators:

- each section answers a reader question;
- no section promise exceeds admitted claims;
- downstream writing unit is addressable.

### 5.3 Control-material selection packet

Purpose: implement S09A.

Agent type: `planner` or main-agent script.

Inputs:

- `ClaimBoundaryMap`
- `ReaderSpine`
- `TerminologyRegister`
- `RhetoricalMoveMatrix`
- target manuscript unit

Outputs:

- `SelectedControlBundle`
- `ControlPriorityMap`
- `MissingControlReport` if blocked

Validators:

- controls are sufficient but not all-context dump;
- priority order resolves conflicts;
- every mandatory control links to a source material.

### 5.4 Writing task packet assembly

Purpose: implement S09B.

Agent type: main-agent script first, `planner` only for ambiguous cases.

Inputs:

- `SelectedControlBundle`
- evidence anchors
- target unit
- validator refs

Outputs:

- `WritingTaskPacket`

Validators:

- required Codex fields present;
- allowed paths/tools present;
- `completion_forbidden: true`;
- `no_recursive_orchestration: true`;
- output path declared.

### 5.5 Section writing packet

Purpose: create candidate text only.

Agent type: `writer`.

Inputs:

- `WritingTaskPacket`
- cited evidence snippets or locators
- local section context

Outputs:

- `SectionDraft@candidate`
- `DraftEvidenceTrace`
- `KnownLimitations`

Validators:

- no unsupported claim;
- no raw internal IDs if forbidden;
- terminology follows register;
- output matches target section only.

### 5.6 Review finding packet

Purpose: produce structured findings, not rewrites.

Agent type: `critic` or `verifier`.

Inputs:

- `SectionDraft` or integrated manuscript;
- `ClaimBoundaryMap`;
- evidence anchors;
- figure/export artifacts when relevant.

Outputs:

- `ReviewFinding[]`
- optional `ReviewClosure` if no open P0/P1 issues

Validators:

- every finding has severity;
- every finding has primary target candidate;
- every finding has evidence or location;
- no direct uncontrolled rewrite.

### 5.7 Backflow compiler packet

Purpose: implement S14.

Agent type: script first, `planner`/`verifier` for ambiguous classification.

Inputs:

- `ReviewFinding`
- graph state
- material dependency map

Outputs:

- `BackflowTask`
- `AffectedDownstreamSet`
- owner gate status

Validators:

- one primary target per finding;
- target material exists;
- owner gate is set when semantic scope changes;
- downstream impact is explicit.

### 5.8 Repair execution packet

Purpose: implement S15.

Agent type: `writer`, `executor`, or `verifier` depending on repair kind.

Inputs:

- `BackflowTask`
- target material version
- stale downstream set

Outputs:

- revised material version;
- regenerated task packet if needed;
- revised candidate text/figure if needed;
- validator report.

Validators:

- new version supersedes old;
- unrelated materials unchanged;
- original finding resolved;
- new high-severity finding not introduced.

### 5.9 Delivery gate packet

Purpose: implement S16.

Agent type: `verifier` or deterministic script.

Inputs:

- `CleanFinalCandidate` or `RepairCompletePackage`
- `ReviewClosure`
- repository state
- export artifacts

Outputs:

- `DeliveryGate`
- `ExportManifest`
- `RepositoryHygieneReport`

Validators:

- open P0/P1 findings are zero or owner-deferred;
- artifact paths exist;
- export can open/render;
- dirty worktree is classified.

## 6. Implementation reference map

| Runtime need | Current reference | Next concrete artifact |
| --- | --- | --- |
| Stage taxonomy | `docs/SUBAGENT_STAGE_BLUEPRINT.md` | Keep as transform map |
| Material topology | `docs/TOPOLOGY.md` | `ppg_store.py`, stronger graph examples |
| Material envelope | `docs/MATERIAL_SCHEMA.md` | `ppg-material.schema.json`, typed schemas |
| Main-agent loop | `docs/RUNTIME_PROTOCOL.md` | frontier selector, packet compiler |
| Backflow | `docs/BACKFLOW_PROTOCOL.md` | `compile_backflow.py`, stale fixture |
| Validation | `docs/VALIDATION_AND_TESTING.md` | validator suite MVP |
| Viewer | `docs/runtime-viewer/` | add material graph mode later |
| Strict review | `docs/RUNTIME_STRICT_REVIEW_ROUND2_2026-06-29.md` | P0 gating backlog |
| Plugin OS pattern | `yxj-plugin-incubator` references | single public manager entry later |

## 6.5 Phase-scoped Autopilot execution protocol

The detailed ideal-state eight-phase roadmap and the recommended phase-scoped `$autopilot` / `$ralplan -> $ultragoal` cycle are recorded in [`PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md`](PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md).

Key rule:

```text
Do not run one project-wide Autopilot over all phases.
Use one phase-scoped Autopilot or Ralplan/Ultragoal cycle per promoted phase.
Each phase needs its own plan, Ultragoal ledger evidence, validation output, review gate, and promotion record.
```

## 7. Concrete execution order for next sessions

### Session 1: graph core and schemas

1. Add `ppg-material.schema.json`.
2. Add `ppg-transform-task.schema.json`.
3. Add `ppg-validator-report.schema.json`.
4. Implement `ppg_store.py inspect`.
5. Create `examples/runtime/overclaim-loop.v1.json`.
6. Validate old and new examples.

### Session 2: negative validation and supersedes invariant

1. Add invalid fixture: repair without v2/supersedes.
2. Make validator fail it.
3. Add valid fixture with `ClaimBoundaryMap@v2 --supersedes--> @v1`.
4. Add active version resolution.

### Session 3: stale propagation

1. Implement `propagate_stale.py`.
2. Fixture: overclaim stales only intro packet/draft.
3. Add unrelated-section preservation test.

### Session 4: backflow compiler

1. Add `ReviewFinding` schema.
2. Add `BackflowTask` schema.
3. Implement `compile_backflow.py` for failure type mapping.
4. Add tests for `claim_overreach`, `terminology_leak`, `figure_data_trace`.

### Session 5: task packet compiler

1. Add `SelectedControlBundle` schema.
2. Add `WritingTaskPacket` schema.
3. Implement `compile_task_packet.py`.
4. Add negative tests for missing evidence anchors, missing output path, `completion_forbidden=false`, and all-context dump.

### Session 6: closed-loop fixture

1. Add deterministic mock writer.
2. Add deterministic mock reviewer.
3. Run full overclaim loop.
4. Add `ReviewClosure` and `DeliveryGate`.

### Session 7: first real subagent pilot

1. Use strict `WritingTaskPacket`.
2. Dispatch a `writer` subagent for one section only.
3. Validate returned candidate.
4. Commit new material version only after validators pass.

## 8. Stop and escalation rules

Main agent continues autonomously when:

- editing schemas/scripts/fixtures locally;
- running validators;
- adding negative tests;
- updating viewer/docs to reflect verified state;
- using mock agents/scripts.

Main agent must ask or stop before:

- live installing plugin;
- mutating old `$yxj-paper-os`;
- publishing marketplace entries;
- external submission/upload;
- credentialed external services;
- destructive cleanup;
- paper-owner semantic decisions;
- launching `$team` for a current story without approval.

## 9. Success definition

The next milestone is not “the plugin can write a paper.”

The next milestone is:

```text
A single overclaim review finding causes a local material repair,
creates a new material version,
marks only affected downstream materials stale,
regenerates the writing packet and section draft,
passes review closure,
and reaches delivery gate without touching unrelated sections.
```

Once that is true, the project has a runnable runtime core worth wrapping as a plugin.
