---
name: resy-hunter
description: "Monitor hard-to-get restaurant reservations on Resy, OpenTable, and Tock. Check availability, manage a watchlist, and get Telegram alerts when tables open up."
version: 2.1.0
metadata:
  openclaw:
    requires:
      env:
        - RESY_API_KEY
        - RESY_EMAIL
        - RESY_PASSWORD
      bins:
        - curl
        - jq
        - node
        - sed
    primaryEnv: RESY_API_KEY
    emoji: "🍽️"
---

# Resy Hunter

Monitor restaurant reservations across Resy, OpenTable, and Tock. Detect open tables and alert the user via Telegram.

## When to Use

- User asks to check if a restaurant has availability
- User wants to find open tables at a specific restaurant on a date
- User wants to monitor a restaurant for cancellations or new openings
- User wants to manage their restaurant watchlist (add, remove, list)
- User asks to set up background monitoring or alerts

## Platforms Supported

| Platform | Script | Identifier | Auth Required | Notes |
|----------|--------|------------|---------------|-------|
| Resy | `resy-check.sh` | `venue_id` (integer) | Yes — `RESY_API_KEY` + `RESY_EMAIL` + `RESY_PASSWORD` | Auto-login via API, token cached 12h |
| OpenTable | `opentable-check.js` | `restaurant_id` (integer) | Yes — manual login via `opentable-login.js` | One-time visible browser login, session persisted |
| Tock | `tock-check.js` | `slug` (URL slug) | No | Playwright bypasses Cloudflare |

## Parsing Natural Language Requests

Users speak casually. Extract these fields from every request:

| Field | How to parse | Default |
|-------|-------------|---------|
| **Restaurant** | Name mentioned, or "my list" / "my watchlist" → sweep all watchlist entries | — |
| **Party size** | "for 2", "party of 4", "2 people", "two" | Ask if missing |
| **Date(s)** | "March 9" → `2026-03-09`. "this Saturday" → resolve to YYYY-MM-DD. "next 30 days" → generate array of dates. "this weekend" → upcoming Sat + Sun. "any Friday in April" → all Fridays in April. | Ask if missing |
| **Time window** | "6-9pm" → `earliest: "18:00", latest: "21:00"`. "7:30p" → `earliest: "19:00", latest: "20:00"` (±30min). "dinner" / "prime time" → `earliest: "18:00", latest: "21:00"`. "lunch" → `earliest: "11:30", latest: "14:00"`. "tonight" → `earliest: "18:00", latest: "22:00"` | All times |
| **Fallback** | "if nothing, check my list" → on zero results, sweep watchlist with same date/party/time constraints | None |
| **Action** | "book me" / "find me a res" / "get me a table" → find availability and present booking links (skill is read-only, never books). "monitor" / "alert me" / "watch for" → set up cron. "add to my list" → watchlist add. | Check availability |

**"Book" always means "find availability."** This skill never books. Always present results with a direct booking link so the user can book themselves.

### Example Requests → Execution Plans

---

**"Book me a res at Tatiana by Kwame sometime in the next 30 days between 6-9pm for 2 people"**

Parsed:
- Restaurant: Tatiana by Kwame → run `resy-search-venue.sh "Tatiana by Kwame"` to get venue_id
- Dates: next 30 days → generate `["2026-03-06", "2026-03-07", ..., "2026-04-04"]`
- Time: 6-9pm → `earliest: "18:00", latest: "21:00"`
- Party size: 2

Execute:
1. `bash scripts/resy-search-venue.sh "Tatiana by Kwame"` → get venue_id
2. Loop through each date: `bash scripts/resy-check.sh <venue_id> <date> 2`
3. Filter returned slots to only those between 18:00-21:00
4. Present all dates that have matching slots, with booking links
5. If zero results across all 30 days, offer to add to watchlist for monitoring

---

**"Find me a res from my list of restaurants for 3 people this Sat between 6-7:30p, alert me with which ones are available and I will pick one"**

