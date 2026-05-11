---
name: security-tool-validator
description: "Validates tool call parameters before execution to prevent security threats"
metadata:
  openclaw:
    emoji: "🔒"
    events: ["agent:bootstrap"]
    plugin_api: "tool_result_persist"
---

# Security Tool Validator

Validates tool/function call parameters before execution, protecting against:
- Command injection in shell commands
- SSRF (Server-Side Request Forgery) in URL parameters
- Path traversal in file operations
- Malicious file content
- Unsafe parameter values

## How It Works

This hook uses OpenClaw's `tool_result_persist` plugin API to intercept tool calls before execution. It validates parameters for security-sensitive tools including:

### Protected Tools

- **bash**, **exec** - Command injection validation
- **read**, **write**, **edit** - Path traversal validation
- **web_fetch**, **curl**, **wget** - SSRF validation
- **Any tool with parameters containing**: `command`, `url`, `path`, `file`

### Actions

Based on the validation result, the hook will:

- **ALLOW**: Execute the tool call normally
- **WARN**: Execute but log the warning
- **BLOCK**: Prevent execution and show error message

## Configuration

The hook uses the OpenClaw Security configuration file:

**Config File Locations** (in priority order):
1. `./openclaw-sec.yaml` (current directory)
2. `~/.openclaw/security-config.yaml` (home directory)
3. Default configuration

### Example Configuration

```yaml
openclaw_security:
  enabled: true
  sensitivity: medium  # paranoid | strict | medium | permissive

  modules:
    command_validator:
      enabled: true
      sensitivity: strict
    url_validator:
      enabled: true
    path_validator:
      enabled: true
      sensitivity: paranoid
    content_scanner:
      enabled: true

  actions:
    SAFE: allow
    LOW: log
    MEDIUM: warn
    HIGH: block
    CRITICAL: block_notify
```

## Parameter Validation

The hook intelligently determines which parameters need validation based on:

1. **Tool Name**: Known security-sensitive tools (bash, read, write, etc.)
2. **Parameter Name**: Parameters with security-relevant names (command, url, path, file)
3. **Parameter Type**: String parameters that could contain malicious input

### Validation Examples

```typescript
// BLOCKED: Command injection
{
  toolName: "bash",
  parameters: [
    { name: "command", value: "ls && rm -rf /" }
  ]
}

// BLOCKED: Path traversal
{
  toolName: "read",
  parameters: [
    { name: "file_path", value: "../../../../etc/passwd" }
  ]
}

// BLOCKED: SSRF attempt
{
  toolName: "web_fetch",
  parameters: [
    { name: "url", value: "http://169.254.169.254/latest/meta-data/" }
  ]
}

// ALLOWED: Safe operation
{
  toolName: "bash",
  parameters: [
    { name: "command", value: "ls -la" }
  ]
}
```

## Security Events

All tool call validations are logged to the security database:

```bash
# View recent tool validations
openclaw-sec events --limit 50 --context hookType:security-tool-validator

# View blocked tool calls
openclaw-sec events --action BLOCK --context hookType:security-tool-validator

# View specific tool validations
openclaw-sec events --context toolName:bash
```

## Performance

- **Validation Time**: ~20-50ms per parameter
- **Selective Validation**: Only validates security-relevant parameters
- **Async Logging**: Database writes don't block execution
- **Parallel Scanning**: Multiple parameters validated concurrently

## Error Handling

The hook fails-open by default - if an error occurs during validation, the tool call will be allowed through to prevent breaking the workflow. All errors are logged for troubleshooting.

## Integration with Plugin API

This hook uses OpenClaw's `tool_result_persist` plugin API, which allows it to:

1. **Intercept** tool calls before execution
2. **Validate** parameters against security policies
3. **Block** or **allow** execution based on findings
4. **Persist** validation results for audit
5. **Modify** parameters if needed (future enhancement)
