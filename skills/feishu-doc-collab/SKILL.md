---
name: feishu-doc-collab
description: |
  Enable real-time AI collaboration in Feishu (Lark) documents. When a user edits a Feishu doc,
  the agent automatically detects the change, reads the document, and responds inline —
  turning any Feishu document into a live human-AI conversation.

  Features:
  - Feishu document edit event → triggers isolated agent session automatically
  - Structured in-doc chat protocol (status flags prevent premature AI responses while user is still typing)
  - Multi-party support: multiple humans + multiple AI agents in one document
  - Bitable (spreadsheet) task board integration for collaborative task management
  - Anti-loop: bot's own edits are automatically ignored

  Triggers: Feishu doc collaboration, 飞书文档协作, document edit event, in-doc chat, 文档内对话,
  Lark document AI, feishu doc auto-reply, 飞书文档自动回复
---

# Feishu Document Collaboration Skill

Turn any Feishu document into a real-time human-AI collaboration space.

## Overview

This skill patches OpenClaw's Feishu extension to detect document edit events and trigger
isolated agent sessions. Combined with a structured in-document chat protocol, it enables:

- ✍️ Write a question in a Feishu doc → AI reads it and appends a reply
- 🚦 Status flags (🔴 editing / 🟢 done) prevent premature responses
- 👥 Multi-party routing: messages can target specific participants
- 📋 Optional Bitable task board for structured task management

## Prerequisites

1. **OpenClaw with Feishu channel configured** (app ID, app secret, event subscriptions)
2. **Feishu app event subscriptions enabled:**
   - `drive.file.edit_v1` — document edit events
   - `drive.file.bitable_record_changed_v1` — (optional) bitable record changes
3. **Hooks enabled** in `openclaw.json`:
   ```json
   {
     "hooks": {
       "enabled": true,
       "token": "your-hooks-token-here"
     }
   }
   ```

## Quick Setup

### Step 1: Enable hooks in openclaw.json

Add the `hooks` section if not present:

```bash
# Generate a random token
TOKEN=$(openssl rand -hex 16)
echo "Your hooks token: $TOKEN"
# Then add to openclaw.json:
# "hooks": { "enabled": true, "token": "<TOKEN>" }
```

### Step 2: Apply the monitor patch

```bash
bash ./skills/feishu-doc-collab/scripts/patch-monitor.sh
```

This patches `monitor.ts` in the Feishu extension to:
- Detect `drive.file.edit_v1` events
- Trigger an isolated agent session via `/hooks/agent`
- The agent reads the doc, checks for new messages, and responds

### Step 3: Configure your agent identity

Edit `./skills/feishu-doc-collab/config.json`:

```json
{
  "agent_name": "MyBot",
  "agent_display_name": "My AI Assistant"
}
```

The patch script uses this to set up message routing (who the agent responds as).

### Step 4: Restart the gateway

```bash
openclaw gateway restart
```

### Step 5: Set up the Doc Chat Protocol

Copy the protocol template to your workspace:

```bash
cp ./skills/feishu-doc-collab/assets/DOC_PROTOCOL_TEMPLATE.md ./DOC_PROTOCOL.md
```

Edit `DOC_PROTOCOL.md` to fill in your participant roster.

## How It Works

### Document Edit Flow

```
User edits Feishu doc
        ↓
Feishu sends drive.file.edit_v1 event
        ↓
Patched monitor.ts receives event
        ↓
Checks: is this the bot's own edit? → Yes: skip (anti-loop)
        ↓ No
POST /hooks/agent with isolated session instructions
        ↓
Agent reads DOC_PROTOCOL.md for message format
        ↓
Agent reads the document, finds last message block
        ↓
Checks: status=🟢? addressed to me? not from me?
        ↓ Yes
Agent composes reply and appends to document
```

### In-Document Chat Protocol

Messages in the document follow this format:

```markdown
---
> **Sender Name** → **Receiver Name** | 🟢 完成

Your message content here.
```

