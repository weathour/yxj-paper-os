#!/usr/bin/env python3
"""Dependency-free structural validator for PPG graph JSON examples."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_NODE_TYPES = {
    "owner_intent",
    "material",
    "transform_task",
    "agent_run",
    "validator",
    "validation_report",
    "manuscript_artifact",
    "review_finding",
    "backflow_task",
}
ALLOWED_STATUSES = {
    "planned",
    "candidate",
    "validated",
    "committed",
    "stale",
    "rejected",
    "blocked",
    "owner_gated",
}
ALLOWED_EDGE_TYPES = {
    "consumes",
    "constrains",
    "produces",
    "validates",
    "reports",
    "invalidates",
    "repairs",
    "supersedes",
    "references",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"cannot read JSON: {exc}"]

    if graph.get("schema_version") != "ppg-graph/v0.1":
        fail(errors, "schema_version must be ppg-graph/v0.1")
    if not graph.get("graph_id"):
        fail(errors, "graph_id is required")

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list):
        fail(errors, "nodes must be a list")
        nodes = []
    if not isinstance(edges, list):
        fail(errors, "edges must be a list")
        edges = []

    node_ids: set[str] = set()
    for i, node in enumerate(nodes):
        prefix = f"nodes[{i}]"
        node_id = node.get("id")
        if not node_id:
            fail(errors, f"{prefix}.id is required")
            continue
        if node_id in node_ids:
            fail(errors, f"duplicate node id: {node_id}")
        node_ids.add(node_id)
        if node.get("node_type") not in ALLOWED_NODE_TYPES:
            fail(errors, f"{prefix}.node_type invalid: {node.get('node_type')}")
        if node.get("status") not in ALLOWED_STATUSES:
            fail(errors, f"{prefix}.status invalid: {node.get('status')}")
        if not node.get("label"):
            fail(errors, f"{prefix}.label is required")
        if node.get("status") == "stale" and not node.get("stale_reason"):
            fail(errors, f"{prefix} is stale but stale_reason is missing")

    edge_ids: set[str] = set()
    incoming_by_type: dict[tuple[str, str], int] = {}
    for i, edge in enumerate(edges):
        prefix = f"edges[{i}]"
        edge_id = edge.get("id")
        if not edge_id:
            fail(errors, f"{prefix}.id is required")
            continue
        if edge_id in edge_ids:
            fail(errors, f"duplicate edge id: {edge_id}")
        edge_ids.add(edge_id)
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_ids:
            fail(errors, f"{prefix}.source does not exist: {source}")
        if target not in node_ids:
            fail(errors, f"{prefix}.target does not exist: {target}")
        edge_type = edge.get("edge_type")
        if edge_type not in ALLOWED_EDGE_TYPES:
            fail(errors, f"{prefix}.edge_type invalid: {edge_type}")
        if target and edge_type:
            incoming_by_type[(target, edge_type)] = incoming_by_type.get((target, edge_type), 0) + 1

    for node in nodes:
        node_id = node.get("id")
        node_type = node.get("node_type")
        status = node.get("status")
        if status == "committed" and node_type != "owner_intent":
            has_input = any(
                incoming_by_type.get((node_id, t), 0) > 0
                for t in ("consumes", "constrains", "produces", "references")
            )
            if not has_input:
                fail(errors, f"committed node has no provenance/input edge: {node_id}")
        if node_type == "manuscript_artifact":
            has_task = incoming_by_type.get((node_id, "produces"), 0) > 0
            if not has_task:
                fail(errors, f"manuscript artifact has no producing task: {node_id}")
        if node_type == "review_finding":
            has_report = incoming_by_type.get((node_id, "reports"), 0) > 0
            if not has_report:
                fail(errors, f"review finding has no reporting validator/reviewer: {node_id}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_graph.py <graph.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    errors = validate(path)
    if errors:
        print(f"INVALID {path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
