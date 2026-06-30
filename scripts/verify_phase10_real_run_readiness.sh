#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

cleanup_paths=()
cleanup() {
  for path in "${cleanup_paths[@]:-}"; do
    if [[ "$path" == "$repo_root/runs/.phase10-negative-"* || "$path" == "$repo_root/runs/.phase10-negative."* ]]; then
      rm -rf -- "$path"
    fi
  done
}
trap cleanup EXIT

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

python3 scripts/verify_phase10_forbidden_side_effects.py
python3 scripts/verify_stage_contracts.py
python3 scripts/generate_local_paper_full_pilot.py --pilot-root examples/local-paper/security-state-aware-mixed-platoon --check
python3 scripts/generate_phase10_run_dry_run.py --check
python3 scripts/verify_phase10_run_readiness.py
bash scripts/verify_phase9_full_stage_runtime.sh
bash scripts/verify_phase8_plugin_surface.sh
python3 scripts/run_fixture_suite.py examples/runtime/overclaim-loop.v1.json
bash scripts/verify_phase6_task_packets.sh
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /home/weathour/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-ppg-runtime
python3 -m py_compile scripts/*.py

# Negative: content validator with too few dimensions must fail.
python3 - <<'PY'
import copy, sys
sys.path.insert(0, 'scripts')
from verify_phase10_run_readiness import REGISTRY, VALIDATORS, load_json, verify_validator_registry
registry = load_json(REGISTRY)
validators = copy.deepcopy(load_json(VALIDATORS))
validators['validators'][0]['dimensions'] = validators['validators'][0]['dimensions'][:1]
errors = verify_validator_registry(registry, validators)
if not any('E_PHASE10_VALIDATOR_DIMENSIONS' in error for error in errors):
    raise SystemExit(f'NEGATIVE_VALIDATOR_DIMENSIONS_MISSING: {errors}')
print('NEGATIVE_PHASE10_VALIDATOR_DIMENSIONS_OK')
PY

# Negative: bare S09 injected into a run fixture must fail.
negative_bare=$(mktemp -d "$repo_root/runs/.phase10-negative-bare-s09.XXXXXX")
cleanup_paths+=("$negative_bare")
cp -a runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/. "$negative_bare/"
python3 - "$negative_bare/run_state.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['canonical_stage_ids'][0] = 'S09'
data['stages'][0]['stage_id'] = 'S09'
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_BARE_S09 python3 scripts/verify_phase10_run_readiness.py "$negative_bare"

# Negative: source snapshot drift inside a pre-existing untracked source path must fail.
negative_source=$(mktemp -d "$repo_root/runs/.phase10-negative-source-drift.XXXXXX")
cleanup_paths+=("$negative_source")
cp -a runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/. "$negative_source/"
python3 - "$negative_source/manifest.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
entries = data['source_snapshot_after']['entries']
target = 'docs/runtime-viewer/index.html' if 'docs/runtime-viewer/index.html' in entries else sorted(entries)[0]
entries[target] = dict(entries[target])
entries[target]['sha256'] = '0' * 64
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_SOURCE_SNAPSHOT_DRIFT python3 scripts/verify_phase10_run_readiness.py "$negative_source"

# Negative: source-contained run output must be rejected before writes.
source_root=$(python3 - <<'PY'
import json
print(json.load(open('examples/local-paper/security-state-aware-mixed-platoon/manifest.json'))['source_root'])
PY
)
forbidden_source_run="$source_root/phase10-forbidden-run"
rm -rf -- "$forbidden_source_run"
assert_fails_with PHASE10_DRY_RUN_GENERATE_INVALID python3 scripts/generate_phase10_run_dry_run.py --run-root "$forbidden_source_run"
test ! -e "$forbidden_source_run"

# Negative: symlink run root must be rejected.
negative_symlink=$(mktemp -u "$repo_root/runs/.phase10-negative-symlink.XXXXXX")
cleanup_paths+=("$negative_symlink")
ln -s "$source_root" "$negative_symlink"
assert_fails_with PHASE10_DRY_RUN_GENERATE_INVALID python3 scripts/generate_phase10_run_dry_run.py --run-root "$negative_symlink"

# Negative: final/submission overclaim must fail.
negative_overclaim=$(mktemp -d "$repo_root/runs/.phase10-negative-overclaim.XXXXXX")
cleanup_paths+=("$negative_overclaim")
cp -a runs/security-state-aware-mixed-platoon/phase10-readiness-dry-run/. "$negative_overclaim/"
python3 - "$negative_overclaim/run_state.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['completion_boundary'] = 'ready to submit final manuscript complete'
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_COMPLETION_OVERCLAIM python3 scripts/verify_phase10_run_readiness.py "$negative_overclaim"

# Negative: misleading success marker with nonzero exit must not pass.
set +e
misleading=$(bash -c 'echo PHASE10_REAL_RUN_READINESS_VERIFY_OK; exit 7' 2>&1)
misleading_rc=$?
set -e
if [[ $misleading_rc -eq 0 ]]; then
  echo "MISLEADING_SUCCESS_EXIT_NOT_DETECTED" >&2
  echo "$misleading" >&2
  exit 1
fi

cleanup
cleanup_paths=()

git diff --check -- .
if [[ -n "$(git status --short -- .)" ]]; then
  echo "PHASE10_WORKTREE_NOT_CLEAN" >&2
  git status --short -- . >&2
  exit 1
fi

echo PHASE10_REAL_RUN_READINESS_VERIFY_OK
