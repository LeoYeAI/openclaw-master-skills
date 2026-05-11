---
name: wahoo-cloud
description: Wahoo Fitness Cloud API — fetch workouts, download FIT files, parse power/HR/cadence/GPS into local SQLite for analysis
homepage: https://cloud-api.wahooligan.com/
metadata: {"clawdbot":{"emoji":"🚴","requires":{"bins":["python3"],"env":["WAHOO_CLIENT_ID","WAHOO_CLIENT_SECRET"]},"primaryEnv":"WAHOO_CLIENT_ID"}}
---

# Wahoo Cloud API Skill

Programmatic access to the Wahoo Fitness Cloud API for ELEMNT BOLT/ROAM/ACE head units. Fetches workout metadata, downloads FIT files from Wahoo's CDN, and parses ride data (power, cadence, HR, GPS, elevation) into a local SQLite database.

API base: `https://api.wahooligan.com`. Workout endpoints live under `/v1/workouts`. OAuth2 with the `offline_data` scope yields a long-lived refresh token; access tokens expire after ~2 hours and the skill auto-refreshes on 401.

## Agent quickstart (read this first)

If you're an agent invoking this skill on behalf of a user:

| User asks | Run this |
|---|---|
| "Sync my Wahoo workouts" / "Pull new rides" | `python3 {baseDir}/scripts/fetch_workouts.py` |
| "Show recent rides" / "Last week's training" | Query `~/.openclaw/workspace/training/wahoo.db` (or `$WAHOO_TRAINING_DIR/wahoo.db`) — schema below |
| "Parse this FIT file" | `python3 {baseDir}/scripts/parse_fit.py PATH.fit [--summary-only]` |
| "Set up Wahoo" / "Connect my Wahoo" | Walk the user through Setup §1–3 below; then run `python3 {baseDir}/scripts/oauth_setup.py` |
| "Refresh my Wahoo token" | `bash {baseDir}/scripts/refresh_token.sh` (only needed if auto-refresh fails) |

The fetch script is **idempotent** — safe to run on a heartbeat. It skips workouts already fully synced (`fit_parsed_at IS NOT NULL`). Sandbox rate limits (25 req / 5 min) trigger automatic backoff, so a first sync of a long history may take many minutes.

The skill **cannot** ship credentials. Each user needs their own Wahoo developer app — no shortcut. Setup is a one-time browser handshake.

**Credential auto-loading:** if `WAHOO_CLIENT_ID` / `WAHOO_CLIENT_SECRET` aren't in the calling shell, `wahoo_auth.py` automatically reads them from `~/.openclaw/secrets/wahoo.env` (override path with `$WAHOO_ENV_FILE`). This means an OpenClaw agent can invoke `fetch_workouts.py` without sourcing anything — token refresh just works.

## Setup

### 1. Register a Wahoo Developer App

1. Go to https://developers.wahooligan.com
2. Create an application (Sandbox is automatic — no review)
3. Set callback URL (e.g. `https://localhost:8080/` — the manual-paste OAuth helper works with any registered callback)
4. Request scopes: `workouts_read offline_data user_read` (add `power_zones_read plans_read routes_read` if you want zones/plans/routes)
5. Note your **Client ID** and **Client Secret**

### 2. Configure Credentials

Add to `~/.clawdbot/clawdbot.json`:
```json
{
  "skills": {
    "entries": {
      "wahoo": {
        "enabled": true,
        "env": {
          "WAHOO_CLIENT_ID": "your-client-id",
          "WAHOO_CLIENT_SECRET": "your-client-secret",
          "WAHOO_REDIRECT_URI": "https://localhost:8080/"
        }
      }
    }
  }
}
```

Or as environment variables:
```bash
export WAHOO_CLIENT_ID="..."
export WAHOO_CLIENT_SECRET="..."
export WAHOO_REDIRECT_URI="https://localhost:8080/"
```

### 3. Run OAuth2 Flow

```bash
python3 {baseDir}/scripts/oauth_setup.py
```

The script prints an authorization URL. Open it in a browser, log in with your Wahoo account, approve. You'll be redirected to your callback URL with `?code=...` in the query string (the page itself will fail to load — that's expected; just copy the URL or the `code` value). Paste it back into the script. It exchanges the code for tokens and writes them to `~/.openclaw/secrets/wahoo_tokens.json`.

