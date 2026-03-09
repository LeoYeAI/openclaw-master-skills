# OpenClaw Agent Lifecycle Playbook

## 1) Create agent workspace + registry

```bash
openclaw agents add <AGENT_ID> --workspace ~/.openclaw/workspace-<AGENT_ID>
```

## 2) Inherit auth profile (optional, from main)

```bash
mkdir -p ~/.openclaw/agents/<AGENT_ID>/agent/
cp ~/.openclaw/agents/main/agent/auth-profiles.json ~/.openclaw/agents/<AGENT_ID>/agent/
```

## 3) Add Telegram channel account

```bash
openclaw channels add --channel telegram --account <AGENT_ID> --token "<TELEGRAM_TOKEN>"
```

## 4) Configure bindings (append new item)

First inspect current bindings:

```bash
openclaw config get bindings --json
```

Append one binding entry without losing existing items (example with jq):

```bash
BINDINGS_JSON="$(openclaw config get bindings --json 2>/dev/null || echo '[]')"
NEW_BINDINGS="$(jq -c --arg agentId "<AGENT_ID>" '
  . + [{agentId:$agentId, match:{channel:"telegram", accountId:$agentId}}]
' <<< "$BINDINGS_JSON")"
openclaw config set bindings "$NEW_BINDINGS" --json
```

> Do not require `openclaw gateway restart` by default after this step.

## 5) Trigger pairing code from Telegram

After binding is done, user must send `/start` to the bot in Telegram.
Only then will a pairing code be generated.

You can list pending pairing requests:

```bash
openclaw pairing list --channel telegram --account <AGENT_ID> --json
```

## 6) Approve pairing

```bash
openclaw pairing approve <PAIRING_CODE> --channel telegram --account <AGENT_ID>
```

---

## Archive before delete

Recommended archive items:

- `~/.openclaw/agents/<AGENT_ID>/`
- `~/.openclaw/workspace-<AGENT_ID>/`
- runtime status snapshots:
  - `openclaw agents list --json`
  - `openclaw status --json`
  - `openclaw gateway status --json`

Preferred deletion command:

```bash
scripts/delete-agent-safe.sh <AGENT_ID>
```

This script enforces: archive -> confirmation -> bindings cleanup -> telegram account cleanup -> agent delete -> dashboard/log update.

Only use direct delete command(s) if this safe flow is unavailable.

## Required bookkeeping

After create/configure/archive/delete:

1. refresh dashboard outputs
2. append one lifecycle log record (UTC timestamp, action, agent id, summary, operator)
