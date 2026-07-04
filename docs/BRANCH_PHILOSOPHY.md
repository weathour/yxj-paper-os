# yxj-paper-os 分支理念与外部 Skill 仓库清单

状态：当前分支设计文档。  
分支：`yxj-paper-os-slot-skill-redesign`  
基线提交：`b2a7597`  
记录日期：2026-07-04

## 1. 当前分支为什么存在

本分支面向交通与计算机/AI 论文场景；医学、临床和 medical-AI 专用写作路线不作为默认目标。

这个分支不是对旧 `yxj-paper-os` 做小修小补，而是一次有意的清空重建。

旧版本尝试把论文写作管理为完整的 Paper Production Graph runtime：阶段注册、物料图、任务包、候选输出、验证器、回流、修复、导出、运行复盘等全部内建。理论上完整，但实际使用中暴露出几个问题：

1. 上下文过长，主 agent 难以稳定把握当前责任边界。
2. 内部审核、阶段标准、validator 和 worker 输出之间容易漂移。
3. runtime 过重，用户真正需要的往往只是“把已有目标期刊 + 已有实验材料组织成可写论文的设计包”。
4. 论文正文、图件、引用、润色、审稿模拟等能力已有更成熟的外部 skills / repos，可以 handoff，而不必在本仓库重造。

因此，本分支的基本判断是：

> **保留 yxj-paper-os 的上游判断力，放弃自建完整论文生产 runtime。**

## 2. 新版一句话定义

新版 `yxj-paper-os` 应该是：

```text
Codex 原生 paper-planning plugin。
它不直接写论文，而是把“目标期刊 + 已完成实验材料”整理成高质量 WRITING_DESIGN_PACK.md，
再把写作、图件、引用、润色、审稿和格式化交给成熟外部 skills。
```

等价地说，旧系统从：

```text
Paper Production Graph Runtime
```

重构为：

```text
Paper Design Slot System + External Codex Skills
```

## 3. 当前分支的架构原则

### 3.1 只保留上游控制

保留这些问题的分析与设计：

- 目标期刊和文章类型是什么？
- 已有实验、图、表、代码、数据和文献材料在哪里？
- 哪些 claim 有证据支持，哪些不能说？
- 贡献应该如何表述，哪些路线需要拒绝？
- 读者/审稿人的问题链是什么？
- 论文结构、段落功能、对象颗粒度、术语、语气、修辞如何控制？
- 图表故事线和 caption 边界是什么？

### 3.2 不再内建生产 runtime

本仓库不再原生承担：

- 全文正文生成；
- 投稿级图件生产；
- 文献检索和 BibTeX 自动补全；
- reviewer simulation；
- 全文润色；
- LaTeX 模板适配和最终导出；
- 自动投稿、上传、发表、接收状态判断；
- S00-S16/G01/G02 全阶段 runtime；
- 大型 validator matrix；
- recursive worker orchestration。

### 3.3 Markdown 槽位优先

未来工作区应优先是简单 Markdown 槽位，而不是 JSON graph：

```text
paper_project/
  00_META.md
  OWNER_DECISIONS.md
  STALE_FLAGS.md

  phase0/
    00_project_brief.md
    01_target_journal_profile.md
    02_material_inventory.md
    03_evidence_inventory.md
    04_source_and_citation_bank.md

  phase1/
    10_research_dossier.md
    11_exemplar_language_profile.md
    12_contribution_options.md
    13_claim_evidence_map.md
    14_wording_boundary.md
    15_limitation_and_risk_matrix.md

  phase2/
    20_reader_spine.md
    21_manuscript_outline.md
    22_object_granularity.md
    23_surface_control.md
    24_visual_plan.md
    25_WRITING_DESIGN_PACK.md

  phase3_draft/
  phase4_refine/
  phase5_final/
```

其中 Phase 0-2 是 `yxj-paper-os` 的原生责任；Phase 3 之后交给外部 skills。

## 4. 目标原生 Skill 划分

MVP 版本优先做 6 个原生 skills：

| Skill | 责任 |
|---|---|
| `yxj-paper-init` | 初始化 Markdown 槽位工作区 |
| `yxj-phase0-intake` | 项目入口、目标期刊、文章类型、owner gates |
| `yxj-phase0-materials` | 材料、证据、来源、引用候选盘点 |
| `yxj-phase1-claim-boundary` | contribution options、claim-evidence、wording boundary、limitation/risk |
| `yxj-phase2-reader-spine` | reader spine、manuscript outline、段落功能 |
| `yxj-design-pack-compiler` | 编译 `WRITING_DESIGN_PACK.md` 并生成外部 skill handoff |

完整版本再补 4 个：

| Skill | 责任 |
|---|---|
| `yxj-phase1-research-dossier` | SOTA、exemplar、语言画像 |
| `yxj-phase2-object-granularity` | 对象、变量、机制、解释颗粒度 |
| `yxj-phase2-surface-control` | 术语、语气、修辞、句法和文本组织控制 |
| `yxj-phase2-visual-plan` | 图表、caption、supplement story plan |

## 5. 最终原生产物

`yxj-paper-os` 的最终原生产物不是 manuscript，而是：

```text
phase2/25_WRITING_DESIGN_PACK.md
```

该文件应固定包含：

1. Project Route
2. Material Boundary
3. Core Contribution
4. Claim-Evidence Map
5. Allowed / Forbidden Wording
6. Reader Spine
7. Object and Granularity
8. Surface Control
9. Visual Plan
10. External Skill Handoff

