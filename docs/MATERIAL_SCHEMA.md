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
- `PaperControlSpine`
- `PaperSpine`

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
