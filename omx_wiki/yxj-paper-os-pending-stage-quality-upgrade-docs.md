---
title: "YXJ Paper OS Pending Stage-Quality Upgrade Documents"
tags: ["yxj-paper-os", "pending-upgrade", "stage-quality", "task-packet", "audit-gate"]
created: 2026-07-03T20:45:00+08:00
updated: 2026-07-03T20:45:00+08:00
category: architecture
confidence: high
schemaVersion: 1
---

# YXJ Paper OS Pending Stage-Quality Upgrade Documents

## Basis and cutoff

This page keeps only the actually pending `yxj-paper-os` body-work after comparing:

1. paper-side process-spec targets created in the KBS workspace on 2026-07-03, especially:
   - `paper-os/process-specs/S00-S16-task-packet-and-audit/YXJ-PAPER-OS-UPGRADE-GOALS.zh.md`
   - `STAGE-QUALITY-CONTRACTS.zh.md`
   - `TEMPLATE-producer-task-packet.zh.md`
   - `TEMPLATE-audit-subagent-packet.zh.md`
   - `S00-S16-current-material-taskpacket-audit-matrix.zh.md`
   - `S10-S16-input-packet-readiness-audit.zh.md`
   - `LATEX-full-manuscript-audit-gate.zh.md`
2. plugin commits already present on `origin/main` through `f900ed0` at `2026-07-03 13:33:28 +0800`.

The S16 template-only / target-global / compiled semantic surface thread is considered completed by commits from `4cbcaec` through `85d2ecd` and follow-up fixes through `dce0449`, `bbbb3a0`, and `bb745a4`. The S09/S10 material-closure/read-receipt thread is considered partially completed by `2086d0b` through `f900ed0`.

## Pending upgrade surface

### P0 — New or promoted cross-cutting contracts

- Add a first-class `StageQualityContract` concept to the docs/schema layer.
- Add a platform-neutral `RenderedManuscriptAuditGate` contract. It must not be named as an OMX/UltraQA dependency, though yxj-paper-auto may adapt it.
- Add explicit `ProducerTaskPacket` versus `AuditVerifierPacket` obligations:
  - producer packets carry rich context with moderate hard constraints;
  - audit packets inherit all producer inputs and add stricter quality, downstream-usefulness, severity, and routing checks.
- Add `VenueProfile` / `TemplateStats` as machine-readable active profile obligations, not KBS/KDAC defaults.
- Add shared severity and locality vocabulary: `BLOCKING`, `MAJOR`, `MINOR`, `WATCH`, `nearest_responsible_stage`, `affected_downstream_nodes`, and rerun order.

Likely files:

- `docs/MATERIAL_SCHEMA.md`
- `docs/RUNTIME_PROTOCOL.md`
- `docs/VALIDATION_AND_TESTING.md`
- `docs/TARGET_DELIVERY_CONTRACT.md` or a new `docs/RENDERED_MANUSCRIPT_AUDIT_GATE.md`
- `schemas/ppg-material-payloads.schema.json`
- `schemas/ppg-task-packet.schema.json`
- `schemas/ppg-stage-contract.schema.json`
- `runtime/stage_registry.json`
- `runtime/phase10_content_validators.json`
- `runtime/stage_overlay_registry.json`

### P1 — S00-S08 design-force and template/profile upgrades

The current plugin stage docs mostly mention stage purpose and generic nearest-upstream fallback, but they do not yet encode the full process-spec target: downstream design force, active profile/template statistics, producer/audit split, obligation-level read receipts, and per-stage material self-audit.

Likely files:

- `docs/stages/S00-owner-semantic-contract.md`
- `docs/stages/S01-source-evidence-inventory.md`
- `docs/stages/S02-research-dossier.md`
- `docs/stages/S03-contribution-options.md`
- `docs/stages/S04-claim-admissibility.md`
- `docs/stages/S05-reader-spine.md`
- `docs/stages/S06-object-granularity.md`
- `docs/stages/S07-rhetoric-surface-control.md`
- `docs/stages/S08-visual-formal-plan.md`
- corresponding `examples/stage-contracts/S00...S08*.json`
- corresponding positive/negative `examples/materials/*` fixtures.

