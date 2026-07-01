#!/usr/bin/env python3
"""Verify the standard PaperWorkspaceContract manifest.

This validator is intentionally dependency-free. It validates the canonical
cross-repository paper directory contract used before LaTeX source-writeback
can be promoted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "examples/paper-workspaces/standard-paper-workspace.valid.json"
DEFAULT_NEGATIVE = ROOT / "examples/paper-workspaces/invalid-broad-paper-workspace.json"

REQUIRED_ROLES = {
    "semantic_control",
    "manuscript_source",
    "latex_template",
    "figure_source",
    "figure_generated",
    "evidence",
    "claim_control",
    "review_backflow",
    "export",
    "runtime_state",
}
BROAD_PATHS = {"", ".", "./", "..", "../", "/", "manuscript/", "figures/", "exports/", "paper-os/"}
RUNTIME_ROLE = "runtime_state"
SOURCE_ROLES = {"manuscript_source", "figure_source", "figure_generated"}


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"manifest must be a JSON object: {path}")
    return data


def is_safe_manifest_path(value: str) -> bool:
    if value.strip() != value or "\\" in value or "\x00" in value:
        return False
    if value in BROAD_PATHS or value.startswith("~/") or value.startswith("../"):
        return False
    parsed = PurePosixPath(value)
    if parsed.is_absolute():
        return False
    return not any(part in {"", ".", ".."} for part in value.split("/"))


def validate_role_paths(role: str, paths: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(paths, list) or not paths:
        return [issue("E_WORKSPACE_ROLE_PATHS", f"{role} must map to a non-empty list")]
    for raw in paths:
        if not isinstance(raw, str) or not is_safe_manifest_path(raw):
            errors.append(issue("E_WORKSPACE_PATH_UNSAFE", f"{role}: {raw!r}"))
            continue
        if role == "manuscript_source" and not raw.startswith("manuscript/"):
            errors.append(issue("E_WORKSPACE_MANUSCRIPT_SCOPE", f"{role}: {raw}"))
        if role == "figure_source" and not raw.startswith("figures/src/"):
            errors.append(issue("E_WORKSPACE_FIGURE_SOURCE_SCOPE", f"{role}: {raw}"))
        if role == "figure_generated" and not raw.startswith("figures/generated/"):
            errors.append(issue("E_WORKSPACE_FIGURE_GENERATED_SCOPE", f"{role}: {raw}"))
        if role == "export" and not raw.startswith("exports/"):
            errors.append(issue("E_WORKSPACE_EXPORT_SCOPE", f"{role}: {raw}"))
        if role == RUNTIME_ROLE and not (raw.startswith("paper-os/") or raw.startswith("runs/")):
            errors.append(issue("E_WORKSPACE_RUNTIME_SCOPE", f"{role}: {raw}"))
    return errors


def validate_latex_profile(profile: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return [issue("E_WORKSPACE_LATEX_PROFILE", "latex_profile must be an object")]
    required = {
        "main_tex",
        "engine",
        "build_commands",
        "output_pdf",
        "section_globs",
        "bib_globs",
        "template_roots",
        "template_status",
        "template_adapter_policy",
    }
    missing = sorted(required - set(profile))
    if missing:
        errors.append(issue("E_WORKSPACE_LATEX_PROFILE", f"missing {missing}"))
    if profile.get("main_tex") != "manuscript/main.tex":
        errors.append(issue("E_WORKSPACE_LATEX_MAIN", "main_tex should be manuscript/main.tex or an explicitly mapped equivalent"))
    build = profile.get("build_commands")
    if not isinstance(build, list) or not build or not all(isinstance(cmd, str) and cmd.strip() for cmd in build):
        errors.append(issue("E_WORKSPACE_LATEX_BUILD", "build_commands must be non-empty"))
    elif not any("latexmk" in cmd or "pdflatex" in cmd or "xelatex" in cmd or "lualatex" in cmd for cmd in build):
        errors.append(issue("E_WORKSPACE_LATEX_BUILD", "build_commands must include a LaTeX engine command"))
    if not isinstance(profile.get("template_roots"), list):
        errors.append(issue("E_WORKSPACE_TEMPLATE_ROOTS", "template_roots must be a list; use an explicit pending status if none exist yet"))
    if profile.get("template_adapter_policy") != "preserve_template_preamble_and_inject_controlled_body_units":
        errors.append(issue("E_WORKSPACE_TEMPLATE_POLICY", "template adapter policy must preserve template preamble and inject controlled body units"))
    return errors


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "ppg-paper-workspace/v0.1":
        errors.append(issue("E_WORKSPACE_SCHEMA", str(data.get("schema_version"))))
    if not isinstance(data.get("project_slug"), str) or not data["project_slug"].strip():
        errors.append(issue("E_WORKSPACE_PROJECT_SLUG", "project_slug required"))
    if data.get("source_root_policy") != "single_paper_root_only":
        errors.append(issue("E_WORKSPACE_ROOT_POLICY", "source_root_policy must be single_paper_root_only"))
    if data.get("external_submission_owner_gated") is not True:
        errors.append(issue("E_WORKSPACE_OWNER_GATE", "external_submission_owner_gated must be true"))

    roles = data.get("roles")
    if not isinstance(roles, dict):
        errors.append(issue("E_WORKSPACE_ROLES", "roles must be an object"))
    else:
        missing = sorted(REQUIRED_ROLES - set(roles))
        if missing:
            errors.append(issue("E_WORKSPACE_ROLE_MISSING", f"missing {missing}"))
        for role, paths in roles.items():
            errors.extend(validate_role_paths(str(role), paths))
        runtime_paths = set(roles.get(RUNTIME_ROLE, [])) if isinstance(roles.get(RUNTIME_ROLE), list) else set()
        for role in SOURCE_ROLES:
            source_paths = set(roles.get(role, [])) if isinstance(roles.get(role), list) else set()
            overlap = sorted(source_paths & runtime_paths)
            if overlap:
                errors.append(issue("E_WORKSPACE_RUNTIME_SOURCE_OVERLAP", f"{role}: {overlap}"))

    errors.extend(validate_latex_profile(data.get("latex_profile")))
    boundary = data.get("runtime_boundary")
    if not isinstance(boundary, dict):
        errors.append(issue("E_WORKSPACE_RUNTIME_BOUNDARY", "runtime_boundary must be object"))
    else:
        if boundary.get("default_source_write_forbidden") is not True:
            errors.append(issue("E_WORKSPACE_RUNTIME_BOUNDARY", "default_source_write_forbidden must be true"))
        if boundary.get("source_writeback_requires_plan") is not True:
            errors.append(issue("E_WORKSPACE_RUNTIME_BOUNDARY", "source_writeback_requires_plan must be true"))
        roots = boundary.get("runtime_output_roots")
        if not isinstance(roots, list) or not roots:
            errors.append(issue("E_WORKSPACE_RUNTIME_OUTPUT_ROOTS", "runtime output roots required"))
        else:
            for root in roots:
                if not isinstance(root, str) or not is_safe_manifest_path(root) or not (root.startswith("paper-os/") or root.startswith("runs/")):
                    errors.append(issue("E_WORKSPACE_RUNTIME_OUTPUT_ROOTS", f"unsafe runtime root {root!r}"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--skip-negative", action="store_true")
    args = parser.parse_args()

    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = ROOT / manifest
    errors = validate_manifest(load_json(manifest))

    if not args.skip_negative:
        negative_errors = validate_manifest(load_json(DEFAULT_NEGATIVE))
        if not any(error.startswith("E_WORKSPACE_PATH_UNSAFE") for error in negative_errors):
            errors.append(issue("E_WORKSPACE_NEGATIVE_CASE", "invalid-broad-paper-workspace did not fail unsafe path checks"))
        if not any(error.startswith("E_WORKSPACE_OWNER_GATE") for error in negative_errors):
            errors.append(issue("E_WORKSPACE_NEGATIVE_CASE", "invalid-broad-paper-workspace did not fail owner gate checks"))
        if not any(error.startswith("E_WORKSPACE_RUNTIME_BOUNDARY") for error in negative_errors):
            errors.append(issue("E_WORKSPACE_NEGATIVE_CASE", "invalid-broad-paper-workspace did not fail runtime boundary checks"))

    if errors:
        print("INVALID PaperWorkspaceContract")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PPG_PAPER_WORKSPACE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
