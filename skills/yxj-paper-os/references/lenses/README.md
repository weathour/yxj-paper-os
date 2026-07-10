# Canonical Lens Registry

These six lenses are conditional planning schemas, not manuscript-drafting instructions. Activate a lens only when its trigger is present; otherwise record `not_applicable` or `deferred` in the owning template. Canonical headings and field IDs are stable for validators and handoffs.

| Lens | Trigger | Primary dimensions | Gate |
|---|---|---|---|
| Contribution evidence forms | contribution/claim or evidence ambiguity | D06,D10,D11,D19 | every active form has owner, anchor, boundary |
| Research-design validity | design/reporting/reproducibility concern | D04-D06,D13,D15,D19 | method facts separated from claims |
| Evidence/results/statistics | result, table, metric, or statistical display exists | D05,D06,D11,D18,D19 | result anchor and uncertainty/display note |
| Literature differentiation | related-work or novelty positioning needed | D07,D08,D10,D14 | source role and gap boundary recorded |
| Reproducibility governance | data/code/materials or reporting availability | D02,D04,D05,D15,D19 | availability state and owner decision |
| Argument/language/visual | rhetorical, wording, caption, or accessibility risk | D12-D15,D18,D19 | allowed/forbidden wording and visual handoff |

All schemas use the same conditional states: `active`, `not_applicable`, `deferred`, `absent`, `rejected`.
