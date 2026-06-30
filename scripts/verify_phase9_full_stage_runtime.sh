#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/phase9-full-stage-runtime.XXXXXX")"
repo_negative_pilot="$repo_root/examples/local-paper/.phase9-negative-symlink"
cleanup() { rm -rf "$tmp_dir" "$repo_negative_pilot"; }
trap cleanup EXIT

pilot_root="examples/local-paper/security-state-aware-mixed-platoon"
source_root="/home/weathour/文档/CPS-Papers/papers/security-state-aware-mixed-platoon"
stage_coverage="$pilot_root/stage_coverage.json"

negative_source="$tmp_dir/fake-source"
negative_pilot="$negative_source/pilot-under-source"
mkdir -p "$negative_pilot"
python3 - "$negative_source" "$negative_pilot" <<'PY'
import json
import sys
from pathlib import Path
source = Path(sys.argv[1]).resolve()
pilot = Path(sys.argv[2]).resolve()
(pilot / "manifest.json").write_text(json.dumps({
    "schema_version": "ppg-local-paper-pilot-manifest/v0.1",
    "project_slug": "negative-source-contained",
    "source_root": str(source),
    "runtime_output_root": str(pilot),
    "read_only_source": True,
    "claim_boundary": {},
    "source_git_status_before": "",
    "source_git_status_after": "",
    "source_fingerprint_before": {},
    "source_fingerprint_after": {}
}, indent=2) + "\n", encoding="utf-8")
PY
if python3 scripts/generate_local_paper_full_pilot.py --pilot-root "$negative_pilot" --check >"$tmp_dir/negative-generator.out" 2>"$tmp_dir/negative-generator.err"; then
  echo "PHASE9_NEGATIVE_SOURCE_CONTAINED_GENERATOR_UNEXPECTED_PASS" >&2
  exit 1
fi
if [ -e "$negative_pilot/stage-runs" ] || [ -e "$negative_pilot/artifacts" ] || [ -e "$negative_pilot/graph.json" ] || [ -e "$negative_pilot/stage_coverage.json" ]; then
  echo "PHASE9_NEGATIVE_SOURCE_CONTAINED_GENERATOR_WROTE_OUTPUTS" >&2
  exit 1
fi
symlink_source="$tmp_dir/symlink-source"
mkdir -p "$repo_negative_pilot" "$symlink_source"
echo "unchanged" >"$symlink_source/graph-target.json"
python3 - "$symlink_source" "$repo_negative_pilot" <<'PY'
import json
import sys
from pathlib import Path
source = Path(sys.argv[1]).resolve()
pilot = Path(sys.argv[2]).resolve()
(pilot / "manifest.json").write_text(json.dumps({
    "schema_version": "ppg-local-paper-pilot-manifest/v0.1",
    "project_slug": "negative-symlink-write-through",
    "source_root": str(source),
    "runtime_output_root": str(pilot),
    "read_only_source": True,
    "claim_boundary": {},
    "source_git_status_before": "",
    "source_git_status_after": "",
    "source_fingerprint_before": {},
    "source_fingerprint_after": {}
}, indent=2) + "\n", encoding="utf-8")
PY
ln -s "$symlink_source/graph-target.json" "$repo_negative_pilot/graph.json"
if python3 scripts/generate_local_paper_full_pilot.py --pilot-root "$repo_negative_pilot" --check >"$tmp_dir/negative-symlink.out" 2>"$tmp_dir/negative-symlink.err"; then
  echo "PHASE9_NEGATIVE_SYMLINK_OUTPUT_UNEXPECTED_PASS" >&2
  exit 1
fi
grep -Eq "output file must not be a symlink|output path must remain inside pilot_root" "$tmp_dir/negative-symlink.err"
grep -qx "unchanged" "$symlink_source/graph-target.json"
if [ -e "$repo_negative_pilot/stage-runs" ] || [ -e "$repo_negative_pilot/artifacts" ] || [ -e "$repo_negative_pilot/stage_coverage.json" ]; then
  echo "PHASE9_NEGATIVE_SYMLINK_OUTPUT_WROTE_BEFORE_REJECT" >&2
  exit 1
fi

