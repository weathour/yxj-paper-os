#!/usr/bin/env python3
"""Dry-run scoped stale propagation for Phase 5 PPG runtime graphs."""
from __future__ import annotations

import argparse
from collections import deque
import copy
import json
import tempfile
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_store import GraphStore
    from validate_graph import validate as validate_graph
except ImportError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_store import GraphStore  # type: ignore  # noqa: E402
    from validate_graph import validate as validate_graph  # type: ignore  # noqa: E402


PROPAGATING_EDGE_TYPES = {"consumes", "constrains", "produces", "invalidates", "repairs"}
NON_PROPAGATING_EDGE_TYPES = {"references", "reports", "supersedes", "validates"}
OWNER_BOUNDARY_NODE_TYPES = {"owner_intent", "owner_decision"}
OWNER_BOUNDARY_MATERIAL_TYPES = {"OwnerIntent", "PaperSpine"}


def _print_graph_errors(path: Path, errors: list[str]) -> int:
    print(f"INVALID {path}", file=sys.stderr)
    for validation_issue in errors:
        print(f"- {validation_issue}", file=sys.stderr)
    return 1


def _material_version_handle(query: str) -> tuple[str, str] | None:
    if "." not in query:
        return None
    material_id, version = query.rsplit(".", 1)
    if not material_id or not version:
        return None
    if version.startswith("v"):
        return material_id, version
    return None


def resolve_source(store: GraphStore, query: str) -> tuple[dict[str, Any], str, str]:
    if query in store.nodes_by_id:
        node = store.nodes_by_id[query]
        return node, str(node.get("material_id") or query), "concrete_node_id"

    dotted = _material_version_handle(query)
    if dotted:
        material_id, version = dotted
        for node in store.material_nodes(material_id):
            if node.get("version") == version:
                return node, material_id, "material_version_handle"

    material_id, node, resolved_by = store.resolve_material(query)
    return node, material_id, resolved_by


def _edge_sort(edge: dict[str, Any]) -> str:
    return str(edge.get("id", ""))


def _node_id(node: dict[str, Any]) -> str:
    return str(node.get("id", ""))


def _is_owner_boundary(node: dict[str, Any]) -> bool:
    return (
        node.get("node_type") in OWNER_BOUNDARY_NODE_TYPES
        or node.get("material_type") in OWNER_BOUNDARY_MATERIAL_TYPES
    )


def _format_path(path_edges: list[dict[str, Any]], start_node: str, end_node: str) -> str:
    if not path_edges:
        return start_node
    parts = [start_node]
    for edge in path_edges:
        parts.append(f"--{edge.get('edge_type')}/{edge.get('id')}-->")
        parts.append(str(edge.get("target")))
    if parts[-1] != end_node:
        parts.append(end_node)
    return " ".join(parts)


def _superseded_targets(store: GraphStore, source_id: str) -> list[str]:
    targets: set[str] = set()
    source = store.nodes_by_id.get(source_id, {})
    declared = source.get("supersedes")
    if isinstance(declared, str) and declared:
        targets.add(declared)
    for edge in store.downstream_edges(source_id):
        if edge.get("edge_type") == "supersedes" and isinstance(edge.get("target"), str):
            targets.add(str(edge["target"]))
    return sorted(targets)


def _stale_reason(source_id: str, seed_id: str, path_text: str) -> str:
    return f"Downstream of revised source {source_id} via invalidated predecessor {seed_id}: {path_text}"


