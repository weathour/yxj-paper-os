# Workspace contract

yxj-paper-os is workspace-centric. Detect the paper root in this priority order:

1. explicit user-supplied paper project path;
2. current directory when it contains manuscript, notes, control-loop status, or yxj-paper-os profile markers;
3. repository project index mapping.

Block writes when multiple plausible roots would mix paper artifacts.

## Workspaces

| workspace | path pattern | purpose | owner lane |
| --- | --- | --- | --- |
| ws-paper-root | `<paper-root>/` | project boundary | state-steward |
| ws-control-plane | `<paper-root>/.omx/state/yxj-paper-os/` | machine state and ledgers | state-steward |
| ws-profile | `<paper-root>/notes/yxj-paper-os/profile/` or state profile | paper type, venue, profile | profile-architect |
| ws-intake | `<paper-root>/notes/yxj-paper-os/intake/` | brief, interview, decisions | interview-owner |
| ws-source-map | `<paper-root>/notes/yxj-paper-os/source-map/` | source inventory and locators | source-map-curator |
| ws-research | `<paper-root>/notes/yxj-paper-os/research/` | scene/exemplar/SOTA/novelty | research-director |
| ws-evidence | `<paper-root>/notes/yxj-paper-os/evidence/` or `<paper-root>/evidence/` | evidence banks and claim support | evidence-curator |
| ws-planning | `<paper-root>/notes/yxj-paper-os/planning/` | motivation, blueprints, rationale | paper-architect |
| ws-manuscript | `<paper-root>/manuscript/` or `<paper-root>/paper/` | manuscript sources | manuscript-owner |
| ws-figures | `<paper-root>/figures/` and notes figures | figure assets and provenance | figure-owner |
| ws-review | `<paper-root>/notes/yxj-paper-os/review/` | hostile review and backflow | review-director |
| ws-export | `<paper-root>/exports/` and notes export | export packages and manifests | export-owner |
| ws-shared-library | configured yxj-wiki or source backend locator | shared library by locator only | yxj-wiki-bridge |

## Private/raw zones

Use locator/hash/summary only for private PDFs, unpublished manuscripts, credentials, reviewer-confidential material, and raw source archives unless the owner explicitly authorizes tracked copying.
