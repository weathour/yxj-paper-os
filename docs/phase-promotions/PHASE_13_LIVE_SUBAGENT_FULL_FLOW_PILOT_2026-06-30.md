# Phase 13 Promotion — Live Native-Subagent Full-Flow Pilot

Date: 2026-06-30

## Promotion decision

Phase 13 promotes `yxj-paper-os` from a deterministic formal full-flow runtime-test harness to a **live native-subagent full-flow pilot**.

This phase proves that the main agent can plan and dispatch bounded task packets to real Codex native subagents for every canonical paper-production stage, collect raw producer returns, dispatch independent verifier subagents, ingest the paired results into run-owned stage-effect and validation records, and pass safety/negative verification gates. It remains a runtime pilot only; it is not a final manuscript, submission-readiness, or publication-readiness claim.

## Scope

Phase 13 covers:

- a run-owned artifact tree under `runs/security-state-aware-mixed-platoon/phase13-live-subagent-full-flow-pilot/`;
- all 20 canonical stages `S00-S16/G01/G02`, preserving the split `S09A/S09B` stages;
- 40 native-subagent lanes: one producer lane plus one independent verifier lane per stage;
- explicit producer/verifier task packets and dispatch prompts for every stage;
- raw native-subagent return files for every producer and verifier lane;
- per-stage effect records and live-validation records generated from the paired returns;
- a `subagent_threads.json` provenance ledger with unique thread ids, role names, raw-return hashes, prompt hashes, packet hashes, and native-subagent flags;
- source-read-only snapshot comparison before/after/current against the local paper source root;
- final-state source snapshot equality as the Phase 13 source-write proof; it does not claim process-level immutable mounts for subagent processes;
- delivery gate verdict `pass_for_live_runtime_pilot_only` with 20 `accept_with_limitations`, 0 `needs_repair`, and 0 `reject` outcomes;
- exact-code negative probes for missing returns, duplicate thread ids, weak/generic returns, missing packet citation, verifier parroting, worker-role misuse, authority-mode mismatch, unauthorized-route activation, recursive orchestration claims, rejected stages, unresolved repairs, and source snapshot drift, non-worker agent-type mismatch, exact thread-coverage loss, verifier producer-return grounding tamper, missing/tampered dispatch and validation ledgers, dispatch authority tamper, raw verifier verdict tamper, validation status mismatch, effect/controller-acceptance mismatch, and missing dispatch records.

## Double-agent stage model

Each stage is exercised with a two-lane contract:

1. **Producer subagent** consumes the stage producer packet and emits a stage-local candidate/effect assessment.
2. **Verifier subagent** consumes the verifier packet plus the producer return and emits an independent verdict and critique.

The verifier does not become the controller. Every verifier return is evidence for the main-agent/controller delivery gate, not a controller-owned completion decision.

The per-stage effect scores are pilot triage scores derived from bounded return properties and verifier verdicts. They support controller routing and repair-locality inspection, but they are not manuscript-quality metrics and do not certify semantic paper progress.

## Authority boundary

The live pilot is controller-owned:

```text
source_write_forbidden=true
controller_owned_completion=true
worker_completion_forbidden=true
no_recursive_orchestration=true
leader_summary_only=false
native_subagent=true
```

Stages that do not require worker task packets remain `assessment_only`: `S00`, `S01`, `S09A`, `S09B`, `S14`, `S16`, `G01`, and `G02`.

The term "zero trust" remains scoped to the local paper's controller-side zero-default authority for degraded V2X evidence. Phase 13 keeps controller-owned completion and source-read-only boundaries.

## Core artifacts

- `scripts/generate_phase13_live_pilot.py`
- `scripts/record_phase13_subagent_return.py`
- `scripts/ingest_phase13_live_pilot.py`
- `scripts/verify_phase13_live_subagent_pilot.py`
- `scripts/verify_phase13_live_subagent_pilot.sh`
- `runs/security-state-aware-mixed-platoon/phase13-live-subagent-full-flow-pilot/`

## Verification

Focused checks:

```bash
python3 scripts/generate_phase13_live_pilot.py --run-root runs/.phase13-negative-scaffold-probe --check
python3 scripts/ingest_phase13_live_pilot.py
python3 scripts/verify_phase13_live_subagent_pilot.py
python3 -m compileall -q scripts
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
git diff --check -- .
```

Full post-commit gate:

```bash
bash scripts/verify_phase13_live_subagent_pilot.sh
```

Expected terminal marker:

```text
PHASE13_LIVE_SUBAGENT_PILOT_VERIFY_OK
```

## Explicit non-goals

- No source-paper repository writes.
- No process-level immutable source mount claim; Phase 13 proves final-state source snapshot equality only.
- Phase 13 itself did not perform plugin install, marketplace registration, publish lifecycle, or cachebuster update; those lifecycle actions belong to a separate owner-authorized replacement workflow.
- No production-grade semantic scoring claim; Phase 13 effect scores are pilot-only triage evidence.
- No final manuscript, final paper, submission-readiness, or publication-readiness claim.
- No verifier-owned or worker-owned completion authority.
- No recursive subagent orchestration by stage lanes.
- Only controller-authorized PPG runtime routes are active routes.

## Next phase

A later phase can harden live-run UX and controller ergonomics: richer live dispatch dashboards, resumable run state, stricter stage-specific artifact completeness scoring, and optional owner-gated progression from runtime-pilot evidence into controlled manuscript patch proposals.
