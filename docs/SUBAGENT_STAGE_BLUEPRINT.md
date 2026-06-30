# Subagent Stage Blueprint — Important PPG Runtime Rings

This blueprint converts the yxj-paper-os neural material layers into dispatchable rings. Each ring is intended to run as:

```text
Strict TaskPacket + consumed material bundle
  -> bounded subagent/script work
  -> CandidateArtifactReturn / MissingMaterialReport
  -> validators
  -> main-agent commit/backflow decision
```

A ring is not a department. It is a repeatable transform over explicit inputs and outputs.

## Stage interface

Every stage should be representable as:

```yaml
stage_id:
stage_name:
purpose:
recommended_agent_type:
mode: agent_generated | script_generated | hybrid_generated | owner_gated
consumes:
produces:
validators:
backflow_targets:
completion_gate:
```


## Context bundle policy

Use ADR-0003: subagents may receive relatively large material bundles, but the bundle must be structured rather than lossy-compressed. The task packet compiler should organize materials into mandatory controls, evidence/source anchors, local context, optional background, forbidden routes, validator refs, and return format.

The goal is not to minimize context at all costs. The goal is to prevent undifferentiated context dumps and to make the packet an authority boundary.

Phase 6 strict packets add explicit `allowed_read_paths`, `allowed_write_paths`, `output_artifact_path`, `worker_boot_clause`, `completion_forbidden: true`, `no_recursive_orchestration: true`, and `owner_gate_required: false`. A worker return is only a candidate: it cannot mark graph completion or widen its write surface.

## Stage-local overlay policy

Phase 11 adds `nature_expert_writing` as a stage-local overlay. It is not a department and not a separate worker route.

When a stage uses this overlay, the subagent receives it only through existing packet channels:

- `mandatory_controls.nature_overlay_ref`;
- `mandatory_controls.nature_overlay_stage_binding`;
- `mandatory_controls.nature_overlay_packet_clauses`;
- `validators: stage_overlay:nature_expert_writing:<stage_id>`.

The overlay may add expert-writing controls, expected outputs, and review checks to the stage. It may not add a top-level TaskPacket field, dispatch another subagent, mark completion, or bypass the main-agent controller.

## Important dispatchable stages

### S00 — Owner semantic contract

- **Purpose:** convert human need into bounded paper commitments.
- **Agent type:** main agent; optionally `analyst` / `planner` for interview synthesis.
- **Mode:** `owner_gated` + `hybrid_generated`.
- **Consumes:** human prompt, existing paper profile, source/evidence summary.
- **Produces:** `paper-profile.yaml`, `motivation.yaml`, decision records, forbidden routes, success criteria.
- **Validators:** owner confirmation for core motivation, venue, claim scope, private-source policy.
- **Backflow targets:** human owner; no subagent may silently change this layer.
- **Completion gate:** explicit confirmed decision or recorded assumption with owner-gated status.

### S01 — Source / citation / evidence inventory

- **Purpose:** make raw paper inputs locatable and support-safe.
- **Agent type:** `explore` for local lookup; `researcher` for external source lookup; `verifier` for support checks.
- **Mode:** `hybrid_generated`.
- **Consumes:** initial files, result dirs, BibTeX/citation files, source locators, owner source policy.
- **Produces:** `source-map.yaml`, `citation-bank.yaml`, `evidence-bank.yaml`, `nature-source-inventory.yaml` when the `nature_expert_writing` overlay applies.
- **Validators:** source locator resolution, privacy boundary check, evidence artifact existence, citation bank structural check.
- **Backflow targets:** owner source policy, evidence inventory, citation support.
- **Completion gate:** every claim-relevant source is locator-backed or explicitly unresolved.

### S02 — Research / scene / exemplar / SOTA analysis

- **Purpose:** understand field scene, template expectations, exemplar structure, and related-work positioning.
- **Agent type:** `researcher` for external docs/literature; `explore` for local project context; `planner` for synthesis.
- **Mode:** `agent_generated` + validator-backed source checks.
- **Consumes:** source map, citation bank, target venue/reader route, allowed exemplar locators.
- **Produces:** `research-dossier.yaml`, `paper-reader-package.yaml`, `search-strategy-dossier.yaml`, `template-quant-profile.yaml`, `journal-style-profile.yaml`, `citation-verification-report.yaml`.
- **Validators:** source citations/locators, no template copying, exemplar-use boundary, citation verification.
- **Backflow targets:** source inventory, target venue decision, template policy.
- **Completion gate:** research dossier and template/profile outputs are source-located and safe to consume.

### S03 — Novelty and contribution option analysis

