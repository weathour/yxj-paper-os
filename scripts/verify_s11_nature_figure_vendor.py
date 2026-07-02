#!/usr/bin/env python3
"""Verify the vendored nature-figure capability layer for S11."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, NoReturn


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "third_party" / "nature-figure"
MANIFEST = VENDOR / "PARITY_MANIFEST.json"
EXPECTED_COMMIT = "c91df241a7a963ea151687ac669c5534404f53e5"
EXPECTED_VERSION = "2.0.0"
EXPECTED_SCHEMA = "yxj-paper-os-nature-figure-parity/v0.1"
REQUIRED_TOP_LEVEL = {"SKILL.md", "manifest.yaml", "README.md", "LICENSE", "UPSTREAM.md"}
REQUIRED_DIRS = {"static", "references", "assets", "evals"}
REQUIRED_CORE_PATHS = {
    "static/core/contract.md",
    "static/core/stance.md",
    "static/fragments/backend/python.md",
    "static/fragments/backend/r.md",
    "references/figure-contract.md",
    "references/backend-selection.md",
    "references/qa-contract.md",
    "references/design-theory.md",
    "references/api.md",
    "references/common-patterns.md",
    "references/chart-types.md",
    "references/demos.md",
}
REQUIRED_SKILL_PHRASES = {
    "Python or R?",
    "Use only the selected backend",
    "static/core/contract.md",
    "static/core/stance.md",
}
LOCAL_MANIFEST_FILES = {"PARITY_MANIFEST.json"}


def _fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        _fail("E_S11_NATURE_VENDOR_JSON", f"{path}: {exc}")
    if not isinstance(data, dict):
        _fail("E_S11_NATURE_VENDOR_JSON", f"{path}: root must be an object")
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean_ref(ref: str) -> str:
    return ref.rstrip(".,:;`")


def _manifest_refs_from_text(text: str) -> set[str]:
    refs = {
        _clean_ref(match)
        for match in re.findall(r"(?:static|references|assets|evals)/[^\s\]\)\"']+", text)
    }
    return {ref for ref in refs if "." in Path(ref).name}


def _asset_refs_from_texts(files: list[Path]) -> set[str]:
    refs: set[str] = set()
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # pragma: no cover - binary assets are skipped by suffix filter
            continue
        for match in re.findall(r"(?:\.\./)?assets/[^\s\]\)\"']+", text):
            value = _clean_ref(match)
            if value.startswith("../"):
                value = value[3:]
            refs.add(value)
    return refs


def _verify_manifest(data: dict[str, Any]) -> None:
    if data.get("schema_version") != EXPECTED_SCHEMA:
        _fail("E_S11_NATURE_VENDOR_SCHEMA", f"schema_version must be {EXPECTED_SCHEMA}")
    upstream = data.get("upstream")
    if not isinstance(upstream, dict):
        _fail("E_S11_NATURE_VENDOR_UPSTREAM", "upstream must be present")
    if upstream.get("commit") != EXPECTED_COMMIT:
        _fail("E_S11_NATURE_VENDOR_UPSTREAM", "upstream commit mismatch")
    if upstream.get("version") != EXPECTED_VERSION:
        _fail("E_S11_NATURE_VENDOR_UPSTREAM", "upstream version mismatch")
    if upstream.get("license") != "Apache-2.0":
        _fail("E_S11_NATURE_VENDOR_UPSTREAM", "upstream license must be Apache-2.0")
    required_top = set(data.get("required_top_level_files", []))
    missing_top = sorted(REQUIRED_TOP_LEVEL - required_top)
    if missing_top:
        _fail("E_S11_NATURE_VENDOR_MANIFEST", f"required_top_level_files missing {missing_top}")
    required_dirs = set(data.get("required_directories", []))
    missing_dirs = sorted(REQUIRED_DIRS - required_dirs)
    if missing_dirs:
        _fail("E_S11_NATURE_VENDOR_MANIFEST", f"required_directories missing {missing_dirs}")
    exclusions = data.get("exclusion_policy")
    if not isinstance(exclusions, dict) or exclusions.get("excluded_paths") not in ([], None):
        _fail("E_S11_NATURE_VENDOR_EXCLUSION", "unexpected vendored capability exclusions")


def _verify_inventory(data: dict[str, Any]) -> None:
    files = data.get("files")
    if not isinstance(files, list) or len(files) < 80:
        _fail("E_S11_NATURE_VENDOR_INVENTORY", "files inventory is missing or too small for full vendor")
    indexed: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            _fail("E_S11_NATURE_VENDOR_INVENTORY", "file inventory entries must be objects with path")
        rel = item["path"]
        if rel.startswith("/") or ".." in rel.split("/"):
            _fail("E_S11_NATURE_VENDOR_PATH", f"unsafe inventory path {rel!r}")
        indexed[rel] = item
        path = VENDOR / rel
        if not path.is_file():
            _fail("E_S11_NATURE_VENDOR_FILE", f"vendored file missing: {rel}")
        if item.get("sha256") != _sha256(path):
            _fail("E_S11_NATURE_VENDOR_HASH", f"sha256 mismatch for {rel}")
        if item.get("bytes") != path.stat().st_size:
            _fail("E_S11_NATURE_VENDOR_SIZE", f"size mismatch for {rel}")
    missing_core = sorted((REQUIRED_TOP_LEVEL | REQUIRED_CORE_PATHS) - set(indexed))
    if missing_core:
        _fail("E_S11_NATURE_VENDOR_REQUIRED", f"required files missing from inventory: {missing_core}")
    actual_files = {
        str(path.relative_to(VENDOR))
        for path in VENDOR.rglob("*")
        if path.is_file()
    }
    unexpected_files = sorted(actual_files - set(indexed) - LOCAL_MANIFEST_FILES)
    if unexpected_files:
        _fail("E_S11_NATURE_VENDOR_EXTRA_FILE", f"vendored files not recorded in parity manifest: {unexpected_files}")
    for directory in REQUIRED_DIRS:
        path = VENDOR / directory
        if not path.is_dir() or not any(path.rglob("*")):
            _fail("E_S11_NATURE_VENDOR_DIR", f"required vendor directory missing/empty: {directory}")


def _verify_references(data: dict[str, Any]) -> None:
    manifest_yaml = VENDOR / "manifest.yaml"
    manifest_refs = _manifest_refs_from_text(manifest_yaml.read_text(encoding="utf-8"))
    recorded_manifest_refs = set(data.get("manifest_references", []))
    missing_recorded = sorted(manifest_refs - recorded_manifest_refs)
    if missing_recorded:
        _fail("E_S11_NATURE_VENDOR_REFS", f"manifest references not recorded: {missing_recorded}")
    missing_manifest_paths = sorted(ref for ref in recorded_manifest_refs if not (VENDOR / ref).exists())
    if missing_manifest_paths:
        _fail("E_S11_NATURE_VENDOR_REFS", f"manifest referenced paths missing: {missing_manifest_paths}")

    text_files = [
        path
        for path in VENDOR.rglob("*")
        if path.is_file()
        and path.name not in {"PARITY_MANIFEST.json", "UPSTREAM.md"}
        and path.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".py", ".r", ".txt"}
    ]
    asset_refs = _asset_refs_from_texts(text_files)
    recorded_asset_refs = set(data.get("referenced_asset_paths", []))
    missing_asset_records = sorted(asset_refs - recorded_asset_refs)
    if missing_asset_records:
        _fail("E_S11_NATURE_VENDOR_ASSET_REF", f"asset references not recorded: {missing_asset_records}")
    missing_asset_paths = sorted(
        ref
        for ref in recorded_asset_refs
        if not (list(VENDOR.glob(ref)) if "*" in ref else (VENDOR / ref).exists())
    )
    if missing_asset_paths:
        _fail("E_S11_NATURE_VENDOR_ASSET", f"referenced assets missing: {missing_asset_paths}")


def _verify_skill_contract() -> None:
    skill = (VENDOR / "SKILL.md").read_text(encoding="utf-8")
    for phrase in REQUIRED_SKILL_PHRASES:
        if phrase not in skill:
            _fail("E_S11_NATURE_VENDOR_SKILL", f"SKILL.md missing phrase {phrase!r}")
    if f"version: {EXPECTED_VERSION}" not in skill:
        _fail("E_S11_NATURE_VENDOR_SKILL", "SKILL.md version mismatch")
    license_text = (VENDOR / "LICENSE").read_text(encoding="utf-8", errors="ignore")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        _fail("E_S11_NATURE_VENDOR_LICENSE", "Apache-2.0 license text missing")
    upstream = (VENDOR / "UPSTREAM.md").read_text(encoding="utf-8")
    if EXPECTED_COMMIT not in upstream or "S11.nature_figure_production_pass" not in upstream:
        _fail("E_S11_NATURE_VENDOR_UPSTREAM", "UPSTREAM.md missing pinned commit or S11 use")


def main() -> int:
    if not VENDOR.is_dir():
        _fail("E_S11_NATURE_VENDOR_MISSING", "third_party/nature-figure is missing")
    if not MANIFEST.is_file():
        _fail("E_S11_NATURE_VENDOR_MANIFEST", "PARITY_MANIFEST.json is missing")
    data = _load_json(MANIFEST)
    _verify_manifest(data)
    _verify_inventory(data)
    _verify_references(data)
    _verify_skill_contract()
    print("PPG_S11_NATURE_FIGURE_VENDOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
