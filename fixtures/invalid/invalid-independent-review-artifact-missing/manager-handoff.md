# Manager handoff

```yaml
authority_role_separation:
  manager_direct_used: true
  manager_direct_interventions: [MDI-001]
  inferred_manager_direct: true
  execution_actor_id: manager:session-main
  final_certifier_actor_id: verifier:final-001
  reviewer_actor_id: reviewer:critic-001
  independent_review_required: true
  independent_review_artifacts: [reviews/missing-independent-review.yaml]
  completion_claim: complete
  completion_limit_reason: independent review and final certifier separation present
  residual_self_certification_risk: none
```
