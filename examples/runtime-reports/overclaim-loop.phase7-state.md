# PPG Runtime State Report

## Graph
- graph_id: phase2-overclaim-material-graph
- title: Deterministic Overclaim Repair Vertical Slice
- source_path: examples/runtime/overclaim-loop.phase7-after.json
- nodes: 22
- edges: 31

## Next Frontier
- id: claim_boundary_map_candidate_v3
- kind: material
- priority: 5
- reason: candidate_material_awaiting_validation_or_commit_plan

## Active Versions
- claim_boundary_map -> claim_boundary_map_v2 (committed, v2)
- evidence_inventory -> evidence_inventory_v1 (committed, v1)
- reader_spine -> reader_spine_v1 (committed, v1)

## Stale Materials
- claim_boundary_map_v1: claim_boundary_map@v1; historical=true; active_path=false

## Candidate Materials
- claim_boundary_map_candidate_v3: candidate_for=claim_boundary_map; status=candidate; supersedes=

## Owner Decisions
- none

## Open Review Findings
- finding_overclaim_v1: claim_overreach; closure_status=open; classified_repair=true; repair_tasks=repair_claim_boundary_task_v1

## Closed Review Findings
- phase7_overclaim_review_finding_v1: claim_overreach; closed_by=phase7_overclaim_closure_v1; repair_tasks=phase7_overclaim_review_finding_v1_backflow_v1

## Backflow Tasks
- phase7_overclaim_review_finding_v1_backflow_v1: planned; artifact=examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml
- repair_claim_boundary_task_v1: validated; artifact=

## Delivery Gates
- phase7_delivery_gate_v1: validated; validates=none

## Review Closures
- phase7_overclaim_closure_v1: validated; validates=phase7_overclaim_review_finding_v1,phase7_delivery_gate_v1

## Completion Blockers
- candidate claim_boundary_map_candidate_v3 cannot commit: candidate status must be validated before commit; candidate must declare supersedes=claim_boundary_map_v2; candidate must have supersedes edge claim_boundary_map_candidate_v3 -> claim_boundary_map_v2; candidate-specific validator edge is required; candidate-specific validation report reference is required
