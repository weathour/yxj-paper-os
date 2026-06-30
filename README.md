# yxj-paper-ppg-runtime

`yxj-paper-ppg-runtime` is a planning and implementation repository for a Codex-native paper production management plugin.

The target model is:

> **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**

This repository intentionally replaces the failed department-self-loop model with a graph runtime model: the main Codex agent controls a versioned paper-production graph, specialist agents or scripts operate on bounded graph nodes, validators decide node status, and review findings produce targeted backflow instead of whole-paper rewrites.

This project is not based on `$yxj-plugin-incubator` or Plugin OS v2+ concepts. Its control model is the PPG runtime itself: material versions, transform tasks, validators, local backflow, and a main-agent controller.

## Current status

- Phase: Phase 10 promoted — real-subagent-run readiness with strict packet coverage for every dispatchable worker stage, content validator registry, runtime-owned dry-run fixture, untracked-aware source-read-only proof, and aggregate validation over inherited Phase 9/8/7/6 gates.
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
12. [`docs/SUBAGENT_STAGE_BLUEPRINT.md`](docs/SUBAGENT_STAGE_BLUEPRINT.md) — dispatchable subagent stages with consumed bundles, outputs, validators, and backflow targets.
13. [`docs/decisions/0003-large-structured-material-bundles.md`](docs/decisions/0003-large-structured-material-bundles.md) — use large structured material bundles instead of lossy pre-compression.
14. [`docs/STAGE_COVERAGE_AUDIT.md`](docs/STAGE_COVERAGE_AUDIT.md) — audit whether the 17 dispatchable stages are excessive, redundant, or incomplete.
15. [`docs/PPG_RUNTIME_CONTROL_BLOCK.md`](docs/PPG_RUNTIME_CONTROL_BLOCK.md) — complete runtime control-block diagram with per-stage inputs, outputs, controller channels, validators, sidecars, and feedback loops.
16. [`docs/runtime-viewer/index.html`](docs/runtime-viewer/index.html) — interactive frontend for manually exploring the runtime graph, stage inputs/outputs, edge filters, focus paths, and review backflow.
17. [`docs/PPG_RUNTIME_MACRO_EXECUTION_PLAN_2026-06-29.md`](docs/PPG_RUNTIME_MACRO_EXECUTION_PLAN_2026-06-29.md) — macro execution plan for the new repository: phases, schemas, scripts, subagent packets, main-agent dispatch principles, and plugin wrapping order.
18. [`docs/PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md`](docs/PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md) — detailed eight-phase ideal-state roadmap and phase-scoped `$autopilot` / `$ralplan -> $ultragoal` execution protocol.
19. [`docs/phase-promotions/PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md`](docs/phase-promotions/PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md) — formal promotion record that freezes Phase 1 as the v0.2 abstract model baseline for Phase 2 implementation.
20. [`docs/phase-promotions/PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md`](docs/phase-promotions/PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md) — formal promotion record for the executable material graph core.
21. [`docs/phase-promotions/PHASE_3_CONTROLLER_LOGIC_2026-06-29.md`](docs/phase-promotions/PHASE_3_CONTROLLER_LOGIC_2026-06-29.md) — formal promotion record for the dry-run main-agent controller logic.
22. [`docs/phase-promotions/PHASE_4_MATERIAL_SCHEMAS_VALIDATORS_2026-06-29.md`](docs/phase-promotions/PHASE_4_MATERIAL_SCHEMAS_VALIDATORS_2026-06-29.md) — formal promotion record for Phase 4 material schemas and semantic validators.
23. [`docs/phase-promotions/PHASE_5_LOCAL_BACKFLOW_STALE_PROPAGATION_2026-06-29.md`](docs/phase-promotions/PHASE_5_LOCAL_BACKFLOW_STALE_PROPAGATION_2026-06-29.md) — formal promotion record for Phase 5 local backflow and scoped stale propagation.
24. [`docs/phase-promotions/PHASE_6_SUBAGENT_TASK_PACKET_MECHANISM_2026-06-29.md`](docs/phase-promotions/PHASE_6_SUBAGENT_TASK_PACKET_MECHANISM_2026-06-29.md) — formal promotion record for Phase 6 strict packet compilation and return contracts.
25. [`docs/phase-promotions/PHASE_7_VERTICAL_SLICE_2026-06-29.md`](docs/phase-promotions/PHASE_7_VERTICAL_SLICE_2026-06-29.md) — formal promotion record for the deterministic overclaim repair vertical slice.
26. [`docs/phase-promotions/PHASE_8_PLUGIN_FRONTEND_RUNTIME_SURFACE_2026-06-30.md`](docs/phase-promotions/PHASE_8_PLUGIN_FRONTEND_RUNTIME_SURFACE_2026-06-30.md) — formal promotion record for the local plugin/frontend runtime surface.
27. [`docs/phase-promotions/PHASE_9_FULL_STAGE_LOCAL_PAPER_PILOT_2026-06-30.md`](docs/phase-promotions/PHASE_9_FULL_STAGE_LOCAL_PAPER_PILOT_2026-06-30.md) — formal promotion record for full-stage local-paper PilotStageRun coverage.
28. [`docs/phase-promotions/PHASE_10_REAL_SUBAGENT_RUN_READINESS_2026-06-30.md`](docs/phase-promotions/PHASE_10_REAL_SUBAGENT_RUN_READINESS_2026-06-30.md) — formal promotion record for real full-flow subagent run readiness without starting paper production.

