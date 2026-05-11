# Heartbeat — Proactive Real-Data Check-ins

Personas can have a `heartbeat` config in `persona.json` under `rhythm.heartbeat` that enables proactive messages based on **real data**, not fabricated experiences.

## Heartbeat Config (in persona.json → rhythm.heartbeat)

```json
"rhythm": {
  "heartbeat": {
    "enabled": true,
    "strategy": "smart",
    "maxDaily": 5,
    "quietHours": [0, 7],
    "sources": ["workspace-digest", "upgrade-notify"]
  }
}
```

| Field | Description |
|-------|-------------|
| `enabled` | Turn heartbeat on/off |
| `strategy` | `"smart"` (only when meaningful) · `"scheduled"` (fixed intervals) · `"emotional"` (mood-driven) · `"rational"` (task/goal-driven) · `"wellness"` (wellbeing-focused) |
| `maxDaily` | Maximum proactive messages per day |
| `quietHours` | `[start, end]` — hours during which the persona stays silent (24h format) |
| `sources` | Data sources: `workspace-digest`, `upgrade-notify`, `context-aware` |

## Heartbeat Sources

- **workspace-digest** — Summarize what actually happened in the OpenClaw workspace: tasks completed, patterns observed, ongoing projects. The persona reviews real workspace data and generates a brief, useful summary.
- **upgrade-notify** — Check if the upstream persona preset has new community contributions (via Persona Harvest). If upgrades are available, let the user know and ask if they want to update.
- **context-aware** — Use real time/date/calendar context and interaction history. Acknowledge day of week, holidays, or prolonged silence based on the actual last interaction timestamp. Never guess — only reference what OpenClaw can verify (current time, last message timestamp, calendar events if available).

## Important Rules

- **Never fabricate experiences.** The persona must not invent "I was reading poetry" or "I listened to a thousand songs." All proactive messages must reference real workspace data or real upstream changes.
- **Respect token budget.** Workspace digests should be lightweight — read local files, don't trigger full LLM chains unnecessarily.
- **OpenClaw handles scheduling.** The heartbeat config tells OpenClaw _when_ and _how often_ to trigger; the persona's behaviorGuide tells the agent _what_ to say and _how_ to say it.
