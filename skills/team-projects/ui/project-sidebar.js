/**
 * Team Projects — Project Sidebar UI
 *
 * Right-hand sidebar panel for the OpenClaw Control UI.
 * Shows project list, WBS, task board, and progress tracking.
 *
 * Registers via the plugin UI registry as a custom tab.
 */

// ── Styles ──────────────────────────────────────────────────────────────

const SIDEBAR_CSS = `
  .tp-sidebar {
    display: flex;
    flex-direction: column;
    height: 100%;
    font-family: var(--font-sans, system-ui, sans-serif);
    color: var(--text, #e0e0e0);
    background: var(--bg-secondary, #1a1a2e);
    overflow: hidden;
  }

  .tp-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border, #333);
    flex-shrink: 0;
  }

  .tp-header h2 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .tp-btn {
    background: var(--accent, #6366f1);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  .tp-btn:hover { opacity: 0.85; }
  .tp-btn--sm { padding: 4px 8px; font-size: 11px; }
  .tp-btn--ghost {
    background: transparent;
    color: var(--text-muted, #888);
    border: 1px solid var(--border, #444);
  }
  .tp-btn--ghost:hover { background: var(--bg-hover, #222); }
  .tp-btn--danger { background: #ef4444; }

  .tp-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 12px 16px;
  }

  /* Project List */
  .tp-project-list { list-style: none; padding: 0; margin: 0; }
  .tp-project-item {
    background: var(--bg-tertiary, #232340);
    border: 1px solid var(--border, #333);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.15s;
  }
  .tp-project-item:hover { border-color: var(--accent, #6366f1); }
  .tp-project-item.active { border-color: var(--accent, #6366f1); border-width: 2px; }

  .tp-project-name {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
  }
  .tp-project-meta {
    font-size: 11px;
    color: var(--text-muted, #888);
    display: flex;
    gap: 12px;
    align-items: center;
  }

  /* Progress Bar */
  .tp-progress {
    width: 100%;
    height: 6px;
    background: var(--bg-primary, #111);
    border-radius: 3px;
    margin-top: 8px;
    overflow: hidden;
  }
  .tp-progress-bar {
    height: 100%;
    background: var(--accent, #6366f1);
    border-radius: 3px;
    transition: width 0.3s ease;
  }
  .tp-progress-bar.complete { background: #22c55e; }

  /* Status badges */
  .tp-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .tp-badge--planning { background: #3b82f620; color: #60a5fa; }
  .tp-badge--active { background: #22c55e20; color: #4ade80; }
  .tp-badge--paused { background: #f59e0b20; color: #fbbf24; }
  .tp-badge--completed { background: #22c55e20; color: #22c55e; }
  .tp-badge--todo { background: #64748b20; color: #94a3b8; }
  .tp-badge--in_progress { background: #6366f120; color: #818cf8; }
  .tp-badge--blocked { background: #ef444420; color: #f87171; }
  .tp-badge--review { background: #f59e0b20; color: #fbbf24; }
  .tp-badge--done { background: #22c55e20; color: #22c55e; }

  .tp-badge--critical { background: #ef444430; color: #f87171; }
  .tp-badge--high { background: #f97316 30; color: #fb923c; }
  .tp-badge--medium { background: #3b82f620; color: #60a5fa; }
  .tp-badge--low { background: #64748b20; color: #94a3b8; }

  /* WBS / Phase view */
  .tp-phase {
    margin-bottom: 16px;
  }
  .tp-phase-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted, #aaa);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border, #333);
    margin-bottom: 8px;
  }

  .tp-task {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px;
    border-radius: 6px;
    margin-bottom: 4px;
    background: var(--bg-tertiary, #232340);
    border-left: 3px solid transparent;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.1s;
  }
  .tp-task:hover { background: var(--bg-hover, #2a2a4a); }
  .tp-task--critical { border-left-color: #ef4444; }
  .tp-task--high { border-left-color: #f97316; }
  .tp-task--medium { border-left-color: #3b82f6; }
  .tp-task--low { border-left-color: #64748b; }

  .tp-task-checkbox {
    width: 16px; height: 16px;
    border: 2px solid var(--border, #555);
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 1px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px;
    transition: all 0.15s;
  }
  .tp-task-checkbox.checked {
    background: #22c55e;
    border-color: #22c55e;
    color: white;
  }

  .tp-task-content { flex: 1; min-width: 0; }
  .tp-task-title { font-weight: 500; }
  .tp-task-title.done { text-decoration: line-through; color: var(--text-muted, #666); }
  .tp-task-detail {
    font-size: 11px;
    color: var(--text-muted, #888);
    margin-top: 2px;
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .tp-agent-avatar {
    width: 18px; height: 18px;
    border-radius: 50%;
    background: var(--accent, #6366f1);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
  }

  /* Create Project Modal */
  .tp-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
  }
  .tp-modal {
    background: var(--bg-secondary, #1a1a2e);
    border: 1px solid var(--border, #333);
    border-radius: 12px;
    padding: 24px;
    width: 480px;
    max-width: 90vw;
    max-height: 80vh;
    overflow-y: auto;
  }
  .tp-modal h3 { margin: 0 0 16px 0; font-size: 18px; }

  .tp-field {
    margin-bottom: 12px;
  }
  .tp-field label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted, #888);
    margin-bottom: 4px;
  }
  .tp-field input, .tp-field textarea, .tp-field select {
    width: 100%;
    background: var(--bg-primary, #111);
    border: 1px solid var(--border, #444);
    border-radius: 6px;
    padding: 8px 10px;
    color: var(--text, #e0e0e0);
    font-size: 13px;
    font-family: inherit;
  }
  .tp-field textarea { min-height: 60px; resize: vertical; }

  /* Empty state */
  .tp-empty {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-muted, #666);
  }
  .tp-empty-icon { font-size: 48px; margin-bottom: 12px; }
  .tp-empty-text { font-size: 14px; margin-bottom: 16px; }

  /* Action bar */
  .tp-actions {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid var(--border, #333);
    flex-shrink: 0;
  }

  /* Tabs within project view */
  .tp-tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--border, #333);
    padding: 0 16px;
    flex-shrink: 0;
  }
  .tp-tab {
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted, #888);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
  }
  .tp-tab:hover { color: var(--text, #e0e0e0); }
  .tp-tab.active {
    color: var(--accent, #6366f1);
    border-bottom-color: var(--accent, #6366f1);
  }

  /* Stats grid */
  .tp-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-bottom: 16px;
  }
  .tp-stat {
    background: var(--bg-tertiary, #232340);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
  }
  .tp-stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--accent, #6366f1);
  }
  .tp-stat-label {
    font-size: 11px;
    color: var(--text-muted, #888);
    margin-top: 2px;
  }

  /* Team list */
  .tp-team {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
  }
  .tp-team-member {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-tertiary, #232340);
    border-radius: 16px;
    padding: 4px 10px 4px 4px;
    font-size: 12px;
  }
`;

