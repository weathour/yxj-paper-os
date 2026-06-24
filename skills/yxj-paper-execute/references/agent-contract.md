# Agent contract

This contract is backed by the canonical lane registry in `agent-lane-registry.yaml`. Runtime/state validators must derive owner-lane closure from that registry, not from a stale hard-coded subset.

## Native subagent rule

Every direct task must declare a concrete OMX/Codex native `agent_type` from the registry. `paper-owner-gate` is not a subagent lane; it routes to `omx_question` and a decision-ledger entry. Do not use `worker` as a general-purpose subagent outside active Team/Swarm runtime.

## V2 department/material binding rule

Every registry lane now belongs to exactly one v2 department and declares the material object classes it consumes and produces. A compiled task packet must mirror the registry row with `owner_department`, `input_materials`, `expected_output_materials`, `validator_refs`, `backflow_route`, `state_ingestion`, and the normal runtime fields. If `narrative_binding_required` or `template_binding_required` is true for the lane, the task must carry non-empty `narrative_object_refs` or `template_object_refs` respectively. A task-local exception is not enough; non-applicability must be independently accepted in `validator-report.yaml`.

This is the management handoff boundary: the manager dispatches people/agents through lanes, but the lane closes only when its material I/O is collected, validated, ingested, and transitioned. PUA telemetry remains an escalation/control artifact and never substitutes for the declared validators.

## Canonical lane-to-agent/material closure table

| owner_lane | department | lane kind | route/agent_type | material inputs | material outputs | reader/template binding | validator_refs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `profile-architect` | `pmo` | `direct_subagent` | `architect` | paper-profile, workspace-contract, department-io-contract | paper-profile-policy, profile-validation-plan | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `interview-owner` | `pmo` | `direct_subagent` | `analyst` | owner-question, paper-profile, decision-ledger | decision-brief, owner-gated-decision-record | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `state-steward` | `pmo` | `direct_subagent` | `verifier` | task-ledger, artifact-ledger, validator-report | state-transition-record, manager-state-snapshot | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `source-map-curator` | `evidence_and_method` | `direct_subagent` | `explore` | paper-profile, local-source-locators | source-map, privacy-boundary-report | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `scene-analyst` | `paper_architecture_and_narrative` | `direct_subagent` | `researcher` | target-venue-route, reader-spine-brief, source-map | scene-analysis-brief, reviewer-expectation-map | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `exemplar-learner` | `paper_architecture_and_narrative` | `direct_subagent` | `researcher` | allowed-exemplar-set, template-quant-profile | template-quant-profile, section-function-budget | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `sota-mapper` | `evidence_and_method` | `direct_subagent` | `researcher` | source-map, citation-bank, reader-spine-brief | sota-gap-map, claim-risk-map | narrative | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `novelty-panel` | `paper_architecture_and_narrative` | `direct_subagent` | `researcher` | sota-gap-map, reader-spine-brief, evidence-bank | novelty-options, assumption-risk-register | narrative | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `citation-banker` | `evidence_and_method` | `direct_subagent` | `researcher` | source-map, claim-list | citation-bank, citation-support-map | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `evidence-curator` | `evidence_and_method` | `direct_subagent` | `verifier` | claim-list, source-map, reader-spine-brief | evidence-bank, claim-support-matrix | narrative | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `paper-architect` | `paper_architecture_and_narrative` | `direct_subagent` | `planner` | reader-spine-brief, object-representation-matrix, template-quant-profile, evidence-bank | contribution-map, section-blueprint, section-function-budget | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `manuscript-owner` | `manuscript_and_figure_production` | `direct_subagent` | `writer` | section-blueprint, object-representation-matrix, evidence-bank, section-function-budget | manuscript-section-draft, reader-transition-map | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `method-verifier` | `evidence_and_method` | `direct_subagent` | `verifier` | method-description, object-representation-matrix, evidence-bank | method-contract, experiment-validity-report | narrative | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `figure-owner` | `manuscript_and_figure_production` | `direct_subagent` | `executor` | visual-table-algorithm-formula-budget, evidence-bank, object-representation-matrix | figure-plan, caption-brief, visual-provenance-record | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `review-director` | `review_and_governance` | `direct_subagent` | `critic` | manuscript-draft, reader-spine-brief, object-representation-matrix, template-quant-profile | reader-experience-review-report, narrative-backflow-task | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `style-auditor` | `review_and_governance` | `direct_subagent` | `verifier` | manuscript-draft, reader-spine-brief, section-function-budget | style-audit-report, lab-notebook-smell-findings | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `export-owner` | `manuscript_and_figure_production` | `direct_subagent` | `executor` | validated-manuscript, figure-package, export-manifest | export-package, readiness-report | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `repository-hygiene-owner` | `pmo` | `direct_subagent` | `verifier` | git-status-snapshot, task-ledger, export-manifest | RepositoryHygieneReport, delivery-cleanliness-gate | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_repository_hygiene_report |
| `yxj-wiki-bridge` | `evidence_and_method` | `direct_subagent` | `researcher` | yxj-wiki-query, source-map | wiki-source-capsule, source-support-note | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `research-director` | `paper_architecture_and_narrative` | `umbrella` | `researcher` | scene-analysis-brief, template-quant-profile, sota-gap-map | research-route-plan, research-synthesis | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `execution-coordinator` | `pmo` | `direct_subagent` | `executor` | task-packet, agent-lane-registry, department-io-contract | compiled-task-packet, execution-collection-plan | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `paper-owner-gate` | `pmo` | `user_gate` | `omx_question` | owner-gated-question, decision-context | decision-ledger-entry, semantic-authority-record | none | validate_decision_ledger, validate_motivation_confirmation, validate_agent_lane_department_binding, validate_task_material_io |
| `verifier` | `review_and_governance` | `alias` | `verifier` | validator-report, task-ledger, artifact-ledger | verification-summary, closure-risk-note | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `final-verifier` | `review_and_governance` | `direct_subagent` | `verifier` | all-validator-evidence, manager-handoff-report-v2 | final-closure-report, residual-risk-register | narrative, template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `artifact-schema-designer` | `pmo` | `direct_subagent` | `architect` | department-io-contract, reader-narrative-governance | artifact-schema, template-contract | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `docs-writer` | `pmo` | `direct_subagent` | `writer` | validated-contracts, manager-handoff-report-v2 | operation-doc-update, migration-doc-update | template | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io, validate_narrative_object_binding, validate_template_object_binding |
| `migration-owner` | `pmo` | `direct_subagent` | `planner` | v1-state, v2-contracts, fixture-matrix | migration-plan, compatibility-report | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `plugin-packaging-lane` | `pmo` | `scaffold_lane` | `executor` | source-scaffold, plugin-manifest | packaging-readiness-report | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `scaffold-executor` | `pmo` | `scaffold_lane` | `executor` | scaffold-checklist, source-tree | scaffold-patch, scaffold-validation-report | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `workspace-architect` | `pmo` | `scaffold_lane` | `architect` | workspace-contract, paper-root-evidence | workspace-layout-plan, root-detection-policy | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `domain-analyst` | `pmo` | `scaffold_lane` | `analyst` | domain-brief, paper-profile | domain-spec, routing-matrix | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `validator-designer` | `review_and_governance` | `scaffold_lane` | `test-engineer` | validator-contract, fixture-matrix | validator-implementation-plan, fixture-coverage-report | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |
| `omx-workflow-router` | `pmo` | `scaffold_lane` | `planner` | ralplan-handoff, ultragoal-ledger, team-gate-policy | workflow-route-decision, gate-status-report | none | validate_task_packet, validate_subagent_output, validate_task_status_transitions, validate_pua_telemetry, validate_agent_lane_department_binding, validate_task_material_io |

