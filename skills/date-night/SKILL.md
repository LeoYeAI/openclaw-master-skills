---
name: date-night
description: >
  Your AI date night concierge — plans, books, and coordinates an entire evening
  out through browser automation. Say "plan a date night" and it handles everything:
  restaurant reservations (OpenTable, Resy), movie tickets (Fandango, Megaplex, AMC),
  event tickets with price comparison (SeatGeek, Ticketmaster, StubHub), weather checks,
  drive-time estimates, budget totals, calendar events, and partner notifications.
  Configurable dietary preferences, childcare reminders, favorite theaters, and
  babysitter-rate budgeting. First run walks through a friendly onboarding —
  after that, just tell it what kind of night you want.
  Triggers: date night, dinner reservation, book a table, OpenTable, Resy, find restaurants,
  movie tickets, what's playing, concert tickets, sports tickets, events near me,
  dinner and a movie, plan a date, date ideas, cancel reservation, modify reservation,
  reconfigure date night preferences.
metadata:
  openclaw:
    emoji: "💑"
    requires:
      bins:
        - playwright-cli
      anyBins:
        - gog
        - gcal
        - ical
      optionalBins:
        - goplaces
        - imsg
        - jq
      optionalEnv:
        - GOOGLE_PLACES_API_KEY
      tools:
        - web_search
        - web_fetch
        - browser
        - message
    install:
      - id: playwright-cli
        kind: npm
        package: "@anthropic-ai/playwright-cli@latest"
        bins: ["playwright-cli"]
        label: "Install playwright-cli (npm)"
      - id: chromium
        kind: shell
        command: "npx playwright install chromium"
        label: "Install Chromium for playwright-cli"
    access:
      local_data:
        - path: "~/.openclaw/skills/date-night/config.json"
          purpose: "User preferences (name, email, phone, dietary, location)"
          sensitive: true
        - path: "~/.openclaw/skills/date-night/state/*.json"
          purpose: "Browser session cookies for Resy (opt-in, clearable)"
          sensitive: true
        - path: "~/.openclaw/skills/date-night/history.jsonl"
          purpose: "Date night log (restaurant, date, rating)"
          sensitive: false
      messaging:
        - channel: "configured notification channel"
          purpose: "Partner notifications — always drafted and shown for approval before sending"
          autonomous: false
      pii:
        - "Name, email, phone stored locally for auto-filling reservation forms"
        - "Never transmitted except to booking sites during form submission"
      sms_read:
        - purpose: "Retrieve booking verification codes from specific senders only"
          scope: "Last 1-2 messages from known booking service short codes (e.g. OpenTable 22395)"
          broad_scan: false
          always_on: false
          trigger: "Only during active reservation flow when site sends SMS verification"
      email_read:
        - purpose: "Find confirmation numbers for modify/cancel requests only"
          scope: "Targeted query (e.g. 'from:opentable reservation confirmed'), max 5 results"
          always_on: false
          trigger: "Only when user explicitly asks to modify/cancel and lacks confirmation number"
---

# Date Night Skill (Published)

End-to-end date night planning: restaurants, movies, events, logistics, and notifications. Powered by `playwright-cli` browser automation.

---

## User Preferences

This skill uses `~/.openclaw/skills/date-night/config.json`. **Run onboarding on first use** (see below). After that, load config silently at the start of every session.

```bash
cat ~/.openclaw/skills/date-night/config.json 2>/dev/null
```

Config schema:
```json
{
  "name": "string",
  "first_name": "string",
  "last_name": "string",
  "user_email": "string",
  "user_phone": "string (digits only, e.g. 8015550155)",
  "partner": "string | null",
  "notify_channel": "iMessage | Telegram | Discord | Signal | SMS",
  "dietary": ["no alcohol", "vegetarian", "..."],
  "has_children": false,
  "children_count": 0,
  "children_ages": "string | null",
  "location": "City, ST",
  "zip": "00000",
  "preferred_theater": "string | null",
  "babysitter_rate": 18,
  "calendar_tool": "gog | gcal | ical",
  "onboarded_at": "ISO timestamp"
}
```

**PII note:** `user_email`, `user_phone`, `first_name`, and `last_name` are used to auto-fill reservation and ticket forms. They are stored locally in `config.json` and never transmitted except to the booking site during form submission.

---

## First Run Onboarding

**Check at every skill invocation:**

```bash
CONFIG=~/.openclaw/skills/date-night/config.json
if [ ! -f "$CONFIG" ]; then
  echo "ONBOARDING_NEEDED"
fi
```

If `ONBOARDING_NEEDED`: run the onboarding flow **before** doing anything else.

### Onboarding Flow

