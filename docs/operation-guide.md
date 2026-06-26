# Operation guide

## Safe use

Use the installed `yxj-paper-os` public entry from a permitted Codex/OMX runtime.
For local validation of this installed source, run:

```bash
python3 skills/yxj-paper-index/scripts/validate_scaffold.py .
python3 skills/yxj-paper-index/scripts/run_fixture_suite.py .
python3 skills/yxj-paper-index/scripts/ledger_guard.py check --root <paper-root>
```

## Orchestrator activation pattern

Use the single public `yxj-paper-os` entry as the canonical yxj Paper
Orchestrator / 论文经理 / 论文统筹 handoff point. The public plugin skill path
contains only `entry-skills/yxj-paper-os`; the `skills/yxj-paper-*` directories
are internal departments. Do not ask the paper owner to invoke those departments
directly. A separate `yxj-paper-orchestrator` skill is not required; add only a
thin alias later if smoke prompts show the single public entry does not activate
reliably.

When the user asks a broad question such as "看一下这篇论文整体推进情况" or
"推进这篇论文", the orchestrator should not ask the user to choose a low-level
module first. It should:

1. detect the paper root;
2. read `.omx/state/yxj-paper-os/state.yaml` and relevant ledgers;
3. use `notes/yxj-paper-os/ledger-snapshot/` when the tracked mirror is needed;
4. report by workstream/department and, for v2-managed tasks, by material object:
   - experiments and empirical evidence;
   - references and citation support;
   - template/exemplar research, `TemplateQuantProfile`, and writing inputs;
   - writing story / PaperSpine / section design, `ReaderSpineBrief`, and `ObjectRepresentationMatrix`;
   - method and experiment design ownership;
   - review findings and backflow fixes;
   - terminology and nomenclature consistency;
   - figures and export readiness;
5. for every reported department, include:
   - current concrete situation with artifact/ledger evidence and owner lane;
   - current problems, risks, blockers, weak evidence, or "none recorded";
   - exact files, sections, figures, claims, or semantic/venue choices the paper
   owner should inspect or decide;
   - impact on the final paper, reviewer risk, evidence strength, or export
     readiness;
6. end broad reports with a separate "Needs paper-owner attention" block;
7. choose or recommend the next safe workflow route;
8. report validation, ledger, and residual-risk evidence for any work performed.

## Paper-owner handoff mode

For broad handoffs, pre-author-review closure, post-execution summaries, or
managerial status reports, use:

**Gate-based Manager Report + Department Table + Decision Queue + Verification
Appendix**.

Recommended shape:

1. **30-second manager summary**: state, gate, route, last verified task,
   machine blockers, owner-gated decisions, external-gated actions, and the next
   safe route.
2. **Department Table**: department/internal owner module, owner lane/agent type,
   material inputs consumed, material outputs produced, narrative/template refs,
   evidence/artifacts, closure state, risk/blocker, owner attention, and
   final-paper impact.
3. **Decision Queue**: decision id, owner question, options, recommended option,
   no-decision consequence, blocked/enabled actions, and trigger/deadline.
4. **Verification Appendix**: commands, validator outcomes, fixture matrix
   status, ledger guard, snapshot freshness, changed files, commit hash when
   available, and unverified gaps.

Use `validated`, `ingested`, `recommended`, `blocked`, `owner-gated`, and
`external-gated` precisely. Split next steps into `auto-continuable`,
`requires paper-owner decision`, and `hard-gated/prohibited until explicit
authorization`. Never replace this with a vague "done" paragraph, raw logs, or
PUA rhetoric without validator and ledger evidence.


## v2 governance references

For v2 work, the manager must connect task routing to material objects:

- `entry-skills/yxj-paper-os/references/department-io-contract.md` defines the
  PMO + department model, mandatory task-packet bindings, material-object
  lifecycle, handoff fields, and hard boundaries.
- `entry-skills/yxj-paper-os/references/reader-narrative-governance.md` defines
  ReaderSpineBrief, ObjectRepresentationMatrix, TemplateQuantProfile,
  SectionFunctionBudget, VisualTableAlgorithmFormulaBudget,
  ReaderExperienceReviewReport, NarrativeBackflowTask, and expression-design
  expectations for CognitiveLoadBudget, ExplanationLadder,
  RhetoricalMoveMatrix, ClaimEvidenceVisibilityMap, and TerminologyRegister.

