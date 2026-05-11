# Top Errors & Solutions

Complete reference for common Claude Agent SDK errors and how to fix them.

---

## Error #1: CLI Not Found

### Error Message
```
"Claude Code CLI not installed"
```

### Why It Happens
The SDK requires Claude Code CLI to be installed globally, but it's not found in PATH.

### Solution
```bash
npm install -g @anthropic-ai/claude-code
```

Verify installation:
```bash
which claude-code
# Should output: /usr/local/bin/claude-code or similar
```

### Prevention
- Install CLI before using SDK
- Add to project setup documentation
- Check CLI availability in CI/CD

---

## Error #2: Authentication Failed

### Error Message
```
"Invalid API key"
"Authentication failed"
```

### Why It Happens
- ANTHROPIC_API_KEY environment variable not set
- API key is invalid or expired
- API key has wrong format

### Solution
```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify it's set
echo $ANTHROPIC_API_KEY
```

Get API key:
1. Visit https://console.anthropic.com/
2. Navigate to API Keys section
3. Create new key
4. Copy and save securely

### Prevention
- Use environment variables (never hardcode)
- Check key before running
- Add to .env.example template
- Document setup process

---

## Error #3: Permission Denied

### Error Message
```
"Tool use blocked"
"Permission denied for tool: Bash"
```

### Why It Happens
- Tool not in `allowedTools` array
- `permissionMode` is too restrictive
- Custom `canUseTool` callback denied execution

### Solution
```typescript
// Add tool to allowedTools
options: {
  allowedTools: ["Read", "Write", "Edit", "Bash"]  // Add needed tools
}

// Or use less restrictive permission mode
options: {
  permissionMode: "acceptEdits"  // Auto-approve edits
}

// Or check canUseTool logic
options: {
  canUseTool: async (toolName, input) => {
    console.log("Tool requested:", toolName);  // Debug
    return { behavior: "allow" };
  }
}
```

### Prevention
- Set appropriate `allowedTools` from start
- Test permission logic thoroughly
- Use `permissionMode: "bypassPermissions"` in CI/CD

---

## Error #4: Context Length Exceeded

### Error Message
```
"Prompt too long"
"Context length exceeded"
"Too many tokens"
```

### Why It Happens
- Input prompt exceeds model's context window (200k tokens)
- Long conversation without pruning
- Large files in context

### Solution
SDK auto-compacts context, but you can:

```typescript
// Fork session to start fresh from a point
const forked = query({
  prompt: "Continue with fresh context",
  options: {
    resume: sessionId,
    forkSession: true  // Start fresh
  }
});

// Or reduce context
options: {
  allowedTools: ["Read", "Grep"],  // Limit tools
  systemPrompt: "Keep responses concise."
}
```

### Prevention
- Use session forking for long tasks
- Keep prompts focused
- Don't load unnecessary files
- Monitor context usage

---

## Error #5: Tool Execution Timeout

### Error Message
```
"Tool did not respond"
"Tool execution timeout"
```

### Why It Happens
- Tool takes too long (>5 minutes default)
- Infinite loop in tool implementation
- Network timeout for external tools

### Solution

For custom tools:
```typescript
tool("long_task", "Description", schema, async (args) => {
  // Add timeout
  const timeout = 60000; // 1 minute
  const promise = performLongTask(args);
  const result = await Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), timeout)
    )
  ]);
  return { content: [{ type: "text", text: result }] };
})
```

For bash commands:
```typescript
// Add timeout to bash command
command: "timeout 60s long-running-command"
```

### Prevention
- Set reasonable timeouts
- Optimize tool implementations
- Use background jobs for long tasks
- Test tools independently

---

## Error #6: Session Not Found

### Error Message
```
"Invalid session ID"
"Session not found"
```

### Why It Happens
- Session ID is incorrect
- Session expired (old)
- Session from different CLI instance

### Solution
```typescript
// Ensure session ID captured correctly
let sessionId: string | undefined;
for await (const message of response) {
  if (message.type === 'system' && message.subtype === 'init') {
    sessionId = message.session_id;  // Capture here
    console.log("Session:", sessionId);  // Verify
  }
}

// Use correct session ID
query({
  prompt: "...",
  options: { resume: sessionId }  // Must match exactly
});
```

### Prevention
- Always capture session_id from system init
- Store session IDs reliably
- Don't rely on sessions lasting indefinitely
- Handle session errors gracefully

---

## Error #7: MCP Server Connection Failed

### Error Message
```
"Server connection error"
"MCP server not responding"
"Failed to connect to MCP server"
```

### Why It Happens
- Server command/URL incorrect
- Server crashed or not running
- Network issues (HTTP/SSE servers)
- Missing dependencies

### Solution

