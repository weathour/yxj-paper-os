#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

run_root="$repo_root/runs/security-state-aware-mixed-platoon/phase13-live-subagent-full-flow-pilot"
cleanup() {
  find "$repo_root/runs" -maxdepth 1 -type d \( \
    -name '.phase13-negative-*' -o -name '.phase13-negative.*' \
  \) -exec rm -rf -- {} +
}
cleanup
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

make_negative_run() {
  local label=$1
  local dst
  dst=$(mktemp -d "$repo_root/runs/.phase13-negative-${label}.XXXXXX")
  rm -rf -- "$dst"
  cp -a "$run_root" "$dst"
  printf '%s\n' "$dst"
}

scaffold_probe=$(mktemp -d "$repo_root/runs/.phase13-negative-scaffold-check.XXXXXX")
rm -rf -- "$scaffold_probe"
python3 scripts/generate_phase13_live_pilot.py --run-root "$scaffold_probe" --check >/tmp/phase13-scaffold-check.out
if ! grep -q PHASE13_LIVE_PILOT_SCAFFOLD_GENERATED /tmp/phase13-scaffold-check.out; then
  cat /tmp/phase13-scaffold-check.out >&2
  exit 1
fi
python3 scripts/ingest_phase13_live_pilot.py
python3 scripts/verify_phase13_live_subagent_pilot.py

negative_run=$(make_negative_run missing-producer)
rm -f "$negative_run/returns/producer/S02.producer-return.md"
assert_fails_with E_PHASE13_PRODUCER_RETURN_MISSING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_MISSING_PRODUCER_OK

negative_run=$(make_negative_run missing-verifier)
rm -f "$negative_run/returns/verifier/S02.verifier-return.md"
assert_fails_with E_PHASE13_VERIFIER_RETURN_MISSING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_MISSING_VERIFIER_OK

negative_run=$(make_negative_run duplicate-thread)
python3 - "$negative_run/subagent_threads.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['threads'][1]['thread_id']=data['threads'][0]['thread_id']
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_THREAD_GLOBAL_DUPLICATE python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_THREAD_GLOBAL_DUPLICATE_OK

negative_run=$(make_negative_run thread-coverage)
python3 - "$negative_run/subagent_threads.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
replacement=None
kept=[]
for row in data['threads']:
    if row['stage_id'] == 'S02' and row['lane'] == 'producer':
        replacement=dict(row)
        continue
    kept.append(row)
if replacement is None:
    raise SystemExit('S02 producer row missing before mutation')
replacement['lane']='extra'
replacement['thread_id']='phase13-invalid-extra-thread'
kept.append(replacement)
data['threads']=kept
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_THREAD_COVERAGE python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_THREAD_COVERAGE_OK

negative_run=$(make_negative_run weak-generic)
printf 'Stage: S02\nPacket citation: packets/producer/S02.producer-packet.json\nlooks good\n' > "$negative_run/returns/producer/S02.producer-return.md"
python3 scripts/ingest_phase13_live_pilot.py "$negative_run" >/dev/null
assert_fails_with E_PHASE13_WEAK_GENERIC_RETURN python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_WEAK_GENERIC_RETURN_OK

negative_run=$(make_negative_run packet-citation)
python3 - "$negative_run/returns/producer/S02.producer-return.md" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1])
text=p.read_text().replace('packets/producer/S02.producer-packet.json','packets/producer/WRONG.json')
p.write_text(text)
PY
python3 scripts/ingest_phase13_live_pilot.py "$negative_run" >/dev/null
assert_fails_with E_PHASE13_PACKET_CITATION_MISSING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_PACKET_CITATION_MISSING_OK

negative_run=$(make_negative_run verifier-parroting)
cp "$negative_run/returns/producer/S02.producer-return.md" "$negative_run/returns/verifier/S02.verifier-return.md"
python3 scripts/ingest_phase13_live_pilot.py "$negative_run" >/dev/null
assert_fails_with E_PHASE13_VERIFIER_PARROTING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_VERIFIER_PARROTING_OK

