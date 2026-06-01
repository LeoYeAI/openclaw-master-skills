# OpenClaw + Kiro CLI Coding Agent Skill

[中文文档](./README.zh-CN.md)

> Integrate [Kiro CLI](https://kiro.dev/) (AWS AI coding assistant) with [OpenClaw](https://github.com/openclaw/openclaw) for seamless AI-powered coding workflows.

## What is This?

This repository provides a **coding-agent skill** for OpenClaw that enables integration with Kiro CLI and other coding agents (Codex, Claude Code, OpenCode, Pi). The skill teaches OpenClaw how to:

- Launch and manage coding agents in the background
- Handle multi-turn conversations with interactive CLIs
- Monitor progress and capture outputs
- Coordinate coding tasks through chat interfaces (WhatsApp, Discord, Telegram, etc.)

## What is OpenClaw?

[OpenClaw](https://github.com/openclaw/openclaw) is an open-source AI assistant framework that connects to various messaging platforms. It can:

- Run as a personal AI assistant across WhatsApp, Discord, Telegram, Signal, etc.
- Execute shell commands, browse the web, manage files
- Be extended with **skills** — modular instruction sets for specific tasks

## What is Kiro CLI?

[Kiro CLI](https://kiro.dev/) is AWS's AI coding assistant with powerful features:

- Session persistence and conversation resume
- Custom agents with pre-defined tool permissions
- Steering files for project context
- MCP (Model Context Protocol) integration
- Plan Agent for structured task planning

## Installation

### 1. Install OpenClaw

Follow the [OpenClaw installation guide](https://docs.openclaw.ai/).

### 2. Install Kiro CLI

```bash
# macOS / Linux (recommended)
curl -fsSL https://cli.kiro.dev/install | bash

# Or download from https://kiro.dev/
```

After installation, run `kiro-cli login` to authenticate (supports GitHub, Google, AWS Builder ID, or IAM Identity Center).

### 3. Add the Skill

Copy `SKILL.md` to your OpenClaw workspace skills directory:

```bash
mkdir -p ~/.openclaw/workspace/skills/coding-agent
cp SKILL.md ~/.openclaw/workspace/skills/coding-agent/
```

Or clone this repo directly:

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/terrificdm/openclaw-kirocli-coding-agent.git coding-agent
```

## Usage

Once installed, you can ask OpenClaw to use Kiro CLI for coding tasks.

> **Note:** Use the magic word **"kiro"** in your message to activate Kiro CLI. For example: "Use **kiro** to..." or "Ask **kiro** to..."

### One-Shot Queries

```
"Use kiro to check what AWS Lambda features were released recently"
"Ask kiro to list all TODO comments in my project"
```

OpenClaw will run:
```bash
kiro-cli chat --no-interactive --trust-all-tools "your query"
```

### Multi-Turn Conversations

```
"Start a conversation with kiro about building a REST API"
"Tell kiro I want to use Python and FastAPI"
"Ask kiro to create the project structure"
```

OpenClaw manages the session using background processes:
```bash
# Start interactive session
exec pty:true background:true command:"kiro-cli chat --trust-all-tools"

# Send messages
process action:paste sessionId:XXX text:"your message"
process action:send-keys sessionId:XXX keys:["Enter"]

# Read responses
process action:log sessionId:XXX
```

### Complex Tasks with Plan Agent

For multi-step features, suggest using Kiro's Plan Agent:

```
"Use kiro's /plan mode to design a user authentication system"
```

Plan Agent will:
1. Gather requirements through structured questions
2. Research your codebase
3. Create a detailed implementation plan
4. Hand off to execution after your approval

## Key Features

| Feature | Description |
|---------|-------------|
| **PTY Support** | Proper terminal emulation for interactive CLIs |
| **Background Sessions** | Long-running tasks don't block the conversation |
| **Multi-Agent Support** | Works with Kiro, Codex, Claude Code, OpenCode, Pi |
| **Session Management** | Monitor, send input, kill sessions as needed |

## Supported Coding Agents

| Agent | Command | Notes |
|-------|---------|-------|
| **Kiro CLI** | `kiro-cli` | AWS AI assistant, recommended |
| Codex | `codex` | OpenAI, requires git repo |
| Claude Code | `claude` | Anthropic |
| OpenCode | `opencode` | Open source |
| Pi | `pi` | Lightweight, multi-provider |

## Important Notes

1. **Always use `pty:true`** — Coding agents need a pseudo-terminal
2. **Use `--trust-all-tools`** — For automation without confirmation prompts
3. **Use `--no-interactive`** — For simple one-shot queries
4. **Set `workdir`** — Keep agents focused on specific projects

## Example Workflow

```
User: "Use kiro to help me refactor the auth module"

OpenClaw: Starting Kiro session for auth refactoring...
         [Launches: kiro-cli chat --trust-all-tools]

User: "I want to switch from JWT to session-based auth"

OpenClaw: [Sends message to Kiro session]
         Kiro says: "I'll help you migrate from JWT to session-based 
         authentication. Let me first analyze your current implementation..."
         
User: "Go ahead with the changes"

OpenClaw: [Sends approval to Kiro]
         Kiro is making changes... I'll notify you when done.
```

## License

MIT

## Links

- [OpenClaw](https://github.com/openclaw/openclaw)
- [Kiro CLI](https://kiro.dev/)
- [OpenClaw Documentation](https://docs.openclaw.ai/)
