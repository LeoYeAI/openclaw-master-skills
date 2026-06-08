/**
 * Team Projects — Control UI View
 *
 * Renders the team projects dashboard inside the plugin tab.
 */

import { html, nothing } from "lit";
import type { GatewayBrowserClient } from "../client.ts";

interface TeamProjectsViewState {
  client: GatewayBrowserClient | null;
  connected: boolean;
}

// ── Project data types ──────────────────────────────────────────────────

interface Task {
  id: string;
  title: string;
  description: string;
  assignee: string;
  priority: "critical" | "high" | "medium" | "low";
  status: "todo" | "in_progress" | "blocked" | "review" | "done";
  dependsOn: string[];
  comments: Array<{ author: string; text: string; timestamp: string }>;
  artifacts: string[];
  createdAt: string;
  completedAt: string | null;
}

interface Phase {
  id: string;
  name: string;
  description: string;
  order: number;
  status: "pending" | "active" | "completed";
  tasks: Task[];
}

interface Project {
  id: string;
  name: string;
  slug: string;
  description: string;
  coordinator: string;
  agents: string[];
  status: "planning" | "active" | "paused" | "completed" | "archived";
  phases: Phase[];
  createdAt: string;
  updatedAt: string;
}

// ── View State ──────────────────────────────────────────────────────────

let projects: Project[] = [];
let activeProjectId: string | null = null;
let activeTab: "board" | "team" | "stats" = "board";
let loading = false;
let error: string | null = null;

// ── RPC Calls ───────────────────────────────────────────────────────────

async function loadProjects(client: GatewayBrowserClient | null): Promise<void> {
  if (!client) return;
  loading = true;
  error = null;
  try {
    // Send a chat message to the agent to get project data
    // For now, read directly from the filesystem via a session message
    const result = (await client.call("sessions.send", {
      message:
        "Run this silently and respond ONLY with the raw JSON output, no commentary: node /home/charl/.openclaw/workspace/skills/team-projects/scripts/project-store.js list",
    })) as { response?: string } | undefined;

    if (result?.response) {
      try {
        projects = JSON.parse(result.response);
      } catch {
        projects = [];
      }
    }
  } catch (err) {
    error = String(err);
  } finally {
    loading = false;
  }
}

// ── Render Functions ────────────────────────────────────────────────────

