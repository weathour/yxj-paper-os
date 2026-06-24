#!/usr/bin/env python3
"""yxj-paper-os ledger closure guard.

This is intentionally small and project-local: it does not execute paper work.
It prevents false completion by checking/stamping the ledger closure that every
paper task must finish with:

    collect -> validate -> ingest -> state_transition

Commands:
  check    Validate required ledgers and completion/ingestion invariants.
  stamp    Upsert a completed task and optional artifact rows into ledgers.
  snapshot Copy ignored .omx ledgers to a tracked notes/ mirror for review.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required: python3 -m pip install pyyaml") from exc

REQUIRED_LEDGER_NAMES = [
    "state.yaml",
    "task-ledger.yaml",
    "artifact-ledger.yaml",
    "decision-ledger.yaml",
    "evidence-ledger.yaml",
    "review-ledger.yaml",
    "export-ledger.yaml",
]
TERMINAL_SUCCESS = "complete"
LEDGER_REL = Path(".omx/state/yxj-paper-os")
DEFAULT_SNAPSHOT_REL = Path("notes/yxj-paper-os/ledger-snapshot")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return default if data is None and default is not None else data


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_root(root: str | Path) -> Path:
    return Path(root).expanduser().resolve()


def ledger_dir(root: Path) -> Path:
    return root / LEDGER_REL


def rel_path(root: Path, path: str | Path) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.resolve().relative_to(root))
        except ValueError:
            return str(p)
    return str(p)


def ensure_required_ledgers(root: Path) -> tuple[dict[str, Any], list[str]]:
    ledgers: dict[str, Any] = {}
    errors: list[str] = []
    base = ledger_dir(root)
    for name in REQUIRED_LEDGER_NAMES:
        path = base / name
        if not path.exists():
            errors.append(f"missing required ledger: {path}")
            continue
        try:
            ledgers[name] = load_yaml(path, {})
        except Exception as exc:  # noqa: BLE001 - report parser failure cleanly
            errors.append(f"cannot parse {path}: {exc}")
    return ledgers, errors


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def task_validator_refs(task: dict[str, Any]) -> list[str]:
    refs = task.get("validator_refs")
    if refs is None:
        refs = task.get("validators")
    return [str(item) for item in listify(refs)]


def passing_validators(task: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for item in listify(task.get("validator_evidence")):
        if isinstance(item, dict) and item.get("status") == "pass" and item.get("validator"):
            names.add(str(item["validator"]))
    return names


def task_has_ingestion(task: dict[str, Any]) -> bool:
    ingestion = task.get("state_ingestion") or {}
    return ingestion.get("status") == "ingested" and bool(ingestion.get("ledger_path"))


def task_has_complete_transition(task: dict[str, Any]) -> bool:
    transition = task.get("state_transition") or {}
    return (
        task.get("pipeline_stage") == "state_transition"
        and bool(transition.get("from"))
        and transition.get("to") == TERMINAL_SUCCESS
        and bool(transition.get("at"))
    )


def task_completion_errors(root: Path, task: dict[str, Any], *, check_outputs_exist: bool) -> list[str]:
    errors: list[str] = []
    task_id = str(task.get("task_id", "<missing-task-id>"))
    status = task.get("status")
    outputs = [str(item) for item in listify(task.get("collected_outputs"))]
    refs = task_validator_refs(task)
    missing_refs = sorted(set(refs) - passing_validators(task))
    validated = bool(refs) and not missing_refs
    ingested = task_has_ingestion(task)

    if status == TERMINAL_SUCCESS:
        if not outputs:
            errors.append(f"{task_id}: complete without collected_outputs")
        if check_outputs_exist:
            for output in outputs:
                output_path = root / output if not Path(output).is_absolute() else Path(output)
                if not output_path.exists():
                    errors.append(f"{task_id}: collected output does not exist: {output}")
        if not refs:
            errors.append(f"{task_id}: complete without validator_refs")
        if missing_refs:
            errors.append(f"{task_id}: complete missing passing validator evidence: {', '.join(missing_refs)}")
        if not ingested:
            errors.append(f"{task_id}: complete without state_ingestion.status=ingested")
        if not task.get("state_transition"):
            errors.append(f"{task_id}: complete without state_transition")
        elif not task_has_complete_transition(task):
            errors.append(
                f"{task_id}: complete requires pipeline_stage=state_transition "
                "and state_transition.from, state_transition.to=complete, state_transition.at"
            )

    if validated and not ingested:
        errors.append(f"{task_id}: validated but not ingested")
    return errors


def parse_key_value(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise SystemExit(f"expected KEY=VALUE evidence entry, got: {raw}")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"empty evidence key in: {raw}")
        parsed[key] = value.strip()
    return parsed


def parse_artifact(raw: str) -> dict[str, Any]:
    parts = raw.split(":", 5)
    if len(parts) < 5:
        raise SystemExit(
            "--artifact must be artifact_id:path:type:owner_lane:status[:privacy_policy]"
        )
    artifact_id, path, artifact_type, owner_lane, status = parts[:5]
    privacy_policy = parts[5] if len(parts) == 6 else "tracked yxj-paper-os operation artifact"
    if not artifact_id or not path:
        raise SystemExit(f"invalid --artifact value: {raw}")
    return {
        "artifact_id": artifact_id,
        "path": path,
        "type": artifact_type or "operation_artifact",
        "owner_lane": owner_lane or "state-steward",
        "privacy_policy": privacy_policy,
        "status": status or "active",
    }


def upsert_by_key(items: list[dict[str, Any]], key: str, row: dict[str, Any]) -> list[dict[str, Any]]:
    value = row.get(key)
    replaced = False
    output: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict) and item.get(key) == value:
            merged = dict(item)
            merged.update(row)
            output.append(merged)
            replaced = True
        else:
            output.append(item)
    if not replaced:
        output.append(row)
    return output


def cmd_check(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    ledgers, errors = ensure_required_ledgers(root)
    task_ledger = ledgers.get("task-ledger.yaml") or {}
    tasks = listify(task_ledger.get("tasks"))
    if not tasks:
        errors.append("task-ledger.yaml has no tasks")

    found_task = False
    for task in tasks:
        if not isinstance(task, dict):
            errors.append("task-ledger.yaml contains a non-dict task entry")
            continue
        if args.task_id and task.get("task_id") != args.task_id:
            # Still check already-complete tasks globally to prevent stale false completion.
            if task.get("status") != TERMINAL_SUCCESS:
                continue
        if args.task_id and task.get("task_id") == args.task_id:
            found_task = True
        errors.extend(task_completion_errors(root, task, check_outputs_exist=not args.skip_output_exists))

    if args.task_id and not found_task:
        errors.append(f"task not found: {args.task_id}")
    if args.require_complete and args.task_id:
        target = next((t for t in tasks if isinstance(t, dict) and t.get("task_id") == args.task_id), None)
        if target and target.get("status") != TERMINAL_SUCCESS:
            errors.append(f"{args.task_id}: status is {target.get('status')!r}, not complete")

    if args.require_snapshot_fresh:
        snapshot_dir = root / args.snapshot_dir
        for name in REQUIRED_LEDGER_NAMES:
            live = ledger_dir(root) / name
            snap = snapshot_dir / name
            if not snap.exists():
                errors.append(f"snapshot missing: {snap}")
            elif live.exists() and sha256_file(live) != sha256_file(snap):
                errors.append(f"snapshot stale: {snap}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("yxj-paper-os ledger guard: PASS")
    return 0


def cmd_stamp(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    ledgers, errors = ensure_required_ledgers(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    now = utc_now()
    output_paths = [rel_path(root, item) for item in args.output]
    validators = [str(item) for item in args.validator]
    if args.status == TERMINAL_SUCCESS and not output_paths:
        print("ERROR: --status complete requires at least one --output", file=sys.stderr)
        return 1
    if args.status == TERMINAL_SUCCESS and not validators:
        print("ERROR: --status complete requires at least one --validator", file=sys.stderr)
        return 1
    if args.status == TERMINAL_SUCCESS and args.transition_to != TERMINAL_SUCCESS:
        print("ERROR: --status complete requires --transition-to complete", file=sys.stderr)
        return 1
    evidence_text = parse_key_value(args.evidence)
    validator_evidence = [
        {
            "validator": validator,
            "status": "pass",
            "evidence": evidence_text.get(validator, f"recorded by ledger_guard stamp at {now}"),
        }
        for validator in validators
    ]
    task: dict[str, Any] = {
        "task_id": args.task_id,
        "title": args.title,
        "route": args.route,
        "adapter": "native_subagent_pipeline_adapter",
        "owner_lane": args.owner_lane,
        "agent_type": args.agent_type,
        "status": args.status,
        "pipeline_stage": "state_transition" if args.status == TERMINAL_SUCCESS else args.status,
        "compiled_at": now,
        "updated_at": now,
        "scoped_context": args.context,
        "expected_output_artifacts": list(output_paths),
        "collection_path": args.collection_path or f"notes/yxj-paper-os/collections/{args.task_id}",
        "state_ledger_path": ".omx/state/yxj-paper-os/task-ledger.yaml",
        "collected_outputs": list(output_paths),
        "validator_refs": validators,
        "validator_evidence": validator_evidence,
    }
    if args.status == TERMINAL_SUCCESS:
        task["state_ingestion"] = {
            "status": "ingested",
            "ledger_path": ".omx/state/yxj-paper-os/task-ledger.yaml",
            "at": now,
        }
        task["state_transition"] = {
            "from": args.transition_from,
            "to": args.transition_to,
            "at": now,
        }

    task_ledger = ledgers["task-ledger.yaml"]
    task_ledger.setdefault("schema_version", 1)
    task_ledger.setdefault("paper_root", ".")
    task_ledger["last_updated_at"] = now
    task_ledger["tasks"] = upsert_by_key(listify(task_ledger.get("tasks")), "task_id", task)
    write_yaml(ledger_dir(root) / "task-ledger.yaml", task_ledger)

    artifact_ledger = ledgers["artifact-ledger.yaml"]
    artifact_ledger.setdefault("schema_version", 1)
    artifact_ledger.setdefault("paper_root", ".")
    artifact_ledger["last_updated_at"] = now
    artifacts = listify(artifact_ledger.get("artifacts"))
    for raw in args.artifact:
        artifact = parse_artifact(raw)
        artifact.setdefault("validator_refs", validators)
        artifact["updated_at"] = now
        artifacts = upsert_by_key(artifacts, "artifact_id", artifact)
    artifact_ledger["artifacts"] = artifacts
    write_yaml(ledger_dir(root) / "artifact-ledger.yaml", artifact_ledger)

    state = ledgers["state.yaml"]
    state["last_updated_at"] = now
    if args.next_safe_action:
        state["next_safe_action"] = args.next_safe_action
    state.setdefault("ledger_closure", {})
    state["ledger_closure"].update(
        {
            "guard": "skills/yxj-paper-index/scripts/ledger_guard.py",
            "last_task_id": args.task_id,
            "last_stamp_at": now,
            "final_check_required": True,
            "snapshot_recommended": True,
        }
    )
    write_yaml(ledger_dir(root) / "state.yaml", state)

    return cmd_check(argparse.Namespace(
        root=str(root),
        task_id=args.task_id,
        require_complete=args.status == TERMINAL_SUCCESS,
        require_snapshot_fresh=False,
        snapshot_dir=str(DEFAULT_SNAPSHOT_REL),
        skip_output_exists=False,
    ))


def cmd_snapshot(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    ledgers, errors = ensure_required_ledgers(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    snapshot_dir = root / args.snapshot_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    for name in REQUIRED_LEDGER_NAMES:
        shutil.copy2(ledger_dir(root) / name, snapshot_dir / name)
    manifest = {
        "schema_version": 1,
        "generated_at": now,
        "source": str(LEDGER_REL),
        "ledgers": [
            {"name": name, "sha256": sha256_file(snapshot_dir / name)} for name in REQUIRED_LEDGER_NAMES
        ],
        "purpose": "tracked mirror of yxj-paper-os ledgers when .omx is ignored by repository policy",
    }
    write_yaml(snapshot_dir / "snapshot-manifest.yaml", manifest)
    readme = snapshot_dir / "README.md"
    readme.write_text(
        "# yxj-paper-os ledger snapshot\n\n"
        "This directory is a tracked mirror of `.omx/state/yxj-paper-os/`.\n"
        "Refresh it with:\n\n"
        "```bash\n"
        "python3 scripts/yxj_paper_os_ledger_guard.py snapshot --root .\n"
        "python3 scripts/yxj_paper_os_ledger_guard.py check --root . --require-snapshot-fresh\n"
        "```\n",
        encoding="utf-8",
    )
    print(f"snapshot written: {snapshot_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="yxj-paper-os ledger closure guard")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="validate ledger closure invariants")
    check.add_argument("--root", default=".")
    check.add_argument("--task-id")
    check.add_argument("--require-complete", action="store_true")
    check.add_argument("--require-snapshot-fresh", action="store_true")
    check.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_REL))
    check.add_argument("--skip-output-exists", action="store_true")
    check.set_defaults(func=cmd_check)

    stamp = sub.add_parser("stamp", help="upsert a task completion row into ledgers")
    stamp.add_argument("--root", default=".")
    stamp.add_argument("--task-id", required=True)
    stamp.add_argument("--title", required=True)
    stamp.add_argument("--route", required=True)
    stamp.add_argument("--owner-lane", required=True)
    stamp.add_argument("--agent-type", required=True)
    stamp.add_argument("--status", default=TERMINAL_SUCCESS)
    stamp.add_argument("--context", action="append", default=[])
    stamp.add_argument("--output", action="append", default=[])
    stamp.add_argument("--validator", action="append", default=[])
    stamp.add_argument("--evidence", action="append", default=[])
    stamp.add_argument("--artifact", action="append", default=[])
    stamp.add_argument("--collection-path")
    stamp.add_argument("--transition-from", default="previous_yxj_paper_os_state")
    stamp.add_argument("--transition-to", default=TERMINAL_SUCCESS)
    stamp.add_argument("--next-safe-action")
    stamp.set_defaults(func=cmd_stamp)

    snapshot = sub.add_parser("snapshot", help="copy live ledgers to a tracked notes mirror")
    snapshot.add_argument("--root", default=".")
    snapshot.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_REL))
    snapshot.set_defaults(func=cmd_snapshot)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
