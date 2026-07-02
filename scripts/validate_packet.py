#!/usr/bin/env python3
"""Validate Phase 6 strict TaskPacket fixtures.

Stale minimal packets may remain as fixtures, but Phase 6 strict
validation is intended for generated/migrated packets such as intro v2 and
claim-repair packets.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        issue,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        issue,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )

BROAD_PATHS = {"", ".", "./", "..", "../", "/", "examples", "examples/", "schemas", "schemas/", "scripts", "scripts/"}
SAFE_READ_PREFIXES = (
    "examples/materials/",
    "examples/review_findings/",
    "examples/backflow_tasks/",
)
SAFE_WRITE_PREFIXES = (
    "examples/candidate-artifacts/",
    "examples/materials/",
    "runs/",
)
REQUIRED_FORBIDDEN_ROUTES = {
    "mark_graph_complete",
    "dispatch_subagents",
    "write_outside_allowed_write_paths",
    "change_owner_intent",
}
ALLOWED_FORBIDDEN_ROUTES = REQUIRED_FORBIDDEN_ROUTES | {
    "alter_unrelated_sections",
    "claim_submission_or_publication_readiness",
    "introduce_new_claims",
    "mark_manuscript_complete",
    "strengthen_claims_beyond_s04",
}
SAFE_ALLOWED_ACTIONS = {
    "read_material_bundle",
    "draft_candidate_artifact",
    "return_evidence",
}
SAFE_ALLOWED_TOOLS = {"none"}
CANONICAL_STAGE_ID_RE = re.compile(r"^(S(0[0-8]|09A|09B|1[0-6])|G0[12])$")
ALLOWED_PACKET_FIELDS = {
    "schema_version",
    "packet_id",
    "status",
    "stage_id",
    "stage_contract_ref",
    "task_kind",
    "agent_type",
    "mission",
    "target_material",
    "input_materials",
    "mandatory_controls",
    "hard_constraints",
    "local_context",
    "adjacent_context",
    "background_context_usage",
    "negative_controls",
    "authority_and_target",
    "s08_visual_formal_contract",
    "panel_evidence_package",
    "source_data_package",
    "terminology_and_surface_controls",
    "visual_quality_profile",
    "visual_polish_policy",
    "s12_input_package",
    "s10_text_candidates",
    "s11_visual_candidates",
    "upstream_control_materials",
    "stale_material_policy",
    "s13_review_input_package",
    "structured_s12_candidate",
    "reviewer_panel_profile",
    "adversarial_review_protocol",
    "finding_taxonomy",
    "local_backflow_routing_rules",
    "s15_repair_task",
    "repair_scope",
    "pre_repair_snapshot_requirements",
    "affected_downstream_set",
    "protected_unrelated_nodes",
    "diff_locality_requirements",
    "finding_resolution_requirements",
    "regression_scan_requirements",
    "section_or_unit_move_plan",
    "claim_boundary_controls",
    "object_granularity_controls",
    "terminology_surface_controls",
    "visual_formal_controls",
    "evidence_anchors",
    "forbidden_routes",
    "allowed_actions",
    "allowed_read_paths",
    "allowed_write_paths",
    "allowed_tools",
    "output_artifact_path",
    "expected_output_schema",
    "expected_material_type",
    "expected_payload_schema",
    "internal_execution_protocol",
    "output_contract",
    "coverage_ledgers_required",
    "descriptive_not_prescriptive_controls",
    "validators",
    "return_format",
    "single_writer_lock",
    "packet_authority_boundary",
    "ingestion_target",
    "stop_condition",
    "failure_report_format",
    "worker_boot_clause",
    "completion_forbidden",
    "no_recursive_orchestration",
    "owner_gate_required",
}
BOOT_REQUIRED_TERMS = (
    "completion_forbidden",
    "no_recursive_orchestration",
    "allowed_write_paths",
    "missingmaterialreport",
)


def _is_non_empty_mapping(value: Any) -> bool:
    return isinstance(value, dict) and bool(value)


def _path_is_within(path: str, allowed: str) -> bool:
    if not _is_safe_repo_relative_path(path) or not _is_safe_repo_relative_path(allowed):
        return False
    normalized = PurePosixPath(path)
    allowed_normalized = PurePosixPath(allowed)
    if normalized == allowed_normalized:
        return True
    try:
        normalized.relative_to(allowed_normalized)
    except ValueError:
        return False
    return True


def _is_safe_repo_relative_path(path: str) -> bool:
    if path.strip() != path or "\\" in path:
        return False
    if any(ord(char) < 32 for char in path):
        return False
    if path.startswith("~") or (len(path) >= 2 and path[1] == ":"):
        return False
    if path.strip() in BROAD_PATHS:
        return False
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or not parsed.suffix:
        return False
    return not any(part in {"", ".", ".."} for part in path.split("/"))


def _has_allowed_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _list_values(value: Any) -> set[str]:
    if not is_non_empty_string_list(value):
        return set()
    assert isinstance(value, list)
    return {str(item) for item in value}


def _validate_paths(data: dict[str, Any]) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    read_paths = data.get("allowed_read_paths")
    write_paths = data.get("allowed_write_paths")
    output_path = data.get("output_artifact_path")

    if not is_non_empty_string_list(read_paths):
        errors.append(issue("E_TASK_ALLOWED_READ_PATHS_REQUIRED", "allowed_read_paths must be a non-empty list of string paths"))
    if not is_non_empty_string_list(write_paths):
        errors.append(issue("E_TASK_ALLOWED_WRITE_PATHS_REQUIRED", "allowed_write_paths must be a non-empty list of string paths"))
    for field_name, paths, prefixes in (
        ("allowed_read_paths", read_paths, SAFE_READ_PREFIXES),
        ("allowed_write_paths", write_paths, SAFE_WRITE_PREFIXES),
    ):
        if isinstance(paths, list):
            for path in paths:
                if isinstance(path, str) and (not _is_safe_repo_relative_path(path) or not _has_allowed_prefix(path, prefixes)):
                    errors.append(issue("E_TASK_ALLOWED_PATH_TOO_BROAD", f"{field_name} contains broad path: {path}"))
    if not is_non_empty_string(output_path):
        errors.append(issue("E_TASK_OUTPUT_PATH_REQUIRED", "output_artifact_path must be a non-empty string"))
    elif isinstance(write_paths, list) and all(is_non_empty_string(path) for path in write_paths):
        if write_paths != [output_path]:
            errors.append(issue("E_TASK_ALLOWED_WRITE_PATHS_REQUIRED", "allowed_write_paths must contain exactly output_artifact_path for strict worker packets"))
        if not any(_path_is_within(str(output_path), str(path)) for path in write_paths):
            errors.append(issue("E_TASK_OUTPUT_OUTSIDE_ALLOWED_WRITES", "output_artifact_path must be within allowed_write_paths"))
    return errors


def _validate_authority_fields(data: dict[str, Any]) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    forbidden_routes_raw = data.get("forbidden_routes")
    forbidden_routes = _list_values(data.get("forbidden_routes"))
    if forbidden_routes and (
        not REQUIRED_FORBIDDEN_ROUTES <= forbidden_routes
        or not forbidden_routes <= ALLOWED_FORBIDDEN_ROUTES
        or not isinstance(forbidden_routes_raw, list)
        or len(forbidden_routes_raw) != len(forbidden_routes)
    ):
        missing = sorted(REQUIRED_FORBIDDEN_ROUTES - forbidden_routes)
        extra = sorted(forbidden_routes - ALLOWED_FORBIDDEN_ROUTES)
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"extra: {', '.join(extra)}")
        if not details:
            details.append("duplicates are not allowed")
        errors.append(issue("E_TASK_FORBIDDEN_ROUTES_REQUIRED", f"forbidden_routes must match canonical set ({'; '.join(details)})"))

    allowed_actions_raw = data.get("allowed_actions")
    allowed_actions = _list_values(data.get("allowed_actions"))
    if allowed_actions and (
        allowed_actions != SAFE_ALLOWED_ACTIONS
        or not isinstance(allowed_actions_raw, list)
        or len(allowed_actions_raw) != len(SAFE_ALLOWED_ACTIONS)
    ):
        missing = sorted(SAFE_ALLOWED_ACTIONS - allowed_actions)
        unsafe = sorted(allowed_actions - SAFE_ALLOWED_ACTIONS)
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unsafe:
            details.append(f"unsafe: {', '.join(unsafe)}")
        if not details:
            details.append("duplicates are not allowed")
        errors.append(issue("E_TASK_ALLOWED_ACTIONS_REQUIRED", f"allowed_actions must match canonical safe set ({'; '.join(details)})"))

    allowed_tools_raw = data.get("allowed_tools")
    allowed_tools = _list_values(allowed_tools_raw)
    if allowed_tools and (allowed_tools != SAFE_ALLOWED_TOOLS or allowed_tools_raw != ["none"]):
        errors.append(issue("E_TASK_ALLOWED_TOOLS_REQUIRED", "allowed_tools must be exactly: none"))
    return errors


def _validate_worker_boot_clause(data: dict[str, Any]) -> list[ValidationIssue]:
    boot = data.get("worker_boot_clause")
    if not is_non_empty_string(boot):
        return [issue("E_TASK_WORKER_BOOT_CLAUSE_REQUIRED", "worker_boot_clause must be a non-empty string")]
    lowered = str(boot).lower()
    missing = [term for term in BOOT_REQUIRED_TERMS if term not in lowered]
    if missing:
        return [issue("E_TASK_WORKER_BOOT_CLAUSE_REQUIRED", f"worker_boot_clause missing required intent: {', '.join(missing)}")]
    return []


def validate(data: Any) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)

    errors.extend(require_string_fields(data, ["schema_version", "packet_id", "status", "mission"], "E_ENVELOPE_REQUIRED"))
    errors.extend(require_string_fields(data, ["stage_id", "stage_contract_ref"], "E_TASK_STAGE_BINDING_REQUIRED"))
    unknown_fields = sorted(set(data) - ALLOWED_PACKET_FIELDS)
    if unknown_fields:
        errors.append(issue("E_TASK_UNKNOWN_FIELD", f"unknown TaskPacket fields are not allowed: {', '.join(unknown_fields)}"))
    if data.get("schema_version") and data.get("schema_version") != "ppg-task-packet/v0.1":
        errors.append(issue("E_ENVELOPE_REQUIRED", "schema_version must be ppg-task-packet/v0.1"))
    stage_id = data.get("stage_id")
    stage_contract_ref = data.get("stage_contract_ref")
    if isinstance(stage_id, str) and not CANONICAL_STAGE_ID_RE.fullmatch(stage_id):
        errors.append(issue("E_TASK_STAGE_BINDING_STAGE_ID", f"stage_id is not canonical: {stage_id}"))
    if isinstance(stage_id, str) and isinstance(stage_contract_ref, str):
        expected_contract_ref = f"examples/stage-contracts/{stage_id}.stage-contract.json"
        if stage_contract_ref != expected_contract_ref:
            errors.append(issue("E_TASK_STAGE_BINDING_MISMATCH", f"stage_contract_ref must be {expected_contract_ref}"))
    errors.extend(validate_runtime_status(data))
    if data.get("status") and data.get("status") != "planned":
        errors.append(issue("E_TASK_STATUS_PLANNED_REQUIRED", "strict TaskPacket status must be planned"))

    errors.extend(require_string_fields(
        data,
        [
            "task_kind",
            "agent_type",
            "target_material",
            "output_artifact_path",
            "expected_output_schema",
            "ingestion_target",
            "stop_condition",
            "failure_report_format",
        ],
        "E_TASK_FIELD_REQUIRED",
    ))

    if not is_non_empty_string_list(data.get("input_materials")):
        errors.append(issue("E_TASK_INPUTS_REQUIRED", "input_materials must be a non-empty list of string material handles"))
    if not _is_non_empty_mapping(data.get("mandatory_controls")):
        errors.append(issue("E_TASK_MANDATORY_CONTROLS_REQUIRED", "mandatory_controls must be a non-empty mapping"))
    if not is_non_empty_string_list(data.get("evidence_anchors")):
        errors.append(issue("E_TASK_EVIDENCE_ANCHORS_REQUIRED", "evidence_anchors must be a non-empty list of strings"))
    for field_name, code in (
        ("forbidden_routes", "E_TASK_FORBIDDEN_ROUTES_REQUIRED"),
        ("allowed_actions", "E_TASK_ALLOWED_ACTIONS_REQUIRED"),
        ("allowed_tools", "E_TASK_ALLOWED_TOOLS_REQUIRED"),
        ("validators", "E_PAYLOAD_REQUIRED"),
    ):
        if not is_non_empty_string_list(data.get(field_name)):
            errors.append(issue(code, f"{field_name} must be a non-empty list of strings"))
    if not _is_non_empty_mapping(data.get("return_format")):
        errors.append(issue("E_TASK_RETURN_FORMAT_REQUIRED", "return_format must be a non-empty mapping"))
    for field_name in ("expected_material_type", "expected_payload_schema"):
        if field_name in data and not is_non_empty_string(data.get(field_name)):
            errors.append(issue("E_TASK_FIELD_REQUIRED", f"{field_name} must be a non-empty string when present"))
    for field_name in ("internal_execution_protocol", "output_contract", "descriptive_not_prescriptive_controls"):
        if field_name in data and not _is_non_empty_mapping(data.get(field_name)):
            errors.append(issue("E_TASK_FIELD_REQUIRED", f"{field_name} must be a non-empty mapping when present"))
    if "coverage_ledgers_required" in data and not is_non_empty_string_list(data.get("coverage_ledgers_required")):
        errors.append(issue("E_TASK_FIELD_REQUIRED", "coverage_ledgers_required must be a non-empty list of strings when present"))

    errors.extend(_validate_paths(data))
    errors.extend(_validate_authority_fields(data))

    if data.get("completion_forbidden") is not True:
        errors.append(issue("E_TASK_COMPLETION_FORBIDDEN_REQUIRED", "completion_forbidden must be literal true"))
    if data.get("no_recursive_orchestration") is not True:
        errors.append(issue("E_TASK_NO_RECURSIVE_ORCHESTRATION_REQUIRED", "no_recursive_orchestration must be literal true"))
    if "owner_gate_required" not in data:
        errors.append(issue("E_TASK_OWNER_GATE_REQUIRED", "owner_gate_required must be present and false for strict worker packets"))
    elif data.get("owner_gate_required") is not False:
        errors.append(issue("E_TASK_OWNER_GATE_FORBIDDEN", "owner_gate_required must be false for strict worker packets"))

    errors.extend(_validate_worker_boot_clause(data))
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_packet.py <task-packet.json|yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    return print_result(path, validate(data))


if __name__ == "__main__":
    raise SystemExit(main())
