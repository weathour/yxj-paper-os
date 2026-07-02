# Material Schema

## Shared material envelope

All paper materials use a common envelope plus typed payload.

```yaml
material_id:
material_type:
schema_version:
version:
status:
created_at:
created_by:
source_inputs:
artifact_path:
summary:
payload:
validators:
downstream_consumers:
invalidation_policy:
provenance:
```

## Status authority

A worker can propose `candidate` output. It cannot commit material. The main agent commits only after validation, provenance capture, and graph update.

## Core material families

### Semantic root

- `OwnerIntent`
- `OwnerDecision`
- `OwnerIntake`
- `OwnerSemanticContract`
- `PaperControlSpine`
- `PaperSpine`

#### S00 owner semantic materials

S00 uses typed material payloads rather than a normal worker task packet:

- `OwnerIntake` (`payload.schema_version: ppg-s00-owner-intake/v0.1`) preserves the original owner wording, activation reason, route assumptions, source/privacy constraints, claim-scope preferences, evidence limitations, and unresolved owner questions.
- `OwnerSemanticContract` (`payload.schema_version: ppg-s00-owner-semantic-contract/v0.1`) records the owner-confirmed or owner-gated route, ambition boundary, claim-family boundary, private-source policy, external-action boundary, blocked routes with unblock conditions, and downstream stale targets.

S00 remains `owner_gated`; workers may challenge or summarize but cannot commit these materials, change owner intent, strengthen claim scope, authorize private-source use, or claim submission/public-release readiness.

#### S01 source/citation/evidence inventory materials

S01 remains an inventory stage, not a claim-admissibility stage. It uses typed material payloads to make raw paper inputs, citations, evidence artifacts, figure source data, supplements, and provenance locatable for later stages:

- `S01InventoryInput` (`payload.schema_version: ppg-s01-inventory-input/v0.1`) is a read-only scan brief. It lists repository roots, manuscript/BibTeX/evidence/figure/supplement sources, S00 source/privacy policy, freshness requirements, and the `read_only_boundary` (`source_write_forbidden: true`, `inventory_candidate_only: true`).
- `S01SourceEvidenceInventory` (`payload.schema_version: ppg-s01-source-evidence-inventory/v0.1`) is the candidate inventory output. It records `source_map`, `citation_bank`, `evidence_bank`, `figure_source_data_inventory`, `data_availability_inventory`, `supplement_inventory`, `privacy_boundary_report`, `unresolved_locator_register`, `freshness_report`, `coverage_ledger`, and `candidate_return`.

S01 must preserve the public graph outputs `source map`, `citation bank`, and `evidence bank`; the richer fields are internal material structure. S01 may include support hints, but it must not decide support strength, allowed wording, claim admissibility, graph completion, manuscript completion, submission readiness, or publication readiness. S04 owns admissibility and wording.

#### S02 research scene / SOTA / exemplar / language profile materials

S02 remains a research-profile stage, not a writing, contribution-freeze, claim-admissibility, manuscript-integration, submission, or publication stage. It preserves the public graph outputs `research dossier`, `reader package`, `template profile`, and `citation verification report`; the richer structure is carried by `S02ResearchDossier` (`payload.schema_version: ppg-s02-research-dossier/v0.1`).

`S02ResearchDossier` requires:

- `research_scene_profile` with source locators and citation anchors;
- `sota_comparator_map` with source-located comparator families;
- `template_exemplar_profile` with an explicit no-copy boundary;
- `template_language_profile` covering paragraph functions, syntax patterns, lexical strength, citation patterns, quantitative style metrics, result narratives, and limitation language;
- `source_coverage_ledger`, `exemplar_sample_register`, `language_profile_sample_limits`, and `sota_family_coverage_ledger`;
- `unresolved_source_report` with S01/S00 backflow targets where needed;
- `downstream_handoff_coverage` for S03, S05, and S07;
- `descriptive_not_prescriptive_controls` and `misuse_guard`.

