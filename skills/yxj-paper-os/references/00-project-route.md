# Playbook 00 — Project Route

Use this playbook when `00_PROJECT_ROUTE.md` is missing or incomplete, or when D01/D03/D04 in `00_DIMENSION_INDEX.md` are unhandled.

## Schema 0.3 route and gate contract

Decision Records uses exactly: Decision ID | Gate category | Issue / options / decision | Affected scopes | Origin | Resolution | Grounding / owner-answer pointer | Recheck trigger.

Only scientific_commitment, argument_spine, material_local_tradeoff, and deliberate_divergence require owner confirmation. not_applicable marks an ordinary grounded decision. Routine route projection, template discovery, document-role classification, and reversible design adaptation do not require confirmation unless they trigger one of the four categories.

Record template discovery authority, one design question, affected scopes, and eligible roles official_venue&#124;target_topic&#124;article_form&#124;time_cohort&#124;control&#124;exemplar. Model semantic reading is primary; deterministic analysis is optional for a declared measurable question. External template material stays design_only and cannot become scientific evidence without a separate promotion record.

At entry, an exact schema-0.2 workspace is legacy input: do not preserve or report its writer-ready state as current. Route it to the agent-led, non-destructive 0.2-to-0.3 recompilation in `04-design-pack-compiler.md`; do not auto-migrate, overwrite, or invent missing design records.

## Dimension rubric reference

For schema-0.3 sufficiency, question depth, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is the central internal rubric/reference. This file is one of five task playbooks, not a public workspace file; it translates rubric gaps into compact question cards and write landings without overriding the D00-D19 ladder.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D01 | `Owner decisions` | `00_DIMENSION_INDEX.md` + `00_PROJECT_ROUTE.md#Owner Decisions` |
| D03 | `Project brief` | `00_PROJECT_ROUTE.md#Project Brief` |
| D04 | `Target route profile` | `00_PROJECT_ROUTE.md#Target Route` and `#Audience and Reviewer Expectation` |

After updating route content, update the matching D01/D03/D04 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## Question-depth translator guide

Use the central rubric to inspect the current Dxx record and scope readiness, then translate only the unresolved gap into the next compact card. Do not introduce another status vocabulary, public file, D ID, index column, manuscript prose, invented fact, external skill execution, semantic score, or runtime orchestration.

| D ID(s) | Default card mode | Ask a depth follow-up when... | Reconcile or conflict-check when... | Write landing |
|---|---|---|---|---|
| D01 | `focused-question` | one of the four owner-gate categories is triggered, or a tempting route needs an explicit rejection rationale | D04, D10, D11, or D19 assumes a decision the owner has not confirmed | `00_PROJECT_ROUTE.md#Owner Decisions` or `#Forbidden Routes`, then D01 row |
| D03 | `candidate-confirmation` from supplied wording; otherwise `focused-question` | topic, domain, object, or working thesis is broad enough to let downstream claims drift | the brief conflicts with D04 route, D10 contribution, or D16 object granularity | `00_PROJECT_ROUTE.md#Project Brief`, then D03 row |
| D04 | `focused-question` | a route tradeoff changes article type, audience, reporting, visual/storyline, or handoff expectations | route/profile conflicts with D01 gates, D03 brief, D14 spine, D15 jobs, D18 visuals, or D19 handoff | `00_PROJECT_ROUTE.md#Target Route`, `#Audience and Reviewer Expectation`, `#Route Readiness`, then D04 row |

## Adaptive D04 route/profile pointer

`00-dimension-rubric.md` remains the source of truth for D04 sufficiency. In this playbook, treat D04 as a focused venue/profile card, not as a full rubric copy:

- Separate owner-confirmed route from agent-inferred audience or reviewer expectation.
- Capture category-family intent for venue family, article type, content/format/reporting fit, primary audience, reviewer expectation, hard constraints, forbidden routes, and owner confirmation state.
- Record route/profile uncertainty as `deferred` or explicit owner-accepted final-route deferral; do not silently convert dossier notes, exemplars, or writing style into a venue decision.
- Use hard constraints to constrain D14 reader path, D15 section jobs, D18 visual format/storyline, and D19 submission blueprint.
- Mechanical checks may confirm that route/profile content and pointers exist; they must not judge actual venue fit, novelty, or acceptance likelihood.

## Additional route planning additions

