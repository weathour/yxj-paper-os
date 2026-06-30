# Phase 5 Promotion — Local Backflow and Scoped Stale Propagation

Date: 2026-06-29

## Promotion decision

Phase 5 is promoted as the first executable local-backpropagation proof for the PPG runtime.

The runtime can now:

1. validate a `ReviewFinding`;
2. compile it into a local `BackflowTask` for the nearest responsible upstream material;
3. preserve historical finding targets while repairing the active material version;
4. compute affected downstream nodes from a revised material version;
5. mark only affected downstream nodes stale in an output graph copy;
6. explain stale and preserved nodes in deterministic reports.

## Implemented artifacts

- `scripts/compile_backflow.py`
- `scripts/propagate_stale.py`
- `examples/review_findings/unsupported-failure-type.v1.yaml`
- `examples/backflow_tasks/overclaim_repair.compiled.v1.yaml`
- `examples/runtime/overclaim-loop.phase5-stale.json`
- `examples/controller-reports/overclaim-loop.phase5-stale.report.txt`
- `examples/controller-reports/weak-reference.phase5-stale.report.txt`
- `examples/controller-reports/disconnected-sidecar.phase5-stale.report.txt`
- `docs/BACKFLOW_PROTOCOL.md` canonical Phase4/5 field reconciliation

## Accepted semantics

### Backflow mapping

The promoted L3 path is:

```text
overclaim / claim_overreach -> L3_claim_evidence -> active ClaimBoundaryMap
```

For the current fixture:

- finding target: `claim_boundary_map_v1`;
- nearest active repair target: `claim_boundary_map_v2`;
- intended next candidate handle: `claim_boundary_map_candidate_v3`;
- owner gate: `false`.

Unsupported failure types fail closed with `E_BACKFLOW_MAPPING_UNSUPPORTED`.

### Stale propagation

For `--source claim_boundary_map.v2`, the source is preserved. Its `supersedes` predecessor `claim_boundary_map_v1` becomes the invalidated dependency seed. Hard downstream dependency/output edges then mark:

- `intro_writing_packet_v1` stale;
- `intro_draft_v1` stale.

The following remain preserved:

- active `claim_boundary_map_v2`;
- `reader_spine_v1`;
- `evidence_inventory_v1`;
- `claim_boundary_map_candidate_v3`;
- weak-reference and disconnected sidecar examples.

`references`, `reports`, `validates`, and ordinary `supersedes` traversal do not propagate stale. `supersedes` is used only to identify predecessor seeds.

## Verification evidence

Core commands:

```bash
python3 scripts/compile_backflow.py examples/review_findings/overclaim.v1.yaml \
  --graph examples/runtime/overclaim-loop.v1.json \
  --out /tmp/phase5-backflow.yaml
python3 scripts/validate_backflow.py /tmp/phase5-backflow.yaml

python3 scripts/propagate_stale.py examples/runtime/overclaim-loop.v1.json \
  --source claim_boundary_map.v2 \
  --out /tmp/phase5-stale.json \
  --report /tmp/phase5-stale.report.txt
python3 scripts/validate_graph.py /tmp/phase5-stale.json
```

Regression commands are recorded in `.omx/plans/phase5-local-backflow-stale-propagation-test-spec.md` and were run before promotion.

## Ralplan consensus

- Architect round 2: APPROVE / CLEAR (`019f133e-034e-7101-bc90-4e35f397ae1d`).
- Critic round 2: APPROVE / CLEAR (`019f1341-09c3-7591-af28-86efc4b00901`).

## Explicit limits

Phase 5 does not:

- dispatch real subagents;
- regenerate paper text;
- validate or commit the expected output material;
- update frontend visualization;
- install or publish the plugin;
- activate controller-bypassing route behavior.

Those belong to later phases.
