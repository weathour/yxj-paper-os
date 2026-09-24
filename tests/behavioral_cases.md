# Forward cases

Run these as separate fictional paper requests using the current skill. All evidence
needed for each bounded task is below; do not search for real papers or operate on a
live manuscript. Use an isolated workspace for any requested output. Preserve the raw
inputs. For requests without edit authorization, answer without writing files. These
cases do not establish actual reader comprehension or rendered visual quality.

## 1. Section order

Request: Assess this tutorial outline and recommend a reader-friendly order. Do not edit.

Evidence: Section 2 defines a common input-output operator and response norm. Section 3
uses frequency-domain assumptions to derive a gain bound. Section 4 instead
uses dissipativity assumptions to derive an energy bound. Both use Section 2;
neither uses the other. They enable different comparisons, and the intended readers are
more familiar with energy methods. Section 5 compares their applicability; Appendix A
contains reproducibility details. A colleague says Sections 3 and 4 can be swapped.

## 2. Branch relations

Request: Design the relationships and labels for this overview figure; do not draw it.

Evidence: A common model feeds a delay bound, a disturbance bound, and a heterogeneity
bound. Each bound can be used independently when its own assumptions hold. An application
may combine any subset if the relevant assumptions are compatible. The current sketch
uses an exclusive-choice diamond and rejoins all branches at a box labeled "mandatory
combined certificate". The reader first wants to locate the bound for their objective.

## 3. Joint conditions

Request: Assess whether this theorem diagram should become a set of optional routes.

Evidence: The only proved result is (A AND B) implies C. There is a counterexample to
A alone implying C, and another to B alone implying C. The current figure sends A and B
to a common junction and then C. A reader asks to navigate from desired conclusion C
to the conditions they must check.

## 4. Defensive prose

Request: Rewrite the following paragraph in revised.md with a more direct account of
the result. Keep the science unchanged; this is a standalone prose task with no PDF.

Evidence: Across 12 simulated routes, median tracking error falls by 18% relative to
controller B when delay is at most 40 ms. Above 40 ms, two runs diverge. There are no
hardware tests. The study estimates no population-level significance.

Paragraph: We do not claim to solve tracking in general. It should be emphasized that
our work is only a simulation study, and we cannot promise improvement everywhere.
Nevertheless, our method obtains an 18% lower median tracking error than controller B
across 12 routes when delay is at most 40 ms. Two runs diverge above this threshold.
It is important to stress once again that this is not a universal solution and we make
no claim of hardware validation.

## 5. Negative result

Request: Write a short abstract contribution paragraph in revised.md from this result.
This is a standalone text draft, with no full manuscript or rendered output.

Evidence: A proof establishes that no static gain in the defined class can satisfy both
uniform disturbance attenuation and the specified headway constraint for all chain
lengths under assumptions H1-H3. It says nothing about dynamic controllers or gains
outside the class. No successful alternative controller has been constructed or tested.

## 6. Figure bundle

Request: Audit whether these section headings and figures communicate the supplied
scientific argument. Do not edit or generate artwork.

Evidence: The paper's contribution is a proved interface lemma M connecting measurable
signal A to certificate B, enabling conditional prediction C. Existing papers supply
A's measurement method and B's definition; this paper proves M and tests C under M's
assumptions. The manuscript proves M in Section 3, but no supplied figure or caption
mentions M or the conditions for applying it.

Visible surfaces: Sections are "Measurement", "Framework", and "Experiments". Figure 1
shows A's measurement apparatus. Figure 2 shows the definition of B. Figures 3 and 4
show two views of prediction accuracy C. Each figure is individually accurate and
legible. All captions name only the illustrated quantities.

## 7. Local edit

Request: Only revise this one sentence for clarity and save it as revised.md. Do not
restructure the paper or create planning documents. This is a standalone text task.

Sentence: For all N greater than or equal to 2, under A1-A3, the bound is independent
of N, while the experiments evaluate only N=5 and N=10.

## 8. Discussion only

Request: Discuss how to improve this paper's writing approach. Do not apply changes yet.

Evidence: The current plan begins every section with "we do not claim" and has a
mandatory sequence of independent methods. The source manuscript.md is authoritative.
The author has not settled a new outline or requested persistent design notes. In an
earlier conversation they considered rewriting the introduction but never authorized it.

