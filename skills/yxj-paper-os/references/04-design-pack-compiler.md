# Playbook 04 — Design Pack Compiler

Use this playbook only when compiling or validating `04_WRITING_DESIGN_PACK.md`, or when D00/D02/D19 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, question-depth, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is the central internal rubric/reference. The central rubric decides sufficiency and question-depth; this file is not a sixth task playbook and not a public workspace file. This playbook translates the current rubric gaps into compact question cards and write landings; it must not duplicate or override the central D00-D19 ladder.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D00 | `Workspace metadata` | `00_DIMENSION_INDEX.md#Workspace Metadata` |
| D02 | `Stale/readiness flags` | `00_DIMENSION_INDEX.md#Dimension Status Index` + `#Readiness Gate` |
| D19 | `Writing design pack` | `04_WRITING_DESIGN_PACK.md` |

After compiling, update D00/D02/D19 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Question-depth translator guide

Use the central rubric to judge whether D00/D02/D19 are missing, minimum-only, standard-ready, deferred, or rejected. Use this table only to translate that gate state into the next compact card; do not add public files, D IDs, index columns/statuses, manuscript prose, citations, sources, results, evidence anchors, external skill execution, semantic scoring, or runtime orchestration.

| D ID(s) | Default card mode | Ask a depth follow-up when... | Reconcile or conflict-check when... | Write landing |
|---|---|---|---|---|
| D00 | `focused-question` only when identity/provenance is ambiguous | provenance, owner/project identity, source revision, or intake-change notes could prevent a wrong-project or stale handoff | D00 freshness conflicts with D02 stale state or D19 validation notes | `00_DIMENSION_INDEX.md#Workspace Metadata`, then D00 row |
| D02 | `stale-alert` | a changed upstream dimension could make a reused pack section misleading without a recompile or owner-accepted risk note | current upstream content conflicts with D19 timestamp/content, route decisions, or critical-standard rows | `00_DIMENSION_INDEX.md#Readiness Gate` and D02 row |
| D19 | `focused-question` for one missing handoff; `reconciliation` for conflicts; `stale-alert` for outdated packs | an unresolved owner, evidence, source, visual, wording, stale, or handoff boundary must be surfaced before downstream use | critical-standard gaps, placeholders, D02 state, D16/D17 conflicts, or owner-gated assumptions contradict compile readiness | `04_WRITING_DESIGN_PACK.md` coverage/validation/handoff sections, then D19 row |

## Program-mode evaluator action

Use the canonical evaluator states and breakpoint card in `SKILL.md`; this compiler playbook only supplies D00/D02/D19 write landings. Auto-fill mechanical D19 coverage and validation notes only after upstream dimensions are handled. If a compile blocker is owner-gated, conflicting, stale, or D07 is falsely marked `filled` without supplied source detail, emit one breakpoint card naming the write target and resume action instead of compiling.

## First-batch D19/D02 handoff pointers

`00-dimension-rubric.md` remains the source of truth for D00/D02/D19 sufficiency. This compiler playbook should only apply focused compile and stale-gate cards:

- D19 is a structural handoff/submission blueprint plus semantic-risk note. It may summarize dimension coverage, submission blueprint, statement inventory, supplement boundary, external handoff routes, unresolved dimension consequences, and validation notes.
- D19 must not claim manuscript readiness, submission readiness, publication readiness, acceptance likelihood, novelty, citation truth, prose quality, visual quality, or semantic adequacy.
- D19 must include a final handoff card that distinguishes structural writing-planning readiness from final citations, manuscript-ready prose, submission, publication, acceptance, semantic adequacy, and downstream skill execution.
- D02 stale gate should name category-family intent for changed dimension, affected pack section, stale since, recompile required, owner decision, required action, and semantic risk note when a prior design pack may be reused.
- A fresh D00/D02 state does not prove semantic adequacy. It only proves the metadata/stale decision was structurally handled.
- Mechanical checks may inspect coverage, status/pointer consistency, stale/D19 incompatibility when explicitly structured, and placeholder absence; they must not execute external writing/citation/figure skills or score semantic quality.

