---
name: mem9
version: 1.0.7
description: |
  Persistent cloud memory for OpenClaw agents.

  Use when users say:
  - "install mem9"
  - "setup memory"
  - "add memory plugin"
  - "openclaw memory"
  - "mem9 onboarding"
  - "memory not working"
  - "import memories"
  - "upload sessions"

keywords:
  - mem9
  - memory plugin
  - persistent memory
  - agent memory
  - install memory
  - setup memory
  - openclaw memory
  - cloud memory
metadata:
  openclaw:
    emoji: "🧠"
---

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   ███╗   ███╗███████╗███╗   ███╗ █████╗                      │
│   ████╗ ████║██╔════╝████╗ ████║██╔══██╗                     │
│   ██╔████╔██║█████╗  ██╔████╔██║╚██████║                     │
│   ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║ ╚═══██║                     │
│   ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║ █████╔╝                     │
│   ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚════╝                      │
│                                                              │
│   persistent memory for ai agents                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

# mem9

mem9 gives OpenClaw persistent memory across resets, restarts, and new machines.

The plugin connects to one cloud memory space, identified by an API key.

When talking to end users:

- Say "API key" or "mem9 API key"
- Prefer `apiKey` when you are editing current OpenClaw plugin config
- Mention `tenantID` only when explaining legacy compatibility or editing old raw config
- Explain that the API key is what reconnects the user to the same mem9 space
- Treat the API key as something the user should save for reconnecting later
- Clearly warn that the API key is effectively a secret and must never be shared

---

## Trigger phrases

Use this skill when the user expresses intent to store, recall, or manage long-term memory.

Common triggers include:

- "remember this"
- "save this for later"
- "don't forget that..."
- "what did I say last time?"
- "recall my preferences"
- "forget that"

---

## When to use this skill

Use this skill when the user wants OpenClaw to persist or manage long-term memory across sessions, devices, or restarts.

Typical situations include:

- The user asks OpenClaw to remember something for future sessions
- The user wants to recall or reconnect to existing long-term memory
- The user wants persistent memory instead of local/session-only memory
- The user wants to import existing OpenClaw memory files into mem9
- The user is moving to a new machine and wants to keep the same memory
- The user wants multiple agents or workflows to share the same memory space

---

## When NOT to use this skill

Do not use this skill for:

- Temporary conversation context that only matters in the current session
- One-off tasks that do not require long-term memory
- Troubleshooting unrelated to mem9 setup, import, or reconnection

---

## What should be remembered

Good candidates:

- User preferences
- Profile facts about the user
- Project context or ongoing work
- Important decisions made during conversations
- Long-term instructions or habits

Avoid storing:

- Temporary debugging context
- Large data or files
- Secrets, passwords, or API keys

---

## Memory intent detection

If the user explicitly asks to remember something (for example: "remember this", "save this", "don't forget"), the agent should store the information using mem9 if mem9 is installed.

If mem9 is not installed yet, suggest installing mem9 to enable persistent memory.

---

## Definition of Done

This task is NOT complete until all of the following are true:

1. mem9 API key is created or verified reachable
2. plugin is installed
3. openclaw.json is configured correctly
4. OpenClaw is restarted
5. setup is verified
6. the user has been sent the full Step 7 handoff message, including:

- next step: import memories
- API key warning
- recovery steps
- backup plan

---

## What You Get

| Tool            | When                                            |
| --------------- | ----------------------------------------------- |
| `memory_store`  | Persist facts, decisions, context               |
| `memory_search` | Find the right memories by keywords and meaning |
| `memory_get`    | Retrieve by ID                                  |
| `memory_update` | Modify existing memory                          |
| `memory_delete` | Remove                                          |

Lifecycle hooks (automatic — no agent action needed):

| Hook                  | Trigger         | What happens                          |
| --------------------- | --------------- | ------------------------------------- |
| `before_prompt_build` | Every LLM call  | Relevant memories injected as context |
| `before_reset`        | Before `/reset` | Session summary saved                 |
| `agent_end`           | Agent finishes  | Last response captured                |

---

## Common failure mode

Agents often finish the technical setup and forget to send the required final handoff.
Prevent this by treating the handoff as part of the setup itself, not as optional follow-up.

---

## Onboarding

### Terminology

Use this distinction consistently:

| Internal term     | User-facing explanation                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------- |
| `apiKey`          | Preferred OpenClaw config field; sends the same mem9 API key in `X-API-Key` for v1alpha2 |
| `tenantID`        | Legacy OpenClaw config field; only mention for compatibility or old raw configs          |
| `API_KEY` env var | A local variable holding the user's mem9 API key                                         |
| `secret`          | Treat as the same value as the mem9 API key unless the user clearly means something else |
| "recovery key"    | Avoid this term; say "API key" instead                                                   |

Short rule: `API key`, `apiKey`, and `secret` may refer to the same mem9 identifier. Prefer saying `API key` to users, use `apiKey` in new config examples, and mention `tenantID` only as the legacy fallback alias.
Security note:
Treat the API key like a secret. Anyone who has it can access that mem9 space.

If the user asks "What is this for?" answer plainly:

> This is the API key that reconnects you to your mem9 space. OpenClaw uses it to save and recall your memory in the right place.

If the user asks "What is the relationship between tenantID and key?" answer plainly:

> You only need the API key. In current OpenClaw config, the preferred field is `apiKey`. `tenantID` is the legacy config field for the same value. Important: this API key is effectively your secret, so save it somewhere safe and never share it with anyone.

### Step 0 — Check for existing API key

`[AGENT]` Ask the user before doing anything else:

> Which setup do you want?
>
> 1. Create a new mem9 API key
> 2. Reconnect an existing mem9 API key
>
> If you choose reconnect, paste your existing API key.
>
> Heads-up: OpenClaw will restart later in this setup. When that happens, please wait a few minutes, then send "Hi" here to reconnect and continue.

Branching:

- If the user chooses reconnect and provides an API key, verify it first.
  - If reachable, continue to Step 2.
  - If unreachable, ask the user to re-check it or choose Step 1 to create a new API key.
- If the user chooses create, continue to Step 1.

```text
API_KEY="<paste-from-user>"
```

When the user provides an existing API key, verify it is reachable before continuing:

```bash
curl -sf \
  -H "X-API-Key: $API_KEY" \
  "https://api.mem9.ai/v1alpha2/mem9s/memories?limit=1" \
  && echo "OK" || echo "UNREACHABLE"
```

If the check returns `OK`, say:

> Great, your existing mem9 API key is reachable. I will keep going and connect this setup to that same memory.

If the check fails, say:

> I could not reach that API key. Please double-check it, or create a new mem9 API key instead.

**If no** — proceed to Step 1 to provision a new API key.

---

### Step 1 — Create a new mem9 API key

> Skip this step if the user provided an existing API key in Step 0.

`[AGENT]`

```bash
curl -sX POST https://api.mem9.ai/v1alpha1/mem9s | jq .
```

Response:

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Save `id` as `API_KEY`.

When explaining it to the user, say:

> Your new mem9 API key is ready. This API key is how this machine, and any future machine you trust, reconnects to the same memory.
>
> Important: this API key is also your secret. Never share it with anyone. If someone else gets it, they can access your memory.

### Step 2 — Install plugin

`[AGENT]` Detect npm registry reachability first. On mainland China / Alibaba Cloud networks, the default npm registry is often slow or unstable. Prefer a one-shot registry override instead of changing the user's global npm config.

```bash
NPMJS_TIME="$(curl -o /dev/null -sS --connect-timeout 2 --max-time 6 -w '%{time_total}' https://registry.npmjs.org/@mem9%2fmem9 || echo timeout)"
MIRROR_TIME="$(curl -o /dev/null -sS --connect-timeout 2 --max-time 6 -w '%{time_total}' https://registry.npmmirror.com/@mem9%2fmem9 || echo timeout)"

if [ "$MIRROR_TIME" != "timeout" ] && { [ "$NPMJS_TIME" = "timeout" ] || awk "BEGIN { exit !($NPMJS_TIME > 2 && $MIRROR_TIME < $NPMJS_TIME) }"; }; then
  echo "Using China npm mirror: https://registry.npmmirror.com"
  NPM_CONFIG_REGISTRY=https://registry.npmmirror.com openclaw plugins install @mem9/mem9
else
  openclaw plugins install @mem9/mem9
fi
```

Decision rule:

- If the official npm registry times out, but `npmmirror` is reachable, treat this as a China-optimized network path and use `https://registry.npmmirror.com`.
- If both are reachable, but the official registry is materially slower, prefer `npmmirror`.
- Do not run `npm config set registry ...` globally unless the user explicitly asks for a permanent npm mirror change.

**Immediately after install completes**, tell the user (before restarting anything):

> ✅ mem9 plugin installed. Next I need to restart the OpenClaw gateway so the plugin can load and the hooks/tools become active.
>
> The restart will take about 1 minute. After that, send me a message to confirm mem9 is functional.

⚠️ **Important (tool ordering):** If you (the agent) are going to restart the gateway automatically via tools/exec, you must send the notice above as an outbound message _first_ (e.g. via the `message` tool). Do **not** rely on the final assistant reply text, because tool calls happen before the final reply is delivered and a gateway restart can prevent that reply from being sent.

Then proceed to the gateway restart step for the user’s environment/profile.

After the restart completes, ask the user to wait ~1 minute and then send a quick message so you can confirm mem9 is working (for example: "Hello mem9").

### Step 3 — Detect OpenClaw version

`[AGENT]` Check the installed OpenClaw version before editing config:

```bash
openclaw --version
```

Routing rule:

- If the reported version is `>= 2.2.0`, use the config path in **Step 4A**.
- If the reported version is `< 2.2.0`, use the config path in **Step 4B**.
- If the version command is unavailable or unclear, tell the user you could not determine the OpenClaw version and ask them which version they are using before editing `openclaw.json`.

### Step 4 — Configure openclaw.json

#### OpenClaw ≥2.2.0

`[AGENT]` Patch existing config (merge-safe, preserves other keys):

```bash
jq --arg api_key "$API_KEY" '
  .plugins.slots.memory = "mem9" |
  if (.plugins.entries.mem9.config // {}) == {}
  then
    .plugins.entries.mem9 = {
      enabled: true,
      config: { apiUrl: "https://api.mem9.ai", apiKey: $api_key }
    }
  else
    .plugins.entries.mem9.config.apiKey = $api_key |
    .plugins.entries.mem9.enabled = true
  end |
  .plugins.allow = ((.plugins.allow // []) + ["mem9"] | unique)
' openclaw.json > tmp.json && mv tmp.json openclaw.json
```

**Note:** The `allow` array is additive—existing entries are preserved, `mem9` is appended (deduplicated).
If `mem9` config already exists, only `apiKey` is written; all other existing fields (such as `apiUrl`, `agentName`) are preserved.

Or if no `openclaw.json` exists, create:

```json
{
  "plugins": {
    "slots": { "memory": "mem9" },
    "entries": {
      "mem9": {
        "enabled": true,
        "config": {
          "apiUrl": "https://api.mem9.ai",
          "apiKey": "<your-api-key>"
        }
      }
    },
    "allow": ["mem9"]
  }
}
```

#### OpenClaw <2.2.0

`[AGENT]` No `allow` array needed:

```bash
jq --arg api_key "$API_KEY" '
  .plugins.slots.memory = "mem9" |
  if (.plugins.entries.mem9.config // {}) == {}
  then
    .plugins.entries.mem9 = {
      enabled: true,
      config: { apiUrl: "https://api.mem9.ai", apiKey: $api_key }
    }
  else
    .plugins.entries.mem9.config.apiKey = $api_key |
    .plugins.entries.mem9.enabled = true
  end
' openclaw.json > tmp.json && mv tmp.json openclaw.json
```

If `mem9` config already exists, only `apiKey` is written; all other existing fields are preserved.

Or if no `openclaw.json` exists, create:

```json
{
  "plugins": {
    "slots": { "memory": "mem9" },
    "entries": {
      "mem9": {
        "enabled": true,
        "config": {
          "apiUrl": "https://api.mem9.ai",
          "apiKey": "<your-api-key>"
        }
      }
    }
  }
}
```

Compatibility rule:

- Existing configs that already use `tenantID` continue to work as a legacy alias for `apiKey`
- Do not use `apiToken` or `userToken`

If result returns stored memory → setup successful.

### Step 5 — Restart OpenClaw

Restart OpenClaw so the new mem9 plugin config is loaded.

### Step 6 — Verify setup

A setup is successful if all of the following are true:

- the mem9 API is reachable
- OpenClaw loads the mem9 plugin without config or plugin errors
- the configured API key can be read successfully
- an empty result is acceptable for a newly created API key
  Note:
  A newly created mem9 API key may contain zero memories. Empty is still a valid success state.

### Step 7 — What's Next

`[AGENT]` After successful setup, the agent MUST send the following structured handoff before ending the task.
Do not summarize or remove any parts of it.
Translate the content into the user's language before sending, while keeping the same structure and all warnings.

```
✅ Your mem9 API key is ready.
🧭 WHAT YOU CAN DO NEXT

Import your existing local memory so mem9 starts with your real history.

Say: "import memories to mem9"
I can scan local memory notes and session files, then transform/import them into mem9.
Common local files include: memory/*.md, MEMORY.md, sessions/*.jsonl.


💾 YOUR MEM9 API KEY

API_KEY: <your-api-key>

This API key is your access key to mem9.
Keep it private and store it somewhere safe.


♻️ RECOVERY

Reinstall mem9 and use the same API_KEY in Step 4.
Your memory will reconnect instantly.


📦 BACKUP PLAN

Keep your original local memory/session files as backup.
Also store the API_KEY in a password manager or secure vault.
```

Do not default to offering a synthetic write/read demo as the next step.

Preferred next-step order:

1. Guide the user to import historical memories
2. Explain the recovery path for a new machine or accidental local loss
3. Explain local backup plus offsite backup
4. Only offer a live write/read verification if the user explicitly asks for a test or if import/recovery is already clear

---

## API Reference

Base: `https://api.mem9.ai`  
Preferred routes: `/v1alpha2/mem9s/...` with `X-API-Key: <api-key>`  
Legacy routes: `/v1alpha1/mem9s/{tenantID}/...`  
Header: `X-Mnemo-Agent-Id: <name>` (optional)

| Method | Path                            | Description                                     |
| ------ | ------------------------------- | ----------------------------------------------- |
| POST   | `/v1alpha1/mem9s`               | Provision tenant                                |
| GET    | `/healthz`                      | Health check                                    |
| POST   | `/v1alpha2/mem9s/memories`      | Create memory (`X-API-Key`)                     |
| GET    | `/v1alpha2/mem9s/memories`      | Search (`?q=`, `?tags=`, `?source=`, `?limit=`) |
| GET    | `/v1alpha2/mem9s/memories/{id}` | Get by ID                                       |
| PUT    | `/v1alpha2/mem9s/memories/{id}` | Update                                          |
| DELETE | `/v1alpha2/mem9s/memories/{id}` | Delete                                          |
| POST   | `/v1alpha2/mem9s/imports`       | Upload file (multipart)                         |
| GET    | `/v1alpha2/mem9s/imports`       | List import tasks                               |
| GET    | `/v1alpha2/mem9s/imports/{id}`  | Task status                                     |

---

## Examples

```bash
export API_KEY="your-api-key"
export API="https://api.mem9.ai/v1alpha2/mem9s"
```

**Store:**

```bash
curl -sX POST "$API/memories" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"content":"Project uses PostgreSQL 15","tags":["tech"],"source":"agent-1"}'
```

**Search:**

```bash
curl -s -H "X-API-Key: $API_KEY" "$API/memories?q=postgres&limit=5"
curl -s -H "X-API-Key: $API_KEY" "$API/memories?tags=tech&source=agent-1"
```

**Get/Update/Delete:**

```bash
curl -s -H "X-API-Key: $API_KEY" "$API/memories/{id}"
curl -sX PUT "$API/memories/{id}" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d '{"content":"updated"}'
curl -sX DELETE "$API/memories/{id}" -H "X-API-Key: $API_KEY"
```

**Import files:**

```bash
# Read agent id from openclaw.json — same field the plugin uses at runtime (agents.list[].id).
# Falls back to plugins.entries.mem9.config.agentName if agents.list is absent.
AGENT_ID="$(jq -r '(.agents.list[0].id) // (.plugins.entries.mem9.config.agentName) // empty' openclaw.json 2>/dev/null)"
AGENT_FIELD=""
[ -n "$AGENT_ID" ] && AGENT_FIELD="-F agent_id=$AGENT_ID"

# Memory file
curl -sX POST "$API/imports" -H "X-API-Key: $API_KEY" $AGENT_FIELD -F "file=@memory.json" -F "file_type=memory"

# Session file
curl -sX POST "$API/imports" -H "X-API-Key: $API_KEY" $AGENT_FIELD -F "file=@session.json" -F "file_type=session" -F "session_id=ses-001"

# Check status
curl -s -H "X-API-Key: $API_KEY" "$API/imports"
```

