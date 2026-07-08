# Dimension Rubric — Central Internal Reference

This is a central internal rubric/reference for `yxj-paper-os`. It is not a public skill, not a sixth task playbook, and not a public workspace file.

Use it when judging D00-D19 sufficiency, deciding whether to ask another focused question, marking a dimension handled, or deciding whether `04_WRITING_DESIGN_PACK.md` can be compiled.

## Global tier rules

- `minimum`: enough to avoid blank/TODO and know whether the dimension is `filled`, `not_applicable`, `absent`, `deferred`, or `rejected`.
- `standard`: enough for reliable downstream design-pack handoff.
- `ideal`: richer optional material that improves writing quality but does not block by default.

Tier judgment is internal. Do not add `minimum`, `standard`, `ideal`, or `tier` columns/statuses to `00_DIMENSION_INDEX.md`. Express the result through the existing `Status`, `Reason / owner note`, and `Pointer or handoff` fields.

## Critical-standard dimensions

The exact dimensions that must reach `standard` before final design-pack compilation are:

```text
D04,D05,D06,D10,D11,D12,D13,D14,D15,D16,D17,D18
```

Non-critical dimensions still require at least `minimum` handling. They are not optional. `Blocks design pack?` keeps its existing meaning: readiness-critical if unhandled; it is not the same as the standard-required set. `ideal` never blocks.

## Mixed confirmation rules

- Owner-gated facts, route decisions, contribution choices, claims, evidence anchors, source/citation facts, and forbidden routes require owner confirmation before final `filled`/standard handling.
- Agent-designable structural dimensions may be proposed and marked standard when grounded in confirmed upstream material and with rationale.
- If user confirmation is still needed, keep the content as candidate/deferred rather than final.
- Never invent experiments, results, sources, citations, figures, claims, or owner decisions.

## Program guardrail boundary

In program-mode, the public workspace schema still does not change: no new D IDs, files, public status values, public tier columns, or public readiness columns. Use the existing `Status`, `Reason / owner note`, `Pointer or handoff`, and `Blocks design pack?` fields to express the internal judgment.

- Agent-auto-fill is limited to mechanical metadata, observed stale/file-state notes, and agent-designable structure grounded in confirmed upstream material.
- Owner-gated route decisions, source/citation facts, claim selection, evidence anchors, support strength, forbidden wording, stale-risk acceptance, and final-route choices require owner confirmation or an explicit absence/defer/reject handoff.
- D07 false-completion rule: if D07 is `filled`, `01_MATERIALS_INVENTORY.md#Source and Citation Bank` must contain supplied source/citation detail; if no source detail is supplied, D07 should be `absent` or `deferred` with a no-invention handoff.
- D19 final handoff must say that a valid pack is ready for downstream writing planning from `04_WRITING_DESIGN_PACK.md` only, and is not final-citation, manuscript-prose, submission, publication, acceptance, or semantic-adequacy approval.
- Mechanical gates may check structure, status/text consistency, pointers, placeholders, D07 filled/absence consistency, final-handoff boundary text, stale carry-through, and forbidden execution/readiness language only.

## Question-card interpretation

The rubric decides what is missing; the playbooks decide how to ask. Use question cards to translate the missing rubric field into one answerable user choice. Prefer:

- `focused-question` for owner-gated route, contribution, claim, evidence, source, or forbidden-wording decisions;
- `quick-form` for empty workspaces with several low-risk material/metadata fields;
- `candidate-confirmation` when the agent can propose options from confirmed upstream material;
- `reconciliation` when D16/D17 or other cross-file statements conflict;
- `stale-alert` when D02 indicates the downstream design pack may be stale.

`standard` means the answer is operational enough for downstream writing to act without guessing. It does not require ideal background research, manuscript prose, citation search, or external skill execution.


## First-batch boundary rules

Use this first-batch guidance for D04, D07, D08, D09, D14, D15, D18, D19, D00, and D02. The central rubric is the source of truth; task playbooks should contain only focused cards or pointers.

- `source ≠ evidence ≠ claim`: D07 source records and D08 dossier notes cannot strengthen D11 claims unless a D06 evidence anchor and D11 support relation exist.
- `route ≠ audience expectation`: D04 separates owner-confirmed route/profile from agent-inferred reviewer questions and route risks.
- `exemplar style ≠ citation source`: D09 may guide language fingerprint; if an exemplar is cited or used as a source, handle it under D07.
- `visual plan ≠ evidence artifact`: D18 planned, needed, deferred, or absent visuals cannot support active claims unless actual evidence exists in D06 and the claim mapping exists in D11.
- `design pack ≠ manuscript prose`: D19 is a structural handoff and submission blueprint with risk notes, not manuscript, submission, publication, or acceptance readiness.
- `metadata/staleness ≠ semantic adequacy`: D00/D02 freshness and completeness checks do not prove claim truth, source truth, novelty, prose quality, visual quality, or manuscript adequacy.
- Mechanical gates may check structure, presence, explicit absence/defer reasons, cross-reference consistency, status values, and placeholder absence only. They must not judge venue fit, novelty, source authority, citation truth, argument persuasiveness, style similarity, visual correctness, or readiness for submission.

## Six-track writing-surface crosswalk

This second-batch crosswalk is internal planning guidance. It maps writing-surface needs into the existing D00-D19 dimensions, five content homes, and D19 handoff. It does not create public dimensions, public files, public status values, public track columns, or a separate user-facing workflow.

Tier internal-only rule: `minimum`, `standard`, and `ideal` remain rubric judgments only. When a track affects `00_DIMENSION_INDEX.md`, express it through the existing `Status`, `Reason / owner note`, `Pointer or handoff`, and `Blocks design pack?` fields using only `filled`, `not_applicable`, `absent`, `deferred`, or `rejected`.

| Track | Primary dimensions | Primary internal homes | Internal field families | Mechanical gate intent | Boundary |
|---|---|---|---|---|---|
| Front matter / hook | D04, D09, D12, D14, D15, D18, D19; secondary D01/D03 | `00_PROJECT_ROUTE.md`, `03_WRITING_STRUCTURE.md`, `04_WRITING_DESIGN_PACK.md` | Route/title/abstract/keyword constraints; owner-gated front-matter inputs; hook purpose; visual-hook status; exemplar/style constraints; allowed/forbidden surface terms; section/job implications; handoff notes | Check that front-matter and hook planning rows have owner-confirmed, deferred, absent, or rejected state; check route/structure/visual links are present; check planned hook material is not treated as completed evidence | Planning constraints only; no draft-ready title, abstract, keyword, graphical-hook, or caption copy |
| Intro-related / citation function | D07, D08, D10, D11, D13, D14; secondary D04/D15/D19 | `01_MATERIALS_INVENTORY.md`, `02_CLAIM_EVIDENCE_BOUNDARY.md`, `03_WRITING_STRUCTURE.md`, `04_WRITING_DESIGN_PACK.md` | Source role; citation function such as background/gap/contrast/benchmark/method lineage/limitation/counterpoint; related-work move; gap or problem claim; claim-to-evidence link; unresolved source need; counterevidence/risk note | Check source/function buckets, owner/source status, D06 evidence anchor dependency, D11 claim mapping dependency, and explicit unresolved-source consequences | Source notes and citation functions do not create support; no new source facts, no new reference entries, and no novelty or authority judgment |
| Method / reporting / repro | D04, D05, D06, D13, D15, D19; secondary D02 | `00_PROJECT_ROUTE.md`, `01_MATERIALS_INVENTORY.md`, `03_WRITING_STRUCTURE.md`, `04_WRITING_DESIGN_PACK.md` | Method object/component; reporting guideline or statement need; data/code/artifact availability state; implementation-detail location; protocol/parameter boundary; baseline/metric material state; reproducibility gap; limitation and risk note | Check locatable material or explicit absence/defer consequence; check method/reporting facts trace to D05/D06 or owner confirmation; check D19 statement inventory and unresolved-risk notes | Do not create method facts, data, code, baselines, metrics, or outcome values |
| Results / visual / captions / tables / accessibility | D05, D06, D11, D12, D13, D14, D15, D18, D19 | `01_MATERIALS_INVENTORY.md`, `02_CLAIM_EVIDENCE_BOUNDARY.md`, `03_WRITING_STRUCTURE.md`, `04_WRITING_DESIGN_PACK.md` | Result artifact; table/figure id; visual status such as existing/needed/deferred/absent; caption job; legend job; table role; statistic-display note; accessibility or alt-text need; linked claim/evidence/reader step; overclaim boundary | Check existing/needed/deferred/absent status and rationale; check every active result/visual claim has D06/D11 support; check needed/deferred visuals are not used as active evidence; check caption/table/accessibility items are handoff constraints | No new results, no invented visual/table facts, and no caption/table text used as evidence |
| Downstream route matrix | D01, D02, D07, D08, D18, D19; references all critical-standard dimensions | `04_WRITING_DESIGN_PACK.md` plus source sections that feed D19 | Route candidate; input pack section; allowed handoff scope; blocked or deferred action; source/evidence/visual boundary; stale-risk note; owner decision; unresolved dimension consequence | Check route rows are recommendations/handoff constraints only; check no row claims a downstream action already happened; check D19 compiles only after D00-D18 handling and stale-gate resolution or explicit owner risk note | Handoff planning only; no automatic downstream action, acceptance prediction, or readiness certification |
| Templates / validators | D00-D19 contract | Existing six templates, `verify_dimension_rubric.py`, `verify_design_pack.py`, and test fixtures | Template section/table presence; D00-D19 coverage; public status set; pointer/handoff reasons; placeholder rejection; public-schema guard; cross-reference presence; forbidden-promise scan | Check structure, headings, columns, statuses, non-placeholder values, pointers, and explicit absence/defer reasons; keep checks mechanical and actionable | Do not add public files, index columns, public status values, or scholarly-quality scoring |

### Internal field-family routing notes

