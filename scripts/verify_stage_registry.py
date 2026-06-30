#!/usr/bin/env python3
"""Verify the Phase9 canonical stage registry."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "runtime" / "stage_registry.json"
REQUIRED_STAGE_IDS = [
    "S00", "S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09A", "S09B", "S10", "S11", "S12", "S13", "S14", "S15", "S16", "G01", "G02"
]
EXECUTION_MODES = {"owner_gated", "script_generated", "agent_generated", "hybrid_generated"}
REQUIRED_STAGE_FIELDS = {
    "stage_id", "stage_name", "purpose", "execution_mode", "requires_worker_task_packet", "recommended_agent_type", "consumes", "produces", "validators", "backflow_targets", "completion_gate", "coverage_status", "pilot_required", "activation_policy", "contract_ref"
}


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def validate_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "ppg-stage-registry/v0.1":
        errors.append(issue("E_STAGE_REGISTRY_SCHEMA", "schema_version must be ppg-stage-registry/v0.1"))
    if data.get("canonical_stage_ids") != REQUIRED_STAGE_IDS:
        errors.append(issue("E_STAGE_REGISTRY_CANONICAL_IDS", "canonical_stage_ids must match the exact Phase9 list"))
    if set(data.get("execution_mode_enum", [])) != EXECUTION_MODES:
        errors.append(issue("E_STAGE_REGISTRY_MODE_ENUM", "execution_mode_enum drifted"))
    stages = data.get("stages")
    if not isinstance(stages, list):
        return errors + [issue("E_STAGE_REGISTRY_STAGES", "stages must be a list")]
    ids: list[str] = []
    for idx, stage in enumerate(stages):
        if not isinstance(stage, dict):
            errors.append(issue("E_STAGE_REGISTRY_STAGE_SHAPE", f"stage[{idx}] must be object"))
            continue
        missing = sorted(REQUIRED_STAGE_FIELDS - set(stage))
        if missing:
            errors.append(issue("E_STAGE_REGISTRY_FIELD_MISSING", f"{stage.get('stage_id', idx)} missing {missing}"))
        stage_id = stage.get("stage_id")
        if not isinstance(stage_id, str) or not stage_id:
            errors.append(issue("E_STAGE_REGISTRY_ID", f"stage[{idx}] missing stage_id"))
            continue
        ids.append(stage_id)
        if stage_id == "S09":
            errors.append(issue("E_STAGE_REGISTRY_BARE_S09", "bare S09 is forbidden; use S09A and S09B"))
        if stage_id not in REQUIRED_STAGE_IDS:
            errors.append(issue("E_STAGE_REGISTRY_UNKNOWN_ID", stage_id))
        mode = stage.get("execution_mode")
        if mode not in EXECUTION_MODES:
            errors.append(issue("E_STAGE_REGISTRY_MODE", f"{stage_id} invalid mode {mode!r}"))
        if mode == "owner_gated" and stage.get("requires_worker_task_packet") is True:
            errors.append(issue("E_STAGE_REGISTRY_FAKE_WORKER_PACKET", f"{stage_id} owner_gated cannot require worker packet"))
        if mode == "script_generated" and stage.get("requires_worker_task_packet") is True:
            errors.append(issue("E_STAGE_REGISTRY_FAKE_WORKER_PACKET", f"{stage_id} script_generated cannot require worker packet"))
        for field in ["stage_name", "purpose", "recommended_agent_type", "completion_gate", "activation_policy", "coverage_status", "contract_ref"]:
            if not isinstance(stage.get(field), str) or not stage[field].strip():
                errors.append(issue("E_STAGE_REGISTRY_EMPTY_FIELD", f"{stage_id}.{field}"))
        for field in ["consumes", "produces", "validators"]:
            value = stage.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(issue("E_STAGE_REGISTRY_LIST_FIELD", f"{stage_id}.{field}"))
        if "$yxj-plugin-incubator" in json.dumps(stage, ensure_ascii=False) or "legacy $yxj-paper-os" in json.dumps(stage, ensure_ascii=False):
            errors.append(issue("E_STAGE_REGISTRY_FORBIDDEN_ROUTE", stage_id))
    if ids != REQUIRED_STAGE_IDS:
        errors.append(issue("E_STAGE_REGISTRY_ORDER_OR_SET", f"got {ids}"))
    if len(ids) != len(set(ids)):
        errors.append(issue("E_STAGE_REGISTRY_DUPLICATE", "duplicate stage_id present"))
    return errors


def run_negative_cases(valid: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    cases: list[tuple[str, dict[str, Any], str]] = []
    missing_stage = copy.deepcopy(valid)
    missing_stage["stages"] = missing_stage["stages"][:-1]
    missing_stage["canonical_stage_ids"] = REQUIRED_STAGE_IDS[:-1]
    cases.append(("missing_stage", missing_stage, "E_STAGE_REGISTRY_CANONICAL_IDS"))
    duplicate = copy.deepcopy(valid)
    duplicate["stages"] = duplicate["stages"] + [copy.deepcopy(duplicate["stages"][0])]
    cases.append(("duplicate", duplicate, "E_STAGE_REGISTRY_DUPLICATE"))
    invalid_mode = copy.deepcopy(valid)
    invalid_mode["stages"][0]["execution_mode"] = "department_loop"
    cases.append(("invalid_mode", invalid_mode, "E_STAGE_REGISTRY_MODE"))
    missing_contract = copy.deepcopy(valid)
    missing_contract["stages"][0].pop("contract_ref", None)
    cases.append(("missing_contract", missing_contract, "E_STAGE_REGISTRY_FIELD_MISSING"))
    fake_worker = copy.deepcopy(valid)
    fake_worker["stages"][0]["requires_worker_task_packet"] = True
    cases.append(("fake_worker", fake_worker, "E_STAGE_REGISTRY_FAKE_WORKER_PACKET"))
    bare_s09 = copy.deepcopy(valid)
    bare_s09["stages"][9]["stage_id"] = "S09"
    cases.append(("bare_s09", bare_s09, "E_STAGE_REGISTRY_BARE_S09"))
    for name, data, expected in cases:
        errors = validate_registry(data)
        if not any(expected in error for error in errors):
            failures.append(issue("E_STAGE_REGISTRY_NEGATIVE_CASE", f"{name} did not trigger {expected}: {errors}"))
    return failures


def main() -> int:
    data = load_registry()
    errors = validate_registry(data)
    errors.extend(run_negative_cases(data))
    if errors:
        print("INVALID runtime/stage_registry.json", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE9_STAGE_REGISTRY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
