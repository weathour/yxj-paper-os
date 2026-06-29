#!/usr/bin/env python3
"""Run the deterministic Phase 7 overclaim repair fixture suite."""
from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

try:
    from validate_graph import validate as validate_graph
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate_graph import validate as validate_graph  # type: ignore  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
EXPECTED_NEW_STALE_SET = ["intro_draft_v1", "intro_writing_packet_v1"]
PHASE7_AFTER_GRAPH = REPO_ROOT / "examples/runtime/overclaim-loop.phase7-after.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_absolute() and path.is_relative_to(REPO_ROOT) else str(path)


def _run(cmd: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if expect_success and result.returncode != 0:
        print(f"COMMAND_FAILED exit={result.returncode}: {' '.join(cmd)}", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    if not expect_success and result.returncode == 0:
        print(f"COMMAND_UNEXPECTED_PASS: {' '.join(cmd)}", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        raise SystemExit(1)
    return result


def _require_file_equal(actual: Path, expected: Path) -> None:
    if not filecmp.cmp(actual, expected, shallow=False):
        print(f"FIXTURE_MISMATCH actual={actual} expected={expected}", file=sys.stderr)
        diff = shutil.which("diff")
        if diff:
            result = subprocess.run([diff, "-u", str(expected), str(actual)], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            print(result.stdout, file=sys.stderr)
        raise SystemExit(1)


def _load_graph(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(node.get("id")): node for node in graph.get("nodes", []) if isinstance(node, dict)}


def _newly_affected_stale_set(before_path: Path, after_path: Path) -> list[str]:
    before = _nodes_by_id(_load_graph(before_path))
    after = _nodes_by_id(_load_graph(after_path))
    affected: list[str] = []
    for node_id, after_node in after.items():
        before_status = before.get(node_id, {}).get("status")
        after_status = after_node.get("status")
        if before_status != "stale" and after_status == "stale":
            affected.append(node_id)
    return sorted(affected)


def _snapshot_files() -> dict[str, str]:
    roots = ["examples", "scripts", "schemas", "docs"]
    ignored_suffixes = {".pyc"}
    snapshot: dict[str, str] = {}
    for root_name in roots:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in ignored_suffixes:
                continue
            rel_path = _rel(path)
            snapshot[rel_path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def build_phase7_after_graph(stale_graph_path: Path) -> dict[str, Any]:
    graph = _load_graph(stale_graph_path)
    nodes = list(graph.get("nodes", []))
    edges = list(graph.get("edges", []))
    existing_node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    existing_edge_ids = {edge.get("id") for edge in edges if isinstance(edge, dict)}

    new_nodes: list[dict[str, Any]] = [
        {
            "id": "phase7_mock_reviewer_finding_v1",
            "node_type": "validator",
            "label": "Phase7 mock reviewer finding pass",
            "status": "validated",
            "version": "v1",
            "layer": 5,
            "summary": "Deterministic reviewer pass over stale intro draft that emits the Phase7 overclaim finding.",
        },
        {
            "id": "phase7_overclaim_review_finding_v1",
            "node_type": "review_finding",
            "label": "Phase7 finding: intro overclaim v1",
            "status": "validated",
            "version": "v1",
            "layer": 5,
            "failure_type": "claim_overreach",
            "primary_target": "claim_boundary_map_v1",
            "artifact_path": "examples/review_findings/phase7_overclaim.v1.yaml",
            "summary": "Mock reviewer found universal safety overclaim in intro_draft_v1.",
        },
        {
            "id": "phase7_overclaim_review_finding_v1_backflow_v1",
            "node_type": "backflow_task",
            "label": "Phase7 overclaim backflow task v1",
            "status": "planned",
            "version": "v1",
            "layer": 6,
            "artifact_path": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml",
            "summary": "Compiled local backflow task that maps claim_overreach to active ClaimBoundaryMap repair target.",
        },
        {
            "id": "intro_writing_packet_v2",
            "node_type": "transform_task",
            "task_id": "intro_writing_packet",
            "label": "WritingTaskPacket intro v2",
            "status": "validated",
            "version": "v2",
            "layer": 3,
            "artifact_path": "examples/packets/intro_writing_packet.v2.yaml",
            "summary": "Regenerated strict intro packet using active claim_boundary_map_v2 and reader_spine_v1.",
        },
        {
            "id": "phase7_mock_writer_v1",
            "node_type": "agent_run",
            "label": "Phase7 mock writer run v1",
            "status": "validated",
            "version": "v1",
            "layer": 4,
            "artifact_path": "examples/candidate_returns/intro_candidate_return.phase7.yaml",
            "summary": "Deterministic packet-bounded mock writer run returning candidate intro_draft_v2.",
        },
        {
            "id": "intro_draft_v2",
            "node_type": "manuscript_artifact",
            "label": "Intro draft v2 candidate",
            "status": "candidate",
            "version": "v2",
            "layer": 4,
            "artifact_path": "examples/candidate-artifacts/intro_draft.v2.md",
            "summary": "Regenerated candidate intro draft using bounded authority wording.",
        },
        {
            "id": "phase7_mock_reviewer_closure_v1",
            "node_type": "validator",
            "label": "Phase7 mock reviewer closure pass",
            "status": "validated",
            "version": "v1",
            "layer": 5,
            "summary": "Deterministic reviewer pass that validates intro_draft_v2 and closes the overclaim finding.",
        },
        {
            "id": "phase7_overclaim_closure_v1",
            "node_type": "validation_report",
            "report_id": "phase7_overclaim_closure_v1",
            "label": "Phase7 overclaim ReviewClosure v1",
            "status": "validated",
            "version": "v1",
            "layer": 6,
            "artifact_path": "examples/delivery/phase7_overclaim_closure.v1.yaml",
            "summary": "ReviewClosure proving the intro overclaim finding is locally repaired.",
        },
        {
            "id": "phase7_delivery_gate_v1",
            "node_type": "validation_report",
            "report_id": "phase7_delivery_gate_v1",
            "label": "Phase7 DeliveryGate v1",
            "status": "validated",
            "version": "v1",
            "layer": 7,
            "artifact_path": "examples/delivery/phase7_delivery_gate.pass.yaml",
            "summary": "DeliveryGate pass for the deterministic intro overclaim repair vertical slice.",
        },
    ]
    for node in new_nodes:
        if node["id"] not in existing_node_ids:
            nodes.append(node)

    new_edges: list[dict[str, Any]] = [
        {"id": "p7e0", "source": "phase7_mock_reviewer_finding_v1", "target": "intro_draft_v1", "edge_type": "validates", "dependency_strength": "soft"},
        {"id": "p7e1", "source": "phase7_mock_reviewer_finding_v1", "target": "phase7_overclaim_review_finding_v1", "edge_type": "reports", "dependency_strength": "provenance"},
        {"id": "p7e2", "source": "phase7_overclaim_review_finding_v1", "target": "claim_boundary_map_v1", "edge_type": "invalidates", "dependency_strength": "hard"},
        {"id": "p7e3", "source": "phase7_overclaim_review_finding_v1", "target": "phase7_overclaim_review_finding_v1_backflow_v1", "edge_type": "produces", "dependency_strength": "hard"},
        {"id": "p7e4", "source": "claim_boundary_map_v2", "target": "intro_writing_packet_v2", "edge_type": "consumes", "dependency_strength": "hard"},
        {"id": "p7e5", "source": "reader_spine_v1", "target": "intro_writing_packet_v2", "edge_type": "consumes", "dependency_strength": "hard"},
        {"id": "p7e6", "source": "evidence_inventory_v1", "target": "intro_writing_packet_v2", "edge_type": "consumes", "dependency_strength": "hard"},
        {"id": "p7e7", "source": "intro_writing_packet_v2", "target": "phase7_mock_writer_v1", "edge_type": "constrains", "dependency_strength": "hard"},
        {"id": "p7e8", "source": "phase7_mock_writer_v1", "target": "intro_draft_v2", "edge_type": "produces", "dependency_strength": "hard"},
        {"id": "p7e9", "source": "intro_writing_packet_v2", "target": "intro_draft_v2", "edge_type": "produces", "dependency_strength": "hard"},
        {"id": "p7e10", "source": "phase7_mock_reviewer_closure_v1", "target": "intro_draft_v2", "edge_type": "validates", "dependency_strength": "hard"},
        {"id": "p7e11", "source": "phase7_mock_reviewer_closure_v1", "target": "phase7_overclaim_closure_v1", "edge_type": "reports", "dependency_strength": "provenance"},
        {"id": "p7e12", "source": "phase7_overclaim_closure_v1", "target": "phase7_overclaim_review_finding_v1", "edge_type": "validates", "dependency_strength": "hard"},
        {"id": "p7e13", "source": "phase7_overclaim_closure_v1", "target": "phase7_delivery_gate_v1", "edge_type": "validates", "dependency_strength": "hard"},
    ]
    for edge in new_edges:
        if edge["id"] not in existing_edge_ids:
            edges.append(edge)

    graph["title"] = "Phase 7 Deterministic Overclaim Repair Vertical Slice"
    graph["nodes"] = nodes
    graph["edges"] = edges
    return graph


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _assert_after_graph_facts(path: Path) -> None:
    graph = _load_graph(path)
    nodes = _nodes_by_id(graph)
    required = {
        "intro_writing_packet_v2": ("transform_task", "validated"),
        "intro_draft_v2": ("manuscript_artifact", "candidate"),
        "phase7_overclaim_closure_v1": ("validation_report", "validated"),
        "phase7_delivery_gate_v1": ("validation_report", "validated"),
    }
    for node_id, (node_type, status) in required.items():
        node = nodes.get(node_id)
        if node is None:
            raise SystemExit(f"AFTER_GRAPH_MISSING_NODE {node_id}")
        if node.get("node_type") != node_type or node.get("status") != status:
            raise SystemExit(f"AFTER_GRAPH_BAD_NODE {node_id}: {node}")
    if nodes.get("intro_writing_packet_v1", {}).get("status") != "stale":
        raise SystemExit("AFTER_GRAPH_OLD_PACKET_NOT_STALE")
    if nodes.get("intro_draft_v1", {}).get("status") != "stale":
        raise SystemExit("AFTER_GRAPH_OLD_DRAFT_NOT_STALE")
    if graph.get("active_versions", {}).get("claim_boundary_map") != "claim_boundary_map_v2":
        raise SystemExit("AFTER_GRAPH_ACTIVE_CLAIM_BOUNDARY_CHANGED")


def run_suite(graph_path: Path, *, update_after_graph: bool = False) -> int:
    graph_path = graph_path if graph_path.is_absolute() else REPO_ROOT / graph_path
    graph_errors = validate_graph(graph_path)
    if graph_errors:
        for err in graph_errors:
            print(f"GRAPH_INVALID: {err}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="phase7-suite-") as tmp_text:
        tmp = Path(tmp_text)
        finding_out = tmp / "phase7-overclaim.yaml"
        backflow_out = tmp / "phase7-backflow.yaml"
        stale_graph = tmp / "phase7-stale.json"
        stale_report = tmp / "phase7-stale.report.txt"
        intro_packet = tmp / "phase7-intro-packet.yaml"
        intro_return = tmp / "phase7-intro-return.yaml"
        closure_out = tmp / "phase7-closure.yaml"
        gate_out = tmp / "phase7-gate.yaml"
        old_closure_out = tmp / "phase7-old-closure.yaml"
        old_gate_out = tmp / "phase7-old-gate.yaml"
        generated_after = tmp / "phase7-after.json"

        _run([PYTHON, "scripts/mock_reviewer.py", "--mode", "finding", "--draft", "examples/manuscript/intro.v1.md", "--out", str(finding_out)])
        _run([PYTHON, "scripts/validate_review_finding.py", str(finding_out)])
        _require_file_equal(finding_out, REPO_ROOT / "examples/review_findings/phase7_overclaim.v1.yaml")

        _run([PYTHON, "scripts/compile_backflow.py", "examples/review_findings/phase7_overclaim.v1.yaml", "--graph", _rel(graph_path), "--out", str(backflow_out)])
        _run([PYTHON, "scripts/validate_backflow.py", str(backflow_out)])
        _require_file_equal(backflow_out, REPO_ROOT / "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml")

        _run([PYTHON, "scripts/propagate_stale.py", _rel(graph_path), "--source", "claim_boundary_map.v2", "--out", str(stale_graph), "--report", str(stale_report)])
        _run([PYTHON, "scripts/validate_graph.py", str(stale_graph)])
        stale_set = _newly_affected_stale_set(graph_path, stale_graph)
        if stale_set != EXPECTED_NEW_STALE_SET:
            print(f"STALE_SET_MISMATCH actual={stale_set} expected={EXPECTED_NEW_STALE_SET}", file=sys.stderr)
            return 1

        _run([PYTHON, "scripts/compile_task_packet.py", "--graph", _rel(graph_path), "--target", "section_draft_intro.v1", "--out", str(intro_packet)])
        _run([PYTHON, "scripts/validate_packet.py", str(intro_packet)])
        _require_file_equal(intro_packet, REPO_ROOT / "examples/packets/intro_writing_packet.v2.yaml")

        before = _snapshot_files()
        _run([PYTHON, "scripts/mock_writer.py", "--packet", "examples/packets/intro_writing_packet.v2.yaml", "--return-out", str(intro_return)])
        after = _snapshot_files()
        changed = _changed_files(before, after)
        allowed_changed = ["examples/candidate-artifacts/intro_draft.v2.md"]
        disallowed = [path for path in changed if path not in allowed_changed]
        if disallowed:
            print(f"MOCK_WRITER_SIDE_EFFECTS disallowed={disallowed}", file=sys.stderr)
            return 1
        _run([PYTHON, "scripts/validate_candidate_return.py", str(intro_return), "--packet", "examples/packets/intro_writing_packet.v2.yaml"])
        _require_file_equal(intro_return, REPO_ROOT / "examples/candidate_returns/intro_candidate_return.phase7.yaml")
        _run([PYTHON, "scripts/validate_section_draft.py", "examples/candidate-artifacts/intro_draft.v2.md"])

        _run([PYTHON, "scripts/mock_reviewer.py", "--mode", "closure", "--draft", "examples/candidate-artifacts/intro_draft.v2.md", "--closure-out", str(closure_out), "--gate-out", str(gate_out)])
        _run([PYTHON, "scripts/validate_delivery_gate.py", str(closure_out)])
        _run([PYTHON, "scripts/validate_delivery_gate.py", str(gate_out)])
        _require_file_equal(closure_out, REPO_ROOT / "examples/delivery/phase7_overclaim_closure.v1.yaml")
        _require_file_equal(gate_out, REPO_ROOT / "examples/delivery/phase7_delivery_gate.pass.yaml")

        _run([PYTHON, "scripts/mock_reviewer.py", "--mode", "closure", "--draft", "examples/manuscript/intro.v1.md", "--closure-out", str(old_closure_out), "--gate-out", str(old_gate_out)], expect_success=False)
        _run([PYTHON, "scripts/validate_delivery_gate.py", str(old_closure_out)])
        _run([PYTHON, "scripts/validate_delivery_gate.py", str(old_gate_out)])
        old_gate = old_gate_out.read_text(encoding="utf-8")
        if "status: pass" in old_gate:
            print("NEGATIVE_CLOSURE_GATE_UNEXPECTED_PASS", file=sys.stderr)
            return 1

        after_graph = build_phase7_after_graph(stale_graph)
        _write_json(generated_after, after_graph)
        generated_errors = validate_graph(generated_after)
        if generated_errors:
            for err in generated_errors:
                print(f"GENERATED_AFTER_GRAPH_INVALID: {err}", file=sys.stderr)
            return 1
        if update_after_graph:
            _write_json(PHASE7_AFTER_GRAPH, after_graph)
        if not PHASE7_AFTER_GRAPH.exists():
            print(f"AFTER_GRAPH_MISSING {PHASE7_AFTER_GRAPH}", file=sys.stderr)
            return 1
        _require_file_equal(generated_after, PHASE7_AFTER_GRAPH)
        _run([PYTHON, "scripts/validate_graph.py", _rel(PHASE7_AFTER_GRAPH)])
        _assert_after_graph_facts(PHASE7_AFTER_GRAPH)

    print("PHASE7_FIXTURE_SUITE_OK")
    print("stale_set: " + ",".join(EXPECTED_NEW_STALE_SET))
    print("writer_return_valid: true")
    print("closure_valid: true")
    print("delivery_gate_pass: true")
    print("after_graph_valid: true")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Phase7 deterministic overclaim repair fixture suite.")
    parser.add_argument("graph", type=Path, help="Input PPG runtime graph fixture")
    parser.add_argument("--update-after-graph", action="store_true", help="Regenerate the committed Phase7 after graph fixture")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_suite(args.graph, update_after_graph=args.update_after_graph)


if __name__ == "__main__":
    raise SystemExit(main())
