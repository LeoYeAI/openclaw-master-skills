# Agent Council

Complete toolkit for creating and managing autonomous AI agents with Discord integration for [OpenClaw](https://openclaw.ai).

## Features

**Agent Creation:**
- Autonomous agent architecture with self-contained workspaces
- SOUL.md personality system
- Memory management (hybrid architecture with daily logs)
- Discord channel bindings
- Automatic gateway configuration
- Optional cron job setup

**Discord Channel Management:**
- Create Discord channels via API
- Configure OpenClaw gateway allowlists
- Set channel-specific system prompts
- Rename channels and update references
- Optional workspace file search

## Installation

### Prerequisites
- [OpenClaw](https://openclaw.ai) installed and configured
- Node.js/npm via nvm (for OpenClaw)
- Discord bot with "Manage Channels" permission (optional)
- Python 3.6+ (standard library only)

### Install Skill

```bash
# Clone the repo
git clone https://github.com/itsahedge/agent-council.git
cd agent-council

# Copy to OpenClaw skills directory
cp -r . ~/.openclaw/skills/agent-council/

# Enable skill in config
openclaw gateway config.patch --raw '{
  "skills": {
    "entries": {
      "agent-council": {"enabled": true}
    }
  }
}'
```

## Quick Start

### Create an Agent

```bash
~/.openclaw/skills/agent-council/scripts/create-agent.sh \
  --name "Watson" \
  --id "watson" \
  --emoji "🔬" \
  --specialty "Research and analysis specialist" \
  --model "anthropic/claude-opus-4-5" \
  --workspace "$HOME/agents/watson" \
  --discord-channel "1234567890"
```

### Create a Discord Channel

```bash
python3 ~/.openclaw/skills/agent-council/scripts/setup-channel.py \
  --name research \
  --context "Deep research and competitive analysis"
```

### Rename a Channel

```bash
python3 ~/.openclaw/skills/agent-council/scripts/rename-channel.py \
  --id 1234567890 \
  --old-name old-name \
  --new-name new-name
```

## Common Workflow

**Complete multi-agent setup:**

```bash
# 1. Create Discord channel
python3 scripts/setup-channel.py \
  --name research \
  --context "Deep research and competitive analysis" \
  --category-id "1234567890"

# (Copy the channel ID from output)

# 2. Apply gateway config for channel
openclaw gateway config.patch --raw '{"channels": {...}}'

# 3. Create agent bound to that channel
scripts/create-agent.sh \
  --name "Watson" \
  --id "watson" \
  --emoji "🔬" \
  --specialty "Deep research and competitive analysis" \
  --model "anthropic/claude-opus-4-5" \
  --workspace "$HOME/agents/watson" \
  --discord-channel "1234567890"

# Done! Agent is created and bound to the channel
```

## Agent Creation

### Basic Usage

```bash
scripts/create-agent.sh \
  --name "Agent Name" \
  --id "agent-id" \
  --emoji "🤖" \
  --specialty "What this agent does" \
  --model "provider/model-name" \
  --workspace "/path/to/workspace" \
  --discord-channel "1234567890"  # Optional
```

### What It Does

- ✅ Creates workspace with memory subdirectory
- ✅ Generates SOUL.md (personality & responsibilities)
- ✅ Generates HEARTBEAT.md (cron execution logic)
- ✅ Updates gateway config automatically
- ✅ Adds Discord channel binding (if specified)
- ✅ Restarts gateway to apply changes
- ✅ Optionally sets up daily memory cron job

### Examples

**Research agent:**
```bash
scripts/create-agent.sh \
  --name "Watson" \
  --id "watson" \
  --emoji "🔬" \
  --specialty "Deep research and competitive analysis" \
  --model "anthropic/claude-opus-4-5" \
  --workspace "$HOME/agents/watson" \
  --discord-channel "1234567890"
```

**Image generation agent:**
```bash
scripts/create-agent.sh \
  --name "Picasso" \
  --id "picasso" \
  --emoji "🎨" \
  --specialty "Image generation and editing specialist" \
  --model "google/gemini-3-flash-preview" \
  --workspace "$HOME/agents/picasso" \
  --discord-channel "9876543210"
```

**Health tracking agent:**
```bash
scripts/create-agent.sh \
  --name "Nurse Joy" \
  --id "nurse-joy" \
  --emoji "💊" \
  --specialty "Health tracking and wellness monitoring" \
  --model "anthropic/claude-opus-4-5" \
  --workspace "$HOME/agents/nurse-joy" \
  --discord-channel "5555555555"
```

## Discord Channel Management

### Create Channel

**Basic:**
```bash
python3 scripts/setup-channel.py \
  --name fitness \
  --context "Fitness tracking and workout planning"
```

**With category:**
```bash
python3 scripts/setup-channel.py \
  --name research \
  --context "Deep research and competitive analysis" \
  --category-id "1234567890"
```

**Use existing channel:**
```bash
python3 scripts/setup-channel.py \
  --name personal-finance \
  --id 1466184336901537897 \
  --context "Personal finance management"
```

### Rename Channel

**Basic:**
```bash
python3 scripts/rename-channel.py \
  --id 1234567890 \
  --old-name old-name \
  --new-name new-name
```

**With workspace search:**
```bash
python3 scripts/rename-channel.py \
  --id 1234567890 \
  --old-name old-name \
  --new-name new-name \
  --workspace "$HOME/my-workspace"
```

## Architecture

### Agent Structure

Each agent is self-contained:

```
agents/
├── watson/
│   ├── SOUL.md              # Personality and responsibilities
│   ├── HEARTBEAT.md         # Cron execution logic
│   ├── memory/              # Agent-specific memory
│   │   ├── 2026-02-01.md   # Daily memory logs
│   │   ├── 2026-02-02.md
│   │   └── 2026-02-03.md
│   └── .openclaw/
│       └── skills/          # Agent-specific skills (optional)
```

### Memory System

**Hybrid architecture:**
- **Agent-specific memory:** `<workspace>/memory/YYYY-MM-DD.md`
- **Shared memory access:** Agents can read shared workspace for context
- **Daily updates:** Optional cron job for end-of-day summaries

### Gateway Configuration

Agents and channels are automatically configured:

```json
{
  "agents": {
    "list": [
      {
        "id": "watson",
        "name": "Watson",
        "workspace": "/path/to/agents/watson",
        "model": {
          "primary": "anthropic/claude-opus-4-5"
        },
        "identity": {
          "name": "Watson",
          "emoji": "🔬"
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "watson",
      "match": {
        "channel": "discord",
        "peer": {
          "kind": "channel",
          "id": "1234567890"
        }
      }
    }
  ],
  "channels": {
    "discord": {
      "guilds": {
        "YOUR_GUILD_ID": {
          "channels": {
            "1234567890": {
              "allow": true,
              "requireMention": false,
              "systemPrompt": "Deep research and competitive analysis"
            }
          }
        }
      }
    }
  }
}
```

## Agent Coordination

Your main agent can coordinate with specialized agents using OpenClaw's built-in tools.

### List Active Agents

See all active agents and their recent activity:

```typescript
sessions_list({
  kinds: ["agent"],
  limit: 10,
  messageLimit: 3  // Show last 3 messages per agent
})
```

### Send Messages to Agents

**Direct communication:**
```typescript
sessions_send({
  label: "watson",  // Agent ID
  message: "Research the competitive landscape for X"
})
```

**Wait for response:**
```typescript
sessions_send({
  label: "watson",
  message: "What did you find about X?",
  timeoutSeconds: 300  // Wait up to 5 minutes
})
```

### Spawn Sub-Agent Tasks

For complex work, spawn a sub-agent in an isolated session:

```typescript
sessions_spawn({
  agentId: "watson",  // Optional: use specific agent
  task: "Research competitive landscape for X and write a report",
  model: "anthropic/claude-opus-4-5",  // Optional: override model
  runTimeoutSeconds: 3600,  // 1 hour max
  cleanup: "delete"  // Delete session after completion
})
```

The sub-agent will:
1. Execute the task in isolation
2. Announce completion back to your session
3. Self-delete (if `cleanup: "delete"`)

### Check Agent History

Review what an agent has been working on:

```typescript
sessions_history({
  sessionKey: "watson-session-key",
  limit: 50
})
```

### Coordination Patterns

**1. Direct delegation (Discord-bound agents):**
- User messages agent's Discord channel
- Agent responds directly in that channel
- Main agent doesn't need to coordinate

**2. Programmatic delegation (main agent → sub-agent):**
```typescript
// Main agent delegates task
sessions_send({
  label: "watson",
  message: "Research X and update memory/research-X.md"
})

// Watson works independently, updates files
// Main agent checks later or Watson reports back
```

**3. Spawn for complex tasks:**
```typescript
// For longer-running, isolated work
sessions_spawn({
  agentId: "watson",
  task: "Deep dive: analyze competitors A, B, C. Write report to reports/competitors.md",
  runTimeoutSeconds: 7200,
  cleanup: "keep"  // Keep session for review
})
```

**4. Agent-to-agent communication:**
Agents can send messages to each other:
```typescript
// In Watson's context
sessions_send({
  label: "picasso",
  message: "Create an infographic from data in reports/research.md"
})
```

### Best Practices

**When to use Discord bindings:**
- ✅ Domain-specific agents (research, health, images)
- ✅ User wants direct access to agent
- ✅ Agent should respond to channel activity

**When to use sessions_send:**
- ✅ Programmatic coordination
- ✅ Main agent delegates to specialists
- ✅ Need response in same session

**When to use sessions_spawn:**
- ✅ Long-running tasks (>5 minutes)
- ✅ Complex multi-step work
- ✅ Want isolation from main session
- ✅ Background processing

### Example: Research Workflow

```typescript
// Main agent receives request: "Research competitor X"

// 1. Check if Watson is active
const agents = sessions_list({ kinds: ["agent"] })

// 2. Delegate to Watson
sessions_send({
  label: "watson",
  message: "Research competitor X: products, pricing, market position. Write findings to memory/research-X.md"
})

// 3. Watson works independently:
//    - Searches web
//    - Analyzes data
//    - Updates memory file
//    - Reports back when done

// 4. Main agent retrieves results
const results = Read("agents/watson/memory/research-X.md")

// 5. Share with user
"Research complete! Watson found: [summary]"
```

## Configuration

### Discord Category ID

Organize channels in Discord categories:

**Option 1: Command line**
```bash
python3 scripts/setup-channel.py \
  --name channel-name \
  --context "Purpose" \
  --category-id "1234567890"
```

**Option 2: Environment variable**
```bash
export DISCORD_CATEGORY_ID="1234567890"
python3 scripts/setup-channel.py --name channel-name --context "Purpose"
```

### Finding Discord IDs

**Enable Developer Mode:**
- Settings → Advanced → Developer Mode

**Copy IDs:**
- Right-click channel → Copy ID
- Right-click category → Copy ID

## Scripts Reference

### create-agent.sh

Creates autonomous AI agents.

**Arguments:**
- `--name` (required) - Agent name
- `--id` (required) - Agent ID (lowercase, hyphenated)
- `--emoji` (required) - Agent emoji
- `--specialty` (required) - What the agent does
- `--model` (required) - LLM to use (provider/model-name)
- `--workspace` (required) - Where to create agent files
- `--discord-channel` (optional) - Discord channel ID to bind

### setup-channel.py

Creates and configures Discord channels.

**Arguments:**
- `--name` (required) - Channel name
- `--context` (required) - Channel purpose/context
- `--id` (optional) - Existing channel ID
- `--category-id` (optional) - Discord category ID

### rename-channel.py

Renames channels and updates references.

**Arguments:**
- `--id` (required) - Channel ID
- `--old-name` (required) - Current channel name
- `--new-name` (required) - New channel name
- `--workspace` (optional) - Workspace directory to search

## Documentation

See [SKILL.md](./SKILL.md) for complete documentation including:
- Detailed workflows
- Cron job setup
- Troubleshooting
- Advanced multi-agent coordination
- Best practices

## Use Cases

- **Domain specialists** - Research, health, finance, coding agents
- **Creative agents** - Image generation, writing, design
- **Task automation** - Scheduled monitoring, reports, alerts
- **Multi-agent systems** - Coordinated team of specialized agents
- **Discord organization** - Structured channels for different agent domains

## Bot Permissions

Required Discord bot permissions:
- `Manage Channels` - To create/rename channels
- `View Channels` - To read channel list
- `Send Messages` - To post in channels

## Community

- **OpenClaw Docs:** https://docs.openclaw.ai
- **OpenClaw Discord:** https://discord.com/invite/clawd
- **Skill Catalog:** https://clawhub.com

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a PR with clear description

## License

MIT License - see [LICENSE](./LICENSE) file for details

## About

Community-contributed skill for the OpenClaw ecosystem.

Complete toolkit for building multi-agent systems with autonomous agents and organized Discord channels.
