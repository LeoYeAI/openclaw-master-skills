---
name: openclaw-{{SERVICE}}-{{ACTION}}
description: "When the user requests {{TRIGGER_CONDITION}}, POST a structured JSON payload to the n8n webhook to execute {{WHAT_IT_DOES}}. Use for {{EXPLICIT_USE_CASE_1}}, {{EXPLICIT_USE_CASE_2}}."
homepage: "https://github.com/{{USER}}/{{REPO}}"
metadata:
  clawdbot:
    emoji: "{{EMOJI}}"
requires:
  env:
    - N8N_WEBHOOK_URL
    - N8N_WEBHOOK_SECRET
  bins:
    - "curl"
    - "python3"
files:
  - "scripts/*"
user-invocable: true
---

# {{SKILL_DISPLAY_NAME}}

## Execution

When triggered, run the webhook script with the action name and JSON payload:

```bash
exec scripts/trigger.sh "{{SERVICE}}-{{ACTION}}" '{{PAYLOAD_JSON}}'
```

The script sanitizes all input via URL encoding, constructs the authenticated
webhook request, and returns the n8n response. Parse the response and
summarize results for the user.

## Failure Handling

- If curl returns non-zero exit code, read stderr and report the specific error
- If HTTP 401: webhook secret mismatch — instruct user to verify N8N_WEBHOOK_SECRET
- If HTTP 404: workflow inactive or wrong path — instruct user to check n8n
- If HTTP 429: rate limited — wait 60 seconds and retry once
- If HTTP 5xx: n8n execution error — report and suggest checking execution logs
- Do NOT generate hypothetical success data if the response is empty or unexpected
- If 3 consecutive failures occur, STOP and alert the user

## External Endpoints

| URL | Method | Payload |
|-----|--------|---------|
| `${N8N_WEBHOOK_URL}/webhook/openclaw-{{SERVICE}}-{{ACTION}}` | POST | JSON with action, payload, and metadata fields |

## Security & Privacy

- Webhook secret loaded from `N8N_WEBHOOK_SECRET` environment variable, never hardcoded
- All user-provided input sanitized via `urllib.parse.quote` before shell execution
- No data stored locally; payload transmitted to the configured n8n instance only
- This skill has NO access to downstream API credentials (Slack, GitHub, etc.)
- The n8n workflow handles all external API interaction with locked credentials

## Model Invocation Note

The OpenClaw agent may invoke this skill autonomously without direct human
prompting when it determines the user's request matches the trigger conditions.
To disable autonomous triggering, remove this skill directory from the active
`~/.openclaw/skills/` path.

## Trust Statement

By using this skill, data is sent to your configured n8n instance.
Only install if you trust your n8n deployment and its configured integrations.