## 9. Chinese prose already fit for its purpose

Request: 检查下面的方法说明是否自然。只有存在实际表达问题时才改写，直接答复，不写文件。

Evidence: The author has approved concise formal Chinese. The procedure genuinely first
computes a feasible set and then selects a gain from that set. This is a standalone
methods passage, without a target journal or missing scientific inputs.

Passage: 首先计算可行域，再在其中选择增益。所有试验均采用相同的采样间隔。

## 10. English technical focus

Request: Assess whether this methods passage needs more natural English. Explain only
necessary changes and do not edit files.

Evidence: The objects have already been defined. The subsection reports the acquisition
settings and measured output, not who operated the equipment. The author prefers the
existing formal register; all facts below are supported.

Passage: The sampling interval was fixed at 20 ms. The output noise spectrum was
estimated from 30 repeated measurements.

## 11. Concrete Chinese results with an adverse finding

Request: 将下面的结果段改得自然、具体，保留证据边界，保存为 revised.md。
这是独立段落任务，不需要全文或PDF。

Evidence: On dataset A, method M has mean absolute error 0.8 and estimator B has 1.0.
On dataset C, method M has mean absolute error 1.2 and estimator B has 1.0. No
significance test, causal analysis, or deployment evaluation has been performed.

Passage: 本研究构建了一个全面而强大的框架，展现出卓越的预测性能。
该方法在多个数据集上体现了广泛的适用性，为实际部署提供了坚实基础。

## 12. Bilingual uncertainty and causal limits

Request: Translate this discussion passage into natural academic English and save it
as revised.md. This is a standalone text task; do not change its evidential strength.

Evidence: An observational study reports an association. It does not identify causal
direction or rule out unmeasured confounding. The tested group difference did not reach
statistical significance; no equivalence test was performed.

Passage: 该相关性提示二者可能有关，但不能据此确定因果方向，也不能排除未测量混杂的影响。
两组差异未达到统计显著水平；这不意味着两组等效。

## 13. Author and cited-source roles

Request: Revise this paragraph for author voice in revised.md. It is part of our paper,
not a review of it. Preserve source attribution and do not add claims.

Evidence: Lee [12] introduced estimator B. Our study compared B with M on two datasets;
no causal mechanism was investigated. The author uses "we" for our research choices
but keeps prior results attributed to their original authors.

Passage: The authors introduced estimator B [12]. The authors then compared B with M
on two datasets, offering profound insights into the underlying causal mechanisms.

## 14. Two approved voices for the same facts

Request: Draft one English paragraph for each of two independent authors using their
approved sample and audience. Save a.md and b.md. Do not copy the sample's facts into
the new text; no full manuscript or PDF is needed.

Shared new evidence: Under H1-H3, the proved bound holds for every N >= 2 and is
independent of N. The only numerical checks are N=8 and N=16; these checks are not
the proof of the all-N result.

Author A: Writes compact result-first prose for specialists. Approved sample:
"Under A1, the estimate is uniform in time. The constant depends only on the initial energy."

Author B: Writes explanatory tutorials for readers who need the distinction between
a theorem and numerical evidence spelled out. Approved sample:
"We first separate the model assumption from the observation. The assumption defines
the case being studied; the observation tells us what happened within that case."

## 15. Terminology during figure design

Request: 为这张概览图拟定中英文节点名称，并解释需要调整的用词。只讨论设计，不绘图、不改文件。

Evidence: Section 2 derives a deterministic upper bound on an input-output gain.
Section 3 derives a data-dependent upper confidence bound for a fixed unknown gain.
Section 4 explicitly defines a Lyapunov certificate as a matrix satisfying the stated
inequality; the author has approved that term. These methods are optional alternatives
under their own assumptions. The current sketch calls all three nodes "certificate /
证书" because a planning note calls the common reader task "certificate lookup".
No source establishes that this umbrella term is a disciplinary convention.

## 16. Consequential wording with unchanged equations

Request: Correct the English and Chinese prose in revised.md using the supplied
mathematics. Keep the equations and scope unchanged. This is a standalone passage;
no full manuscript, figure, or PDF is needed.

