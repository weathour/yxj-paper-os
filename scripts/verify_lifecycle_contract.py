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
import re
import sys
from pathlib import Path, PurePosixPath
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
    "examples/lifecycle/invalid-active-omx-command.json": "E_STANDALONE_DEPENDENCY_FORBIDDEN",
    "examples/lifecycle/invalid-bare-s09-attribution.json": "E_ATTRIBUTION_STAGE_INVALID",
    "examples/lifecycle/invalid-broad-repair-path.json": "E_REPAIR_PATH_UNSAFE",
    "examples/lifecycle/invalid-retrospective-linkage.json": "E_RETROSPECTIVE_LINKAGE_INVALID",
}
REGISTRY = ROOT / "runtime/stage_registry.json"
FORBIDDEN_READINESS_RE = re.compile(
    r"\b(submit|submitted|submission|publication|publish|published|accepted|acceptance|camera\s*ready|final)\b"
)
HOST_LOCAL_MARKERS = ("/home/", "/Users/", "C:/", "C:\\", "/.codex/", "\\.codex\\")
ACTIVE_OMX_RE = re.compile(r"(^|\b)(omx|oh-my-codex)(\b|:|/)", re.IGNORECASE)
BROAD_REPAIR_RE = re.compile(
    r"\b(whole\s+manuscript|full\s+manuscript|entire\s+(paper|manuscript)|all\s+(sections|manuscript)|"
    r"rewrite\s+all|from\s+scratch|global\s+rewrite)\b"
)
BROAD_WRITE_PATHS = {"", ".", "./", "..", "../", "/", "manuscript", "manuscript/", "paper-os", "paper-os/", "docs", "docs/"}
SAFE_REPAIR_WRITE_PREFIXES = (
    "examples/materials/",
    "examples/candidate-artifacts/",
    "manuscript/sections/",
    "figures/",
    "tables/",
    "runs/",
)
SAFE_AUTHORITY_REF_PREFIXES = ("examples/packets/", "examples/backflow_tasks/")

try:
    from ppg_validate_common import load_document
    from validate_backflow import validate as validate_backflow
    from validate_packet import validate as validate_task_packet
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(ROOT / "scripts"))
    from ppg_validate_common import load_document  # type: ignore  # noqa: E402
    from validate_backflow import validate as validate_backflow  # type: ignore  # noqa: E402
    from validate_packet import validate as validate_task_packet  # type: ignore  # noqa: E402


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


def canonical_stages() -> set[str]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    stages = registry.get("canonical_stage_ids")
    if not isinstance(stages, list) or not all(isinstance(item, str) for item in stages):
        raise ContractError("E_ATTRIBUTION_STAGE_INVALID", "stage registry canonical_stage_ids missing")
    return set(stages)


def normalize_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def normalize_material(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def reject_host_local(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        optional_adapter_slot = len(path) >= 2 and path[-2] == "optional_adapters" and value == "omx_as_personal_adapter"
        if not optional_adapter_slot and (
            "$autopilot" in lowered
            or "$pipeline" in lowered
            or "$team" in lowered
            or "$ralplan" in lowered
            or "$ultragoal" in lowered
            or ACTIVE_OMX_RE.search(value)
        ):
            raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "active lifecycle contract requires OMX command")
        if any(marker.lower() in lowered for marker in HOST_LOCAL_MARKERS):
            raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "active lifecycle contract requires host-local path")
    elif isinstance(value, dict):
        for key, child in value.items():
            reject_host_local(child, (*path, str(key)))
    elif isinstance(value, list):
        parent = path[-1] if path else "[]"
        for child in value:
            reject_host_local(child, (*path, parent))


def safe_repo_relative_path(raw: Any, *, allowed_prefixes: tuple[str, ...]) -> bool:
    if not isinstance(raw, str) or raw.strip() != raw or "\\" in raw:
        return False
    if raw in BROAD_WRITE_PATHS or raw.startswith("~") or (len(raw) > 1 and raw[1] == ":"):
        return False
    parsed = PurePosixPath(raw)
    if parsed.is_absolute() or not parsed.suffix:
        return False
    if any(part in {"", ".", ".."} for part in raw.split("/")):
        return False
    return any(raw.startswith(prefix) for prefix in allowed_prefixes)


