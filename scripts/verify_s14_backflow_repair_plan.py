#!/usr/bin/env python3
"""Verify S14 nearest-responsible backflow repair plan."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, NoReturn

try:
    from ppg_validate_common import load_document
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_MATERIAL = ROOT / "scripts" / "validate_material.py"
MATERIAL = ROOT / "examples/materials/phase10_s14_backflow_repair_plan.json"
PUBLIC_CONSUMES = [
    "accepted S13/S16/validator findings",
    "validator reports",
    "affected material graph slice",
    "owner gate policy",
]
PUBLIC_PRODUCES = [
    "normalized backflow repair plan",
    "nearest responsible stage map",
    "bounded repair task plan",
    "response action map",
]
REQUIRED_SCHEMA_FIELDS = {
    "schema_version",
    "stage_id",
    "completion_boundary",
    "authority_boundary",
    "finding_intake_ledger",
    "finding_normalization_table",
    "nearest_responsible_stage_map",
    "affected_material_graph_slice",
    "repair_scope_plan",
    "repair_task_packets",
    "control_reselection_tasks",
    "response_action_map",
    "priority_schedule",
    "owner_gate_report",
    "validation_plan",
    "unresolved_or_ambiguous_findings",
    "validator_report",
    "remaining_risks",
}
REQUIRED_REGISTRY_VALIDATORS = {
    "S14_finding_intake_coverage",
    "S14_duplicate_and_rejection_reason",
    "S14_failure_type_classification",
    "S14_nearest_responsible_stage",
    "S14_no_bare_S09_route",
    "S14_repair_locality",
    "S14_affected_downstream_nodes",
    "S14_protected_unrelated_nodes",
    "S14_owner_gate_status",
    "S14_task_packet_compile",
    "S14_no_execution",
    "S14_no_completion_claim",
}
REQUIRED_DIMS = {
    "s14_finding_intake_coverage",
    "s14_failure_type_classification",
    "s14_nearest_responsible_stage",
    "s14_repair_locality",
    "s14_owner_gate_status",
    "s14_task_response_validation_plan",
    "s14_no_execution_completion",
    "s14_nature_overlay",
}
NEGATIVES = {
    "invalid-s14-backflow-plan-missing-intake-ledger.json": "E_S14_FINDING_INTAKE_REQUIRED",
    "invalid-s14-backflow-plan-intake-coverage-gap.json": "E_S14_FINDING_INTAKE_COVERAGE",
    "invalid-s14-backflow-plan-invalid-failure-type.json": "E_S14_FAILURE_TYPE_REQUIRED",
    "invalid-s14-backflow-plan-bare-s09-route.json": "E_S14_NO_BARE_S09_ROUTE",
    "invalid-s14-backflow-plan-missing-route-rationale.json": "E_S14_NEAREST_STAGE_REQUIRED",
    "invalid-s14-backflow-plan-missing-stale-nodes.json": "E_S14_AFFECTED_GRAPH_REQUIRED",
    "invalid-s14-backflow-plan-global-rewrite-scope.json": "E_S14_REPAIR_LOCALITY_REQUIRED",
    "invalid-s14-backflow-plan-task-executed.json": "E_S14_NO_REPAIR_EXECUTION",
    "invalid-s14-backflow-plan-missing-task-for-finding.json": "E_S14_TASK_COMPILATION_REQUIRED",
    "invalid-s14-backflow-plan-response-missing-evidence.json": "E_S14_RESPONSE_ACTION_REQUIRED",
    "invalid-s14-backflow-plan-owner-gate-disabled.json": "E_S14_OWNER_GATE_REQUIRED",
    "invalid-s14-backflow-plan-validation-missing-stale.json": "E_S14_VALIDATION_PLAN_REQUIRED",
    "invalid-s14-backflow-plan-completion-overclaim.json": "E_S14_NO_COMPLETION_OVERCLAIM",
    "invalid-s14-backflow-plan-authority-repair-executed.json": "E_S14_AUTHORITY_BOUNDARY_REQUIRED",
}


def fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_doc(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        fail("E_S14_DOC_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        fail("E_S14_DOC_LOAD", f"{path}: root must be mapping")
    return data


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def verify_fixtures() -> None:
    result = run([sys.executable, str(VALIDATE_MATERIAL), str(MATERIAL)])
    if result.returncode != 0:
        fail("E_S14_POSITIVE", result.stdout)
    for name, expected_code in NEGATIVES.items():
        path = ROOT / "examples/materials" / name
        result = run([sys.executable, str(VALIDATE_MATERIAL), str(path)])
        if result.returncode == 0 or expected_code not in result.stdout:
            fail("E_S14_NEGATIVE", f"{name} expected {expected_code}, got\n{result.stdout}")


def verify_schema_material() -> None:
    props = load_json(ROOT / "schemas/ppg-material-payloads.schema.json")["properties"]
    if "S14BackflowRepairPlan" not in props:
        fail("E_S14_SCHEMA", "missing S14BackflowRepairPlan")
    missing = REQUIRED_SCHEMA_FIELDS - set(props["S14BackflowRepairPlan"].get("required", []))
    if missing:
        fail("E_S14_SCHEMA", f"missing {sorted(missing)}")
    material = load_json(MATERIAL)
    payload = material["payload"]
    if payload["authority_boundary"].get("fake_worker_task_packet_created") is not False:
        fail("E_S14_FAKE_PACKET", "S14 must not fake worker task packets")
    accepted = set(payload["finding_intake_ledger"]["accepted_finding_ids"])
    task_findings = {item["finding_id"] for item in payload["repair_task_packets"]}
    route_findings = {item["finding_id"] for item in payload["nearest_responsible_stage_map"]}
    if accepted - task_findings or accepted - route_findings:
        fail("E_S14_COVERAGE", "accepted findings must have route and task plan")
    if any(item.get("target_stage") == "S09" for item in payload["nearest_responsible_stage_map"]):
        fail("E_S14_NO_BARE_S09", "bare S09 route found")
    if any(task.get("repair_executed") is not False for task in payload["repair_task_packets"]):
        fail("E_S14_NO_EXECUTION", "repair task must be plan-only")


def verify_registry_phase() -> None:
    registry = load_json(ROOT / "runtime/stage_registry.json")
    s14 = {s["stage_id"]: s for s in registry["stages"]}["S14"]
    if s14["requires_worker_task_packet"] is not False:
        fail("E_S14_WORKER_PACKET", "S14 must remain no-worker-packet controller/planner stage")
    if s14["consumes"] != PUBLIC_CONSUMES or s14["produces"] != PUBLIC_PRODUCES:
        fail("E_S14_IO", "public IO drift")
    missing_validators = REQUIRED_REGISTRY_VALIDATORS - set(s14.get("validators", []))
    if missing_validators:
        fail("E_S14_VALIDATORS", f"missing {sorted(missing_validators)}")
    contract = load_json(ROOT / "examples/stage-contracts/S14.stage-contract.json")
    for key in ["consumes", "produces", "validators", "completion_gate", "coverage_status", "requires_worker_task_packet"]:
        if contract.get(key) != s14.get(key):
            fail("E_S14_CONTRACT", f"mismatch {key}")
    phase = load_json(ROOT / "runtime/phase10_content_validators.json")
    validator = {v["stage_id"]: v for v in phase["validators"]}["S14"]
    dims = {d["dimension_id"] for d in validator["dimensions"]}
    missing_dims = REQUIRED_DIMS - dims
    if missing_dims:
        fail("E_S14_PHASE", f"missing dims {sorted(missing_dims)}")
    checks = set(validator["required_checks"])
    missing_checks = {item.lower() for item in REQUIRED_REGISTRY_VALIDATORS} - checks
    if missing_checks:
        fail("E_S14_PHASE", f"missing checks {sorted(missing_checks)}")


def main() -> int:
    verify_fixtures()
    verify_schema_material()
    verify_registry_phase()
    print("PPG_S14_BACKFLOW_REPAIR_PLAN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
