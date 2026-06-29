# Implementation Flow — PPG Runtime Core First

This document defines the concrete推进流程 for building the Paper Production Graph Runtime before considering OMX Pipeline as an outer shell.

## Strategy

Do not integrate OMX Pipeline in the early phase. Build the inner PPG core first:

```text
schema -> graph store -> validators -> stale propagation -> task packets -> local backflow -> read-only visualization -> single-section pilot
```

OMX Pipeline can later wrap these phases after the graph runtime is proven.


## Build-order decision

The implementation order is not pure top-down framework design and not pure bottom-up material design. Follow ADR-0002:

```text
thin framework skeleton -> one concrete vertical slice -> generalize material families
```

The first concrete slice is:

```text
OwnerIntent -> PaperControlSpine -> ClaimBoundaryMap -> ReviewerQuestionMap -> TerminologyRegister -> WritingTaskPacket -> SectionDraft -> ReviewFinding -> BackflowTask -> stale propagation / revised packet
```

This keeps the runtime architecture stable while forcing every abstraction to prove itself on a real paper-production path.

## Workstream order

### F0 — Repository spine and design freeze

Status: complete.

Artifacts:

- `README.md`
- `AGENTS.md`
- `docs/PLAN.md`
- `docs/TOPOLOGY.md`
- `docs/VISUALIZATION_CONTRACT.md`
- `docs/MATERIAL_SCHEMA.md`
- `docs/RUNTIME_PROTOCOL.md`
- `docs/BACKFLOW_PROTOCOL.md`
- `docs/VALIDATION_AND_TESTING.md`
- `docs/RELATED_FRAMEWORKS.md`
- `schemas/ppg-graph.schema.json`
- `examples/minimal-paper-production-graph.json`
- `scripts/validate_graph.py`

Exit gate:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

### F1 — Graph core schema and state store

Goal: make the graph more than documentation.

Deliverables:

- `schemas/ppg-material.schema.json` — shared material envelope;
- `schemas/ppg-task-packet.schema.json` — task packet envelope;
- `schemas/ppg-review-finding.schema.json` — review finding envelope;
- `schemas/ppg-backflow-task.schema.json` — backflow task envelope;
- `scripts/ppg_store.py` — load/save graph, query nodes, query dependencies;
- `examples/materials/*.yaml` — minimal material fixtures;
- `examples/packets/*.yaml` — minimal task packet fixture.

Required behavior:

- load a graph;
- resolve node by id;
- list upstream/downstream nodes;
- detect missing endpoints;
- detect stale nodes;
- preserve versioned nodes.

Exit gate:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
python3 scripts/ppg_store.py inspect examples/minimal-paper-production-graph.json --node intro_gap_draft_v1
```

### F2 — Stale propagation engine

Goal: implement local dependency invalidation.

Deliverables:

- `scripts/propagate_stale.py`;
- `examples/backflow/claim-overreach-before.json`;
- `examples/backflow/claim-overreach-after.json`;
- test fixture showing one upstream change marks only affected downstream nodes stale.

Required behavior:

- consume a graph and a changed/invalidated node id;
- traverse hard `consumes` / `constrains` edges;
- mark affected downstream nodes `stale`;
- preserve unrelated nodes;
- record `stale_reason`.

Exit gate:

```bash
python3 scripts/propagate_stale.py examples/backflow/claim-overreach-before.json \
  --source claim_boundary_map_v1 \
  --reason "overclaim finding" \
  --out /tmp/ppg-after.json
python3 scripts/validate_graph.py /tmp/ppg-after.json
```

### F3 — Backflow compiler

Goal: convert review findings into targeted repair tasks.

Deliverables:

- `scripts/compile_backflow.py`;
- `examples/findings/overclaim.yaml`;
- `examples/backflow_tasks/repair_claim_visibility.yaml`;
- failure-type-to-target mapping table.

Failure mapping MVP:

| failure_type | target material |
| --- | --- |
| `surface_expression` | `SectionDraft` |
| `terminology_leak` | `TerminologyRegister` |
| `reader_question_gap` | `ReviewerQuestionMap` / `MainTextConstructionMatrix` |
| `rhetorical_function_gap` | `MainTextConstructionMatrix` / `RhetoricalMoveMatrix` |
| `claim_overreach` | `ClaimEvidenceVisibilityMap` / `ClaimBoundaryMap` |
| `evidence_missing` | `ClaimEvidenceMatrix` / `EvidenceInventory` |
| `spine_mismatch` | `PaperSpine` / owner-gated |

Exit gate:

```bash
python3 scripts/compile_backflow.py examples/findings/overclaim.yaml \
  --graph examples/minimal-paper-production-graph.json \
  --out /tmp/backflow.yaml