- Front matter / hook fields normally start in D04 route constraints, flow through D14/D15 structure jobs and D18 visual-hook state, and surface in D19 as constraints and handoff notes only.
- Intro-related / citation function fields normally start in D07/D08 source and dossier records, become claim/gap boundaries through D10/D11/D13, and shape D14 reader moves without bypassing evidence anchors.
- Method / reporting / repro fields normally start as D04 route/reporting implications and D05/D06 material locations, then become D15 section jobs and D19 statement or reproducibility notes.
- Results / visual / captions / tables / accessibility fields normally start as D05/D06 materials, become D11/D12/D13 claim and wording boundaries, then become D18 visual/table plans and D19 handoff constraints.
- Downstream route matrix fields belong to D19 but must preserve D01 owner decisions, D02 stale state, D07/D08 source boundaries, and D18 visual boundaries.
- Templates / validators fields are structure checks for existing files only; they are not paper-quality judgments and do not alter the D00-D19 identity set.

## Template Quantification Gate

Template Quantification Gate is a standard design-pack gate, not decoration. When D04 records a target route, article type, owner-provided templates, or template expectation, D19 valid handoff requires at least 3 parseable full-text templates, source/similarity rationale, and quantitative writing-design outputs. Citation-only, abstract-only, metadata-only, missing, or unparseable records do not count. If the owner cannot supply enough parseable full text, the agent must ask for the missing materials and keep D19 as blocked-not-valid-handoff.

The gate is mechanical and structural: it checks recorded applicability, parseable-template count, source/similarity rationale presence, output-status presence, and blocker propagation. Its explicit non-goals are no semantic scoring, no extraction tooling, no yxj-backend integration, no downstream execution, no public schema expansion, and no hardcoded journal thresholds. It must not judge venue fit, prose quality, style similarity, visual correctness, source authority, citation truth, novelty, or manuscript readiness.

Template statistics guide writing design only. They can inform D09 exemplar language profile, D15 manuscript outline, D17 surface control, D18 visual plan, and D19 current-design comparison; they are not D06 claim evidence and cannot strengthen D11 claims without separately promoted evidence anchors.

Gate-specific landing expectations:

- D04 records `Route Template Expectation / Quantification Trigger`, including yes/no/not_applicable status, trigger basis, owner material need, and no-template rationale when applicable.
- D05 records `Template Corpus / Quantification Basis`, with minimum 3 parseable full-text templates plus source/similarity rationale when the gate applies.
- D06-D13 preserve the claim-evidence boundary: template stats may shape claim-design placement and wording, but they do not become evidence anchors or support strength.
- D15 records section/function distribution implications from the template corpus when available, or carries quantification incomplete as a blocker.
- D17 records surface-control implications from quantified language rhythm, surface-reference patterns, and route-safe wording controls.
- D18 records figure/table density and visual-reference implications while preserving the planned-visuals-are-not-evidence boundary.
- D19 records the canonical `Quantification Gate Status` table and D19 Quantification Handoff; valid is allowed only when the gate passes, otherwise blocked-not-valid-handoff.

## Required entry fields

Every D00-D19 entry below preserves these rubric fields where applicable: ID, Name, Dimension type, Purpose, Primary home / write target, Owner/source of truth, Minimum sufficiency, Standard sufficiency, Ideal sufficiency, Agent may propose?, Owner confirmation required?, Ask prompts, Candidate options pattern, Status examples, Stop / defer / reject rule, Common failure modes, Downstream handoff note.

Every D00-D19 entry also carries exactly one internal question-depth ladder label set: Dimension essence, Minimum probe, Standard probe, Depth probe, Conflict probe, Weak-answer handling, Stop condition, Write-normalization rule, Owner-confirmation rule, Downstream consequence, and Mechanical gate intent. These ladder labels are internal guidance for agent questioning, sufficiency judgment, write normalization, and mechanical validation only; they do not create public index columns, public statuses, public workspace files, public template fields, or manuscript prose.

## Dimension entries

### D00 — Workspace metadata

- **ID:** D00
- **Name:** Workspace metadata
- **Dimension type:** metadata/compiler
- **Purpose:** Track workspace identity and readiness metadata so the agent knows which project state it is updating, without treating metadata freshness as semantic adequacy.
- **Dimension essence:** Decide whether workspace identity and freshness metadata are explicit without implying semantic adequacy.
- **Minimum probe:** What slug/date/readiness state should be recorded, and is any identity detail ambiguous?
- **Standard probe:** Which owner/project identity, source revision, timestamps, readiness state, and semantic-adequacy disclaimer belong in metadata?
- **Depth probe:** What provenance or intake-change note would prevent stale or wrong-project handoff?
- **Conflict probe:** Does D00 freshness conflict with D02 stale flags or D19 validation notes?
- **Weak-answer handling:** Mark ambiguous identity or unknown revision deferred; keep only safe mechanical metadata.
- **Stop condition:** Stop when identity and freshness fields are explicit, or the ambiguity is deferred with consequence.
- **Write-normalization rule:** Write only workspace metadata/readiness notes and update the D00 row status and pointer.
- **Owner-confirmation rule:** Required only when owner/project identity or a provenance decision is ambiguous.
- **Downstream consequence:** Downstream may use identity and freshness hints, not claim, source, or paper-quality proof.
- **Mechanical gate intent:** Check metadata presence, non-placeholder values, and ambiguity/defer notes; never score semantic adequacy.
- **Primary home / write target:** 00_DIMENSION_INDEX.md#Workspace Metadata
- **Owner/source of truth:** agent-maintained; owner confirms project identity if ambiguous
- **Minimum sufficiency:** Project slug/date/readiness state are explicit or safely derived from the workspace, with any ambiguity visible.
- **Standard sufficiency:** Workspace identity metadata records project slug, owner/project identity or ambiguity note, created/updated timestamps, last source revision if known, readiness state, and a semantic-adequacy disclaimer.
- **Ideal sufficiency:** Includes run/date notes, concise provenance for major intake changes, and why any ambiguous identity or source revision can remain deferred.
- **First-batch upgraded goal:** Clarify workspace identity and readiness metadata as a compiler guardrail, not as evidence of paper quality, source truth, claim validity, or manuscript adequacy.
- **Field-category families / table intent:** Project slug; owner/project identity; created/updated timestamps; last source revision; readiness state; ambiguity note; semantic-adequacy disclaimer. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check metadata presence, non-placeholder values, and explicit ambiguity/defer notes; must not treat recent timestamps or completed metadata as semantic freshness or adequacy.
- **Cross-dimension dependencies:** D02 stale gate; D19 validation notes; all workspace file identity assumptions.
- **Non-goals:** Do not infer owner identity, venue/claim adequacy, or paper quality from metadata.
- **User-burden tier:** Light by default; deep only when provenance or ownership ambiguity materially affects handoff.
- **Agent may propose?:** Yes, for mechanical metadata.
- **Owner confirmation required?:** Only when project identity or owner decision is ambiguous.
- **Ask prompts:**
  - What project slug/name should this planning workspace use?
  - Has any material changed since the last design pack?
- **Candidate options pattern:** Offer a normalized slug/date/readiness summary from file context; ask owner only for ambiguous identity.
- **Status examples:** `D00 | filled | workspace metadata updated | 00_DIMENSION_INDEX.md#Workspace Metadata | yes`
- **Stop / defer / reject rule:** If project identity is unclear, mark deferred and ask owner before final handoff.
- **Common failure modes:** Treating stale metadata as proof that content is current; inventing owner identity; using D00 to imply manuscript readiness.
- **Downstream handoff note:** Downstream writing may use this only for workspace identity and freshness hints, not paper claims or semantic adequacy.

### D01 — Owner decisions

- **ID:** D01
- **Name:** Owner decisions
- **Dimension type:** owner-decision
- **Purpose:** Record owner-gated decisions, forbidden routes, and decisions the agent may not infer.
- **Dimension essence:** Decide which owner-gated decisions, forbidden routes, and non-inferable boundaries control the workspace.
- **Minimum probe:** Which decision or forbidden route is already known, or should this dimension record that none is known?
- **Standard probe:** Which route, claim, evidence, citation, or handoff choices must not be inferred automatically?
- **Depth probe:** What tempting route or claim should be rejected, and why would it distort the project?
- **Conflict probe:** Which D04, D10, D11, or D19 assumption conflicts with an owner gate?
- **Weak-answer handling:** Keep vague or later decisions deferred with the exact pending choice; do not promote candidates to decisions.
- **Stop condition:** Stop when the owner confirms the decision set, confirms none, or defers a named gate with consequence.
- **Write-normalization rule:** Record decisions in `00_PROJECT_ROUTE.md#Owner Decisions` and update the D01 row.
- **Owner-confirmation rule:** Mandatory for all final owner-gated decisions and forbidden routes.
- **Downstream consequence:** Downstream tools must preserve these gates and cannot override them with agent preference.
- **Mechanical gate intent:** Check explicit decision/defer/reject state and pointer; do not judge whether the owner decision is wise.
- **Primary home / write target:** 00_PROJECT_ROUTE.md#Owner Decisions + 00_DIMENSION_INDEX.md#Owner Notes
- **Owner/source of truth:** owner/user
- **Minimum sufficiency:** At least one owner decision or explicit statement that no special owner gate is known.
- **Standard sufficiency:** Forbidden routes and owner-gated choices that affect route, claim, evidence, or handoff are explicit.
- **Ideal sufficiency:** Includes rationale and examples of tempting but rejected decisions.
- **Agent may propose?:** No, except to propose candidate decision categories.
- **Owner confirmation required?:** Yes.
- **Ask prompts:**
  - Which route or claim boundary is owner-gated and should not be inferred automatically?
  - What route should be avoided even if it sounds attractive?
- **Candidate options pattern:** Offer likely decision categories: venue route, contribution type, claim strength, citation boundary, downstream skill route.
- **Status examples:** `D01 | filled | owner confirmed non-medical route and no citation invention | 00_PROJECT_ROUTE.md#Owner Decisions | yes`
- **Stop / defer / reject rule:** If the owner will decide later, mark deferred with the exact pending decision.
- **Common failure modes:** Converting agent preference into owner decision; hiding forbidden routes.
- **Downstream handoff note:** Downstream modules must preserve owner-gated decisions.

### D02 — Stale/readiness flags