export function renderTeamProjects(state: TeamProjectsViewState) {
  const activeProject = activeProjectId
    ? projects.find((p) => p.id === activeProjectId) ?? null
    : null;

  return html`
    <style>
      .tp-container {
        display: grid;
        grid-template-columns: 1fr;
        gap: 16px;
        padding: 0 4px;
      }

      .tp-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }

      .tp-btn {
        background: var(--accent, #6366f1);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
        cursor: pointer;
        transition: opacity 0.15s;
        font-family: inherit;
      }
      .tp-btn:hover {
        opacity: 0.85;
      }
      .tp-btn--ghost {
        background: transparent;
        color: var(--text-muted, #888);
        border: 1px solid var(--border, #444);
      }
      .tp-btn--ghost:hover {
        background: var(--bg-hover, #222);
      }
      .tp-btn--sm {
        padding: 4px 10px;
        font-size: 12px;
      }

      .tp-card {
        background: var(--bg-secondary, #1a1a2e);
        border: 1px solid var(--border, #333);
        border-radius: 12px;
        overflow: hidden;
      }

      .tp-card-header {
        padding: 16px 20px;
        border-bottom: 1px solid var(--border, #333);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .tp-card-header h3 {
        margin: 0;
        font-size: 15px;
        font-weight: 600;
      }
      .tp-card-body {
        padding: 16px 20px;
      }

      .tp-project-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 12px;
      }

      .tp-project-card {
        background: var(--bg-tertiary, #232340);
        border: 1px solid var(--border, #333);
        border-radius: 10px;
        padding: 16px;
        cursor: pointer;
        transition: border-color 0.15s, transform 0.1s;
      }
      .tp-project-card:hover {
        border-color: var(--accent, #6366f1);
        transform: translateY(-1px);
      }
      .tp-project-card.active {
        border-color: var(--accent, #6366f1);
        border-width: 2px;
      }

      .tp-project-name {
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 6px;
      }
      .tp-project-desc {
        font-size: 12px;
        color: var(--text-muted, #888);
        margin-bottom: 10px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      .tp-project-meta {
        display: flex;
        gap: 12px;
        align-items: center;
        font-size: 12px;
        color: var(--text-muted, #888);
      }

      .tp-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .tp-badge--planning {
        background: #3b82f620;
        color: #60a5fa;
      }
      .tp-badge--active {
        background: #22c55e20;
        color: #4ade80;
      }
      .tp-badge--paused {
        background: #f59e0b20;
        color: #fbbf24;
      }
      .tp-badge--completed {
        background: #22c55e20;
        color: #22c55e;
      }

      .tp-badge--todo {
        background: #64748b20;
        color: #94a3b8;
      }
      .tp-badge--in_progress {
        background: #6366f120;
        color: #818cf8;
      }
      .tp-badge--blocked {
        background: #ef444420;
        color: #f87171;
      }
      .tp-badge--review {
        background: #f59e0b20;
        color: #fbbf24;
      }
      .tp-badge--done {
        background: #22c55e20;
        color: #22c55e;
      }

      .tp-progress {
        width: 100%;
        height: 6px;
        background: var(--bg-primary, #111);
        border-radius: 3px;
        margin-top: 10px;
        overflow: hidden;
      }
      .tp-progress-bar {
        height: 100%;
        background: var(--accent, #6366f1);
        border-radius: 3px;
        transition: width 0.3s ease;
      }
      .tp-progress-bar.complete {
        background: #22c55e;
      }

      .tp-empty {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-muted, #666);
      }
      .tp-empty-icon {
        font-size: 56px;
        margin-bottom: 16px;
      }
      .tp-empty-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text, #e0e0e0);
        margin-bottom: 8px;
      }
      .tp-empty-text {
        font-size: 14px;
        margin-bottom: 24px;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.5;
      }

      .tp-stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 20px;
      }
      .tp-stat {
        background: var(--bg-tertiary, #232340);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
      }
      .tp-stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--accent, #6366f1);
      }
      .tp-stat-label {
        font-size: 11px;
        color: var(--text-muted, #888);
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .tp-task-list {
        list-style: none;
        padding: 0;
        margin: 0;
      }
      .tp-task-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        background: var(--bg-tertiary, #232340);
        border-left: 3px solid transparent;
        font-size: 13px;
        transition: background 0.1s;
      }
      .tp-task-item:hover {
        background: var(--bg-hover, #2a2a4a);
      }
      .tp-task-item--critical {
        border-left-color: #ef4444;
      }
      .tp-task-item--high {
        border-left-color: #f97316;
      }
      .tp-task-item--medium {
        border-left-color: #3b82f6;
      }
      .tp-task-item--low {
        border-left-color: #64748b;
      }

      .tp-task-title {
        font-weight: 500;
        flex: 1;
      }
      .tp-task-title.done {
        text-decoration: line-through;
        color: var(--text-muted, #666);
      }
      .tp-task-detail {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 11px;
        color: var(--text-muted, #888);
        margin-top: 3px;
      }

      .tp-agent-avatar {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--accent, #6366f1);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
      }

      .tp-phase-section {
        margin-bottom: 20px;
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

      .tp-team-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .tp-team-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        background: var(--bg-tertiary, #232340);
        border-radius: 20px;
        padding: 6px 12px 6px 6px;
        font-size: 13px;
      }

      .tp-info-hint {
        background: var(--bg-tertiary, #232340);
        border: 1px solid var(--border, #333);
        border-radius: 8px;
        padding: 16px;
        font-size: 13px;
        line-height: 1.6;
        color: var(--text-muted, #aaa);
      }
      .tp-info-hint code {
        background: var(--bg-primary, #111);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
      }
    </style>

    <div class="tp-container">
      ${activeProject ? renderProjectDetail(activeProject, state) : renderProjectList(state)}
    </div>
  `;
}