// ── Component Rendering ─────────────────────────────────────────────────

/**
 * Render the full sidebar HTML.
 * This is called by the plugin view renderer.
 *
 * @param {object} state - { projects, activeProject, activeTab, modal, client }
 * @returns {string} HTML string
 */
export function renderSidebar(state) {
  const { projects = [], activeProject, activeTab = "board", modal } = state;

  let html = `<style>${SIDEBAR_CSS}</style>`;
  html += `<div class="tp-sidebar">`;

  if (modal) {
    html += renderModal(modal, state);
  }

  if (activeProject) {
    html += renderProjectView(activeProject, activeTab, state);
  } else {
    html += renderProjectList(projects, state);
  }

  html += `</div>`;
  return html;
}

function renderProjectList(projects, state) {
  let html = `
    <div class="tp-header">
      <h2>📋 Projects</h2>
      <button class="tp-btn tp-btn--sm" data-action="create-project">+ New</button>
    </div>
    <div class="tp-scroll">
  `;

  if (projects.length === 0) {
    html += `
      <div class="tp-empty">
        <div class="tp-empty-icon">🚀</div>
        <div class="tp-empty-text">No projects yet</div>
        <button class="tp-btn" data-action="create-project">Create Your First Project</button>
      </div>
    `;
  } else {
    html += `<ul class="tp-project-list">`;
    for (const p of projects) {
      const progress = p.taskCount > 0 ? Math.round((p.completedCount / p.taskCount) * 100) : 0;
      html += `
        <li class="tp-project-item" data-action="open-project" data-project-id="${p.id}">
          <div class="tp-project-name">${esc(p.name)}</div>
          <div class="tp-project-meta">
            <span class="tp-badge tp-badge--${p.status}">${p.status}</span>
            <span>${p.completedCount}/${p.taskCount} tasks</span>
            <span>${p.agents?.length || 0} agents</span>
          </div>
          <div class="tp-progress">
            <div class="tp-progress-bar ${progress === 100 ? 'complete' : ''}"
                 style="width: ${progress}%"></div>
          </div>
        </li>
      `;
    }
    html += `</ul>`;
  }

  html += `</div>`;
  return html;
}