- **Purpose:** identify viable contribution framings without treating speculation as evidence.
- **Agent type:** `critic`, `planner`, `researcher` depending on route.
- **Mode:** `agent_generated`.
- **Consumes:** research dossier, evidence inventory, motivation, SOTA map.
- **Produces:** contribution options, novelty readiness assessment, risk list; later feeds `motivation.yaml`, `rationale-matrix.yaml`, `reader-spine-brief.yaml`.
- **Validators:** evidence-readiness score, source anchors, owner confirmation for semantic shifts.
- **Backflow targets:** owner semantic contract, research dossier, evidence inventory.
- **Completion gate:** viable options are classified as supported, owner-gated, or rejected.

### S04 — Evidence-to-claim admissibility

- **Purpose:** bind evidence and citations to exact claim boundaries.
- **Agent type:** `verifier` primary; `researcher` support for citations; `critic` for overclaim challenge.
- **Mode:** `hybrid_generated`.
- **Consumes:** evidence bank, citation bank, result artifacts, research dossier, motivation/contribution options.
- **Produces:** `claim-citation-capsule.yaml`, `result-package.yaml`, `claim-evidence-visibility-map.yaml`, `data-availability-plan.yaml`.
- **Validators:** claim support, result package boundary, allowed/forbidden wording, data availability non-invention.
- **Backflow targets:** evidence inventory, source map, owner claim scope.
- **Completion gate:** every claim-bearing unit has support strength, evidence anchor, allowed wording, and forbidden wording.

### S05 — Paper spine and reader-question synthesis

- **Purpose:** synthesize paper argument path and reader/reviewer questions.
- **Agent type:** `architect` or `planner`; `critic` for challenge.
- **Mode:** `agent_generated`.
- **Consumes:** motivation, contribution options, research dossier, template profile, claim/evidence materials.
- **Produces:** `reader-spine-brief.yaml`, `reviewer-question-map.yaml`, `rationale-matrix.yaml`.
- **Validators:** each core claim appears in spine, each section answers a reader/reviewer question, unresolved owner decisions explicit.
- **Backflow targets:** owner semantic contract, novelty analysis, claim admissibility.
- **Completion gate:** spine is coherent and claim-bounded before writing begins.

### S06 — Object representation and granularity design

- **Purpose:** decide how paper objects appear across sections and at what granularity.
- **Agent type:** `architect` / `planner`.
- **Mode:** `agent_generated`.
- **Consumes:** reader spine, reviewer question map, template profile, claim evidence visibility.
- **Produces:** `object-representation-matrix.yaml`, `section-function-budget.yaml`, `cognitive-load-budget.yaml`, `explanation-ladder.yaml`.
- **Validators:** no flat repetition, allowed granularity progression, cognitive load budget exists for paper-facing units.
- **Backflow targets:** reader spine, template profile, claim visibility.
- **Completion gate:** writing units can consume explicit object/granularity instructions.

### S07 — Rhetoric, terminology, and surface-control synthesis

- **Purpose:** turn reader/object design into paragraph-level rhetorical and terminology controls.
- **Agent type:** `writer` for expression design; `critic` for surface risks.
- **Mode:** `hybrid_generated`.
- **Consumes:** object representation, cognitive load, explanation ladder, claim visibility, source/evidence wording.
- **Produces:** `main-text-construction-matrix.yaml`, `rhetorical-move-matrix.yaml`, `terminology-register.yaml`, `expression-design-bundle.yaml`, `main-text-surface-rules.yaml`.
- **Validators:** terminology coverage, forbidden internal ids, claim visibility, rhetorical move coverage.
- **Backflow targets:** object representation, claim visibility, reader question map.
- **Completion gate:** main text can be generated without raw internal method ids, unsupported claims, or lab-notebook smell.

### S08 — Visual/formal object planning

- **Purpose:** decide which figures/tables/algorithms/formulas exist and what they prove.
- **Agent type:** `designer`, `architect`, or `planner`; `verifier` for evidence links.
- **Mode:** `hybrid_generated`.
- **Consumes:** reader spine, section function budget, claim/evidence materials, visual/formal budget.
- **Produces:** `visual-table-algorithm-formula-budget.yaml`, `nature-figure-contract.yaml`, `nature-figure-aesthetic-profile.yaml`, `nature-panel-evidence-map.yaml`, `figure-backend-route.yaml`.
- **Validators:** each visual/formal object has a reader question, supported claim, evidence refs, backend route, and non-decorative role.
- **Backflow targets:** reader spine, claim/evidence materials, visual budget.
- **Completion gate:** no final/export-facing figure can proceed without contract/evidence/backend route.

### S09A — Control-material selection

