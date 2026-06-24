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
    'validate_validator_report', 'validate_source_locator_resolution', 'validate_owner_lane_closure',
    'validate_validator_reference_closure', 'validate_task_status_transitions',
    'validate_direct_execution_adapter', 'validate_verifier_review', 'validate_pua_telemetry',
    'validate_agent_lane_department_binding', 'validate_task_material_io',
    'validate_narrative_object_binding', 'validate_template_object_binding',
    'validate_template_mirror_sync', 'validate_fixture_matrix_nonempty',
    'validate_manager_handoff_v2',
    'validate_reader_spine_brief', 'validate_object_representation_matrix',
    'validate_template_quant_profile', 'validate_section_function_budget',
    'validate_visual_budget', 'validate_reader_experience_review_gate',
    'validate_narrative_backflow', 'validate_repository_hygiene_report',
    'validate_main_text_surface_rules', 'validate_no_internal_codes_in_main_prose',
    'validate_no_snake_case_constraints_in_main_prose', 'validate_no_raw_method_ids_in_main_prose',
    'validate_no_defensive_claim_boundary_wall', 'validate_no_bare_citekeys_in_export',
    'validate_rendered_pdf_surface_text',
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
    'main-text-surface-rules.yaml',
]

REQUIRED_ROOT_FILES = [
    '.codex-plugin/plugin.json',
    'skills/yxj-paper-index/references/workspace-contract.md',
    'skills/yxj-paper-state/references/state-contract.md',
    'skills/yxj-paper-execute/references/runtime-execution-contract.md',
    'skills/yxj-paper-execute/references/agent-contract.md',
    'skills/yxj-paper-execute/references/agent-lane-registry.yaml',
    'skills/yxj-paper-index/references/source-influences.md',
    'docs/architecture.md', 'docs/operation-guide.md', 'docs/migration-notes.md',
    'docs/production-readiness-checklist.md',
]


def load_yaml(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as fh:
        return yaml.safe_load(fh) or default


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
    invalid_root = root / 'fixtures/invalid'
    if not invalid_root.exists() or len([p for p in invalid_root.iterdir() if p.is_dir()]) < 15:
        failures.append('missing_invalid_fixture_set')
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
}

V2_VALIDATOR_REFS = {
    'validate_agent_lane_department_binding', 'validate_task_material_io',
    'validate_narrative_object_binding', 'validate_template_object_binding',
    'validate_repository_hygiene_report',
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
    inputs = task.get('input_materials')
    outputs = task.get('expected_output_materials')
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
            if type(worktree.get(key)) is not int or worktree.get(key) < 0:
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
        if 'validate_repository_hygiene_report' in refs:
            if not validate_repository_hygiene_report(task, fixture, artifacts):
                failures.append('validate_repository_hygiene_report')
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