Evidence: Under A1-A3, each fixed size N has a finite response-gain upper bound g_N.
No bound independent of N or matching lower bound has been established.

Equation: For every N >= 1, ||T_N|| <= g_N < infinity.

English: Under A1-A3, this gives the exact gain g_N uniformly over all sizes. The
unchanged equation confirms that the wording preserves the mathematics.

Chinese: 在 A1-A3 下，该式给出了对所有规模一致的精确增益 g_N。
由于公式未变，用词调整不会改变数学含义。

Run this second passage separately under the same request:

Evidence: The feature map psi is fixed before sampling. Its input x_k, the regressor
phi_k = psi(x_k), the dataset, and the estimator are random. No conditioning on a realized
dataset is imposed in this passage.

Equation: phi_k = psi(x_k).

English: With fixed features, the regression vectors and estimated model are fixed;
only the response noise is random.

Chinese: 特征固定后，回归向量与估计模型也固定，只有响应噪声是随机的。

## 17. Contribution and reader uses

Request: Propose a contributions paragraph and an intended-readers-and-use paragraph
for Paper A. Then explain how Paper B's contribution statement should differ. Discuss
only; do not edit files or search for sources.

Evidence: Paper A organizes established definitions, compares their assumptions and
bounds, and explains how existing identification and robustness estimates fit together.
Its source audit attributes all these results to prior work; its derivations expose
connections in a common notation. The author has adopted this synthesis identity.
The intended audience includes newcomers, researchers comparing models and methods,
and engineers interpreting simulations or experiments. The current draft says:
"Our main advance is a new finite-data method. Readers can use it to accept or reject
a controller against one prescribed gain limit."

Paper B is independent. It proves a new conversion theorem under H1-H3; the supplied
source comparison verifies that prior results do not cover that conversion. It also
contains a synthesis section for newcomers. Its numerical examples illustrate the
theorem and do not establish a controller-design improvement.

## 18. Compression and explanatory functions

Request: Assess the two proposed deletions below and recommend wording where needed.
Keep the author's supported purposes and mathematical scope. Do not edit files.

Evidence: The introduction says the paper connects definitions, analysis methods, and
model uncertainty. The body establishes conditional conversions between response
bounds, compares method assumptions, and explains finite-data uncertainty. The author
approved uses in learning the subject, choosing comparisons, and interpreting experiments.

Conclusion: Taken together, these connections let newcomers relate the definitions to
the responses they describe, let researchers compare methods under matched assumptions,
and help experimenters judge whether their disturbance and observation choices are
covered by a theoretical bound. They provide a common basis for interpreting reported
amplification across those settings.

Proposal A replaces the conclusion with: "We discussed definitions, methods, and model
uncertainty." Its rationale is that each subject already appeared in the introduction.

Elsewhere, two adjacent body sentences read: "The response bound is independent of N
under H1-H3. Under H1-H3, the response bound does not depend on N." There is no intervening
equation or reference, and the second sentence has no later cross-reference.
Proposal B deletes the second sentence.

## 19. Page budget and float placement

Request: Recommend the next layout variant from these supplied build and inspection
observations. Explain the tradeoff and any remaining verification; do not claim to have
built or inspected a PDF yourself. No files should be changed.

Evidence: The complete paper must fit 40 pages. Font size and margins are fixed; modest
figure display-size changes are allowed. A note deferring pagination belonged to a
completed figure-drafting round. The current 41-page PDF leaves the last conclusion
paragraph on a separate page before the appendix. Figure assets and captions are intact.

| Variant | Estimated saving in equivalent pages | Complete PDF | Supplied final-size inspection |
| --- | --- | --- | --- |
| Delete the conclusion's explanation of uses | 0.18 | 40 pages | Uses are no longer brought together at the close |
| Display figures at 96% width | 0.15 | 41 pages | Labels remain legible |
| Display figures at 92% width | 0.31 | 40 pages | Labels remain legible; conclusion retained |
| Display figures at 89% width | 0.42 | 40 pages | Small labels are difficult to read |

## 20. Journal requirements and template migration

Request: Assess whether the bibliography needs migration to the publisher template's
default implementation and estimate the kinds of edits involved. Discuss only.

