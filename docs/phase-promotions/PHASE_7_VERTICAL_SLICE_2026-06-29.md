# Phase 7 Promotion — Deterministic Overclaim Repair Vertical Slice

Date: 2026-06-29

## Status

Promoted after ralplan consensus and milestone-committed implementation.

Ralplan gate:

- Architect: `APPROVE` / `CLEAR` (`.omx/plans/phase7-vertical-slice-architect-review.md`)
- Critic: `APPROVE` / `CLEAR` (`.omx/plans/phase7-vertical-slice-critic-review.md`)

Implementation commits:

- `6ea613b` — `Promote phase seven section draft contract`
- `0cc7455` — `Promote phase seven deterministic workers`
- current promotion commit — `Promote phase seven vertical slice`

## Promotion claim

A single intro overclaim finding now causes a local repair loop:

```text
intro_draft_v1 overclaims universal safety
-> phase7 mock reviewer emits claim_overreach finding
-> compile_backflow maps the finding to active ClaimBoundaryMap repair target
-> propagate_stale marks only intro_writing_packet_v1 and intro_draft_v1 newly stale
-> compile_task_packet regenerates intro_writing_packet_v2
-> mock_writer returns intro_draft_v2 and CandidateArtifactReturn
-> mock_reviewer validates repaired draft and writes ReviewClosure + DeliveryGate
-> phase7 after graph records the closed loop without changing active claim_boundary_map_v2
```

## Delivered artifacts

### Section draft contract

- `schemas/ppg-section-draft.schema.json`
- `scripts/validate_section_draft.py`
- `examples/manuscript/intro.v1.md`
- `examples/candidate-artifacts/intro_draft.v2.md`
- section-draft negative fixtures under `examples/candidate-artifacts/invalid-section-draft-*.md`

### Deterministic workers and fixtures

- `scripts/mock_writer.py`
- `scripts/mock_reviewer.py`
- `examples/review_findings/phase7_overclaim.v1.yaml`
- `examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml`
- `examples/candidate_returns/intro_candidate_return.phase7.yaml`
- `examples/delivery/phase7_overclaim_closure.v1.yaml`
- `examples/delivery/phase7_delivery_gate.pass.yaml`
- blocked closure/gate negative fixtures under `examples/delivery/phase7_*blocked.yaml`

### Suite and graph state

- `scripts/run_fixture_suite.py`
- `examples/runtime/overclaim-loop.phase7-after.json`

## Key invariants

- Deterministic mock fixtures are the promotion gate; real subagent output is non-gating shadow evidence only.
- Main agent/controller owns graph completion. Workers/mocks return candidate artifacts and evidence only.
- `stale_set` in the suite means newly affected stale nodes, excluding nodes already stale before propagation.
- Expected newly affected stale set is exactly:
  - `intro_writing_packet_v1`
  - `intro_draft_v1`
- Active `claim_boundary_map` remains `claim_boundary_map_v2`; Phase7 does not commit a candidate material as active.
- Mock writer side-effect guard allows only `examples/candidate-artifacts/intro_draft.v2.md` to change during writer execution.

## Verification evidence

Commands run before promotion:

```bash
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
python3 scripts/validate_graph.py examples/runtime/overclaim-loop.phase7-after.json
bash scripts/verify_phase6_task_packets.sh
git diff --check -- .
```

Expected Phase7 suite signals:

```text
PHASE7_FIXTURE_SUITE_OK
stale_set: intro_draft_v1,intro_writing_packet_v1
writer_return_valid: true
closure_valid: true
delivery_gate_pass: true
after_graph_valid: true
```

## Deferred items

- No `$team` launch in Phase7.
- No plugin publish/install/marketplace step in Phase7.
- No mutation of old `$yxj-paper-os`.
- No `$yxj-plugin-incubator` design route.
- Real native subagent pilot remains optional non-gating shadow evidence after deterministic suite stability.
