# Phase 10 Promotion — Real Subagent Run Readiness

Date: 2026-06-30

## Promotion decision

Phase 10 promotes `yxj-paper-os` from full-stage pilot coverage to real-subagent-run readiness.

This phase does **not** start a formal paper-production run, does **not** produce a final manuscript, and does **not** claim submission readiness. It proves that the plugin/runtime can safely prepare a later full-flow subagent execution campaign under main-agent control.

## Scope

Phase 10 covers:

- strict linked TaskPacket templates for every dispatchable worker stage;
- run-owned TaskPacket materialization for dispatchable worker stages;
- semantic packet-stage binding through `stage_id` and `stage_contract_ref`;
- content validator registry for every canonical stage;
- runtime-owned dry-run fixture under `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`;
- source-read-only filesystem snapshot proof excluding `.git/.omx` runtime state;
- forbidden-side-effect guard for unapproved-runtime, external route, live lifecycle, and false-readiness boundaries;
- aggregate verification over Phase10 plus inherited Phase9/8/7/6 gates.

## Worker packet readiness

After Phase 10:

- `linked_strict_packet=12`
- `planned_with_blocker=0`
- `not_required=8`

Every dispatchable stage has a strict template packet, and the Phase10 dry-run materializes a per-run packet whose allowed write path is the run-owned candidate artifact. Every non-worker stage remains non-worker. Subagents still do not own graph completion, manuscript completion, recursive dispatch, source repository writes, or owner-intent changes.

## Dry-run boundary

The Phase10 dry-run fixture records dispatch, validation, candidate-placeholder, per-run TaskPacket, ledger, and run-state evidence. It is a controller/readiness fixture, not worker-produced content.

The source paper repository remains read-only. The verifier recomputes a source filesystem snapshot below the paper source root, excluding `.git/.omx` runtime state, so tracked, untracked, ignored, directory, and symlink mutations in paper content paths are detectable.

## Core artifacts

- `runtime/phase10_content_validators.json`
- `schemas/ppg-run-state.schema.json`
- `scripts/generate_phase10_run_dry_run.py`
- `scripts/verify_phase10_run_readiness.py`
- `scripts/verify_phase10_forbidden_side_effects.py`
- `scripts/verify_phase10_real_run_readiness.sh`
- `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`
- `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/packets/*.task-packet.json`
- `examples/packets/phase10_*.yaml`

## Verification

Run the complete Phase10 gate:

```bash
bash scripts/verify_phase10_real_run_readiness.sh
```

Expected terminal marker:

```text
PHASE10_REAL_RUN_READINESS_VERIFY_OK
```

The aggregate gate includes positive checks and negative probes for wrong-stage packet binding, missing validator dimensions, source-contained output, symlink run roots, source snapshot drift, wrong source-root binding, dispatch/validation/candidate tampering, run-packet output escape, bare `S09`, final/submission overclaim, misleading success markers, inherited gates, plugin validation, skill validation, Python compilation, whitespace checks, and clean-worktree assertion.

## Explicit non-goals

- Boundary: do not activate the controller-bypassing route behavior.
- Boundary: only controller-authorized PPG runtime routes are active.
- Local plugin install/cachebuster lifecycle: enabled only through explicit owner-authorized plugin maintenance; this promotion itself remains a runtime-readiness gate, not a publication/submission claim.
- Marketplace registration: not enabled.
- Publish/cachebuster lifecycle: not enabled.
- No final manuscript or submission-ready claim.

## Next phase

A later phase may start a real full-flow subagent paper-production run. That run should consume Phase10 TaskPackets, content validators, dry-run state, and main-agent completion rules, and it should still write candidate outputs to a controlled runtime/run area before any owner-approved source-repository patch.
