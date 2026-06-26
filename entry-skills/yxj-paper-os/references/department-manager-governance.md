# Department Manager governance — yxj-paper-os v2+

This contract adds an internal middle-management layer under the single public
`yxj-paper-os` Paper Orchestrator. It does not add public commands, new native
agent types, or a second top-level manager. It exists to compress the current
management span: five departments, internal modules, lane registry entries,
material objects, validators, and ledgers.

## Governance principle

The paper owner hands work to one Paper Orchestrator. The Paper Orchestrator
manages through internal Department Managers. Department Managers turn broad
paper work into department-level route cards; they do not replace TaskPacketV2,
`native_subagent_pipeline_adapter`, validators, ledgers, PMO state transitions,
or independent review.

A `DepartmentRouteCard` is therefore a coordination and recommendation material
object, not completion evidence. A task can still close only by the preserved
pipeline:

`compile -> execute -> collect -> validate -> ingest -> state_transition`

## Department Manager roster

| Department Manager | Owns | Primary material objects | Typical downstream lanes |
| --- | --- | --- | --- |
| PMO Department Manager | global state, task routing, decision queue, repository hygiene, final handoff | `TaskPacketV2`, `DepartmentRouteCard`, `ManagerHandoffReportV2`, `RepositoryHygieneReport`, ledgers | `state-steward`, `execution-coordinator`, `repository-hygiene-owner`, `paper-owner-gate`, `final-verifier` |
| Paper Architecture & Narrative Manager | reader-facing argument, paper spine, section function, template/exemplar fit, novelty route | `ReaderSpineBrief`, `ObjectRepresentationMatrix`, `TemplateQuantProfile`, `SectionFunctionBudget`, `DepartmentRouteCard` | `scene-analyst`, `exemplar-learner`, `novelty-panel`, `paper-architect`, `research-director` |
| Evidence & Method Manager | source/citation/evidence support, claim boundaries, method and experiment admissibility | `source-map`, `citation-bank`, `evidence-bank`, `claim-support-matrix`, `method-contract`, `DepartmentRouteCard` | `source-map-curator`, `sota-mapper`, `citation-banker`, `evidence-curator`, `method-verifier`, `yxj-wiki-bridge` |
| Manuscript & Figure Production Manager | manuscript sections, figures/tables/algorithms/formulas, captions, export inputs | section drafts, `VisualTableAlgorithmFormulaBudget`, figure plan, caption brief, export package inputs, `DepartmentRouteCard` | `manuscript-owner`, `figure-owner`, `export-owner` |
| Review & Governance Manager | hostile review, style audit, reader-surface gates, authority separation, backflow | `ReaderExperienceReviewReport`, `NarrativeBackflowTask`, style findings, final closure report, `DepartmentRouteCard` | `review-director`, `style-auditor`, `verifier`, `final-verifier`, `validator-designer` |

## Existence forms

Department Managers have three permitted forms:

1. **Internal contract / prompt mode** — default. The Paper Orchestrator loads
   this governance contract plus the relevant department/module contract and
   reasons in a department-manager voice without launching another agent.
2. **Temporary native subagent mode** — for complex department slices. The
   subagent must use an installed OMX role such as `planner`, `architect`,
   `verifier`, `critic`, `writer`, `researcher`, or `executor` from the lane
   registry. It returns a `DepartmentRouteCard`; it does not spawn uncontrolled
   descendants or certify completion.
3. **Team lane-lead mode** — for large approved stories only. Team may be used
   after RALPLAN consensus and explicit current-story paper-owner approval. Team
   leads coordinate department work and return artifacts/evidence upward; the
   Paper Orchestrator and PMO still own state checkpoints and closure.

## Authority and routing boundary

Department Managers may:

- classify department state, gaps, risks, and owner gates;
- identify upstream materials that must be consumed before execution;
- propose lane requests and expected material outputs;
- recommend validator refs, backflow routes, and PMO handoff actions;
- recommend Team staffing for large work after the Team gate is satisfied.

Department Managers must not:

- expose themselves as public `$` commands;
- add or require new native `agent_type`s;
- recursively spawn uncontrolled subagents;
- launch Team without RALPLAN plus explicit current-story approval;
- copy private/raw material without explicit authority;
- make paper-owner semantic decisions;
- certify final completion or override validator/ledger evidence;
- weaken manager-direct intervention, actor provenance, independent review, or
  final-certifier separation requirements.

## Dispatch pattern

The normal pattern is:

`Paper Orchestrator -> Department Manager contract/subagent -> DepartmentRouteCard -> PMO/execution-coordinator -> TaskPacketV2 -> native subagent/Team worker -> collect -> validate -> ingest -> state_transition`

The route card is an input to task-packet compilation. It can justify which lane
should run, what materials must be consumed, and which validators must pass, but
it cannot satisfy those validators by itself.

## DepartmentRouteCard minimum content

A route card must state:

- `department_id` and `department_manager`;
- `mode` (`contract_only`, `department_manager_subagent`, or `team_lane_lead`);
- current gate, scoped request, and consumed input materials;
- missing inputs and unresolved owner gates;
- proposed lanes and requested `TaskPacketV2` ids;
- expected material outputs and collection paths;
- validator refs, backflow route, ledger/state-ingestion target;
- Team gate status when Team is recommended or active;
- recursion-control statement;
- authority boundaries and non-completion status;
- PMO handoff summary and next safe action.

## Handoff requirement

Broad Paper Orchestrator reports should summarize the five Department Managers
instead of exposing raw module/lane lists. Each department row should point to
its latest `DepartmentRouteCard` when one exists, then separately report actual
collected outputs, validator evidence, ledger ingestion, and state transition.
