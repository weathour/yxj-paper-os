#!/usr/bin/env python3
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from validate_yxj_paper_os import main  # noqa: E402

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
raise SystemExit(main(["fixtures", str(root)]))
