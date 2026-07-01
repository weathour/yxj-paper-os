# yxj-paper-os

语言：**中文** | [English](README.md)

`yxj-paper-os` 是一个面向学术论文生产的 Codex 插件。它不是“自动写完整篇论文”的路线，而是把论文生产组织成一个可见、可验证、可局部修复的 **Paper Production Graph（PPG）运行时**。

核心模型：

> **显式材料图 + 局部回流修复 + 主 Agent 调度**

主 Agent 是运行时控制器：观察图状态，选择下一前沿，编译任务包，派发 bounded worker 或脚本，收回候选产物，运行验证器，然后决定提交、阻塞、标记 stale 或编译 backflow。子 Agent 只能返回候选产物和证据，不能宣布图完成、不能改 owner intent、不能递归调度。

## 当前状态

- 阶段：Phase 13 live native-subagent full-flow pilot 已提升。它记录了 20 个 canonical stage，每个 stage 在严格 QA 模式下有 producer + verifier 两条 native-subagent lane，共 40 条 lane。
- 边界：这是 runtime-pilot 能力，不是最终 manuscript、submission-ready 或 publication-ready 声明。
- 只读前端：`docs/runtime-viewer/index.html` 提供路线图、详细节点图、环节工作台、Runtime State 和 Stage Coverage。

## 如何理解这个系统

传统 agent 写作容易变成隐藏闭环：

```text
route -> internal analysis -> internal review -> route claims progress
```

PPG runtime 改成显式状态转移：

```text
material -> task -> candidate output -> validator -> committed / stale / backflow
```

也就是说，一个环节不是因为 agent 写了一段文字就完成；只有当图中记录了候选产物、验证证据、提交状态和 stale/backflow 边界，主 Agent 才能接受它。

## 主控面唤醒契约

当用户唤醒 `yxj-paper-os` 时，主 Agent 的身份必须切换为 **Paper Production Graph Runtime Controller**，而不是普通写稿助手或 LaTeX 编辑器。它应先定位当前图状态，再报告 active stage/gate、已提交材料、候选/归档/陈旧/阻塞材料、owner-gated 决策、最近可推进阶段、禁止捷径和验证证据。具体交接模板与反馈路由见 [`docs/MANAGER_SURFACE_PROTOCOL.md`](docs/MANAGER_SURFACE_PROTOCOL.md)。


## 环节命名对照

这些是给使用者看的易懂名称；运行时仍使用稳定的 `Sxx/Gxx` id 和 canonical StageContract 名称。

