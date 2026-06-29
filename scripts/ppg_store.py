#!/usr/bin/env python3
"""Dependency-free store/controller CLI for PPG runtime graph fixtures."""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any, cast

try:
    from validate_graph import validate
except ImportError:  # pragma: no cover - script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate_graph import validate  # type: ignore  # noqa: E402


FRONTIER_REASONS = {
    "owner_gated": "owner_gated_root_decision",
    "stale": "unsuperseded_stale_upstream_control",
    "blocked": "blocked_validator_or_material_prerequisite",
    "missing_task_packet": "missing_task_packet_for_active_manuscript_unit",
    "candidate": "candidate_material_awaiting_validation_or_commit_plan",
    "review_finding": "review_finding_awaiting_classification",
    "export_blocker": "export_or_rendering_blocker",
    "none": "no_runnable_frontier",
}


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

    def nodes_by_status(self, status: str) -> list[dict[str, Any]]:
        return sorted((node for node in self.nodes if node.get("status") == status), key=_node_id)

    def owner_gated_items(self) -> list[dict[str, Any]]:
        return self.nodes_by_status("owner_gated")

    def blocked_items(self) -> list[dict[str, Any]]:
        return self.nodes_by_status("blocked")

    def stale_materials(self) -> list[dict[str, Any]]:
        return sorted(
            (node for node in self.nodes if node.get("node_type") == "material" and node.get("status") == "stale"),
            key=_node_id,
        )

    def committed_materials(self) -> list[dict[str, Any]]:
        return sorted(
            (node for node in self.nodes if node.get("node_type") == "material" and node.get("status") == "committed"),
            key=_node_id,
        )

    def candidate_materials(self) -> list[dict[str, Any]]:
        return sorted(
            (node for node in self.nodes if _is_candidate_material(node)),
            key=_node_id,
        )

    def open_review_findings(self) -> list[dict[str, Any]]:
        closed = {"committed", "rejected"}
        return sorted(
            (node for node in self.nodes if node.get("node_type") == "review_finding" and node.get("status") not in closed),
            key=_node_id,
        )

    def has_classified_repair(self, review_finding_id: str) -> bool:
        for edge in self.downstream_edges(review_finding_id):
            target = self.nodes_by_id.get(str(edge.get("target")), {})
            if edge.get("edge_type") in {"produces", "repairs"} and target.get("node_type") == "backflow_task":
                return True
        return False

    def supersedes_targets(self, node_id: str) -> set[str]:
        node = self.nodes_by_id.get(node_id, {})
        targets: set[str] = set()
        declared = node.get("supersedes")
        if isinstance(declared, str) and declared:
            targets.add(declared)
        for edge in self.downstream_edges(node_id):
            if edge.get("edge_type") == "supersedes" and isinstance(edge.get("target"), str):
                targets.add(cast(str, edge["target"]))
        return targets

    def is_historical_stale_superseded_by_active(self, stale_node: dict[str, Any]) -> bool:
        """Return true when a stale material is already behind the active version.

        Phase 3 still reports historical stale materials, but the frontier must
        not keep selecting an old stale version that is already superseded by the
        material's active committed node.
        """

        if stale_node.get("node_type") != "material" or stale_node.get("status") != "stale":
            return False
        stale_id = str(stale_node.get("id", ""))
        material_id = stale_node.get("material_id")
        if not isinstance(material_id, str):
            return False
        active_id = self.active_versions.get(material_id)
        if not active_id or active_id == stale_id:
            return False

        queue: deque[str] = deque([active_id])
        visited: set[str] = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for target in sorted(self.supersedes_targets(current)):
                if target == stale_id:
                    return True
                if target not in visited:
                    queue.append(target)
        return False

    def is_stale_upstream_control_on_active_path(self, stale_node: dict[str, Any]) -> bool:
        """Return true for unsuperseded stale control material on a live path.

        This is intentionally smaller than Phase 5 stale propagation. It only
        prevents disconnected stale sidecars from outranking real candidate work
        while preserving Phase 3's active/control-path frontier semantics.
        """

        if stale_node.get("node_type") != "material" or stale_node.get("status") != "stale":
            return False
        stale_id = _node_id(stale_node)
        if self.is_historical_stale_superseded_by_active(stale_node):
            return False

        live_node_types = {"transform_task", "manuscript_artifact", "material", "backflow_task"}
        live_statuses = {"planned", "candidate", "validated", "blocked", "owner_gated"}
        queue: deque[str] = deque([stale_id])
        visited: set[str] = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for edge in self.downstream_edges(current):
                edge_type = edge.get("edge_type")
                if edge_type not in {"consumes", "constrains"}:
                    continue
                if edge.get("dependency_strength") == "provenance":
                    continue
                target_id = str(edge.get("target", ""))
                target = self.nodes_by_id.get(target_id, {})
                if target_id != stale_id and target.get("node_type") in live_node_types and target.get("status") in live_statuses:
                    return True
                if target_id and target_id not in visited:
                    queue.append(target_id)
        return False


