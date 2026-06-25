# yxj-paper-os architecture

This directory is the installed local source for the `yxj-paper-os` Codex
plugin. It is installed from the personal-local marketplace and remains a local
development plugin: it is not published, it does not mutate source-truth
repositories, and it does not remove the archived old implementation.

## Layers

1. Plugin manifest and single public entry routing.
2. Paper Orchestrator activation contract.
3. Workspace/state contracts.
4. Native subagent pipeline adapter.
5. Paper modules: research, novelty, evidence, PaperSpine, review, figures, export.
6. Validators and fixtures.

## Paper Orchestrator layer

`entry-skills/yxj-paper-os` is the only public `$` completion entry. It is the
canonical top-level yxj Paper Orchestrator / 论文经理 / 论文统筹 handoff point.
The `skills/yxj-paper-*` directories remain internal department modules for
contracts, templates, scripts, and validators; they should not be offered to the
paper owner as separate commands. A separate `yxj-paper-orchestrator` skill is
not required: duplicating the top-level surface would create routing ambiguity
before there is smoke-test evidence that a separate alias is needed.

When invoked for a paper workspace, the orchestrator should:

1. detect the paper root;
2. read yxj-paper-os state and ledgers before status reporting when feasible;
3. report by workstream/department rather than by module list only;
4. for each reported department, include the current concrete situation,
   current problems/risks, exact paper-owner review/decision items, and impact
   on the final paper;
5. separate author-facing review items into a final "Needs paper-owner
   attention" block for broad status reports;
6. choose the next safe route: interview, RALPLAN, direct execution, evidence,
   PaperSpine, review, figures, export, migration, or Team recommendation.

The detailed public activation behavior is defined in
`entry-skills/yxj-paper-os/references/orchestrator-contract.md`; the internal
source module remains at `skills/yxj-paper-index/references/orchestrator-contract.md`.

## Task-autonomy and hard gates

The orchestrator may use task-autonomy for scoped paper progress: read state,
run read-only checks, draft task packets, run RALPLAN, dispatch direct native
subagents, update task notes/ledgers, validate, snapshot, and report evidence.

It must still ask before Team launch, external submission/upload, credentialed
services, destructive actions, active install/uninstall/publish operations,
private/raw source copying, cross-paper-root mixing, or paper-owner semantic
decisions such as final motivation, venue commitment, claim scope beyond
evidence, or contribution spine.

## Critical invariant

`dispatched != complete`.

Completion requires collected output, validator evidence, and state ingestion.
The state machine is defined in
`skills/yxj-paper-state/references/state-contract.md`.

## PaperSpine/Sisyphus absorption

PaperSpine contributes source-map-first writing, research triplet, citation
support bank, confirmed motivation, rationale matrix, branch backflow, and
export discipline. Sisyphus contributes novelty engines, hostile reviewers,
verifier/style-auditor/writer separation, and adversarial review routing. Both
are adapted into project-relative yxj-paper-os workspaces and validators; their
implementations are not vendored into this plugin.

## Registry-backed closure

`skills/yxj-paper-execute/references/agent-lane-registry.yaml` is the canonical
owner-lane/agent-type registry. Validators derive owner-lane closure from it and
require every `validator_ref` to have passing evidence before completion.

Validator evidence closure covers task-ledger `validator_refs` and artifact-ledger validator refs for artifacts marked validated/complete/ready.


## V2 governance management planes

The v2 upgrade treats yxj-paper-os as a managed paper organization rather than a
linear workflow. The four control planes are:

1. **Responsible departments**: PMO / Paper Management, Paper Architecture &
   Narrative, Evidence & Method, Manuscript & Figure Production, and Review &
   Governance. Each task has exactly one `owner_department` and one
   `owner_lane`.
2. **Material-object management**: tasks consume and produce named material
   objects such as `ReaderSpineBrief`, `ObjectRepresentationMatrix`,
   `TemplateQuantProfile`, evidence banks, method contracts, manuscript section
   outputs, figure packages, review reports, and export packages.
3. **Agent/personnel lanes**: `agent-lane-registry.yaml` maps each lane to an
   installed `agent_type`, department, material inputs, material outputs, and
   required reader/template binding.
4. **Closure loops**: completion still requires
   `compile -> execute -> collect -> validate -> ingest -> state_transition`,
   now with department/material/narrative/template validators in the loop.

Reader-facing writing is therefore not governed by prose advice alone. A task
that shapes method, problem, contribution, scenario, experiment, baseline,
ablation, figure, table, algorithm, formula, review, or export representation
must consume the relevant narrative/template objects or record a
validator-accepted non-applicable reason. This is what prevents final reports
from degrading into lab-notebook records.

