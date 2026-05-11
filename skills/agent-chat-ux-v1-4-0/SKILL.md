---
name: agent-chat-ux
version: 1.4.0
author: Charles Sears
description: "Multi-agent UX for OpenClaw Control UI — agent selector, per-agent sessions, session history viewer with search, agent-filtered Sessions tab with friendly names, Create Agent wizard, emoji picker, and backend agent CRUD."
---

# agent-chat-ux

**name:** agent-chat-ux  
**version:** 1.4.0  
**author:** Charles Sears  
**description:** Multi-agent UX for OpenClaw Control UI — agent selector, per-agent sessions, session history viewer with search, agent-filtered Sessions tab with friendly names, Create Agent wizard, emoji picker, and backend agent CRUD.

---

## ⚠️ Security & Transparency Notes

Before applying this skill's patches, be aware of the following:

### Credential Access (`agents.wizard`)

The AI Wizard backend (`agents.wizard` RPC) calls the configured model provider API directly via HTTP. To do this it needs an API key. It resolves credentials in this exact order:

1. **Default config auth** — uses it if the resolved mode is `api-key` (most common)
2. **Auth profile store** — searches for the first `api_key`-type profile matching the provider. Reads only `provider` and `type` fields to find it; does not log or return values.
3. **Environment variable** — `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` as a last resort

> **If you don't want the wizard reading your auth store**, set `ANTHROPIC_API_KEY` in your environment and ensure your default auth profile is already `api-key` mode — step 2 is skipped entirely in that case.

### External API Calls

`agents.wizard` makes a single HTTP POST to:
- `https://api.anthropic.com/v1/messages` (Anthropic models)
- `https://api.openai.com/v1/chat/completions` (OpenAI-compatible models)

No other outbound calls. The call carries your user-supplied description and nothing else from your system.

### Patch Scope

These patches modify **only** agent-related files:

| Patch | File modified | What it changes |
|---|---|---|
| `schema-agents.txt` | `src/gateway/protocol/schema/agents-models-skills.ts` | Adds `emoji` optional param to `AgentsUpdateParamsSchema` |
| `server-agents.txt` | `src/gateway/server-methods/agents.ts` | Adds `agents.wizard` RPC; fixes `agents.update` to write `- Emoji:` (not `- Avatar:`) so emoji edits persist correctly |
| `app-main.txt` | `ui/src/ui/app.ts` | Adds 19 `@state()` fields: 10 for Create Agent/Wizard + 9 for edit agent, delete agent |
| `app-render.txt` | `ui/src/ui/app-render.ts` | Wires create/wizard props + edit agent save handler (sends `emoji` param, not `avatar`; evicts identity cache after save) |
| `app-render-helpers.txt` | `ui/src/ui/app-render.helpers.ts` | Agent selector dropdown in chat header (uses `resolveAgentEmoji()` for correct emoji), per-agent session filter, `+` New Session button |
| `agents-view.txt` | `ui/src/ui/views/agents.ts` | Create Agent panel (manual + wizard modes, 103-emoji picker); Edit agent inline form (name/emoji/workspace); Delete agent with confirmation; always-editable Overview |
| `agents-utils.txt` | `ui/src/ui/views/agents-utils.ts` | `buildModelOptionsMulti()` for multi-select fallback dropdown |
| `agents-panels-cron.txt` | `ui/src/ui/views/agents-panels-status-files.ts` | Cron Jobs tab Scheduler card now shows agent-specific job count and next-wake (not global gateway stats) |

Each patch is scoped to a single concern. If any patch file modifies more than the files listed above, stop — you have an outdated copy.

### LLM Output Validation

Wizard model output is parsed as JSON and validated before use:
- Must be a JSON object with `name` (string), `emoji` (string), `soul` (string)
- `name` is capped at 100 characters, `emoji` at 10
- `soul` must be ≥ 20 characters
- Empty or non-JSON responses are rejected with a user-visible error — nothing is auto-created

### Source Code Modification

This skill applies `git apply` patches against `~/openclaw` and requires a UI + gateway rebuild. Changes are persistent. **Always backup before patching:**

```bash
cd ~/openclaw && git stash  # or git branch backup/pre-agent-ux
```

---

## What This Skill Adds

### 1. Agent Selector Dropdown in Chat Header
When multiple agents are configured, a dropdown appears **left of the session dropdown** in the chat header. Selecting an agent switches to that agent's most recent session (or falls back to a fresh webchat key for that agent). The session dropdown automatically filters to show **only sessions belonging to the selected agent**.

