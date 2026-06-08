---
name: openclaw
description: Comprehensive guide for installing, configuring, operating, and troubleshooting OpenClaw — a self-hosted, multi-channel AI agent gateway. Use when the user asks about OpenClaw setup, configuration, channel management (WhatsApp/Telegram/Discord/Slack/iMessage/etc.), model provider setup, Gateway operations, multi-agent routing, security hardening, troubleshooting, or any maintenance task related to their local OpenClaw installation. Also use when encountering errors from `openclaw` CLI commands or the Gateway daemon.
---

# OpenClaw Maintenance Skill

OpenClaw is a self-hosted, open-source (MIT) gateway that routes AI agents across WhatsApp, Telegram, Discord, Slack, iMessage, Signal, and 15+ other channels simultaneously. It runs on macOS, Linux, or Windows.

## Reference Files

| Reference | Coverage |
|---|---|
| [channels.md](references/channels.md) | Per-channel setup (WhatsApp, Telegram, Discord, etc.) |
| [channel_troubleshooting.md](references/channel_troubleshooting.md) | Per-channel failure signatures and walkthroughs |
| [tools.md](references/tools.md) | Tools inventory (profiles, groups, all built-in tools) |
| [exec.md](references/exec.md) | Exec tool: parameters, config, PATH, security, process tool |
| [exec_approvals.md](references/exec_approvals.md) | Exec approvals: allowlists, safe bins, approval flow |
| [browser.md](references/browser.md) | Browser tool: profiles, CDP, relay, SSRF, Control API |
| [web_tools.md](references/web_tools.md) | Web tools: Brave, Perplexity, Gemini search providers |
| [pdf_tool.md](references/pdf_tool.md) | PDF tool: native/fallback modes, config, page filtering |
| [elevated.md](references/elevated.md) | Elevated mode: /elevated directives, sandbox breakout |
| [lobster.md](references/lobster.md) | Lobster: typed workflow runtime with approvals |
| [llm_task.md](references/llm_task.md) | LLM Task: JSON-only LLM step for structured output |
| [openprose.md](references/openprose.md) | OpenProse: multi-agent program runtime |
| [plugins.md](references/plugins.md) | Plugins: official list, config, manifest, CLI, authoring |
| [skills.md](references/skills.md) | Skills: locations, config, ClawHub, watcher, token impact |
| [providers.md](references/providers.md) | Model provider setup |
| [multi_agent.md](references/multi_agent.md) | Multi-agent routing |
| [nodes.md](references/nodes.md) | Nodes (iOS/Android/macOS/headless) |
| [security.md](references/security.md) | Security hardening |
| [secrets.md](references/secrets.md) | Secrets management (SecretRef, vault) |
| [sandboxing.md](references/sandboxing.md) | Sandboxing (Docker isolation) |
| [config_reference.md](references/config_reference.md) | Full config field reference |
| [gateway_ops.md](references/gateway_ops.md) | Gateway operations |
| [remote_access.md](references/remote_access.md) | Remote access, SSH, Tailscale, web dashboard |
| [sessions.md](references/sessions.md) | Session management, DM isolation, lifecycle, compaction |
| [hooks.md](references/hooks.md) | Hooks: internal event hooks, HTTP webhooks, authoring, CLI |
| [automation.md](references/automation.md) | Cron jobs, webhooks, Gmail Pub/Sub |
| [acp_agents.md](references/acp_agents.md) | ACP agents: spawn external AI runtimes (Codex, Claude, etc.) |
| [install.md](references/install.md) | Installation, updating, rollback, migration, uninstall |
| [web_ui.md](references/web_ui.md) | Web surfaces: Dashboard, Control UI, WebChat |
| [slash_commands.md](references/slash_commands.md) | Chat slash commands (/new, /model, /acp, etc.) |
| [platforms.md](references/platforms.md) | Platform-specific guides (macOS, iOS, Android, Linux, Windows) |
| [diffs_firecrawl.md](references/diffs_firecrawl.md) | Diffs plugin + Firecrawl anti-bot fallback |
| [subagents.md](references/subagents.md) | Sub-agents: nested spawning, thread binding, announce, tool policy |
| [memory.md](references/memory.md) | Memory system, vector search, hybrid BM25, compaction, QMD backend |
| [architecture.md](references/architecture.md) | Gateway architecture, wire protocol, pairing, invariants |
| [agent_runtime.md](references/agent_runtime.md) | Agent runtime, bootstrap files, agent loop, hooks, timeouts |
| [streaming.md](references/streaming.md) | Streaming + chunking: block streaming, coalescing, preview modes |
| [queue.md](references/queue.md) | Command queue: modes (steer/followup/collect), concurrency, per-session |
| [model_failover.md](references/model_failover.md) | Model failover, OAuth, auth profiles, cooldowns, billing disables |
| [clawhub.md](references/clawhub.md) | ClawHub: public skill registry, CLI commands, publish/install |
| [thinking.md](references/thinking.md) | Thinking levels, verbose directives, reasoning visibility |
| [polls.md](references/polls.md) | Polls: Telegram, WhatsApp, Discord, MS Teams |
| [voice.md](references/voice.md) | Talk Mode (voice interaction) + Voice Wake (wake words) |
| [presence_discovery.md](references/presence_discovery.md) | Presence system, discovery (Bonjour/Tailscale), transports |
| [gateway_internals.md](references/gateway_internals.md) | Network model, gateway lock, health checks, doctor, logging, background exec |
| [heartbeat.md](references/heartbeat.md) | Heartbeat: config, delivery, visibility, HEARTBEAT.md, per-agent |
| [bonjour.md](references/bonjour.md) | Bonjour/mDNS: TXT keys, wide-area DNS-SD, debugging, failure modes |
| [pairing.md](references/pairing.md) | Gateway pairing: node approval, CLI, API, auto-approval, storage |
| [tui.md](references/tui.md) | TUI: keyboard shortcuts, slash commands, pickers, local shell, delivery |
| [media.md](references/media.md) | Media: camera capture, images, audio/voice notes, transcription |
| [channel_routing.md](references/channel_routing.md) | Channel routing, session keys, agent selection, Mattermost, BlueBubbles |