## Second-batch D19 handoff additions

Use these additions to compile planning signals from existing sections into the design pack. They describe handoff packets and matrix seeds; they do not add public workspace files, public index columns, runtime orchestration, semantic scoring, external execution, or manuscript drafting.

- **Front matter / hook packet:** summarize route-facing title/abstract/keyword/hook constraints, allowed/forbidden promise level, visual-hook status, and unresolved owner decisions. Do not draft front matter or hook copy.
- **Intro / related / citation-function packet:** summarize supplied source roles, dossier boundaries, gap/context/counterevidence handoff, and claim/evidence dependencies. Do not search citations, complete BibTeX, or treat source roles as claim support.
- **Method / reporting / reproducibility packet:** summarize checklist state for method artifacts, code/data/baseline/metric availability, supplement/statement needs, unresolved reporting risks, and forbidden reproducibility promises.
- **Results / visual / caption / table / accessibility packet:** summarize result/figure/table storyline, caption/legend/table jobs, statistics-display notes, accessibility constraints, non-visual fallback, and any visual-dependent claim risk.
- **Downstream route matrix:** list recommended downstream route category, required input sections, owner-gated facts still needed, forbidden actions, and whether the route is ready, deferred, absent, or rejected. Recommendations are handoff notes only.
- **Templates / validator handoff:** state which template/design-pack sections should receive each packet and which validation expectations are mechanical only, such as section presence, non-placeholder pointers, and stale/route consistency.

## Template Quantification Gate compile rule

D19 valid handoff is hard-blocked by the Template Quantification Gate. The canonical `04_WRITING_DESIGN_PACK.md#Quantification Gate Status` table must be mechanically consistent: Gate applies yes requires count >= 3, Source/similarity rationale present yes (source/similarity rationale), Quantitative outputs status present, Blocker propagation clear, and D19 pack status valid. If any required field fails, D19 pack status must be blocked and the handoff must carry blocked-not-valid-handoff.

Gate no/not_applicable requires a non-empty trigger/no-template rationale and must not claim route-style adequacy. This compiler does no semantic scoring, no extraction tooling, no yxj-backend integration, no downstream execution, no public schema expansion, and no hardcoded journal thresholds.

## Inputs

Read these files first:

- `00_DIMENSION_INDEX.md`
- `00_PROJECT_ROUTE.md`
- `01_MATERIALS_INVENTORY.md`
- `02_CLAIM_EVIDENCE_BOUNDARY.md`
- `03_WRITING_STRUCTURE.md`

## Compile only if clear

Do not compile the final design pack when any hard blocker remains:

- unhandled D00-D19 dimension row;
- invalid status, reason, pointer/handoff, or `Blocks design pack?` value in `00_DIMENSION_INDEX.md`;
- project route;
- core materials;
- core contribution;
- claim-evidence boundary;
- writing structure;
- external route.

If blocked, report the missing blocker or dimension ID and ask the next focused question instead.

## Compile decision table

Use this table before creating or updating `04_WRITING_DESIGN_PACK.md`.

| Condition | Result |
|---|---|
| D00-D19 missing from `00_DIMENSION_INDEX.md` | Block; repair the index before content compilation. |
| Invalid status or placeholder reason/pointer/handoff | Block; ask or repair the relevant row. |
| Non-critical dimension reaches minimum with explicit reason/handoff | May pass that dimension. |
| Critical-standard dimension only reaches minimum | Continue asking; do not compile final design pack. |
| Owner-gated route/claim/evidence/source/forbidden wording unconfirmed | Keep as candidate/deferred; do not mark standard/filled. |
| Agent-designable structure is grounded in confirmed material and rationale | May propose and mark standard when the write target records the rationale. |
| D16/D17 primary and claim-side statements conflict | Block and ask a reconciliation card. |
| D04 route deferred | Continue upstream intake, but final pack requires owner-confirmed route or explicit final-route deferral acceptance. |
| D18 no visuals | Pass only with no-visual rationale, alternative storyline, and no active visual-dependent claim. |
| Final pack contains TODO/TBD/UNKNOWN/REPLACE_ME | Invalid; do not hand off. |
| External writing/citation skill not executed | Not blocking; this plugin only recommends handoff and does not execute external skills. |
| Six-track handoff packet missing or unresolved | Block only if the corresponding upstream dimension is readiness-critical and unhandled; otherwise record absent/deferred/rejected consequence. |
| Downstream route matrix includes execution language | Invalid; rewrite as recommendation/constraint only and do not run the route. |
| Template/validator handoff claims semantic adequacy | Invalid; validators are mechanical and final pack must state unresolved semantic risks rather than scoring them. |

