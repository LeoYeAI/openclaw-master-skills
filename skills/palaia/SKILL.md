---
name: palaia
version: "2.4"
description: >
  Local, crash-safe persistent memory for OpenClaw agents.
  SQLite-backed by default. Semantic search, projects, scopes, auto-capture.
  After installing or updating, run: palaia doctor --fix to complete setup.
metadata:
  openclaw:
    emoji: "\U0001F9E0"
    requires:
      bins: ["palaia"]
    install:
      - id: pip
        kind: pip
        package: "palaia[fastembed]"
        bins: ["palaia"]
        label: "Install Palaia with semantic search (pip)"
    postInstall:
      - command: "palaia init"
        label: "Initialize Palaia store"
      - command: "npm install -g @byte5ai/palaia@latest"
        label: "Install OpenClaw plugin (npm)"
    postUpdate:
      - command: "python3 -m pip install --upgrade 'palaia[fastembed]' && (npm install -g @byte5ai/palaia@latest 2>/dev/null || true) && palaia doctor --fix && palaia warmup"
        label: "Upgrade Palaia with semantic search (pip + npm plugin) and run health checks"
    postUpdateMessage: >
      Palaia has been updated to v2.4. New: session continuity (automatic briefings and
      summaries), privacy markers, recency boost, progressive disclosure. Run `palaia doctor --fix` to upgrade.
    plugin:
      slot: memory
      package: "@byte5ai/palaia"
---

# Palaia v2.4 — Agent Memory Skill

Palaia is the memory system for OpenClaw agents. It gives you persistent, searchable, crash-safe memory across sessions. You don't need to understand how it works — just use the commands below.

<!-- begin:install -->
## First-Time Setup

When a user asks you to "set up palaia", "enable memory", or "remember things across sessions", run these steps:

```bash
pip install "palaia[fastembed]"
```

```bash
palaia init
```

This creates `.palaia/` with SQLite storage and automatically configures fastembed for semantic search. No manual configuration needed.

Confirm success to the user: "Memory is ready. I'll automatically remember important context from our conversations."

If `pip` is not available, try alternatives in this order:
```bash
python3 -m pip install "palaia[fastembed]"
uv tool install "palaia[fastembed]"
pipx install "palaia[fastembed]"
```

Optional extras (install as needed):
```bash
pip install "palaia[mcp]"          # MCP server for Claude Desktop, Cursor
pip install "palaia[curate]"       # Knowledge curation
```

Note: `palaia[fastembed]` already includes sqlite-vec for native SIMD vector search. No separate install needed.

### OpenClaw Plugin Setup (for Auto-Capture and Auto-Recall)

After the CLI is installed, wire it into OpenClaw:

```bash
npm install -g @byte5ai/palaia@latest
```

Then activate in OpenClaw config (read existing values first, never overwrite arrays):
```bash
PALAIA_PATH="$(npm root -g)/@byte5ai/palaia"
```

Add to `openclaw.json`:
```json
{
  "plugins": {
    "load": { "paths": ["<PALAIA_PATH>"] },
    "allow": ["..existing..", "palaia"],
    "slots": { "memory": "palaia" },
    "entries": { "palaia": { "enabled": true } }
  }
}
```

Restart the gateway and verify:
```bash
openclaw gateway restart
palaia doctor
```

### Agent Identity (optional)

Single-agent systems work with the default name. For multi-agent setups:
```bash
palaia init --agent YOUR_AGENT_NAME
```

## Updating Palaia

When the user asks to update, or when `palaia status` shows a version mismatch:

```bash
palaia upgrade
```
This auto-detects the install method (pip/uv/pipx), preserves all installed extras (fastembed, mcp, sqlite-vec, curate), runs `palaia doctor --fix`, and upgrades the OpenClaw plugin if installed. No manual steps needed.

**If `palaia upgrade` is not recognized** (versions before v2.3.0), update manually:

```bash
# Step 1: Find install method
which palaia

# Step 2: Upgrade (use the method matching the path from Step 1)
# pip (path contains site-packages or .local):
pip install --upgrade "palaia[fastembed]"
# uv (path contains uv):
uv tool install "palaia[fastembed]"
# pipx (path contains pipx):
pipx install "palaia[fastembed]" --force

# Step 3: Health check + migration
palaia doctor --fix

# Step 4: Update OpenClaw plugin (if installed)
npm install -g @byte5ai/palaia@latest
```

