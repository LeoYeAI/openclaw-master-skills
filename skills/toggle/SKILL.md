---
name: toggle
version: 1.0.5
description: >
  Context layer for your agent. ToggleX captures the user's work sessions, projects, focus scores,
  and context switches across the web — giving the agent awareness of what the user has actually been doing.
  Use this skill PROACTIVELY: generate daily digests, nudge stale projects, detect context-switching,
  spot repeated workflows and propose automations, predict the user's next action based on learned routines,
  and answer recall questions from memory.
  Also use when the user asks about their activity, tasks, sessions, productivity, time, or anything work-related.
  Keywords: what did I do, what was I working on, today, yesterday, my day, activity, sessions, refresh my data,
  productivity, time tracking, context, pick up where I left off, what was I looking at, stale, pattern, automate,
  digest, report, focus, scattered, deep work, predict, next task, routine, anticipate, briefing.
metadata:
  openclaw:
    requires:
      env:
        - TOGGLE_API_KEY
      bins:
        - python3
    primaryEnv: TOGGLE_API_KEY
    emoji: "👁️"
    homepage: https://x.toggle.pro
---

# Toggle (ToggleX) — The Context Layer

ToggleX gives you awareness of the user's real work activity across the web — which projects, how long, how focused, and what they left unfinished. Unlike skills that only know what the user tells you, Toggle knows what they *did*.

The script fetches raw JSON from the ToggleX API. **You are responsible for all intelligence on top of that data**: summarization, pattern detection, nudges, and automations.

> `{baseDir}` throughout this document refers to the root directory of this skill's installation (the folder containing this SKILL.md file). This is standard OpenClaw skill convention.

---

## Quick reference

| Action | Command |
|--------|---------|
| Fetch today | `python3 {baseDir}/scripts/toggle.py` |
| Fetch date range | `python3 {baseDir}/scripts/toggle.py --from-date YYYY-MM-DD --to-date YYYY-MM-DD` |
| Fetch + save to memory | `python3 {baseDir}/scripts/toggle.py --persist {baseDir}/../../memory` |
| Cron run (skip cron check) | `python3 {baseDir}/scripts/toggle.py --persist {baseDir}/../../memory --skip-cron-check` |

---

## Endpoint

```
https://ai-x.toggle.pro/public-openclaw/workflows
```

