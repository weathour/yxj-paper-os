# Backflow Protocol — Local Backpropagation

## Principle

Review does not trigger whole-paper rewrite by default. It emits loss signals that the main agent maps to upstream material nodes.

```text
review finding -> classify -> locate source node -> mark stale/rejected -> compile repair task -> regenerate affected downstream outputs
```

## Review finding schema

```yaml
ReviewFinding:
  finding_id:
  severity:
  failure_type:
  evidence:
  affected_artifacts:
  suspected_source_node:
  recommended_backflow_level:
  repair_constraints:
```

## Backflow levels

| Level | Failure class | Primary target |
| --- | --- | --- |
| `L0_surface` | grammar, local expression | `SectionDraft` |
| `L1_terminology` | internal codes, inconsistent labels | `TerminologyRegister` |
| `L2_rhetorical` | unclear paragraph function, reader question gap | `MainTextConstructionMatrix`, `ReviewerQuestionMap` |
| `L3_claim_evidence` | overclaim, missing evidence, wrong baseline | `ClaimBoundaryMap`, `ClaimEvidenceMatrix`, `ClaimEvidenceVisibilityMap` |
| `L4_spine` | contribution/paper problem mismatch | `PaperSpine`, `OwnerIntent` |

## Backflow task schema

```yaml
BackflowTask:
  backflow_id:
  source_finding:
  target_node:
  target_version:
  repair_mission:
  constraints:
  affected_downstream_nodes:
  validators:
  owner_gate_required:
```

## Stale propagation

When a control node changes:

1. find downstream edges with `consumes` or `constrains`;
2. mark dependent nodes `stale`;
3. preserve old versions for provenance;
4. compile repair packets for only impacted nodes;
5. rerun validators on impacted manuscript units.

## Owner gate

Backflow to `OwnerIntent` or core `PaperSpine` is owner-gated. The main agent may summarize alternatives and consequences, but it must not invent a new paper commitment.