`Blocks design pack? = yes` means the dimension is readiness-critical if unhandled. It does not mean the row is currently blocking after it has a valid handled status, reason, and pointer/handoff.

## D16/D17 canonical write rule

- D16 primary pointer normally lives in `03_WRITING_STRUCTURE.md#Object Granularity`.
- D17 primary pointer normally lives in `03_WRITING_STRUCTURE.md#Surface Control`.
- Claim-side D16/D17 details may live in `02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity`, `#Allowed Wording`, and `#Forbidden Wording`.
- If primary and claim-side statements conflict, block compilation and ask a `reconciliation` question card before writing the final design pack.

## Question card pattern

Use this card when D00/D02/D19 or the `external-route` / final handoff blocker is unresolved.

```text
Current stage: Handoff
Dimension / blocker: D00/D02/D19 / design-pack compile gate
Why this matters: the final design pack must be current, placeholder-free, and bounded before downstream writing tools use it.
Mode chosen: stale-alert for changed upstream material; focused-question for one missing handoff route; reconciliation if compile inputs conflict.
Question: What should happen before final handoff?
Options:
A. compile now — only if every D00-D19 row is handled and critical-standard dimensions are standard.
B. recompile after stale change — update D02 and regenerate D19 from current upstream files.
C. defer handoff — record the missing blocker and ask the next focused question instead of compiling.
D. invalid final pack — if TODO/TBD/UNKNOWN/REPLACE_ME remains, mark D19 deferred and repair the source section.
E. external route only — record the recommended downstream writing/figure/citation/review route without executing it.
Agent action after answer: update 00_DIMENSION_INDEX.md#Readiness Gate and 04_WRITING_DESIGN_PACK.md only when the compile decision table passes.
```

## Second-batch question-card seeds

Use these cards only after upstream playbooks have produced enough handled input or explicit absence/defer/reject decisions. If a card exposes missing route, material, source, claim, evidence, wording, or visual facts, return to the owning playbook.

### Six-track handoff completeness

```text
Current stage: Handoff
Dimension / blocker: D00/D02/D19 with D04/D07/D08/D10-D18 / six-track handoff completeness
Why this matters: the design pack must expose planning constraints for all six writing-surface tracks before downstream tools use it.
Mode chosen: reconciliation when upstream packets conflict; focused-question when one packet needs an owner decision; stale-alert when a prior pack may be outdated.
Question: Which six-track handoff packet should I compile, defer, or mark absent?
Options:
A. front matter / hook packet — compile constraints and forbidden promises only; do not draft title, abstract, keywords, or hook copy.
B. intro / related / citation-function packet — compile source-role and claim-boundary handoff without searching or inventing citations.
C. method / reporting / reproducibility packet — compile checklist state, artifact locations, and forbidden reproducibility promises.
D. results / visual / caption / table / accessibility packet — compile storyline, caption/table/accessibility jobs, and visual-dependent claim risks.
E. unresolved packet — mark absent/deferred/rejected with consequence and keep final handoff cautious or blocked as the dimension rules require.
Agent action after answer: update 04_WRITING_DESIGN_PACK.md under existing relevant sections and D19 in 00_DIMENSION_INDEX.md; update D02 if upstream material changed after the prior pack.
```

### Downstream route matrix

