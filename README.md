# yxj-paper-os

A standard Codex plugin scaffold for rebuilding `yxj-paper-os` from a clean branch.

## Branch philosophy

- [`docs/BRANCH_PHILOSOPHY.md`](docs/BRANCH_PHILOSOPHY.md) — current clean-rewrite philosophy, target paper-planning architecture, and external skill/repository inventory.

## Structure

- `.codex-plugin/plugin.json` — plugin manifest
- `skills/` — plugin skills
- `scripts/` — repo-local helper scripts
- `assets/` — optional plugin assets
- `references/` — pinned external reference repositories as Git submodules

## External references

- [`references/README.md`](references/README.md) documents the external reference submodules used for traffic/computer-science paper-planning rebuild work.

## Validation

```bash
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```