Ask questions **one at a time**, conversationally. This is a date night skill — make it feel warm and fun, not like filling out a DMV form.

**Opening:**
> "Hey! Looks like it's your first time using the Date Night skill — exciting. Let me grab a few quick things so I can make it feel personal. Won't take long."

**Question sequence** (ask naturally, wait for each answer):

1. **Name:**
   > "First — what's your name?"
   — Collect first name and last name (needed for reservation forms).

2. **Email & Phone:**
   > "What email and phone number should I use for reservations? These go directly into booking forms — I store them locally and nowhere else."

3. **Partner:**
   > "Planning these with a partner, or flying solo? (Solo date nights are completely valid.)"
   — If partner: "What's their name?"

3. **Partner notification:**
   > "What's the best way to reach {partner}? Like, if I wanted to send them a heads-up about a reservation — iMessage, Telegram, Signal, Discord, something else?"
   — Skip if solo.

4. **Dietary / lifestyle:**
   > "Any food preferences or restrictions I should know about? Things like no alcohol, vegetarian, gluten-free, shellfish allergy — or just 'none, we eat everything'?"

5. **Kids:**
   > "Do you have kids at home? (I ask because I'll remind you about childcare after every booking.)"
   — If yes: "How many, and roughly what ages?"

6. **Location:**
   > "What city or zip code are you in? I'll use this for finding nearby restaurants, theaters, and venues."

7. **Theater preference (optional):**
   > "Any favorite movie theater chain, or a go-to theater near you? I can default to that when searching showtimes. (Skip if you don't have one.)"

8. **Babysitter rate (optional, only if has_children):**
   > "What's your babysitter rate — roughly? I use it for budget estimates. Default is $18/hr if you're not sure."

9. **Calendar tool:**
   > "Last one — how do you manage your calendar? I can add events automatically. Options: `gog` (Google), `gcal`, `ical`, or tell me what you use."

**Closing:**
> "Perfect — you're all set! 🎉 Just say 'plan a date night,' 'find us a restaurant,' or 'get us tickets' anytime. I've got the rest."

### Save Config

After collecting all answers, write the file:

```bash
mkdir -p ~/.openclaw/skills/date-night
cat > ~/.openclaw/skills/date-night/config.json << 'EOF'
{
  "name": "{name}",
  "first_name": "{first_name}",
  "last_name": "{last_name}",
  "user_email": "{email}",
  "user_phone": "{phone_digits}",
  "partner": "{partner_or_null}",
  "notify_channel": "{channel}",
  "dietary": ["{pref1}", "{pref2}"],
  "has_children": {true|false},
  "children_count": {N},
  "children_ages": "{ages_or_null}",
  "location": "{City, ST}",
  "zip": "{zip}",
  "preferred_theater": "{theater_or_null}",
  "babysitter_rate": {rate},
  "calendar_tool": "{tool}",
  "onboarded_at": "{ISO_TIMESTAMP}"
}
EOF
```

### Applying Config Throughout the Skill

After loading config, substitute into all references:

| Config field | Used in |
|-------------|---------|
| `first_name` / `last_name` | Auto-fill reservation and ticket forms |
| `user_email` | Auto-fill booking forms, account lookups |
| `user_phone` | Auto-fill booking forms, SMS verification |
| `dietary` | Restaurant recommendations (filter per preferences) |
| `location` / `zip` | All nearby searches, drive time estimates |
| `partner` | Notification drafts, calendar events |
| `notify_channel` | How to send partner notifications |
| `has_children` | Childcare prompt after every booking |
| `babysitter_rate` | Budget estimates |
| `preferred_theater` | Default theater for movie searches |
| `calendar_tool` | All calendar event creation commands |

**Dietary preference enforcement:**
If `dietary` includes `"no alcohol"`: never highlight wine lists, cocktail programs, bar scenes, or alcohol features when recommending restaurants or events. Focus on food, ambiance, service.

---

## Reconfigure

If user says **"update my date night preferences"**, **"reconfigure date night"**, or **"change my date night settings"**:

```bash
# Back up existing config
cp ~/.openclaw/skills/date-night/config.json \
   ~/.openclaw/skills/date-night/config.backup.json 2>/dev/null || true
```

Then re-run the onboarding flow with current values shown as defaults:
> "Sure — let's update your preferences. I'll show what you have now and you can change anything. Hit Enter to keep the current value."

After re-running, overwrite config.json. Confirm:
> "Updated! Changes are live for the next date night."

---

## Requirements

### External Binaries (must be installed separately)

| Binary | Install | Required? |
|--------|---------|-----------|
| `playwright-cli` | `npm install -g @playwright/cli@latest` | **Yes** |
| Chromium | `npx playwright install chromium` | **Yes** (used by playwright-cli) |
| `goplaces` | `brew install steipete/tap/goplaces` | Optional — enhanced restaurant search |

