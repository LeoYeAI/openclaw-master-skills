/**
 * Team Chat Drawer — slide-out panel from right edge
 *
 * Shows live project activity: agents talking, task progress, and work
 * being done in real-time. Always-visible edge tab on the right side.
 */

import { html, nothing } from "lit";
import type { AppViewState } from "../app-view-state.ts";
import type { GatewayBrowserClient } from "../gateway.ts";

// ── Types ───────────────────────────────────────────────────────────────

interface TeamChatEntry {
  type: "task_update" | "agent_message" | "comment" | "system";
  agent?: string;
  taskTitle?: string;
  text: string;
  timestamp: string;
}

interface TaskInfo {
  id: string;
  title: string;
  status: string;
  assignee?: string;
}

interface ProjectInfo {
  id: string;
  name: string;
  phases?: Array<{
    tasks?: TaskInfo[];
  }>;
}

type DrawerState = AppViewState & { requestUpdate?: () => void };

// ── Polling ─────────────────────────────────────────────────────────────

let pollTimer: ReturnType<typeof setInterval> | null = null;

function startPolling(state: DrawerState, client: GatewayBrowserClient) {
  stopPolling();
  fetchTeamData(state, client);
  pollTimer = setInterval(() => fetchTeamData(state, client), 5000);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function fetchTeamData(state: DrawerState, client: GatewayBrowserClient) {
  if (state.teamChatLoading) return;
  state.teamChatLoading = true;
  state.requestUpdate?.();

  try {
    // Fetch sub-agent sessions
    const sessionsResult = await client.request("sessions.list", {
      limit: 20,
      includeLastMessage: true,
    }) as { sessions?: unknown[] } | null;
    // Filter to subagent/isolated sessions client-side
    const allSessions = (sessionsResult?.sessions ?? []) as Array<{ key?: string; [k: string]: unknown }>;
    state.teamChatSessions = allSessions.filter(
      (s) => s.key && (s.key.includes(":subagent:") || s.key.includes(":cron:")),
    );

    // Fetch project data via dedicated RPC
    try {
      const projectResult = await client.request("teamProjects.list", {}) as {
        projects?: Array<{ id: string; status?: string; name?: string }>;
      } | null;

      const projects = projectResult?.projects ?? [];
      if (projects.length > 0) {
        // Prefer the active project, or the first one
        const active = projects.find((p) => p.status === "active") ?? projects[0];
        state.teamChatProject = active;
      }
    } catch { /* project fetch error — ignore */ }

    // Build activity feed from sessions
    const activity: TeamChatEntry[] = [];
    const sessions = state.teamChatSessions as Array<{
      key?: string;
      label?: string;
      running?: boolean;
      updatedAt?: number;
      lastMessages?: Array<{ role?: string; text?: string; timestamp?: number }>;
    }>;

    for (const session of sessions) {
      const agentName = session.label ?? session.key ?? "Unknown Agent";
      const msgs = session.lastMessages ?? [];
      for (const msg of msgs) {
        if (msg.role === "assistant" && msg.text) {
          activity.push({
            type: "agent_message",
            agent: agentName,
            text: msg.text.length > 200 ? msg.text.slice(0, 200) + "…" : msg.text,
            timestamp: msg.timestamp
              ? new Date(msg.timestamp).toISOString()
              : new Date().toISOString(),
          });
        }
      }

      // Add system entry for running sessions
      if (session.running) {
        activity.push({
          type: "system",
          agent: agentName,
          text: `${agentName} is working…`,
          timestamp: session.updatedAt
            ? new Date(session.updatedAt).toISOString()
            : new Date().toISOString(),
        });
      }
    }

    // Sort by timestamp desc
    activity.sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );

    state.teamChatActivity = activity;
  } catch {
    // Silently handle errors
  } finally {
    state.teamChatLoading = false;
    state.requestUpdate?.();
  }
}

// ── Helper functions ────────────────────────────────────────────────────

function getProjectTasks(project: unknown): TaskInfo[] {
  if (!project || typeof project !== "object") return [];
  const p = project as ProjectInfo;
  const tasks: TaskInfo[] = [];
  for (const phase of p.phases ?? []) {
    for (const task of phase.tasks ?? []) {
      tasks.push(task);
    }
  }
  return tasks;
}

