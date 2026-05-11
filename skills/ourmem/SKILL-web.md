---
name: ourmem
version: 0.2.1
description: |
  Shared memory that never forgets, hosted at api.ourmem.ai.
  Collective intelligence for AI agents with Space-based sharing across agents and teams.

  Use when users say:
  - "install ourmem" / "install omem"
  - "setup memory" / "setup omem"
  - "add memory plugin"
  - "ourmem onboarding" / "omem onboarding"
  - "memory not working"
  - "remember this"
  - "save this for later"
  - "don't forget"
  - "recall preferences"
  - "what did I say last time"
  - "import memories"
  - "share memories"
  - "share with user"
  - "share memories to someone"
  - "team memory"
  - "shared space"
  - "persistent memory"
  - "cross-session memory"
  - "collective intelligence"
  - "memory analytics"
  - "memory stats"

  Even if the user doesn't say "ourmem" or "omem", trigger when they want persistent memory,
  memory sharing between agents, memory analytics, or memory import/export.
keywords:
  - ourmem
  - omem
  - memory
  - persistent memory
  - agent memory
  - remember
  - recall
  - space sharing
  - team memory
  - collective intelligence
  - memory analytics
  - memory decay
metadata:
  openclaw:
    emoji: "🧠"
---

```
 ┌─────────────────────────────────────────────────────────────┐
 │                                                             │
 │    ██████╗ ██╗   ██╗██████╗ ███╗   ███╗███████╗███╗   ███╗ │
 │   ██╔═══██╗██║   ██║██╔══██╗████╗ ████║██╔════╝████╗ ████║ │
 │   ██║   ██║██║   ██║██████╔╝██╔████╔██║█████╗  ██╔████╔██║ │
 │   ██║   ██║██║   ██║██╔══██╗██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║ │
 │   ╚██████╔╝╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║ │
 │    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ │
 │                                                             │
 │    shared memory that never forgets                         │
 │                                                             │
 └─────────────────────────────────────────────────────────────┘
```

# ourmem (omem)

ourmem (also known as **omem**) gives AI agents shared persistent memory across sessions, devices, agents, and teams.

Most memory systems trap knowledge in silos. ourmem's three-tier Space architecture enables collective intelligence: knowledge flows across agents and teams with provenance tracking and quality-gated sharing. One API key reconnects everything. Hosted at `api.ourmem.ai`, nothing to deploy.

---

## Trigger phrases

Use this skill when the user expresses intent to store, recall, share, or manage long-term memory.

Common triggers include:

- "remember this"
- "save this for later"
- "don't forget that..."
- "what did I say last time?"
- "recall my preferences"
- "forget that"
- "share this with my team"
- "share this with Bob"
- "share my memories with another user"
- "import memories"
- "setup memory"
- "memory not working"

---

## When to use this skill

Use this skill when the user wants persistent or shared memory across sessions, devices, or agents.

Typical situations:

- The user asks the agent to remember something for future sessions
- The user wants to recall or reconnect to existing long-term memory
- The user wants persistent memory instead of local/session-only memory
- The user wants to import existing memory files into ourmem
- The user is moving to a new machine and wants to keep the same memory
- The user wants multiple agents or workflows to share the same memory space
- The user mentions team collaboration or shared knowledge
- The user wants memory analytics or stats

## When NOT to use this skill

Do not use for:

- Temporary conversation context that only matters right now
- One-off tasks that don't need long-term memory
- Troubleshooting unrelated to ourmem setup, import, or reconnection

---

## What to remember / skip

Good candidates:

- User preferences
- Profile facts about the user
- Project context or ongoing work
- Important decisions made during conversations
- Long-term instructions or habits
- Architecture decisions, coding standards

Avoid storing:

- Temporary debugging context
- Large data or files (use file upload instead)
- Secrets, passwords, or API keys
- Content inside `<private>` tags

---

## Memory intent detection

If the user explicitly asks to remember something ("remember this", "save this", "don't forget"), store the information using `memory_store` if ourmem is installed.

If ourmem is not installed yet, suggest installing it:

