# Runtime Protocol — Main-Agent Control

The main agent is the **Paper Production Graph Runtime Controller**. It owns process control and graph authority.

## Runtime loop

```text
observe graph
  -> choose frontier or feedback item
  -> compile task/repair packet
  -> dispatch specialist or deterministic script
  -> collect candidate output
  -> validate
  -> commit / reject / mark stale / create backflow
  -> after full run, evaluate retrospective learning
```

## Graph state summary

```yaml
GraphState:
  active_target:
  current_gate:
  committed_materials:
  candidate_materials:
  stale_materials:
  blocked_materials:
  owner_gated_materials:
  open_feedback_packages:
  open_review_findings:
  open_backflow_tasks:
  proposed_stage_improvements:
  next_frontier:
```

A template-only LaTeX build proves template sanity, not S12 integration or manuscript readiness.

## Frontier priority

```text
owner-gated root decision
> blocked upstream material or validator prerequisite
> active feedback attribution or repair task
> stale downstream regeneration
> missing task packet for active manuscript unit
> candidate output awaiting validation
> review finding awaiting classification
> export/rendering blocker
> post-run stage improvement
> optional improvement
```

## TaskPacket boundary

Subagents receive bounded context only:

```yaml
TaskPacket:
  schema_version: ppg-task-packet/v0.1
  packet_id:
  status: planned
  task_kind:
  agent_type:
  mission:
  target_material:
  input_materials: []
  mandatory_controls: {}
  evidence_anchors: []
  forbidden_routes: []
  allowed_actions: []
  allowed_read_paths: []
  allowed_write_paths: []
  allowed_tools: []
  output_artifact_path:
  expected_output_schema:
  expected_material_type:        # optional typed-material refinement
  expected_payload_schema:       # optional typed-payload refinement
  internal_execution_protocol:   # optional stage-specific pass/work-queue contract
  output_contract:               # optional stage-specific material module contract
  coverage_ledgers_required: []  # optional explicit coverage/unresolved/handoff ledgers
  descriptive_not_prescriptive_controls: {} # optional language/profile misuse guard
  validators: []
  return_format:
  ingestion_target:
  stop_condition:
  failure_report_format:
  worker_boot_clause:
  completion_forbidden: true
  no_recursive_orchestration: true
  owner_gate_required: false
```

Workers return `CandidateArtifactReturn` plus candidate artifact/evidence. They do not mark completion, recursively dispatch agents, change owner intent, or write outside allowed paths.

S02 uses the optional typed-packet fields. Its packet must force a multi-pass queue: source/citation/exemplar inventory, SOTA family mapping, comparator verification, template/exemplar extraction, language/rhetorical profiling, and downstream handoff/backflow. The worker output is an `S02ResearchDossier` candidate only. The controller must reject any S02 output that treats sampled language statistics as fixed writing rules or that claims contribution, final prose, graph, manuscript, submission, or publication completion.

## RepairTaskPacket boundary

Repair packets are scoped current-paper repair contracts. They wrap or point to strict TaskPackets/BackflowTasks and inherit the same authority restrictions:

- no completion authority;
- no recursive orchestration;
- no owner-intent changes;
- no whole-paper rewrite unless owner-gated;
- scoped read/write paths;
- explicit preserve and must-change clauses;
- downstream stale targets and validators.

## Dispatch policy

Use scripts for deterministic tasks:

- schema validation;
- graph consistency;
- stale propagation;
- artifact indexing;
- internal-code scanning;
- rendered text scanning;
- hash/manifest generation.

Use semantic agents for bounded tasks:

- field/SOTA analysis;
- contribution challenge;
- claim boundary analysis;
- paper spine and reader questions;
- writing and caption candidates;
- adversarial review;
- failure attribution review for high-risk findings.

## Main-agent lane policy

The stage registry controls single/double-lane use:

```text
read stage.subagent_lane_policy
  -> mandatory_double: producer + independent verifier
  -> conditional_double: producer, add verifier on listed triggers
  -> single_with_deterministic_validation: script/controller plus validators
  -> controller accepts, rejects, or routes backflow
```

## Commit protocol

```text
candidate exists
  -> validators pass
  -> provenance recorded
  -> stale impact checked
  -> graph status updated
  -> active version pointer updated
```

Only then can a node become `committed`.

