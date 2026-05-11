---
name: agent-team-builder
description: >
  Guide users through building a custom multi-agent team on OpenClaw — from role design
  to workspace files, routing bindings, channel configuration, and collaboration rules.
  Use this skill whenever the user mentions building an AI team, multi-agent setup,
  multi-agent collaboration, agent roles, OpenClaw team configuration, or wants to
  create multiple agents that work together. Also trigger when the user says things like
  "set up my agents", "create an agent team", "configure multi-agent", "I want multiple
  AI assistants working together", or references team coordination, agent routing,
  agent-to-agent communication, or workspace isolation in OpenClaw.
---

# Agent Team Builder for OpenClaw

Build a custom multi-agent collaboration team on OpenClaw — step by step, with correct
architecture, workspace files, routing config, and collaboration rules.

> **Important**: This skill is based on verified OpenClaw documentation (docs.openclaw.ai)
> and the official GitHub repo (github.com/openclaw/openclaw). All configuration patterns,
> file names, and architecture decisions reflect the actual OpenClaw system as of early 2026.

---

## How This Skill Works

This is an interactive, guided workflow. You walk the user through 8 phases:

1. **Team Design** — Define roles, responsibilities, and collaboration model
2. **Architecture Planning** — Single Gateway + multi-agent + channel strategy
3. **Agent & Workspace Setup** — Create agents, workspace files, identity
4. **Routing & Bindings** — Wire messages to the right agent
5. **Collaboration Rules** — Group chat strategy, mention gates, ping-pong limits
6. **Agent-to-Agent Communication** — sessions_send, sessions_spawn, allowlists
7. **Team Shared Memory** — Cross-agent knowledge sharing mechanism
8. **Memory, Operations & Delivery** — Per-agent memory, heartbeat, cost control, final config

At each phase, ask the user questions, validate their choices, then generate the
corresponding configuration and workspace files.

---

## Phase 1: Team Design

### Goal
Help the user define their agent team composition.

### Questions to Ask

1. **What is your primary use case?**
   - Personal productivity (schedule, research, writing)
   - Software development (code, review, deploy)
   - Content creation (writing, editing, publishing)
   - Business operations (strategy, analysis, execution)
   - Custom / mixed

2. **How many agents do you want?** (recommend 2–5 to start; more adds complexity)

3. **For each agent, define:**
   - `id`: short lowercase identifier (e.g., `planner`, `coder`, `writer`)
   - `name`: display name (e.g., "🧠 Planner")
   - `role`: one-sentence description of what this agent does
   - `mode`: Does it lead (orchestrator) or follow (specialist)?

4. **Do you want an orchestrator agent?**
   - An orchestrator monitors all group messages and dispatches to specialists
   - Specialists only respond when explicitly @-mentioned
   - This is the recommended pattern for 3+ agents

### Guidance

**Recommended team templates** (user can customize):

**Dev Team (4 agents)**:
- `planner` — Task decomposition, prioritization, project tracking
- `coder` — Code implementation, debugging, technical execution
- `reviewer` — Code review, quality assurance, testing
- `writer` — Documentation, commit messages, technical writing

**Content Team (3 agents)**:
- `strategist` — Content strategy, audience analysis, topic planning
- `creator` — Writing, editing, creative output
- `critic` — Quality review, fact-checking, style consistency

**Business Team (4 agents)**:
- `chief` — Overall coordination, decision synthesis
- `analyst` — Data analysis, market research, risk assessment
- `builder` — Technical implementation, automation
- `communicator` — External communication, reports, presentations

**Solo+ (2 agents)**:
- `main` — General-purpose assistant (default agent)
- `research` — Deep research, analysis, background tasks

---

## Phase 2: Architecture Planning

### Key Architecture Facts (from official docs)

Explain these to the user clearly:

1. **Single Gateway, Multiple Agents**
   - One `openclaw gateway` process hosts ALL agents
   - Each agent has its own workspace, session store, and memory index
   - Agents are defined in `agents.list[]` in `~/.openclaw/openclaw.json`
   - No need to run multiple Gateway processes

2. **Isolation is real**
   - Each agent gets: workspace directory, `agentDir` for auth/state, session transcripts under `~/.openclaw/agents/<agentId>/sessions/`, memory index database
   - **Never reuse `agentDir` across agents** — causes auth/session collisions

