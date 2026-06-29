# Stage Coverage Audit — Are 17 Rings Too Many or Missing Anything?

This audit reviews the dispatchable PPG Runtime stages (`S00`-`S16`, with `S09` split into `S09A/S09B`) plus sidecar governance stages. It asks:

1. Are there too many stages?
2. Are some stages duplicates?
3. Are any major paper-production responsibilities missing?
4. What stage set should be used for MVP versus full runtime?

## Executive answer

The 17-logical-stage taxonomy is not too many as a **full long-term paper-production runtime taxonomy**. Materializing S09 as S09A/S09B yields one extra dispatch node, and the whole set is too many as a **default execution chain**.

Use three levels:

```text
MVP chain: 10 logical responsibilities / 11 dispatch nodes after S09 split
Standard full paper route: stage-selected path with S03 optional and S09 split explicit
Full runtime taxonomy: 17 logical stages / 18 dispatch nodes + sidecars
```

The 17 logical stages cover the full paper-production lifecycle well. The main missing item is not another stage, but a cross-cutting mechanism: **versioned graph state and dependency/stale propagation**. That belongs to the runtime core, not to a subagent stage.

## Coverage against paper lifecycle

| Lifecycle need | Covered by stages | Status |
| --- | --- | --- |
| Human need / owner authority | S00 | covered |
| Source/citation/evidence intake | S01 | covered |
| Field scene / SOTA / template analysis | S02 | covered |
| Novelty and contribution exploration | S03 | covered, optional |
| Claim/evidence admissibility | S04 | covered |
| Paper spine / reader questions | S05 | covered |
| Object representation / granularity | S06 | covered |
| Rhetoric / terminology / surface controls | S07 | covered |
| Figure/table/algorithm/formula planning | S08 | covered |
| Control-material selection | S09A | covered |
| Per-unit task packet compilation | S09B | covered |
| Main-text drafting | S10 | covered |
| Figure/caption/formal artifact production | S11 | covered |
| Integration / cross-section consistency | S12 | covered |
| Adversarial review / validation loss | S13 | covered |
| Backflow compilation | S14 | covered |
| Repair and local regeneration | S15 | covered |
| Export / handoff / delivery hygiene | S16 | covered |
| Runtime governance | G01 | sidecar covered |
| Post-paper derivative outputs | G02 | sidecar covered |
| Graph versioning / stale propagation | runtime core | covered by protocol, not a stage |
| Human handoff UX | later owner-interface layer | not in stage chain yet |

## Redundancy / merge analysis

### S02 and S03

- `S02` understands the field/template/SOTA.
- `S03` explores novelty/contribution options.

They are related but should not always merge. Novelty exploration is optional or activated when the contribution is not stable.

Recommendation:

- MVP: skip or fold S03 into S05.
- Full runtime: keep S03 as optional branch.

### S05, S06, S07

These three are tightly related:

- `S05`: paper spine and reviewer-question synthesis;
- `S06`: object representation and granularity;
- `S07`: rhetoric, terminology, and surface controls.

They can be merged for small tasks, but should remain distinct in the taxonomy because they control different failure modes:

| Failure | Needed stage |
| --- | --- |
| core story unclear | S05 |
| object repeated at wrong granularity | S06 |
| paragraph move/terminology/surface leaks | S07 |

Recommendation:

- MVP: combine S05-S07 into one `Reader-Control Bundle` stage.
- Full runtime: keep separated.

### S08 and S11

- `S08` plans visual/formal artifacts.
- `S11` produces them.

Do not merge for final/export-facing figures. Planning and production must remain separate because figures carry claims and evidence.

Recommendation:

- MVP if no figures: skip both.
- MVP with one figure: keep both but use minimal contracts.

### S13, S14, S15

- `S13`: detect loss/finding;
- `S14`: convert finding to repair task;
- `S15`: execute repair and regenerate.

Do not merge in the full runtime. The separation prevents reviewers from rewriting uncontrolled text.

Recommendation:

- MVP: may implement as one scripted/reasoned loop but keep separate records.
- Full runtime: keep separated.

## Missing or under-specified items

### M1 — Graph state/version/stale propagation is cross-cutting

Not a subagent stage. It must exist as runtime infrastructure:

```text
MaterialNode versions
Edge dependencies
Commit protocol
Stale propagation
Supersedes edges
Impact scope
```

Action: keep this in graph core, not the stage list.

### M2 — Human handoff / decision UX is not a stage yet

`S00` handles owner authority, but there is no explicit later-stage owner handoff/approval interface.

This should be a cross-cutting interface layer, not a paper-production stage:

- owner decision queue;
- options and consequences;
- approval/diff view;
- semantic decision record;
- interruption/resume.

Action: add later as `Owner Interface Layer`, not in current stage chain.

### M3 — Quality/cost scheduling policy is not a stage

The runtime still needs a policy deciding when to run heavy stages:

- skip S03 if contribution stable;
- skip S08/S11 if no figure touched;
- skip S16 until export/handoff;
- run S13 lightly for section draft and heavily for full manuscript.

Action: add a `Stage Activation Policy` document.

### M4 — Data/code experiment validation may need a specialized substage in empirical papers

Current S01/S04/S12/S13 cover evidence and validation, but empirical papers may need an explicit code/experiment validation ring:

```text
ExperimentReproCheck
MetricConsistencyCheck
AblationBaselineCheck
FigureDataTraceCheck
```

This can be a profile-specific expansion of S04/S13, not a universal stage.

Action: record as optional profile stage `S04E` for empirical/computational papers.

### M5 — Citation style and bibliography rendering is split across S01/S02/S16

This is acceptable. It does not need a new stage unless citation-heavy literature reviews become a target profile.

## Recommended stage sets

### MVP chain: 10 logical responsibilities / 11 dispatch nodes

Use this for the first runnable slice:

```text
S00 Owner semantic contract
S01 Source/citation/evidence inventory
S04 Evidence-to-claim admissibility
S05 Paper spine and reader-question synthesis
S07 Rhetoric, terminology, and surface-control synthesis
S09A Control-material selection
S09B Per-unit task packet assembly
S10 Main-text production
S13 Adversarial manuscript review
S14 Backflow compilation and repair planning
S15 Repair execution and local regeneration
```

This proves:

```text
human need -> evidence-bound writing -> review loss -> local backflow
```

### Standard full paper route

Use for normal full manuscript production:

```text
S00 -> S01 -> S02 -> S04 -> S05 -> S06 -> S07 -> S08 -> S09A -> S09B -> S10 -> S11 -> S12 -> S13 -> S14/S15 loop -> S16
```

S03 is optional if novelty/contribution is unstable.

### Full runtime taxonomy: 17 logical stages / 18 dispatch nodes + sidecars

Keep all logical stages as the classification system:

```text
S00-S16, with S09 materialized as S09A/S09B, plus G01 + G02
```

Use only activated stages per project state.

## Stage activation policy draft

| Condition | Activate |
| --- | --- |
| owner motivation/venue/claim scope unclear | S00 |
| source/evidence unknown or stale | S01 |
| field/template/SOTA uncertain | S02 |
| contribution unstable or weak | S03 |
| claim-bearing writing planned | S04 |
| new section or major rewrite planned | S05-S07 |
| figure/table/algorithm/formula touched | S08/S11 |
| writing execution needed | S09A/S09B/S10 |
| multiple modules integrated | S12 |
| candidate manuscript/module exists | S13 |
| review finding exists | S14/S15 |
| handoff/export requested | S16 |
| automation/permissions/state changes needed | G01 |
| presentation/patent/Nature absorption requested | G02 |

## Final judgment

The 17 stages are complete enough for the full lifecycle. They should not be executed linearly by default. The runtime should treat them as a **stage library** and select a minimal active path from the graph state.

In other words:

```text
17 stages = taxonomy
active stage path = project-specific execution route
```