Quantitative language/style observations are descriptive priors only. They must be represented as ranges, quantiles, sample sizes, confidence notes, and sample limits rather than hard sentence-count, paragraph-count, cadence, or move-order rules. Exemplar language must not be copied. S02 cannot freeze contribution wording, final claim wording, graph completion, manuscript readiness, submission readiness, or publication readiness.

#### S03 contribution option classifier materials

S03 classifies possible contribution framings; it does not admit claims, freeze final wording, or write manuscript prose. Its typed output is `S03ContributionOptions` (`payload.schema_version: ppg-s03-contribution-options/v0.1`).

`S03ContributionOptions` requires:

- `contribution_option_queue` with every option classified as `supported`, `supportable_after_S04`, `weak`, `owner_gated`, or `rejected`;
- `sota_contrast_matrix` stating nearest SOTA family, actual difference, and what cannot be claimed;
- `evidence_readiness_score` as an S04 dependency signal, not final support strength;
- `unsupported_claim_register`, `rejected_option_register`, `owner_gated_option_register`, and `owner_gated_semantic_shift_log`;
- `reviewer_attack_map` and `contribution_coherence`;
- `option_coverage_ledger`, `sota_contrast_coverage`, `s04_handoff`, and `s04_handoff_coverage`;
- `anti_rhetoric_guard`, `unresolved_backflow_register`, and `candidate_return`.

S03 may hand claim candidates to S04 with evidence-readiness hints and forbidden-scope hints, but S04 alone decides claim admissibility, support strength, allowed wording, forbidden wording, and downstream use permission. S03 outputs must not contain final claim wording, admitted claims, allowed wording, graph completion, manuscript readiness, submission readiness, or publication readiness.

#### S04 claim admissibility materials

S04 is the evidence-to-claim safety gate. It consumes contribution options,
evidence/citation banks, result artifacts, and claim-boundary controls, then
returns `S04ClaimAdmissibility` (`payload.schema_version:
ppg-s04-claim-admissibility/v0.1`). It does not write final prose, compile a
manuscript, review a PDF, or claim graph/submission/publication readiness.

`S04ClaimAdmissibility` requires:

- `claim_queue`, `claim_unit_decomposition`, and `atomic_claim_register` so
  every claim-bearing unit is processed explicitly;
- `claim_capsules` with status `admitted`, `weakened`, `rejected`,
  `backflowed`, or `owner_gated`;
- `support_strength_map` using `strong`, `moderate`, `weak`,
  `background_only`, `unsupported`, or `forbidden`;
- `evidence_anchor_map` and `evidence_locator_coverage` with source/result/
  citation/artifact locators or explicit missing-locator backflow;
- `allowed_wording_map` and `forbidden_wording_map` with admitted wording,
  safe verbs/modifiers, required caveats, forbidden wording, and forbidden
  interpretations;
- `result_package_boundary_matrix` stating what each result artifact supports
  and does not support;
- `claim_transformation_log`, `claim_coverage_ledger`,
  `unsupported_claim_backflow_register`, `data_availability_plan`,
  `downstream_handoffs`, `downstream_use_permission_matrix`,
  `unresolved_backflow_register`, and `candidate_return`.

No admitted or weakened capsule may have `unsupported` or `forbidden` support.
Raw S03 contribution options are not writing-ready; S05, S07, S10, S12, and
S13 must consume S04 capsules and wording boundaries rather than raw novelty
framing.

#### S05 reader-spine controller materials

S05 is the paper-spine control stage. It consumes S02 research/profile
materials, S03 contribution options, S04 claim-admissibility capsules, and
claim-boundary controls, then returns `S05ReaderSpine`
(`payload.schema_version: ppg-s05-reader-spine/v0.1`). It does not add new
claims, strengthen S04 support, draft final prose, compile a manuscript, or
claim graph/manuscript/submission/publication readiness.

`S05ReaderSpine` requires:

- `admitted_claim_intake_ledger` so every S04 intake claim is placed,
  excluded, backflowed, or owner-gated with source capsule trace;
- `reader_question_inventory` and `reader_question_coverage_ledger` so every
  reader question has an answer path, deferral, backflow, or owner gate;
- `reader_spine.reader_question_progression`,
  `reader_spine.claim_to_section_spine`,
  `reader_spine.front_half_promise_map`, and
  `reader_spine.story_arc_matrix`;
- `reviewer_question_map` and `rationale_matrix` for reviewer attacks,
  section functions, claim support, dependencies, and removal risks;
- `claim_section_coverage_ledger`, `front_half_promise_coverage`,
  `excluded_claim_or_question_register`, and `owner_decision_log`;
- explicit `s06_handoff`, `s07_handoff`, `s08_handoff`, and
  `s06_s07_s08_handoff_coverage`;
- `coherence_overpromise_audit`, `unresolved_backflow_register`, and
  `candidate_return`.

S05 preserves the public graph outputs `reader spine`, `reviewer question
map`, and `rationale matrix`. The richer ledgers are internal payload
structure. S06/S07/S08 may consume S05 handoff controls, but S10 writing still
requires the later S09A/S09B packetization path; S05 alone is not writing-ready
manuscript material.


#### S06 object/granularity controller materials

S06 is the object-representation and granularity-control stage. It consumes
S05 reader spine/reviewer-question controls, S04 claim visibility, S02 template
profile context, and claim/terminology controls, then returns
`S06ObjectGranularity` (`payload.schema_version:
ppg-s06-object-granularity/v0.1`). It does not admit claims, redesign the
reader spine, plan final figures, prescribe final wording, draft final prose, or
claim graph/manuscript/submission/publication readiness.

`S06ObjectGranularity` requires:

- `object_inventory` and `mechanism_variable_inventory` so every detected
  paper object and variable is represented, deferred, downgraded, excluded,
  unresolved, or backflow-required;
- `object_cards` for P0/P1/P2 objects and `mechanism_variable_cards` for
  represented variables;
- `cross_maps` covering object relations, object-to-claim,
  object-to-reader-question, object-to-section, variable-to-object, and
  section-object-load maps;
- `granularity_progression_map`, `section_function_budget`,
  `cognitive_load_budget`, and `explanation_ladder`;
- `repetition_risk_register`, `coverage_ledger`, and
  `unresolved_object_report`;
- explicit `handoff_to_s07`, `handoff_to_s08`, and `handoff_to_s10`;
- `coherence_and_boundary_audit` and `candidate_return`.

S06 preserves the public graph outputs `object representation matrix`, `section
function budget`, `load budget`, and `explanation ladder`; the item-level
queues/cards/ledgers are stricter internal payload structure. S10 must consume
S06 through S09A/S09B task packets, not as direct free-form writing authority.


#### S07 rhetoric/surface-control materials

S07 is the claim-safe expression-control stage. It consumes S02 descriptive
language/profile controls, S04 claim capsules and allowed/forbidden wording,
S05 reader-spine and reviewer-question controls, S06 object/granularity
controls, and terminology inputs, then returns `S07RhetoricSurfaceControl`
(`payload.schema_version: ppg-s07-rhetoric-surface-control/v0.1`). It does not
write final manuscript prose, introduce or strengthen claims, copy exemplars,
turn S02 statistics into fixed sentence/paragraph rules, or claim graph/
manuscript/submission/publication readiness.

`S07RhetoricSurfaceControl` requires:

- `input_coverage_ledger` for S02/S04/S05/S06/terminology material coverage;
- `claim_surface_rule_map` binding S04 claim capsules to allowed/forbidden
  verbs, modifiers, qualifiers, caveats, citation attachment, and section use;
- `terminology_surface_register` for S06 object/variable reader-facing names,
  variants, notation policy, confusion risk, and claim-strength risk;
