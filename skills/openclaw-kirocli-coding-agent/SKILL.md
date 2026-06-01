---
name: coding-agent
description: Run Codex CLI, Claude Code, Kiro CLI, OpenCode, or Pi Coding Agent via background process for programmatic control.
metadata:
  {
    "openclaw": { "emoji": "🧩", "requires": { "anyBins": ["claude", "codex", "opencode", "pi", "kiro-cli"] } },
  }
---

# Coding Agent

Launch and manage AI coding agents (Codex, Claude Code, Kiro CLI, OpenCode, Pi) from OpenClaw using bash with background process control.

## PTY Mode Required

Coding agents are **interactive terminal applications** that need a pseudo-terminal (PTY). Without it, output breaks or the agent hangs.

**Always set `pty:true`:**

```bash
# Correct — with PTY
bash pty:true command:"codex exec 'Your prompt'"

# Wrong — agent may break or hang
bash command:"codex exec 'Your prompt'"
```

## Tool Reference

### Bash Parameters

| Parameter    | Type    | Description                                                 |
| ------------ | ------- | ----------------------------------------------------------- |
| `command`    | string  | Shell command to run                                        |
| `pty`        | boolean | Allocate a pseudo-terminal (**required for coding agents**) |
| `workdir`    | string  | Working directory (agent sees only this folder)             |
| `background` | boolean | Run in background; returns `sessionId` for monitoring       |
| `timeout`    | number  | Timeout in seconds (kills process on expiry)                |
| `elevated`   | boolean | Run on host instead of sandbox (if allowed)                 |

### Process Actions (background sessions)

| Action      | Description                                          |
| ----------- | ---------------------------------------------------- |
| `list`      | List all running/recent sessions                     |
| `poll`      | Check if a session is still running                  |
| `log`       | Get session output (optional offset/limit)           |
| `write`     | Send raw data to stdin (no newline)                  |
| `submit`    | Send data + newline (like typing and pressing Enter) |
| `send-keys` | Send key tokens or hex bytes                         |
| `paste`     | Paste text (optional bracketed mode)                 |
| `kill`      | Terminate the session                                |

---

## Quick Start: One-Shot Tasks

```bash
# Codex needs a git repo — create a temp one for scratch work
SCRATCH=$(mktemp -d) && cd $SCRATCH && git init && codex exec "Your prompt"

# Run inside an existing project (with PTY)
bash pty:true workdir:~/project command:"codex exec 'Add error handling to the API calls'"
```

---

## Core Pattern: workdir + background + pty

For longer tasks, combine all three:

```bash
# 1. Start the agent
bash pty:true workdir:~/project background:true command:"codex exec --full-auto 'Build a snake game'"
# → returns sessionId

# 2. Monitor progress
process action:log sessionId:XXX

# 3. Check completion
process action:poll sessionId:XXX

# 4. Send input if the agent asks a question
process action:submit sessionId:XXX data:"yes"     # text + Enter
process action:write sessionId:XXX data:"y"         # raw keystroke

# 5. Kill if stuck
process action:kill sessionId:XXX
```

**Why `workdir`?** The agent starts in a focused directory and won't wander into unrelated files.

---

## Codex CLI

**Default model:** `gpt-5.2-codex` (set in `~/.codex/config.toml`)

### Flags

| Flag            | Effect                                             |
| --------------- | -------------------------------------------------- |
| `exec "prompt"` | One-shot execution, exits when done                |
| `--full-auto`   | Sandboxed, auto-approves within workspace          |
| `--yolo`        | No sandbox, no approvals (fastest, most dangerous) |

### Building / Creating

```bash
# One-shot with auto-approve
bash pty:true workdir:~/project command:"codex exec --full-auto 'Build a dark mode toggle'"

# Background for longer work
bash pty:true workdir:~/project background:true command:"codex --yolo 'Refactor the auth module'"
```

### Reviewing PRs

**Never review PRs in OpenClaw's own project folder.** Clone to a temp directory or use a git worktree.

```bash
# Clone to temp
REVIEW_DIR=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW_DIR
cd $REVIEW_DIR && gh pr checkout 130
bash pty:true workdir:$REVIEW_DIR command:"codex review --base origin/main"

# Or use git worktree (keeps main intact)
git worktree add /tmp/pr-130-review pr-130-branch
bash pty:true workdir:/tmp/pr-130-review command:"codex review --base main"
```

### Batch PR Reviews

```bash
# Fetch all PR refs
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# Launch one Codex per PR (all background + PTY)
bash pty:true workdir:~/project background:true command:"codex exec 'Review PR #86. git diff origin/main...origin/pr/86'"
bash pty:true workdir:~/project background:true command:"codex exec 'Review PR #87. git diff origin/main...origin/pr/87'"

# Monitor
process action:list

# Post results
gh pr comment <PR#> --body "<review content>"
```