Evidence: The supplied current official guide for this fictional journal and article
type requires APA 7 output at the relevant submission stage, without prescribing a
backend. The generic publisher template uses a different author-year style with BibTeX.
The current manuscript uses biblatex/Biber and meets the specified output format, except
that one journal record lacks an article number in both source and output.

The existing library contains journal articles with article numbers in eid, conference
papers with booktitle and pages, and preprints stored as online records. A supplied
temporary build with the template default drops the article numbers and fails to render
the preprints; the current build preserves these fields and types. Some published papers
use numbered citations, but no supplied instruction grants an exception to the guide.

Contrast case: For a different journal, the applicable guide requires numbered citations
while the current output is author-year. The current backend already supports the required
style; a supplied trial with that style preserves all record information.

## 21. Compression changes its own acceptance check

Request: Audit this compression patch and its revised check. Explain whether the
supplied evidence supports accepting it. Do not edit or run a paper build.

Evidence: The author requests a shorter review while retaining both method families,
their comparison, and known failure cases. The original cited set has 80 works. Source
R is the only documented support for family B's operating assumptions; source S reports
a counterexample to a comparison claim that remains in the conclusion. The patch cuts
the family B discussion and the counterexample, leaving 18 works. It changes the
coverage test's expected count from 80 to 18 and deletes its checks for R and S.
All revised checks pass and the requested page count is met. No author instruction
changes the retained comparison or its coverage requirements.

## 22. Authorized removal of an independent side branch

Request: Apply the approved scope reduction to the supplied manuscript and reference
snapshot in an isolated workspace. These Markdown artifacts are the complete deliverable;
there is no PDF. Preserve the remaining result and its limitation.

Evidence: The author explicitly removes the optional estimation extension to concentrate
on the comparison of methods A and B. References R and S fully support that comparison
and its limitation. T supports only the extension; no retained claim, proof, or comparison
depends on it. The snapshot tracks the cited set, not a minimum coverage requirement.

manuscript.md:
"This review compares methods A and B and develops an estimation extension.
Under H1-H3, A bounds the individual response while B bounds aggregate energy [R,S].
Neither comparison covers time-varying parameters [S].
The optional estimation extension supplies a separate sampling bound [T]."

reference_snapshot.json: {"cited_keys": ["R", "S", "T"], "count": 3}

## 23. Feedback diagnosis and proposed repair

Request: Assess these three editing suggestions against the current passage. Recommend
only changes justified by the supplied facts; do not edit files or request a new outline.

Evidence: The author has approved a synthesis review with the current introduction.
Under H1-H3, prior work proves the displayed bound for every N. The review makes no new
theorem claim. Experiments check only N=5 and N=10. H3 is necessary: a supplied
counterexample violates the bound without it. An old draft omitted the experimental
sizes; the current passage already includes them.

Passage: "Under H1-H3, the established bound holds for every N. The experiments evaluate
only N=5 and N=10. This establishes it."

Suggestions: (a) "This establishes it" has an ambiguous referent, so rewrite the whole
introduction as an original-theorem paper. (b) Add N=5 and N=10 to the passage.
(c) Remove H3 to make the sentence less defensive. These suggestions are described
as agreed by three reviewers, but no additional evidence is supplied.

## 24. Staged language revision and factual resumption state

Run the two requests sequentially in one isolated fictional project. All deliverables
are Markdown; no PDF or external service exists.

Repository instructions: en.md and zh.md are the two manuscript editions. STATUS.md
owns current completion facts. The paper contract preserves H1-H3 and the conclusion's
scope. Governance changes require separate authorization; routine factual status
maintenance is not reserved. Author acceptance has not been established.

en.md: "Under H1-H3, the response bound is independent of N. Under H1-H3, the response
bound does not depend on N."

zh.md: "在H1-H3下，响应界与N无关。在H1-H3下，响应界不依赖N。"

STATUS.md: "Both editions await removal of the adjacent duplicate sentence.
Author acceptance: pending."

First request: Remove the duplicate sentence from the English manuscript only. Leave
the Chinese manuscript for a later batch. Complete this English revision.

Second request, after inspecting the first result: Now synchronize the Chinese edition
with the English revision and complete that batch. No author-acceptance decision is added.

Contrast request in a fresh copy of the same starting project: Assess whether the
duplicate sentences should be removed. Do not apply changes or update project records.

