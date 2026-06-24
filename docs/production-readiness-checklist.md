# Production-readiness checklist

This scaffold is not production-live until all gates pass.

- [ ] Plugin is installed only after explicit live-install confirmation.
- [ ] Old yxj-paper-os migration/uninstall has explicit destructive-action confirmation.
- [ ] Manifest and skills validate.
- [ ] `validate_scaffold.py` passes.
- [ ] `run_fixture_suite.py` passes and catches every invalid fixture.
- [ ] Direct execution smoke proves compile -> execute -> collect -> validate -> ingest -> state_transition.
- [ ] Team smoke, if needed, is explicitly approved and checkpoints evidence back to Ultragoal/state.
- [ ] Privacy scan shows no private/raw leakage.
- [ ] Export manifest references validation evidence and residual risks.

- [ ] Agent lane registry covers every paper/scaffold owner lane and every direct lane has an installed `agent_type`, context scope, expected outputs, validator refs, and fallback policy.
- [ ] Validator evidence closure requires every `validator_ref` to pass before completion.
- [ ] Artifact-ledger validator refs for validated/complete/ready artifacts have passing validator evidence.

- [ ] `ledger_guard.py check` passes on at least one initialized paper workspace.
- [ ] Any repository that ignores `.omx/` has a tracked ledger snapshot refreshed by `ledger_guard.py snapshot`.
- [ ] Final-answer workflow blocks on `ledger_guard.py check` failure rather than relying on prose discipline.
- [ ] Paper-owner handoffs use Gate-based Manager Report + Department Table +
      Decision Queue + Verification Appendix, with precise validated/ingested/
      recommended/blocked/owner-gated/external-gated status vocabulary.

## PUA/RALPLAN governance readiness

- [ ] `pua_telemetry` exists in task packet templates and fixture task ledgers.
- [ ] `validate_pua_telemetry` is known to the fixture validator and appears in validator reports.
- [ ] `[PUA-DIAGNOSIS]`, `[PUA-REPORT]`, owner-four-questions, L1-L4 escalation, and L3 seven-item checklist are documented in contracts and operation guide.
- [ ] Documentation states that PUA telemetry never replaces validator evidence.
- [ ] RALPLAN remains the gate for architecture/test-shape uncertainty.
- [ ] Team remains gated by RALPLAN plus explicit current-story approval.
- [ ] `paper-owner-gate` remains `user_gate` and is never compiled as a native subagent.
- [ ] L2+ `pua_report` exactly mirrors top-level telemetry fields.
- [ ] `complete` task fixtures require `pipeline_stage: state_transition` and `state_transition.to: complete`.


### Explicit state transition fixture rule

Fixture-level validation mirrors `ledger_guard.py`: a task marked `complete` must include collected outputs, validator evidence, state ingestion, `pipeline_stage: state_transition`, and an explicit `state_transition` object with `from`, `to: complete`, and `at`. `pipeline_stage: state_transition` alone is not enough.


## V2 governance readiness

- [ ] `agent-lane-registry.yaml` uses schema `yxj-paper-os/agent-lane-registry/v2`.
- [ ] Every lane declares `department`, `material_inputs`, `material_outputs`,
      `narrative_binding_required`, `template_binding_required`, and v2
      validator coverage.
- [ ] `task-packet.yaml` exposes `owner_department`, `input_materials`,
      `expected_output_materials`, `narrative_object_refs`,
      `template_object_refs`, and `backflow_route`.
- [ ] Public-entry templates and canonical templates are byte-identical.
- [ ] Fixture suite has at least one valid v1 compatibility fixture, one valid
      v2 governance fixture, and invalid v2 blockers for department/material/
      narrative/template/reference/pseudo-completion failures.
- [ ] Broad handoffs use `Manager Handoff Report v2` with department, material
      I/O, owner lane/agent, closure state, evidence, owner decisions, hard
      gates, and final-paper impact.
- [ ] Reader narrative governance objects are consumed before manuscript,
      method, evidence, review, figure, table, algorithm, formula, or export
      tasks claim completion.

- [ ] Scaffold validation passes semantic object shape validators for ReaderSpine, object representation, template profile, section budget, visual/formal budget, reader-experience review, and narrative backflow templates.
- [ ] Binding exceptions are independently accepted in `validator-report.yaml`; task-local exception fields cannot self-attest non-applicability.
- [ ] Material-output closure requires declaration in `collected_outputs` or `artifact-ledger`; raw file existence alone is not completion evidence.

## Repository hygiene / delivery cleanliness

- [ ] `RepositoryHygieneReport` exists for the active handoff.
- [ ] `validate_repository_hygiene_report` passed.
- [ ] Dirty entries are split into current-paper, sibling/parent, generated/ephemeral, and disallowed groups.
- [ ] Sibling/parent contamination is none or covered by an explicit owner decision.
- [ ] Ledger snapshot freshness is pass or not required.
- [ ] Export-manifest hashes are pass or not required.
- [ ] External submission/upload remains explicitly gated unless the paper owner confirmed it.
