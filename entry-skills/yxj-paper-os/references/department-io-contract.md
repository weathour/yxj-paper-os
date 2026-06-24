# Department I/O contract — yxj-paper-os v2

This contract defines the v2 institutional control plane for the single public
`yxj-paper-os` Paper Orchestrator. It is a source-level governance contract: it
does not install, publish, upload, or mutate external services.

## Core principle

A paper-management task is not complete because an agent was dispatched, a PUA
pressure level was recorded, or a manager wrote a persuasive summary. A task can
close only when its department owner, material inputs, material outputs,
validators, collection path, state ingestion, backflow route, and state
transition are explicit and checked.

The preserved completion invariant is:

`compile -> execute -> collect -> validate -> ingest -> state_transition`

## PMO + department model

| Department | Owns | Consumes | Produces | Typical lanes |
| --- | --- | --- | --- | --- |
| PMO / Paper Management | route, task ledger, decision queue, hard gates, final manager handoff | all department status and validator evidence | `TaskPacketV2`, `ManagerHandoffReportV2`, state transitions | `state-steward`, `execution-coordinator`, `final-verifier` |
| Paper Architecture & Narrative | reader-facing argument architecture | target venue, claims, evidence, template profile | `ReaderSpineBrief`, `ObjectRepresentationMatrix`, `SectionFunctionBudget`, `ReaderTransitionMap` | `paper-architect`, `exemplar-learner`, `style-auditor` |
| Evidence & Method | truth boundary and method/experiment admissibility | source map, experiments, claims, narrative needs | Evidence pack, method contract, experiment contract, baseline/ablation rationale | `evidence-curator`, `method-verifier`, `citation-banker` |
| Manuscript & Figure Production | section/figure/table/algorithm/formula representation | narrative objects, evidence contracts, template budgets | manuscript section outputs, visual/formal package, export package inputs | `manuscript-owner`, `figure-owner`, `export-owner` |
| Review & Governance | independent closure, hostile review, backflow | all produced objects and handoff evidence | `ReaderExperienceReviewReport`, `NarrativeBackflowTask`, validator report | `review-director`, `verifier`, `final-verifier` |

## Mandatory task packet bindings

Every v2 task packet must identify:

- `owner_department` and `owner_lane`;
- `agent_type` or non-subagent route;
- `input_materials` with artifact ids/paths;
- `expected_output_materials` with artifact ids/paths;
- `validator_refs` using the canonical field name;
- `narrative_object_refs` when writing, review, figure, evidence, method, or
  export work depends on reader-facing argument structure;
- `template_object_refs` when target venue/exemplar form affects the output;
- `backflow_route` for failed review or lab-notebook-smell findings;
- `collection_path`, `state_ingestion`, `pipeline_stage`, and `state_transition`;
- `pua_telemetry` as control evidence only.

A task that produces paper-facing text, figures, method claims, experiment
claims, review findings, or export readiness must not close without the relevant
narrative/template object refs unless the task explicitly records why the refs
are not applicable and a validator accepts that exception.

## Manager-direct authority exception

The Paper Orchestrator may coordinate, inspect, compile, route, and report as manager.
When the same active manager directly writes, edits, reviews, verifies, exports, or
transitions department-owned work, that action is a `ManagerDirectIntervention`
exception. It must be declared or inferred from actor provenance; a task packet
self-report of `manager_direct_intervention.present:false` is not authoritative.

Every completion-sensitive task must carry actor provenance for executor, reviewer,
verifier, and final certifier. The effective actor key is derived from
`actor_kind`, `actor_id`, `actor_lane`, and `run_or_session_id`. The same manager
session switching lanes is still the same effective actor and cannot count as
independent review. Missing or unparseable provenance cannot satisfy independence.

`paper_facing` and `state_sensitive` are derived classifications. They are inferred
from owner department/lane, material/output paths, validator refs, handoff claims,
and state-transition fields. Self-report cannot downgrade sensitivity.

Paper-facing, export-facing, claim/evidence, or state-sensitive manager-direct work
may be `candidate` or `validated` without independent review, but it cannot become
`complete` until trusted provenance, independent review, and final-certifier
separation are present.

## Material object lifecycle

1. **Planned** — required inputs/outputs and owner lane are declared.
2. **Collected** — the output exists at the declared path.
3. **Validated** — all declared validators have passing evidence.
4. **Ingested** — state/artifact/review/evidence ledgers reference the output.
5. **Transitioned** — the task records a valid `state_transition` to `complete`.

`recommended`, `dispatched`, `validated`, and `ingested` are not synonyms for
`complete`.

## Manager handoff v2 fields

Broad manager reports and completion handoffs must expose:

- department / workstream;
- internal owner module and agent lane;
- material inputs consumed;
- material outputs produced;
- validator and fixture evidence;
- closure state: planned, collected, validated, ingested, transitioned, blocked;
- risks and unresolved gaps;
- owner decisions vs auto-continuable next steps;
- hard-gated actions that cannot proceed without explicit authorization;
- impact on final paper, reviewer risk, evidence strength, or export readiness.

## Hard boundaries

The department I/O contract does not authorize live install, publish,
marketplace update, external submission/upload, credentialed service calls,
destructive actions, private/raw copying, cross-paper-root mixing, or paper-owner
semantic decisions. Those remain explicit gates.
