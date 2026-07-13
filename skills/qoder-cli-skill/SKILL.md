---
name: qoder-agent
description: 'Delegate coding tasks to Qoder CLI using Print mode (non-interactive). Use when: (1) building/creating new features or apps, (2) code reviews, (3) refactoring, (4) iterative coding that needs file exploration. Supports subagents, worktrees, MCP servers, quest mode, and hooks. Works in all session types (direct chat, group chat, Discord, etc.). NOT for: simple one-liner fixes (just edit), reading code (use read tool). Requires qodercli installed.'
metadata:
  {
    "openclaw": { "emoji": "🤖", "requires": { "anyBins": ["qodercli"] } },
  }
---

# Qoder Agent (Print Mode - Non-Interactive)

**Use Print mode (`-p`)** for all Qoder CLI work in OpenClaw. TUI mode is not supported in automated environments.

**✅ All-Sessions Ready:** This skill works in:
- Direct 1:1 chats
- Group chats (DingTalk, Discord, Slack, etc.)
- Shared workspace sessions
- Private sessions

---

## ⚠️ Important: Print Mode Only

**TUI mode is NOT supported** in OpenClaw or other automated environments due to TTY requirements.

**Always use Print mode** with the `-p` flag:

```bash
# ✅ Correct - Print mode (non-interactive)
bash workdir:~/project command:"qodercli -p 'Add error handling'"

# ❌ Wrong - TUI mode requires interactive terminal
bash pty:true command:"qodercli"  # Will fail
```

---

## 🔐 Environment Setup (Auto-Detected)

Qoder CLI authentication is automatically available via:

```bash
# Environment variable (set in ~/.zshrc)
QODER_PERSONAL_ACCESS_TOKEN="your_token_here"

# Or check if already authenticated
qodercli status
```

**In any session type**, the environment variable is inherited from the shell, so Qoder CLI works seamlessly.

---

## 🚀 Quick Start

### Basic Usage

```bash
# Quick one-shot task
bash workdir:~/project command:"qodercli -p 'Add error handling to the API calls'"

# With ultimate model for best quality
bash workdir:~/project command:"qodercli --model=ultimate -p 'Refactor this module'"

# With JSON output
bash workdir:~/project command:"qodercli --output-format=json -p 'Analyze this code'"

# Continue last session
bash workdir:~/project command:"qodercli -c -p 'Continue the refactoring'"

# Max turns limit
bash workdir:~/project command:"qodercli --max-turns=10 -p 'Fix the bug'"

# Yolo mode (skip permissions)
bash workdir:~/project command:"qodercli --yolo -p 'Make the changes'"
```

---

## 🎯 Print Mode Flags

| Flag | Description | Example |
|------|-------------|---------|
| `-p` | **Required** - Run non-interactively | `qodercli -p "task"` |
| `-q` | Quiet mode (hide spinner) | `qodercli -q -p "task"` |
| `--output-format` | Output format: text, json, stream-json | `qodercli --output-format=json` |
| `-w` | Specify workspace directory | `qodercli -w /path/to/project` |
| `-c` | Continue last session | `qodercli -c -p "continue"` |
| `-r` | Resume specific session | `qodercli -r <session-id>` |
| `--model` | Model tier selection | `qodercli --model=ultimate` |
| `--max-turns` | Maximum dialog turns (0 = unlimited) | `qodercli --max-turns=10` |
| `--max-output-tokens` | Max tokens: 16k, 32k | `qodercli --max-output-tokens=32k` |
| `--yolo` | Skip permission checks | `qodercli --yolo` |
| `--allowed-tools` | Allow only specified tools | `qodercli --allowed-tools=READ,WRITE` |
| `--disallowed-tools` | Disallow specified tools | `qodercli --disallowed-tools=Bash` |
| `--agents` | JSON object defining custom agents | `qodercli --agents='{"reviewer":{...}}'` |
| `--attachment` | Attach image files (repeatable) | `qodercli --attachment=img.png` |

---

## 🧠 Model Selection

Qoder CLI uses **automatic model routing** - it selects the globally optimal model based on task characteristics. You can override this:

