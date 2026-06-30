#!/usr/bin/env python3
"""Generate Phase13 live native-subagent pilot scaffold.

This script creates run-owned producer/verifier packets and dispatch prompts for
all canonical PPG stages. It does not dispatch agents; the main controller does
that and later records raw returns/provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import ROOT, compute_source_snapshot, ensure_run_root_safe, ensure_source_snapshot_no_runtime_artifacts, is_relative_to, load_json, repo_rel, write_json, write_text
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import ROOT, compute_source_snapshot, ensure_run_root_safe, ensure_source_snapshot_no_runtime_artifacts, is_relative_to, load_json, repo_rel, write_json, write_text  # type: ignore  # noqa: E402

DEFAULT_PILOT = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon"
DEFAULT_RUN_ROOT = ROOT / "runs" / "security-state-aware-mixed-platoon" / "phase13-live-subagent-full-flow-pilot"
REGISTRY = ROOT / "runtime" / "stage_registry.json"
PHASE12_RUN = ROOT / "runs" / "security-state-aware-mixed-platoon" / "phase12-formal-full-flow-runtime-test"
RUN_ID = "security-state-aware-mixed-platoon.phase13-live-subagent-full-flow-pilot"
SCHEMA_VERSION = "ppg-phase13-run-state/v0.1"
FIXED_GENERATED_AT = "2026-06-30T00:00:00Z"
OWNERSHIP_MARKER = ".phase13-run-root.json"
NEGATIVE_PREFIXES = (".phase13-negative-", ".phase13-negative.")

NON_WORKER_AUTHORITY = "assessment_only"
WORKER_AUTHORITY = "production_candidate"
BANNED_COMPLETION = "Phase13 live subagent pilot only; no manuscript, submission, or publication readiness claim."

PRODUCER_ROLE_BY_STAGE = {
    "S00": "analyst", "S01": "researcher", "S02": "researcher", "S03": "analyst", "S04": "analyst",
    "S05": "architect", "S06": "architect", "S07": "writer", "S08": "designer", "S09A": "analyst",
    "S09B": "executor", "S10": "writer", "S11": "designer", "S12": "architect", "S13": "critic",
    "S14": "planner", "S15": "executor", "S16": "git-master", "G01": "architect", "G02": "analyst",
}

LIMITATION_BY_STAGE = {
    "S00": "needs_human_owner_decision", "G02": "needs_human_owner_decision",
    "S09B": "script_or_registry_assessment_only", "G01": "script_or_registry_assessment_only",
    "S01": "needs_downstream_integration", "S09A": "needs_downstream_integration", "S14": "needs_downstream_integration", "S16": "needs_downstream_integration",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_slug(stage: dict[str, Any]) -> str:
    return str(stage["stage_name"]).lower().replace(" ", "-").replace("/", "-")


def validator_by_stage() -> dict[str, dict[str, Any]]:
    validators = load_json(ROOT / "runtime" / "phase10_content_validators.json")
    return {item["stage_id"]: item for item in validators.get("validators", []) if isinstance(item, dict) and item.get("stage_id")}


def pilot_run_by_stage(pilot_root: Path, sid: str) -> dict[str, Any]:
    return load_json(pilot_root / "stage-runs" / f"{sid}.pilot-stage-run.json")


def source_brief(pilot_manifest: dict[str, Any]) -> dict[str, Any]:
    claim = pilot_manifest.get("claim_boundary", {}) if isinstance(pilot_manifest.get("claim_boundary"), dict) else {}
    return {
        "project_slug": pilot_manifest.get("project_slug"),
        "active_method": claim.get("active_method"),
        "method_name": claim.get("method_name"),
        "evidence_spine": claim.get("evidence_spine"),
        "non_text_evidence_spine": claim.get("non_text_evidence_spine"),
        "validation_scope": claim.get("validation_scope"),
        "zero_trust_boundary": claim.get("zero_trust_boundary"),
    }


def phase13_scope_allowed(run_root: Path) -> tuple[bool, str]:
    runs_root = (ROOT / "runs").resolve(strict=False)
    resolved = run_root.resolve(strict=False)
    if resolved == runs_root:
        return False, "run root must not be runtime runs container"
    try:
        rel_parts = resolved.relative_to(runs_root).parts
    except ValueError:
        return False, "run root must remain under runtime runs directory"
    is_negative = len(rel_parts) == 1 and rel_parts[0].startswith(NEGATIVE_PREFIXES)
    if len(rel_parts) < 2 and not is_negative:
        return False, "run root must not be a broad project/container directory"
    return True, "ok"


def owner_doc(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.is_symlink() or not path.is_file():
        return None
    try:
        value = load_json(path)
    except Exception:  # noqa: BLE001
        return None
    return value if isinstance(value, dict) and value.get("run_id") == RUN_ID else None


def owned_existing_run_root(run_root: Path) -> bool:
    marker = owner_doc(run_root / OWNERSHIP_MARKER)
    if marker is not None and marker.get("schema_version") == "ppg-phase13-run-root-owner/v0.1":
        return True
    manifest = owner_doc(run_root / "manifest.json")
    return manifest is not None and manifest.get("schema_version") == "ppg-phase13-run-manifest/v0.1"


def clean_run_root(run_root: Path, source_root: Path) -> None:
    ensure_run_root_safe(run_root, source_root)
    allowed, reason = phase13_scope_allowed(run_root)
    if not allowed:
        raise ValueError(f"unsafe Phase13 run root cleanup target: {run_root}: {reason}")
    if run_root.exists():
        if run_root.is_symlink() or not run_root.is_dir():
            raise ValueError(f"unsafe Phase13 run root: {run_root}")
        resolved = run_root.resolve(strict=True)
        runs_root = (ROOT / "runs").resolve(strict=True)
        if not is_relative_to(resolved, runs_root) or is_relative_to(resolved, source_root.resolve(strict=True)):
            raise ValueError(f"unsafe Phase13 run root cleanup target: {run_root}")
        if any(run_root.iterdir()) and not owned_existing_run_root(run_root):
            raise ValueError(f"refusing to delete non-Phase13-owned run root: {run_root}")
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    ensure_run_root_safe(run_root, source_root)
    write_json(run_root / OWNERSHIP_MARKER, {
        "schema_version": "ppg-phase13-run-root-owner/v0.1",
        "run_id": RUN_ID,
        "run_root": repo_rel(run_root),
        "ownership": "phase13-live-subagent-full-flow-pilot",
        "cleanup_authority": "Phase13 may clean this directory only after this marker or matching manifest is present",
    }, run_root, source_root)


def authority_for(stage: dict[str, Any]) -> str:
    return WORKER_AUTHORITY if stage.get("requires_worker_task_packet") else NON_WORKER_AUTHORITY


def build_packet(stage: dict[str, Any], lane: str, pilot_run: dict[str, Any], validator: dict[str, Any], pilot_manifest: dict[str, Any]) -> dict[str, Any]:
    sid = stage["stage_id"]
    authority = authority_for(stage)
    packet_ref = f"packets/{lane}/{sid}.{lane}-packet.json"
    return {
        "schema_version": "ppg-phase13-live-task-packet/v0.1",
        "run_id": RUN_ID,
        "packet_id": f"phase13.{sid}.{lane}",
        "stage_id": sid,
        "stage_name": stage["stage_name"],
        "lane": lane,
        "agent_type": "verifier" if lane == "verifier" else PRODUCER_ROLE_BY_STAGE[sid],
        "authority_mode": authority,
        "requires_worker_task_packet": bool(stage.get("requires_worker_task_packet")),
        "stage_contract_ref": stage.get("contract_ref"),
        "content_validator_id": validator.get("validator_id"),
        "source_brief": source_brief(pilot_manifest),
        "consumes": stage.get("consumes", []),
        "produces": stage.get("produces", []),
        "pilot_consumed_materials": pilot_run.get("consumed_materials", []),
        "phase12_candidate_ref": f"{repo_rel(PHASE12_RUN)}/candidate-artifacts/{sid}.candidate.json",
        "packet_ref": packet_ref,
        "output_return_ref": f"returns/{lane}/{sid}.{lane}-return.md",
        **({
            "producer_return_ref": f"returns/producer/{sid}.producer-return.md",
            "producer_return_sha256": None,
            "producer_thread_id": None,
        } if lane == "verifier" else {}),
        "controller_owned_completion": True,
        "worker_completion_forbidden": True,
        "no_recursive_orchestration": True,
        "source_write_forbidden": True,
        "legacy_routes_forbidden": ["legacy department-loop yxj-paper-os route", "$yxj-plugin-incubator"],
        "completion_boundary": BANNED_COMPLETION,
        "instructions": [
            f"Cite this packet path exactly: {packet_ref}",
            f"Address stage {sid}: {stage['stage_name']} specifically.",
            "Return text only; do not edit files.",
            "Do not dispatch agents, do not mark final completion, do not claim manuscript/submission/publication readiness.",
            "If authority_mode is assessment_only, assess/report only and do not authorize or rewrite controller/script/owner-gated outputs.",
        ],
    }


def build_prompt(packet: dict[str, Any], stage: dict[str, Any], lane: str) -> str:
    sid = stage["stage_id"]
    packet_ref = packet["packet_ref"]
    producer_grounding = ""
    if lane == "producer":
        role_task = "produce a stage-specific candidate/effect report"
        required = "Candidate material / Assessment; Actual effect; Limitations; Downstream usefulness; Boundary statement"
        verdict = "Do not include a final verifier verdict."
    else:
        role_task = "independently verify the producer return and judge its stage effect"
        required = "Verdict; Independent critique; Dimension scores; Limitations; Repair locality if needed; Boundary statement"
        verdict = "Verdict must be exactly one of: accept, accept_with_limitations, needs_repair, reject."
        producer_grounding = f"""
