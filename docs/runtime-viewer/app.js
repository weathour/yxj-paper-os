(function initRuntimeViewer() {
  const graph = window.PPG_RUNTIME_GRAPH;
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));
  const edgeKinds = Object.keys(graph.legend);
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
      return `<div class="node-head"><span class="node-id">${node.id}</span><span class="node-phase">${node.phase}</span></div><div><div class="node-title">${node.titleZh}</div></div><div class="io-preview"><span><strong>OUT</strong>${truncate(node.outputs.slice(0, 2).join('；'), 44)}</span></div>`;
    }
    return `<div class="node-head"><span class="node-id">${node.id}</span><span class="node-phase">${node.phase}</span></div><div><div class="node-title">${node.titleZh}</div><div class="node-subtitle">${node.title}</div></div><div class="io-preview"><span><strong>IN</strong>${truncate(node.inputs.join('；'), 48)}</span><span><strong>OUT</strong>${truncate(node.outputs.join('；'), 48)}</span></div>`;
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
      button.innerHTML = `<span class="id">${node.id}</span><span>${node.titleZh.replace(/^S\d+[A-Z]?\s+/, '')}</span>`;
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
    detailContent.innerHTML = `<h2>${node.titleZh}</h2><div class="detail-id">${node.id} · ${node.title} · ${node.phase}</div><p class="detail-description">${node.description}</p>${detailBlock('输入', node.inputs)}${detailBlock('输出', node.outputs)}${detailBlock('验证器 / 门控', node.validators)}${detailBlock('可能回流目标', node.backflowTargets)}${relationBlock('流入关系', incoming, 'source')}${relationBlock('流出关系', outgoing, 'target')}`;
    detailContent.querySelectorAll('[data-jump]').forEach((button) => button.addEventListener('click', () => selectNode(button.dataset.jump, true)));
  }

  function activeCanvas() { return state.mode === 'graph' ? { canvas: graphCanvas, stage: graphStage, frame: graphFrame, width: graph.meta.canvas.width } : { canvas: roadmapCanvas, stage: roadmapStage, frame: roadmapFrame, width: graph.roadmap.canvas.width }; }
  function applyZoom() {
    const zoom = state.mode === 'state' || state.mode === 'coverage' ? null : state.zooms[state.mode];
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
    document.getElementById('runtimeStateMode').classList.toggle('is-active', state.mode === 'state');
    document.getElementById('stageCoverageMode').classList.toggle('is-active', state.mode === 'coverage');
    roadmapFrame.classList.toggle('is-hidden', state.mode !== 'roadmap');
    graphFrame.classList.toggle('is-hidden', state.mode !== 'graph');
    runtimeStateFrame.classList.toggle('is-hidden', state.mode !== 'state');
    stageCoverageFrame.classList.toggle('is-hidden', state.mode !== 'coverage');
    document.getElementById('roadmapGuide').classList.toggle('is-hidden', state.mode !== 'roadmap');
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
    document.getElementById('runtimeStateMode').addEventListener('click', () => { state.mode = 'state'; update(); });
    document.getElementById('stageCoverageMode').addEventListener('click', () => { state.mode = 'coverage'; update(); });
    document.getElementById('fitWidth').addEventListener('click', () => { if (state.mode === 'state' || state.mode === 'coverage') return; const active = activeCanvas(); state.zooms[state.mode] = Math.max(0.32, Math.min(1.25, Number(((active.frame.clientWidth - 32) / active.width).toFixed(2)))); applyZoom(); });
    document.getElementById('zoomOut').addEventListener('click', () => { if (state.mode === 'state' || state.mode === 'coverage') return; state.zooms[state.mode] = Math.max(0.32, Number((state.zooms[state.mode] - 0.1).toFixed(2))); applyZoom(); });
    document.getElementById('zoomIn').addEventListener('click', () => { if (state.mode === 'state' || state.mode === 'coverage') return; state.zooms[state.mode] = Math.min(1.25, Number((state.zooms[state.mode] + 0.1).toFixed(2))); applyZoom(); });
    document.querySelectorAll('[data-guide-jump]').forEach((button) => button.addEventListener('click', () => selectNode(button.dataset.guideJump, true)));
    document.querySelectorAll('[data-guide-preset]').forEach((button) => button.addEventListener('click', () => activatePreset(button.dataset.guidePreset)));
  }

  renderLanes(laneLayer, graph.layers || []); renderGraphNodes(); renderGraphEdges();
  renderLanes(roadmapLaneLayer, graph.roadmap.lanes || []); renderRoadmapNodes(); renderRoadmapEdges();
  renderRuntimeState(); renderStageCoverage(); renderIndex(); renderPresets(); renderFilters(); bindControls(); applyZoom(); update();
})();