| Model Value | Use Case | Speed | Quality | Cost |
|-------------|----------|-------|---------|------|
| `auto` | **Default** - automatic routing | ⚡⚡⚡ | ⭐⭐⭐ | 💰💰💰 |
| `efficient` | Quick tasks, simple queries | ⚡⚡⚡⚡ | ⭐⭐ | 💰💰 |
| `lite` | Very simple tasks | ⚡⚡⚡⚡⚡ | ⭐ | 💰 |
| `performance` | Complex tasks needing depth | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰💰💰 |
| `ultimate` | **Best quality** - refactoring, architecture, code review | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰💰💰 |
| `qmodel` | Qwen model family | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰💰💰 |
| `q35model` | Qwen 3.5 specific | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰💰💰 |
| `mmodel` | MiniMax model | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰💰💰 |
| `gmodel` | GPT model family | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰💰 |

**Recommendations:**
- **Default**: Use `--model=auto` (let Qoder choose)
- **Refactoring/Architecture**: `--model=ultimate`
- **Quick fixes**: `--model=efficient`
- **Code review**: `--model=performance` or `ultimate`
- **Simple queries**: `--model=lite` or `efficient`

---

## 🎯 Quest Mode (Spec-Driven Development)

Quest Mode allows you to write specifications while AI automatically completes development tasks using subagents.

```bash
# Quest mode via prompt
bash workdir:~/project command:"qodercli --model=ultimate -p 'Build a REST API with authentication, rate limiting, and logging'"
```

Quest Mode automatically:
1. Analyzes requirements
2. Routes to appropriate subagents
3. Coordinates multi-step development
4. Ensures consistency across files

---

## 🤖 Subagents

Subagents are specialized AI agents for specific tasks with their own context windows and tool permissions.

### Create a Subagent (Manual)

Create markdown files in:
- `~/.qoder/agents/<agentName>.md` - User-level (all projects)
- `${project}/agents/<agentName>.md` - Project-level

**Example: code-review agent**
```markdown
---
name: code-review
description: Code review expert for quality and security checks
tools: Read, Grep, Glob, Bash
---

You are a senior code reviewer responsible for ensuring code quality.

Checklist:
1. Readability and code style
2. Naming conventions
3. Error handling
4. Security checks
5. Test coverage
6. Performance considerations
```

### Use Subagents

```bash
# Explicit invocation
bash workdir:~/project command:"qodercli -p 'Use code-review subagent to check code issues'"

# Implicit invocation
bash workdir:~/project command:"qodercli -p 'Analyze this code for potential performance issues'"

# Chained subagents
bash workdir:~/project command:"qodercli -p 'First use design subagent for system design, then use code-review subagent'"

# Custom agents inline
bash workdir:~/project command:"qodercli --agents='{\"reviewer\":{\"description\":\"Reviews code\",\"prompt\":\"You are a code reviewer\"}}' -p 'Review this'"
```

---

## 🌳 Worktree (Parallel Jobs)

Worktree jobs are concurrent jobs that use Git worktrees to run tasks in parallel, avoiding read/write conflicts.

**Requirements:** Git installed and usable locally.

### Commands

| Command | Description |
|---------|-------------|
| `qodercli --worktree "job description"` | Create and start new worktree job |
| `qodercli jobs --worktree` | List existing worktree jobs |
| `qodercli rm <jobId>` | Remove a job (delete worktree) |

### Create a Job

```bash
# Basic worktree job (non-interactive)
bash workdir:~/project command:"qodercli --worktree -p 'Fix issue #78'"

# With branch specification
bash workdir:~/project command:"qodercli --worktree --branch=main -p 'Implement feature'"

# With max turns
bash workdir:~/project command:"qodercli --worktree --max-turns=20 -p 'Complex refactoring'"
```

### View Jobs

```bash
bash workdir:~/project command:"qodercli jobs --worktree"
```

### Delete Jobs

```bash
bash workdir:~/project command:"qodercli rm <jobId>"
```

⚠️ **Warning:** Deletion is irreversible. Proceed with caution.

### Parallel Issue Fixing Example

```bash
# Multiple worktrees for parallel work
bash workdir:~/project background:true command:"qodercli --worktree -p 'Fix issue #78'"
bash workdir:~/project background:true command:"qodercli --worktree -p 'Fix issue #99'"

# Monitor progress
process action:list
process action:log sessionId:XXX
```

---

## 🔌 MCP Servers

Qoder CLI integrates with any standard MCP (Model Context Protocol) tool.

### Add MCP Servers

```bash
# Basic syntax
bash command:"qodercli mcp add <name> -- <command>"

# Example: Playwright for browser control
bash command:"qodercli mcp add playwright -- npx -y @playwright/mcp@latest"
```

### Recommended MCP Tools

