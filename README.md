# yxj-paper-os

Language: **English** | [中文](README.zh-CN.md)

`yxj-paper-os` is the active Codex plugin for paper production management, implemented as a Paper Production Graph runtime.

The target model is:

> **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**

This plugin uses a graph runtime model: the main Codex agent controls a versioned paper-production graph, specialist agents or scripts operate on bounded graph nodes, validators decide node status, and review findings produce targeted backflow instead of whole-paper rewrites.

Its control model is the PPG runtime itself: material versions, transform tasks, validators, local backflow, and a main-agent controller.

## Current status

- Phase: Phase 13 promoted — live native-subagent full-flow pilot on top of the Phase 12 formal harness, followed by post-Phase13 main-agent lane-policy hardening. The runtime records 40 real native-subagent lanes in strict QA mode, and the canonical stage registry now tells the main agent when production should use mandatory producer+verifier lanes, conditional verifier escalation, or one lane plus deterministic validation. It remains a runtime-pilot capability, not a manuscript or submission-readiness claim.
- Local install: enabled through the personal-local marketplace as `yxj-paper-os`.
- Marketplace source: local personal marketplace entry pointing at `/home/weathour/plugins/yxj-paper-os`.

## Plain-language stage map

These names are the user-facing layer over the canonical StageContract names. The runtime still uses the stable `Sxx/Gxx` ids and official contract names.