A writing, review, figure, evidence, method, or export task that affects the
reader-facing paper should not be reported complete unless it declares the
relevant narrative/template object refs or records a validator-accepted
not-applicable reason.

Manuscript, figure/table/algorithm/formula, review, and export tasks that are
paper-facing must also declare additive `expression_design_object_refs` or carry
a validator-accepted non-applicable exception. These refs do not replace
`narrative_object_refs`, `template_object_refs`, or `evidence_object_refs`.
`ExpressionDesignBundle` may index the typed objects, but cannot bypass their
independent validators.

For final/export-facing figures, Nature-grade figure governance is additive to
the same material plane. The manager should compile or collect:

- `NatureFigureContract` and `NatureFigureAestheticProfile` from Paper
  Architecture & Narrative;
- `NaturePanelEvidenceMap`, `FigureSourceDataStatistics`, and
  `FigureImageIntegrityRecord` from Evidence & Method;
- `FigureBackendRoute`, `NatureCaptionLegendBrief`, and `FigureExportBundle`
  from Manuscript & Figure Production;
- `RenderedSurfaceGateReport` and `NatureFigureQAReport` from Review &
  Governance.

This is how aesthetic quality is guaranteed: objective contract fields and
independent validators govern archetype, hierarchy, palette, typography, labels,
legend, background, source/data/statistics, image integrity, caption, export,
and rendered-surface checks. A figure-owner summary is not aesthetic closure.

## Manager boot and department accountability objects

At the start of broad paper work, use the manager boot checklist before drafting
or dispatching tasks. The boot record should answer these questions with current
evidence, not guesses:

1. What did the paper owner ask for, and what outcome/stop condition is active?
2. Which paper/project root and yxj-paper-os state snapshot are in force?
3. Which gate is active: status query, contract-only routing, department-manager
   subagent, Team lane lead, validation, migration, export, or owner decision?
4. Which departments are primary/support DRIs for the requested function?
5. Which material objects must be consumed, produced, validated, ingested, and
   possibly backflowed?
6. Which route mode is allowed now, and which actions are hard-gated?

Use the department object layer as the source of truth:

- `department-charter.yaml` for DRI scope, authority boundaries, owner-gated
  decisions, and prohibited actions;
- `department-material-manifest.yaml` for material ownership, consumers,
  validators, ledger ingestion, and backflow;
- `department-lane-registry.yaml` for allowed owner lanes and installed
  `agent_type`/non-subagent routes;
- `required-function-material-map.yaml` for function-to-material requirements;
- `department-state.yaml` for current readiness, blockers, stale evidence, and
  downstream impact;
- `department-handoff-report.yaml` for department-to-PMO handoff evidence;
- `manager-boot-checklist.yaml` for the activation snapshot.

The normal operating order is:

```text
ManagerBootChecklist
  -> DepartmentCharter / DepartmentMaterialManifest / DepartmentLaneRegistry
  -> RequiredFunctionMaterialMap / DepartmentState
  -> DepartmentRouteCard or direct TaskPacketV2Plus compilation
  -> execution lane or Team lane lead
  -> DepartmentHandoffReport / material candidate
  -> validator evidence
  -> ledger ingestion
  -> PMO state transition or backflow
```

Do not report `DepartmentState`, `DepartmentRouteCard`, or
`DepartmentHandoffReport` as completion by themselves. They can justify routing
or candidate validation, but closure still needs collected outputs, validator
passes, ledger ingestion, and explicit state transition.

Design Function is not Writing Production. Design owns reader experience,
argument choreography, information architecture, figure/text interaction,
material shape, expression-design controls, and reviewer-facing specifications.
Writing Production consumes those specifications to realize prose, captions,
tables, formulas, and export text. If a writer changes design intent, the change
must be routed back through the design/architecture accountability path rather
than hidden in a prose edit.

## Department Manager operating pattern

For broad or multi-lane work, the Paper Orchestrator should first choose the
responsible internal Department Manager rather than directly juggling every
module, lane, and material object. The default existence form is
`contract_only`: load `department-manager-governance.md` and the relevant
department contract, then produce or update a `DepartmentRouteCard`.

