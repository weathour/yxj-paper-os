# Visualization Contract

## Purpose

The front end is not decoration. It is the operator view for the paper production graph. It must let the owner and main agent see material flow, dependency strength, validation state, and backflow impact.

## Minimum viable view

### 1. Graph canvas

Render nodes and edges from `ppg-graph` JSON.

Required visual encodings:

| Status | Node color intent |
| --- | --- |
| `planned` | gray outline |
| `candidate` | blue outline |
| `validated` | green outline |
| `committed` | solid green |
| `stale` | orange |
| `rejected` | red |
| `blocked` | red with blocker icon |
| `owner_gated` | yellow with lock icon |

Edge encodings:

| Edge type | Style |
| --- | --- |
| `consumes` | solid black |
| `constrains` | solid purple |
| `produces` | solid blue |
| `validates` | dashed blue |
| `invalidates` | dashed red |
| `repairs` | solid red arrow |
| `supersedes` | gray version link |
| `references` | dotted gray |

### 2. Node inspector

Selecting a node must show:

- id, type, version, status;
- summary;
- artifact path;
- upstream dependencies;
- downstream consumers;
- validators and latest reports;
- invalidation policy;
- owner gate status;
- latest task packet or agent run provenance.

### 3. Backflow trace view

Selecting a review finding must show:

```text
finding -> suspected source node -> backflow task -> new version -> stale downstream nodes
```

This view is mandatory because local backpropagation is the core management mode.

### 4. Writing progress view

For manuscript artifacts, show:

- section/unit;
- writing task packet status;
- control materials consumed;
- validation status;
- stale reason if invalidated;
- reviewer findings linked to this unit.

## Front-end data requirements

Every graph file must include:

```json
{
  "graph_id": "...",
  "schema_version": "ppg-graph/v0.1",
  "nodes": [],
  "edges": []
}
```

Nodes must have stable ids. Edge endpoints must refer to existing node ids. Versions are encoded on nodes, not by mutating ids alone.

## Non-goals for MVP

- interactive editing;
- drag-and-drop task dispatch;
- real-time multi-agent telemetry;
- live Codex control;
- authentication;
- remote persistence.

First front end should be read-only.

