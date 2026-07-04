# External Reference Repositories

This directory contains pinned shallow Git submodules used as reference material
while rebuilding `yxj-paper-os` as a traffic/computer-science paper-planning
Codex plugin.

These repositories are **references**, not runtime dependencies. The plugin must
not silently vendor, execute, or depend on them. When a future `yxj-paper-os`
skill hands off work to an external skill, it should do so through explicit
Markdown artifacts such as `WRITING_DESIGN_PACK.md`.

## Current submodules

| Local path | Upstream | Intended reference role |
|---|---|---|
| `references/external/nature-skills` | <https://github.com/Yuan1z0825/nature-skills> | Nature-style writing, polishing, figures, citation, review, response-letter workflow references |
| `references/external/research-paper-writing-skills` | <https://github.com/Master-cai/Research-Paper-Writing-Skills> | ML/CV/NLP paper-writing skill references, useful for computer-science and algorithm papers |
| `references/external/academic-research-skills-codex` | <https://github.com/Imbad0202/academic-research-skills-codex> | Codex-native academic research/write/review workflow references |
| `references/external/paperdebugger` | <https://github.com/PaperDebugger/paperdebugger> | In-editor review/revision and Overleaf-style feedback workflow reference |
| `references/external/pantheonos` | <https://github.com/aristoteleo/PantheonOS> | Multi-agent paper-writing and graph-maker team design reference; not a default runtime base |

## Clone / restore

After cloning this repository, initialize references with:

```bash
git submodule update --init --recursive --depth 1
```

If a local Git config rewrites GitHub HTTPS URLs to SSH and SSH is unavailable,
use:

```bash
GIT_CONFIG_GLOBAL=/dev/null git submodule update --init --recursive --depth 1
```

## Update policy

- Pin submodules by commit.
- Update one reference at a time.
- Record why the update is needed in the commit message.
- Do not copy third-party files from these references into plugin-owned skills
  unless license, source commit, and adaptation rationale are documented.
