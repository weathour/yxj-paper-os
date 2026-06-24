---
name: yxj-paper-export
description: "Validate and package yxj-paper-os exports, including PDF/LaTeX/Word packages, export manifests, build reports, validation evidence, residual risks, and submission-readiness checks. Use only after state/evidence/review gates pass."
---


# yxj-paper-export

Do not export as ready unless source artifacts, build reports, validation evidence, and residual risks are recorded.

Export is blocked when claim validation, review backflow, or privacy checks fail. Active submission or external production upload requires separate explicit confirmation.

## Reader-facing export surface gate

A successful PDF/LaTeX build is necessary but not sufficient. Export validation
must also inspect the rendered artifact as a reader would see it.

Before marking an export-ready or manuscript-facing task complete, check the
rendered PDF/text output for:
- raw citekeys or renderer placeholders such as `(see: citekey)`;
- internal scenario/family codes in main explanatory prose or figure labels;
- snake_case implementation identifiers and trace internals;
- raw method ids instead of reader-facing method names;
- defensive claim-boundary walls where scope should be explained naturally.

Use validator refs such as `validate_no_bare_citekeys_in_export` and
`validate_rendered_pdf_surface_text` in the task ledger. A build that passes but
leaks internal planning language remains `needs_backflow`, not `complete`.


## Authority gate for export readiness

Export readiness is blocked when manuscript/export changes were manager-direct and
lack trusted provenance, independent review, final-certifier separation, or the
structured YAML `authority_role_separation` handoff disclosure. A successful build
plus manager certification remains `candidate` or `validated`, not `complete`, until
those authority gates pass.
