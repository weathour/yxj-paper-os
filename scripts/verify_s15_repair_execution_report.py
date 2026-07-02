#!/usr/bin/env python3
"""Verify S15 scoped repair execution and local regeneration."""
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
VALIDATE_PACKET = ROOT / "scripts" / "validate_packet.py"
VALIDATE_RETURN = ROOT / "scripts" / "validate_candidate_return.py"
PACKET = ROOT / "examples/packets/phase10_s15_scoped_repair_packet.v1.yaml"
MATERIAL = ROOT / "examples/materials/phase10_s15_repair_execution_report.json"
RETURN = ROOT / "examples/candidate_returns/phase10_s15_repair_execution_report_return.json"
PUBLIC_CONSUMES = [
    "strict S14 repair task packet",
    "target material base version",
    "affected downstream stale set",
    "protected unrelated node list",
]
PUBLIC_PRODUCES = [
    "repair execution report",
    "revised material candidate",
    "regenerated affected outputs",
    "updated validator report",
]
REQUIRED_SCHEMA_FIELDS = {
    "schema_version", "stage_id", "completion_boundary", "authority_boundary", "repair_task_ack",
    "pre_repair_snapshot", "target_material_diff", "revised_material_candidate", "regenerated_task_packets",
    "regenerated_text_or_figure_candidates", "affected_downstream_regeneration_log", "stale_resolution_report",
    "unrelated_node_preservation_report", "finding_resolution_evidence", "updated_validator_report",
    "new_risk_scan", "candidate_artifact_return", "missing_material_report", "verifier_evidence", "remaining_risks",
}
REQUIRED_PACKET_FIELDS = {
    "s15_repair_task", "repair_scope", "pre_repair_snapshot_requirements", "affected_downstream_set",
    "protected_unrelated_nodes", "diff_locality_requirements", "finding_resolution_requirements",
    "regression_scan_requirements",
}
REQUIRED_REGISTRY_VALIDATORS = {
    "S15_strict_packet_ack", "S15_missing_material_report", "S15_diff_locality",
    "S15_unrelated_nodes_unchanged", "S15_stale_propagation", "S15_finding_resolution",
    "S15_no_new_high_severity", "S15_overlay_clause_preserved", "S15_candidate_return_schema",
    "S15_no_completion_claim",
}
REQUIRED_DIMS = {
    "s15_strict_packet_ack", "s15_diff_locality", "s15_unrelated_node_preservation",
    "s15_stale_propagation", "s15_finding_resolution", "s15_no_new_high_severity",
    "s15_candidate_return_verifier", "s15_nature_overlay",
}
NEGATIVES = {
    "invalid-s15-repair-execution-missing-task-ack.json": "E_S15_STRICT_PACKET_ACK_REQUIRED",
    "invalid-s15-repair-execution-bad-task-kind.json": "E_S15_STRICT_PACKET_ACK_REQUIRED",
    "invalid-s15-repair-execution-unsafe-diff-path.json": "E_S15_DIFF_LOCALITY_REQUIRED",
    "invalid-s15-repair-execution-global-rewrite.json": "E_S15_DIFF_LOCALITY_REQUIRED",
    "invalid-s15-repair-execution-bad-claim-impact.json": "E_S15_REVISED_CANDIDATE_REQUIRED",
    "invalid-s15-repair-execution-bare-s09-packet.json": "E_S15_REGENERATED_TASK_PACKETS_REQUIRED",
    "invalid-s15-repair-execution-missing-artifact.json": "E_S15_REGENERATED_ARTIFACTS_REQUIRED",
    "invalid-s15-repair-execution-bad-downstream-action.json": "E_S15_STALE_PROPAGATION_REQUIRED",
    "invalid-s15-repair-execution-stale-unresolved.json": "E_S15_STALE_PROPAGATION_REQUIRED",
    "invalid-s15-repair-execution-missing-preservation.json": "E_S15_UNRELATED_PRESERVATION_REQUIRED",
    "invalid-s15-repair-execution-bad-resolution-status.json": "E_S15_FINDING_RESOLUTION_REQUIRED",
    "invalid-s15-repair-execution-validator-failed.json": "E_S15_VALIDATOR_REPORT_REQUIRED",
    "invalid-s15-repair-execution-new-high-risk.json": "E_S15_NO_NEW_HIGH_SEVERITY_REQUIRED",
    "invalid-s15-repair-execution-bad-candidate-return.json": "E_S15_CANDIDATE_RETURN_REQUIRED",
    "invalid-s15-repair-execution-blocked-missing-material.json": "E_S15_MISSING_MATERIAL_REPORT_REQUIRED",
    "invalid-s15-repair-execution-missing-verifier-check.json": "E_S15_VERIFIER_EVIDENCE_REQUIRED",
    "invalid-s15-repair-execution-completion-overclaim.json": "E_S15_NO_COMPLETION_OVERCLAIM",
    "invalid-s15-repair-execution-authority-exported.json": "E_S15_AUTHORITY_BOUNDARY_REQUIRED",
}


def fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_doc(path: Path) -> dict[str, Any]:
    data, errors = load_document(path)
    if errors:
        fail("E_S15_DOC_LOAD", f"{path}: {errors[0].code}: {errors[0].message}")
    if not isinstance(data, dict):
        fail("E_S15_DOC_LOAD", f"{path}: root must be mapping")
    return data


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def verify_fixtures() -> None:
    for cmd in ([sys.executable, str(VALIDATE_PACKET), str(PACKET)], [sys.executable, str(VALIDATE_MATERIAL), str(MATERIAL)], [sys.executable, str(VALIDATE_RETURN), str(RETURN), "--packet", str(PACKET)]):
        result = run(cmd)
        if result.returncode != 0:
            fail("E_S15_POSITIVE", f"{' '.join(cmd)}\n{result.stdout}")
    for name, expected_code in NEGATIVES.items():
        result = run([sys.executable, str(VALIDATE_MATERIAL), str(ROOT / "examples/materials" / name)])
        if result.returncode == 0 or expected_code not in result.stdout:
            fail("E_S15_NEGATIVE", f"{name} expected {expected_code}, got\n{result.stdout}")


def verify_schema_packet_material() -> None:
    props = load_json(ROOT / "schemas/ppg-material-payloads.schema.json")["properties"]
    if "S15RepairExecutionReport" not in props:
        fail("E_S15_SCHEMA", "missing S15RepairExecutionReport")
    missing = REQUIRED_SCHEMA_FIELDS - set(props["S15RepairExecutionReport"].get("required", []))
    if missing:
        fail("E_S15_SCHEMA", f"missing {sorted(missing)}")
    task_props = load_json(ROOT / "schemas/ppg-task-packet.schema.json").get("properties", {})
    missing_packet_schema = REQUIRED_PACKET_FIELDS - set(task_props)
    if missing_packet_schema:
        fail("E_S15_PACKET_SCHEMA", f"missing packet schema fields {sorted(missing_packet_schema)}")
    packet = load_doc(PACKET)
    if REQUIRED_PACKET_FIELDS - set(packet):
        fail("E_S15_PACKET", "S15 packet missing scoped repair fields")
    if packet.get("stage_id") != "S15" or packet.get("agent_type") != "executor":
        fail("E_S15_PACKET", "S15 packet must bind S15 executor")
    material = load_json(MATERIAL)
    payload = material["payload"]
    if payload["candidate_artifact_return"] != load_json(RETURN):
        fail("E_S15_RETURN", "embedded return mismatch")
    if payload["authority_boundary"].get("controller_commit_claimed") is not False:
        fail("E_S15_AUTHORITY", "S15 must not claim controller commit")
    if payload["new_risk_scan"].get("new_high_severity_findings"):
        fail("E_S15_RISK", "new high-severity risk must be empty")


def verify_registry_phase() -> None:
    registry = load_json(ROOT / "runtime/stage_registry.json")
    s15 = {s["stage_id"]: s for s in registry["stages"]}["S15"]
    if s15["consumes"] != PUBLIC_CONSUMES or s15["produces"] != PUBLIC_PRODUCES:
        fail("E_S15_IO", "public IO drift")
    missing_validators = REQUIRED_REGISTRY_VALIDATORS - set(s15.get("validators", []))
    if missing_validators:
        fail("E_S15_VALIDATORS", f"missing {sorted(missing_validators)}")
    contract = load_json(ROOT / "examples/stage-contracts/S15.stage-contract.json")
    if contract.get("worker_packet_coverage", {}).get("packet_ref") != "examples/packets/phase10_s15_scoped_repair_packet.v1.yaml":
        fail("E_S15_CONTRACT", "S15 contract must link scoped repair packet")
    for key in ["consumes", "produces", "validators", "completion_gate", "coverage_status"]:
        if contract.get(key) != s15.get(key):
            fail("E_S15_CONTRACT", f"mismatch {key}")
    phase = load_json(ROOT / "runtime/phase10_content_validators.json")
    validator = {v["stage_id"]: v for v in phase["validators"]}["S15"]
    dims = {d["dimension_id"] for d in validator["dimensions"]}
    missing_dims = REQUIRED_DIMS - dims
    if missing_dims:
        fail("E_S15_PHASE", f"missing dims {sorted(missing_dims)}")
    checks = set(validator["required_checks"])
    missing_checks = {item.lower() for item in REQUIRED_REGISTRY_VALIDATORS} - checks
    if missing_checks:
        fail("E_S15_PHASE", f"missing checks {sorted(missing_checks)}")


def main() -> int:
    verify_fixtures()
    verify_schema_packet_material()
    verify_registry_phase()
    print("PPG_S15_REPAIR_EXECUTION_REPORT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
