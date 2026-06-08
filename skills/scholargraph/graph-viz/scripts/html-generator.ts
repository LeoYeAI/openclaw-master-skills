/**
 * @module graph-viz/html-generator
 * @description 生成交互式知识图谱 HTML（D3.js v7 力导向布局）
 *
 * 特性：
 * - D3.js v7 从 CDN 加载
 * - 力导向布局：forceLink / forceManyBody / forceCollide / forceCenter
 * - 缩放平移（d3.zoom）、节点拖拽（d3.drag）
 * - 点击节点：右侧面板显示详情 + 关联论文
 * - 悬停 tooltip、搜索栏、图例
 * - 可选嵌入论文数据，支持"查看演示"功能
 */

import type {
  D3GraphData,
  D3GraphNode,
  D3GraphEdge,
  GraphHtmlOptions,
  PaperPayload,
} from './types';
import { CATEGORY_COLORS, RELATION_STYLES } from './types';

/**
 * 生成交互式图谱 HTML
 * @param data - D3 图谱数据
 * @param options - HTML 生成选项
 * @returns 完整 HTML 字符串
 */
export function generateGraphHtml(data: D3GraphData, options?: GraphHtmlOptions): string {
  const opts: Required<GraphHtmlOptions> = {
    includePaperData: options?.includePaperData ?? true,
    paperPayload: options?.paperPayload ?? {},
    width: options?.width ?? 1200,
    height: options?.height ?? 800,
  };

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(data.metadata.name)} — Knowledge Graph</title>
<style>
${generateCSS()}
</style>
</head>
<body>
<div class="app">
  <header class="toolbar">
    <h1 class="graph-title">${escapeHtml(data.metadata.name)}</h1>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="Search nodes..." autocomplete="off">
      <span class="search-icon">&#128269;</span>
    </div>
    <div class="stats">
      <span>${data.metadata.totalNodes} nodes</span>
      <span>${data.metadata.totalEdges} edges</span>
      <span>${data.metadata.totalPapers} papers</span>
    </div>
  </header>
  <div class="main">
    <div class="graph-container" id="graphContainer">
      <svg id="graphSvg"></svg>
    </div>
    <aside class="panel" id="panel">
      <div class="panel-placeholder">
        <p>Click a node to see details</p>
      </div>
      <div class="panel-content" id="panelContent" style="display:none"></div>
    </aside>
  </div>
  <div class="legend" id="legend">
    <div class="legend-title">Categories</div>
    ${Object.entries(CATEGORY_COLORS)
      .map(([cat, color]) => `<div class="legend-item"><span class="legend-dot" style="background:${color}"></span>${cat}</div>`)
      .join('\n    ')}
    <div class="legend-title" style="margin-top:8px">Node Size = Paper Count</div>
    <div class="legend-title">Relations</div>
    ${Object.entries(RELATION_STYLES)
      .map(([rel, s]) => `<div class="legend-item"><span class="legend-line" style="background:${s.color};${s.dasharray ? 'border-style:dashed' : ''}"></span>${rel}</div>`)
      .join('\n    ')}
  </div>
  <div class="tooltip" id="tooltip"></div>
</div>
<script src="https://d3js.org/d3.v7.min.js"><\/script>
<script>
const GRAPH_DATA = ${JSON.stringify({ nodes: data.nodes, edges: data.edges })};
const PAPER_DATA = ${JSON.stringify(opts.paperPayload)};
const INCLUDE_PAPERS = ${opts.includePaperData};
${generateJS(opts)}
<\/script>
</body>
</html>`;
}

/** 生成 CSS */
function generateCSS(): string {
  return `
:root {
  --bg: #0F172A;
  --surface: #1E293B;
  --surface-hover: #334155;
  --text: #F1F5F9;
  --text-secondary: #94A3B8;
  --primary: #60A5FA;
  --accent: #F59E0B;
  --border: rgba(255,255,255,0.08);
  --radius: 10px;
  --panel-width: 360px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  overflow: hidden;
  height: 100vh;
}

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* === Toolbar === */
.toolbar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}
.graph-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary);
  white-space: nowrap;
}
.search-box {
  position: relative;
  flex: 0 1 280px;
}
.search-box input {
  width: 100%;
  padding: 0.45rem 0.75rem 0.45rem 2rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}
.search-box input:focus { border-color: var(--primary); }
.search-icon {
  position: absolute;
  left: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  opacity: 0.5;
}
.stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-left: auto;
}
.stats span {
  background: var(--bg);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

/* === Main Layout === */
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.graph-container {
  flex: 1;
  position: relative;
}
#graphSvg {
  width: 100%;
  height: 100%;
  cursor: grab;
}
#graphSvg:active { cursor: grabbing; }

/* === Side Panel === */
.panel {
  width: var(--panel-width);
  background: var(--surface);
  border-left: 1px solid var(--border);
  overflow-y: auto;
  transition: transform 0.3s;
  padding: 1.2rem;
}
.panel-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.panel-node-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}
.panel-node-label {
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.3;
}
.panel-category {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.panel-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}
.panel-section-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 1rem 0 0.5rem;
}

/* Paper list */
.paper-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  transition: border-color 0.2s;
  cursor: default;
}
.paper-card:hover { border-color: var(--primary); }
.paper-title {
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 0.3rem;
}
.paper-authors {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
}
.paper-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.7rem;
  color: var(--text-secondary);
}
.paper-meta span {
  background: var(--surface);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
}
.paper-actions {
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
}
.btn-sm {
  padding: 0.25rem 0.6rem;
  font-size: 0.72rem;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}
.btn-sm:hover { background: var(--primary); color: var(--bg); border-color: var(--primary); }
.btn-primary { background: var(--primary); color: var(--bg); border-color: var(--primary); }
.btn-primary:hover { opacity: 0.85; }

/* === Legend === */
.legend {
  position: fixed;
  bottom: 1rem;
  left: 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem;
  font-size: 0.75rem;
  z-index: 10;
  max-width: 180px;
}
.legend-title {
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
  font-size: 0.7rem;
  text-transform: uppercase;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.15rem 0;
  color: var(--text-secondary);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-line {
  width: 18px;
  height: 3px;
  border-radius: 2px;
  flex-shrink: 0;
}

/* === Tooltip === */
.tooltip {
  position: fixed;
  padding: 0.5rem 0.75rem;
  background: rgba(15,23,42,0.95);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--text);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
  z-index: 100;
  max-width: 250px;
}
.tooltip.visible { opacity: 1; }
.tooltip-label { font-weight: 600; }
.tooltip-count { color: var(--text-secondary); font-size: 0.7rem; }

/* Node highlight */
.node-dimmed circle { opacity: 0.15; }
.node-dimmed text { opacity: 0.15; }
.edge-dimmed { opacity: 0.05 !important; }
.node-highlight circle { filter: drop-shadow(0 0 8px currentColor); }

/* Search highlight */
.node-search-match circle { stroke: var(--accent); stroke-width: 3px; }

@media (max-width: 768px) {
  .panel { width: 100%; position: fixed; bottom: 0; left: 0; height: 50vh; border-left: none; border-top: 1px solid var(--border); transform: translateY(100%); z-index: 20; }
  .panel.open { transform: translateY(0); }
  .legend { display: none; }
  .stats { display: none; }
}
`;
}

/** 生成交互 JS */
function generateJS(opts: Required<GraphHtmlOptions>): string {
  return `
