# yxj-paper-os

`yxj-paper-os` is a minimal Codex plugin for preparing traffic / computer-science / AI paper projects before manuscript drafting.

It does **not** write the manuscript. It guides Codex to collect the missing upstream information, blocks when required information is absent, and produces a writing-design handoff for downstream writing modules.

## MVP architecture

```text
Single public skill
  + five internal playbooks
  + five Markdown templates
  + one lightweight validator
```

The public surface is one skill:

```text
skills/yxj-paper-os/SKILL.md
```

The internal planning files are:

```text
paper_project/
  00_PROJECT_ROUTE.md
  01_MATERIALS_INVENTORY.md
  02_CLAIM_EVIDENCE_BOUNDARY.md
  03_WRITING_STRUCTURE.md
  04_WRITING_DESIGN_PACK.md
```

`04_WRITING_DESIGN_PACK.md` is the handoff artifact for writing, figure, citation, polishing, or review tools.

## What the plugin owns

- project route and venue/type positioning;
- material and evidence location;
- contribution and claim-evidence boundary;
- allowed / forbidden wording;
- reader spine and writing structure;
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
    assets/templates/    # Markdown templates
    scripts/             # lightweight validation
  docs/BRANCH_PHILOSOPHY.md
  references/            # external reference repos, not runtime dependencies
```

## External references

`references/external/` contains pinned external repositories used only as reference material. They are not vendored runtime dependencies and must not be executed automatically by this plugin.

## Validation

Portable workspace validation is repo-local:

```bash
python3 skills/yxj-paper-os/scripts/verify_design_pack.py <paper_project>
```

During plugin development, also run the Codex plugin and skill validators provided by the local Codex installation. Those tools are environment-provided and are not required runtime dependencies of this repository.
