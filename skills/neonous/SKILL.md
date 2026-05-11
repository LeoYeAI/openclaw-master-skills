---
name: neonous
description: Operate the Neonous AI agent platform — create agents, chat, manage tools, run workflows.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - NEONOUS_API_KEY
        - NEONOUS_URL
      bins:
        - curl
        - jq
      primaryEnv: NEONOUS_API_KEY
    emoji: "🧠"
    homepage: https://neonous-ai.com
---

# Neonous Skill

You can operate the **Neonous AI agent platform** on behalf of the user. Neonous lets users create, configure, and deploy AI agents through a web interface — with tools, MCP servers, workflows, templates, and more.

## When to Use API vs Web Interface

**Prefer suggesting the web interface** for complex or visual tasks:
- Creating/editing agents with detailed instructions → **Web UI** has a rich editor, AI-assisted instruction enhancement, and template gallery
- Building workflows → **Web UI** has a visual canvas editor (drag & drop)
- Browsing MCP catalog → **Web UI** has a searchable catalog with one-click install
- Managing MCP server environment variables → **Web UI** handles secrets securely
- Browsing community templates → **Web UI** has categories, previews, and one-click clone

**Use the API** for quick operations:
- Listing agents, tools, workflows (quick status checks)
- Chatting with an agent
- Executing a workflow
- Checking token balance
- Simple agent creation with known parameters
- Scripting and automation

The web interface is at `$NEONOUS_URL` — guide the user there for anything visual or complex.

## Authentication

All API requests require the user's API key:

```
-H "x-api-key: $NEONOUS_API_KEY"
```

Base URL: `$NEONOUS_URL` (e.g., `https://app.neonous-ai.com`).

### How to Get an API Key

Users generate API keys from the **Settings** page in Neonous. The key starts with `nn_` and is only shown once. If not set up yet:

1. Log in to Neonous at `$NEONOUS_URL`
2. Go to **Settings** > **API Keys**
3. Click **Create API Key**, give it a name
4. Copy the key (won't be shown again) and set it as `NEONOUS_API_KEY`

---

## Agents

### List Agents

```bash
curl -s "$NEONOUS_URL/custom/builder/agents" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.[]| {id, name, model, enabled}'
```

### Get Agent Details

```bash
curl -s "$NEONOUS_URL/custom/builder/agents/<AGENT_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

Returns full config including `instructions`, `predefined_tools`, `custom_tools`, `mcp_servers`.

### List Available Models

Always fetch models before creating an agent — do not hardcode model IDs:

```bash
curl -s "$NEONOUS_URL/custom/builder/agents/available-models" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.models[]| {id, provider, display_name, is_default}'
```

Use the model marked `is_default: true` unless the user requests a specific one.

### List Available Tools

```bash
curl -s "$NEONOUS_URL/custom/builder/agents/available-tools" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.tools[]| {id, name, description}'
```

Returns pre-defined tools that can be assigned to agents via `predefined_tools`.

### Create an Agent

For complex agents, recommend the web UI — it has AI-assisted generation and a template gallery. For simple agents via API:

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/agents" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Agent",
    "description": "A helpful assistant",
    "instructions": "You are a helpful assistant that...",
    "model": "<MODEL_ID from available-models>",
    "enabled": true,
    "predefined_tools": [],
    "custom_tools": [],
    "mcp_servers": []
  }' | jq .
```

### AI-Generate Agent Config

Let Neonous AI generate a full agent config from a name and description:

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/agents/generate" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Code Reviewer",
    "description": "Reviews pull requests and suggests improvements"
  }' | jq .
```

Returns a complete agent config (name, instructions, model, tools) ready to use with the create endpoint.

### AI-Enhance Instructions

Improve existing agent instructions with AI:

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/enhance-instructions" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"instructions": "You help with code"}' | jq '.enhanced'
```

### Update an Agent

```bash
curl -s -X PUT "$NEONOUS_URL/custom/builder/agents/<AGENT_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "instructions": "Updated instructions..."
  }' | jq .
```

Only include fields you want to change.

### Delete an Agent

```bash
curl -s -X DELETE "$NEONOUS_URL/custom/builder/agents/<AGENT_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Chat

### Chat with an Agent

Non-streaming generate endpoint — returns a complete JSON response:

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/chat/generate" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "x-agent-id: <AGENT_ID>" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello, what can you do?"}]}' | jq .
```

Response:
```json
{
  "response": "Hi! I can help you with...",
  "usage": { "inputTokens": 42, "outputTokens": 18, "totalTokens": 60 }
}
```