- **ID:** D02
- **Name:** Stale/readiness flags
- **Dimension type:** metadata/compiler
- **Purpose:** Track whether upstream changes make the design pack stale, and state the recompile or risk-handoff action without judging content truth.
- **Dimension essence:** Decide whether upstream changes make the design pack stale and what recompile or risk action follows.
- **Minimum probe:** Has anything changed after the last pack, or is stale state not assessed yet?
- **Standard probe:** Which dimensions changed, which pack sections are affected, what stale-since marker exists, and what action is required?
- **Depth probe:** Which dependency changed enough that reusing D19 would mislead downstream writing?
- **Conflict probe:** Does a D19 pack timestamp or content conflict with current upstream dimensions or owner decisions?
- **Weak-answer handling:** Mark not-assessed or unresolved stale state deferred and carry a visible stale-risk note.
- **Stop condition:** Stop when there is no prior pack, no stale conflict, or a recompile/risk action is explicit.
- **Write-normalization rule:** Write the stale/readiness note in the dimension index gate area and update the D02 row.
- **Owner-confirmation rule:** Required only to ignore, defer, or accept risk from a stale/recompile flag.
- **Downstream consequence:** Downstream must pause, recompile, or carry the explicit stale-risk note.
- **Mechanical gate intent:** Check stale/deferred/recompile notes and D19 incompatibility markers; never infer content truth from stale=false.
- **Primary home / write target:** 00_DIMENSION_INDEX.md#Readiness Gate
- **Owner/source of truth:** agent-maintained from local edits and owner updates
- **Minimum sufficiency:** Readiness/stale state is explicit, even if simply 'not assessed yet'.
- **Standard sufficiency:** Changed dimensions, affected pack section, stale-since marker, recompile requirement, owner decision state, required action, and semantic-risk note are named when a design pack exists or may be reused.
- **Ideal sufficiency:** Includes a concise stale-dependency note for changed materials/claims/structure and the consequence of deferring recompile.
- **First-batch upgraded goal:** Express dependency freshness between upstream dimensions and D19 so handoff users know what changed and what must be recompiled.
- **Field-category families / table intent:** Changed dimension; affected pack section; stale since; recompile required; owner decision; required action; semantic risk note. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check explicit stale/deferred/recompile notes and obvious D19 incompatibility when structured stale data exists; must not infer content truth, claim validity, or semantic adequacy from stale=false.
- **Cross-dimension dependencies:** D00 timestamps; all upstream dimensions; D19 compile/readiness note.
- **Non-goals:** Metadata update does not clear stale risk; stale=false does not prove claims, citations, visuals, or manuscript quality are valid.
- **User-burden tier:** Light for a new workspace/no pack; default whenever D19 exists; deep after major upstream changes.
- **Agent may propose?:** Yes.
- **Owner confirmation required?:** Only when deciding whether to ignore a stale flag.
- **Ask prompts:**
  - Which dimension changed after the last design pack?
  - Should the design pack be recompiled before writing?
- **Candidate options pattern:** Infer stale flags from modified upstream files; do not infer content truth.
- **Status examples:** `D02 | deferred | D11 changed after design pack | Handoff: recompile design pack before writing | yes`
- **Stop / defer / reject rule:** If any critical upstream dimension changed after D19, block handoff until recompile or owner defers with an explicit risk note.
- **Common failure modes:** Treating old design pack as current after claim/material edits; treating timestamp freshness as semantic adequacy.
- **Downstream handoff note:** Downstream writing should pause or carry an explicit risk note when stale flags remain unresolved.

### D03 — Project brief

- **ID:** D03
- **Name:** Project brief
- **Dimension type:** owner-decision
- **Purpose:** State the project topic, domain, object, and working thesis at planning level.
- **Dimension essence:** Decide the planning-level topic, domain, object, and working thesis without drafting manuscript copy.
- **Minimum probe:** What one-sentence topic or project brief should anchor the workspace?
- **Standard probe:** Which domain positioning, research object, and working thesis should downstream use without guessing?
- **Depth probe:** What boundary prevents hype, overbroad domain claims, or a wrong object framing?
- **Conflict probe:** Does the brief conflict with D04 route, D10 contribution, or D16 object granularity?
- **Weak-answer handling:** Treat broad areas as deferred until object/topic is explicit; do not turn them into claims.
- **Stop condition:** Stop when the brief constrains route and claims, or the missing object/topic is named as blocker.
- **Write-normalization rule:** Write the normalized brief to `00_PROJECT_ROUTE.md#Project Brief` and update the D03 row.
- **Owner-confirmation rule:** Required when the topic, thesis, or boundary is inferred or materially changed.
- **Downstream consequence:** Downstream may use the brief as planning input, not as manuscript prose or evidence.
- **Mechanical gate intent:** Check nonblank brief or explicit deferral and pointer; do not judge topic quality.
- **Primary home / write target:** 00_PROJECT_ROUTE.md#Project Brief
- **Owner/source of truth:** owner/user, with agent normalization
- **Minimum sufficiency:** A one-sentence topic or project brief exists.
- **Standard sufficiency:** Brief names domain positioning, research object, and working thesis without hype.
- **Ideal sufficiency:** Includes short rationale for why the project belongs in the selected traffic/computing route.
- **Agent may propose?:** Yes, to normalize wording from user input.
- **Owner confirmation required?:** Yes if topic/thesis is inferred or changes claim boundary.
- **Ask prompts:**
  - In one sentence, what is the topic and domain positioning?
  - What is the working thesis without hype?
- **Candidate options pattern:** Offer 2-3 concise brief phrasings based on supplied material; ask owner to choose or revise.
- **Status examples:** `D03 | filled | owner confirmed project brief | 00_PROJECT_ROUTE.md#Project Brief | yes`
- **Stop / defer / reject rule:** If the user has only a broad area, mark deferred and ask for object/topic before claims.
- **Common failure modes:** Writing a promotional abstract; confusing project area with contribution.
- **Downstream handoff note:** Downstream writing may reuse the brief as planning input, not as manuscript prose.

### D04 — Target route profile

- **ID:** D04
- **Name:** Target route profile
- **Dimension type:** owner-decision
- **Purpose:** Define target venue/family, paper type, route profile, audience, reviewer expectations, and hard constraints as a planning target.
- **Dimension essence:** Decide the owner-confirmed route, venue family, paper type, audience, and hard constraints.
- **Minimum probe:** What route/profile is known, or should route remain explicitly deferred with uncertainty?
- **Standard probe:** Which venue family, article type, audience, reviewer expectation, constraints, forbidden routes, and owner state are recorded?
- **Depth probe:** Which route tradeoff changes structure, visuals, reporting, or downstream handoff expectations?
- **Conflict probe:** Does the selected route conflict with D01 gates, D03 brief, D14 spine, D15 outline, or D18 visual plan?
- **Weak-answer handling:** Keep unselected route options as candidates/deferred; do not claim venue fit or acceptance likelihood.
- **Stop condition:** Stop when owner confirms route/profile or explicitly accepts final-route deferral risk.
- **Write-normalization rule:** Write route/audience constraints to `00_PROJECT_ROUTE.md` and update the D04 row.
- **Owner-confirmation rule:** Mandatory before standard/filled route handling.
- **Downstream consequence:** Downstream follows route constraints but cannot claim guaranteed fit, novelty, or readiness.
- **Mechanical gate intent:** Check route decision state, constraints, forbidden-route notes, and pointers; do not judge venue fit.
- **Primary home / write target:** 00_PROJECT_ROUTE.md#Target Route + 00_PROJECT_ROUTE.md#Audience and Reviewer Expectation
- **Owner/source of truth:** owner/user, with agent route options
- **Minimum sufficiency:** A venue family, route/profile placeholder, or explicit deferred route exists with downstream uncertainty visible.
- **Standard sufficiency:** Venue family, article/paper type, content/format/reporting fit intent, primary audience, reviewer expectation, hard constraints, forbidden routes, and owner confirmation state are recorded; final-route deferral is allowed only when the owner explicitly accepts downstream uncertainty.
- **Ideal sufficiency:** Includes alternative routes rejected/deferred with tradeoffs and route-specific consequences for D14/D15/D18/D19.
- **First-batch upgraded goal:** Upgrade from a venue label to a venue/profile route intent that separates owner-confirmed route from inferred audience/reviewer expectations.
- **Field-category families / table intent:** Venue family; article type; content-fit intent; format-fit intent; reporting-fit intent; primary audience; reviewer expectation; hard constraints; forbidden routes; owner confirmation state. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check route decision state, audience/reviewer content, hard-constraint/forbidden-route notes, and pointers to route sections; must not judge actual venue fit or acceptance likelihood.
- **Cross-dimension dependencies:** D01 owner decisions; D03 brief; D14 reader path; D15 outline/section jobs; D18 visual format/storyline; D19 submission blueprint.
- **Non-goals:** Do not infer owner-confirmed venue from exemplars, source notes, or dossier notes; do not claim fit, novelty, or readiness.
- **User-burden tier:** Default for ordinary projects; deep for high-stakes venue targeting or strict formatting/reporting routes.
- **Template Quantification Gate note:** D04 must record the route/template trigger basis; a target route, article type, or owner template expectation makes template quantification applicable unless an owner-confirmed no-template rationale is recorded.
- **Agent may propose?:** Yes, to propose route options.
- **Owner confirmation required?:** Yes before marking standard/filled.
- **Ask prompts:**
  - What venue or venue family should this paper target?
  - What paper type is this: method, system, benchmark, application, survey, or other?
- **Candidate options pattern:** Offer 2-4 route/profile options with content/format/reporting risks, such as intelligent-transportation venue, computer-science/AI method venue, application/systems venue, or deferred route; recommend one only as candidate until owner selects.
- **Status examples:** `D04 | filled | owner selected intelligent-transportation venue family | 00_PROJECT_ROUTE.md#Target Route | yes`
- **Stop / defer / reject rule:** If owner has not selected, mark deferred; continue upstream intake only, and do not compile final pack unless owner confirms venue family/paper type/audience or explicitly accepts final-route deferral.
- **Common failure modes:** Inferring venue certainty; switching to medical/clinical framing unasked; merging audience expectation with owner-confirmed route.
- **Downstream handoff note:** Downstream writing should follow route/profile expectations and hard constraints but not claim guaranteed fit.

