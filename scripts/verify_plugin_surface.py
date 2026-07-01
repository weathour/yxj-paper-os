#!/usr/bin/env python3
"""Dependency-free plugin surface sanity checks.

This replaces host-local Codex plugin/skill validator calls in standalone Paper OS
regression scripts. It does not claim marketplace installation; it only proves
that the repo contains a coherent plugin manifest and public manager skill.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HOST_LOCAL_RE = re.compile(r"(/home/|/Users/|[A-Za-z]:\\\\|/\\.codex/|\\\\\\.codex\\\\)")
ACTIVE_OMX_RE = re.compile(r"(^|[\s`\"'$(:/])(omx|oh-my-codex)([\s`\"'):/]|$)", re.IGNORECASE)
PUBLIC_SCAN_PATHS = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "PRODUCT.md",
    ROOT / ".codex-plugin/plugin.json",
    ROOT / "skills/yxj-paper-os/SKILL.md",
    ROOT / "docs/MANAGER_SURFACE_PROTOCOL.md",
    ROOT / "docs/RUNTIME_PROTOCOL.md",
    ROOT / "docs/FEEDBACK_LIFECYCLE_PROTOCOL.md",
    ROOT / "docs/BACKFLOW_PROTOCOL.md",
    ROOT / "docs/MATERIAL_SCHEMA.md",
    ROOT / "docs/VALIDATION_AND_TESTING.md",
    ROOT / "docs/runtime-viewer/index.html",
    ROOT / "docs/runtime-viewer/runtime-graph-data.js",
    ROOT / "examples/local-paper/sample-paper-workspace/manifest.json",
    ROOT / "examples/local-paper/sample-paper-workspace/stage_coverage.json",
    ROOT / "examples/paper-workspaces/standard-paper-workspace.valid.json",
    ROOT / "examples/writeback-plans/latex-writeback.plan.valid.json",
    ROOT / "examples/writeback-plans/fixture-latex-writeback.plan.valid.json",
]
ACCEPTANCE_SCRIPTS = [
    ROOT / "scripts/import_local_paper_pilot.py",
    ROOT / "scripts/generate_local_paper_full_pilot.py",
    ROOT / "scripts/generate_phase10_run_dry_run.py",
    ROOT / "scripts/generate_phase12_full_flow_run.py",
    ROOT / "scripts/generate_phase13_live_pilot.py",
    ROOT / "scripts/verify_phase9_full_stage_runtime.sh",
    ROOT / "scripts/verify_phase10_real_run_readiness.sh",
    ROOT / "scripts/verify_phase12_formal_full_flow.sh",
    ROOT / "scripts/verify_phase13_live_subagent_pilot.sh",
]


def fail(code: str, message: str) -> int:
    print(f"{code}: {message}", file=sys.stderr)
    return 1


def iter_text_lines(path: Path) -> list[tuple[int, str]]:
    if not path.exists() or not path.is_file():
        return []
    try:
        return list(enumerate(path.read_text(encoding="utf-8").splitlines(), start=1))
    except UnicodeDecodeError:
        return []


def public_surface_violations() -> list[str]:
    violations: list[str] = []
    for path in PUBLIC_SCAN_PATHS + ACCEPTANCE_SCRIPTS:
        for lineno, line in iter_text_lines(path):
            stripped = line.strip()
            if path.name == "verify_plugin_surface.py":
                continue
            # Allow the public doctrine to mention optional OMX adapters, but not
            # commands or required authority dependencies.
            allowed_optional = "optional" in stripped.lower() and ("omx" in stripped.lower() or "oh-my-codex" in stripped.lower())
            if HOST_LOCAL_RE.search(stripped):
                violations.append(f"{path.relative_to(ROOT)}:{lineno}: host-local path")
            if ACTIVE_OMX_RE.search(stripped) and not allowed_optional and "does not depend on OMX" not in stripped:
                violations.append(f"{path.relative_to(ROOT)}:{lineno}: active OMX dependency")
    return violations


def viewer_asset_violations() -> list[str]:
    html_path = ROOT / "docs/runtime-viewer/index.html"
    text = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    refs = re.findall(r"""(?:src|href)=["']([^"'#][^"']*)["']""", text)
    violations: list[str] = []
    for ref in refs:
        if ref.startswith(("http://", "https://", "mailto:", "javascript:")):
            continue
        path = (html_path.parent / ref).resolve(strict=False)
        try:
            path.relative_to(ROOT.resolve(strict=True))
        except ValueError:
            violations.append(f"docs/runtime-viewer/index.html: asset escapes repo: {ref}")
            continue
        if not path.exists():
            violations.append(f"docs/runtime-viewer/index.html: missing asset: {ref}")
    return violations


def main() -> int:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    skill_path = ROOT / "skills" / "yxj-paper-os" / "SKILL.md"
    if not manifest_path.is_file():
        return fail("E_PLUGIN_MANIFEST_MISSING", str(manifest_path))
    if not skill_path.is_file():
        return fail("E_PLUGIN_SKILL_MISSING", str(skill_path))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail("E_PLUGIN_MANIFEST_JSON", str(exc))
    if manifest.get("name") != "yxj-paper-os":
        return fail("E_PLUGIN_NAME", "manifest name must be yxj-paper-os")
    if manifest.get("skills") != "./skills/":
        return fail("E_PLUGIN_SKILLS_PATH", "manifest skills must be ./skills/")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        return fail("E_PLUGIN_INTERFACE", "interface object required")
    for key in ["displayName", "shortDescription", "longDescription", "capabilities", "defaultPrompt"]:
        if key not in interface:
            return fail("E_PLUGIN_INTERFACE", f"interface.{key} required")
    skill = skill_path.read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        return fail("E_SKILL_FRONTMATTER", "skill frontmatter required")
    if "name: yxj-paper-os" not in skill:
        return fail("E_SKILL_NAME", "skill name must be yxj-paper-os")
    if "Paper Production Graph Runtime Controller" not in skill:
        return fail("E_SKILL_CONTROLLER_IDENTITY", "controller identity missing")
    if "does not depend on OMX" not in skill:
        return fail("E_SKILL_STANDALONE_BOUNDARY", "standalone boundary missing")
    public_violations = public_surface_violations()
    if public_violations:
        return fail("E_PLUGIN_STANDALONE_SCAN", "; ".join(public_violations[:8]))
    asset_violations = viewer_asset_violations()
    if asset_violations:
        return fail("E_PLUGIN_VIEWER_ASSET_LINK", "; ".join(asset_violations[:8]))
    print("PPG_PLUGIN_SURFACE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
