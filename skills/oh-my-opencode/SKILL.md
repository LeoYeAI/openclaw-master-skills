---
name: oh-my-opencode
description: Multi-agent orchestration plugin for OpenCode. Use when the user wants to install, configure, or operate oh-my-opencode — including agent delegation, ultrawork mode, Prometheus planning, background tasks, category-based task routing, model resolution, tmux integration, or any oh-my-opencode feature. Covers installation, configuration, all agents (Sisyphus, Oracle, Librarian, Explore, Atlas, Prometheus, Metis, Momus), all categories, slash commands, hooks, skills, MCPs, and troubleshooting.
metadata:
  clawdbot:
    emoji: "🏔️"
    homepage: "https://github.com/code-yeongyu/oh-my-opencode"
    requires:
      bins: ["opencode"]
---

# Oh My OpenCode

Multi-agent orchestration plugin that transforms OpenCode into a full agent harness with specialized agents, background task execution, category-based model routing, and autonomous work modes.

**Package**: `oh-my-opencode` (install via `bunx oh-my-opencode install`)
**Repository**: https://github.com/code-yeongyu/oh-my-opencode
**Schema**: https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json

---

## Prerequisites

1. **OpenCode** installed and configured (`opencode --version` should be 1.0.150+)
   ```bash
   curl -fsSL https://opencode.ai/install | bash
   # or: npm install -g opencode-ai
   # or: bun install -g opencode-ai
   ```
2. At least one LLM provider authenticated (`opencode auth login`)
3. **Strongly recommended**: Anthropic Claude Pro/Max subscription (Sisyphus uses Claude Opus 4.5)

---

## Installation

Run the interactive installer:

```bash
bunx oh-my-opencode install
```

Non-interactive mode with provider flags:

```bash
bunx oh-my-opencode install --no-tui \
  --claude=<yes|no|max20> \
  --openai=<yes|no> \
  --gemini=<yes|no> \
  --copilot=<yes|no> \
  --opencode-zen=<yes|no> \
  --zai-coding-plan=<yes|no>
```

Verify:

```bash
opencode --version
cat ~/.config/opencode/opencode.json  # should contain "oh-my-opencode" in plugin array
```

---

## Two Workflow Modes

### Mode 1: Ultrawork (Quick Autonomous Work)

Include `ultrawork` or `ulw` in your prompt. That's it.

```
ulw add authentication to my Next.js app
```

The agent will automatically:
1. Explore your codebase to understand existing patterns
2. Research best practices via specialized background agents
3. Implement the feature following your conventions
4. Verify with diagnostics and tests
5. Keep working until 100% complete

### Mode 2: Prometheus (Precise Planned Work)

For complex or critical tasks:

1. **Press Tab** → switches to Prometheus (Planner) mode
2. **Describe your work** → Prometheus interviews you, asking clarifying questions while researching your codebase
3. **Confirm the plan** → review generated plan in `.sisyphus/plans/*.md`
4. **Run `/start-work`** → Atlas orchestrator takes over:
   - Distributes tasks to specialized sub-agents
   - Verifies each task completion independently
   - Accumulates learnings across tasks
   - Tracks progress across sessions (resume anytime)

**Critical rule**: Do NOT use Atlas without `/start-work`. Prometheus and Atlas are a pair — always use them together.

---

## Agents

All agents are enabled by default. Each has a default model and provider priority fallback chain.