Use `department_manager_subagent` only for complex department slices, and only
with an installed OMX role from the lane registry. Use `team_lane_lead` only
after RALPLAN consensus and explicit current-story approval. Department Managers
return route cards, requested lanes, owner gates, and risks upward; they do not
spawn uncontrolled descendants, expose public commands, make semantic owner
decisions, launch Team by themselves, or certify completion.

A `DepartmentRouteCard` may justify TaskPacketV2 compilation, but final closure
still requires collected outputs, validator evidence, ledger ingestion, and
`compile -> execute -> collect -> validate -> ingest -> state_transition`.

## V2 department/material execution pattern

For a v2-managed task, compile a task packet from the lane registry and the
material objects, not from a generic prompt. The packet must contain:

- `owner_department`, `owner_lane`, and `agent_type`;
- `input_materials` and `expected_output_materials` with artifact ids/types and
  paths where outputs are expected;
- `narrative_object_refs` when the lane affects reader-facing problem, method,
  contribution, scenario, experiment, baseline, ablation, result, figure,
  table, algorithm, formula, review, or export representation;
- `template_object_refs` when target venue or exemplar form constrains output;
- `expression_design_object_refs` when paper-facing writing, visual/formal,
  review, or export work must consume reader-load, explanation ladder,
  rhetorical move, claim visibility, and terminology controls;
- Nature-grade figure object refs when the task draws, captions, reviews, or
  exports a final manuscript figure;
- `backflow_route`, `state_ingestion`, `state_transition`, and `pua_telemetry`;
- v2 validator refs required by the lane.

A manager handoff must consume these same objects. The department table should
show what each department consumed and produced, who owned the lane, what
validator evidence closed it, what owner decisions remain, and how the output
changes the final paper. Do not translate task logs directly into a final paper
report; translate them into reader-facing function, representation, evidence,
and reviewer-risk terms.

## V2 validation commands

Run all three checks from the plugin scaffold root:

```bash
python3 entry-skills/yxj-paper-os/scripts/validate_yxj_paper_os.py scaffold .
python3 entry-skills/yxj-paper-os/scripts/validate_yxj_paper_os.py fixtures .
python3 entry-skills/yxj-paper-os/scripts/run_fixture_suite.py .
```

The fixture suite must report a non-empty matrix with both valid and invalid
fixtures. Passing with zero valid or zero invalid fixtures is a failure through
`validate_fixture_matrix_nonempty`.

Binding exceptions must be independently accepted in `validator-report.yaml`; a task-local `narrative_binding_exception` or `template_binding_exception` cannot self-attest non-applicability. Declared material outputs must appear in `collected_outputs` or `artifact-ledger` and the referenced file must exist; raw file existence alone is not closure.

## Task-autonomy boundary

For scoped paper-progress requests, the orchestrator may automatically run
RALPLAN, prepare task packets, dispatch direct native subagents, update relevant
notes/ledgers, run validators, refresh snapshots, and report closure evidence.

The orchestrator must still ask before:

- Team launch;
- external submission/upload or credentialed services;
- destructive actions;
- active install, old-plugin uninstall, publishing, or marketplace update;
- paper-owner semantic decisions such as motivation, venue, contribution spine,
  claim scope beyond evidence, or private/raw source copying policy;
- mixing multiple plausible paper roots.

## Direct execution pattern

1. Build or load a `task-packet.yaml`.
2. Confirm `agent_type`, scoped context, expected outputs, collection path, state-ledger path, and `validator_refs`.
3. Launch the declared native subagent only inside an installed, permitted runtime.
4. Collect outputs.
5. Run validators.
6. Ingest state.
7. Stamp the ledger closure with `ledger_guard.py stamp` or an equivalent explicit ledger update.
8. Refresh the tracked snapshot when the paper repository ignores `.omx`: `ledger_guard.py snapshot --root <paper-root>`.
9. Run `ledger_guard.py check --root <paper-root> --require-snapshot-fresh` before claiming completion.
10. Mark complete only after state transition and a passing guard check.

## Team pattern

Team is not launched automatically. Use Team only after RALPLAN and explicit
current-story approval. Team workers return evidence; the leader owns
Ultragoal/state checkpoints.

