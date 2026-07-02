# yxj-paper-os

`yxj-paper-os` 是一个独立的 Codex 论文生产管理插件，把学术论文写作管理为显式的 Paper Production Graph。

当前模型是：

> **显式物料图 + 阶段责任归因 + 局部反向传播 + 全流程复盘学习 + 主 agent 调度**

主 Codex agent 是 **Paper Production Graph Runtime Controller**。它读取当前论文工作区，区分已提交物料、候选物料、归档材料和 stale 节点，编译受限任务包，调度 worker 或脚本，验证候选输出，提交图状态，并把反馈路由到最近的责任阶段/物料。

worker、脚本、PDF、前端面板和可选编排工具只能提供证据或候选输出，不能拥有完成权威。

## 产品理念

好稿件不应该靠最后全文重写抢救，而应该自然来自前置物料质量：

```text
S00-S08 控制物料
  -> S09A/S09B 任务包
  -> S10/S11 候选正文和图表
  -> S12 集成候选稿
  -> S13 审稿发现
  -> S14/S15 局部修复
  -> S16 清洁交付
```

如果审查失败，主 agent 先把失败归因到对应阶段/物料，再只修受影响范围。整篇跑完之后，反复出现的问题才能进入阶段提示词、任务包、validator 或物料模板的系统改进。

## 独立性边界

`yxj-paper-os` 自己拥有阶段注册表、物料权威、validator、反馈生命周期和运行记录。它不依赖 OMX。OMX 或其他编排系统可以作为个人可选适配器，但不是公共入口、依赖或权威源。

## 核心阶段

- `S00`：目标、期刊、贡献边界和禁止路线
- `S01`：来源、引用、实验结果和证据盘点
- `S02`：期刊、模板文献、SOTA 和场域定位
- `S03`：贡献路线生成与挑战
- `S04`：主张-证据边界与禁止说法
- `S05`：论文主线和读者/审稿人问题链
- `S06`：对象、机制、变量和解释颗粒度
- `S07`：术语、修辞、语气和表面控制
- `S08`：图表、公式、算法契约
- `S09A/S09B`：选择控制材料并编译单元任务包
- `S10/S11`：生成正文、图表和 caption 候选
- `S12`：全文集成和一致性检查
- `S13`：对抗审稿，生成 actionable findings
- `S14/S15`：把 findings 转成局部修复任务并执行
- `S16`：导出、仓库卫生和交接
- `G01/G02`：运行治理与论文后派生输出

机器权威来自 `runtime/stage_registry.json` 和 `examples/stage-contracts/`。

## 新反馈生命周期对象

- `ReviewFeedbackPackage`：把用户/审稿反馈结构化，尚不授权修改。
- `FailureAttributionRecord`：把反馈归因到最近责任阶段/物料。
- `RepairTaskPacket`：当前论文的局部修复任务包。
- `RunRetrospectiveReport`：整篇运行后的复盘。
- `StageImprovementRecord`：基于反复失败模式改进提示词、任务包、validator 或物料模板。

这些对象补充既有的 `ReviewFinding`、`BackflowTask` 和 `TaskPacket`，不会替代它们的权威边界。

## 核心文档

- [`docs/ARCHITECTURE_OVERVIEW.md`](docs/ARCHITECTURE_OVERVIEW.md) — 紧凑架构不变量、边界与取舍。

1. [`docs/MANAGER_SURFACE_PROTOCOL.md`](docs/MANAGER_SURFACE_PROTOCOL.md)
2. [`docs/RUNTIME_PROTOCOL.md`](docs/RUNTIME_PROTOCOL.md)
3. [`docs/FEEDBACK_LIFECYCLE_PROTOCOL.md`](docs/FEEDBACK_LIFECYCLE_PROTOCOL.md)
4. [`docs/BACKFLOW_PROTOCOL.md`](docs/BACKFLOW_PROTOCOL.md)
5. [`docs/MATERIAL_SCHEMA.md`](docs/MATERIAL_SCHEMA.md)
6. [`docs/TOPOLOGY.md`](docs/TOPOLOGY.md)
7. [`docs/VALIDATION_AND_TESTING.md`](docs/VALIDATION_AND_TESTING.md)
8. [`docs/STANDARD_PAPER_WORKSPACE.md`](docs/STANDARD_PAPER_WORKSPACE.md)
9. [`docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md`](docs/LATEX_SOURCE_WRITEBACK_PROTOCOL.md)
10. [`docs/NATURE_STAGE_OVERLAY_SPEC.md`](docs/NATURE_STAGE_OVERLAY_SPEC.md)
11. [`docs/stages/README.md`](docs/stages/README.md) — 双语逐阶段说明，覆盖功能、输入、任务包、输出、validator 与实现索引。

## 验证

```bash
python3 scripts/verify_lifecycle_contract.py
python3 scripts/verify_stage_registry.py
python3 scripts/verify_stage_contracts.py
python3 scripts/verify_stage_overlays.py
python3 scripts/verify_paper_workspace_contract.py
python3 scripts/verify_latex_writeback_contract.py
python3 scripts/verify_latex_writeback_execution.py
```

## 完成规则

论文生产节点只有在候选输出、validator 证据、已提交状态和 scoped stale/backflow 状态都被记录后才算完成。审稿发现默认生成局部修复路径，不授权整篇重写。
