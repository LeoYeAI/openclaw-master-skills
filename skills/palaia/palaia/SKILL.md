---
name: palaia
version: "2.0.8"
description: >
  Local, crash-safe persistent memory for OpenClaw agents.
  Replaces built-in memory-core with semantic search, projects, and scope-based access control.
  After installing or updating, run: palaia doctor --fix to complete setup.
metadata:
  openclaw:
    emoji: 🧠
    requires:
      bins: ["palaia"]
    install:
      - id: pip
        kind: pip
        package: "palaia[fastembed]"
        bins: ["palaia"]
        label: "Install Palaia with fastembed (pip)"
    postInstall:
      - command: "palaia init"
        label: "Initialize Palaia store"
      - command: "npm install -g @byte5ai/palaia@latest"
        label: "Install OpenClaw plugin (npm)"
    postUpdate:
      - command: "python3 -m pip install --upgrade 'palaia[fastembed]' && (npm install -g @byte5ai/palaia@latest 2>/dev/null || true) && palaia doctor --fix && palaia warmup"
        label: "Upgrade Palaia (pip + npm plugin if available) and run health checks"
    postUpdateMessage: >
      Palaia has been updated to v2.0. New features: Auto-Capture (on by default),
      Query-based Recall, optimized defaults for zero-config UX.
      Recommendation: Run `palaia doctor --fix` to upgrade your config to the new defaults.
      Custom values you've set will NOT be touched.
    plugin:
      slot: memory
      package: "@byte5ai/palaia"
---

# Palaia — Agent Memory Skill

## Auto-Check (run every time this skill is loaded)

**[INSTRUCTION for LLM]:** Before doing anything else with Palaia, run `palaia doctor` silently. If it reports ANY warnings (version mismatch, missing providers, legacy patterns, incomplete setup), address them immediately by following `palaia doctor --fix` recommendations. Do not proceed with other Palaia tasks until doctor reports no issues. This ensures the memory system is always up-to-date and correctly configured.

## Zero-Config: It Just Works

**Palaia works out of the box after installation. No config edits needed.**

After `pip install "palaia[fastembed]"` and activating the OpenClaw plugin, Palaia immediately:
- **Injects relevant memories** into every agent prompt (`memoryInject: true`)
- **Auto-captures significant exchanges** as searchable memories (`autoCapture: true`)
- **Uses semantic recall** to find context-relevant memories (`recallMode: query`)

No settings to tweak. No README to study. Install it and it works.

**For power users:** All defaults can be customized via `openclaw.json` plugin config or `palaia init --capture-level`. See the Configuration section below.

**Upgrading from v1.x?** Run `palaia doctor --fix` — it detects old defaults and upgrades them. Custom values you've set are preserved.

## Communication During Setup

- After each major step, send a brief status message to the user. Don't go silent.
- If a step takes longer than ~10 seconds, say what you're doing: "Installing sentence-transformers, this takes a moment…"
- If something unexpected happens (e.g. CUDA error, provider fails), explain what happened and what you're doing instead — immediately.
- Don't batch all steps and report at the end. Report after each step.

Example pacing:
1. "Installing Palaia…" → [runs pip install] → "Done. Initializing store…" → [runs palaia init] → "Store ready."
2. "Installing OpenClaw plugin…" → [runs npm install -g @byte5ai/palaia@latest] → "Plugin installed. Activating…" → [patches config, restarts gateway] → "Plugin active."
3. "Running diagnostics…" → [runs palaia doctor] → "Found: [X]. Quick question:"
4. [Onboarding conversation — max 3 questions]
5. "Configuring chain… warming up model (this takes ~15 seconds)…" → "Ready."
6. "All set. Here's your setup: [one sentence summary]"

## Setup Flow (follow this exactly)

### Step 1: Install and initialize

**Choose your package manager** (use whichever is available on your system):
```bash
# pip (most common)
python3 -m pip install "palaia[fastembed]"

# uv (if pip is not available)
uv tool install "palaia[fastembed]"

# pipx (alternative)
pipx install "palaia[fastembed]"
```

> **Important (uv users):** Always include the `[fastembed]` extra. `uv tool install palaia` without extras will remove previously installed embedding providers (fastembed, sentence-transformers) on upgrade. This is by design — `uv` strictly manages dependencies. Always use `uv tool install "palaia[fastembed]"` for both install and upgrade.

```bash
palaia init
```

**Agent identity is optional but recommended.** `palaia init` without `--agent` sets the agent name to "default". This works fine for single-agent systems. For multi-agent setups, use `--agent`:
```bash
palaia init --agent YOUR_AGENT_NAME
```

If an OpenClaw config with a single agent is detected, the name is auto-detected:
```
Auto-detected agent: HAL (from OpenClaw config)
```

The agent name is stored in `.palaia/config.json` and automatically attached to all writes and memo operations. No env vars needed.

**Single-Agent to Multi-Agent Migration:**
When adding a second agent later, existing entries keep their original agent name ("default"). To associate old "default" entries with your named agent:
```bash
palaia config set-alias default YOUR_NAME
```
This makes queries for YOUR_NAME also return entries written as "default". No entries are rewritten — aliases are query-time only. `palaia doctor` will remind you if this is needed.

**Optional: Set session instance** (for multi-instance agents):
```bash
palaia instance set YOUR_INSTANCE_NAME
```
Instance is session-local and adds traceability to entries. Memos can target specific instances.

### Step 2: Install and activate OpenClaw plugin (REQUIRED)

The npm plugin wires Palaia into OpenClaw's memory slot — without it, Auto-Capture and Auto-Recall don't work.

```bash
npm install -g @byte5ai/palaia@latest
```

Now activate the plugin in OpenClaw.

**[INSTRUCTION for LLM]:** Do NOT blindly overwrite plugin config arrays with `openclaw config set`.
Arrays like `plugins.allow` and `plugins.load.paths` may already contain other plugins (telegram, slack, clawsy-bridge...).
Overwriting them destroys the existing configuration. Always read first, then append if missing.

**Preferred: Use gateway config.patch (deep-merges, safest)**

