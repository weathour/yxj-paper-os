# Migration notes

The previous `/home/weathour/plugins/yxj-paper-os` implementation was archived before this local install. The installed `yxj-paper-os` source does not delete the archive, publish marketplace updates beyond the existing personal-local entry, or remove old project artifacts.

Archive locator:

```text
/home/weathour/plugins/.backups/yxj-paper-os-before-v2-install-20260622T121414Z
```

## Suggested future migration stages

1. Inventory old yxj-paper-os profiles, state files, and task packets by locator only.
2. Classify each artifact as preserve, adapt, replace, or discard.
3. Map old native-subagent-job packets to current task packets with explicit `agent_type`, collection path, state ledger path, and `validator_refs`.
4. Run current validators against migrated fixtures.
5. Ask for explicit confirmation before old-plugin archive removal, production publication, or destructive migration.


## V1-to-v2 governance migration

V1 paper-control fixtures and old project ledgers remain readable, but v2 tasks
must add governance fields before they can be considered managed by the new
system:

| V1 artifact/field | V2 target |
| --- | --- |
| `owner_lane` only | `owner_department` + `owner_lane` derived from `agent-lane-registry.yaml` |
| `expected_output_artifacts` | `expected_output_artifacts` plus `expected_output_materials` |
| generic context paths | typed `input_materials` with artifact ids/types/paths |
| narrative notes in prose | `ReaderSpineBrief` and `ObjectRepresentationMatrix` refs |
| exemplar/template notes in prose | `TemplateQuantProfile`, `SectionFunctionBudget`, and visual/formal budget refs |
| review findings as comments | `ReaderExperienceReviewReport` and `NarrativeBackflowTask` |
| validator report only | validator report plus fixture-matrix and mirror-sync evidence |

Migration is source-only unless the paper owner explicitly authorizes live
install, publish, old-plugin removal, external submission/upload, destructive
changes, credentialed services, or private/raw material copying. A migrated task
is not complete until the v2 material outputs are collected, validators pass,
state is ingested, and the state transition is explicit.

## Manager authority migration

Older ledgers may contain manager-authored prose, validator summaries, or closure
claims without actor provenance. When migrating such records, do not preserve the
old `complete` claim blindly. Reclassify manager-authored department work as a
`ManagerDirectIntervention` candidate, add provenance where available, derive
paper/state sensitivity from materials and state transitions, and require
independent review before promoting the migrated task to `complete`.

If provenance cannot be reconstructed, keep the migrated record as
`candidate`/`validated` with residual self-certification risk instead of
inventing an independent reviewer.


## V2-to-v2plus material migration

Existing v2 task packets remain valid when they preserve required v2 fields.
Do not rewrite old ledgers merely to satisfy v2plus fields. Instead, add v2plus
materials when a new or migrated task touches reader-facing writing, evidence,
review, export, or shared editing hotspots.

| Existing v2 concept | V2plus addition |
| --- | --- |
| `ReaderSpineBrief` / `ObjectRepresentationMatrix` | `ReviewerQuestionMap` + `MainTextConstructionMatrix` for section-level construction |
| citation/evidence bank | `ClaimCitationCapsule` for claim-level support |
| experiment/result artifact | `ResultPackage` for claim boundary and allowed wording |
| unmanaged section edit | `SingleWriterSectionLock` |
| prose review comment | `ReaderSurfaceTutorReview` with source/rendered spans and backflow route |
| export validation | `RenderedSurfaceGateReport` against rendered text |

Migration rule: old tasks can remain historical, but new completion claims for
paper-facing or state-sensitive work must pass the v2plus material/validator
contracts once the corresponding objects are introduced.

## Figure migration to Nature-grade governance

Existing figure plans, TikZ folders, generated plots, captions, or export
manifests do not need bulk rewriting. When a figure is newly created,
substantially redesigned, moved toward final manuscript use, or included in an
export package, migrate it into the Nature-grade chain:

| Existing figure artifact | Nature-grade addition |
| --- | --- |
| informal sketch / figure idea | `NatureFigureContract` with core conclusion, reader question, archetype, panel hierarchy, and evidence refs |
| style notes or copied exemplar taste | `NatureFigureAestheticProfile` with semantic palette, typography, labels, legend, background, and legibility gates |
| panel list | `NaturePanelEvidenceMap` with unique panel reader questions and evidence roles |
| mixed scripts/manual edits | `FigureBackendRoute` selecting one final editable source of truth |
| plot data notes | `FigureSourceDataStatistics` or explicit conceptual no-data rationale |
| image/screenshot/raster processing | `FigureImageIntegrityRecord` or explicit not-applicable vector rationale |
| caption draft | `NatureCaptionLegendBrief` with source/statistics/privacy/claim controls |
| generated SVG/PDF/PNG files | `FigureExportBundle` with editable text, dimensions, manifest refs, and hash provenance |
| visual review comment | `NatureFigureQAReport` plus rendered-surface gate and backflow route |

Migration must preserve yxj-paper-os philosophy: the public manager remains
single-entry, departments own their materials, validators prove closure, and the
state transition happens only after collection, validation, ingestion, and
backflow resolution. Do not treat the external Nature workflow as a hidden
manager or copy external figures; absorb only its process discipline and
aesthetic controls.


## Nature full-absorption control plane

Milestone M1 extends the earlier Nature-grade figure work into a broader yxj-native absorption layer for non-figure Nature skills. The source basis is `Yuan1z0825/nature-skills` at commit `5d2ba1dee1c087be6de8f4a8aad4b27f04974be9`. The absorption is not a public `nature-*` skill copy: the single public `yxj-paper-os` manager remains the only user-facing entry, and every absorbed capability is represented as an internal SOP/capability cell, material object, validator, fixture, backflow route, and ledger/state closure candidate.

The 14 first-class M1 materials are: `NatureSourceInventory`, `CompanySkillRegistry`, `NatureAbsorptionPackage`, `PaperReaderPackage`, `SearchStrategyDossier`, `CitationVerificationReport`, `SectionMovePlan`, `JournalStyleProfile`, `PolishingRepairReport`, `DataAvailabilityPlan`, `ReviewerPanelReport`, `ResponseActionMap`, `PresentationPlan`, and `PatentDraftBoundary`. `PresentationPlan` is owned by the existing canonical department id `manuscript_and_figure_production` as a writing/expression capability cell; the display label may say Manuscript / Figure / Communication Production, but the canonical id is frozen. Patent output is a source-grounded drafting aid only, not legal advice or a patentability guarantee.
