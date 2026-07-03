# Stage Quality Upgrade Targets

This document is the plugin-body target and migration map for the 2026-07-03 `yxj-paper-os` stage-quality upgrade. It turns the temporary paper-workspace process-spec work into plugin-level doctrine, schemas, validators, fixtures, and stage documentation.

## Status and authority

- This file is part of the `yxj-paper-os` plugin body and is a durable upgrade target document.
- The current paper workspace process specs under `paper-os/process-specs/S00-S16-task-packet-and-audit/` are migration inputs, not plugin authority.
- `yxj-paper-os` remains standalone. OMX, code-review, UltraQA, and yxj-paper-auto may adapt these contracts, but they are not Paper OS authority sources.

## Source evidence used

Non-draft analysis inputs from the KBS workspace:

- `reviews/2026-07-03_chatgpt-share_paper-os-upgrade-and-kbs-failure-analysis.md`
- `omx_wiki/2026-07-03-论文质量反馈与后续审核要求.md`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/analysis/S00-S10-writing-input-audit.md`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/analysis/S00-S10-writing-input-audit.counts.json`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/review/G010.*`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/validation/G004.claim-boundary-audit.json`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/validation/G005.visual-formal-callout-audit.json`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/validation/G006.s12-integration-surface-audit.json`
- `paper-os/runs/paper-auto-repair-rerun-20260703T061905Z/validation/G009.s16-audit-repair-summary.json`

Migration checklist inputs:

- `paper-os/process-specs/S00-S16-task-packet-and-audit/YXJ-PAPER-OS-UPGRADE-GOALS.zh.md`
- `paper-os/process-specs/S00-S16-task-packet-and-audit/STAGE-QUALITY-CONTRACTS.zh.md`
- `paper-os/process-specs/S00-S16-task-packet-and-audit/TEMPLATE-producer-task-packet.zh.md`
- `paper-os/process-specs/S00-S16-task-packet-and-audit/TEMPLATE-audit-subagent-packet.zh.md`
- `paper-os/process-specs/S00-S16-task-packet-and-audit/S10-S16-input-packet-readiness-audit.zh.md`
- `paper-os/process-specs/S00-S16-task-packet-and-audit/LATEX-full-manuscript-audit-gate.zh.md`
- S00-S16 stage-quality draft docs in that directory.

## Core failure class

The bad pattern to eliminate is:

```text
rich upstream design exists
  -> S09/S10 packets compress it into generic read/draft/trace instructions
  -> stage audits check artifact/schema presence rather than downstream usefulness
  -> S16/export can be clean while the manuscript remains short, thin, weakly cited, visually sparse, and not template-competitive
```

The upgrade therefore focuses on preserving design force from S00-S08 into S09B/S10/S11/S12/S13/S16, and on making audit packets stricter than producer packets.

## Non-negotiable principles

1. **Do not fear large inputs.** High-quality producer or subagent packets may include all useful references. Token minimization must not erase design force.
2. **Designs become obligations.** Owner goals, venue profile, citation burden, reader spine, object granularity, rhetoric controls, and visual/formal plans must become executable packet constraints and audit checks.
3. **Producer/audit split.** Producer packets carry rich context plus moderate non-negotiables; audit/verifier packets inherit all producer inputs and add strict quality, sufficiency, downstream-usefulness, and routing checks.
4. **Obligation-level reading.** `allowed_read_paths` is never enough. Packets and candidate returns must prove which material selectors/obligations were read, extracted, implemented, blocked, owner-gated, or routed.
5. **Profile-local template controls.** KBS/KDAC can be an active profile example, never a global default.
6. **S16 is export/handoff only.** It may fail obvious compiled-PDF defects, but manuscript-quality approval belongs to the downstream `RenderedManuscriptAuditGate`.
7. **Nearest-stage backflow.** Failures route to the closest responsible stage and stale dependent downstream nodes; whole-paper rewrite is not the default.
8. **Hostile fixtures.** Old bad behavior must fail, including thin schema-valid sections, packet compression, audit-input loss, global profile defaults, over-strict minor/watch blocking, and export pass misread as manuscript quality.

## Concept mapping: do not duplicate existing authority

