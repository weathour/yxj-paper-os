#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/phase8-plugin-surface.XXXXXX")"
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT
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
    "closed_review_findings",
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
    raise SystemExit("PHASE8_EXPECTED_OPEN_REVIEW_FINDINGS")
if not payload.get("closed_review_findings"):
    raise SystemExit("PHASE8_EXPECTED_CLOSED_REVIEW_FINDINGS")
for finding in payload.get("open_review_findings", []):
    if finding.get("closure_status") != "open":
        raise SystemExit("PHASE8_OPEN_FINDING_BAD_CLOSURE_STATUS")
for finding in payload.get("closed_review_findings", []):
    if finding.get("closure_status") != "closed" or not finding.get("closed_by"):
        raise SystemExit("PHASE8_CLOSED_FINDING_MISSING_CLOSURE")
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
    "## Open Review Findings",
    "## Closed Review Findings",
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

if python3 scripts/ppg_runtime_adapter.py --graph examples/runtime/overclaim-loop.phase7-after.json --format json --out examples/runtime/overclaim-loop.phase7-after.json >"$tmp_dir/out-guard.json" 2>"$tmp_dir/out-guard.err"; then
  echo "PHASE8_OUT_GUARD_UNEXPECTED_PASS" >&2
  exit 1
fi

cp examples/runtime/overclaim-loop.phase7-after.json "$tmp_dir/graph-copy.json"
ln "$tmp_dir/graph-copy.json" "$tmp_dir/graph-hardlink.json"
if python3 scripts/ppg_runtime_adapter.py --graph "$tmp_dir/graph-copy.json" --format markdown --out "$tmp_dir/graph-hardlink.json" >"$tmp_dir/hardlink-guard.json" 2>"$tmp_dir/hardlink-guard.err"; then
  echo "PHASE8_HARDLINK_OUT_GUARD_UNEXPECTED_PASS" >&2
  exit 1
fi
python3 -m json.tool "$tmp_dir/graph-copy.json" >/dev/null

python3 - "$tmp_dir/blocked-closure.json" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(Path('examples/runtime/overclaim-loop.phase7-after.json').read_text(encoding='utf-8'))
for node in payload.get('nodes', []):
    if node.get('id') == 'phase7_overclaim_closure_v1':
        node['status'] = 'blocked'
        break
path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
PY
python3 scripts/ppg_runtime_adapter.py --graph "$tmp_dir/blocked-closure.json" --format json --out "$tmp_dir/blocked-closure-state.json"
python3 - "$tmp_dir/blocked-closure-state.json" <<'PY'
import json
import sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
open_ids = {item['id'] for item in payload.get('open_review_findings', [])}
closed_ids = {item['id'] for item in payload.get('closed_review_findings', [])}
if 'phase7_overclaim_review_finding_v1' not in open_ids:
    raise SystemExit('PHASE8_BLOCKED_CLOSURE_FINDING_NOT_OPEN')
if 'phase7_overclaim_review_finding_v1' in closed_ids:
    raise SystemExit('PHASE8_BLOCKED_CLOSURE_FINDING_STILL_CLOSED')
print('PHASE8_BLOCKED_CLOSURE_ASSERTIONS_OK')
PY

diff -u examples/runtime-reports/overclaim-loop.phase7-state.json "$json_out"
diff -u examples/runtime-reports/overclaim-loop.phase7-state.md "$md_out"
node - <<'JS'
const fs = require('fs');
global.window = {};
require(process.cwd() + '/docs/runtime-viewer/runtime-graph-data.js');
const embedded = global.window.PPG_RUNTIME_GRAPH.runtimeState;
const fixture = JSON.parse(fs.readFileSync('examples/runtime-reports/overclaim-loop.phase7-state.json', 'utf8'));
if (JSON.stringify(embedded) !== JSON.stringify(fixture)) {
  console.error('PHASE8_FRONTEND_RUNTIME_STATE_DRIFT');
  process.exit(1);
}
console.log('PHASE8_FRONTEND_RUNTIME_STATE_SYNC_OK');
JS
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
if grep -q 'runtimeStateContent\.innerHTML' docs/runtime-viewer/app.js; then
  echo "PHASE8_RUNTIME_STATE_UNSAFE_INNERHTML" >&2
  exit 1
fi
grep -q 'runtimeStateContent.textContent' docs/runtime-viewer/app.js
grep -q 'createTextElement' docs/runtime-viewer/app.js
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-ppg-runtime
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
bash scripts/verify_phase6_task_packets.sh

echo "PHASE8_PLUGIN_SURFACE_VERIFY_OK"
