# Canonical Lens Registry

These seven modules expose conditional, composable planning lenses, not manuscript-drafting instructions. Activate a lens only when its trigger is present; otherwise omit the sparse activation/requirement record or use an explicit local `not_applicable`/`deferred` state when it carries information. Canonical lens IDs are stable for validators and handoffs.

| Lens | Trigger | Primary dimensions | Gate |
|---|---|---|---|
| Contribution evidence forms | contribution/claim or evidence ambiguity | D06,D10,D11,D19 | every active form has owner, anchor, boundary |
| Research-design validity | design/reporting/reproducibility concern | D04-D06,D13,D15,D19 | method facts separated from claims |
| Evidence/results/statistics | result, table, metric, or statistical display exists | D05,D06,D11,D18,D19 | result anchor and uncertainty/display note |
| Literature differentiation | related-work or novelty positioning needed | D07,D08,D10,D14 | source role and gap boundary recorded |
| Reproducibility governance | data/code/materials or reporting availability | D02,D04,D05,D15,D19 | availability state and owner decision |
| Argument/language/visual | rhetorical, wording, caption, or accessibility risk | D12-D15,D18,D19 | allowed/forbidden wording and visual handoff |
| Venue-template corpus analysis | supplied venue/topic/exemplar documents can change a requested writing surface | D04,D05,D09,D15,D17-D19 | honest `case_set`/`exploratory`/`distributional` mode, current summary/profile pointer, scientific-evidence firewall |

Lens state remains conditional: `active`, `not_applicable`, `deferred`, `absent`, or `rejected`. The `venue-template` authority is `venue-template.md`; it uses canonical `documents`/`doc_id`/`partition` vocabulary and never creates a global corpus-size gate.
