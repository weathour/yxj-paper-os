# Human Need to Paper Artifact Flow

This document defines the first human-centered paper-production flow for PPG Runtime.

The starting point is not a framework, department, or material schema. The starting point is a concrete human need:

> I want to produce a paper that makes a specific contribution credible, readable, reviewable, and publishable.

The runtime should then organize analysis, design, writing, integration, review, and backflow around that need.

## Core idea

A paper is not produced by a single writing step. It is produced by multiple dimensions of design and evidence that converge into writing modules, then undergo review losses and targeted backflow.

```text
human need
  -> semantic contract
  -> parallel analysis/design dimensions
  -> synthesized control materials
  -> writing task packets
  -> section/figure/caption modules
  -> integrated manuscript
  -> multi-loss review
  -> local backflow
  -> revised materials / revised text
  -> final paper artifact
```

## Layer 0 — Human concrete need

This is the root. It cannot be replaced by agent inference.

Typical inputs:

- topic or problem direction;
- intended paper type;
- target reader or venue route;
- available evidence or experiments;
- desired contribution;
- hard constraints and forbidden routes;
- author preference and risk tolerance.

Output:

- `OwnerNeedBrief` or `HumanNeedContract`.

## Layer 1 — Semantic contract

The main agent translates the human need into a bounded semantic contract.

Questions:

- What is the paper trying to make believable?
- What must not be claimed?
- What evidence exists?
- What reader is being served?
- What kind of publication object is expected?

Output candidates:

- `PaperControlSpine`;
- `OwnerDecisionQueue`;
- `ForbiddenRouteList`;
- `SuccessCriteria`.

This layer remains owner-gated when it changes core semantics.

## Layer 2 — Parallel analysis/design dimensions

These are not departments. They are dimensions that must be considered before serious writing.

### 2.1 Topic and contribution design

Purpose:

- locate the problem;
- define the contribution;
- separate novelty from implementation detail;
- distinguish central claim from secondary claim.

Outputs:

- `TopicAnalysis`;
- `ContributionMap`;
- `PaperSpineCandidate`.

### 2.2 Venue/template design

Purpose:

- identify target paper form;
- infer section functions;
- set volume, figure, table, algorithm, and citation budgets;
- avoid writing a paper in the wrong genre.

Outputs:

- `TemplateProfile`;
- `SectionFunctionBudget`;
- `FormalObjectBudget`.

### 2.3 Evidence and experiment design

Purpose:

- list available evidence;
- map evidence to claims;
- identify missing support;
- constrain claim strength.

Outputs:

- `EvidenceInventory`;
- `ExperimentResultInventory`;
- `ClaimEvidenceMatrix`;
- `EvidenceGapList`.

### 2.4 Reader and reviewer design

Purpose:

- predict what readers need to understand;
- predict reviewer objections;
- make section purposes explicit;
- prevent lab-notebook writing.

Outputs:

- `ReaderProfile`;
- `ReviewerConcernMap`;
- `ReviewerQuestionMap`.

### 2.5 Terminology and granularity design

Purpose:

- translate internal method names into reader-facing names;
- control conceptual load;
- decide where intuition, mechanism, evidence, insight, and limitation appear.

Outputs:

- `TerminologyRegister`;
- `CognitiveLoadBudget`;
- `ObjectRepresentationMatrix`;
- `ExplanationLadder`.

### 2.6 Rhetoric and organization design

Purpose:

- decide paragraph functions;
- define transitions;
- ensure section-to-section progression;
- prevent flat repetition.

Outputs:

- `RhetoricalMoveMatrix`;
- `CrossSectionDependencyMap`;
- `MainTextConstructionMatrix`.

### 2.7 Visual, table, algorithm, and formula design

Purpose:

- decide what deserves a figure/table/algorithm/formula;
- connect visual/formal objects to claims and reader questions;
- avoid decorative or redundant figures.

Outputs:

- `VisualFormalPlan`;
- `FigureContract`;
- `PanelEvidenceMap`;
- `CaptionBrief`.

