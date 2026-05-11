---
name: security-input-validator
description: "Validates user prompts for security threats before submission to AI agents"
metadata:
  openclaw:
    emoji: "🛡️"
    events: ["command:new"]
---

# Security Input Validator

Validates user input before it's submitted to AI agents, protecting against:
- Prompt injection attempts
- Command injection patterns
- Malicious URLs and SSRF attacks
- Path traversal attempts
- Secret exposure
- Obfuscation and policy violations

## How It Works

This hook intercepts user prompts at the `command:new` event and performs comprehensive security validation using the OpenClaw Security Engine. If threats are detected, the hook will:

- **ALLOW**: Let safe input through
- **WARN**: Show a warning but allow (low/medium severity)
- **BLOCK**: Reject the request (high/critical severity)

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
    prompt_injection:
      enabled: true
    command_validator:
      enabled: true
    url_validator:
      enabled: true
    path_validator:
      enabled: true
    secret_detector:
      enabled: true
    content_scanner:
      enabled: true

  actions:
    SAFE: allow
    LOW: log
    MEDIUM: warn
    HIGH: block
    CRITICAL: block_notify
```

## Security Events

All validations are logged to the security database for audit and analytics:

```bash
# View recent events
openclaw-sec events --limit 50

# View events for specific user
openclaw-sec events --user-id "alice@example.com"

# View blocked events
openclaw-sec events --action BLOCK
```

## Performance

- **Validation Time**: ~20-50ms per check
- **Async Writes**: Database writes don't block validation
- **Parallel Scanning**: All modules run concurrently
- **Minimal Overhead**: Negligible impact on user experience

## Error Handling

The hook fails-open by default, meaning if an error occurs during validation, the input will be allowed through to prevent breaking the workflow. All errors are logged for troubleshooting.
