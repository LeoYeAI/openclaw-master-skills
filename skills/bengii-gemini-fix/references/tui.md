# TUI (Terminal UI) Reference

> Source: https://docs.openclaw.ai/web/tui

## Quick Start

```bash
openclaw gateway                                      # 1. Start Gateway
openclaw tui                                          # 2. Open TUI
# Type a message and press Enter                      # 3. Chat

# Remote Gateway
openclaw tui --url ws://<host>:<port> --token <token>
# or --password <password>
```

## What You See

| Area | Content |
|---|---|
| **Header** | Connection URL, current agent, current session |
| **Chat log** | User messages, assistant replies, system notices, tool cards |
| **Status line** | Connection/run state (connecting, running, streaming, idle, error) |
| **Footer** | Connection state + agent + session + model + think/verbose/reasoning + token counts + deliver |
| **Input** | Text editor with autocomplete |

## Mental Model: Agents + Sessions

- **Agents**: unique slugs (e.g., `main`, `research`). Gateway exposes the list.
- **Sessions**: belong to the current agent. Keys: `agent:<agentId>:<sessionKey>`.
- `/session main` → expands to `agent:<currentAgent>:main`
- `/session agent:other:main` → switch to that agent session explicitly
- **Session scope**:
  - `per-sender` (default): each agent has many sessions
  - `global`: TUI always uses global session

## Sending + Delivery

- Messages sent to the Gateway; delivery to providers is **off by default**.
- Turn on: `/deliver on` | Settings panel | `openclaw tui --deliver`

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Enter` | Send message |
| `Esc` | Abort active run |
| `Ctrl+C` | Clear input (twice to exit) |
| `Ctrl+D` | Exit |
| `Ctrl+L` | Model picker |
| `Ctrl+G` | Agent picker |
| `Ctrl+P` | Session picker |
| `Ctrl+O` | Toggle tool output expansion |
| `Ctrl+T` | Toggle thinking visibility (reloads history) |

## Slash Commands

| Command | Description |
|---|---|
| `/help` | Help |
| `/status` | Status |
| `/agent <id>` / `/agents` | Switch/list agents |
| `/session <key>` / `/sessions` | Switch/list sessions |
| `/model <provider/model>` / `/models` | Switch/list models |
| `/think <off\|minimal\|low\|medium\|high>` | Set thinking level |
| `/verbose <on\|full\|off>` | Set verbose mode |
| `/reasoning <on\|off\|stream>` | Set reasoning visibility |
| `/usage <off\|tokens\|full>` | Set usage display |
| `/elevated <on\|off\|ask\|full>` | Set elevated mode |
| `/activation <mention\|always>` | Set activation mode |
| `/deliver <on\|off>` | Toggle delivery |
| `/new` / `/reset` | Reset session |
| `/abort` | Abort active run |
| `/settings` | Settings overlay |
| `/exit` | Exit TUI |

## Local Shell Commands

- Prefix a line with `!` to run a local shell command on the TUI host.
- TUI prompts once per session to allow local execution.
- Commands run in a fresh, non-interactive shell in the TUI working directory.
- Receive `OPENCLAW_SHELL=tui-local` in environment.
- A lone `!` is sent as a normal message.

## Tool Output

- Tool calls show as cards with args + results.
- `Ctrl+O` toggles collapsed/expanded views.
- While tools run, partial updates stream into the same card.

## Terminal Colors

- TUI keeps assistant text in terminal's default foreground (dark + light compatible).
- `OPENCLAW_THEME=light` when auto-detection is wrong on light terminals.
- `OPENCLAW_THEME=dark` to force dark palette.

## Options

| Flag | Description |
|---|---|
| `--url <url>` | Gateway WebSocket URL |
| `--token <token>` | Gateway token |
| `--password <password>` | Gateway password |
| `--session <key>` | Session key (default: `main` or `global`) |
| `--deliver` | Deliver replies to provider (default: off) |
| `--thinking <level>` | Override thinking level |
| `--timeout-ms <ms>` | Agent timeout in ms |

## Connection Details

- TUI registers with Gateway as `mode: "tui"`.
- Reconnects show system message; event gaps surfaced in log.

## See Also

- [web_ui.md](web_ui.md) — WebChat, Control UI, Dashboard
- [slash_commands.md](slash_commands.md) — Full slash command reference
- [thinking.md](thinking.md) — Thinking levels and verbose