Use these additions as planning-only route prompts. They seed downstream sections and question cards; they do not draft title, abstract, keywords, graphical-hook copy, captions, reporting statements, or manuscript prose.

- **Front matter / hook constraints:** capture route implications for title style, abstract type, keyword scope, visual/graphical hook feasibility, length/format limits, and forbidden front-matter promises. Treat final wording as downstream; ask the owner only if a four-category gate is triggered.
- **Article type → reporting implications:** record whether the route implies a method, system, benchmark, application, survey, data, reproducibility, ethics, availability, or supplement statement. This is an inventory seed only; do not certify reporting compliance.
- **Method/reporting/repro seed:** route constraints may point D05/D06 materials and D15 section jobs to required artifacts such as code/data availability, protocol details, parameter settings, ablation expectations, or baseline disclosure.
- **Downstream route matrix seed:** record candidate downstream writing/figure/citation/review routes as recommendations and constraints for D19. Do not execute those routes; ask the owner only when the route choice triggers one of the four gate categories.
- **Boundary invariant:** owner confirmation is mandatory only for a triggered four-category gate. Routine grounded route implications may be recorded without ceremony; unresolved consequential choices remain candidate or deferred.

## Conditional template-analysis route trigger

Activate template analysis only when a concrete writing-design question can change a requested surface. Record discovery authority, eligible document roles, affected scopes, and design_only firewall. Model-semantic reading is primary. Use the deterministic analyzer only for a declared measurable question; it is never a document-count or readiness prerequisite.

Official presentation constraints may be hard. Exemplar patterns remain descriptive and adaptable. Missing inputs affect only linked scopes, and grounded not_applicable needs neither dossier nor analyzer.

## Required fields

- Project brief: project/paper slug, topic, domain positioning, working thesis.
- Target venue, conference, journal, or venue family.
- Paper type: research article, conference paper, short paper, system paper, survey, benchmark, application, or other explicit type.
- Research topic in one sentence.
- Traffic / computer-science / AI positioning.
- Intended audience and reviewer expectation.
- Owner decisions and forbidden routes.

## Ask when missing

Ask one focused question at a time. Choose the next question adaptively from the unresolved owner decision or highest-leverage dependency; the following prompts are unordered examples:

- “What venue or venue family should this paper target?”
- “What paper type is this: method, system, experiment/benchmark, application, survey, or something else?”
- “In one sentence, what is the topic and domain positioning?”
- “Which route or claim boundary triggers scientific_commitment, argument_spine, material_local_tradeoff, or deliberate_divergence?”
- “What route should be avoided even if it sounds attractive?”

## Question card pattern

Use this card when D04 or the `project-route` blocker is first unresolved.

```text
Current stage: Route
Dimension / blocker: D04 / project-route
Why this matters: target route controls paper type, audience expectation, claim strength, and downstream writing route.
Mode chosen: focused-question, because this branch changes the argument spine or creates a material local tradeoff.
Question: Which target route should this paper use for planning?
Options:
A. intelligent-transportation journal/conference — write venue family, paper type, and reviewer expectation to 00_PROJECT_ROUTE.md#Target Route.
B. computer-science / AI method venue — write method-oriented audience and evidence expectations to 00_PROJECT_ROUTE.md#Audience and Reviewer Expectation.
C. application / systems venue — write deployment/system expectation and required material gaps to 00_PROJECT_ROUTE.md#Target Route.
D. defer route — continue Materials intake, but final 04_WRITING_DESIGN_PACK.md remains blocked until owner confirms route or explicitly accepts final-route deferral.
E. rejected route — record the forbidden route in 00_PROJECT_ROUTE.md#Forbidden Routes and keep it out of downstream handoff.
Agent action after answer: update 00_PROJECT_ROUTE.md#Target Route, including the paper-type line, or #Audience and Reviewer Expectation as applicable, then update D04 in 00_DIMENSION_INDEX.md.
```

## Additional question-card seeds

Use these cards only when their specific track is the current blocker. Keep one card active at a time.

### Front matter / hook route constraints