> I can set up ourmem so I'll remember this across sessions. Takes about 2 minutes. Want to do it now?

---

## Terminology

Use this distinction consistently:

| Internal term | User-facing explanation |
|---------------|------------------------|
| `apiKey` / `OMEM_API_KEY` | The ourmem API key. Sends as `X-API-Key` header. |
| `API key` | Preferred user-facing term. Say "ourmem API key" or just "API key". |
| `secret` | Treat as the same value as the API key unless the user clearly means something else. |
| `tenant` | The workspace behind an API key. Don't use this term with users. |

Short rule: `API key`, `apiKey`, and `secret` may refer to the same ourmem identifier. Prefer saying "API key" to users. Use `OMEM_API_KEY` in config examples.

Security note: Treat the API key like a secret. Anyone who has it can access that ourmem space.

If the user asks "What is this for?" answer plainly:

> This is the API key that reconnects you to your ourmem space. Your agent uses it to save and recall memory in the right place.

---

## Definition of Done

This task is NOT complete until ALL of the following are true:

1. ourmem API key is created or verified reachable
2. Plugin is installed for the user's platform
3. Config is updated with correct URL and key
4. Client is restarted
5. Setup is verified (health + auth pass)
6. The user has been sent the full Step 5 handoff message, including:
   - What they can do now (import, remember, team space)
   - API key display
   - Recovery steps
   - Backup plan

---

## Common failure mode

Agents often finish the technical setup and forget to send the required final handoff message.
Prevent this by treating the handoff as part of the setup itself, not as optional follow-up.

---

## What You Get

| Tool | When |
|------|------|
| `memory_store` | Persist facts, decisions, preferences, context |
| `memory_search` | Find memories by keywords and meaning (hybrid search) |
| `memory_list` | List memories with filters and pagination |
| `memory_get` | Retrieve a specific memory by ID |
| `memory_update` | Modify existing memory content or tags |
| `memory_forget` | Remove a memory |
| `memory_ingest` | Smart-ingest conversation into atomic memories |
| `memory_stats` | View memory analytics and counts |
| `memory_profile` | Get auto-generated user profile |

Lifecycle hooks (automatic, no agent action needed):

| Hook | Trigger | What happens | Platform |
|------|---------|--------------|----------|
| SessionStart | First message in new session | Memories + user profile injected into context (once per session, semantic search) | All |
| Stop | Conversation ends | Last messages auto-captured via smart ingest | Claude Code |
| PreCompact | Before context compaction | Saves memories before context is truncated | Claude Code, OpenCode |

> **Note:** OpenCode does not have a session-end hook. Memory storage in OpenCode relies on the agent proactively using the `memory_store` tool.

---

## Onboarding

### Step 0: Check for existing API key

`[AGENT]` Ask the user before doing anything else:

> Which setup do you want?
>
> 1. Create a new ourmem API key
> 2. Reconnect an existing ourmem API key
>
> If you choose reconnect, paste your existing API key.
>
> Heads-up: your client will restart later in this setup. When that happens, please wait a moment, then send "Hi" to reconnect and continue.

Branching:

- If the user chooses **reconnect** and provides an API key, verify it first:

```bash
API_KEY="<paste-from-user>"
curl -sf \
  -H "X-API-Key: $API_KEY" \
  "https://api.ourmem.ai/v1/memories?limit=1" \
  && echo "OK" || echo "UNREACHABLE"
```

  - If `OK`: say "Great, your existing ourmem API key is reachable. I'll connect this setup to that same memory." Then continue to **Step 2**.
  - If `UNREACHABLE`: say "I could not reach that API key. Please double-check it, or create a new one instead." Ask the user to retry or choose Step 1.

- If the user chooses **create**, continue to Step 1.

---

### Step 1: Create a new API key

> Skip this step if the user provided a working API key in Step 0.

`[AGENT]`

```bash
curl -sX POST https://api.ourmem.ai/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "my-workspace"}' | jq .
```