function renderProjectView(project, tab, state) {
  const stats = computeStats(project);

  let html = `
    <div class="tp-header">
      <h2>
        <span style="cursor:pointer;opacity:0.6" data-action="back-to-list">←</span>
        ${esc(project.name)}
      </h2>
      <span class="tp-badge tp-badge--${project.status}">${project.status}</span>
    </div>

    <div class="tp-tabs">
      <div class="tp-tab ${tab === 'board' ? 'active' : ''}" data-action="switch-tab" data-tab="board">Board</div>
      <div class="tp-tab ${tab === 'team' ? 'active' : ''}" data-action="switch-tab" data-tab="team">Team</div>
      <div class="tp-tab ${tab === 'stats' ? 'active' : ''}" data-action="switch-tab" data-tab="stats">Stats</div>
    </div>

    <div class="tp-scroll">
  `;

  if (tab === "board") {
    html += renderBoard(project, state);
  } else if (tab === "team") {
    html += renderTeam(project, state);
  } else if (tab === "stats") {
    html += renderStats(project, stats);
  }

  html += `</div>`;

  // Action bar
  html += `
    <div class="tp-actions">
      <button class="tp-btn tp-btn--sm" data-action="add-phase"
              data-project-id="${project.id}">+ Phase</button>
      <button class="tp-btn tp-btn--sm" data-action="dispatch-ready"
              data-project-id="${project.id}">🚀 Dispatch</button>
      <button class="tp-btn tp-btn--sm tp-btn--ghost" data-action="refresh">↻ Refresh</button>
    </div>
  `;

  return html;
}

function renderBoard(project, state) {
  let html = "";
  const phases = project.phases || [];

  if (phases.length === 0) {
    html += `
      <div class="tp-empty">
        <div class="tp-empty-icon">📑</div>
        <div class="tp-empty-text">No phases yet. Add a phase to start breaking down work.</div>
      </div>
    `;
    return html;
  }

  for (const phase of phases) {
    const tasks = phase.tasks || [];
    const done = tasks.filter(t => t.status === "done").length;

    html += `<div class="tp-phase">`;
    html += `
      <div class="tp-phase-header">
        <span>${esc(phase.name)} (${done}/${tasks.length})</span>
        <button class="tp-btn tp-btn--sm tp-btn--ghost"
                data-action="add-task" data-project-id="${project.id}" data-phase-id="${phase.id}">+ Task</button>
      </div>
    `;

    for (const task of tasks) {
      const isDone = task.status === "done";
      const initial = (task.assignee || "?")[0].toUpperCase();
      html += `
        <div class="tp-task tp-task--${task.priority}" data-action="open-task"
             data-project-id="${project.id}" data-task-id="${task.id}">
          <div class="tp-task-checkbox ${isDone ? 'checked' : ''}"
               data-action="toggle-task" data-project-id="${project.id}" data-task-id="${task.id}">
            ${isDone ? '✓' : ''}
          </div>
          <div class="tp-task-content">
            <div class="tp-task-title ${isDone ? 'done' : ''}">${esc(task.title)}</div>
            <div class="tp-task-detail">
              ${task.assignee ? `<span class="tp-agent-avatar">${initial}</span><span>@${esc(task.assignee)}</span>` : ''}
              <span class="tp-badge tp-badge--${task.status}">${task.status.replace("_", " ")}</span>
            </div>
          </div>
        </div>
      `;
    }

    html += `</div>`;
  }

  return html;
}

