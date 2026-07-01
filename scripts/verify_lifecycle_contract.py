#!/usr/bin/env python3
"""Verify the Paper OS feedback lifecycle contract fixtures.

The validator is intentionally dependency-free. It checks the executable
semantics that matter for Paper OS authority: feedback must be attributed before
repair, repairs must be local and bounded, system-learning records require
retrospective evidence, and the core contract cannot depend on OMX or host-local
Codex paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "examples/lifecycle/feedback_to_stage_improvement.valid.json"
NEGATIVE_FIXTURES = {
    "examples/lifecycle/invalid-unrouted-feedback.json": "E_FEEDBACK_UNROUTED",
    "examples/lifecycle/invalid-global-rewrite-repair.json": "E_REPAIR_SCOPE_GLOBAL_REWRITE",
    "examples/lifecycle/invalid-recursive-repair-authority.json": "E_REPAIR_AUTHORITY_ESCALATION",
    "examples/lifecycle/invalid-premature-stage-improvement.json": "E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED",
    "examples/lifecycle/invalid-retrospective-submission-claim.json": "E_RETROSPECTIVE_READINESS_OVERCLAIM",
    "examples/lifecycle/invalid-active-omx-dependency.json": "E_STANDALONE_DEPENDENCY_FORBIDDEN",
}
STAGES = {f"S{i:02d}" for i in range(17)} | {"S09A", "S09B", "G01", "G02"}
FORBIDDEN_READINESS = {"submission_ready", "published", "publication_ready", "final", "accepted"}
HOST_LOCAL_MARKERS = ("/home/", "/Users/", "C:/", "C:\\", "/.codex/", "\\.codex\\")


class ContractError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:  # pragma: no cover - exact message not part of contract
        raise ContractError("E_JSON_INVALID", str(exc)) from exc
    if not isinstance(data, dict):
        raise ContractError("E_ROOT_OBJECT_REQUIRED", "lifecycle contract must be an object")
    return data


def require_str(obj: dict[str, Any], key: str, code: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(code, f"{key} is required")
    return value


def require_list(obj: dict[str, Any], key: str, code: str) -> list[Any]:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        raise ContractError(code, f"{key} must be a non-empty list")
    return value


def reject_host_local(value: Any) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if "$autopilot" in lowered or "$pipeline" in lowered or "$team" in lowered or "$ralplan" in lowered or "$ultragoal" in lowered:
            raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "active lifecycle contract requires OMX command")
        if any(marker.lower() in lowered for marker in HOST_LOCAL_MARKERS):
            raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "active lifecycle contract requires host-local path")
    elif isinstance(value, dict):
        for child in value.values():
            reject_host_local(child)
    elif isinstance(value, list):
        for child in value:
            reject_host_local(child)


def verify(data: dict[str, Any]) -> None:
    if data.get("schema_version") != "ppg-lifecycle-contract/v0.1":
        raise ContractError("E_SCHEMA_VERSION", "schema_version must be ppg-lifecycle-contract/v0.1")

    standalone = data.get("standalone_contract")
    if not isinstance(standalone, dict):
        raise ContractError("E_STANDALONE_REQUIRED", "standalone_contract is required")
    if standalone.get("omx_dependency") is not False or standalone.get("host_local_dependency") is not False:
        raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "OMX and host-local dependencies must be false")
    if standalone.get("authority_source") != "paper_os":
        raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "authority_source must be paper_os")
    reject_host_local(standalone)

    feedback = require_list(data, "feedback_packages", "E_FEEDBACK_REQUIRED")
    try:
        attributions = require_list(data, "attributions", "E_ATTRIBUTION_REQUIRED")
    except ContractError as exc:
        if exc.code == "E_ATTRIBUTION_REQUIRED":
            raise ContractError("E_FEEDBACK_UNROUTED", "every feedback package needs attribution before repair") from exc
        raise
    repairs = require_list(data, "repair_packets", "E_REPAIR_REQUIRED")
    retrospectives = require_list(data, "retrospectives", "E_RETROSPECTIVE_REQUIRED")
    improvements = require_list(data, "stage_improvements", "E_STAGE_IMPROVEMENT_REQUIRED")

    feedback_ids: set[str] = set()
    for item in feedback:
        if not isinstance(item, dict):
            raise ContractError("E_FEEDBACK_REQUIRED", "feedback item must be object")
        fid = require_str(item, "package_id", "E_FEEDBACK_REQUIRED")
        feedback_ids.add(fid)
        require_str(item, "affected_artifact", "E_FEEDBACK_REQUIRED")
        require_list(item, "candidate_failure_types", "E_FEEDBACK_REQUIRED")

    attribution_by_id: dict[str, dict[str, Any]] = {}
    attributed_feedback = set()
    for item in attributions:
        if not isinstance(item, dict):
            raise ContractError("E_ATTRIBUTION_REQUIRED", "attribution item must be object")
        aid = require_str(item, "attribution_id", "E_ATTRIBUTION_REQUIRED")
        attribution_by_id[aid] = item
        fid = require_str(item, "feedback_package_id", "E_ATTRIBUTION_REQUIRED")
        if fid not in feedback_ids:
            raise ContractError("E_FEEDBACK_UNROUTED", "attribution references unknown feedback package")
        attributed_feedback.add(fid)
        stage = require_str(item, "nearest_stage", "E_ATTRIBUTION_STAGE_INVALID")
        if stage not in STAGES:
            raise ContractError("E_ATTRIBUTION_STAGE_INVALID", f"unknown stage {stage}")
        require_str(item, "responsible_material", "E_ATTRIBUTION_REQUIRED")
        require_str(item, "failure_level", "E_ATTRIBUTION_REQUIRED")
        if not isinstance(item.get("owner_gate_required"), bool):
            raise ContractError("E_ATTRIBUTION_REQUIRED", "owner_gate_required must be boolean")
        require_list(item, "downstream_stale_targets", "E_ATTRIBUTION_REQUIRED")
    if feedback_ids - attributed_feedback:
        raise ContractError("E_FEEDBACK_UNROUTED", "every feedback package needs attribution before repair")

    for item in repairs:
        if not isinstance(item, dict):
            raise ContractError("E_REPAIR_REQUIRED", "repair item must be object")
        rid = require_str(item, "repair_packet_id", "E_REPAIR_REQUIRED")
        aid = require_str(item, "attribution_id", "E_REPAIR_REQUIRED")
        if aid not in attribution_by_id:
            raise ContractError("E_REPAIR_ATTRIBUTION_UNKNOWN", f"{rid} references unknown attribution")
        target = require_str(item, "target_material", "E_REPAIR_REQUIRED")
        action = require_str(item, "repair_action", "E_REPAIR_REQUIRED")
        owner_gate = item.get("owner_gate_required") is True or attribution_by_id[aid].get("owner_gate_required") is True
        if ("whole_manuscript" in target or "whole_manuscript_rewrite" in action) and not owner_gate:
            raise ContractError("E_REPAIR_SCOPE_GLOBAL_REWRITE", "whole manuscript repair requires owner gate")
        if item.get("completion_forbidden") is not True or item.get("no_recursive_orchestration") is not True:
            raise ContractError("E_REPAIR_AUTHORITY_ESCALATION", "repair packet must forbid completion and recursive orchestration")
        require_list(item, "allowed_write_paths", "E_REPAIR_REQUIRED")
        require_list(item, "validators", "E_REPAIR_REQUIRED")
        reject_host_local(item)

    retrospective_ids: set[str] = set()
    for item in retrospectives:
        if not isinstance(item, dict):
            raise ContractError("E_RETROSPECTIVE_REQUIRED", "retrospective item must be object")
        rid = require_str(item, "retrospective_id", "E_RETROSPECTIVE_REQUIRED")
        retrospective_ids.add(rid)
        for claim in item.get("readiness_claims", []):
            if isinstance(claim, str) and claim in FORBIDDEN_READINESS:
                raise ContractError("E_RETROSPECTIVE_READINESS_OVERCLAIM", "retrospective cannot claim submission/publication/final readiness")
        require_list(item, "feedback_packages", "E_RETROSPECTIVE_REQUIRED")

    for item in improvements:
        if not isinstance(item, dict):
            raise ContractError("E_STAGE_IMPROVEMENT_REQUIRED", "stage improvement item must be object")
        status = item.get("status")
        if status == "committed":
            raise ContractError("E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED", "stage improvements are proposals, not direct committed graph edits")
        stage = require_str(item, "stage_id", "E_STAGE_IMPROVEMENT_REQUIRED")
        if stage not in STAGES:
            raise ContractError("E_ATTRIBUTION_STAGE_INVALID", f"unknown improvement stage {stage}")
        evidence_count = item.get("evidence_count")
        source_retrospective = item.get("source_retrospective")
        if not isinstance(evidence_count, int) or evidence_count < 2 or source_retrospective not in retrospective_ids:
            raise ContractError("E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED", "stage improvement requires repeated evidence and retrospective source")
        if item.get("regression_test_needed") is not True:
            raise ContractError("E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED", "stage improvement needs regression test")


def verify_file(path: Path) -> str | None:
    try:
        verify(load(path))
    except ContractError as exc:
        return exc.code
    return None


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        for raw in argv[1:]:
            path = Path(raw)
            error = verify_file(path)
            if error:
                print(f"INVALID {path}\n- {error}")
                return 1
            print(f"VALID {path}")
        return 0

    error = verify_file(VALID)
    if error:
        print(f"INVALID {VALID}\n- {error}")
        return 1

    failures: list[str] = []
    for rel, expected in NEGATIVE_FIXTURES.items():
        path = ROOT / rel
        actual = verify_file(path)
        if actual != expected:
            failures.append(f"{rel}: expected {expected}, got {actual or 'VALID'}")
    if failures:
        print("PPG_LIFECYCLE_CONTRACT_FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PPG_LIFECYCLE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
