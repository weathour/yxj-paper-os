#!/usr/bin/env bash
set -euo pipefail

python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/phase6-intro-packet.yaml
python3 scripts/validate_packet.py /tmp/phase6-intro-packet.yaml
cmp /tmp/phase6-intro-packet.yaml examples/packets/intro_writing_packet.v2.yaml

python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target claim_boundary_map_candidate_v3 \
  --out /tmp/phase6-claim-repair-packet.yaml
python3 scripts/validate_packet.py /tmp/phase6-claim-repair-packet.yaml
cmp /tmp/phase6-claim-repair-packet.yaml examples/packets/claim_repair_packet.v1.yaml

set +e
python3 scripts/validate_packet.py examples/packets/invalid-missing-allowed-read-paths.yaml > /tmp/pkt-read.out 2>&1; rc_read=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-allowed-write-paths.yaml > /tmp/pkt-write.out 2>&1; rc_write=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-output-path.yaml > /tmp/pkt-output.out 2>&1; rc_output=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-evidence-anchors.yaml > /tmp/pkt-evidence.out 2>&1; rc_evidence=$?
python3 scripts/validate_packet.py examples/packets/invalid-completion-forbidden-false.yaml > /tmp/pkt-completion.out 2>&1; rc_completion=$?
python3 scripts/validate_packet.py examples/packets/invalid-recursive-orchestration-false.yaml > /tmp/pkt-recursive.out 2>&1; rc_recursive=$?
python3 scripts/validate_packet.py examples/packets/invalid-output-outside-allowed-writes.yaml > /tmp/pkt-outside.out 2>&1; rc_outside=$?
python3 scripts/validate_packet.py examples/packets/invalid-owner-gate-required-true.yaml > /tmp/pkt-owner-true.out 2>&1; rc_owner_true=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-owner-gate-required.yaml > /tmp/pkt-owner-missing.out 2>&1; rc_owner_missing=$?
python3 scripts/validate_packet.py examples/packets/invalid-broad-allowed-read-path.yaml > /tmp/pkt-broad-read.out 2>&1; rc_broad_read=$?
python3 scripts/validate_packet.py examples/packets/invalid-broad-allowed-write-path.yaml > /tmp/pkt-broad-write.out 2>&1; rc_broad_write=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-worker-boot-clause.yaml > /tmp/pkt-boot-missing.out 2>&1; rc_boot_missing=$?
python3 scripts/validate_packet.py examples/packets/invalid-weak-worker-boot-clause.yaml > /tmp/pkt-boot-weak.out 2>&1; rc_boot_weak=$?
python3 scripts/validate_packet.py examples/packets/invalid-output-traversal.yaml > /tmp/pkt-traversal.out 2>&1; rc_pkt_traversal=$?
python3 scripts/validate_packet.py examples/packets/invalid-allowed-write-traversal.yaml > /tmp/pkt-write-traversal.out 2>&1; rc_pkt_write_traversal=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-forbidden-route.yaml > /tmp/pkt-blocked-route.out 2>&1; rc_pkt_forbidden_route=$?
python3 scripts/validate_packet.py examples/packets/invalid-unsafe-allowed-action.yaml > /tmp/pkt-action.out 2>&1; rc_pkt_action=$?
python3 scripts/validate_packet.py examples/packets/invalid-unsafe-allowed-tool.yaml > /tmp/pkt-tool.out 2>&1; rc_pkt_tool=$?
python3 scripts/validate_packet.py examples/packets/invalid-broad-material-read-dir.yaml > /tmp/pkt-broad-material-read.out 2>&1; rc_pkt_broad_material_read=$?
python3 scripts/validate_packet.py examples/packets/invalid-broad-candidate-write-dir.yaml > /tmp/pkt-broad-candidate-write.out 2>&1; rc_pkt_broad_candidate_write=$?
python3 scripts/validate_packet.py examples/packets/invalid-tilde-read-path.yaml > /tmp/pkt-tilde-read.out 2>&1; rc_pkt_tilde_read=$?
python3 scripts/validate_packet.py examples/packets/invalid-drive-write-path.yaml > /tmp/pkt-drive-write.out 2>&1; rc_pkt_drive_write=$?
python3 scripts/validate_packet.py examples/packets/invalid-duplicate-none-tool.yaml > /tmp/pkt-dupe-tool.out 2>&1; rc_pkt_dupe_tool=$?
python3 scripts/validate_packet.py examples/packets/invalid-status-committed.yaml > /tmp/pkt-status.out 2>&1; rc_pkt_status=$?
python3 scripts/validate_packet.py examples/packets/invalid-unknown-field.yaml > /tmp/pkt-unknown.out 2>&1; rc_pkt_unknown=$?
python3 scripts/validate_packet.py examples/packets/invalid-missing-safe-action.yaml > /tmp/pkt-missing-action.out 2>&1; rc_pkt_missing_action=$?
set -e
test $rc_read -ne 0 && grep -q E_TASK_ALLOWED_READ_PATHS_REQUIRED /tmp/pkt-read.out
test $rc_write -ne 0 && grep -q E_TASK_ALLOWED_WRITE_PATHS_REQUIRED /tmp/pkt-write.out
test $rc_output -ne 0 && grep -q E_TASK_OUTPUT_PATH_REQUIRED /tmp/pkt-output.out
test $rc_evidence -ne 0 && grep -q E_TASK_EVIDENCE_ANCHORS_REQUIRED /tmp/pkt-evidence.out
test $rc_completion -ne 0 && grep -q E_TASK_COMPLETION_FORBIDDEN_REQUIRED /tmp/pkt-completion.out
test $rc_recursive -ne 0 && grep -q E_TASK_NO_RECURSIVE_ORCHESTRATION_REQUIRED /tmp/pkt-recursive.out
test $rc_outside -ne 0 && grep -q E_TASK_OUTPUT_OUTSIDE_ALLOWED_WRITES /tmp/pkt-outside.out
test $rc_owner_true -ne 0 && grep -q E_TASK_OWNER_GATE_FORBIDDEN /tmp/pkt-owner-true.out
test $rc_owner_missing -ne 0 && grep -q E_TASK_OWNER_GATE_REQUIRED /tmp/pkt-owner-missing.out
test $rc_broad_read -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-broad-read.out
test $rc_broad_write -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-broad-write.out
test $rc_boot_missing -ne 0 && grep -q E_TASK_WORKER_BOOT_CLAUSE_REQUIRED /tmp/pkt-boot-missing.out
test $rc_boot_weak -ne 0 && grep -q E_TASK_WORKER_BOOT_CLAUSE_REQUIRED /tmp/pkt-boot-weak.out
test $rc_pkt_traversal -ne 0 && grep -q E_TASK_OUTPUT_OUTSIDE_ALLOWED_WRITES /tmp/pkt-traversal.out
test $rc_pkt_write_traversal -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-write-traversal.out
test $rc_pkt_forbidden_route -ne 0 && grep -q E_TASK_FORBIDDEN_ROUTES_REQUIRED /tmp/pkt-blocked-route.out
test $rc_pkt_action -ne 0 && grep -q E_TASK_ALLOWED_ACTIONS_REQUIRED /tmp/pkt-action.out
test $rc_pkt_tool -ne 0 && grep -q E_TASK_ALLOWED_TOOLS_REQUIRED /tmp/pkt-tool.out
test $rc_pkt_broad_material_read -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-broad-material-read.out
test $rc_pkt_broad_candidate_write -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-broad-candidate-write.out
test $rc_pkt_tilde_read -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-tilde-read.out
test $rc_pkt_drive_write -ne 0 && grep -q E_TASK_ALLOWED_PATH_TOO_BROAD /tmp/pkt-drive-write.out
test $rc_pkt_dupe_tool -ne 0 && grep -q E_TASK_ALLOWED_TOOLS_REQUIRED /tmp/pkt-dupe-tool.out
test $rc_pkt_status -ne 0 && grep -q E_TASK_STATUS_PLANNED_REQUIRED /tmp/pkt-status.out
test $rc_pkt_unknown -ne 0 && grep -q E_TASK_UNKNOWN_FIELD /tmp/pkt-unknown.out
test $rc_pkt_missing_action -ne 0 && grep -q E_TASK_ALLOWED_ACTIONS_REQUIRED /tmp/pkt-missing-action.out