| Agent | Role | Default Model | Provider Priority Chain |
|-------|------|---------------|------------------------|
| **Sisyphus** | Primary orchestrator | `claude-opus-4-5` | anthropic → kimi-for-coding → zai-coding-plan → openai → google |
| **Sisyphus-Junior** | Focused task executor (used by `delegate_task` with categories) | Determined by category | Per-category chain |
| **Hephaestus** | Autonomous deep worker — goal-oriented, explores before acting | `gpt-5.2-codex` (medium) | openai → github-copilot → opencode (requires gpt-5.2-codex) |
| **Oracle** | Architecture, debugging, high-IQ reasoning (read-only) | `gpt-5.2` | openai → google → anthropic |
| **Librarian** | Official docs, OSS search, remote codebase analysis | `glm-4.7` | zai-coding-plan → opencode → anthropic |
| **Explore** | Fast codebase grep (contextual search) | `claude-haiku-4-5` | anthropic → github-copilot → opencode |
| **Multimodal Looker** | Image/PDF/diagram analysis | `gemini-3-flash` | google → openai → zai-coding-plan → kimi-for-coding → anthropic → opencode |
| **Prometheus** | Work planner (interview-based plan generation) | `claude-opus-4-5` | anthropic → kimi-for-coding → openai → google |
| **Metis** | Pre-planning consultant (ambiguity/failure-point analysis) | `claude-opus-4-5` | anthropic → kimi-for-coding → openai → google |
| **Momus** | Plan reviewer (clarity, verifiability, completeness) | `gpt-5.2` | openai → anthropic → google |
| **Atlas** | Plan orchestrator (executes Prometheus plans via `/start-work`) | `k2p5` / `claude-sonnet-4-5` | kimi-for-coding → opencode → anthropic → openai → google |
| **OpenCode-Builder** | Default build agent (disabled by default when Sisyphus is active) | System default | System default |

### Agent Invocation

Agents are invoked via `delegate_task()` or the `--agent` CLI flag — NOT with `@` prefix.

```javascript
// Invoke a specific agent
delegate_task(subagent_type="oracle", prompt="Review this architecture...")

// Invoke via category (routes to Sisyphus-Junior with category model)
delegate_task(category="visual-engineering", load_skills=["frontend-ui-ux"], prompt="...")

// Background execution (non-blocking)
delegate_task(subagent_type="explore", run_in_background=true, prompt="Find auth patterns...")
```

CLI:

```bash
opencode --agent oracle
opencode run --agent librarian "Explain how auth works in this codebase"
```

### When to Use Which Agent

| Situation | Agent |
|-----------|-------|
| General coding tasks | Sisyphus (default) |
| Autonomous goal-oriented deep work | Hephaestus (requires gpt-5.2-codex) |
| Architecture decisions, debugging after 2+ failures | Oracle |
| Looking up library docs, finding OSS examples | Librarian |
| Finding code patterns in your codebase | Explore |
| Analyzing images, PDFs, diagrams | Multimodal Looker |
| Complex multi-day projects needing a plan | Prometheus + Atlas (via Tab → `/start-work`) |
| Pre-planning scope analysis | Metis |
| Reviewing a generated plan for gaps | Momus |
| Quick single-file changes | delegate_task with `quick` category |

---

## Categories

Categories route tasks to Sisyphus-Junior with domain-optimized models via `delegate_task()`.

| Category | Default Model | Variant | Provider Priority Chain | Best For |
|----------|---------------|---------|------------------------|----------|
| `visual-engineering` | `gemini-3-pro` | — | google → anthropic → zai-coding-plan | Frontend, UI/UX, design, styling, animation |
| `ultrabrain` | `gpt-5.2-codex` | `xhigh` | openai → google → anthropic | Deep logical reasoning, complex architecture |
| `deep` | `gpt-5.2-codex` | `medium` | openai → anthropic → google | Goal-oriented autonomous problem-solving (Hephaestus-style) |
| `artistry` | `gemini-3-pro` | `max` | google → anthropic → openai | Creative/novel approaches, unconventional solutions |
| `quick` | `claude-haiku-4-5` | — | anthropic → google → opencode | Trivial tasks, single file changes, typo fixes |
| `unspecified-low` | `claude-sonnet-4-5` | — | anthropic → openai → google | General tasks, low effort |
| `unspecified-high` | `claude-opus-4-5` | `max` | anthropic → openai → google | General tasks, high effort |
| `writing` | `gemini-3-flash` | — | google → anthropic → zai-coding-plan → openai | Documentation, prose, technical writing |