If you have access to the gateway tool, use `config.patch` — it deep-merges instead of overwriting:

```
# First, read existing values to avoid duplicates
PALAIA_PATH="$(npm root -g)/@byte5ai/palaia"
existingAllow = gateway(action="config.get", key="plugins.allow")  // e.g. ["telegram","slack"]
existingPaths = gateway(action="config.get", key="plugins.load.paths")  // e.g. ["/path/to/telegram"]

# Then patch (only add palaia if not already present)
gateway(action="config.patch", raw=JSON.stringify({
  plugins: {
    load: { paths: [...existingPaths, palaiaPath] },
    allow: [...existingAllow, "palaia"],
    slots: { memory: "palaia" },
    entries: { palaia: { enabled: true } }
  }
}), note="Palaia plugin activated")
```

**Alternative: Safe shell approach (reads existing config, adds palaia, never overwrites)**

```bash
PALAIA_PATH="$(npm root -g)/@byte5ai/palaia"

# Add to plugins.allow (only if not already present)
CURRENT_ALLOW=$(openclaw config get plugins.allow 2>/dev/null || echo '[]')
if ! echo "$CURRENT_ALLOW" | grep -q '"palaia"'; then
  NEW_ALLOW=$(echo "$CURRENT_ALLOW" | python3 -c "import sys,json; a=json.load(sys.stdin); a.append('palaia'); print(json.dumps(a))")
  openclaw config set plugins.allow "$NEW_ALLOW"
fi

# Add to plugins.load.paths (only if not already present)
CURRENT_PATHS=$(openclaw config get plugins.load.paths 2>/dev/null || echo '[]')
if ! echo "$CURRENT_PATHS" | grep -q "$PALAIA_PATH"; then
  NEW_PATHS=$(echo "$CURRENT_PATHS" | python3 -c "import sys,json,os; a=json.load(sys.stdin); a.append(os.environ['PALAIA_PATH']); print(json.dumps(a))")
  openclaw config set plugins.load.paths "$NEW_PATHS"
fi

# Set memory slot (safe — single value, not array)
openclaw config set plugins.slots.memory palaia
```

> **Typical `npm root -g` paths:**
> - Linux (Homebrew): `/home/linuxbrew/.linuxbrew/lib/node_modules`
> - macOS (Homebrew): `/opt/homebrew/lib/node_modules`
> - macOS (nvm): `~/.nvm/versions/node/vXX/lib/node_modules`
> - Linux (system): `/usr/lib/node_modules`
> - Windows: `%AppData%\npm\node_modules`

Restart the gateway so the plugin loads:
```bash
openclaw gateway restart
```

Wait for the gateway to come back up, then verify:
```bash
palaia doctor
```
The output must include `OpenClaw plugin: palaia is active`. If it does not, re-check the path and config values above.

### Step 3: Check for existing memory systems (REQUIRED — do not skip)
```bash
palaia doctor
```

Review **every** warning before continuing. For each warning found by `palaia doctor`, immediately offer to fix it — do not wait for the user to ask:

**HEARTBEAT.md legacy patterns:**
→ Tell the user: "Your heartbeat still uses old memory patterns. Should I update it to use Palaia? (Takes a moment, no data loss)"
- If yes: update HEARTBEAT.md, replace `memory_search`/`memory_get`/direct file reads with `palaia query`/`palaia write` equivalents
- If no: skip, move to next warning

**Smart-Memory skill detected:**
→ Tell the user: "The old smart-memory skill is still installed. Should I remove it? (Only after confirming Palaia has your memories)"
- If yes: run `palaia migrate <workspace-path>`, then remove the smart-memory skill folder
- If no: continue, but both systems will run in parallel (not recommended)

**OpenClaw plugin still memory-core:**
→ Tell the user: "Palaia isn't connected to OpenClaw's memory system yet. Should I switch it? (Requires a quick OpenClaw restart)"
- If yes: update OpenClaw config (`plugins.slots.memory = "palaia"`), restart OpenClaw
- If no: Palaia runs standalone (no `memory_search`/`memory_get` tool integration)

**openai-only chain (no local fallback):**
→ Tell the user: "Your search has no local backup. Should I install fastembed as a fallback? (Small download, no GPU needed)"
- If yes: `pip install fastembed`, then `palaia warmup`, update chain to include fastembed before bm25
- If no: skip (warn: "Search may degrade when OpenAI is unavailable")

Rules:
- For each warning: ask immediately, one question at a time
- Do not batch all questions — address them in order
- Do not wait for the user to notice and ask
- After user answers yes/no, move to next warning
- Report when all warnings are resolved

**Do not proceed until all warnings are addressed or explicitly dismissed by the user.**

### Onboarding Conversation

After running `palaia doctor` and reviewing warnings, have a brief conversation with your user.
Keep it short — 3 questions max. No technical details unless the user asks.

**Script:**

Tell the user:
"I've set up Palaia for you — your memory is now crash-safe and searchable.
Quick setup: 3 short questions."

**Question 1 — Search quality:**

If an OpenAI API key is present AND a local model (sentence-transformers/fastembed/ollama) is also detected:
  → Just confirm: "I'll use your OpenAI key with a local backup model. Good setup."
  → No question needed.

If an OpenAI API key is present BUT no local model is installed:
  → Tell the user: "You have an OpenAI API key — great for search quality. But without a local backup, search quality drops significantly when OpenAI is unavailable. I recommend installing a small local model (300MB, free, runs offline). Should I do that?"
  → yes: pip install sentence-transformers (if CUDA issues: pip install fastembed instead — lighter, no GPU needed), then palaia warmup, chain = openai → sentence-transformers → bm25
  → no: chain = openai → bm25 (warn: "Note: search may fail or degrade without a local fallback.")

If no OpenAI key AND no local model:
  → Tell the user: "No search provider found yet. I recommend installing a free local model (300MB). Should I do that?"
  → yes: pip install sentence-transformers (if CUDA issues: pip install fastembed instead — lighter, no GPU needed), then palaia warmup, chain = sentence-transformers → bm25
  → no: BM25 only (warn: "Search will be keyword-based — you can improve this later with palaia detect.")

