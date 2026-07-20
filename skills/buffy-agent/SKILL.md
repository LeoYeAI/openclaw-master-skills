---
name: buffy-agent
description: Free habit tracking, todo, and routines — create and track up to 25 habits, 100 tasks, and 15 routines; schedule reminders and daily briefings across ChatGPT, Telegram, Slack, and OpenClaw. Completely free, no paid tiers. Use when the user wants to manage habits, todo/tasks, or routines, get progress summaries, or set reminder timing.
primaryEnv: BUFFY_API_KEY
requires:
  env:
    - BUFFY_API_KEY
metadata: {"openclaw":{"primaryEnv":"BUFFY_API_KEY","requires":{"env":["BUFFY_API_KEY"]},"keywords":["habit","todo","tasks","routines","reminders","daily briefing","free"],"summary":"Free habit & todo in chat — track up to 25 habits, 100 tasks, and 15 routines with reminders. No paid plans."}}
---

**Free habit & todo in chat.** Track up to 25 habits, 100 tasks, and 15 routines with reminders and daily briefings — completely free, no paid tiers. Ask in plain language; Buffy creates and tracks for you.

## What you can do (habit, todo, routines)

| Search for… | You can say… |
|-------------|--------------|
| **Habit** | "Create a habit to drink water every 2 hours." / "What habits did I complete today?" |
| **Todo** | "Add to my todo: buy groceries." / "What's on my todo?" / "Mark 'call mom' done." |
| **Routines** | "Start my morning routine." / "Remind me at 8am to plan my day." |

Buffy understands natural language — no forms or menus. One message creates or updates habits, todo items, and routines.

## Overview

Buffy is a **free** personal behavior agent for **habits**, **todo/tasks**, and **routines**. It tracks activities, schedules reminders, and sends daily briefings across multiple channels (ChatGPT, Telegram, Slack, OpenClaw), all powered by a single unified behavior engine. Buffy is completely free with generous limits: 25 habits, 100 tasks, 15 routines, 200 reminders/day, and 365 days of memory.

**This skill** is only the HTTP client for the Buffy API and **requires only `BUFFY_API_KEY`**. Buffy runs as an external HTTP API; all behavior logic lives in the Buffy backend.

Buffy also exposes a hook-based observability system:

- Backend hooks in the Go service emit events like `message:received`, `message:replied`, and
  `reminder:sent` so logs, metrics, and long-term memory can be updated without changing core
  behavior logic. See `backend/internal/hooks/` for details.
- OpenClaw hooks can be installed **alongside** this skill (see the `hooks/` docs in this repo) to
  log Buffy conversations to markdown logs, record Buffy-related errors for observability, and
  track Buffy behavior over time. These hooks are **optional and separately installed** by the
  integrator; they are **not** part of this skill’s declared requirements. If the integrator installs
  them, they may write user content to disk or call other APIs and have their own credential and
  privacy implications.

For low-level HTTP details and the full API surface, treat the repository `README.md` and `openapi-buffy.yaml`
as canonical. This `SKILL.md` file is the canonical guide for how agents and tools should invoke Buffy.

## Base URL and authentication

- **Base URL**: default `https://api.buffyai.org` (can be overridden via config, see below).
- **Auth header**: always send
  - `Authorization: Bearer <BUFFY_API_KEY>`
- **Optional user header** (when using a system key):
  - `X-Buffy-User-ID: <stable-user-id>`

`BUFFY_API_KEY` is injected from the environment for the agent run. Do **not** include the key
in prompts, logs, or user-visible text.

For registries and gateways:

- Treat `BUFFY_API_KEY` as the **primary credential** for this skill (declared in this file’s frontmatter and in the root [skill.md](skill.md) for registry compatibility).
- Do not enable the skill unless `BUFFY_API_KEY` has been configured (for example, via `requires.env` metadata).

## Core endpoint: POST /v1/message

For most use cases, **always prefer** `POST /v1/message`. Buffy’s behavior core understands
natural language instructions and orchestrates activities, reminders, and daily briefings.