---

## Claude Code

```bash
# One-shot
bash pty:true workdir:~/project command:"claude 'Your task'"

# Background
bash pty:true workdir:~/project background:true command:"claude 'Your task'"
```

---

## Kiro CLI (AWS)

AWS AI coding assistant with session persistence, custom agents, skills, hooks, steering, subagents, planning mode, and MCP integration.

**Install:** https://kiro.dev/docs/cli/installation

### Basic Usage

```bash
kiro-cli                           # Interactive chat (default)
kiro-cli chat "Your question"      # Direct question
kiro-cli --agent my-agent          # Use a specific agent
kiro-cli chat --resume             # Resume last session (per-directory)
kiro-cli chat --resume-picker      # Pick from saved sessions
kiro-cli chat --list-sessions      # List all sessions
```

### Non-Interactive Mode

For scripting and automation — outputs a single response to STDOUT, then exits.

```bash
# Single response
kiro-cli chat --no-interactive "Show current directory"

# Trust all tools (no confirmation prompts)
kiro-cli chat --no-interactive --trust-all-tools "Create hello.py"

# Trust specific tools only
kiro-cli chat --no-interactive --trust-tools "fs_read,fs_write" "Read package.json"
```

**Tool trust:** `--trust-all-tools` for full automation. For untrusted input, use `--trust-tools "fs_read,fs_write,shell"` to limit scope.

### OpenClaw Integration

```bash
# Interactive session (background)
bash pty:true workdir:~/project background:true command:"kiro-cli"

# One-shot query (non-interactive)
bash pty:true workdir:~/project command:"kiro-cli chat --no-interactive --trust-all-tools 'List all TODO comments in src/'"

# With a specific agent
bash pty:true workdir:~/project background:true command:"kiro-cli --agent aws-expert 'Set up Lambda'"

# Resume previous session
bash pty:true workdir:~/project command:"kiro-cli chat --resume"
```

### Skills (Agent Skills)

Skills are **portable instruction packages** that extend what Kiro knows. When a request matches a skill's description, Kiro automatically loads and follows its instructions — no slash command needed.

#### Skill Locations

| Location | Scope | Notes |
| --- | --- | --- |
| `.kiro/skills/<name>/` | Workspace (project) | Shared via version control |
| `~/.kiro/skills/<name>/` | Global (all projects) | Personal workflows |

Workspace skills take priority when names collide.

#### Creating a Skill

A skill is a folder with a `SKILL.md` file:

```
my-skill/
├── SKILL.md          # Required — frontmatter + instructions
└── references/       # Optional — detailed docs loaded on demand
    └── guide.md
```

**SKILL.md format:**

````markdown
---
name: pr-review
description: Review pull requests for code quality, security issues, and test coverage.
---

## Review checklist

1. Check for vulnerabilities, injection risks, exposed secrets
2. Verify edge cases and failure modes are handled
3. Confirm new code has appropriate tests

For detailed patterns, see `references/guide.md`.
````

- **`name`** — Unique identifier for the skill.
- **`description`** — Determines when Kiro activates the skill. Be specific; include keywords that match how you'd phrase requests.
- **Reference files** — Stored in `references/`. Kiro loads them only when the instructions direct it to.

#### Skills in Custom Agents

The default agent auto-discovers skills. Custom agents need explicit resource declarations:

```json
{
  "name": "my-agent",
  "resources": [
    "skill://.kiro/skills/*/SKILL.md",
    "skill://~/.kiro/skills/*/SKILL.md"
  ]
}
```

#### Skill Best Practices

- **Precise descriptions** — "Review pull requests for security vulnerabilities and test coverage" activates reliably; "Helps with code review" does not.
- **Keep SKILL.md actionable** — Put lengthy reference material in `references/` files.
- **Right scope** — Global skills for personal workflows; workspace skills for team/project conventions.
- **Version control** — Commit `.kiro/skills/` so the team shares the same workflows.
- **Check availability** — Use `/context show` to see which skills are loaded in the current session.

### Planning Mode (Plan Agent)

Plan Agent is a **built-in read-only agent** for structured planning before execution. It transforms ideas into detailed implementation plans through an interactive workflow.

#### When to Use

- Complex multi-step features (e.g., "build a user authentication system")
- Unclear or evolving requirements that need refinement
- Large features that benefit from task breakdown before coding

#### When NOT to Use

- Simple queries or single-step tasks
- User already has clear, specific instructions
- Quick fixes or small changes

#### How to Enter Planning Mode

```bash
# Slash command
> /plan

# With an immediate prompt
> /plan Build a REST API for user authentication

# Keyboard shortcut (toggles plan ↔ execution)
Shift + Tab
```

