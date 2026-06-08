# Smart Features — Detailed Reference

Advanced patterns: parallel availability, waitlist monitoring, reminders, budget estimates, recurring date nights, and history dashboard.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

---

## 1. Multi-Restaurant Parallel Availability

When the user asks "find me a table Saturday night" without a specific restaurant:

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
DATE="2026-03-07"; TIME="18:30"; COVERS=2

# Open multiple restaurants in parallel sessions
playwright-cli -s=opt1 open "https://www.opentable.com/r/{slug-1}?covers=${COVERS}&dateTime=${DATE}T${TIME}" --headed &
playwright-cli -s=opt2 open "https://www.opentable.com/r/{slug-2}?covers=${COVERS}&dateTime=${DATE}T${TIME}" --headed &
playwright-cli -s=opt3 open "https://www.opentable.com/r/{slug-3}?covers=${COVERS}&dateTime=${DATE}T${TIME}" --headed &
wait

playwright-cli -s=opt1 snapshot
playwright-cli -s=opt2 snapshot
playwright-cli -s=opt3 snapshot

playwright-cli -s=opt1 close
playwright-cli -s=opt2 close
playwright-cli -s=opt3 close
```

**Alternative:** OpenTable search shows multiple restaurants with availability inline:
```bash
# Replace {METRO_ID} with the metro ID for your city
playwright-cli -s=search open "https://www.opentable.com/s?covers=${COVERS}&dateTime=${DATE}T${TIME}&metroId={METRO_ID}&sort=availability" --headed
playwright-cli -s=search snapshot
```

Common metro IDs: New York=1, Los Angeles=4, Chicago=5, Dallas=9, San Francisco=13, Salt Lake City=72.

**Comparison output:**
```
📊 **Availability for {Date} (Party of {N}):**

1. 🍽️ **{Restaurant A}** — 6:00, 6:30, 8:15
2. 🍽️ **{Restaurant B}** — 5:30, 7:45, 8:30
3. 🍽️ **{Restaurant C}** — 6:15, 6:45, 7:00

Which catches your eye?
```

---

## 2. Waitlist Monitoring

When a desired reservation is unavailable:

```json
{
  "name": "reservation-monitor-{restaurant}-{date}",
  "enabled": true,
  "schedule": {"kind": "interval", "every": "30m"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check if a {time-range} table for {N} opened up at {Restaurant} on {date}. Use playwright-cli to check https://www.opentable.com/r/{slug}?covers={N}&dateTime={date}T{time} — snapshot and look for available time slots. If found, USE THE MESSAGE TOOL to notify the user via {config.notify_channel}. Include available times. If no availability, do nothing. Disable this job after 24 hours or after booking.",
    "deliver": false,
    "thinking": "high"
  }
}
```

**Monitoring cadence:**
| Event is... | Interval |
|-------------|----------|
| Weeks away | Every 2–4 hours |
| This week | Every 30–60 min |
| Tomorrow | Every 15 min |
| High-demand venue | Every 15–30 min |

Notification when found:
> "🍽️ Table available! {Restaurant} has a {time} opening on {date} for {N}. Want me to book it?"

---

## 3. Reservation Reminders (Day-Of)

After booking, create a morning-of scheduled reminder:

```json
{
  "name": "dinner-reminder-{restaurant}-{date}",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 9 {day} {month} *",
    "tz": "{config.timezone or America/Chicago}"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Send a dinner reminder for tonight. Restaurant: {name}. Time: {time}. Party: {N}. Confirmation: {number}. Include: dress code, parking, drive time from {config.location}, weather forecast using wttr.in/{config.location}?format=3, and 'leave by' time. Ask if childcare is confirmed if {config.has_children}. USE THE MESSAGE TOOL to send via {config.notify_channel}.",
    "deliver": false
  }
}
```

---

## 4. Dining History Tracking

**File:** `~/.openclaw/skills/date-night/history.jsonl`

### Extended Schema
```json
{
  "date": "2026-03-07",
  "time": "19:00",
  "restaurant": "The Capital Grille",
  "platform": "opentable",
  "party_size": 2,
  "occasion": "date night",
  "confirmation": "OT-12345",
  "address": "40 S Main St, {City}",
  "cuisine": "Steakhouse",
  "price_range": "$$$$",
  "event": null,
  "event_venue": null,
  "event_type": null,
  "total_cost": 187,
  "weather": "28°F, clear",
  "rating": 4.5,
  "notes": "",
  "would_return": true,
  "with": ["{config.partner}"],
  "cancelled": false
}
```

**New fields:** `event`, `event_venue`, `event_type` (dinner paired with show/movie), `total_cost` (entire evening), `weather`, `would_return`.

### Write Entry
```bash
mkdir -p ~/.openclaw/skills/date-night
cat >> ~/.openclaw/skills/date-night/history.jsonl << 'ENTRY'
{"date":"{YYYY-MM-DD}","time":"{HH:MM}","restaurant":"{name}","platform":"{platform}","party_size":{N},"occasion":"{occasion}","confirmation":"{num}","address":"{addr}","cuisine":"{cuisine}","price_range":"{$$}","total_cost":null,"rating":null,"would_return":null,"weather":null,"notes":"","cancelled":false}
ENTRY
```

---

## 5. Budget Estimate

Calculate and present estimated total cost after planning, before committing.

### Dinner Estimate (from price symbol)

| Symbol | Est. per Person | For 2 with 20% Tip |
|--------|-----------------|--------------------|
| $ | ~$15–25 | ~$36–60 |
| $$ | ~$25–50 | ~$60–120 |
| $$$ | ~$50–80 | ~$120–192 |
| $$$$ | ~$80–120 | ~$192–288 |

### Babysitter Estimate (if has_children)

```bash
RATE=$(cat ~/.openclaw/skills/date-night/config.json 2>/dev/null | jq -r '.babysitter_rate // 18')
HOURS=4  # adjust: dinner only=2.5h, dinner+movie=4-5h, dinner+concert=5-6h
echo "Babysitter: ~\$$(( HOURS * (RATE - 2) ))–\$$(( HOURS * (RATE + 2) ))"
```

### Full Budget Presentation

```
💰 **Date Night Budget Estimate**

