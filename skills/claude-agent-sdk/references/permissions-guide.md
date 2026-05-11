# Permissions Guide

Complete guide to permission control in Claude Agent SDK.

---

## Permission Modes

### Overview

Three built-in modes:

| Mode | Behavior | Use Case |
|------|----------|----------|
| `default` | Standard checks | General use, production |
| `acceptEdits` | Auto-approve file edits | Trusted refactoring |
| `bypassPermissions` | Skip ALL checks | CI/CD, sandboxed envs |

---

## Default Mode

Standard permission checks.

```typescript
options: {
  permissionMode: "default"
}
```

**Prompts user for**:
- File writes/edits
- Potentially dangerous bash commands
- Sensitive operations

**Auto-allows**:
- Read operations (Read, Grep, Glob)
- Safe bash commands

---

## Accept Edits Mode

Automatically approves file modifications.

```typescript
options: {
  permissionMode: "acceptEdits"
}
```

**Auto-approves**:
- File edits (Edit)
- File writes (Write)

**Still prompts for**:
- Dangerous bash commands
- Sensitive operations

**Use when**: Refactoring, code generation workflows

---

## Bypass Permissions Mode

⚠️ **DANGER**: Skips ALL permission checks.

```typescript
options: {
  permissionMode: "bypassPermissions"
}
```

**Auto-approves EVERYTHING**:
- All file operations
- All bash commands
- All tools

**ONLY use in**:
- CI/CD pipelines
- Sandboxed containers
- Docker environments
- Trusted, isolated contexts

**NEVER use in**:
- Production systems
- User-facing environments
- Untrusted inputs

---

## Custom Permission Logic

### canUseTool Callback

```typescript
type CanUseTool = (
  toolName: string,
  input: any
) => Promise<PermissionDecision>;

type PermissionDecision =
  | { behavior: "allow" }
  | { behavior: "deny"; message?: string }
  | { behavior: "ask"; message?: string };
```

### Basic Example

```typescript
options: {
  canUseTool: async (toolName, input) => {
    // Allow read-only
    if (['Read', 'Grep', 'Glob'].includes(toolName)) {
      return { behavior: "allow" };
    }

    // Deny dangerous bash
    if (toolName === 'Bash' && input.command.includes('rm -rf')) {
      return {
        behavior: "deny",
        message: "Destructive command blocked"
      };
    }

    // Ask for confirmation
    if (toolName === 'Write') {
      return {
        behavior: "ask",
        message: `Create ${input.file_path}?`
      };
    }

    return { behavior: "allow" };
  }
}
```

---

## Common Patterns

### Pattern 1: Block Destructive Commands

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === 'Bash') {
    const dangerous = [
      'rm -rf',
      'dd if=',
      'mkfs',
      '> /dev/',
      'shutdown',
      'reboot',
      'kill -9',
      'pkill'
    ];

    for (const pattern of dangerous) {
      if (input.command.includes(pattern)) {
        return {
          behavior: "deny",
          message: `Blocked dangerous command: ${pattern}`
        };
      }
    }
  }

  return { behavior: "allow" };
}
```

### Pattern 2: Protect Sensitive Files

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === 'Write' || toolName === 'Edit') {
    const sensitivePaths = [
      '/etc/',
      '/root/',
      '.env',
      'credentials',
      'secrets',
      'config/production',
      '.ssh/',
      'private_key'
    ];

    for (const path of sensitivePaths) {
      if (input.file_path?.includes(path)) {
        return {
          behavior: "ask",
          message: `⚠️  Modify sensitive file: ${input.file_path}?`
        };
      }
    }
  }

  return { behavior: "allow" };
}
```

### Pattern 3: Environment-Based Permissions

```typescript
const environment = process.env.NODE_ENV; // 'development' | 'staging' | 'production'

canUseTool: async (toolName, input) => {
  // Production: require approval for everything
  if (environment === 'production') {
    if (toolName === 'Bash' || toolName === 'Write' || toolName === 'Edit') {
      return {
        behavior: "ask",
        message: `PRODUCTION: Approve ${toolName}?`
      };
    }
  }

  // Staging: auto-approve edits
  if (environment === 'staging') {
    if (toolName === 'Write' || toolName === 'Edit') {
      return { behavior: "allow" };
    }
  }

  // Development: allow most things
  if (environment === 'development') {
    return { behavior: "allow" };
  }

  return { behavior: "allow" };
}
```