- **Method**: `POST`
- **Path**: `/v1/message`
- **Headers**:
  - `Authorization: Bearer <BUFFY_API_KEY>`
  - `Content-Type: application/json`
  - Optionally `X-Buffy-User-ID: <stable-user-id>` if acting on behalf of a specific user via a system key.

- **Body**:

```json
{
  "user_id": "user-123",
  "platform": "openclaw",
  "message": "Remind me to drink water every 2 hours"
}
```

- **Response (simplified)**:

```json
{
  "reply": "Created a routine activity for you: \"Remind me to drink water every 2 hours\"."
}
```

For users who have a clan (any user gets one on first use), the backend may append clan context to the reply (e.g. clan name, shared energy, and active boss progress). The skill does not need to change how it calls the API; just surface the full `reply` to the user.

### Usage notes for the agent

When calling `POST /v1/message`:

- Choose a **stable** `user_id` for the end-user:
  - Prefer a consistent external ID from the calling system (for example, an OpenClaw user ID) when available.
  - Otherwise, use the chat/session’s stable user identifier if provided in context.
- Always set `"platform": "openclaw"` unless the environment explicitly configures another platform.
- Put the user’s natural-language request in `"message"` in a clear, concise form.
- Reuse the same `user_id` across the conversation so Buffy can maintain context.

Examples of when to call Buffy (habit, todo, routines):

- **Habit:** "Create a habit to stretch every hour during workdays." / "What habits have I completed today?"
- **Todo:** "Add to my todo: review the report." / "What's on my todo?" / "Mark 'send email' as done."
- **Routines:** "Pause my evening exercise routine this week." / "Set a reminder tomorrow at 8am to plan my day."

## Use via Buffy CLI

You can call the same Buffy API from the **terminal or scripts** using the official **Buffy CLI**. The same `BUFFY_API_KEY` used by this skill works for the CLI.

