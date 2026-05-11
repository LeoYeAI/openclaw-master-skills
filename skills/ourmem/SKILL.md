---
name: ourmem
version: 0.2.1
description: |
  Shared memory that never forgets. Cloud hosted or self-deployed.
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
  - "self-host memory"
  - "deploy memory server"

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
  - self-host
metadata:
  openclaw:
    emoji: "🧠"
---

# ourmem (omem) — Shared Memory That Never Forgets

ourmem (also known as **omem**) gives AI agents shared persistent memory across sessions, devices, agents, and teams.

Most memory systems trap knowledge in silos. ourmem's three-tier Space architecture enables collective intelligence: knowledge flows across agents and teams with provenance tracking and quality-gated sharing. One API key reconnects everything. Available as hosted (`api.ourmem.ai`) or self-deployed.

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
- "self-host memory"
- "deploy memory server"

---

## When to use this skill

Use when the user wants persistent or shared memory across sessions, devices, or agents.

Typical situations:

- The user asks the agent to remember something for future sessions
- The user wants to recall or reconnect to existing long-term memory
- The user wants persistent memory instead of local/session-only memory
- The user wants to import existing memory files into ourmem
- The user is moving to a new machine and wants to keep the same memory
- The user wants multiple agents or workflows to share the same memory space
- The user mentions team collaboration or shared knowledge
- The user wants memory analytics or stats
- The user wants to self-host the memory server

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

### Step 0: Choose mode

`[AGENT]` Ask the user before doing anything else:

> How would you like to run ourmem?
>
> 1. **Hosted** (api.ourmem.ai) — no server to manage, start in 2 minutes
> 2. **Self-hosted** (Docker or binary on your machine) — full control, data stays local
>
> Already have an API key? Paste it and I'll reconnect you.
>
> Heads-up: your client will restart later in this setup. When that happens, please wait a moment, then send "Hi" to reconnect and continue.

Branching:

- **Hosted** -> READ `references/hosted-setup.md` for detailed setup, then continue from Step 1
- **Self-hosted** -> READ `references/selfhost-setup.md` for server deployment + setup, then continue from Step 1
- **Existing key** -> Verify it first (see below), then skip to Step 2

If the user provides an existing API key, verify reachability:

```bash
API_URL="${OMEM_API_URL:-https://api.ourmem.ai}"
API_KEY="<paste-from-user>"
curl -sf -H "X-API-Key: $API_KEY" "$API_URL/v1/memories?limit=1" \
  && echo "OK" || echo "UNREACHABLE"
```

- If `OK`: say "Great, your existing ourmem API key is reachable. I'll connect this setup to that same memory." Then continue to **Step 2**.
- If `UNREACHABLE`: say "I could not reach that API key. Please double-check it, or create a new one instead." Ask the user to retry or choose a fresh setup.

---

### Step 1: Create API key

> Skip this step if the user provided a working API key in Step 0.

`[AGENT]`

**Hosted:**

```bash
curl -sX POST https://api.ourmem.ai/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "my-workspace"}' | jq .
```

**Self-hosted:**

```bash
curl -sX POST http://localhost:8080/v1/tenants \
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

1. If `claude` CLI exists in PATH, or the environment looks like Claude Code -> **Claude Code path**
2. If `opencode.json` exists in the current directory or project root -> **OpenCode path**
3. If `openclaw.json` exists in the current directory or project root -> **OpenClaw path**
4. Otherwise -> **MCP path** (works with Cursor, VS Code, Claude Desktop, and others)

If detection is ambiguous, ask the user which platform they're using.

**Quick reference per platform:**

| Platform | Install command | Config |
|----------|----------------|--------|
| Claude Code | `/plugin marketplace add ourmem/omem` then `/plugin install ourmem@ourmem` | `OMEM_API_URL` + `OMEM_API_KEY` env vars |
| OpenCode | `"plugin": ["@ourmem/opencode"]` in opencode.json | `OMEM_API_URL` + `OMEM_API_KEY` env vars |
| OpenClaw | `openclaw plugins install @ourmem/openclaw` | `openclaw.json` with apiUrl + apiKey |
| MCP | `npx -y @ourmem/mcp` in MCP config | `OMEM_API_URL` + `OMEM_API_KEY` in env block |

For detailed per-platform instructions (config file formats, jq commands, npm mirror detection for China networks), READ `references/hosted-setup.md` or `references/selfhost-setup.md` depending on the mode chosen in Step 0.

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
API_URL="${OMEM_API_URL:-https://api.ourmem.ai}"

# 1. Health check (no auth needed)
curl -sf "$API_URL/health" && echo "Server OK"

# 2. Auth check
curl -sf -H "X-API-Key: $API_KEY" "$API_URL/v1/memories?limit=1" && echo "Auth OK"
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
  Server:  <api-url>

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

Proactively suggest Spaces when:

- User has multiple agents -> suggest sharing preferences across agents
- User mentions team collaboration -> suggest creating a team space
- User wants org-wide knowledge -> suggest organization space

For Space API operations (create, add members, share, pull, batch share), READ `references/api-quick-ref.md`.

### Cross-User Sharing (Convenience)

When a user says "share this with Bob" or "share my memories with another user", use the convenience APIs that handle space creation automatically:

**Share a single memory to another user:**

The agent should call `share-to-user` which auto-creates a bridging Team Space if needed, adds the target user as a member, and shares the memory in one step.

```bash
curl -sX POST "$API_URL/v1/memories/MEMORY_ID/share-to-user" \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"target_user": "TARGET_USER_TENANT_ID"}'
# Returns: { "space_id": "team/xxx", "shared_copy_id": "yyy", "space_created": true }
```

**Share all matching memories to another user:**

When the user wants to share everything (or a filtered subset) with someone:

```bash
curl -sX POST "$API_URL/v1/memories/share-all-to-user" \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
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