Producer return grounding:
- producer_return_ref: {packet.get('producer_return_ref')}
- producer_return_sha256: {packet.get('producer_return_sha256') or 'pending-until-producer-recorded'}
- producer_thread_id: {packet.get('producer_thread_id') or 'pending-until-producer-recorded'}
You must consume the producer return above and refer to it as the producer return in your critique.
"""
    return f"""You are a Phase13 live-subagent {lane} lane for the PPG runtime.

Repository: /home/weathour/plugins/yxj-paper-os
Stage: {sid} — {stage['stage_name']}
Packet citation: {packet_ref}
Agent type requested: {packet['agent_type']}
Authority mode: {packet['authority_mode']}

Task: {role_task} for this exact stage, using the packet content below and the local-paper pilot context. Return text only in your final answer; do not edit files.

Required sections: {required}.
{verdict}
{producer_grounding}
Hard boundaries:
- Cite `{packet_ref}` exactly.
- Mention stage `{sid}` and `{stage['stage_name']}`.
- Do not claim final manuscript completion, submission readiness, or publication readiness.
- Do not dispatch agents or claim controller completion authority.
- Do not revive the legacy department-loop yxj-paper-os route or $yxj-plugin-incubator as active routes.
- If authority mode is assessment_only, only assess/report; do not authorize owner/script/control outputs.