## Required task prompt fields

Each native subagent task prompt must include:

- scoped context paths from the registry row plus task-specific inputs;
- read/write scope;
- `owner_department`, `owner_lane`, and `agent_type` or non-subagent route;
- `input_materials` consumed and `expected_output_materials` to produce;
- `narrative_object_refs` / `template_object_refs` when required by the lane;
- expected output artifacts and collection path;
- state-ledger path, state-ingestion plan, and backflow route;
- validator refs, including the v2 material/narrative/template validators and `validate_repository_hygiene_report` when repository/delivery cleanliness is in scope;
- prohibition on marking dispatch as completion.

## Validator evidence closure

For completion, every `validator_ref` must have passing evidence either in task-level `validator_evidence[]` or in `validator-report.yaml#validators_run[]`. Partial validator evidence is not sufficient. V2 closure additionally requires the registry department to match `owner_department`, the declared material inputs/outputs to be non-empty and collected/ingested as applicable, required narrative/template refs to point to known governance objects, and repository/delivery lanes to produce a passing `RepositoryHygieneReport`.

## Team boundary

Use OMX Team only after RALPLAN and explicit user confirmation for the current story. Workers return artifacts and evidence; the leader owns Ultragoal checkpoints and state transitions.

## Managed-agent pressure protocol

Every managed LLM agent receives a bounded task prompt and is accountable to the Paper Orchestrator. The prompt must include:

```text
[PUA-DIAGNOSIS]
problem/goal is ___;
evidence is ___;
next action is ___.
```

The agent must answer the owner-four-questions before execution: root cause/target, impact surface, prevention/check, and data/evidence. If the agent fails twice or repeats the same approach, it must stop the current line, switch hypotheses, and return `[PUA-REPORT]` at L2+ with failure count, failure mode, attempts, excluded causes, next hypothesis, and requested manager action. L3+ requires the seven-item checklist. The leader records this in `pua_telemetry`.

`pua_telemetry` is a pressure and coordination artifact only. It does not make a subagent output valid and cannot override missing `validator_refs`, missing validator evidence, missing collected artifacts, missing material I/O, missing narrative/template refs, or missing ledger ingestion. `paper-owner-gate` remains a `user_gate` through `omx_question`; it must never be compiled as a native subagent task.

## Stable governance markers

- `paper-owner-gate remains a user_gate`: route paper-owner semantic authority through `omx_question` and decision-ledger evidence; never compile it as a native subagent task.
- `Team only after RALPLAN`: launch Team only after RALPLAN consensus and explicit current-story user approval.
- `department/material I/O is required`: every compiled task must declare department, material inputs, material outputs, and backflow/state-ingestion closure.
