# Query API Reference

Complete reference for the `query()` function - the primary interface for Claude Agent SDK.

---

## Function Signature

```typescript
function query(config: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): AsyncGenerator<SDKMessage, void>;
```

---

## Parameters

### prompt

**Type**: `string | AsyncIterable<SDKUserMessage>`
**Required**: Yes

The task or question for the agent.

```typescript
// Simple string prompt
query({ prompt: "Analyze the codebase" })

// Streaming prompt (advanced)
query({ prompt: streamingUserMessages() })
```

### options

**Type**: `Options`
**Required**: No

Configuration options for the query.

---

## Options Reference

### model

**Type**: `"sonnet" | "haiku" | "opus" | "claude-sonnet-4-5" | "inherit"`
**Default**: `"sonnet"`

Model to use for the agent.

```typescript
options: {
  model: "claude-sonnet-4-5"  // Specific version
  model: "haiku"               // Fast
  model: "opus"                // Maximum capability
  model: "inherit"             // Use parent model (subagents)
}
```

### workingDirectory

**Type**: `string`
**Default**: Current working directory

Directory where agent operates.

```typescript
options: {
  workingDirectory: "/path/to/project"
}
```

### systemPrompt

**Type**: `string | { type: 'preset', preset: 'claude_code' }`
**Default**: None

System prompt that defines agent behavior.

```typescript
// Custom prompt
options: {
  systemPrompt: "You are a security-focused code reviewer."
}

// Use CLAUDE.md from project
options: {
  systemPrompt: { type: 'preset', preset: 'claude_code' },
  settingSources: ["project"]  // Required to load CLAUDE.md
}
```

### allowedTools

**Type**: `string[]`
**Default**: All tools

Whitelist of tools agent can use.

```typescript
options: {
  allowedTools: ["Read", "Grep", "Glob"]  // Read-only
}
```

### disallowedTools

**Type**: `string[]`
**Default**: None

Blacklist of tools agent cannot use.

```typescript
options: {
  disallowedTools: ["Bash", "Write", "Edit"]  // No modifications
}
```

**Note**: If both specified, `allowedTools` wins.

### permissionMode

**Type**: `"default" | "acceptEdits" | "bypassPermissions"`
**Default**: `"default"`

Permission strategy.

```typescript
options: {
  permissionMode: "default"            // Standard checks
  permissionMode: "acceptEdits"        // Auto-approve edits
  permissionMode: "bypassPermissions"  // Skip all checks (caution!)
}
```

### canUseTool

**Type**: `(toolName: string, input: any) => Promise<PermissionDecision>`
**Default**: None

Custom permission logic.

```typescript
options: {
  canUseTool: async (toolName, input) => {
    if (toolName === 'Bash' && input.command.includes('rm -rf')) {
      return { behavior: "deny", message: "Blocked" };
    }
    return { behavior: "allow" };
  }
}
```

**PermissionDecision**:
- `{ behavior: "allow" }` - Allow execution
- `{ behavior: "deny", message?: string }` - Block execution
- `{ behavior: "ask", message?: string }` - Prompt user

### agents

**Type**: `Record<string, AgentDefinition>`
**Default**: None

Subagent definitions.

```typescript
options: {
  agents: {
    "test-runner": {
      description: "Run test suites",
      prompt: "You run tests. Fail if any test fails.",
      tools: ["Bash", "Read"],
      model: "haiku"
    }
  }
}
```

**AgentDefinition**:
- `description` (string, required) - When to use agent
- `prompt` (string, required) - Agent's system prompt
- `tools` (string[], optional) - Allowed tools
- `model` (string, optional) - Model override

### mcpServers

**Type**: `Record<string, McpServerConfig>`
**Default**: None

MCP server configurations.

```typescript
options: {
  mcpServers: {
    "custom-server": customServer,  // In-process
    "filesystem": {                 // External (stdio)
      command: "npx",
      args: ["@modelcontextprotocol/server-filesystem"]
    },
    "remote": {                     // External (HTTP)
      url: "https://api.example.com/mcp",
      headers: { "Authorization": "Bearer token" }
    }
  }
}
```

### settingSources

**Type**: `("user" | "project" | "local")[]`
**Default**: `[]` (no filesystem settings)

Filesystem settings to load.

```typescript
options: {
  settingSources: ["project"]                   // Project only (CI/CD)
  settingSources: ["user", "project", "local"]  // All sources
  settingSources: []                            // Isolated (no files)
}
```