python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/import_local_paper_pilot.py --source "$source_root" --out "$pilot_root" --check
python3 scripts/generate_local_paper_full_pilot.py --pilot-root "$pilot_root" --check
python3 scripts/verify_local_paper_full_pilot.py "$pilot_root"
python3 scripts/verify_phase9_frontend_stage_coverage.py
git diff --exit-code -- "$pilot_root" docs/runtime-viewer/runtime-graph-data.js
cp -a "$pilot_root" "$tmp_dir/wrong-ref-pilot"
python3 - "$tmp_dir/wrong-ref-pilot" <<'PY'
import json
import sys
from pathlib import Path
run_path = Path(sys.argv[1]) / "stage-runs" / "S10.pilot-stage-run.json"
payload = json.loads(run_path.read_text(encoding="utf-8"))
for item in payload["consumed_materials"]:
    if item.get("kind") == "upstream_stage_output" and item.get("producer_stage_id") == "S09B":
        item["ref"] = "artifacts/S00-owner-semantic-contract.json"
        break
else:
    raise SystemExit("PHASE9_NEGATIVE_WRONG_REF_FIXTURE_MISSING")
run_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
PY
if python3 scripts/verify_local_paper_full_pilot.py "$tmp_dir/wrong-ref-pilot" >"$tmp_dir/wrong-ref.out" 2>"$tmp_dir/wrong-ref.err"; then
  echo "PHASE9_NEGATIVE_WRONG_STAGE_REF_UNEXPECTED_PASS" >&2
  exit 1
fi
grep -q "E_PILOT_RUN_UPSTREAM_REF_WRONG_PRODUCER" "$tmp_dir/wrong-ref.err"
cp -a "$pilot_root" "$tmp_dir/coordinated-wrong-ref-pilot"
python3 - "$tmp_dir/coordinated-wrong-ref-pilot" <<'PY'
import json
import sys
from pathlib import Path
pilot = Path(sys.argv[1])
graph_path = pilot / "graph.json"
graph = json.loads(graph_path.read_text(encoding="utf-8"))
edges = graph["edges"]
edges.append({"id": "negative-extra-edge", "source": "S00", "target": "S10", "kind": "material", "label": "malicious coordinated graph drift"})
graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
run_path = pilot / "stage-runs" / "S10.pilot-stage-run.json"
payload = json.loads(run_path.read_text(encoding="utf-8"))
for item in payload["consumed_materials"]:
    if item.get("kind") == "upstream_stage_output" and item.get("producer_stage_id") == "S09B":
        item["producer_stage_id"] = "S00"
        item["material_id"] = "s00_pilot_output"
        item["ref"] = "artifacts/S00-owner-semantic-contract.json"
        break
else:
    raise SystemExit("PHASE9_NEGATIVE_COORDINATED_WRONG_REF_FIXTURE_MISSING")
run_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
PY
if python3 scripts/verify_local_paper_full_pilot.py "$tmp_dir/coordinated-wrong-ref-pilot" >"$tmp_dir/coordinated-wrong-ref.out" 2>"$tmp_dir/coordinated-wrong-ref.err"; then
  echo "PHASE9_NEGATIVE_COORDINATED_WRONG_REF_UNEXPECTED_PASS" >&2
  exit 1
fi
grep -Eq "E_PILOT_GRAPH_EDGE_SET|E_PILOT_RUN_UPSTREAM_PRODUCER_UNEXPECTED|E_PILOT_RUN_UPSTREAM_PRODUCER_SET" "$tmp_dir/coordinated-wrong-ref.err"

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
if python3 scripts/ppg_runtime_adapter.py \
  --graph examples/runtime/overclaim-loop.phase7-after.json \
  --stage-coverage "$stage_coverage" \
  --format json \
  --out "$stage_coverage" >"$tmp_dir/adapter-overwrite.out" 2>"$tmp_dir/adapter-overwrite.err"; then
  echo "PHASE9_ADAPTER_STAGE_COVERAGE_OVERWRITE_UNEXPECTED_PASS" >&2
  exit 1
fi
grep -q "stage coverage input" "$tmp_dir/adapter-overwrite.err"

python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
bash scripts/verify_phase8_plugin_surface.sh
bash scripts/verify_phase6_task_packets.sh
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
node --check docs/runtime-viewer/runtime-graph-data.js
node --check docs/runtime-viewer/app.js
git diff --check -- .

echo "PHASE9_FULL_STAGE_RUNTIME_VERIFY_OK"
