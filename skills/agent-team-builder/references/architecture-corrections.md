# Architecture Corrections: Common Misconceptions in OpenClaw Multi-Agent Setups

This reference documents corrections to commonly circulated claims about OpenClaw
multi-agent architecture, verified against official documentation (docs.openclaw.ai)
and the GitHub source (github.com/openclaw/openclaw) as of March 2026.

---

## 1. OpenClaw Is Not Primarily a "Multi-Agent Collaboration Framework"

**Common claim**: OpenClaw is built for multi-agent team collaboration.

**Reality**: OpenClaw is a **personal AI assistant** framework. Multi-agent is a
supported capability for isolating different use cases (work vs personal, different
tool policies, different models), not primarily designed as a "team of agents
working together." The official description is:

> "A personal AI assistant you run on your own devices."

Multi-agent support exists to let multiple people share one Gateway, to separate
concerns (e.g., a coding agent vs a messaging agent), or to use different models
for different tasks. Group collaboration between agents is possible but is an
advanced, user-configured pattern — not the default use case.

---

## 2. Workspace File Inventory

### Standard Files (per docs.openclaw.ai/concepts/agent-workspace)

| File | Auto-created | Loaded | Purpose |
|------|-------------|--------|---------|
| AGENTS.md | Yes (setup) | Every session | Operating instructions, memory rules |
| SOUL.md | Yes (setup) | Every session | Persona, tone, boundaries |
| USER.md | Yes (setup) | Every session | User profile |
| IDENTITY.md | Yes (bootstrap) | Every session | Agent name, emoji |
| TOOLS.md | Yes (setup) | Every session | Tool guidance (NOT access control) |
| HEARTBEAT.md | Yes (setup) | Heartbeat runs | Tiny checklist |
| BOOT.md | Optional | Gateway restart | Startup tasks |
| BOOTSTRAP.md | Yes (first run) | Once, then deleted | Onboarding ritual |
| MEMORY.md | Created by agent | **Private sessions only** | Long-term curated memory |
| memory/YYYY-MM-DD*.md | Created by agent | On demand | Daily logs |
| skills/ | User-created | Skill triggers | Workspace-specific skills |

### NOT Standard OpenClaw Files

These are custom inventions sometimes seen in blog posts — they will NOT be
automatically loaded by OpenClaw:

- `ROLE-COLLAB-RULES.md` — Put this content in AGENTS.md instead
- `TEAM-RULEBOOK.md` — Put this content in AGENTS.md instead
- `TEAM-DIRECTORY.md` — Put this content in AGENTS.md instead
- `GROUP_MEMORY.md` — Not a standard file; MEMORY.md already has group/private scoping

If you create custom .md files in the workspace, the agent CAN read them with
`memory_get` or file tools, but they are NOT automatically loaded into the session
context the way AGENTS.md, SOUL.md, USER.md, and IDENTITY.md are.

---

## 3. Bindings: More Than channel + accountId → agentId

**Common oversimplification**: Bindings map `channel + accountId` to `agentId`.

**Full picture**: Each binding has a `match` object that can include:

- `channel` — Which messaging platform
- `accountId` — Which bot account on that channel
- `chatType` — "direct" or "group"
- `peer.kind` + `peer.id` — Specific sender/group matching
- Guild/team IDs — For Discord guilds, Slack teams

Bindings are evaluated **in order** — first match wins. More specific bindings
(peer matches) should come before general ones (channel-wide).

When no binding matches, the **default agent** handles the message.

Example of a peer-specific binding:
```json5
{
  agentId: "vip-handler",
  match: {
    channel: "whatsapp",
    peer: { kind: "direct", id: "+15551234567" },
  },
}
```

---

## 4. Agent-to-Agent Communication

### sessions_send (ping-pong)

- Controlled by `session.agentToAgent.maxPingPongTurns` (range: 0–5)
- After the ping-pong, the target agent runs an **announce** step
- Reply `REPLY_SKIP` to stop ping-pong early; reply `ANNOUNCE_SKIP` to suppress announcement
- Setting to 0 prevents reply-back but doesn't prevent all inter-agent communication

### sessions_spawn (sub-agents)

- Sub-agents are background workers spawned from a conversation
- They run in their own isolated session
- Post results back to the requester when done
- Controlled by per-agent allowlists: `agents.list[].subagents.allowAgents`

### Loop Detection

OpenClaw has built-in loop detection (since v2026.x):

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      warningThreshold: 10,
      criticalThreshold: 20,
      detectors: {
        genericRepeat: true,      // Same tool + same params
        knownPollNoProgress: true, // Polling with no changes
        pingPong: true,            // A/B/A/B patterns
      },
    },
  },
}
```

---

## 5. MEMORY.md Scoping

**Critical fact**: MEMORY.md is **only loaded in the main, private session**.
It is never loaded in group contexts. This is an intentional privacy protection.

For information that needs to be accessible across sessions (including groups,
crons, sub-agents), use a `projects/` directory pattern with self-contained
docs that agents can read via `memory_get` or file tools.

The concept of a separate `GROUP_MEMORY.md` is a user invention, not an
OpenClaw standard. Group chats have their own isolated session state, and
any durable information should be written to daily logs or project docs.

---

## 6. TOOLS.md Does NOT Control Tool Access

**Common misconception**: Writing tool rules in TOOLS.md restricts what the agent can do.

**Reality**: TOOLS.md is "notes about your local tools and conventions. Does not
control tool availability; it is only guidance." (Official docs)

Actual tool access is controlled by:
- `agents.list[].tools.allow` — Explicit allow list
- `agents.list[].tools.deny` — Explicit deny list
- `agents.defaults.tools` — Default policy for all agents
- `tools.profile` — Preset profiles like "messaging" (restrictive)

---

## 7. Sandbox Is NOT Default

Workspaces are **not sandboxed by default**. Tools resolve relative paths against
the workspace, but absolute paths can still reach anywhere on the host.

To enable sandboxing:
```json5
{
  agents: {
    list: [{
      id: "coder",
      sandbox: {
        mode: "all",     // or "non-main"
        scope: "agent",  // or "session"
      },
    }],
  },
}
```

---

## 8. dmScope Configuration

For multi-agent setups where different people might DM different bots:

- `session.dmScope: "main"` (default) — All DMs share one session. Fine for single user.
- `session.dmScope: "per-channel-peer"` — Each channel+sender pair gets isolated context. **Recommended for shared setups.**
- `session.dmScope: "per-account-channel-peer"` — Also isolates by account. Best for multi-account inboxes.

**Security warning**: Without proper dmScope, all users sharing a bot can see
each other's conversation context.

---

## 9. Discord vs Other Channels

**Claim**: "Only Discord works for multi-agent collaboration."

**Reality**: Any channel supports multi-agent routing. Discord is convenient because:
- Each bot has a distinct visible identity in the server
- @mention mechanics are native and intuitive
- Multiple bots coexist naturally in channels
- Message Content Intent gives bots access to all messages

But Slack, Feishu, Telegram groups, and others all support multi-agent patterns.
The key requirement is: one bot account per agent on the chosen channel.

---

## 10. Configuration File Location

The main config file is `~/.openclaw/openclaw.json` (JSON5 format).

It is NOT called `config.yaml` or `openclaw.config.json` (though project-specific
overrides via `openclaw.config.json` in a project directory are supported for merging).

Edit via CLI:
```bash
openclaw config set <key> <value>
openclaw config show
openclaw doctor  # validate config
```