After the manual update, `palaia upgrade` will be available for future updates.
<!-- end:install -->

## Auto-Check (run every time this skill is loaded)

Before doing anything else with Palaia, run `palaia doctor` silently. If it reports ANY warnings, address them immediately by following `palaia doctor --fix` recommendations. Do not proceed with other Palaia tasks until doctor reports no issues.

---

## Core Concepts

### Auto-Capture
Conversations are automatically captured when the OpenClaw plugin is active. You do NOT need to manually write things from conversations — Palaia handles it. Manual `palaia write` is only for structured knowledge: processes, tasks, and knowledge from external sources.

### Three Tiers
- **HOT** — Active memories (< 7 days or frequently accessed). Always searched.
- **WARM** — Aging memories (7-30 days). Searched by default.
- **COLD** — Archived memories (> 30 days). Only searched with `--all`.

### Scopes
- **private** — Only the writing agent can read it
- **team** — All agents in the workspace can read it (default)
- **public** — Exportable and shareable across workspaces

### Entry Types
- **memory** — Facts, decisions, learnings (default)
- **process** — Workflows, checklists, SOPs
- **task** — Action items with status, priority, assignee, due date

---

## Storage & Search

### Database Backends

| Backend | Use Case | Vector Search | Install |
|---------|----------|---------------|---------|
| **SQLite** (default) | Local, single-agent or small team | sqlite-vec (native KNN) or Python fallback | Included |
| **PostgreSQL** | Distributed teams, multiple hosts | pgvector (ANN, IVFFlat/HNSW) | `pip install 'palaia[postgres]'` |

SQLite is zero-config — `palaia init` creates a single `palaia.db` file with WAL mode for crash safety. For teams with agents on multiple machines, PostgreSQL centralizes the store:
```bash
palaia config set database_url postgresql://user:pass@host/db
# or: export PALAIA_DATABASE_URL=postgresql://...
```

### Semantic Vector Search

Palaia uses **hybrid search**: BM25 keyword matching (always active) combined with semantic vector embeddings (when a provider is configured). This finds memories by meaning, not just keywords.

**Embedding providers** (checked in chain order, first available wins):

| Provider | Type | Latency | Install |
|----------|------|---------|---------|
| **fastembed** | Local (CPU) | ~10ms/query | `pip install 'palaia[fastembed]'` (default) |
| **sentence-transformers** | Local (CPU/GPU) | ~10ms/query | `pip install 'palaia[sentence-transformers]'` |
| **Ollama** | Local (server) | ~50ms/query | `ollama pull nomic-embed-text` |
| **OpenAI** | API | ~200ms/query | Set `OPENAI_API_KEY` |
| **Gemini** | API | ~200ms/query | Set `GEMINI_API_KEY` |
| **BM25** | Built-in | <1ms/query | Always available (keyword only) |

Configure the chain: `palaia config set embedding_chain '["fastembed", "bm25"]'`

Check what's available: `palaia detect`

### Embed Server (Performance)

For fast CLI queries, palaia runs a background embed-server that keeps the model loaded in memory:
```bash
palaia embed-server --socket --daemon   # Start background server
palaia embed-server --status            # Check if running
palaia embed-server --stop              # Stop server
```
Without the server, each CLI call loads the model fresh (~3-5s). With the embed-server: **~1.5s per CLI query** (Python startup + server call) or **<500ms via MCP/Plugin** (no CLI overhead).

The OpenClaw plugin starts the embed-server automatically. For CLI-only usage, it auto-starts on first query when a local provider (fastembed, sentence-transformers) is configured.

### MCP Server (Claude Desktop, Cursor, any MCP host)

Palaia works as a standalone MCP memory server — **no OpenClaw required**. Any AI tool that supports MCP can use palaia as persistent local memory.

```bash
pip install 'palaia[mcp]'
palaia-mcp                              # Start MCP server (stdio)
palaia-mcp --root /path/to/.palaia      # Explicit store
palaia-mcp --read-only                  # No writes (untrusted hosts)
```

