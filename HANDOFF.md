# yxj-paper-os Handoff

Status: clean rewrite branch baseline.

## Current branch

`yxj-paper-os-slot-skill-redesign`

This branch intentionally deletes the old Paper Production Graph runtime and
restarts `yxj-paper-os` as a standard Codex plugin scaffold.

## Current architecture

```text
yxj-paper-os/
  .codex-plugin/
    plugin.json        # Codex plugin manifest
  skills/
    yxj-paper-os/
      SKILL.md         # single public plugin skill, currently scaffold-only
  scripts/
    .gitkeep           # placeholder for future repo-local helper scripts
  assets/
    .gitkeep           # placeholder for future plugin assets
  README.md            # minimal scaffold documentation
  HANDOFF.md           # current architecture and branch handoff
  .gitignore
```

The plugin currently exposes one skill:

- `yxj-paper-os`: a clean scaffold skill for rebuilding the paper-planning
  workflow incrementally.

No old runtime behavior is currently present in this branch. In particular, this
branch does not currently provide:

- Paper Production Graph runtime;
- S00-S16/G01/G02 stage registry;
- validators, schemas, examples, runtime viewer, or LaTeX writeback;
- manuscript drafting, figure production, citation lookup, reviewer simulation,
  formatting, submission, upload, publication, or acceptance claims.

## Validation

Use the plugin-creator validator as the baseline check:

```bash
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Expected output:

```text
Plugin validation passed: /home/weathour/plugins/yxj-paper-os
```

## Branch and version-management method

- `main`: preserve the old implementation/history unless explicitly replaced
  by a reviewed merge.
- `yxj-paper-os-slot-skill-redesign`: active clean rewrite branch.
- Commit policy: small commits that keep the plugin valid after each step.
- Version policy:
  - keep `.codex-plugin/plugin.json` at `0.1.0` while the scaffold is being
    rebuilt;
  - bump patch versions for validated internal scaffold additions;
  - bump minor version when a user-facing skill or stable workspace contract is
    added;
  - do not claim production paper behavior until it is implemented and
    owner-gated.
- Migration policy: rebuild forward from this scaffold; recover old material
  from `main` or Git history only when deliberately reintroduced.

## Recommended next steps

1. Add Markdown slot templates for the new paper-planning workflow.
2. Add a dependency-free template validator.
3. Add `yxj-paper-init` as the first real native skill.
4. Add one minimal example workspace.
5. Expand only after the plugin validator and any new local validators pass.
