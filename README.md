# YXJ Paper OS

YXJ Paper OS is a skills-only Codex plugin for developing academic papers from existing
research, a draft, or a focused writing question. It brings the problem, contribution,
argument, evidence, displays and reader's route into a coherent account.

The skill offers four composable actions: position the work, design the whole-paper
architecture, develop the manuscript, and reread, revise and prepare the requested
deliverable. Start with the current task and move between these actions as the writing
and evidence develop. When Paper OS is invoked proactively during other work, it uses
`yxj-practice` to understand the user's purpose and choose appropriate analysis,
examples, drafting or execution.

Whole-paper design selects an organizing principle, develops parent and child units,
coordinates parallel branches and cross-section relations, and plans where evidence,
displays and synthesis belong. Section scale and detail follow the article's task;
existing good organization can be reused. The [organization reference](skills/yxj-paper-os/references/question-material-structure.md#whole-paper-architecture)
and [composition examples](skills/yxj-paper-os/references/composition-examples.md)
provide detailed methods and cases.

The skill preserves four manuscript prohibitions across titles, abstracts, text,
appendices and displays: defensive or formulaic expression, work logs in place of
scientific argument, internal labels or unsupported names, and redundant material
without a role. It explicitly prohibits the “not X, but Y” formula and its variants.
Scientific conditions, meaningful limitations, negative results, established terminology
and purposeful repetition retain their roles; see [authorial style](skills/yxj-paper-os/references/authorial-style.md).

Language statistics and journal comparisons are selected for the task or existing
project requirements. Previously adopted metrics, thresholds and counting definitions
remain in effect; a complete statistics package or five-paper reference cohort is not
automatically required for each manuscript. [Language analysis](skills/yxj-paper-os/references/academic-language-comparison.md)
and [venue calibration](skills/yxj-paper-os/references/venue-calibration.md) describe
the available methods.

## Use

Ask naturally, for example:

- “Help me design a review around the relationship between these definitions.”
- “Revise this section while keeping the mathematical assumptions and evidence intact.”
- “Use the existing manuscript and reviewer feedback to prepare a submission-ready draft.”
- “Compare sentence patterns in these papers using the specified statistics.”

The skill can also be invoked explicitly as `$yxj-paper-os:yxj-paper-os`. Supply or
identify the relevant manuscript, scientific evidence, author choices and project or
venue requirements. Existing project records and the optional bundled
[Paper Brief](skills/yxj-paper-os/assets/PAPER_BRIEF.md) can retain adopted choices;
the plugin does not create a separate workflow-state system.

## Host resources

This package contains the `yxj-paper-os` skill, its references, the optional brief and
its supplemental language term list. It does not bundle companion skills, a literature
library, a statistics CLI or manuscript build tools.

For proactive Paper OS use, the host must also provide `yxj-practice` and make the
relative `../yxj-practice/SKILL.md` link from Paper OS resolve. Depending on the task,
other referenced skills include `yxj-chinese-expression`, `thesis-figure-skill`,
`paper-topic-incubation`, `yxj-backend` and `paper-deep-research`; the host supplies
these alongside Paper OS when they are needed.

Some example routes and source analyses point to the author's local `yxj-wiki` library
through absolute or workstation-relative paths. The optional language-statistics CLI
also lives outside this package. These paths are local resources, not bundled examples
or tools; provide equivalent accessible resources and adjust the paths for another host.
The bundled guides can still be used for the writing decisions they explain.

## Verify this plugin

```bash
python3 -m unittest discover -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/yxj-paper-os
```

The automated checks cover package structure and bundled resource links. The
[behavioral cases](tests/behavioral_cases.md) are fictional requests for a separate,
scoped forward pass; they do not establish model behavior for every paper.
