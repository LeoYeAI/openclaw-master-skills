# OpenClaw agent workspace (cheat sheet)

This reference is for building **OpenClaw-specific agents** (not generic LLM “agents”).

## Workspace layout (canonical)

Workspace = agent’s “home” directory.

Common files at workspace root:

- `AGENTS.md` — operating instructions (how to behave, safety rules, memory workflow)
- `SOUL.md` — persona, tone, boundaries
- `IDENTITY.md` — name/vibe/emoji (short)
- `USER.md` — who the user is + how to address them
- `TOOLS.md` — local notes + conventions (NOT tool availability)
- `HEARTBEAT.md` — optional heartbeat checklist (keep tiny)
- `BOOTSTRAP.md` — one-time first-run ritual; delete after completed
- `MEMORY.md` — optional curated long-term memory (private sessions only)
- `memory/YYYY-MM-DD.md` — daily logs
- `skills/` — optional workspace-specific skills

## What NOT to store in the workspace

Do not commit secrets or credentials. Keep these out of the workspace repo:

- `~/.openclaw/openclaw.json` (config)
- `~/.openclaw/credentials/` (OAuth tokens, API keys)
- `~/.openclaw/agents/<agentId>/sessions/` (session transcripts)

## Heartbeats

Default heartbeat prompt:

`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`

Best practices:

- Keep `HEARTBEAT.md` extremely short.
- If `HEARTBEAT.md` exists but is effectively empty (only blank lines / headers), OpenClaw can skip heartbeat runs.
- Heartbeats burn tokens; enable only once you trust the agent.

## Safety defaults (recommended)

- Never run destructive/state-changing actions without explicit permission.
- Never send outbound messages/emails/posts unless explicitly asked.
- Prefer `trash` over `rm`.
- Stop on CLI usage errors; run `--help` and correct.
- In group chats: don’t be the user’s voice; respond only when mentioned or clearly useful.

## Sub-agents (important)

Sub-agents do not receive full bootstrap files. In particular, sub-agents only get `AGENTS.md` + `TOOLS.md` by default (not `SOUL.md`, `USER.md`, etc.).

Implication: if you delegate, ensure `AGENTS.md` contains the cross-cutting safety and operating rules you need sub-agents to follow.