function getProgressInfo(project: unknown): { done: number; total: number; pct: number } {
  const tasks = getProjectTasks(project);
  if (tasks.length === 0) return { done: 0, total: 0, pct: 0 };
  const done = tasks.filter((t) => t.status === "done").length;
  return { done, total: tasks.length, pct: Math.round((done / tasks.length) * 100) };
}

function statusBadgeClass(status: string): string {
  switch (status) {
    case "done":
      return "badge--done";
    case "in_progress":
      return "badge--progress";
    case "blocked":
      return "badge--blocked";
    case "review":
      return "badge--review";
    default:
      return "badge--todo";
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case "done":
      return "Done";
    case "in_progress":
      return "In Progress";
    case "blocked":
      return "Blocked";
    case "review":
      return "Review";
    case "todo":
      return "To Do";
    default:
      return status;
  }
}

function formatTimestamp(ts: string): string {
  try {
    const d = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    if (diffMs < 60_000) return "just now";
    if (diffMs < 3_600_000) return `${Math.floor(diffMs / 60_000)}m ago`;
    if (diffMs < 86_400_000) return `${Math.floor(diffMs / 3_600_000)}h ago`;
    return d.toLocaleDateString([], { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

function entryIcon(type: string): string {
  switch (type) {
    case "task_update":
      return "📋";
    case "agent_message":
      return "🤖";
    case "comment":
      return "💬";
    case "system":
      return "⚙️";
    default:
      return "•";
  }
}

// ── Edge Tab (always visible) ───────────────────────────────────────────

export function renderTeamChatEdgeTab(state: DrawerState, client?: GatewayBrowserClient | null) {
  const sessions = state.teamChatSessions as Array<{ running?: boolean }>;
  const activeCount = sessions.filter((s) => s.running).length;

  const onToggle = () => {
    state.teamChatOpen = !state.teamChatOpen;
    // Use state.client (live reference) instead of closure-captured client
    // which may be null if captured before WebSocket connected
    const liveClient = (state as unknown as { client: GatewayBrowserClient | null }).client ?? client;
    if (state.teamChatOpen && liveClient) {
      startPolling(state, liveClient);
    } else {
      stopPolling();
    }
    state.requestUpdate?.();
  };

  return html`
    ${teamChatInlineStyles}
    <button
      class="tc-edge-tab ${state.teamChatOpen ? "tc-edge-tab--open" : ""}"
      @click=${onToggle}
      title="Toggle Team Chat"
    >
      <span class="tc-edge-tab__content">
        <span class="tc-edge-tab__icon">📋</span>
        <span class="tc-edge-tab__label">Team</span>
        ${activeCount > 0
          ? html`<span class="tc-edge-tab__badge">${activeCount}</span>`
          : nothing}
      </span>
    </button>
  `;
}

// ── Main Drawer Panel ───────────────────────────────────────────────────

export function renderTeamChatDrawer(
  state: DrawerState,
  client?: GatewayBrowserClient | null,
): ReturnType<typeof html> {
  if (!state.teamChatOpen) return html`${nothing}`;

  const project = state.teamChatProject as ProjectInfo | null;
  const activity = (state.teamChatActivity ?? []) as TeamChatEntry[];
  const tasks = getProjectTasks(project);
  const progress = getProgressInfo(project);

  const onClose = () => {
    state.teamChatOpen = false;
    stopPolling();
    state.requestUpdate?.();
  };

  const onOverlayClick = (e: Event) => {
    if ((e.target as HTMLElement).classList.contains("tc-overlay")) onClose();
  };

  const onInputChange = (e: Event) => {
    state.teamChatInput = (e.target as HTMLTextAreaElement).value;
    state.requestUpdate?.();
  };

  const onSend = async () => {
    const msg = (state.teamChatInput ?? "").trim();
    if (!msg || !client) return;
    state.teamChatInput = "";
    state.requestUpdate?.();
    try {
      await client.request("sessions.send", { message: msg });
    } catch { /* ignore */ }
  };

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void onSend();
    }
  };

  const onToggleTasks = () => {
    state.teamChatTasksCollapsed = !state.teamChatTasksCollapsed;
    state.requestUpdate?.();
  };

  return html`
    <div class="tc-overlay" @click=${onOverlayClick}>
      <div class="tc-panel">
        <!-- Header -->
        <div class="tc-header">
          <span class="tc-header__title">📋 Team Chat</span>
          <div class="tc-header__actions">
            ${state.teamChatLoading
              ? html`<span class="tc-spinner">⟳</span>`
              : nothing}
            <button class="tc-icon-btn" title="Close" @click=${onClose}>✕</button>
          </div>
        </div>

        <!-- Project Info & Progress -->
        ${project
          ? html`
            <div class="tc-project-bar">
              <span class="tc-project-name">${(project as ProjectInfo).name ?? "Project"}</span>
              <span class="tc-project-status">${(project as { status?: string }).status ?? ""}</span>
            </div>
            <div class="tc-progress">
              <div class="tc-progress__bar">
                <div class="tc-progress__fill" style="width: ${progress.pct}%"></div>
              </div>
              <span class="tc-progress__label">${progress.done}/${progress.total} tasks (${progress.pct}%)</span>
            </div>
          `
          : html`
            <div class="tc-project-bar">
              <span class="tc-project-name tc-muted">No active project</span>
            </div>
          `}

        <!-- Activity Feed -->
        <div class="tc-section-label">Activity</div>
        <div class="tc-activity" id="tc-activity-feed">
          ${activity.length === 0
            ? html`<div class="tc-empty">No recent activity</div>`
            : activity.map(
                (entry) => html`
                  <div class="tc-entry tc-entry--${entry.type}">
                    <span class="tc-entry__icon">${entryIcon(entry.type)}</span>
                    <div class="tc-entry__body">
                      ${entry.agent
                        ? html`<span class="tc-entry__agent">${entry.agent}</span>`
                        : nothing}
                      <span class="tc-entry__text">${entry.text}</span>
                    </div>
                    <span class="tc-entry__time">${formatTimestamp(entry.timestamp)}</span>
                  </div>
                `,
              )}
        </div>

        <!-- Task Overview -->
        <div class="tc-section-label tc-section-label--toggle" @click=${onToggleTasks}>
          <span>${state.teamChatTasksCollapsed ? "▶" : "▼"} Tasks</span>
          <span class="tc-task-count">${tasks.length}</span>
        </div>
        ${state.teamChatTasksCollapsed
          ? nothing
          : html`
            <div class="tc-tasks">
              ${tasks.length === 0
                ? html`<div class="tc-empty">No tasks</div>`
                : tasks.map(
                    (task) => html`
                      <div class="tc-task">
                        <span class="tc-task__badge ${statusBadgeClass(task.status)}">${statusLabel(task.status)}</span>
                        <span class="tc-task__title">${task.title}</span>
                        ${task.assignee
                          ? html`<span class="tc-task__assignee">→ ${task.assignee}</span>`
                          : nothing}
                      </div>
                    `,
                  )}
            </div>
          `}

        <!-- Quick Actions -->
        <div class="tc-input-row">
          <textarea
            class="tc-input"
            placeholder="Send a message… (Enter to send)"
            .value=${state.teamChatInput ?? ""}
            @input=${onInputChange}
            @keydown=${onKeyDown}
            rows="2"
          ></textarea>
          <button
            class="tc-send-btn"
            @click=${() => void onSend()}
            ?disabled=${!(state.teamChatInput ?? "").trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  `;
}

// ── Inline Styles (no Shadow DOM — styles must be in rendered HTML) ─────

const teamChatInlineStyles = html`<style>
  /* ── Edge Tab ─────────────────────────────────────────────────────── */
  .tc-edge-tab {
    position: fixed;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    z-index: 8999;
    background: var(--bg-header, #16162a);
    border: 1px solid var(--border-color, #2e2e4a);
    border-right: none;
    border-radius: 8px 0 0 8px;
    padding: 12px 6px;
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: -2px 0 12px rgba(0, 0, 0, 0.3);
  }

  .tc-edge-tab:hover {
    background: var(--bg-hover, rgba(255, 255, 255, 0.07));
  }

  .tc-edge-tab--open {
    background: var(--bg-panel, #1a1a2e);
    border-color: var(--border-color, #2e2e4a);
    right: min(480px, 100vw);
    transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.2s;
  }

  .tc-edge-tab__content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    writing-mode: vertical-rl;
    text-orientation: mixed;
  }

  .tc-edge-tab__icon {
    font-size: 14px;
    writing-mode: horizontal-tb;
  }

  .tc-edge-tab__label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: var(--text-primary, #e0e0f0);
    text-transform: uppercase;
  }

  .tc-edge-tab__badge {
    writing-mode: horizontal-tb;
    background: rgba(99, 102, 241, 0.9);
    color: white;
    font-size: 10px;
    font-weight: 700;
    min-width: 16px;
    height: 16px;
    line-height: 16px;
    text-align: center;
    border-radius: 8px;
    padding: 0 4px;
    animation: tc-pulse 2s ease-in-out infinite;
  }

  @keyframes tc-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }

  /* ── Overlay & Panel ──────────────────────────────────────────────── */
  .tc-overlay {
    position: fixed;
    inset: 0;
    z-index: 9000;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    justify-content: flex-end;
    animation: tc-fade-in 0.2s ease-out;
  }

  @keyframes tc-fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .tc-panel {
    width: min(480px, 100vw);
    height: 100vh;
    background: var(--bg-panel, #1a1a2e);
    border-left: 1px solid var(--border-color, #2e2e4a);
    display: flex;
    flex-direction: column;
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.5);
    font-family: var(--font-sans, system-ui, sans-serif);
    font-size: 13px;
    color: var(--text-primary, #e0e0f0);
    animation: tc-slide-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  @keyframes tc-slide-in {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
  }

  /* ── Header ───────────────────────────────────────────────────────── */
  .tc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color, #2e2e4a);
    background: var(--bg-header, #16162a);
    flex-shrink: 0;
  }

  .tc-header__title {
    font-weight: 600;
    font-size: 14px;
  }

  .tc-header__actions {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .tc-icon-btn {
    background: none;
    border: none;
    color: var(--text-secondary, #888);
    cursor: pointer;
    font-size: 16px;
    padding: 4px 8px;
    border-radius: 4px;
    transition: background 0.15s;
  }

  .tc-icon-btn:hover {
    background: var(--bg-hover, rgba(255, 255, 255, 0.07));
    color: var(--text-primary, #e0e0f0);
  }

  .tc-spinner {
    display: inline-block;
    animation: tc-spin 1s linear infinite;
    font-size: 14px;
    opacity: 0.6;
  }

  @keyframes tc-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  /* ── Project Bar & Progress ───────────────────────────────────────── */
  .tc-project-bar {
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color, #2e2e4a);
    flex-shrink: 0;
  }

  .tc-project-name {
    font-weight: 600;
    font-size: 13px;
  }

  .tc-project-status {
    font-size: 11px;
    color: var(--text-secondary, #888);
    text-transform: capitalize;
  }

  .tc-muted {
    color: var(--text-secondary, #888);
    font-weight: 400;
  }

  .tc-progress {
    padding: 8px 16px;
    border-bottom: 1px solid var(--border-color, #2e2e4a);
    flex-shrink: 0;
  }

  .tc-progress__bar {
    height: 6px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 4px;
  }

  .tc-progress__fill {
    height: 100%;
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.8), rgba(34, 197, 94, 0.8));
    border-radius: 3px;
    transition: width 0.5s ease;
  }

  .tc-progress__label {
    font-size: 11px;
    color: var(--text-secondary, #888);
  }

  /* ── Section Labels ───────────────────────────────────────────────── */
  .tc-section-label {
    padding: 6px 16px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-secondary, #888);
    border-bottom: 1px solid var(--border-color, #2e2e4a);
    flex-shrink: 0;
    background: var(--bg-header, #16162a);
  }

  .tc-section-label--toggle {
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    user-select: none;
  }

  .tc-section-label--toggle:hover {
    background: var(--bg-hover, rgba(255, 255, 255, 0.04));
  }

  .tc-task-count {
    background: rgba(255, 255, 255, 0.08);
    padding: 1px 6px;
    border-radius: 8px;
    font-size: 10px;
  }

  /* ── Activity Feed ────────────────────────────────────────────────── */
  .tc-activity {
    flex: 1;
    overflow-y: auto;
    padding: 8px 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-height: 120px;
  }

  .tc-empty {
    color: var(--text-secondary, #888);
    font-size: 12px;
    text-align: center;
    padding: 24px 0;
    opacity: 0.6;
  }

  .tc-entry {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid transparent;
    transition: background 0.15s;
  }

  .tc-entry:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  .tc-entry--agent_message {
    background: rgba(34, 197, 94, 0.06);
    border-color: rgba(34, 197, 94, 0.12);
  }

  .tc-entry--task_update {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.12);
  }

  .tc-entry--system {
    background: rgba(234, 179, 8, 0.04);
    border-color: rgba(234, 179, 8, 0.1);
    opacity: 0.8;
  }

  .tc-entry--comment {
    background: rgba(148, 163, 184, 0.06);
    border-color: rgba(148, 163, 184, 0.12);
  }

  .tc-entry__icon {
    flex-shrink: 0;
    font-size: 12px;
    margin-top: 2px;
  }

  .tc-entry__body {
    flex: 1;
    min-width: 0;
  }

  .tc-entry__agent {
    font-size: 11px;
    font-weight: 600;
    color: rgba(99, 102, 241, 0.9);
    display: block;
    margin-bottom: 2px;
  }

  .tc-entry__text {
    font-size: 12px;
    line-height: 1.4;
    word-break: break-word;
    color: var(--text-primary, #e0e0f0);
    display: block;
    white-space: pre-wrap;
    max-height: 80px;
    overflow: hidden;
  }

  .tc-entry__time {
    flex-shrink: 0;
    font-size: 10px;
    color: var(--text-secondary, #888);
    opacity: 0.6;
    white-space: nowrap;
    margin-top: 2px;
  }

  /* ── Tasks ────────────────────────────────────────────────────────── */
  .tc-tasks {
    max-height: 200px;
    overflow-y: auto;
    padding: 6px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    border-bottom: 1px solid var(--border-color, #2e2e4a);
    flex-shrink: 0;
  }

  .tc-task {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 6px;
    border-radius: 4px;
    font-size: 12px;
  }

  .tc-task:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  .tc-task__badge {
    flex-shrink: 0;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.3px;
    white-space: nowrap;
  }

  .badge--done {
    background: rgba(34, 197, 94, 0.15);
    color: rgba(34, 197, 94, 0.9);
  }

  .badge--progress {
    background: rgba(99, 102, 241, 0.15);
    color: rgba(99, 102, 241, 0.9);
  }

  .badge--blocked {
    background: rgba(239, 68, 68, 0.15);
    color: rgba(239, 68, 68, 0.9);
  }

  .badge--review {
    background: rgba(234, 179, 8, 0.15);
    color: rgba(234, 179, 8, 0.9);
  }

  .badge--todo {
    background: rgba(148, 163, 184, 0.12);
    color: rgba(148, 163, 184, 0.8);
  }

  .tc-task__title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .tc-task__assignee {
    flex-shrink: 0;
    font-size: 10px;
    color: var(--text-secondary, #888);
    opacity: 0.7;
  }

  /* ── Input Row ────────────────────────────────────────────────────── */
  .tc-input-row {
    display: flex;
    gap: 8px;
    padding: 10px 12px;
    border-top: 1px solid var(--border-color, #2e2e4a);
    background: var(--bg-header, #16162a);
    flex-shrink: 0;
  }

  .tc-input {
    flex: 1;
    background: var(--bg-input, #0f0f1e);
    border: 1px solid var(--border-color, #2e2e4a);
    color: var(--text-primary, #e0e0f0);
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 13px;
    resize: none;
    font-family: inherit;
    transition: border-color 0.15s;
  }

  .tc-input:focus {
    outline: none;
    border-color: rgba(99, 102, 241, 0.5);
  }

  .tc-send-btn {
    background: rgba(99, 102, 241, 0.8);
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: background 0.15s;
    align-self: flex-end;
  }

  .tc-send-btn:hover:not(:disabled) {
    background: rgba(99, 102, 241, 1);
  }

  .tc-send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
</style>`;