Required closure examples:

- S02 must emit active venue/template statistics: section length bands, figure/table/formula/reference/citation density, rhetorical move profile, and language/citation patterns.
- S05/S07/S08 must provide paragraph-depth, language, citation, figure/table/formal-callout obligations that S09B/S10/S11 cannot compress away.

### P2 — S09/S10 remaining quality obligations beyond material closure

S09/S10 now have stronger material-closure and read-receipt validation, but still need the broader quality contract from the paper-side process specs:

- S09B pre-dispatch packet audit must prove no loss of S00-S08 design force, not only exact material selector closure.
- S09B packets must carry word/paragraph/citation/visual/formal/terminology/depth obligations.
- S10 must prove section depth, claim/evidence/citation realization, template/profile contribution, and current LaTeX/BibTeX context use, not only hydration/read receipts.

Likely files:

- `docs/stages/S09-control-packet-assembly.md`
- `docs/stages/S10-candidate-text-return.md`
- `scripts/compile_task_packet.py`
- `scripts/validate_packet.py`
- `scripts/verify_s09_control_packet_assembly.py`
- `scripts/verify_s10_candidate_text_return.py`
- `examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml`
- S09/S10 positive and negative fixtures under `examples/materials/` and `examples/packets/`.

### P3 — S11-S16 uniform read/audit packet and manuscript-surface handoff

S11-S16 still need the uniform producer/audit packet and read/coverage structure described in the KBS process-spec targets.

Likely files:

- `docs/stages/S11-figure-caption-artifact-bundle.md`
- `docs/stages/S12-integration-consistency.md`
- `docs/stages/S13-adversarial-review-report.md`
- `docs/stages/S14-backflow-repair-plan.md`
- `docs/stages/S15-repair-execution-report.md`
- `docs/stages/S16-export-handoff-package.md`
- `scripts/verify_s11_figure_caption_artifact_bundle.py`
- `scripts/verify_s12_integration_consistency.py`
- `scripts/verify_s13_adversarial_review_report.py`
- `scripts/verify_s14_backflow_repair_plan.py`
- `scripts/verify_s15_repair_execution_report.py`
- `scripts/verify_s16_export_handoff_package.py`
- `scripts/verify_s16_live_export_evidence.py`

Required closure examples:

- S11 must consume S10 callout needs and current LaTeX figure/table slots, not only S08 plans.
- S12 must validate final-paper integration quality, promise/payoff, citation/figure consistency, and profile parity, not only candidate trace structure.
- S13/S14/S15 must route terminal manuscript failures to nearest responsible stages and mark dependent nodes stale.
- S16 must remain export/handoff hygiene plus input handoff to `RenderedManuscriptAuditGate`; it must not itself claim final manuscript quality.

### P4 — Hostile fixtures and validator closure

Add fixtures that fail when the old bad behaviors recur:

- short/thin sections despite schema-valid materials;
- too few or non-functional figures/tables;
- weak or missing citations despite bibliography presence;
- task-packet compression of S00-S08 design force;
- KBS/KDAC hardcoded as global defaults instead of active profile;
- audit packets that do not inherit producer inputs;
- final build/export success treated as manuscript-quality pass;
- over-strict findings that block on `MINOR`/`WATCH` instead of routing them to risk ledgers.

Likely files:

- `examples/materials/invalid-*`
- `examples/packets/invalid-*`
- `examples/stage-contracts/*`
- `runs/sample-paper-workspace/*`
- `scripts/verify_*.py`
- `docs/runtime-viewer/runtime-graph-data.js`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`

## Deleted or superseded records

The previous wiki pages for S16 template-only evidence, target-global delivery design, compiled semantic surface taxonomy, S16 hardening completion, and the old repair-plan seed were removed from this wiki because their direction is already implemented or superseded. Their durable implementation authority is now the committed plugin docs, schemas, validators, fixtures, and commit history, not the old planning records.
