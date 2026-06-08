# OpenClaw Slash Commands Reference

## Table of Contents

- [Overview](#overview)
- [Command List](#command-list)
- [Model Selection](#model-selection)
- [Config Updates](#config-updates)
- [Debug Overrides](#debug-overrides)
- [Usage Surfaces](#usage-surfaces)
- [Configuration](#configuration)

## Overview

Slash commands are in-chat commands that control agent behavior, session management, and configuration. They are processed by the Gateway before reaching the model.

## Command List

### Session Management

| Command | Description |
|---|---|
| `/new` | Start a fresh session (clears context) |
| `/new <model>` | Start fresh session with specific model |
| `/reset` | Alias for `/new` |
| `/stop` | Abort current run + clear queued followups |
| `/restart` | Restart gateway |
| `/compact` | Summarize older context to free window space |
| `/compact <instructions>` | Compact with specific focus instructions |

### Status & Inspection

| Command | Description |
|---|---|
| `/status` | Show agent status, context usage, WhatsApp cred freshness |
| `/context list` | List what's in system prompt + injected files |
| `/context detail` | Detailed view of context contributors |
| `/help` | Show available commands |
| `/commands` | List all available commands |
| `/whoami` | Show current agent identity |

### Model & Thinking

| Command | Description |
|---|---|
| `/model` | Show current model |
| `/model <alias>` | Switch to model by alias |
| `/model <provider/model>` | Switch to specific model |
| `/model <provider>` | Switch to provider (fuzzy match) |
| `/thinking <level>` | Set thinking level (off/minimal/low/medium/high/xhigh) |
| `/fast` | Toggle fast mode (lower latency) |
| `/reasoning` | Show reasoning/thinking output |
| `/verbose` | Toggle verbose output mode |

### Send Policy

| Command | Description |
|---|---|
| `/send on` | Allow sending for this session |
| `/send off` | Deny sending for this session |
| `/send inherit` | Clear override, use config rules |

### Skills & Context

| Command | Description |
|---|---|
| `/skill <name>` | Run a specific skill |
| `/context` | Show context information |
| `/btw <question>` | Ask a side question without affecting main context |

### Execution & Tools

| Command | Description |
|---|---|
| `/elevated on\|ask\|full\|off` | Control elevated mode |
| `/exec` | Execute command directly |
| `/bash` | Open shell session |
| `/tts off\|always\|inbound\|tagged\|status\|provider\|limit\|summary\|audio` | Text-to-speech control |
| `/activation` | Manage activation settings |
| `/queue` | View/manage command queue |

### ACP (Agent Communication Protocol)

| Command | Description |
|---|---|
| `/acp spawn <agent>` | Spawn ACP session |
| `/acp cancel` | Cancel current ACP turn |
| `/acp steer <instructions>` | Nudge ACP session |
| `/acp close` | Close ACP session |
| `/acp status` | ACP runtime status |
| `/acp sessions` | List active ACP sessions |
| `/acp model <id>` | Change ACP model |
| `/acp permissions <profile>` | Set ACP permissions |
| `/acp timeout <seconds>` | Set ACP timeout |
| `/acp doctor` | Diagnose ACP setup |

### Sub-agents

| Command | Description |
|---|---|
| `/subagents list` | List active sub-agent sessions |
| `/subagents kill <id\|#\|all>` | Stop a sub-agent (or all) + cascade to children |
| `/subagents log <id\|#> [limit] [tools]` | View sub-agent transcript |
| `/subagents info <id\|#>` | Detailed sub-agent info |
| `/subagents send <id\|#> <message>` | Send message to sub-agent |
| `/subagents steer <id\|#> <message>` | Nudge sub-agent without replacing context |
| `/subagents spawn <agentId> <task>` | Spawn new sub-agent (one-shot mode) |

### Thread & Focus

| Command | Description |
|---|---|
| `/focus <target>` | Bind current thread to a sub-agent/session target |
| `/unfocus` | Remove thread binding for current bound thread |
| `/agents` | List active runs and binding state (`thread:<id>` or `unbound`) |
| `/session idle <duration\|off>` | Set/inspect inactivity auto-unfocus |
| `/session max-age <duration\|off>` | Set/inspect hard cap age |

### Configuration & Debug

| Command | Description |
|---|---|
| `/config show` | Show current config |
| `/config get <path>` | Get config value |
| `/config set <path> <value>` | Set config value |
| `/config unset <path>` | Remove config value |
| `/mcp show` | Show MCP configuration |
| `/mcp get <path>` | Get MCP config value |
| `/mcp set <path> <value>` | Set MCP config value |
| `/mcp unset <path>` | Remove MCP config value |
| `/plugins list` | List installed plugins |
| `/plugins show <name>` | Show plugin details |
| `/plugins enable <name>` | Enable a plugin |
| `/plugins disable <name>` | Disable a plugin |
| `/debug show` | Show debug state |
| `/debug set <key> <value>` | Set debug option |
| `/debug unset <key>` | Remove debug option |
| `/debug reset` | Reset all debug options |

### Other

| Command | Description |
|---|---|
| `/version` | Show OpenClaw version |

## Model Selection

`/model` accepts:
- **Alias**: names from `agents.defaults.models` (e.g., "Sonnet", "GPT")
- **Provider/model**: full model ID (e.g., `anthropic/claude-sonnet-4-5`)
- **Provider name**: fuzzy-matched provider (e.g., "anthropic")

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "openai/gpt-5.2": { alias: "GPT" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
}
```

## Config Updates

Some slash commands can modify runtime config:
- `/model` changes the session's active model
- `/thinking` changes the thinking level for the session
- `/verbose` toggles verbose mode
- `/send` changes send policy for the session

These are **session-scoped** overrides; they don't persist to `openclaw.json`.

## Debug Overrides

For debugging:
- `/verbose` toggles showing reasoning/thinking blocks in replies
- `/thinking off` disables extended thinking for faster responses
- `/context detail` reveals the biggest context contributors

## Usage Surfaces

| Surface | Supports Slash Commands |
|---|---|
| WhatsApp | ✅ |
| Telegram | ✅ |
| Discord | ✅ |
| Slack | ✅ |
| Control UI / WebChat | ✅ |
| iMessage | ✅ |
| Signal | ✅ |

**Note**: Some commands may behave differently per channel (e.g., thread-related commands only on thread-supporting channels).

## Configuration

Enable/disable individual commands:

```json5
{
  commands: {
    // Disable specific commands
    restart: false,    // Disable gateway restart from chat
  },
}
```

Stop phrases (abort triggers): `stop`, `stop action`, `stop run`, `stop openclaw` — these are standalone messages that abort the current run.

Reset triggers can be customized:

```json5
{
  session: {
    resetTriggers: ["/new", "/reset"],
  },
}
```
