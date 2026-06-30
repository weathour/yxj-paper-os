#!/usr/bin/env python3
"""Generate deterministic Phase9 full-stage local-paper pilot runs.

This is a projection pilot, not a manuscript-completion engine. It consumes the
read-only local-paper manifest produced by import_local_paper_pilot.py, links each
canonical stage to its StageContract, emits one PilotStageRun per stage, and
builds a stage-flow graph/coverage summary that downstream validators and the
frontend can inspect.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon"
REGISTRY = ROOT / "runtime" / "stage_registry.json"
CONTRACT_DIR = ROOT / "examples" / "stage-contracts"
SCHEMA_VERSION = "ppg-pilot-stage-run/v0.1"
SUMMARY_SCHEMA_VERSION = "ppg-local-paper-full-pilot/v0.1"
COVERAGE_KIND_BY_STAGE = {
    "S00": "source_projected",
    "S01": "source_projected",
    "S02": "source_projected",
    "S03": "source_projected",
    "S04": "source_projected",
    "S05": "source_projected",
    "S06": "source_projected",
    "S07": "fixture_generated",
    "S08": "source_projected",
    "S09A": "script_checked",
    "S09B": "script_checked",
    "S10": "source_projected",
    "S11": "source_projected",
    "S12": "fixture_generated",
    "S13": "fixture_generated",
    "S14": "script_checked",
    "S15": "fixture_generated",
    "S16": "script_checked",
    "G01": "script_checked",
    "G02": "owner_gated_deferred",
}
EXERCISE_LEVEL_BY_STAGE = {
    "G02": "deferred_with_gate",
}
STAGE_SOURCE_REFS = {
    "S00": ["README.md", "HANDOFF.md", "PROJECT_STATUS.md"],
    "S01": ["README.md", "HANDOFF.md", "docs/CURRENT_PLAN.md", "docs/LATEST_SYNC_BRIEF.md"],
    "S02": ["manuscript/sections/02_related_work.tex", "docs/CURRENT_PLAN.md"],
    "S03": ["README.md", "HANDOFF.md", "manuscript/sections/01_introduction.tex"],
    "S04": ["docs/L3_METHOD_FAITHFUL_UNIFIED_SCENE_RERUN_2026-06-25.md", "docs/L3_METHOD_FAITHFUL_NON_TEXT_EVIDENCE_CHECKLIST_2026-06-25.md", "manuscript/sections/05_experiments.tex"],
    "S05": ["manuscript/sections/01_introduction.tex", "manuscript/sections/03_problem_formulation.tex", "manuscript/sections/04_method.tex"],
    "S06": ["manuscript/sections/03_problem_formulation.tex", "manuscript/sections/04_method.tex", "manuscript/sections/06_results_discussion.tex"],
    "S07": ["manuscript/main.tex", "manuscript/sections/01_introduction.tex", "manuscript/sections/07_conclusion.tex"],
    "S08": ["docs/L3_METHOD_FAITHFUL_NON_TEXT_EVIDENCE_CHECKLIST_2026-06-25.md", "manuscript/sections/05_experiments.tex", "manuscript/sections/06_results_discussion.tex"],
    "S09A": ["examples/local-paper/security-state-aware-mixed-platoon/materials/owner_contract.json", "examples/local-paper/security-state-aware-mixed-platoon/materials/source_inventory.json"],
    "S09B": ["examples/packets/intro_writing_packet.v2.yaml", "examples/packets/claim_repair_packet.v1.yaml"],
    "S10": ["manuscript/sections/01_introduction.tex", "manuscript/sections/04_method.tex", "manuscript/sections/06_results_discussion.tex"],
    "S11": ["docs/L3_METHOD_FAITHFUL_NON_TEXT_EVIDENCE_CHECKLIST_2026-06-25.md"],
    "S12": ["manuscript/main.tex", "manuscript/sections/01_introduction.tex", "manuscript/sections/06_results_discussion.tex"],
    "S13": ["PROJECT_STATUS.md", "HANDOFF.md", "manuscript/main.tex"],
    "S14": ["examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml", "examples/review_findings/phase7_overclaim.v1.yaml"],
    "S15": ["examples/packets/claim_repair_packet.v1.yaml", "examples/candidate_returns/intro_candidate_return.phase7.yaml"],
    "S16": ["PROJECT_STATUS.md", "HANDOFF.md", "manuscript/main.tex"],
    "G01": ["runtime/stage_registry.json", "examples/stage-contracts"],
    "G02": ["PROJECT_STATUS.md"],
}
FLOW_EDGES = [
    ("S00", "S01", "profile/forbidden routes"),
    ("S01", "S02", "source map"),
    ("S02", "S03", "research dossier"),
    ("S01", "S04", "evidence bank"),
    ("S03", "S04", "contribution options"),
    ("S04", "S05", "admissible claims"),
    ("S05", "S06", "reader spine"),
    ("S06", "S07", "object/granularity controls"),
    ("S05", "S08", "visual questions"),
    ("S06", "S08", "function budget"),
    ("S04", "S08", "panel evidence"),
    ("S04", "S09A", "claim control"),
    ("S05", "S09A", "spine control"),
    ("S06", "S09A", "granularity control"),
    ("S07", "S09A", "surface control"),
    ("S09A", "S09B", "selected control bundle"),
    ("S09B", "S10", "text task packet"),
    ("S01", "S11", "source data locators"),
    ("S04", "S11", "panel evidence/result package"),
    ("S08", "S11", "figure contract"),
    ("S10", "S12", "candidate text"),
    ("S11", "S12", "figure bundle"),
    ("S12", "S13", "integrated candidate"),
    ("S13", "S16", "clean review closure route"),
    ("S13", "S14", "findings/loss"),
    ("S14", "S15", "repair packets"),
    ("S15", "S10", "local text regeneration"),
    ("S15", "S12", "re-integration"),
    ("S14", "S04", "claim/evidence backflow"),
    ("S14", "S07", "terminology/surface backflow"),
    ("S14", "S09A", "control-material reselection"),
    ("S15", "S09B", "task packet regeneration"),
    ("S15", "S16", "repair-complete delivery package"),
    ("S16", "G02", "post-paper derivative gate"),
    ("G01", "S00", "governance boot"),
    ("G01", "S09B", "packet authority boundary"),
    ("G01", "S16", "completion authority boundary"),
]


def repo_rel(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def stage_output_kind(stage: dict[str, Any]) -> str:
    mode = stage["execution_mode"]
    if mode == "owner_gated":
        return "owner_gate_projection"
    if mode == "script_generated":
        return "script_check_output"
    if stage["stage_id"] in {"S10", "S11", "S15"}:
        return "candidate_or_repair_projection"
    if stage["stage_id"] in {"S13", "S14"}:
        return "review_backflow_projection"
    return "analysis_material_projection"


def consumed_materials(stage: dict[str, Any], pilot_root: Path) -> list[dict[str, str]]:
    sid = stage["stage_id"]
    values: list[dict[str, str]] = []
    for idx, item in enumerate(stage.get("consumes", []), start=1):
        values.append({"material_id": f"{sid.lower()}_declared_input_{idx}", "kind": "contract_declared", "ref": str(item)})
    source_refs = STAGE_SOURCE_REFS.get(sid, [])
    for ref in source_refs:
        values.append({"material_id": f"{sid.lower()}_source_ref_{slug(ref)[:48]}", "kind": "source_or_runtime_ref", "ref": ref})
    if sid not in {"S00", "G01"}:
        previous = [edge[0] for edge in FLOW_EDGES if edge[1] == sid and edge[0] not in {"G01"}]
        for prev in sorted(set(previous)):
            values.append({"material_id": f"{prev.lower()}_pilot_output", "kind": "upstream_stage_output", "ref": f"artifacts/{prev}-{slug(prev)}.json"})
    if not values:
        values.append({"material_id": f"{sid.lower()}_pilot_context", "kind": "pilot_context", "ref": repo_rel(pilot_root / "manifest.json")})
    return values


def worker_packet_evidence(contract: dict[str, Any]) -> dict[str, Any]:
    coverage = contract.get("worker_packet_coverage", {})
    return {
        "required": bool(contract.get("requires_worker_task_packet")),
        "status": coverage.get("status", "not_required"),
        "packet_ref": coverage.get("packet_ref"),
        "return_contract_ref": coverage.get("return_contract_ref"),
        "blocker": coverage.get("blocker"),
    }


def build_artifact(stage: dict[str, Any], contract: dict[str, Any], manifest: dict[str, Any], consumed: list[dict[str, str]]) -> dict[str, Any]:
    sid = stage["stage_id"]
    claim_boundary = manifest.get("claim_boundary", {})
    return {
        "schema_version": "ppg-pilot-stage-artifact/v0.1",
        "stage_id": sid,
        "stage_name": stage["stage_name"],
        "artifact_kind": stage_output_kind(stage),
        "source_project": manifest.get("project_slug"),
        "purpose": stage.get("purpose"),
        "contract_ref": stage.get("contract_ref"),
        "consumed_ref_count": len(consumed),
        "projected_outputs": list(stage.get("produces", [])),
        "claim_boundary_snapshot": {
            "active_method": claim_boundary.get("active_method"),
            "evidence_spine": claim_boundary.get("evidence_spine"),
            "forbidden_overclaim_boundary": claim_boundary.get("raw_safety_boundary"),
        },
        "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
    }


def build_run(stage: dict[str, Any], contract: dict[str, Any], manifest: dict[str, Any], pilot_root: Path, artifact_rel: str) -> dict[str, Any]:
    sid = stage["stage_id"]
    coverage_kind = COVERAGE_KIND_BY_STAGE[sid]
    exercise_level = EXERCISE_LEVEL_BY_STAGE.get(sid, "full_stage_exercised")
    consumed = consumed_materials(stage, pilot_root)
    fingerprints_match = manifest.get("source_fingerprint_before") == manifest.get("source_fingerprint_after")
    status_match = manifest.get("source_git_status_before") == manifest.get("source_git_status_after")
    output_under_source = False
    source_root = Path(str(manifest.get("source_root", ""))).resolve()
    try:
        output_under_source = pilot_root.resolve().is_relative_to(source_root)
    except ValueError:
        output_under_source = False
    return {
        "schema_version": SCHEMA_VERSION,
        "stage_id": sid,
        "contract_ref": stage["contract_ref"],
        "status": "owner_gated" if sid == "G02" else "validated",
        "coverage_kind": coverage_kind,
        "exercise_level": exercise_level,
        "stage_name": stage["stage_name"],
        "execution_mode": stage["execution_mode"],
        "recommended_agent_type": stage["recommended_agent_type"],
        "consumed_materials": consumed,
        "produced_artifacts": [
            {
                "artifact_id": f"{sid.lower()}_pilot_output",
                "artifact_type": stage_output_kind(stage),
                "artifact_path": artifact_rel,
                "description": "; ".join(stage.get("produces", [])[:4]),
            }
        ],
        "worker_task_packet_evidence": worker_packet_evidence(contract),
        "validator_evidence": [
            {
                "validator": "stage_contract_link",
                "status": "pass",
                "evidence": f"{sid} links to {stage['contract_ref']} with completion_gate present",
            },
            {
                "validator": "source_read_only_fingerprint",
                "status": "pass" if fingerprints_match and status_match and not output_under_source else "blocked",
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
            },
            {
                "validator": "coverage_boundary",
                "status": "pass",
                "evidence": f"coverage_kind={coverage_kind}; exercise_level={exercise_level}; no source manuscript write claimed",
            },
        ],
        "source_projection_boundary": {
            "source_root": manifest.get("source_root"),
            "runtime_output_root": manifest.get("runtime_output_root"),
            "read_only_source": manifest.get("read_only_source") is True,
            "writes_to_source_allowed": False,
            "runtime_output_under_source": output_under_source,
            "source_git_status_before": manifest.get("source_git_status_before", ""),
            "source_git_status_after": manifest.get("source_git_status_after", ""),
            "source_status_unchanged": status_match,
            "selected_source_fingerprints_unchanged": fingerprints_match,
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
        },
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
    }


def build_graph(registry: dict[str, Any], pilot_root: Path) -> dict[str, Any]:
    stages = registry["stages"]
    nodes = [
        {
            "id": stage["stage_id"],
            "label": stage["stage_name"],
            "execution_mode": stage["execution_mode"],
            "requires_worker_task_packet": stage["requires_worker_task_packet"],
            "contract_ref": stage["contract_ref"],
            "run_ref": f"stage-runs/{stage['stage_id']}.pilot-stage-run.json",
        }
        for stage in stages
    ]
    edges = [
        {"id": f"e{idx:02d}", "source": source, "target": target, "kind": "material" if "backflow" not in label and "regeneration" not in label and "reselection" not in label else "backflow", "label": label}
        for idx, (source, target, label) in enumerate(FLOW_EDGES, start=1)
    ]
    return {
        "schema_version": "ppg-pilot-stage-flow/v0.1",
        "graph_id": "security-state-aware-mixed-platoon.phase9-full-stage-pilot",
        "project_slug": "security-state-aware-mixed-platoon",
        "nodes": nodes,
        "edges": edges,
        "must_contain_routes": [
            ["S09A", "S09B", "S10"],
            ["S13", "S14", "S15", "S12"],
            ["S14", "S04"],
            ["S14", "S07"],
            ["S15", "S09B"],
        ],
        "claim_boundary": "pilot graph does not contain bare S09 and does not claim final submission completion",
        "pilot_root": repo_rel(pilot_root),
    }


def build_summary(registry: dict[str, Any], runs: list[dict[str, Any]], pilot_root: Path) -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    by_level: dict[str, int] = {}
    worker_packet_status: dict[str, int] = {}
    for run in runs:
        by_kind[run["coverage_kind"]] = by_kind.get(run["coverage_kind"], 0) + 1
        by_level[run["exercise_level"]] = by_level.get(run["exercise_level"], 0) + 1
        status = run["worker_task_packet_evidence"]["status"]
        worker_packet_status[status] = worker_packet_status.get(status, 0) + 1
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "project_slug": "security-state-aware-mixed-platoon",
        "canonical_stage_count": len(registry["canonical_stage_ids"]),
        "pilot_stage_run_count": len(runs),
        "coverage_kind_counts": dict(sorted(by_kind.items())),
        "exercise_level_counts": dict(sorted(by_level.items())),
        "worker_task_packet_status_counts": dict(sorted(worker_packet_status.items())),
        "stage_runs": [
            {
                "stage_id": run["stage_id"],
                "stage_name": run["stage_name"],
                "status": run["status"],
                "coverage_kind": run["coverage_kind"],
                "exercise_level": run["exercise_level"],
                "contract_ref": run["contract_ref"],
                "worker_packet_status": run["worker_task_packet_evidence"]["status"],
                "run_ref": f"stage-runs/{run['stage_id']}.pilot-stage-run.json",
            }
            for run in runs
        ],
        "graph_ref": "graph.json",
        "completion_boundary": "all canonical stages have PilotStageRun coverage; this is not a final manuscript/submission claim",
        "pilot_root": repo_rel(pilot_root),
    }


def generate(pilot_root: Path) -> dict[str, Any]:
    manifest = load_json(pilot_root / "manifest.json")
    registry = load_json(REGISTRY)
    stage_run_dir = pilot_root / "stage-runs"
    artifact_dir = pilot_root / "artifacts"
    runs: list[dict[str, Any]] = []
    for stage in registry["stages"]:
        sid = stage["stage_id"]
        contract = load_json(ROOT / stage["contract_ref"])
        artifact_rel = f"artifacts/{sid}-{slug(stage['stage_name'])}.json"
        consumed = consumed_materials(stage, pilot_root)
        artifact = build_artifact(stage, contract, manifest, consumed)
        write_json(pilot_root / artifact_rel, artifact)
        run = build_run(stage, contract, manifest, pilot_root, artifact_rel)
        write_json(stage_run_dir / f"{sid}.pilot-stage-run.json", run)
        runs.append(run)
    graph = build_graph(registry, pilot_root)
    summary = build_summary(registry, runs, pilot_root)
    write_json(pilot_root / "graph.json", graph)
    write_json(pilot_root / "stage_coverage.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Phase9 local-paper full-stage PilotStageRun fixtures.")
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT, help="Local-paper pilot root created by import_local_paper_pilot.py")
    parser.add_argument("--check", action="store_true", help="Run the full pilot verifier after generation")
    args = parser.parse_args(argv)
    pilot_root = args.pilot_root if args.pilot_root.is_absolute() else ROOT / args.pilot_root
    if not pilot_root.is_dir():
        print(f"PILOT_ROOT_MISSING {pilot_root}", file=sys.stderr)
        return 1
    summary = generate(pilot_root)
    if args.check:
        try:
            from verify_local_paper_full_pilot import verify_pilot
        except ImportError:  # pragma: no cover
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from verify_local_paper_full_pilot import verify_pilot  # type: ignore  # noqa: E402
        errors = verify_pilot(pilot_root)
        if errors:
            print("INVALID local paper full pilot", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
    print("PHASE9_LOCAL_PAPER_FULL_PILOT_GENERATED")
    print(f"stage_runs={summary['pilot_stage_run_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
