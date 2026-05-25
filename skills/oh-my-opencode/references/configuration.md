# Oh My OpenCode — Configuration Reference

Complete configuration reference for oh-my-opencode. All settings go in `oh-my-opencode.json` (or `.jsonc`).

## Config File Locations

Priority order (higher overrides lower):

1. `.opencode/oh-my-opencode.json` (project-level)
2. `~/.config/opencode/oh-my-opencode.json` (user-level)

When both `.jsonc` and `.json` exist, `.jsonc` takes priority.

### JSONC Support

The config file supports JSONC (JSON with Comments):
- Line comments: `// comment`
- Block comments: `/* comment */`
- Trailing commas: `{ "key": "value", }`

### Schema Autocomplete

```json
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json"
}
```

---

## Agents

Override built-in agent settings. Each agent supports:

`model`, `variant`, `temperature`, `top_p`, `prompt`, `prompt_append`, `tools`, `disable`, `description`, `mode`, `color`, `permission`, `category`, `skills`, `maxTokens`, `thinking`, `reasoningEffort`, `textVerbosity`, `providerOptions`

### Agent Defaults and Provider Chains

| Agent | Default Model (no prefix) | Provider Priority Chain | Purpose |
|-------|---------------------------|------------------------|---------|
| **Sisyphus** | `claude-opus-4-5` | anthropic → kimi-for-coding → zai-coding-plan → openai → google | Primary orchestrator |
| **Sisyphus-Junior** | Per category | Per category | Focused task executor |
| **Hephaestus** | `gpt-5.2-codex` (medium) | openai → github-copilot → opencode | Autonomous deep worker (requires gpt-5.2-codex) |
| **Oracle** | `gpt-5.2` | openai → google → anthropic | Architecture, debugging |
| **Librarian** | `glm-4.7` | zai-coding-plan → opencode → anthropic | Docs/OSS search |
| **Explore** | `claude-haiku-4-5` | anthropic → github-copilot → opencode | Codebase grep |
| **Multimodal Looker** | `gemini-3-flash` | google → openai → zai-coding-plan → kimi-for-coding → anthropic → opencode | Media analysis |
| **Prometheus (Planner)** | `claude-opus-4-5` | anthropic → kimi-for-coding → openai → google | Work planning |
| **Metis (Plan Consultant)** | `claude-opus-4-5` | anthropic → kimi-for-coding → openai → google | Pre-planning analysis |
| **Momus (Plan Reviewer)** | `gpt-5.2` | openai → anthropic → google | Plan review |
| **Atlas** | `k2p5` / `claude-sonnet-4-5` | kimi-for-coding → opencode → anthropic → openai → google | Plan orchestration |
| **OpenCode-Builder** | System default | System default | Default build agent (disabled by default) |

### Agent Configuration Example

```jsonc
{
  "agents": {
    "oracle": {
      "model": "openai/gpt-5.2",
      "temperature": 0.3
    },
    "explore": {
      "model": "anthropic/claude-haiku-4-5"
    },
    "librarian": {
      "model": "zai-coding-plan/glm-4.7",
      "prompt_append": "Always use the elisp-dev-mcp for Emacs Lisp documentation lookups."
    },
    "multimodal-looker": {
      "disable": true  // Disable an agent entirely
    }
  }
}
```

### Configuring Sisyphus and Builder Names

Use the exact names as config keys:

```jsonc
{
  "agents": {
    "Sisyphus": { "model": "anthropic/claude-opus-4-5" },
    "OpenCode-Builder": { "model": "anthropic/claude-opus-4" },
    "Prometheus (Planner)": { "model": "openai/gpt-5.2" },
    "Metis (Plan Consultant)": { "model": "anthropic/claude-sonnet-4-5" }
  }
}
```

### Thinking Options (Anthropic Models)

```json
{
  "agents": {
    "oracle": {
      "thinking": {
        "type": "enabled",
        "budgetTokens": 200000
      }
    }
  }
}
```

