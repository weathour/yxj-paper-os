# AGENTS.md — yxj-paper-os

This repository is the source of the standalone `yxj-paper-os` Codex plugin.

## Operating model

Use:

```text
Explicit Material Graph
  + Stage Accountability
  + Local Backpropagation
  + Run Retrospective Learning
  + Main-Agent Dispatch
```

The main Codex agent is the **Paper Production Graph Runtime Controller**.
Workers, scripts, validators, fixtures, and frontend panels may provide
candidates or evidence, but they do not own completion authority.

## Current goal

Maintain a clean plugin surface that helps a main agent manage an academic paper
from source materials to candidate manuscript integration:

1. read material authority and stage state;
2. compile bounded task packets;
3. validate candidate outputs;
4. route feedback to the nearest responsible stage/material;
5. create scoped repair/backflow packets;
6. mark downstream stale nodes and revalidate them;
7. after a full run, propose stage-prompt/task-packet/validator improvements
   from repeated feedback patterns.

## Standalone boundary

- Paper OS owns its stage registry, material authority, feedback lifecycle,
  validators, and run records.
- OMX or other orchestration systems may be used personally as optional
  adapters, but they are not public interfaces, dependencies, or authority
  sources for this plugin.
- Do not require user-home or machine-local validator paths.
- Publication, upload, submission, acceptance, and final-paper claims remain
  owner-gated.

## Constraints

- Prefer existing docs, schemas, examples, and local dependency-free validators.
- No new dependencies unless explicitly requested.
- Keep diffs small, reviewable, and backed by validation.
- Historical `phase*` names may remain only as internal fixture IDs or
  compatibility wrappers; public guidance should use Paper OS stage/lifecycle
  language (`S00-S16/G01/G02`, readiness run, formal full-flow fixture, live
  pilot scaffold).

## Verification

Run the standalone validation surface:

```bash
python3 scripts/verify_plugin_surface.py
python3 scripts/verify_lifecycle_contract.py
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```

For the portable sample paper projection:

```bash
python3 scripts/import_local_paper_pilot.py --check
python3 scripts/generate_local_paper_full_pilot.py --check
python3 scripts/verify_local_paper_full_pilot.py
```