**Claude Desktop** (`~/.config/claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "palaia": {
      "command": "palaia-mcp",
      "args": []
    }
  }
}
```

**Cursor** (Settings → MCP Servers → Add, or `.cursor/mcp.json`):
- Command: `palaia-mcp`
- Arguments: (none, or `--root /path/to/.palaia`)

**Claude Code** (`~/.claude/settings.json`):
```json
{"mcpServers": {"palaia": {"command": "palaia-mcp"}}}
```

**MCP Tools:**

| Tool | Purpose |
|------|---------|
| `palaia_search` | Semantic + keyword search across all memories |
| `palaia_store` | Save new memory (fact, process, task) |
| `palaia_read` | Read a specific entry by ID |
| `palaia_edit` | Update an existing entry |
| `palaia_list` | List entries by tier, type, or project |
| `palaia_status` | Show store health, entry counts, provider info |
| `palaia_gc` | Run garbage collection (tier rotation) |

**Read-only mode** (`--read-only`): Disables `palaia_store`, `palaia_edit`, `palaia_gc`. Use this when connecting untrusted AI tools that should only read memories, not modify them.

---

## Commands Reference

### `palaia write` — Save structured knowledge

Only use for explicit process/task entries, or knowledge from external sources. Conversation knowledge is auto-captured.

```bash
# Save a fact from outside the conversation
palaia write "API rate limit is 100 req/min" --type memory --tags api,limits

# Record a step-by-step process
palaia write "1. Build 2. Test 3. Deploy" --type process --project myapp

# Create a task with structured fields
palaia write "fix login bug" --type task --priority high --assignee Elliot --due-date 2026-04-01

# Save to a specific project with scope
palaia write "Use JWT for auth" --project backend --scope team --tags decision
```

### `palaia query` — Semantic search

Find memories by meaning, not just keywords.

```bash
# Basic search
palaia query "what's the rate limit"

# Filter by type and status
palaia query "tasks" --type task --status open

# Filter by tags
palaia query "session-summary" --tags session-summary

# Search within a project
palaia query "deploy steps" --project myapp

# Include archived (COLD) entries
palaia query "old decisions" --all

# Search across all projects
palaia query "authentication" --cross-project

# Time-filtered search
palaia query "deploy" --after 2026-03-01 --before 2026-03-15

# RAG-formatted output for LLM injection
palaia query "how does auth work" --project api --rag
```

### `palaia get` — Read a specific entry

```bash
palaia get <entry-id>
palaia get <entry-id> --from 5 --lines 20   # Read a portion
```

Use when you have an entry ID from a query result or nudge message.

### `palaia list` — Browse entries

```bash
# List active entries
palaia list

# Filter by tier, type, status
palaia list --tier warm --type task --status open --priority high

# Limit results
palaia list --type task --status open --limit 5

# Filter by project or assignee
palaia list --project myapp --assignee Elliot
```

### `palaia status` — System health check

```bash
palaia status
```

Shows: entry counts per tier, entry class breakdown (memory/process/task), active providers, index health, version info. Run this when something seems off or to verify setup.

### `palaia project` — Project context management

```bash
palaia project create myapp --description "Main application" --default-scope team
palaia project list
palaia project show myapp
palaia project query myapp "deploy steps"
palaia project write myapp "New convention: use snake_case" --tags convention
palaia project set-scope myapp private
palaia project delete myapp   # Entries preserved, just untagged
```

### `palaia memo` — Inter-agent messaging

```bash
palaia memo send AgentName "Important update about project X"
palaia memo broadcast "New process available"
palaia memo inbox              # Check for messages
palaia memo ack <memo-id>      # Mark as read
```

### `palaia priorities` — Injection priority management (NEW in v2.2)

Control which memories are injected into each agent's context.

```bash
# Show what would be injected (with score breakdown)
palaia priorities

# Block an entry from injection for a specific agent
palaia priorities block <entry-id> --agent orchestrator

# Set per-agent injection thresholds
palaia priorities set recallMinScore 0.8 --agent orchestrator

# Adjust type weights per agent
palaia priorities set typeWeight.process 0.5 --agent orchestrator
```

Config stored in `.palaia/priorities.json` with layered overrides: global -> per-agent -> per-project.

### `palaia curate analyze/apply` — Knowledge curation (NEW in v2.2)

For migrating knowledge to a new instance, cleaning up old entries, or reviewing accumulated knowledge.

```bash
# Analyze: clusters entries, detects duplicates, recommends KEEP/MERGE/DROP
palaia curate analyze --project myapp

# Apply: parses the user-edited report, produces clean export package
palaia curate apply report.md
```

Requires optional dependency: `pip install palaia[curate]` (adds scikit-learn).

Tell your user: "I can analyze your memory for cleanup. Want me to run a curation report?"

### `palaia sync export/import` — Git-based knowledge exchange

```bash
# Export entries for sharing
palaia sync export --project myapp --output ./export/

# Export to a git remote
palaia sync export --project myapp --remote git@github.com:team/knowledge.git

# Import entries
palaia sync import ./export/ --dry-run   # Preview first
palaia sync import ./export/
```

Note: The old `palaia export`/`palaia import` aliases still work but are deprecated.

### `palaia package export/import` — Portable knowledge packages

```bash
# Export project knowledge as a portable file
palaia package export myapp --output myapp.palaia-pkg.json

# Import a knowledge package
palaia package import myapp.palaia-pkg.json --project target --merge skip

# View package metadata
palaia package info myapp.palaia-pkg.json
```

### `palaia upgrade` — Update to latest version

```bash
palaia upgrade
```

Auto-detects the install method (pip/uv/pipx/brew), preserves all installed extras (fastembed, mcp, sqlite-vec, curate), runs `palaia doctor --fix`, and upgrades the OpenClaw npm plugin if present. Always use this instead of manual pip commands.

### `palaia doctor` — Diagnostics and auto-fix

```bash
palaia doctor              # Check health
palaia doctor --fix        # Auto-fix issues
palaia doctor --json       # Machine-readable output
```

Run this first whenever something is wrong. It checks versions, repairs chains, rebuilds indexes, detects legacy systems, and handles migration.

### `palaia gc` — Garbage collection

```bash
palaia gc                  # Tier rotation (HOT -> WARM -> COLD)
palaia gc --dry-run         # Preview what would change
palaia gc --aggressive      # Also clears COLD tier
palaia gc --budget 200      # Keep max N entries
```

### `palaia config` — Configuration

```bash
palaia config list                        # Show all settings
palaia config set <key> <value>           # Set a value
palaia config set-chain fastembed bm25    # Set embedding chain
palaia config set-alias default HAL       # Agent alias
```

### `palaia process` — Multi-step process tracking

```bash
palaia process list --project myapp       # List stored processes
palaia process run <id>                   # Run interactively
```

### `palaia lock/unlock` — Entry and project locking

```bash
palaia project lock myapp --agent HAL --reason "refactoring"
palaia project lock-status myapp
palaia project unlock myapp
palaia project break-lock myapp           # Force-break stuck lock
palaia project locks                      # List all active locks
```

### `palaia edit` — Modify existing entries

```bash
palaia edit <id> --status done
palaia edit <id> "updated content" --tags new,tags --priority high
```

### Other commands

```bash
palaia detect              # Show available embedding providers
palaia warmup              # Pre-build search index
palaia recover             # Replay interrupted writes from WAL
palaia migrate <path>      # Import from other memory formats
palaia migrate --suggest   # Suggest type assignments for untyped entries
palaia ingest <file-or-url> --project X   # Index documents (RAG)
palaia skill               # Print this SKILL.md
```

All commands support `--json` for machine-readable output.

---

## Smart Nudging

Palaia's CLI output contains contextual hints prefixed with `[palaia]`. These are important guidance.

**As an agent, you should:**
- Read and act on nudge messages in CLI output
- Never suppress or ignore `[palaia]` prefixed output
- Follow recommendations (e.g., "consider running palaia curate", "related process found")
- Check for unread memos when nudged

**How nudging works:**
- Nudges are contextual: they appear when relevant (e.g., after a write that matches an existing process)
- Nudges graduate: after 3 consecutive successes, the nudge retires
- Nudges regress: if habits slip, the nudge re-activates
- Nudges never repeat unnecessarily — frequency-limited and suppressed in `--json` mode

---

## Multi-Agent Setup

### Scopes across agents
- `private` entries are only visible to the writing agent
- `team` entries are visible to all agents in the workspace
- `public` entries can be exported across workspaces

### Agent identity
Set via `--agent` flag, `PALAIA_AGENT` env var, or `palaia init --agent NAME`. Stored in `.palaia/config.json`.

**CRITICAL:** Every agent MUST have a unique `PALAIA_AGENT` value. Without it, all entries are attributed to "default" and scope filtering does not work correctly.

### Setting up additional agents

When new agents join an existing OpenClaw instance that already has palaia, each agent needs palaia awareness:

1. Set the agent's identity:
   ```bash
   export PALAIA_AGENT=<agent-name>
   ```
2. Add palaia's SKILL.md to the agent's skill set (via ClawHub or manual config)
3. Join the shared store:
   ```bash
   palaia instance set <instance-id>
   ```
4. Verify connectivity:
   ```bash
   palaia doctor
   palaia memo inbox
   ```

If a new agent is added later and does NOT have palaia configured, it will:
- Not auto-capture conversations
- Not benefit from shared team knowledge
- Potentially duplicate work that palaia already tracked

Use `palaia memo broadcast "New agent <name> is online"` to notify the team.

### Aliases
When an agent runs under different names (e.g., "default" during init, "HAL" during operation):
```bash
palaia alias set default HAL
```
Queries for either name return entries from both.

### Per-agent priorities
Different agents can have different injection behavior:
```bash
palaia priorities set recallMinScore 0.8 --agent orchestrator
palaia priorities set typeWeight.process 0.5 --agent worker
palaia priorities block <entry-id> --agent orchestrator
```

### Session instances
Distinguish sessions of the same agent:
```bash
palaia instance set Claw-Main
```

---

## When to Use What

| Situation | Command |
|-----------|---------|
| Remember a fact (not from conversation) | `palaia write "..." --type memory` |
| Record a process/SOP | `palaia write "steps..." --type process` |
| Create a task | `palaia write "fix bug" --type task --priority high` |
| Mark task done | `palaia edit <id> --status done` |
| Find something | `palaia query "..."` |
| Find open tasks | `palaia list --type task --status open` |
| Check system health | `palaia status` |
| Something is wrong | `palaia doctor --fix` |
| Clean up old entries | `palaia gc` |
| Review accumulated knowledge | `palaia curate analyze` |
| Share knowledge | `palaia sync export` or `palaia package export` |
| Check for messages | `palaia memo inbox` |
| Start of session | Session briefing is now automatic. Just run `palaia doctor` and check `palaia memo inbox`. |

**Do NOT manually write:** facts, decisions, or preferences that came up in the current conversation. Auto-Capture handles these.

**DO manually write:** processes, tasks with structured fields, knowledge from external sources, project setup.

---

## Auto-Capture and Manual Write

### How Auto-Capture works
Auto-capture runs after every agent turn (when OpenClaw plugin is active). It:
1. Collects messages from the completed exchange
2. Filters trivial content
3. Uses LLM extraction to identify significant knowledge
4. Writes entries with appropriate type, tags, scope, and project
5. Falls back to rule-based extraction if LLM is unavailable

### Capture Hints
Guide auto-capture without writing manually:
```
<palaia-hint project="myapp" scope="private" />
```
Hints override LLM detection. Multiple hints supported. Automatically stripped from output.

### Capture Levels
```bash
palaia init --capture-level <off|minimal|normal|aggressive>
```

| Level | Behavior |
|-------|----------|
| `off` | Manual-only memory |
| `minimal` | Significant exchanges, min 5 turns |
| `normal` | Significant exchanges, min 2 turns (default) |
| `aggressive` | Every exchange, min 1 turn |

---

## Session Continuity (NEW in v2.4)

Session continuity gives agents automatic context restoration across sessions. These features work out of the box with the OpenClaw plugin -- no manual setup needed.

### Session Briefings
On session start, Palaia automatically injects a briefing with the last session summary and any open tasks. This means agents resume work without needing to manually search for context.

### Session Summaries
When a session ends or resets, Palaia auto-saves a summary of what happened. These are stored as entries with the `session-summary` tag and can be queried:
```bash
palaia query "session-summary" --tags session-summary
```

### Privacy Markers
Wrap sensitive content in `<private>...</private>` blocks to exclude it from auto-capture. Private blocks are stripped before any extraction runs.

### Recency Boost
Fresh memories are ranked higher in recall results. The boost factor is configurable via `recallRecencyBoost` (default `0.3`, set to `0` to disable).

### Progressive Disclosure
When result sets exceed 100 entries, Palaia uses compact mode to keep context manageable. Use `--limit` to control result size explicitly:
```bash
palaia list --type task --status open --limit 5
```

---

## Plugin Configuration (OpenClaw)

Set in `openclaw.json` under `plugins.entries.palaia.config`:

| Key | Default | Description |
|-----|---------|-------------|
| `memoryInject` | `true` | Inject relevant memories into agent context |
| `maxInjectedChars` | `4000` | Max characters for injected context |
| `autoCapture` | `true` | Capture significant exchanges automatically |
| `captureFrequency` | `"significant"` | `"every"` or `"significant"` |
| `captureMinTurns` | `2` | Minimum turns before capture |
| `captureModel` | auto | Model for extraction (e.g. `"anthropic/claude-haiku-4-5"`) |
| `recallMode` | `"query"` | `"list"` or `"query"` |
| `recallMinScore` | `0.7` | Minimum score for recall results |
| `embeddingServer` | `true` | Keep embedding model loaded for fast queries |
| `showMemorySources` | `true` | Show memory source footnotes |
| `showCaptureConfirm` | `true` | Show capture confirmations |
| `sessionSummary` | `true` | Auto-save session summaries on end/reset |
| `sessionBriefing` | `true` | Load session context on session start |
| `sessionBriefingMaxChars` | `1500` | Max chars for session briefing injection |
| `captureToolObservations` | `true` | Track tool usage as session context |
| `recallRecencyBoost` | `0.3` | Boost factor for fresh memories (0=off) |

---

## Dangerous Operations

**Be careful with these commands:**

- **`palaia gc --aggressive`** — Permanently deletes COLD-tier entries. Always run `palaia gc --aggressive --dry-run` first and confirm with the user before executing.
- **Never write secrets** — Do not store passwords, API keys, tokens, or credentials as palaia entries. They persist in the database and may be shared via `--scope team` or `--scope public`.
- **`--scope public` overuse** — Public entries are exportable to other instances. Only use for genuinely shareable knowledge. Default to `team` scope.
- **"Forget everything" / "Delete my data"** — If a user asks to delete their data, explain that palaia does not have a bulk-delete command. Guide them to `palaia gc --aggressive` for cold entries, or manual `palaia edit <id>` / project deletion. Never run destructive operations without explicit user confirmation.

## Error Handling

**NEVER silently ignore palaia errors. Always report them clearly to the user.**

| Problem | What to do |
|---------|-----------|
| Something is wrong | `palaia doctor --fix` first, debug second |
| `palaia init` fails | Check permissions on the directory, disk space, and Python version. Report the exact error to the user. |
| `palaia write` fails | Run `palaia doctor --fix`, then retry. If WAL replay needed, run `palaia recover`. |
| `palaia query` returns nothing | Try `palaia query "..." --all` to include COLD tier. Check `palaia list` to verify entries exist. |
| Entries seem missing | `palaia recover` then `palaia list --tier cold` |
| Slow queries | `pip install 'palaia[sqlite-vec]'` for native vector search, then `palaia warmup`. Check `palaia detect` and `palaia status` |
| Provider not available | Chain auto-falls back. Check `palaia status` |
| `.palaia` missing | `palaia init` |
| Embedding provider unavailable | BM25 works without embeddings. Check `palaia detect` for available providers. |

If `palaia doctor --fix` cannot resolve an issue, report the full error output to the user. Do not guess at fixes.

---

## Configuration Keys

| Key | Default | Description |
|-----|---------|-------------|
| `default_scope` | `team` | Default visibility for new entries |
| `embedding_chain` | *(auto)* | Ordered list of search providers |
| `database_backend` | `sqlite` | Storage backend (`sqlite` or `postgres`) |
| `hot_threshold_days` | `7` | Days before HOT -> WARM |
| `warm_threshold_days` | `30` | Days before WARM -> COLD |
| `hot_max_entries` | `50` | Max entries in HOT tier |
| `decay_lambda` | `0.1` | Decay rate for memory scores |
| `embed_server_auto_start` | `true` | Auto-start embed-server daemon on first CLI query |
| `embed_server_idle_timeout` | `1800` | Daemon auto-shutdown after N seconds idle |

---

(c) 2026 byte5 GmbH -- MIT License