## V2 validator plane

### Semantic object shape gate

Scaffold validation checks the structural shape of ReaderSpine, object representation, template profile, section function budget, visual/formal budget, reader-experience review, and narrative backflow templates. This gives the reader-narrative plane an executable schema-level gate while preserving the rule that paper-owner semantic claims must not be invented by the manager.


The validator plane includes the legacy closure checks plus v2 checks:

- `validate_agent_lane_department_binding` checks the registry department and
  `agent_type` for a task lane.
- `validate_task_material_io` checks typed, addressable material inputs and
  outputs and blocks pseudo-completion when declared material outputs are not
  collected/ingested.
- `validate_narrative_object_binding` and `validate_template_object_binding`
  check ReaderSpine/template-object references for lanes that affect reader
  understanding or venue/exemplar form.
- `validate_template_mirror_sync` ensures public-entry templates remain
  byte-identical to canonical templates.
- `validate_fixture_matrix_nonempty` prevents empty fixture-suite false
  positives.
- `validate_manager_handoff_v2` protects the broad manager handoff shape.

## PUA/RALPLAN governance control plane

The architecture uses a single-entry Paper Orchestrator with internal matrix
lanes. PUA is represented as structured operational telemetry, not motivational
copy. Each task packet can be statically checked for `pua_telemetry`,
`[PUA-DIAGNOSIS]`, owner-four-questions, L1-L4 escalation state, `[PUA-REPORT]`
requirements, and the L3 seven-item checklist.

This control plane sits beside, not above, the validator plane. It helps the
manager detect LLM-agent failure modes such as repeated same-path attempts,
no-search guessing, passive waiting, rough-grain plans, and empty completion
claims. It cannot declare paper work complete. Completion remains governed by
registry-derived owner lanes, validator refs, validator evidence, ledger
ingestion, and the exact pipeline `compile -> execute -> collect -> validate -> ingest -> state_transition`.

RALPLAN is the consensus gate for architecture/test-shape uncertainty. Team is a
parallel execution lane only after RALPLAN and explicit current-story approval.
`paper-owner-gate` is always a user gate and is never scheduled as a native
subagent.

## Repository hygiene / delivery cleanliness control plane

`yxj-paper-os` treats repository hygiene as PMO evidence, not cosmetic cleanup. The `repository-hygiene-owner` verifier lane produces `RepositoryHygieneReport` before final handoff/export readiness claims. This separates content readiness from delivery cleanliness and blocks false-ready reports when the git worktree has disallowed current-paper changes, sibling/parent contamination, stale snapshots, missing export-manifest hashes, or unconfirmed external-submission boundaries.

## Manager authority / anti-self-certification plane

The manager is the single public entry, not an all-purpose self-certifier. When
the active Paper Orchestrator directly writes, edits, reviews, verifies, exports,
or transitions department-owned work, the action becomes a visible
`ManagerDirectIntervention` exception. The exception is governed by three
mechanical facts: trusted `actor_provenance`, resolved effective actor identity,
and derived sensitivity classification.

The validator plane treats `manager_direct_intervention.present:false` as only a
claim. If actor provenance shows manager execution, the intervention is inferred
and must have a governance artifact. Paper-facing, export-facing, claim/evidence,
or state-sensitive manager-direct work cannot become `complete` until independent
review and final-certifier separation are both proven. The same manager/session
switching lanes is still the same effective actor.


## V2plus material-skill architecture

The v2plus layer keeps the existing v2 state machine and task-packet fields but
adds a stronger material-skill management plane:

- `TaskPacketV2Plus` is additive-only and preserves old v2 fields such as
  `collection_path`, `state_ingestion`, `pipeline_stage`, and `state_transition`.
- `CompanySkillRegistry` records internal SOP capabilities and prevents skills
  from becoming hidden managers.
- `SingleWriterSectionLock` protects manuscript sections and shared hotspots.
- Reader-facing writing is governed by `ReviewerQuestionMap` and
  `MainTextConstructionMatrix`, so method/problem/contribution/scene/result
  objects appear at the right granularity in each manuscript location.
- Evidence-facing writing is bounded by `ClaimCitationCapsule` and
  `ResultPackage`, so source support and result scope travel into prose.
- Review/export closure uses `ReaderSurfaceTutorReview` and
  `RenderedSurfaceGateReport` to catch internal codes, snake_case constraints,
  raw method ids, bare citekeys, and defensive claim-boundary walls in rendered
  output.

This architecture separates responsibility from automation: departments own
accountability, agents execute, skills provide SOPs, materials carry outputs,
validators prove contracts, ledgers preserve memory, and the PMO routes closure.
