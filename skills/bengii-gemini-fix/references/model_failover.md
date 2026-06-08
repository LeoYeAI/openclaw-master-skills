# Model Failover & OAuth

> Sources:
> - https://docs.openclaw.ai/concepts/model-failover
> - https://docs.openclaw.ai/concepts/oauth

## Auth Storage (Keys + OAuth)

- Secrets live in `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (legacy: `~/.openclaw/agent/auth-profiles.json`).
- Config `auth.profiles` / `auth.order` are metadata + routing only (no secrets).
- Legacy import-only OAuth file: `~/.openclaw/credentials/oauth.json` (imported into `auth-profiles.json` on first use).

### Profile Types

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }` (+ `projectId`/`enterpriseUrl` for some providers)

### Profile IDs

- Default: `provider:default` when no email is available.
- OAuth with email: `provider:<email>` (e.g. `google-antigravity:user@gmail.com`).

## Rotation Order

1. Explicit config: `auth.order[provider]` (if set).
2. Configured profiles: `auth.profiles` filtered by provider.
3. Stored profiles: entries in `auth-profiles.json` for the provider.

- Primary key: profile type (OAuth before API keys).
- Secondary key: `usageStats.lastUsed` (oldest first, within each type).
- Cooldown/disabled profiles are moved to the end, ordered by soonest expiry.

### Session Stickiness (Cache-Friendly)

- Auth profile is pinned for the duration of a session when possible to improve cache hit rates.

## Cooldowns

- Error-based backoff: 1 min → 5 min → 25 min → 1 hour (cap).
- Tracked in `auth-profiles.json` under `usageStats`:

```json
{
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2
    }
  }
}
```

## Billing Disables

- Billing backoff starts at 5 hours, doubles per billing failure, and caps at 24 hours.
- Backoff counters reset if the profile hasn't failed for 24 hours (configurable).

## Model Fallback

- Primary: `agents.defaults.model.primary`
- Fallbacks: `agents.defaults.model.fallbacks` (tried in order when primary fails)

## Related Config

| Config Path | Purpose |
|---|---|
| `auth.profiles` / `auth.order` | Profile metadata + routing |
| `auth.cooldowns.billingBackoffHours` | Initial backoff |
| `auth.cooldowns.billingBackoffHoursByProvider` | Per-provider overrides |
| `auth.cooldowns.billingMaxHours` | Max billing backoff |
| `auth.cooldowns.failureWindowHours` | Reset window |
| `agents.defaults.model.primary` / `fallbacks` | Model selection |
| `agents.defaults.imageModel` | Image model routing |

---

## OAuth

### Anthropic Setup-Token (Subscription Auth)

- `openclaw models auth add` → select Anthropic → paste setup token.
- The Gateway exchanges the setup token for an OAuth access + refresh token pair.

### OpenAI Codex (ChatGPT OAuth)

- `openclaw models auth add` → select OpenAI → browser-based OAuth flow.

### Refresh + Expiry

- OAuth tokens are auto-refreshed before expiry.
- Refresh failures trigger cooldown (like API errors).

### Multiple Accounts (Profiles + Routing)

1. Preferred: separate agents with different profiles.
2. Advanced: multiple profiles in one agent (use `auth.order` to control rotation).
