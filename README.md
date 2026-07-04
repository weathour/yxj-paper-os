# yxj-paper-os

A standard Codex plugin scaffold for rebuilding `yxj-paper-os` from a clean branch.

## Branch philosophy

- [`docs/BRANCH_PHILOSOPHY.md`](docs/BRANCH_PHILOSOPHY.md) — current clean-rewrite philosophy, target paper-planning architecture, and external skill/repository inventory.

## Structure

- `.codex-plugin/plugin.json` — plugin manifest
- `skills/` — plugin skills
- `scripts/` — repo-local helper scripts
- `assets/` — optional plugin assets

## Validation

```bash
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```