python3 scripts/validate_missing_material_report.py examples/missing_material_reports/intro_missing_reader_spine.v1.yaml
set +e
python3 scripts/validate_missing_material_report.py examples/missing_material_reports/invalid-completion-forbidden-false.yaml > /tmp/missing-report-invalid.out 2>&1
rc_missing_report_invalid=$?
python3 scripts/validate_missing_material_report.py examples/missing_material_reports/invalid-unknown-field.yaml > /tmp/missing-report-unknown.out 2>&1
rc_missing_report_unknown=$?
set -e
test $rc_missing_report_invalid -ne 0
grep -q E_REPORT_COMPLETION_FORBIDDEN_REQUIRED /tmp/missing-report-invalid.out
test $rc_missing_report_unknown -ne 0
grep -q E_REPORT_UNKNOWN_FIELD /tmp/missing-report-unknown.out

rm -f /tmp/should-not-exist-packet.yaml /tmp/phase6-missing-report.yaml
set +e
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/phase6-missing-reader-spine.json \
  --target section_draft_intro.v2 \
  --out /tmp/should-not-exist-packet.yaml \
  --missing-report-out /tmp/phase6-missing-report.yaml > /tmp/phase6-missing-compile.out 2>&1
rc_missing_compile=$?
set -e
test $rc_missing_compile -ne 0
test ! -e /tmp/should-not-exist-packet.yaml
python3 scripts/validate_missing_material_report.py /tmp/phase6-missing-report.yaml