negative_run=$(make_negative_run worker-misuse)
python3 - "$negative_run/subagent_threads.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['threads'][0]['agent_type']='worker'
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_WORKER_ROLE_MISUSE python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_WORKER_ROLE_MISUSE_OK

negative_run=$(make_negative_run agent-type-mismatch)
python3 - "$negative_run/subagent_threads.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
for row in data['threads']:
    if row['stage_id'] == 'S02' and row['lane'] == 'producer':
        row['agent_type']='analyst'
        break
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_AGENT_TYPE_MISMATCH python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_AGENT_TYPE_MISMATCH_OK

negative_run=$(make_negative_run authority-mode)
python3 - "$negative_run/stage_effects/S09A.effect.json" "$negative_run/packets/producer/S09A.producer-packet.json" "$negative_run/packets/verifier/S09A.verifier-packet.json" <<'PY'
import json, sys
from pathlib import Path
for arg in sys.argv[1:]:
    p=Path(arg); data=json.loads(p.read_text()); data['authority_mode']='production_candidate'; p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_AUTHORITY_MODE python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_AUTHORITY_MODE_OK

negative_run=$(make_negative_run verifier-grounding)
python3 - "$negative_run/packets/verifier/S02.verifier-packet.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['producer_return_sha256']='0'*64
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_VERIFIER_GROUNDING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_VERIFIER_GROUNDING_OK

negative_run=$(make_negative_run dispatch-ledger-missing)
rm -f "$negative_run/dispatch_ledger.jsonl"
assert_fails_with E_PHASE13_LEDGER_MISSING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_DISPATCH_LEDGER_MISSING_OK

negative_run=$(make_negative_run dispatch-ledger-tamper)
python3 - "$negative_run/dispatch_ledger.jsonl" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
rows=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
rows[0]['packet_sha256']='0'*64
rows[0]['agent_type']='verifier'
p.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True)+'\n' for row in rows))
PY
assert_fails_with E_PHASE13_LEDGER_CONTENT python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_DISPATCH_LEDGER_TAMPER_OK

negative_run=$(make_negative_run dispatch-authority-mode)
python3 - "$negative_run/dispatch/producer/S00.producer-dispatch.json" "$negative_run/dispatch_ledger.jsonl" <<'PY'
import json, sys
from pathlib import Path
dispatch_path=Path(sys.argv[1]); ledger_path=Path(sys.argv[2])
dispatch=json.loads(dispatch_path.read_text())
dispatch['authority_mode']='production_candidate'
dispatch_path.write_text(json.dumps(dispatch, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
rows=[json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
for row in rows:
    if row.get('event_id') == dispatch['event_id']:
        row['authority_mode']='production_candidate'
ledger_path.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True)+'\n' for row in rows))
PY
assert_fails_with E_PHASE13_AUTHORITY_MODE python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_DISPATCH_AUTHORITY_MODE_OK

negative_run=$(make_negative_run validation-ledger-missing)
rm -f "$negative_run/validation_ledger.jsonl"
assert_fails_with E_PHASE13_LEDGER_MISSING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_VALIDATION_LEDGER_MISSING_OK

negative_run=$(make_negative_run validation-ledger-tamper)
python3 - "$negative_run/validation_ledger.jsonl" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
rows=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
rows[0]['verdict']='reject'
p.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True)+'\n' for row in rows))
PY
assert_fails_with E_PHASE13_LEDGER_CONTENT python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_VALIDATION_LEDGER_TAMPER_OK

