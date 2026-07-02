# Stage Guides / 阶段说明文档

This directory contains bilingual, human-readable and agent-executable guides for the paper-production stages. / 本目录包含论文生产各环节的双语说明文档，既给人读，也给 agent 执行时对齐契约。

These pages explain purpose, graph position, trigger conditions, inputs, task packets or controller packages, execution sequence, output materials, validators, failure modes, downstream handoffs, authority boundaries, and implementation files. / 每份文档说明目的、图中位置、触发条件、输入、任务包或主控包、执行顺序、输出物料、验证器、失败模式、下游交接、权威边界和实现文件。

They do not replace the machine contracts. The source of truth remains `runtime/stage_registry.json`, `examples/stage-contracts/`, schemas, validators, and fixtures. / 它们不替代机器契约；权威源仍是 `runtime/stage_registry.json`、`examples/stage-contracts/`、schema、validator 和 fixtures。

## Guides / 文档列表

| Stage | Guide / 文档 | Summary / 摘要 |
| --- | --- | --- |
| `S00` | [Owner Semantic Contract / 作者意图语义契约](S00-owner-semantic-contract.md) | S00 turns the owner's human need, venue route, contribution boundary, and forbidden routes into the first authoritative semantic contract. / S00 把作者的真实需求、目标路线、贡献边界和禁止路线转成第一份具有权威性的语义契约。 |
| `S01` | [Source and Evidence Inventory / 来源、引用与证据盘点](S01-source-evidence-inventory.md) | S01 builds the read-only inventory of sources, citations, evidence, figure data, supplements, privacy boundaries, and freshness status. / S01 建立只读的来源、引用、证据、图表数据、补充材料、隐私边界和新鲜度状态盘点。 |
| `S02` | [Research Dossier / 研究场景、SOTA 与语言画像](S02-research-dossier.md) | S02 analyzes field scene, SOTA families, exemplar/template structure, and language/rhetorical distributions as descriptive context for downstream stages. / S02 分析研究场景、SOTA 家族、模板/标杆结构和语言修辞分布，为后续环节提供描述性上下文。 |
| `S03` | [Contribution Options / 贡献选项与新颖性风险门](S03-contribution-options.md) | S03 generates, classifies, rejects, owner-gates, and hands off contribution options without making admissibility or final-wording decisions. / S03 生成、分类、拒绝或 owner-gate 贡献选项，并把候选交给 S04，但不判断最终可说性和最终措辞。 |
| `S04` | [Claim Admissibility / 主张—证据准入](S04-claim-admissibility.md) | S04 decomposes claim candidates, binds evidence anchors, assigns support strength, and derives allowed/forbidden wording boundaries. / S04 拆解候选主张、绑定证据锚点、判定支持强度，并推导允许/禁止措辞边界。 |
| `S05` | [Reader Spine / 读者问题链与论文主脊](S05-reader-spine.md) | S05 converts admitted claim capsules into a reader/reviewer question path, section spine, rationale matrix, and downstream design handoffs. / S05 把已准入的 claim capsule 组织成读者/审稿人问题链、章节主脊、理由矩阵和下游设计交接。 |
| `S06` | [Object Granularity / 对象、机制变量与解释颗粒度](S06-object-granularity.md) | S06 designs object representations, mechanism-variable cards, section load budgets, granularity progression, and explanation ladders. / S06 设计对象表示、机制变量卡、章节负载预算、颗粒度递进和解释阶梯。 |
| `S07` | [Rhetoric and Surface Control / 术语、修辞与表层表达控制](S07-rhetoric-surface-control.md) | S07 compiles claim-safe terminology, paragraph jobs, rhetorical moves, flexible language controls, and forbidden-expression guards. / S07 编译安全承载 claim 的术语、段落任务、修辞动作、灵活语言控制和禁用表达防线。 |
| `S08` | [Visual and Formal Plan / 图表与形式对象计划](S08-visual-formal-plan.md) | S08 plans visual/formal objects, figure/table/formal contracts, panel evidence maps, visual budgets, backend routes, and caption boundaries. / S08 规划图表/形式对象、figure/table/formal contracts、panel evidence map、视觉预算、后端路线和 caption 边界。 |
| `S09` | [Control Selection and Task-Packet Assembly / 控制材料选择与任务包编译](S09-control-packet-assembly.md) | S09 is an umbrella stage: S09A selects rich controls for a target unit, and S09B compiles those controls into a bounded worker TaskPacket. / S09 是总括环节：S09A 为目标单元选择丰富控制材料，S09B 把这些控制材料编译成受限 worker TaskPacket。 |
| `S10` | [Candidate Text Return / 正文候选生成与返回](S10-candidate-text-return.md) | S10 produces bounded main-text candidates from S09B packets with traceable claim, evidence, move, terminology, object, and visual-callout evidence. / S10 根据 S09B 任务包生成受限正文候选，并返回 claim、evidence、move、terminology、object 和 visual callout 追踪证据。 |
| `S11` | [Figure Caption Artifact Bundle / 图表、caption 与形式 artifact 候选包](S11-figure-caption-artifact-bundle.md) | S11 produces contract-bound visual/formal artifacts and captions with source-data trace, panel-claim trace, visual polish, accessibility, and export evidence. / S11 根据契约生成图表/形式对象和 caption 候选，并提供源数据、panel-claim、视觉润色、可访问性和导出证据。 |
| `S12` | [Integration and Consistency / 集成候选稿与一致性审查](S12-integration-consistency.md) | S12 assembles structured S10/S11 candidates into an integrated manuscript candidate and audits consistency, traceability, stale nodes, and backflow needs. / S12 把结构化 S10/S11 候选集成为 integrated manuscript candidate，并审查一致性、可追踪性、stale 节点和回流需求。 |
| `S13` | [Adversarial Review Report / 对抗性稿件审查报告](S13-adversarial-review-report.md) | S13 reviews the structured S12 candidate adversarially and returns actionable findings with severity, evidence, location, and nearest-stage routing. / S13 对结构化 S12 候选稿做对抗性审查，返回带严重度、证据、位置和最近责任阶段路由的 actionable findings。 |
| `S14` | [Backflow Repair Plan / 回流归因与修复计划](S14-backflow-repair-plan.md) | S14 converts review/integration findings into nearest-responsible-stage backflow plans, repair scopes, task packets, priorities, and validation plans. / S14 把审查/集成发现转换为最近责任阶段回流计划、修复范围、任务包、优先级和验证计划。 |
| `S15` | [Repair Execution Report / 局部修复执行报告](S15-repair-execution-report.md) | S15 executes bounded repairs from S14, records diff locality, revised candidates, downstream regeneration, stale resolution, and no-new-risk evidence. / S15 执行 S14 的受限修复，记录 diff locality、修订候选、下游再生成、stale 解决和无新增风险证据。 |
| `S16` | [Export and Handoff Package / 导出、仓库卫生与交接包](S16-export-handoff-package.md) | S16 verifies upstream closure, build/readiness states, rendered surface, manifests, hashes, repository hygiene, handoff completeness, and feedback routes. / S16 验证上游 closure、构建/就绪状态、渲染表面、manifest、hash、仓库卫生、交接完整性和反馈路线。 |

## Use pattern / 使用方式

1. The controller identifies the current frontier, stale node, feedback item, or requested stage. / 主控识别当前 frontier、stale node、反馈项或目标 stage。
2. Read the relevant guide to understand the human purpose and execution flow. / 阅读对应文档理解人类目的和执行流程。
3. Use the referenced stage contract, packet, schema, and verifier as the executable authority. / 使用文档引用的 stage contract、packet、schema 和 verifier 作为可执行权威。
4. Commit graph state only after schema, semantic validators, candidate returns, and handoff status are valid. / 只有 schema、语义 validator、candidate return 和交接状态有效后才提交图状态。