- **Install**: Download a binary from [Releases](https://github.com/phantue2002/buffy-cli/releases) for your OS/arch, or run `go install github.com/phantue2002/buffy-cli@latest` (Go 1.21+).
- **Authenticate**: Set `export BUFFY_API_KEY=your_key` or pass `--api-key KEY` (or `--api-base URL` for a different endpoint).
- **Send a message** (creates habits, tasks, routines, reminders in natural language):
  - `buffy message --text "remind me to drink water every day"`
- **Manage settings and keys**: `buffy user-settings get`, `buffy user-settings set`, `buffy api-key list`, `buffy api-key create`, `buffy api-key revoke`.

Repo: [github.com/phantue2002/buffy-cli](https://github.com/phantue2002/buffy-cli). Use the CLI when the user prefers the command line or wants to automate Buffy from scripts; use this skill (HTTP) when invoking Buffy from an agent or chat surface.

## Supporting endpoints

You **usually do not need** these, but they are available for more advanced flows.

### Clan / team

Any user can use clans (shared energy, boss fights). A personal clan is created on first use; no team plan required. The **reply from `POST /v1/message`** already includes clan name, energy, and active boss progress when the user has a clan; you do not need to call these unless building a custom flow.

- **GET /v1/clans/me** — Current user's clan (creates team and clan on first access if needed; 404 only if user not found).
- **GET /v1/clans/{clan_id}/energy** — Clan energy (members only).
- **POST /v1/clans/{clan_id}/bosses** — Create a boss (owner/admin).
- **GET /v1/clans/{clan_id}/bosses** — List bosses; **GET /v1/clans/{clan_id}/bosses/{boss_id}** — Boss detail.

All require the same `Authorization: Bearer <BUFFY_API_KEY>` and (for system keys) `X-Buffy-User-ID` when acting on behalf of a user. Prefer `POST /v1/message` for normal chat; use these only for dedicated clan/team UI or automation.

### User settings

These endpoints control personalization (name, timezone, language, reminder preferences, etc.).

- **GET /v1/users/{id}/settings**
  - Fetch current settings for a user.

- **PUT /v1/users/{id}/settings**
  - Update one or more settings for a user.
  - Body fields are all optional:
    - `name: string`
    - `language: "en" | "vi" | ...`
    - `timezone: string` (IANA TZ, e.g. `"Asia/Ho_Chi_Minh"`)
    - `preferred_reminder_hour: number` (0–23)
    - `preferred_channels: string` (comma-separated, e.g. `"clawbot,telegram"`)
    - `morning_person: boolean`
    - `night_owl: boolean`

Only use these endpoints when the user is explicitly changing preferences (for example:
“Change my preferred reminder time to 8am.”). For general “help me with my habits” queries,
prefer `POST /v1/message`.

### API key provisioning (advanced)

Buffy can create API keys for other tools and integrations:

- **POST /v1/users/{id}/api-keys**

Body:

```json
{
  "label": "clawbot",
  "type": "system"
}
```

This returns a one-time `api_key` string that can be used in the `Authorization` header.

**Important**: this is an advanced operation. Do **not** automatically create keys unless the
user explicitly wants to manage Buffy API keys or set up additional integrations.

## Invocation pattern and best practices

When deciding whether and how to call Buffy:

- Use Buffy when the request clearly relates to **habits, tasks, routines, reminders, daily briefings, or clan/team status** (e.g. "What's our clan energy?" — reply includes clan name, energy, and active boss when the user has a clan).
- Default to `POST /v1/message` rather than manually composing lower-level operations.
- Preserve a consistent `user_id` so Buffy’s behavior core and memory can work effectively.
- Keep `message` short, clear, and close to what the user asked for, but you may add clarifying
  details that the user has already given in the conversation.

Avoid:

- Creating or exposing raw internal IDs to the user when not necessary.
- Making redundant calls to Buffy if you already have the needed information from a recent response.
- Using Buffy for requests that are **not** about habits, todo, routines, reminders, or clan/team (e.g. "how do I do X", "find a skill for X", testing, deployment, design). For those, use or suggest the **find-skills** workflow (e.g. `npx skills find [query]`) so the user can discover and install the right skill.

### Extending capabilities (find-skills)

When the user asks for help that is **outside** Buffy’s scope (e.g. "how do I test my API?", "find a skill for React", "is there a skill that can review PRs?"):

1. **Do not** call Buffy for those requests.
2. If the **find-skills** skill is available, use it: run `npx skills find [query]` with a relevant query, then present install commands and links (e.g. `npx skills add <owner/repo@skill> -g -y`).
3. If find-skills is not available, suggest the user run `npx skills find <topic>` or browse https://skills.sh/ to discover and install a skill for that capability.

This keeps Buffy focused on habit/todo/routines and lets the agent hand off capability discovery to find-skills for best performance.

## Security, privacy, and sandboxing

- **Secrets**:
  - `BUFFY_API_KEY` is provided via the agent environment (for this skill’s turn).
  - Never log, echo, or include `BUFFY_API_KEY` in any user-facing message or tool arguments.
  - Do not serialize or store the key in prompts, memory, or external logs.

- **User data**:
  - Buffy responses can contain sensitive information about a user’s routines, health-related habits,
    and daily schedule.
  - Treat all such data as private; only surface to the user who owns it and avoid sharing across users.

- **Conversation logs and hooks**:
  - This skill **does not itself** write any logs to disk.
  - Optional OpenClaw hooks (for example, `buffy-error-tracker`) may append Buffy-related events to
    repo-local markdown logs under a path you control (such as `logs/`).
  - Decide explicitly whether you want such logs, where they live, and how they are rotated or pruned.
  - Avoid storing highly sensitive user content in long-lived logs unless your compliance model allows it.

- **Sandboxing and network access**:
  - Buffy is an **external HTTPS API**. The agent (or sandbox, if used) must have outbound HTTPS
    access to the configured Buffy endpoint (default `https://api.buffyai.org`).
  - This skill does **not** require any local binaries inside the sandbox (`requires.bins` is not used).
  - If the gateway uses sandboxed runs for untrusted tools, ensure that the sandbox image allows
    HTTPS egress to the Buffy endpoint while still respecting whatever network and filesystem
    restrictions are configured.

- **Reminder dispatch and channel credentials**:
  - Reminder delivery to channels like Telegram or Clawbot is implemented via **separate hooks/tools**
    (for example, the `buffy-reminder-dispatch` hook), not by this core Buffy skill.
  - This skill’s metadata does **not** declare those channel credentials, because they are not required
    for the core Buffy API client.
  - Those hooks will typically require their own channel credentials (Telegram bot tokens, Clawbot
    API keys, etc.); they should be configured **only** for the dispatch implementation you control.
  - Do not reuse `BUFFY_API_KEY` as a channel credential, and do not expose channel tokens to the
    Buffy HTTP client unless absolutely necessary.

## Configuration via openclaw.json

This skill is configured through `~/.openclaw/openclaw.json` using the `skills.entries` map.
Because the metadata sets `primaryEnv` to `BUFFY_API_KEY`, you can either provide an API key
directly or reference an existing environment variable.

### Minimal config (using process env)

If `BUFFY_API_KEY` is already set in the process environment:

```json
{
  "skills": {
    "entries": {
      "buffy-agent": {
        "enabled": true,
        "apiKey": {
          "source": "env",
          "provider": "default",
          "id": "BUFFY_API_KEY"
        }
      }
    }
  }
}
```

### Config with explicit env injection and endpoint override

If you want OpenClaw to inject `BUFFY_API_KEY` only for this skill and/or override the API endpoint
for staging or local development:

```json
{
  "skills": {
    "entries": {
      "buffy-agent": {
        "enabled": true,
        "apiKey": "BUFFY_KEY_HERE",
        "env": {
          "BUFFY_API_KEY": "BUFFY_KEY_HERE"
        },
        "config": {
          "endpoint": "https://api.buffyai.org",
          "platform": "openclaw"
        }
      }
    }
  }
}
```

Notes:

- `env` values are only injected if the variable is not already set in the process.
- `config.endpoint` can be changed to point to:
  - `https://api-dev.buffyai.org` (staging), or
  - `http://localhost:8080` (local backend).
- `config.platform` can be used by the tool implementation as the default `"platform"` field
  when calling `POST /v1/message`.

## Testing the Buffy AgentSkill

To validate that the skill works end-to-end:

1. **Start Buffy**:
   - Either run the full stack with Docker (`docker compose up`) or start the backend locally
     following the repository README.
2. **Obtain an API key**:
   - Use `POST /v1/users/{id}/api-keys` to create a system key labeled for OpenClaw usage.
3. **Configure OpenClaw**:
   - Add an entry for `"buffy-agent"` in `~/.openclaw/openclaw.json` as shown above, pointing
     `config.endpoint` at your running Buffy instance and wiring `BUFFY_API_KEY`.
4. **Verify skill discovery**:
   - Use the OpenClaw UI or CLI to list skills and confirm:
     - `buffy-agent` appears.
     - The emoji, description, and website are correct.
5. **Run a sample interaction**:
   - From OpenClaw, invoke the `/buffy-agent` command (or let the agent auto-select the skill) with
     a request such as “Remind me to stretch every hour during workdays.”
   - Confirm that Buffy:
     - Receives a `POST /v1/message` with the expected `user_id`, `platform`, and `message`.
     - Returns a sensible `reply` that the agent surfaces to the user.
6. **Regression checks**:
   - Confirm the skill is **filtered out** when `BUFFY_API_KEY` is not configured (per `requires.env`).
   - Confirm it still works when `env` injection is omitted but `BUFFY_API_KEY` is already present
     in the process environment.

This completes the Buffy AgentSkill wiring: a thin, secure HTTP wrapper around the existing
Buffy behavior core, suitable for both autonomous model use and direct user invocation.

