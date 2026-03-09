---
name: compaction-ui
version: 2.3.0
description: "Background memory compaction with auto-trigger, chat summary paragraph, configurable threshold, model selector, settings tab, and result storage for OpenClaw Control UI."
---

# Compaction UI v2.1.0

Memory compaction system for the OpenClaw Control UI — background execution with toast notifications, auto-trigger at configurable token thresholds, conversation summary paragraphs in compacted output, dedicated settings tab with model selector, and result history.

## Status: ✅ Active

| Component | Status |
|-----------|--------|
| Context Gauge Button | ✅ Working |
| Background Compaction (toast) | ✅ Working |
| Auto-Compaction Trigger | ✅ Working |
| Conversation Summary Paragraph | ✅ Working |
| Settings Tab (plugin-registered) | ✅ Working |
| Model Selector | ✅ Working |
| Last Result Storage + Viewer | ✅ Working |
| Settings Persistence & Reload | ✅ Working |
| Auth Hierarchy (OAuth > API > Fallback) | ✅ Working |
| Chat History Filters | ✅ Working |
| Full Background Isolation (no chat interference) | ✅ Working |

## Features

### 1. Context Gauge Button (`app-render.helpers.ts`)

A circular SVG progress ring in the chat toolbar that doubles as the manual compact trigger.

- **Placement:** After session selector dropdown in `renderChatControls()`
- **Data source:** `sessionsResult.sessions[].totalTokens` and `contextTokens` from session rows
- **Colors:** Green (<60%), Yellow (60-85%), Red (≥85%)
- **Disabled:** When utilization <20% or during active compaction
- **Tooltip:** Shows "Context: XK / YK tokens (Z%)"

### 2. Background Compaction (Toast)

On click (or auto-trigger), compaction runs in the background using the standard bottom-right toast system — **no blocking modal**. The UI remains fully interactive.

- **Running toast:** Shows "Memory Compaction" with spinner
- **Complete toast:** Shows "Compacted: XK → YK" with checkmark (auto-dismisses after 5s)
- **Error toast:** Shows failure message (auto-dismisses after 5s)
- Uses `backgroundJobToasts` system consistent with all other background processes (cron, knowledge extraction, etc.)

### 3. Auto-Compaction

After every chat response (`final` event), the UI checks token usage against the configured threshold. If exceeded:

- Background compaction triggers automatically
- Toast shows "Auto-Compacting (X%)" with the current utilization
- 5-minute debounce prevents repeated triggers
- Chat refreshes automatically after successful compaction
- Silent toast removal if nothing was compacted

### 4. Conversation Summary Paragraph

Every compaction output now begins with a `## Conversation Summary` section **before** the structured `## Goal` section. This is a 3-6 sentence natural language paragraph that:

- Describes the overall topic(s) of the conversation
- Explains the flow of discussion and key transitions
- Summarizes how the conversation progressed
- Written in past tense as a narrative overview

**Implementation:** Custom instructions are injected into the upstream compaction LLM call via `compact.ts`. The instruction is prepended to any user-provided custom instructions (from `/compact [instructions]`), so both coexist.

**Example output:**
```
## Conversation Summary
The conversation began with the user requesting improvements to the compaction
system, specifically moving from a blocking modal to background toasts. Discussion
then shifted to adding a settings tab with auto-compaction controls. After
implementing and testing those features, the user noticed settings weren't
persisting across tab navigations, which led to a fix for the module-level
state cache. Finally, the user requested adding a narrative summary paragraph
to the compaction output for better context.

## Goal
...
```

### 5. Settings Tab (Plugin-Registered)

A dedicated Compaction tab under the **Agent** navigation group, registered via the Plugin UI architecture.

**Registration:** `plugins-ui.ts` → `BUILTIN_UI_VIEWS` with `id: "compaction"`, `group: "agent"`, `position: 7`, `icon: "archive"`

**Cards:**

#### Auto-Compaction Card
- **Toggle:** Enable/disable automatic compaction
- **Threshold slider:** 10% to 95% (default: 60%)
- **Color-coded:** Green (<60%), Yellow (60-85%), Red (≥85%)

#### Model Card
- **Dropdown:** Select a specific model for compaction or use session default
- **Grouped by provider** with context window sizes shown
- **Warning callout** when custom model selected (API key reminder)
- **Fallback:** If custom model fails, automatically falls back to session default

#### Result Storage Card
- **Toggle:** Opt-in to save the compacted summary text for review

#### Last Compaction Card
- **Before/After:** Large styled token counts in a 2-column grid
- **Stats:** Tokens saved, percent reduction, trigger type, timestamp, session key
- **View Results:** Expandable summary viewer (when storage is enabled)
- **Clear:** Reset stored result
- **Hint:** Shows "Enable Store Results" message when storage is off

**State Management:**
- Module-level state persists across re-renders within a session
- Settings reload from backend every time the tab is visited (2-second staleness threshold)
- `resetCompactionSettingsState()` exported for tests and tab switches

### 6. Auth Hierarchy

Compaction uses `resolveApiKeyForProvider` via `getApiKeyForModel` — the same auth chain as chat:

**OAuth → API Key → Fallback**

No separate configuration needed. If OAuth (Claude Max) is configured as the primary auth profile, compaction uses it automatically. Custom model selection uses this same auth chain independently.

