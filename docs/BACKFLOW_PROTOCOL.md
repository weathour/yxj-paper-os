# Backflow Protocol — Local Backpropagation

## Principle

Review does not trigger whole-paper rewrite by default. It emits loss signals that the main agent maps to upstream material nodes.

```text
review finding -> classify -> locate source node -> compile repair task -> mark scoped stale downstream -> regenerate impacted outputs later
```

Phase 5 makes this executable with two deterministic scripts:

- `scripts/compile_backflow.py`: compiles a structurally valid `ReviewFinding` into a local `BackflowTask`.
- `scripts/propagate_stale.py`: computes a dry-run output graph where only downstream nodes affected by a revised material version are marked `stale`.

These scripts are controller aids. They do not dispatch subagents, rewrite manuscript text, or commit new material versions.

User feedback to the manager surface is also graph input. The controller must classify feedback before acting: reporting-quality corrections usually target `G01`; route/venue/claim-scope corrections target `S00`; source/evidence corrections target `S01/S04`; story, terminology, and visual-design corrections target `S05-S08`; manuscript-quality findings target `S13` and then `S14/S15`. This prevents a conversational correction from becoming an uncontrolled whole-paper rewrite.

## ReviewFinding contract

Canonical Phase 4/5 fields:

```yaml
schema_version: ppg-review-finding/v0.1
finding_id: overclaim_review_finding_v1
status: validated
failure_type: overclaim
target: claim_boundary_map_v1
severity: high
summary: Reviewer found an overstrong safety guarantee.
```

Required fields are enforced by `scripts/validate_review_finding.py`:

- `schema_version`
- `finding_id`
- `status`
- `failure_type`
- `target`

Additional evidence fields are allowed, but the main agent must not treat prose evidence as a permission to rewrite unrelated paper regions.

## Backflow levels and nearest responsible targets

| Level | Failure class | Primary target | Owner gate |
| --- | --- | --- | --- |
| `L0_surface` | grammar, local expression | section/draft artifact | no |
| `L1_terminology` | internal codes, inconsistent labels | `TerminologyRegister` | no |
| `L2_rhetorical` | unclear paragraph function, reader question gap | `ReaderSpine` / rhetorical design material | no |
| `L3_claim_evidence` | overclaim, missing evidence, wrong baseline | `ClaimBoundaryMap`, claim-evidence materials | no |
| `L4_spine` | contribution/problem mismatch | `PaperSpine`, `OwnerIntent` | yes |

Phase 5 acceptance is centered on the L3 overclaim path:

```text
overclaim / claim_overreach -> L3_claim_evidence -> active ClaimBoundaryMap
```

If a finding points to a stale historical material version, the compiler resolves the logical material and targets the active committed version. The historical target remains recorded as `source_target` for provenance.

## BackflowTask contract

Canonical Phase 4/5 fields:

```yaml
schema_version: ppg-backflow-task/v0.1
backflow_id: overclaim_review_finding_v1_backflow_v1
finding_id: overclaim_review_finding_v1
status: planned
target: claim_boundary_map_v2
action: Replace universal safety wording with evidence-supported bounded authority allocation wording.
expected_output: claim_boundary_map_candidate_v3
```

Required fields are enforced by `scripts/validate_backflow.py`:

- `schema_version`
- `backflow_id`
- `finding_id`
- `status`
- `target`
- `action`

Phase 5 explainability fields are allowed and produced by `compile_backflow.py`:

- `failure_type`
- `backflow_level`
- `mapping_rule`
- `source_target`
- `owner_gate_required`
- `affected_material_id`

`expected_output` is an intended next candidate handle. It is not a claim that the candidate material has been generated, validated, committed, or made active.

## Stale propagation

When a revised material version becomes the source:

1. Resolve `--source` as exact node id, logical material id, or dotted material-version handle such as `claim_boundary_map.v2`.
2. Preserve the source node.
3. If the source supersedes older material versions, use those older versions as invalidated dependency seeds.
4. Walk only hard downstream dependency/output edges from those seeds.
5. Mark reachable non-owner downstream nodes `stale` in an output graph copy.
6. Preserve unrelated nodes and the input graph.
7. Emit a deterministic report explaining stale and preserved nodes.

Propagating edge types:

- `consumes`
- `constrains`
- `produces`
- `invalidates`
- `repairs`

Non-propagating edge types:

- `references`
- `reports`
- `supersedes`
- `validates`

`supersedes` is special: it may identify predecessor seeds for a revised material version, but it is not traversed as an ordinary dependency edge.

## Owner gate

Backflow to `OwnerIntent`, `OwnerDecision`, or core `PaperSpine` is owner-gated. The main agent may summarize alternatives and consequences, but it must not invent a new paper commitment.

## Phase 5 validation examples

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

Expected result: the intro writing packet and intro draft become stale; active `claim_boundary_map_v2`, `reader_spine_v1`, `evidence_inventory_v1`, weak reference sidecars, and disconnected sidecars remain preserved.