function renderProjectList(state: TeamProjectsViewState) {
  return html`
    <div class="tp-toolbar">
      <span style="font-size: 13px; color: var(--text-muted, #888)">
        ${projects.length} project${projects.length !== 1 ? "s" : ""}
      </span>
      <div style="display: flex; gap: 8px">
        <button
          class="tp-btn tp-btn--ghost tp-btn--sm"
          @click=${() => {
            void loadProjects(state.client);
          }}
        >
          ↻ Refresh
        </button>
        <button class="tp-btn tp-btn--sm">+ New Project</button>
      </div>
    </div>

    ${loading ? html`<p style="color: var(--text-muted)">Loading...</p>` : nothing}
    ${error ? html`<p style="color: #ef4444">${error}</p>` : nothing}

    ${
      projects.length === 0
        ? html`
            <div class="tp-card">
              <div class="tp-card-body">
                <div class="tp-empty">
                  <div class="tp-empty-icon">🚀</div>
                  <div class="tp-empty-title">No projects yet</div>
                  <div class="tp-empty-text">
                    Create your first team project by telling me in the chat. For example:
                    <br />
                    <em>"Create a team project to build a marketing website"</em>
                  </div>
                  <div class="tp-info-hint">
                    <strong>How it works:</strong> Ask me to create a project in the chat. I'll
                    break it into phases and tasks, assign them to agents like
                    <code>@scout-spark</code> and <code>@scout-monitor</code>, and dispatch work
                    using <code>sessions_spawn</code>. Progress appears here automatically.
                  </div>
                </div>
              </div>
            </div>
          `
        : html`
            <div class="tp-project-grid">
              ${projects.map((p) => {
                const totalTasks = p.phases.reduce((sum, ph) => sum + ph.tasks.length, 0);
                const doneTasks = p.phases.reduce(
                  (sum, ph) => sum + ph.tasks.filter((t) => t.status === "done").length,
                  0,
                );
                const progress = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;
                return html`
                  <div
                    class="tp-project-card ${activeProjectId === p.id ? "active" : ""}"
                    @click=${() => {
                      activeProjectId = p.id;
                    }}
                  >
                    <div class="tp-project-name">${p.name}</div>
                    <div class="tp-project-desc">${p.description || "No description"}</div>
                    <div class="tp-project-meta">
                      <span class="tp-badge tp-badge--${p.status}">${p.status}</span>
                      <span>${doneTasks}/${totalTasks} tasks</span>
                      <span>${p.agents.length} agents</span>
                    </div>
                    <div class="tp-progress">
                      <div
                        class="tp-progress-bar ${progress === 100 ? "complete" : ""}"
                        style="width: ${progress}%"
                      ></div>
                    </div>
                  </div>
                `;
              })}
            </div>
          `
    }
  `;
}

