# AdCP Protocol Details

Understanding MCP vs A2A protocols for AdCP integration.

**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Protocol Comparison**: https://docs.adcontextprotocol.org/docs/building/understanding/protocol-comparison  
**MCP Guide**: https://docs.adcontextprotocol.org/docs/building/integration/mcp-guide  
**A2A Guide**: https://docs.adcontextprotocol.org/docs/building/integration/a2a-guide

This guide explains how to use AdCP with different transport protocols. For the complete protocol specification, see the [official AdCP protocol documentation](https://docs.adcontextprotocol.org/docs/building/understanding/protocol-comparison).

## Overview

AdCP works over two transport protocols:
- **MCP (Model Context Protocol)** - For Claude and MCP-compatible AI assistants
- **A2A (Agent-to-Agent)** - For Google's agent ecosystem and complex workflows

**The tasks are identical** across both protocols - only the transport format differs.

## When to Use Which Protocol

### Use MCP When:
- Building for Claude or MCP-compatible clients
- Direct integration with AI assistants
- Simpler request/response workflows
- Working in Cursor, Cline, or other MCP hosts

### Use A2A When:
- Building for Google's agent ecosystem
- Complex multi-agent workflows
- Agent collaboration scenarios
- Need streaming responses with SSE

## Protocol Comparison

| Feature | MCP | A2A |
|---------|-----|-----|
| **Tasks** | Same 8 media buy tasks | Same 8 media buy tasks |
| **Request Format** | JSON-RPC tool calls | HTTP POST with JSON |
| **Response Format** | Unified status system | Same unified status |
| **Authentication** | Bearer token header | API key in request |
| **Transport** | WebSocket or SSE | HTTP with SSE streaming |
| **Artifacts** | N/A | Agent cards, proposals |

## MCP Integration

### Setup

```javascript
import { createMCPClient } from '@adcp/client';

const client = createMCPClient({
  url: 'https://agent.example.com/mcp',
  auth: {
    type: 'bearer',
    token: 'your-auth-token'
  }
});
```

### Making Requests

```javascript
// MCP tool call format
const result = await client.callTool({
  name: 'get_products',
  arguments: {
    brief: 'Display advertising for tech startup',
    brand_manifest: {
      url: 'https://startup.com'
    }
  }
});

// Response is the task result directly
console.log(result.products);
```

### Context Management

MCP sessions maintain context automatically:

```javascript
// Context is preserved across calls
await client.callTool({ name: 'get_products', arguments: {...} });
await client.callTool({ name: 'list_creative_formats', arguments: {...} });
await client.callTool({ name: 'create_media_buy', arguments: {...} });
```

## A2A Integration

### Setup

```javascript
import { createA2AClient } from '@adcp/client';

const client = createA2AClient({
  agentUrl: 'https://agent.example.com',
  agentId: 'sales-agent-001',
  auth: {
    apiKey: 'your-api-key'
  }
});
```

### Making Requests

```javascript
// A2A uses call_adcp_agent wrapper
const result = await client.executeTask({
  task: 'get_products',
  params: {
    brief: 'Display advertising for tech startup',
    brand_manifest: {
      url: 'https://startup.com'
    }
  }
});

// Response includes agent card and task result
console.log(result.agent_card);
console.log(result.task_result.products);
```

### Agent Cards

A2A agents expose metadata via agent cards:

```javascript
// Fetch agent card
const card = await client.getAgentCard();

console.log(card.name);                    // Agent name
console.log(card.description);             // Agent description
console.log(card.capabilities);            // Supported protocols
console.log(card.portfolio.publishers);    // Publisher portfolio
```

### Streaming Responses (SSE)

A2A supports streaming for long-running operations:

```javascript
const stream = await client.executeTaskStream({
  task: 'create_media_buy',
  params: {...}
});

for await (const event of stream) {
  if (event.type === 'status') {
    console.log(`Status: ${event.status}`);
  } else if (event.type === 'progress') {
    console.log(`Progress: ${event.percent}%`);
  } else if (event.type === 'complete') {
    console.log('Campaign created:', event.result);
  }
}
```

## Unified Status System

Both protocols use the same status system for task responses:

```typescript
{
  status: "completed" | "pending" | "failed";
  
  // If completed
  data?: {...};
  
  // If pending
  task_id?: string;
  estimated_completion?: string;
  
  // If failed
  error?: {
    code: string;
    message: string;
    field?: string;
  };
}
```

### Handling Pending Operations

```javascript
async function waitForCompletion(taskId, protocol) {
  let status = 'pending';
  
  while (status === 'pending') {
    await sleep(5000);  // Wait 5 seconds
    
    if (protocol === 'mcp') {
      const result = await mcpClient.callTool({
        name: 'get_task_status',
        arguments: { task_id: taskId }
      });
      status = result.status;
    } else {
      const result = await a2aClient.executeTask({
        task: 'get_task_status',
        params: { task_id: taskId }
      });
      status = result.task_result.status;
    }
  }
  
  return status;
}
```

## Authentication

### MCP Authentication

```javascript
// Bearer token in header
const client = createMCPClient({
  url: 'https://agent.example.com/mcp',
  auth: {
    type: 'bearer',
    token: 'your-auth-token'
  }
});

// JWT authentication
const client = createMCPClient({
  url: 'https://agent.example.com/mcp',
  auth: {
    type: 'jwt',
    token: 'your-jwt-token'
  }
});
```

### A2A Authentication

```javascript
// API key
const client = createA2AClient({
  agentUrl: 'https://agent.example.com',
  auth: {
    apiKey: 'your-api-key'
  }
});

// OAuth
const client = createA2AClient({
  agentUrl: 'https://agent.example.com',
  auth: {
    type: 'oauth',
    accessToken: 'your-access-token'
  }
});
```

## Error Handling

### MCP Errors

```javascript
try {
  const result = await mcpClient.callTool({
    name: 'create_media_buy',
    arguments: {...}
  });
} catch (error) {
  if (error.code === 'VALIDATION_ERROR') {
    console.error(`Validation error: ${error.message}`);
    console.error(`Field: ${error.field}`);
  } else if (error.code === 'UNAUTHORIZED') {
    console.error('Authentication failed');
  } else {
    console.error(`Error: ${error.message}`);
  }
}
```

### A2A Errors

```javascript
const result = await a2aClient.executeTask({
  task: 'create_media_buy',
  params: {...}
});

if (result.status === 'failed') {
  console.error(`Error: ${result.error.message}`);
  console.error(`Code: ${result.error.code}`);
  if (result.error.field) {
    console.error(`Field: ${result.error.field}`);
  }
}
```

## Best Practices

### 1. Start with Capabilities

Always call `get_adcp_capabilities` first, regardless of protocol:

```javascript
// MCP
const caps = await mcpClient.callTool({
  name: 'get_adcp_capabilities',
  arguments: {}
});

// A2A
const caps = await a2aClient.executeTask({
  task: 'get_adcp_capabilities',
  params: {}
});
```

### 2. Handle Async Operations

Both protocols support asynchronous operations. Design for pending states:

```javascript
const result = await client.createMediaBuy(...);

if (result.status === 'pending') {
  console.log('Awaiting approval...');
  // Poll or wait for webhook
} else if (result.status === 'completed') {
  console.log('Campaign created immediately');
}
```

### 3. Use Appropriate Protocol

- **MCP**: Simple AI assistant integrations
- **A2A**: Complex workflows, agent collaboration

### 4. Implement Retries

Both protocols benefit from retry logic:

```javascript
async function retryOperation(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000);  // Exponential backoff
    }
  }
}
```

## OpenClaw Integration

### Using AdCP with OpenClaw

OpenClaw agents can use either protocol seamlessly:

```javascript
// In OpenClaw skill
export async function publishAd(brief, brandUrl) {
  // Detect available protocol
  const protocol = detectProtocol();
  
  if (protocol === 'mcp') {
    return await publishViaMCP(brief, brandUrl);
  } else {
    return await publishViaA2A(brief, brandUrl);
  }
}

function detectProtocol() {
  // Check if MCP client is available
  if (typeof mcpClient !== 'undefined') {
    return 'mcp';
  }
  return 'a2a';
}
```

### Test Agent Access

Both protocols work with the test agent:

```javascript
// MCP endpoint
const mcpUrl = 'https://test-agent.adcontextprotocol.org/mcp';

// A2A endpoint
const a2aUrl = 'https://test-agent.adcontextprotocol.org';

// Auth token (same for both)
const authToken = '1v8tAhASaUYYp4odoQ1PnMpdqNaMiTrCRqYo9OJp6IQ';
```

## Summary

| Aspect | MCP | A2A |
|--------|-----|-----|
| **Use Case** | AI assistants | Agent workflows |
| **Complexity** | Simpler | More features |
| **Format** | JSON-RPC | HTTP + JSON |
| **Tasks** | Same 8 tasks | Same 8 tasks |
| **Auth** | Bearer token | API key |
| **Streaming** | Limited | Full SSE support |
| **Artifacts** | No | Yes (agent cards) |

**Key Takeaway**: The advertising functionality is identical. Choose based on your integration environment.

## Additional Resources

### Official AdCP Protocol Documentation
- **Protocol Comparison**: https://docs.adcontextprotocol.org/docs/building/understanding/protocol-comparison
- **MCP Integration Guide**: https://docs.adcontextprotocol.org/docs/building/integration/mcp-guide
- **A2A Integration Guide**: https://docs.adcontextprotocol.org/docs/building/integration/a2a-guide
- **Authentication Guide**: https://docs.adcontextprotocol.org/docs/building/integration/authentication
- **Main Documentation**: https://docs.adcontextprotocol.org
- **Complete Index**: https://docs.adcontextprotocol.org/llms.txt
