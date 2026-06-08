# OpenClaw Secrets Management Reference

## Table of Contents

- [Overview](#overview)
- [Runtime Model](#runtime-model)
- [SecretRef Contract](#secretref-contract)
- [Provider Config](#provider-config)
- [CLI Commands](#cli-commands)
- [Integration Examples](#integration-examples)
- [In-Scope Fields](#in-scope-fields)
- [Environment Variables](#environment-variables)
- [Env Var Substitution](#env-var-substitution)
- [Best Practices](#best-practices)

## Overview

OpenClaw supports external secret resolution to avoid plaintext credentials in config files. Secrets can come from environment variables, files, or external commands (1Password, Vault, sops).

## Runtime Model

- Resolution is **eager during activation**, not lazy
- Startup **fails fast** if any referenced credential cannot be resolved
- Reload uses **atomic swap**: full success or keep last-known-good
- Runtime requests read from the active in-memory snapshot

## SecretRef Contract

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

### source: "env"

Reads from environment variables.

```json5
{ source: "env", provider: "default", id: "OPENAI_API_KEY" }
```

- `provider` must match `^[a-z][a-z0-9_-]{0,63}$`
- `id` must match `^[A-Z][A-Z0-9_]{0,127}$`

### source: "file"

Reads from a JSON file managed by a file provider.

```json5
{ source: "file", provider: "filemain", id: "/providers/openai/apiKey" }
```

- `id` must be an absolute JSON pointer (`/...`)
- RFC6901 escaping: `~` → `~0`, `/` → `~1`

### source: "exec"

Runs a command to fetch the secret.

```json5
{ source: "exec", provider: "vault", id: "providers/openai/apiKey" }
```

- `id` must match `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`

## Provider Config

```json5
{
  secrets: {
    providers: {
      // Env provider (default, always available)
      default: { type: "env" },

      // File provider
      filemain: {
        type: "file",
        path: "~/.openclaw/secrets.json",
      },

      // Exec provider
      vault: {
        type: "exec",
        command: "op read op://MyVault/{id}",    // {id} is replaced
        timeoutMs: 10000,
        shell: true,
      },
    },
  },
}
```

### Exec Provider Examples

**1Password CLI:**
```json5
{
  secrets: {
    providers: {
      op: {
        type: "exec",
        command: "op read op://MyVault/{id}",
        shell: true,
      },
    },
  },
  models: {
    providers: {
      openai: {
        apiKey: { source: "exec", provider: "op", id: "OpenAI/credential" },
      },
    },
  },
}
```

**HashiCorp Vault CLI:**
```json5
{
  secrets: {
    providers: {
      vault: {
        type: "exec",
        command: "vault kv get -field=value secret/{id}",
        shell: true,
      },
    },
  },
}
```

**sops:**
```json5
{
  secrets: {
    providers: {
      sops: {
        type: "exec",
        command: "sops --decrypt --extract '[\"providers\"][\"openai\"][\"apiKey\"]' ~/.openclaw/secrets.enc.json",
        shell: true,
      },
    },
  },
}
```

## CLI Commands

```bash
openclaw secrets reload             # Re-resolve refs, swap runtime snapshot
openclaw secrets audit              # Scan for plaintext, unresolved refs
openclaw secrets configure          # Interactive setup + SecretRef mapping
openclaw secrets apply --from <f>   # Apply plan (--dry-run supported)
```

## Integration Examples

Full config with SecretRefs:

```json5
{
  models: {
    providers: {
      openai: {
        apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" },
      },
    },
  },
  channels: {
    telegram: {
      botToken: { source: "exec", provider: "op", id: "Telegram/BotToken" },
    },
    googlechat: {
      serviceAccountRef: { source: "exec", provider: "vault", id: "channels/googlechat/serviceAccount" },
    },
  },
}
```

## In-Scope Fields

SecretRefs are supported in:

**~/.openclaw/openclaw.json:**
- `models.providers.<provider>.apiKey`
- `channels.<channel>.botToken` / `token`
- `channels.<channel>.signingSecret`
- `channels.<channel>.appToken`
- `gateway.auth.token` / `password`
- Skill API keys

**~/.openclaw/agents/<agentId>/agent/auth-profiles.json**

## Environment Variables

### .env Files

OpenClaw loads env from (in order):
1. `.env` from current working directory (if present)
2. `~/.openclaw/.env` (global fallback)

### Inline Env Vars in Config

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
  },
}
```

### Shell Env Import

```json5
{
  env: {
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

Or `OPENCLAW_LOAD_SHELL_ENV=1`.

## Env Var Substitution

Use `${VAR_NAME}` in config values:

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
  models: {
    providers: {
      custom: { apiKey: "${CUSTOM_API_KEY}" },
    },
  },
}
```

Rules:
- Only uppercase names matched: `[A-Z_][A-Z0-9_]*`
- Missing/empty vars throw error at load time
- Escape with `$${VAR}` for literal output
- Works inside `$include` files
- Inline: `"${BASE}/v1"` → `"https://api.example.com/v1"`

## Best Practices

1. **Never store plaintext API keys** in `openclaw.json` — use SecretRefs or env vars
2. **Run `openclaw secrets audit`** regularly to scan for plaintext leaks
3. **Use `openclaw secrets configure`** for interactive setup
4. **Prefer `source: "env"`** for simplicity, `source: "exec"` for vault integration
5. **File permissions**: `chmod 600 ~/.openclaw/secrets.json`
6. **Rotate secrets** immediately if you suspect compromise
