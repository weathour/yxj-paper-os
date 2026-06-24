# Manager Handoff Report v2

## 30-second manager summary
- current_state:
- active_gate:
- last_verified_task:
- recommended_next_safe_route:
- hard_gated_actions:
- repository_hygiene_state: clean | dirty_allowed | dirty_blocked | owner_gated
- delivery_cleanliness_gate: pass | blocked | owner_gated

## Department table
| Department | Owner lane / agent | Inputs consumed | Outputs produced | Narrative/template refs | Closure state | Evidence | Risks/blockers | Owner attention | Final-paper impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PMO / Paper Management | state-steward |  |  |  | planned |  |  |  |  |
| Repository hygiene / Delivery cleanliness | repository-hygiene-owner / verifier | git status, ledger snapshot, export manifest | RepositoryHygieneReport | n/a unless handoff affects narrative/template objects | planned |  |  |  | reproducibility, rollback, clean handoff, and submission-package trust |


## Authority & Role Separation
```yaml
authority_role_separation:
  manager_direct_used: false
  manager_direct_interventions: []
  inferred_manager_direct: false
  execution_actor_id: null
  final_certifier_actor_id: null
  independent_review_required: false
  independent_review_artifacts: []
  completion_claim: candidate # candidate | validated | complete
  completion_limit_reason: null
  residual_self_certification_risk: none # none | low | medium | high
```

## Decision queue
| decision_id | owner question | options | recommended option | consequence of no decision | blocks/enables | trigger/deadline |
| --- | --- | --- | --- | --- | --- | --- |

## Verification appendix
- commands:
- validator outcomes:
- fixture matrix status:
- repository hygiene / delivery cleanliness:
  - worktree status:
  - dirty counts by scope:
  - sibling/parent contamination:
  - generated/ephemeral entries:
  - disallowed entries:
  - cleanup actions / owner decisions:
- ledger/snapshot guard:
- changed files/artifacts:
- commit hash if any:
- residual risks / unverified gaps:
