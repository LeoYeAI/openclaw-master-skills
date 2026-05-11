---
paths: "**/*agent*.ts", "**/*.ts"
---

# Claude Agent SDK Corrections

This uses **@anthropic-ai/claude-agent-sdk v0.1.50**.

## MCP Tool Naming Convention

```typescript
/* ❌ Wrong naming */
const tool = 'mcp_server_tool'

/* ✅ Double underscores required */
const tool = 'mcp__server-name__tool-name'
// Format: mcp__<server-name>__<tool-name>
```

## No Default System Prompt

```typescript
/* ❌ Assuming default instructions */
const agent = new Agent({
  model: 'claude-sonnet-4-5-20250929',
  // No system prompt...
})

/* ✅ Always provide custom system instruction */
const agent = new Agent({
  model: 'claude-sonnet-4-5-20250929',
  system: 'You are a helpful assistant that...',
})
```

## Permission Control

```typescript
/* ✅ Implement canUseTool for security */
const agent = new Agent({
  model: 'claude-sonnet-4-5-20250929',
  canUseTool: async (tool) => {
    if (tool.name.startsWith('dangerous_')) return 'deny'
    if (tool.name === 'file_write') return 'ask'
    return 'allow'
  },
})

// Permission modes:
// 'default' - Normal permissions
// 'acceptEdits' - Auto-accept file edits
// 'bypassPermissions' - CI/CD only!
// 'plan' - Planning mode
```

## Session Forking (Unique Feature)

```typescript
/* ✅ Create branch without modifying original */
const forkedSession = await session.fork()
// Original session unchanged
// Forked session can diverge
```

## Subagent Definitions

```typescript
/* ❌ Missing required fields */
const subagent = { prompt: 'Do task' }

/* ✅ Include description and prompt */
const subagent = {
  description: 'Handles data processing tasks',
  prompt: 'Process the provided data and return results',
}
```

## Settings Priority

```
Highest → Lowest:
1. Programmatic (code)
2. Local (.claude/settings.local.json)
3. Project (.claude/settings.json)
4. User (~/.claude/settings.json)
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `mcp_server_tool` | `mcp__server__tool` (double underscores) |
| No system prompt | Always provide `system` instruction |
| Missing canUseTool | Implement permission control |
| Subagent without description | Include `description` and `prompt` |
| Tool timeout issues | >5 minutes raises error, handle long tasks |
