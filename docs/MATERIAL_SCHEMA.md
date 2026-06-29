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

