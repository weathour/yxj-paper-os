#!/usr/bin/env python3
"""Small dependency-free store/inspection CLI for PPG runtime graph fixtures."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

try:
    from validate_graph import validate
except ImportError:  # pragma: no cover - script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate_graph import validate  # type: ignore  # noqa: E402


class GraphStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.graph = json.loads(path.read_text(encoding="utf-8"))
        self.nodes: list[dict[str, Any]] = self.graph.get("nodes", [])
        self.edges: list[dict[str, Any]] = self.graph.get("edges", [])
        self.nodes_by_id: dict[str, dict[str, Any]] = {
            node["id"]: node for node in self.nodes if isinstance(node, dict) and node.get("id")
        }
        self.active_versions: dict[str, str] = self.graph.get("active_versions", {}) or {}

    def material_nodes(self, material_id: str) -> list[dict[str, Any]]:
        return [node for node in self.nodes if node.get("node_type") == "material" and node.get("material_id") == material_id]

    def resolve_material(self, query: str) -> tuple[str, dict[str, Any], str]:
        """Resolve a logical material id or exact material node id.

        Logical material ids resolve to their active committed version. Concrete
        node ids resolve to that exact node so historical/stale versions remain
        directly addressable.
        """

        if query in self.active_versions:
            node_id = self.active_versions[query]
            node = self.nodes_by_id.get(node_id)
            if not node:
                raise KeyError(f"active material {query} points to missing node {node_id}")
            return query, node, "logical_material_id"

        node = self.nodes_by_id.get(query)
        if node:
            if node.get("node_type") != "material":
                raise KeyError(f"node is not a material: {query}")
            material_id = node.get("material_id") or query
            return material_id, node, "concrete_node_id"

        matches = self.material_nodes(query)
        if matches:
            active_id = self.active_versions.get(query)
            if active_id and active_id in self.nodes_by_id:
                return query, self.nodes_by_id[active_id], "logical_material_id"
            committed = [node for node in matches if node.get("status") == "committed"]
            if len(committed) == 1:
                return query, committed[0], "logical_material_id"

        raise KeyError(f"cannot resolve material or node: {query}")

    def upstream_edges(self, node_id: str) -> list[dict[str, Any]]:
        return sorted((edge for edge in self.edges if edge.get("target") == node_id), key=lambda e: e.get("id", ""))

    def downstream_edges(self, node_id: str) -> list[dict[str, Any]]:
        return sorted((edge for edge in self.edges if edge.get("source") == node_id), key=lambda e: e.get("id", ""))

    def material_history(self, material_id: str) -> list[dict[str, Any]]:
        return sorted(self.material_nodes(material_id), key=lambda n: (str(n.get("version", "")), str(n.get("id", ""))))

    def candidates(self, material_id: str) -> list[dict[str, Any]]:
        return [
            node for node in self.material_history(material_id)
            if node.get("status") == "candidate" or node.get("candidate_for") == material_id
        ]


def _format_edge(edge: dict[str, Any], store: GraphStore, direction: str) -> str:
    other_id = cast(str, edge["source"] if direction == "upstream" else edge["target"])
    other = store.nodes_by_id.get(other_id, {})
    label = other.get("label", other_id)
    return f"  - {edge.get('id')}: {edge.get('edge_type')} {other_id} [{other.get('node_type', 'unknown')}] {label}"


def inspect(path: Path, query: str) -> int:
    errors = validate(path)
    if errors:
        print(f"INVALID {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    store = GraphStore(path)
    try:
        material_id, selected_node, resolved_by = store.resolve_material(query)
    except KeyError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    selected_id = selected_node.get("id")
    active_id = store.active_versions.get(material_id, "")
    print(f"graph_id: {store.graph.get('graph_id')}")
    print(f"material_id: {material_id}")
    print(f"resolved_by: {resolved_by}")
    print(f"selected_node: {selected_id}")
    print(f"active_node: {active_id}")
    print(f"status: {selected_node.get('status')}")
    print(f"version: {selected_node.get('version')}")
    print(f"artifact_path: {selected_node.get('artifact_path', '')}")
    if selected_node.get("supersedes"):
        print(f"supersedes: {selected_node.get('supersedes')}")
    print(f"summary: {selected_node.get('summary', '')}")

    print("versions:")
    for node in store.material_history(material_id):
        marker = " active" if node.get("id") == active_id else ""
        marker += " selected" if node.get("id") == selected_id else ""
        supersedes = f" supersedes={node.get('supersedes')}" if node.get("supersedes") else ""
        candidate_for = f" candidate_for={node.get('candidate_for')}" if node.get("candidate_for") else ""
        print(f"  - {node.get('id')}: version={node.get('version')} status={node.get('status')}{marker}{supersedes}{candidate_for}")

    print("candidates:")
    candidates = store.candidates(material_id)
    if candidates:
        for node in candidates:
            print(f"  - {node.get('id')}: version={node.get('version')} status={node.get('status')}")
    else:
        print("  - none")

    print("upstream:")
    upstream = store.upstream_edges(str(selected_id))
    if upstream:
        for edge in upstream:
            print(_format_edge(edge, store, "upstream"))
    else:
        print("  - none")

    print("downstream:")
    downstream = store.downstream_edges(str(selected_id))
    if downstream:
        for edge in downstream:
            print(_format_edge(edge, store, "downstream"))
    else:
        print("  - none")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect PPG runtime graph fixtures.")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="Inspect a material by logical material id or concrete node id.")
    inspect_parser.add_argument("graph", type=Path)
    inspect_parser.add_argument("--node", required=True, help="Logical material id or concrete material node id.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        return inspect(args.graph, args.node)
    raise AssertionError(f"unknown command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