## Archived provenance

Historical yxj-paper-os process inventory and neural-layer map artifacts are preserved under [`archive/legacy-yxj-paper-os-design-20260630/MANIFEST.md`](archive/legacy-yxj-paper-os-design-20260630/MANIFEST.md). They are provenance only and are not active runtime instructions.

## Minimal artifacts

- [`schemas/ppg-graph.schema.json`](schemas/ppg-graph.schema.json): graph data schema for front-end/runtime exchange, now including Phase 2 runtime material fields.
- [`schemas/ppg-material.schema.json`](schemas/ppg-material.schema.json), [`schemas/ppg-transform-task.schema.json`](schemas/ppg-transform-task.schema.json), [`schemas/ppg-validator-report.schema.json`](schemas/ppg-validator-report.schema.json): Phase 2 core runtime object contracts.
- [`schemas/ppg-owner-decision.schema.json`](schemas/ppg-owner-decision.schema.json): Phase 3 minimal owner decision record contract for owner-gated controller frontier items.
- [`schemas/ppg-review-finding.schema.json`](schemas/ppg-review-finding.schema.json), [`schemas/ppg-backflow-task.schema.json`](schemas/ppg-backflow-task.schema.json), [`schemas/ppg-review-closure.schema.json`](schemas/ppg-review-closure.schema.json), [`schemas/ppg-delivery-gate.schema.json`](schemas/ppg-delivery-gate.schema.json), [`schemas/ppg-task-packet.schema.json`](schemas/ppg-task-packet.schema.json), and [`schemas/ppg-material-payloads.schema.json`](schemas/ppg-material-payloads.schema.json): Phase 4 P0/P1 schema-and-validator spine, with Phase 6 strict TaskPacket authority fields.
- [`schemas/ppg-missing-material-report.schema.json`](schemas/ppg-missing-material-report.schema.json), [`schemas/ppg-candidate-return.schema.json`](schemas/ppg-candidate-return.schema.json), [`schemas/ppg-stage-contract.schema.json`](schemas/ppg-stage-contract.schema.json), and [`schemas/ppg-pilot-stage-run.schema.json`](schemas/ppg-pilot-stage-run.schema.json): Phase 6 blocked-dispatch/candidate-return contracts plus Phase 9 stage and pilot-run contracts.
- [`examples/minimal-paper-production-graph.json`](examples/minimal-paper-production-graph.json): smallest useful paper-production graph.
- [`examples/runtime/overclaim-loop.v1.json`](examples/runtime/overclaim-loop.v1.json): Phase 2 executable material-version runtime graph.
- [`examples/runtime/owner-gated-decision.json`](examples/runtime/owner-gated-decision.json), [`examples/runtime/stale-upstream-control.json`](examples/runtime/stale-upstream-control.json), [`examples/runtime/disconnected-stale-material.json`](examples/runtime/disconnected-stale-material.json), [`examples/runtime/weak-reference-stale-material.json`](examples/runtime/weak-reference-stale-material.json), [`examples/runtime/missing-task-packet.json`](examples/runtime/missing-task-packet.json), [`examples/runtime/commit-ready-candidate.json`](examples/runtime/commit-ready-candidate.json), [`examples/runtime/commit-ready-missing-provenance.json`](examples/runtime/commit-ready-missing-provenance.json): Phase 3 controller fixtures for owner-gated priority, stale frontier active-path filtering, missing task-packet priority, positive commit-plan dry-run readiness, and distinct provenance checks.
- [`examples/controller-reports/`](examples/controller-reports/): mandatory exact-output fixtures for Phase 3 controller reports.
- [`scripts/validate_graph.py`](scripts/validate_graph.py): dependency-free structural and Phase 2 runtime-semantics validator for graph examples.
- [`scripts/ppg_store.py`](scripts/ppg_store.py): dependency-free runtime graph inspection and dry-run controller CLI (`inspect`, `report`, `frontier`, `commit-plan`).
- [`scripts/validate_material.py`](scripts/validate_material.py), [`scripts/validate_review_finding.py`](scripts/validate_review_finding.py), [`scripts/validate_packet.py`](scripts/validate_packet.py), [`scripts/validate_backflow.py`](scripts/validate_backflow.py), [`scripts/validate_delivery_gate.py`](scripts/validate_delivery_gate.py), [`scripts/validate_missing_material_report.py`](scripts/validate_missing_material_report.py), and [`scripts/validate_candidate_return.py`](scripts/validate_candidate_return.py): dependency-free semantic validators with stable `VALID`/`INVALID` CLI output and failure codes.
- [`scripts/compile_backflow.py`](scripts/compile_backflow.py) and [`scripts/propagate_stale.py`](scripts/propagate_stale.py): Phase 5 deterministic local backflow compiler and scoped stale-propagation dry-run engine.
- [`examples/backflow_tasks/overclaim_repair.compiled.v1.yaml`](examples/backflow_tasks/overclaim_repair.compiled.v1.yaml), [`examples/runtime/overclaim-loop.phase5-stale.json`](examples/runtime/overclaim-loop.phase5-stale.json), and [`examples/controller-reports/overclaim-loop.phase5-stale.report.txt`](examples/controller-reports/overclaim-loop.phase5-stale.report.txt): Phase 5 before/after evidence that only affected downstream nodes become stale.
- [`scripts/compile_task_packet.py`](scripts/compile_task_packet.py): Phase 6 deterministic strict TaskPacket compiler for intro-writing and claim-repair targets.
- [`scripts/verify_phase6_task_packets.sh`](scripts/verify_phase6_task_packets.sh): Phase 6 regression matrix for strict packet compilation, missing-material reports, packet-aware returns, authority/path negative fixtures, and Phase 5 regressions.
- [`scripts/ppg_runtime_adapter.py`](scripts/ppg_runtime_adapter.py): Phase 8 graph-state-read-only operator-facing adapter that validates a graph and emits deterministic JSON/Markdown runtime state reports.
- [`scripts/verify_phase8_plugin_surface.sh`](scripts/verify_phase8_plugin_surface.sh): Phase 8 validation wrapper for adapter semantic keys/sections, invalid graph/output-path rejection, frontend runtime-state sync, frontend syntax/safe-DOM assertions, plugin/skill validation, and Phase7/Phase6 inherited gates.
- [`examples/runtime-reports/overclaim-loop.phase7-state.json`](examples/runtime-reports/overclaim-loop.phase7-state.json) and [`examples/runtime-reports/overclaim-loop.phase7-state.md`](examples/runtime-reports/overclaim-loop.phase7-state.md): deterministic Phase 8 state report fixtures for the Phase 7 after graph.
- [`runtime/stage_registry.json`](runtime/stage_registry.json), [`examples/stage-contracts/`](examples/stage-contracts/), and [`examples/local-paper/security-state-aware-mixed-platoon/`](examples/local-paper/security-state-aware-mixed-platoon/): Phase 9 canonical stage registry, StageContracts, and full-stage local-paper pilot fixtures, now upgraded by Phase 10 to linked strict worker packet coverage for every dispatchable worker stage.
- [`runtime/phase10_content_validators.json`](runtime/phase10_content_validators.json), [`runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`](runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/), [`scripts/generate_phase10_run_dry_run.py`](scripts/generate_phase10_run_dry_run.py), [`scripts/verify_phase10_run_readiness.py`](scripts/verify_phase10_run_readiness.py), [`scripts/verify_phase10_forbidden_side_effects.py`](scripts/verify_phase10_forbidden_side_effects.py), and [`scripts/verify_phase10_real_run_readiness.sh`](scripts/verify_phase10_real_run_readiness.sh): Phase 10 real-subagent-run readiness surface, dry-run fixture, source-read-only proof, forbidden-side-effect guard, and aggregate promotion gate.
- [`scripts/import_local_paper_pilot.py`](scripts/import_local_paper_pilot.py), [`scripts/generate_local_paper_full_pilot.py`](scripts/generate_local_paper_full_pilot.py), [`scripts/verify_local_paper_full_pilot.py`](scripts/verify_local_paper_full_pilot.py), [`scripts/verify_phase9_frontend_stage_coverage.py`](scripts/verify_phase9_frontend_stage_coverage.py), and [`scripts/verify_phase9_full_stage_runtime.sh`](scripts/verify_phase9_full_stage_runtime.sh): Phase 9 read-only import, PilotStageRun generation, frontend sync, and aggregate verification gates.
- [`examples/packets/intro_writing_packet.v2.yaml`](examples/packets/intro_writing_packet.v2.yaml), [`examples/packets/claim_repair_packet.v1.yaml`](examples/packets/claim_repair_packet.v1.yaml), [`examples/missing_material_reports/intro_missing_reader_spine.v1.yaml`](examples/missing_material_reports/intro_missing_reader_spine.v1.yaml), and [`examples/candidate_returns/intro_candidate_return.v1.yaml`](examples/candidate_returns/intro_candidate_return.v1.yaml): Phase 6 positive evidence for strict packets, blocked compilation, and non-self-certifying candidate return.
- [`examples/runtime/overclaim-loop.phase7-after.json`](examples/runtime/overclaim-loop.phase7-after.json): Phase 7 closed-loop after graph consumed by the Phase 8 runtime adapter/frontend state surface.

## Design principle

The main agent is not a department manager. It is the runtime controller of a paper-production graph:

```text
observe graph -> select frontier -> compile packet -> dispatch/execute -> collect -> validate -> commit/stale/backflow -> repeat
```