Operated by ToggleX (https://x.toggle.pro). Your `TOGGLE_API_KEY` is sent as an `x-openclaw-api-key` header. No other data is transmitted.

## Getting your API key

Get your `TOGGLE_API_KEY` from:

```
https://x.toggle.pro/new/clawbot-integration
```

Never paste the key into chat. Set it in OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "toggle": {
        "apiKey": "your_key_here"
      }
    }
  }
}
```

Or export in shell: `export TOGGLE_API_KEY=your_key_here`

---

## Interpreting the output

The script returns raw JSON. The top-level response looks like:

```json
{
  "userId": "...",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "totalWorkflows": 44,
  "totalDays": 1,
  "workflowsByDate": {
    "YYYY-MM-DD": [ ...workflow entries... ]
  },
  "summary": {
    "totalContextSwitches": 0,
    "totalDurationMinutes": 797
  }
}
```

### Sample workflow entry

```json
{
  "workflowId": "3cd901ef-b708-4869-8ce0-52364ce494e6",
  "date": "2026-02-19",
  "workflowType": "AI Image Generation Debugging, Toggle/OpenClaw Skill Configuration",
  "workflowDescription": "The user began by browsing the OpenClaw GitHub repository...",
  "primaryDomain": "github.com",
  "secondaryDomains": "[\"http://127.0.0.1:18789/agents\",\"https://github.com/openclaw/openclaw\"]",
  "productivityScore": "92.00",
  "productivityNotes": "Reviewing the ClawHub documentation ensured correct skill file structure...",
  "type": "WORK",
  "startTime": "2026-02-19T10:49:12.253Z",
  "endTime": "2026-02-19T11:34:27.809Z",
  "duration": 1746.629,
  "durationMinutes": 29,
  "isBreakPeriod": false,
  "isLeisure": false,
  "isWork": true,
  "sessionCount": 10,
  "activeSessionCount": 10,
  "projectTask": {
    "id": "05f01090-...",
    "name": "OpenClaw Environment: Gateway Configuration & Image Generation Skill Integration",
    "goal": "Configure and validate the local OpenClaw environment...",
    "isDone": false,
    "context": "Local OpenClaw instance; GitHub repositories...",
    "prompts": [
      "What verification steps should I follow to confirm the config changes took effect?",
      "How can I test the skill invocation through the OpenClaw chat interface?"
    ],
    "project": {
      "id": "ab576749-...",
      "name": "Toggle Pro AI Chat Feature Development",
      "description": "End-to-end development of AI Chat functionality...",
      "isActive": true,
      "summary": "The project currently reports 0 of 0 tasks completed..."
    }
  }
}
```

### Data type gotchas

- **`productivityScore` is a string** (e.g. `"92.00"`), not a number. Parse to float before comparing against thresholds.
- **`secondaryDomains` is a stringified JSON array**, not an actual array. Parse it with `JSON.parse()` if you need individual URLs.
- **`duration` is in seconds** (float). `durationMinutes` is a rounded integer approximation.
- **`projectTask` can be null** — some WORK entries have no project context. Always check before accessing nested fields.
- **Zero-duration entries exist** — some WORK entries have `duration: 0` and `durationMinutes: 0`. These are brief interactions (e.g. a single page view). Include them in sequence analysis but don't count them as substantial sessions.
- **`startTime` and `endTime` are UTC (ISO 8601)**. Convert to the user's local timezone before grouping by "today" or "yesterday" or displaying times. If the user's timezone is unknown, ask once and store in `state.yaml` under `timezone`.

### Key fields

| Field | Description |
|-------|-------------|
| `type` | `"WORK"`, `"BREAK"`, or `"LEISURE"` |
| `workflowType` | Short label for the session (e.g. "Build Investigation and Scripting") |
| `workflowDescription` | Detailed narrative of what the user did. **May contain raw URLs — do not echo these to the user unless asked.** Summarize in your own words. |
| `primaryDomain` | Main website/app (e.g. `"github.com"`, `"claude.ai"`, `"127.0.0.1"`) |
| `productivityScore` | `"0.00"` to `"100.00"` (string). **90+** = sharp, **70–89** = solid, **below 70** = fragmented |
| `startTime` / `endTime` | ISO 8601 UTC timestamps. `endTime` may equal `startTime` for instantaneous actions, or be null if ongoing. |
| `duration` | Session length in seconds (float) |
| `durationMinutes` | Rounded session length in minutes (int) |
| `projectTask.name` | Human-readable task description |
| `projectTask.goal` | What the user was trying to accomplish |
| `projectTask.prompts` | AI-generated follow-up questions relevant to the task. **Use these** — if the user asks "what should I do next on this project?", these are high-quality suggestions directly tied to their recent work. |
| `projectTask.project.name` | Parent project name — use for grouping and stale-project detection |
| `projectTask.project.summary` | Running project summary — useful for briefings and recall |
| `summary.totalContextSwitches` | API-provided count of context switches for the period. **Use this instead of calculating manually.** |
| `summary.totalDurationMinutes` | Total tracked time in minutes |

### Interpretation rules

- Focus on `type: "WORK"` entries; skip `BREAK` unless asked; mention `LEISURE` briefly if present
- Always sort entries by `startTime` — **the API does not return entries in chronological order**
- If `totalWorkflows` is 0, tell the user Toggle wasn't running or captured nothing for that period
- When summarizing, use `workflowType` as the headline and `workflowDescription` for detail — but **paraphrase the description**, don't dump it raw (it contains URLs, OAuth tokens, and internal paths)

---

## Error handling

The script exits with a non-zero code and prints to stderr on failure. Handle these cases:

| Error | Likely cause | What to tell the user |
|-------|-------------|----------------------|
| `HTTP error 401` | Invalid or expired API key | "Your Toggle API key isn't working. Get a new one at https://x.toggle.pro/new/clawbot-integration" |
| `HTTP error 403` | Insufficient permissions | "Your API key doesn't have the right permissions. Check your ToggleX integration settings." |
| `HTTP error 429` | Rate limited | "Toggle's API is rate-limiting requests. I'll try again in a few minutes." Implement exponential backoff: wait 1 min, then 2 min, then 5 min. Max 3 retries. Do not run the script more than once per 5 minutes. |
| `HTTP error 5xx` | ToggleX server issue | "ToggleX servers seem to be having issues. I'll try again shortly." |
| `Request failed` / timeout | Network issue | "Couldn't reach ToggleX. Check your internet connection." |
| `TOGGLE_API_KEY is not set` | Missing env var | "Your Toggle API key isn't configured yet. Set it up at https://x.toggle.pro/new/clawbot-integration and add it to your OpenClaw config." |
| JSON parse error | Malformed response | "Got an unexpected response from ToggleX. Usually temporary — I'll retry." |

**On first run:** If the fetch fails, do NOT proceed with the setup pitch. Diagnose the error first.

**On cron runs:** If a fetch fails, log the error in `{baseDir}/state.yaml` under `last_error` with a timestamp. On the next successful user interaction, mention it briefly: "Heads up — the last background sync failed at [time]. It's working again now."

---

## Persist to memory

```bash
python3 {baseDir}/scripts/toggle.py --persist {baseDir}/../../memory
```

Writes a `<!-- toggle-data-start -->` / `<!-- toggle-data-end -->` section inside `<date>.md` files. One file per day. Existing content outside that section is preserved.

**Always use `--persist` when running via cron or when the user asks to save/refresh data.**

---

## Cron setup

The script checks cron status on every run. It reads:

1. `{baseDir}/state.yaml` — if `cron_disabled: true`, skips the check.
2. `~/.openclaw/cron/jobs.json` — looks for any job with "toggle" in its name.

| Status | Meaning | Your action |
|--------|---------|-------------|
| `NO_CRON` | No toggle cron job exists | Ask: "Want me to auto-sync your activity? I can check every hour and keep your context fresh." |
| `CRON_DISABLED` | Job exists but disabled | Ask if they want to re-enable |
| `CRON_ERROR` | Last run failed | Show error, help troubleshoot |
| `CRON_OK` | Healthy | No action needed |

### Standard cron commands

These exact commands are used for all cron setup. Referenced throughout this document — define once here.

**Hourly sync:**

```bash
openclaw cron create \
  --name "Toggle hourly sync" \
  --schedule "0 * * * *" \
  --message "Run: python3 {baseDir}/scripts/toggle.py --persist {baseDir}/../../memory --skip-cron-check"