## Retrospective protocol

After a full paper run or major review cycle:

```text
collect feedback/repair records
  -> group recurring failure patterns
  -> decide current-paper issue vs system issue
  -> propose StageImprovementRecord candidates
  -> add regression tests before changing prompts/task packets/validators
```

A StageImprovementRecord is a system-learning proposal. It does not directly edit the current manuscript.

## Authority boundaries

- Owner intent changes require owner decision evidence.
- Subagents cannot commit or close graph nodes.
- Reviewers produce findings, not whole-paper edits.
- Main agent can repair locally only inside existing owner-approved semantics.
- Optional orchestration tools are adapters, not Paper OS authority sources.

### S00 owner semantic contract boundary

S00 is the root semantic authority stage and stays `owner_gated`.
It records `OwnerIntake` and `OwnerSemanticContract` materials; it does not
dispatch a normal worker-production packet. Advisory subagents may identify
contradictions, downstream risks, or missing owner questions, but the controller
can commit only owner-confirmed decisions or explicit owner-gated assumptions.

The S00 contract must keep these hard boundaries explicit:

- no worker may select the venue route, change owner intent, increase claim
  strength, authorize private-source use, or approve external actions;
- `submission_allowed` and `public_release_allowed` remain false until a later
  owner-approved gate changes them;
- blocked routes include reasons and unblock conditions;
- changes to route, claim scope, source/privacy policy, or external-action
  policy mark downstream provenance, analysis, claim, spine, review, and export
  stages stale as declared by the contract.

### S01 read-only inventory boundary

S01 is a hybrid-generated inventory stage, but it still keeps
`requires_worker_task_packet: false`. A worker may receive a read-only inventory
brief (`ppg-readonly-inventory-task/v0.1`) and return a candidate inventory, but
it must not mutate source files, commit graph state, dispatch subagents, infer
missing locators, or decide claim admissibility.

The S01 controller commit must validate:

- every supplied root is scanned or explicitly excluded with reason;
- citation keys, BibTeX/PDF metadata, result artifacts, figure source data,
  editable figure sources, supplements, and data-availability materials are
  locatable or listed in the unresolved locator register;
- hash/mtime/freshness state is recorded where required;
- private or forbidden sources from S00 policy are marked and never promoted as
  citable public evidence;
- S01 outputs support hints only. S04 remains responsible for admissibility,
  support strength, allowed wording, and forbidden wording.

### S02 research profile and descriptive-language boundary

S02 keeps `requires_worker_task_packet: true` and `mandatory_double`
producer/verifier policy because its SOTA, exemplar, and language-profile
outputs shape downstream novelty, spine, and surface-control decisions. The
packet is strict and output-scoped: workers may read the declared material
bundle and write only the declared candidate `S02ResearchDossier` artifact.

The S02 controller commit must validate:

- every source cluster, comparator family, exemplar, and language-profile
  sample is processed, excluded with reason, or unresolved;
- unresolved source or exemplar gaps are routed back to S01/S00 rather than
  silently ignored;
- paragraph-function, syntax, lexical, citation, result-narrative,
  limitation-language, and quantitative style observations are present;
- quantitative metrics are descriptive distributions with sample limits and
  confidence notes;
- S03/S05/S07 handoffs state allowed use and misuse warnings;
- no exemplar copying, final prose, contribution freeze, final claim wording,
  graph completion, manuscript readiness, submission readiness, or publication
  readiness is claimed.

### S03 contribution option classifier boundary

S03 keeps `requires_worker_task_packet: true` and `mandatory_double`
producer/verifier policy. It consumes S02 research/SOTA context plus evidence
and owner boundaries, then produces a candidate `S03ContributionOptions`
material. It does not produce admitted claims or manuscript-ready contribution
language.

The S03 controller commit must validate:

- every generated or detected contribution option is classified as supported,
  supportable after S04, weak, owner-gated, or rejected;
- every option appears in the option coverage ledger;
- every option has SOTA contrast, evidence-readiness classification, and
  reviewer-attack/coherence evidence;
- rejected and weak options are recorded with reopening/backflow conditions;
- owner-gated options have owner-decision and semantic-shift records;
- only claim-bearing supported/supportable options are handed to S04;
- no S03 output contains claim admissibility, final claim wording, allowed
  wording, graph completion, manuscript readiness, submission readiness, or
  publication readiness.

