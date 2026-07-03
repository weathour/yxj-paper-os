# S05 Reader Spine / 读者问题链与论文主脊

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S05 converts admitted claim capsules into a reader/reviewer question path, section spine, rationale matrix, and downstream design handoffs.

**中文。** S05 把已准入的 claim capsule 组织成读者/审稿人问题链、章节主脊、理由矩阵和下游设计交接。

**Contract purpose / 契约原文目的。** Build a claim-bounded reader-question spine from S04-admitted claim capsules, with coverage ledgers and downstream S06/S07/S08 handoffs; no new claims or final prose.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S04/S03/S02 → S05 → S06/S07/S08/S10
```

**EN.** S05 answers “what journey should the reader take?” It decides where claims belong and why each section exists.

**中文。** S05 回答“读者应该怎样走完整篇论文”。它决定 claim 放在哪里，以及每个章节为什么存在。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 已经有 admitted claims 但论文主线不清楚时
- 读者/审稿人问题、章节功能和前后承诺关系需要显式化时
- 需要把结构需求交给 S06/S07/S08 时

**English triggers:**

- Admitted claims exist but the paper spine is unclear.
- Reader/reviewer questions, section functions, and promise/payoff relations must be explicit.
- Structural needs must be handed to S06/S07/S08.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `motivation`
- `contribution options`
- `template profile`
- `claim materials`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- admitted claim intake
- reader/reviewer question inventory
- claim-to-section placement
- front-half promise/payoff
- section rationale and removal risk

**English:**

- Admitted-claim intake.
- Reader/reviewer question inventory.
- Claim-to-section placement.
- Front-half promise/payoff.
- Section rationale and removal risk.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S05` requires a strict worker task packet / `S05` 需要严格 worker 任务包: `examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml`](../../examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- admitted-claim intake
- reader/reviewer question inventory
- claim-to-section placement
- section-function/rationale construction
- front-half promise/payoff pass
- coherence and overpromise audit
- S06/S07/S08 downstream handoff

**English execution sequence:**

- Admitted-claim intake.
- Reader/reviewer question inventory.
- Claim-to-section placement.
- Section-function/rationale construction.
- Front-half promise/payoff pass.
- Coherence and overpromise audit.
- S06/S07/S08 downstream handoff.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `reader spine`
- `reviewer question map`
- `rationale matrix`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s05_reader_spine.yaml`](../../examples/materials/phase10_s05_reader_spine.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `admitted_claim_intake_ledger`
- `reader_question_inventory`
- `reader_question_coverage_ledger`
- `reader_spine`
- `reviewer_question_map`
- `rationale_matrix`
- `claim_section_coverage_ledger`
- `front_half_promise_coverage`
- `excluded_claim_or_question_register`
- `owner_decision_log`
- `s06_handoff`
- `s07_handoff`
- `s08_handoff`
- `s06_s07_s08_handoff_coverage`
- `coherence_overpromise_audit`
- `unresolved_backflow_register`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S05_admitted_claim_intake_ledger`
- `S05_reader_question_inventory`
- `S05_reader_question_coverage_ledger`
- `S05_reader_question_progression`
- `S05_claim_to_section_spine`
- `S05_claim_section_coverage_ledger`
- `S05_front_half_promise_coverage`
- `S05_reviewer_question_map`
- `S05_rationale_matrix`
- `S05_owner_decision_log`
- `S05_s06_s07_s08_handoff_coverage`
- `S05_coherence_overpromise_audit`
- `S05_no_new_claims_or_final_prose`
- `S05_no_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s05-reader-spine-completion-overclaim.yaml`
- `examples/materials/invalid-s05-reader-spine-final-prose.yaml`
- `examples/materials/invalid-s05-reader-spine-hidden-owner-decision.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-admitted-claim-intake.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-claim-section-coverage.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-claim-section-spine.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-front-half-payoff.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-rationale.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-reader-question-coverage.yaml`
- `examples/materials/invalid-s05-reader-spine-missing-s06-s07-s08-handoff.yaml`
- `examples/materials/invalid-s05-reader-spine-new-claim.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s05_reader_spine.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能引入新 claim
- 不能写最终段落
- 不能隐藏 owner decision 或 unsupported promise

**English boundaries:**

- It must not introduce new claims.
- It must not write final paragraphs.
- It must not hide owner decisions or unsupported promises.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S05`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S05.stage-contract.json`](../../examples/stage-contracts/S05.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s05_reader_spine.py`](../../scripts/verify_s05_reader_spine.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S05 回答“读者应该怎样走完整篇论文”。它决定 claim 放在哪里，以及每个章节为什么存在。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S05 answers “what journey should the reader take?” It decides where claims belong and why each section exists. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## Stage-quality upgrade contract / 阶段质量升级合同

**EN.** This stage must convert upstream design into downstream constraints rather than returning advisory prose. Producer packets should include all relevant owner, profile, claim, reader, object, rhetoric, and visual materials needed for this stage. Audit/verifier packets inherit those inputs and check whether the stage output gives later stages enough design force to execute without guessing.

**中文。** 本阶段必须把上游设计转成下游约束，而不是只产出建议性文本。生产包应给足本阶段需要的 owner/profile/claim/reader/object/rhetoric/visual 材料；审核包继承这些输入，并检查产物是否真正给下游提供了可执行设计力。

Stage-quality focus / 阶段质量焦点：`reader spine paragraph-depth gate`.

Required extraction examples / 必须抽取示例：reader_questions, section_jobs, paragraph_depth_obligations, promise_payoff_map, reviewer_question_map.

Downstream design force / 下游设计力：S10 receives paragraph-depth obligations; S12 checks promise/payoff; S13 can attack unresolved reader questions.

If these obligations are absent or too weak, the failure routes to `S05` or its nearest upstream source rather than being hidden as a later S10/S12/S16 defect.