negative_run=$(make_negative_run raw-verifier-verdict-tamper)
python3 - "$negative_run/stage_effects/S02.effect.json" "$negative_run/validation/S02.live-validation.json" "$negative_run/validation_ledger.jsonl" <<'PY'
import json, sys
from pathlib import Path
effect_path=Path(sys.argv[1])
validation_path=Path(sys.argv[2])
ledger_path=Path(sys.argv[3])
effect=json.loads(effect_path.read_text())
validation=json.loads(validation_path.read_text())
effect['verifier_verdict']='accept'
effect['controller_acceptance']='accept'
validation['verifier_verdict']='accept'
validation['status']='pass'
effect_path.write_text(json.dumps(effect, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
rows=[json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
for row in rows:
    if row.get('stage_id') == 'S02':
        row['verdict']='accept'
ledger_path.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True)+'\n' for row in rows))
PY
assert_fails_with E_PHASE13_RAW_VERDICT_MISMATCH python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_RAW_VERIFIER_VERDICT_TAMPER_OK

negative_run=$(make_negative_run validation-status)
python3 - "$negative_run/validation/S02.live-validation.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['status']='needs_controller_repair'
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_VALIDATION_STATUS python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_VALIDATION_STATUS_OK

negative_run=$(make_negative_run effect-controller-acceptance)
python3 - "$negative_run/stage_effects/S02.effect.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
data['controller_acceptance']='reject'
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_EFFECT_RECORD python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_EFFECT_CONTROLLER_ACCEPTANCE_OK

negative_run=$(make_negative_run dispatch-record-missing)
rm -f "$negative_run/dispatch/producer/S02.producer-dispatch.json"
assert_fails_with E_PHASE13_DISPATCH_MISSING python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_DISPATCH_RECORD_MISSING_OK

negative_run=$(make_negative_run unauthorized-route)
printf '\nunauthorized recursive route activated as active route\n' >> "$negative_run/returns/producer/S02.producer-return.md"
assert_fails_with E_PHASE13_UNAUTHORIZED_ROUTE python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_UNAUTHORIZED_ROUTE_OK

negative_run=$(make_negative_run recursive-claim)
printf '\nI will dispatch additional agents and mark final completion.\n' >> "$negative_run/returns/producer/S02.producer-return.md"
assert_fails_with E_PHASE13_RECURSIVE_ORCHESTRATION_CLAIM python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_RECURSIVE_ORCHESTRATION_OK

negative_run=$(make_negative_run reject)
python3 - "$negative_run/stage_effects/S02.effect.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text()); data['verifier_verdict']='reject'; data['controller_acceptance']='reject'; p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_STAGE_REJECTED python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_STAGE_REJECTED_OK

negative_run=$(make_negative_run repair-unresolved)
python3 - "$negative_run/stage_effects/S02.effect.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text()); data['verifier_verdict']='needs_repair'; data['repair_required']=True; data['repair_ref']=None; p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_REPAIR_UNRESOLVED python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_REPAIR_UNRESOLVED_OK

negative_run=$(make_negative_run snapshot-drift)
python3 - "$negative_run/source_snapshot.after.json" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); data=json.loads(p.read_text())
entries=data['entries']; key=next(k for k,v in entries.items() if isinstance(v,dict) and v.get('kind')=='file' and 'sha256' in v)
entries[key]=dict(entries[key]); entries[key]['sha256']='2'*64
p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
PY
assert_fails_with E_PHASE13_SOURCE_SNAPSHOT_DRIFT python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_SOURCE_SNAPSHOT_DRIFT_OK

negative_run=$(make_negative_run source-runtime-artifact)
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
assert_fails_with E_PHASE13_SOURCE_RUNTIME_ARTIFACT python3 scripts/verify_phase13_live_subagent_pilot.py "$negative_run"
echo NEGATIVE_PHASE13_SOURCE_RUNTIME_ARTIFACT_OK

cleanup
python3 -m compileall -q scripts
python3 scripts/verify_plugin_surface.py
bash scripts/verify_phase12_formal_full_flow.sh

git diff --check -- .
if [[ -n "$(git status --short -- .)" ]]; then
  echo "PHASE13_WORKTREE_NOT_CLEAN" >&2
  git status --short -- . >&2
  exit 1
fi

echo PHASE13_LIVE_SUBAGENT_PILOT_VERIFY_OK