### S04 evidence-to-claim admissibility boundary

S04 keeps `requires_worker_task_packet: true` and `mandatory_double`
producer/verifier policy. It converts S03 claim candidates and evidence/result
materials into `S04ClaimAdmissibility` capsules. Its completion boundary is:
claim admissibility only, with no final prose and no graph/manuscript/export/
submission/publication completion claim.

The S04 controller commit must validate:

- every claim-bearing unit appears in `claim_queue`, is decomposed into atomic
  claim rows, and has a `claim_coverage_ledger` decision;
- every capsule is admitted, weakened, rejected, owner-gated, or backflowed;
- admitted/weakened capsules have non-unsupported support strength, evidence
  anchors, allowed wording, forbidden wording, required caveats, and a result
  package boundary;
- unsupported, forbidden, rejected, or missing-locator claims are routed through
  `unsupported_claim_backflow_register` or `unresolved_backflow_register`;
- result packages state what they support and do not support, including
  forbidden interpretations;
- downstream handoffs to S05/S07/S10/S12/S13 carry claim ids, allowed use, and
  misuse warnings;
- no S04 output contains final prose, manuscript text, PDF/export readiness,
  graph completion, manuscript readiness, submission readiness, or publication
  readiness.

### S05 reader-spine controller boundary

S05 keeps `requires_worker_task_packet: true` and `mandatory_double`
producer/verifier policy. It turns S04 claim-admissibility capsules plus S02
research/profile context and S03 contribution-option context into a
`S05ReaderSpine` controller material. Its public graph I/O remains unchanged:
it consumes `motivation`, `contribution options`, `template profile`, and
`claim materials`; it produces `reader spine`, `reviewer question map`, and
`rationale matrix`.

The S05 controller commit must validate:

- every S04 intake claim is accounted for in
  `admitted_claim_intake_ledger` and `claim_section_coverage_ledger`;
- every placed S04 claim appears in `reader_spine.claim_to_section_spine`;
- no raw S03 option or new claim id is introduced into the spine, rationale
  matrix, or coverage ledgers;
- every reader question appears in the inventory, coverage ledger, and
  progression or has explicit backflow/owner gating;
- front-half promises have payoff sections and overpromise risks;
- reviewer questions, rationale rows, exclusions, owner decisions, and
  unresolved backflow are explicit;
- S06/S07/S08 handoffs and handoff coverage are present with allowed use and
  misuse warnings;
- no S05 output contains final prose, manuscript text, PDF/export readiness,
  graph completion, manuscript readiness, submission readiness, or publication
  readiness.


### S06 object/granularity controller boundary

S06 keeps `requires_worker_task_packet: true` and `conditional_double` lane
policy. It converts S05 reader-spine controls, S04 claim visibility, S02
template profile context, and terminology controls into an
`S06ObjectGranularity` controller material. Its public graph I/O remains
unchanged: it consumes `reader spine`, `reviewer question map`,
`template profile`, and `claim visibility`; it produces `object representation
matrix`, `section function budget`, `load budget`, and `explanation ladder`.

The S06 controller commit must validate:

- every detected object and mechanism variable is processed, explicitly
  excluded, deferred, downgraded, unresolved, or backflow-required;
- every represented P0/P1/P2 object has an object card and explanation ladder;
- represented mechanism variables have variable cards linked to known objects;
- object-to-claim maps use only S04/S05-sourced claim ids and do not introduce
  new claims;
- object-to-reader-question and object-to-section maps cover S05 reader
  questions and planned section use;
- granularity progression, section function budget, cognitive load budget,
  repetition risk check, coverage ledger, and unresolved-object report are
  present;
- S07/S08/S10 handoffs are explicit and include allowed use plus misuse
  warnings;
- no S06 output contains final prose, manuscript text, PDF/export readiness,
  graph completion, manuscript readiness, submission readiness, or publication
  readiness.


### S07 rhetoric/surface-control boundary

S07 keeps `requires_worker_task_packet: true`, `hybrid_generated` execution,
writer producer role, and `conditional_double` lane policy. It converts S02
language-profile controls, S04 claim wording boundaries, S05 reader-spine
controls, S06 object/granularity controls, and terminology inputs into
`S07RhetoricSurfaceControl`. Its public graph I/O remains unchanged: it
consumes `object representation`, `claim visibility`, and `evidence wording`;
it produces `construction matrix`, `rhetorical matrix`, `terminology register`,
and `surface rules`.

