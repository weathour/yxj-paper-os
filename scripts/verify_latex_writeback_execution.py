#!/usr/bin/env python3
"""Verify that the LaTeX writeback executor can dry-run, apply, build, and reject unsafe patchsets."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/writeback-plans/fixture-paper"
PLAN = ROOT / "examples/writeback-plans/fixture-latex-writeback.plan.valid.json"
PATCHSET = ROOT / "examples/writeback-plans/latex-writeback.patchset.valid.json"
NEGATIVE_PATCHSET = ROOT / "examples/writeback-plans/invalid-unsafe-latex-writeback.patchset.json"
SCRIPT = ROOT / "scripts/execute_latex_writeback_plan.py"


def run(cmd: list[str], *, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if expect_ok and proc.returncode != 0:
        raise SystemExit(f"COMMAND_FAILED {cmd}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    if not expect_ok and proc.returncode == 0:
        raise SystemExit(f"EXPECTED_FAILURE_MISSING {cmd}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc


def parse_report(proc: subprocess.CompletedProcess[str]) -> dict:
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"REPORT_JSON_PARSE_FAILED\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}") from exc


def init_fixture_git(source: Path) -> None:
    run(["git", "-C", str(source), "init"])
    run(["git", "-C", str(source), "config", "user.email", "paper-os@example.invalid"])
    run(["git", "-C", str(source), "config", "user.name", "Paper OS Test"])
    run(["git", "-C", str(source), "add", "--", "manuscript/main.tex", "manuscript/sections/01_intro.tex"])
    run(["git", "-C", str(source), "commit", "-m", "fixture baseline"])


def main() -> int:
    if not FIXTURE.is_dir():
        raise SystemExit(f"FIXTURE_MISSING {FIXTURE}")
    with tempfile.TemporaryDirectory(prefix="ppg-latex-writeback-") as tmp:
        source = Path(tmp) / "paper"
        shutil.copytree(FIXTURE, source)
        init_fixture_git(source)

        dry = run([
            "python3",
            str(SCRIPT),
            str(PLAN),
            str(PATCHSET),
            "--source-root",
            str(source),
            "--dry-run",
        ])
        dry_report = parse_report(dry)
        if dry_report.get("status") != "dry_run_ok":
            raise SystemExit(f"DRY_RUN_STATUS_BAD {dry_report}")
        intro = source / "manuscript/sections/01_intro.tex"
        if "Original placeholder sentence" not in intro.read_text(encoding="utf-8"):
            raise SystemExit("DRY_RUN_MUTATED_SOURCE")

        negative = run([
            "python3",
            str(SCRIPT),
            str(PLAN),
            str(NEGATIVE_PATCHSET),
            "--source-root",
            str(source),
            "--dry-run",
        ], expect_ok=False)
        if "E_WRITEBACK_PATCH_TARGET_UNSAFE" not in negative.stdout and "E_WRITEBACK_PATCH_TARGET_FORBIDDEN" not in negative.stdout:
            raise SystemExit(f"NEGATIVE_UNSAFE_TARGET_CODE_MISSING {negative.stdout}")

        report_out = Path(tmp) / "report.json"
        applied = run([
            "python3",
            str(SCRIPT),
            str(PLAN),
            str(PATCHSET),
            "--source-root",
            str(source),
            "--report-out",
            str(report_out),
        ])
        applied_report = parse_report(applied)
        if applied_report.get("status") != "applied_committed":
            raise SystemExit(f"APPLY_STATUS_BAD {applied_report}")
        if applied_report.get("apply_requested") is not True or applied_report.get("build_requested") is not True:
            raise SystemExit(f"DEFAULT_APPLY_BUILD_POLICY_BAD {applied_report}")
        text = intro.read_text(encoding="utf-8")
        if "controlled LaTeX body unit was promoted" not in text:
            raise SystemExit("APPLY_CONTENT_MISSING")
        if applied_report.get("changed_files") != ["manuscript/sections/01_intro.tex"]:
            raise SystemExit(f"APPLY_CHANGED_FILES_BAD {applied_report.get('changed_files')}")
        if not (source / "manuscript/build/main.pdf").is_file():
            raise SystemExit("LATEX_BUILD_OUTPUT_MISSING")
        commit_result = applied_report.get("git_commit_result", {})
        if commit_result.get("status") != "committed":
            raise SystemExit(f"GIT_COMMIT_STATUS_BAD {commit_result}")
        log = run(["git", "-C", str(source), "log", "-1", "--pretty=%s"]).stdout.strip()
        if "ppg latex writeback: S10 fixture-paper.s10.introduction-marker-writeback.v1" != log:
            raise SystemExit(f"GIT_COMMIT_MESSAGE_BAD {log}")
        diff = run(["git", "-C", str(source), "diff", "--", "manuscript/sections/01_intro.tex"])
        if diff.stdout.strip():
            raise SystemExit(f"GIT_COMMIT_DID_NOT_RECORD_SOURCE_DIFF {diff.stdout}")
        if not report_out.is_file():
            raise SystemExit("REPORT_OUT_MISSING")
    print("PPG_LATEX_WRITEBACK_EXECUTION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
