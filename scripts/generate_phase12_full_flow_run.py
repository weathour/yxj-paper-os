#!/usr/bin/env python3
"""Generate a deterministic Phase12 formal full-flow runtime-test fixture.

Phase12 is a controller-owned formal runtime test. It writes only to a
run-owned directory under this repository and does not mutate the source paper
repository. It does not claim manuscript/submission/publication readiness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import (
        NATURE_OVERLAY_ID,
        OVERLAY_REGISTRY,
        ROOT,
        compute_source_snapshot,
        ensure_source_snapshot_no_runtime_artifacts,
        ensure_run_root_safe,
        is_relative_to,
        load_json,
        load_task_packet_template,
        overlay_binding_by_stage,
        repo_rel,
        stage_overlay_summary,
        write_json,
        write_text,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import (  # type: ignore  # noqa: E402
        NATURE_OVERLAY_ID,
        OVERLAY_REGISTRY,
        ROOT,
        compute_source_snapshot,
        ensure_source_snapshot_no_runtime_artifacts,
        ensure_run_root_safe,
        is_relative_to,
        load_json,
        load_task_packet_template,
        overlay_binding_by_stage,
        repo_rel,
        stage_overlay_summary,
        write_json,
        write_text,
    )

DEFAULT_PILOT = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon"
DEFAULT_RUN_ROOT = ROOT / "runs" / "security-state-aware-mixed-platoon" / "phase12-formal-full-flow-runtime-test"
REGISTRY = ROOT / "runtime" / "stage_registry.json"
VALIDATORS = ROOT / "runtime" / "phase10_content_validators.json"
RUN_ID = "security-state-aware-mixed-platoon.phase12-formal-full-flow-runtime-test"
SCHEMA_VERSION = "ppg-phase12-run-state/v0.1"
FIXED_GENERATED_AT = "2026-06-30T00:00:00Z"
OWNERSHIP_MARKER = ".phase12-run-root.json"
NEGATIVE_RUN_PREFIXES = (".phase12-negative-", ".phase12-negative.")

STAGE_STATUS_BY_ID = {
    "S00": "owner_boundary_validated",
    "S01": "candidate_validated",
    "S02": "candidate_validated",
    "S03": "candidate_validated",
    "S04": "candidate_validated",
    "S05": "candidate_validated",
    "S06": "candidate_validated",
    "S07": "candidate_validated",
    "S08": "candidate_validated",
    "S09A": "script_validated",
    "S09B": "script_validated",
    "S10": "candidate_validated",
    "S11": "candidate_validated",
    "S12": "candidate_validated",
    "S13": "review_finding_recorded",
    "S14": "backflow_task_compiled",
    "S15": "backflow_closed",
    "S16": "delivery_gate_passed",
    "G01": "governance_boundary_validated",
    "G02": "owner_gated_deferred",
}

BANNED_COMPLETION = "runtime-test completion only; candidate artifacts require controller validation and do not claim manuscript, submission, or publication readiness"


def validator_by_stage(validators: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["stage_id"]: item for item in validators.get("validators", []) if isinstance(item, dict) and "stage_id" in item}


def pilot_run_by_stage(pilot_root: Path, stage_id: str) -> dict[str, Any]:
    return load_json(pilot_root / "stage-runs" / f"{stage_id}.pilot-stage-run.json")


def _phase12_owner_doc(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.is_symlink() or not path.is_file():
        return None
    try:
        value = load_json(path)
    except Exception:  # noqa: BLE001
        return None
    return value if isinstance(value, dict) and value.get("run_id") == RUN_ID else None


def phase12_cleanup_scope_allowed(run_root: Path) -> tuple[bool, str]:
    runs_root = (ROOT / "runs").resolve(strict=False)
    resolved = run_root.resolve(strict=False)
    if resolved == runs_root:
        return False, "run root must not be the runtime runs container"
    try:
        rel_parts = resolved.relative_to(runs_root).parts
    except ValueError:
        return False, "run root must remain below runtime runs directory"
    if not rel_parts:
        return False, "run root must not be the runtime runs container"
    is_negative_probe = len(rel_parts) == 1 and rel_parts[0].startswith(NEGATIVE_RUN_PREFIXES)
    if len(rel_parts) < 2 and not is_negative_probe:
        return False, "run root must not be a broad project/container directory"
    return True, "ok"


def phase12_owned_existing_run_root(run_root: Path) -> bool:
    marker = _phase12_owner_doc(run_root / OWNERSHIP_MARKER)
    if marker is not None and marker.get("schema_version") == "ppg-phase12-run-root-owner/v0.1":
        return True
    manifest = _phase12_owner_doc(run_root / "manifest.json")
    return manifest is not None and manifest.get("schema_version") == "ppg-phase12-run-manifest/v0.1"


def write_ownership_marker(run_root: Path, source_root: Path) -> None:
    marker = {
        "schema_version": "ppg-phase12-run-root-owner/v0.1",
        "run_id": RUN_ID,
        "run_root": repo_rel(run_root),
        "ownership": "phase12-formal-full-flow-runtime-test",
        "cleanup_authority": "this directory may be cleaned only by Phase12 after this marker or a matching Phase12 manifest is present",
    }
    write_json(run_root / OWNERSHIP_MARKER, marker, run_root, source_root)


def clean_run_root(run_root: Path, source_root: Path) -> None:
    ensure_run_root_safe(run_root, source_root)
    scope_allowed, scope_reason = phase12_cleanup_scope_allowed(run_root)
    if not scope_allowed:
        raise ValueError(f"unsafe Phase12 run root cleanup target: {run_root}: {scope_reason}")
    if run_root.exists():
        if run_root.is_symlink():
            raise ValueError(f"run root must not be a symlink: {run_root}")
        if not run_root.is_dir():
            raise ValueError(f"run root must be a directory: {run_root}")
        resolved = run_root.resolve(strict=True)
        runs_root = (ROOT / "runs").resolve(strict=True)
        if not is_relative_to(resolved, runs_root) or is_relative_to(resolved, source_root.resolve(strict=True)):
            raise ValueError(f"unsafe Phase12 run root cleanup target: {run_root}")
        has_existing_content = any(run_root.iterdir())
        if has_existing_content and not phase12_owned_existing_run_root(run_root):
            raise ValueError(f"refusing to delete non-Phase12-owned run root: {run_root}")
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    ensure_run_root_safe(run_root, source_root)
    write_ownership_marker(run_root, source_root)


def build_phase12_task_packet(template_packet: dict[str, Any], sid: str, candidate_ref: str, run_root: Path) -> dict[str, Any]:
    packet = dict(template_packet)
    output_repo_path = repo_rel(run_root / candidate_ref)
    packet["packet_id"] = f"{template_packet.get('packet_id')}.phase12_run"
    packet["allowed_write_paths"] = [output_repo_path]
    packet["output_artifact_path"] = output_repo_path
    packet["ingestion_target"] = output_repo_path
    packet["stop_condition"] = (
        f"{sid} candidate artifact written to the run-owned Phase12 path only; "
        "return evidence without claiming graph, manuscript, submission, or publication completion."
    )
    packet["failure_report_format"] = (
        "MissingMaterialReport with run-owned candidate path, consumed material ids, "
        "validator evidence, and no source-repository writes"
    )
    return packet


def material_type_for(stage: dict[str, Any]) -> str:
    produces = stage.get("produces")
    if isinstance(produces, list) and produces:
        return str(produces[0]).replace(" ", "_").replace("/", "_")
    return f"{stage['stage_id'].lower()}_material"


def stage_material_id(stage_id: str) -> str:
    return f"phase12_{stage_id.lower()}_material_v1"


def stage_candidate_summary(stage: dict[str, Any], pilot_run: dict[str, Any]) -> str:
    return (
        f"Phase12 formal runtime-test candidate for {stage['stage_id']} ({stage['stage_name']}). "
        f"Consumes pilot materials {len(pilot_run.get('consumed_materials', []))}; "
        "records bounded controller-owned candidate evidence only."
    )


def build_candidate(
    run_root: Path,
    stage: dict[str, Any],
    pilot_run: dict[str, Any],
    validator: dict[str, Any],
    packet_ref: str | None,
    overlay_summary: dict[str, Any],
    produced_material: str,
) -> dict[str, Any]:
    sid = stage["stage_id"]
    return {
        "schema_version": "ppg-phase12-stage-candidate/v0.1",
        "run_id": RUN_ID,
        "stage_id": sid,
        "stage_name": stage["stage_name"],
        "packet_ref": packet_ref,
        "candidate_only": True,
        "controller_commit_required": True,
        "worker_completion_forbidden": True,
        "no_recursive_orchestration": True,
        "source_write_forbidden": True,
        "completion_boundary": BANNED_COMPLETION,
        "consumed_materials": pilot_run.get("consumed_materials", []),
        "produced_materials": [produced_material],
        "active_stage_overlays": [overlay_summary],
        "validator_refs": [validator["validator_id"], f"stage_overlay:{NATURE_OVERLAY_ID}:{sid}"],
        "content_summary": stage_candidate_summary(stage, pilot_run),
    }


def build_dispatch(
    stage: dict[str, Any],
    contract: dict[str, Any],
    pilot_run: dict[str, Any],
    validator: dict[str, Any],
    packet_ref: str | None,
    packet_template_ref: str | None,
    candidate_ref: str,
    overlay_summary: dict[str, Any],
) -> dict[str, Any]:
    sid = stage["stage_id"]
    return {
        "schema_version": "ppg-phase12-dispatch-record/v0.1",
        "run_id": RUN_ID,
        "stage_id": sid,
        "stage_name": stage["stage_name"],
        "stage_contract_ref": stage["contract_ref"],
        "packet_ref": packet_ref,
        "packet_template_ref": packet_template_ref,
        "content_validator_ref": "runtime/phase10_content_validators.json",
        "content_validator_id": validator["validator_id"],
        "candidate_output_path": candidate_ref,
        "source_read_only": True,
        "consumed_materials": pilot_run.get("consumed_materials", []),
        "active_stage_overlays": [overlay_summary],
        "worker_authority": {
            "completion_forbidden": True,
            "no_recursive_orchestration": True,
            "controller_owned_completion": True,
            "source_write_forbidden": True,
        },
        "owner_decision_refs": ["owner_decision_log.jsonl#source_write_policy"],
        "completion_boundary": BANNED_COMPLETION,
    }


def build_validation(stage: dict[str, Any], validator: dict[str, Any], candidate_ref: str, overlay_binding: dict[str, Any], overlay_summary: dict[str, Any]) -> dict[str, Any]:
    sid = stage["stage_id"]
    status = "owner_gated" if sid == "G02" else "pass_with_runtime_test_limitations"
    if sid in {"S00", "S09A", "S09B", "G01"}:
        status = "pass"
    return {
        "schema_version": "ppg-phase12-stage-validation/v0.1",
        "run_id": RUN_ID,
        "stage_id": sid,
        "validator_id": validator["validator_id"],
        "status": status,
        "candidate_ref": candidate_ref,
        "active_stage_overlays": [overlay_summary],
        "stage_overlay_checks": overlay_binding.get("validator_checks", []),
        "required_checks": validator.get("required_checks", []),
        "evidence": [
            f"{sid} candidate exists in run-owned path",
            f"{sid} StageContract is linked",
            f"{sid} content validator is linked",
            f"{sid} Nature overlay binding remains stage-local",
        ],
        "completion_boundary": BANNED_COMPLETION,
    }


def write_jsonl(path: Path, events: list[dict[str, Any]], run_root: Path, source_root: Path) -> None:
    write_text(path, "".join(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n" for event in events), run_root, source_root)


def generate(run_root: Path, pilot_root: Path) -> dict[str, Any]:
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    pilot_manifest = load_json(pilot_root / "manifest.json")
    source_root = Path(str(pilot_manifest["source_root"])).resolve(strict=True)
    clean_run_root(run_root, source_root)

    registry = load_json(REGISTRY)
    validators = load_json(VALIDATORS)
    overlays = load_json(OVERLAY_REGISTRY)
    by_validator = validator_by_stage(validators)
    by_overlay_binding = overlay_binding_by_stage(overlays)
    source_snapshot_before = compute_source_snapshot(source_root)
    ensure_source_snapshot_no_runtime_artifacts(source_snapshot_before, context="phase12 source snapshot before")

    stage_states: list[dict[str, Any]] = []
    stage_statuses: list[dict[str, Any]] = []
    materials: list[dict[str, Any]] = []
    frontier_events: list[dict[str, Any]] = []
    dispatch_ledger: list[dict[str, Any]] = []
    validation_ledger: list[dict[str, Any]] = []
    global_ledger: list[dict[str, Any]] = [
        {"event_id": "000-run-start", "event": "run_start", "run_id": RUN_ID, "artifact_ref": "manifest.json"}
    ]
    owner_log: list[dict[str, Any]] = [
        {
            "event_id": "owner-001-boundary",
            "event": "owner_boundary_assumption",
            "run_id": RUN_ID,
            "stage_id": "S00",
            "decision": "Use current source-paper mainline and Phase11 overlay-aware runtime boundaries for formal test.",
            "writes_to_source_allowed": False,
        },
        {
            "event_id": "owner-002-source-write-policy",
            "event": "source_write_policy",
            "run_id": RUN_ID,
            "stage_id": "G01",
            "decision": "All Phase12 outputs remain in the runtime run root; source-paper writes are forbidden.",
            "writes_to_source_allowed": False,
        },
    ]

    canonical_ids = list(registry["canonical_stage_ids"])
    upstream_materials: list[str] = []
    for index, stage in enumerate(registry["stages"], start=1):
        sid = stage["stage_id"]
        contract = load_json(ROOT / stage["contract_ref"])
        validator = by_validator[sid]
        overlay_binding = by_overlay_binding[sid]
        overlay_summary = stage_overlay_summary(sid, overlay_binding)
        pilot_run = pilot_run_by_stage(pilot_root, sid)
        coverage = contract.get("worker_packet_coverage", {}) if isinstance(contract.get("worker_packet_coverage"), dict) else {}
        packet_template_ref = coverage.get("packet_ref") if stage.get("requires_worker_task_packet") else None
        candidate_ref = f"candidate-artifacts/{sid}.candidate.json"
        dispatch_ref = f"dispatch/{sid}.dispatch.json"
        validation_ref = f"validation/{sid}.validation.json"
        packet_ref = f"packets/{sid}.task-packet.json" if packet_template_ref else None
        produced_material = stage_material_id(sid)

        if packet_template_ref:
            run_packet = build_phase12_task_packet(load_task_packet_template(str(packet_template_ref)), sid, candidate_ref, run_root)
            write_json(run_root / str(packet_ref), run_packet, run_root, source_root)

        candidate = build_candidate(run_root, stage, pilot_run, validator, packet_ref, overlay_summary, produced_material)
        dispatch = build_dispatch(stage, contract, pilot_run, validator, packet_ref, packet_template_ref, candidate_ref, overlay_summary)
        validation = build_validation(stage, validator, candidate_ref, overlay_binding, overlay_summary)

        write_json(run_root / candidate_ref, candidate, run_root, source_root)
        write_json(run_root / dispatch_ref, dispatch, run_root, source_root)
        write_json(run_root / validation_ref, validation, run_root, source_root)

        material_status = "committed_for_runtime_test"
        stale = False
        if sid == "S10":
            material_status = "stale"
            stale = True
        if sid == "S15":
            material_status = "repaired"
        material = {
            "material_id": produced_material,
            "material_type": material_type_for(stage),
            "producer_stage": sid,
            "version": "v1",
            "status": material_status,
            "candidate_ref": candidate_ref,
            "validation_ref": validation_ref,
            "consumed_by": [canonical_ids[index]] if index < len(canonical_ids) else [],
            "support_strength": "runtime_test_evidence",
            "stale": stale,
        }
        materials.append(material)

        ready_inputs = list(upstream_materials[-3:]) or pilot_run.get("consumed_materials", [])[:3]
        stage_statuses.append(
            {
                "stage_id": sid,
                "status": STAGE_STATUS_BY_ID[sid],
                "ready_inputs": ready_inputs,
                "produced_materials": [produced_material],
                "candidate_ref": candidate_ref,
                "validation_ref": validation_ref,
                "blocked_reason": None if sid != "G02" else "post-paper derivative outputs require explicit owner request",
                "stale_materials": [stage_material_id("S10")] if sid == "S15" else [],
                "next_frontier_hint": canonical_ids[index] if index < len(canonical_ids) else "delivery-gate/delivery_gate.json",
            }
        )
        frontier_events.append(
            {
                "event_id": f"frontier-{index:03d}-{sid}",
                "stage_id": sid,
                "reason": "dependency_topology_then_blocker_then_owner_gate_then_frontier",
                "consumed_materials": ready_inputs,
                "produced_materials": [produced_material],
                "controller_decision": "record deterministic Phase12 runtime-test candidate and validator evidence",
            }
        )
        stage_states.append(
            {
                "stage_id": sid,
                "stage_name": stage["stage_name"],
                "status": STAGE_STATUS_BY_ID[sid],
                "execution_mode": stage["execution_mode"],
                "requires_worker_task_packet": stage["requires_worker_task_packet"],
                "stage_contract_ref": stage["contract_ref"],
                "packet_ref": packet_ref,
                "packet_template_ref": packet_template_ref,
                "candidate_ref": candidate_ref,
                "validation_ref": validation_ref,
                "dispatch_ref": dispatch_ref,
                "material_ids": [produced_material],
                "active_stage_overlays": [overlay_summary],
                "controller_owned_completion": True,
                "worker_completion_forbidden": True,
                "completion_boundary": BANNED_COMPLETION,
            }
        )
        dispatch_ledger.append(
            {
                "event_id": f"dispatch-{index:03d}-{sid}",
                "event": "dispatch_recorded",
                "run_id": RUN_ID,
                "stage_id": sid,
                "dispatch_ref": dispatch_ref,
                "candidate_ref": candidate_ref,
                "packet_ref": packet_ref,
                "worker_authority": dispatch["worker_authority"],
            }
        )
        validation_ledger.append(
            {
                "event_id": f"validation-{index:03d}-{sid}",
                "event": "validation_recorded",
                "run_id": RUN_ID,
                "stage_id": sid,
                "validation_ref": validation_ref,
                "status": validation["status"],
                "validator_id": validator["validator_id"],
            }
        )
        global_ledger.extend(
            [
                {"event_id": f"{index:03d}-{sid}-dispatch", "event": "dispatch_recorded", "run_id": RUN_ID, "stage_id": sid, "artifact_ref": dispatch_ref},
                {"event_id": f"{index:03d}-{sid}-candidate", "event": "candidate_recorded", "run_id": RUN_ID, "stage_id": sid, "artifact_ref": candidate_ref},
                {"event_id": f"{index:03d}-{sid}-validation", "event": "validation_recorded", "run_id": RUN_ID, "stage_id": sid, "artifact_ref": validation_ref},
            ]
        )
        upstream_materials.append(produced_material)

    finding_ref = "review-findings/S13-overclaim-locality.review-finding.json"
    task_ref = "backflow-tasks/S14-overclaim-locality.backflow-task.json"
    repair_ref = "repair-artifacts/S15-overclaim-locality.repair-candidate.json"
    closure_ref = "closures/S15-overclaim-locality.review-closure.json"
    finding = {
        "schema_version": "ppg-phase12-review-finding/v0.1",
        "finding_id": "phase12_overclaim_locality_finding_v1",
        "run_id": RUN_ID,
        "source_stage_id": "S13",
        "failure_type": "claim_overreach",
        "target_material_id": stage_material_id("S04"),
        "severity": "medium",
        "locality_scope": [stage_material_id("S04"), stage_material_id("S10")],
        "whole_paper_rewrite_authorized": False,
        "completion_boundary": BANNED_COMPLETION,
    }
    backflow_task = {
        "schema_version": "ppg-phase12-backflow-task/v0.1",
        "backflow_task_id": "phase12_overclaim_locality_backflow_v1",
        "run_id": RUN_ID,
        "source_finding_ref": finding_ref,
        "target_stage_id": "S14",
        "repair_stage_id": "S15",
        "affected_materials": [stage_material_id("S04"), stage_material_id("S10")],
        "unaffected_materials": [stage_material_id("S02"), stage_material_id("S08"), stage_material_id("S11")],
        "owner_gate_required": False,
        "expected_repair_candidate_ref": repair_ref,
        "completion_boundary": BANNED_COMPLETION,
    }
    repair = {
        "schema_version": "ppg-phase12-repair-candidate/v0.1",
        "repair_candidate_id": "phase12_overclaim_locality_repair_v1",
        "run_id": RUN_ID,
        "stage_id": "S15",
        "source_backflow_task_ref": task_ref,
        "candidate_only": True,
        "controller_commit_required": True,
        "affected_materials_repaired": [stage_material_id("S04"), stage_material_id("S10")],
        "unaffected_materials_preserved": [stage_material_id("S02"), stage_material_id("S08"), stage_material_id("S11")],
        "completion_boundary": BANNED_COMPLETION,
    }
    closure = {
        "schema_version": "ppg-phase12-review-closure/v0.1",
        "closure_id": "phase12_overclaim_locality_closure_v1",
        "run_id": RUN_ID,
        "source_finding_ref": finding_ref,
        "source_backflow_task_ref": task_ref,
        "repair_candidate_ref": repair_ref,
        "status": "closed_for_runtime_test",
        "delivery_gate_consumed": True,
        "completion_boundary": BANNED_COMPLETION,
    }
    write_json(run_root / finding_ref, finding, run_root, source_root)
    write_json(run_root / task_ref, backflow_task, run_root, source_root)
    write_json(run_root / repair_ref, repair, run_root, source_root)
    write_json(run_root / closure_ref, closure, run_root, source_root)
    backflow_ledger = [
        {"event_id": "backflow-001-finding", "event": "review_finding_recorded", "run_id": RUN_ID, "stage_id": "S13", "finding_ref": finding_ref},
        {"event_id": "backflow-002-task", "event": "backflow_task_compiled", "run_id": RUN_ID, "stage_id": "S14", "source_finding_ref": finding_ref, "backflow_task_ref": task_ref},
        {"event_id": "backflow-003-repair", "event": "repair_candidate_recorded", "run_id": RUN_ID, "stage_id": "S15", "source_backflow_task_ref": task_ref, "repair_candidate_ref": repair_ref},
        {"event_id": "backflow-004-closure", "event": "review_closure_recorded", "run_id": RUN_ID, "stage_id": "S15", "source_finding_ref": finding_ref, "source_backflow_task_ref": task_ref, "repair_candidate_ref": repair_ref, "closure_ref": closure_ref},
    ]
    global_ledger.extend(backflow_ledger)

    delivery = {
        "schema_version": "ppg-phase12-delivery-gate/v0.1",
        "run_id": RUN_ID,
        "stage_id": "S16",
        "verdict": "pass_for_runtime_test_only",
        "consumed_stage_count": len(canonical_ids),
        "consumed_stage_ids": canonical_ids,
        "consumed_closure_refs": [closure_ref],
        "source_read_only_verified": True,
        "no_final_manuscript_claim": True,
        "no_submission_ready_claim": True,
        "completion_boundary": "Phase12 formal runtime-test gate passed for controller flow only; no manuscript or submission readiness claim is made.",
        "open_risks": [
            "Deterministic candidates are runtime-test evidence, not live worker manuscript quality evidence.",
            "A later phase may replace deterministic candidates with live subagent returns.",
        ],
    }
    write_json(run_root / "delivery-gate/delivery_gate.json", delivery, run_root, source_root)
    global_ledger.append({"event_id": "998-delivery-gate", "event": "delivery_gate_recorded", "run_id": RUN_ID, "stage_id": "S16", "artifact_ref": "delivery-gate/delivery_gate.json"})
    global_ledger.append({"event_id": "999-run-complete-runtime-test-only", "event": "run_complete_runtime_test_only", "run_id": RUN_ID, "artifact_ref": "final-report.md"})

    source_snapshot_after = compute_source_snapshot(source_root)
    ensure_source_snapshot_no_runtime_artifacts(source_snapshot_after, context="phase12 source snapshot after")
    write_json(run_root / "source_snapshot.before.json", source_snapshot_before, run_root, source_root)
    write_json(run_root / "source_snapshot.after.json", source_snapshot_after, run_root, source_root)

    manifest = {
        "schema_version": "ppg-phase12-run-manifest/v0.1",
        "run_id": RUN_ID,
        "project_slug": pilot_manifest.get("project_slug", "security-state-aware-mixed-platoon"),
        "generated_at": FIXED_GENERATED_AT,
        "runtime_root": ".",
        "run_root": repo_rel(run_root),
        "source_root": str(source_root),
        "pilot_root": repo_rel(pilot_root),
        "source_read_only": True,
        "writes_to_source_allowed": False,
        "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
        "active_stage_overlays": [NATURE_OVERLAY_ID],
        "source_snapshot_scope": "referenced snapshot files cover all files, directories, and symlinks below source_root excluding .git and volatile .omx runtime state; git status is scoped to source_root",
        "source_snapshot_before_ref": "source_snapshot.before.json",
        "source_snapshot_after_ref": "source_snapshot.after.json",
        "completion_boundary": "Phase12 formal runtime-test fixture only; no manuscript, submission, or publication readiness claim.",
    }
    run_state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": RUN_ID,
        "project_slug": manifest["project_slug"],
        "source_read_only": True,
        "completion_boundary": "Phase12 formal full-flow runtime-test only; controller-owned candidate flow and local backflow are verified without claiming manuscript or submission readiness.",
        "canonical_stage_ids": canonical_ids,
        "stages": stage_states,
        "stage_status_ref": "stage_status.json",
        "material_inventory_ref": "material_inventory.json",
        "frontier_queue_ref": "frontier_queue.json",
        "ledger_ref": "ledger.jsonl",
        "dispatch_ledger_ref": "dispatch_ledger.jsonl",
        "validation_ledger_ref": "validation_ledger.jsonl",
        "backflow_ledger_ref": "backflow_ledger.jsonl",
        "owner_decision_log_ref": "owner_decision_log.jsonl",
        "delivery_gate_ref": "delivery-gate/delivery_gate.json",
        "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
        "active_stage_overlays": [NATURE_OVERLAY_ID],
    }
    stage_status_doc = {"schema_version": "ppg-phase12-stage-status/v0.1", "run_id": RUN_ID, "stages": stage_statuses}
    material_inventory = {"schema_version": "ppg-phase12-material-inventory/v0.1", "run_id": RUN_ID, "materials": materials}
    frontier_queue = {
        "schema_version": "ppg-phase12-frontier-queue/v0.1",
        "run_id": RUN_ID,
        "selection_policy": "dependency_topology_then_blocker_then_owner_gate_then_frontier",
        "frontier_events": frontier_events,
    }
    final_report = f"""# Phase12 Formal Full-Flow Runtime Test Report