```

The output must target a specific material node and declare owner-gate status.

### F4 — Task packet compiler

Goal: make every agent/script operation explicit.

Deliverables:

- `scripts/compile_task_packet.py`;
- `examples/packets/intro_gap_packet.v1.yaml`;
- task context bundle schema;
- packet validation script.

Required packet fields:

```yaml
task_id:
mission:
input_materials:
relevant_artifacts:
forbidden_routes:
expected_output_schema:
validators:
return_format:
completion_forbidden: true
```

Exit gate:

```bash
python3 scripts/compile_task_packet.py \
  --graph examples/minimal-paper-production-graph.json \
  --target intro_gap_draft_v1 \
  --out /tmp/intro_packet.yaml
```

The packet must be small enough for a Codex subagent prompt and complete enough for bounded execution.

### F5 — Validator suite MVP

Goal: separate machine-checkable validation from semantic review.

Deliverables:

- `scripts/validate_material.py`;
- `scripts/validate_packet.py`;
- `scripts/scan_internal_terms.py`;
- `scripts/validate_backflow.py`;
- fixture cases that pass and fail intentionally.

Exit gate:

```bash
python3 scripts/validate_material.py examples/materials/claim_boundary_map.v1.yaml
python3 scripts/validate_packet.py examples/packets/intro_gap_packet.v1.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/repair_claim_visibility.yaml
```

### F6 — Read-only graph viewer MVP

Goal: prove topology can be visualized before adding orchestration complexity.

Deliverables:

- `viewer/` static app or simple generated HTML;
- graph canvas;
- status colors;
- edge type styling;
- node inspector;
- backflow trace panel.

Acceptable first implementation:

- dependency-free HTML generation from Python, or
- a small static React Flow app if dependencies are explicitly accepted later.

Exit gate:

```bash
python3 scripts/render_graph_html.py examples/minimal-paper-production-graph.json --out /tmp/ppg.html
```

Open `/tmp/ppg.html` and verify that nodes, edges, statuses, and selected-node details are visible.

### F7 — Mock paper closed loop

Goal: run one complete local loop without real paper complexity.

Scenario:

```text
intent -> evidence inventory -> claim boundary -> reviewer questions -> writing packet -> draft candidate -> review finding -> backflow -> stale propagation -> revised packet
```

Deliverables:

- `examples/mock-paper/graph.initial.json`;
- `examples/mock-paper/materials/`;
- `examples/mock-paper/findings/`;
- `examples/mock-paper/expected/`;
- `scripts/run_mock_loop.py`.

Exit gate:

```bash
python3 scripts/run_mock_loop.py examples/mock-paper/graph.initial.json --out /tmp/ppg-mock-run
```

Expected evidence:

- review finding generated or loaded;
- backflow task compiled;
- target upstream node identified;
- affected draft marked stale;
- unrelated nodes remain committed.

### F8 — Real-paper single-section pilot

Goal: apply the runtime to one small manuscript unit from a real paper.

Scope:

- one Introduction paragraph or one Results interpretation paragraph;
- no whole-paper rewrite;
- no plugin install;
- no owner-gated semantic rewrite unless explicitly decided.

Deliverables:

- graph snapshot under the paper workspace;
- control materials for the chosen unit;
- writing task packet;
- candidate draft;
- review finding/backflow if applicable;
- validation report.

Exit gate:

- graph remains inspectable;
- candidate text traces to input materials;
- review failure maps to a specific upstream node;
- repair does not touch unrelated sections.

### F9 — Main-agent operating protocol hardening

Goal: turn observed process into durable instructions.

Deliverables:

- final main-agent prompt contract;
- subagent task packet prompt templates;
- commit protocol checklist;
- owner-gate checklist;
- graph-state report format.

Exit gate:

- another Codex session can read the repo and run the same mock loop.

### F10 — Only then evaluate OMX Pipeline wrapping

Questions to answer after F1-F9:

- Which PPG phases are stable enough to become pipeline stages?
- Does `$pipeline` add useful resume/stage visibility, or duplicate PPG state?
- Should pipeline wrap only high-level milestones while graph controls inner nodes?

Likely mapping:

```text
PPG design-check -> material-build -> writing-node-run -> review-backflow -> export-check
```

But this should not be implemented until the graph core works.

## Current next action

Start F1:

1. create material/task/finding/backflow schemas;
2. implement `ppg_store.py inspect`;
3. add minimal fixtures;
4. validate graph and fixture loading.