- **Purpose:** choose the minimal control material set needed by the target manuscript unit before compiling a writing task.
- **Agent type:** main agent or `planner`; may be script-assisted.
- **Mode:** `hybrid_generated`.
- **Consumes:** admitted claim capsules, reader spine, object/granularity controls, terminology/surface controls, target manuscript unit.
- **Produces:** `selected-control-bundle.yaml`, `control-priority-map.yaml`, `missing-control-report.yaml`.
- **Validators:** required controls present, no overloaded all-context packet, priority order resolves conflicts, missing materials are explicit.
- **Backflow targets:** claim/evidence materials, reader spine, granularity controls, surface controls.
- **Completion gate:** S09B can build a task packet without guessing which upstream controls matter.

### S09B — Per-unit task packet assembly

- **Purpose:** compile one bounded `WritingTaskPacket` for a section/unit from the selected control bundle, evidence anchors, validator refs, and return contract.
- **Agent type:** main agent or `planner`; may be script-assisted.
- **Mode:** `hybrid_generated`.
- **Consumes:** `selected-control-bundle.yaml`, evidence/source anchors, target manuscript unit, validator refs, expected return format, single-writer lock requirements.
- **Produces:** strict `task-packet.yaml`, `section-move-plan.yaml`, `single-writer-section-lock.yaml`; if blocked, `MissingMaterialReport`.
- **Validators:** required inputs present, expected output path, validator refs, `allowed_read_paths`, `allowed_write_paths`, `worker_boot_clause`, `completion_forbidden=true`, `no_recursive_orchestration=true`, `owner_gate_required=false` for worker/subagent, single-writer lock for shared hotspots.
- **Backflow targets:** S09A control selection, missing evidence anchors, S14/S15 repair packet source.
- **Completion gate:** packet is narrow enough for subagent execution, complete enough for validation, and cannot grant graph-completion or recursive-dispatch authority.

### S10 — Main-text production

- **Purpose:** produce candidate manuscript modules from task packets.
- **Agent type:** `writer` or `executor` depending on text/code mix.
- **Mode:** `agent_generated`.
- **Consumes:** S09B task packet, construction matrix, terminology register, claim/evidence visibility, source/citation/result capsules.
- **Produces:** candidate abstract/introduction/related-work/method/experiment/results/discussion/conclusion units plus `CandidateArtifactReturn`; may later feed polishing materials.
- **Validators:** no internal code leakage, claim strength obeys boundary, reader question answered, citations/rendering not raw, output matches packet, return packet id matches origin, output path is inside packet write boundary, `remaining_risks` present.
- **Backflow targets:** S09B task packet, rhetoric/surface controls, claim/evidence visibility, section plan.
- **Completion gate:** candidate text collected and validated; not complete until review and graph commit.

### S11 — Figure / caption / formal artifact production

- **Purpose:** produce figures, captions, tables, algorithms, formulas, and their export bundles.
- **Agent type:** `executor` for deterministic drawing/code; `designer` for visual plan; `verifier` for QA.
- **Mode:** `hybrid_generated`.
- **Consumes:** figure contracts from S08, panel evidence/result packages from S04, source data locators from S01, backend route, image-integrity requirements, caption brief.
- **Produces:** `figure-source-data-statistics.yaml`, `figure-image-integrity-record.yaml`, `nature-caption-legend-brief.yaml`, `figure-export-bundle.yaml`, candidate figure/caption artifacts.
- **Validators:** build/render, source data, image integrity, caption claim boundary, legibility, backend source of truth.
- **Backflow targets:** S08 figure contract, S04 panel evidence/result package, S01 evidence inventory/source locator, caption brief.
- **Completion gate:** figure/caption has editable source, rendered outputs, provenance, QA route, and claim support.

### S12 — Integration and consistency pass

- **Purpose:** assemble modules and check cross-section dependencies.
- **Agent type:** `verifier`, `critic`, or `writer` for integration edits after verification.
- **Mode:** `hybrid_generated`.
- **Consumes:** candidate text modules, figures/captions, section move plan, cross-section dependencies, terminology register, claim visibility.
- **Produces:** integrated manuscript candidate; consistency findings; may emit `validator-report.yaml`.
- **Validators:** introduction promises satisfied, method/experiment/result alignment, terminology consistency, figure-text consistency, citation rendering plan.
- **Backflow targets:** affected section packet, terminology, claim visibility, visual/formal plan.
- **Completion gate:** integrated candidate is ready for adversarial review, not final.

### S13 — Adversarial manuscript review

