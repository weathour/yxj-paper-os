# Phase 10 Promotion — Real Subagent Run Readiness

Date: 2026-06-30

## Promotion decision

Phase 10 promotes `yxj-paper-ppg-runtime` from full-stage pilot coverage to real-subagent-run readiness.

This phase does **not** start a formal paper-production run, does **not** produce a final manuscript, and does **not** claim submission readiness. It proves that the plugin/runtime can safely prepare a later full-flow subagent execution campaign under main-agent control.

## Scope

Phase 10 covers:

- strict linked TaskPackets for every dispatchable worker stage;
- semantic packet-stage binding through `stage_id` and `stage_contract_ref`;
- content validator registry for every canonical stage;
- runtime-owned dry-run fixture under `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`;
- untracked-aware source-read-only snapshot proof;
- forbidden-side-effect guard for old-runtime, incubator, live lifecycle, and false-readiness boundaries;
- aggregate verification over Phase10 plus inherited Phase9/8/7/6 gates.

## Worker packet readiness

After Phase 10:

- `linked_strict_packet=12`
- `planned_with_blocker=0`
- `not_required=8`

Every dispatchable stage has a strict packet and every non-worker stage remains non-worker. Subagents still do not own graph completion, manuscript completion, recursive dispatch, source repository writes, or owner-intent changes.

## Dry-run boundary

The Phase10 dry-run fixture records dispatch, validation, candidate-placeholder, ledger, and run-state evidence. It is a controller/readiness fixture, not worker-produced content.

The source paper repository remains read-only. The verifier recomputes a source snapshot that includes untracked files, so mutation inside existing untracked source paths is detectable.

## Core artifacts

- `runtime/phase10_content_validators.json`
- `schemas/ppg-run-state.schema.json`
- `scripts/generate_phase10_run_dry_run.py`
- `scripts/verify_phase10_run_readiness.py`
- `scripts/verify_phase10_forbidden_side_effects.py`
- `scripts/verify_phase10_real_run_readiness.sh`
- `runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/`
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

The aggregate gate includes positive checks and negative probes for wrong-stage packet binding, missing validator dimensions, source-contained output, symlink run roots, untracked source snapshot drift, bare `S09`, final/submission overclaim, misleading success markers, inherited gates, plugin validation, skill validation, Python compilation, whitespace checks, and clean-worktree assertion.

## Explicit non-goals

- Forbidden boundary: do not mutate or revive old `$yxj-paper-os` as an operating model.
- Forbidden boundary: do not use `$yxj-plugin-incubator` as a design source or active route.
- Live install: not enabled.
- Marketplace registration: not enabled.
- Publish/cachebuster lifecycle: not enabled.
- No final manuscript or submission-ready claim.

## Next phase

A later phase may start a real full-flow subagent paper-production run. That run should consume Phase10 TaskPackets, content validators, dry-run state, and main-agent completion rules, and it should still write candidate outputs to a controlled runtime/run area before any owner-approved source-repository patch.
