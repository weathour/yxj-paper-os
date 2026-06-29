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

This repository is a local Phase8 plugin/runtime surface. It provides:

- read-only runtime adapter: `scripts/ppg_runtime_adapter.py`;
- deterministic state reports: `examples/runtime-reports/overclaim-loop.phase7-state.{json,md}`;
- interactive frontend: `docs/runtime-viewer/index.html` with roadmap, detailed graph, and Runtime State modes;
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
9. `docs/phase-promotions/PHASE_8_PLUGIN_FRONTEND_RUNTIME_SURFACE_2026-06-30.md`

## Runtime inspection commands

Use these local read-only commands before claiming graph state:

```bash
python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --format json

python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --format markdown
```

For the complete local Phase8 gate:

```bash
bash scripts/verify_phase8_plugin_surface.sh
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
bash scripts/verify_phase6_task_packets.sh
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

## Completion rule

A paper-production node is not complete because an agent produced text. It is complete only when the graph records candidate output, validator evidence, committed state, and scoped stale/backflow status. Review findings produce local backflow tasks; they do not authorize whole-paper rewrites by default.

## Safe operating boundaries

- Treat owner decisions as semantic authority gates.
- Treat runtime adapter output as read-only inspection evidence.
- Treat frontend state as human-owner observability, not as a commit surface.
- Keep graph-operation modules bounded by material/task/validator/backflow/delivery contracts.
- Preserve existing validation gates before promoting any phase or manuscript state.
