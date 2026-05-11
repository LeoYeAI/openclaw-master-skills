---
name: medo-app-builder
description: Create, modify, generate, and deploy websites, web apps, dashboards, SaaS products, internal tools, interactive web pages, Weixin mini program , games on the Baidu Medo platform using natural-language instructions.
metadata: { "openclaw": {"requires": { "bins": ["python3"], "env":["MEDO_API_KEY"]},"primaryEnv":"MEDO_API_KEY" } }
---

# Medo App Builder

Medo is a **chat-driven full-stack application builder**.
Official website: https://www.medo.dev

Users describe what they want in natural language and Medo generates a **production-ready web product**, including:

- frontend UI
- backend services
- database schema
- integrations
- deployable hosting

Typical outputs include:

- websites
- web applications
- dashboards
- SaaS products
- admin panels
- internal tools
- landing pages
- interactive web pages
- browser games and mini games

This skill enables AI agents to interact with the **Medo platform** to create, iterate, generate, and deploy applications.

All platform operations must be executed through the packaged CLI script:

```bash
python scripts/medo_api.py <command> [options]
```

Do **not** call platform APIs directly. Always use the CLI commands provided by this skill.

---

# When to Use This Skill

Use this skill whenever the user wants to:

* create a **website**
* create a **webpage**
* build a **web application**
* build a **dashboard**
* create a **SaaS product**
* build an **admin panel**
* build an **internal tool**
* create a **landing page**
* build an **interactive web page**
* create a **browser game**
* create a **mini game**
* generate an **MVP web product**
* modify an existing **Medo project**
* publish or deploy a **Medo application**

Do **not** use this skill for unrelated programming tasks.

---

# Routing Keywords

Trigger this skill if the request includes concepts such as:

* build a website
* create a webpage
* build a web app
* create a SaaS
* build a dashboard
* create an admin panel
* build an internal tool
* create a landing page
* build a browser game
* create a mini game
* generate a web product
* make a snake game webpage
* build a todo web app
* create a blog site

---

# Example Requests

Examples that should route to this skill:

* "Create a todo list web app"
* "Build a personal blog website"
* "Make a dashboard for sales analytics"
* "Create a SaaS landing page"
* "Build an admin panel"
* "Write a snake game webpage"
* "Create a browser game"
* "Build a mini web game"
* "Modify my Medo project"
* "Publish this Medo app"

---

# Stateless Execution Model

The CLI script is **stateless**.

It does not store workflow state between calls.

Application workflow state is maintained by the Medo platform and must be inferred from:

* `appId`
* `conversationId`
* application detail
* conversation trajectory events

Agents must pass the appropriate identifiers when continuing conversations or modifying applications.

---

# Application Lifecycle Rules

Medo applications follow a strict lifecycle.

Agents must follow these rules.

---

## Initial Creation

For a new application:

1. Start with a `chat` request describing the product.
2. The application enters the **PRD refinement stage**.
3. Continue chatting to refine the specification.
4. When the trajectory contains a **Generate App** button (`type":"button"` and `event":{"name":"generateApp"}` in `result.artifact.parts[].data.actions[]`), trigger application generation using `generate-app`.

Generation is required **only once** during the initial creation.

---

## Multi-Round Modification

After an application has already been generated:

* **Do not call `generate-app` again.**
* Continue using `chat` with the same `appId` and `conversationId`.

Normal chat messages modify the existing application.

---

## Publishing

Publishing is allowed **after the application has been generated at least once**.

Rules:

* Publishing does **not require another generation step**
* Publishing may happen anytime after the first generation
* Publishing must be followed by **status polling** (or use `--wait` flag)

Typical deployment flow:

```
publish → publish-status polling
```

Or use the `--wait` flag to auto-poll:

```
publish --wait
```

Stop polling when the status becomes:

* `SUCCESS`
* `FAILED`

---

# Application URLs

Medo provides two types of URLs during the lifecycle.

---

## Project Preview (Editor / Development)

After the application is created, the project can be accessed at:

```
https://www.medo.dev/projects/<app_id>
```

This URL can be shared with the user for:

* viewing the project
* editing the application
* previewing the generated result

The preview URL becomes available once an `appId` is created.

---

## Production Deployment URL

After publishing succeeds, the application is accessible at:

```
https://<app_id>.appmedo.com
```

This is the **public production URL** of the deployed application.

Only return this URL after publishing completes successfully.

---

# Standard Workflow

## Create New Application

```
chat → PRD refinement → generate-app → publish
```

---

## Modify Existing Generated Application

```
chat → chat → chat
```

(no additional generation step required)

---

## Deploy Application

```
publish → publish-status polling
```

Or:

```
publish --wait
```

---

# Available Commands

All commands are executed via the CLI script.

**Important**: Always set the `MEDO_API_KEY` environment variable before running commands.

```bash
export MEDO_API_KEY="your_api_key_here"
```

---

## list-apps

List all applications belonging to the authenticated user.

**Usage:**

```bash
python scripts/medo_api.py list-apps [--brief]
```

**Optional Parameters:**
- `--brief`: Output only key fields: `appId`, `name`, `type`, `appFocus`, `host`, `updatedAt`. Recommended for agents to reduce token usage.
- `--name NAME`: Filter by app name (substring)
- `--page PAGE`: Page number (default: 1)
- `--size SIZE`: Page size (default: 12)

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"

# Brief mode (recommended for agents)
python scripts/medo_api.py list-apps --brief

# Full mode
python scripts/medo_api.py list-apps
```

**Returns:** JSON array of applications with `appId`, `name`, `type`, etc.

---

## app-detail

Get detailed information about a specific application. **Automatically injects `conversationId`** into the response by default — no need to call `get-context-id` separately.

**Usage:**

```bash
python scripts/medo_api.py app-detail --app-id <app_id> [--no-context]
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID

**Optional Parameters:**
- `--no-context`: Skip auto-fetching `conversationId` from trajectory (faster, but response will not contain `conversationId`)

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py app-detail --app-id app-abc123xyz
```

**Returns:** JSON object with application details, configuration, and status. `data.conversationId` is automatically populated.

---

## get-context-id

Recover the `conversationId` for an existing app by reading its trajectory. Useful when the `conversationId` has been lost after a session reset.

**Usage:**

```bash
python scripts/medo_api.py get-context-id --app-id <app_id>
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID

**Optional Parameters:**
- `--fetch-timeout SECONDS`: Request timeout in seconds (default: 10)

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py get-context-id --app-id app-abc123xyz
```

**Returns:** `{"appId": "app-abc123xyz", "conversationId": "conv-def456uvw"}`

**Use Cases:**
- Need to modify a previously created app in a new session but `conversationId` is lost
- Use the returned `conversationId` with `chat --app-id --context-id` to resume modification

---

## conversation-history

Show a human/agent-readable summary of past interactions for an app. More convenient than `trajectory` or `fetch-trajectory` for quickly understanding what happened in previous sessions.

**Usage:**

```bash
python scripts/medo_api.py conversation-history --app-id <app_id> [options]
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID

**Optional Parameters:**
- `--full`: Show full content instead of truncated summaries (default: truncate at 200 chars)
- `--limit N`: Only show the last N conversation turns
- `--fetch-timeout SECONDS`: Request timeout in seconds (default: 10)

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"

# View conversation history summary
python scripts/medo_api.py conversation-history --app-id app-abc123xyz

# Only show the last 3 turns
python scripts/medo_api.py conversation-history --app-id app-abc123xyz --limit 3

# Show full content without truncation
python scripts/medo_api.py conversation-history --app-id app-abc123xyz --full
```

**Returns:** JSON Lines, one entry per meaningful turn:

```json
{"eventId": 5, "role": "user", "type": "message", "content": "创建一个待办事项应用..."}
{"eventId": 865, "role": "agent", "type": "file", "content": "[file: 需求文档.md]"}
{"eventId": 880, "role": "user", "type": "message", "content": "生成应用"}
```

**Use Cases:**
- Quickly understand what happened in previous sessions before resuming work
- Determine which phase the app is in (PRD refinement / generated / modified)
- Check for unfinished modifications or cancelled tasks

---

## chat

Start or continue a conversation to create or modify an application.

**Usage:**

```bash
python scripts/medo_api.py chat --text "description" [options]
```

**Required Parameters:**
- `--text TEXT`: The message/instruction to send

**Optional Parameters:**
- `--context-id CONTEXT_ID`: Conversation ID of an existing app.
- `--app-id APP_ID`: Application ID of an existing app.
- `--query-mode QUERY_MODE`: Query mode (default: deep_mode)
- `--input-field-type INPUT_FIELD_TYPE`: Input field type (default: web)
- `--poll-interval SECONDS`: Seconds between trajectory polls (default: 2.0)
- `--fetch-timeout SECONDS`: Per-request timeout for each trajectory fetch (default: 10)
- `--no-stream`: Return raw chat POST response without trajectory polling
- `--prompt-generate`: After polling, interactively ask whether to submit app generation if text was returned

> **⚠️ IMPORTANT — `--app-id` and `--context-id` must always be used together.**
>
> | Intent | `--app-id` | `--context-id` |
> |--------|-----------|----------------|
> | Create a brand-new app | omit | omit |
> | Continue / modify an existing app | required | required (conversationId) |
>
> Passing `--app-id` **without** `--context-id` will **NOT** modify the existing app.
> The platform will silently create a **new** app every time. The CLI will now raise an error in this case to prevent accidental app proliferation.

**Examples:**

**1. Create a new application:**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py chat --text "创建一个待办事项管理应用"
```

