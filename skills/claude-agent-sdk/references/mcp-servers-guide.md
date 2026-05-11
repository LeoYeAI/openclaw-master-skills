# MCP Servers Guide

Complete guide to creating and using Model Context Protocol (MCP) servers with Claude Agent SDK.

---

## What Are MCP Servers?

MCP servers extend agent capabilities with custom tools. Think of them as plugins that give your agent new abilities.

**Use Cases**:
- Database access
- API integrations
- Custom calculations
- External service interactions
- File system operations

---

## Creating In-Process MCP Servers

### Basic Server

```typescript
import { createSdkMcpServer, tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const myServer = createSdkMcpServer({
  name: "my-service",
  version: "1.0.0",
  tools: [
    tool(
      "tool_name",
      "Tool description",
      { /* Zod schema */ },
      async (args) => {
        // Implementation
        return {
          content: [{ type: "text", text: "Result" }]
        };
      }
    )
  ]
});
```

### Tool Definition Pattern

```typescript
tool(
  name: string,           // Tool identifier
  description: string,    // What it does
  inputSchema: ZodSchema, // Input validation
  handler: Handler        // Implementation
)
```

---

## Zod Schemas

### Common Patterns

```typescript
import { z } from "zod";

// String
z.string()
z.string().email()
z.string().url()
z.string().min(5).max(100)
z.string().describe("Description for AI")

// Number
z.number()
z.number().int()
z.number().positive()
z.number().min(0).max(100)

// Boolean
z.boolean()
z.boolean().default(false)

// Enum
z.enum(["option1", "option2", "option3"])
z.union([z.literal("a"), z.literal("b")])

// Optional
z.string().optional()
z.number().default(10)

// Object
z.object({
  name: z.string(),
  age: z.number(),
  email: z.string().email().optional()
})

// Array
z.array(z.string())
z.array(z.number()).min(1).max(10)

// Complex nested
z.object({
  user: z.object({
    id: z.string().uuid(),
    name: z.string(),
    roles: z.array(z.enum(["admin", "user", "guest"]))
  }),
  metadata: z.record(z.any()).optional()
})
```

### Best Practices

```typescript
// ✅ Good: Clear descriptions
{
  location: z.string().describe("City name or coordinates (e.g., 'San Francisco, CA')"),
  radius: z.number().min(1).max(100).describe("Search radius in kilometers")
}

// ❌ Bad: No descriptions
{
  location: z.string(),
  radius: z.number()
}

// ✅ Good: Validation constraints
{
  email: z.string().email(),
  age: z.number().int().min(0).max(120),
  role: z.enum(["admin", "user", "guest"])
}

// ❌ Bad: No validation
{
  email: z.string(),
  age: z.number(),
  role: z.string()
}
```

---

## Handler Implementation

### Success Response

```typescript
async (args) => {
  const result = await performOperation(args);
  return {
    content: [{
      type: "text",
      text: JSON.stringify(result, null, 2)
    }]
  };
}
```

### Error Response

```typescript
async (args) => {
  try {
    const result = await riskyOperation(args);
    return {
      content: [{ type: "text", text: result }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error: ${error.message}`
      }],
      isError: true  // Mark as error
    };
  }
}
```

---

## Complete Examples

### Weather Service

```typescript
const weatherServer = createSdkMcpServer({
  name: "weather",
  version: "1.0.0",
  tools: [
    tool(
      "get_weather",
      "Get current weather for a location",
      {
        location: z.string().describe("City name"),
        units: z.enum(["celsius", "fahrenheit"]).default("celsius")
      },
      async (args) => {
        const response = await fetch(
          `https://api.weather.com/v1/current?location=${args.location}&units=${args.units}`
        );
        const data = await response.json();
        return {
          content: [{
            type: "text",
            text: `Temp: ${data.temp}° ${args.units}\nConditions: ${data.conditions}`
          }]
        };
      }
    ),
    tool(
      "get_forecast",
      "Get 7-day forecast",
      {
        location: z.string(),
        days: z.number().min(1).max(7).default(7)
      },
      async (args) => {
        const forecast = await fetchForecast(args.location, args.days);
        return {
          content: [{ type: "text", text: JSON.stringify(forecast, null, 2) }]
        };
      }
    )
  ]
});
```

### Database Service

```typescript
const databaseServer = createSdkMcpServer({
  name: "database",
  version: "1.0.0",
  tools: [
    tool(
      "query",
      "Execute SQL query",
      {
        sql: z.string().describe("SQL query to execute"),
        params: z.array(z.any()).optional().describe("Query parameters")
      },
      async (args) => {
        try {
          const results = await db.query(args.sql, args.params);
          return {
            content: [{ type: "text", text: JSON.stringify(results, null, 2) }]
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `SQL Error: ${error.message}` }],
            isError: true
          };
        }
      }
    )
  ]
});
```

---

## Using MCP Servers

### In Query Options

```typescript
const response = query({
  prompt: "What's the weather in NYC?",
  options: {
    mcpServers: {
      "weather": weatherServer,
      "database": databaseServer
    },
    allowedTools: [
      "mcp__weather__get_weather",
      "mcp__database__query"
    ]
  }
});
```

### Tool Naming Convention

**Format**: `mcp__<server-name>__<tool-name>`

Examples:
- `mcp__weather__get_weather`
- `mcp__database__query`
- `mcp__filesystem__read_file`

**CRITICAL**: Server and tool names must match exactly.

---

## External MCP Servers

### Stdio Servers

```typescript
options: {
  mcpServers: {
    "filesystem": {
      command: "npx",
      args: ["@modelcontextprotocol/server-filesystem"],
      env: {
        ALLOWED_PATHS: "/path/to/allowed/dir"
      }
    }
  }
}
```

### HTTP/SSE Servers

```typescript
options: {
  mcpServers: {
    "remote": {
      url: "https://api.example.com/mcp",
      headers: {
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
      }
    }
  }
}
```

---

## Best Practices

### ✅ Do

- Use clear tool names and descriptions
- Add `.describe()` to all Zod fields
- Implement error handling in handlers
- Validate inputs with Zod constraints
- Return clear, formatted responses
- Test tools independently before integration
- Use unique tool names across servers
- Version your servers

### ❌ Don't

- Use generic names like "process" or "run"
- Skip input validation
- Return raw error objects
- Forget `isError: true` on errors
- Use duplicate tool names
- Expose sensitive operations without checks
- Skip testing in isolation

---

## Troubleshooting

### Tool Not Found

**Problem**: `"Tool mcp__server__tool not found"`

**Solution**:
1. Check server name matches
2. Check tool name matches
3. Include in `allowedTools` array
4. Verify server added to `mcpServers`

### Tool Name Collision

**Problem**: Two tools with same name

**Solution**: Use unique names or prefix with server name

### Validation Errors

**Problem**: Invalid input to tool

**Solution**: Add descriptive Zod schemas with constraints

---

**For more details**: See SKILL.md
**Official MCP docs**: https://modelcontextprotocol.io/
