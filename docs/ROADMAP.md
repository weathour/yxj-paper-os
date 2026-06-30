# Roadmap


## Current promotion status

- [x] Phase 12 deterministic formal full-flow runtime-test harness.
- [x] Phase 13 live native-subagent full-flow pilot: 20 producer lanes + 20 independent verifier lanes, run-owned evidence, source-read-only snapshots, and exact-code negative probes.
- [x] Post-Phase13 main-agent lane policy: canonical stages now encode whether they are mandatory double-subagent, conditional double-subagent, or single-lane with deterministic validation.

## M0 — Repository and documentation spine

- [x] create isolated repository;
- [x] scaffold Codex plugin metadata;
- [x] document graph runtime plan;
- [x] create minimal graph schema and example;
- [x] add dependency-free graph validator.

## M1 — Graph topology MVP

- [ ] finalize node and edge vocabularies;
- [ ] finalize status transition table;
- [ ] define active-version pointer policy;
- [ ] define graph state file layout;
- [ ] add more fixtures for stale propagation.

## M2 — Visualization MVP

- [ ] choose rendering stack;
- [ ] implement read-only graph viewer;
- [ ] implement node inspector;
- [ ] implement backflow trace panel;
- [ ] implement writing progress panel.

## M3 — Material schema MVP

- [ ] implement material envelope schema;
- [ ] implement core typed payload schemas;
- [ ] add material validators;
- [ ] define artifact directory conventions.

## M4 — Runtime MVP

- [ ] implement graph state loader;
- [ ] implement frontier selector;
- [x] implement deterministic strict task packet compiler for the Phase 6 intro-writing and claim-repair targets;
- [ ] implement commit protocol;
- [x] implement scoped stale propagation dry-run.

## M5 — Closed-loop test

- [ ] build mock paper graph;
- [ ] run one forward pass;
- [ ] inject review finding;
- [ ] run local backflow;
- [ ] regenerate affected node only.

## M6 — Human handoff and front-end upgrade

- [ ] design owner decision queue;
- [ ] design approval UX;
- [ ] design diff/trace view;
- [ ] design multi-paper dashboard.
