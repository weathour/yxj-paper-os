# Paper OS Architecture Overview

`yxj-paper-os` is a standalone Paper Production Graph runtime. Its architecture is intentionally small:

```text
material authority
  -> stage accountability
  -> bounded task packets
  -> candidate returns
  -> validation and commit/reject
  -> local backflow for failures
  -> retrospective stage improvement after a full run
```

## Accepted invariants

1. **The graph is the authority surface.** A manuscript node is not complete until the graph records candidate output, validator evidence, committed state, and downstream stale/backflow status.
2. **The main agent is the controller.** Workers and scripts return candidates or evidence; they cannot dispatch other workers, commit graph state, or claim paper completion.
3. **Task packets are the write boundary.** Each worker receives a bounded `TaskPacket` with explicit input materials, allowed actions, allowed paths, validators, return format, and `completion_forbidden=true`.
4. **Feedback is routed before repair.** A user/reviewer finding first becomes a `ReviewFeedbackPackage`, then a `FailureAttributionRecord` naming the nearest accountable stage/material. Only then may the controller create a scoped repair/backflow packet.
5. **System learning is post-run.** `StageImprovementRecord` objects are proposals derived from repeated failures and a run retrospective. They do not mutate the current paper directly.
6. **Submission remains owner-gated.** Export, upload, submission, acceptance, and final-publication claims are never inferred from validator success.

## Boundary between current-paper repair and system learning

Current-paper repair answers: “Which material or candidate is wrong in this paper, and what bounded artifact may be regenerated?”

System learning answers: “Which stage prompt, packet clause, validator, or material template repeatedly caused failures across the run and should be improved for future runs?”

The controller may perform the first during a run. The second requires retrospective evidence and should be committed only as an explicit plugin/runtime improvement.

## Why historical phase fixtures remain internally

Some script and fixture filenames still contain `phase*` because they are tested compatibility wrappers from earlier development milestones. They are not public routes and do not define the product model. Public operation should use:

- canonical stages `S00-S16/G01/G02`;
- `readiness-dry-run` for safe pre-dispatch run assembly;
- `formal-full-flow-runtime-test` for deterministic full-flow fixture evidence;
- `live-subagent-pilot` for recorded producer/verifier lane evidence.

## Trade-offs

- **Explicit graph over flat drafts:** more structure, less chance of silent overclaim or lost provenance.
- **Local repair over whole-paper rewrite:** slower for broad failures, safer for preserving valid materials and owner intent.
- **Standalone validators over host tooling:** less marketplace coverage, but reproducible across checkouts and not tied to one user's machine.
- **Retrospective improvements over live prompt mutation:** fewer hidden changes during a paper run, better auditability after the run.
