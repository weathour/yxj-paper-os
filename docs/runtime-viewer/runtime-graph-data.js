window.PPG_RUNTIME_GRAPH = (() => {
  const meta = {
    title: 'PPG Runtime 人工把握视图',
    subtitle: '显式物料图 + 局部反向传播 + 主 Agent 调度',
    canvas: { width: 2220, height: 1540 },
  };
  const legend = {
    material: '物料正向流',
    dispatch: '主 Agent 派发',
    validation: '验证与门控',
    graph: '图状态读写',
    backflow: '审核回流',
    governance: '治理与 sidecar',
  };
  const nodeRows = [
    ['OWNER','control','control',40,48,250,92,'Human owner','人类作者/语义权威','提供需求、边界、审稿偏好和关键取舍，批准会改变论文核心语义的决策。',['真实写作需求','目标期刊或读者','可接受风险','核心禁区'],['语义授权','重大决策','边界修订','最终接受或退回'],['是否涉及核心语义改变'],['S00']],
    ['CTRL','controller','control',370,36,560,112,'Main Agent / Runtime Controller','主 Agent / Runtime 控制器','观察物料图，选择前沿节点，编译任务包，调度 subagent 或程序，收集候选产物，执行验证和提交。',['Owner 决策','物料图状态','验证报告','回流任务'],['TaskPacket','MaterialBundle','调度命令','提交或回滚决策'],['只有主 Agent 可以宣布图节点完成'],['任意 stale 节点']],
    ['GRAPH','graph','control',1000,36,500,112,'Versioned Material Graph / Ledger','版本化物料图 / Ledger','保存节点、边、版本、依赖、验证器、来源锚点、stale 传播和 sidecar 状态。',['候选产物','验证结果','依赖变化','回流标记'],['可执行前沿','物料版本','stale 集合','可视化数据'],['schema 校验','依赖完整性校验','版本一致性校验'],['CTRL']],
    ['VALIDATORS','validator','control',1560,36,390,112,'Validator Registry','验证器注册表','集中管理 schema、证据、引用、审稿体验、渲染、导出和仓库卫生检查。',['候选物料','目标节点契约','期刊模板','证据锚点'],['通过/失败','错误定位','严重度','回流建议'],['主 Agent 选择并解释验证器'],['S14']],
    ['BUS','bus','control',370,198,1130,78,'TaskPacket + Structured MaterialBundle Bus','任务包 + 结构化物料包总线','把大上下文变成结构化包，而不是压缩成摘要。每个环节只负责一个有边界的产物。',['任务目标','强制控制项','证据和来源锚点','局部上下文','可选背景','禁用路线','验证器','返回格式'],['可派发任务包','subagent 输入包','程序转换输入'],['字段完整性','上下文边界','禁止路线存在性'],['CTRL']],

    ['S00','stage','root',40,330,360,152,'Owner semantic contract','S00 人类需求与语义契约','把人的真实写作目的转成论文 runtime 可执行的约束，确定什么能自动推进，什么必须回到人类。',['human need','paper profile','evidence summary'],['profile','motivation','core decisions','forbidden routes'],['目标具体','禁用路线显式','证据足以进入后续阶段'],['OWNER']],
    ['S01','stage','inventory',470,330,360,152,'Source/citation/evidence inventory','S01 来源、引用、证据盘点','建立论文能够使用的真实材料边界，防止后续写作脱离证据。',['files','BibTeX','result dirs','locators'],['source map','citation bank','evidence bank','Nature source inventory'],['路径可访问','引用字段完整','证据可追溯'],['S00']],
    ['S02','analysis','research',900,330,360,152,'Research / scene / template / SOTA','S02 研究场景、模板、SOTA 分析','把材料放入读者、期刊模板、领域争论和相关工作的位置中。',['source map','venue','exemplars'],['research dossier','reader package','search strategy','template or journal profile'],['场景覆盖读者问题','模板约束可执行','SOTA 可引用'],['S01']],
    ['S03','analysis','research',1330,330,360,152,'Novelty / contribution options','S03 新颖性与贡献选项','产生可选贡献路线，但必须经过证据可承载性门控。',['research','evidence','SOTA','motivation'],['contribution options','evidence-readiness','risk list'],['贡献可被证据支持','风险显式','避免过度声明'],['S02','S04']],

    ['S04','gate','claim',40,585,360,152,'Evidence-to-claim admissibility','S04 证据到主张的准入门','把实验、引用和观察变成可写入论文的 claim capsule，确定哪些话能说、说到什么强度。',['evidence bank','citations','results'],['claim capsules','result packages','claim visibility','data availability'],['每个 claim 有证据锚点','结论强度不过载','数据可用性明确'],['S01','S00']],
    ['S05','design','spine',470,585,360,152,'Paper spine / reader questions','S05 论文主脊与读者问题','形成论文从问题到贡献到证据的主线，定义读者每一节需要得到的答案。',['motivation','contribution','template','claims'],['reader spine','reviewer question map','rationale matrix'],['章节问题递进','主线单一','读者疑问被覆盖'],['S03','S04']],
    ['S06','design','spine',900,585,360,152,'Object / granularity design','S06 对象表示与颗粒度设计','决定论文里哪些对象、变量、机制、图表和术语要出现到什么细度。',['spine','questions','template','claim visibility'],['object representation','section budget','load budget','explanation ladder'],['概念层级不混乱','读者负荷可控','支撑 claim 可见性'],['S05']],
    ['S07','design','surface',1330,585,360,152,'Rhetoric / terminology / surface controls','S07 修辞、术语与表层控制','控制语气、术语、句式、段落组织和论文表面，防止概念正确但表达失焦。',['object design','claim visibility','evidence wording'],['construction matrix','rhetorical matrix','terminology register','surface rules'],['术语一致','claim 强度匹配','表层贴近目标期刊'],['S06','S04']],
    ['S08','design','visual',1760,585,360,152,'Visual / formal planning','S08 图表与形式对象规划','为图、表、公式、算法、补充材料建立契约，避免正文写完后再补图。',['spine','section budget','claims/evidence'],['visual budget','figure contract','aesthetic profile','panel evidence','backend route'],['图有论证功能','panel 绑定证据','导出路径明确'],['S05','S04']],

    ['S09','packet','writing',40,840,360,152,'Main-text packet compilation','S09 正文任务包编译','把几乎所有前置物料汇入一个局部写作任务包，锁定目标小节和单写作者上下文。',['control materials','target unit'],['task packet','section move plan','single-writer lock'],['含核心控制项','目标小节有边界','避免多人同时改同一文本'],['S04','S05','S07']],
    ['S10','production','writing',470,840,360,152,'Main-text production','S10 正文产出','基于任务包写出候选文本单元，不能自行宣布最终完成。',['task packet','construction','terminology','claim/evidence'],['candidate text units'],['claim 有锚点','术语一致','段落功能满足任务包'],['S09','S07']],
    ['S11','production','visual',900,840,360,152,'Figure / caption / formal production','S11 图表、caption 与形式对象产出','生成图、表、caption、算法或公式相关产物，并把数据来源和导出痕迹留在物料图中。',['figure contract','panel evidence','source data','caption brief'],['figure stats','image integrity','caption brief','figure export bundle','artifacts'],['图像可打开','caption 承接 claim','数据可追踪'],['S08','S04']],
    ['S12','integration','integration',1330,840,360,152,'Integration / consistency pass','S12 集成与一致性检查','合并正文和图表，检查术语、claim、引用、图文关系和章节递进。',['candidate modules','figures','terminology','claims'],['integrated manuscript candidate','consistency findings'],['跨章节术语一致','图文互相引用','claim 不漂移'],['S10','S11','S07']],

    ['S13','review','review',40,1095,360,152,'Adversarial review / loss','S13 对抗审核与损失信号','审核器只产生 findings 和 loss，不直接重写全文。',['manuscript','evidence','narrative','figures/export'],['review reports','reader surface report','rendered gate','validator report'],['审稿人视角问题','证据断裂','表层和模板问题','导出问题'],['S14']],
    ['S14','review','backflow',470,1095,360,152,'Backflow compilation','S14 回流任务编译','把审核 findings 映射到最近责任物料，而不是从头重写整篇论文。',['findings','graph state','affected materials'],['narrative backflow task','repair packets','polishing/response plans'],['定位最近责任节点','标记影响下游','修复任务足够小'],['S04','S07','S09','S15']],
    ['S15','repair','backflow',900,1095,360,152,'Repair / local regeneration','S15 局部修复与再生成','只重写受影响的物料、文本或图表，并重新触发必要验证。',['backflow task','target material','stale downstream set'],['revised material/text/figure','updated validator report'],['目标修复通过','下游 stale 清理','未破坏无关部分'],['S04','S07','S10','S12']],
    ['S16','delivery','delivery',1330,1095,360,152,'Export / handoff / delivery','S16 导出、交付与交接','完成可交付论文、图表、补充材料、仓库卫生和后续交接报告。',['final candidate','figures','review closure','repository state'],['export manifest','repository hygiene report','manager handoff reports'],['导出可打开','引用和图表路径完整','仓库风险明确'],['S13','S15']],

    ['G01','sidecar','governance',1740,770,390,150,'Runtime governance sidecar','G01 Runtime 治理 sidecar','保存权限、技能、部门元数据、路线记录和状态控制，不直接进入正文认知链。',['state','permissions','department metadata'],['skill registry','route/governance records','state controls','authority limits'],['是否越权','是否污染写作物料'],['CTRL']],
    ['G02','sidecar','derivative',1740,990,390,150,'Derivative/post-paper sidecar','G02 论文后派生 sidecar','稳定论文之后再派生 PPT、专利边界、Nature 吸收包等，不干扰当前论文完成。',['stable paper','owner request'],['presentation plan','patent boundary','Nature absorption package'],['是否晚于论文稳定点','是否不回写污染正文'],['S16']],
    ['FINAL','final','delivery',730,1370,650,92,'Final Paper Artifact','最终论文产物','正文、图表、补充材料、证据链、导出清单和给人的交接说明。',['S16 delivery package'],['manuscript','figures','supplement','provenance','owner handoff'],['人类最终验收'],['S13','S00']],
  ];
  const nodes = nodeRows.map(([id,type,phase,x,y,w,h,title,titleZh,description,inputs,outputs,validators,backflowTargets]) => ({ id,type,phase,x,y,w,h,title,titleZh,description,inputs,outputs,validators,backflowTargets }));
  const edges = [
    ['c1','governance','OWNER','CTRL','需求/决策'], ['c2','graph','CTRL','GRAPH','读写物料图'], ['c3','validation','GRAPH','VALIDATORS','验证请求'], ['c4','validation','VALIDATORS','CTRL','验证报告'], ['c5','dispatch','CTRL','BUS','编译任务包'],
    ['m00','material','S00','S01','profile -> inventory'], ['m01','material','S01','S02','source map'], ['m02','material','S02','S03','research dossier'], ['m03','material','S01','S04','evidence bank'], ['m04','material','S03','S05','contribution options'], ['m05','material','S04','S05','claim capsules'], ['m06','material','S05','S06','reader spine'], ['m07','material','S06','S07','object design'], ['m08','material','S05','S08','spine to figures'], ['m09','material','S04','S09','claim control'], ['m10','material','S05','S09','spine control'], ['m11','material','S06','S09','granularity control'], ['m12','material','S07','S09','surface control'], ['m13','material','S08','S11','figure contract'], ['m14','material','S09','S10','text task packet'], ['m15','material','S10','S12','candidate text'], ['m16','material','S11','S12','figure bundle'], ['m17','material','S12','S13','integrated candidate'], ['m18','material','S13','S14','findings/loss'], ['m19','material','S14','S15','repair packets'], ['m20','material','S15','S16','delivery-ready package'], ['m21','material','S16','FINAL','final artifact'],
    ['v1','validation','S04','VALIDATORS','claim/evidence gate'], ['v2','validation','S12','VALIDATORS','consistency gate'], ['v3','validation','S13','VALIDATORS','review gate'], ['v4','validation','S16','VALIDATORS','export gate'],
    ['b1','backflow','S14','S07','L1-L2 表层/术语','leftRail'], ['b2','backflow','S14','S04','L3 claim/evidence','leftRail'], ['b3','backflow','S14','S00','L4 语义重置','leftRail'], ['b4','backflow','S15','S10','局部文本再生成'], ['b5','backflow','S15','S12','重新集成验证'],
    ['g1','governance','G01','CTRL','权限/路线控制'], ['g2','governance','G01','GRAPH','状态控制'], ['g3','governance','S16','G02','论文后派生'],
  ].map(([id,kind,source,target,label,route]) => ({ id,kind,source,target,label,route }));
  nodes.filter((node) => node.id.startsWith('S')).forEach((node, index) => edges.push({ id: `d${String(index).padStart(2,'0')}`, kind: 'dispatch', source: 'BUS', target: node.id, label: 'dispatch' }));
  const presets = [
    { id: 'all', label: '全流程', nodes: ['OWNER','CTRL','GRAPH','VALIDATORS','BUS','S00','S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14','S15','S16','G01','G02','FINAL'] },
    { id: 'writing', label: '写作汇入', nodes: ['S04','S05','S06','S07','S08','S09','S10','S11','S12'] },
    { id: 'review', label: '审核回流', nodes: ['S12','S13','S14','S15','S04','S07','S09','S10'] },
    { id: 'control', label: '控制面', nodes: ['OWNER','CTRL','GRAPH','VALIDATORS','BUS','G01'] },
  ];
  return { meta, legend, nodes, edges, presets };
})();