For multi-turn conversations, include the full message history:
```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/chat/generate" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "x-agent-id: <AGENT_ID>" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is 2+2?"},
      {"role": "assistant", "content": "4"},
      {"role": "user", "content": "Multiply that by 10"}
    ]
  }' | jq .
```

### List Chat Sessions

```bash
curl -s "$NEONOUS_URL/custom/builder/chat/sessions" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.sessions[]| {id, title, agentId, created_at}'
```

Filter by agent: append `?agentId=<AGENT_ID>`.

### Get Chat Session (with Messages)

```bash
curl -s "$NEONOUS_URL/custom/builder/chat/sessions/<SESSION_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Create a Chat Session

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/chat/sessions" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<AGENT_ID>", "title": "My Session"}' | jq .
```

### Delete a Chat Session

```bash
curl -s -X DELETE "$NEONOUS_URL/custom/builder/chat/sessions/<SESSION_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## MCP Servers

For adding MCP servers, recommend the **web UI** — it has a searchable catalog with one-click install and secure environment variable management.

### List MCP Servers

```bash
curl -s "$NEONOUS_URL/custom/builder/mcp" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.[]| {id, name, type, enabled}'
```

### Get MCP Server Details

```bash
curl -s "$NEONOUS_URL/custom/builder/mcp/<MCP_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### List Tools from an MCP Server

```bash
curl -s "$NEONOUS_URL/custom/builder/mcp/<MCP_ID>/tools" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.tools[]| {name, description}'
```

### Add an MCP Server (stdio)

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/mcp" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-mcp",
    "name": "My MCP Server",
    "description": "Provides extra tools",
    "config": {
      "connectionType": "stdio",
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "envVars": []
    }
  }' | jq .
```

### Add an MCP Server (http)

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/mcp" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-http-mcp",
    "name": "My HTTP MCP",
    "config": {
      "connectionType": "http",
      "url": "https://mcp.example.com/sse",
      "headers": {}
    }
  }' | jq .
```

### Delete an MCP Server

```bash
curl -s -X DELETE "$NEONOUS_URL/custom/builder/mcp/<MCP_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

Add `?force=true` to delete even if agents are using it.

### Test MCP Server Connection

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/mcp/<MCP_ID>/test" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Workflows

For building workflows, **always recommend the web UI** — it has a visual drag-and-drop canvas editor that's far easier than raw JSON.

### List Workflows

```bash
curl -s "$NEONOUS_URL/custom/builder/workflows" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.[]| {id, name, enabled}'
```

### Get Workflow Details

```bash
curl -s "$NEONOUS_URL/custom/builder/workflows/<WORKFLOW_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Execute a Workflow

```bash
curl -s -X POST "$NEONOUS_URL/custom/builder/workflows/<WORKFLOW_ID>/execute" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"key": "value"}}' | jq .
```

### List Workflow Runs

```bash
curl -s "$NEONOUS_URL/custom/builder/workflows/<WORKFLOW_ID>/runs?limit=10" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.runs[]| {id, status, created_at}'
```

### Get Workflow Run Details

```bash
curl -s "$NEONOUS_URL/custom/builder/workflows/runs/<RUN_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Get Workflow Run Logs

```bash
curl -s "$NEONOUS_URL/custom/builder/workflows/runs/<RUN_ID>/logs" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.logs'
```

---

## Templates & Community

### List Agent Templates

```bash
curl -s "$NEONOUS_URL/custom/builder/templates" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.templates[]| {id, name, category}'
```

Filter by category: append `?category=<CATEGORY>`.

### Get Template Details

```bash
curl -s "$NEONOUS_URL/custom/builder/templates/<TEMPLATE_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Browse Community Templates

```bash
curl -s "$NEONOUS_URL/custom/builder/community-templates" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.templates[]| {id, name, category, author}'
```

For browsing and cloning templates, recommend the **web UI** — it has previews, categories, and one-click clone.

### Browse Community MCP Servers

```bash
curl -s "$NEONOUS_URL/custom/builder/community-mcp" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.[]| {id, name, categories}'
```

---

## Artifacts & Spaces

Agents generate **artifacts** during chat — code files, documents, charts, diagrams, and more. These are automatically saved and versioned. Users organize artifacts into **spaces** (project-based collections). For full artifact management, recommend the **web UI** — it has a file-manager interface with drag-and-drop, folders, and visual previews.

### Browse Artifacts

