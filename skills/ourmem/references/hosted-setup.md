# ourmem Hosted Setup Guide

API Base: `https://api.ourmem.ai`

The hosted version runs on ourmem's cloud infrastructure. No server to manage, no Docker, no storage buckets. You get an API key and start using it.

## Step 1: Create API Key

```bash
curl -sX POST https://api.ourmem.ai/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "my-workspace"}' | jq .
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "api_key": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active"
}
```

`api_key` is your credential for all subsequent requests. Save it somewhere safe.

A personal Space is created automatically with your tenant.

## Step 2: Install Plugin

Pick the platform the user is on.

### Claude Code

`[AGENT]` Set environment variables. Add to `~/.bashrc` or `~/.zshrc` for persistence:

```bash
export OMEM_API_URL="https://api.ourmem.ai"
export OMEM_API_KEY="YOUR_API_KEY"
```

Then install the plugin inside Claude Code:

```
/plugin marketplace add ourmem/omem
/plugin install ourmem@ourmem
```

**Immediately after install completes**, tell the user (before restarting):

> ourmem plugin installed. Next I need to restart Claude Code so the memory plugin loads and the hooks become active.

### OpenCode

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
export OMEM_API_KEY="YOUR_API_KEY"
```

### OpenClaw

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
          "apiKey": "YOUR_API_KEY"
        }
      }
    },
    "allow": ["ourmem"]
  }
}
```

### MCP Server (Cursor / VS Code / Claude Desktop)

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
        "OMEM_API_KEY": "YOUR_API_KEY",
        "OMEM_API_URL": "https://api.ourmem.ai"
      }
    }
  }
}
```

Replace `YOUR_API_KEY` with the actual key.

## Step 3: Configure

Replace `YOUR_API_KEY` in the config above with the actual key from Step 1.

Double-check the API URL is `https://api.ourmem.ai` (not localhost).

## Step 4: Restart

- **Claude Code**: restart the `claude` process
- **OpenCode**: restart the `opencode` process
- **OpenClaw**: restart the gateway
- **MCP clients**: restart the app

The plugin needs a fresh start to load. Wait about a minute, then send a test message.

## Step 5: Verify

```bash
# Health
curl -sf https://api.ourmem.ai/health && echo "OK"

# Auth
curl -sf -H "X-API-Key: YOUR_API_KEY" \
  "https://api.ourmem.ai/v1/memories?limit=1" && echo "Auth OK"

# Store a test memory
curl -sX POST https://api.ourmem.ai/v1/memories \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"content": "ourmem hosted setup complete", "tags": ["test"]}'

# Search it back
curl -s "https://api.ourmem.ai/v1/memories/search?q=hosted+setup&limit=1" \
  -H "X-API-Key: YOUR_API_KEY" | jq '.results[0].memory.content'
```

If all checks pass, return to the main SKILL.md and continue with Step 5 (handoff).