function renderTeam(project, state) {
  const agents = project.agents || [];
  const coordinator = project.coordinator || "main";

  let html = `<h3 style="font-size:14px;margin-bottom:12px">Team Members</h3>`;
  html += `<div class="tp-team">`;

  // Coordinator
  html += `
    <div class="tp-team-member">
      <span class="tp-agent-avatar" style="background:#22c55e">${coordinator[0].toUpperCase()}</span>
      <span>@${esc(coordinator)}</span>
      <span class="tp-badge tp-badge--active">coordinator</span>
    </div>
  `;

  // Other agents
  for (const agentId of agents) {
    if (agentId === coordinator) continue;
    const taskCount = countAgentTasks(project, agentId);
    html += `
      <div class="tp-team-member">
        <span class="tp-agent-avatar">${agentId[0].toUpperCase()}</span>
        <span>@${esc(agentId)}</span>
        <span style="color:var(--text-muted);font-size:11px">${taskCount} tasks</span>
      </div>
    `;
  }

  html += `</div>`;

  html += `
    <button class="tp-btn tp-btn--sm tp-btn--ghost" data-action="add-agent"
            data-project-id="${project.id}">+ Add Agent</button>
  `;

  return html;
}

function renderStats(project, stats) {
  let html = `
    <div class="tp-stats">
      <div class="tp-stat">
        <div class="tp-stat-value">${stats.progress}%</div>
        <div class="tp-stat-label">Progress</div>
      </div>
      <div class="tp-stat">
        <div class="tp-stat-value">${stats.total}</div>
        <div class="tp-stat-label">Total Tasks</div>
      </div>
      <div class="tp-stat">
        <div class="tp-stat-value">${stats.done}</div>
        <div class="tp-stat-label">Completed</div>
      </div>
      <div class="tp-stat">
        <div class="tp-stat-value">${stats.inProgress}</div>
        <div class="tp-stat-label">In Progress</div>
      </div>
    </div>
  `;

  // By agent breakdown
  html += `<h3 style="font-size:14px;margin-bottom:8px">By Agent</h3>`;
  for (const [agentId, count] of Object.entries(stats.byAssignee)) {
    const agentDone = stats.doneByAssignee[agentId] || 0;
    const pct = count > 0 ? Math.round((agentDone / count) * 100) : 0;
    html += `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:13px">
        <span class="tp-agent-avatar">${agentId[0].toUpperCase()}</span>
        <span style="flex:1">@${esc(agentId)}</span>
        <span style="color:var(--text-muted)">${agentDone}/${count}</span>
        <div class="tp-progress" style="width:60px">
          <div class="tp-progress-bar ${pct === 100 ? 'complete' : ''}" style="width:${pct}%"></div>
        </div>
      </div>
    `;
  }

  return html;
}