### 2. Per-Agent Session Filtering (Sorted Newest First)
Sessions are now scoped to the active agent and sorted newest-first. No more mixing other agents' cron jobs and subagent sessions into the current chat's session picker.

### 3. + New Session Button in Chat Header
A `+` icon button sits right of the session dropdown, allowing new sessions to be started without typing `/new`.

### 4. Create Agent Panel (Manual + AI Wizard)
The Agents tab gains a **+ Create Agent** button that expands a panel with two modes:

**Manual mode:**
- Agent name
- Workspace path (auto-generated from name if left blank)
- Emoji picker (see below)

**AI Wizard mode:**
- Describe the agent in plain English
- Click "Generate Agent" — AI generates name, emoji, and full SOUL.md
- Review the preview, then click "✅ Create This Agent"

After creation, the agents list **and** config form are both refreshed automatically — no "not found in config" error, no manual reload needed.

### 5. Emoji Picker Dropdown
The emoji field in Create Agent and Edit Agent forms is a **dropdown with 103 curated emojis** grouped into 5 categories (Tech & AI, People & Roles, Animals, Nature & Elements, Objects & Symbols), each showing the emoji and its name. A large live preview shows the selected emoji next to the dropdown.

### 6. Edit Agent Inline (Agents Overview)
The Agents Overview card now shows editable inputs directly — no toggle needed:
- **Name**, **Emoji** (dropdown, 103 emojis), **Workspace** are always editable
- Changes activate the bottom **Save** button — no separate inline Save/Cancel
- Emoji is saved as `- Emoji:` in IDENTITY.md (last-wins override of creation value); identity cache is evicted after save so changes appear immediately
- Edit uses the `emoji` param of `agents.update` (not `avatar`) so the correct IDENTITY.md key is written

### 7. Delete Agent
- 🗑️ **Delete** button appears in the Overview header for non-default agents
- Inline confirmation dialog before deletion; hidden for the main/default agent

### 8. Agent-Specific Cron Stats
The **Scheduler** card on the Cron Jobs tab previously showed global gateway stats (total job count, global next wake). Now:
- **Jobs** → count of cron jobs targeting *this agent only*
- **Next wake** → earliest `nextRunAtMs` across this agent's jobs (`n/a` if no jobs)
- **Subtitle** → "Agent cron scheduling status." (was "Gateway cron status.")
This means agents with no crons correctly show `Jobs: 0` / `Next wake: n/a`.