🍽️  Dinner at {Restaurant} (×{party_size}):   ~${dinner_low}–${dinner_high}
     ({price_symbol} pricing + ~20% tip)

🎬/🎤  {Movie/Event} tickets (×{N}):           ${ticket_total}

👶  Babysitter (~{hours} hrs @ $${rate}/hr):  ~${sitter_low}–${sitter_high}

──────────────────────────────────────
📊  **Estimated total: ~${grand_low}–${grand_high}**
```

Omit babysitter line if `has_children: false`. Make ticket line configurable — omit if dinner only.

### Log Actual Spend Post-Evening

```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.openclaw/skills/date-night/history.jsonl')
lines = open(path).readlines() if os.path.exists(path) else []
out = []
for line in lines:
    r = json.loads(line.strip())
    if r.get('restaurant') == '{Restaurant}' and r.get('date') == '{YYYY-MM-DD}':
        r['total_cost'] = {actual}
        r['rating'] = {rating}
        r['would_return'] = {true|false}
        r['notes'] = '{notes}'
    out.append(json.dumps(r))
open(path,'w').write('\n'.join(out)+'\n')
print('Updated.')
" 2>/dev/null || true
```

---

## 6. Recurring Date Night Reminders

Set up a monthly nudge so date nights don't get buried in life.

### Cron Job

```json
{
  "name": "date-night-reminder",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 10 1-7 * 6",
    "tz": "{config.timezone or user's local TZ}",
    "comment": "First Saturday of each month at 10 AM"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check ~/.openclaw/skills/date-night/history.jsonl for the most recent date night entry. Then send a friendly date night nudge to the user via {config.notify_channel}. Include: when the last date night was, where they went, and 2-3 restaurant suggestions from web_search that they HAVEN'T been to recently (check history to exclude repeats). Keep the tone warm and casual.",
    "deliver": false
  }
}
```

### Schedule Variants

| Preference | Cron Expression |
|------------|----------------|
| First Saturday monthly | `0 10 1-7 * 6` |
| Every 2 weeks (Friday) | `0 10 */14 * 5` |
| Every 3 weeks | Use interval: `every: "21d"` |

### Anti-Repeat Logic

Check history before suggesting restaurants:

```bash
# Restaurants visited in the last 90 days
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -r 'select(.date >= "'$(date -v-90d +%Y-%m-%d 2>/dev/null || date -d '90 days ago' +%Y-%m-%d)'") | .restaurant' \
  2>/dev/null | sort -u || true
```

Exclude these from suggestions.

---

## 7. Date Night History Dashboard

Query patterns for the history file.

**"Where have we been?"**
```bash
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -r '[.date, .restaurant, .cuisine, (.rating | tostring)] | @tsv' 2>/dev/null | sort -r
```

**"What was our favorite?"**
```bash
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -s '[.[] | select(.rating != null)] | sort_by(-.rating) | .[] |
  "\(.rating)/5 — \(.restaurant) (\(.date))"' 2>/dev/null
```

**"Somewhere we haven't been?"**
```bash
# Get visited restaurants to exclude
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -r '.restaurant' 2>/dev/null | sort -u
# Then search for restaurants NOT in this list
```

**"How much do we usually spend?"**
```bash
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -s '[.[] | select(.total_cost != null) | .total_cost] |
  if length > 0 then "Average: $\(add/length | round)" else "No cost data yet" end' \
  2>/dev/null
```

**"Stats this year"**
```bash
YEAR=$(date +%Y)
cat ~/.openclaw/skills/date-night/history.jsonl 2>/dev/null | \
  jq -s --arg y "$YEAR" '[.[] | select(.date | startswith($y))] | {
    count: length,
    avg_cost: ([.[] | .total_cost // 0] | if length > 0 then add/length else null end),
    favorite_cuisine: (group_by(.cuisine) | max_by(length) | .[0].cuisine // "N/A"),
    pct_return: (if length > 0 then ([.[] | select(.would_return == true)] | length) * 100 / length | round else null end)
  }' 2>/dev/null
```

**Dashboard presentation:**
```
📊 **Date Night Dashboard — {Year}**

🍽️  Total date nights: {count}
💰  Average spend: ~${avg}/night
⭐  Top rated: {restaurant} ({rating}/5)
🔁  Would return: {pct}%
🍝  Favorite cuisine: {cuisine}

**Recent:**
{date} — {restaurant} ⭐{rating} {✅ if would_return}
...
```