## Registry-backed execution

Before launching a native subagent, resolve the task owner lane in
`skills/yxj-paper-execute/references/agent-lane-registry.yaml`. If the
recommended agent type is unavailable, mark blocked with evidence rather than
substituting silently.

## Ledger closure guard

`skills/yxj-paper-index/scripts/ledger_guard.py` is the canonical lightweight guard for final ledger closure:

- `check --root <paper-root>` validates required ledgers and rejects false
  completion, including complete tasks without collected outputs, passing
  validator evidence, `state_ingestion`, or `state_transition`.
- `stamp --root <paper-root> ...` upserts a completed task row, validator
  evidence, state ingestion, state transition, and optional artifact-ledger rows.
- `snapshot --root <paper-root>` mirrors `.omx/state/yxj-paper-os/` into
  `notes/yxj-paper-os/ledger-snapshot/` for repositories that ignore `.omx`.

Every yxj-paper-os operation that changes manuscript state, evidence, review,
figures, export, or planning must end with either an explicit ledger edit plus
`check`, or a `stamp`/`snapshot`/`check` sequence. A final answer should not
claim completion while `ledger_guard.py check` fails.

## PUA/RALPLAN governance operations

The yxj Paper Orchestrator is a single-entry PMO. The paper owner hands work to
this manager; departments and LLM agents are internal routing. For every bounded
execution, the manager adds `[PUA-DIAGNOSIS]`, owner-four-questions, and
`pua_telemetry` to the task packet or collected control artifact.

Escalation rules:

- L0: normal execution.
- L1: second failure or same-approach loop; switch to a fundamentally different approach.
- L2: guessing/no-search/passive wait; read state/source/original material and return `[PUA-REPORT]`.
- L3: poor-quality or repeated non-closure; complete the seven-item checklist.
- L4: isolate with minimal PoC, change lane, or mark blocked with evidence.

`pua_telemetry` is not a substitute for validator evidence. The manager must
still run validators, ingest state, and preserve `compile -> execute -> collect -> validate -> ingest -> state_transition`.
RALPLAN remains mandatory for architecture, route, tradeoff, or test-shape
uncertainty. Team remains gated by RALPLAN plus explicit current-story approval.


### PUA report semantic checks

At L2+ `pua_report.present:true` is mandatory and must exactly mirror failure count, failure mode, attempts, excluded causes, next hypothesis, and manager action from top-level `pua_telemetry`. At L3+ all seven checklist booleans must be true. L4 requires `failure_count >= 5`. These semantics are enforced by `validate_pua_telemetry` and covered by invalid fixtures.


### Explicit state transition fixture rule

Fixture-level validation mirrors `ledger_guard.py`: a task marked `complete` must include collected outputs, validator evidence, state ingestion, `pipeline_stage: state_transition`, and an explicit `state_transition` object with `from`, `to: complete`, and `at`. `pipeline_stage: state_transition` alone is not enough, and a `complete` task with another pipeline stage or non-complete transition target is invalid.

## Repository hygiene / delivery cleanliness gate

Before claiming pre-author-review, export readiness, or final handoff, run/read a `RepositoryHygieneReport`. The report must classify dirty entries by active paper, parent/shared, and sibling paper scope; name generated/ephemeral files; list disallowed entries; check ledger snapshot freshness and export-manifest hashes; and state the external-submission boundary. If the gate is not `pass`, report the paper as content-validated but delivery-dirty, blocked, or owner-gated.

## Manager-direct authority gate

Use manager-direct work only as an exception. If the manager directly produces,
reviews, verifies, exports, or transitions department-owned material, compile the
task with:

- `actor_provenance` that identifies execution actor, final certifier, run/session
  ids, and YAML/JSON provenance artifacts;
- `manager_direct_intervention` with declaration or provenance inference, reason,
  affected departments, independent-review requirement, and completion limit;
- `role_separation` proving executor, reviewer/verifier, and final certifier are
  distinct effective actors when the task is paper/export/claim/evidence/state
  sensitive;
- a manager handoff YAML block named `authority_role_separation`.

Do not close such work with a manager summary, PUA telemetry, or
`present:false`. Without trusted provenance and required independent review, the
allowed state is `candidate` or `validated`, not `complete`.


## Company-style material governance v2plus