3. **Channel Strategy**
   Ask the user which channels they want to use:
   - **Discord**: Best for visible multi-agent group collaboration. Each agent needs its own bot account (Discord Developer Portal → one bot per agent). Enable Message Content Intent for each bot.
   - **Telegram**: Each agent needs its own bot via BotFather. Good for controlled/private channels.
   - **WhatsApp**: Each agent maps to a phone number/account. Good for personal use.
   - **Slack, Signal, iMessage, etc.**: All supported. See channel guides in docs.

4. **Discord is recommended for group collaboration** because:
   - Each bot has a visible identity in the server
   - @mention mechanics work naturally
   - Conversation threading is visible
   - Multiple bots can coexist in one guild/server

### Questions to Ask

1. Which channel(s) will you use? (can be multiple)
2. For group collaboration, which channel will be the "main stage"?
3. Do you want the same agents on multiple channels, or different agents per channel?

---

## Phase 3: Agent & Workspace Setup

### Creating Agents

For each agent, the user should run:

```bash
openclaw agents add <agent-id>
```

Or define them in `~/.openclaw/openclaw.json`:

```json5
{
  agents: {
    list: [
      { id: "planner", workspace: "~/.openclaw/workspace-planner" },
      { id: "coder", workspace: "~/.openclaw/workspace-coder" },
      { id: "reviewer", workspace: "~/.openclaw/workspace-reviewer" },
    ],
  },
}
```

### Workspace Files

Each agent's workspace follows this **standard structure** (per official docs):

| File | Purpose | Loaded When |
|------|---------|-------------|
| `AGENTS.md` | Operating instructions, memory rules, behavior priorities | Every session |
| `SOUL.md` | Persona, tone, boundaries | Every session |
| `USER.md` | Who the user is, how to address them | Every session |
| `IDENTITY.md` | Agent name, vibe, emoji (created during bootstrap) | Every session |
| `TOOLS.md` | Notes about local tools/conventions (guidance only, does NOT control tool access) | Every session |
| `HEARTBEAT.md` | Optional tiny checklist for heartbeat runs | Heartbeat only |
| `BOOT.md` | Optional startup checklist on gateway restart | Gateway start |
| `BOOTSTRAP.md` | One-time first-run ritual, deleted after completion | First run only |
| `memory/YYYY-MM-DD*.md` | Daily memory logs (append-only) | On demand |
| `MEMORY.md` | Curated long-term memory | **Private sessions only** |

> **Critical correction**: The official workspace does NOT include files named
> `ROLE-COLLAB-RULES.md`, `TEAM-RULEBOOK.md`, `TEAM-DIRECTORY.md`, or
> `GROUP_MEMORY.md` as standard OpenClaw files. These are custom additions.
> If the user wants collaboration rules, they should be embedded in `AGENTS.md`
> and `SOUL.md`, which are the files OpenClaw actually loads every session.

### Generate Workspace Files

For each agent, generate these files based on the user's team design.

**SOUL.md template** — Customize per agent:

```markdown
# Soul of [Agent Name]

## Identity
- Name: [Display Name]
- Role: [One-line role description]
- Emoji: [Emoji identifier]

## Personality
[2-3 sentences describing tone, communication style]

## Responsibilities
[Bullet list of what this agent owns]

## Boundaries
- [What this agent should NOT do]
- [When to defer to other agents]

## Private Chat Mode
[How to behave in 1:1 conversations — act as full-service expert]

## Group Chat Mode
[How to behave in group — follow team protocol, incremental contributions only]
```

**AGENTS.md template** — Customize per agent:

```markdown
# Operating Manual for [Agent Name]

## Core Behavior
- Always read IDENTITY.md and USER.md at session start
- In group chats, only respond when @-mentioned (unless you are the orchestrator)
- Write important decisions to memory/YYYY-MM-DD.md

## Memory Protocol
- Read today's and yesterday's daily log at session start
- Use memory_search for semantic recall before answering complex questions
- Write durable facts to MEMORY.md only in private sessions
- Never load MEMORY.md in group contexts

## Collaboration Protocol
- When your task is done, summarize your output clearly
- If a task is outside your role, say so and suggest which agent to @
- Never engage in back-and-forth with other agents without user involvement

## Quality Standards
[Role-specific quality requirements]
```

**IDENTITY.md template**:

```markdown
# [Agent Name]

- id: [agent-id]
- name: [Display Name]
- emoji: [Emoji]
- role: [Role description]
- capabilities: [What this agent can do]
```

---

## Phase 4: Routing & Bindings

### How Bindings Work

