# PPG Runtime Eight-Phase Autopilot Execution Plan

Date: 2026-06-29  
Scope: record the ideal eight-phase path for advancing `yxj-paper-ppg-runtime`, and decide how `$autopilot`, `$ralplan`, and `$ultragoal` should be used to drive each phase.

Non-reference baseline: do not use `$yxj-plugin-incubator`, Plugin OS v2+, hidden-department IO, seven-artifact incubation packages, or PUA-style managed-agent governance as references for this runtime. The eight phases are governed by the PPG model itself: explicit material graph, main-agent controller, validators, task packets, and local backflow.

## 0. Executive conclusion

The eight phases are suitable for OMX/Codex managed execution, but they should **not** be run as one giant monolithic `$autopilot` job.

Recommended management model:

```text
one repository-level roadmap
  -> one phase-scoped Autopilot or Ralplan/Ultragoal cycle per major phase
    -> multiple Ultragoal stories inside the phase
      -> validator-backed phase promotion
```

The useful inner loop is the user's proposed:

```text
$ralplan -> $ultragoal
```

When wrapped by strict `$autopilot`, the complete loop becomes:

```text
context snapshot
-> deep-interview / requirements gate
-> ralplan consensus gate
-> ultragoal implementation + verification ledger
-> code-review gate
-> ultraqa pass or explicit skip
-> phase promotion record
```

Therefore:

- use `$ralplan` for phase design, scope control, alternatives, test shape, and Architect -> Critic consensus;
- use `$ultragoal` for durable sequential execution, checkpoints, verification, and ledger evidence;
- use `$autopilot` when a phase contains non-trivial implementation and should continue hands-off through review/QA;
- do **not** use `$autopilot` as a substitute for the runtime being built. Autopilot manages development of the plugin; the plugin later manages paper production.

## 1. Autopilot fit decision

### 1.1 What Autopilot is good for here

Autopilot is well matched to the **development process** of this runtime because every phase can be converted into:

```text
clear phase objective
+ implementation stories
+ validation commands
+ review gates
+ phase promotion criteria
```

It is especially useful for:

- schema and validator implementation;
- executable graph store work;
- stale propagation/backflow algorithms;
- task packet compiler;
- mock closed-loop fixture;
- real subagent pilot with bounded packets;
- final plugin manager surface and frontend runtime state view.

### 1.2 Where Autopilot is too heavy

Autopilot is too heavy when the work is only:

- discussion;
- visual taxonomy refinement;
- a small docs update;
- pure strategic comparison without code or executable tests.

For these cases, use direct editing or `$ralplan` only, and record the result as a design artifact. If strict `$autopilot` is used for a docs-only phase, `ultraqa` should be explicitly skipped with a documented docs-only reason, not silently omitted.

### 1.3 Do not run all eight phases as one Codex goal

A single goal covering all eight phases would be fragile because:

- phase boundaries contain different validation regimes;
- later phases depend on evidence produced by earlier phases;
- review findings may require steering the later goal decomposition;
- context and ledger artifacts would become too large;
- failure localization would be poor.

Preferred strategy:

```text
Phase N has its own plan, goals, ledger evidence, review result, and promotion record.
Phase N+1 starts only from the promoted state of Phase N.
```

## 2. Global phase cycle contract

Each phase should use the same management envelope.

### 2.1 Phase intake

Create or reuse a context snapshot containing:

```yaml
phase_id:
phase_name:
status_before:
desired_outcome:
known_artifacts:
constraints:
non_goals:
unknowns:
likely_touchpoints:
validation_targets:
human_owner_gates:
```

### 2.2 Ralplan gate

`$ralplan` should produce a phase plan with:

```yaml
prd_or_phase_plan:
acceptance_criteria:
test_spec:
architecture_invariants:
implementation_options:
chosen_option:
risks:
subagent_roles_if_needed:
verification_commands:
stop_conditions:
```

Execution is allowed only after durable consensus evidence:

```text
Architect APPROVE -> Critic APPROVE
```

Planning files alone are not enough.

### 2.3 Ultragoal execution

