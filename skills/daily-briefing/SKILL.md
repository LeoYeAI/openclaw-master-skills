---
name: daily-briefing
description: "Use when generating a morning briefing or daily summary. Pulls calendar, email, tasks, weather, and news into a concise daily hit."
version: 1.1.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [briefing, daily, morning, calendar, email, productivity, cron]
    related_skills: [google-workspace, himalaya]
---

# Daily Briefing

## Overview

A structured morning briefing that aggregates everything CAMML needs to start the day: calendar events, unread emails, pending tasks, weather, and relevant news. Designed to be run as a cron job or on-demand.

## When to Use

- User asks for a morning briefing or daily summary
- Setting up an automated daily cron job
- User asks "what's on my plate today?"
- Quick situational awareness needed

Don't use for:
- Single-source queries (just check calendar / just check email)
- Deep research on a topic (use deep-research skill)

## Briefing Structure

A daily briefing has these sections, in order:

```
DAILY BRIEFING — [Date, Day of Week]

1. WEATHER
2. CALENDAR
3. EMAIL TRIAGE
4. TASKS & REMINDERS
5. HEADLINES (optional)
6. THE ANGLE (Papi's take)
```

## Data Sources & Commands

### Weather

```bash
# Using wttr.in (no API key needed)
curl -s "wttr.in/?format=3"

# Full forecast
curl -s "wttr.in/?1QF"

# JSON format for programmatic use
curl -s "wttr.in/?format=j1" | jq '{temp: .current_condition[0].temp_C, desc: .current_condition[0].weatherDesc[0].value, feels: .current_condition[0].FeelsLikeC}'
```

### Calendar (Google Workspace)

Load the `google-workspace` skill first. Key commands:

```bash
# Today's events
gws calendar list --from today --to today

# This week's events
gws calendar list --from today --to "in 7 days"
```

### Email (Himalaya)

Load the `himalaya` skill first. Key commands:

```bash
# Unread count
himalaya envelope list --folder Inbox --filter "unseen" | head -20

# Quick scan of today's emails
himalaya envelope list --folder Inbox --filter "newer-than:1d" | head -30
```

### Tasks & Reminders

Check for:
- Open TODO items from the session todo tool
- GitHub issues assigned to the user
- Any `.hermes/plans/` that have pending items

```bash
# GitHub issues assigned to you
gh issue list --assignee @me --state open

# Pull requests needing review
gh pr list --search "review-requested:@me"
```

### Headlines

```bash
# Hacker News top stories — requires jq
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq '.[:5]' | jq -r '.[]' | while read id; do curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json" | jq -r '"\(.title) — \(.url // "https://news.ycombinator.com/item?id=\(.id)")"'; done

# FALLBACK: Python when jq not installed (common on WSL)
python3 -c "
import urllib.request, json
ids = json.loads(urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/topstories.json').read())[:5]
for id in ids:
    item = json.loads(urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{id}.json').read())
    print(f'• {item.get(\"title\", \"No title\")}')
"

# Alternative: quick web search for "top tech news today"
```

## Delivery: ntfy.sh Push Notifications

Free push notifications to your phone. No account needed.

**Setup (1 minute):**
1. Install the **ntfy** app on your phone (iOS/Android, free)
2. Subscribe to a topic (e.g., `papi-camml-briefing`)
3. Done. Any curl to that topic hits your phone instantly.

**Sending a notification:**
```bash
curl -s -H "Title: Daily Briefing" -H "Priority: default" \
  -d "$(echo 'BRIEFING TEXT HERE' | head -c 4000)" \
  https://ntfy.sh/papi-camml-briefing
```

**Priority levels:** `default` (normal), `high` (security scan with issues), `urgent` (critical findings)

**Alternative delivery:**
- **Email-to-SMS (Verizon):** `3303880025@vtext.com` — free, needs SMTP sender (msmtp + Gmail)
- **Telegram:** more formatting, needs bot setup
- **Discord:** push notifications, needs bot setup

## Cron Job Setup

To automate as a daily morning briefing:

```yaml
# Create via cronjob tool
schedule: "0 7 * * *"  # 7:00 AM daily
prompt: |
  Generate the daily briefing for CAMML.
  1. Fetch weather via: curl -s "wttr.in/?format=3"
  2. Check today's calendar events via gws
  3. Scan unread emails via himalaya (last 20)
  4. Check open GitHub issues assigned to CAMML
  5. Pull top 5 Hacker News headlines (use Python fallback if jq not installed)
  6. Format as a clean, concise briefing
  7. Add "The Angle" — your one-line take on what matters most today
  8. Push to ntfy.sh: curl -s -H "Title: Daily Briefing" -H "Priority: default" -d "$(echo 'BRIEFING' | head -c 4000)" https://ntfy.sh/papi-camml-briefing
enabled_toolsets: ["terminal", "web"]
```

## Phone Notification Delivery (ntfy.sh)

Free push notifications to phone — no account, no API key. Works for cron job delivery.

```bash
# Send notification (topic = papi-camml-briefing)
curl -s -H "Title: Daily Briefing" -H "Priority: default" \
  -d "Briefing content here" https://ntfy.sh/papi-camml-briefing

# Urgent priority (bypasses phone battery saver / DND)
curl -s -H "Title: Security Alert" -H "Priority: urgent" -H "Tags: warning" \
  -d "Critical finding" https://ntfy.sh/papi-camml-briefing
```

