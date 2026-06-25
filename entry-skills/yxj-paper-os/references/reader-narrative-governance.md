# Reader narrative governance — yxj-paper-os v2

This contract turns reader-facing paper quality into managed material objects.
It does not rewrite a specific manuscript by itself; it defines what later
writing, evidence, review, figure, and export tasks must consume and produce.

## Governance principle

Reader narrative is not free-form advice. If a task affects how the paper is
understood by readers or reviewers, the task must reference the relevant
narrative/template objects and explain how its output changes those objects or
uses them.

Expression design is now part of that same material-governance plane. A
paper-facing task must not draft manuscript prose, captions, review findings, or
export readiness directly from experiment logs, internal method ids, or generic
template advice. It must either consume the required expression-design objects
or record a validator-accepted non-applicable exception.

Expression-design objects refine the existing reader chain:

```text
ReviewerQuestionMap
  -> ObjectRepresentationMatrix
  -> MainTextConstructionMatrix
  -> CognitiveLoadBudget / ExplanationLadder / RhetoricalMoveMatrix
     / ClaimEvidenceVisibilityMap / TerminologyRegister
  -> section, figure/table/algorithm/formula, review, or export work
  -> ReaderSurfaceTutorReview / RenderedSurfaceGateReport
```

They do not replace evidence, template, or narrative governance. In task
packets, `expression_design_object_refs` is additive and must not replace
`narrative_object_refs`, `template_object_refs`, or `evidence_object_refs`.

## Required narrative and template objects

### ReviewerQuestionMap
Turns target-reader and reviewer expectations into explicit questions that the
abstract, introduction, method, experiments, results, discussion, figures, and
export surface must answer. It prevents writing tasks from starting with raw
experiment logs or internal method codes.

Minimum content:
- target reader and venue route;
- reviewer personas and their likely concerns;
- reader/reviewer questions with expected answer locations;
- section targets and required objects;
- risk tags such as lab-notebook smell, unsupported claim, internal-code leak,
  and claim-boundary overreach;
- downstream consumers, especially `MainTextConstructionMatrix`, section-writing,
  review, and rendered-surface gates.

### MainTextConstructionMatrix
Translates reader questions, template rules, evidence anchors, and object
representation requirements into section-level writing instructions. It is the
construction bridge between planning materials and manuscript prose.

Each row should declare:
- section and manuscript unit;
- linked reviewer/reader question;
- object representation form and forbidden forms;
- granularity expected at that location: intuition, contract, mechanism,
  evidence, insight, or boundary;
- evidence anchor or explicit accepted non-applicable reason;
- template rule consumed from exemplar analysis;
- surface rule that prevents raw internal codes, snake_case constraints, raw
  method ids, bare citekeys, and defensive claim walls;
- final text checks required before a writing task can report completion.

### ReaderSpineBrief
Defines the reader problem, paper spine, contribution visibility, section
question sequence, reviewer expectations, and unresolved owner semantic
decisions.

Minimum content:
- target reader and venue route;
- one-sentence paper spine;
- section-by-section reader question sequence;
- contribution claims and evidence boundaries;
- reviewer objections that the paper must preempt;
- owner-gated semantic decisions.

### ObjectRepresentationMatrix
Tracks how major objects appear across the paper and at what granularity.
Typical rows include scenario, problem, method, contribution, evidence,
experiment, baseline, ablation, result, limitation, and future work.

For each section, record:
- representation form: phrase, paragraph, running example, definition, figure,
  table, algorithm, formula, metric, caveat, or reviewer-facing transition;
- granularity: intuition, operational definition, mechanism, evidence, insight,
  or boundary;
- required evidence/source anchors;
- downstream tasks that consume this representation.

### TemplateQuantProfile
Captures target-journal/exemplar structure as quantitative and functional
constraints, not copied prose.

Minimum content:
- exemplar/source manifest and allowed-use boundary;
- section function distribution;
- paragraph/volume ranges where known;
- figure/table/algorithm/formula budget;
- baseline/ablation/experiment/result ordering patterns;
- target-manuscript gap audit.

### SectionFunctionBudget
Maps each section to rhetorical function, expected objects, volume/budget,
required figures/tables/formal elements, and validation rules.

### VisualTableAlgorithmFormulaBudget
Explains why each planned visual/formal object exists, which claim it supports,
which section consumes it, and what evidence or source anchors it requires.

### CognitiveLoadBudget
Defines how much conceptual, formal, metric, terminology, and claim-boundary
load each reader-facing unit may carry. It prevents abstracts, introductions,
method overviews, results paragraphs, captions, and exports from becoming raw
object dumps.

Minimum content:
- section or surface id;
- linked reader/reviewer question;
- allowed granularity and maximum new terms/formal objects;
- required progression, such as intuition before mechanism or evidence before
  claim;
- forbidden overload patterns, including raw logs, snake_case constraints,
  internal method ids, and metric dumps;
- downstream writing/review/export tasks that must consume the budget.

### ExplanationLadder
Records how a reader should climb from intuition to mechanism, evidence, and
bounded claim. It rejects direct jumps from raw formalism or internal ids to
final claims.

Minimum content:
- object id and linked reader question;
- ordered stages: intuition, mechanism, evidence, bounded claim, or an explicit
  accepted variant;
- allowed inputs and forbidden shortcuts at each stage;
- final-text checks proving the stage order survived drafting.

### RhetoricalMoveMatrix
Maps reader question, object, granularity, evidence anchor, planned text move,
and final text check for each paper-facing unit.

Minimum content:
- section/surface and manuscript unit;
- reader question;
- object id and representation granularity;
- evidence anchor or validator-accepted non-applicable reason;
- planned rhetorical move and forbidden moves;
- final text checks consumed by writing, review, and rendered-surface gates.

