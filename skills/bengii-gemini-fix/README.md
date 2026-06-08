# OpenClaw Agent Skill 🦞

[中文文档](README_CN.md) | English

A comprehensive **Agent Skill** for installing, configuring, operating, and troubleshooting [OpenClaw](https://github.com/openclaw/openclaw) — a self-hosted, multi-channel AI agent gateway.

## What is This?

This is an Agent Skill designed for AI coding assistants (like Claude with Antigravity). Once installed, the AI assistant gains deep knowledge of OpenClaw and can help you with:

- 🔧 **Installation & Updates** — Install, upgrade, or migrate OpenClaw
- ⚙️ **Configuration** — Edit `openclaw.json`, set up models, manage secrets
- 📡 **Channel Management** — Set up WhatsApp, Telegram, Discord, Slack, iMessage, and 15+ other channels
- 🚀 **Gateway Operations** — Start, stop, restart, health check, remote access
- 🤖 **Multi-Agent Routing** — Configure multiple agents with isolated workspaces and sessions
- 🔒 **Security Hardening** — Audit, lock down access, manage tokens and secrets
- 🔍 **Troubleshooting** — Diagnose and fix common errors from CLI and Gateway

## Skill Structure

```
OpenClaw-Skill/
├── SKILL.md                     # Main entry (core workflows, commands, troubleshooting)
└── references/              
    ├── architecture.md          # Gateway architecture, wire protocol, pairing, invariants
    ├── agent_runtime.md         # Agent runtime, bootstrap, agent loop, hooks, timeouts
    ├── bonjour.md               # Bonjour/mDNS: TXT keys, wide-area DNS-SD, debugging
    ├── channel_routing.md       # Channel routing, session keys, Mattermost, BlueBubbles
    ├── channels.md              # 20+ channel setup guides (WhatsApp, Telegram, Discord, etc.)
    ├── clawhub.md               # ClawHub public skill registry, CLI commands
    ├── gateway_internals.md     # Network model, lock, health, doctor, logging, background exec
    ├── gateway_ops.md           # Gateway operations, service management
    ├── heartbeat.md             # Heartbeat: config, delivery, visibility, HEARTBEAT.md
    ├── media.md                 # Media: camera capture, images, audio/voice notes, transcription
    ├── memory.md                # Memory system, vector search, hybrid BM25, QMD backend
    ├── model_failover.md        # Model failover, OAuth, auth profiles, cooldowns
    ├── multi_agent.md           # Multi-agent routing, bindings, per-agent config
    ├── pairing.md               # Gateway pairing: node approval, CLI, API, auto-approval
    ├── polls.md                 # Polls (Telegram, WhatsApp, Discord, MS Teams)
    ├── presence_discovery.md    # Presence system, discovery (Bonjour/Tailscale)
    ├── providers.md             # 20+ model providers (Anthropic, OpenAI, Ollama, etc.)
    ├── queue.md                 # Command queue: steer/followup/collect modes
    ├── security.md              # Auth, access control, hardening baseline
    ├── streaming.md             # Block streaming, chunking, coalescing, preview modes
    ├── thinking.md              # Thinking levels, verbose directives, reasoning visibility
    ├── tui.md                   # TUI: keyboard shortcuts, slash commands, pickers, local shell
    ├── voice.md                 # Talk Mode (voice interaction) + Voice Wake (wake words)
    └── ... (51 reference files total)
```

**Total: ~5,500+ lines** of structured reference covering all core OpenClaw functionality.

## Installation

### For Antigravity (Claude)

Copy the skill folder to your Antigravity skills directory:

```bash
# Clone this repo
git clone https://github.com/win4r/OpenClaw-Skill.git

# Copy to your skills directory
cp -r OpenClaw-Skill ~/.gemini/antigravity/skills/openclaw
```

The skill will be automatically detected and triggered when you ask about OpenClaw-related tasks.

### For Other AI Assistants

The `SKILL.md` and `references/` files contain structured documentation that can be adapted for any AI assistant that supports skill/knowledge injection.

## Usage Examples

Once installed, just ask naturally:

| What You Say | What the AI Does |
|---|---|
| "Help me upgrade OpenClaw" | Runs `npm install -g openclaw@latest`, `openclaw doctor`, restarts Gateway, verifies |
| "Set up a Telegram bot" | Walks through bot creation, token setup, config, and verification |
| "Gateway is not responding" | Runs diagnostic command ladder: status → logs → doctor → channels probe |
| "Lock down my OpenClaw security" | Runs security audit, applies hardened baseline, fixes permissions |
| "Add a second agent for work" | Creates agent, sets up workspace, configures bindings, restarts |
| "EADDRINUSE error" | Identifies port conflict, runs `openclaw gateway --force` or changes port |

## Key Commands Quick Reference

```bash
# Status & Health
openclaw status                    # Overall status
openclaw gateway status            # Gateway daemon status
openclaw doctor                    # Diagnose issues
openclaw channels status --probe   # Channel health

# Gateway Management
openclaw gateway install           # Install as system service
openclaw gateway start/stop/restart

# Configuration
openclaw config get <path>         # Read config value
openclaw config set <path> <value> # Set config value
openclaw configure                 # Interactive wizard

# Security
openclaw security audit            # Check security posture
openclaw security audit --fix      # Auto-fix issues
openclaw secrets reload            # Reload secret refs

# Channels
openclaw channels add              # Add channel (wizard)
openclaw channels login            # WhatsApp QR pairing
openclaw channels list             # Show configured channels

# Models
openclaw models set <model>        # Set default model
openclaw models status --probe     # Check auth status
```

## Documentation Source

This skill is built from the official [OpenClaw Documentation](https://docs.openclaw.ai/), covering:

- [Install](https://docs.openclaw.ai/install)
- [Gateway Architecture](https://docs.openclaw.ai/concepts/architecture)
- [Agent Runtime](https://docs.openclaw.ai/concepts/agent)
- [Agent Loop](https://docs.openclaw.ai/concepts/agent-loop)
- [Configuration](https://docs.openclaw.ai/gateway/configuration)
- [Channels](https://docs.openclaw.ai/channels)
- [Model Providers](https://docs.openclaw.ai/providers)
- [Model Failover & OAuth](https://docs.openclaw.ai/concepts/model-failover)
- [Tools](https://docs.openclaw.ai/tools)
- [Thinking Levels](https://docs.openclaw.ai/tools/thinking)
- [Command Queue](https://docs.openclaw.ai/concepts/queue)
- [Streaming & Chunking](https://docs.openclaw.ai/concepts/streaming)
- [Memory & Vector Search](https://docs.openclaw.ai/concepts/memory)
- [ClawHub Registry](https://docs.openclaw.ai/tools/clawhub)
- [Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent)
- [Talk Mode & Voice Wake](https://docs.openclaw.ai/nodes/talk)
- [Polls](https://docs.openclaw.ai/automation/poll)
- [Presence & Discovery](https://docs.openclaw.ai/concepts/presence)
- [ACP Agents](https://docs.openclaw.ai/pi)
- [Security](https://docs.openclaw.ai/gateway/security)
- [Troubleshooting](https://docs.openclaw.ai/gateway/troubleshooting)
- [CLI Reference](https://docs.openclaw.ai/cli)

## License

This skill is provided as-is for use with AI assistants. OpenClaw itself is [MIT licensed](https://github.com/openclaw/openclaw/blob/main/LICENSE).

## Contributing

Issues and PRs welcome! If OpenClaw releases new features or changes, feel free to update the reference files accordingly.
