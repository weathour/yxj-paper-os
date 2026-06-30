# yxj-paper-os Process Inventory

This document inventories what `$yxj-paper-os` already covered in academic paper production. It records aspects, layers, dimensions, materials, and workflow gates so PPG Runtime can preserve the useful analysis while replacing department self-loops with explicit material graph control.

## Summary

`yxj-paper-os` covered a very broad paper-production system. Its problem was not lack of analytical coverage; it covered almost every major dimension of paper creation. The failure mode was organizational: it modeled those dimensions as departments and manager loops rather than as explicit material nodes and local backflow edges.

## Top-level process

The top-level invariant was:

```text
compile -> execute -> collect -> validate -> ingest -> state_transition
```

This is worth preserving. In PPG Runtime, it maps to:

```text
compile task packet -> produce candidate material -> validate -> commit graph state -> propagate stale/backflow
```

## Main layers covered

### 1. PMO / state control layer

Covered by:

- `yxj-paper-os` public entry;
- `yxj-paper-index`;
- `yxj-paper-state`;
- orchestrator, workspace, department, repository hygiene references.

Analysis dimensions:

- paper-root detection;
- active gate;
- ledgers;
- artifact ownership;
- decision status;
- evidence/review/export state;
- repository hygiene;
- delivery cleanliness;
- final handoff readiness;
- owner-gated vs auto-continuable work.

Materials:

- `state.yaml`;
- `task-ledger.yaml`;
- `artifact-ledger.yaml`;
- `decision-ledger.yaml`;
- `evidence-ledger.yaml`;
- `review-ledger.yaml`;
- `export-ledger.yaml`;
- `RepositoryHygieneReport`;
- `ManagerHandoffReportV2`.

### 2. Owner decision / interview layer

Covered by `yxj-paper-interview`.

Analysis dimensions:

- final motivation;
- contribution spine;
- target venue;
- claim scope;
- source-use policy;
- private/raw material policy;
- destructive/external/team gates.

Materials:

- decision records;
- confirmed decisions vs assumptions;
- owner-gated blockers.

### 3. Research and scene-analysis layer

Covered by `yxj-paper-research` and PaperSpine influence.

Analysis dimensions:

- field scene;
- problem framing;
- venue expectations;
- exemplar learning;
- style/structure learning;
- SOTA mapping;
- citation candidates;
- source-grounded research dossiers.

Lanes:

- Scene Analyst;
- Exemplar Learner;
- SOTA Mapper.

Materials:

- `ResearchDossier`;
- source map;
- template profile;
- SOTA/citation candidate records.

### 4. Novelty exploration layer

Covered by `yxj-paper-novelty` and Sisyphus influence.

Analysis dimensions:

- contrarian lens;
- cross-pollination;
- assumption excavation;
- counterfactual generation;
- paradox sifting;
- heretic challenge;
- evidence readiness;
- novelty risk.

Materials:

- novelty options;
- evidence-readiness score;
- risk/source anchors;
- owner-confirmation requirements.

### 5. Planning / PaperSpine / manuscript architecture layer

Covered by `yxj-paper-plan` and `yxj-paper-paperspine`.

Analysis dimensions:

- confirmed motivation;
- contribution map;
- section blueprint;
- writing rationale;
- branch ownership;
- validators;
- expected failure modes;
- state transition plan.

Materials:

- `motivation.yaml`;
- contribution map;
- section blueprints;
- `rationale-matrix.yaml`;
- branch owner map;
- validator list;
- state transition plan.

### 6. Evidence / claim / citation layer

Covered by `yxj-paper-evidence`.

Analysis dimensions:

- source maps;
- citation support;
- evidence bank;
- claim support;
- claim wording constraints;
- experiment result promotion;
- privacy/source locator boundary;
- unresolved support.

Materials:

- `source-map.yaml`;
- `citation-bank.yaml`;
- `evidence-bank.yaml`;
- `ClaimCitationCapsule`;
- `ResultPackage`;
- claim support maps;
- source locator reports.

Core rule:

> Evidence materials are not prose. Writing consumes evidence through construction materials so source boundaries and support strength survive drafting.

### 7. Reader narrative and expression-design layer

Covered by `reader-narrative-governance.md`.

Analysis dimensions:

- reader/reviewer questions;
- object representation across sections;
- section function;
- paragraph rhetorical moves;
- cognitive load;
- explanation progression;
- claim visibility;
- terminology translation;
- lab-notebook-smell detection;
- rendered reader surface.

Materials:

- `ReviewerQuestionMap`;
- `ReaderSpineBrief`;
- `ObjectRepresentationMatrix`;
- `MainTextConstructionMatrix`;
- `TemplateQuantProfile`;
- `SectionFunctionBudget`;
- `CognitiveLoadBudget`;
- `ExplanationLadder`;
- `RhetoricalMoveMatrix`;
- `ClaimEvidenceVisibilityMap`;
- `TerminologyRegister`;
- `ReaderExperienceReviewReport`;
- `NarrativeBackflowTask`;
- `MainTextSurfaceRules`;
- `RenderedSurfaceGateReport`.