Response includes `appId` and `contextId` for subsequent calls.

**2. Continue conversation (refine PRD):**

```bash
python scripts/medo_api.py chat \
  --text "添加优先级标记功能" \
  --app-id app-abc123xyz \
  --context-id conv-def456uvw
```

**3. Modify existing generated app:**

```bash
python scripts/medo_api.py chat \
  --text "把按钮颜色改成蓝色" \
  --app-id app-abc123xyz \
  --context-id conv-def456uvw
```

**Important Notes:**
- Extract `appId` and `contextId` from the response and save them
- Use these IDs for all subsequent operations on the same app
- The first `chat` creates the app and starts PRD refinement
- After generation, `chat` directly modifies the app (no `generate-app` needed)

---

## trajectory

Poll trajectory events until the task reaches a terminal state.

**Usage:**

```bash
python scripts/medo_api.py trajectory --app-id <app_id> [options]
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID

**Optional Parameters:**
- `--last-event-id EVENT_ID`: Start eventId; -1 = all events from beginning (default: -1)
- `--poll-interval SECONDS`: Seconds between polls (default: 2.0)
- `--fetch-timeout SECONDS`: Per-request timeout in seconds (default: 10)
- `--sse`: Use legacy SSE streaming instead of polling

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py trajectory --app-id app-abc123xyz
```

**Use Cases:**
- Monitor conversation / generation progress
- Detect when PRD refinement is complete (look for Generate App button in `result.artifact.parts[].data.actions[]`)
- Verify generation has completed

---

## fetch-trajectory

Fetch one batch of trajectory events (single request, no polling loop).

**Usage:**

```bash
python scripts/medo_api.py fetch-trajectory --app-id <app_id> [options]
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID

**Optional Parameters:**
- `--last-event-id EVENT_ID`: Fetch events after this eventId; -1 = all (default: -1)
- `--fetch-timeout SECONDS`: Request timeout in seconds (default: 10)

**Example:**

```bash
# First call — get all events (note maxEventId from stderr)
python scripts/medo_api.py fetch-trajectory --app-id app-abc123xyz

# Subsequent calls — incremental fetch
python scripts/medo_api.py fetch-trajectory --app-id app-abc123xyz --last-event-id 345
```

Events are printed to stdout as JSON lines; `{"maxEventId": N, "isTerminal": bool}` is printed to stderr.

**Generate App readiness:** Inspect `result.artifact.parts[].data.actions[]` for an action with `"type":"button"` and `"event":{"name":"generateApp"}`. Example:

```json
{"type":"button","label":"Generate App","value":"Generate App","event":{"name":"generateApp"}}
```

When this button appears, PRD is ready and `generate-app` may be called.

---

## generate-app

Submit app-generation confirmation and return immediately with `appId`/`conversationId`.

**Usage:**

```bash
python scripts/medo_api.py generate-app --app-id <app_id> --context-id <context_id> [options]
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID

**Optional Parameters:**
- `--context-id CONTEXT_ID`: Conversation ID (default: "")
- `--query-mode QUERY_MODE`: Query mode (default: deep_mode)
- `--watch`: Block and poll trajectory until generation completes (default: return immediately)
- `--poll-interval SECONDS`: Seconds between polls when `--watch` is set (default: 2.0)
- `--fetch-timeout SECONDS`: Per-request timeout in seconds when `--watch` is set (default: 10)

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"
# Submit and return immediately — check status later with fetch-trajectory
python scripts/medo_api.py generate-app \
  --app-id app-abc123xyz \
  --context-id conv-def456uvw

