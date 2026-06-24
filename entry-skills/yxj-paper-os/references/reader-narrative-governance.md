# Reader narrative governance — yxj-paper-os v2

This contract turns reader-facing paper quality into managed material objects.
It does not rewrite a specific manuscript by itself; it defines what later
writing, evidence, review, figure, and export tasks must consume and produce.

## Governance principle

Reader narrative is not free-form advice. If a task affects how the paper is
understood by readers or reviewers, the task must reference the relevant
narrative/template objects and explain how its output changes those objects or
uses them.

## Required narrative and template objects

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

The ObjectRepresentationMatrix records exceptions when a paper deliberately uses
a different order.

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

Recommended validator names:
- `validate_no_internal_codes_in_main_prose`
- `validate_no_snake_case_constraints_in_main_prose`
- `validate_no_raw_method_ids_in_main_prose`
- `validate_no_defensive_claim_boundary_wall`
- `validate_no_bare_citekeys_in_export`
- `validate_rendered_pdf_surface_text`