### D05 — Material inventory

- **ID:** D05
- **Name:** Material inventory
- **Dimension type:** factual-material
- **Purpose:** Inventory real materials: results, figures, data, code, baselines, metrics, and absences.
- **Dimension essence:** Inventory real materials and explicit absences so claims cannot rely on invented results or artifacts.
- **Minimum probe:** Which results, figures, data, code, baselines, metrics, or absences are known by category?
- **Standard probe:** Where are core materials locatable, which are absent/deferred, and which planned items are not completed evidence?
- **Depth probe:** Which material can support which claim or section, and what provenance or scope limit matters?
- **Conflict probe:** Does the material inventory conflict with D06 anchors, D11 claims, or D18 visual status?
- **Weak-answer handling:** Mark missing materials absent/deferred with consequence; never invent locations, metrics, or outcomes.
- **Stop condition:** Stop when material states are explicit enough to allow or block related claims.
- **Write-normalization rule:** Write material categories to `01_MATERIALS_INVENTORY.md#Results and Experiments` and update D05.
- **Owner-confirmation rule:** Required for material existence, location, and interpretation.
- **Downstream consequence:** Downstream may use only listed material boundaries and absence/defer notes.
- **Mechanical gate intent:** Check category/status/pointer presence and planned-vs-complete separation; do not judge result quality.
- **Primary home / write target:** 01_MATERIALS_INVENTORY.md#Results and Experiments
- **Owner/source of truth:** user-supplied or locally locatable project material
- **Minimum sufficiency:** Known materials or explicit absences are listed by category.
- **Standard sufficiency:** Core results/figures/data/code/baselines/metrics are locatable or explicitly absent/deferred with consequence; planned-but-not-run work is separated from completed evidence.
- **Ideal sufficiency:** Includes quality notes, provenance, and which claims each material can support.
- **Template Quantification Gate note:** D05 owns the template corpus material intake; when applicable it must record minimum 3 parseable full-text templates plus source/similarity rationale, and citation-only/unparseable records do not count.
- **Agent may propose?:** Only to classify supplied materials.
- **Owner confirmation required?:** Yes for material existence and interpretation.
- **Ask prompts:**
  - Where are the main results, tables, or experiment logs?
  - What baselines and metrics support the core comparison?
- **Candidate options pattern:** Offer category checklist for results, figures/tables, data, code, baselines, metrics, existing text, and explicit absences; never invent material locations or outcomes.
- **Status examples:** `D05 | filled | experiment/result locations supplied | 01_MATERIALS_INVENTORY.md#Results and Experiments | yes`
- **Stop / defer / reject rule:** If core materials are missing, mark absent/deferred with consequences and avoid supported claims.
- **Common failure modes:** Treating planned experiments as completed; inventing metrics/results.
- **Downstream handoff note:** Downstream writing may only use listed material boundaries.

### D06 — Evidence inventory

- **ID:** D06
- **Name:** Evidence inventory
- **Dimension type:** evidence
- **Purpose:** Create evidence anchors that can support or reject claims.
- **Dimension essence:** Create evidence anchors that can support, weaken, or reject claims without inventing support.
- **Minimum probe:** Is there at least one evidence anchor, or is evidence absence explicit?
- **Standard probe:** Which locatable anchor, type, supported claim, support status, and owner-confirmed relation applies to each active claim?
- **Depth probe:** What support strength, limitation, or cross-link prevents overclaiming from this anchor?
- **Conflict probe:** Does any D11 claim, D12 wording, or D18 visual rely on a missing or mismatched anchor?
- **Weak-answer handling:** Claims without anchors must be downgraded, deferred, or rejected; vague evidence is not standard.
- **Stop condition:** Stop when every active core claim is anchored or removed/deferred with consequence.
- **Write-normalization rule:** Write anchors to `01_MATERIALS_INVENTORY.md#Evidence Inventory` and update D06.
- **Owner-confirmation rule:** Required for evidence existence and support relation.
- **Downstream consequence:** Downstream can cite anchors only within their confirmed support limits.
- **Mechanical gate intent:** Check anchor fields, statuses, and claim cross-references; do not verify truth or strength semantically.
- **Primary home / write target:** 01_MATERIALS_INVENTORY.md#Evidence Inventory
- **Owner/source of truth:** user-supplied or locatable evidence artifacts
- **Minimum sufficiency:** At least one anchor table exists or evidence absence is explicit.
- **Standard sufficiency:** Each active core claim has an evidence anchor with type, location, supported claim/dimension, support status, and owner-confirmed support relation; missing anchors force claim defer/reject/downgrade.
- **Ideal sufficiency:** Includes evidence strength notes and cross-links to figures/tables/results.
- **Template Quantification Gate note:** D06 evidence anchors remain separate from template statistics; template statistics guide writing design and are not claim evidence unless separately promoted through D06/D11 rules.
- **Agent may propose?:** Only to name/normalize anchors from supplied material.
- **Owner confirmation required?:** Yes for evidence existence and support relation.
- **Ask prompts:**
  - Which result, figure, table, or artifact supports the strongest planned claim?
  - What evidence anchor should support this claim?
- **Candidate options pattern:** Suggest anchor IDs like E1/E2 only for supplied artifacts, with choices for active anchor, absent evidence, deferred evidence, or rejected claim; do not create evidence from memory.
- **Status examples:** `D06 | filled | evidence anchors mapped to supplied results | 01_MATERIALS_INVENTORY.md#Evidence Inventory | yes`
- **Stop / defer / reject rule:** A claim without evidence must be deferred/rejected or downgraded; do not mark standard.
- **Common failure modes:** Using vague 'experiments show' without anchor; mismatching anchors to claims.
- **Downstream handoff note:** Downstream writing must cite evidence anchors, not unsupported claims.

### D07 — Source and citation bank

- **ID:** D07
- **Name:** Source and citation bank
- **Dimension type:** source-citation
- **Purpose:** Record known source/citation candidates, source roles, citation status, and citation boundaries without native search or claim support inflation.
- **Dimension essence:** Record supplied source/citation candidates and roles without turning them into source truth or claim evidence.
- **Minimum probe:** Are sources supplied, absent, or deferred with a no-invention boundary?
- **Standard probe:** Which source identity, role, citation status, locator, use, limitation, permission, and handoff need are visible?
- **Depth probe:** Which citation function or unresolved source boundary will matter to downstream writing?
- **Conflict probe:** Does a source role conflict with D08 notes, D06 evidence anchors, or D11 claim support?
- **Weak-answer handling:** Mark absent/deferred sources explicitly and hand off the need; do not invent references or facts.
- **Stop condition:** Stop when supplied source state and boundary are explicit, and no active claim relies on unsupported source use.
- **Write-normalization rule:** Write source records to `01_MATERIALS_INVENTORY.md#Source and Citation Bank` and update D07.
- **Owner-confirmation rule:** Required for source existence, citation choices, and source-role claims.
- **Downstream consequence:** Downstream receives a citation/source boundary, not completed bibliography or evidence support.
- **Mechanical gate intent:** Check table shape or explicit absent/deferred reason; do not verify citation truth, authority, or support.
- **Primary home / write target:** 01_MATERIALS_INVENTORY.md#Source and Citation Bank
- **Owner/source of truth:** user-provided candidate sources only
- **Minimum sufficiency:** Citation bank is supplied, absent, or deferred with no-invention and source/evidence/claim boundary notes.
- **Standard sufficiency:** Known candidate sources are separated from missing/deferred citation work; source identity, role, citation status, owner confirmation, locator/version/category, key use, limitation, reuse permission, and handoff need are visible when applicable.
- **Ideal sufficiency:** Includes downstream lookup needs, source-role limitations, and explicit links showing when a source is background context rather than evidence.
- **First-batch upgraded goal:** Upgrade to a source-role and citation-boundary registry so supplied sources are organized without becoming automatic evidence or claim support.
- **Field-category families / table intent:** Source identity; source role; citation status; owner confirmation; locator such as DOI/URL/page/section/version or explicit absence; key use; limitation; reuse permission; handoff need. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May require table shape or explicit absent/deferred reason; must not verify citation truth, bibliography correctness, source authority, or claim support.
- **Cross-dimension dependencies:** D06 evidence inventory; D08 research dossier; D11 claim-evidence map; D12 wording boundary; D19 source/citation boundary.
- **Non-goals:** D07 does not itself support claims; source-to-claim support routes through D06 evidence anchors and D11 claim mapping.
- **User-burden tier:** Light if no sources supplied; default when sources are supplied; deep for citation-heavy or reuse-sensitive projects.
- **Template Quantification Gate note:** D07 may record template sources or citation metadata, but citation-only source records do not satisfy the parseable full-text template count.
- **Agent may propose?:** No, except to organize supplied sources.
- **Owner confirmation required?:** Yes for source existence and citation choices.
- **Ask prompts:**
  - Which sources or citation candidates are already known or supplied by you?
  - Should missing sources be marked absent/deferred rather than invented?
- **Candidate options pattern:** Offer source-role categories: background, baseline, method, dataset, standard, exemplar, absent, or deferred-to-downstream; never supply source facts for the owner.
- **Status examples:** `D07 | absent | owner supplied no citation candidates; plugin must not search | Handoff: downstream may ask owner for sources | yes`
- **Stop / defer / reject rule:** If no sources are supplied, mark absent/deferred; do not block standard dimensions if source work is explicitly handed off and no active claim depends on a missing source/evidence path.
- **Common failure modes:** Inventing references; turning related-work guesses into citations; using a source list as evidence for a claim.
- **Downstream handoff note:** Downstream citation modules may receive the boundary but must not treat it as completed bibliography or evidence support.

### D08 — Research dossier

