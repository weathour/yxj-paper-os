---
name: yxj-paper-os
description: "Operate the standalone yxj Paper OS / Paper Production Graph Runtime as one public manager surface: inspect material authority, route feedback to accountable stages, compile bounded task/repair packets, validate outputs, and manage local backflow plus run retrospectives. Publication/submission claims remain owner-gated."
---

# yxj-paper-os

Use this skill when the user wants to design, inspect, or operate a Codex-native paper production graph runtime.

## Public surface

Expose exactly one public manager surface: the main Codex agent manages the paper-production graph. Internal graph operations, validators, task-packet compilers, worker lanes, fixtures, and frontend panels are implementation surfaces, not user-facing routes.

The current runtime model is:

> Explicit Material Graph + Stage Accountability + Local Backpropagation + Run Retrospective Learning + Main-Agent Dispatch

The main agent is the **Paper Production Graph Runtime Controller**. It controls versioned materials, task packets, feedback packages, failure attributions, validators, review findings, backflow tasks, repair packets, run retrospectives, stage-improvement records, owner decisions, review closures, and delivery gates.

Specialist agents and scripts may return candidates or evidence. Only the main agent/controller commits graph state or claims a node complete.

## Standalone boundary

`yxj-paper-os` owns its stage registry, material authority, validators, feedback lifecycle, and run records. It does not depend on OMX. OMX may be used personally as an optional orchestration adapter, but it is not a public interface, dependency, or authority source.

## Controller doctrine

A good integrated manuscript should emerge from high-quality upstream materials and bounded task packets. Review failure is treated as a signal that a stage/material/task packet/candidate did not meet its contract.

Default loop:

```text
observe graph
  -> select next frontier or feedback item
  -> compile task/repair packet
  -> dispatch worker or deterministic script
  -> collect candidate output
  -> validate
  -> commit / reject / mark stale / create backflow
  -> after full run, aggregate recurring failures into stage improvements
```

Do not rewrite the whole paper by default. First classify feedback, attribute it to the nearest responsible stage/material, repair only the affected scope, then revalidate downstream stale nodes.

## First documents to read

1. `README.md` or `README.zh-CN.md`
2. `docs/ARCHITECTURE_OVERVIEW.md`
3. `docs/MANAGER_SURFACE_PROTOCOL.md`
4. `docs/RUNTIME_PROTOCOL.md`
5. `docs/FEEDBACK_LIFECYCLE_PROTOCOL.md`
6. `docs/BACKFLOW_PROTOCOL.md`
7. `docs/MATERIAL_SCHEMA.md`
8. `docs/TOPOLOGY.md`
9. `docs/VALIDATION_AND_TESTING.md`
10. `docs/STANDARD_PAPER_WORKSPACE.md` when a local paper repository is involved
11. `docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md` when source writeback is requested or implied
12. `runtime/stage_registry.json` and relevant StageContracts when mapping work to `S00-S16/G01/G02`

## Runtime inspection commands

Use local graph-state-read-only commands before claiming graph state:

```bash
python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --format markdown
```

Check lifecycle contracts:

```bash
python3 scripts/verify_lifecycle_contract.py
```

Check core stage contracts:

```bash
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
```

Check standard workspace and writeback contracts:

```bash
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```

## Completion rule

A paper-production node is not complete because an agent produced text. It is complete only when the graph records candidate output, validator evidence, committed state, and scoped stale/backflow status.

Review findings and user feedback produce structured feedback/attribution/repair objects. They do not authorize whole-paper rewrites by default. Stage-improvement records are post-run system-learning proposals, not direct edits to the current paper.

## Safe operating boundaries

- Treat owner decisions as semantic authority gates.
- Treat runtime adapter output as graph-state-read-only inspection evidence.
- Treat frontend state as human-owner observability, not as a commit surface.
- Keep graph operations bounded by material/task/validator/feedback/backflow/delivery contracts.
- Preserve validation gates before promoting any manuscript state.
- Treat venue overlays as stage-local controls only; they may shape TaskPacket controls and validators but cannot become routes, dispatchers, or completion authority.