### 4. Fetch Workouts

```bash
python3 ~/.openclaw/workspace/training/fetch_wahoo.py
```

This pulls the workout list, fetches detail (and FIT URL) for each new workout, downloads FIT files into `~/.openclaw/workspace/training/wahoo_fit/`, parses them, and upserts records into `~/.openclaw/workspace/training/wahoo.db`.

## Usage

### List Workouts (paginated)

```bash
curl -s -H "Authorization: Bearer ${WAHOO_ACCESS_TOKEN}" \
  "https://api.wahooligan.com/v1/workouts?page=1&per_page=30"
```

Response shape: `{ workouts: [...], total, page, per_page, order, sort }`. Note that `workout_summary` is `null` in the list response — fetch detail per workout to get summary + FIT URL.

### Get Workout Detail (with FIT URL)

```bash
curl -s -H "Authorization: Bearer ${WAHOO_ACCESS_TOKEN}" \
  "https://api.wahooligan.com/v1/workouts/WORKOUT_ID"
```

The FIT file URL lives at `workout_summary.file.url`.

### Download a FIT File

```bash
curl -L -o ride.fit "$FIT_URL"
```

The CDN doesn't require auth and doesn't count against your API rate limit.

### Get User Profile

```bash
curl -s -H "Authorization: Bearer ${WAHOO_ACCESS_TOKEN}" \
  "https://api.wahooligan.com/v1/user"
```

Returns `{ id, height, weight, first, last, email, birth, gender, created_at, updated_at }`. Height and weight are returned as decimal strings.

### Refresh Access Token

```bash
bash {baseDir}/scripts/refresh_token.sh
```

The Python OAuth helper auto-refreshes on 401 if a `refresh_token` is on file. The shell helper is for manual/cron use.

```bash
curl -s -X POST https://api.wahooligan.com/oauth/token \
  -d client_id="${WAHOO_CLIENT_ID}" \
  -d client_secret="${WAHOO_CLIENT_SECRET}" \
  -d grant_type=refresh_token \
  -d refresh_token="${WAHOO_REFRESH_TOKEN}"
```

The new access token does not invalidate the old one until you successfully use it (Wahoo allows up to 10 unrevoked access tokens per user as of Jan 2026).

## Common Data Fields

`workout_summary` includes:
- `ascent_accum` — total elevation gain (m)
- `cadence_avg` — average cadence (rpm)
- `calories_accum` — kcal
- `distance_accum` — distance (m)
- `duration_active_accum` / `duration_paused_accum` / `duration_total_accum` — seconds
- `heart_rate_avg` — bpm
- `power_avg` — average power (W)
- `power_bike_np_last` — normalized power
- `power_bike_tss_last` — Training Stress Score
- `speed_avg` — m/s
- `work_accum` — total work (J)
- `time_zone` — IANA tz
- `file.url` — FIT file URL (CDN)

All decimal values are returned as strings — cast before math.

`workout_type_id` is an integer enum whose mapping isn't published. Empirically observed: cycling rides come back as `0`. Treat as opaque and key off the FIT `sport`/`sub_sport` fields (parsed into `workouts.fit_*` columns) when you need to filter by activity type.

## Rate Limits

| Tier | per 5 min | per hour | per day |
|------|-----------|----------|---------|
| Sandbox | 25 | 100 | 250 |
| Production | 200 | 1,000 | 5,000 |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. The sync pipeline backs off automatically on 429.

## Tips

- Convert m → mi: divide by 1609.34
- Convert m/s → mph: multiply by 2.237
- Decimal strings: `float(workout_summary["power_avg"])` before any math
- The list endpoint omits `workout_summary` — always hit detail (`/v1/workouts/:id`) to get FIT URL

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 401 | Access token expired/invalid | Run `refresh_token.sh` or let `wahoo_auth.py` auto-refresh |
| 403 | Scope insufficient | Re-authorize with the missing scope |
| 429 | Rate limit hit | Wait until `X-RateLimit-Reset` |
| 404 | Workout not found / not yours | Confirm ID + ownership |
