---
name: yxj-paper-os
description: Prepare and inspect a paper-planning workspace with a sparse cognitive kernel, composable academic lenses, and scoped writing handoffs.
---

# yxj-paper-os: thin cognitive kernel

This skill is model-led reasoning over one public skill and six Markdown workspace files. It is not a fixed workflow, state machine, form-completion score, or semantic judge. Read the whole situation, inspect/derive before asking, and use only the sparse records needed for the requested scope.

## Public contract

- Preserve the six filenames, D00-D19 index, public index columns/status values, and schema version `0.2`.
- Initialize only from `assets/templates/`; never create a seventh public workspace file.
- `04_WRITING_DESIGN_PACK.md` is a structural, scoped handoff. It never claims research, manuscript, submission, publication, or semantic readiness.
- The dashboard is read-only and writes only `<workspace>/.yxj-paper-os/dashboard.html`.

## Five kernel invariants

1. **Epistemic distinction:** substantive decision/material/claim records distinguish origin (`artifact-observed`, `owner-stated`, `model-derived`, `model-proposed`), claim support (`evidence-supported`, `evidence-partial`, `evidence-unsupported`, `not_applicable`), resolution, and grounding.
2. **Whole-situation synthesis:** consider all six files, available local artifacts, owner statements, active conflicts, changed records, and requested writing surface before choosing what to do.
3. **Qualitative highest-value action:** choose the action that most reduces consequential uncertainty or unlocks the requested surface. Do not use a numeric score, fixed scan order, or one-question script.
4. **Dependency recheck:** when a DEC/M/C record changes, update a parseable Dependency Recheck declaration for affected D IDs/scopes; recheck or mark only those dependents stale/candidate/blocked.
5. **Scoped writer-ready:** judge each requested `SCOPE-*` independently. A ready scope has declared inputs, satisfied/not-applicable requirements, no stale/candidate/blocked dependency, blocker=`none`, next action=`none`, and a resolvable output pointer. Other scopes remain partial, blocked, or deferred.

## Canonical action families

Use any zero or more of these unordered families in a turn:

`inspect`, `record-observation`, `derive`, `propose`, `reconcile`, `ask-owner`, `dependency-recheck`, `compile-scoped-handoff`, `keep-claim-inactive`, `initialize-workspace`.

Actions describe judgment, not runtime states. Simple metadata edits remain lightweight. Optional native subagents are allowed only when volume, ambiguity, or claim risk materially benefits; they never become mandatory stages and never ask the owner or execute downstream skills directly.

## Composable lenses

Load `references/lenses/README.md` and then only relevant modules. Lenses may compose from 0..N IDs; they are not exclusive paper types. The canonical registry maps module files to IDs, including method/system/benchmark forms in `contribution-evidence-forms.md` and the conditional `venue-template` lens. An inactive lens creates no empty requirement table and does not block unrelated scopes.

Every lens provides activation signals, theory/distinctions, sufficiency predicates, safe derivations, owner-only decisions, dependency invalidation, failure modes, workspace projection, and writer-ready consequences. Theory informs judgment; it never prescribes question order.

## Sparse recording rules

Only record a conditional table when it carries real information:

- `00_DIMENSION_INDEX.md`: `Writing Scopes` is the universal readiness registry; Active Lenses, Conditional Requirements, and Dependency Recheck are conditional.
- `00_PROJECT_ROUTE.md`: add Decision Records only for consequential choices/conflicts.
- `01_MATERIALS_INVENTORY.md`: add Material Records only for real artifacts/facts/results/evidence/source/governance/absence records.
- `02_CLAIM_EVIDENCE_BOUNDARY.md`: add Claim Records only for proposed, active, downgraded, deferred, or rejected claims.
- `03_WRITING_STRUCTURE.md`: add Scoped Writing Plan when designing a requested surface.
- `04_WRITING_DESIGN_PACK.md`: add Scoped Handoff when compiling D19.

Blank cells are invalid. Use literal `none` only where the table contract permits it. Free prose is not a foreign key. Preserve local artifact locators and six-file `file#heading` pointers. `model-proposed` records remain candidate/unresolved/rejected; acceptance creates a new grounded record rather than mutating origin.

## Adaptive operating guidance

1. Inspect existing files, local materials, and the requested output surface; initialize missing files only when asked.
2. Synthesize all relevant dimensions and active lenses. Record direct observations and safe derivations before asking.
3. Ask one concise owner question only for an unresolved consequential commitment, authority conflict, evidence permission, or wording choice. State consequence and landing pointer; offer defer/absent when valid.
4. Write the answer/observation to its canonical sparse record, update the relevant D row, and declare dependent rechecks when a DEC/M/C record changes.
5. Compile or refresh only the affected scoped handoff. Keep unrelated scope blockers explicit.
6. Run `python3 skills/yxj-paper-os/scripts/verify_design_pack.py <workspace>` for structural lint, and add `--require-handoff` only when a scoped D19 handoff is requested.

## Question card (optional rendering)

```text
Decision / observation: <one answerable item>
Why it matters: <affected scope or dependency>
What is already observed/derived: <short grounded summary>
Owner choice if needed: A ...  B ...  C defer/absent
Write landing: <file#heading and D row>
```

## Boundaries

Do not draft manuscript prose, invent claims/evidence/sources/results, search citations by default, execute external skills, write outside the six workspace files (except the hidden dashboard), add runtime services, or claim scholarly quality. Mechanical validators check structure and declared relations only; they do not prove academic truth, novelty, venue fit, statistics, prose quality, or future model behavior.