# Submit and block until generation finishes
python scripts/medo_api.py generate-app \
  --app-id app-abc123xyz \
  --context-id conv-def456uvw \
  --watch
```

**Important:**
- Only call this **once** during initial creation
- Call **only** when trajectory contains a Generate App button in `result.artifact.parts[].data.actions[]`: an action with `"type":"button"` and `"event":{"name":"generateApp"}` (label may vary by locale; use event name for the check). This indicates PRD is ready.
- Do **not** call again for modifications after the first generation
- After this command, use `chat` to modify the generated app

---

## publish

Trigger deployment to production.

**Usage:**

```bash
python scripts/medo_api.py publish --app-id <app_id> [options]
```

**Required Parameters:**
- `--app-id APP_ID`: Application ID to publish

**Optional Parameters:**
- `--env ENV`: Target environment (default: PRODUCE)
- `--wait`: Auto-poll publish status until SUCCESS or FAILED

**Examples:**

**1. Publish and manually check status:**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py publish --app-id app-abc123xyz
```

Returns `releaseId` immediately. Then poll with `publish-status`.

**2. Publish and auto-wait for completion (recommended):**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py publish --app-id app-abc123xyz --wait
```

This polls automatically and exits when deployment succeeds or fails.

**Important:**
- Application must be generated at least once before publishing
- After successful publish, the app is live at: `https://<app_id>.appmedo.com`

---

## publish-status

Check the status of a deployment.

**Usage:**

```bash
python scripts/medo_api.py publish-status --release-id <release_id>
```

**Required Parameters:**
- `--release-id RELEASE_ID`: Release ID from `publish` command

**Example:**

```bash
export MEDO_API_KEY="sk_xxxxx"
python scripts/medo_api.py publish-status --release-id app_release_record-xyz789abc
```

**Returns:** JSON with status: `PROCESSING`, `RUNNING`, `SUCCESS`, or `FAILED`

**Usage Pattern:**

```bash
# Get release ID from publish
RELEASE_ID=$(python scripts/medo_api.py publish --app-id app-abc123xyz | jq -r '.releaseId')

# Poll status
while true; do
  STATUS=$(python scripts/medo_api.py publish-status --release-id $RELEASE_ID | jq -r '.status')
  echo "Status: $STATUS"
  if [[ "$STATUS" == "SUCCESS" || "$STATUS" == "FAILED" ]]; then
    break
  fi
  sleep 5
done
```

**Tip:** Use `publish --wait` to avoid manual polling.

---

# Complete Workflow Examples

## Example 1: Create and Deploy a New App

```bash
export MEDO_API_KEY="sk_xxxxx"
cd ~/.openclaw/skills/medo-app-builder

# Step 1: Create app via chat (returns appId + conversationId on first line)
FIRST=$(python scripts/medo_api.py chat --text "创建一个简单的计数器应用" | head -1)
APP_ID=$(echo $FIRST | jq -r '.appId')
CONTEXT_ID=$(echo $FIRST | jq -r '.conversationId')

# Step 2: Generate the app (returns immediately; use fetch-trajectory to check progress)
python scripts/medo_api.py generate-app \
  --app-id $APP_ID \
  --context-id $CONTEXT_ID

# Step 3: Poll until generation finishes
python scripts/medo_api.py trajectory --app-id $APP_ID

# Step 4: Publish (with auto-wait)
python scripts/medo_api.py publish --app-id $APP_ID --wait

# Done! App is live at:
echo "https://$APP_ID.appmedo.com"
```

---

## Example 2: Modify an Existing App

> **IMPORTANT — Always update `CONTEXT_ID` from each `chat` response.**
>
> Each `chat` call prints a JSON header line `{"appId": "...", "conversationId": "..."}`.
> The platform may return an updated `conversationId` in this response.
> **Always capture it and use it for the next `chat` call**, or the next round will create a brand-new app.