Bindings route inbound messages to agents. They are evaluated in order — **first match wins**.
More specific bindings should come before general ones.

Each binding matches on: `channel`, `accountId`, `chatType`, `peer`, `guild/team` IDs.

### Discord Configuration

Each Discord bot = one `accountId`. Bind each to an agent:

```json5
{
  bindings: [
    { agentId: "planner", match: { channel: "discord", accountId: "planner-bot" } },
    { agentId: "coder", match: { channel: "discord", accountId: "coder-bot" } },
    { agentId: "reviewer", match: { channel: "discord", accountId: "reviewer-bot" } },
  ],
  channels: {
    discord: {
      accounts: {
        "planner-bot": {
          token: "${DISCORD_TOKEN_PLANNER}",
          guilds: {
            "<guild-id>": {
              channels: {
                "<collab-channel-id>": { allow: true },
              },
            },
          },
        },
        "coder-bot": {
          token: "${DISCORD_TOKEN_CODER}",
          // ... similar guild/channel config
        },
        // ... other bots
      },
    },
  },
}
```

### Telegram Configuration

Each Telegram bot = one `accountId`:

```json5
{
  bindings: [
    { agentId: "planner", match: { channel: "telegram", accountId: "default" } },
    { agentId: "coder", match: { channel: "telegram", accountId: "coder" } },
  ],
  channels: {
    telegram: {
      accounts: {
        default: { botToken: "${TELEGRAM_TOKEN_PLANNER}" },
        coder: { botToken: "${TELEGRAM_TOKEN_CODER}" },
      },
    },
  },
}
```

### Questions to Ask

1. For Discord: Have you created bot accounts in the Discord Developer Portal?
2. Do you want all agents in the same guild channel, or separate channels?
3. For each agent, what's their account identifier?

---

## Phase 5: Collaboration Rules

### Group Chat Strategy

**The recommended pattern** for multi-agent group collaboration:

**Orchestrator agent**: `requireMention: false` (sees all messages)
- Monitors all group messages
- Decides when to dispatch tasks
- Does NOT respond to everything — stays silent by default, intervenes when needed

**Specialist agents**: `requireMention: true` (only responds when @-mentioned)
- Each specialist has `mentionPatterns` for reliable triggering
- Only acts when explicitly called upon

```json5
// In the orchestrator's account config:
guilds: {
  "<guild-id>": {
    channels: {
      "<channel-id>": { allow: true, requireMention: false },
    },
  },
},

// In specialist accounts:
guilds: {
  "<guild-id>": {
    channels: {
      "<channel-id>": { allow: true, requireMention: true },
    },
  },
},
```

### Mention Patterns

Configure per-agent mention patterns so users can reliably summon agents:

```json5
// Per agent in agents.list[]:
{
  id: "coder",
  groupChat: {
    mentionPatterns: ["@coder", "@engineer", "@Coder Bot"],
  },
}
```

### Agent-to-Agent Ping-Pong Limit (Group Chat Safety)

In group chat, you also want to prevent agents from endlessly replying to each other.
This is controlled by `session.agentToAgent.maxPingPongTurns` (range 0–5).
For group chat safety, set to `0` or `1`. Full agent communication setup is in Phase 6.

```json5
{
  session: {
    agentToAgent: {
      maxPingPongTurns: 1,  // 0 = no reply-back, 1 = one exchange max
    },
  },
}
```

### Group Policy

```json5
// Per channel:
channels: {
  discord: {
    groupPolicy: "allowlist",  // recommended: explicit control
    // or "open" for more permissive setups
  },
},
```

---

## Phase 6: Agent-to-Agent Communication

OpenClaw provides two primitives for inter-agent communication, both **disabled by default**.
Read `references/agent-communication.md` for full configuration details and patterns.

### Quick Summary

**1. Enable the master switch** (global, not per-agent):
```json5
{ tools: { agentToAgent: { enabled: true, allow: ["planner", "coder", "reviewer", "writer"] } } }
```

**2. Two communication primitives**:

| Primitive | Use Case | Behavior |
|-----------|----------|----------|
| `sessions_send` | Direct agent-to-agent conversation | Synchronous, supports ping-pong (0–5 turns) |
| `sessions_spawn` | Delegate task to another agent | Async, isolated session, announces result back |

**3. Per-agent allowlists** for `sessions_spawn`:
```json5
{ id: "planner", subagents: { allowAgents: ["coder", "reviewer", "writer"] } }
```

