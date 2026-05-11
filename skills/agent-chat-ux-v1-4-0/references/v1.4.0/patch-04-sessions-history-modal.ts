import { html, nothing } from "lit";

export type SessionHistoryItem = {
  role: string;
  text: string;
  timestamp: string;
};

export type SessionHistoryResult = {
  key: string;
  sessionId: string;
  agentId: string;
  total: number;
  offset: number;
  items: SessionHistoryItem[];
};

export type SessionHistoryModalProps = {
  open: boolean;
  loading: boolean;
  error: string | null;
  result: SessionHistoryResult | null;
  /** All available agents for the filter dropdown */
  agents: Array<{ id: string; name: string; emoji?: string }>;
  /** Currently selected agent filter (empty = all) */
  agentFilter: string;
  /** All sessions for the filtered agent */
  sessions: Array<{ key: string; displayName?: string }>;
  /** Currently selected session key */
  sessionKey: string;
  /** Search input value */
  search: string;
  /** Active role filter */
  roleFilter: string; // "all" | "user" | "assistant" | "system" | "tool"
  onClose: () => void;
  onAgentChange: (agentId: string) => void;
  onSessionChange: (key: string) => void;
  onSearchChange: (search: string) => void;
  onRoleFilterChange: (role: string) => void;
  onLoadMore: () => void;
};

function roleIcon(role: string): string {
  switch (role) {
    case "user":
      return "👤";
    case "assistant":
      return "🤖";
    case "system":
      return "⚙️";
    case "tool":
    case "toolResult":
      return "🔧";
    default:
      return "💬";
  }
}

function roleLabel(role: string): string {
  switch (role) {
    case "user":
      return "User";
    case "assistant":
      return "Assistant";
    case "system":
      return "System";
    case "tool":
    case "toolResult":
      return "Tool";
    default:
      return role;
  }
}

function formatTimestamp(ts: string): string {
  if (!ts) return "";
  try {
    const d = new Date(ts);
    return d.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return ts;
  }
}

const ROLE_FILTERS = ["all", "user", "assistant", "system", "tool"] as const;

