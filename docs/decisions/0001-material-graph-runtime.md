# ADR-0001 — Replace department self-loops with material graph runtime

## Status

Accepted for plugin design.

## Context

The previous yxj-paper-os department model separated paper work into departments and attempted to let each department run internal loops. This caused hidden coordination, context overload, weak execution precision, and difficult debugging under Codex's main-agent/subagent runtime.

Codex is stronger when tasks are explicit, bounded, validated, and committed by the main agent after evidence collection.

## Decision

Use **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**.

Departments may remain as metadata labels, but runtime control is graph-based:

- material nodes;
- transform tasks;
- validator nodes;
- manuscript artifacts;
- review findings;
- backflow tasks;
- versioned replacements.

The main agent is the graph runtime controller. Subagents operate on task packets and return candidates only.

## Consequences

Positive:

- visible dependencies;
- scoped repair;
- front-end inspectability;
- stronger validation;
- better Codex fit;
- easier debugging.

Costs:

- more explicit schemas;
- graph state maintenance;
- validators required before claims of completion;
- initial front-end contract needed early.

