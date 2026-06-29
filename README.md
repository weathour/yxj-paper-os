# yxj-paper-ppg-runtime

`yxj-paper-ppg-runtime` is a planning and implementation repository for a Codex-native paper production management plugin.

The target model is:

> **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**

This repository intentionally replaces the failed department-self-loop model with a graph runtime model: the main Codex agent controls a versioned paper-production graph, specialist agents or scripts operate on bounded graph nodes, validators decide node status, and review findings produce targeted backflow instead of whole-paper rewrites.

This project is not based on `$yxj-plugin-incubator` or Plugin OS v2+ concepts. Its control model is the PPG runtime itself: material versions, transform tasks, validators, local backflow, and a main-agent controller.

## Current status

- Phase: Phase 5 promoted — local backflow compiler and scoped stale propagation over the Phase 4 validator baseline.
- Live install: not enabled.
- Marketplace registration: not enabled.
- Existing `$yxj-paper-os`: not mutated by this repository.

## Core documents

1. [`docs/PLAN.md`](docs/PLAN.md) — full staged plan.
2. [`docs/TOPOLOGY.md`](docs/TOPOLOGY.md) — material graph topology, node/edge types, status, versioning.
3. [`docs/VISUALIZATION_CONTRACT.md`](docs/VISUALIZATION_CONTRACT.md) — front-end graph visualization requirements.
4. [`docs/MATERIAL_SCHEMA.md`](docs/MATERIAL_SCHEMA.md) — material envelope and typed payload families.
5. [`docs/RUNTIME_PROTOCOL.md`](docs/RUNTIME_PROTOCOL.md) — main-agent dispatch, task packets, frontier queue, commit protocol.
6. [`docs/BACKFLOW_PROTOCOL.md`](docs/BACKFLOW_PROTOCOL.md) — local backpropagation and stale propagation.
7. [`docs/VALIDATION_AND_TESTING.md`](docs/VALIDATION_AND_TESTING.md) — validator plan and closed-loop tests.
8. [`docs/ROADMAP.md`](docs/ROADMAP.md) — implementation roadmap.
9. [`docs/RELATED_FRAMEWORKS.md`](docs/RELATED_FRAMEWORKS.md) — OMX pipeline and related graph/agent framework survey.
10. [`docs/IMPLEMENTATION_FLOW.md`](docs/IMPLEMENTATION_FLOW.md) — concrete core-first implementation flow before OMX Pipeline wrapping.
11. [`docs/HUMAN_NEED_TO_PAPER_FLOW.md`](docs/HUMAN_NEED_TO_PAPER_FLOW.md) — human-need-centered paper production dimensions and flow diagram.
12. [`docs/YXJ_PAPER_OS_PROCESS_INVENTORY.md`](docs/YXJ_PAPER_OS_PROCESS_INVENTORY.md) — inventory of yxj-paper-os paper-production layers, dimensions, and materials.
13. [`docs/YXJ_PAPER_OS_NEURAL_LAYER_MAP.md`](docs/YXJ_PAPER_OS_NEURAL_LAYER_MAP.md) — all yxj-paper-os materials reorganized into neural-network-like paper-production layers.
14. [`docs/SUBAGENT_STAGE_BLUEPRINT.md`](docs/SUBAGENT_STAGE_BLUEPRINT.md) — dispatchable subagent stages with consumed bundles, outputs, validators, and backflow targets.
15. [`docs/decisions/0003-large-structured-material-bundles.md`](docs/decisions/0003-large-structured-material-bundles.md) — use large structured material bundles instead of lossy pre-compression.
16. [`docs/STAGE_COVERAGE_AUDIT.md`](docs/STAGE_COVERAGE_AUDIT.md) — audit whether the 17 dispatchable stages are excessive, redundant, or incomplete.
17. [`docs/PPG_RUNTIME_CONTROL_BLOCK.md`](docs/PPG_RUNTIME_CONTROL_BLOCK.md) — complete runtime control-block diagram with per-stage inputs, outputs, controller channels, validators, sidecars, and feedback loops.
18. [`docs/runtime-viewer/index.html`](docs/runtime-viewer/index.html) — interactive frontend for manually exploring the runtime graph, stage inputs/outputs, edge filters, focus paths, and review backflow.
19. [`docs/PPG_RUNTIME_MACRO_EXECUTION_PLAN_2026-06-29.md`](docs/PPG_RUNTIME_MACRO_EXECUTION_PLAN_2026-06-29.md) — macro execution plan for the new repository: phases, schemas, scripts, subagent packets, main-agent dispatch principles, and plugin wrapping order.
20. [`docs/PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md`](docs/PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md) — detailed eight-phase ideal-state roadmap and phase-scoped `$autopilot` / `$ralplan -> $ultragoal` execution protocol.
21. [`docs/phase-promotions/PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md`](docs/phase-promotions/PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md) — formal promotion record that freezes Phase 1 as the v0.2 abstract model baseline for Phase 2 implementation.
22. [`docs/phase-promotions/PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md`](docs/phase-promotions/PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md) — formal promotion record for the executable material graph core.
23. [`docs/phase-promotions/PHASE_3_CONTROLLER_LOGIC_2026-06-29.md`](docs/phase-promotions/PHASE_3_CONTROLLER_LOGIC_2026-06-29.md) — formal promotion record for the dry-run main-agent controller logic.
24. [`docs/phase-promotions/PHASE_4_MATERIAL_SCHEMAS_VALIDATORS_2026-06-29.md`](docs/phase-promotions/PHASE_4_MATERIAL_SCHEMAS_VALIDATORS_2026-06-29.md) — formal promotion record for Phase 4 material schemas and semantic validators.
25. [`docs/phase-promotions/PHASE_5_LOCAL_BACKFLOW_STALE_PROPAGATION_2026-06-29.md`](docs/phase-promotions/PHASE_5_LOCAL_BACKFLOW_STALE_PROPAGATION_2026-06-29.md) — formal promotion record for Phase 5 local backflow and scoped stale propagation.