The upgraded management model should be operated as a company-style paper
production system:

```text
PMO / Paper Orchestrator
  -> Department accountability
  -> Agent lane execution
  -> Internal skill SOP
  -> Material object candidate
  -> Validator evidence
  -> Ledger ingestion
  -> State transition or backflow
```

Use the single public `yxj-paper-os` entry. Do not expose internal
`skills/yxj-paper-*` modules as public commands. Skills are SOP capabilities
that produce/consume/review/repair/route material candidates under permissions;
they do not certify completion or make paper-owner semantic decisions.

### Phase-1 MVP material objects

Operate these seven objects as the first reusable institutional layer:

| Object | Owner | Main consumer |
| --- | --- | --- |
| `ReviewerQuestionMap` | Paper Architecture & Narrative | MainTextConstructionMatrix / writing / review |
| `MainTextConstructionMatrix` | Paper Architecture & Narrative | section-writing / content-refinement |
| `ClaimCitationCapsule` | Evidence & Method | MainTextConstructionMatrix / writing |
| `ResultPackage` | Evidence & Method | results writing / surface gate |
| `SingleWriterSectionLock` | PMO | section/shared-hotspot editing |
| `ReaderSurfaceTutorReview` | Review & Governance | backflow fixes |
| `RenderedSurfaceGateReport` | Review & Governance / Export | final rendered export checks |

### Expression-design material objects

Operate these as the reader-expression design layer below the reader question
and construction matrices:

| Object | Owner | Main consumer |
| --- | --- | --- |
| `CognitiveLoadBudget` | Paper Architecture & Narrative | section-writing / figure-caption / rendered-surface gate |
| `ExplanationLadder` | Paper Architecture & Narrative | MainTextConstructionMatrix / manuscript drafting / review |
| `RhetoricalMoveMatrix` | Paper Architecture & Narrative | section-writing / visual-formal production / review |
| `ClaimEvidenceVisibilityMap` | Paper Architecture & Narrative with Evidence & Method inputs | writing / review / claim-boundary checks |
| `TerminologyRegister` | Paper Architecture & Narrative | prose, captions, tables, export text |
| `ExpressionDesignBundle` | Paper Architecture & Narrative | optional index only; cannot replace typed-object refs or validators |

### Production tasks

Before a production task can claim completion, verify that it consumed the
required `ReviewerQuestionMap`, `MainTextConstructionMatrix`, evidence refs, and
`SingleWriterSectionLock` where applicable. Production lanes may provide
validator requirements but must not directly edit shared validator scripts,
fixture directories, or lane registry files.

### Fixture contract

Fixture cases live under `<plugin-root>/fixtures/valid/<case-dir>/` and
`<plugin-root>/fixtures/invalid/<case-dir>/`. Invalid fixture cases must include
`fixture-meta.yaml.expected_failures`; standalone YAML files directly under
`fixtures/valid` or `fixtures/invalid` are not accepted as fixture cases.


## Nature full-absorption control plane

Milestone M1 extends the earlier Nature-grade figure work into a broader yxj-native absorption layer for non-figure Nature skills. The source basis is `Yuan1z0825/nature-skills` at commit `5d2ba1dee1c087be6de8f4a8aad4b27f04974be9`. The absorption is not a public `nature-*` skill copy: the single public `yxj-paper-os` manager remains the only user-facing entry, and every absorbed capability is represented as an internal SOP/capability cell, material object, validator, fixture, backflow route, and ledger/state closure candidate.

The 14 first-class M1 materials are: `NatureSourceInventory`, `CompanySkillRegistry`, `NatureAbsorptionPackage`, `PaperReaderPackage`, `SearchStrategyDossier`, `CitationVerificationReport`, `SectionMovePlan`, `JournalStyleProfile`, `PolishingRepairReport`, `DataAvailabilityPlan`, `ReviewerPanelReport`, `ResponseActionMap`, `PresentationPlan`, and `PatentDraftBoundary`. `PresentationPlan` is owned by the existing canonical department id `manuscript_and_figure_production` as a writing/expression capability cell; the display label may say Manuscript / Figure / Communication Production, but the canonical id is frozen. Patent output is a source-grounded drafting aid only, not legal advice or a patentability guarantee.
