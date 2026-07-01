#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

cleanup_paths=()
cleanup_files=()
cleanup_dirs=()
negative_run=""
cleanup() {
  for path in "${cleanup_paths[@]:-}"; do
    if [[ "$path" == "$repo_root/runs/.phase12-negative-"* || "$path" == "$repo_root/runs/.phase12-negative."* ]]; then
      rm -rf -- "$path"
    fi
  done
  for path in "${cleanup_files[@]:-}"; do
    if [[ "$path" == /tmp/* ]]; then
      rm -f -- "$path"
    fi
  done
  for path in "${cleanup_dirs[@]:-}"; do
    if [[ "$path" == /tmp/* ]]; then
      rm -rf -- "$path"
    fi
  done
}
trap cleanup EXIT

make_negative_run() {
  local label=$1
  negative_run=$(mktemp -d "$repo_root/runs/.phase12-negative-${label}.XXXXXX")
  cleanup_paths+=("$negative_run")
  python3 scripts/generate_phase12_full_flow_run.py --run-root "$negative_run" --check >/dev/null
}

assert_fails_with() {
  local expected=$1
  shift
  local out
  out=$(mktemp)
  set +e
  "$@" >"$out" 2>&1
  local rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "EXPECTED_FAILURE_MISSING: $*" >&2
    cat "$out" >&2
    rm -f "$out"
    exit 1
  fi
  if ! grep -q "$expected" "$out"; then
    echo "EXPECTED_ERROR_CODE_MISSING expected=$expected cmd=$*" >&2
    cat "$out" >&2
    rm -f "$out"
    exit 1
  fi
  rm -f "$out"
}

python3 scripts/generate_phase12_full_flow_run.py --check
python3 scripts/verify_phase12_full_flow_run.py

python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')
import generate_phase12_full_flow_run as gen
pilot_manifest = gen.load_json(gen.DEFAULT_PILOT / 'manifest.json')
source_root = Path(str(pilot_manifest['source_root'])).resolve(strict=True)
called = []
def fake_rmtree(path):
    called.append(str(path))
for target in [gen.ROOT / 'runs', gen.ROOT / 'runs' / 'security-state-aware-mixed-platoon']:
    gen.shutil.rmtree = fake_rmtree
    try:
        gen.clean_run_root(target, source_root)
    except ValueError as exc:
        if 'unsafe Phase12 run root cleanup target' not in str(exc):
            raise SystemExit(f'NEGATIVE_BROAD_RUN_ROOT_WRONG_ERROR: {target}: {exc}')
    else:
        raise SystemExit(f'NEGATIVE_BROAD_RUN_ROOT_NOT_REJECTED: {target}')
    if called:
        raise SystemExit(f'NEGATIVE_BROAD_RUN_ROOT_ATTEMPTED_DELETE: {called}')
print('NEGATIVE_PHASE12_BROAD_RUN_ROOT_CLEANUP_OK')
PY

rootlink="$repo_root/runs/.phase12-negative-rootlink"
rm -rf -- "$rootlink"
external_root=$(mktemp -d)
cleanup_paths+=("$rootlink")
cleanup_dirs+=("$external_root")
printf '{not-json: external sentinel}\n' > "$external_root/manifest.json"
printf '{}\n' > "$external_root/run_state.json"
ln -s "$external_root" "$rootlink"
out=$(mktemp)
set +e
python3 scripts/verify_phase12_full_flow_run.py "$rootlink" >"$out" 2>&1
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  echo "EXPECTED_FAILURE_MISSING: run-root symlink" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
if ! grep -q E_PHASE12_RUN_ROOT "$out"; then
  echo "EXPECTED_ERROR_CODE_MISSING expected=E_PHASE12_RUN_ROOT run-root symlink" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
if grep -q E_PHASE12_JSON_PARSE "$out"; then
  echo "RUN_ROOT_VALIDATOR_READ_SYMLINK_TARGET" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
rm -f "$out"
echo NEGATIVE_PHASE12_RUN_ROOT_SYMLINK_NO_READ_OK

make_negative_run backflow-chain
: > "$negative_run/backflow_ledger.jsonl"
assert_fails_with E_PHASE12_BACKFLOW_CHAIN python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_BACKFLOW_CHAIN_OK

make_negative_run bare-s09
python3 - "$negative_run/run_state.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['canonical_stage_ids'][0]='S09'; data['stages'][0]['stage_id']='S09'
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_BARE_S09 python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_BARE_S09_OK

make_negative_run overlay-link
python3 - "$negative_run/candidate-artifacts/S02.candidate.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data.pop('active_stage_overlays', None)
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_STAGE_OVERLAY_LINK python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_OVERLAY_LINK_OK

make_negative_run completion-overclaim
python3 - "$negative_run/candidate-artifacts/S02.candidate.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['completion_boundary']='submission ready'
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_COMPLETION_OVERCLAIM python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_COMPLETION_OVERCLAIM_OK

make_negative_run packet-output-escape
python3 - "$negative_run/packets/S02.task-packet.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['output_artifact_path']='examples/materials/phase12_escape.yaml'
data['allowed_write_paths']=['examples/materials/phase12_escape.yaml']
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_RUN_PACKET_OUTPUT_BOUNDARY python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_PACKET_OUTPUT_ESCAPE_OK

make_negative_run source-snapshot-drift
python3 - "$negative_run/source_snapshot.after.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
entries=data['entries']; key=next(k for k,v in entries.items() if isinstance(v,dict) and v.get('kind')=='file' and 'sha256' in v)
entries[key]=dict(entries[key]); entries[key]['sha256']='0'*64
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_SOURCE_SNAPSHOT_DRIFT python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_SOURCE_SNAPSHOT_DRIFT_OK

make_negative_run source-current-drift
python3 - "$negative_run/source_snapshot.before.json" "$negative_run/source_snapshot.after.json" <<'PY'
import json, sys
from pathlib import Path
paths=[Path(sys.argv[1]), Path(sys.argv[2])]
data=json.loads(paths[0].read_text())
entries=data['entries']; key=next(k for k,v in entries.items() if isinstance(v,dict) and v.get('kind')=='file' and 'sha256' in v)
entries[key]=dict(entries[key]); entries[key]['sha256']='1'*64
for p in paths:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_SOURCE_SNAPSHOT_CURRENT_DRIFT python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_SOURCE_CURRENT_DRIFT_OK
echo NEGATIVE_PHASE12_SOURCE_DRIFT_OK

make_negative_run source-runtime-artifact
python3 - "$negative_run/source_snapshot.before.json" "$negative_run/source_snapshot.after.json" <<'PY'
import json, sys
from pathlib import Path
entry = {"kind": "file", "size": 1, "sha256": "1" * 64}
for arg in sys.argv[1:]:
    p = Path(arg)
    data = json.loads(p.read_text())
    data["entries"]["docs/runtime-viewer/index.html"] = entry
    rows = data.setdefault("git_status_porcelain_v1", [])
    if "?? docs/runtime-viewer/index.html" not in rows:
        rows.append("?? docs/runtime-viewer/index.html")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
PY
assert_fails_with E_PHASE12_SOURCE_RUNTIME_ARTIFACT python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_SOURCE_RUNTIME_ARTIFACT_OK

make_negative_run candidate-authority
python3 - "$negative_run/candidate-artifacts/S02.candidate.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['candidate_only']=False
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_CANDIDATE_AUTHORITY python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_CANDIDATE_AUTHORITY_OK

make_negative_run controller-commit-required
python3 - "$negative_run/candidate-artifacts/S02.candidate.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['controller_commit_required']=False
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_CONTROLLER_COMMIT_REQUIRED python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_CONTROLLER_COMMIT_REQUIRED_OK

make_negative_run worker-completion-forbidden
python3 - "$negative_run/dispatch/S02.dispatch.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['worker_authority']['completion_forbidden']=False
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_WORKER_COMPLETION_FORBIDDEN python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_WORKER_COMPLETION_FORBIDDEN_OK

make_negative_run non-worker-fake-packet
python3 - "$negative_run/run_state.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
for stage in data['stages']:
    if stage['stage_id']=='S00':
        stage['packet_ref']='packets/S02.task-packet.json'
        break
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_NON_WORKER_FAKE_PACKET python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_NON_WORKER_FAKE_PACKET_OK

make_negative_run owner-ledger-tamper
python3 - "$negative_run/owner_decision_log.jsonl" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); events=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
events[-1]['writes_to_source_allowed']=True
p.write_text(''.join(json.dumps(e, ensure_ascii=False, sort_keys=True)+'\n' for e in events))
PY
assert_fails_with E_PHASE12_OWNER_LEDGER_TAMPER python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_OWNER_LEDGER_TAMPER_OK

python3 - <<'PY'
import copy, json, sys
sys.path.insert(0, 'scripts')
from verify_phase12_full_flow_run import OVERLAY_REGISTRY, load_json, validate_overlay_authority
registry = copy.deepcopy(load_json(OVERLAY_REGISTRY))
registry['overlays'][0]['authority_model']['overlay_dispatch_allowed'] = True
errors = validate_overlay_authority(registry)
if not any('E_PHASE12_OVERLAY_AUTHORITY' in error for error in errors):
    raise SystemExit(f'NEGATIVE_OVERLAY_AUTHORITY_MISSING: {errors}')
print('NEGATIVE_PHASE12_OVERLAY_AUTHORITY_OK')
PY

make_negative_run doc-boundary
printf '\nThis runtime is submission ready.\n' >> "$negative_run/final-report.md"
assert_fails_with E_PHASE12_DOC_BOUNDARY python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_DOC_BOUNDARY_OK

make_negative_run symlink-run-ref
ln -s S02.candidate.json "$negative_run/candidate-artifacts/S02.symlink-candidate.json"
python3 - "$negative_run/run_state.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
for stage in data['stages']:
    if stage['stage_id']=='S02':
        stage['candidate_ref']='candidate-artifacts/S02.symlink-candidate.json'
        break
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_RUN_REF python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_SYMLINK_RUN_REF_OK

make_negative_run symlink-packet-output
ln -s S02.candidate.json "$negative_run/candidate-artifacts/S02.symlink-output.json"
python3 - "$negative_run/packets/S02.task-packet.json" "$negative_run" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); run_root=Path(sys.argv[2]).resolve(); data=json.loads(p.read_text())
repo_root=Path.cwd().resolve(); ref=(run_root/'candidate-artifacts/S02.symlink-output.json').relative_to(repo_root).as_posix()
data['output_artifact_path']=ref; data['allowed_write_paths']=[ref]
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE12_RUN_PACKET_OUTPUT_BOUNDARY python3 scripts/verify_phase12_full_flow_run.py "$negative_run"
echo NEGATIVE_PHASE12_SYMLINK_PACKET_OUTPUT_OK
echo NEGATIVE_PHASE12_SYMLINK_REF_OK

make_negative_run boundary-symlink
external_boundary=$(mktemp)
printf 'external sentinel: submission ready\n' > "$external_boundary"
cleanup_files+=("$external_boundary")
ln -s "$external_boundary" "$negative_run/unreferenced-external.md"
out=$(mktemp)
set +e
python3 scripts/verify_phase12_full_flow_run.py "$negative_run" >"$out" 2>&1
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  echo "EXPECTED_FAILURE_MISSING: symlink boundary scan" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
if ! grep -q E_PHASE12_RUN_REF "$out"; then
  echo "EXPECTED_ERROR_CODE_MISSING expected=E_PHASE12_RUN_REF symlink boundary scan" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
if grep -q E_PHASE12_DOC_BOUNDARY "$out"; then
  echo "BOUNDARY_SCAN_FOLLOWED_SYMLINK" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
rm -f "$out"
echo NEGATIVE_PHASE12_BOUNDARY_SYMLINK_NO_READ_OK

make_negative_run absolute-backflow-ref
external_backflow=$(mktemp)
printf '{not-json: external sentinel}\n' > "$external_backflow"
cleanup_files+=("$external_backflow")
python3 - "$negative_run/backflow_ledger.jsonl" "$external_backflow" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); external=Path(sys.argv[2]).resolve().as_posix()
events=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
events[0]['finding_ref']=external
events[1]['source_finding_ref']=external
events[3]['source_finding_ref']=external
p.write_text(''.join(json.dumps(e, ensure_ascii=False, sort_keys=True)+'\n' for e in events))
PY
out=$(mktemp)
set +e
python3 scripts/verify_phase12_full_flow_run.py "$negative_run" >"$out" 2>&1
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  echo "EXPECTED_FAILURE_MISSING: absolute backflow ref" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
if ! grep -q E_PHASE12_BACKFLOW_CHAIN "$out"; then
  echo "EXPECTED_ERROR_CODE_MISSING expected=E_PHASE12_BACKFLOW_CHAIN absolute backflow ref" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
if grep -q E_PHASE12_JSON_PARSE "$out"; then
  echo "BACKFLOW_VALIDATOR_READ_UNSAFE_ABSOLUTE_REF" >&2
  cat "$out" >&2
  rm -f "$out"
  exit 1
fi
rm -f "$out"
echo NEGATIVE_PHASE12_ABSOLUTE_BACKFLOW_REF_NO_READ_OK

python3 -m compileall -q scripts
python3 scripts/verify_plugin_surface.py

# Phase10 inherited gate contains its own clean-worktree assertion; remove
# Phase12 negative fixtures before invoking it so only real repository diffs
# can trip that assertion.
cleanup
cleanup_paths=()
bash scripts/verify_phase10_real_run_readiness.sh

git diff --check -- .
if [[ -n "$(git status --short -- .)" ]]; then
  echo "PHASE12_WORKTREE_NOT_CLEAN" >&2
  git status --short -- . >&2
  exit 1
fi

echo PHASE12_FORMAL_FULL_FLOW_VERIFY_OK