| Option | Type | Description |
|--------|------|-------------|
| `type` | string | `enabled` or `disabled` |
| `budgetTokens` | number | Maximum budget tokens for extended thinking |

### Additional Agent Options

| Option | Type | Description |
|--------|------|-------------|
| `category` | string | Inherit model/settings from a category |
| `variant` | string | Model variant: `max`, `high`, `medium`, `low`, `xhigh` |
| `maxTokens` | number | Maximum tokens for response |
| `reasoningEffort` | string | OpenAI reasoning effort: `low`, `medium`, `high`, `xhigh` |
| `textVerbosity` | string | Text verbosity: `low`, `medium`, `high` |
| `providerOptions` | object | Provider-specific options passed to SDK |
| `prompt_append` | string | Extra instructions added to (not replacing) the default system prompt |

### Permission Options

Fine-grained control over what agents can do:

```json
{
  "agents": {
    "explore": {
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "webfetch": "allow"
      }
    }
  }
}
```

| Permission | Description | Values |
|------------|-------------|--------|
| `edit` | File editing | `ask` / `allow` / `deny` |
| `bash` | Bash execution | `ask` / `allow` / `deny` or per-command: `{ "git": "allow", "rm": "deny" }` |
| `webfetch` | Web requests | `ask` / `allow` / `deny` |
| `doom_loop` | Infinite loop detection override | `ask` / `allow` / `deny` |
| `external_directory` | Access files outside project root | `ask` / `allow` / `deny` |

### Disabling Agents

```json
{
  "disabled_agents": ["oracle", "multimodal-looker"]
}
```

Available agents for disabling: `sisyphus`, `prometheus`, `oracle`, `librarian`, `explore`, `multimodal-looker`, `metis`, `momus`, `atlas`

---

## Categories

Categories enable domain-specific task delegation via `delegate_task`. Each category applies runtime presets to Sisyphus-Junior.

### Category Defaults and Provider Chains

| Category | Default Model (no prefix) | Variant | Provider Priority Chain |
|----------|---------------------------|---------|------------------------|
| `visual-engineering` | `gemini-3-pro` | — | google → anthropic → zai-coding-plan |
| `ultrabrain` | `gpt-5.2-codex` | `xhigh` | openai → google → anthropic |
| `deep` | `gpt-5.2-codex` | `medium` | openai → anthropic → google |
| `artistry` | `gemini-3-pro` | `max` | google → anthropic → openai |
| `quick` | `claude-haiku-4-5` | — | anthropic → google → opencode |
| `unspecified-low` | `claude-sonnet-4-5` | — | anthropic → openai → google |
| `unspecified-high` | `claude-opus-4-5` | `max` | anthropic → openai → google |
| `writing` | `gemini-3-flash` | — | google → anthropic → zai-coding-plan → openai |

### Recommended Category Configuration

To use optimal models per category, explicitly add them to your config:

```jsonc
{
  "categories": {
    "visual-engineering": { "model": "google/gemini-3-pro-preview" },
    "ultrabrain": { "model": "openai/gpt-5.2-codex", "variant": "xhigh" },
    "deep": { "model": "openai/gpt-5.2-codex" },
    "artistry": { "model": "google/gemini-3-pro-preview", "variant": "max" },
    "quick": { "model": "anthropic/claude-haiku-4-5" },
    "unspecified-low": { "model": "anthropic/claude-sonnet-4-5" },
    "unspecified-high": { "model": "anthropic/claude-opus-4-5", "variant": "max" },
    "writing": { "model": "google/gemini-3-flash-preview" }
  }
}
```

**Only configure categories for providers you have access to.** Unconfigured categories fall back to your system default model.

### Category Options

Each category supports:

| Option | Type | Description |
|--------|------|-------------|
| `model` | string | Override model for this category |
| `temperature` | number | Temperature (0-2) |
| `top_p` | number | Top-p sampling (0-1) |
| `maxTokens` | number | Maximum response tokens |
| `thinking` | object | Extended thinking config (Anthropic) |
| `reasoningEffort` | string | Reasoning effort (OpenAI) |
| `textVerbosity` | string | Text verbosity level |
| `tools` | object | Tool whitelist |
| `prompt_append` | string | Additional prompt instructions |
| `variant` | string | Model variant |
| `description` | string | Human-readable description |
| `is_unstable_agent` | boolean | Force background mode for monitoring (auto-enabled for Gemini) |

### Custom Categories

```json
{
  "categories": {
    "data-science": {
      "model": "anthropic/claude-sonnet-4-5",
      "temperature": 0.2,
      "prompt_append": "Focus on data analysis, ML pipelines, and statistical methods."
    }
  }
}
```

---

## Model Resolution System

3-step resolution to determine which model to use at runtime:

```
Step 1: USER OVERRIDE
  → User specified model in oh-my-opencode.json? Use exactly as specified.
  → No? Continue to Step 2.

Step 2: PROVIDER PRIORITY FALLBACK
  → For each provider in the agent/category's priority chain:
    Try: provider/default-model
    Found in available models? → Use it.
    Not found? → Try next provider.

Step 3: SYSTEM DEFAULT
  → Return systemDefaultModel (from opencode.json)
```

### Checking Resolution

```bash
bunx oh-my-opencode doctor --verbose
```

Shows each agent/category's model requirement, provider fallback chain, user overrides, and effective resolution path.

---

## Sisyphus Agent Configuration

