# Complete Composition Examples

Use these cases when deciding or explaining organization, not as mandatory templates.
Read the case matching the current reader question. A prestigious venue does not make
an unrelated paper an appropriate model. These are selected cases, not evidence of how
frequently a venue uses a structure.

- [What makes an example complete](#what-makes-an-example-complete)
- [Review: a field map with explanatory depth](#review-a-field-map-with-explanatory-depth)
- [Method: a design that answers an observed difficulty](#method-a-design-that-answers-an-observed-difficulty)
- [Empirical: a claim tied to the experiment](#empirical-a-claim-tied-to-the-experiment)
- [Theory: distinguish achievable performance from limitations](#theory-distinguish-achievable-performance-from-limitations)
- [Broad readership: establish significance before architectural detail](#broad-readership-establish-significance-before-architectural-detail)
- [Display: preserve relationships while changing appearance](#display-preserve-relationships-while-changing-appearance)
- [Book-guided authored demonstrations](#book-guided-authored-demonstrations)
- [Transfer the work, not the template](#transfer-the-work-not-the-template)

## What makes an example complete

Match the example to the decision. A sentence needs enough preceding and following
context to explain its subject, comparison, or connective. A paragraph example includes
the entire paragraph; an abstract example includes the entire abstract. A section plan
names the actual sections, their distinct work, and how they connect. An example of a
transition includes both units it connects. Neither a list of rhetorical verbs nor a
fill-in skeleton demonstrates organization.

Recover the source's object, reason for writing, and content relationships before
borrowing wording. Keep three things distinguishable: source text with a precise
locator; analysis of its organization; and an explicitly labelled demonstration or
paraphrase. When full quotation is inappropriate, locate the original and supply a
complete attributed paraphrase or authored example. Never fabricate a quotation or
present a hypothetical draft as a published result. No new data are needed to teach a
writing choice. Delivered revised prose can itself be the complete example.

The international cases below use whole-paper functional outlines and complete short
demonstration paragraphs, not verbatim quotations or translations. Their source-reading
scope is specified. They illustrate organization, not a fresh scientific audit.

## Review: a field map with explanatory depth

**Practice source.** The Chinese working review *车辆编队串稳定性研究综述*,
commit `7de986605`, project `vehicle-platoon-string-stability-operator-tutorial`.
Read `manuscript/jtysgcxb-zh/main.tex` and its six active section inputs.
This is a local revision case, not a published exemplar or whole-paper author acceptance.
The complete abstract and a technical paragraph are reproduced with analysis in
`yxj-chinese-expression/references/technical-writing.md`.

**Complete section arrangement and its reader path:**

| Section | Concrete job and connection |
|---|---|
| 0 引言 | Start with longitudinal disturbance propagation; locate car-following and cooperative-control traditions; explain why their performance claims need comparison. Promise a bounded review of that object. |
| 1 研究脉络与性能指标 | Connect the two traditions, then distinguish observed vehicles, response measures, and requirements across platoon sizes. Give the reader the vocabulary needed for subsequent comparisons. |
| 2 扰动传播与规模效应 | Explain how vehicle dynamics, spacing/information choices, communications, and heterogeneity affect propagation. These are interacting influences, not successive historical stages. |
| 3 串稳定性分析方法 | Compare the questions and conditions handled by frequency-domain, spectral, storage, and robust methods. Reuse the previous section's propagation questions without pretending all methods form one algorithm. |
| 4 运行性能解释与验证 | Relate mathematical performance to operating goals; distinguish what simulation, vehicle experiments, and finite observations can establish. Interpret the scope of the preceding theory. |
| 5 结语 | Synthesize the distinctions and derive research directions from limitations already explained in the body. |

**A complete local explanation, adapted from section 1.2:**

> Consider one scalar disturbance input and the same $L_2$ response measure throughout.
> The tail-vehicle gain observes one vehicle; the worst-vehicle gain selects the largest
> response; the unweighted aggregate gain combines all vehicles. If every vehicle has
> the same input–output map, the aggregate gain is $\sqrt{N}$ times the single-vehicle gain.
> Its growth can therefore reflect the number of responding vehicles even when their
> individual responses do not grow. Comparing scalability claims requires the input
> budget and output aggregation to remain explicit.

This paragraph gives the mathematical example a comparative purpose, then returns to
the field-level question. The formal inequality and conditions remain in the manuscript.
The appropriate lesson is this connection, not a ban on mathematical depth. Six sections,
eight figures, five tables, a citation target, or this draft's appendix length are local
choices. A specialist mathematical review may need a much longer technical argument.

## Method: a design that answers an observed difficulty

**Source:** He et al., *Deep Residual Learning for Image Recognition*, CVPR 2016.
[Published PDF](https://openaccess.thecvf.com/content_cvpr_2016/papers/He_Deep_Residual_Learning_CVPR_2016_paper.pdf),
§§1–4; paragraph basis: §3.1, p. 772; comparison: §4.1, Fig. 4 and Table 2.

**Whole-paper organization, paraphrased:** §1 identifies degradation as depth increases;
§2 locates residual representations and shortcuts in prior work; §3 develops residual
learning, shortcuts, architectures, and implementation; §4 tests ImageNet classification,
CIFAR-10 behavior, and object detection. The comparisons return to the motivating difficulty.

**Complete demonstration paragraph, authored from §3.1:**

> A deeper plain network can have higher training error than its shallower counterpart.
> Yet additional layers implementing the identity should preserve the shallower solution.
> This discrepancy motivates learning a residual $F(x)=H(x)-x$ and recovering the desired
> mapping as $F(x)+x$, when dimensions agree. If identity is appropriate, the residual can
> approach zero. This reasoning motivates the parameterization; it does not prove that
> every deeper residual network will optimize better. That expectation needs comparison
> with the corresponding plain network.

**Transfer:** link the design choice to the difficulty it addresses. Keep motivation
distinct from proof, and method explanation distinct from its experimental support.

## Empirical: a claim tied to the experiment

**Source:** Stern et al., *Dissipation of stop-and-go waves via control of autonomous
vehicles: Field experiments*, Transportation Research Part C, 2018.
[Version read: arXiv:1705.01693v1](https://arxiv.org/pdf/1705.01693v1), §§1–5 and Appendix;
paragraph basis: §§1.2, 4.2 and 5. [Publication](https://doi.org/10.1016/j.trc.2018.02.005).

**Whole-paper organization, paraphrased:** §1 motivates sparse vehicle control;
§2 establishes the experiment and procedure; §3 explains the controllers;
§4 defines metrics and compares experiments; §5 interprets benefits and further testing
needs. The appendix supplies vehicle specifications and oscillation-onset identification.

**Complete demonstration paragraph, authored from the specified sections:**

> The ring-road experiments ask whether controlling one vehicle can dampen waves formed
> by human drivers. The reported trajectories and performance measures show wave
> reduction under the tested conditions. However, improvements do not occur in every
> metric: throughput decreases in experiment C. The result supports the feasibility of
> sparse vehicle control in this setting. Quantifying benefits on multilane freeways
> requires further experiments that include lane-changing interactions.

**Transfer:** describe the comparison before interpreting it; retain a material exception
beside the benefit. Do not turn a field demonstration into a network-wide guarantee.

## Theory: distinguish achievable performance from limitations

**Source:** Bamieh et al., *Coherence in Large-Scale Networks: Dimension-Dependent
Limitations of Local Feedback*, IEEE TAC, 2012.
[Version read: arXiv:1112.4011v1](https://arxiv.org/pdf/1112.4011v1), organization in §§I–VII and appendix headings;
paragraph basis: §§II.C–III and IV–V.

**Whole-paper organization:** I motivates coherence; II defines models and assumptions;
III defines performance; IV gives achievable upper bounds; V establishes limitations;
VI interprets multiscale behavior; VII discusses related work and open questions.
Appendices supply Fourier identities, estimates, and calculations.

**Complete demonstration paragraph, authored from the specified sections:**

> On discrete tori, standard consensus algorithms provide attainable variance bounds.
> A limitation of the feedback class requires a lower bound as well. The analysis
> restricts feedback by spatial invariance, locality, symmetry, and bounded control
> effort; relative and absolute measurements must also be distinguished. Coordinate
> decoupling simplifies the formation problem. Matching asymptotic upper and lower
> bounds identifies a scaling limitation under these restrictions. Changing the output
> measure or feedback class requires reconsidering that conclusion.

**Transfer:** give definitions, assumptions, and bounds different jobs. Examples aid
interpretation; they do not replace a lower-bound proof or extend its quantifiers.

## Broad readership: establish significance before architectural detail

**Source:** Jumper et al., *Highly accurate protein structure prediction with AlphaFold*,
Nature, 2021. [Publisher full text](https://www.nature.com/articles/s41586-021-03819-2).
Read the main article through Discussion and the Methods entry; paragraph basis: Main,
the CASP14 explanation and results preceding “The AlphaFold network.”

**Whole-paper organization, grouped by function:** Main introduces the problem and
evaluations; the network sections explain architecture and training; interpretation
examines learned behavior and component contributions; related work and Discussion
position the result. Methods and Supplementary Methods carry implementation detail.
Benchmark evidence appears before the detailed architecture.

**Complete demonstration paragraph, authored from Main:**

> AlphaFold was evaluated in CASP14, a blind assessment using structures not publicly
> disclosed to participating methods. Its predictions were more accurate than those of
> competing methods in that assessment. Evaluation on PDB structures released after the
> training-data cut-off also tested performance beyond the competition targets. These
> results support accuracy on the assessed structures; reliability estimates further
> help distinguish predictions with different levels of confidence.

**Transfer:** results may orient readers before detailed methods when their meaning and
evidential basis are intelligible. This arrangement does not authorize hiding essential
conditions or imposing a short supplement on every research paper.

## Display: preserve relationships while changing appearance

**Practice source:** the review commit above, Figure 5 source
`figures/tutorial-v2-zh/F4_local_to_platoon_structure.tex` and `HANDOFF.md`.
The author found an enclosing frame unsuitable, then found the ungrouped revision too
scattered. The source revision restored local groups and explicit connections.

**Complete relationship example:** one common model splits into parameter settings
(a) output aggregation and (b) a selected channel. Setting (c) changes a gain in (b),
so its connection originates on the (b) branch. All three examples connect by an
undirected “condition comparison” link to the general criterion below. This is not
three serial operations or three examples proving a universal criterion.

**Authored explanatory caption:**

> The common input–output model is evaluated under two parameter settings. Panel (a)
> compares aggregate and tail responses; panel (b) contrasts a full inverse bound with
> a selected-channel bound. Panel (c) perturbs a gain in setting (b). The lower connection
> compares the examples with the analytical criterion; it does not denote a proof.

Scientific relationships determine grouping, connection origins, and arrow meaning.
Frame removal alone does not solve visual organization. This case records source-level
relations and actual author feedback, not a new PDF or final-size visual inspection.

## Book-guided authored demonstrations

These cases realize the conditional [four-book methods](writing-books.md). Except for
the short identified book quotation, their inputs and prose are authored teaching
examples. Their numbers and studies are hypothetical; they are neither published
observations nor the user's project evidence. Complete units show choices and protected
meaning. Use the matching case, not the whole set for every task.

### Question, theory plan, abstract and closing

**Input.** A hypothetical analysis gives an upper bound `B(f,u)` on error `E(f,u)` for
every admissible `f` in `F` and `u` in `U`. No exact-error equality, observed accuracy,
optimality, broad-model guarantee or literature-priority claim is supplied. Readers
need to understand what this bound permits them to decide. A topic-only draft says,
“We study error bounds with a mathematical framework.”

**Working question.** Which error-threshold decisions follow from the upper bound,
and which require information it does not provide? The conceptual consequence is a
correct interpretation of an available guarantee, without an invented application.

**Complete section plan.**

| Section | Job and connection |
|---|---|
| 1. Interpreting an error guarantee | Introduce the reader's decision and state the supported question. |
| 2. Admissible functions, inputs and error | Define `F`, `U`, `E`, `B` and the threshold before using the guarantee. |
| 3. From an upper bound to a decision | Establish the sufficient threshold implication from the supplied inequality; give its meaning. |
| 4. Information needed beyond that implication | Explain what an upper bound alone leaves undetermined; do not invent an unattainability proof. |
| 5. Examples of the decision | Illustrate the two logical cases; examples do not enlarge the quantified domain. |
| 6. What the guarantee provides | Synthesize the supported decision and the exact condition on its use. |

**Complete abstract.**

> An error bound supplies information for a threshold decision. We examine this
> interpretation for an error $E(f,u)$ and a bound $B(f,u)$ over stated classes of
> functions and inputs. The inequality $E(f,u)\leq B(f,u)$ gives a sufficient test:
> $B(f,u)\leq\varepsilon$ guarantees that the error meets the tolerance. When the
> bound exceeds the tolerance, the inequality alone leaves the error's threshold status
> undetermined. Separating these cases clarifies how to use the supplied guarantee and
> which decisions need additional information.

**Complete closing paragraph.**

> The upper bound provides a sufficient test for meeting the error tolerance over the
> stated function and input classes. Its usefulness depends on retaining those classes
> and the direction of the inequality. Decisions left open by the test require further
> information about the actual error or a tighter bound. This distinction keeps the
> mathematical guarantee and its use aligned.

**Choices and protected meaning.** C3–4/C8–11, W6–9/W18 and S7 turn a topic into an
answerable question and conceptual consequence. The plan separates definitions,
implication and interpretation. The abstract and closing promise the same result;
neither treats `B > epsilon` as a violation. This simple example teaches organization;
it does not establish a publishable research contribution or novelty.

### Method: explain why each operation answers the question

**Input.** On a stated compact domain `K`, a supplied valid Lipschitz constant is `L`.
The evaluated grid is contained in `K`; every point of `K` is within distance `h` of
a grid point, and `m` is the largest grid value. The resulting supremum interval is
`[m, m+Lh]`. No speed comparison
or empirical validation is supplied. The question is whether `sup_K f <= b`.

**Complete method paragraph.**

> We evaluate the function on a grid in $K$ whose covering distance is $h$ and denote the
> largest evaluated value by $m$. The supplied Lipschitz bound controls the values
> between grid points, giving $m\leq\sup_K f\leq m+Lh$. If $m+Lh\leq b$, the
> interval certifies the threshold condition; if $m>b$, a grid value establishes its
> violation. The remaining case is unresolved by this interval. Refining the grid
> reduces the interpolation allowance $Lh$, while the validity of the test continues
> to depend on the stated domain and Lipschitz bound.

**Choices and protected meaning.** C7–11 and W7–8 tie evaluation, interpolation control
and decision to their actual jobs. The three outputs retain the strict/non-strict
boundaries. No finite stopping at equality, superiority or unknown global constant is
invented. A method name or “effective algorithm” cannot replace this explanation.

### Empirical: retain the adverse result and comparison scope

**Input.** Two hypothetical evaluations, D1 and D2, each use the same 25 cases for
estimators A and B. Mean absolute errors in metres are D1: A=.8, B=1.0; D2: A=1.2,
B=1.0. No dispersion, confidence interval or causal design is supplied. The initial
paragraph claims, “A consistently improves accuracy and has broad applicability.”

**Complete revision.**

> Estimator A had a mean absolute error of 0.8 m on D1, compared with 1.0 m for B.
> On D2, A had an error of 1.2 m and B again had an error of 1.0 m. Each comparison
> uses the same 25 cases for both estimators. The direction of the difference therefore
> changes between these two evaluations. They show how the observed comparison depends
> on the dataset; its statistical uncertainty requires information beyond the supplied
> mean errors.

**Choices and protected meaning.** T17, C8–9 and W8/18 make the quantity, units and
comparison visible. The adverse result remains next to the favorable one; “observed”
does not become a general or causal guarantee. No p-value, significance or uncertainty
estimate is fabricated. Writing the result directly supplies more value than another
sentence calling it comprehensive.

### Review: fair agreement without a manufactured dispute

**Input.** Three hypothetical source summaries are supplied: Study A bounds a response
for fixed parameters; Study B measures responses at one operating condition; Study C
estimates a mean under a specified random parameter law. None claims to answer every
other question. The review must compare what information each provides.

**Complete synthesis paragraph.**

> The three studies describe the response at different levels. Study A supplies a
> bound for its fixed parameter values. Study B provides observations at one operating
> condition, giving a comparison for that setting. Study C incorporates parameter
> variation and reports a mean under its specified law. Their contributions are
> complementary: comparison requires the response quantity, parameter conditions and
> probability model to be stated together. A bound, an observation and a mean then
> retain their distinct evidential roles.

**Choices and protected meaning.** C5–6, T2/4/15/18 and W6 organize sources by the shared
question and preserve their different aims. Agreement yields a useful synthesis without
calling a source deficient for a task it did not attempt. Actual manuscripts require
actual sources and locators; these teaching labels are not citations to insert.

### Paragraph flow, passive voice and useful nominalization

**Input.** Two probability upper bounds were derived separately for events A and B
under the supplied parameter law. The dependence between events is unspecified; no
independence or joint-probability guarantee is supplied. The known actor is immaterial.
The draft says, “The performance of derivations of probability upper bounds for events
A and B was carried out separately. A consideration of a joint interpretation of these
derivations requires a specification of their dependence.”

**Complete English revision.**

> A probability upper bound was derived separately for each of events A and B under
> the supplied parameter law. The two derivations provide separate guarantees. Their
> upper bounds also bound the union and intersection by the usual probability
> inequalities. An exact joint-event probability requires further information about
> the joint law; the supplied results leave event dependence unspecified.

**Complete Chinese adaptation.**

> 在给定的参数分布下，分别为事件A和B推导了概率上界。两项推导分别提供保证，也可利用
> 通常的概率不等式得到并集和交集的上界。确定联合事件的精确概率还需要联合分布的
> 进一步信息；现有结果未指定两事件的依赖关系。

**Choices and protected meaning.** S3–6, C17, W12–14 and T8 give the first sentence a
clear operation, then carry “two derivations” into their interpretation. Passive voice
keeps the focus on the bounds; “derivations” is a useful conceptual noun. No agent is
invented. Separate derivations do not become independent events. Both languages retain
the same law, guarantee scope and missing dependence information. Missing dependence
does not prevent union/intersection upper bounds; it does not determine exact joint
probabilities from separate upper bounds either.

### Long sentence, punctuation and exact endpoints

**Input.** Use the grid method above. The writer wants one clear sentence connecting
the admitted conditions and the sufficient test. The initial text is: “The supremum
which is bounded by the grid maximum plus the Lipschitz allowance and which is compared
to a threshold is used when the function is Lipschitz with constant L on K and points
are within distance h of the grid to certify that the threshold is satisfied if the
upper bound is less than b.” Its last phrase incorrectly drops equality.

**Complete revision.**

> When $f$ is $L$-Lipschitz on $K$, the grid is contained in $K$, and every point lies within $h$ of
> the grid, the grid maximum plus $Lh$ bounds the supremum; an upper bound at most
> $b$ certifies the threshold condition on that domain.

**Choices and protected meaning.** S9–11/Appendix I and W12/16 make the main relation
recoverable and use the semicolon between related independent clauses. The condition
opens the sentence, the decision closes it. The scientific check repairs `< b` to
`<= b` from the supplied contract; brevity alone would not catch this. “At most” and
the domain remain load-bearing, as S's payment example demonstrates by its inconsistent
intermediate rewrite. This long sentence need not be split merely for length.

### Display design: lookup and a claim-bearing caption

**Input.** Use the empirical data above. Readers need exact errors and the change in
comparison direction; no uncertainty estimates are available. This is a design task,
not authorization to produce a figure or edit a manuscript.

**Complete table design.**

| Evaluation | A: MAE $m$ | B: MAE $m$ |
|---|---:|---:|
| D1 | 0.8 | 1.0 |
| D2 | 1.2 | 1.0 |

**Complete caption.**

> Mean absolute error for estimators A and B on two evaluations. Each row compares
> the estimators on the same 25 cases. A has lower error on D1 and higher error on D2.
> The entries are evaluation means; dispersion and interval estimates are not supplied.

**Choices and protected meaning.** C15/T17/W8 select a table for exact lookup and
retain the changed direction. Aligned dots could serve a visual comparison if drawing
were requested. No error bars are invented, no favorable row selected away, and no
line implies a continuous sequence between D1 and D2. A rendered graphic would still
need the scientific and visual production gates.

### Source quotation: frame, explain and keep authority separate

**Input.** Explain the writing concept of a warrant using a short actual book quotation.
The original is C11, `OEBPS/Text/part0024.xhtml#ch11`, exact local ref
`epub:src-001948:b001379:9f16dee50f2b`. Its surrounding argument distinguishes a reason's
validity from its relevance and explains when a warrant needs stating.

**Complete paragraph with an exact quotation.**

> The Craft of Research defines the connection explicitly: “A warrant is a principle
> that connects a reason to a claim.” A reason can be accurate while its relevance
> to the proposed conclusion remains unclear. Checking that connection therefore asks
> more than whether the reported fact is correct: it asks why the fact supports this
> particular claim.

**Choices and protected meaning.** T3, C11/14 and S Appendix II identify the source,
quote its actual wording and explain the current purpose. This is a writing-method
explanation, not proof of a scientific claim or a citation to add to every manuscript.
The locator is a verified EPUB block, not an invented page number; normalized text and
original markup were checked for this quotation.

### Material objection: narrow the claim rather than decorate it

**Input.** A proof supports the grid test with a valid global Lipschitz bound `L`. A
proposed paragraph claims the same guarantee using `L` estimated only at sampled points.
No argument shows that the estimated value bounds variation between points.

**Complete assessment and supported wording.**

> The proposed extension needs an additional bound on variation between grid points.
> The supplied proof establishes certification with a valid Lipschitz constant over
> the stated domain. The manuscript can state that guarantee directly: “With a supplied
> Lipschitz bound valid on $K$, the grid interval certifies the stated threshold
> condition.” Using a sampled estimate of that constant remains a separate claim.

**Choices and protected meaning.** C10–11, T6 and W18 answer the actual proof gap.
Calling the estimate a limitation does not establish the extension. Assessment supplies
the diagnosis and a concrete suggestion; it does not edit the paper or launch a new
experiment. The established mathematical guarantee remains strong within its conditions.

## Transfer the work, not the template

Across these cases, decide what readers need to judge, recover the scientific relations,
and arrange sufficient evidence and explanation before choosing wording. The result
can be a field map, a design rationale, an experimental comparison, a proof sequence,
or a result-led article. Those are different realizations of the same composition priority.

Use a fresh source when a new organizational job is absent here. Check the relevant
complete unit, then give the concrete example and its applicable conditions. Retain
already-effective writing; a small terminology correction does not require another
cohort, a whole-paper rewrite, or a teaching appendix. Format checks establish file
integrity; subsequent writing and reader feedback establish whether these lessons help.