- `internal_id_ban_list`, `paragraph_job_map`, `rhetorical_move_matrix`, and
  `flexible_language_control`;
- `surface_rules`, `forbidden_expression_list`, `coverage_ledger`,
  `unresolved_surface_control_report`, `downstream_handoff`,
  `surface_safety_audit`, and `candidate_return`.

S07 preserves the public graph outputs `construction matrix`, `rhetorical
matrix`, `terminology register`, and `surface rules`; detailed expression
controls are internal payload structure.


#### S08 visual/formal planning materials

S08 is the visual/formal object contract stage. It consumes S04 claim/evidence
boundaries, S05 reader-question spine controls, S06 object/section budgets,
S01/evidence source-data inventories, terminology inputs, and optionally S07
surface controls, then returns `S08VisualFormalPlan` (`payload.schema_version:
ppg-s08-visual-formal-plan/v0.1`). It does not render final figures, write
final captions, introduce or strengthen claims, compile/export manuscripts, or
claim graph/manuscript/submission/publication readiness.

`S08VisualFormalPlan` requires:

- `authority_boundary_audit` and `input_coverage_ledger` so missing inputs and
  completion boundaries are explicit;
- `normalized_claim_evidence_table`, `visual_need_inventory`,
  `formal_visual_need_map`, `source_data_inventory_projection`, and
  `candidate_visual_object_queue` so needs precede figure ideas;
- `visual_budget` and `main_story_visual_path` so main visuals form an
  argument path without overload;
- `figure_contracts`, `table_contracts`, and `formal_object_contracts` for
  reader role, proof role, supported/unsupported claims, S04 capsule trace,
  source data, backend route, and caption boundary;
- `panel_evidence_map` and `visual_claim_evidence_map` so panels and visual
  claim bindings cannot exceed S04 evidence boundaries;
- `backend_route_map`, `main_supplement_split_plan`, `caption_legend_brief`,
  and `accessibility_and_style_constraints`;
- `coverage_ledger`, `unresolved_visual_object_report`,
  `downstream_handoff`, `visual_safety_audit`, and `candidate_return`.

S08 preserves the public graph outputs `visual budget`, `figure contract`,
`panel evidence map`, and `backend route`; item-level candidates, contracts,
caption briefs, accessibility constraints, and ledgers are stricter internal
payload structure. S11 consumes S08 for artifact generation; S08 itself is not
the final figure/caption/export stage.


#### S09A/S09B control-selection and packet-assembly materials

Bare `S09` is not a valid material or execution stage. The split is:

- `S09A` selects a target-specific, context-rich, priority-ordered control
  bundle;
- `S09B` compiles that bundle into one bounded, authority-safe TaskPacket for
  S10/S11/S15 execution.

S09A returns `S09ARichControlBundle` (`payload.schema_version:
ppg-s09a-rich-control-selection/v0.1`). It may include rich context, adjacent
context, global orientation, negative examples, and S08 visual/formal controls,
but every layer must be labeled by allowed use and misuse boundaries. It does
not compile worker packets, draft prose, generate figures, or claim graph/
manuscript completion.

`S09ARichControlBundle` requires:

- `authority_boundary_audit`, `target_unit_profile`, and `hard_constraints`;
- `local_context`, `adjacent_context`, and `global_orientation` with
  background-only labeling;
- `claim_control_bundle`, `reader_context_bundle`, `object_context_bundle`,
  `surface_control_bundle`, optional/applicable
  `visual_formal_control_bundle`, and `evidence_anchor_bundle`;
- `negative_control_bundle`, `conflict_resolution_log`,
  `control_priority_map`, and `context_usage_instructions`;
- `excluded_or_deferred_controls`, `freshness_check`,
  `missing_control_report`, `coverage_ledger`,
  `downstream_packet_requirements`, and `candidate_return`.