```bash
# List all artifacts
curl -s "$NEONOUS_URL/custom/builder/artifacts" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.[]| {id, title, type, created_at}'

# Get artifact details
curl -s "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Search artifacts
curl -s "$NEONOUS_URL/custom/builder/artifacts/search?q=<QUERY>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Quick search
curl -s "$NEONOUS_URL/custom/builder/artifacts/quick-search?q=<QUERY>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Recent / Starred / Trash
curl -s "$NEONOUS_URL/custom/builder/artifacts/recent" -H "x-api-key: $NEONOUS_API_KEY" | jq .
curl -s "$NEONOUS_URL/custom/builder/artifacts/starred" -H "x-api-key: $NEONOUS_API_KEY" | jq .
curl -s "$NEONOUS_URL/custom/builder/artifacts/trash" -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Stats and tags
curl -s "$NEONOUS_URL/custom/builder/artifacts/stats" -H "x-api-key: $NEONOUS_API_KEY" | jq .
curl -s "$NEONOUS_URL/custom/builder/artifacts/tags" -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Artifact Versions

```bash
# List versions
curl -s "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>/versions" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Restore a version
curl -s -X POST "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>/versions/<VERSION>/restore" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Folders

```bash
# Create folder
curl -s -X POST "$NEONOUS_URL/custom/builder/artifacts/folders" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Folder"}' | jq .

# Get folder contents
curl -s "$NEONOUS_URL/custom/builder/artifacts/folders/<FOLDER_ID>/contents" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Move artifacts to folder
curl -s -X POST "$NEONOUS_URL/custom/builder/artifacts/move" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"artifactIds": ["<ID1>", "<ID2>"], "folderId": "<FOLDER_ID>"}' | jq .
```

### Sharing

```bash
# Share artifact (returns a public share link)
curl -s -X POST "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>/share" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Revoke share
curl -s -X DELETE "$NEONOUS_URL/custom/builder/artifacts/shares/<SHARE_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Other Artifact Operations

```bash
# Delete (moves to trash)
curl -s -X DELETE "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Restore from trash
curl -s -X POST "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>/restore" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Duplicate
curl -s -X POST "$NEONOUS_URL/custom/builder/artifacts/<ARTIFACT_ID>/duplicate" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Empty trash
curl -s -X DELETE "$NEONOUS_URL/custom/builder/artifacts/trash" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Spaces

Spaces group artifacts by project or topic. An artifact can belong to multiple spaces.

```bash
# List spaces
curl -s "$NEONOUS_URL/custom/builder/spaces" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq '.spaces[]| {id, name, description}'

# Get space (with its artifacts)
curl -s "$NEONOUS_URL/custom/builder/spaces/<SPACE_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Create space
curl -s -X POST "$NEONOUS_URL/custom/builder/spaces" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Artifacts for my project", "icon": "📁", "color": "#3B82F6"}' | jq .

# Update space
curl -s -X PUT "$NEONOUS_URL/custom/builder/spaces/<SPACE_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Renamed Space"}' | jq .

# Delete space
curl -s -X DELETE "$NEONOUS_URL/custom/builder/spaces/<SPACE_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Add artifact to space
curl -s -X POST "$NEONOUS_URL/custom/builder/spaces/<SPACE_ID>/artifacts" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"artifactId": "<ARTIFACT_ID>"}' | jq .

# Remove artifact from space
curl -s -X DELETE "$NEONOUS_URL/custom/builder/spaces/<SPACE_ID>/artifacts/<ARTIFACT_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Bookmarks

Save important messages from chat sessions.

```bash
# List bookmarks
curl -s "$NEONOUS_URL/custom/builder/bookmarks" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# List bookmark tags
curl -s "$NEONOUS_URL/custom/builder/bookmarks/tags" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get bookmarks for a session
curl -s "$NEONOUS_URL/custom/builder/bookmarks/session/<SESSION_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Create bookmark
curl -s -X POST "$NEONOUS_URL/custom/builder/bookmarks" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "<SESSION_ID>", "messageId": "<MSG_ID>", "tags": ["important"]}' | jq .

# Delete bookmark
curl -s -X DELETE "$NEONOUS_URL/custom/builder/bookmarks/<BOOKMARK_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Skills

Agent skills extend what agents can do.

