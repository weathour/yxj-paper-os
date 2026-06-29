#!/usr/bin/env python3
"""Dependency-free structural validator for PPG graph JSON examples."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_NODE_TYPES = {
    "owner_intent",
    "owner_decision",
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
PROVENANCE_EDGE_TYPES = ("consumes", "constrains", "produces", "references")
ACTIVE_STATUSES = {"committed"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _relative_to_repo(path_text: str) -> Path:
    return Path(path_text)


def _requires_runtime_artifact_check(path_text: str) -> bool:
    """Only runtime fixture artifact handles are forced to exist.

    Legacy examples intentionally use paths such as ``materials/foo.yaml`` that
    are documentation handles, not repo-root fixture paths. Stricter artifact
    existence checks apply to current runtime fixture folders under examples/.
    """

    path = _relative_to_repo(path_text)
    parts = path.parts
    return len(parts) >= 2 and parts[0] == "examples" and parts[1] in {"materials", "owner-decisions", "validator-reports"}


def _validate_owner_decision_artifact(node: dict[str, Any], errors: list[str], prefix: str) -> None:
    artifact_path = node.get("artifact_path")
    if not artifact_path:
        fail(errors, f"{prefix}.artifact_path is required for owner_decision")
        return
    artifact = _relative_to_repo(str(artifact_path))
    if not artifact.exists():
        fail(errors, f"{prefix}.artifact_path does not exist: {artifact_path}")
        return
    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"{prefix}.artifact_path is not valid owner decision JSON: {exc}")
        return

    required = ["schema_version", "decision_id", "status", "question", "why_owner_gated", "blocks", "options", "created_at"]
    for key in required:
        if key not in payload:
            fail(errors, f"{prefix}.owner_decision missing required field: {key}")
    if payload.get("schema_version") != "ppg-owner-decision/v0.1":
        fail(errors, f"{prefix}.owner_decision schema_version must be ppg-owner-decision/v0.1")
    if payload.get("decision_id") != node.get("id"):
        fail(errors, f"{prefix}.owner_decision decision_id must match node id")
    if payload.get("status") not in {"queued", "answered", "deferred"}:
        fail(errors, f"{prefix}.owner_decision status invalid: {payload.get('status')}")
    if not isinstance(payload.get("blocks"), list):
        fail(errors, f"{prefix}.owner_decision blocks must be a list")
    options = payload.get("options")
    if not isinstance(options, list) or not options:
        fail(errors, f"{prefix}.owner_decision options must be a non-empty list")


def _node_label(node: dict[str, Any]) -> str:
    return f"{node.get('id')} ({node.get('node_type')}, {node.get('status')})"


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
    active_versions = graph.get("active_versions", {})
    has_active_versions = "active_versions" in graph

    if not isinstance(nodes, list):
        fail(errors, "nodes must be a list")
        nodes = []
    if not isinstance(edges, list):
        fail(errors, "edges must be a list")
        edges = []
    if not isinstance(active_versions, dict):
        fail(errors, "active_versions must be an object when present")
        active_versions = {}

    node_ids: set[str] = set()
    nodes_by_id: dict[str, dict[str, Any]] = {}
    material_versions: dict[tuple[str, str], str] = {}
    material_nodes_by_id: dict[str, list[str]] = {}

    for i, node in enumerate(nodes):
        prefix = f"nodes[{i}]"
        if not isinstance(node, dict):
            fail(errors, f"{prefix} must be an object")
            continue
        node_id = node.get("id")
        if not node_id:
            fail(errors, f"{prefix}.id is required")
            continue
        if node_id in node_ids:
            fail(errors, f"duplicate node id: {node_id}")
        node_ids.add(node_id)
        nodes_by_id[node_id] = node

        node_type = node.get("node_type")
        status = node.get("status")
        if node_type not in ALLOWED_NODE_TYPES:
            fail(errors, f"{prefix}.node_type invalid: {node_type}")
        if status not in ALLOWED_STATUSES:
            fail(errors, f"{prefix}.status invalid: {status}")
        if not node.get("label"):
            fail(errors, f"{prefix}.label is required")
        if status == "stale" and not node.get("stale_reason"):
            fail(errors, f"{prefix} is stale but stale_reason is missing")

        if node_type == "material":
            material_id = node.get("material_id")
            version = node.get("version")
            if has_active_versions and not material_id:
                fail(errors, f"{prefix}.material_id is required when active_versions is present")
            if material_id:
                material_nodes_by_id.setdefault(material_id, []).append(node_id)
            if material_id and version:
                key = (material_id, version)
                previous = material_versions.get(key)
                if previous and previous != node_id:
                    fail(errors, f"duplicate material version for {material_id}@{version}: {previous}, {node_id}")
                material_versions[key] = node_id

            artifact_path = node.get("artifact_path")
            if artifact_path and _requires_runtime_artifact_check(str(artifact_path)):
                artifact = _relative_to_repo(str(artifact_path))
                if not artifact.exists():
                    fail(errors, f"{prefix}.artifact_path does not exist: {artifact_path}")

        if node_type == "owner_decision":
            _validate_owner_decision_artifact(node, errors, prefix)

    edge_ids: set[str] = set()
    incoming_by_type: dict[tuple[str, str], int] = {}
    supersedes_edges_by_source: dict[str, set[str]] = {}

    for i, edge in enumerate(edges):
        prefix = f"edges[{i}]"
        if not isinstance(edge, dict):
            fail(errors, f"{prefix} must be an object")
            continue
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

        if edge_type == "supersedes" and source in nodes_by_id and target in nodes_by_id:
            source_node = nodes_by_id[source]
            target_node = nodes_by_id[target]
            supersedes_edges_by_source.setdefault(source, set()).add(target)
            if source_node.get("node_type") != "material" or target_node.get("node_type") != "material":
                fail(errors, f"{prefix}.supersedes must connect material nodes new_version -> old_version")
            elif source_node.get("material_id") != target_node.get("material_id"):
                fail(errors, f"{prefix}.supersedes material_id mismatch: {source} -> {target}")
            elif source_node.get("supersedes") != target:
                fail(errors, f"{prefix}.supersedes direction invalid: source {source} must declare supersedes={target}")
            if target_node.get("supersedes") == source:
                fail(errors, f"{prefix}.supersedes appears reversed: target {target} declares supersedes={source}")

    for node in nodes:
        node_id = node.get("id")
        node_type = node.get("node_type")
        status = node.get("status")
        if status == "committed" and node_type != "owner_intent":
            has_input = any(
                incoming_by_type.get((node_id, t), 0) > 0
                for t in PROVENANCE_EDGE_TYPES
            )
            if not has_input:
                fail(errors, f"committed node has no provenance/input edge: {node_id}")
        if node_type == "manuscript_artifact":
            has_task = incoming_by_type.get((node_id, "produces"), 0) > 0
            is_missing_task_placeholder = status == "planned" and node.get("needs_task_packet") is True
            if not has_task and not is_missing_task_placeholder:
                fail(errors, f"manuscript artifact has no producing task: {node_id}")
        if node_type == "review_finding":
            has_report = incoming_by_type.get((node_id, "reports"), 0) > 0
            if not has_report:
                fail(errors, f"review finding has no reporting validator/reviewer: {node_id}")

        if node_type == "material" and node.get("supersedes"):
            superseded_id = node.get("supersedes")
            superseded = nodes_by_id.get(superseded_id)
            if not superseded:
                fail(errors, f"material node {node_id}.supersedes does not exist: {superseded_id}")
            elif superseded.get("node_type") != "material":
                fail(errors, f"material node {node_id}.supersedes target is not material: {superseded_id}")
            elif node.get("material_id") != superseded.get("material_id"):
                fail(errors, f"material node {node_id}.supersedes material_id mismatch: {superseded_id}")
            edge_targets = supersedes_edges_by_source.get(node_id, set())
            if edge_targets and superseded_id not in edge_targets:
                fail(errors, f"material node {node_id}.supersedes disagrees with supersedes edge")

    for material_id, active_node_id in active_versions.items():
        if not isinstance(material_id, str) or not material_id:
            fail(errors, "active_versions keys must be non-empty material ids")
            continue
        if not isinstance(active_node_id, str) or not active_node_id:
            fail(errors, f"active_versions[{material_id}] must be a non-empty node id")
            continue
        active_node = nodes_by_id.get(active_node_id)
        if not active_node:
            fail(errors, f"active_versions[{material_id}] target does not exist: {active_node_id}")
            continue
        if active_node.get("node_type") != "material":
            fail(errors, f"active_versions[{material_id}] target is not a material: {_node_label(active_node)}")
            continue
        if active_node.get("material_id") != material_id:
            fail(errors, f"active_versions[{material_id}] material_id mismatch: {active_node_id} has {active_node.get('material_id')}")
        if active_node.get("status") not in ACTIVE_STATUSES:
            fail(errors, f"active_versions[{material_id}] target must be committed, got {_node_label(active_node)}")
        if active_node.get("candidate_for"):
            fail(errors, f"active_versions[{material_id}] target is a candidate: {active_node_id}")

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
