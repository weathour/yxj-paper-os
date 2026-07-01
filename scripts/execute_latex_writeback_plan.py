#!/usr/bin/env python3
"""Execute a controller-owned LaTeX writeback patchset.

The executor is intentionally narrower than a general file-editing tool.  It
promotes an already validated candidate patchset through a LatexWritebackPlan,
checks stage-scoped target paths, snapshots source surfaces before/after, can
run the declared LaTeX build commands, and rolls back if apply-time validation
fails.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from verify_latex_writeback_contract import (  # noqa: E402
    allowed_source_pattern,
    issue,
    load_json,
    safe_pattern,
    validate_plan,
)

PATCHSET_SCHEMA = "ppg-latex-writeback-patchset/v0.1"
VALID_OPS = {"replace_file", "replace_between_markers", "copy_file"}
SNAPSHOT_PREFIXES = ("manuscript/", "figures/src/", "figures/generated/", "paper-os/writeback/")
SNAPSHOT_EXCLUDE_PREFIXES = (
    ".git/",
    ".omx/",
    "exports/",
    "manuscript/build/",
    "manuscript/build_zh/",
)
DEFAULT_REPORT_DIR = "paper-os/writeback"
LOCAL_APPLY_MODE = "apply_with_validation_and_rollback"


@dataclass(frozen=True)
class Operation:
    op: str
    path: str
    raw: dict[str, Any]


def resolve_input(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def to_posix(path: Path) -> str:
    return path.as_posix()


def matches_pattern(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(prefix + "/")
    if any(ch in pattern for ch in "*?["):
        return PurePosixPath(path).match(pattern)
    return path == pattern


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(matches_pattern(path, pattern) for pattern in patterns)


def stage_contract(plan: dict[str, Any], stage_id: str) -> dict[str, Any] | None:
    for item in plan.get("stage_writebacks", []):
        if isinstance(item, dict) and item.get("stage_id") == stage_id:
            return item
    return None


def resolve_source_root(plan: dict[str, Any], override: str | None) -> Path:
    raw = override if override is not None else str(plan.get("source_root", ""))
    source_root = Path(raw)
    if not source_root.is_absolute():
        source_root = ROOT / source_root
    return source_root.resolve()


def ensure_under_root(source_root: Path, rel_path: str) -> Path:
    target = (source_root / rel_path).resolve()
    try:
        target.relative_to(source_root)
    except ValueError as exc:
        raise ValueError(issue("E_WRITEBACK_PATH_ESCAPE", rel_path)) from exc
    return target


def path_has_symlink_boundary(source_root: Path, target: Path) -> bool:
    current = target
    source_root = source_root.resolve()
    while current != source_root and current != current.parent:
        if current.exists() and current.is_symlink():
            return True
        current = current.parent
    return False


def validate_target_path(
    rel_path: str,
    *,
    plan: dict[str, Any],
    stage: dict[str, Any],
    source_root: Path,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(rel_path, str) or not allowed_source_pattern(rel_path):
        return [issue("E_WRITEBACK_PATCH_TARGET_UNSAFE", repr(rel_path))]
    forbidden = [str(item) for item in plan.get("forbidden_source_write_paths", []) if isinstance(item, str)]
    if matches_any(rel_path, forbidden):
        errors.append(issue("E_WRITEBACK_PATCH_TARGET_FORBIDDEN", rel_path))
    allowed = [str(item) for item in plan.get("allowed_source_write_paths", []) if isinstance(item, str)]
    if not matches_any(rel_path, allowed):
        errors.append(issue("E_WRITEBACK_PATCH_TARGET_NOT_IN_PLAN", rel_path))
    stage_targets = [str(item) for item in stage.get("write_targets", []) if isinstance(item, str)]
    if not matches_any(rel_path, stage_targets):
        errors.append(issue("E_WRITEBACK_PATCH_TARGET_NOT_IN_STAGE", rel_path))
    try:
        target = ensure_under_root(source_root, rel_path)
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    if path_has_symlink_boundary(source_root, target):
        errors.append(issue("E_WRITEBACK_PATCH_TARGET_SYMLINK", rel_path))
    return errors


def validate_candidate_ref(value: Any) -> list[str]:
    if not isinstance(value, str) or not safe_pattern(value):
        return [issue("E_WRITEBACK_PATCH_CANDIDATE_REF", "candidate_ref must be a safe repo-relative path")]
    return []


def validate_template_adapter(patchset: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    adapter = patchset.get("template_adapter")
    if adapter is None:
        return []
    if not isinstance(adapter, dict):
        return [issue("E_WRITEBACK_PATCH_TEMPLATE_ADAPTER", "template_adapter must be object")]
    expected = plan.get("latex_profile", {}).get("template_adapter_policy")
    if adapter.get("policy") != expected:
        return [issue("E_WRITEBACK_PATCH_TEMPLATE_POLICY", "patchset template adapter policy must match plan")]
    mode = adapter.get("body_injection_mode")
    if mode not in {"section_file_or_marker_block", "marker_block", "section_file"}:
        return [issue("E_WRITEBACK_PATCH_TEMPLATE_MODE", "unsupported body injection mode")]
    return []


def validate_operation_shape(op: Any) -> tuple[Operation | None, list[str]]:
    errors: list[str] = []
    if not isinstance(op, dict):
        return None, [issue("E_WRITEBACK_PATCH_OPERATION", "operation must be object")]
    op_name = op.get("op")
    rel_path = op.get("path")
    if op_name not in VALID_OPS:
        errors.append(issue("E_WRITEBACK_PATCH_OP", f"unsupported op {op_name!r}"))
    if not isinstance(rel_path, str):
        errors.append(issue("E_WRITEBACK_PATCH_TARGET", "operation path required"))
    if errors:
        return None, errors
    if op_name in {"replace_file", "replace_between_markers"}:
        content = op.get("content")
        if not isinstance(content, str):
            errors.append(issue("E_WRITEBACK_PATCH_CONTENT", f"{op_name} requires string content"))
        elif "\x00" in content:
            errors.append(issue("E_WRITEBACK_PATCH_CONTENT", "content must not contain NUL"))
    if op_name == "replace_between_markers":
        for key in ["start_marker", "end_marker"]:
            if not isinstance(op.get(key), str) or not op[key]:
                errors.append(issue("E_WRITEBACK_PATCH_MARKER", f"{key} required"))
    if op_name == "copy_file":
        source = op.get("source")
        if not isinstance(source, str) or not safe_pattern(source):
            errors.append(issue("E_WRITEBACK_PATCH_COPY_SOURCE", "copy_file source must be safe relative path"))
    return Operation(str(op_name), str(rel_path), op), errors


def validate_patchset(
    patchset: dict[str, Any],
    plan: dict[str, Any],
    source_root: Path,
) -> tuple[list[Operation], list[str]]:
    errors: list[str] = []
    operations: list[Operation] = []
    if patchset.get("schema_version") != PATCHSET_SCHEMA:
        errors.append(issue("E_WRITEBACK_PATCH_SCHEMA", str(patchset.get("schema_version"))))
    if not isinstance(patchset.get("patchset_id"), str) or not patchset["patchset_id"].strip():
        errors.append(issue("E_WRITEBACK_PATCH_ID", "patchset_id required"))
    if patchset.get("plan_id") != plan.get("plan_id"):
        errors.append(issue("E_WRITEBACK_PATCH_PLAN_ID", "patchset plan_id must match plan"))
    stage_id = patchset.get("stage_id")
    if not isinstance(stage_id, str):
        errors.append(issue("E_WRITEBACK_PATCH_STAGE", "stage_id required"))
        stage = None
    else:
        stage = stage_contract(plan, stage_id)
        if stage is None:
            errors.append(issue("E_WRITEBACK_PATCH_STAGE", f"stage {stage_id!r} not in plan"))
    if stage is not None and stage.get("candidate_ref_required") is True:
        errors.extend(validate_candidate_ref(patchset.get("candidate_ref")))
    errors.extend(validate_template_adapter(patchset, plan))

    raw_ops = patchset.get("operations")
    if not isinstance(raw_ops, list) or not raw_ops:
        errors.append(issue("E_WRITEBACK_PATCH_OPERATIONS", "operations must be non-empty list"))
    elif stage is not None:
        seen_targets: set[str] = set()
        for raw_op in raw_ops:
            op, op_errors = validate_operation_shape(raw_op)
            errors.extend(op_errors)
            if op is None:
                continue
            errors.extend(validate_target_path(op.path, plan=plan, stage=stage, source_root=source_root))
            if op.path in seen_targets and op.op != "copy_file":
                errors.append(issue("E_WRITEBACK_PATCH_DUPLICATE_TARGET", op.path))
            seen_targets.add(op.path)
            operations.append(op)
    expected = patchset.get("expected_changed_files")
    if expected is not None:
        if not isinstance(expected, list) or not all(isinstance(item, str) and allowed_source_pattern(item) for item in expected):
            errors.append(issue("E_WRITEBACK_PATCH_EXPECTED_CHANGED_FILES", "expected_changed_files must be safe source paths"))
    return operations, errors


def snapshot(source_root: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    if not source_root.exists():
        return entries
    for path in sorted(source_root.rglob("*")):
        rel = to_posix(path.relative_to(source_root))
        if any(rel == prefix[:-1] or rel.startswith(prefix) for prefix in SNAPSHOT_EXCLUDE_PREFIXES):
            continue
        if not any(rel == prefix[:-1] or rel.startswith(prefix) for prefix in SNAPSHOT_PREFIXES):
            continue
        if path.is_symlink():
            entries[rel] = {"kind": "symlink"}
        elif path.is_file():
            entries[rel] = {"kind": "file", "size": path.stat().st_size, "sha256": sha256_file(path)}
    return entries


def diff_snapshots(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    changed: list[str] = []
    for rel in sorted(set(before) | set(after)):
        if before.get(rel) != after.get(rel):
            changed.append(rel)
    return changed


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_from_candidate(op: Operation, target: Path, candidate_root: Path | None) -> None:
    if candidate_root is None:
        raise RuntimeError(issue("E_WRITEBACK_PATCH_CANDIDATE_ROOT", "copy_file requires --candidate-root"))
    source = (candidate_root / op.raw["source"]).resolve()
    try:
        source.relative_to(candidate_root.resolve())
    except ValueError as exc:
        raise RuntimeError(issue("E_WRITEBACK_PATCH_COPY_ESCAPE", op.raw["source"])) from exc
    if source.is_symlink() or not source.is_file():
        raise RuntimeError(issue("E_WRITEBACK_PATCH_COPY_SOURCE", f"not a regular file: {op.raw['source']}"))
    expected_sha = op.raw.get("sha256")
    actual_sha = sha256_file(source)
    if expected_sha is not None and expected_sha != actual_sha:
        raise RuntimeError(issue("E_WRITEBACK_PATCH_COPY_SHA256", f"{op.raw['source']} sha256 mismatch"))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def materialize_operation(op: Operation, source_root: Path, candidate_root: Path | None, apply: bool) -> str:
    target = ensure_under_root(source_root, op.path)
    if op.op == "replace_file":
        if not target.exists() and op.raw.get("create") is not True:
            raise RuntimeError(issue("E_WRITEBACK_PATCH_TARGET_MISSING", f"{op.path} missing; set create=true"))
        if apply:
            write_text(target, op.raw["content"])
        return "replace_file"
    if op.op == "replace_between_markers":
        if not target.is_file():
            raise RuntimeError(issue("E_WRITEBACK_PATCH_MARKER_TARGET", f"{op.path} must exist"))
        text = read_text(target)
        start = op.raw["start_marker"]
        end = op.raw["end_marker"]
        start_index = text.find(start)
        end_index = text.find(end)
        if start_index < 0 or end_index < 0 or end_index <= start_index:
            raise RuntimeError(issue("E_WRITEBACK_PATCH_MARKER_NOT_FOUND", op.path))
        body_start = start_index + len(start)
        replacement = "\n" + op.raw["content"].rstrip() + "\n"
        new_text = text[:body_start] + replacement + text[end_index:]
        if apply:
            write_text(target, new_text)
        return "replace_between_markers"
    if op.op == "copy_file":
        if apply:
            copy_from_candidate(op, target, candidate_root)
        return "copy_file"
    raise RuntimeError(issue("E_WRITEBACK_PATCH_OP", op.op))


def backup_targets(source_root: Path, operations: list[Operation]) -> dict[str, bytes | None]:
    backups: dict[str, bytes | None] = {}
    for op in operations:
        target = ensure_under_root(source_root, op.path)
        if op.path in backups:
            continue
        backups[op.path] = target.read_bytes() if target.exists() else None
    return backups


def restore_targets(source_root: Path, backups: dict[str, bytes | None]) -> None:
    for rel_path, data in backups.items():
        target = ensure_under_root(source_root, rel_path)
        if data is None:
            if target.exists():
                target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


def run_build(plan: dict[str, Any], source_root: Path, timeout: int) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    commands = plan.get("latex_profile", {}).get("build_commands", [])
    for command in commands:
        proc = subprocess.run(
            command,
            cwd=source_root,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        result = {
            "command": command,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
        results.append(result)
        if proc.returncode != 0:
            errors.append(issue("E_WRITEBACK_LATEX_BUILD_FAILED", command))
            break
    return results, errors


def report_path_for(source_root: Path, patchset: dict[str, Any], override: str | None) -> Path | None:
    if override is None:
        return None
    raw = Path(override)
    if raw.is_absolute():
        return raw
    return source_root / raw


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def local_apply_policy(plan: dict[str, Any]) -> dict[str, Any]:
    policy = plan.get("local_apply_policy")
    return policy if isinstance(policy, dict) else {}


def should_apply(args: argparse.Namespace, plan: dict[str, Any]) -> bool:
    if args.dry_run:
        return False
    if args.apply:
        return True
    return local_apply_policy(plan).get("default_execution_mode") == LOCAL_APPLY_MODE


def should_run_build(args: argparse.Namespace, apply_requested: bool) -> bool:
    return bool(args.run_build or apply_requested)


def should_git_commit(args: argparse.Namespace, plan: dict[str, Any], apply_requested: bool) -> bool:
    if not apply_requested or args.no_git_commit:
        return False
    return local_apply_policy(plan).get("git_commit_after_validation") is True


def run_git(source_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(source_root), *args],
        text=True,
        capture_output=True,
    )


def format_commit_message(plan: dict[str, Any], patchset: dict[str, Any]) -> str:
    template = str(local_apply_policy(plan).get("commit_message_template", "ppg latex writeback: {stage_id} {patchset_id}"))
    return template.format(
        stage_id=str(patchset.get("stage_id", "UNKNOWN")),
        patchset_id=str(patchset.get("patchset_id", "unknown-patchset")),
    )


def git_commit_after_validation(
    source_root: Path,
    changed_files: list[str],
    plan: dict[str, Any],
    patchset: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not changed_files:
        return {"status": "skipped_no_source_changes"}, []
    probe = run_git(source_root, ["rev-parse", "--show-toplevel"])
    if probe.returncode != 0:
        return {"status": "failed_not_git_repo", "stderr_tail": probe.stderr[-2000:]}, [
            issue("E_WRITEBACK_GIT_COMMIT", "source root is not inside a git repository")
        ]
    add = run_git(source_root, ["add", "--", *changed_files])
    if add.returncode != 0:
        return {"status": "failed_add", "stderr_tail": add.stderr[-2000:]}, [
            issue("E_WRITEBACK_GIT_ADD_FAILED", add.stderr[-2000:])
        ]
    message = format_commit_message(plan, patchset)
    commit = run_git(source_root, ["commit", "-m", message])
    if commit.returncode != 0:
        return {"status": "failed_commit", "message": message, "stderr_tail": commit.stderr[-2000:], "stdout_tail": commit.stdout[-2000:]}, [
            issue("E_WRITEBACK_GIT_COMMIT_FAILED", commit.stderr[-2000:] or commit.stdout[-2000:])
        ]
    rev = run_git(source_root, ["rev-parse", "--short", "HEAD"])
    commit_hash = rev.stdout.strip() if rev.returncode == 0 else ""
    return {"status": "committed", "message": message, "commit": commit_hash, "files": changed_files}, []


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a stage-scoped LaTeX writeback patchset")
    parser.add_argument("plan", help="LatexWritebackPlan JSON")
    parser.add_argument("patchset", help="LatexWritebackPatchset JSON")
    parser.add_argument("--source-root", help="override plan source_root, used for fixture/temp runs")
    parser.add_argument("--candidate-root", help="base path for copy_file sources; defaults to plugin root")
    parser.add_argument("--dry-run", action="store_true", help="force dry-run even when the plan defaults to local apply")
    parser.add_argument("--apply", action="store_true", help="force apply operations; the default follows local_apply_policy")
    parser.add_argument("--owner-local-apply-ok", action="store_true", help="legacy confirmation flag; only required if the plan policy requires it")
    parser.add_argument("--run-build", action="store_true", help="run plan latex_profile.build_commands; apply mode runs the build by default")
    parser.add_argument("--no-git-commit", action="store_true", help="do not create the post-validation scoped git commit")
    parser.add_argument("--build-timeout", type=int, default=120)
    parser.add_argument("--report-out", help="optional JSON report output path; relative paths resolve under source root")
    args = parser.parse_args()

    plan_path = resolve_input(args.plan)
    patch_path = resolve_input(args.patchset)
    plan = load_json(plan_path)
    patchset = load_json(patch_path)
    source_root = resolve_source_root(plan, args.source_root)
    candidate_root = Path(args.candidate_root).resolve() if args.candidate_root else ROOT
    apply_requested = should_apply(args, plan)
    build_requested = should_run_build(args, apply_requested)
    git_commit_requested = should_git_commit(args, plan, apply_requested)

    errors = validate_plan(plan)
    operations, patch_errors = validate_patchset(patchset, plan, source_root)
    errors.extend(patch_errors)
    if args.apply and args.dry_run:
        errors.append(issue("E_WRITEBACK_EXECUTION_MODE", "--apply and --dry-run are mutually exclusive"))
    if apply_requested and local_apply_policy(plan).get("human_confirmation_required_for_local_apply") is True and not args.owner_local_apply_ok:
        errors.append(issue("E_WRITEBACK_APPLY_CONFIRMATION", "this plan requires --owner-local-apply-ok"))
    if not source_root.exists() or not source_root.is_dir():
        errors.append(issue("E_WRITEBACK_SOURCE_ROOT", f"source root not found: {source_root}"))
    main_tex = source_root / plan.get("latex_profile", {}).get("main_tex", "")
    if not main_tex.is_file():
        errors.append(issue("E_WRITEBACK_LATEX_MAIN", f"main tex not found: {main_tex}"))

    pre_snapshot = snapshot(source_root)
    materialized: list[dict[str, str]] = []
    runtime_errors: list[str] = []
    backups: dict[str, bytes | None] = {}
    status = "dry_run_ok"
    build_results: list[dict[str, Any]] = []
    changed_files: list[str] = []
    git_commit_result: dict[str, Any] = {"status": "not_requested"}

    if not errors:
        try:
            for op in operations:
                action = materialize_operation(op, source_root, candidate_root, apply=False)
                materialized.append({"op": action, "path": op.path})
            if apply_requested:
                backups = backup_targets(source_root, operations)
                for op in operations:
                    materialize_operation(op, source_root, candidate_root, apply=True)
                if build_requested:
                    build_results, build_errors = run_build(plan, source_root, args.build_timeout)
                    runtime_errors.extend(build_errors)
                post_snapshot = snapshot(source_root)
                changed_files = diff_snapshots(pre_snapshot, post_snapshot)
                allowed = [str(item) for item in plan.get("allowed_source_write_paths", []) if isinstance(item, str)]
                forbidden = [str(item) for item in plan.get("forbidden_source_write_paths", []) if isinstance(item, str)]
                for rel in changed_files:
                    if matches_any(rel, forbidden):
                        runtime_errors.append(issue("E_WRITEBACK_CHANGED_FORBIDDEN_PATH", rel))
                    if not matches_any(rel, allowed):
                        runtime_errors.append(issue("E_WRITEBACK_CHANGED_OUTSIDE_SCOPE", rel))
                expected = patchset.get("expected_changed_files")
                if isinstance(expected, list):
                    missing = sorted(set(expected) - set(changed_files))
                    if missing:
                        runtime_errors.append(issue("E_WRITEBACK_EXPECTED_CHANGE_MISSING", str(missing)))
                if runtime_errors:
                    restore_targets(source_root, backups)
                    status = "rolled_back"
                    changed_files = diff_snapshots(pre_snapshot, snapshot(source_root))
                else:
                    status = "applied"
                    if git_commit_requested:
                        git_commit_result, commit_errors = git_commit_after_validation(source_root, changed_files, plan, patchset)
                        if commit_errors:
                            runtime_errors.extend(commit_errors)
                            status = "applied_commit_failed"
                        elif git_commit_result.get("status") == "committed":
                            status = "applied_committed"
        except Exception as exc:  # noqa: BLE001 - convert to machine-readable report
            runtime_errors.append(str(exc))
            if apply_requested and backups:
                restore_targets(source_root, backups)
                status = "rolled_back"
                changed_files = diff_snapshots(pre_snapshot, snapshot(source_root))
            else:
                status = "invalid"

    if errors:
        status = "invalid"

    report = {
        "schema_version": "ppg-latex-writeback-execution-report/v0.1",
        "status": status,
        "plan_ref": to_posix(plan_path.relative_to(ROOT)) if plan_path.is_relative_to(ROOT) else str(plan_path),
        "patchset_ref": to_posix(patch_path.relative_to(ROOT)) if patch_path.is_relative_to(ROOT) else str(patch_path),
        "source_root": str(source_root),
        "stage_id": patchset.get("stage_id"),
        "apply_requested": apply_requested,
        "build_requested": build_requested,
        "git_commit_requested": git_commit_requested,
        "git_commit_result": git_commit_result,
        "materialized_operations": materialized,
        "changed_files": changed_files,
        "contract_errors": errors,
        "runtime_errors": runtime_errors,
        "build_results": build_results,
        "validators_executed": [
            "pre_apply_source_snapshot",
            "patch_target_scope_check",
            "marker_or_file_materialization_check",
            "post_apply_source_snapshot" if apply_requested else "post_apply_source_snapshot:not_run_dry_run",
            "latex_build_after_apply" if build_requested else "latex_build_after_apply:not_requested",
            "scoped_git_commit_after_validation" if git_commit_requested else "scoped_git_commit_after_validation:not_requested",
            "rollback_on_failure_check",
        ],
    }
    report_out = report_path_for(source_root, patchset, args.report_out)
    if report_out is not None:
        write_report(report_out, report)
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if status in {"dry_run_ok", "applied", "applied_committed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
