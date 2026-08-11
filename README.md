# YXJ Paper OS

YXJ Paper OS is a reader-first, evidence-bound Codex plugin for revising one academic
paper from assessment through direct writeback and verification.

Scientific integrity is the non-negotiable evidence boundary. Within that boundary, the
plugin works to:

1. help the intended reader care about the problem;
2. make the central claim, contribution, and evidence path unmistakable;
3. tell the clearest and most persuasive story supported by all claim-relevant evidence;
   and
4. keep defensive prose accurate, local, and no more prominent than necessary.

It is a skills-only plugin, not a standalone CLI, LaTeX builder, literature database, or
deterministic paper generator. It can verify the reader-facing realization in the paper;
an actual reader effect requires reader or reviewer feedback. Results depend on the
paper artifacts, available tools, and the host model following the skill contract.

## Use

Invoke the installed skill explicitly for predictable routing:

```text
$yxj-paper-os:yxj-paper-os Assess the paper's claim and contribution. Do not edit files.
$yxj-paper-os:yxj-paper-os Design a stronger reader-facing argument. Do not edit files.
$yxj-paper-os:yxj-paper-os Revise the paper from reviewer.md, update every materially affected surface, build the PDF, and verify the rendered result.
$yxj-paper-os:yxj-paper-os Audit claim/result/figure consistency. Report only.
```

Provide or identify the manuscript, rendered PDF, local scientific evidence, figures,
references or exemplars, and author/reviewer feedback. Use an explicit edit verb such as
`revise`, `rewrite`, `apply`, `fix`, or `update` when writeback is intended.

| Mode | Effect |
|---|---|
| `assess` | Inspect and report; never edit. |
| `design` | Resolve the story or display design; edit only when explicitly asked. |
| `revise` | Edit requested artifacts, close all affected surfaces, and verify. |
| `audit` | Inspect and report; repair only with explicit edit authorization. |

The bundled `skills/yxj-paper-os/assets/PAPER_BRIEF.md` is a read-only template. Copy it
to the paper root only when a current constraint cannot be recovered safely from the
paper, evidence, feedback, or Git. Do not use it as a production log.

## Verify this plugin

```bash
python3 -m unittest discover -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Release or install from a clean export or clean clone. Do not package the developer
working tree with `.git/`, `.omx/`, caches, logs, or build outputs.