The S07 controller commit must validate:

- every S04 claim capsule has a claim-safe surface rule or explicit unresolved
  backflow;
- every S06 object/variable has a reader-facing terminology rule or explicit
  unresolved backflow;
- internal material ids, object ids, raw claim ids, pipeline labels, and
  lab-notebook handles are banned or scoped out of prose-facing contexts;
- S05 reader questions/section functions map to paragraph jobs with claims,
  objects, evidence, caveats, and forbidden content;
- rhetorical moves are flexible function-specific variants, not a universal
  fixed paragraph template;
- S02 language statistics remain descriptive and do not become fixed word,
  sentence, paragraph-length, cadence, or exemplar-copying rules;
- forbidden expression categories and S09/S10/S12/S13 handoffs are present;
- no S07 output contains final prose, new or strengthened claims, internal-id
  leakage authorization, graph completion, manuscript readiness, submission
  readiness, or publication readiness.


### S08 visual/formal planning boundary

S08 keeps `requires_worker_task_packet: true`, `hybrid_generated` execution,
designer producer role, and `conditional_double` lane policy. It compiles S04
claim/evidence boundaries, S05 reader-question spine controls, S06
object/section budgets, S01/evidence source-data routes, terminology inputs,
and optional S07 surface controls into `S08VisualFormalPlan`. Its public graph
I/O remains unchanged: it consumes `reader spine`, `section function budget`,
and `claim evidence materials`; it produces `visual budget`, `figure
contract`, `panel evidence map`, and `backend route`.

The S08 controller commit must validate:

- input coverage across S04/S05/S06/S01/evidence/terminology materials is
  explicit, with missing inputs backflowed;
- visual needs are extracted from reader/reviewer questions before candidate
  figures, tables, algorithms, formulas, or schematics are proposed;
- every candidate is kept, merged, moved to supplement, deferred, or rejected
  with a reason;
- visual budget and main-story visual path prevent decorative or overloaded
  figures;
- every paper-facing figure/table/formal object has reader role, proof role,
  supported and unsupported claim boundary, source S04 capsule, backend route,
  and caption/legend boundary;
- every required figure panel has source data/evidence refs, supported and
  forbidden claims, labels, and caveats;
- schematics and formal objects are not treated as empirical evidence;
- backend routes, main/supplement split, accessibility/style constraints,
  coverage ledger, unresolved report, and S10/S11/S12/S13 handoffs are
  present;
- no S08 output contains final figures, final captions, new or strengthened
  claims, manuscript/export artifacts, graph completion, manuscript readiness,
  submission readiness, or publication readiness.


### S09A/S09B control-selection and packet-assembly boundary

Bare `S09` remains forbidden. Runtime attribution must use `S09A` for control
selection failures and `S09B` for packet-assembly failures.

S09A keeps `requires_worker_task_packet: false` and
`single_with_deterministic_validation`. It selects a target-specific,
context-rich, priority-ordered `S09ARichControlBundle`. Rich context is
allowed and encouraged when useful; the validation boundary is structure, use
labels, priority rules, freshness, conflict resolution, and negative controls,
not mechanical minimization.

The S09A controller commit must validate:

- target unit identity, target stage, write-path candidate, dependencies, and
  downstream consumers are explicit;
- S04 claim/evidence hard constraints, forbidden claims, allowed/forbidden
  wording, caveats, and authority requirements are present;
- local, adjacent, and global context are separated; global orientation and
  style profile are background only;
- S04/S05/S06/S07 and applicable S08 controls are selected with negative
  controls and no internal-id leakage;
- conflicts are resolved by priority order before any worker sees the packet;
- context usage instructions state what must be obeyed, what is local/adjacent
  context, what is background-only, and what must not be quoted, claimed, or
  output;
- freshness, missing-control report, coverage ledger, excluded/deferred
  controls, and downstream S09B packet requirements are present;
- S09A does not compile the worker packet, draft final content, dispatch
  subagents, or claim graph/manuscript completion.