def _node_id(node: dict[str, Any]) -> str:
    return str(node.get("id", ""))


def _is_candidate_material(node: dict[str, Any]) -> bool:
    return (
        node.get("node_type") == "material"
        and (node.get("status") == "candidate" or isinstance(node.get("candidate_for"), str))
    )


def _format_edge(edge: dict[str, Any], store: GraphStore, direction: str) -> str:
    other_id = cast(str, edge["source"] if direction == "upstream" else edge["target"])
    other = store.nodes_by_id.get(other_id, {})
    label = other.get("label", other_id)
    return f"  - {edge.get('id')}: {edge.get('edge_type')} {other_id} [{other.get('node_type', 'unknown')}] {label}"


def _print_node_list(nodes: list[dict[str, Any]], formatter: Any) -> None:
    if not nodes:
        print("  - none")
        return
    for node in nodes:
        print(formatter(node))


def _material_line(node: dict[str, Any], *, extra: str = "") -> str:
    pieces = [
        f"material_id={node.get('material_id', '')}",
        f"version={node.get('version', '')}",
        f"status={node.get('status', '')}",
    ]
    if node.get("candidate_for"):
        pieces.append(f"candidate_for={node.get('candidate_for')}")
    if node.get("supersedes"):
        pieces.append(f"supersedes={node.get('supersedes')}")
    if extra:
        pieces.append(extra)
    return f"  - {_node_id(node)}: " + " ".join(pieces)


def _item_line(node: dict[str, Any], *, extra: str = "") -> str:
    pieces = [
        f"type={node.get('node_type', '')}",
        f"status={node.get('status', '')}",
    ]
    if node.get("version"):
        pieces.append(f"version={node.get('version')}")
    if extra:
        pieces.append(extra)
    return f"  - {_node_id(node)}: " + " ".join(pieces)


def _has_validation_report_for(store: GraphStore, node_id: str) -> bool:
    for edge in store.upstream_edges(node_id):
        source = store.nodes_by_id.get(str(edge.get("source")), {})
        if edge.get("edge_type") == "references" and source.get("node_type") == "validation_report" and source.get("status") == "validated":
            return True
    return False


def _has_validator_for(store: GraphStore, node_id: str) -> bool:
    for edge in store.upstream_edges(node_id):
        source = store.nodes_by_id.get(str(edge.get("source")), {})
        if edge.get("edge_type") == "validates" and source.get("node_type") == "validator" and source.get("status") == "validated":
            return True
    return False


def _has_provenance_for(store: GraphStore, node_id: str) -> bool:
    provenance_edges = {"produces", "consumes", "constrains"}
    for edge in store.upstream_edges(node_id):
        source = store.nodes_by_id.get(str(edge.get("source")), {})
        if source.get("node_type") == "validation_report":
            continue
        if edge.get("edge_type") in provenance_edges:
            return True
    return False


