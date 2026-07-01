# LaTeX Source-Writeback Protocol

This protocol upgrades `yxj-paper-os` from source-read-only runtime pilots to controlled LaTeX source promotion. It does not create a new all-powerful “LaTeX master” route. Instead, it adds a source-writeback promotion layer to the existing stages.

## Design decision

Real manuscript rewriting belongs inside the existing stage chain:

- `S10` writes or rewrites bounded manuscript text units.
- `S11` writes or regenerates figures, captions, formal artifacts, and figure provenance.
- `S12` integrates and validates the patched paper.
- `S13` produces actionable review findings.
- `S14` compiles local repair tasks.
- `S15` applies bounded repair patches and regenerates affected outputs.
- `S16` proves build/export/repository hygiene while submission remains owner-gated.

A separate global LaTeX-writing route is forbidden because it would bypass claim, terminology, figure, and backflow gates.

## Promotion model

The source-writeback model is a controller-owned state transition:

```text
candidate artifact
  -> patch proposal
  -> pre-apply snapshot
  -> scoped source apply
  -> post-apply snapshot
  -> LaTeX/template build
  -> claim/terminology/rendered-surface validation
  -> graph commit or rollback
```

Workers may generate candidate text, figure scripts, captions, or patch proposals. They may not mark source writeback complete. The controller records the patch manifest and validation evidence.

## Implemented executor surface

The implemented writeback surface is deliberately small and auditable:

- `scripts/verify_latex_writeback_contract.py` validates the `LatexWritebackPlan`;
- `scripts/execute_latex_writeback_plan.py` dry-runs or applies one stage-scoped `LatexWritebackPatchset`;
- `scripts/verify_latex_writeback_execution.py` copies a fixture paper to a temporary git repository, proves dry-run non-mutation, rejects unsafe paths, applies an `S10` marker-bounded LaTeX patch by default, runs `latexmk`, checks the generated PDF, and creates a scoped git commit.

The executor supports three controlled operations:

1. `replace_between_markers` for template-preserving body injection;
2. `replace_file` for bounded source-unit replacement;
3. `copy_file` for generated figure/source artifacts from a candidate root.

For ordinary local paper iteration, apply is the default once a valid plan and patchset exist. The executor records a pre-apply snapshot, materializes only stage-declared targets, runs the LaTeX build command, checks changed files against the plan, and restores the pre-apply contents if any apply-time validator fails. After successful validation it creates a scoped git commit for the changed source files. `--dry-run` remains available for inspection, and `--no-git-commit` is available for exceptional local debugging.

This means the owner should not be asked for a separate “may I write the manuscript?” confirmation during normal local production. The owner gate remains for semantic route changes, template changes that alter paper structure/claims, cross-repository writes, external submission/upload, and other irreversible external actions.

## Writeback plan fields

A `LatexWritebackPlan` must declare:

- `workspace_manifest_ref`: the paper workspace manifest used for path roles;
- `source_root`: the paper repository root;
- `latex_profile`: main file, engine, build commands, output PDF, template roots, and adapter policy;
- `stage_writebacks`: scoped writeback entries for `S10`, `S11`, `S12`, `S15`, and `S16`;
- `local_apply_policy`: default local execution mode, confirmation policy, rollback policy, and scoped git-commit policy;
- `allowed_source_write_paths`: exact files or narrow globs under `manuscript/`, `figures/src/`, or `figures/generated/`;
- `forbidden_source_write_paths`: generated build directories, exports, broad roots, `.git`, `.omx`, and sibling projects;
- `validators`: build, diff, claim, terminology, figure provenance, rendered-surface, and template compatibility gates;
- `rollback_policy`: how to restore the pre-apply snapshot if any validator fails;
- `owner_gate`: explicit owner authorization for export/submission, not for ordinary local patch validation.

## Template adaptation

The LaTeX conversion/build skill is used as a helper inside S10/S11/S12, not as a public route. It supplies these implementation tactics:

1. parse the target template's document class, front matter, bibliography style, and body insertion slots;
2. preserve the template preamble unless a missing package is required for existing content;
3. inject body sections through manifest-declared units instead of manual copy-paste;
4. normalize figure paths relative to the active `main.tex`;
5. compile with the manifest-declared command and inspect the log;
6. record all template-specific fixes in `paper-os/writeback/template-adapter-report.json`.

## Stage-specific writeback rules

### S10 — main text

Allowed outputs: patch proposals for `manuscript/sections/*.tex`, plus a candidate-return record. S10 must not edit build products, exports, evidence packages, or sibling repositories.

### S11 — figures and captions

Allowed outputs: editable figure sources, generated figure files, provenance/hash records, and caption patches. S11 must prove source-data locators and caption claim support.

### S12 — integration

Allowed outputs: validation reports and, only when declared, minimal integration patches such as include order or cross-reference fixes. S12 must run LaTeX build, reference/citation checks, figure-text checks, and claim-boundary checks.

### S15 — repair execution

Allowed outputs: patches limited to the stale/affected downstream set. S15 must prove unrelated nodes are unchanged and the original review finding is resolved.

### S16 — export/handoff

Allowed outputs: export manifest, repository hygiene report, handoff update, and optional export package. Submission/upload is never automatic.

## Safety invariants

- Default unplanned worker/runtime writes remain `source_write_forbidden: true`.
- Planned local source writeback defaults to apply/build/validate/commit/rollback through a valid `LatexWritebackPlan`.
- Source writeback requires a valid `LatexWritebackPlan`, a valid `LatexWritebackPatchset`, and a pre-apply snapshot.
- Broad roots such as `.` or `manuscript/` are not valid write targets by themselves.
- A passed worker lane is not enough; the controller must run validators and record commit evidence.
- Generated PDFs and exports are never the source of truth.

## Validation commands

```bash
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```

The execution verifier is fixture-based and does not edit a real paper repository. Real manuscript writeback still requires a valid workspace manifest, a valid writeback plan, a candidate patchset, and successful post-apply validation; it does not require an extra human confirmation for ordinary local manuscript writes.