**4. Session visibility** — orchestrator needs `"all"`, specialists use default `"tree"`:
```json5
{ tools: { sessions: { visibility: "all" } } }  // For orchestrator only
```

**5. Loop detection** — always enable as safety net:
```json5
{ tools: { loopDetection: { enabled: true, detectors: { pingPong: true, genericRepeat: true } } } }
```

### Questions to Ask

1. Which agents need to talk to each other? (Draw the communication graph)
2. Synchronous exchanges (`sessions_send`) or async delegation (`sessions_spawn`)?
3. Should the orchestrator spawn tasks to ALL other agents?
4. Max ping-pong turns? (0 = safest, 2 = practical, 5 = max)

---

## Phase 7: Team Shared Memory

Each agent has its own isolated workspace and memory. There is **no built-in
cross-agent shared memory**. Read `references/team-shared-memory.md` for full
implementation details, setup scripts, and file templates.

### The Design

Create a shared directory symlinked into every agent's workspace:

```
~/.openclaw/team-shared/           ← Single source of truth
├── TEAM-KNOWLEDGE.md              ← Durable facts, preferences, quality standards
├── TEAM-DECISIONS.md              ← Decision log with date/context/rationale
├── TEAM-STATUS.md                 ← Current priorities, active tasks, blockers
├── TEAM-DIRECTORY.md              ← Agent IDs, session keys, mention patterns
└── projects/
    ├── INDEX.md                   ← Registry of all active projects
    └── <project-name>.md          ← Per-project context doc

~/.openclaw/workspace-planner/team-shared → symlink to above
~/.openclaw/workspace-coder/team-shared   → symlink to above
~/.openclaw/workspace-reviewer/team-shared → symlink to above
```

### Quick Setup

```bash
mkdir -p ~/.openclaw/team-shared/projects
# Create shared files (see references/team-shared-memory.md for templates)
# Then symlink into each workspace:
for agent in planner coder reviewer writer; do
  ln -s ~/.openclaw/team-shared ~/.openclaw/workspace-$agent/team-shared
done
```

### Why This Pattern

- All agents read/write via `memory_get` and file tools — no special API needed
- Changes by one agent are immediately visible to others on next turn
- **Not auto-loaded** into bootstrap — avoids prompt cache invalidation on every update
- Agents read on demand per AGENTS.md instructions, keeping token costs low

### AGENTS.md Rules (Add to Every Agent)

```markdown
## Team Shared Memory Protocol
- Before significant tasks: read team-shared/TEAM-STATUS.md
- After completing tasks: update TEAM-STATUS.md with outcome
- For team decisions: append to TEAM-DECISIONS.md with date + rationale
- For project work: read/update team-shared/projects/<project>.md
- NEVER write private user information to team-shared files
```

### Memory Search Limitation

`memory_search` only indexes the current agent's workspace. Symlinked dirs may not
be indexed. Use `memory_get` (targeted file read) for shared files — it always works.

---

## Phase 8: Memory, Operations & Delivery

### Memory Architecture

OpenClaw's memory is **file-based Markdown** with semantic search.

**Two standard layers** (per official docs):

1. **Daily logs** (`memory/YYYY-MM-DD.md`) — append-only, day-to-day decisions and context
2. **Long-term memory** (`MEMORY.md`) — curated durable facts, **only loaded in private sessions**

**Memory tools available to agents**:
- `memory_search` — semantic recall over indexed snippets (hybrid BM25 + vector search)
- `memory_get` — targeted read of a specific file/line range

> **Critical correction**: The article mentions `GROUP_MEMORY.md` as a standard file.
> This is NOT a standard OpenClaw workspace file. The official approach is:
> - `MEMORY.md` loads only in private/main sessions (never in groups)
> - Group chats have their own isolated session state
> - For cross-session context sharing, use a `projects/` directory pattern
>   with self-contained docs readable from any session

### Memory Configuration

```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
        },
      },
      memorySearch: {
        enabled: true,
        // Auto-selects: local → OpenAI → Gemini → BM25 fallback
      },
    },
  },
}
```

### Cost Control Tips

1. **Model tiering**: Use expensive models (Opus) for the orchestrator, cheaper models (Sonnet/Haiku) for specialists
2. **Heartbeat budget**: Keep HEARTBEAT.md short to avoid token burn
3. **Bootstrap file limits**: Default `bootstrapMaxChars: 20000` per file, `bootstrapTotalMaxChars: 150000` total
4. **Memory flush**: Enable auto-flush before compaction to preserve context