### 7. Result Storage

When enabled, the most recent compaction result is persisted to `{agentDir}/compaction-config.json`:

```json
{
  "settings": {
    "autoEnabled": true,
    "autoThresholdPercent": 60,
    "storeLastResult": true,
    "compactionModel": "anthropic/claude-sonnet-4-6"
  },
  "lastResult": {
    "timestamp": 1709283600000,
    "trigger": "manual",
    "tokensBefore": 50614,
    "tokensAfter": 4766,
    "tokensSaved": 45848,
    "percentReduction": 91,
    "sessionKey": "agent:main:main",
    "summary": "## Conversation Summary\nThe conversation focused on...\n\n## Goal\n..."
  }
}
```

When storage is disabled, metadata (timestamps, token counts) is still saved but the summary text is omitted.

### 8. Chat History Filters

- **NO_REPLY/HEARTBEAT_OK filtering:** Skips assistant messages with these exact texts
- **Compaction divider:** Renders labeled divider line for `__openclaw.kind === "compaction"` messages

## Architecture

### Backend RPCs

| Method | Description |
|--------|-------------|
| `sessions.compact` | Execute compaction (records result after completion) |
| `compaction.getSettings` | Read settings from config file |
| `compaction.saveSettings` | Update settings (threshold auto-clamped 10-95%) |
| `compaction.getLastResult` | Get stored last compaction result |
| `compaction.clearLastResult` | Clear stored result |

### Files Modified

| File | Purpose |
|------|---------|
| `src/gateway/server-methods/compaction.ts` | Settings RPCs, config I/O, result recording |
| `src/gateway/server-methods/sessions.ts` | `sessions.compact` RPC (records result after compaction) |
| `src/gateway/server-methods/plugins-ui.ts` | Plugin view registration |
| `src/gateway/server-methods.ts` | Handler wiring |
| `src/gateway/server-methods-list.ts` | Method registration |
| `src/gateway/method-scopes.ts` | Scope registration |
| `src/agents/pi-embedded-runner/compact.ts` | Chat summary instruction injection |
| `ui/src/ui/app-render.helpers.ts` | Context gauge + background toast trigger |
| `ui/src/ui/app-gateway.ts` | Auto-compaction check after final event |
| `ui/src/ui/views/compaction-settings.ts` | Settings tab view |
| `ui/src/ui/app-render.ts` | View wiring + import |
| `ui/src/ui/views/chat.ts` | Chat history filters |

### Config File

`{agentDir}/compaction-config.json` — per-agent, created on first settings save.

### Plugin Registration

The compaction tab is registered as a builtin plugin view in `plugins-ui.ts`:

```typescript
{
  id: "compaction",
  label: "Compaction",
  subtitle: "Memory Management",
  icon: "archive",
  group: "agent",
  position: 7,
  pluginId: "compaction-ui",
}
```

## Known Gotchas

- **Settings not persisting across tab visits:** Fixed in v2.1.0. The module-level `_state.loaded` flag was preventing reloads. Now reloads every 2 seconds when re-entering the tab.
- **Model selector requires API keys:** If you select a custom model, make sure the provider's API key is configured. The UI shows a warning callout.
- **Compaction model format:** Must be `"provider/model"` format (e.g. `"anthropic/claude-sonnet-4-6"`). Invalid formats are silently ignored and fall back to session default.
- **parentId skip-set propagation must be message-only:** When filtering memory flush messages from `readSessionMessages`, the skip set must ONLY propagate through entries with a `message` field. Non-message protocol entries (`type:"custom"`) bridge between logical turns — if their IDs enter the skip set, the entire remaining conversation gets hidden. The fix: only check `parsed?.message` entries against the skip set, and only add their IDs to it.
- **No blocking modal — ever:** The gauge button in `app-render.helpers.ts` must NEVER render a full-screen overlay modal. Compaction is a background process; all status is communicated via the bottom-right toast system. Remove any `position:fixed; inset:0` overlay conditioned on `compactState.phase`. The button may show a spinner icon while running, but must not block the UI.

## Changelog

### v2.1.0
- **Conversation summary paragraph:** Compaction output now starts with a `## Conversation Summary` narrative paragraph before structured sections
- **Model selector:** Choose a specific model for compaction or use session default, with provider-grouped dropdown
- **Settings reload fix:** Tab now reloads settings from backend every 2s instead of caching forever
- **Reference files updated:** Synced `references/` with current source

### v2.0.0
- **Background compaction:** Replaced blocking full-screen modal with background job toast
- **Auto-compaction:** Triggers after chat response when token usage exceeds threshold (configurable, default 60%, 5-minute debounce)
- **Settings tab:** Plugin-registered Compaction tab under Agent nav group
- **Result recording:** `sessions.compact` records before/after token counts and optional summary
- **Auth hierarchy:** Same OAuth → API → Fallback chain as chat
- **Settings RPCs:** `compaction.getSettings`, `compaction.saveSettings`, `compaction.getLastResult`, `compaction.clearLastResult`

### v1.0.0
- Initial release: Context gauge button, blocking modal with animated phases, `sessions.compact` RPC with LLM summarization, chat history NO_REPLY/HEARTBEAT_OK filtering, compaction divider lines