PATH setup: `export PATH="$HOME/.npm-global/bin:$PATH"`

### Environment Variables

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `GOOGLE_PLACES_API_KEY` | Google Places API for `goplaces` CLI | Only if using `goplaces` |

### OpenClaw Built-in Capabilities Used

These are **standard OpenClaw agent tools** — not external dependencies. They require no separate installation; they are available to any OpenClaw agent with the appropriate tool policies enabled.

| OpenClaw Tool | Purpose in This Skill |
|---------------|----------------------|
| `web_search` | Find restaurants, events, movies, reviews (public web) |
| `web_fetch` | Extract menus, reviews, showtimes from URLs (public web) |
| `message` (send) | Draft partner notifications — **always shown for approval before sending** |
| Calendar skills (`gog`/`ical`) | Create calendar events after booking |
| SMS/iMessage skill (`imsg`) | Retrieve booking verification codes (see Sensitive Access below) |

**No additional credentials or API tokens are needed** for these built-in tools — they use whatever channels and connectors the user has already configured in their OpenClaw instance.

### Sensitive Access Declaration

**SMS verification codes:** OpenTable and Resy send 6-digit verification codes via SMS during booking. This skill retrieves them by reading the **most recent 1–2 messages from the specific sender** (e.g., short code `22395` for OpenTable). It does NOT perform broad inbox scans. Specific patterns used:
```bash
# OpenTable: read last message from known short code only
imsg history --chat-id {OPENTABLE_CHAT_ID} --limit 1 | grep -oE '[0-9]{6}'
# Resy: read last 10 messages, filter for "resy" or "verification" only
imsg history --limit 10 | grep -i "resy\|verification\|code"
```

**Gmail (modify/cancel only):** When the user explicitly asks to modify or cancel a reservation and doesn't have the confirmation number, the skill searches Gmail with a **targeted query** — e.g., `from:opentable reservation confirmed` — limited to 5 results. This is never triggered during normal booking flows.

**Partner notifications:** Notifications are always **drafted and shown to the user for approval** before sending. The skill never sends messages autonomously. The messaging channel (iMessage/Telegram/Discord/Signal) is whatever the user configures in their OpenClaw instance — no additional credentials are stored by this skill.

**Auth state persistence:** The Resy flow optionally saves browser session state to `~/.openclaw/skills/date-night/state/resy-auth.json` to avoid re-login. This file contains session cookies. To clear: `rm -rf ~/.openclaw/skills/date-night/state/`. The skill **never asks for or stores site passwords** — it uses interactive browser login and saves only the resulting session cookies with user consent.

### Data Persistence

| Path | Contents | Sensitive? |
|------|----------|------------|
| `~/.openclaw/skills/date-night/config.json` | Preferences, name, email, phone | **Yes — PII** |
| `~/.openclaw/skills/date-night/history.jsonl` | Date night log (restaurant, date, rating) | Low |
| `~/.openclaw/skills/date-night/state/*.json` | Browser session cookies (Resy only, opt-in) | **Yes — auth tokens** |

To purge all skill data: `rm -rf ~/.openclaw/skills/date-night/`

### Pre-Flight Check
```bash
# Verify playwright-cli is available
export PATH="$HOME/.npm-global/bin:$PATH"
playwright-cli --version || echo "INSTALL: npm install -g @playwright/cli@latest"
```

---

## References

| Topic | File |
|-------|------|
| Playwright CLI | [references/playwright-cli.md](references/playwright-cli.md) |
| OpenTable flow | [references/opentable-flow.md](references/opentable-flow.md) |
| Resy flow | [references/resy-flow.md](references/resy-flow.md) |
| Restaurant search | [references/search-restaurants.md](references/search-restaurants.md) |
| Movie booking | [references/movie-booking.md](references/movie-booking.md) |
| Event tickets | [references/event-tickets.md](references/event-tickets.md) |
| Finding movies | [references/search-movies.md](references/search-movies.md) |
| Finding events | [references/search-events.md](references/search-events.md) |
| Modify / Cancel | [references/modify-cancel.md](references/modify-cancel.md) |
| SMS verification | [references/sms-codes.md](references/sms-codes.md) |
| Pre-evening intel | [references/pre-evening.md](references/pre-evening.md) |
| Smart features | [references/smart-features.md](references/smart-features.md) |

---

