#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="${TMPDIR:-/tmp}/phase8-plugin-surface-$$"
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT
mkdir -p "$tmp_dir"
json_out="$tmp_dir/runtime-state.json"
md_out="$tmp_dir/runtime-state.md"

python3 scripts/ppg_runtime_adapter.py --graph examples/runtime/overclaim-loop.phase7-after.json --format json --out "$json_out"
python3 -m json.tool "$json_out" >/dev/null
python3 scripts/ppg_runtime_adapter.py --graph examples/runtime/overclaim-loop.phase7-after.json --format markdown --out "$md_out"

python3 - "$json_out" <<'PY'
import json
import sys
from pathlib import Path
required = [
    "schema_version",
    "graph",
    "active_versions",
    "next_frontier",
    "stale_materials",
    "candidate_materials",
    "owner_decisions",
    "open_review_findings",
    "backflow_tasks",
    "delivery_gates",
    "review_closures",
    "completion_blockers",
]
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
missing = [key for key in required if key not in payload]
if missing:
    raise SystemExit(f"PHASE8_JSON_KEYS_MISSING {missing}")
if payload.get("schema_version") != "ppg-runtime-state-report/v0.1":
    raise SystemExit("PHASE8_JSON_BAD_SCHEMA")
frontier = payload.get("next_frontier", {})
for key in ["id", "kind", "priority", "reason"]:
    if key not in frontier:
        raise SystemExit(f"PHASE8_FRONTIER_KEY_MISSING {key}")
if not payload.get("stale_materials"):
    raise SystemExit("PHASE8_EXPECTED_STALE_MATERIALS")
if not payload.get("open_review_findings"):
    raise SystemExit("PHASE8_EXPECTED_REVIEW_FINDINGS")
if not payload.get("backflow_tasks"):
    raise SystemExit("PHASE8_EXPECTED_BACKFLOW_TASKS")
if not payload.get("delivery_gates"):
    raise SystemExit("PHASE8_EXPECTED_DELIVERY_GATES")
print("PHASE8_JSON_ASSERTIONS_OK")
PY

python3 - "$md_out" <<'PY'
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
required_sections = [
    "## Graph",
    "## Next Frontier",
    "## Active Versions",
    "## Stale Materials",
    "## Review Findings",
    "## Backflow Tasks",
    "## Owner Decisions",
    "## Delivery Gates",
    "## Completion Blockers",
]
missing = [section for section in required_sections if section not in text]
if missing:
    raise SystemExit(f"PHASE8_MARKDOWN_SECTIONS_MISSING {missing}")
print("PHASE8_MARKDOWN_ASSERTIONS_OK")
PY

if python3 scripts/ppg_runtime_adapter.py --graph examples/runtime/invalid-active-candidate.json --format json >"$tmp_dir/invalid.json" 2>"$tmp_dir/invalid.err"; then
  echo "PHASE8_INVALID_GRAPH_UNEXPECTED_PASS" >&2
  exit 1
fi

diff -u examples/runtime-reports/overclaim-loop.phase7-state.json "$json_out"
diff -u examples/runtime-reports/overclaim-loop.phase7-state.md "$md_out"
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
if grep -q 'runtimeStateContent\.innerHTML' docs/runtime-viewer/app.js; then
  echo "PHASE8_RUNTIME_STATE_UNSAFE_INNERHTML" >&2
  exit 1
fi
grep -q 'runtimeStateContent.textContent' docs/runtime-viewer/app.js
grep -q 'createTextElement' docs/runtime-viewer/app.js
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .

echo "PHASE8_PLUGIN_SURFACE_VERIFY_OK"
