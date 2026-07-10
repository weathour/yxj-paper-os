#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
import re
import datetime
from pathlib import Path


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract(raw):
    t = Path(raw).read_text(encoding="utf-8")
    m = re.search(r'\{\s*"responses"\s*:\s*\[.*\]\s*\}', t, re.S)
    if not m:
        raise ValueError("raw output must contain top-level responses JSON")
    x = json.loads(m.group(0))
    if set(x) != {"responses"}:
        raise ValueError("capture document must contain only responses")
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["init", "finalize"])
    ap.add_argument("--capture", required=True)
    ap.add_argument("--model", default="unknown")
    ap.add_argument("--runtime", default="unknown")
    ap.add_argument("--skill", default="skills/yxj-paper-os/SKILL.md")
    ap.add_argument(
        "--scenarios",
        default="skills/yxj-paper-os/assets/evals/behavior-scenarios.json",
    )
    a = ap.parse_args()
    c = Path(a.capture)
    c.mkdir(parents=True, exist_ok=True)
    if a.command == "init":
        scen = Path(a.scenarios).read_text()
        prompt = f'Behavior capture. Return exactly JSON object {{"responses":[14 response objects]}}.\nSKILL SHA-256: {sha(Path(a.skill))}\nSCENARIOS:\n{scen}'
        (c / "prompt.md").write_text(prompt)
        print(c / "prompt.md")
        return 0
    raw = c / "raw-output.md"
    obj = extract(raw)
    responses = obj.get("responses")
    required = {
        "scenario_id",
        "selected_actions",
        "target_dimensions",
        "target_scopes",
        "updates",
        "readiness_updates",
        "question",
        "side_effects",
    }
    if (
        not isinstance(responses, list)
        or len(responses) != 14
        or len({r.get("scenario_id") for r in responses if isinstance(r, dict)}) != 14
    ):
        raise ValueError("capture must contain exactly 14 unique response records")
    if any(not isinstance(r, dict) or not required.issubset(r) for r in responses):
        raise ValueError("every response must match the response schema")
    (c / "actions.json").write_text(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    )
    man = {
        "model": a.model,
        "runtime": a.runtime,
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "skill_sha256": sha(Path(a.skill)),
        "scenarios_sha256": sha(Path(a.scenarios)),
        "prompt_sha256": sha(c / "prompt.md"),
        "raw_output_sha256": sha(raw),
        "actions_sha256": sha(c / "actions.json"),
        "scenario_ids": [r.get("scenario_id") for r in responses],
    }
    (c / "manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    print(c / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
