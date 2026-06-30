# Nature Expert-Writing Stage Overlay Specification

Date: 2026-06-30

## Purpose

The Nature-related writing expertise is absorbed as a **stage-local overlay**, not as a new route, not as a second orchestration loop, and not as a replacement for the PPG runtime controller.

The invariant remains:

```text
Explicit Material Graph + Local Backflow + Main-Agent Dispatch
```

The overlay contributes expert-writing controls to existing stages. It never dispatches workers, certifies completion, mutates the graph, or claims manuscript/submission readiness.

## Core artifacts

- Registry: `runtime/stage_overlay_registry.json`
- Schema: `schemas/ppg-stage-overlay-registry.schema.json`
- Validator: `scripts/verify_stage_overlays.py`
- Positive fixtures: `examples/overlays/nature_stage_overlay.valid.json`, `examples/overlays/valid-controller-boundary-note.json`
- Negative fixtures: `examples/overlays/invalid-*.json`
- Contract links: `examples/stage-contracts/*.stage-contract.json` field `stage_local_overlays`
- TaskPacket transport: `mandatory_controls.nature_overlay_*` plus `validators: stage_overlay:nature_expert_writing:<stage_id>`
- Phase10 run links: `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/**`

## Authority model

`nature_expert_writing` is valid only when all of these are true:

- `stage_local_only=true`
- `no_independent_route=true`
- `controller_owned_completion=true`
- `worker_completion_forbidden=true`
- `no_recursive_orchestration=true`
- `overlay_dispatch_allowed=false`
- `route_kind=stage_local_overlay`

This means a TaskPacket can consume Nature overlay controls, but the worker still returns only candidate artifacts/evidence. Completion remains owned by the main-agent runtime controller.

## Stage binding profile

| Binding strength | Stages | Meaning |
| --- | --- | --- |
| `primary` | S02, S04, S05, S06, S07, S08, S09A, S09B, S10, S11, S12, S13, S14, S15, S16 | Nature expertise materially shapes the stage’s controls, outputs, or review lens. |
| `support` | S03 | Novelty/significance brainstorming is allowed, but S03 remains support/light and must pass S04 before writing. |
| `light` | S00, S01 | Owner route, article-type/source/data-availability inventories; no semantic completion authority. |
| `governance` | G01 | Records authority constraints only. |
| `derivative` | G02 | Post-paper derivative packaging only; not current manuscript cognition. |

`S09` is still forbidden as a bare stage. Overlay bindings must use `S09A` and `S09B`.

## Stage-local inputs and outputs

Each registry binding declares:

- `input_controls`: the Nature-specific controls consumed by the stage;
- `output_materials`: the Nature-shaped materials emitted by the stage;
- `packet_clauses`: mandatory clauses that must appear inside worker TaskPacket `mandatory_controls`, not top-level packet fields;
- `validator_checks`: stage-local checks consumed by validator registries and run artifacts;
- `backflow_targets`: nearest stages to revisit when the overlay finds a problem;
- `prohibited_routes`: authority boundaries that prevent controller-bypassing route behavior.

Examples:

- S04 adds claim-strength calibration, overclaim patterns, evidence visibility, allowed/forbidden wording, and data-availability planning.
- S08 adds figure contract, panel-evidence, visual hierarchy, reporting standards, and supplement planning.
- S10 adds lede/focus, paragraph economy, contribution-first prose, citation cadence, and conclusion restraint.
- S13 adds reviewer-objection, editorial desk-risk, figure-quality, claim-strength, and reader-experience checks.

## TaskPacket transport rule

The overlay must be transported through the existing strict TaskPacket boundary:

```yaml
mandatory_controls:
  nature_overlay_ref: runtime/stage_overlay_registry.json#nature_expert_writing
  nature_overlay_stage_binding: S10
  nature_overlay_packet_clauses:
    - "nature_overlay_ref:nature_expert_writing"
    - "nature_stage_binding:S10"
    - "nature_overlay_role:primary"
validators:
  - "stage_overlay:nature_expert_writing:S10"
```

Forbidden: adding a new top-level `nature_*` TaskPacket field, an overlay-owned dispatch model, or a worker-owned completion status.

## Phase10 / real-run readiness integration

Phase10 now proves overlay linkage before real subagent execution:

- `scripts/generate_phase10_run_dry_run.py` writes `stage_overlay_registry_ref` and `active_stage_overlays` into dispatch records, validation records, candidate placeholders, stage states, manifest, and run state.
- `scripts/verify_phase10_run_readiness.py` validates the overlay registry, StageContract links, TaskPacket controls, per-run TaskPacket controls, and dry-run artifact linkage.
- `scripts/verify_phase10_real_run_readiness.sh` includes overlay validation and negative probes for missing dispatch/packet overlay linkage.

## Validation matrix

Run:

```bash
python3 scripts/verify_stage_overlays.py
python3 scripts/generate_phase10_run_dry_run.py --check
python3 scripts/verify_phase10_run_readiness.py
```

The validator locks these failure classes:

- unknown stage id;
- bare `S09`;
- authority expansion or autonomous execution route;
- missing worker packet clause;
- missing content-validator coverage;
- invalid backflow target;
- missing required Nature overlay;
- missing primary binding;
- false positive prevention for documentation text that states controller-only stage-local boundaries.

## Non-goals

- No migration back to controller-bypassing routes.
- Only controller-authorized PPG runtime routes are active.
- No lifecycle mutation inside the Nature overlay absorption itself; owner-authorized plugin replacement may update install/cachebuster through the controller workflow.
- No claim that Nature skill absorption makes the paper complete or submission-ready.