```bash
# List skills
curl -s "$NEONOUS_URL/custom/builder/skills" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get skill details
curl -s "$NEONOUS_URL/custom/builder/skills/<SKILL_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Reminders & Notifications

Agents can set reminders that trigger notifications or AI-generated follow-ups.

```bash
# List reminders
curl -s "$NEONOUS_URL/custom/builder/reminders" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Create reminder (schedule is a cron expression)
curl -s -X POST "$NEONOUS_URL/custom/builder/reminders" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Check deployment",
    "message": "Verify the production deploy succeeded",
    "agentId": "<AGENT_ID>",
    "schedule": "0 9 * * *"
  }' | jq .

# Toggle reminder on/off
curl -s -X POST "$NEONOUS_URL/custom/builder/reminders/<REMINDER_ID>/toggle" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Delete reminder
curl -s -X DELETE "$NEONOUS_URL/custom/builder/reminders/<REMINDER_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# List notifications
curl -s "$NEONOUS_URL/custom/builder/notifications" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Unread count
curl -s "$NEONOUS_URL/custom/builder/notifications/unread-count" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Mark all notifications read
curl -s -X POST "$NEONOUS_URL/custom/builder/notifications/read-all" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Telegram

Connect agents to Telegram bots. For setup, recommend the **web UI** — it handles bot token configuration.

```bash
# List Telegram connections
curl -s "$NEONOUS_URL/custom/builder/telegram/connections" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Connect agent to Telegram
curl -s -X POST "$NEONOUS_URL/custom/builder/telegram/connect" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<AGENT_ID>", "botToken": "<TELEGRAM_BOT_TOKEN>"}' | jq .

# Disconnect
curl -s -X DELETE "$NEONOUS_URL/custom/builder/telegram/connections/<CONNECTION_ID>" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Working Memory

Agents remember context across conversations via working memory.

```bash
# Get working memory
curl -s "$NEONOUS_URL/custom/builder/users/working-memory" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Reset working memory
curl -s -X DELETE "$NEONOUS_URL/custom/builder/users/working-memory" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Wishlist

Users can submit and vote on feature wishes.

```bash
# List wishes
curl -s "$NEONOUS_URL/custom/builder/wishes" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Create wish
curl -s -X POST "$NEONOUS_URL/custom/builder/wishes" \
  -H "x-api-key: $NEONOUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Feature request", "description": "I would like..."}' | jq .

# Upvote/un-upvote
curl -s -X POST "$NEONOUS_URL/custom/builder/wishes/<WISH_ID>/upvote" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

---

## Account & Tokens

### Get Token Balance

```bash
curl -s "$NEONOUS_URL/tokens/balance" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Token Usage History

```bash
curl -s "$NEONOUS_URL/tokens/usage" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Monthly Usage Summary

```bash
curl -s "$NEONOUS_URL/tokens/summary" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

### Billing, Plans & Subscriptions

Subscribing, upgrading plans, and purchasing tokens all go through Stripe checkout in the browser. **Always direct users to the web UI** at `$NEONOUS_URL/settings` (or the billing/pricing page) to subscribe or buy tokens — these cannot be completed via API alone.

You can check the user's current plan and billing status via API:

```bash
# Get available plans (shows what they can subscribe to)
curl -s "$NEONOUS_URL/custom/builder/billing/plans" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get current subscription (shows active plan)
curl -s "$NEONOUS_URL/custom/builder/billing/subscription" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get billing status
curl -s "$NEONOUS_URL/custom/builder/billing/status" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get token pricing (for purchasing extra tokens)
curl -s "$NEONOUS_URL/custom/builder/billing/token-pricing" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get purchase history
curl -s "$NEONOUS_URL/custom/builder/billing/purchases" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .

# Get invoices
curl -s "$NEONOUS_URL/custom/builder/billing/invoices" \
  -H "x-api-key: $NEONOUS_API_KEY" | jq .
```

If the user wants to subscribe, upgrade, or buy tokens, tell them to visit the **Settings > Billing** page in the web UI.

### Health Check

```bash
curl -s "$NEONOUS_URL/custom/builder/health" | jq .
```

No authentication required.

---

## Guidelines

- **Always list agents first** before chatting, so you know valid agent IDs.
- **Fetch models before creating** — never hardcode model IDs; use `available-models` endpoint.
- **Recommend the web UI** for complex tasks: building workflows (canvas editor), browsing templates/MCP catalog, editing agent instructions (AI-enhanced editor), and managing secrets/env vars.
- **Use the API** for quick tasks: listing resources, chatting, executing workflows, checking balance.
- For multi-turn chat, keep the full message history and pass it in each request.
- Check token balance if you get a **402** error — the user is out of tokens.
- Show the agent's response text directly to the user; omit usage details unless asked.
- Format lists as clean tables or bullet points for readability.
