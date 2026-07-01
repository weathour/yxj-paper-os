# yxj-paper-os

`yxj-paper-os` is a standalone Codex plugin for managing academic paper production as an explicit Paper Production Graph.

The current model is:

> **Explicit Material Graph + Stage Accountability + Local Backpropagation + Run Retrospective Learning + Main-Agent Dispatch**

A main Codex agent acts as the **Paper Production Graph Runtime Controller**. It reads the active paper workspace, distinguishes committed materials from candidates or archives, dispatches bounded task packets, validates outputs, commits graph state, routes feedback to the nearest responsible stage, and records scoped stale/backflow status.

Workers, scripts, PDFs, frontend panels, and optional orchestration tools may provide evidence. They do not own completion authority.

## Product principle

The best paper is not rescued by last-minute rewriting. It should emerge from strong upstream controls:

```text
S00-S08 control materials
  -> S09A/S09B task packets
  -> S10/S11 candidates
  -> S12 integrated candidate
  -> S13 review
  -> S14/S15 scoped repair when needed
  -> S16 clean handoff
```

If review fails, the controller first attributes the failure to the responsible stage/material, then repairs only the affected scope. After a full run, repeated feedback patterns can improve stage prompts, task-packet clauses, validators, and material templates.

## Standalone boundary

`yxj-paper-os` owns its stage registry, material authority, validators, feedback lifecycle, and run records. It does **not** depend on OMX. OMX or other orchestration systems may be used as optional personal adapters, but they are never the public interface, dependency, or authority source.

## Canonical stages

| ID | Purpose |
| --- | --- |
| `S00` | Owner route, venue, contribution boundary, and forbidden routes |
| `S01` | Source, citation, result, and evidence inventory |
| `S02` | Venue, exemplar, SOTA, and field-position analysis |
| `S03` | Contribution option framing and challenge |
| `S04` | Claim-evidence admissibility and forbidden wording |
| `S05` | Paper spine and reader/reviewer question path |
| `S06` | Object, mechanism, variable, and granularity design |
| `S07` | Terminology, rhetoric, tone, and surface controls |
| `S08` | Figure, table, formula, and algorithm contracts |
| `S09A` | Select controls for a target writing/artifact unit |
| `S09B` | Compile a bounded per-unit TaskPacket |
| `S10` | Produce main-text candidates from packets |
| `S11` | Produce figures, captions, tables, formulas, and artifact bundles |
| `S12` | Integrate candidates and check cross-section consistency |
| `S13` | Generate actionable review findings, not whole-paper rewrites |
| `S14` | Convert findings into local repair tasks |
| `S15` | Execute bounded repairs and regenerate only affected outputs |
| `S16` | Export, repository hygiene, and owner handoff |
| `G01` | Runtime governance, authority, and state controls |
| `G02` | Optional post-paper derivative outputs after paper stability |

The machine source of truth is `runtime/stage_registry.json` plus `examples/stage-contracts/`.

## Core lifecycle objects

- `Material` — versioned paper material envelope and typed payload.
- `TaskPacket` — bounded worker contract with explicit input materials, evidence anchors, allowed actions, allowed paths, validators, and no completion authority.
- `CandidateArtifactReturn` — worker return object; candidate only.
- `ReviewFinding` — validated loss signal from review.
- `BackflowTask` — local repair plan targeting one responsible material.
- `ReviewFeedbackPackage` — normalized user/reviewer feedback before repair.
- `FailureAttributionRecord` — nearest-stage/material routing evidence.
- `RepairTaskPacket` — bounded current-paper repair contract.
- `RunRetrospectiveReport` — full-run learning report.
- `StageImprovementRecord` — proposed improvement to prompts, packets, validators, or material templates.

## Core documents

1. [`docs/MANAGER_SURFACE_PROTOCOL.md`](docs/MANAGER_SURFACE_PROTOCOL.md) — public manager identity, read sequence, status reports, and decision routing.
2. [`docs/RUNTIME_PROTOCOL.md`](docs/RUNTIME_PROTOCOL.md) — controller loop, frontier priority, dispatch policy, lane policy, and commit protocol.
3. [`docs/FEEDBACK_LIFECYCLE_PROTOCOL.md`](docs/FEEDBACK_LIFECYCLE_PROTOCOL.md) — feedback packages, attribution, repair packets, retrospectives, and stage improvements.
4. [`docs/BACKFLOW_PROTOCOL.md`](docs/BACKFLOW_PROTOCOL.md) — local backpropagation and stale propagation.
5. [`docs/MATERIAL_SCHEMA.md`](docs/MATERIAL_SCHEMA.md) — material envelope and typed material families.
6. [`docs/TOPOLOGY.md`](docs/TOPOLOGY.md) — graph nodes, edge types, status vocabulary, and versioning rules.
7. [`docs/VALIDATION_AND_TESTING.md`](docs/VALIDATION_AND_TESTING.md) — validation commands and regression matrix.
8. [`docs/STANDARD_PAPER_WORKSPACE.md`](docs/STANDARD_PAPER_WORKSPACE.md) — cross-repository paper workspace contract.
9. [`docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md`](docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md) — controlled manuscript source writeback.
10. [`docs/NATURE_STAGE_OVERLAY_SPEC.md`](docs/NATURE_STAGE_OVERLAY_SPEC.md) — stage-local venue overlay controls.

## Validation quick start

```bash
python3 scripts/verify_lifecycle_contract.py
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```

For local-paper projection, use the repo-local sample workspace:

```bash
python3 scripts/import_local_paper_pilot.py \
  --source examples/sample-paper-workspace \
  --out examples/local-paper/sample-paper-workspace \
  --check
python3 scripts/generate_local_paper_full_pilot.py \
  --pilot-root examples/local-paper/sample-paper-workspace \
  --check
python3 scripts/verify_local_paper_full_pilot.py \
  examples/local-paper/sample-paper-workspace
```

## Completion rule

A paper-production node is complete only when the graph records candidate output, validator evidence, committed state, and scoped stale/backflow status. A review finding produces a local repair path; it does not authorize a whole-paper rewrite by default.