- **Purpose:** generate loss signals, not direct uncontrolled rewrites.
- **Agent type:** `critic`, `verifier`, `code-reviewer` for code/experiment artifacts when relevant.
- **Mode:** `agent_generated` + validator checks.
- **Consumes:** integrated manuscript candidate, evidence/claim materials, reader/terminology/rhetoric materials, figure/export artifacts.
- **Produces:** `reviewer-panel-report.yaml`, `review-output.yaml`, `reader-experience-review-report.yaml`, `reader-surface-tutor-review.yaml`, `rendered-surface-gate-report.yaml`, `nature-figure-qa-report.yaml`, `validator-report.yaml`.
- **Validators:** every accepted finding has severity, evidence, affected artifact, owner/backflow target, and resolution status.
- **Backflow targets:** nearest responsible upstream material, not whole paper by default.
- **Completion gate:** review findings are actionable and routed.

### S14 — Backflow compilation and repair planning

- **Purpose:** convert review/loss signals into local repair tasks.
- **Agent type:** main agent or `planner`; `verifier` for routing validity.
- **Mode:** `hybrid_generated`.
- **Consumes:** review outputs, validator reports, affected materials graph.
- **Produces:** `narrative-backflow-task.yaml`, repair task packets, S09A control-reselection tasks when scope changed, S09B packet-regeneration tasks when text must be regenerated, `polishing-repair-report.yaml`, `response-action-map.yaml` when reviewer/editor responses exist.
- **Validators:** each finding has target layer/material, affected downstream nodes, repair mission, validators, owner-gate status.
- **Backflow targets:** `L0_surface`, `L1_terminology`, `L2_rhetorical_move`, `L3_claim_evidence`, `L4_spine_semantics`, `L5_figure_data`, `L6_export_render`, `L7_repository_hygiene`, with explicit nearest-responsible material id.
- **Completion gate:** no accepted finding remains unrouted.

### S15 — Repair execution and local regeneration

- **Purpose:** execute the bounded backflow task and regenerate only affected downstream outputs.
- **Agent type:** `executor`, `writer`, `verifier`, or `critic` depending on fix.
- **Mode:** `agent_generated` / `hybrid_generated`.
- **Consumes:** backflow task packet, target material, stale downstream set.
- **Produces:** revised material, regenerated S09B task packet when needed, revised text/figure, updated validator report.
- **Validators:** stale propagation scoped, unrelated nodes unchanged, original finding resolved, no new high-severity finding introduced.
- **Backflow targets:** S09B for regenerated writing packets, S10/S11 for local text/figure regeneration, S12 for reintegration, or the same/deeper layer if fix fails.
- **Completion gate:** graph records new version and affected nodes are revalidated.

### S16 — Export, repository hygiene, and handoff

- **Purpose:** package final paper and prove delivery cleanliness.
- **Agent type:** `verifier` / `executor` for builds; main agent for owner handoff.
- **Mode:** `hybrid_generated`.
- **Consumes:** clean final candidate from S12, review closure from S13, repair-complete delivery package from S15, figures/captions, export package inputs, repository state.
- **Produces:** `export-manifest.yaml`, `repository-hygiene-report.yaml`, `manager-handoff-report.md`, `manager-handoff-report-v2.md`.
- **Validators:** build success, rendered surface checks, no raw citekeys/internal ids, manifest hashes, dirty worktree classification, external submission boundary.
- **Backflow targets:** export surface, manuscript surface, repository hygiene, owner decisions.
- **Completion gate:** content-ready and delivery-clean states are separately proven.

## Sidecar stages

These are important but not part of the main paper cognition forward pass.

### G01 — Runtime governance registry

- **Consumes/produces:** `state.yaml`, `manager-boot-checklist.yaml`, department/governance templates, `company-skill-registry.yaml`.
- **Purpose:** define permissions, lane ownership, state control, skill-as-SOP registry.
- **Agent type:** main agent / `verifier`.
- **Use:** before enabling automation, not before every writing task.

### G02 — Post-paper derivative outputs

- **Consumes/produces:** `presentation-plan.yaml`, `patent-draft-boundary.yaml`, optional profile-specific derivative package.
- **Purpose:** manage post-paper or external derivative capabilities.
- **Agent type:** `planner`, `writer`, `verifier` depending on derivative.
- **Use:** after paper content is stable or when explicitly requested.

Nature writing expertise for the current manuscript is **not** routed through G02. It is the stage-local `nature_expert_writing` overlay on the active stage.

## Minimal stage chain for first implementation

The first runnable chain should not use every stage. Use:

```text
S00 -> S01 -> S04 -> S05 -> S07 -> S09A -> S09B -> S10 -> S13 -> S14 -> S15
```

This proves one manuscript unit can move from owner need to evidence-bound writing, review loss, local backflow, and revised output.