| Upgrade concept | Plugin-body integration target |
| --- | --- |
| StageQualityContract | Companion/extension to existing StageContract docs, schema optional field, stage fixtures, registry/validator dimensions. |
| MustReadMaterialManifest | Conceptual bundle mapped to `unit_material_closure`, `material_access_manifest`, and `material_read_obligations`; no new executable alias. |
| ObligationExtractionLedger | Selector/obligation-level extension of `material_read_obligations.required_selectors_by_material` and return receipts. |
| ObligationCoverageLedger | Stage/candidate/audit evidence mapping each obligation to implemented, missing, blocked, owner-gated, watchlisted, or routed. |
| ProducerTaskPacketQualityContract | Extension of existing `ppg-task-packet.schema.json`, lane policy, worker authority boundary, and packet validators. |
| AuditVerifierPacketQualityContract | Verifier lane contract that inherits producer inputs and adds stricter checks; not a public route or completion authority. |
| FindingSeverity | Compatibility layer: `BLOCKING` maps to existing `blocker`/`critical`; `MAJOR` to high/major repair; `MINOR` and `WATCH` do not force downstream rerun by default. |
| RenderedManuscriptAuditGate | Downstream terminal manuscript-surface gate consuming S16 evidence and S00-S16 materials; emits routed findings and does not make S16 a quality-pass stage. |

## S00-S16 problem table and target upgrade

| Stage | Observed problem | Upgrade target |
| --- | --- | --- |
| S00 | Later owner quality goals such as template parity/statistical similarity/blind judging were not encoded as executable acceptance criteria. | Owner quality contract must expose active venue/profile, quality ambition, owner gates, external-action boundary, and downstream stale effects. |
| S01 | Citation/template/evidence locators existed but many were candidate/locator-needed; downstream citation readiness was weak. | Source inventory must provide citable/source/figure/template locators, freshness, privacy, gaps, and citation-readiness obligations. |
| S02 | KBS exemplars/SOTA were background orientation, not measured profile controls. | Emit active VenueProfile/TemplateStats: section bands, figure/table/formal density, citation/reference density, rhetorical moves, sample limits. |
| S03 | Contribution options and attack rows did not become hard writing depth requirements. | Contribution/attack map must feed S05/S07/S09/S10/S13 obligations and rejected/owner-gated option controls. |
| S04 | Claim safety was strong, but positive persuasive burden per claim was under-specified. | Claim capsules must include citation/evidence/figure/table burden and allowed persuasive depth, not only forbidden overclaims. |
| S05 | Reader questions did not become enough paragraph-level work. | Reader spine must emit section jobs, paragraph-depth obligations, promise/payoff checks, and reviewer-question coverage. |
| S06 | Rich objects/variables/granularity did not force method/evaluation depth. | Object cards and granularity ladders must become S10/S11/S12 required extractions and audit dimensions. |
| S07 | Terminology/surface controls did not provide enough paragraph/move detail. | Rhetoric contract must carry terminology definitions, move obligations, anti-slop, citation/callout wording, and forbidden residue scans. |
| S08 | Visual/formal plans did not become a strong visual-quality gate. | Visual/formal contracts must carry proof role, source route, placement, density budget, caption boundaries, and S10/S11/S12 obligations. |
| S09A | Control selection mapped materials but did not force concrete word/paragraph/citation/visual requirements. | Control selection must preserve usage labels, unit closure, profile/template obligations, and design-force coverage. |
| S09B | Packets could be valid while too generic. | Pre-dispatch packet audit must prove no loss of S00-S08 design force and must block generic packets. |
| S10 | Candidate text passed trace coverage while remaining short/thin. | Candidate returns must prove section depth, claim/evidence/citation realization, template/profile contribution, LaTeX context use, and obligation coverage. |
| S11 | Visual artifacts existed but did not guarantee functional visual density or S10 callout response. | S11 must consume S10 callouts, current LaTeX slots, S08 contracts, S01 source routes, and active visual density/profile targets. |
| S12 | Integration checked consistency but not template-statistical parity or writeback loss. | S12 must verify promise/payoff, claim/citation/figure consistency, profile parity, stale nodes, and source/writeback surface. |
| S13 | Review found issues but did not hard-gate template/blind-review quality. | S13 must review material-chain defects and manuscript sufficiency with severity, exact locators, nearest stage, and S14 handoff. |
| S14 | Backflow localized final findings but under-routed systemic packet/material defects. | S14 must route root causes upstream enough to fix weak stage contracts or packets, not just final prose symptoms. |
| S15 | Local repairs could not fix upstream absence of quality gates. | S15 must stay within S14 scope, prove downstream regeneration, and backflow insufficient repair packets rather than hiding them. |
| S16 | Export/build/semantic checks could be overread as manuscript quality. | S16 must remain export/handoff hygiene and provide complete terminal audit input manifest to RenderedManuscriptAuditGate. |

## File-by-file migration map

