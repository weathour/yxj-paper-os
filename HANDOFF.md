# yxj-paper-os Handoff

Status: active minimal implementation branch.

## Current branch

`yxj-paper-os-slot-skill-redesign`

This branch intentionally deleted the old Paper Production Graph runtime and rebuilds `yxj-paper-os` as a standard Codex plugin with one public paper-planning skill.

## Governing architecture

```text
Single Skill, Five Internal Playbooks, Six Workspace Files
```

Public surface:

```text
skills/yxj-paper-os/SKILL.md
```

Internal resources:

```text
skills/yxj-paper-os/
  references/
    00-project-route.md
    01-materials-inventory.md
    02-claim-evidence-boundary.md
    03-writing-structure.md
    04-design-pack-compiler.md
  assets/templates/
    00_DIMENSION_INDEX.md
    00_PROJECT_ROUTE.md
    01_MATERIALS_INVENTORY.md
    02_CLAIM_EVIDENCE_BOUNDARY.md
    03_WRITING_STRUCTURE.md
    04_WRITING_DESIGN_PACK.md
  scripts/
    verify_design_pack.py
```

## Product contract

`yxj-paper-os` is a pre-writing information-completion gate. It helps Codex ask focused questions, fill six planning Markdown files, track D00-D19 in `00_DIMENSION_INDEX.md`, and compile `04_WRITING_DESIGN_PACK.md` only when hard blockers are resolved.

Hard blockers for design-pack generation:

1. project route;
2. core materials;
3. core contribution;
4. claim-evidence boundary;
5. writing structure;
6. external handoff route.

The plugin must block and ask when these are missing. It must not emit a final design pack full of unresolved placeholders.

## Non-goals

This branch does not provide:

- manuscript drafting;
- external skill execution;
- Paper Production Graph runtime;
- retired runtime-stage registry;
- large validator matrix;
- native citation lookup;
- reviewer simulation;
- LaTeX writeback, formatting export, submission, upload, publication, or acceptance claims.

Historical phase/slot names and older five-file planning notes may remain only as background context in old history. They are not the MVP public workflow.

## Branch and version management

- `main`: preserve historical implementation unless explicitly merged or replaced.
- `yxj-paper-os-slot-skill-redesign`: active clean rewrite branch.
- Commit policy: small commits that keep the plugin valid after each step.
- Version policy:
  - keep `.codex-plugin/plugin.json` at `0.1.0` during MVP rebuild;
  - bump patch for validated internal additions if desired;
  - bump minor only after the owner accepts a stable user-facing workspace contract.
- Migration policy: rebuild forward from the minimal plugin surface; recover old runtime pieces only by explicit decision.

## Validation

Workspace/design-pack validation is repo-local:

```bash
python3 skills/yxj-paper-os/scripts/verify_design_pack.py <paper_project>
```

For development, also run the plugin and skill validators from the active Codex installation. Keep those as environment-provided checks; do not make user-home or machine-local validator paths part of the public plugin contract.

## External references

`references/external/` is reference-only. External writing or review tools may receive `04_WRITING_DESIGN_PACK.md` as a handoff artifact, but this plugin must not execute those tools automatically.