S09B keeps `requires_worker_task_packet: false`,
`script_generated` execution, and `single_with_deterministic_validation`. It
compiles one bounded `S09BTaskPacketAssembly` and an emitted strict TaskPacket
for S10/S11/S15 execution.

The S09B controller commit must validate:

- packet identity, target unit, selected S09A bundle ref, task mission, and
  emitted packet ref are explicit;
- allowed read paths are concrete and safe; allowed write paths contain exactly
  one target path and match the single-writer lock;
- forbidden routes include graph/manuscript completion, submission/publication
  readiness, recursive dispatch, owner-intent change, unrelated-section
  alteration, new claims, and claim strengthening beyond S04;
- worker boot clause includes completion forbidden, no recursive
  orchestration, allowed write paths, S04 hard constraints,
  MissingMaterialReport behavior, and candidate/evidence/risk return;
- section/unit move plan propagates allowed claims, evidence, objects,
  rhetorical moves, forbidden moves, figure callouts, caveats, and stop
  condition;
- S09A context usage labels are preserved, especially background-not-claim
  authority;
- return format, missing-material report, stale policy, single-writer lock,
  packet authority boundary, and validate_packet-clean emitted packet are
  present;
- S09B does not generate candidate content, claim graph/manuscript completion,
  alter owner intent, or broaden the target unit.


### S10 packet-bounded candidate prose boundary

S10 keeps `requires_worker_task_packet: true`, `agent_generated` execution,
writer producer role, and mandatory writer/verifier split. It may start only
from a validate_packet-clean S09B TaskPacket. The packet is the sole authority
for target unit, allowed paths, hard claim boundaries, local/adjacent/context
usage, object granularity, terminology, visual/formal callout limits, and
return format.

The S10 writer must execute these passes in order: boot the authority boundary,
read/validate the S09B packet, extract hard constraints, extract reader and
move plan, extract object/terminology controls, extract visual/formal controls
when applicable, build the unit skeleton, draft candidate text, generate
traces, self-check, write only to the allowed path, and return
`CandidateArtifactReturn`.

The S10 verifier independently checks packet target, allowed write path, no
completion claim, no recursion request, every claim mapped to S04, no claim
strengthening, caveats, move trace, terminology/internal-id controls, S06
object granularity, S08 visual callout boundary, candidate return completeness,
and honest risk reporting. The verifier does not rewrite the candidate.

S10 failure routes to the nearest responsible stage: S09B for packet defects,
S09A for thin/stale controls, S07 for terminology/surface failures, S06 for
object granularity failures, S05 for unclear reader function, S04 for claim
boundary/evidence defects, S08 for visual/formal callout defects, and S15 for
scoped regeneration after attribution.


### S11 contract-bound visual/formal artifact boundary

S11 keeps `requires_worker_task_packet: true`, `hybrid_generated` execution,
executor producer role, and conditional verifier escalation. It executes an
S09B/S11 task packet against an S08 visual/formal contract, S04 claim
boundaries, S01/S08 source-data routes, S07 terminology/surface controls, and
a visual quality profile.

S11 may improve visual clarity, readability, accessibility, journal-fit, and
render/export planning. It may not change proof role, supported claims,
evidence encoding, panel interpretation, caption claim strength, caveats,
source-data provenance, or owner intent. Visual polish must be recorded as a
policy-bound report with `claim_meaning_changed=false`,
`evidence_encoding_changed=false`, and `proof_role_changed=false`.

If rendering is not executed or not allowed, S11 must return a render plan
rather than claiming final export readiness. S16 remains the owner-facing
export/PDF preflight stage.

S11 failure routes to S08 for missing/wrong visual contracts or backend routes,
S04 for caption/panel claim boundary defects, S01 for source-data/provenance
gaps, S07 for terminology/surface defects, S09B for packet authority/path
defects, and S15 for scoped regeneration after attribution.


### S12 structured integration and consistency boundary

S12 consumes structured S10 candidate returns and S11 visual/formal bundles plus
upstream controls. It produces a structured integrated candidate package, trace
indexes, audits, findings, a backflow queue, and a validator report. It must
not compile or export PDF, claim final manuscript/submission/publication
readiness, change claim boundaries, or repair by untracked rewrite.

S12 may mark `ready_for_s13_review=true` only when blocker/high consistency
issues are absent or explicitly routed according to controller policy. It must
keep `ready_for_s16_export=false`; S16 is responsible for human-readable PDF
and export/handoff readiness after review/repair closure.

