---
title: Agent Presets
description: Configure your coding agent
---

Ship Loop works with any coding agent that accepts a prompt via stdin. Presets make configuration easier for popular agents.

## Available Presets

| Preset | Command | Notes |
|--------|---------|-------|
| `claude-code` | `claude --print --permission-mode bypassPermissions` | Anthropic's Claude Code CLI |
| `codex` | `codex --quiet` | OpenAI's Codex CLI |
| `aider` | `aider --yes-always --no-git` | Aider (git disabled, Ship Loop handles git) |

## Using a Preset

```yaml
agent: claude-code
```

That's it. Ship Loop resolves the preset to the full command.

## Using a Custom Command

```yaml
agent_command: "your-agent --your-flags"
```

Requirements for custom commands:
- Must accept a prompt via **stdin** (Ship Loop pipes the prompt file: `cat prompt.txt | your-command`)
- Must exit 0 on success, non-zero on failure
- Should write code changes to the working directory

If both `agent` and `agent_command` are set, `agent_command` takes priority.

## Claude Code Setup

1. Install: `npm install -g @anthropic-ai/claude-code`
2. Authenticate: `claude auth`
3. Config:

```yaml
agent: claude-code
```

The `--print` flag runs Claude Code in non-interactive mode (outputs to stdout). The `--permission-mode bypassPermissions` flag allows file writes without confirmation prompts.

## Codex Setup

1. Install: follow [Codex docs](https://github.com/openai/codex)
2. Config:

```yaml
agent: codex
```

## Aider Setup

1. Install: `pip install aider-chat`
2. Set your API key: `export ANTHROPIC_API_KEY=...` or `export OPENAI_API_KEY=...`
3. Config:

```yaml
agent: aider
```

The `--no-git` flag is important: Ship Loop manages all git operations (explicit staging, security scanning, tagging). Letting Aider also commit would cause conflicts.

## Any Other Agent

If your agent CLI accepts prompts via stdin:

```yaml
agent_command: "my-agent --batch --output-dir ."
```

If it reads from a file instead, wrap it:

```yaml
agent_command: "sh -c 'cat > /tmp/prompt.txt && my-agent --prompt /tmp/prompt.txt'"
```

## Timeouts

Agent invocations have a configurable timeout:

```yaml
timeouts:
  agent: 900    # 15 minutes (default)
```

If the agent exceeds this, it's killed and the segment enters the repair loop.
