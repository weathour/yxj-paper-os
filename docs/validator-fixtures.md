# Validator fixtures

The fixture suite contains fifteen valid paper-control-plane fixtures and
ninety-six invalid fixtures:

- dispatch-as-complete;
- missing agent_type;
- missing source-map;
- unconfirmed motivation;
- shallow rationale matrix;
- unsupported claim;
- unrouted review finding;
- export without validation;
- private/raw leakage;
- collected without validator;
- validated without ingest;
- dispatched timeout without output;
- unknown owner lane;
- missing validator definition;
- unresolved source locator;
- partial validator evidence;
- missing artifact validator evidence;
- missing/corrupt PUA telemetry;
- L2 missing structured PUA-REPORT;
- L2 PUA-REPORT mismatch against top-level telemetry;
- L3 incomplete seven-item checklist;
- L4 inconsistent failure count;
- complete without explicit state_transition;
- complete with wrong state_transition target;
- complete with wrong pipeline stage.
- Nature-grade figure contract/aesthetic/evidence/backend/statistics/integrity/
  caption/export/rendered-surface failures.

Run `python3 skills/yxj-paper-index/scripts/run_fixture_suite.py .` from the plugin scaffold root.

## Expected-vs-extra failure contract

Each invalid fixture declares `expected_failures`. The fixture suite fails when expected failures are missing or when extra failures appear without an explicit `allowed_extra_failures` entry. This keeps broad cascading failures visible instead of silently accepting them.

## PUA telemetry fixture contract

Task-ledger fixtures include `pua_telemetry` and validator fixtures know
`validate_pua_telemetry`. Valid fixtures prove that L0 control telemetry coexists
with normal validator evidence. Invalid fixtures may still fail for dispatch,
validator, evidence, owner-lane, privacy, or ingestion reasons; PUA telemetry is
not allowed to mask those failures.

Invalid PUA telemetry fixtures intentionally omit, corrupt, or desynchronize
`pua_telemetry`/`pua_report` and should expect `validate_pua_telemetry`.


## V2 governance fixture coverage

Valid fixtures:

- `minimal-valid`: v1 compatibility fixture; proves old task packets still pass
  when they have complete collection, validator evidence, ingestion, and state
  transition.
- `v2-governance-valid`: v2 fixture; proves department binding, material I/O,
  narrative refs, template refs, validator evidence, ingestion, and state
  transition can close together.
- `expression-design-object-refs-additive`: v2 expression-design fixture; proves
  `expression_design_object_refs` can be added while `narrative_object_refs`,
  `template_object_refs`, and `evidence_object_refs` remain present.
- `v2plus-nature-figure-valid`: v2plus Nature-grade figure fixture; proves
  architecture, evidence/method, figure production, export, rendered-surface,
  and review lanes can close a final/export-facing figure through typed
  material objects and validator evidence.

Additional invalid v2 fixtures:

- `invalid-v2-missing-owner-department` expects
  `validate_agent_lane_department_binding`.
- `invalid-v2-missing-material-io` expects `validate_task_material_io`.
- `invalid-v2-missing-narrative-refs` expects
  `validate_narrative_object_binding`.
- `invalid-v2-missing-template-refs` expects
  `validate_template_object_binding`.
- `invalid-v2-missing-validator-ref` expects
  `validate_validator_reference_closure`.
- `invalid-v2-pseudo-complete-uncollected-material` expects
  `validate_task_material_io` and blocks the common pseudo-completion pattern:
  legacy output exists, but the declared v2 material output was not collected.

The suite also rejects empty valid/invalid matrices with
`validate_fixture_matrix_nonempty`, so a wrongly shaped suite command cannot
silently pass with no fixtures checked.

- `invalid-v2-self-declared-narrative-exception` expects
  `validate_narrative_object_binding`; a task-local exception cannot self-attest
  that required reader narrative refs are not applicable.
- `invalid-v2-self-declared-template-exception` expects
  `validate_template_object_binding`; a task-local exception cannot self-attest
  that required template refs are not applicable.
- `invalid-expression-design-replaces-narrative-refs` expects
  `validate_narrative_object_binding` and `validate_template_object_binding`;
  `expression_design_object_refs` is additive and cannot stand in for required
  reader narrative or template references on paper-facing writing work.
- The pseudo-completion fixture includes the raw expected material file but keeps
  it out of `collected_outputs` and `artifact-ledger`, proving raw file
  existence alone cannot close material I/O.

## Nature-grade figure fixture coverage

The valid fixture `v2plus-nature-figure-valid` exercises the complete material
chain:

- `NatureFigureContract` and `NatureFigureAestheticProfile`;
- `NaturePanelEvidenceMap`;
- `FigureBackendRoute`;
- `FigureSourceDataStatistics`;
- `FigureImageIntegrityRecord`;
- `NatureCaptionLegendBrief`;
- `FigureExportBundle`;
- `RenderedSurfaceGateReport`;
- `NatureFigureQAReport`.

Invalid fixtures pin each closure gate:

- `invalid-nature-figure-missing-contract` expects
  `validate_nature_figure_contract`.
- `invalid-nature-figure-missing-expression-refs` expects
  `validate_expression_design_object_binding`.
- `invalid-nature-figure-backend-exclusivity` expects
  `validate_figure_backend_route`.
- `invalid-nature-figure-panel-evidence-gap` expects
  `validate_panel_evidence_map`.
- `invalid-nature-figure-panel-material-ref-gap` expects
  `validate_panel_evidence_map` when panel statistics/image-integrity refs are
  missing.
- `invalid-nature-figure-panel-wrong-material-type` expects
  `validate_panel_evidence_map` when panel statistics/image-integrity refs
  resolve to the wrong material type.
