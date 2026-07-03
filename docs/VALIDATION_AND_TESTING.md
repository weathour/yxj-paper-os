# Validation and Testing Plan

## Validator categories

### Graph validators

- all edge endpoints exist;
- node ids are unique;
- committed manuscript artifacts have task packets;
- review findings have backflow targets;
- stale nodes list stale reasons;
- owner intent changes have owner evidence.

### Material validators

- envelope fields present;
- typed payload required fields present;
- source inputs exist;
- validators are declared;
- invalidation policy exists.

### Lifecycle validators

- every feedback package is routed before repair;
- every attribution names a canonical stage and responsible material;
- repair packets are scoped and cannot request recursive orchestration or completion authority;
- whole-manuscript rewrite is owner-gated;
- stage improvements require retrospective or repeated-failure evidence;
- retrospectives cannot claim submission/publication readiness;
- active contracts do not require external orchestrators or host-local Codex paths.

### Manuscript validators

- no internal code leakage in main prose;
- no raw internal constraints in rendered output;
- no bare citation keys in rendered output;
- claims obey evidence visibility limits;
- section units answer declared reader questions;
- terminology register is consumed.

### Backflow validators

- every finding has a failure type;
- every backflow task has a target node;
- stale propagation is scoped;
- unrelated downstream nodes remain unchanged;
- repaired nodes create new versions.

## Core commands

```bash
python3 scripts/verify_lifecycle_contract.py
python3 scripts/validate_material.py examples/materials/claim_boundary_map.v2.yaml
python3 scripts/verify_s00_owner_semantic_contract.py
python3 scripts/verify_s01_source_evidence_inventory.py
python3 scripts/verify_s02_research_dossier.py
python3 scripts/verify_s03_contribution_options.py
python3 scripts/verify_s04_claim_admissibility.py
python3 scripts/verify_s05_reader_spine.py
python3 scripts/verify_s06_object_granularity.py
python3 scripts/verify_s07_rhetoric_surface_control.py
python3 scripts/validate_review_finding.py examples/review_findings/overclaim.v1.yaml
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v2.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/overclaim_repair.v1.yaml
python3 scripts/validate_delivery_gate.py examples/delivery/review_closure.pass.yaml
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```


## S01 source/evidence inventory contract

Positive fixtures:

- `examples/materials/s01_inventory_input.v1.yaml`
- `examples/materials/s01_source_evidence_inventory.v1.yaml`

Negative fixtures:

- `examples/materials/invalid-s01-inventory-input-source-write-allowed.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-missing-completion-boundary.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-claim-admissibility.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-missing-privacy-boundary.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-missing-unresolved-register.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-private-promoted.yaml`

Expected aggregate signal:

```text
PPG_S01_SOURCE_EVIDENCE_INVENTORY_OK
```

## S02 research dossier / language-profile contract

Positive fixture:

- `examples/materials/phase10_s02_research_dossier.yaml`

Negative fixtures:

- `examples/materials/invalid-s02-research-dossier-missing-language-profile.yaml`
- `examples/materials/invalid-s02-research-dossier-prescriptive-metrics.yaml`
- `examples/materials/invalid-s02-research-dossier-template-copying.yaml`
- `examples/materials/invalid-s02-research-dossier-claim-freeze.yaml`
- `examples/materials/invalid-s02-research-dossier-completion-overclaim.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-unresolved-report.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-downstream-handoff.yaml`

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes `S02ResearchDossier`;
- S02 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and mandatory producer/verifier lanes;
- `examples/packets/phase10_s02_sota_analysis_packet.v1.yaml` validates and
  declares typed output, internal execution passes, coverage ledgers, and
  descriptive-not-prescriptive controls;
- `runtime/phase10_content_validators.json` contains S02-specific dimensions
  and checks for source coverage, template language profile, misuse guard,
  unresolved/backflow, and S03/S05/S07 handoff coverage.

Expected aggregate signal:

```text
PPG_S02_RESEARCH_DOSSIER_OK
```

## S03 contribution option classifier contract

Positive fixture:

- `examples/materials/phase10_s03_contribution_options.yaml`

Negative fixtures:

