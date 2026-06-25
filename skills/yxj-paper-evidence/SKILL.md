---
name: yxj-paper-evidence
description: "Maintain yxj-paper-os source maps, citation support banks, evidence banks, claim support maps, yxj-wiki locators, privacy boundaries, and unresolved source locators. Use whenever manuscript claims, citations, or experiment evidence must be checked."
---


# yxj-paper-evidence

Every claim must have an evidence, citation, or paper-owner source anchor, or be marked unresolved.

## Source rules

Use locators, hashes, anchors, and summaries for private or licensed material. Do not copy raw unpublished manuscripts or private PDFs into tracked notes without explicit authorization.

Validate with `validate_source_map`, `validate_citation_support_bank`, `validate_evidence_bank`, `validate_claim_support`, `validate_privacy_boundaries`, and `validate_source_locator_resolution`.



## ClaimCitationCapsule

Use `ClaimCitationCapsule` when a manuscript claim needs a source, citation, or
project-evidence anchor before it can be consumed by writing or review.

Required fields:

- `claim_id` and exact claim text/location;
- `query` describing the support question;
- `source_locator` with citekey/path/anchor/hash where applicable;
- `supporting_snippet` as a bounded paraphrase or authorized quote reference;
- `support_strength` and risk flags;
- `bibtex_key` where a bibliographic citation is used;
- `usable_sentence.allowed_wording` and `forbidden_wording`.

Validator requirement for Lane E: `validate_claim_citation_capsule_support` must
reject citation-only capsules without a source locator and support snippet.

## ResultPackage

Use `ResultPackage` when experiment, ablation, baseline, metric, or figure/table
evidence is promoted into a manuscript result claim.

Required fields:

- `result_id` and `source_locator` for the result artifact;
- `supported_claim` with the exact claim boundary;
- `metric_anchor` and `figure_table_anchor`;
- `allowed_wording` and `forbidden_wording`;
- `reviewer_risk` and mitigation;
- `promotion_status`;
- future-evidence branch information when the result is not yet admissible for
  the Results section.

Validator requirement for Lane E: `validate_result_package_claim_boundary` must
reject packages without source locator, metric/figure anchor, or allowed/forbidden
wording, and must prevent future-evidence branches from being presented as current
Results evidence.

## Evidence-to-writing handoff

Evidence materials are not prose. Writing lanes consume `ClaimCitationCapsule` and
`ResultPackage` through `MainTextConstructionMatrix` so that manuscript sentences
inherit source boundaries, support strength, and reviewer risk instead of copying
raw experiment records.