外部 skills 必须读取这个 design pack；它们可以生成候选稿、润色稿、图件或引用建议，但不能越过 claim/evidence/owner gates。

## 6. 提到的外部 Skill / 仓库清单

下面列出此前讨论中提到、且适合交通与计算机/AI 论文场景的 handoff 目标或参考对象。核验时间为 2026-07-04；采用前仍应重新检查仓库活跃度、license、安装方式和 skill 目录结构。当前已在 `references/external/` 以 Git submodule 方式固定这些参考仓库。

### 6.1 优先 handoff 候选

| 用途 | 仓库 / 项目 | 地址 | 本仓库使用方式 | 边界 |
|---|---|---|---|---|
| Nature 风格写作、润色、图件、引用、审稿等 | `Yuan1z0825/nature-skills` | <https://github.com/Yuan1z0825/nature-skills> | 作为 Phase 3+ 主要外部 handoff；可路由到 `nature-writing`、`nature-polishing`、`nature-figure`、`nature-citation`、`nature-reviewer`、`nature-data`、`nature-response` 等 | 不把它 vendored 进本仓库；只通过 design pack 显式交接 |
| ML/CV/NLP 论文写作 | `Master-cai/Research-Paper-Writing-Skills` | <https://github.com/Master-cai/Research-Paper-Writing-Skills> | AI/ML/算法/实验 repo 到 paper 的外部写作路线候选 | 仅在主题适配时使用；不让其改写 claim boundary |
| Codex-native academic research suite | `Imbad0202/academic-research-skills-codex` | <https://github.com/Imbad0202/academic-research-skills-codex> | 可拆用 research/write/review/revise/finalize 中适合的阶段；作为成熟 workflow 参考 | 不直接复制 10+ stage 大流程，避免重回复杂 runtime |
| 原版 academic research skills | `Imbad0202/academic-research-skills` | <https://github.com/Imbad0202/academic-research-skills> | 作为 Claude Code 原版参考；对比 Codex 版结构 | 不是本插件直接依赖 |

### 6.2 参考型项目，不作为默认 Codex handoff

| 用途 | 仓库 / 项目 | 地址 | 本仓库使用方式 | 边界 |
|---|---|---|---|---|
| 多智能体论文写作/图件团队参考 | `aristoteleo/PantheonOS` | <https://github.com/aristoteleo/PantheonOS> | 参考其 paper-writing / graph-maker team 思路 | 它是独立 multi-agent framework，不是本仓库默认运行底座 |
| Overleaf 内联审稿/修改 | `PaperDebugger/paperdebugger` | <https://github.com/PaperDebugger/paperdebugger> | 作为 reviewer/revision UX 参考，或后期人工使用工具 | 不作为 Codex plugin 内部依赖 |
| LaTeX/Overleaf 引用插入 | `cheyanneshariat/OverCite` | <https://github.com/cheyanneshariat/OverCite> | 作为引用补全/编辑器集成参考 | 不承担 claim-support verification；只处理 citation insertion 辅助 |

### 6.3 本地/通用 skill 名称，仓库未在本分支锁定

此前讨论还提到这些 skill 名称或能力，但当前分支不锁定其仓库来源：

| 名称 | 角色 | 当前处理 |
|---|---|---|
| `scientific-writing` | 通用 IMRAD / 科学论文写作 | 作为可能已安装的本地/社区 skill；本仓库只在 design pack 里声明 handoff 输入 |
| `citation-management` | 引用管理 | 作为辅助技能类别；具体工具在项目中按需确认 |
| `PaperMentor` | Overleaf inline feedback / writing tutor | 找到论文/项目描述，但未在本分支锁定 GitHub 仓库；暂列参考概念 |
| `PaperDebugger` | 审稿与编辑辅助 | 已加入 `references/external/paperdebugger`；默认仍作为外部工具而非内置依赖 |
| `OverCite` | citation insertion | 未加入当前参考 submodules；默认仍作为外部工具而非内置依赖 |

## 7. 外部仓库采用规则

1. **参考仓库用 submodule 固定，不默认 vendoring。** `references/external/` 只保存上游仓库指针与工作副本，外部 skill/repo 不直接复制进插件运行面；除非明确需要并记录 license、来源 commit 和同步策略，否则不要把第三方文件改写成插件自有文件。
2. **Design pack 是唯一 handoff 契约。** 外部 skill 必须消费 `WRITING_DESIGN_PACK.md`，不能从模型记忆推断 claim、证据、target journal 或 owner gates。
3. **只交候选，不交权威。** 外部 skill 可以生成候选正文、图件、引用、审稿意见或润色稿；最终是否采用由 owner / 本插件后续确认逻辑决定。
4. **禁止越权。** 外部 skill 不得加强 claim、不许伪造 citation、不许绕过 limitation/risk、不许声明投稿/发表完成。
5. **每次采用前重新核验。** 仓库地址、license、目录结构、安装方式、活跃度都可能变化；不得长期依赖本文件的旧快照。

## 8. 下一步落地顺序

1. 添加 `templates/slots/`。
2. 添加 `scripts/verify_slot_templates.py`。
3. 添加 `yxj-paper-init`。
4. 添加最小示例工作区。
5. 添加 `yxj-design-pack-compiler`。
6. 再逐步增加 Phase 0-2 的 slot-filling skills。

每一步都必须保持：

```bash
python3 /home/weathour/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

通过。
