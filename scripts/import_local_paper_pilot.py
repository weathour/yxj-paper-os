#!/usr/bin/env python3
"""Project a paper repository into a read-only Paper OS pilot package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "examples" / "sample-paper-workspace"
DEFAULT_OUT = ROOT / "examples" / "local-paper" / "sample-paper-workspace"
REQUIRED_SOURCE_FILES = [
    "README.md",
    "HANDOFF.md",
    "PROJECT_STATUS.md",
    "NEXT-SESSION-START.md",
    "docs/CURRENT_PLAN.md",
    "docs/LATEST_SYNC_BRIEF.md",
    "paper-workspace.json",
    "paper-os/materials/current-material-index.json",
    "manuscript/README.md",
    "manuscript/main.tex",
]
OPTIONAL_PROVENANCE_FILES = [
    "archive/2026-07-01-prewriting-reset/ARCHIVE_MANIFEST.md",
    "archive/2026-07-01-prewriting-reset/paper-os/materials/ClaimBoundaryMap-current.json",
    "archive/2026-07-01-prewriting-reset/paper-os/materials/EvidenceInventory-L3-20260625.json",
    "archive/2026-07-01-prewriting-reset/docs/L3_METHOD_FAITHFUL_UNIFIED_SCENE_RERUN_2026-06-25.md",
    "archive/2026-07-01-prewriting-reset/docs/L3_METHOD_FAITHFUL_NON_TEXT_EVIDENCE_CHECKLIST_2026-06-25.md",
]
MANUSCRIPT_SECTIONS = [
    "manuscript/sections/01_introduction.tex",
    "manuscript/sections/02_related_work.tex",
    "manuscript/sections/03_problem_formulation.tex",
    "manuscript/sections/04_method.tex",
    "manuscript/sections/05_experiments.tex",
    "manuscript/sections/06_results_discussion.tex",
    "manuscript/sections/07_conclusion.tex",
]
EVIDENCE_LOCATORS = [
    "experiments/results/L3_method_faithful_unified_scene_20260625",
    "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements",
    "experiments/baselines/method_faithful_final_claim_classes_20260625_l3.csv",
]
VERIFICATION_COMMANDS = [
    "cd manuscript && latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex",
    "python experiments/src/verify_sota_baseline_method_faithful_experiment.py --results experiments/results/L3_method_faithful_unified_scene_20260625 --mode validate --expected-seeds 200",
    "python scripts/generate_sota_non_text_evidence_supplements.py --source experiments/results/L3_method_faithful_unified_scene_20260625 --out experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements --docs-out docs/L3_METHOD_FAITHFUL_NON_TEXT_EVIDENCE_CHECKLIST_2026-06-25.md --check",
]

FORBIDDEN_SOURCE_RUNTIME_ARTIFACT_PREFIXES = (
    "docs/runtime-viewer",
)


def fail(code: str, message: str) -> int:
    print(f"{code}: {message}", file=sys.stderr)
    return 1


def run_git_status(source: Path) -> str:
    try:
        proc = subprocess.run(["git", "-C", str(source), "status", "--short", "--", "."], check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return "<git-not-found>"
    if proc.returncode != 0:
        return f"<git-status-error:{proc.stderr.strip()}>"
    return proc.stdout

def source_runtime_artifact_violations(source: Path, git_status: str) -> list[str]:
    violations: set[str] = set()
    for path in source.rglob("*"):
        rel = path.relative_to(source)
        if ".git" in rel.parts or ".omx" in rel.parts:
            continue
        norm = rel.as_posix().strip("/")
        for prefix in FORBIDDEN_SOURCE_RUNTIME_ARTIFACT_PREFIXES:
            if norm == prefix or norm.startswith(prefix + "/"):
                violations.add(norm)
    for row in git_status.splitlines():
        path_part = row[3:] if len(row) > 3 else row
        candidates = [path_part]
        if " -> " in path_part:
            candidates.extend(path_part.split(" -> "))
        for candidate in candidates:
            norm = candidate.strip().strip("/")
            for prefix in FORBIDDEN_SOURCE_RUNTIME_ARTIFACT_PREFIXES:
                if norm == prefix or norm.startswith(prefix + "/"):
                    violations.add(norm)
    return sorted(violations)


def file_fingerprint(path: Path) -> dict[str, Any]:
    st = path.stat()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    # Keep committed sample fingerprints checkout-portable: mtime/ctime vary across archives and clones.
    return {"size": st.st_size, "sha256": digest}


def selected_fingerprints(source: Path) -> dict[str, dict[str, Any]]:
    targets = REQUIRED_SOURCE_FILES + MANUSCRIPT_SECTIONS
    out: dict[str, dict[str, Any]] = {}
    for rel in targets:
        path = source / rel
        if path.is_file():
            out[rel] = file_fingerprint(path)
    return out


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def repo_ref(path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(ROOT.resolve(strict=True)).as_posix()
    except ValueError:
        return str(resolved)


def write_text_artifact(out: Path, rel: str, content: str) -> None:
    path = out / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json_artifact(out: Path, rel: str, payload: dict[str, Any]) -> None:
    path = out / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_s16_live_export_fixture_artifacts(out: Path) -> None:
    """Recreate deterministic S16 live-export fixture files after pilot import.

    `import_local_paper_pilot.py` owns the destructive rebuild of the local-paper
    pilot root.  Any committed fixture under that generated root must therefore
    be re-emitted here; otherwise Phase9/Phase10 readiness checks correctly flag
    tracked deletions.  These files are fixture export artifacts only and do not
    mutate the read-only source paper repository.
    """

    write_text_artifact(out, "build/latexmk.log", "Latexmk fixture: build completed without errors.\n")
    write_text_artifact(
        out,
        "build/main-template.pdf",
        "%PDF-1.4\n% template-only fixture\n1 0 obj << /Type /Catalog >> endobj\n%%EOF\n",
    )
    write_text_artifact(
        out,
        "build/main-template.txt",
        "Manuscript Not Started\n\n"
        "This template-only placeholder TODO text should never satisfy a compiled initial draft target.\n\n"
        "References\n",
    )
    write_text_artifact(
        out,
        "build/main.pdf",
        "%PDF-1.4\n% content-bearing compiled draft fixture\n1 0 obj << /Type /Catalog >> endobj\n%%EOF\n",
    )
    write_text_artifact(
        out,
        "build/main.txt",
        "Security-state-aware mixed platoon control is evaluated through a content-bearing manuscript fixture. "
        "The first body paragraph states the problem, explains the cyber-physical safety context, and connects "
        "experiment evidence to the manuscript contribution using complete draft language. It contains enough "
        "natural language to serve as a rendered-text smoke fixture for the compiled target gate.\n\n"
        "The second body paragraph discusses methods, data, figure references, and claim boundaries. It mentions "
        "Figure 1 as a real paper-facing figure and describes how the evidence supports a bounded initial draft "
        "rather than a publication or submission claim. The paragraph is intentionally long enough to be counted "
        "as body content by the live verifier.\n\n"
        "References\n"
        "[1] Jane Doe. Fixture Reference for Paper OS validation. Journal, 2026.\n",
    )
    write_text_artifact(out, "figures/figure1.pdf", "%PDF-1.4\n% figure fixture\n%%EOF\n")
    write_text_artifact(
        out,
        "manuscript/main.tex",
        "\\documentclass{article}\n\\begin{document}\nContent-bearing compiled draft fixture.\\end{document}\n",
    )
    write_text_artifact(
        out,
        "refs/references.bib",
        "@article{fixture2026, title={Fixture Reference}, author={Doe, Jane}, journal={Journal}, year={2026}}\n",
    )
    write_json_artifact(
        out,
        "build/rendered-surface-review.json",
        {
            "schema_version": "ppg-rendered-surface-review/v0.1",
            "review_id": "compiled-draft-rendered-surface-review-fixture-v1",
            "pdf_ref": "examples/local-paper/sample-paper-workspace/build/main.pdf",
            "text_ref": "examples/local-paper/sample-paper-workspace/build/main.txt",
            "body_paragraphs_present": True,
            "bibliography_present": True,
            "forbidden_template_sentinels": [],
            "status": "pass",
        },
    )
    write_json_artifact(
        out,
        "paper-os/writeback/compiled-draft-plan.json",
        {
            "schema_version": "ppg-latex-writeback-plan/v0.1",
            "plan_id": "compiled-draft-plan-fixture-v1",
            "target": "compiled_initial_draft",
            "source_material_ref": "examples/materials/phase10_s12_integration_report.json",
            "actions": [
                "write integrated S12 manuscript into manuscript/main.tex",
                "preserve bibliography and figure refs",
                "build after writeback",
            ],
            "status": "ready",
        },
    )
    write_json_artifact(
        out,
        "paper-os/writeback/compiled-draft-patchset.json",
        {
            "schema_version": "ppg-latex-writeback-patchset/v0.1",
            "patchset_id": "compiled-draft-patchset-fixture-v1",
            "files_changed": [
                "examples/local-paper/sample-paper-workspace/manuscript/main.tex",
                "examples/local-paper/sample-paper-workspace/refs/references.bib",
            ],
            "claim_boundary_preserved": True,
            "status": "prepared",
        },
    )
    write_json_artifact(
        out,
        "paper-os/writeback/compiled-draft-apply-report.json",
        {
            "schema_version": "ppg-latex-writeback-apply-report/v0.1",
            "apply_report_id": "compiled-draft-apply-fixture-v1",
            "applied_files": [
                "examples/local-paper/sample-paper-workspace/manuscript/main.tex",
                "examples/local-paper/sample-paper-workspace/refs/references.bib",
            ],
            "build_required_after_apply": True,
            "status": "applied",
        },
    )
    write_json_artifact(
        out,
        "paper-os/writeback/source-tree-after.json",
        {
            "schema_version": "ppg-source-tree-snapshot/v0.1",
            "snapshot_id": "compiled-draft-source-tree-after-fixture-v1",
            "tracked_sources": [
                "examples/local-paper/sample-paper-workspace/manuscript/main.tex",
                "examples/local-paper/sample-paper-workspace/refs/references.bib",
                "examples/local-paper/sample-paper-workspace/figures/figure1.pdf",
            ],
            "unexpected_changes": [],
            "status": "captured",
        },
    )
    write_json_artifact(
        out,
        "paper-os/writeback/claim-boundary-audit.json",
        {
            "schema_version": "ppg-claim-boundary-audit/v0.1",
            "audit_id": "compiled-draft-claim-boundary-audit-fixture-v1",
            "overclaims": [],
            "unsupported_claims": [],
            "boundary_status": "pass",
        },
    )
    write_json_artifact(
        out,
        "paper-os/writeback/template-compatibility-check.json",
        {
            "schema_version": "ppg-template-compatibility-check/v0.1",
            "check_id": "compiled-draft-template-compatibility-fixture-v1",
            "template_only_sections_remaining": [],
            "internal_stage_id_leakage": [],
            "status": "pass",
        },
    )


def ensure_output_safe(source: Path, out: Path) -> None:
    source_resolved = source.resolve(strict=True)
    runtime_root = ROOT.resolve(strict=True)
    out_parent_resolved = out.parent.resolve(strict=False)
    out_resolved = out.resolve(strict=False)
    if is_relative_to(out_resolved, source_resolved) or out_resolved == source_resolved:
        raise ValueError("output path must not be inside the source paper repository")
    if is_relative_to(out_parent_resolved, source_resolved) or out_parent_resolved == source_resolved:
        raise ValueError("output parent must not be inside the source paper repository")
    if not is_relative_to(out_parent_resolved, runtime_root):
        raise ValueError("output parent must be inside the runtime repository")
    if out.exists() or out.is_symlink():
        existing_target = out.resolve(strict=True)
        if is_relative_to(existing_target, source_resolved) or existing_target == source_resolved:
            raise ValueError("output path symlink/write-through target must not point into source paper repository")
        if not is_relative_to(existing_target, runtime_root):
            raise ValueError("existing output path must remain inside the runtime repository")


def extract_claim_boundary(readme: str, status: str, workspace: dict[str, Any], material_index: dict[str, Any]) -> dict[str, Any]:
    manuscript_state = workspace.get("manuscript_state")
    material_status = material_index.get("status")
    active_authority = workspace.get("active_manuscript_authority") or material_index.get("active_manuscript_authority")
    if manuscript_state == "not_started" or material_status == "prewriting_not_started":
        return {
            "manuscript_state": "not_started",
            "active_method": None,
            "method_name": None,
            "active_manuscript_authority": active_authority or "template_only",
            "claim_ladder_status": "none",
            "figure_table_status": "none",
            "previous_content_policy": workspace.get("previous_content_policy", "reference_only"),
            "archive_ref": material_index.get("archive_ref") or workspace.get("reference_archive"),
            "candidate_evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
            "candidate_non_text_evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/",
            "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
            "source_excerpt_sha256": hashlib.sha256((readme + status + json.dumps(workspace, sort_keys=True) + json.dumps(material_index, sort_keys=True)).encode("utf-8")).hexdigest(),
        }
    return {
        "active_method": "zt_md_mpc_full",
        "method_name": "Zero-Trust Memory-Degradation MPC",
        "zero_trust_boundary": "controller-side zero-default authority for degraded V2X evidence; not cryptographic/network zero trust",
        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
        "non_text_evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/",
        "external_rows_claim_class": "shared-lab L3 method-mechanism comparators; not exact source-paper scenario/result reproductions",
        "validation_scope": "17 methods × 9 scenarios × 200 held-out validation seeds = 30600 raw rows",
        "raw_safety_boundary": "ACC-only leads raw gap/TTC; ZT-MD-MPC wins aggregate score and is collision-free in validation suite",
        "source_excerpt_sha256": hashlib.sha256((readme + status).encode("utf-8")).hexdigest(),
    }


def project(source: Path, out: Path, *, check: bool) -> int:
    source = source.expanduser().resolve(strict=True)
    out = out.expanduser()
    ensure_output_safe(source, out)
    missing = [rel for rel in REQUIRED_SOURCE_FILES if not (source / rel).is_file()]
    if missing:
        return fail("E_PHASE9_LOCAL_PAPER_SOURCE_MISSING", ", ".join(missing))
    before_status = run_git_status(source)
    violations = source_runtime_artifact_violations(source, before_status)
    if violations:
        return fail("E_PHASE9_SOURCE_RUNTIME_ARTIFACT", ", ".join(violations[:8]))
    before_fingerprints = selected_fingerprints(source)
    if out.exists() and not out.is_symlink():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    materials = out / "materials"
    materials.mkdir(parents=True, exist_ok=True)
    readme = (source / "README.md").read_text(encoding="utf-8")
    handoff = (source / "HANDOFF.md").read_text(encoding="utf-8")
    status = (source / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_plan = (source / "docs/CURRENT_PLAN.md").read_text(encoding="utf-8")
    workspace = json.loads((source / "paper-workspace.json").read_text(encoding="utf-8"))
    material_index = json.loads((source / "paper-os/materials/current-material-index.json").read_text(encoding="utf-8"))
    claim_boundary = extract_claim_boundary(readme, status, workspace, material_index)
    source_files = REQUIRED_SOURCE_FILES + MANUSCRIPT_SECTIONS
    provenance_files = [rel for rel in OPTIONAL_PROVENANCE_FILES if (source / rel).exists()]
    manifest = {
        "schema_version": "ppg-local-paper-pilot-manifest/v0.1",
        "project_slug": workspace.get("project_slug", out.name),
        "source_root": repo_ref(source),
        "runtime_output_root": repo_ref(out),
        "read_only_source": True,
        "claim_boundary": claim_boundary,
        "source_files": [{"path": rel, "exists": (source / rel).exists()} for rel in source_files],
        "optional_provenance_files": [{"path": rel, "exists": (source / rel).exists()} for rel in OPTIONAL_PROVENANCE_FILES],
        "present_provenance_files": provenance_files,
        "evidence_locators": [{"path": rel, "exists": (source / rel).exists(), "authority": "candidate_input_until_S01_S04_promotion"} for rel in EVIDENCE_LOCATORS],
        "verification_commands": VERIFICATION_COMMANDS,
        "source_git_status_before": before_status,
        "source_git_status_after": None,
        "source_fingerprint_before": before_fingerprints,
        "source_fingerprint_after": None,
    }
    (materials / "owner_contract.json").write_text(json.dumps({
        "schema_version": "ppg-pilot-material/v0.1",
        "material_id": "pilot_owner_contract",
        "source_refs": ["README.md", "HANDOFF.md", "PROJECT_STATUS.md"],
        "claim_boundary": claim_boundary,
        "submission_owner_gated": True,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (materials / "source_inventory.json").write_text(json.dumps({
        "schema_version": "ppg-pilot-material/v0.1",
        "material_id": "pilot_source_inventory",
        "source_refs": source_files,
        "evidence_locators": EVIDENCE_LOCATORS,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (materials / "paper_status_summary.json").write_text(json.dumps({
        "schema_version": "ppg-pilot-material/v0.1",
        "material_id": "pilot_paper_status_summary",
        "source_refs": ["HANDOFF.md", "PROJECT_STATUS.md", "docs/CURRENT_PLAN.md"],
        "summary_sha256": hashlib.sha256((handoff + status + current_plan).encode("utf-8")).hexdigest(),
        "manuscript_state": claim_boundary.get("manuscript_state", "active_or_legacy"),
        "active_method": claim_boundary.get("active_method"),
        "active_manuscript_authority": claim_boundary.get("active_manuscript_authority"),
        "ready_for_runtime_pilot": True,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_s16_live_export_fixture_artifacts(out)
    after_status = run_git_status(source)
    violations = source_runtime_artifact_violations(source, after_status)
    if violations:
        return fail("E_PHASE9_SOURCE_RUNTIME_ARTIFACT", ", ".join(violations[:8]))
    after_fingerprints = selected_fingerprints(source)
    manifest["source_git_status_after"] = after_status
    manifest["source_fingerprint_after"] = after_fingerprints
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if check:
        if before_status != after_status:
            return fail("E_PHASE9_LOCAL_PAPER_SOURCE_STATUS_CHANGED", "source git status changed during import")
        if before_fingerprints != after_fingerprints:
            return fail("E_PHASE9_LOCAL_PAPER_SOURCE_FINGERPRINT_CHANGED", "source fingerprints changed during import")
        with tempfile.TemporaryDirectory(prefix="phase9-import-guard-") as tmp:
            tmp_path = Path(tmp)
            fake_source = tmp_path / "fake-source"
            fake_source.mkdir()
            rejected_parent = fake_source / "new-parent"
            try:
                ensure_output_safe(fake_source, rejected_parent / "pilot")
            except ValueError:
                if rejected_parent.exists():
                    return fail("E_PHASE9_LOCAL_PAPER_NEGATIVE_PARENT_CREATED", "rejected source-contained output parent was created")
            else:
                return fail("E_PHASE9_LOCAL_PAPER_NEGATIVE_NEW_PARENT_UNDER_SOURCE", "new output parent under source was not rejected")
            try:
                ensure_output_safe(source, source / "phase9-output-negative")
            except ValueError:
                pass
            else:
                return fail("E_PHASE9_LOCAL_PAPER_NEGATIVE_UNDER_SOURCE", "output-under-source was not rejected")
            escape = tmp_path / "escape"
            escape.symlink_to(source, target_is_directory=True)
            try:
                ensure_output_safe(source, escape)
            except ValueError:
                pass
            else:
                return fail("E_PHASE9_LOCAL_PAPER_NEGATIVE_SYMLINK", "symlink output escape was not rejected")
        loaded = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        loaded_boundary = loaded["claim_boundary"]
        if loaded_boundary.get("manuscript_state") == "not_started":
            if loaded_boundary.get("active_manuscript_authority") != "template_only":
                return fail("E_PHASE9_LOCAL_PAPER_CLAIM_BOUNDARY", "prewriting reset must remain template_only")
        elif "L3 method-mechanism" not in loaded_boundary.get("external_rows_claim_class", ""):
            return fail("E_PHASE9_LOCAL_PAPER_CLAIM_BOUNDARY", "L3 claim class missing")
    print("PHASE9_LOCAL_PAPER_IMPORT_OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        return project(args.source, args.out, check=args.check)
    except ValueError as exc:
        return fail("E_PHASE9_LOCAL_PAPER_OUTPUT_GUARD", str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
