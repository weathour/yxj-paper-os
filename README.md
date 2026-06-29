# yxj-paper-ppg-runtime

`yxj-paper-ppg-runtime` is a planning and implementation repository for a Codex-native paper production management plugin.

The target model is:

> **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**

This repository intentionally replaces the failed department-self-loop model with a graph runtime model: the main Codex agent controls a versioned paper-production graph, specialist agents or scripts operate on bounded graph nodes, validators decide node status, and review findings produce targeted backflow instead of whole-paper rewrites.

This project is not based on `$yxj-plugin-incubator` or Plugin OS v2+ concepts. Its control model is the PPG runtime itself: material versions, transform tasks, validators, local backflow, and a main-agent controller.

## Current status

- Phase: architecture and contract design.
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

## Minimal artifacts

- [`schemas/ppg-graph.schema.json`](schemas/ppg-graph.schema.json): draft graph data schema for front-end/runtime exchange.
- [`examples/minimal-paper-production-graph.json`](examples/minimal-paper-production-graph.json): smallest useful paper-production graph.
- [`scripts/validate_graph.py`](scripts/validate_graph.py): dependency-free structural validator for graph examples.

## Design principle

The main agent is not a department manager. It is the runtime controller of a paper-production graph:

```text
observe graph -> select frontier -> compile packet -> dispatch/execute -> collect -> validate -> commit/stale/backflow -> repeat
```