Packet JSON:
```json
{json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)}
```
"""


def generate(run_root: Path, pilot_root: Path) -> dict[str, Any]:
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    pilot_manifest = load_json(pilot_root / "manifest.json")
    source_root = Path(str(pilot_manifest["source_root"])).resolve(strict=True)
    clean_run_root(run_root, source_root)

    registry = load_json(REGISTRY)
    validators = validator_by_stage()
    source_snapshot_before = compute_source_snapshot(source_root)
    ensure_source_snapshot_no_runtime_artifacts(source_snapshot_before, context="phase13 source snapshot before")
    write_json(run_root / "source_snapshot.before.json", source_snapshot_before, run_root, source_root)

    stages_out: list[dict[str, Any]] = []
    dispatch_events: list[dict[str, Any]] = []
    thread_rows: list[dict[str, Any]] = []
    for index, stage in enumerate(registry["stages"], start=1):
        sid = stage["stage_id"]
        pilot_run = pilot_run_by_stage(pilot_root, sid)
        validator = validators.get(sid, {})
        stage_record = {
            "stage_id": sid,
            "stage_name": stage["stage_name"],
            "execution_mode": stage.get("execution_mode"),
            "requires_worker_task_packet": bool(stage.get("requires_worker_task_packet")),
            "authority_mode": authority_for(stage),
            "producer_packet_ref": f"packets/producer/{sid}.producer-packet.json",
            "verifier_packet_ref": f"packets/verifier/{sid}.verifier-packet.json",
            "producer_prompt_ref": f"prompts/producer/{sid}.producer-prompt.md",
            "verifier_prompt_ref": f"prompts/verifier/{sid}.verifier-prompt.md",
            "producer_return_ref": f"returns/producer/{sid}.producer-return.md",
            "verifier_return_ref": f"returns/verifier/{sid}.verifier-return.md",
            "effect_ref": f"stage_effects/{sid}.effect.json",
            "validation_ref": f"validation/{sid}.live-validation.json",
            "controller_owned_completion": True,
            "worker_completion_forbidden": True,
        }
        stages_out.append(stage_record)
        for lane in ["producer", "verifier"]:
            packet = build_packet(stage, lane, pilot_run, validator, pilot_manifest)
            prompt = build_prompt(packet, stage, lane)
            packet_path = run_root / str(stage_record[f"{lane}_packet_ref"])
            prompt_path = run_root / str(stage_record[f"{lane}_prompt_ref"])
            write_json(packet_path, packet, run_root, source_root)
            write_text(prompt_path, prompt, run_root, source_root)
            dispatch = {
                "schema_version": "ppg-phase13-dispatch/v0.1",
                "run_id": RUN_ID,
                "event_id": f"dispatch-{index:03d}-{sid}-{lane}",
                "event": "dispatch_prepared",
                "stage_id": sid,
                "lane": lane,
                "agent_type": packet["agent_type"],
                "authority_mode": packet["authority_mode"],
                "packet_ref": stage_record[f"{lane}_packet_ref"],
                "packet_sha256": sha256_file(packet_path),
                "dispatch_prompt_ref": stage_record[f"{lane}_prompt_ref"],
                "dispatch_prompt_sha256": sha256_file(prompt_path),
                "raw_return_ref": stage_record[f"{lane}_return_ref"],
                "status": "prepared",
            }
            write_json(run_root / f"dispatch/{lane}/{sid}.{lane}-dispatch.json", dispatch, run_root, source_root)
            dispatch_events.append(dispatch)
            thread_rows.append({
                "schema_version": "ppg-phase13-subagent-thread/v0.1",
                "run_id": RUN_ID,
                "stage_id": sid,
                "lane": lane,
                "thread_id": None,
                "agent_type": packet["agent_type"],
                "native_subagent": True,
                "started_at": None,
                "completed_at": None,
                "packet_ref": stage_record[f"{lane}_packet_ref"],
                "packet_sha256": dispatch["packet_sha256"],
                "dispatch_prompt_ref": stage_record[f"{lane}_prompt_ref"],
                "dispatch_prompt_sha256": dispatch["dispatch_prompt_sha256"],
                "raw_return_ref": stage_record[f"{lane}_return_ref"],
                "raw_return_sha256": None,
                "source": "multi_agent_v1.spawn_agent/wait_agent",
                "leader_summary_only": False,
            })

    manifest = {
        "schema_version": "ppg-phase13-run-manifest/v0.1",
        "run_id": RUN_ID,
        "project_slug": pilot_manifest.get("project_slug"),
        "generated_at": FIXED_GENERATED_AT,
        "runtime_root": str(ROOT),
        "run_root": repo_rel(run_root),
        "source_root": str(source_root),
        "pilot_root": repo_rel(pilot_root),
        "phase12_run_ref": repo_rel(PHASE12_RUN),
        "source_read_only": True,
        "writes_to_source_allowed": False,
        "stage_count": len(stages_out),
        "lane_count": len(thread_rows),
        "completion_boundary": BANNED_COMPLETION,
    }
    run_state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": RUN_ID,
        "canonical_stage_ids": registry.get("canonical_stage_ids", []),
        "stages": stages_out,
        "subagent_threads_ref": "subagent_threads.json",
        "dispatch_ledger_ref": "dispatch_ledger.jsonl",
        "validation_ledger_ref": "validation_ledger.jsonl",
        "delivery_gate_ref": "delivery-gate/delivery_gate.json",
        "source_snapshot_before_ref": "source_snapshot.before.json",
        "source_snapshot_after_ref": "source_snapshot.after.json",
        "completion_boundary": BANNED_COMPLETION,
    }
    write_json(run_root / "manifest.json", manifest, run_root, source_root)
    write_json(run_root / "run_state.json", run_state, run_root, source_root)
    write_json(run_root / "subagent_threads.json", {"schema_version": "ppg-phase13-subagent-threads/v0.1", "run_id": RUN_ID, "threads": thread_rows}, run_root, source_root)
    write_text(run_root / "dispatch_ledger.jsonl", "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in dispatch_events), run_root, source_root)
    write_text(run_root / "validation_ledger.jsonl", "", run_root, source_root)
    write_text(run_root / "final-report.md", f"# Phase13 Live Subagent Full-Flow Pilot\n\nRun id: `{RUN_ID}`\n\nStatus: scaffold prepared; live returns pending. This is a runtime pilot only.\n", run_root, source_root)
    return run_state


def scaffold_errors(run_root: Path) -> list[str]:
    errors: list[str] = []
    state = load_json(run_root / "run_state.json")
    stages = state.get("stages", [])
    if len(stages) != 20:
        errors.append(f"stage count={len(stages)}")
    for stage in stages:
        sid = stage["stage_id"]
        for key in ["producer_packet_ref", "verifier_packet_ref", "producer_prompt_ref", "verifier_prompt_ref"]:
            if not (run_root / stage[key]).is_file():
                errors.append(f"missing {sid}.{key}")
    threads = load_json(run_root / "subagent_threads.json").get("threads", [])
    if len(threads) != 40:
        errors.append(f"thread scaffold count={len(threads)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Phase13 live native-subagent pilot scaffold.")
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        state = generate(args.run_root, args.pilot_root)
    except Exception as exc:  # noqa: BLE001
        print(f"PHASE13_LIVE_PILOT_GENERATE_INVALID: {exc}", file=sys.stderr)
        return 1
    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    if args.check:
        errors = scaffold_errors(run_root)
        if errors:
            print("INVALID Phase13 scaffold", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
    print("PHASE13_LIVE_PILOT_SCAFFOLD_GENERATED")
    print(f"stages={len(state['stages'])}")
    print("lanes=40")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