### 9. Agents Tab — Model Selector Cleanup
- Removed the redundant read-only "Primary Model" row from the Overview grid (it's already editable in the Model Selection section below)
- **Fallback models** converted from a free-text comma-separated input to a proper **`<select multiple>`** using the same full model catalog as the primary selector
- Added spacing and clear labels between primary and fallback fields
- Small hint "(hold Ctrl/⌘ to select multiple)" on the fallback selector

### 10. Backend — `agents.create` / `agents.update` / `agents.delete` / `agents.wizard`
New RPC handlers wired into the gateway:

| Method | Description |
|--------|-------------|
| `agents.create` | Provisions a new agent entry in config + scaffolds workspace (SOUL.md, AGENTS.md, USER.md) |
| `agents.update` | Patches agent config (name, workspace, model, identity, etc.) |
| `agents.delete` | Removes agent from config |
| `agents.wizard` | Calls the configured LLM to generate name, emoji, and SOUL.md from a plain-text description |

**Auth fix in `agents.wizard`:** Raw HTTP calls to the model API require an `api_key` token, not an OAuth/bearer token. The wizard now falls back to an explicit `api_key` profile (or `ANTHROPIC_API_KEY` env var) when the default resolved auth mode is `oauth` or `token`.

### 11. Session History Viewer (v1.4.0)
A modal overlay accessible from the **Sessions tab** that displays full conversation history for any session:
- **Agent dropdown filter** — scope sessions by agent
- **Session dropdown** — pick a session to view (filtered by agent)
- **Search bar** — debounced full-text search across message content (case-insensitive)
- **Role filter chips** — All / User / Assistant / System / Tool
- **Message timeline** — role icons (👤/🤖/⚙️/🔧), timestamps, and message text
- **Pagination** — "Load More" with count display (100 messages per page)
- Click "History" button on any row in the Sessions tab to open

### 12. Sessions Tab Overhaul (v1.4.0)
The Sessions tab now provides a unified multi-agent experience:
- **Agent filter dropdown** — filter sessions by agent (populated from `agents.list`)
- **Friendly session names** — "Main Session", "Cron: pipedream-token-refresh", "discord:#bot-chat" instead of raw keys like `agent:main:cron:cc63fdb3-...`
- **Agent identity column** — shows agent emoji + identity name (e.g. "🤖 Assistant") using `identity.name` → `name` → `id` fallback chain
- **Raw key shown as subtitle** — full technical key displayed in smaller muted monospace text below the friendly name
- **Label column removed** — redundant since the friendly name already incorporates label/displayName
- **CSS grid layout** — proper column alignment using `grid-template-columns` with proportional widths; headers align precisely with data
- **Empty state** — clear message when an agent has no sessions
- **Session count** — total/filtered count shown in the store info line
- **History button pre-selects** — clicking History on a row opens the modal with agent and session already selected, loading history immediately

### 13. Backend — `sessions.history` RPC (v1.4.0)
New RPC handler that reads full JSONL transcript files:

| Param | Type | Description |
|-------|------|-------------|
| `key` | string | Session key |
| `limit` | number | Max messages (default 200, max 500) |
| `offset` | number | Pagination offset |
| `search` | string | Full-text search filter |
| `rolesFilter` | string[] | Filter by role(s) |

Returns `{key, sessionId, agentId, total, offset, items[{role, text, timestamp}]}`.

---

## Files Changed

| File | Change |
|------|--------|
| `src/gateway/protocol/schema/agents-models-skills.ts` | Adds `emoji` optional param to `AgentsUpdateParamsSchema` |
| `src/gateway/server-methods/agents.ts` | `agents.wizard` RPC; `agents.update` emoji fix (writes `- Emoji:` not `- Avatar:`) |
| `ui/src/ui/app-render.helpers.ts` | Agent dropdown in chat (with `resolveAgentEmoji()`), per-agent session filter, `+` New Session button |
| `ui/src/ui/views/agents.ts` | Create Agent panel, 103-emoji picker, edit/delete agent UI, always-editable Overview |
| `ui/src/ui/views/agents-utils.ts` | `buildModelOptionsMulti()` for multi-select fallback model dropdown |
| `ui/src/ui/views/agents-panels-status-files.ts` | Cron Jobs tab Scheduler card: agent-specific job count + next wake |
| `ui/src/ui/app-render.ts` | Create/wizard props wiring + edit agent save handler (emoji param, cache eviction) + session history modal wiring + agent filter for Sessions tab + agent identity name resolution (`identity.name` fallback chain) + History button agent pre-selection |
| `ui/src/ui/app.ts` | 19 `@state()` fields: create/wizard (10) + edit/delete agent (9) + session history modal (8) + sessions agent filter (1) |
| `ui/src/ui/app-view-state.ts` | Session history modal + sessions agent filter type definitions |
| `ui/src/ui/views/sessions.ts` | Overhauled: friendly names, agent identity column, agent filter dropdown, CSS grid layout, History button, Label column removed |
| `ui/src/ui/views/sessions-history-modal.ts` | **New file:** Session history modal component |
| `src/gateway/protocol/schema/sessions.ts` | `SessionsHistoryParamsSchema` |
| `src/gateway/protocol/schema/types.ts` | `SessionsHistoryParams` type export |
| `src/gateway/protocol/index.ts` | `validateSessionsHistoryParams` + re-exports |
| `src/gateway/server-methods/sessions.ts` | `sessions.history` RPC handler |
| `ui/src/ui/app-chat.ts` | Removed `CHAT_SESSIONS_ACTIVE_MINUTES` time filter (was 120min, now 0 = show all sessions in chat dropdown) |

---

## UI Design & Styling Reference

This section documents the UI design decisions for anyone installing or extending this skill.

### Sessions Tab Layout
Uses **CSS grid** (`display: grid`) instead of the default OpenClaw `.table` flex layout for precise column alignment:

```css
.sessions-grid {
  grid-template-columns: 2fr 1.2fr 0.6fr 0.8fr 1fr 0.8fr 0.8fr auto;
  /* Session | Agent | Kind | Updated | Tokens | Thinking | Reasoning | Actions */
}
```

- **Headers**: 12px uppercase, letter-spacing 0.5px, `var(--text-muted)` color, bottom border
- **Rows**: `display: contents` for grid participation, subtle bottom border, hover highlight at 2% white opacity
- **Session name cell**: Friendly name as bold link (`var(--accent, #6366f1)`), raw key below in 11px muted monospace at 50% opacity
- **Agent column**: 13px text, emoji + identity name (e.g. "🤖 Assistant")
- **Selects**: `max-width: 100px` to prevent overflow

### Session History Modal
Dark overlay modal with the following structure:

```
┌──────────────────────────────────────────────────┐
│  Session History                            [✕]  │
│  [Agent ▼]  [Session ▼]                         │
│  [🔍 Search...]  [All] [User] [Asst] [Sys] [Tool]│
│  ─────────────────────────────────────────────── │
│  👤 User · Feb 23, 10:23 AM                     │
│  Hello, can you help me?                         │
│  ─────────────────────────────────────────────── │
│  🤖 Assistant · Feb 23, 10:23 AM                │
│  Of course! What do you need?                    │
│  ─────────────────────────────────────────────── │
│          [Load More ↓]  Showing 100 of 342       │
└──────────────────────────────────────────────────┘
```

**Key CSS variables used:**
- `var(--bg-card, #1a1a2e)` — modal background
- `var(--border, #333)` — borders
- `var(--accent, #6366f1)` — user role color, active chip
- `var(--text, #e0e0e0)` — message text
- `var(--border-subtle, rgba(255,255,255,0.06))` — message separators

**Role colors:**
| Role | Color |
|------|-------|
| User | `var(--accent, #6366f1)` (indigo) |
| Assistant | `#10b981` (emerald) |
| System | `#f59e0b` (amber) |
| Tool | `#8b5cf6` (violet) |

**Role icons:** 👤 User, 🤖 Assistant, ⚙️ System, 🔧 Tool, 💬 Other

### Session Name Resolution
The friendly name fallback chain:
1. `row.label` (user-set label)
2. `row.displayName` (server-computed, e.g. "discord:#bot-chat")
3. Smart key parsing:
   - `*:main` → "Main Session"
   - `*:cron:*:run:*` → "Cron Run"
   - `*:cron:*` → "Cron Job"
   - `*:subagent:*` → "Subagent"
   - `*:openai:*` → "OpenAI Session"
   - `*:<channel>:direct:<id>` → "Channel · id"
   - `*:<channel>:group:*` → "Channel Group"
4. Raw key as fallback

### Agent Identity Resolution
For the Agent column and dropdowns:
1. `agent.identity.name` (from IDENTITY.md — e.g. "Assistant")
2. `agent.name` (from config — e.g. "main")
3. `agent.id` (raw identifier)

Emoji: `agent.identity.emoji` with "🤖" as fallback.

### Chat Dropdown
The session dropdown in the chat header shows **all sessions** for the selected agent (no time filter). Previously limited to sessions active within 120 minutes, which hid older Discord channels and other sessions.

---

## Installation

This skill requires patching OpenClaw source files and a UI + gateway rebuild.

### Prerequisites
- OpenClaw source at `~/openclaw` (fork or local clone)
- `pnpm` installed (`npm install -g pnpm`)
- Node.js 20+

### Step 1: Apply patches

```bash
cd ~/openclaw

git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/schema-agents.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/agents-view.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/agents-utils.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/agents-panels-cron.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/app-render-helpers.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/app-render.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/app-main.txt
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/server-agents.txt
```

If any patch fails due to upstream drift, apply manually using the patch file as a line-by-line reference.

### Step 1b: Apply v1.4.0 patches (Session History + Sessions Tab Overhaul)

```bash
cd ~/openclaw

# Backend: sessions.history RPC
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/v1.4.0/patch-01-sessions-history-rpc.txt

# Sessions tab: friendly names, agent column, agent filter
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/v1.4.0/patch-02-sessions-tab-overhaul.txt

# App state + render wiring for history modal
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/v1.4.0/patch-03-app-wiring.txt

# New file: session history modal component
cp ~/.openclaw/workspace/skills/agent-chat-ux/references/v1.4.0/patch-04-sessions-history-modal.ts \
   ui/src/ui/views/sessions-history-modal.ts

# Chat dropdown: show all sessions (remove 120min active filter)
git apply ~/.openclaw/workspace/skills/agent-chat-ux/references/v1.4.0/patch-05-chat-sessions-all.txt
```

### Step 2: Rebuild UI

```bash
cd ~/openclaw
pnpm ui:build
```

### Step 3: Rebuild gateway (for backend agent methods)

```bash
cd ~/openclaw
pnpm build
```

### Step 4: Restart gateway

```bash
openclaw gateway restart
```

### Step 5: Verify

1. Open Control UI at `http://localhost:18789`
2. **Chat tab** — agent dropdown appears left of session dropdown (if >1 agent configured); `+` button appears right of session dropdown
3. **Agents tab** — "+ Create Agent" button with Manual and AI Wizard modes
4. **Agents → Overview → Model Selection** — fallback is now a multi-select dropdown
5. Create an agent with the AI Wizard — should generate cleanly and appear in the list with no "not found" error
6. **Agents → Overview** — Name, Emoji, Workspace are editable directly; Save button at bottom activates on any change
7. Change an agent's emoji — after Save it should persist (not revert to the original creation emoji)
8. **Agents → Cron Jobs** — agents with no cron jobs show `Jobs: 0` / `Next wake: n/a` (not the global gateway count)
9. **Sessions tab** — sessions show friendly names (e.g. "Main Session") with agent emoji+name column; agent filter dropdown works
10. **Sessions tab → History button** — opens modal with conversation history, search, and role filter chips
11. **History modal → Agent filter** — changing agent filters the session dropdown; selecting a session loads its messages
12. **Chat dropdown** — session dropdown shows ALL sessions for the selected agent (including older Discord channels, OpenAI sessions, etc. — not just recent ones)

---

## Usage

### Chat: Switching Agents & Sessions
- **Agent dropdown** (left of session): picks the agent; session list updates to show only that agent's sessions
- **Session dropdown**: switches between existing conversations for the selected agent, newest first
- **`+` button**: starts a new session for the current agent (same as `/new`)

### Agents: Create Agent
1. Click **+ Create Agent**
2. **Manual:** enter name, workspace, pick emoji → "Create Agent"
3. **AI Wizard:** describe the agent → "Generate Agent" → review preview → "✅ Create This Agent"

### Agents: Fallback Models
In Model Selection:
- **Primary model** — single dropdown
- **Fallback models** — multi-select (`Ctrl`/`⌘` + click for multiple); these are retried in order when the primary model fails (rate limit, context overflow, etc.)

### Sessions: Viewing History
1. Go to **Sessions** tab
2. Optionally filter by agent using the **Agent** dropdown
3. Click **History** on any session row
4. The modal opens with the full conversation
5. **Search** — type to search across all messages (300ms debounce)
6. **Role chips** — click All/User/Assistant/System/Tool to filter by role
7. **Load More** — pagination loads 100 messages at a time

### Sessions: Agent-Filtered View
The Sessions tab now shows:
- **Session column** — friendly name with raw key as subtitle
- **Agent column** — emoji + name from agent identity
- **Agent filter** — dropdown at top to scope the view per-agent

---

## Architecture Notes

### Session Key Format
`agent:<agentId>:<rest>` — the agent selector reads `parseAgentSessionKey(state.sessionKey).agentId` to determine the active agent and filters the session list accordingly.

### Config Refresh After Creation
After `agents.create` succeeds, the UI calls both `agents.list` (to update the sidebar) and `loadConfig` (to refresh `configForm`). Without the `loadConfig` call, selecting the new agent would show "not found in config" because the config form was stale.

### Wizard Auth Resolution
`agents.wizard` makes a direct HTTP call to the model provider API. Raw HTTP calls require an `api_key` type credential — not an OAuth bearer token. The resolution order is:
1. Default `resolveApiKeyForProvider` result (used if mode is `api-key`)
2. First `api_key`-type profile in the auth store for the provider
3. `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` env var directly

This mirrors the same pattern used in `enhanced-loop-hook.ts`.

### Model Fallbacks
Stored as `model.fallbacks[]` in the agent config. The runtime tries them via `runWithModelFallback()` when the primary model returns an error.

---

## Changelog

### 1.4.0 (2026-02-23)
- **New:** Session History Viewer — modal overlay with full conversation history, full-text search, role filtering (All/User/Assistant/System/Tool), and pagination (100 messages per page)
- **New:** `sessions.history` RPC — reads full JSONL transcripts with search, role filtering, and offset/limit pagination
- **New:** Sessions tab agent filter dropdown — scope view to a single agent
- **New:** Sessions tab agent identity column — shows emoji + name per row
- **Overhaul:** Sessions tab now shows friendly display names ("Main Session", "Cron: pipedream-token-refresh") instead of raw keys (`agent:main:main`, `agent:main:cron:cc63fdb3-...`)
- **Overhaul:** Raw session key shown as muted subtitle under the friendly name for technical reference
- **New:** Empty state for agent-filtered sessions — clear message when an agent has no sessions
- **New:** Session count shown in store info line
- **Replaced:** Verbose + Label columns removed from Sessions tab, replaced by Agent column (better multi-agent UX; label was redundant with friendly name)
- **Design:** CSS grid layout for Sessions tab — proper column alignment using `grid-template-columns` with proportional widths
- **Design:** Agent identity resolution uses `identity.name` → config `name` → agent `id` fallback chain (shows "Assistant" not "Main Agent")
- **Design:** History button pre-selects agent filter and session in modal, loads history immediately
- **Design:** Raw session key shown as muted monospace subtitle for technical reference
- **Fix:** Chat session dropdown now shows ALL sessions (removed `CHAT_SESSIONS_ACTIVE_MINUTES` 120min time filter that was hiding older Discord channels and API sessions)
- **Patches:** 5 patch files in `references/v1.4.0/`

### 1.3.0 (2026-02-19)
- **New:** Edit agent inline — name, emoji, workspace always editable in Overview; single bottom Save button activates on any change; no inline Save/Cancel toggle
- **New:** Delete agent — 🗑️ button with inline confirmation; hidden for default agent
- **New:** `agents-panels-cron.txt` patch — Scheduler card on Cron Jobs tab now shows agent-specific job count and next-wake (`n/a` when no jobs assigned)
- **Fix:** Emoji reverting after save — `agents.update` now accepts an `emoji` param and writes `- Emoji:` to IDENTITY.md; previously wrote `- Avatar:` which was always overridden by the creation-time `- Emoji:` line
- **Fix:** Schema patch added (`schema-agents.txt`) — `AgentsUpdateParamsSchema` now includes optional `emoji` field
- **Fix:** Identity cache eviction after agent save — identity is reloaded immediately so changes are visible without refresh
- **Fix:** Chat dropdown emoji now uses `resolveAgentEmoji()` to correctly pick up IDENTITY.md emoji (not just `agent.identity.emoji`)
- **Expanded:** AGENT_EMOJIS from 60 → 103 entries across all 5 categories

### 1.2.1 (2026-02-19)
- **Critical fix:** Removed out-of-scope props and handlers from `app-render.txt` that referenced state not defined by this skill's `app-main.txt` patch — applying the previous patch would have caused TypeScript errors and runtime crashes
- **Critical fix:** Removed unused import from `app-render.txt`
- **Fix:** Replaced remaining `as any` casts in agent create handlers with typed assertions (`{ ok?: boolean; error?: string } | null`)

### 1.2.0 (2026-02-19)
- **Security:** Added Security & Transparency section to SKILL.md documenting credential access, external calls, patch scope, and LLM output validation
- **Security:** `.metadata.json` now explicitly declares `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` as optional env vars with auth resolution order documented
- **Fix:** Stripped out-of-scope state fields from `app-main.txt` that belonged to an unrelated feature
- **Hardening:** `agents.wizard` JSON parsing now performs structural validation before accepting model output — rejects non-object, missing fields, empty strings, truncated content
- **Hardening:** `name` capped to 100 chars, `emoji` to 10 chars on output to prevent oversized values
- **Metadata:** Added `capabilities` block documenting auth_profile_read, external_api_calls, and source_code_patch with mitigations

### 1.1.0 (2026-02-18)
- **Fix:** AI Wizard 401 error — OAuth token was being passed as `x-api-key`; now falls back to `api_key` profile or env var
- **Fix:** "Agent not found in config" after creation — `loadConfig` now called after `agents.create` in both Manual and Wizard paths
- **New:** Emoji picker dropdown (60 emojis, 5 categories, live preview) replaces free-text emoji input
- Patches refreshed with all fixes included

### 1.0.0 (2026-02-18)
- Initial release
- Agent selector dropdown in chat header
- Per-agent session filtering (newest-first)
- New session button (`+`) in chat header
- Create Agent panel — Manual + AI Wizard modes
- Fallback model multi-select dropdown
- Removed duplicate "Primary Model" display from Agents overview
- `agents.create` / `agents.update` / `agents.delete` / `agents.wizard` backend methods