function renderProjectDetail(project: Project, _state: TeamProjectsViewState) {
  const totalTasks = project.phases.reduce((sum, ph) => sum + ph.tasks.length, 0);
  const doneTasks = project.phases.reduce(
    (sum, ph) => sum + ph.tasks.filter((t) => t.status === "done").length,
    0,
  );
  const inProgressTasks = project.phases.reduce(
    (sum, ph) => sum + ph.tasks.filter((t) => t.status === "in_progress").length,
    0,
  );
  const blockedTasks = project.phases.reduce(
    (sum, ph) => sum + ph.tasks.filter((t) => t.status === "blocked").length,
    0,
  );
  const progress = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;

  return html`
    <div class="tp-toolbar">
      <div style="display: flex; align-items: center; gap: 12px">
        <button
          class="tp-btn tp-btn--ghost tp-btn--sm"
          @click=${() => {
            activeProjectId = null;
          }}
        >
          ← Back
        </button>
        <span style="font-weight: 600; font-size: 16px">${project.name}</span>
        <span class="tp-badge tp-badge--${project.status}">${project.status}</span>
      </div>
    </div>

    <div class="tp-stats-grid">
      <div class="tp-stat">
        <div class="tp-stat-value">${progress}%</div>
        <div class="tp-stat-label">Progress</div>
      </div>
      <div class="tp-stat">
        <div class="tp-stat-value">${totalTasks}</div>
        <div class="tp-stat-label">Total Tasks</div>
      </div>
      <div class="tp-stat">
        <div class="tp-stat-value">${doneTasks}</div>
        <div class="tp-stat-label">Completed</div>
      </div>
      <div class="tp-stat">
        <div class="tp-stat-value" style="color: ${blockedTasks > 0 ? "#ef4444" : "var(--accent)"}">
          ${inProgressTasks}${blockedTasks > 0 ? html` / <span style="color:#ef4444">${blockedTasks}⚠</span>` : nothing}
        </div>
        <div class="tp-stat-label">Active / Blocked</div>
      </div>
    </div>

    <div class="tp-card">
      <div class="tp-card-header">
        <h3>Team</h3>
      </div>
      <div class="tp-card-body">
        <div class="tp-team-chips">
          <div class="tp-team-chip">
            <span class="tp-agent-avatar" style="background: #22c55e">
              ${project.coordinator[0].toUpperCase()}
            </span>
            @${project.coordinator}
            <span class="tp-badge tp-badge--active">coordinator</span>
          </div>
          ${project.agents
            .filter((a) => a !== project.coordinator)
            .map(
              (a) => html`
                <div class="tp-team-chip">
                  <span class="tp-agent-avatar">${a[0].toUpperCase()}</span>
                  @${a}
                </div>
              `,
            )}
        </div>
      </div>
    </div>

    ${project.phases.map((phase) => {
      const phaseDone = phase.tasks.filter((t) => t.status === "done").length;
      return html`
        <div class="tp-card">
          <div class="tp-card-header">
            <h3>
              ${phase.name}
              <span style="font-weight: normal; color: var(--text-muted); font-size: 12px">
                (${phaseDone}/${phase.tasks.length})
              </span>
            </h3>
            <span class="tp-badge tp-badge--${phase.status}">${phase.status}</span>
          </div>
          <div class="tp-card-body">
            ${phase.tasks.length === 0
              ? html`<p style="color: var(--text-muted); font-size: 13px">No tasks in this phase</p>`
              : html`
                  <ul class="tp-task-list">
                    ${phase.tasks.map(
                      (task) => html`
                        <li class="tp-task-item tp-task-item--${task.priority}">
                          <div>
                            <div class="tp-task-title ${task.status === "done" ? "done" : ""}">
                              ${task.title}
                            </div>
                            <div class="tp-task-detail">
                              ${task.assignee
                                ? html`
                                    <span class="tp-agent-avatar" style="width:16px;height:16px;font-size:8px">
                                      ${task.assignee[0].toUpperCase()}
                                    </span>
                                    <span>@${task.assignee}</span>
                                  `
                                : nothing}
                              <span class="tp-badge tp-badge--${task.status}">
                                ${task.status.replace("_", " ")}
                              </span>
                              ${task.dependsOn.length > 0
                                ? html`<span style="color: var(--text-muted)">
                                    deps: ${task.dependsOn.length}
                                  </span>`
                                : nothing}
                            </div>
                          </div>
                        </li>
                      `,
                    )}
                  </ul>
                `}
          </div>
        </div>
      `;
    })}
  `;
}
