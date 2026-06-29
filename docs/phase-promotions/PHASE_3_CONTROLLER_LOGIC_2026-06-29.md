# Phase 3 Promotion Record — Main-Agent Controller Logic

Date: 2026-06-29  
Status: promoted after strict Autopilot/Ralplan consensus, implementation validation, and dry-run runtime QA.  
Precondition: Phase 2 executable material graph core promoted in `PHASE_2_EXECUTABLE_MATERIAL_GRAPH_CORE_2026-06-29.md`.

## Claim

Phase 3 is complete for implementation purposes.

The repository now has a dependency-free dry-run main-agent controller layer over the executable material graph. Given a graph state, the controller can report material status, select the next frontier, explain why it is next, expose owner-gated blockers, and dry-run candidate commit readiness without mutating the graph.

## Autopilot / Ralplan evidence

User constraints for this phase:

- use `$oh-my-codex:autopilot`;
- strictly pass through ralplan;
- do not open `$team`;
- if milestones are used, each milestone must be committed.

Execution contract used one Phase 3 total milestone, so the phase receives one final commit after all gates.

Ralplan artifacts:

- `.omx/plans/phase3-controller-logic-plan.md`
- `.omx/plans/phase3-controller-logic-test-spec.md`

Review sequence before implementation:

1. Architect review: `ITERATE/WATCH`.
   - Required frontier policy alignment with `docs/RUNTIME_PROTOCOL.md`.
   - Required an unsuperseded stale fixture.
   - Required explicit `owner_decision` graph support.
2. Architect re-review: `APPROVE/CLEAR`.
3. Critic review: `ITERATE/WATCH`.
   - Required owner-gated `report` coverage.
   - Required command-level no-mutation proof.
   - Required positive `commit-plan` fixture.
   - Required mandatory controller report fixtures.
   - Required stale fixture wording to preserve committed-only `active_versions`.
4. Architect re-review: `APPROVE/CLEAR`.
5. Critic re-review: `ITERATE/WATCH`.
   - Required no-mutation proof for the positive commit-ready path as well as the negative path.
6. Architect re-review: `APPROVE/CLEAR`.
7. Critic re-review: `APPROVE/CLEAR`.

Implementation began only after the final Architect -> Critic approval sequence.

First code-review result after implementation:

- code-reviewer: `REQUEST CHANGES`;
- architect: `WATCH`;
- findings: stale frontier predicate was too broad, missing-task-packet branch was unreachable for valid graphs, candidate provenance could be satisfied by validation-report references, and owner-decision artifact/schema validation should be tightened.

Rework result:

- stale frontier now requires a hard active dependency/control path (`consumes` / `constrains`, not weak `references`), not merely stale status;
- planned manuscript artifacts with `needs_task_packet: true` are valid missing-task placeholders;
- candidate provenance excludes validation-report references and requires distinct `produces` / `consumes` / `constrains` evidence;
- owner-decision artifacts receive dependency-free required-field validation through `validate_graph.py`;
- additional positive/negative fixtures prove those branches.

## Added / changed artifacts

Controller CLI:

- `scripts/ppg_store.py`
  - existing `inspect` preserved;
  - added `report`;
  - added `frontier`;
  - added `commit-plan` dry-run.

Graph/schema support:

- `schemas/ppg-graph.schema.json`
  - adds `owner_decision` node type.
- `scripts/validate_graph.py`
  - allows `owner_decision` node type.
- `schemas/ppg-owner-decision.schema.json`
  - minimal Phase 3 owner decision record contract.

Runtime fixtures:

- `examples/runtime/owner-gated-decision.json`
- `examples/runtime/stale-upstream-control.json`
- `examples/runtime/disconnected-stale-material.json`
- `examples/runtime/weak-reference-stale-material.json`
- `examples/runtime/missing-task-packet.json`
- `examples/runtime/commit-ready-candidate.json`
- `examples/runtime/commit-ready-missing-provenance.json`
- `examples/runtime/invalid-owner-decision-artifact.json`
- `examples/owner-decisions/contribution-strength.v1.json`
- `examples/owner-decisions/invalid-missing-question.json`
- `examples/materials/terminology_register.v1.yaml`
- `examples/materials/claim_boundary_map.v3-ready.yaml`
- `examples/validator-reports/claim_boundary_map.v3-ready.json`

