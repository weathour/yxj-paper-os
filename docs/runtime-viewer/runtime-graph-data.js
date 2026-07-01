window.PPG_RUNTIME_GRAPH = (() => {
  const meta = {
    title: 'PPG Runtime 人工把握视图',
    subtitle: 'Paper OS runtime state surface：显式物料图、stage-local Nature overlay、前沿、stale/backflow 与交付门可见',
    status: {
      baseline: 'Paper OS runtime surface：adapter、stage coverage 与 Nature overlay 绑定同源',
      scope: '当前视图同时展示 stage taxonomy、deterministic fixture-backed runtime state、readiness evidence 与 stage-local overlay；仍不代表已 install/publish/submission ready',
      next: '后续真实论文生产运行仍由主 Agent 按 StageContract、TaskPacket、overlay validator 与 owner gate 调度；安装/marketplace 需额外授权',
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
    { id: 'L6', y: 1335, h: 200, title: 'L6 导出与论文后派生', subtitle: '交付包、最终论文产物、PPT/专利/期刊 profile 等派生 sidecar', tone: 'delivery' },
  ];
  const nodeRows = [
    ['OWNER','control','control',210,82,250,92,'Human owner','人类作者/语义权威','提供需求、边界、审稿偏好和关键取舍，批准会改变论文核心语义的决策。',['真实写作需求','目标期刊或读者','可接受风险','核心禁区'],['语义授权','重大决策','边界修订','最终接受或退回'],['是否涉及核心语义改变'],['S00']],
    ['CTRL','controller','control',520,72,400,112,'Main Agent / Runtime Controller','主 Agent / Runtime 控制器','观察物料图，选择前沿节点，编译任务包，调度 subagent 或程序，收集候选产物，执行验证和提交。',['Owner 决策','物料图状态','验证报告','回流任务'],['TaskPacket','MaterialBundle','调度命令','提交或回滚决策'],['只有主 Agent 可以宣布图节点完成'],['任意 stale 节点']],
    ['GRAPH','graph','control',980,72,360,112,'Versioned Material Graph / Ledger','版本化物料图 / Ledger','保存节点、边、版本、依赖、验证器、来源锚点、stale 传播和 sidecar 状态。',['候选产物','验证结果','依赖变化','回流标记'],['可执行前沿','物料版本','stale 集合','可视化数据'],['schema 校验','依赖完整性校验','版本一致性校验'],['CTRL']],
    ['VALIDATORS','validator','control',1400,72,330,112,'Validator Registry','验证器注册表','集中管理 schema、证据、引用、stage-local overlay、审稿体验、渲染、导出和仓库卫生检查。',['候选物料','目标节点契约','期刊模板','证据锚点'],['通过/失败','错误定位','严重度','回流建议'],['主 Agent 选择并解释验证器'],['S14']],
    ['G01','sidecar','governance',1785,72,300,112,'Runtime governance sidecar','G01 Runtime 治理 sidecar','保存权限、技能、路线元数据、路线记录和状态控制，不直接进入正文认知链。',['state','permissions','route metadata'],['skill registry','route/governance records','state controls','authority limits'],['是否越权','是否污染写作物料'],['CTRL']],
    ['BUS','bus','control',520,212,1210,70,'TaskPacket + Structured MaterialBundle Bus','任务包 + 结构化物料包总线','把大上下文变成结构化包，而不是压缩成摘要。每个环节只负责一个有边界的产物。',['任务目标','强制控制项','Nature stage-local overlay clause','证据和来源锚点','局部上下文','可选背景','禁用路线','验证器','返回格式'],['可派发任务包','subagent 输入包','程序转换输入'],['字段完整性','上下文边界','禁止路线存在性'],['CTRL']],

    ['S00','stage','root',210,360,300,126,'Owner semantic contract','S00 人类需求与语义契约','把人的真实写作目的转成论文 runtime 可执行的约束，确定什么能自动推进，什么必须回到人类。',['human need','paper profile','evidence summary'],['profile','motivation','core decisions','blocked routes'],['目标具体','禁用路线显式','证据足以进入后续阶段'],['OWNER']],
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
    ['G02','sidecar','derivative',1410,1378,330,126,'Derivative/post-paper sidecar','G02 论文后派生 sidecar','稳定论文之后再派生 PPT、专利边界或期刊 profile 包等，不干扰当前论文完成。',['stable paper','owner request'],['presentation plan','patent boundary','profile-specific derivative package'],['是否晚于论文稳定点','是否不回写污染正文'],['S16']],
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
      ['r-01','S00','S01','profile / blocked routes','material'], ['r-02','S01','S02','source map','material'], ['r-03','S02','S03','research dossier','material'], ['r-04','S03','S04','贡献候选进入证据门','material'], ['r-05','S04','S05','可写 claim','material'], ['r-06','S05','S06','reader spine','material'], ['r-07','S06','S07','对象与颗粒度','material'], ['r-08','S07','S09A','表层控制进入控制选择','material'], ['r-09','S09A','S09B','选定控制物料','material'], ['r-10','S09B','S10','正文任务包','material'], ['r-11','S10','S12','候选文本','material'], ['r-12','S12','S13','集成候选稿','material'], ['r-clean','S13','S16','review closure / clean export','material'], ['r-15','S16','FINAL','最终论文包','material'],
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
            "label": "Overclaim backflow task v1",
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
            "label": "Finding: intro overclaim v1",
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
            "label": "DeliveryGate v1",
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
        "title": "Deterministic Overclaim Repair Vertical Slice"
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
            "label": "Overclaim ReviewClosure v1",
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
            "summary": "Superseded claim boundary version preserved for provenance.",
            "version": "v1"
        }
    ]
};

  const stageCoverage = {
    "active_stage_overlays": [
        "nature_expert_writing"
    ],
    "canonical_stage_count": 20,
    "completion_boundary": "all canonical stages have PilotStageRun coverage; this is not a final manuscript/submission claim",
    "coverage_kind_counts": {
        "fixture_generated": 4,
        "owner_gated_deferred": 1,
        "script_checked": 5,
        "source_projected": 10
    },
    "exercise_level_counts": {
        "deferred_with_gate": 1,
        "full_stage_exercised": 19
    },
    "graph_ref": "graph.json",
    "pilot_root": "examples/local-paper/sample-paper-workspace",
    "pilot_stage_run_count": 20,
    "project_slug": "sample-paper-workspace",
    "schema_version": "ppg-local-paper-full-pilot/v0.1",
    "stage_overlay_binding_counts": {
        "nature_bound": 20
    },
    "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
    "stage_runs": [
        {
            "contract_ref": "examples/stage-contracts/S00.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S00.pilot-stage-run.json",
            "stage_id": "S00",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "light",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S00",
                    "validator_ref": "stage_overlay:nature_expert_writing:S00"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "light",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S01",
                    "validator_ref": "stage_overlay:nature_expert_writing:S01"
                }
            ],
            "stage_name": "Source citation evidence inventory",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/S02.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S02.pilot-stage-run.json",
            "stage_id": "S02",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S02",
                    "validator_ref": "stage_overlay:nature_expert_writing:S02"
                }
            ],
            "stage_name": "Research scene exemplar SOTA analysis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S03.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S03.pilot-stage-run.json",
            "stage_id": "S03",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "support",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S03",
                    "validator_ref": "stage_overlay:nature_expert_writing:S03"
                }
            ],
            "stage_name": "Novelty and contribution option analysis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S04.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S04.pilot-stage-run.json",
            "stage_id": "S04",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S04",
                    "validator_ref": "stage_overlay:nature_expert_writing:S04"
                }
            ],
            "stage_name": "Evidence-to-claim admissibility",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S05.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S05.pilot-stage-run.json",
            "stage_id": "S05",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S05",
                    "validator_ref": "stage_overlay:nature_expert_writing:S05"
                }
            ],
            "stage_name": "Paper spine and reader-question synthesis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S06.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S06.pilot-stage-run.json",
            "stage_id": "S06",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S06",
                    "validator_ref": "stage_overlay:nature_expert_writing:S06"
                }
            ],
            "stage_name": "Object representation and granularity design",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S07.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S07.pilot-stage-run.json",
            "stage_id": "S07",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S07",
                    "validator_ref": "stage_overlay:nature_expert_writing:S07"
                }
            ],
            "stage_name": "Rhetoric terminology and surface-control synthesis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S08.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S08.pilot-stage-run.json",
            "stage_id": "S08",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S08",
                    "validator_ref": "stage_overlay:nature_expert_writing:S08"
                }
            ],
            "stage_name": "Visual and formal object planning",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S09A.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S09A.pilot-stage-run.json",
            "stage_id": "S09A",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S09A",
                    "validator_ref": "stage_overlay:nature_expert_writing:S09A"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S09B",
                    "validator_ref": "stage_overlay:nature_expert_writing:S09B"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S10",
                    "validator_ref": "stage_overlay:nature_expert_writing:S10"
                }
            ],
            "stage_name": "Main-text production",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S11.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S11.pilot-stage-run.json",
            "stage_id": "S11",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S11",
                    "validator_ref": "stage_overlay:nature_expert_writing:S11"
                }
            ],
            "stage_name": "Figure caption formal artifact production",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S12.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S12.pilot-stage-run.json",
            "stage_id": "S12",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S12",
                    "validator_ref": "stage_overlay:nature_expert_writing:S12"
                }
            ],
            "stage_name": "Integration and consistency pass",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S13.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S13.pilot-stage-run.json",
            "stage_id": "S13",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S13",
                    "validator_ref": "stage_overlay:nature_expert_writing:S13"
                }
            ],
            "stage_name": "Adversarial manuscript review",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S14.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S14.pilot-stage-run.json",
            "stage_id": "S14",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S14",
                    "validator_ref": "stage_overlay:nature_expert_writing:S14"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S15",
                    "validator_ref": "stage_overlay:nature_expert_writing:S15"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S16",
                    "validator_ref": "stage_overlay:nature_expert_writing:S16"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "governance",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "G01",
                    "validator_ref": "stage_overlay:nature_expert_writing:G01"
                }
            ],
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
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "derivative",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "G02",
                    "validator_ref": "stage_overlay:nature_expert_writing:G02"
                }
            ],
            "stage_name": "Derivative and post-paper outputs",
            "status": "owner_gated",
            "worker_packet_status": "not_required"
        }
    ],
    "worker_task_packet_status_counts": {
        "linked_strict_packet": 12,
        "not_required": 8
    }
};

  const stageRunDetails = {
    "G01": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_1",
                "ref": "state"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_2",
                "ref": "permissions"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_3",
                "ref": "skill registry"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_runtime-stage-registry-json",
                "ref": "runtime/stage_registry.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_examples-stage-contracts",
                "ref": "examples/stage-contracts"
            }
        ],
        "contract": {
            "activation_policy": "activate before automation/permissions/state changes",
            "backflow_targets": [
                "S00",
                "S16"
            ],
            "completion_gate": "governance constraints are recorded and cannot inject route metadata into paper-facing cognition",
            "consumes": [
                "state",
                "permissions",
                "skill registry"
            ],
            "produces": [
                "route governance records",
                "state controls",
                "manager boot checklist"
            ],
            "purpose": "Define permissions, route governance, and state controls before automation.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "runtime governance registry or validator semantics change",
                    "full-flow QA mode",
                    "owner requests governance audit"
                ],
                "policy": "single_with_deterministic_validation",
                "producer_agent_type": "verifier",
                "rationale": "Governance records are registry/validator-controlled and should default to deterministic validation rather than extra agents.",
                "verifier_agent_type": null
            },
            "validators": [
                "permission boundary",
                "route registry",
                "state integrity"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/G01.stage-contract.json",
        "coverage_kind": "script_checked",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_1",
                "ref": "state"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_2",
                "ref": "permissions"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_3",
                "ref": "skill registry"
            }
        ],
        "execution_mode": "script_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [],
        "produced_artifacts": [
            {
                "artifact_id": "g01_pilot_output",
                "artifact_path": "artifacts/G01-runtime-governance-registry.json",
                "artifact_type": "script_check_output",
                "description": "route governance records; state controls; manager boot checklist",
                "payload": {
                    "artifact_kind": "script_check_output",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 5,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "route governance records",
                        "state controls",
                        "manager boot checklist"
                    ],
                    "purpose": "Define permissions, route governance, and state controls before automation.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "governance",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "G01",
                            "validator_ref": "stage_overlay:nature_expert_writing:G01"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "verifier",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_runtime-stage-registry-json",
                "ref": "runtime/stage_registry.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_examples-stage-contracts",
                "ref": "examples/stage-contracts"
            }
        ],
        "stage_id": "G01",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "governance",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "G01",
                "validator_ref": "stage_overlay:nature_expert_writing:G01"
            }
        ],
        "stage_name": "Runtime governance registry",
        "status": "validated",
        "upstream_inputs": [],
        "validator_evidence": [
            {
                "evidence": "G01 links to examples/stage-contracts/G01.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "G01 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "G02": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_1",
                "ref": "stable paper"
            },
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_2",
                "ref": "owner request"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g02_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s16_pilot_output",
                "producer_stage_id": "S16",
                "ref": "artifacts/S16-export-repository-hygiene-and-handoff.json"
            }
        ],
        "contract": {
            "activation_policy": "activate only after paper content stability or explicit derivative request",
            "backflow_targets": [
                "owner",
                "S16"
            ],
            "completion_gate": "only explicit owner request can activate derivative output; otherwise recorded not-applicable/deferred",
            "consumes": [
                "stable paper",
                "owner request"
            ],
            "produces": [
                "presentation plan",
                "patent boundary",
                "profile-specific derivative package"
            ],
            "purpose": "Manage presentation, patent, profile-specific derivative packages, or other post-paper outputs after paper stability or explicit owner request.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "post-paper derivative output is owner-facing",
                    "external-use boundary changes",
                    "owner requests derivative audit"
                ],
                "policy": "single_with_deterministic_validation",
                "producer_agent_type": "planner",
                "rationale": "Derivative outputs are outside the main paper cognition path and should stay single-lane until an owner-facing derivative is active.",
                "verifier_agent_type": null
            },
            "validators": [
                "owner authorization",
                "derivative boundary",
                "no premature submission claim"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/G02.stage-contract.json",
        "coverage_kind": "owner_gated_deferred",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_1",
                "ref": "stable paper"
            },
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_2",
                "ref": "owner request"
            }
        ],
        "execution_mode": "owner_gated",
        "exercise_level": "deferred_with_gate",
        "handoff_consumers": [],
        "produced_artifacts": [
            {
                "artifact_id": "g02_pilot_output",
                "artifact_path": "artifacts/G02-derivative-and-post-paper-outputs.json",
                "artifact_type": "owner_gate_projection",
                "description": "presentation plan; patent boundary; profile-specific derivative package",
                "payload": {
                    "artifact_kind": "owner_gate_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 4,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "presentation plan",
                        "patent boundary",
                        "profile-specific derivative package"
                    ],
                    "purpose": "Manage presentation, patent, profile-specific derivative packages, or other post-paper outputs after paper stability or explicit owner request.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "derivative",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "G02",
                            "validator_ref": "stage_overlay:nature_expert_writing:G02"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "planner",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g02_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            }
        ],
        "stage_id": "G02",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "derivative",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "G02",
                "validator_ref": "stage_overlay:nature_expert_writing:G02"
            }
        ],
        "stage_name": "Derivative and post-paper outputs",
        "status": "owner_gated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s16_pilot_output",
                "producer_stage_id": "S16",
                "ref": "artifacts/S16-export-repository-hygiene-and-handoff.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "G02 links to examples/stage-contracts/G02.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=owner_gated_deferred; exercise_level=deferred_with_gate; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "G02 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "S00": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_1",
                "ref": "human need"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_2",
                "ref": "paper profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_3",
                "ref": "evidence summary"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            }
        ],
        "contract": {
            "activation_policy": "activate when owner motivation, venue, claim scope, or private-source policy is unclear",
            "backflow_targets": [
                "owner"
            ],
            "completion_gate": "confirmed owner decision or recorded owner-gated assumption; no worker may silently change this stage",
            "consumes": [
                "human need",
                "paper profile",
                "evidence summary"
            ],
            "produces": [
                "paper-profile",
                "motivation",
                "decisions",
                "blocked routes"
            ],
            "purpose": "Convert human need into bounded paper commitments and owner decisions.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "owner semantic contract changes",
                    "venue or claim-scope freeze",
                    "owner requests independent challenge"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "main",
                "rationale": "Owner semantics are controller-owned; a second lane is needed only when commitments change or freeze.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "owner confirmation",
                "blocked route check"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/S00.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_1",
                "ref": "human need"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_2",
                "ref": "paper profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_3",
                "ref": "evidence summary"
            }
        ],
        "execution_mode": "owner_gated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s00_pilot_output",
                "ref": "artifacts/S00-owner-semantic-contract.json",
                "stage_id": "S01",
                "stage_name": "Source citation evidence inventory"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s00_pilot_output",
                "artifact_path": "artifacts/S00-owner-semantic-contract.json",
                "artifact_type": "owner_gate_projection",
                "description": "paper-profile; motivation; decisions; blocked routes",
                "payload": {
                    "artifact_kind": "owner_gate_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 6,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "paper-profile",
                        "motivation",
                        "decisions",
                        "blocked routes"
                    ],
                    "purpose": "Convert human need into bounded paper commitments and owner decisions.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "light",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S00",
                            "validator_ref": "stage_overlay:nature_expert_writing:S00"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "main",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            }
        ],
        "stage_id": "S00",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "light",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S00",
                "validator_ref": "stage_overlay:nature_expert_writing:S00"
            }
        ],
        "stage_name": "Owner semantic contract",
        "status": "validated",
        "upstream_inputs": [],
        "validator_evidence": [
            {
                "evidence": "S00 links to examples/stage-contracts/S00.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S00 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "S01": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_1",
                "ref": "initial files"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_2",
                "ref": "result dirs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_3",
                "ref": "BibTeX"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_4",
                "ref": "source locators"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-latest-sync-brief-md",
                "ref": "docs/LATEST_SYNC_BRIEF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s00_pilot_output",
                "producer_stage_id": "S00",
                "ref": "artifacts/S00-owner-semantic-contract.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when source or evidence inventory is missing/stale",
            "backflow_targets": [
                "S00",
                "S04"
            ],
            "completion_gate": "claim-relevant sources are locator-backed or explicitly unresolved",
            "consumes": [
                "initial files",
                "result dirs",
                "BibTeX",
                "source locators"
            ],
            "produces": [
                "source map",
                "citation bank",
                "evidence bank"
            ],
            "purpose": "Make raw paper inputs locatable and support-safe.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "new source family is admitted",
                    "citation/evidence support is uncertain",
                    "pre-writing inventory freeze"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "explore",
                "rationale": "Inventory work is mostly structural but needs independent verification when source support or evidence admissibility is uncertain.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "source locator resolution",
                "privacy boundary check",
                "evidence path check"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/S01.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_1",
                "ref": "initial files"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_2",
                "ref": "result dirs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_3",
                "ref": "BibTeX"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_4",
                "ref": "source locators"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s01_pilot_output",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json",
                "stage_id": "S02",
                "stage_name": "Research scene exemplar SOTA analysis"
            },
            {
                "material_id": "s01_pilot_output",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json",
                "stage_id": "S04",
                "stage_name": "Evidence-to-claim admissibility"
            },
            {
                "material_id": "s01_pilot_output",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json",
                "stage_id": "S11",
                "stage_name": "Figure caption formal artifact production"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s01_pilot_output",
                "artifact_path": "artifacts/S01-source-citation-evidence-inventory.json",
                "artifact_type": "analysis_material_projection",
                "description": "source map; citation bank; evidence bank",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 10,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "source map",
                        "citation bank",
                        "evidence bank"
                    ],
                    "purpose": "Make raw paper inputs locatable and support-safe.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "light",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S01",
                            "validator_ref": "stage_overlay:nature_expert_writing:S01"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "explore",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-latest-sync-brief-md",
                "ref": "docs/LATEST_SYNC_BRIEF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            }
        ],
        "stage_id": "S01",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "light",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S01",
                "validator_ref": "stage_overlay:nature_expert_writing:S01"
            }
        ],
        "stage_name": "Source citation evidence inventory",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s00_pilot_output",
                "producer_stage_id": "S00",
                "ref": "artifacts/S00-owner-semantic-contract.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S01 links to examples/stage-contracts/S01.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S01 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "S02": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_1",
                "ref": "source map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_3",
                "ref": "venue route"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_4",
                "ref": "exemplar locators"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-readme-md",
                "ref": "references/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-citation-workspace-map-md",
                "ref": "references/citation-workspace-map.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when field/template/SOTA is uncertain",
            "backflow_targets": [
                "S01",
                "S00"
            ],
            "completion_gate": "research dossier and template/profile outputs are source-located and safe to consume",
            "consumes": [
                "source map",
                "citation bank",
                "venue route",
                "exemplar locators"
            ],
            "produces": [
                "research dossier",
                "reader package",
                "template profile",
                "citation verification report"
            ],
            "purpose": "Understand field scene, template expectations, exemplar structure, and related-work positioning.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "researcher",
                "rationale": "Research/SOTA materials shape all downstream claims, so producer output must be independently checked before commit.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "source locator check",
                "citation verification",
                "template copying boundary"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s02_sota_analysis_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S02.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_1",
                "ref": "source map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_3",
                "ref": "venue route"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_4",
                "ref": "exemplar locators"
            }
        ],
        "execution_mode": "agent_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s02_pilot_output",
                "ref": "artifacts/S02-research-scene-exemplar-sota-analysis.json",
                "stage_id": "S03",
                "stage_name": "Novelty and contribution option analysis"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s02_pilot_output",
                "artifact_path": "artifacts/S02-research-scene-exemplar-sota-analysis.json",
                "artifact_type": "analysis_material_projection",
                "description": "research dossier; reader package; template profile; citation verification report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 8,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "research dossier",
                        "reader package",
                        "template profile",
                        "citation verification report"
                    ],
                    "purpose": "Understand field scene, template expectations, exemplar structure, and related-work positioning.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S02",
                            "validator_ref": "stage_overlay:nature_expert_writing:S02"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "researcher",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-readme-md",
                "ref": "references/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-citation-workspace-map-md",
                "ref": "references/citation-workspace-map.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            }
        ],
        "stage_id": "S02",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S02",
                "validator_ref": "stage_overlay:nature_expert_writing:S02"
            }
        ],
        "stage_name": "Research scene exemplar SOTA analysis",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S02 links to examples/stage-contracts/S02.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S02 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s02_sota_analysis_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S03": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_1",
                "ref": "research dossier"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_2",
                "ref": "evidence inventory"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_3",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_4",
                "ref": "SOTA map"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s02_pilot_output",
                "producer_stage_id": "S02",
                "ref": "artifacts/S02-research-scene-exemplar-sota-analysis.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when contribution is unstable or weak",
            "backflow_targets": [
                "S00",
                "S02",
                "S04"
            ],
            "completion_gate": "viable options are classified as supported, owner-gated, or rejected",
            "consumes": [
                "research dossier",
                "evidence inventory",
                "motivation",
                "SOTA map"
            ],
            "produces": [
                "contribution options",
                "novelty readiness",
                "risk list"
            ],
            "purpose": "Identify viable contribution framings without treating speculation as evidence.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "critic",
                "rationale": "Novelty framing is high-risk and speculative by nature; independent challenge prevents unsupported contribution claims.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "evidence readiness score",
                "source anchors",
                "owner semantic-shift gate"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S03.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_1",
                "ref": "research dossier"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_2",
                "ref": "evidence inventory"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_3",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_4",
                "ref": "SOTA map"
            }
        ],
        "execution_mode": "agent_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s03_pilot_output",
                "ref": "artifacts/S03-novelty-and-contribution-option-analysis.json",
                "stage_id": "S04",
                "stage_name": "Evidence-to-claim admissibility"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s03_pilot_output",
                "artifact_path": "artifacts/S03-novelty-and-contribution-option-analysis.json",
                "artifact_type": "analysis_material_projection",
                "description": "contribution options; novelty readiness; risk list",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 9,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "contribution options",
                        "novelty readiness",
                        "risk list"
                    ],
                    "purpose": "Identify viable contribution framings without treating speculation as evidence.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "support",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S03",
                            "validator_ref": "stage_overlay:nature_expert_writing:S03"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "critic",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            }
        ],
        "stage_id": "S03",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "support",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S03",
                "validator_ref": "stage_overlay:nature_expert_writing:S03"
            }
        ],
        "stage_name": "Novelty and contribution option analysis",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s02_pilot_output",
                "producer_stage_id": "S02",
                "ref": "artifacts/S02-research-scene-exemplar-sota-analysis.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S03 links to examples/stage-contracts/S03.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S03 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S04": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_1",
                "ref": "evidence bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_3",
                "ref": "result artifacts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_4",
                "ref": "contribution options"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_claims-readme-md",
                "ref": "claims/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625/manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s03_pilot_output",
                "producer_stage_id": "S03",
                "ref": "artifacts/S03-novelty-and-contribution-option-analysis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "contract": {
            "activation_policy": "activate before claim-bearing writing or review",
            "backflow_targets": [
                "S01",
                "S03",
                "S00"
            ],
            "completion_gate": "every claim-bearing unit has support strength, evidence anchor, allowed wording, and forbidden wording",
            "consumes": [
                "evidence bank",
                "citation bank",
                "result artifacts",
                "contribution options"
            ],
            "produces": [
                "claim citation capsules",
                "result packages",
                "claim evidence visibility",
                "data availability plan"
            ],
            "purpose": "Bind evidence and citations to exact claim boundaries.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "verifier",
                "rationale": "Claim-evidence admissibility is a safety-critical gate; production and verification must remain separate.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "claim support",
                "allowed wording",
                "forbidden wording",
                "result package boundary"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S04.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_1",
                "ref": "evidence bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_3",
                "ref": "result artifacts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_4",
                "ref": "contribution options"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json",
                "stage_id": "S05",
                "stage_name": "Paper spine and reader-question synthesis"
            },
            {
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json",
                "stage_id": "S08",
                "stage_name": "Visual and formal object planning"
            },
            {
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json",
                "stage_id": "S09A",
                "stage_name": "Control-material selection"
            },
            {
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json",
                "stage_id": "S11",
                "stage_name": "Figure caption formal artifact production"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s04_pilot_output",
                "artifact_path": "artifacts/S04-evidence-to-claim-admissibility.json",
                "artifact_type": "analysis_material_projection",
                "description": "claim citation capsules; result packages; claim evidence visibility; data availability plan",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 11,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "claim citation capsules",
                        "result packages",
                        "claim evidence visibility",
                        "data availability plan"
                    ],
                    "purpose": "Bind evidence and citations to exact claim boundaries.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S04",
                            "validator_ref": "stage_overlay:nature_expert_writing:S04"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "verifier",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_claims-readme-md",
                "ref": "claims/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625/manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            }
        ],
        "stage_id": "S04",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S04",
                "validator_ref": "stage_overlay:nature_expert_writing:S04"
            }
        ],
        "stage_name": "Evidence-to-claim admissibility",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s03_pilot_output",
                "producer_stage_id": "S03",
                "ref": "artifacts/S03-novelty-and-contribution-option-analysis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S04 links to examples/stage-contracts/S04.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S04 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S05": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_1",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_2",
                "ref": "contribution options"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_4",
                "ref": "claim materials"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            }
        ],
        "contract": {
            "activation_policy": "activate for new section or major rewrite",
            "backflow_targets": [
                "S00",
                "S03",
                "S04"
            ],
            "completion_gate": "spine is coherent and claim-bounded before writing begins",
            "consumes": [
                "motivation",
                "contribution options",
                "template profile",
                "claim materials"
            ],
            "produces": [
                "reader spine",
                "reviewer question map",
                "rationale matrix"
            ],
            "purpose": "Synthesize paper argument path and reader/reviewer questions.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "architect",
                "rationale": "The paper spine controls global argument order; independent challenge catches incoherent or unsupported reader paths.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "claim appears in spine",
                "section answers reader question",
                "owner decisions explicit"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S05.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_1",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_2",
                "ref": "contribution options"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_4",
                "ref": "claim materials"
            }
        ],
        "execution_mode": "agent_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s05_pilot_output",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json",
                "stage_id": "S06",
                "stage_name": "Object representation and granularity design"
            },
            {
                "material_id": "s05_pilot_output",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json",
                "stage_id": "S08",
                "stage_name": "Visual and formal object planning"
            },
            {
                "material_id": "s05_pilot_output",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json",
                "stage_id": "S09A",
                "stage_name": "Control-material selection"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s05_pilot_output",
                "artifact_path": "artifacts/S05-paper-spine-and-reader-question-synthesis.json",
                "artifact_type": "analysis_material_projection",
                "description": "reader spine; reviewer question map; rationale matrix",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 8,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "reader spine",
                        "reviewer question map",
                        "rationale matrix"
                    ],
                    "purpose": "Synthesize paper argument path and reader/reviewer questions.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S05",
                            "validator_ref": "stage_overlay:nature_expert_writing:S05"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "architect",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            }
        ],
        "stage_id": "S05",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S05",
                "validator_ref": "stage_overlay:nature_expert_writing:S05"
            }
        ],
        "stage_name": "Paper spine and reader-question synthesis",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S05 links to examples/stage-contracts/S05.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S05 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S06": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_2",
                "ref": "reviewer question map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_4",
                "ref": "claim visibility"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            }
        ],
        "contract": {
            "activation_policy": "activate for full paper route or when object repetition risk exists",
            "backflow_targets": [
                "S05",
                "S04"
            ],
            "completion_gate": "writing units can consume explicit object and granularity instructions",
            "consumes": [
                "reader spine",
                "reviewer question map",
                "template profile",
                "claim visibility"
            ],
            "produces": [
                "object representation matrix",
                "section function budget",
                "load budget",
                "explanation ladder"
            ],
            "purpose": "Decide how paper objects appear across sections and at what granularity.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "new object family or granularity ladder is introduced",
                    "multi-section object reuse is planned",
                    "pre-writing design freeze"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "architect",
                "rationale": "Object/granularity design is reusable control material; single production is enough unless it changes multi-section semantics.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "granularity progression",
                "no flat repetition",
                "load budget present"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S06.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_2",
                "ref": "reviewer question map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_4",
                "ref": "claim visibility"
            }
        ],
        "execution_mode": "agent_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s06_pilot_output",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json",
                "stage_id": "S07",
                "stage_name": "Rhetoric terminology and surface-control synthesis"
            },
            {
                "material_id": "s06_pilot_output",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json",
                "stage_id": "S08",
                "stage_name": "Visual and formal object planning"
            },
            {
                "material_id": "s06_pilot_output",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json",
                "stage_id": "S09A",
                "stage_name": "Control-material selection"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s06_pilot_output",
                "artifact_path": "artifacts/S06-object-representation-and-granularity-design.json",
                "artifact_type": "analysis_material_projection",
                "description": "object representation matrix; section function budget; load budget; explanation ladder",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 8,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "object representation matrix",
                        "section function budget",
                        "load budget",
                        "explanation ladder"
                    ],
                    "purpose": "Decide how paper objects appear across sections and at what granularity.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S06",
                            "validator_ref": "stage_overlay:nature_expert_writing:S06"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "architect",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "stage_id": "S06",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S06",
                "validator_ref": "stage_overlay:nature_expert_writing:S06"
            }
        ],
        "stage_name": "Object representation and granularity design",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S06 links to examples/stage-contracts/S06.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S06 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S07": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_1",
                "ref": "object representation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_2",
                "ref": "claim visibility"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_3",
                "ref": "evidence wording"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-07-conclusion-tex",
                "ref": "manuscript/sections/07_conclusion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "contract": {
            "activation_policy": "activate before writing execution",
            "backflow_targets": [
                "S06",
                "S04",
                "S05"
            ],
            "completion_gate": "main text can be generated without unsupported claims, raw internal ids, or lab-notebook smell",
            "consumes": [
                "object representation",
                "claim visibility",
                "evidence wording"
            ],
            "produces": [
                "construction matrix",
                "rhetorical matrix",
                "terminology register",
                "surface rules"
            ],
            "purpose": "Turn reader/object design into paragraph-level rhetorical and terminology controls.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "terminology affects claim strength",
                    "surface rules govern multiple writing units",
                    "pre-writing expression freeze"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "writer",
                "rationale": "Surface and terminology controls are broad but usually locally checkable; escalate when they constrain claims across sections.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "terminology coverage",
                "forbidden internal ids",
                "rhetorical move coverage"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S07.stage-contract.json",
        "coverage_kind": "fixture_generated",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_1",
                "ref": "object representation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_2",
                "ref": "claim visibility"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_3",
                "ref": "evidence wording"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s07_pilot_output",
                "ref": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json",
                "stage_id": "S09A",
                "stage_name": "Control-material selection"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s07_pilot_output",
                "artifact_path": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json",
                "artifact_type": "analysis_material_projection",
                "description": "construction matrix; rhetorical matrix; terminology register; surface rules",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 8,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "construction matrix",
                        "rhetorical matrix",
                        "terminology register",
                        "surface rules"
                    ],
                    "purpose": "Turn reader/object design into paragraph-level rhetorical and terminology controls.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S07",
                            "validator_ref": "stage_overlay:nature_expert_writing:S07"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "writer",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-07-conclusion-tex",
                "ref": "manuscript/sections/07_conclusion.tex"
            }
        ],
        "stage_id": "S07",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S07",
                "validator_ref": "stage_overlay:nature_expert_writing:S07"
            }
        ],
        "stage_name": "Rhetoric terminology and surface-control synthesis",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S07 links to examples/stage-contracts/S07.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S07 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S08": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_2",
                "ref": "section function budget"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_3",
                "ref": "claim evidence materials"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when figure/table/algorithm/formula is touched",
            "backflow_targets": [
                "S05",
                "S04",
                "S06"
            ],
            "completion_gate": "no final/export-facing figure proceeds without contract, evidence, and backend route",
            "consumes": [
                "reader spine",
                "section function budget",
                "claim evidence materials"
            ],
            "produces": [
                "visual budget",
                "figure contract",
                "panel evidence map",
                "backend route"
            ],
            "purpose": "Decide which figures, tables, algorithms, and formulas exist and what they prove.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "figure/table/formula object will be paper-facing",
                    "visual claim support is uncertain",
                    "pre-export visual-plan freeze"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "designer",
                "rationale": "Visual/formal planning is often design-led and evidence-linked; escalate before paper-facing visual commitments freeze.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "reader question",
                "supported claim",
                "evidence refs",
                "backend route"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S08.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_2",
                "ref": "section function budget"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_3",
                "ref": "claim evidence materials"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s08_pilot_output",
                "ref": "artifacts/S08-visual-and-formal-object-planning.json",
                "stage_id": "S11",
                "stage_name": "Figure caption formal artifact production"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s08_pilot_output",
                "artifact_path": "artifacts/S08-visual-and-formal-object-planning.json",
                "artifact_type": "analysis_material_projection",
                "description": "visual budget; figure contract; panel evidence map; backend route",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 10,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "visual budget",
                        "figure contract",
                        "panel evidence map",
                        "backend route"
                    ],
                    "purpose": "Decide which figures, tables, algorithms, and formulas exist and what they prove.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S08",
                            "validator_ref": "stage_overlay:nature_expert_writing:S08"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "designer",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "stage_id": "S08",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S08",
                "validator_ref": "stage_overlay:nature_expert_writing:S08"
            }
        ],
        "stage_name": "Visual and formal object planning",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S08 links to examples/stage-contracts/S08.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S08 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S09A": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_1",
                "ref": "claim controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_2",
                "ref": "spine controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_3",
                "ref": "granularity controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_4",
                "ref": "surface rules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_5",
                "ref": "target unit"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/owner_contract.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/source_inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s07_pilot_output",
                "producer_stage_id": "S07",
                "ref": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "contract": {
            "activation_policy": "activate before per-unit packet assembly",
            "backflow_targets": [
                "S04",
                "S05",
                "S06",
                "S07"
            ],
            "completion_gate": "S09B can build a task packet without guessing upstream controls",
            "consumes": [
                "claim controls",
                "spine controls",
                "granularity controls",
                "surface rules",
                "target unit"
            ],
            "produces": [
                "selected control bundle",
                "control priority map",
                "missing control report"
            ],
            "purpose": "Choose the minimal control material set needed by the target manuscript unit.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "owner requests audit of control selection",
                    "full-flow QA mode",
                    "control selection changes high-risk claim inputs"
                ],
                "policy": "single_with_deterministic_validation",
                "producer_agent_type": "planner",
                "rationale": "Control-material selection is a controller/script-like routing step and is primarily proven by deterministic validation.",
                "verifier_agent_type": null
            },
            "validators": [
                "required controls present",
                "no overloaded all-context packet",
                "conflict priority resolved"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/S09A.stage-contract.json",
        "coverage_kind": "script_checked",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_1",
                "ref": "claim controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_2",
                "ref": "spine controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_3",
                "ref": "granularity controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_4",
                "ref": "surface rules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_5",
                "ref": "target unit"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s09a_pilot_output",
                "ref": "artifacts/S09A-control-material-selection.json",
                "stage_id": "S09B",
                "stage_name": "Per-unit task packet assembly"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s09a_pilot_output",
                "artifact_path": "artifacts/S09A-control-material-selection.json",
                "artifact_type": "analysis_material_projection",
                "description": "selected control bundle; control priority map; missing control report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 12,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "selected control bundle",
                        "control priority map",
                        "missing control report"
                    ],
                    "purpose": "Choose the minimal control material set needed by the target manuscript unit.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S09A",
                            "validator_ref": "stage_overlay:nature_expert_writing:S09A"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "planner",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/owner_contract.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/source_inventory.json"
            }
        ],
        "stage_id": "S09A",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S09A",
                "validator_ref": "stage_overlay:nature_expert_writing:S09A"
            }
        ],
        "stage_name": "Control-material selection",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s07_pilot_output",
                "producer_stage_id": "S07",
                "ref": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S09A links to examples/stage-contracts/S09A.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S09A has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "S09B": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_1",
                "ref": "selected control bundle"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_2",
                "ref": "evidence anchors"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_3",
                "ref": "target unit"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_4",
                "ref": "validator refs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_5",
                "ref": "return format"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-intro-writing-packet-v2-yaml",
                "ref": "examples/packets/intro_writing_packet.v2.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s09a_pilot_output",
                "producer_stage_id": "S09A",
                "ref": "artifacts/S09A-control-material-selection.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when a worker needs a section/unit packet",
            "backflow_targets": [
                "S09A",
                "S14",
                "S15"
            ],
            "completion_gate": "packet is bounded and cannot grant graph-completion or recursive-dispatch authority",
            "consumes": [
                "selected control bundle",
                "evidence anchors",
                "target unit",
                "validator refs",
                "return format"
            ],
            "produces": [
                "task packet",
                "section move plan",
                "single-writer lock",
                "missing material report"
            ],
            "purpose": "Compile one bounded writing TaskPacket for a section/unit.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "packet compiler or authority-boundary code changes",
                    "full-flow QA mode",
                    "owner requests task-packet audit"
                ],
                "policy": "single_with_deterministic_validation",
                "producer_agent_type": "main",
                "rationale": "Task-packet assembly is an authority-boundary compiler step and is primarily proven by deterministic validation.",
                "verifier_agent_type": null
            },
            "validators": [
                "allowed read/write paths",
                "worker boot clause",
                "completion forbidden",
                "no recursive orchestration"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/S09B.stage-contract.json",
        "coverage_kind": "script_checked",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_1",
                "ref": "selected control bundle"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_2",
                "ref": "evidence anchors"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_3",
                "ref": "target unit"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_4",
                "ref": "validator refs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_5",
                "ref": "return format"
            }
        ],
        "execution_mode": "script_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s09b_pilot_output",
                "ref": "artifacts/S09B-per-unit-task-packet-assembly.json",
                "stage_id": "S10",
                "stage_name": "Main-text production"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s09b_pilot_output",
                "artifact_path": "artifacts/S09B-per-unit-task-packet-assembly.json",
                "artifact_type": "script_check_output",
                "description": "task packet; section move plan; single-writer lock; missing material report",
                "payload": {
                    "artifact_kind": "script_check_output",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 9,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "task packet",
                        "section move plan",
                        "single-writer lock",
                        "missing material report"
                    ],
                    "purpose": "Compile one bounded writing TaskPacket for a section/unit.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S09B",
                            "validator_ref": "stage_overlay:nature_expert_writing:S09B"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "main",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-intro-writing-packet-v2-yaml",
                "ref": "examples/packets/intro_writing_packet.v2.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            }
        ],
        "stage_id": "S09B",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S09B",
                "validator_ref": "stage_overlay:nature_expert_writing:S09B"
            }
        ],
        "stage_name": "Per-unit task packet assembly",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s09a_pilot_output",
                "producer_stage_id": "S09A",
                "ref": "artifacts/S09A-control-material-selection.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S09B links to examples/stage-contracts/S09B.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S09B has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "S10": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_1",
                "ref": "S09B task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_2",
                "ref": "construction matrix"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_3",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_4",
                "ref": "claim visibility"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s09b_pilot_output",
                "producer_stage_id": "S09B",
                "ref": "artifacts/S09B-per-unit-task-packet-assembly.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when writing execution is needed",
            "backflow_targets": [
                "S09B",
                "S07",
                "S04"
            ],
            "completion_gate": "candidate text is validated and collected; graph completion remains controller-owned",
            "consumes": [
                "S09B task packet",
                "construction matrix",
                "terminology register",
                "claim visibility"
            ],
            "produces": [
                "candidate text unit",
                "CandidateArtifactReturn"
            ],
            "purpose": "Produce candidate manuscript modules from task packets.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "writer",
                "rationale": "Main-text production is paper-facing semantic output; independent verification is mandatory before controller acceptance.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "section draft validator",
                "candidate return validator",
                "claim boundary check"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/intro_writing_packet.v2.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S10.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_1",
                "ref": "S09B task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_2",
                "ref": "construction matrix"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_3",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_4",
                "ref": "claim visibility"
            }
        ],
        "execution_mode": "agent_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s10_pilot_output",
                "ref": "artifacts/S10-main-text-production.json",
                "stage_id": "S12",
                "stage_name": "Integration and consistency pass"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s10_pilot_output",
                "artifact_path": "artifacts/S10-main-text-production.json",
                "artifact_type": "candidate_or_repair_projection",
                "description": "candidate text unit; CandidateArtifactReturn",
                "payload": {
                    "artifact_kind": "candidate_or_repair_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 9,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "candidate text unit",
                        "CandidateArtifactReturn"
                    ],
                    "purpose": "Produce candidate manuscript modules from task packets.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S10",
                            "validator_ref": "stage_overlay:nature_expert_writing:S10"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "writer",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "stage_id": "S10",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S10",
                "validator_ref": "stage_overlay:nature_expert_writing:S10"
            }
        ],
        "stage_name": "Main-text production",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s09b_pilot_output",
                "producer_stage_id": "S09B",
                "ref": "artifacts/S09B-per-unit-task-packet-assembly.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S10 links to examples/stage-contracts/S10.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S10 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/intro_writing_packet.v2.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S11": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_1",
                "ref": "figure contracts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_2",
                "ref": "panel evidence packages"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_3",
                "ref": "source data locators"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_4",
                "ref": "caption brief"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s08_pilot_output",
                "producer_stage_id": "S08",
                "ref": "artifacts/S08-visual-and-formal-object-planning.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when figure/caption/formal artifacts are touched",
            "backflow_targets": [
                "S08",
                "S04",
                "S01"
            ],
            "completion_gate": "figure/caption has editable source, rendered output, provenance, QA route, and claim support",
            "consumes": [
                "figure contracts",
                "panel evidence packages",
                "source data locators",
                "caption brief"
            ],
            "produces": [
                "figure statistics",
                "image integrity record",
                "caption brief",
                "figure export bundle"
            ],
            "purpose": "Produce figures, captions, tables, algorithms, formulas, and export bundles.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "artifact is paper-facing or data-backed",
                    "caption makes a claim",
                    "pre-export figure/caption freeze"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "executor",
                "rationale": "Artifact production is often deterministic but paper-facing; independent QA is required when it becomes final/export-facing.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "build/render",
                "source data",
                "image integrity",
                "caption claim boundary"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S11.stage-contract.json",
        "coverage_kind": "source_projected",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_1",
                "ref": "figure contracts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_2",
                "ref": "panel evidence packages"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_3",
                "ref": "source data locators"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_4",
                "ref": "caption brief"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s11_pilot_output",
                "ref": "artifacts/S11-figure-caption-formal-artifact-production.json",
                "stage_id": "S12",
                "stage_name": "Integration and consistency pass"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s11_pilot_output",
                "artifact_path": "artifacts/S11-figure-caption-formal-artifact-production.json",
                "artifact_type": "candidate_or_repair_projection",
                "description": "figure statistics; image integrity record; caption brief; figure export bundle",
                "payload": {
                    "artifact_kind": "candidate_or_repair_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 9,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "figure statistics",
                        "image integrity record",
                        "caption brief",
                        "figure export bundle"
                    ],
                    "purpose": "Produce figures, captions, tables, algorithms, formulas, and export bundles.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S11",
                            "validator_ref": "stage_overlay:nature_expert_writing:S11"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "executor",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            }
        ],
        "stage_id": "S11",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S11",
                "validator_ref": "stage_overlay:nature_expert_writing:S11"
            }
        ],
        "stage_name": "Figure caption formal artifact production",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s08_pilot_output",
                "producer_stage_id": "S08",
                "ref": "artifacts/S08-visual-and-formal-object-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S11 links to examples/stage-contracts/S11.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S11 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S12": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_1",
                "ref": "candidate text modules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_2",
                "ref": "figures/captions"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_3",
                "ref": "section move plan"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_4",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_5",
                "ref": "claim visibility"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s10_pilot_output",
                "producer_stage_id": "S10",
                "ref": "artifacts/S10-main-text-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s11_pilot_output",
                "producer_stage_id": "S11",
                "ref": "artifacts/S11-figure-caption-formal-artifact-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when multiple modules are integrated",
            "backflow_targets": [
                "S10",
                "S11",
                "S07",
                "S04"
            ],
            "completion_gate": "integrated candidate is ready for adversarial review, not final",
            "consumes": [
                "candidate text modules",
                "figures/captions",
                "section move plan",
                "terminology register",
                "claim visibility"
            ],
            "produces": [
                "integrated manuscript candidate",
                "consistency findings",
                "validator report"
            ],
            "purpose": "Assemble modules and check cross-section dependencies.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "verifier",
                "rationale": "Integration can create cross-section contradictions, so independent consistency verification is mandatory.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "promise satisfaction",
                "method/result alignment",
                "terminology consistency",
                "figure-text consistency"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s12_integration_consistency_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S12.stage-contract.json",
        "coverage_kind": "fixture_generated",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_1",
                "ref": "candidate text modules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_2",
                "ref": "figures/captions"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_3",
                "ref": "section move plan"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_4",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_5",
                "ref": "claim visibility"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s12_pilot_output",
                "ref": "artifacts/S12-integration-and-consistency-pass.json",
                "stage_id": "S13",
                "stage_name": "Adversarial manuscript review"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s12_pilot_output",
                "artifact_path": "artifacts/S12-integration-and-consistency-pass.json",
                "artifact_type": "analysis_material_projection",
                "description": "integrated manuscript candidate; consistency findings; validator report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 11,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "integrated manuscript candidate",
                        "consistency findings",
                        "validator report"
                    ],
                    "purpose": "Assemble modules and check cross-section dependencies.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S12",
                            "validator_ref": "stage_overlay:nature_expert_writing:S12"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "verifier",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "stage_id": "S12",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S12",
                "validator_ref": "stage_overlay:nature_expert_writing:S12"
            }
        ],
        "stage_name": "Integration and consistency pass",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s10_pilot_output",
                "producer_stage_id": "S10",
                "ref": "artifacts/S10-main-text-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s11_pilot_output",
                "producer_stage_id": "S11",
                "ref": "artifacts/S11-figure-caption-formal-artifact-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S12 links to examples/stage-contracts/S12.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S12 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s12_integration_consistency_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S13": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_1",
                "ref": "integrated candidate"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_2",
                "ref": "evidence/claim materials"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_3",
                "ref": "reader/terminology/rhetoric materials"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_4",
                "ref": "figure/export artifacts"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s12_pilot_output",
                "producer_stage_id": "S12",
                "ref": "artifacts/S12-integration-and-consistency-pass.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when candidate manuscript/module exists",
            "backflow_targets": [
                "S14"
            ],
            "completion_gate": "accepted findings are actionable and routed to nearest responsible upstream material",
            "consumes": [
                "integrated candidate",
                "evidence/claim materials",
                "reader/terminology/rhetoric materials",
                "figure/export artifacts"
            ],
            "produces": [
                "reviewer panel report",
                "reader experience report",
                "validator report",
                "review findings"
            ],
            "purpose": "Generate actionable review/loss signals, not uncontrolled rewrites.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "critic",
                "rationale": "Adversarial review itself produces loss signals that must be independently validated for actionability and routing.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "finding severity",
                "evidence",
                "affected artifact",
                "backflow target",
                "resolution status"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s13_adversarial_review_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S13.stage-contract.json",
        "coverage_kind": "fixture_generated",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_1",
                "ref": "integrated candidate"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_2",
                "ref": "evidence/claim materials"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_3",
                "ref": "reader/terminology/rhetoric materials"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_4",
                "ref": "figure/export artifacts"
            }
        ],
        "execution_mode": "agent_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s13_pilot_output",
                "ref": "artifacts/S13-adversarial-manuscript-review.json",
                "stage_id": "S14",
                "stage_name": "Backflow compilation and repair planning"
            },
            {
                "material_id": "s13_pilot_output",
                "ref": "artifacts/S13-adversarial-manuscript-review.json",
                "stage_id": "S16",
                "stage_name": "Export repository hygiene and handoff"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s13_pilot_output",
                "artifact_path": "artifacts/S13-adversarial-manuscript-review.json",
                "artifact_type": "review_backflow_projection",
                "description": "reviewer panel report; reader experience report; validator report; review findings",
                "payload": {
                    "artifact_kind": "review_backflow_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 8,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "reviewer panel report",
                        "reader experience report",
                        "validator report",
                        "review findings"
                    ],
                    "purpose": "Generate actionable review/loss signals, not uncontrolled rewrites.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S13",
                            "validator_ref": "stage_overlay:nature_expert_writing:S13"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "critic",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            }
        ],
        "stage_id": "S13",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S13",
                "validator_ref": "stage_overlay:nature_expert_writing:S13"
            }
        ],
        "stage_name": "Adversarial manuscript review",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s12_pilot_output",
                "producer_stage_id": "S12",
                "ref": "artifacts/S12-integration-and-consistency-pass.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S13 links to examples/stage-contracts/S13.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S13 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s13_adversarial_review_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S14": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_1",
                "ref": "review outputs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_2",
                "ref": "validator reports"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_3",
                "ref": "affected materials graph"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-backflow-tasks-phase7-overclaim-repair-",
                "ref": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-review-findings-phase7-overclaim-v1-yam",
                "ref": "examples/review_findings/phase7_overclaim.v1.yaml"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when review finding exists",
            "backflow_targets": [
                "S04",
                "S07",
                "S09A",
                "S09B",
                "S15"
            ],
            "completion_gate": "no accepted finding remains unrouted",
            "consumes": [
                "review outputs",
                "validator reports",
                "affected materials graph"
            ],
            "produces": [
                "narrative backflow task",
                "repair task packets",
                "control reselection tasks",
                "response action map"
            ],
            "purpose": "Convert review/loss signals into local repair tasks.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "repair changes upstream claim/spine/material semantics",
                    "review finding severity is high",
                    "repair plan affects multiple downstream nodes"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "planner",
                "rationale": "Backflow planning is controller-owned routing; single planner lane is enough unless severe or multi-node repairs are involved.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "target layer/material",
                "affected downstream nodes",
                "repair mission",
                "owner gate status"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/S14.stage-contract.json",
        "coverage_kind": "script_checked",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_1",
                "ref": "review outputs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_2",
                "ref": "validator reports"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_3",
                "ref": "affected materials graph"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json",
                "stage_id": "S04",
                "stage_name": "Evidence-to-claim admissibility"
            },
            {
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json",
                "stage_id": "S07",
                "stage_name": "Rhetoric terminology and surface-control synthesis"
            },
            {
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json",
                "stage_id": "S09A",
                "stage_name": "Control-material selection"
            },
            {
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json",
                "stage_id": "S15",
                "stage_name": "Repair execution and local regeneration"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s14_pilot_output",
                "artifact_path": "artifacts/S14-backflow-compilation-and-repair-planning.json",
                "artifact_type": "review_backflow_projection",
                "description": "narrative backflow task; repair task packets; control reselection tasks; response action map",
                "payload": {
                    "artifact_kind": "review_backflow_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 6,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "narrative backflow task",
                        "repair task packets",
                        "control reselection tasks",
                        "response action map"
                    ],
                    "purpose": "Convert review/loss signals into local repair tasks.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S14",
                            "validator_ref": "stage_overlay:nature_expert_writing:S14"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "planner",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-backflow-tasks-phase7-overclaim-repair-",
                "ref": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-review-findings-phase7-overclaim-v1-yam",
                "ref": "examples/review_findings/phase7_overclaim.v1.yaml"
            }
        ],
        "stage_id": "S14",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S14",
                "validator_ref": "stage_overlay:nature_expert_writing:S14"
            }
        ],
        "stage_name": "Backflow compilation and repair planning",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S14 links to examples/stage-contracts/S14.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S14 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    },
    "S15": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_1",
                "ref": "backflow task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_2",
                "ref": "target material"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_3",
                "ref": "stale downstream set"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-candidate-returns-intro-candidate-retur",
                "ref": "examples/candidate_returns/intro_candidate_return.phase7.yaml"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when repair task exists",
            "backflow_targets": [
                "S09B",
                "S10",
                "S11",
                "S12",
                "S15"
            ],
            "completion_gate": "graph records new version and affected nodes are revalidated",
            "consumes": [
                "backflow task packet",
                "target material",
                "stale downstream set"
            ],
            "produces": [
                "revised material",
                "regenerated task packet",
                "revised text/figure",
                "updated validator report"
            ],
            "purpose": "Execute bounded backflow task and regenerate only affected downstream outputs.",
            "requires_worker_task_packet": true,
            "subagent_lane_policy": {
                "default_lane_count": 2,
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "policy": "mandatory_double",
                "producer_agent_type": "executor",
                "rationale": "Repair execution changes accepted materials; independent verification is mandatory to prove the finding is resolved without regressions.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "scoped stale propagation",
                "unrelated nodes unchanged",
                "finding resolved",
                "no new high severity finding"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/claim_repair_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            }
        },
        "contract_ref": "examples/stage-contracts/S15.stage-contract.json",
        "coverage_kind": "fixture_generated",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_1",
                "ref": "backflow task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_2",
                "ref": "target material"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_3",
                "ref": "stale downstream set"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json",
                "stage_id": "S09B",
                "stage_name": "Per-unit task packet assembly"
            },
            {
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json",
                "stage_id": "S10",
                "stage_name": "Main-text production"
            },
            {
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json",
                "stage_id": "S12",
                "stage_name": "Integration and consistency pass"
            },
            {
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json",
                "stage_id": "S16",
                "stage_name": "Export repository hygiene and handoff"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s15_pilot_output",
                "artifact_path": "artifacts/S15-repair-execution-and-local-regeneration.json",
                "artifact_type": "candidate_or_repair_projection",
                "description": "revised material; regenerated task packet; revised text/figure; updated validator report",
                "payload": {
                    "artifact_kind": "candidate_or_repair_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 6,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "revised material",
                        "regenerated task packet",
                        "revised text/figure",
                        "updated validator report"
                    ],
                    "purpose": "Execute bounded backflow task and regenerate only affected downstream outputs.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S15",
                            "validator_ref": "stage_overlay:nature_expert_writing:S15"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "executor",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-candidate-returns-intro-candidate-retur",
                "ref": "examples/candidate_returns/intro_candidate_return.phase7.yaml"
            }
        ],
        "stage_id": "S15",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S15",
                "validator_ref": "stage_overlay:nature_expert_writing:S15"
            }
        ],
        "stage_name": "Repair execution and local regeneration",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S15 links to examples/stage-contracts/S15.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S15 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/claim_repair_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        }
    },
    "S16": {
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_1",
                "ref": "clean final candidate"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_2",
                "ref": "review closure"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_3",
                "ref": "repair-complete package"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_4",
                "ref": "figures/captions"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_5",
                "ref": "repository state"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "contract": {
            "activation_policy": "activate when export/handoff requested",
            "backflow_targets": [
                "S12",
                "S13",
                "S15",
                "owner"
            ],
            "completion_gate": "content-ready and delivery-clean states are separately proven; external submission remains owner-gated",
            "consumes": [
                "clean final candidate",
                "review closure",
                "repair-complete package",
                "figures/captions",
                "repository state"
            ],
            "produces": [
                "export manifest",
                "repository hygiene report",
                "manager handoff report"
            ],
            "purpose": "Package final paper and prove delivery cleanliness.",
            "requires_worker_task_packet": false,
            "subagent_lane_policy": {
                "default_lane_count": 1,
                "escalate_to_double_when": [
                    "handoff/export is owner-facing",
                    "dirty-worktree or build hygiene is ambiguous",
                    "release/submission boundary is near"
                ],
                "policy": "conditional_double",
                "producer_agent_type": "verifier",
                "rationale": "Export/handoff is mostly deterministic hygiene; escalate when the output is owner-facing or boundary-sensitive.",
                "verifier_agent_type": "verifier"
            },
            "validators": [
                "build success",
                "rendered surface checks",
                "manifest hashes",
                "dirty worktree classification"
            ],
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            },
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            }
        },
        "contract_ref": "examples/stage-contracts/S16.stage-contract.json",
        "coverage_kind": "script_checked",
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_1",
                "ref": "clean final candidate"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_2",
                "ref": "review closure"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_3",
                "ref": "repair-complete package"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_4",
                "ref": "figures/captions"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_5",
                "ref": "repository state"
            }
        ],
        "execution_mode": "hybrid_generated",
        "exercise_level": "full_stage_exercised",
        "handoff_consumers": [
            {
                "material_id": "s16_pilot_output",
                "ref": "artifacts/S16-export-repository-hygiene-and-handoff.json",
                "stage_id": "G02",
                "stage_name": "Derivative and post-paper outputs"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s16_pilot_output",
                "artifact_path": "artifacts/S16-export-repository-hygiene-and-handoff.json",
                "artifact_type": "analysis_material_projection",
                "description": "export manifest; repository hygiene report; manager handoff report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "consumed_ref_count": 10,
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "projected_outputs": [
                        "export manifest",
                        "repository hygiene report",
                        "manager handoff report"
                    ],
                    "purpose": "Package final paper and prove delivery cleanliness.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S16",
                            "validator_ref": "stage_overlay:nature_expert_writing:S16"
                        }
                    ]
                }
            }
        ],
        "recommended_agent_type": "verifier",
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        },
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            }
        ],
        "stage_id": "S16",
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S16",
                "validator_ref": "stage_overlay:nature_expert_writing:S16"
            }
        ],
        "stage_name": "Export repository hygiene and handoff",
        "status": "validated",
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S16 links to examples/stage-contracts/S16.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S16 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        }
    }
};


  return { meta, legend, defaultVisibleKinds, layers, nodes, edges, presets, roadmap, runtimeState, stageCoverage, stageRunDetails };
})();