- `examples/materials/invalid-s03-contribution-options-missing-option-queue.yaml`
- `examples/materials/invalid-s03-contribution-options-invalid-status.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-sota-contrast.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-rejected-register.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-owner-gated-register.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-s04-handoff.yaml`
- `examples/materials/invalid-s03-contribution-options-claim-admissibility.yaml`
- `examples/materials/invalid-s03-contribution-options-completion-overclaim.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-anti-rhetoric-guard.yaml`

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes `S03ContributionOptions`;
- S03 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and mandatory producer/verifier lanes;
- `examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml` validates
  and declares typed output, internal execution passes, option coverage
  ledgers, rejected/owner-gated registers, and S04 handoff coverage;
- `runtime/phase10_content_validators.json` contains S03-specific dimensions
  and checks for option classification, SOTA contrast, evidence readiness,
  reviewer attack/coherence, S04 handoff, anti-rhetoric guard, and no
  claim-admissibility/final-wording leakage.

Expected aggregate signal:

```text
PPG_S03_CONTRIBUTION_OPTIONS_OK
```

## S04 claim admissibility contract

Positive fixture:

- `examples/materials/phase10_s04_claim_admissibility.yaml`

Negative fixtures:

- `examples/materials/invalid-s04-claim-admissibility-missing-claim-queue.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-evidence-anchor.yaml`
- `examples/materials/invalid-s04-claim-admissibility-unsupported-admitted.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-allowed-wording.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-forbidden-wording.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-result-boundary.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-transformation-log.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-downstream-handoff.yaml`
- `examples/materials/invalid-s04-claim-admissibility-completion-overclaim.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s04-claim-admissibility-final-prose.yaml`
- `examples/materials/invalid-s04-claim-admissibility-invalid-support-strength.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-downstream-permission.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-unresolved-backflow.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-data-availability.yaml`

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes
  `S04ClaimAdmissibility`;
- S04 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and mandatory producer/verifier lanes;
- `examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml`
  validates and declares typed output, internal execution passes, claim queue,
  atomic claim register, claim coverage ledger, evidence locator coverage,
  unsupported/backflow registers, and downstream handoff coverage;
- `runtime/phase10_content_validators.json` contains S04-specific dimensions
  and checks for claim queue, atomic decomposition, capsules, coverage ledger,
  support strength, evidence anchors, allowed/forbidden wording, result
  package boundary, transformation/backflow, downstream handoff coverage, and
  no final-prose/completion overclaim.

Expected aggregate signal:

```text
PPG_S04_CLAIM_ADMISSIBILITY_OK
```

## S05 reader-spine contract

Positive fixture:

- `examples/materials/phase10_s05_reader_spine.yaml`

Negative fixtures:

- `examples/materials/invalid-s05-reader-spine-missing-admitted-claim-intake.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-reader-question-coverage.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-claim-section-spine.yaml`
- `examples/materials/invalid-s05-reader-spine-new-claim.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-claim-section-coverage.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-front-half-payoff.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-rationale.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-s06-s07-s08-handoff.yaml`
- `examples/materials/invalid-s05-reader-spine-final-prose.yaml`
- `examples/materials/invalid-s05-reader-spine-completion-overclaim.yaml`
- `examples/materials/invalid-s05-reader-spine-hidden-owner-decision.yaml`

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes `S05ReaderSpine`;
- S05 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and mandatory producer/verifier lanes;
- `examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml`
  validates and declares typed output, S04-controlled claim intake, reader
  question progression, claim-to-section spine, front-half promise payoff,
  reviewer-question mapping, rationale matrix, owner-decision surfacing,
  downstream S06/S07/S08 handoffs, and no-final-prose/no-new-claim controls;
- `runtime/phase10_content_validators.json` contains S05-specific dimensions
  and checks for admitted claim intake, reader-question coverage, claim-section
  coverage, front-half promise payoff, reviewer/rationale maps, owner decisions,
  downstream handoff coverage, coherence/overpromise audit, and no completion
  overclaim.

Expected aggregate signal:

```text
PPG_S05_READER_SPINE_OK
```


## S06 object/granularity contract

Positive fixture:

- `examples/materials/phase10_s06_object_granularity.yaml`