printf 'stale packet' > /tmp/preexisting-missing-packet.yaml
set +e
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/phase6-missing-reader-spine.json \
  --target section_draft_intro.v2 \
  --out /tmp/preexisting-missing-packet.yaml \
  --missing-report-out /tmp/preexisting-missing-report.yaml > /tmp/preexisting-missing.out 2>&1
rc_pre_missing=$?
set -e
test $rc_pre_missing -ne 0
test ! -e /tmp/preexisting-missing-packet.yaml
python3 scripts/validate_missing_material_report.py /tmp/preexisting-missing-report.yaml

printf 'stale report' > /tmp/preexisting-success-report.yaml
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/preexisting-success-packet.yaml \
  --missing-report-out /tmp/preexisting-success-report.yaml
test ! -e /tmp/preexisting-success-report.yaml

python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/intro_candidate_return.v1.yaml
set +e
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-graph-completion-claimed.yaml > /tmp/return-completion.out 2>&1; rc_return_completion=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-recursive-dispatch-requested.yaml > /tmp/return-recursive.out 2>&1; rc_return_recursive=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-writes-outside-allowed.yaml > /tmp/return-writes-flag.out 2>&1; rc_return_writes_flag=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-outside-path-despite-claim.yaml > /tmp/return-outside-path.out 2>&1; rc_return_outside_path=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-packet-id-mismatch.yaml > /tmp/return-packet-id.out 2>&1; rc_return_packet_id=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-missing-remaining-risks.yaml > /tmp/return-risk.out 2>&1; rc_return_risk=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-path-traversal-despite-prefix.yaml > /tmp/return-traversal.out 2>&1; rc_return_traversal=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-output-path-mismatch.yaml > /tmp/return-mismatch.out 2>&1; rc_return_mismatch=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-tilde-output-path.yaml > /tmp/return-tilde.out 2>&1; rc_return_tilde=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-drive-output-path.yaml > /tmp/return-drive.out 2>&1; rc_return_drive=$?
python3 scripts/validate_candidate_return.py --packet examples/packets/intro_writing_packet.v2.yaml examples/candidate_returns/invalid-unknown-field.yaml > /tmp/return-unknown.out 2>&1; rc_return_unknown=$?
set -e
test $rc_return_completion -ne 0 && grep -q E_RETURN_GRAPH_COMPLETION_FORBIDDEN /tmp/return-completion.out
test $rc_return_recursive -ne 0 && grep -q E_RETURN_RECURSIVE_DISPATCH_FORBIDDEN /tmp/return-recursive.out
test $rc_return_writes_flag -ne 0 && grep -q E_RETURN_WRITE_ESCAPE_FORBIDDEN /tmp/return-writes-flag.out
test $rc_return_outside_path -ne 0 && grep -q E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES /tmp/return-outside-path.out
test $rc_return_packet_id -ne 0 && grep -q E_RETURN_PACKET_ID_MISMATCH /tmp/return-packet-id.out
test $rc_return_risk -ne 0 && grep -q E_RETURN_REMAINING_RISKS_REQUIRED /tmp/return-risk.out
test $rc_return_traversal -ne 0 && grep -q E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES /tmp/return-traversal.out
test $rc_return_mismatch -ne 0 && grep -q E_RETURN_OUTPUT_PATH_MISMATCH /tmp/return-mismatch.out
test $rc_return_tilde -ne 0 && grep -q E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES /tmp/return-tilde.out
test $rc_return_drive -ne 0 && grep -q E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES /tmp/return-drive.out
test $rc_return_unknown -ne 0 && grep -q E_RETURN_UNKNOWN_FIELD /tmp/return-unknown.out

