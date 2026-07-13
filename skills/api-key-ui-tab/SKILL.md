---
name: apikeys-ui
description: "Vault-backed API Keys management for OpenClaw. Secure file-based secret storage with one-click migration from plaintext config, dynamic key discovery, vault key selector for skills, manual secret creation, and plugin-registered settings tab."
version: 3.0.0
author: OpenClaw Community
metadata: {"openclaw":{"emoji":"🔐","requires":{"openclaw":">=2026.1.0"},"category":"settings"}}
---

# Vault Enhancements w/ UI v3.0.0

Vault-backed API key management for the OpenClaw Control dashboard. Keys are stored in a secure file (`~/.openclaw/secrets.json`, mode 0600) and referenced via OpenClaw's built-in Secrets System. The AI agent never sees your keys.

## Status: ✅ Active

| Component | Status |
|-----------|--------|
| Vault File Storage | ✅ Working |
| Secret References (SecretRef) | ✅ Working |
| Dynamic Key Discovery | ✅ Working |
| One-Click Migration | ✅ Working |
| Plugin-Registered Tab | ✅ Working |
| Vault Status Banner | ✅ Working |
| Key Status Badges | ✅ Working |
| Vault-Only Keys Section | ✅ Working |
| Manual "+ Add Secret" Form | ✅ Working |
| Restart Notification Banner | ✅ Working |
| Skills Vault Key Selector | ✅ Working |
| Skills Inline Key Creation | ✅ Working |
| Auth Profiles Display | ✅ Working |

## Features

### 1. Vault-Backed Storage

Keys are stored in `~/.openclaw/secrets.json` (file permissions `0600`). When you save a key, the UI:

1. Writes the value to the vault file
2. Configures the file secret provider in `openclaw.json` (if not already present)
3. Replaces the plaintext config value with a `SecretRef` object
4. Shows a restart notification — user must restart gateway for changes to take effect

**Config before migration:**
```json
{
  "env": {
    "OPENAI_API_KEY": "sk-proj-abc123..."
  }
}
```

**Config after migration:**
```json
{
  "env": {
    "OPENAI_API_KEY": { "source": "file", "provider": "default", "id": "/OPENAI_API_KEY" }
  },
  "secrets": {
    "providers": {
      "default": { "source": "file", "path": "~/.openclaw/secrets.json", "mode": "json" }
    },
    "defaults": { "file": "default" }
  }
}
```

**Vault file (`~/.openclaw/secrets.json`):**
```json
{
  "OPENAI_API_KEY": "sk-proj-abc123..."
}
```

### 2. One-Click Migration

The "🔒 Migrate to Vault" button appears when plaintext keys are detected. It:

- Scans `openclaw.json` for all plaintext API key values
- Moves each to the vault file
- Replaces with `SecretRef` objects in config
- Auto-configures the file provider if needed
- Reports what was migrated

### 3. Dynamic Key Discovery

The UI automatically scans the entire config for API keys — no hardcoded list.

**Detection patterns:** `apiKey`, `api_key`, `token`, `secret`, `*_KEY`, `*_TOKEN`, `*_SECRET`

**Where it looks:**
- `env.*` — Environment variables
- `skills.entries.*.apiKey` — Skill-specific keys
- `messages.tts.*.apiKey` — TTS provider keys
- Any nested config path

**Known providers** get friendly names, descriptions, and "Get key ↗" links:

| Provider | Env Key |
|----------|---------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Google / Gemini | `GOOGLE_API_KEY` / `GEMINI_API_KEY` |
| Brave Search | `BRAVE_API_KEY` |
| ElevenLabs | `ELEVENLABS_API_KEY` |
| Deepgram | `DEEPGRAM_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Fireworks | `FIREWORKS_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| xAI (Grok) | `XAI_API_KEY` |
| Perplexity | `PERPLEXITY_API_KEY` |
| GitHub | `GITHUB_TOKEN` |
| Hume AI | `HUME_API_KEY` / `HUME_SECRET_KEY` |

### 4. Vault Status Banner

Top of the page shows:
- **🔒 Vault Active** (green) — All keys in vault, provider configured
- **⚠️ X Plaintext Keys Detected** (yellow) — Migration recommended

### 5. Key Status Badges

Each key row shows:
- **VAULT** (green) — Stored in secure vault file
- **PLAINTEXT** (yellow) — Still in config as raw string
- **NOT SET** (grey) — Not configured

### 6. Vault-Only Keys Section

Keys stored in the vault that aren't referenced by any config path are displayed in a dedicated "Vault-Only Keys" card. These are keys created manually or by skills that don't have a corresponding env/config entry. Each shows:
- 🔒 icon with the key name (monospace)
- Masked value preview
- Delete button

### 7. Manual "+ Add Secret" Form

The Vault tab header includes a "+ Add Secret" button that expands an inline form:
- **KEY_NAME** input (monospace, UPPER_SNAKE_CASE recommended)
- **Secret value** input (password field)
- **Save** / **Cancel** buttons
- Writes to vault with `envEntry: false` — no config entry created, no restart triggered
- Key appears immediately in the "Vault-Only Keys" section

