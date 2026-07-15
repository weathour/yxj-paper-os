# 00 Dimension Index

## Workspace Schema Version

- Workspace schema version: 0.2

## Dimension Status Index

| ID | Dimension | Current home | Status | Reason / owner note | Pointer or handoff | Blocks design pack? |
|---|---|---|---|---|---|---|
| D00 | Workspace metadata | 00_DIMENSION_INDEX.md | filled | Legacy metadata recorded | 00_DIMENSION_INDEX.md#Workspace Schema Version | no |
| D01 | Owner decisions | 00_PROJECT_ROUTE.md | filled | Legacy route fixed | 00_PROJECT_ROUTE.md#Decision Records | no |
| D02 | Readiness flags | 00_DIMENSION_INDEX.md | filled | Legacy status recorded | 00_DIMENSION_INDEX.md#Writing Scopes | no |
| D03 | Project brief | 00_PROJECT_ROUTE.md | filled | Sanitized brief recorded | 00_PROJECT_ROUTE.md#Project Brief | no |
| D04 | Target route | 00_PROJECT_ROUTE.md | filled | Generic route recorded | 00_PROJECT_ROUTE.md#Project Brief | no |
| D05 | Materials | 01_MATERIALS_INVENTORY.md | filled | Sanitized material recorded | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D06 | Evidence | 01_MATERIALS_INVENTORY.md | filled | Legacy evidence boundary recorded | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D07 | Sources | 01_MATERIALS_INVENTORY.md | filled | Source role recorded | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D08 | Dossier | 01_MATERIALS_INVENTORY.md | not_applicable | Sanitized fixture omits dossier | 01_MATERIALS_INVENTORY.md#Material Records | no |
| D09 | Exemplar profile | 03_WRITING_STRUCTURE.md | not_applicable | Legacy scope used no exemplar analysis | 03_WRITING_STRUCTURE.md#Section Jobs | no |
| D10 | Contribution | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Boundary recorded | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D11 | Claim map | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Boundary recorded | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D12 | Wording | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Constraint recorded | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D13 | Limitations | 02_CLAIM_EVIDENCE_BOUNDARY.md | filled | Limitation recorded | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim Records | no |
| D14 | Reader spine | 03_WRITING_STRUCTURE.md | filled | Section job recorded | 03_WRITING_STRUCTURE.md#Section Jobs | no |
| D15 | Outline | 03_WRITING_STRUCTURE.md | filled | Section job recorded | 03_WRITING_STRUCTURE.md#Section Jobs | no |
| D16 | Granularity | 03_WRITING_STRUCTURE.md | filled | Section-only granularity recorded | 03_WRITING_STRUCTURE.md#Section Jobs | no |
| D17 | Surface control | 03_WRITING_STRUCTURE.md | filled | Legacy boundary recorded | 03_WRITING_STRUCTURE.md#Section Jobs | no |
| D18 | Visual plan | 03_WRITING_STRUCTURE.md | not_applicable | No visual in sanitized scope | 03_WRITING_STRUCTURE.md#Section Jobs | no |
| D19 | Design pack | 04_WRITING_DESIGN_PACK.md | filled | Legacy handoff compiled | 04_WRITING_DESIGN_PACK.md#Scoped Handoff | no |

## Writing Scopes

| Scope ID | Writing surface | Intended output | Readiness | Available inputs | Required requirement IDs | Remaining blocker | Next action | Output pointer |
|---|---|---|---|---|---|---|---|---|
| SCOPE-legacy | Sanitized section-level scope | Controlled downstream handoff | writer-ready | M-legacy | none | none | none | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |

## Active Calibration Lenses

| Lens ID | Activation basis | Affected scopes |
|---|---|---|

## Conditional Requirements

| Requirement ID | Lens ID | Requirement | Affected scopes | Handling | Evidence / decision pointer |
|---|---|---|---|---|---|

## Dependency Recheck

| Changed record | Affected D IDs / scopes | Disposition | Resolution or next action |
|---|---|---|---|
| M-legacy | D05; SCOPE-legacy | rechecked | Legacy section-level handoff recorded |
