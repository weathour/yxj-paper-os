# RenderedManuscriptAuditGate

`RenderedManuscriptAuditGate` is the downstream rendered-quality audit after S16 export/handoff evidence exists. It is not a replacement for S00-S16, and S16 is not allowed to substitute for this gate.

## Purpose

S16 proves export, build, manifest, repository, and handoff hygiene. `RenderedManuscriptAuditGate` consumes S16 evidence plus the rendered PDF/text sidecar and asks whether the owner-facing rendered manuscript surface is paper-quality enough for the active target.

It checks rendered semantics and presentation after source writeback/export, including:

- content-bearing body text and section structure;
- body citation anchors and rendered reference entries;
- figure/table/formal-artifact callouts, placement, captions, labels, and exported artifact bindings;
- claim/caveat/evidence consistency against S12/S13/S14/S15 closure;
- absence of template-only text, internal lexicon leakage, missing-material notes, and manager-risk prose in paper-facing text;
- readability, visual surface, obvious layout/render anomalies, and owner-handoff limitations.

## Inputs

The gate must inherit enough S16 evidence to avoid re-guessing:

- `s16_export_handoff_package_ref`;
- `output_pdf_ref`;
- `rendered_text_ref` generated from the same output PDF;
- `file_hash_manifest_ref` and hashes for the PDF/text sidecar/artifacts;
- `source_writeback_evidence_ref` and `post_writeback_validation_ref` for compiled targets;
- S12/S13/S14/S15 closure references and unresolved-risk state.

If any of these are missing for a compiled target, the gate blocks and routes to the nearest responsible stage. It must not downcast a compiled target to template-only handoff.

## Severity policy

- `BLOCKING`: rendered manuscript cannot support owner review for the active target; route to S14/S15/S12/S16 as appropriate.
- `MAJOR`: substantial quality, evidence, citation, reference, figure, or semantic-surface defect; route to S14 with nearest responsible stage evidence.
- `MINOR`: local polish, copy, spacing, label, or wording issue that can be repaired locally and does not invalidate the rendered manuscript surface.
- `WATCH`: risk or preference signal that should be visible to the owner/reviewer but does not block handoff by itself.

`MINOR` and `WATCH` findings are tracked; they do not force a full rerun or block by default. A pass decision is allowed only when no unresolved `BLOCKING` or `MAJOR` finding remains and template-only/internal-risk leakage checks pass.

## Authority boundary

The gate may return an audit decision and findings. It cannot claim submission, publication, or scientific acceptance. Owner submission remains owner-gated. Repairs route through S14/S15 or the nearest accountable upstream stage; the gate does not rewrite the manuscript.

## Schema and verifier

- Schema: [`schemas/ppg-rendered-manuscript-audit-gate.schema.json`](../schemas/ppg-rendered-manuscript-audit-gate.schema.json)
- Verifier: [`scripts/verify_rendered_manuscript_audit_gate.py`](../scripts/verify_rendered_manuscript_audit_gate.py)
- Positive fixture: [`examples/delivery/rendered_manuscript_audit_gate.pass.json`](../examples/delivery/rendered_manuscript_audit_gate.pass.json)