```bash
# Context7 - Upstash context management
bash command:"qodercli mcp add context7 -- npx -y @upstash/context7-mcp@latest"

# DeepWiki - Wikipedia/knowledge access
bash command:"qodercli mcp add deepwiki -- npx -y mcp-deepwiki@latest"

# Chrome DevTools - Browser automation
bash command:"qodercli mcp add chrome-devtools -- npx chrome-devtools-mcp@latest"
```

### Manage MCP Servers

```bash
# List servers
bash command:"qodercli mcp list"

# Remove server
bash command:"qodercli mcp remove playwright"
```

---

## 🔐 Permissions

Qoder CLI enforces precise tool execution permissions.

### Configuration Files (precedence: high → low)

1. `${project}/.qoder/settings.local.json` - Project-level, highest (gitignore)
2. `${project}/.qoder/settings.json` - Project-level
3. `~/.qoder/settings.json` - User-level

### Permission Strategies

| Strategy | Description |
|----------|-------------|
| `allow` | Automatically allow matching operations |
| `deny` | Automatically deny matching operations |
| `ask` | Prompt for permission (default for outside project) |

### Example Configuration

```json
{
  "permissions": {
    "ask": [
      "Read(!/Users/demo/projects/myproject/**)",
      "Edit(!/Users/demo/projects/myproject/**)"
    ],
    "allow": [
      "Read(/Users/demo/projects/myproject/**)",
      "Edit(/Users/demo/projects/myproject/**)"
    ],
    "deny": [
      "Bash(rm -rf /**)"
    ]
  }
}
```

### Permission Types

#### 1. Read & Edit Rules

Patterns follow gitignore-style matching:

| Pattern Form | Description | Example | Matches |
|--------------|-------------|---------|---------|
| `/path` | Absolute from system root | `Read(/Users/demo/**)` | `/Users/demo/xx` |
| `~/path` | From home directory | `Read(~/Documents/*.png)` | `/Users/demo/Documents/xx.png` |
| `path` or `./path` | Relative to current dir | `Read(/*.java)` | `./xx.java` |
| `!**` | Negation pattern | `Read(!**/node_modules/**)` | Excludes node_modules |

#### 2. WebFetch Rules

Restrict domains for network fetch:

```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:example.com)",
      "WebFetch(domain:*.github.io)"
    ]
  }
}
```

#### 3. Bash Rules

Restrict commands for shell execution:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run build)",
      "Bash(npm run test:*)",
      "Bash(curl http://site.com/:*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ]
  }
}
```

---

## 📝 Memory (AGENTS.md)

Qoder CLI uses `AGENTS.md` as memory - content is auto-loaded as context.

### File Locations

- **User-level**: `~/.qoder/AGENTS.md` - Applies to all projects
- **Project-level**: `${project}/AGENTS.md` - Applies to current project

### Typical Content

- Development standards and notes
- Overall system architecture
- Project-specific conventions
- API documentation
- Testing requirements

### Generate/Manage

```bash
# Manually create AGENTS.md in project root
cat > ~/project/AGENTS.md << 'EOF'
# Project Guidelines

## Architecture
- MVC pattern
- REST API design

## Code Style
- ESLint strict mode
- Prettier formatting
EOF
```

---

## ⚡ Advanced Options

| Option | Description | Example |
|--------|-------------|---------|
| `-w` | Specify workspace directory | `qodercli -w /path/to/project` |
| `-c` | Continue last session | `qodercli -c -p "continue"` |
| `-r` | Resume specific session | `qodercli -r <session-id>` |
| `--allowed-tools` | Allow only specified tools | `qodercli --allowed-tools=READ,WRITE` |
| `--disallowed-tools` | Disallow specified tools | `qodercli --disallowed-tools=Bash` |
| `--max-turns` | Maximum dialog turns | `qodercli --max-turns=10` |
| `--yolo` | Skip permission checks | `qodercli --yolo` |
| `--worktree` | Create worktree job | `qodercli --worktree "task"` |
| `--branch` | Set branch for worktree | `qodercli --worktree --branch=main` |
| `--agents` | Define custom agents inline | `qodercli --agents='{...}'` |
| `--attachment` | Attach image files | `qodercli --attachment=img.png` |

---

## ⚠️ Rules

1. **Print mode only** - TUI mode not supported in OpenClaw
2. **Always use `-p` flag** - Non-interactive mode required
3. **Respect workdir** - Qoder sees only the specified directory's context
4. **Monitor with process:log** - check background session progress
5. **Use worktrees for parallel work** - avoid read/write conflicts
6. **Initialize AGENTS.md** - helps Qoder understand project context
7. **Configure permissions** - set appropriate access rules per project
8. **Leverage subagents** - specialized agents for specific tasks
9. **Add MCP servers** - extend capabilities with external tools
10. **Works in all sessions** - environment variables are inherited automatically
11. **Use ultimate model for complex tasks** - refactoring, architecture, code review

---

## Progress Updates (Critical)

When you spawn Qoder CLI in the background, keep the user in the loop:

- Send 1 short message when you start (what's running + where)
- Then only update again when something changes:
  - a milestone completes (build finished, tests passed)
  - the CLI asks a question / needs input
  - you hit an error or need user action
  - the CLI finishes (include what changed + where)
- If you kill a session, immediately say you killed it and why

This prevents the user from seeing only "Agent failed before reply" and having no idea what happened.

---

## Auto-Notify on Completion

For long-running background tasks, append a wake trigger:

```bash
bash workdir:~/project background:true command:"qodercli --model=ultimate 'Build a REST API for todos.

