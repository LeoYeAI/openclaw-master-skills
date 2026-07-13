# OpenTable & Tock Reference

## OpenTable (Playwright)

OpenTable has no public consumer API and no login endpoint for programmatic auth. This skill uses Playwright to run a real Chromium browser that logs in with email/password and captures availability data.

### How It Works

1. Launches headless Chromium with persistent session state (`.playwright-state/opentable.json`)
2. Navigates to the OpenTable restaurant page with date/party params
3. Intercepts network responses containing availability data (XHR/fetch to availability endpoints)
4. If no active session, detects the login wall and fills OPENTABLE_EMAIL + OPENTABLE_PASSWORD
5. Saves session cookies/localStorage for reuse across runs
6. Parses availability JSON from intercepted responses, with DOM fallback
7. Outputs JSON to stdout

### Script Interface

```
node scripts/opentable-check.js <restaurant_id> <date> <party_size> [time]
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENTABLE_EMAIL` | OpenTable account email |
| `OPENTABLE_PASSWORD` | OpenTable account password |

### Session Persistence

Session state is saved to `~/.openclaw/skills/resy-hunter/.playwright-state/opentable.json`. Delete this file to force a fresh login.

### Finding the Restaurant ID

The `rid` can be found in OpenTable URLs:
- `https://www.opentable.com/r/restaurant-name-city?rid=123456`
- The `rid` query parameter is the restaurant ID

### Booking URL

```
https://www.opentable.com/booking/widget?rid=<rid>&datetime=<ISO>&covers=<party_size>
```

---

## Tock (Playwright)

Tock (exploretock.com) has no API. The site is protected by Cloudflare Turnstile which blocks curl/wget. This skill uses Playwright to run a real Chromium browser that passes Cloudflare challenges.

### How It Works

1. Launches headless Chromium (real browser fingerprint passes Turnstile)
2. Navigates to the Tock search URL with date/party/time params
3. If Cloudflare challenge appears, waits up to 18 seconds for auto-resolution
4. Once page renders, tries three extraction strategies:
   - Extract `__NEXT_DATA__` JSON from the DOM (most reliable)
   - Query DOM for time slot elements (fallback)
   - Detect "no availability" text
5. If still blocked after wait, returns URL for manual check (`blocked: true`)
6. Outputs JSON to stdout

### Script Interface

```
node scripts/tock-check.js <slug> <date> <party_size> [time]
```

### No Credentials Required

Tock search pages are public. No login needed.

### Search URL Format

```
https://www.exploretock.com/<slug>/search?date=<YYYY-MM-DD>&size=<party_size>&time=<HH:MM>
```

### Booking URL

Same as the search URL:
```
https://www.exploretock.com/<slug>/search?date=<YYYY-MM-DD>&size=<party_size>
```
