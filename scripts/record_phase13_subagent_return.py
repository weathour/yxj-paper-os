#!/usr/bin/env python3
"""Record one Phase13 native-subagent return and update provenance."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
from pathlib import Path
import sys
from typing import Any

try:
    from generate_phase10_run_dry_run import ROOT, load_json, write_json, write_text
    from generate_phase13_live_pilot import DEFAULT_RUN_ROOT, DEFAULT_PILOT
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_phase10_run_dry_run import ROOT, load_json, write_json, write_text  # type: ignore  # noqa: E402
    from generate_phase13_live_pilot import DEFAULT_RUN_ROOT, DEFAULT_PILOT  # type: ignore  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record Phase13 subagent return.")
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--lane", choices=["producer", "verifier"], required=True)
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--agent-type", required=True)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--completed-at", default=None)
    args = parser.parse_args(argv)
    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    pilot_manifest = load_json(DEFAULT_PILOT / "manifest.json")
    source_root = Path(str(pilot_manifest["source_root"])).resolve(strict=True)
    state = load_json(run_root / "run_state.json")
    stage = next((item for item in state.get("stages", []) if item.get("stage_id") == args.stage_id), None)
    if not isinstance(stage, dict):
        print(f"unknown stage: {args.stage_id}", file=sys.stderr)
        return 1
    text = sys.stdin.read()
    if not text.strip():
        print("empty return", file=sys.stderr)
        return 1
    packet = load_json(run_root / stage[f"{args.lane}_packet_ref"])
    expected_agent_type = packet.get("agent_type")
    if args.agent_type != expected_agent_type:
        print(f"agent type mismatch for {args.stage_id}.{args.lane}: expected={expected_agent_type} actual={args.agent_type}", file=sys.stderr)
        return 1
    return_ref = stage[f"{args.lane}_return_ref"]
    return_path = run_root / return_ref
    write_text(return_path, text.rstrip() + "\n", run_root, source_root)
    threads_path = run_root / "subagent_threads.json"
    threads_doc: dict[str, Any] = load_json(threads_path)
    now = args.completed_at or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    matched = False
    for row in threads_doc.get("threads", []):
        if row.get("stage_id") == args.stage_id and row.get("lane") == args.lane:
            row["thread_id"] = args.thread_id
            row["agent_type"] = args.agent_type
            row["native_subagent"] = True
            row["started_at"] = row.get("started_at") or now
            row["completed_at"] = now
            row["raw_return_sha256"] = sha256_file(return_path)
            row["source"] = "multi_agent_v1.spawn_agent/wait_agent"
            row["leader_summary_only"] = False
            matched = True
            break
    if not matched:
        print(f"thread row missing for {args.stage_id}.{args.lane}", file=sys.stderr)
        return 1
    write_json(threads_path, threads_doc, run_root, source_root)
    print("PHASE13_RETURN_RECORDED")
    print(f"stage={args.stage_id}")
    print(f"lane={args.lane}")
    print(f"return_ref={return_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
