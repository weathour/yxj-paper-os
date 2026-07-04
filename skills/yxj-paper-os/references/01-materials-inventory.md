# Playbook 01 — Materials Inventory

Use this playbook when `01_MATERIALS_INVENTORY.md` is missing or incomplete, or when D05/D06/D07/D08 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D05 | `02_material_inventory.md` | `01_MATERIALS_INVENTORY.md` |
| D06 | `03_evidence_inventory.md` | `01_MATERIALS_INVENTORY.md#Evidence Inventory` + `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map` |
| D07 | `04_source_and_citation_bank.md` | `01_MATERIALS_INVENTORY.md#Source and Citation Bank` |
| D08 | `10_research_dossier.md` | `01_MATERIALS_INVENTORY.md#Research Dossier` + `04_WRITING_DESIGN_PACK.md#Research Dossier Notes` |

After updating material content, update the matching D05-D08 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Required fields

- Experiment/result locations.
- Figure and table locations.
- Data locations.
- Code locations.
- Baselines or comparison methods.
- Metrics and evaluation dimensions.
- Evidence inventory: anchors, type, location, supported claim/dimension, status.
- User-provided source/citation candidates, if any.
- Existing related-work/research-dossier notes, if any.
- Existing draft fragments, if any.
- Explicitly absent materials and their consequences.

## Ask when missing

Ask one focused question at a time. Prefer this order:

1. “Where are the main results, tables, or experiment logs?”
2. “Which figures/tables already exist, and where are they?”
3. “What baselines and metrics support the core comparison?”
4. “Which evidence anchor supports the strongest planned claim?”
5. “Which sources or citation candidates are already known or supplied by you?”
6. “Which related-work notes are absent and should be marked absent/deferred rather than invented?”
7. “Which expected materials are absent and should be marked absent rather than invented?”

## Hard blocker

Block design-pack compilation if materials are not locatable and no explicit absence/defer/reject decision exists for:

- results;
- figures/tables;
- data/code when they are relevant to the claimed contribution;
- baselines;
- metrics;
- evidence anchors for core claims;
- source/citation bank status.

## Output sections

Update `01_MATERIALS_INVENTORY.md` with:

- Results and experiments;
- Figures and tables;
- Data sources;
- Code / implementation;
- Baselines;
- Metrics;
- Evidence inventory;
- Source and citation bank;
- Research dossier;
- Existing text fragments;
- Explicit absences.

## Index update examples

- Filled materials: `D05 | filled | experiment locations provided | 01_MATERIALS_INVENTORY.md#Results and Experiments | yes`.
- Absent citation bank: `D07 | absent | owner has not supplied citation candidates; plugin must not search | Handoff: downstream writing may request sources from owner | yes`.

## Do not assume

- Do not invent experiment outcomes.
- Do not convert planned experiments into completed evidence.
- Do not treat “we can probably show” as evidence.
- Do not perform native citation search or invent BibTeX entries.