(function() {
  'use strict';

  var nodes = GRAPH_DATA.nodes;
  var edges = GRAPH_DATA.edges;

  var container = document.getElementById('graphContainer');
  var svg = d3.select('#graphSvg');
  var width = container.clientWidth;
  var height = container.clientHeight;

  svg.attr('viewBox', [0, 0, width, height]);

  // === Zoom ===
  var g = svg.append('g').attr('class', 'graph-root');
  var zoom = d3.zoom()
    .scaleExtent([0.1, 5])
    .on('zoom', function(event) {
      g.attr('transform', event.transform);
    });
  svg.call(zoom);

  // === Arrow markers ===
  svg.append('defs').selectAll('marker')
    .data(['prerequisite', 'derived', 'component', 'related'])
    .join('marker')
    .attr('id', function(d) { return 'arrow-' + d; })
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 20)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#78909C');

  // === Edges ===
  var edgeGroup = g.append('g').attr('class', 'edges');
  var edgeEls = edgeGroup.selectAll('line')
    .data(edges)
    .join('line')
    .attr('stroke', function(d) { return d.style.color; })
    .attr('stroke-width', function(d) { return d.strokeWidth; })
    .attr('stroke-opacity', function(d) { return d.style.opacity; })
    .attr('stroke-dasharray', function(d) { return d.style.dasharray; })
    .attr('marker-end', function(d) { return 'url(#arrow-' + d.relation + ')'; });

  // === Nodes ===
  var nodeGroup = g.append('g').attr('class', 'nodes');
  var nodeEls = nodeGroup.selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .style('cursor', 'pointer');

  nodeEls.append('circle')
    .attr('r', function(d) { return d.radius; })
    .attr('fill', function(d) { return d.color; })
    .attr('stroke', 'rgba(255,255,255,0.1)')
    .attr('stroke-width', 1.5);

  nodeEls.append('text')
    .text(function(d) { return d.label; })
    .attr('text-anchor', 'middle')
    .attr('dy', function(d) { return d.radius + 14; })
    .attr('fill', '#94A3B8')
    .attr('font-size', function(d) { return Math.max(10, Math.min(d.radius * 0.45, 14)) + 'px'; })
    .attr('font-weight', '500')
    .attr('pointer-events', 'none');

  // === Drag ===
  var drag = d3.drag()
    .on('start', function(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    })
    .on('drag', function(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    })
    .on('end', function(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    });
  nodeEls.call(drag);

  // === Force Simulation ===
  var simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges)
      .id(function(d) { return d.id; })
      .distance(function(d) { return 120 - d.strokeWidth * 5; })
    )
    .force('charge', d3.forceManyBody()
      .strength(function(d) { return -200 - d.radius * 5; })
    )
    .force('collide', d3.forceCollide()
      .radius(function(d) { return d.radius + 8; })
    )
    .force('center', d3.forceCenter(width / 2, height / 2))
    .on('tick', ticked);

  function ticked() {
    edgeEls
      .attr('x1', function(d) { return d.source.x; })
      .attr('y1', function(d) { return d.source.y; })
      .attr('x2', function(d) { return d.target.x; })
      .attr('y2', function(d) { return d.target.y; });
    nodeEls.attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });
  }

  // === Tooltip ===
  var tooltip = document.getElementById('tooltip');
  nodeEls.on('mouseenter', function(event, d) {
    tooltip.innerHTML = '<div class="tooltip-label">' + escHtml(d.label) + '</div>' +
      '<div class="tooltip-count">' + d.paperCount + ' papers · importance ' + d.importance + '</div>';
    tooltip.classList.add('visible');
  }).on('mousemove', function(event) {
    tooltip.style.left = (event.clientX + 12) + 'px';
    tooltip.style.top = (event.clientY - 10) + 'px';
  }).on('mouseleave', function() {
    tooltip.classList.remove('visible');
  });

  // === Click → Panel ===
  var selectedNode = null;
  var panel = document.getElementById('panel');
  var panelContent = document.getElementById('panelContent');
  var panelPlaceholder = panel.querySelector('.panel-placeholder');

  nodeEls.on('click', function(event, d) {
    event.stopPropagation();
    selectedNode = d;
    showPanel(d);
    highlightNode(d);
  });

  svg.on('click', function() {
    selectedNode = null;
    hidePanel();
    clearHighlight();
  });

  function showPanel(d) {
    panelPlaceholder.style.display = 'none';
    panelContent.style.display = 'block';
    panel.classList.add('open');

    var html = '<div class="panel-header">' +
      '<span class="panel-node-dot" style="background:' + d.color + '"></span>' +
      '<div><div class="panel-node-label">' + escHtml(d.label) + '</div>' +
      '<span class="panel-category" style="background:' + d.color + '22;color:' + d.color + '">' + d.category + '</span>' +
      '</div></div>';

    if (d.description) {
      html += '<p class="panel-desc">' + escHtml(d.description) + '</p>';
    }

    html += '<div style="display:flex;gap:0.75rem;flex-wrap:wrap;font-size:0.78rem;color:#94A3B8;margin-bottom:0.75rem">' +
      '<span>Importance: ' + d.importance + '/5</span>' +
      '<span>Papers: ' + d.paperCount + '</span></div>';

    // Connected nodes
    var connected = edges.filter(function(e) {
      var sid = typeof e.source === 'object' ? e.source.id : e.source;
      var tid = typeof e.target === 'object' ? e.target.id : e.target;
      return sid === d.id || tid === d.id;
    });

    if (connected.length > 0) {
      html += '<div class="panel-section-title">Connections (' + connected.length + ')</div>';
      connected.forEach(function(e) {
        var sid = typeof e.source === 'object' ? e.source.id : e.source;
        var tid = typeof e.target === 'object' ? e.target.id : e.target;
        var otherId = sid === d.id ? tid : sid;
        var other = nodes.find(function(n) { return n.id === otherId; });
        if (other) {
          var dir = sid === d.id ? ' → ' : ' ← ';
          html += '<div class="legend-item" style="padding:0.2rem 0"><span class="legend-dot" style="background:' +
            other.color + '"></span>' + dir + escHtml(other.label) +
            ' <span style="color:#64748B;font-size:0.7rem">(' + e.relation + ')</span></div>';
        }
      });
    }

    // Papers
    if (INCLUDE_PAPERS && PAPER_DATA[d.id] && PAPER_DATA[d.id].length > 0) {
      var papers = PAPER_DATA[d.id];
      html += '<div class="panel-section-title">Related Papers (' + papers.length + ')</div>';
      papers.forEach(function(p) {
        html += '<div class="paper-card">' +
          '<div class="paper-title">' + escHtml(p.title) + '</div>' +
          '<div class="paper-authors">' + escHtml(p.authors.slice(0, 3).join(', ')) + (p.authors.length > 3 ? ' et al.' : '') + '</div>' +
          '<div class="paper-meta">' +
          (p.citations != null ? '<span>' + p.citations + ' citations</span>' : '') +
          '<span>relevance: ' + (p.relevance * 100).toFixed(0) + '%</span>' +
          '<span>' + p.mentionType + '</span></div>' +
          '<div class="paper-actions">';

        if (p.url) {
          html += '<a class="btn-sm" href="' + escHtml(p.url) + '" target="_blank">Open Paper</a>';
        }
        html += '<button class="btn-sm btn-primary" onclick="openPaperPreview(\\'' + escapeForJs(p.id) + '\\')">View Presentation</button>';
        html += '</div></div>';
      });
    } else if (d.paperCount > 0) {
      html += '<div class="panel-section-title">Papers</div>';
      html += '<p class="panel-desc">' + d.paperCount + ' papers associated. Run full analysis for details.</p>';
    }

    panelContent.innerHTML = html;
  }

  function hidePanel() {
    panelPlaceholder.style.display = 'flex';
    panelContent.style.display = 'none';
    panel.classList.remove('open');
  }

  // === Highlight ===
  function highlightNode(d) {
    var connectedIds = new Set();
    connectedIds.add(d.id);
    edges.forEach(function(e) {
      var sid = typeof e.source === 'object' ? e.source.id : e.source;
      var tid = typeof e.target === 'object' ? e.target.id : e.target;
      if (sid === d.id) connectedIds.add(tid);
      if (tid === d.id) connectedIds.add(sid);
    });

    nodeEls.classed('node-dimmed', function(n) { return !connectedIds.has(n.id); });
    nodeEls.classed('node-highlight', function(n) { return n.id === d.id; });
    edgeEls.classed('edge-dimmed', function(e) {
      var sid = typeof e.source === 'object' ? e.source.id : e.source;
      var tid = typeof e.target === 'object' ? e.target.id : e.target;
      return !connectedIds.has(sid) || !connectedIds.has(tid);
    });
  }

  function clearHighlight() {
    nodeEls.classed('node-dimmed', false).classed('node-highlight', false);
    edgeEls.classed('edge-dimmed', false);
  }

  // === Search ===
  var searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', function() {
    var q = this.value.trim().toLowerCase();
    nodeEls.classed('node-search-match', function(d) {
      return q && d.label.toLowerCase().includes(q);
    });
    if (q) {
      var match = nodes.find(function(n) { return n.label.toLowerCase().includes(q); });
      if (match && match.x != null) {
        var t = d3.zoomIdentity.translate(width/2 - match.x, height/2 - match.y);
        svg.transition().duration(500).call(zoom.transform, t);
      }
    } else {
      nodeEls.classed('node-search-match', false);
    }
  });

  // === Paper Preview (client-side mini presentation) ===
  window.openPaperPreview = function(paperId) {
    if (!PAPER_DATA) return;
    var paper = null;
    for (var nid in PAPER_DATA) {
      var found = PAPER_DATA[nid].find(function(p) { return p.id === paperId; });
      if (found) { paper = found; break; }
    }
    if (!paper) return;

    // Build minimal presentation HTML
    var html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>' + escHtml(paper.title) +
      '</title><style>' +
      'body{margin:0;font-family:Inter,system-ui,sans-serif;background:#0F172A;color:#F1F5F9}' +
      '.slide{min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:4rem 8rem;scroll-snap-align:start}' +
      'h1{font-size:2.5rem;color:#60A5FA;margin-bottom:1rem}' +
      'h2{font-size:1.8rem;color:#60A5FA;margin-bottom:1rem}' +
      '.authors{color:#F59E0B;font-size:1.2rem;margin-bottom:0.5rem}' +
      'p{font-size:1.1rem;line-height:1.8;color:#94A3B8;max-width:900px}' +
      '.meta{font-size:0.9rem;color:#64748B;margin-top:1rem}' +
      'html{scroll-snap-type:y mandatory;scrollbar-width:none}' +
      '</style></head><body>' +
      '<section class="slide" style="text-align:center;align-items:center">' +
      '<h1>' + escHtml(paper.title) + '</h1>' +
      '<div class="authors">' + escHtml(paper.authors.join(', ')) + '</div>' +
      (paper.url ? '<div class="meta"><a href="' + escHtml(paper.url) + '" style="color:#60A5FA" target="_blank">View Paper</a></div>' : '') +
      '</section>' +
      '<section class="slide"><h2>Abstract</h2><p>' + escHtml(paper.abstract) + '</p></section>' +
      '</body></html>';

    var blob = new Blob([html], {type: 'text/html'});
    var url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  // === Resize ===
  window.addEventListener('resize', function() {
    width = container.clientWidth;
    height = container.clientHeight;
    svg.attr('viewBox', [0, 0, width, height]);
    simulation.force('center', d3.forceCenter(width / 2, height / 2));
    simulation.alpha(0.3).restart();
  });

  function escHtml(s) {
    if (!s) return '';
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function escapeForJs(s) {
    return s.replace(/'/g, "\\\\'").replace(/"/g, '\\\\"');
  }
})();
`;
}

/** HTML 转义（构建时） */
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
