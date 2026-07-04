---
name: yxj-paper-os
description: Use for traffic, computer-science, or AI paper projects when Codex needs to initialize or inspect a lightweight paper-planning workspace, guide the user through missing project/material/claim/structure information, enforce claim-evidence boundaries, compile 04_WRITING_DESIGN_PACK.md, or validate a yxj writing design pack before handing off to downstream writing modules.
---

# yxj-paper-os

Operate `yxj-paper-os` as one public guided workflow with five internal playbooks.

Do not split the MVP into public subskills. Load only the internal playbook needed for the current missing area.

## Workspace contract

Use exactly these five project files:

```text
00_PROJECT_ROUTE.md
01_MATERIALS_INVENTORY.md
02_CLAIM_EVIDENCE_BOUNDARY.md
03_WRITING_STRUCTURE.md
04_WRITING_DESIGN_PACK.md
```

If files are missing, copy templates from `assets/templates/` before filling content.

## Core workflow

1. **Inspect / initialize.** Check whether the five files exist. If not, create them from `assets/templates/`.
2. **Find the first blocker.** Read the current files and identify the first missing hard-blocker category.
3. **Load one playbook.** Read the matching file under `references/`:
   - `00-project-route.md` for target venue, paper type, topic, and positioning.
   - `01-materials-inventory.md` for experiments, results, figures, data, code, baselines, and metrics.
   - `02-claim-evidence-boundary.md` for contribution, claims, evidence, wording, and limitations.
   - `03-writing-structure.md` for reader spine, section jobs, and figure storyline.
   - `04-design-pack-compiler.md` for final handoff compilation.
4. **Ask one focused question when blocked.** If required information is missing, ask only the next highest-leverage question and wait for the answer. Do not batch many questions unless the user explicitly asks for a form to fill.
5. **Update the relevant Markdown file.** Normalize the answer into the proper file. Preserve uncertainty as explicit `absent`, `deferred`, or `rejected` decisions instead of pretending completeness.
6. **Compile only when clear.** Generate or update `04_WRITING_DESIGN_PACK.md` only after all hard blockers are resolved.
7. **Validate.** Run `scripts/verify_design_pack.py <paper_project>` when a design pack is ready.

## Hard blockers

Block design-pack compilation and ask for missing information when any category below is incomplete:

| Blocker | Minimum required information |
|---|---|
| `project-route` | target venue/family, paper type, topic, traffic/computer positioning |
| `core-materials` | experiment/result/figure/table/data/code/baseline/metric locations or explicit absence decisions |
| `core-contribution` | problem, object, method/system/model, one-sentence contribution |
| `claim-evidence` | every core claim has evidence anchor, support strength, and forbidden wording boundary |
| `writing-structure` | reader spine, section jobs, figure storyline sufficient for downstream drafting |
| `external-route` | downstream writing route/skill category and handoff constraints |

A final `04_WRITING_DESIGN_PACK.md` with unresolved `TODO`, `TBD`, `REPLACE_ME`, or `UNKNOWN` is invalid.

## Boundaries

Do not:

- draft manuscript prose;
- execute external skills automatically;
- search for citations or invent BibTeX entries;
- invent experiments, data, baselines, metrics, results, or evidence anchors;
- strengthen claims beyond evidence;
- build a runtime graph, stage registry, worker orchestration, or large validator matrix;
- claim submission, upload, publication, acceptance, or final-paper completion.

External writing tools may receive `04_WRITING_DESIGN_PACK.md`, but they cannot override claim/evidence/owner boundaries.

## Output discipline

When reporting progress, name:

- which of the five files changed;
- which hard blockers remain;
- whether `04_WRITING_DESIGN_PACK.md` is valid or still blocked;
- which validation command was run and its result.