---

## Communication Style

When presenting onboarding or recovery instructions:

- Use plain product language, not backend vocabulary
- Prefer "API key" or "mem9 API key"
- Explain concretely that the same API key reconnects the same cloud memory on another trusted machine
- If the user sounds worried about recovery, lead with backup/import/reconnect steps instead of API demos

Suggested English wording:

```text
This API_KEY is not a nickname.
It is the key that reconnects you to your mem9 space.
It is also effectively your secret.
Never share it with anyone.
If someone else gets it, they can access your memory.
Save it somewhere safe because you will use the same value later if you want to reconnect on another machine.

The best next step is to bring in your existing history instead of running a demo first.
I can scan local files such as memory.json, memories/*.json, and sessions/*.json and import them into mem9.

Recovery plan:
1. Local backup: keep the original memory/session files even after import
2. Offsite recovery: save the API_KEY in a password manager, team vault, or another secure offsite location
3. New machine recovery: reinstall the plugin and configure the same API_KEY as `apiKey` in openclaw.json to reconnect to the same cloud memory
```

---

## Default Import Behavior

When user says "import memories to mem9" without specifying files:

1. Scan agent workspace for memory/session files
2. Upload **15 most recent** (by mtime)
3. **Upload in parallel** for speed

Before uploading, read the agent id from the active openclaw.json config — using the same resolution order the plugin uses at runtime:

```bash
# agents.list[0].id is what the plugin receives as ctx.agentId at runtime.
# Falls back to plugins.entries.mem9.config.agentName (explicit plugin override).
AGENT_ID="$(jq -r '(.agents.list[0].id) // (.plugins.entries.mem9.config.agentName) // empty' openclaw.json 2>/dev/null)"
AGENT_FIELD=""
[ -n "$AGENT_ID" ] && AGENT_FIELD="-F agent_id=$AGENT_ID"
```

Include `-F "agent_id=$AGENT_ID"` in each upload only when a value is found; omit it entirely otherwise.

**Paths to scan:**

```
./memory.json         → file_type=memory
./memories.json       → file_type=memory
./memories/*.json     → file_type=memory
./sessions/*.json     → file_type=session (session_id = filename)
./session/*.json      → file_type=session (session_id = filename)
```

---

## Troubleshooting

| Symptom                                                                 | Fix                                                                                                                                                                |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Plugin not loading                                                      | Check `slots.memory = "mem9"` and `entries.mem9.enabled = true`                                                                                                    |
| Plugin install hangs or fails on Alibaba Cloud / mainland China network | Re-run **Step 2** and let it switch to `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com`; verify `curl -I https://registry.npmmirror.com/@mem9%2fmem9` succeeds |
| `404` on API call                                                       | Verify the saved API key was written into the plugin config; run `curl https://api.mem9.ai/healthz`                                                                |
| Existing API key unreachable                                            | Re-check the value for typos; confirm network access to `api.mem9.ai`; if the key is lost, provision a new one via Step 1                                          |

---

## Next Steps

After first read, do this immediately:

1. **Import history first** — Offer to scan and upload existing memory/session files before any demo.
2. **Explain recovery** — Tell the user that reusing the same `API_KEY` reconnects the same cloud memory on a new machine.
3. **Explain backup** — Recommend keeping original local files and saving the API key in a secure offsite location.
4. **Explore** — `curl -s -H "X-API-Key: $API_KEY" "https://api.mem9.ai/v1alpha2/mem9s/memories?limit=10" | jq .`
5. **Verify only if useful** — Offer a live `memory_store` / `memory_search` test only after import and recovery guidance are clear, or if the user explicitly asks for validation.

---

## Update

Do not set up automatic daily self-updates for this skill.

Only update the local skill file when the user or maintainer explicitly asks for a refresh from a reviewed source.

---

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░  stateless agents · cloud memory · zero amnesia              ░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```