Run id: `{RUN_ID}`

Verdict: `pass_for_runtime_test_only`

This report records a deterministic controller-owned formal runtime test over all {len(canonical_ids)} canonical PPG stages. It is not a manuscript, submission, or publication readiness claim.

## Evidence

- Source snapshots are referenced by `source_snapshot.before.json` and `source_snapshot.after.json`.
- Stage records: {len(stage_states)}.
- Candidate artifacts: {len(stage_states)}.
- Worker packets: {sum(1 for stage in stage_states if stage['packet_ref'])}.
- Backflow sequence: `review_finding_recorded -> backflow_task_compiled -> repair_candidate_recorded -> review_closure_recorded`.
- Delivery gate: `delivery-gate/delivery_gate.json`.

## Boundary

All Phase12 outputs are under `{repo_rel(run_root)}`. Source-paper writes remain forbidden.
"""

    write_json(run_root / "manifest.json", manifest, run_root, source_root)
    write_json(run_root / "run_state.json", run_state, run_root, source_root)
    write_json(run_root / "stage_status.json", stage_status_doc, run_root, source_root)
    write_json(run_root / "material_inventory.json", material_inventory, run_root, source_root)
    write_json(run_root / "frontier_queue.json", frontier_queue, run_root, source_root)
    write_jsonl(run_root / "dispatch_ledger.jsonl", dispatch_ledger, run_root, source_root)
    write_jsonl(run_root / "validation_ledger.jsonl", validation_ledger, run_root, source_root)
    write_jsonl(run_root / "backflow_ledger.jsonl", backflow_ledger, run_root, source_root)
    write_jsonl(run_root / "owner_decision_log.jsonl", owner_log, run_root, source_root)
    write_jsonl(run_root / "ledger.jsonl", global_ledger, run_root, source_root)
    write_text(run_root / "final-report.md", final_report, run_root, source_root)
    return run_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic Phase12 formal full-flow runtime-test fixture.")
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        state = generate(args.run_root, args.pilot_root)
    except Exception as exc:  # noqa: BLE001
        print(f"PHASE12_FULL_FLOW_GENERATE_INVALID: {exc}", file=sys.stderr)
        return 1
    if args.check:
        try:
            from verify_phase12_full_flow_run import verify_phase12_run
        except ImportError:  # pragma: no cover
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from verify_phase12_full_flow_run import verify_phase12_run  # type: ignore  # noqa: E402
        errors = verify_phase12_run(args.run_root if args.run_root.is_absolute() else ROOT / args.run_root, args.pilot_root)
        if errors:
            print("INVALID Phase12 full-flow run", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
    print("PHASE12_FULL_FLOW_RUN_GENERATED")
    print(f"stages={len(state['stages'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