Controller report fixtures:

- `examples/controller-reports/overclaim-loop.report.v1.txt`
- `examples/controller-reports/owner-gated-decision.report.v1.txt`

Documentation:

- `README.md`
- `docs/PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md`

## Promoted controller semantics

### Controller report

`report` produces stable plain-text sections:

```text
graph_id
active_versions
committed_materials
candidate_materials
stale_materials
blocked_items
owner_gated_items
open_review_findings
next_frontier
completion_blockers
```

Report fixtures are mandatory exact-output contracts for Phase 3.

### Frontier selection

MVP priority order:

```text
owner-gated root decision
> unsuperseded stale upstream control material on the active dependency/control path
> blocked validator/material prerequisite
> missing task-packet placeholder
> candidate material awaiting validation/commit planning
> review finding awaiting classification
> export/rendering blocker
> no runnable frontier
```

Historical stale rule:

- a stale material already superseded by the material's active committed node remains visible in `report`;
- it does not become the frontier.

Fixtures prove:

- `overclaim-loop.v1.json` selects `claim_boundary_map_candidate_v3` because `claim_boundary_map_v1` is historical stale already superseded by active `claim_boundary_map_v2`;
- `owner-gated-decision.json` selects `owner_decision_contribution_strength_v1` before autonomous candidate work;
- `stale-upstream-control.json` selects `terminology_register_v1`, proving the implementation does not ignore all stale materials.

### Candidate commit plan

`commit-plan` is dry-run only. It never mutates the graph.

It reports:

```text
candidate
material_id
active_node
candidate_status
can_commit
missing_requirements
would_update_active_versions
event_log_preview
```

Readiness checks include:

- concrete material candidate node exists;
- candidate is validated before commit;
- `candidate_for` names the target logical material;
- target material has an active committed node;
- candidate declares `supersedes` active node;
- matching `supersedes` edge exists;
- candidate-specific validator edge exists;
- candidate-specific validation-report reference exists;
- candidate provenance exists.

Fixtures prove both directions:

- `overclaim-loop.v1.json` / `claim_boundary_map_candidate_v3` returns `can_commit: false` with missing requirements;
- `commit-ready-candidate.json` / `claim_boundary_map_candidate_v3_ready` returns `can_commit: true` and prints a dry-run `would_update_active_versions` preview;
- a committed non-candidate node returns `can_commit: false`.

### Owner decision visibility

`owner_decision` is intentionally minimal in Phase 3. It exists so the controller can surface owner-gated semantic decisions as graph state. It is not a full queue runtime and does not implement owner interview UX. The graph validator performs a minimal dependency-free check that owner-decision artifacts exist and contain the required Phase 3 fields.

## Validation evidence

Fresh validation command group:

```bash
python3 -m py_compile scripts/validate_graph.py scripts/ppg_store.py
python3 -m ruff check scripts/validate_graph.py scripts/ppg_store.py
pyright scripts/validate_graph.py scripts/ppg_store.py
python3 scripts/validate_graph.py examples/runtime/overclaim-loop.v1.json
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
python3 scripts/validate_graph.py examples/runtime/owner-gated-decision.json
python3 scripts/validate_graph.py examples/runtime/stale-upstream-control.json
python3 scripts/validate_graph.py examples/runtime/disconnected-stale-material.json
python3 scripts/validate_graph.py examples/runtime/weak-reference-stale-material.json
python3 scripts/validate_graph.py examples/runtime/missing-task-packet.json
python3 scripts/validate_graph.py examples/runtime/commit-ready-candidate.json
python3 scripts/validate_graph.py examples/runtime/commit-ready-missing-provenance.json
for f in examples/runtime/invalid-*.json; do ! python3 scripts/validate_graph.py "$f"; done
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map_v1
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map_candidate_v3
python3 scripts/ppg_store.py report examples/runtime/overclaim-loop.v1.json
python3 scripts/ppg_store.py report examples/runtime/owner-gated-decision.json
python3 scripts/ppg_store.py frontier examples/runtime/overclaim-loop.v1.json
python3 scripts/ppg_store.py frontier examples/runtime/owner-gated-decision.json
python3 scripts/ppg_store.py frontier examples/runtime/stale-upstream-control.json
python3 scripts/ppg_store.py frontier examples/runtime/disconnected-stale-material.json
python3 scripts/ppg_store.py frontier examples/runtime/weak-reference-stale-material.json
python3 scripts/ppg_store.py frontier examples/runtime/missing-task-packet.json
python3 scripts/ppg_store.py commit-plan examples/runtime/overclaim-loop.v1.json --candidate claim_boundary_map_candidate_v3
python3 scripts/ppg_store.py commit-plan examples/runtime/commit-ready-candidate.json --candidate claim_boundary_map_candidate_v3_ready
python3 scripts/ppg_store.py commit-plan examples/runtime/commit-ready-missing-provenance.json --candidate claim_boundary_map_candidate_v3_ready
python3 scripts/ppg_store.py commit-plan examples/runtime/overclaim-loop.v1.json --candidate claim_boundary_map_v2
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Observed result:

```text
py_compile: passed
ruff: All checks passed
pyright executable: `0 errors, 0 warnings, 0 informations`
JSON parse: all schemas and examples parsed
valid graph fixtures: VALID, including disconnected-stale, missing-task, commit-ready, and missing-provenance controller fixtures
invalid graph fixtures: all rejected as expected, including invalid owner-decision artifact
inspect regression: logical active, old concrete, and candidate concrete lookups passed
report fixture diffs: passed
frontier overclaim: claim_boundary_map_candidate_v3 / candidate_material_awaiting_validation_or_commit_plan
frontier owner-gated: owner_decision_contribution_strength_v1 / owner_gated_root_decision
frontier stale-upstream: terminology_register_v1 / unsuperseded_stale_upstream_control
frontier disconnected stale: claim_boundary_map_candidate_v3 / candidate_material_awaiting_validation_or_commit_plan
frontier weak-reference stale: claim_boundary_map_candidate_v3 / candidate_material_awaiting_validation_or_commit_plan
frontier missing task: methods_draft_placeholder_v1 / missing_task_packet_for_active_manuscript_unit
commit-plan negative: can_commit false with missing supersedes/report/validator requirements
commit-plan positive: can_commit true with dry-run active-version update preview
commit-plan missing provenance: can_commit false with distinct candidate provenance requirement
commit-plan non-candidate: can_commit false
no-mutation proof: sha256 before/after and git diff checks passed for negative and positive paths
plugin validation: passed
```

## Review and QA gate

Code-review gate:

```text
first code-review: REQUEST CHANGES / WATCH
rework: stale frontier restricted to hard active dependency/control edges, missing-task placeholder made valid, provenance separated from validation-report references, owner-decision artifact checks added
second code-review: REQUEST CHANGES / CLEAR
final rework: weak references excluded from stale frontier traversal; weak-reference stale fixture added
final code-reviewer: APPROVE, total issues 0
final architect: CLEAR
final recommendation: APPROVE/CLEAR
```

UltraQA disposition:

```text
status: skipped-as-separate-interactive-run
reason: Phase 3 is a dependency-free local CLI/runtime surface with no live frontend, browser UI, external service, or production integration.
substitute QA evidence: adversarial CLI fixture suite covering owner-gated priority, historical stale, active-path stale, disconnected stale, weak-reference stale, missing task packet, negative/positive commit-plan, missing provenance, non-candidate rejection, invalid owner-decision artifact, report fixture exact diffs, and no-mutation hash/diff checks.
result: clean
```

## Known limits

Phase 3 still does not implement:

- graph mutation / real commit command;
- persistent event store;
- stale propagation engine;
- local backflow compiler;
- task-packet compiler;
- real subagent dispatch;
- owner interview UI;
- frontend runtime state view.

These are later-phase responsibilities.

## Next phase start state

Phase 4 may start from this promoted controller baseline.

Expected next focus:

- material schemas and validators for high-priority paper-production material families;
- review finding / backflow task / review closure / delivery gate schemas;
- stricter validator failure codes and schema-level report contracts.