Negative fixtures cover missing object inventory, mechanism-variable inventory,
P0/P1/P2 object cards, variable cards, reader-question mapping, granularity
progression, section/load budgets, explanation ladder, coverage ledger,
downstream handoff, final prose, completion overclaim, hidden unresolved
objects, and new claim leakage.

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes `S06ObjectGranularity`;
- S06 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and conditional producer/verifier lane policy;
- `examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml`
  validates and declares typed output, S04/S05 controls, internal passes,
  object/variable cards, cross maps, granularity/load/ladder controls,
  downstream S07/S08/S10 handoffs, and no-final-prose/no-new-claim controls;
- `runtime/phase10_content_validators.json` contains S06-specific dimensions
  and checks for object/variable coverage, mappings, granularity, load,
  ladders, repetition, unresolved objects, handoffs, and boundary audit.

Expected aggregate signal:

```text
PPG_S06_OBJECT_GRANULARITY_OK
```


## S07 rhetoric/surface-control contract

Positive fixture:

- `examples/materials/phase10_s07_surface_control.yaml`

Negative fixtures cover missing input coverage, claim surface rules, terminology
register, internal-id bans, paragraph jobs, rhetorical moves, flexible language
controls, forbidden expressions, coverage ledger, downstream handoff, new claim
leakage, final prose, completion overclaim, claim-strengthening, and rigid
language/template misuse.

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes
  `S07RhetoricSurfaceControl`;
- S07 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and conditional writer/verifier lane policy;
- `examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml`
  validates and declares typed output, internal execution passes, claim-safe
  terminology/surface controls, flexible language guard, forbidden expressions,
  downstream handoffs, and no-new-claim/no-claim-strengthening/no-final-prose
  controls;
- `runtime/phase10_content_validators.json` contains S07-specific dimensions
  and checks for input coverage, claim surface rules, terminology, internal-id
  bans, paragraph jobs, rhetorical moves, language flexibility, forbidden
  expressions, coverage ledger, downstream handoffs, and surface safety audit.

Expected aggregate signal:

```text
PPG_S07_RHETORIC_SURFACE_CONTROL_OK
```


## S08 visual/formal planning contract

Positive fixture:

- `examples/materials/phase10_s08_visual_formal_plan.yaml`

Negative fixtures cover missing input coverage, visual needs, candidate queue,
visual budget, figure/table/formal contracts, panel evidence maps,
visual-claim bindings, backend routes, caption boundaries, accessibility
constraints, downstream handoff, hidden unresolved objects, new claim leakage,
schematic-as-evidence misuse, final figure/caption artifact leakage,
completion overclaim, and claim-strengthening.

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes
  `S08VisualFormalPlan`;
- S08 registry and stage contract preserve public graph I/O, strict worker
  packet coverage, and conditional designer/verifier lane policy;
- `examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml`
  validates and declares typed output, ordered internal passes from visual need
  to candidate to contract to evidence/backend/caption/coverage audit, and
  controls against final figures, final captions, new claims, claim
  strengthening, schematic-as-evidence misuse, and decorative visuals;
- `runtime/phase10_content_validators.json` contains S08-specific dimensions
  and checks for input coverage, visual needs, candidate decisions, visual
  budget, figure/table/formal contracts, panel evidence, claim bindings,
  backend routes, caption boundaries, accessibility constraints, coverage
  ledger, downstream handoffs, and visual safety audit.

Expected aggregate signal:

```text
PPG_S08_VISUAL_FORMAL_PLAN_OK
```


## S09A/S09B rich control selection and strict packet assembly

Positive fixtures:

- `examples/materials/phase10_s09a_rich_control_bundle.yaml`
- `examples/materials/phase10_s09b_task_packet_assembly.yaml`
- `examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml`

Negative fixtures cover S09A missing target unit, missing hard constraints,
missing rich local context, missing applicable S08 visual controls, missing
conflict resolution, missing context usage labels, stale freshness, missing
downstream packet requirements, blocking missing controls, final-content
leakage, and completion overclaim. S09B negative fixtures cover missing packet
identity, unsafe write path, missing strengthened forbidden routes, weak boot
clause, missing move plan, missing context usage, missing return format,
missing single-writer lock, authority expansion, candidate-content leakage,
completion overclaim, and missing emitted-packet trace.

The verifier also checks:

- `schemas/ppg-material-payloads.schema.json` includes
  `S09ARichControlBundle` and `S09BTaskPacketAssembly`;
