# Runtime execution contract

The runtime adapter is named `native_subagent_pipeline_adapter`.

## Direct execution sequence

1. **compile**: create a v2 task packet from profile, source-map, reader narrative objects, template budgets, evidence/rationale rows, and owner lane. The packet mirrors `agent-lane-registry.yaml` with `owner_department`, `input_materials`, `expected_output_materials`, required narrative/template refs, `backflow_route`, and validator refs.
2. **execute**: launch a Codex native subagent with the declared `agent_type`; Team requires explicit gate.
3. **collect**: copy returned artifacts/material objects to `collection_path` and list them in the task ledger.
4. **validate**: run all `validator_refs`, including v2 department/material/narrative/template validators when declared by the lane; write `validator-report.yaml`.
5. **ingest**: update state/artifact/evidence/review/export ledgers so produced materials are visible to downstream departments.
6. **state_transition**: move the task and project phase only after ingestion evidence.

The preserved completion invariant is `compile -> execute -> collect -> validate -> ingest -> state_transition`.

## Required task packet fields

- `task_id`
- `route`
- `adapter: native_subagent_pipeline_adapter`
- `owner_department`
- `owner_lane`
- `agent_type`
- `input_materials`
- `expected_output_materials`
- `narrative_object_refs` when required by the owner lane
- `template_object_refs` when required by the owner lane
- `backflow_route`
- `scoped_context`
- `expected_output_artifacts`
- `collection_path`
- `state_ledger_path`
- `state_ingestion`
- `validator_refs`
- `pipeline_stage`
- `state_transition`
- `pua_telemetry`

## V2 validation checkpoints

- `validate_agent_lane_department_binding`: `owner_department` must match the canonical registry row for `owner_lane`; `agent_type` must match the lane route or the allowed non-subagent route.
- `validate_task_material_io`: input and expected output materials must be non-empty, typed, and path/id-addressable for subagent/scaffold lanes; produced outputs must be represented in collected outputs and/or ledgers before completion. Raw file existence alone is not material closure.
- `validate_narrative_object_binding`: lanes that shape reader-facing text, method claims, evidence claims, figures, review, or export must carry relevant narrative object refs, unless `validator-report.yaml` records an independently accepted binding exception.
- `validate_template_object_binding`: lanes affected by exemplar/venue form must carry relevant template object refs, unless `validator-report.yaml` records an independently accepted binding exception.
- `validate_fixture_matrix_nonempty`: fixture-suite verification must show at least one valid fixture and at least one invalid fixture, preventing an empty-matrix false positive.
- `validate_manager_handoff_v2`: broad handoffs must expose department, material I/O, owner lane/agent, closure state, evidence, risks, owner decisions, and final-paper impact.
- `validate_repository_hygiene_report`: export/final/pre-author-review handoffs must prove dirty worktree scope, sibling/parent contamination, snapshot freshness, export-manifest hashes, cleanup actions, and external-submission boundary through `RepositoryHygieneReport`.

## Failure policy

- Dispatch without collected output remains `dispatched` or `failed`, never `complete`.
- Collected output without validator evidence remains `collected` or `failed`.
- Validated output without ingestion remains `validated` or `failed`.
- Missing `owner_department`, material I/O, required narrative/template refs, backflow route, repository hygiene report for export/final handoff lanes, or state-ingestion plan blocks completion.
- Unknown `agent_type`, owner lane, source locator, material object, narrative/template object ref, or validator ref blocks completion.

## PUA/RALPLAN execution telemetry

Every task packet must carry `pua_telemetry`. The default pressure level is L0; L1-L4 record escalation when an LLM agent repeats a failed approach, guesses without reading state/source material, waits passively, or claims completion without evidence.

Required `pua_telemetry` fields:

- `pressure_level`: `L0`, `L1`, `L2`, `L3`, or `L4`.
- `failure_count` and `failure_mode`.
- `pua_diagnosis.problem_or_goal`, `pua_diagnosis.evidence`, and `pua_diagnosis.next_action`.
- `owner_four_questions.root_cause_or_target`, `impact_surface`, `prevention_or_check`, and `data_or_evidence`.
- `attempts`, `excluded`, `next_hypothesis`, and `manager_action`.
- `seven_item_checklist` booleans for the L3 checks.

At L2+ the collected output must include `[PUA-REPORT]` or equivalent structured telemetry. `validate_pua_telemetry` checks this control plane. It never replaces `validate_task_packet`, `validate_subagent_output`, material I/O validators, narrative/template validators, validator evidence, ledger ingestion, or `compile -> execute -> collect -> validate -> ingest -> state_transition`.

### PUA report semantic checks

At L2+ `pua_report.present:true` is mandatory and must exactly mirror failure count, failure mode, attempts, excluded causes, next hypothesis, and manager action from top-level `pua_telemetry`. At L3+ all seven checklist booleans must be true. L4 requires `failure_count >= 5`. These semantics are enforced by `validate_pua_telemetry` and covered by invalid fixtures.