- `invalid-nature-figure-missing-source-data-statistics` expects
  `validate_figure_source_data_statistics`.
- `invalid-nature-figure-missing-image-integrity` expects
  `validate_figure_image_integrity_record`.
- `invalid-nature-figure-image-integrity-not-applicable-wrong-route` expects
  `validate_figure_image_integrity_record` when a not-applicable image-integrity
  claim points to a raster/extracted backend route.
- `invalid-nature-figure-image-integrity-shadow-route` expects
  `validate_figure_image_integrity_record` when stale local
  `selected_route`/`backend_route` fields try to override the typed
  `FigureBackendRoute`.
- `invalid-nature-figure-missing-image-integrity-qa` expects
  `validate_nature_figure_qa_report`.
- `invalid-nature-figure-caption-private-leak` expects
  `validate_nature_caption_legend`.
- `invalid-nature-figure-caption-cross-platform-private-leak` expects
  `validate_nature_caption_legend` for macOS `/Users/...` and Windows
  `C:\Users\...` / `C:\users\...` / `C:/users/...` private path leaks,
  including lowercase `/users/...` aliases.
- `invalid-nature-figure-export-bundle-incomplete` expects
  `validate_figure_export_bundle`.
- `invalid-nature-figure-rendered-surface-gap` expects
  `validate_rendered_pdf_surface_text`,
  `validate_no_internal_codes_in_rendered_text`, and
  `validate_no_bare_citekeys_in_export`.

## Semantic object shape gate

Scaffold validation also checks the executable shape of the v2 reader/template objects: `ReaderSpineBrief`, `ObjectRepresentationMatrix`, `TemplateQuantProfile`, `SectionFunctionBudget`, `VisualTableAlgorithmFormulaBudget`, `ReaderExperienceReviewReport`, and `NarrativeBackflowTask`. This is a structural governance gate, not a license to invent paper-owner semantics.

## Repository hygiene fixture contract

`validate_repository_hygiene_report` rejects handoff/export fixtures that mark delivery cleanliness as pass while `RepositoryHygieneReport` contains disallowed dirty entries, sibling/parent contamination without an owner decision, stale snapshots, missing export-manifest hash checks, or no explicit external-submission boundary.

## Manager authority fixture coverage

The current manager-authority matrix extends the fixture suite. New valid
fixtures prove that manager-direct work can
close only when provenance, disclosure, and required independent review are
present. New invalid fixtures prove these blockers:

- `invalid-manager-direct-undeclared-paper-facing-complete`: manager execution is
  inferred but no intervention artifact is declared.
- `invalid-manager-direct-present-false-but-manager-actor`: self-report says no
  manager-direct work while actor provenance says manager execution.
- `invalid-provenance-artifact-missing-or-unparseable`: actor fields exist but
  the provenance artifact is missing or untrusted.
- `invalid-manager-direct-no-independent-review`: paper/state-sensitive
  manager-direct completion lacks independent review.
- `invalid-independent-review-same-effective-actor`: role names differ but the
  same effective actor executes/reviews/certifies.
- `invalid-low-risk-self-classified-paper-facing`: a paper-facing task tries to
  self-downgrade sensitivity.
- `invalid-manager-direct-hidden-from-handoff`: the intervention is absent from
  structured handoff disclosure.
- `invalid-manager-same-session-different-lane-reviewer`: the same manager/session
  changes lanes and still cannot count as an independent reviewer.
- `invalid-manager-direct-declared-paper-facing-no-review`: declared
  `manager_direct_intervention.present:true` paper-facing work still requires
  independent review even when manager execution was not inferred from provenance.
- `invalid-independent-review-artifact-missing`: non-empty review paths are not
  trusted unless the review artifact exists and parses.
- `invalid-independent-review-wrong-task`: review artifacts must bind to the same
  `task_id`.
- `invalid-independent-review-reject-verdict`: rejecting review verdicts cannot
  authorize completion.
- `invalid-independent-review-reviewer-mismatch`: review artifacts must bind to
  the declared reviewer effective actor.
- `invalid-manager-direct-false-handoff-block`: a default/false
  `authority_role_separation` block is not truthful disclosure.
- `invalid-provenance-source-hash-missing`: file-backed provenance must include
  source hash evidence and `source_hash_verified:true`.
- `invalid-manager-direct-authority-refs-omitted`: authority-relevant manager-direct
  tasks cannot opt out by stripping authority validators from `validator_refs`;
  content-triggered governance still fails `validate_validator_reference_closure`.
- `invalid-provenance-producer-mismatch`: provenance producer must match the
  task executor actor key.
- `invalid-provenance-certifier-mismatch`: provenance certifier must match the
  task final-certifier actor key.
- `invalid-provenance-material-ref-mismatch`: provenance material refs must be
  declared task input materials.
- `invalid-provenance-output-ref-mismatch`: provenance output refs must be
  declared task output/collection materials.
- `invalid-provenance-source-hash-mismatch`: local `source_path` hash must match
  the artifact `source_hash` when `source_hash_verified:true` is claimed.

These fixtures are intentionally stronger than prose policy: the suite fails if
any expected authority validator is absent or if an unapproved cascade appears.


## Nature full-absorption fixtures

The fixture matrix now includes `fixtures/valid/v2plus-nature-full-absorption-valid/` and targeted invalid fixtures for public `nature-*`/hidden-manager leakage, missing root absorption refs/backflow, PPT ownership drift to export-only, invented data identifiers, invented response line numbers or missing reviewer IDs, and missing patent boundary disclaimers/professional review gates. Current expected fixture suite size after this milestone is 15 valid / 96 invalid.