| ID | Friendly name | Canonical contract name | What moves to the next stage |
| --- | --- | --- | --- |
| `S00` | Set goals and boundaries / 定目标与边界 | Owner semantic contract | Human intent, constraints, and approval gates become executable paper constraints. |
| `S01` | Inventory sources and evidence / 盘点来源与证据 | Source citation evidence inventory | Files, citations, result folders, and evidence anchors become a traceable material base. |
| `S02` | Map the research position / 看清研究位置 | Research scene exemplar SOTA analysis | Evidence is placed against field context, readers, venue patterns, and SOTA. |
| `S03` | Shape contribution options / 形成贡献候选 | Novelty and contribution option analysis | Possible contribution routes are generated, then sent to S04 for evidence admissibility. |
| `S04` | Lock evidence-backed claims / 锁定能说的主张 | Evidence-to-claim admissibility | Evidence and citations become bounded claims with allowed strength and forbidden overclaims. |
| `S05` | Build the paper spine / 搭建论文主线 | Paper spine and reader-question synthesis | Admitted claims become the reader question chain and section-level argument path. |
| `S06` | Design objects and granularity / 设计对象与颗粒度 | Object representation and granularity design | The paper decides what objects, variables, mechanisms, and explanation levels must appear. |
| `S07` | Align terminology and tone / 统一术语与表达 | Rhetoric terminology and surface-control synthesis | Terms, tone, rhetorical moves, and surface rules become writing controls. |
| `S08` | Plan figures and formal objects / 规划图表与形式对象 | Visual and formal object planning | Spine, evidence, and reader questions become figure/table/formula/algorithm contracts. |
| `S09A` | Select writing controls / 选择写作控制材料 | Control-material selection | Only the controls needed by the current unit are selected from claims, spine, granularity, and surface rules. |
| `S09B` | Assemble unit task packets / 组装单元任务包 | Per-unit task packet assembly | Selected controls, evidence anchors, boundaries, and return format become a bounded TaskPacket. |
| `S10` | Draft text candidates / 产出正文候选 | Main-text production | A worker returns candidate text and evidence from the packet, without completion authority. |
| `S11` | Produce figures and captions / 产出图表与说明 | Figure caption formal artifact production | Figure contracts and evidence locators become figures, tables, captions, formulas, or algorithm artifacts. |
| `S12` | Integrate and check consistency / 合并并查一致性 | Integration and consistency pass | Text, figures, citations, and terminology are merged and checked for cross-section drift. |
| `S13` | Run adversarial review / 对抗审稿找问题 | Adversarial manuscript review | Reviewers emit findings/loss signals instead of rewriting the whole paper. |
| `S14` | Compile repair tasks / 把问题转成修复任务 | Backflow compilation and repair planning | Findings are mapped to nearest responsible materials and converted into local repair packets. |
| `S15` | Repair and regenerate locally / 局部修复与再生成 | Repair execution and local regeneration | Only affected materials, text, or figures are regenerated and revalidated. |
| `S16` | Export, clean, and hand off / 导出、整理与交接 | Export repository hygiene and handoff | Closed review/repair state becomes export manifests, hygiene checks, and handoff notes. |
| `G01` | Runtime governance and authority / 运行治理与权限 | Runtime governance registry | Authority, route, state, and control boundaries are recorded without polluting manuscript cognition. |
| `G02` | Post-paper derivatives / 论文后派生输出 | Derivative and post-paper outputs | After the paper is stable, derivative outputs such as slides, patent boundaries, or profile packages may be created. |

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
29. [`docs/NATURE_STAGE_OVERLAY_SPEC.md`](docs/NATURE_STAGE_OVERLAY_SPEC.md) — stage-local Nature expert-writing overlay specification, authority model, stage bindings, TaskPacket transport, Phase10 integration, and validation matrix.
30. [`docs/phase-promotions/PHASE_11_NATURE_STAGE_OVERLAY_ABSORPTION_2026-06-30.md`](docs/phase-promotions/PHASE_11_NATURE_STAGE_OVERLAY_ABSORPTION_2026-06-30.md) — formal promotion record for Nature overlay absorption.
31. [`docs/phase-promotions/PHASE_12_FORMAL_FULL_FLOW_RUNTIME_TEST_2026-06-30.md`](docs/phase-promotions/PHASE_12_FORMAL_FULL_FLOW_RUNTIME_TEST_2026-06-30.md) — formal promotion record for the full-flow runtime-test harness.
32. [`docs/phase-promotions/PHASE_13_LIVE_SUBAGENT_FULL_FLOW_PILOT_2026-06-30.md`](docs/phase-promotions/PHASE_13_LIVE_SUBAGENT_FULL_FLOW_PILOT_2026-06-30.md) — formal promotion record for the live native-subagent full-flow pilot with producer/verifier lanes.
33. [`docs/STANDARD_PAPER_WORKSPACE.md`](docs/STANDARD_PAPER_WORKSPACE.md) — standard cross-repository paper directory/manifest contract for clear source, evidence, runtime, review, and export management.
34. [`docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md`](docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md) — source-writeback promotion protocol that upgrades S10/S11/S12/S15/S16 without creating a new LaTeX-master route.

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
- [`runtime/stage_registry.json`](runtime/stage_registry.json), [`examples/stage-contracts/`](examples/stage-contracts/), and [`examples/local-paper/security-state-aware-mixed-platoon/`](examples/local-paper/security-state-aware-mixed-platoon/): Phase 9 canonical stage registry, StageContracts, and full-stage local-paper pilot fixtures, now upgraded by Phase 10 to linked strict worker packet coverage for every dispatchable worker stage and post-Phase13 `subagent_lane_policy` for main-agent single/double-lane dispatch.
- [`runtime/phase10_content_validators.json`](runtime/phase10_content_validators.json), [`runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`](runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/), [`scripts/generate_phase10_run_dry_run.py`](scripts/generate_phase10_run_dry_run.py), [`scripts/verify_phase10_run_readiness.py`](scripts/verify_phase10_run_readiness.py), [`scripts/verify_phase10_forbidden_side_effects.py`](scripts/verify_phase10_forbidden_side_effects.py), and [`scripts/verify_phase10_real_run_readiness.sh`](scripts/verify_phase10_real_run_readiness.sh): Phase 10 real-subagent-run readiness surface, run-owned packet dry-run fixture, source-read-only filesystem snapshot proof excluding `.git/.omx`, forbidden-side-effect guard, and aggregate promotion gate.
- [`runtime/stage_overlay_registry.json`](runtime/stage_overlay_registry.json), [`schemas/ppg-stage-overlay-registry.schema.json`](schemas/ppg-stage-overlay-registry.schema.json), [`scripts/verify_stage_overlays.py`](scripts/verify_stage_overlays.py), and [`examples/overlays/`](examples/overlays/): Phase 11 Nature expert-writing stage-local overlay registry, machine-checkable authority/binding contract, positive/negative fixtures, StageContract links, strict TaskPacket overlay clauses, and Phase10 dry-run linkage.

