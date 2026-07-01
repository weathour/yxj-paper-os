#!/usr/bin/env python3
"""Verify the LaTeX source-writeback plan contract.

This validator does not apply patches. It proves that a writeback plan is
stage-scoped, template-aware, owner-gated for external submission, and safe to
hand to a later controller-owned patch/apply implementation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "examples/writeback-plans/latex-writeback.plan.valid.json"
DEFAULT_NEGATIVE = ROOT / "examples/writeback-plans/invalid-unsafe-latex-writeback.plan.json"

REQUIRED_STAGES = {"S10", "S11", "S12", "S15", "S16"}
REQUIRED_VALIDATORS = {
    "pre_apply_source_snapshot",
    "post_apply_source_snapshot",
    "git_diff_scope_check",
    "latex_build_after_apply",
    "claim_boundary_check",
    "reader_surface_check",
    "template_compatibility_check",
    "rollback_on_failure_check",
}
LOCAL_APPLY_MODE = "apply_with_validation_and_rollback"
COMMIT_SCOPE = "changed_files_only"
ALLOWED_SOURCE_PREFIXES = (
    "manuscript/",
    "figures/src/",
    "figures/generated/",
    "paper-os/writeback/",
)
BANNED_ALLOWED_PREFIXES = (
    ".git/",
    ".omx/",
    "exports/",
    "manuscript/build/",
    "manuscript/build_zh/",
    "../",
)
BROAD_PATHS = {"", ".", "./", "..", "../", "/", "manuscript/", "figures/", "figures/src/", "figures/generated/", "exports/"}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"plan must be JSON object: {path}")
    return data


def safe_pattern(value: str) -> bool:
    if value.strip() != value or "\\" in value or "\x00" in value:
        return False
    if value in BROAD_PATHS or value.startswith("~/"):
        return False
    parsed = PurePosixPath(value)
    if parsed.is_absolute():
        return False
    return not any(part in {"", ".", ".."} for part in value.split("/"))


def allowed_source_pattern(value: str) -> bool:
    if not safe_pattern(value):
        return False
    if any(value.startswith(prefix) for prefix in BANNED_ALLOWED_PREFIXES):
        return False
    return any(value.startswith(prefix) for prefix in ALLOWED_SOURCE_PREFIXES)


def pattern_matches_allowed(target: str, allowed: list[str]) -> bool:
    if target in allowed:
        return True
    for prefix in ALLOWED_SOURCE_PREFIXES:
        if target.startswith(prefix) and any(item.startswith(prefix) for item in allowed):
            return True
    return False


def validate_latex_profile(profile: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return [issue("E_WRITEBACK_LATEX_PROFILE", "latex_profile must be object")]
    for key in ["main_tex", "engine", "build_commands", "output_pdf", "template_roots", "template_adapter_policy", "supports_supplied_template"]:
        if key not in profile:
            errors.append(issue("E_WRITEBACK_LATEX_PROFILE", f"missing {key}"))
    if profile.get("main_tex") != "manuscript/main.tex":
        errors.append(issue("E_WRITEBACK_LATEX_MAIN", "main_tex must be manifest-mapped manuscript/main.tex for the standard contract"))
    commands = profile.get("build_commands")
    if not isinstance(commands, list) or not commands or not all(isinstance(cmd, str) and cmd.strip() for cmd in commands):
        errors.append(issue("E_WRITEBACK_LATEX_BUILD", "build_commands required"))
    elif not any("latexmk" in cmd or "pdflatex" in cmd or "xelatex" in cmd or "lualatex" in cmd for cmd in commands):
        errors.append(issue("E_WRITEBACK_LATEX_BUILD", "build command must run a LaTeX engine"))
    if profile.get("template_adapter_policy") != "preserve_template_preamble_and_inject_controlled_body_units":
        errors.append(issue("E_WRITEBACK_TEMPLATE_POLICY", "template adapter must preserve template preamble and inject controlled body units"))
    if profile.get("supports_supplied_template") is not True:
        errors.append(issue("E_WRITEBACK_TEMPLATE_SUPPORT", "supports_supplied_template must be true"))
    return errors


def validate_stage_writebacks(items: Any, allowed: list[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(items, list):
        return [issue("E_WRITEBACK_STAGE_LIST", "stage_writebacks must be list")]
    by_stage: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            errors.append(issue("E_WRITEBACK_STAGE_ITEM", "stage item must be object"))
            continue
        sid = item.get("stage_id")
        if sid in by_stage:
            errors.append(issue("E_WRITEBACK_STAGE_DUPLICATE", str(sid)))
        if sid not in REQUIRED_STAGES:
            errors.append(issue("E_WRITEBACK_STAGE_SCOPE", f"unexpected stage {sid!r}"))
        else:
            by_stage[str(sid)] = item
        targets = item.get("write_targets")
        if not isinstance(targets, list) or not targets:
            errors.append(issue("E_WRITEBACK_STAGE_TARGETS", f"{sid} write_targets required"))
        else:
            for target in targets:
                if not isinstance(target, str) or not allowed_source_pattern(target):
                    errors.append(issue("E_WRITEBACK_STAGE_TARGET_UNSAFE", f"{sid}: {target!r}"))
                elif not pattern_matches_allowed(target, allowed):
                    errors.append(issue("E_WRITEBACK_STAGE_TARGET_NOT_ALLOWED", f"{sid}: {target}"))
        validators = item.get("validators")
        if not isinstance(validators, list) or not validators:
            errors.append(issue("E_WRITEBACK_STAGE_VALIDATORS", f"{sid} validators required"))
        if item.get("candidate_ref_required") is not True and sid != "S16":
            errors.append(issue("E_WRITEBACK_STAGE_CANDIDATE_REF", f"{sid} must require candidate_ref"))
    missing = sorted(REQUIRED_STAGES - set(by_stage))
    if missing:
        errors.append(issue("E_WRITEBACK_STAGE_MISSING", f"missing {missing}"))
    return errors


def validate_local_apply_policy(policy: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(policy, dict):
        return [issue("E_WRITEBACK_LOCAL_APPLY_POLICY", "local_apply_policy must be object")]
    if policy.get("default_execution_mode") != LOCAL_APPLY_MODE:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_MODE", f"default_execution_mode must be {LOCAL_APPLY_MODE}"))
    if policy.get("human_confirmation_required_for_local_apply") is not False:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_CONFIRMATION", "local manuscript apply must not require a separate human confirmation step"))
    if policy.get("validation_before_persistence") is not True:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_VALIDATION", "validation_before_persistence must be true"))
    if policy.get("rollback_on_validation_failure") is not True:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_ROLLBACK", "rollback_on_validation_failure must be true"))
    if policy.get("git_commit_after_validation") is not True:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_COMMIT", "git_commit_after_validation must be true for the default production loop"))
    if policy.get("commit_scope") != COMMIT_SCOPE:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_COMMIT_SCOPE", f"commit_scope must be {COMMIT_SCOPE}"))
    message = policy.get("commit_message_template")
    if not isinstance(message, str) or "{stage_id}" not in message or "{patchset_id}" not in message:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_COMMIT_MESSAGE", "commit_message_template must include {stage_id} and {patchset_id}"))
    if policy.get("dry_run_available") is not True:
        errors.append(issue("E_WRITEBACK_LOCAL_APPLY_DRY_RUN", "dry_run_available must remain true"))
    return errors


def validate_plan(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "ppg-latex-writeback-plan/v0.1":
        errors.append(issue("E_WRITEBACK_SCHEMA", str(data.get("schema_version"))))
    if data.get("mode") != "staged_patch_promotion":
        errors.append(issue("E_WRITEBACK_MODE", "mode must be staged_patch_promotion"))
    if data.get("default_source_write_forbidden") is not True:
        errors.append(issue("E_WRITEBACK_DEFAULT_FORBIDDEN", "default source writes must remain forbidden"))
    if data.get("controller_commit_required") is not True:
        errors.append(issue("E_WRITEBACK_CONTROLLER_COMMIT", "controller commit required"))
    errors.extend(validate_local_apply_policy(data.get("local_apply_policy")))
    if not isinstance(data.get("workspace_manifest_ref"), str) or not safe_pattern(data["workspace_manifest_ref"]):
        errors.append(issue("E_WRITEBACK_WORKSPACE_REF", "workspace_manifest_ref must be safe repo-relative path"))
    if not isinstance(data.get("source_root"), str) or not data["source_root"].strip():
        errors.append(issue("E_WRITEBACK_SOURCE_ROOT", "source_root required"))
    errors.extend(validate_latex_profile(data.get("latex_profile")))

    allowed = data.get("allowed_source_write_paths")
    if not isinstance(allowed, list) or not allowed:
        errors.append(issue("E_WRITEBACK_ALLOWED_PATHS", "allowed_source_write_paths required"))
        allowed_list: list[str] = []
    else:
        allowed_list = []
        for path in allowed:
            if not isinstance(path, str) or not allowed_source_pattern(path):
                errors.append(issue("E_WRITEBACK_ALLOWED_PATH_UNSAFE", repr(path)))
            else:
                allowed_list.append(path)
    forbidden = data.get("forbidden_source_write_paths")
    if not isinstance(forbidden, list) or not forbidden:
        errors.append(issue("E_WRITEBACK_FORBIDDEN_PATHS", "forbidden_source_write_paths required"))
    else:
        forbidden_text = "\n".join(str(item) for item in forbidden)
        for expected in [".git", ".omx", "manuscript/build", "exports", "../"]:
            if expected not in forbidden_text:
                errors.append(issue("E_WRITEBACK_FORBIDDEN_PATHS", f"missing forbidden surface {expected}"))
    errors.extend(validate_stage_writebacks(data.get("stage_writebacks"), allowed_list))

    validators = data.get("required_validators")
    if not isinstance(validators, list):
        errors.append(issue("E_WRITEBACK_REQUIRED_VALIDATORS", "required_validators must be list"))
    else:
        missing = sorted(REQUIRED_VALIDATORS - set(validators))
        if missing:
            errors.append(issue("E_WRITEBACK_REQUIRED_VALIDATORS", f"missing {missing}"))
    rollback = data.get("rollback_policy")
    if not isinstance(rollback, dict) or rollback.get("pre_apply_snapshot_required") is not True or rollback.get("rollback_if_any_validator_fails") is not True:
        errors.append(issue("E_WRITEBACK_ROLLBACK", "rollback policy must require pre-apply snapshot and rollback on any validator failure"))
    owner = data.get("owner_gate")
    if not isinstance(owner, dict) or owner.get("external_submission") != "required":
        errors.append(issue("E_WRITEBACK_OWNER_GATE", "external submission owner gate required"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", nargs="?", default=str(DEFAULT_PLAN))
    parser.add_argument("--skip-negative", action="store_true")
    args = parser.parse_args()

    plan = Path(args.plan)
    if not plan.is_absolute():
        plan = ROOT / plan
    errors = validate_plan(load_json(plan))

    if not args.skip_negative:
        negative_errors = validate_plan(load_json(DEFAULT_NEGATIVE))
        for expected in ["E_WRITEBACK_MODE", "E_WRITEBACK_DEFAULT_FORBIDDEN", "E_WRITEBACK_LOCAL_APPLY_POLICY", "E_WRITEBACK_ALLOWED_PATH_UNSAFE", "E_WRITEBACK_OWNER_GATE"]:
            if not any(error.startswith(expected) for error in negative_errors):
                errors.append(issue("E_WRITEBACK_NEGATIVE_CASE", f"negative fixture did not trigger {expected}: {negative_errors}"))

    if errors:
        print("INVALID LatexWritebackPlan")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PPG_LATEX_WRITEBACK_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