### 2.8 Source and citation design

Purpose:

- align related work with contribution logic;
- ensure citations support the claims they are attached to;
- avoid citation dumping.

Outputs:

- `SourceMap`;
- `CitationSupportMatrix`;
- `RelatedWorkPositioning`.

## Layer 3 — Synthesis/control materials

Parallel dimensions converge into control materials that shape writing.

Important synthesis outputs:

- `PaperSpine` — the argument path of the paper;
- `ClaimBoundaryMap` — what may be claimed and how strongly;
- `ReviewerQuestionMap` — what must be answered;
- `ObjectRepresentationMatrix` — where objects appear and at what granularity;
- `MainTextConstructionMatrix` — section/unit writing instructions;
- `CrossSectionDependencyMap` — how sections depend on each other;
- `ClaimEvidenceVisibilityMap` — where claims become visible;
- `TerminologyRegister` — allowed reader-facing names;
- `VisualFormalPlan` — visual/formal object commitments.

These materials are the bridge between thinking and writing.

## Layer 4 — Writing task packets

The main agent converts control materials into bounded writing tasks.

A writing task is not “write the introduction.” It is:

```yaml
target_section:
target_unit:
mission:
input_materials:
required_moves:
forbidden_moves:
claim_strength_limits:
terminology_constraints:
validators:
expected_output:
```

This is the main Codex-compatible execution unit.

## Layer 5 — Paper-facing production modules

Writing produces concrete modules:

- abstract;
- introduction;
- related work;
- method;
- experiment setup;
- results;
- discussion;
- conclusion;
- figures;
- tables;
- algorithms;
- formulas;
- captions;
- supplements.

Each module must trace back to control materials.

## Layer 6 — Integration layer

Modules are integrated into a manuscript candidate.

Checks:

- Does Introduction promise what Method and Experiments actually deliver?
- Does Method introduce objects that Results use?
- Do Results produce insights rather than metric dumps?
- Does Discussion explain limits without weakening supported claims unnecessarily?
- Are figures, captions, and text mutually consistent?

Outputs:

- `FullManuscriptCandidate`;
- `NarrativeContinuityReport`;
- `ClaimConsistencyReport`;
- `TerminologyConsistencyReport`;
- `EvidenceCoverageReport`.

## Layer 7 — Multi-loss review

Review produces loss signals instead of directly rewriting the whole manuscript.

Loss dimensions:

- evidence loss;
- claim overreach loss;
- reader confusion loss;
- terminology leak loss;
- rhetorical organization loss;
- template mismatch loss;
- grammar/surface loss;
- visual/formal inconsistency loss;
- rendered export loss.

Outputs:

- `ReviewFinding`;
- `EvidenceReviewReport`;
- `ReaderExperienceReviewReport`;
- `RenderedSurfaceGateReport`.

## Layer 8 — Local backflow

The main agent classifies review findings and routes them to the nearest responsible upstream node.

Examples:

| Finding | Backflow target |
| --- | --- |
| grammar problem | section draft |
| terminology leak | terminology register |
| paragraph has no purpose | main text construction matrix |
| reader question unanswered | reviewer question map |
| overclaim | claim boundary / claim evidence visibility |
| evidence missing | claim evidence matrix / evidence inventory |
| wrong paper story | paper spine / owner decision |
| decorative figure | visual formal plan / figure contract |

The system should repair locally and regenerate only affected downstream nodes.

## Diagram

Editable source:

- [`docs/diagrams/human-need-to-paper-flow.drawio`](diagrams/human-need-to-paper-flow.drawio)

Preview/export files are generated when draw.io CLI is available.

## Design implication for PPG Runtime

The first product object should not be “a complete framework.” It should be this flow as a visible production map:

1. human need;
2. semantic contract;
3. analysis/design dimensions;
4. synthesis/control materials;
5. writing packets;
6. manuscript modules;
7. integration;
8. review losses;
9. local backflow.

The first concrete implementation slice should instantiate only a small part of this flow, but the full flow should guide what the slice is proving.
