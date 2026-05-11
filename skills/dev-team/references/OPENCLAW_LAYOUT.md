# OpenClaw layout × `dev_team` (`TEAM_ROOT`)

**New to this skill?** Start with **[SKILL-SETUP.md](SKILL-SETUP.md)** (guided setup, exact folder list, copy-paste prompts).

This reference aligns with the official OpenClaw docs and the **`dev_team`** skill. It works the same on a laptop, a bare-metal server, or in Docker — only **`stateDir`**, per-agent workspaces, and mounts differ.

**Sources:** [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace), [Skills](https://docs.openclaw.ai/tools/skills), [Multi-agent routing](https://docs.openclaw.ai/concepts/multi-agent), [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing).

## Resolve paths on this gateway

1. **`stateDir`:** use `$OPENCLAW_STATE_DIR` if set, otherwise `~/.openclaw`.
2. **`TEAM_ROOT`:** use `$DEV_TEAM_ROOT` if set, otherwise **`<stateDir>/dev-team`**.

Shared agency files live under **`TEAM_ROOT/team/`** (customers, tasks, handoffs, etc.). See [SKILL.md](../SKILL.md) — *Extended shared directory layout*.

## Official OpenClaw path map (summary)

| Purpose | Typical default | Config / override |
|--------|-----------------|-------------------|
| Gateway config | `<stateDir>/openclaw.json` | e.g. `OPENCLAW_CONFIG_PATH` (see docs) |
| State root | `~/.openclaw` | `OPENCLAW_STATE_DIR` |
| Agent workspace (default CWD for file tools) | `~/.openclaw/workspace` | `agents.list[].workspace`; `OPENCLAW_PROFILE` |
| Per-agent auth / state | `<stateDir>/agents/<agentId>/agent` | `agents.list[].agentDir` |
| Sessions | `<stateDir>/agents/<agentId>/sessions/` | — |
| Workspace skills | `<workspace>/skills/` | Highest precedence for that agent |
| Managed (shared) skills | `<stateDir>/skills/` | Same host / same `stateDir` |
| Extra skill dirs | — | `skills.load.extraDirs` |
| Workspace bootstrap | `AGENTS.md`, `SOUL.md`, `USER.md`, … | [Agent workspace — file map](https://docs.openclaw.ai/concepts/agent-workspace) |

## Sandbox and Docker

If each agent runs in an isolated sandbox or container, **file tools** only see what is mounted. Mount **`TEAM_ROOT`** at the **same absolute path** in every container that must read or write `team/customers/.../tasks/...`, etc. See [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing).

## `AGENTS.md` snippet (every participating agent workspace)

Use the **same** resolved absolute path in each workspace. Replace the placeholder after you resolve `stateDir` on the host.

```markdown
## Shared project memory (`dev_team`)

- **TEAM_ROOT** (this gateway): `/absolute/path/to/dev-team`  
  - Default if unset: `<stateDir>/dev-team` where `<stateDir>` is `$OPENCLAW_STATE_DIR` or `~/.openclaw`.  
  - Override: set environment variable **`DEV_TEAM_ROOT`** to an absolute path (document here if used).
- **Canonical tree:** `TEAM_ROOT/team/` — per customer `team/customers/<customer_id>/CONTEXT.md` and task artefacts under `team/customers/<customer_id>/tasks/<task_id>/` (`SPEC.md`, `HANDOFF.md`, `QA_NOTES.md`). No top-level `team/tasks/`.
- **Portfolio index:** `team/PROJECT_STATUS.md` = short human index only; `team/board.json` = structured active-task overview — see [BOARD_SCHEMA.md](BOARD_SCHEMA.md) and [SKILL.md — Portfolio index](../SKILL.md#portfolio-index-project_status-and-boardjson).
- Use **absolute** paths in handoffs so all agents see the same files regardless of workspace CWD.
```

Example default on a typical Linux install (no overrides):

- `stateDir` = `~/.openclaw`
- `TEAM_ROOT` = `~/.openclaw/dev-team`
- Shared tree = `~/.openclaw/dev-team/team/`

On a server with `OPENCLAW_STATE_DIR=/var/lib/openclaw`:

- `TEAM_ROOT` = `/var/lib/openclaw/dev-team` unless `DEV_TEAM_ROOT` is set.

## Skill package vs team data

Skill files live under **`{baseDir}`** after install (see [Creating Skills](https://docs.openclaw.ai/tools/creating-skills)). **`TEAM_ROOT`** is **not** `{baseDir}` — it holds **your** `team/` data; the skill only defines how to name and bootstrap it.
