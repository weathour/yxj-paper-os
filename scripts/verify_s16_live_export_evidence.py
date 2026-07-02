#!/usr/bin/env python3
"""Verify S16 live-export evidence or explicitly bounded fixture/projection mode."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_MATERIAL = ROOT / "scripts" / "validate_material.py"
DEFAULT_MATERIAL = ROOT / "examples/materials/phase10_s16_export_handoff_package.json"


def fail(code: str, message: str) -> NoReturn:
    print(f"{code}: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("E_S16_LIVE_DOC", "material root must be a mapping")
    return data


def run_validate(path: Path) -> None:
    result = subprocess.run([sys.executable, str(VALIDATE_MATERIAL), str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if result.returncode != 0:
        fail("E_S16_LIVE_SCHEMA", result.stdout)


def safe_repo_file(path_text: str) -> Path:
    if path_text.strip() != path_text or "\\" in path_text or path_text.startswith("~"):
        fail("E_S16_LIVE_PATH", f"unsafe path: {path_text}")
    parsed = PurePosixPath(path_text)
    if parsed.is_absolute() or not parsed.suffix or any(part in {"", ".", ".."} for part in parsed.parts):
        fail("E_S16_LIVE_PATH", f"unsafe path: {path_text}")
    return ROOT / parsed


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_projection(payload: dict[str, Any]) -> None:
    live = payload.get("live_export_verification")
    if not isinstance(live, dict):
        fail("E_S16_LIVE_PROJECTION", "live_export_verification must be an object")
    for key in ("filesystem_paths_checked", "hashes_recomputed", "pdf_opened_from_disk", "physical_export_claimed", "live_handoff_claimed"):
        if live.get(key) is not False:
            fail("E_S16_LIVE_PROJECTION", f"{key} must be false in fixture_projection mode")
    print("PPG_S16_LIVE_EXPORT_EVIDENCE_PROJECTION_OK")


def verify_live(payload: dict[str, Any]) -> None:
    manifest = payload.get("export_manifest", {})
    exported_files = manifest.get("exported_files") if isinstance(manifest, dict) else None
    hashes = payload.get("file_hash_manifest")
    if not isinstance(exported_files, list) or not exported_files:
        fail("E_S16_LIVE_MANIFEST", "export_manifest.exported_files must be non-empty")
    if not isinstance(hashes, list) or not hashes:
        fail("E_S16_LIVE_MANIFEST", "file_hash_manifest must be non-empty")
    hash_manifest = {str(item.get("path")): str(item.get("sha256")) for item in hashes if isinstance(item, dict)}
    for item in exported_files:
        if not isinstance(item, dict):
            fail("E_S16_LIVE_MANIFEST", "export_manifest item must be an object")
        path_text = str(item.get("path") or "")
        path = safe_repo_file(path_text)
        if not path.is_file():
            fail("E_S16_LIVE_FILE", f"missing exported file: {path_text}")
        actual = sha256(path)
        expected = str(item.get("sha256") or "")
        expected_from_hash_manifest = hash_manifest.get(path_text)
        if actual != expected or actual != expected_from_hash_manifest:
            fail("E_S16_LIVE_HASH", f"hash mismatch for {path_text}")
        if item.get("kind") == "pdf" and not path.read_bytes().startswith(b"%PDF"):
            fail("E_S16_LIVE_PDF", f"PDF file does not start with %PDF: {path_text}")
    build = payload.get("build_run_report")
    if not isinstance(build, dict):
        fail("E_S16_LIVE_BUILD", "build_run_report must be an object")
    for key in ("log_ref", "output_pdf"):
        path = safe_repo_file(str(build.get(key) or ""))
        if not path.is_file():
            fail("E_S16_LIVE_BUILD", f"missing build artifact {key}: {build.get(key)}")
    print("PPG_S16_LIVE_EXPORT_EVIDENCE_OK")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MATERIAL
    run_validate(path)
    material = load_json(path)
    payload = material.get("payload")
    if not isinstance(payload, dict):
        fail("E_S16_LIVE_DOC", "payload must be a mapping")
    mode = payload.get("evidence_mode")
    if not isinstance(mode, dict):
        fail("E_S16_LIVE_MODE", "evidence_mode must be an object")
    if mode.get("mode") == "fixture_projection":
        verify_projection(payload)
    elif mode.get("mode") == "live_export":
        verify_live(payload)
    else:
        fail("E_S16_LIVE_MODE", "evidence_mode.mode must be fixture_projection or live_export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