- **ID:** D08
- **Name:** Research dossier
- **Dimension type:** source-citation
- **Purpose:** Capture related-work notes, exemplar notes, research context, synthesis/gap notes, counterevidence, and absent research-context boundaries without inferring novelty.
- **Dimension essence:** Organize owner-supplied research context, dossier notes, and gaps without inferring novelty or source truth.
- **Minimum probe:** Are related-work notes present, absent, or deferred, and what consequence follows?
- **Standard probe:** Which study notes, synthesis/gap notes, conflict map, counterevidence, and unresolved source needs are separated?
- **Depth probe:** Which gap, conflict, or counterevidence risk constrains contribution, limitations, or reader path?
- **Conflict probe:** Do dossier notes conflict with D07 sources, D10 contribution, D11 claims, D13 risks, or D14 spine?
- **Weak-answer handling:** Record absence/defer state and risk; do not synthesize literature from memory.
- **Stop condition:** Stop when research-context state and downstream consequence are explicit.
- **Write-normalization rule:** Write dossier notes to inventory/design-pack dossier sections and update D08.
- **Owner-confirmation rule:** Required for source claims, research-gap claims, and counterevidence interpretation.
- **Downstream consequence:** Downstream treats notes as context and risk, not proof of novelty or claim truth.
- **Mechanical gate intent:** Check dossier status and risk/handoff note; do not infer novelty, adequacy, source truth, or authority.
- **Primary home / write target:** 01_MATERIALS_INVENTORY.md#Research Dossier + 04_WRITING_DESIGN_PACK.md#Research Dossier Notes
- **Owner/source of truth:** user-provided notes or explicit absence
- **Minimum sufficiency:** Research notes are present, absent, or deferred explicitly with downstream consequence.
- **Standard sufficiency:** Known dossier notes distinguish research/context boundary, study-level notes, theme-level synthesis, conflict map, gap hypothesis, counterevidence, unresolved source needs, and downstream consequence when absent/deferred.
- **Ideal sufficiency:** Includes relation to venue expectations, claim boundaries, limitation risks, and explicit unresolved research tasks.
- **First-batch upgraded goal:** Upgrade from note pile to research-context and synthesis/gap intent while preserving that absence does not prove novelty.
- **Field-category families / table intent:** Research question/context boundary; study-level notes; theme-level synthesis; conflict map; gap hypothesis; counterevidence; unresolved source needs; downstream consequence. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May require explicit dossier status and risk/handoff note; must not infer novelty, related-work adequacy, source truth, or citation authority.
- **Cross-dimension dependencies:** D07 sources; D10 contribution options; D11 claims; D13 limitations; D14 reader path; D19 semantic-risk note.
- **Non-goals:** Do not turn dossier notes into manuscript prose, citation truth, novelty judgment, or claim support without D06/D11 anchors.
- **User-burden tier:** Light if absent with risk note; default for known related-work context; deep for review/synthesis-heavy projects.
- **Template Quantification Gate note:** D08 may record research/context reasons for template choice, but source/similarity rationale is a writing-design basis and not novelty or claim support.
- **Agent may propose?:** Only to organize supplied notes.
- **Owner confirmation required?:** Yes for claims about sources or research gaps.
- **Ask prompts:**
  - Which related-work notes are absent and should be marked absent/deferred rather than invented?
  - Do you have exemplar papers, known gaps, conflicts, or counterevidence to preserve?
- **Candidate options pattern:** Offer dossier buckets: known related work, theme synthesis, conflict/counterevidence, gap notes, unresolved source needs, absent dossier, or deferred research task.
- **Status examples:** `D08 | deferred | no related-work dossier supplied | Handoff: downstream writing asks owner for source notes | no`
- **Stop / defer / reject rule:** If absent, record absence and downstream consequence; do not synthesize literature from memory.
- **Common failure modes:** Smuggling citation search into planning; overstating novelty from missing dossier; using source notes as evidence anchors.
- **Downstream handoff note:** Downstream research/writing should treat dossier notes as owner-supplied context and risk, not proof of novelty or claim truth.

### D09 — Exemplar language profile

- **ID:** D09
- **Name:** Exemplar language profile
- **Dimension type:** agent-designable-structure
- **Purpose:** Capture language/style exemplars, route-consistent style fingerprint, and forbidden imitation boundaries, or explicitly mark no exemplar profile.
- **Dimension essence:** Capture exemplar/style constraints and forbidden imitation boundaries without copying or inventing exemplars.
- **Minimum probe:** Is an exemplar/language profile supplied, absent, or deferred?
- **Standard probe:** Which style role, positive rules, forbidden imitation, voice, tense, hedge, terminology, and wording links apply?
- **Depth probe:** Which style constraint most affects route fit, claim strength, or overclaim control?
- **Conflict probe:** Does exemplar use conflict with D07 source handling or D12/D17 wording boundaries?
- **Weak-answer handling:** If absent/deferred, use only generic route-consistent controls and name the limitation.
- **Stop condition:** Stop when profile absence is explicit or constraints are usable without fake exemplar sources.
- **Write-normalization rule:** Write to `03_WRITING_STRUCTURE.md#Exemplar Language Profile` and update D09.
- **Owner-confirmation rule:** Required for naming specific exemplar papers or treating a source as exemplar.
- **Downstream consequence:** Downstream may use style constraints but not fake citations, copied prose, or stronger claims.
- **Mechanical gate intent:** Check exemplar status and rationale; do not judge prose quality, style similarity, or authorial quality.
- **Primary home / write target:** 03_WRITING_STRUCTURE.md#Exemplar Language Profile
- **Owner/source of truth:** user-supplied exemplars or generic route constraints
- **Minimum sufficiency:** Exemplar profile is supplied, absent, or deferred with status and rationale.
- **Standard sufficiency:** Exemplar status/role, positive style rules, forbidden imitation, voice/tense/hedge/terminology/banned-pattern guidance, and D12/D17 wording links are visible when applicable.
- **Ideal sufficiency:** Includes positive and negative style examples from owner-provided exemplars and route-specific surface constraints without copying source prose.
- **First-batch upgraded goal:** Upgrade from “has exemplar?” to a style fingerprint with forbidden imitation and claim-strength boundaries.
- **Field-category families / table intent:** Exemplar status; exemplar role; positive style rules; forbidden imitation; voice/tense; hedge strength; terminology density; banned patterns; D12/D17 wording links. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May require status and rationale when filled/absent/deferred; must not judge prose quality, style similarity, or authorial quality.
- **Cross-dimension dependencies:** D04 venue tone; D07 if an exemplar is cited as a source; D12 wording boundary; D17 surface control; D19 handoff constraints.
- **Non-goals:** Exemplar style must not raise claim strength, create citations, or become source evidence unless separately handled in D07 and anchored through D06/D11 when claim-bearing.
- **User-burden tier:** Light when absent; default when one style target exists; deep for journal/style-sensitive drafting.
- **Template Quantification Gate note:** D09 should carry quantified language rhythm, distribution, hedge/tense, and surface-reference design outputs when the gate applies; incomplete quantification blocks D19 valid handoff.
- **Agent may propose?:** Yes, for generic route-consistent language constraints.
- **Owner confirmation required?:** Yes for naming specific exemplar papers or style sources.
- **Ask prompts:**
  - Are there supplied exemplar papers or language profiles?
  - Should this dimension be marked absent/deferred?
- **Candidate options pattern:** Offer generic style controls only when no exemplar is supplied; do not invent exemplar sources.
- **Status examples:** `D09 | absent | owner supplied no exemplar profile | Handoff: downstream uses generic route constraints | no`
- **Stop / defer / reject rule:** If no exemplar exists, mark absent/deferred; do not block design pack if route/structure are otherwise clear.
- **Common failure modes:** Inventing exemplar papers; copying manuscript prose style claims; using style as evidence for stronger claims.
- **Downstream handoff note:** Downstream writing may use generic constraints but not fake exemplar citations or unsupported claim strength.

### D10 — Contribution options

- **ID:** D10
- **Name:** Contribution options
- **Dimension type:** claim-boundary
- **Purpose:** List selected, rejected, or deferred contribution options with reasons.
- **Dimension essence:** Decide selected, rejected, and deferred contribution framings with owner-confirmed boundaries.
- **Minimum probe:** What candidate contribution exists, or should contribution selection be deferred?
- **Standard probe:** Which selected/rejected options are owner-confirmed and tied to material, evidence, problem, object, and method/system/model framing?
- **Depth probe:** Which framing tradeoff changes paper type, evidence burden, or route expectations?
- **Conflict probe:** Does the contribution conflict with D03 brief, D04 route, D11 evidence, or D16 object granularity?
- **Weak-answer handling:** Keep unconfirmed options candidate/deferred; never choose the contribution for the owner.
- **Stop condition:** Stop when owner selects the contribution boundary or records the exact pending decision.
- **Write-normalization rule:** Write contribution options to `02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options` and update D10.
- **Owner-confirmation rule:** Mandatory before standard/filled contribution handling.
- **Downstream consequence:** Downstream must follow selected/rejected contribution boundaries.
- **Mechanical gate intent:** Check selected/deferred/rejected state, rationale, and pointer; do not judge novelty or contribution strength.
- **Primary home / write target:** 02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options
- **Owner/source of truth:** owner/user decision grounded in material/evidence
- **Minimum sufficiency:** At least one candidate contribution option exists or is explicitly deferred.
- **Standard sufficiency:** Selected/rejected/deferred contribution options are owner-confirmed, tied to evidence/material dependency, and distinguish problem, object, method/system/model, and one-sentence contribution.
- **Ideal sufficiency:** Includes tradeoffs between method/system/benchmark/application framings.
- **Template Quantification Gate note:** D10 contribution options may be placed or emphasized using template claim-design benchmarks, but template patterns do not create contribution evidence.
- **Agent may propose?:** Yes, as candidate options.
- **Owner confirmation required?:** Yes before standard/filled.
- **Ask prompts:**
  - What is the one-sentence contribution without hype?
  - Which contribution option is selected, and which tempting options should be rejected?
- **Candidate options pattern:** Offer contribution option set: method, system, model, dataset, benchmark, application, analysis object, selected, rejected, or deferred; require owner selection.
- **Status examples:** `D10 | filled | owner selected system-method contribution and rejected benchmark framing | 02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options | yes`
- **Stop / defer / reject rule:** Unconfirmed contribution options remain candidate/deferred; do not compile as final standard.
- **Common failure modes:** Choosing contribution for the owner; listing options without decision rationale.
- **Downstream handoff note:** Downstream writing must follow selected/rejected contribution boundaries.