## Quick Reference

### Key Paths

| Path | Purpose |
|---|---|
| `~/.openclaw/openclaw.json` | Main config (JSON5) |
| `~/.openclaw/.env` | Global env fallback |
| `~/.openclaw/workspace` | Default agent workspace |
| `~/.openclaw/agents/<id>/` | Per-agent state + sessions |
| `~/.openclaw/skills/` | Managed/local skills |
| `~/.openclaw/agents/<id>/qmd/` | QMD memory backend state |
| `~/.openclaw/agents/<id>/agent/auth-profiles.json` | Auth profiles + OAuth tokens |
| `OPENCLAW_CONFIG_PATH` | Override config location |
| `OPENCLAW_STATE_DIR` | Override state directory |
| `OPENCLAW_HOME` | Override home directory |

### Essential Commands

```
openclaw status                    # Overall status
openclaw gateway status            # Gateway daemon status
openclaw gateway status --deep     # Deep scan including system services
openclaw doctor                    # Diagnose config/service issues
openclaw doctor --fix              # Auto-fix safe issues
openclaw logs --follow             # Tail gateway logs
openclaw channels status --probe   # Channel health check
openclaw security audit            # Security posture check
openclaw security audit --fix      # Auto-fix security issues
openclaw update                    # Self-update
openclaw dashboard                 # Open Control UI in browser
openclaw tui                       # Terminal UI (interactive REPL)
openclaw agent                     # Direct agent interaction via CLI
openclaw health                    # Health check
openclaw usage                     # Usage tracking
openclaw config validate           # Validate config file
openclaw config file               # Print active config path
openclaw sessions cleanup          # Session disk cleanup
openclaw agents bindings           # Agent-channel bindings
openclaw agents bind               # Bind agent to account
openclaw agents unbind             # Unbind agent
openclaw update --dry-run          # Preview update
openclaw system presence           # View connected clients/nodes
openclaw system heartbeat last     # Last heartbeat info
openclaw system heartbeat now      # Trigger heartbeat immediately
openclaw memory search <query>     # CLI memory search
openclaw docs <query>              # Search OpenClaw docs
openclaw nodes pending             # List pending pairing requests
openclaw nodes approve <id>        # Approve node pairing
openclaw nodes status              # Show all paired nodes
openclaw health --json             # Full health snapshot (JSON)
openclaw message send --media <p>  # Send media message
```

### Default Gateway

- Bind: `127.0.0.1:18789` (loopback)
- Dashboard: `http://127.0.0.1:18789/`
- Protocol: WebSocket (JSON text frames)

## Core Workflow

### Diagnosing Issues

Always follow this command ladder:

1. `openclaw status` — quick overview
2. `openclaw gateway status` — daemon running? RPC probe ok?
3. `openclaw logs --follow` — watch for errors
4. `openclaw doctor` — config/service diagnostics
5. `openclaw channels status --probe` — per-channel health

### Starting / Restarting Gateway

```bash
# Foreground with verbose logging
openclaw gateway --port 18789 --verbose

# Force-kill existing listener then start
openclaw gateway --force

# Service management (launchd on macOS, systemd on Linux)
openclaw gateway install
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
```

### Configuration

Edit config via any method:

```bash
# Interactive wizard
openclaw onboard                    # Full setup
openclaw configure                  # Config wizard

# CLI one-liners
openclaw config get <path>          # Read value
openclaw config set <path> <value>  # Set value (JSON5 or raw string)
openclaw config unset <path>        # Remove value

# Direct edit
# Edit ~/.openclaw/openclaw.json (JSON5 format)
# Gateway hot-reloads on save (if gateway.reload.mode != "off")
```

Minimal config example:

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

### Channel Setup

For detailed per-channel setup, see [references/channels.md](references/channels.md).
For per-channel troubleshooting (failure signatures, setup walkthroughs), see [references/channel_troubleshooting.md](references/channel_troubleshooting.md).
For plugins adding new channels (Matrix, Nostr, MS Teams, etc.), see [references/plugins.md](references/plugins.md).

Quick channel add:

```bash
# Interactive wizard
openclaw channels add

# Non-interactive
openclaw channels add --channel telegram --account default --name "My Bot" --token $BOT_TOKEN
openclaw channels login --channel whatsapp     # QR pairing for WhatsApp
openclaw channels status --probe               # Verify
```

### Model Provider Setup

For detailed provider setup, see [references/providers.md](references/providers.md).

```bash
# Set default model
openclaw models set anthropic/claude-sonnet-4-5

# List available models
openclaw models list --all

# Check auth/token status
openclaw models status --probe

# Add auth interactively
openclaw models auth add
```

Config example:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["openai/gpt-5.2"],
      },
    },
  },
}
```

### Multi-Agent Routing

For detailed multi-agent config, see [references/multi_agent.md](references/multi_agent.md).

```bash
openclaw agents add <id>                # Create agent
openclaw agents list --bindings         # Show agent-channel bindings
openclaw agents delete <id>             # Remove agent
```

### Nodes (iOS / Android / macOS / Headless)

For detailed node setup, see [references/nodes.md](references/nodes.md).

```bash
openclaw nodes status                   # List connected nodes
openclaw nodes describe --node <id>     # Node capabilities
openclaw devices list                   # Pending device approvals
openclaw devices approve <requestId>    # Approve a device
openclaw node run --host <host> --port 18789  # Start headless node host
```

### Security

For detailed security hardening, see [references/security.md](references/security.md).
For secrets management (SecretRef, vault integration), see [references/secrets.md](references/secrets.md).
For sandboxing (Docker isolation for tools), see [references/sandboxing.md](references/sandboxing.md).
For full config field reference, see [references/config_reference.md](references/config_reference.md).
For remote access (SSH, Tailscale, VPN), see [references/remote_access.md](references/remote_access.md).

```bash
openclaw security audit                 # Check posture
openclaw security audit --deep          # Live gateway probe
openclaw security audit --fix           # Auto-fix safe issues
openclaw secrets reload                 # Re-resolve secret refs
openclaw secrets audit                  # Scan for plaintext leaks
```

### Update / Uninstall

For detailed installation, updating, rollback, and migration guide, see [references/install.md](references/install.md).

```bash
# Install (recommended)
curl -fsSL https://openclaw.ai/install.sh | bash

# Update
openclaw update                    # Self-update command
# Or: npm install -g openclaw@latest
openclaw doctor                    # Run after update to apply migrations