## Minimal artifacts

- [`schemas/ppg-graph.schema.json`](schemas/ppg-graph.schema.json): graph data schema for front-end/runtime exchange, now including Phase 2 runtime material fields.
- [`schemas/ppg-material.schema.json`](schemas/ppg-material.schema.json), [`schemas/ppg-transform-task.schema.json`](schemas/ppg-transform-task.schema.json), [`schemas/ppg-validator-report.schema.json`](schemas/ppg-validator-report.schema.json): Phase 2 core runtime object contracts.
- [`schemas/ppg-owner-decision.schema.json`](schemas/ppg-owner-decision.schema.json): Phase 3 minimal owner decision record contract for owner-gated controller frontier items.
- [`schemas/ppg-review-finding.schema.json`](schemas/ppg-review-finding.schema.json), [`schemas/ppg-backflow-task.schema.json`](schemas/ppg-backflow-task.schema.json), [`schemas/ppg-review-closure.schema.json`](schemas/ppg-review-closure.schema.json), [`schemas/ppg-delivery-gate.schema.json`](schemas/ppg-delivery-gate.schema.json), [`schemas/ppg-task-packet.schema.json`](schemas/ppg-task-packet.schema.json), and [`schemas/ppg-material-payloads.schema.json`](schemas/ppg-material-payloads.schema.json): Phase 4 P0/P1 schema-and-validator spine.
- [`examples/minimal-paper-production-graph.json`](examples/minimal-paper-production-graph.json): smallest useful paper-production graph.
- [`examples/runtime/overclaim-loop.v1.json`](examples/runtime/overclaim-loop.v1.json): Phase 2 executable material-version runtime graph.
- [`examples/runtime/owner-gated-decision.json`](examples/runtime/owner-gated-decision.json), [`examples/runtime/stale-upstream-control.json`](examples/runtime/stale-upstream-control.json), [`examples/runtime/disconnected-stale-material.json`](examples/runtime/disconnected-stale-material.json), [`examples/runtime/weak-reference-stale-material.json`](examples/runtime/weak-reference-stale-material.json), [`examples/runtime/missing-task-packet.json`](examples/runtime/missing-task-packet.json), [`examples/runtime/commit-ready-candidate.json`](examples/runtime/commit-ready-candidate.json), [`examples/runtime/commit-ready-missing-provenance.json`](examples/runtime/commit-ready-missing-provenance.json): Phase 3 controller fixtures for owner-gated priority, stale frontier active-path filtering, missing task-packet priority, positive commit-plan dry-run readiness, and distinct provenance checks.
- [`examples/controller-reports/`](examples/controller-reports/): mandatory exact-output fixtures for Phase 3 controller reports.
- [`scripts/validate_graph.py`](scripts/validate_graph.py): dependency-free structural and Phase 2 runtime-semantics validator for graph examples.
- [`scripts/ppg_store.py`](scripts/ppg_store.py): dependency-free runtime graph inspection and dry-run controller CLI (`inspect`, `report`, `frontier`, `commit-plan`).
- [`scripts/validate_material.py`](scripts/validate_material.py), [`scripts/validate_review_finding.py`](scripts/validate_review_finding.py), [`scripts/validate_packet.py`](scripts/validate_packet.py), [`scripts/validate_backflow.py`](scripts/validate_backflow.py), and [`scripts/validate_delivery_gate.py`](scripts/validate_delivery_gate.py): Phase 4 dependency-free semantic validators with stable `VALID`/`INVALID` CLI output and failure codes.
- [`scripts/compile_backflow.py`](scripts/compile_backflow.py) and [`scripts/propagate_stale.py`](scripts/propagate_stale.py): Phase 5 deterministic local backflow compiler and scoped stale-propagation dry-run engine.
- [`examples/backflow_tasks/overclaim_repair.compiled.v1.yaml`](examples/backflow_tasks/overclaim_repair.compiled.v1.yaml), [`examples/runtime/overclaim-loop.phase5-stale.json`](examples/runtime/overclaim-loop.phase5-stale.json), and [`examples/controller-reports/overclaim-loop.phase5-stale.report.txt`](examples/controller-reports/overclaim-loop.phase5-stale.report.txt): Phase 5 before/after evidence that only affected downstream nodes become stale.

## Design principle

The main agent is not a department manager. It is the runtime controller of a paper-production graph:

```text
observe graph -> select frontier -> compile packet -> dispatch/execute -> collect -> validate -> commit/stale/backflow -> repeat
```