function renderModal(modal, state) {
  if (modal.type === "create-project") {
    return `
      <div class="tp-modal-overlay" data-action="close-modal">
        <div class="tp-modal" onclick="event.stopPropagation()">
          <h3>🚀 New Project</h3>
          <div class="tp-field">
            <label>Project Name</label>
            <input type="text" id="tp-project-name" placeholder="e.g., Website Redesign" />
          </div>
          <div class="tp-field">
            <label>Description</label>
            <textarea id="tp-project-desc" placeholder="What's this project about?"></textarea>
          </div>
          <div class="tp-field">
            <label>Coordinator Agent</label>
            <input type="text" id="tp-project-coordinator" value="main" placeholder="Agent ID" />
          </div>
          <div class="tp-field">
            <label>Team Agents (comma-separated)</label>
            <input type="text" id="tp-project-agents" placeholder="e.g., researcher, coder, designer" />
          </div>
          <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
            <button class="tp-btn tp-btn--ghost" data-action="close-modal">Cancel</button>
            <button class="tp-btn" data-action="submit-create-project">Create Project</button>
          </div>
        </div>
      </div>
    `;
  }

  if (modal.type === "add-phase") {
    return `
      <div class="tp-modal-overlay" data-action="close-modal">
        <div class="tp-modal" onclick="event.stopPropagation()">
          <h3>📑 Add Phase</h3>
          <div class="tp-field">
            <label>Phase Name</label>
            <input type="text" id="tp-phase-name" placeholder="e.g., Research, Design, Development" />
          </div>
          <div class="tp-field">
            <label>Description</label>
            <textarea id="tp-phase-desc" placeholder="What work happens in this phase?"></textarea>
          </div>
          <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
            <button class="tp-btn tp-btn--ghost" data-action="close-modal">Cancel</button>
            <button class="tp-btn" data-action="submit-add-phase">Add Phase</button>
          </div>
        </div>
      </div>
    `;
  }

  if (modal.type === "add-task") {
    const agents = state.activeProject?.agents || [];
    return `
      <div class="tp-modal-overlay" data-action="close-modal">
        <div class="tp-modal" onclick="event.stopPropagation()">
          <h3>✅ Add Task</h3>
          <div class="tp-field">
            <label>Task Title</label>
            <input type="text" id="tp-task-title" placeholder="What needs to be done?" />
          </div>
          <div class="tp-field">
            <label>Description</label>
            <textarea id="tp-task-desc" placeholder="Details, acceptance criteria, context..."></textarea>
          </div>
          <div style="display:flex;gap:8px">
            <div class="tp-field" style="flex:1">
              <label>Assign To</label>
              <select id="tp-task-assignee">
                <option value="">Unassigned</option>
                ${agents.map(a => `<option value="${a}">@${a}</option>`).join("")}
              </select>
            </div>
            <div class="tp-field" style="flex:1">
              <label>Priority</label>
              <select id="tp-task-priority">
                <option value="medium">Medium</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          <div class="tp-field">
            <label>Depends On (task IDs, comma-separated)</label>
            <input type="text" id="tp-task-deps" placeholder="e.g., task_abc123, task_def456" />
          </div>
          <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
            <button class="tp-btn tp-btn--ghost" data-action="close-modal">Cancel</button>
            <button class="tp-btn" data-action="submit-add-task">Add Task</button>
          </div>
        </div>
      </div>
    `;
  }

  return "";
}

// ── Helpers ──────────────────────────────────────────────────────────────

function esc(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function computeStats(project) {
  let total = 0, done = 0, inProgress = 0;
  const byAssignee = {};
  const doneByAssignee = {};
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      total++;
      if (task.status === "done") done++;
      if (task.status === "in_progress") inProgress++;
      if (task.assignee) {
        byAssignee[task.assignee] = (byAssignee[task.assignee] || 0) + 1;
        if (task.status === "done") {
          doneByAssignee[task.assignee] = (doneByAssignee[task.assignee] || 0) + 1;
        }
      }
    }
  }
  return {
    total, done, inProgress,
    progress: total > 0 ? Math.round((done / total) * 100) : 0,
    byAssignee,
    doneByAssignee,
  };
}

function countAgentTasks(project, agentId) {
  let count = 0;
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      if (task.assignee === agentId) count++;
    }
  }
  return count;
}