| Area | Files |
| --- | --- |
| Target doctrine | `docs/STAGE_QUALITY_UPGRADE_TARGETS.md` |
| Shared contracts | `docs/STAGE_QUALITY_CONTRACTS.md`, `docs/MATERIAL_SCHEMA.md`, `docs/RUNTIME_PROTOCOL.md`, `docs/VALIDATION_AND_TESTING.md` |
| Rendered audit gate | `docs/RENDERED_MANUSCRIPT_AUDIT_GATE.md`, `schemas/ppg-rendered-manuscript-audit-gate.schema.json`, `scripts/verify_rendered_manuscript_audit_gate.py`, `examples/delivery/rendered_manuscript_audit_gate.pass.json`, hostile rendered-audit fixtures |
| Stage docs | `docs/stages/S00...S16*.md` |
| Stage fixtures | `examples/stage-contracts/S00...S16.stage-contract.json` |
| Packet/material schemas | `schemas/ppg-stage-contract.schema.json`, `schemas/ppg-task-packet.schema.json`, `schemas/ppg-material-payloads.schema.json` |
| Runtime validators | `runtime/stage_registry.json`, `runtime/phase10_content_validators.json` |
| Verifiers | `scripts/verify_stage_quality_contracts.py`, focused stage verifiers, `scripts/validate_packet.py`, `scripts/validate_material.py` where needed |

## Milestone plan and commit boundaries

### M-1 Git preflight and baseline hygiene

Acceptance commands:

```bash
git fetch origin --prune
git status --short --branch
git log --oneline origin/main..HEAD
```

Current preflight status: fetch succeeded, worktree clean, `main` is ahead of `origin/main` by two intended wiki cleanup commits: `22ebbbb` and `56792b4`.

### M0 Target implementation document

Commit: `docs: define stage quality upgrade targets`.

Acceptance:

```bash
test -s docs/STAGE_QUALITY_UPGRADE_TARGETS.md
grep -q 'RenderedManuscriptAuditGate' docs/STAGE_QUALITY_UPGRADE_TARGETS.md
grep -q 'S00' docs/STAGE_QUALITY_UPGRADE_TARGETS.md
grep -q 'M-1' docs/STAGE_QUALITY_UPGRADE_TARGETS.md
```

### M1 Shared quality contract surface

Commit: `feat: add stage quality contract surface`.

Acceptance:

```bash
python3 scripts/verify_stage_quality_contracts.py
python3 -m py_compile scripts/verify_stage_quality_contracts.py
python3 scripts/verify_stage_contracts.py
```

### M2a S00-S04 upstream authority/profile/claim gates

Commit: `feat: harden S00 S04 quality gates`.

### M2b S05-S08 reader/object/rhetoric/visual gates

Commit: `feat: harden S05 S08 design force gates`.

### M3a S09A/S09B pre-dispatch packet gates

Commit: `feat: harden S09 packet quality gates`.

### M3b S10/S11 obligation realization gates

Commit: `feat: enforce S10 S11 obligation coverage`.

### M4a S12-S14 integration/review/backflow gates

Commit: `feat: harden S12 S14 review routing gates`.

### M4b S15-S16 repair/export boundary gates

Commit: `feat: harden S15 S16 handoff boundaries`.

### M4c RenderedManuscriptAuditGate

Commit: `feat: add rendered manuscript audit gate`.

Acceptance:

```bash
python3 scripts/verify_rendered_manuscript_audit_gate.py
python3 -m py_compile scripts/verify_rendered_manuscript_audit_gate.py
python3 scripts/verify_stage_quality_contracts.py
```

### M5 Final verification and push readiness

Acceptance:

```bash
python3 scripts/verify_lifecycle_contract.py
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 scripts/verify_stage_quality_contracts.py
python3 scripts/verify_rendered_manuscript_audit_gate.py
python3 scripts/verify_s09_control_packet_assembly.py
python3 scripts/verify_s10_candidate_text_return.py
python3 scripts/verify_s11_figure_caption_artifact_bundle.py
python3 scripts/verify_s12_integration_consistency.py
python3 scripts/verify_s13_adversarial_review_report.py
python3 scripts/verify_s14_backflow_repair_plan.py
python3 scripts/verify_s15_repair_execution_report.py
python3 scripts/verify_s16_export_handoff_package.py
python3 scripts/verify_s16_live_export_evidence.py
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
python3 -m py_compile scripts/verify_stage_quality_contracts.py scripts/verify_rendered_manuscript_audit_gate.py
git diff --check
git status --short --branch
git log --oneline origin/main..HEAD
```

## Final stop condition

The upgrade is complete only when the plugin body contains the target docs/schema/runtime/fixture/verifier surfaces, all required verification commands pass, code review is clean, QA is passed or explicitly skipped with evidence, milestone commits are present, and push to GitHub `main` succeeds or a credential/remote blocker is recorded.