Parsed:
- Restaurant: "from my list" → sweep entire watchlist
- Date: "this Sat" → resolve to upcoming Saturday YYYY-MM-DD
- Time: 6-7:30p → `earliest: "18:00", latest: "19:30"`
- Party size: 3 (override each entry's party_size for this check)

Execute:
1. `bash scripts/watchlist.sh list` → get all entries
2. For each entry, run the platform check script with the resolved Saturday date and party_size=3
3. Filter slots to 18:00-19:30 window
4. Present results grouped by restaurant, with booking links
5. Let the user pick — do not choose for them

---

**"Book me at Carbone for 2 on March 9 5-9pm, if no availability find something else from my list"**

Parsed:
- Restaurant: Carbone → search venue_id
- Date: March 9 → `2026-03-09`
- Time: 5-9pm → `earliest: "17:00", latest: "21:00"`
- Party size: 2
- Fallback: sweep watchlist

Execute:
1. `bash scripts/resy-search-venue.sh "Carbone"` → get venue_id
2. `bash scripts/resy-check.sh <venue_id> 2026-03-09 2`
3. Filter slots to 17:00-21:00
4. If slots found → present with booking link, done
5. If no slots → `bash scripts/watchlist.sh list`, then check each entry for 2026-03-09 party_size=2 with 17:00-21:00 filter
6. Present any alternatives found from the watchlist

---

**"Any openings at Don Angie tonight for 4?"**

Parsed:
- Restaurant: Don Angie → search venue_id
- Date: tonight → today's date
- Time: (tonight implies dinner) → `earliest: "18:00", latest: "22:00"`
- Party size: 4

Execute:
1. `bash scripts/resy-search-venue.sh "Don Angie"` → get venue_id
2. `bash scripts/resy-check.sh <venue_id> <today> 4`
3. Filter to 18:00-22:00, present results

---

**"Set up alerts for Atomix, party of 2, any Friday or Saturday in April between 7-9"**

Parsed:
- Restaurant: Atomix → search venue_id
- Dates: every Fri + Sat in April 2026 → `["2026-04-03", "2026-04-04", "2026-04-10", "2026-04-11", ...]`
- Time: 7-9 → `earliest: "19:00", latest: "21:00"`
- Party size: 2
- Action: set up monitoring

Execute:
1. `bash scripts/resy-search-venue.sh "Atomix"` → get venue_id
2. `bash scripts/watchlist.sh add '{"name":"Atomix","platform":"resy","venue_id":<id>,"party_size":2,"dates":["2026-04-03","2026-04-04",...],"preferred_times":{"earliest":"19:00","latest":"21:00"}}'`
3. Set up cron if not already running:
```bash
openclaw cron add --name "resy-hunter-sweep" --every "15m" --session isolated --message "Run resy-hunter monitor..." --announce
```
4. Confirm to user: "Monitoring Atomix for Friday/Saturday openings in April, 7-9 PM, party of 2. I'll alert you on Telegram when something opens."

---

**"What's available this weekend from my list?"**

Parsed:
- Restaurant: "from my list" → sweep watchlist
- Date: "this weekend" → upcoming Saturday + Sunday
- Time: not specified → all times
- Party size: not specified → use each entry's configured party_size

Execute:
1. `bash scripts/watchlist.sh list` → get all entries
2. For each entry, check both Saturday and Sunday dates using the entry's own party_size
3. Present all results grouped by restaurant and date

---

**"Check everything on my list for tomorrow night"**

Parsed:
- Restaurant: "everything on my list" → sweep watchlist
- Date: tomorrow → resolve to YYYY-MM-DD
- Time: "night" → `earliest: "18:00", latest: "22:00"`
- Party size: use each entry's configured party_size

Execute: same as watchlist sweep pattern above

---

**"Monitor Torrisi for cancellations, party of 4, March 15, prime time"**

Parsed:
- Restaurant: Torrisi → search venue_id
- Date: March 15 → `2026-03-15`
- Time: "prime time" → `earliest: "18:00", latest: "21:00"`
- Party size: 4
- Action: "monitor for cancellations" → add to watchlist + set up cron

Execute:
1. Search venue_id, add to watchlist, set up cron
2. Confirm monitoring is active

---

**"Add Lilia to my watchlist, 2 people, next three Saturdays, dinner time"**

Parsed:
- Restaurant: Lilia → search venue_id
- Dates: next 3 Saturdays → resolve to specific YYYY-MM-DD values
- Time: "dinner time" → `earliest: "18:00", latest: "21:00"`
- Party size: 2
- Action: watchlist add only (no cron unless asked)

Execute:
1. `bash scripts/resy-search-venue.sh "Lilia"` → get venue_id
2. `bash scripts/watchlist.sh add '{"name":"Lilia","platform":"resy","venue_id":<id>,"party_size":2,"dates":["<sat1>","<sat2>","<sat3>"],"preferred_times":{"earliest":"18:00","latest":"21:00"}}'`

---

**"Is there anything at 4 Charles or Via Carota for 2 this Thursday?"**

Parsed:
- Restaurants: two separate — "4 Charles" and "Via Carota"
- Date: this Thursday → resolve
- Party size: 2

Execute:
1. Search venue_ids for both restaurants
2. Check both for the resolved Thursday date with party_size=2
3. Present results side by side

---

**"Cancel monitoring for Carbone"**

Parsed:
- Action: remove from watchlist

Execute:
1. `bash scripts/watchlist.sh list` → find Carbone's id
2. `bash scripts/watchlist.sh remove <id>`
3. If watchlist is now empty, suggest removing the cron job too

## How to Run Checks

1. Determine the platform (ask the user if unclear)
2. Get the restaurant identifier:
   - **Resy**: If the user doesn't know the `venue_id`, run `scripts/resy-search-venue.sh "<name>" [lat] [long]` to find it
   - **OpenTable**: The `restaurant_id` is in the OpenTable URL (e.g., `opentable.com/r/restaurant-name-city?rid=123456` → rid is `123456`)
   - **Tock**: The slug is in the URL (e.g., `exploretock.com/alinea` → slug is `alinea`)
3. Run the appropriate check script:
   - Resy: `bash ~/.openclaw/skills/resy-hunter/scripts/resy-check.sh <venue_id> <date> <party_size>`
   - OpenTable: `node ~/.openclaw/skills/resy-hunter/scripts/opentable-check.js <restaurant_id> <date> <party_size>`
   - Tock: `node ~/.openclaw/skills/resy-hunter/scripts/tock-check.js <slug> <date> <party_size>`
4. Parse the JSON output and present available slots in a clean table format:
   ```
   Restaurant | Date | Time | Type | Platform
   ```
5. If no slots found, offer to add to the watchlist for background monitoring

## Watchlist Management

The watchlist lives at `~/.openclaw/data/resy-hunter/watchlist.json` (separate from the skill directory so reinstalls don't wipe user data).

- **List**: `bash ~/.openclaw/skills/resy-hunter/scripts/watchlist.sh list`
- **Add**: `bash ~/.openclaw/skills/resy-hunter/scripts/watchlist.sh add '<json>'`
  - JSON must include: `name`, `platform` (resy/opentable/tock), platform identifier (`venue_id`/`restaurant_id`/`slug`), `party_size`, `dates` array
  - Optional: `preferred_times` object with `earliest` and `latest` in HH:MM format
- **Remove**: `bash ~/.openclaw/skills/resy-hunter/scripts/watchlist.sh remove <id>`
- **Set Priority**: `bash ~/.openclaw/skills/resy-hunter/scripts/watchlist.sh set-priority <id> <high|low>`

### Priority Levels

- **high** — Telegram alerts fire immediately when new slots appear
- **low** — Slots are tracked (dedup works) but Telegram alerts only when the user explicitly asks for a sweep

Default priority is `low` when adding entries. Set it to `high` for restaurants the user actively wants alerts on. The JSON report from `monitor.sh` always includes all priorities.

### Default Time Window

All entries default to a **6:00 PM – 10:00 PM** time window. Slots outside this window are filtered out. Override per restaurant via `preferred_times` when adding:

Example add:
```bash
bash ~/.openclaw/skills/resy-hunter/scripts/watchlist.sh add '{
  "name": "Carbone",
  "platform": "resy",
  "venue_id": 5286,
  "party_size": 2,
  "dates": ["2026-03-15", "2026-03-22"],
  "preferred_times": {"earliest": "18:00", "latest": "21:30"},
  "priority": "high"
}'
```

## Background Monitoring

The monitor runs checks in parallel and staggers platforms by frequency:
- **Resy** (curl): checked every sweep, up to 8 concurrent
- **Tock** (Playwright): checked once per hour, up to 2 concurrent
- **OpenTable** (Playwright): checked once per hour, up to 2 concurrent

To set up cron monitoring, run:

```bash
openclaw cron add \
  --name "resy-hunter-sweep" \
  --every "15m" \
  --session isolated \
  --message "Run resy-hunter monitor. Execute bash ~/.openclaw/skills/resy-hunter/scripts/monitor.sh. If new availability is found in the output JSON (new_availability array is non-empty), format a clear alert listing each restaurant name, platform, date, available time slots, and party size. Include a direct booking link. If nothing new, respond only: No new availability." \
  --announce
```

The 15-minute cron means Resy is checked every 15 minutes while Tock and OpenTable are automatically checked once per hour (the monitor tracks timestamps and skips platforms checked less than 60 minutes ago).

For high-frequency sniping on a specific date (e.g., when reservations drop):

```bash
openclaw cron add \
  --name "resy-hunter-snipe" \
  --every "2m" \
  --session isolated \
  --message "Snipe mode: run bash ~/.openclaw/skills/resy-hunter/scripts/resy-check.sh <venue_id> <date> <party_size>. Report immediately if any slot appears." \
  --announce
```

To stop monitoring: `openclaw cron remove --name "resy-hunter-sweep"`

## Manual Monitor Sweep

To run a one-time sweep of the entire watchlist:

```bash
bash ~/.openclaw/skills/resy-hunter/scripts/monitor.sh
```

To check only a specific platform (bypasses the hourly interval timer):

```bash
bash ~/.openclaw/skills/resy-hunter/scripts/monitor.sh --platform resy
bash ~/.openclaw/skills/resy-hunter/scripts/monitor.sh --platform tock
bash ~/.openclaw/skills/resy-hunter/scripts/monitor.sh --platform opentable
```

Multiple platforms can be combined:

```bash
bash ~/.openclaw/skills/resy-hunter/scripts/monitor.sh --platform resy --platform tock
```

Interpret the output JSON:
- `new_availability` array: newly detected slots since last sweep
- `total_checked`: number of restaurant+date combinations checked
- `total_with_availability`: how many had open slots

## Sending Notifications Manually

```bash
bash ~/.openclaw/skills/resy-hunter/scripts/notify.sh "Your message here"
```

This sends a Telegram message. The bot token is pulled from OpenClaw's Telegram channel config (`channels.telegram.botToken`). Falls back to `TELEGRAM_BOT_TOKEN` env var if config not found.

## Booking Links

When reporting availability, always include a direct booking link:
- **Resy**: `https://resy.com/cities/<city>-<region>/venues/<slug>?date=<YYYY-MM-DD>&seats=<party_size>`
- **OpenTable**: `https://www.opentable.com/booking/widget?rid=<restaurant_id>&datetime=<ISO>&covers=<party_size>`
- **Tock**: `https://www.exploretock.com/<slug>/search?date=<YYYY-MM-DD>&size=<party_size>`

## Error Handling

- If a Resy request returns HTTP 419, the script automatically clears the cached token and re-authenticates. No manual action needed.
- If Resy login fails (HTTP 401/403), check `RESY_EMAIL` and `RESY_PASSWORD`.
- If OpenTable returns `session_expired: true`, run `node ~/.openclaw/skills/resy-hunter/scripts/opentable-login.js` to re-authenticate manually. The monitor will send a Telegram alert when this happens.
- If Tock returns `blocked: true` in output, Cloudflare blocked even the Playwright browser. Return the URL for the user to check manually. This is rare — retrying usually works.

## Credential Setup

**Resy (auto-login via API):**
1. `RESY_API_KEY` — one-time extraction from browser DevTools (static, never expires):
   - Log into resy.com → DevTools → Network tab
   - Find any request to `api.resy.com`
   - `Authorization` header → value after `ResyAPI api_key=` is the API key
2. `RESY_EMAIL` — your Resy account email
3. `RESY_PASSWORD` — your Resy account password
4. Auth tokens are fetched and cached automatically (12-hour TTL). No manual token extraction needed.

**OpenTable (manual login via Playwright):**
1. Run once: `node ~/.openclaw/skills/resy-hunter/scripts/opentable-login.js`
2. A visible browser opens to OpenTable's login page
3. Log in with your email + OTP code manually
4. The script detects login and saves session cookies to `~/.openclaw/data/resy-hunter/opentable-session.json`
5. Future runs use the saved session headlessly. If it expires, the monitor sends a Telegram alert telling you to re-run `opentable-login.js`.

**Tock (no credentials):**
No credentials needed. Playwright uses a real browser that passes Cloudflare Turnstile challenges automatically.

## First-Time Setup

After installing the skill, run once to install dependencies:
```bash
cd ~/.openclaw/skills/resy-hunter
npm install
npx playwright install chromium
```

## Important

- This skill is **read-only**. Never attempt to book a reservation. The user books manually.
- Respect rate limits. Do not run checks more frequently than every 2 minutes.
- Dates in the past should be skipped automatically by the monitor script.