If no OpenAI key BUT local model detected:
  → Just confirm: "Using local search model — works offline, no API costs."
  → No question needed.

**Question 2 — Existing memory (only ask if legacy memory files exist OR smart-memory detected):**
  Ask: "You have existing memory. Should I bring it into Palaia?"
  → yes: run palaia migrate <workspace-path>
  → no: start fresh (existing files stay untouched)

**Question 3 — Projects (only ask if multiple project folders detected OR more than 1 agent present):**
  Ask: "Do you work on multiple projects? I can keep their memories separate."
  → yes: briefly explain: "Use 'palaia project create <name>' for each project. I'll remember which memories belong where."
  → no: skip

**Question 4 — Capture Model (only ask if autoCapture is enabled, which is the default):**
  Ask: "Auto-Capture saves significant conversations automatically. Which model should it use for extraction? A cheap/fast model is best (e.g. claude-haiku-4-5, gpt-4.1-mini, gemini-2.0-flash)."
  → User names a model: set `captureModel` in openclaw.json plugin config
  → User says "use default" or skips: leave unset (primary model will be used, doctor will nudge)

**Wrap up:**
Tell the user what was configured — one sentence:
"Done. [Search quality: OpenAI / local model / keyword-only]. [Migration: X entries imported / fresh start]. [Projects: configured / not used]."

Do not explain commands, WAL, BM25, embedding models, or any technical details unless the user explicitly asks.

### Step 4: Migrate existing entries (best practice — do this now)
If there are existing entries from an earlier Palaia version (or from initial setup), run:
```bash
palaia migrate --suggest
```
This checks for entries without type classification and suggests improvements. Better to do this early while the store is small — it gets harder as the store grows. Apply the suggestions that make sense.

### Step 5a: Check embedding setup (auto-configured by init)
```bash
palaia detect
```
Review the detected providers and configured chain. `palaia init` automatically detects available providers
and configures the best embedding chain — you usually don't need to change anything.

If the chain looks wrong or you want to change it:
```bash
palaia config set-chain <provider1> [provider2] bm25
```

If only BM25 is shown and you want semantic search:
```bash
# fastembed — lightweight, no GPU needed, recommended for most systems
python3 -m pip install fastembed    # or: uv pip install fastembed
palaia warmup                       # pre-load model + build index
```
If fastembed is unavailable, sentence-transformers works too (`python3 -m pip install sentence-transformers`) but is heavier and slower on CPU-only systems.

### Step 5b: Warm up models
```bash
palaia warmup
```
This pre-downloads embedding models so the first search is instant. Always run after chain setup.

### Step 6: Verify setup (mandatory — do not skip)
Run a test query to verify semantic search works end-to-end:
```bash
palaia query "important context and decisions"
```
**Check:**
- Results must appear (not empty)
- Response time should be under 5 seconds
- If it times out or returns no results: check `palaia status` and `palaia detect`, fix any issues before proceeding

Then verify `palaia status` shows indexed entries (Index: N/N, not 0/N).
If index is 0/N after warmup, run a few queries — indexing happens lazily on first query.

**Do not tell the user "setup complete" until this verification passes.** Assumption is not verification.

### Step 7: Optional — migrate additional memory files (skip if done in Step 4)
```bash
palaia migrate <path> --dry-run   # Preview first
palaia migrate <path>             # Then import
```
Note: If smart-memory migration was already handled in Step 3, skip this unless there are other sources to import.

### Step 8: Add Palaia maintenance to your heartbeat (mandatory)

This is required. Palaia's tiering (HOT → WARM → COLD) only runs when triggered.
Without periodic maintenance, all entries stay HOT forever and search quality degrades over time.

Check if `HEARTBEAT.md` exists in the workspace (`~/.openclaw/workspace/HEARTBEAT.md`).

**If it exists:** Append the following block at the end (before any final comments):

```
# TASK: Palaia Maintenance (daily + weekly)
# [INSTRUCTION for LLM]:
# Daily: run `palaia gc` — moves entries between HOT/WARM/COLD based on age and access.
# Weekly (Sunday): run `palaia gc --aggressive` — also clears COLD tier.
# Fast operation, never blocks user queries. Only run if palaia is installed (check: which palaia).
```

**If it does not exist:** Create `HEARTBEAT.md` with the block above as its first task.

Tell the user: "I've added a Palaia maintenance task to your heartbeat schedule. This keeps your memory organized automatically — nothing you need to do."

## Troubleshooting: pip Not Found

On some hosts, `pip` is not available as a standalone command. Use these fallbacks in order:

```bash
# Option 1: python3 -m pip (most reliable)
python3 -m pip install --upgrade "palaia[fastembed]"

# Option 2: uv (modern Python package manager)
uv tool install "palaia[fastembed]"

# Option 3: pipx (if installed)
pipx install "palaia[fastembed]"

# Option 4: Bootstrap pip first
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade "palaia[fastembed]"

# Option 5: Install from git directly
python3 -m pip install "palaia[fastembed] @ git+https://github.com/iret77/palaia.git"
```

> **uv users:** When upgrading with `uv tool install`, always include `[fastembed]` — `uv` removes packages not in the dependency spec on upgrade. Running `uv tool install palaia` without extras will silently uninstall fastembed.

## Troubleshooting: Debian/Ubuntu (PEP 668)

On Debian-based systems (Debian 12+, Ubuntu 23.04+), pip may fail with "externally-managed-environment".
This is due to PEP 668 which prevents pip from modifying system Python packages.

Use one of these approaches:

```bash
# Option 1: User install (recommended)
python3 -m pip install --user "palaia[fastembed]"

# Option 2: Break system packages (use if you know what you're doing)
python3 -m pip install --break-system-packages "palaia[fastembed]"

# Option 3: pipx (cleanest isolation)
pipx install "palaia[fastembed]"

# Option 4: Virtual environment
python3 -m venv ~/.palaia-venv
~/.palaia-venv/bin/pip install "palaia[fastembed]"
alias palaia=~/.palaia-venv/bin/palaia
```

