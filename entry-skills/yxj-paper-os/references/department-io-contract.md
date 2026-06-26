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

## Company-style control plane

`yxj-paper-os` is managed as a small paper-production organization rather than a
linear prompt workflow. The public surface remains one PMO / Paper Orchestrator;
departments own accountability; agent lanes perform bounded work; internal
skills provide reusable SOP capability; material objects are the handoff unit;
validators provide evidence; ledgers and state transitions close the loop.

The control plane is:

```text
Paper Owner semantic authority
  -> PMO / Paper Orchestrator route and gate
  -> Department Manager route card
  -> Department accountability
  -> Agent lane execution
  -> Internal skill SOP
  -> Material object candidate
  -> Validator evidence
  -> Ledger ingestion
  -> State transition / backflow / owner-gate
```

Internal skills must never become a second manager. They may produce, consume,
repair, or review material candidates only inside declared permissions. They do
not make paper-owner semantic decisions, certify their own outputs, mutate final
state, or override PMO gates.

## PMO + department model

| Department | Owns | Consumes | Produces | Typical lanes |
| --- | --- | --- | --- | --- |
| PMO / Paper Management | route, task ledger, decision queue, hard gates, final manager handoff | all department status and validator evidence | `TaskPacketV2`, `DepartmentRouteCard`, `ManagerHandoffReportV2`, state transitions | `state-steward`, `execution-coordinator`, `final-verifier` |
| Paper Architecture & Narrative | reader-facing argument architecture and expression design | target venue, claims, evidence, template profile, reader questions | `ReaderSpineBrief`, `ObjectRepresentationMatrix`, `SectionFunctionBudget`, `ReaderTransitionMap`, `CognitiveLoadBudget`, `ExplanationLadder`, `RhetoricalMoveMatrix`, `ClaimEvidenceVisibilityMap`, `TerminologyRegister` | `paper-architect`, `exemplar-learner`, `style-auditor` |
| Evidence & Method | truth boundary and method/experiment admissibility | source map, experiments, claims, narrative needs | Evidence pack, method contract, experiment contract, baseline/ablation rationale | `evidence-curator`, `method-verifier`, `citation-banker` |
| Manuscript & Figure Production | section/figure/table/algorithm/formula representation | narrative objects, evidence contracts, template budgets, expression-design objects, Nature-grade figure contracts | manuscript section outputs, visual/formal package, Nature-grade figure package, export package inputs | `manuscript-owner`, `figure-owner`, `export-owner` |
| Review & Governance | independent closure, hostile review, backflow, rendered reader-surface validation | all produced objects, expression-design evidence, and handoff evidence | `ReaderExperienceReviewReport`, `NarrativeBackflowTask`, validator report, `RenderedSurfaceGateReport` | `review-director`, `verifier`, `final-verifier` |


## Department Manager layer

A Department Manager is an internal middle-management role, not a public skill,
not a new native `agent_type`, and not a second top-level manager. Its allowed
outputs are department state classification, lane requests, owner-gate risks,
validator recommendations, and a `DepartmentRouteCard`. The route card can feed
TaskPacketV2 compilation but is not completion evidence. It cannot replace
material output collection, validator evidence, ledger ingestion, manager-direct
intervention records, independent review, or final-certifier separation.

Permitted existence forms are: `contract_only`, `department_manager_subagent`
using an installed OMX role, and `team_lane_lead` after RALPLAN plus explicit
current-story approval. Recursive uncontrolled subagent spawning is prohibited.

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
- `expression_design_object_refs` when manuscript, figure/table/algorithm/formula,
  review, or export work is paper-facing and must consume
  `CognitiveLoadBudget`, `ExplanationLadder`, `RhetoricalMoveMatrix`,
  `ClaimEvidenceVisibilityMap`, and `TerminologyRegister`;
- `backflow_route` for failed review or lab-notebook-smell findings;
- `collection_path`, `state_ingestion`, `pipeline_stage`, and `state_transition`;
- `pua_telemetry` as control evidence only.

A task that produces paper-facing text, figures, method claims, experiment
claims, review findings, or export readiness must not close without the relevant
narrative/template object refs unless the task explicitly records why the refs
are not applicable and a validator accepts that exception.

A manuscript, figure/table/algorithm/formula, review, or export task must also
bind `expression_design_object_refs` unless the task carries a validator-accepted
non-applicable exception. This rule is additive: expression-design refs never
replace narrative, template, or evidence refs.

## TaskPacketV2Plus additive governance

`TaskPacketV2Plus` is an additive superset of the existing v2 task packet. It
must not remove, rename, or weaken current required v2 fields:

- `owner_department`
- `owner_lane`
- `agent_type`
- `input_materials`
- `expected_output_materials`
- `validator_refs`
- `collection_path`
- `state_ingestion`
- `pipeline_stage`
- `state_transition`
- `backflow_route`
- `pua_telemetry`

The v2plus layer may add fields that improve management clarity:

- `skill_refs` — internal SOP skills the lane may use;
- `mode_permissions` — whether the lane may produce, consume, review, repair, or
  route material objects;
- `mission` — the bounded task outcome in reader/reviewer terms;
- `expected_output_materials` — the material object contract, not just a file;
- `narrative_object_refs`, `template_object_refs`, and `evidence_object_refs` —
  required when the task touches writing, review, figures, claims, methods,
  experiments, or export surface;
- `expression_design_object_refs` — required for paper-facing manuscript,
  figure/table/algorithm/formula, review, or export surfaces unless
  `validate_expression_design_object_binding` accepts non-applicability;
- `expression_design_requirement` — declares paper-facing判定 surfaces,
  non-applicable exception policy, rendered-output requirements, and validator
  refs needed when expression design applies;
- `single_writer_lock` — required when a section/file/shared hotspot has one
  current writer;
- `authority_role_separation` — executor, reviewer, verifier, state steward, and
  final certifier boundaries;
- `completion_claim_allowed` — false until collection, validation, ingestion,
  and state transition evidence exist.

V2plus does not authorize worker-local completion. It only makes the task packet
clear enough for agents to exercise intelligence inside institutional bounds.

## Single-writer section and hotspot locks

Shared manuscript sections, registry files, validator scripts, fixture
directories, and export/readiness artifacts must have a single effective writer
at a time. A `SingleWriterSectionLock` records:

- `lock_id`;
- `section_or_file`;
- `owner_lane`;
- `agent_actor`;
- `allowed_collaborators`;
- `expires_or_release_condition`;
- `conflict_policy`;
- `validator_refs`.

Reviewer and collaborator lanes may comment or provide patch snippets, but the
lock owner integrates changes. A task that edits a locked path without a matching
lock cannot claim `complete`.

## Authority role separation

Completion-sensitive work must keep these roles separable:

| Role | Responsibility | Cannot replace |
| --- | --- | --- |
| Executor | produces the candidate material | independent reviewer |
| Reviewer | checks reader/surface/evidence risks | final certifier |
| Verifier | proves validators and fixtures pass | paper-owner semantic authority |
| State steward | ingests evidence and records transitions | executor |
| Final certifier | signs off completion after evidence | same effective actor as executor for sensitive work |

The same manager session switching lanes is still the same effective actor. For
paper-facing, export-facing, claim/evidence, or state-sensitive outputs,
manager-direct work may remain candidate/validated but cannot become complete
without trusted provenance, independent review, and final-certifier separation.

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

## Nature-grade figure material chain

Final/export-facing paper figures are governed by an additive Nature-grade
material chain. It absorbs the workflow discipline of `nature-figure` while
keeping yxj-paper-os ownership, validators, and ledger closure:

```text
Paper Architecture & Narrative
  -> NatureFigureContract
  -> NatureFigureAestheticProfile
Evidence & Method
  -> NaturePanelEvidenceMap
  -> FigureSourceDataStatistics
  -> FigureImageIntegrityRecord
Manuscript & Figure Production
  -> FigureBackendRoute
  -> NatureCaptionLegendBrief
  -> FigureExportBundle
Review & Governance
  -> RenderedSurfaceGateReport
  -> NatureFigureQAReport
PMO / State
  -> validator evidence
  -> ledger ingestion
  -> state transition / backflow
```

These objects are department-owned:

| Material object | Primary owner | Closure purpose |
| --- | --- | --- |
| `NatureFigureContract` | Paper Architecture & Narrative / `paper-architect` or `figure-owner` | Fixes the figure's one core conclusion, reader question, archetype, hero/support panel hierarchy, panel map, claim/evidence refs, and required narrative/template/expression refs before drawing. |
| `NatureFigureAestheticProfile` | Paper Architecture & Narrative with figure/style consumers | Converts aesthetic quality into objective gates: composition archetype, hero-panel exception policy, semantic palette roles, editable typography, panel-label policy, legend strategy, white/background/export constraints. |
| `NaturePanelEvidenceMap` | Evidence & Method | Prevents ornamental panels by requiring each panel to carry a unique reader question, evidence role, supported claim ids, and evidence/statistics/image-integrity refs. |
| `FigureBackendRoute` | Manuscript & Figure Production | Selects exactly one final source of truth and blocks backend mixing; source markdown or generated previews never replace editable figure source. |
| `FigureSourceDataStatistics` | Evidence & Method | Carries source-data/statistics details for measured panels or a validator-accepted conceptual no-data rationale. |
| `FigureImageIntegrityRecord` | Evidence & Method / Figure Production | Carries image/raster processing provenance or a validator-accepted not-applicable record for pure deterministic vector/conceptual figures. |
| `NatureCaptionLegendBrief` | Manuscript & Figure Production | Binds title, present-tense panel explanations, statistics/source-data statements, claim-closing sentence, privacy surface, and attribution/permission note. |
| `NatureFigureQAReport` | Review & Governance | Independently checks visual, aesthetic, evidence, caption, image-integrity, export, and rendered-surface gates and routes failures back to owning lanes. |
| `FigureExportBundle` | Export owner / Figure owner | Records editable source, SVG/PDF plus preview/raster output, target dimensions, legibility, manifest refs, and hash provenance. |

The aesthetic gate is not subjective self-certification. It is enforced through
typed material fields and validators: a figure must name its archetype, establish
hero/support hierarchy, use semantic color roles, keep editable text and
legible typography, avoid decorative badges, choose a controlled legend/direct
label strategy, inspect rendered output, and pass independent QA. Review failures
produce backflow tasks rather than completion claims.

For conceptual/vector figures, `FigureSourceDataStatistics.conceptual:true` and
`FigureImageIntegrityRecord.image_integrity_applicability.status:not_applicable`
are valid only with an explicit rationale and a deterministic/manual-review route.
For data or image panels, source locators, statistics, processing steps, and
integrity evidence are mandatory.

## Manager handoff v2 fields

Broad manager reports and completion handoffs must expose:

- department / workstream;
- internal owner module and agent lane;
- material inputs consumed;
- material outputs produced;
- validator and fixture evidence;
- closure state: planned, collected, validated, ingested, transitioned, blocked;
- reader-load status: not_applicable, planned, collected, validated, or blocked;
- expression-design status: not_applicable, planned, collected, validated, or
  blocked;
- risks and unresolved gaps;
- owner decisions vs auto-continuable next steps;
- hard-gated actions that cannot proceed without explicit authorization;
- impact on final paper, reviewer risk, evidence strength, or export readiness.

## Hard boundaries

The department I/O contract does not authorize live install, publish,
marketplace update, external submission/upload, credentialed service calls,
destructive actions, private/raw copying, cross-paper-root mixing, or paper-owner
semantic decisions. Those remain explicit gates.

## Expression-design hard boundaries

- `ExpressionDesignBundle` is only an index. It cannot replace the five typed
  object refs or satisfy their validators by itself.
- `ClaimEvidenceVisibilityMap` cannot increase claim strength; Evidence & Method
  artifacts remain authoritative.
- Export readiness cannot close on source markdown alone. Rendered output must
  be inspected through the rendered-surface gate.
- This plugin-source upgrade does not re-review any current manuscript unless a
  separate paper-level task instantiates, validates, ingests, and transitions
  the new expression-design objects.


## Nature full-absorption material chain

Non-figure Nature skills are absorbed as yxj-native internal capability cells. The canonical departments do not change; display labels may expand, but state/validator department IDs remain stable. In particular, presentation/PPT is a writing/expression production capability under `manuscript_and_figure_production`, not an export-only department.

The M1 chain is:

```text
NatureSourceInventory
  -> CompanySkillRegistry
  -> PaperReaderPackage / SearchStrategyDossier / CitationVerificationReport
  -> SectionMovePlan / JournalStyleProfile / PolishingRepairReport
  -> DataAvailabilityPlan
  -> ReviewerPanelReport / ResponseActionMap
  -> PresentationPlan / PatentDraftBoundary
  -> NatureAbsorptionPackage
  -> validator evidence
  -> ledger ingestion / state transition / backflow
```

Boundary rules:
- `CompanySkillRegistry` rows must set `public_surface_allowed:false` and `hidden_manager:false`.
- `NatureAbsorptionPackage` must link every required capability material and a backflow route before closure.
- `DataAvailabilityPlan` may not invent repository identifiers, licences, accessions, access committees, or embargoes.
- `ResponseActionMap` must preserve reviewer/editor comment IDs and must not invent line numbers or manuscript changes.
- `PresentationPlan` must consume narrative/expression refs and cannot be owned only by `export-owner`.
- `PatentDraftBoundary` is a drafting-aid boundary, not legal advice, not a patentability opinion, and not filing authorization.
