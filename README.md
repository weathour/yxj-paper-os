# yxj-paper-os

`yxj-paper-os` is a minimal Codex plugin for preparing traffic / computer-science / AI paper projects before manuscript drafting.

It does **not** write the manuscript. It guides Codex to collect missing upstream information, blocks when required information is unhandled, and produces a writing-design handoff for downstream writing modules.

## MVP architecture

```text
Single public skill
  + five internal playbooks
  + six Markdown workspace templates
  + one lightweight validator
```

The public surface is one skill:

```text
skills/yxj-paper-os/SKILL.md
```

The public paper workspace has exactly six files:

```text
paper_project/
  00_DIMENSION_INDEX.md
  00_PROJECT_ROUTE.md
  01_MATERIALS_INVENTORY.md
  02_CLAIM_EVIDENCE_BOUNDARY.md
  03_WRITING_STRUCTURE.md
  04_WRITING_DESIGN_PACK.md
```

`00_DIMENSION_INDEX.md` is the required public checklist for the 20 information dimensions. It records whether each dimension is filled, not applicable, absent, deferred, or rejected, with a reason and a pointer/handoff note.

`04_WRITING_DESIGN_PACK.md` is the handoff artifact for writing, figure, citation, polishing, or review tools.

## Guided intake model

The skill should feel like a lightweight guided form, not a runtime system. The agent first explains that it prepares six planning files and one writing design pack, then works through five user-facing phases:

```text
Route → Materials → Claim/Evidence → Writing Structure → Handoff
```

Internally, those phases are backed by the D00-D19 rubric and `00_DIMENSION_INDEX.md`. When information is missing, the agent should ask a short question card with options, consequences, and the file/D-row it will update. If an OMX question UI is available it may render the same card through `omx question`, but Markdown cards remain the standalone fallback.

## Native subagent acceleration

The skill may use native subagents as bounded accelerators, while the leader remains the single user-facing owner and final file writer. Recommended defaults are:

- `verifier` after inspect/init and after design-pack compilation;
- `explore` for local Materials scans when artifacts are numerous or unclear;
- `critic` before compiling D19 to challenge claim/evidence/wording boundaries;
- `architect` or `writer` to propose Writing Structure from confirmed upstream material;
- `writer` only for a leader-reviewed design-pack candidate when the compile gate passes.

Subagents must not ask the user directly, invent facts, finalize owner-gated route/claim/evidence/source/wording decisions, search citations by default, execute downstream writing skills, or create extra public workspace files.

## What the plugin owns

- project route and venue/type positioning;
- material and evidence location;
- source/citation candidate notes supplied by the user;
- contribution and claim-evidence boundary;
- allowed / forbidden wording;
- reader spine and writing structure;
- 20-dimension readiness status;
- external handoff constraints.

## What the plugin does not own

- manuscript drafting;
- external skill execution;
- citation search or BibTeX completion;
- runtime graph / stage registry;
- large validator matrix;
- reviewer simulation;
- LaTeX writeback or submission/export;
- upload, publication, acceptance, or final-paper claims.

## Repository structure

```text
yxj-paper-os/
  .codex-plugin/plugin.json
  skills/yxj-paper-os/
    SKILL.md
    references/          # internal playbooks
    assets/templates/    # six Markdown workspace templates
    scripts/             # lightweight validation
  docs/BRANCH_PHILOSOPHY.md
  references/            # external reference repos, not runtime dependencies
```

## External references

`references/external/` contains pinned external repositories used only as reference material. They are not vendored runtime dependencies and must not be executed automatically by this plugin.

## Validation

Portable structural workspace validation is repo-local:

```bash
python3 skills/yxj-paper-os/scripts/verify_design_pack.py <paper_project>
```

For offline structural dashboard visibility, use the existing `yxj-paper-os` skill submode triggered by `yxj-paper-os dashboard`, `dashboard`, or `维度 dashboard`, or run the generator directly:

```bash
python3 skills/yxj-paper-os/scripts/generate_dashboard.py <paper_project>
```

The dashboard writes only `<paper_project>/.yxj-paper-os/dashboard.html`. It does not initialize workspaces, copy templates, create or repair Markdown, write manuscript prose, run external skills, perform semantic scoring, prove paper readiness, start a runtime/server/watcher/graph, or add public workspace files. The six Markdown files remain the source of truth; the dashboard is structural visibility only, and `verify_design_pack.py` remains the validator of record.

During plugin development, also run the Codex plugin and skill validators provided by the local Codex installation. Those tools are environment-provided and are not required runtime dependencies of this repository.

Structural validation checks the six-file contract, dimension-index completeness, and claim/evidence anchors. It does not prove semantic adequacy of the paper plan.
