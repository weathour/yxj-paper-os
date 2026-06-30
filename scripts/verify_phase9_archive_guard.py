#!/usr/bin/env python3
"""Verify Phase9 legacy archive boundaries."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "legacy-yxj-paper-os-design-20260630"
MANIFEST = ARCHIVE / "MANIFEST.md"
ALLOWLIST = [
    "docs/YXJ_PAPER_OS_PROCESS_INVENTORY.md",
    "docs/YXJ_PAPER_OS_NEURAL_LAYER_MAP.md",
    "docs/data/yxj-paper-os-layer-map.json",
    "docs/diagrams/yxj-paper-os-neural-layer-map.drawio",
    "docs/diagrams/yxj-paper-os-neural-layer-map.drawio.png",
    "docs/diagrams/yxj-paper-os-neural-layer-map.png",
    "docs/diagrams/yxj-paper-os-neural-layer-map.svg",
]


def fail(code: str, message: str) -> int:
    print(f"{code}: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not MANIFEST.is_file():
        return fail("E_PHASE9_ARCHIVE_MANIFEST_MISSING", str(MANIFEST.relative_to(ROOT)))
    manifest = MANIFEST.read_text(encoding="utf-8")
    for rel in ALLOWLIST:
        active = ROOT / rel
        archived = ARCHIVE / rel
        if active.exists():
            return fail("E_PHASE9_ARCHIVE_ACTIVE_LEGACY_PRESENT", rel)
        if not archived.is_file():
            return fail("E_PHASE9_ARCHIVE_FILE_MISSING", str(archived.relative_to(ROOT)))
        if rel not in manifest or str(archived.relative_to(ROOT)) not in manifest:
            return fail("E_PHASE9_ARCHIVE_MANIFEST_INCOMPLETE", rel)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    forbidden_active_links = [
        "docs/YXJ_PAPER_OS_PROCESS_INVENTORY.md",
        "docs/YXJ_PAPER_OS_NEURAL_LAYER_MAP.md",
    ]
    for needle in forbidden_active_links:
        if needle in readme:
            return fail("E_PHASE9_ARCHIVE_README_ACTIVE_LINK", needle)
    if "$yxj-plugin-incubator" in readme and "not based on `$yxj-plugin-incubator`" not in readme:
        return fail("E_PHASE9_ARCHIVE_INCUBATOR_ROUTE", "unexpected incubator route in README")
    print("PHASE9_ARCHIVE_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