### D11 — Claim-evidence map

- **ID:** D11
- **Name:** Claim-evidence map
- **Dimension type:** claim-boundary/evidence
- **Purpose:** Bind each core claim to evidence anchors and support strength.
- **Dimension essence:** Bind each active core claim to evidence anchors, support strength, and allowed scope.
- **Minimum probe:** Which claims are active, deferred, or rejected?
- **Standard probe:** For each active claim, what owner-confirmed wording, evidence anchor, support strength, status, and wording boundary applies?
- **Depth probe:** Which claim should be split, downgraded, or rejected because support is narrow or weak?
- **Conflict probe:** Does any claim exceed D06 evidence, D12 wording, D13 limitations, or D18 visual evidence?
- **Weak-answer handling:** Unconfirmed or unsupported claims remain candidate, deferred, or rejected; do not make them active.
- **Stop condition:** Stop when active claims are all anchored and bounded, or removed/deferred with consequence.
- **Write-normalization rule:** Write mapping to `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map` and update D11.
- **Owner-confirmation rule:** Required for final claim wording and evidence-to-claim support relation.
- **Downstream consequence:** Downstream must preserve claim-evidence mapping and support strength.
- **Mechanical gate intent:** Check claim rows, anchor links, support status, and absence of unsupported active claims; do not verify truth.
- **Primary home / write target:** 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map
- **Owner/source of truth:** owner-confirmed claims plus evidence anchors
- **Minimum sufficiency:** Claims are listed or explicitly deferred/rejected.
- **Standard sufficiency:** Every active core claim has owner-confirmed wording, evidence anchor, support strength, status, and allowed/forbidden wording boundary; unsupported claims are deferred or rejected.
- **Ideal sufficiency:** Includes claim hierarchy and downgrade/reject rationale for weak evidence.
- **Template Quantification Gate note:** D11 claim-evidence support cannot be strengthened by template statistics; use template claim-design comparison only for placement, emphasis, and wording boundaries.
- **Agent may propose?:** Yes, as candidate claim phrasing from confirmed material.
- **Owner confirmation required?:** Yes before standard/filled.
- **Ask prompts:**
  - List the core claims you want the paper to make.
  - For this claim, what result, figure, table, or artifact supports it?
- **Candidate options pattern:** Suggest conservative claim candidates from supplied evidence with options for active, downgraded, deferred, or rejected status; require owner confirmation and anchor match.
- **Status examples:** `D11 | filled | core claims mapped to evidence anchors with support strength | 02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map | yes`
- **Stop / defer / reject rule:** Claim without evidence becomes deferred/rejected; unconfirmed claim remains candidate.
- **Common failure modes:** Evidence-free claims; stronger wording than support allows; fake anchors.
- **Downstream handoff note:** Downstream writing must preserve claim-evidence mapping and support strength.

### D12 — Wording boundary

- **ID:** D12
- **Name:** Wording boundary
- **Dimension type:** claim-boundary
- **Purpose:** Define allowed and forbidden wording so downstream writing cannot overclaim.
- **Dimension essence:** Define allowed and forbidden wording so downstream writing cannot overclaim.
- **Minimum probe:** What wording boundary exists, or should it be deferred?
- **Standard probe:** Which allowed and forbidden phrases are tied to evidence strength, object granularity, and owner-confirmed claim scope?
- **Depth probe:** Which tempting stronger phrase must be prohibited, and what cautious alternative is allowed?
- **Conflict probe:** Does D17 surface language or D11 claim wording exceed D06 support?
- **Weak-answer handling:** If boundaries are missing, mark deferred and default to conservative language; do not permit stronger wording.
- **Stop condition:** Stop when wording boundaries cover core claims or the unresolved risk is explicit.
- **Write-normalization rule:** Write to allowed/forbidden wording sections and update D12.
- **Owner-confirmation rule:** Required for final claim boundaries and forbidden overclaims.
- **Downstream consequence:** Downstream treats forbidden wording as a hard boundary.
- **Mechanical gate intent:** Check allowed/forbidden entries and links to claims/evidence; do not judge prose quality.
- **Primary home / write target:** 02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording + 02_CLAIM_EVIDENCE_BOUNDARY.md#Forbidden Wording
- **Owner/source of truth:** agent proposal grounded in evidence; owner confirms claim boundaries
- **Minimum sufficiency:** At least one allowed/forbidden wording boundary exists or is explicitly deferred.
- **Standard sufficiency:** Allowed wording, forbidden wording, and overclaim boundaries are tied to evidence strength, object granularity, and owner-confirmed core-claim scope.
- **Ideal sufficiency:** Includes examples of safe phrasing by claim strength.
- **Template Quantification Gate note:** D12 allowed/forbidden wording may be guided by template language statistics, but the gate does not score prose quality or style similarity.
- **Agent may propose?:** Yes, to propose conservative wording.
- **Owner confirmation required?:** Yes for final claim boundaries and forbidden overclaims.
- **Ask prompts:**
  - Which stronger wording must be forbidden because evidence does not support it?
  - What cautious wording is allowed for this evidence strength?
- **Candidate options pattern:** Offer safe/unsafe phrasing pairs based on support strength, including cautious allowed wording, banned stronger wording, and deferred wording when evidence is incomplete; ask owner to confirm.
- **Status examples:** `D12 | filled | allowed/forbidden wording confirmed for core claims | 02_CLAIM_EVIDENCE_BOUNDARY.md#Forbidden Wording | yes`
- **Stop / defer / reject rule:** If boundaries are missing, block final design pack for core claims.
- **Common failure modes:** Permitting universal claims from narrow experiments; hiding forbidden wording.
- **Downstream handoff note:** Downstream writing must treat forbidden wording as a hard boundary.

### D13 — Limitation and risk matrix

- **ID:** D13
- **Name:** Limitation and risk matrix
- **Dimension type:** claim-boundary
- **Purpose:** Record limitations, risks, and claim constraints that must remain visible.
- **Dimension essence:** Keep limitations, risks, and claim constraints visible as writing guardrails.
- **Minimum probe:** What limitation/risk exists, or does the owner explicitly say none is known with rationale?
- **Standard probe:** Which risks tie to material gaps, evidence strength, route expectations, rejected claims, and wording constraints?
- **Depth probe:** Which hidden limitation would change contribution, route, or reader expectation if omitted?
- **Conflict probe:** Does the risk matrix contradict D11 claims, D12 wording, D14 reader path, or D19 handoff notes?
- **Weak-answer handling:** Unknown limitations remain deferred; do not imply absence without owner rationale.
- **Stop condition:** Stop when material risks are explicit or deferred with downstream consequence.
- **Write-normalization rule:** Write risks to `02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks` and update D13.
- **Owner-confirmation rule:** Required for final material-risk interpretation and owner-known absence claims.
- **Downstream consequence:** Downstream uses risks as guardrails, not optional caveats to drop.
- **Mechanical gate intent:** Check risk/defer entries, rationale, and pointers; do not judge limitation adequacy.
- **Primary home / write target:** 02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks
- **Owner/source of truth:** agent inference from gaps plus owner confirmation for material risks
- **Minimum sufficiency:** At least one limitation/risk exists or owner explicitly says none known with rationale.
- **Standard sufficiency:** Limitations/risks are tied to material gaps, evidence strength, route expectations, rejected claims, and downstream wording constraints.
- **Ideal sufficiency:** Includes mitigation/handoff notes for each major limitation.
- **Template Quantification Gate note:** D13 must carry limitations when template quantification is incomplete, insufficient, citation-only, or not applicable by owner-confirmed route rationale.
- **Agent may propose?:** Yes, to infer candidate risks from missing materials/evidence.
- **Owner confirmation required?:** Yes for final material risk interpretation.
- **Ask prompts:**
  - What limitation or risk should downstream writing keep visible?
  - Where should the paper be conservative because evidence is limited?
- **Candidate options pattern:** Offer risk categories: data scope, baseline scope, metric scope, deployment, generalization, citation gap, visual evidence gap, or owner-known risk.
- **Status examples:** `D13 | filled | limitations tied to baseline and dataset scope | 02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks | yes`
- **Stop / defer / reject rule:** If limitations are unknown, mark deferred; do not imply absence without owner rationale.
- **Common failure modes:** Writing 'no limitations'; burying risks outside handoff.
- **Downstream handoff note:** Downstream writing should reuse limitations as guardrails, not optional caveats.

### D14 — Reader spine

- **ID:** D14
- **Name:** Reader spine
- **Dimension type:** agent-designable-structure
- **Purpose:** Define the reader's question-and-answer path through the paper, linked to route, claims, evidence, limitations, and transitions.
- **Dimension essence:** Define the reader's question-and-answer path through confirmed route, claims, evidence, and limits.
- **Minimum probe:** What rough reader question sequence should structure the argument?
- **Standard probe:** Which reader persona, question sequence, expected answers, linked claims/evidence/limitations, forbidden questions, and transitions apply?
- **Depth probe:** Which hidden reviewer question or ordering tradeoff would change the argument path?
- **Conflict probe:** Does the spine conflict with D04 audience, D10 contribution, D11 evidence, D15 outline, or D18 visuals?
- **Weak-answer handling:** Keep the spine candidate/deferred when claims, materials, or route remain unconfirmed.
- **Stop condition:** Stop when the path follows confirmed boundaries or names the exact blocker.
- **Write-normalization rule:** Write to `03_WRITING_STRUCTURE.md#Reader Spine` and update D14.
- **Owner-confirmation rule:** Optional unless the spine changes route, contribution, or claim emphasis.
- **Downstream consequence:** Downstream uses the spine as argument order while preserving evidence/limitation boundaries.
- **Mechanical gate intent:** Check question-path shape and cross-references; do not judge persuasiveness or reviewer satisfaction.
- **Primary home / write target:** 03_WRITING_STRUCTURE.md#Reader Spine
- **Owner/source of truth:** agent proposal grounded in confirmed route/materials/claims
- **Minimum sufficiency:** A rough reader question sequence exists.
- **Standard sufficiency:** Reader spine records reader persona, question sequence, expected answers, linked claim/evidence/limitation, forbidden questions, and transition rationale while following confirmed route, contribution, evidence, and limitation boundaries.
- **Ideal sufficiency:** Includes alternative spine rejected and rationale for section order and reviewer expectation tradeoffs.
- **First-batch upgraded goal:** Upgrade outline-adjacent notes into a reader question path that downstream drafting can follow without guessing the argument order.
- **Field-category families / table intent:** Reader persona; question sequence; expected answer; linked claim; linked evidence; linked limitation; forbidden question; transition rationale. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check structured question-path shape and cross-reference presence; must not judge argument persuasiveness or reviewer satisfaction.
- **Cross-dimension dependencies:** D04 audience/reviewer profile; D10 contribution; D11 evidence; D13 limitations; D15 section jobs; D18 visual storyline.
- **Non-goals:** Reader spine is not a section outline, not manuscript prose, and not copied reviewer expectation.
- **User-burden tier:** Default; deep when the paper needs careful argument design.
- **Agent may propose?:** Yes.
- **Owner confirmation required?:** Owner confirmation optional unless spine changes claim/route emphasis.
- **Ask prompts:**
  - What question should the reader ask first, and what answer should the paper give?
  - What is the argument path from problem to evidence to limitation?
