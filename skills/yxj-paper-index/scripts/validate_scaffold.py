#!/usr/bin/env python3
"""Compatibility wrapper for yxj-paper-os scaffold validation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_yxj_paper_os import main  # type: ignore[reportMissingImports]  # noqa: E402


def _normalized_args(argv: list[str]) -> list[str]:
    """Accept legacy `validate_scaffold.py [root]` and forward new subcommands."""
    if not argv:
        return ["scaffold", str(Path(__file__).resolve().parents[3])]
    if argv[0] in {"scaffold", "fixture", "fixtures"}:
        return argv
    return ["scaffold", str(Path(argv[0]))]


if __name__ == "__main__":
    raise SystemExit(main(_normalized_args(sys.argv[1:])))
