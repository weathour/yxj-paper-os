(function initRuntimeViewer() {
  const graph = window.PPG_RUNTIME_GRAPH;
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));
  const edgeKinds = Object.keys(graph.legend);
  const stageRuns = graph.stageCoverage?.stage_runs || [];
  const stageRunById = new Map(stageRuns.map((stage) => [stage.stage_id, stage]));
  const stageDetailById = new Map(Object.entries(graph.stageRunDetails || {}));
  const stageOrder = stageRuns.map((stage) => stage.stage_id);
  const nonCanvasModes = new Set(['state', 'coverage', 'workbench']);
  const stageFriendly = {
    S00: { zh: '定目标与边界', en: 'Set goals and boundaries', handoff: '把人的写作目的、禁区和需要人工批准的事项变成后续环节可执行的约束。' },
    S01: { zh: '盘点来源与证据', en: 'Inventory sources and evidence', handoff: '把论文能使用的文件、引用、结果目录和证据位置整理成可追踪材料库。' },
    S02: { zh: '看清研究位置', en: 'Map the research position', handoff: '把证据放进领域、读者、模板和 SOTA 背景中，形成后续贡献判断的语境。' },
    S03: { zh: '形成贡献候选', en: 'Shape contribution options', handoff: '提出可能的贡献说法和风险，但必须交给 S04 判断哪些能被证据承载。' },
    S04: { zh: '锁定能说的主张', en: 'Lock evidence-backed claims', handoff: '把证据、引用和结果转成可写 claim，明确能说什么、强度到哪里为止。' },
    S05: { zh: '搭建论文主线', en: 'Build the paper spine', handoff: '把可写主张组织成读者一路能跟上的问题链和章节主线。' },
    S06: { zh: '设计对象与颗粒度', en: 'Design objects and granularity', handoff: '决定论文中哪些对象、变量、机制和解释层级需要出现，以及细到什么程度。' },
    S07: { zh: '统一术语与表达', en: 'Align terminology and tone', handoff: '把术语、语气、段落功能和表层表达规则交给写作任务包。' },
    S08: { zh: '规划图表与形式对象', en: 'Plan figures and formal objects', handoff: '把主线、证据和读者问题转成图表、公式、算法、补充材料的契约。' },
    S09A: { zh: '选择写作控制材料', en: 'Select writing controls', handoff: '从 claim、主线、颗粒度和表层规则中挑出当前单元真正需要的控制材料。' },
    S09B: { zh: '组装单元任务包', en: 'Assemble unit task packets', handoff: '把选定控制材料、证据锚点、边界和返回格式编译成可派发的 TaskPacket。' },
    S10: { zh: '产出正文候选', en: 'Draft text candidates', handoff: '子 agent 只根据任务包产出候选正文和证据，不拥有完成权。' },
    S11: { zh: '产出图表与说明', en: 'Produce figures and captions', handoff: '根据图表契约和证据位置生成图、表、caption、公式或算法相关产物。' },
    S12: { zh: '合并并查一致性', en: 'Integrate and check consistency', handoff: '把正文、图表、引用和术语合在一起，检查跨章节是否漂移。' },
    S13: { zh: '对抗审稿找问题', en: 'Run adversarial review', handoff: '像审稿人一样输出 findings/loss，不直接重写全文。' },
    S14: { zh: '把问题转成修复任务', en: 'Compile repair tasks', handoff: '把审核问题定位到最近责任材料，形成局部 backflow 和 repair packets。' },
    S15: { zh: '局部修复与再生成', en: 'Repair and regenerate locally', handoff: '只修受影响的材料、文本或图表，再触发必要验证。' },
    S16: { zh: '导出、整理与交接', en: 'Export, clean, and hand off', handoff: '在 review/repair 闭合后整理导出物、仓库卫生和交接说明。' },
    G01: { zh: '运行治理与权限', en: 'Runtime governance and authority', handoff: '记录权限、路线、状态和控制边界，防止治理信息污染正文材料。' },
    G02: { zh: '论文后派生输出', en: 'Post-paper derivatives', handoff: '论文稳定后再派生 PPT、专利边界、期刊 profile 等外部材料。' },
    FINAL: { zh: '最终论文包', en: 'Final paper package', handoff: '聚合正文、图表、补充材料、证据链和 owner handoff。' },
  };
  const kindColors = {
    material: 'var(--material)', dispatch: 'var(--dispatch)', validation: 'var(--validation)',
    graph: 'var(--graph)', backflow: 'var(--backflow)', governance: 'var(--governance)', control: 'var(--governance)',
  };
  const primaryRoadmapEdges = new Set(['r-01','r-02','r-03','r-04','r-05','r-06','r-07','r-08','r-09','r-10','r-11','r-12','r-clean','r-15']);
  const roadmapFocusGroups = [
    { id: 'figures', nodes: new Set(['S01','S04','S05','S06','S08','S11','S12']), edges: new Set(['r-b0','r-b1','r-b1a','r-b2a','r-b2b','r-b2','r-b3']) },
  ];
  const FLOW_RAIL_GAPS = { roadmap: 36, graph: 20 };
  const urlPreset = new URLSearchParams(window.location.search).get('preset');
  const initialPreset = graph.presets.find((preset) => preset.id === urlPreset) || graph.presets.find((preset) => preset.id === 'all');
  const state = {
    mode: 'roadmap', selectedId: initialPreset.id === 'all' ? 'S00' : initialPreset.nodes[0], query: '',
    zooms: { roadmap: 0.72, graph: 0.62 },
    visibleKinds: new Set(graph.defaultVisibleKinds || edgeKinds),
    activePreset: initialPreset.id, focusSet: new Set(initialPreset.nodes), stepIndex: 0,
  };

  const laneLayer = document.getElementById('laneLayer');
  const nodeLayer = document.getElementById('nodeLayer');
  const edgeLayer = document.getElementById('edgeLayer');
  const graphCanvas = document.getElementById('graphCanvas');
  const graphFrame = document.getElementById('canvasFrame');
  const graphStage = document.getElementById('graphStage');
  const roadmapLaneLayer = document.getElementById('roadmapLaneLayer');
  const roadmapNodeLayer = document.getElementById('roadmapNodeLayer');
  const roadmapEdgeLayer = document.getElementById('roadmapEdgeLayer');
  const roadmapCanvas = document.getElementById('roadmapCanvas');
  const roadmapFrame = document.getElementById('roadmapFrame');
  const roadmapStage = document.getElementById('roadmapStage');
  const detailContent = document.getElementById('detailContent');
  const nodeIndex = document.getElementById('nodeIndex');
  const presetButtons = document.getElementById('presetButtons');
  const edgeFilters = document.getElementById('edgeFilters');
  const referenceFigure = document.getElementById('referenceFigure');
  const runtimeStateFrame = document.getElementById('runtimeStateFrame');
  const runtimeStateContent = document.getElementById('runtimeStateContent');
  const stageCoverageFrame = document.getElementById('stageCoverageFrame');
  const stageCoverageContent = document.getElementById('stageCoverageContent');
  const stageWorkbenchFrame = document.getElementById('stageWorkbenchFrame');
  const stageWorkbenchContent = document.getElementById('stageWorkbenchContent');

  graphCanvas.style.width = `${graph.meta.canvas.width}px`;
  graphCanvas.style.height = `${graph.meta.canvas.height}px`;
  edgeLayer.setAttribute('viewBox', `0 0 ${graph.meta.canvas.width} ${graph.meta.canvas.height}`);
  roadmapCanvas.style.width = `${graph.roadmap.canvas.width}px`;
  roadmapCanvas.style.height = `${graph.roadmap.canvas.height}px`;
  roadmapEdgeLayer.setAttribute('viewBox', `0 0 ${graph.roadmap.canvas.width} ${graph.roadmap.canvas.height}`);

  function textIncludes(node, query) {
    if (!query) return true;
    const haystack = [node.id, node.title, node.titleZh, node.phase, node.description, ...node.inputs, ...node.outputs, ...node.validators, ...node.backflowTargets].join(' ').toLowerCase();
    return haystack.includes(query.toLowerCase());
  }
  function truncate(value, max = 48) { return value.length > max ? `${value.slice(0, max - 1)}…` : value; }
  function ensureStageSelection() {
    if (!stageDetailById.has(state.selectedId) && stageOrder.length) state.selectedId = stageOrder[0];
  }
  function selectedStageDetail() {
    return stageDetailById.get(state.selectedId) || stageDetailById.get(stageOrder[0]);
  }
  function friendlyStage(id) { return stageFriendly[id] || {}; }
  function stageTitleZh(node) { return friendlyStage(node.id).zh || node.titleZh; }
  function stageTitleEn(node) { return friendlyStage(node.id).en || node.title; }
  function stageDisplayName(stageId) {
    const node = nodeById.get(stageId);
    return node ? `${stageId} ${stageTitleZh(node)}` : stageId;
  }

  function laneMarkup(layer) {
    return `<div class="lane-label"><strong>${layer.title}</strong><span>${layer.subtitle}</span></div>`;
  }
  function renderLanes(target, layers) {
    target.innerHTML = '';
    layers.forEach((layer) => {
      const section = document.createElement('section');
      section.className = `runtime-lane tone-${layer.tone || 'control'}`;
      section.style.top = `${layer.y}px`;
      section.style.height = `${layer.h}px`;
      section.innerHTML = laneMarkup(layer);
      target.appendChild(section);
    });
  }

  function nodeCardMarkup(node, compact = false) {
    if (compact) {
      return `<div class="node-head"><span class="node-id">${node.id}</span><span class="node-phase">${node.phase}</span></div><div><div class="node-title">${stageTitleZh(node)}</div><div class="node-subtitle">${stageTitleEn(node)}</div></div><div class="io-preview"><span><strong>OUT</strong>${truncate(node.outputs.slice(0, 2).join('；'), 44)}</span></div>`;
    }
    return `<div class="node-head"><span class="node-id">${node.id}</span><span class="node-phase">${node.phase}</span></div><div><div class="node-title">${stageTitleZh(node)}</div><div class="node-subtitle">${stageTitleEn(node)}</div></div><div class="io-preview"><span><strong>IN</strong>${truncate(node.inputs.join('；'), 48)}</span><span><strong>OUT</strong>${truncate(node.outputs.join('；'), 48)}</span></div>`;
  }

  function renderGraphNodes() {
    nodeLayer.innerHTML = '';
    graph.nodes.forEach((node) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `node-card type-${node.type}`;
      button.dataset.id = node.id;
      button.style.left = `${node.x}px`; button.style.top = `${node.y}px`; button.style.width = `${node.w}px`; button.style.height = `${node.h}px`;
      button.setAttribute('aria-label', `${node.id} ${node.titleZh}`);
      button.innerHTML = nodeCardMarkup(node);
      button.addEventListener('click', () => selectNode(node.id));
      nodeLayer.appendChild(button);
    });
  }

  function renderRoadmapNodes() {
    roadmapNodeLayer.innerHTML = '';
    graph.roadmap.nodes.forEach((routeNode) => {
      const node = nodeById.get(routeNode.id);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `node-card route-card type-${node.type}`;
      button.dataset.id = node.id;
      button.style.left = `${routeNode.x}px`; button.style.top = `${routeNode.y}px`; button.style.width = `${routeNode.w}px`; button.style.height = `${routeNode.h}px`;
      button.setAttribute('aria-label', `${node.id} ${node.titleZh}`);
      button.innerHTML = nodeCardMarkup(node, true);
      button.addEventListener('click', () => selectNode(node.id));
      roadmapNodeLayer.appendChild(button);
    });
  }

  function renderIndex() {
    nodeIndex.innerHTML = '';
    graph.nodes.forEach((node) => {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'index-button'; button.dataset.id = node.id;
      button.innerHTML = `<span class="id">${node.id}</span><span>${stageTitleZh(node)}</span>`;
      button.addEventListener('click', () => selectNode(node.id, true));
      nodeIndex.appendChild(button);
    });
  }

  function renderPresets() {
    presetButtons.innerHTML = '';
    graph.presets.forEach((preset) => {
      const button = document.createElement('button');
      button.type = 'button'; button.textContent = preset.label; button.dataset.preset = preset.id;
      button.addEventListener('click', () => activatePreset(preset.id));
      presetButtons.appendChild(button);
    });
  }

  function renderFilters() {
    edgeFilters.innerHTML = '';
    edgeKinds.forEach((kind) => {
      const label = document.createElement('label');
      label.className = 'filter-item';
      label.innerHTML = `<input type="checkbox" data-kind="${kind}" /><span class="filter-swatch" style="--swatch:${kindColors[kind]}"></span><span>${graph.legend[kind]}</span>`;
      const checkbox = label.querySelector('input');
      checkbox.checked = state.visibleKinds.has(kind);
      checkbox.addEventListener('change', (event) => {
        if (event.target.checked) state.visibleKinds.add(kind); else state.visibleKinds.delete(kind);
        update();
      });
      edgeFilters.appendChild(label);
    });
  }

  class NodeBox {
    constructor(element) {
      this.id = element.dataset.id;
      this.x = element.offsetLeft;
      this.y = element.offsetTop;
      this.w = element.offsetWidth;
      this.h = element.offsetHeight;
    }
    port(name) {
      const centerX = this.x + this.w / 2;
      if (name === 'in') return { x: centerX, y: this.y };
      if (name === 'out') return { x: centerX, y: this.y + this.h };
      return { x: centerX, y: this.y + this.h / 2 };
    }
  }

  class LeftRailRouter {
    constructor({ boxes, railX }) {
      this.boxes = boxes;
      this.railX = railX;
      this.explicitOffsets = new Map([
        ['r-b0', 22], ['r-b1', 44], ['r-b1a', 66], ['r-b2a', 88], ['r-b2b', 110], ['r-b2', 132], ['r-b3', 154],
      ]);
      this.explicitTracks = new Map([
        ['r-b0', 0], ['r-b1', 14], ['r-b1a', 28], ['r-b2a', 42], ['r-b2b', 56], ['r-b2', 70], ['r-b3', 84],
      ]);
    }
    bendOffset(edge, edgeIndex) {
      return this.explicitOffsets.get(edge.id) || (20 + (edgeIndex % 6) * 5);
    }
    railTrack(edge) {
      return this.railX + (this.explicitTracks.get(edge.id) || 0);
    }
    route(edge, edgeIndex) {
      const source = this.boxes.get(edge.source);
      const target = this.boxes.get(edge.target);
      if (!source || !target) return null;
      const out = source.port('out');
      const input = target.port('in');
      const offset = this.bendOffset(edge, edgeIndex);
      const railX = this.railTrack(edge);
      const sourceExitY = out.y + offset;
      const targetEntryY = Math.max(12, input.y - offset);
      return {
        path: `M ${out.x} ${out.y} V ${sourceExitY} H ${railX} V ${targetEntryY} H ${input.x} V ${input.y}`,
        label: { x: Math.max(railX + 20, input.x - 200), y: input.y - 10 },
        sourcePort: out,
        targetPort: input,
      };
    }
  }

  function measureNodeBoxes(layer) {
    return new Map(Array.from(layer.querySelectorAll('.node-card')).map((element) => {
      const box = new NodeBox(element);
      return [box.id, box];
    }));
  }
  function railXFor(boxes, mode) {
    const minNodeX = Math.min(...Array.from(boxes.values()).map((box) => box.x));
    return Math.max(48, minNodeX - FLOW_RAIL_GAPS[mode]);
  }
  function setRailPosition(canvas, railX) {
    canvas.style.setProperty('--flow-rail-x', `${railX}px`);
  }
  function renderEdgeSet(svg, edges, boxes, modeClass, railX) {
    const router = new LeftRailRouter({ boxes, railX });
    const paths = [];
    const ports = [];
    const labels = [];
    svg.innerHTML = '';
    edges.forEach((edge, index) => {
      const route = router.route(edge, index);
      if (!route) return;
      const kind = edgeKinds.includes(edge.kind) ? edge.kind : 'governance';
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('id', edge.id);
      path.setAttribute('class', `edge-path ${modeClass} kind-${kind}${primaryRoadmapEdges.has(edge.id) ? ' primary-edge' : ''}`);
      path.setAttribute('d', route.path);
      path.setAttribute('stroke', kindColors[kind]);
      path.dataset.kind = kind;
      path.dataset.source = edge.source;
      path.dataset.target = edge.target;
      paths.push(path);
      const sourcePort = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      sourcePort.setAttribute('class', `edge-port ${modeClass} edge-port-source kind-${kind}`);
      sourcePort.setAttribute('cx', route.sourcePort.x);
      sourcePort.setAttribute('cy', route.sourcePort.y);
      sourcePort.setAttribute('r', 5);
      sourcePort.dataset.kind = kind;
      sourcePort.dataset.source = edge.source;
      sourcePort.dataset.target = edge.target;
      ports.push(sourcePort);
      const targetPort = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      targetPort.setAttribute('class', `edge-port ${modeClass} edge-port-target kind-${kind}`);
      targetPort.setAttribute('cx', route.targetPort.x);
      targetPort.setAttribute('cy', route.targetPort.y);
      targetPort.setAttribute('r', 5);
      targetPort.dataset.kind = kind;
      targetPort.dataset.source = edge.source;
      targetPort.dataset.target = edge.target;
      ports.push(targetPort);
      if (edge.label) {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('class', `edge-label ${modeClass}${primaryRoadmapEdges.has(edge.id) ? ' primary-edge' : ''}`);
        text.setAttribute('x', route.label.x);
        text.setAttribute('y', route.label.y);
        text.textContent = modeClass === 'roadmap-edge' ? `${edge.source}→${edge.target} · ${edge.label}` : edge.label;
        text.dataset.kind = kind;
        text.dataset.source = edge.source;
        text.dataset.target = edge.target;
        labels.push(text);
      }
    });
    [...paths, ...ports, ...labels].forEach((element) => svg.appendChild(element));
  }
  function renderGraphEdges() {
    const boxes = measureNodeBoxes(nodeLayer);
    const railX = railXFor(boxes, 'graph');
    setRailPosition(graphCanvas, railX);
    renderEdgeSet(edgeLayer, graph.edges, boxes, 'graph-edge', railX);
  }
  function renderRoadmapEdges() {
    const boxes = measureNodeBoxes(roadmapNodeLayer);
    const railX = railXFor(boxes, 'roadmap');
    setRailPosition(roadmapCanvas, railX);
    renderEdgeSet(roadmapEdgeLayer, graph.roadmap.edges, boxes, 'roadmap-edge', railX);
  }

  function relatedNodeIds(id) {
    const related = new Set([id]);
    [...graph.edges, ...graph.roadmap.edges].forEach((edge) => { if (edge.source === id) related.add(edge.target); if (edge.target === id) related.add(edge.source); });
    return related;
  }
  function detailBlock(title, items) { return `<section class="detail-section"><h3>${title}</h3><div class="chip-list">${items.map((item) => `<span class="chip">${item}</span>`).join('')}</div></section>`; }

  function createTextElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text == null || text === '' ? '—' : String(text);
    return element;
  }
  function appendKeyValue(parent, label, value) {
    const row = document.createElement('div');
    row.className = 'state-kv';
    row.appendChild(createTextElement('span', 'state-kv__key', label));
    row.appendChild(createTextElement('span', 'state-kv__value', value));
    parent.appendChild(row);
  }
  function appendList(parent, items, className = 'workbench-list') {
    const list = document.createElement('ul');
    list.className = className;
    (items || []).forEach((item) => {
      const row = document.createElement('li');
      row.textContent = String(item);
      list.appendChild(row);
    });
    if (!list.children.length) appendEmpty(parent);
    else parent.appendChild(list);
  }
  function appendStageJump(parent, stageId, label = stageDisplayName(stageId)) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'stage-jump-button';
    button.textContent = label;
    button.addEventListener('click', () => {
      state.mode = 'workbench';
      selectNode(stageId, false);
    });
    parent.appendChild(button);
  }
  function appendPath(parent, label, value) {
    const row = document.createElement('div');
    row.className = 'path-row';
    row.appendChild(createTextElement('span', 'path-row__label', label));
    row.appendChild(createTextElement('code', 'path-row__value', value));
    parent.appendChild(row);
  }
  function appendStateSection(parent, title, subtitle) {
    const section = document.createElement('section');
    section.className = 'state-section';
    section.appendChild(createTextElement('h3', '', title));
    if (subtitle) section.appendChild(createTextElement('p', 'state-section__subtitle', subtitle));
    parent.appendChild(section);
    return section;
  }
  function appendEmpty(section, message = '当前没有待处理项目。') {
    const empty = createTextElement('div', 'empty-state', message);
    section.appendChild(empty);
  }
  function appendCardList(section, items, renderer) {
    const list = document.createElement('div');
    list.className = 'state-card-grid';
    if (!items || !items.length) {
      appendEmpty(section);
      return;
    }
    items.forEach((item, index) => list.appendChild(renderer(item, index)));
    section.appendChild(list);
  }
  function stateCard(title, tone = 'neutral') {
    const card = document.createElement('article');
    card.className = `state-card tone-${tone}`;
    card.appendChild(createTextElement('h4', '', title));
    return card;
  }
  function renderRuntimeState() {
    const runtime = graph.runtimeState;
    runtimeStateContent.textContent = '';
    if (!runtime) {
      appendEmpty(runtimeStateContent, 'runtimeState 数据未加载。');
      return;
    }

    const summary = appendStateSection(runtimeStateContent, 'Graph + Frontier', '主 Agent 首先看这里：当前图、下一前沿、是否有阻塞。');
    const summaryGrid = document.createElement('div');
    summaryGrid.className = 'state-summary-grid';
    const graphCard = stateCard('Graph', 'graph');
    appendKeyValue(graphCard, 'graph_id', runtime.graph.graph_id);
    appendKeyValue(graphCard, 'title', runtime.graph.title);
    appendKeyValue(graphCard, 'source', runtime.graph.source_path);
    appendKeyValue(graphCard, 'nodes / edges', `${runtime.graph.node_count} / ${runtime.graph.edge_count}`);
    const frontierCard = stateCard('Next Frontier', 'frontier');
    appendKeyValue(frontierCard, 'id', runtime.next_frontier.id);
    appendKeyValue(frontierCard, 'kind', runtime.next_frontier.kind);
    appendKeyValue(frontierCard, 'priority', runtime.next_frontier.priority);
    appendKeyValue(frontierCard, 'reason', runtime.next_frontier.reason);
    summaryGrid.appendChild(graphCard);
    summaryGrid.appendChild(frontierCard);
    summary.appendChild(summaryGrid);

    const active = appendStateSection(runtimeStateContent, 'Active Versions', '逻辑物料 -> 当前 committed 节点。');
    appendCardList(active, runtime.active_versions, (item) => {
      const card = stateCard(item.material_id, 'active');
      appendKeyValue(card, 'active node', item.active_node);
      appendKeyValue(card, 'status', item.status);
      appendKeyValue(card, 'version', item.version);
      appendKeyValue(card, 'artifact', item.artifact_path);
      return card;
    });

    const stale = appendStateSection(runtimeStateContent, 'Stale / Candidate Materials', '局部回流和未提交候选物料是 owner/main-agent 决策焦点。');
    appendCardList(stale, [...runtime.stale_materials, ...runtime.candidate_materials], (item) => {
      const tone = item.status === 'stale' ? 'stale' : 'candidate';
      const card = stateCard(item.id, tone);
      appendKeyValue(card, 'status', item.status);
      appendKeyValue(card, 'material', item.material_id || item.candidate_for);
      appendKeyValue(card, 'version', item.version);
      if ('historical_superseded_by_active' in item) appendKeyValue(card, 'historical', item.historical_superseded_by_active);
      if ('on_active_control_path' in item) appendKeyValue(card, 'active path', item.on_active_control_path);
      if (item.candidate_for) appendKeyValue(card, 'candidate_for', item.candidate_for);
      appendKeyValue(card, 'artifact', item.artifact_path);
      return card;
    });

    const review = appendStateSection(runtimeStateContent, 'Review Findings + Backflow Tasks', '审核 finding 不直接重写全文，而是映射到最近责任物料和局部 repair task；已闭合 finding 显示 closed_by。');
    appendCardList(review, [...runtime.open_review_findings, ...runtime.closed_review_findings], (item) => {
      const card = stateCard(item.id, 'review');
      appendKeyValue(card, 'failure', item.failure_type);
      appendKeyValue(card, 'target', item.primary_target);
      appendKeyValue(card, 'closure status', item.closure_status || 'open');
      appendKeyValue(card, 'closed by', (item.closed_by || []).join(', ') || 'none');
      appendKeyValue(card, 'classified repair', item.classified_repair);
      appendKeyValue(card, 'repair tasks', (item.repair_tasks || []).join(', ') || 'none');
      return card;
    });
    appendCardList(review, runtime.backflow_tasks, (item) => {
      const card = stateCard(item.id, 'backflow');
      appendKeyValue(card, 'status', item.status);
      appendKeyValue(card, 'sources', (item.source_findings || []).join(', ') || 'none');
      appendKeyValue(card, 'targets', (item.targets || []).join(', ') || 'none');
      appendKeyValue(card, 'artifact', item.artifact_path);
      return card;
    });

    const owner = appendStateSection(runtimeStateContent, 'Owner Decisions', '只有会改变论文核心语义或授权边界的事项进入 owner queue。');
    appendCardList(owner, runtime.owner_decisions, (item) => {
      const card = stateCard(item.id, 'owner');
      appendKeyValue(card, 'status', item.status);
      appendKeyValue(card, 'label', item.label);
      appendKeyValue(card, 'artifact', item.artifact_path);
      return card;
    });

    const delivery = appendStateSection(runtimeStateContent, 'Delivery Gates + Review Closures', '交付门和 ReviewClosure 证明局部修复已闭合，但不代表 live publish。');
    appendCardList(delivery, [...runtime.delivery_gates, ...runtime.review_closures], (item) => {
      const card = stateCard(item.id, item.id.includes('closure') ? 'closure' : 'delivery');
      appendKeyValue(card, 'status', item.status);
      appendKeyValue(card, 'report id', item.report_id);
      appendKeyValue(card, 'validates', (item.validates || []).join(', ') || 'none');
      appendKeyValue(card, 'artifact', item.artifact_path);
      return card;
    });

    const blockers = appendStateSection(runtimeStateContent, 'Completion Blockers', '这些 blocker 阻止主 Agent 宣称图完成。');
    appendCardList(blockers, runtime.completion_blockers, (item, index) => {
      const card = stateCard(`blocker ${index + 1}`, 'blocker');
      card.appendChild(createTextElement('p', 'state-blocker-text', item));
      return card;
    });
  }

  function renderCountChips(parent, counts) {
    const list = document.createElement('div');
    list.className = 'coverage-chip-list';
    Object.entries(counts || {}).forEach(([key, value]) => {
      const chip = document.createElement('span');
      chip.className = 'coverage-chip';
      chip.appendChild(createTextElement('strong', '', key));
      chip.appendChild(createTextElement('span', '', value));
      list.appendChild(chip);
    });
    if (!list.children.length) appendEmpty(parent, '没有 coverage count。');
    else parent.appendChild(list);
  }

  function toneForCoverage(item) {
    if (item.coverage_kind === 'owner_gated_deferred') return 'owner';
    if (item.worker_packet_status === 'planned_with_blocker') return 'blocker';
    if (item.worker_packet_status === 'linked_strict_packet') return 'active';
    if (item.coverage_kind === 'script_checked') return 'delivery';
    return item.coverage_kind === 'source_projected' ? 'graph' : 'candidate';
  }

  function renderStageCoverage() {
    const coverage = graph.stageCoverage;
    stageCoverageContent.textContent = '';
    if (!coverage) {
      appendEmpty(stageCoverageContent, 'stageCoverage 数据未加载。');
      return;
    }
    const summary = appendStateSection(stageCoverageContent, 'Coverage Summary', '每个 canonical stage 都必须有 PilotStageRun；completion boundary 防止把 pilot 误认为最终论文完成。');
    const summaryGrid = document.createElement('div');
    summaryGrid.className = 'state-summary-grid';
    const countCard = stateCard('PilotStageRun Count', 'frontier');
    appendKeyValue(countCard, 'project', coverage.project_slug);
    appendKeyValue(countCard, 'stage runs', `${coverage.pilot_stage_run_count} / ${coverage.canonical_stage_count}`);
    appendKeyValue(countCard, 'graph', coverage.graph_ref);
    const boundaryCard = stateCard('Completion Boundary', 'delivery');
    boundaryCard.appendChild(createTextElement('p', 'state-blocker-text', coverage.completion_boundary));
    summaryGrid.appendChild(countCard);
    summaryGrid.appendChild(boundaryCard);
    summary.appendChild(summaryGrid);

    const counts = appendStateSection(stageCoverageContent, 'Coverage Kinds + Worker Packets', 'source_projected/script_checked/fixture_generated 是 pilot 的证据类型；linked_strict_packet 表示该 worker stage 已有严格任务包，not_required 表示非 worker stage。');
    renderCountChips(counts, coverage.coverage_kind_counts);
    renderCountChips(counts, coverage.exercise_level_counts);
    renderCountChips(counts, coverage.worker_task_packet_status_counts);
    renderCountChips(counts, coverage.stage_overlay_binding_counts);

    const stages = appendStateSection(stageCoverageContent, 'Stage Runs', '点击左侧 stage 图可看拓扑；这里看每个 stage 的实际 pilot 覆盖、任务包状态、stage-local overlay 和 contract ref。');
    appendCardList(stages, coverage.stage_runs, (item) => {
      const card = stateCard(`${item.stage_id} ${item.stage_name}`, toneForCoverage(item));
      appendKeyValue(card, 'status', item.status);
      appendKeyValue(card, 'coverage', item.coverage_kind);
      appendKeyValue(card, 'exercise', item.exercise_level);
      appendKeyValue(card, 'worker packet', item.worker_packet_status);
      appendKeyValue(card, 'overlay', (item.stage_local_overlays || []).map((overlay) => `${overlay.overlay_id}:${overlay.binding_strength}`).join(', ') || 'none');
      appendKeyValue(card, 'contract', item.contract_ref);
      appendKeyValue(card, 'run', item.run_ref);
      appendStageJump(card, item.stage_id, '打开环节工作台');
      return card;
    });
  }

  function renderStageProgress(parent, selectedId) {
    const rail = document.createElement('div');
    rail.className = 'stage-progress-rail';
    stageRuns.forEach((stage, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `stage-progress-step tone-${toneForCoverage(stage)}`;
      button.classList.toggle('is-active', stage.stage_id === selectedId);
      button.textContent = stage.stage_id;
      button.title = `${stage.stage_id} ${stage.stage_name} · ${stage.status}`;
      button.addEventListener('click', () => selectNode(stage.stage_id, false));
      rail.appendChild(button);
      if (index < stageRuns.length - 1) rail.appendChild(createTextElement('span', 'stage-progress-link', '→'));
    });
    parent.appendChild(rail);
  }

  function renderMaterialGroup(title, items, options = {}) {
    const section = document.createElement('article');
    section.className = 'handoff-column';
    section.appendChild(createTextElement('h4', '', title));
    if (!items || !items.length) {
      appendEmpty(section);
      return section;
    }
    items.forEach((item) => {
      const card = document.createElement('div');
      card.className = 'material-card';
      if (item.producer_stage_id) appendStageJump(card, item.producer_stage_id);
      appendKeyValue(card, 'material', item.material_id || '—');
      appendPath(card, 'ref', item.ref || '—');
      if (options.consumer && item.stage_id) appendStageJump(card, item.stage_id, `进入 ${stageDisplayName(item.stage_id)}`);
      section.appendChild(card);
    });
    return section;
  }

  function renderArtifactCard(artifact) {
    const card = stateCard(artifact.artifact_id || artifact.artifact_path || 'artifact', 'candidate');
    appendKeyValue(card, 'type', artifact.artifact_type || artifact.payload?.artifact_kind);
    appendPath(card, 'path', artifact.artifact_path);
    appendKeyValue(card, 'description', artifact.description);
    if (artifact.payload?.purpose) appendKeyValue(card, 'purpose', artifact.payload.purpose);
    if (artifact.payload?.projected_outputs?.length) {
      const outputs = document.createElement('div');
      outputs.className = 'mini-section';
      outputs.appendChild(createTextElement('strong', '', 'projected outputs'));
      appendList(outputs, artifact.payload.projected_outputs);
      card.appendChild(outputs);
    }
    const snapshot = artifact.payload?.claim_boundary_snapshot;
    if (snapshot) {
      const boundary = document.createElement('div');
      boundary.className = 'boundary-snapshot';
      boundary.appendChild(createTextElement('strong', '', 'claim boundary snapshot'));
      appendKeyValue(boundary, 'method', snapshot.active_method);
      appendPath(boundary, 'evidence', snapshot.evidence_spine);
      appendKeyValue(boundary, 'forbidden overclaim', snapshot.forbidden_overclaim_boundary);
      card.appendChild(boundary);
    }
    return card;
  }

  function renderStageWorkbench() {
    stageWorkbenchContent.textContent = '';
    const detail = selectedStageDetail();
    if (!detail) {
      appendEmpty(stageWorkbenchContent, '没有可展示的 stage-run detail。');
      return;
    }
    const node = nodeById.get(detail.stage_id);

    const progress = appendStateSection(stageWorkbenchContent, 'Overall Progress Map', '这条只读进度条来自 canonical stage coverage；点击任意环节查看其分析、设计和交接。');
    renderStageProgress(progress, detail.stage_id);

    const overview = appendStateSection(stageWorkbenchContent, `${detail.stage_id} · ${detail.stage_name}`, node?.description || detail.contract?.purpose);
    const overviewGrid = document.createElement('div');
    overviewGrid.className = 'workbench-overview-grid';
    const friendly = friendlyStage(detail.stage_id);
    const plainCard = stateCard('使用者看到的环节名', 'frontier');
    appendKeyValue(plainCard, '中文', friendly.zh || detail.stage_name);
    appendKeyValue(plainCard, 'English', friendly.en || detail.stage_name);
    appendKeyValue(plainCard, '官方名', detail.stage_name);
    if (friendly.handoff) plainCard.appendChild(createTextElement('p', 'state-blocker-text', friendly.handoff));
    const stageCard = stateCard('环节状态', toneForCoverage(stageRunById.get(detail.stage_id) || detail));
    appendKeyValue(stageCard, 'status', detail.status);
    appendKeyValue(stageCard, 'coverage', detail.coverage_kind);
    appendKeyValue(stageCard, 'exercise', detail.exercise_level);
    appendKeyValue(stageCard, 'execution', detail.execution_mode);
    appendKeyValue(stageCard, 'agent', detail.recommended_agent_type);
    const lane = detail.contract?.subagent_lane_policy || {};
    const packet = detail.worker_task_packet_evidence || detail.contract?.worker_packet_coverage || {};
    const packetCard = stateCard('任务包 / lane policy', packet.status === 'linked_strict_packet' ? 'active' : 'graph');
    appendKeyValue(packetCard, 'lane policy', lane.policy);
    appendKeyValue(packetCard, 'default lanes', lane.default_lane_count);
    appendKeyValue(packetCard, 'producer', lane.producer_agent_type);
    appendKeyValue(packetCard, 'verifier', lane.verifier_agent_type || 'deterministic validation');
    appendKeyValue(packetCard, 'packet status', packet.status);
    appendPath(packetCard, 'packet', packet.packet_ref || 'not required');
    appendPath(packetCard, 'return contract', packet.return_contract_ref || 'not required');
    const boundaryCard = stateCard('完成边界', 'delivery');
    appendKeyValue(boundaryCard, 'completion gate', detail.contract?.completion_gate);
    boundaryCard.appendChild(createTextElement('p', 'state-blocker-text', detail.completion_claim));
    overviewGrid.appendChild(plainCard);
    overviewGrid.appendChild(stageCard);
    overviewGrid.appendChild(packetCard);
    overviewGrid.appendChild(boundaryCard);
    overview.appendChild(overviewGrid);

    const material = appendStateSection(stageWorkbenchContent, 'Input → Analysis/Design → Handoff', '这里展示信息如何进入本环节、形成什么产物，以及被哪些下游环节消费。');
    const handoff = document.createElement('div');
    handoff.className = 'handoff-grid';
    handoff.appendChild(renderMaterialGroup('契约声明输入', detail.declared_inputs));
    handoff.appendChild(renderMaterialGroup('来源 / runtime refs', detail.source_refs));
    handoff.appendChild(renderMaterialGroup('上游环节产物', detail.upstream_inputs));
    handoff.appendChild(renderMaterialGroup('下游消费', detail.handoff_consumers, { consumer: true }));
    material.appendChild(handoff);

    const artifacts = appendStateSection(stageWorkbenchContent, '具体分析 / 设计产物', '这些是本环节在 pilot 中形成或投影出的物料，仍是只读 evidence，不是最终论文完成声明。');
    appendCardList(artifacts, detail.produced_artifacts || [], renderArtifactCard);

    const validation = appendStateSection(stageWorkbenchContent, 'Validators + Read-only Boundary', '验证证据、overlay、source-read-only 边界共同决定这个环节是否能被主 Agent 接收。');
    const validationGrid = document.createElement('div');
    validationGrid.className = 'workbench-overview-grid';
    const validators = stateCard('contract validators', 'delivery');
    appendList(validators, detail.contract?.validators || []);
    const evidence = stateCard('validator evidence', 'closure');
    appendList(evidence, (detail.validator_evidence || []).map((item) => `${item.status}: ${item.validator} — ${item.evidence}`));
    const readonly = stateCard('source boundary', 'graph');
    const boundary = detail.source_projection_boundary || {};
    appendKeyValue(readonly, 'read only source', boundary.read_only_source);
    appendKeyValue(readonly, 'writes allowed', boundary.writes_to_source_allowed);
    appendKeyValue(readonly, 'status unchanged', boundary.source_status_unchanged);
    appendPath(readonly, 'source root', boundary.source_root || '—');
    appendPath(readonly, 'runtime output', boundary.runtime_output_root || '—');
    validationGrid.appendChild(validators);
    validationGrid.appendChild(evidence);
    validationGrid.appendChild(readonly);
    validation.appendChild(validationGrid);

    const graphLinks = appendStateSection(stageWorkbenchContent, 'Graph Structure Around This Stage', '直接流入/流出边用于核对整体图结构；它们解释这个环节在全局进展中的位置。');
    const localEdges = [...graph.edges, ...graph.roadmap.edges].filter((edge) => edge.source === detail.stage_id || edge.target === detail.stage_id);
    appendCardList(graphLinks, localEdges, (edge) => {
      const card = stateCard(`${edge.source} → ${edge.target}`, edge.kind === 'backflow' ? 'backflow' : 'graph');
      appendKeyValue(card, 'kind', edge.kind);
      appendKeyValue(card, 'label', edge.label);
      appendStageJump(card, edge.source === detail.stage_id ? edge.target : edge.source);
      return card;
    });
  }

  function relationBlock(title, edges, directionKey) {
    if (!edges.length) return `<section class="detail-section"><h3>${title}</h3><div class="empty-state">没有直接关系。</div></section>`;
    const items = edges.map((edge) => {
      const otherId = edge[directionKey]; const other = nodeById.get(otherId);
      return `<div class="relation-item"><button type="button" data-jump="${otherId}">${otherId}</button> ${edge.kind} · ${edge.label || '无标签'} · ${other ? other.titleZh : ''}</div>`;
    }).join('');
    return `<section class="detail-section"><h3>${title}</h3><div class="relation-list">${items}</div></section>`;
  }
  function renderDetail() {
    const node = nodeById.get(state.selectedId) || nodeById.get('CTRL');
    const allEdges = [...graph.edges, ...graph.roadmap.edges];
    const incoming = allEdges.filter((edge) => edge.target === node.id);
    const outgoing = allEdges.filter((edge) => edge.source === node.id);
    const friendly = friendlyStage(node.id);
    const handoff = friendly.handoff ? `<p class="detail-description detail-handoff">${friendly.handoff}</p>` : '';
    detailContent.innerHTML = `<h2>${stageTitleZh(node)}</h2><div class="detail-id">${node.id} · ${stageTitleEn(node)} · ${node.phase}</div><p class="detail-description">${node.description}</p>${handoff}${detailBlock('输入', node.inputs)}${detailBlock('输出', node.outputs)}${detailBlock('验证器 / 门控', node.validators)}${detailBlock('可能回流目标', node.backflowTargets)}${relationBlock('流入关系', incoming, 'source')}${relationBlock('流出关系', outgoing, 'target')}`;
    detailContent.querySelectorAll('[data-jump]').forEach((button) => button.addEventListener('click', () => selectNode(button.dataset.jump, true)));
  }

  function activeCanvas() { return state.mode === 'graph' ? { canvas: graphCanvas, stage: graphStage, frame: graphFrame, width: graph.meta.canvas.width } : { canvas: roadmapCanvas, stage: roadmapStage, frame: roadmapFrame, width: graph.roadmap.canvas.width }; }
  function applyZoom() {
    const zoom = nonCanvasModes.has(state.mode) ? null : state.zooms[state.mode];
    const targets = [
      { canvas: roadmapCanvas, stage: roadmapStage, width: graph.roadmap.canvas.width, height: graph.roadmap.canvas.height, zoom: state.zooms.roadmap },
      { canvas: graphCanvas, stage: graphStage, width: graph.meta.canvas.width, height: graph.meta.canvas.height, zoom: state.zooms.graph },
    ];
    targets.forEach(({ canvas, stage, width, height, zoom: z }) => {
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      canvas.style.transform = `scale(${z})`;
      stage.style.width = `${width * z}px`;
      stage.style.height = `${height * z}px`;
    });
    document.getElementById('zoomLabel').textContent = zoom === null ? 'state' : `${Math.round(zoom * 100)}%`;
  }

  function updateCards(selector) {
    const selectedRelated = relatedNodeIds(state.selectedId);
    const hasFocus = state.focusSet && state.focusSet.size && state.activePreset !== 'all';
    document.querySelectorAll(selector).forEach((element) => {
      const id = element.dataset.id; const node = nodeById.get(id);
      const matchesSearch = textIncludes(node, state.query); const inFocus = state.focusSet.has(id); const related = selectedRelated.has(id);
      element.classList.toggle('is-selected', id === state.selectedId);
      element.classList.toggle('is-in-focus', inFocus && hasFocus);
      element.classList.toggle('is-dimmed', hasFocus ? !inFocus : false);
      element.classList.toggle('is-search-miss', !matchesSearch);
      element.classList.toggle('is-related-card', related && id !== state.selectedId);
    });
  }
  function isGroupedRoadmapEdge(element) {
    if (state.mode !== 'roadmap' || !element.classList.contains('roadmap-edge')) return false;
    return roadmapFocusGroups.some((group) => group.nodes.has(state.selectedId) && group.edges.has(element.id));
  }
  function updateEdges(selector) {
    document.querySelectorAll(selector).forEach((element) => {
      const kind = element.dataset.kind; const source = element.dataset.source; const target = element.dataset.target;
      const visibleByKind = state.mode === 'roadmap' && kind === 'dispatch' ? true : state.visibleKinds.has(kind);
      const related = source === state.selectedId || target === state.selectedId;
      const inFocus = state.focusSet.has(source) && state.focusSet.has(target);
      const hasFocus = state.focusSet && state.focusSet.size && state.activePreset !== 'all';
      const localOnly = state.mode === 'roadmap' && element.classList.contains('roadmap-edge');
      const focusEdge = localOnly && hasFocus && inFocus;
      const groupedEdge = isGroupedRoadmapEdge(element);
      const emphasized = related || focusEdge || groupedEdge;
      element.style.display = visibleByKind && (!localOnly || emphasized) ? '' : 'none';
      element.classList.toggle('is-related', emphasized);
      element.classList.toggle('is-focus-edge', focusEdge || groupedEdge);
      element.classList.toggle('is-dimmed', hasFocus ? !inFocus && !groupedEdge : false);
    });
  }
  function update() {
    updateCards('.node-card');
    document.querySelectorAll('.index-button').forEach((element) => {
      const id = element.dataset.id; const node = nodeById.get(id);
      element.classList.toggle('is-active', id === state.selectedId); element.classList.toggle('is-hidden', !textIncludes(node, state.query));
    });
    updateEdges('.edge-path, .edge-label, .edge-port');
    document.querySelectorAll('[data-preset]').forEach((button) => button.classList.toggle('is-active', button.dataset.preset === state.activePreset));
    document.getElementById('roadmapMode').classList.toggle('is-active', state.mode === 'roadmap');
    document.getElementById('graphMode').classList.toggle('is-active', state.mode === 'graph');
    document.getElementById('stageWorkbenchMode').classList.toggle('is-active', state.mode === 'workbench');
    document.getElementById('runtimeStateMode').classList.toggle('is-active', state.mode === 'state');
    document.getElementById('stageCoverageMode').classList.toggle('is-active', state.mode === 'coverage');
    roadmapFrame.classList.toggle('is-hidden', state.mode !== 'roadmap');
    graphFrame.classList.toggle('is-hidden', state.mode !== 'graph');
    stageWorkbenchFrame.classList.toggle('is-hidden', state.mode !== 'workbench');
    runtimeStateFrame.classList.toggle('is-hidden', state.mode !== 'state');
    stageCoverageFrame.classList.toggle('is-hidden', state.mode !== 'coverage');
    document.getElementById('roadmapGuide').classList.toggle('is-hidden', state.mode !== 'roadmap');
    if (state.mode === 'workbench') renderStageWorkbench();
    renderDetail(); applyZoom();
  }
  function selectNode(id, scrollIntoView = false) {
    if (!nodeById.has(id)) return;
    state.selectedId = id;
    const preset = graph.presets.find((item) => item.id === state.activePreset);
    if (preset) { const index = preset.nodes.indexOf(id); if (index >= 0) state.stepIndex = index; }
    update();
    if (scrollIntoView) {
      const selector = state.mode === 'roadmap' ? `#roadmapNodeLayer .node-card[data-id="${CSS.escape(id)}"]` : `#nodeLayer .node-card[data-id="${CSS.escape(id)}"]`;
      const element = document.querySelector(selector);
      if (element) element.scrollIntoView({ block: 'center', inline: 'center', behavior: 'smooth' });
    }
  }
  function activatePreset(id) {
    const preset = graph.presets.find((item) => item.id === id) || graph.presets[0];
    state.activePreset = preset.id; state.focusSet = new Set(preset.nodes); state.stepIndex = 0; selectNode(preset.nodes[0], true);
  }
  function moveStep(delta) {
    const preset = graph.presets.find((item) => item.id === state.activePreset) || graph.presets[0];
    state.stepIndex = (state.stepIndex + delta + preset.nodes.length) % preset.nodes.length; selectNode(preset.nodes[state.stepIndex], true);
  }
  function bindControls() {
    document.getElementById('searchInput').addEventListener('input', (event) => { state.query = event.target.value.trim(); update(); });
    document.getElementById('prevStep').addEventListener('click', () => moveStep(-1));
    document.getElementById('nextStep').addEventListener('click', () => moveStep(1));
    document.getElementById('resetFocus').addEventListener('click', () => activatePreset('all'));
    document.getElementById('showReference').addEventListener('click', () => { referenceFigure.hidden = !referenceFigure.hidden; });
    document.getElementById('roadmapMode').addEventListener('click', () => { state.mode = 'roadmap'; update(); });
    document.getElementById('graphMode').addEventListener('click', () => { state.mode = 'graph'; update(); });
    document.getElementById('stageWorkbenchMode').addEventListener('click', () => { ensureStageSelection(); state.mode = 'workbench'; update(); });
    document.getElementById('runtimeStateMode').addEventListener('click', () => { state.mode = 'state'; update(); });
    document.getElementById('stageCoverageMode').addEventListener('click', () => { state.mode = 'coverage'; update(); });
    document.getElementById('workbenchOpenGraph').addEventListener('click', () => { state.mode = 'roadmap'; update(); selectNode(state.selectedId, true); });
    document.getElementById('fitWidth').addEventListener('click', () => { if (nonCanvasModes.has(state.mode)) return; const active = activeCanvas(); state.zooms[state.mode] = Math.max(0.32, Math.min(1.25, Number(((active.frame.clientWidth - 32) / active.width).toFixed(2)))); applyZoom(); });
    document.getElementById('zoomOut').addEventListener('click', () => { if (nonCanvasModes.has(state.mode)) return; state.zooms[state.mode] = Math.max(0.32, Number((state.zooms[state.mode] - 0.1).toFixed(2))); applyZoom(); });
    document.getElementById('zoomIn').addEventListener('click', () => { if (nonCanvasModes.has(state.mode)) return; state.zooms[state.mode] = Math.min(1.25, Number((state.zooms[state.mode] + 0.1).toFixed(2))); applyZoom(); });
    document.querySelectorAll('[data-guide-jump]').forEach((button) => button.addEventListener('click', () => selectNode(button.dataset.guideJump, true)));
    document.querySelectorAll('[data-guide-preset]').forEach((button) => button.addEventListener('click', () => activatePreset(button.dataset.guidePreset)));
  }

  renderLanes(laneLayer, graph.layers || []); renderGraphNodes(); renderGraphEdges();
  renderLanes(roadmapLaneLayer, graph.roadmap.lanes || []); renderRoadmapNodes(); renderRoadmapEdges();
  renderRuntimeState(); renderStageCoverage(); renderStageWorkbench(); renderIndex(); renderPresets(); renderFilters(); bindControls(); applyZoom(); update();
})();
