# Playbook 04 — Design Pack Compiler

Use this playbook only when compiling or validating `04_WRITING_DESIGN_PACK.md`, or when D00/D02/D19 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is a central internal rubric/reference, not a sixth task playbook and not a public workspace file. Do not duplicate its full D00-D19 rubric here.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D00 | `00_META.md` | `00_DIMENSION_INDEX.md#Workspace Metadata` |
| D02 | `STALE_FLAGS.md` | `00_DIMENSION_INDEX.md#Dimension Status Index` + `#Readiness Gate` |
| D19 | `25_WRITING_DESIGN_PACK.md` | `04_WRITING_DESIGN_PACK.md` |

After compiling, update D00/D02/D19 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Inputs

Read these files first:

- `00_DIMENSION_INDEX.md`
- `00_PROJECT_ROUTE.md`
- `01_MATERIALS_INVENTORY.md`
- `02_CLAIM_EVIDENCE_BOUNDARY.md`
- `03_WRITING_STRUCTURE.md`

## Compile only if clear

Do not compile the final design pack when any hard blocker remains:

- unhandled D00-D19 dimension row;
- invalid status, reason, pointer/handoff, or `Blocks design pack?` value in `00_DIMENSION_INDEX.md`;
- project route;
- core materials;
- core contribution;
- claim-evidence boundary;
- writing structure;
- external route.

If blocked, report the missing blocker or dimension ID and ask the next focused question instead.

## Required design-pack sections

`04_WRITING_DESIGN_PACK.md` must include:

- Dimension Coverage Summary;
- Project Route;
- Material Boundary;
- Source / Citation Boundary;
- Research Dossier Notes;
- Core Contribution;
- Claim-Evidence Map, including support status;
- Allowed Wording;
- Forbidden Wording;
- Limitations and Risks;
- Reader Spine;
- Writing Structure;
- Visual and Figure Storyline;
- External Skill Handoff;
- Validation Notes.

## External handoff

Recommend a downstream route only as guidance. Do not execute external skills.

Examples:

- Nature-style writing/polishing route when venue and tone justify it.
- ML/CV/NLP/algorithm writing route for computer-science method papers.
- Generic scientific-writing route when no specialized route is known.

## Index update examples

- Ready design pack: `D19 | filled | design pack compiled after all dimensions handled | 04_WRITING_DESIGN_PACK.md#Dimension Coverage Summary | yes`.
- Stale downstream pack: `D02 | deferred | material/claim dimension changed after pack compile | Handoff: recompile design pack before writing | yes`.

## Validation meaning

A passing validator means the design pack is structurally valid against the six-file/20-dimension contract. It does not prove semantic adequacy or manuscript quality.

## Do not assume

- Do not fill unresolved fields with TODO in the final design pack.
- Do not turn deferred claims into supported claims.
- Do not omit limitations that constrain wording.
- Do not execute downstream writing or citation skills.