### 8. Writing / execution layer

Covered by `yxj-paper-execute`, production lane expectations, and task packet governance.

Analysis dimensions:

- task packet compilation;
- agent type selection;
- scoped context;
- output collection path;
- validator refs;
- ledger ingestion;
- state transition;
- managed-agent pressure telemetry;
- single-writer locks;
- authority role separation.

Materials:

- `TaskPacketV2` / `TaskPacketV2Plus`;
- `SingleWriterSectionLock`;
- `ManagerDirectIntervention`;
- authority role separation block;
- collection artifacts;
- validator reports.

### 9. Figure / visual / formal-object layer

Covered by `yxj-paper-figures` and Nature-grade figure governance.

Analysis dimensions:

- figure message;
- reader question;
- figure archetype;
- panel hierarchy;
- panel evidence;
- source data/statistics;
- image/raster integrity;
- figure backend route;
- caption claims;
- visual/aesthetic QA;
- export bundle;
- TikZ instruction design.

Materials:

- `VisualTableAlgorithmFormulaBudget`;
- `NatureFigureContract`;
- `NatureFigureAestheticProfile`;
- `NaturePanelEvidenceMap`;
- `FigureBackendRoute`;
- `FigureSourceDataStatistics`;
- `FigureImageIntegrityRecord`;
- `NatureCaptionLegendBrief`;
- `NatureFigureQAReport`;
- `FigureExportBundle`;
- `FIGURE_INSTRUCTION.md`;
- figure README/data manifest.

### 10. Review / adversarial backflow layer

Covered by `yxj-paper-review` and Sisyphus hostile-review influence.

Analysis dimensions:

- hostile reviewer panels;
- theory/method/evidence/style critique;
- reader surface critique;
- review independence;
- manager self-certification risk;
- fix task routing;
- severity/evidence status;
- resolution tracking.

Reviewer lenses:

- theorist;
- empiricist;
- methodologist;
- skeptic;
- historian;
- competitor;
- pragmatist;
- ethicist;
- student;
- dreamer.

Materials:

- `ReviewOutput`;
- `ReviewerPanelReport`;
- `ReaderExperienceReviewReport`;
- `NarrativeBackflowTask`;
- review-ledger entries;
- fix tasks.

### 11. Export / rendered surface / delivery layer

Covered by `yxj-paper-export` and repository delivery governance.

Analysis dimensions:

- PDF/LaTeX/Word package build;
- export manifest;
- build report;
- rendered PDF text inspection;
- citation rendering;
- internal code leaks;
- privacy checks;
- residual risks;
- external submission boundary;
- delivery cleanliness.

Materials:

- `ExportManifest`;
- build reports;
- `RenderedSurfaceGateReport`;
- `RepositoryHygieneReport`;
- export-ledger entries.

### 12. Nature capability absorption layer

Covered by `nature-absorption-governance.md` and `skill-registry-governance.md`.

Analysis dimensions:

- reader package;
- academic search;
- citation verification;
- section moves;
- journal style;
- polishing repair;
- data availability;
- reviewer panels;
- response mapping;
- presentation/PPT planning;
- patent-draft boundary.

Materials:

- `NatureSourceInventory`;
- `CompanySkillRegistry`;
- `PaperReaderPackage`;
- `SearchStrategyDossier`;
- `CitationVerificationReport`;
- `SectionMovePlan`;
- `JournalStyleProfile`;
- `PolishingRepairReport`;
- `DataAvailabilityPlan`;
- `ReviewerPanelReport`;
- `ResponseActionMap`;
- `PresentationPlan`;
- `PatentDraftBoundary`;
- `NatureAbsorptionPackage`.

### 13. Migration / provenance layer

Covered by `yxj-paper-migration`.

Analysis dimensions:

- old artifact compatibility;
- preserve/adapt/replace/discard classification;
- non-destructive migration;
- install/uninstall gates;
- source scaffold comparison.

Materials:

- migration notes;
- artifact classification;
- required gate records.

## Department model used by yxj-paper-os

The final v2 department model grouped the above into five Department Managers:

1. PMO / Paper Management;
2. Paper Architecture & Narrative;
3. Evidence & Method;
4. Manuscript & Figure Production;
5. Review & Governance.

This was an accountability model. The problematic implementation tendency was letting these become active organizational self-loops rather than graph labels.

## What PPG Runtime should preserve

Preserve these analytical dimensions:

- owner intent and semantic gates;
- source/evidence/citation support;
- reader/reviewer question design;
- paper spine and section function;
- object representation and granularity progression;
- terminology and claim visibility;
- task packet discipline;
- single-writer and authority separation;
- figure/caption/evidence provenance;
- hostile review and routed backflow;
- rendered export and repository hygiene.

## What PPG Runtime should change

Replace:

```text
department manager -> department loop -> department report
```

with:

```text
material node -> transform task -> candidate output -> validator -> graph commit / backflow
```

Departments become metadata labels. Materials, validators, and backflow edges become the control surface.
