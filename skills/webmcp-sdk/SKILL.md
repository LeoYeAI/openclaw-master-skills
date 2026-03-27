---
name: webmcp-sdk
description: Developer toolkit for building WebMCP-compliant tool servers. Implements the W3C WebMCP spec with tool registration, security middleware, rate limiting, audit logging, React hooks, and proxy relay. Use when you want a website or web service to expose structured tools that browser-based AI agents can discover and call.
---

# WebMCP SDK

A developer toolkit for implementing the [WebMCP specification](https://webmcp.dev) — a W3C-proposed standard that lets websites expose structured tools for browser agents. Drop this SDK into any Node.js or React project to make your site agent-accessible.

- **GitHub**: https://github.com/up2itnow0822/webmcp-sdk
- **npm**: `webmcp-sdk`

## Core Capabilities

- **Tool registration** — Declare tools with typed schemas that agents can discover via `/.well-known/mcp.json`
- **Security middleware** — Origin validation, CORS, CSP, and request signing
- **Rate limiting** — Per-agent and per-tool rate limits to protect backend services
- **Audit logging** — Structured logs of every tool call with caller identity and outcome
- **React hooks** — `useWebMCP` and related hooks for React apps that want to surface tools client-side
- **Proxy relay** — Route agent tool calls to internal services without exposing them directly

## Setup

```bash
npm install webmcp-sdk
```

## Express / Node.js Server

Expose tools from an existing Express app:

```typescript
import express from 'express';
import { WebMCPServer, tool, z } from 'webmcp-sdk';

const app = express();
const mcp = new WebMCPServer({ app });

// Register a tool
mcp.register(
  tool({
    name: 'search_products',
    description: 'Search the product catalog by keyword',
    input: z.object({
      query: z.string().describe('Search terms'),
      limit: z.number().optional().default(10),
    }),
    handler: async ({ query, limit }) => {
      const results = await db.products.search(query, limit);
      return { results };
    },
  })
);

app.listen(3000);
```

Agents can now discover tools at `GET /.well-known/mcp.json` and call them via `POST /mcp/tools/{name}`.

## React Hooks

Expose tools from a client-side React app:

```tsx
import { useWebMCP, defineTool } from 'webmcp-sdk/react';

const searchTool = defineTool({
  name: 'search_ui',
  description: 'Trigger a search in the current UI context',
  input: z.object({ query: z.string() }),
  handler: async ({ query }) => {
    setSearchQuery(query); // update React state
    return { triggered: true };
  },
});

function App() {
  useWebMCP({ tools: [searchTool] });
  // ...
}
```

## Security Middleware

Enable built-in security controls:

```typescript
const mcp = new WebMCPServer({
  app,
  security: {
    allowedOrigins: ['https://trusted-agent.example.com'],
    requireSignedRequests: true, // verify HMAC on each call
    csrfProtection: true,
  },
});
```

## Rate Limiting

Protect tools from excessive calls:

```typescript
const mcp = new WebMCPServer({
  app,
  rateLimit: {
    windowMs: 60_000,     // 1-minute window
    maxPerAgent: 30,      // 30 calls per agent per minute
    maxPerTool: 10,       // 10 calls per specific tool per minute
  },
});
```

## Audit Logging

Every tool call is logged with caller identity and outcome:

```typescript
const mcp = new WebMCPServer({
  app,
  audit: {
    enabled: true,
    logger: (event) => {
      // event: { tool, input, output, agentId, duration, status }
      console.log(JSON.stringify(event));
    },
  },
});
```

## Proxy Relay

Route agent requests to internal microservices without exposing them:

```typescript
import { proxyRelay } from 'webmcp-sdk';

// Forward tool calls matching a pattern to an internal service
mcp.use(
  proxyRelay({
    match: /^internal_/,
    target: 'http://internal-api:8080',
    rewritePath: (name) => `/tools/${name}`,
  })
);
```

## Discovery Endpoint

Once configured, agents discover available tools via the standard WebMCP manifest:

```
GET /.well-known/mcp.json
```

Response:

```json
{
  "schema_version": "1.0",
  "tools": [
    {
      "name": "search_products",
      "description": "Search the product catalog by keyword",
      "inputSchema": { ... }
    }
  ]
}
```

## Security Rules

1. **Restrict `allowedOrigins`** to known agent hosts in production.
2. **Enable `requireSignedRequests`** for any tool that writes data or accesses sensitive information.
3. **Set rate limits** before exposing tools publicly — agents can call rapidly.
4. **Review audit logs** regularly for unexpected callers or tool abuse.
5. **Do not expose internal service URLs** via tool descriptions or error messages.

## References

- GitHub: https://github.com/up2itnow0822/webmcp-sdk
- npm: https://www.npmjs.com/package/webmcp-sdk
- WebMCP specification: https://webmcp.dev