- **Candidate options pattern:** Propose a spine from route + contribution + evidence, such as problem→gap→object→method/system→evidence→limitation; note assumptions and ask if emphasis changes claims.
- **Status examples:** `D14 | filled | reader question sequence derived from confirmed claims and materials | 03_WRITING_STRUCTURE.md#Reader Spine | yes`
- **Stop / defer / reject rule:** If claims/materials are unconfirmed, keep spine deferred/candidate.
- **Common failure modes:** Creating a spine around unsupported claims; drafting prose instead of structure; confusing reader path with section titles.
- **Downstream handoff note:** Downstream writing uses the spine as argument order and must preserve linked evidence/limitation boundaries.

### D15 — Manuscript outline

- **ID:** D15
- **Name:** Manuscript outline
- **Dimension type:** agent-designable-structure
- **Purpose:** Define manuscript outline and section-job responsibilities for downstream drafting without writing manuscript prose.
- **Dimension essence:** Define outline and section-job responsibilities without drafting manuscript prose.
- **Minimum probe:** What section list exists, or should outline work be deferred?
- **Standard probe:** Which section jobs, input dimensions, output promises, required evidence, forbidden content, length/function hints, and constraints apply?
- **Depth probe:** Which section job prevents unsupported prose, omitted limitations, or wrong paper-type structure?
- **Conflict probe:** Does the outline conflict with D04 route, D11 evidence, D13 limitations, D14 spine, or D18 visuals?
- **Weak-answer handling:** Keep outline candidate/deferred when route, type, or claims are unresolved.
- **Stop condition:** Stop when section jobs can guide downstream writing without guessing.
- **Write-normalization rule:** Write to manuscript outline and section-job sections, then update D15.
- **Owner-confirmation rule:** Required if the outline chooses among materially different paper types or routes.
- **Downstream consequence:** Downstream treats section jobs as constraints, not finished prose.
- **Mechanical gate intent:** Check section/job pairing and responsibility categories; do not judge rhetorical optimality or draft quality.
- **Primary home / write target:** 03_WRITING_STRUCTURE.md#Manuscript Outline + 03_WRITING_STRUCTURE.md#Section Jobs
- **Owner/source of truth:** agent proposal grounded in route/type/claims
- **Minimum sufficiency:** A section list or explicit outline deferral exists.
- **Standard sufficiency:** Outline and section jobs pair each section with job, input dimensions, output promise, required evidence, forbidden content, length/paragraph-function hints, and downstream constraints matched to paper type, route, reader spine, limitations, and figure/table responsibilities.
- **Ideal sufficiency:** Includes paragraph/function map, section-level evidence responsibilities, and rejected outline alternatives.
- **First-batch upgraded goal:** Upgrade section titles into a section-job matrix so each section has a defined function and evidence responsibility.
- **Field-category families / table intent:** Section; job; input dimensions; output promise; required evidence; forbidden content; length hint; paragraph/function map; downstream constraint. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check section/job pairing and presence of required responsibility categories; must not judge rhetorical optimality or draft prose quality.
- **Cross-dimension dependencies:** D04 paper type; D11 claims/evidence; D13 limitations; D14 reader spine; D18 visuals; D19 blueprint.
- **Non-goals:** Do not draft manuscript prose, optimize rhetoric semantically, or let an outline create unsupported claims.
- **User-burden tier:** Default; deep for complex or multi-claim papers.
- **Template Quantification Gate note:** D15 should reflect template section/function distribution and paragraph/job implications when the gate applies; missing outputs propagate as blocked-not-valid-handoff.
- **Agent may propose?:** Yes.
- **Owner confirmation required?:** Owner confirmation needed if outline chooses among materially different paper types.
- **Ask prompts:**
  - What job should each major section perform?
  - What paper type should this outline serve?
- **Candidate options pattern:** Offer outline variants by paper type, such as method, system, benchmark, application, or survey; ask owner when the choice changes route or contribution.
- **Status examples:** `D15 | filled | outline and section jobs aligned to route and reader spine | 03_WRITING_STRUCTURE.md#Manuscript Outline | yes`
- **Stop / defer / reject rule:** If route/type/claims are unresolved, outline remains deferred/candidate.
- **Common failure modes:** Over-specific manuscript drafting; generic outline unrelated to evidence; section jobs that omit limitations or required evidence.
- **Downstream handoff note:** Downstream writing should treat section jobs as task constraints, not as finished prose.

### D16 — Object granularity

- **ID:** D16
- **Name:** Object granularity
- **Dimension type:** claim-boundary/structure
- **Purpose:** Clarify whether the paper is about a method, system, model, dataset, benchmark, application, or analysis object.
- **Dimension essence:** Clarify exact research-object granularity so claims, structure, and wording target the same object.
- **Minimum probe:** What object type is named, or should object granularity be deferred?
- **Standard probe:** Which precise object boundary binds claims, evidence, outline, wording, and structure/claim-side consistency?
- **Depth probe:** Which adjacent object level or non-object must be excluded to prevent overbroad claims?
- **Conflict probe:** Do structure-side and claim-side object statements conflict with D10, D11, D12, or D17?
- **Weak-answer handling:** Vague object language remains deferred and triggers reconciliation; do not allow broad claims.
- **Stop condition:** Stop when the object boundary is confirmed or an exact conflict remains as a blocking defer note.
- **Write-normalization rule:** Write reconciled object notes to both structure and claim-boundary homes, then update D16.
- **Owner-confirmation rule:** Required when the object boundary affects claims, contribution, or paper scope.
- **Downstream consequence:** Downstream must preserve object granularity in every claim and section job.
- **Mechanical gate intent:** Check dual landing and reconciliation notes; do not judge the taxonomy's scholarly correctness.
- **Primary home / write target:** 03_WRITING_STRUCTURE.md#Object Granularity + 02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity
- **Owner/source of truth:** owner for claim-affecting object boundary; agent for structural phrasing
- **Minimum sufficiency:** Research object type is named or deferred.
- **Standard sufficiency:** Object granularity is precise enough to bind claims, evidence, outline, and wording boundaries, with primary structure-side wording reconciled against claim-side wording.
- **Ideal sufficiency:** Includes object/non-object distinctions and examples of too-broad claims.
- **Agent may propose?:** Yes, to propose granularity options.
- **Owner confirmation required?:** Yes when object boundary affects claims/contribution.
- **Ask prompts:**
  - What is the exact research object?
  - What object/variable/mechanism granularity should writing preserve?
- **Candidate options pattern:** Offer object candidates from materials: method, system, model, dataset, benchmark, application, analysis object, primary object, secondary object, or deferred; require confirmation if claim-bearing.
- **Status examples:** `D16 | filled | owner confirmed object as system-method rather than deployment product | 03_WRITING_STRUCTURE.md#Object Granularity | yes`
- **Stop / defer / reject rule:** If object boundary is vague or conflicts between structure-side and claim-side files, block standard for claims and structure and ask a reconciliation card.
- **Common failure modes:** Mixing method/system/application levels; allowing claims about unstudied objects.
- **Downstream handoff note:** Downstream writing must preserve object granularity in every claim.

### D17 — Surface control

- **ID:** D17
- **Name:** Surface control
- **Dimension type:** claim-boundary/structure
- **Purpose:** Control terminology, tone, claim strength, and surface wording constraints.
- **Dimension essence:** Control terminology, tone, and claim-strength surface choices across structure and claim-boundary files.
- **Minimum probe:** What term, tone, or surface-control boundary exists, or should it be deferred?
- **Standard probe:** Which controls map to route, evidence strength, forbidden wording, object granularity, terminology, and cross-file consistency?
- **Depth probe:** Which term, adjective, or tone would create overclaim, wrong audience framing, or domain confusion?
- **Conflict probe:** Do D17 controls conflict with D12 allowed/forbidden wording, D09 style, D16 object, or D04 route?
- **Weak-answer handling:** Use conservative provisional controls or defer; never permit banned terms or unsupported adjectives.
- **Stop condition:** Stop when controls are reconciled with claim-side boundaries or a specific conflict blocks D19.
- **Write-normalization rule:** Write controls to surface-control and allowed-wording homes, then update D17.
- **Owner-confirmation rule:** Required for final forbidden overclaims and domain-sensitive terms.
- **Downstream consequence:** Downstream must obey controls as wording guardrails.
- **Mechanical gate intent:** Check controls, banned terms, and reconciliation notes; do not judge style quality.
- **Primary home / write target:** 03_WRITING_STRUCTURE.md#Surface Control + 02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording
- **Owner/source of truth:** agent proposal grounded in route/evidence; owner confirms forbidden overclaims
- **Minimum sufficiency:** Tone/term controls or explicit deferral exist.
- **Standard sufficiency:** Surface controls map to route, evidence strength, forbidden wording, object granularity, tone, terminology, and primary/claim-side consistency.
- **Ideal sufficiency:** Includes reusable safe phrases, banned phrases, and tone examples.
- **Template Quantification Gate note:** D17 should reflect quantified surface controls such as terminology density, hedge strength, and surface-reference rhythm without treating them as semantic scoring.
- **Agent may propose?:** Yes, to propose conservative controls.
- **Owner confirmation required?:** Yes for final forbidden overclaim and domain-sensitive terms.
- **Ask prompts:**
  - Which terms, tone, or wording style should downstream writing control?
  - Which terms must not be used?