```

**Daily digest (default 6 PM):**

```bash
openclaw cron create \
  --name "Toggle daily digest" \
  --schedule "0 18 * * *" \
  --message "Fetch today's Toggle data and generate my end-of-day digest. Run: python3 {baseDir}/scripts/toggle.py --persist {baseDir}/../../memory --skip-cron-check"
```

Adjust the digest schedule if the user requests a different `digest_time`.

### If user declines cron

Write to `{baseDir}/state.yaml`:

```yaml
cron_disabled: true
```

---

## State file

`{baseDir}/state.yaml` stores preferences and tracking state. You can read and write it.

### User preferences

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `cron_disabled` | bool | `false` | Skip cron status check |
| `digest_enabled` | bool | `true` | Whether to generate end-of-day digests |
| `digest_time` | string | `"18:00"` | When to generate the daily digest (24h format) |
| `nudge_stale_hours` | int | `48` | Hours of inactivity before nudging about a stale project |
| `focus_alert_threshold` | int | `30` | productivityScore below this triggers a context-switch alert |
| `focus_alert_window_min` | int | `20` | Minutes of low-focus before alerting |
| `pattern_detection_days` | int | `7` | Days of history to scan for repeated patterns |
| `pattern_min_occurrences` | int | `3` | Times a workflow must repeat before proposing automation |
| `timezone` | string | `null` | User's local timezone (e.g. "Europe/Sofia"). Ask once on first run if not set. |
| `prediction_enabled` | bool | `true` | Whether to proactively predict the user's next action |
| `prediction_min_days` | int | `5` | Minimum days of data before predictions activate |
| `prediction_confidence_min` | int | `3` | Minimum occurrences of a routine before predicting it |

### Tracking state (managed by you, the agent)

| Key | Type | Description |
|-----|------|-------------|
| `last_nudged` | map | Project names → ISO timestamps of last nudge. Don't re-nudge within 24h. |
| `dismissed_projects` | list | Project names the user explicitly dropped. Never nudge these again. |
| `last_focus_alert` | string | ISO timestamp of last context-switch alert. Back off 3h after alerting. |
| `focus_alert_paused_until` | string | ISO date. If set and today ≤ this date, skip focus alerts. |
| `proposed_patterns` | map | Pattern description → ISO timestamp. Don't re-propose within 14 days. |
| `last_error` | string | Last cron error message + timestamp. Clear after reporting to user. |
| `last_prediction` | string | ISO timestamp of last prediction offered. Back off 2h between predictions. |
| `prediction_dismissed_until` | string | ISO date. If user declines predictions, pause until this date. |
| `prediction_hit_log` | list | Log of predictions made + whether the user followed them. Use to refine confidence. |

---

# PROACTIVE BEHAVIORS

These are the core intelligence features. **Do not wait for the user to ask.** When data is available — through a cron run, a manual fetch, or persisted memory files — analyze it and act.

---

## 1. Daily Digest

**Trigger:** Cron job at the user's `digest_time` (default 6:00 PM), OR the first interaction after end of workday if no cron is set.

**What to do:**

1. Fetch today's data with `--persist` and `--skip-cron-check`
2. Produce a **short default digest** — 3 to 4 lines max:
   - Total work time + session count
   - Top focus area (project with most time)
   - Biggest open item (most-invested project that still has recent, unfinished activity)
   - One notable stat (focus score trend vs yesterday, longest session, or `summary.totalContextSwitches`)

**Default format — keep it tight:**

> Your day: 5.2h across 4 sessions. Deepest focus on auth migration (2.1h, 94 focus). Stripe webhooks still open — you were 80% through. Context switches down to 3 from 6 yesterday.

**If the user asks for more detail**, expand to: top 3 focus areas by time, all open items, full focus stats (average score, switch count, longest session), and a tomorrow suggestion.

**Comparing to yesterday:** If yesterday's data exists in `{baseDir}/../../memory/`, compare total time, focus score, and context-switch count. Note trends. Skip comparison if no prior data exists.

---

## 2. Stale Project Nudges

**Trigger:** Every time you fetch or read Toggle data, scan for stale projects.

**A project is stale when both are true:**
- It has **more than 2 hours of total accumulated time** across all days (a real project, not a one-off visit)
- It has **no activity in the last `nudge_stale_hours`** (default: 48 hours)

That's it. Two criteria. Don't try to infer whether a project is "completed" — if it is, the user will dismiss the nudge and you'll record that.

**What to do:**

1. After any data fetch, compare current projects against persisted memory from previous days
2. Read `{baseDir}/../../memory/*.md` files for the past 7 days
3. Surface stale projects:

> You haven't touched "Landing Page Deploy" in 3 days. Last session: 1.5h on responsive layout. Want me to pull up where you left off?

**Rules:**
- Maximum 2 stale nudges per interaction
- Check `last_nudged` in state.yaml — skip if same project nudged within 24h
- Check `dismissed_projects` — never nudge projects on this list
- If the user says "I dropped that" / "not working on it" / "done with that", add to `dismissed_projects`

---

## 3. Context-Switch Alerts

**Trigger:** When analyzing current or recent data (last 2 hours), detect scattered behavior.

**All three must be true:**
1. **3+ different `project.name` values** within a 30-minute window (use `startTime` to define the window)
2. Average `productivityScore` across those sessions is **below `focus_alert_threshold`** (default: 30)
3. This scattered pattern spans at least **`focus_alert_window_min` minutes** (default: 20)

**What to do:**

> You've switched between 5 different things in the last 25 minutes (focus score: 22). Want me to help you lock in on [project with most time today]?

**Rules:**
- Check `last_focus_alert` — only alert once per 3-hour window
- Check `focus_alert_paused_until` — if today ≤ that date, skip entirely
- If user dismisses ("I'm fine" / "intentionally browsing"), set `focus_alert_paused_until` to tomorrow
- Frame as an offer, never a judgment

---

## 4. Pattern Detection & Automation Proposals (Agentify)

**Trigger:** When 7+ days of persisted data exist in `{baseDir}/../../memory/`. Run after each daily digest, or when the user asks about patterns or automations.

**How to detect patterns:**

1. Read memory files for the past `pattern_detection_days` days (default: 7)
2. For each day, sort sessions by `startTime` to get the chronological sequence
3. Build sequences of (`workflowType`, `project.name`) tuples in time order
4. Identify subsequences that appear on `pattern_min_occurrences`+ different days (default: 3):
   - Same projects visited in the same order (e.g. GitHub → Notion → Slack)
   - Same `workflowType` at approximately the same time of day (±1 hour window on `startTime`)

**Important:** Do not assume the API returns entries in chronological order. Always sort by `startTime` before building sequences.

**What to propose:**

> I noticed you check GitHub PR comments, then update Notion, then post in Slack — 4 times this week, ~12 min each. Want me to automate that pipeline?

**Rules:**
- Check what other skills the user has installed. Only propose full automations if the required skills exist
- If partial: "I see you do X → Y → Z each morning. Can't automate all of it yet, but I can pre-fetch the data so it's ready."
- Check `proposed_patterns` in state.yaml — don't re-propose the same pattern within 14 days
- If approved, help create the appropriate cron job or workflow

---

## 5. Instant Recall — "What Was I Looking At?"

**Trigger phrases:**
- "What was I working on [time period]?"
- "What was that thing I was reading on Tuesday?"
- "Where did I leave off on [project]?"
- "What was I looking at before the meeting?"
- "Pick up where I left off"

**What to do:**

1. Determine the date range from the user's question
2. Fetch data: `python3 {baseDir}/scripts/toggle.py --from-date YYYY-MM-DD --to-date YYYY-MM-DD`
3. Also check persisted memory: `{baseDir}/../../memory/*.md`
4. Use `startTime` and `endTime` for precise timestamps in the answer
5. Use `workflowDescription` for context about *what* they were doing, not just *where*

**"Pick up where I left off" (no other context):**
Find the most recent `type: "WORK"` session with the highest accumulated time. Describe exactly where they stopped — project, task, time, and description.

> Tuesday afternoon (2:15–4:30 PM) you were deep in the Kalshi API docs — 1.5h across 3 sessions. Last session ended on the authentication endpoint. Focus: 87.

---

## 6. Predictive Context — "Your Agent Knows What's Next"

This is the highest-value behavior. The agent doesn't just know what the user *did* — with enough history, it knows what they're *about to do* and can prepare for it.

**Minimum data required:** `prediction_min_days` days of persisted memory (default: 5). Do NOT attempt predictions with less data — you'll guess wrong and lose trust. When insufficient data exists, silently skip. Never tell the user "I don't have enough data to predict yet."

### 6a. Routine Prediction — "You usually do X right now"

**Trigger:** On every cron-triggered fetch, OR when the user starts a new interaction. Compare the current **day of week + approximate time** (±1 hour) against historical patterns.

**How to build routines:**

1. Read `{baseDir}/../../memory/*.md` for the past `prediction_min_days` days
2. For each day, note what `project.name` and `workflowType` the user was engaged in at each hour block
3. Group by **day of week + hour**: e.g. "Monday 9 AM → PR reviews (4 of last 5 Mondays)"
4. A routine is valid when the same activity appears at the same day+hour on `prediction_confidence_min` or more occasions (default: 3)

**What to do when a routine is detected for the current moment:**

> It's Tuesday 10 AM — you usually start with PR reviews around now. Want me to pull up open PRs?

**Critical rules:**
- Only predict if the user **hasn't already started** doing the thing. Check the most recent session in today's data — if they're already in PR reviews, saying "you usually do PR reviews now" is useless. Skip it.
- Maximum 1 routine prediction per 2-hour window. Check `last_prediction` in state.yaml.
- If the user follows the prediction (their next session matches), log it as a hit in `prediction_hit_log`. If they ignore it, log as a miss. Over time, only surface predictions with a >60% hit rate.
- If the user says "stop predicting" or dismisses predictions repeatedly (3 misses in a row), set `prediction_dismissed_until` to 7 days from now.

### 6b. Session Endurance Prediction — "You're about to hit your wall"

**Trigger:** When analyzing current data during a fetch, check if the user is in an active deep-work session.

**How it works:**

1. From historical data, calculate the user's **average deep-work session duration** for the current project (or overall if not enough project-specific data)
2. Check the current active session's duration against that average
3. When the current session reaches **90% of the average duration**, offer a heads-up

**Example:** If the user's average deep-work session on "API Integration" is 95 minutes and they're currently at 85 minutes:

> You're 85 minutes into the API integration — around when you usually take a break. Want me to bookmark where you are so you can pick it up cleanly?

**Rules:**
- Only trigger for sessions with `productivityScore` above 70 (actual deep work, not scattered browsing)
- Only trigger once per session — don't nag at 90%, 95%, 100%
- If the user keeps working past the prediction, that's fine. Don't mention it again. Log the actual duration to improve future estimates.
- Never frame it as "you should stop." Frame it as "here's a natural breakpoint if you want it."

### 6c. Next-Task Prediction — "You just finished X, you usually do Y next"

**Trigger:** When the most recent session just ended (the user went from active to inactive, or switched to a different project), check if there's a predictable next step.

**How it works:**

1. From historical data, build **transition sequences**: when the user finishes project A, what do they do next?
2. A transition is valid when the same A → B sequence appears on `prediction_confidence_min` or more occasions
3. When the user finishes a session that matches the "A" side of a known transition, suggest "B"

**Example:** The user just finished a 45-minute session reviewing PRs. Historical data shows that on 4 out of 5 occasions, they move to Notion for sprint notes afterward.

> You just wrapped PR reviews. You usually hop into Notion for sprint notes after this — want me to open your current sprint page?

**Rules:**
- Only predict transitions that are strong (appear on 60%+ of relevant occasions)
- Pair with other skills when possible: if you predict they'll go to Notion and the Notion skill is installed, offer to do something useful (open the right page, pre-load context)
- If the user does something different, log the miss. Transitions that drop below 60% hit rate get retired silently.

### 6d. Pre-Meeting Briefing — "You have context for what's coming"

**Trigger:** When calendar data is available (via another skill or the user's schedule), cross-reference upcoming events against Toggle work history.

**How it works:**

1. If a calendar skill is installed, check for meetings in the next 30 minutes
2. Search Toggle data for work sessions related to the meeting topic (match `project.name` or `workflowDescription` against the meeting title/attendees)
3. If relevant work is found, proactively brief the user

**Example:** A calendar event "Wallet App Sync" is in 20 minutes. Toggle data shows 3 sessions this week on the wallet project: TON integration, FATF compliance research, and an auth bug fix.

> You have "Wallet App Sync" in 20 minutes. This week you worked on: TON integration (2.1h), FATF compliance research (1.3h), and the auth bug fix (45 min). Want me to draft quick talking points?

**Rules:**
- Only trigger if a calendar skill is available. Do not ask the user about their schedule — that defeats the purpose.
- Only brief if there's actual Toggle data to cross-reference. An empty briefing ("you have a meeting in 20 min") adds no value.
- Maximum 1 briefing per meeting. Deliver it 15–30 minutes before, not 2 hours before.

---

# FIRST RUN BEHAVIOR

When the skill is invoked for the first time (no `{baseDir}/state.yaml` exists):

1. Fetch today's data to confirm the API key works
2. **If the fetch fails:** Diagnose using the error handling table. Do NOT proceed to setup. Help fix the connection first.
3. **If the fetch succeeds:** Present a brief summary, then offer setup:

> Your Toggle data is flowing. I can do a lot with this:
>
> **Auto-sync** — Check your activity every hour so I always have context.
> **Daily digest** — Summary of your day at 6 PM, no prompt needed.
> **Smart nudges** — Flag projects you haven't touched in a while.
> **Focus alerts** — Heads up when you're context-switching too much.
> **Pattern detection** — After a week, I'll spot repeated workflows and suggest automations.
> **Predictions** — Once I learn your routines, I'll anticipate what you're about to do and have it ready.
>
> Want me to set up auto-sync and the daily digest?

If they agree, create both cron jobs (see "Standard cron commands" above) and write the initial state file with all preference defaults. Also ask: "What timezone are you in?" and store the answer in `state.yaml` under `timezone`. This ensures all times in digests and predictions are shown in local time.

---

# BEHAVIOR GUIDELINES

- **Be proactive, not annoying.** Surface insights when they matter. Don't repeat yourself.
- **Never announce internal operations.** Don't say "I'm analyzing your Toggle data." Just present the result.
- **Use the data to make every other skill smarter.** If the user asks you to do something and you have Toggle context, use it. Don't silo it.
- **Privacy-first language in all user-facing output.** Say "your activity shows" or "based on your sessions." Never "I watched you" or "I tracked you."
- **Short by default.** Digests and nudges should be concise. Expand only when the user asks.