**Auto-scan flow:**

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
| `./.claude/memory/*.json` | memory | Claude Code |
| `./MEMORY.md` | markdown | Common |
| `./memory/*.md` | markdown | Common |

**Import API:**

```bash
curl -sX POST "$API_URL/v1/imports" -H "X-API-Key: $API_KEY" \
  -F "file=@memory.json" -F "file_type=memory" -F "strategy=auto"
```

**Strategy parameter** controls how content is chunked: `auto` (default, heuristic detection), `atomic` (short facts, minimal LLM), `section` (split by headings), `document` (entire file as one chunk).

**Cross-reconcile** (discover relations via vector similarity):

```bash
curl -sX POST "$API_URL/v1/imports/cross-reconcile" -H "X-API-Key: $API_KEY"
```

For full import API details (progress tracking, intelligence triggers, rollback), READ `references/api-quick-ref.md`.

---

## Analytics

Memory analytics through the stats API:

- **Overview** (`/v1/stats`): totals by type, category, tier, space, agent + timeline
- **Space overview** (`/v1/stats/spaces`): per-space stats, member contributions
- **Sharing flow** (`/v1/stats/sharing`): who shared what, where, when
- **Agent activity** (`/v1/stats/agents`): per-agent memory creation, search counts
- **Tag frequency** (`/v1/stats/tags`): tag usage across spaces
- **Decay curves** (`/v1/stats/decay?memory_id=X`): Weibull decay visualization
- **Relation graph** (`/v1/stats/relations`): memory relationship network
- **Server config** (`/v1/stats/config`): decay parameters, retrieval settings

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
| Plugin install hangs or fails on China network | Re-run install with `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com` |
| Connection refused | Server may be down. Try `curl $OMEM_API_URL/health` and retry in a minute |
| 401 Unauthorized | API key is wrong. Verify the key or create a new tenant via `POST /v1/tenants` |
| 404 on API call | URL path should start with `/v1/`. Check the endpoint table below |
| npm install hangs | Use mirror: `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com` |
| No memories returned | Normal for new keys. Store one first, then search |
| Search returns empty | Index builds after first write. Wait a moment and retry |
| Existing API key unreachable | Re-check the value for typos; confirm network access to the server |
| Embedding errors | Check `OMEM_EMBED_PROVIDER` on the server; use `noop` for testing |

---

## API Reference

Base: `https://api.ourmem.ai` (hosted) or `http://localhost:8080` (self-hosted)
Auth: `X-API-Key: <api-key>` header on all requests (except `/health` and `POST /v1/tenants`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (no auth) |
| POST | `/v1/tenants` | Create workspace, get API key |
| POST | `/v1/memories` | Store memory or smart-ingest conversation |
| GET | `/v1/memories/search?q=` | Hybrid search (vector + keyword) |
| GET | `/v1/memories?limit=20` | List with filters + pagination |
| GET | `/v1/memories/:id` | Get single memory |
| PUT | `/v1/memories/:id` | Update memory |
| DELETE | `/v1/memories/:id` | Soft delete |
| POST | `/v1/memories/batch-delete` | Batch delete by IDs or filter |
| DELETE | `/v1/memories/all` | Clear all (requires X-Confirm header) |
| POST | `/v1/imports` | Batch import file |
| POST | `/v1/imports/cross-reconcile` | Discover relations via vector similarity |
| GET | `/v1/profile` | User profile (static + dynamic) |
| POST | `/v1/spaces` | Create shared space |
| GET | `/v1/spaces` | List accessible spaces |
| POST | `/v1/spaces/:id/members` | Add member to space |
| POST | `/v1/memories/:id/share` | Share to a space |
| POST | `/v1/memories/:id/share-to-user` | One-step share to another user (auto-creates bridging space) |
| POST | `/v1/memories/:id/pull` | Pull from another space |
| POST | `/v1/memories/batch-share` | Batch share multiple memories |
| POST | `/v1/memories/share-all-to-user` | Bulk share to another user (auto-creates bridging space) |
| POST | `/v1/files` | Upload file (PDF/image/video/code) |
| GET | `/v1/stats` | Global stats |
| GET | `/v1/stats/*` | Spaces, sharing, agents, tags, decay, relations, config |

For full endpoint details with curl examples, READ `references/api-quick-ref.md`.

For the complete API documentation (35 endpoints), READ `docs/API.md`.

---

## Update

Do not set up automatic daily self-updates for this skill.

Only update the local skill file when the user or maintainer explicitly asks for a refresh from a reviewed source.