S12 findings route to the nearest responsible stage: S04/S05/S06/S07/S08 for
upstream semantic/control failures, S09A/S09B for control selection or packet
propagation failures, S10/S11 for candidate generation failures, and S14/S15
for repair planning/execution.

### S13 adversarial review and loss-signal boundary

S13 consumes the structured S12 integrated candidate package plus S12 traces,
S10/S11 candidate traces, and S04-S08 upstream controls. Its primary review
object is the structured S12 package, not a PDF. Human-readable PDF/export
belongs to S16.

S13 produces actionable adversarial review findings and reviewer-risk reports.
It must not rewrite the manuscript, execute repairs, dispatch recursive agents,
export or review PDF as the primary object, change owner intent, or mark graph/
manuscript/submission/publication completion.

The S13 critic protocol is ordered: authority-boundary boot, review-object
inventory, scope definition, claim/evidence attack, reader-path attack,
method/result attack, figure/caption attack, terminology/surface attack,
desk-risk synthesis, finding generation, actionability gate, and candidate
return. A verifier lane checks that every accepted finding has evidence,
affected artifact, affected location, severity, nearest responsible stage,
local repair scope, and S14 routing.

S13 accepted findings enter S14. S14 decides the bounded repair plan and S15
executes local regeneration; S13 itself only reviews to route.


### S14 nearest-responsible backflow compilation boundary

S14 consumes accepted S13/S16/validator findings, validator evidence, the
affected material graph slice, and owner-gate policy. It classifies each finding,
chooses the nearest responsible concrete stage/material, records rejected route
alternatives, defines downstream stale nodes, protects unrelated nodes, and
compiles bounded repair plans for S15 or upstream regeneration.

S14 must not execute the repair. It must not create fake strict worker packets
for itself because `requires_worker_task_packet` is false. It must not route to
bare `S09`; packet/control issues must be attributed to `S09A` or `S09B`. A plan
is not a closure: S15/S16 validators and any owner decisions are still required
before a finding can be marked resolved.


### S15 scoped repair execution boundary

S15 executes only the repair task authorized by S14. It must acknowledge the
strict repair packet, capture a pre-repair snapshot, modify only allowed paths,
regenerate or revalidate the affected downstream set, prove protected unrelated
nodes are unchanged, and return finding-resolution plus no-new-high-severity
evidence.

S15 may produce revised material/text/figure candidates and regenerated task
packet candidates, but it does not commit graph state, close findings by itself,
compile/export PDF, claim manuscript/submission readiness, or dispatch recursive
agents. If the S14 task is too broad, impossible, under-specified, or missing
authority, S15 returns a blocker/missing-material report rather than expanding
scope.

## S16 target-global delivery hardening

S16 `ppg-s16-export-handoff-package/v0.1` requires `payload.delivery_target`. This in-place safety hardening prevents stage-local export hygiene from being mistaken for compiled PDF target completion. Compiled initial/revised PDF targets require source-writeback, post-writeback validation, and content-bearing rendered text evidence; explicit template-only/export-hygiene handoffs remain non-compiled targets.

## S09/S10 Material-Closure Runtime Rule

S09/S10 production must preserve original material authority. Runtime controllers should treat S09 summaries as navigation and require S09B packets to carry current-authority material closure modules (`control_digest_policy`, `global_material_coverage`, `unit_material_closure`, `material_access_manifest`, `material_read_obligations`, `deferred_control_ledger`, and `section_specific_blockers`).

S10 workers must complete a material hydration pass before drafting and return `material_hydration_report` plus `material_read_receipt_ledger`. Missing section-critical material is a blocking condition, not a non-blocking `remaining_risks` note. S12/S16 should consume the same receipts when checking integration and rendered delivery surfaces.

## Rendered manuscript audit gate

After S16 creates a human-readable export/handoff package, the controller may run `RenderedManuscriptAuditGate` for compiled owner-facing targets. S16 remains export hygiene; the rendered gate audits paper-facing quality from the exported PDF/text/hash evidence and routes failures back through S14/S15 or the nearest accountable stage. Verify the gate contract with:

```bash
python3 scripts/verify_rendered_manuscript_audit_gate.py
```
