# Topology — Explicit Paper Material Graph

## Graph form

The runtime graph is a versioned directed graph with explicit backflow. Each forward pass is a DAG. Backflow creates new versions instead of mutating old nodes in place.

```text
MaterialNode(v1) -> TransformTask -> MaterialNode(v1 output)
ReviewFinding -> BackflowTask -> MaterialNode(v2)
MaterialNode(v2) --supersedes--> MaterialNode(v1)
```

## Node types

| Node type | Purpose | Examples |
| --- | --- | --- |
| `owner_intent` | Human semantic root and hard constraints | topic, venue, forbidden routes |
| `material` | Analysis/design/control material | ClaimBoundaryMap, TerminologyRegister |
| `transform_task` | Converts inputs to candidate outputs | compile ReviewerQuestionMap |
| `agent_run` | Provenance record for a specialist run | writer/verifier/researcher run |
| `validator` | Checks material or artifact | schema check, claim support check |
| `validation_report` | Result of validator execution | pass/fail report |
| `manuscript_artifact` | Paper-facing output | section draft, caption, full manuscript |
| `review_finding` | Loss signal from review | overclaim, terminology leak |
| `backflow_task` | Targeted repair task | repair ClaimEvidenceVisibilityMap |

## Edge types

| Edge type | Meaning | Invalidates downstream? |
| --- | --- | --- |
| `consumes` | target uses source as input | yes, if hard dependency |
| `constrains` | source limits target wording/structure | yes, scoped |
| `produces` | task creates output | no by itself |
| `validates` | validator checks target | no; report decides |
| `reports` | validator/review emits report | no by itself |
| `invalidates` | finding marks node stale/rejected | yes |
| `repairs` | backflow task repairs target | creates new version |
| `supersedes` | new version replaces old version | yes for downstream consumers of old active version |
| `references` | weak reference/provenance only | warning, not automatic stale |

## Layer topology

```text
Layer 0: Owner Intent / Semantic Root
Layer 1: Parallel Analysis Materials
Layer 2: Synthesis and Control Materials
Layer 3: Task Packet Compilation
Layer 4: Writing / Figure / Formal Production
Layer 5: Integration / Manuscript Candidate
Layer 6: Review / Loss / Backflow
```

## Canonical forward chain

```text
OwnerIntent
  -> TopicAnalysis / TemplateProfile / EvidenceInventory / ReaderProfile / TerminologyInventory
  -> PaperSpine / ClaimBoundaryMap / ReviewerQuestionMap / ObjectRepresentationMatrix
  -> MainTextConstructionMatrix / ClaimEvidenceVisibilityMap / TerminologyRegister
  -> WritingTaskPacket
  -> SectionDraft / FigureDraft / CaptionDraft
  -> FullManuscriptCandidate
  -> ReviewFinding
  -> BackflowTask
  -> targeted upstream material version
```

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `planned` | node is required but not produced |
| `candidate` | output exists but is not validated |
| `validated` | validators passed, not yet committed as active graph state |
| `committed` | active graph state uses this version |
| `stale` | dependency changed; node must be regenerated or reviewed |
| `rejected` | validator/review says output cannot be used |
| `blocked` | missing machine evidence or failed validator prevents progress |
| `owner_gated` | human semantic decision is required |

## Versioning rule

Do not overwrite old material nodes. Repairs create a new version:

```text
claim_boundary_map@v1 --superseded_by--> claim_boundary_map@v2
```

Downstream nodes that consumed `v1` are marked `stale` unless the edge is `references` or a validator accepts non-impact.

## Graph invariants

1. Every committed material has at least one provenance source.
2. Every manuscript artifact has a task packet and at least one control material input.
3. Every review finding has a failure type and a proposed backflow target.
4. Every backflow task targets exactly one primary node and may list secondary affected nodes.
5. No subagent can mark a node `committed`; only the main-agent commit protocol can.
6. Owner intent nodes cannot be changed by agent inference; changes require owner decision evidence.
7. A stale upstream control node prevents dependent writing packets from closing.