### ClaimEvidenceVisibilityMap
Controls where claims become visible to readers and which evidence/method object
allows that strength. It is a visibility and wording control, not a truth
promotion mechanism.

Rules:
- it may reference Evidence & Method objects, claim-citation capsules, result
  packages, and method contracts;
- it cannot independently upgrade claim strength;
- every visible claim needs allowed strength, support location, required
  limitation/boundary visibility, and forbidden wording;
- unsupported or over-strength wording routes to review/backflow.

### TerminologyRegister
Translates internal method ids, scenario families, constraints, run labels, and
snake_case fields into reader-facing language before prose or rendered exports
close.

Minimum content:
- internal forms and reader-facing labels;
- allowed and forbidden surfaces;
- replacement rules for main prose, tables, supplements, and provenance traces;
- rendered-output checks that catch raw identifiers and unrendered placeholders.

### ExpressionDesignBundle
An optional compact bundle may index the five expression-design objects for a
task, but it is only a manifest. It cannot bypass independent typed-object
validators for `CognitiveLoadBudget`, `ExplanationLadder`,
`RhetoricalMoveMatrix`, `ClaimEvidenceVisibilityMap`, or
`TerminologyRegister`.

### ReaderExperienceReviewReport
Independent review artifact that checks:
- whether the draft reads like a lab notebook;
- whether section transitions answer reader questions;
- whether objects appear at appropriate granularity;
- whether baselines/ablations are narrated as argument, not just results;
- whether figures/tables/algorithms/formulas serve the paper spine;
- which `NarrativeBackflowTask` owns each accepted finding.

### NarrativeBackflowTask
Routes narrative/reviewer findings back to the responsible department and lane.
Every accepted lab-notebook-smell or reader-confusion finding needs a backflow
owner, expected output, validator refs, and state-ingestion plan.

## Granularity progression rule

The same object should not be repeated at one flat level throughout the paper.
A normal progression is:

`motivation intuition -> problem contract -> method mechanism -> experiment evidence -> result insight -> limitation boundary`

`ReviewerQuestionMap` records why the reader needs the object. `ObjectRepresentationMatrix`
records how the object appears. `MainTextConstructionMatrix` records the exact
section/unit representation form and granularity. A writing task may not flatten
these layers into one generic paragraph plan.

The ObjectRepresentationMatrix records exceptions when a paper deliberately uses
a different order; the MainTextConstructionMatrix must then name the exception
and the validator/backflow route that accepts it.

## Lab-notebook-smell gate

A manuscript-facing task is suspicious when it primarily lists scenarios,
experiments, baselines, metrics, or ablations without explaining the reader
question, mechanism, comparison stance, or section transition. Such findings are
not automatically blockers, but accepted findings must route to a
`NarrativeBackflowTask` and cannot be hidden inside prose.

## Boundary

The governance objects shape future writing and review tasks. They do not let the
manager invent paper-owner semantic claims, target-venue commitments, or evidence
strength beyond sources and owner decisions.

`ClaimEvidenceVisibilityMap` is bound by the same rule: it may reduce, stage, or
surface an evidence-supported claim, but it cannot raise claim strength beyond
Evidence & Method support.

## Reader-facing surface translator gate

Template analysis and reader-spine objects are not allowed to pass directly into
main manuscript prose as internal planning language. A manuscript-facing task
must translate internal governance, experiment, method, and export objects into
reader-facing language before it can be reported as complete.

This gate is owned by `reader_narrative_governance` and consumed by manuscript
execution, review backflow, figures, and export validation.

### MainTextSurfaceRules

Create or consume a `MainTextSurfaceRules`/reader-surface artifact when a task
rewrites abstracts, introductions, method sections, experiments, results,
discussion, captions, or rendered exports.

Minimum checks:
- internal family codes such as `S0/S1/S3/S4/S5` must be translated to reader
  family names in main prose; code-like family ids may remain only in tables,
  supplements, or provenance artifacts where explicitly needed;
- snake_case implementation fields, constraint identifiers, and trace internals
  must be translated into natural-language method descriptions in main prose;
- raw method ids such as `VG-KZTR_full`, `B2_*`, or `no_*` must be translated to
  reader labels such as "full VG-KZTR", "majority voting", or "no action-gate
  ablation";
- claim boundaries must be stated as scope and future-work logic, not as a
  defensive wall of "not X, not Y" disclaimers;
- rendered PDFs must not expose raw citekeys or internal renderer placeholders;
  citations should render through the target bibliography pipeline;
- figures and captions included in the main export must use reader-facing labels
  even when the underlying data source uses internal ids.

### Rendered-output validation

A manuscript/export task is not complete if only markdown/source files are
reviewed. The final rendered artifact must be checked for reader-surface leaks,
including raw citekeys, internal scenario codes, snake_case constraints,
raw method ids, and defensive claim-boundary walls.

Recommended narrative-construction validator names:
- `validate_reviewer_question_map`
- `validate_main_text_construction_matrix_refs`
- `validate_expression_design_object_binding`
- `validate_cognitive_load_budget`
- `validate_explanation_ladder`
- `validate_rhetorical_move_matrix`
- `validate_claim_evidence_visibility_map`
- `validate_terminology_register`

Recommended surface validator names:
- `validate_no_internal_codes_in_main_prose`
- `validate_no_snake_case_constraints_in_main_prose`
- `validate_no_raw_method_ids_in_main_prose`
- `validate_no_defensive_claim_boundary_wall`
- `validate_no_bare_citekeys_in_export`
- `validate_rendered_pdf_surface_text`
- `validate_cognitive_load_budget_consumed`
- `validate_rhetorical_move_matrix_consumed`
- `validate_explanation_ladder_progression`
- `validate_claim_evidence_visibility`
- `validate_terminology_register_surface`