```json5
{
  agents: {
    list: [
      {
        id: "planner",
        model: { primary: "anthropic/claude-sonnet-4-20250514" },
      },
      {
        id: "coder",
        model: { primary: "anthropic/claude-sonnet-4-20250514" },
      },
    ],
  },
}
```

### Per-Agent Tool Policies

Each agent can have its own tool allow/deny list:

```json5
{
  id: "coder",
  tools: {
    allow: ["exec", "read", "write", "edit", "apply_patch", "browser"],
    deny: ["cron"],
  },
  sandbox: {
    mode: "all",
    scope: "agent",
  },
}
```

---

## Phase 9: Generate & Deliver

After collecting all information, generate:

1. **`openclaw.json`** — Complete configuration (see `references/openclaw-team-example.json5` for full template)
2. **Workspace files** — SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md for each agent
3. **Team shared directory** — TEAM-KNOWLEDGE.md, TEAM-DECISIONS.md, TEAM-STATUS.md, TEAM-DIRECTORY.md
4. **Symlink setup script** — Creates `team-shared/` symlinks in every workspace
5. **Setup script** — Shell commands to create agents, wire channels, verify
6. **Quick-start guide** — How to test the team

### Verification Commands

```bash
# List all agents and their bindings
openclaw agents list --bindings

# Check channel connectivity
openclaw channels status --probe

# Validate configuration
openclaw doctor

# Restart gateway to apply changes
openclaw gateway restart
```

---

## Common Corrections & Pitfalls

When guiding users, proactively correct these common misconceptions:

### Architecture Misconceptions

1. **"Each agent needs its own Gateway process"** → Wrong. One Gateway hosts all agents.
   Multiple agents share the same server process and config file.

2. **"Workspaces are sandboxed by default"** → Wrong. Agents can access other host
   locations via absolute paths unless `sandbox` is explicitly enabled per-agent.

3. **"TOOLS.md controls tool access"** → Wrong. TOOLS.md is guidance text only.
   Actual tool access is controlled by `agents.list[].tools.allow/deny` in config.

### File Name Misconceptions

4. **Custom files like `ROLE-COLLAB-RULES.md`, `TEAM-RULEBOOK.md`, `GROUP_MEMORY.md`**
   → These are NOT standard OpenClaw files. Put collaboration rules in `AGENTS.md`
   and `SOUL.md` which are loaded every session. Custom files won't auto-load.

5. **"MEMORY.md loads everywhere"** → Wrong. MEMORY.md only loads in private/main
   sessions, never in group contexts. This is a privacy protection.

### Routing Misconceptions

6. **"bindings map `channel + accountId → agentId`"** → Partially correct but
   oversimplified. Bindings can match on channel, accountId, chatType, peer (kind + id),
   and guild/team IDs. They are evaluated in order, first match wins.

7. **"You need N×M bindings for N agents × M channels"** → Not necessarily. You can
   use channel-wide defaults and only add specific bindings for exceptions.

### Collaboration Misconceptions

8. **"agentToAgent ping-pong set to 0 means agents can't communicate"** → It means
   agents can't do reply-back ping-pong via `sessions_send`. They can still use
   `sessions_spawn` for sub-agent tasks, and the orchestrator can still @-mention
   others in group chats.

9. **"Discord is the only platform for multi-agent collaboration"** → Any channel works.
   Discord is convenient because each bot has visible identity and @mention is natural.
   Feishu, Slack, and others support similar patterns.

---

## Reference: Official Workspace File List

From docs.openclaw.ai/concepts/agent-workspace:

- `AGENTS.md` — Operating instructions (loaded every session)
- `SOUL.md` — Persona, tone, boundaries (loaded every session)
- `USER.md` — User profile (loaded every session)
- `IDENTITY.md` — Agent name/emoji (created during bootstrap)
- `TOOLS.md` — Tool notes, guidance only (loaded every session)
- `HEARTBEAT.md` — Heartbeat checklist (optional)
- `BOOT.md` — Startup checklist (optional)
- `BOOTSTRAP.md` — First-run ritual (deleted after completion)
- `memory/YYYY-MM-DD*.md` — Daily memory logs
- `MEMORY.md` — Long-term memory (private sessions only)
- `skills/` — Workspace-specific skills

For the complete multi-agent reference, read:
- `references/architecture-corrections.md` — Common misconceptions and corrections
- `references/openclaw-team-example.json5` — Full example configuration file
