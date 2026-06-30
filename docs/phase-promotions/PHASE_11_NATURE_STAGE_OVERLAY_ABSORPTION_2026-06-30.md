# Phase 11 Promotion — Nature Stage Overlay Absorption

Date: 2026-06-30

## Promotion decision

Phase 11 promotes `yxj-paper-os` from Phase10 real-subagent-run readiness to a Nature-experience-aware runtime surface.

The Nature skill experience is absorbed as `nature_expert_writing`, a **stage-local overlay** on existing PPG stages. It does not create a new department, does not change the stage topology, does not dispatch workers, and does not own graph/manuscript/submission completion.

## Scope

Phase 11 covers:

- a generic stage-overlay registry framework with `nature_expert_writing` as the first profile;
- full canonical-stage bindings for `S00-S16/G01/G02`, with `S09A/S09B` split preserved and bare `S09` rejected;
- S03 restricted to support/light contribution-option use, gated through S04 before writing;
- StageContract metadata for every canonical stage through `stage_local_overlays`;
- strict worker TaskPacket overlay transport through `mandatory_controls` plus `stage_overlay:nature_expert_writing:<stage_id>` validators;
- Phase10 dry-run linkage in dispatch records, validation records, candidate placeholders, run-state, manifest, and per-run TaskPackets;
- local-paper stage coverage and frontend display of overlay bindings;
- positive and negative validator fixtures proving the overlay cannot become a department/self-certifying route.

## Core artifacts

- `docs/NATURE_STAGE_OVERLAY_SPEC.md`
- `runtime/stage_overlay_registry.json`
- `schemas/ppg-stage-overlay-registry.schema.json`
- `scripts/verify_stage_overlays.py`
- `examples/overlays/`
- `examples/stage-contracts/*.stage-contract.json`
- `examples/packets/*.yaml` for dispatchable worker stages
- `runtime/phase10_content_validators.json`
- `scripts/generate_phase10_run_dry_run.py`
- `scripts/verify_phase10_run_readiness.py`
- `scripts/verify_phase10_real_run_readiness.sh`
- `examples/local-paper/security-state-aware-mixed-platoon/stage_coverage.json`
- `docs/runtime-viewer/runtime-graph-data.js`

## Authority boundary

The overlay is valid only as a passive, stage-local expert-writing profile:

```text
stage_local_only=true
no_new_department=true
controller_owned_completion=true
worker_completion_forbidden=true
no_recursive_orchestration=true
overlay_dispatch_allowed=false
route_kind=stage_local_overlay
```

Subagents receive overlay clauses as part of their bounded TaskPacket. They return candidate outputs and evidence only.

## Verification

Focused gates:

```bash
python3 scripts/verify_stage_overlays.py
python3 scripts/generate_local_paper_full_pilot.py --pilot-root examples/local-paper/security-state-aware-mixed-platoon --check
python3 scripts/verify_phase9_frontend_stage_coverage.py
python3 scripts/generate_phase10_run_dry_run.py --check
python3 scripts/verify_phase10_run_readiness.py
```

Complete gate after committing the upgrade:

```bash
bash scripts/verify_phase10_real_run_readiness.sh
```

Expected terminal marker:

```text
PHASE10_REAL_RUN_READINESS_VERIFY_OK
```

The aggregate gate now includes Nature overlay validation and negative probes for missing dispatch overlay linkage and missing per-run TaskPacket overlay controls.

## Explicit non-goals

- This Phase11 overlay absorption itself did not perform live install, marketplace registration, publish, or cachebuster update; lifecycle changes require a separate owner-authorized replacement workflow.
- No replacement of the PPG runtime with legacy `$yxj-paper-os` department loops.
- No design dependency on `$yxj-plugin-incubator`.
- No claim that Nature overlay absorption means a real paper-production run has occurred.
- No final manuscript, submission-ready, or publication-ready claim.

## Next phase

A later phase can start a real full-flow subagent paper-production run. That run should consume the overlay-aware StageContracts, strict TaskPackets, Phase10 dry-run safety boundaries, and controller-owned validation/commit protocol.
