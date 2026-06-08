/**
 * Team Projects — Team Chat UI
 *
 * Multi-agent chat view where agents can communicate within a project.
 * Supports @-mentions with autocomplete, task references, and message routing.
 */

const CHAT_CSS = `
  .tc-chat {
    display: flex;
    flex-direction: column;
    height: 100%;
    font-family: var(--font-sans, system-ui, sans-serif);
    color: var(--text, #e0e0e0);
    background: var(--bg-primary, #111);
  }

  .tc-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border, #333);
    background: var(--bg-secondary, #1a1a2e);
    flex-shrink: 0;
  }
  .tc-header-title {
    font-weight: 600;
    font-size: 14px;
    flex: 1;
  }
  .tc-header-badge {
    font-size: 11px;
    color: var(--text-muted, #888);
  }

  .tc-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .tc-msg {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    animation: tc-fadein 0.15s ease;
  }
  @keyframes tc-fadein {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .tc-msg-avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .tc-msg-body {
    flex: 1;
    min-width: 0;
  }

  .tc-msg-header {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 2px;
  }
  .tc-msg-author {
    font-weight: 600;
    font-size: 13px;
  }
  .tc-msg-time {
    font-size: 11px;
    color: var(--text-muted, #666);
  }

  .tc-msg-text {
    font-size: 13px;
    line-height: 1.5;
    word-break: break-word;
  }
  .tc-msg-text .mention {
    background: var(--accent, #6366f1)20;
    color: var(--accent, #6366f1);
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 600;
  }
  .tc-msg-text .task-ref {
    background: #f59e0b20;
    color: #fbbf24;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 12px;
    cursor: pointer;
  }

  .tc-msg--system {
    justify-content: center;
    margin: 16px 0;
  }
  .tc-msg--system .tc-msg-text {
    font-size: 12px;
    color: var(--text-muted, #666);
    text-align: center;
    font-style: italic;
  }

  /* Task completion inline */
  .tc-msg--completion {
    background: #22c55e10;
    border: 1px solid #22c55e30;
    border-radius: 8px;
    padding: 8px;
  }

  /* Input area */
  .tc-input-area {
    border-top: 1px solid var(--border, #333);
    padding: 12px 16px;
    background: var(--bg-secondary, #1a1a2e);
    flex-shrink: 0;
  }

  .tc-input-row {
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }

  .tc-input {
    flex: 1;
    background: var(--bg-primary, #111);
    border: 1px solid var(--border, #444);
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--text, #e0e0e0);
    font-size: 13px;
    font-family: inherit;
    resize: none;
    min-height: 36px;
    max-height: 120px;
    overflow-y: auto;
  }
  .tc-input:focus {
    outline: none;
    border-color: var(--accent, #6366f1);
  }

  .tc-send-btn {
    background: var(--accent, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    width: 36px; height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    flex-shrink: 0;
    transition: opacity 0.15s;
  }
  .tc-send-btn:hover { opacity: 0.85; }
  .tc-send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  /* Autocomplete dropdown */
  .tc-autocomplete {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    background: var(--bg-secondary, #1a1a2e);
    border: 1px solid var(--border, #444);
    border-radius: 8px;
    margin-bottom: 4px;
    max-height: 200px;
    overflow-y: auto;
    box-shadow: 0 -4px 12px rgba(0,0,0,0.3);
    z-index: 100;
  }
  .tc-autocomplete-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.1s;
  }
  .tc-autocomplete-item:hover,
  .tc-autocomplete-item.selected {
    background: var(--bg-hover, #2a2a4a);
  }

  /* Typing indicator */
  .tc-typing {
    padding: 4px 16px;
    font-size: 11px;
    color: var(--text-muted, #666);
    font-style: italic;
    min-height: 20px;
  }
`;

// ── Agent Colors ────────────────────────────────────────────────────────

const AGENT_COLORS = [
  "#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#3b82f6",
  "#ec4899", "#8b5cf6", "#14b8a6", "#f97316", "#06b6d4",
];

function agentColor(agentId) {
  let hash = 0;
  for (const c of agentId) hash = ((hash << 5) - hash + c.charCodeAt(0)) | 0;
  return AGENT_COLORS[Math.abs(hash) % AGENT_COLORS.length];
}

// ── Render Functions ────────────────────────────────────────────────────

export function renderTeamChat(state) {
  const { projectId, projectName, messages = [], agents = [], typingAgents = [] } = state;

  let html = `<style>${CHAT_CSS}</style>`;
  html += `<div class="tc-chat">`;

  // Header
  html += `
    <div class="tc-header">
      <span style="font-size:18px">💬</span>
      <span class="tc-header-title">${esc(projectName || "Team Chat")}</span>
      <span class="tc-header-badge">${agents.length} agents</span>
    </div>
  `;

  // Messages
  html += `<div class="tc-messages" id="tc-messages">`;

  if (messages.length === 0) {
    html += `
      <div class="tc-msg tc-msg--system">
        <div class="tc-msg-text">
          Start the conversation! Tag an agent with @name to get their attention.
        </div>
      </div>
    `;
  }

  for (const msg of messages) {
    if (msg.type === "system") {
      html += `
        <div class="tc-msg tc-msg--system">
          <div class="tc-msg-text">${esc(msg.text)}</div>
        </div>
      `;
      continue;
    }

    const color = agentColor(msg.author || "unknown");
    const initial = (msg.author || "?")[0].toUpperCase();
    const isCompletion = msg.text?.includes("TASK_COMPLETE:");

    html += `
      <div class="tc-msg ${isCompletion ? 'tc-msg--completion' : ''}">
        <div class="tc-msg-avatar" style="background:${color}">${initial}</div>
        <div class="tc-msg-body">
          <div class="tc-msg-header">
            <span class="tc-msg-author" style="color:${color}">@${esc(msg.author)}</span>
            <span class="tc-msg-time">${formatTime(msg.timestamp)}</span>
          </div>
          <div class="tc-msg-text">${formatMessageText(msg.text)}</div>
        </div>
      </div>
    `;
  }

  html += `</div>`;

  // Typing indicator
  html += `<div class="tc-typing">`;
  if (typingAgents.length > 0) {
    const names = typingAgents.map(a => `@${a}`).join(", ");
    html += `${names} ${typingAgents.length === 1 ? "is" : "are"} thinking...`;
  }
  html += `</div>`;

  // Input area
  html += `
    <div class="tc-input-area">
      <div class="tc-input-row" style="position:relative">
        <textarea class="tc-input" id="tc-input"
                  placeholder="Message the team... (use @ to mention agents)"
                  rows="1"></textarea>
        <button class="tc-send-btn" id="tc-send" data-action="send-chat">▶</button>
      </div>
    </div>
  `;

  html += `</div>`;
  return html;
}

// ── Text Formatting ─────────────────────────────────────────────────────

function formatMessageText(text) {
  if (!text) return "";
  let formatted = esc(text);

  // Highlight @mentions
  formatted = formatted.replace(/@([a-zA-Z][a-zA-Z0-9_-]{0,63})\b/g,
    '<span class="mention">@$1</span>');

  // Highlight #task refs
  formatted = formatted.replace(/#(task_[a-f0-9]+)/g,
    '<span class="task-ref">#$1</span>');

  // Newlines
  formatted = formatted.replace(/\n/g, "<br>");

  return formatted;
}

function formatTime(ts) {
  if (!ts) return "";
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

function esc(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