rm -f /tmp/unknown-packet.yaml
set +e
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target missing_target.v1 \
  --out /tmp/unknown-packet.yaml > /tmp/unknown-packet.out 2>&1
rc_unknown=$?
set -e
test $rc_unknown -ne 0
grep -q E_TASK_TARGET_UNSUPPORTED /tmp/unknown-packet.out
test ! -e /tmp/unknown-packet.yaml

printf 'stale packet' > /tmp/preexisting-unknown-packet.yaml
set +e
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target missing_target.v1 \
  --out /tmp/preexisting-unknown-packet.yaml > /tmp/preexisting-unknown.out 2>&1
rc_pre_unknown=$?
set -e
test $rc_pre_unknown -ne 0
grep -q E_TASK_TARGET_UNSUPPORTED /tmp/preexisting-unknown.out
test ! -e /tmp/preexisting-unknown-packet.yaml

python3 scripts/compile_backflow.py examples/review_findings/overclaim.v1.yaml \
  --graph examples/runtime/overclaim-loop.v1.json \
  --out /tmp/phase6-backflow-regression.yaml
python3 scripts/validate_backflow.py /tmp/phase6-backflow-regression.yaml
python3 scripts/propagate_stale.py examples/runtime/overclaim-loop.v1.json \
  --source claim_boundary_map.v2 \
  --out /tmp/phase6-stale-regression.json \
  --report /tmp/phase6-stale-regression.report.txt
python3 scripts/validate_graph.py /tmp/phase6-stale-regression.json
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v2.yaml
python3 scripts/validate_packet.py examples/packets/claim_repair_packet.v1.yaml
python3 -m py_compile scripts/*.py
ruff check scripts
pyright scripts
python3 -m json.tool schemas/ppg-task-packet.schema.json >/tmp/phase6-task-schema.json
python3 -m json.tool schemas/ppg-missing-material-report.schema.json >/tmp/phase6-missing-schema.json
python3 -m json.tool schemas/ppg-candidate-return.schema.json >/tmp/phase6-return-schema.json
python3 - <<'PY'
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from ppg_validate_common import load_document  # type: ignore  # noqa: E402

schema = json.loads(Path("schemas/ppg-candidate-return.schema.json").read_text(encoding="utf-8"))
pattern = schema["properties"]["output_artifact_path"]["pattern"]

positive, positive_errors = load_document(Path("examples/candidate_returns/intro_candidate_return.v1.yaml"))
if positive_errors:
    raise SystemExit(positive_errors)
assert isinstance(positive, dict)
assert re.fullmatch(pattern, str(positive["output_artifact_path"]))

negative_fixtures = [
    "examples/candidate_returns/invalid-path-traversal-despite-prefix.yaml",
    "examples/candidate_returns/invalid-tilde-output-path.yaml",
    "examples/candidate_returns/invalid-drive-output-path.yaml",
]
for fixture in negative_fixtures:
    data, errors = load_document(Path(fixture))
    if errors:
        raise SystemExit(errors)
    assert isinstance(data, dict)
    if re.fullmatch(pattern, str(data["output_artifact_path"])):
        raise SystemExit(f"schema pattern unexpectedly accepts {fixture}")

print("RETURN_SCHEMA_PATH_PATTERN_OK")
PY
git diff --check -- .

echo PHASE6_TASK_PACKET_VERIFY_OK