Response:

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "api_key": "xxx-xxx-xxx",
  "status": "active"
}
```

Save the `api_key` value as `API_KEY`.

When explaining to the user, say:

> Your new ourmem API key is ready. This key reconnects you to the same memory from any machine.
>
> Important: this API key is also your secret. Never share it with anyone. If someone else gets it, they can access your memory.

---

### Step 2: Detect platform and install

`[AGENT]` Auto-detect which platform is running. Do NOT ask the user to pick. Use this detection logic:

**Detection order:**

1. If `claude` CLI exists in PATH, or the environment looks like Claude Code (e.g., `CLAUDE_CODE` env var, or running inside a Claude Code session) -> **Claude Code path**
2. If `opencode.json` exists in the current directory or project root -> **OpenCode path**
3. If `openclaw.json` exists in the current directory or project root -> **OpenClaw path**
4. Otherwise -> **MCP path** (works with Cursor, VS Code, Claude Desktop, and others)

If detection is ambiguous, ask the user which platform they're using.

---

#### Claude Code

`[AGENT]` Set environment variables. Add to `~/.bashrc` or `~/.zshrc` for persistence:

```bash
export OMEM_API_URL="https://api.ourmem.ai"
export OMEM_API_KEY="$API_KEY"
```

Then install the plugin inside Claude Code:

```
/plugin marketplace add ourmem/omem
/plugin install ourmem@ourmem
```

**Immediately after install completes**, tell the user (before restarting):

> ourmem plugin installed. Next I need to restart Claude Code so the memory plugin loads and the hooks become active.
>
> The restart will take a moment. After that, send me a message to confirm ourmem is working.

Then proceed to Step 3.

---

#### OpenCode

`[AGENT]` Add the plugin to `opencode.json`:

```bash
# If opencode.json exists, merge the plugin entry
jq '.plugin = ((.plugin // []) + ["@ourmem/opencode"] | unique)' opencode.json > tmp.json && mv tmp.json opencode.json
```

If no `opencode.json` exists, create one:

```json
{
  "plugin": ["@ourmem/opencode"]
}
```

Set environment variables (add to `~/.bashrc` or `~/.zshrc` for persistence):

```bash
export OMEM_API_URL="https://api.ourmem.ai"
export OMEM_API_KEY="$API_KEY"
```

Tell the user:

> ourmem plugin added to opencode.json. I need to restart OpenCode so the plugin loads.

Then proceed to Step 3.

---

#### OpenClaw

`[AGENT]` Detect npm registry reachability first. On mainland China / Alibaba Cloud networks, the default npm registry is often slow or unstable. Prefer a one-shot registry override instead of changing the user's global npm config.

```bash
NPMJS_TIME="$(curl -o /dev/null -sS --connect-timeout 2 --max-time 6 -w '%{time_total}' https://registry.npmjs.org/@ourmem%2fopenclaw || echo timeout)"
MIRROR_TIME="$(curl -o /dev/null -sS --connect-timeout 2 --max-time 6 -w '%{time_total}' https://registry.npmmirror.com/@ourmem%2fopenclaw || echo timeout)"

if [ "$MIRROR_TIME" != "timeout" ] && { [ "$NPMJS_TIME" = "timeout" ] || awk "BEGIN { exit !($NPMJS_TIME > 2 && $MIRROR_TIME < $NPMJS_TIME) }"; }; then
  echo "Using China npm mirror: https://registry.npmmirror.com"
  NPM_CONFIG_REGISTRY=https://registry.npmmirror.com openclaw plugins install @ourmem/openclaw
else
  openclaw plugins install @ourmem/openclaw
fi
```

Decision rule:

- If the official npm registry times out but `npmmirror` is reachable, use `https://registry.npmmirror.com`.
- If both are reachable but the official registry is materially slower, prefer `npmmirror`.
- Do NOT run `npm config set registry ...` globally unless the user explicitly asks.

Then configure `openclaw.json`:

```bash
jq --arg api_key "$API_KEY" '
  .plugins.slots.memory = "ourmem" |
  if (.plugins.entries.ourmem.config // {}) == {}
  then
    .plugins.entries.ourmem = {
      enabled: true,
      config: { apiUrl: "https://api.ourmem.ai", apiKey: $api_key }
    }
  else
    .plugins.entries.ourmem.config.apiKey = $api_key |
    .plugins.entries.ourmem.enabled = true
  end |
  .plugins.allow = ((.plugins.allow // []) + ["ourmem"] | unique)
' openclaw.json > tmp.json && mv tmp.json openclaw.json
```

If no `openclaw.json` exists, create:

```json
{
  "plugins": {
    "slots": { "memory": "ourmem" },
    "entries": {
      "ourmem": {
        "enabled": true,
        "config": {
          "apiUrl": "https://api.ourmem.ai",
          "apiKey": "<your-api-key>"
        }
      }
    },
    "allow": ["ourmem"]
  }
}
```

Tell the user:

> ourmem plugin installed and configured. I need to restart the OpenClaw gateway so the plugin loads.

Then proceed to Step 3.

---

#### MCP (Cursor / VS Code / Claude Desktop)

`[AGENT]` Add the ourmem MCP server to the client's config file.

**Cursor:** Edit `.cursor/mcp.json` in the project root (or global settings).

**VS Code:** Edit `.vscode/mcp.json` or user settings.

**Claude Desktop:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows).

Add this entry:

```json
{
  "mcpServers": {
    "ourmem": {
      "command": "npx",
      "args": ["-y", "@ourmem/mcp"],
      "env": {
        "OMEM_API_KEY": "$API_KEY",
        "OMEM_API_URL": "https://api.ourmem.ai"
      }
    }
  }
}
```

Replace `$API_KEY` with the actual key.

Tell the user:

> ourmem MCP server configured. Please restart your app so it picks up the new config.

Then proceed to Step 3.

---

### Step 3: Restart client

`[AGENT]` Tell the user a restart is needed and what to expect:

> I'm restarting so the memory plugin loads. After the restart, send me a message to confirm everything is working.
>
> This usually takes less than a minute.

Platform-specific restart:

- **Claude Code**: restart the `claude` process
- **OpenCode**: restart the `opencode` process
- **OpenClaw**: restart the gateway
- **MCP clients**: restart the app (Cursor, VS Code, Claude Desktop)

---

### Step 4: Verify

`[AGENT]` After restart, run these checks:

```bash
# 1. Health check (no auth needed)
curl -sf https://api.ourmem.ai/health && echo "Server OK"

# 2. Auth check
curl -sf -H "X-API-Key: $API_KEY" "https://api.ourmem.ai/v1/memories?limit=1" && echo "Auth OK"
```

A setup is successful if:

- The ourmem API is reachable (health returns OK)
- The API key authenticates successfully (auth returns OK or empty list)
- Empty results are acceptable for a newly created API key

If both pass, proceed to Step 5.

If health fails: "The ourmem server seems unreachable. Check your network connection and try again."

If auth fails: "Your API key didn't authenticate. Double-check the key value, or create a new one."

---

### Step 5: Handoff

`[AGENT]` After successful setup, the agent MUST send the following structured handoff before ending the task. Do not summarize or remove any parts. Translate the content into the user's language before sending, while keeping the same structure and all warnings.

```
ourmem is ready.

WHAT YOU CAN DO NOW

1. Import your existing memories (recommended)
   Say: "import memories to ourmem"
   I'll scan local files and import your history automatically.

2. Just talk normally. I'll automatically remember important things.

3. Say "remember: [something]" to explicitly save a fact.

4. Say "create a team space" to share memories between agents.


YOUR OURMEM API KEY

  API Key: <your-api-key>
  Server:  https://api.ourmem.ai

This API key is your access key to ourmem.
Keep it private and store it somewhere safe.


RECOVERY

Reinstall the plugin with the same API key.
Your memory reconnects instantly.


BACKUP PLAN

Keep your original local memory/session files as backup.
Store the API key in a password manager or secure vault.
On a new machine: reinstall the plugin, configure the same API key, done.
```

Do not default to offering a synthetic write/read demo as the next step.

Preferred next-step order:

1. Guide the user to import historical memories
2. Explain the recovery path for a new machine or accidental loss
3. Explain local backup plus offsite backup
4. Only offer a live write/read verification if the user explicitly asks

---

## Smart Ingest

When conversations are ingested (`"mode": "smart"`), the server runs a multi-stage pipeline:

1. **LLM extraction**: extracts atomic facts from conversation, classified into 6 categories (profile, preferences, entities, events, cases, patterns)
2. **Noise filter**: regex patterns + vector prototype matching + feedback learning removes low-value content
3. **Admission control**: 5-dimension scoring (utility, confidence, novelty, recency, type prior) gates what gets stored
4. **7-decision reconciliation**: each fact is compared against existing memories: CREATE (new), MERGE (refine), SKIP (duplicate), SUPERSEDE (outdated), SUPPORT (reinforce), CONTEXTUALIZE (add nuance), or CONTRADICT (conflicting)

The memory store gets smarter over time. Contradictions are resolved, duplicates are merged, noise is filtered.

---

## Space Sharing

ourmem organizes memories into three-tier Spaces for collective intelligence:

| Type | Scope | Example |
|------|-------|---------|
| Personal | One user, multiple agents | Your Coder + Writer share preferences |
| Team | Multiple users | Backend team shares architecture decisions |
| Organization | Company-wide | Tech standards, security policies |

**Roles:** `admin` (full control), `member` (read/write), `reader` (read-only)

Each agent sees: own private + shared spaces. Can modify own + shared. Never another agent's private data. Every shared memory carries provenance: who shared it, when, and where it came from.

### When to suggest Spaces

Proactively suggest Spaces when:

- User has multiple agents ("I also use Claude Code for writing") -> suggest sharing preferences across agents
- User mentions team collaboration ("share this with my team") -> suggest creating a team space
- User wants org-wide knowledge ("company coding standards") -> suggest organization space

How to explain it:

> Right now your memories are private to this agent. If you want your other agents to also access these memories, I can set up sharing. Want me to create a shared space?

### Space operations

**List my spaces:**

```bash
curl -s https://api.ourmem.ai/v1/spaces -H "X-API-Key: $API_KEY"
```

**Create a team space:**

```bash
curl -sX POST https://api.ourmem.ai/v1/spaces \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"name": "Backend Team", "space_type": "team"}'
```

**Add a member to a space:**

```bash
curl -sX POST "https://api.ourmem.ai/v1/spaces/SPACE_ID/members" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"user_id": "colleague-tenant-id", "role": "member"}'
```

**Share a memory to a space:**

```bash
curl -sX POST "https://api.ourmem.ai/v1/memories/MEMORY_ID/share" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"target_space": "team/SPACE_ID"}'
```

**Batch share multiple memories:**

```bash
curl -sX POST https://api.ourmem.ai/v1/memories/batch-share \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"memory_ids": ["id1", "id2", "id3"], "target_space": "team/SPACE_ID"}'
```

**Pull a memory from another space to personal:**

```bash
curl -sX POST "https://api.ourmem.ai/v1/memories/MEMORY_ID/pull" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"source_space": "team/SPACE_ID"}'
```

After sharing, search automatically spans all spaces the user has access to. No extra configuration needed.

### Cross-User Sharing (Convenience)

When a user says "share this with Bob" or "share my memories with another user", use the convenience APIs that handle space creation automatically:

**Share a single memory to another user:**

```bash
curl -sX POST "https://api.ourmem.ai/v1/memories/MEMORY_ID/share-to-user" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"target_user": "TARGET_USER_TENANT_ID"}'
# Returns: { "space_id": "team/xxx", "shared_copy_id": "yyy", "space_created": true }
```

This auto-creates a bridging Team Space if needed, adds the target user as a member, and shares the memory in one step.

**Share all matching memories to another user:**

```bash
curl -sX POST "https://api.ourmem.ai/v1/memories/share-all-to-user" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"target_user": "TARGET_USER_TENANT_ID", "filters": {"min_importance": 0.7}}'
# Returns: { "space_id": "team/xxx", "space_created": false, "total": 80, "shared": 15, ... }
```