After upgrading, always run `palaia doctor --fix` to verify providers and update the store.

**Important:** If you had sentence-transformers or fastembed installed before upgrading,
verify they are still available after the upgrade:
```bash
palaia detect
```
If a provider is missing, reinstall it:
```bash
python3 -m pip install "palaia[sentence-transformers]"
palaia warmup
```

## Plugin Activation (OpenClaw Memory Backend)

After installing palaia, activate it as your memory backend:

### 1. Install the OpenClaw plugin
```bash
npm install -g @byte5ai/palaia
```

### 2. Configure OpenClaw

**Config path:** `plugins.entries.palaia.config` in your OpenClaw config (`openclaw.json`).

> **Warning:** Do NOT use `plugins.config.palaia` — that path does not exist.
> The correct structure is `plugins.entries.palaia.config`.

Patch your OpenClaw config (`openclaw.json`) to load and activate the plugin:

```json
{
  "plugins": {
    "load": {
      "paths": ["<path-to-npm-global>/node_modules/@byte5ai/palaia"]
    },
    "allow": ["..existing..", "palaia"],
    "slots": {
      "memory": "palaia"
    },
    "entries": {
      "palaia": {
        "enabled": true,
        "config": {
          "workspace": "/path/to/.openclaw/workspace"
        }
      }
    }
  }
}
```

Find your npm global path with: `npm root -g`

**Plugin config keys** (under `plugins.entries.palaia.config`):

| Key | Description |
|-----|-------------|
| `workspace` | Path to the OpenClaw workspace (where `.palaia/` lives) |
| `memoryInject` | Inject memories into agent context (default: `true`) |
| `maxInjectedChars` | Max characters for injected context (default: `4000`) |
| `recallMinScore` | Minimum score for relevant recall results (default: `0.7`) |
| `autoCapture` | Capture significant exchanges automatically (default: `true`) |
| `captureFrequency` | `"every"` or `"significant"` (default: `"significant"`) |
| `captureMinTurns` | Minimum exchange turns before capture (default: 2) |
| `captureModel` | Explicit model for LLM extraction (e.g. `"anthropic/claude-haiku-4-5"`). Recommended: set a cheap/fast model. If unset, uses your primary model. |
| `showMemorySources` | Show memory source footnotes in responses (default: `true`) |
| `showCaptureConfirm` | Show capture confirmations in responses (default: `true`) |
| `recallMode` | `"list"` or `"query"` — how memories are retrieved (default: `"query"`) |

> **Note (Issue #66):** Plugin config is currently **global** — all agents on the same OpenClaw
> instance share the same config from `openclaw.json`. Per-agent config resolution would require
> an OpenClaw upstream change where the plugin API provides agent-scoped config.
> Individual agent behavior (e.g. different capture levels) can be configured via
> `palaia init --capture-level` which writes to `.palaia/config.json` locally.

### Capture Level (Issue #67)

Configure how aggressively Palaia auto-captures agent exchanges:

```bash
palaia init --capture-level <off|sparsam|normal|aggressiv>
```

| Level | autoCapture | Frequency | Min Turns | Use Case |
|-------|-------------|-----------|-----------|----------|
| `off` | false | — | — | Manual-only memory |
| `sparsam` | true | significant | 5 | Low noise, long sessions |
| `normal` | true | significant | 2 | Recommended default |
| `aggressiv` | true | every | 1 | Maximize capture |

The setting is stored in `.palaia/config.json` under `plugin_config`.
`palaia doctor` checks if a capture level is configured and suggests setting one in OpenClaw environments.

### 3. Restart OpenClaw Gateway
The config change requires a gateway restart to take effect.

### What changes
- `memory_search` and `memory_get` tools now search the Palaia store instead of MEMORY.md files
- MEMORY.md and workspace files continue to be loaded as project context (unchanged)
- All Palaia features (projects, scopes, tiering, semantic search) are available through the standard memory tools

## Auto-Capture and Capture Hints

### How Auto-Capture Works

Auto-capture runs automatically after every agent turn (when `autoCapture: true`, which is the default). It:

1. Collects all messages from the completed exchange
2. Filters out trivial exchanges (short, system content, acknowledgments)
3. Uses LLM-based extraction to identify significant knowledge: decisions, lessons, processes, commitments, preferences
4. Writes extracted items to Palaia with appropriate type, tags, scope, and project attribution
5. Falls back to rule-based extraction if LLM is unavailable

**Agent attribution:** If `PALAIA_AGENT` is set in the environment, all auto-captured entries are attributed to that agent via `--agent`. Otherwise, the CLI uses the configured default.

**Project detection:** Auto-capture passes the list of known projects to the LLM, which assigns entries to the most relevant project (or none if unclear).

**Scope detection:** The LLM also determines scope per item: `private` (personal preference), `team` (shared knowledge), or `public` (documentation).

### When to Use Manual Write vs Auto-Capture

**Auto-Capture** handles conversation knowledge automatically: decisions mentioned in chat, facts discussed, lessons learned during work. You don't need to save these — Palaia does it for you.

**Manual `palaia write` is for structured knowledge that Auto-Capture cannot create:**

| Use Case | Command | Why Manual? |
|----------|---------|-------------|
| Step-by-step procedure | `palaia write "1. Build 2. Test 3. Deploy" --type process` | Structure matters |
| Task with owner/deadline | `palaia write "fix auth" --type task --priority high --assignee Elliot` | Structured fields |
| Project setup | `palaia project create myproject` | Explicit organization |
| Knowledge from external source | `palaia write "API limit: 100/min" --type memory --project api` | Not from conversation |

**Do NOT manually write:**
- Facts, decisions, or preferences that came up in the current conversation (auto-captured)
- "We decided to use X" after discussing X (auto-captured)
- Status updates or progress notes (auto-captured if significant)

**Rule of thumb:** If it just happened in conversation → trust Auto-Capture. If it needs structure (steps, fields, project assignment) → write manually.

### Capture Hints

When you want to guide auto-capture without writing manually, use `<palaia-hint />` tags in your message:

```
<palaia-hint project="myapp" scope="private" />
```

Hints are parsed from all messages in the exchange and used as overrides:
- **Priority:** Hint > LLM detection > Config override > Default
- **Attributes:** `project`, `scope`, `type`, `tags` (comma-separated)
- **Stripping:** Hints are automatically removed from outgoing messages — the user never sees them

Multiple hints are supported (e.g., for different projects in the same turn):
```
<palaia-hint project="frontend" scope="team" tags="decision" />
<palaia-hint project="backend" type="process" />
```

### Static Config Overrides

For setups where every entry should go to the same project/scope, set in plugin config:
- `captureScope`: Static scope override (e.g., `"team"`)
- `captureProject`: Static project override (e.g., `"myapp"`)

These override LLM detection but are overridden by capture hints.

## Knowledge Packages

Export and import project knowledge as portable package files.

```bash
# Export all entries from a project
palaia package export <project> [--output file.palaia-pkg.json] [--types memory,process]

# Import a knowledge package
palaia package import <file> [--project target] [--merge skip|overwrite|append] [--agent name]

# View package metadata without importing
palaia package info <file>
```

The `--agent` flag on import attributes all imported entries to a specific agent name.

## Process Runner

Run stored process entries as interactive checklists:

```bash
# List all stored processes
palaia process list [--project NAME]

# Run a process interactively
palaia process run <id>
```

## Temporal Queries

Filter entries by time with `--before` and `--after`:

```bash
palaia query "deploy" --after 2026-03-01 --before 2026-03-15
palaia list --after 2026-03-01
```

Dates are in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).