| ID | 易懂名 | Canonical contract name | 如何交给下一环 |
| --- | --- | --- | --- |
| `S00` | 定目标与边界 / Set goals and boundaries | Owner semantic contract | 把人的写作目的、禁区和需要人工批准的事项变成后续环节可执行的约束。 |
| `S01` | 盘点来源与证据 / Inventory sources and evidence | Source citation evidence inventory | 把论文能使用的文件、引用、结果目录和证据位置整理成可追踪材料库。 |
| `S02` | 看清研究位置 / Map the research position | Research scene exemplar SOTA analysis | 把证据放进领域、读者、模板和 SOTA 背景中，形成后续贡献判断的语境。 |
| `S03` | 形成贡献候选 / Shape contribution options | Novelty and contribution option analysis | 提出可能的贡献说法和风险，但必须交给 S04 判断哪些能被证据承载。 |
| `S04` | 锁定能说的主张 / Lock evidence-backed claims | Evidence-to-claim admissibility | 把证据、引用和结果转成可写 claim，明确能说什么、强度到哪里为止。 |
| `S05` | 搭建论文主线 / Build the paper spine | Paper spine and reader-question synthesis | 把可写主张组织成读者一路能跟上的问题链和章节主线。 |
| `S06` | 设计对象与颗粒度 / Design objects and granularity | Object representation and granularity design | 决定论文中哪些对象、变量、机制和解释层级需要出现，以及细到什么程度。 |
| `S07` | 统一术语与表达 / Align terminology and tone | Rhetoric terminology and surface-control synthesis | 把术语、语气、段落功能和表层表达规则交给写作任务包。 |
| `S08` | 规划图表与形式对象 / Plan figures and formal objects | Visual and formal object planning | 把主线、证据和读者问题转成图表、公式、算法、补充材料的契约。 |
| `S09A` | 选择写作控制材料 / Select writing controls | Control-material selection | 从 claim、主线、颗粒度和表层规则中挑出当前单元真正需要的控制材料。 |
| `S09B` | 组装单元任务包 / Assemble unit task packets | Per-unit task packet assembly | 把选定控制材料、证据锚点、边界和返回格式编译成可派发的 TaskPacket。 |
| `S10` | 产出正文候选 / Draft text candidates | Main-text production | 子 agent 只根据任务包产出候选正文和证据，不拥有完成权。 |
| `S11` | 产出图表与说明 / Produce figures and captions | Figure caption formal artifact production | 根据图表契约和证据位置生成图、表、caption、公式或算法相关产物。 |
| `S12` | 合并并查一致性 / Integrate and check consistency | Integration and consistency pass | 把正文、图表、引用和术语合在一起，检查跨章节是否漂移。 |
| `S13` | 对抗审稿找问题 / Run adversarial review | Adversarial manuscript review | 像审稿人一样输出 findings/loss，不直接重写全文。 |
| `S14` | 把问题转成修复任务 / Compile repair tasks | Backflow compilation and repair planning | 把审核问题定位到最近责任材料，形成局部 backflow 和 repair packets。 |
| `S15` | 局部修复与再生成 / Repair and regenerate locally | Repair execution and local regeneration | 只修受影响的材料、文本或图表，再触发必要验证。 |
| `S16` | 导出、整理与交接 / Export, clean, and hand off | Export repository hygiene and handoff | 在 review/repair 闭合后整理导出物、仓库卫生和交接说明。 |
| `G01` | 运行治理与权限 / Runtime governance and authority | Runtime governance registry | 记录权限、路线、状态和控制边界，防止治理信息污染正文材料。 |
| `G02` | 论文后派生输出 / Post-paper derivatives | Derivative and post-paper outputs | 论文稳定后再派生 PPT、专利边界、期刊 profile 等外部材料。 |

## 关键目录

- `docs/MANAGER_SURFACE_PROTOCOL.md`：唤醒插件后的主控身份、读取层级、状态汇报、用户反馈回流和交接协议。
- `docs/runtime-viewer/`：只读前端，适合人工查看环节、交接、进展和 backflow。
- `runtime/stage_registry.json`：canonical stage registry。
- `examples/stage-contracts/`：每个环节的契约、输入、输出、验证器、lane policy。
- `examples/local-paper/security-state-aware-mixed-platoon/stage-runs/`：每个环节的 PilotStageRun 证据。
- `examples/local-paper/security-state-aware-mixed-platoon/artifacts/`：每个环节形成或投影出的分析/设计产物摘要。
- `runs/security-state-aware-mixed-platoon/phase13-live-subagent-full-flow-pilot/`：Phase13 live subagent pilot 证据。

## 常用验证

```bash
python3 scripts/verify_phase9_frontend_stage_coverage.py
bash scripts/verify_phase8_plugin_surface.sh
python3 scripts/ingest_phase13_live_pilot.py
python3 scripts/verify_phase13_live_subagent_pilot.py
```

完整 Phase13 聚合门：

```bash
bash scripts/verify_phase13_live_subagent_pilot.sh
```

## 重要边界

- 前端是 observability surface，不是 commit surface。
- 子 Agent 产出 candidate/evidence，不拥有完成权。
- OwnerIntent、论文核心语义和投稿边界必须 owner-gated。
- Review finding 默认触发局部 backflow，不默认全文重写。
- Runtime pilot pass 不等于论文已完成或可投稿。