- S09A/S09B registry and stage contracts preserve public graph I/O, keep
  `requires_worker_task_packet: false`, reject fake worker-packet coverage,
  and retain deterministic single-lane validation;
- `examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml` validates
  as an S10 TaskPacket while carrying strengthened S09B forbidden routes and a
  single write path;
- `runtime/phase10_content_validators.json` contains S09A dimensions/checks
  for rich layered control selection and S09B dimensions/checks for strict
  authority-safe packet assembly;
- bare `S09` does not appear as a stage id.

Expected aggregate signal:

```text
PPG_S09_CONTROL_PACKET_ASSEMBLY_OK
```

## S10 packet-bounded candidate text production

Positive fixtures:

- `examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml`
- `examples/candidate-artifacts/phase10_intro_callout_candidate.md`
- `examples/candidate_returns/phase10_intro_callout_candidate_return.json`
- `examples/materials/phase10_s10_candidate_text_return.json`

Negative fixtures cover missing packet compliance, unsafe write paths,
completion overclaim, forbidden candidate body expressions, missing
claim/evidence trace, terminology/internal-id leakage, object granularity
violations, visual callout misuse, non-clean forbidden-expression scan,
unresolved coverage requirements, CandidateArtifactReturn authority escape,
missing writer evidence, missing verifier evidence, blocked missing-material
status, and final-acceptance leakage.

The verifier also checks:

- `S10CandidateTextReturn` is present in the payload schema;
- the S10 registry and stage contract preserve graph-level consumes/produces,
  retain mandatory writer/verifier split, and link the strict S09B packet;
- the candidate artifact validates as `ppg-section-draft/v0.1`;
- the candidate return validates against the originating S09B packet;
- phase10 validator dimensions include packet compliance, candidate unit,
  claim/evidence trace, move trace, terminology/object/visual traces,
  forbidden-expression scan, coverage, CandidateArtifactReturn, and
  writer/verifier evidence.

Expected aggregate signal:

```text
PPG_S10_CANDIDATE_TEXT_RETURN_OK
```

## S11 contract-bound visual/formal artifact production

Positive fixtures:

- `examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml`
- `examples/candidate-artifacts/phase10_s11_figure_caption_bundle.md`
- `examples/candidate_returns/phase10_s11_figure_caption_bundle_return.json`
- `examples/materials/phase10_s11_figure_caption_artifact_bundle.json`

Negative fixtures cover missing S08 contract compliance, proof-role drift,
unsafe paths, missing render/render-plan, missing source-data trace, missing
panel trace, caption-claim boundary violation, visual polish changing claim
meaning, incomplete polish policy, accessibility failure, final-export
overclaim, unresolved coverage, CandidateArtifactReturn authority escape,
missing verifier evidence, completion overclaim, and blocked missing-material
status.

The verifier also checks:

- `S11FigureCaptionArtifactBundle` is present in the payload schema;
- the S11 packet includes authority/target, S08 contract, panel evidence,
  source data package, terminology/surface controls, visual quality profile,
  and visual polish policy;
- the S11 registry and contract preserve graph-level consumes/produces and
  link the strict S11 packet;
- phase10 validator dimensions include packet compliance, S08 contract
  preservation, source provenance, panel/caption claim trace, render or
  render-plan integrity, polish-without-meaning-drift, accessibility, export
  manifest, CandidateArtifactReturn, and verifier evidence.

Expected aggregate signal:

```text
PPG_S11_FIGURE_CAPTION_ARTIFACT_BUNDLE_OK
```

## S12 structured integration and consistency audit

Positive fixtures:

- `examples/packets/phase10_s12_integration_consistency_packet.v1.yaml`
- `examples/materials/phase10_s12_integration_report.json`
- `examples/candidate_returns/phase10_s12_integration_report_return.json`

Negative fixtures cover missing module inventory, PDF/export claims, S16 export
readiness overclaim, untracked rewrite, missing trace index, untraced claims,
overpromised reader promises, failed cross-section consistency, stale recompile
requirements, malformed findings, invalid backflow stage, validator blocking
S13, CandidateArtifactReturn authority escape, and completion overclaim.

Expected aggregate signal:

```text
PPG_S12_INTEGRATION_CONSISTENCY_OK
```