- **Candidate options pattern:** Offer conservative tone/term controls derived from route and evidence strength, including allowed terms, banned terms, claim-strength adjectives, and style constraints.
- **Status examples:** `D17 | filled | surface controls tied to evidence strength and forbidden wording | 03_WRITING_STRUCTURE.md#Surface Control | yes`
- **Stop / defer / reject rule:** If surface control is unhandled or conflicts with claim-side allowed/forbidden wording, block final design pack and ask a reconciliation card.
- **Common failure modes:** Making style generic; allowing unsupported adjectives like optimal/universal/deployed.
- **Downstream handoff note:** Downstream writing must obey surface controls as wording guardrails.

### D18 — Visual plan

- **ID:** D18
- **Name:** Visual plan
- **Dimension type:** agent-designable-structure/material
- **Purpose:** Plan figure/table storyline, visual evidence boundaries, and handoff needs while separating planned visuals from actual evidence.
- **Dimension essence:** Plan figure/table storyline and visual evidence boundaries without treating planned visuals as evidence.
- **Minimum probe:** Which visuals are existing, needed, deferred, absent, or unnecessary, and what consequence follows?
- **Standard probe:** Which id/type/status, story role, linked claim/evidence/reader step, data need, panel order, legend job, accessibility note, and handoff apply?
- **Depth probe:** Which visual, caption, or table constraint changes the evidence story or downstream handoff?
- **Conflict probe:** Does the visual plan conflict with D05 materials, D06 evidence, D11 claims, D14 spine, or D15 section jobs?
- **Weak-answer handling:** Mark missing visuals as needed/deferred and ensure no active claim depends on them.
- **Stop condition:** Stop when visual state is explicit and no active claim relies on missing visual evidence, or risk is deferred.
- **Write-normalization rule:** Write to visual plan/storyline sections and update D18 plus D19 handoff notes when needed.
- **Owner-confirmation rule:** Required if adding or changing a figure affects scope, evidence, or claims.
- **Downstream consequence:** Downstream receives a plan only, not generated artifact evidence or claim proof.
- **Mechanical gate intent:** Check status categories, rationale, and cross-references; do not validate figure correctness or design quality.
- **Primary home / write target:** 03_WRITING_STRUCTURE.md#Visual Plan + 03_WRITING_STRUCTURE.md#Figure / Table Storyline
- **Owner/source of truth:** agent proposal grounded in supplied figures/tables/material gaps
- **Minimum sufficiency:** Existing, needed, deferred, absent, or no-visual rationale is listed with consequence.
- **Standard sufficiency:** Visual plan records visual id/type/status, story role, linked claim/evidence/reader step, data needed, panel order, legend job, accessibility check, and handoff; any missing/no-visual path states why no active claim depends on missing visual evidence.
- **Ideal sufficiency:** Includes visual order, panel/legend intent, missing figure needs, accessibility notes, and downstream figure-skill handoff constraints.
- **First-batch upgraded goal:** Upgrade from a figure/table list to visual storyline plus visual evidence boundary.
- **Field-category families / table intent:** Visual id; type; status such as existing/needed/deferred/absent; story role; linked claim; linked evidence; linked reader step; data needed; panel order; legend job; accessibility check; handoff. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check valid status categories, explicit no-visual/deferred rationale, and cross-reference presence; must not validate figure quality, visual correctness, or design quality.
- **Cross-dimension dependencies:** D05 materials; D06 evidence; D11 claims; D14 reader path; D15 section jobs; D19 visual handoff.
- **Non-goals:** Needed/deferred visuals cannot support active claims; D18 is not generated figure evidence and does not prove visual quality.
- **User-burden tier:** Light for no-visual rationale; default for figure/table papers; deep for visual-heavy submissions.
- **Template Quantification Gate note:** D18 should reflect figure/table density and visual-reference placement from parseable templates while preserving that planned visuals are not evidence.
- **Agent may propose?:** Yes, from confirmed materials and claims.
- **Owner confirmation required?:** Yes if inventing/adding a new figure changes scope or evidence claims.
- **Ask prompts:**
  - Which figures/tables carry the main story, and in what order?
  - Which expected visuals are absent and should be marked needed/deferred?
- **Candidate options pattern:** Offer visual sequence from existing figures/tables, no-visual rationale, needed overview figure, or deferred figure/table handoff; mark missing visuals as needed, not invented.
- **Status examples:** `D18 | filled | visual storyline grounded in supplied F1/T1 and missing overview figure handoff | 03_WRITING_STRUCTURE.md#Visual Plan | yes`
- **Stop / defer / reject rule:** If no visual evidence/storyline exists, pass only with explicit no-visual rationale, alternative storyline, and no active visual-dependent claim; otherwise mark absent/deferred with downstream consequence.
- **Common failure modes:** Inventing figures; implying results shown in visuals that do not exist; using planned visuals as evidence anchors.
- **Downstream handoff note:** Downstream figure modules may use this as a plan, not as generated artifact evidence or proof of claim support.

### D19 — Writing design pack

- **ID:** D19
- **Name:** Writing design pack
- **Dimension type:** handoff
- **Purpose:** Compile the final writing design pack as a structural handoff and submission blueprint only after dimension gates are satisfied.
- **Dimension essence:** Compile the design pack as a structural handoff after gates pass, not as manuscript or readiness certification.
- **Minimum probe:** Is D19 deferred, or what exact blocker and consequence prevents compilation?
- **Standard probe:** Do coverage, blueprint, risk notes, statements, supplement boundary, handoff routes, unresolved consequences, and validation notes cover handled D00-D18?
- **Depth probe:** Which unresolved boundary must be surfaced so downstream tools do not overrun owner, evidence, source, or stale limits?
- **Conflict probe:** Does D19 conflict with D02 stale state, critical-standard gaps, placeholders, or unresolved owner gates?
- **Weak-answer handling:** Do not compile final D19; ask the next blocker or record owner-accepted risk where allowed.
- **Stop condition:** Stop when gates are satisfied and stale risk is resolved/accepted, otherwise keep D19 deferred.
- **Write-normalization rule:** Write only to `04_WRITING_DESIGN_PACK.md` coverage/validation/handoff sections and update D19.
- **Owner-confirmation rule:** Required only for unresolved owner-gated assumptions or accepted risks.
- **Downstream consequence:** Downstream receives a bounded blueprint and cannot claim manuscript, submission, publication, or acceptance readiness.
- **Mechanical gate intent:** Check coverage, status/pointer consistency, stale-risk handling, and placeholder absence; never score readiness.
- **Primary home / write target:** 04_WRITING_DESIGN_PACK.md#Dimension Coverage Summary
- **Owner/source of truth:** agent compiler after gates pass
- **Minimum sufficiency:** D19 is deferred until upstream dimensions are handled, or records the exact blocker and handoff consequence.
- **Standard sufficiency:** Design pack covers dimension coverage, submission blueprint, semantic-risk note, statement inventory, supplement boundary, external handoff routes, unresolved dimension consequences, validation notes, route, materials, source boundary, claims, wording, risks, structure, and visuals with D00-D18 handled and no TODO/TBD/UNKNOWN/REPLACE_ME placeholders.
- **Ideal sufficiency:** Includes optional gaps and downstream recommendations without executing external skills, plus concise risk notes for unresolved but owner-accepted boundaries.
- **First-batch upgraded goal:** Upgrade to submission blueprint plus semantic-risk handoff, while avoiding manuscript, submission, publication, or semantic readiness claims.
- **Field-category families / table intent:** Dimension coverage; submission blueprint; semantic-risk note; statement inventory; supplement boundary; external handoff routes; unresolved dimension consequences; validation notes. Use category-family wording rather than locking final public field names.
- **First-batch mechanical gate note:** May check section/table coverage, status/pointer consistency, stale-risk handling, and unresolved placeholder absence; must not claim manuscript, publication, submission, acceptance, or semantic readiness.
- **Cross-dimension dependencies:** D00 identity; D02 stale status; D04 route; D07/D08 boundaries; D11/D12 claims/wording; D14/D15/D18 structure.
- **Non-goals:** D19 is not manuscript prose, not external skill execution, not citation/figure production, and not a final readiness score.
- **User-burden tier:** Default for all final handoffs; deep when multiple downstream routes or supplement/submission constraints exist.
- **Template Quantification Gate note:** D19 must parse the canonical Quantification Gate Status table; valid requires gate applies yes with count >= 3, source/similarity rationale yes, quantitative outputs present, blocker propagation clear, and D19 pack status valid, or an owner-confirmed no/not_applicable rationale with no route-style adequacy claim. Otherwise emit blocked-not-valid-handoff.
- **Agent may propose?:** Yes, to compile from confirmed/handled inputs.
- **Owner confirmation required?:** Owner confirmation needed only for unresolved owner-gated assumptions.
- **Ask prompts:**
  - Are all hard blockers handled, or which dimension still blocks compilation?
  - Should this handoff go to generic writing, figure, citation, or review tools?
- **Candidate options pattern:** Compile only from existing six-file content; options are compile now, ask next blocker, recompile stale pack, or record external handoff route without executing it; do not fill unknowns with TODO.
- **Status examples:** `D19 | filled | design pack compiled after all dimensions handled | 04_WRITING_DESIGN_PACK.md#Dimension Coverage Summary | yes`
- **Stop / defer / reject rule:** If any critical standard or minimum handling gate fails, do not compile final pack; ask next focused question or record explicit owner-accepted risk where allowed.
- **Common failure modes:** Leaving TODOs; executing external skills; treating design pack as manuscript completion or submission readiness.
- **Downstream handoff note:** Downstream tools receive the design pack as a structural blueprint with risk boundaries; they cannot override owner/evidence/source/stale boundaries.
