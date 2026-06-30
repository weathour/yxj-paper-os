# Phase 9 Promotion — Full-Stage Local Paper Pilot

Date: 2026-06-30

## Promotion decision

Phase 9 is promoted as the first full-stage coverage baseline for `yxj-paper-os`.

This phase does **not** claim that a paper has been fully written, reviewed, or made submission-ready. It claims that the runtime now has a verified full-stage local-paper pilot surface: every canonical stage has a StageContract, a PilotStageRun record, produced pilot artifacts, validator evidence, and an explicit completion boundary.

## Scope

Phase 9 covers:

- archival guard for old `$yxj-paper-os` design provenance;
- canonical stage registry for `S00, S01, S02, S03, S04, S05, S06, S07, S08, S09A, S09B, S10, S11, S12, S13, S14, S15, S16, G01, G02`;
- StageContract fixtures for all canonical stages;
- read-only import/projection of the local paper repository `security-state-aware-mixed-platoon`;
- one PilotStageRun per canonical stage;
- frontend Stage Coverage mode for human inspection;
- aggregate verification wrapper for Phase 9 plus inherited Phase 8/7/6 gates.

## Core artifacts

- `runtime/stage_registry.json`
- `schemas/ppg-stage-contract.schema.json`
- `schemas/ppg-pilot-stage-run.schema.json`
- `examples/stage-contracts/*.stage-contract.json`
- `examples/local-paper/security-state-aware-mixed-platoon/manifest.json`
- `examples/local-paper/security-state-aware-mixed-platoon/stage_coverage.json`
- `examples/local-paper/security-state-aware-mixed-platoon/graph.json`
- `examples/local-paper/security-state-aware-mixed-platoon/stage-runs/*.pilot-stage-run.json`
- `examples/local-paper/security-state-aware-mixed-platoon/artifacts/*.json`
- `scripts/import_local_paper_pilot.py`
- `scripts/generate_local_paper_full_pilot.py`
- `scripts/verify_local_paper_full_pilot.py`
- `scripts/verify_phase9_frontend_stage_coverage.py`
- `scripts/verify_phase9_full_stage_runtime.sh`

## Pilot coverage summary

Current coverage summary from `stage_coverage.json`:

- canonical stages: 20
- PilotStageRun records: 20
- coverage kinds: `source_projected=10`, `script_checked=5`, `fixture_generated=4`, `owner_gated_deferred=1`
- exercise levels: `full_stage_exercised=9`, `contract_only=10`, `deferred_with_gate=1`
- worker task packet status: `linked_strict_packet=2`, `planned_with_blocker=10`, `not_required=8`

This is intentionally honest: Phase 9 proves full-stage runtime coverage and local-paper projection, not that all future worker subagent task packets are already implemented.

## Boundaries

- The source paper repository is read-only pilot input.
- Pilot artifacts are written under this runtime repository, not inside the source paper repository.
- `S09` remains forbidden; `S09A` and `S09B` are distinct control-material selection and task-packet assembly stages.
- Worker stages may be `linked_strict_packet` or `planned_with_blocker`; non-worker stages must not fake worker packets.
- This Phase9 promotion itself did not perform plugin install, marketplace registration, cachebuster update, or public `yxj-paper-os` replacement; lifecycle changes require a separate owner-authorized replacement workflow.
- The frontend is an observability surface, not a graph commit surface.

## Verification

Run the complete Phase 9 gate:

```bash
bash scripts/verify_phase9_full_stage_runtime.sh
```

The wrapper verifies:

1. legacy archive guard;
2. stage registry and StageContract fixtures;
3. read-only local-paper import;
4. generated full-stage PilotStageRun coverage;
5. frontend Stage Coverage sync and safe-DOM guard;
6. runtime adapter optional `--stage-coverage` JSON/Markdown output;
7. inherited Phase 7 fixture suite;
8. inherited Phase 8 plugin/frontend runtime surface gate;
9. inherited Phase 6 strict task-packet gate;
10. plugin and skill validators;
11. frontend JavaScript syntax and whitespace diff check.

Expected terminal marker:

```text
PHASE9_FULL_STAGE_RUNTIME_VERIFY_OK
```

## Remaining work after Phase 9

- Convert `planned_with_blocker` worker stages into linked strict task packets as later milestones, prioritizing stages that materially affect real writing/review execution.
- Add richer per-stage validators when real paper-writing artifacts replace pilot projections.
- Keep the main-agent controller as the only completion authority; subagents return candidates and evidence, not global completion claims.
