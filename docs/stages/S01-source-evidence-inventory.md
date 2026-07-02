# S01 Source and Evidence Inventory / 来源、引用与证据盘点

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S01 builds the read-only inventory of sources, citations, evidence, figure data, supplements, privacy boundaries, and freshness status.

**中文。** S01 建立只读的来源、引用、证据、图表数据、补充材料、隐私边界和新鲜度状态盘点。

**Contract purpose / 契约原文目的。** Make raw paper inputs locatable and support-safe.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S00 → S01 → S02/S04/S08/S11/S16
```

**EN.** S01 is the paper's evidence warehouse map. It tells later stages what exists and where it is; it does not decide what claims are admissible.

**中文。** S01 是论文证据仓库地图。它告诉后续有哪些材料、在哪里，但不判断哪些主张能说。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 开始分析前没有可靠 source map 时
- 引用、数据、图源、supplement 或 provenance 不清楚时
- 后续 claim/figure/export 需要可追踪来源时

**English triggers:**

- There is no reliable source map before analysis begins.
- Citation, data, figure-source, supplement, or provenance status is unclear.
- Later claim, figure, or export stages need traceable source handles.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `initial files`
- `result dirs`
- `BibTeX`
- `source locators`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- 文献与引用银行
- 实验/结果/数据证据位置
- 图表源数据与补充材料
- 隐私、访问、定位器和 freshness 风险

**English:**

- Literature and citation bank.
- Experiment/result/data evidence locations.
- Figure source data and supplements.
- Privacy, access, locator, and freshness risks.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S01` does not require a normal worker task packet / `S01` 不需要普通 worker 任务包 (`not_required`).

**Packet/material contract files / 任务包或控制包文件：**

- _Not applicable / 不适用_

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 扫描仓库和 manuscript/source roots
- 整理 citation bank 与 evidence bank
- 盘点 figure data 和 supplement
- 标记 privacy / unresolved locator / freshness 风险
- 输出 coverage ledger 和 candidate return

**English execution sequence:**

- Scan repository and manuscript/source roots.
- Build citation and evidence banks.
- Inventory figure data and supplements.
- Flag privacy, unresolved locator, and freshness risks.
- Return coverage ledger and candidate return.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `source map`
- `citation bank`
- `evidence bank`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/s01_inventory_input.v1.yaml`](../../examples/materials/s01_inventory_input.v1.yaml)
- [`examples/materials/s01_source_evidence_inventory.v1.yaml`](../../examples/materials/s01_source_evidence_inventory.v1.yaml)

**Payload modules / payload 模块：**

- `s01_inventory_input.v1.yaml:schema_version`
- `s01_inventory_input.v1.yaml:stage_id`
- `s01_inventory_input.v1.yaml:activation_reason`
- `s01_inventory_input.v1.yaml:repository_roots`
- `s01_inventory_input.v1.yaml:manuscript_sources`
- `s01_inventory_input.v1.yaml:bibliography_sources`
- `s01_inventory_input.v1.yaml:evidence_sources`
- `s01_inventory_input.v1.yaml:figure_sources`
- `s01_inventory_input.v1.yaml:supplement_sources`
- `s01_inventory_input.v1.yaml:source_policy_from_s00`
- `s01_inventory_input.v1.yaml:freshness_policy`
- `s01_inventory_input.v1.yaml:read_only_boundary`
- `s01_source_evidence_inventory.v1.yaml:schema_version`
- `s01_source_evidence_inventory.v1.yaml:stage_id`
- `s01_source_evidence_inventory.v1.yaml:completion_boundary`
- `s01_source_evidence_inventory.v1.yaml:source_map`
- `s01_source_evidence_inventory.v1.yaml:citation_bank`
- `s01_source_evidence_inventory.v1.yaml:evidence_bank`
- `s01_source_evidence_inventory.v1.yaml:figure_source_data_inventory`
- `s01_source_evidence_inventory.v1.yaml:data_availability_inventory`
- `s01_source_evidence_inventory.v1.yaml:supplement_inventory`
- `s01_source_evidence_inventory.v1.yaml:privacy_boundary_report`
- `s01_source_evidence_inventory.v1.yaml:unresolved_locator_register`
- `s01_source_evidence_inventory.v1.yaml:freshness_report`
- `s01_source_evidence_inventory.v1.yaml:coverage_ledger`
- `s01_source_evidence_inventory.v1.yaml:candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `source locator resolution`
- `privacy boundary check`
- `evidence path check`
- `S01_read_only_boundary`
- `S01_root_coverage`
- `S01_source_locator_resolution`
- `S01_bibtex_key_coverage`
- `S01_evidence_artifact_locator`
- `S01_figure_source_data_locator`
- `S01_supplement_inventory`
- `S01_privacy_boundary`
- `S01_freshness_hash_report`
- `S01_no_claim_admissibility`
- `S01_unresolved_locator_register`
- `S01_no_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s01-inventory-input-source-write-allowed.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-claim-admissibility.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-missing-completion-boundary.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-missing-privacy-boundary.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-missing-unresolved-register.yaml`
- `examples/materials/invalid-s01-source-evidence-inventory-private-promoted.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s01_source_evidence_inventory.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 只读盘点，不提升未验证材料为 evidence
- 不做 claim admissibility
- 不改写 source 或 manuscript

**English boundaries:**

- Read-only inventory; it must not promote unverified material into evidence.
- It does not perform claim admissibility.
- It does not rewrite sources or manuscript text.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S01`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S01.stage-contract.json`](../../examples/stage-contracts/S01.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s01_source_evidence_inventory.py`](../../scripts/verify_s01_source_evidence_inventory.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S01 是论文证据仓库地图。它告诉后续有哪些材料、在哪里，但不判断哪些主张能说。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S01 is the paper's evidence warehouse map. It tells later stages what exists and where it is; it does not decide what claims are admissible. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