## 25. Discovery as the principal contribution

Request: Design this paper's opening and contribution order. Give a short candidate
opening and explain the order; do not edit files or search for sources.

Evidence: The paper studies failures of a simulated tracking system under two disturbance
generators. The disturbances have the same marginal distribution and variance, but one
generator clusters large disturbances in time. Under the supplied fixed controller and
model, repeated independent runs show longer threshold-exceedance episodes for the
clustered generator. The comparison and uncertainty estimates support that finding only
for the tested model and settings. The closest-work comparison confirms that those works
report marginal disturbance variance without this temporal comparison. The simulation
method and controller are established; no new controller, general causal theorem, or
design rule has been developed. Readers know tracking error and disturbance variance but
may not distinguish the frequency of exceedance from the duration of an episode.

Current outline: New simulation framework; new theoretical law; engineering design.
Current contribution: "We provide a comprehensive framework for reliable tracking."

## 26. Repeated feedback and a proposed permanent rule

Request: Revise the opening in revised.md using these facts. Maintain PAPER_BRIEF.md
only if this task adds a lasting adopted direction or genuine unfinished work. This
is a standalone text task with no rendered output.

Evidence: The intended readers are graduate control researchers. The paper establishes
an upper bound on disturbance amplification under H1-H3. Its opening introduces six
symbols before identifying the disturbance input and measured response. Twice the
author has said, "The opening is still hard to follow; help the reader understand what
the bound describes." A previous assistant proposed banning equations from all future
introductions. The author has not adopted that proposal or changed the intended readers.

opening.md: "Let H, G, W, V, N and gamma be given. Under H1-H3, ||G|| <= gamma.
G maps the disturbance input to the measured response."

PAPER_BRIEF.md: "## Current constraints\nWrite for graduate control researchers.\n"

## 27. Existing brief formats and current authorization

Request: Revise the duplicated sentence in manuscript.md and update the current task
entry in PROJECT_NOTE.md. Complete this local Markdown revision; no PDF is required.

Repository instructions: manuscript.md is canonical. PROJECT_NOTE.md is the canonical
brief; retain its existing prose headings, Decision and Next. Factual maintenance of
Next is authorized. The declared H1-H3 scope remains active.

manuscript.md: "Under H1-H3, the bound is independent of N. Under H1-H3, the bound
does not depend on N."

PROJECT_NOTE.md: "# Project note\n## Decision\nKeep H1-H3 explicit.\n## Next\nRemove
the duplicated bound sentence; completion means one supported statement remains.\n"

Contrast request in a fresh isolated workspace: Assess what remains to do from this
older PAPER_BRIEF.md and the same manuscript. Explain only; do not edit files.

PAPER_BRIEF.md: "## Current constraints\n| ID | Scope | Strength | Active constraint or stable author direction | Source or locator | Supersedes |\n|---|---|---|---|---|---|\n| D1 | Whole paper | hard | Keep H1-H3 explicit | Author | |\n## Open work\n- **Mode:** revise\n- **Latest explicit pending revision:** Remove the duplicated bound sentence.\n"

## 28. Explanatory proportion and evidence for the contribution

Request: Design a revised introduction opening and the explanation after the main result.
Recommend where to change the allocation of space and how to describe validation.
Discuss only, using the supplied evidence; no literature search or experiment is requested.

Evidence: The intended readers estimate signals from limited samples. They know the
standard least-squares setup. The paper proves that, under H1-H3, the estimation error
is at most C/sqrt(n) for each positive integer n, with a known positive C. Its verified
closest-work comparison supplies an asymptotic convergence result without a computable
finite-sample constant. The paper does not establish an optimal or necessary sample
size, better empirical performance than competing estimators, or validity without H3.
An independent computation at n=100 and n=400 agrees with the bound; that computation
does not establish the all-n result. A failed check without H3 is retained in the evidence.

Current structure: Three pages repeat the readers' standard setup. The main proof uses
one unfamiliar concentration step, stated without explanation. After the bound appears,
the only interpretation is "This establishes the effectiveness of our framework."
The opening says only "Signal estimation is important in many modern applications."
The validation paragraph says "Two successful examples prove universal reliability."
