# Phase 2 Promotion Record — Executable Material Graph Core

Date: 2026-06-29  
Status: promoted after Autopilot/Ralplan consensus and implementation validation.  
Precondition: Phase 1 abstract model freeze promoted in `PHASE_1_ABSTRACT_MODEL_FREEZE_2026-06-29.md`.

## Claim

Phase 2 is complete for implementation purposes.

The repository now has a dependency-free executable material graph core that can load a runtime graph, resolve a logical material id to its active committed version, inspect direct dependencies, preserve superseded versions, represent `supersedes` explicitly, separate candidates from active committed material, and reject invalid endpoint or active-version references.

## Autopilot / Ralplan evidence

Deep-interview was skipped because the task was already bounded by:

- the promoted Phase 1 baseline;
- the Phase 2 roadmap;
- explicit deliverables and validation commands;
- no pending human semantic decision.

Ralplan artifacts were written under `.omx/plans/` during the run:

- `phase2-executable-material-graph-plan.md`
- `phase2-executable-material-graph-test-spec.md`

Review sequence:

1. Architect initial review: `ITERATE`.
   - Required committed-only active versions.
   - Required active-candidate negative test.
   - Required scoped artifact existence checks.
   - Required canonical `supersedes` semantics.
2. Architect re-review: `APPROVE`.
3. Critic review: `APPROVE`.

The final implementation follows those review constraints.

## Added artifacts

Schemas:

- `schemas/ppg-material.schema.json`
- `schemas/ppg-transform-task.schema.json`
- `schemas/ppg-validator-report.schema.json`
- updated `schemas/ppg-graph.schema.json` with runtime material fields and `active_versions`

Runtime scripts:

- `scripts/ppg_store.py`
- extended `scripts/validate_graph.py`

Runtime examples:

- `examples/runtime/overclaim-loop.v1.json`
- `examples/runtime/invalid-missing-endpoint.json`
- `examples/runtime/invalid-active-version.json`
- `examples/runtime/invalid-active-candidate.json`
- `examples/runtime/invalid-supersedes-reversed.json`
- `examples/runtime/invalid-supersedes-disagreement.json`

Payload fixtures:

- `examples/materials/evidence_inventory.v1.yaml`
- `examples/materials/claim_boundary_map.v1.yaml`
- `examples/materials/claim_boundary_map.v2.yaml`
- `examples/materials/claim_boundary_map.v3-candidate.yaml`
- `examples/materials/reader_spine.v1.yaml`
- `examples/validator-reports/claim_boundary_map.v2.json`

## Promoted runtime semantics

### Active material versions

`active_versions` maps logical material ids to concrete material node ids:

```json
"active_versions": {
  "claim_boundary_map": "claim_boundary_map_v2"
}
```

A target must be:

- an existing node;
- `node_type: material`;
- matching `material_id`;
- `status: committed`.

It must not be candidate, validated-only, stale, rejected, missing, or another node type.

### Supersedes

Canonical direction:

```text
new material version -> old material version
```

Example:

```text
claim_boundary_map_v2 --supersedes--> claim_boundary_map_v1
```

Every `supersedes` edge must use the new-version -> old-version direction. The source material node must declare `supersedes` equal to the edge target. Reversed edges and node-level / edge-level disagreement are invalid. Supersedes must connect material nodes with the same `material_id`.

### Candidate separation

Candidate material versions may exist in the graph, but they cannot be active. The fixture `invalid-active-candidate.json` proves the validator rejects candidate activation.

### Compatibility boundary

Current/minimal graph examples remain valid. Artifact existence checks are scoped to Phase 2 runtime fixture paths under `examples/materials/`, so old documentation handles such as `materials/foo.yaml` do not force new files.

## Validation evidence

Fresh validation commands:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
python3 scripts/validate_graph.py examples/runtime/overclaim-loop.v1.json
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map_v2
python3 scripts/ppg_store.py inspect examples/runtime/overclaim-loop.v1.json --node claim_boundary_map_v1
python3 scripts/validate_graph.py examples/runtime/invalid-missing-endpoint.json
python3 scripts/validate_graph.py examples/runtime/invalid-active-version.json
python3 scripts/validate_graph.py examples/runtime/invalid-active-candidate.json
python3 scripts/validate_graph.py examples/runtime/invalid-supersedes-reversed.json
python3 scripts/validate_graph.py examples/runtime/invalid-supersedes-disagreement.json
```

Observed result:

```text
VALID examples/minimal-paper-production-graph.json
VALID examples/runtime/overclaim-loop.v1.json
inspect by logical id: exit 0, active_node claim_boundary_map_v2
inspect by active node id: exit 0, selected_node claim_boundary_map_v2
inspect by old node id: exit 0, selected_node claim_boundary_map_v1, active_node claim_boundary_map_v2
INVALID invalid-missing-endpoint: missing endpoint rejected
INVALID invalid-active-version: missing active target rejected
INVALID invalid-active-candidate: active candidate rejected
INVALID invalid-supersedes-reversed: old -> new supersedes edge rejected
INVALID invalid-supersedes-disagreement: node-level / edge-level supersedes disagreement rejected
```


## Independent review and QA gate

Code-review gate:

```text
code-reviewer re-review: APPROVE
architectural_status: CLEAR
blocking findings: none
validation coverage: adequate for Phase 2 approval
```

Architecture-invariant gate:

```text
architect re-review: CLEAR
old concrete material versions remain directly addressable
supersedes direction and disagreement fixtures are rejected
active committed-only material semantics preserved
disabled minimal graph compatibility preserved
```

UltraQA disposition:

```text
status: skipped-as-separate-adversarial-ui-run
reason: Phase 2 changes are dependency-free CLI/runtime fixtures and schemas, not an interactive UI flow.
substitute QA evidence: full positive/negative fixture suite, static typing, ruff, py_compile, JSON parsing, viewer JS syntax checks, plugin validation, and independent code-review/architecture gates.
```

## Known limits

Phase 2 still does not implement:

- stale propagation;
- backflow compiler;
- task packet compiler;
- review closure or delivery gate;
- real subagent dispatch;
- full JSON Schema runtime validation.

These are later-phase responsibilities.

## Next phase start state

Phase 3 may start from this promoted core.

Expected next focus:

- main-agent controller/frontier selection semantics;
- candidate -> validate -> commit protocol;
- state transition/event log;
- owner decision queue/record contract.