### 8. Restart Notification Banner

When a vault write triggers a config change, a yellow warning banner appears:
> ⚠ New secrets require a gateway restart to take effect.
> [Restart Now]

The banner persists until the user clicks "Restart Now" or refreshes. This replaces the previous auto-reload behavior that caused unexpected gateway restarts.

### 9. Skills Vault Key Selector

On the Skills tab, skills that declare a `primaryEnv` get a vault key selector instead of a raw password input:

**When unlinked:**
- Dropdown shows all vault keys with 🔒 icons
- "Select vault key for ENV_NAME…" placeholder
- Selecting a key writes a `SecretRef` to `skills.entries.<key>.apiKey` in config
- "＋ Add new vault key…" option opens inline creation form

**When linked:**
- Shows `🔒 KEY_NAME` with an "Unlink" button
- Unlink removes the SecretRef from config

**Inline key creation:**
- KEY_NAME + Secret value fields
- "Save & Link" creates the vault key and links it to the skill in one step
- Key also appears in the Vault tab's vault-only keys section

### 10. Skills Expanded by Default

All skill groups (workspace, built-in, managed) render expanded (`<details open>`) for better discoverability. Previously workspace and built-in were collapsed by default.

### 11. Auth Profiles Display

Auth profile keys (from `auth-profiles.json`) that are stored in the vault are listed with their status. Backend RPCs support listing, error reset, and deletion.

## Architecture

### Security Model

```
┌──────────────────────────────────────────────────────────┐
│  Browser                                                  │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Vault Tab                                        │    │
│  │  ┌──────────────────────────────────────────┐    │    │
│  │  │ OpenAI: [••••••••••] [Save] [✕]  🟢VAULT │    │    │
│  │  │ Anthropic: [        ] [Save]     ⚪NOT SET│    │    │
│  │  │ + Add Secret  [KEY_NAME] [value] [Save]   │    │    │
│  │  └──────────────────────────────────────────┘    │    │
│  │                                                   │    │
│  │  Skills Tab                                       │    │
│  │  ┌──────────────────────────────────────────┐    │    │
│  │  │ whisper-api: 🔒 OPENAI_API_KEY  [Unlink] │    │    │
│  │  │ sag:         [Select vault key ▾]         │    │    │
│  │  └──────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────┘    │
│                           │                               │
│                           ▼ (direct RPC, not via agent)   │
└───────────────────────────┼───────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   Gateway     │
                    │ secrets.write │
                    │ skills.update │
                    └──┬─────────┬──┘
                       │         │
              ┌────────▼──┐  ┌──▼────────────┐
              │ secrets.   │  │ openclaw.json  │
              │ json       │  │ (SecretRef     │
              │ (0600)     │  │  objects only) │
              └────────────┘  └────────────────┘
```

### Backend RPCs

| Method | Description |
|--------|-------------|
| `secrets.status` | Vault file status, key count, plaintext count |
| `secrets.list` | List secret IDs with masked values |
| `secrets.write` | Store key in vault + optionally update config with SecretRef. `envEntry` param (default `true`) controls whether an env block entry is created. Returns `restartNeeded` flag instead of auto-reloading. |
| `secrets.delete` | Remove from vault + config |
| `secrets.migrate` | Batch-migrate all plaintext keys to vault |
| `secrets.authProfiles.list` | List auth profile keys with vault status |
| `secrets.authProfiles.resetErrors` | Reset auth profile error state |
| `secrets.authProfiles.delete` | Delete an auth profile |
| `skills.update` | Updated with `vaultKeyId` param — writes a SecretRef to `skills.entries.<key>.apiKey` or unlinks (empty string) |

### Skills-Status Integration

`SkillStatusEntry` includes a `vaultKeyId` field that reads the **raw** config JSON (not the runtime-resolved config where SecretRefs are replaced with resolved strings). This is done via `extractVaultKeyIdFromConfig()` which reads and caches `openclaw.json` directly, checking for SecretRef objects in `skills.entries.<key>.apiKey`.

### Restart Behavior

**No auto-restart on vault save.** Previously, `secrets.write` called `reloadSecrets()` which could trigger a gateway restart. Now:
- Vault-only saves (`envEntry: false`) don't touch config — no restart needed
- Config-touching saves return `restartNeeded: true` — UI shows a restart banner
- Skills vault linking writes to config via `writeConfigFile()` — triggers the config file watcher which causes a gateway restart (inherent to the config watcher system)

### OpenClaw Secrets System Integration

This skill uses OpenClaw's built-in Secrets System (`src/secrets/`):

- **File provider:** `{ source: "file", path: "~/.openclaw/secrets.json", mode: "json" }`
- **SecretRef format:** `{ source: "file", provider: "default", id: "/<KEY_NAME>" }`
- **Runtime resolution:** `prepareSecretsRuntimeSnapshot()` resolves all refs at gateway startup
- **Security:** File permissions checked (0600), ownership verified, path guards

The secrets system also supports `env` and `exec` providers for advanced setups (e.g., environment variables, external vault commands). The file provider is the default for this UI.

### Files Modified (Source Locations in OpenClaw Repo)

