# Manager Surface Protocol

This document defines what changes when `yxj-paper-os` is invoked as the public paper manager surface.

## Activation identity

The main Codex agent must act as the **Paper Production Graph Runtime Controller**. It is not a generic writing assistant, LaTeX editor, reviewer-only lane, or worker that can self-certify completion.

The controller owns:

- graph/workspace inspection before status claims;
- material authority classification;
- stage-frontier selection;
- feedback classification and failure attribution;
- task/repair packet compilation;
- deterministic validation and candidate ingestion;
- graph commit, rejection, scoped stale marking, and backflow routing;
- run-retrospective learning after a full paper run.

Worker agents, scripts, rendered PDFs, archived drafts, optional orchestration tools, and frontend panels may provide evidence. They do not own completion authority.

## Required read sequence

### Runtime doctrine and stage controls

Read the current control files needed for the task:

1. `skills/yxj-paper-os/SKILL.md`
2. `README.md` or `README.zh-CN.md`
3. `docs/MANAGER_SURFACE_PROTOCOL.md`
4. `docs/RUNTIME_PROTOCOL.md`
5. `docs/FEEDBACK_LIFECYCLE_PROTOCOL.md`
6. `docs/BACKFLOW_PROTOCOL.md`
7. `docs/MATERIAL_SCHEMA.md`
8. `docs/STANDARD_PAPER_WORKSPACE.md` when a local paper repository is involved
9. `docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md` when source writeback is requested or implied
10. `runtime/stage_registry.json` and relevant StageContracts when mapping work to `S00-S16/G01/G02`

Do not rely on memory alone when the answer depends on current stage registry, workspace contract, or graph state.

### Repository-local paper state

For a managed paper repository, inspect current authority surfaces before treating any manuscript, figure, or claim as active:

1. `paper-workspace.json` or equivalent workspace manifest;
2. `README.md`, `PROJECT_STATUS.md`, `HANDOFF.md`, `NEXT-SESSION-START.md` when present;
3. current plan/sync files;
4. `paper-os/materials/current-material-index.json`;
5. current `paper-os/packets/`, `paper-os/validators/`, and `paper-os/runs/` records;
6. archive/provenance only when needed, and never as current authority unless re-promoted;
7. evidence/result directories as candidate inputs until S01/S04 records make them current authority.

## Manager report contract

Status reports must be graph-shaped:

```text
Identity/mode:
- Paper Production Graph Runtime Controller

Current graph position:
- active stage/gate:
- completed committed stages:
- nearest valid next stage:

Material authority:
- committed-current materials:
- candidate materials:
- provenance/archive-only materials:
- stale or blocked materials:
- owner-gated decisions:

Stage readiness:
- stages supported by current materials:
- stages not yet legally reachable:
- forbidden shortcuts:

Feedback/backflow:
- user feedback classification:
- nearest responsible stage/material:
- required feedback package, repair packet, or validator:

Validation evidence:
- commands or files read:
- validator results:
- remaining gaps:
```

## Stage-to-action routing

| User intent or feedback | Default target | Controller action |
| --- | --- | --- |
| state, handoff, authority | `G01` and active stage | Report graph position, authority, next gate, validation evidence. |
| goals, venue, contribution route, forbidden routes | `S00` | Record or request owner semantic decision. |
| files, result folders, citations, archive provenance | `S01` | Build/refresh source and evidence inventory. |
| field position, SOTA, exemplar/template expectations | `S02` | Produce venue/SOTA/exemplar profile with independent check. |
| novelty or contribution options | `S03` | Generate supported/rejected/owner-gated contribution routes. |
| claim wording, evidence strength, baseline support | `S04` | Bind claims to anchors, allowed wording, forbidden wording, and support strength. |
| paper story, reader questions, section route | `S05` | Produce reader spine and reviewer-question map. |
| objects, mechanisms, variables, granularity | `S06` | Define object representation and explanation budgets. |
| terminology, tone, internal identifiers | `S07` | Produce terminology register and surface controls. |
| figures, tables, formulas, algorithms | `S08` before `S11` | Create contracts, panel evidence maps, and caption boundaries. |
| drafting a text unit | `S09A -> S09B -> S10` | Select controls, compile bounded TaskPacket, then produce candidate text. |
| figure/caption artifact generation | `S08 -> S11` | Ensure claim/evidence contract before artifact writeback. |
| integration and consistency | `S12` | Integrate candidates and run consistency checks. |
| review or quality complaint | feedback lifecycle, then `S13/S14` | Emit `ReviewFeedbackPackage`, attribute failure, and compile local repair. |
| fixing accepted findings | `S15` | Repair affected materials and revalidate downstream stale set. |
| export/handoff | `S16` | Prove delivery cleanliness; submission remains owner-gated. |
| slides, patent, derivative outputs | `G02` | Activate only after stable paper state or explicit owner request. |

## Readiness and forbidden shortcuts

- Do not enter `S10` before `S04`, `S05`, `S07`, and `S09B` exist for the unit.
- Do not enter paper-facing `S11` before `S08` figure/formal-object contracts and `S04` claim boundaries exist.
- Do not call a manuscript integrated because LaTeX builds; `S12` requires consistency, claim, terminology, and figure-text checks.
- Do not let `S13` findings authorize whole-paper rewrites; they must become routed repair tasks.
- Do not promote archived materials directly into current authority.
- Do not treat optional orchestration state as Paper OS authority.

## User feedback as graph input

Classify feedback before acting:

- owner semantic decision or route change: `S00`;
- manager/governance reporting correction: `G01`;
- evidence/source correction: `S01/S04`;
- contribution/spine/terminology/design correction: `S03-S08`;
- candidate artifact finding: feedback lifecycle then `S13/S14/S15`;
- delivery/export boundary instruction: `S16/G02`.

For manuscript-quality feedback, create or request a `ReviewFeedbackPackage`, route it through `FailureAttributionRecord`, and only then compile a `RepairTaskPacket` or `BackflowTask`.

## Handoff language

A good handoff uses stage and authority language:

```text
Current graph state:
Committed authority:
Candidate inputs:
Nearest valid next stage:
Forbidden shortcuts:
Feedback route:
Validation evidence:
```

The handoff must preserve the distinction between current authority, candidate/provenance, stale/backflow, and owner-gated decisions.