## Quick Flow: Dinner Reservation

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)
```

1. **Find restaurant** — see [search-restaurants.md](references/search-restaurants.md)
2. **Open restaurant page:**
   ```bash
   playwright-cli open "https://www.opentable.com/r/{slug}?covers={N}&dateTime={YYYY-MM-DDTHH:MM}" --headed
   ```
3. **Snapshot → select date → select time**
4. **Fill guest details** (name, phone, email from user's MEMORY.md or config)
5. **Submit → handle phone verification** (see [sms-codes.md](references/sms-codes.md))
6. **Confirm → post-booking actions** (below)

Full flow details: [opentable-flow.md](references/opentable-flow.md) | [resy-flow.md](references/resy-flow.md)

---

## Quick Flow: Movie Tickets

1. Start at preferred theater (from config) or search via Fandango
2. Select movie, showtime, seats
3. ⚠️ **STOP at payment** — show all-in price, confirm with user before purchase
4. Post-purchase actions (below)

Full details: [movie-booking.md](references/movie-booking.md) | [search-movies.md](references/search-movies.md)

---

## Quick Flow: Event Tickets

**Start with SeatGeek** (best price discovery + Deal Score):
```bash
playwright-cli open "https://seatgeek.com/search?q={event}&location={config.location}" --headed
```
Then cross-check Ticketmaster (official) and StubHub (resale).
⚠️ Ticketmaster has aggressive bot protection — see [event-tickets.md](references/event-tickets.md).
⚠️ **STOP at payment** — confirm all-in price with user before purchase.

---

## Full Date Night Flow

When user says *"plan a date night around [event/movie/idea]"*:

```
1. LOAD config.json silently
2. FIND the event/movie → SeatGeek + Ticketmaster + StubHub price comparison
3. PRESENT options + prices to user → get approval to proceed
4. BOOK tickets (with explicit user confirmation at payment)
5. NOTE venue and show time
6. SEARCH restaurants within 1 mile of venue, open before the show
7. SUGGEST 2-3 dinner options with ratings and OpenTable availability
8. BOOK dinner (with approval) at time that ends ~1 hr before show
9. CHECK weather for that evening → include in summary
10. CALCULATE timeline: leave home → dinner → venue → showtime
11. ADD both events to calendar ({config.calendar_tool})
12. DRAFT partner notification → show draft → send with approval
13. IF has_children: PROMPT about childcare — every time, no exceptions
14. OFFER dessert spot near venue (optional extension)
15. PRESENT budget estimate: dinner + tickets + babysitter total
```

**Example timeline for 7:30 PM show:**
```
6:00 PM  Leave home
6:30 PM  Dinner (2-block walk from venue)
8:00 PM  Walk to venue
7:30 PM  Show
10:30 PM Done — dessert optional
```

---

## Post-Booking Actions

Execute after **every** reservation or ticket purchase:

### 1. Add to Calendar
```bash
{config.calendar_tool} calendar create primary \
  --summary "{Event/Dinner} @ {Venue/Restaurant}" \
  --from "{datetime}" \
  --to "{datetime+duration}" \
  --location "{address}" \
  --description "{details + confirmation number}" \
  --reminder "popup:2h" --reminder "popup:1d"
```

### 2. Notify Partner (if configured)
Draft in user's casual voice → show draft → **require approval before sending**.
```
"Hey {partner}, got us a reservation at {Restaurant} on {date} at {time} 🍽️"
```

### 3. Childcare Prompt
If `has_children: true` — **ALWAYS ask, no exceptions:**
> "Do you have childcare sorted for that evening? {N} kid(s) to account for."

### 4. Log to History
```bash
mkdir -p ~/.openclaw/skills/date-night
cat >> ~/.openclaw/skills/date-night/history.jsonl << 'EOF'
{"date":"{YYYY-MM-DD}","restaurant":"{name}","event":"{event_or_null}","total_cost":null,"rating":null,"would_return":null,"weather":null,"notes":""}
EOF
```

---

## Error Recovery

| Error | Recovery |
|-------|----------|
| Config not found | Run onboarding before proceeding |
| OT timer expired | Restart from restaurant page URL |
| Verification code not received | Wait 30s, click Resend, check SMS |
| Phone field cleared | Known OT bug — re-fill before submit |
| TM queue/CAPTCHA | Document for user; offer manual assist |
| Seat map won't load | Use `playwright-cli screenshot` to diagnose |
| StubHub price changed | Re-check before submitting; prices fluctuate |

---

## Checklists

### Before Booking (Any)
- [ ] Config loaded
- [ ] Restaurant/movie/event, date, time, party size confirmed with user
- [ ] **Full price shown to user before any purchase**

### After Booking (Any)
- [ ] Calendar event created
- [ ] Partner notified (draft approved)
- [ ] Childcare asked (if has_children)
- [ ] Logged to history
- [ ] Pre-evening intel offered (weather, parking, drive time)
- [ ] Budget estimate presented
