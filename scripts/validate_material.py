#!/usr/bin/env python3
"""Validate PPG material fixture envelopes and Phase 4 P1 payload semantics."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        as_mapping,
        as_sequence,
        issue,
        is_non_empty_mapping_list,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )
except ImportError:  # pragma: no cover - script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        as_mapping,
        as_sequence,
        issue,
        is_non_empty_mapping_list,
        is_non_empty_string,
        is_non_empty_string_list,
        lint_paper_facing_terms,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
        validate_runtime_status,
    )


ALLOWED_CLAIM_STRENGTHS = {
    "bounded",
    "bounded-method-evidence",
    "descriptive",
    "evidence_supported",
    "limited",
    "qualified",
}


def _payload(data: dict[str, Any], errors: list[ValidationIssue]) -> dict[str, Any] | None:
    payload = as_mapping(data.get("payload"))
    if payload is None:
        errors.append(issue("E_PAYLOAD_REQUIRED", "payload mapping is required"))
    return payload


def _validate_evidence_inventory(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    packages = payload.get("evidence_packages")
    if not is_non_empty_mapping_list(packages):
        errors.append(issue("E_PAYLOAD_REQUIRED", "EvidenceInventory.evidence_packages must be a non-empty list of mappings"))
        return
    assert isinstance(packages, list)
    for idx, package in enumerate(packages):
        assert isinstance(package, dict)
        if not is_non_empty_string(package.get("id")) or not is_non_empty_string(package.get("claim_strength")):
            errors.append(issue("E_PAYLOAD_REQUIRED", f"evidence_packages[{idx}] needs string id and claim_strength"))


def _valid_guardrail_list(payload: dict[str, Any], field: str, errors: list[ValidationIssue]) -> bool:
    if field not in payload:
        return False
    value = payload.get(field)
    if not is_non_empty_string_list(value):
        errors.append(issue("E_PAYLOAD_REQUIRED", f"ClaimBoundaryMap.{field} must be a non-empty list of strings"))
        return False
    return True


def _validate_claim_boundary_map(data: dict[str, Any], payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    raw_allowed_claims = payload.get("allowed_claims")
    allowed_claims = as_sequence(raw_allowed_claims)
    if raw_allowed_claims is not None and not is_non_empty_mapping_list(raw_allowed_claims):
        errors.append(issue("E_PAYLOAD_REQUIRED", "ClaimBoundaryMap.allowed_claims must be a non-empty list of mappings"))
        return
    if not allowed_claims:
        status = data.get("status")
        if isinstance(status, str) and status in {"committed", "stale"} and not data.get("candidate_for"):
            errors.append(issue("E_PAYLOAD_REQUIRED", "ClaimBoundaryMap.allowed_claims must be non-empty for committed/stale material"))
        return

    invalid_strength = False
    for idx, claim in enumerate(allowed_claims):
        if not isinstance(claim, dict):
            errors.append(issue("E_PAYLOAD_REQUIRED", f"allowed_claims[{idx}] must be a mapping"))
            continue
        if not is_non_empty_string(claim.get("id")):
            errors.append(issue("E_PAYLOAD_REQUIRED", f"allowed_claims[{idx}].id must be a non-empty string"))
        strength = claim.get("strength")
        if not isinstance(strength, str) or strength not in ALLOWED_CLAIM_STRENGTHS:
            invalid_strength = True
            errors.append(issue("E_CLAIM_STRENGTH_INVALID", f"allowed_claims[{idx}].strength is not bounded: {strength}"))

    valid_guardrails = False
    for field in ("forbidden_claims", "forbidden_wording", "forbidden_terms"):
        if _valid_guardrail_list(payload, field, errors):
            valid_guardrails = True
    if not invalid_strength and not valid_guardrails:
        errors.append(issue("E_FORBIDDEN_WORDING_REQUIRED", "ClaimBoundaryMap requires forbidden wording or forbidden claim guardrails"))


def _validate_reader_spine(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    if not is_non_empty_string_list(payload.get("questions")):
        errors.append(issue("E_READER_QUESTION_REQUIRED", "ReaderSpine.questions must be a non-empty list of strings"))


S00_ROUTE_STATUSES = {"confirmed", "assumed", "owner_gated", "rejected"}
S00_AMBITION_LEVELS = {"conservative", "moderate", "high", "nature_like", "owner_gated"}
S00_ACTIVATION_REASONS = {
    "owner_motivation_unclear",
    "venue_unclear",
    "claim_scope_unclear",
    "private_source_policy_unclear",
    "owner_route_change",
    "submission_boundary_question",
}
S00_REQUIRED_EXTERNAL_ACTION_BLOCKS = {"submission", "public_release"}
S00_REQUIRED_OWNER_APPROVAL_ACTIONS = {
    "submission",
    "venue_route_change",
    "claim_strength_increase",
    "private_source_use",
    "public_release",
}
S00_REQUIRED_STALE_TARGETS = {"S01", "S02", "S03", "S04", "S05", "S13", "S16"}
S01_ACTIVATION_REASONS = {
    "inventory_missing",
    "inventory_stale",
    "new_results_added",
    "new_bibtex_added",
    "figure_source_changed",
    "s04_missing_evidence",
    "s16_data_availability_gap",
}
S01_COMPLETION_BOUNDARY = "inventory_only_no_claim_admissibility_no_graph_completion"
S01_COVERAGE_STATUSES = {"pass", "partial", "fail"}
S01_FORBIDDEN_ADMISSIBILITY_KEYS = {
    "admissibility_decision",
    "admissible_claims",
    "admitted_claims",
    "allowed_claims",
    "allowed_wording",
    "claim_admissibility",
    "claim_support_decision",
    "claim_supported",
    "forbidden_wording",
    "proves_claim",
    "support_strength",
    "supported_claims",
}
S02_COMPLETION_BOUNDARY = "research_profile_only_no_contribution_freeze_no_claim_wording_no_graph_or_manuscript_completion"
S02_PROCESSING_STATUSES = {"processed", "excluded", "unresolved"}
S02_FORBIDDEN_FREEZE_KEYS = {
    "admissibility_decision",
    "allowed_claims",
    "allowed_wording",
    "claim_admissibility",
    "claim_freeze",
    "claim_support_decision",
    "contribution_freeze",
    "copyable_sentence_template",
    "copyable_sentence_templates",
    "final_claim",
    "final_claim_wording",
    "final_prose",
    "graph_complete",
    "manuscript_ready",
    "paragraph_rule",
    "publication_readiness",
    "sentence_rule",
    "submission_readiness",
    "supported_claims",
}
S02_COMPLETION_OVERCLAIM_KEYS = {
    "graph_complete",
    "manuscript_ready",
    "publication_readiness",
    "submission_readiness",
}
S02_LANGUAGE_PROFILE_FIELDS = {
    "citation_pattern_profile",
    "lexical_strength_map",
    "limitation_language_patterns",
    "paragraph_function_taxonomy",
    "quantitative_style_metrics",
    "result_narrative_patterns",
    "syntax_pattern_inventory",
}
S02_REQUIRED_CONTROL_FLAGS = {
    "allow_deviation_when_claim_boundary_requires",
    "exemplar_copying_forbidden",
    "no_sentence_or_paragraph_rule_generation",
    "preserve_claim_boundary_over_metric_matching",
    "statistics_are_descriptive",
}
S02_REQUIRED_HANDOFF_STAGES = {"S03", "S05", "S07"}
S03_COMPLETION_BOUNDARY = "contribution_options_only_no_claim_admissibility_no_final_wording_no_graph_or_manuscript_completion"
S03_OPTION_STATUSES = {"supported", "supportable_after_S04", "weak", "owner_gated", "rejected"}
S03_CLAIM_ADMISSIBILITY_KEYS = {
    "admissibility_decision",
    "admitted_claims",
    "allowed_claims",
    "allowed_wording",
    "claim_admissibility",
    "claim_freeze",
    "final_claim",
    "final_claim_wording",
    "final_prose",
    "forbidden_wording",
    "support_strength",
    "supported_claims",
}
S03_COMPLETION_OVERCLAIM_KEYS = {
    "graph_complete",
    "manuscript_ready",
    "publication_readiness",
    "submission_readiness",
}
S04_COMPLETION_BOUNDARY = "claim_admissibility_only_no_final_prose_no_graph_or_manuscript_completion"
S04_SUPPORT_STRENGTHS = {"strong", "moderate", "weak", "background_only", "unsupported", "forbidden"}
S04_CLAIM_STATUSES = {"admitted", "weakened", "rejected", "backflowed", "owner_gated"}
S04_REQUIRED_HANDOFF_STAGES = {"S05", "S07", "S10", "S12", "S13"}
S04_COMPLETION_OVERCLAIM_KEYS = {
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S04_FINAL_PROSE_KEYS = {
    "body_text",
    "compiled_manuscript",
    "draft_paragraph",
    "final_manuscript",
    "final_prose",
    "manuscript_text",
    "paragraph_text",
    "section_draft",
}
S05_COMPLETION_BOUNDARY = "reader_spine_control_only_no_new_claims_no_final_prose_no_graph_or_manuscript_completion"
S05_CLAIM_PLACEMENT_STATUSES = {"placed", "excluded", "backflowed", "owner_gated"}
S05_QUESTION_STATUSES = {"answered", "deferred", "backflowed", "owner_gated"}
S05_REQUIRED_HANDOFF_STAGES = {"S06", "S07", "S08"}
S05_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "publication_readiness",
    "submission_readiness",
}
S05_FINAL_PROSE_KEYS = {
    "body_text",
    "draft_paragraph",
    "final_prose",
    "manuscript_text",
    "paragraph_text",
    "section_draft",
}
S06_COMPLETION_BOUNDARY = "object_granularity_design_only_no_new_claims_no_final_prose_no_graph_or_manuscript_completion"
S06_OBJECT_PRIORITIES = {"P0", "P1", "P2", "P3", "P4"}
S06_OBJECT_CARD_PRIORITIES = {"P0", "P1", "P2"}
S06_OBJECT_STATUSES = {"represented", "deferred", "downgraded", "unresolved", "backflow_required", "excluded"}
S06_VARIABLE_STATUSES = {"represented", "deferred", "unresolved", "backflow_required"}
S06_GRANULARITY_LEVELS = {
    "mention_only",
    "intuitive_description",
    "operational_definition",
    "formal_definition",
    "algorithmic_detail",
    "empirical_instantiation",
    "limitation_boundary",
}
S06_REQUIRED_HANDOFFS = {"handoff_to_s07", "handoff_to_s08", "handoff_to_s10"}
S06_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S06_FINAL_PROSE_KEYS = {
    "body_text",
    "draft_paragraph",
    "final_prose",
    "manuscript_text",
    "paragraph_text",
    "section_draft",
}
S07_COMPLETION_BOUNDARY = "rhetoric_surface_control_only_no_new_claims_no_final_prose_no_graph_or_manuscript_completion"
S07_RULE_STATUSES = {"ready", "deferred", "unresolved", "backflow_required", "owner_gated"}
S07_TERM_STATUSES = {"ready", "deferred", "unresolved", "backflow_required"}
S07_REQUIRED_HANDOFFS = {"S09A_S09B", "S10", "S12", "S13"}
S07_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S07_FINAL_PROSE_KEYS = {
    "body_text",
    "draft_paragraph",
    "final_prose",
    "manuscript_text",
    "paragraph_text",
    "section_draft",
}
S08_COMPLETION_BOUNDARY = "visual_formal_planning_only_no_final_figures_no_final_captions_no_new_claims_no_graph_or_manuscript_completion"
S08_VISUAL_TYPES = {"algorithm", "figure", "formula", "schematic", "table"}
S08_CANDIDATE_STATUSES = {"keep", "merge", "supplement", "defer", "reject"}
S08_PLACEMENTS = {"main", "supplement", "deferred", "reject"}
S08_EXPLANATORY_EVIDENTIAL_ROLES = {"explanatory", "evidential", "formal", "mixed"}
S08_FORMAL_TYPES = {"algorithm", "definition", "formula", "theorem_like_statement"}
S08_REQUIRED_HANDOFFS = {"S10", "S11", "S12", "S13"}
S08_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S08_FINAL_ARTIFACT_KEYS = {
    "caption_text",
    "compiled_pdf",
    "exported_figure",
    "exported_pdf",
    "figure_export_bundle",
    "final_caption",
    "final_caption_text",
    "final_figure",
    "final_figure_file",
    "rendered_figure",
    "rendered_outputs",
}
S09A_COMPLETION_BOUNDARY = "rich_control_selection_only_no_task_packet_no_final_prose_no_graph_or_manuscript_completion"
S09B_COMPLETION_BOUNDARY = "task_packet_assembly_only_no_candidate_content_no_graph_or_manuscript_completion"
S09_TARGET_STAGES = {"S10", "S11", "S15"}
S09A_TARGET_UNIT_TYPES = {
    "caption",
    "figure_callout",
    "formula_explanation",
    "paragraph",
    "repair_unit",
    "section",
    "subsection",
    "table_note",
}
S09_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S09_FINAL_CONTENT_KEYS = {
    "body_text",
    "candidate_text",
    "caption_text",
    "draft_paragraph",
    "final_caption",
    "final_figure",
    "final_prose",
    "manuscript_text",
    "paragraph_text",
    "rendered_figure",
    "section_draft",
}
S09B_REQUIRED_FORBIDDEN_ROUTES = {
    "alter_unrelated_sections",
    "change_owner_intent",
    "claim_submission_or_publication_readiness",
    "dispatch_subagents",
    "introduce_new_claims",
    "mark_graph_complete",
    "mark_manuscript_complete",
    "strengthen_claims_beyond_s04",
    "write_outside_allowed_write_paths",
}
S09B_BOOT_REQUIRED_TERMS = {
    "allowed_write_paths",
    "candidate/evidence",
    "completion_forbidden",
    "missingmaterialreport",
    "no_recursive_orchestration",
    "s04",
}
S09B_MATERIAL_CLOSURE_FIELDS = {
    "control_digest_policy",
    "global_material_coverage",
    "unit_material_closure",
    "material_access_manifest",
    "material_read_obligations",
    "deferred_control_ledger",
    "section_specific_blockers",
}
S09B_REJECTED_ALIAS_FIELDS = {"must_read_material_closure"}
S10_COMPLETION_BOUNDARY = "candidate_text_only_no_graph_manuscript_submission_or_publication_completion"
S10_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "final_acceptance",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S10_FINAL_ACCEPTANCE_KEYS = {
    "accepted_text",
    "committed_manuscript_text",
    "final_manuscript",
    "final_prose",
    "final_section",
    "publication_ready_text",
}
S10_REQUIRED_FORBIDDEN_SCAN_CATEGORIES = {
    "certainty_overreach",
    "forbidden_claim_wording",
    "internal_id_leakage",
    "lab_notebook_smell",
    "rigid_template_pattern",
    "unsupported_generalization",
    "unsupported_novelty_terms",
}
S10_REQUIRED_VERIFIER_CHECKS = {
    "allowed_write_path_obeyed",
    "candidate_return_complete",
    "completion_not_claimed",
    "every_claim_maps_to_s04_capsule",
    "forbidden_wording_absent",
    "internal_id_leakage_absent",
    "material_hydration_report_checked",
    "material_read_receipts_checked",
    "move_trace_complete",
    "no_claim_strengthening",
    "object_granularity_obeyed",
    "packet_target_unit_obeyed",
    "recursion_not_requested",
    "required_caveats_present",
    "risks_reported_honestly",
    "terminology_controls_obeyed",
    "visual_callouts_obey_s08",
}
S10_REQUIRED_WRITER_PASSES = {
    "boot_authority_boundary",
    "build_unit_skeleton",
    "draft_candidate_text",
    "extract_hard_constraints",
    "extract_object_and_terminology_controls",
    "extract_reader_and_move_plan",
    "extract_visual_formal_controls_if_applicable",
    "generate_traces",
    "hydrate_required_materials",
    "read_and_validate_s09b_packet",
    "record_material_read_receipts",
    "return_candidate_artifact_return",
    "self_check_against_controls",
    "write_candidate_artifact_if_allowed",
}
S11_COMPLETION_BOUNDARY = "visual_artifact_candidate_only_no_graph_manuscript_submission_publication_or_final_export_completion"
S11_VISUAL_TYPES = {"algorithm", "caption_bundle", "figure", "formula", "schematic", "table"}
S11_ARTIFACT_TYPES = {"algorithm", "caption", "export_bundle", "figure", "formula", "schematic", "table"}
S11_ARTIFACT_STATUSES = {"blocked", "candidate", "render_plan_only"}
S11_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "final_export_ready",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S11_REQUIRED_FORBIDDEN_CHANGES = {
    "add_decorative_elements_implying_unsupported_mechanism",
    "change_axis_scale_to_exaggerate_effect",
    "change_proof_role",
    "change_supported_claims",
    "cherry_pick_prettier_examples",
    "copy_exemplar_visual_style_too_closely",
    "hide_negative_or_uncertain_results",
    "remove_required_caveats",
    "remove_required_panels",
    "strengthen_caption_claims",
    "treat_schematic_as_empirical_evidence",
}
S11_REQUIRED_VERIFIER_CHECKS = {
    "accessibility_checked",
    "candidate_return_complete",
    "caption_claim_boundary_preserved",
    "completion_not_claimed",
    "editable_source_or_render_plan_present",
    "exemplar_boundary_and_similarity_checked",
    "image_integrity_record_present",
    "nature_figure_backend_gate_checked",
    "nature_figure_direct_call_mapping_complete",
    "nature_figure_parity_manifest_verified",
    "nature_figure_vendor_verified",
    "no_cross_backend_rendering",
    "no_mock_data_for_evidential_figure",
    "no_recursive_dispatch",
    "panel_claim_trace_complete",
    "polish_preserves_evidence_meaning",
    "proof_role_preserved",
    "source_data_trace_present",
    "supported_claims_preserved",
    "visual_contract_obeyed",
    "write_path_obeyed",
}
S11_NATURE_UPSTREAM_COMMIT = "c91df241a7a963ea151687ac669c5534404f53e5"
S11_NATURE_VENDOR_PATH = "third_party/nature-figure"
S11_NATURE_PARITY_TARGET = "nature-figure@2.0.0"
S11_NATURE_PARITY_MANIFEST = "third_party/nature-figure/PARITY_MANIFEST.json"
S11_NATURE_CALL_STEP = "S11.nature_figure_production_pass"
S11_NATURE_WRITE_PREFIXES = ("examples/candidate-artifacts/", "figures/src/", "figures/generated/")
S11_NATURE_CANDIDATE_PREFIXES = ("examples/candidate-artifacts/",)
S11_NATURE_SOURCE_PREFIXES = ("examples/candidate-artifacts/", "figures/src/")
S11_NATURE_SCRIPT_PREFIXES = ("figures/src/",)
S11_NATURE_RENDER_PREFIXES = ("figures/generated/",)
S11_NATURE_DATA_PREFIXES = ("examples/materials/",)
S11_NATURE_BACKEND_TOOLS = {"python": "python3", "r": "Rscript"}
S11_NATURE_BACKEND_FRAGMENTS = {
    "python": "static/fragments/backend/python.md",
    "r": "static/fragments/backend/r.md",
}
S11_NATURE_REQUIRED_LOADED_COMPONENTS = {
    "SKILL.md",
    "manifest.yaml",
    "static/core/contract.md",
    "static/core/stance.md",
    "references/figure-contract.md",
    "references/qa-contract.md",
    "references/design-theory.md",
}
S11_NATURE_REQUIRED_QA_FLAGS = {
    "source_data_trace_ok",
    "claim_boundary_preserved",
    "proof_role_preserved",
    "s11_mapping_complete",
    "cross_backend_rendering_absent",
    "mock_data_absent_or_non_evidential",
    "exemplar_boundary_preserved",
    "accessibility_contract_present",
    "editable_source_or_render_plan_present",
}
S12_COMPLETION_BOUNDARY = "structured_integrated_candidate_only_no_pdf_export_no_final_manuscript_no_untracked_rewrite"
S12_COMPLETION_OVERCLAIM_KEYS = {
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S12_BACKFLOW_TARGETS = {"S04", "S05", "S06", "S07", "S08", "S09A", "S09B", "S10", "S11", "S14", "S15"}
S13_COMPLETION_BOUNDARY = "adversarial_loss_signal_report_only_no_pdf_review_no_rewrite_no_repair_execution"
S13_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "accepted_manuscript",
    "final_manuscript",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "rewritten_manuscript",
    "submission_readiness",
}
S13_REVIEW_MODES = {
    "reviewer_panel",
    "desk_reject",
    "reader_experience",
    "claim_evidence",
    "method_result",
    "figure_caption",
    "surface_accessibility",
}
S13_REVIEWER_ROLES = {
    "technical_method_reviewer",
    "empirical_evaluation_reviewer",
    "domain_application_reviewer",
    "journal_scope_or_editorial_reviewer",
}
S13_NEAREST_RESPONSIBLE_STAGES = {"S04", "S05", "S06", "S07", "S08", "S09A", "S09B", "S10", "S11", "S12"}
S13_ALLOWED_SEVERITIES = {"low", "medium", "high", "blocker"}
S13_REQUIRED_VERIFIER_CHECKS = {
    "each_finding_has_evidence",
    "each_finding_has_affected_artifact",
    "each_finding_has_affected_location",
    "each_finding_has_severity",
    "each_finding_routes_through_s14",
    "nearest_responsible_stage_plausible",
    "repair_scope_is_local",
    "no_uncontrolled_rewrite_requested",
    "no_completion_claimed",
    "no_pdf_primary_review",
    "duplicate_findings_merged",
    "vague_findings_rejected",
    "findings_ready_for_s14",
}
S14_COMPLETION_BOUNDARY = "backflow_repair_plan_only_no_repair_execution_no_graph_manuscript_export_or_submission_completion"
S14_COMPLETION_OVERCLAIM_KEYS = {
    "export_complete",
    "finding_resolved",
    "findings_resolved",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "repair_complete",
    "submission_readiness",
}
S14_FAILURE_TYPES = {
    "caption_overclaim",
    "export_hygiene",
    "figure_mismatch",
    "missing_bridge",
    "owner_decision_needed",
    "repository_hygiene",
    "stale_packet",
    "terminology_drift",
    "under_evidenced_claim",
    "overclaim",
    "wrong_granularity",
}
S14_ACCEPTANCE_STATUSES = {"accepted", "rejected", "duplicate", "owner_gated", "ambiguous"}
S14_TARGET_STAGES = {"S04", "S05", "S06", "S07", "S08", "S09A", "S09B", "S10", "S11", "S12", "S15", "S16", "owner"}
S14_REPAIR_SCOPES = {
    "control_reselection",
    "export_hygiene_fix",
    "figure_caption_regeneration",
    "local_wording",
    "manuscript_reintegration",
    "owner_decision",
    "section_candidate_regeneration",
    "task_packet_regeneration",
}
S14_EXECUTION_STAGES = {"S09A", "S09B", "S10", "S11", "S12", "S15", "S16", "owner"}
S14_RESPONSE_ACTIONS = {"repair", "rebut", "defer", "owner_decision", "no_action_duplicate"}
S14_PRIORITIES = {"P0", "P1", "P2", "P3"}
S15_COMPLETION_BOUNDARY = "repair_candidate_only_controller_commits_graph_after_validation_no_export_or_submission_completion"
S15_COMPLETION_OVERCLAIM_KEYS = {
    "export_complete",
    "final_manuscript",
    "finding_resolved",
    "graph_complete",
    "manuscript_complete",
    "manuscript_ready",
    "pdf_ready",
    "publication_readiness",
    "submission_readiness",
}
S15_REPAIR_TASK_KINDS = {
    "claim_boundary_repair",
    "control_reselection_repair",
    "export_hygiene_repair",
    "figure_caption_repair",
    "manuscript_integration_repair",
    "packet_regeneration",
    "section_text_repair",
}
S15_DOWNSTREAM_ACTIONS = {"regenerated", "revalidated", "still_stale", "blocked"}
S15_RESOLUTION_STATUSES = {"resolved_candidate", "partially_resolved", "blocked", "owner_gated"}
S15_CLAIM_IMPACTS = {"none", "weakened", "clarified", "owner_gated"}
S15_REQUIRED_VERIFIER_CHECKS = {
    "strict_packet_ack",
    "diff_locality",
    "unrelated_nodes_unchanged",
    "stale_propagation",
    "finding_resolution_evidence",
    "no_new_high_severity",
    "overlay_clause_preserved",
    "candidate_return_schema",
    "no_completion_claim",
}
S16_COMPLETION_BOUNDARY = "export_handoff_package_only_no_external_submission_or_publication_claim"
S16_COMPLETION_OVERCLAIM_KEYS = {
    "acceptance_readiness",
    "accepted_manuscript",
    "camera_ready_claim",
    "camera_ready_package",
    "final_submission_package",
    "graph_complete",
    "manuscript_complete",
    "publication_ready",
    "publication_readiness",
    "submitted_manuscript",
    "submission_ready",
    "submission_readiness",
    "venue_acceptance_claimed",
}
S16_READINESS_STATES = {"pass", "fail", "blocked"}
S16_CLOSURE_STATUSES = {"closed", "not_applicable", "owner_accepted_risk"}
S16_EXPORT_KINDS = {"pdf", "tex", "bib", "figure", "table", "algorithm", "formula", "schematic", "supplement", "report", "log"}
S16_EVIDENCE_MODES = {"fixture_projection", "live_export"}
S16_NARRATIVE_OVERCLAIM_PHRASES = {
    "accepted for publication",
    "camera ready",
    "external submission performed",
    "journal ready",
    "owner approved submission",
    "owner authorized submission",
    "paper has been submitted",
    "publication ready",
    "publication readiness achieved",
    "ready for publication",
    "ready for submission",
    "scientific review passed",
    "scientifically accepted",
    "submission publication ready",
    "submission ready",
    "submission readiness achieved",
    "submitted to journal",
    "venue ready",
}
S16_FEEDBACK_ROUTES = {
    "if_content_feedback": "route_to_S14",
    "if_build_or_export_feedback": "route_to_S16",
    "if_submission_decision": "route_to_owner",
}
S16_RECOMMENDED_NEXT_STEPS = {"read_pdf", "approve_submission_gate", "route_feedback_to_s14", "fix_export_hygiene"}
S16_REQUIRED_VERIFIER_CHECKS = {
    "upstream_closure_checked",
    "readiness_states_separated",
    "delivery_target_declared",
    "target_binding_checked",
    "compiled_pdf_target_gate_checked",
    "semantic_surface_checked",
    "body_citation_anchors_checked",
    "reference_entries_checked",
    "visual_formal_artifacts_checked",
    "internal_lexicon_checked",
    "unresolved_risk_leakage_checked",
    "semantic_failure_attribution_checked",
    "template_only_boundary_checked",
    "build_success_recorded",
    "rendered_surface_checked",
    "manifest_hashes_recorded",
    "repository_hygiene_classified",
    "handoff_complete",
    "feedback_route_declared",
    "no_submission_or_publication_claim",
}
S16_DELIVERY_TARGET_KINDS = {
    "export_hygiene_handoff",
    "template_only_handoff",
    "materials_only",
    "compiled_initial_draft",
    "revised_compiled_pdf",
}
S16_COMPILED_DELIVERY_TARGETS = {"compiled_initial_draft", "revised_compiled_pdf"}
S16_NON_COMPILED_DELIVERY_TARGETS = S16_DELIVERY_TARGET_KINDS - S16_COMPILED_DELIVERY_TARGETS
S16_REQUESTED_TARGET_SOURCES = {
    "owner_intake",
    "manager_active_target",
    "runtime_active_target",
    "repair_backflow",
    "fixture_contract",
}
S16_ACTIVE_TARGET_SOURCES = {"manager_active_target", "runtime_active_target"}
S16_COMPILED_READINESS_KEYS = {"content_ready", "build_ready", "render_clean", "repository_clean", "handoff_ready"}
S16_COMPILED_TARGET_POLICY = {
    "compiled_pdf_claimed": True,
    "requires_content_bearing_pdf": True,
    "requires_source_writeback": True,
    "allows_template_only_handoff": False,
    "allows_candidate_only_completion": False,
    "requires_post_writeback_s12": True,
    "requires_final_s16_content_ready_pass": True,
}
S16_NON_COMPILED_TARGET_POLICY = {
    "compiled_pdf_claimed": False,
}
S16_SOURCE_WRITEBACK_REQUIRED_FIELDS = {
    "latex_writeback_plan_ref",
    "latex_writeback_patchset_ref",
    "latex_writeback_apply_report_ref",
    "source_tree_after_writeback_ref",
    "claim_boundary_audit_ref",
    "template_compatibility_check_ref",
    "status",
}
S16_POST_WRITEBACK_REQUIRED_FIELDS = {
    "s12_post_writeback_ref",
    "build_after_writeback_ref",
    "rendered_surface_review_ref",
    "pdf_text_ref",
    "pdf_text_sha256",
    "output_pdf_ref",
    "output_pdf_sha256",
    "status",
}
S16_COMPILED_SURFACE_BOOL_FIELDS = {
    "template_only_text_absent",
    "manuscript_not_started_absent",
    "placeholder_text_absent",
    "body_paragraphs_present",
    "body_citation_anchors_present",
    "reference_entries_present",
    "actual_bibliography_rendered",
    "paper_facing_figures_captions_present",
    "visual_formal_callouts_present",
    "required_visual_formal_artifacts_present",
    "internal_stage_id_leakage_absent",
    "forbidden_internal_terms_absent",
    "unresolved_manager_risk_leakage_absent",
}
S16_VISUAL_FORMAL_ARTIFACT_TYPES = {"algorithm", "figure", "formula", "schematic", "table"}
S16_VISUAL_FORMAL_EXPORT_KIND_BY_ARTIFACT_TYPE = {
    "algorithm": "algorithm",
    "figure": "figure",
    "formula": "formula",
    "schematic": "schematic",
    "table": "table",
}
S16_SEMANTIC_FAILURE_ATTRIBUTION_ROUTES = {
    "missing_citation_or_reference": {"S01", "S02", "S04", "S09B", "S10", "S12", "S16"},
    "missing_visual_formal_artifact": {"S08", "S11", "S12", "S16"},
    "internal_lexicon_leakage": {"S07", "S09B", "S10", "S12", "S16"},
    "unresolved_manager_risk_leakage": {"S12", "S13", "S14", "S15", "S16"},
}
S16_TEMPLATE_SENTINELS = {
    "manuscript not started",
    "template-only",
    "template only",
    "placeholder",
    "validator_placeholder",
}


def _require_mapping(payload: dict[str, Any], field: str, code: str, errors: list[ValidationIssue]) -> dict[str, Any] | None:
    value = as_mapping(payload.get(field))
    if value is None:
        errors.append(issue(code, f"{field} must be a mapping"))
    return value


def _require_mapping_fields(value: dict[str, Any] | None, field: str, required: list[str], code: str, errors: list[ValidationIssue]) -> None:
    if value is None:
        return
    for key in required:
        if not is_non_empty_string(value.get(key)):
            errors.append(issue(code, f"{field}.{key} must be a non-empty string"))


def _require_string_list(value: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue], *, allow_empty: bool = False) -> None:
    if value is None:
        return
    raw = value.get(key)
    if allow_empty and raw == []:
        return
    if not is_non_empty_string_list(raw):
        errors.append(issue(code, f"{field}.{key} must be a non-empty list of strings"))


def _require_mapping_list(value: dict[str, Any] | None, field: str, key: str, required: list[str], code: str, errors: list[ValidationIssue]) -> None:
    if value is None:
        return
    items = value.get(key)
    if not is_non_empty_mapping_list(items):
        errors.append(issue(code, f"{field}.{key} must be a non-empty list of mappings"))
        return
    assert isinstance(items, list)
    for idx, item in enumerate(items):
        assert isinstance(item, dict)
        for required_key in required:
            if not is_non_empty_string(item.get(required_key)):
                errors.append(issue(code, f"{field}.{key}[{idx}].{required_key} must be a non-empty string"))


def _require_s00_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S00":
        errors.append(issue(code, "payload.stage_id must be 'S00'"))


def _require_s01_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S01":
        errors.append(issue(code, "payload.stage_id must be 'S01'"))


def _require_s02_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S02":
        errors.append(issue(code, "payload.stage_id must be 'S02'"))


def _require_s03_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S03":
        errors.append(issue(code, "payload.stage_id must be 'S03'"))


def _require_s04_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S04":
        errors.append(issue(code, "payload.stage_id must be 'S04'"))


def _require_s05_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S05":
        errors.append(issue(code, "payload.stage_id must be 'S05'"))


def _require_s06_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S06":
        errors.append(issue(code, "payload.stage_id must be 'S06'"))


def _require_s07_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S07":
        errors.append(issue(code, "payload.stage_id must be 'S07'"))


def _require_s08_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S08":
        errors.append(issue(code, "payload.stage_id must be 'S08'"))


def _require_s09a_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S09A":
        errors.append(issue(code, "payload.stage_id must be 'S09A'"))


def _require_s09b_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S09B":
        errors.append(issue(code, "payload.stage_id must be 'S09B'"))


def _require_s10_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S10":
        errors.append(issue(code, "payload.stage_id must be 'S10'"))


def _require_s11_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S11":
        errors.append(issue(code, "payload.stage_id must be 'S11'"))


def _require_s12_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S12":
        errors.append(issue(code, "payload.stage_id must be 'S12'"))


def _require_s13_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S13":
        errors.append(issue(code, "payload.stage_id must be 'S13'"))


def _require_s14_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S14":
        errors.append(issue(code, "payload.stage_id must be 'S14'"))


def _require_s15_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S15":
        errors.append(issue(code, "payload.stage_id must be 'S15'"))


def _require_s16_payload_header(payload: dict[str, Any], expected_schema_version: str, code: str, errors: list[ValidationIssue]) -> None:
    if payload.get("schema_version") != expected_schema_version:
        errors.append(issue(code, f"payload.schema_version must be {expected_schema_version!r}"))
    if payload.get("stage_id") != "S16":
        errors.append(issue(code, "payload.stage_id must be 'S16'"))


def _validate_s00_owner_intake(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s00_payload_header(payload, "ppg-s00-owner-intake/v0.1", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    if payload.get("activation_reason") not in S00_ACTIVATION_REASONS:
        errors.append(issue("E_S00_OWNER_INTAKE_REQUIRED", f"activation_reason must be one of {sorted(S00_ACTIVATION_REASONS)}"))

    human_need = _require_mapping(payload, "human_need", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    _require_mapping_fields(
        human_need,
        "human_need",
        ["original_request", "target_outcome", "intended_reader", "success_criteria"],
        "E_S00_OWNER_INTAKE_REQUIRED",
        errors,
    )

    paper_route = _require_mapping(payload, "paper_route", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    _require_mapping_fields(
        paper_route,
        "paper_route",
        ["target_journal_family", "article_type"],
        "E_S00_OWNER_INTAKE_REQUIRED",
        errors,
    )
    if paper_route is not None:
        if paper_route.get("ambition_level") not in S00_AMBITION_LEVELS:
            errors.append(issue("E_S00_OWNER_INTAKE_REQUIRED", f"paper_route.ambition_level must be one of {sorted(S00_AMBITION_LEVELS)}"))
        if paper_route.get("route_status") not in S00_ROUTE_STATUSES:
            errors.append(issue("E_S00_OWNER_INTAKE_REQUIRED", f"paper_route.route_status must be one of {sorted(S00_ROUTE_STATUSES)}"))

    owner_constraints = _require_mapping(payload, "owner_constraints", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    for key in ("allowed_sources", "private_sources", "forbidden_sources", "external_actions_forbidden"):
        _require_string_list(owner_constraints, "owner_constraints", key, "E_S00_OWNER_INTAKE_REQUIRED", errors)
    if owner_constraints is not None and isinstance(owner_constraints.get("external_actions_forbidden"), list):
        blocked = set(owner_constraints["external_actions_forbidden"])
        missing = sorted(S00_REQUIRED_EXTERNAL_ACTION_BLOCKS - blocked)
        if missing:
            errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", f"owner_constraints.external_actions_forbidden missing {missing}"))

    claim_scope = _require_mapping(payload, "claim_scope_preferences", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    for key in ("desired_claim_families", "forbidden_claim_families", "owner_gated_claim_families"):
        _require_string_list(claim_scope, "claim_scope_preferences", key, "E_S00_OWNER_INTAKE_REQUIRED", errors)

    evidence_summary = _require_mapping(payload, "evidence_summary", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    for key in ("known_result_dirs", "known_limitations", "unresolved_evidence_questions"):
        _require_string_list(evidence_summary, "evidence_summary", key, "E_S00_OWNER_INTAKE_REQUIRED", errors)

    decision_status = _require_mapping(payload, "decision_status", "E_S00_OWNER_INTAKE_REQUIRED", errors)
    for key in ("confirmed_by_owner", "assumed_until_owner_confirms", "unresolved_questions"):
        _require_string_list(decision_status, "decision_status", key, "E_S00_OWNER_INTAKE_REQUIRED", errors)


def _validate_s00_owner_semantic_contract(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s00_payload_header(payload, "ppg-s00-owner-semantic-contract/v0.1", "E_S00_OWNER_CONTRACT_REQUIRED", errors)

    expected_boundary = "owner_semantic_contract_only_no_worker_completion_no_submission_claim"
    if payload.get("completion_boundary") != expected_boundary:
        errors.append(issue("E_S00_OWNER_NO_WORKER_COMPLETION", f"completion_boundary must be {expected_boundary!r}"))

    paper_profile = _require_mapping(payload, "paper_profile", "E_S00_OWNER_CONTRACT_REQUIRED", errors)
    _require_mapping_fields(
        paper_profile,
        "paper_profile",
        ["target_route", "article_type", "ambition_boundary"],
        "E_S00_OWNER_CONTRACT_REQUIRED",
        errors,
    )
    if paper_profile is not None and paper_profile.get("route_status") not in S00_ROUTE_STATUSES:
        errors.append(issue("E_S00_OWNER_CONTRACT_REQUIRED", f"paper_profile.route_status must be one of {sorted(S00_ROUTE_STATUSES)}"))

    motivation = _require_mapping(payload, "motivation_contract", "E_S00_OWNER_CONTRACT_REQUIRED", errors)
    _require_mapping_fields(
        motivation,
        "motivation_contract",
        ["core_problem", "intended_contribution_area", "reader_value"],
        "E_S00_OWNER_CONTRACT_REQUIRED",
        errors,
    )

    owner_decisions = _require_mapping(payload, "owner_decisions", "E_S00_OWNER_DECISION_TRACE_REQUIRED", errors)
    _require_mapping_list(owner_decisions, "owner_decisions", "confirmed_decisions", ["decision_id", "statement", "evidence_or_context"], "E_S00_OWNER_DECISION_TRACE_REQUIRED", errors)
    _require_mapping_list(owner_decisions, "owner_decisions", "owner_gated_assumptions", ["assumption_id", "statement", "allowed_until"], "E_S00_OWNER_DECISION_TRACE_REQUIRED", errors)
    _require_mapping_list(owner_decisions, "owner_decisions", "rejected_routes", ["route", "reason"], "E_S00_OWNER_DECISION_TRACE_REQUIRED", errors)

    claim_scope = _require_mapping(payload, "claim_scope_boundary", "E_S00_OWNER_CLAIM_SCOPE_BOUNDARY", errors)
    for key in ("allowed_claim_families", "forbidden_claim_families", "claims_requiring_owner_confirmation"):
        _require_string_list(claim_scope, "claim_scope_boundary", key, "E_S00_OWNER_CLAIM_SCOPE_BOUNDARY", errors)
    if claim_scope is not None and claim_scope.get("claim_strength_increase_requires_owner") is not True:
        errors.append(issue("E_S00_OWNER_CLAIM_SCOPE_BOUNDARY", "claim_strength_increase_requires_owner must be true"))

    source_policy = _require_mapping(payload, "source_policy", "E_S00_OWNER_SOURCE_POLICY_BOUNDARY", errors)
    _require_mapping_fields(
        source_policy,
        "source_policy",
        ["allowed_private_source_use", "forbidden_private_source_use", "citation_policy_boundary"],
        "E_S00_OWNER_SOURCE_POLICY_BOUNDARY",
        errors,
    )
    _require_string_list(source_policy, "source_policy", "anonymization_or_redaction_required", "E_S00_OWNER_SOURCE_POLICY_BOUNDARY", errors)

    external = _require_mapping(payload, "external_action_boundary", "E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", errors)
    if external is not None:
        if external.get("submission_allowed") is not False:
            errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", "external_action_boundary.submission_allowed must be false"))
        if external.get("public_release_allowed") is not False:
            errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", "external_action_boundary.public_release_allowed must be false"))
        owner_approval = external.get("owner_approval_required_for")
        if not is_non_empty_string_list(owner_approval):
            errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", "external_action_boundary.owner_approval_required_for must be a non-empty list of strings"))
        else:
            assert isinstance(owner_approval, list)
            missing = sorted(S00_REQUIRED_OWNER_APPROVAL_ACTIONS - set(owner_approval))
            if missing:
                errors.append(issue("E_S00_OWNER_EXTERNAL_ACTION_BOUNDARY", f"external_action_boundary.owner_approval_required_for missing {missing}"))

    blocked_routes = payload.get("blocked_routes")
    if not is_non_empty_mapping_list(blocked_routes):
        errors.append(issue("E_S00_OWNER_BLOCKED_ROUTES_REQUIRED", "blocked_routes must be a non-empty list of mappings"))
    else:
        assert isinstance(blocked_routes, list)
        for idx, route in enumerate(blocked_routes):
            assert isinstance(route, dict)
            for key in ("route", "reason", "unblock_condition"):
                if not is_non_empty_string(route.get(key)):
                    errors.append(issue("E_S00_OWNER_BLOCKED_ROUTES_REQUIRED", f"blocked_routes[{idx}].{key} must be a non-empty string"))

    downstream = _require_mapping(payload, "downstream_effects_if_changed", "E_S00_OWNER_STALE_TARGETS_REQUIRED", errors)
    _require_string_list(downstream, "downstream_effects_if_changed", "stages_to_mark_stale", "E_S00_OWNER_STALE_TARGETS_REQUIRED", errors)
    _require_mapping_fields(downstream, "downstream_effects_if_changed", ["rationale"], "E_S00_OWNER_STALE_TARGETS_REQUIRED", errors)
    if downstream is not None and isinstance(downstream.get("stages_to_mark_stale"), list):
        missing = sorted(S00_REQUIRED_STALE_TARGETS - set(downstream["stages_to_mark_stale"]))
        if missing:
            errors.append(issue("E_S00_OWNER_STALE_TARGETS_REQUIRED", f"downstream_effects_if_changed.stages_to_mark_stale missing {missing}"))

    questions = payload.get("unresolved_owner_questions")
    if not is_non_empty_mapping_list(questions):
        errors.append(issue("E_S00_OWNER_UNRESOLVED_REQUIRED", "unresolved_owner_questions must be a non-empty list of mappings"))
    else:
        assert isinstance(questions, list)
        for idx, question in enumerate(questions):
            assert isinstance(question, dict)
            for key in ("question", "consequence_if_unanswered"):
                if not is_non_empty_string(question.get(key)):
                    errors.append(issue("E_S00_OWNER_UNRESOLVED_REQUIRED", f"unresolved_owner_questions[{idx}].{key} must be a non-empty string"))


def _require_list_field(value: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue], *, allow_empty: bool = True) -> None:
    if value is None:
        return
    raw = value.get(key)
    if allow_empty and isinstance(raw, list):
        return
    if not is_non_empty_string_list(raw):
        errors.append(issue(code, f"{field}.{key} must be a list of strings"))


def _require_bool_true(value: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue]) -> None:
    if value is None:
        return
    if value.get(key) is not True:
        errors.append(issue(code, f"{field}.{key} must be true"))


def _contains_forbidden_key(value: Any, forbidden: set[str]) -> str | None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in forbidden:
                return key
            found = _contains_forbidden_key(nested, forbidden)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _contains_forbidden_key(nested, forbidden)
            if found is not None:
                return found
    return None


def _record_promoted_as_citable(record: Any) -> bool:
    return isinstance(record, dict) and (
        record.get("citable") is True
        or record.get("promoted_as_citable") is True
        or record.get("citation_role") == "evidence_support"
    )


def _validate_s01_inventory_input(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s01_payload_header(payload, "ppg-s01-inventory-input/v0.1", "E_S01_INVENTORY_INPUT_REQUIRED", errors)
    if payload.get("activation_reason") not in S01_ACTIVATION_REASONS:
        errors.append(issue("E_S01_INVENTORY_INPUT_REQUIRED", f"activation_reason must be one of {sorted(S01_ACTIVATION_REASONS)}"))

    roots = payload.get("repository_roots")
    if not is_non_empty_mapping_list(roots):
        errors.append(issue("E_S01_INVENTORY_INPUT_REQUIRED", "repository_roots must be a non-empty list of mappings"))
    else:
        assert isinstance(roots, list)
        for idx, root in enumerate(roots):
            assert isinstance(root, dict)
            for key in ("path", "role"):
                if not is_non_empty_string(root.get(key)):
                    errors.append(issue("E_S01_INVENTORY_INPUT_REQUIRED", f"repository_roots[{idx}].{key} must be a non-empty string"))

    manuscript = _require_mapping(payload, "manuscript_sources", "E_S01_INVENTORY_INPUT_REQUIRED", errors)
    for key in ("tex_files", "markdown_files", "existing_pdf"):
        _require_list_field(manuscript, "manuscript_sources", key, "E_S01_INVENTORY_INPUT_REQUIRED", errors)

    bibliography = _require_mapping(payload, "bibliography_sources", "E_S01_INVENTORY_INPUT_REQUIRED", errors)
    for key in ("bib_files", "citation_keys", "pdf_library_paths"):
        _require_list_field(bibliography, "bibliography_sources", key, "E_S01_INVENTORY_INPUT_REQUIRED", errors)

    evidence = _require_mapping(payload, "evidence_sources", "E_S01_INVENTORY_INPUT_REQUIRED", errors)
    for key in ("result_dirs", "csv_files", "logs", "notebooks", "scripts"):
        _require_list_field(evidence, "evidence_sources", key, "E_S01_INVENTORY_INPUT_REQUIRED", errors)

    figures = _require_mapping(payload, "figure_sources", "E_S01_INVENTORY_INPUT_REQUIRED", errors)
    for key in ("figure_files", "source_data_files", "generation_scripts", "editable_sources"):
        _require_list_field(figures, "figure_sources", key, "E_S01_INVENTORY_INPUT_REQUIRED", errors)

    supplements = _require_mapping(payload, "supplement_sources", "E_S01_INVENTORY_INPUT_REQUIRED", errors)
    for key in ("supplement_paths", "data_availability_materials"):
        _require_list_field(supplements, "supplement_sources", key, "E_S01_INVENTORY_INPUT_REQUIRED", errors)

    source_policy = _require_mapping(payload, "source_policy_from_s00", "E_S01_PRIVACY_BOUNDARY", errors)
    _require_string_list(source_policy, "source_policy_from_s00", "allowed_private_sources", "E_S01_PRIVACY_BOUNDARY", errors)
    _require_string_list(source_policy, "source_policy_from_s00", "forbidden_private_sources", "E_S01_PRIVACY_BOUNDARY", errors)
    _require_mapping_fields(source_policy, "source_policy_from_s00", ["citation_boundary"], "E_S01_PRIVACY_BOUNDARY", errors)

    freshness = _require_mapping(payload, "freshness_policy", "E_S01_SOURCE_INVENTORY_REQUIRED", errors)
    for key in ("hash_required", "mtime_required", "stale_detection_required"):
        _require_bool_true(freshness, "freshness_policy", key, "E_S01_SOURCE_INVENTORY_REQUIRED", errors)

    read_only = _require_mapping(payload, "read_only_boundary", "E_S01_READ_ONLY_BOUNDARY", errors)
    _require_bool_true(read_only, "read_only_boundary", "source_write_forbidden", "E_S01_READ_ONLY_BOUNDARY", errors)
    _require_bool_true(read_only, "read_only_boundary", "inventory_candidate_only", "E_S01_READ_ONLY_BOUNDARY", errors)


def _validate_mapping_records(
    payload: dict[str, Any],
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> None:
    container = _require_mapping(payload, field, code, errors)
    if container is None:
        return
    records = container.get(key)
    if allow_empty and records == []:
        return
    if not is_non_empty_mapping_list(records):
        errors.append(issue(code, f"{field}.{key} must be a non-empty list of mappings"))
        return
    assert isinstance(records, list)
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        for required_key in required:
            if not is_non_empty_string(record.get(required_key)):
                errors.append(issue(code, f"{field}.{key}[{idx}].{required_key} must be a non-empty string"))


def _validate_s01_source_evidence_inventory(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s01_payload_header(payload, "ppg-s01-source-evidence-inventory/v0.1", "E_S01_SOURCE_INVENTORY_REQUIRED", errors)
    if payload.get("completion_boundary") != S01_COMPLETION_BOUNDARY:
        errors.append(issue("E_S01_COMPLETION_BOUNDARY", f"completion_boundary must be {S01_COMPLETION_BOUNDARY!r}"))

    forbidden_key = _contains_forbidden_key(payload, S01_FORBIDDEN_ADMISSIBILITY_KEYS)
    if forbidden_key is not None:
        errors.append(issue("E_S01_NO_CLAIM_ADMISSIBILITY", f"S01 inventory must not contain claim-admissibility field {forbidden_key!r}"))

    _validate_mapping_records(payload, "source_map", "repo_files", ["path", "role", "hash", "mtime"], "E_S01_LOCATOR_REQUIRED", errors)
    _validate_mapping_records(payload, "citation_bank", "bib_entries", ["citation_key", "metadata_status", "source_pdf_status", "citation_role", "locator"], "E_S01_LOCATOR_REQUIRED", errors)
    _validate_mapping_records(payload, "evidence_bank", "result_artifacts", ["artifact_id", "path", "artifact_type", "freshness_status", "support_hint"], "E_S01_LOCATOR_REQUIRED", errors)

    figures = payload.get("figure_source_data_inventory")
    if not is_non_empty_mapping_list(figures):
        errors.append(issue("E_S01_LOCATOR_REQUIRED", "figure_source_data_inventory must be a non-empty list of mappings"))
    else:
        assert isinstance(figures, list)
        for idx, figure in enumerate(figures):
            assert isinstance(figure, dict)
            for key in ("figure_id", "figure_file", "provenance_status"):
                if not is_non_empty_string(figure.get(key)):
                    errors.append(issue("E_S01_LOCATOR_REQUIRED", f"figure_source_data_inventory[{idx}].{key} must be a non-empty string"))

    _validate_mapping_records(payload, "data_availability_inventory", "datasets", ["dataset_id", "path_or_access", "availability_status", "access_boundary"], "E_S01_LOCATOR_REQUIRED", errors)

    supplement = _require_mapping(payload, "supplement_inventory", "E_S01_LOCATOR_REQUIRED", errors)
    for key in ("supplement_files", "missing_supplements"):
        _require_list_field(supplement, "supplement_inventory", key, "E_S01_LOCATOR_REQUIRED", errors)

    privacy = _require_mapping(payload, "privacy_boundary_report", "E_S01_PRIVACY_BOUNDARY", errors)
    for key in ("private_sources", "forbidden_sources", "anonymization_needed"):
        raw = None if privacy is None else privacy.get(key)
        if raw is None or not isinstance(raw, list):
            errors.append(issue("E_S01_PRIVACY_BOUNDARY", f"privacy_boundary_report.{key} must be a list"))
        elif key in {"private_sources", "forbidden_sources"} and any(_record_promoted_as_citable(record) for record in raw):
            errors.append(issue("E_S01_PRIVACY_BOUNDARY", f"privacy_boundary_report.{key} must not promote private/forbidden sources as citable evidence"))

    unresolved = _require_mapping(payload, "unresolved_locator_register", "E_S01_LOCATOR_REQUIRED", errors)
    for key in ("missing_files", "ambiguous_sources", "stale_paths", "citation_without_pdf_or_metadata", "evidence_needed_by_claim_but_missing"):
        _require_list_field(unresolved, "unresolved_locator_register", key, "E_S01_LOCATOR_REQUIRED", errors)

    freshness = _require_mapping(payload, "freshness_report", "E_S01_SOURCE_INVENTORY_REQUIRED", errors)
    for key in ("hashed_paths", "stale_materials", "unknown_freshness"):
        raw = None if freshness is None else freshness.get(key)
        if raw is None or not isinstance(raw, list):
            errors.append(issue("E_S01_SOURCE_INVENTORY_REQUIRED", f"freshness_report.{key} must be a list"))

    coverage = _require_mapping(payload, "coverage_ledger", "E_S01_COVERAGE_LEDGER_REQUIRED", errors)
    _require_string_list(coverage, "coverage_ledger", "input_roots_scanned", "E_S01_COVERAGE_LEDGER_REQUIRED", errors)
    if coverage is not None:
        if not isinstance(coverage.get("roots_not_scanned_with_reason"), list):
            errors.append(issue("E_S01_COVERAGE_LEDGER_REQUIRED", "coverage_ledger.roots_not_scanned_with_reason must be a list"))
        for key in ("bibliography_coverage", "evidence_locator_coverage", "figure_source_data_coverage", "supplement_coverage", "privacy_policy_coverage"):
            if coverage.get(key) not in S01_COVERAGE_STATUSES:
                errors.append(issue("E_S01_COVERAGE_LEDGER_REQUIRED", f"coverage_ledger.{key} must be one of {sorted(S01_COVERAGE_STATUSES)}"))

    candidate = _require_mapping(payload, "candidate_return", "E_S01_SOURCE_INVENTORY_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S01_SOURCE_INVENTORY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S01_SOURCE_INVENTORY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S01_SOURCE_INVENTORY_REQUIRED", errors, allow_empty=True)


def _has_non_empty_payload_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def _require_s02_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "research_scene_profile",
        "sota_comparator_map",
        "template_exemplar_profile",
        "template_language_profile",
        "descriptive_not_prescriptive_controls",
        "source_coverage_ledger",
        "exemplar_sample_register",
        "language_profile_sample_limits",
        "sota_family_coverage_ledger",
        "unresolved_source_report",
        "downstream_handoff_coverage",
        "misuse_guard",
        "citation_verification_report",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S02_RESEARCH_DOSSIER_REQUIRED", f"S02ResearchDossier missing required modules: {missing}"))


def _require_top_level_mapping_list(payload: dict[str, Any], field: str, key: str, required: list[str], code: str, errors: list[ValidationIssue]) -> None:
    container = _require_mapping(payload, field, code, errors)
    if container is None:
        return
    records = container.get(key)
    if not is_non_empty_mapping_list(records):
        errors.append(issue(code, f"{field}.{key} must be a non-empty list of mappings"))
        return
    assert isinstance(records, list)
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        for required_key in required:
            if not is_non_empty_string(record.get(required_key)):
                errors.append(issue(code, f"{field}.{key}[{idx}].{required_key} must be a non-empty string"))
        status = record.get("processing_status")
        if "processing_status" in required and status not in S02_PROCESSING_STATUSES:
            errors.append(issue(code, f"{field}.{key}[{idx}].processing_status must be one of {sorted(S02_PROCESSING_STATUSES)}"))


def _validate_s02_template_language_profile(profile: dict[str, Any] | None, errors: list[ValidationIssue]) -> None:
    if profile is None:
        return
    missing = sorted(field for field in S02_LANGUAGE_PROFILE_FIELDS if not _has_non_empty_payload_value(profile.get(field)))
    if missing:
        errors.append(issue("E_S02_TEMPLATE_LANGUAGE_PROFILE_REQUIRED", f"template_language_profile missing {missing}"))
    metrics = as_mapping(profile.get("quantitative_style_metrics"))
    if metrics is None:
        return
    summaries = metrics.get("metric_distribution_summaries")
    if not is_non_empty_mapping_list(summaries):
        errors.append(issue("E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", "quantitative_style_metrics.metric_distribution_summaries must describe ranges/quantiles/sample limits"))
        return
    assert isinstance(summaries, list)
    for idx, summary in enumerate(summaries):
        assert isinstance(summary, dict)
        for key in ("metric_id", "range", "quantiles", "sample_size", "confidence"):
            if not _has_non_empty_payload_value(summary.get(key)):
                errors.append(issue("E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", f"metric_distribution_summaries[{idx}].{key} is required"))


def _validate_s02_descriptive_controls(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    controls = _require_mapping(payload, "descriptive_not_prescriptive_controls", "E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", errors)
    if controls is not None:
        for key in sorted(S02_REQUIRED_CONTROL_FLAGS):
            if controls.get(key) is not True:
                errors.append(issue("E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", f"descriptive_not_prescriptive_controls.{key} must be true"))
        forbidden = controls.get("forbidden_interpretations")
        if not is_non_empty_string_list(forbidden):
            errors.append(issue("E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", "descriptive_not_prescriptive_controls.forbidden_interpretations must be a non-empty list of strings"))
    guard = _require_mapping(payload, "misuse_guard", "E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", errors)
    _require_string_list(guard, "misuse_guard", "downstream_warnings", "E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", errors)
    _require_string_list(guard, "misuse_guard", "flexibility_rules", "E_S02_DESCRIPTIVE_NOT_PRESCRIPTIVE", errors)


def _validate_s02_coverage_ledgers(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_top_level_mapping_list(payload, "source_coverage_ledger", "source_clusters", ["cluster_id", "source_locator", "processing_status"], "E_S02_COVERAGE_LEDGER_REQUIRED", errors)
    _require_top_level_mapping_list(payload, "sota_family_coverage_ledger", "families", ["family_id", "coverage_status", "processing_status"], "E_S02_COVERAGE_LEDGER_REQUIRED", errors)
    _require_top_level_mapping_list(payload, "exemplar_sample_register", "exemplars", ["exemplar_id", "locator", "selection_reason", "processing_status"], "E_S02_COVERAGE_LEDGER_REQUIRED", errors)
    _require_top_level_mapping_list(payload, "language_profile_sample_limits", "samples", ["sample_id", "locator", "included_scope", "processing_status"], "E_S02_COVERAGE_LEDGER_REQUIRED", errors)


def _validate_s02_unresolved_and_handoff(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    unresolved = _require_mapping(payload, "unresolved_source_report", "E_S02_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_source_report", "unresolved_sources", "E_S02_UNRESOLVED_BACKFLOW_REQUIRED", errors, allow_empty=True)
    _require_string_list(unresolved, "unresolved_source_report", "backflow_targets", "E_S02_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    if unresolved is not None and isinstance(unresolved.get("backflow_targets"), list):
        targets = set(unresolved["backflow_targets"])
        if not {"S01", "S00"} & targets:
            errors.append(issue("E_S02_UNRESOLVED_BACKFLOW_REQUIRED", "unresolved_source_report.backflow_targets must include S01 or S00"))

    handoffs = _require_mapping(payload, "downstream_handoff_coverage", "E_S02_DOWNSTREAM_HANDOFF_REQUIRED", errors)
    if handoffs is not None:
        missing = sorted(stage for stage in S02_REQUIRED_HANDOFF_STAGES if not isinstance(handoffs.get(stage), dict))
        if missing:
            errors.append(issue("E_S02_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoff_coverage missing stage handoffs: {missing}"))
        for stage in sorted(S02_REQUIRED_HANDOFF_STAGES):
            handoff = as_mapping(handoffs.get(stage))
            if handoff is None:
                continue
            for key in ("handoff_summary", "allowed_use", "misuse_warning"):
                if not is_non_empty_string(handoff.get(key)):
                    errors.append(issue("E_S02_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoff_coverage.{stage}.{key} must be a non-empty string"))


def _validate_s02_research_dossier(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s02_payload_header(payload, "ppg-s02-research-dossier/v0.1", "E_S02_RESEARCH_DOSSIER_REQUIRED", errors)
    _require_s02_required_modules(payload, errors)
    if payload.get("completion_boundary") != S02_COMPLETION_BOUNDARY:
        errors.append(issue("E_S02_COMPLETION_BOUNDARY", f"completion_boundary must be {S02_COMPLETION_BOUNDARY!r}"))

    completion_overclaim_key = _contains_forbidden_key(payload, S02_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S02_NO_COMPLETION_OVERCLAIM", f"S02 dossier must not contain completion field {completion_overclaim_key!r}"))
    forbidden_key = _contains_forbidden_key(payload, S02_FORBIDDEN_FREEZE_KEYS)
    if forbidden_key is not None:
        errors.append(issue("E_S02_NO_CONTRIBUTION_OR_CLAIM_FREEZE", f"S02 dossier must not contain claim/final-prose/completion field {forbidden_key!r}"))

    scene = _require_mapping(payload, "research_scene_profile", "E_S02_SOURCE_LOCATOR_REQUIRED", errors)
    _require_mapping_fields(scene, "research_scene_profile", ["scene_summary", "source_locator"], "E_S02_SOURCE_LOCATOR_REQUIRED", errors)
    _require_string_list(scene, "research_scene_profile", "citation_anchors", "E_S02_SOURCE_LOCATOR_REQUIRED", errors)

    comparator = _require_mapping(payload, "sota_comparator_map", "E_S02_SOURCE_LOCATOR_REQUIRED", errors)
    _require_mapping_list(comparator, "sota_comparator_map", "comparator_families", ["family_id", "basis", "source_locator"], "E_S02_SOURCE_LOCATOR_REQUIRED", errors)

    exemplar = _require_mapping(payload, "template_exemplar_profile", "E_S02_TEMPLATE_COPYING_BOUNDARY", errors)
    _require_mapping_fields(exemplar, "template_exemplar_profile", ["exemplar_use_boundary"], "E_S02_TEMPLATE_COPYING_BOUNDARY", errors)
    if exemplar is not None:
        if exemplar.get("no_exemplar_copying") is not True:
            errors.append(issue("E_S02_TEMPLATE_COPYING_BOUNDARY", "template_exemplar_profile.no_exemplar_copying must be true"))
        if "copyable_sentence_templates" in exemplar:
            errors.append(issue("E_S02_TEMPLATE_COPYING_BOUNDARY", "template_exemplar_profile must not expose copyable sentence templates"))

    language_profile = _require_mapping(payload, "template_language_profile", "E_S02_TEMPLATE_LANGUAGE_PROFILE_REQUIRED", errors)
    _validate_s02_template_language_profile(language_profile, errors)
    _validate_s02_descriptive_controls(payload, errors)
    _validate_s02_coverage_ledgers(payload, errors)
    _validate_s02_unresolved_and_handoff(payload, errors)

    citation_report = _require_mapping(payload, "citation_verification_report", "E_S02_SOURCE_LOCATOR_REQUIRED", errors)
    _require_mapping_fields(citation_report, "citation_verification_report", ["verification_scope", "source_locator_status"], "E_S02_SOURCE_LOCATOR_REQUIRED", errors)

    candidate = _require_mapping(payload, "candidate_return", "E_S02_RESEARCH_DOSSIER_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S02_RESEARCH_DOSSIER_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S02_RESEARCH_DOSSIER_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S02_RESEARCH_DOSSIER_REQUIRED", errors, allow_empty=True)


def _require_s03_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "contribution_option_queue",
        "contribution_type_taxonomy",
        "sota_contrast_matrix",
        "evidence_readiness_score",
        "unsupported_claim_register",
        "rejected_option_register",
        "owner_gated_option_register",
        "owner_gated_semantic_shift_log",
        "reviewer_attack_map",
        "contribution_coherence",
        "option_coverage_ledger",
        "sota_contrast_coverage",
        "s04_handoff",
        "s04_handoff_coverage",
        "anti_rhetoric_guard",
        "unresolved_backflow_register",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S03_CONTRIBUTION_OPTIONS_REQUIRED", f"S03ContributionOptions missing required modules: {missing}"))


def _require_s03_mapping_list(
    payload: dict[str, Any],
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    container = _require_mapping(payload, field, code, errors)
    if container is None:
        return []
    records = container.get(key)
    if allow_empty and records == []:
        return []
    if not is_non_empty_mapping_list(records):
        errors.append(issue(code, f"{field}.{key} must be a non-empty list of mappings"))
        return []
    assert isinstance(records, list)
    result: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        result.append(record)
        for required_key in required:
            if not is_non_empty_string(record.get(required_key)):
                errors.append(issue(code, f"{field}.{key}[{idx}].{required_key} must be a non-empty string"))
    return result


def _source_option_ids(records: list[dict[str, Any]], field: str = "source_option_id") -> set[str]:
    return {str(record.get(field)) for record in records if is_non_empty_string(record.get(field))}


def _validate_s03_option_queue(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    options = _require_s03_mapping_list(
        payload,
        "contribution_option_queue",
        "options",
        ["option_id", "contribution_type", "proposed_framing", "novelty_basis", "evidence_readiness", "status"],
        "E_S03_OPTION_CLASSIFICATION_REQUIRED",
        errors,
    )
    for idx, option in enumerate(options):
        status = option.get("status")
        if status not in S03_OPTION_STATUSES:
            errors.append(issue("E_S03_STATUS_INVALID", f"contribution_option_queue.options[{idx}].status must be one of {sorted(S03_OPTION_STATUSES)}"))
    return options


def _validate_s03_option_coverage(payload: dict[str, Any], options: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    option_ids = {str(option.get("option_id")) for option in options if is_non_empty_string(option.get("option_id"))}
    coverage = _require_s03_mapping_list(
        payload,
        "option_coverage_ledger",
        "options",
        ["option_id", "classification_status", "processing_status"],
        "E_S03_COVERAGE_LEDGER_REQUIRED",
        errors,
    )
    coverage_ids = {str(record.get("option_id")) for record in coverage if is_non_empty_string(record.get("option_id"))}
    missing = sorted(option_ids - coverage_ids)
    if missing:
        errors.append(issue("E_S03_COVERAGE_LEDGER_REQUIRED", f"option_coverage_ledger missing options {missing}"))
    for idx, record in enumerate(coverage):
        status = record.get("processing_status")
        if status not in S02_PROCESSING_STATUSES:
            errors.append(issue("E_S03_COVERAGE_LEDGER_REQUIRED", f"option_coverage_ledger.options[{idx}].processing_status must be one of {sorted(S02_PROCESSING_STATUSES)}"))


def _validate_s03_registers(payload: dict[str, Any], options: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    by_status = {status: {str(option.get("option_id")) for option in options if option.get("status") == status and is_non_empty_string(option.get("option_id"))} for status in S03_OPTION_STATUSES}
    rejected = _require_s03_mapping_list(
        payload,
        "rejected_option_register",
        "rejected_options",
        ["source_option_id", "rejection_reason", "violated_boundary", "reopening_condition"],
        "E_S03_REJECTED_OPTION_REGISTER_REQUIRED",
        errors,
        allow_empty=True,
    )
    missing_rejected = sorted(by_status["rejected"] - _source_option_ids(rejected))
    if missing_rejected:
        errors.append(issue("E_S03_REJECTED_OPTION_REGISTER_REQUIRED", f"rejected_option_register missing rejected options {missing_rejected}"))

    owner_gated = _require_s03_mapping_list(
        payload,
        "owner_gated_option_register",
        "options",
        ["source_option_id", "owner_decision_required", "risk", "blocked_downstream"],
        "E_S03_OWNER_GATED_REGISTER_REQUIRED",
        errors,
        allow_empty=True,
    )
    missing_owner_gated = sorted(by_status["owner_gated"] - _source_option_ids(owner_gated))
    if missing_owner_gated:
        errors.append(issue("E_S03_OWNER_GATED_REGISTER_REQUIRED", f"owner_gated_option_register missing owner-gated options {missing_owner_gated}"))

    shifts = _require_s03_mapping_list(
        payload,
        "owner_gated_semantic_shift_log",
        "shifts",
        ["source_option_id", "from_scope", "to_scope", "owner_decision_required"],
        "E_S03_OWNER_GATED_REGISTER_REQUIRED",
        errors,
        allow_empty=True,
    )
    missing_shifts = sorted(by_status["owner_gated"] - _source_option_ids(shifts))
    if missing_shifts:
        errors.append(issue("E_S03_OWNER_GATED_REGISTER_REQUIRED", f"owner_gated_semantic_shift_log missing owner-gated options {missing_shifts}"))

    unsupported = _require_s03_mapping_list(
        payload,
        "unsupported_claim_register",
        "unsupported_options",
        ["source_option_id", "claim_or_framing", "missing_evidence", "backflow_target"],
        "E_S03_REJECTED_OPTION_REGISTER_REQUIRED",
        errors,
        allow_empty=True,
    )
    missing_weak = sorted(by_status["weak"] - _source_option_ids(unsupported))
    if missing_weak:
        errors.append(issue("E_S03_REJECTED_OPTION_REGISTER_REQUIRED", f"unsupported_claim_register missing weak options {missing_weak}"))


def _validate_s03_sota_and_evidence(payload: dict[str, Any], options: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    option_ids = {str(option.get("option_id")) for option in options if is_non_empty_string(option.get("option_id"))}
    contrasts = _require_s03_mapping_list(
        payload,
        "sota_contrast_matrix",
        "contrasts",
        ["source_option_id", "nearest_sota_family", "difference_type", "actual_difference", "cannot_claim"],
        "E_S03_SOTA_CONTRAST_REQUIRED",
        errors,
    )
    contrast_ids = _source_option_ids(contrasts)
    missing_contrasts = sorted(option_ids - contrast_ids)
    if missing_contrasts:
        errors.append(issue("E_S03_SOTA_CONTRAST_REQUIRED", f"sota_contrast_matrix missing options {missing_contrasts}"))
    _require_s03_mapping_list(
        payload,
        "sota_contrast_coverage",
        "families",
        ["family_id", "covered_options", "coverage_status"],
        "E_S03_SOTA_CONTRAST_REQUIRED",
        errors,
    )
    readiness = _require_s03_mapping_list(
        payload,
        "evidence_readiness_score",
        "scores",
        ["source_option_id", "readiness_status", "evidence_refs", "s04_dependency", "confidence"],
        "E_S03_EVIDENCE_READINESS_REQUIRED",
        errors,
    )
    readiness_ids = _source_option_ids(readiness)
    missing_readiness = sorted(option_ids - readiness_ids)
    if missing_readiness:
        errors.append(issue("E_S03_EVIDENCE_READINESS_REQUIRED", f"evidence_readiness_score missing options {missing_readiness}"))


def _validate_s03_s04_handoff(payload: dict[str, Any], options: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    handoff = _require_s03_mapping_list(
        payload,
        "s04_handoff",
        "claim_candidates",
        ["source_option_id", "claim_candidate", "evidence_readiness_hint", "required_evidence_refs", "allowed_scope_hint", "forbidden_scope_hint", "unresolved_support"],
        "E_S03_S04_HANDOFF_REQUIRED",
        errors,
        allow_empty=True,
    )
    handoff_ids = _source_option_ids(handoff)
    required_handoff = {
        str(option.get("option_id"))
        for option in options
        if option.get("status") in {"supported", "supportable_after_S04"} and is_non_empty_string(option.get("option_id"))
    }
    missing = sorted(required_handoff - handoff_ids)
    if missing:
        errors.append(issue("E_S03_S04_HANDOFF_REQUIRED", f"s04_handoff missing supported/supportable options {missing}"))
    coverage = _require_mapping(payload, "s04_handoff_coverage", "E_S03_S04_HANDOFF_REQUIRED", errors)
    _require_string_list(coverage, "s04_handoff_coverage", "handed_to_s04", "E_S03_S04_HANDOFF_REQUIRED", errors, allow_empty=True)
    _require_string_list(coverage, "s04_handoff_coverage", "excluded_from_s04", "E_S03_S04_HANDOFF_REQUIRED", errors, allow_empty=True)
    _require_string_list(coverage, "s04_handoff_coverage", "handoff_gaps", "E_S03_S04_HANDOFF_REQUIRED", errors, allow_empty=True)


def _validate_s03_contribution_options(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s03_payload_header(payload, "ppg-s03-contribution-options/v0.1", "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    _require_s03_required_modules(payload, errors)
    if payload.get("completion_boundary") != S03_COMPLETION_BOUNDARY:
        errors.append(issue("E_S03_COMPLETION_BOUNDARY", f"completion_boundary must be {S03_COMPLETION_BOUNDARY!r}"))

    completion_overclaim_key = _contains_forbidden_key(payload, S03_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S03_NO_COMPLETION_OVERCLAIM", f"S03 options must not contain completion field {completion_overclaim_key!r}"))
    admissibility_key = _contains_forbidden_key(payload, S03_CLAIM_ADMISSIBILITY_KEYS)
    if admissibility_key is not None:
        errors.append(issue("E_S03_NO_CLAIM_ADMISSIBILITY", f"S03 options must not contain claim-admissibility/final-wording field {admissibility_key!r}"))

    options = _validate_s03_option_queue(payload, errors)
    _validate_s03_option_coverage(payload, options, errors)
    _validate_s03_sota_and_evidence(payload, options, errors)
    _validate_s03_registers(payload, options, errors)
    _validate_s03_s04_handoff(payload, options, errors)
    _require_mapping_list(_require_mapping(payload, "contribution_type_taxonomy", "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors), "contribution_type_taxonomy", "types", ["type_id", "definition"], "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    _require_s03_mapping_list(payload, "reviewer_attack_map", "attacks", ["source_option_id", "likely_attack", "severity", "missing_support", "backflow_target"], "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    coherence = _require_mapping(payload, "contribution_coherence", "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    _require_mapping_fields(coherence, "contribution_coherence", ["primary_option_id", "recommended_bundle", "fragmentation_risk"], "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    guard = _require_mapping(payload, "anti_rhetoric_guard", "E_S03_ANTI_RHETORIC_GUARD", errors)
    _require_string_list(guard, "anti_rhetoric_guard", "banned_novelty_moves", "E_S03_ANTI_RHETORIC_GUARD", errors)
    _require_string_list(guard, "anti_rhetoric_guard", "required_checks", "E_S03_ANTI_RHETORIC_GUARD", errors)
    unresolved = _require_mapping(payload, "unresolved_backflow_register", "E_S03_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_string_list(unresolved, "unresolved_backflow_register", "backflow_targets", "E_S03_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_backflow_register", "unresolved_items", "E_S03_UNRESOLVED_BACKFLOW_REQUIRED", errors, allow_empty=True)
    candidate = _require_mapping(payload, "candidate_return", "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S03_CONTRIBUTION_OPTIONS_REQUIRED", errors, allow_empty=True)


def _require_s04_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "claim_queue",
        "claim_unit_decomposition",
        "atomic_claim_register",
        "claim_capsules",
        "support_strength_map",
        "evidence_anchor_map",
        "allowed_wording_map",
        "forbidden_wording_map",
        "result_package_boundary_matrix",
        "claim_transformation_log",
        "data_availability_plan",
        "downstream_handoffs",
        "claim_coverage_ledger",
        "unsupported_claim_backflow_register",
        "evidence_locator_coverage",
        "downstream_use_permission_matrix",
        "unresolved_backflow_register",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S04_CLAIM_ADMISSIBILITY_REQUIRED", f"S04ClaimAdmissibility missing required modules: {missing}"))


def _require_s04_mapping_list(
    payload: dict[str, Any],
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    container = _require_mapping(payload, field, code, errors)
    if container is None:
        return []
    records = container.get(key)
    if allow_empty and records == []:
        return []
    if not is_non_empty_mapping_list(records):
        errors.append(issue(code, f"{field}.{key} must be a non-empty list of mappings"))
        return []
    assert isinstance(records, list)
    result: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        result.append(record)
        for required_key in required:
            if not is_non_empty_string(record.get(required_key)):
                errors.append(issue(code, f"{field}.{key}[{idx}].{required_key} must be a non-empty string"))
    return result


def _record_ids(records: list[dict[str, Any]], field: str) -> set[str]:
    return {str(record.get(field)) for record in records if is_non_empty_string(record.get(field))}


def _validate_s04_claim_queue(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    return _require_s04_mapping_list(
        payload,
        "claim_queue",
        "claims",
        ["source_claim_id", "source_option_id", "proposed_claim", "claim_type", "source_material_ref", "intended_downstream_use"],
        "E_S04_CLAIM_QUEUE_REQUIRED",
        errors,
    )


def _validate_s04_atomic_claims(payload: dict[str, Any], claim_queue: list[dict[str, Any]], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    source_claim_ids = _record_ids(claim_queue, "source_claim_id")
    decomposition = _require_s04_mapping_list(
        payload,
        "claim_unit_decomposition",
        "units",
        ["source_claim_id", "atomic_claim_id", "claim_type", "component_claim", "decomposition_status"],
        "E_S04_ATOMIC_CLAIM_REQUIRED",
        errors,
    )
    atomic = _require_s04_mapping_list(
        payload,
        "atomic_claim_register",
        "atomic_claims",
        ["atomic_claim_id", "source_claim_id", "claim_type", "processing_status"],
        "E_S04_ATOMIC_CLAIM_REQUIRED",
        errors,
    )
    decomposed_sources = _record_ids(decomposition, "source_claim_id")
    missing_decomposition = sorted(source_claim_ids - decomposed_sources)
    if missing_decomposition:
        errors.append(issue("E_S04_ATOMIC_CLAIM_REQUIRED", f"claim_unit_decomposition missing source claims {missing_decomposition}"))
    registered_atomic = _record_ids(atomic, "atomic_claim_id")
    decomposed_atomic = _record_ids(decomposition, "atomic_claim_id")
    missing_atomic = sorted(decomposed_atomic - registered_atomic)
    if missing_atomic:
        errors.append(issue("E_S04_ATOMIC_CLAIM_REQUIRED", f"atomic_claim_register missing atomic claims {missing_atomic}"))
    for idx, record in enumerate(atomic):
        status = record.get("processing_status")
        if status not in S02_PROCESSING_STATUSES:
            errors.append(issue("E_S04_ATOMIC_CLAIM_REQUIRED", f"atomic_claim_register.atomic_claims[{idx}].processing_status must be one of {sorted(S02_PROCESSING_STATUSES)}"))
    return atomic


def _validate_s04_claim_coverage(payload: dict[str, Any], claim_queue: list[dict[str, Any]], atomic: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    source_claim_ids = _record_ids(claim_queue, "source_claim_id")
    atomic_ids = _record_ids(atomic, "atomic_claim_id")
    coverage = _require_s04_mapping_list(
        payload,
        "claim_coverage_ledger",
        "claims",
        ["source_claim_id", "decision_status", "processing_status"],
        "E_S04_COVERAGE_LEDGER_REQUIRED",
        errors,
    )
    coverage_ids = _record_ids(coverage, "source_claim_id")
    missing = sorted(source_claim_ids - coverage_ids)
    if missing:
        errors.append(issue("E_S04_COVERAGE_LEDGER_REQUIRED", f"claim_coverage_ledger missing source claims {missing}"))
    for idx, record in enumerate(coverage):
        if record.get("decision_status") not in S04_CLAIM_STATUSES:
            errors.append(issue("E_S04_COVERAGE_LEDGER_REQUIRED", f"claim_coverage_ledger.claims[{idx}].decision_status must be one of {sorted(S04_CLAIM_STATUSES)}"))
        if record.get("processing_status") not in S02_PROCESSING_STATUSES:
            errors.append(issue("E_S04_COVERAGE_LEDGER_REQUIRED", f"claim_coverage_ledger.claims[{idx}].processing_status must be one of {sorted(S02_PROCESSING_STATUSES)}"))
        raw_atomic_ids = record.get("atomic_claim_ids")
        if not is_non_empty_string_list(raw_atomic_ids):
            errors.append(issue("E_S04_COVERAGE_LEDGER_REQUIRED", f"claim_coverage_ledger.claims[{idx}].atomic_claim_ids must be a non-empty list of strings"))
        else:
            assert isinstance(raw_atomic_ids, list)
            unknown = sorted(set(raw_atomic_ids) - atomic_ids)
            if unknown:
                errors.append(issue("E_S04_COVERAGE_LEDGER_REQUIRED", f"claim_coverage_ledger.claims[{idx}].atomic_claim_ids references unknown claims {unknown}"))


def _validate_s04_capsules(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    capsules = _require_s04_mapping_list(
        payload,
        "claim_capsules",
        "capsules",
        [
            "claim_id",
            "source_claim_id",
            "admitted_claim",
            "status",
            "support_strength",
            "evidence_anchors",
            "allowed_wording_ref",
            "forbidden_wording_ref",
            "required_caveats",
            "result_package_boundary_ref",
            "downstream_use_permission",
        ],
        "E_S04_CLAIM_CAPSULE_REQUIRED",
        errors,
    )
    for idx, capsule in enumerate(capsules):
        status = capsule.get("status")
        support = capsule.get("support_strength")
        if status not in S04_CLAIM_STATUSES:
            errors.append(issue("E_S04_CLAIM_CAPSULE_REQUIRED", f"claim_capsules.capsules[{idx}].status must be one of {sorted(S04_CLAIM_STATUSES)}"))
        if support not in S04_SUPPORT_STRENGTHS:
            errors.append(issue("E_S04_SUPPORT_STRENGTH_REQUIRED", f"claim_capsules.capsules[{idx}].support_strength must be one of {sorted(S04_SUPPORT_STRENGTHS)}"))
        if status in {"admitted", "weakened"} and support in {"unsupported", "forbidden"}:
            errors.append(issue("E_S04_UNSUPPORTED_ADMITTED", f"claim_capsules.capsules[{idx}] must not admit unsupported/forbidden claim {capsule.get('claim_id')!r}"))
    return capsules


def _validate_s04_support_and_evidence(payload: dict[str, Any], capsules: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    claim_ids = _record_ids(capsules, "claim_id")
    strengths = _require_s04_mapping_list(
        payload,
        "support_strength_map",
        "claims",
        ["claim_id", "support_strength", "evidence_refs", "limitation", "confidence"],
        "E_S04_SUPPORT_STRENGTH_REQUIRED",
        errors,
    )
    strength_ids = _record_ids(strengths, "claim_id")
    missing_strength = sorted(claim_ids - strength_ids)
    if missing_strength:
        errors.append(issue("E_S04_SUPPORT_STRENGTH_REQUIRED", f"support_strength_map missing claims {missing_strength}"))
    for idx, record in enumerate(strengths):
        if record.get("support_strength") not in S04_SUPPORT_STRENGTHS:
            errors.append(issue("E_S04_SUPPORT_STRENGTH_REQUIRED", f"support_strength_map.claims[{idx}].support_strength must be one of {sorted(S04_SUPPORT_STRENGTHS)}"))

    anchors = _require_s04_mapping_list(
        payload,
        "evidence_anchor_map",
        "anchors",
        ["claim_id", "material_ref", "source_locator", "citation_locator", "result_artifact", "visibility_status"],
        "E_S04_EVIDENCE_ANCHOR_REQUIRED",
        errors,
    )
    anchor_ids = _record_ids(anchors, "claim_id")
    admitted_ids = {
        str(capsule.get("claim_id"))
        for capsule in capsules
        if capsule.get("status") in {"admitted", "weakened"} and is_non_empty_string(capsule.get("claim_id"))
    }
    missing_anchors = sorted(admitted_ids - anchor_ids)
    if missing_anchors:
        errors.append(issue("E_S04_EVIDENCE_ANCHOR_REQUIRED", f"evidence_anchor_map missing admitted/weakened claims {missing_anchors}"))

    coverage = _require_mapping(payload, "evidence_locator_coverage", "E_S04_EVIDENCE_ANCHOR_REQUIRED", errors)
    _require_string_list(coverage, "evidence_locator_coverage", "claim_ids_with_locators", "E_S04_EVIDENCE_ANCHOR_REQUIRED", errors, allow_empty=True)
    _require_string_list(coverage, "evidence_locator_coverage", "missing_locator_claim_ids", "E_S04_EVIDENCE_ANCHOR_REQUIRED", errors, allow_empty=True)
    _require_string_list(coverage, "evidence_locator_coverage", "visibility_gaps", "E_S04_EVIDENCE_ANCHOR_REQUIRED", errors, allow_empty=True)
    if coverage is not None and isinstance(coverage.get("claim_ids_with_locators"), list):
        missing_from_coverage = sorted(admitted_ids - set(coverage["claim_ids_with_locators"]))
        if missing_from_coverage:
            errors.append(issue("E_S04_EVIDENCE_ANCHOR_REQUIRED", f"evidence_locator_coverage.claim_ids_with_locators missing {missing_from_coverage}"))


def _validate_s04_wording(payload: dict[str, Any], capsules: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    claim_ids = _record_ids(capsules, "claim_id")
    allowed = _require_s04_mapping_list(
        payload,
        "allowed_wording_map",
        "claims",
        ["claim_id", "admitted_wording", "safe_verbs", "required_qualifiers", "section_permissions"],
        "E_S04_ALLOWED_WORDING_REQUIRED",
        errors,
    )
    allowed_ids = _record_ids(allowed, "claim_id")
    missing_allowed = sorted(claim_ids - allowed_ids)
    if missing_allowed:
        errors.append(issue("E_S04_ALLOWED_WORDING_REQUIRED", f"allowed_wording_map missing claims {missing_allowed}"))

    forbidden = _require_s04_mapping_list(
        payload,
        "forbidden_wording_map",
        "claims",
        ["claim_id", "forbidden_wording", "forbidden_interpretations", "forbidden_scope_expansions", "owner_or_evidence_required_before_use"],
        "E_S04_FORBIDDEN_WORDING_REQUIRED",
        errors,
    )
    forbidden_ids = _record_ids(forbidden, "claim_id")
    missing_forbidden = sorted(claim_ids - forbidden_ids)
    if missing_forbidden:
        errors.append(issue("E_S04_FORBIDDEN_WORDING_REQUIRED", f"forbidden_wording_map missing claims {missing_forbidden}"))


def _validate_s04_result_boundaries(payload: dict[str, Any], capsules: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    claim_ids = _record_ids(capsules, "claim_id")
    packages = _require_s04_mapping_list(
        payload,
        "result_package_boundary_matrix",
        "packages",
        ["package_id", "supports", "does_not_support", "allowed_metrics", "forbidden_interpretations", "required_caveats", "visibility_status"],
        "E_S04_RESULT_BOUNDARY_REQUIRED",
        errors,
    )
    supported_claims: set[str] = set()
    for idx, package in enumerate(packages):
        raw_claim_ids = package.get("supports_claim_ids")
        if not is_non_empty_string_list(raw_claim_ids):
            errors.append(issue("E_S04_RESULT_BOUNDARY_REQUIRED", f"result_package_boundary_matrix.packages[{idx}].supports_claim_ids must be a non-empty list of strings"))
            continue
        assert isinstance(raw_claim_ids, list)
        supported_claims.update(str(item) for item in raw_claim_ids)
    missing_boundaries = sorted(claim_ids - supported_claims)
    if missing_boundaries:
        errors.append(issue("E_S04_RESULT_BOUNDARY_REQUIRED", f"result_package_boundary_matrix missing claims {missing_boundaries}"))


def _validate_s04_transformation_and_backflow(payload: dict[str, Any], claim_queue: list[dict[str, Any]], capsules: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    source_claim_ids = _record_ids(claim_queue, "source_claim_id")
    transformations = _require_s04_mapping_list(
        payload,
        "claim_transformation_log",
        "transformations",
        ["source_claim_id", "source_option_id", "original_candidate_wording", "admitted_or_rejected_wording", "decision", "reason_for_change", "backflow_target"],
        "E_S04_TRANSFORMATION_LOG_REQUIRED",
        errors,
    )
    transformation_ids = _record_ids(transformations, "source_claim_id")
    missing_transformations = sorted(source_claim_ids - transformation_ids)
    if missing_transformations:
        errors.append(issue("E_S04_TRANSFORMATION_LOG_REQUIRED", f"claim_transformation_log missing source claims {missing_transformations}"))
    for idx, record in enumerate(transformations):
        if record.get("decision") not in S04_CLAIM_STATUSES:
            errors.append(issue("E_S04_TRANSFORMATION_LOG_REQUIRED", f"claim_transformation_log.transformations[{idx}].decision must be one of {sorted(S04_CLAIM_STATUSES)}"))

    unsupported = _require_s04_mapping_list(
        payload,
        "unsupported_claim_backflow_register",
        "unsupported_claims",
        ["source_claim_id", "claim_or_component", "rejection_reason", "missing_evidence", "backflow_target"],
        "E_S04_UNSUPPORTED_BACKFLOW_REQUIRED",
        errors,
        allow_empty=True,
    )
    unsupported_ids = _record_ids(unsupported, "source_claim_id")
    rejected_or_backflowed_sources = {
        str(capsule.get("source_claim_id"))
        for capsule in capsules
        if capsule.get("status") in {"rejected", "backflowed"} and is_non_empty_string(capsule.get("source_claim_id"))
    }
    missing_backflow = sorted(rejected_or_backflowed_sources - unsupported_ids)
    if missing_backflow:
        errors.append(issue("E_S04_UNSUPPORTED_BACKFLOW_REQUIRED", f"unsupported_claim_backflow_register missing rejected/backflowed source claims {missing_backflow}"))


def _validate_s04_downstream(payload: dict[str, Any], capsules: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    claim_ids = _record_ids(capsules, "claim_id")
    handoffs = _require_mapping(payload, "downstream_handoffs", "E_S04_DOWNSTREAM_HANDOFF_REQUIRED", errors)
    if handoffs is not None:
        missing_stages = sorted(stage for stage in S04_REQUIRED_HANDOFF_STAGES if not isinstance(handoffs.get(stage), dict))
        if missing_stages:
            errors.append(issue("E_S04_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoffs missing stage handoffs: {missing_stages}"))
        for stage in sorted(S04_REQUIRED_HANDOFF_STAGES):
            handoff = as_mapping(handoffs.get(stage))
            if handoff is None:
                continue
            for key in ("handoff_summary", "allowed_use", "misuse_warning"):
                if not is_non_empty_string(handoff.get(key)):
                    errors.append(issue("E_S04_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoffs.{stage}.{key} must be a non-empty string"))
            raw_claims = handoff.get("claim_ids")
            if not is_non_empty_string_list(raw_claims):
                errors.append(issue("E_S04_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoffs.{stage}.claim_ids must be a non-empty list of strings"))

    permissions = _require_s04_mapping_list(
        payload,
        "downstream_use_permission_matrix",
        "permissions",
        ["claim_id", "s05_allowed", "s07_allowed", "s10_allowed", "s12_s13_audit_required"],
        "E_S04_DOWNSTREAM_PERMISSION_REQUIRED",
        errors,
    )
    permission_ids = _record_ids(permissions, "claim_id")
    missing_permissions = sorted(claim_ids - permission_ids)
    if missing_permissions:
        errors.append(issue("E_S04_DOWNSTREAM_PERMISSION_REQUIRED", f"downstream_use_permission_matrix missing claims {missing_permissions}"))


def _validate_s04_data_and_unresolved(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    data_plan = _require_mapping(payload, "data_availability_plan", "E_S04_DATA_AVAILABILITY_REQUIRED", errors)
    for key in ("paper_visible_artifacts", "supplementary_artifacts", "internal_only_artifacts", "missing_artifacts", "disclosure_caveats"):
        _require_list_field(data_plan, "data_availability_plan", key, "E_S04_DATA_AVAILABILITY_REQUIRED", errors, allow_empty=True)
    unresolved = _require_mapping(payload, "unresolved_backflow_register", "E_S04_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_string_list(unresolved, "unresolved_backflow_register", "backflow_targets", "E_S04_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_backflow_register", "unresolved_items", "E_S04_UNRESOLVED_BACKFLOW_REQUIRED", errors, allow_empty=True)


def _validate_s04_claim_admissibility(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s04_payload_header(payload, "ppg-s04-claim-admissibility/v0.1", "E_S04_CLAIM_ADMISSIBILITY_REQUIRED", errors)
    _require_s04_required_modules(payload, errors)
    if payload.get("completion_boundary") != S04_COMPLETION_BOUNDARY:
        errors.append(issue("E_S04_COMPLETION_BOUNDARY", f"completion_boundary must be {S04_COMPLETION_BOUNDARY!r}"))

    completion_overclaim_key = _contains_forbidden_key(payload, S04_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S04_NO_COMPLETION_OVERCLAIM", f"S04 claim admissibility must not contain completion field {completion_overclaim_key!r}"))
    final_prose_key = _contains_forbidden_key(payload, S04_FINAL_PROSE_KEYS)
    if final_prose_key is not None:
        errors.append(issue("E_S04_NO_FINAL_PROSE", f"S04 claim admissibility must not contain final-prose/manuscript field {final_prose_key!r}"))

    claim_queue = _validate_s04_claim_queue(payload, errors)
    atomic = _validate_s04_atomic_claims(payload, claim_queue, errors)
    _validate_s04_claim_coverage(payload, claim_queue, atomic, errors)
    capsules = _validate_s04_capsules(payload, errors)
    _validate_s04_support_and_evidence(payload, capsules, errors)
    _validate_s04_wording(payload, capsules, errors)
    _validate_s04_result_boundaries(payload, capsules, errors)
    _validate_s04_transformation_and_backflow(payload, claim_queue, capsules, errors)
    _validate_s04_downstream(payload, capsules, errors)
    _validate_s04_data_and_unresolved(payload, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S04_CLAIM_ADMISSIBILITY_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S04_CLAIM_ADMISSIBILITY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S04_CLAIM_ADMISSIBILITY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S04_CLAIM_ADMISSIBILITY_REQUIRED", errors, allow_empty=True)


def _require_s05_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "admitted_claim_intake_ledger",
        "reader_question_inventory",
        "reader_question_coverage_ledger",
        "reader_spine",
        "reviewer_question_map",
        "rationale_matrix",
        "claim_section_coverage_ledger",
        "front_half_promise_coverage",
        "excluded_claim_or_question_register",
        "owner_decision_log",
        "s06_handoff",
        "s07_handoff",
        "s08_handoff",
        "s06_s07_s08_handoff_coverage",
        "coherence_overpromise_audit",
        "unresolved_backflow_register",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S05_READER_SPINE_REQUIRED", f"S05ReaderSpine missing required modules: {missing}"))


def _require_s05_mapping_list(
    payload: dict[str, Any] | None,
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    container = _require_mapping(payload, field, code, errors) if payload is not None else None
    if container is None:
        return []
    return _require_s05_list_records(container, f"{field}.{key}", key, required, code, errors, allow_empty=allow_empty)


def _require_s05_list_records(
    container: dict[str, Any] | None,
    label: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    if container is None:
        return []
    records = container.get(key)
    if allow_empty and records == []:
        return []
    if not is_non_empty_mapping_list(records):
        errors.append(issue(code, f"{label} must be a non-empty list of mappings"))
        return []
    assert isinstance(records, list)
    result: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        result.append(record)
        for required_key in required:
            if not is_non_empty_string(record.get(required_key)):
                errors.append(issue(code, f"{label}[{idx}].{required_key} must be a non-empty string"))
    return result


def _validate_s05_admitted_claims(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    claims = _require_s05_mapping_list(
        payload,
        "admitted_claim_intake_ledger",
        "claims",
        ["claim_id", "source_s04_capsule", "admitted_claim", "support_strength", "required_caveat", "intake_status"],
        "E_S05_ADMITTED_CLAIM_INTAKE_REQUIRED",
        errors,
    )
    for idx, claim in enumerate(claims):
        status = claim.get("intake_status")
        if status not in S05_CLAIM_PLACEMENT_STATUSES:
            errors.append(
                issue(
                    "E_S05_ADMITTED_CLAIM_INTAKE_REQUIRED",
                    f"admitted_claim_intake_ledger.claims[{idx}].intake_status must be one of {sorted(S05_CLAIM_PLACEMENT_STATUSES)}",
                )
            )
    return claims


def _validate_s05_reader_questions(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    questions = _require_s05_mapping_list(
        payload,
        "reader_question_inventory",
        "questions",
        ["question_id", "reader_question", "why_asked_now", "source_claim_ids", "priority"],
        "E_S05_READER_QUESTION_REQUIRED",
        errors,
    )
    coverage = _require_s05_mapping_list(
        payload,
        "reader_question_coverage_ledger",
        "questions",
        ["question_id", "coverage_status", "section_or_backflow", "answer_path"],
        "E_S05_READER_QUESTION_COVERAGE_REQUIRED",
        errors,
    )
    question_ids = _record_ids(questions, "question_id")
    coverage_ids = _record_ids(coverage, "question_id")
    missing = sorted(question_ids - coverage_ids)
    if missing:
        errors.append(issue("E_S05_READER_QUESTION_COVERAGE_REQUIRED", f"reader_question_coverage_ledger missing questions {missing}"))
    unknown = sorted(coverage_ids - question_ids)
    if unknown:
        errors.append(issue("E_S05_READER_QUESTION_COVERAGE_REQUIRED", f"reader_question_coverage_ledger contains unknown questions {unknown}"))
    for idx, record in enumerate(coverage):
        if record.get("coverage_status") not in S05_QUESTION_STATUSES:
            errors.append(
                issue(
                    "E_S05_READER_QUESTION_COVERAGE_REQUIRED",
                    f"reader_question_coverage_ledger.questions[{idx}].coverage_status must be one of {sorted(S05_QUESTION_STATUSES)}",
                )
            )
    return questions


def _validate_s05_reader_spine_modules(payload: dict[str, Any], admitted_claims: list[dict[str, Any]], questions: list[dict[str, Any]], errors: list[ValidationIssue]) -> set[str]:
    spine = _require_mapping(payload, "reader_spine", "E_S05_READER_SPINE_REQUIRED", errors)
    if spine is None:
        return set()
    claim_ids = _record_ids(admitted_claims, "claim_id")
    question_ids = _record_ids(questions, "question_id")
    progression = _require_s05_list_records(
        spine,
        "reader_spine.reader_question_progression",
        "reader_question_progression",
        ["step_id", "question_id", "reader_question", "section_or_unit", "answer_function", "required_prior_context"],
        "E_S05_READER_QUESTION_REQUIRED",
        errors,
    )
    progression_question_ids = _record_ids(progression, "question_id")
    missing_question_progression = sorted(question_ids - progression_question_ids)
    if missing_question_progression:
        errors.append(issue("E_S05_READER_QUESTION_REQUIRED", f"reader_spine.reader_question_progression missing questions {missing_question_progression}"))
    unknown_progression = sorted(progression_question_ids - question_ids)
    if unknown_progression:
        errors.append(issue("E_S05_READER_QUESTION_REQUIRED", f"reader_spine.reader_question_progression contains unknown questions {unknown_progression}"))

    claim_spine = _require_s05_list_records(
        spine,
        "reader_spine.claim_to_section_spine",
        "claim_to_section_spine",
        ["claim_id", "source_s04_capsule", "section", "rhetorical_role", "first_appearance", "required_caveat", "forbidden_expansion"],
        "E_S05_CLAIM_SECTION_SPINE_REQUIRED",
        errors,
    )
    placed_claim_ids = _record_ids(claim_spine, "claim_id")
    unknown_claims = sorted(placed_claim_ids - claim_ids)
    if unknown_claims:
        errors.append(issue("E_S05_NO_NEW_CLAIMS", f"reader_spine.claim_to_section_spine contains claims not admitted by S04 intake: {unknown_claims}"))
    expected_placed_claims = {
        str(claim.get("claim_id"))
        for claim in admitted_claims
        if claim.get("intake_status") == "placed" and is_non_empty_string(claim.get("claim_id"))
    }
    missing_placed_claims = sorted(expected_placed_claims - placed_claim_ids)
    if missing_placed_claims:
        errors.append(issue("E_S05_CLAIM_SECTION_SPINE_REQUIRED", f"reader_spine.claim_to_section_spine missing placed claims {missing_placed_claims}"))

    promise_map = _require_s05_list_records(
        spine,
        "reader_spine.front_half_promise_map",
        "front_half_promise_map",
        ["promise_id", "promise", "where_introduced", "payoff_section", "required_claim_capsules", "overpromise_risk"],
        "E_S05_FRONT_HALF_PROMISE_REQUIRED",
        errors,
    )
    if not promise_map:
        return set()
    promise_ids = _record_ids(promise_map, "promise_id")
    _require_s05_list_records(
        spine,
        "reader_spine.story_arc_matrix",
        "story_arc_matrix",
        ["arc_id", "problem_pressure", "unresolved_gap", "method_object", "evidence_ladder", "boundary_discovery", "implication", "limitation"],
        "E_S05_READER_SPINE_REQUIRED",
        errors,
    )
    return promise_ids


def _validate_s05_claim_section_coverage(payload: dict[str, Any], admitted_claims: list[dict[str, Any]], questions: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    claim_ids = _record_ids(admitted_claims, "claim_id")
    question_ids = _record_ids(questions, "question_id")
    coverage = _require_s05_mapping_list(
        payload,
        "claim_section_coverage_ledger",
        "claims",
        ["claim_id", "placement_status", "section_or_exclusion", "reader_question_id"],
        "E_S05_CLAIM_SECTION_COVERAGE_REQUIRED",
        errors,
    )
    coverage_ids = _record_ids(coverage, "claim_id")
    missing = sorted(claim_ids - coverage_ids)
    if missing:
        errors.append(issue("E_S05_CLAIM_SECTION_COVERAGE_REQUIRED", f"claim_section_coverage_ledger missing claims {missing}"))
    unknown_claims = sorted(coverage_ids - claim_ids)
    if unknown_claims:
        errors.append(issue("E_S05_NO_NEW_CLAIMS", f"claim_section_coverage_ledger contains claims not admitted by S04 intake: {unknown_claims}"))
    coverage_question_ids = _record_ids(coverage, "reader_question_id")
    unknown_questions = sorted(coverage_question_ids - question_ids)
    if unknown_questions:
        errors.append(issue("E_S05_CLAIM_SECTION_COVERAGE_REQUIRED", f"claim_section_coverage_ledger contains unknown reader questions {unknown_questions}"))
    for idx, record in enumerate(coverage):
        if record.get("placement_status") not in S05_CLAIM_PLACEMENT_STATUSES:
            errors.append(
                issue(
                    "E_S05_CLAIM_SECTION_COVERAGE_REQUIRED",
                    f"claim_section_coverage_ledger.claims[{idx}].placement_status must be one of {sorted(S05_CLAIM_PLACEMENT_STATUSES)}",
                )
            )


def _validate_s05_reviewer_and_rationale(payload: dict[str, Any], admitted_claims: list[dict[str, Any]], questions: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    claim_ids = _record_ids(admitted_claims, "claim_id")
    question_ids = _record_ids(questions, "question_id")
    _require_s05_mapping_list(
        payload,
        "reviewer_question_map",
        "questions",
        ["question_id", "reviewer_question", "severity", "answer_section", "claim_capsule_needed", "risk_if_unanswered", "backflow_target"],
        "E_S05_REVIEWER_QUESTION_REQUIRED",
        errors,
    )
    rationale = _require_s05_mapping_list(
        payload,
        "rationale_matrix",
        "sections",
        ["section", "section_function", "reader_question_answered", "claim_supported", "evidence_used", "dependency_on_previous_section", "risk_if_removed"],
        "E_S05_RATIONALE_MATRIX_REQUIRED",
        errors,
    )
    rationale_question_ids = _record_ids(rationale, "reader_question_answered")
    unknown_questions = sorted(rationale_question_ids - question_ids)
    if unknown_questions:
        errors.append(issue("E_S05_RATIONALE_MATRIX_REQUIRED", f"rationale_matrix.sections contains unknown reader questions {unknown_questions}"))
    rationale_claim_ids = _record_ids(rationale, "claim_supported")
    unknown_claims = sorted(rationale_claim_ids - claim_ids)
    if unknown_claims:
        errors.append(issue("E_S05_NO_NEW_CLAIMS", f"rationale_matrix.sections contains claims not admitted by S04 intake: {unknown_claims}"))


def _validate_s05_promises_exclusions_owner(payload: dict[str, Any], promise_ids: set[str], errors: list[ValidationIssue]) -> None:
    promise_coverage = _require_mapping(payload, "front_half_promise_coverage", "E_S05_FRONT_HALF_PROMISE_REQUIRED", errors)
    _require_string_list(promise_coverage, "front_half_promise_coverage", "promise_ids_with_payoff", "E_S05_FRONT_HALF_PROMISE_REQUIRED", errors, allow_empty=True)
    _require_string_list(promise_coverage, "front_half_promise_coverage", "promise_ids_missing_payoff", "E_S05_FRONT_HALF_PROMISE_REQUIRED", errors, allow_empty=True)
    _require_string_list(promise_coverage, "front_half_promise_coverage", "overpromise_risks", "E_S05_FRONT_HALF_PROMISE_REQUIRED", errors, allow_empty=True)
    if promise_coverage is not None and promise_ids:
        promised_with_payoff = set(promise_coverage.get("promise_ids_with_payoff") or [])
        missing_payoff = set(promise_coverage.get("promise_ids_missing_payoff") or [])
        missing_from_coverage = sorted(promise_ids - promised_with_payoff - missing_payoff)
        if missing_from_coverage:
            errors.append(issue("E_S05_FRONT_HALF_PROMISE_REQUIRED", f"front_half_promise_coverage missing promises {missing_from_coverage}"))
        if missing_payoff:
            errors.append(issue("E_S05_FRONT_HALF_PROMISE_REQUIRED", f"front_half_promise_coverage contains promises without payoff {sorted(missing_payoff)}"))
    excluded = _require_mapping(payload, "excluded_claim_or_question_register", "E_S05_EXCLUSION_REGISTER_REQUIRED", errors)
    _require_list_field(excluded, "excluded_claim_or_question_register", "excluded_claims", "E_S05_EXCLUSION_REGISTER_REQUIRED", errors, allow_empty=True)
    _require_list_field(excluded, "excluded_claim_or_question_register", "excluded_questions", "E_S05_EXCLUSION_REGISTER_REQUIRED", errors, allow_empty=True)
    _require_s05_list_records(
        excluded,
        "excluded_claim_or_question_register.backflow_items",
        "backflow_items",
        ["item_id", "item_type", "reason", "backflow_target"],
        "E_S05_EXCLUSION_REGISTER_REQUIRED",
        errors,
    )
    _require_s05_mapping_list(
        payload,
        "owner_decision_log",
        "decisions",
        ["decision_id", "affected_spine_part", "owner_or_assumption_status", "downstream_block_if_unresolved"],
        "E_S05_OWNER_DECISION_REQUIRED",
        errors,
        allow_empty=True,
    )


def _validate_s05_downstream(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    for field, code in (
        ("s06_handoff", "E_S05_DOWNSTREAM_HANDOFF_REQUIRED"),
        ("s07_handoff", "E_S05_DOWNSTREAM_HANDOFF_REQUIRED"),
        ("s08_handoff", "E_S05_DOWNSTREAM_HANDOFF_REQUIRED"),
    ):
        handoff = _require_mapping(payload, field, code, errors)
        _require_mapping_fields(handoff, field, ["handoff_summary", "allowed_use", "misuse_warning"], code, errors)
        _require_list_field(handoff, field, "items", code, errors, allow_empty=False)
    coverage = _require_mapping(payload, "s06_s07_s08_handoff_coverage", "E_S05_DOWNSTREAM_HANDOFF_REQUIRED", errors)
    if coverage is not None:
        missing = sorted(stage for stage in S05_REQUIRED_HANDOFF_STAGES if not isinstance(coverage.get(stage), dict))
        if missing:
            errors.append(issue("E_S05_DOWNSTREAM_HANDOFF_REQUIRED", f"s06_s07_s08_handoff_coverage missing stage handoffs: {missing}"))
        for stage in sorted(S05_REQUIRED_HANDOFF_STAGES):
            stage_coverage = as_mapping(coverage.get(stage))
            if stage_coverage is None:
                continue
            _require_string_list(stage_coverage, f"s06_s07_s08_handoff_coverage.{stage}", "handed_off_items", "E_S05_DOWNSTREAM_HANDOFF_REQUIRED", errors, allow_empty=True)
            _require_string_list(stage_coverage, f"s06_s07_s08_handoff_coverage.{stage}", "handoff_gaps", "E_S05_DOWNSTREAM_HANDOFF_REQUIRED", errors, allow_empty=True)


def _validate_s05_audit_and_unresolved(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    audit = _require_mapping(payload, "coherence_overpromise_audit", "E_S05_COHERENCE_AUDIT_REQUIRED", errors)
    for key in ("no_new_claims", "no_strengthened_claims", "no_unsupported_promise", "no_hidden_owner_decision"):
        if audit is not None and audit.get(key) is not True:
            errors.append(issue("E_S05_COHERENCE_AUDIT_REQUIRED", f"coherence_overpromise_audit.{key} must be true"))
    _require_string_list(audit, "coherence_overpromise_audit", "remaining_coherence_risks", "E_S05_COHERENCE_AUDIT_REQUIRED", errors, allow_empty=True)
    unresolved = _require_mapping(payload, "unresolved_backflow_register", "E_S05_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_string_list(unresolved, "unresolved_backflow_register", "backflow_targets", "E_S05_UNRESOLVED_BACKFLOW_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_backflow_register", "unresolved_items", "E_S05_UNRESOLVED_BACKFLOW_REQUIRED", errors, allow_empty=True)


def _validate_s05_reader_spine(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s05_payload_header(payload, "ppg-s05-reader-spine/v0.1", "E_S05_READER_SPINE_REQUIRED", errors)
    _require_s05_required_modules(payload, errors)
    if payload.get("completion_boundary") != S05_COMPLETION_BOUNDARY:
        errors.append(issue("E_S05_COMPLETION_BOUNDARY", f"completion_boundary must be {S05_COMPLETION_BOUNDARY!r}"))

    completion_overclaim_key = _contains_forbidden_key(payload, S05_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S05_NO_COMPLETION_OVERCLAIM", f"S05 reader spine must not contain completion field {completion_overclaim_key!r}"))
    final_prose_key = _contains_forbidden_key(payload, S05_FINAL_PROSE_KEYS)
    if final_prose_key is not None:
        errors.append(issue("E_S05_NO_FINAL_PROSE", f"S05 reader spine must not contain final-prose/manuscript field {final_prose_key!r}"))

    admitted_claims = _validate_s05_admitted_claims(payload, errors)
    questions = _validate_s05_reader_questions(payload, errors)
    promise_ids = _validate_s05_reader_spine_modules(payload, admitted_claims, questions, errors)
    _validate_s05_claim_section_coverage(payload, admitted_claims, questions, errors)
    _validate_s05_reviewer_and_rationale(payload, admitted_claims, questions, errors)
    _validate_s05_promises_exclusions_owner(payload, promise_ids, errors)
    _validate_s05_downstream(payload, errors)
    _validate_s05_audit_and_unresolved(payload, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S05_READER_SPINE_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S05_READER_SPINE_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S05_READER_SPINE_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S05_READER_SPINE_REQUIRED", errors, allow_empty=True)


def _require_s06_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "object_inventory",
        "mechanism_variable_inventory",
        "object_cards",
        "mechanism_variable_cards",
        "cross_maps",
        "granularity_progression_map",
        "section_function_budget",
        "cognitive_load_budget",
        "explanation_ladder",
        "repetition_risk_register",
        "coverage_ledger",
        "unresolved_object_report",
        "handoff_to_s07",
        "handoff_to_s08",
        "handoff_to_s10",
        "coherence_and_boundary_audit",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S06_OBJECT_GRANULARITY_REQUIRED", f"S06ObjectGranularity missing required modules: {missing}"))


def _require_s06_mapping_list(
    payload: dict[str, Any] | None,
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    return _require_s05_mapping_list(payload, field, key, required, code, errors, allow_empty=allow_empty)


def _split_s06_ids(value: Any) -> set[str]:
    if isinstance(value, str):
        return {item.strip() for item in value.split(",") if item.strip()}
    if isinstance(value, list):
        return {str(item).strip() for item in value if isinstance(item, str) and item.strip()}
    return set()


def _validate_s06_object_inventory(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    objects = _require_s06_mapping_list(
        payload,
        "object_inventory",
        "objects",
        ["object_id", "object_name", "object_type", "priority", "source_materials", "related_claim_ids", "related_reader_question_ids", "status"],
        "E_S06_OBJECT_INVENTORY_REQUIRED",
        errors,
    )
    for idx, obj in enumerate(objects):
        priority = obj.get("priority")
        if priority not in S06_OBJECT_PRIORITIES:
            errors.append(issue("E_S06_OBJECT_INVENTORY_REQUIRED", f"object_inventory.objects[{idx}].priority must be one of {sorted(S06_OBJECT_PRIORITIES)}"))
        status = obj.get("status")
        if status not in S06_OBJECT_STATUSES:
            errors.append(issue("E_S06_OBJECT_INVENTORY_REQUIRED", f"object_inventory.objects[{idx}].status must be one of {sorted(S06_OBJECT_STATUSES)}"))
    return objects


def _validate_s06_variable_inventory(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    variables = _require_s06_mapping_list(
        payload,
        "mechanism_variable_inventory",
        "variables",
        ["variable_id", "variable_name", "variable_type", "belongs_to_object", "role_in_method", "role_in_experiment", "definition_status", "notation_or_name", "confusion_risk", "status"],
        "E_S06_MECHANISM_VARIABLE_REQUIRED",
        errors,
    )
    for idx, variable in enumerate(variables):
        if variable.get("status") not in S06_VARIABLE_STATUSES:
            errors.append(issue("E_S06_MECHANISM_VARIABLE_REQUIRED", f"mechanism_variable_inventory.variables[{idx}].status must be one of {sorted(S06_VARIABLE_STATUSES)}"))
    return variables


def _validate_s06_object_cards(payload: dict[str, Any], objects: list[dict[str, Any]], errors: list[ValidationIssue]) -> set[str]:
    object_ids = _record_ids(objects, "object_id")
    cards = _require_s06_mapping_list(
        payload,
        "object_cards",
        "cards",
        [
            "object_id",
            "first_appearance",
            "sections_used",
            "representation_modes",
            "granularity_by_section",
            "required_definition",
            "required_example",
            "required_visual_or_formula",
            "cognitive_load_risk",
            "repetition_risk",
            "confusion_risk",
            "downstream_handoff",
            "status",
        ],
        "E_S06_OBJECT_CARD_REQUIRED",
        errors,
    )
    card_ids = _record_ids(cards, "object_id")
    unknown = sorted(card_ids - object_ids)
    if unknown:
        errors.append(issue("E_S06_OBJECT_CARD_REQUIRED", f"object_cards.cards contains unknown objects {unknown}"))
    required_card_ids = {
        str(obj.get("object_id"))
        for obj in objects
        if obj.get("priority") in S06_OBJECT_CARD_PRIORITIES and obj.get("status") in {"represented", "deferred", "downgraded"} and is_non_empty_string(obj.get("object_id"))
    }
    missing = sorted(required_card_ids - card_ids)
    if missing:
        errors.append(issue("E_S06_OBJECT_CARD_REQUIRED", f"object_cards.cards missing P0/P1/P2 objects {missing}"))
    return card_ids


def _validate_s06_variable_cards(payload: dict[str, Any], variables: list[dict[str, Any]], objects: list[dict[str, Any]], errors: list[ValidationIssue]) -> set[str]:
    variable_ids = _record_ids(variables, "variable_id")
    object_ids = _record_ids(objects, "object_id")
    cards = _require_s06_mapping_list(
        payload,
        "mechanism_variable_cards",
        "cards",
        [
            "variable_id",
            "variable_name",
            "variable_type",
            "belongs_to_object",
            "role_in_method",
            "role_in_experiment",
            "sections_used",
            "definition_status",
            "notation_or_name",
            "evidence_source_ref",
            "confusion_risk",
            "visualization_need",
            "status",
        ],
        "E_S06_MECHANISM_VARIABLE_CARD_REQUIRED",
        errors,
    )
    card_ids = _record_ids(cards, "variable_id")
    unknown_vars = sorted(card_ids - variable_ids)
    if unknown_vars:
        errors.append(issue("E_S06_MECHANISM_VARIABLE_CARD_REQUIRED", f"mechanism_variable_cards.cards contains unknown variables {unknown_vars}"))
    for idx, card in enumerate(cards):
        obj_id = card.get("belongs_to_object")
        if is_non_empty_string(obj_id) and str(obj_id) not in object_ids:
            errors.append(issue("E_S06_MECHANISM_VARIABLE_CARD_REQUIRED", f"mechanism_variable_cards.cards[{idx}].belongs_to_object is unknown: {obj_id}"))
    expected = {
        str(variable.get("variable_id"))
        for variable in variables
        if variable.get("status") == "represented" and is_non_empty_string(variable.get("variable_id"))
    }
    missing = sorted(expected - card_ids)
    if missing:
        errors.append(issue("E_S06_MECHANISM_VARIABLE_CARD_REQUIRED", f"mechanism_variable_cards.cards missing represented variables {missing}"))
    return card_ids


def _validate_s06_cross_maps(payload: dict[str, Any], objects: list[dict[str, Any]], variables: list[dict[str, Any]], errors: list[ValidationIssue]) -> set[str]:
    object_ids = _record_ids(objects, "object_id")
    variable_ids = _record_ids(variables, "variable_id")
    claim_ids: set[str] = set()
    reader_question_ids: set[str] = set()
    for obj in objects:
        claim_ids.update(_split_s06_ids(obj.get("related_claim_ids")))
        reader_question_ids.update(_split_s06_ids(obj.get("related_reader_question_ids")))
    cross = _require_mapping(payload, "cross_maps", "E_S06_CROSS_MAP_REQUIRED", errors)
    if cross is None:
        return set()

    _require_s05_list_records(
        cross,
        "cross_maps.object_relation_map",
        "object_relation_map",
        ["source_object_id", "target_object_id", "relation_type", "explanation"],
        "E_S06_CROSS_MAP_REQUIRED",
        errors,
    )
    object_to_claim = _require_s05_list_records(
        cross,
        "cross_maps.object_to_claim_map",
        "object_to_claim_map",
        ["object_id", "claim_id", "mapping_role"],
        "E_S06_CLAIM_OBJECT_MAP_REQUIRED",
        errors,
    )
    object_to_question = _require_s05_list_records(
        cross,
        "cross_maps.object_to_reader_question_map",
        "object_to_reader_question_map",
        ["object_id", "reader_question_id", "mapping_role"],
        "E_S06_READER_QUESTION_OBJECT_MAP_REQUIRED",
        errors,
    )
    object_to_section = _require_s05_list_records(
        cross,
        "cross_maps.object_to_section_map",
        "object_to_section_map",
        ["object_id", "section", "section_role"],
        "E_S06_OBJECT_SECTION_MAP_REQUIRED",
        errors,
    )
    variable_to_object = _require_s05_list_records(
        cross,
        "cross_maps.variable_to_object_map",
        "variable_to_object_map",
        ["variable_id", "object_id", "relation"],
        "E_S06_VARIABLE_OBJECT_MAP_REQUIRED",
        errors,
    )
    _require_s05_list_records(
        cross,
        "cross_maps.section_object_load_map",
        "section_object_load_map",
        ["section", "new_objects", "reused_objects", "load_risk"],
        "E_S06_SECTION_OBJECT_LOAD_MAP_REQUIRED",
        errors,
    )

    mapped_object_ids = _record_ids(object_to_claim + object_to_question + object_to_section, "object_id")
    unknown_objects = sorted(mapped_object_ids - object_ids)
    if unknown_objects:
        errors.append(issue("E_S06_CROSS_MAP_REQUIRED", f"cross_maps contains unknown objects {unknown_objects}"))
    mapped_claim_ids = _record_ids(object_to_claim, "claim_id")
    unknown_claims = sorted(mapped_claim_ids - claim_ids)
    if unknown_claims:
        errors.append(issue("E_S06_NO_NEW_CLAIMS", f"cross_maps.object_to_claim_map contains claims not sourced from S04/S05 intake: {unknown_claims}"))
    mapped_question_ids = _record_ids(object_to_question, "reader_question_id")
    unknown_questions = sorted(mapped_question_ids - reader_question_ids)
    if unknown_questions:
        errors.append(issue("E_S06_READER_QUESTION_OBJECT_MAP_REQUIRED", f"cross_maps.object_to_reader_question_map contains unknown reader questions {unknown_questions}"))
    variable_map_ids = _record_ids(variable_to_object, "variable_id")
    unknown_variables = sorted(variable_map_ids - variable_ids)
    if unknown_variables:
        errors.append(issue("E_S06_VARIABLE_OBJECT_MAP_REQUIRED", f"cross_maps.variable_to_object_map contains unknown variables {unknown_variables}"))
    return {str(record.get("section")) for record in object_to_section if is_non_empty_string(record.get("section"))}


def _validate_s06_granularity_and_budgets(payload: dict[str, Any], objects: list[dict[str, Any]], section_ids: set[str], errors: list[ValidationIssue]) -> None:
    object_ids = _record_ids(objects, "object_id")
    progression = _require_s06_mapping_list(
        payload,
        "granularity_progression_map",
        "entries",
        ["object_id", "section", "intended_granularity", "reason", "forbidden_detail_level", "next_granularity_step"],
        "E_S06_GRANULARITY_REQUIRED",
        errors,
    )
    progression_object_ids = _record_ids(progression, "object_id")
    unknown_objects = sorted(progression_object_ids - object_ids)
    if unknown_objects:
        errors.append(issue("E_S06_GRANULARITY_REQUIRED", f"granularity_progression_map.entries contains unknown objects {unknown_objects}"))
    for idx, record in enumerate(progression):
        if record.get("intended_granularity") not in S06_GRANULARITY_LEVELS:
            errors.append(issue("E_S06_GRANULARITY_REQUIRED", f"granularity_progression_map.entries[{idx}].intended_granularity must be one of {sorted(S06_GRANULARITY_LEVELS)}"))

    section_budget = _require_s06_mapping_list(
        payload,
        "section_function_budget",
        "sections",
        ["section", "allowed_object_functions", "forbidden_object_functions", "max_new_core_objects", "required_prior_context", "risk_if_overloaded"],
        "E_S06_SECTION_FUNCTION_BUDGET_REQUIRED",
        errors,
    )
    section_budget_ids = _record_ids(section_budget, "section")
    missing_section_budget = sorted(section_ids - section_budget_ids)
    if missing_section_budget:
        errors.append(issue("E_S06_SECTION_FUNCTION_BUDGET_REQUIRED", f"section_function_budget.sections missing sections {missing_section_budget}"))

    load_budget = _require_s06_mapping_list(
        payload,
        "cognitive_load_budget",
        "sections",
        ["section", "new_objects", "reused_objects", "formal_symbols", "reader_load_risk", "mitigation", "defer_to_section_or_supplement"],
        "E_S06_COGNITIVE_LOAD_BUDGET_REQUIRED",
        errors,
    )
    load_budget_ids = _record_ids(load_budget, "section")
    missing_load_budget = sorted(section_ids - load_budget_ids)
    if missing_load_budget:
        errors.append(issue("E_S06_COGNITIVE_LOAD_BUDGET_REQUIRED", f"cognitive_load_budget.sections missing sections {missing_load_budget}"))


def _validate_s06_ladders_repetition_coverage(payload: dict[str, Any], objects: list[dict[str, Any]], variables: list[dict[str, Any]], section_ids: set[str], errors: list[ValidationIssue]) -> None:
    required_ladder_ids = {
        str(obj.get("object_id"))
        for obj in objects
        if obj.get("priority") in S06_OBJECT_CARD_PRIORITIES and obj.get("status") in {"represented", "deferred", "downgraded"} and is_non_empty_string(obj.get("object_id"))
    }
    ladders = _require_s06_mapping_list(
        payload,
        "explanation_ladder",
        "ladders",
        ["object_id", "intuition", "pipeline_role", "definition", "mechanism", "formalism", "empirical_example", "boundary_limitation"],
        "E_S06_EXPLANATION_LADDER_REQUIRED",
        errors,
    )
    ladder_ids = _record_ids(ladders, "object_id")
    missing_ladders = sorted(required_ladder_ids - ladder_ids)
    if missing_ladders:
        errors.append(issue("E_S06_EXPLANATION_LADDER_REQUIRED", f"explanation_ladder.ladders missing P0/P1/P2 objects {missing_ladders}"))

    repetition = _require_mapping(payload, "repetition_risk_register", "E_S06_REPETITION_RISK_REQUIRED", errors)
    _require_string_list(repetition, "repetition_risk_register", "checked_object_ids", "E_S06_REPETITION_RISK_REQUIRED", errors)
    _require_list_field(repetition, "repetition_risk_register", "risks", "E_S06_REPETITION_RISK_REQUIRED", errors, allow_empty=True)
    checked_ids = set(repetition.get("checked_object_ids") or []) if repetition is not None else set()
    missing_repetition_check = sorted(required_ladder_ids - checked_ids)
    if missing_repetition_check:
        errors.append(issue("E_S06_REPETITION_RISK_REQUIRED", f"repetition_risk_register.checked_object_ids missing core objects {missing_repetition_check}"))

    object_ids = _record_ids(objects, "object_id")
    variable_ids = _record_ids(variables, "variable_id")
    coverage = _require_mapping(payload, "coverage_ledger", "E_S06_COVERAGE_LEDGER_REQUIRED", errors)
    for key in (
        "objects_detected",
        "objects_processed",
        "objects_unresolved",
        "variables_detected",
        "variables_processed",
        "variables_unresolved",
        "claims_mapped",
        "claims_unmapped",
        "reader_questions_mapped",
        "reader_questions_unmapped",
        "sections_with_load_budget",
        "sections_missing_load_budget",
    ):
        _require_string_list(coverage, "coverage_ledger", key, "E_S06_COVERAGE_LEDGER_REQUIRED", errors, allow_empty=key.endswith("_unresolved") or key.endswith("_unmapped") or key == "sections_missing_load_budget")
    if coverage is not None:
        covered_objects = set(coverage.get("objects_processed") or []) | set(coverage.get("objects_unresolved") or [])
        missing_objects = sorted(object_ids - covered_objects)
        if missing_objects:
            errors.append(issue("E_S06_COVERAGE_LEDGER_REQUIRED", f"coverage_ledger does not reconcile objects {missing_objects}"))
        covered_variables = set(coverage.get("variables_processed") or []) | set(coverage.get("variables_unresolved") or [])
        missing_variables = sorted(variable_ids - covered_variables)
        if missing_variables:
            errors.append(issue("E_S06_COVERAGE_LEDGER_REQUIRED", f"coverage_ledger does not reconcile variables {missing_variables}"))
        if coverage.get("claims_unmapped"):
            errors.append(issue("E_S06_CLAIM_OBJECT_MAP_REQUIRED", f"coverage_ledger.claims_unmapped must be empty before S06 completion: {coverage.get('claims_unmapped')}"))
        if coverage.get("reader_questions_unmapped"):
            errors.append(issue("E_S06_READER_QUESTION_OBJECT_MAP_REQUIRED", f"coverage_ledger.reader_questions_unmapped must be empty before S06 completion: {coverage.get('reader_questions_unmapped')}"))
        missing_sections = sorted(section_ids - set(coverage.get("sections_with_load_budget") or []))
        if missing_sections:
            errors.append(issue("E_S06_COGNITIVE_LOAD_BUDGET_REQUIRED", f"coverage_ledger.sections_with_load_budget missing sections {missing_sections}"))
        if coverage.get("sections_missing_load_budget"):
            errors.append(issue("E_S06_COGNITIVE_LOAD_BUDGET_REQUIRED", f"coverage_ledger.sections_missing_load_budget must be empty before S06 completion: {coverage.get('sections_missing_load_budget')}"))


def _validate_s06_unresolved_handoffs_audit(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    unresolved = _require_mapping(payload, "unresolved_object_report", "E_S06_UNRESOLVED_OBJECT_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_object_report", "items", "E_S06_UNRESOLVED_OBJECT_REQUIRED", errors, allow_empty=True)
    _require_string_list(unresolved, "unresolved_object_report", "backflow_targets", "E_S06_UNRESOLVED_OBJECT_REQUIRED", errors, allow_empty=True)

    for handoff_field in sorted(S06_REQUIRED_HANDOFFS):
        handoff = _require_mapping(payload, handoff_field, "E_S06_DOWNSTREAM_HANDOFF_REQUIRED", errors)
        _require_mapping_fields(handoff, handoff_field, ["handoff_summary", "allowed_use", "misuse_warning"], "E_S06_DOWNSTREAM_HANDOFF_REQUIRED", errors)
        _require_list_field(handoff, handoff_field, "items", "E_S06_DOWNSTREAM_HANDOFF_REQUIRED", errors, allow_empty=False)

    audit = _require_mapping(payload, "coherence_and_boundary_audit", "E_S06_BOUNDARY_AUDIT_REQUIRED", errors)
    for key in ("no_new_claims", "no_strengthened_claims", "no_final_prose", "no_hidden_unresolved_objects", "no_flat_repetition_without_progression"):
        if audit is not None and audit.get(key) is not True:
            errors.append(issue("E_S06_BOUNDARY_AUDIT_REQUIRED", f"coherence_and_boundary_audit.{key} must be true"))
    _require_string_list(audit, "coherence_and_boundary_audit", "remaining_risks", "E_S06_BOUNDARY_AUDIT_REQUIRED", errors, allow_empty=True)


def _validate_s06_object_granularity(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s06_payload_header(payload, "ppg-s06-object-granularity/v0.1", "E_S06_OBJECT_GRANULARITY_REQUIRED", errors)
    _require_s06_required_modules(payload, errors)
    if payload.get("completion_boundary") != S06_COMPLETION_BOUNDARY:
        errors.append(issue("E_S06_COMPLETION_BOUNDARY", f"completion_boundary must be {S06_COMPLETION_BOUNDARY!r}"))

    completion_overclaim_key = _contains_forbidden_key(payload, S06_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S06_NO_COMPLETION_OVERCLAIM", f"S06 object granularity must not contain completion field {completion_overclaim_key!r}"))
    final_prose_key = _contains_forbidden_key(payload, S06_FINAL_PROSE_KEYS)
    if final_prose_key is not None:
        errors.append(issue("E_S06_NO_FINAL_PROSE", f"S06 object granularity must not contain final-prose/manuscript field {final_prose_key!r}"))

    objects = _validate_s06_object_inventory(payload, errors)
    variables = _validate_s06_variable_inventory(payload, errors)
    _validate_s06_object_cards(payload, objects, errors)
    _validate_s06_variable_cards(payload, variables, objects, errors)
    section_ids = _validate_s06_cross_maps(payload, objects, variables, errors)
    _validate_s06_granularity_and_budgets(payload, objects, section_ids, errors)
    _validate_s06_ladders_repetition_coverage(payload, objects, variables, section_ids, errors)
    _validate_s06_unresolved_handoffs_audit(payload, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S06_OBJECT_GRANULARITY_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S06_OBJECT_GRANULARITY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S06_OBJECT_GRANULARITY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S06_OBJECT_GRANULARITY_REQUIRED", errors, allow_empty=True)


def _require_s07_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "input_coverage_ledger",
        "claim_surface_rule_map",
        "terminology_surface_register",
        "internal_id_ban_list",
        "paragraph_job_map",
        "rhetorical_move_matrix",
        "flexible_language_control",
        "surface_rules",
        "forbidden_expression_list",
        "coverage_ledger",
        "unresolved_surface_control_report",
        "downstream_handoff",
        "surface_safety_audit",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S07_SURFACE_CONTROL_REQUIRED", f"S07RhetoricSurfaceControl missing required modules: {missing}"))


def _require_s07_mapping_list(
    payload: dict[str, Any] | None,
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    return _require_s05_mapping_list(payload, field, key, required, code, errors, allow_empty=allow_empty)


def _validate_s07_input_coverage(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    ledger = _require_mapping(payload, "input_coverage_ledger", "E_S07_INPUT_COVERAGE_REQUIRED", errors)
    for key in (
        "s02_language_profile_read",
        "s02_misuse_guard_read",
        "s04_claim_capsules_read",
        "s04_allowed_forbidden_wording_read",
        "s05_reader_spine_read",
        "s05_reviewer_question_map_read",
        "s06_object_representation_read",
        "s06_explanation_ladder_read",
        "terminology_register_read",
    ):
        if ledger is not None and ledger.get(key) is not True:
            errors.append(issue("E_S07_INPUT_COVERAGE_REQUIRED", f"input_coverage_ledger.{key} must be true"))
    _require_string_list(ledger, "input_coverage_ledger", "missing_inputs", "E_S07_INPUT_COVERAGE_REQUIRED", errors, allow_empty=True)
    _require_string_list(ledger, "input_coverage_ledger", "unresolved_inputs", "E_S07_INPUT_COVERAGE_REQUIRED", errors, allow_empty=True)
    _require_list_field(ledger, "input_coverage_ledger", "backflow_targets", "E_S07_INPUT_COVERAGE_REQUIRED", errors, allow_empty=True)


def _validate_s07_claim_surface_rules(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    rules = _require_s07_mapping_list(
        payload,
        "claim_surface_rule_map",
        "rules",
        [
            "claim_id",
            "admitted_claim",
            "support_strength",
            "source_s04_capsule",
            "allowed_verbs",
            "allowed_modifiers",
            "required_qualifiers",
            "forbidden_verbs",
            "forbidden_modifiers",
            "forbidden_expansions",
            "allowed_sections",
            "forbidden_sections",
            "required_caveats",
            "citation_attachment_rule",
            "result_evidence_boundary",
            "downstream_writing_permission",
            "status",
        ],
        "E_S07_CLAIM_SURFACE_RULE_REQUIRED",
        errors,
    )
    for idx, rule in enumerate(rules):
        if rule.get("status") not in S07_RULE_STATUSES:
            errors.append(issue("E_S07_CLAIM_SURFACE_RULE_REQUIRED", f"claim_surface_rule_map.rules[{idx}].status must be one of {sorted(S07_RULE_STATUSES)}"))
    return rules


def _validate_s07_terminology_register(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    terms = _require_s07_mapping_list(
        payload,
        "terminology_surface_register",
        "terms",
        [
            "object_or_variable_id",
            "canonical_reader_facing_name",
            "allowed_variants",
            "forbidden_variants",
            "first_definition_location",
            "abbreviation_policy",
            "notation_policy",
            "related_claims",
            "related_sections",
            "required_explanation_level",
            "confusion_risk",
            "claim_strength_risk",
            "status",
        ],
        "E_S07_TERMINOLOGY_REQUIRED",
        errors,
    )
    for idx, term in enumerate(terms):
        if term.get("status") not in S07_TERM_STATUSES:
            errors.append(issue("E_S07_TERMINOLOGY_REQUIRED", f"terminology_surface_register.terms[{idx}].status must be one of {sorted(S07_TERM_STATUSES)}"))
    return terms


def _validate_s07_internal_ids_and_paragraphs(payload: dict[str, Any], errors: list[ValidationIssue]) -> list[dict[str, Any]]:
    ban_items = _require_s07_mapping_list(
        payload,
        "internal_id_ban_list",
        "items",
        ["raw_internal_id_or_pattern", "replacement", "allowed_context_if_any", "forbidden_context", "reason", "detection_note"],
        "E_S07_INTERNAL_ID_BAN_REQUIRED",
        errors,
    )
    if not ban_items:
        errors.append(issue("E_S07_INTERNAL_ID_BAN_REQUIRED", "internal_id_ban_list.items must include internal-id or lab-notebook patterns"))
    jobs = _require_s07_mapping_list(
        payload,
        "paragraph_job_map",
        "jobs",
        [
            "unit_id",
            "section",
            "reader_question_id",
            "paragraph_job",
            "source_claim_ids",
            "source_object_ids",
            "required_evidence",
            "rhetorical_function",
            "forbidden_content",
            "required_caveats",
            "dependency_on_prior_context",
            "downstream_writer_instruction",
        ],
        "E_S07_PARAGRAPH_JOB_REQUIRED",
        errors,
    )
    return jobs


def _validate_s07_moves_and_language(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    moves = _require_s07_mapping_list(
        payload,
        "rhetorical_move_matrix",
        "moves",
        [
            "paragraph_function",
            "allowed_move_variants",
            "required_moves",
            "optional_moves",
            "forbidden_moves",
            "suitable_sections",
            "citation_expectation",
            "claim_strength_limit",
            "flexibility_rule",
            "risk_notes",
        ],
        "E_S07_RHETORICAL_MOVE_REQUIRED",
        errors,
    )
    if len(moves) < 2:
        errors.append(issue("E_S07_RIGID_TEMPLATE_FORBIDDEN", "rhetorical_move_matrix must provide multiple function-specific move variants, not one universal template"))
    control = _require_mapping(payload, "flexible_language_control", "E_S07_FLEXIBLE_LANGUAGE_CONTROL_REQUIRED", errors)
    for key in (
        "statistics_are_descriptive",
        "no_sentence_level_word_count_enforcement",
        "no_fixed_paragraph_length_rule",
        "no_uniform_sentence_cadence",
        "no_exemplar_copying",
        "distributional_similarity_only",
        "local_rhetorical_function_first",
        "claim_boundary_first",
        "readability_first",
    ):
        if control is not None and control.get(key) is not True:
            errors.append(issue("E_S07_FLEXIBLE_LANGUAGE_CONTROL_REQUIRED", f"flexible_language_control.{key} must be true"))


def _validate_s07_surface_and_forbidden(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    rules = _require_mapping(payload, "surface_rules", "E_S07_SURFACE_RULES_REQUIRED", errors)
    for key in (
        "claim_strength_rules",
        "hedge_policy",
        "citation_attachment_rules",
        "comparison_language_policy",
        "limitation_language_policy",
        "result_language_policy",
        "method_language_policy",
        "anti_template_policy",
        "anti_lab_notebook_policy",
        "anti_internal_id_policy",
    ):
        _require_string_list(rules, "surface_rules", key, "E_S07_SURFACE_RULES_REQUIRED", errors)
    categories = _require_s07_mapping_list(
        payload,
        "forbidden_expression_list",
        "categories",
        ["category", "forbidden_patterns", "reason", "safe_alternative"],
        "E_S07_FORBIDDEN_EXPRESSION_REQUIRED",
        errors,
    )
    if len(categories) < 3:
        errors.append(issue("E_S07_FORBIDDEN_EXPRESSION_REQUIRED", "forbidden_expression_list.categories must cover multiple expression-risk categories"))


def _validate_s07_coverage(payload: dict[str, Any], rules: list[dict[str, Any]], terms: list[dict[str, Any]], jobs: list[dict[str, Any]], errors: list[ValidationIssue]) -> None:
    coverage = _require_mapping(payload, "coverage_ledger", "E_S07_COVERAGE_LEDGER_REQUIRED", errors)
    for key in (
        "claim_capsules_read",
        "claim_capsules_with_surface_rules",
        "claim_capsules_unresolved",
        "objects_variables_read",
        "objects_variables_with_terminology_rules",
        "objects_variables_unresolved",
        "reader_questions_read",
        "reader_questions_mapped_to_paragraph_jobs",
        "paragraph_jobs_unresolved",
        "forbidden_expression_categories_populated",
        "downstream_handoffs_generated",
        "unresolved_items",
        "backflow_targets",
    ):
        _require_string_list(
            coverage,
            "coverage_ledger",
            key,
            "E_S07_COVERAGE_LEDGER_REQUIRED",
            errors,
            allow_empty=key.endswith("_unresolved") or key in {"paragraph_jobs_unresolved", "unresolved_items", "backflow_targets"},
        )
    if coverage is None:
        return
    claim_ids = _record_ids(rules, "claim_id")
    covered_claims = set(coverage.get("claim_capsules_with_surface_rules") or []) | set(coverage.get("claim_capsules_unresolved") or [])
    missing_claims = sorted(set(coverage.get("claim_capsules_read") or []) - covered_claims)
    if missing_claims:
        errors.append(issue("E_S07_CLAIM_SURFACE_RULE_REQUIRED", f"coverage_ledger missing surface rules/unresolved records for claims {missing_claims}"))
    unknown_rule_claims = sorted(claim_ids - set(coverage.get("claim_capsules_read") or []))
    if unknown_rule_claims:
        errors.append(issue("E_S07_NO_NEW_CLAIMS", f"claim_surface_rule_map contains claims not declared in coverage_ledger.claim_capsules_read: {unknown_rule_claims}"))
    term_ids = _record_ids(terms, "object_or_variable_id")
    missing_terms = sorted(set(coverage.get("objects_variables_read") or []) - set(coverage.get("objects_variables_with_terminology_rules") or []) - set(coverage.get("objects_variables_unresolved") or []))
    if missing_terms:
        errors.append(issue("E_S07_TERMINOLOGY_REQUIRED", f"coverage_ledger missing terminology/unresolved records for objects/variables {missing_terms}"))
    unknown_terms = sorted(term_ids - set(coverage.get("objects_variables_read") or []))
    if unknown_terms:
        errors.append(issue("E_S07_TERMINOLOGY_REQUIRED", f"terminology_surface_register contains unknown object/variable ids {unknown_terms}"))
    job_question_ids = _record_ids(jobs, "reader_question_id")
    missing_questions = sorted(set(coverage.get("reader_questions_read") or []) - set(coverage.get("reader_questions_mapped_to_paragraph_jobs") or []))
    if missing_questions:
        errors.append(issue("E_S07_PARAGRAPH_JOB_REQUIRED", f"coverage_ledger missing paragraph jobs for reader questions {missing_questions}"))
    unknown_questions = sorted(job_question_ids - set(coverage.get("reader_questions_read") or []))
    if unknown_questions:
        errors.append(issue("E_S07_PARAGRAPH_JOB_REQUIRED", f"paragraph_job_map contains unknown reader questions {unknown_questions}"))
    if coverage.get("claim_capsules_unresolved") or coverage.get("objects_variables_unresolved") or coverage.get("paragraph_jobs_unresolved") or coverage.get("unresolved_items"):
        errors.append(issue("E_S07_UNRESOLVED_SURFACE_CONTROL_REQUIRED", "coverage_ledger unresolved lists must be empty or routed before S07 completion"))


def _validate_s07_unresolved_handoff_audit(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    unresolved = _require_mapping(payload, "unresolved_surface_control_report", "E_S07_UNRESOLVED_SURFACE_CONTROL_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_surface_control_report", "items", "E_S07_UNRESOLVED_SURFACE_CONTROL_REQUIRED", errors, allow_empty=True)
    _require_string_list(unresolved, "unresolved_surface_control_report", "backflow_targets", "E_S07_UNRESOLVED_SURFACE_CONTROL_REQUIRED", errors, allow_empty=True)

    handoff = _require_mapping(payload, "downstream_handoff", "E_S07_DOWNSTREAM_HANDOFF_REQUIRED", errors)
    if handoff is not None:
        missing = sorted(stage for stage in S07_REQUIRED_HANDOFFS if not isinstance(handoff.get(stage), dict))
        if missing:
            errors.append(issue("E_S07_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoff missing stages {missing}"))
        for stage in sorted(S07_REQUIRED_HANDOFFS):
            stage_handoff = as_mapping(handoff.get(stage))
            if stage_handoff is None:
                continue
            _require_mapping_fields(stage_handoff, f"downstream_handoff.{stage}", ["handoff_summary", "allowed_use", "misuse_warning"], "E_S07_DOWNSTREAM_HANDOFF_REQUIRED", errors)
            _require_list_field(stage_handoff, f"downstream_handoff.{stage}", "items", "E_S07_DOWNSTREAM_HANDOFF_REQUIRED", errors, allow_empty=False)

    audit = _require_mapping(payload, "surface_safety_audit", "E_S07_SURFACE_SAFETY_AUDIT_REQUIRED", errors)
    for key in ("no_new_claims", "no_claim_strengthening", "no_final_prose", "no_rigid_language_template", "no_internal_id_leakage", "no_completion_overclaim"):
        if audit is not None and audit.get(key) is not True:
            errors.append(issue("E_S07_SURFACE_SAFETY_AUDIT_REQUIRED", f"surface_safety_audit.{key} must be true"))
    _require_string_list(audit, "surface_safety_audit", "remaining_risks", "E_S07_SURFACE_SAFETY_AUDIT_REQUIRED", errors, allow_empty=True)


def _validate_s07_rhetoric_surface_control(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s07_payload_header(payload, "ppg-s07-rhetoric-surface-control/v0.1", "E_S07_SURFACE_CONTROL_REQUIRED", errors)
    _require_s07_required_modules(payload, errors)
    if payload.get("completion_boundary") != S07_COMPLETION_BOUNDARY:
        errors.append(issue("E_S07_COMPLETION_BOUNDARY", f"completion_boundary must be {S07_COMPLETION_BOUNDARY!r}"))
    completion_overclaim_key = _contains_forbidden_key(payload, S07_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S07_NO_COMPLETION_OVERCLAIM", f"S07 surface control must not contain completion field {completion_overclaim_key!r}"))
    final_prose_key = _contains_forbidden_key(payload, S07_FINAL_PROSE_KEYS)
    if final_prose_key is not None:
        errors.append(issue("E_S07_NO_FINAL_PROSE", f"S07 surface control must not contain final-prose/manuscript field {final_prose_key!r}"))

    _validate_s07_input_coverage(payload, errors)
    rules = _validate_s07_claim_surface_rules(payload, errors)
    terms = _validate_s07_terminology_register(payload, errors)
    jobs = _validate_s07_internal_ids_and_paragraphs(payload, errors)
    _validate_s07_moves_and_language(payload, errors)
    _validate_s07_surface_and_forbidden(payload, errors)
    _validate_s07_coverage(payload, rules, terms, jobs, errors)
    _validate_s07_unresolved_handoff_audit(payload, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S07_SURFACE_CONTROL_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S07_SURFACE_CONTROL_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S07_SURFACE_CONTROL_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S07_SURFACE_CONTROL_REQUIRED", errors, allow_empty=True)


def _require_s08_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary_audit",
        "input_coverage_ledger",
        "source_data_inventory_projection",
        "normalized_claim_evidence_table",
        "visual_need_inventory",
        "formal_visual_need_map",
        "candidate_visual_object_queue",
        "visual_budget",
        "main_story_visual_path",
        "figure_contracts",
        "table_contracts",
        "formal_object_contracts",
        "panel_evidence_map",
        "visual_claim_evidence_map",
        "backend_route_map",
        "main_supplement_split_plan",
        "caption_legend_brief",
        "accessibility_and_style_constraints",
        "coverage_ledger",
        "unresolved_visual_object_report",
        "downstream_handoff",
        "visual_safety_audit",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S08_VISUAL_FORMAL_PLAN_REQUIRED", f"S08VisualFormalPlan missing required modules: {missing}"))


def _require_s08_mapping_list(
    payload: dict[str, Any] | None,
    field: str,
    key: str,
    required: list[str],
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    return _require_s05_mapping_list(payload, field, key, required, code, errors, allow_empty=allow_empty)


def _s08_string_items(value: Any) -> list[str]:
    if is_non_empty_string_list(value):
        assert isinstance(value, list)
        return [str(item) for item in value]
    if is_non_empty_string(value):
        return [part.strip() for part in str(value).replace(";", ",").split(",") if part.strip()]
    return []


def _material_ref_parts(ref: str) -> tuple[str, str]:
    material, sep, selector = ref.partition("#")
    return material, selector if sep else "payload"


def _material_selector_map(refs: Any) -> dict[str, set[str]]:
    selector_map: dict[str, set[str]] = {}
    for ref in _s08_string_items(refs):
        material, selector = _material_ref_parts(ref)
        selector_map.setdefault(material, set()).add(selector)
    return selector_map


def _require_s08_string_items(
    record: dict[str, Any],
    label: str,
    key: str,
    code: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool = False,
) -> set[str]:
    items = _s08_string_items(record.get(key))
    if not items and not allow_empty:
        errors.append(issue(code, f"{label}.{key} must be a non-empty string or list of strings"))
    return set(items)


def _s08_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _require_s08_count(container: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue]) -> int | None:
    if container is None:
        return None
    value = _s08_int(container.get(key))
    if value is None or value < 0:
        errors.append(issue(code, f"{field}.{key} must be a non-negative integer"))
    return value


def _validate_s08_authority_boundary(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    audit = _require_mapping(payload, "authority_boundary_audit", "E_S08_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "final_figures_generated",
        "final_captions_written",
        "new_claims_introduced",
        "claim_strength_modified",
        "submission_readiness_claimed",
    ):
        if audit is not None and audit.get(key) is not False:
            errors.append(issue("E_S08_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary_audit.{key} must be false"))
    if audit is not None and audit.get("controller_owned_completion") is not True:
        errors.append(issue("E_S08_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary_audit.controller_owned_completion must be true"))


def _validate_s08_input_coverage(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    ledger = _require_mapping(payload, "input_coverage_ledger", "E_S08_INPUT_COVERAGE_REQUIRED", errors)
    for key in (
        "s04_claim_capsules_read",
        "s04_evidence_boundaries_read",
        "s05_reader_spine_read",
        "s06_object_budget_read",
        "evidence_inventory_read",
        "source_data_inventory_read",
        "result_artifact_manifest_read",
        "terminology_register_read",
    ):
        if ledger is not None and ledger.get(key) is not True:
            errors.append(issue("E_S08_INPUT_COVERAGE_REQUIRED", f"input_coverage_ledger.{key} must be true"))
    _require_string_list(ledger, "input_coverage_ledger", "missing_inputs", "E_S08_INPUT_COVERAGE_REQUIRED", errors, allow_empty=True)
    _require_string_list(ledger, "input_coverage_ledger", "unresolved_inputs", "E_S08_INPUT_COVERAGE_REQUIRED", errors, allow_empty=True)
    _require_list_field(ledger, "input_coverage_ledger", "backflow_targets", "E_S08_INPUT_COVERAGE_REQUIRED", errors, allow_empty=True)


def _validate_s08_claims_needs_and_sources(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[set[str], set[str], set[str], set[str]]:
    claims = _require_s08_mapping_list(
        payload,
        "normalized_claim_evidence_table",
        "claims",
        [
            "claim_id",
            "admitted_claim",
            "support_strength",
            "evidence_refs",
            "result_artifacts",
            "allowed_interpretation",
            "forbidden_interpretation",
            "required_caveat",
            "visualizable",
            "visual_risk",
        ],
        "E_S08_CLAIM_EVIDENCE_TABLE_REQUIRED",
        errors,
    )
    claim_ids = _record_ids(claims, "claim_id")

    needs = _require_s08_mapping_list(
        payload,
        "visual_need_inventory",
        "needs",
        [
            "need_id",
            "reader_question",
            "reviewer_question",
            "target_section",
            "section_function",
            "why_visual_needed",
            "risk_if_text_only",
            "priority",
        ],
        "E_S08_VISUAL_NEED_REQUIRED",
        errors,
    )
    need_ids = _record_ids(needs, "need_id")
    for idx, need in enumerate(needs):
        related_claims = _require_s08_string_items(need, f"visual_need_inventory.needs[{idx}]", "related_claims", "E_S08_VISUAL_NEED_REQUIRED", errors)
        unknown = sorted(related_claims - claim_ids)
        if unknown:
            errors.append(issue("E_S08_NO_NEW_CLAIMS", f"visual_need_inventory.needs[{idx}].related_claims references unknown claims {unknown}"))
        _require_s08_string_items(need, f"visual_need_inventory.needs[{idx}]", "related_objects", "E_S08_VISUAL_NEED_REQUIRED", errors)

    formal_needs = _require_s08_mapping_list(
        payload,
        "formal_visual_need_map",
        "objects",
        [
            "object_or_variable_id",
            "object_name",
            "current_granularity",
            "required_granularity",
            "cognitive_load_risk",
            "explanation_ladder_level",
        ],
        "E_S08_FORMAL_VISUAL_NEED_REQUIRED",
        errors,
    )
    object_ids = _record_ids(formal_needs, "object_or_variable_id")
    for idx, record in enumerate(formal_needs):
        representations = _require_s08_string_items(record, f"formal_visual_need_map.objects[{idx}]", "suggested_representation", "E_S08_FORMAL_VISUAL_NEED_REQUIRED", errors)
        unknown = sorted(representations - S08_VISUAL_TYPES)
        if unknown:
            errors.append(issue("E_S08_FORMAL_VISUAL_NEED_REQUIRED", f"formal_visual_need_map.objects[{idx}].suggested_representation contains unsupported types {unknown}"))

    sources = _require_s08_mapping_list(
        payload,
        "source_data_inventory_projection",
        "artifacts",
        [
            "artifact_id",
            "source_data_path",
            "result_artifact_path",
            "script_path",
            "reproducibility_status",
            "risk",
        ],
        "E_S08_SOURCE_DATA_PROJECTION_REQUIRED",
        errors,
    )
    artifact_ids = _record_ids(sources, "artifact_id")
    for idx, record in enumerate(sources):
        _require_s08_string_items(record, f"source_data_inventory_projection.artifacts[{idx}]", "suitable_visual_types", "E_S08_SOURCE_DATA_PROJECTION_REQUIRED", errors)
        _require_s08_string_items(record, f"source_data_inventory_projection.artifacts[{idx}]", "missing_items", "E_S08_SOURCE_DATA_PROJECTION_REQUIRED", errors, allow_empty=True)

    return claim_ids, need_ids, object_ids, artifact_ids


def _validate_s08_candidates_budget_and_path(
    payload: dict[str, Any],
    need_ids: set[str],
    claim_ids: set[str],
    errors: list[ValidationIssue],
) -> tuple[list[dict[str, Any]], set[str]]:
    candidates = _require_s08_mapping_list(
        payload,
        "candidate_visual_object_queue",
        "candidates",
        [
            "visual_id",
            "visual_type",
            "candidate_title",
            "target_section",
            "role",
            "priority",
            "explanatory_or_evidential",
            "status",
            "reason",
        ],
        "E_S08_CANDIDATE_QUEUE_REQUIRED",
        errors,
    )
    candidate_ids = _record_ids(candidates, "visual_id")
    for idx, candidate in enumerate(candidates):
        if candidate.get("visual_type") not in S08_VISUAL_TYPES:
            errors.append(issue("E_S08_CANDIDATE_QUEUE_REQUIRED", f"candidate_visual_object_queue.candidates[{idx}].visual_type must be one of {sorted(S08_VISUAL_TYPES)}"))
        if candidate.get("status") not in S08_CANDIDATE_STATUSES:
            errors.append(issue("E_S08_CANDIDATE_QUEUE_REQUIRED", f"candidate_visual_object_queue.candidates[{idx}].status must be one of {sorted(S08_CANDIDATE_STATUSES)}"))
        if candidate.get("explanatory_or_evidential") not in S08_EXPLANATORY_EVIDENTIAL_ROLES:
            errors.append(issue("E_S08_EXPLANATORY_EVIDENTIAL_BOUNDARY", f"candidate_visual_object_queue.candidates[{idx}].explanatory_or_evidential must be one of {sorted(S08_EXPLANATORY_EVIDENTIAL_ROLES)}"))
        source_needs = _require_s08_string_items(candidate, f"candidate_visual_object_queue.candidates[{idx}]", "source_need_ids", "E_S08_CANDIDATE_QUEUE_REQUIRED", errors)
        unknown_needs = sorted(source_needs - need_ids)
        if unknown_needs:
            errors.append(issue("E_S08_CANDIDATE_QUEUE_REQUIRED", f"candidate_visual_object_queue.candidates[{idx}].source_need_ids references unknown needs {unknown_needs}"))

    budget = _require_mapping(payload, "visual_budget", "E_S08_VISUAL_BUDGET_REQUIRED", errors)
    _require_s08_count(budget, "visual_budget", "total_main_figures", "E_S08_VISUAL_BUDGET_REQUIRED", errors)
    _require_s08_count(budget, "visual_budget", "rejected_or_deferred_count", "E_S08_VISUAL_BUDGET_REQUIRED", errors)
    section_budget = _require_s05_list_records(
        budget,
        "visual_budget.section_level_budget",
        "section_level_budget",
        ["section", "required_visual_function", "cognitive_load_limit", "overload_risk"],
        "E_S08_VISUAL_BUDGET_REQUIRED",
        errors,
    )
    for idx, record in enumerate(section_budget):
        if _s08_int(record.get("max_visual_objects")) is None:
            errors.append(issue("E_S08_VISUAL_BUDGET_REQUIRED", f"visual_budget.section_level_budget[{idx}].max_visual_objects must be an integer"))
    if budget is not None and not is_non_empty_string(budget.get("supplement_capacity")):
        errors.append(issue("E_S08_VISUAL_BUDGET_REQUIRED", "visual_budget.supplement_capacity must be a non-empty string"))

    story = _require_s08_mapping_list(
        payload,
        "main_story_visual_path",
        "path",
        ["visual_id", "story_function", "reader_question_answered", "claim_supported", "dependency_on_previous_visual"],
        "E_S08_MAIN_STORY_PATH_REQUIRED",
        errors,
    )
    for idx, record in enumerate(story):
        if _s08_int(record.get("order")) is None:
            errors.append(issue("E_S08_MAIN_STORY_PATH_REQUIRED", f"main_story_visual_path.path[{idx}].order must be an integer"))
        visual_id = str(record.get("visual_id"))
        if visual_id not in candidate_ids:
            errors.append(issue("E_S08_MAIN_STORY_PATH_REQUIRED", f"main_story_visual_path.path[{idx}].visual_id references unknown visual {visual_id!r}"))
        claim_id = str(record.get("claim_supported"))
        if claim_id not in claim_ids:
            errors.append(issue("E_S08_NO_NEW_CLAIMS", f"main_story_visual_path.path[{idx}].claim_supported references unknown claim {claim_id!r}"))

    return candidates, candidate_ids


def _validate_s08_contracts(
    payload: dict[str, Any],
    claim_ids: set[str],
    need_ids: set[str],
    object_ids: set[str],
    candidate_ids: set[str],
    errors: list[ValidationIssue],
) -> tuple[set[str], set[str], set[str]]:
    figures = _require_s08_mapping_list(
        payload,
        "figure_contracts",
        "figures",
        [
            "visual_id",
            "visual_type",
            "proposed_title",
            "target_section",
            "main_or_supplement",
            "reader_question_answered",
            "section_function",
            "proof_role",
            "explanatory_or_evidential",
            "backend_route_ref",
            "caption_brief_ref",
            "cognitive_load_risk",
            "status",
        ],
        "E_S08_FIGURE_CONTRACT_REQUIRED",
        errors,
    )
    figure_ids = _record_ids(figures, "visual_id")
    panel_ids_required: set[str] = set()
    for idx, figure in enumerate(figures):
        label = f"figure_contracts.figures[{idx}]"
        visual_id = str(figure.get("visual_id"))
        if visual_id not in candidate_ids:
            errors.append(issue("E_S08_FIGURE_CONTRACT_REQUIRED", f"{label}.visual_id references unknown candidate {visual_id!r}"))
        if figure.get("visual_type") != "figure":
            errors.append(issue("E_S08_FIGURE_CONTRACT_REQUIRED", f"{label}.visual_type must be 'figure'"))
        if figure.get("explanatory_or_evidential") not in S08_EXPLANATORY_EVIDENTIAL_ROLES:
            errors.append(issue("E_S08_EXPLANATORY_EVIDENTIAL_BOUNDARY", f"{label}.explanatory_or_evidential must be one of {sorted(S08_EXPLANATORY_EVIDENTIAL_ROLES)}"))
        for key in ("supported_claims", "unsupported_claims", "source_s04_capsules", "required_panels", "required_data", "terminology_constraints", "accessibility_constraints"):
            items = _require_s08_string_items(figure, label, key, "E_S08_FIGURE_CONTRACT_REQUIRED", errors)
            if key in {"supported_claims", "unsupported_claims"}:
                unknown = sorted(items - claim_ids)
                if unknown:
                    errors.append(issue("E_S08_NO_NEW_CLAIMS", f"{label}.{key} references unknown claims {unknown}"))
            if key == "required_panels":
                panel_ids_required.update(items)

    tables = _require_s08_mapping_list(
        payload,
        "table_contracts",
        "tables",
        [
            "table_id",
            "table_type",
            "target_section",
            "reader_question_answered",
            "row_semantics",
            "column_semantics",
            "forbidden_interpretation",
            "main_or_supplement",
            "backend_route_ref",
            "status",
        ],
        "E_S08_TABLE_CONTRACT_REQUIRED",
        errors,
    )
    table_ids = _record_ids(tables, "table_id")
    for idx, table in enumerate(tables):
        label = f"table_contracts.tables[{idx}]"
        table_id = str(table.get("table_id"))
        if table_id not in candidate_ids:
            errors.append(issue("E_S08_TABLE_CONTRACT_REQUIRED", f"{label}.table_id references unknown candidate {table_id!r}"))
        for key in ("required_entries", "source_data", "supported_claims"):
            items = _require_s08_string_items(table, label, key, "E_S08_TABLE_CONTRACT_REQUIRED", errors)
            if key == "supported_claims":
                unknown = sorted(items - claim_ids)
                if unknown:
                    errors.append(issue("E_S08_NO_NEW_CLAIMS", f"{label}.supported_claims references unknown claims {unknown}"))

    formal_objects = _require_s08_mapping_list(
        payload,
        "formal_object_contracts",
        "formal_objects",
        [
            "formal_id",
            "formal_type",
            "target_section",
            "purpose",
            "reader_question_answered",
            "forbidden_interpretation",
            "backend_or_source_route",
            "cognitive_load_risk",
            "status",
        ],
        "E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED",
        errors,
    )
    formal_ids = _record_ids(formal_objects, "formal_id")
    for idx, formal in enumerate(formal_objects):
        label = f"formal_object_contracts.formal_objects[{idx}]"
        formal_id = str(formal.get("formal_id"))
        if formal_id not in candidate_ids:
            errors.append(issue("E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED", f"{label}.formal_id references unknown candidate {formal_id!r}"))
        if formal.get("formal_type") not in S08_FORMAL_TYPES:
            errors.append(issue("E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED", f"{label}.formal_type must be one of {sorted(S08_FORMAL_TYPES)}"))
        refs = _require_s08_string_items(formal, label, "object_or_variable_refs", "E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED", errors)
        unknown_refs = sorted(refs - object_ids)
        if unknown_refs:
            errors.append(issue("E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED", f"{label}.object_or_variable_refs references unknown S06 objects/variables {unknown_refs}"))
        claims = _require_s08_string_items(formal, label, "supported_claims", "E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED", errors)
        unknown_claims = sorted(claims - claim_ids)
        if unknown_claims:
            errors.append(issue("E_S08_NO_NEW_CLAIMS", f"{label}.supported_claims references unknown claims {unknown_claims}"))
        for key in ("notation_requirements", "required_definitions_before_use"):
            _require_s08_string_items(formal, label, key, "E_S08_FORMAL_OBJECT_CONTRACT_REQUIRED", errors)

    return figure_ids | table_ids | formal_ids, figure_ids, panel_ids_required


def _validate_s08_evidence_routes_and_boundaries(
    payload: dict[str, Any],
    claim_ids: set[str],
    contract_ids: set[str],
    figure_ids: set[str],
    required_panel_ids: set[str],
    errors: list[ValidationIssue],
) -> None:
    panels = _require_s08_mapping_list(
        payload,
        "panel_evidence_map",
        "panels",
        [
            "visual_id",
            "panel_id",
            "panel_role",
            "visual_encoding",
            "source_data",
            "evidence_ref",
            "supported_claim",
            "forbidden_claim",
            "required_axis_or_label",
            "required_caveat",
        ],
        "E_S08_PANEL_EVIDENCE_MAP_REQUIRED",
        errors,
    )
    panel_ids = _record_ids(panels, "panel_id")
    missing_panels = sorted(required_panel_ids - panel_ids)
    if missing_panels:
        errors.append(issue("E_S08_PANEL_EVIDENCE_MAP_REQUIRED", f"panel_evidence_map missing required panels {missing_panels}"))
    for idx, panel in enumerate(panels):
        label = f"panel_evidence_map.panels[{idx}]"
        visual_id = str(panel.get("visual_id"))
        if visual_id not in figure_ids:
            errors.append(issue("E_S08_PANEL_EVIDENCE_MAP_REQUIRED", f"{label}.visual_id references unknown figure {visual_id!r}"))
        for key in ("supported_claim", "forbidden_claim"):
            claim_id = str(panel.get(key))
            if claim_id not in claim_ids:
                errors.append(issue("E_S08_NO_NEW_CLAIMS", f"{label}.{key} references unknown claim {claim_id!r}"))
        role_text = f"{panel.get('panel_role', '')} {panel.get('visual_encoding', '')}".lower()
        if "schematic" in role_text and any(term in role_text for term in ("empirical", "evidential", "result proof")):
            errors.append(issue("E_S08_EXPLANATORY_EVIDENTIAL_BOUNDARY", f"{label} treats a schematic as empirical evidence"))

    bindings = _require_s08_mapping_list(
        payload,
        "visual_claim_evidence_map",
        "bindings",
        [
            "visual_id",
            "claim_id",
            "source_s04_capsule",
            "evidence_ref",
            "result_artifact",
            "source_data",
            "support_strength",
            "allowed_interpretation",
            "forbidden_interpretation",
            "required_caveat",
        ],
        "E_S08_VISUAL_CLAIM_BINDING_REQUIRED",
        errors,
    )
    for idx, binding in enumerate(bindings):
        label = f"visual_claim_evidence_map.bindings[{idx}]"
        visual_id = str(binding.get("visual_id"))
        if visual_id not in contract_ids:
            errors.append(issue("E_S08_VISUAL_CLAIM_BINDING_REQUIRED", f"{label}.visual_id references unknown contract {visual_id!r}"))
        claim_id = str(binding.get("claim_id"))
        if claim_id not in claim_ids:
            errors.append(issue("E_S08_NO_NEW_CLAIMS", f"{label}.claim_id references unknown claim {claim_id!r}"))

    routes = _require_s08_mapping_list(
        payload,
        "backend_route_map",
        "routes",
        [
            "visual_id",
            "source_data_path",
            "script_path",
            "manual_design_needed",
            "generation_tool",
            "reproducibility_status",
            "dependency_risk",
        ],
        "E_S08_BACKEND_ROUTE_REQUIRED",
        errors,
    )
    route_ids = _record_ids(routes, "visual_id")
    missing_routes = sorted(contract_ids - route_ids)
    if missing_routes:
        errors.append(issue("E_S08_BACKEND_ROUTE_REQUIRED", f"backend_route_map missing paper-facing routes {missing_routes}"))
    for idx, route in enumerate(routes):
        label = f"backend_route_map.routes[{idx}]"
        _require_s08_string_items(route, label, "missing_backend_items", "E_S08_BACKEND_ROUTE_REQUIRED", errors, allow_empty=True)
        _require_s08_string_items(route, label, "export_targets", "E_S08_BACKEND_ROUTE_REQUIRED", errors)

    placements = _require_s08_mapping_list(
        payload,
        "main_supplement_split_plan",
        "placements",
        ["visual_id", "placement", "reason", "reader_importance", "claim_importance", "evidence_strength", "cognitive_load_impact", "section_budget_fit"],
        "E_S08_MAIN_SUPPLEMENT_SPLIT_REQUIRED",
        errors,
    )
    placement_ids = _record_ids(placements, "visual_id")
    missing_placements = sorted(contract_ids - placement_ids)
    if missing_placements:
        errors.append(issue("E_S08_MAIN_SUPPLEMENT_SPLIT_REQUIRED", f"main_supplement_split_plan missing contract placements {missing_placements}"))
    for idx, placement in enumerate(placements):
        if placement.get("placement") not in S08_PLACEMENTS:
            errors.append(issue("E_S08_MAIN_SUPPLEMENT_SPLIT_REQUIRED", f"main_supplement_split_plan.placements[{idx}].placement must be one of {sorted(S08_PLACEMENTS)}"))

    captions = _require_s08_mapping_list(
        payload,
        "caption_legend_brief",
        "briefs",
        ["visual_id", "caption_job", "must_mention", "must_not_claim", "required_caveat", "terminology_constraints", "panel_label_policy", "citation_or_data_note"],
        "E_S08_CAPTION_BOUNDARY_REQUIRED",
        errors,
    )
    caption_ids = _record_ids(captions, "visual_id")
    missing_captions = sorted(contract_ids - caption_ids)
    if missing_captions:
        errors.append(issue("E_S08_CAPTION_BOUNDARY_REQUIRED", f"caption_legend_brief missing contract briefs {missing_captions}"))

    accessibility = _require_s08_mapping_list(
        payload,
        "accessibility_and_style_constraints",
        "objects",
        [
            "visual_id",
            "color_policy",
            "colorblind_safe_required",
            "minimum_label_size",
            "axis_label_requirements",
            "legend_policy",
            "panel_label_policy",
            "vector_or_raster_policy",
            "journal_style_constraints",
            "readability_risk",
        ],
        "E_S08_ACCESSIBILITY_REQUIRED",
        errors,
    )
    accessibility_ids = _record_ids(accessibility, "visual_id")
    missing_accessibility = sorted(contract_ids - accessibility_ids)
    if missing_accessibility:
        errors.append(issue("E_S08_ACCESSIBILITY_REQUIRED", f"accessibility_and_style_constraints missing contract constraints {missing_accessibility}"))


def _validate_s08_coverage_handoff_and_audit(
    payload: dict[str, Any],
    candidates: list[dict[str, Any]],
    contract_ids: set[str],
    figure_ids: set[str],
    errors: list[ValidationIssue],
) -> None:
    coverage = _require_mapping(payload, "coverage_ledger", "E_S08_COVERAGE_LEDGER_REQUIRED", errors)
    count_keys = (
        "total_reader_questions",
        "reader_questions_requiring_visuals",
        "visual_needs_detected",
        "visual_needs_covered",
        "visual_needs_unresolved",
        "candidate_visuals_generated",
        "visuals_kept",
        "visuals_merged",
        "visuals_supplement",
        "visuals_deferred",
        "visuals_rejected",
        "figures_with_contract",
        "tables_with_contract",
        "formal_objects_with_contract",
        "panels_with_evidence_map",
        "visuals_with_backend_route",
        "visuals_with_caption_brief",
    )
    counts = {key: _require_s08_count(coverage, "coverage_ledger", key, "E_S08_COVERAGE_LEDGER_REQUIRED", errors) for key in count_keys}
    _require_string_list(coverage, "coverage_ledger", "unresolved_items", "E_S08_COVERAGE_LEDGER_REQUIRED", errors, allow_empty=True)
    if coverage is not None:
        if counts.get("candidate_visuals_generated") != len(candidates):
            errors.append(issue("E_S08_COVERAGE_LEDGER_REQUIRED", "coverage_ledger.candidate_visuals_generated must match candidate queue length"))
        if counts.get("figures_with_contract") != len(figure_ids):
            errors.append(issue("E_S08_COVERAGE_LEDGER_REQUIRED", "coverage_ledger.figures_with_contract must match figure contract count"))
        table_formal_count = len(contract_ids - figure_ids)
        tables_with_contract = counts.get("tables_with_contract")
        formal_objects_with_contract = counts.get("formal_objects_with_contract")
        if tables_with_contract is not None and formal_objects_with_contract is not None:
            if tables_with_contract + formal_objects_with_contract != table_formal_count:
                errors.append(issue("E_S08_COVERAGE_LEDGER_REQUIRED", "coverage_ledger table/formal counts must match non-figure contracts"))
        visuals_with_backend_route = counts.get("visuals_with_backend_route")
        if visuals_with_backend_route is not None and visuals_with_backend_route < len(contract_ids):
            errors.append(issue("E_S08_BACKEND_ROUTE_REQUIRED", "coverage_ledger.visuals_with_backend_route must cover every paper-facing contract"))
        visuals_with_caption_brief = counts.get("visuals_with_caption_brief")
        if visuals_with_caption_brief is not None and visuals_with_caption_brief < len(contract_ids):
            errors.append(issue("E_S08_CAPTION_BOUNDARY_REQUIRED", "coverage_ledger.visuals_with_caption_brief must cover every paper-facing contract"))
        if counts.get("visual_needs_unresolved") not in (None, 0) or coverage.get("unresolved_items"):
            errors.append(issue("E_S08_UNRESOLVED_VISUAL_OBJECT_REQUIRED", "coverage_ledger unresolved items must be empty or routed before S08 completion"))

    unresolved = _require_mapping(payload, "unresolved_visual_object_report", "E_S08_UNRESOLVED_VISUAL_OBJECT_REQUIRED", errors)
    _require_list_field(unresolved, "unresolved_visual_object_report", "items", "E_S08_UNRESOLVED_VISUAL_OBJECT_REQUIRED", errors, allow_empty=True)
    _require_string_list(unresolved, "unresolved_visual_object_report", "backflow_targets", "E_S08_UNRESOLVED_VISUAL_OBJECT_REQUIRED", errors, allow_empty=True)

    handoff = _require_mapping(payload, "downstream_handoff", "E_S08_DOWNSTREAM_HANDOFF_REQUIRED", errors)
    if handoff is not None:
        missing = sorted(stage for stage in S08_REQUIRED_HANDOFFS if not isinstance(handoff.get(stage), dict))
        if missing:
            errors.append(issue("E_S08_DOWNSTREAM_HANDOFF_REQUIRED", f"downstream_handoff missing stages {missing}"))
        for stage in sorted(S08_REQUIRED_HANDOFFS):
            stage_handoff = as_mapping(handoff.get(stage))
            if stage_handoff is None:
                continue
            _require_mapping_fields(stage_handoff, f"downstream_handoff.{stage}", ["handoff_summary", "allowed_use", "misuse_warning"], "E_S08_DOWNSTREAM_HANDOFF_REQUIRED", errors)
            _require_list_field(stage_handoff, f"downstream_handoff.{stage}", "items", "E_S08_DOWNSTREAM_HANDOFF_REQUIRED", errors, allow_empty=False)

    audit = _require_mapping(payload, "visual_safety_audit", "E_S08_VISUAL_SAFETY_AUDIT_REQUIRED", errors)
    for key in (
        "no_new_claims",
        "no_claim_strengthening",
        "no_final_figures",
        "no_final_captions",
        "no_schematic_as_empirical_evidence",
        "no_decorative_visuals",
        "no_missing_backend_routes",
        "no_completion_overclaim",
    ):
        if audit is not None and audit.get(key) is not True:
            errors.append(issue("E_S08_VISUAL_SAFETY_AUDIT_REQUIRED", f"visual_safety_audit.{key} must be true"))
    _require_string_list(audit, "visual_safety_audit", "remaining_risks", "E_S08_VISUAL_SAFETY_AUDIT_REQUIRED", errors, allow_empty=True)


def _validate_s08_visual_formal_plan(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s08_payload_header(payload, "ppg-s08-visual-formal-plan/v0.1", "E_S08_VISUAL_FORMAL_PLAN_REQUIRED", errors)
    _require_s08_required_modules(payload, errors)
    if payload.get("completion_boundary") != S08_COMPLETION_BOUNDARY:
        errors.append(issue("E_S08_COMPLETION_BOUNDARY", f"completion_boundary must be {S08_COMPLETION_BOUNDARY!r}"))
    completion_overclaim_key = _contains_forbidden_key(payload, S08_COMPLETION_OVERCLAIM_KEYS)
    if completion_overclaim_key is not None:
        errors.append(issue("E_S08_NO_COMPLETION_OVERCLAIM", f"S08 visual/formal plan must not contain completion field {completion_overclaim_key!r}"))
    final_artifact_key = _contains_forbidden_key(payload, S08_FINAL_ARTIFACT_KEYS)
    if final_artifact_key is not None:
        errors.append(issue("E_S08_NO_FINAL_ARTIFACT", f"S08 visual/formal plan must not contain final figure/caption/export field {final_artifact_key!r}"))

    _validate_s08_authority_boundary(payload, errors)
    _validate_s08_input_coverage(payload, errors)
    claim_ids, need_ids, object_ids, _artifact_ids = _validate_s08_claims_needs_and_sources(payload, errors)
    candidates, candidate_ids = _validate_s08_candidates_budget_and_path(payload, need_ids, claim_ids, errors)
    contract_ids, figure_ids, required_panel_ids = _validate_s08_contracts(payload, claim_ids, need_ids, object_ids, candidate_ids, errors)
    _validate_s08_evidence_routes_and_boundaries(payload, claim_ids, contract_ids, figure_ids, required_panel_ids, errors)
    _validate_s08_coverage_handoff_and_audit(payload, candidates, contract_ids, figure_ids, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S08_VISUAL_FORMAL_PLAN_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S08_VISUAL_FORMAL_PLAN_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S08_VISUAL_FORMAL_PLAN_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S08_VISUAL_FORMAL_PLAN_REQUIRED", errors, allow_empty=True)


def _require_s09a_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary_audit",
        "target_unit_profile",
        "hard_constraints",
        "local_context",
        "adjacent_context",
        "global_orientation",
        "claim_control_bundle",
        "reader_context_bundle",
        "object_context_bundle",
        "surface_control_bundle",
        "visual_formal_control_bundle",
        "evidence_anchor_bundle",
        "negative_control_bundle",
        "conflict_resolution_log",
        "control_priority_map",
        "context_usage_instructions",
        "excluded_or_deferred_controls",
        "freshness_check",
        "missing_control_report",
        "coverage_ledger",
        "downstream_packet_requirements",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S09A_RICH_CONTROL_BUNDLE_REQUIRED", f"S09ARichControlBundle missing required modules: {missing}"))


def _require_s09b_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "packet_identity",
        "target_unit",
        "selected_control_bundle_ref",
        "control_digest",
        "control_digest_policy",
        "global_material_coverage",
        "unit_material_closure",
        "material_access_manifest",
        "material_read_obligations",
        "deferred_control_ledger",
        "section_specific_blockers",
        "task_mission",
        "allowed_read_paths",
        "allowed_write_paths",
        "forbidden_routes",
        "worker_boot_clause",
        "section_or_unit_move_plan",
        "claim_boundary_controls",
        "reader_spine_controls",
        "object_granularity_controls",
        "terminology_surface_controls",
        "visual_formal_controls",
        "negative_controls",
        "context_usage_instructions",
        "validators",
        "return_format",
        "single_writer_lock",
        "stale_material_policy",
        "missing_material_report",
        "packet_authority_boundary",
        "emitted_task_packet",
        "candidate_return",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S09B_TASK_PACKET_ASSEMBLY_REQUIRED", f"S09BTaskPacketAssembly missing required modules: {missing}"))


def _s09_path_is_safe(path: str) -> bool:
    if not is_non_empty_string(path) or path.strip() != path:
        return False
    if path.startswith("/") or path.startswith("~") or "\\" in path or ".." in path.split("/"):
        return False
    if path in {"", ".", "examples", "runs", "scripts", "schemas"}:
        return False
    return "." in path.rsplit("/", 1)[-1]


def _require_s09_list(container: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue], *, allow_empty: bool = False) -> set[str]:
    if container is None:
        return set()
    items = _s08_string_items(container.get(key))
    if not items and not allow_empty:
        errors.append(issue(code, f"{field}.{key} must be a non-empty string or list of strings"))
    return set(items)


def _validate_s09_authority_audit(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    audit = _require_mapping(payload, "authority_boundary_audit", "E_S09A_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "final_prose_generated",
        "final_figures_generated",
        "task_packet_compiled",
        "new_claims_introduced",
        "claim_strength_modified",
    ):
        if audit is not None and audit.get(key) is not False:
            errors.append(issue("E_S09A_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary_audit.{key} must be false"))
    if audit is not None and audit.get("controller_owned_completion") is not True:
        errors.append(issue("E_S09A_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary_audit.controller_owned_completion must be true"))


def _validate_s09a_target_and_constraints(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    target = _require_mapping(payload, "target_unit_profile", "E_S09A_TARGET_UNIT_REQUIRED", errors)
    _require_mapping_fields(
        target,
        "target_unit_profile",
        ["target_unit_id", "target_unit_type", "target_artifact", "target_write_path_candidate", "stage_target", "unit_purpose", "expected_output_kind"],
        "E_S09A_TARGET_UNIT_REQUIRED",
        errors,
    )
    if target is not None:
        if target.get("target_unit_type") not in S09A_TARGET_UNIT_TYPES:
            errors.append(issue("E_S09A_TARGET_UNIT_REQUIRED", f"target_unit_profile.target_unit_type must be one of {sorted(S09A_TARGET_UNIT_TYPES)}"))
        if target.get("stage_target") not in S09_TARGET_STAGES:
            errors.append(issue("E_S09A_TARGET_UNIT_REQUIRED", f"target_unit_profile.stage_target must be one of {sorted(S09_TARGET_STAGES)}"))
        _require_s09_list(target, "target_unit_profile", "upstream_dependencies", "E_S09A_TARGET_UNIT_REQUIRED", errors)
        _require_s09_list(target, "target_unit_profile", "downstream_consumers", "E_S09A_TARGET_UNIT_REQUIRED", errors)

    hard = _require_mapping(payload, "hard_constraints", "E_S09A_HARD_CONSTRAINTS_REQUIRED", errors)
    _require_mapping_fields(hard, "hard_constraints", ["owner_intent_boundary"], "E_S09A_HARD_CONSTRAINTS_REQUIRED", errors)
    for key in ("admitted_claims", "forbidden_claims", "allowed_wording", "forbidden_wording", "required_caveats", "evidence_anchors", "result_package_boundaries"):
        _require_s09_list(hard, "hard_constraints", key, "E_S09A_HARD_CONSTRAINTS_REQUIRED", errors)
    for key in ("no_new_claims", "no_claim_strengthening", "no_internal_id_leakage", "completion_forbidden_required", "no_recursive_orchestration_required"):
        if hard is not None and hard.get(key) is not True:
            errors.append(issue("E_S09A_HARD_CONSTRAINTS_REQUIRED", f"hard_constraints.{key} must be true"))


def _validate_s09a_context_layers(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    local = _require_mapping(payload, "local_context", "E_S09A_RICH_CONTEXT_REQUIRED", errors)
    _require_mapping_fields(local, "local_context", ["reader_question", "paragraph_or_unit_job", "section_function", "object_granularity"], "E_S09A_RICH_CONTEXT_REQUIRED", errors)
    for key in ("required_claims", "required_evidence", "required_objects", "rhetorical_moves", "visual_callouts", "required_caveats", "target_unit_success_criteria"):
        _require_s09_list(local, "local_context", key, "E_S09A_RICH_CONTEXT_REQUIRED", errors)

    adjacent = _require_mapping(payload, "adjacent_context", "E_S09A_RICH_CONTEXT_REQUIRED", errors)
    _require_mapping_fields(
        adjacent,
        "adjacent_context",
        ["previous_unit_summary", "next_unit_expectation", "previous_reader_question", "next_reader_question", "continuity_notes"],
        "E_S09A_RICH_CONTEXT_REQUIRED",
        errors,
    )
    for key in ("prior_definitions", "later_payoff_targets", "do_not_preempt", "repetition_risks"):
        _require_s09_list(adjacent, "adjacent_context", key, "E_S09A_RICH_CONTEXT_REQUIRED", errors)

    global_orientation = _require_mapping(payload, "global_orientation", "E_S09A_RICH_CONTEXT_REQUIRED", errors)
    _require_mapping_fields(
        global_orientation,
        "global_orientation",
        [
            "paper_spine_summary",
            "contribution_bundle_summary",
            "global_claim_boundary",
            "terminology_policy",
            "visual_story_path",
            "article_type_or_venue_profile",
            "style_profile",
            "flexibility_guard",
        ],
        "E_S09A_RICH_CONTEXT_REQUIRED",
        errors,
    )
    if global_orientation is not None and global_orientation.get("use_as_background_only") is not True:
        errors.append(issue("E_S09A_CONTEXT_USAGE_REQUIRED", "global_orientation.use_as_background_only must be true"))


def _validate_s09a_control_bundles(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    claim = _require_mapping(payload, "claim_control_bundle", "E_S09A_CLAIM_CONTROL_REQUIRED", errors)
    for key in ("primary_claim_capsules", "adjacent_claim_capsules", "forbidden_claims", "rejected_claims", "unsupported_claim_risks", "allowed_wording", "forbidden_wording", "required_caveats", "evidence_anchor_refs", "overclaim_risks"):
        _require_s09_list(claim, "claim_control_bundle", key, "E_S09A_CLAIM_CONTROL_REQUIRED", errors)

    reader = _require_mapping(payload, "reader_context_bundle", "E_S09A_READER_CONTEXT_REQUIRED", errors)
    _require_mapping_fields(reader, "reader_context_bundle", ["current_reader_question", "previous_reader_question", "next_reader_question", "reviewer_question_if_any", "section_function", "argument_dependency", "front_half_promise_or_payoff", "removal_risk"], "E_S09A_READER_CONTEXT_REQUIRED", errors)

    obj = _require_mapping(payload, "object_context_bundle", "E_S09A_OBJECT_CONTEXT_REQUIRED", errors)
    for key in ("relevant_object_cards", "relevant_variable_cards", "granularity_for_target_unit", "forbidden_detail_level", "explanation_ladder", "cognitive_load_notes", "repetition_risk", "terminology_drift_risk"):
        _require_s09_list(obj, "object_context_bundle", key, "E_S09A_OBJECT_CONTEXT_REQUIRED", errors)

    surface = _require_mapping(payload, "surface_control_bundle", "E_S09A_SURFACE_CONTROL_REQUIRED", errors)
    for key in ("claim_surface_rules", "terminology_rules", "internal_id_ban_list", "forbidden_expression_list", "rhetorical_move_variants", "flexible_language_control", "anti_template_guard"):
        _require_s09_list(surface, "surface_control_bundle", key, "E_S09A_SURFACE_CONTROL_REQUIRED", errors)

    visual = _require_mapping(payload, "visual_formal_control_bundle", "E_S09A_VISUAL_CONTROL_REQUIRED", errors)
    if visual is not None and visual.get("applicable") is True:
        for key in ("figure_contracts", "table_contracts", "formal_object_contracts", "panel_evidence_map", "visual_claim_evidence_map", "backend_route_map", "caption_legend_brief", "callout_rules", "unsupported_visual_interpretations"):
            _require_s09_list(visual, "visual_formal_control_bundle", key, "E_S09A_VISUAL_CONTROL_REQUIRED", errors)

    evidence = _require_mapping(payload, "evidence_anchor_bundle", "E_S09A_EVIDENCE_ANCHOR_REQUIRED", errors)
    for key in ("required_evidence_refs", "citation_refs", "result_artifact_refs", "source_data_refs", "visibility_status"):
        _require_s09_list(evidence, "evidence_anchor_bundle", key, "E_S09A_EVIDENCE_ANCHOR_REQUIRED", errors)
    _require_s09_list(evidence, "evidence_anchor_bundle", "missing_or_stale_evidence", "E_S09A_EVIDENCE_ANCHOR_REQUIRED", errors, allow_empty=True)

    negative = _require_mapping(payload, "negative_control_bundle", "E_S09A_NEGATIVE_CONTROLS_REQUIRED", errors)
    for key in ("do_not_claim", "do_not_use_terms", "do_not_reference_internal_ids", "do_not_explain_yet", "do_not_repeat", "do_not_move_to_this_unit", "do_not_use_as_evidence", "do_not_turn_background_into_claim"):
        _require_s09_list(negative, "negative_control_bundle", key, "E_S09A_NEGATIVE_CONTROLS_REQUIRED", errors)


def _validate_s09a_resolution_coverage_and_handoff(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    conflicts = _require_s08_mapping_list(
        payload,
        "conflict_resolution_log",
        "conflicts",
        ["conflict_id", "conflict_type", "involved_controls", "resolution", "priority_rule_used", "worker_instruction", "backflow_target_if_unresolved"],
        "E_S09A_CONFLICT_RESOLUTION_REQUIRED",
        errors,
    )
    if not conflicts:
        errors.append(issue("E_S09A_CONFLICT_RESOLUTION_REQUIRED", "conflict_resolution_log.conflicts must record at least one resolved priority rule"))

    priority = _require_mapping(payload, "control_priority_map", "E_S09A_PRIORITY_MAP_REQUIRED", errors)
    order = _require_s09_list(priority, "control_priority_map", "priority_order", "E_S09A_PRIORITY_MAP_REQUIRED", errors)
    if not {"owner_intent", "S04_claim_boundary", "S04_evidence_boundary"} <= order:
        errors.append(issue("E_S09A_PRIORITY_MAP_REQUIRED", "control_priority_map.priority_order must include owner_intent, S04_claim_boundary, and S04_evidence_boundary"))
    _require_mapping_fields(priority, "control_priority_map", ["principle"], "E_S09A_PRIORITY_MAP_REQUIRED", errors)

    usage = _require_mapping(payload, "context_usage_instructions", "E_S09A_CONTEXT_USAGE_REQUIRED", errors)
    for key in ("must_obey", "use_as_local_context", "use_as_adjacent_context", "use_as_background_only", "do_not_quote", "do_not_turn_into_claim", "do_not_expand_scope", "do_not_include_in_output"):
        _require_s09_list(usage, "context_usage_instructions", key, "E_S09A_CONTEXT_USAGE_REQUIRED", errors)

    excluded = _require_s08_mapping_list(
        payload,
        "excluded_or_deferred_controls",
        "controls",
        ["control_ref", "reason", "risk_if_included", "maybe_needed_for", "downstream_or_backflow_target"],
        "E_S09A_EXCLUDED_CONTROLS_REQUIRED",
        errors,
    )
    if not excluded:
        errors.append(issue("E_S09A_EXCLUDED_CONTROLS_REQUIRED", "excluded_or_deferred_controls.controls must record at least one excluded/deferred control"))

    freshness = _require_mapping(payload, "freshness_check", "E_S09A_FRESHNESS_CHECK_REQUIRED", errors)
    for key in ("upstream_material_versions", "stale_materials", "affected_downstream_packets"):
        _require_s09_list(freshness, "freshness_check", key, "E_S09A_FRESHNESS_CHECK_REQUIRED", errors, allow_empty=key != "upstream_material_versions")
    if freshness is not None:
        if freshness.get("requires_reselection") is not False:
            errors.append(issue("E_S09A_FRESHNESS_CHECK_REQUIRED", "freshness_check.requires_reselection must be false for a ready bundle"))
        if freshness.get("requires_s09b_recompile") is not True:
            errors.append(issue("E_S09A_FRESHNESS_CHECK_REQUIRED", "freshness_check.requires_s09b_recompile must be true"))

    missing = _require_mapping(payload, "missing_control_report", "E_S09A_MISSING_CONTROL_REPORT_REQUIRED", errors)
    _require_list_field(missing, "missing_control_report", "items", "E_S09A_MISSING_CONTROL_REPORT_REQUIRED", errors, allow_empty=True)
    _require_s09_list(missing, "missing_control_report", "backflow_targets", "E_S09A_MISSING_CONTROL_REPORT_REQUIRED", errors, allow_empty=True)
    if missing is not None and missing.get("blocks_s09b") is not False:
        errors.append(issue("E_S09A_MISSING_CONTROL_REPORT_REQUIRED", "missing_control_report.blocks_s09b must be false for a ready bundle"))

    coverage = _require_mapping(payload, "coverage_ledger", "E_S09A_COVERAGE_LEDGER_REQUIRED", errors)
    for key in (
        "target_unit_controls_required",
        "hard_constraints_selected",
        "local_context_items_selected",
        "adjacent_context_items_selected",
        "claim_controls_selected",
        "object_controls_selected",
        "surface_controls_selected",
        "visual_controls_selected",
        "evidence_anchors_selected",
    ):
        value = _require_s08_count(coverage, "coverage_ledger", key, "E_S09A_COVERAGE_LEDGER_REQUIRED", errors)
        if value is not None and key != "visual_controls_selected" and value <= 0:
            errors.append(issue("E_S09A_COVERAGE_LEDGER_REQUIRED", f"coverage_ledger.{key} must be positive"))
    _require_s09_list(coverage, "coverage_ledger", "missing_controls", "E_S09A_COVERAGE_LEDGER_REQUIRED", errors, allow_empty=True)
    _require_s09_list(coverage, "coverage_ledger", "excluded_controls", "E_S09A_COVERAGE_LEDGER_REQUIRED", errors)
    _require_s09_list(coverage, "coverage_ledger", "unresolved_conflicts", "E_S09A_COVERAGE_LEDGER_REQUIRED", errors, allow_empty=True)
    if coverage is not None and (coverage.get("missing_controls") or coverage.get("unresolved_conflicts")):
        errors.append(issue("E_S09A_MISSING_CONTROL_REPORT_REQUIRED", "coverage_ledger missing controls or unresolved conflicts must be empty before S09B compilation"))

    downstream = _require_mapping(payload, "downstream_packet_requirements", "E_S09A_DOWNSTREAM_PACKET_REQUIREMENTS_REQUIRED", errors)
    _require_mapping_fields(downstream, "downstream_packet_requirements", ["target_stage", "expected_task_kind", "allowed_write_path_target", "required_worker_boot_clause"], "E_S09A_DOWNSTREAM_PACKET_REQUIREMENTS_REQUIRED", errors)
    for key in ("required_packet_fields", "required_validators", "required_return_format", "allowed_read_path_sources"):
        _require_s09_list(downstream, "downstream_packet_requirements", key, "E_S09A_DOWNSTREAM_PACKET_REQUIREMENTS_REQUIRED", errors)
    if downstream is not None:
        if downstream.get("target_stage") not in S09_TARGET_STAGES:
            errors.append(issue("E_S09A_DOWNSTREAM_PACKET_REQUIREMENTS_REQUIRED", f"downstream_packet_requirements.target_stage must be one of {sorted(S09_TARGET_STAGES)}"))
        for key in ("single_writer_lock_required", "completion_forbidden_required", "no_recursive_orchestration_required"):
            if downstream.get(key) is not True:
                errors.append(issue("E_S09A_DOWNSTREAM_PACKET_REQUIREMENTS_REQUIRED", f"downstream_packet_requirements.{key} must be true"))


def _validate_s09a_rich_control_bundle(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s09a_payload_header(payload, "ppg-s09a-rich-control-selection/v0.1", "E_S09A_RICH_CONTROL_BUNDLE_REQUIRED", errors)
    _require_s09a_required_modules(payload, errors)
    if payload.get("completion_boundary") != S09A_COMPLETION_BOUNDARY:
        errors.append(issue("E_S09A_COMPLETION_BOUNDARY", f"completion_boundary must be {S09A_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S09_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S09A_NO_COMPLETION_OVERCLAIM", f"S09A rich control bundle must not contain completion field {completion_key!r}"))
    final_key = _contains_forbidden_key(payload, S09_FINAL_CONTENT_KEYS)
    if final_key is not None:
        errors.append(issue("E_S09A_NO_FINAL_CONTENT", f"S09A rich control bundle must not contain final content field {final_key!r}"))

    _validate_s09_authority_audit(payload, errors)
    _validate_s09a_target_and_constraints(payload, errors)
    _validate_s09a_context_layers(payload, errors)
    _validate_s09a_control_bundles(payload, errors)
    _validate_s09a_resolution_coverage_and_handoff(payload, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S09A_RICH_CONTROL_BUNDLE_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S09A_RICH_CONTROL_BUNDLE_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S09A_RICH_CONTROL_BUNDLE_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S09A_RICH_CONTROL_BUNDLE_REQUIRED", errors, allow_empty=True)


def _validate_s09b_identity_paths_and_authority(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    identity = _require_mapping(payload, "packet_identity", "E_S09B_PACKET_IDENTITY_REQUIRED", errors)
    _require_mapping_fields(identity, "packet_identity", ["packet_id", "schema_version", "target_stage", "task_kind", "source_s09a_bundle", "generated_by", "generated_at"], "E_S09B_PACKET_IDENTITY_REQUIRED", errors)
    if identity is not None:
        if identity.get("target_stage") not in S09_TARGET_STAGES:
            errors.append(issue("E_S09B_PACKET_IDENTITY_REQUIRED", f"packet_identity.target_stage must be one of {sorted(S09_TARGET_STAGES)}"))
        if identity.get("generated_by") != "S09B":
            errors.append(issue("E_S09B_PACKET_IDENTITY_REQUIRED", "packet_identity.generated_by must be S09B"))

    target = _require_mapping(payload, "target_unit", "E_S09B_TARGET_UNIT_REQUIRED", errors)
    _require_mapping_fields(target, "target_unit", ["unit_id", "unit_type", "target_artifact", "allowed_write_path", "expected_output_schema", "output_artifact_path"], "E_S09B_TARGET_UNIT_REQUIRED", errors)

    read_paths = _s08_string_items(payload.get("allowed_read_paths"))
    if not read_paths:
        errors.append(issue("E_S09B_ALLOWED_READ_PATHS_REQUIRED", "allowed_read_paths must be a non-empty list"))
    for path in read_paths:
        if not _s09_path_is_safe(path):
            errors.append(issue("E_S09B_ALLOWED_READ_PATHS_REQUIRED", f"unsafe allowed_read_paths entry {path!r}"))
    write_paths = _s08_string_items(payload.get("allowed_write_paths"))
    if len(write_paths) != 1:
        errors.append(issue("E_S09B_ALLOWED_WRITE_PATHS_REQUIRED", "allowed_write_paths must contain exactly one target path"))
    for path in write_paths:
        if not _s09_path_is_safe(path):
            errors.append(issue("E_S09B_ALLOWED_WRITE_PATHS_REQUIRED", f"unsafe allowed_write_paths entry {path!r}"))
    if target is not None and write_paths:
        if target.get("allowed_write_path") != write_paths[0] or target.get("output_artifact_path") != write_paths[0]:
            errors.append(issue("E_S09B_ALLOWED_WRITE_PATHS_REQUIRED", "target_unit write path and output path must match allowed_write_paths[0]"))

    forbidden_routes = set(_s08_string_items(payload.get("forbidden_routes")))
    missing_forbidden = sorted(S09B_REQUIRED_FORBIDDEN_ROUTES - forbidden_routes)
    if missing_forbidden:
        errors.append(issue("E_S09B_FORBIDDEN_ROUTES_REQUIRED", f"forbidden_routes missing {missing_forbidden}"))
    boot = payload.get("worker_boot_clause")
    if not is_non_empty_string(boot):
        errors.append(issue("E_S09B_WORKER_BOOT_CLAUSE_REQUIRED", "worker_boot_clause must be a non-empty string"))
    else:
        lowered = str(boot).lower()
        missing_boot = sorted(term for term in S09B_BOOT_REQUIRED_TERMS if term not in lowered)
        if missing_boot:
            errors.append(issue("E_S09B_WORKER_BOOT_CLAUSE_REQUIRED", f"worker_boot_clause missing required intent {missing_boot}"))

    boundary = _require_mapping(payload, "packet_authority_boundary", "E_S09B_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in ("completion_forbidden", "no_recursive_orchestration", "controller_owned_completion", "owner_intent_change_forbidden", "graph_commit_forbidden", "publication_claim_forbidden"):
        if boundary is not None and boundary.get(key) is not True:
            errors.append(issue("E_S09B_AUTHORITY_BOUNDARY_REQUIRED", f"packet_authority_boundary.{key} must be true"))


def _validate_s09b_digest_move_and_controls(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    if not is_non_empty_string(payload.get("selected_control_bundle_ref")):
        errors.append(issue("E_S09B_SELECTED_CONTROLS_REQUIRED", "selected_control_bundle_ref must be a non-empty string"))
    if not is_non_empty_string(payload.get("task_mission")):
        errors.append(issue("E_S09B_TASK_MISSION_REQUIRED", "task_mission must be a non-empty string"))

    digest = _require_mapping(payload, "control_digest", "E_S09B_CONTROL_DIGEST_REQUIRED", errors)
    _require_mapping_fields(digest, "control_digest", ["hard_constraints_summary", "local_context_summary", "adjacent_context_summary", "background_orientation_summary"], "E_S09B_CONTROL_DIGEST_REQUIRED", errors)
    for key in ("must_obey_refs", "background_only_refs", "do_not_use_as_claim_refs"):
        _require_s09_list(digest, "control_digest", key, "E_S09B_CONTROL_DIGEST_REQUIRED", errors)

    move_plan = _require_mapping(payload, "section_or_unit_move_plan", "E_S09B_UNIT_MOVE_PLAN_REQUIRED", errors)
    jobs = _require_s05_list_records(
        move_plan,
        "section_or_unit_move_plan.paragraph_jobs",
        "paragraph_jobs",
        ["job_id", "reader_question", "stop_condition"],
        "E_S09B_UNIT_MOVE_PLAN_REQUIRED",
        errors,
    )
    for idx, job in enumerate(jobs):
        for key in ("allowed_claims", "required_evidence", "required_objects", "rhetorical_moves", "forbidden_moves", "figure_callouts", "required_caveats"):
            _require_s08_string_items(job, f"section_or_unit_move_plan.paragraph_jobs[{idx}]", key, "E_S09B_UNIT_MOVE_PLAN_REQUIRED", errors)

    for field, code in (
        ("claim_boundary_controls", "E_S09B_SELECTED_CONTROLS_REQUIRED"),
        ("reader_spine_controls", "E_S09B_SELECTED_CONTROLS_REQUIRED"),
        ("object_granularity_controls", "E_S09B_SELECTED_CONTROLS_REQUIRED"),
        ("terminology_surface_controls", "E_S09B_SELECTED_CONTROLS_REQUIRED"),
        ("visual_formal_controls", "E_S09B_SELECTED_CONTROLS_REQUIRED"),
        ("negative_controls", "E_S09B_NEGATIVE_CONTROLS_REQUIRED"),
    ):
        bundle = _require_mapping(payload, field, code, errors)
        _require_s09_list(bundle, field, "items", code, errors)

    usage = _require_mapping(payload, "context_usage_instructions", "E_S09B_CONTEXT_USAGE_REQUIRED", errors)
    for key in ("must_obey", "use_as_local_context", "use_as_adjacent_context", "use_as_background_only", "do_not_turn_into_claim", "do_not_expand_scope"):
        _require_s09_list(usage, "context_usage_instructions", key, "E_S09B_CONTEXT_USAGE_REQUIRED", errors)


def _validate_s09b_material_closure(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    digest_policy = _require_mapping(payload, "control_digest_policy", "E_S09B_CONTROL_DIGEST_POLICY_REQUIRED", errors)
    if digest_policy is not None:
        if digest_policy.get("status") != "non_authoritative_navigation_only":
            errors.append(issue("E_S09B_CONTROL_DIGEST_POLICY_REQUIRED", "control_digest_policy.status must be non_authoritative_navigation_only"))
        for key in ("may_not_be_cited_as_evidence", "may_not_replace_material_dereference"):
            if digest_policy.get(key) is not True:
                errors.append(issue("E_S09B_CONTROL_DIGEST_POLICY_REQUIRED", f"control_digest_policy.{key} must be true"))

    coverage = _require_mapping(payload, "global_material_coverage", "E_S09B_GLOBAL_COVERAGE_REQUIRED", errors)
    if coverage is not None:
        if coverage.get("status") != "pass":
            errors.append(issue("E_S09B_GLOBAL_COVERAGE_REQUIRED", "global_material_coverage.status must be pass for an emitted writing packet"))
        for key in ("claims_covered", "reader_questions_covered", "evidence_artifacts_covered", "visual_formal_needs_covered"):
            _require_s09_list(coverage, "global_material_coverage", key, "E_S09B_GLOBAL_COVERAGE_REQUIRED", errors)
        _require_s09_list(coverage, "global_material_coverage", "deferred_controls_open", "E_S09B_GLOBAL_COVERAGE_REQUIRED", errors, allow_empty=True)
        if coverage.get("blocks_s10_batch") is not False:
            errors.append(issue("E_S09B_GLOBAL_COVERAGE_REQUIRED", "global_material_coverage.blocks_s10_batch must be false for a ready S09B packet"))

    closure = _require_mapping(payload, "unit_material_closure", "E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", errors)
    closure_selectors: dict[str, set[str]] = {}
    if closure is not None:
        _require_mapping_fields(closure, "unit_material_closure", ["target_unit_id"], "E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", errors)
        if closure.get("closure_status") != "complete":
            errors.append(issue("E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", "unit_material_closure.closure_status must be complete"))
        for key in ("must_dereference", "block_if_missing"):
            _require_s09_list(closure, "unit_material_closure", key, "E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", errors)
        _require_s09_list(closure, "unit_material_closure", "may_read_background", "E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", errors, allow_empty=True)
        _require_s09_list(closure, "unit_material_closure", "forbidden_materials", "E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", errors, allow_empty=True)
        closure_selectors = _material_selector_map(closure.get("must_dereference"))
        target = as_mapping(payload.get("target_unit"))
        if target is not None and is_non_empty_string(target.get("unit_id")) and closure.get("target_unit_id") != target.get("unit_id"):
            errors.append(issue("E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", "unit_material_closure.target_unit_id must match target_unit.unit_id"))

    access = _require_mapping(payload, "material_access_manifest", "E_S09B_MATERIAL_ACCESS_MANIFEST_REQUIRED", errors)
    if access is not None:
        _require_mapping_fields(access, "material_access_manifest", ["authority_root"], "E_S09B_MATERIAL_ACCESS_MANIFEST_REQUIRED", errors)
        for key in ("allowed_authority_status", "forbidden_status", "required_selectors"):
            _require_s09_list(access, "material_access_manifest", key, "E_S09B_MATERIAL_ACCESS_MANIFEST_REQUIRED", errors)

    obligations = _require_mapping(payload, "material_read_obligations", "E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED", errors)
    if obligations is not None:
        required_materials = set(_require_s09_list(obligations, "material_read_obligations", "required_materials", "E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED", errors))
        required_selectors_by_material: dict[str, set[str]] = {}
        selectors = obligations.get("required_selectors_by_material")
        if not isinstance(selectors, dict) or not selectors:
            errors.append(issue("E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED", "material_read_obligations.required_selectors_by_material must be a non-empty mapping"))
        else:
            selector_materials = set(str(material) for material in selectors)
            if required_materials and selector_materials != required_materials:
                errors.append(issue("E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED", "material_read_obligations.required_selectors_by_material keys must exactly match required_materials"))
            for material, selector_list in selectors.items():
                if not is_non_empty_string(str(material)) or not _s08_string_items(selector_list):
                    errors.append(issue("E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED", "material_read_obligations.required_selectors_by_material entries must map material refs to non-empty selector lists"))
                else:
                    required_selectors_by_material[str(material)] = set(_s08_string_items(selector_list))
        for key in ("read_receipt_required", "hydration_required_before_drafting"):
            if obligations.get(key) is not True:
                errors.append(issue("E_S09B_MATERIAL_READ_OBLIGATIONS_REQUIRED", f"material_read_obligations.{key} must be true"))
        if required_materials and closure_selectors and set(closure_selectors) != required_materials:
            errors.append(issue("E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", "unit_material_closure.must_dereference materials must exactly match material_read_obligations.required_materials"))
        if closure_selectors and required_selectors_by_material:
            for material, required_selector_set in sorted(required_selectors_by_material.items()):
                if closure_selectors.get(material, set()) != required_selector_set:
                    errors.append(issue("E_S09B_UNIT_MATERIAL_CLOSURE_REQUIRED", f"unit_material_closure.must_dereference selectors for {material!r} must exactly match material_read_obligations.required_selectors_by_material"))

    deferred = _require_mapping(payload, "deferred_control_ledger", "E_S09B_DEFERRED_CONTROL_LEDGER_REQUIRED", errors)
    if deferred is not None:
        controls = deferred.get("controls")
        if controls != [] and not is_non_empty_mapping_list(controls):
            errors.append(issue("E_S09B_DEFERRED_CONTROL_LEDGER_REQUIRED", "deferred_control_ledger.controls must be a list of mappings"))
        if isinstance(controls, list):
            for idx, control in enumerate(controls):
                if not isinstance(control, dict):
                    continue
                for key in ("control_id", "required_for", "status"):
                    if not is_non_empty_string(control.get(key)):
                        errors.append(issue("E_S09B_DEFERRED_CONTROL_LEDGER_REQUIRED", f"deferred_control_ledger.controls[{idx}].{key} must be a non-empty string"))
                if "blocking_before_s12" in control and not isinstance(control.get("blocking_before_s12"), bool):
                    errors.append(issue("E_S09B_DEFERRED_CONTROL_LEDGER_REQUIRED", f"deferred_control_ledger.controls[{idx}].blocking_before_s12 must be boolean when present"))
        count = deferred.get("blocking_unresolved_count")
        if not isinstance(count, int) or count < 0:
            errors.append(issue("E_S09B_DEFERRED_CONTROL_LEDGER_REQUIRED", "deferred_control_ledger.blocking_unresolved_count must be a non-negative integer"))

    blockers = _require_mapping(payload, "section_specific_blockers", "E_S09B_SECTION_BLOCKERS_REQUIRED", errors)
    if blockers is not None:
        _require_mapping_fields(blockers, "section_specific_blockers", ["section_type"], "E_S09B_SECTION_BLOCKERS_REQUIRED", errors)
        _require_s09_list(blockers, "section_specific_blockers", "block_if_missing", "E_S09B_SECTION_BLOCKERS_REQUIRED", errors)
        if blockers.get("missing_material_policy") != "block_candidate_output":
            errors.append(issue("E_S09B_SECTION_BLOCKERS_REQUIRED", "section_specific_blockers.missing_material_policy must be block_candidate_output"))


def _validate_s09b_return_lock_and_packet(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    validators = set(_s08_string_items(payload.get("validators")))
    if not {"validate_packet:phase10_stage_binding", "stage_overlay:nature_expert_writing:S10"} <= validators:
        errors.append(issue("E_S09B_VALIDATORS_REQUIRED", "validators must include validate_packet and S10 Nature overlay validators"))

    return_format = _require_mapping(payload, "return_format", "E_S09B_RETURN_FORMAT_REQUIRED", errors)
    for key in ("candidate_artifact", "evidence", "remaining_risks"):
        if return_format is not None and return_format.get(key) != "required":
            errors.append(issue("E_S09B_RETURN_FORMAT_REQUIRED", f"return_format.{key} must be required"))

    lock = _require_mapping(payload, "single_writer_lock", "E_S09B_SINGLE_WRITER_LOCK_REQUIRED", errors)
    _require_mapping_fields(lock, "single_writer_lock", ["target_artifact", "locked_unit", "lock_owner", "allowed_write_path", "conflict_policy", "stale_packet_policy"], "E_S09B_SINGLE_WRITER_LOCK_REQUIRED", errors)
    write_paths = _s08_string_items(payload.get("allowed_write_paths"))
    if lock is not None and write_paths and lock.get("allowed_write_path") != write_paths[0]:
        errors.append(issue("E_S09B_SINGLE_WRITER_LOCK_REQUIRED", "single_writer_lock.allowed_write_path must match allowed_write_paths[0]"))

    stale = _require_mapping(payload, "stale_material_policy", "E_S09B_STALE_POLICY_REQUIRED", errors)
    _require_mapping_fields(stale, "stale_material_policy", ["policy", "stale_if_upstream_changes", "recompile_trigger"], "E_S09B_STALE_POLICY_REQUIRED", errors)

    missing = _require_mapping(payload, "missing_material_report", "E_S09B_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    _require_mapping_fields(missing, "missing_material_report", ["status", "format"], "E_S09B_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    _require_list_field(missing, "missing_material_report", "items", "E_S09B_MISSING_MATERIAL_REPORT_REQUIRED", errors, allow_empty=True)

    emitted = _require_mapping(payload, "emitted_task_packet", "E_S09B_EMITTED_PACKET_REQUIRED", errors)
    _require_mapping_fields(emitted, "emitted_task_packet", ["packet_ref", "packet_id", "validation_status"], "E_S09B_EMITTED_PACKET_REQUIRED", errors)
    if emitted is not None and emitted.get("validation_status") != "validates_with_validate_packet":
        errors.append(issue("E_S09B_EMITTED_PACKET_REQUIRED", "emitted_task_packet.validation_status must be validates_with_validate_packet"))


def _validate_s09b_task_packet_assembly(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s09b_payload_header(payload, "ppg-s09b-task-packet-assembly/v0.1", "E_S09B_TASK_PACKET_ASSEMBLY_REQUIRED", errors)
    rejected = sorted(S09B_REJECTED_ALIAS_FIELDS & set(payload))
    if rejected:
        errors.append(issue("E_S09B_FORBIDDEN_ALIAS_FIELD", f"S09BTaskPacketAssembly must not use rejected alias fields: {rejected}"))
    _require_s09b_required_modules(payload, errors)
    if payload.get("completion_boundary") != S09B_COMPLETION_BOUNDARY:
        errors.append(issue("E_S09B_COMPLETION_BOUNDARY", f"completion_boundary must be {S09B_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S09_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S09B_NO_COMPLETION_OVERCLAIM", f"S09B task packet assembly must not contain completion field {completion_key!r}"))
    final_key = _contains_forbidden_key(payload, S09_FINAL_CONTENT_KEYS)
    if final_key is not None:
        errors.append(issue("E_S09B_NO_CANDIDATE_CONTENT", f"S09B task packet assembly must not contain candidate/final content field {final_key!r}"))

    _validate_s09b_identity_paths_and_authority(payload, errors)
    _validate_s09b_digest_move_and_controls(payload, errors)
    _validate_s09b_material_closure(payload, errors)
    _validate_s09b_return_lock_and_packet(payload, errors)
    candidate = _require_mapping(payload, "candidate_return", "E_S09B_TASK_PACKET_ASSEMBLY_REQUIRED", errors)
    _require_mapping_fields(candidate, "candidate_return", ["candidate_artifact"], "E_S09B_TASK_PACKET_ASSEMBLY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "evidence", "E_S09B_TASK_PACKET_ASSEMBLY_REQUIRED", errors)
    _require_string_list(candidate, "candidate_return", "remaining_risks", "E_S09B_TASK_PACKET_ASSEMBLY_REQUIRED", errors, allow_empty=True)


def _require_s10_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary",
        "packet_compliance_report",
        "material_hydration_report",
        "material_read_receipt_ledger",
        "candidate_text_unit",
        "section_or_unit_skeleton",
        "move_trace",
        "claim_evidence_trace",
        "terminology_trace",
        "object_granularity_trace",
        "visual_callout_trace",
        "forbidden_expression_scan",
        "coverage_ledger",
        "candidate_artifact_return",
        "writer_execution_evidence",
        "verifier_evidence",
        "remaining_risks",
        "missing_material_report",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S10_CANDIDATE_TEXT_RETURN_REQUIRED", f"S10CandidateTextReturn missing required modules: {missing}"))


def _validate_s10_completion_boundary(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    if payload.get("completion_boundary") != S10_COMPLETION_BOUNDARY:
        errors.append(issue("E_S10_COMPLETION_BOUNDARY", f"completion_boundary must be {S10_COMPLETION_BOUNDARY!r}"))
    boundary = _require_mapping(payload, "authority_boundary", "E_S10_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "recursive_dispatch_requested",
        "writes_outside_allowed_paths",
        "owner_intent_changed",
        "final_acceptance_claimed",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S10_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S10_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))


def _validate_s10_packet_compliance(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[str, str]:
    report = _require_mapping(payload, "packet_compliance_report", "E_S10_PACKET_COMPLIANCE_REQUIRED", errors)
    _require_mapping_fields(report, "packet_compliance_report", ["packet_id", "target_unit", "allowed_write_path_used"], "E_S10_PACKET_COMPLIANCE_REQUIRED", errors)
    for key in ("allowed_read_paths_used", "validators_acknowledged", "forbidden_routes_observed"):
        _require_s09_list(report, "packet_compliance_report", key, "E_S10_PACKET_COMPLIANCE_REQUIRED", errors)
    _require_s09_list(report, "packet_compliance_report", "missing_packet_fields", "E_S10_PACKET_COMPLIANCE_REQUIRED", errors, allow_empty=True)
    packet_id = ""
    output_path = ""
    if report is not None:
        packet_id = str(report.get("packet_id") or "")
        output_path = str(report.get("allowed_write_path_used") or "")
        if report.get("return_format_acknowledged") is not True:
            errors.append(issue("E_S10_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.return_format_acknowledged must be true"))
        if report.get("single_writer_lock_observed") is not True:
            errors.append(issue("E_S10_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.single_writer_lock_observed must be true"))
        if report.get("blocked") is not False:
            errors.append(issue("E_S10_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.blocked must be false for candidate output"))
        if report.get("missing_packet_fields"):
            errors.append(issue("E_S10_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.missing_packet_fields must be empty"))
        forbidden = set(_s08_string_items(report.get("forbidden_routes_observed")))
        missing_forbidden = sorted(S09B_REQUIRED_FORBIDDEN_ROUTES - forbidden)
        if missing_forbidden:
            errors.append(issue("E_S10_PACKET_COMPLIANCE_REQUIRED", f"packet_compliance_report.forbidden_routes_observed missing {missing_forbidden}"))
        if not _s09_path_is_safe(output_path) or not output_path.startswith("examples/candidate-artifacts/"):
            errors.append(issue("E_S10_ALLOWED_WRITE_PATH_REQUIRED", f"unsafe S10 output path {output_path!r}"))
    return packet_id, output_path


def _s10_packet_obligations(packet: dict[str, Any] | None, packet_id: str, errors: list[ValidationIssue]) -> tuple[set[str], dict[str, set[str]]]:
    if packet is None:
        errors.append(issue("E_S10_PACKET_OBLIGATIONS_REQUIRED", "S10 candidate validation requires --packet pointing to the S09B-emitted S10 TaskPacket"))
        return set(), {}
    if packet.get("stage_id") != "S10" or packet.get("task_kind") != "writing":
        errors.append(issue("E_S10_PACKET_OBLIGATIONS_REQUIRED", "S10 --packet must be an S10 writing TaskPacket"))
    if packet_id and packet.get("packet_id") != packet_id:
        errors.append(issue("E_S10_PACKET_OBLIGATIONS_REQUIRED", "S10 --packet packet_id must match packet_compliance_report.packet_id"))
    obligations = packet.get("material_read_obligations")
    if not isinstance(obligations, dict):
        errors.append(issue("E_S10_PACKET_OBLIGATIONS_REQUIRED", "S10 --packet must carry material_read_obligations"))
        return set(), {}
    required_materials = set(_s08_string_items(obligations.get("required_materials")))
    selectors_raw = obligations.get("required_selectors_by_material")
    selectors: dict[str, set[str]] = {}
    if isinstance(selectors_raw, dict):
        selectors = {str(material): set(_s08_string_items(selector_list)) for material, selector_list in selectors_raw.items()}
    if not required_materials or set(selectors) != required_materials or any(not selector_set for selector_set in selectors.values()):
        errors.append(issue("E_S10_PACKET_OBLIGATIONS_REQUIRED", "S10 --packet material_read_obligations must exactly map every required material to required selectors"))
    return required_materials, selectors


def _validate_s10_material_hydration_and_receipts(payload: dict[str, Any], packet_id: str, packet: dict[str, Any] | None, errors: list[ValidationIssue]) -> None:
    packet_required_materials, packet_required_selectors = _s10_packet_obligations(packet, packet_id, errors)
    hydration = _require_mapping(payload, "material_hydration_report", "E_S10_MATERIAL_HYDRATION_REQUIRED", errors)
    required_materials: set[str] = set()
    hydrated_materials: set[str] = set()
    required_selectors_by_material: dict[str, set[str]] = {}
    if hydration is not None:
        _require_mapping_fields(hydration, "material_hydration_report", ["status", "packet_id"], "E_S10_MATERIAL_HYDRATION_REQUIRED", errors)
        required_materials = set(_require_s09_list(hydration, "material_hydration_report", "required_materials", "E_S10_MATERIAL_HYDRATION_REQUIRED", errors))
        hydrated_materials = set(_require_s09_list(hydration, "material_hydration_report", "hydrated_materials", "E_S10_MATERIAL_HYDRATION_REQUIRED", errors))
        missing_materials = _require_s09_list(hydration, "material_hydration_report", "missing_materials", "E_S10_MATERIAL_HYDRATION_REQUIRED", errors, allow_empty=True)
        if packet_required_materials and required_materials != packet_required_materials:
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.required_materials must exactly match S09B packet material_read_obligations.required_materials"))
            errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when required materials diverge from the S09B packet"))
        if packet_id and hydration.get("packet_id") != packet_id:
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.packet_id must match packet_compliance_report.packet_id"))
        if hydration.get("status") != "pass":
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.status must be pass for candidate output"))
        if hydration.get("blocked") is not False:
            errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "material_hydration_report.blocked must be false for candidate output"))
        if missing_materials:
            errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 candidate output is forbidden while material_hydration_report.missing_materials is non-empty"))
        missing_hydration = sorted(required_materials - hydrated_materials)
        if missing_hydration:
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", f"material_hydration_report.hydrated_materials missing required materials {missing_hydration}"))
            errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must return a blocked output instead of candidate text until all required materials are hydrated"))
        expected_hydrated_materials = packet_required_materials or required_materials
        extra_hydration = sorted(hydrated_materials - expected_hydrated_materials)
        if extra_hydration:
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", f"material_hydration_report.hydrated_materials contains materials not required by the S09B packet {extra_hydration}"))
            errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when hydrated materials diverge from S09B packet obligations"))
        required_selectors = hydration.get("required_selectors_by_material")
        hydrated_selectors = hydration.get("hydrated_selectors_by_material")
        if not isinstance(required_selectors, dict) or not required_selectors:
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.required_selectors_by_material must be a non-empty mapping"))
        if not isinstance(hydrated_selectors, dict) or not hydrated_selectors:
            errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.hydrated_selectors_by_material must be a non-empty mapping"))
        if isinstance(required_selectors, dict) and isinstance(hydrated_selectors, dict):
            required_selector_keys = set(str(material) for material in required_selectors)
            hydrated_selector_keys = set(str(material) for material in hydrated_selectors)
            expected_selector_keys = packet_required_materials or required_materials
            if expected_selector_keys and required_selector_keys != expected_selector_keys:
                errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.required_selectors_by_material keys must exactly match S09B packet required materials"))
                errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when required selector declarations diverge from the S09B packet"))
            if expected_selector_keys and hydrated_selector_keys != expected_selector_keys:
                errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", "material_hydration_report.hydrated_selectors_by_material keys must exactly match S09B packet required materials"))
                errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when hydrated selector declarations diverge from the S09B packet"))
            for material, packet_selectors in sorted(packet_required_selectors.items()):
                declared = set(_s08_string_items(required_selectors.get(material)))
                hydrated = set(_s08_string_items(hydrated_selectors.get(material)))
                if declared != packet_selectors:
                    errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", f"material_hydration_report.required_selectors_by_material[{material!r}] must exactly match S09B packet selectors"))
                    errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when selector obligations diverge from the S09B packet"))
                if hydrated != packet_selectors:
                    errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", f"material_hydration_report.hydrated_selectors_by_material[{material!r}] must exactly match S09B packet selectors"))
                    errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output until every S09B-required selector is hydrated"))
            for material in sorted(required_materials):
                required = packet_required_selectors.get(material) or set(_s08_string_items(required_selectors.get(material)))
                hydrated = set(_s08_string_items(hydrated_selectors.get(material)))
                required_selectors_by_material[material] = required
                if not required:
                    errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", f"material_hydration_report.required_selectors_by_material missing selectors for {material!r}"))
                missing_selectors = sorted(required - hydrated)
                if missing_selectors:
                    errors.append(issue("E_S10_MATERIAL_HYDRATION_REQUIRED", f"material_hydration_report.hydrated_selectors_by_material[{material!r}] missing selectors {missing_selectors}"))
                    errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output until required material selectors are hydrated"))

    receipts = _require_mapping(payload, "material_read_receipt_ledger", "E_S10_MATERIAL_READ_RECEIPT_REQUIRED", errors)
    if receipts is None:
        return
    _require_mapping_fields(receipts, "material_read_receipt_ledger", ["status", "reader_agent_type", "packet_id"], "E_S10_MATERIAL_READ_RECEIPT_REQUIRED", errors)
    if packet_id and receipts.get("packet_id") != packet_id:
        errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", "material_read_receipt_ledger.packet_id must match packet_compliance_report.packet_id"))
    if receipts.get("reader_agent_type") != "writer":
        errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", "material_read_receipt_ledger.reader_agent_type must be writer"))
    if receipts.get("status") != "pass":
        errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", "material_read_receipt_ledger.status must be pass for candidate output"))
    if receipts.get("blocked") is not False:
        errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "material_read_receipt_ledger.blocked must be false for candidate output"))
    missing_receipts = _require_s09_list(receipts, "material_read_receipt_ledger", "missing_receipts", "E_S10_MATERIAL_READ_RECEIPT_REQUIRED", errors, allow_empty=True)
    if missing_receipts:
        errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 candidate output is forbidden while material_read_receipt_ledger.missing_receipts is non-empty"))
    records = receipts.get("receipts")
    if not is_non_empty_mapping_list(records):
        errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", "material_read_receipt_ledger.receipts must be a non-empty list of mappings"))
        return
    assert isinstance(records, list)
    seen_materials: set[str] = set()
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        for key in ("material_ref", "receipt_status", "source_packet_obligation"):
            if not is_non_empty_string(record.get(key)):
                errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts[{idx}].{key} must be a non-empty string"))
        selectors_read = _s08_string_items(record.get("selectors_read"))
        if not selectors_read:
            errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts[{idx}].selectors_read must be a non-empty list of strings"))
        if record.get("receipt_status") != "read":
            errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts[{idx}].receipt_status must be read"))
        material_ref = str(record.get("material_ref") or "")
        if material_ref:
            seen_materials.add(material_ref)
            expected_materials = packet_required_materials or required_materials
            if expected_materials and material_ref not in expected_materials:
                errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts[{idx}].material_ref is not required by the S09B packet"))
                errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when read receipts diverge from S09B packet obligations"))
            missing_selectors = sorted(required_selectors_by_material.get(material_ref, set()) - set(selectors_read))
            if missing_selectors:
                errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts[{idx}].selectors_read missing required selectors {missing_selectors}"))
                errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output until every required selector has a read receipt"))
    expected_receipt_materials = packet_required_materials or required_materials
    missing_read_materials = sorted(expected_receipt_materials - seen_materials)
    if missing_read_materials:
        errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts missing required materials {missing_read_materials}"))
        errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output until every required material has a read receipt"))
    extra_read_materials = sorted(seen_materials - expected_receipt_materials)
    if extra_read_materials:
        errors.append(issue("E_S10_MATERIAL_READ_RECEIPT_REQUIRED", f"material_read_receipt_ledger.receipts contains materials not required by the S09B packet {extra_read_materials}"))
        errors.append(issue("E_S10_BLOCKED_OUTPUT_REQUIRED", "S10 must block candidate output when read receipts contain materials outside S09B packet obligations"))


def _validate_s10_candidate_text_unit(payload: dict[str, Any], packet_id: str, output_path: str, errors: list[ValidationIssue]) -> None:
    unit = _require_mapping(payload, "candidate_text_unit", "E_S10_CANDIDATE_TEXT_UNIT_REQUIRED", errors)
    _require_mapping_fields(unit, "candidate_text_unit", ["draft_id", "status", "target_unit_id", "section_id", "packet_id", "output_artifact_path", "candidate_body"], "E_S10_CANDIDATE_TEXT_UNIT_REQUIRED", errors)
    for key in ("source_materials", "evidence_anchors"):
        _require_s09_list(unit, "candidate_text_unit", key, "E_S10_CANDIDATE_TEXT_UNIT_REQUIRED", errors)
    if unit is None:
        return
    if unit.get("status") != "candidate":
        errors.append(issue("E_S10_CANDIDATE_TEXT_UNIT_REQUIRED", "candidate_text_unit.status must be candidate"))
    if packet_id and unit.get("packet_id") != packet_id:
        errors.append(issue("E_S10_PACKET_COMPLIANCE_REQUIRED", "candidate_text_unit.packet_id must match packet_compliance_report.packet_id"))
    if output_path and unit.get("output_artifact_path") != output_path:
        errors.append(issue("E_S10_ALLOWED_WRITE_PATH_REQUIRED", "candidate_text_unit.output_artifact_path must match packet_compliance_report.allowed_write_path_used"))
    if unit.get("graph_completion_claimed") is not False:
        errors.append(issue("E_S10_AUTHORITY_BOUNDARY_REQUIRED", "candidate_text_unit.graph_completion_claimed must be false"))
    if unit.get("recursive_dispatch_requested") is not False:
        errors.append(issue("E_S10_AUTHORITY_BOUNDARY_REQUIRED", "candidate_text_unit.recursive_dispatch_requested must be false"))
    body = unit.get("candidate_body")
    if not is_non_empty_string(body):
        errors.append(issue("E_S10_CANDIDATE_TEXT_UNIT_REQUIRED", "candidate_text_unit.candidate_body must be non-empty"))
        return
    lowered = str(body).lower()
    for phrase in (
        "guarantees universal safety",
        "always safe",
        "paper is complete",
        "manuscript is ready",
        "submission ready",
    ):
        if phrase in lowered:
            errors.append(issue("E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED", f"candidate_body contains forbidden expression {phrase!r}"))
    for required_term in ("bounded", "authority"):
        if required_term not in lowered:
            errors.append(issue("E_S10_CLAIM_EVIDENCE_TRACE_REQUIRED", f"candidate_body must preserve bounded authority framing; missing {required_term!r}"))


def _validate_s10_skeleton_and_traces(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    skeleton = payload.get("section_or_unit_skeleton")
    if not is_non_empty_mapping_list(skeleton):
        errors.append(issue("E_S10_SKELETON_REQUIRED", "section_or_unit_skeleton must be a non-empty list of mappings"))
    else:
        assert isinstance(skeleton, list)
        for idx, item in enumerate(skeleton):
            assert isinstance(item, dict)
            for key in ("unit_part_id", "paragraph_or_sentence_group_job", "reader_question", "object_granularity", "rhetorical_move"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S10_SKELETON_REQUIRED", f"section_or_unit_skeleton[{idx}].{key} must be a non-empty string"))
            for key in ("allowed_claims", "required_evidence", "required_objects", "visual_callouts", "forbidden_content", "required_caveats"):
                _require_s08_string_items(item, f"section_or_unit_skeleton[{idx}]", key, "E_S10_SKELETON_REQUIRED", errors)

    trace_specs = (
        ("move_trace", "E_S10_MOVE_TRACE_REQUIRED", ["text_span_or_paragraph_id", "paragraph_job", "source_s07_rule", "source_s09b_move_plan", "reader_question_answered"], ["rhetorical_moves_used"]),
        ("claim_evidence_trace", "E_S10_CLAIM_EVIDENCE_TRACE_REQUIRED", ["text_span_or_sentence_id", "claim_id", "source_s04_capsule", "admitted_claim", "evidence_anchor", "support_strength", "allowed_wording_used"], []),
        ("terminology_trace", "E_S10_TERMINOLOGY_TRACE_REQUIRED", ["term_used", "canonical_term", "source_terminology_rule", "first_definition_status", "drift_risk"], []),
        ("object_granularity_trace", "E_S10_OBJECT_GRANULARITY_TRACE_REQUIRED", ["object_id", "text_span_or_paragraph_id", "intended_granularity", "actual_granularity", "explanation_ladder_level", "cognitive_load_risk", "repetition_risk"], []),
        ("visual_callout_trace", "E_S10_VISUAL_CALLOUT_TRACE_REQUIRED", ["text_span_or_callout_id", "visual_id", "source_s08_contract", "callout_claim", "backend_route_referenced_if_needed"], ["supported_claims"]),
    )
    for field, code, string_keys, list_keys in trace_specs:
        records = payload.get(field)
        if not is_non_empty_mapping_list(records):
            errors.append(issue(code, f"{field} must be a non-empty list of mappings"))
            continue
        assert isinstance(records, list)
        for idx, record in enumerate(records):
            assert isinstance(record, dict)
            for key in string_keys:
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue(code, f"{field}[{idx}].{key} must be a non-empty string"))
            for key in list_keys:
                _require_s08_string_items(record, f"{field}[{idx}]", key, code, errors)
            if field == "claim_evidence_trace":
                for key in ("forbidden_wording_absent", "wording_within_allowed_boundary"):
                    if record.get(key) is not True:
                        errors.append(issue(code, f"{field}[{idx}].{key} must be true"))
            if field == "terminology_trace" and record.get("internal_id_leakage") is not False:
                errors.append(issue(code, f"{field}[{idx}].internal_id_leakage must be false"))
            if field == "object_granularity_trace" and record.get("forbidden_detail_violated") is not False:
                errors.append(issue(code, f"{field}[{idx}].forbidden_detail_violated must be false"))
            if field == "visual_callout_trace":
                for key in ("unsupported_claims_avoided", "schematic_not_used_as_evidence", "caption_boundary_observed"):
                    if record.get(key) is not True:
                        errors.append(issue(code, f"{field}[{idx}].{key} must be true"))


def _validate_s10_scan_coverage_return_and_evidence(payload: dict[str, Any], packet_id: str, output_path: str, errors: list[ValidationIssue]) -> None:
    scan = _require_mapping(payload, "forbidden_expression_scan", "E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED", errors)
    categories = _require_s09_list(scan, "forbidden_expression_scan", "scanned_for", "E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED", errors)
    missing_categories = sorted(S10_REQUIRED_FORBIDDEN_SCAN_CATEGORIES - categories)
    if missing_categories:
        errors.append(issue("E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED", f"forbidden_expression_scan.scanned_for missing {missing_categories}"))
    _require_s09_list(scan, "forbidden_expression_scan", "findings", "E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED", errors, allow_empty=True)
    if scan is not None and scan.get("clean") is not True:
        errors.append(issue("E_S10_FORBIDDEN_EXPRESSION_SCAN_REQUIRED", "forbidden_expression_scan.clean must be true for a candidate output"))

    coverage = _require_mapping(payload, "coverage_ledger", "E_S10_COVERAGE_LEDGER_REQUIRED", errors)
    for key in (
        "paragraph_jobs_required",
        "paragraph_jobs_completed",
        "admitted_claims_required",
        "admitted_claims_used",
        "evidence_anchors_required",
        "evidence_anchors_used",
        "required_objects",
        "objects_used_at_correct_granularity",
        "required_caveats",
        "caveats_included",
        "visual_callouts_required",
        "visual_callouts_completed",
    ):
        value = _require_s08_count(coverage, "coverage_ledger", key, "E_S10_COVERAGE_LEDGER_REQUIRED", errors)
        if value is not None and key.endswith("_required") and value <= 0:
            errors.append(issue("E_S10_COVERAGE_LEDGER_REQUIRED", f"coverage_ledger.{key} must be positive"))
    _require_s09_list(coverage, "coverage_ledger", "unresolved_packet_requirements", "E_S10_COVERAGE_LEDGER_REQUIRED", errors, allow_empty=True)
    if coverage is not None and coverage.get("unresolved_packet_requirements"):
        errors.append(issue("E_S10_COVERAGE_LEDGER_REQUIRED", "coverage_ledger.unresolved_packet_requirements must be empty for a candidate output"))

    candidate_return = _require_mapping(payload, "candidate_artifact_return", "E_S10_CANDIDATE_RETURN_REQUIRED", errors)
    _require_mapping_fields(candidate_return, "candidate_artifact_return", ["schema_version", "return_id", "status", "packet_id", "output_artifact_path"], "E_S10_CANDIDATE_RETURN_REQUIRED", errors)
    for key in ("evidence", "validator_expectations", "remaining_risks"):
        _require_s09_list(candidate_return, "candidate_artifact_return", key, "E_S10_CANDIDATE_RETURN_REQUIRED", errors)
    if candidate_return is not None:
        if candidate_return.get("schema_version") != "ppg-candidate-return/v0.1":
            errors.append(issue("E_S10_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.schema_version must be ppg-candidate-return/v0.1"))
        if candidate_return.get("status") != "candidate":
            errors.append(issue("E_S10_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.status must be candidate"))
        if packet_id and candidate_return.get("packet_id") != packet_id:
            errors.append(issue("E_S10_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.packet_id must match packet"))
        if output_path and candidate_return.get("output_artifact_path") != output_path:
            errors.append(issue("E_S10_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.output_artifact_path must match allowed write path"))
        for key in ("graph_completion_claimed", "recursive_dispatch_requested", "writes_outside_allowed_paths"):
            if candidate_return.get(key) is not False:
                errors.append(issue("E_S10_CANDIDATE_RETURN_REQUIRED", f"candidate_artifact_return.{key} must be false"))

    writer = _require_mapping(payload, "writer_execution_evidence", "E_S10_WRITER_EVIDENCE_REQUIRED", errors)
    _require_mapping_fields(writer, "writer_execution_evidence", ["agent_type", "packet_ref", "output_artifact_path"], "E_S10_WRITER_EVIDENCE_REQUIRED", errors)
    passes = _require_s09_list(writer, "writer_execution_evidence", "required_passes_completed", "E_S10_WRITER_EVIDENCE_REQUIRED", errors)
    missing_passes = sorted(S10_REQUIRED_WRITER_PASSES - passes)
    if missing_passes:
        errors.append(issue("E_S10_WRITER_EVIDENCE_REQUIRED", f"writer_execution_evidence.required_passes_completed missing {missing_passes}"))
    if writer is not None:
        if writer.get("agent_type") != "writer":
            errors.append(issue("E_S10_WRITER_EVIDENCE_REQUIRED", "writer_execution_evidence.agent_type must be writer"))
        if writer.get("wrote_only_allowed_path") is not True:
            errors.append(issue("E_S10_WRITER_EVIDENCE_REQUIRED", "writer_execution_evidence.wrote_only_allowed_path must be true"))
        if output_path and writer.get("output_artifact_path") != output_path:
            errors.append(issue("E_S10_WRITER_EVIDENCE_REQUIRED", "writer_execution_evidence.output_artifact_path must match allowed write path"))

    verifier = _require_mapping(payload, "verifier_evidence", "E_S10_VERIFIER_EVIDENCE_REQUIRED", errors)
    _require_mapping_fields(verifier, "verifier_evidence", ["agent_type", "verification_status", "acceptance_recommendation"], "E_S10_VERIFIER_EVIDENCE_REQUIRED", errors)
    checks = _require_s09_list(verifier, "verifier_evidence", "checks_completed", "E_S10_VERIFIER_EVIDENCE_REQUIRED", errors)
    missing_checks = sorted(S10_REQUIRED_VERIFIER_CHECKS - checks)
    if missing_checks:
        errors.append(issue("E_S10_VERIFIER_EVIDENCE_REQUIRED", f"verifier_evidence.checks_completed missing {missing_checks}"))
    for key in ("findings", "claim_boundary_violations", "missing_traces", "terminology_or_id_violations", "object_granularity_violations", "visual_callout_violations", "authority_boundary_violations"):
        _require_s09_list(verifier, "verifier_evidence", key, "E_S10_VERIFIER_EVIDENCE_REQUIRED", errors, allow_empty=True)
    if verifier is not None:
        if verifier.get("agent_type") != "verifier":
            errors.append(issue("E_S10_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.agent_type must be verifier"))
        if verifier.get("verification_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S10_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.verification_status must be pass or pass_with_risks"))

    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S10_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))
    missing = _require_mapping(payload, "missing_material_report", "E_S10_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    _require_mapping_fields(missing, "missing_material_report", ["status", "backflow_target_if_blocked"], "E_S10_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    if missing is not None and missing.get("status") != "not_blocked":
        errors.append(issue("E_S10_MISSING_MATERIAL_REPORT_REQUIRED", "missing_material_report.status must be not_blocked for candidate output"))


def _validate_s10_candidate_text_return(payload: dict[str, Any], errors: list[ValidationIssue], packet: dict[str, Any] | None = None) -> None:
    _require_s10_payload_header(payload, "ppg-s10-candidate-text-return/v0.1", "E_S10_CANDIDATE_TEXT_RETURN_REQUIRED", errors)
    _require_s10_required_modules(payload, errors)
    completion_key = _contains_forbidden_key(payload, S10_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S10_NO_COMPLETION_OVERCLAIM", f"S10 candidate text return must not contain completion field {completion_key!r}"))
    final_key = _contains_forbidden_key(payload, S10_FINAL_ACCEPTANCE_KEYS)
    if final_key is not None:
        errors.append(issue("E_S10_NO_FINAL_ACCEPTANCE", f"S10 candidate text return must not contain final acceptance field {final_key!r}"))

    _validate_s10_completion_boundary(payload, errors)
    packet_id, output_path = _validate_s10_packet_compliance(payload, errors)
    _validate_s10_material_hydration_and_receipts(payload, packet_id, packet, errors)
    _validate_s10_candidate_text_unit(payload, packet_id, output_path, errors)
    _validate_s10_skeleton_and_traces(payload, errors)
    _validate_s10_scan_coverage_return_and_evidence(payload, packet_id, output_path, errors)


def _require_s11_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary",
        "packet_compliance_report",
        "figure_contract_compliance",
        "generated_artifacts",
        "editable_source_bundle",
        "nature_figure_capability_report",
        "nature_figure_contract",
        "nature_figure_execution",
        "nature_figure_qa_report",
        "source_data_trace",
        "panel_claim_trace",
        "caption_legend_draft",
        "caption_claim_trace",
        "image_integrity_record",
        "visual_polish_policy",
        "visual_polish_report",
        "figure_statistics",
        "accessibility_check",
        "export_manifest",
        "coverage_ledger",
        "candidate_artifact_return",
        "verifier_evidence",
        "remaining_risks",
        "missing_material_report",
    ]
    missing = [field for field in required if not _has_non_empty_payload_value(payload.get(field))]
    if missing:
        errors.append(issue("E_S11_ARTIFACT_BUNDLE_REQUIRED", f"S11FigureCaptionArtifactBundle missing required modules: {missing}"))


def _s11_path_has_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _validate_s11_safe_paths(paths: Any, label: str, prefixes: tuple[str, ...], code: str, errors: list[ValidationIssue]) -> None:
    for path in _s08_string_items(paths):
        if not _s09_path_is_safe(path) or not _s11_path_has_prefix(path, prefixes):
            errors.append(issue(code, f"{label} contains unsafe or wrong-scope path: {path}"))


def _s11_nature_direct_call_enabled(payload: dict[str, Any]) -> bool:
    return isinstance(payload.get("nature_figure_capability_report"), dict)


def _validate_s11_nature_figure_direct_call(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    capability = _require_mapping(payload, "nature_figure_capability_report", "E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED", errors)
    _require_mapping_fields(
        capability,
        "nature_figure_capability_report",
        ["parity_target", "upstream_commit", "vendor_path", "parity_manifest_ref", "direct_call_step"],
        "E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED",
        errors,
    )
    loaded_components = _require_s09_list(
        capability,
        "nature_figure_capability_report",
        "loaded_components",
        "E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED",
        errors,
    )
    if capability is not None:
        expected_pairs = {
            "parity_target": S11_NATURE_PARITY_TARGET,
            "upstream_commit": S11_NATURE_UPSTREAM_COMMIT,
            "vendor_path": S11_NATURE_VENDOR_PATH,
            "parity_manifest_ref": S11_NATURE_PARITY_MANIFEST,
            "direct_call_step": S11_NATURE_CALL_STEP,
        }
        for key, expected in expected_pairs.items():
            if capability.get(key) != expected:
                errors.append(issue("E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED", f"nature_figure_capability_report.{key} must be {expected!r}"))
        missing_components = sorted(S11_NATURE_REQUIRED_LOADED_COMPONENTS - loaded_components)
        if missing_components:
            errors.append(issue("E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED", f"nature_figure_capability_report.loaded_components missing {missing_components}"))
        for key in ("s11_contract_overrides_skill", "capability_floor_preserved"):
            if capability.get(key) is not True:
                errors.append(issue("E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED", f"nature_figure_capability_report.{key} must be true"))

    contract = _require_mapping(payload, "nature_figure_contract", "E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", errors)
    _require_mapping_fields(
        contract,
        "nature_figure_contract",
        ["core_conclusion", "archetype", "backend", "selected_backend_fragment"],
        "E_S11_NATURE_FIGURE_CONTRACT_REQUIRED",
        errors,
    )
    _require_s09_list(contract, "nature_figure_contract", "evidence_chain", "E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", errors)
    _require_s09_list(contract, "nature_figure_contract", "review_risk_checks", "E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", errors)
    if contract is not None:
        backend = contract.get("backend")
        expected_fragment = S11_NATURE_BACKEND_FRAGMENTS.get(str(backend))
        if backend not in S11_NATURE_BACKEND_TOOLS:
            errors.append(issue("E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", "nature_figure_contract.backend must be python or r"))
        elif contract.get("selected_backend_fragment") != expected_fragment:
            errors.append(issue("E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", "nature_figure_contract.selected_backend_fragment must match backend"))
        if contract.get("backend_selected_before_worker") is not True:
            errors.append(issue("E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", "nature_figure_contract.backend_selected_before_worker must be true"))
        if expected_fragment is not None and expected_fragment not in loaded_components:
            errors.append(issue("E_S11_NATURE_FIGURE_CAPABILITY_REQUIRED", "nature_figure_capability_report.loaded_components must include selected backend fragment"))
        journal = as_mapping(contract.get("journal_export_contract"))
        if journal is None:
            errors.append(issue("E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", "nature_figure_contract.journal_export_contract must be a mapping"))
        else:
            target_formats = set(_s08_string_items(journal.get("target_formats")))
            if not {"svg", "pdf"}.issubset(target_formats):
                errors.append(issue("E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", "nature_figure_contract.journal_export_contract.target_formats must include svg and pdf"))
            for key in ("editable_text_required", "source_data_trace_required"):
                if journal.get(key) is not True:
                    errors.append(issue("E_S11_NATURE_FIGURE_CONTRACT_REQUIRED", f"nature_figure_contract.journal_export_contract.{key} must be true"))

    execution = _require_mapping(payload, "nature_figure_execution", "E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", errors)
    _require_mapping_fields(
        execution,
        "nature_figure_execution",
        ["call_step", "backend", "selected_tool", "runtime_status", "script_path"],
        "E_S11_NATURE_FIGURE_EXECUTION_REQUIRED",
        errors,
    )
    _require_s09_list(execution, "nature_figure_execution", "rendered_files_planned", "E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", errors)
    if execution is not None:
        backend = execution.get("backend")
        expected_fragment = S11_NATURE_BACKEND_FRAGMENTS.get(str(backend))
        if backend not in S11_NATURE_BACKEND_TOOLS:
            errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", "nature_figure_execution.backend must be python or r"))
        elif execution.get("selected_tool") != S11_NATURE_BACKEND_TOOLS[backend]:
            errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", "nature_figure_execution.selected_tool must match selected backend"))
        if expected_fragment is not None and contract is not None and contract.get("selected_backend_fragment") != expected_fragment:
            errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", "nature_figure_contract.selected_backend_fragment must match execution backend"))
        if execution.get("call_step") != S11_NATURE_CALL_STEP:
            errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", f"nature_figure_execution.call_step must be {S11_NATURE_CALL_STEP!r}"))
        if execution.get("runtime_status") not in {"render_plan_only", "executed", "blocked"}:
            errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", "nature_figure_execution.runtime_status is invalid"))
        if not _s09_path_is_safe(str(execution.get("script_path") or "")) or not str(execution.get("script_path") or "").startswith("figures/src/"):
            errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", "nature_figure_execution.script_path must be a safe figures/src path"))
        _validate_s11_safe_paths(
            execution.get("rendered_files_planned"),
            "nature_figure_execution.rendered_files_planned",
            S11_NATURE_RENDER_PREFIXES,
            "E_S11_NATURE_FIGURE_PATH_REQUIRED",
            errors,
        )
        for key in ("backend_exclusive",):
            if execution.get(key) is not True:
                errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", f"nature_figure_execution.{key} must be true"))
        for key in ("worker_backend_question_asked", "cross_backend_used", "mock_data_used"):
            if execution.get(key) is not False:
                errors.append(issue("E_S11_NATURE_FIGURE_EXECUTION_REQUIRED", f"nature_figure_execution.{key} must be false"))

    qa = _require_mapping(payload, "nature_figure_qa_report", "E_S11_NATURE_FIGURE_QA_REQUIRED", errors)
    _require_s09_list(qa, "nature_figure_qa_report", "checks_completed", "E_S11_NATURE_FIGURE_QA_REQUIRED", errors)
    if qa is not None:
        for key in S11_NATURE_REQUIRED_QA_FLAGS:
            if qa.get(key) is not True:
                errors.append(issue("E_S11_NATURE_FIGURE_QA_REQUIRED", f"nature_figure_qa_report.{key} must be true"))
        if qa.get("final_export_claimed") is not False:
            errors.append(issue("E_S11_NATURE_FIGURE_QA_REQUIRED", "nature_figure_qa_report.final_export_claimed must be false"))

    exemplar = as_mapping(payload.get("exemplar_design_analysis"))
    transfer = as_mapping(payload.get("design_transfer_plan"))
    similarity = as_mapping(payload.get("similarity_risk_report"))
    if exemplar is not None and exemplar.get("exemplar_used") is True:
        _require_s09_list(exemplar, "exemplar_design_analysis", "design_features_observed", "E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED", errors)
        _require_s09_list(exemplar, "exemplar_design_analysis", "prohibited_copy_features", "E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED", errors)
    if transfer is not None:
        if transfer.get("direct_copy_forbidden") is not True or transfer.get("exact_layout_copy_forbidden") is not True:
            errors.append(issue("E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED", "design_transfer_plan must forbid direct and exact-layout copying"))
        if transfer.get("transfer_mode") not in {"not_applicable", "abstract_design_principles_only"}:
            errors.append(issue("E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED", "design_transfer_plan.transfer_mode must avoid direct style copying"))
    if similarity is not None:
        for key in ("exact_layout_copied", "distinctive_style_copied"):
            if similarity.get(key) is not False:
                errors.append(issue("E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED", f"similarity_risk_report.{key} must be false"))
        if similarity.get("similarity_risk") not in {"none", "low", "medium"}:
            errors.append(issue("E_S11_NATURE_FIGURE_EXEMPLAR_BOUNDARY_REQUIRED", "similarity_risk_report.similarity_risk must be none, low, or medium"))


def _validate_s11_authority_and_packet(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[str, str]:
    if payload.get("completion_boundary") != S11_COMPLETION_BOUNDARY:
        errors.append(issue("E_S11_COMPLETION_BOUNDARY", f"completion_boundary must be {S11_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S11_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S11_NO_COMPLETION_OVERCLAIM", f"S11 artifact bundle must not contain completion field {completion_key!r}"))

    boundary = _require_mapping(payload, "authority_boundary", "E_S11_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "final_export_claimed",
        "recursive_dispatch_requested",
        "writes_outside_allowed_paths",
        "owner_intent_changed",
        "proof_role_changed",
        "claim_strength_modified",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S11_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S11_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))

    report = _require_mapping(payload, "packet_compliance_report", "E_S11_PACKET_COMPLIANCE_REQUIRED", errors)
    _require_mapping_fields(report, "packet_compliance_report", ["packet_id", "target_visual_id", "target_visual_type"], "E_S11_PACKET_COMPLIANCE_REQUIRED", errors)
    for key in ("allowed_read_paths_used", "allowed_write_paths_used", "validators_acknowledged", "forbidden_routes_observed"):
        _require_s09_list(report, "packet_compliance_report", key, "E_S11_PACKET_COMPLIANCE_REQUIRED", errors)
    _require_s09_list(report, "packet_compliance_report", "missing_packet_fields", "E_S11_PACKET_COMPLIANCE_REQUIRED", errors, allow_empty=True)
    packet_id = ""
    output_path = ""
    if report is not None:
        packet_id = str(report.get("packet_id") or "")
        write_paths = _s08_string_items(report.get("allowed_write_paths_used"))
        candidate_paths = [path for path in write_paths if path.startswith("examples/candidate-artifacts/")]
        output_path = candidate_paths[0] if candidate_paths else (write_paths[0] if write_paths else "")
        if report.get("target_visual_type") not in S11_VISUAL_TYPES:
            errors.append(issue("E_S11_PACKET_COMPLIANCE_REQUIRED", f"target_visual_type must be one of {sorted(S11_VISUAL_TYPES)}"))
        if report.get("single_writer_lock_observed") is not True:
            errors.append(issue("E_S11_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.single_writer_lock_observed must be true"))
        if report.get("blocked") is not False:
            errors.append(issue("E_S11_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.blocked must be false for candidate output"))
        if report.get("missing_packet_fields"):
            errors.append(issue("E_S11_PACKET_COMPLIANCE_REQUIRED", "packet_compliance_report.missing_packet_fields must be empty"))
        forbidden = set(_s08_string_items(report.get("forbidden_routes_observed")))
        missing_forbidden = sorted(S09B_REQUIRED_FORBIDDEN_ROUTES - forbidden)
        if missing_forbidden:
            errors.append(issue("E_S11_PACKET_COMPLIANCE_REQUIRED", f"packet_compliance_report.forbidden_routes_observed missing {missing_forbidden}"))
        if _s11_nature_direct_call_enabled(payload):
            invalid_paths = [
                path
                for path in write_paths
                if not _s09_path_is_safe(path) or not _s11_path_has_prefix(path, S11_NATURE_WRITE_PREFIXES)
            ]
            if invalid_paths:
                errors.append(issue("E_S11_ALLOWED_WRITE_PATH_REQUIRED", f"packet_compliance_report.allowed_write_paths_used contains unsafe S11 nature paths: {invalid_paths}"))
            if not candidate_paths:
                errors.append(issue("E_S11_ALLOWED_WRITE_PATH_REQUIRED", "S11 nature direct call must include a candidate-artifact output path"))
            if not any(path.startswith("figures/src/") for path in write_paths):
                errors.append(issue("E_S11_ALLOWED_WRITE_PATH_REQUIRED", "S11 nature direct call must include an editable figures/src path"))
        elif len(write_paths) != 1 or not _s09_path_is_safe(output_path) or not output_path.startswith("examples/candidate-artifacts/"):
            errors.append(issue("E_S11_ALLOWED_WRITE_PATH_REQUIRED", "packet_compliance_report.allowed_write_paths_used must contain one safe candidate-artifact path"))
    return packet_id, output_path


def _validate_s11_contract_and_artifacts(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    contract = _require_mapping(payload, "figure_contract_compliance", "E_S11_FIGURE_CONTRACT_REQUIRED", errors)
    _require_mapping_fields(contract, "figure_contract_compliance", ["visual_id", "source_s08_contract", "proof_role"], "E_S11_FIGURE_CONTRACT_REQUIRED", errors)
    for key in (
        "proof_role_preserved",
        "supported_claims_preserved",
        "unsupported_claims_avoided",
        "required_panels_present",
        "caption_boundary_observed",
        "accessibility_constraints_checked",
    ):
        if contract is not None and contract.get(key) is not True:
            errors.append(issue("E_S11_FIGURE_CONTRACT_REQUIRED", f"figure_contract_compliance.{key} must be true"))

    artifacts = payload.get("generated_artifacts")
    if not is_non_empty_mapping_list(artifacts):
        errors.append(issue("E_S11_GENERATED_ARTIFACTS_REQUIRED", "generated_artifacts must be a non-empty list of mappings"))
    else:
        assert isinstance(artifacts, list)
        for idx, artifact in enumerate(artifacts):
            assert isinstance(artifact, dict)
            for key in ("artifact_id", "artifact_type", "status", "path", "source_contract_ref", "generated_from"):
                if not is_non_empty_string(artifact.get(key)):
                    errors.append(issue("E_S11_GENERATED_ARTIFACTS_REQUIRED", f"generated_artifacts[{idx}].{key} must be a non-empty string"))
            if artifact.get("artifact_type") not in S11_ARTIFACT_TYPES:
                errors.append(issue("E_S11_GENERATED_ARTIFACTS_REQUIRED", f"generated_artifacts[{idx}].artifact_type is invalid"))
            if artifact.get("status") not in S11_ARTIFACT_STATUSES:
                errors.append(issue("E_S11_GENERATED_ARTIFACTS_REQUIRED", f"generated_artifacts[{idx}].status is invalid"))
            path = str(artifact.get("path") or "")
            allowed_prefixes = S11_NATURE_WRITE_PREFIXES if _s11_nature_direct_call_enabled(payload) else ("examples/candidate-artifacts/",)
            if not _s09_path_is_safe(path) or not _s11_path_has_prefix(path, allowed_prefixes):
                errors.append(issue("E_S11_ALLOWED_WRITE_PATH_REQUIRED", f"generated_artifacts[{idx}].path must be a safe S11 artifact path"))

    editable = _require_mapping(payload, "editable_source_bundle", "E_S11_EDITABLE_SOURCE_REQUIRED", errors)
    _require_mapping_fields(editable, "editable_source_bundle", ["visual_id"], "E_S11_EDITABLE_SOURCE_REQUIRED", errors)
    for key in ("source_files", "editing_notes"):
        _require_s09_list(editable, "editable_source_bundle", key, "E_S11_EDITABLE_SOURCE_REQUIRED", errors)
    if editable is not None and editable.get("source_available") is not True:
        errors.append(issue("E_S11_EDITABLE_SOURCE_REQUIRED", "editable_source_bundle.source_available must be true or a missing-material route is required"))
    if editable is not None and _s11_nature_direct_call_enabled(payload):
        _validate_s11_safe_paths(
            editable.get("source_files"),
            "editable_source_bundle.source_files",
            S11_NATURE_SOURCE_PREFIXES,
            "E_S11_NATURE_FIGURE_PATH_REQUIRED",
            errors,
        )
        _validate_s11_safe_paths(
            editable.get("script_files"),
            "editable_source_bundle.script_files",
            S11_NATURE_SCRIPT_PREFIXES,
            "E_S11_NATURE_FIGURE_PATH_REQUIRED",
            errors,
        )

    rendered = as_mapping(payload.get("rendered_output_bundle"))
    render_plan = as_mapping(payload.get("render_plan_if_not_rendered"))
    if rendered is None and render_plan is None:
        errors.append(issue("E_S11_RENDER_OR_PLAN_REQUIRED", "rendered_output_bundle or render_plan_if_not_rendered is required"))
    if rendered is not None:
        _require_mapping_fields(rendered, "rendered_output_bundle", ["visual_id", "render_status"], "E_S11_RENDER_OR_PLAN_REQUIRED", errors)
        _require_s09_list(rendered, "rendered_output_bundle", "rendered_files", "E_S11_RENDER_OR_PLAN_REQUIRED", errors)
        if _s11_nature_direct_call_enabled(payload):
            _validate_s11_safe_paths(
                rendered.get("rendered_files"),
                "rendered_output_bundle.rendered_files",
                S11_NATURE_RENDER_PREFIXES,
                "E_S11_NATURE_FIGURE_PATH_REQUIRED",
                errors,
            )
    if render_plan is not None:
        _require_mapping_fields(render_plan, "render_plan_if_not_rendered", ["visual_id", "required_command_or_tool", "reproducibility_notes"], "E_S11_RENDER_OR_PLAN_REQUIRED", errors)
        _require_s09_list(render_plan, "render_plan_if_not_rendered", "expected_outputs", "E_S11_RENDER_OR_PLAN_REQUIRED", errors)
        if _s11_nature_direct_call_enabled(payload):
            _validate_s11_safe_paths(
                render_plan.get("expected_outputs"),
                "render_plan_if_not_rendered.expected_outputs",
                S11_NATURE_RENDER_PREFIXES,
                "E_S11_NATURE_FIGURE_PATH_REQUIRED",
                errors,
            )


def _validate_s11_traces_caption_and_quality(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    trace_specs = (
        ("source_data_trace", "E_S11_SOURCE_DATA_TRACE_REQUIRED", ["visual_id", "source_data_path", "result_artifact_path", "script_path", "evidence_ref", "provenance_status"], []),
        ("panel_claim_trace", "E_S11_PANEL_CLAIM_TRACE_REQUIRED", ["visual_id", "panel_id", "panel_role", "source_data", "evidence_ref", "claim_supported", "claim_boundary", "forbidden_interpretation"], ["caption_sentence_refs"]),
        ("caption_claim_trace", "E_S11_CAPTION_CLAIM_TRACE_REQUIRED", ["caption_span", "claim_id", "source_s04_capsule", "allowed_wording_used", "support_strength"], []),
    )
    for field, code, string_keys, list_keys in trace_specs:
        records = payload.get(field)
        if not is_non_empty_mapping_list(records):
            errors.append(issue(code, f"{field} must be a non-empty list of mappings"))
            continue
        assert isinstance(records, list)
        for idx, record in enumerate(records):
            assert isinstance(record, dict)
            for key in string_keys:
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue(code, f"{field}[{idx}].{key} must be a non-empty string"))
            for key in list_keys:
                _require_s08_string_items(record, f"{field}[{idx}]", key, code, errors)
            if field == "caption_claim_trace":
                for key in ("forbidden_wording_absent", "required_caveat_present"):
                    if record.get(key) is not True:
                        errors.append(issue(code, f"{field}[{idx}].{key} must be true"))

    caption = _require_mapping(payload, "caption_legend_draft", "E_S11_CAPTION_BOUNDARY_REQUIRED", errors)
    _require_mapping_fields(caption, "caption_legend_draft", ["visual_id", "caption_text_candidate", "source_caption_brief", "status"], "E_S11_CAPTION_BOUNDARY_REQUIRED", errors)
    for key in ("claims_made", "supported_claims", "forbidden_claims_avoided", "required_caveats"):
        _require_s09_list(caption, "caption_legend_draft", key, "E_S11_CAPTION_BOUNDARY_REQUIRED", errors)
    if caption is not None:
        if caption.get("status") != "candidate":
            errors.append(issue("E_S11_CAPTION_BOUNDARY_REQUIRED", "caption_legend_draft.status must be candidate"))
        if caption.get("terminology_constraints_obeyed") is not True:
            errors.append(issue("E_S11_CAPTION_BOUNDARY_REQUIRED", "caption_legend_draft.terminology_constraints_obeyed must be true"))

    polish_policy = _require_mapping(payload, "visual_polish_policy", "E_S11_VISUAL_POLISH_POLICY_REQUIRED", errors)
    _require_s09_list(polish_policy, "visual_polish_policy", "priority_order", "E_S11_VISUAL_POLISH_POLICY_REQUIRED", errors)
    _require_s09_list(polish_policy, "visual_polish_policy", "allowed_changes", "E_S11_VISUAL_POLISH_POLICY_REQUIRED", errors)
    forbidden_changes = _require_s09_list(polish_policy, "visual_polish_policy", "forbidden_changes", "E_S11_VISUAL_POLISH_POLICY_REQUIRED", errors)
    missing_forbidden = sorted(S11_REQUIRED_FORBIDDEN_CHANGES - forbidden_changes)
    if missing_forbidden:
        errors.append(issue("E_S11_VISUAL_POLISH_POLICY_REQUIRED", f"visual_polish_policy.forbidden_changes missing {missing_forbidden}"))

    polish = _require_mapping(payload, "visual_polish_report", "E_S11_VISUAL_POLISH_REPORT_REQUIRED", errors)
    changes = polish.get("changes_made") if polish is not None else None
    if not is_non_empty_mapping_list(changes):
        errors.append(issue("E_S11_VISUAL_POLISH_REPORT_REQUIRED", "visual_polish_report.changes_made must be a non-empty list of mappings"))
    else:
        assert isinstance(changes, list)
        for idx, change in enumerate(changes):
            assert isinstance(change, dict)
            for key in ("change", "reason", "affected_contract_field"):
                if not is_non_empty_string(change.get(key)):
                    errors.append(issue("E_S11_VISUAL_POLISH_REPORT_REQUIRED", f"visual_polish_report.changes_made[{idx}].{key} must be a non-empty string"))
            for key in ("claim_meaning_changed", "evidence_encoding_changed", "proof_role_changed"):
                if change.get(key) is not False:
                    errors.append(issue("E_S11_VISUAL_POLISH_REPORT_REQUIRED", f"visual_polish_report.changes_made[{idx}].{key} must be false"))
    for key in ("readability_improvements", "accessibility_improvements", "style_consistency_improvements", "unresolved_visual_quality_risks"):
        _require_s09_list(polish, "visual_polish_report", key, "E_S11_VISUAL_POLISH_REPORT_REQUIRED", errors, allow_empty=key == "unresolved_visual_quality_risks")


def _validate_s11_integrity_accessibility_return(payload: dict[str, Any], packet_id: str, output_path: str, errors: list[ValidationIssue]) -> None:
    integrity = _require_mapping(payload, "image_integrity_record", "E_S11_IMAGE_INTEGRITY_REQUIRED", errors)
    _require_mapping_fields(integrity, "image_integrity_record", ["visual_id", "render_command", "integrity_status"], "E_S11_IMAGE_INTEGRITY_REQUIRED", errors)
    for key in ("rendered_files", "source_files", "data_files", "script_files", "hashes", "missing_assets"):
        _require_s09_list(integrity, "image_integrity_record", key, "E_S11_IMAGE_INTEGRITY_REQUIRED", errors, allow_empty=key in {"missing_assets", "rendered_files"})
    if integrity is not None and integrity.get("integrity_status") not in {"candidate_ok", "render_plan_recorded"}:
        errors.append(issue("E_S11_IMAGE_INTEGRITY_REQUIRED", "image_integrity_record.integrity_status must be candidate_ok or render_plan_recorded"))
    if integrity is not None and _s11_nature_direct_call_enabled(payload):
        _validate_s11_safe_paths(integrity.get("rendered_files"), "image_integrity_record.rendered_files", S11_NATURE_RENDER_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)
        _validate_s11_safe_paths(integrity.get("source_files"), "image_integrity_record.source_files", S11_NATURE_SOURCE_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)
        _validate_s11_safe_paths(integrity.get("data_files"), "image_integrity_record.data_files", S11_NATURE_DATA_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)
        _validate_s11_safe_paths(integrity.get("script_files"), "image_integrity_record.script_files", S11_NATURE_SCRIPT_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)

    stats = _require_mapping(payload, "figure_statistics", "E_S11_FIGURE_STATISTICS_REQUIRED", errors)
    _require_mapping_fields(stats, "figure_statistics", ["visual_id"], "E_S11_FIGURE_STATISTICS_REQUIRED", errors)
    for key in ("panel_count", "data_series_count", "baseline_count", "legend_entries"):
        _require_s08_count(stats, "figure_statistics", key, "E_S11_FIGURE_STATISTICS_REQUIRED", errors)
    for key in ("plotted_metrics", "axes", "units"):
        _require_s09_list(stats, "figure_statistics", key, "E_S11_FIGURE_STATISTICS_REQUIRED", errors)

    accessibility = _require_mapping(payload, "accessibility_check", "E_S11_ACCESSIBILITY_CHECK_REQUIRED", errors)
    _require_mapping_fields(accessibility, "accessibility_check", ["visual_id"], "E_S11_ACCESSIBILITY_CHECK_REQUIRED", errors)
    for key in (
        "readable_at_target_size",
        "colorblind_safe",
        "axes_and_units_clear",
        "legend_non_obstructive",
        "panel_labels_consistent",
        "uncertainty_visible_when_required",
        "caveats_not_removed",
        "export_quality_sufficient",
        "editable_source_available",
    ):
        if accessibility is not None and accessibility.get(key) is not True:
            errors.append(issue("E_S11_ACCESSIBILITY_CHECK_REQUIRED", f"accessibility_check.{key} must be true"))
    _require_s09_list(accessibility, "accessibility_check", "findings", "E_S11_ACCESSIBILITY_CHECK_REQUIRED", errors, allow_empty=True)

    export = _require_mapping(payload, "export_manifest", "E_S11_EXPORT_MANIFEST_REQUIRED", errors)
    _require_mapping_fields(export, "export_manifest", ["visual_id", "candidate_status"], "E_S11_EXPORT_MANIFEST_REQUIRED", errors)
    for key in ("export_files", "source_files", "data_files", "script_files", "target_formats"):
        _require_s09_list(export, "export_manifest", key, "E_S11_EXPORT_MANIFEST_REQUIRED", errors)
    if export is not None:
        if export.get("final_export_claimed") is not False:
            errors.append(issue("E_S11_EXPORT_MANIFEST_REQUIRED", "export_manifest.final_export_claimed must be false"))
        if export.get("candidate_status") != "candidate":
            errors.append(issue("E_S11_EXPORT_MANIFEST_REQUIRED", "export_manifest.candidate_status must be candidate"))
        if _s11_nature_direct_call_enabled(payload):
            _validate_s11_safe_paths(export.get("export_files"), "export_manifest.export_files", S11_NATURE_CANDIDATE_PREFIXES + S11_NATURE_RENDER_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)
            _validate_s11_safe_paths(export.get("source_files"), "export_manifest.source_files", S11_NATURE_SOURCE_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)
            _validate_s11_safe_paths(export.get("data_files"), "export_manifest.data_files", S11_NATURE_DATA_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)
            _validate_s11_safe_paths(export.get("script_files"), "export_manifest.script_files", S11_NATURE_SCRIPT_PREFIXES, "E_S11_NATURE_FIGURE_PATH_REQUIRED", errors)

    coverage = _require_mapping(payload, "coverage_ledger", "E_S11_COVERAGE_LEDGER_REQUIRED", errors)
    for key in (
        "target_visuals_required",
        "target_visuals_generated_or_planned",
        "required_panels",
        "panels_generated",
        "panels_with_claim_trace",
        "captions_required",
        "captions_drafted",
        "captions_with_claim_trace",
        "source_data_refs_required",
        "source_data_refs_traced",
        "editable_sources_required",
        "editable_sources_present",
        "rendered_outputs_required",
        "rendered_outputs_present_or_planned",
    ):
        _require_s08_count(coverage, "coverage_ledger", key, "E_S11_COVERAGE_LEDGER_REQUIRED", errors)
    _require_s09_list(coverage, "coverage_ledger", "unresolved_items", "E_S11_COVERAGE_LEDGER_REQUIRED", errors, allow_empty=True)
    if coverage is not None and coverage.get("unresolved_items"):
        errors.append(issue("E_S11_COVERAGE_LEDGER_REQUIRED", "coverage_ledger.unresolved_items must be empty for candidate output"))

    candidate_return = _require_mapping(payload, "candidate_artifact_return", "E_S11_CANDIDATE_RETURN_REQUIRED", errors)
    _require_mapping_fields(candidate_return, "candidate_artifact_return", ["schema_version", "return_id", "status", "packet_id", "output_artifact_path"], "E_S11_CANDIDATE_RETURN_REQUIRED", errors)
    for key in ("evidence", "validator_expectations", "remaining_risks"):
        _require_s09_list(candidate_return, "candidate_artifact_return", key, "E_S11_CANDIDATE_RETURN_REQUIRED", errors)
    if candidate_return is not None:
        if candidate_return.get("schema_version") != "ppg-candidate-return/v0.1" or candidate_return.get("status") != "candidate":
            errors.append(issue("E_S11_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return must use ppg-candidate-return/v0.1 candidate status"))
        if packet_id and candidate_return.get("packet_id") != packet_id:
            errors.append(issue("E_S11_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.packet_id must match packet"))
        if output_path and candidate_return.get("output_artifact_path") != output_path:
            errors.append(issue("E_S11_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.output_artifact_path must match allowed write path"))
        for key in ("graph_completion_claimed", "recursive_dispatch_requested", "writes_outside_allowed_paths"):
            if candidate_return.get(key) is not False:
                errors.append(issue("E_S11_CANDIDATE_RETURN_REQUIRED", f"candidate_artifact_return.{key} must be false"))

    verifier = _require_mapping(payload, "verifier_evidence", "E_S11_VERIFIER_EVIDENCE_REQUIRED", errors)
    _require_mapping_fields(verifier, "verifier_evidence", ["agent_type", "verification_status", "acceptance_recommendation"], "E_S11_VERIFIER_EVIDENCE_REQUIRED", errors)
    checks = _require_s09_list(verifier, "verifier_evidence", "checks_completed", "E_S11_VERIFIER_EVIDENCE_REQUIRED", errors)
    missing_checks = sorted(S11_REQUIRED_VERIFIER_CHECKS - checks)
    if missing_checks:
        errors.append(issue("E_S11_VERIFIER_EVIDENCE_REQUIRED", f"verifier_evidence.checks_completed missing {missing_checks}"))
    if verifier is not None:
        if verifier.get("agent_type") != "verifier":
            errors.append(issue("E_S11_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.agent_type must be verifier"))
        if verifier.get("verification_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S11_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.verification_status must be pass or pass_with_risks"))
    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S11_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))
    missing = _require_mapping(payload, "missing_material_report", "E_S11_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    _require_mapping_fields(missing, "missing_material_report", ["status", "backflow_target_if_blocked"], "E_S11_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    if missing is not None and missing.get("status") != "not_blocked":
        errors.append(issue("E_S11_MISSING_MATERIAL_REPORT_REQUIRED", "missing_material_report.status must be not_blocked for candidate output"))


def _validate_s11_figure_caption_artifact_bundle(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s11_payload_header(payload, "ppg-s11-figure-caption-artifact-bundle/v0.1", "E_S11_ARTIFACT_BUNDLE_REQUIRED", errors)
    _require_s11_required_modules(payload, errors)
    packet_id, output_path = _validate_s11_authority_and_packet(payload, errors)
    _validate_s11_nature_figure_direct_call(payload, errors)
    _validate_s11_contract_and_artifacts(payload, errors)
    _validate_s11_traces_caption_and_quality(payload, errors)
    _validate_s11_integrity_accessibility_return(payload, packet_id, output_path, errors)


def _require_s12_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary",
        "module_inventory",
        "assembly_manifest",
        "integrated_manuscript_candidate",
        "trace_index",
        "claim_boundary_audit",
        "promise_satisfaction_report",
        "cross_section_consistency_report",
        "terminology_consistency_report",
        "object_granularity_consistency_report",
        "figure_text_alignment_report",
        "surface_consistency_report",
        "stale_material_report",
        "integration_findings",
        "backflow_queue",
        "validator_report",
        "candidate_artifact_return",
        "remaining_risks",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        errors.append(issue("E_S12_INTEGRATION_REPORT_REQUIRED", f"S12IntegrationConsistencyReport missing required modules: {missing}"))


def _validate_s12_authority(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[str, str]:
    _require_s12_payload_header(payload, "ppg-s12-integration-consistency-report/v0.1", "E_S12_INTEGRATION_REPORT_REQUIRED", errors)
    if payload.get("completion_boundary") != S12_COMPLETION_BOUNDARY:
        errors.append(issue("E_S12_COMPLETION_BOUNDARY", f"completion_boundary must be {S12_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S12_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S12_NO_COMPLETION_OVERCLAIM", f"S12 integration report must not contain completion field {completion_key!r}"))
    boundary = _require_mapping(payload, "authority_boundary", "E_S12_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "final_pdf_exported",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "uncontrolled_rewrite_performed",
        "claim_boundaries_changed",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S12_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S12_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))
    candidate_return = as_mapping(payload.get("candidate_artifact_return"))
    packet_id = str(candidate_return.get("packet_id") or "") if candidate_return else ""
    output_path = str(candidate_return.get("output_artifact_path") or "") if candidate_return else ""
    return packet_id, output_path


def _validate_s12_inventory_and_candidate(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    inventory = _require_mapping(payload, "module_inventory", "E_S12_MODULE_INVENTORY_REQUIRED", errors)
    text_modules = inventory.get("text_modules") if inventory is not None else None
    visual_modules = inventory.get("visual_modules") if inventory is not None else None
    if not is_non_empty_mapping_list(text_modules):
        errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", "module_inventory.text_modules must be a non-empty list"))
    else:
        assert isinstance(text_modules, list)
        for idx, item in enumerate(text_modules):
            assert isinstance(item, dict)
            for key in ("module_id", "section_id", "source_s10_packet", "output_path", "status"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", f"module_inventory.text_modules[{idx}].{key} must be a non-empty string"))
            if item.get("trace_available") is not True:
                errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", f"module_inventory.text_modules[{idx}].trace_available must be true"))
    if not is_non_empty_mapping_list(visual_modules):
        errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", "module_inventory.visual_modules must be a non-empty list"))
    else:
        assert isinstance(visual_modules, list)
        for idx, item in enumerate(visual_modules):
            assert isinstance(item, dict)
            for key in ("visual_id", "source_s11_packet", "figure_contract", "status"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", f"module_inventory.visual_modules[{idx}].{key} must be a non-empty string"))
            for key in ("caption_available", "panel_trace_available"):
                if item.get(key) is not True:
                    errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", f"module_inventory.visual_modules[{idx}].{key} must be true"))
    for key in ("missing_modules", "duplicate_modules", "stale_modules"):
        _require_s09_list(inventory, "module_inventory", key, "E_S12_MODULE_INVENTORY_REQUIRED", errors, allow_empty=True)
        if inventory is not None and inventory.get(key):
            errors.append(issue("E_S12_MODULE_INVENTORY_REQUIRED", f"module_inventory.{key} must be empty before S13 review"))

    manifest = _require_mapping(payload, "assembly_manifest", "E_S12_ASSEMBLY_MANIFEST_REQUIRED", errors)
    _require_mapping_fields(manifest, "assembly_manifest", ["manuscript_candidate_id"], "E_S12_ASSEMBLY_MANIFEST_REQUIRED", errors)
    if manifest is not None and manifest.get("final_manuscript_claimed") is not False:
        errors.append(issue("E_S12_ASSEMBLY_MANIFEST_REQUIRED", "assembly_manifest.final_manuscript_claimed must be false"))
    if not is_non_empty_mapping_list(manifest.get("assembly_order") if manifest else None):
        errors.append(issue("E_S12_ASSEMBLY_MANIFEST_REQUIRED", "assembly_manifest.assembly_order must be a non-empty list"))
    for key in ("source_module_versions", "assembly_decisions", "excluded_modules"):
        _require_s09_list(manifest, "assembly_manifest", key, "E_S12_ASSEMBLY_MANIFEST_REQUIRED", errors, allow_empty=key == "excluded_modules")

    candidate = _require_mapping(payload, "integrated_manuscript_candidate", "E_S12_INTEGRATED_CANDIDATE_REQUIRED", errors)
    _require_mapping_fields(candidate, "integrated_manuscript_candidate", ["candidate_id", "source_format", "main_source_candidate", "trace_index_ref", "unresolved_findings_ref"], "E_S12_INTEGRATED_CANDIDATE_REQUIRED", errors)
    for key in ("section_sources", "figure_refs", "table_refs", "formula_algorithm_refs", "bibliography_refs"):
        _require_s09_list(candidate, "integrated_manuscript_candidate", key, "E_S12_INTEGRATED_CANDIDATE_REQUIRED", errors, allow_empty=key in {"table_refs", "formula_algorithm_refs"})
    if candidate is not None:
        if candidate.get("ready_for_s13_review") is not True:
            errors.append(issue("E_S12_INTEGRATED_CANDIDATE_REQUIRED", "integrated_manuscript_candidate.ready_for_s13_review must be true for this fixture"))
        if candidate.get("ready_for_s16_export") is not False:
            errors.append(issue("E_S12_NO_PDF_EXPORT", "integrated_manuscript_candidate.ready_for_s16_export must be false"))
        if candidate.get("final_manuscript_claimed") is not False:
            errors.append(issue("E_S12_NO_FINAL_MANUSCRIPT", "integrated_manuscript_candidate.final_manuscript_claimed must be false"))


def _validate_s12_trace_and_audits(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    trace = _require_mapping(payload, "trace_index", "E_S12_TRACE_INDEX_REQUIRED", errors)
    for key in ("claim_trace_index", "object_trace_index", "terminology_trace_index", "figure_trace_index"):
        if not is_non_empty_mapping_list(trace.get(key) if trace else None):
            errors.append(issue("E_S12_TRACE_INDEX_REQUIRED", f"trace_index.{key} must be a non-empty list"))

    claim = _require_mapping(payload, "claim_boundary_audit", "E_S12_CLAIM_BOUNDARY_AUDIT_REQUIRED", errors)
    for key in ("traced_claims", "recommended_backflow"):
        _require_s09_list(claim, "claim_boundary_audit", key, "E_S12_CLAIM_BOUNDARY_AUDIT_REQUIRED", errors)
    for key in ("untraced_claims", "strengthened_claims", "forbidden_wording_hits", "missing_caveats", "caption_claim_mismatches", "conclusion_overreach"):
        _require_s09_list(claim, "claim_boundary_audit", key, "E_S12_CLAIM_BOUNDARY_AUDIT_REQUIRED", errors, allow_empty=True)
        if claim is not None and claim.get(key):
            errors.append(issue("E_S12_CLAIM_BOUNDARY_AUDIT_REQUIRED", f"claim_boundary_audit.{key} must be empty before S13 review"))

    promise = payload.get("promise_satisfaction_report")
    if not is_non_empty_mapping_list(promise):
        errors.append(issue("E_S12_PROMISE_SATISFACTION_REQUIRED", "promise_satisfaction_report must be a non-empty list"))
    else:
        assert isinstance(promise, list)
        for idx, item in enumerate(promise):
            assert isinstance(item, dict)
            for key in ("promise_id", "introduced_where", "expected_payoff", "actual_payoff_location", "backflow_target"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S12_PROMISE_SATISFACTION_REQUIRED", f"promise_satisfaction_report[{idx}].{key} must be a non-empty string"))
            for key in ("satisfied",):
                if item.get(key) is not True:
                    errors.append(issue("E_S12_PROMISE_SATISFACTION_REQUIRED", f"promise_satisfaction_report[{idx}].{key} must be true"))
            for key in ("overpromised", "underdeveloped"):
                if item.get(key) is not False:
                    errors.append(issue("E_S12_PROMISE_SATISFACTION_REQUIRED", f"promise_satisfaction_report[{idx}].{key} must be false"))

    for field, code in (
        ("cross_section_consistency_report", "E_S12_CROSS_SECTION_CONSISTENCY_REQUIRED"),
        ("terminology_consistency_report", "E_S12_TERMINOLOGY_CONSISTENCY_REQUIRED"),
        ("object_granularity_consistency_report", "E_S12_OBJECT_GRANULARITY_CONSISTENCY_REQUIRED"),
        ("figure_text_alignment_report", "E_S12_FIGURE_TEXT_ALIGNMENT_REQUIRED"),
        ("surface_consistency_report", "E_S12_SURFACE_CONSISTENCY_REQUIRED"),
    ):
        report = _require_mapping(payload, field, code, errors)
        _require_s09_list(report, field, "repair_targets", code, errors, allow_empty=True)
        if report is not None and report.get("pass") is not True:
            errors.append(issue(code, f"{field}.pass must be true or findings must block S13"))

    stale = _require_mapping(payload, "stale_material_report", "E_S12_STALE_MATERIAL_REPORT_REQUIRED", errors)
    for key in ("stale_s09b_packets", "stale_s10_candidates", "stale_s11_artifacts", "upstream_material_changed", "affected_downstream_nodes"):
        _require_s09_list(stale, "stale_material_report", key, "E_S12_STALE_MATERIAL_REPORT_REQUIRED", errors, allow_empty=True)
    if stale is not None:
        if stale.get("requires_recompile") is not False or stale.get("requires_regeneration") is not False:
            errors.append(issue("E_S12_STALE_MATERIAL_REPORT_REQUIRED", "stale_material_report must not require recompile/regeneration before S13 review"))


def _validate_s12_findings_return(payload: dict[str, Any], packet_id: str, output_path: str, errors: list[ValidationIssue]) -> None:
    findings = payload.get("integration_findings")
    if not is_non_empty_mapping_list(findings):
        errors.append(issue("E_S12_INTEGRATION_FINDINGS_REQUIRED", "integration_findings must be a non-empty list"))
    else:
        assert isinstance(findings, list)
        for idx, finding in enumerate(findings):
            assert isinstance(finding, dict)
            for key in ("finding_id", "finding_type", "severity", "source_trace", "nearest_responsible_stage", "recommended_backflow_target", "suggested_repair_scope"):
                if not is_non_empty_string(finding.get(key)):
                    errors.append(issue("E_S12_INTEGRATION_FINDINGS_REQUIRED", f"integration_findings[{idx}].{key} must be a non-empty string"))
            for key in ("affected_artifacts", "evidence"):
                _require_s08_string_items(finding, f"integration_findings[{idx}]", key, "E_S12_INTEGRATION_FINDINGS_REQUIRED", errors)
            if finding.get("recommended_backflow_target") not in S12_BACKFLOW_TARGETS:
                errors.append(issue("E_S12_INTEGRATION_FINDINGS_REQUIRED", f"integration_findings[{idx}].recommended_backflow_target invalid"))
            if finding.get("severity") in {"high", "blocker"} and finding.get("blocks_s13_review") is not True:
                errors.append(issue("E_S12_INTEGRATION_FINDINGS_REQUIRED", f"integration_findings[{idx}] high/blocker findings must block S13"))

    queue = payload.get("backflow_queue")
    if not is_non_empty_mapping_list(queue):
        errors.append(issue("E_S12_BACKFLOW_QUEUE_REQUIRED", "backflow_queue must be a non-empty list"))
    else:
        assert isinstance(queue, list)
        for idx, item in enumerate(queue):
            assert isinstance(item, dict)
            for key in ("queue_id", "target_stage", "target_material", "repair_type", "preserve_scope", "priority"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S12_BACKFLOW_QUEUE_REQUIRED", f"backflow_queue[{idx}].{key} must be a non-empty string"))
            _require_s08_string_items(item, f"backflow_queue[{idx}]", "finding_refs", "E_S12_BACKFLOW_QUEUE_REQUIRED", errors)
            _require_s08_string_items(item, f"backflow_queue[{idx}]", "affected_downstream_nodes", "E_S12_BACKFLOW_QUEUE_REQUIRED", errors)
            if item.get("target_stage") not in S12_BACKFLOW_TARGETS:
                errors.append(issue("E_S12_BACKFLOW_QUEUE_REQUIRED", f"backflow_queue[{idx}].target_stage invalid"))

    validator = _require_mapping(payload, "validator_report", "E_S12_VALIDATOR_REPORT_REQUIRED", errors)
    for key in ("cross_section_consistency", "figure_text_alignment", "promise_satisfaction", "claim_boundary_compliance", "terminology_consistency", "object_granularity_consistency", "surface_consistency", "stale_material_check"):
        if validator is not None and validator.get(key) not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S12_VALIDATOR_REPORT_REQUIRED", f"validator_report.{key} must be pass or pass_with_risks"))
    if validator is not None:
        if validator.get("pass_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S12_VALIDATOR_REPORT_REQUIRED", "validator_report.pass_status must be pass or pass_with_risks"))
        if validator.get("blocks_s13_review") is not False:
            errors.append(issue("E_S12_VALIDATOR_REPORT_REQUIRED", "validator_report.blocks_s13_review must be false for this fixture"))

    candidate_return = _require_mapping(payload, "candidate_artifact_return", "E_S12_CANDIDATE_RETURN_REQUIRED", errors)
    _require_mapping_fields(candidate_return, "candidate_artifact_return", ["schema_version", "return_id", "status", "packet_id", "output_artifact_path"], "E_S12_CANDIDATE_RETURN_REQUIRED", errors)
    for key in ("evidence", "validator_expectations", "remaining_risks"):
        _require_s09_list(candidate_return, "candidate_artifact_return", key, "E_S12_CANDIDATE_RETURN_REQUIRED", errors)
    if candidate_return is not None:
        if candidate_return.get("schema_version") != "ppg-candidate-return/v0.1" or candidate_return.get("status") != "candidate":
            errors.append(issue("E_S12_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return must use ppg-candidate-return/v0.1 candidate status"))
        if packet_id and candidate_return.get("packet_id") != packet_id:
            errors.append(issue("E_S12_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.packet_id must match packet"))
        if output_path and candidate_return.get("output_artifact_path") != output_path:
            errors.append(issue("E_S12_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.output_artifact_path must match output path"))
        for key in ("graph_completion_claimed", "recursive_dispatch_requested", "writes_outside_allowed_paths"):
            if candidate_return.get(key) is not False:
                errors.append(issue("E_S12_CANDIDATE_RETURN_REQUIRED", f"candidate_artifact_return.{key} must be false"))
    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S12_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))


def _validate_s12_integration_consistency_report(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s12_required_modules(payload, errors)
    packet_id, output_path = _validate_s12_authority(payload, errors)
    _validate_s12_inventory_and_candidate(payload, errors)
    _validate_s12_trace_and_audits(payload, errors)
    _validate_s12_findings_return(payload, packet_id, output_path, errors)


def _require_s13_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary",
        "review_scope",
        "review_object_inventory",
        "reviewer_panel_report",
        "desk_reject_risk_report",
        "reader_experience_report",
        "claim_evidence_review",
        "contribution_significance_review",
        "method_result_review",
        "figure_caption_review",
        "structure_argument_review",
        "surface_accessibility_review",
        "review_findings",
        "finding_actionability_report",
        "validator_report",
        "candidate_artifact_return",
        "verifier_evidence",
        "remaining_risks",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        errors.append(issue("E_S13_ADVERSARIAL_REVIEW_REQUIRED", f"S13AdversarialReviewReport missing required modules: {missing}"))


def _validate_s13_authority(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[str, str]:
    _require_s13_payload_header(payload, "ppg-s13-adversarial-review-report/v0.1", "E_S13_ADVERSARIAL_REVIEW_REQUIRED", errors)
    if payload.get("completion_boundary") != S13_COMPLETION_BOUNDARY:
        errors.append(issue("E_S13_COMPLETION_BOUNDARY", f"completion_boundary must be {S13_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S13_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S13_NO_COMPLETION_OVERCLAIM", f"S13 adversarial review must not contain completion field {completion_key!r}"))
    boundary = _require_mapping(payload, "authority_boundary", "E_S13_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "pdf_review_claimed",
        "pdf_exported",
        "repair_executed",
        "uncontrolled_rewrite_performed",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "recursive_dispatch_requested",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S13_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S13_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))
    candidate_return = as_mapping(payload.get("candidate_artifact_return"))
    packet_id = str(candidate_return.get("packet_id") or "") if candidate_return else ""
    output_path = str(candidate_return.get("output_artifact_path") or "") if candidate_return else ""
    return packet_id, output_path


def _validate_s13_scope_and_inventory(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    scope = _require_mapping(payload, "review_scope", "E_S13_REVIEW_SCOPE_REQUIRED", errors)
    modes = _require_s09_list(scope, "review_scope", "review_modes", "E_S13_REVIEW_SCOPE_REQUIRED", errors)
    missing_modes = sorted(S13_REVIEW_MODES - modes)
    if missing_modes:
        errors.append(issue("E_S13_REVIEW_SCOPE_REQUIRED", f"review_scope.review_modes missing {missing_modes}"))
    for key in ("target_sections", "target_figures", "excluded_scope"):
        _require_s09_list(scope, "review_scope", key, "E_S13_REVIEW_SCOPE_REQUIRED", errors, allow_empty=key == "excluded_scope")
    if scope is not None and scope.get("full_integrated_candidate") is not True:
        errors.append(issue("E_S13_REVIEW_SCOPE_REQUIRED", "review_scope.full_integrated_candidate must be true for this fixture"))

    inventory = _require_mapping(payload, "review_object_inventory", "E_S13_REVIEW_OBJECT_INVENTORY_REQUIRED", errors)
    _require_mapping_fields(
        inventory,
        "review_object_inventory",
        ["integrated_candidate_ref", "s12_report_ref", "trace_index_ref"],
        "E_S13_REVIEW_OBJECT_INVENTORY_REQUIRED",
        errors,
    )
    for key in ("text_modules", "figure_bundles", "trace_indexes", "upstream_controls", "missing_review_materials"):
        _require_s09_list(inventory, "review_object_inventory", key, "E_S13_REVIEW_OBJECT_INVENTORY_REQUIRED", errors, allow_empty=key == "missing_review_materials")
    if inventory is not None:
        if inventory.get("blocked") is not False:
            errors.append(issue("E_S13_REVIEW_OBJECT_INVENTORY_REQUIRED", "review_object_inventory.blocked must be false"))
        if inventory.get("primary_object_is_pdf") is not False:
            errors.append(issue("E_S13_NO_PDF_PRIMARY_REVIEW", "review_object_inventory.primary_object_is_pdf must be false"))
        if inventory.get("s16_pdf_export_ref") not in ("none", None, ""):
            errors.append(issue("E_S13_NO_PDF_PRIMARY_REVIEW", "review_object_inventory.s16_pdf_export_ref must be none/empty during S13"))


def _validate_s13_reports(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    panel = _require_mapping(payload, "reviewer_panel_report", "E_S13_REVIEWER_PANEL_REQUIRED", errors)
    reviewers = panel.get("reviewers") if panel else None
    if not is_non_empty_mapping_list(reviewers):
        errors.append(issue("E_S13_REVIEWER_PANEL_REQUIRED", "reviewer_panel_report.reviewers must be a non-empty list"))
    else:
        assert isinstance(reviewers, list)
        roles: set[str] = set()
        for idx, reviewer in enumerate(reviewers):
            assert isinstance(reviewer, dict)
            for key in ("reviewer_role", "severity"):
                if not is_non_empty_string(reviewer.get(key)):
                    errors.append(issue("E_S13_REVIEWER_PANEL_REQUIRED", f"reviewer_panel_report.reviewers[{idx}].{key} must be a non-empty string"))
            role = reviewer.get("reviewer_role")
            if isinstance(role, str):
                roles.add(role)
            if reviewer.get("severity") not in S13_ALLOWED_SEVERITIES:
                errors.append(issue("E_S13_REVIEWER_PANEL_REQUIRED", f"reviewer_panel_report.reviewers[{idx}].severity invalid"))
            for key in ("likely_concerns", "evidence_refs", "affected_artifacts"):
                _require_s08_string_items(reviewer, f"reviewer_panel_report.reviewers[{idx}]", key, "E_S13_REVIEWER_PANEL_REQUIRED", errors)
        missing_roles = sorted(S13_REVIEWER_ROLES - roles)
        if missing_roles:
            errors.append(issue("E_S13_REVIEWER_PANEL_REQUIRED", f"reviewer_panel_report missing reviewer roles {missing_roles}"))

    desk = _require_mapping(payload, "desk_reject_risk_report", "E_S13_DESK_REJECT_RISK_REQUIRED", errors)
    _require_mapping_fields(desk, "desk_reject_risk_report", ["severity", "summary"], "E_S13_DESK_REJECT_RISK_REQUIRED", errors)
    for key in ("scope_mismatch", "novelty_underdeveloped", "claim_evidence_gap", "unclear_contribution", "overclaim_in_abstract_or_intro", "figure_quality_or_caption_risk", "missing_data_availability_signal", "readability_or_structure_risk"):
        _require_s09_list(desk, "desk_reject_risk_report", key, "E_S13_DESK_REJECT_RISK_REQUIRED", errors, allow_empty=True)
    if desk is not None and desk.get("severity") not in S13_ALLOWED_SEVERITIES:
        errors.append(issue("E_S13_DESK_REJECT_RISK_REQUIRED", "desk_reject_risk_report.severity invalid"))

    for field, code, keys in (
        ("reader_experience_report", "E_S13_READER_EXPERIENCE_REQUIRED", ("reader_path_breaks", "missing_definitions", "cognitive_load_spikes", "unclear_object_transitions", "repeated_or_flat_explanations", "figure_callout_confusion", "section_purpose_confusion")),
        ("claim_evidence_review", "E_S13_CLAIM_EVIDENCE_REVIEW_REQUIRED", ("unsupported_claims", "overstrengthened_claims", "ambiguous_claims", "missing_caveats", "evidence_visibility_gaps", "likely_reviewer_attacks")),
        ("contribution_significance_review", "E_S13_CONTRIBUTION_REVIEW_REQUIRED", ("underdeveloped_contributions", "novelty_risk_cases", "missing_positioning", "reviewer_questions")),
        ("method_result_review", "E_S13_METHOD_RESULT_REVIEW_REQUIRED", ("method_result_mismatches", "evaluation_sufficiency_risks", "baseline_or_ablation_gaps", "threats_to_validity")),
        ("figure_caption_review", "E_S13_FIGURE_CAPTION_REVIEW_REQUIRED", ("visual_claim_mismatches", "caption_overclaims", "schematic_as_evidence_cases", "missing_panel_explanation", "unreadable_visual_elements", "figure_text_alignment_risks", "legend_or_axis_confusion")),
        ("structure_argument_review", "E_S13_STRUCTURE_ARGUMENT_REVIEW_REQUIRED", ("argument_path_breaks", "section_order_risks", "promise_payoff_gaps", "transition_failures")),
        ("surface_accessibility_review", "E_S13_SURFACE_ACCESSIBILITY_REQUIRED", ("terminology_drift", "internal_id_leakage", "rigid_template_language", "register_mismatch", "accessibility_risks")),
    ):
        report = _require_mapping(payload, field, code, errors)
        for key in keys:
            _require_s09_list(report, field, key, code, errors, allow_empty=True)


def _validate_s13_findings(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    findings = payload.get("review_findings")
    finding_ids: list[str] = []
    if not is_non_empty_mapping_list(findings):
        errors.append(issue("E_S13_REVIEW_FINDINGS_REQUIRED", "review_findings must be a non-empty list"))
    else:
        assert isinstance(findings, list)
        for idx, finding in enumerate(findings):
            assert isinstance(finding, dict)
            for key in (
                "finding_id",
                "finding_type",
                "severity",
                "affected_artifact",
                "affected_location",
                "reviewer_rationale",
                "nearest_responsible_stage",
                "recommended_backflow_target",
                "suggested_repair_scope",
                "resolution_status",
            ):
                if not is_non_empty_string(finding.get(key)):
                    errors.append(issue("E_S13_REVIEW_FINDINGS_REQUIRED", f"review_findings[{idx}].{key} must be a non-empty string"))
            if is_non_empty_string(finding.get("finding_id")):
                finding_ids.append(str(finding["finding_id"]))
            for key in ("evidence", "source_trace"):
                _require_s08_string_items(finding, f"review_findings[{idx}]", key, "E_S13_REVIEW_FINDINGS_REQUIRED", errors)
            if finding.get("severity") not in S13_ALLOWED_SEVERITIES:
                errors.append(issue("E_S13_REVIEW_FINDINGS_REQUIRED", f"review_findings[{idx}].severity invalid"))
            if finding.get("nearest_responsible_stage") not in S13_NEAREST_RESPONSIBLE_STAGES:
                errors.append(issue("E_S13_REVIEW_FINDINGS_REQUIRED", f"review_findings[{idx}].nearest_responsible_stage invalid"))
            if finding.get("recommended_backflow_target") != "S14":
                errors.append(issue("E_S13_BACKFLOW_TARGET_REQUIRED", f"review_findings[{idx}].recommended_backflow_target must be S14"))
            if finding.get("resolution_status") != "open":
                errors.append(issue("E_S13_REVIEW_FINDINGS_REQUIRED", f"review_findings[{idx}].resolution_status must be open"))
            if finding.get("repair_executed") is not False:
                errors.append(issue("E_S13_NO_REPAIR_EXECUTION", f"review_findings[{idx}].repair_executed must be false"))
            if finding.get("rewrite_requested") is not False:
                errors.append(issue("E_S13_NO_UNCONTROLLED_REWRITE", f"review_findings[{idx}].rewrite_requested must be false"))
            if not isinstance(finding.get("blocks_progression"), bool):
                errors.append(issue("E_S13_REVIEW_FINDINGS_REQUIRED", f"review_findings[{idx}].blocks_progression must be boolean"))
            repair_scope = str(finding.get("suggested_repair_scope") or "").lower()
            if "whole manuscript" in repair_scope or "rewrite entire" in repair_scope or "rewrite the entire" in repair_scope:
                errors.append(issue("E_S13_NO_UNCONTROLLED_REWRITE", f"review_findings[{idx}].suggested_repair_scope must be local"))
    if len(finding_ids) != len(set(finding_ids)):
        errors.append(issue("E_S13_ACTIONABILITY_REQUIRED", "review_findings finding_id values must be unique after duplicate merge"))

    actionability = _require_mapping(payload, "finding_actionability_report", "E_S13_ACTIONABILITY_REQUIRED", errors)
    for key in ("actionable_findings", "vague_findings_rejected", "duplicate_findings_merged", "findings_needing_owner_interpretation", "findings_needing_more_evidence", "findings_ready_for_s14"):
        _require_s09_list(actionability, "finding_actionability_report", key, "E_S13_ACTIONABILITY_REQUIRED", errors, allow_empty=key != "findings_ready_for_s14")
    if actionability is not None and finding_ids:
        ready = set(_s08_string_items(actionability.get("findings_ready_for_s14")))
        missing_ready = sorted(set(finding_ids) - ready)
        if missing_ready:
            errors.append(issue("E_S13_ACTIONABILITY_REQUIRED", f"finding_actionability_report.findings_ready_for_s14 missing {missing_ready}"))


def _validate_s13_validator_return(payload: dict[str, Any], packet_id: str, output_path: str, errors: list[ValidationIssue]) -> None:
    validator = _require_mapping(payload, "validator_report", "E_S13_VALIDATOR_REPORT_REQUIRED", errors)
    for key in (
        "review_object_inventory",
        "review_scope",
        "reviewer_panel_report",
        "desk_reject_risk_report",
        "reader_experience_report",
        "claim_evidence_review",
        "figure_caption_review",
        "review_findings_schema",
        "finding_actionability",
        "backflow_target_validity",
        "no_uncontrolled_rewrite",
        "no_pdf_primary_review",
        "candidate_return_complete",
    ):
        if validator is not None and validator.get(key) not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S13_VALIDATOR_REPORT_REQUIRED", f"validator_report.{key} must be pass or pass_with_risks"))
    if validator is not None:
        if validator.get("pass_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S13_VALIDATOR_REPORT_REQUIRED", "validator_report.pass_status must be pass or pass_with_risks"))
        if validator.get("recommended_next_stage") != "S14":
            errors.append(issue("E_S13_VALIDATOR_REPORT_REQUIRED", "validator_report.recommended_next_stage must be S14"))

    candidate_return = _require_mapping(payload, "candidate_artifact_return", "E_S13_CANDIDATE_RETURN_REQUIRED", errors)
    _require_mapping_fields(candidate_return, "candidate_artifact_return", ["schema_version", "return_id", "status", "packet_id", "output_artifact_path"], "E_S13_CANDIDATE_RETURN_REQUIRED", errors)
    for key in ("evidence", "validator_expectations", "remaining_risks"):
        _require_s09_list(candidate_return, "candidate_artifact_return", key, "E_S13_CANDIDATE_RETURN_REQUIRED", errors)
    if candidate_return is not None:
        if candidate_return.get("schema_version") != "ppg-candidate-return/v0.1" or candidate_return.get("status") != "candidate":
            errors.append(issue("E_S13_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return must use ppg-candidate-return/v0.1 candidate status"))
        if packet_id and candidate_return.get("packet_id") != packet_id:
            errors.append(issue("E_S13_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.packet_id must match packet"))
        if output_path and candidate_return.get("output_artifact_path") != output_path:
            errors.append(issue("E_S13_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.output_artifact_path must match output path"))
        for key in ("graph_completion_claimed", "recursive_dispatch_requested", "writes_outside_allowed_paths"):
            if candidate_return.get(key) is not False:
                errors.append(issue("E_S13_CANDIDATE_RETURN_REQUIRED", f"candidate_artifact_return.{key} must be false"))

    verifier = _require_mapping(payload, "verifier_evidence", "E_S13_VERIFIER_EVIDENCE_REQUIRED", errors)
    _require_mapping_fields(verifier, "verifier_evidence", ["agent_type", "verification_status", "recommended_next_stage"], "E_S13_VERIFIER_EVIDENCE_REQUIRED", errors)
    checks = _require_s09_list(verifier, "verifier_evidence", "checks_completed", "E_S13_VERIFIER_EVIDENCE_REQUIRED", errors)
    missing_checks = sorted(S13_REQUIRED_VERIFIER_CHECKS - checks)
    if missing_checks:
        errors.append(issue("E_S13_VERIFIER_EVIDENCE_REQUIRED", f"verifier_evidence.checks_completed missing {missing_checks}"))
    for key in ("accepted_findings", "rejected_or_vague_findings", "duplicate_merge_notes", "routing_corrections"):
        _require_s09_list(verifier, "verifier_evidence", key, "E_S13_VERIFIER_EVIDENCE_REQUIRED", errors, allow_empty=key != "accepted_findings")
    if verifier is not None:
        if verifier.get("agent_type") != "verifier":
            errors.append(issue("E_S13_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.agent_type must be verifier"))
        if verifier.get("verification_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S13_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.verification_status must be pass or pass_with_risks"))
        if verifier.get("recommended_next_stage") != "S14":
            errors.append(issue("E_S13_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.recommended_next_stage must be S14"))
    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S13_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))


def _validate_s13_adversarial_review_report(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s13_required_modules(payload, errors)
    packet_id, output_path = _validate_s13_authority(payload, errors)
    _validate_s13_scope_and_inventory(payload, errors)
    _validate_s13_reports(payload, errors)
    _validate_s13_findings(payload, errors)
    _validate_s13_validator_return(payload, packet_id, output_path, errors)


def _require_s14_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary",
        "finding_intake_ledger",
        "finding_normalization_table",
        "nearest_responsible_stage_map",
        "affected_material_graph_slice",
        "repair_scope_plan",
        "repair_task_packets",
        "control_reselection_tasks",
        "response_action_map",
        "priority_schedule",
        "owner_gate_report",
        "validation_plan",
        "unresolved_or_ambiguous_findings",
        "validator_report",
        "remaining_risks",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        errors.append(issue("E_S14_BACKFLOW_PLAN_REQUIRED", f"S14BackflowRepairPlan missing required modules: {missing}"))


def _validate_s14_authority(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s14_payload_header(payload, "ppg-s14-backflow-repair-plan/v0.1", "E_S14_BACKFLOW_PLAN_REQUIRED", errors)
    if payload.get("completion_boundary") != S14_COMPLETION_BOUNDARY:
        errors.append(issue("E_S14_COMPLETION_BOUNDARY", f"completion_boundary must be {S14_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S14_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S14_NO_COMPLETION_OVERCLAIM", f"S14 backflow plan must not contain completion field {completion_key!r}"))
    boundary = _require_mapping(payload, "authority_boundary", "E_S14_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "pdf_exported",
        "repair_executed",
        "finding_resolution_claimed",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "fake_worker_task_packet_created",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S14_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S14_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))


def _validate_s14_intake_and_normalization(payload: dict[str, Any], errors: list[ValidationIssue]) -> set[str]:
    ledger = _require_mapping(payload, "finding_intake_ledger", "E_S14_FINDING_INTAKE_REQUIRED", errors)
    for key in ("total_findings", "accepted", "rejected_with_reason", "duplicate", "owner_gated", "unresolved_or_ambiguous"):
        _require_s08_count(ledger, "finding_intake_ledger", key, "E_S14_FINDING_INTAKE_REQUIRED", errors)
    all_ids = _require_s09_list(ledger, "finding_intake_ledger", "all_input_finding_ids", "E_S14_FINDING_INTAKE_REQUIRED", errors)
    accepted_ids = _require_s09_list(ledger, "finding_intake_ledger", "accepted_finding_ids", "E_S14_FINDING_INTAKE_REQUIRED", errors)
    if ledger is not None:
        if ledger.get("source_stage") not in {"S13", "S16-human-feedback", "validator", "owner"}:
            errors.append(issue("E_S14_FINDING_INTAKE_REQUIRED", "finding_intake_ledger.source_stage invalid"))
        if ledger.get("activation_reason") not in {"review_finding_exists", "validator_failure", "human_feedback_after_s16", "regression_after_s15"}:
            errors.append(issue("E_S14_FINDING_INTAKE_REQUIRED", "finding_intake_ledger.activation_reason invalid"))
        if accepted_ids and not accepted_ids <= all_ids:
            errors.append(issue("E_S14_FINDING_INTAKE_COVERAGE", "accepted_finding_ids must be a subset of all_input_finding_ids"))

    normalization = payload.get("finding_normalization_table")
    normalized_ids: set[str] = set()
    if not is_non_empty_mapping_list(normalization):
        errors.append(issue("E_S14_FINDING_NORMALIZATION_REQUIRED", "finding_normalization_table must be a non-empty list"))
    else:
        assert isinstance(normalization, list)
        for idx, item in enumerate(normalization):
            assert isinstance(item, dict)
            for key in ("finding_id", "normalized_problem", "original_text_ref", "failure_type", "severity", "acceptance_status"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S14_FINDING_NORMALIZATION_REQUIRED", f"finding_normalization_table[{idx}].{key} must be a non-empty string"))
            if is_non_empty_string(item.get("finding_id")):
                normalized_ids.add(str(item["finding_id"]))
            if item.get("failure_type") not in S14_FAILURE_TYPES:
                errors.append(issue("E_S14_FAILURE_TYPE_REQUIRED", f"finding_normalization_table[{idx}].failure_type invalid"))
            if item.get("severity") not in S13_ALLOWED_SEVERITIES:
                errors.append(issue("E_S14_FINDING_NORMALIZATION_REQUIRED", f"finding_normalization_table[{idx}].severity invalid"))
            if item.get("acceptance_status") not in S14_ACCEPTANCE_STATUSES:
                errors.append(issue("E_S14_FINDING_NORMALIZATION_REQUIRED", f"finding_normalization_table[{idx}].acceptance_status invalid"))
            if item.get("acceptance_status") in {"rejected", "duplicate", "owner_gated", "ambiguous"} and not is_non_empty_string(item.get("status_reason")):
                errors.append(issue("E_S14_DUPLICATE_REJECTION_REASON_REQUIRED", f"finding_normalization_table[{idx}].status_reason is required"))
    missing_normalized = sorted(accepted_ids - normalized_ids)
    if missing_normalized:
        errors.append(issue("E_S14_FINDING_INTAKE_COVERAGE", f"accepted findings missing from normalization table: {missing_normalized}"))
    return accepted_ids


def _s14_records_by_finding(payload: dict[str, Any], field: str, code: str, required: tuple[str, ...], errors: list[ValidationIssue]) -> dict[str, dict[str, Any]]:
    records = payload.get(field)
    by_id: dict[str, dict[str, Any]] = {}
    if not is_non_empty_mapping_list(records):
        errors.append(issue(code, f"{field} must be a non-empty list"))
        return by_id
    assert isinstance(records, list)
    for idx, record in enumerate(records):
        assert isinstance(record, dict)
        for key in required:
            if not is_non_empty_string(record.get(key)):
                errors.append(issue(code, f"{field}[{idx}].{key} must be a non-empty string"))
        finding_id = record.get("finding_id")
        if is_non_empty_string(finding_id):
            by_id[str(finding_id)] = record
    return by_id


def _validate_s14_routing_graph_scope(payload: dict[str, Any], accepted_ids: set[str], errors: list[ValidationIssue]) -> None:
    routes = _s14_records_by_finding(
        payload,
        "nearest_responsible_stage_map",
        "E_S14_NEAREST_STAGE_REQUIRED",
        ("finding_id", "target_stage", "target_material", "rationale"),
        errors,
    )
    for finding_id in sorted(accepted_ids - set(routes)):
        errors.append(issue("E_S14_NEAREST_STAGE_REQUIRED", f"accepted finding {finding_id} missing nearest responsible route"))
    route_records_raw = payload.get("nearest_responsible_stage_map")
    route_records: list[Any] = route_records_raw if isinstance(route_records_raw, list) else []
    for idx, route in enumerate(route_records):
        assert isinstance(route, dict)
        if route.get("target_stage") == "S09":
            errors.append(issue("E_S14_NO_BARE_S09_ROUTE", f"nearest_responsible_stage_map[{idx}] must route to S09A or S09B, not S09"))
        elif route.get("target_stage") not in S14_TARGET_STAGES:
            errors.append(issue("E_S14_NEAREST_STAGE_REQUIRED", f"nearest_responsible_stage_map[{idx}].target_stage invalid"))
        not_routed = route.get("not_routed_to")
        if not is_non_empty_mapping_list(not_routed):
            errors.append(issue("E_S14_NEAREST_STAGE_REQUIRED", f"nearest_responsible_stage_map[{idx}].not_routed_to must explain rejected alternatives"))

    graph = _s14_records_by_finding(
        payload,
        "affected_material_graph_slice",
        "E_S14_AFFECTED_GRAPH_REQUIRED",
        ("finding_id", "upstream_target"),
        errors,
    )
    for finding_id in sorted(accepted_ids - set(graph)):
        errors.append(issue("E_S14_AFFECTED_GRAPH_REQUIRED", f"accepted finding {finding_id} missing graph slice"))
    graph_records_raw = payload.get("affected_material_graph_slice")
    graph_records: list[Any] = graph_records_raw if isinstance(graph_records_raw, list) else []
    for idx, item in enumerate(graph_records):
        assert isinstance(item, dict)
        for key in ("downstream_nodes_to_mark_stale", "protected_unrelated_nodes"):
            _require_s08_string_items(item, f"affected_material_graph_slice[{idx}]", key, "E_S14_AFFECTED_GRAPH_REQUIRED", errors)

    scopes = _s14_records_by_finding(
        payload,
        "repair_scope_plan",
        "E_S14_REPAIR_LOCALITY_REQUIRED",
        ("finding_id", "repair_scope", "smallest_safe_scope"),
        errors,
    )
    for finding_id in sorted(accepted_ids - set(scopes)):
        errors.append(issue("E_S14_REPAIR_LOCALITY_REQUIRED", f"accepted finding {finding_id} missing repair scope plan"))
    scope_records_raw = payload.get("repair_scope_plan")
    scope_records: list[Any] = scope_records_raw if isinstance(scope_records_raw, list) else []
    for idx, item in enumerate(scope_records):
        assert isinstance(item, dict)
        if item.get("repair_scope") not in S14_REPAIR_SCOPES:
            errors.append(issue("E_S14_REPAIR_LOCALITY_REQUIRED", f"repair_scope_plan[{idx}].repair_scope invalid"))
        _require_s08_string_items(item, f"repair_scope_plan[{idx}]", "forbidden_scope_expansion", "E_S14_REPAIR_LOCALITY_REQUIRED", errors)
        scope = str(item.get("smallest_safe_scope") or "").lower()
        if "whole manuscript" in scope or "rewrite entire" in scope or "global rewrite" in scope:
            errors.append(issue("E_S14_REPAIR_LOCALITY_REQUIRED", f"repair_scope_plan[{idx}].smallest_safe_scope must remain local"))


def _validate_s14_tasks_response_validation(payload: dict[str, Any], accepted_ids: set[str], errors: list[ValidationIssue]) -> None:
    task_findings: set[str] = set()
    tasks = payload.get("repair_task_packets")
    if not is_non_empty_mapping_list(tasks):
        errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", "repair_task_packets must be a non-empty list"))
    else:
        assert isinstance(tasks, list)
        for idx, task in enumerate(tasks):
            assert isinstance(task, dict)
            for key in ("task_id", "finding_id", "execution_stage", "task_kind", "target_material", "expected_output_schema"):
                if not is_non_empty_string(task.get(key)):
                    errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", f"repair_task_packets[{idx}].{key} must be a non-empty string"))
            if is_non_empty_string(task.get("finding_id")):
                task_findings.add(str(task["finding_id"]))
            if task.get("execution_stage") == "S09":
                errors.append(issue("E_S14_NO_BARE_S09_ROUTE", f"repair_task_packets[{idx}].execution_stage must be S09A or S09B, not S09"))
            elif task.get("execution_stage") not in S14_EXECUTION_STAGES:
                errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", f"repair_task_packets[{idx}].execution_stage invalid"))
            _require_s08_string_items(task, f"repair_task_packets[{idx}]", "required_validators", "E_S14_TASK_COMPILATION_REQUIRED", errors)
            _require_s08_string_items(task, f"repair_task_packets[{idx}]", "must_not_touch", "E_S14_TASK_COMPILATION_REQUIRED", errors)
            if task.get("repair_executed") is not False:
                errors.append(issue("E_S14_NO_REPAIR_EXECUTION", f"repair_task_packets[{idx}].repair_executed must be false"))
    for finding_id in sorted(accepted_ids - task_findings):
        errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", f"accepted finding {finding_id} missing repair task packet"))

    reselection = payload.get("control_reselection_tasks")
    if not isinstance(reselection, list):
        errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", "control_reselection_tasks must be a list"))
    else:
        for idx, task in enumerate(reselection):
            if not isinstance(task, dict):
                errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", f"control_reselection_tasks[{idx}] must be a mapping"))
                continue
            for key in ("task_id", "target_stage"):
                if not is_non_empty_string(task.get(key)):
                    errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", f"control_reselection_tasks[{idx}].{key} must be a non-empty string"))
            if task.get("target_stage") != "S09A":
                errors.append(issue("E_S14_TASK_COMPILATION_REQUIRED", f"control_reselection_tasks[{idx}].target_stage must be S09A"))
            _require_s08_string_items(task, f"control_reselection_tasks[{idx}]", "controls_to_reselect", "E_S14_TASK_COMPILATION_REQUIRED", errors)

    response = _s14_records_by_finding(
        payload,
        "response_action_map",
        "E_S14_RESPONSE_ACTION_REQUIRED",
        ("finding_id", "response_action"),
        errors,
    )
    for finding_id in sorted(accepted_ids - set(response)):
        errors.append(issue("E_S14_RESPONSE_ACTION_REQUIRED", f"accepted finding {finding_id} missing response action"))
    response_records_raw = payload.get("response_action_map")
    response_records: list[Any] = response_records_raw if isinstance(response_records_raw, list) else []
    for idx, item in enumerate(response_records):
        assert isinstance(item, dict)
        if item.get("response_action") not in S14_RESPONSE_ACTIONS:
            errors.append(issue("E_S14_RESPONSE_ACTION_REQUIRED", f"response_action_map[{idx}].response_action invalid"))
        _require_s08_string_items(item, f"response_action_map[{idx}]", "required_evidence_for_closure", "E_S14_RESPONSE_ACTION_REQUIRED", errors)

    schedule = payload.get("priority_schedule")
    if not is_non_empty_mapping_list(schedule):
        errors.append(issue("E_S14_PRIORITY_REQUIRED", "priority_schedule must be a non-empty list"))
    else:
        assert isinstance(schedule, list)
        for idx, item in enumerate(schedule):
            assert isinstance(item, dict)
            for key in ("task_id", "priority"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S14_PRIORITY_REQUIRED", f"priority_schedule[{idx}].{key} must be a non-empty string"))
            if item.get("priority") not in S14_PRIORITIES:
                errors.append(issue("E_S14_PRIORITY_REQUIRED", f"priority_schedule[{idx}].priority invalid"))
            if _s08_int(item.get("dependency_order")) is None:
                errors.append(issue("E_S14_PRIORITY_REQUIRED", f"priority_schedule[{idx}].dependency_order must be an integer"))

    validation = _require_mapping(payload, "validation_plan", "E_S14_VALIDATION_PLAN_REQUIRED", errors)
    _require_s09_list(validation, "validation_plan", "validators_to_run_after_repair", "E_S14_VALIDATION_PLAN_REQUIRED", errors)
    _require_s09_list(validation, "validation_plan", "stale_nodes_to_revalidate", "E_S14_VALIDATION_PLAN_REQUIRED", errors)


def _validate_s14_owner_validator_risks(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    owner = _require_mapping(payload, "owner_gate_report", "E_S14_OWNER_GATE_REQUIRED", errors)
    for key in ("owner_decisions_required", "owner_gated_findings", "owner_gate_rationale"):
        _require_s09_list(owner, "owner_gate_report", key, "E_S14_OWNER_GATE_REQUIRED", errors, allow_empty=key != "owner_gate_rationale")
    if owner is not None:
        for key in ("semantic_claim_change_requires_owner", "journal_route_change_requires_owner", "external_submission_forbidden_without_owner"):
            if owner.get(key) is not True:
                errors.append(issue("E_S14_OWNER_GATE_REQUIRED", f"owner_gate_report.{key} must be true"))

    unresolved = payload.get("unresolved_or_ambiguous_findings")
    if not isinstance(unresolved, list):
        errors.append(issue("E_S14_UNRESOLVED_REQUIRED", "unresolved_or_ambiguous_findings must be a list"))
    else:
        for idx, item in enumerate(unresolved):
            if not isinstance(item, dict):
                errors.append(issue("E_S14_UNRESOLVED_REQUIRED", f"unresolved_or_ambiguous_findings[{idx}] must be a mapping"))
                continue
            for key in ("finding_id", "blocker"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S14_UNRESOLVED_REQUIRED", f"unresolved_or_ambiguous_findings[{idx}].{key} must be a non-empty string"))

    validator = _require_mapping(payload, "validator_report", "E_S14_VALIDATOR_REPORT_REQUIRED", errors)
    for key in (
        "finding_intake_coverage",
        "duplicate_and_rejection_reason",
        "failure_type_classification",
        "nearest_responsible_stage",
        "no_bare_s09_route",
        "repair_locality",
        "affected_downstream_nodes",
        "protected_unrelated_nodes",
        "owner_gate_status",
        "task_packet_compile",
        "no_execution",
        "no_completion_claim",
    ):
        if validator is not None and validator.get(key) not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S14_VALIDATOR_REPORT_REQUIRED", f"validator_report.{key} must be pass or pass_with_risks"))
    if validator is not None:
        if validator.get("pass_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S14_VALIDATOR_REPORT_REQUIRED", "validator_report.pass_status must be pass or pass_with_risks"))
        if validator.get("recommended_next_stage") != "S15":
            errors.append(issue("E_S14_VALIDATOR_REPORT_REQUIRED", "validator_report.recommended_next_stage must be S15"))
    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S14_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))


def _validate_s14_backflow_repair_plan(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s14_required_modules(payload, errors)
    _validate_s14_authority(payload, errors)
    accepted_ids = _validate_s14_intake_and_normalization(payload, errors)
    _validate_s14_routing_graph_scope(payload, accepted_ids, errors)
    _validate_s14_tasks_response_validation(payload, accepted_ids, errors)
    _validate_s14_owner_validator_risks(payload, errors)


def _require_s15_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "completion_boundary",
        "authority_boundary",
        "repair_task_ack",
        "pre_repair_snapshot",
        "target_material_diff",
        "revised_material_candidate",
        "regenerated_task_packets",
        "regenerated_text_or_figure_candidates",
        "affected_downstream_regeneration_log",
        "stale_resolution_report",
        "unrelated_node_preservation_report",
        "finding_resolution_evidence",
        "updated_validator_report",
        "new_risk_scan",
        "candidate_artifact_return",
        "missing_material_report",
        "verifier_evidence",
        "remaining_risks",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        errors.append(issue("E_S15_REPAIR_EXECUTION_REPORT_REQUIRED", f"S15RepairExecutionReport missing required modules: {missing}"))


def _validate_s15_authority(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[str, str]:
    _require_s15_payload_header(payload, "ppg-s15-repair-execution-report/v0.1", "E_S15_REPAIR_EXECUTION_REPORT_REQUIRED", errors)
    if payload.get("completion_boundary") != S15_COMPLETION_BOUNDARY:
        errors.append(issue("E_S15_COMPLETION_BOUNDARY", f"completion_boundary must be {S15_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S15_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S15_NO_COMPLETION_OVERCLAIM", f"S15 repair report must not contain completion field {completion_key!r}"))
    boundary = _require_mapping(payload, "authority_boundary", "E_S15_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "pdf_exported",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "recursive_dispatch_requested",
        "writes_outside_allowed_paths",
        "controller_commit_claimed",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S15_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S15_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))
    candidate_return = as_mapping(payload.get("candidate_artifact_return"))
    packet_id = str(candidate_return.get("packet_id") or "") if candidate_return else ""
    output_path = str(candidate_return.get("output_artifact_path") or "") if candidate_return else ""
    return packet_id, output_path


def _validate_s15_task_snapshot_diff(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    ack = _require_mapping(payload, "repair_task_ack", "E_S15_STRICT_PACKET_ACK_REQUIRED", errors)
    _require_mapping_fields(ack, "repair_task_ack", ["repair_task_id", "source_s14_plan", "task_kind", "target_stage", "target_material", "base_version", "understood_scope"], "E_S15_STRICT_PACKET_ACK_REQUIRED", errors)
    for key in ("allowed_write_paths", "allowed_actions", "forbidden_actions", "refused_scope_expansion"):
        _require_s09_list(ack, "repair_task_ack", key, "E_S15_STRICT_PACKET_ACK_REQUIRED", errors)
    if ack is not None:
        if ack.get("task_kind") not in S15_REPAIR_TASK_KINDS:
            errors.append(issue("E_S15_STRICT_PACKET_ACK_REQUIRED", "repair_task_ack.task_kind invalid"))
        if ack.get("target_stage") not in S14_TARGET_STAGES:
            errors.append(issue("E_S15_STRICT_PACKET_ACK_REQUIRED", "repair_task_ack.target_stage invalid"))
        if ack.get("stop_condition_acknowledged") is not True:
            errors.append(issue("E_S15_STRICT_PACKET_ACK_REQUIRED", "repair_task_ack.stop_condition_acknowledged must be true"))

    snapshot = _require_mapping(payload, "pre_repair_snapshot", "E_S15_PRE_REPAIR_SNAPSHOT_REQUIRED", errors)
    _require_mapping_fields(snapshot, "pre_repair_snapshot", ["target_material", "base_version", "hash_or_version_ref"], "E_S15_PRE_REPAIR_SNAPSHOT_REQUIRED", errors)
    _require_s09_list(snapshot, "pre_repair_snapshot", "downstream_stale_set_before", "E_S15_PRE_REPAIR_SNAPSHOT_REQUIRED", errors)

    diff = _require_mapping(payload, "target_material_diff", "E_S15_DIFF_LOCALITY_REQUIRED", errors)
    _require_mapping_fields(diff, "target_material_diff", ["locality_rationale"], "E_S15_DIFF_LOCALITY_REQUIRED", errors)
    for key in ("changed_materials", "changed_paths", "protected_materials_unchanged"):
        _require_s09_list(diff, "target_material_diff", key, "E_S15_DIFF_LOCALITY_REQUIRED", errors)
    if diff is not None:
        for path in _s08_string_items(diff.get("changed_paths")):
            if not _s09_path_is_safe(path):
                errors.append(issue("E_S15_DIFF_LOCALITY_REQUIRED", f"target_material_diff.changed_paths contains unsafe path {path!r}"))
        broad = str(diff.get("locality_rationale") or "").lower()
        if "whole manuscript" in broad or "global rewrite" in broad:
            errors.append(issue("E_S15_DIFF_LOCALITY_REQUIRED", "target_material_diff.locality_rationale must be local"))

    revised = _require_mapping(payload, "revised_material_candidate", "E_S15_REVISED_CANDIDATE_REQUIRED", errors)
    _require_mapping_fields(revised, "revised_material_candidate", ["material_id", "version_candidate", "content_ref", "claim_boundary_impact"], "E_S15_REVISED_CANDIDATE_REQUIRED", errors)
    if revised is not None and revised.get("claim_boundary_impact") not in S15_CLAIM_IMPACTS:
        errors.append(issue("E_S15_REVISED_CANDIDATE_REQUIRED", "revised_material_candidate.claim_boundary_impact invalid"))


def _validate_s15_regeneration_resolution(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    packets = payload.get("regenerated_task_packets")
    if not is_non_empty_mapping_list(packets):
        errors.append(issue("E_S15_REGENERATED_TASK_PACKETS_REQUIRED", "regenerated_task_packets must be a non-empty list"))
    else:
        assert isinstance(packets, list)
        for idx, packet in enumerate(packets):
            assert isinstance(packet, dict)
            for key in ("packet_id", "regeneration_reason", "target_stage"):
                if not is_non_empty_string(packet.get(key)):
                    errors.append(issue("E_S15_REGENERATED_TASK_PACKETS_REQUIRED", f"regenerated_task_packets[{idx}].{key} must be a non-empty string"))
            if packet.get("target_stage") == "S09":
                errors.append(issue("E_S15_REGENERATED_TASK_PACKETS_REQUIRED", f"regenerated_task_packets[{idx}].target_stage must be S09A/S09B not S09"))
            elif packet.get("target_stage") not in {"S09B", "S10", "S11", "S12"}:
                errors.append(issue("E_S15_REGENERATED_TASK_PACKETS_REQUIRED", f"regenerated_task_packets[{idx}].target_stage invalid"))

    artifacts = payload.get("regenerated_text_or_figure_candidates")
    if not is_non_empty_mapping_list(artifacts):
        errors.append(issue("E_S15_REGENERATED_ARTIFACTS_REQUIRED", "regenerated_text_or_figure_candidates must be a non-empty list"))
    else:
        assert isinstance(artifacts, list)
        for idx, artifact in enumerate(artifacts):
            assert isinstance(artifact, dict)
            for key in ("artifact_id", "artifact_kind", "content_ref"):
                if not is_non_empty_string(artifact.get(key)):
                    errors.append(issue("E_S15_REGENERATED_ARTIFACTS_REQUIRED", f"regenerated_text_or_figure_candidates[{idx}].{key} must be a non-empty string"))
            if artifact.get("artifact_kind") not in {"section_text", "caption", "figure", "integrated_manuscript_fragment", "control_material"}:
                errors.append(issue("E_S15_REGENERATED_ARTIFACTS_REQUIRED", f"regenerated_text_or_figure_candidates[{idx}].artifact_kind invalid"))

    log = payload.get("affected_downstream_regeneration_log")
    if not is_non_empty_mapping_list(log):
        errors.append(issue("E_S15_STALE_PROPAGATION_REQUIRED", "affected_downstream_regeneration_log must be a non-empty list"))
    else:
        assert isinstance(log, list)
        for idx, item in enumerate(log):
            assert isinstance(item, dict)
            for key in ("node", "action", "evidence_ref"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(issue("E_S15_STALE_PROPAGATION_REQUIRED", f"affected_downstream_regeneration_log[{idx}].{key} must be a non-empty string"))
            if item.get("action") not in S15_DOWNSTREAM_ACTIONS:
                errors.append(issue("E_S15_STALE_PROPAGATION_REQUIRED", f"affected_downstream_regeneration_log[{idx}].action invalid"))

    stale = _require_mapping(payload, "stale_resolution_report", "E_S15_STALE_PROPAGATION_REQUIRED", errors)
    _require_s09_list(stale, "stale_resolution_report", "stale_nodes_resolved", "E_S15_STALE_PROPAGATION_REQUIRED", errors)
    _require_s09_list(stale, "stale_resolution_report", "stale_nodes_remaining", "E_S15_STALE_PROPAGATION_REQUIRED", errors, allow_empty=True)
    _require_mapping_fields(stale, "stale_resolution_report", ["remaining_stale_reason"], "E_S15_STALE_PROPAGATION_REQUIRED", errors)

    preservation = _require_mapping(payload, "unrelated_node_preservation_report", "E_S15_UNRELATED_PRESERVATION_REQUIRED", errors)
    _require_s09_list(preservation, "unrelated_node_preservation_report", "checked_nodes", "E_S15_UNRELATED_PRESERVATION_REQUIRED", errors)
    _require_s09_list(preservation, "unrelated_node_preservation_report", "unchanged_evidence", "E_S15_UNRELATED_PRESERVATION_REQUIRED", errors)

    resolution = _require_mapping(payload, "finding_resolution_evidence", "E_S15_FINDING_RESOLUTION_REQUIRED", errors)
    _require_mapping_fields(resolution, "finding_resolution_evidence", ["finding_id", "resolution_status", "explanation"], "E_S15_FINDING_RESOLUTION_REQUIRED", errors)
    _require_s09_list(resolution, "finding_resolution_evidence", "evidence_refs", "E_S15_FINDING_RESOLUTION_REQUIRED", errors)
    if resolution is not None and resolution.get("resolution_status") not in S15_RESOLUTION_STATUSES:
        errors.append(issue("E_S15_FINDING_RESOLUTION_REQUIRED", "finding_resolution_evidence.resolution_status invalid"))


def _validate_s15_validator_return(payload: dict[str, Any], packet_id: str, output_path: str, errors: list[ValidationIssue]) -> None:
    validator = _require_mapping(payload, "updated_validator_report", "E_S15_VALIDATOR_REPORT_REQUIRED", errors)
    for key in ("validators_run", "passed", "failed", "not_run_with_reason"):
        _require_s09_list(validator, "updated_validator_report", key, "E_S15_VALIDATOR_REPORT_REQUIRED", errors, allow_empty=key in {"failed", "not_run_with_reason"})
    if validator is not None and validator.get("failed"):
        errors.append(issue("E_S15_VALIDATOR_REPORT_REQUIRED", "updated_validator_report.failed must be empty for a resolved candidate fixture"))

    risk = _require_mapping(payload, "new_risk_scan", "E_S15_NO_NEW_HIGH_SEVERITY_REQUIRED", errors)
    _require_s09_list(risk, "new_risk_scan", "new_high_severity_findings", "E_S15_NO_NEW_HIGH_SEVERITY_REQUIRED", errors, allow_empty=True)
    _require_s09_list(risk, "new_risk_scan", "residual_risks", "E_S15_NO_NEW_HIGH_SEVERITY_REQUIRED", errors)
    if risk is not None and risk.get("new_high_severity_findings"):
        errors.append(issue("E_S15_NO_NEW_HIGH_SEVERITY_REQUIRED", "new_risk_scan.new_high_severity_findings must be empty"))

    candidate_return = _require_mapping(payload, "candidate_artifact_return", "E_S15_CANDIDATE_RETURN_REQUIRED", errors)
    _require_mapping_fields(candidate_return, "candidate_artifact_return", ["schema_version", "return_id", "status", "packet_id", "output_artifact_path"], "E_S15_CANDIDATE_RETURN_REQUIRED", errors)
    for key in ("evidence", "validator_expectations", "remaining_risks"):
        _require_s09_list(candidate_return, "candidate_artifact_return", key, "E_S15_CANDIDATE_RETURN_REQUIRED", errors)
    if candidate_return is not None:
        if candidate_return.get("schema_version") != "ppg-candidate-return/v0.1" or candidate_return.get("status") != "candidate":
            errors.append(issue("E_S15_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return must use ppg-candidate-return/v0.1 candidate status"))
        if packet_id and candidate_return.get("packet_id") != packet_id:
            errors.append(issue("E_S15_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.packet_id must match packet"))
        if output_path and candidate_return.get("output_artifact_path") != output_path:
            errors.append(issue("E_S15_CANDIDATE_RETURN_REQUIRED", "candidate_artifact_return.output_artifact_path must match output path"))
        for key in ("graph_completion_claimed", "recursive_dispatch_requested", "writes_outside_allowed_paths"):
            if candidate_return.get(key) is not False:
                errors.append(issue("E_S15_CANDIDATE_RETURN_REQUIRED", f"candidate_artifact_return.{key} must be false"))

    missing = _require_mapping(payload, "missing_material_report", "E_S15_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    _require_mapping_fields(missing, "missing_material_report", ["status", "backflow_target_if_blocked"], "E_S15_MISSING_MATERIAL_REPORT_REQUIRED", errors)
    if missing is not None and missing.get("status") != "not_blocked":
        errors.append(issue("E_S15_MISSING_MATERIAL_REPORT_REQUIRED", "missing_material_report.status must be not_blocked for candidate fixture"))

    verifier = _require_mapping(payload, "verifier_evidence", "E_S15_VERIFIER_EVIDENCE_REQUIRED", errors)
    _require_mapping_fields(verifier, "verifier_evidence", ["agent_type", "verification_status"], "E_S15_VERIFIER_EVIDENCE_REQUIRED", errors)
    checks = _require_s09_list(verifier, "verifier_evidence", "checks_completed", "E_S15_VERIFIER_EVIDENCE_REQUIRED", errors)
    missing_checks = sorted(S15_REQUIRED_VERIFIER_CHECKS - checks)
    if missing_checks:
        errors.append(issue("E_S15_VERIFIER_EVIDENCE_REQUIRED", f"verifier_evidence.checks_completed missing {missing_checks}"))
    if verifier is not None:
        if verifier.get("agent_type") != "verifier":
            errors.append(issue("E_S15_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.agent_type must be verifier"))
        if verifier.get("verification_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S15_VERIFIER_EVIDENCE_REQUIRED", "verifier_evidence.verification_status must be pass or pass_with_risks"))
    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S15_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))


def _validate_s15_repair_execution_report(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s15_required_modules(payload, errors)
    packet_id, output_path = _validate_s15_authority(payload, errors)
    _validate_s15_task_snapshot_diff(payload, errors)
    _validate_s15_regeneration_resolution(payload, errors)
    _validate_s15_validator_return(payload, packet_id, output_path, errors)


def _require_s16_required_modules(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = [
        "schema_version",
        "stage_id",
        "completion_boundary",
        "authority_boundary",
        "evidence_mode",
        "live_export_verification",
        "readiness_state_separation",
        "upstream_closure_check",
        "build_readiness_check",
        "build_run_report",
        "rendered_surface_check",
        "export_manifest",
        "file_hash_manifest",
        "figure_file_checklist",
        "data_availability_statement_check",
        "supplement_manifest",
        "repository_hygiene_report",
        "manager_handoff_report",
        "owner_gate_report",
        "human_feedback_intake_route",
        "validator_report",
        "remaining_risks",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        errors.append(issue("E_S16_EXPORT_HANDOFF_PACKAGE_REQUIRED", f"S16ExportHandoffPackage missing required modules: {missing}"))


def _s16_string_items(value: Any) -> list[str]:
    return _s08_string_items(value)


def _require_s16_list(container: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue], *, allow_empty: bool = False) -> set[str]:
    if container is None:
        return set()
    items = _s16_string_items(container.get(key))
    if not items and not allow_empty:
        errors.append(issue(code, f"{field}.{key} must be a non-empty string or list of strings"))
    return set(items)


def _validate_s16_path_list(container: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue], *, allow_empty: bool = False) -> set[str]:
    paths = _require_s16_list(container, field, key, code, errors, allow_empty=allow_empty)
    for path in paths:
        if not _s09_path_is_safe(path):
            errors.append(issue(code, f"{field}.{key} contains unsafe path {path!r}"))
    return paths


def _s16_valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _collect_s16_required_manifest_paths(payload: dict[str, Any]) -> set[str]:
    required: set[str] = set()
    target = as_mapping(payload.get("delivery_target"))
    compiled = target is not None and target.get("kind") in S16_COMPILED_DELIVERY_TARGETS
    readiness = as_mapping(payload.get("build_readiness_check"))
    if readiness is not None:
        for key in ("output_paths", "figure_paths"):
            required.update(_s16_string_items(readiness.get(key)))
    build = as_mapping(payload.get("build_run_report"))
    if build is not None:
        for key in ("output_pdf", "log_ref"):
            if is_non_empty_string(build.get(key)):
                required.add(str(build[key]))
    checklist = payload.get("figure_file_checklist")
    if isinstance(checklist, list):
        for record in checklist:
            if isinstance(record, dict) and is_non_empty_string(record.get("exported_file")):
                required.add(str(record["exported_file"]))
    supplement = as_mapping(payload.get("supplement_manifest"))
    if supplement is not None:
        required.update(_s16_string_items(supplement.get("files")))
    handoff = as_mapping(payload.get("manager_handoff_report"))
    if handoff is not None:
        required.update(_s16_string_items(handoff.get("human_readable_outputs")))
    surface = as_mapping(payload.get("rendered_surface_check"))
    if surface is not None and is_non_empty_string(surface.get("rendered_text_ref")):
        required.add(str(surface["rendered_text_ref"]))
    if surface is not None and is_non_empty_string(surface.get("source_pdf_ref")):
        required.add(str(surface["source_pdf_ref"]))
    artifact_refs = surface.get("visual_formal_artifact_refs") if surface is not None else None
    if isinstance(artifact_refs, list):
        for record in artifact_refs:
            if isinstance(record, dict) and is_non_empty_string(record.get("exported_file")):
                required.add(str(record["exported_file"]))
    post_writeback = as_mapping(payload.get("post_writeback_validation"))
    if post_writeback is not None:
        keys = ("pdf_text_ref", "output_pdf_ref")
        if compiled:
            keys = tuple(sorted(S16_POST_WRITEBACK_REQUIRED_FIELDS - {"status", "pdf_text_sha256", "output_pdf_sha256"}))
        for key in keys:
            if is_non_empty_string(post_writeback.get(key)):
                required.add(str(post_writeback[key]))
    if compiled:
        source_writeback = as_mapping(payload.get("source_writeback_evidence"))
        if source_writeback is not None:
            for key in sorted(S16_SOURCE_WRITEBACK_REQUIRED_FIELDS - {"status"}):
                if is_non_empty_string(source_writeback.get(key)):
                    required.add(str(source_writeback[key]))
    return required


def _collect_s16_expected_manifest_hashes(payload: dict[str, Any]) -> dict[str, tuple[str, str]]:
    target = as_mapping(payload.get("delivery_target"))
    if target is None or target.get("kind") not in S16_COMPILED_DELIVERY_TARGETS:
        return {}
    expected: dict[str, tuple[str, str]] = {}

    def add(ref: Any, digest: Any, source: str) -> None:
        if is_non_empty_string(ref) and _s16_valid_sha256(digest):
            expected.setdefault(str(ref), (str(digest), source))

    surface = as_mapping(payload.get("rendered_surface_check"))
    if surface is not None:
        add(surface.get("rendered_text_ref"), surface.get("rendered_text_sha256"), "rendered_surface_check.rendered_text_sha256")
        add(surface.get("source_pdf_ref"), surface.get("source_pdf_sha256"), "rendered_surface_check.source_pdf_sha256")

    post_writeback = as_mapping(payload.get("post_writeback_validation"))
    if post_writeback is not None:
        add(post_writeback.get("pdf_text_ref"), post_writeback.get("pdf_text_sha256"), "post_writeback_validation.pdf_text_sha256")
        add(post_writeback.get("output_pdf_ref"), post_writeback.get("output_pdf_sha256"), "post_writeback_validation.output_pdf_sha256")
    return expected


def _normalize_s16_text(value: str) -> str:
    normalized = value.lower()
    for char in "-_/.,;:()[]{}":
        normalized = normalized.replace(char, " ")
    return " ".join(normalized.split())


def _s16_phrase_is_negated(text: str, index: int) -> bool:
    before_tokens = text[:index].split()
    if not before_tokens:
        return False
    direct_negation_patterns = (
        ("not",),
        ("not", "yet"),
        ("never",),
        ("no",),
        ("without", "claiming"),
        ("without", "claim"),
        ("does", "not", "claim"),
        ("do", "not", "claim"),
        ("must", "not", "claim"),
        ("is", "not"),
        ("are", "not"),
    )
    return any(tuple(before_tokens[-len(pattern):]) == pattern for pattern in direct_negation_patterns)


def _find_s16_narrative_overclaim(value: Any) -> str | None:
    if isinstance(value, dict):
        for nested in value.values():
            found = _find_s16_narrative_overclaim(nested)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _find_s16_narrative_overclaim(nested)
            if found is not None:
                return found
    elif isinstance(value, str):
        text = _normalize_s16_text(value)
        for phrase in sorted(S16_NARRATIVE_OVERCLAIM_PHRASES):
            start = 0
            while True:
                index = text.find(phrase, start)
                if index < 0:
                    break
                if not _s16_phrase_is_negated(text, index):
                    return phrase
                start = index + len(phrase)
    return None


def _validate_s16_authority(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s16_payload_header(payload, "ppg-s16-export-handoff-package/v0.1", "E_S16_EXPORT_HANDOFF_PACKAGE_REQUIRED", errors)
    if payload.get("completion_boundary") != S16_COMPLETION_BOUNDARY:
        errors.append(issue("E_S16_COMPLETION_BOUNDARY", f"completion_boundary must be {S16_COMPLETION_BOUNDARY!r}"))
    completion_key = _contains_forbidden_key(payload, S16_COMPLETION_OVERCLAIM_KEYS)
    if completion_key is not None:
        errors.append(issue("E_S16_NO_SUBMISSION_PUBLICATION_OVERCLAIM", f"S16 export handoff must not contain completion/submission/publication field {completion_key!r}"))
    narrative_overclaim = _find_s16_narrative_overclaim(payload)
    if narrative_overclaim is not None:
        errors.append(issue("E_S16_NO_SUBMISSION_PUBLICATION_OVERCLAIM", f"S16 export handoff must not contain narrative overclaim phrase {narrative_overclaim!r}"))
    boundary = _require_mapping(payload, "authority_boundary", "E_S16_AUTHORITY_BOUNDARY_REQUIRED", errors)
    for key in (
        "graph_completion_claimed",
        "manuscript_completion_claimed",
        "scientific_review_performed",
        "content_repair_performed",
        "external_submission_performed",
        "submission_readiness_claimed",
        "publication_readiness_claimed",
        "owner_submission_authorization_claimed",
        "recursive_dispatch_requested",
        "writes_outside_export_paths",
    ):
        if boundary is not None and boundary.get(key) is not False:
            errors.append(issue("E_S16_AUTHORITY_BOUNDARY_REQUIRED", f"authority_boundary.{key} must be false"))
    if boundary is not None and boundary.get("controller_owned_completion") is not True:
        errors.append(issue("E_S16_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.controller_owned_completion must be true"))
    if boundary is not None and boundary.get("human_readable_export_allowed") is not True:
        errors.append(issue("E_S16_AUTHORITY_BOUNDARY_REQUIRED", "authority_boundary.human_readable_export_allowed must be true"))


def _validate_s16_evidence_mode(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    mode = _require_mapping(payload, "evidence_mode", "E_S16_EVIDENCE_MODE_REQUIRED", errors)
    _require_mapping_fields(mode, "evidence_mode", ["mode", "live_mode_verifier", "handoff_claim_boundary"], "E_S16_EVIDENCE_MODE_REQUIRED", errors)
    mode_value = mode.get("mode") if mode is not None else None
    if mode is not None and mode_value not in S16_EVIDENCE_MODES:
        errors.append(issue("E_S16_EVIDENCE_MODE_REQUIRED", "evidence_mode.mode must be fixture_projection or live_export"))
    live = _require_mapping(payload, "live_export_verification", "E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", errors)
    _require_mapping_fields(live, "live_export_verification", ["status", "required_before_owner_handoff"], "E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", errors)
    if live is not None and mode_value == "fixture_projection":
        for key in ("filesystem_paths_checked", "hashes_recomputed", "pdf_opened_from_disk", "physical_export_claimed", "live_handoff_claimed"):
            if live.get(key) is not False:
                errors.append(issue("E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", f"live_export_verification.{key} must be false for fixture/projection material"))
        if live.get("status") != "not_run_fixture_projection":
            errors.append(issue("E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", "live_export_verification.status must be not_run_fixture_projection for the contract fixture"))
    elif live is not None and mode_value == "live_export":
        for key in ("filesystem_paths_checked", "hashes_recomputed", "pdf_opened_from_disk", "physical_export_claimed"):
            if live.get(key) is not True:
                errors.append(issue("E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", f"live_export_verification.{key} must be true for live_export material"))
        if live.get("live_handoff_claimed") is not False:
            errors.append(issue("E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", "live_export_verification.live_handoff_claimed must remain false until controller/owner handoff commit"))
        if live.get("status") != "passed_live_export_verification":
            errors.append(issue("E_S16_LIVE_EXPORT_VERIFICATION_REQUIRED", "live_export_verification.status must be passed_live_export_verification for live_export material"))


def _s16_require_bool(container: dict[str, Any] | None, field: str, key: str, expected: bool | None, code: str, errors: list[ValidationIssue]) -> None:
    if container is None:
        return
    value = container.get(key)
    if not isinstance(value, bool):
        errors.append(issue(code, f"{field}.{key} must be a boolean"))
    elif expected is not None and value is not expected:
        errors.append(issue(code, f"{field}.{key} must be {str(expected).lower()}"))


def _s16_require_safe_ref(container: dict[str, Any] | None, field: str, key: str, code: str, errors: list[ValidationIssue]) -> str | None:
    if container is None:
        return None
    value = container.get(key)
    if not is_non_empty_string(value):
        errors.append(issue(code, f"{field}.{key} must be a non-empty string"))
        return None
    text = str(value)
    if not _s09_path_is_safe(text):
        errors.append(issue(code, f"{field}.{key} must be a safe repo-relative file path"))
    return text


def _validate_s16_delivery_target(payload: dict[str, Any], errors: list[ValidationIssue]) -> tuple[str | None, bool]:
    target = _require_mapping(payload, "delivery_target", "E_S16_DELIVERY_TARGET_REQUIRED", errors)
    _require_mapping_fields(
        target,
        "delivery_target",
        ["kind", "target_ref", "requested_target_source"],
        "E_S16_DELIVERY_TARGET_REQUIRED",
        errors,
    )
    for key in (
        "compiled_pdf_claimed",
        "requires_content_bearing_pdf",
        "requires_source_writeback",
        "allows_template_only_handoff",
        "allows_candidate_only_completion",
        "requires_post_writeback_s12",
        "requires_final_s16_content_ready_pass",
    ):
        _s16_require_bool(target, "delivery_target", key, None, "E_S16_DELIVERY_TARGET_REQUIRED", errors)
    if target is None:
        return None, False

    kind = target.get("kind")
    source = target.get("requested_target_source")
    if kind not in S16_DELIVERY_TARGET_KINDS:
        errors.append(issue("E_S16_DELIVERY_TARGET_REQUIRED", "delivery_target.kind invalid"))
    if source not in S16_REQUESTED_TARGET_SOURCES:
        errors.append(issue("E_S16_DELIVERY_TARGET_REQUIRED", "delivery_target.requested_target_source invalid"))
    if is_non_empty_string(target.get("target_ref")) and str(target.get("target_ref")).strip() != str(target.get("target_ref")):
        errors.append(issue("E_S16_DELIVERY_TARGET_REQUIRED", "delivery_target.target_ref must be trimmed"))

    active_target_declared = is_non_empty_string(target.get("active_target_kind")) or is_non_empty_string(target.get("active_target_ref"))
    if source in S16_ACTIVE_TARGET_SOURCES or active_target_declared:
        _require_mapping_fields(
            target,
            "delivery_target",
            ["active_target_kind", "active_target_ref"],
            "E_S16_DELIVERY_TARGET_BINDING",
            errors,
        )
        if target.get("active_target_kind") != kind:
            errors.append(issue("E_S16_DELIVERY_TARGET_BINDING", "delivery_target.active_target_kind must match delivery_target.kind"))
        active_ref = target.get("active_target_ref")
        target_ref = target.get("target_ref")
        chain = _s16_string_items(target.get("target_ref_chain"))
        if is_non_empty_string(active_ref) and is_non_empty_string(target_ref) and active_ref != target_ref and str(active_ref) not in chain:
            errors.append(issue("E_S16_DELIVERY_TARGET_BINDING", "delivery_target.active_target_ref must match target_ref or appear in target_ref_chain"))

    compiled = kind in S16_COMPILED_DELIVERY_TARGETS
    expected_policy = S16_COMPILED_TARGET_POLICY if compiled else S16_NON_COMPILED_TARGET_POLICY
    code = "E_S16_COMPILED_TARGET_GATE" if compiled else "E_S16_TEMPLATE_ONLY_HANDOFF_BOUNDARY"
    for key, expected in expected_policy.items():
        _s16_require_bool(target, "delivery_target", key, expected, code, errors)
    if kind in S16_NON_COMPILED_DELIVERY_TARGETS and target.get("compiled_pdf_claimed") is not False:
        errors.append(issue("E_S16_TEMPLATE_ONLY_HANDOFF_BOUNDARY", "non-compiled delivery targets must not claim compiled PDF delivery"))
    return str(kind) if isinstance(kind, str) else None, compiled


def _validate_s16_compiled_source_writeback(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    evidence = _require_mapping(payload, "source_writeback_evidence", "E_S16_SOURCE_WRITEBACK_REQUIRED", errors)
    if evidence is not None:
        missing = sorted(field for field in S16_SOURCE_WRITEBACK_REQUIRED_FIELDS if field not in evidence)
        if missing:
            errors.append(issue("E_S16_SOURCE_WRITEBACK_REQUIRED", f"source_writeback_evidence missing {missing}"))
        for key in sorted(S16_SOURCE_WRITEBACK_REQUIRED_FIELDS - {"status"}):
            _s16_require_safe_ref(evidence, "source_writeback_evidence", key, "E_S16_SOURCE_WRITEBACK_REQUIRED", errors)
        if evidence.get("status") != "applied":
            errors.append(issue("E_S16_SOURCE_WRITEBACK_REQUIRED", "source_writeback_evidence.status must be applied"))

    validation = _require_mapping(payload, "post_writeback_validation", "E_S16_POST_WRITEBACK_VALIDATION_REQUIRED", errors)
    if validation is not None:
        missing = sorted(field for field in S16_POST_WRITEBACK_REQUIRED_FIELDS if field not in validation)
        if missing:
            errors.append(issue("E_S16_POST_WRITEBACK_VALIDATION_REQUIRED", f"post_writeback_validation missing {missing}"))
        for key in sorted(S16_POST_WRITEBACK_REQUIRED_FIELDS - {"status", "pdf_text_sha256", "output_pdf_sha256"}):
            _s16_require_safe_ref(validation, "post_writeback_validation", key, "E_S16_POST_WRITEBACK_VALIDATION_REQUIRED", errors)
        for key in ("pdf_text_sha256", "output_pdf_sha256"):
            if not _s16_valid_sha256(validation.get(key)):
                errors.append(issue("E_S16_POST_WRITEBACK_VALIDATION_REQUIRED", f"post_writeback_validation.{key} must be a lowercase sha256"))
        if validation.get("status") != "pass":
            errors.append(issue("E_S16_POST_WRITEBACK_VALIDATION_REQUIRED", "post_writeback_validation.status must be pass"))


def _validate_s16_compiled_readiness(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    readiness = as_mapping(payload.get("readiness_state_separation"))
    if readiness is None:
        return
    for key in sorted(S16_COMPILED_READINESS_KEYS):
        if readiness.get(key) != "pass":
            errors.append(issue("E_S16_COMPILED_TARGET_GATE", f"compiled PDF target requires readiness_state_separation.{key} to be pass"))


def _validate_s16_readiness_and_upstream(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    readiness = _require_mapping(payload, "readiness_state_separation", "E_S16_READINESS_STATE_REQUIRED", errors)
    _require_mapping_fields(
        readiness,
        "readiness_state_separation",
        ["content_ready", "build_ready", "render_clean", "repository_clean", "handoff_ready"],
        "E_S16_READINESS_STATE_REQUIRED",
        errors,
    )
    if readiness is not None:
        for key in ("content_ready", "build_ready", "render_clean", "repository_clean", "handoff_ready"):
            if readiness.get(key) not in S16_READINESS_STATES:
                errors.append(issue("E_S16_READINESS_STATE_REQUIRED", f"readiness_state_separation.{key} invalid"))
        if readiness.get("submission_gated") is not True:
            errors.append(issue("E_S16_READINESS_STATE_REQUIRED", "readiness_state_separation.submission_gated must be true"))
        if readiness.get("submission_state") != "owner_gated_not_authorized":
            errors.append(issue("E_S16_READINESS_STATE_REQUIRED", "readiness_state_separation.submission_state must be owner_gated_not_authorized"))

    upstream = _require_mapping(payload, "upstream_closure_check", "E_S16_UPSTREAM_CLOSURE_REQUIRED", errors)
    _require_mapping_fields(
        upstream,
        "upstream_closure_check",
        ["s12_candidate_ref", "s13_review_closure_ref", "s14_backflow_status", "s15_repair_status"],
        "E_S16_UPSTREAM_CLOSURE_REQUIRED",
        errors,
    )
    if upstream is not None:
        for key in ("s14_backflow_status", "s15_repair_status"):
            if upstream.get(key) not in S16_CLOSURE_STATUSES:
                errors.append(issue("E_S16_UPSTREAM_CLOSURE_REQUIRED", f"upstream_closure_check.{key} invalid"))
        _require_s16_list(upstream, "upstream_closure_check", "accepted_risks", "E_S16_UPSTREAM_CLOSURE_REQUIRED", errors, allow_empty=True)
        unresolved = _require_s16_list(upstream, "upstream_closure_check", "unresolved_findings", "E_S16_UPSTREAM_CLOSURE_REQUIRED", errors, allow_empty=True)
        stale = _require_s16_list(upstream, "upstream_closure_check", "stale_nodes_remaining", "E_S16_UPSTREAM_CLOSURE_REQUIRED", errors, allow_empty=True)
        if unresolved or stale:
            errors.append(issue("E_S16_UPSTREAM_CLOSURE_REQUIRED", "unresolved findings and stale_nodes_remaining must be empty before clean export"))


def _validate_s16_build_and_render(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    readiness = _require_mapping(payload, "build_readiness_check", "E_S16_BUILD_READINESS_REQUIRED", errors)
    _require_mapping_fields(readiness, "build_readiness_check", ["latex_root", "build_command", "status"], "E_S16_BUILD_READINESS_REQUIRED", errors)
    for key in ("bibliography_paths", "figure_paths", "output_paths"):
        _validate_s16_path_list(readiness, "build_readiness_check", key, "E_S16_BUILD_READINESS_REQUIRED", errors)
    if readiness is not None:
        if not _s09_path_is_safe(str(readiness.get("latex_root") or "")):
            errors.append(issue("E_S16_BUILD_READINESS_REQUIRED", "build_readiness_check.latex_root must be a safe repo-relative file path"))
        if readiness.get("status") != "pass":
            errors.append(issue("E_S16_BUILD_READINESS_REQUIRED", "build_readiness_check.status must be pass"))

    build = _require_mapping(payload, "build_run_report", "E_S16_BUILD_SUCCESS_REQUIRED", errors)
    _require_mapping_fields(build, "build_run_report", ["command", "log_ref", "output_pdf"], "E_S16_BUILD_SUCCESS_REQUIRED", errors)
    _require_s16_list(build, "build_run_report", "warnings_summary", "E_S16_BUILD_SUCCESS_REQUIRED", errors, allow_empty=True)
    errors_summary = _require_s16_list(build, "build_run_report", "errors_summary", "E_S16_BUILD_SUCCESS_REQUIRED", errors, allow_empty=True)
    if build is not None:
        if build.get("exit_code") != 0:
            errors.append(issue("E_S16_BUILD_SUCCESS_REQUIRED", "build_run_report.exit_code must be 0"))
        for key in ("log_ref", "output_pdf"):
            if not _s09_path_is_safe(str(build.get(key) or "")):
                errors.append(issue("E_S16_BUILD_SUCCESS_REQUIRED", f"build_run_report.{key} must be a safe repo-relative file path"))
        if errors_summary:
            errors.append(issue("E_S16_BUILD_SUCCESS_REQUIRED", "build_run_report.errors_summary must be empty for clean export"))

    surface = _require_mapping(payload, "rendered_surface_check", "E_S16_RENDERED_SURFACE_REQUIRED", errors)
    for key in ("figures_present", "captions_present"):
        _require_s16_list(surface, "rendered_surface_check", key, "E_S16_RENDERED_SURFACE_REQUIRED", errors)
    anomalies = _require_s16_list(surface, "rendered_surface_check", "obvious_rendering_anomalies", "E_S16_RENDERED_SURFACE_REQUIRED", errors, allow_empty=True)
    if surface is not None:
        for key in ("pdf_exists", "pdf_opens", "title_author_abstract_present", "references_present"):
            if surface.get(key) is not True:
                errors.append(issue("E_S16_RENDERED_SURFACE_REQUIRED", f"rendered_surface_check.{key} must be true"))
        if not isinstance(surface.get("page_count"), int) or surface.get("page_count", 0) <= 0:
            errors.append(issue("E_S16_RENDERED_SURFACE_REQUIRED", "rendered_surface_check.page_count must be a positive integer"))
        if anomalies:
            errors.append(issue("E_S16_RENDERED_SURFACE_REQUIRED", "rendered_surface_check.obvious_rendering_anomalies must be empty for clean export"))


def _validate_s16_compiled_semantic_surface(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    surface = _require_mapping(payload, "rendered_surface_check", "E_S16_PDF_SEMANTIC_SURFACE", errors)
    validation = as_mapping(payload.get("post_writeback_validation"))
    build = as_mapping(payload.get("build_run_report"))
    if surface is None:
        return
    text_ref = _s16_require_safe_ref(surface, "rendered_surface_check", "rendered_text_ref", "E_S16_PDF_SEMANTIC_SURFACE", errors)
    pdf_ref = _s16_require_safe_ref(surface, "rendered_surface_check", "source_pdf_ref", "E_S16_PDF_SEMANTIC_SURFACE", errors)
    if not _s16_valid_sha256(surface.get("rendered_text_sha256")):
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.rendered_text_sha256 must be a lowercase sha256"))
    if not _s16_valid_sha256(surface.get("source_pdf_sha256")):
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.source_pdf_sha256 must be a lowercase sha256"))
    if validation is not None:
        if text_ref is not None and validation.get("pdf_text_ref") != text_ref:
            errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.rendered_text_ref must match post_writeback_validation.pdf_text_ref"))
        if surface.get("rendered_text_sha256") != validation.get("pdf_text_sha256"):
            errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.rendered_text_sha256 must match post_writeback_validation.pdf_text_sha256"))
        if pdf_ref is not None and validation.get("output_pdf_ref") != pdf_ref:
            errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.source_pdf_ref must match post_writeback_validation.output_pdf_ref"))
        if surface.get("source_pdf_sha256") != validation.get("output_pdf_sha256"):
            errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.source_pdf_sha256 must match post_writeback_validation.output_pdf_sha256"))
        if build is not None and pdf_ref is not None and build.get("output_pdf") != pdf_ref:
            errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "compiled target source_pdf_ref must match build_run_report.output_pdf"))
    for key in sorted(S16_COMPILED_SURFACE_BOOL_FIELDS):
        if surface.get(key) is not True:
            errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.{key} must be true for compiled PDF targets"))
    figures = _s16_string_items(surface.get("figures_present"))
    captions = _s16_string_items(surface.get("captions_present"))
    lower_tokens = " ".join(str(item).lower() for item in [*figures, *captions, surface.get("rendered_surface_semantics", "")])
    if any(sentinel in lower_tokens for sentinel in S16_TEMPLATE_SENTINELS):
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check must not use template/placeholder sentinel evidence for compiled PDF targets"))

    body_citations = _require_s16_list(surface, "rendered_surface_check", "body_citation_anchors", "E_S16_PDF_SEMANTIC_SURFACE", errors)
    if not body_citations:
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "compiled PDF targets require rendered_surface_check.body_citation_anchors to prove body citation use"))
    references = _require_s16_list(surface, "rendered_surface_check", "reference_entries", "E_S16_PDF_SEMANTIC_SURFACE", errors)
    if not references:
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "compiled PDF targets require rendered_surface_check.reference_entries to prove non-empty rendered references"))

    exported_kinds = {
        str(record.get("path") or ""): str(record.get("kind") or "")
        for record in (as_mapping(payload.get("export_manifest")) or {}).get("exported_files", [])
        if isinstance(record, dict)
    }
    exported_paths = set(exported_kinds)
    hash_paths = {
        str(record.get("path") or "")
        for record in payload.get("file_hash_manifest", [])
        if isinstance(record, dict)
    }
    figure_files = {
        str(record.get("figure_id")): str(record.get("exported_file"))
        for record in payload.get("figure_file_checklist", [])
        if (
            isinstance(record, dict)
            and record.get("status") == "pass"
            and is_non_empty_string(record.get("figure_id"))
            and is_non_empty_string(record.get("exported_file"))
        )
    }

    callouts = surface.get("visual_formal_callouts")
    if not is_non_empty_mapping_list(callouts):
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.visual_formal_callouts must be a non-empty list for compiled PDF targets"))
        callout_ids: set[str] = set()
    else:
        assert isinstance(callouts, list)
        callout_ids = set()
        for idx, record in enumerate(callouts):
            assert isinstance(record, dict)
            for key in ("callout_id", "artifact_id", "artifact_type", "callout_text"):
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_callouts[{idx}].{key} must be a non-empty string"))
            artifact_type = record.get("artifact_type")
            if artifact_type not in S16_VISUAL_FORMAL_ARTIFACT_TYPES:
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_callouts[{idx}].artifact_type invalid"))
            if is_non_empty_string(record.get("artifact_id")):
                callout_ids.add(str(record["artifact_id"]))

    artifact_refs = surface.get("visual_formal_artifact_refs")
    if not is_non_empty_mapping_list(artifact_refs):
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.visual_formal_artifact_refs must be a non-empty list for compiled PDF targets"))
        artifact_ids: set[str] = set()
    else:
        assert isinstance(artifact_refs, list)
        artifact_ids = set()
        for idx, record in enumerate(artifact_refs):
            assert isinstance(record, dict)
            for key in ("artifact_id", "artifact_type", "source_ref", "status"):
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].{key} must be a non-empty string"))
            artifact_type = record.get("artifact_type")
            if artifact_type not in S16_VISUAL_FORMAL_ARTIFACT_TYPES:
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].artifact_type invalid"))
            if record.get("status") != "pass":
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].status must be pass"))
            source_ref = record.get("source_ref")
            if is_non_empty_string(source_ref) and not _s09_path_is_safe(str(source_ref)):
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].source_ref must be safe"))
            exported_file = record.get("exported_file")
            if not is_non_empty_string(exported_file) or not _s09_path_is_safe(str(exported_file)):
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].exported_file must be a safe non-empty path"))
            elif str(exported_file) not in exported_paths or str(exported_file) not in hash_paths:
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].exported_file must be exported and hash-listed"))
            elif exported_kinds.get(str(exported_file)) != S16_VISUAL_FORMAL_EXPORT_KIND_BY_ARTIFACT_TYPE.get(str(artifact_type)):
                errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].exported_file kind must match artifact_type"))
            if is_non_empty_string(record.get("artifact_id")):
                artifact_id = str(record["artifact_id"])
                artifact_ids.add(artifact_id)
                if artifact_type == "figure":
                    expected_figure_file = figure_files.get(artifact_id)
                    if not expected_figure_file:
                        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].artifact_id must match a passing figure_file_checklist entry"))
                    elif is_non_empty_string(exported_file) and str(exported_file) != expected_figure_file:
                        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"rendered_surface_check.visual_formal_artifact_refs[{idx}].exported_file must match figure_file_checklist for {artifact_id}"))

    missing_artifacts = sorted(callout_ids - artifact_ids)
    if missing_artifacts:
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", f"visual/formal callouts lack artifact refs {missing_artifacts}"))

    detected_internal = _require_s16_list(surface, "rendered_surface_check", "forbidden_internal_terms_detected", "E_S16_PDF_SEMANTIC_SURFACE", errors, allow_empty=True)
    if detected_internal:
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.forbidden_internal_terms_detected must be empty for compiled PDF targets"))
    leaked_unresolved = _require_s16_list(surface, "rendered_surface_check", "unresolved_paper_facing_phrases_detected", "E_S16_PDF_SEMANTIC_SURFACE", errors, allow_empty=True)
    if leaked_unresolved:
        errors.append(issue("E_S16_PDF_SEMANTIC_SURFACE", "rendered_surface_check.unresolved_paper_facing_phrases_detected must be empty for compiled PDF targets"))

    attribution = _require_mapping(payload, "compiled_semantic_failure_attribution", "E_S16_SEMANTIC_FAILURE_ATTRIBUTION", errors)
    if attribution is not None:
        for route_key, required_stages in sorted(S16_SEMANTIC_FAILURE_ATTRIBUTION_ROUTES.items()):
            route = set(_require_s16_list(attribution, "compiled_semantic_failure_attribution", route_key, "E_S16_SEMANTIC_FAILURE_ATTRIBUTION", errors))
            missing = sorted(required_stages - route)
            if missing:
                errors.append(issue("E_S16_SEMANTIC_FAILURE_ATTRIBUTION", f"compiled_semantic_failure_attribution.{route_key} missing stages {missing}"))


def _validate_s16_manifests(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required_manifest_paths = _collect_s16_required_manifest_paths(payload)
    manifest = _require_mapping(payload, "export_manifest", "E_S16_EXPORT_MANIFEST_REQUIRED", errors)
    exported = manifest.get("exported_files") if manifest is not None else None
    exported_paths: set[str] = set()
    exported_hashes: dict[str, str] = {}
    if not is_non_empty_mapping_list(exported):
        errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", "export_manifest.exported_files must be a non-empty list of mappings"))
    else:
        assert isinstance(exported, list)
        for idx, record in enumerate(exported):
            assert isinstance(record, dict)
            for key in ("path", "kind", "sha256"):
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", f"export_manifest.exported_files[{idx}].{key} must be a non-empty string"))
            path = str(record.get("path") or "")
            if path:
                exported_paths.add(path)
                if not _s09_path_is_safe(path):
                    errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", f"export_manifest.exported_files[{idx}].path must be safe"))
                sha = str(record.get("sha256") or "")
                if path in exported_hashes and exported_hashes[path] != sha:
                    errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", f"export_manifest.exported_files[{idx}] conflicts with previous hash for {path!r}"))
                exported_hashes[path] = sha
            if record.get("kind") not in S16_EXPORT_KINDS:
                errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", f"export_manifest.exported_files[{idx}].kind invalid"))
            if not _s16_valid_sha256(record.get("sha256")):
                errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", f"export_manifest.exported_files[{idx}].sha256 must be a lowercase sha256"))

    hashes = payload.get("file_hash_manifest")
    hash_paths: set[str] = set()
    file_hashes: dict[str, str] = {}
    if not is_non_empty_mapping_list(hashes):
        errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", "file_hash_manifest must be a non-empty list of mappings"))
    else:
        assert isinstance(hashes, list)
        for idx, record in enumerate(hashes):
            assert isinstance(record, dict)
            for key in ("path", "sha256"):
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest[{idx}].{key} must be a non-empty string"))
            path = str(record.get("path") or "")
            if path:
                hash_paths.add(path)
                if not _s09_path_is_safe(path):
                    errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest[{idx}].path must be safe"))
                sha = str(record.get("sha256") or "")
                if path in file_hashes and file_hashes[path] != sha:
                    errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest[{idx}] conflicts with previous hash for {path!r}"))
                file_hashes[path] = sha
            if not _s16_valid_sha256(record.get("sha256")):
                errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest[{idx}].sha256 must be a lowercase sha256"))
    missing_hashes = sorted(exported_paths - hash_paths)
    if missing_hashes:
        errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest missing exported files {missing_hashes}"))
    missing_required_exports = sorted(required_manifest_paths - exported_paths)
    if missing_required_exports:
        errors.append(issue("E_S16_EXPORT_MANIFEST_REQUIRED", f"export_manifest missing required build/handoff files {missing_required_exports}"))
    missing_required_hashes = sorted(required_manifest_paths - hash_paths)
    if missing_required_hashes:
        errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest missing required build/handoff files {missing_required_hashes}"))
    expected_manifest_hashes = _collect_s16_expected_manifest_hashes(payload)
    for path, (expected_sha, source) in sorted(expected_manifest_hashes.items()):
        exported_sha = exported_hashes.get(path)
        if exported_sha is not None and exported_sha != expected_sha:
            errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"export_manifest hash for {path!r} must match {source}"))
        manifest_sha = file_hashes.get(path)
        if manifest_sha is not None and manifest_sha != expected_sha:
            errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest hash for {path!r} must match {source}"))
    mismatched_hashes = sorted(path for path in exported_paths & hash_paths if exported_hashes.get(path) != file_hashes.get(path))
    if mismatched_hashes:
        errors.append(issue("E_S16_HASH_MANIFEST_REQUIRED", f"file_hash_manifest hash mismatch for exported files {mismatched_hashes}"))

    checklist = payload.get("figure_file_checklist")
    if not is_non_empty_mapping_list(checklist):
        errors.append(issue("E_S16_FIGURE_CAPTION_CHECK_REQUIRED", "figure_file_checklist must be a non-empty list of mappings"))
    else:
        assert isinstance(checklist, list)
        for idx, record in enumerate(checklist):
            assert isinstance(record, dict)
            for key in ("figure_id", "source_data_ref", "exported_file", "caption_ref", "status"):
                if not is_non_empty_string(record.get(key)):
                    errors.append(issue("E_S16_FIGURE_CAPTION_CHECK_REQUIRED", f"figure_file_checklist[{idx}].{key} must be a non-empty string"))
            if record.get("status") != "pass":
                errors.append(issue("E_S16_FIGURE_CAPTION_CHECK_REQUIRED", f"figure_file_checklist[{idx}].status must be pass"))
            if is_non_empty_string(record.get("exported_file")) and not _s09_path_is_safe(str(record["exported_file"])):
                errors.append(issue("E_S16_FIGURE_CAPTION_CHECK_REQUIRED", f"figure_file_checklist[{idx}].exported_file must be safe"))


def _validate_s16_data_repo_handoff(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    data_check = _require_mapping(payload, "data_availability_statement_check", "E_S16_DATA_AVAILABILITY_REQUIRED", errors)
    _require_mapping_fields(data_check, "data_availability_statement_check", ["statement_ref", "matches_data_inventory"], "E_S16_DATA_AVAILABILITY_REQUIRED", errors)
    if data_check is not None and data_check.get("matches_data_inventory") != "pass":
        errors.append(issue("E_S16_DATA_AVAILABILITY_REQUIRED", "data_availability_statement_check.matches_data_inventory must be pass"))

    supplement = _require_mapping(payload, "supplement_manifest", "E_S16_SUPPLEMENT_MANIFEST_REQUIRED", errors)
    _validate_s16_path_list(supplement, "supplement_manifest", "files", "E_S16_SUPPLEMENT_MANIFEST_REQUIRED", errors, allow_empty=True)
    missing = _validate_s16_path_list(supplement, "supplement_manifest", "missing_or_untracked", "E_S16_SUPPLEMENT_MANIFEST_REQUIRED", errors, allow_empty=True)
    if missing:
        errors.append(issue("E_S16_SUPPLEMENT_MANIFEST_REQUIRED", "supplement_manifest.missing_or_untracked must be empty for clean export"))

    repo = _require_mapping(payload, "repository_hygiene_report", "E_S16_REPOSITORY_HYGIENE_REQUIRED", errors)
    _require_mapping_fields(repo, "repository_hygiene_report", ["git_status_summary", "generated_artifact_policy"], "E_S16_REPOSITORY_HYGIENE_REQUIRED", errors)
    dirty = _require_mapping(repo or {}, "dirty_worktree_classification", "E_S16_REPOSITORY_HYGIENE_REQUIRED", errors)
    if dirty is not None:
        for key in ("intended_outputs", "source_changes", "unexpected_dirty_paths"):
            if key not in dirty:
                errors.append(issue("E_S16_REPOSITORY_HYGIENE_REQUIRED", f"dirty_worktree_classification.{key} must be present"))
        _validate_s16_path_list(dirty, "repository_hygiene_report.dirty_worktree_classification", "intended_outputs", "E_S16_REPOSITORY_HYGIENE_REQUIRED", errors)
        _validate_s16_path_list(dirty, "repository_hygiene_report.dirty_worktree_classification", "source_changes", "E_S16_REPOSITORY_HYGIENE_REQUIRED", errors, allow_empty=True)
        _validate_s16_path_list(dirty, "repository_hygiene_report.dirty_worktree_classification", "unexpected_dirty_paths", "E_S16_REPOSITORY_HYGIENE_REQUIRED", errors, allow_empty=True)
    if dirty is not None and dirty.get("unexpected_dirty_paths"):
        errors.append(issue("E_S16_REPOSITORY_HYGIENE_REQUIRED", "dirty_worktree_classification.unexpected_dirty_paths must be empty"))

    handoff = _require_mapping(payload, "manager_handoff_report", "E_S16_HANDOFF_COMPLETENESS_REQUIRED", errors)
    _validate_s16_path_list(handoff, "manager_handoff_report", "human_readable_outputs", "E_S16_HANDOFF_COMPLETENESS_REQUIRED", errors)
    for key in ("known_limitations", "owner_actions_required"):
        _require_s16_list(handoff, "manager_handoff_report", key, "E_S16_HANDOFF_COMPLETENESS_REQUIRED", errors)
    if handoff is not None and handoff.get("recommended_next_step") not in S16_RECOMMENDED_NEXT_STEPS:
        errors.append(issue("E_S16_HANDOFF_COMPLETENESS_REQUIRED", "manager_handoff_report.recommended_next_step invalid"))

    owner = _require_mapping(payload, "owner_gate_report", "E_S16_OWNER_GATE_REQUIRED", errors)
    _require_s16_list(owner, "owner_gate_report", "required_owner_decisions", "E_S16_OWNER_GATE_REQUIRED", errors)
    if owner is not None and owner.get("external_submission_authorized") is not False:
        errors.append(issue("E_S16_OWNER_GATE_REQUIRED", "owner_gate_report.external_submission_authorized must be false"))

    route = _require_mapping(payload, "human_feedback_intake_route", "E_S16_FEEDBACK_ROUTE_REQUIRED", errors)
    if route is not None:
        for key, expected in S16_FEEDBACK_ROUTES.items():
            if route.get(key) != expected:
                errors.append(issue("E_S16_FEEDBACK_ROUTE_REQUIRED", f"human_feedback_intake_route.{key} must be {expected}"))


def _validate_s16_validator(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    validator = _require_mapping(payload, "validator_report", "E_S16_VALIDATOR_REPORT_REQUIRED", errors)
    _require_mapping_fields(validator, "validator_report", ["agent_type", "verification_status"], "E_S16_VALIDATOR_REPORT_REQUIRED", errors)
    checks = _require_s16_list(validator, "validator_report", "checks_completed", "E_S16_VALIDATOR_REPORT_REQUIRED", errors)
    missing_checks = sorted(S16_REQUIRED_VERIFIER_CHECKS - checks)
    if missing_checks:
        errors.append(issue("E_S16_VALIDATOR_REPORT_REQUIRED", f"validator_report.checks_completed missing {missing_checks}"))
    if validator is not None:
        if validator.get("agent_type") != "verifier":
            errors.append(issue("E_S16_VALIDATOR_REPORT_REQUIRED", "validator_report.agent_type must be verifier"))
        if validator.get("verification_status") not in {"pass", "pass_with_risks"}:
            errors.append(issue("E_S16_VALIDATOR_REPORT_REQUIRED", "validator_report.verification_status must be pass or pass_with_risks"))
    if not is_non_empty_string_list(payload.get("remaining_risks")):
        errors.append(issue("E_S16_REMAINING_RISKS_REQUIRED", "remaining_risks must be a non-empty list of strings"))


def _validate_s16_export_handoff_package(payload: dict[str, Any], errors: list[ValidationIssue]) -> None:
    _require_s16_required_modules(payload, errors)
    _validate_s16_authority(payload, errors)
    _validate_s16_evidence_mode(payload, errors)
    _delivery_target_kind, compiled_target = _validate_s16_delivery_target(payload, errors)
    _validate_s16_readiness_and_upstream(payload, errors)
    if compiled_target:
        _validate_s16_compiled_readiness(payload, errors)
        _validate_s16_compiled_source_writeback(payload, errors)
    _validate_s16_build_and_render(payload, errors)
    if compiled_target:
        _validate_s16_compiled_semantic_surface(payload, errors)
    _validate_s16_manifests(payload, errors)
    _validate_s16_data_repo_handoff(payload, errors)
    _validate_s16_validator(payload, errors)


def _validate_material_payload(data: dict[str, Any], errors: list[ValidationIssue], packet: dict[str, Any] | None = None) -> None:
    payload = _payload(data, errors)
    if payload is None:
        return
    material_type = data.get("material_type")
    if material_type == "EvidenceInventory":
        _validate_evidence_inventory(payload, errors)
    elif material_type == "ClaimBoundaryMap":
        _validate_claim_boundary_map(data, payload, errors)
    elif material_type == "ReaderSpine":
        _validate_reader_spine(payload, errors)
    elif material_type == "TerminologyRegister":
        return
    elif material_type == "OwnerIntake":
        _validate_s00_owner_intake(payload, errors)
    elif material_type == "OwnerSemanticContract":
        _validate_s00_owner_semantic_contract(payload, errors)
    elif material_type == "S01InventoryInput":
        _validate_s01_inventory_input(payload, errors)
    elif material_type == "S01SourceEvidenceInventory":
        _validate_s01_source_evidence_inventory(payload, errors)
    elif material_type == "S02ResearchDossier":
        _validate_s02_research_dossier(payload, errors)
    elif material_type == "S03ContributionOptions":
        _validate_s03_contribution_options(payload, errors)
    elif material_type == "S04ClaimAdmissibility":
        _validate_s04_claim_admissibility(payload, errors)
    elif material_type == "S05ReaderSpine":
        _validate_s05_reader_spine(payload, errors)
    elif material_type == "S06ObjectGranularity":
        _validate_s06_object_granularity(payload, errors)
    elif material_type == "S07RhetoricSurfaceControl":
        _validate_s07_rhetoric_surface_control(payload, errors)
    elif material_type == "S08VisualFormalPlan":
        _validate_s08_visual_formal_plan(payload, errors)
    elif material_type == "S09ARichControlBundle":
        _validate_s09a_rich_control_bundle(payload, errors)
    elif material_type == "S09BTaskPacketAssembly":
        _validate_s09b_task_packet_assembly(payload, errors)
    elif material_type == "S10CandidateTextReturn":
        _validate_s10_candidate_text_return(payload, errors, packet)
    elif material_type == "S11FigureCaptionArtifactBundle":
        _validate_s11_figure_caption_artifact_bundle(payload, errors)
    elif material_type == "S12IntegrationConsistencyReport":
        _validate_s12_integration_consistency_report(payload, errors)
    elif material_type == "S13AdversarialReviewReport":
        _validate_s13_adversarial_review_report(payload, errors)
    elif material_type == "S14BackflowRepairPlan":
        _validate_s14_backflow_repair_plan(payload, errors)
    elif material_type == "S15RepairExecutionReport":
        _validate_s15_repair_execution_report(payload, errors)
    elif material_type == "S16ExportHandoffPackage":
        _validate_s16_export_handoff_package(payload, errors)


def validate(data: Any, packet: dict[str, Any] | None = None) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    errors.extend(
        require_string_fields(
            data,
            ["schema_version", "material_id", "version", "status", "material_type"],
            "E_ENVELOPE_REQUIRED",
        )
    )
    if data.get("schema_version") and data.get("schema_version") != "ppg-material/v0.1":
        errors.append(issue("E_ENVELOPE_REQUIRED", "schema_version must be ppg-material/v0.1"))
    errors.extend(validate_runtime_status(data))
    _validate_material_payload(data, errors, packet)
    errors.extend(lint_paper_facing_terms(data))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PPG material fixtures.")
    parser.add_argument("material", type=Path)
    parser.add_argument("--packet", type=Path, help="Authoritative S09B-emitted TaskPacket for S10CandidateTextReturn validation.")
    args = parser.parse_args()
    path = args.material
    data, errors = load_document(path)
    if errors:
        return print_result(path, errors)
    packet = None
    if args.packet is not None:
        packet, packet_errors = load_document(args.packet)
        if packet_errors:
            return print_result(args.packet, packet_errors)
        if not isinstance(packet, dict):
            return print_result(args.packet, [issue("E_S10_PACKET_OBLIGATIONS_REQUIRED", "S10 --packet must be a mapping")])
    return print_result(path, validate(data, packet=packet))


if __name__ == "__main__":
    raise SystemExit(main())
