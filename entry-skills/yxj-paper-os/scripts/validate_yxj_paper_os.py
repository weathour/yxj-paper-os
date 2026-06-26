#!/usr/bin/env python3
"""yxj-paper-os installed-source scaffold and fixture validators."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print(f"PyYAML is required for yxj-paper-os validators: {exc}", file=sys.stderr)
    sys.exit(2)

KNOWN_VALIDATORS = {
    'validate_required_artifacts', 'validate_package_metadata', 'validate_schema_fields',
    'validate_cross_references', 'validate_route_enums', 'validate_confirmation_gates',
    'validate_decision_ledger', 'validate_forbidden_actions', 'validate_target_scaffold_checklist',
    'validate_plugin_bundle_conditionals', 'validate_privacy_boundaries', 'validate_handoff_prompt',
    'validate_paper_root_detection', 'validate_profile_schema', 'validate_state_machine',
    'validate_task_packet', 'validate_dispatch_not_complete', 'validate_subagent_output',
    'validate_source_map', 'validate_research_triplet_collection', 'validate_citation_support_bank',
    'validate_evidence_bank', 'validate_motivation_confirmation', 'validate_rationale_matrix',
    'validate_claim_support', 'validate_review_independence', 'validate_review_backflow',
    'validate_export_manifest', 'validate_project_brief', 'validate_research_dossier',
    'validate_exemplar_learning', 'validate_sota_gap_map', 'validate_novelty_options',
    'validate_section_blueprints', 'validate_workflow_plan', 'validate_team_gate',
    'validate_department_route_card',
    'validate_department_charters', 'validate_department_material_manifest',
    'validate_department_lane_registry', 'validate_required_function_material_map',
    'validate_no_orphan_material_owner', 'validate_no_orphan_function_owner',
    'validate_no_public_department_exposure', 'validate_no_route_card_completion_claim',
    'validate_manager_boot_checklist', 'validate_department_state_projection',
    'validate_department_handoff_report',
    'validate_validator_report', 'validate_source_locator_resolution', 'validate_owner_lane_closure',
    'validate_validator_reference_closure', 'validate_task_status_transitions',
    'validate_direct_execution_adapter', 'validate_verifier_review', 'validate_pua_telemetry',
    'validate_agent_lane_department_binding', 'validate_task_material_io',
    'validate_narrative_object_binding', 'validate_template_object_binding',
    'validate_template_mirror_sync', 'validate_fixture_matrix_nonempty',
    'validate_manager_handoff_v2', 'validate_actor_provenance_present',
    'validate_actor_provenance_artifact_trusted', 'validate_effective_actor_identity_resolved',
    'validate_derived_sensitivity_classification', 'validate_manager_direct_inferred_or_declared',
    'validate_manager_direct_intervention_declared', 'validate_manager_direct_independent_review',
    'validate_no_manager_self_certification', 'validate_role_separation_for_paper_facing_tasks',
    'validate_manager_direct_handoff_disclosure', 'validate_completion_state_limited_without_independent_review',
    'validate_reader_spine_brief', 'validate_object_representation_matrix',
    'validate_template_quant_profile', 'validate_section_function_budget',
    'validate_visual_budget', 'validate_reader_experience_review_gate',
    'validate_narrative_backflow', 'validate_repository_hygiene_report',
    'validate_expression_design_object_binding', 'validate_cognitive_load_budget',
    'validate_explanation_ladder', 'validate_rhetorical_move_matrix',
    'validate_claim_evidence_visibility_map', 'validate_terminology_register',
    'validate_cognitive_load_budget_consumed', 'validate_rhetorical_move_matrix_consumed',
    'validate_explanation_ladder_progression', 'validate_claim_evidence_visibility',
    'validate_terminology_register_surface',
    'validate_main_text_surface_rules', 'validate_no_internal_codes_in_main_prose',
    'validate_no_snake_case_constraints_in_main_prose', 'validate_no_raw_method_ids_in_main_prose',
    'validate_no_defensive_claim_boundary_wall', 'validate_no_bare_citekeys_in_export',
    'validate_rendered_pdf_surface_text',
    'validate_reviewer_question_map', 'validate_main_text_construction_matrix_refs',
    'validate_claim_citation_capsule_support', 'validate_result_package_claim_boundary',
    'validate_single_writer_lock_held', 'validate_reader_surface_tutor_review_spans',
    'validate_no_internal_codes_in_rendered_text',
    'validate_nature_figure_contract', 'validate_nature_figure_aesthetic_profile',
    'validate_panel_evidence_map', 'validate_figure_backend_route',
    'validate_figure_source_data_statistics', 'validate_figure_image_integrity_record',
    'validate_nature_caption_legend', 'validate_nature_figure_qa_report',
    'validate_figure_export_bundle',
    'validate_nature_source_inventory',
    'validate_nature_absorption_package',
    'validate_company_skill_registry',
    'validate_paper_reader_package',
    'validate_search_strategy_dossier',
    'validate_citation_verification_report',
    'validate_section_move_plan',
    'validate_journal_style_profile',
    'validate_polishing_repair_report',
    'validate_data_availability_plan',
    'validate_reviewer_panel_report',
    'validate_response_action_map',
    'validate_presentation_plan',
    'validate_patent_draft_boundary',
}

DEFAULT_ALLOWED_OWNER_LANES = {
    'plugin-packaging-lane', 'scaffold-executor', 'domain-analyst', 'workspace-architect',
    'profile-architect', 'state-steward', 'interview-owner', 'source-map-curator',
    'research-director', 'scene-analyst', 'exemplar-learner', 'sota-mapper',
    'novelty-panel', 'novelty-panel-designer', 'citation-banker', 'evidence-curator',
    'paper-architect', 'paper-owner-gate', 'manuscript-owner', 'method-verifier',
    'figure-owner', 'review-director', 'style-auditor', 'export-owner', 'migration-owner',
    'validator-designer', 'docs-writer', 'artifact-schema-designer', 'omx-workflow-router',
    'yxj-wiki-bridge', 'verifier', 'final-verifier', 'execution-coordinator',
    'repository-hygiene-owner',
}


def scaffold_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_lane_registry(root: Path | None = None) -> dict[str, Any]:
    base = root or scaffold_root()
    path = base / 'skills/yxj-paper-execute/references/agent-lane-registry.yaml'
    data = load_yaml(path, {})
    return data if isinstance(data, dict) else {}


def allowed_owner_lanes(root: Path | None = None) -> set[str]:
    registry = load_lane_registry(root)
    lanes: set[str] = set()
    for entry in registry.get('lanes', []):
        if not isinstance(entry, dict):
            continue
        lane_id = entry.get('lane_id')
        if isinstance(lane_id, str) and lane_id:
            lanes.add(lane_id)
    return lanes or set(DEFAULT_ALLOWED_OWNER_LANES)


def lane_registry_by_id(root: Path | None = None) -> dict[str, dict[str, Any]]:
    registry = load_lane_registry(root)
    return {
        str(entry.get('lane_id')): entry
        for entry in registry.get('lanes', [])
        if isinstance(entry, dict) and entry.get('lane_id')
    }


def infer_root_from_fixture(fixture: Path) -> Path:
    fixture = fixture.resolve()
    for parent in [fixture, *fixture.parents]:
        if (parent / '.codex-plugin/plugin.json').exists():
            return parent
    return scaffold_root()


REQUIRED_SKILLS = [
    'yxj-paper-index', 'yxj-paper-state', 'yxj-paper-interview', 'yxj-paper-plan',
    'yxj-paper-execute', 'yxj-paper-research', 'yxj-paper-novelty', 'yxj-paper-evidence',
    'yxj-paper-paperspine', 'yxj-paper-review', 'yxj-paper-figures', 'yxj-paper-export',
    'yxj-paper-migration',
]

PUBLIC_SKILLS_RESOURCE = './entry-skills/'
PUBLIC_ENTRY_SKILLS = {'yxj-paper-os'}

REQUIRED_TEMPLATES = [
    'paper-profile.yaml', 'state.yaml', 'source-map.yaml', 'task-packet.yaml',
    'research-dossier.yaml', 'citation-bank.yaml', 'motivation.yaml', 'evidence-bank.yaml',
    'rationale-matrix.yaml', 'review-output.yaml', 'validator-report.yaml', 'export-manifest.yaml',
]

REQUIRED_V2_TEMPLATES = [
    'department-io-contract.yaml', 'reader-spine-brief.yaml',
    'object-representation-matrix.yaml', 'template-quant-profile.yaml',
    'section-function-budget.yaml', 'visual-table-algorithm-formula-budget.yaml',
    'reader-experience-review-report.yaml', 'narrative-backflow-task.yaml',
    'template-mirror-policy.yaml', 'repository-hygiene-report.yaml',
    'main-text-surface-rules.yaml', 'manager-direct-intervention.yaml',
    'department-charter.yaml', 'department-material-manifest.yaml',
    'department-lane-registry.yaml', 'department-state.yaml',
    'department-handoff-report.yaml', 'required-function-material-map.yaml',
    'manager-boot-checklist.yaml', 'department-route-card.yaml',
    'cognitive-load-budget.yaml', 'explanation-ladder.yaml',
    'rhetorical-move-matrix.yaml', 'claim-evidence-visibility-map.yaml',
    'terminology-register.yaml', 'expression-design-bundle.yaml',
    'nature-figure-contract.yaml', 'nature-figure-aesthetic-profile.yaml',
    'nature-panel-evidence-map.yaml', 'figure-backend-route.yaml',
    'figure-source-data-statistics.yaml', 'figure-image-integrity-record.yaml',
    'nature-caption-legend-brief.yaml', 'nature-figure-qa-report.yaml',
    'figure-export-bundle.yaml',
    'nature-source-inventory.yaml', 'nature-absorption-package.yaml',
    'company-skill-registry.yaml', 'paper-reader-package.yaml',
    'search-strategy-dossier.yaml', 'citation-verification-report.yaml',
    'section-move-plan.yaml', 'journal-style-profile.yaml',
    'polishing-repair-report.yaml', 'data-availability-plan.yaml',
    'reviewer-panel-report.yaml', 'response-action-map.yaml',
    'presentation-plan.yaml', 'patent-draft-boundary.yaml',
]

REQUIRED_DEPARTMENT_FIXTURES = {
    'valid': {
        'valid-department-accountability-registry',
        'valid-manager-boot-with-department-state',
        'valid-task-packet-with-department-registry-binding',
    },
    'invalid': {
        'invalid-missing-department-charter',
        'invalid-orphan-material-no-owner-department',
        'invalid-orphan-function-no-primary-department',
        'invalid-lane-agent-type-without-department',
        'invalid-internal-department-public-exposure',
        'invalid-skill-registry-hidden-manager',
        'invalid-route-card-claims-completion',
        'invalid-manager-boot-omits-department-state-gap',
        'invalid-department-state-claims-completion-evidence',
    },
}

REQUIRED_ROOT_FILES = [
    '.codex-plugin/plugin.json',
    'skills/yxj-paper-index/references/workspace-contract.md',
    'skills/yxj-paper-state/references/state-contract.md',
    'skills/yxj-paper-execute/references/runtime-execution-contract.md',
    'skills/yxj-paper-execute/references/agent-contract.md',
    'skills/yxj-paper-execute/references/agent-lane-registry.yaml',
    'skills/yxj-paper-index/references/source-influences.md',
    'skills/yxj-paper-index/references/department-manager-governance.md',
    'entry-skills/yxj-paper-os/references/department-manager-governance.md',
    'docs/architecture.md', 'docs/operation-guide.md', 'docs/migration-notes.md',
    'docs/production-readiness-checklist.md',
]


def load_yaml(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as fh:
        return yaml.safe_load(fh) or default


def yaml_has_duplicate_keys(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        root = yaml.compose(path.read_text(encoding='utf-8'))
    except yaml.YAMLError:
        return True

    def visit(node: Any) -> bool:
        if isinstance(node, yaml.MappingNode):
            keys: set[Any] = set()
            for key_node, value_node in node.value:
                key = key_node.value
                if key in keys:
                    return True
                keys.add(key)
                if visit(value_node):
                    return True
        if isinstance(node, yaml.SequenceNode):
            return any(visit(item) for item in node.value)
        return False

    return visit(root) if root is not None else False


def dump_result(ok: bool, failures: list[str], detail: dict[str, Any] | None = None) -> int:
    payload = {'ok': ok, 'failures': sorted(set(failures)), 'detail': detail or {}}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def skill_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError('missing frontmatter')
    end = text.find('\n---\n', 4)
    if end < 0:
        raise ValueError('unterminated frontmatter')
    return yaml.safe_load(text[4:end]) or {}


def require_path(data: Any, dotted_path: str) -> bool:
    cur = data
    for part in dotted_path.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return False
    return True


def check_v2_template_shapes(root: Path) -> list[str]:
    failures: list[str] = []
    template_root = root / 'skills/yxj-paper-index/templates'
    checks = {
        'reader-spine-brief.yaml': (
            'validate_reader_spine_brief',
            ['target_reader', 'paper_spine.one_sentence', 'section_question_sequence', 'claim_visibility', 'reviewer_expectations', 'owner_gated_decisions'],
        ),
        'object-representation-matrix.yaml': (
            'validate_object_representation_matrix',
            ['objects', 'required_object_ids'],
        ),
        'template-quant-profile.yaml': (
            'validate_template_quant_profile',
            ['exemplar_manifest', 'section_function_distribution', 'visual_formal_budget.figures', 'comparison_patterns.baseline_ordering', 'target_manuscript_gap_audit'],
        ),
        'section-function-budget.yaml': (
            'validate_section_function_budget',
            ['sections'],
        ),
        'visual-table-algorithm-formula-budget.yaml': (
            'validate_visual_budget',
            ['items'],
        ),
        'reader-experience-review-report.yaml': (
            'validate_reader_experience_review_gate',
            ['review_scope.manuscript_paths', 'checks.lab_notebook_smell', 'checks.reader_question_flow', 'checks.object_granularity_progression', 'checks.template_fit', 'findings'],
        ),
        'narrative-backflow-task.yaml': (
            'validate_narrative_backflow',
            ['source_review_artifact', 'source_finding_id', 'owner_department', 'owner_lane', 'agent_type', 'input_materials', 'expected_output_materials', 'backflow_route.return_validator', 'state_ingestion.ledger_path'],
        ),
        'repository-hygiene-report.yaml': (
            'validate_repository_hygiene_report',
            ['scope.paper_root', 'scope.commands', 'worktree.status', 'worktree.total_dirty_entries', 'worktree.disallowed_dirty_entries', 'sibling_or_parent_contamination.status', 'snapshot_freshness.status', 'export_manifest_hashes.status', 'external_submission.status', 'delivery_cleanliness_gate.status'],
        ),
        'main-text-surface-rules.yaml': (
            'validate_main_text_surface_rules',
            ['owner_department', 'consumers', 'required_validators', 'rules'],
        ),
        'department-charter.yaml': (
            'validate_department_charters',
            ['artifact_type', 'departments', 'single_public_entry', 'public_surface_allowed', 'completion_invariant'],
        ),
        'department-material-manifest.yaml': (
            'validate_department_material_manifest',
            ['artifact_type', 'charter_ref', 'materials', 'manifest_rules.department_state_is_completion_evidence', 'manifest_rules.department_route_card_is_completion_evidence'],
        ),
        'department-lane-registry.yaml': (
            'validate_department_lane_registry',
            ['artifact_type', 'department_lanes', 'installed_agent_types', 'rules.use_installed_agent_types_only', 'rules.department_sops_are_internal_not_public_skills'],
        ),
        'department-state.yaml': (
            'validate_department_state_projection',
            ['artifact_type', 'state_kind', 'is_completion_evidence', 'projection_rules.department_state_does_not_close_tasks', 'projection_rules.completion_requires_collected_outputs_validators_ledger_and_state_transition', 'department_status'],
        ),
        'department-handoff-report.yaml': (
            'validate_department_handoff_report',
            ['artifact_type', 'handoff_identity.from_department_id', 'scope.requested_outcome', 'inputs_consumed', 'outputs_produced', 'validation.route_card_is_completion_evidence', 'validation.department_state_is_completion_evidence', 'ledger_and_state.state_transition_required', 'pmo_summary.next_safe_action'],
        ),
        'required-function-material-map.yaml': (
            'validate_required_function_material_map',
            ['artifact_type', 'functions', 'rules.every_function_requires_primary_department', 'rules.every_function_requires_material_output', 'rules.every_function_requires_validator_gate', 'rules.every_function_requires_backflow_target'],
        ),
        'manager-boot-checklist.yaml': (
            'validate_manager_boot_checklist',
            ['artifact_type', 'public_identity', 'boot_context.requested_outcome', 'boot_context.active_gate', 'boot_context.stop_condition', 'state_first_reads', 'registry_reads', 'route_selection.route_mode', 'material_accountability.primary_dri', 'activation_report_required_fields', 'non_completion_boundaries.department_state_is_completion_evidence'],
        ),
        'department-route-card.yaml': (
            'validate_department_route_card',
            ['card_id', 'task_id', 'department_id', 'department_manager.name', 'department_manager.existence_form', 'department_manager.authority_scope.may_decompose', 'department_manager.authority_scope.may_request_lanes', 'department_manager.authority_scope.may_certify_completion', 'request.summary', 'request.current_gate', 'input_materials_consumed', 'proposed_lanes', 'requested_task_packets', 'expected_material_outputs', 'validators.required', 'backflow_route.on_validator_failure', 'team_gate_status.status', 'recursion_control.recursive_subagent_spawning_allowed', 'authority_boundaries.route_card_is_completion_evidence', 'authority_boundaries.completion_invariant', 'pmo_handoff.next_safe_action', 'closure_state'],
        ),
        'cognitive-load-budget.yaml': (
            'validate_cognitive_load_budget',
            ['artifact_id', 'owning_department', 'consumers', 'section_budgets', 'forbidden_overload_rules', 'validator_refs'],
        ),
        'explanation-ladder.yaml': (
            'validate_explanation_ladder',
            ['artifact_id', 'owning_department', 'consumers', 'ladders', 'validator_refs'],
        ),
        'rhetorical-move-matrix.yaml': (
            'validate_rhetorical_move_matrix',
            ['artifact_id', 'owning_department', 'consumers', 'rows', 'validator_refs'],
        ),
        'claim-evidence-visibility-map.yaml': (
            'validate_claim_evidence_visibility_map',
            ['artifact_id', 'owning_department', 'consumers', 'truth_boundary.can_raise_claim_strength', 'claims', 'validator_refs'],
        ),
        'terminology-register.yaml': (
            'validate_terminology_register',
            ['artifact_id', 'owning_department', 'consumers', 'terms', 'validator_refs'],
        ),
        'expression-design-bundle.yaml': (
            'validate_expression_design_object_binding',
            ['artifact_id', 'owning_department', 'consumers', 'typed_object_refs', 'bundle_rules.cannot_bypass_typed_object_validators', 'validator_refs'],
        ),
        'nature-figure-contract.yaml': (
            'validate_nature_figure_contract',
            ['artifact_id', 'owning_department', 'figure_id', 'core_conclusion', 'reader_question', 'figure_archetype', 'panel_hierarchy.hero_panel_id', 'panel_map', 'narrative_object_refs', 'template_object_refs', 'expression_design_object_refs', 'evidence_refs', 'validator_refs'],
        ),
        'nature-figure-aesthetic-profile.yaml': (
            'validate_nature_figure_aesthetic_profile',
            ['artifact_id', 'owning_department', 'figure_id', 'composition.figure_archetype', 'composition.dashboard_equal_panel_bias_check', 'palette.semantic_roles', 'typography.editable_text_required', 'panel_label_policy.lowercase_bold', 'legend_strategy', 'background_policy', 'expression_design_object_refs', 'validator_refs'],
        ),
        'nature-panel-evidence-map.yaml': (
            'validate_panel_evidence_map',
            ['artifact_id', 'owning_department', 'figure_id', 'panels', 'validator_refs'],
        ),
        'figure-backend-route.yaml': (
            'validate_figure_backend_route',
            ['artifact_id', 'owning_department', 'figure_id', 'selected_route', 'route_exclusivity_required', 'final_source_of_truth.type', 'cross_backend_rendering_allowed', 'missing_runtime_policy', 'validator_refs'],
        ),
        'figure-source-data-statistics.yaml': (
            'validate_figure_source_data_statistics',
            ['artifact_id', 'owning_department', 'figure_id', 'conceptual', 'statistics', 'legend_statistics_block', 'backend_route_ref', 'validator_refs'],
        ),
        'figure-image-integrity-record.yaml': (
            'validate_figure_image_integrity_record',
            ['artifact_id', 'owning_department', 'figure_id', 'image_integrity_applicability.status', 'backend_route_ref', 'raster_or_image_panel', 'validator_refs'],
        ),
        'nature-caption-legend-brief.yaml': (
            'validate_nature_caption_legend',
            ['artifact_id', 'owning_department', 'figure_id', 'caption_title', 'panel_descriptions', 'statistics_statement', 'source_data_statement', 'privacy_surface', 'validator_refs'],
        ),
        'nature-figure-qa-report.yaml': (
            'validate_nature_figure_qa_report',
            ['artifact_id', 'owning_department', 'figure_id', 'checks', 'verdict', 'backflow_route', 'validator_refs'],
        ),
        'figure-export-bundle.yaml': (
            'validate_figure_export_bundle',
            ['artifact_id', 'owning_department', 'figure_id', 'source_artifacts', 'outputs', 'editable_text_status', 'final_dimensions', 'manifest_refs', 'hash_provenance.status', 'validator_refs'],
        ),
        'nature-source-inventory.yaml': (
            'validate_nature_source_inventory',
            ['artifact_id', 'owning_department', 'source_repo.name', 'source_repo.url', 'source_repo.commit_hash', 'source_files_required', 'capabilities', 'validator_refs'],
        ),
        'company-skill-registry.yaml': (
            'validate_company_skill_registry',
            ['artifact_id', 'owning_department', 'registry_scope', 'single_public_entry', 'public_surface_allowed', 'capabilities', 'validator_refs'],
        ),
        'nature-absorption-package.yaml': (
            'validate_nature_absorption_package',
            ['artifact_id', 'owning_department', 'source_inventory_ref', 'company_skill_registry_ref', 'capability_material_refs', 'department_backflow_routes', 'closure_invariant', 'validator_refs'],
        ),
        'paper-reader-package.yaml': (
            'validate_paper_reader_package',
            ['artifact_id', 'owning_department', 'source_format', 'source_blocks', 'figure_table_map', 'exact_source_anchors_required', 'summary_only', 'validator_refs'],
        ),
        'search-strategy-dossier.yaml': (
            'validate_search_strategy_dossier',
            ['artifact_id', 'owning_department', 'workflow', 'queries', 'source_tiers', 'deduplication.status', 'failure_log', 'validator_refs'],
        ),
        'citation-verification-report.yaml': (
            'validate_citation_verification_report',
            ['artifact_id', 'owning_department', 'segments', 'export_route.format', 'export_route.reference_manager_ready', 'validator_refs'],
        ),
        'section-move-plan.yaml': (
            'validate_section_move_plan',
            ['artifact_id', 'owning_department', 'paper_type', 'section', 'language', 'journal', 'narrative_object_refs', 'evidence_refs', 'move_sequence', 'validator_refs'],
        ),
        'journal-style-profile.yaml': (
            'validate_journal_style_profile',
            ['artifact_id', 'owning_department', 'journal', 'source_basis', 'style_axes', 'diction_rules', 'forbidden_patterns', 'validator_refs'],
        ),
        'polishing-repair-report.yaml': (
            'validate_polishing_repair_report',
            ['artifact_id', 'owning_department', 'failure_modes', 'repairs', 'phrasebank_application.status', 'chinese_author_alignment.status', 'validator_refs'],
        ),
        'data-availability-plan.yaml': (
            'validate_data_availability_plan',
            ['artifact_id', 'owning_department', 'datasets', 'fair_metadata_checklist.status', 'statement_draft', 'validator_refs'],
        ),
        'reviewer-panel-report.yaml': (
            'validate_reviewer_panel_report',
            ['artifact_id', 'owning_department', 'reviewer_reports', 'cross_review_synthesis', 'technical_failing_map', 'broad_interest_readout', 'validator_refs'],
        ),
        'response-action-map.yaml': (
            'validate_response_action_map',
            ['artifact_id', 'owning_department', 'comments', 'point_by_point_draft.status', 'tone_qa.status', 'invented_line_numbers_present', 'validator_refs'],
        ),
        'presentation-plan.yaml': (
            'validate_presentation_plan',
            ['artifact_id', 'owning_department', 'canonical_department_id', 'narrative_object_refs', 'expression_design_object_refs', 'presentation_narrative_arc', 'slides', 'self_review.status', 'validator_refs'],
        ),
        'patent-draft-boundary.yaml': (
            'validate_patent_draft_boundary',
            ['artifact_id', 'owning_department', 'source_ids', 'source_support_map', 'drafting_aid_only', 'not_legal_opinion', 'no_patentability_guarantee', 'professional_review_gate.required', 'formal_filing_authorized', 'validator_refs'],
        ),
    }
    for filename, (validator, paths) in checks.items():
        data = load_yaml(template_root / filename, {})
        if not isinstance(data, dict):
            failures.append(f'{validator}:invalid_yaml:{filename}')
            continue
        for path in paths:
            if not require_path(data, path):
                failures.append(f'{validator}:missing_field:{filename}:{path}')
        refs = data.get('validator_refs') or []
        if validator not in refs:
            failures.append(f'{validator}:missing_validator_ref:{filename}')
        if not str(data.get('schema_version', '')).startswith('yxj-paper-os/'):
            failures.append(f'{validator}:missing_schema_version:{filename}')
        if filename == 'department-route-card.yaml':
            allowed_departments = {'pmo', 'paper_architecture_and_narrative', 'evidence_and_method', 'manuscript_and_figure_production', 'review_and_governance'}
            allowed_forms = {'contract_only', 'department_manager_subagent', 'team_lane_lead'}
            allowed_team_status = {'not_required', 'recommended', 'approved', 'blocked'}
            if data.get('artifact_type') != 'DepartmentRouteCard':
                failures.append(f'{validator}:wrong_artifact_type:{filename}')
            if data.get('department_id') not in allowed_departments:
                failures.append(f'{validator}:invalid_department_id:{filename}')
            manager = data.get('department_manager') or {}
            if not isinstance(manager, dict) or manager.get('existence_form') not in allowed_forms:
                failures.append(f'{validator}:invalid_existence_form:{filename}')
            authority = manager.get('authority_scope') if isinstance(manager, dict) else {}
            if not isinstance(authority, dict) or authority.get('may_certify_completion') is not False:
                failures.append(f'{validator}:may_certify_completion_not_false:{filename}')
            if not isinstance(authority, dict) or authority.get('may_make_owner_semantic_decisions') is not False:
                failures.append(f'{validator}:may_make_owner_semantic_decisions_not_false:{filename}')
            recursion = data.get('recursion_control') or {}
            if not isinstance(recursion, dict) or recursion.get('recursive_subagent_spawning_allowed') is not False:
                failures.append(f'{validator}:recursive_spawning_not_false:{filename}')
            boundaries = data.get('authority_boundaries') or {}
            if not isinstance(boundaries, dict) or boundaries.get('route_card_is_completion_evidence') is not False:
                failures.append(f'{validator}:route_card_completion_evidence_not_false:{filename}')
            invariant = str(boundaries.get('completion_invariant') or '') if isinstance(boundaries, dict) else ''
            if 'compile -> execute -> collect -> validate -> ingest -> state_transition' not in invariant:
                failures.append(f'{validator}:missing_completion_invariant:{filename}')
            team_gate = data.get('team_gate_status') or {}
            if not isinstance(team_gate, dict) or team_gate.get('status') not in allowed_team_status:
                failures.append(f'{validator}:invalid_team_gate_status:{filename}')
            if team_gate.get('team_recommended') is True and not team_gate.get('ralplan_consensus_ref'):
                failures.append(f'{validator}:team_recommended_without_ralplan:{filename}')

        if filename == 'claim-evidence-visibility-map.yaml':
            rows = data.get('claims') or []
            if not isinstance(rows, list) or not rows:
                failures.append(f'{validator}:missing_claim_rows:{filename}')
            for idx, row in enumerate(rows):
                if not isinstance(row, dict):
                    failures.append(f'{validator}:invalid_claim_row:{filename}:{idx}')
                    continue
                allowed = row.get('allowed_strength') or row.get('allowed_claim_strength')
                evidence = row.get('evidence_strength') or row.get('source_strength') or row.get('support_strength')
                allowed_rank = claim_strength_rank(allowed)
                evidence_rank = claim_strength_rank(evidence)
                if allowed_rank is None:
                    failures.append(f'{validator}:unknown_allowed_strength:{filename}:{idx}')
                if evidence_rank is None:
                    failures.append(f'{validator}:missing_or_unknown_evidence_strength:{filename}:{idx}')
                if allowed_rank is not None and evidence_rank is not None and allowed_rank > evidence_rank:
                    failures.append(f'{validator}:template_claim_strength_upgrade:{filename}:{idx}')
        if filename == 'expression-design-bundle.yaml':
            typed_refs = data.get('typed_object_refs') or {}
            bundle_rules = data.get('bundle_rules') or {}
            if bundle_rules.get('cannot_bypass_typed_object_validators') is not True:
                failures.append(f'{validator}:bundle_can_bypass:{filename}')
            required_keys = {'cognitive_load_budget', 'explanation_ladder', 'rhetorical_move_matrix', 'claim_evidence_visibility_map', 'terminology_register'}
            if not isinstance(typed_refs, dict) or not required_keys.issubset(set(typed_refs)):
                failures.append(f'{validator}:missing_required_typed_ref:{filename}')

    for yaml_path in list(template_root.glob('*.yaml')) + list((root / 'entry-skills/yxj-paper-os/templates').glob('*.yaml')):
        if yaml_has_duplicate_keys(yaml_path):
            failures.append(f'validate_schema_fields:duplicate_yaml_key:{yaml_path.relative_to(root)}')

    manager_direct = load_yaml(template_root / 'manager-direct-intervention.yaml', {})
    if not isinstance(manager_direct, dict):
        failures.append('validate_manager_direct_intervention_declared:invalid_yaml:manager-direct-intervention.yaml')
    else:
        for path in ['intervention_id', 'task_id', 'trigger', 'why_not_delegated', 'affected_departments', 'manager_actions', 'derived_from_actor_provenance', 'actor_provenance_refs', 'required_independent_review.present', 'independent_review.verdict', 'forbidden_self_certification', 'allowed_completion_state', 'state_ingestion.ledger_path', 'backflow_route.on_authority_failure']:
            if not require_path(manager_direct, path):
                failures.append(f'validate_manager_direct_intervention_declared:missing_field:manager-direct-intervention.yaml:{path}')
        if not str(manager_direct.get('schema_version', '')).startswith('yxj-paper-os/manager-direct-intervention/'):
            failures.append('validate_manager_direct_intervention_declared:missing_schema_version:manager-direct-intervention.yaml')

    task_packet = load_yaml(template_root / 'task-packet.yaml', {})
    for path in ['actor_provenance.execution_actor_id', 'actor_provenance.execution_actor_kind', 'actor_provenance.manager_role_at_execution', 'actor_provenance.final_certifier_actor_id', 'actor_provenance.actor_provenance_artifacts', 'manager_direct_intervention.present', 'manager_direct_intervention.inferred_from_actor_provenance', 'manager_direct_intervention.required_independent_review', 'role_separation.executor_actor_id', 'role_separation.reviewer_actor_id', 'role_separation.final_certifier_actor_id']:
        if not require_path(task_packet, path):
            failures.append(f'validate_actor_provenance_present:missing_task_packet_field:{path}')
    if isinstance(task_packet, dict):
        for path in ['role_identity.department', 'role_identity.owner_lane', 'role_identity.agent_type', 'intelligence_zone.allowed', 'intelligence_zone.requires_owner_gate', 'forbidden_zone']:
            if not require_path(task_packet, path):
                failures.append(f'validate_task_packet:missing_task_packet_field:{path}')
        task_lane = lane_registry_by_id(root).get(str(task_packet.get('owner_lane') or ''))
        if not validate_agent_lane_department_binding(task_packet, task_lane):
            failures.append('validate_agent_lane_department_binding:task-packet-template-owner-binding')
        task_packet_refs = set(task_packet.get('validator_refs') or [])
        required_refs = {'validate_agent_lane_department_binding', 'validate_task_material_io'}
        if task_lane and task_lane.get('narrative_binding_required'):
            required_refs.add('validate_narrative_object_binding')
        if task_lane and task_lane.get('template_binding_required'):
            required_refs.add('validate_template_object_binding')
        missing_refs = required_refs - task_packet_refs
        if missing_refs:
            failures.append(
                f"validate_validator_reference_closure:task-packet-template-missing:{','.join(sorted(missing_refs))}"
            )
        lane_outputs = {
            str(item.get('artifact_type'))
            for item in task_lane.get('material_outputs', [])
            if isinstance(item, dict) and item.get('artifact_type')
        } if task_lane else set()
        packet_outputs = {
            str(item.get('artifact_type'))
            for field in ['expected_output_materials', 'expected_output_artifacts']
            for item in task_packet.get(field, [])
            if isinstance(item, dict) and item.get('artifact_type')
        }
        if lane_outputs and not (packet_outputs & lane_outputs):
            failures.append('validate_task_material_io:task-packet-template-output-not-in-lane')
        if not validate_narrative_object_binding(task_packet, task_lane, template_root, {}):
            failures.append('validate_narrative_object_binding:task-packet-template-unresolved')
        if not validate_template_object_binding(task_packet, task_lane, template_root, {}):
            failures.append('validate_template_object_binding:task-packet-template-unresolved')

    handoff = (template_root / 'manager-handoff-report-v2.md').read_text(encoding='utf-8', errors='ignore') if (template_root / 'manager-handoff-report-v2.md').exists() else ''
    if '```yaml' not in handoff or 'authority_role_separation:' not in handoff:
        failures.append('validate_manager_direct_handoff_disclosure:missing_yaml_authority_role_separation_template')
    return failures


def check_scaffold(root: Path) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    detail: dict[str, Any] = {'root': str(root)}
    for rel in REQUIRED_ROOT_FILES:
        if not (root / rel).exists():
            failures.append(f'missing_required_file:{rel}')
    manifest_path = root / '.codex-plugin/plugin.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as exc:
        failures.append(f'invalid_plugin_manifest:{exc}')
        manifest = {}
    if manifest:
        if manifest.get('name') != 'yxj-paper-os':
            failures.append('manifest_name_not_yxj-paper-os')
        if not re.match(r'^\d+\.\d+\.\d+(?:\+[A-Za-z0-9.-]+)?$', str(manifest.get('version', ''))):
            failures.append('manifest_version_not_semver')
        if not manifest.get('author', {}).get('name'):
            failures.append('manifest_missing_author_name')
        if manifest.get('skills') != PUBLIC_SKILLS_RESOURCE:
            failures.append('manifest_missing_skills_resource')
        for forbidden in ('hooks', 'mcpServers', 'apps'):
            if forbidden in manifest:
                failures.append(f'manifest_unapproved_resource_field:{forbidden}')
        if '[TODO:' in json.dumps(manifest):
            failures.append('manifest_contains_todo_placeholder')
    public_root = root / PUBLIC_SKILLS_RESOURCE
    public_skill_names = {
        p.name
        for p in public_root.iterdir()
        if p.is_dir() and (p / 'SKILL.md').exists()
    } if public_root.exists() else set()
    if public_skill_names != PUBLIC_ENTRY_SKILLS:
        failures.append(f'public_skill_surface_not_single_entry:{",".join(sorted(public_skill_names))}')
    public_entry = public_root / 'yxj-paper-os/SKILL.md'
    if public_entry.exists():
        try:
            public_fm = skill_frontmatter(public_entry)
        except Exception as exc:
            failures.append(f'invalid_public_entry_frontmatter:{exc}')
            public_fm = {}
        if public_fm.get('name') != 'yxj-paper-os':
            failures.append('public_entry_name_mismatch')
        public_text = public_entry.read_text(encoding='utf-8')
        for marker in ['Single public entry', 'internal paper departments', '../../skills/']:
            if marker not in public_text:
                failures.append(f'public_entry_missing_visibility_marker:{marker}')
    else:
        failures.append('missing_public_entry:yxj-paper-os')
    for skill in REQUIRED_SKILLS:
        path = root / 'skills' / skill / 'SKILL.md'
        if not path.exists():
            failures.append(f'missing_skill:{skill}')
            continue
        try:
            fm = skill_frontmatter(path)
        except Exception as exc:
            failures.append(f'invalid_skill_frontmatter:{skill}:{exc}')
            continue
        if fm.get('name') != skill:
            failures.append(f'skill_name_mismatch:{skill}')
        if not fm.get('description'):
            failures.append(f'skill_missing_description:{skill}')
        if '[TODO:' in path.read_text(encoding='utf-8'):
            failures.append(f'skill_contains_todo:{skill}')
    for tmpl in REQUIRED_TEMPLATES + REQUIRED_V2_TEMPLATES:
        path = root / 'skills/yxj-paper-index/templates' / tmpl
        if not path.exists():
            failures.append(f'missing_template:{tmpl}')
        elif not isinstance(load_yaml(path), dict):
            failures.append(f'invalid_template_yaml:{tmpl}')
    handoff_v2 = root / 'skills/yxj-paper-index/templates/manager-handoff-report-v2.md'
    if not handoff_v2.exists():
        failures.append('missing_template:manager-handoff-report-v2.md')
    else:
        handoff_text = handoff_v2.read_text(encoding='utf-8', errors='ignore')
        for marker in ['Department table', 'Inputs consumed', 'Outputs produced', 'Narrative/template refs', 'Closure state', 'Verification appendix']:
            if marker not in handoff_text:
                failures.append(f'validate_manager_handoff_v2:missing_marker:{marker}')
    canonical_templates = root / 'skills/yxj-paper-index/templates'
    mirror_templates = root / 'entry-skills/yxj-paper-os/templates'
    if canonical_templates.exists() and mirror_templates.exists():
        canonical_files = sorted(p.relative_to(canonical_templates) for p in canonical_templates.iterdir() if p.is_file())
        mirror_files = sorted(p.relative_to(mirror_templates) for p in mirror_templates.iterdir() if p.is_file())
        if canonical_files != mirror_files:
            failures.append('validate_template_mirror_sync:file_set_mismatch')
        else:
            for rel in canonical_files:
                c_hash = hashlib.sha256((canonical_templates / rel).read_bytes()).hexdigest()
                m_hash = hashlib.sha256((mirror_templates / rel).read_bytes()).hexdigest()
                if c_hash != m_hash:
                    failures.append(f'validate_template_mirror_sync:hash_mismatch:{rel}')
    else:
        failures.append('validate_template_mirror_sync:missing_template_tree')
    failures.extend(check_v2_template_shapes(root))
    for script in ['validate_yxj_paper_os.py', 'validate_scaffold.py', 'validate_fixture.py', 'run_fixture_suite.py']:
        if not (root / 'skills/yxj-paper-index/scripts' / script).exists():
            failures.append(f'missing_validator_script:{script}')
    registry = load_lane_registry(root)
    registry_lanes = {e.get('lane_id'): e for e in registry.get('lanes', []) if isinstance(e, dict)}
    required_registry_lanes = {'scene-analyst', 'exemplar-learner', 'sota-mapper', 'citation-banker', 'paper-owner-gate', 'method-verifier', 'style-auditor', 'verifier', 'repository-hygiene-owner'}
    missing_registry_lanes = sorted(required_registry_lanes - set(registry_lanes))
    if missing_registry_lanes:
        failures.append(f'missing_agent_lane_registry_entries:{",".join(missing_registry_lanes)}')
    installed = set(registry.get('installed_agent_types') or [])
    for lane_id, entry in registry_lanes.items():
        kind = entry.get('lane_kind')
        agent = entry.get('recommended_agent_type')
        if kind in {'direct_subagent', 'umbrella', 'alias', 'scaffold_lane'} and agent not in installed:
            failures.append(f'unknown_registry_agent_type:{lane_id}:{agent}')
        for field in ['context_scope', 'expected_output_artifacts', 'validator_refs', 'fallback_policy']:
            if not entry.get(field):
                failures.append(f'incomplete_registry_lane:{lane_id}:{field}')
    agent_contract = root / 'skills/yxj-paper-execute/references/agent-contract.md'
    if agent_contract.exists():
        agent_text = agent_contract.read_text(encoding='utf-8')
        for lane in required_registry_lanes:
            if lane not in agent_text:
                failures.append(f'agent_contract_missing_lane:{lane}')
        if 'agent-lane-registry.yaml' not in agent_text:
            failures.append('agent_contract_not_registry_backed')
    if not (root / 'fixtures/valid/minimal-valid').exists():
        failures.append('missing_valid_fixture:minimal-valid')
    for fixture_name in sorted(REQUIRED_DEPARTMENT_FIXTURES['valid']):
        if not (root / 'fixtures/valid' / fixture_name).is_dir():
            failures.append(f'missing_valid_fixture:{fixture_name}')
    invalid_root = root / 'fixtures/invalid'
    if not invalid_root.exists() or len([p for p in invalid_root.iterdir() if p.is_dir()]) < 15:
        failures.append('missing_invalid_fixture_set')
    for fixture_name in sorted(REQUIRED_DEPARTMENT_FIXTURES['invalid']):
        if not (root / 'fixtures/invalid' / fixture_name).is_dir():
            failures.append(f'missing_invalid_fixture:{fixture_name}')
    source_doc = root / 'skills/yxj-paper-index/references/source-influences.md'
    if source_doc.exists():
        influence_candidates = {
            'PaperSpine': [
                root / '../../tools/PaperSpine',
                Path('/home/weathour/文档/CPS-Papers/shared/paper-writing-tools-lab/tools/PaperSpine'),
                Path('/home/weathour/writing/PaperSpine'),
            ],
            'sisyphus-academica': [
                root / '../../tools/sisyphus-academica',
                Path('/home/weathour/文档/CPS-Papers/shared/paper-writing-tools-lab/tools/sisyphus-academica'),
                Path('/home/weathour/writing/sisyphus-academica'),
            ],
        }
        for name, candidates in influence_candidates.items():
            if not any(candidate.resolve().exists() for candidate in candidates):
                failures.append(f'unresolved_source_influence:{name}')
    text_all = ''
    for p in root.rglob('*'):
        if p.is_file() and p.suffix in {'.md', '.yaml', '.yml', '.json', '.py'}:
            text_all += p.read_text(encoding='utf-8', errors='ignore')[:200000]
    if 'active-install' not in text_all and 'active install' not in text_all:
        failures.append('missing_active_install_gate_language')
    if 'dispatched != complete' not in text_all and 'dispatch' not in text_all:
        failures.append('missing_dispatch_completion_invariant')
    governance_marker_checks = {
        'skills/yxj-paper-index/references/orchestrator-contract.md': ['PUA-DIAGNOSIS', 'PUA-REPORT', 'pua_telemetry', 'RALPLAN'],
        'skills/yxj-paper-index/references/department-manager-governance.md': ['DepartmentRouteCard', 'team_lane_lead', 'compile -> execute -> collect -> validate -> ingest -> state_transition'],
        'skills/yxj-paper-execute/references/runtime-execution-contract.md': ['pua_telemetry', 'validate_pua_telemetry', 'compile -> execute -> collect -> validate -> ingest -> state_transition'],
        'skills/yxj-paper-execute/references/agent-contract.md': ['PUA-DIAGNOSIS', 'PUA-REPORT', 'paper-owner-gate'],
        'skills/yxj-paper-state/references/state-contract.md': ['pua_telemetry', 'never replaces validator evidence'],
        'skills/yxj-paper-index/templates/task-packet.yaml': ['pua_telemetry', 'validate_pua_telemetry'],
        'skills/yxj-paper-index/templates/validator-report.yaml': ['validate_pua_telemetry', 'pua_telemetry_checked'],
        'docs/operation-guide.md': ['PUA/RALPLAN governance', 'PUA-DIAGNOSIS', 'PUA-REPORT'],
        'docs/architecture.md': ['PUA/RALPLAN governance control plane', 'paper-owner-gate'],
        'docs/validator-fixtures.md': ['PUA telemetry fixture contract', 'validate_pua_telemetry', 'validate_repository_hygiene_report'],
    }
    for rel, markers in governance_marker_checks.items():
        marker_path = root / rel
        marker_text = marker_path.read_text(encoding='utf-8', errors='ignore') if marker_path.exists() else ''
        for marker in markers:
            if marker not in marker_text:
                failures.append(f'missing_governance_marker:{rel}:{marker}')
    detail['public_entry_skills'] = sorted(PUBLIC_ENTRY_SKILLS)
    detail['required_internal_skills'] = REQUIRED_SKILLS
    detail['required_templates'] = REQUIRED_TEMPLATES
    detail['required_v2_templates'] = REQUIRED_V2_TEMPLATES + ['manager-handoff-report-v2.md']
    return failures, detail


def normalize_validator_refs(task: dict[str, Any], failures: list[str]) -> list[str]:
    refs = task.get('validator_refs')
    legacy = task.get('validators')
    if refs is None and legacy is not None:
        refs = legacy
    elif refs is not None and legacy is not None and refs != legacy:
        failures.append('validator_alias_mismatch')
    if refs is None:
        return []
    return list(refs or [])


def task_has_collected(task: dict[str, Any], fixture: Path) -> bool:
    outputs = task.get('collected_outputs') or []
    if not outputs:
        return False
    for out in outputs:
        p = out.get('path') if isinstance(out, dict) else None
        if not p or not (fixture / p).exists():
            return False
    return True


def passing_validator_names(task: dict[str, Any], report: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for e in task.get('validator_evidence') or []:
        if isinstance(e, dict) and e.get('status') == 'pass' and e.get('validator') in KNOWN_VALIDATORS:
            names.add(e['validator'])
    for e in report.get('validators_run') or []:
        if isinstance(e, dict) and e.get('status') == 'pass' and e.get('validator') in KNOWN_VALIDATORS:
            names.add(e['validator'])
    return names


def missing_validator_evidence(task: dict[str, Any], report: dict[str, Any], refs: list[str]) -> set[str]:
    return set(refs) - passing_validator_names(task, report)


def task_has_ingest(task: dict[str, Any]) -> bool:
    ingest = task.get('state_ingestion') or {}
    return ingest.get('status') == 'ingested' and bool(ingest.get('ledger_path'))


def task_has_state_transition(task: dict[str, Any]) -> bool:
    transition = task.get('state_transition') or {}
    return (
        task.get('pipeline_stage') == 'state_transition'
        and bool(transition.get('from'))
        and transition.get('to') == 'complete'
        and bool(transition.get('at'))
    )


PUA_PRESSURE_LEVELS = {'L0', 'L1', 'L2', 'L3', 'L4'}
PUA_FAILURE_MODES = {None, 'stuck_loop', 'give_up_blame', 'poor_quality', 'no_search_guess', 'passive_wait', 'rough_grain', 'empty_completion'}
PUA_SEVEN_ITEM_KEYS = {
    'read_failure_signal', 'searched_core_problem', 'read_original_material',
    'verified_prerequisites', 'reversed_assumption', 'minimal_isolation', 'changed_direction',
}


def validate_pua_telemetry(task: dict[str, Any]) -> bool:
    telemetry = task.get('pua_telemetry')
    if not isinstance(telemetry, dict):
        return False
    level = telemetry.get('pressure_level')
    if level not in PUA_PRESSURE_LEVELS:
        return False
    failure_count = telemetry.get('failure_count')
    if type(failure_count) is not int or failure_count < 0:
        return False
    failure_mode = telemetry.get('failure_mode')
    if failure_mode not in PUA_FAILURE_MODES:
        return False
    diagnosis = telemetry.get('pua_diagnosis') or {}
    if not isinstance(diagnosis, dict) or not all(k in diagnosis for k in ['problem_or_goal', 'evidence', 'next_action']):
        return False
    if not isinstance(diagnosis.get('evidence'), list):
        return False
    if not isinstance(diagnosis.get('problem_or_goal'), str) or not isinstance(diagnosis.get('next_action'), str):
        return False
    owner_q = telemetry.get('owner_four_questions') or {}
    if not isinstance(owner_q, dict) or not all(k in owner_q for k in ['root_cause_or_target', 'impact_surface', 'prevention_or_check', 'data_or_evidence']):
        return False
    for key in ['attempts', 'excluded']:
        if not isinstance(telemetry.get(key), list):
            return False
    if not isinstance(telemetry.get('next_hypothesis'), str) or not isinstance(telemetry.get('manager_action'), str):
        return False
    checklist = telemetry.get('seven_item_checklist') or {}
    if not isinstance(checklist, dict) or set(checklist) != PUA_SEVEN_ITEM_KEYS:
        return False
    if not all(isinstance(v, bool) for v in checklist.values()):
        return False
    report = telemetry.get('pua_report')
    if not isinstance(report, dict) or not isinstance(report.get('present'), bool):
        return False

    min_counts = {'L0': 0, 'L1': 2, 'L2': 3, 'L3': 4, 'L4': 5}
    if failure_count < min_counts[level]:
        return False
    if level == 'L0':
        return failure_count == 0 and failure_mode is None and report.get('present') is False
    if failure_mode is None:
        return False
    if not telemetry.get('attempts') or not telemetry.get('next_hypothesis') or not telemetry.get('manager_action'):
        return False
    if level in {'L2', 'L3', 'L4'}:
        if report.get('present') is not True:
            return False
        report_failure_count = report.get('failure_count')
        if type(report_failure_count) is not int or report_failure_count != failure_count or report.get('failure_mode') != failure_mode:
            return False
        for key in ['attempts', 'excluded', 'next_hypothesis', 'manager_action']:
            if report.get(key) != telemetry.get(key):
                return False
        if not report.get('attempts') or not report.get('next_hypothesis') or not report.get('manager_action'):
            return False
    if level in {'L3', 'L4'} and not all(checklist.values()):
        return False
    return True


V2_TASK_FIELDS = {
    'owner_department', 'input_materials', 'expected_output_materials',
    'narrative_object_refs', 'template_object_refs', 'backflow_route',
    'expression_design_object_refs', 'expression_design_applicability',
    'expression_design_binding_exception',
}

V2_VALIDATOR_REFS = {
    'validate_agent_lane_department_binding', 'validate_task_material_io',
    'validate_narrative_object_binding', 'validate_template_object_binding',
    'validate_repository_hygiene_report',
    'validate_expression_design_object_binding', 'validate_cognitive_load_budget',
    'validate_explanation_ladder', 'validate_rhetorical_move_matrix',
    'validate_claim_evidence_visibility_map', 'validate_terminology_register',
    'validate_cognitive_load_budget_consumed', 'validate_rhetorical_move_matrix_consumed',
    'validate_explanation_ladder_progression', 'validate_claim_evidence_visibility',
    'validate_terminology_register_surface',
    'validate_actor_provenance_present', 'validate_actor_provenance_artifact_trusted',
    'validate_effective_actor_identity_resolved', 'validate_derived_sensitivity_classification',
    'validate_manager_direct_inferred_or_declared', 'validate_manager_direct_intervention_declared',
    'validate_manager_direct_independent_review', 'validate_no_manager_self_certification',
    'validate_role_separation_for_paper_facing_tasks', 'validate_manager_direct_handoff_disclosure',
    'validate_completion_state_limited_without_independent_review',
    'validate_nature_figure_contract', 'validate_nature_figure_aesthetic_profile',
    'validate_panel_evidence_map', 'validate_figure_backend_route',
    'validate_figure_source_data_statistics', 'validate_figure_image_integrity_record',
    'validate_nature_caption_legend', 'validate_nature_figure_qa_report',
    'validate_figure_export_bundle',
    'validate_nature_source_inventory',
    'validate_nature_absorption_package',
    'validate_company_skill_registry',
    'validate_paper_reader_package',
    'validate_search_strategy_dossier',
    'validate_citation_verification_report',
    'validate_section_move_plan',
    'validate_journal_style_profile',
    'validate_polishing_repair_report',
    'validate_data_availability_plan',
    'validate_reviewer_panel_report',
    'validate_response_action_map',
    'validate_presentation_plan',
    'validate_patent_draft_boundary',
}

EXPRESSION_DESIGN_OBJECT_VALIDATORS = {
    'validate_cognitive_load_budget',
    'validate_explanation_ladder',
    'validate_rhetorical_move_matrix',
    'validate_claim_evidence_visibility_map',
    'validate_terminology_register',
}

EXPRESSION_DESIGN_REQUIRED_REF_MARKERS: dict[str, set[str]] = {
    'CognitiveLoadBudget': {'cognitiveloadbudget', 'cognitiveload', 'cognitive-load-budget'},
    'ExplanationLadder': {'explanationladder', 'explanation-ladder'},
    'RhetoricalMoveMatrix': {'rhetoricalmovematrix', 'rhetorical-move-matrix'},
    'ClaimEvidenceVisibilityMap': {
        'claimevidencevisibilitymap',
        'claim-evidence-visibility-map',
        'claimevidencevisibility',
    },
    'TerminologyRegister': {'terminologyregister', 'terminology-register'},
}

PAPER_FACING_EXPRESSION_LANES = {
    'manuscript-owner',
    'figure-owner',
    'review-director',
    'style-auditor',
    'export-owner',
    'final-verifier',
}

PAPER_FACING_EXPRESSION_DEPARTMENTS = {
    'manuscript_and_figure_production',
    'review_and_governance',
}

PAPER_FACING_EXPRESSION_MARKERS = {
    'manuscript',
    'maintext',
    'main-text',
    'section',
    'paragraph',
    'figure',
    'table',
    'algorithm',
    'formula',
    'caption',
    'review',
    'reader',
    'rendered',
    'export',
    'submission',
}

RENDERED_SURFACE_REQUIRED_MARKERS = {
    'manuscriptsectiondraft',
    'validatedmanuscript',
    'manuscriptdraft',
    'figurepackage',
    'figureplan',
    'caption',
    'exportpackage',
    'exportmanifest',
    'submissionpackage',
    'readersurfacereview',
    'renderedsurface',
}


def task_is_v2(task: dict[str, Any], refs: list[str]) -> bool:
    return any(field in task for field in V2_TASK_FIELDS) or bool(set(refs) & V2_VALIDATOR_REFS)


def validate_agent_lane_department_binding(task: dict[str, Any], lane: dict[str, Any] | None) -> bool:
    if not lane:
        return False
    if task.get('owner_department') != lane.get('department'):
        return False
    expected_agent = lane.get('recommended_agent_type')
    kind = lane.get('lane_kind')
    actual_agent = task.get('agent_type')
    if kind == 'user_gate':
        return actual_agent == expected_agent
    if kind in {'direct_subagent', 'umbrella', 'alias', 'scaffold_lane'}:
        return actual_agent == expected_agent
    return bool(actual_agent)


def material_entries_are_valid(entries: Any, *, require_path: bool) -> bool:
    if not isinstance(entries, list) or not entries:
        return False
    for item in entries:
        if not isinstance(item, dict):
            return False
        if not isinstance(item.get('artifact_type'), str) or not item.get('artifact_type'):
            return False
        has_address = bool(item.get('artifact_id') or item.get('path'))
        if not has_address:
            return False
        if require_path and not item.get('path'):
            return False
    return True


def task_material_ids_and_paths(task: dict[str, Any]) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    paths: set[str] = set()
    for field in ['input_materials', 'expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
        for item in task.get(field) or []:
            if not isinstance(item, dict):
                continue
            for key in ['artifact_id', 'object_id']:
                if isinstance(item.get(key), str) and item[key]:
                    ids.add(item[key])
            if isinstance(item.get('path'), str) and item['path']:
                paths.add(item['path'].rstrip('/'))
    return ids, paths


def ledger_artifact_paths(artifacts: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for art in artifacts.get('artifacts') or []:
        if isinstance(art, dict) and isinstance(art.get('path'), str):
            paths.add(art['path'].rstrip('/'))
    return paths


def validate_task_material_io(task: dict[str, Any], fixture: Path, artifacts: dict[str, Any]) -> bool:
    inputs = task.get('input_materials') or []
    outputs = task.get('expected_output_materials') or []
    if not material_entries_are_valid(inputs, require_path=False):
        return False
    if not material_entries_are_valid(outputs, require_path=True):
        return False
    if not isinstance(task.get('backflow_route'), dict) or not task['backflow_route']:
        return False
    if task.get('status') == 'complete':
        collected_paths = {
            item.get('path', '').rstrip('/')
            for item in task.get('collected_outputs') or []
            if isinstance(item, dict)
        }
        artifact_paths = ledger_artifact_paths(artifacts)
        for item in outputs:
            path = str(item.get('path') or '').rstrip('/')
            declared_output = path in collected_paths or path in artifact_paths
            if not path or not declared_output:
                return False
            if not (fixture / path).exists():
                return False
        if not task_has_ingest(task):
            return False
    return True


def refs_are_resolved(refs: Any, task: dict[str, Any], fixture: Path) -> bool:
    if not isinstance(refs, list) or not refs:
        return False
    known_ids, known_paths = task_material_ids_and_paths(task)
    for ref in refs:
        ref_id = ref.get('artifact_id') if isinstance(ref, dict) else ref
        if not isinstance(ref_id, str) or not ref_id:
            return False
        candidates = {
            ref_id,
            f'{ref_id}.yaml',
            f'narrative/{ref_id}.yaml',
            f'templates/{ref_id}.yaml',
            f'expression-design/{ref_id}.yaml',
            f'expression-design/{ref_id}',
            f'expression_design/{ref_id}.yaml',
            f'expression_design/{ref_id}',
        }
        if ref_id in known_ids or ref_id in known_paths:
            continue
        if any((fixture / c).exists() for c in candidates):
            continue
        return False
    return True


def report_accepts_binding_exception(report: dict[str, Any], task: dict[str, Any], kind: str, reason: str) -> bool:
    if not reason:
        return False
    task_id = task.get('task_id')
    for item in report.get('binding_exceptions') or []:
        if not isinstance(item, dict):
            continue
        if item.get('task_id') != task_id or item.get('kind') != kind:
            continue
        if item.get('non_applicable_reason') != reason:
            continue
        if item.get('status') != 'accepted' or item.get('reviewer_independent') is not True:
            continue
        return True
    return False


def validate_narrative_object_binding(task: dict[str, Any], lane: dict[str, Any] | None, fixture: Path, report: dict[str, Any]) -> bool:
    if lane and not lane.get('narrative_binding_required') and 'validate_narrative_object_binding' not in normalize_validator_refs(task, []):
        return True
    exception = task.get('narrative_binding_exception') or {}
    if report_accepts_binding_exception(report, task, 'narrative', str(exception.get('non_applicable_reason') or '')):
        return True
    return refs_are_resolved(task.get('narrative_object_refs'), task, fixture)


def validate_template_object_binding(task: dict[str, Any], lane: dict[str, Any] | None, fixture: Path, report: dict[str, Any]) -> bool:
    if lane and not lane.get('template_binding_required') and 'validate_template_object_binding' not in normalize_validator_refs(task, []):
        return True
    exception = task.get('template_binding_exception') or {}
    if report_accepts_binding_exception(report, task, 'template', str(exception.get('non_applicable_reason') or '')):
        return True
    return refs_are_resolved(task.get('template_object_refs'), task, fixture)


def material_ref_strings(refs: Any) -> list[str]:
    values: list[str] = []
    if not isinstance(refs, list):
        return values
    for ref in refs:
        if isinstance(ref, dict):
            for key in ['artifact_id', 'object_id', 'artifact_type', 'type', 'path']:
                value = ref.get(key)
                if isinstance(value, str) and value:
                    values.append(value)
        elif isinstance(ref, str) and ref:
            values.append(ref)
    return values


def task_material_text(task: dict[str, Any]) -> str:
    values: list[str] = [
        str(task.get('task_id') or ''),
        str(task.get('route') or ''),
        str(task.get('owner_lane') or ''),
        str(task.get('owner_department') or ''),
        str(task.get('mission') or ''),
        str(task.get('pipeline_stage') or ''),
    ]
    for field in ['input_materials', 'expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
        for item in task.get(field) or []:
            if not isinstance(item, dict):
                continue
            for key in ['artifact_type', 'artifact_id', 'type', 'path']:
                value = item.get(key)
                if isinstance(value, str) and value:
                    values.append(value)
    return ' '.join(values)


def task_requires_expression_design(task: dict[str, Any], lane: dict[str, Any] | None) -> bool:
    applicability = task.get('expression_design_applicability') or {}
    if isinstance(applicability, dict):
        if applicability.get('required') is True or applicability.get('paper_facing') is True:
            return True
        if applicability.get('required') is False:
            return False
    owner_lane = str(task.get('owner_lane') or '')
    if owner_lane in PAPER_FACING_EXPRESSION_LANES:
        return True
    owner_department = str(task.get('owner_department') or (lane or {}).get('department') or '')
    if owner_department in PAPER_FACING_EXPRESSION_DEPARTMENTS:
        text = normalize_material_key(task_material_text(task))
        if any(normalize_material_key(marker) in text for marker in PAPER_FACING_EXPRESSION_MARKERS):
            return True
    return False


def expression_design_non_applicable_accepted(task: dict[str, Any], report: dict[str, Any]) -> bool:
    exception = task.get('expression_design_binding_exception') or {}
    reason = str(exception.get('non_applicable_reason') or '')
    if report_accepts_binding_exception(report, task, 'expression_design', reason):
        return True
    applicability = task.get('expression_design_applicability') or {}
    if isinstance(applicability, dict) and applicability.get('required') is False:
        reason = str(applicability.get('non_applicable_reason') or reason)
        return report_accepts_binding_exception(report, task, 'expression_design', reason)
    return False


def expression_refs_cover_required_types(refs: Any) -> bool:
    normalized = {normalize_material_key(value) for value in material_ref_strings(refs)}
    if not normalized:
        return False
    for markers in EXPRESSION_DESIGN_REQUIRED_REF_MARKERS.values():
        normalized_markers = {normalize_material_key(marker) for marker in markers}
        if not any(any(marker in value for marker in normalized_markers) for value in normalized):
            return False
    return True


def expression_design_bundle_declared(refs: Any, task: dict[str, Any]) -> bool:
    values = material_ref_strings(refs)
    values.extend(material_ref_strings(task.get('input_materials')))
    values.extend(material_ref_strings(task.get('expected_output_materials')))
    values.extend(material_ref_strings(task.get('expected_output_artifacts')))
    values.extend(material_ref_strings(task.get('collected_outputs')))
    return any('expressiondesignbundle' in normalize_material_key(value) for value in values)


def validate_expression_design_object_binding(
    task: dict[str, Any],
    lane: dict[str, Any] | None,
    fixture: Path,
    report: dict[str, Any],
) -> bool:
    refs = task.get('expression_design_object_refs')
    validator_refs = set(normalize_validator_refs(task, []))
    required = task_requires_expression_design(task, lane)
    if not required and not refs:
        return True
    if expression_design_non_applicable_accepted(task, report):
        return True
    if 'validate_expression_design_object_binding' not in validator_refs:
        return False
    if not refs_are_resolved(refs, task, fixture):
        return False
    if not expression_refs_cover_required_types(refs):
        return False
    if lane and lane.get('narrative_binding_required') and not task.get('narrative_object_refs'):
        return False
    if lane and lane.get('template_binding_required') and not task.get('template_object_refs'):
        return False
    if not refs_are_resolved(task.get('evidence_object_refs'), task, fixture):
        return False
    if not EXPRESSION_DESIGN_OBJECT_VALIDATORS.issubset(validator_refs):
        return False
    if expression_design_bundle_declared(refs, task) and not EXPRESSION_DESIGN_OBJECT_VALIDATORS.issubset(validator_refs):
        return False
    return True


def task_requires_rendered_surface_gate(task: dict[str, Any], lane: dict[str, Any] | None) -> bool:
    applicability = task.get('expression_design_applicability') or {}
    if isinstance(applicability, dict):
        if applicability.get('rendered_surface_required') is True:
            return True
        if applicability.get('rendered_surface_required') is False:
            return False
    if not task_requires_expression_design(task, lane):
        return False
    owner_lane = str(task.get('owner_lane') or '')
    if owner_lane in {'review-director', 'style-auditor', 'export-owner', 'final-verifier'}:
        return True
    text = normalize_material_key(task_material_text(task))
    return any(marker in text for marker in RENDERED_SURFACE_REQUIRED_MARKERS)


def task_declares_rendered_surface_gate(task: dict[str, Any], fixture: Path) -> bool:
    spec = MATERIAL_OBJECT_SPECS['RenderedSurfaceGateReport']
    for field in ['input_materials', 'expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
        for item in task.get(field) or []:
            if not isinstance(item, dict):
                continue
            if not material_spec_matches_entry(spec, item):
                continue
            path = item.get('path')
            return isinstance(path, str) and bool(path) and (fixture / path).exists()
    return False


def hygiene_report_paths(task: dict[str, Any], artifacts: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    fields = ['expected_output_materials', 'expected_output_artifacts', 'collected_outputs']
    for field in fields:
        for item in task.get(field) or []:
            if not isinstance(item, dict):
                continue
            artifact_type = str(item.get('artifact_type') or '').lower()
            path = item.get('path')
            if not isinstance(path, str) or not path:
                continue
            if 'hygiene' in artifact_type or 'cleanliness' in artifact_type or 'repository-hygiene' in path:
                if path not in paths:
                    paths.append(path)
    for art in artifacts.get('artifacts') or []:
        if not isinstance(art, dict):
            continue
        artifact_type = str(art.get('artifact_type') or art.get('type') or '').lower()
        path = art.get('path')
        if isinstance(path, str) and ('hygiene' in artifact_type or 'cleanliness' in artifact_type or 'repository-hygiene' in path):
            if path not in paths:
                paths.append(path)
    return paths


def validate_repository_hygiene_report(task: dict[str, Any], fixture: Path, artifacts: dict[str, Any]) -> bool:
    paths = hygiene_report_paths(task, artifacts)
    if not paths:
        return False
    for rel in paths:
        report = load_yaml(fixture / rel, {})
        if not isinstance(report, dict):
            return False
        if not str(report.get('schema_version', '')).startswith('yxj-paper-os/repository-hygiene-report/'):
            return False
        scope = report.get('scope') or {}
        if not scope.get('paper_root'):
            return False
        commands = scope.get('commands') or []
        if not commands and not scope.get('non_git_workspace_reason'):
            return False
        worktree = report.get('worktree') or {}
        if worktree.get('status') not in {'clean', 'dirty_allowed', 'dirty_blocked', 'owner_gated'}:
            return False
        for key in ['total_dirty_entries', 'current_paper_dirty_entries', 'sibling_or_parent_dirty_entries']:
            value = worktree.get(key)
            if type(value) is not int or value < 0:
                return False
        for key in ['modified_entries', 'deleted_entries', 'untracked_entries', 'generated_or_ephemeral_entries', 'allowed_dirty_patterns', 'disallowed_dirty_entries']:
            if not isinstance(worktree.get(key), list):
                return False
        sibling = report.get('sibling_or_parent_contamination') or {}
        if sibling.get('status') not in {'none', 'present_blocked', 'accepted_with_owner_decision'}:
            return False
        if sibling.get('status') == 'accepted_with_owner_decision' and not sibling.get('owner_decision_id'):
            return False
        for section in ['snapshot_freshness', 'export_manifest_hashes']:
            status = (report.get(section) or {}).get('status')
            if status not in {'pass', 'fail', 'not_required'}:
                return False
        external = report.get('external_submission') or {}
        if external.get('status') not in {'not_performed_requires_explicit_confirmation', 'explicit_owner_confirmed'}:
            return False
        gate = report.get('delivery_cleanliness_gate') or {}
        if gate.get('status') not in {'pass', 'blocked', 'owner_gated'}:
            return False
        if not isinstance(gate.get('required_before'), list) or not gate.get('required_before'):
            return False
        if gate.get('status') == 'pass':
            if worktree.get('disallowed_dirty_entries'):
                return False
            if sibling.get('status') == 'present_blocked':
                return False
            if (report.get('snapshot_freshness') or {}).get('status') == 'fail':
                return False
            if (report.get('export_manifest_hashes') or {}).get('status') == 'fail':
                return False
            if worktree.get('status') not in {'clean', 'dirty_allowed'}:
                return False
        else:
            # A non-pass gate must explain the blocker or owner gate.
            if not gate.get('reason'):
                return False
    return True



AUTHORITY_VALIDATOR_REFS = {
    'validate_actor_provenance_present', 'validate_actor_provenance_artifact_trusted',
    'validate_effective_actor_identity_resolved', 'validate_derived_sensitivity_classification',
    'validate_manager_direct_inferred_or_declared', 'validate_manager_direct_intervention_declared',
    'validate_manager_direct_independent_review', 'validate_no_manager_self_certification',
    'validate_role_separation_for_paper_facing_tasks', 'validate_manager_direct_handoff_disclosure',
    'validate_completion_state_limited_without_independent_review',
}

PAPER_FACING_LANES = {
    'manuscript-owner', 'figure-owner', 'export-owner', 'paper-architect', 'review-director',
    'style-auditor', 'method-verifier', 'evidence-curator', 'scene-analyst', 'exemplar-learner',
    'sota-mapper', 'research-director', 'final-verifier',
}
PAPER_FACING_TERMS = {
    'manuscript', 'paper', 'section', 'abstract', 'introduction', 'method', 'results',
    'discussion', 'conclusion', 'figure', 'table', 'algorithm', 'formula', 'caption',
    'bibliography', 'citation', 'export', 'pdf', 'latex', 'review', 'reader', 'claim', 'evidence',
}
STATE_SENSITIVE_TERMS = {'state', 'ledger', 'transition', 'gate', 'handoff', 'readiness', 'export', 'publish', 'install'}


def authority_value_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(authority_value_present(item) for item in value)
    if isinstance(value, dict):
        return any(authority_value_present(item) for item in value.values())
    return bool(value)


def authority_material_present(task: dict[str, Any]) -> bool:
    if manager_direct_active(task):
        return True
    provenance_raw = task.get('actor_provenance')
    provenance: dict[str, Any] = provenance_raw if isinstance(provenance_raw, dict) else {}
    if any(authority_value_present(provenance.get(key)) for key in [
        'execution_actor_id', 'execution_actor_kind', 'execution_actor_lane', 'manager_role_at_execution',
        'run_or_session_id', 'final_certifier_actor_id', 'final_certifier_actor_kind',
        'final_certifier_lane', 'final_certifier_run_or_session_id', 'actor_provenance_artifacts',
    ]):
        return True
    separation_raw = task.get('role_separation')
    separation: dict[str, Any] = separation_raw if isinstance(separation_raw, dict) else {}
    role_keys = [
        'executor_actor_id', 'executor_lane', 'reviewer_actor_id', 'reviewer_actor_kind',
        'reviewer_lane', 'reviewer_run_or_session_id', 'verifier_actor_id', 'verifier_actor_kind',
        'verifier_lane', 'verifier_run_or_session_id', 'final_certifier_actor_id', 'same_actor_exceptions',
    ]
    return any(authority_value_present(separation.get(key)) for key in role_keys)


def authority_refs_enabled(refs: list[str], task: dict[str, Any]) -> bool:
    return bool(set(refs) & AUTHORITY_VALIDATOR_REFS) or authority_material_present(task)


def required_authority_validator_refs(task: dict[str, Any], refs: list[str]) -> set[str]:
    if not authority_refs_enabled(refs, task):
        return set()
    required = set(AUTHORITY_VALIDATOR_REFS)
    if not manager_direct_active(task):
        required -= {
            'validate_manager_direct_inferred_or_declared',
            'validate_manager_direct_intervention_declared',
            'validate_manager_direct_independent_review',
            'validate_no_manager_self_certification',
            'validate_manager_direct_handoff_disclosure',
            'validate_completion_state_limited_without_independent_review',
        }
    return required


def missing_authority_validator_refs(task: dict[str, Any], refs: list[str]) -> set[str]:
    return required_authority_validator_refs(task, refs) - set(refs)


def normalize_actor_part(value: Any) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', '-', str(value).strip().lower())


def actor_record(task: dict[str, Any], role: str) -> dict[str, Any] | None:
    provenance = task.get('actor_provenance') or {}
    separation = task.get('role_separation') or {}
    if role == 'executor':
        actor = {
            'actor_kind': provenance.get('execution_actor_kind'),
            'actor_id': separation.get('executor_actor_id') or provenance.get('execution_actor_id'),
            'actor_lane': separation.get('executor_lane') or provenance.get('execution_actor_lane') or task.get('owner_lane'),
            'run_or_session_id': provenance.get('run_or_session_id'),
        }
    elif role == 'reviewer':
        actor = {
            'actor_kind': separation.get('reviewer_actor_kind') or provenance.get('reviewer_actor_kind') or 'native_subagent',
            'actor_id': separation.get('reviewer_actor_id') or provenance.get('reviewer_actor_id'),
            'actor_lane': separation.get('reviewer_lane') or provenance.get('reviewer_lane'),
            'run_or_session_id': separation.get('reviewer_run_or_session_id') or provenance.get('reviewer_run_or_session_id'),
        }
    elif role == 'verifier':
        actor = {
            'actor_kind': separation.get('verifier_actor_kind') or provenance.get('verifier_actor_kind') or 'native_subagent',
            'actor_id': separation.get('verifier_actor_id') or provenance.get('verifier_actor_id'),
            'actor_lane': separation.get('verifier_lane') or provenance.get('verifier_lane'),
            'run_or_session_id': separation.get('verifier_run_or_session_id') or provenance.get('verifier_run_or_session_id'),
        }
    else:
        actor = {
            'actor_kind': provenance.get('final_certifier_actor_kind'),
            'actor_id': separation.get('final_certifier_actor_id') or provenance.get('final_certifier_actor_id'),
            'actor_lane': separation.get('final_certifier_lane') or provenance.get('final_certifier_lane'),
            'run_or_session_id': provenance.get('final_certifier_run_or_session_id'),
        }
    return actor if actor_key(actor) else None


def actor_key(actor: dict[str, Any], *, prefix: str = '') -> str | None:
    kind = actor.get(f'{prefix}actor_kind') or actor.get('actor_kind')
    actor_id = actor.get(f'{prefix}actor_id') or actor.get('actor_id')
    lane = actor.get(f'{prefix}actor_lane') or actor.get('actor_lane') or actor.get(f'{prefix}lane') or actor.get('lane')
    run = actor.get(f'{prefix}run_or_session_id') or actor.get('run_or_session_id')
    parts = [normalize_actor_part(kind), normalize_actor_part(actor_id), normalize_actor_part(lane), normalize_actor_part(run)]
    if not all(parts):
        return None
    return ':'.join(parts)


def actor_key_from_task(task: dict[str, Any], role: str) -> str | None:
    actor = actor_record(task, role)
    return actor_key(actor) if actor else None


def same_effective_actor(left: dict[str, Any] | None, right: dict[str, Any] | None) -> bool:
    """Return true when two records represent the same effective actor.

    Lane changes are not enough to create independence. In particular, the same
    manager identity or same manager session remains the same actor even if the
    declared lane changes.
    """
    if not left or not right:
        return False
    left_key = actor_key(left)
    right_key = actor_key(right)
    if left_key and right_key and left_key == right_key:
        return True
    l_kind = normalize_actor_part(left.get('actor_kind'))
    r_kind = normalize_actor_part(right.get('actor_kind'))
    l_id = normalize_actor_part(left.get('actor_id'))
    r_id = normalize_actor_part(right.get('actor_id'))
    l_run = normalize_actor_part(left.get('run_or_session_id'))
    r_run = normalize_actor_part(right.get('run_or_session_id'))
    if l_id and r_id and l_id == r_id:
        return True
    if l_kind == r_kind == 'manager' and l_run and r_run and l_run == r_run:
        return True
    return False


def actors_are_independent(*actors: dict[str, Any] | None) -> bool:
    if any(actor is None for actor in actors):
        return False
    concrete = [actor for actor in actors if actor is not None]
    for idx, left in enumerate(concrete):
        for right in concrete[idx + 1:]:
            if same_effective_actor(left, right):
                return False
    return True


def provenance_artifact_refs(task: dict[str, Any]) -> list[str]:
    refs = (task.get('actor_provenance') or {}).get('actor_provenance_artifacts') or []
    paths: list[str] = []
    for item in refs:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict) and isinstance(item.get('path'), str):
            paths.append(item['path'])
    return paths


def load_provenance_artifacts(task: dict[str, Any], fixture: Path) -> list[dict[str, Any]] | None:
    paths = provenance_artifact_refs(task)
    if not paths:
        return None
    loaded: list[dict[str, Any]] = []
    for rel in paths:
        path = fixture / rel
        if path.suffix.lower() not in {'.yaml', '.yml', '.json'} or not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding='utf-8')) if path.suffix.lower() == '.json' else load_yaml(path, {})
        except Exception:
            return None
        if not isinstance(data, dict):
            return None
        loaded.append(data)
    return loaded


def actor_key_matches(left: dict[str, Any] | None, right: dict[str, Any] | None) -> bool:
    return bool(left and right and actor_key(left) == actor_key(right))


def task_ref_values(task: dict[str, Any], fields: list[str]) -> set[str]:
    values: set[str] = set()
    for field in fields:
        for item in task.get(field) or []:
            if not isinstance(item, dict):
                continue
            for key in ['artifact_id', 'object_id', 'path']:
                value = item.get(key)
                if isinstance(value, str) and value:
                    values.add(value.rstrip('/'))
    return values


def action_ref_values(refs: Any) -> set[str] | None:
    if not isinstance(refs, list) or not refs:
        return None
    values: set[str] = set()
    for item in refs:
        if isinstance(item, str) and item:
            values.add(item.rstrip('/'))
        elif isinstance(item, dict):
            found = False
            for key in ['artifact_id', 'object_id', 'path']:
                value = item.get(key)
                if isinstance(value, str) and value:
                    values.add(value.rstrip('/'))
                    found = True
            if not found:
                return None
        else:
            return None
    return values if values else None


def source_hash_matches(fixture: Path, source_path: Any, expected_hash: Any) -> bool:
    if not isinstance(source_path, str) or not isinstance(expected_hash, str) or not expected_hash:
        return False
    path = fixture / source_path
    if not path.exists() or not path.is_file():
        return False
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = expected_hash.strip().lower()
    if expected.startswith('sha256:'):
        expected = expected.split(':', 1)[1]
    return expected == actual


def validate_actor_provenance_present(task: dict[str, Any]) -> bool:
    provenance = task.get('actor_provenance')
    if not isinstance(provenance, dict):
        return False
    required = ['execution_actor_id', 'execution_actor_kind', 'execution_actor_lane', 'manager_role_at_execution', 'run_or_session_id', 'final_certifier_actor_id', 'final_certifier_actor_kind', 'final_certifier_lane', 'final_certifier_run_or_session_id', 'actor_provenance_artifacts']
    if any(not provenance.get(key) for key in required):
        return False
    if provenance.get('execution_actor_kind') not in {'manager', 'native_subagent', 'team_worker', 'user_gate', 'external_tool'}:
        return False
    if provenance.get('manager_role_at_execution') not in {'orchestrator', 'executor', 'reviewer', 'verifier', 'none'}:
        return False
    return isinstance(provenance.get('actor_provenance_artifacts'), list) and bool(provenance['actor_provenance_artifacts'])


def validate_actor_provenance_artifact_trusted(task: dict[str, Any], fixture: Path) -> bool:
    artifacts = load_provenance_artifacts(task, fixture)
    if not artifacts:
        return False
    task_id = task.get('task_id')
    executor = actor_record(task, 'executor')
    certifier = actor_record(task, 'final_certifier')
    input_refs = task_ref_values(task, ['input_materials'])
    output_refs = task_ref_values(task, ['expected_output_materials', 'expected_output_artifacts', 'collected_outputs'])
    if not executor or not certifier or not input_refs or not output_refs:
        return False
    for item in artifacts:
        if item.get('task_id') != task_id:
            return False
        if not item.get('provenance_artifact_id') or not item.get('source_type') or not item.get('source_path'):
            return False
        if not item.get('source_hash'):
            return False
        for section in ['producer', 'action', 'certifier', 'binding']:
            if not isinstance(item.get(section), dict):
                return False
        for section in ['producer', 'certifier']:
            actor = item[section]
            for field in ['actor_id', 'actor_kind', 'actor_lane', 'run_or_session_id']:
                if not actor.get(field):
                    return False
        if not actor_key_matches(item['producer'], executor):
            return False
        if not actor_key_matches(item['certifier'], certifier):
            return False
        action = item['action']
        material_refs = action_ref_values(action.get('material_refs'))
        produced_refs = action_ref_values(action.get('output_refs'))
        if not action.get('action_type') or material_refs is None or produced_refs is None:
            return False
        if not material_refs <= input_refs:
            return False
        if not produced_refs <= output_refs:
            return False
        binding = item['binding']
        if binding.get('task_id_matches_packet') is not True or binding.get('material_refs_exist') is not True:
            return False
        if binding.get('source_hash_verified') is not True:
            return False
        if not source_hash_matches(fixture, item.get('source_path'), item.get('source_hash')):
            return False
    return True


def validate_effective_actor_identity_resolved(task: dict[str, Any]) -> bool:
    return bool(actor_key_from_task(task, 'executor') and actor_key_from_task(task, 'final_certifier'))


def derived_sensitivity(task: dict[str, Any], refs: list[str]) -> tuple[bool, bool]:
    texts: list[str] = [str(task.get('owner_department') or ''), str(task.get('owner_lane') or '')]
    for field in ['input_materials', 'expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
        for item in task.get(field) or []:
            if isinstance(item, dict):
                texts.extend(str(item.get(k) or '') for k in ['artifact_id', 'artifact_type', 'path'])
    texts.extend(ref for ref in refs if ref not in AUTHORITY_VALIDATOR_REFS)
    texts.append(str(task.get('state_transition') or ''))
    joined = ' '.join(texts).lower()
    paper = any(term in joined for term in PAPER_FACING_TERMS) or str(task.get('owner_lane')) in PAPER_FACING_LANES
    state = any(term in joined for term in STATE_SENSITIVE_TERMS) or bool(task.get('state_transition')) or bool(task.get('state_ingestion'))
    return paper, state


def validate_derived_sensitivity_classification(task: dict[str, Any], refs: list[str]) -> bool:
    paper, state = derived_sensitivity(task, refs)
    mdi = task.get('manager_direct_intervention') or {}
    if paper and mdi.get('paper_facing') is False:
        return False
    if state and mdi.get('state_sensitive') is False:
        return False
    return True


def manager_direct_inferred(task: dict[str, Any]) -> bool:
    provenance = task.get('actor_provenance') or {}
    return provenance.get('execution_actor_kind') == 'manager' or provenance.get('manager_role_at_execution') in {'executor', 'reviewer', 'verifier'}


def manager_direct_declared(task: dict[str, Any]) -> bool:
    mdi = task.get('manager_direct_intervention') or {}
    return mdi.get('present') is True or mdi.get('inferred_from_actor_provenance') is True


def manager_direct_active(task: dict[str, Any]) -> bool:
    return manager_direct_declared(task) or manager_direct_inferred(task)


def validate_manager_direct_inferred_or_declared(task: dict[str, Any]) -> bool:
    return (not manager_direct_inferred(task)) or manager_direct_declared(task)


def validate_manager_direct_intervention_declared(task: dict[str, Any], fixture: Path) -> bool:
    mdi = task.get('manager_direct_intervention') or {}
    if not manager_direct_declared(task):
        return not manager_direct_inferred(task)
    intervention_id = mdi.get('intervention_id')
    if not intervention_id:
        return False
    candidates = [fixture / f'{intervention_id}.yaml', fixture / 'manager-direct-intervention.yaml', fixture / f'authority/{intervention_id}.yaml']
    data = None
    for path in candidates:
        if path.exists():
            data = load_yaml(path, {})
            break
    if not isinstance(data, dict):
        return False
    if data.get('task_id') != task.get('task_id') or data.get('forbidden_self_certification') is not True:
        return False
    return bool(data.get('manager_actions')) and data.get('allowed_completion_state') in {'candidate', 'validated', 'complete_after_independent_review'}


def independent_review_required(task: dict[str, Any], refs: list[str]) -> bool:
    mdi = task.get('manager_direct_intervention') or {}
    paper, state = derived_sensitivity(task, refs)
    return manager_direct_active(task) and (paper or state or mdi.get('required_independent_review') is True)


def load_independent_review_artifact(task: dict[str, Any], fixture: Path) -> dict[str, Any] | None:
    mdi = task.get('manager_direct_intervention') or {}
    rel = mdi.get('independent_review_artifact')
    if not isinstance(rel, str) or not rel.strip():
        return None
    path = fixture / rel
    if path.suffix.lower() not in {'.yaml', '.yml', '.json'} or not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8')) if path.suffix.lower() == '.json' else load_yaml(path, {})
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def review_artifact_actor(review: dict[str, Any]) -> dict[str, Any] | None:
    nested_raw = review.get('reviewer')
    nested: dict[str, Any] = nested_raw if isinstance(nested_raw, dict) else {}
    actor = {
        'actor_id': review.get('reviewer_actor_id') or nested.get('actor_id'),
        'actor_kind': review.get('reviewer_actor_kind') or nested.get('actor_kind'),
        'actor_lane': review.get('reviewer_lane') or review.get('reviewer_actor_lane') or nested.get('actor_lane') or nested.get('lane'),
        'run_or_session_id': review.get('reviewer_run_or_session_id') or nested.get('run_or_session_id'),
    }
    return actor if actor_key(actor) else None


def review_verdict_is_approving(value: Any) -> bool:
    return normalize_actor_part(value) in {'approve', 'approved', 'pass', 'passed', 'clear', 'accepted'}


def validate_manager_direct_independent_review(task: dict[str, Any], refs: list[str], fixture: Path) -> bool:
    if not independent_review_required(task, refs):
        return True
    review = load_independent_review_artifact(task, fixture)
    if not review or review.get('task_id') != task.get('task_id'):
        return False
    if not review_verdict_is_approving(review.get('verdict')):
        return False
    if not (review.get('evidence') or review.get('evidence_path')):
        return False
    review_actor = review_artifact_actor(review)
    declared_reviewer = actor_record(task, 'reviewer')
    if not review_actor or not declared_reviewer:
        return False
    if not same_effective_actor(review_actor, declared_reviewer):
        return False
    executor = actor_record(task, 'executor')
    certifier = actor_record(task, 'final_certifier')
    return actors_are_independent(executor, review_actor, certifier)


def validate_no_manager_self_certification(task: dict[str, Any], refs: list[str]) -> bool:
    if not independent_review_required(task, refs):
        return True
    return actors_are_independent(actor_record(task, 'executor'), actor_record(task, 'reviewer'), actor_record(task, 'final_certifier'))


def validate_role_separation_for_paper_facing_tasks(task: dict[str, Any], refs: list[str]) -> bool:
    paper, state = derived_sensitivity(task, refs)
    if not (paper or state):
        return True
    return validate_effective_actor_identity_resolved(task) and validate_no_manager_self_certification(task, refs)


def parse_authority_blocks_from_markdown(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for match in re.finditer(r'```ya?ml\s*\n(.*?)\n```', text, flags=re.IGNORECASE | re.DOTALL):
        body = match.group(1)
        if 'authority_role_separation:' not in body:
            continue
        data = yaml.safe_load(body)
        if isinstance(data, dict) and isinstance(data.get('authority_role_separation'), dict):
            blocks.append(data['authority_role_separation'])
    return blocks


def authority_role_separation_blocks(fixture: Path) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for path in fixture.rglob('*.md'):
        try:
            blocks.extend(parse_authority_blocks_from_markdown(path.read_text(encoding='utf-8', errors='ignore')))
        except Exception:
            continue
    for path in fixture.rglob('*.yaml'):
        data = load_yaml(path, {})
        if isinstance(data, dict) and isinstance(data.get('authority_role_separation'), dict):
            blocks.append(data['authority_role_separation'])
    return blocks


def list_contains_value(values: Any, value: Any) -> bool:
    if not isinstance(values, list):
        return False
    target = normalize_actor_part(value)
    return any(normalize_actor_part(item) == target for item in values)


def handoff_block_matches_task(block: dict[str, Any], task: dict[str, Any], refs: list[str]) -> bool:
    mdi = task.get('manager_direct_intervention') or {}
    provenance = task.get('actor_provenance') or {}
    intervention_id = mdi.get('intervention_id')
    review_required = independent_review_required(task, refs)
    if block.get('manager_direct_used') is not True:
        return False
    if intervention_id and not list_contains_value(block.get('manager_direct_interventions'), intervention_id):
        return False
    if manager_direct_inferred(task) and block.get('inferred_manager_direct') is not True:
        return False
    if normalize_actor_part(block.get('execution_actor_id')) != normalize_actor_part(provenance.get('execution_actor_id')):
        return False
    if normalize_actor_part(block.get('final_certifier_actor_id')) != normalize_actor_part(provenance.get('final_certifier_actor_id')):
        return False
    if block.get('independent_review_required') is not review_required:
        return False
    if review_required:
        rel = mdi.get('independent_review_artifact')
        if not list_contains_value(block.get('independent_review_artifacts'), rel):
            return False
    if not block.get('completion_claim'):
        return False
    if task.get('status') == 'complete' and normalize_actor_part(block.get('completion_claim')) != 'complete':
        return False
    if not block.get('completion_limit_reason') or not block.get('residual_self_certification_risk'):
        return False
    return True


def validate_manager_direct_handoff_disclosure(task: dict[str, Any], fixture: Path, refs: list[str]) -> bool:
    if not manager_direct_active(task):
        return True
    return any(handoff_block_matches_task(block, task, refs) for block in authority_role_separation_blocks(fixture))


def validate_completion_state_limited_without_independent_review(task: dict[str, Any], refs: list[str], fixture: Path) -> bool:
    if task.get('status') != 'complete':
        return True
    if not independent_review_required(task, refs):
        return True
    return validate_manager_direct_independent_review(task, refs, fixture) and validate_no_manager_self_certification(task, refs)

def load_named_material(fixture: Path, *names: str) -> dict[str, Any] | None:
    for name in names:
        path = fixture / name
        if path.exists():
            data = load_yaml(path, {})
            if isinstance(data, dict):
                return data
    return None


DEPARTMENT_IDS = {
    'pmo',
    'paper_architecture_and_narrative',
    'evidence_and_method',
    'manuscript_and_figure_production',
    'review_and_governance',
}

DEPARTMENT_VALIDATOR_NAMES = {
    'validate_department_charters',
    'validate_department_material_manifest',
    'validate_department_lane_registry',
    'validate_required_function_material_map',
    'validate_no_orphan_material_owner',
    'validate_no_orphan_function_owner',
    'validate_no_public_department_exposure',
    'validate_no_route_card_completion_claim',
    'validate_manager_boot_checklist',
    'validate_department_state_projection',
}

DEPARTMENT_FAILURE_CODES = {
    'validate_department_charters': 'MISSING_DEPARTMENT_CHARTER',
    'validate_no_orphan_material_owner': 'ORPHAN_MATERIAL_OWNER',
    'validate_no_orphan_function_owner': 'ORPHAN_FUNCTION_OWNER',
    'validate_agent_lane_department_binding': 'LANE_WITHOUT_DEPARTMENT',
    'validate_no_public_department_exposure': 'PUBLIC_INTERNAL_DEPARTMENT',
    'validate_company_skill_registry': 'HIDDEN_MANAGER_SKILL',
    'validate_no_route_card_completion_claim': 'ROUTE_CARD_COMPLETION_CLAIM',
    'validate_manager_boot_checklist': 'MANAGER_BOOT_MISSING_DEPARTMENT_STATE_OR_GAP',
    'validate_department_state_projection': 'DEPARTMENT_STATE_USED_AS_COMPLETION_EVIDENCE',
}


def material_list(data: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    values = data.get(key) or []
    return [item for item in values if isinstance(item, dict)]


def fixture_meta(fixture: Path) -> dict[str, Any]:
    data = load_yaml(fixture / 'fixture-meta.yaml', {})
    return data if isinstance(data, dict) else {}


def department_fixture_active(fixture: Path, meta: dict[str, Any], tasks: Any) -> bool:
    expected = set(meta.get('expected_failures') or [])
    if expected & DEPARTMENT_VALIDATOR_NAMES:
        return True
    department_files = {
        'department-charter.yaml',
        'department-charters.yaml',
        'department-material-manifest.yaml',
        'department-lane-registry.yaml',
        'department-handoff-report.yaml',
        'required-function-material-map.yaml',
        'manager-boot-checklist.yaml',
        'department-state.yaml',
        'department-route-card.yaml',
        'public-skill-manifest.json',
    }
    return any((fixture / name).exists() for name in department_files)


def department_charters_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-charter.yaml', {})
    if not data:
        data = load_yaml(fixture / 'department-charters.yaml', {})
    departments = material_list(data, 'departments')
    seen = {str(item.get('department_id') or '') for item in departments}
    if not DEPARTMENT_IDS.issubset(seen):
        return False
    for item in departments:
        if str(item.get('department_id') or '') not in DEPARTMENT_IDS:
            return False
        if not has_text(item.get('display_name')) or not has_text(item.get('primary_responsibility')):
            return False
        if not non_empty_list(item.get('validator_refs')):
            return False
    return True


def department_material_manifest_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-material-manifest.yaml', {})
    materials = material_list(data, 'materials')
    if not materials:
        return False
    for item in materials:
        if not has_text(item.get('material_id')) or not has_text(item.get('artifact_type')):
            return False
        if not has_text(item.get('owner_lane')):
            return False
        if not non_empty_list(item.get('validator_refs')) or not non_empty_list(item.get('ledger_targets')):
            return False
    return True


def no_orphan_material_owner_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-material-manifest.yaml', {})
    materials = material_list(data, 'materials')
    if not materials:
        return False
    for item in materials:
        owner = str(item.get('owner_department') or '')
        if owner not in DEPARTMENT_IDS:
            return False
    return True


def department_lane_registry_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-lane-registry.yaml', {})
    lanes = material_list(data, 'lanes')
    if not lanes:
        return False
    for item in lanes:
        if not has_text(item.get('lane_id')) or not has_text(item.get('agent_type')):
            return False
        if not non_empty_list(item.get('validator_refs')):
            return False
    return True


def lane_agent_department_binding_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-lane-registry.yaml', {})
    lanes = material_list(data, 'lanes')
    if not lanes:
        return False
    for item in lanes:
        if has_text(item.get('agent_type')) and str(item.get('department_id') or item.get('owner_department') or '') not in DEPARTMENT_IDS:
            return False
    return True


def required_function_material_map_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'required-function-material-map.yaml', {})
    functions = material_list(data, 'functions')
    if not functions:
        return False
    for item in functions:
        if not has_text(item.get('function_id')):
            return False
        if not non_empty_list(item.get('output_materials')) or not non_empty_list(item.get('validators')):
            return False
        if not has_text(item.get('backflow_target')):
            return False
    return True


def no_orphan_function_owner_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'required-function-material-map.yaml', {})
    functions = material_list(data, 'functions')
    if not functions:
        return False
    for item in functions:
        owner = str(item.get('primary_department') or '')
        if owner not in DEPARTMENT_IDS:
            return False
    return True


def no_public_department_exposure_ok(fixture: Path, root: Path) -> bool:
    manifest_path = fixture / 'public-skill-manifest.json'
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except Exception:
            return False
    else:
        try:
            manifest = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        except Exception:
            return False
    text = json.dumps(manifest)
    forbidden = {
        'department-charter',
        'department-manager',
        'paper-architecture-and-narrative',
        'evidence-and-method',
        'manuscript-and-figure-production',
        'review-and-governance',
        'yxj-paper-pmo',
    }
    if any(marker in text for marker in forbidden):
        return False
    if isinstance(manifest, dict) and manifest.get('skills') not in {PUBLIC_SKILLS_RESOURCE, './entry-skills/'}:
        return False
    return True


def no_route_card_completion_claim_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-route-card.yaml', {})
    if not data:
        return True
    boundaries = data.get('authority_boundaries') or {}
    manager = data.get('department_manager') or {}
    authority = manager.get('authority_scope') if isinstance(manager, dict) else {}
    closure = normalize_material_key(data.get('closure_state'))
    if closure in {'complete', 'completed', 'validated', 'ready', 'done'}:
        return False
    if isinstance(boundaries, dict) and boundaries.get('route_card_is_completion_evidence') is not False:
        return False
    if isinstance(authority, dict) and authority.get('may_certify_completion') is not False:
        return False
    return True


def manager_boot_checklist_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'manager-boot-checklist.yaml', {})
    if not data:
        return False
    report = data.get('status_report') or {}
    if 'Paper Manager' not in str(data.get('manager_identity') or report.get('self_identifies_as') or ''):
        return False
    has_state = has_text(data.get('department_state_ref')) or bool(report.get('department_state_loaded'))
    gap_disclosed = bool(report.get('missing_department_state_gap_disclosed') or data.get('missing_department_state_gap'))
    if not (has_state or gap_disclosed):
        return False
    if not non_empty_list(data.get('required_departments_checked')):
        return False
    return True


def department_state_projection_ok(fixture: Path) -> bool:
    data = load_yaml(fixture / 'department-state.yaml', {})
    if not data:
        return False
    if data.get('projection_only') is not True:
        return False
    if data.get('used_as_completion_evidence') is not False or data.get('completion_evidence') is True:
        return False
    if normalize_material_key(data.get('closure_state')) in {'complete', 'completed', 'validated', 'ready', 'done'}:
        return False
    departments = material_list(data, 'departments')
    return DEPARTMENT_IDS.issubset({str(item.get('department_id') or '') for item in departments})


def validate_department_accountability_fixture(
    fixture: Path,
    root: Path,
    tasks: Any,
    artifacts: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    meta = fixture_meta(fixture)
    if not department_fixture_active(fixture, meta, tasks):
        return [], {}
    checks = {
        'validate_department_charters': department_charters_ok(fixture),
        'validate_department_material_manifest': department_material_manifest_ok(fixture),
        'validate_no_orphan_material_owner': no_orphan_material_owner_ok(fixture),
        'validate_department_lane_registry': department_lane_registry_ok(fixture),
        'validate_agent_lane_department_binding': lane_agent_department_binding_ok(fixture),
        'validate_required_function_material_map': required_function_material_map_ok(fixture),
        'validate_no_orphan_function_owner': no_orphan_function_owner_ok(fixture),
        'validate_no_public_department_exposure': no_public_department_exposure_ok(fixture, root),
        'validate_no_route_card_completion_claim': no_route_card_completion_claim_ok(fixture),
        'validate_manager_boot_checklist': manager_boot_checklist_ok(fixture),
        'validate_department_state_projection': department_state_projection_ok(fixture),
    }
    failures = [name for name, ok in checks.items() if not ok]
    if (fixture / 'company-skill-registry.yaml').exists() and not validate_company_skill_registry_material(fixture, artifacts, tasks):
        failures.append('validate_company_skill_registry')
    detail = {
        'active': True,
        'diagnostic_codes': [
            {'validator': name, 'code': DEPARTMENT_FAILURE_CODES.get(name, name)}
            for name in sorted(set(failures))
        ],
    }
    return sorted(set(failures)), detail


def non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def non_empty_dict(value: Any) -> bool:
    return isinstance(value, dict) and bool(value)


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())



MATERIAL_OBJECT_SPECS: dict[str, dict[str, Any]] = {
    'ReviewerQuestionMap': {
        'filenames': {'reviewer-question-map.yaml'},
        'schema_version': 'yxj-paper-os/reviewer-question-map/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_reviewer_question_map',
        'aliases': {'ReviewerQuestionMap', 'reviewer-question-map', 'reviewer_question_map'},
    },
    'MainTextConstructionMatrix': {
        'filenames': {'main-text-construction-matrix.yaml'},
        'schema_version': 'yxj-paper-os/main-text-construction-matrix/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_main_text_construction_matrix_refs',
        'aliases': {'MainTextConstructionMatrix', 'main-text-construction-matrix', 'main_text_construction_matrix'},
    },
    'CognitiveLoadBudget': {
        'filenames': {'cognitive-load-budget.yaml'},
        'schema_version': 'yxj-paper-os/cognitive-load-budget/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_cognitive_load_budget',
        'aliases': {'CognitiveLoadBudget', 'cognitive-load-budget', 'cognitive_load_budget'},
    },
    'ExplanationLadder': {
        'filenames': {'explanation-ladder.yaml'},
        'schema_version': 'yxj-paper-os/explanation-ladder/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_explanation_ladder',
        'aliases': {'ExplanationLadder', 'explanation-ladder', 'explanation_ladder'},
    },
    'RhetoricalMoveMatrix': {
        'filenames': {'rhetorical-move-matrix.yaml'},
        'schema_version': 'yxj-paper-os/rhetorical-move-matrix/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_rhetorical_move_matrix',
        'aliases': {'RhetoricalMoveMatrix', 'rhetorical-move-matrix', 'rhetorical_move_matrix'},
    },
    'ClaimEvidenceVisibilityMap': {
        'filenames': {'claim-evidence-visibility-map.yaml'},
        'schema_version': 'yxj-paper-os/claim-evidence-visibility-map/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_claim_evidence_visibility_map',
        'aliases': {'ClaimEvidenceVisibilityMap', 'claim-evidence-visibility-map', 'claim_evidence_visibility_map'},
    },
    'TerminologyRegister': {
        'filenames': {'terminology-register.yaml'},
        'schema_version': 'yxj-paper-os/terminology-register/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect'},
        'validator': 'validate_terminology_register',
        'aliases': {'TerminologyRegister', 'terminology-register', 'terminology_register'},
    },
    'ClaimCitationCapsule': {
        'filenames': {'claim-citation-capsule.yaml'},
        'schema_version': 'yxj-paper-os/claim-citation-capsule/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'evidence_and_method'},
        'allowed_lanes': {'evidence-curator', 'method-verifier'},
        'validator': 'validate_claim_citation_capsule_support',
        'aliases': {'ClaimCitationCapsule', 'claim-citation-capsule', 'claim_citation_capsule'},
    },
    'ResultPackage': {
        'filenames': {'result-package.yaml'},
        'schema_version': 'yxj-paper-os/result-package/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'evidence_and_method'},
        'allowed_lanes': {'evidence-curator', 'method-verifier'},
        'validator': 'validate_result_package_claim_boundary',
        'aliases': {'ResultPackage', 'result-package', 'result_package'},
    },
    'SingleWriterSectionLock': {
        'filenames': {'single-writer-section-lock.yaml'},
        'schema_version': 'yxj-paper-os/single-writer-section-lock/v1',
        'owner_fields': {'owner_department'},
        'allowed_departments': {'pmo'},
        'allowed_lanes': {'single-writer-lock-owner'},
        'validator': 'validate_single_writer_lock_held',
        'aliases': {'SingleWriterSectionLock', 'single-writer-section-lock', 'single_writer_section_lock'},
    },
    'ReaderSurfaceTutorReview': {
        'filenames': {'reader-surface-tutor-review.yaml'},
        'schema_version': 'yxj-paper-os/reader-surface-tutor-review/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'review_and_governance'},
        'allowed_lanes': {'review-director', 'style-auditor', 'final-verifier'},
        'validator': 'validate_reader_surface_tutor_review_spans',
        'aliases': {'ReaderSurfaceTutorReview', 'reader-surface-tutor-review', 'reader_surface_tutor_review'},
    },
    'RenderedSurfaceGateReport': {
        'filenames': {'rendered-surface-gate-report.yaml'},
        'schema_version': 'yxj-paper-os/rendered-surface-gate-report/v1',
        'owner_fields': {'owning_department'},
        'allowed_departments': {'review_and_governance', 'manuscript_and_figure_production'},
        'allowed_lanes': {'review-director', 'style-auditor', 'final-verifier', 'export-owner'},
        'validator': 'validate_no_internal_codes_in_rendered_text',
        'aliases': {'RenderedSurfaceGateReport', 'rendered-surface-gate-report', 'rendered_surface_gate_report'},
    },
    'NatureFigureContract': {
        'filenames': {'nature-figure-contract.yaml'},
        'schema_version': 'yxj-paper-os/nature-figure-contract/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'paper_architecture_and_narrative', 'manuscript_and_figure_production'},
        'allowed_lanes': {'paper-architect', 'figure-owner'},
        'validator': 'validate_nature_figure_contract',
        'aliases': {'NatureFigureContract', 'nature-figure-contract', 'nature_figure_contract'},
    },
    'NatureFigureAestheticProfile': {
        'filenames': {'nature-figure-aesthetic-profile.yaml'},
        'schema_version': 'yxj-paper-os/nature-figure-aesthetic-profile/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'paper_architecture_and_narrative', 'manuscript_and_figure_production'},
        'allowed_lanes': {'paper-architect', 'figure-owner'},
        'validator': 'validate_nature_figure_aesthetic_profile',
        'aliases': {'NatureFigureAestheticProfile', 'nature-figure-aesthetic-profile', 'nature_figure_aesthetic_profile'},
    },
    'NaturePanelEvidenceMap': {
        'filenames': {'nature-panel-evidence-map.yaml'},
        'schema_version': 'yxj-paper-os/nature-panel-evidence-map/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method', 'paper_architecture_and_narrative'},
        'allowed_lanes': {'evidence-curator', 'method-verifier', 'paper-architect'},
        'validator': 'validate_panel_evidence_map',
        'aliases': {'NaturePanelEvidenceMap', 'nature-panel-evidence-map', 'nature_panel_evidence_map'},
    },
    'FigureBackendRoute': {
        'filenames': {'figure-backend-route.yaml'},
        'schema_version': 'yxj-paper-os/figure-backend-route/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'manuscript_and_figure_production'},
        'allowed_lanes': {'figure-owner', 'export-owner'},
        'validator': 'validate_figure_backend_route',
        'aliases': {'FigureBackendRoute', 'figure-backend-route', 'figure_backend_route'},
    },
    'FigureSourceDataStatistics': {
        'filenames': {'figure-source-data-statistics.yaml'},
        'schema_version': 'yxj-paper-os/figure-source-data-statistics/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method'},
        'allowed_lanes': {'method-verifier', 'evidence-curator'},
        'validator': 'validate_figure_source_data_statistics',
        'aliases': {'FigureSourceDataStatistics', 'figure-source-data-statistics', 'figure_source_data_statistics'},
    },
    'FigureImageIntegrityRecord': {
        'filenames': {'figure-image-integrity-record.yaml'},
        'schema_version': 'yxj-paper-os/figure-image-integrity-record/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method', 'manuscript_and_figure_production'},
        'allowed_lanes': {'method-verifier', 'evidence-curator', 'figure-owner'},
        'validator': 'validate_figure_image_integrity_record',
        'aliases': {'FigureImageIntegrityRecord', 'figure-image-integrity-record', 'figure_image_integrity_record'},
    },
    'NatureCaptionLegendBrief': {
        'filenames': {'nature-caption-legend-brief.yaml'},
        'schema_version': 'yxj-paper-os/nature-caption-legend-brief/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'manuscript_and_figure_production'},
        'allowed_lanes': {'figure-owner', 'manuscript-owner'},
        'validator': 'validate_nature_caption_legend',
        'aliases': {'NatureCaptionLegendBrief', 'nature-caption-legend-brief', 'nature_caption_legend_brief'},
    },
    'NatureFigureQAReport': {
        'filenames': {'nature-figure-qa-report.yaml'},
        'schema_version': 'yxj-paper-os/nature-figure-qa-report/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'review_and_governance'},
        'allowed_lanes': {'review-director', 'style-auditor', 'final-verifier'},
        'validator': 'validate_nature_figure_qa_report',
        'aliases': {'NatureFigureQAReport', 'nature-figure-qa-report', 'nature_figure_qa_report'},
    },
    'FigureExportBundle': {
        'filenames': {'figure-export-bundle.yaml'},
        'schema_version': 'yxj-paper-os/figure-export-bundle/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'manuscript_and_figure_production'},
        'allowed_lanes': {'export-owner', 'figure-owner'},
        'validator': 'validate_figure_export_bundle',
        'aliases': {'FigureExportBundle', 'figure-export-bundle', 'figure_export_bundle'},
    },

    'NatureSourceInventory': {
        'filenames': {'nature-source-inventory.yaml'},
        'schema_version': 'yxj-paper-os/nature-source-inventory/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'pmo'},
        'allowed_lanes': {'skill-registry-owner', 'research-director'},
        'validator': 'validate_nature_source_inventory',
        'aliases': {'NatureSourceInventory', 'nature-source-inventory', 'nature_source_inventory'},
    },
    'CompanySkillRegistry': {
        'filenames': {'company-skill-registry.yaml'},
        'schema_version': 'yxj-paper-os/company-skill-registry/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'pmo'},
        'allowed_lanes': {'skill-registry-owner'},
        'validator': 'validate_company_skill_registry',
        'aliases': {'CompanySkillRegistry', 'company-skill-registry', 'company_skill_registry'},
    },
    'NatureAbsorptionPackage': {
        'filenames': {'nature-absorption-package.yaml'},
        'schema_version': 'yxj-paper-os/nature-absorption-package/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'pmo'},
        'allowed_lanes': {'skill-registry-owner', 'final-verifier'},
        'validator': 'validate_nature_absorption_package',
        'aliases': {'NatureAbsorptionPackage', 'nature-absorption-package', 'nature_absorption_package'},
    },
    'PaperReaderPackage': {
        'filenames': {'paper-reader-package.yaml'},
        'schema_version': 'yxj-paper-os/paper-reader-package/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method'},
        'allowed_lanes': {'evidence-curator', 'source-map-curator'},
        'validator': 'validate_paper_reader_package',
        'aliases': {'PaperReaderPackage', 'paper-reader-package', 'paper_reader_package'},
    },
    'SearchStrategyDossier': {
        'filenames': {'search-strategy-dossier.yaml'},
        'schema_version': 'yxj-paper-os/search-strategy-dossier/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method', 'paper_architecture_and_narrative'},
        'allowed_lanes': {'sota-mapper', 'research-director'},
        'validator': 'validate_search_strategy_dossier',
        'aliases': {'SearchStrategyDossier', 'search-strategy-dossier', 'search_strategy_dossier'},
    },
    'CitationVerificationReport': {
        'filenames': {'citation-verification-report.yaml'},
        'schema_version': 'yxj-paper-os/citation-verification-report/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method'},
        'allowed_lanes': {'citation-banker', 'evidence-curator'},
        'validator': 'validate_citation_verification_report',
        'aliases': {'CitationVerificationReport', 'citation-verification-report', 'citation_verification_report'},
    },
    'SectionMovePlan': {
        'filenames': {'section-move-plan.yaml'},
        'schema_version': 'yxj-paper-os/section-move-plan/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'paper-architect', 'manuscript-owner'},
        'validator': 'validate_section_move_plan',
        'aliases': {'SectionMovePlan', 'section-move-plan', 'section_move_plan'},
    },
    'JournalStyleProfile': {
        'filenames': {'journal-style-profile.yaml'},
        'schema_version': 'yxj-paper-os/journal-style-profile/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'paper_architecture_and_narrative'},
        'allowed_lanes': {'exemplar-learner', 'paper-architect', 'style-auditor'},
        'validator': 'validate_journal_style_profile',
        'aliases': {'JournalStyleProfile', 'journal-style-profile', 'journal_style_profile'},
    },
    'PolishingRepairReport': {
        'filenames': {'polishing-repair-report.yaml'},
        'schema_version': 'yxj-paper-os/polishing-repair-report/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'manuscript_and_figure_production', 'review_and_governance'},
        'allowed_lanes': {'manuscript-owner', 'style-auditor'},
        'validator': 'validate_polishing_repair_report',
        'aliases': {'PolishingRepairReport', 'polishing-repair-report', 'polishing_repair_report'},
    },
    'DataAvailabilityPlan': {
        'filenames': {'data-availability-plan.yaml'},
        'schema_version': 'yxj-paper-os/data-availability-plan/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'evidence_and_method'},
        'allowed_lanes': {'method-verifier', 'evidence-curator'},
        'validator': 'validate_data_availability_plan',
        'aliases': {'DataAvailabilityPlan', 'data-availability-plan', 'data_availability_plan'},
    },
    'ReviewerPanelReport': {
        'filenames': {'reviewer-panel-report.yaml'},
        'schema_version': 'yxj-paper-os/reviewer-panel-report/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'review_and_governance'},
        'allowed_lanes': {'review-director', 'final-verifier'},
        'validator': 'validate_reviewer_panel_report',
        'aliases': {'ReviewerPanelReport', 'reviewer-panel-report', 'reviewer_panel_report'},
    },
    'ResponseActionMap': {
        'filenames': {'response-action-map.yaml'},
        'schema_version': 'yxj-paper-os/response-action-map/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'review_and_governance'},
        'allowed_lanes': {'review-director', 'manuscript-owner'},
        'validator': 'validate_response_action_map',
        'aliases': {'ResponseActionMap', 'response-action-map', 'response_action_map'},
    },
    'PresentationPlan': {
        'filenames': {'presentation-plan.yaml'},
        'schema_version': 'yxj-paper-os/presentation-plan/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'manuscript_and_figure_production'},
        'allowed_lanes': {'manuscript-owner', 'paper-architect'},
        'validator': 'validate_presentation_plan',
        'aliases': {'PresentationPlan', 'presentation-plan', 'presentation_plan'},
    },
    'PatentDraftBoundary': {
        'filenames': {'patent-draft-boundary.yaml'},
        'schema_version': 'yxj-paper-os/patent-draft-boundary/v1',
        'owner_fields': {'owning_department', 'owner_department'},
        'allowed_departments': {'manuscript_and_figure_production', 'evidence_and_method'},
        'allowed_lanes': {'docs-writer', 'manuscript-owner', 'method-verifier'},
        'validator': 'validate_patent_draft_boundary',
        'aliases': {'PatentDraftBoundary', 'patent-draft-boundary', 'patent_draft_boundary'},
    },
}


INTERNAL_CODE_PATTERNS = [
    re.compile(r'\bS[0-9]+(?:/S[0-9]+)+\b'),
    re.compile(r'\b[A-Za-z0-9]+_[A-Za-z0-9_]*\b'),
    re.compile(r'\b(?:VG-KZTR_full|B2_[A-Za-z0-9_]+|no_[A-Za-z0-9_]+)\b'),
]


def normalize_material_key(value: Any) -> str:
    return re.sub(r'[^a-z0-9]+', '', str(value or '').lower())


def material_spec_matches_entry(spec: dict[str, Any], entry: dict[str, Any]) -> bool:
    artifact_type = normalize_material_key(entry.get('artifact_type') or entry.get('type'))
    aliases = {normalize_material_key(alias) for alias in spec.get('aliases') or set()}
    path_name = Path(str(entry.get('path') or '')).name
    return artifact_type in aliases or path_name in set(spec.get('filenames') or set())


def material_spec_for_data(data: dict[str, Any]) -> dict[str, Any] | None:
    schema = data.get('schema_version')
    for spec in MATERIAL_OBJECT_SPECS.values():
        if schema == spec.get('schema_version'):
            return spec
    return None


def declared_task_material_entries(
    tasks: Any,
    spec: dict[str, Any],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    entries: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        for field in ['expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
            for item in task.get(field) or []:
                if isinstance(item, dict) and material_spec_matches_entry(spec, item):
                    entries.append((task, item))
    return entries


def declared_artifact_entries(artifacts: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        art for art in artifacts.get('artifacts') or []
        if isinstance(art, dict) and material_spec_matches_entry(spec, art)
    ]


def material_declared_paths(
    fixture: Path,
    spec: dict[str, Any],
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> list[str]:
    paths: set[str] = set()
    for filename in spec.get('filenames') or set():
        if (fixture / filename).exists():
            paths.add(str(filename))
    if artifacts:
        for art in declared_artifact_entries(artifacts, spec):
            path = art.get('path')
            if isinstance(path, str) and path:
                paths.add(path.rstrip('/'))
    for _, item in declared_task_material_entries(tasks, spec):
        path = item.get('path')
        if isinstance(path, str) and path:
            paths.add(path.rstrip('/'))
    return sorted(paths)


def material_data_items(
    fixture: Path,
    spec: dict[str, Any],
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> list[tuple[str, dict[str, Any] | None]]:
    items: list[tuple[str, dict[str, Any] | None]] = []
    for rel in material_declared_paths(fixture, spec, artifacts, tasks):
        data = load_yaml(fixture / rel, {})
        items.append((rel, data if isinstance(data, dict) else None))
    return items


def material_owner_department(data: dict[str, Any], spec: dict[str, Any]) -> str:
    for field in spec.get('owner_fields') or set():
        value = data.get(field)
        if isinstance(value, str) and value:
            return value
    return ''


def lane_department(lane_id: Any, registry_lanes: dict[str, dict[str, Any]]) -> str:
    lane = registry_lanes.get(str(lane_id or '')) or {}
    return str(lane.get('department') or '')


def validate_known_material_object_bindings(
    fixture: Path,
    artifacts: dict[str, Any],
    tasks: Any,
    registry_lanes: dict[str, dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    for spec in MATERIAL_OBJECT_SPECS.values():
        allowed_lanes = set(spec.get('allowed_lanes') or set())
        allowed_departments = set(spec.get('allowed_departments') or set())
        object_validator = str(spec.get('validator'))
        paths = material_declared_paths(fixture, spec, artifacts, tasks)
        if not paths:
            continue

        for rel, data in material_data_items(fixture, spec, artifacts, tasks):
            if data is None:
                failures.append(object_validator)
                continue
            if material_spec_for_data(data) != spec:
                failures.append(object_validator)
            owner_department = material_owner_department(data, spec)
            if owner_department not in allowed_departments:
                failures.append('validate_agent_lane_department_binding')

        artifact_entries = declared_artifact_entries(artifacts, spec)
        for rel in paths:
            path_artifacts = [
                art for art in artifact_entries
                if str(art.get('path') or '').rstrip('/') == rel
            ]
            if not path_artifacts:
                failures.append('validate_owner_lane_closure')
            for art in path_artifacts:
                owner_lane = str(art.get('owner_lane') or '')
                if owner_lane not in allowed_lanes:
                    failures.append('validate_owner_lane_closure')
                if lane_department(owner_lane, registry_lanes) not in allowed_departments:
                    failures.append('validate_agent_lane_department_binding')

        for task, item in declared_task_material_entries(tasks, spec):
            owner_lane = str(task.get('owner_lane') or '')
            task_department = str(task.get('owner_department') or lane_department(owner_lane, registry_lanes))
            if owner_lane not in allowed_lanes:
                failures.append('validate_owner_lane_closure')
            if task_department not in allowed_departments:
                failures.append('validate_agent_lane_department_binding')
            path = str(item.get('path') or '').rstrip('/')
            if path and not (fixture / path).exists():
                failures.append(object_validator)
    return sorted(set(failures))


def validate_reviewer_question_map_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ReviewerQuestionMap'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        required = ['target_reader', 'reviewer_personas', 'questions', 'section_targets', 'risk_tags', 'downstream_consumers']
        if any(not data.get(field) for field in required):
            return False
        if not non_empty_list(data.get('reviewer_personas')) or not non_empty_list(data.get('questions')):
            return False
        for q in data.get('questions') or []:
            if not isinstance(q, dict) or not has_text(q.get('question_id')) or not has_text(q.get('question')):
                return False
            if not non_empty_list(q.get('expected_answer_location')):
                return False
    return True


def validate_main_text_construction_matrix_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['MainTextConstructionMatrix'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        rows_value = data.get('rows')
        if not isinstance(rows_value, list) or not rows_value:
            return False
        rows: list[Any] = rows_value
        for row in rows:
            if not isinstance(row, dict):
                return False
            for field in ['section', 'manuscript_unit', 'reader_question', 'object_representation', 'granularity', 'evidence_anchor', 'template_rule', 'surface_rule', 'final_text_check']:
                if not row.get(field):
                    return False
            anchor = row.get('evidence_anchor')
            if not isinstance(anchor, dict) or anchor.get('required') is not True or not has_text(anchor.get('artifact_id')):
                return False
            obj = row.get('object_representation')
            if not isinstance(obj, dict) or not has_text(obj.get('object')) or not has_text(obj.get('form')):
                return False
    return True


def validate_cognitive_load_budget_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['CognitiveLoadBudget'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        if not has_text(data.get('budget_id') or data.get('artifact_id')):
            return False
        sections = data.get('section_budgets') or data.get('sections')
        if not isinstance(sections, list) or not sections:
            return False
        forbidden = data.get('forbidden_overload_rules') or data.get('forbidden_rules')
        if not non_empty_list(forbidden):
            return False
        for section in sections:
            if not isinstance(section, dict):
                return False
            if not has_text(section.get('section_id') or section.get('section')):
                return False
            limits = section.get('load_limits') or section.get('budget') or section.get('reader_load_budget')
            if not (non_empty_dict(limits) or non_empty_list(limits)):
                return False
            if not (section.get('forbidden_overload_rules') or forbidden):
                return False
    return True


def validate_cognitive_load_budget_consumed_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['CognitiveLoadBudget'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        consumers = data.get('downstream_consumers') or data.get('consumers') or data.get('downstream_task_refs')
        if not non_empty_list(consumers):
            return False
    return True


def validate_explanation_ladder_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ExplanationLadder'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        if not has_text(data.get('ladder_id') or data.get('artifact_id')):
            return False
        steps = data.get('steps') or data.get('ladder') or data.get('rows')
        if not isinstance(steps, list) or len(steps) < 3:
            return False
        for step in steps:
            if not isinstance(step, dict):
                return False
            if not has_text(step.get('stage') or step.get('level')):
                return False
            if not has_text(step.get('reader_explanation') or step.get('explanation') or step.get('planned_text')):
                return False
    return True


def validate_explanation_ladder_progression_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ExplanationLadder'], artifacts, tasks)
    if not items:
        return True
    required = {'intuition', 'mechanism', 'evidence'}
    forbidden_jump = {'claim', 'resultclaim', 'conclusion'}
    for _, data in items:
        if data is None:
            return False
        steps = data.get('steps') or data.get('ladder') or data.get('rows') or []
        stage_names = [normalize_material_key(step.get('stage') or step.get('level')) for step in steps if isinstance(step, dict)]
        if not stage_names:
            return False
        if not all(any(req in stage for stage in stage_names) for req in required):
            return False
        if stage_names[0] in forbidden_jump:
            return False
        if any('raw' in stage or 'internal' in stage or 'formal' in stage for stage in stage_names[:1]):
            if len(stage_names) < 4:
                return False
            before_claim = stage_names[: max((i for i, s in enumerate(stage_names) if 'claim' in s), default=len(stage_names))]
            if not all(any(req in stage for stage in before_claim) for req in required):
                return False
    return True


def validate_rhetorical_move_matrix_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['RhetoricalMoveMatrix'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        rows = data.get('rows') or data.get('moves')
        if not isinstance(rows, list) or not rows:
            return False
        for row in rows:
            if not isinstance(row, dict):
                return False
            for field in ['reader_question', 'object', 'granularity', 'planned_text_move', 'final_text_check']:
                if not has_text(row.get(field)):
                    return False
            anchor = row.get('evidence_anchor')
            if not (has_text(anchor) or (isinstance(anchor, dict) and (has_text(anchor.get('artifact_id')) or has_text(anchor.get('source'))))):
                return False
    return True


def validate_rhetorical_move_matrix_consumed_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['RhetoricalMoveMatrix'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        consumers = data.get('downstream_consumers') or data.get('consumers') or data.get('downstream_task_refs')
        if not non_empty_list(consumers):
            return False
    return True


CLAIM_STRENGTH_ORDER = {
    'unsupported': 0,
    'unresolved': 0,
    'hypothesis': 1,
    'speculative': 1,
    'observed': 2,
    'descriptive': 2,
    'bounded': 3,
    'qualified': 3,
    'supported': 4,
    'strong': 5,
    'proven': 6,
    'definitive': 6,
}


def claim_strength_rank(value: Any) -> int | None:
    normalized = normalize_material_key(value)
    if not normalized:
        return None
    for key, rank in CLAIM_STRENGTH_ORDER.items():
        if normalize_material_key(key) == normalized:
            return rank
    return None


def claim_visibility_rows(data: dict[str, Any]) -> list[Any]:
    return data.get('claims') or data.get('rows') or data.get('claim_visibility_rows') or []


def validate_claim_evidence_visibility_map_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ClaimEvidenceVisibilityMap'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        if not has_text(data.get('map_id') or data.get('artifact_id')):
            return False
        rows = claim_visibility_rows(data)
        if not isinstance(rows, list) or not rows:
            return False
        for row in rows:
            if not isinstance(row, dict):
                return False
            if not has_text(row.get('claim_id') or row.get('claim')):
                return False
            if not has_text(row.get('support_location') or row.get('location') or row.get('manuscript_location')):
                return False
            refs = row.get('evidence_refs') or row.get('method_refs') or row.get('evidence_method_refs')
            if not non_empty_list(refs):
                return False
            if not has_text(row.get('allowed_strength') or row.get('allowed_claim_strength')):
                return False
            if not non_empty_list(row.get('forbidden_wording') or row.get('forbidden_wording_patterns')):
                return False
    return True


CLAIM_STRENGTH_UPGRADE_KEYS = {
    'claim_strength_override',
    'upgraded_claim_strength',
    'promotion_status',
    'can_strengthen_claim',
    'can_raise_claim_strength',
    'claim_strength_promotion',
    'strength_upgrade',
}

CLAIM_STRENGTH_UPGRADE_VALUES = {
    'true',
    'promote',
    'promoted',
    'promotion',
    'upgrade',
    'upgraded',
    'raise',
    'raised',
    'stronger',
    'strongerthanevidence',
}


def claim_strength_upgrade_requested(container: Any) -> bool:
    if not isinstance(container, dict):
        return False
    for key in CLAIM_STRENGTH_UPGRADE_KEYS:
        value = container.get(key)
        if value is True:
            return True
        if isinstance(value, str) and normalize_material_key(value) in CLAIM_STRENGTH_UPGRADE_VALUES:
            return True
    truth_boundary = container.get('truth_boundary')
    if isinstance(truth_boundary, dict):
        if truth_boundary.get('can_raise_claim_strength') is True:
            return True
        value = truth_boundary.get('claim_strength_policy') or truth_boundary.get('claim_strength_upgrade')
        if isinstance(value, str) and normalize_material_key(value) in CLAIM_STRENGTH_UPGRADE_VALUES:
            return True
    return False


def validate_claim_evidence_visibility_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ClaimEvidenceVisibilityMap'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        if claim_strength_upgrade_requested(data):
            return False
        for row in claim_visibility_rows(data):
            if not isinstance(row, dict):
                return False
            if claim_strength_upgrade_requested(row):
                return False
            refs = row.get('evidence_refs') or row.get('method_refs') or row.get('evidence_method_refs') or []
            normalized_refs = ' '.join(normalize_material_key(ref) for ref in material_ref_strings(refs))
            if not normalized_refs:
                return False
            if not any(marker in normalized_refs for marker in ['evidence', 'method', 'source', 'result', 'claimcitation', 'resultpackage']):
                return False
            allowed = row.get('allowed_strength') or row.get('allowed_claim_strength')
            evidence = row.get('evidence_strength') or row.get('source_strength') or row.get('support_strength')
            allowed_rank = claim_strength_rank(allowed)
            evidence_rank = claim_strength_rank(evidence)
            if allowed_rank is None or evidence_rank is None:
                return False
            if allowed_rank > evidence_rank:
                return False
            if normalize_material_key(allowed) in CLAIM_STRENGTH_UPGRADE_VALUES:
                return False
    return True


def validate_terminology_register_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['TerminologyRegister'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        entries = data.get('terms') or data.get('entries') or data.get('terminology')
        if not isinstance(entries, list) or not entries:
            return False
        for entry in entries:
            if not isinstance(entry, dict):
                return False
            if not has_text(entry.get('term') or entry.get('raw_term')):
                return False
            if entry.get('main_prose_allowed') is None and entry.get('allowed_in_main_prose') is None:
                return False
            if not has_text(entry.get('reader_facing_term') or entry.get('replacement') or entry.get('surface_term')):
                return False
    return True


def validate_terminology_register_surface_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['TerminologyRegister'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        entries = data.get('terms') or data.get('entries') or data.get('terminology') or []
        for entry in entries:
            if not isinstance(entry, dict):
                return False
            term = str(entry.get('term') or entry.get('raw_term') or '')
            allowed = entry.get('main_prose_allowed')
            if allowed is None:
                allowed = entry.get('allowed_in_main_prose')
            raw_like = any(pattern.search(term) for pattern in INTERNAL_CODE_PATTERNS)
            raw_like = raw_like or bool(re.search(r'[A-Za-z]+_[A-Za-z0-9_]+', term))
            if raw_like and allowed is True:
                return False
            if raw_like and not has_text(entry.get('reader_facing_term') or entry.get('replacement') or entry.get('surface_term')):
                return False
    return True


def validate_claim_citation_capsule_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ClaimCitationCapsule'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        if not has_text(data.get('claim_id')) or not has_text(data.get('claim_text')):
            return False
        locator = data.get('source_locator')
        snippet = data.get('supporting_snippet')
        usable = data.get('usable_sentence')
        if not isinstance(locator, dict) or not (has_text(locator.get('path_or_citekey')) or has_text(locator.get('locator_id'))):
            return False
        if not isinstance(snippet, dict) or not has_text(snippet.get('summary')):
            return False
        if normalize_actor_part(data.get('support_strength')) in {'', 'unresolved'}:
            return False
        if not has_text(data.get('bibtex_key')):
            return False
        if not isinstance(usable, dict) or not has_text(usable.get('allowed_wording')) or not non_empty_list(usable.get('forbidden_wording')):
            return False
    return True


def validate_result_package_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ResultPackage'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        locator = data.get('source_locator')
        if not isinstance(locator, dict) or not has_text(locator.get('path')):
            return False
        for field in ['supported_claim', 'metric_anchor', 'figure_table_anchor', 'reviewer_risk']:
            if not non_empty_dict(data.get(field)):
                return False
        if not non_empty_list(data.get('allowed_wording')) or not non_empty_list(data.get('forbidden_wording')):
            return False
        future = data.get('future_evidence_branch')
        if isinstance(future, dict) and future.get('current_results_section_allowed') is True and normalize_actor_part(data.get('promotion_status')) != 'promoted':
            return False
    return True


def validate_single_writer_lock_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['SingleWriterSectionLock'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        for field in ['lock_id', 'section_or_file', 'owner_lane', 'agent_actor', 'expires_or_release_condition', 'conflict_policy']:
            if not data.get(field):
                return False
        if not isinstance(data.get('agent_actor'), dict) or not has_text(data['agent_actor'].get('actor_lane')):
            return False
        if not non_empty_list(data.get('validator_refs')):
            return False
    return True


def validate_reader_surface_tutor_review_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['ReaderSurfaceTutorReview'], artifacts, tasks)
    if not items:
        return True
    for _, data in items:
        if data is None:
            return False
        for field in ['review_id', 'source_path', 'source_span', 'rendered_span', 'severity', 'violated_rule', 'responsible_department', 'responsible_lane', 'expected_fix_output', 'backflow_route']:
            if not data.get(field):
                return False
        for field in ['source_span', 'rendered_span']:
            span = data.get(field)
            if not isinstance(span, dict) or not has_text(span.get('text')) or span.get('start_line') is None:
                return False
    return True



NATURE_FIGURE_ARCHETYPES = {
    'quantitative_grid', 'schematic_led_composite', 'image_plate_plus_quant',
    'asymmetric_mixed_modality',
}
NATURE_BACKEND_ROUTES = {'tikz_cps_tikz', 'python', 'r', 'extracted_asset', 'manual_review_only'}
NATURE_VECTOR_ROUTES = {'tikz_cps_tikz', 'manual_review_only'}
NATURE_PRIVACY_LEAK_PATTERNS = [
    re.compile(r'/home/[^\s,;)]*'),
    re.compile(r'/users/[^\s,;)]*', re.IGNORECASE),
    re.compile(r'[A-Za-z]:[\\/]+users[\\/][^\s,;)]*', re.IGNORECASE),
    re.compile(r'BEGIN PRIVATE RAW'),
    re.compile(r'private_raw_content\s*:'),
    re.compile(r'raw_unpublished_manuscript\s*:'),
    re.compile(r'API_KEY\s*='),
    re.compile(r'SECRET\s*='),
]
NATURE_REQUIRED_EXPRESSION_MARKERS = {
    'CognitiveLoadBudget': {'cognitiveloadbudget', 'cognitiveload', 'cognitive-load-budget'},
    'ExplanationLadder': {'explanationladder', 'explanation-ladder'},
    'RhetoricalMoveMatrix': {'rhetoricalmovematrix', 'rhetorical-move-matrix'},
    'ClaimEvidenceVisibilityMap': {'claimevidencevisibilitymap', 'claim-evidence-visibility-map', 'claimevidencevisibility'},
    'TerminologyRegister': {'terminologyregister', 'terminology-register'},
}


def raw_task_validator_refs(tasks: Any) -> set[str]:
    refs: set[str] = set()
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        values = task.get('validator_refs')
        if values is None:
            values = task.get('validators')
        for ref in values or []:
            if isinstance(ref, str):
                refs.add(ref)
    return refs


def material_validator_required(tasks: Any, validator: str) -> bool:
    return validator in raw_task_validator_refs(tasks)


def nature_material_items(
    fixture: Path,
    key: str,
    artifacts: dict[str, Any] | None,
    tasks: Any,
) -> list[tuple[str, dict[str, Any] | None]]:
    return material_data_items(fixture, MATERIAL_OBJECT_SPECS[key], artifacts, tasks)


def nature_items_or_required(
    fixture: Path,
    key: str,
    validator: str,
    artifacts: dict[str, Any] | None,
    tasks: Any,
) -> tuple[list[tuple[str, dict[str, Any] | None]], bool]:
    items = nature_material_items(fixture, key, artifacts, tasks)
    return items, bool(items) or material_validator_required(tasks, validator)


def figure_archetype_ok(value: Any) -> bool:
    return normalize_material_key(value) in {normalize_material_key(v) for v in NATURE_FIGURE_ARCHETYPES}


def nature_expression_refs_complete(refs: Any) -> bool:
    normalized = {normalize_material_key(ref) for ref in material_ref_strings(refs)}
    if not normalized:
        return False
    for markers in NATURE_REQUIRED_EXPRESSION_MARKERS.values():
        marker_norms = {normalize_material_key(marker) for marker in markers}
        if not any(marker in ref or ref in marker for ref in normalized for marker in marker_norms):
            return False
    return True


def nature_no_private_leak(value: Any) -> bool:
    text = yaml.safe_dump(value, allow_unicode=True) if not isinstance(value, str) else value
    return not any(pattern.search(text) for pattern in NATURE_PRIVACY_LEAK_PATTERNS)


def nature_ref_resolves_material_type(
    ref: Any,
    fixture: Path,
    artifacts: dict[str, Any] | None,
    tasks: Any,
    spec_key: str,
) -> bool:
    if not has_text(ref):
        return False
    spec = MATERIAL_OBJECT_SPECS[spec_key]
    ref_id = str(ref)
    ref_path = ref_id.rstrip('/')
    if nature_material_data_for_ref(ref, fixture, artifacts, tasks, spec_key) is not None:
        return True
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        for field in ['input_materials', 'expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
            for item in task.get(field) or []:
                if not isinstance(item, dict) or not material_spec_matches_entry(spec, item):
                    continue
                item_id = item.get('artifact_id') or item.get('object_id')
                item_path = str(item.get('path') or '').rstrip('/')
                if ref_id == item_id or ref_path == item_path or ref_id == Path(item_path).stem:
                    return True
    for art in (artifacts or {}).get('artifacts') or []:
        if not isinstance(art, dict):
            continue
        if not material_spec_matches_entry(spec, art):
            continue
        art_id = art.get('artifact_id') or art.get('object_id')
        art_path = str(art.get('path') or '').rstrip('/')
        if ref_id == art_id or ref_path == art_path or ref_id == Path(art_path).stem:
            return True
    for candidate in nature_ref_candidate_paths(ref_id):
        path = fixture / candidate
        if not path.exists() or not path.is_file():
            continue
        data = load_yaml(path, {})
        if isinstance(data, dict) and material_spec_for_data(data) == spec:
            return True
    return False


def nature_ref_candidate_paths(ref_id: str) -> set[str]:
    return {
        ref_id,
        ref_id.rstrip('/'),
        f'{ref_id}.yaml',
        f'nature/{ref_id}.yaml',
        f'figures/{ref_id}.yaml',
        f'narrative/{ref_id}.yaml',
    }


def nature_material_data_for_ref(
    ref: Any,
    fixture: Path,
    artifacts: dict[str, Any] | None,
    tasks: Any,
    spec_key: str,
) -> dict[str, Any] | None:
    if not has_text(ref):
        return None
    spec = MATERIAL_OBJECT_SPECS[spec_key]
    ref_id = str(ref)
    ref_path = ref_id.rstrip('/')

    def entry_matches(entry: dict[str, Any]) -> str | None:
        if not material_spec_matches_entry(spec, entry):
            return None
        entry_id = entry.get('artifact_id') or entry.get('object_id')
        entry_path = str(entry.get('path') or '').rstrip('/')
        if ref_id == entry_id or ref_path == entry_path or ref_id == Path(entry_path).stem:
            return entry_path
        return None

    candidate_paths = list(nature_ref_candidate_paths(ref_id))
    for art in (artifacts or {}).get('artifacts') or []:
        if isinstance(art, dict):
            path = entry_matches(art)
            if path:
                candidate_paths.insert(0, path)
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        for field in ['input_materials', 'expected_output_materials', 'expected_output_artifacts', 'collected_outputs']:
            for item in task.get(field) or []:
                if isinstance(item, dict):
                    path = entry_matches(item)
                    if path:
                        candidate_paths.insert(0, path)
    seen: set[str] = set()
    for rel in candidate_paths:
        if not rel or rel in seen:
            continue
        seen.add(rel)
        path = fixture / rel
        if not path.exists() or not path.is_file():
            continue
        data = load_yaml(path, {})
        if isinstance(data, dict) and material_spec_for_data(data) == spec:
            return data
    return None


def validate_nature_figure_contract_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'NatureFigureContract', 'validate_nature_figure_contract', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        for field in ['artifact_id', 'figure_id', 'core_conclusion', 'reader_question', 'figure_archetype']:
            if not has_text(data.get(field)):
                return False
        if not figure_archetype_ok(data.get('figure_archetype')):
            return False
        hierarchy = data.get('panel_hierarchy') or {}
        if not isinstance(hierarchy, dict) or not has_text(hierarchy.get('hero_panel_id')):
            if normalize_material_key(data.get('figure_archetype')) != 'quantitativegrid':
                return False
        panels = data.get('panel_map') or []
        if not isinstance(panels, list) or not panels:
            return False
        for panel in panels:
            if not isinstance(panel, dict):
                return False
            for field in ['panel_id', 'reader_question', 'evidence_role']:
                if not has_text(panel.get(field)):
                    return False
            if not non_empty_list(panel.get('supports_claim_ids')) or not non_empty_list(panel.get('evidence_refs')):
                return False
        if not non_empty_list(data.get('narrative_object_refs')) or not non_empty_list(data.get('template_object_refs')):
            return False
        if not nature_expression_refs_complete(data.get('expression_design_object_refs')):
            return False
        if not non_empty_list(data.get('evidence_refs')):
            return False
    return True


def validate_nature_figure_aesthetic_profile_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'NatureFigureAestheticProfile', 'validate_nature_figure_aesthetic_profile', artifacts, tasks)
    if not items:
        return not required
    allowed_legends = {'directlabel', 'sharedlegend', 'legendpanel', 'nonewithcaptionmapping'}
    for _, data in items:
        if data is None:
            return False
        composition = data.get('composition') or {}
        if not isinstance(composition, dict) or not figure_archetype_ok(composition.get('figure_archetype')):
            return False
        if normalize_actor_part(composition.get('dashboard_equal_panel_bias_check')) not in {'pass', 'passed', 'clean'}:
            return False
        archetype = normalize_material_key(composition.get('figure_archetype'))
        exception = composition.get('hero_panel_exception') or {}
        if archetype != 'quantitativegrid' and not has_text(composition.get('hero_panel_id')):
            return False
        if archetype == 'quantitativegrid' and not has_text(composition.get('hero_panel_id')) and exception.get('accepted') is not True:
            return False
        if not isinstance(composition.get('panel_hierarchy'), dict):
            return False
        palette = data.get('palette') or {}
        roles = palette.get('semantic_roles') if isinstance(palette, dict) else None
        if not isinstance(roles, dict) or not roles.get('neutral') or not roles.get('signal'):
            return False
        typography = data.get('typography') or {}
        if not isinstance(typography, dict) or typography.get('editable_text_required') is not True or not has_text(typography.get('font_family_policy')):
            return False
        labels = data.get('panel_label_policy') or {}
        if not isinstance(labels, dict) or labels.get('lowercase_bold') is not True or labels.get('decorative_badges') is not False:
            return False
        if normalize_material_key(data.get('legend_strategy')) not in allowed_legends:
            return False
        background = data.get('background_policy') or {}
        if not isinstance(background, dict) or normalize_material_key(background.get('plot_background')) != 'white':
            return False
        if not nature_expression_refs_complete(data.get('expression_design_object_refs')):
            return False
    return True


def validate_panel_evidence_map_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'NaturePanelEvidenceMap', 'validate_panel_evidence_map', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        panels = data.get('panels') or []
        if not isinstance(panels, list) or not panels:
            return False
        questions: set[str] = set()
        for panel in panels:
            if not isinstance(panel, dict):
                return False
            for field in ['panel_id', 'reader_question', 'evidence_role']:
                if not has_text(panel.get(field)):
                    return False
            q = normalize_material_key(panel.get('reader_question'))
            if not q or q in questions:
                return False
            questions.add(q)
            if not non_empty_list(panel.get('supports_claim_ids')) or not non_empty_list(panel.get('evidence_refs')):
                return False
            if not nature_ref_resolves_material_type(
                panel.get('statistics_ref'),
                fixture,
                artifacts,
                tasks,
                'FigureSourceDataStatistics',
            ):
                return False
            if not nature_ref_resolves_material_type(
                panel.get('image_integrity_ref'),
                fixture,
                artifacts,
                tasks,
                'FigureImageIntegrityRecord',
            ):
                return False
            if panel.get('unique_evidence_role') is not True:
                return False
    return True


def validate_figure_backend_route_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'FigureBackendRoute', 'validate_figure_backend_route', artifacts, tasks)
    if not items:
        return not required
    allowed = {normalize_material_key(route) for route in NATURE_BACKEND_ROUTES}
    for _, data in items:
        if data is None:
            return False
        route = normalize_material_key(data.get('selected_route'))
        if route not in allowed:
            return False
        if data.get('route_exclusivity_required') is not True:
            return False
        if data.get('cross_backend_rendering_allowed') is not False:
            return False
        source = data.get('final_source_of_truth') or {}
        if not isinstance(source, dict) or not has_text(source.get('type')) or not has_text(source.get('path')):
            return False
        if not has_text(data.get('missing_runtime_policy')):
            return False
        if route in {'python', 'r'} and normalize_material_key(data.get('missing_runtime_policy')) != 'stopbeforerendering':
            return False
        if route == normalize_material_key('tikz_cps_tikz') and 'raster' in normalize_material_key(source.get('type')):
            return False
    return True


def validate_figure_source_data_statistics_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'FigureSourceDataStatistics', 'validate_figure_source_data_statistics', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if not nature_ref_resolves_material_type(data.get('backend_route_ref'), fixture, artifacts, tasks, 'FigureBackendRoute'):
            return False
        conceptual = data.get('conceptual') is True
        if conceptual:
            if not has_text(data.get('no_data_rationale')) or not has_text(data.get('backend_route_ref')):
                return False
            continue
        if not non_empty_list(data.get('source_data_refs')):
            return False
        stats = data.get('statistics') or {}
        if not isinstance(stats, dict):
            return False
        for field in ['n', 'error_definition', 'statistical_test']:
            if not has_text(stats.get(field)):
                return False
        legend = data.get('legend_statistics_block') or {}
        if not isinstance(legend, dict) or legend.get('required') is not True or not has_text(legend.get('text')):
            return False
    return True


def validate_figure_image_integrity_record_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'FigureImageIntegrityRecord', 'validate_figure_image_integrity_record', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        backend_route = nature_material_data_for_ref(data.get('backend_route_ref'), fixture, artifacts, tasks, 'FigureBackendRoute')
        if backend_route is None:
            return False
        applicability = data.get('image_integrity_applicability') or {}
        if not isinstance(applicability, dict) or not has_text(applicability.get('status')):
            return False
        status = normalize_material_key(applicability.get('status'))
        if status in {'notapplicable', 'na'}:
            if not has_text(applicability.get('rationale')):
                return False
            route_value = backend_route.get('selected_route')
            route_text = normalize_material_key(route_value)
            if data.get('raster_or_image_panel') is True:
                return False
            if route_text and not any(marker in route_text for marker in ['tikz', 'manualreview']):
                return False
            continue
        if status not in {'applicable', 'required'}:
            return False
        if not (has_text(data.get('raw_locator')) or non_empty_dict(data.get('raw_locator'))):
            return False
        if not (has_text(data.get('processed_locator')) or non_empty_dict(data.get('processed_locator'))):
            return False
        if not non_empty_list(data.get('processing_steps')):
            return False
    return True


def validate_nature_caption_legend_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'NatureCaptionLegendBrief', 'validate_nature_caption_legend', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None or not nature_no_private_leak(data):
            return False
        title = str(data.get('caption_title') or '')
        if not title.startswith('Fig.') and not title.startswith('Figure'):
            return False
        panels = data.get('panel_descriptions') or []
        if not isinstance(panels, list) or not panels:
            return False
        for panel in panels:
            if not isinstance(panel, dict) or not has_text(panel.get('panel_id')) or not has_text(panel.get('text')):
                return False
            if normalize_material_key(panel.get('tense') or 'present') != 'present':
                return False
        for field in ['statistics_statement', 'source_data_statement']:
            statement = data.get(field) or {}
            if not isinstance(statement, dict) or statement.get('required') is None or not has_text(statement.get('text')):
                return False
        privacy = data.get('privacy_surface') or {}
        if isinstance(privacy, dict):
            if normalize_actor_part(privacy.get('private_path_leak_status')) in {'fail', 'failed', 'present'}:
                return False
            if normalize_actor_part(privacy.get('raw_locator_leak_status')) in {'fail', 'failed', 'present'}:
                return False
    return True


def validate_nature_figure_qa_report_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'NatureFigureQAReport', 'validate_nature_figure_qa_report', artifacts, tasks)
    if not items:
        return not required
    required_checks = {
        'visual_qa', 'aesthetic_qa', 'evidence_qa', 'caption_qa',
        'image_integrity_qa', 'export_qa', 'rendered_surface_qa',
    }
    for _, data in items:
        if data is None:
            return False
        checks = data.get('checks') or {}
        if not isinstance(checks, dict) or not required_checks.issubset(set(checks)):
            return False
        if any(normalize_actor_part(checks.get(check)) not in {'pass', 'passed', 'clean', 'notapplicable'} for check in required_checks):
            return False
        if normalize_actor_part(data.get('verdict')) not in {'pass', 'passed', 'clean', 'approve', 'approved'}:
            return False
        if not isinstance(data.get('backflow_route'), dict):
            return False
    return True


def validate_figure_export_bundle_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = nature_items_or_required(fixture, 'FigureExportBundle', 'validate_figure_export_bundle', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if not non_empty_list(data.get('source_artifacts')):
            return False
        outputs = data.get('outputs') or []
        if not isinstance(outputs, list) or not outputs:
            return False
        formats = {normalize_material_key(out.get('format')) for out in outputs if isinstance(out, dict)}
        if 'svg' not in formats or 'pdf' not in formats:
            return False
        if not any(fmt in formats for fmt in {'tiff', 'tif', 'pngpreview', 'png'}):
            return False
        for out in outputs:
            if not isinstance(out, dict) or not has_text(out.get('path')) or not has_text(out.get('format')):
                return False
            if normalize_material_key(out.get('format')) in {'svg', 'pdf'} and out.get('editable_text') is not True:
                return False
        if normalize_actor_part(data.get('editable_text_status')) not in {'pass', 'passed', 'clean'}:
            return False
        dims = data.get('final_dimensions') or {}
        if not isinstance(dims, dict) or not has_text(dims.get('target_width')) or normalize_actor_part(dims.get('legibility_status')) not in {'pass', 'passed', 'clean'}:
            return False
        if not non_empty_list(data.get('manifest_refs')):
            return False
        provenance = data.get('hash_provenance') or {}
        if not isinstance(provenance, dict) or normalize_actor_part(provenance.get('status')) not in {'recorded', 'pass', 'passed', 'clean'}:
            return False
    return True


NATURE_ABSORBED_SKILLS = {
    'nature-writing', 'nature-polishing', 'nature-reader', 'nature-academic-search',
    'nature-citation', 'nature-data', 'nature-reviewer', 'nature-response',
    'nature-paper2ppt', 'nature-paper-to-patent',
}
NATURE_SEARCH_WORKFLOWS = {
    'multi-source-search', 'citation-verification', 'mesh-strategy',
    'citation-file-mgmt', 'reference-mgmt',
}
NATURE_READER_FORMATS = {'pdf-text', 'scanned-pdf', 'html', 'doi-arxiv', 'pasted-text'}
NATURE_WRITING_PAPER_TYPES = {'research', 'methods', 'hypothesis', 'algorithmic', 'review'}
NATURE_WRITING_SECTIONS = {'abstract', 'intro', 'introduction', 'related-work', 'method', 'methods', 'experiments', 'results', 'discussion', 'conclusion', 'title'}
NATURE_WRITING_LANGUAGES = {'en', 'zh-to-en'}
NATURE_JOURNALS = {'nature', 'nat-comms', 'generic', 'kbs', 'eswa'}
NATURE_REQUIRED_CAPABILITY_KEYS = {'reader', 'search', 'citation', 'writing', 'journal_style', 'polishing', 'data', 'reviewer', 'response', 'presentation', 'patent'}


def absorption_items_or_required(
    fixture: Path,
    key: str,
    validator: str,
    artifacts: dict[str, Any] | None,
    tasks: Any,
) -> tuple[list[tuple[str, dict[str, Any] | None]], bool]:
    return nature_items_or_required(fixture, key, validator, artifacts, tasks)


def validate_nature_source_inventory_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'NatureSourceInventory', 'validate_nature_source_inventory', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        repo = data.get('source_repo') or {}
        if not isinstance(repo, dict) or not has_text(repo.get('name')) or not has_text(repo.get('url')):
            return False
        commit = str(repo.get('commit_hash') or '')
        if not re.fullmatch(r'[0-9a-f]{40}', commit):
            return False
        if not non_empty_list(data.get('source_files_required')):
            return False
        seen: set[str] = set()
        for cap in data.get('capabilities') or []:
            if not isinstance(cap, dict):
                return False
            skill = str(cap.get('skill_name') or '')
            if skill not in NATURE_ABSORBED_SKILLS:
                return False
            seen.add(skill)
            if not non_empty_list(cap.get('source_files')) or not has_text(cap.get('absorbed_as')):
                return False
        if not NATURE_ABSORBED_SKILLS.issubset(seen):
            return False
    return True


def validate_company_skill_registry_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'CompanySkillRegistry', 'validate_company_skill_registry', artifacts, tasks)
    if not items:
        return not required
    required_caps = {f'{skill}-absorption' for skill in NATURE_ABSORBED_SKILLS}
    required_produces = {
        'PaperReaderPackage', 'SearchStrategyDossier', 'CitationVerificationReport',
        'SectionMovePlan', 'JournalStyleProfile', 'PolishingRepairReport',
        'DataAvailabilityPlan', 'ReviewerPanelReport', 'ResponseActionMap',
        'PresentationPlan', 'PatentDraftBoundary',
    }
    for _, data in items:
        if data is None:
            return False
        if data.get('public_surface_allowed') is not False:
            return False
        if str(data.get('single_public_entry') or '') != 'yxj-paper-os':
            return False
        seen: set[str] = set()
        produced: set[str] = set()
        for cap in data.get('capabilities') or []:
            if not isinstance(cap, dict):
                return False
            cap_id = str(cap.get('capability_id') or '')
            if cap_id.startswith('nature-'):
                seen.add(cap_id)
            if cap.get('public_surface_allowed') is not False or cap.get('hidden_manager') is not False:
                return False
            if 'yxj-paper-os' not in [str(c) for c in cap.get('allowed_callers') or []]:
                return False
            if not has_text(cap.get('owner_department')) or not has_text(cap.get('owner_lane')):
                return False
            if not non_empty_list(cap.get('produces')) or not non_empty_list(cap.get('validator_refs')):
                return False
            produced.update(str(item) for item in cap.get('produces') or [] if has_text(item))
            limits = {normalize_material_key(x) for x in cap.get('authority_limits') or []}
            if cap_id.startswith('nature-') and not limits:
                # Every absorbed Nature capability must carry at least one explicit authority limit.
                return False
        if not required_caps.issubset(seen):
            return False
        if not required_produces.issubset(produced):
            return False
    return True


def validate_paper_reader_package_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'PaperReaderPackage', 'validate_paper_reader_package', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if str(data.get('source_format') or '') not in NATURE_READER_FORMATS:
            return False
        if data.get('exact_source_anchors_required') is not True or data.get('summary_only') is not False:
            return False
        blocks = data.get('source_blocks') or []
        if not isinstance(blocks, list) or not blocks:
            return False
        for block in blocks:
            if not isinstance(block, dict) or not has_text(block.get('source_id')) or not has_text(block.get('anchor')):
                return False
            if normalize_actor_part(block.get('grounding_status')) not in {'grounded', 'pass', 'passed'}:
                return False
        if not isinstance(data.get('figure_table_map'), list):
            return False
    return True


def validate_search_strategy_dossier_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'SearchStrategyDossier', 'validate_search_strategy_dossier', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if str(data.get('workflow') or '') not in NATURE_SEARCH_WORKFLOWS:
            return False
        if not non_empty_list(data.get('queries')) or not isinstance(data.get('source_tiers'), dict):
            return False
        for q in data.get('queries') or []:
            if not isinstance(q, dict) or not has_text(q.get('query')) or not non_empty_list(q.get('source_targets')):
                return False
        dedup = data.get('deduplication') or {}
        if not isinstance(dedup, dict) or not has_text(dedup.get('status')):
            return False
        if not isinstance(data.get('failure_log'), list):
            return False
    return True


def validate_citation_verification_report_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'CitationVerificationReport', 'validate_citation_verification_report', artifacts, tasks)
    if not items:
        return not required
    allowed = {'direct', 'partial', 'background', 'contradictory', 'unsupported'}
    for _, data in items:
        if data is None:
            return False
        segments = data.get('segments') or []
        if not isinstance(segments, list) or not segments:
            return False
        for seg in segments:
            if not isinstance(seg, dict) or not has_text(seg.get('segment_id')) or not has_text(seg.get('claim_text')):
                return False
            if str(seg.get('support_grade') or '') not in allowed:
                return False
            if seg.get('metadata_only') is True or seg.get('checked_abstract_or_publisher') is not True:
                return False
            if not non_empty_list(seg.get('source_refs')):
                return False
        export = data.get('export_route') or {}
        if not isinstance(export, dict) or normalize_actor_part(export.get('reference_manager_ready')) not in {'true', 'pass', 'passed'}:
            return False
        if normalize_material_key(export.get('format')) not in {'ris', 'enw', 'zoterordf', 'bibtex'}:
            return False
    return True


def validate_section_move_plan_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'SectionMovePlan', 'validate_section_move_plan', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if str(data.get('paper_type') or '') not in NATURE_WRITING_PAPER_TYPES:
            return False
        if str(data.get('section') or '') not in NATURE_WRITING_SECTIONS:
            return False
        if str(data.get('language') or '') not in NATURE_WRITING_LANGUAGES:
            return False
        if str(data.get('journal') or '') not in NATURE_JOURNALS:
            return False
        if not non_empty_list(data.get('narrative_object_refs')) or not non_empty_list(data.get('evidence_refs')):
            return False
        if not non_empty_list(data.get('move_sequence')):
            return False
    return True


def validate_journal_style_profile_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'JournalStyleProfile', 'validate_journal_style_profile', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if str(data.get('journal') or '') not in NATURE_JOURNALS:
            return False
        if not non_empty_list(data.get('source_basis')) or not isinstance(data.get('style_axes'), dict):
            return False
        if not non_empty_list(data.get('diction_rules')) or not isinstance(data.get('forbidden_patterns'), list):
            return False
    return True


def validate_polishing_repair_report_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'PolishingRepairReport', 'validate_polishing_repair_report', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if not non_empty_list(data.get('failure_modes')) or not non_empty_list(data.get('repairs')):
            return False
        for repair in data.get('repairs') or []:
            if not isinstance(repair, dict) or not has_text(repair.get('repair_action')):
                return False
            change = repair.get('claim_strength_change') or {}
            if isinstance(change, dict) and change.get('allowed') is True and not has_text(change.get('evidence_approval_ref')):
                return False
        if normalize_actor_part((data.get('phrasebank_application') or {}).get('status')) not in {'applied', 'pass', 'checked'}:
            return False
        if normalize_actor_part((data.get('chinese_author_alignment') or {}).get('status')) not in {'checked', 'pass', 'notapplicable'}:
            return False
    return True


def identifier_confirmed_or_sourced(container: Any) -> bool:
    if not isinstance(container, dict):
        return False
    status = normalize_actor_part(container.get('confirmation_status'))
    return status == 'confirmed' or has_text(container.get('source_locator'))


def validate_data_availability_plan_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'DataAvailabilityPlan', 'validate_data_availability_plan', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        datasets = data.get('datasets') or []
        if not isinstance(datasets, list) or not datasets:
            return False
        for ds in datasets:
            if not isinstance(ds, dict) or not has_text(ds.get('dataset_id')) or not has_text(ds.get('access_route')):
                return False
            repo = ds.get('repository_route') or {}
            if not isinstance(repo, dict) or not has_text(repo.get('name')):
                return False
            ids = ds.get('identifiers') or {}
            for field in ['doi', 'accession']:
                if isinstance(ids, dict) and has_text(ids.get(field)) and not identifier_confirmed_or_sourced(ids):
                    return False
            lic = ds.get('license')
            if isinstance(lic, dict) and has_text(lic.get('value')) and not identifier_confirmed_or_sourced(lic):
                return False
        fair = data.get('fair_metadata_checklist') or {}
        if not isinstance(fair, dict) or normalize_actor_part(fair.get('status')) not in {'pass', 'passed', 'checked'}:
            return False
        if not has_text(data.get('statement_draft')):
            return False
    return True


def validate_reviewer_panel_report_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'ReviewerPanelReport', 'validate_reviewer_panel_report', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        reports = data.get('reviewer_reports') or []
        if not isinstance(reports, list) or len(reports) != 3:
            return False
        for rep in reports:
            if not isinstance(rep, dict) or not has_text(rep.get('reviewer_id')) or not has_text(rep.get('emphasis')):
                return False
            if rep.get('invented_identity') is True:
                return False
            if not non_empty_list(rep.get('major_concerns')):
                return False
        if not isinstance(data.get('cross_review_synthesis'), dict) or not non_empty_list(data.get('technical_failing_map')):
            return False
        if data.get('editorial_decision_claimed') is True:
            return False
    return True


def validate_response_action_map_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'ResponseActionMap', 'validate_response_action_map', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if data.get('invented_line_numbers_present') is True:
            return False
        comments = data.get('comments') or []
        if not isinstance(comments, list) or not comments:
            return False
        for comment in comments:
            if not isinstance(comment, dict) or not has_text(comment.get('comment_id')) or not has_text(comment.get('source')):
                return False
            if not has_text(comment.get('action')) or not has_text(comment.get('owner_lane')) or not has_text(comment.get('response_text')):
                return False
            for ref in comment.get('line_refs') or []:
                if isinstance(ref, dict) and normalize_actor_part(ref.get('confirmation_status')) in {'invented', 'unconfirmed', 'guessed'}:
                    return False
        draft = data.get('point_by_point_draft') or {}
        if not isinstance(draft, dict) or draft.get('preserve_comment_ids') is not True:
            return False
        if normalize_actor_part((data.get('tone_qa') or {}).get('status')) not in {'pass', 'passed', 'checked'}:
            return False
    return True


def validate_presentation_plan_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'PresentationPlan', 'validate_presentation_plan', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if str(data.get('canonical_department_id') or data.get('owning_department') or '') != 'manuscript_and_figure_production':
            return False
        if str(data.get('owner_lane') or '') == 'export-owner':
            return False
        if not non_empty_list(data.get('narrative_object_refs')) or not nature_expression_refs_complete(data.get('expression_design_object_refs')):
            return False
        if not (non_empty_list(data.get('figure_refs')) or non_empty_list(data.get('evidence_refs'))):
            return False
        slides = data.get('slides') or []
        if not isinstance(slides, list) or not slides:
            return False
        for slide in slides:
            if not isinstance(slide, dict) or not has_text(slide.get('slide_id')) or not has_text(slide.get('speaker_notes')):
                return False
        if normalize_actor_part((data.get('self_review') or {}).get('status')) not in {'pass', 'passed', 'checked'}:
            return False
    return True


def validate_patent_draft_boundary_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'PatentDraftBoundary', 'validate_patent_draft_boundary', artifacts, tasks)
    if not items:
        return not required
    for _, data in items:
        if data is None:
            return False
        if not non_empty_list(data.get('source_ids')) or not non_empty_list(data.get('source_support_map')):
            return False
        for support in data.get('source_support_map') or []:
            if not isinstance(support, dict) or not has_text(support.get('feature_id')) or not non_empty_list(support.get('source_ids')):
                return False
            if str(support.get('support_state') or '') not in {'explicit', 'inherent', 'needs-confirmation'}:
                return False
        for field in ['drafting_aid_only', 'not_legal_opinion', 'no_patentability_guarantee']:
            if data.get(field) is not True:
                return False
        gate = data.get('professional_review_gate') or {}
        if not isinstance(gate, dict) or gate.get('required') is not True:
            return False
        if data.get('formal_filing_authorized') is not False:
            return False
    return True


def validate_nature_absorption_package_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> bool:
    items, required = absorption_items_or_required(fixture, 'NatureAbsorptionPackage', 'validate_nature_absorption_package', artifacts, tasks)
    if not items:
        return not required
    ref_specs = {
        'source_inventory_ref': 'NatureSourceInventory',
        'company_skill_registry_ref': 'CompanySkillRegistry',
    }
    cap_specs = {
        'reader': 'PaperReaderPackage',
        'search': 'SearchStrategyDossier',
        'citation': 'CitationVerificationReport',
        'writing': 'SectionMovePlan',
        'journal_style': 'JournalStyleProfile',
        'polishing': 'PolishingRepairReport',
        'data': 'DataAvailabilityPlan',
        'reviewer': 'ReviewerPanelReport',
        'response': 'ResponseActionMap',
        'presentation': 'PresentationPlan',
        'patent': 'PatentDraftBoundary',
    }
    for _, data in items:
        if data is None:
            return False
        for field, spec in ref_specs.items():
            if not nature_ref_resolves_material_type(data.get(field), fixture, artifacts, tasks, spec):
                return False
        refs = data.get('capability_material_refs') or {}
        if not isinstance(refs, dict) or not NATURE_REQUIRED_CAPABILITY_KEYS.issubset(set(refs)):
            return False
        for key, spec in cap_specs.items():
            if not nature_ref_resolves_material_type(refs.get(key), fixture, artifacts, tasks, spec):
                return False
        routes = data.get('department_backflow_routes') or {}
        allowed_departments = {'pmo', 'paper_architecture_and_narrative', 'evidence_and_method', 'manuscript_and_figure_production', 'review_and_governance'}
        if not isinstance(routes, dict) or not NATURE_REQUIRED_CAPABILITY_KEYS.issubset(set(routes)):
            return False
        if any(str(route) not in allowed_departments for route in routes.values()):
            return False
        if str(data.get('closure_invariant') or '') != 'compile -> execute -> collect -> validate -> ingest -> state_transition':
            return False
    return True

SOURCE_ONLY_RENDERED_METHODS = {'sourceonly', 'sourcemarkdown', 'markdownsource', 'source', 'markdown'}


def validate_rendered_surface_gate_material(
    fixture: Path,
    artifacts: dict[str, Any] | None = None,
    tasks: Any = None,
) -> tuple[bool, bool, bool]:
    items = material_data_items(fixture, MATERIAL_OBJECT_SPECS['RenderedSurfaceGateReport'], artifacts, tasks)
    if not items:
        return True, True, True
    all_rendered_text_ok = True
    all_internal_ok = True
    all_citekeys_ok = True
    for _, data in items:
        if data is None:
            return False, False, False
        for field in ['artifact_path', 'rendered_text_locator', 'checks', 'violations', 'verdict']:
            if data.get(field) is None:
                return False, False, False
        locator = data.get('rendered_text_locator')
        if not isinstance(locator, dict):
            return False, False, False
        text = str(data.get('rendered_text_sample') or data.get('rendered_text') or '')
        extraction_method = normalize_material_key(locator.get('extraction_method'))
        locator_text_path = locator.get('text_path') or locator.get('extracted_text_path') or data.get('rendered_text_path')
        rendered_text_ok = bool(text.strip())
        rendered_text_ok = rendered_text_ok and bool(data.get('artifact_path'))
        rendered_text_ok = rendered_text_ok and bool(extraction_method)
        rendered_text_ok = rendered_text_ok and data.get('source_only_validation_allowed') is not True
        rendered_text_ok = rendered_text_ok and extraction_method not in SOURCE_ONLY_RENDERED_METHODS
        if 'sourceonly' in extraction_method or (extraction_method.startswith('source') and 'pdf' not in extraction_method):
            rendered_text_ok = False
        rendered_text_ok = rendered_text_ok and (has_text(locator_text_path) or bool(text.strip()))
        no_internal_codes = rendered_text_ok and not any(pattern.search(text) for pattern in INTERNAL_CODE_PATTERNS)
        no_bare_citekeys = rendered_text_ok and not re.search(r'(?<!\w)@[A-Za-z][A-Za-z0-9:_-]+', text)
        statuses = [
            normalize_actor_part(data.get('internal_code_status')),
            normalize_actor_part(data.get('snake_case_status')),
            normalize_actor_part(data.get('raw_method_id_status')),
        ]
        if any(status in {'fail', 'failed', 'present', 'dirty'} for status in statuses):
            no_internal_codes = False
        if normalize_actor_part(data.get('bare_citekey_status')) in {'fail', 'failed', 'present', 'dirty'}:
            no_bare_citekeys = False
        if normalize_actor_part(data.get('verdict')) not in {'pass', 'passed', 'clean', 'approve', 'approved'}:
            no_internal_codes = False
            no_bare_citekeys = False
        all_rendered_text_ok = all_rendered_text_ok and bool(rendered_text_ok)
        all_internal_ok = all_internal_ok and bool(no_internal_codes)
        all_citekeys_ok = all_citekeys_ok and bool(no_bare_citekeys)
    return all_rendered_text_ok, all_internal_ok, all_citekeys_ok


def check_fixture(fixture: Path, root: Path | None = None) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    detail: dict[str, Any] = {'fixture': str(fixture)}
    root = root or infer_root_from_fixture(fixture)
    registry_lanes = lane_registry_by_id(root)
    state = load_yaml(fixture / 'state.yaml', {})
    ledger = load_yaml(fixture / 'task-ledger.yaml', {})
    artifacts = load_yaml(fixture / 'artifact-ledger.yaml', {})
    report = load_yaml(fixture / 'validator-report.yaml', {})
    source_map = load_yaml(fixture / 'source-map.yaml')
    motivation = load_yaml(fixture / 'motivation.yaml', {})
    rationale = load_yaml(fixture / 'rationale-matrix.yaml', {})
    evidence_bank = load_yaml(fixture / 'evidence-bank.yaml', {})
    review = load_yaml(fixture / 'review-output.yaml', {})
    export = load_yaml(fixture / 'export-manifest.yaml', {})

    if not state or 'current_phase' not in state:
        failures.append('validate_state_machine')
    if not isinstance(report, dict) or not report.get('validators_run'):
        failures.append('validate_validator_report')

    # Privacy leak scan.
    raw_text = ''
    for p in fixture.rglob('*'):
        if p.is_file() and p.suffix in {'.yaml', '.yml', '.md', '.txt'}:
            raw_text += p.read_text(encoding='utf-8', errors='ignore') + '\n'
    leak_markers = ['BEGIN PRIVATE RAW', 'private_raw_content:', 'raw_unpublished_manuscript:', 'API_KEY=', 'SECRET=']
    if any(marker in raw_text for marker in leak_markers):
        failures.append('validate_privacy_boundaries')

    if not source_map or not source_map.get('sources'):
        failures.extend(['validate_source_map', 'validate_research_triplet_collection'])
    else:
        for src in source_map.get('sources') or []:
            if src.get('locator_status') != 'resolved':
                failures.append('validate_source_locator_resolution')
            if src.get('privacy') in {'private_raw', 'raw_private'}:
                failures.append('validate_privacy_boundaries')

    tasks = ledger.get('tasks') or []
    if not tasks:
        failures.append('validate_task_packet')
    for task in tasks:
        for field in ['task_id', 'route', 'adapter', 'owner_lane', 'agent_type', 'scoped_context', 'expected_output_artifacts', 'collection_path', 'state_ledger_path']:
            if not task.get(field):
                failures.append('validate_task_packet')
        if task.get('adapter') != 'native_subagent_pipeline_adapter':
            failures.append('validate_direct_execution_adapter')
        if task.get('owner_lane') not in allowed_owner_lanes(root):
            failures.append('validate_owner_lane_closure')
        refs = normalize_validator_refs(task, failures)
        if not refs:
            failures.append('validate_task_packet')
        if 'validate_pua_telemetry' not in refs or not validate_pua_telemetry(task):
            failures.append('validate_pua_telemetry')
        lane = registry_lanes.get(str(task.get('owner_lane')))
        is_v2 = task_is_v2(task, refs)
        if is_v2:
            required_v2_refs = {'validate_agent_lane_department_binding', 'validate_task_material_io'}
            if lane and lane.get('narrative_binding_required'):
                required_v2_refs.add('validate_narrative_object_binding')
            if lane and lane.get('template_binding_required'):
                required_v2_refs.add('validate_template_object_binding')
            if (
                'validate_expression_design_object_binding' in refs
                or task.get('expression_design_object_refs')
                or task.get('expression_design_applicability')
                or task_requires_expression_design(task, lane)
            ):
                required_v2_refs.add('validate_expression_design_object_binding')
            if not required_v2_refs.issubset(set(refs)):
                failures.append('validate_validator_reference_closure')
        if is_v2 or 'validate_agent_lane_department_binding' in refs:
            if not validate_agent_lane_department_binding(task, lane):
                failures.append('validate_agent_lane_department_binding')
        if is_v2 or 'validate_task_material_io' in refs:
            if not validate_task_material_io(task, fixture, artifacts):
                failures.append('validate_task_material_io')
        if is_v2 or 'validate_narrative_object_binding' in refs:
            if not validate_narrative_object_binding(task, lane, fixture, report):
                failures.append('validate_narrative_object_binding')
        if is_v2 or 'validate_template_object_binding' in refs:
            if not validate_template_object_binding(task, lane, fixture, report):
                failures.append('validate_template_object_binding')
        if (
            'validate_expression_design_object_binding' in refs
            or task.get('expression_design_object_refs')
            or task.get('expression_design_applicability')
            or task_requires_expression_design(task, lane)
        ):
            if not validate_expression_design_object_binding(task, lane, fixture, report):
                failures.append('validate_expression_design_object_binding')
            if task_requires_rendered_surface_gate(task, lane) and not task_declares_rendered_surface_gate(task, fixture):
                failures.append('validate_rendered_pdf_surface_text')
        if 'validate_repository_hygiene_report' in refs:
            if not validate_repository_hygiene_report(task, fixture, artifacts):
                failures.append('validate_repository_hygiene_report')
        if authority_refs_enabled(refs, task):
            if missing_authority_validator_refs(task, refs):
                failures.append('validate_validator_reference_closure')
            if not validate_actor_provenance_present(task):
                failures.append('validate_actor_provenance_present')
            if not validate_actor_provenance_artifact_trusted(task, fixture):
                failures.append('validate_actor_provenance_artifact_trusted')
            if not validate_effective_actor_identity_resolved(task):
                failures.append('validate_effective_actor_identity_resolved')
            if not validate_derived_sensitivity_classification(task, refs):
                failures.append('validate_derived_sensitivity_classification')
            if not validate_manager_direct_inferred_or_declared(task):
                failures.append('validate_manager_direct_inferred_or_declared')
            if not validate_manager_direct_intervention_declared(task, fixture):
                failures.append('validate_manager_direct_intervention_declared')
            if not validate_manager_direct_independent_review(task, refs, fixture):
                failures.append('validate_manager_direct_independent_review')
            if not validate_no_manager_self_certification(task, refs):
                failures.append('validate_no_manager_self_certification')
            if not validate_role_separation_for_paper_facing_tasks(task, refs):
                failures.append('validate_role_separation_for_paper_facing_tasks')
            if not validate_manager_direct_handoff_disclosure(task, fixture, refs):
                failures.append('validate_manager_direct_handoff_disclosure')
            if not validate_completion_state_limited_without_independent_review(task, refs, fixture):
                failures.append('validate_completion_state_limited_without_independent_review')
        unknown_refs = [r for r in refs if r not in KNOWN_VALIDATORS]
        if unknown_refs:
            failures.append('validate_validator_reference_closure')
        collected = task_has_collected(task, fixture)
        missing_evidence = missing_validator_evidence(task, report, refs)
        validated = bool(refs) and not missing_evidence
        if missing_evidence:
            failures.extend(['validate_task_status_transitions', 'validate_validator_report'])
        ingested = task_has_ingest(task)
        transitioned = task_has_state_transition(task)
        status = task.get('status')
        if status == 'complete' and not (collected and validated and ingested and transitioned):
            failures.extend(['validate_dispatch_not_complete', 'validate_state_machine', 'validate_task_status_transitions'])
        if task.get('collected_outputs') and not validated:
            failures.extend(['validate_task_status_transitions', 'validate_subagent_output'])
        if validated and not ingested:
            failures.extend(['validate_task_status_transitions', 'validate_state_machine'])
        if status == 'dispatched' and task.get('timeout_policy', {}).get('timed_out') and not collected:
            failures.extend(['validate_dispatch_not_complete', 'validate_task_status_transitions'])

    if motivation.get('confirmation_status') != 'confirmed':
        failures.append('validate_motivation_confirmation')

    rows = rationale.get('rows') or []
    if len(rows) < 2:
        failures.append('validate_rationale_matrix')
    for row in rows:
        purpose = str(row.get('rhetorical_purpose', ''))
        if len(purpose.split()) < 8 or not (row.get('evidence_anchors') or row.get('citation_anchors')):
            failures.append('validate_rationale_matrix')

    for claim in evidence_bank.get('claims') or []:
        if claim.get('support_status') != 'supported' or not (claim.get('evidence_refs') or claim.get('citation_refs') or claim.get('source_refs')):
            failures.append('validate_claim_support')

    for finding in review.get('findings') or []:
        if finding.get('status') == 'accepted':
            required = ['severity', 'evidence_status', 'owner_lane', 'fix_task', 'resolution_status']
            if any(not finding.get(k) for k in required) or finding.get('owner_lane') not in allowed_owner_lanes(root):
                failures.append('validate_review_backflow')

    val_summary = export.get('validation_summary') or {}
    if export and (export.get('readiness') == 'ready') and val_summary.get('status') != 'pass':
        failures.append('validate_export_manifest')

    failures.extend(validate_known_material_object_bindings(fixture, artifacts, tasks, registry_lanes))

    if not validate_reviewer_question_map_material(fixture, artifacts, tasks):
        failures.append('validate_reviewer_question_map')
    if not validate_main_text_construction_matrix_material(fixture, artifacts, tasks):
        failures.append('validate_main_text_construction_matrix_refs')
    if not validate_cognitive_load_budget_material(fixture, artifacts, tasks):
        failures.append('validate_cognitive_load_budget')
    if not validate_cognitive_load_budget_consumed_material(fixture, artifacts, tasks):
        failures.append('validate_cognitive_load_budget_consumed')
    if not validate_explanation_ladder_material(fixture, artifacts, tasks):
        failures.append('validate_explanation_ladder')
    if not validate_explanation_ladder_progression_material(fixture, artifacts, tasks):
        failures.append('validate_explanation_ladder_progression')
    if not validate_rhetorical_move_matrix_material(fixture, artifacts, tasks):
        failures.append('validate_rhetorical_move_matrix')
    if not validate_rhetorical_move_matrix_consumed_material(fixture, artifacts, tasks):
        failures.append('validate_rhetorical_move_matrix_consumed')
    if not validate_claim_evidence_visibility_map_material(fixture, artifacts, tasks):
        failures.append('validate_claim_evidence_visibility_map')
    if not validate_claim_evidence_visibility_material(fixture, artifacts, tasks):
        failures.append('validate_claim_evidence_visibility')
    if not validate_terminology_register_material(fixture, artifacts, tasks):
        failures.append('validate_terminology_register')
    if not validate_terminology_register_surface_material(fixture, artifacts, tasks):
        failures.append('validate_terminology_register_surface')
    if not validate_claim_citation_capsule_material(fixture, artifacts, tasks):
        failures.append('validate_claim_citation_capsule_support')
    if not validate_result_package_material(fixture, artifacts, tasks):
        failures.append('validate_result_package_claim_boundary')
    if not validate_single_writer_lock_material(fixture, artifacts, tasks):
        failures.append('validate_single_writer_lock_held')
    if not validate_reader_surface_tutor_review_material(fixture, artifacts, tasks):
        failures.append('validate_reader_surface_tutor_review_spans')
    if not validate_nature_figure_contract_material(fixture, artifacts, tasks):
        failures.append('validate_nature_figure_contract')
    if not validate_nature_figure_aesthetic_profile_material(fixture, artifacts, tasks):
        failures.append('validate_nature_figure_aesthetic_profile')
    if not validate_panel_evidence_map_material(fixture, artifacts, tasks):
        failures.append('validate_panel_evidence_map')
    if not validate_figure_backend_route_material(fixture, artifacts, tasks):
        failures.append('validate_figure_backend_route')
    if not validate_figure_source_data_statistics_material(fixture, artifacts, tasks):
        failures.append('validate_figure_source_data_statistics')
    if not validate_figure_image_integrity_record_material(fixture, artifacts, tasks):
        failures.append('validate_figure_image_integrity_record')
    if not validate_nature_caption_legend_material(fixture, artifacts, tasks):
        failures.append('validate_nature_caption_legend')
    if not validate_nature_figure_qa_report_material(fixture, artifacts, tasks):
        failures.append('validate_nature_figure_qa_report')
    if not validate_figure_export_bundle_material(fixture, artifacts, tasks):
        failures.append('validate_figure_export_bundle')
    if not validate_nature_source_inventory_material(fixture, artifacts, tasks):
        failures.append('validate_nature_source_inventory')
    if not validate_company_skill_registry_material(fixture, artifacts, tasks):
        failures.append('validate_company_skill_registry')
    if not validate_paper_reader_package_material(fixture, artifacts, tasks):
        failures.append('validate_paper_reader_package')
    if not validate_search_strategy_dossier_material(fixture, artifacts, tasks):
        failures.append('validate_search_strategy_dossier')
    if not validate_citation_verification_report_material(fixture, artifacts, tasks):
        failures.append('validate_citation_verification_report')
    if not validate_section_move_plan_material(fixture, artifacts, tasks):
        failures.append('validate_section_move_plan')
    if not validate_journal_style_profile_material(fixture, artifacts, tasks):
        failures.append('validate_journal_style_profile')
    if not validate_polishing_repair_report_material(fixture, artifacts, tasks):
        failures.append('validate_polishing_repair_report')
    if not validate_data_availability_plan_material(fixture, artifacts, tasks):
        failures.append('validate_data_availability_plan')
    if not validate_reviewer_panel_report_material(fixture, artifacts, tasks):
        failures.append('validate_reviewer_panel_report')
    if not validate_response_action_map_material(fixture, artifacts, tasks):
        failures.append('validate_response_action_map')
    if not validate_presentation_plan_material(fixture, artifacts, tasks):
        failures.append('validate_presentation_plan')
    if not validate_patent_draft_boundary_material(fixture, artifacts, tasks):
        failures.append('validate_patent_draft_boundary')
    if not validate_nature_absorption_package_material(fixture, artifacts, tasks):
        failures.append('validate_nature_absorption_package')

    department_failures, department_detail = validate_department_accountability_fixture(
        fixture, root, tasks, artifacts
    )
    failures.extend(department_failures)
    if department_detail:
        detail['department_accountability'] = department_detail

    rendered_text_ok, rendered_ok, bare_citekeys_ok = validate_rendered_surface_gate_material(fixture, artifacts, tasks)
    if not rendered_text_ok:
        failures.append('validate_rendered_pdf_surface_text')
    if not rendered_ok:
        failures.append('validate_no_internal_codes_in_rendered_text')
    if not bare_citekeys_ok:
        failures.append('validate_no_bare_citekeys_in_export')

    if artifacts:
        fixture_passing_validators: set[str] = set()
        for task in tasks:
            refs = normalize_validator_refs(task, failures)
            fixture_passing_validators.update(passing_validator_names(task, report))
        for art in artifacts.get('artifacts') or []:
            art_refs = list(art.get('validator_refs') or [])
            for ref in art_refs:
                if ref not in KNOWN_VALIDATORS:
                    failures.append('validate_validator_reference_closure')
            if art.get('owner_lane') and art.get('owner_lane') not in allowed_owner_lanes(root):
                failures.append('validate_owner_lane_closure')
            if art.get('status') in {'validated', 'complete', 'ready'}:
                missing_artifact_evidence = set(art_refs) - fixture_passing_validators
                if missing_artifact_evidence:
                    failures.append('validate_validator_report')

    return sorted(set(failures)), detail


def check_fixtures(root: Path) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    detail: dict[str, Any] = {'valid': {}, 'invalid': {}, 'valid_count': 0, 'invalid_count': 0}
    valid_root = root / 'fixtures/valid'
    for fx in sorted(valid_root.iterdir() if valid_root.exists() else []):
        if not fx.is_dir():
            continue
        detail['valid_count'] += 1
        fx_fail, _ = check_fixture(fx, root)
        detail['valid'][fx.name] = fx_fail
        if fx_fail:
            failures.append(f'valid_fixture_failed:{fx.name}:{",".join(fx_fail)}')
    invalid_root = root / 'fixtures/invalid'
    for fx in sorted(invalid_root.iterdir() if invalid_root.exists() else []):
        if not fx.is_dir():
            continue
        detail['invalid_count'] += 1
        meta = load_yaml(fx / 'fixture-meta.yaml', {})
        expected = set(meta.get('expected_failures') or [])
        allowed_extra = set(meta.get('allowed_extra_failures') or [])
        fx_fail, _ = check_fixture(fx, root)
        got = set(fx_fail)
        detail['invalid'][fx.name] = {
            'expected': sorted(expected),
            'allowed_extra': sorted(allowed_extra),
            'got': sorted(got),
        }
        if not expected:
            failures.append(f'invalid_fixture_missing_expected:{fx.name}')
        if not got:
            failures.append(f'invalid_fixture_unexpectedly_passed:{fx.name}')
        missing = expected - got
        if missing:
            failures.append(f'invalid_fixture_missing_expected_failures:{fx.name}:{",".join(sorted(missing))}')
        unexpected = got - expected - allowed_extra
        if unexpected:
            failures.append(f'invalid_fixture_unexpected_extra_failures:{fx.name}:{",".join(sorted(unexpected))}')
    if detail['valid_count'] == 0 or detail['invalid_count'] == 0:
        failures.append('validate_fixture_matrix_nonempty')
    for fixture_name in sorted(REQUIRED_DEPARTMENT_FIXTURES['valid']):
        if fixture_name not in detail['valid']:
            failures.append(f'missing_valid_fixture:{fixture_name}')
    for fixture_name in sorted(REQUIRED_DEPARTMENT_FIXTURES['invalid']):
        if fixture_name not in detail['invalid']:
            failures.append(f'missing_invalid_fixture:{fixture_name}')
    return failures, detail


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('scaffold')
    p.add_argument('root', type=Path)
    p = sub.add_parser('fixture')
    p.add_argument('fixture_dir', type=Path)
    p = sub.add_parser('fixtures')
    p.add_argument('root', type=Path)
    args = parser.parse_args(argv)
    if args.cmd == 'scaffold':
        failures, detail = check_scaffold(args.root)
    elif args.cmd == 'fixture':
        failures, detail = check_fixture(args.fixture_dir)
    else:
        failures, detail = check_fixtures(args.root)
    return dump_result(not failures, failures, detail)

if __name__ == '__main__':
    raise SystemExit(main())