- [`scripts/generate_phase12_full_flow_run.py`](scripts/generate_phase12_full_flow_run.py), [`scripts/verify_phase12_full_flow_run.py`](scripts/verify_phase12_full_flow_run.py), [`scripts/verify_phase12_formal_full_flow.sh`](scripts/verify_phase12_formal_full_flow.sh), and [`runs/security-state-aware-mixed-platoon/phase12-formal-full-flow-runtime-test/`](runs/security-state-aware-mixed-platoon/phase12-formal-full-flow-runtime-test/): Phase 12 deterministic formal full-flow runtime-test harness with run-owned candidates, dispatch/validation/material/frontier ledgers, local backflow closure, delivery-gate evidence, source snapshot refs, and exact-code negative probes.
- [`scripts/generate_phase13_live_pilot.py`](scripts/generate_phase13_live_pilot.py), [`scripts/record_phase13_subagent_return.py`](scripts/record_phase13_subagent_return.py), [`scripts/ingest_phase13_live_pilot.py`](scripts/ingest_phase13_live_pilot.py), [`scripts/verify_phase13_live_subagent_pilot.py`](scripts/verify_phase13_live_subagent_pilot.py), [`scripts/verify_phase13_live_subagent_pilot.sh`](scripts/verify_phase13_live_subagent_pilot.sh), and [`runs/security-state-aware-mixed-platoon/phase13-live-subagent-full-flow-pilot/`](runs/security-state-aware-mixed-platoon/phase13-live-subagent-full-flow-pilot/): Phase 13 live native-subagent pilot with 20 producer lanes, 20 independent verifier lanes, thread/hash provenance, run-owned stage effects, live validations, source-read-only snapshots, delivery-gate evidence, and exact-code negative probes.
- [`scripts/import_local_paper_pilot.py`](scripts/import_local_paper_pilot.py), [`scripts/generate_local_paper_full_pilot.py`](scripts/generate_local_paper_full_pilot.py), [`scripts/verify_local_paper_full_pilot.py`](scripts/verify_local_paper_full_pilot.py), [`scripts/verify_phase9_frontend_stage_coverage.py`](scripts/verify_phase9_frontend_stage_coverage.py), and [`scripts/verify_phase9_full_stage_runtime.sh`](scripts/verify_phase9_full_stage_runtime.sh): Phase 9 read-only import, PilotStageRun generation, frontend sync, and aggregate verification gates.
- [`schemas/ppg-paper-workspace.schema.json`](schemas/ppg-paper-workspace.schema.json), [`examples/paper-workspaces/`](examples/paper-workspaces/), and [`scripts/verify_paper_workspace_contract.py`](scripts/verify_paper_workspace_contract.py): standard PaperWorkspaceContract fixtures and validation for cross-repository paper directory management.
- [`schemas/ppg-latex-writeback-plan.schema.json`](schemas/ppg-latex-writeback-plan.schema.json), [`schemas/ppg-latex-writeback-patchset.schema.json`](schemas/ppg-latex-writeback-patchset.schema.json), [`examples/writeback-plans/`](examples/writeback-plans/), [`scripts/verify_latex_writeback_contract.py`](scripts/verify_latex_writeback_contract.py), [`scripts/execute_latex_writeback_plan.py`](scripts/execute_latex_writeback_plan.py), and [`scripts/verify_latex_writeback_execution.py`](scripts/verify_latex_writeback_execution.py): template-aware LaTeX source-writeback plan/patchset contract plus a fixture-proven executor for controlled S10/S11/S12/S15/S16 patch promotion; valid local production plans default to apply, build, validate, and create a scoped git commit, with rollback on validation failure.
- [`examples/packets/intro_writing_packet.v2.yaml`](examples/packets/intro_writing_packet.v2.yaml), [`examples/packets/claim_repair_packet.v1.yaml`](examples/packets/claim_repair_packet.v1.yaml), [`examples/missing_material_reports/intro_missing_reader_spine.v1.yaml`](examples/missing_material_reports/intro_missing_reader_spine.v1.yaml), and [`examples/candidate_returns/intro_candidate_return.v1.yaml`](examples/candidate_returns/intro_candidate_return.v1.yaml): Phase 6 positive evidence for strict packets, blocked compilation, and controller-bounded candidate return.
- [`examples/runtime/overclaim-loop.phase7-after.json`](examples/runtime/overclaim-loop.phase7-after.json): Phase 7 closed-loop after graph consumed by the Phase 8 runtime adapter/frontend state surface.

## Design principle

The main agent is the runtime controller of a paper-production graph:

```text
observe graph -> select frontier -> compile packet -> dispatch/execute -> collect -> validate -> commit/stale/backflow -> repeat
```
