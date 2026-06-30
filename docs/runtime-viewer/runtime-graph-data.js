window.PPG_RUNTIME_GRAPH = (() => {
  const meta = {
    title: 'PPG Runtime 人工把握视图',
    subtitle: 'Phase8 本地 runtime state surface：显式物料图、前沿、stale/backflow 与交付门可见',
    status: {
      baseline: 'Phase8 本地插件/runtime surface 已进入实现：adapter 报告与前端状态面板同源',
      scope: '当前视图同时展示 stage taxonomy 与 Phase7 fixture-backed runtime state；仍不代表已 live-install/publish',
      next: '后续可在明确授权后扩展 live graph import / install / marketplace；Phase8 只做本地只读 surface',
    },
    canvas: { width: 2260, height: 1680 },
  };
  const legend = {
    material: '物料正向流',
    dispatch: '主 Agent 派发',
    validation: '验证与门控',
    graph: '图状态读写',
    backflow: '审核回流',
    governance: '治理与 sidecar',
  };
  const defaultVisibleKinds = ['material', 'dispatch', 'validation', 'graph', 'backflow', 'governance'];
  const layers = [
    { id: 'L0', y: 30, h: 280, title: 'L0 控制面', subtitle: '人类授权、主 Agent、物料图、验证器、任务包总线', tone: 'control' },
    { id: 'L1', y: 335, h: 170, title: 'L1 基础材料', subtitle: '需求语义契约与来源/证据盘点', tone: 'source' },
    { id: 'L2', y: 535, h: 170, title: 'L2 研究与 claim 准入', subtitle: '场景/SOTA、贡献选项、证据到主张的门控', tone: 'research' },
    { id: 'L3', y: 735, h: 170, title: 'L3 论文结构设计', subtitle: '主脊、对象颗粒度、术语修辞、图表形式计划', tone: 'design' },
    { id: 'L4', y: 935, h: 170, title: 'L4 写作与形式产出', subtitle: '正文任务包、文本单元、图表/caption/形式对象', tone: 'production' },
    { id: 'L5', y: 1135, h: 170, title: 'L5 集成、审核、回流', subtitle: '集成候选稿、对抗审核、回流任务、局部再生成', tone: 'review' },
    { id: 'L6', y: 1335, h: 200, title: 'L6 导出与论文后派生', subtitle: '交付包、最终论文产物、PPT/专利/Nature 等派生 sidecar', tone: 'delivery' },
  ];
  const nodeRows = [
    ['OWNER','control','control',210,82,250,92,'Human owner','人类作者/语义权威','提供需求、边界、审稿偏好和关键取舍，批准会改变论文核心语义的决策。',['真实写作需求','目标期刊或读者','可接受风险','核心禁区'],['语义授权','重大决策','边界修订','最终接受或退回'],['是否涉及核心语义改变'],['S00']],
    ['CTRL','controller','control',520,72,400,112,'Main Agent / Runtime Controller','主 Agent / Runtime 控制器','观察物料图，选择前沿节点，编译任务包，调度 subagent 或程序，收集候选产物，执行验证和提交。',['Owner 决策','物料图状态','验证报告','回流任务'],['TaskPacket','MaterialBundle','调度命令','提交或回滚决策'],['只有主 Agent 可以宣布图节点完成'],['任意 stale 节点']],
    ['GRAPH','graph','control',980,72,360,112,'Versioned Material Graph / Ledger','版本化物料图 / Ledger','保存节点、边、版本、依赖、验证器、来源锚点、stale 传播和 sidecar 状态。',['候选产物','验证结果','依赖变化','回流标记'],['可执行前沿','物料版本','stale 集合','可视化数据'],['schema 校验','依赖完整性校验','版本一致性校验'],['CTRL']],
    ['VALIDATORS','validator','control',1400,72,330,112,'Validator Registry','验证器注册表','集中管理 schema、证据、引用、审稿体验、渲染、导出和仓库卫生检查。',['候选物料','目标节点契约','期刊模板','证据锚点'],['通过/失败','错误定位','严重度','回流建议'],['主 Agent 选择并解释验证器'],['S14']],
    ['G01','sidecar','governance',1785,72,300,112,'Runtime governance sidecar','G01 Runtime 治理 sidecar','保存权限、技能、部门元数据、路线记录和状态控制，不直接进入正文认知链。',['state','permissions','department metadata'],['skill registry','route/governance records','state controls','authority limits'],['是否越权','是否污染写作物料'],['CTRL']],
    ['BUS','bus','control',520,212,1210,70,'TaskPacket + Structured MaterialBundle Bus','任务包 + 结构化物料包总线','把大上下文变成结构化包，而不是压缩成摘要。每个环节只负责一个有边界的产物。',['任务目标','强制控制项','证据和来源锚点','局部上下文','可选背景','禁用路线','验证器','返回格式'],['可派发任务包','subagent 输入包','程序转换输入'],['字段完整性','上下文边界','禁止路线存在性'],['CTRL']],

    ['S00','stage','root',210,360,300,126,'Owner semantic contract','S00 人类需求与语义契约','把人的真实写作目的转成论文 runtime 可执行的约束，确定什么能自动推进，什么必须回到人类。',['human need','paper profile','evidence summary'],['profile','motivation','core decisions','forbidden routes'],['目标具体','禁用路线显式','证据足以进入后续阶段'],['OWNER']],
    ['S01','stage','inventory',560,360,300,126,'Source/citation/evidence inventory','S01 来源、引用、证据盘点','建立论文能够使用的真实材料边界，防止后续写作脱离证据。',['files','BibTeX','result dirs','locators'],['source map','citation bank','evidence bank','Nature source inventory'],['路径可访问','引用字段完整','证据可追溯'],['S00']],

    ['S02','analysis','research',210,560,300,126,'Research / scene / template / SOTA','S02 研究场景、模板、SOTA 分析','把材料放入读者、期刊模板、领域争论和相关工作的位置中。',['source map','venue','exemplars'],['research dossier','reader package','search strategy','template or journal profile'],['场景覆盖读者问题','模板约束可执行','SOTA 可引用'],['S01']],
    ['S03','analysis','research',560,560,300,126,'Novelty / contribution options','S03 新颖性与贡献选项','产生可选贡献路线，但必须经过证据可承载性门控；不能绕过 S04 直接进入写作主脊。',['research','evidence','SOTA','motivation'],['contribution options','evidence-readiness','risk list'],['贡献可被证据支持','风险显式','避免过度声明'],['S02','S04']],
    ['S04','gate','claim',910,560,300,126,'Evidence-to-claim admissibility','S04 证据到主张的准入门','把贡献候选、实验、引用和观察变成可写入论文的 claim capsule，确定哪些话能说、说到什么强度。',['evidence bank','citations','results','contribution options'],['claim capsules','result packages','claim visibility','data availability','admitted contribution scope'],['每个 claim 有证据锚点','结论强度不过载','数据可用性明确'],['S01','S03','S00']],

    ['S05','design','spine',210,760,300,126,'Paper spine / reader questions','S05 论文主脊与读者问题','形成论文从问题到贡献到证据的主线，定义读者每一节需要得到的答案。',['motivation','contribution','template','claims'],['reader spine','reviewer question map','rationale matrix'],['章节问题递进','主线单一','读者疑问被覆盖'],['S03','S04']],
    ['S06','design','spine',560,760,300,126,'Object / granularity design','S06 对象表示与颗粒度设计','决定论文里哪些对象、变量、机制、图表和术语要出现到什么细度。',['spine','questions','template','claim visibility'],['object representation','section budget','load budget','explanation ladder'],['概念层级不混乱','读者负荷可控','支撑 claim 可见性'],['S05']],
    ['S07','design','surface',910,760,300,126,'Rhetoric / terminology / surface controls','S07 修辞、术语与表层控制','控制语气、术语、句式、段落组织和论文表面，防止概念正确但表达失焦。',['object design','claim visibility','evidence wording'],['construction matrix','rhetorical matrix','terminology register','surface rules'],['术语一致','claim 强度匹配','表层贴近目标期刊'],['S06','S04']],
    ['S08','design','visual',1260,760,300,126,'Visual / formal planning','S08 图表与形式对象规划','为图、表、公式、算法、补充材料建立契约；必须同时吃主脊、章节功能预算和 claim/evidence。',['reader spine','section/function budget','claims/evidence'],['visual budget','figure contract','aesthetic profile','panel evidence','backend route'],['图有论证功能','panel 绑定证据','导出路径明确'],['S05','S06','S04']],

    ['S09A','packet','writing',210,960,300,126,'Control-material selection','S09A 控制物料选择','从 claim、主脊、颗粒度和表层规则中选择当前目标单元必需的控制物料，避免把全部上下文倒进写作包。',['claim control','spine control','granularity control','surface rules','target unit'],['selected control bundle','control priority map','missing-control report'],['控制项足够且不过载','冲突优先级明确','缺失物料显式'],['S04','S05','S06','S07']],
    ['S09B','packet','writing',560,960,300,126,'Per-unit task packet assembly','S09B 单元任务包组装','把选定控制物料、证据锚点和返回格式编译成可派发给单个 subagent 的 WritingTaskPacket。',['selected control bundle','evidence anchors','target unit','return format'],['task packet','section move plan','single-writer lock'],['任务包字段完整','目标小节有边界','completion_forbidden 为真'],['S09A','S14','S15']],
    ['S10','production','writing',910,960,300,126,'Main-text production','S10 正文产出','基于 S09B 任务包写出候选文本单元，不能自行宣布最终完成。',['task packet','construction','terminology','claim/evidence'],['candidate text units'],['claim 有锚点','术语一致','段落功能满足任务包'],['S09B','S07']],
    ['S11','production','visual',1260,960,300,126,'Figure / caption / formal production','S11 图表、caption 与形式对象产出','生成图、表、caption、算法或公式相关产物；数据/证据必须来自 S01/S04，不能由图表 agent 自造。',['figure contract','panel evidence','source data locators','result package','caption constraints'],['figure stats','image integrity','caption brief','figure export bundle','artifacts'],['图像可打开','caption 承接 claim','数据可追踪'],['S08','S04','S01']],

    ['S12','integration','integration',210,1160,300,126,'Integration / consistency pass','S12 集成与一致性检查','合并正文和图表，检查术语、claim、引用、图文关系和章节递进。',['candidate modules','figures','terminology','claims'],['integrated manuscript candidate','consistency findings'],['跨章节术语一致','图文互相引用','claim 不漂移'],['S10','S11','S07']],
    ['S13','review','review',560,1160,300,126,'Adversarial review / loss','S13 对抗审核与损失信号','审核器只产生 findings 和 loss，不直接重写全文。',['manuscript','evidence','narrative','figures/export'],['review reports','reader surface report','rendered gate','validator report'],['审稿人视角问题','证据断裂','表层和模板问题','导出问题'],['S14']],
    ['S14','review','backflow',910,1160,300,126,'Backflow compilation','S14 回流任务编译','把审核 findings 映射到最近责任物料，而不是从头重写整篇论文；必要时先回到 S09A 重选控制物料。',['findings','graph state','affected materials'],['narrative backflow task','repair packets','polishing/response plans'],['定位最近责任节点','标记影响下游','修复任务足够小'],['S04','S07','S09A','S09B','S15']],
    ['S15','repair','backflow',1260,1160,300,126,'Repair / local regeneration','S15 局部修复与再生成','只重写受影响的物料、文本或图表，并重新触发必要验证；文本修复优先回到 S09B 再生成任务包。',['backflow task','target material','stale downstream set'],['revised material/text/figure','regenerated task packet when needed','updated validator report'],['目标修复通过','下游 stale 清理','未破坏无关部分'],['S04','S07','S09B','S10','S12']],

    ['S16','delivery','delivery',560,1378,300,126,'Export / handoff / delivery','S16 导出、交付与交接','只接收已通过集成/审核闭合或局部修复闭合的交付包，完成论文、图表、补充材料、仓库卫生和交接报告。',['clean final candidate','review closure','repair-complete delivery package','figures','repository state'],['export manifest','repository hygiene report','manager handoff reports'],['导出可打开','引用和图表路径完整','仓库风险明确'],['S12','S13','S15']],
    ['FINAL','final','delivery',910,1378,420,126,'Final Paper Artifact','最终论文产物','正文、图表、补充材料、证据链、导出清单和给人的交接说明。',['S16 delivery package'],['manuscript','figures','supplement','provenance','owner handoff'],['人类最终验收'],['S13','S00']],
    ['G02','sidecar','derivative',1410,1378,330,126,'Derivative/post-paper sidecar','G02 论文后派生 sidecar','稳定论文之后再派生 PPT、专利边界、Nature 吸收包等，不干扰当前论文完成。',['stable paper','owner request'],['presentation plan','patent boundary','Nature absorption package'],['是否晚于论文稳定点','是否不回写污染正文'],['S16']],
  ];
  const nodes = nodeRows.map(([id,type,phase,x,y,w,h,title,titleZh,description,inputs,outputs,validators,backflowTargets]) => ({ id,type,phase,x,y,w,h,title,titleZh,description,inputs,outputs,validators,backflowTargets }));
  const edges = [
    ['c1','governance','OWNER','CTRL','需求/决策'], ['c2','graph','CTRL','GRAPH','读写物料图'], ['c3','validation','GRAPH','VALIDATORS','验证请求'], ['c4','validation','VALIDATORS','CTRL','验证报告'], ['c5','dispatch','CTRL','BUS','编译任务包'],
    ['m00','material','S00','S01','profile -> inventory'], ['m01','material','S01','S02','source map'], ['m02','material','S02','S03','research dossier'], ['m03','material','S01','S04','evidence bank'], ['m04','material','S03','S04','contribution options -> claim gate'], ['m05','material','S04','S05','admitted claim/contribution capsules'], ['m06','material','S05','S06','reader spine'], ['m07','material','S06','S07','object design'], ['m08','material','S05','S08','spine to figures'], ['m08b','material','S06','S08','section/function budget'], ['m09','material','S04','S09A','claim control'], ['m10','material','S05','S09A','spine control'], ['m11','material','S06','S09A','granularity control'], ['m12','material','S07','S09A','surface control'], ['m13','material','S08','S11','figure contract'], ['m13a','material','S01','S11','source data locators'], ['m13b','material','S04','S11','panel evidence/result package'], ['m14','material','S09A','S09B','selected control bundle'], ['m14b','material','S09B','S10','text task packet'], ['m15','material','S10','S12','candidate text'], ['m16','material','S11','S12','figure bundle'], ['m17','material','S12','S13','integrated candidate'], ['m18','material','S13','S14','findings/loss'], ['m19','material','S14','S15','repair packets'], ['m20','material','S15','S16','repair-complete delivery package'], ['m20b','material','S12','S16','clean final candidate'], ['m20c','material','S13','S16','review closure'], ['m21','material','S16','FINAL','final artifact'],
    ['v1','validation','S04','VALIDATORS','claim/evidence gate','rightRail'], ['v2','validation','S12','VALIDATORS','consistency gate','rightRail'], ['v3','validation','S13','VALIDATORS','review gate','rightRail'], ['v4','validation','S16','VALIDATORS','export gate','rightRail'],
    ['b1','backflow','S14','S07','L1-L2 表层/术语','leftRail'], ['b2','backflow','S14','S04','L3 claim/evidence','leftRail'], ['b3','backflow','S14','S00','L4 语义重置','leftRail'], ['b4','backflow','S15','S10','局部文本再生成'], ['b5','backflow','S15','S12','重新集成验证'], ['b6','backflow','S14','S09A','修复范围重选控制物料'], ['b7','backflow','S15','S09B','再生成任务包'],
    ['g1','governance','G01','CTRL','权限/路线控制'], ['g2','governance','G01','GRAPH','状态控制'], ['g3','governance','S16','G02','论文后派生'],
  ].map(([id,kind,source,target,label,route]) => ({ id,kind,source,target,label,route }));
  nodes.filter((node) => node.id.startsWith('S')).forEach((node, index) => edges.push({ id: `d${String(index).padStart(2,'0')}`, kind: 'dispatch', source: 'BUS', target: node.id, label: 'dispatch' }));

  const roadmap = {
    canvas: { width: 1760, height: 1260 },
    lanes: [
      { id: 'R0', y: 24, h: 150, title: '控制闭环', subtitle: '人类授权 -> 主 Agent -> 任务包 -> 验证器/物料图', tone: 'control' },
      { id: 'R1', y: 210, h: 130, title: '1 基础材料', subtitle: '把人的需求和证据边界变成可执行材料', tone: 'source' },
      { id: 'R2', y: 370, h: 130, title: '2 研究与 claim', subtitle: '从研究场景到可被证据支持的主张', tone: 'research' },
      { id: 'R3', y: 530, h: 130, title: '3 论文设计', subtitle: '组织读者路线、概念颗粒度、术语表层和图表契约', tone: 'design' },
      { id: 'R4', y: 690, h: 130, title: '4 内容生产', subtitle: '正文任务包、正文产出、图表产出汇入集成稿', tone: 'production' },
      { id: 'R5', y: 850, h: 150, title: '5 审核回流', subtitle: '审核只产生 loss，回流到最近责任物料并局部再生成', tone: 'review' },
      { id: 'R6', y: 1040, h: 150, title: '6 交付派生', subtitle: '最终交付和论文稳定后的外部派生', tone: 'delivery' },
    ],
    nodes: [
      ['OWNER',190,60,180,78], ['CTRL',420,60,210,78], ['BUS',680,60,230,78], ['VALIDATORS',960,60,210,78], ['GRAPH',1220,60,210,78], ['G01',1480,60,210,78],
      ['S00',190,236,220,78], ['S01',500,236,220,78],
      ['S02',190,396,220,78], ['S03',500,396,220,78], ['S04',810,396,220,78],
      ['S05',190,556,220,78], ['S06',500,556,220,78], ['S07',810,556,220,78], ['S08',1120,556,220,78],
      ['S09A',190,716,200,78], ['S09B',430,716,200,78], ['S10',670,716,200,78], ['S11',910,716,200,78], ['S12',1150,716,200,78],
      ['S13',190,882,220,78], ['S14',500,882,220,78], ['S15',810,882,220,78],
      ['S16',500,1080,220,78], ['FINAL',810,1080,260,78], ['G02',1160,1080,230,78],
    ].map(([id,x,y,w,h]) => ({ id,x,y,w,h })),
    edges: [
      ['r-c1','OWNER','CTRL','需求/批准','governance'], ['r-c2','CTRL','BUS','编译任务包','dispatch'], ['r-c3','BUS','VALIDATORS','验证规则','validation'], ['r-c4','VALIDATORS','GRAPH','验证报告','validation'], ['r-c5','GRAPH','CTRL','图状态','graph'], ['r-c6','G01','CTRL','治理边界','governance'],
      ['r-01','S00','S01','profile / forbidden routes','material'], ['r-02','S01','S02','source map','material'], ['r-03','S02','S03','research dossier','material'], ['r-04','S03','S04','贡献候选进入证据门','material'], ['r-05','S04','S05','可写 claim','material'], ['r-06','S05','S06','reader spine','material'], ['r-07','S06','S07','对象与颗粒度','material'], ['r-08','S07','S09A','表层控制进入控制选择','material'], ['r-09','S09A','S09B','选定控制物料','material'], ['r-10','S09B','S10','正文任务包','material'], ['r-11','S10','S12','候选文本','material'], ['r-12','S12','S13','集成候选稿','material'], ['r-clean','S13','S16','review closure / clean export','material'], ['r-15','S16','FINAL','最终论文包','material'],
      ['r-repair1','S13','S14','findings / loss','material'], ['r-repair2','S14','S15','repair packets','material'], ['r-repair3','S15','S16','repair-complete delivery-ready','material'],
      ['r-b0','S06','S08','section/function budget','material'], ['r-b1','S05','S08','图表/形式计划','material'], ['r-b1a','S04','S08','claim/evidence to visual plan','material'], ['r-b2a','S01','S11','source data locators','material'], ['r-b2b','S04','S11','panel evidence/result package','material'], ['r-b2','S08','S11','figure contract','material'], ['r-b3','S11','S12','图表与 caption','material'], ['r-f1','S04','S09A','claim control','material'], ['r-f2','S05','S09A','spine control','material'], ['r-f3','S06','S09A','granularity control','material'],
      ['r-v1','S04','VALIDATORS','claim gate','validation','rightRail'], ['r-v2','S12','VALIDATORS','consistency gate','validation','rightRail'], ['r-v3','S13','VALIDATORS','review gate','validation','rightRail'], ['r-v4','S16','VALIDATORS','export gate','validation','rightRail'],
      ['r-r1','S14','S04','claim/evidence 回流','backflow','backRail'], ['r-r2','S14','S07','术语/表层回流','backflow','backRail'], ['r-r3','S15','S10','局部文本再生成','backflow'], ['r-r4','S15','S12','重新集成','backflow'], ['r-r5','S15','S04','必要时重开 claim 门','backflow','backRail'], ['r-r6','S14','S09A','重选控制物料','backflow'], ['r-r7','S15','S09B','再生成任务包','backflow'],
      ['r-d1','S16','G02','论文后派生','governance'],
    ].map(([id,source,target,label,kind,route]) => ({ id,source,target,label,kind,route })),
  };

  const presets = [
    { id: 'all', label: '全流程', nodes: ['OWNER','CTRL','GRAPH','VALIDATORS','BUS','G01','S00','S01','S02','S03','S04','S05','S06','S07','S08','S09A','S09B','S10','S11','S12','S13','S14','S15','S16','FINAL','G02'] },
    { id: 'spine', label: '论文主线', nodes: ['S00','S01','S02','S03','S04','S05','S06','S07','S08','S09A','S09B','S10','S11','S12','S13','S14','S15','S16','FINAL'] },
    { id: 'writing', label: '写作汇入', nodes: ['S04','S05','S06','S07','S08','S09A','S09B','S10','S11','S12'] },
    { id: 'figures', label: '图表支路', nodes: ['S01','S04','S05','S06','S08','S11','S12'] },
    { id: 'review', label: '审核回流', nodes: ['S12','S13','S14','S15','S04','S07','S09A','S09B','S10'] },
    { id: 'control', label: '控制面', nodes: ['OWNER','CTRL','GRAPH','VALIDATORS','BUS','G01'] },
    { id: 'runtime-core', label: '执行核心', nodes: ['CTRL','GRAPH','VALIDATORS','BUS','S09A','S09B','S13','S14','S15','S16'] },
  ];
  const runtimeState = {
  "active_versions": [
    {
      "active_node": "claim_boundary_map_v2",
      "artifact_path": "examples/materials/claim_boundary_map.v2.yaml",
      "material_id": "claim_boundary_map",
      "status": "committed",
      "version": "v2"
    },
    {
      "active_node": "evidence_inventory_v1",
      "artifact_path": "examples/materials/evidence_inventory.v1.yaml",
      "material_id": "evidence_inventory",
      "status": "committed",
      "version": "v1"
    },
    {
      "active_node": "reader_spine_v1",
      "artifact_path": "examples/materials/reader_spine.v1.yaml",
      "material_id": "reader_spine",
      "status": "committed",
      "version": "v1"
    }
  ],
  "backflow_tasks": [
    {
      "artifact_path": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml",
      "id": "phase7_overclaim_review_finding_v1_backflow_v1",
      "label": "Phase7 overclaim backflow task v1",
      "node_type": "backflow_task",
      "source_findings": [
        "phase7_overclaim_review_finding_v1"
      ],
      "status": "planned",
      "summary": "Compiled local backflow task that maps claim_overreach to active ClaimBoundaryMap repair target.",
      "targets": [],
      "version": "v1"
    },
    {
      "id": "repair_claim_boundary_task_v1",
      "label": "Repair ClaimBoundaryMap task v1",
      "node_type": "backflow_task",
      "source_findings": [
        "finding_overclaim_v1"
      ],
      "status": "validated",
      "summary": "Backflow task that creates claim_boundary_map_v2.",
      "targets": [
        "claim_boundary_map_v2",
        "claim_boundary_map_candidate_v3"
      ],
      "version": "v1"
    }
  ],
  "candidate_materials": [
    {
      "artifact_path": "examples/materials/claim_boundary_map.v3-candidate.yaml",
      "candidate_for": "claim_boundary_map",
      "id": "claim_boundary_map_candidate_v3",
      "label": "ClaimBoundaryMap v3 candidate",
      "material_id": "claim_boundary_map",
      "node_type": "material",
      "status": "candidate",
      "summary": "Candidate future revision; not active.",
      "version": "v3-candidate"
    }
  ],
  "closed_review_findings": [
    {
      "artifact_path": "examples/review_findings/phase7_overclaim.v1.yaml",
      "classified_repair": true,
      "closed_by": [
        "phase7_overclaim_closure_v1"
      ],
      "closure_status": "closed",
      "failure_type": "claim_overreach",
      "id": "phase7_overclaim_review_finding_v1",
      "invalidates": [
        "claim_boundary_map_v1"
      ],
      "label": "Phase7 finding: intro overclaim v1",
      "node_type": "review_finding",
      "primary_target": "claim_boundary_map_v1",
      "repair_tasks": [
        "phase7_overclaim_review_finding_v1_backflow_v1"
      ],
      "status": "validated",
      "summary": "Mock reviewer found universal safety overclaim in intro_draft_v1.",
      "version": "v1"
    }
  ],
  "completion_blockers": [
    "candidate claim_boundary_map_candidate_v3 cannot commit: candidate status must be validated before commit; candidate must declare supersedes=claim_boundary_map_v2; candidate must have supersedes edge claim_boundary_map_candidate_v3 -> claim_boundary_map_v2; candidate-specific validator edge is required; candidate-specific validation report reference is required"
  ],
  "delivery_gates": [
    {
      "artifact_path": "examples/delivery/phase7_delivery_gate.pass.yaml",
      "id": "phase7_delivery_gate_v1",
      "label": "Phase7 DeliveryGate v1",
      "node_type": "validation_report",
      "report_id": "phase7_delivery_gate_v1",
      "reported_by": [],
      "status": "validated",
      "summary": "DeliveryGate pass for the deterministic intro overclaim repair vertical slice.",
      "validates": [],
      "version": "v1"
    }
  ],
  "graph": {
    "edge_count": 31,
    "graph_id": "phase2-overclaim-material-graph",
    "node_count": 22,
    "source_path": "examples/runtime/overclaim-loop.phase7-after.json",
    "title": "Phase 7 Deterministic Overclaim Repair Vertical Slice"
  },
  "next_frontier": {
    "id": "claim_boundary_map_candidate_v3",
    "kind": "material",
    "priority": 5,
    "reason": "candidate_material_awaiting_validation_or_commit_plan"
  },
  "open_review_findings": [
    {
      "classified_repair": true,
      "closed_by": [],
      "closure_status": "open",
      "failure_type": "claim_overreach",
      "id": "finding_overclaim_v1",
      "invalidates": [
        "claim_boundary_map_v1"
      ],
      "label": "Finding: overclaim v1",
      "node_type": "review_finding",
      "primary_target": "claim_boundary_map_v1",
      "repair_tasks": [
        "repair_claim_boundary_task_v1"
      ],
      "status": "candidate",
      "summary": "Draft states stronger guarantee than evidence supports.",
      "version": "v1"
    }
  ],
  "owner_decisions": [],
  "review_closures": [
    {
      "artifact_path": "examples/delivery/phase7_overclaim_closure.v1.yaml",
      "id": "phase7_overclaim_closure_v1",
      "label": "Phase7 overclaim ReviewClosure v1",
      "node_type": "validation_report",
      "report_id": "phase7_overclaim_closure_v1",
      "reported_by": [
        "phase7_mock_reviewer_closure_v1"
      ],
      "status": "validated",
      "summary": "ReviewClosure proving the intro overclaim finding is locally repaired.",
      "validates": [
        "phase7_overclaim_review_finding_v1",
        "phase7_delivery_gate_v1"
      ],
      "version": "v1"
    }
  ],
  "schema_version": "ppg-runtime-state-report/v0.1",
  "stale_materials": [
    {
      "artifact_path": "examples/materials/claim_boundary_map.v1.yaml",
      "historical_superseded_by_active": true,
      "id": "claim_boundary_map_v1",
      "label": "ClaimBoundaryMap v1",
      "material_id": "claim_boundary_map",
      "node_type": "material",
      "on_active_control_path": false,
      "stale_reason": "Superseded by claim_boundary_map_v2 after overclaim review finding.",
      "status": "stale",
      "summary": "Old claim boundary version preserved for provenance.",
      "version": "v1"
    }
  ]
};

  const stageCoverage = {
  "canonical_stage_count": 20,
  "completion_boundary": "all canonical stages have PilotStageRun coverage; this is not a final manuscript/submission claim",
  "coverage_kind_counts": {
    "fixture_generated": 4,
    "owner_gated_deferred": 1,
    "script_checked": 5,
    "source_projected": 10
  },
  "exercise_level_counts": {
    "contract_only": 10,
    "deferred_with_gate": 1,
    "full_stage_exercised": 9
  },
  "graph_ref": "graph.json",
  "pilot_root": "examples/local-paper/security-state-aware-mixed-platoon",
  "pilot_stage_run_count": 20,
  "project_slug": "security-state-aware-mixed-platoon",
  "schema_version": "ppg-local-paper-full-pilot/v0.1",
  "stage_runs": [
    {
      "contract_ref": "examples/stage-contracts/S00.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S00.pilot-stage-run.json",
      "stage_id": "S00",
      "stage_name": "Owner semantic contract",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/S01.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S01.pilot-stage-run.json",
      "stage_id": "S01",
      "stage_name": "Source citation evidence inventory",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/S02.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S02.pilot-stage-run.json",
      "stage_id": "S02",
      "stage_name": "Research scene exemplar SOTA analysis",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S03.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S03.pilot-stage-run.json",
      "stage_id": "S03",
      "stage_name": "Novelty and contribution option analysis",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S04.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S04.pilot-stage-run.json",
      "stage_id": "S04",
      "stage_name": "Evidence-to-claim admissibility",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S05.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S05.pilot-stage-run.json",
      "stage_id": "S05",
      "stage_name": "Paper spine and reader-question synthesis",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S06.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S06.pilot-stage-run.json",
      "stage_id": "S06",
      "stage_name": "Object representation and granularity design",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S07.stage-contract.json",
      "coverage_kind": "fixture_generated",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S07.pilot-stage-run.json",
      "stage_id": "S07",
      "stage_name": "Rhetoric terminology and surface-control synthesis",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S08.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S08.pilot-stage-run.json",
      "stage_id": "S08",
      "stage_name": "Visual and formal object planning",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S09A.stage-contract.json",
      "coverage_kind": "script_checked",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S09A.pilot-stage-run.json",
      "stage_id": "S09A",
      "stage_name": "Control-material selection",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/S09B.stage-contract.json",
      "coverage_kind": "script_checked",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S09B.pilot-stage-run.json",
      "stage_id": "S09B",
      "stage_name": "Per-unit task packet assembly",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/S10.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S10.pilot-stage-run.json",
      "stage_id": "S10",
      "stage_name": "Main-text production",
      "status": "validated",
      "worker_packet_status": "linked_strict_packet"
    },
    {
      "contract_ref": "examples/stage-contracts/S11.stage-contract.json",
      "coverage_kind": "source_projected",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S11.pilot-stage-run.json",
      "stage_id": "S11",
      "stage_name": "Figure caption formal artifact production",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S12.stage-contract.json",
      "coverage_kind": "fixture_generated",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S12.pilot-stage-run.json",
      "stage_id": "S12",
      "stage_name": "Integration and consistency pass",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S13.stage-contract.json",
      "coverage_kind": "fixture_generated",
      "exercise_level": "contract_only",
      "run_ref": "stage-runs/S13.pilot-stage-run.json",
      "stage_id": "S13",
      "stage_name": "Adversarial manuscript review",
      "status": "validated",
      "worker_packet_status": "planned_with_blocker"
    },
    {
      "contract_ref": "examples/stage-contracts/S14.stage-contract.json",
      "coverage_kind": "script_checked",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S14.pilot-stage-run.json",
      "stage_id": "S14",
      "stage_name": "Backflow compilation and repair planning",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/S15.stage-contract.json",
      "coverage_kind": "fixture_generated",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S15.pilot-stage-run.json",
      "stage_id": "S15",
      "stage_name": "Repair execution and local regeneration",
      "status": "validated",
      "worker_packet_status": "linked_strict_packet"
    },
    {
      "contract_ref": "examples/stage-contracts/S16.stage-contract.json",
      "coverage_kind": "script_checked",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/S16.pilot-stage-run.json",
      "stage_id": "S16",
      "stage_name": "Export repository hygiene and handoff",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/G01.stage-contract.json",
      "coverage_kind": "script_checked",
      "exercise_level": "full_stage_exercised",
      "run_ref": "stage-runs/G01.pilot-stage-run.json",
      "stage_id": "G01",
      "stage_name": "Runtime governance registry",
      "status": "validated",
      "worker_packet_status": "not_required"
    },
    {
      "contract_ref": "examples/stage-contracts/G02.stage-contract.json",
      "coverage_kind": "owner_gated_deferred",
      "exercise_level": "deferred_with_gate",
      "run_ref": "stage-runs/G02.pilot-stage-run.json",
      "stage_id": "G02",
      "stage_name": "Derivative and post-paper outputs",
      "status": "owner_gated",
      "worker_packet_status": "not_required"
    }
  ],
  "worker_task_packet_status_counts": {
    "linked_strict_packet": 2,
    "not_required": 8,
    "planned_with_blocker": 10
  }
};

  return { meta, legend, defaultVisibleKinds, layers, nodes, edges, presets, roadmap, runtimeState, stageCoverage };
})();
