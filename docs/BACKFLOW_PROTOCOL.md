# Backflow Protocol — Local Backpropagation

## Principle

Review does not trigger whole-paper rewrite by default. It emits loss signals that the main agent maps to upstream material nodes.

```text
feedback/review finding
  -> classify
  -> attribute to nearest responsible stage/material
  -> compile repair task
  -> mark scoped stale downstream
  -> regenerate impacted outputs
  -> validate
```

## Relationship to the feedback lifecycle

`ReviewFeedbackPackage` normalizes the observed problem. `FailureAttributionRecord` decides the nearest responsible stage/material. `BackflowTask` and `RepairTaskPacket` then define current-paper repair.

Existing `ReviewFinding` and `BackflowTask` remain the executable local-backflow spine. The newer feedback lifecycle objects add provenance, attribution, preserve scope, and post-run system-learning boundaries.

## Backflow levels

| Level | Failure class | Primary target | Owner gate |
| --- | --- | --- | --- |
| `L0_surface` | grammar, local expression | section/draft artifact | no |
| `L1_terminology` | internal codes, inconsistent labels | `TerminologyRegister` | no |
| `L2_rhetorical` | unclear paragraph function, reader question gap | `ReaderSpine` or rhetorical design material | no |
| `L3_claim_evidence` | overclaim, missing evidence, wrong baseline | `ClaimBoundaryMap` / claim-evidence materials | no |
| `L4_spine` | contribution/problem mismatch | `PaperSpine` / `OwnerIntent` | yes |

## BackflowTask contract

```yaml
schema_version: ppg-backflow-task/v0.1
backflow_id:
finding_id:
status: planned
target:
action:
expected_output:
failure_type:
backflow_level:
source_target:
owner_gate_required:
affected_material_id:
```

`expected_output` is an intended candidate handle. It is not a claim that the candidate has been generated, validated, committed, or made active.

## Stale propagation

When a revised material version becomes the source:

1. Resolve the source node or logical material version.
2. Preserve the source node.
3. Use superseded older versions as invalidated dependency seeds.
4. Walk only hard downstream dependency/output edges.
5. Mark reachable non-owner downstream nodes `stale` in an output graph copy.
6. Preserve unrelated nodes and the input graph.
7. Emit a deterministic report explaining stale and preserved nodes.

Propagating edges:

- `consumes`
- `constrains`
- `produces`
- `invalidates`
- `repairs`

Non-propagating edges:

- `references`
- `reports`
- `supersedes` as ordinary traversal
- `validates`

## Owner gate

Backflow to `OwnerIntent`, `OwnerDecision`, target venue, contribution route, or core `PaperSpine` is owner-gated. The main agent may summarize alternatives and consequences, but it must not invent a new paper commitment.

## Current-paper repair vs stage improvement

A single feedback item normally creates a local repair task. A `StageImprovementRecord` should be created only after recurring failures or a full-run retrospective indicates the stage prompt, material template, task-packet clause, or validator is systematically weak.

## Validation examples

```bash
python3 scripts/compile_backflow.py examples/review_findings/overclaim.v1.yaml \
  --graph examples/runtime/overclaim-loop.v1.json \
  --out /tmp/backflow.yaml
python3 scripts/validate_backflow.py /tmp/backflow.yaml

python3 scripts/propagate_stale.py examples/runtime/overclaim-loop.v1.json \
  --source claim_boundary_map.v2 \
  --out /tmp/overclaim-stale.json \
  --report /tmp/overclaim-stale.report.txt
python3 scripts/validate_graph.py /tmp/overclaim-stale.json
```