## S13 adversarial review/loss-signal audit

Positive fixtures:

- `examples/packets/phase10_s13_adversarial_review_packet.v1.yaml`
- `examples/materials/phase10_s13_adversarial_review_report.json`
- `examples/candidate_returns/phase10_s13_adversarial_review_report_return.json`

Negative fixtures cover missing review-object inventory, PDF primary review,
PDF-review authority escape, uncontrolled rewrite, missing review modes,
missing reviewer-panel roles, malformed findings, missing evidence/location,
invalid severity or nearest stage, bypassing S14, whole-manuscript repair
scope, actionability gaps, CandidateArtifactReturn authority escape, missing
verifier checks, and completion overclaim.

Expected aggregate signal:

```text
PPG_S13_ADVERSARIAL_REVIEW_REPORT_OK
```


## S14 backflow repair-plan audit

Positive fixture:

- `examples/materials/phase10_s14_backflow_repair_plan.json`

Negative fixtures cover missing intake ledger, intake coverage gaps, invalid
failure type, bare `S09` routing, missing route rationale, missing stale nodes,
global rewrite scope, repair execution, missing task plan for an accepted
finding, missing response closure evidence, disabled owner gate, missing
stale-node validation plan, completion overclaim, and authority-boundary repair
execution.

Expected aggregate signal:

```text
PPG_S14_BACKFLOW_REPAIR_PLAN_OK
```


## S15 repair execution/local regeneration audit

Positive fixtures:

- `examples/packets/phase10_s15_scoped_repair_packet.v1.yaml`
- `examples/materials/phase10_s15_repair_execution_report.json`
- `examples/candidate_returns/phase10_s15_repair_execution_report_return.json`

Negative fixtures cover missing strict packet ack, invalid task kind, unsafe diff
path, global rewrite scope, invalid claim-boundary impact, bare `S09` packet
route, missing regenerated artifact, invalid downstream action, stale propagation
gap, missing unrelated-node preservation, invalid finding resolution status,
failed validator report, new high-severity risk, CandidateArtifactReturn escape,
blocked missing-material status, missing verifier checks, completion overclaim,
and authority-boundary export claim.

Expected aggregate signal:

```text
PPG_S15_REPAIR_EXECUTION_REPORT_OK
```

## S16 export/repository-hygiene/handoff audit

Positive fixture:

- `examples/materials/phase10_s16_export_handoff_package.json`

Negative fixtures cover bad readiness-state separation, unresolved upstream
closure, failed build, rendered-surface anomalies, missing manifest hashes,
missing handoff/build output manifest entries, manifest/hash mismatch, failed
figure/caption export checks, data-availability mismatch, unexpected dirty paths,
feedback misrouting, owner-gate escape,
submission-readiness field overclaim, narrative submission/publication overclaim,
unrelated-negation narrative overclaim bypasses, negated-first repeated-phrase
overclaim bypasses, authority-boundary submission claim,
projection/live-export boundary escape,
missing verifier checks, missing human-readable output, and unsafe export paths.

Projection fixtures do not claim physical filesystem proof. The live/projection
boundary verifier is:

```bash
python3 scripts/verify_s16_live_export_evidence.py \
  examples/materials/phase10_s16_export_handoff_package.json
```

It emits `PPG_S16_LIVE_EXPORT_EVIDENCE_PROJECTION_OK` for fixture projection
mode. A real owner-facing handoff must use `live_export` mode and pass physical
file existence, recomputed hash, and PDF/log checks before it can be treated as
live export proof.

Expected aggregate signal:

```text
PPG_S16_EXPORT_HANDOFF_PACKAGE_OK
```

## Local-paper projection

Standalone validation uses a repo-local sample paper workspace:

```bash
python3 scripts/import_local_paper_pilot.py \
  --source examples/sample-paper-workspace \
  --out examples/local-paper/sample-paper-workspace \
  --check
python3 scripts/generate_local_paper_full_pilot.py \
  --pilot-root examples/local-paper/sample-paper-workspace \
  --check
python3 scripts/verify_local_paper_full_pilot.py \
  examples/local-paper/sample-paper-workspace
```

A user’s private paper path may be imported as optional provenance when present, but it is not a standalone plugin acceptance dependency.

## Lifecycle fixture matrix

Positive:

- `examples/lifecycle/feedback_to_stage_improvement.valid.json`

Negative:

- `examples/lifecycle/invalid-unrouted-feedback.json`
- `examples/lifecycle/invalid-global-rewrite-repair.json`
- `examples/lifecycle/invalid-recursive-repair-authority.json`
- `examples/lifecycle/invalid-premature-stage-improvement.json`
- `examples/lifecycle/invalid-retrospective-submission-claim.json`
- `examples/lifecycle/invalid-active-omx-dependency.json`

Expected aggregate signal:

```text
PPG_LIFECYCLE_CONTRACT_OK
```

## S16 target-global delivery gate tests

The S16 target-global delivery gate is covered by focused fixture and live-export checks:

```bash
python3 scripts/verify_s16_export_handoff_package.py
python3 scripts/verify_s16_live_export_evidence.py examples/materials/phase10_s16_compiled_live_export_package.json
python3 scripts/verify_s16_live_export_evidence.py examples/materials/invalid-s16-live-export-template-pdf-text.json  # must fail E_S16_LIVE_TEXT
python3 scripts/verify_s16_live_export_evidence.py examples/materials/invalid-s16-live-export-missing-source-writeback-file.json  # must fail E_S16_LIVE_EVIDENCE
```

Regression expectations:

- S16 materials without `payload.delivery_target` fail `E_S16_DELIVERY_TARGET_REQUIRED`.
- Compiled targets with blocked readiness fail `E_S16_COMPILED_TARGET_GATE`.
- Compiled targets without source-writeback evidence fail `E_S16_SOURCE_WRITEBACK_REQUIRED`.
- Compiled targets without post-writeback validation fail `E_S16_POST_WRITEBACK_VALIDATION_REQUIRED`.
- Compiled targets with template/manuscript-not-started/placeholder rendered text fail `E_S16_PDF_SEMANTIC_SURFACE` or `E_S16_LIVE_TEXT`.
- Compiled targets whose rendered text/PDF manifest hashes drift from `rendered_surface_check` or `post_writeback_validation` fail `E_S16_HASH_MANIFEST_REQUIRED`.
- Live compiled targets whose source-writeback/post-writeback evidence refs do not exist or do not match manifest hashes fail `E_S16_LIVE_EVIDENCE`.
- Existing non-compiled export-hygiene/template handoffs remain valid only with explicit non-compiled `delivery_target`.

### Active-target downcast regression

`invalid-s16-export-handoff-implicit-active-target-downcast.json` proves that a package cannot omit the active-target source by declaring `requested_target_source: fixture_contract` while still carrying a compiled `active_target_kind`. Any declared `active_target_kind`/`active_target_ref` must bind to `delivery_target.kind` and `target_ref`/`target_ref_chain`; otherwise validation fails `E_S16_DELIVERY_TARGET_BINDING`.

## S09/S10 Material-Closure Validation

S09B validation must reject packets that provide only `allowed_read_paths` without explicit material closure and read obligations. Expected S09B error families include:

```text
E_S09B_CONTROL_DIGEST_POLICY_REQUIRED
E_S09B_GLOBAL_COVERAGE_REQUIRED
E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED
E_S09B_MATERIAL_ACCESS_MANIFEST_REQUIRED
E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED
E_S09B_DEFERRED_CONTROL_LEDGER_REQUIRED
E_S09B_SECTION_BLOCKERS_REQUIRED
```

S10 validation must reject candidate prose when material hydration is absent, incomplete, or blocked. Expected S10 error families include:

```text
E_S10_MATERIAL_HYDRATION_REQUIRED
E_S10_MATERIAL_READ_RECEIPT_REQUIRED
E_S10_BLOCKED_OUTPUT_REQUIRED
```

Final acceptance should run positive focused verifiers and negative fixtures for these codes; a positive-only green run is not sufficient for milestone acceptance.

## RenderedManuscriptAuditGate

Rendered manuscript quality is checked after S16 export/handoff evidence exists. S16 does not substitute for this gate. Positive and hostile fixtures live under `examples/delivery/`; run:

```bash
python3 scripts/verify_rendered_manuscript_audit_gate.py
```

Expected aggregate signal:

```text
PPG_RENDERED_MANUSCRIPT_AUDIT_GATE_OK
```