# Uninstall
openclaw uninstall
```

## Tools Reference

For detailed per-tool documentation, see [references/tools.md](references/tools.md).

For specific tools, see:
- [references/exec.md](references/exec.md) — Exec tool deep-dive
- [references/exec_approvals.md](references/exec_approvals.md) — Exec approvals and allowlists
- [references/browser.md](references/browser.md) — Browser automation deep-dive
- [references/web_tools.md](references/web_tools.md) — Web search/fetch with multiple providers
- [references/lobster.md](references/lobster.md) — Lobster workflow runtime
- [references/llm_task.md](references/llm_task.md) — LLM Task for structured JSON output
- [references/openprose.md](references/openprose.md) — OpenProse multi-agent programs
- [references/plugins.md](references/plugins.md) — Plugin system (install, author, distribute)
- [references/skills.md](references/skills.md) — Skills system (load, config, ClawHub)

For ACP agents (Codex, Claude Code, Gemini CLI, etc.), see [references/acp_agents.md](references/acp_agents.md).
For Diffs plugin and Firecrawl anti-bot fallback, see [references/diffs_firecrawl.md](references/diffs_firecrawl.md).
For chat slash commands (/new, /model, /acp, etc.), see [references/slash_commands.md](references/slash_commands.md).
For thinking levels (/think, /verbose, /reasoning), see [references/thinking.md](references/thinking.md).
For polls (Telegram, WhatsApp, Discord, MS Teams), see [references/polls.md](references/polls.md).
For Talk Mode and Voice Wake, see [references/voice.md](references/voice.md).
For Gateway architecture and wire protocol, see [references/architecture.md](references/architecture.md).
For agent runtime and loop details, see [references/agent_runtime.md](references/agent_runtime.md).
For command queue system, see [references/queue.md](references/queue.md).
For model failover and OAuth, see [references/model_failover.md](references/model_failover.md).
For ClawHub skill registry, see [references/clawhub.md](references/clawhub.md).
For presence and discovery, see [references/presence_discovery.md](references/presence_discovery.md).
For streaming and chunking, see [references/streaming.md](references/streaming.md).
For Gateway internals (network model, lock, health, doctor, logging), see [references/gateway_internals.md](references/gateway_internals.md).
For heartbeat system, see [references/heartbeat.md](references/heartbeat.md).
For Bonjour/mDNS discovery details, see [references/bonjour.md](references/bonjour.md).
For Gateway node pairing, see [references/pairing.md](references/pairing.md).
For Terminal UI (TUI), see [references/tui.md](references/tui.md).
For media (camera, images, audio), see [references/media.md](references/media.md).
For channel routing and session keys, see [references/channel_routing.md](references/channel_routing.md).

**Tool profiles**: `minimal`, `coding`, `messaging`, `full` (default).

**Tool groups** (for allow/deny):
- `group:runtime` — exec, bash, process
- `group:fs` — read, write, edit, apply_patch
- `group:sessions` — sessions_list/history/send/spawn, session_status
- `group:memory` — memory_search, memory_get
- `group:web` — web_search, web_fetch
- `group:ui` — browser, canvas
- `group:automation` — cron, gateway
- `group:messaging` — message
- `group:nodes` — nodes
- `group:openclaw` — all built-in OpenClaw tools (excludes provider plugins)

## Common Failure Signatures

| Error | Cause | Fix |
|---|---|---|
| `refusing to bind gateway ... without auth` | Non-loopback bind without token | Set `gateway.auth.token` or `gateway.auth.password` |
| `another gateway instance is already listening` / `EADDRINUSE` | Port conflict | `openclaw gateway --force` or change port |
| `Gateway start blocked: set gateway.mode=local` | Local mode not enabled | Set `gateway.mode="local"` |
| `unauthorized` / reconnect loop | Token/password mismatch | Check `OPENCLAW_GATEWAY_TOKEN` or config auth |
| `device identity required` | Missing device auth | Ensure client completes connect.challenge flow |
| No replies from bot | Pairing/allowlist/mention gating | Check `openclaw pairing list`, DM policy, mention patterns |
| `Embedding provider authentication failed (401)` | `.env` has placeholder API key (e.g. `your-jina-api-key-here`) | Replace with real API key in `~/.openclaw/.env`, restart Gateway |
| `config change requires gateway restart (plugins.*)` | Plugin config changes can't hot-reload | Full `openclaw gateway restart` or `launchctl kickstart -k` |
| `Bootstrap failed: 5: Input/output error` | LaunchAgent plist in stale/stuck state | `openclaw gateway install` then `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway` |
| `Missing env var "X" referenced at config path: ...` | `.env` missing or variable not defined | Add variable to `~/.openclaw/.env` and restart Gateway |

## Environment Variables

| Variable | Purpose |
|---|---|
| `OPENCLAW_GATEWAY_TOKEN` | Gateway auth token |
| `OPENCLAW_GATEWAY_PASSWORD` | Gateway auth password |
| `OPENCLAW_GATEWAY_PORT` | Override gateway port |
| `OPENCLAW_CONFIG_PATH` | Override config file path |
| `OPENCLAW_STATE_DIR` | Override state directory |
| `OPENCLAW_HOME` | Override home directory |
| `OPENCLAW_LOAD_SHELL_ENV` | Import shell env (set to `1`) |
| `OPENCLAW_VERBOSE` | Verbose logging |
| `OPENCLAW_LOG_FILE` | File logging path |
| `OPENCLAW_LOG_LEVEL` | Log level control |
| `OPENCLAW_SHELL` | Set by OpenClaw in exec/acp/tui runtimes |
| `BRAVE_API_KEY` | For web_search tool |
| `FIRECRAWL_API_KEY` | For Firecrawl anti-bot fallback |
| `ELEVENLABS_API_KEY` | For Talk Mode TTS |
| `ELEVENLABS_VOICE_ID` | Default voice for Talk Mode |
| `CLAWHUB_TOKEN` | ClawHub API token for CI/automation |
| `CLAWHUB_WORKDIR` | ClawHub working directory override |
| `OLLAMA_API_KEY` | For Ollama embeddings provider |