Setup: User installs ntfy app (iOS/Android), subscribes to the topic. That's it.

Alternative: Verizon email-to-SMS gateway (3303880025@vtext.com) — requires SMTP sender (msmtp + Gmail App Password). ntfy is simpler and free.

## Output Format

Keep it tight. No filler. Example:

```
DAILY BRIEFING — Monday, Apr 29

WEATHER
72°F, partly cloudy. Low 58°F tonight.

CALENDAR
• 9:00 AM — Team standup (Zoom)
• 11:30 AM — 1:1 with Sarah
• 2:00 PM — Sprint review

EMAIL (14 unread)
• 3 from client — project timeline questions (flag)
• AWS billing alert — usage spike
• Rest: newsletters, auto-generated

TASKS
• 4 open GitHub issues (2 assigned to you)
• 1 PR awaiting your review
• Pending: auth module refactor plan

HEADLINES
• Google announces Gemini 2.5 — hn
• Rust 1.78 released — hn
• OpenAI opens GPT-5 API — hn

THE ANGLE
The client emails about timeline are the priority. The AWS billing spike could be real — worth checking before standup so you've got answers.
```

## Delivery Options

Cron jobs can deliver to multiple targets. Free options for push notifications to your phone:

### Email-to-SMS (FREE — actual text messages, no accounts needed)

Every major carrier has a free email-to-SMS gateway. Send an email, it arrives as a text.

| Carrier | Format |
|---|---|
| AT&T | 5551234567@txt.att.net |
| T-Mobile | 5551234567@tmomail.net |
| Verizon | 5551234567@vtext.com |
| Sprint/T-Mobile | 5551234567@messaging.sprintpcs.com |
| US Cellular | 5551234567@email.uscc.net |
| Google Fi | 5551234567@msg.fi.google.com |

Full carrier list: see `references/carrier-sms-gateways.md`

Setup: configure himalaya or gws to send to `number@carrier-gateway`. Requires knowing the user's phone number and carrier. Ask for both.

### Telegram (FREE — best formatting, push notifications)

Best UX for briefings. Supports markdown, links, and instant push notifications. Requires:
1. Create bot via @BotFather (2 min, free)
2. Add bot token to Hermes gateway: `hermes gateway setup`
3. Set cron delivery to the Telegram chat

### ntfy.sh (FREE — open source push notifications)

No account needed. Install ntfy app, subscribe to a topic.
```bash
curl -d "Briefing ready" ntfy.sh/your-topic-name
```

### Discord (FREE)

Push notifications, already in Hermes config skeleton. Set up via `hermes gateway setup`.

### Paid Options

- **Twilio** — proper SMS API, free trial tier, then ~$0.0079/message
- **Vonage** — similar pricing

**Recommendation:** Email-to-SMS if you want actual texts. Telegram if you want better formatting and it's already set up. ntfy.sh if you want zero-config push notifications.

For full carrier gateway list and international carriers, see `references/carrier-sms-gateways.md`.

## Fallbacks for Missing Tools

When a tool isn't available, skip gracefully — don't let one missing source kill the whole briefing.

| Tool Missing | Fallback |
|---|---|
| `jq` | Use Python: `python3 -c "import urllib.request, json; ..."` |
| `gws` | Skip calendar section, note it's not configured |
| `himalaya` | Skip email section, note it's not configured |
| `gh` | Skip GitHub tasks, note it's not configured |
| `curl` blocked | Needs `hermes config set approvals.mode smart` — routine API calls shouldn't require manual approval |

### Hacker News without jq

```bash
# Python fallback for HN headlines
python3 -c "
import urllib.request, json
ids = json.loads(urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/topstories.json').read())[:5]
for id in ids:
    item = json.loads(urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{id}.json').read())
    print(f'• {item.get(\"title\", \"No title\")}')
"
```

## Common Pitfalls

1. **Overloading the briefing.** This is a briefing, not a report. 3-5 bullets per section max. If something needs deep attention, flag it — don't expand it.

2. **Failing silently on missing tools.** If gws or himalaya isn't configured, skip that section gracefully. Don't let one missing source kill the whole briefing.

3. **Stale cron jobs.** If you set up a cron job, test it once manually before walking away. Verify the delivery target is correct.

5. **Ignoring timezone.** Calendar events and cron schedules should match CAMML's timezone. Ask if unsure.

5. **Too many headlines.** 5 is the cap. Nobody needs 20 headlines at 7 AM.

6. **jq not installed.** On WSL and minimal Linux installs, jq is often missing. Always have the Python urllib fallback ready for HN headlines.

7. **API calls blocked by approval settings.** wttr.in and HN API calls may get blocked by `approvals.mode: manual`. Run `hermes config set approvals.mode smart` so routine API calls auto-approve.

7. **Approval settings blocking API calls.** If `curl` to weather/HN APIs gets blocked, the briefing dies silently. Either set `approvals.mode: smart` or ensure the cron job runs with `--yolo` flag or appropriate toolset permissions.

8. **ntfy message too long.** ntfy has a ~4000 char limit per message. If the briefing is long, truncate or split into title + body.

## Verification Checklist

- [ ] All available data sources queried
- [ ] Missing sources handled gracefully (skipped, not errored)
- [ ] Briefing formatted per the structure above
- [ ] "The Angle" provides genuine prioritization, not generic advice
- [ ] Total briefing fits in one screen (under 40 lines)
