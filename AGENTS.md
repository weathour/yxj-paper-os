# AGENTS.md — yxj-paper-ppg-runtime

This repository develops a Codex-native paper production graph runtime.

## Operating model

Use **Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch**.

Do not revive the department-self-loop model. Departments may appear only as metadata labels or ownership tags; they must not become autonomous self-certifying loops.

## Current goal

Create a documented, testable plugin design for paper production management:

1. graph topology;
2. front-end visualization contract;
3. material schemas;
4. runtime protocol;
5. local backflow protocol;
6. validation and closed-loop testing;
7. later human handoff and front-end upgrades.

## Constraints

- Do not mutate or install the existing `yxj-paper-os` plugin from this repository.
- Do not publish, marketplace-register, or enable live plugin behavior without explicit user authorization.
- Prefer docs, schemas, examples, and local validators first.
- No new dependencies unless explicitly requested.
- Keep each change small, reviewable, and backed by validation.

## Verification

Run:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

