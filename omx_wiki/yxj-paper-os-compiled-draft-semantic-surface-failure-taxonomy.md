---
title: "YXJ Paper OS Compiled Draft Semantic Surface Failure Taxonomy"
tags: ["yxj-paper-os", "s16", "compiled-draft", "semantic-surface", "failure-attribution"]
created: 2026-07-03T01:20:00Z
updated: 2026-07-03T01:20:00Z
sources: []
links: ["target-global-delivery-contract-design", "yxj-paper-os-stage-acceptance-gap-audit", "yxj-paper-os-s16-template-only-failure-evidence"]
category: architecture
confidence: high
schemaVersion: 1
---

# YXJ Paper OS Compiled Draft Semantic Surface Failure Taxonomy

## Purpose

This page records the full failure class exposed by the recent bad compiled PDF run. The issue is broader than `content_ready: blocked` or `template_only`: a compiled initial/revised draft can also be invalid when it has no paper-facing citations, no figure/table/formal evidence, internal experiment terms, unresolved manager-handoff prose, or a reader/method spine too thin for the declared target.

## Observable failure symptoms

| Symptom | Bad PDF signal | Must be blocked by |
| --- | --- | --- |
| Missing citations/references | Related Work uses generic prose with no body citation anchors; conclusion says citations should be added later | S01/S02/S04/S10/S12/S16 |
| Missing figures/tables/formal artifacts | Results are prose-only; conclusion says figures/tables should be added later | S08/S11/S12/S16 |
| Internal experiment language leakage | Terms such as `L3 unified-scene`, `controller rows`, `raw metric rows`, `project-local rows`, `registered score` appear paper-facing | S07/S09B/S10/S12/S16 |
| Unresolved-risk leakage | `Future work should add validated citations and contract-bound figures and tables` appears in paper conclusion instead of manager handoff | S12/S13/S14/S15/S16 |
| Reader/method underdevelopment | Method lacks notation/object/variable definitions; result evidence not rendered as tables/figures | S05/S06/S08/S10/S12/S13 |
| Premature export | Build/hash/PDF-header success is treated as manuscript readiness | S16 target-global delivery gate |

## Root cause

The Paper OS design already has stage contracts, validators, candidate/commit authority, and backflow. The failure occurs when those contracts are treated as generation guidance or fixture/schema checks rather than hard gates over the current paper instance. Build success is not manuscript readiness.

## Required compiled-target semantic surface contract

For `delivery_target.kind in {compiled_initial_draft, revised_compiled_pdf}`, S16 must prove all of the following with current-instance evidence:

- body citation anchors are present in the manuscript body, not only a `References` heading;
- reference entries are rendered and non-empty;
- visual/formal callouts are present when claims/results require them;
- required figure/table/formal artifacts are exported or hash-bound through the artifact checklist;
- forbidden internal terms are absent and any detected terms are listed;
- unresolved manager-risk phrases are absent from paper-facing text;
- upstream findings/stale nodes are closed or explicitly owner-gated in a target-compatible way.

## Nearest-stage failure attribution

| S16 failure class | Nearest responsible route | Downstream stale/regeneration path |
| --- | --- | --- |
| Missing body citation anchors or reference entries | S01/S02 for source/citation bank, S04 for claim-evidence map | S09B → S10 → S12 → S16 |
| Missing visual/formal callouts or artifacts | S08 visual/formal plan, S11 artifact bundle | S12 → S16 |
| Internal lexicon leakage | S07 terminology/surface control, S09B packet propagation | S10 → S12 → S16 |
| Unresolved-risk text in paper surface | S12 surface/firewall audit; S13 finding; S14/S15 repair | S12/S13 as needed → S16 |
| Source-writeback missing | S15 source-writeback repair | S12 post-writeback → S16 |
| Post-writeback validation missing | S12 post-writeback integration | S13 optional review → S16 |

## Non-goal

This does not make S16 a writing stage. S16 is a fail-closed delivery gate and failure router. If the compiled target fails, the controller must create a bounded feedback/backflow/repair path to the nearest accountable upstream material rather than rewriting the paper globally.