```json
{
  "sisyphus_agent": {
    "disabled": false,
    "default_builder_enabled": false,
    "planner_enabled": true,
    "replace_plan": true
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `disabled` | `false` | Disable all Sisyphus orchestration, restore original build/plan |
| `default_builder_enabled` | `false` | Enable OpenCode-Builder alongside Sisyphus |
| `planner_enabled` | `true` | Enable Prometheus (Planner) with work-planner methodology |
| `replace_plan` | `true` | Demote default plan agent to subagent mode |

---

## Background Tasks

```json
{
  "background_task": {
    "defaultConcurrency": 5,
    "staleTimeoutMs": 180000,
    "providerConcurrency": {
      "anthropic": 3,
      "openai": 5,
      "google": 10
    },
    "modelConcurrency": {
      "anthropic/claude-opus-4-5": 2,
      "google/gemini-3-flash": 10
    }
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `defaultConcurrency` | — | Default max concurrent background tasks |
| `staleTimeoutMs` | `180000` | Interrupt tasks with no activity for this duration (min: 60000ms) |
| `providerConcurrency` | — | Per-provider concurrency limits |
| `modelConcurrency` | — | Per-model concurrency limits (overrides provider limits) |

---

## Browser Automation

```json
{
  "browser_automation_engine": {
    "provider": "playwright"
  }
}
```

| Provider | Interface | Installation |
|----------|-----------|-------------|
| `playwright` (default) | MCP tools | Auto-installed via npx |
| `agent-browser` | Bash CLI | Requires `bun add -g agent-browser && agent-browser install` |

---

## Skills Configuration

```jsonc
{
  "skills": {
    "sources": [
      { "path": "./custom-skills", "recursive": true },
      "https://example.com/skill.yaml"
    ],
    "enable": ["my-custom-skill"],
    "disable": ["other-skill"],
    "my-skill": {
      "description": "Custom skill description",
      "template": "Custom prompt template",
      "from": "source-file.ts",
      "model": "custom/model",
      "agent": "custom-agent",
      "subtask": true,
      "argument-hint": "usage hint",
      "license": "MIT",
      "compatibility": ">= 3.0.0",
      "metadata": { "author": "Your Name" },
      "allowed-tools": ["tool1", "tool2"]
    }
  }
}
```

### Disabling Built-in Skills

```json
{
  "disabled_skills": ["playwright"]
}
```

Available built-in skills: `playwright`, `frontend-ui-ux`, `git-master`

---

## Tmux Integration

```json
{
  "tmux": {
    "enabled": true,
    "layout": "main-vertical",
    "main_pane_size": 60,
    "main_pane_min_width": 120,
    "agent_pane_min_width": 40
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `false` | Enable tmux subagent pane spawning |
| `layout` | `main-vertical` | Layout for agent panes |
| `main_pane_size` | `60` | Main pane size as percentage (20-80) |
| `main_pane_min_width` | `120` | Minimum width for main pane in columns |
| `agent_pane_min_width` | `40` | Minimum width for each agent pane |

### Layout Options

| Layout | Description |
|--------|-------------|
| `main-vertical` | Main pane left, agent panes stacked right (default) |
| `main-horizontal` | Main pane top, agent panes stacked bottom |
| `tiled` | All panes in equal-sized grid |
| `even-horizontal` | All panes in horizontal row |
| `even-vertical` | All panes in vertical stack |

### Requirements

1. Must run inside an existing tmux session
2. Tmux installed and in PATH
3. OpenCode running with `--port` flag (server mode)

### Running with Tmux

```bash
tmux new -s dev
opencode --port 4096
# Background agents now appear in separate panes
```

### Shell Function (Bash/Zsh)

```bash
oc() {
    local base_name=$(basename "$PWD")
    local path_hash=$(echo "$PWD" | md5sum | cut -c1-4)
    local session_name="${base_name}-${path_hash}"
    local port=4096
    while [ $port -lt 5096 ]; do
        if ! lsof -i :$port >/dev/null 2>&1; then break; fi
        port=$((port + 1))
    done
    export OPENCODE_PORT=$port
    if [ -n "$TMUX" ]; then
        opencode --port $port "$@"
    else
        local oc_cmd="OPENCODE_PORT=$port opencode --port $port $*; exec $SHELL"
        if tmux has-session -t "$session_name" 2>/dev/null; then
            tmux new-window -t "$session_name" -c "$PWD" "$oc_cmd"
            tmux attach-session -t "$session_name"
        else
            tmux new-session -s "$session_name" -c "$PWD" "$oc_cmd"
        fi
    fi
}
```

---

## Git Master

```json
{
  "git_master": {
    "commit_footer": true,
    "include_co_authored_by": true
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `commit_footer` | `true` | Adds "Ultraworked with Sisyphus" footer to commits |
| `include_co_authored_by` | `true` | Adds `Co-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>` trailer |

---

## Google Auth (Antigravity OAuth)

For Gemini models, install the `opencode-antigravity-auth` plugin:

```json
{
  "plugin": [
    "oh-my-opencode",
    "opencode-antigravity-auth@latest"
  ]
}
```

Features: multi-account load balancing (up to 10 accounts), variant-based thinking levels, dual quota system (Antigravity + Gemini CLI).

### Available Antigravity Models

**Antigravity quota:**
- `google/antigravity-gemini-3-pro` — variants: `low`, `high`
- `google/antigravity-gemini-3-flash` — variants: `minimal`, `low`, `medium`, `high`
- `google/antigravity-claude-sonnet-4-5` — no variants
- `google/antigravity-claude-sonnet-4-5-thinking` — variants: `low`, `max`
- `google/antigravity-claude-opus-4-5-thinking` — variants: `low`, `max`

**Gemini CLI quota:**
- `google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `google/gemini-3-flash-preview`, `google/gemini-3-pro-preview`

### Agent Model Override for Antigravity

```json
{
  "agents": {
    "multimodal-looker": { "model": "google/antigravity-gemini-3-flash" }
  }
}
```

Authenticate:
```bash
opencode auth login
# Provider: Google → Login method: OAuth with Google (Antigravity)
```

---

## Ollama Provider

**IMPORTANT**: Set `stream: false` when using Ollama to avoid JSON parse errors.

```json
{
  "agents": {
    "explore": {
      "model": "ollama/qwen3-coder",
      "stream": false
    }
  }
}
```

Ollama returns NDJSON when streaming, but the SDK expects a single JSON object. `stream: false` is the required workaround.

Supported models: `ollama/qwen3-coder`, `ollama/ministral-3:14b`, `ollama/lfm2.5-thinking`

---

## Hooks

All hooks are enabled by default. Disable via `disabled_hooks`:

```json
{
  "disabled_hooks": ["comment-checker", "agent-usage-reminder"]
}
```

### All Available Hooks

`todo-continuation-enforcer`, `context-window-monitor`, `session-recovery`, `session-notification`, `comment-checker`, `grep-output-truncator`, `tool-output-truncator`, `directory-agents-injector`, `directory-readme-injector`, `empty-task-response-detector`, `think-mode`, `anthropic-context-window-limit-recovery`, `rules-injector`, `background-notification`, `auto-update-checker`, `startup-toast`, `keyword-detector`, `agent-usage-reminder`, `non-interactive-env`, `interactive-bash-session`, `compaction-context-injector`, `thinking-block-validator`, `claude-code-hooks`, `ralph-loop`, `preemptive-compaction`, `auto-slash-command`, `sisyphus-junior-notepad`, `edit-error-recovery`, `delegate-task-retry`, `prometheus-md-only`, `start-work`, `atlas`

**Notes:**
- `directory-agents-injector` is auto-disabled on OpenCode 1.1.37+ (native support via PR #10678)
- `startup-toast` is a sub-feature of `auto-update-checker` — disable independently if needed

---

## Disabled Commands

```json
{
  "disabled_commands": ["init-deep"]
}
```

Available commands for disabling: `init-deep`, `start-work`

---

## Disabled MCPs

Disable built-in MCP servers:

```json
{
  "disabled_mcps": ["websearch", "context7"]
}
```

---

## Experimental Features

```json
{
  "experimental": {
    "aggressive_truncation": true
  }
}
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENCODE_PORT` | Default port for HTTP server (used if `--port` not specified) |
| `OPENCODE_ENABLE_EXA` | Enable Exa web search tools |
| `OPENCODE_SERVER_PASSWORD` | Enable basic auth for `serve`/`web` |

See the [OpenCode CLI docs](https://opencode.ai/docs/cli/) for the full list of OpenCode environment variables.

---

## Full Example Configuration

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json",

  // Agent overrides
  "agents": {
    "oracle": { "model": "openai/gpt-5.2" },
    "librarian": { "model": "zai-coding-plan/glm-4.7" },
    "explore": { "model": "opencode/gpt-5-nano" },
    "multimodal-looker": { "model": "google/antigravity-gemini-3-flash" }
  },

  // Category overrides for optimal model routing
  "categories": {
    "visual-engineering": { "model": "google/gemini-3-pro-preview" },
    "ultrabrain": { "model": "openai/gpt-5.2-codex", "variant": "xhigh" },
    "deep": { "model": "openai/gpt-5.2-codex" },
    "quick": { "model": "anthropic/claude-haiku-4-5" },
    "writing": { "model": "google/gemini-3-flash-preview" }
  },

  // Background task concurrency
  "background_task": {
    "defaultConcurrency": 5,
    "providerConcurrency": { "anthropic": 3, "google": 10 }
  },

  // Tmux multi-pane agents
  "tmux": {
    "enabled": true,
    "layout": "main-vertical",
    "main_pane_size": 60
  },

  // Git commit styling
  "git_master": {
    "commit_footer": true,
    "include_co_authored_by": true
  },

  // Experimental features
  "experimental": {
    "aggressive_truncation": true
  }
}
```