```text
Current stage: Handoff
Dimension / blocker: D01/D02/D07/D08/D18/D19 / downstream route matrix
Why this matters: downstream writing, citation, figure, and review tools need route recommendations, required inputs, and forbidden actions without being executed by this plugin.
Mode chosen: focused-question when owner must choose or reject a route; candidate-confirmation when upstream files already imply safe candidates.
Question: Which downstream route-matrix row should I record?
Options:
A. writing/polishing route — record route category, required design-pack sections, owner-gated facts, and forbidden drafting scope.
B. citation/source route — record supplied-source needs and citation-function constraints without search, BibTeX completion, or citation-truth claims.
C. figure/caption/accessibility route — record visual assets, caption/table jobs, accessibility handoff, and missing evidence boundaries without creating visuals.
D. validation/review route — record structural validator or reviewer handoff expectations without semantic scoring or acceptance prediction.
E. rejected/deferred route — record why the route must not run or is not ready.
Agent action after answer: update 04_WRITING_DESIGN_PACK.md#External Skill Handoff or equivalent D19 handoff section and update D19/D02 rows in 00_DIMENSION_INDEX.md.
```

### Templates / validator handoff

```text
Current stage: Handoff
Dimension / blocker: D00/D02/D19 / templates-validator handoff
Why this matters: templates and validators should receive structural expectations only, so downstream users do not mistake a valid pack for semantic paper readiness.
Mode chosen: focused-question when one structural expectation is missing; reconciliation if template wording conflicts with validator meaning.
Question: Which template or validator handoff expectation should be recorded?
Options:
A. section/table presence expectation — record the required design-pack section or table pointer and non-placeholder rule.
B. stale/route consistency expectation — record when D02 requires recompile or owner-accepted risk.
C. unresolved-risk expectation — record semantic-risk, source-risk, visual-risk, or reporting-risk notes for downstream tools.
D. deferred validator coverage — record that mechanical checks are unavailable or not yet implemented, with a manual review handoff.
E. rejected semantic promise — remove or forbid any wording that suggests validators prove novelty, citation truth, venue fit, prose quality, or acceptance.
Agent action after answer: update 04_WRITING_DESIGN_PACK.md#Validation Notes and D19/D02 pointers; do not change public index columns or execute external tools.
```

## Required design-pack sections

`04_WRITING_DESIGN_PACK.md` must include:

- Dimension Coverage Summary;
- Six-Track Coverage;
- Project Route;
- Front-Matter / Hook Planning Handoff;
- Introduction / Related-Work / Citation Function Handoff;
- Method / Reporting / Reproducibility Handoff;
- Results / Visual / Captions / Tables / Accessibility Handoff;
- Material Boundary;
- Source / Citation Boundary;
- Research Dossier Notes;
- Core Contribution;
- Claim-Evidence Map, including support status;
- Allowed Wording;
- Forbidden Wording;
- Limitations and Risks;
- Reader Spine;
- Writing Structure;
- Visual and Figure Storyline;
- Downstream Route Matrix;
- D02 Stale Gate;
- External Skill Handoff;
- Template and Mechanical Validator Notes;
- Validation Notes.

## External handoff

Recommend a downstream route only as guidance. Do not execute external skills.

Examples:

- Nature-style writing/polishing route when venue and tone justify it.
- ML/CV/NLP/algorithm writing route for computer-science method papers.
- Generic scientific-writing route when no specialized route is known.

## Index update examples

- Ready design pack: `D19 | filled | design pack compiled after all dimensions handled | 04_WRITING_DESIGN_PACK.md#Dimension Coverage Summary | yes`.
- Stale downstream pack: `D02 | deferred | material/claim dimension changed after pack compile | Handoff: recompile design pack before writing | yes`.

## Validation meaning

A passing validator means the design pack is structurally valid against the six-file/20-dimension contract. It does not prove semantic adequacy or manuscript quality.

## Do not assume

- Do not fill unresolved fields with TODO in the final design pack.
- Do not turn deferred claims into supported claims.
- Do not omit limitations that constrain wording.
- Do not execute downstream writing or citation skills.
