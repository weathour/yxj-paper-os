---
name: yxj-paper-execute
description: "Directly execute yxj-paper-os task packets through the approved native_subagent_pipeline_adapter. Use when compiling, dispatching, collecting, validating, ingesting, and transitioning bounded native subagent paper tasks without treating dispatch as completion."
---


# yxj-paper-execute

Operate the approved `native_subagent_pipeline_adapter`.

## Execution loop

1. Compile a task packet with `agent_type`, scoped context, expected output artifacts, collection path, state-ledger path, and `validator_refs`.
2. Execute through a Codex native subagent with the declared `agent_type`, or through an explicitly approved OMX Team run.
3. Collect output into `collection_path`.
4. Run validators referenced by `validator_refs`.
5. Ingest validated artifacts into the state/artifact/evidence/review ledgers.
6. Transition state only after ingestion evidence exists.
7. Run `../yxj-paper-index/scripts/ledger_guard.py check --root <paper-root>`; if `.omx/` is ignored, run `snapshot` and require a fresh snapshot before the final completion claim.

Read `references/runtime-execution-contract.md`, `references/agent-contract.md`, `references/agent-lane-registry.yaml`, and `references/production-lane-expectations.md` before implementing runtime behavior. Use `../yxj-paper-index/scripts/validate_fixture.py` for task-ledger checks.


## Managed-agent pressure protocol

Every compiled task packet should include `pua_telemetry` and every native
subagent prompt should include `[PUA-DIAGNOSIS]`. If an LLM agent fails twice,
repeats the same approach, guesses without source/state checks, waits passively,
or claims completion without validation, the execution coordinator escalates
L1-L4 and requires `[PUA-REPORT]` at L2+. The report is collected as control
evidence but does not replace `validator_refs` or validator evidence.