For stdio servers:
```typescript
// Verify command works independently
// Test: npx @modelcontextprotocol/server-filesystem
options: {
  mcpServers: {
    "filesystem": {
      command: "npx",  // Verify npx is available
      args: ["@modelcontextprotocol/server-filesystem"],
      env: {
        ALLOWED_PATHS: "/path"  // Verify path exists
      }
    }
  }
}
```

For HTTP servers:
```typescript
// Test URL separately
const testResponse = await fetch("https://api.example.com/mcp");
console.log(testResponse.status);  // Should be 200
```

### Prevention
- Test MCP servers independently before integration
- Verify command/URL works
- Add error handling for server failures
- Use health checks

---

## Error #8: Subagent Definition Error

### Error Message
```
"Invalid AgentDefinition"
"Agent configuration error"
```

### Why It Happens
- Missing required fields (`description` or `prompt`)
- Invalid `model` value
- Invalid `tools` array

### Solution
```typescript
agents: {
  "my-agent": {
    description: "Clear description of when to use",  // Required
    prompt: "Detailed system prompt",                  // Required
    tools: ["Read", "Write"],                          // Optional
    model: "sonnet"                                    // Optional
  }
}
```

### Prevention
- Always include `description` and `prompt`
- Use TypeScript types
- Test agent definitions
- Follow examples in templates

---

## Error #9: Settings File Not Found

### Error Message
```
"Cannot read settings"
"Settings file not found"
```

### Why It Happens
- `settingSources` includes non-existent file
- File path incorrect
- File permissions deny read

### Solution
```typescript
// Check file exists before loading
import fs from 'fs';

const projectSettingsPath = '.claude/settings.json';
const settingSources = [];

if (fs.existsSync(projectSettingsPath)) {
  settingSources.push('project');
}

options: {
  settingSources  // Only existing files
}
```

### Prevention
- Check file exists before including in sources
- Use empty array for isolated execution
- Handle missing files gracefully

---

## Error #10: Tool Name Collision

### Error Message
```
"Duplicate tool name"
"Tool already defined"
```

### Why It Happens
- Two MCP servers define same tool name
- Tool name conflicts with built-in tool

### Solution
```typescript
// Use unique tool names
const server1 = createSdkMcpServer({
  name: "service-a",
  tools: [
    tool("service_a_process", ...)  // Prefix with server name
  ]
});

const server2 = createSdkMcpServer({
  name: "service-b",
  tools: [
    tool("service_b_process", ...)  // Different name
  ]
});
```

### Prevention
- Use unique tool names
- Prefix tools with server name
- Test integration before deployment

---

## Error #11: Zod Schema Validation Error

### Error Message
```
"Invalid tool input"
"Schema validation failed"
```

### Why It Happens
- Agent provided data that doesn't match Zod schema
- Schema too restrictive
- Missing `.describe()` on fields

### Solution
```typescript
// Add descriptive schemas
{
  email: z.string().email().describe("User email address"),
  age: z.number().int().min(0).max(120).describe("Age in years"),
  role: z.enum(["admin", "user"]).describe("User role")
}

// Make fields optional if appropriate
{
  email: z.string().email(),
  phoneOptional: z.string().optional()  // Not required
}
```

### Prevention
- Use `.describe()` on all fields
- Add validation constraints
- Test with various inputs
- Make optional fields explicit

---

## Error #12: Filesystem Permission Denied

### Error Message
```
"Access denied"
"Cannot access path"
"EACCES: permission denied"
```

### Why It Happens
- Path outside `workingDirectory`
- No read/write permissions
- Protected system directory

### Solution
```typescript
// Set correct working directory
options: {
  workingDirectory: "/path/to/accessible/dir"
}

// Or fix permissions
// chmod +r file.txt  (add read)
// chmod +w file.txt  (add write)
```

### Prevention
- Set appropriate `workingDirectory`
- Verify file permissions
- Don't access system directories
- Use dedicated project directories

---

## General Error Handling Pattern

```typescript
try {
  const response = query({ prompt: "...", options: { ... } });

  for await (const message of response) {
    if (message.type === 'error') {
      console.error('Agent error:', message.error);
      // Handle non-fatal errors
    }
  }
} catch (error) {
  console.error('Fatal error:', error);

  // Handle specific errors
  switch (error.code) {
    case 'CLI_NOT_FOUND':
      console.error('Install: npm install -g @anthropic-ai/claude-code');
      break;
    case 'AUTHENTICATION_FAILED':
      console.error('Check ANTHROPIC_API_KEY');
      break;
    case 'RATE_LIMIT_EXCEEDED':
      console.error('Rate limited. Retry with backoff.');
      break;
    case 'CONTEXT_LENGTH_EXCEEDED':
      console.error('Reduce context or fork session');
      break;
    default:
      console.error('Unexpected error:', error);
  }
}
```

---

**For more details**: See SKILL.md
**Template**: templates/error-handling.ts
