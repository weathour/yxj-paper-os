# Playbook 01 — Materials Inventory

Use this playbook when `01_MATERIALS_INVENTORY.md` is missing or incomplete.

## Required fields

- Experiment/result locations.
- Figure and table locations.
- Data locations.
- Code locations.
- Baselines or comparison methods.
- Metrics and evaluation dimensions.
- Existing draft fragments, if any.
- Explicitly absent materials and their consequences.

## Ask when missing

Ask one focused question at a time. Prefer this order:

1. “Where are the main results, tables, or experiment logs?”
2. “Which figures/tables already exist, and where are they?”
3. “What baselines and metrics support the core comparison?”
4. “Which expected materials are absent and should be marked absent rather than invented?”

## Hard blocker

Block design-pack compilation if materials are not locatable and no explicit absence decision exists for:

- results;
- figures/tables;
- data/code when they are relevant to the claimed contribution;
- baselines;
- metrics.

## Output sections

Update `01_MATERIALS_INVENTORY.md` with:

- Results and experiments;
- Figures and tables;
- Data sources;
- Code / implementation;
- Baselines;
- Metrics;
- Existing text fragments;
- Explicit absences.

## Do not assume

- Do not invent experiment outcomes.
- Do not convert planned experiments into completed evidence.
- Do not treat “we can probably show” as evidence.