**Status flags:**
- 🔴 编辑中 (editing) — AI will NOT process this message (user is still typing)
- 🟢 完成 (done) — AI will read and respond to this message

**Routing:**
- `→ AgentName` — addressed to a specific AI agent
- `→ all` — broadcast to all participants

This solves a critical problem: Feishu auto-saves continuously while typing, which would
trigger multiple premature AI responses without the status flag mechanism.

### Bitable Task Board (Optional)

For structured task management alongside document collaboration:

1. Create a Bitable with these fields:
   - Task Summary (Text)
   - Status (SingleSelect): Unread / Read / In Progress / Done / N/A
   - Created (DateTime)
   - From (SingleSelect): participant names
   - To (MultiSelect): participant names
   - Priority (SingleSelect): Low / Medium / High / Urgent
   - Notes (Text)
   - Related Doc (URL)

2. Configure in `config.json`:
   ```json
   {
     "bitable": {
       "app_token": "your_bitable_app_token",
       "table_id": "your_table_id"
     }
   }
   ```

3. The patch also handles `bitable_record_changed_v1` events for task routing.

## Re-applying After Updates

**⚠️ OpenClaw updates overwrite `monitor.ts`.** After any update:

```bash
bash ./skills/feishu-doc-collab/scripts/patch-monitor.sh
openclaw gateway restart
```

The patch script is idempotent — safe to run multiple times.

## Configuration Reference

### config.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_name` | string | Yes | Internal name used in protocol routing |
| `agent_display_name` | string | Yes | Display name shown in doc replies |
| `bitable.app_token` | string | No | Bitable app token for task board |
| `bitable.table_id` | string | No | Bitable table ID for task board |

### Environment

The patch reads from `~/.openclaw/openclaw.json`:
- `hooks.token` — authentication for /hooks/agent endpoint
- `gateway.port` — gateway port (default: 18789)

## Known Issues & Solutions

### Event Storm (事件风暴)

**Problem:** Feishu sends multiple `drive.file.edit_v1` and `bitable_record_changed_v1` events
for a single logical edit. Bitable edits are especially bad — changing one record field can trigger
10-20+ events in rapid succession. Without debounce, each event spawns a separate isolated agent
session (using the full model), causing massive token waste.

**Real-world impact:** A single bitable task edit triggered 15+ Hook sessions consuming 350k+ tokens,
all running in parallel and all reaching the same conclusion: "nothing to do".

**Solution:** 30-second debounce per fileToken (implemented in patch-monitor.sh v2):
- A `Map<string, number>` tracks the last trigger timestamp per file/table
- If the same file was triggered within 30 seconds, the event is silently skipped
- For bitable events, the debounce key includes both fileToken and tableId
- The debounce is applied **before** the `/hooks/agent` call, so no session is created

**Bot self-edit loop:** When the agent updates a bitable record (e.g., changing status to "处理完"),
that edit triggers MORE events. The bot self-edit check (comparing `operator_id` to `botOpenId`)
catches most of these, but the debounce provides a critical safety net for cases where the
operator ID doesn't match (e.g., API calls vs. bot identity).

**Important:** Already-running sessions cannot be stopped by debounce. If an event storm has
already started, the sessions will run to completion. Debounce only prevents NEW triggers.

### Re-patching After Updates

OpenClaw updates overwrite `monitor.ts`. After any update:
```bash
bash ./skills/feishu-doc-collab/scripts/patch-monitor.sh
openclaw gateway restart
```
The patch script is idempotent — checks for both `/hooks/agent` and `_editDebounce` markers.

## Limitations

- Requires patching OpenClaw source files (fragile across updates)
- Feishu app needs `drive.file.edit_v1` event subscription approval
- Document must use the structured protocol format for reliable routing
- Works best with docx type; other file types (sheets, slides) are not supported

## Credits

Created by dongwei. Inspired by the need for real-time human-AI collaboration
in Chinese enterprise workflows using Feishu/Lark.

## License

MIT
