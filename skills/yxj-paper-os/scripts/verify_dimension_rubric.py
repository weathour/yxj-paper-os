#!/usr/bin/env python3
"""Validate the yxj-paper-os internal D00-D19 dimension rubric.

This is a structural development check. It does not judge academic adequacy,
search citations, execute external skills, or change the public workspace schema.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent
RUBRIC = ROOT / "references" / "00-dimension-rubric.md"
SKILL = ROOT / "SKILL.md"
TEMPLATES = ROOT / "assets" / "templates"
INDEX_TEMPLATE = TEMPLATES / "00_DIMENSION_INDEX.md"
VALIDATOR = ROOT / "scripts" / "verify_design_pack.py"
TASK_PLAYBOOKS = [
    ROOT / "references" / "00-project-route.md",
    ROOT / "references" / "01-materials-inventory.md",
    ROOT / "references" / "02-claim-evidence-boundary.md",
    ROOT / "references" / "03-writing-structure.md",
    ROOT / "references" / "04-design-pack-compiler.md",
]
EXPECTED_PLAYBOOK_NAMES = {path.name for path in TASK_PLAYBOOKS}
EXPECTED_REFERENCE_FILES = EXPECTED_PLAYBOOK_NAMES | {"00-dimension-rubric.md"}
EXPECTED_TEMPLATES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}
REQUIRED_IDS = [f"D{i:02d}" for i in range(20)]
EXPECTED_DIMENSION_NAMES = {
    "D00": "Workspace metadata",
    "D01": "Owner decisions",
    "D02": "Stale/readiness flags",
    "D03": "Project brief",
    "D04": "Target route profile",
    "D05": "Material inventory",
    "D06": "Evidence inventory",
    "D07": "Source and citation bank",
    "D08": "Research dossier",
    "D09": "Exemplar language profile",
    "D10": "Contribution options",
    "D11": "Claim-evidence map",
    "D12": "Wording boundary",
    "D13": "Limitation and risk matrix",
    "D14": "Reader spine",
    "D15": "Manuscript outline",
    "D16": "Object granularity",
    "D17": "Surface control",
    "D18": "Visual plan",
    "D19": "Writing design pack",
}
CRITICAL_STANDARD = "D04,D05,D06,D10,D11,D12,D13,D14,D15,D16,D17,D18"
REQUIRED_FIELDS = [
    "ID",
    "Name",
    "Dimension type",
    "Purpose",
    "Primary home / write target",
    "Owner/source of truth",
    "Minimum sufficiency",
    "Standard sufficiency",
    "Ideal sufficiency",
    "Agent may propose?",
    "Owner confirmation required?",
    "Ask prompts",
    "Candidate options pattern",
    "Status examples",
    "Stop / defer / reject rule",
    "Common failure modes",
    "Downstream handoff note",
]
QUESTION_DEPTH_LADDER_FIELDS = [
    "Dimension essence",
    "Minimum probe",
    "Standard probe",
    "Depth probe",
    "Conflict probe",
    "Weak-answer handling",
    "Stop condition",
    "Write-normalization rule",
    "Owner-confirmation rule",
    "Downstream consequence",
    "Mechanical gate intent",
]
RUBRIC_LADDER_INTERNAL_PHRASES = [
    "Every D00-D19 entry also carries exactly one internal question-depth ladder label set",
    "These ladder labels are internal guidance for agent questioning, sufficiency judgment, write normalization, and mechanical validation only",
    "they do not create public index columns, public statuses, public workspace files, public template fields, or manuscript prose",
]
PLAYBOOK_TRANSLATOR_PHRASES = [
    "central internal rubric/reference",
    "The central rubric decides sufficiency and question-depth",
    "This playbook translates the current rubric gaps into compact question cards and write landings",
    "must not duplicate or override the central D00-D19 ladder",
]
PLAYBOOK_TRANSLATOR_TABLE_HEADER = [
    "D ID(s)",
    "Default card mode",
    "Ask a depth follow-up when...",
    "Reconcile or conflict-check when...",
    "Write landing",
]
PLAYBOOK_COVERED_IDS = {
    "00-project-route.md": ["D01", "D03", "D04"],
    "01-materials-inventory.md": ["D05", "D06", "D07", "D08"],
    "02-claim-evidence-boundary.md": ["D10", "D11", "D12", "D13", "D16", "D17"],
    "03-writing-structure.md": ["D09", "D14", "D15", "D16", "D17", "D18"],
    "04-design-pack-compiler.md": ["D00", "D02", "D19"],
}
INDEX_COLUMNS = [
    "ID",
    "Dimension",
    "Current home",
    "Status",
    "Reason / owner note",
    "Pointer or handoff",
    "Blocks design pack?",
]
EXPECTED_STATUS_SET = {"filled", "not_applicable", "absent", "deferred", "rejected"}
FORBIDDEN_PUBLIC_SCHEMA_TERMS = {
    "tier",
    "minimum",
    "standard",
    "ideal",
    "currently_blocking",
    "currently blocking",
}
FIRST_BATCH_DIMENSIONS = ["D04", "D07", "D08", "D09", "D14", "D15", "D18", "D19", "D00", "D02"]
FIRST_BATCH_FIELD_LABELS = [
    "First-batch upgraded goal",
    "Field-category families / table intent",
    "Mechanical gate intent",
    "Cross-dimension dependencies",
    "Non-goals",
    "User-burden tier",
]
FIRST_BATCH_DIMENSION_PHRASES = {
    "D00": [
        "project slug",
        "owner/project identity",
        "created/updated timestamps",
        "last source revision",
        "readiness state",
        "ambiguity note",
        "semantic-adequacy disclaimer",
        "must not treat recent timestamps or completed metadata as semantic freshness or adequacy",
    ],
    "D02": [
        "Changed dimension",
        "affected pack section",
        "stale since",
        "recompile required",
        "owner decision",
        "required action",
        "semantic risk note",
        "obvious D19 incompatibility when structured stale data exists",
        "stale=false does not prove",
    ],
    "D04": [
        "Venue family",
        "article type",
        "content-fit intent",
        "format-fit intent",
        "reporting-fit intent",
        "primary audience",
        "reviewer expectation",
        "hard constraints",
        "forbidden routes",
        "owner confirmation state",
        "must not judge actual venue fit",
    ],
    "D07": [
        "source identity",
        "source role",
        "citation status",
        "owner confirmation",
        "locator such as DOI/URL/page/section/version",
        "key use",
        "limitation",
        "reuse permission",
        "handoff need",
        "source-to-claim support routes through D06 evidence anchors and D11 claim mapping",
    ],
    "D08": [
        "research/context boundary",
        "study-level notes",
        "theme-level synthesis",
        "conflict map",
        "gap hypothesis",
        "counterevidence",
        "unresolved source needs",
        "downstream consequence",
        "must not infer novelty",
    ],
    "D09": [
        "Exemplar status",
        "exemplar role",
        "positive style rules",
        "forbidden imitation",
        "voice/tense",
        "hedge strength",
        "terminology density",
        "banned patterns",
        "D12/D17 wording links",
        "must not judge prose quality, style similarity",
        "must not raise claim strength",
    ],
    "D14": [
        "Reader persona",
        "question sequence",
        "expected answer",
        "linked claim",
        "linked evidence",
        "linked limitation",
        "forbidden question",
        "transition rationale",
        "must not judge argument persuasiveness",
    ],
    "D15": [
        "Section",
        "job",
        "input dimensions",
        "output promise",
        "required evidence",
        "forbidden content",
        "length hint",
        "paragraph/function map",
        "downstream constraint",
        "must not judge rhetorical optimality",
    ],
    "D18": [
        "Visual id",
        "status such as existing/needed/deferred/absent",
        "story role",
        "linked claim",
        "linked evidence",
        "linked reader step",
        "data needed",
        "panel order",
        "legend job",
        "accessibility check",
        "handoff",
        "Needed/deferred visuals cannot support active claims",
        "must not validate figure quality, visual correctness",
    ],
    "D19": [
        "Dimension coverage",
        "submission blueprint",
        "semantic-risk note",
        "statement inventory",
        "supplement boundary",
        "external handoff routes",
        "unresolved dimension consequences",
        "validation notes",
        "must not claim manuscript, publication, submission, acceptance, or semantic readiness",
    ],
}
FIRST_BATCH_PLAYBOOK_PHRASES = {
    "00-project-route.md": [
        "## First-batch D04 route/profile pointer",
        "Separate owner-confirmed route from agent-inferred audience or reviewer expectation",
        "venue family, article type, content/format/reporting fit, primary audience, reviewer expectation, hard constraints, forbidden routes, and owner confirmation state",
        "D14 reader path, D15 section jobs, D18 visual format/storyline, and D19 submission blueprint",
        "must not judge actual venue fit, novelty, or acceptance likelihood",
    ],
    "01-materials-inventory.md": [
        "## First-batch D07/D08 source and dossier pointers",
        "source ≠ evidence ≠ claim",
        "cannot support or strengthen a claim unless a D06 evidence anchor exists and D11 maps the claim to that anchor",
        "source identity, source role, citation status, owner confirmation, locator/version or explicit absence, key use, limitation, reuse permission, and handoff need",
        "research/context boundary, study notes, theme synthesis, conflict map, gap hypothesis, counterevidence, unresolved source needs, and downstream consequence",
        "must not verify citation truth, source authority, novelty, or claim support",
    ],
    "02-claim-evidence-boundary.md": [
        "## First-batch cross-boundary reminder",
        "Sources, citation candidates, research dossier notes, exemplar/style guidance, design-pack summaries, and visual plans are not evidence anchors by themselves",
        "A claim may be supported only when D06 identifies a locatable evidence anchor and D11 maps the active claim to that anchor",
        "D09 can constrain style and D17 surface control; it cannot raise claim strength",
        "D18 can plan visuals; needed/deferred/absent visuals cannot support active claims",
        "D19 can summarize the boundary as a structural handoff",
    ],
    "03-writing-structure.md": [
        "## First-batch structure cards",
        "D09 style fingerprint",
        "exemplar status/role, positive style rules, forbidden imitation, voice/tense, hedge strength, terminology density, banned patterns, and D12/D17 wording links",
        "D14 reader spine",
        "reader persona, question sequence, expected answers, linked claim/evidence/limitation, forbidden questions, and transition rationale",
        "D15 section-job matrix",
        "input dimensions, output promise, required evidence, forbidden content, length or paragraph/function hints, and downstream constraints",
        "D18 visual storyline/brief",
        "visual id/type/status, story role, linked claim/evidence/reader step, data needed, panel order, legend job, accessibility check, and handoff",
        "must not judge prose quality, rhetoric, visual quality, or figure correctness",
    ],
    "04-design-pack-compiler.md": [
        "## First-batch D19/D02 handoff pointers",
        "D19 is a structural handoff/submission blueprint plus semantic-risk note",
        "dimension coverage, submission blueprint, statement inventory, supplement boundary, external handoff routes, unresolved dimension consequences, and validation notes",
        "D19 must not claim manuscript readiness, submission readiness, publication readiness, acceptance likelihood, novelty, citation truth, prose quality, visual quality, or semantic adequacy",
        "D02 stale gate should name category-family intent for changed dimension, affected pack section, stale since, recompile required, owner decision, required action, and semantic risk note",
        "A fresh D00/D02 state does not prove semantic adequacy",
        "stale/D19 incompatibility when explicitly structured",
        "must not execute external writing/citation/figure skills or score semantic quality",
    ],
}
MECHANICAL_BOUNDARY_PHRASES = [
    "structural",
    "does not judge",
]
FORBIDDEN_VALIDATOR_PROMISE_PATTERNS = [
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+(?:actual\s+)?venue fit\b", re.IGNORECASE), "venue fit"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+novelty\b", re.IGNORECASE), "novelty"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+source authority\b", re.IGNORECASE), "source authority"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+citation truth\b", re.IGNORECASE), "citation truth"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+bibliography correctness\b", re.IGNORECASE), "bibliography correctness"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+argument persuasiveness\b", re.IGNORECASE), "argument persuasiveness"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+prose quality\b", re.IGNORECASE), "prose quality"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+style similarity\b", re.IGNORECASE), "style similarity"),
    (re.compile(r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\s+visual (?:correctness|quality)\b", re.IGNORECASE), "visual correctness/quality"),
    (re.compile(r"\b(?:manuscript|submission|publication|acceptance) readiness (?:passed|validated|verified|certified|approved)\b", re.IGNORECASE), "readiness promise"),
]
SKILL_INTERACTION_PHRASES = [
    "Wake-up identity",
    "I prepare your paper project as six planning files and one writing design pack.",
    "User-facing phases",
    "Route → Materials → Claim/Evidence → Writing Structure → Handoff",
    "Interaction modes",
    "focused-question",
    "quick-form",
    "candidate-confirmation",
    "reconciliation",
    "stale-alert",
    "Question cards",
    "Agent action after answer",
    "omx question --input",
    "Markdown question cards remain the standalone fallback",
]
PLAYBOOK_CARD_PHRASES = [
    "## Question card pattern",
    "Current stage:",
    "Dimension / blocker:",
    "Why this matters:",
    "Mode chosen:",
    "Options:",
    "Agent action after answer:",
]
COMPILER_GATE_PHRASES = [
    "## Compile decision table",
    "D00-D19 missing",
    "Invalid status or placeholder",
    "Non-critical dimension reaches minimum",
    "Critical-standard dimension only reaches minimum",
    "Owner-gated route/claim/evidence/source/forbidden wording unconfirmed",
    "D16/D17 primary and claim-side statements conflict",
    "D04 route deferred",
    "D18 no visuals",
    "Final pack contains TODO/TBD/UNKNOWN/REPLACE_ME",
    "External writing/citation skill not executed",
    "Blocks design pack? = yes",
    "readiness-critical if unhandled",
    "D16/D17 canonical write rule",
    "03_WRITING_STRUCTURE.md#Object Granularity",
    "03_WRITING_STRUCTURE.md#Surface Control",
    "02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity",
    "reconciliation",
]
RUBRIC_INTERACTION_PHRASES = [
    "Question-card interpretation",
    "focused-question",
    "quick-form",
    "candidate-confirmation",
    "reconciliation",
    "stale-alert",
    "final-route deferral",
    "no-visual rationale",
]
SIX_TRACK_KEYS = {
    "front_matter_hook": "Front matter / hook",
    "intro_related_citation": "Introduction / related work / citation function",
    "method_reporting_repro": "Method / reporting / reproducibility",
    "results_visual_caption_accessibility": "Results / visual narrative / captions / tables / accessibility",
    "downstream_route_matrix": "Downstream route matrix",
    "templates_validators": "Templates + validators",
}
SIX_TRACK_RUBRIC_PHRASE_GROUPS = [
    (
        "front matter / hook track",
        [
            "Front matter / hook",
            "front-matter hook",
            "title, abstract, keywords, graphical/visual hook planning",
        ],
    ),
    (
        "intro / related / citation-function track",
        [
            "Introduction / related work / citation function",
            "Intro-related / citation function",
            "citation-function boundaries",
            "citation function such as",
            "CARS-style moves",
        ],
    ),
    (
        "method / reporting / reproducibility track",
        [
            "Method / reporting / reproducibility",
            "Method / reporting / repro",
            "reproducibility checklist",
            "method reporting",
        ],
    ),
    (
        "results / visual / captions / accessibility track",
        [
            "Results / visual narrative / captions / tables / accessibility",
            "Results / visual / captions / tables / accessibility",
            "figure/table/caption/statistics/accessibility handoff boundaries",
            "caption job",
            "caption/statistics/accessibility",
        ],
    ),
    (
        "downstream route matrix track",
        [
            "Downstream route matrix",
            "route to writing, polishing, citation, figure, review, data, PDF, backend/library",
            "without executing them",
        ],
    ),
    (
        "templates + validators track",
        [
            "Templates + validators",
            "Templates / validators",
            "mechanical validator/test expectations",
            "Template section/table presence",
            "required sections/tables/rows exist",
        ],
    ),
    (
        "six-track D00-D19 mapping",
        [
            "Six-track writing-surface crosswalk",
            "Likely existing dimensions / playbooks",
            "Primary dimensions",
            "Track | Likely existing dimensions",
            "maps them to existing D00-D19",
            "existing D00-D19",
        ],
    ),
]
SECOND_BATCH_PLAYBOOK_PHRASE_GROUPS = {
    "00-project-route.md": [
        ("front-matter route constraints", ["front-matter route constraints", "Front matter / hook constraints", "Front Matter / Hook Route Constraints"]),
        ("abstract/keyword/reporting implication", ["abstract/keyword/reporting", "abstract", "keywords"]),
        ("reporting statement prompts", ["reporting/statement", "statement inventory", "reporting guideline", "Reporting and reproducibility route seed"]),
    ],
    "01-materials-inventory.md": [
        ("citation-function buckets", ["citation-function", "citation function"]),
        ("related-work synthesis", ["related-work synthesis", "related-work notes"]),
        ("method/repro materials", ["method/repro materials", "Method / reporting / reproducibility checklist materials", "reproducibility materials"]),
        ("result/table/caption/accessibility materials", ["result/table/caption/accessibility", "Results / visual / caption / table / accessibility materials", "caption/accessibility"]),
    ],
    "02-claim-evidence-boundary.md": [
        ("intro gap/claim boundaries", ["intro gap/claim", "introduction gap", "citation-function claim"]),
        ("method/result claim boundaries", ["method/result claim", "method claim", "result claim"]),
        ("caption/result overclaim prevention", ["caption/result overclaim", "caption overclaim", "result overclaim"]),
    ],
    "03-writing-structure.md": [
        ("front-matter hook brief", ["front-matter hook", "Front matter / hook brief", "Front-Matter Hook Brief"]),
        ("intro move sequence", ["intro/related-work move", "intro move sequence", "related-work move"]),
        ("method/reporting jobs", ["method/reporting jobs", "Method / reporting / reproducibility section jobs", "Method / Reporting Section Jobs"]),
        ("results narrative", ["results narrative", "result narrative path", "Results Narrative Path"]),
        ("caption/table/accessibility prompts", ["caption/table/accessibility", "caption / table / accessibility", "accessibility prompts"]),
    ],
    "04-design-pack-compiler.md": [
        ("downstream route matrix", ["downstream route matrix", "Downstream Route Matrix"]),
        ("six-track handoff sections", ["six-track handoff", "Six-Track Coverage"]),
        ("front-matter hook constraints", ["front-matter hook constraints", "Front matter / hook packet", "front-matter handoff"]),
        (
            "intro/related/citation-function handoff",
            ["intro/related/citation-function handoff", "Intro / related / citation-function packet", "citation-function handoff"],
        ),
        (
            "method/reporting/repro checklist",
            ["method/reporting/repro checklist", "Method / reporting / reproducibility packet", "reproducibility checklist"],
        ),
        (
            "results/visual/caption/accessibility state",
            ["results/visual/caption/accessibility", "Results / visual / caption / table / accessibility packet", "caption/accessibility state"],
        ),
    ],
}
SECOND_BATCH_TEMPLATE_PHRASE_GROUPS = {
    "00_PROJECT_ROUTE.md": [
        ("front-matter route constraints", ["Front Matter / Hook Route Constraints", "Front-Matter Route Constraints", "front-matter route constraints"]),
        ("reporting statements", ["Reporting, Statements, and Downstream Route Seed", "Reporting and Statement", "statement inventory"]),
    ],
    "01_MATERIALS_INVENTORY.md": [
        ("citation-function notes", ["Citation Function", "citation-function"]),
        ("method/repro materials", ["Method / Reporting / Reproducibility Materials", "Method Reporting and Reproducibility", "reproducibility materials"]),
        ("result/caption/accessibility materials", ["Results / Visual / Caption / Accessibility", "Results / Visual / Caption / Accessibility Materials", "caption/accessibility"]),
    ],
    "02_CLAIM_EVIDENCE_BOUNDARY.md": [
        ("intro/method/result claim boundaries", ["Writing-Surface Claim Boundary Matrix", "Intro / Method / Result Claim Boundaries", "caption/result overclaim"]),
    ],
    "03_WRITING_STRUCTURE.md": [
        ("front-matter hook brief", ["Front-Matter / Hook Planning Brief", "Front-Matter Hook Brief", "front-matter hook"]),
        ("intro/related move sequence", ["Introduction / Related-Work Move Sequence", "Intro / Related-Work Move Sequence", "intro move sequence"]),
        ("method/reporting jobs", ["Method / Reporting / Reproducibility Job Plan", "Method / Reporting Section Jobs", "method/reporting jobs"]),
        ("results/caption/accessibility plan", ["Results Narrative / Caption / Accessibility Plan", "Results / Caption / Accessibility Plan", "caption/accessibility"]),
    ],
    "04_WRITING_DESIGN_PACK.md": [
        ("six-track coverage table", ["Six-Track Coverage", "Track | Input planning field locations", "Track | Dimension IDs"]),
        ("downstream route matrix", ["Downstream Route Matrix", "Downstream route", "External route category"]),
    ],
}
FORBIDDEN_SOURCE_PROMISE_PATTERNS = [
    (
        re.compile(
            r"\bclaim(?:s|ed|ing)?\s+(?:semantic[-\s]+adequacy|semantic[-\s]+readiness|paper\s+quality|"
            r"manuscript[-\s]+quality|manuscript[-\s]+readiness|actual\s+venue\s+fit|venue\s+fit|novelty|"
            r"source\s+authority|citation\s+truth|bibliography\s+correctness|argument\s+persuasiveness|"
            r"prose\s+quality|style\s+similarity|visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
            r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^.\n|;:]{0,60}"
            r"\b(?:semantic[-\s]+adequacy|paper\s+quality|manuscript[-\s]+quality|actual\s+venue\s+fit|venue\s+fit|"
            r"semantic[-\s]+readiness|manuscript[-\s]+readiness|novelty|source\s+authority|citation\s+truth|"
            r"bibliography\s+correctness|argument\s+persuasiveness|"
            r"prose\s+quality|style\s+similarity|visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b",
            re.IGNORECASE,
        ),
        "semantic scoring promise",
    ),
    (
        re.compile(
            r"\b(?:manuscript|submission|publication|acceptance|semantic)[-\s]+readiness\b"
            r"[^.\n|;:]{0,60}\b(?:passed|validated|verified|certified|approved|ready)\b|"
            r"\b(?:ready\s+for\s+submission|publication\s+ready|acceptance\s+likely)\b",
            re.IGNORECASE,
        ),
        "readiness promise",
    ),
]
CLAUSE_SPLIT_RE = re.compile(r"[|;:：.。\n]+|\bbut\b", re.IGNORECASE)
NEGATED_BOUNDARY_RE = re.compile(
    r"\b(?:no|not|never|without|forbid(?:s|den)?|forbidden|avoid|do\s+not|does\s+not|must\s+not|cannot|can't|is\s+not|are\s+not)\b",
    re.IGNORECASE,
)
NEGATED_FORBIDDEN_PROMISE_RE = re.compile(
    r"\b(?:(?:do|does|did|must|should|will|can)\s+not|cannot|can't|never|without|forbid(?:s|den)?|forbidden)\b"
    r"[^|;:.\n]{0,80}?\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|"
    r"manuscript[-\s]+(?:quality|readiness)|actual\s+venue\s+fit|venue\s+fit|novelty|"
    r"source\s+authority|citation\s+truth|bibliography\s+correctness|argument\s+persuasiveness|"
    r"prose\s+quality|style\s+similarity|visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\bnot\s+(?:a\s+)?(?:proof|evidence|certification|confirmation)\s+of\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:not|never)\s+(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:do|does|did|must|should|will|can)\s+not\s+"
    r"(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:cannot|can't|without|avoid|forbid|forbids|forbidden|remove|reject|rejected)\b[^|;:.\n]{0,80}?"
    r"\b(?:validat(?:e|es|ed|ing)|verif(?:y|ies|ied|ying)|judg(?:e|es|ed|ing)|scor(?:e|es|ed|ing)|certif(?:y|ies|ied|ying)|prov(?:e|es|ed|ing)|assess(?:es|ed|ing)?|impl(?:y|ies|ied|ying)|infer(?:s|red|ring)?|treat(?:s|ed|ing)?)\b[^|;:.\n]{0,80}?"
    r"\b(?:semantic[-\s]+(?:adequacy|readiness)|paper\s+quality|manuscript[-\s]+(?:quality|readiness)|"
    r"actual\s+venue\s+fit|venue\s+fit|novelty|source\s+authority|citation\s+truth|"
    r"bibliography\s+correctness|argument\s+persuasiveness|prose\s+quality|style\s+similarity|"
    r"visual\s+(?:correctness|quality)|acceptance\s+likelihood)\b|"
    r"\b(?:no|without)\b[^|;:.\n]{0,80}?\b(?:semantic\s+scor(?:e|er|ing)|readiness\s+certification|"
    r"publication\s+readiness|submission\s+readiness|acceptance\s+prediction)\b",
    re.IGNORECASE,
)


def section_for_id(text: str, dim_id: str) -> str:
    pattern = re.compile(rf"^### {re.escape(dim_id)}\b.*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    next_match = re.search(r"^### D\d{2}\b", text[match.end() :], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[start:end]


def markdown_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(cell and set(cell) <= {"-", ":", " "} for cell in cells)


def parse_first_table(text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    marker = f"## {heading}"
    pos = text.find(marker)
    if pos == -1:
        return [], []
    rest = text[pos + len(marker) :]
    table_lines: list[str] = []
    for line in rest.splitlines():
        stripped = line.strip()
        if not table_lines:
            if stripped.startswith("|"):
                table_lines.append(stripped)
            continue
        if stripped.startswith("|"):
            table_lines.append(stripped)
            continue
        break
    if not table_lines:
        return [], []
    header = markdown_table_cells(table_lines[0])
    rows = []
    for line in table_lines[1:]:
        cells = markdown_table_cells(line)
        if is_separator_row(cells):
            continue
        rows.append(cells)
    return header, rows


def parse_first_table_header(text: str, heading: str) -> list[str]:
    header, _rows = parse_first_table(text, heading)
    return header


def validate_dimension_heading_inventory(rubric_text: str, errors: list[str]) -> None:
    ids = re.findall(r"^### (D\d{2})\b", rubric_text, re.MULTILINE)
    for dim_id in REQUIRED_IDS:
        count = ids.count(dim_id)
        if count != 1:
            errors.append(f"{dim_id}: rubric heading must appear exactly once; found {count}")
    unexpected = sorted(set(ids) - set(REQUIRED_IDS))
    for dim_id in unexpected:
        errors.append(f"{dim_id}: unexpected rubric heading outside D00-D19")
    if ids != REQUIRED_IDS:
        errors.append(f"rubric must contain headings D00-D19 exactly once and in order; found: {ids}")


def validate_question_depth_ladder(rubric_text: str, errors: list[str]) -> None:
    require_phrases("rubric ladder internal declaration", rubric_text, RUBRIC_LADDER_INTERNAL_PHRASES, errors)
    for dim_id in REQUIRED_IDS:
        section = section_for_id(rubric_text, dim_id)
        if not section:
            continue
        for field in QUESTION_DEPTH_LADDER_FIELDS:
            marker = f"**{field}:**"
            count = section.count(marker)
            if count != 1:
                errors.append(
                    f"{dim_id}: question-depth ladder label {field!r} must appear exactly once; found {count}"
                )


def validate_playbook_translator_guidance(playbook: Path, text: str, errors: list[str]) -> None:
    for phrase in PLAYBOOK_TRANSLATOR_PHRASES:
        if phrase not in text:
            errors.append(f"{playbook.name}: missing playbook translator/rubric-authority phrase: {phrase}")

    header, rows = parse_first_table(text, "Question-depth translator guide")
    if header != PLAYBOOK_TRANSLATOR_TABLE_HEADER:
        errors.append(f"{playbook.name}: Question-depth translator guide table columns changed; found {header}")
    if not rows:
        errors.append(f"{playbook.name}: missing compact question-depth translator table")
        id_cells = ""
    else:
        id_cells = "\n".join(row[0] for row in rows if row)
    for dim_id in PLAYBOOK_COVERED_IDS[playbook.name]:
        if not re.search(rf"\b{re.escape(dim_id)}\b", id_cells):
            errors.append(f"{playbook.name}: translator table missing covered dimension {dim_id}")

    if all(label in text for label in QUESTION_DEPTH_LADDER_FIELDS):
        errors.append(
            f"{playbook.name}: duplicates the complete eleven-label question-depth ladder; "
            "keep the full ladder only in 00-dimension-rubric.md"
        )


def require_phrases(label: str, text: str, phrases: list[str], errors: list[str]) -> None:
    for phrase in phrases:
        if phrase not in text:
            errors.append(f"{label}: missing required phrase: {phrase}")


def require_phrase_groups(label: str, text: str, groups: list[tuple[str, list[str]]], errors: list[str]) -> None:
    for group_label, alternatives in groups:
        if not any(phrase in text for phrase in alternatives):
            errors.append(f"{label}: missing required phrase group: {group_label} ({' | '.join(alternatives)})")


def has_unnegated_match(text: str, positive_pattern: re.Pattern[str], negated_pattern: re.Pattern[str]) -> bool:
    masked = list(text)
    for match in negated_pattern.finditer(text):
        start, end = match.span()
        masked[start:end] = " " * (end - start)
    return bool(positive_pattern.search("".join(masked)))


def validate_forbidden_source_promises(label: str, text: str, errors: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("|"):
            continue
        if "**Common failure modes:**" in stripped:
            continue
        for clause in [part.strip() for part in CLAUSE_SPLIT_RE.split(stripped) if part.strip()]:
            for pattern, promise_label in FORBIDDEN_SOURCE_PROMISE_PATTERNS:
                if has_unnegated_match(clause, pattern, NEGATED_FORBIDDEN_PROMISE_RE):
                    errors.append(f"{label}:{line_number}: appears to make a forbidden {promise_label}")


def python_literal_assignment(source: str, name: str) -> object | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name:
                value = node.value
                if value is None:
                    return None
                try:
                    return ast.literal_eval(value)
                except (ValueError, TypeError):
                    return None
    return None


def validate_first_batch_rubric(rubric_text: str, errors: list[str]) -> None:
    for dim_id in FIRST_BATCH_DIMENSIONS:
        section = section_for_id(rubric_text, dim_id)
        if not section:
            errors.append(f"rubric missing first-batch dimension section: {dim_id}")
            continue
        for field in FIRST_BATCH_FIELD_LABELS:
            if f"**{field}:**" not in section:
                errors.append(f"{dim_id}: missing first-batch field label: {field}")
        require_phrases(f"{dim_id} first-batch coverage", section, FIRST_BATCH_DIMENSION_PHRASES[dim_id], errors)


def validate_second_batch_surfaces(rubric_text: str, errors: list[str]) -> None:
    require_phrase_groups("rubric six-track coverage", rubric_text, SIX_TRACK_RUBRIC_PHRASE_GROUPS, errors)

    for playbook in TASK_PLAYBOOKS:
        if not playbook.is_file():
            continue
        text = playbook.read_text(encoding="utf-8")
        require_phrase_groups(
            f"{playbook.name} second-batch coverage",
            text,
            SECOND_BATCH_PLAYBOOK_PHRASE_GROUPS[playbook.name],
            errors,
        )
        validate_forbidden_source_promises(playbook.name, text, errors)

    for template_name, groups in SECOND_BATCH_TEMPLATE_PHRASE_GROUPS.items():
        template = TEMPLATES / template_name
        if not template.is_file():
            errors.append(f"missing template for second-batch coverage: {template}")
            continue
        text = template.read_text(encoding="utf-8")
        require_phrase_groups(f"{template_name} second-batch coverage", text, groups, errors)
        validate_forbidden_source_promises(template_name, text, errors)


def validate_mechanical_boundary(label: str, text: str, errors: list[str], *, scan_promises: bool = True) -> None:
    lower_text = text.lower()
    for phrase in MECHANICAL_BOUNDARY_PHRASES:
        if phrase not in lower_text:
            errors.append(f"{label}: missing mechanical-only boundary phrase: {phrase}")
    if not scan_promises:
        return
    for pattern, semantic_area in FORBIDDEN_VALIDATOR_PROMISE_PATTERNS:
        if pattern.search(text):
            errors.append(f"{label}: appears to promise semantic scoring for {semantic_area}")


def main() -> int:
    errors: list[str] = []

    if not RUBRIC.is_file():
        errors.append(f"missing rubric: {RUBRIC}")
        rubric_text = ""
    else:
        rubric_text = RUBRIC.read_text(encoding="utf-8")

    validate_dimension_heading_inventory(rubric_text, errors)

    for dim_id in REQUIRED_IDS:
        section = section_for_id(rubric_text, dim_id)
        if not section:
            continue
        for field in REQUIRED_FIELDS:
            if f"**{field}:**" not in section:
                errors.append(f"{dim_id}: missing required field label: {field}")
        expected_name = EXPECTED_DIMENSION_NAMES[dim_id]
        if f"**Name:** {expected_name}" not in section:
            errors.append(f"{dim_id}: Name must be current semantic dimension name {expected_name!r}")

    validate_question_depth_ladder(rubric_text, errors)

    if CRITICAL_STANDARD not in rubric_text:
        errors.append(f"rubric missing exact critical-standard set: {CRITICAL_STANDARD}")
    for required_phrase in [
        "not a public skill, not a sixth task playbook",
        "Non-critical dimensions still require at least `minimum` handling",
        "`ideal` never blocks",
        "Owner-gated facts, route decisions, contribution choices, claims, evidence anchors, source/citation facts, and forbidden routes require owner confirmation",
        "Do not add `minimum`, `standard`, `ideal`, or `tier` columns/statuses",
    ]:
        if required_phrase not in rubric_text:
            errors.append(f"rubric missing required invariant phrase: {required_phrase}")
    require_phrases("rubric interaction guidance", rubric_text, RUBRIC_INTERACTION_PHRASES, errors)
    validate_first_batch_rubric(rubric_text, errors)
    validate_second_batch_surfaces(rubric_text, errors)
    validate_forbidden_source_promises("00-dimension-rubric.md", rubric_text, errors)

    if not SKILL.is_file():
        errors.append(f"missing skill: {SKILL}")
    else:
        skill_text = SKILL.read_text(encoding="utf-8")
        for phrase in [
            "references/00-dimension-rubric.md",
            CRITICAL_STANDARD,
            "Do not add tier columns or tier status values",
        ]:
            if phrase not in skill_text:
                errors.append(f"SKILL.md missing rubric wiring phrase: {phrase}")
        require_phrases("SKILL.md interaction guidance", skill_text, SKILL_INTERACTION_PHRASES, errors)
        validate_forbidden_source_promises("SKILL.md", skill_text, errors)

    references_dir = ROOT / "references"
    actual_reference_files = {path.name for path in references_dir.glob("*.md")}
    if actual_reference_files != EXPECTED_REFERENCE_FILES:
        errors.append(
            "internal reference surface changed; expected central rubric plus five playbooks "
            f"{sorted(EXPECTED_REFERENCE_FILES)}, found {sorted(actual_reference_files)}"
        )
    actual_playbooks = actual_reference_files - {"00-dimension-rubric.md"}
    if actual_playbooks != EXPECTED_PLAYBOOK_NAMES:
        errors.append(
            "internal playbook surface changed; expected exactly five playbooks "
            f"{sorted(EXPECTED_PLAYBOOK_NAMES)}, found {sorted(actual_playbooks)}"
        )

    for playbook in TASK_PLAYBOOKS:
        if not playbook.is_file():
            errors.append(f"missing task playbook: {playbook}")
            continue
        text = playbook.read_text(encoding="utf-8")
        if "00-dimension-rubric.md" not in text:
            errors.append(f"{playbook.name}: missing rubric reference")
        validate_playbook_translator_guidance(playbook, text, errors)
        require_phrases(f"{playbook.name} question-card guidance", text, PLAYBOOK_CARD_PHRASES, errors)
        require_phrases(f"{playbook.name} first-batch guidance", text, FIRST_BATCH_PLAYBOOK_PHRASES[playbook.name], errors)
        header = parse_first_table_header(text, "Dimension IDs covered")
        if header and header != ["ID", "Dimension", "Home"]:
            errors.append(f"{playbook.name}: Dimension IDs covered table columns changed; found {header}")

    compiler = ROOT / "references" / "04-design-pack-compiler.md"
    if compiler.is_file():
        require_phrases(
            "04-design-pack-compiler.md compile gate guidance",
            compiler.read_text(encoding="utf-8"),
            COMPILER_GATE_PHRASES,
            errors,
        )

    actual_templates = {path.name for path in TEMPLATES.glob("*.md")}
    if actual_templates != EXPECTED_TEMPLATES:
        errors.append(f"template surface changed; expected {sorted(EXPECTED_TEMPLATES)}, found {sorted(actual_templates)}")

    if INDEX_TEMPLATE.is_file():
        index_text = INDEX_TEMPLATE.read_text(encoding="utf-8")
        header, rows = parse_first_table(index_text, "Dimension Status Index")
        if header != INDEX_COLUMNS:
            errors.append(f"00_DIMENSION_INDEX.md table columns changed; found {header}")
        for cell in header:
            normalized = cell.lower().replace("_", " ")
            if any(term == normalized for term in FORBIDDEN_PUBLIC_SCHEMA_TERMS):
                errors.append(f"00_DIMENSION_INDEX.md exposes forbidden public schema column: {cell}")
        for row in rows:
            if len(row) < 2:
                continue
            dim_id, dimension_name = row[0], row[1]
            expected_name = EXPECTED_DIMENSION_NAMES.get(dim_id)
            if expected_name is not None and dimension_name != expected_name:
                errors.append(
                    f"00_DIMENSION_INDEX.md row {dim_id}: Dimension must be current semantic name "
                    f"{expected_name!r}; found {dimension_name!r}"
                )
    else:
        errors.append(f"missing index template: {INDEX_TEMPLATE}")

    if VALIDATOR.is_file():
        validator_text = VALIDATOR.read_text(encoding="utf-8")
        status_set = python_literal_assignment(validator_text, "VALID_DIMENSION_STATUSES")
        if status_set != EXPECTED_STATUS_SET:
            errors.append(f"verify_design_pack.py valid status set changed unexpectedly: {status_set!r}")
        dimension_columns = python_literal_assignment(validator_text, "DIMENSION_COLUMNS")
        if dimension_columns != INDEX_COLUMNS:
            errors.append(f"verify_design_pack.py dimension index columns changed unexpectedly: {dimension_columns!r}")
        current_dimension_names = python_literal_assignment(validator_text, "CURRENT_DIMENSION_NAMES")
        if current_dimension_names != EXPECTED_DIMENSION_NAMES:
            errors.append(f"verify_design_pack.py current dimension names changed unexpectedly: {current_dimension_names!r}")
        six_track_keys = python_literal_assignment(validator_text, "SIX_TRACK_KEYS")
        if six_track_keys != SIX_TRACK_KEYS:
            errors.append(f"verify_design_pack.py six-track keys changed unexpectedly: {six_track_keys!r}")
        six_track_columns = python_literal_assignment(validator_text, "SIX_TRACK_COLUMNS")
        if six_track_columns != ["Track", "Input planning field locations", "Design-pack output location", "Boundary note"]:
            errors.append(f"verify_design_pack.py six-track columns changed unexpectedly: {six_track_columns!r}")
        downstream_route_columns = python_literal_assignment(validator_text, "DOWNSTREAM_ROUTE_COLUMNS")
        if downstream_route_columns != [
            "Downstream route",
            "Eligible input sections",
            "Constraints to pass forward",
            "Blocker / defer note",
        ]:
            errors.append(f"verify_design_pack.py downstream route matrix columns changed unexpectedly: {downstream_route_columns!r}")
        validate_mechanical_boundary("verify_design_pack.py", validator_text, errors)
        validate_forbidden_source_promises("verify_design_pack.py", validator_text, errors)
        normalized_validator = re.sub(r"\s+", " ", validator_text.lower())
        if (
            "semantic adequacy" in normalized_validator
            and "does not prove semantic adequacy" not in normalized_validator
            and "does not judge semantic adequacy" not in normalized_validator
        ):
            errors.append("validator appears to claim semantic adequacy")
    else:
        errors.append(f"missing validator: {VALIDATOR}")

    self_text = Path(__file__).read_text(encoding="utf-8")
    validate_mechanical_boundary("verify_dimension_rubric.py", self_text, errors, scan_promises=False)

    public_skills = sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))
    if [p.parent.name for p in public_skills] != ["yxj-paper-os"]:
        errors.append(f"expected exactly one public skill yxj-paper-os; found {[str(p) for p in public_skills]}")

    if errors:
        print("Dimension rubric validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Dimension rubric structural validation passed: {RUBRIC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
