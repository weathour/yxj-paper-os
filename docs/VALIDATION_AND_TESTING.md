# Validation and Testing Plan

## Validator categories

### Graph validators

- all edge endpoints exist;
- node ids are unique;
- committed manuscript artifacts have task packets;
- review findings have backflow targets;
- stale nodes list stale reasons;
- owner intent changes have owner evidence.

### Material validators

- envelope fields present;
- typed payload required fields present;
- source inputs exist;
- validators are declared;
- invalidation policy exists.

### Lifecycle validators

- every feedback package is routed before repair;
- every attribution names a canonical stage and responsible material;
- repair packets are scoped and cannot request recursive orchestration or completion authority;
- whole-manuscript rewrite is owner-gated;
- stage improvements require retrospective or repeated-failure evidence;
- retrospectives cannot claim submission/publication readiness;
- active contracts do not require external orchestrators or host-local Codex paths.

### Manuscript validators

- no internal code leakage in main prose;
- no raw internal constraints in rendered output;
- no bare citation keys in rendered output;
- claims obey evidence visibility limits;
- section units answer declared reader questions;
- terminology register is consumed.

### Backflow validators

- every finding has a failure type;
- every backflow task has a target node;
- stale propagation is scoped;
- unrelated downstream nodes remain unchanged;
- repaired nodes create new versions.

## Core commands

```bash
python3 scripts/verify_lifecycle_contract.py
python3 scripts/validate_material.py examples/materials/claim_boundary_map.v2.yaml
python3 scripts/validate_review_finding.py examples/review_findings/overclaim.v1.yaml
python3 scripts/validate_packet.py examples/packets/intro_writing_packet.v2.yaml
python3 scripts/validate_backflow.py examples/backflow_tasks/overclaim_repair.v1.yaml
python3 scripts/validate_delivery_gate.py examples/delivery/review_closure.pass.yaml
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```

## Local-paper projection

Standalone validation uses a repo-local sample paper workspace:

```bash
python3 scripts/import_local_paper_pilot.py \
  --source examples/sample-paper-workspace \
  --out examples/local-paper/sample-paper-workspace \
  --check
python3 scripts/generate_local_paper_full_pilot.py \
  --pilot-root examples/local-paper/sample-paper-workspace \
  --check
python3 scripts/verify_local_paper_full_pilot.py \
  examples/local-paper/sample-paper-workspace
```

A user’s private paper path may be imported as optional provenance when present, but it is not a standalone plugin acceptance dependency.

## Lifecycle fixture matrix

Positive:

- `examples/lifecycle/feedback_to_stage_improvement.valid.json`

Negative:

- `examples/lifecycle/invalid-unrouted-feedback.json`
- `examples/lifecycle/invalid-global-rewrite-repair.json`
- `examples/lifecycle/invalid-recursive-repair-authority.json`
- `examples/lifecycle/invalid-premature-stage-improvement.json`
- `examples/lifecycle/invalid-retrospective-submission-claim.json`
- `examples/lifecycle/invalid-active-omx-dependency.json`

Expected aggregate signal:

```text
PPG_LIFECYCLE_CONTRACT_OK
```