def require_safe_write_paths(item: dict[str, Any]) -> list[str]:
    paths = require_list(item, "allowed_write_paths", "E_REPAIR_REQUIRED")
    out: list[str] = []
    for path in paths:
        if not safe_repo_relative_path(path, allowed_prefixes=SAFE_REPAIR_WRITE_PREFIXES):
            raise ContractError("E_REPAIR_PATH_UNSAFE", f"unsafe repair write path: {path!r}")
        out.append(path)
    return out


def validate_authority_ref(ref: str, *, kind: str) -> dict[str, Any]:
    if not safe_repo_relative_path(ref, allowed_prefixes=SAFE_AUTHORITY_REF_PREFIXES):
        raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", f"unsafe authority ref: {ref}")
    path = ROOT / ref
    if not path.is_file():
        raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", f"missing authority ref: {ref}")
    data, errors = load_document(path)
    if errors:
        raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", f"cannot load {ref}: {errors[0].message}")
    if kind == "task":
        issues = validate_task_packet(data)
        if issues:
            raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", f"invalid task packet ref {ref}: {issues[0].code}")
    elif kind == "backflow":
        issues = validate_backflow(data)
        if issues:
            raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", f"invalid backflow ref {ref}: {issues[0].code}")
    else:  # pragma: no cover
        raise AssertionError(kind)
    if not isinstance(data, dict):
        raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", f"{ref} must load as object")
    return data


def assert_repair_authority_ref(item: dict[str, Any], attribution: dict[str, Any]) -> None:
    task_ref = item.get("task_packet_ref")
    backflow_ref = item.get("backflow_task_ref")
    if not isinstance(task_ref, str) and not isinstance(backflow_ref, str):
        raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", "repair packet must point to a strict TaskPacket or BackflowTask")
    if isinstance(task_ref, str):
        packet = validate_authority_ref(task_ref, kind="task")
        if packet.get("completion_forbidden") is not True or packet.get("no_recursive_orchestration") is not True:
            raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", "task packet authority flags are not strict")
    if isinstance(backflow_ref, str):
        backflow = validate_authority_ref(backflow_ref, kind="backflow")
        expected = normalize_material(attribution.get("responsible_material"))
        targets = {
            normalize_material(backflow.get("target")),
            normalize_material(backflow.get("source_target")),
            normalize_material(backflow.get("affected_material_id")),
        }
        if expected and expected not in targets:
            raise ContractError("E_REPAIR_AUTHORITY_REF_INVALID", "backflow ref does not bind to attributed material")