### Category Usage

```javascript
delegate_task(category="visual-engineering", load_skills=["frontend-ui-ux"], prompt="Create a dashboard component")
delegate_task(category="ultrabrain", load_skills=[], prompt="Design the payment processing flow")
delegate_task(category="quick", load_skills=["git-master"], prompt="Fix the typo in README.md")
delegate_task(category="deep", load_skills=[], prompt="Investigate and fix the memory leak in the worker pool")
```

### Critical: Model Resolution Priority

Categories do NOT use their built-in defaults unless configured. Resolution order:

1. **User-configured model** (in `oh-my-opencode.json`) — highest priority
2. **Category's built-in default** (if category is in config)
3. **System default model** (from `opencode.json`) — fallback

To use optimal models, add categories to your config. See [references/configuration.md](references/configuration.md).

---

## Built-in Skills

| Skill | Purpose | Usage |
|-------|---------|-------|
| `playwright` | Browser automation via Playwright MCP (default browser engine) | `load_skills=["playwright"]` |
| `agent-browser` | Vercel's agent-browser CLI with session management | Switch via `browser_automation_engine` config |
| `git-master` | Git expert: atomic commits, rebase/squash, history search | `load_skills=["git-master"]` |
| `frontend-ui-ux` | Designer-turned-developer for stunning UI/UX | `load_skills=["frontend-ui-ux"]` |

Skills are injected into subagents via `delegate_task(load_skills=[...])`.

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/init-deep` | Initialize hierarchical AGENTS.md knowledge base |
| `/start-work` | Execute a Prometheus plan with Atlas orchestrator |
| `/ralph-loop` | Start self-referential development loop until completion |
| `/ulw-loop` | Start ultrawork loop — continues until completion |
| `/cancel-ralph` | Cancel active Ralph Loop |
| `/refactor` | Intelligent refactoring with LSP, AST-grep, architecture analysis, TDD |
| `/stop-continuation` | Stop all continuation mechanisms (ralph loop, todo continuation, boulder) |

---

## Process Management

### Background Agents

Fire multiple agents in parallel for exploration and research:

```javascript
// Launch background agents (non-blocking)
delegate_task(subagent_type="explore", run_in_background=true, prompt="Find auth patterns in codebase")
delegate_task(subagent_type="librarian", run_in_background=true, prompt="Find JWT best practices")

// Collect results when needed
background_output(task_id="bg_abc123")

// Cancel all background tasks before final answer
background_cancel(all=true)
```

### Concurrency Configuration

```json
{
  "background_task": {
    "defaultConcurrency": 5,
    "staleTimeoutMs": 180000,
    "providerConcurrency": { "anthropic": 3, "google": 10 },
    "modelConcurrency": { "anthropic/claude-opus-4-5": 2 }
  }
}
```

Priority: `modelConcurrency` > `providerConcurrency` > `defaultConcurrency`

### Tmux Integration

Run background agents in separate tmux panes for visual multi-agent execution:

```json
{
  "tmux": {
    "enabled": true,
    "layout": "main-vertical",
    "main_pane_size": 60
  }
}
```

Requires running OpenCode in server mode inside a tmux session:

```bash
tmux new -s dev
opencode --port 4096
```

Layout options: `main-vertical` (default), `main-horizontal`, `tiled`, `even-horizontal`, `even-vertical`

---

## Parallel Execution Patterns

### Pattern 1: Explore + Librarian (Research Phase)

```javascript
// Internal codebase search
delegate_task(subagent_type="explore", run_in_background=true, prompt="Find how auth middleware is implemented")
delegate_task(subagent_type="explore", run_in_background=true, prompt="Find error handling patterns in the API layer")

// External documentation search
delegate_task(subagent_type="librarian", run_in_background=true, prompt="Find official JWT documentation and security recommendations")

// Continue working immediately — collect results when needed
```

### Pattern 2: Category-Based Delegation (Implementation Phase)

```javascript
// Frontend work → visual-engineering category
delegate_task(category="visual-engineering", load_skills=["frontend-ui-ux"], prompt="Build the settings page")