`$ultragoal` should split the phase into story-sized goals. Each story must have:

```yaml
goal_id:
objective:
allowed_files_or_dirs:
expected_artifacts:
validation:
completion_evidence:
rollback_or_recovery:
```

Ultragoal completion evidence must include real artifacts and validation output, not a statement that a subagent was dispatched.

### 2.4 Review and QA

After Ultragoal execution:

- run code review for non-doc diffs;
- run UI/CLI/runtime QA when behavior changed;
- explicitly skip QA only for docs-only or trivially non-runtime changes;
- return to `$ralplan` if review/QA proves the plan was wrong;
- use implementation rework only when the plan is sound but the implementation is flawed.

### 2.5 Phase promotion record

A phase is promoted only when a durable record answers:

```text
What changed?
Which material/runtime invariant is now true?
Which validator proved it?
Which tests passed?
Which review gates passed or were explicitly skipped?
What remains out of scope?
What is the next phase's allowed starting state?
```

## 3. Eight-phase roadmap with Autopilot handoff shape

### Phase 1 — 固化论文生产的抽象模型

Purpose: freeze the human-facing ontology of paper production: materials, stages, flows, review backflow, and unused sidecars.

Current status: complete / promoted as v0.2 baseline. See [`phase-promotions/PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md`](phase-promotions/PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md).

Consumes:

- existing yxj-paper-os process inventory;
- stage taxonomy S00-S16;
- runtime viewer feedback;
- Architect/Critic strict review notes.

Produces:

- confirmed transform taxonomy;
- per-stage input/output/meaning table;
- visual topology contract;
- explicit statement that this is not yet a runnable runtime.

Ralplan focus:

- decide whether any stage is still missing or redundant;
- verify that S09A/S09B split, figure branch, and review backflow are conceptually stable;
- define which disagreements are deferred to executable runtime rather than more diagram changes.

Ultragoal stories:

1. update docs and viewer labels to reflect confirmed baseline;
2. add crosswalk from old yxj-paper-os analysis dimensions to new stage/material taxonomy;
3. add a baseline promotion record.

Validation:

```bash
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
```

Phase promotion gate:

```text
v0.2 stage/material taxonomy is frozen for implementation;
no document claims the runtime is executable yet.
```

Autopilot recommendation: mostly unnecessary now. Use direct docs/viewer updates unless another major topology dispute appears.

---

### Phase 2 — 把图变成可执行的数据结构

Purpose: move from a diagram to a runtime-readable versioned material graph.

Consumes:

- Phase 1 taxonomy;
- current minimal graph schema;
- strict review requirement for `Material@vN`, `supersedes`, stale state, and validator reports.

Produces:

- first-class material envelope;
- active-version resolution;
- transform task representation;
- validator report representation;
- example runtime graph with versions.

Ralplan focus:

- choose graph storage shape for MVP fixtures;
- decide JSON vs YAML boundary for materials and graph state;
- define active pointer and version/supersedes invariants;
- define negative fixtures that must fail.

Ultragoal stories:

1. add `ppg-material.schema.json`;
2. add `ppg-transform-task.schema.json`;
3. add `ppg-validator-report.schema.json`;
4. implement `scripts/ppg_store.py inspect`;
5. create `examples/runtime/overclaim-loop.v1.json`;
6. add invalid fixture coverage for missing endpoints and invalid active versions.

Validation:

```bash
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map
python3 scripts/validate_graph.py examples/runtime/overclaim-loop.v1.json
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
```

Phase promotion gate:

```text
The repo can load a runtime graph, resolve a material's active version,
show upstream/downstream dependencies, and reject structurally invalid references.
```

Autopilot result: promoted after phase-scoped Autopilot/Ralplan consensus and implementation validation. See [`phase-promotions/PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md`](phase-promotions/PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md).

---

### Phase 3 — 建立主 agent 的控制器逻辑

Purpose: define and implement the runtime controller rules that let the main agent manage state instead of merely writing prose.

Consumes:

- executable material graph core;
- material statuses and validator reports;
- main-agent principles from macro plan.

Produces:

- frontier selection policy;
- candidate -> validate -> commit protocol;
- event log / state transition record;
- owner decision queue/record contract;
- controller report format.

Ralplan focus:

- choose the minimal controller API for MVP;
- decide whether controller behavior is script-first, doc-first, or mixed;
- specify priority order for frontier tasks;
- distinguish owner-gated semantic decisions from autonomous mechanical work.

Ultragoal stories:

1. implement a frontier selector over example runtime graph state;
2. implement candidate material commit rules;
3. implement state transition/event log output;
4. add `OwnerDecisionQueue` / `OwnerDecisionRecord` schemas or placeholders;
5. add controller report fixture.

Validation:

```bash
python3 scripts/ppg_store.py frontier examples/runtime/overclaim-loop.v1.json
python3 scripts/ppg_store.py report examples/runtime/overclaim-loop.v1.json
python3 scripts/validate_graph.py examples/runtime/overclaim-loop.v1.json
```

Phase promotion gate:

```text
Given a graph state, the main-agent controller can say what is next,
why it is next, what is blocked by the human owner, and what cannot be called complete.
```

Autopilot recommendation: yes, but keep stories small. This phase defines the management semantics; require Architect/Critic review.

---

### Phase 4 — 设计各类物料 schema 与验证器

Purpose: make the important paper-production materials machine-checkable.

Consumes:

- material graph core;
- controller protocol;
- stage/material taxonomy;
- strict review P0/P1 schema list.

Produces:

P0 schemas:

- `ReviewFinding`;
- `BackflowTask`;
- `ReviewClosure`;
- `DeliveryGate`;
- `TaskPacket`.

P1 schemas:

- owner intent/decision;
- evidence inventory;
- claim boundary map;
- claim evidence visibility map;
- reader spine;
- terminology register;
- selected control bundle;
- writing task packet;
- section draft;
- figure contract and panel evidence map.

Ralplan focus:

- pick P0 schema order;
- decide strict vs permissive fields;
- define validator failure codes;
- define sidecar pollution lint.

Ultragoal stories:

1. implement P0 schemas;
2. implement generic payload validation;
3. add P0 valid/invalid fixtures;
4. implement enough P1 schemas for the vertical slice;
5. add schema documentation and example material files.

Validation:

```bash
python3 scripts/validate_material.py examples/materials/claim_boundary_map.v1.yaml
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v1.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/overclaim_repair.v1.yaml
python3 scripts/validate_delivery_gate.py examples/delivery/review_closure.pass.yaml
```

Phase promotion gate:

```text
Critical runtime materials can fail validation for semantic reasons,
not just missing files or malformed JSON/YAML.
```

Autopilot recommendation: yes. This phase benefits strongly from `$ralplan` test-spec discipline and Ultragoal checkpoints.

---

### Phase 5 — 建立局部反向传播机制

Purpose: prove that review does not cause whole-paper rewrite; it produces local backflow and stale propagation.

Consumes:

- versioned material graph;
- ReviewFinding and BackflowTask schemas;
- material dependency map;
- controller event/state transition rules.

Produces:

- `compile_backflow.py`;
- `propagate_stale.py`;
- failure-type mapping table;
- before/after backflow fixtures;
- affected downstream set calculation.

Ralplan focus:

- define local backflow semantics;
- decide nearest-responsible-material mapping;
- define when owner gate is required;
- define stale propagation invariants;
- define unrelated-material preservation tests.

Ultragoal stories:

1. implement `ReviewFinding -> BackflowTask` mapping for `claim_overreach`;
2. implement stale propagation from a revised material version;
3. preserve unrelated sections as valid;
4. add negative fixtures for overbroad stale propagation;
5. add logs/reports explaining why each downstream node is stale or still valid.

Validation:

```bash
python3 scripts/compile_backflow.py examples/findings/overclaim.yaml \
  --graph examples/runtime/overclaim-loop.v1.json \
  --out /tmp/backflow.yaml
python3 scripts/propagate_stale.py examples/runtime/overclaim-loop.v1.json \
  --source claim_boundary_map.v2 \
  --out /tmp/overclaim-stale.json
python3 scripts/validate_backflow.py /tmp/backflow.yaml
```