S09B returns `S09BTaskPacketAssembly` (`payload.schema_version:
ppg-s09b-task-packet-assembly/v0.1`). It records how the S09A bundle was
compiled into an emitted strict TaskPacket. It preserves S09A usage labels,
uses explicit allowed read/write paths, carries strengthened forbidden routes,
and proves single-writer, completion-forbidden, no-recursive authority.

`S09BTaskPacketAssembly` requires:

- `packet_identity`, `target_unit`, `selected_control_bundle_ref`,
  `control_digest`, and `task_mission`;
- `allowed_read_paths`, exactly scoped `allowed_write_paths`,
  `forbidden_routes`, and `worker_boot_clause`;
- `section_or_unit_move_plan` plus propagated claim, reader, object,
  terminology, visual/formal, negative, and context-usage controls;
- `validators`, `return_format`, `single_writer_lock`,
  `stale_material_policy`, `missing_material_report`,
  `packet_authority_boundary`, `emitted_task_packet`, and
  `candidate_return`.

S09A/S09B preserve public graph I/O: S09A still produces selected control
bundle, priority map, and missing-control report; S09B still produces task
packet, section move plan, single-writer lock, and missing-material report. The
stricter rich bundle and assembly record are internal payload structure.

#### S10 candidate text return materials

S10 returns `S10CandidateTextReturn` (`payload.schema_version:
ppg-s10-candidate-text-return/v0.1`) plus a packet-compatible
`CandidateArtifactReturn`. This is the first stage that contains candidate
paper prose, but it remains candidate-only: S10 does not own truth, acceptance,
completion, publication readiness, or submission readiness.

`S10CandidateTextReturn` requires:

- `completion_boundary` and `authority_boundary` with graph/manuscript/
  submission/publication completion, recursive dispatch, write escape, owner
  intent change, and final acceptance all false;
- `packet_compliance_report` proving S09B packet id, target unit, allowed
  read/write paths, validators, return format, forbidden routes, and
  single-writer lock were observed;
- `candidate_text_unit` with the actual candidate body for the target unit
  only, source materials, evidence anchors, and no graph completion claim;
- `section_or_unit_skeleton`, `move_trace`, `claim_evidence_trace`,
  `terminology_trace`, `object_granularity_trace`, and `visual_callout_trace`;
- `forbidden_expression_scan`, `coverage_ledger`, embedded
  `candidate_artifact_return`, `writer_execution_evidence`,
  `verifier_evidence`, `remaining_risks`, and `missing_material_report`.

S10 preserves public graph I/O: it still produces candidate text unit and
`CandidateArtifactReturn`. The trace ledgers are stricter internal payload
structure that S12/S13 can audit; they should not be converted into rigid
sentence-count or paragraph-count templates.

#### S11 figure/caption/formal artifact bundle materials

S11 returns `S11FigureCaptionArtifactBundle` (`payload.schema_version:
ppg-s11-figure-caption-artifact-bundle/v0.1`) plus a packet-compatible
`CandidateArtifactReturn`. It may improve clarity, readability, accessibility,
journal fit, and export planning, but it may not change S08 proof role, S04
claim boundaries, evidence encoding, supported claim sets, or required caveats.

`S11FigureCaptionArtifactBundle` requires:

- `completion_boundary`, `authority_boundary`, and `packet_compliance_report`;
- `figure_contract_compliance` preserving proof role, supported/unsupported
  claims, required panels, caption boundary, and accessibility constraints;
- `generated_artifacts`, `editable_source_bundle`, and either
  `rendered_output_bundle` or `render_plan_if_not_rendered`;
- `source_data_trace`, `panel_claim_trace`, `caption_legend_draft`, and
  `caption_claim_trace`;
- `image_integrity_record`, `visual_polish_policy`,
  `visual_polish_report`, `figure_statistics`, `accessibility_check`, and
  `export_manifest`;
- `coverage_ledger`, `candidate_artifact_return`, `verifier_evidence`,
  `remaining_risks`, and `missing_material_report`.

