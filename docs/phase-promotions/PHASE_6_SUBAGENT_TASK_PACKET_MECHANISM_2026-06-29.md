# Phase 6 Promotion — Subagent Task Packet Mechanism

Date: 2026-06-29

## Promoted state

Phase 6 is promoted as the first executable subagent-boundary layer of `yxj-paper-os`.

The runtime can now compile strict, bounded task packets from validated graph state and validate worker-style returns without trusting worker self-certification.

The promoted verifier is:

```bash
scripts/verify_phase6_task_packets.sh
```

## What changed

### Strict TaskPacket compiler

- Added `scripts/compile_task_packet.py`.
- Supported deterministic targets:
  - `section_draft_intro.v1`, `section_draft_intro.v2`, `intro_draft_v2` -> `intro_writing_packet_v2`;
  - `claim_boundary_map_candidate_v3`, `claim_boundary_repair.v1` -> `claim_repair_packet_v1`.
- Unknown targets fail with `E_TASK_TARGET_UNSUPPORTED` and write no packet.
- Missing graph materials fail with `E_TASK_MISSING_MATERIAL`; when requested, the compiler writes a valid `MissingMaterialReport` and no packet.
- Failed compiles clear a pre-existing `--out` file, so a stale packet cannot survive a blocked/unsupported compile.
- A pre-existing `--missing-report-out` sidecar is also cleared at compile start, including successful compiles that do not produce a missing report.
- Emitted packet/report YAML is round-trip loaded and validated before success is printed.

### Strict packet authority fields

`schemas/ppg-task-packet.schema.json` and `scripts/validate_packet.py` now require packet-level authority boundaries:

- `status: planned`;
- `allowed_read_paths`;
- `allowed_write_paths`;
- `output_artifact_path` inside the allowed write surface;
- `evidence_anchors`;
- `worker_boot_clause`;
- `completion_forbidden: true`;
- `no_recursive_orchestration: true`;
- `owner_gate_required: false`.
- exact required forbidden routes for no graph completion, no recursive dispatch, no outside writes, and no owner-intent mutation;
- exact canonical safe allowed actions only;
- `allowed_tools: [none]`;
- safe repo-relative paths with no absolute/root-like/traversal components.
- file-level read/write paths only: reads are limited to current Phase 6 fixture evidence surfaces, and writes must be the single exact output file under the candidate-artifact/material surfaces.
- no unknown TaskPacket fields.

The historical `examples/packets/intro_writing_packet.v1.yaml` remains a byte-preserved legacy fixture tied to stale `claim_boundary_map_v1`. Phase 6 strict evidence starts with `examples/packets/intro_writing_packet.v2.yaml` and `examples/packets/claim_repair_packet.v1.yaml`.

### Missing-material and candidate-return contracts

- Added `schemas/ppg-missing-material-report.schema.json` and `scripts/validate_missing_material_report.py`.
- Added `schemas/ppg-candidate-return.schema.json` and `scripts/validate_candidate_return.py`.
- Candidate returns are packet-aware: the validator compares `packet_id` and `output_artifact_path` against the originating packet. `writes_outside_allowed_paths: false` is not trusted if the path escapes the packet boundary.
- Candidate return `output_artifact_path` must equal the originating packet's `output_artifact_path`, not merely fit inside a broad write directory.
- Missing reports and candidate returns reject unknown fields.

## Evidence fixtures

Positive fixtures:

- `examples/packets/intro_writing_packet.v2.yaml`;
- `examples/packets/claim_repair_packet.v1.yaml`;
- `examples/runtime/phase6-missing-reader-spine.json`;
- `examples/missing_material_reports/intro_missing_reader_spine.v1.yaml`;
- `examples/candidate_returns/intro_candidate_return.v1.yaml`.

Negative fixture families:

- missing allowed read/write paths;
- missing output path;
- missing evidence anchors;
- completion/recursive-orchestration authority violations;
- owner-gate violations;
- broad path roots;
- weak/missing worker boot clause;
- path traversal in packet output or allowed writes;
- broad-but-lexically-valid read/write directories;
- home/drive-style path prefixes;
- missing required forbidden route;
- unsafe allowed action/tool;
- duplicate `none` tool entries;
- committed/candidate/stale packet status;
- unknown TaskPacket fields;
- missing canonical safe action;
- candidate return graph-completion claim;
- recursive dispatch request;
- write-escape self-certification;
- packet-aware outside-path escape;
- packet-id mismatch;
- output path mismatch;
- candidate return path traversal;
- candidate return home/drive-style path prefixes;
- unknown MissingMaterialReport / CandidateArtifactReturn fields;
- missing remaining risks.

## Verification commands

Primary Phase 6 checks:

```bash
python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target section_draft_intro.v1 \
  --out /tmp/phase6-intro-packet.yaml
python3 scripts/validate_packet.py /tmp/phase6-intro-packet.yaml
cmp /tmp/phase6-intro-packet.yaml examples/packets/intro_writing_packet.v2.yaml

git diff --exit-code -- examples/packets/intro_writing_packet.v1.yaml

python3 scripts/compile_task_packet.py \
  --graph examples/runtime/overclaim-loop.v1.json \
  --target claim_boundary_map_candidate_v3 \
  --out /tmp/phase6-claim-repair-packet.yaml
python3 scripts/validate_packet.py /tmp/phase6-claim-repair-packet.yaml
cmp /tmp/phase6-claim-repair-packet.yaml examples/packets/claim_repair_packet.v1.yaml

python3 scripts/validate_missing_material_report.py \
  examples/missing_material_reports/intro_missing_reader_spine.v1.yaml
python3 scripts/validate_candidate_return.py \
  --packet examples/packets/intro_writing_packet.v2.yaml \
  examples/candidate_returns/intro_candidate_return.v1.yaml
```

Regression suite:

```bash
scripts/verify_phase6_task_packets.sh
```

Expanded checks inside the script include:

```bash
python3 scripts/compile_backflow.py examples/review_findings/overclaim.v1.yaml \
  --graph examples/runtime/overclaim-loop.v1.json \
  --out /tmp/phase6-backflow-regression.yaml
python3 scripts/validate_backflow.py /tmp/phase6-backflow-regression.yaml
python3 scripts/propagate_stale.py examples/runtime/overclaim-loop.v1.json \
  --source claim_boundary_map.v2 \
  --out /tmp/phase6-stale-regression.json \
  --report /tmp/phase6-stale-regression.report.txt
python3 scripts/validate_graph.py /tmp/phase6-stale-regression.json
python3 -m py_compile scripts/*.py
ruff check scripts
pyright scripts
python3 -m json.tool schemas/ppg-task-packet.schema.json >/tmp/phase6-task-schema.json
python3 -m json.tool schemas/ppg-missing-material-report.schema.json >/tmp/phase6-missing-schema.json
python3 -m json.tool schemas/ppg-candidate-return.schema.json >/tmp/phase6-return-schema.json
git diff --check -- .
```

## Phase 6 limits

Phase 6 does **not** run a real writer/verifier subagent pilot. It does **not** commit candidate outputs to the graph. It does **not** update the frontend and does **not** revive legacy department-loop `$yxj-paper-os` behavior.

The next phase should use these strict packets for a single real subagent pilot and ingest only validator-backed candidate artifacts.
