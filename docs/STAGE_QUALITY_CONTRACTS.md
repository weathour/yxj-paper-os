# Stage Quality Contracts

`yxj-paper-os` stage quality contracts extend the existing Paper Production Graph without adding a second authority system. The controller still owns completion; workers and scripts return candidates, receipts, findings, and evidence only.

## Contract stack

```text
StageContract
  -> StageQualityContract
  -> ProducerTaskPacketQualityContract
  -> AuditVerifierPacketQualityContract
  -> Candidate/Review/Backflow evidence
```

## Integration with existing closure fields

The upgrade deliberately reuses existing canonical S09/S10 closure surfaces:

- `unit_material_closure`
- `material_access_manifest`
- `material_read_obligations`
- `material_hydration_report`
- `material_read_receipt_ledger`

`MustReadMaterialManifest` is a conceptual name for these fields as a bundle. It is not a new executable alias and must not replace the canonical fields above.

## StageQualityContract required semantics

Each stage-quality contract records:

- `stage_id`
- `active_profile_source`
- `must_read_materials` as a manifest of material refs, read modes, and required extractions;
- `required_extractions` for obligations that downstream stages must consume;
- `producer_return_obligations` such as read receipts, extraction ledgers, coverage ledgers, missing-material reports, and candidate evidence;
- `audit_verifier_obligations` that inherit producer inputs and add stricter quality checks;
- `downstream_design_force` explaining what later stages can do without guessing;
- `failure_severity_policy` using `BLOCKING`, `MAJOR`, `MINOR`, and `WATCH` while mapping to existing blocker/critical/high/medium/low report vocabularies;
- `nearest_responsible_stage_policy` and `affected_downstream_nodes`;
- `anti_over_strictness_boundary` to prevent minor/watch issues from forcing full reruns by default.

## ProducerTaskPacketQualityContract

Producer packets are intentionally context-rich. They may include many source and design materials when quality depends on them. The packet must still keep worker authority narrow:

- no completion claim;
- no recursive orchestration;
- no owner/external/submission action;
- no write outside allowed paths;
- no new or strengthened claims outside S04/S00 authority.

Producer quality obligations include:

- all current-authority materials needed for the target unit;
- active venue/template/profile controls from S00/S02;
- claim, reader, object, rhetoric, visual/formal, citation, and LaTeX-context obligations where relevant;
- missing-material blocking rules;
- return requirements for material hydration, read receipts, extraction ledgers, coverage ledgers, and candidate evidence.

## AuditVerifierPacketQualityContract

Audit/verifier packets must inherit every producer input. They then add stricter checks:

- verify each required material was read at the requested mode;
- independently re-extract key obligations from the same sources;
- compare output against section depth, citation, visual/formal, language, template/profile, downstream-usefulness, and authority-boundary requirements;
- return exact evidence, severity, nearest responsible stage, affected downstream nodes, and repair route for every non-accept finding.

The verifier cannot accept a stage simply because JSON schema validation passes.

## Severity normalization

| Stage-quality term | Existing-compatible meaning | Default action |
| --- | --- | --- |
| `BLOCKING` | maps to `blocker` / `critical` where existing reports require those names | reject or backflow; stale affected downstream nodes |
| `MAJOR` | high-impact quality failure | scoped repair or backflow |
| `MINOR` | local editorial/trace/format defect | local revision or risk ledger |
| `WATCH` | possible future reviewer risk | track; do not block by default |

## Venue/profile rule

KBS, KDAC, Nature, or any other route can appear only as active owner/profile data or examples. They must not be hardcoded as global defaults. Active profile obligations must be read from S00/S02 or venue overlay materials.

## Rendered manuscript audit relationship

`RenderedManuscriptAuditGate` is downstream of S16 export/handoff evidence. S16 provides the source/PDF/text/manifests/risk map; the rendered gate checks the actual manuscript surface against S00-S16 obligations and emits routed findings. S16 itself still does not claim manuscript-quality approval.