## Cross-Project Search

Search across all projects at once:

```bash
palaia query "authentication" --cross-project
```

Without `--cross-project`, queries only search entries in the active project context.

## Bounded Memory and Garbage Collection

Palaia supports budgeted garbage collection to keep the store lean:

```bash
# Preview what would be collected
palaia gc --dry-run

# Collect with a target budget (max entries to keep)
palaia gc --budget 200

# Aggressive collection — also clears COLD tier
palaia gc --aggressive
```

GC rotates entries through tiers: HOT (active, <7 days) -> WARM (recent, <30 days) -> COLD (archived).

## Significance Tagging

Auto-capture automatically detects and tags entries with significance markers:

| Tag | Meaning | Example |
|-----|---------|---------|
| `decision` | A choice was made | "We decided to use PostgreSQL" |
| `lesson` | Something was learned | "I learned that caching needs invalidation on deploy" |
| `surprise` | Unexpected discovery | "The API returns 200 even on errors" |
| `commitment` | Promise or action item | "I will refactor auth by Friday" |
| `correction` | Error was corrected | "Actually, the limit is 100, not 50" |
| `preference` | User/agent preference | "I prefer tabs over spaces" |
| `fact` | Important factual information | "The prod DB is on port 5433" |

These tags enable targeted queries: `palaia query "decisions" --tags decision`

## Adaptive Nudging

Palaia includes a graduation system that adapts to agent behavior:

**What it does:** When the agent writes an entry that relates to an existing process, Palaia nudges: "Related process found: [title]. Consider following it."

**How it learns:** The nudging system tracks whether agents follow stored processes. Over time:
- Agents that consistently follow processes see fewer nudges (graduated)
- Agents that frequently skip processes continue to receive nudges
- New processes always trigger nudges until a pattern is established

**Important:** SKILL.md documentation is the primary source for agent behavior. Nudging is the safety net for when agents don't read the docs — not a replacement for good documentation.

## Transparency Features

Palaia makes its memory operations visible to the user by default. Both features are enabled out of the box and can be toggled independently.

### Memory Source Footnotes

When Palaia injects memories into the agent context and the agent uses them in a response, a footnote is appended:

```
📎 Palaia: "PostgreSQL migration plan" (Mar 16), "Deploy process" (Mar 10)
```

This shows the user which memories influenced the response. Max 3 sources are shown, selected by keyword relevance between the memory title and the response text.

**Disable:** `palaia config set showMemorySources false`
**Re-enable:** `palaia config set showMemorySources true`

### Capture Confirmations

When Palaia auto-captures a significant exchange, a confirmation is shown:

```
💾 Saved: "Team decided to use PostgreSQL for the project due to JSON support"
```

This confirms that knowledge was stored and gives the user a preview of what was captured.

**Disable:** `palaia config set showCaptureConfirm false`
**Re-enable:** `palaia config set showCaptureConfirm true`

### Satisfaction and Preference Nudges

After sustained usage, Palaia nudges agents to check in with the user:

1. **Satisfaction check** (after ~10 successful recalls): Ask the user if the memory system is working well. Suggest `palaia doctor` if there are issues.
2. **Transparency preference** (after ~50 recalls or ~7 days): Ask the user whether they want to keep seeing footnotes and capture confirmations, or hide them. Both are one-shot nudges that won't repeat.

## Commands Reference

### Basic Memory

```bash
# Write a memory entry (default type: memory)
palaia write "text" [--scope private|team|public] [--project NAME] [--tags a,b] [--title "Title"] [--type memory|process|task] [--instance NAME]

# Write a task with structured fields
palaia write "fix login bug" --type task --status open --priority high --assignee Elliot --due-date 2026-04-01

# Edit an existing entry (content, metadata, task fields)
palaia edit <id> ["new content"] [--status done] [--priority high] [--tags new,tags] [--title "New Title"] [--type task]

# Search memories (semantic + keyword) with structured filters
palaia query "search term" [--project NAME] [--limit N] [--all] [--type task] [--status open] [--priority high] [--assignee NAME] [--instance NAME]

# Read a specific entry by ID
palaia get <id> [--from LINE] [--lines N]

# List entries in a tier with filters
palaia list [--tier hot|warm|cold] [--project NAME] [--type task] [--status open] [--priority high] [--assignee NAME] [--instance NAME]

# System health, active providers, and entry class breakdown
palaia status

# Suggest type assignments for untyped entries
palaia migrate --suggest
```

### Projects

