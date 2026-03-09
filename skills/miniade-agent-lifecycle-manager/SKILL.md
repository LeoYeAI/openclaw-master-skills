---
name: agent-lifecycle-manager
description: "Manage full OpenClaw agent lifecycle operations on a node: create/register agents, configure channel bindings, inherit credentials, approve pairing, archive and delete agents, refresh status dashboards, and write lifecycle change logs. Use when a user asks to onboard a new agent, reconfigure an existing agent, retire/archive/delete agents, or maintain agent status boards and lifecycle audit records."
---

# Agent Lifecycle Manager

Use this skill to execute repeatable, low-error lifecycle operations for OpenClaw agents.

## Workflow

1. Collect required inputs
2. Run lifecycle action (create/configure/archive/delete/status)
3. Verify runtime status (`openclaw status`, `openclaw agents list`)
4. Refresh dashboard files
5. Append lifecycle log entry

If deleting an agent, always archive first and require explicit confirmation.

## Required inputs by action

- Create + Telegram bind:
  - `AGENT_ID`
  - `TELEGRAM_TOKEN`
  - optional `WORKSPACE` (default: `~/.openclaw/workspace-<AGENT_ID>`)
- Pairing approval (separate step):
  - `AGENT_ID`
  - `PAIRING_CODE` (obtained only after user sends `/start` to the bot)
- Reconfigure:
  - `AGENT_ID`
  - changed fields (model/routes/channel token/etc.)
- Archive/Delete:
  - `AGENT_ID`
  - archive destination (default under `state/archive/<AGENT_ID>/`)

## Command playbook

Read `references/openclaw-agent-lifecycle-playbook.md` before running uncommon operations.

For deterministic execution, use scripts in this skill:

- `scripts/create-telegram-agent.sh`
- `scripts/approve-telegram-pairing.sh`
- `scripts/archive-agent.sh`
- `scripts/delete-agent-safe.sh`
- `scripts/refresh-dashboard.sh`
- `scripts/lifecycle-log.sh`

## Execution rules

- Prefer `openclaw` CLI over ad-hoc file edits.
- Configure bindings via `openclaw config get/set` (append entry; do not overwrite blindly).
- Do not restart gateway by default after binding/config changes.
- Use pairing command with explicit channel flag: `openclaw pairing approve <PAIRING_CODE> --channel telegram`.
- Never hard-delete before successful archive.
- For deletion, prefer `scripts/delete-agent-safe.sh` (archive verification + explicit confirmation + cleanup + logging).
- After every lifecycle change, run dashboard refresh + lifecycle logging.

## Minimal post-change verification

Run:

```bash
openclaw agents list --json
openclaw status --json
openclaw gateway status --json
```

Confirm:
- target agent exists (or is absent after deletion)
- expected bindings/routes are present
- gateway runtime is healthy and RPC probe is ok
