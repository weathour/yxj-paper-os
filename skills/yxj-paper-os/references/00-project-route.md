# Playbook 00 — Project Route

Use this playbook when `00_PROJECT_ROUTE.md` is missing or incomplete, or when D01/D03/D04 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension rubric reference

For minimum/standard/ideal sufficiency, proposal permission, owner-confirmation rules, status examples, and stop/defer/reject behavior for the D IDs covered here, consult `00-dimension-rubric.md`. That file is a central internal rubric/reference, not a sixth task playbook and not a public workspace file. Do not duplicate its full D00-D19 rubric here.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D01 | `OWNER_DECISIONS.md` | `00_DIMENSION_INDEX.md` + `00_PROJECT_ROUTE.md#Owner Decisions` |
| D03 | `00_project_brief.md` | `00_PROJECT_ROUTE.md#Project Brief` |
| D04 | `01_target_journal_profile.md` | `00_PROJECT_ROUTE.md#Target Route` and `#Audience and Reviewer Expectation` |

After updating route content, update the matching D01/D03/D04 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

## First-batch D04 route/profile pointer

`00-dimension-rubric.md` remains the source of truth for D04 sufficiency. In this playbook, treat D04 as a focused venue/profile card, not as a full rubric copy:

- Separate owner-confirmed route from agent-inferred audience or reviewer expectation.
- Capture category-family intent for venue family, article type, content/format/reporting fit, primary audience, reviewer expectation, hard constraints, forbidden routes, and owner confirmation state.
- Record route/profile uncertainty as `deferred` or explicit owner-accepted final-route deferral; do not silently convert dossier notes, exemplars, or writing style into a venue decision.
- Use hard constraints to constrain D14 reader path, D15 section jobs, D18 visual format/storyline, and D19 submission blueprint.
- Mechanical checks may confirm that route/profile content and pointers exist; they must not judge actual venue fit, novelty, or acceptance likelihood.

## Required fields

- Project brief: project/paper slug, topic, domain positioning, working thesis.
- Target venue, conference, journal, or venue family.
- Paper type: research article, conference paper, short paper, system paper, survey, benchmark, application, or other explicit type.
- Research topic in one sentence.
- Traffic / computer-science / AI positioning.
- Intended audience and reviewer expectation.
- Owner decisions and forbidden routes.

## Ask when missing

Ask one focused question at a time. Prefer this order:

1. “What venue or venue family should this paper target?”
2. “What paper type is this: method, system, experiment/benchmark, application, survey, or something else?”
3. “In one sentence, what is the topic and domain positioning?”
4. “Which route or claim boundary is owner-gated and should not be inferred automatically?”
5. “What route should be avoided even if it sounds attractive?”

## Question card pattern

Use this card when D04 or the `project-route` blocker is first unresolved.

```text
Current stage: Route
Dimension / blocker: D04 / project-route
Why this matters: target route controls paper type, audience expectation, claim strength, and downstream writing route.
Mode chosen: focused-question, because venue family and paper type are owner-gated branch decisions.
Question: Which target route should this paper use for planning?
Options:
A. intelligent-transportation journal/conference — write venue family, paper type, and reviewer expectation to 00_PROJECT_ROUTE.md#Target Route.
B. computer-science / AI method venue — write method-oriented audience and evidence expectations to 00_PROJECT_ROUTE.md#Audience and Reviewer Expectation.
C. application / systems venue — write deployment/system expectation and required material gaps to 00_PROJECT_ROUTE.md#Target Route.
D. defer route — continue Materials intake, but final 04_WRITING_DESIGN_PACK.md remains blocked until owner confirms route or explicitly accepts final-route deferral.
E. rejected route — record the forbidden route in 00_PROJECT_ROUTE.md#Forbidden Routes and keep it out of downstream handoff.
Agent action after answer: update 00_PROJECT_ROUTE.md#Target Route, including the paper-type line, or #Audience and Reviewer Expectation as applicable, then update D04 in 00_DIMENSION_INDEX.md.
```

## Hard blocker

Block design-pack compilation if any of these are absent and not explicitly marked `not_applicable`, `absent`, `deferred`, or `rejected` with a reason in `00_DIMENSION_INDEX.md`:

- target venue/family;
- paper type;
- topic;
- traffic/computer positioning;
- owner-gated decisions that affect claims or route.

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
