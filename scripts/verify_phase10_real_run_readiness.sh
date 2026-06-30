#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

cleanup_paths=()
negative_run=""
cleanup() {
  for path in "${cleanup_paths[@]:-}"; do
    if [[ "$path" == "$repo_root/runs/.phase10-negative-"* || "$path" == "$repo_root/runs/.phase10-negative."* ]]; then
      rm -rf -- "$path"
    fi
  done
}
trap cleanup EXIT

make_negative_run() {
  local label=$1
  negative_run=$(mktemp -d "$repo_root/runs/.phase10-negative-${label}.XXXXXX")
  cleanup_paths+=("$negative_run")
  python3 scripts/generate_phase10_run_dry_run.py --run-root "$negative_run" --check >/dev/null
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

python3 scripts/verify_phase10_forbidden_side_effects.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 - <<'PY'
import json
from pathlib import Path
stage_contract_required = set(json.loads(Path('schemas/ppg-stage-contract.schema.json').read_text())['required'])
run_state_required = set(json.loads(Path('schemas/ppg-run-state.schema.json').read_text())['required'])
if 'stage_local_overlays' not in stage_contract_required:
    raise SystemExit('PHASE11_STAGE_CONTRACT_SCHEMA_OVERLAY_REQUIRED_MISSING')
missing_run = {'stage_overlay_registry_ref', 'active_stage_overlays'} - run_state_required
if missing_run:
    raise SystemExit(f'PHASE11_RUN_STATE_SCHEMA_OVERLAY_REQUIRED_MISSING {sorted(missing_run)}')
print('PHASE11_SCHEMA_OVERLAY_REQUIRED_FIELDS_OK')
PY
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

# Negative: StageContract packet refs must reject symlinked packet files.
python3 - <<'PY'
import json
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')
from verify_stage_contracts import validate_contract

link = Path('examples/packets/.phase10-negative-symlink.yaml')
try:
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to('phase10_s02_sota_analysis_packet.v1.yaml')
    registry = json.load(open('runtime/stage_registry.json'))
    stage = next(item for item in registry['stages'] if item['stage_id'] == 'S02')
    contract = json.load(open('examples/stage-contracts/S02.stage-contract.json'))
    contract['worker_packet_coverage']['packet_ref'] = str(link)
    errors = validate_contract(contract, stage)
    if not any('E_STAGE_CONTRACT_PACKET_REF_SCOPE' in error for error in errors):
        raise SystemExit(f'NEGATIVE_PACKET_SYMLINK_MISSING: {errors}')
    print('NEGATIVE_PHASE10_PACKET_SYMLINK_SCOPE_OK')
finally:
    if link.exists() or link.is_symlink():
        link.unlink()
PY

# Negative: bare S09 injected into a run fixture must fail.
make_negative_run bare-s09
negative_bare=$negative_run
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

# Negative: run-state must keep Nature overlay registry linkage.
make_negative_run run-state-overlay
negative_run_state_overlay=$negative_run
python3 - "$negative_run_state_overlay/run_state.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data.pop('stage_overlay_registry_ref', None)
data.pop('active_stage_overlays', None)
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_STAGE_OVERLAY_LINK python3 scripts/verify_phase10_run_readiness.py "$negative_run_state_overlay"

# Negative: source snapshot drift inside a pre-existing untracked source path must fail.
make_negative_run source-drift
negative_source=$negative_run
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

source_root=$(python3 - <<'PY'
import json
print(json.load(open('examples/local-paper/security-state-aware-mixed-platoon/manifest.json'))['source_root'])
PY
)

# Negative: manifest source_root must remain bound to the pilot manifest source root.
make_negative_run wrong-source-root
negative_wrong_source_root=$negative_run
python3 - "$negative_wrong_source_root/manifest.json" "$source_root/docs" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['source_root'] = sys.argv[2]
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_SOURCE_ROOT python3 scripts/verify_phase10_run_readiness.py "$negative_wrong_source_root"

# Negative: dispatch content must keep source-read-only and worker authority boundaries.
make_negative_run dispatch
negative_dispatch=$negative_run
python3 - "$negative_dispatch/dispatch/S02.dispatch.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['source_read_only'] = False
data['worker_authority']['completion_forbidden'] = False
data['completion_claim'] = 'ready to submit final manuscript complete'
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_DISPATCH_CONTENT python3 scripts/verify_phase10_run_readiness.py "$negative_dispatch"

# Negative: validation records must match the stage content-validator registry.
make_negative_run validation
negative_validation=$negative_run
python3 - "$negative_validation/validation/S02.validation.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['dimension_count'] = 0
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_VALIDATION_CONTENT python3 scripts/verify_phase10_run_readiness.py "$negative_validation"

# Negative: dispatch records must keep Nature overlay linkage explicit.
make_negative_run stage-overlay-dispatch
negative_stage_overlay_dispatch=$negative_run
python3 - "$negative_stage_overlay_dispatch/dispatch/S02.dispatch.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data.pop('active_stage_overlays', None)
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_STAGE_OVERLAY_LINK python3 scripts/verify_phase10_run_readiness.py "$negative_stage_overlay_dispatch"

# Negative: candidate placeholders must not overclaim manuscript completion.
make_negative_run candidate
negative_candidate=$negative_run
python3 - "$negative_candidate/candidate-artifacts/S02.candidate-placeholder.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['completion_boundary'] = 'final manuscript complete'
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_COMPLETION_OVERCLAIM python3 scripts/verify_phase10_run_readiness.py "$negative_candidate"

# Negative: per-run TaskPackets must write only to the run-owned candidate artifact path.
make_negative_run run-packet
negative_run_packet=$negative_run
python3 - "$negative_run_packet/packets/S02.task-packet.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['output_artifact_path'] = 'examples/materials/phase10_s02_research_dossier.yaml'
data['allowed_write_paths'] = ['examples/materials/phase10_s02_research_dossier.yaml']
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_RUN_PACKET_OUTPUT_BOUNDARY python3 scripts/verify_phase10_run_readiness.py "$negative_run_packet"

# Negative: per-run TaskPackets must carry the Nature overlay clause and validator.
make_negative_run run-packet-overlay
negative_run_packet_overlay=$negative_run
python3 - "$negative_run_packet_overlay/packets/S02.task-packet.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data['mandatory_controls'].pop('nature_overlay_ref', None)
data['validators'] = [item for item in data.get('validators', []) if not str(item).startswith('stage_overlay:')]
p.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
PY
assert_fails_with E_PHASE10_STAGE_OVERLAY_LINK python3 scripts/verify_phase10_run_readiness.py "$negative_run_packet_overlay"

# Negative: source-contained run output must be rejected before writes.
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
make_negative_run overclaim
negative_overclaim=$negative_run
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
