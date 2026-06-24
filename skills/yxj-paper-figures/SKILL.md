---
name: yxj-paper-figures
description: "Plan and validate yxj-paper-os academic figures, figure provenance, data locators, captions, figure claims, and export references. Use when creating or reviewing paper figures and visual evidence."
---


# yxj-paper-figures

Treat figures as evidence-bearing artifacts.

Each figure plan must include source data locator, generation script or manual provenance, caption claim anchors, privacy policy, and validation status. Route unsupported visual claims to `$yxj-paper-evidence` or `$yxj-paper-review`.

## Required gates

Do not treat drawing as complete until the figure has passed:

`plan -> source/provenance -> render/build -> visual inspect -> manuscript/caption check -> claim/evidence validation -> ledger/export update when applicable`.

For claim-bearing manuscript figures, distinguish:

- **Conceptual/vector figures:** TikZ/cps-tikz or another deterministic vector source.
- **Data figures:** script-generated from declared CSV/JSON/result locators.
- **Draft-only visual ideation:** optional non-evidence assets; never cite as data or final manuscript proof.

## TikZ pre-drawing gate

Before creating or substantially rewriting any TikZ/cps-tikz figure, write a **Figure Instruction / module-position design card** in the figure source folder, for example:

`figures/src/<figure-id>/FIGURE_INSTRUCTION.md`

This card is mandatory for new TikZ figures and for major layout rewrites. A tiny compile-only fix may skip a new card only when an existing card/source plan already covers the figure and the final report states that no layout or claim changed.

The card must define:

1. **Success criterion:** paper context, one-sentence message, and what the reader should understand.
2. **Format/layer:** TikZ 2D, TikZ 2.5D traffic, or other deterministic vector route; library entry point; target column/page shape.
3. **Layout plan:** information-flow direction, zones/stages, alignment groups, and cross-zone link rails.
4. **Modules table:** module ID, exact text, role, visual hierarchy, style/color, and position/anchor.
5. **Links table:** from/to, relation type, arrow style, label, and route/rail.
6. **Embedded visuals:** mini chart/matrix/none, data shown, and reserved size.
7. **ASCII sketch:** rough but explicit placement before code is written.
8. **Claim boundary:** allowed caption claims and non-claims.
9. **Validation checklist:** compile command, generated artifacts, visual checks, manuscript slot, and evidence/ledger validators.

When a shared CPS TikZ library is available, follow its drawing entrypoint and checklist before writing TikZ code:

- `shared/cps-tikz-library/DRAWING-ENTRYPOINT.md`
- `shared/cps-tikz-library/checklists/figure-instruction-template.md`
- `shared/cps-tikz-library/checklists/figure-review-checklist.md`

If those files are not present, still create the same fields locally in `FIGURE_INSTRUCTION.md`.

## TikZ drawing workflow

For TikZ/cps-tikz figures:

1. Create or update the `FIGURE_INSTRUCTION.md` design card.
2. Create or update `README.md` with figure ID, manuscript slot, route, supported claim, allowed caption claims, non-claims, source files, generated artifacts, and rerun command.
3. Create or update `data_manifest.json`; use an explicit `conceptual: true` and `no_data_rationale` for non-data schematics.
4. Implement the figure in deterministic TikZ source. Prefer shared semantic colors/styles/macros over ad hoc colors.
5. Compile standalone PDF and convert to SVG/PNG when used by the manuscript/export package.
6. Visually inspect the rendered PNG/PDF for clipping, unreadable text, overlaps, arrow crossings, wrong direction, and target-column fit.
7. Insert or update the manuscript `\includegraphics`, label, and caption only after standalone validation.
8. Rebuild the manuscript and rerun claim/evidence/export/ledger checks when the figure affects the paper package.

## Hard prohibitions

- Do not use ImageGen or other raster generation as the final source for a TikZ-style academic diagram.
- Do not draw measured trajectories, confidence intervals, rankings, or real-data/proxy evidence unless the source data locator and script are declared.
- Do not copy template-paper figures; transfer only functional roles and journal-style discipline.
- Do not let a generated/rendered artifact become the source of truth when editable TikZ/script source exists.
