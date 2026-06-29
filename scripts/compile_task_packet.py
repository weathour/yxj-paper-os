#!/usr/bin/env python3
"""Compile Phase 6 graph state into strict subagent TaskPacket fixtures.

The compiler is intentionally deterministic and dependency-free. It does not
dispatch workers and it does not mutate the graph: it only emits a bounded
TaskPacket, or a MissingMaterialReport when required source materials are not
available.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_store import GraphStore
    from ppg_validate_common import ValidationIssue, load_document
    from validate_graph import validate as validate_graph
    from validate_missing_material_report import validate as validate_missing_material_report
    from validate_packet import validate as validate_packet
except ImportError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_store import GraphStore  # type: ignore  # noqa: E402
    from ppg_validate_common import ValidationIssue, load_document  # type: ignore  # noqa: E402
    from validate_graph import validate as validate_graph  # type: ignore  # noqa: E402
    from validate_missing_material_report import validate as validate_missing_material_report  # type: ignore  # noqa: E402
    from validate_packet import validate as validate_packet  # type: ignore  # noqa: E402


INTRO_TARGET_ALIASES = {"section_draft_intro.v1", "section_draft_intro.v2", "intro_draft_v2"}
CLAIM_REPAIR_TARGET_ALIASES = {"claim_boundary_map_candidate_v3", "claim_boundary_repair.v1"}

COMMON_FORBIDDEN_ROUTES = [
    "mark_graph_complete",
    "dispatch_subagents",
    "write_outside_allowed_write_paths",
    "change_owner_intent",
]
COMMON_ALLOWED_ACTIONS = [
    "read_material_bundle",
    "draft_candidate_artifact",
    "return_evidence",
]
COMMON_ALLOWED_TOOLS = ["none"]
COMMON_RETURN_FORMAT = {
    "candidate_artifact": "required",
    "evidence": "required",
    "remaining_risks": "required",
    "missing_material_report": "required_if_blocked",
}
WORKER_BOOT_CLAUSE = (
    "completion_forbidden; no_recursive_orchestration; allowed_write_paths; "
    "MissingMaterialReport required when materials are missing; return candidate/evidence only."
)

PACKET_KEY_ORDER = [
    "schema_version",
    "packet_id",
    "status",
    "task_kind",
    "agent_type",
    "mission",
    "target_material",
    "input_materials",
    "mandatory_controls",
    "evidence_anchors",
    "forbidden_routes",
    "allowed_actions",
    "allowed_read_paths",
    "allowed_write_paths",
    "allowed_tools",
    "output_artifact_path",
    "expected_output_schema",
    "validators",
    "return_format",
    "ingestion_target",
    "stop_condition",
    "failure_report_format",
    "worker_boot_clause",
    "completion_forbidden",
    "no_recursive_orchestration",
    "owner_gate_required",
]

MISSING_REPORT_KEY_ORDER = [
    "schema_version",
    "report_id",
    "status",
    "packet_id",
    "missing_materials",
    "reason",
    "controller_action",
    "completion_forbidden",
    "no_recursive_orchestration",
]


@dataclass(frozen=True)
class MaterialHandle:
    node_id: str
    artifact_path: str


def _print_validation_issues(label: str, issues: list[ValidationIssue]) -> int:
    print(f"INVALID {label}", file=sys.stderr)
    for validation_issue in issues:
        print(f"- {validation_issue.code}: {validation_issue.message}", file=sys.stderr)
    return 1


def _print_graph_issues(path: Path, errors: list[str]) -> int:
    print(f"INVALID {path}", file=sys.stderr)
    for validation_issue in errors:
        print(f"- {validation_issue}", file=sys.stderr)
    return 1


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    text = str(value)
    needs_quote = (
        text == ""
        or text.strip() != text
        or ":" in text
        or text.startswith(("[", "{", "#", "-"))
        or text.lower() in {"true", "false", "null", "none", "~"}
    )
    if needs_quote:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _emit_yaml_value(key: str, value: Any, lines: list[str], indent: int) -> None:
    prefix = " " * indent
    if isinstance(value, dict):
        lines.append(f"{prefix}{key}:")
        for nested_key, nested_value in value.items():
            _emit_yaml_value(str(nested_key), nested_value, lines, indent + 2)
    elif isinstance(value, list):
        lines.append(f"{prefix}{key}:")
        for item in value:
            item_prefix = " " * (indent + 2)
            if isinstance(item, dict):
                lines.append(f"{item_prefix}-")
                for nested_key, nested_value in item.items():
                    _emit_yaml_value(str(nested_key), nested_value, lines, indent + 4)
            else:
                lines.append(f"{item_prefix}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{prefix}{key}: {_yaml_scalar(value)}")


def _write_yaml(path: Path, payload: dict[str, Any], key_order: list[str]) -> None:
    lines: list[str] = []
    emitted: set[str] = set()
    for key in key_order:
        if key in payload:
            _emit_yaml_value(key, payload[key], lines, 0)
            emitted.add(key)
    for key in payload:
        if key not in emitted:
            _emit_yaml_value(key, payload[key], lines, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _clear_file_output(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except IsADirectoryError:
        return


def _validate_written_yaml(
    path: Path,
    validator: Any,
    *,
    remove_on_failure: bool,
) -> list[ValidationIssue]:
    data, load_errors = load_document(path)
    if load_errors:
        if remove_on_failure:
            path.unlink(missing_ok=True)
        return load_errors
    validation_errors = validator(data)
    if validation_errors and remove_on_failure:
        path.unlink(missing_ok=True)
    return validation_errors


def _material_handle(store: GraphStore, node_id: str) -> MaterialHandle | None:
    node = store.nodes_by_id.get(node_id)
    if not node:
        return None
    artifact_path = node.get("artifact_path")
    if not isinstance(artifact_path, str) or not artifact_path:
        return None
    return MaterialHandle(node_id=node_id, artifact_path=artifact_path)


def _active_material_handle(store: GraphStore, material_id: str) -> MaterialHandle | None:
    active_node_id = store.active_versions.get(material_id)
    if not isinstance(active_node_id, str) or not active_node_id:
        return None
    return _material_handle(store, active_node_id)


def _node_exists(store: GraphStore, node_id: str) -> bool:
    return node_id in store.nodes_by_id


def _missing_intro_materials(store: GraphStore) -> list[str]:
    checks = {
        "evidence_inventory_v1": _material_handle(store, "evidence_inventory_v1"),
        "claim_boundary_map_v2": _active_material_handle(store, "claim_boundary_map"),
        "reader_spine_v1": _material_handle(store, "reader_spine_v1"),
    }
    missing: list[str] = []
    for expected, handle in checks.items():
        if handle is None or handle.node_id != expected:
            missing.append(expected)
    return missing


def _missing_claim_repair_materials(store: GraphStore) -> list[str]:
    checks = {
        "evidence_inventory_v1": _material_handle(store, "evidence_inventory_v1"),
        "claim_boundary_map_v2": _active_material_handle(store, "claim_boundary_map"),
        "finding_overclaim_v1": _node_exists(store, "finding_overclaim_v1"),
        "repair_claim_boundary_task_v1": _node_exists(store, "repair_claim_boundary_task_v1"),
    }
    missing: list[str] = []
    for expected, present in checks.items():
        if not present:
            missing.append(expected)
    return missing


def _base_packet() -> dict[str, Any]:
    return {
        "schema_version": "ppg-task-packet/v0.1",
        "status": "planned",
        "forbidden_routes": COMMON_FORBIDDEN_ROUTES,
        "allowed_actions": COMMON_ALLOWED_ACTIONS,
        "allowed_tools": COMMON_ALLOWED_TOOLS,
        "return_format": COMMON_RETURN_FORMAT,
        "failure_report_format": "ppg-missing-material-report/v0.1",
        "worker_boot_clause": WORKER_BOOT_CLAUSE,
        "completion_forbidden": True,
        "no_recursive_orchestration": True,
        "owner_gate_required": False,
    }


def _intro_packet() -> dict[str, Any]:
    packet = _base_packet()
    packet.update(
        {
            "packet_id": "intro_writing_packet_v2",
            "task_kind": "writing",
            "agent_type": "writer",
            "mission": "Draft a candidate introduction section from bounded claim and reader-spine materials.",
            "target_material": "intro_draft_v2",
            "input_materials": [
                "evidence_inventory_v1",
                "claim_boundary_map_v2",
                "reader_spine_v1",
            ],
            "mandatory_controls": {
                "evidence_inventory": "evidence_inventory_v1",
                "claim_boundary": "claim_boundary_map_v2",
                "reader_spine": "reader_spine_v1",
            },
            "evidence_anchors": [
                "examples/materials/evidence_inventory.v1.yaml",
                "examples/materials/claim_boundary_map.v2.yaml",
                "examples/materials/reader_spine.v1.yaml",
            ],
            "allowed_read_paths": [
                "examples/materials/evidence_inventory.v1.yaml",
                "examples/materials/claim_boundary_map.v2.yaml",
                "examples/materials/reader_spine.v1.yaml",
            ],
            "allowed_write_paths": ["examples/candidate-artifacts/intro_draft.v2.md"],
            "output_artifact_path": "examples/candidate-artifacts/intro_draft.v2.md",
            "expected_output_schema": "ppg-section-draft/v0.1",
            "validators": [
                "validate_packet:phase6",
                "validate_material:claim_boundary_map_v2",
            ],
            "ingestion_target": "intro_draft_v2",
            "stop_condition": "Return candidate artifact and evidence only; do not mark graph completion.",
        }
    )
    return packet


def _claim_repair_packet() -> dict[str, Any]:
    packet = _base_packet()
    packet.update(
        {
            "packet_id": "claim_repair_packet_v1",
            "task_kind": "claim_boundary_repair",
            "agent_type": "planner",
            "mission": "Draft a candidate ClaimBoundaryMap repair from overclaim finding and active evidence.",
            "target_material": "claim_boundary_map_candidate_v3",
            "input_materials": [
                "evidence_inventory_v1",
                "claim_boundary_map_v2",
                "finding_overclaim_v1",
                "repair_claim_boundary_task_v1",
            ],
            "mandatory_controls": {
                "evidence_inventory": "evidence_inventory_v1",
                "claim_boundary": "claim_boundary_map_v2",
                "review_finding": "finding_overclaim_v1",
                "backflow_task": "repair_claim_boundary_task_v1",
            },
            "evidence_anchors": [
                "examples/materials/evidence_inventory.v1.yaml",
                "examples/materials/claim_boundary_map.v2.yaml",
                "examples/review_findings/overclaim.v1.yaml",
                "examples/backflow_tasks/overclaim_repair.v1.yaml",
            ],
            "allowed_read_paths": [
                "examples/materials/evidence_inventory.v1.yaml",
                "examples/materials/claim_boundary_map.v2.yaml",
                "examples/review_findings/overclaim.v1.yaml",
                "examples/backflow_tasks/overclaim_repair.v1.yaml",
                "examples/backflow_tasks/overclaim_repair.compiled.v1.yaml",
            ],
            "allowed_write_paths": ["examples/materials/claim_boundary_map.v3-candidate.yaml"],
            "output_artifact_path": "examples/materials/claim_boundary_map.v3-candidate.yaml",
            "expected_output_schema": "ppg-material/v0.1",
            "validators": [
                "validate_packet:phase6",
                "validate_material:claim_boundary_map_v3_candidate",
            ],
            "ingestion_target": "claim_boundary_map_candidate_v3",
            "stop_condition": "Return candidate material and evidence only; do not commit the graph.",
        }
    )
    return packet


def _missing_report(packet_id: str, missing_materials: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "ppg-missing-material-report/v0.1",
        "report_id": f"{packet_id}_missing_materials_v1",
        "status": "blocked",
        "packet_id": packet_id,
        "missing_materials": missing_materials,
        "reason": "Required graph materials are missing; packet compilation is blocked.",
        "controller_action": "Main agent must restore or produce the missing materials before dispatch.",
        "completion_forbidden": True,
        "no_recursive_orchestration": True,
    }


def _compile_for_target(target: str, store: GraphStore) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str | None]:
    if target in INTRO_TARGET_ALIASES:
        missing = _missing_intro_materials(store)
        if missing:
            return None, _missing_report("intro_writing_packet_v2", missing), None
        return _intro_packet(), None, None
    if target in CLAIM_REPAIR_TARGET_ALIASES:
        missing = _missing_claim_repair_materials(store)
        if missing:
            return None, _missing_report("claim_repair_packet_v1", missing), None
        return _claim_repair_packet(), None, None
    return None, None, "E_TASK_TARGET_UNSUPPORTED"


def compile_task_packet(graph_path: Path, target: str, out_path: Path, missing_report_out: Path | None) -> int:
    _clear_file_output(out_path)
    if missing_report_out:
        _clear_file_output(missing_report_out)
    graph_errors = validate_graph(graph_path)
    if graph_errors:
        return _print_graph_issues(graph_path, graph_errors)

    store = GraphStore(graph_path)
    packet, missing_report, unsupported_code = _compile_for_target(target, store)
    if unsupported_code:
        print(f"INVALID {graph_path}", file=sys.stderr)
        print(f"- {unsupported_code}: unsupported task target: {target}", file=sys.stderr)
        return 1

    if missing_report is not None:
        report_errors = validate_missing_material_report(missing_report)
        if report_errors:
            return _print_validation_issues(str(missing_report_out or graph_path), report_errors)
        if missing_report_out:
            _write_yaml(missing_report_out, missing_report, MISSING_REPORT_KEY_ORDER)
            written_report_errors = _validate_written_yaml(
                missing_report_out,
                validate_missing_material_report,
                remove_on_failure=True,
            )
            if written_report_errors:
                return _print_validation_issues(str(missing_report_out), written_report_errors)
        print(f"INVALID {graph_path}", file=sys.stderr)
        print(f"- E_TASK_MISSING_MATERIAL: target {target} is missing required materials", file=sys.stderr)
        for material_id in missing_report["missing_materials"]:
            print(f"  - {material_id}", file=sys.stderr)
        return 1

    assert packet is not None
    packet_errors = validate_packet(packet)
    if packet_errors:
        return _print_validation_issues(str(out_path), packet_errors)
    _write_yaml(out_path, packet, PACKET_KEY_ORDER)
    written_packet_errors = _validate_written_yaml(out_path, validate_packet, remove_on_failure=True)
    if written_packet_errors:
        return _print_validation_issues(str(out_path), written_packet_errors)

    print("TASK_PACKET_COMPILE_OK")
    print(f"target: {target}")
    print(f"packet_id: {packet['packet_id']}")
    print(f"output_artifact_path: {packet['output_artifact_path']}")
    print(f"wrote: {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile a strict Phase 6 TaskPacket from a PPG graph.")
    parser.add_argument("--graph", required=True, type=Path, help="PPG graph JSON fixture")
    parser.add_argument("--target", required=True, help="Task target or supported target alias")
    parser.add_argument("--out", required=True, type=Path, help="Output TaskPacket YAML path")
    parser.add_argument("--missing-report-out", type=Path, help="Optional MissingMaterialReport YAML path for blocked compiles")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return compile_task_packet(args.graph, args.target, args.out, args.missing_report_out)


if __name__ == "__main__":
    raise SystemExit(main())