Phase promotion gate:

```text
A ReviewFinding can repair the nearest upstream material,
create a new version, mark only affected downstream materials stale,
and leave unrelated sections untouched.
```

Autopilot recommendation: yes, full phase-scoped Autopilot is appropriate. This is a core proof phase.

---

### Phase 6 — 建立 subagent 任务包机制

Purpose: make subagent work bounded, auditable, and non-self-certifying.

Consumes:

- controller frontier decision;
- selected control materials;
- material graph and stale state;
- task packet schema;
- allowed read/write/tool policies.

Produces:

- task packet compiler;
- strict packet examples;
- worker boot clause;
- MissingMaterialReport contract;
- candidate artifact return contract.

Ralplan focus:

- define mandatory task-packet fields;
- decide large material bundle policy;
- define no-recursive-orchestration boundary;
- define validator-backed ingestion;
- decide when script vs subagent is allowed.

Ultragoal stories:

1. implement `compile_task_packet.py`;
2. add `WritingTaskPacket` example for intro;
3. add repair packet example for claim boundary repair;
4. validate `completion_forbidden: true` and `no_recursive_orchestration: true`;
5. add negative tests for missing allowed paths, output path, and evidence anchors.

Validation:

```bash
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/intro_packet.yaml
python3 scripts/validate_packet.py /tmp/intro_packet.yaml
```

Phase promotion gate:

```text
A subagent can receive a strict packet and return a candidate artifact,
but cannot mark graph completion, dispatch other agents, or write outside the allowed surface.
```

Autopilot recommendation: yes. Use subagents only for review of the packet design at first; real worker pilots wait until Phase 7.

---

### Phase 7 — 做一个最小完整闭环 vertical slice

Purpose: prove the runtime with a deterministic overclaim repair loop before using real writing agents broadly.

Consumes:

- graph core;
- schemas and validators;
- controller logic;
- local backflow;
- task packet compiler;
- mock writer/reviewer fixtures.

Produces:

- deterministic fixture suite;
- mock writer;
- mock reviewer;
- overclaim before/after graph states;
- ReviewClosure;
- DeliveryGate;
- phase evidence package.

Ralplan focus:

- choose one vertical slice target, preferably `intro`;
- define exact expected stale set;
- define closure criteria;
- define delivery gate conditions;
- decide what remains fake/mock vs real.

Ultragoal stories:

1. build deterministic mock writer;
2. build deterministic mock reviewer that emits `claim_overreach`;
3. run backflow compiler and stale propagation;
4. regenerate intro writing packet and draft;
5. produce ReviewClosure and DeliveryGate;
6. add one command that runs the whole fixture suite.

Validation:

```bash
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
```

Phase promotion gate:

```text
A single overclaim finding causes a local repair, new material version,
scoped stale propagation, regenerated writing packet/draft, review closure,
and delivery gate pass without touching unrelated sections.
```

Autopilot recommendation: yes, and this should be treated as the first major release candidate of the runtime core.

---

### Phase 8 — 扩展成 runtime adapter 与前端 state surface

Purpose: expose the proven PPG runtime through a thin operator-facing adapter and make material-graph state visible to the human owner. This phase must not import Plugin OS / incubator concepts; it only wraps the already-proven runtime controller.

Consumes:

- proven vertical slice;
- runtime controller protocol;
- material graph schemas and validators;
- runtime viewer product constraints.

Produces:

- one operator-facing runtime entry;
- runtime modules organized by graph operation, not departments;
- frontend material graph mode;
- active frontier view;
- stale/backflow visualization;
- OwnerDecisionQueue view;
- DeliveryGate view;
- plugin validation package.

Ralplan focus:

- decide runtime adapter surface and non-live boundaries;
- decide module boundaries around graph operations;
- decide controller report format;
- decide frontend state model;
- decide install/publish gates.

Ultragoal stories:

1. scaffold thin runtime entry and graph-operation modules;
2. wire runtime boot to graph state inspection;
3. add frontend runtime state mode beyond stage taxonomy;
4. add owner decision and stale/backflow panels;
5. add plugin validation and docs;
6. prepare but do not publish live install/marketplace entries without explicit approval.

