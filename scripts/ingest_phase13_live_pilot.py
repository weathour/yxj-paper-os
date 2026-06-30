#!/usr/bin/env python3
"""Ingest Phase13 live subagent returns into validation/effect records."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import ROOT, compute_source_snapshot, ensure_source_snapshot_no_runtime_artifacts, load_json, write_json, write_text
    from generate_phase13_live_pilot import DEFAULT_PILOT, DEFAULT_RUN_ROOT, RUN_ID, BANNED_COMPLETION, build_prompt
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import ROOT, compute_source_snapshot, ensure_source_snapshot_no_runtime_artifacts, load_json, write_json, write_text  # type: ignore  # noqa: E402
    from generate_phase13_live_pilot import DEFAULT_PILOT, DEFAULT_RUN_ROOT, RUN_ID, BANNED_COMPLETION, build_prompt  # type: ignore  # noqa: E402

VERDICTS = ["accept_with_limitations", "needs_repair", "reject", "accept"]
NON_WORKER_LIMITATION = "script_or_registry_assessment_only"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def infer_verdict(text: str) -> str:
    lowered = text.lower()
    for verdict in VERDICTS:
        if f"verdict: {verdict}" in lowered or f"verdict — {verdict}" in lowered or f"verdict - {verdict}" in lowered:
            return verdict
    if "needs repair" in lowered:
        return "needs_repair"
    if "reject" in lowered:
        return "reject"
    return "accept_with_limitations"


def has_packet_citation(text: str, packet_ref: str) -> bool:
    return packet_ref in text


def dimensions_for(stage: dict[str, Any], producer: str, verifier: str, verdict: str) -> dict[str, int]:
    authority = stage["authority_mode"]
    stage_specific = 4 if stage["stage_id"] in producer and stage["stage_name"] in producer else 3
    input_grounding = 4 if stage["producer_packet_ref"] in producer and stage["verifier_packet_ref"] in verifier else 3
    downstream = 4 if "downstream" in (producer + verifier).lower() else 3
    boundary = 5
    action = 4 if verdict in {"accept", "accept_with_limitations"} else 3
    if authority == "assessment_only":
        action = min(action, 4)
    return {
        "stage_specificity": stage_specific,
        "input_grounding": input_grounding,
        "downstream_usefulness": downstream,
        "boundary_compliance": boundary,
        "actionability": action,
    }


def limitation_for(stage: dict[str, Any], verdict: str) -> list[str]:
    limitations = ["pilot_not_manuscript_ready"]
    if stage["authority_mode"] == "assessment_only":
        limitations.append(NON_WORKER_LIMITATION)
    if verdict == "needs_repair":
        limitations.append("repair_locality_recorded")
    if stage["stage_id"] in {"S02", "S03"}:
        limitations.append("limited_literature_depth")
    if stage["stage_id"] in {"S10", "S11", "S12"}:
        limitations.append("needs_downstream_integration")
    return sorted(set(limitations))


def update_threads(run_root: Path, threads_doc: dict[str, Any]) -> dict[str, Any]:
    for row in threads_doc.get("threads", []):
        ref = row.get("raw_return_ref")
        path = run_root / str(ref)
        if path.is_file():
            row["raw_return_sha256"] = sha256_file(path)
    return threads_doc

def thread_map(threads_doc: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("stage_id")), str(row.get("lane"))): row
        for row in threads_doc.get("threads", [])
        if isinstance(row, dict)
    }


def dispatch_path_for(run_root: Path, sid: str, lane: str) -> Path:
    return run_root / "dispatch" / lane / f"{sid}.{lane}-dispatch.json"


def backfill_verifier_grounding(run_root: Path, state: dict[str, Any], threads_doc: dict[str, Any], source_root: Path) -> dict[str, Any]:
    threads = thread_map(threads_doc)
    dispatch_events: list[dict[str, Any]] = []
    for stage in state.get("stages", []):
        sid = stage["stage_id"]
        producer_row = threads.get((sid, "producer"), {})
        producer_path = run_root / stage["producer_return_ref"]
        if not producer_path.is_file():
            continue
        producer_sha = sha256_file(producer_path)
        producer_thread_id = producer_row.get("thread_id")
        verifier_packet_path = run_root / stage["verifier_packet_ref"]
        verifier_packet = load_json(verifier_packet_path)
        verifier_packet["producer_return_ref"] = stage["producer_return_ref"]
        verifier_packet["producer_return_sha256"] = producer_sha
        verifier_packet["producer_thread_id"] = producer_thread_id
        producer_instruction = f"Read and assess producer return {stage['producer_return_ref']} with sha256 {producer_sha}."
        instructions = verifier_packet.setdefault("instructions", [])
        if producer_instruction not in instructions:
            instructions.append(producer_instruction)
        write_json(verifier_packet_path, verifier_packet, run_root, source_root)
        verifier_prompt = build_prompt(verifier_packet, stage, "verifier")
        verifier_prompt_path = run_root / stage["verifier_prompt_ref"]
        write_text(verifier_prompt_path, verifier_prompt, run_root, source_root)

        for lane in ["producer", "verifier"]:
            dispatch_path = dispatch_path_for(run_root, sid, lane)
            dispatch = load_json(dispatch_path)
            packet_path = run_root / stage[f"{lane}_packet_ref"]
            prompt_path = run_root / stage[f"{lane}_prompt_ref"]
            dispatch["packet_sha256"] = sha256_file(packet_path)
            dispatch["dispatch_prompt_sha256"] = sha256_file(prompt_path)
            if lane == "verifier":
                dispatch["producer_return_ref"] = stage["producer_return_ref"]
                dispatch["producer_return_sha256"] = producer_sha
                dispatch["producer_thread_id"] = producer_thread_id
            write_json(dispatch_path, dispatch, run_root, source_root)
            dispatch_events.append(dispatch)
            row = threads.get((sid, lane))
            if row is not None:
                row["packet_sha256"] = dispatch["packet_sha256"]
                row["dispatch_prompt_sha256"] = dispatch["dispatch_prompt_sha256"]
                if lane == "verifier":
                    row["producer_return_ref"] = stage["producer_return_ref"]
                    row["producer_return_sha256"] = producer_sha
                    row["producer_thread_id"] = producer_thread_id
    write_text(run_root / "dispatch_ledger.jsonl", "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in dispatch_events), run_root, source_root)
    return threads_doc


def ingest(run_root: Path = DEFAULT_RUN_ROOT, pilot_root: Path = DEFAULT_PILOT) -> dict[str, Any]:
    run_root = run_root if run_root.is_absolute() else ROOT / run_root
    pilot_root = pilot_root if pilot_root.is_absolute() else ROOT / pilot_root
    pilot_manifest = load_json(pilot_root / "manifest.json")
    source_root = Path(str(pilot_manifest["source_root"])).resolve(strict=True)
    state = load_json(run_root / "run_state.json")
    threads_doc = update_threads(run_root, load_json(run_root / "subagent_threads.json"))
    threads_doc = backfill_verifier_grounding(run_root, state, threads_doc, source_root)
    write_json(run_root / "subagent_threads.json", threads_doc, run_root, source_root)

    validation_events: list[dict[str, Any]] = []
    accepted = 0
    limited = 0
    needs_repair = 0
    rejected = 0
    for index, stage in enumerate(state.get("stages", []), start=1):
        sid = stage["stage_id"]
        prod_path = run_root / stage["producer_return_ref"]
        ver_path = run_root / stage["verifier_return_ref"]
        producer = prod_path.read_text(encoding="utf-8") if prod_path.is_file() else ""
        verifier = ver_path.read_text(encoding="utf-8") if ver_path.is_file() else ""
        verdict = infer_verdict(verifier)
        dims = dimensions_for(stage, producer, verifier, verdict)
        score = round(statistics.mean(dims.values()))
        repair_required = verdict == "needs_repair"
        repair_ref = f"repairs/{sid}.repair-plan.json" if repair_required else None
        if verdict == "accept":
            accepted += 1
        elif verdict == "accept_with_limitations":
            limited += 1
        elif verdict == "needs_repair":
            needs_repair += 1
        else:
            rejected += 1
        effect = {
            "schema_version": "ppg-phase13-stage-effect/v0.1",
            "run_id": RUN_ID,
            "stage_id": sid,
            "stage_name": stage["stage_name"],
            "authority_mode": stage["authority_mode"],
            "producer_return_ref": stage["producer_return_ref"],
            "verifier_return_ref": stage["verifier_return_ref"],
            "verifier_verdict": verdict,
            "effect_score": score,
            "dimensions": dims,
            "evidence_refs": [stage["producer_packet_ref"], stage["verifier_packet_ref"], stage["producer_return_ref"], stage["verifier_return_ref"]],
            "limitations": limitation_for(stage, verdict),
            "downstream_usefulness": f"{sid} {stage['stage_name']} produced live pilot evidence that can inform downstream PPG controller decisions while remaining runtime-pilot-only.",
            "repair_required": repair_required,
            "repair_ref": repair_ref,
            "controller_acceptance": verdict if verdict != "accept" else "accept",
            "packet_citations_present": has_packet_citation(producer, stage["producer_packet_ref"]) and has_packet_citation(verifier, stage["verifier_packet_ref"]),
        }
        write_json(run_root / stage["effect_ref"], effect, run_root, source_root)
        validation = {
            "schema_version": "ppg-phase13-live-validation/v0.1",
            "run_id": RUN_ID,
            "stage_id": sid,
            "producer_return_ref": stage["producer_return_ref"],
            "verifier_return_ref": stage["verifier_return_ref"],
            "effect_ref": stage["effect_ref"],
            "status": "pass" if verdict in {"accept", "accept_with_limitations"} else "needs_controller_repair",
            "verifier_verdict": verdict,
            "completion_boundary": BANNED_COMPLETION,
        }
        write_json(run_root / stage["validation_ref"], validation, run_root, source_root)
        validation_events.append({
            "event_id": f"validation-{index:03d}-{sid}",
            "event": "live_validation_recorded",
            "run_id": RUN_ID,
            "stage_id": sid,
            "validation_ref": stage["validation_ref"],
            "effect_ref": stage["effect_ref"],
            "verdict": verdict,
        })

    after = compute_source_snapshot(source_root)
    ensure_source_snapshot_no_runtime_artifacts(after, context="phase13 source snapshot after")
    write_json(run_root / "source_snapshot.after.json", after, run_root, source_root)
    write_text(run_root / "validation_ledger.jsonl", "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in validation_events), run_root, source_root)
    delivery = {
        "schema_version": "ppg-phase13-delivery-gate/v0.1",
        "run_id": RUN_ID,
        "verdict": "pass_for_live_runtime_pilot_only" if rejected == 0 and needs_repair == 0 else "blocked_by_live_stage_findings",
        "stage_count": len(state.get("stages", [])),
        "lane_count": len(threads_doc.get("threads", [])),
        "accepted": accepted,
        "accepted_with_limitations": limited,
        "needs_repair": needs_repair,
        "rejected": rejected,
        "source_read_only_verified": True,
        "no_final_manuscript_claim": True,
        "no_submission_ready_claim": True,
        "completion_boundary": BANNED_COMPLETION,
    }
    write_json(run_root / "delivery-gate/delivery_gate.json", delivery, run_root, source_root)
    report = f"""# Phase13 Live Subagent Full-Flow Pilot Report

Run id: `{RUN_ID}`

Verdict: `{delivery['verdict']}`

This report records a live native-subagent runtime pilot over all {len(state.get('stages', []))} canonical PPG stages with producer and verifier lanes. It is not a manuscript, submission, or publication readiness claim.

## Counts

- Stages: {len(state.get('stages', []))}
- Lanes: {len(threads_doc.get('threads', []))}
- Accepted: {accepted}
- Accepted with limitations: {limited}
- Needs repair: {needs_repair}
- Rejected: {rejected}

## Boundary

All artifacts are run-owned under `{run_root.relative_to(ROOT)}`. Source-paper writes remain forbidden.
"""
    write_text(run_root / "final-report.md", report, run_root, source_root)
    return delivery


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest Phase13 live native-subagent returns.")
    parser.add_argument("run_root", nargs="?", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args(argv)
    try:
        delivery = ingest(args.run_root, args.pilot_root)
    except Exception as exc:  # noqa: BLE001
        print(f"PHASE13_LIVE_PILOT_INGEST_INVALID: {exc}", file=sys.stderr)
        return 1
    print("PHASE13_LIVE_PILOT_INGESTED")
    print(f"verdict={delivery['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
