#!/usr/bin/env python3
"""Generate a deterministic Phase10 real-subagent-run readiness dry-run fixture.

This does not dispatch workers and does not mutate the source paper repository.
It assembles run-owned dispatch, candidate-placeholder, validation, ledger, and
run-state records that prove the runtime can safely prepare a later real
subagent execution campaign.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from ppg_validate_common import load_document

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon"
DEFAULT_RUN_ROOT = ROOT / "runs" / "security-state-aware-mixed-platoon" / "phase10-readiness-dry-run"
REGISTRY = ROOT / "runtime" / "stage_registry.json"
VALIDATORS = ROOT / "runtime" / "phase10_content_validators.json"
OVERLAY_REGISTRY = ROOT / "runtime" / "stage_overlay_registry.json"
SCHEMA_VERSION = "ppg-run-state/v0.1"
RUN_ID = "security-state-aware-mixed-platoon.phase10-readiness-dry-run"
FIXED_GENERATED_AT = "2026-06-30T00:00:00Z"
NATURE_OVERLAY_ID = "nature_expert_writing"

BANNED_COMPLETION_PHRASES = [
    "final manuscript complete",
    "final paper complete",
    "submission ready",
    "ready to submit",
    "publication ready",
]

FORBIDDEN_SOURCE_RUNTIME_ARTIFACT_PREFIXES = (
    "docs/runtime-viewer",
)


def source_runtime_artifact_violations(snapshot: dict[str, Any]) -> list[str]:
    """Return source-paper paths/status rows that look like runtime/plugin artifacts.

    The local paper repository is a read-only source fixture. Runtime viewer,
    run, plugin, and generated control artifacts must stay in this plugin repo.
    """
    violations: set[str] = set()
    entries = snapshot.get("entries", {}) if isinstance(snapshot, dict) else {}
    if isinstance(entries, dict):
        for rel in entries:
            norm = str(rel).strip("/")
            for prefix in FORBIDDEN_SOURCE_RUNTIME_ARTIFACT_PREFIXES:
                if norm == prefix or norm.startswith(prefix + "/"):
                    violations.add(norm)
    status_rows = snapshot.get("git_status_porcelain_v1", []) if isinstance(snapshot, dict) else []
    if isinstance(status_rows, list):
        for row in status_rows:
            text = str(row)
            path_part = text[3:] if len(text) > 3 else text
            candidates = [path_part]
            if " -> " in path_part:
                candidates.extend(path_part.split(" -> "))
            for candidate in candidates:
                norm = candidate.strip().strip("/")
                for prefix in FORBIDDEN_SOURCE_RUNTIME_ARTIFACT_PREFIXES:
                    if norm == prefix or norm.startswith(prefix + "/"):
                        violations.add(norm)
    return sorted(violations)


def ensure_source_snapshot_no_runtime_artifacts(snapshot: dict[str, Any], *, context: str = "source snapshot") -> None:
    violations = source_runtime_artifact_violations(snapshot)
    if violations:
        joined = ", ".join(violations[:8])
        raise ValueError(f"{context} contains runtime/plugin artifacts under source paper repository: {joined}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def run_git(source_root: Path, args: list[str]) -> str:
    return subprocess.check_output(["git", "-C", str(source_root), *args], text=True)


def source_file_list(source_root: Path) -> list[str]:
    source_root = source_root.resolve(strict=True)
    rels: list[str] = []
    for path in source_root.rglob("*"):
        rel = path.relative_to(source_root)
        if ".git" in rel.parts or ".omx" in rel.parts:
            continue
        if path.is_file() or path.is_dir() or path.is_symlink():
            rels.append(rel.as_posix())
    return sorted(rels)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_source_snapshot(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve(strict=True)
    entries: dict[str, Any] = {}
    for rel in source_file_list(source_root):
        if rel.startswith(".git/"):
            continue
        path = source_root / rel
        try:
            stat = path.lstat()
        except FileNotFoundError:
            entries[rel] = {"kind": "missing"}
            continue
        if path.is_symlink():
            entries[rel] = {"kind": "symlink", "target": os.readlink(path), "size": stat.st_size}
        elif path.is_file():
            entries[rel] = {"kind": "file", "size": stat.st_size, "sha256": sha256_file(path)}
        elif path.is_dir():
            entries[rel] = {"kind": "directory", "size": stat.st_size}
        else:
            entries[rel] = {"kind": "other", "size": stat.st_size}
    status = run_git(source_root, ["status", "--porcelain=v1", "--untracked-files=all", "--", "."]).splitlines()
    return {
        "schema_version": "ppg-source-snapshot/v0.1",
        "source_root": str(source_root),
        "git_status_porcelain_v1": status,
        "entry_count": len(entries),
        "entries": entries,
    }


def ensure_run_root_safe(run_root: Path, source_root: Path) -> None:
    runtime_runs = (ROOT / "runs").resolve(strict=False)
    source_root = source_root.resolve(strict=True)
    resolved = run_root.resolve(strict=False)
    if run_root.exists() and run_root.is_symlink():
        raise ValueError(f"run root must not be a symlink: {run_root}")
    if not is_relative_to(resolved, runtime_runs):
        raise ValueError(f"run root must remain under runtime runs directory: {run_root}")
    if is_relative_to(resolved, source_root) or resolved == source_root:
        raise ValueError(f"run root must not be inside source paper repository: {run_root}")
    for parent in [run_root.parent, run_root.parent.parent]:
        if parent.exists() and parent.is_symlink():
            raise ValueError(f"run root parent must not be a symlink: {parent}")


def ensure_output_file_safe(path: Path, run_root: Path, source_root: Path) -> None:
    run_resolved = run_root.resolve(strict=True)
    resolved = path.resolve(strict=False)
    if not is_relative_to(resolved, run_resolved):
        raise ValueError(f"output path must stay inside run root: {path}")
    if is_relative_to(resolved, source_root.resolve(strict=True)):
        raise ValueError(f"output path must not point into source paper repository: {path}")
    if path.is_symlink():
        raise ValueError(f"output file must not be a symlink: {path}")
    if path.exists() and not path.is_file():
        raise ValueError(f"output path must be a regular file: {path}")


def write_json(path: Path, payload: Any, run_root: Path, source_root: Path) -> None:
    ensure_output_file_safe(path, run_root, source_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_output_file_safe(path, run_root, source_root)
    tmp_path = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if tmp_path.exists() or tmp_path.is_symlink():
        raise ValueError(f"temporary output already exists: {tmp_path}")
    try:
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def write_text(path: Path, text: str, run_root: Path, source_root: Path) -> None:
    ensure_output_file_safe(path, run_root, source_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_output_file_safe(path, run_root, source_root)
    tmp_path = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if tmp_path.exists() or tmp_path.is_symlink():
        raise ValueError(f"temporary output already exists: {tmp_path}")
    try:
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def validator_by_stage(validators: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["stage_id"]: item for item in validators.get("validators", []) if isinstance(item, dict) and "stage_id" in item}


def overlay_binding_by_stage(overlays: dict[str, Any], overlay_id: str = NATURE_OVERLAY_ID) -> dict[str, dict[str, Any]]:
    """Return stage-local overlay bindings keyed by canonical stage id."""
    overlay = next(
        (item for item in overlays.get("overlays", []) if isinstance(item, dict) and item.get("overlay_id") == overlay_id),
        None,
    )
    if not isinstance(overlay, dict):
        raise ValueError(f"required stage overlay not found: {overlay_id}")
    bindings = overlay.get("stage_bindings")
    if not isinstance(bindings, list):
        raise ValueError(f"stage overlay has no stage_bindings list: {overlay_id}")
    return {
        str(binding["stage_id"]): binding
        for binding in bindings
        if isinstance(binding, dict) and isinstance(binding.get("stage_id"), str)
    }


def stage_overlay_summary(stage_id: str, binding: dict[str, Any]) -> dict[str, Any]:
    """Small run-artifact summary; detailed content stays in the overlay registry."""
    return {
        "overlay_id": NATURE_OVERLAY_ID,
        "overlay_registry_ref": "runtime/stage_overlay_registry.json",
        "stage_id": stage_id,
        "binding_strength": binding.get("binding_strength"),
        "validator_ref": f"stage_overlay:{NATURE_OVERLAY_ID}:{stage_id}",
        "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
    }


def pilot_run_by_stage(pilot_root: Path, stage_id: str) -> dict[str, Any]:
    return load_json(pilot_root / "stage-runs" / f"{stage_id}.pilot-stage-run.json")


def stage_completion_claim(stage_id: str) -> str:
    return (
        f"{stage_id} phase10_real_run_readiness_only: dispatch packet, content validator, "
        "candidate placeholder, and ledger evidence are prepared; no final manuscript completion or submission claim is made."
    )


def build_candidate_placeholder(stage: dict[str, Any], validator: dict[str, Any], packet_ref: str | None, overlay_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ppg-phase10-candidate-placeholder/v0.1",
        "stage_id": stage["stage_id"],
        "stage_name": stage["stage_name"],
        "packet_ref": packet_ref,
        "validator_id": validator["validator_id"],
        "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
        "active_stage_overlays": [overlay_summary],
        "expected_outputs": stage.get("produces", []),
        "completion_boundary": "placeholder proves run readiness only; it is not worker-produced manuscript content",
    }


def load_task_packet_template(packet_ref: str) -> dict[str, Any]:
    packet, errors = load_document(ROOT / packet_ref)
    if errors:
        raise ValueError(f"cannot load template packet {packet_ref}: {errors[0].message}")
    if not isinstance(packet, dict):
        raise ValueError(f"template packet must be a mapping: {packet_ref}")
    return dict(packet)


def build_run_task_packet(template_packet: dict[str, Any], sid: str, candidate_ref: str, run_root: Path) -> dict[str, Any]:
    packet = dict(template_packet)
    output_repo_path = repo_rel(run_root / candidate_ref)
    packet["packet_id"] = f"{template_packet.get('packet_id')}.phase10_run"
    packet["allowed_write_paths"] = [output_repo_path]
    packet["output_artifact_path"] = output_repo_path
    packet["ingestion_target"] = output_repo_path
    packet["stop_condition"] = (
        f"{sid} candidate artifact written to the run-owned path only; "
        "return evidence without claiming graph, manuscript, or submission completion."
    )
    packet["failure_report_format"] = (
        "MissingMaterialReport with run-owned candidate path, consumed material ids, "
        "validator evidence, and no source-repository writes"
    )
    return packet


def generate(run_root: Path, pilot_root: Path) -> dict[str, Any]:
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    pilot_manifest = load_json(pilot_root / "manifest.json")
    source_root = Path(str(pilot_manifest["source_root"])).resolve(strict=True)
    ensure_run_root_safe(run_root, source_root)
    run_root.mkdir(parents=True, exist_ok=True)
    ensure_run_root_safe(run_root, source_root)

    registry = load_json(REGISTRY)
    validators = load_json(VALIDATORS)
    overlays = load_json(OVERLAY_REGISTRY)
    by_validator = validator_by_stage(validators)
    by_overlay_binding = overlay_binding_by_stage(overlays)
    before = compute_source_snapshot(source_root)
    ensure_source_snapshot_no_runtime_artifacts(before, context="phase10 source snapshot before")

    dispatch_records: list[dict[str, Any]] = []
    validation_records: list[dict[str, Any]] = []
    stage_states: list[dict[str, Any]] = []
    ledger_events: list[dict[str, Any]] = [
        {"event_id": "000-run-start", "event": "run_start", "run_id": RUN_ID, "generated_at": FIXED_GENERATED_AT}
    ]

    for index, stage in enumerate(registry["stages"], start=1):
        sid = stage["stage_id"]
        contract = load_json(ROOT / stage["contract_ref"])
        validator = by_validator[sid]
        overlay_binding = by_overlay_binding[sid]
        overlay_summary = stage_overlay_summary(sid, overlay_binding)
        pilot_run = pilot_run_by_stage(pilot_root, sid)
        packet_ref = contract.get("worker_packet_coverage", {}).get("packet_ref")
        packet_template_ref = packet_ref
        dispatch_ref = f"dispatch/{sid}.dispatch.json"
        validation_ref = f"validation/{sid}.validation.json"
        candidate_ref = f"candidate-artifacts/{sid}.candidate-placeholder.json"
        run_packet_ref = f"packets/{sid}.task-packet.json" if packet_template_ref else None
        completion_claim = stage_completion_claim(sid)
        if packet_template_ref:
            run_packet = build_run_task_packet(load_task_packet_template(str(packet_template_ref)), sid, candidate_ref, run_root)
            write_json(run_root / str(run_packet_ref), run_packet, run_root, source_root)
        dispatch = {
            "schema_version": "ppg-phase10-dispatch-record/v0.1",
            "run_id": RUN_ID,
            "stage_id": sid,
            "stage_name": stage["stage_name"],
            "stage_contract_ref": stage["contract_ref"],
            "packet_ref": run_packet_ref,
            "packet_template_ref": packet_template_ref,
            "content_validator_ref": "runtime/phase10_content_validators.json",
            "content_validator_id": validator["validator_id"],
            "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
            "active_stage_overlays": [overlay_summary],
            "source_read_only": True,
            "consumed_materials": pilot_run.get("consumed_materials", []),
            "candidate_output_path": candidate_ref,
            "worker_authority": {
                "completion_forbidden": True,
                "no_recursive_orchestration": True,
                "controller_owned_completion": True,
            },
            "completion_claim": completion_claim,
        }
        validation = {
            "schema_version": "ppg-phase10-stage-validation/v0.1",
            "run_id": RUN_ID,
            "stage_id": sid,
            "validator_id": validator["validator_id"],
            "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
            "active_stage_overlays": [overlay_summary],
            "stage_overlay_checks": overlay_binding.get("validator_checks", []),
            "dimension_count": len(validator.get("dimensions", [])),
            "required_checks": validator.get("required_checks", []),
            "status": "pass" if sid != "G02" else "owner_gated",
            "evidence": [
                f"{sid} StageContract is linked",
                f"{sid} PilotStageRun is present",
                f"{sid} content validator dimensions are present",
                f"{sid} Nature overlay binding is present",
            ],
            "completion_boundary": "validation proves run readiness only; controller retains completion authority",
        }
        candidate = build_candidate_placeholder(stage, validator, run_packet_ref, overlay_summary)
        write_json(run_root / dispatch_ref, dispatch, run_root, source_root)
        write_json(run_root / validation_ref, validation, run_root, source_root)
        write_json(run_root / candidate_ref, candidate, run_root, source_root)
        dispatch_records.append(dispatch)
        validation_records.append(validation)
        stage_states.append(
            {
                "stage_id": sid,
                "stage_name": stage["stage_name"],
                "status": "owner_gated_ready" if sid == "G02" else "ready_for_real_subagent_run",
                "requires_worker_task_packet": stage["requires_worker_task_packet"],
                "packet_ref": run_packet_ref,
                "packet_template_ref": packet_template_ref,
                "stage_contract_ref": stage["contract_ref"],
                "dispatch_ref": dispatch_ref,
                "validation_ref": validation_ref,
                "candidate_ref": candidate_ref,
                "content_validator_id": validator["validator_id"],
                "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
                "active_stage_overlays": [overlay_summary],
                "completion_claim": completion_claim,
            }
        )
        ledger_events.append({"event_id": f"{index:03d}-{sid}-dispatch", "event": "stage_dispatch", "stage_id": sid, "dispatch_ref": dispatch_ref})
        ledger_events.append({"event_id": f"{index:03d}-{sid}-validation", "event": "stage_validation", "stage_id": sid, "validation_ref": validation_ref})

    ledger_events.append({"event_id": "999-run-ready-boundary", "event": "run_ready_boundary", "run_id": RUN_ID, "completion_boundary": "Phase10 run readiness only; no final manuscript or submission-ready claim."})
    after = compute_source_snapshot(source_root)
    ensure_source_snapshot_no_runtime_artifacts(after, context="phase10 source snapshot after")
    manifest = {
        "schema_version": "ppg-phase10-run-manifest/v0.1",
        "run_id": RUN_ID,
        "project_slug": pilot_manifest.get("project_slug", "security-state-aware-mixed-platoon"),
        "generated_at": FIXED_GENERATED_AT,
        "runtime_root": str(ROOT),
        "run_root": repo_rel(run_root),
        "source_root": str(source_root),
        "pilot_root": repo_rel(pilot_root),
        "source_snapshot_scope": "all files, directories, and symlinks below source_root excluding .git and volatile .omx runtime state; git status is scoped to source_root",
        "source_read_only": True,
        "writes_to_source_allowed": False,
        "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
        "active_stage_overlays": [NATURE_OVERLAY_ID],
        "source_snapshot_before": before,
        "source_snapshot_after": after,
        "completion_boundary": "dry-run fixture for runtime readiness only; no worker execution and no final manuscript claim",
    }
    run_state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": RUN_ID,
        "project_slug": manifest["project_slug"],
        "source_read_only": True,
        "completion_boundary": "Phase10 real-subagent-run readiness only; no final manuscript completion, publication, or submission-ready claim.",
        "canonical_stage_ids": registry["canonical_stage_ids"],
        "stages": stage_states,
        "dispatch_count": len(dispatch_records),
        "validation_count": len(validation_records),
        "ledger_ref": "ledger.jsonl",
        "manifest_ref": "manifest.json",
        "content_validators_ref": "runtime/phase10_content_validators.json",
        "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
        "active_stage_overlays": [NATURE_OVERLAY_ID],
    }
    write_json(run_root / "manifest.json", manifest, run_root, source_root)
    write_json(run_root / "run_state.json", run_state, run_root, source_root)
    write_text(run_root / "ledger.jsonl", "".join(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n" for event in ledger_events), run_root, source_root)
    return run_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic Phase10 readiness dry-run fixture.")
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        state = generate(args.run_root, args.pilot_root)
    except Exception as exc:  # noqa: BLE001 - CLI guard normalization
        print(f"PHASE10_DRY_RUN_GENERATE_INVALID: {exc}", file=sys.stderr)
        return 1
    if args.check:
        try:
            from verify_phase10_run_readiness import verify_run_readiness
        except ImportError:  # pragma: no cover
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from verify_phase10_run_readiness import verify_run_readiness  # type: ignore  # noqa: E402
        errors = verify_run_readiness(args.run_root if args.run_root.is_absolute() else ROOT / args.run_root, args.pilot_root)
        if errors:
            print("INVALID Phase10 run readiness", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
    print("PHASE10_RUN_DRY_RUN_GENERATED")
    print(f"stages={len(state['stages'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