def candidate_commit_analysis(store: GraphStore, candidate_id: str) -> dict[str, Any]:
    node = store.nodes_by_id.get(candidate_id)
    missing: list[str] = []
    material_id = ""
    active_id = ""

    if not node:
        return {
            "candidate": candidate_id,
            "material_id": material_id,
            "active_node": active_id,
            "candidate_status": "missing",
            "can_commit": False,
            "missing_requirements": ["candidate node does not exist"],
            "would_update_active_versions": None,
            "event_log_preview": None,
        }

    candidate_status = str(node.get("status", ""))
    is_material = node.get("node_type") == "material"
    is_candidate_like = _is_candidate_material(node)
    if not is_material:
        missing.append("node must be a material candidate")
    if not is_candidate_like:
        missing.append("node is not marked as candidate material")

    if is_candidate_like:
        if candidate_status != "validated":
            missing.append("candidate status must be validated before commit")

        material_id = str(node.get("candidate_for") or node.get("material_id") or "")
        if not material_id:
            missing.append("candidate material_id or candidate_for is required")
        elif node.get("material_id") and node.get("material_id") != material_id:
            missing.append("candidate material_id must match candidate_for")

        active_id = store.active_versions.get(material_id, "") if material_id else ""
        active_node = store.nodes_by_id.get(active_id, {}) if active_id else {}
        if not active_id:
            missing.append("target material must have an active committed node")
        elif active_node.get("status") != "committed":
            missing.append("active target must be committed")

        if node.get("candidate_for") != material_id:
            missing.append("candidate_for must name the target logical material")

        if active_id:
            if node.get("supersedes") != active_id:
                missing.append(f"candidate must declare supersedes={active_id}")
            has_matching_edge = any(
                edge.get("edge_type") == "supersedes" and edge.get("source") == candidate_id and edge.get("target") == active_id
                for edge in store.edges
            )
            if not has_matching_edge:
                missing.append(f"candidate must have supersedes edge {candidate_id} -> {active_id}")

        if not _has_validator_for(store, candidate_id):
            missing.append("candidate-specific validator edge is required")
        if not _has_validation_report_for(store, candidate_id):
            missing.append("candidate-specific validation report reference is required")
        if not _has_provenance_for(store, candidate_id):
            missing.append("candidate provenance edge is required")
    elif is_material:
        material_id = str(node.get("material_id") or "")
        active_id = store.active_versions.get(material_id, "") if material_id else ""

    can_commit = not missing
    transition = {
        "material_id": material_id,
        "from_node": active_id,
        "to_node": candidate_id,
    } if is_candidate_like and material_id and active_id else None
    return {
        "candidate": candidate_id,
        "material_id": material_id,
        "active_node": active_id,
        "candidate_status": candidate_status,
        "can_commit": can_commit,
        "missing_requirements": missing,
        "would_update_active_versions": transition,
        "event_log_preview": {
            "action": "commit_candidate",
            "dry_run": True,
            **transition,
        } if transition else None,
    }


def select_frontier(store: GraphStore) -> dict[str, Any]:
    owner_items = store.owner_gated_items()
    if owner_items:
        node = owner_items[0]
        return {"priority": 1, "id": _node_id(node), "kind": str(node.get("node_type", "owner_decision")), "reason": FRONTIER_REASONS["owner_gated"]}

    stale_frontiers = [node for node in store.stale_materials() if store.is_stale_upstream_control_on_active_path(node)]
    if stale_frontiers:
        node = stale_frontiers[0]
        return {"priority": 2, "id": _node_id(node), "kind": "material", "reason": FRONTIER_REASONS["stale"]}

    blocked = store.blocked_items()
    if blocked:
        node = blocked[0]
        return {"priority": 3, "id": _node_id(node), "kind": str(node.get("node_type", "blocked")), "reason": FRONTIER_REASONS["blocked"]}

    missing_task_packets = [
        node for node in store.nodes
        if node.get("node_type") == "manuscript_artifact" and node.get("status") == "planned" and node.get("needs_task_packet") is True
    ]
    if missing_task_packets:
        node = sorted(missing_task_packets, key=_node_id)[0]
        return {"priority": 4, "id": _node_id(node), "kind": "manuscript_artifact", "reason": FRONTIER_REASONS["missing_task_packet"]}

    candidates = store.candidate_materials()
    if candidates:
        node = candidates[0]
        return {"priority": 5, "id": _node_id(node), "kind": "material", "reason": FRONTIER_REASONS["candidate"]}

    unclassified_findings = [node for node in store.open_review_findings() if not store.has_classified_repair(_node_id(node))]
    if unclassified_findings:
        node = unclassified_findings[0]
        return {"priority": 6, "id": _node_id(node), "kind": "review_finding", "reason": FRONTIER_REASONS["review_finding"]}

    return {"priority": 0, "id": "none", "kind": "none", "reason": FRONTIER_REASONS["none"]}


def completion_blockers(store: GraphStore) -> list[str]:
    blockers: list[str] = []
    for node in store.candidate_materials():
        analysis = candidate_commit_analysis(store, _node_id(node))
        if not analysis["can_commit"]:
            missing = "; ".join(analysis["missing_requirements"])
            blockers.append(f"candidate {_node_id(node)} cannot commit: {missing}")
    for item in store.owner_gated_items():
        blockers.append(f"owner-gated item {_node_id(item)} requires human owner decision")
    return blockers


def emit_frontier(frontier: dict[str, Any]) -> None:
    print(f"frontier_id: {frontier['id']}")
    print(f"frontier_kind: {frontier['kind']}")
    print(f"priority: {frontier['priority']}")
    print(f"reason: {frontier['reason']}")