def propagate_stale(graph_path: Path, source_query: str, out_path: Path, report_path: Path | None) -> int:
    graph_errors = validate_graph(graph_path)
    if graph_errors:
        return _print_graph_errors(graph_path, graph_errors)

    store = GraphStore(graph_path)
    try:
        source_node, material_id, resolved_by = resolve_source(store, source_query)
    except KeyError as exc:
        print(f"ERROR cannot resolve source {source_query}: {exc}", file=sys.stderr)
        return 1

    source_id = _node_id(source_node)
    if source_node.get("node_type") != "material":
        print(f"ERROR source must be a material node, got {source_node.get('node_type')}: {source_id}", file=sys.stderr)
        return 1

    graph_out = copy.deepcopy(store.graph)
    out_nodes = graph_out.get("nodes", [])
    out_nodes_by_id = {node.get("id"): node for node in out_nodes if isinstance(node, dict) and node.get("id")}

    superseded = _superseded_targets(store, source_id)
    seeds = superseded if superseded else [source_id]
    seed_reason = "supersedes_predecessor" if superseded else "source_without_supersedes_predecessor"

    queue: deque[tuple[str, str, list[dict[str, Any]]]] = deque((seed, seed, []) for seed in seeds)
    visited_pairs: set[tuple[str, str]] = set()
    affected: dict[str, dict[str, Any]] = {}
    already_stale: dict[str, str] = {}
    owner_boundaries: dict[str, str] = {}
    non_propagating_seen: list[dict[str, Any]] = []

    while queue:
        current_id, seed_id, path_edges = queue.popleft()
        pair = (current_id, seed_id)
        if pair in visited_pairs:
            continue
        visited_pairs.add(pair)

        for edge in sorted(store.downstream_edges(current_id), key=_edge_sort):
            edge_type = str(edge.get("edge_type"))
            target_id = str(edge.get("target", ""))
            target = store.nodes_by_id.get(target_id)
            if not target:
                continue

            edge_strength = str(edge.get("dependency_strength") or "hard")
            if edge_type in NON_PROPAGATING_EDGE_TYPES or edge_strength != "hard":
                non_propagating_seen.append(edge)
                continue
            if edge_type not in PROPAGATING_EDGE_TYPES:
                non_propagating_seen.append(edge)
                continue

            new_path = [*path_edges, edge]
            path_text = _format_path(new_path, seed_id, target_id)
            if target_id == source_id:
                continue
            if _is_owner_boundary(target):
                owner_boundaries[target_id] = path_text
                continue
            if target.get("status") == "stale":
                already_stale[target_id] = path_text
            else:
                affected.setdefault(
                    target_id,
                    {
                        "seed": seed_id,
                        "path_edges": new_path,
                        "path_text": path_text,
                    },
                )
            queue.append((target_id, seed_id, new_path))

    for target_id, info in sorted(affected.items()):
        out_node = out_nodes_by_id[target_id]
        out_node["status"] = "stale"
        out_node["stale_reason"] = _stale_reason(source_id, str(info["seed"]), str(info["path_text"]))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    graph_text = json.dumps(graph_out, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tmp_file:
        tmp_file.write(graph_text)
        tmp_path = Path(tmp_file.name)
    output_errors = validate_graph(tmp_path)
    tmp_path.unlink(missing_ok=True)
    if output_errors:
        return _print_graph_errors(out_path, output_errors)
    out_path.write_text(graph_text, encoding="utf-8")

    report_text = build_report(
        store=store,
        source_query=source_query,
        source_node=source_node,
        material_id=material_id,
        resolved_by=resolved_by,
        seeds=seeds,
        seed_reason=seed_reason,
        affected=affected,
        already_stale=already_stale,
        owner_boundaries=owner_boundaries,
        non_propagating_seen=non_propagating_seen,
    )
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")

    print("STALE_PROPAGATION_OK")
    print(f"graph_id: {store.graph.get('graph_id')}")
    print(f"source_query: {source_query}")
    print(f"source_node: {source_id}")
    print(f"resolved_by: {resolved_by}")
    print(f"affected_count: {len(affected)}")
    print(f"wrote: {out_path}")
    if report_path:
        print(f"report: {report_path}")
    return 0


def build_report(
    *,
    store: GraphStore,
    source_query: str,
    source_node: dict[str, Any],
    material_id: str,
    resolved_by: str,
    seeds: list[str],
    seed_reason: str,
    affected: dict[str, dict[str, Any]],
    already_stale: dict[str, str],
    owner_boundaries: dict[str, str],
    non_propagating_seen: list[dict[str, Any]],
) -> str:
    source_id = _node_id(source_node)
    lines: list[str] = []
    lines.append("STALE_PROPAGATION_REPORT")
    lines.append(f"graph_id: {store.graph.get('graph_id')}")
    lines.append(f"source_query: {source_query}")
    lines.append(f"source_node: {source_id}")
    lines.append(f"source_material_id: {material_id}")
    lines.append(f"source_status: {source_node.get('status')}")
    lines.append(f"resolved_by: {resolved_by}")
    lines.append("propagating_edge_types: consumes, constrains, produces, invalidates, repairs")
    lines.append("non_propagating_edge_types: references, reports, supersedes, validates")
    lines.append("traversal_seeds:")
    for seed in seeds:
        if seed_reason == "supersedes_predecessor":
            lines.append(f"  - {seed}: supersedes predecessor seed of {source_id}; supersedes is not traversed as a dependency edge")
        else:
            lines.append(f"  - {seed}: source seed without supersedes predecessor")
    lines.append(f"affected_count: {len(affected)}")
    lines.append("stale_nodes:")
    if affected:
        for target_id, info in sorted(affected.items()):
            lines.append(f"  - {target_id}: {info['path_text']}")
            lines.append(f"    reason: downstream of revised source {source_id} via seed {info['seed']}")
    else:
        lines.append("  - none")
    lines.append("already_stale_nodes:")
    if already_stale:
        for node_id, path_text in sorted(already_stale.items()):
            lines.append(f"  - {node_id}: {path_text}")
    else:
        lines.append("  - none")
    lines.append("owner_gate_boundaries:")
    if owner_boundaries:
        for node_id, path_text in sorted(owner_boundaries.items()):
            lines.append(f"  - {node_id}: {path_text}")
    else:
        lines.append("  - none")
    lines.append("non_propagating_edges_seen:")
    if non_propagating_seen:
        seen_ids: set[str] = set()
        for edge in sorted(non_propagating_seen, key=_edge_sort):
            edge_id = str(edge.get("id", ""))
            if edge_id in seen_ids:
                continue
            seen_ids.add(edge_id)
            lines.append(
                f"  - {edge_id}: {edge.get('edge_type')} {edge.get('source')} -> {edge.get('target')} "
                f"({edge.get('dependency_strength', 'unspecified')}; non-propagating)"
            )
    else:
        lines.append("  - none")
    lines.append("preserved_nodes:")
    for node in sorted(store.nodes, key=_node_id):
        node_id = _node_id(node)
        if node_id in affected:
            continue
        reason = "not_reachable_from_invalidated_seed"
        if node_id == source_id:
            reason = "source_preserved"
        elif node_id in seeds and node.get("status") == "stale":
            reason = "already_stale_seed"
        elif node_id in already_stale:
            reason = "already_stale_reachable"
        elif node_id in owner_boundaries:
            reason = "owner_gate_boundary"
        lines.append(f"  - {node_id}: {reason}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run scoped stale propagation for a PPG graph.")
    parser.add_argument("graph", type=Path, help="PPG graph JSON fixture")
    parser.add_argument("--source", required=True, help="Source node id, logical material id, or material.version handle")
    parser.add_argument("--out", required=True, type=Path, help="Output graph JSON")
    parser.add_argument("--report", type=Path, help="Optional deterministic text report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return propagate_stale(args.graph, args.source, args.out, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
