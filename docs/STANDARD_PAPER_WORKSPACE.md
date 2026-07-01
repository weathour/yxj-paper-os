# Standard Paper Workspace Contract

This document defines the ideal repository layout that `yxj-paper-os` expects when it manages a paper across evidence, writing, figures, review, export, and runtime backflow. It is intentionally repository-local and template-adaptable: a project may use IEEE, Nature, MDPI, Springer, or a supplied custom LaTeX template as long as the manifest declares how the template maps to the canonical surfaces.

## Goal

The runtime needs one stable directory grammar so that agents can tell the difference between:

- source manuscript files that can eventually be patched;
- generated figures and build outputs;
- evidence packages that support claims;
- review/backflow/runtime records; and
- owner-gated exports or submissions.

The directory contract does **not** require every project to physically move files. A project can provide a `paper-workspace.json` manifest that maps its local paths to the canonical roles.

When the manager surface is invoked for a local paper repository, the controller must combine this workspace manifest with [`MANAGER_SURFACE_PROTOCOL.md`](MANAGER_SURFACE_PROTOCOL.md): first determine current authority/candidate/archive/stale boundaries, then map the next task to `S00-S16/G01/G02`.

## Canonical top-level layout

```text
paper-root/
  AGENTS.md                         # local agent contract and safety boundaries
  README.md                         # public project overview
  PROJECT_STATUS.md                 # current authority/status summary
  HANDOFF.md                        # current manager handoff
  paper-workspace.json              # PaperWorkspaceContract manifest

  manuscript/                       # canonical LaTeX source tree
    main.tex                        # primary build target, or manifest-declared equivalent
    sections/                       # one source unit per paper section where feasible
    bib/                            # BibTeX/Biber databases
    templates/                      # optional copied or referenced journal templates
    build/                          # generated build products, not claim authority

  figures/
    src/                            # editable figure sources/scripts/data manifests
    generated/                      # rendered figures with provenance/hash records

  experiments/ or evidence/          # raw/processed evidence packages
    results/                        # validation packages and manifests

  claims/                           # claim ladder, evidence map, limitation matrix
  docs/                             # current plan, sync briefs, method/evidence notes
  reviews/                          # hostile review, response, closure records
  references/                       # BibTeX workspace, template notes, source maps
  data/                             # lightweight curated data or external-data manifests
  exports/                          # owner-facing export packages, regenerated on demand
  notes/                            # transient but current-spine notes

  paper-os/                         # optional repo-local runtime workspace
    materials/                      # committed graph materials if owner chooses repo-local state
    packets/                        # source-writeback task packets
    candidates/                     # candidate text/figure patches before promotion
    writeback/                      # source-writeback plans, patch manifests, apply reports
    validators/                     # validation reports and rendered-surface gates
    runs/                           # run-owned scratch artifacts; never manuscript authority by itself
```

## Required manifest roles

A repository is Paper-OS-ready when `paper-workspace.json` or an equivalent imported manifest declares these roles:

| Role | Purpose | Typical paths |
|---|---|---|
| `semantic_control` | owner/status/handoff surfaces | `README.md`, `PROJECT_STATUS.md`, `HANDOFF.md` |
| `manuscript_source` | canonical editable LaTeX source | `manuscript/main.tex`, `manuscript/sections/*.tex`, `manuscript/bib/*.bib` |
| `latex_template` | venue/template profile and build assumptions | `manuscript/templates/<venue>/`, `references/journal_templates/<venue>/` |
| `figure_source` | editable figure scripts/source data | `figures/src/**` |
| `figure_generated` | rendered figures and provenance | `figures/generated/**` |
| `evidence` | experiment/result evidence packages | `experiments/results/**` or `evidence/**` |
| `claim_control` | claim/evidence/limitation ladder | `claims/**` |
| `review_backflow` | review findings and local repair tasks | `reviews/**`, `paper-os/writeback/**` |
| `export` | generated author/submission bundles | `exports/**` |
| `runtime_state` | Paper OS graph/run artifacts | `paper-os/**` or plugin-owned `runs/**` |

## LaTeX template profile

The manifest must include a template-aware LaTeX profile instead of assuming a fixed class or layout:

```json
{
  "latex_profile": {
    "main_tex": "manuscript/main.tex",
    "engine": "latexmk",
    "build_commands": [
      "cd manuscript && latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex"
    ],
    "output_pdf": "manuscript/build/main.pdf",
    "section_globs": ["manuscript/sections/*.tex"],
    "bib_globs": ["manuscript/bib/*.bib"],
    "template_roots": ["manuscript/templates", "references/journal_templates"],
    "template_adapter_policy": "preserve_template_preamble_and_inject_controlled_body_units"
  }
}
```

Template adaptation should reuse the repository's LaTeX conversion/build skills: parse the supplied template, preserve its document class and required front matter, map source sections into the target body slots, then compile and inspect the log. A template adapter is allowed to change LaTeX structure only through an explicit writeback plan and validation gate.

## Source-writeback relationship

The standard workspace does not make every runtime stage a writer. Unplanned worker/runtime writes remain read-only by default. Real local source writes are allowed when a `LatexWritebackPlan` promotes a validated candidate into a scoped patch; for ordinary manuscript iteration the Paper OS controller applies the patch, compiles, validates, and creates a scoped source commit without asking for an extra confirmation step:

```text
S10 candidate text      -> patch manuscript/sections/*.tex
S11 figure/caption      -> patch figures/src/**, figures/generated/**, or caption blocks
S12 integration gate    -> compile, cross-reference, claim-surface, figure-text checks
S13 review              -> actionable findings only
S14 repair plan         -> local repair tasks
S15 repair writeback    -> patch affected nodes only
S16 delivery gate       -> build/export/handoff with owner-gated submission
```

No stage may bypass S04 claim admissibility, S07 terminology/surface control, S11 figure provenance, or S12/S16 validation. The controller owns promotion; workers return candidates and patch proposals.

`--dry-run` remains available for inspection, but it is not the default production mode. Owner gates are reserved for semantic route changes, supplied-template changes that alter structure/claims, cross-repository writes, exports/submission, and other external or irreversible actions.

## Validation rules

A valid workspace contract must prove:

1. source paths are explicit and not broad repository roots;
2. runtime output paths are separated from manuscript source paths;
3. LaTeX build commands and output PDF are declared;
4. template roots or an explicit `no_template_supplied_yet` state are declared;
5. evidence, claim, review, and export roles are present;
6. generated exports are not treated as manuscript authority;
7. external submission remains owner-gated.
