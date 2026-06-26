# Skill registry governance — yxj-paper-os

This reference defines how `yxj-paper-os` treats skills inside the company-style
paper production system.

## Core rule

A skill is a reusable SOP capability. It is not:

- a department;
- an agent/person;
- a hidden manager;
- a final certifier;
- a substitute for validators, ledgers, or paper-owner decisions.

The public user-facing entry remains `yxj-paper-os`. Internal skills are called
by the PMO or a department lane through a task packet and must return material
objects plus evidence, not unmanaged prose claims of completion.

## Required registry fields

Every internal skill entry must be representable as:

```yaml
skill_id:
owning_department:
primary_department_dri:
primary_lane_dri:
allowed_callers:
mode_permissions:
  - produce
  - consume
  - review
  - repair
  - route
input_materials:
output_materials:
validator_refs:
ledger_targets:
hard_gates:
references:
templates:
fixture_cases:
authority_limits:
function_responsibility:
lane_responsibility:
material_io:
state_controls:
```

## Permission meanings

| Permission | Meaning | Hard limit |
| --- | --- | --- |
| `produce` | create a candidate material object | cannot self-certify |
| `consume` | read declared upstream materials | cannot invent missing evidence |
| `review` | emit review findings or tutor comments | cannot be final certifier for its own output |
| `repair` | produce a bounded fix candidate | cannot change claim boundary without Evidence/Method approval |
| `route` | recommend a department/backflow route | PMO/state steward performs the actual transition |

## CompanySkillRegistry material

The PMO owns `CompanySkillRegistry` as a governance material. It records:

- skill id and human-readable purpose;
- owning department;
- primary department DRI and lane DRI for the governed function;
- allowed caller departments/lanes;
- permitted modes;
- required inputs and outputs with material-level department DRI, validator,
  ingestion, ledger, and backflow bindings;
- validator refs and fixture cases;
- ledger targets;
- hard gates and authority limits;
- references/templates used by the skill.

The registry is consumed by `TaskPacketV2Plus` compilation and by validators
checking that a worker used an allowed SOP capability for the declared material
object.

Each `capabilities[]` row must bind four responsibilities:

1. `function_responsibility` — the capability/function id, primary department
   DRI, primary lane DRI, validation owner, ingestion owner, backflow target, and
   completion limit.
2. `lane_responsibility` — the execution lane, owning department, allowed
   callers, public-surface prohibition, hidden-manager prohibition, and absence
   of state-transition authority.
3. `material_io` — input and output material contracts with primary department
   DRI, validator ownership, ingestion ownership, ledger targets, and backflow
   targets.
4. `state_controls` — registry/artifact ledger targets plus the department that
   owns ingestion and the department that receives failed validation/backflow.

Internal department SOPs remain hidden capability cells. They are invalid if
they are exposed as public `$` skills, declare themselves a department manager,
or claim completion without validator evidence and ledger ingestion.

## Anti-hidden-manager checks

A skill entry is invalid when it:

1. declares itself as final certifier;
2. exposes itself as a public `$` command for ordinary users when it is intended
   to remain internal;
3. mutates ledger/state directly without a state-steward route;
4. makes paper-owner semantic decisions;
5. changes claim boundaries without Evidence & Method approval;
6. allows completion without validator evidence.

These checks are enforced later through fixture-backed validators. Until those
validators exist, PMO handoff must explicitly state that a skill-produced output
is only a candidate material object.

## Relationship to departments and agents

```text
Department owns accountability.
Agent lane performs the task.
Skill provides the SOP.
Material object carries the output.
Validator proves the contract.
Ledger stores the institutional memory.
PMO coordinates route and closure.
```

This separation is mandatory. It lets agents remain intelligent and adaptive
without turning ad hoc writing into ungoverned completion claims.


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
