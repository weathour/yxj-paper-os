# S03 Contribution Options / 贡献选项与新颖性风险门

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S03 generates, classifies, rejects, owner-gates, and hands off contribution options without making admissibility or final-wording decisions.

**中文。** S03 生成、分类、拒绝或 owner-gate 贡献选项，并把候选交给 S04，但不判断最终可说性和最终措辞。

**Contract purpose / 契约原文目的。** Identify viable contribution framings without treating speculation as evidence.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S02/S00/S01 → S03 → S04/S05
```

**EN.** S03 asks “what could this paper plausibly contribute?” and keeps unsupported novelty ideas from becoming claims too early.

**中文。** S03 问的是“这篇论文可能贡献什么”，并阻止没有证据的新颖性想法过早变成主张。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 需要从 SOTA/owner intent 形成候选贡献路线时
- 贡献点太多、太散或证据状态不清楚时
- 需要把 unsupported/owner-gated/rejected option 显式记录时

**English triggers:**

- Candidate contribution routes must be derived from SOTA and owner intent.
- Contribution ideas are too many, fragmented, or evidence-unclear.
- Unsupported, owner-gated, or rejected options must be recorded explicitly.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `research dossier`
- `evidence inventory`
- `motivation`
- `SOTA map`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- 候选贡献类型和组合
- 与近邻 SOTA 的差异
- 证据准备度和 reviewer attack
- 语义变化是否需要 owner gate

**English:**

- Candidate contribution types and bundles.
- Differences from nearby SOTA.
- Evidence readiness and reviewer attacks.
- Whether semantic shifts require owner gating.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S03` requires a strict worker task packet / `S03` 需要严格 worker 任务包: `examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml`](../../examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 输入边界盘点
- 候选贡献生成
- SOTA contrast pass
- evidence readiness 分类
- reviewer attack 与 coherence pass
- rejection/owner-gate pass
- S04 handoff pass

**English execution sequence:**

- Input boundary inventory.
- Candidate contribution generation.
- SOTA contrast pass.
- Evidence-readiness classification.
- Reviewer-attack and coherence pass.
- Rejection/owner-gate pass.
- S04 handoff pass.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `contribution options`
- `novelty readiness`
- `risk list`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s03_contribution_options.yaml`](../../examples/materials/phase10_s03_contribution_options.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `contribution_option_queue`
- `contribution_type_taxonomy`
- `sota_contrast_matrix`
- `evidence_readiness_score`
- `unsupported_claim_register`
- `rejected_option_register`
- `owner_gated_option_register`
- `owner_gated_semantic_shift_log`
- `reviewer_attack_map`
- `contribution_coherence`
- `option_coverage_ledger`
- `sota_contrast_coverage`
- `s04_handoff`
- `s04_handoff_coverage`
- `anti_rhetoric_guard`
- `unresolved_backflow_register`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S03_contribution_option_queue`
- `S03_option_coverage_ledger`
- `S03_sota_contrast_matrix`
- `S03_evidence_readiness_classifier`
- `S03_rejected_option_register`
- `S03_owner_gated_option_register`
- `S03_reviewer_attack_map`
- `S03_s04_handoff_coverage`
- `S03_no_claim_admissibility_or_final_wording`
- `S03_no_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s03-contribution-options-claim-admissibility.yaml`
- `examples/materials/invalid-s03-contribution-options-completion-overclaim.yaml`
- `examples/materials/invalid-s03-contribution-options-invalid-status.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-anti-rhetoric-guard.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-option-queue.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-owner-gated-register.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-rejected-register.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-s04-handoff.yaml`
- `examples/materials/invalid-s03-contribution-options-missing-sota-contrast.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s03_contribution_options.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能宣称最终 novelty
- 不能替 S04 批准 claim
- 不能把 rejected/unsupported option 下放到正文

**English boundaries:**

- It must not claim final novelty.
- It must not approve claims for S04.
- It must not pass rejected or unsupported options into prose.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S03`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S03.stage-contract.json`](../../examples/stage-contracts/S03.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s03_contribution_options.py`](../../scripts/verify_s03_contribution_options.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S03 问的是“这篇论文可能贡献什么”，并阻止没有证据的新颖性想法过早变成主张。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S03 asks “what could this paper plausibly contribute?” and keeps unsupported novelty ideas from becoming claims too early. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## Stage-quality upgrade contract / 阶段质量升级合同

**EN.** This stage must not be accepted only because its artifact exists. It must preserve enough upstream authority and design force for downstream stages to execute without guessing. Producer packets may include all relevant source, owner, profile, evidence, and design materials; audit/verifier packets inherit the same inputs and add stricter sufficiency checks.

**中文。** 本阶段不能因为产物存在就算完成。它必须为下游保留足够的权威、证据和设计约束。生产包可以给足所有相关输入；审核包必须继承生产包全部输入，并追加更严格的充分性检查。

Stage-quality focus / 阶段质量焦点：`contribution option and reviewer attack gate`.

Required extraction examples / 必须抽取示例：supported_contribution_options, rejected_options, owner_gated_options, reviewer_attack_map, S04_handoff.

Downstream design force / 下游设计力：S04 receives claim candidates and forbidden options; S05/S07/S13 receive reviewer attack obligations; S10 introduction/discussion depth is grounded.

Blocking or major failures must name the nearest responsible stage and affected downstream nodes instead of defaulting to whole-paper rewrite. MINOR/WATCH findings do not force a full downstream rerun by default.