Projects group related entries. They're optional — everything works without them.

```bash
# Create a project
palaia project create <name> [--description "..."] [--default-scope team]

# List all projects
palaia project list

# Show project details + entries
palaia project show <name>

# Write an entry directly to a project
palaia project write <name> "text" [--scope X] [--tags a,b] [--title "Title"]

# Search within a project only
palaia project query <name> "search term" [--limit N]

# Change the project's default scope
palaia project set-scope <name> <scope>

# Delete a project (entries are preserved, just untagged)
palaia project delete <name>
```

### Agent Alias System

Aliases let multiple agent names resolve to the same identity. Scope checks and queries will match both the alias and the canonical name.

```bash
# Set alias: "default" is treated as "HAL"
palaia alias set default HAL

# List all aliases
palaia alias list

# Remove an alias
palaia alias remove default
```

Use aliases when the same agent runs under different names (e.g., "default" during init, "HAL" during operation). Entries written by either name are accessible to both.

### Project Locking

Advisory locks coordinate multi-agent work on projects. Locks auto-expire after TTL (default: 30 min).

```bash
# Lock a project for exclusive work
palaia project lock <name> --agent <agent> [--reason "..."] [--ttl 3600]

# Check if a project is locked
palaia project lock-status <name>

# Release a lock
palaia project unlock <name>

# Force-break a stuck lock (use with caution)
palaia project break-lock <name>

# List all active locks
palaia project locks
```

Always check lock status before starting work on a shared project. The lock is advisory — it doesn't prevent writes, but agents should respect it.

### Configuration

```bash
# Show all settings
palaia config list

# Get/set a single value
palaia config set <key> <value>

# Set the embedding fallback chain (ordered by priority)
palaia config set-chain <provider1> [provider2] [...] bm25

# Detect available embedding providers on this system
palaia detect

# Pre-download embedding models
palaia warmup
```

### Diagnostics

```bash
# Check Palaia health and detect legacy systems
palaia doctor

# Show guided fix instructions for each warning
palaia doctor --fix

# Machine-readable output
palaia doctor --json
```

### Maintenance

```bash
# Tier rotation — moves old entries from HOT → WARM → COLD
palaia gc [--aggressive]

# Replay any interrupted writes from the write-ahead log
palaia recover
```

### Document Ingestion (RAG)

```bash
# Index a file, URL, or directory into the knowledge base
palaia ingest <file-or-url> [--project X] [--scope X] [--tags a,b] [--chunk-size N] [--dry-run]

# Query with RAG-formatted context (ready for LLM injection)
palaia query "question" --project X --rag
```

### Sync

```bash
# Export entries for sharing
palaia export [--project NAME] [--output DIR] [--remote GIT_URL]

# Import entries from an export
palaia import <path> [--dry-run]

# Import from other memory formats (smart-memory, flat-file, json-memory, generic-md)
palaia migrate <path> [--dry-run] [--format FORMAT] [--scope SCOPE]
```

### JSON Output

All commands support `--json` for machine-readable output:
```bash
palaia status --json
palaia query "search" --json
palaia project list --json
```

## Scope System

Every entry has a visibility scope:

- **`private`** — Only the agent that wrote it can read it
- **`team`** — All agents in the same workspace can read it (default)
- **`public`** — Can be exported and shared across workspaces

**Setting defaults:**
```bash
# Global default
palaia config set default_scope <scope>

# Per-project default
palaia project set-scope <name> <scope>
```

**Scope cascade** (how Palaia decides the scope for a new entry):
1. Explicit `--scope` flag → always wins
2. Project default scope → if entry belongs to a project
3. Global `default_scope` from config
4. Falls back to `team`

## Projects

- Projects are optional and purely additive — Palaia works fine without them
- Each project has its own default scope
- Writing with `--project NAME` or `palaia project write NAME` both assign to a project
- Deleting a project preserves its entries (they just lose the project tag)
- `palaia project show NAME` lists all entries with their tier and scope

## When to Use What

| Situation | Command |
|-----------|---------|
| Remember a simple fact | `palaia write "..."` |
| Remember something for a specific project | `palaia project write <name> "..."` |
| Create a task/todo | `palaia write "fix bug" --type task --priority high` |
| Record a process/SOP | `palaia write "deploy steps" --type process` |
| Mark task as done | `palaia edit <id> --status done` |
| Find something you stored | `palaia query "..."` |
| Find open tasks | `palaia query "tasks" --type task --status open` |
| List high-priority tasks | `palaia list --type task --priority high` |
| Find something within a project | `palaia project query <name> "..."` |
| Check what's in active memory | `palaia list` |
| Check what's in archived memory | `palaia list --tier cold` |
| See system health + class breakdown | `palaia status` |
| Clean up old entries | `palaia gc` |
| Index a document or website | `palaia ingest <file/url> --project <name>` |
| Get type suggestions for old entries | `palaia migrate --suggest` |
| Search indexed documents for LLM context | `palaia query "..." --project <name> --rag` |

## Document Knowledge Base

Use `palaia ingest` to index external documents — PDFs, websites, text files, directories.
Indexed content is chunked, embedded, and stored as regular entries (searchable like memory).

**When to use:**
- User asks you to "remember" a document, manual, or website
- You need to search through a large document
- Building a project-specific knowledge base

**How to use:**
```bash
palaia ingest document.pdf --project my-project
palaia ingest https://docs.example.com --project api-docs --scope team
palaia ingest ./docs/ --project my-project --tags documentation

palaia query "How does X work?" --project my-project --rag
```

The `--rag` flag returns a formatted context block ready to insert into your LLM prompt.

**PDF support:** requires pdfplumber — install with: `pip install pdfplumber`

**Source attribution:** each chunk tracks its origin (file, page, URL) automatically.

## Error Handling

| Problem | What to do |
|---------|-----------|
| Embedding provider not available | Chain automatically falls back to next provider. Check `palaia status` to see which is active. |
| Write-ahead log corrupted | Run `palaia recover` — replays any interrupted writes. |
| Entries seem missing | Run `palaia recover`, then `palaia list`. Check all tiers (`--tier warm`, `--tier cold`). |
| Search returns no results | Try `palaia query "..." --all` to include COLD tier. Check `palaia status` to confirm provider is active. |
| `.palaia` directory missing | Run `palaia init` to create a fresh store. |