When active, the prompt shows a `[plan]` indicator.

#### Plan Workflow (4 phases)

1. **Requirements gathering** — Structured multiple-choice questions to refine your idea. Answer with `1=a, 2=b` syntax or free-text.
2. **Research & analysis** — Explores your codebase using code intelligence, grep, and glob tools.
3. **Implementation plan** — Produces a task breakdown with clear objectives, implementation guidance, and demo descriptions for each task.
4. **Approval & handoff** — You review the plan. On approval (`y`), the plan transfers automatically to the execution agent.

**Plan Agent is read-only:** it can read files, search code, and research, but cannot write files or execute commands until handoff.

#### OpenClaw Integration for Planning Mode

For interactive planning sessions, run Kiro in background mode and relay the `/plan` command:

```bash
# Start interactive Kiro session
bash pty:true workdir:~/project background:true command:"kiro-cli chat --trust-all-tools"

# Enter planning mode
process action:submit sessionId:XXX data:"/plan Build a REST API for user authentication"

# Relay the user's answers to requirement questions
process action:submit sessionId:XXX data:"1=a, 2=d I'm using Rust with Axum"

# Approve the plan
process action:submit sessionId:XXX data:"y"

# Monitor output
process action:log sessionId:XXX
```

#### Example Planning Session

```
> /plan Add user authentication to my web app

[plan] > I understand you want to add user authentication.
[1]: What authentication method?
  a. Email/Password   b. OAuth   c. Magic Links   d. Multi-factor
> 1=a

[plan] > Great! Email/password it is.
[2]: What's your tech stack?
  a. React + Node.js   b. Next.js   c. Django/Flask   d. Other
> 2=d, I'm using Rust with Axum

[plan] > Researching Axum authentication patterns...

**Implementation Plan — User Authentication System**
[Detailed task breakdown...]

Does this plan look good? Ready to exit [plan] agent? [y/n]: y
[default] > Implement this plan: [Plan transferred]
```

### Hooks

Hooks execute custom commands at specific points during agent lifecycle and tool execution. Defined in the agent configuration file.

#### Hook Types

| Hook | Trigger | Can Block? |
| --- | --- | --- |
| `AgentSpawn` | Agent starts | No |
| `UserPromptSubmit` | User sends a prompt | No |
| `PreToolUse` | Before a tool runs | Yes (exit code 2) |
| `PostToolUse` | After a tool runs | No |
| `Stop` | Agent finishes a turn | No |

#### Exit Codes

- **0** — Success. STDOUT captured (added to context for AgentSpawn/UserPromptSubmit).
- **2** — (PreToolUse only) Block tool execution; STDERR returned to the LLM.
- **Other** — Failure. STDERR shown as warning to user.

#### Tool Matching

Use the `matcher` field to target specific tools:

| Matcher | Matches |
| --- | --- |
| `"fs_write"` or `"write"` | Write tool |
| `"execute_bash"` or `"shell"` | Shell execution |
| `"@git"` | All tools from git MCP server |
| `"@git/status"` | Specific MCP tool |
| `"*"` | All tools (built-in + MCP) |
| `"@builtin"` | Built-in tools only |

#### Configuration

- **`timeout_ms`** — Default 30,000ms (30s).
- **`cache_ttl_seconds`** — `0` = no caching (default); `> 0` = cache successful results. AgentSpawn hooks are never cached.

See [Agent Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference) for full syntax.

### Subagents

Kiro can delegate tasks to **subagents** — independent agents with their own context that run autonomously and return results.

```bash
> Use the backend agent to refactor the payment module
```

**Key capabilities:**
- Autonomous execution with isolated context
- Live progress tracking
- Parallel execution for multiple tasks
- Custom agent configurations for specialized workflows

**Available tools in subagents:** read, write, shell, code intelligence, MCP tools.
**Not available:** web_search, web_fetch, use_aws, grep, glob, thinking, todo_list.

### Custom Agents

Pre-define tool permissions, context resources, and behaviors:

```bash
kiro-cli agent list              # List available agents
kiro-cli agent create my-agent   # Create new agent
kiro-cli agent edit my-agent     # Edit agent config
kiro-cli agent validate ./a.json # Validate config file
kiro-cli agent set-default my-agent
```

**Benefits:** Pre-approved tool trust, limited tool access, auto-loaded project docs, shareable team configs.

### Steering (Project Context)

Provide persistent project knowledge via markdown files:

| Path | Scope |
| --- | --- |
| `.kiro/steering/` | Workspace — this project only |
| `~/.kiro/steering/` | Global — all projects |

Example structure:

```
.kiro/steering/
├── product.md           # Product overview
├── tech.md              # Tech stack
├── structure.md         # Project structure
└── api-standards.md     # API conventions
```

