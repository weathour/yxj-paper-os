# Phase 12 Promotion — Formal Full-Flow Runtime Test

Date: 2026-06-30

## Promotion decision

Phase 12 promotes `yxj-paper-os` from Phase10/11 readiness to a deterministic formal full-flow runtime-test harness.

This phase proves that the controller can create a run-owned full-stage flow over the local paper, record candidate/validation/dispatch/material/frontier/backflow/delivery ledgers, preserve source-read-only boundaries, and falsify its own safety claims through negative probes. It is not a manuscript-quality or submission-readiness claim.

## Scope

Phase 12 covers:

- a run-owned artifact tree under `runs/security-state-aware-mixed-platoon/phase12-formal-full-flow-runtime-test/`;
- all 20 canonical stages `S00-S16/G01/G02` with `S09A/S09B` preserved;
- one candidate artifact, dispatch record, validation record, stage status, and material record per canonical stage;
- strict run-owned TaskPackets for every dispatchable worker stage;
- independent source snapshot files `source_snapshot.before.json` and `source_snapshot.after.json` referenced by the manifest;
- a formal local backflow chain with exact events `review_finding_recorded -> backflow_task_compiled -> repair_candidate_recorded -> review_closure_recorded`;
- a delivery gate verdict `pass_for_runtime_test_only` that consumes all 20 stage records and the review closure;
- exact-code negative probes for source drift, bare `S09`, overlay link, candidate authority, worker authority, packet output boundary, owner-ledger tamper, overlay authority, doc boundary, and symlink refs.

## Core artifacts

- `scripts/generate_phase12_full_flow_run.py`
- `scripts/verify_phase12_full_flow_run.py`
- `scripts/verify_phase12_formal_full_flow.sh`
- `runs/security-state-aware-mixed-platoon/phase12-formal-full-flow-runtime-test/`
- `.omx/plans/phase12-formal-full-flow-runtime-test-plan.md`
- `.omx/plans/phase12-formal-full-flow-runtime-test-test-spec.md`

## Authority boundary

The run is controller-owned:

```text
candidate_only=true
controller_commit_required=true
worker_completion_forbidden=true
source_write_forbidden=true
no_recursive_orchestration=true
```

Nature writing expertise remains a passive stage-local overlay. It does not dispatch workers, become a department, or own graph/manuscript completion.

## Verification

Focused pre-commit checks:

```bash
python3 scripts/generate_phase12_full_flow_run.py --check
python3 scripts/verify_phase12_full_flow_run.py
python3 -m compileall -q scripts
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
git diff --check -- .
```

Full post-commit gate:

```bash
bash scripts/verify_phase12_formal_full_flow.sh
```

Expected terminal marker:

```text
PHASE12_FORMAL_FULL_FLOW_VERIFY_OK
```

## Explicit non-goals

- No source-paper repository writes.
- This Phase12 formal runtime test itself did not perform live install, marketplace registration, publish lifecycle, or cachebuster update; lifecycle changes require a separate owner-authorized replacement workflow.
- No replacement of the PPG runtime with old department loops.
- No design dependency on incubator routes.
- No journal-quality, final-paper, or submission-readiness claim.

## Next phase

A later phase can replace deterministic candidates with live subagent returns while retaining the Phase12 verifier, source-safety boundary, local backflow chain, and controller-owned delivery gate.
