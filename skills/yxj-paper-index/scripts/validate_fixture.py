#!/usr/bin/env python3
import sys

sys.dont_write_bytecode = True

from validate_yxj_paper_os import main  # noqa: E402

if len(sys.argv) != 2:
    print("usage: validate_fixture.py <fixture-dir>", file=sys.stderr)
    raise SystemExit(2)
raise SystemExit(main(["fixture", sys.argv[1]]))