```bash
export MEDO_API_KEY="sk_xxxxx"
cd ~/.openclaw/skills/medo-app-builder

APP_ID="app-abc123xyz"

# Step 1: Get app detail — conversationId is auto-injected
DETAIL=$(python scripts/medo_api.py app-detail --app-id $APP_ID)
CONTEXT_ID=$(echo $DETAIL | jq -r '.data.conversationId')

# Abort early if conversationId is missing (app may have no history yet)
if [ -z "$CONTEXT_ID" ] || [ "$CONTEXT_ID" = "null" ]; then
  echo "Error: could not retrieve conversationId. Try: get-context-id --app-id $APP_ID"
  exit 1
fi

# Step 2 (optional): Review conversation history to understand previous work
python scripts/medo_api.py conversation-history --app-id $APP_ID

# Step 3a: First modification — capture the UPDATED conversationId from the response header
CHAT_RESULT=$(python scripts/medo_api.py chat \
  --text "把背景颜色改成深色模式" \
  --app-id $APP_ID \
  --context-id $CONTEXT_ID | head -1)
CONTEXT_ID=$(echo $CHAT_RESULT | jq -r '.conversationId')   # ← UPDATE for next round

# Step 3b: Second modification — uses the updated CONTEXT_ID
CHAT_RESULT=$(python scripts/medo_api.py chat \
  --text "添加暗黑模式切换按钮" \
  --app-id $APP_ID \
  --context-id $CONTEXT_ID | head -1)
CONTEXT_ID=$(echo $CHAT_RESULT | jq -r '.conversationId')   # ← UPDATE again

# Step 4: Re-publish
python scripts/medo_api.py publish --app-id $APP_ID --wait
```

---

# Command Semantics

## chat

Used to:

* create a new application
* refine PRD specifications
* modify an existing generated application

For a new application, `chat` creates the project and begins the PRD stage.

For an existing application, `chat` performs iterative modifications.

---

## trajectory

Streams conversation progress and system events.

Use this to determine:

* whether PRD generation is ongoing
* whether the app is ready for generation (see generate-app condition below)
* whether generation has completed

---

## generate-app

Triggers application generation.

Call **only** when trajectory contains a Generate App button in `result.artifact.parts[].data.actions[]`: an action with `"type":"button"` and `"event":{"name":"generateApp"}`. This indicates PRD is ready. Do **not** rely on text alone—the button structure is the authoritative signal.

Call **once** during initial creation. Do not call again for modifications.

---

## publish

Triggers application deployment.

Use `--wait` flag to auto-poll status (recommended).

---

## publish-status

Polls deployment progress until the release completes.

Not needed if using `publish --wait`.

---

# Error Handling

## IAM AccessKey Validation Failed

**Symptom:**

```
IAM access key validation failed.
```

**Cause:**

The configured `MEDO_API_KEY` is invalid or missing.

**Resolution:**

1. Go to the Medo official website:

   https://www.medo.dev

2. In the left navigation panel, apply for an available access key.

3. Set the key as the environment variable:

   ```bash
   export MEDO_API_KEY="sk_xxxxx"
   ```

4. Or create a `.env` file in the skill directory:

   ```bash
   echo "MEDO_API_KEY=sk_xxxxx" > ~/.openclaw/skills/medo-app-builder/.env
   ```

---

## NotOpenSSLWarning

**Symptom:**

```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+,
currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'
```

**Cause:**

macOS uses LibreSSL by default, but urllib3 v2 recommends OpenSSL.

**Impact:**

This is a **warning only**. API calls still work correctly.

**Resolution (optional):**

If you want to suppress the warning:

```bash
pip3 install 'urllib3<2'
```

Or ignore it - it doesn't affect functionality.

---

# Error Handling Guidance

Agents should handle the following situations:

* generation requested before the platform indicates readiness
* publish requested before generation has completed
* missing `appId` or `conversationId` (use `get-context-id` to recover a lost `conversationId`)
* interrupted trajectory stream
* failed deployment status
* incorrect or missing parameter values

If workflow state is unclear, inspect the trajectory or application detail before taking the next action.

**Pro Tips:**
- Always check command `--help` when unsure about parameters
- Use `--wait` flag with `publish` to simplify deployment
- Save `appId` and `contextId` from first `chat` response
- Only call `generate-app` once during initial creation
- After generation, use `chat` directly for modifications

**Application Sharing Rule (IMPORTANT)**

- You must share your application **only using the production deployment URL** (after it has been published). Do not share the editor (development) URL.

Production deployment URL format:

```
https://<app_id>.appmedo.com
```

- If the application has **not been published**, you must publish it before sharing with others.

Example publish command:

```
python scripts/medo_api.py publish --app-id <app_id> --wait
```

- The project editor URL (`https://www.medo.cn/projects/<app_id>`) is **visible only to yourself**. Other users cannot access your editor environment. Never use the editor URL for sharing with others.

Editor URL is for:
- your own development
- preview
- internal editing only

Editor URL must NOT be used for:
- external/public sharing
- distribution to others or end users
