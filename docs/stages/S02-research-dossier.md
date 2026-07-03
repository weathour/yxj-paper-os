# S02 Research Dossier / 研究场景、SOTA 与语言画像

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S02 analyzes field scene, SOTA families, exemplar/template structure, and language/rhetorical distributions as descriptive context for downstream stages.

**中文。** S02 分析研究场景、SOTA 家族、模板/标杆结构和语言修辞分布，为后续环节提供描述性上下文。

**Contract purpose / 契约原文目的。** Understand field scene, template expectations, exemplar structure, and related-work positioning.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S01 → S02 → S03/S05/S07
```

**EN.** S02 is reconnaissance, not writing. It explains how the field is organized and how papers in this route tend to speak, while explicitly preventing statistical profiles from becoming rigid generation rules.

**中文。** S02 是侦察，不是写作。它说明领域如何组织、同路线论文通常怎样表达，同时防止把统计画像误当成硬性生成规则。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 已有 source/citation inventory 但还不清楚 field/SOTA 格局时
- 需要 exemplar/template 和语言分布供 S03/S05/S07 使用时
- 需要避免后续贡献点或表达凭感觉生成时

**English triggers:**

- A source/citation inventory exists but the field/SOTA landscape is still unclear.
- S03/S05/S07 need exemplar/template and language-profile context.
- Contribution framing or surface language would otherwise be guessed.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `source map`
- `citation bank`
- `venue route`
- `exemplar locators`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- 研究场景和问题传统
- SOTA 方法家族与近邻 comparator
- 标杆论文结构、段落功能和 citation placement
- 语法、用词、段落功能、citation pattern 的描述性分布

**English:**

- Research scene and problem tradition.
- SOTA method families and nearby comparators.
- Exemplar structure, paragraph function, and citation placement.
- Descriptive distributions of syntax, wording, paragraph roles, and citation patterns.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S02` requires a strict worker task packet / `S02` 需要严格 worker 任务包: `examples/packets/phase10_s02_sota_analysis_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s02_sota_analysis_packet.v1.yaml`](../../examples/packets/phase10_s02_sota_analysis_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 材料/source inventory 与范围冻结
- SOTA family clustering
- comparator matrix 构造
- template/exemplar 结构抽取
- language/rhetorical profile 抽取
- misuse guard 与 downstream handoff

**English execution sequence:**

- Material/source inventory and scope freeze.
- SOTA family clustering.
- Comparator matrix construction.
- Template/exemplar structure extraction.
- Language/rhetorical profile extraction.
- Misuse guard and downstream handoff.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `research dossier`
- `reader package`
- `template profile`
- `citation verification report`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s02_research_dossier.yaml`](../../examples/materials/phase10_s02_research_dossier.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `research_scene_profile`
- `sota_comparator_map`
- `template_exemplar_profile`
- `template_language_profile`
- `descriptive_not_prescriptive_controls`
- `source_coverage_ledger`
- `exemplar_sample_register`
- `language_profile_sample_limits`
- `sota_family_coverage_ledger`
- `unresolved_source_report`
- `downstream_handoff_coverage`
- `misuse_guard`
- `citation_verification_report`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S02_source_coverage_ledger`
- `S02_sota_family_coverage_ledger`
- `S02_template_language_profile`
- `S02_descriptive_not_prescriptive`
- `S02_template_copying_boundary`
- `S02_unresolved_backflow_register`
- `S02_downstream_handoff_coverage`
- `S02_no_claim_or_completion_freeze`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s02-research-dossier-claim-freeze.yaml`
- `examples/materials/invalid-s02-research-dossier-completion-overclaim.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-downstream-handoff.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-language-profile.yaml`
- `examples/materials/invalid-s02-research-dossier-missing-unresolved-report.yaml`
- `examples/materials/invalid-s02-research-dossier-prescriptive-metrics.yaml`
- `examples/materials/invalid-s02-research-dossier-template-copying.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s02_research_dossier.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能冻结 claim 或贡献点
- 不能生成最终正文
- 不能照抄 exemplar
- 不能把平均词数/句式/段落长度变成硬规则

**English boundaries:**

- It must not freeze claims or contributions.
- It must not generate final prose.
- It must not copy exemplars.
- It must not turn average word counts, syntax, or paragraph length into hard rules.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S02`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S02.stage-contract.json`](../../examples/stage-contracts/S02.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s02_research_dossier.py`](../../scripts/verify_s02_research_dossier.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S02 是侦察，不是写作。它说明领域如何组织、同路线论文通常怎样表达，同时防止把统计画像误当成硬性生成规则。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S02 is reconnaissance, not writing. It explains how the field is organized and how papers in this route tend to speak, while explicitly preventing statistical profiles from becoming rigid generation rules. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## Stage-quality upgrade contract / 阶段质量升级合同

**EN.** This stage must not be accepted only because its artifact exists. It must preserve enough upstream authority and design force for downstream stages to execute without guessing. Producer packets may include all relevant source, owner, profile, evidence, and design materials; audit/verifier packets inherit the same inputs and add stricter sufficiency checks.

**中文。** 本阶段不能因为产物存在就算完成。它必须为下游保留足够的权威、证据和设计约束。生产包可以给足所有相关输入；审核包必须继承生产包全部输入，并追加更严格的充分性检查。

Stage-quality focus / 阶段质量焦点：`active venue profile and TemplateStats gate`.

Required extraction examples / 必须抽取示例：VenueProfile, TemplateStats, section_length_bands, figure_table_formula_density, citation_reference_density, rhetorical_move_profile, sample_limits.

Downstream design force / 下游设计力：S05/S07/S09/S10 receive section depth and language/profile targets; S08/S11 receive visual/formal density targets; S13/rendered gate receive template parity baselines.

Blocking or major failures must name the nearest responsible stage and affected downstream nodes instead of defaulting to whole-paper rewrite. MINOR/WATCH findings do not force a full downstream rerun by default.