Also supports `AGENTS.md` in the project root or `~/.kiro/steering/`.

**In custom agents:** Add `"resources": ["file://.kiro/steering/**/*.md"]` to config.

### MCP Integration

Connect external tools and data sources via Model Context Protocol:

```bash
kiro-cli mcp add --name my-server --command "node server.js" --scope workspace
kiro-cli mcp list [workspace|global]
kiro-cli mcp status --name my-server
kiro-cli mcp remove --name my-server --scope workspace
```

---

## OpenCode

```bash
bash pty:true workdir:~/project command:"opencode run 'Your task'"
```

---

## Pi Coding Agent

```bash
# Install: npm install -g @mariozechner/pi-coding-agent

# Interactive
bash pty:true workdir:~/project command:"pi 'Your task'"

# Non-interactive (single response)
bash pty:true command:"pi -p 'Summarize src/'"

# Different provider/model
bash pty:true command:"pi --provider openai --model gpt-4o-mini -p 'Your task'"
```

---

## Parallel Issue Fixing (git worktrees)

Fix multiple issues simultaneously using isolated worktrees:

```bash
# 1. Create worktrees
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# 2. Launch agents (background + PTY)
bash pty:true workdir:/tmp/issue-78 background:true command:"pnpm install && codex --yolo 'Fix issue #78: <description>. Commit and push.'"
bash pty:true workdir:/tmp/issue-99 background:true command:"pnpm install && codex --yolo 'Fix issue #99: <description>. Commit and push.'"

# 3. Monitor
process action:list
process action:log sessionId:XXX

# 4. Create PRs
cd /tmp/issue-78 && git push -u origin fix/issue-78
gh pr create --repo user/repo --head fix/issue-78 --title "fix: ..." --body "..."

# 5. Clean up
git worktree remove /tmp/issue-78
git worktree remove /tmp/issue-99
```

---

## Rules

1. **Always use `pty:true`** — Coding agents need a pseudo-terminal.
2. **Respect tool choice** — If the user asks for Kiro, use Kiro; for Codex, use Codex. Do NOT hand-code patches yourself when orchestrating agents. If an agent fails or hangs, respawn it or ask the user — don't silently take over.
3. **Be patient** — Don't kill sessions just because they seem slow.
4. **Monitor with `process:log`** — Check progress without interfering.
5. **Codex auto-approve flags** — Use `--full-auto` (sandboxed) or `--yolo` (no sandbox) for building tasks.
6. **Kiro tool trust** — Use `--trust-all-tools` for automation; `--trust-tools` for restricted scope.
7. **Kiro one-shots** — Use `--no-interactive` for single-response queries.
8. **Parallel is OK** — Run multiple agent processes concurrently for batch work.
9. **Never start agents in `~/clawd/`** — Agents will read system docs and behave unpredictably.
10. **Never checkout branches in `~/Projects/openclaw/`** — That's the live OpenClaw instance.
11. **Suggest Kiro `/plan` for complex tasks** — When requirements are unclear or multi-step, suggest Plan Agent and let the user decide.
12. **Leverage Kiro skills** — If the project has `.kiro/skills/` or the user has `~/.kiro/skills/`, relevant skills activate automatically. No extra flags needed.

---

## Progress Updates

When you spawn coding agents in the background, keep the user informed:

- **On start** — 1 short message: what's running, where, and which agent.
- **On change** — Update only when something happens:
  - A milestone completes (build finished, tests passed)
  - The agent asks a question or needs input
  - An error occurs or user action is needed
  - The agent finishes (include what changed and where)
- **On kill** — Immediately say you killed it and why.

---

## Auto-Notify on Completion

For long-running tasks, append a wake trigger so OpenClaw is notified immediately when the agent finishes:

```
... your task here.

When completely finished, run this command to notify me:
openclaw gateway wake --text "Done: [brief summary]" --mode now
```

**Example:**

```bash
bash pty:true workdir:~/project background:true command:"codex --yolo exec 'Build a REST API for todos.

When completely finished, run: openclaw gateway wake --text \"Done: Built todos REST API with CRUD endpoints\" --mode now'"
```

This triggers an immediate wake event instead of waiting for the next heartbeat.

---

## Learnings

- **PTY is essential** — Without `pty:true`, output breaks or the agent hangs.
- **Git repo required for Codex** — Use `mktemp -d && git init` for scratch work.
- **`exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly.
- **`submit` vs `write`** — `submit` sends input + Enter; `write` sends raw data without newline.
- **Skills activate automatically** — No slash command needed; Kiro matches your request against skill descriptions.
- **Plan before complex builds** — `/plan` saves time on multi-step features by clarifying requirements upfront.