**Agent workflow:**

1. User says "share this with Bob" → agent needs Bob's tenant ID (API key)
2. If the agent doesn't know Bob's ID, ask the user for it
3. Call `share-to-user` with the memory ID and Bob's tenant ID
4. Report: "Shared to Bob via team space {space_id}. Bob can now find it when searching."

Proactively suggest cross-user sharing when:

- User mentions sharing with a specific person ("send this to Alice")
- User wants another user's agent to have access to certain memories
- User asks to collaborate with someone on a project

---

## Memory Import

When the user says "import memories to ourmem", scan their workspace for existing memory and session files, then batch-import them.

### Auto-scan and import flow

1. Detect `agent_id` from platform config (if available)
2. Scan workspace for memory/session files
3. Upload the 20 most recent files (by modification time) via `/v1/imports`
4. Upload in parallel for speed
5. Report results (imported/skipped/errors)

**Paths to scan:**

| Path pattern | file_type | Platform |
|-------------|-----------|----------|
| `./memory.json` | memory | OpenClaw |
| `./memories.json` | memory | OpenClaw |
| `./memories/*.json` | memory | OpenClaw |
| `./sessions/*.json` | session | OpenClaw |
| `./session/*.json` | session | OpenClaw |
| `./.claude/memory/*.json` | memory | Claude Code |
| `./MEMORY.md` | markdown | Common |
| `./memory/*.md` | markdown | Common |

### Import API

**Batch import a file (with auto intelligence):**

```bash
curl -sX POST https://api.ourmem.ai/v1/imports \
  -H "X-API-Key: $API_KEY" \
  -F "file=@memory.json" \
  -F "file_type=memory" \
  -F "agent_id=coder" \
  -F "strategy=auto"
```

**Strategy parameter** controls how content is chunked before LLM extraction:

| Strategy | When auto-detected | Behavior |
|----------|-------------------|----------|
| `auto` (default) | Heuristic detection | Auto-selects based on content type |
| `atomic` | Short JSON facts, key-value pairs | Each item = one memory, minimal LLM processing |
| `section` | Markdown with headings, structured docs | Split by sections, LLM extracts per section |
| `document` | Long prose, conversations, session logs | Entire file as one chunk, LLM extracts holistically |

By default, `post_process=true`: after storage completes, a background task runs LLM re-extraction (same as Smart Ingest) + reconciliation to discover relations.

The `content` field preserves original source text. Vector embeddings and BM25 index are built from the original text, ensuring content fidelity and language preservation (e.g., Chinese input stays Chinese).

To skip intelligence processing: add `-F "post_process=false"`.

Supported `file_type`: `memory` (JSON array), `session` (JSON/JSONL messages), `markdown` (split by paragraphs), `jsonl` (one JSON per line).

Optional fields: `agent_id`, `session_id`, `space_id` (defaults to personal space), `post_process` (default true), `strategy` (default auto).

**Cross-reconcile (discover relations via vector similarity):**

```bash
curl -sX POST "https://api.ourmem.ai/v1/imports/cross-reconcile" -H "X-API-Key: $API_KEY"
```

Scans all memories and discovers SUPPORT/CONTEXTUALIZE/CONTRADICT/SUPERSEDE relations between them. Useful after multiple imports to connect related memories across batches.

**Check import progress:**

```bash
curl -s "https://api.ourmem.ai/v1/imports/IMPORT_ID" -H "X-API-Key: $API_KEY"
```

Returns phase-by-phase progress: storage -> extraction -> reconciliation.

**Manually trigger intelligence on a past import:**

```bash
curl -sX POST "https://api.ourmem.ai/v1/imports/IMPORT_ID/intelligence" -H "X-API-Key: $API_KEY"
```

### Smart ingest from conversation history

```bash
curl -sX POST https://api.ourmem.ai/v1/memories \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"messages": [{"role":"user","content":"I prefer Rust"}], "mode": "smart"}'
```

### Direct fact storage

