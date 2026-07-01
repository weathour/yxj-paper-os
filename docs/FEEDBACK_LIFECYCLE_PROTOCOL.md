# Feedback Lifecycle Protocol

This protocol is the quality-control layer of yxj-paper-os. It turns review or user feedback into accountable graph operations instead of uncontrolled manuscript rewrites.

## Core idea

A good first integrated manuscript should emerge from good upstream materials:

```text
S00-S08 control materials
  -> S09A/S09B bounded task packets
  -> S10/S11 candidate text and artifacts
  -> S12 integrated candidate
```

When S12/S13 or a human reviewer finds a problem, the default assumption is not that the whole paper should be rewritten. The default assumption is that a responsible upstream material, task packet, or candidate output did not meet its stage contract.

```text
feedback
  -> ReviewFeedbackPackage
  -> FailureAttributionRecord
  -> RepairTaskPacket / BackflowTask
  -> scoped stale propagation
  -> local regeneration
  -> validation
  -> optional RunRetrospectiveReport
  -> optional StageImprovementRecord
```

## Lifecycle objects

### ReviewFeedbackPackage

Normalizes human feedback, reviewer comments, S13 findings, rendered-surface failures, or validator findings before any repair is attempted.

It records what was observed. It does **not** authorize edits.

Minimum responsibilities:

- identify the feedback source;
- describe the observed problem;
- name the affected artifact or material;
- list candidate failure types;
- remain neutral about repair until attribution is complete.

### FailureAttributionRecord

Maps a feedback package to the nearest responsible stage and material.

Minimum responsibilities:

- choose `nearest_stage` from the canonical stage registry;
- name the responsible material or candidate artifact;
- classify the failure level;
- state whether an owner gate is required;
- define repair and preserve scopes;
- list forbidden repair routes;
- list downstream stale targets.

A high-quality attribution distinguishes these cases:

| Symptom | Likely stage/material target |
| --- | --- |
| overstrong claim | `S04` / `ClaimBoundaryMap` |
| weak paper argument | `S05` / `PaperSpine` |
| unclear mechanism or object | `S06` / object representation material |
| inconsistent terms or tone | `S07` / `TerminologyRegister` or surface controls |
| figure does not support the text | `S08` / figure contract, then `S11` artifact |
| candidate ignores constraints | `S09B` task packet or `S10/S11` candidate return |
| cross-section contradiction | `S12` integration report |
| route, venue, or contribution change | `S00` owner-gated decision |

### RepairTaskPacket

A bounded current-paper repair contract. It wraps or points to strict `TaskPacket`/`BackflowTask` mechanisms; it does not replace them.

Minimum responsibilities:

- name the target material;
- state what must change;
- state what must be preserved;
- prohibit whole-paper rewrite unless owner-gated;
- preserve TaskPacket authority rules: no completion authority, no recursive orchestration, scoped write paths, and no owner-intent changes.

### RunRetrospectiveReport

Summarizes a completed paper run after review/repair cycles. It is for system learning, not direct manuscript editing.

Minimum responsibilities:

- collect feedback packages and repair outcomes;
- identify recurring stage-level failure patterns;
- separate current-paper fixes from future Paper OS improvements;
- list blocked improvements that require owner decision or later design work.

### StageImprovementRecord

A proposed upgrade to a stage prompt, material template, task-packet clause, or validator. It should normally be produced from repeated evidence, not from one ordinary typo or style preference.

Minimum responsibilities:

- identify the stage;
- summarize the failure pattern and evidence count;
- name the root cause;
- propose prompt, task-packet, and validator changes;
- require a regression test when the system behavior changes.

## Current-paper repair vs system learning

| Layer | Trigger | Output | Authority |
| --- | --- | --- | --- |
| Current-paper repair | one validated feedback item | `RepairTaskPacket` / `BackflowTask` | repairs scoped paper materials |
| System learning | recurring failures or full-run retrospective | `StageImprovementRecord` | proposes changes to Paper OS prompts/templates/validators |

Do not edit stage prompts or task-packet templates just because a single local sentence is weak. First repair the paper locally; later aggregate patterns.

## Forbidden shortcuts

- Do not rewrite the whole paper because a local finding exists.
- Do not mark a worker candidate as committed.
- Do not skip failure attribution.
- Do not treat a generated PDF or successful LaTeX build as S12 integration proof.
- Do not let retrospective records claim submission, publication, or final acceptance readiness.
- Do not turn optional OMX orchestration into a yxj-paper-os dependency.

## Validation

The executable contract is checked by:

```bash
python3 scripts/verify_lifecycle_contract.py
```

The positive fixture proves the full path from feedback to stage improvement. Negative fixtures reject unrouted feedback, global rewrite repairs, recursive authority, premature system improvement, submission-readiness claims, and active OMX dependency claims.