## Tiering

Palaia organizes entries into three tiers based on access frequency:

- **HOT** (default: 7 days) — Frequently accessed, always searched
- **WARM** (default: 30 days) — Less active, still searched by default
- **COLD** — Archived, only searched with `--all` flag

Run `palaia gc` periodically (or let cron handle it) to rotate entries between tiers. `palaia gc --aggressive` forces more entries to lower tiers.

## What Goes Where (Single Source of Truth)

This is the most important section for avoiding duplicated knowledge. Get this right.

**Project files (CONTEXT.md, MEMORY.md, etc.) = static facts:**
- Repo URL, tech stack, architecture overview, current version
- Palaia usage info for this project: project name, common tags, scopes, conventions
- Pointers to Palaia: "Processes: `palaia query --type process --project <name>`"
- Changes rarely. Never store processes, checklists, or decision logs here.

**Palaia = all dynamic knowledge:**
- Processes and checklists (type: process) — reusable, searchable, scope-aware
- Decisions and ADRs (type: memory, tag: adr)
- Learnings and insights (type: memory, tag: learning)
- Tasks and planning (type: task)
- Anything that evolves, gets shared, or should surface at the right time

**External issue trackers (GitHub Issues, Jira, etc.) = bugs and tickets:**
- If a project uses one: bugs, feature requests, and technical tickets live there
- Never duplicate between external trackers and Palaia tasks

**The test:** "Is this a static fact about the project?" → project file. "Is this knowledge that evolves, gets shared, or should be actively surfaced?" → Palaia. "Is this a bug or feature request?" → external tracker.

**Best practice: persist concrete work state, not just project names.**
When saving active context, write the exact step, blocker, and next action — not just "working on Project X". Bad: `palaia write "Working on the API"`. Good: `palaia write "API auth module: implementing JWT refresh tokens, blocked on token expiry race condition, next step: add mutex around refresh logic" --project myapp --tag active-work`. This ensures continuity across sessions and context switches — the next session knows exactly where to pick up.

**Common mistakes to avoid:**
- Writing a release checklist into CONTEXT.md instead of `palaia write --type process`
- Keeping decision logs in markdown files instead of Palaia entries
- Duplicating task lists between files and Palaia
- Persisting vague status ("working on X") instead of concrete state (step, blocker, next action)

## Reconciling with Existing Memory Patterns

When your user installs Palaia, they're telling you: "I want better memory management." That's the benchmark. Your job is to make Palaia deliver on that promise — without breaking what already works.

**If your workspace has existing CONTEXT.md, MEMORY.md, or AGENTS.md files with memory rules that predate Palaia:**

1. **Don't fight them.** These files are authoritative workspace config. You can't and shouldn't override them.
2. **Do identify overlaps.** Read through the existing memory rules and find where they conflict with effective Palaia usage. Common patterns:
   - "Write all project knowledge to CONTEXT.md" → Processes, decisions, and learnings are better in Palaia (searchable, scope-aware, nudge-capable)
   - "Keep checklists in MEMORY.md" → These should be Palaia process entries
   - "Update CONTEXT.md after every task" → Static facts yes, dynamic knowledge should go to Palaia
3. **Propose changes to your user.** Explain what you found, why Palaia would serve them better for dynamic knowledge, and suggest specific edits to their workspace files. Don't make the changes silently.
4. **Migrate gradually.** Move one category at a time (e.g., processes first, then decisions). After each migration, add a pointer in the old location: "Processes now live in Palaia: `palaia query --type process`"
5. **Keep what works.** CONTEXT.md is great for static project steckbriefs. MEMORY.md is great for session-start headlines. These files complement Palaia — they don't compete with it. The goal is clear boundaries, not replacing everything.

**What good coexistence looks like:**
- CONTEXT.md: project URL, tech stack, current version, Palaia project name + common tags
- MEMORY.md: routing rules, agent identities, quick-reference pointers
- Palaia: processes, decisions, learnings, tasks, anything searchable or shareable

**The user chose Palaia.** Honor that choice by making it the primary home for dynamic knowledge. But be pragmatic — a working hybrid is better than a dogmatic migration that breaks the agent's workflow.

## Migration Best Practice

When upgrading to Palaia 1.7+, migrate existing planning data into structured Palaia entries:

**What to migrate:**
- Roadmap items, TODOs, pending tasks from CONTEXT.md or MEMORY.md → `palaia write --type task --status open --priority <level>`
- Checklists, SOPs, release processes → `palaia write --type process`
- Existing Palaia entries without type → run `palaia migrate --suggest` for recommendations

**After migration:**
- Remove migrated items from CONTEXT.md, MEMORY.md, or wherever they lived before
- Replace with a pointer: "Tasks live in Palaia: `palaia list --type task --project <name>`"
- This prevents double sources of truth

**Session Identity:**
- Run `palaia instance set YOUR_INSTANCE_NAME` at session start (e.g., "Claw-Main", "Claw-Palaia")
- This distinguishes entries from different sessions of the same agent
- Use `--instance` flag on queries to filter by session origin
- Alternatively, set `PALAIA_INSTANCE` env var (config file takes precedence)

**Memo Awareness:**
- After `palaia query` and `palaia write`, Palaia automatically checks for unread memos
- If unread memos exist: "You have N unread memos. Run: palaia memo inbox"
- This nudge is frequency-limited (max 1x/hour) and suppressed in --json mode

**Best Practice: Two-Layer Messaging (Multi-Agent Setups)**

When sending memos to other agents, use a two-layer approach for reliable delivery:

1. **Send the memo** (the actual message, persistent):
   ```bash
   palaia memo send AgentName "Important update about project X"
   # or broadcast to all:
   palaia memo broadcast "New process available — check palaia query --type process"
   ```