def verify(data: dict[str, Any]) -> None:
    if data.get("schema_version") != "ppg-lifecycle-contract/v0.1":
        raise ContractError("E_SCHEMA_VERSION", "schema_version must be ppg-lifecycle-contract/v0.1")

    reject_host_local(data)
    stages = canonical_stages()

    standalone = data.get("standalone_contract")
    if not isinstance(standalone, dict):
        raise ContractError("E_STANDALONE_REQUIRED", "standalone_contract is required")
    if standalone.get("omx_dependency") is not False or standalone.get("host_local_dependency") is not False:
        raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "OMX and host-local dependencies must be false")
    if standalone.get("authority_source") != "paper_os":
        raise ContractError("E_STANDALONE_DEPENDENCY_FORBIDDEN", "authority_source must be paper_os")
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
        if stage not in stages:
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
        attribution = attribution_by_id[aid]
        target = require_str(item, "target_material", "E_REPAIR_REQUIRED")
        action = require_str(item, "repair_action", "E_REPAIR_REQUIRED")
        owner_gate = item.get("owner_gate_required") is True or attribution.get("owner_gate_required") is True
        repair_text = f"{normalize_text(target)} {normalize_text(action)}"
        if BROAD_REPAIR_RE.search(repair_text) and not owner_gate:
            raise ContractError("E_REPAIR_SCOPE_GLOBAL_REWRITE", "whole manuscript repair requires owner gate")
        if item.get("completion_forbidden") is not True or item.get("no_recursive_orchestration") is not True:
            raise ContractError("E_REPAIR_AUTHORITY_ESCALATION", "repair packet must forbid completion and recursive orchestration")
        require_safe_write_paths(item)
        require_list(item, "validators", "E_REPAIR_REQUIRED")
        raw_repair_scope = attribution.get("repair_scope")
        repair_scope: dict[str, Any] = raw_repair_scope if isinstance(raw_repair_scope, dict) else {}
        allowed_targets = {
            normalize_material(attribution.get("responsible_material")),
            normalize_material(repair_scope.get("primary")),
            *(normalize_material(value) for value in repair_scope.get("secondary", []) if isinstance(value, str)),
        }
        if normalize_material(target) not in {value for value in allowed_targets if value} and not owner_gate:
            raise ContractError("E_REPAIR_TARGET_OUTSIDE_ATTRIBUTION", "repair target must stay inside attribution scope")
        assert_repair_authority_ref(item, attribution)

    retrospective_ids: set[str] = set()
    retrospective_improvement_refs: dict[str, set[str]] = {}
    for item in retrospectives:
        if not isinstance(item, dict):
            raise ContractError("E_RETROSPECTIVE_REQUIRED", "retrospective item must be object")
        rid = require_str(item, "retrospective_id", "E_RETROSPECTIVE_REQUIRED")
        retrospective_ids.add(rid)
        referenced_feedback = set(require_list(item, "feedback_packages", "E_RETROSPECTIVE_REQUIRED"))
        if not all(isinstance(fid, str) and fid in feedback_ids for fid in referenced_feedback):
            raise ContractError("E_RETROSPECTIVE_LINKAGE_INVALID", "retrospective references unknown feedback package")
        improvement_refs = set(require_list(item, "stage_improvements", "E_RETROSPECTIVE_REQUIRED"))
        if not all(isinstance(iid, str) and iid.strip() for iid in improvement_refs):
            raise ContractError("E_RETROSPECTIVE_LINKAGE_INVALID", "retrospective improvement refs must be strings")
        retrospective_improvement_refs[rid] = improvement_refs
        for claim in item.get("readiness_claims", []):
            if isinstance(claim, str) and FORBIDDEN_READINESS_RE.search(normalize_text(claim)):
                raise ContractError("E_RETROSPECTIVE_READINESS_OVERCLAIM", "retrospective cannot claim submission/publication/final readiness")

    improvement_ids: set[str] = set()
    for item in improvements:
        if not isinstance(item, dict):
            raise ContractError("E_STAGE_IMPROVEMENT_REQUIRED", "stage improvement item must be object")
        improvement_id = require_str(item, "improvement_id", "E_STAGE_IMPROVEMENT_REQUIRED")
        improvement_ids.add(improvement_id)
        status = item.get("status")
        if status == "committed":
            raise ContractError("E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED", "stage improvements are proposals, not direct committed graph edits")
        stage = require_str(item, "stage_id", "E_STAGE_IMPROVEMENT_REQUIRED")
        if stage not in stages:
            raise ContractError("E_ATTRIBUTION_STAGE_INVALID", f"unknown improvement stage {stage}")
        evidence_count = item.get("evidence_count")
        source_retrospective = item.get("source_retrospective")
        if not isinstance(evidence_count, int) or evidence_count < 2 or source_retrospective not in retrospective_ids:
            raise ContractError("E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED", "stage improvement requires repeated evidence and retrospective source")
        if improvement_id not in retrospective_improvement_refs.get(str(source_retrospective), set()):
            raise ContractError("E_RETROSPECTIVE_LINKAGE_INVALID", "stage improvement must be listed by its source retrospective")
        if item.get("regression_test_needed") is not True:
            raise ContractError("E_STAGE_IMPROVEMENT_EVIDENCE_REQUIRED", "stage improvement needs regression test")
    unknown_improvements = set().union(*retrospective_improvement_refs.values()) - improvement_ids if retrospective_improvement_refs else set()
    if unknown_improvements:
        raise ContractError("E_RETROSPECTIVE_LINKAGE_INVALID", f"retrospective references unknown stage improvement: {sorted(unknown_improvements)}")


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