def report(path: Path) -> int:
    errors = validate(path)
    if errors:
        print(f"INVALID {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    store = GraphStore(path)
    frontier = select_frontier(store)
    print(f"graph_id: {store.graph.get('graph_id')}")
    print("active_versions:")
    if store.active_versions:
        for material_id, node_id in sorted(store.active_versions.items()):
            print(f"  - {material_id}: {node_id}")
    else:
        print("  - none")

    print("committed_materials:")
    _print_node_list(store.committed_materials(), _material_line)

    print("candidate_materials:")
    _print_node_list(store.candidate_materials(), _material_line)

    print("stale_materials:")
    stale = store.stale_materials()
    if stale:
        for node in stale:
            historical = str(store.is_historical_stale_superseded_by_active(node)).lower()
            print(_material_line(node, extra=f"historical_superseded_by_active={historical}"))
    else:
        print("  - none")

    print("blocked_items:")
    _print_node_list(store.blocked_items(), _item_line)

    print("owner_gated_items:")
    _print_node_list(store.owner_gated_items(), _item_line)

    print("open_review_findings:")
    findings = store.open_review_findings()
    if findings:
        for node in findings:
            classified = str(store.has_classified_repair(_node_id(node))).lower()
            print(_item_line(node, extra=f"classified_repair={classified}"))
    else:
        print("  - none")

    print("next_frontier:")
    print(f"  id: {frontier['id']}")
    print(f"  kind: {frontier['kind']}")
    print(f"  priority: {frontier['priority']}")
    print(f"  reason: {frontier['reason']}")

    print("completion_blockers:")
    blockers = completion_blockers(store)
    if blockers:
        for blocker in blockers:
            print(f"  - {blocker}")
    else:
        print("  - none")
    return 0


def frontier(path: Path) -> int:
    errors = validate(path)
    if errors:
        print(f"INVALID {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    store = GraphStore(path)
    emit_frontier(select_frontier(store))
    return 0


def commit_plan(path: Path, candidate_id: str) -> int:
    errors = validate(path)
    if errors:
        print(f"INVALID {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    store = GraphStore(path)
    analysis = candidate_commit_analysis(store, candidate_id)
    print(f"graph_id: {store.graph.get('graph_id')}")
    print(f"candidate: {analysis['candidate']}")
    print(f"material_id: {analysis['material_id']}")
    print(f"active_node: {analysis['active_node']}")
    print(f"candidate_status: {analysis['candidate_status']}")
    print(f"can_commit: {str(analysis['can_commit']).lower()}")
    print("missing_requirements:")
    missing = cast(list[str], analysis["missing_requirements"])
    if missing:
        for item in missing:
            print(f"  - {item}")
    else:
        print("  - none")

    print("would_update_active_versions:")
    transition = analysis["would_update_active_versions"]
    if transition:
        print(f"  - {transition['material_id']}: {transition['from_node']} -> {transition['to_node']}")
    else:
        print("  - none")

    print("event_log_preview:")
    event = analysis["event_log_preview"]
    if event:
        print(f"  - action: {event['action']}")
        print(f"    dry_run: {str(event['dry_run']).lower()}")
        print(f"    material_id: {event['material_id']}")
        print(f"    from_node: {event['from_node']}")
        print(f"    to_node: {event['to_node']}")
    else:
        print("  - none")
    return 0


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
    parser = argparse.ArgumentParser(description="Inspect and dry-run-control PPG runtime graph fixtures.")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="Inspect a material by logical material id or concrete node id.")
    inspect_parser.add_argument("graph", type=Path)
    inspect_parser.add_argument("--node", required=True, help="Logical material id or concrete material node id.")

    report_parser = sub.add_parser("report", help="Print a deterministic controller state report.")
    report_parser.add_argument("graph", type=Path)

    frontier_parser = sub.add_parser("frontier", help="Select the next controller frontier item.")
    frontier_parser.add_argument("graph", type=Path)

    commit_parser = sub.add_parser("commit-plan", help="Dry-run candidate commit readiness without mutating the graph.")
    commit_parser.add_argument("graph", type=Path)
    commit_parser.add_argument("--candidate", required=True, help="Concrete candidate material node id.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        return inspect(args.graph, args.node)
    if args.command == "report":
        return report(args.graph)
    if args.command == "frontier":
        return frontier(args.graph)
    if args.command == "commit-plan":
        return commit_plan(args.graph, args.candidate)
    raise AssertionError(f"unknown command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
