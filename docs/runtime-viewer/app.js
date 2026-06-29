(function initRuntimeViewer() {
  const graph = window.PPG_RUNTIME_GRAPH;
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));
  const routeById = new Map((graph.roadmap.nodes || []).map((node) => [node.id, node]));
  const edgeKinds = Object.keys(graph.legend);
  const kindColors = {
    material: 'var(--material)', dispatch: 'var(--dispatch)', validation: 'var(--validation)',
    graph: 'var(--graph)', backflow: 'var(--backflow)', governance: 'var(--governance)', control: 'var(--governance)',
  };
  const primaryRoadmapEdges = new Set(['r-01','r-02','r-03','r-04','r-05','r-06','r-07','r-08','r-09','r-10','r-11','r-12','r-13','r-14','r-15']);
  const ROADMAP_FLOW_RAIL_X = 150;
  const GRAPH_FLOW_RAIL_X = 160;
  const state = {
    mode: 'roadmap', selectedId: 'S00', query: '',
    zooms: { roadmap: 0.72, graph: 0.62 },
    visibleKinds: new Set(graph.defaultVisibleKinds || edgeKinds),
    activePreset: 'all', focusSet: new Set(graph.presets.find((preset) => preset.id === 'all').nodes), stepIndex: 1,
  };

  const laneLayer = document.getElementById('laneLayer');
  const nodeLayer = document.getElementById('nodeLayer');
  const edgeLayer = document.getElementById('edgeLayer');
  const graphCanvas = document.getElementById('graphCanvas');
  const graphFrame = document.getElementById('canvasFrame');
  const roadmapLaneLayer = document.getElementById('roadmapLaneLayer');
  const roadmapNodeLayer = document.getElementById('roadmapNodeLayer');
  const roadmapEdgeLayer = document.getElementById('roadmapEdgeLayer');
  const roadmapCanvas = document.getElementById('roadmapCanvas');
  const roadmapFrame = document.getElementById('roadmapFrame');
  const detailContent = document.getElementById('detailContent');
  const nodeIndex = document.getElementById('nodeIndex');
  const presetButtons = document.getElementById('presetButtons');
  const edgeFilters = document.getElementById('edgeFilters');
  const referenceFigure = document.getElementById('referenceFigure');

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
      button.innerHTML = `<span class="id">${node.id}</span><span>${node.titleZh.replace(/^S\d+\s+/, '')}</span>`;
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

  function inferAnchor(source, target) {
    const dx = (target.x + target.w / 2) - (source.x + source.w / 2);
    const dy = (target.y + target.h / 2) - (source.y + source.h / 2);
    if (Math.abs(dx) > Math.abs(dy)) return dx >= 0 ? 'right' : 'left';
    return dy >= 0 ? 'bottom' : 'top';
  }
  function anchorPoint(box, target, anchor) {
    const side = anchor || inferAnchor(box, target);
    const midX = box.x + box.w / 2; const midY = box.y + box.h / 2;
    if (side === 'left') return { x: box.x, y: midY };
    if (side === 'right') return { x: box.x + box.w, y: midY };
    if (side === 'top') return { x: midX, y: box.y };
    if (side === 'bottom') return { x: midX, y: box.y + box.h };
    return { x: midX, y: midY };
  }
  function railFlowPath(edge, boxById, railX) {
    const source = boxById.get(edge.source);
    const target = boxById.get(edge.target);
    const sourceX = source.x + source.w / 2;
    const sourceY = source.y + source.h;
    const targetX = target.x + target.w / 2;
    const targetY = target.y;
    const spread = (Math.abs(hashId(edge.id)) % 5) * 4;
    const exitY = sourceY + 18 + spread;
    const entryY = targetY - 18 - spread;
    return `M ${sourceX} ${sourceY} V ${exitY} H ${railX} V ${entryY} H ${targetX} V ${targetY}`;
  }
  function edgePath(edge, boxById, canvasWidth, modeClass) {
    const railX = modeClass === 'roadmap-edge' ? ROADMAP_FLOW_RAIL_X : GRAPH_FLOW_RAIL_X;
    return railFlowPath(edge, boxById, railX);
  }
  function labelPoint(edge, boxById, modeClass) {
    const source = boxById.get(edge.source); const target = boxById.get(edge.target);
    const railX = modeClass === 'roadmap-edge' ? ROADMAP_FLOW_RAIL_X : GRAPH_FLOW_RAIL_X;
    return { x: railX + 12, y: Math.round((source.y + source.h + target.y) / 2) - 4 };
  }
  function hashId(value) {
    return [...value].reduce((total, char) => total + char.charCodeAt(0), 0);
  }
  function renderEdgeSet(svg, edges, boxById, canvasWidth, modeClass) {
    svg.innerHTML = '';
    edges.forEach((edge) => {
      const kind = edgeKinds.includes(edge.kind) ? edge.kind : 'governance';
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('id', edge.id); path.setAttribute('class', `edge-path ${modeClass} kind-${kind}${primaryRoadmapEdges.has(edge.id) ? ' primary-edge' : ''}`);
      path.setAttribute('d', edgePath(edge, boxById, canvasWidth, modeClass)); path.setAttribute('stroke', kindColors[kind]);
      path.dataset.kind = kind; path.dataset.source = edge.source; path.dataset.target = edge.target;
      svg.appendChild(path);
      if (edge.label) {
        const point = labelPoint(edge, boxById, modeClass);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('class', `edge-label ${modeClass}${primaryRoadmapEdges.has(edge.id) ? ' primary-edge' : ''}`); text.setAttribute('x', point.x); text.setAttribute('y', point.y);
        text.textContent = modeClass === 'roadmap-edge' && primaryRoadmapEdges.has(edge.id) ? `→ ${edge.label}` : (modeClass === 'roadmap-edge' && kind === 'backflow' ? `↩ ${edge.label}` : edge.label); text.dataset.kind = kind; text.dataset.source = edge.source; text.dataset.target = edge.target;
        svg.appendChild(text);
      }
    });
  }
  function renderGraphEdges() {
    const boxById = new Map(graph.nodes.map((node) => [node.id, node]));
    renderEdgeSet(edgeLayer, graph.edges, boxById, graph.meta.canvas.width, 'graph-edge');
  }
  function renderRoadmapEdges() {
    renderEdgeSet(roadmapEdgeLayer, graph.roadmap.edges, routeById, graph.roadmap.canvas.width, 'roadmap-edge');
  }

  function relatedNodeIds(id) {
    const related = new Set([id]);
    [...graph.edges, ...graph.roadmap.edges].forEach((edge) => { if (edge.source === id) related.add(edge.target); if (edge.target === id) related.add(edge.source); });
    return related;
  }
  function detailBlock(title, items) { return `<section class="detail-section"><h3>${title}</h3><div class="chip-list">${items.map((item) => `<span class="chip">${item}</span>`).join('')}</div></section>`; }
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

  function activeCanvas() { return state.mode === 'roadmap' ? { canvas: roadmapCanvas, frame: roadmapFrame, width: graph.roadmap.canvas.width } : { canvas: graphCanvas, frame: graphFrame, width: graph.meta.canvas.width }; }
  function applyZoom() {
    const zoom = state.zooms[state.mode];
    const targets = [{ canvas: roadmapCanvas, width: graph.roadmap.canvas.width, height: graph.roadmap.canvas.height, zoom: state.zooms.roadmap }, { canvas: graphCanvas, width: graph.meta.canvas.width, height: graph.meta.canvas.height, zoom: state.zooms.graph }];
    targets.forEach(({ canvas, width, height, zoom: z }) => { canvas.style.transform = `scale(${z})`; canvas.style.width = `${width * z}px`; canvas.style.height = `${height * z}px`; });
    document.getElementById('zoomLabel').textContent = `${Math.round(zoom * 100)}%`;
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
  function updateEdges(selector) {
    document.querySelectorAll(selector).forEach((element) => {
      const kind = element.dataset.kind; const source = element.dataset.source; const target = element.dataset.target;
      const visibleByKind = state.mode === 'roadmap' && kind === 'dispatch' ? true : state.visibleKinds.has(kind);
      const related = source === state.selectedId || target === state.selectedId;
      const inFocus = state.focusSet.has(source) && state.focusSet.has(target);
      const hasFocus = state.focusSet && state.focusSet.size && state.activePreset !== 'all';
      const localOnly = state.mode === 'roadmap' && element.classList.contains('roadmap-edge');
      element.style.display = visibleByKind && (!localOnly || related) ? '' : 'none';
      element.classList.toggle('is-related', related);
      element.classList.toggle('is-dimmed', hasFocus ? !inFocus : false);
    });
  }
  function update() {
    updateCards('.node-card');
    document.querySelectorAll('.index-button').forEach((element) => {
      const id = element.dataset.id; const node = nodeById.get(id);
      element.classList.toggle('is-active', id === state.selectedId); element.classList.toggle('is-hidden', !textIncludes(node, state.query));
    });
    updateEdges('.edge-path, .edge-label');
    document.querySelectorAll('[data-preset]').forEach((button) => button.classList.toggle('is-active', button.dataset.preset === state.activePreset));
    document.getElementById('roadmapMode').classList.toggle('is-active', state.mode === 'roadmap');
    document.getElementById('graphMode').classList.toggle('is-active', state.mode === 'graph');
    roadmapFrame.classList.toggle('is-hidden', state.mode !== 'roadmap');
    graphFrame.classList.toggle('is-hidden', state.mode !== 'graph');
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
    document.getElementById('fitWidth').addEventListener('click', () => { const active = activeCanvas(); state.zooms[state.mode] = Math.max(0.32, Math.min(1.25, Number(((active.frame.clientWidth - 32) / active.width).toFixed(2)))); applyZoom(); });
    document.getElementById('zoomOut').addEventListener('click', () => { state.zooms[state.mode] = Math.max(0.32, Number((state.zooms[state.mode] - 0.1).toFixed(2))); applyZoom(); });
    document.getElementById('zoomIn').addEventListener('click', () => { state.zooms[state.mode] = Math.min(1.25, Number((state.zooms[state.mode] + 0.1).toFixed(2))); applyZoom(); });
    document.querySelectorAll('[data-guide-jump]').forEach((button) => button.addEventListener('click', () => selectNode(button.dataset.guideJump, true)));
  }

  renderLanes(laneLayer, graph.layers || []); renderGraphNodes(); renderGraphEdges();
  renderLanes(roadmapLaneLayer, graph.roadmap.lanes || []); renderRoadmapNodes(); renderRoadmapEdges();
  renderIndex(); renderPresets(); renderFilters(); bindControls(); applyZoom(); update();
})();
