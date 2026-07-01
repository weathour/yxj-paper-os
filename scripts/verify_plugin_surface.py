#!/usr/bin/env python3
"""Dependency-free plugin surface sanity checks.

This replaces host-local Codex plugin/skill validator calls in standalone Paper OS
regression scripts. It does not claim marketplace installation; it only proves
that the repo contains a coherent plugin manifest and public manager skill.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(code: str, message: str) -> int:
    print(f"{code}: {message}", file=sys.stderr)
    return 1


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
    print("PPG_PLUGIN_SURFACE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
