# Target Delivery Contract

`yxj-paper-os` separates **stage-local material validity** from **target-global delivery truth**. An S16 export handoff package can be structurally valid as build/export hygiene while still not satisfying a user target such as “initial compiled draft PDF”.

S16 therefore requires `payload.delivery_target` in `ppg-s16-export-handoff-package/v0.1`. This is an intentional v0.1 safety hardening: legacy S16 materials without `delivery_target` must be regenerated or patched with an explicit non-compiled target before validation.

## Target kinds

- `export_hygiene_handoff`: build/export/repository hygiene handoff only.
- `template_only_handoff`: explicitly template-only handoff; never satisfies a compiled draft target.
- `materials_only`: graph/material package only; no PDF delivery claim.
- `compiled_initial_draft`: initial owner-readable content-bearing compiled manuscript PDF.
- `revised_compiled_pdf`: revised owner-readable content-bearing compiled manuscript PDF.

## Compiled-PDF invariant

For `compiled_initial_draft` and `revised_compiled_pdf`, S16 must fail closed unless all critical readiness states are `pass`, source-writeback evidence exists, post-writeback validation exists, and rendered/live text evidence proves a content-bearing manuscript surface. `content_ready: blocked`, template-only text, `Manuscript Not Started`, placeholder sentinels, or missing bibliography/body evidence cannot satisfy the compiled target.

## Target binding

When the controller has an owner/manager/runtime active target, `delivery_target.active_target_kind` and `delivery_target.active_target_ref` bind the S16 package to that target. A compiled active target cannot be downcast to `template_only_handoff` or `export_hygiene_handoff`.

## Standalone boundary

This contract is owned by yxj-paper-os schemas, validators, registry, and docs. OMX/yxj-paper-auto may read it as a personal orchestration adapter, but they are not runtime dependencies or authority sources.