```bash
curl -sX POST https://api.ourmem.ai/v1/memories \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"content": "User prefers dark mode", "tags": ["preference"]}'
```

---

## Analytics

ourmem provides memory analytics through the stats API:

- **Overview** (`/v1/stats`): totals by type, category, tier, space, agent + timeline
- **Space overview** (`/v1/stats/spaces`): per-space stats, member contributions, sharing activity
- **Sharing flow** (`/v1/stats/sharing`): who shared what, where, when + flow graph
- **Agent activity** (`/v1/stats/agents`): per-agent memory creation, search counts, top categories
- **Tag frequency** (`/v1/stats/tags`): tag usage across spaces
- **Decay curves** (`/v1/stats/decay?memory_id=X`): Weibull decay visualization for any memory
- **Relation graph** (`/v1/stats/relations`): memory relationship network with cross-space edges
- **Server config** (`/v1/stats/config`): decay parameters, promotion thresholds, retrieval settings

---

## API Reference

Base: `https://api.ourmem.ai`
Auth: `X-API-Key: <api-key>` header on all requests (except `/health` and `POST /v1/tenants`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| **System** | | |
| GET | `/health` | Health check (no auth) |
| POST | `/v1/tenants` | Create workspace, get API key |
| **Core** | | |
| POST | `/v1/memories` | Store memory or smart-ingest conversation |
| GET | `/v1/memories/search?q=` | Hybrid search (vector + keyword) |
| GET | `/v1/memories?limit=20` | List with filters + pagination |
| GET | `/v1/memories/:id` | Get single memory |
| PUT | `/v1/memories/:id` | Update memory |
| DELETE | `/v1/memories/:id` | Soft delete |
| POST | `/v1/memories/batch-delete` | Batch delete by IDs or filter |
| DELETE | `/v1/memories/all` | Clear all memories (requires X-Confirm header) |
| **Import** | | |
| POST | `/v1/imports` | Batch import file (strategy=auto/atomic/section/document) |
| GET | `/v1/imports/{id}` | Check import progress |
| POST | `/v1/imports/{id}/intelligence` | Trigger intelligence on past import |
| POST | `/v1/imports/{id}/rollback` | Rollback an import (delete memories + sessions) |
| POST | `/v1/imports/cross-reconcile` | Discover relations via vector similarity |
| **Profile** | | |
| GET | `/v1/profile` | User profile (static + dynamic) |
| **Spaces** | | |
| POST | `/v1/spaces` | Create shared space |
| GET | `/v1/spaces` | List accessible spaces |
| POST | `/v1/spaces/:id/members` | Add member to space |
| **Sharing** | | |
| POST | `/v1/memories/:id/share` | Share to a space |
| POST | `/v1/memories/:id/share-to-user` | One-step share to another user (auto-creates bridging space) |
| POST | `/v1/memories/:id/pull` | Pull from another space |
| POST | `/v1/memories/batch-share` | Batch share multiple memories |
| POST | `/v1/memories/share-all-to-user` | Bulk share to another user (auto-creates bridging space) |
| **Files** | | |
| POST | `/v1/files` | Upload file (PDF/image/video/code) |
| **Analytics** | | |
| GET | `/v1/stats` | Global stats (by type/category/tier/space/agent) |
| GET | `/v1/stats/spaces` | Per-space overview |
| GET | `/v1/stats/sharing` | Sharing flow analysis |
| GET | `/v1/stats/agents` | Agent activity |
| GET | `/v1/stats/tags` | Tag frequency |
| GET | `/v1/stats/decay?memory_id=X` | Decay curve for a memory |
| GET | `/v1/stats/relations` | Memory relationship graph |
| GET | `/v1/stats/config` | Server config parameters |

Full API (35 endpoints): https://github.com/ourmem/omem/blob/main/docs/API.md

---

## Examples

```bash
export API_KEY="your-api-key"
export API="https://api.ourmem.ai"
```

**Store a memory:**

```bash
curl -sX POST "$API/v1/memories" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"content":"Project uses PostgreSQL 15","tags":["tech"]}'
```

**Search memories:**

```bash
curl -s "$API/v1/memories/search?q=postgres&limit=5" \
  -H "X-API-Key: $API_KEY"
```

**List memories with filters:**

```bash
curl -s "$API/v1/memories?limit=20&tags=tech" \
  -H "X-API-Key: $API_KEY"
```

**Get / Update / Delete:**

```bash
# Get by ID
curl -s "$API/v1/memories/{id}" -H "X-API-Key: $API_KEY"

# Update
curl -sX PUT "$API/v1/memories/{id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"content":"Updated content","tags":["tech","updated"]}'

# Delete
curl -sX DELETE "$API/v1/memories/{id}" -H "X-API-Key: $API_KEY"
```

**Import a file:**

```bash
curl -sX POST "$API/v1/imports" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@memory.json" \
  -F "file_type=memory" \
  -F "strategy=auto"
```

**Smart ingest conversation:**

```bash
curl -sX POST "$API/v1/memories" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"messages":[{"role":"user","content":"I prefer dark mode"}],"mode":"smart"}'
```

---

## Security

- **Tenant isolation**: every API call is scoped to your tenant via X-API-Key. Data is physically separated per tenant.
- **Privacy protection**: `<private>` tag redaction strips sensitive content before storage.
- **Admission control**: 5-dimension scoring gate rejects low-quality or noisy data before it enters the memory store.
- **Open source**: Apache-2.0 licensed plugins. Audit every line of code.

---

## Communication Style

When presenting onboarding or recovery instructions:

- Use plain product language, not backend vocabulary
- Prefer "API key" or "ourmem API key"
- Explain concretely that the same API key reconnects the same cloud memory on another trusted machine
- If the user sounds worried about recovery, lead with backup/import/reconnect steps instead of API demos
- Use the user's language (detect from conversation)
- Brand: "ourmem" or "omem" (both acceptable, lowercase). "omem" is the short form — use whichever the user uses.
- Official domain: ourmem.ai, API: api.ourmem.ai
- "Space" (capitalized), "Smart Ingest"

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Plugin not loading | Check config has correct `apiUrl` / `OMEM_API_URL` and `apiKey` / `OMEM_API_KEY` |
| Plugin install hangs or fails on China network | Re-run install with `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com`; verify `curl -I https://registry.npmmirror.com/@ourmem%2fopenclaw` succeeds |
| Connection refused | Server may be down. Try `curl https://api.ourmem.ai/health` and retry in a minute |
| 401 Unauthorized | API key is wrong. Verify the key or create a new tenant via `POST /v1/tenants` |
| 404 on API call | URL path should start with `/v1/`. Check the endpoint table above |
| npm install hangs | Use mirror: `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com` |
| No memories returned | Normal for new keys. Store one first, then search |
| Search returns empty | Index builds after first write. Wait a moment and retry |
| Existing API key unreachable | Re-check the value for typos; confirm network access to `api.ourmem.ai`; if the key is lost, provision a new one via Step 1 |

---

## Default Import Behavior

When user says "import memories to ourmem" without specifying files:

1. Scan agent workspace for memory/session files (see paths table above)
2. Upload the **20 most recent** (by mtime)
3. Upload **in parallel** for speed
4. Report results when done

---

## Next Steps

After first read, do this immediately:

1. **Import history first**: offer to scan and upload existing memory/session files before any demo
2. **Explain recovery**: tell the user that reusing the same API key reconnects the same cloud memory on a new machine
3. **Explain backup**: recommend keeping original local files and saving the API key in a secure offsite location
4. **Explore**: `curl -s -H "X-API-Key: $API_KEY" "https://api.ourmem.ai/v1/memories?limit=10" | jq .`
5. **Verify only if useful**: offer a live `memory_store` / `memory_search` test only after import and recovery guidance are clear, or if the user explicitly asks

---

## Update

Do not set up automatic daily self-updates for this skill.

Only update the local skill file when the user or maintainer explicitly asks for a refresh from a reviewed source.

---

```
 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 ░  shared memory · collective intelligence · zero amnesia       ░
 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```
