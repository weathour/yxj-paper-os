# Scoped Design-Pack Compiler Guide

This guide projects a whole-situation model and active lenses into `04_WRITING_DESIGN_PACK.md`. It is not a workflow, state machine, or semantic quality judge.

## Dimension and content homes

| Home | Dimensions | Compiler responsibility |
|---|---|---|
| Route | D00-D04 | preserve owner decisions, route constraints, and explicit deferrals |
| Materials | D05-D08 | carry locators, statuses, absences, source roles, and governance boundaries |
| Claims | D10-D13 | carry claim/evidence/warrant/scope/uncertainty and wording limits |
| Structure | D09, D14-D18 | derive reader/section jobs, visual responsibilities, and drafting boundaries |
| Handoff | D02, D19 | compile scope readiness, dependency declarations, blockers, and next actions |

## Compile decision

Compile or refresh D19 whenever the requested scope has coherent declared inputs. Do not wait for unrelated scopes, inactive lenses, or missing venue templates. For each requested scope:

- `writer-ready` only when blocker and next action are `none`, output pointer resolves, requirements are satisfied/not_applicable, and no stale/candidate/blocked dependency affects it;
- `partial`, `blocked`, or `deferred` must carry a concrete blocker and next action;
- zero scopes is valid for initialization/metadata-only lint, but `--require-handoff` needs at least one.

## Dependency recheck

When a DEC/M/C record changes, add one `Dependency Recheck` row with the changed record, affected D IDs/scopes, disposition, and resolution/next action. Recheck only declared dependents; retain unrelated material observations. The validator checks the declaration, not an inferred graph.

## Progressive lens projection

Activate 0..N lens IDs when their activation signals matter to the requested scope. Omit inactive lens and requirement tables rather than creating empty rows. A `venue-template` lens constrains only explicitly linked route/style/front-matter work. Lens theory informs safe derivation and owner questions; it never prescribes an order.

## Handoff contents

A scoped handoff may contain:

- route/objective/RQ and owner decisions;
- material record IDs, locators, statuses, and explicit absences;
- active claims with evidence IDs, warrant, scope, uncertainty, and allowed/forbidden wording;
- reader and section jobs with input record IDs and drafting boundaries;
- visual/accessibility responsibilities;
- blockers, stale/candidate content, and next actions;
- an explicit statement that the pack is structural/scoped planning only.

Do not draft manuscript prose, invent citations/results, execute downstream skills, or claim research/manuscript/submission/publication/semantic readiness.

## Compiler actions

Use `inspect`, `record-observation`, `derive`, `propose`, `reconcile`, `ask-owner`, `dependency-recheck`, `compile-scoped-handoff`, and `keep-claim-inactive` as unordered action families. Ask one concise question only for a consequential unresolved owner choice; otherwise record or derive safely.
