#!/usr/bin/env python3
"""Read-only operator-facing runtime adapter for PPG graph state.

The adapter intentionally wraps the proven graph store/controller helpers instead
of becoming a second runtime. It validates input first, then emits deterministic
JSON or Markdown state reports for the main agent and the frontend viewer.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from ppg_store import GraphStore, completion_blockers, select_frontier
    from validate_graph import validate
except ImportError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_store import GraphStore, completion_blockers, select_frontier  # type: ignore  # noqa: E402
    from validate_graph import validate  # type: ignore  # noqa: E402

REQUIRED_JSON_KEYS = [
    "schema_version",
    "graph",
    "active_versions",
    "next_frontier",
    "stale_materials",
    "candidate_materials",
    "owner_decisions",
    "open_review_findings",
    "backflow_tasks",
    "delivery_gates",
    "review_closures",
    "completion_blockers",
]


def _node_id(node: dict[str, Any]) -> str:
    return str(node.get("id", ""))


def _edge_target_ids(store: GraphStore, node_id: str, *, edge_types: set[str] | None = None) -> list[str]:
    values: list[str] = []
    for edge in store.downstream_edges(node_id):
        if edge_types and edge.get("edge_type") not in edge_types:
            continue
        target = str(edge.get("target", ""))
        if target:
            values.append(target)
    return values


def _edge_source_ids(store: GraphStore, node_id: str, *, edge_types: set[str] | None = None) -> list[str]:
    values: list[str] = []
    for edge in store.upstream_edges(node_id):
        if edge_types and edge.get("edge_type") not in edge_types:
            continue
        source = str(edge.get("source", ""))
        if source:
            values.append(source)
    return values


def _base_node(node: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": _node_id(node),
        "node_type": node.get("node_type", ""),
        "status": node.get("status", ""),
        "label": node.get("label", ""),
    }
    for key in [
        "material_id",
        "version",
        "artifact_path",
        "summary",
        "stale_reason",
        "failure_type",
        "primary_target",
        "report_id",
        "task_id",
    ]:
        value = node.get(key)
        if value not in (None, ""):
            payload[key] = value
    return payload


def _material_entry(store: GraphStore, node: dict[str, Any]) -> dict[str, Any]:
    entry = _base_node(node)
    if node.get("status") == "stale":
        entry["historical_superseded_by_active"] = store.is_historical_stale_superseded_by_active(node)
        entry["on_active_control_path"] = store.is_stale_upstream_control_on_active_path(node)
    if node.get("candidate_for"):
        entry["candidate_for"] = node.get("candidate_for")
    if node.get("supersedes"):
        entry["supersedes"] = node.get("supersedes")
    return entry


def _sorted_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(nodes, key=lambda node: _node_id(node))


def _validation_reports(store: GraphStore, *, token: str) -> list[dict[str, Any]]:
    token = token.lower()
    reports: list[dict[str, Any]] = []
    for node in _sorted_nodes(store.nodes):
        if node.get("node_type") != "validation_report":
            continue
        haystack = " ".join(str(node.get(key, "")) for key in ["id", "report_id", "label", "summary"]).lower()
        if token not in haystack:
            continue
        entry = _base_node(node)
        entry["validates"] = _edge_target_ids(store, _node_id(node), edge_types={"validates"})
        entry["reported_by"] = _edge_source_ids(store, _node_id(node), edge_types={"reports"})
        reports.append(entry)
    return reports


def _backflow_tasks(store: GraphStore) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for node in _sorted_nodes(store.nodes):
        if node.get("node_type") != "backflow_task":
            continue
        entry = _base_node(node)
        entry["source_findings"] = _edge_source_ids(store, _node_id(node), edge_types={"produces", "repairs", "invalidates"})
        entry["targets"] = _edge_target_ids(store, _node_id(node), edge_types={"repairs", "produces", "constrains", "consumes"})
        tasks.append(entry)
    return tasks


def _owner_decisions(store: GraphStore) -> list[dict[str, Any]]:
    return [_base_node(node) for node in _sorted_nodes(store.nodes) if node.get("node_type") == "owner_decision"]


def _review_findings(store: GraphStore) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for node in store.open_review_findings():
        entry = _base_node(node)
        entry["classified_repair"] = store.has_classified_repair(_node_id(node))
        entry["repair_tasks"] = _edge_target_ids(store, _node_id(node), edge_types={"produces", "repairs"})
        entry["invalidates"] = _edge_target_ids(store, _node_id(node), edge_types={"invalidates"})
        findings.append(entry)
    return findings


def build_runtime_state(graph_path: Path) -> dict[str, Any]:
    errors = validate(graph_path)
    if errors:
        raise ValueError("; ".join(errors))

    store = GraphStore(graph_path)
    state = {
        "schema_version": "ppg-runtime-state-report/v0.1",
        "graph": {
            "graph_id": store.graph.get("graph_id", ""),
            "title": store.graph.get("title", ""),
            "source_path": str(graph_path),
            "node_count": len(store.nodes),
            "edge_count": len(store.edges),
        },
        "active_versions": [
            {
                "material_id": material_id,
                "active_node": node_id,
                "status": store.nodes_by_id.get(node_id, {}).get("status", "missing"),
                "version": store.nodes_by_id.get(node_id, {}).get("version", ""),
                "artifact_path": store.nodes_by_id.get(node_id, {}).get("artifact_path", ""),
            }
            for material_id, node_id in sorted(store.active_versions.items())
        ],
        "next_frontier": select_frontier(store),
        "stale_materials": [_material_entry(store, node) for node in store.stale_materials()],
        "candidate_materials": [_material_entry(store, node) for node in store.candidate_materials()],
        "owner_decisions": _owner_decisions(store),
        "open_review_findings": _review_findings(store),
        "backflow_tasks": _backflow_tasks(store),
        "delivery_gates": _validation_reports(store, token="delivery_gate"),
        "review_closures": _validation_reports(store, token="closure"),
        "completion_blockers": completion_blockers(store),
    }
    missing = [key for key in REQUIRED_JSON_KEYS if key not in state]
    if missing:  # defensive: protects the external report contract
        raise RuntimeError(f"runtime state missing keys: {', '.join(missing)}")
    return state


def _table_or_none(rows: list[str]) -> str:
    return "\n".join(rows) if rows else "- none"


def render_markdown(state: dict[str, Any]) -> str:
    graph = state["graph"]
    frontier = state["next_frontier"]
    sections: list[str] = [
        "# PPG Runtime State Report",
        "",
        "## Graph",
        f"- graph_id: {graph['graph_id']}",
        f"- title: {graph['title']}",
        f"- source_path: {graph['source_path']}",
        f"- nodes: {graph['node_count']}",
        f"- edges: {graph['edge_count']}",
        "",
        "## Next Frontier",
        f"- id: {frontier.get('id', '')}",
        f"- kind: {frontier.get('kind', '')}",
        f"- priority: {frontier.get('priority', '')}",
        f"- reason: {frontier.get('reason', '')}",
        "",
        "## Active Versions",
        _table_or_none([
            f"- {item['material_id']} -> {item['active_node']} ({item.get('status', '')}, {item.get('version', '')})"
            for item in state["active_versions"]
        ]),
        "",
        "## Stale Materials",
        _table_or_none([
            f"- {item['id']}: {item.get('material_id', '')}@{item.get('version', '')}; historical={str(item.get('historical_superseded_by_active', False)).lower()}; active_path={str(item.get('on_active_control_path', False)).lower()}"
            for item in state["stale_materials"]
        ]),
        "",
        "## Candidate Materials",
        _table_or_none([
            f"- {item['id']}: candidate_for={item.get('candidate_for', '')}; status={item.get('status', '')}; supersedes={item.get('supersedes', '')}"
            for item in state["candidate_materials"]
        ]),
        "",
        "## Owner Decisions",
        _table_or_none([f"- {item['id']}: {item.get('status', '')} — {item.get('label', '')}" for item in state["owner_decisions"]]),
        "",
        "## Review Findings",
        _table_or_none([
            f"- {item['id']}: {item.get('failure_type', '')}; classified_repair={str(item.get('classified_repair', False)).lower()}; repair_tasks={','.join(item.get('repair_tasks', [])) or 'none'}"
            for item in state["open_review_findings"]
        ]),
        "",
        "## Backflow Tasks",
        _table_or_none([f"- {item['id']}: {item.get('status', '')}; artifact={item.get('artifact_path', '')}" for item in state["backflow_tasks"]]),
        "",
        "## Delivery Gates",
        _table_or_none([f"- {item['id']}: {item.get('status', '')}; validates={','.join(item.get('validates', [])) or 'none'}" for item in state["delivery_gates"]]),
        "",
        "## Review Closures",
        _table_or_none([f"- {item['id']}: {item.get('status', '')}; validates={','.join(item.get('validates', [])) or 'none'}" for item in state["review_closures"]]),
        "",
        "## Completion Blockers",
        _table_or_none([f"- {item}" for item in state["completion_blockers"]]),
        "",
    ]
    return "\n".join(sections)


def write_output(text: str, out: Path | None) -> None:
    if out is None:
        print(text, end="")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit a deterministic read-only PPG runtime state report.")
    parser.add_argument("--graph", required=True, type=Path, help="PPG graph JSON fixture to inspect.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Report output format.")
    parser.add_argument("--out", type=Path, help="Write output to path instead of stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = build_runtime_state(args.graph)
    except Exception as exc:  # noqa: BLE001 - CLI adapter reports validation failures uniformly
        print(f"INVALID {args.graph}: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        write_output(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", args.out)
    else:
        write_output(render_markdown(state), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
