# 00 Dimension Index

## Workspace Metadata

- Project slug: detailed-ready-minimal
- Design-pack readiness: writer-ready

## Workspace Schema Version

- Workspace schema version: 0.3
- Public template contract: six Markdown files.

## Dimension Status Index

| ID | Dimension | Current home | Status | Reason / owner note | Pointer or handoff | Blocks design pack? |
|---|---|---|---|---|---|---|
| D00 | Workspace metadata | 00_DIMENSION_INDEX.md | filled | Minimal fixture metadata is complete | 00_DIMENSION_INDEX.md#Workspace Metadata | no |
| D01 | Owner decisions | 00_PROJECT_ROUTE.md | filled | No consequence-bearing gate is triggered | 00_PROJECT_ROUTE.md#Decision Records | no |
| D02 | Stale/readiness flags | 00_DIMENSION_INDEX.md | filled | All fixture dependencies are current | 00_DIMENSION_INDEX.md#Dependency Recheck | no |
| D03 | Project brief | 00_PROJECT_ROUTE.md | filled | Generic design target is bounded | 00_PROJECT_ROUTE.md#Project Brief | no |
| D04 | Target route profile | 00_PROJECT_ROUTE.md | filled | Generic route has no venue constraint | 00_PROJECT_ROUTE.md#Target Route | no |
| D05 | Material inventory | 01_MATERIALS_INVENTORY.md | filled | Minimal material records resolve | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D06 | Evidence inventory | 01_MATERIALS_INVENTORY.md | filled | One evidence record resolves | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D07 | Source and citation bank | 01_MATERIALS_INVENTORY.md | not_applicable | No citation-dependent surface is planned | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D08 | Research dossier | 01_MATERIALS_INVENTORY.md | not_applicable | No research dossier is needed for this synthetic scope | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D09 | Exemplar language profile | 03_WRITING_STRUCTURE.md | not_applicable | Template design is grounded not applicable | 04_WRITING_DESIGN_PACK.md#Template Analysis Handling | no |
| D10 | Contribution options | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | One bounded contribution role is fixed | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D11 | Claim-evidence map | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Claim support is explicitly bounded | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D12 | Wording boundary | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Verb and overclaim limits are explicit | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D13 | Limitation and risk matrix | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Synthetic evidence ceiling is explicit | 02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations | no |
| D14 | Reader spine | 03_WRITING_STRUCTURE.md | filled | Paragraph reader-state transitions are complete | 03_WRITING_STRUCTURE.md#Paragraph Map | no |
| D15 | Manuscript outline | 03_WRITING_STRUCTURE.md | filled | One section and two paragraphs are ordered | 03_WRITING_STRUCTURE.md#Section Map | no |
| D16 | Object granularity | 03_WRITING_STRUCTURE.md | filled | Section paragraph frame and visual ownership resolve | 03_WRITING_STRUCTURE.md#Paragraph Payload and Boundary Map | no |
| D17 | Surface control | 03_WRITING_STRUCTURE.md | filled | Language and frame constraints resolve | 03_WRITING_STRUCTURE.md#Surface Language Contract | no |
| D18 | Visual plan | 03_WRITING_STRUCTURE.md | filled | One evidence-grounded visual job resolves | 03_WRITING_STRUCTURE.md#Visual Blueprint | no |
| D19 | Writing design pack | 04_WRITING_DESIGN_PACK.md | filled | Seven-surface manifest and handoff resolve | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage | no |

## Writing Scopes

| Scope ID | Writing surface | Intended output | Readiness | Available inputs | Required requirement IDs | Remaining blocker | Next action | Output pointer |
|---|---|---|---|---|---|---|---|---|
| SCOPE-demo | Synthetic two-paragraph method surface | Controlled writing handoff | writer-ready | M-method;M-evidence;M-visual | REQ-detailed | none | none | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage |

## Active Calibration Lenses

| Lens ID | Activation basis | Affected scopes |
|---|---|---|
| argument-language-visual | Paragraph frames language and visual handoff are required | SCOPE-demo |

## Conditional Requirements

| Requirement ID | Lens ID | Requirement | Affected scopes | Handling | Evidence / decision pointer |
|---|---|---|---|---|---|
| REQ-detailed | argument-language-visual | Complete all applicable detailed surfaces | SCOPE-demo | satisfied | 04_WRITING_DESIGN_PACK.md#Detailed Surface Coverage |

## Dependency Recheck

| Changed record | Affected D IDs / scopes | Disposition | Resolution or next action |
|---|---|---|---|
| M-method | D05;D15;SCOPE-demo | rechecked | Section and paragraph records resolve to the current fixture material |
