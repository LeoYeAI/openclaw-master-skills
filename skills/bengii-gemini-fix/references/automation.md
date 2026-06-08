# OpenClaw Automation Reference (Cron Jobs, Webhooks, Gmail Pub/Sub)

## Table of Contents

- [Cron Jobs](#cron-jobs)
- [Webhooks](#webhooks)
- [Gmail Pub/Sub](#gmail-pubsub)

---

## Cron Jobs

Cron runs inside the **Gateway** (not inside the model). Jobs persist under `~/.openclaw/cron/jobs.json`.

### Quick Start

```bash
# One-shot reminder
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the docs" \
  --wake now \
  --delete-after-run

# Recurring isolated job with announce
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"

# Management
openclaw cron list
openclaw cron run <job-id>
openclaw cron runs --id <job-id>
```

### Concepts

#### Jobs

Each job has:
- **Schedule** (when it runs)
- **Payload** (what it does)
- **Delivery mode** (optional): `announce`, `webhook`, or `none`
- **Agent binding** (optional): `agentId` — run under a specific agent

#### Schedules

| Type | Description | Example |
|---|---|---|
| `at` | One-shot timestamp (ISO 8601) | `schedule.at: "2026-02-01T16:00:00Z"` |
| `every` | Fixed interval (ms) | `schedule.every: 3600000` |
| `cron` | 5-field cron expression + optional timezone | `schedule.cron: "0 7 * * *"` |

Options: `--stagger 30s` to set stagger window, `--exact` to force `staggerMs = 0`.

#### Execution Modes

| Mode | Session Key | Description |
|---|---|---|
| **Main session** | `main` | System event → heartbeat prompt |
| **Isolated** | `cron:<jobId>` | Dedicated agent turn, fresh session per run |

**Main session jobs**: `payload.kind = "systemEvent"`. Wake options: `"now"` (immediate) or `"next-heartbeat"`.

**Isolated jobs**: Each run starts a fresh sessionId. Prompt prefixed with `[cron:<jobId> <job name>]`.

#### Payload Shapes

- `systemEvent`: main-session only, routed through heartbeat
- `agentTurn`: isolated only, runs a dedicated agent turn with `message`, optional `model`/`thinking`/`timeoutSeconds`

#### Delivery

| Mode | Behavior |
|---|---|
| `announce` (default for isolated) | Deliver summary to target channel + main session summary |
| `webhook` | POST to `delivery.to` URL |
| `none` | Internal only, no delivery |

Delivery fields:
- `delivery.channel`: `whatsapp` / `telegram` / `discord` / `slack` / `mattermost` / `signal` / `imessage` / `last`
- `delivery.to`: channel-specific target or webhook URL
- `delivery.bestEffort`: avoid failing if announce delivery fails

**Telegram topics**: Use `delivery.to: "-1001234567890:topic:123"` format.

#### Model & Thinking Overrides

Override priority: Job payload → Hook-specific defaults → Agent config default.

- `model`: `provider/model` string or alias
- `thinking`: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`

### Retry Policy

- **Transient errors** (retried): network timeouts, rate limits, upstream 5xx
- **Permanent errors** (no retry): auth failures, invalid config, model not found
- Default: no config needed; built-in retries for transient errors

### Configuration

```json5
{
  cron: {
    webhookToken: "your-token",     // Auth for webhook mode
    stagger: { defaultMs: 0 },     // Default stagger
  },
}
```

### Troubleshooting

| Problem | Fix |
|---|---|
| "Nothing runs" | Check `openclaw gateway status`, ensure Gateway is running |
| Recurring job delays after failures | Check retry backoff; reset with `openclaw cron run <id>` |
| Telegram delivers to wrong place | Use explicit `:topic:` format for forum threads |
| Subagent announce retries | Set `delivery.bestEffort: true` |

---

## Webhooks

HTTP endpoints exposed by the Gateway for external triggers.

### Enable

```json5
{
  gateway: {
    webhooks: { enabled: true },
  },
}
```

### Auth

Webhooks require `gateway.auth.token` or `gateway.auth.password`. Pass via `Authorization: Bearer <token>` header.

### Endpoints

#### `POST /hooks/wake`

Trigger a wake/heartbeat cycle.

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H "Authorization: Bearer $TOKEN"
```

#### `POST /hooks/agent`

Send a prompt to the agent, run a dedicated turn.

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check server status"}'
```

Options: `model`, `thinking`, `agentId`, `sessionKey`, `delivery`.

#### `POST /hooks/<name>` (mapped)

Custom-named webhook endpoints configured in `gateway.webhooks.map`.

### Session Key Policy

By default, each webhook call gets a fresh `hook:<uuid>` session key. Override with `sessionKey` in the request body.

### Responses

Returns `{ status: "ok", sessionId: "..." }` on success, or error details.

### Security

- Always use auth tokens
- Restrict network exposure (bind to loopback or use Tailscale)
- Webhooks inherit the agent's tool permissions

---

## Gmail Pub/Sub

Connect Gmail inbox notifications to OpenClaw via Google Cloud Pub/Sub.

### Prerequisites

- Google Cloud project with Gmail API + Pub/Sub enabled
- Service account or OAuth credentials
- A Pub/Sub topic and push subscription

### Setup

```bash
# Wizard (recommended)
openclaw webhooks gmail setup

# Manual one-time setup
# 1. Create GCP Pub/Sub topic
# 2. Grant Gmail publish rights
# 3. Configure OpenClaw
```

### Start the Watch

```bash
openclaw webhooks gmail watch
```

### Run the Push Handler

Configure the push subscription to POST to your Gateway's webhook endpoint.

### Troubleshooting

| Problem | Fix |
|---|---|
| No notifications | Verify Pub/Sub subscription is active |
| Auth errors | Check service account permissions |
| Webhook not receiving | Ensure Gateway is accessible from GCP |

### Cleanup

```bash
openclaw webhooks gmail stop
```
