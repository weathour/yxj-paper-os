# Forward cases

Run these as separate fictional paper requests using the current skill. All evidence
needed for each bounded task is below; do not search for real papers or operate on a
live manuscript. Use an isolated workspace for any requested output. Preserve the raw
inputs. For requests without edit authorization, answer without writing files. These
cases do not establish actual reader comprehension or rendered visual quality.

## 1. Section order

Request: Assess this tutorial outline and recommend a reader-friendly order. Do not edit.

Evidence: Section 2 defines a common input-output operator and response norm. Section 3
uses frequency-domain assumptions to derive a frequency certificate. Section 4 instead
uses dissipativity assumptions to derive an energy certificate. Both use Section 2;
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
