# MCP Server Paywall

Protect Model Context Protocol (MCP) servers with Nevermined payments. The library handles MCP server creation, OAuth 2.1 endpoints, paywall protection, and credit billing.

## Installation

```bash
npm install @nevermined-io/payments zod
```

## Quick Start — Complete MCP Server

```typescript
import { Payments } from "@nevermined-io/payments"
import { z } from "zod"

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: "sandbox"
})

// Register tools with built-in paywall
payments.mcp.registerTool(
  "weather.today",
  {
    title: "Today's Weather",
    description: "Get weather for a city",
    inputSchema: z.object({
      city: z.string().min(2).max(80).describe("City name")
    })
  },
  async (args, extra, context) => {
    console.log(`Request ID: ${context?.authResult.requestId}`)
    console.log(`Credits charged: ${context?.credits}`)

    const weather = await fetchWeather(args.city)
    return {
      content: [{
        type: "text",
        text: `Weather in ${args.city}: ${weather.description}, ${weather.temp}°C`
      }]
    }
  },
  { credits: 5n }
)

// Start everything (MCP Server + Express + OAuth)
const { info, stop } = await payments.mcp.start({
  port: 3000,
  agentId: process.env.NVM_AGENT_ID!,
  serverName: "my-weather-server",
  version: "1.0.0",
  description: "Weather MCP server with OAuth authentication"
})

console.log(`Server running at ${info.baseUrl}/mcp`)

process.on("SIGINT", async () => {
  await stop()
  process.exit(0)
})
```

## What `payments.mcp.start()` Does

This single call handles:
1. **Express Server Setup** — creates and configures the Express.js application
2. **OAuth Endpoints** — auto-generates RFC-compliant discovery endpoints:
   - `/.well-known/oauth-authorization-server`
   - `/.well-known/oauth-protected-resource`
   - `/.well-known/openid-configuration`
   - `/register` (Dynamic Client Registration — RFC 7591)
3. **MCP Transport** — HTTP transport endpoints (POST/GET/DELETE `/mcp`)
4. **Session Management** — SSE streaming and session lifecycle
5. **CORS & Middleware** — CORS, JSON parsing, HTTP logging
6. **Graceful Shutdown** — returns a `stop()` function

## Dynamic Credits

Calculate credits based on the handler's result instead of using a fixed value:

```typescript
import type { CreditsContext } from "@nevermined-io/payments"

const dynamicCredits = (ctx: CreditsContext): bigint => {
  const result = ctx.result as { content: Array<{ text: string }> }
  const text = result.content[0]?.text || ""
  return BigInt(Math.ceil(text.length / 100))
}

payments.mcp.registerTool(
  "weather.today",
  config,
  handler,
  { credits: dynamicCredits }
)
```

- **Fixed credits** (`credits: 5n`): calculated BEFORE handler execution
- **Dynamic credits** (function): calculated AFTER handler execution, based on `ctx.result`

## Handler Options

| Option | Type | Description |
|--------|------|-------------|
| `credits` | `bigint` or `function` | Credits to consume per call |
| `planId` | `string` | Optional override for the plan ID (otherwise inferred from token) |
| `maxAmount` | `bigint` | Max credits to verify during authentication (default: `1n`) |
| `onRedeemError` | `string` | `'ignore'` (default) or `'propagate'` to throw on redemption failure |

## Response Metadata (`_meta`)

After each paywall-protected call, the SDK injects a `_meta` field into the response:

```typescript
// Successful redemption
{
  content: [{ type: 'text', text: 'result' }],
  _meta: {
    success: true,
    txHash: '0xabc...',
    creditsRedeemed: '5',
    remainingBalance: '95',
    planId: 'plan-123',
    subscriberAddress: '0x123...',
  }
}

// Failed redemption (onRedeemError: 'ignore')
{
  content: [{ type: 'text', text: 'result' }],
  _meta: {
    success: false,
    creditsRedeemed: '0',
    planId: 'plan-123',
    subscriberAddress: '0x123...',
    errorReason: 'Insufficient credits',
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | Whether credit redemption succeeded |
| `txHash` | `string` | Blockchain transaction hash (only on success) |
| `creditsRedeemed` | `string` | Number of credits burned (`'0'` on failure) |
| `remainingBalance` | `string` | Credits remaining after redemption |
| `planId` | `string` | Plan used for the operation |
| `subscriberAddress` | `string` | Subscriber's wallet address |
| `errorReason` | `string` | Error message (only on failure) |

## Client Usage

### Get Access Token

```typescript
const { accessToken } = await paymentsClient.x402.getX402AccessToken(planId, agentId)
```

### Connect with MCP Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client"
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp"

const transport = new StreamableHTTPClientTransport(
  new URL("http://localhost:3000/mcp"),
  {
    requestInit: {
      headers: { 'payment-signature': accessToken }
    }
  }
)

const client = new Client({ name: "my-client" })
await client.connect(transport)

const result = await client.callTool({
  name: "weather.today",
  arguments: { city: "Madrid" }
})
```

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:3000/mcp",
      "type": "http"
    }
  }
}
```

OAuth authentication is handled automatically by the server.

## Advanced: Low-Level APIs

### `withPaywall` for Custom Servers

```typescript
const protectedHandler = payments.mcp.withPaywall(
  myHandler,
  {
    kind: "tool",
    name: "my.tool",
    credits: 5n
  }
)
```

### `attach` for Declarative Registration

```typescript
const server = new McpServer({ name: "my-server", version: "1.0.0" })
const registrar = payments.mcp.attach(server)

registrar.registerTool(
  "weather.today",
  config,
  handler,
  { credits: 1n }
)
```

## MCP Error Codes

| Error Code | Description |
|---|---|
| `-32003` | Payment Required — no token, invalid token, or insufficient credits |
| `-32002` | Misconfiguration — server setup error |
| `-32603` | Internal Error — handler execution failed |

## Logical MCP URLs

Nevermined identifies protected methods by logical URL:
`mcp://<serverName>/<typeName>/<methodName>`

- `mcp://weather-mcp/tools/weather.today`
- `mcp://weather-mcp/resources/weather.ensureCity`
- `mcp://weather-mcp/meta/initialize`

For dynamic URIs, use placeholders: `mcp://weather-mcp/resources/weather.today?city={city}`

## Environment Variables

```bash
NVM_API_KEY=nvm:your-api-key
NVM_ENVIRONMENT=sandbox
NVM_AGENT_ID=your-agent-id
```

## Tutorial

Production-ready example: [github.com/nevermined-io/tutorials/tree/main/mcp-examples/weather-mcp](https://github.com/nevermined-io/tutorials/tree/main/mcp-examples/weather-mcp)
