# Skills (OpenClaw) Reference

Skills are reusable instruction sets (SKILL.md files) that extend agent capabilities. They're loaded into the system prompt at runtime.

## Locations and Precedence

1. **Bundled skills**: Shipped with the install (npm package or OpenClaw.app) — highest precedence.
2. **Managed/local skills**: `~/.openclaw/skills` — user-installed skills.
3. **Workspace skills**: `<workspace>/skills` — per-workspace skills.

Additional directories: `skills.load.extraDirs` in `~/.openclaw/openclaw.json` (lowest precedence).

## Per-Agent vs Shared Skills

- **Per-agent**: Live in `<workspace>/skills` for that agent only.
- **Shared**: Live in `~/.openclaw/skills` (managed/local), visible to all agents.
- **Extra dirs**: Added via `skills.load.extraDirs` for common skill packs.

## Plugins + Skills

Plugins can include skills via the `skills` field in their `openclaw.plugin.json` manifest. Plugin skills load/unload with `plugins.entries.<id>.enabled`.

Skills that require specific config can declare `metadata.openclaw.requires.config`.

## ClawHub (Install + Sync)

[ClawHub](https://clawhub.com) is a skill marketplace.

```bash
clawhub install <skill-slug>         # Install a skill into workspace
clawhub update --all                 # Update all installed skills
clawhub sync --all                   # Scan + publish updates
```

`clawhub` operates on the `./skills` or `<workspace>/skills` directory.

## Format (AgentSkills + Pi-compatible)

Skills use `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: What this skill does
---
# My Skill

Detailed instructions here...
```

## Gating (Load-Time Filters)

Skills can declare metadata for conditional loading (e.g., only load when certain conditions are met).

## Config Overrides (~/.openclaw/openclaw.json)

```json5
{
  skills: {
    entries: {
      "nano-banana-pro": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" },
        // or plaintext string
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

The skill key is derived from `metadata.openclaw.skillKey`, falling back to the skill name.

### Configuration Semantics

| Key | Meaning |
|---|---|
| `enabled: false` | Disables the skill even if bundled/installed |
| `env` | Injected only if variable not already set in process |
| `apiKey` | For skills declaring `metadata.openclaw.primaryEnv`; supports plaintext or SecretRef `{ source, provider, id }` |
| `config` | Optional bag for custom per-skill fields |
| `allowBundled` | Optional allowlist for bundled skills only |

## Environment Injection (Per Agent Run)

1. Reads skill metadata.
2. Applies `skills.entries.<key>.env` or `.apiKey` to `process.env`.
3. Builds the system prompt with eligible skills.
4. Restores original environment after the run ends.

## Session Snapshot (Performance)

Skills are snapshotted once per session build, not re-read each turn.

## Remote macOS Nodes (Linux Gateway)

Skills referencing `system.run` use `nodes` → `nodes.run` → `system.run` when the gateway runs on Linux but the node is macOS. `deny` the tool or whitelist specific commands.

## Skills Watcher (Auto-Refresh)

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

Changes to `SKILL.md` files trigger automatic reload.

## Token Impact (Skills List)

Each loaded skill contributes to system prompt token count:

```
total = 195 + Σ (97 + len(name) + len(description) + len(location))
```

- Base overhead (only when ≥1 skill loaded): 195 characters.
- Per skill: ~97 characters + escaped field lengths.
- Rough estimate: ~4 chars/token → ~24 tokens per skill plus field lengths.

## Managed Skills Lifecycle

Skills installed via ClawHub or the Control UI go into `~/.openclaw/skills`.

## Config Reference

See [Skills config](https://docs.openclaw.ai/tools/skills-config) for full config schema.

## Security Notes

- Treat third-party skills as **untrusted code**. Read them before enabling.
- Prefer **sandboxed runs** for untrusted inputs and risky tools.
- `skills.entries.*.env` and `.apiKey` inject secrets into the host process (not sandbox). Keep secrets out of prompts and logs.
- See [Security](security.md) for the broader threat model.
