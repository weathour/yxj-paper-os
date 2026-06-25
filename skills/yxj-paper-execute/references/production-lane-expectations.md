# Production lane expectations — yxj-paper-os

This reference defines production-facing task shapes for `yxj-paper-execute`.
It does not implement validators or mutate shared lane registry/fixture files.

## Shared production rule

Manuscript and figure production tasks are not allowed to complete from prose
quality alone. They must consume the relevant construction/evidence objects and
return material outputs that can be collected, validated, ingested, and state
transitioned.

Minimum required inputs for paper-facing production:

- `ReviewerQuestionMap` or accepted non-applicable reason;
- `MainTextConstructionMatrix` row(s) for the target section/unit;
- evidence refs through `ClaimCitationCapsule` and/or `ResultPackage` when a
  claim, result, method, citation, figure, table, or caption is touched;
- `SingleWriterSectionLock` when editing a manuscript section or shared hotspot;
- target output path and collection path;
- validator refs and backflow route.

## Section-writing task

Purpose: produce or substantially rewrite a manuscript section/unit from approved
architecture and evidence materials.

Required task-packet fields:

- `owner_department: manuscript_and_figure_production`;
- `owner_lane: manuscript-owner` or a future section-writing alias;
- `narrative_object_refs` including `ReviewerQuestionMap` and
  `MainTextConstructionMatrix` rows;
- `evidence_object_refs` for every factual/result/method claim;
- `template_object_refs` when exemplar form or venue budget governs the section;
- `single_writer_lock.required: true` for section file edits;
- validator refs for task packet, material I/O, narrative binding, evidence
  support, and surface rules.

Expected outputs:

- section draft or patch path;
- consumed matrix row ids;
- claim/evidence refs used;
- unresolved owner decisions;
- backflow items when the section cannot be completed safely.

## Content-refinement task

Purpose: improve already drafted text without changing claim boundary, evidence
scope, or paper-owner semantic decisions.

Required behavior:

- preserve `ClaimCitationCapsule` and `ResultPackage` boundaries;
- keep section purpose and reviewer question alignment;
- report any desired claim expansion as backflow to Evidence & Method, not as a
  direct rewrite;
- keep citations/source locators attached to affected sentences;
- produce a diff-oriented output or span-level revision notes.

Forbidden behavior:

- converting future evidence branches into current Results claims;
- replacing bounded evidence wording with broader claims;
- deleting caveats required by ResultPackage;
- using raw internal codes or snake_case identifiers in main prose.

## Reader-surface-translator task

Purpose: translate internal planning/experiment/method identifiers into reader-
facing manuscript language without changing the underlying evidence boundary.

Required checks:

- translate scenario family codes such as `S0/S1/S3/S4/S5` when they appear in
  main prose;
- translate snake_case implementation constraints into natural language;
- translate raw method ids such as `VG-KZTR_full`, `B2_*`, or `no_*` into reader
  labels;
- convert defensive claim walls into readable scope/future-work logic;
- flag bare citekeys or renderer placeholders for export/review backflow;
- preserve tables/supplements/provenance paths where internal ids are explicitly
  allowed.

Expected outputs:

- span-level source and rendered-text notes;
- rewritten reader-facing text or patch;
- unresolved spans routed to `ReaderSurfaceTutorReview` / Review & Governance;
- validator requirements for G006 surface validators.

## Shared-file restriction

Production lanes do not directly edit shared validator scripts, fixture runners,
fixture case directories, or the lane registry. They may provide requirements or
patch snippets to the owning PMO/validator lanes.