// Quick fix → quick category
delegate_task(category="quick", load_skills=["git-master"], prompt="Create atomic commit for auth changes")

// Hard problem → ultrabrain category
delegate_task(category="ultrabrain", load_skills=[], prompt="Design the caching invalidation strategy")
```

### Pattern 3: Session Continuity

```javascript
// First delegation returns a session_id
result = delegate_task(category="quick", load_skills=["git-master"], prompt="Fix the type error")
// session_id: "ses_abc123"

// Follow-up uses session_id to preserve full context
delegate_task(session_id="ses_abc123", prompt="Also fix the related test file")
```

---

## CLI Reference

### Core Commands

```bash
opencode                           # Start TUI
opencode --port 4096               # Start TUI with server mode (for tmux integration)
opencode -c                        # Continue last session
opencode -s <session-id>           # Continue specific session
opencode --agent <agent-name>      # Start with specific agent
opencode -m provider/model         # Start with specific model
```

### Non-Interactive Mode

```bash
opencode run "Explain closures in JavaScript"
opencode run --agent oracle "Review this architecture"
opencode run -m openai/gpt-5.2 "Complex reasoning task"
opencode run --format json "Query"    # Raw JSON output
```

### Auth & Provider Management

```bash
opencode auth login                # Add/configure a provider
opencode auth list                 # List authenticated providers
opencode auth logout               # Remove a provider
opencode models                    # List all available models
opencode models anthropic          # List models for specific provider
opencode models --refresh          # Refresh models cache
```

### Session Management

```bash
opencode session list              # List all sessions
opencode session list -n 10        # Last 10 sessions
opencode export <session-id>       # Export session as JSON
opencode import session.json       # Import session
opencode stats                     # Token usage and cost statistics
opencode stats --days 7            # Stats for last 7 days
```

### Plugin & MCP Management

```bash
bunx oh-my-opencode install        # Install/configure oh-my-opencode
bunx oh-my-opencode doctor         # Diagnose configuration issues
opencode mcp list                  # List configured MCP servers
opencode mcp add                   # Add an MCP server
```

### Server Mode

```bash
opencode serve --port 4096         # Headless server
opencode web --port 4096           # Server with web UI
opencode attach http://localhost:4096  # Attach TUI to running server
```

---

## Built-in MCPs

Oh My OpenCode includes these MCP servers out of the box:

| MCP | Tool | Purpose |
|-----|------|---------|
| **Exa** | `web_search_exa` | Web search with clean LLM-ready content |
| **Context7** | `resolve-library-id`, `query-docs` | Official library/framework documentation lookup |
| **Grep.app** | `searchGitHub` | Search real-world code examples from public GitHub repos |

---

## Hooks

All hooks are enabled by default. Disable specific hooks via `disabled_hooks` config:

| Hook | Purpose |
|------|---------|
| `todo-continuation-enforcer` | Forces agent to continue if it quits halfway |
| `context-window-monitor` | Monitors and manages context window usage |
| `session-recovery` | Recovers sessions after crashes |
| `session-notification` | Notifies on session events |
| `comment-checker` | Prevents AI from adding excessive code comments |
| `grep-output-truncator` | Truncates large grep outputs |
| `tool-output-truncator` | Truncates large tool outputs |
| `directory-agents-injector` | Injects AGENTS.md from subdirectories (auto-disabled on OpenCode 1.1.37+) |
| `directory-readme-injector` | Injects README.md context |
| `empty-task-response-detector` | Detects and handles empty task responses |
| `think-mode` | Extended thinking mode control |
| `anthropic-context-window-limit-recovery` | Recovers from Anthropic context limits |
| `rules-injector` | Injects project rules |
| `background-notification` | Notifies when background tasks complete |
| `auto-update-checker` | Checks for oh-my-opencode updates |
| `startup-toast` | Shows startup notification (sub-feature of auto-update-checker) |
| `keyword-detector` | Detects keywords like `ultrawork`/`ulw` to trigger modes |
| `agent-usage-reminder` | Reminds to use specialized agents |
| `non-interactive-env` | Handles non-interactive environments |
| `interactive-bash-session` | Manages interactive bash/tmux sessions |
| `compaction-context-injector` | Injects context during compaction |
| `thinking-block-validator` | Validates thinking blocks |
| `claude-code-hooks` | Claude Code compatibility hooks |
| `ralph-loop` | Ralph Loop continuation mechanism |
| `preemptive-compaction` | Triggers compaction before context overflow |
| `auto-slash-command` | Auto-triggers slash commands |
| `sisyphus-junior-notepad` | Notepad for Sisyphus-Junior subagents |
| `edit-error-recovery` | Recovers from edit errors |
| `delegate-task-retry` | Retries failed task delegations |
| `prometheus-md-only` | Enforces Prometheus markdown-only output |
| `start-work` | Handles /start-work command |
| `atlas` | Atlas orchestrator hook |

---

## Best Practices

### Do

- **Use `ulw` for quick autonomous tasks** — just include the keyword in your prompt
- **Use Prometheus + `/start-work` for complex projects** — interview-based planning leads to better outcomes
- **Configure categories for your providers** — ensures optimal model selection instead of falling back to system default
- **Fire explore/librarian agents in parallel** — always use `run_in_background=true`
- **Use session continuity** — pass `session_id` for follow-up interactions with the same subagent
- **Let the agent delegate** — Sisyphus is an orchestrator, not a solo implementer
- **Run `bunx oh-my-opencode doctor`** to diagnose issues

### Don't

- **Don't use Atlas without `/start-work`** — Atlas requires a Prometheus plan
- **Don't manually specify models for every agent** — the fallback chain handles this
- **Don't disable `todo-continuation-enforcer`** — it's what keeps the agent completing work
- **Don't use Claude Haiku for Sisyphus** — Opus 4.5 is strongly recommended
- **Don't run explore/librarian synchronously** — always background them

### When to Use This Skill

- Installing or configuring oh-my-opencode
- Understanding agent roles and delegation patterns
- Troubleshooting model resolution or provider issues
- Setting up tmux integration for visual multi-agent execution
- Configuring categories for cost optimization
- Understanding the ultrawork vs Prometheus workflow choice

### When NOT to Use This Skill

- General OpenCode usage unrelated to oh-my-opencode plugin features
- Provider authentication issues (use `opencode auth` directly)
- OpenCode core configuration (use OpenCode docs at https://opencode.ai/docs/)

---

## Rules for the Agent

1. **Package name is `oh-my-opencode`** — NOT `@anthropics/opencode` or any other name
2. **Use `bunx` (officially recommended)** — not `npx` for oh-my-opencode CLI commands
3. **Agent invocation uses `--agent` flag or `delegate_task()`** — NOT `@agent` prefix
4. **Never change model settings or disable features** unless the user explicitly requests it
5. **Sisyphus strongly recommends Opus 4.5** — using other models degrades the experience significantly
6. **Categories do NOT use built-in defaults unless configured** — always verify with `bunx oh-my-opencode doctor --verbose`
7. **Prometheus and Atlas are always paired** — never use Atlas without a Prometheus plan
8. **Background agents should always use `run_in_background=true`** — never block on exploration
9. **Session IDs should be preserved and reused** — saves 70%+ tokens on follow-ups
10. **When using Ollama, set `stream: false`** — required to avoid JSON parse errors

---

## Auto-Notify on Completion

Background tasks automatically notify when complete via the `background-notification` hook. No polling needed — the system pushes completion events. Use `background_output(task_id="...")` only when you need to read the result.

---

## Reference Documents

- [Configuration Reference](references/configuration.md) — Complete config with all agents, categories, provider chains, hooks, and options
- [Troubleshooting Guide](references/troubleshooting.md) — Common issues and solutions
