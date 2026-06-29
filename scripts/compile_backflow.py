#!/usr/bin/env python3
"""Compile a Phase 5 ReviewFinding into a local BackflowTask."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_store import GraphStore
    from ppg_validate_common import ValidationIssue, issue, load_document
    from validate_graph import validate as validate_graph
    from validate_review_finding import validate as validate_review_finding
except ImportError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_store import GraphStore  # type: ignore  # noqa: E402
    from ppg_validate_common import ValidationIssue, issue, load_document  # type: ignore  # noqa: E402
    from validate_graph import validate as validate_graph  # type: ignore  # noqa: E402
    from validate_review_finding import validate as validate_review_finding  # type: ignore  # noqa: E402


@dataclass(frozen=True)
class MappingRule:
    level: str
    target_material_types: tuple[str, ...]
    action: str
    expected_output_by_material: dict[str, str]
    owner_gate_required: bool = False


MAPPING_RULES: dict[str, MappingRule] = {
    "overclaim": MappingRule(
        level="L3_claim_evidence",
        target_material_types=("ClaimBoundaryMap",),
        action="Replace universal safety wording with evidence-supported bounded authority allocation wording.",
        expected_output_by_material={"claim_boundary_map": "claim_boundary_map_candidate_v3"},
    ),
    "claim_overreach": MappingRule(
        level="L3_claim_evidence",
        target_material_types=("ClaimBoundaryMap",),
        action="Replace universal safety wording with evidence-supported bounded authority allocation wording.",
        expected_output_by_material={"claim_boundary_map": "claim_boundary_map_candidate_v3"},
    ),
    "claim_evidence": MappingRule(
        level="L3_claim_evidence",
        target_material_types=("ClaimBoundaryMap",),
        action="Repair claim strength so claims do not exceed cited evidence.",
        expected_output_by_material={"claim_boundary_map": "claim_boundary_map_candidate_v3"},
    ),
    "L3_claim_evidence": MappingRule(
        level="L3_claim_evidence",
        target_material_types=("ClaimBoundaryMap",),
        action="Repair claim strength so claims do not exceed cited evidence.",
        expected_output_by_material={"claim_boundary_map": "claim_boundary_map_candidate_v3"},
    ),
    "terminology": MappingRule(
        level="L1_terminology",
        target_material_types=("TerminologyRegister",),
        action="Repair inconsistent terminology and blocked labels in the terminology register.",
        expected_output_by_material={"terminology_register": "terminology_register_v2_candidate"},
    ),
    "term_mismatch": MappingRule(
        level="L1_terminology",
        target_material_types=("TerminologyRegister",),
        action="Repair inconsistent terminology and blocked labels in the terminology register.",
        expected_output_by_material={"terminology_register": "terminology_register_v2_candidate"},
    ),
    "reader_gap": MappingRule(
        level="L2_rhetorical",
        target_material_types=("ReaderSpine",),
        action="Repair reader-question and section-function alignment.",
        expected_output_by_material={"reader_spine": "reader_spine_v2_candidate"},
    ),
    "rhetorical_gap": MappingRule(
        level="L2_rhetorical",
        target_material_types=("ReaderSpine",),
        action="Repair reader-question and section-function alignment.",
        expected_output_by_material={"reader_spine": "reader_spine_v2_candidate"},
    ),
    "spine_mismatch": MappingRule(
        level="L4_spine",
        target_material_types=("PaperSpine", "OwnerIntent"),
        action="Summarize the owner decision needed for the paper spine; do not invent a new commitment.",
        expected_output_by_material={"paper_spine": "paper_spine_owner_decision"},
        owner_gate_required=True,
    ),
    "owner_intent": MappingRule(
        level="L4_spine",
        target_material_types=("PaperSpine", "OwnerIntent"),
        action="Summarize the owner decision needed for the paper spine; do not invent a new commitment.",
        expected_output_by_material={"owner_intent": "owner_intent_decision_required"},
        owner_gate_required=True,
    ),
    "L4_spine": MappingRule(
        level="L4_spine",
        target_material_types=("PaperSpine", "OwnerIntent"),
        action="Summarize the owner decision needed for the paper spine; do not invent a new commitment.",
        expected_output_by_material={"paper_spine": "paper_spine_owner_decision"},
        owner_gate_required=True,
    ),
}

OWNER_GATED_NODE_TYPES = {"owner_intent", "owner_decision"}
OWNER_GATED_MATERIAL_TYPES = {"OwnerIntent", "PaperSpine"}


def _print_issues(label: str, issues: list[ValidationIssue]) -> int:
    print(f"INVALID {label}", file=sys.stderr)
    for validation_issue in issues:
        print(f"- {validation_issue.code}: {validation_issue.message}", file=sys.stderr)
    return 1


def _graph_issues(label: str, issues: list[str]) -> int:
    print(f"INVALID {label}", file=sys.stderr)
    for validation_issue in issues:
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


def resolve_graph_node(store: GraphStore, query: str) -> tuple[dict[str, Any], str, str]:
    """Resolve exact node id, logical material id, or dotted material version."""

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


def _active_material_node(store: GraphStore, node: dict[str, Any], material_id: str) -> dict[str, Any]:
    """Retarget stale/rejected historical material to the active version only."""

    if node.get("status") not in {"stale", "rejected"}:
        return node
    active_id = store.active_versions.get(material_id)
    if not active_id:
        return node
    active_node = store.nodes_by_id.get(active_id)
    if not active_node:
        return node
    return active_node


def _owner_gate_required(rule: MappingRule, target_node: dict[str, Any]) -> bool:
    return (
        rule.owner_gate_required
        or target_node.get("node_type") in OWNER_GATED_NODE_TYPES
        or target_node.get("material_type") in OWNER_GATED_MATERIAL_TYPES
    )


def _mapping_label(failure_type: str, rule: MappingRule, target_node: dict[str, Any]) -> str:
    target_type = target_node.get("material_type") or target_node.get("node_type") or "unknown"
    return f"{failure_type} -> {rule.level} -> {target_type}"


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    text = str(value)
    if text == "" or text.strip() != text or ": " in text or text.startswith(("[", "{", "#", "-")):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _write_backflow(path: Path, backflow: dict[str, Any]) -> None:
    ordered_keys = [
        "schema_version",
        "backflow_id",
        "finding_id",
        "status",
        "target",
        "action",
        "expected_output",
        "failure_type",
        "backflow_level",
        "mapping_rule",
        "source_target",
        "owner_gate_required",
        "affected_material_id",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {_yaml_scalar(backflow[key])}" for key in ordered_keys if key in backflow]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compile_backflow(finding_path: Path, graph_path: Path, out_path: Path) -> int:
    graph_errors = validate_graph(graph_path)
    if graph_errors:
        return _graph_issues(str(graph_path), graph_errors)

    finding, finding_errors = load_document(finding_path)
    if finding_errors:
        return _print_issues(str(finding_path), finding_errors)
    validation_errors = validate_review_finding(finding)
    if validation_errors:
        return _print_issues(str(finding_path), validation_errors)
    assert isinstance(finding, dict)

    store = GraphStore(graph_path)
    failure_type = str(finding.get("failure_type"))
    rule = MAPPING_RULES.get(failure_type)
    if not rule:
        return _print_issues(
            str(finding_path),
            [issue("E_BACKFLOW_MAPPING_UNSUPPORTED", f"unsupported failure_type: {failure_type}")],
        )

    source_target = str(finding.get("target"))
    try:
        resolved_target, material_id, resolved_by = resolve_graph_node(store, source_target)
    except KeyError as exc:
        return _print_issues(str(finding_path), [issue("E_BACKFLOW_TARGET_UNRESOLVED", str(exc))])

    target_node = resolved_target
    if resolved_target.get("node_type") == "material":
        target_node = _active_material_node(store, resolved_target, material_id)
        material_id = str(target_node.get("material_id") or material_id)

    owner_gate_required = _owner_gate_required(rule, target_node)
    target_type = str(target_node.get("material_type") or target_node.get("node_type") or "")
    if not owner_gate_required and rule.target_material_types and target_type not in rule.target_material_types:
        return _print_issues(
            str(finding_path),
            [
                issue(
                    "E_BACKFLOW_TARGET_TYPE_MISMATCH",
                    f"failure_type {failure_type} expects one of {', '.join(rule.target_material_types)}, got {target_type or 'unknown'}",
                )
            ],
        )

    target_id = str(target_node.get("id"))
    expected_output = rule.expected_output_by_material.get(material_id)
    if owner_gate_required and not expected_output:
        expected_output = f"{material_id or target_id}_owner_decision_required"
    if not expected_output:
        expected_output = f"{material_id or target_id}_candidate"

    finding_id = str(finding.get("finding_id"))
    backflow = {
        "schema_version": "ppg-backflow-task/v0.1",
        "backflow_id": f"{finding_id}_backflow_v1",
        "finding_id": finding_id,
        "status": "owner_gated" if owner_gate_required else "planned",
        "target": target_id,
        "action": rule.action,
        "expected_output": expected_output,
        "failure_type": failure_type,
        "backflow_level": rule.level,
        "mapping_rule": _mapping_label(failure_type, rule, target_node),
        "source_target": source_target,
        "owner_gate_required": owner_gate_required,
        "affected_material_id": material_id,
    }
    _write_backflow(out_path, backflow)

    print("BACKFLOW_COMPILE_OK")
    print(f"finding_id: {finding_id}")
    print(f"failure_type: {failure_type}")
    print(f"source_target: {source_target}")
    print(f"resolved_by: {resolved_by}")
    print(f"target: {target_id}")
    print(f"expected_output: {expected_output}")
    print(f"owner_gate_required: {str(owner_gate_required).lower()}")
    print(f"mapping_rule: {backflow['mapping_rule']}")
    print(f"wrote: {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile a ReviewFinding into a Phase 5 local BackflowTask.")
    parser.add_argument("finding", type=Path, help="ReviewFinding JSON/YAML fixture")
    parser.add_argument("--graph", required=True, type=Path, help="PPG graph JSON fixture")
    parser.add_argument("--out", required=True, type=Path, help="Output BackflowTask YAML")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return compile_backflow(args.finding, args.graph, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
