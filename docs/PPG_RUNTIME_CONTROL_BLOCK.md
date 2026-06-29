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
| S04 Evidence-to-claim admissibility | evidence bank, citations, results | claim capsules, result packages, claim visibility, data availability |
| S05 Paper spine/reader questions | motivation, contribution, template, claims | reader spine, reviewer question map, rationale matrix |
| S06 Object/granularity design | spine, questions, template, claim visibility | object representation, section budget, load budget, explanation ladder |
| S07 Rhetoric/terminology/surface controls | object design, claim visibility, evidence wording | construction matrix, rhetorical matrix, terminology register, surface rules |
| S08 Visual/formal planning | spine, section budget, claims/evidence | visual budget, figure contract, aesthetic profile, panel evidence, backend route |
| S09 Main-text packet compilation | control materials, target unit | task packet, section move plan, single-writer lock |
| S10 Main-text production | task packet, construction, terminology, claim/evidence | candidate manuscript units |
| S11 Figure/caption/formal production | figure contract, panel evidence, source data, caption brief | figure stats, image integrity, caption brief, figure export bundle, artifacts |
| S12 Integration/consistency | candidate modules, figures, terminology, claims | integrated manuscript candidate, consistency findings |
| S13 Adversarial review | manuscript candidate, evidence, narrative, figures/export | review reports, reader surface report, rendered gate, validator report |
| S14 Backflow compilation | review findings, graph state, affected materials | narrative backflow task, repair packets, polishing/response plans |
| S15 Repair/local regeneration | backflow task, target material, stale downstream set | revised material/text/figure, updated validator report |
| S16 Export/handoff/delivery | final candidate, figures, review closure, repository state | export manifest, repository hygiene report, manager handoff reports |
| G01 Runtime governance | state, permissions, department metadata | skill registry, route/governance records, state controls |
| G02 Derivative/post-paper outputs | stable paper, owner request | presentation plan, patent boundary, Nature absorption package |

## Key control rules

1. Subagents do not declare completion; they return candidate outputs.
2. Validators and graph commits are owned by the main-agent runtime controller.
3. Reviewers emit findings; they do not rewrite the whole paper directly.
4. Backflow is local: it targets the nearest responsible upstream node and regenerates only affected downstream outputs.
5. The bundle can be large, but it must be structured into mandatory controls, evidence/source anchors, local context, optional background, forbidden routes, validators, and return format.