| File | Purpose |
|------|---------|
| `src/gateway/server-methods/secrets.ts` | Vault RPCs (status, list, write, delete, migrate, authProfiles) |
| `src/gateway/server-methods/skills.ts` | Skills update with `vaultKeyId` param |
| `src/gateway/server-methods/plugins-ui.ts` | Plugin view registration |
| `src/gateway/protocol/schema/agents-models-skills.ts` | `vaultKeyId` in SkillsUpdateParamsSchema |
| `src/agents/skills-status.ts` | `vaultKeyId` field on SkillStatusEntry, raw config reader |
| `ui/src/ui/controllers/apikeys.ts` | Vault-aware state, addVaultSecret, loadVaultOnlyKeys |
| `ui/src/ui/controllers/skills.ts` | VaultKeyEntry type, loadVaultKeys, linkSkillToVaultKey, addVaultKeyAndLink |
| `ui/src/ui/views/apikeys.ts` | Vault UI (banners, badges, migration, add form, vault-only keys, restart banner) |
| `ui/src/ui/views/skills.ts` | Vault key selector dropdown, inline creation, expanded groups |
| `ui/src/ui/app.ts` | State properties (vault, restart, skill key management) |
| `ui/src/ui/app-render.ts` | Prop wiring for vault and skills |
| `ui/src/ui/app-settings.ts` | Tab load triggers for vault keys |
| `ui/src/ui/types.ts` | `vaultKeyId` on SkillStatusEntry |
| `ui/src/ui/navigation.ts` | Vault tab (lock icon), removed 1password/discord standalone tabs |

### Reference Files

```
apikeys-ui/
├── SKILL.md                              # This file
├── INSTALL_INSTRUCTIONS.md               # Step-by-step installation (legacy)
└── reference/
    ├── apikeys-controller.ts             # UI controller (vault tab)
    ├── apikeys-views.ts                  # UI view (vault tab)
    ├── secrets-rpc.ts                    # Backend vault RPCs
    ├── skills-controller.ts              # UI controller (skills vault integration)
    ├── skills-views.ts                   # UI view (vault key selector)
    ├── skills-status.ts                  # Backend skill status with vaultKeyId
    └── skills-rpc.ts                     # Backend skills update RPC
```

## Key Design Decisions

1. **No auto-restart on save** — `secrets.write` no longer calls `reloadSecrets()`. A restart banner with "Restart Now" button lets the user decide when to restart.

2. **Vault-only keys** — Keys created with `envEntry: false` don't appear in config. A separate `secrets.list` call finds all vault entries and shows orphan keys in a dedicated section.

3. **Raw config reading for vaultKeyId** — The runtime resolves SecretRefs to strings, so `loadConfig()` returns resolved values. `extractVaultKeyIdFromConfig()` reads the raw JSON file directly (with mtime caching) to detect SecretRef objects.

4. **Skills expanded by default** — All `<details>` groups render open for better UX. Collapsed-by-default hid skills that needed configuration.

5. **Skills use vault references, not plaintext** — Skills with `primaryEnv` get a vault key selector dropdown instead of a password input. Linking writes a SecretRef to `skills.entries.<key>.apiKey` in config.

6. **Inline key creation from skills** — "＋ Add new vault key…" in the skills dropdown creates a vault entry and links it in one step, reducing friction.

## Changelog

### v3.0.0
- **Manual "+ Add Secret" form** in Vault tab header — create vault keys without config entries
- **Vault-Only Keys section** — shows keys in vault not referenced by config
- **Restart notification banner** — yellow warning with "Restart Now" button replaces auto-reload
- **Skills vault key selector** — dropdown replaces raw password input for skills with `primaryEnv`
- **Skills inline key creation** — "＋ Add new vault key…" creates and links in one step
- **Skills expanded by default** — all groups open, no more collapsed-by-default
- **vaultKeyId on SkillStatusEntry** — reads raw config JSON to detect SecretRef objects
- **`envEntry` param on secrets.write** — controls whether an env block entry is created
- **`vaultKeyId` param on skills.update** — writes SecretRef or unlinks skill from vault key

### v2.0.0
- **Vault-backed storage:** Keys stored in `~/.openclaw/secrets.json` (mode 0600) instead of plaintext config
- **SecretRef integration:** Config values replaced with OpenClaw SecretRef objects pointing to vault
- **One-click migration:** "Migrate to Vault" batch-migrates all plaintext keys
- **Vault status banner:** Green (all secure) or yellow warning (plaintext detected)
- **Key badges:** VAULT / PLAINTEXT / NOT SET per key
- **New RPCs:** `secrets.status`, `secrets.list`, `secrets.write`, `secrets.delete`, `secrets.migrate`
- **Plugin UI registration:** Moved from old nav to plugin architecture (settings group, position 1)
- **Auto-provider config:** Saving a key auto-configures the file secret provider if not present

### v1.1.0
- Dynamic key discovery — scans entire config instead of hardcoded list
- Auto-grouping by category (Environment / Skills / Other)
- Common env keys shown even if not configured

### v1.0.0
- Initial release with hardcoded provider slots
- Save/Clear functionality via `config.patch`