### Pattern 4: Deployment Confirmation

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === 'Bash') {
    const deploymentPatterns = [
      'deploy',
      'kubectl apply',
      'terraform apply',
      'helm install',
      'docker push',
      'npm publish'
    ];

    for (const pattern of deploymentPatterns) {
      if (input.command.includes(pattern)) {
        return {
          behavior: "ask",
          message: `🚀 DEPLOYMENT: ${input.command}\n\nProceed?`
        };
      }
    }
  }

  return { behavior: "allow" };
}
```

### Pattern 5: Audit Logging

```typescript
const auditLog: Array<{
  tool: string;
  input: any;
  decision: string;
  timestamp: Date;
}> = [];

canUseTool: async (toolName, input) => {
  // Log everything
  console.log(`[${new Date().toISOString()}] ${toolName}`);

  const decision = { behavior: "allow" as const };

  // Store audit log
  auditLog.push({
    tool: toolName,
    input,
    decision: decision.behavior,
    timestamp: new Date()
  });

  // Could also send to external service
  // await logToDatadog(toolName, input, decision);

  return decision;
}
```

---

## Combining Modes with Custom Logic

```typescript
options: {
  permissionMode: "acceptEdits",  // Auto-approve file edits
  canUseTool: async (toolName, input) => {
    // But still block dangerous bash
    if (toolName === 'Bash' && input.command.includes('rm -rf')) {
      return { behavior: "deny", message: "Blocked" };
    }

    // Custom logic runs AFTER permission mode
    return { behavior: "allow" };
  }
}
```

---

## Security Best Practices

### ✅ Do

- Start with `"default"` mode
- Use `canUseTool` for fine-grained control
- Block known dangerous patterns
- Require confirmation for sensitive ops
- Log all tool usage for auditing
- Test permission logic thoroughly
- Use environment-based rules
- Implement rate limiting if needed

### ❌ Don't

- Use `"bypassPermissions"` in production
- Skip permission checks for "trusted" inputs
- Allow arbitrary bash without filtering
- Trust file paths without validation
- Ignore audit logging
- Assume AI won't make mistakes
- Give blanket approvals

---

## Testing Permissions

```typescript
async function testPermissions() {
  const tests = [
    { tool: "Read", input: { file_path: "/etc/passwd" }, expectAllow: true },
    { tool: "Bash", input: { command: "rm -rf /" }, expectDeny: true },
    { tool: "Write", input: { file_path: ".env" }, expectAsk: true }
  ];

  for (const test of tests) {
    const decision = await canUseTool(test.tool, test.input);

    if (test.expectAllow && decision.behavior !== 'allow') {
      console.error(`FAIL: Expected allow for ${test.tool}`);
    }
    if (test.expectDeny && decision.behavior !== 'deny') {
      console.error(`FAIL: Expected deny for ${test.tool}`);
    }
    if (test.expectAsk && decision.behavior !== 'ask') {
      console.error(`FAIL: Expected ask for ${test.tool}`);
    }
  }
}
```

---

## Common Scenarios

### Allow Read-Only

```typescript
canUseTool: async (toolName, input) => {
  if (['Read', 'Grep', 'Glob'].includes(toolName)) {
    return { behavior: "allow" };
  }
  return {
    behavior: "deny",
    message: "Read-only mode"
  };
}
```

### Require Approval for All

```typescript
canUseTool: async (toolName, input) => {
  return {
    behavior: "ask",
    message: `Approve ${toolName}?`
  };
}
```

### Block Bash Entirely

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === 'Bash') {
    return {
      behavior: "deny",
      message: "Bash execution disabled"
    };
  }
  return { behavior: "allow" };
}
```

---

## Error Handling

Handle permission errors gracefully:

```typescript
for await (const message of response) {
  if (message.type === 'error') {
    if (message.error.type === 'permission_denied') {
      console.log('Permission denied for:', message.error.tool);
      // Continue with fallback or skip
    }
  }
}
```

---

**For more details**: See SKILL.md
**Template**: templates/permission-control.ts