S11 preserves public graph I/O: it still consumes figure contracts, panel
evidence packages, source-data locators, and caption briefs; it still produces
figure statistics, image integrity record, caption brief, and figure export
bundle. The stronger bundle makes visual polish auditable rather than turning
S11 into an unconstrained design pass.

#### S12 integration and consistency report materials

S12 returns `S12IntegrationConsistencyReport` (`payload.schema_version:
ppg-s12-integration-consistency-report/v0.1`). It compiles a structured
integrated candidate package from S10/S11 outputs and audits consistency, but
it does not compile PDF, export final artifacts, claim final manuscript
completion, or perform untracked rewrites.

Required modules include `module_inventory`, `assembly_manifest`,
`integrated_manuscript_candidate`, `trace_index`, claim/promise/cross-section/
terminology/object/figure-text/surface/stale audits, `integration_findings`,
`backflow_queue`, `validator_report`, `candidate_artifact_return`, and
`remaining_risks`. Findings must include severity, evidence, affected
artifacts, nearest responsible stage, recommended backflow target, and repair
scope so S14/S15 can act without S12 silently repairing text.

S12 preserves public graph I/O: integrated manuscript candidate, consistency
findings, and validator report. The stronger package makes S13 review and
S14/S15 routing traceable while keeping S16 as the only PDF/export stage.

#### S13 adversarial review report materials

S13 returns `S13AdversarialReviewReport` (`payload.schema_version:
ppg-s13-adversarial-review-report/v0.1`). It reviews the structured S12
integrated candidate package, traces, S10/S11 candidate traces, and S04-S08
control materials. It does not use a PDF as the primary review object, rewrite
the manuscript, execute repairs, export PDF, or claim graph/manuscript/
submission/publication completion.

Required modules include `review_scope`, `review_object_inventory`,
reviewer-panel/desk-risk/reader-experience/claim-evidence/contribution/
method-result/figure-caption/structure/surface reports, `review_findings`,
`finding_actionability_report`, `validator_report`,
`candidate_artifact_return`, `verifier_evidence`, and `remaining_risks`.
Every accepted finding must include severity, evidence, affected artifact,
affected location, source trace, nearest responsible stage, local repair scope,
open resolution status, and `recommended_backflow_target: S14`.

S13 preserves the review-to-route boundary: it compiles actionable loss signals
for S14 rather than repairing text itself.


#### S14 backflow repair-plan materials

S14 returns `S14BackflowRepairPlan` (`payload.schema_version:
ppg-s14-backflow-repair-plan/v0.1`). It normalizes accepted S13/S16/validator
findings into nearest-responsible stage/material routes, stale/protected graph
slices, bounded repair task plans, response actions, owner-gate status, and a
validator-based closure plan.

S14 is controller-owned and has `requires_worker_task_packet: false`; a strict
worker packet must not be faked for this stage. The material is a plan only: it
must not rewrite text, regenerate figures, execute repairs, claim finding
resolution, export PDF, or mark graph/manuscript/submission/publication
completion.

Required modules include `finding_intake_ledger`,
`finding_normalization_table`, `nearest_responsible_stage_map`,
`affected_material_graph_slice`, `repair_scope_plan`, `repair_task_packets`,
`control_reselection_tasks`, `response_action_map`, `priority_schedule`,
`owner_gate_report`, `validation_plan`, `unresolved_or_ambiguous_findings`,
`validator_report`, and `remaining_risks`. Routes must target concrete stages
such as `S09A` or `S09B`; bare `S09` is invalid.


#### S15 repair execution report materials

S15 returns `S15RepairExecutionReport` (`payload.schema_version:
ppg-s15-repair-execution-report/v0.1`). It consumes a strict S14 repair packet,
target material base version, affected downstream stale set, and protected
unrelated node list. It produces a repair execution report, revised material
candidate, regenerated affected outputs, updated validator report, candidate
return, and verifier evidence.

