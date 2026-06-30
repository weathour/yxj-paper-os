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

A subagent can propose `candidate` output. It cannot commit material. The main agent commits only after validation and graph update.

## Core material families

### Semantic root

- `OwnerIntent`
- `PaperControlSpine`
- `PaperSpine`

### Analysis materials

- `TopicAnalysis`
- `TemplateProfile`
- `EvidenceInventory`
- `ReaderProfile`
- `ReviewerConcernMap`
- `TerminologyInventory`
- `ExperimentResultInventory`
- `RelatedWorkPositioning`

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

Stage-local overlays are profile/control materials consumed by existing stages. They do not create new stages or departments.

- `StageOverlayRegistry`
- `StageOverlayBinding`
- `NatureVenueProfile`
- `NatureClaimBoundaryMap`
- `NatureFigureContract`
- `NatureReaderExperienceRubric`
- `NatureSurfaceControlProfile`

The first active overlay is `nature_expert_writing` in `runtime/stage_overlay_registry.json`. Its controls are transported through existing TaskPacket `mandatory_controls` and `validators`, not through new top-level worker authority fields.

### Production materials

- `WritingTaskPacket`
- `FigureTaskPacket`
- `SectionDraft`
- `CaptionDraft`
- `FigureDraft`
- `FullManuscriptCandidate`

### Review and backflow materials

- `EvidenceReviewReport`
- `ReaderExperienceReviewReport`
- `TemplateComplianceReport`
- `TerminologyLeakReport`
- `RenderedSurfaceGateReport`
- `AdversarialReviewerReport`
- `ReviewFinding`
- `BackflowTask`

## Example: ClaimEvidenceMatrix payload

```yaml
claims:
  - claim_id:
    claim_text:
    allowed_strength:
    evidence_refs:
    limitations:
    forbidden_wording:
```

## Example: WritingTaskPacket payload

```yaml
target_section:
target_unit:
mission:
input_materials:
constraints:
  forbidden_terms:
  required_moves:
  claim_strength_limits:
validators:
backflow_routes:
expected_output:
```

## Generation method classification

Every material declares one method:

| Method | Use case |
| --- | --- |
| `agent_generated` | semantic design, writing, critique |
| `script_generated` | deterministic scans, schema checks, manifests |
| `hybrid_generated` | LLM candidate plus program validation |
| `manual_owner_decision` | semantic commitments only the owner can make |

## Phase 4 machine-checkable subset

The full material ontology remains larger than the executable MVP. Phase 4 freezes a machine-checkable subset that is sufficient for the current overclaim/backflow vertical slice.

### P0 runtime objects

| Object | Schema | Validator |
| --- | --- | --- |
| `ReviewFinding` | `schemas/ppg-review-finding.schema.json` | `scripts/validate_review_finding.py` |
| `BackflowTask` | `schemas/ppg-backflow-task.schema.json` | `scripts/validate_backflow.py` |
| `ReviewClosure` | `schemas/ppg-review-closure.schema.json` | `scripts/validate_delivery_gate.py` |
| `DeliveryGate` | `schemas/ppg-delivery-gate.schema.json` | `scripts/validate_delivery_gate.py` |
| `TaskPacket` | `schemas/ppg-task-packet.schema.json` | `scripts/validate_packet.py` |

### P1 vertical slice

`schemas/ppg-material-payloads.schema.json` and `scripts/validate_material.py` currently check:

- `EvidenceInventory.evidence_packages`;
- `ClaimBoundaryMap.allowed_claims[*].strength` plus forbidden wording/claim guardrails;
- `ReaderSpine.questions`;
- `TerminologyRegister` as a registry material that may list stale/blocked terms without being treated as paper-facing leakage.

`ClaimEvidenceVisibilityMap`, selected control bundles, section-draft shape, and figure contract/panel evidence maps are deferred until a later phase chooses them as concrete backflow or writing targets.

## Phase 11 stage-overlay registry subset

Phase 11 adds a machine-checkable stage-local overlay registry for expert writing profiles:

- `runtime/stage_overlay_registry.json` stores overlay authority, per-stage input controls, output materials, packet clauses, validator checks, and backflow targets.
- `schemas/ppg-stage-overlay-registry.schema.json` defines the registry shape.
- `scripts/verify_stage_overlays.py` enforces canonical stage bindings, bare-`S09` rejection, no-department authority, StageContract links, TaskPacket overlay clauses, and content-validator coverage.

Overlay bindings may shape stage-specific materials, but they cannot mark graph nodes complete or dispatch workers.

### Sidecar pollution rule

Phase 4 lints only paper-facing text fields such as `draft_text`, `caption_text`, `claim_text`, `summary_for_reader`, `paragraph`, or blocks explicitly marked `paper_facing: true`. It does not fail registry/control fields such as `stale_terms`, `forbidden_terms`, ids, schema names, provenance, or validator metadata merely because those fields name internal runtime terms.
