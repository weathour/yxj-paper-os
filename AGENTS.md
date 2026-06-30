# AGENTS.md — yxj-paper-os

This repository is the active `yxj-paper-os` plugin, implemented as a Codex-native paper production graph runtime.

## Operating model

Use **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**.

Use the PPG runtime as the only active control model. Route labels are metadata only and cannot own completion.

## Current goal

Maintain and operate the installed, documented, testable `yxj-paper-os` PPG runtime for paper production management:

1. graph topology;
2. front-end visualization contract;
3. material schemas;
4. runtime protocol;
5. local backflow protocol;
6. validation and closed-loop testing;
7. later human handoff and front-end upgrades.

## Constraints

- Use controller-owned graph state, validators, TaskPackets, and local backflow as the runtime authority.
- Plugin install/cachebuster updates are allowed only as explicit lifecycle operations; publication/submission claims remain owner-gated.
- Prefer docs, schemas, examples, and local validators first.
- No new dependencies unless explicitly requested.
- Keep each change small, reviewable, and backed by validation.

## Verification

Run:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

