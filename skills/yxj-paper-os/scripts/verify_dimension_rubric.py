#!/usr/bin/env python3
"""Sparse structural check for the cognitive-kernel rubric."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"
REQUIRED = [
    "00-dimension-rubric.md",
    "00-project-route.md",
    "01-materials-inventory.md",
    "02-claim-evidence-boundary.md",
    "03-writing-structure.md",
    "04-design-pack-compiler.md",
]
# Kept as a compatibility export for dashboard fixtures; the sparse contract
# intentionally does not require a universal question ladder.
QUESTION_DEPTH_LADDER_FIELDS: list[str] = []


def main() -> int:
    errors = [f"missing reference: {n}" for n in REQUIRED if not (REF / n).exists()]
    rubric = (
        (REF / "00-dimension-rubric.md").read_text(encoding="utf-8")
        if not errors
        else ""
    )
    ids = re.findall(r"\bD(?:0[0-9]|1[0-9])\b", rubric)
    missing = [f"D{i:02d}" for i in range(20) if f"D{i:02d}" not in ids]
    if missing:
        errors.append("rubric missing dimensions: " + ", ".join(missing))
    if errors:
        print("Sparse rubric validation failed:", *[f"- {e}" for e in errors], sep="\n")
        return 1
    print("Sparse rubric structural validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
