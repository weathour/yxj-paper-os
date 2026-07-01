#!/usr/bin/env python3
"""Verify the runtime viewer embeds the Phase9 stage coverage fixture safely."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "docs" / "runtime-viewer" / "runtime-graph-data.js"
APP_JS = ROOT / "docs" / "runtime-viewer" / "app.js"
COVERAGE_JSON = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon" / "stage_coverage.json"
PILOT_ROOT = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon"


def run_node(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True, check=False)


def build_expected_stage_details(coverage: dict) -> dict:
    run_by_id = {}
    for item in coverage["stage_runs"]:
        run_path = PILOT_ROOT / item["run_ref"]
        run = json.loads(run_path.read_text(encoding="utf-8"))
        run_by_id[run["stage_id"]] = run

    details = {}
    for item in coverage["stage_runs"]:
        sid = item["stage_id"]
        run = run_by_id[sid]
        contract = json.loads((ROOT / run["contract_ref"]).read_text(encoding="utf-8"))
        artifacts = []
        for artifact_ref in run.get("produced_artifacts", []):
            artifact = dict(artifact_ref)
            artifact_path = artifact_ref.get("artifact_path")
            full_path = PILOT_ROOT / artifact_path if artifact_path else None
            if full_path and full_path.exists():
                payload = json.loads(full_path.read_text(encoding="utf-8"))
                artifact["payload"] = {
                    "artifact_kind": payload.get("artifact_kind"),
                    "purpose": payload.get("purpose"),
                    "projected_outputs": payload.get("projected_outputs", []),
                    "consumed_ref_count": payload.get("consumed_ref_count"),
                    "claim_boundary_snapshot": payload.get("claim_boundary_snapshot"),
                    "pilot_note": payload.get("pilot_note"),
                    "stage_local_overlays": payload.get("stage_local_overlays", []),
                }
            artifacts.append(artifact)
        upstream_inputs = [m for m in run.get("consumed_materials", []) if m.get("kind") == "upstream_stage_output"]
        declared_inputs = [m for m in run.get("consumed_materials", []) if m.get("kind") == "contract_declared"]
        source_refs = [m for m in run.get("consumed_materials", []) if m.get("kind") == "source_or_runtime_ref"]
        consumers = []
        for other_id, other in run_by_id.items():
            if other_id == sid:
                continue
            for mat in other.get("consumed_materials", []):
                if mat.get("kind") == "upstream_stage_output" and mat.get("producer_stage_id") == sid:
                    consumers.append({
                        "stage_id": other_id,
                        "stage_name": other.get("stage_name"),
                        "material_id": mat.get("material_id"),
                        "ref": mat.get("ref"),
                    })
        details[sid] = {
            "stage_id": sid,
            "stage_name": run.get("stage_name"),
            "status": run.get("status"),
            "coverage_kind": run.get("coverage_kind"),
            "exercise_level": run.get("exercise_level"),
            "execution_mode": run.get("execution_mode"),
            "recommended_agent_type": run.get("recommended_agent_type"),
            "contract_ref": run.get("contract_ref"),
            "completion_claim": run.get("completion_claim"),
            "contract": {
                "purpose": contract.get("purpose"),
                "activation_policy": contract.get("activation_policy"),
                "completion_gate": contract.get("completion_gate"),
                "consumes": contract.get("consumes", []),
                "produces": contract.get("produces", []),
                "validators": contract.get("validators", []),
                "backflow_targets": contract.get("backflow_targets", []),
                "requires_worker_task_packet": contract.get("requires_worker_task_packet"),
                "worker_packet_coverage": contract.get("worker_packet_coverage"),
                "subagent_lane_policy": contract.get("subagent_lane_policy"),
                "worker_authority_boundary": contract.get("worker_authority_boundary"),
            },
            "consumed_materials": run.get("consumed_materials", []),
            "declared_inputs": declared_inputs,
            "upstream_inputs": upstream_inputs,
            "source_refs": source_refs,
            "produced_artifacts": artifacts,
            "handoff_consumers": consumers,
            "validator_evidence": run.get("validator_evidence", []),
            "worker_task_packet_evidence": run.get("worker_task_packet_evidence"),
            "stage_local_overlays": run.get("stage_local_overlays", []),
            "source_projection_boundary": run.get("source_projection_boundary"),
        }
    return details


def main() -> int:
    expected = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    expected_details = build_expected_stage_details(expected)
    script = r"""
const fs = require('fs');
global.window = {};
require(process.cwd() + '/docs/runtime-viewer/runtime-graph-data.js');
const payload = {
  stageCoverage: global.window.PPG_RUNTIME_GRAPH.stageCoverage,
  stageRunDetails: global.window.PPG_RUNTIME_GRAPH.stageRunDetails
};
process.stdout.write(JSON.stringify(payload));
"""
    result = run_node(script)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    embedded = json.loads(result.stdout)
    if embedded.get("stageCoverage") != expected:
        print("PHASE9_FRONTEND_STAGE_COVERAGE_DRIFT", file=sys.stderr)
        return 1
    if embedded.get("stageRunDetails") != expected_details:
        print("PHASE9_FRONTEND_STAGE_RUN_DETAILS_DRIFT", file=sys.stderr)
        return 1
    app_text = APP_JS.read_text(encoding="utf-8")
    if "stageCoverageContent.innerHTML" in app_text:
        print("PHASE9_STAGE_COVERAGE_UNSAFE_INNERHTML", file=sys.stderr)
        return 1
    if "stageWorkbenchContent.innerHTML" in app_text:
        print("PHASE9_STAGE_WORKBENCH_UNSAFE_INNERHTML", file=sys.stderr)
        return 1
    required_snippets = [
        "stageCoverageContent.textContent",
        "renderStageCoverage",
        "stageCoverageMode",
        "stageWorkbenchContent.textContent",
        "renderStageWorkbench",
        "stageWorkbenchMode",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in app_text]
    if missing:
        print(f"PHASE9_STAGE_COVERAGE_UI_SNIPPETS_MISSING {missing}", file=sys.stderr)
        return 1
    print("PHASE9_FRONTEND_STAGE_COVERAGE_SYNC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
