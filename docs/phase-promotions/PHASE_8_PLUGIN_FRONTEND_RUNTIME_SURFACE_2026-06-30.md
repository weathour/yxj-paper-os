# Phase 8 Promotion — Plugin / Frontend Runtime Surface

Date: 2026-06-30

## Status

Promoted after strict `$autopilot` flow:

```text
deep-interview -> ralplan -> ultragoal -> code-review -> ultraqa
```

Ralplan gate:

- Architect: `APPROVE` / `CLEAR` (`.omx/plans/phase8-plugin-frontend-runtime-surface-architect-review.md`)
- Critic: `APPROVE` / `CLEAR` (`.omx/plans/phase8-plugin-frontend-runtime-surface-critic-review.md`)

Implementation commits:

- `19c0987` — `Promote phase eight runtime adapter`
- `8b1c034` — `Promote phase eight frontend state surface`
- current promotion commit — `Promote phase eight plugin manager surface`

## Promotion claim

The repository now exposes the proven PPG runtime through a local, non-publishing plugin/frontend surface:

```text
Phase7 after graph
-> read-only runtime adapter validates graph
-> deterministic JSON/Markdown state reports
-> frontend Runtime State mode shows graph/frontier/stale/candidate/review/backflow/owner/delivery/blocker panels
-> one public manager skill describes safe operation and validation gates
```

## Delivered artifacts

### Runtime adapter and reports

- `scripts/ppg_runtime_adapter.py`
- `examples/runtime-reports/overclaim-loop.phase7-state.json`
- `examples/runtime-reports/overclaim-loop.phase7-state.md`
- `scripts/verify_phase8_plugin_surface.sh`

The adapter reports:

- graph id/title/source/counts;
- active material versions;
- next frontier;
- stale materials;
- candidate materials;
- owner decisions;
- open review findings;
- backflow tasks;
- delivery gates;
- review closures;
- completion blockers.

### Frontend state surface

- `docs/runtime-viewer/runtime-graph-data.js` now includes `runtimeState` from the adapter report.
- `docs/runtime-viewer/index.html` adds `Runtime State` mode.
- `docs/runtime-viewer/app.js` renders runtime-state values with DOM `textContent` / created elements, not `runtimeStateContent.innerHTML`.
- `docs/runtime-viewer/styles.css` adds state cards/panels for owner-facing inspection.

### Plugin manager surface

- `.codex-plugin/plugin.json` describes the Phase8 local runtime-surface capability with valid manifest fields.
- `skills/yxj-paper-ppg-runtime/SKILL.md` is the one public manager entry and records safe operating boundaries.
- `README.md` records Phase8 promoted status and the new adapter/frontend artifacts.

## Key invariants

- This is a local development surface, not a live plugin install or marketplace publication.
- The runtime remains `Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch`.
- Internal graph-operation lanes are hidden from the public plugin surface.
- Adapter output is read-only inspection evidence; it does not mutate graph state.
- Frontend state is owner observability; it is not a commit surface.
- Completion remains controller-owned and validator-backed.

## Verification evidence

Commands run before promotion:

```bash
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-ppg-runtime
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
bash scripts/verify_phase6_task_packets.sh
bash scripts/verify_phase8_plugin_surface.sh
git diff --check -- .
```

Expected Phase8 wrapper signals:

```text
PHASE8_JSON_ASSERTIONS_OK
PHASE8_MARKDOWN_ASSERTIONS_OK
PHASE8_PLUGIN_SURFACE_VERIFY_OK
```

Expected inherited suite signals:

```text
PHASE7_FIXTURE_SUITE_OK
PHASE6_TASK_PACKET_VERIFY_OK
```

## Deferred items

- No live plugin install.
- No marketplace registration or cachebuster update.
- No mutation of old `$yxj-paper-os`.
- No `$yxj-plugin-incubator` route.
- No `$team` launch.
- Future live graph import/server/marketplace work requires explicit owner approval.