When completely finished, run: openclaw system event --text \"Done: Built todos REST API with CRUD endpoints\" --mode now'"
```

This triggers an immediate wake event — you get pinged in seconds, not minutes.

---

## 🌐 Cross-Session Usage

### In Group Chats (DingTalk, Discord, Slack)

```bash
# Just use normal commands - environment is inherited
bash workdir:~/project command:"qodercli -p 'Help me fix this bug'"

# No special setup needed!
```

### In Direct Messages

Same as group chats - works out of the box.

### In Shared Workspaces

```bash
# Specify the workspace explicitly
bash workdir:/shared/project command:"qodercli --model=ultimate -p 'Refactor this'"
```

### Privacy Note

- Qoder CLI only accesses the specified `workdir`
- Environment variables are inherited from the host shell
- No credentials are exposed in chat messages
- Each session has isolated Qoder CLI state

---

## 📊 Comparison with Other Coding Agents

| Feature | Qoder CLI | Codex | Claude Code |
|---------|-----------|-------|-------------|
| Print Mode | ✅ | ✅ | ❌ |
| Subagents | ✅ | ❌ | ❌ |
| Worktrees | ✅ | ❌ | ❌ |
| MCP Servers | ✅ | ✅ | ✅ |
| Memory (AGENTS.md) | ✅ | ✅ | ✅ |
| Model Selection | ✅ (auto-routing) | ❌ | ❌ |
| Quest Mode | ✅ | ❌ | ❌ |
| Permission System | ✅ (granular) | ⚠️ | ⚠️ |
| All-Sessions Ready | ✅ | ⚠️ | ⚠️ |

**Qoder CLI strengths:**
- Subagents for specialized tasks
- Worktrees for parallel development
- Quest mode for spec-driven development
- Automatic model routing
- Granular permission system
- Cross-session compatibility

---

## 📋 Quick Reference Card

```bash
# Quick task (print mode, auto model)
qodercli -p "Your prompt"

# High-quality task (ultimate model)
qodercli --model=ultimate -p "Your prompt"

# Quest mode (spec-driven)
qodercli -p "Build a REST API with auth"

# Background task (worktree)
qodercli --worktree -p "Your task"

# Check status
qodercli status

# Skip permissions (use with caution)
qodercli --yolo -p "Your prompt"

# Continue last session
qodercli -c -p "Continue"

# JSON output
qodercli --output-format=json -p "Analyze"

# With custom subagents
qodercli --agents='{"reviewer":{...}}' -p "Review this"
```

---

## 🔧 Troubleshooting

### Not Logged In

```bash
# Check status
qodercli status

# Set environment variable
export QODER_PERSONAL_ACCESS_TOKEN="your_token"
```

### Permission Denied

```bash
# Use yolo mode (caution)
qodercli --yolo -p "task"

# Or configure permissions in ~/.qoder/settings.json
```

### Model Selection Issues

```bash
# Explicitly specify model
qodercli --model=ultimate -p "task"

# Or use auto for automatic routing
qodercli --model=auto -p "task"
```

### TUI Mode Error

**TUI mode is NOT supported in OpenClaw.** Always use Print mode:

```bash
# ✅ Correct
qodercli -p "Your task"

# ❌ Wrong (will fail)
qodercli  # TUI requires interactive terminal
```
