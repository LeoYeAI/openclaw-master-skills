# AI Agent Integrations

> **User Action Required.** Each integration below
> requires manual setup outside this skill. This skill
> does not install packages or run code.

MoltFlow works as a tool provider for AI assistants.
Connect your preferred AI platform to the MoltFlow API
and manage WhatsApp directly from conversation.

## Claude Desktop (Native MCP)

25 MCP tools for sessions, messaging, groups, leads,
outreach, usage, and analytics. No npm package or
Node.js required -- connects directly to the MoltFlow
API via Streamable HTTP.

### Option A: OAuth (Recommended) -- No API Key Needed

Just add the URL. You'll be prompted to sign in the
first time you use a tool.

**Add to `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "moltflow": {
      "url": "https://apiv2.waiflow.app/mcp"
    }
  }
}
```

On first use, Claude will prompt you to authorize.
Click through to sign in (or create a free account)
and approve access. That's it -- no API key to copy.

### Option B: API Key (Manual)

If you prefer explicit key management:

```json
{
  "mcpServers": {
    "moltflow": {
      "url": "https://apiv2.waiflow.app/mcp",
      "headers": {
        "X-API-Key": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

**Required scopes:** Use the minimum scopes for your
workflow: `sessions:read`, `messages:send`, `leads:read`,
`custom-groups:read`, `usage:read`. Create a scoped key
at Dashboard > Sessions > API Keys tab.

**Setup guide:** [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow)

**Dashboard setup page:** [https://molt.waiflow.app/mcp](https://molt.waiflow.app/mcp)

## Claude.ai Web (Remote MCP)

No installation required -- configure in Claude.ai under
Settings > Integrations > MCP Servers:

- **URL:** `https://apiv2.waiflow.app/mcp`

OAuth handles authentication automatically. You'll be
prompted to sign in when you first use a MoltFlow tool.

Alternatively, use manual auth:
- **Auth header:** `X-API-Key`
- **Value:** Your scoped MoltFlow API key

All 25 tools are available immediately after configuration.

**Setup guide:** [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow)

## Claude Code

Add MoltFlow as a remote MCP server:

```bash
claude mcp add moltflow --transport http --url https://apiv2.waiflow.app/mcp
```

OAuth handles authentication automatically. On first
tool use you'll be prompted to sign in via your browser.

For manual auth with an API key:

```bash
claude mcp add moltflow --transport http --url https://apiv2.waiflow.app/mcp --header "X-API-Key: YOUR_API_KEY_HERE"
```

All 25 tools are available after adding the server.

**Setup guide:** [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow)

## ChatGPT (MCP Connector)

Add MoltFlow in ChatGPT settings under MCP Servers:

- **URL:** `https://apiv2.waiflow.app/mcp`

OAuth handles authentication. You'll sign in via your
browser on first use.

## OpenAI Custom GPTs

Import the MoltFlow OpenAPI specification in GPT Builder
to give your GPT access to messaging, sessions, leads,
and outreach endpoints.

**Setup guide:** [Connect ChatGPT to MoltFlow](https://molt.waiflow.app/guides/connect-chatgpt-to-moltflow)

Set Authentication to "API Key" with header `X-API-Key`
and paste your scoped MoltFlow API key.

---

## MCP Endpoint Details

- **URL:** `https://apiv2.waiflow.app/mcp`
- **Protocol:** MCP Streamable HTTP (2025-03-26)
- **Auth:** OAuth 2.1 (automatic) or `X-API-Key` header (manual)
- **OAuth discovery:** `https://apiv2.waiflow.app/.well-known/oauth-authorization-server`
- **Tools:** 25 tools across 7 categories (Sessions, Messaging, Groups, Leads, Outreach, Usage, Analytics)

---

## Security Notes

- **OAuth 2.1 with PKCE** -- the recommended auth method.
  Uses S256 code challenge, no client secrets exposed.
- **Scoped API keys** -- if using manual auth, create a
  key with minimum required scopes at Dashboard >
  Sessions > API Keys tab.
- **Environment variables** -- store API keys as env vars,
  not in shared config files. Rotate regularly.
- **GDPR compliance** -- all data processing follows
  GDPR guidelines with appropriate consent gates.

---

## A2A Discovery (ERC-8004)

MoltFlow is registered as [Agent #25477](https://8004agents.ai/ethereum/agent/25477) on Ethereum mainnet.

Other AI agents can discover MoltFlow through:

- **On-chain**: Query ERC-8004 Identity Registry at `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- **HTTP**: Fetch `https://apiv2.waiflow.app/.well-known/agent.json`
- **Agent card**: `https://molt.waiflow.app/.well-known/erc8004-agent.json`