Validation:

```bash
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
```

Phase promotion gate:

```text
The plugin exposes one public manager surface,
hides internal runtime lanes,
can inspect and report graph state,
and shows the human owner where active frontier, stale materials,
review findings, backflow tasks, owner decisions, and delivery gates are.
```

Autopilot recommendation: yes, but with explicit gates: no live install, no marketplace publishing, no mutation of old `$yxj-paper-os`, and no `$team` launch without approval.

## 4. Recommended cadence

### 4.1 Development order

Use this phase order:

```text
Phase 1: promoted; keep frozen.
Phase 2: promoted; executable material graph core.
Phase 3: controller/frontier semantics.
Phase 4: schemas and validators.
Phase 5: local backflow/stale propagation.
Phase 6: task packet compiler.
Phase 7: deterministic vertical slice.
Phase 8: plugin/frontend runtime surface.
```

### 4.2 Execution mode by phase

| Phase | Recommended mode | Why |
| --- | --- | --- |
| 1. Abstract model freeze | direct or `$ralplan` only | mostly docs/viewer baseline already done |
| 2. Executable data structure | `$autopilot` or `$ralplan -> $ultragoal` | code + schemas + validation |
| 3. Main-agent controller | `$autopilot` | architecture semantics must be reviewed |
| 4. Schemas/validators | `$autopilot` | many failure cases and test specs |
| 5. Local backpropagation | `$autopilot` | core runtime proof |
| 6. Subagent packets | `$autopilot` | safety boundaries and validators |
| 7. Vertical slice | `$autopilot` | end-to-end proof with QA |
| 8. Plugin/frontend | `$autopilot` with explicit gates | product/runtime surface, plugin boundaries |

### 4.3 One phase should not start until the previous phase leaves evidence

Minimum promotion evidence:

```yaml
phase_id:
status: promoted
changed_artifacts:
validation_commands:
validation_result:
review_gate:
ultraqa_gate:
known_gaps:
next_phase_start_state:
```

This prevents the old failure mode where a department/subagent claims progress without validated state transition.

## 5. Autopilot prompt template for a phase

Use a bounded activation prompt rather than a broad request.

```text
$autopilot Phase <N> of yxj-paper-ppg-runtime.

Objective:
<one phase objective>

Known baseline:
<links to docs and accepted previous phase promotion record>

Allowed scope:
<files/dirs to edit>

Non-goals:
- do not mutate old $yxj-paper-os
- do not live-install plugin
- do not publish marketplace entries
- do not launch $team unless explicitly approved
- do not weaken validators to pass fixtures

Required ralplan outputs:
- phase plan
- architecture invariants
- acceptance criteria
- validation commands
- Architect APPROVE then Critic APPROVE

Required ultragoal outputs:
- story ledger
- changed artifacts
- fresh validation evidence
- phase promotion record

Stop condition:
<phase promotion gate>
```

For a lighter non-Autopilot cycle, use:

```text
$ralplan Phase <N> ...
# after consensus
$ultragoal from the approved Phase <N> plan
```

## 6. Human owner gates

Even with Autopilot, the main agent must stop or ask before:

- changing the core philosophy of the runtime;
- treating a stage taxonomy change as user-approved when it changes paper production semantics;
- mutating old `$yxj-paper-os`;
- live installing or publishing a plugin;
- launching `$team` for a phase;
- using credentialed external services;
- making destructive cleanup;
- making owner-level paper semantic decisions in a real manuscript.

Everything else that is local, reversible, testable, and inside the phase scope should continue autonomously.

## 7. Final decision

Yes: the eight stages can be advanced by repeated `Ralplan -> Ultragoal` cycles, and strict `$autopilot` can supervise those cycles for implementation-heavy phases.

The best future process is:

```text
Phase-scoped Autopilot, not project-wide Autopilot.
Ralplan creates the reviewed phase contract.
Ultragoal executes story-sized goals with ledger checkpoints.
Validators and review gates promote the phase.
The next phase starts only from promoted evidence.
```
