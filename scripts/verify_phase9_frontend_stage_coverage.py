#!/usr/bin/env python3
"""Verify the runtime viewer embeds the Phase9 stage coverage fixture safely."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "docs" / "runtime-viewer" / "runtime-graph-data.js"
APP_JS = ROOT / "docs" / "runtime-viewer" / "app.js"
COVERAGE_JSON = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon" / "stage_coverage.json"


def run_node(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True, check=False)


def main() -> int:
    expected = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    script = r"""
const fs = require('fs');
global.window = {};
require(process.cwd() + '/docs/runtime-viewer/runtime-graph-data.js');
const payload = global.window.PPG_RUNTIME_GRAPH.stageCoverage;
process.stdout.write(JSON.stringify(payload));
"""
    result = run_node(script)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    embedded = json.loads(result.stdout)
    if embedded != expected:
        print("PHASE9_FRONTEND_STAGE_COVERAGE_DRIFT", file=sys.stderr)
        return 1
    app_text = APP_JS.read_text(encoding="utf-8")
    if "stageCoverageContent.innerHTML" in app_text:
        print("PHASE9_STAGE_COVERAGE_UNSAFE_INNERHTML", file=sys.stderr)
        return 1
    required_snippets = [
        "stageCoverageContent.textContent",
        "renderStageCoverage",
        "stageCoverageMode",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in app_text]
    if missing:
        print(f"PHASE9_STAGE_COVERAGE_UI_SNIPPETS_MISSING {missing}", file=sys.stderr)
        return 1
    print("PHASE9_FRONTEND_STAGE_COVERAGE_SYNC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
