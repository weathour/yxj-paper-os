# Plan — Paper Production Graph Runtime

## Target model

The plugin will manage paper production as a visible, versioned, locally repairable material graph:

```text
human owner <-> main Codex agent
                 |
                 v
        Paper Production Graph Runtime
                 |
                 +-> material nodes
                 +-> transform tasks
                 +-> validator nodes
                 +-> review findings
                 +-> backflow tasks
                 +-> manuscript artifacts
```

The main agent owns process control. Subagents and scripts operate only on explicit task packets.

## Why this replaces the route model

The upstream route model failed because it encouraged hidden self-loops:

```text
route -> internal analysis -> internal review -> route claims progress
```

The new model uses explicit graph state:

```text
material -> task -> candidate output -> validator -> committed/stale/backflow
```

Completion is never inferred from agent activity. Completion requires a graph state transition backed by artifacts and validators.

## Development phases

### Phase 1 — Graph topology

Deliverables:

- node type list;
- edge type list;
- graph layering;
- status vocabulary;
- versioning rules;
- graph invariants;
- minimal example graph.

Exit gate:

- `examples/minimal-paper-production-graph.json` passes structural validation.

### Phase 2 — Front-end visualization contract

Deliverables:

- graph JSON contract suitable for React Flow / Cytoscape / D3;
- node color/status rules;
- edge style rules;
- selected-node inspector contract;
- backflow trace view contract;
- writing progress view contract.

Exit gate:

- every node/edge in the minimal example has enough fields to render and inspect.

### Phase 3 — Material data model

Deliverables:

- shared material envelope;
- typed payload families;
- version and stale policy;
- validator binding;
- provenance fields;
- artifact storage conventions.

Exit gate:

- core paper materials can be represented without relying on prose-only prompt state.

### Phase 4 — Material generation methods

Classify every graph transition as one of:

- `agent_generated` — semantic work by bounded specialist agent;
- `script_generated` — deterministic transform or scan;
- `hybrid_generated` — LLM candidate plus schema/script validation;
- `manual_owner_decision` — human semantic authority required.

Exit gate:

- each core material has a declared generation method and validator.

### Phase 5 — Main-agent runtime protocol

Deliverables:

- graph observation protocol;
- frontier queue;
- task packet compiler;
- context bundle format;
- dispatch policy;
- commit protocol;
- stale propagation policy.

Exit gate:

- main agent can explain why a node is next and what evidence would close it.

### Phase 6 — Closed-loop tests

Deliverables:

- graph structural tests;
- single-node generation fixtures;
- local backflow fixtures;
- small mock-paper closed loop;
- real-paper single-section pilot.

Exit gate:

- a review finding can invalidate one upstream material, regenerate affected downstream nodes, and avoid rewriting unrelated sections.

### Phase 7 — Human handoff and advanced front-end

Only after the graph/runtime loop is validated, design:

- owner decision queues;
- human review panels;
- graph interaction controls;
- approval UX;
- diff views;
- multi-paper dashboards.

## Non-goals for this planning/design phase

These are phase-local boundaries, not permanent bans on an owner-authorized plugin replacement workflow.

- unapproved live install or marketplace publication outside the controller-owned replacement workflow;
- activation or mutation of the unauthorized recursive route;
- full front-end app implementation;
- whole-paper autonomous generation;
- external submission/upload;
- private library ingestion.