S15 is the repair execution stage, but its output is still candidate-only:
controller graph commit, final manuscript state, PDF/export, submission, and
publication readiness remain outside S15 authority. Required modules include
`repair_task_ack`, `pre_repair_snapshot`, `target_material_diff`,
`revised_material_candidate`, regenerated packet/artifact logs,
`stale_resolution_report`, `unrelated_node_preservation_report`,
`finding_resolution_evidence`, `updated_validator_report`, `new_risk_scan`,
`candidate_artifact_return`, `missing_material_report`, `verifier_evidence`,
and `remaining_risks`.

### Analysis materials

- `TopicAnalysis`
- `TemplateProfile`
- `EvidenceInventory`
- `ExperimentResultInventory`
- `RelatedWorkPositioning`
- `ReaderProfile`
- `ReviewerConcernMap`
- `TerminologyInventory`

### Synthesis/control materials

- `ClaimBoundaryMap`
- `ClaimEvidenceMatrix`
- `ReviewerQuestionMap`
- `ObjectRepresentationMatrix`
- `MainTextConstructionMatrix`
- `CrossSectionDependencyMap`
- `TerminologyRegister`
- `CognitiveLoadBudget`
- `ExplanationLadder`
- `RhetoricalMoveMatrix`
- `ClaimEvidenceVisibilityMap`

### Stage-local overlay materials

Stage-local overlays are profile/control materials consumed by existing stages. They do not create new routes or completion authority.

- `StageOverlayRegistry`
- `StageOverlayBinding`
- `VenueProfile`
- `VenueClaimBoundaryMap`
- `VenueFigureContract`
- `VenueReaderExperienceRubric`
- `VenueSurfaceControlProfile`

### Production materials

- `WritingTaskPacket`
- `RepairTaskPacket`
- `FigureTaskPacket`
- `SectionDraft`
- `CaptionDraft`
- `FigureDraft`
- `FullManuscriptCandidate`

### Review, feedback, and backflow materials

- `ReviewFeedbackPackage`
- `FailureAttributionRecord`
- `EvidenceReviewReport`
- `ReaderExperienceReviewReport`
- `TemplateComplianceReport`
- `TerminologyLeakReport`
- `RenderedSurfaceGateReport`
- `AdversarialReviewerReport`
- `ReviewFinding`
- `BackflowTask`
- `RunRetrospectiveReport`
- `StageImprovementRecord`

## Lifecycle object summaries

### ReviewFeedbackPackage payload

```yaml
feedback_source:
summary:
observed_problem:
severity:
affected_artifact:
candidate_failure_types:
```

### FailureAttributionRecord payload

```yaml
feedback_package_id:
nearest_stage:
responsible_material:
failure_level:
owner_gate_required:
repair_scope:
preserve_scope:
forbidden_repair_routes:
downstream_stale_targets:
```

### RepairTaskPacket payload

```yaml
attribution_id:
target_material:
repair_action:
preserve:
must_change:
must_not_change:
allowed_write_paths:
expected_output:
validators:
completion_forbidden: true
no_recursive_orchestration: true
```

### StageImprovementRecord payload

```yaml
stage_id:
failure_pattern:
evidence_count:
root_cause:
recommended_prompt_change:
recommended_task_packet_change:
recommended_validator_change:
regression_test_needed:
```

### RunRetrospectiveReport payload

```yaml
run_id:
feedback_packages:
stage_improvements:
lessons:
blocked_improvements:
```

## Generation method classification

| Method | Use case |
| --- | --- |
| `agent_generated` | semantic design, writing, critique |
| `script_generated` | deterministic scans, schema checks, manifests |
| `hybrid_generated` | LLM candidate plus program validation |
| `manual_owner_decision` | semantic commitments only the owner can make |

## Sidecar pollution rule

Validators should lint paper-facing text fields such as `draft_text`, `caption_text`, `claim_text`, `summary_for_reader`, `paragraph`, or blocks explicitly marked `paper_facing: true`. They should not fail registry/control metadata merely because those fields contain internal runtime terms.
