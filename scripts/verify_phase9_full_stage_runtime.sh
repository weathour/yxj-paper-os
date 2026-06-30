#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/phase9-full-stage-runtime.XXXXXX")"
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT

pilot_root="examples/local-paper/security-state-aware-mixed-platoon"
source_root="/home/weathour/文档/CPS-Papers/papers/security-state-aware-mixed-platoon"
stage_coverage="$pilot_root/stage_coverage.json"

python3 scripts/verify_phase9_archive_guard.py
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/import_local_paper_pilot.py --source "$source_root" --out "$pilot_root" --check
python3 scripts/generate_local_paper_full_pilot.py --pilot-root "$pilot_root" --check
python3 scripts/verify_local_paper_full_pilot.py "$pilot_root"
python3 scripts/verify_phase9_frontend_stage_coverage.py

python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --stage-coverage "$stage_coverage" \
  --format json \
  --out "$tmp_dir/runtime-with-stage-coverage.json"
python3 - "$tmp_dir/runtime-with-stage-coverage.json" <<'PY'
import json
import sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
coverage = payload.get('stage_coverage')
if not coverage:
    raise SystemExit('PHASE9_ADAPTER_STAGE_COVERAGE_MISSING')
if coverage.get('pilot_stage_run_count') != coverage.get('canonical_stage_count'):
    raise SystemExit('PHASE9_ADAPTER_STAGE_COVERAGE_INCOMPLETE')
if coverage.get('pilot_stage_run_count') != 20:
    raise SystemExit(f"PHASE9_ADAPTER_STAGE_COVERAGE_BAD_COUNT {coverage.get('pilot_stage_run_count')}")
print('PHASE9_ADAPTER_STAGE_COVERAGE_ASSERTIONS_OK')
PY
python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --stage-coverage "$stage_coverage" \
  --format markdown \
  --out "$tmp_dir/runtime-with-stage-coverage.md"
grep -q '## Phase9 Stage Coverage' "$tmp_dir/runtime-with-stage-coverage.md"

python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
bash scripts/verify_phase8_plugin_surface.sh
bash scripts/verify_phase6_task_packets.sh
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-ppg-runtime
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
git diff --check -- .

echo "PHASE9_FULL_STAGE_RUNTIME_VERIFY_OK"
