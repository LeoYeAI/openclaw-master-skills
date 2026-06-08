# OpenClaw Multi-Agent Routing Reference

## Table of Contents

- [Overview](#overview)
- [What Is One Agent](#what-is-one-agent)
- [CLI Commands](#cli-commands)
- [Quick Start](#quick-start)
- [Routing Rules](#routing-rules)
- [Bindings](#bindings)
- [Per-Agent Configuration](#per-agent-configuration)
- [Examples](#examples)

## Overview

Multi-agent routing lets one Gateway serve multiple isolated agent personalities, each with its own workspace, sessions, model config, and channel bindings.

## What Is One Agent

Each agent has:
- **Workspace**: files, AGENTS.md, SOUL.md, USER.md, persona rules
- **State directory** (`agentDir`): auth profiles, model registry, per-agent config at `~/.openclaw/agents/<agentId>/agent/`
- **Session store**: chat history + routing state at `~/.openclaw/agents/<agentId>/sessions`
- **Skills**: per-agent skills in `agentDir/skills/` or shared from `~/.openclaw/skills`

## CLI Commands

```bash
openclaw agents add <id>            # Create new agent
openclaw agents list                # List agents
openclaw agents list --bindings     # Show agent-channel bindings
openclaw agents delete <id>         # Remove agent
```

## Quick Start

1. Create agent workspaces:

```bash
openclaw agents add coding
openclaw agents add social
```

2. Create channel accounts (one bot per agent for Discord/Telegram):

```bash
openclaw channels login --channel whatsapp --account work
openclaw channels add --channel telegram --account social --token $TOKEN
```

3. Add agents, accounts, and bindings to config:

```json5
{
  agents: {
    list: [
      {
        id: "coding",
        workspace: "~/.openclaw/workspace-coding",
      },
      {
        id: "social",
        workspace: "~/.openclaw/workspace-social",
      },
    ],
  },
  bindings: [
    {
      agentId: "coding",
      match: { channel: "telegram", accountId: "coding" },
    },
    {
      agentId: "social",
      match: { channel: "telegram", accountId: "social" },
    },
  ],
}
```

4. Restart and verify:

```bash
openclaw gateway restart
openclaw agents list --bindings
openclaw channels status --probe
```

## Routing Rules

Messages pick an agent via bindings (matched first → wins):

- **channel** — match channel name
- **accountId** — match channel account
- **peer.kind** — `"direct"` (DM) or `"group"`
- **peer.id** — specific sender/group ID
- **Default**: unmatched messages → `agents.defaults` (single-agent fallback)

## Bindings

```json5
{
  bindings: [
    // All Telegram "alerts" account → alert agent
    { agentId: "alerts", match: { channel: "telegram", accountId: "alerts" } },
    // Specific WhatsApp DM → personal agent
    {
      agentId: "alex",
      match: {
        channel: "whatsapp",
        peer: { kind: "direct", id: "+15551230001" },
      },
    },
    // Specific WhatsApp group → family agent
    {
      agentId: "family",
      match: {
        channel: "whatsapp",
        peer: { kind: "group", id: "group-jid@g.us" },
      },
    },
  ],
}
```

## Per-Agent Configuration

Each agent can override:
- Model (primary + fallbacks)
- Tools (profile, allow, deny)
- Sandbox settings
- Group chat mention patterns
- Heartbeat settings

```json5
{
  agents: {
    list: [{
      id: "support",
      workspace: "~/.openclaw/workspace-support",
      model: { primary: "anthropic/claude-sonnet-4-5" },
      tools: {
        profile: "messaging",
        allow: ["slack"],
      },
      groupChat: {
        mentionPatterns: ["@support"],
      },
    }],
  },
}
```

## Examples

### WhatsApp Daily Chat + Telegram Deep Work

```json5
{
  agents: {
    list: [
      { id: "daily", workspace: "~/.openclaw/workspace-daily" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "daily", match: { channel: "whatsapp" } },
    { agentId: "work", match: { channel: "telegram" } },
  ],
}
```

### Same Channel, Specific Peer Gets Different Model

```json5
{
  agents: {
    list: [
      { id: "main" },
      { id: "opus", model: { primary: "anthropic/claude-opus-4-6" } },
    ],
  },
  bindings: [
    {
      agentId: "opus",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+1555VIP" } },
    },
  ],
}
```

### Multiple Gateways on One Host

Each needs unique port, config, and state:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```
