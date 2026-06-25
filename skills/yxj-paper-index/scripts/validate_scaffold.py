#!/usr/bin/env python3
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from validate_yxj_paper_os import main  # noqa: E402

DEFAULT_ROOT = Path(__file__).resolve().parents[3]


def dispatch(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] in {"scaffold", "fixtures", "fixture"}:
        return main(argv[1:])
    root = Path(argv[1]) if len(argv) > 1 else DEFAULT_ROOT
    return main(["scaffold", str(root)])


raise SystemExit(dispatch(sys.argv))
