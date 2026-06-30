# PPG Runtime Control Block Diagram

This document defines the complete runtime as a control block diagram. Each stage receives a `TaskPacket + MaterialBundle`, consumes explicit upstream materials, produces required output materials, and returns candidates to the main-agent runtime controller for validation and graph commit/backflow.

## Diagram files

- Interactive frontend: [`docs/runtime-viewer/index.html`](runtime-viewer/index.html)
- Editable source: [`docs/diagrams/ppg-runtime-control-block.drawio`](diagrams/ppg-runtime-control-block.drawio)
- Preview PNG: [`docs/diagrams/ppg-runtime-control-block.png`](diagrams/ppg-runtime-control-block.png)
- Embedded editable PNG: [`docs/diagrams/ppg-runtime-control-block.drawio.png`](diagrams/ppg-runtime-control-block.drawio.png)
- SVG: [`docs/diagrams/ppg-runtime-control-block.svg`](diagrams/ppg-runtime-control-block.svg)

## Runtime pattern

```text
Main Agent / Runtime Controller
  -> compiles TaskPacket + MaterialBundle
  -> dispatches one bounded stage
  -> collects candidate outputs
  -> runs validators
  -> commits graph state or creates backflow
```

## Stage summary

| Stage | Input bundle | Output materials |
| --- | --- | --- |
| S00 Owner semantic contract | human need, paper profile, evidence summary | paper profile, motivation, decisions, forbidden routes |
| S01 Source/citation/evidence inventory | files, BibTeX, result dirs, locators | source map, citation bank, evidence bank, Nature source inventory |
| S02 Research/scene/template/SOTA | source map, venue, exemplars | research dossier, reader package, search strategy, template/journal profile |
| S03 Novelty/contribution options | research, evidence, SOTA, motivation | contribution options, evidence-readiness, risk list |
| S04 Evidence-to-claim admissibility | evidence bank, citations, results, contribution options | claim capsules, result packages, claim visibility, data availability, admitted contribution scope |
| S05 Paper spine/reader questions | motivation, contribution, template, claims | reader spine, reviewer question map, rationale matrix |
| S06 Object/granularity design | spine, questions, template, claim visibility | object representation, section budget, load budget, explanation ladder |
| S07 Rhetoric/terminology/surface controls | object design, claim visibility, evidence wording | construction matrix, rhetorical matrix, terminology register, surface rules |
| S08 Visual/formal planning | reader spine, section/function budget, claims/evidence | visual budget, figure contract, aesthetic profile, panel evidence, backend route |
| S09A Control-material selection | claim controls, spine controls, granularity controls, surface rules, target unit | selected control bundle, control priority map, missing-control report |
| S09B Per-unit task packet assembly | selected control bundle, evidence anchors, target unit, return format | task packet, section move plan, single-writer lock |
| S10 Main-text production | S09B task packet, construction, terminology, claim/evidence | candidate manuscript units |
| S11 Figure/caption/formal production | S08 figure contract, S04 panel evidence/result package, S01 source data locators, caption brief | figure stats, image integrity, caption brief, figure export bundle, artifacts |
| S12 Integration/consistency | candidate modules, figures, terminology, claims | integrated manuscript candidate, consistency findings |
| S13 Adversarial review | manuscript candidate, evidence, narrative, figures/export | review reports, reader surface report, rendered gate, validator report |
| S14 Backflow compilation | review findings, graph state, affected materials | narrative backflow task, repair packets, control-reselection/packet-regeneration tasks, polishing/response plans |
| S15 Repair/local regeneration | backflow task, target material, stale downstream set | revised material/text/figure, regenerated task packet when needed, updated validator report |
| S16 Export/handoff/delivery | clean final candidate from S12, review closure from S13, repair-complete package from S15, figures, repository state | export manifest, repository hygiene report, manager handoff reports |
| G01 Runtime governance | state, permissions, department metadata | skill registry, route/governance records, state controls |
| G02 Derivative/post-paper outputs | stable paper, owner request | presentation plan, patent boundary, profile-specific derivative package |

## Stage-local overlay lane

Phase 11 adds a cross-cutting overlay lane without changing the stage topology:

```text
runtime/stage_overlay_registry.json
  -> StageContract.stage_local_overlays
  -> TaskPacket.mandatory_controls.nature_overlay_*
  -> stage_overlay:nature_expert_writing:<stage_id> validator
  -> Phase10 dispatch/validation/candidate/run-state evidence
```

The active overlay is `nature_expert_writing`. It contributes Nature-style expert writing controls to existing stages, but it is not a department and cannot dispatch workers or certify completion.

Typical stage effects:

- S02: venue/article-type profile, exemplar boundary, search/SOTA expectations.
- S04: claim-strength calibration, allowed/forbidden wording, evidence visibility, data availability.
- S05-S07: reader spine, object granularity, paragraph/rhetorical/surface controls.
- S08/S11: figure contract, panel evidence, caption/legend discipline, source-data trace.
- S10/S12/S13: candidate prose, integration consistency, reviewer/editorial risk checks.
- S14/S15: local repair routing and regeneration without whole-paper rewrite.

## Key control rules

1. Subagents do not declare completion; they return candidate outputs.
2. Validators and graph commits are owned by the main-agent runtime controller.
3. Reviewers emit findings; they do not rewrite the whole paper directly.
4. Backflow is local: it targets the nearest responsible upstream node and regenerates only affected downstream outputs.
5. The bundle can be large, but it must be structured into mandatory controls, evidence/source anchors, local context, optional background, forbidden routes, validators, and return format.
6. Stage-local overlays may add controls and validators inside the existing packet boundary; they must not add a new dispatch loop or completion authority.

## 2026-06-29 strict-review stage-edge corrections

Architect/critic review converted the stage taxonomy into a less ambiguous runtime route:

```text
S03 -> S04 -> S05     # contribution options must pass the claim/evidence gate
S06 -> S08            # section/function budget is required for figure planning
S01/S04 -> S11        # source data and panel evidence must feed figure production
S09A -> S09B -> S10   # control selection is separated from per-unit packet assembly
S12/S13 -> S16        # clean candidate/review closure may export without fake repair
S14 -> S09A           # review can force control-material reselection
S15 -> S09B/S16       # repair can regenerate task packets or deliver repaired package
```

`G01` remains an inert governance sidecar: it may constrain routing and authority, but it must not inject department metadata into paper-facing cognition.
