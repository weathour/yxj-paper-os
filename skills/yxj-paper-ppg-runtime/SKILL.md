---
name: yxj-paper-ppg-runtime
description: "Operate the yxj Paper Production Graph Runtime as one public manager surface: inspect explicit material graph state, local backflow, task packets, validation gates, and frontend runtime reports for Codex-native academic paper production. Local development surface only; not live-installed or published by default."
---

# yxj-paper-ppg-runtime

Use this skill when the user wants to design, inspect, or operate a Codex-native paper production graph runtime.

## Public surface

Expose exactly one public manager surface: the main Codex agent manages the paper-production graph. Internal graph operations, validators, task-packet compilers, mock workers, and frontend panels are implementation lanes, not user-facing departments.

The runtime model is:

> Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch

The main agent controls a versioned graph of materials, task packets, validators, review findings, backflow tasks, owner decisions, review closures, and delivery gates. Specialist agents and scripts may return candidates or reports; only the main agent/controller commits graph state or claims completion.

## Current repository status

This repository is a local Phase10 plugin/runtime readiness surface. It provides:

- graph-state-read-only runtime adapter: `scripts/ppg_runtime_adapter.py`;
- deterministic state reports: `examples/runtime-reports/overclaim-loop.phase7-state.{json,md}`;
- interactive frontend: `docs/runtime-viewer/index.html` with roadmap, detailed graph, Runtime State, and Stage Coverage modes;
- full-stage local-paper pilot fixtures under `examples/local-paper/security-state-aware-mixed-platoon/`;
- one `PilotStageRun` for every canonical stage `S00-S16/G01/G02`, with explicit completion boundaries;
- strict linked TaskPackets for every dispatchable worker stage;
- Phase10 content validators and a runtime-owned dry-run fixture under `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`;
- untracked-aware source-read-only proof and forbidden-side-effect guards;
- Phase7 vertical-slice proof and Phase6 strict task-packet regression gates;
- local plugin manifest validation through the Codex plugin validator.

Do **not** mutate old `$yxj-paper-os`, use `$yxj-plugin-incubator` as a design source, live-install this plugin, publish it, update a cachebuster, or edit marketplace entries unless the user explicitly authorizes that external/plugin lifecycle step.

## First documents to read

1. `README.md`
2. `docs/PLAN.md`
3. `docs/TOPOLOGY.md`
4. `docs/VISUALIZATION_CONTRACT.md`
5. `docs/MATERIAL_SCHEMA.md`
6. `docs/RUNTIME_PROTOCOL.md`
7. `docs/BACKFLOW_PROTOCOL.md`
8. `docs/VALIDATION_AND_TESTING.md`
9. `docs/phase-promotions/PHASE_10_REAL_SUBAGENT_RUN_READINESS_2026-06-30.md`
10. `docs/phase-promotions/PHASE_9_FULL_STAGE_LOCAL_PAPER_PILOT_2026-06-30.md`
11. `docs/phase-promotions/PHASE_8_PLUGIN_FRONTEND_RUNTIME_SURFACE_2026-06-30.md`

## Runtime inspection commands

Use these local graph-state-read-only commands before claiming graph state:

```bash
python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --format json

python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --format markdown
```

To inspect the Phase9 full-stage local-paper pilot:

```bash
python3 scripts/import_local_paper_pilot.py \
  --source /home/weathour/文档/CPS-Papers/papers/security-state-aware-mixed-platoon \
  --out examples/local-paper/security-state-aware-mixed-platoon \
  --check

python3 scripts/generate_local_paper_full_pilot.py \
  --pilot-root examples/local-paper/security-state-aware-mixed-platoon \
  --check

python3 scripts/verify_local_paper_full_pilot.py \
  examples/local-paper/security-state-aware-mixed-platoon

python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --stage-coverage examples/local-paper/security-state-aware-mixed-platoon/stage_coverage.json \
  --format json
```

For the complete local Phase10 readiness gate:

```bash
bash scripts/verify_phase10_real_run_readiness.sh
```

For the inherited Phase9 pilot gate:

```bash
bash scripts/verify_phase9_full_stage_runtime.sh
```

## Completion rule

A paper-production node is not complete because an agent produced text. It is complete only when the graph records candidate output, validator evidence, committed state, and scoped stale/backflow status. Review findings produce local backflow tasks; they do not authorize whole-paper rewrites by default.

## Safe operating boundaries

- Treat owner decisions as semantic authority gates.
- Treat runtime adapter output as graph-state-read-only inspection evidence; `--out` may write report files but must not overwrite the input graph.
- Treat frontend state as human-owner observability, not as a commit surface.
- Keep graph-operation modules bounded by material/task/validator/backflow/delivery contracts.
- Preserve existing validation gates before promoting any phase or manuscript state.