```text
Current stage: Route
Dimension / blocker: D04 with D09/D14/D15/D18/D19 / front-matter-hook constraints
Why this matters: front matter and visual-hook planning must respect route, paper type, evidence strength, and forbidden promises before downstream writing sees the pack.
Mode chosen: focused-question, because the proposed promise triggers scientific_commitment or argument_spine.
Question: Which planning constraint should govern title/abstract/keyword/hook handoff?
Options:
A. title/abstract constraint — record route-facing length, abstract type, tone, and forbidden promise notes in 00_PROJECT_ROUTE.md#Target Route and hand off wording to D19.
B. keyword scope constraint — record owner-confirmed domain/traffic/CS/AI keyword boundaries without drafting keyword text.
C. graphical or visual hook constraint — record whether a hook is existing, needed, deferred, or rejected, and link any visual dependency to D18 rather than inventing artwork or captions.
D. defer front matter — record downstream uncertainty and keep final D19 front-matter handoff constrained.
E. rejected hook/promise — write the forbidden promise to #Forbidden Routes or owner decisions and keep it out of downstream handoff.
Agent action after answer: update 00_PROJECT_ROUTE.md#Target Route, #Audience and Reviewer Expectation, or #Forbidden Routes, then update D04 and any D19 handoff note in 00_DIMENSION_INDEX.md.
```

### Reporting and reproducibility route seed

```text
Current stage: Route
Dimension / blocker: D04 with D05/D06/D13/D15/D19 / method-reporting-repro seed
Why this matters: article type and venue family determine which reporting, reproducibility, supplement, or availability constraints downstream planning must preserve.
Mode chosen: candidate-confirmation when route notes imply checklist candidates; focused-question when the owner must confirm a route-required statement.
Question: Which reporting or reproducibility route constraint should be recorded?
Options:
A. method/reporting checklist needed — record checklist categories such as protocol, parameters, baselines, metrics, ablations, or availability as D05/D06/D15 inputs.
B. availability/supplement statement needed — record the statement category as a D19 handoff constraint without drafting the statement.
C. route does not require a specific checklist — record owner-confirmed absence and downstream consequence.
D. defer checklist — keep D19 blocked for reporting/repro details until owner or materials confirm them.
E. rejected checklist claim — record that the project must not claim compliance or reproducibility beyond supplied artifacts.
Agent action after answer: update 00_PROJECT_ROUTE.md#Target Route and #Route Readiness, then update D04 and hand off material gaps to D05/D06/D15/D19 rows.
```

### Downstream route matrix seed

```text
Current stage: Route
Dimension / blocker: D01/D02/D04/D07/D08/D18/D19 / downstream route matrix seed
Why this matters: downstream writing, citation, figure, and review tools need recommendations and constraints, not automatic execution.
Mode chosen: focused-question, because owner decisions and external-route exclusions are authority-gated.
Question: Which downstream route should be seeded for the design-pack matrix?
Options:
A. writing/polishing route candidate — record route family and constraints for D19 without invoking a writing skill.
B. citation/source route candidate — record source/citation handoff needs from D07/D08 without searching or completing citations.
C. figure/accessibility route candidate — record D18 visual/caption/accessibility handoff needs without creating figures or captions.
D. no external route yet — record deferred route matrix seed and keep final handoff cautious.
E. rejected external route — record the forbidden route or tool category and prevent runtime execution language.
Agent action after answer: update 00_PROJECT_ROUTE.md#Owner Decisions or #Forbidden Routes and add a D19 handoff pointer in 00_DIMENSION_INDEX.md.
```

## Hard blocker

Block design-pack compilation if any of these are absent and not explicitly marked `not_applicable`, `absent`, `deferred`, or `rejected` with a reason in `00_DIMENSION_INDEX.md`:

- target venue/family;
- paper type;
- topic;
- traffic/computer positioning;
- unresolved decisions in one of the four owner-gate categories.

## Output sections

Update `00_PROJECT_ROUTE.md` with:

- Project brief;
- Target route;
- Paper type;
- Topic and positioning;
- Audience / reviewer expectation;
- Owner decisions;
- Forbidden routes;
- Route readiness.

## Index update examples

- Filled project brief: `D03 | filled | brief supplied by owner | 00_PROJECT_ROUTE.md#Project Brief | yes`.
- Deferred target journal: `D04 | deferred | owner has not chosen venue family | Handoff: ask owner before final design pack | yes`.

## Do not assume

- Do not infer a venue from writing style alone.
- Do not switch to medical/clinical route unless the owner explicitly asks.
- Do not claim journal fit as certain; record it as a working target.
