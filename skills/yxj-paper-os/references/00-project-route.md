# Playbook 00 — Project Route

Use this playbook when `00_PROJECT_ROUTE.md` is missing or incomplete, or when D01/D03/D04 in `00_DIMENSION_INDEX.md` are unhandled.

## Dimension IDs covered

| ID | Dimension | Home |
|---|---|---|
| D01 | `OWNER_DECISIONS.md` | `00_DIMENSION_INDEX.md` + `00_PROJECT_ROUTE.md#Owner Decisions` |
| D03 | `00_project_brief.md` | `00_PROJECT_ROUTE.md#Project Brief` |
| D04 | `01_target_journal_profile.md` | `00_PROJECT_ROUTE.md#Target Route` and `#Audience and Reviewer Expectation` |

After updating route content, update the matching D01/D03/D04 rows in `00_DIMENSION_INDEX.md` with status, reason, pointer/handoff, and `Blocks design pack?`.

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
