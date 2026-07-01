#!/usr/bin/env python3
"""Verify Phase9 local-paper full-stage PilotStageRun coverage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    from generate_local_paper_full_pilot import FLOW_EDGES
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_local_paper_full_pilot import FLOW_EDGES  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT = ROOT / "examples" / "local-paper" / "sample-paper-workspace"
REGISTRY = ROOT / "runtime" / "stage_registry.json"
CONTRACT_DIR = ROOT / "examples" / "stage-contracts"
OVERLAY_REGISTRY_REF = "runtime/stage_overlay_registry.json"
NATURE_OVERLAY_ID = "nature_expert_writing"
RUN_SCHEMA_VERSION = "ppg-pilot-stage-run/v0.1"
SUMMARY_SCHEMA_VERSION = "ppg-local-paper-full-pilot/v0.1"
ALLOWED_COVERAGE_KINDS = {"source_projected", "fixture_generated", "script_checked", "owner_gated_deferred", "not_applicable_with_reason"}
ALLOWED_EXERCISE_LEVELS = {"full_stage_exercised", "contract_only", "deferred_with_gate", "not_applicable"}
REQUIRED_RUN_FIELDS = {
    "stage_id", "contract_ref", "status", "coverage_kind", "exercise_level", "consumed_materials",
    "produced_artifacts", "validator_evidence", "source_projection_boundary", "completion_claim",
    "stage_local_overlays",
}
BANNED_CLAIM_PHRASES = [
    "final paper complete",
    "final manuscript complete",
    "submission ready",
    "publication ready",
    "paper is complete",
    "ready to submit",
]
REQUIRED_ROUTES = [
    ("S09A", "S09B"),
    ("S09B", "S10"),
    ("S13", "S14"),
    ("S14", "S15"),
    ("S15", "S12"),
    ("S14", "S04"),
    ("S14", "S07"),
    ("S15", "S09B"),
]


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def rel_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_repo_ref(value: str | Path) -> Path:
    path = Path(str(value)).expanduser()
    if path.is_absolute():
        return path.resolve(strict=True)
    return (ROOT / path).resolve(strict=True)


def validate_run(
    run: dict[str, Any],
    stage: dict[str, Any],
    contract: dict[str, Any],
    pilot_root: Path,
    produced_artifact_refs_by_stage: dict[str, set[str]],
    expected_upstream_by_stage: dict[str, set[str]],
) -> list[str]:
    sid = stage["stage_id"]
    errors: list[str] = []
    missing = sorted(REQUIRED_RUN_FIELDS - set(run))
    if missing:
        errors.append(issue("E_PILOT_RUN_FIELD_MISSING", f"{sid} missing {missing}"))
    if run.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append(issue("E_PILOT_RUN_SCHEMA", f"{sid} bad schema_version"))
    if run.get("stage_id") != sid:
        errors.append(issue("E_PILOT_RUN_STAGE_ID", f"{sid} run has {run.get('stage_id')}"))
    if run.get("contract_ref") != stage.get("contract_ref"):
        errors.append(issue("E_PILOT_RUN_CONTRACT_REF", f"{sid} contract ref mismatch"))
    if run.get("coverage_kind") not in ALLOWED_COVERAGE_KINDS:
        errors.append(issue("E_PILOT_RUN_COVERAGE_KIND", f"{sid} {run.get('coverage_kind')}"))
    if run.get("exercise_level") not in ALLOWED_EXERCISE_LEVELS:
        errors.append(issue("E_PILOT_RUN_EXERCISE_LEVEL", f"{sid} {run.get('exercise_level')}"))
    if sid != "G02" and run.get("coverage_kind") == "owner_gated_deferred":
        errors.append(issue("E_PILOT_RUN_SPURIOUS_OWNER_GATE", f"{sid} owner-gated deferred only allowed for G02 in this pilot"))
    if sid == "G02" and run.get("exercise_level") != "deferred_with_gate":
        errors.append(issue("E_PILOT_RUN_G02_GATE", "G02 must be deferred_with_gate"))
    if run.get("coverage_kind") == "not_applicable_with_reason" and run.get("exercise_level") != "not_applicable":
        errors.append(issue("E_PILOT_RUN_NA_LEVEL", f"{sid} not_applicable coverage must have not_applicable level"))
    expected_overlays = contract.get("stage_local_overlays", [])
    run_overlays = run.get("stage_local_overlays")
    if run_overlays != [
        {
            "overlay_id": item.get("overlay_id"),
            "stage_id": item.get("stage_id", sid),
            "binding_strength": item.get("binding_strength"),
            "registry_ref": item.get("registry_ref", OVERLAY_REGISTRY_REF),
            "validator_ref": f"stage_overlay:{item.get('overlay_id')}:{item.get('stage_id', sid)}",
            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
        }
        for item in expected_overlays
        if isinstance(item, dict)
    ]:
        errors.append(issue("E_PILOT_RUN_STAGE_OVERLAY_LINK", f"{sid} stage_local_overlays mismatch"))
    if not isinstance(run_overlays, list) or not any(isinstance(item, dict) and item.get("overlay_id") == NATURE_OVERLAY_ID for item in run_overlays):
        errors.append(issue("E_PILOT_RUN_STAGE_OVERLAY_LINK", f"{sid} missing Nature overlay binding"))
    consumed = run.get("consumed_materials")
    if not isinstance(consumed, list) or not consumed:
        errors.append(issue("E_PILOT_RUN_CONSUMED_EMPTY", sid))
    elif not all(isinstance(item, dict) and item.get("material_id") and item.get("kind") and item.get("ref") for item in consumed):
        errors.append(issue("E_PILOT_RUN_CONSUMED_SHAPE", sid))
    else:
        actual_upstream_producers: set[str] = set()
        for item in consumed:
            ref = str(item["ref"])
            if item.get("kind") == "upstream_stage_output":
                producer_stage_id = item.get("producer_stage_id")
                if not isinstance(producer_stage_id, str) or not producer_stage_id:
                    errors.append(issue("E_PILOT_RUN_UPSTREAM_PRODUCER_MISSING", f"{sid} {ref}"))
                    continue
                actual_upstream_producers.add(producer_stage_id)
                if producer_stage_id not in expected_upstream_by_stage.get(sid, set()):
                    errors.append(issue("E_PILOT_RUN_UPSTREAM_PRODUCER_UNEXPECTED", f"{sid} producer={producer_stage_id}"))
                if item.get("material_id") != f"{producer_stage_id.lower()}_pilot_output":
                    errors.append(issue("E_PILOT_RUN_UPSTREAM_MATERIAL_ID", f"{sid} producer={producer_stage_id} material_id={item.get('material_id')}"))
                expected_refs = produced_artifact_refs_by_stage.get(producer_stage_id, set())
                ref_path = pilot_root / ref
                if ref not in expected_refs:
                    errors.append(issue("E_PILOT_RUN_UPSTREAM_REF_WRONG_PRODUCER", f"{sid} producer={producer_stage_id} ref={ref}"))
                if not is_inside(ref_path, pilot_root):
                    errors.append(issue("E_PILOT_RUN_UPSTREAM_REF_ESCAPE", f"{sid} {ref}"))
                if not ref_path.is_file():
                    errors.append(issue("E_PILOT_RUN_UPSTREAM_REF_MISSING", f"{sid} {ref}"))
        expected_producers = expected_upstream_by_stage.get(sid, set())
        if actual_upstream_producers != expected_producers:
            errors.append(issue("E_PILOT_RUN_UPSTREAM_PRODUCER_SET", f"{sid} expected={sorted(expected_producers)} actual={sorted(actual_upstream_producers)}"))
    produced = run.get("produced_artifacts")
    if not isinstance(produced, list) or not produced:
        errors.append(issue("E_PILOT_RUN_PRODUCED_EMPTY", sid))
    elif not all(isinstance(item, dict) and item.get("artifact_id") and item.get("artifact_type") and item.get("artifact_path") for item in produced):
        errors.append(issue("E_PILOT_RUN_PRODUCED_SHAPE", sid))
    else:
        for item in produced:
            artifact_path = pilot_root / str(item["artifact_path"])
            if not is_inside(artifact_path, pilot_root):
                errors.append(issue("E_PILOT_RUN_ARTIFACT_ESCAPE", f"{sid} {item['artifact_path']}"))
            if not artifact_path.is_file():
                errors.append(issue("E_PILOT_RUN_ARTIFACT_MISSING", f"{sid} {item['artifact_path']}"))
    validators = run.get("validator_evidence")
    if not isinstance(validators, list) or not validators:
        errors.append(issue("E_PILOT_RUN_VALIDATORS_EMPTY", sid))
    elif not any(item.get("status") == "pass" for item in validators if isinstance(item, dict)):
        errors.append(issue("E_PILOT_RUN_VALIDATORS_NO_PASS", sid))
    elif any(item.get("status") == "blocked" for item in validators if isinstance(item, dict)):
        errors.append(issue("E_PILOT_RUN_VALIDATORS_BLOCKED", sid))
    elif not any(item.get("validator") == "stage_local_overlay_binding" for item in validators if isinstance(item, dict)):
        errors.append(issue("E_PILOT_RUN_STAGE_OVERLAY_LINK", f"{sid} missing overlay validator evidence"))
    boundary = run.get("source_projection_boundary")
    if not isinstance(boundary, dict):
        errors.append(issue("E_PILOT_RUN_BOUNDARY_SHAPE", sid))
    else:
        expected = {
            "read_only_source": True,
            "writes_to_source_allowed": False,
            "runtime_output_under_source": False,
            "source_status_unchanged": True,
            "selected_source_fingerprints_unchanged": True,
        }
        for key, value in expected.items():
            if boundary.get(key) is not value:
                errors.append(issue("E_PILOT_RUN_BOUNDARY", f"{sid}.{key}={boundary.get(key)!r}"))
        if not isinstance(boundary.get("projection_scope"), str) or not boundary["projection_scope"].strip():
            errors.append(issue("E_PILOT_RUN_BOUNDARY_SCOPE", sid))
    completion_claim = str(run.get("completion_claim", "")).lower()
    if "pilot" not in completion_claim or "no final" not in completion_claim:
        errors.append(issue("E_PILOT_RUN_COMPLETION_BOUNDARY", f"{sid} completion claim must be pilot-only/no-final"))
    for phrase in BANNED_CLAIM_PHRASES:
        if phrase in completion_claim:
            errors.append(issue("E_PILOT_RUN_OVERCLAIM", f"{sid} banned phrase {phrase!r}"))
    packet = run.get("worker_task_packet_evidence")
    coverage = contract.get("worker_packet_coverage", {})
    if not isinstance(packet, dict):
        errors.append(issue("E_PILOT_RUN_WORKER_PACKET_SHAPE", sid))
    else:
        if packet.get("required") is not bool(contract.get("requires_worker_task_packet")):
            errors.append(issue("E_PILOT_RUN_WORKER_REQUIRED", sid))
        if packet.get("status") != coverage.get("status"):
            errors.append(issue("E_PILOT_RUN_WORKER_STATUS", f"{sid} {packet.get('status')} != {coverage.get('status')}"))
        if coverage.get("status") == "linked_strict_packet":
            ref = coverage.get("packet_ref")
            if packet.get("packet_ref") != ref or not isinstance(ref, str) or not (ROOT / ref).is_file():
                errors.append(issue("E_PILOT_RUN_WORKER_PACKET_LINK", f"{sid} {ref}"))
        if coverage.get("status") == "planned_with_blocker" and not packet.get("blocker"):
            errors.append(issue("E_PILOT_RUN_WORKER_BLOCKER", sid))
        if coverage.get("status") == "planned_with_blocker" and run.get("exercise_level") != "contract_only":
            errors.append(issue("E_PILOT_RUN_PLANNED_WORKER_LEVEL", f"{sid} planned worker packets must remain contract_only"))
        if coverage.get("status") == "linked_strict_packet" and run.get("exercise_level") != "full_stage_exercised":
            errors.append(issue("E_PILOT_RUN_LINKED_WORKER_LEVEL", f"{sid} linked strict packets should be full_stage_exercised"))
    return errors


def validate_graph(graph: dict[str, Any], expected_stage_ids: list[str]) -> list[str]:
    errors: list[str] = []
    node_ids = [str(node.get("id")) for node in graph.get("nodes", []) if isinstance(node, dict)]
    if sorted(node_ids) != sorted(expected_stage_ids):
        errors.append(issue("E_PILOT_GRAPH_NODE_SET", f"expected {expected_stage_ids}, got {node_ids}"))
    if "S09" in node_ids:
        errors.append(issue("E_PILOT_GRAPH_BARE_S09", "bare S09 node is forbidden; use S09A/S09B"))
    edge_pairs = {(str(edge.get("source")), str(edge.get("target"))) for edge in graph.get("edges", []) if isinstance(edge, dict)}
    canonical_edge_pairs = {(source, target) for source, target, _label in FLOW_EDGES}
    if edge_pairs != canonical_edge_pairs:
        missing = sorted(canonical_edge_pairs - edge_pairs)
        extra = sorted(edge_pairs - canonical_edge_pairs)
        errors.append(issue("E_PILOT_GRAPH_EDGE_SET", f"missing={missing} extra={extra}"))
    for source, target in REQUIRED_ROUTES:
        if (source, target) not in edge_pairs:
            errors.append(issue("E_PILOT_GRAPH_ROUTE_MISSING", f"{source}->{target}"))
    for source, target in edge_pairs:
        if source == "S09" or target == "S09":
            errors.append(issue("E_PILOT_GRAPH_BARE_S09_EDGE", f"{source}->{target}"))
    for node in graph.get("nodes", []):
        if isinstance(node, dict):
            overlays = node.get("stage_local_overlays")
            if not isinstance(overlays, list) or not any(isinstance(item, dict) and item.get("overlay_id") == NATURE_OVERLAY_ID for item in overlays):
                errors.append(issue("E_PILOT_GRAPH_STAGE_OVERLAY_LINK", str(node.get("id"))))
    return errors


def verify_pilot(pilot_root: Path = DEFAULT_PILOT) -> list[str]:
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    errors: list[str] = []
    required_files = [pilot_root / "manifest.json", pilot_root / "stage_coverage.json", pilot_root / "graph.json"]
    for path in required_files:
        if not path.is_file():
            errors.append(issue("E_PILOT_FILE_MISSING", rel_repo(path)))
    if errors:
        return errors
    registry = load_json(REGISTRY)
    manifest = load_json(pilot_root / "manifest.json")
    graph = load_json(pilot_root / "graph.json")
    expected_upstream_by_stage: dict[str, set[str]] = {}
    for source, target, _label in FLOW_EDGES:
        if source and target and source != "G01":
            expected_upstream_by_stage.setdefault(target, set()).add(source)
    if manifest.get("read_only_source") is not True:
        errors.append(issue("E_PILOT_MANIFEST_READ_ONLY", "manifest.read_only_source must be true"))
    if manifest.get("source_git_status_before") != manifest.get("source_git_status_after"):
        errors.append(issue("E_PILOT_MANIFEST_SOURCE_STATUS_DRIFT", "source git status changed during import"))
    if manifest.get("source_fingerprint_before") != manifest.get("source_fingerprint_after"):
        errors.append(issue("E_PILOT_MANIFEST_SOURCE_FINGERPRINT_DRIFT", "selected source fingerprints changed during import"))
    expected_stage_ids = list(registry.get("canonical_stage_ids", []))
    if "S09" in expected_stage_ids:
        errors.append(issue("E_STAGE_REGISTRY_BARE_S09", "canonical registry must not contain S09"))
    stages = registry.get("stages", [])
    if [stage.get("stage_id") for stage in stages] != expected_stage_ids:
        errors.append(issue("E_STAGE_REGISTRY_ORDER", "stages must match canonical_stage_ids order"))
    actual_run_paths = sorted((pilot_root / "stage-runs").glob("*.pilot-stage-run.json"))
    actual_stage_ids = [path.name.removesuffix(".pilot-stage-run.json") for path in actual_run_paths]
    if actual_stage_ids != sorted(expected_stage_ids):
        errors.append(issue("E_PILOT_RUN_SET", f"expected {sorted(expected_stage_ids)}, got {actual_stage_ids}"))
    loaded_runs: dict[str, dict[str, Any]] = {}
    produced_artifact_refs_by_stage: dict[str, set[str]] = {}
    for stage in stages:
        sid = stage["stage_id"]
        run_path = pilot_root / "stage-runs" / f"{sid}.pilot-stage-run.json"
        if run_path.is_file():
            run = load_json(run_path)
            loaded_runs[sid] = run
            produced = run.get("produced_artifacts", [])
            if isinstance(produced, list):
                for item in produced:
                    if isinstance(item, dict) and isinstance(item.get("artifact_path"), str):
                        produced_artifact_refs_by_stage.setdefault(sid, set()).add(item["artifact_path"])
    for stage in stages:
        sid = stage["stage_id"]
        contract_path = ROOT / stage["contract_ref"]
        if not contract_path.is_file():
            errors.append(issue("E_PILOT_CONTRACT_MISSING", stage["contract_ref"]))
            continue
        contract = load_json(contract_path)
        if not contract.get("completion_gate"):
            errors.append(issue("E_PILOT_CONTRACT_GATE_MISSING", sid))
        run_path = pilot_root / "stage-runs" / f"{sid}.pilot-stage-run.json"
        if not run_path.is_file():
            errors.append(issue("E_PILOT_RUN_MISSING", sid))
            continue
        run = loaded_runs.get(sid) or load_json(run_path)
        errors.extend(validate_run(run, stage, contract, pilot_root, produced_artifact_refs_by_stage, expected_upstream_by_stage))
    summary = load_json(pilot_root / "stage_coverage.json")
    if summary.get("schema_version") != SUMMARY_SCHEMA_VERSION:
        errors.append(issue("E_PILOT_SUMMARY_SCHEMA", str(summary.get("schema_version"))))
    if summary.get("pilot_stage_run_count") != len(expected_stage_ids):
        errors.append(issue("E_PILOT_SUMMARY_COUNT", f"{summary.get('pilot_stage_run_count')} != {len(expected_stage_ids)}"))
    if len(summary.get("stage_runs", [])) != len(expected_stage_ids):
        errors.append(issue("E_PILOT_SUMMARY_RUNS", "stage_runs length mismatch"))
    if summary.get("stage_overlay_registry_ref") != OVERLAY_REGISTRY_REF or summary.get("active_stage_overlays") != [NATURE_OVERLAY_ID]:
        errors.append(issue("E_PILOT_SUMMARY_STAGE_OVERLAY_LINK", "summary missing Nature overlay registry link"))
    if summary.get("stage_overlay_binding_counts", {}).get("nature_bound") != len(expected_stage_ids):
        errors.append(issue("E_PILOT_SUMMARY_STAGE_OVERLAY_LINK", f"stage_overlay_binding_counts={summary.get('stage_overlay_binding_counts')}"))
    for item in summary.get("stage_runs", []):
        if isinstance(item, dict):
            overlays = item.get("stage_local_overlays")
            if not isinstance(overlays, list) or not any(isinstance(overlay, dict) and overlay.get("overlay_id") == NATURE_OVERLAY_ID for overlay in overlays):
                errors.append(issue("E_PILOT_SUMMARY_STAGE_OVERLAY_LINK", str(item.get("stage_id"))))
    if "all canonical stages" not in str(summary.get("completion_boundary", "")).lower() or "not a final" not in str(summary.get("completion_boundary", "")).lower():
        errors.append(issue("E_PILOT_SUMMARY_COMPLETION_BOUNDARY", "summary completion boundary must be explicit"))
    errors.extend(validate_graph(graph, expected_stage_ids))
    # Negative local-copy mutation probes: output path must not escape via traversal or source-root containment.
    source_root = resolve_repo_ref(str(manifest.get("source_root", "")))
    output_root = resolve_repo_ref(str(manifest.get("runtime_output_root", pilot_root)))
    if source_root and output_root:
        try:
            if output_root.resolve().is_relative_to(source_root.resolve()):
                errors.append(issue("E_PILOT_OUTPUT_UNDER_SOURCE", f"{output_root} under {source_root}"))
        except OSError:
            errors.append(issue("E_PILOT_OUTPUT_PATH_RESOLVE", str(output_root)))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Phase9 local-paper full-stage PilotStageRun coverage.")
    parser.add_argument("pilot_root", nargs="?", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args(argv)
    errors = verify_pilot(args.pilot_root)
    if errors:
        print("INVALID local paper full pilot", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE9_LOCAL_PAPER_FULL_PILOT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