2. **Ring the doorbell** (short notification to active sessions, ephemeral):
   Notify active agent sessions that new memos are waiting. This is platform-specific — Palaia doesn't handle this part, but here's how it works in practice:

   *OpenClaw example:*
   ```python
   sessions_send(sessionKey="agent:agentname:...", 
     message="New Palaia memos waiting. Please run: palaia memo inbox")
   ```

   *Other platforms:* Use whatever inter-process or webhook mechanism is available to ping the agent.

   If no active notification is possible, that's fine — the CLI nudge will inform the agent at their next `palaia query` or `palaia write`.

**Why two layers?** The memo is the message (persistent, platform-independent). The doorbell is just a ping (ephemeral, platform-specific). If the doorbell fails, the memo is still there. Never put the full message content in the doorbell — that creates duplicates.

## After Updating Palaia

Palaia has three independent components. Update ALL of them — they version independently:

```bash
# 1. Python CLI (the main tool)
python3 -m pip install --upgrade "palaia[fastembed]"
# or: uv tool install "palaia[fastembed]"  (always include [fastembed]!)

# 2. OpenClaw plugin (memory-slot integration)
npm install -g @byte5ai/palaia@latest

# 3. SKILL.md (agent instructions — if installed via ClawHub)
clawhub update palaia

# 4. Always run after updating:
palaia doctor --fix
palaia warmup
```

**Why all three?** The pip package is the CLI. The npm package is the OpenClaw plugin that wires Palaia into the memory slot. The SKILL.md (via ClawHub) tells agents how to use Palaia. Updating only one leaves the others stale.

`palaia doctor` checks your store for compatibility, suggests new features, and handles version stamping. If the installed version differs from the store version, Palaia will warn you on every CLI call until you run `palaia doctor`.

## Agent Field Guide — Lessons from Production

These are hard-won lessons from agents running Palaia in production. Read this before your first query.

### Performance: warmup is not optional
After install or update, always run `palaia warmup`. Without it, **every query re-computes embeddings for all entries** — that's 14+ seconds on CPU systems. After warmup, the same query takes <2 seconds. The warmup builds a persistent embedding cache that survives restarts.

If queries are slow, check:
1. Did you run `palaia warmup`? (`palaia status` shows "X entries not indexed" if not)
2. Which provider is active? (`palaia detect`) — fastembed is 50x faster than sentence-transformers on CPU-only systems
3. Is the embedding chain correct? (`palaia config show`) — the chain should list your preferred provider first

### Provider choice matters on CPU systems
- **fastembed**: ~0.3s per embedding, lightweight, no GPU needed — **recommended for most systems**
- **sentence-transformers**: ~16s per embedding on CPU (loads PyTorch) — only use if you have a GPU
- **gemini**: Cloud-based via Gemini API (`GEMINI_API_KEY` required). Model: `gemini-embedding-exp-03-07` (default) or `text-embedding-004`. No local compute needed.
- If both are installed, set the chain explicitly: `palaia config set-chain fastembed bm25`
- Cloud providers (openai, gemini) can be combined with local fallback: `palaia config set-chain gemini fastembed bm25`
- Switching providers invalidates the embedding cache — run `palaia warmup` after any chain change

### Write incrementally, not at session end
Don't batch all your learnings into one big write at the end. Write after each meaningful step:
```bash
# After a decision
palaia write "Decided to use FastAPI over Flask — async support needed for webhook handlers" --project myproject --tag decision

# After hitting a blocker
palaia write "Redis connection pool exhausted under load — need to configure max_connections" --project myproject --tag blocker,active-work

# After resolving something
palaia write "Fixed Redis pool: set max_connections=50, added connection timeout=5s" --project myproject --tag learning
```
If your session crashes, the knowledge survives. If you write at the end, it doesn't.

### Use processes for anything repeatable
Release checklists, deployment steps, review procedures — write them as `--type process`. Palaia will automatically surface relevant processes when you write or query related topics (Process Nudge). This only works if the process exists in Palaia, not in a markdown file.

### Parallel writes are safe
Palaia uses kernel-level file locking (`fcntl.flock`) with a Write-Ahead Log (WAL) to ensure data integrity. Multiple concurrent `palaia write` calls — such as those from OpenClaw's parallel tool calling — are safe:
- Each write acquires an exclusive lock before touching the store
- The WAL guarantees crash recovery even if a write is interrupted mid-operation
- No entry loss, no corruption, no cross-contamination between parallel writes
- Lock timeout is 5 seconds (configurable via `lock_timeout_seconds`); stale locks (>60s) are auto-detected and overridden

This means agents can safely issue multiple `palaia write` commands in parallel without coordination.

### Tags are your future self's search terms
Pick tags that your future self (or another agent) would search for. Good tags: `decision`, `learning`, `blocker`, `adr`, `release`, `config`. Bad tags: `important`, `note`, `misc`. Use `--project` consistently — it's the primary filter for all multi-project setups.

### doctor is your first response to any problem
Something weird? Run `palaia doctor --fix` first. It checks versions, repairs chains, rebuilds indexes, and catches most issues automatically. After any update, after any config change, after any error — doctor first, debug second.

### Session continuity checklist
At the start of every session:
1. `palaia doctor` — catch any issues
2. `palaia query "active work"` — pick up where you left off
3. `palaia memo inbox` — check for messages from other agents

Before ending a session:
1. Write your current state: exact step, any blockers, next action
2. Close any open tasks: `palaia edit <id> --status done`

## Configuration Keys

| Key | Default | Description |
|-----|---------|-------------|
| `default_scope` | `team` | Default visibility for new entries |
| `embedding_chain` | *(auto)* | Ordered list of search providers |
| `embedding_provider` | `auto` | Legacy single-provider setting |
| `embedding_model` | — | Per-provider model overrides |
| `hot_threshold_days` | `7` | Days before HOT → WARM |
| `warm_threshold_days` | `30` | Days before WARM → COLD |
| `hot_max_entries` | `50` | Max entries in HOT tier |
| `decay_lambda` | `0.1` | Decay rate for memory scores |

---

© 2026 byte5 GmbH — MIT License