export function renderSessionHistoryModal(props: SessionHistoryModalProps) {
  if (!props.open) return nothing;

  const items = props.result?.items ?? [];
  const total = props.result?.total ?? 0;
  const showing = (props.result?.offset ?? 0) + items.length;
  const hasMore = showing < total;

  return html`
    <div
      class="modal-overlay"
      @click=${(e: Event) => {
        if ((e.target as HTMLElement).classList.contains("modal-overlay")) props.onClose();
      }}
    >
      <div class="modal-panel session-history-modal">
        <div class="modal-header">
          <div class="card-title">Session History</div>
          <button class="btn" @click=${props.onClose}>✕</button>
        </div>

        <div class="session-history-filters">
          <label class="field">
            <span>Agent</span>
            <select
              .value=${props.agentFilter}
              @change=${(e: Event) =>
                props.onAgentChange((e.target as HTMLSelectElement).value)}
            >
              <option value="">All Agents</option>
              ${props.agents.map(
                (a) =>
                  html`<option value=${a.id} ?selected=${props.agentFilter === a.id}>
                    ${a.emoji ?? "🤖"} ${a.name || a.id}
                  </option>`,
              )}
            </select>
          </label>

          <label class="field" style="flex: 1;">
            <span>Session</span>
            <select
              .value=${props.sessionKey}
              @change=${(e: Event) =>
                props.onSessionChange((e.target as HTMLSelectElement).value)}
            >
              <option value="">Select a session...</option>
              ${props.sessions.map(
                (s) =>
                  html`<option value=${s.key} ?selected=${props.sessionKey === s.key}>
                    ${s.displayName || s.key}
                  </option>`,
              )}
            </select>
          </label>
        </div>

        <div class="session-history-filters">
          <label class="field" style="flex: 1;">
            <span>Search</span>
            <input
              type="text"
              .value=${props.search}
              placeholder="Search messages..."
              @input=${(e: Event) =>
                props.onSearchChange((e.target as HTMLInputElement).value)}
            />
          </label>

          <div class="session-history-role-chips">
            ${ROLE_FILTERS.map(
              (role) => html`
                <button
                  class="btn btn-sm ${props.roleFilter === role ? "btn-active" : ""}"
                  @click=${() => props.onRoleFilterChange(role)}
                >
                  ${role === "all" ? "All" : roleLabel(role)}
                </button>
              `,
            )}
          </div>
        </div>

        ${props.error
          ? html`<div class="callout danger" style="margin: 12px 0;">${props.error}</div>`
          : nothing}

        <div class="session-history-messages">
          ${props.loading && items.length === 0
            ? html`<div class="muted" style="padding: 24px; text-align: center;">Loading...</div>`
            : items.length === 0 && props.sessionKey
              ? html`<div class="muted" style="padding: 24px; text-align: center;">No messages found.</div>`
              : !props.sessionKey
                ? html`<div class="muted" style="padding: 24px; text-align: center;">Select a session to view history.</div>`
                : nothing}

          ${items.map(
            (item) => html`
              <div class="session-history-msg session-history-msg--${item.role}">
                <div class="session-history-msg-header">
                  <span class="session-history-msg-role">
                    ${roleIcon(item.role)} ${roleLabel(item.role)}
                  </span>
                  <span class="muted">${formatTimestamp(item.timestamp)}</span>
                </div>
                <div class="session-history-msg-text">${item.text}</div>
              </div>
            `,
          )}

          ${hasMore
            ? html`
                <div style="text-align: center; padding: 12px;">
                  <button class="btn" ?disabled=${props.loading} @click=${props.onLoadMore}>
                    ${props.loading ? "Loading..." : `Load More ↓`}
                  </button>
                  <span class="muted" style="margin-left: 8px;">
                    Showing ${showing} of ${total}
                  </span>
                </div>
              `
            : items.length > 0
              ? html`<div class="muted" style="text-align: center; padding: 12px;">
                  ${total} message${total !== 1 ? "s" : ""} total
                </div>`
              : nothing}
        </div>
      </div>
    </div>

    <style>
      .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.6);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(2px);
      }
      .session-history-modal {
        background: var(--bg-card, #1a1a2e);
        border: 1px solid var(--border, #333);
        border-radius: 12px;
        width: 90vw;
        max-width: 800px;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      }
      .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid var(--border, #333);
      }
      .session-history-filters {
        display: flex;
        gap: 12px;
        padding: 12px 20px;
        align-items: end;
        flex-wrap: wrap;
      }
      .session-history-role-chips {
        display: flex;
        gap: 4px;
        align-items: end;
        padding-bottom: 2px;
      }
      .btn-sm {
        padding: 4px 10px;
        font-size: 12px;
      }
      .btn-active {
        background: var(--accent, #6366f1);
        color: white;
      }
      .session-history-messages {
        flex: 1;
        overflow-y: auto;
        padding: 0 20px 16px;
        min-height: 200px;
      }
      .session-history-msg {
        padding: 10px 0;
        border-bottom: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.06));
      }
      .session-history-msg:last-child {
        border-bottom: none;
      }
      .session-history-msg-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
      }
      .session-history-msg-role {
        font-weight: 600;
        font-size: 13px;
      }
      .session-history-msg-text {
        font-size: 14px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-word;
        color: var(--text, #e0e0e0);
        max-height: 300px;
        overflow-y: auto;
      }
      .session-history-msg--user .session-history-msg-role {
        color: var(--accent, #6366f1);
      }
      .session-history-msg--assistant .session-history-msg-role {
        color: #10b981;
      }
      .session-history-msg--system .session-history-msg-role {
        color: #f59e0b;
      }
      .session-history-msg--tool .session-history-msg-role,
      .session-history-msg--toolResult .session-history-msg-role {
        color: #8b5cf6;
      }
    </style>
  `;
}
