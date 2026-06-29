# ADR-0002 — Build thin framework first, then one concrete vertical slice

## Status

Accepted.

## Context

The PPG Runtime is intended as long-term paper-production infrastructure. It can support a rich material graph, local backpropagation, validators, subagent dispatch, and future visualization. However, building the entire abstract framework first risks producing a heavy but untested architecture. Starting with arbitrary concrete materials first risks creating ad hoc schemas that do not generalize.

## Decision

Use a hybrid order:

```text
thin graph/runtime framework
  -> one concrete end-to-end vertical slice
  -> generalize only after the slice works
```

The first framework layer must be thin and stable:

- node and edge vocabulary;
- material envelope;
- status and version lifecycle;
- graph store/query;
- validator interface;
- stale propagation;
- task packet envelope;
- review finding and backflow envelope.

The first concrete vertical slice should cover one manuscript unit:

```text
OwnerIntent
  -> PaperControlSpine
  -> ClaimBoundaryMap
  -> ReviewerQuestionMap
  -> TerminologyRegister
  -> WritingTaskPacket
  -> SectionDraft
  -> ReviewFinding
  -> BackflowTask
  -> stale propagation / revised packet
```

## Non-decision

Do not design every material type before the first slice runs. Do not implement a front-end or OMX Pipeline wrapper before core graph operations and local backflow are proven.

## Consequences

Positive:

- preserves architectural coherence;
- forces concrete validation early;
- avoids overdesigning unused material families;
- gives the front-end a real graph to render later;
- keeps Codex subagent work bounded by explicit task packets.

Costs:

- some material schemas will be revised after the first slice;
- early implementation may feel incomplete;
- requires discipline not to expand into whole-paper production prematurely.

## Exit gate

This decision is satisfied when a mock or real single paragraph can complete:

```text
material inputs -> writing packet -> candidate draft -> review finding -> targeted backflow -> stale propagation -> revised packet
```

Completion requires graph validation evidence and a written trace of which nodes changed and which nodes remained untouched.