**Files**:
- `user` = `~/.claude/settings.json`
- `project` = `.claude/settings.json`
- `local` = `.claude/settings.local.json`

**Priority**: Programmatic > Local > Project > User

### resume

**Type**: `string`
**Default**: None

Session ID to resume.

```typescript
options: {
  resume: "session-id-here"
}
```

### forkSession

**Type**: `boolean`
**Default**: `false`

Create new branch from resumed session.

```typescript
options: {
  resume: "session-id-here",
  forkSession: true  // New branch, original unchanged
}
```

---

## Return Value

**Type**: `AsyncGenerator<SDKMessage, void>`

Asynchronous generator yielding messages.

```typescript
const response = query({ prompt: "..." });

for await (const message of response) {
  // Process message
}
```

---

## Message Types

See full details in SKILL.md. Summary:

| Type | When | Data |
|------|------|------|
| `system` | Session events | `session_id`, `model`, `tools` |
| `assistant` | Agent response | `content` (string or blocks) |
| `tool_call` | Tool requested | `tool_name`, `input` |
| `tool_result` | Tool completed | `tool_name`, `result` |
| `error` | Error occurred | `error` object |

---

## Usage Patterns

### Basic Query

```typescript
const response = query({
  prompt: "Analyze code",
  options: { model: "sonnet" }
});

for await (const message of response) {
  if (message.type === 'assistant') {
    console.log(message.content);
  }
}
```

### With Tools

```typescript
const response = query({
  prompt: "Review and fix bugs",
  options: {
    model: "sonnet",
    allowedTools: ["Read", "Grep", "Edit"]
  }
});
```

### With Subagents

```typescript
const response = query({
  prompt: "Deploy to production",
  options: {
    agents: {
      "tester": { /* ... */ },
      "deployer": { /* ... */ }
    }
  }
});
```

### With Custom Tools

```typescript
const response = query({
  prompt: "Get weather and send notification",
  options: {
    mcpServers: { "weather": weatherServer },
    allowedTools: ["mcp__weather__get_weather"]
  }
});
```

### With Session Management

```typescript
// Start
let session = await startSession("Build API");

// Resume
await resumeSession(session, "Add auth");

// Fork
await forkSession(session, "Try GraphQL instead");
```

---

## Best Practices

### ✅ Do

- Set specific `allowedTools` for security
- Use `canUseTool` for fine-grained control
- Implement error handling for all queries
- Capture `session_id` for resuming
- Use `workingDirectory` for clarity
- Test MCP servers independently
- Monitor tool execution with `tool_call` messages

### ❌ Don't

- Use `bypassPermissions` in production (unless sandboxed)
- Ignore error messages
- Skip session ID capture if planning to resume
- Allow unrestricted Bash without `canUseTool`
- Load user settings in CI/CD
- Use duplicate tool names

---

## Error Handling

```typescript
try {
  const response = query({ prompt: "..." });
  for await (const message of response) {
    if (message.type === 'error') {
      console.error('Agent error:', message.error);
    }
  }
} catch (error) {
  if (error.code === 'CLI_NOT_FOUND') {
    console.error('Install Claude Code CLI');
  }
}
```

---

## TypeScript Types

```typescript
type Options = {
  model?: "sonnet" | "haiku" | "opus" | string;
  workingDirectory?: string;
  systemPrompt?: string | { type: 'preset', preset: 'claude_code' };
  allowedTools?: string[];
  disallowedTools?: string[];
  permissionMode?: "default" | "acceptEdits" | "bypassPermissions";
  canUseTool?: (toolName: string, input: any) => Promise<PermissionDecision>;
  agents?: Record<string, AgentDefinition>;
  mcpServers?: Record<string, McpServerConfig>;
  settingSources?: ("user" | "project" | "local")[];
  resume?: string;
  forkSession?: boolean;
};

type AgentDefinition = {
  description: string;
  prompt: string;
  tools?: string[];
  model?: "sonnet" | "opus" | "haiku" | "inherit";
};

type PermissionDecision =
  | { behavior: "allow" }
  | { behavior: "deny"; message?: string }
  | { behavior: "ask"; message?: string };
```

---

**For more details**: See SKILL.md
**Official docs**: https://docs.claude.com/en/api/agent-sdk/typescript
