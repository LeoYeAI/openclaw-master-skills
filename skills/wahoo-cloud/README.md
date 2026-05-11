# Wahoo Cloud API Skill for OpenClaw

An [OpenClaw](https://openclaw.dev) / [ClawHub](https://clawhub.ai) skill that gives any agent — or any Python script — programmatic access to the [Wahoo Fitness Cloud API](https://cloud-api.wahooligan.com/). Pulls workouts off the Wahoo cloud, downloads the raw FIT files from Wahoo's CDN, parses them with [`fitparse`](https://github.com/dtcooper/python-fitparse), and lands the result in a local SQLite database you control.

Wahoo ELEMNT BOLT, ROAM, and ACE generate gold-standard cycling telemetry — power, cadence, heart rate, GPS, elevation, all at 1 Hz — but Wahoo has historically lacked the third-party ecosystem Garmin and Strava enjoy. This skill closes that gap.

## What you get

- **OAuth2 setup helper** — manual-paste flow that works with any registered callback URL, no local HTTPS server required
- **Auto-refresh** of access tokens via the `offline_data` refresh token
- **API client** — workout list, workout detail, user profile, with built-in 429 backoff
- **FIT downloader** — pulls files from Wahoo's CDN (no API rate-limit cost)
- **FIT parser** — power, cadence, HR, GPS, elevation → JSON / SQLite
- **SQLite sync pipeline** — incremental, idempotent, safe to re-run

## Status

- API client + parser: working, tested against ~650 real workouts
- OAuth flow: confidential-app sandbox tested
- Production approval from Wahoo: not yet submitted

## Quick start

### 1. Register a Wahoo developer app

1. Go to [developers.wahooligan.com](https://developers.wahooligan.com).
2. Create an application. Sandbox is automatic — no review required.
3. Set the callback URL (e.g. `https://localhost:8080/`). The OAuth helper uses manual paste, so any URL you can reach in a browser works.
4. Request scopes. Minimum useful set: `workouts_read offline_data user_read`. Add `power_zones_read plans_read routes_read` if you want zones / plans / routes.
5. Note your **Client ID** and **Client Secret**.

### 2. Install dependencies

```bash
pip install --user 'fitparse>=1.2,<2'
```

(`fitparse` is the only Python dependency. `curl` is needed for the shell refresh helper.)

### 3. Configure credentials

```bash
export WAHOO_CLIENT_ID="..."
export WAHOO_CLIENT_SECRET="..."
export WAHOO_REDIRECT_URI="https://localhost:8080/"
export WAHOO_SCOPES="workouts_read offline_data user_read"
```

Or, if you're running inside OpenClaw, add the equivalent block to `~/.clawdbot/clawdbot.json` — see [`config.example.json`](config.example.json).

### 4. Run the OAuth handshake

```bash
python3 scripts/oauth_setup.py
```

The script prints an authorization URL. Open it in a browser, log in with your Wahoo account, approve. Wahoo redirects to your callback URL with `?code=…` in the query string — the page itself will fail to load (expected, since nothing's listening there). Copy the redirect URL or just the code value, paste it back into the script. Tokens land at `~/.openclaw/secrets/wahoo_tokens.json` (mode `0600`).

### 5. Sync workouts

```bash
python3 scripts/fetch_workouts.py
```

Lists every workout, fetches detail per workout (the list endpoint omits `workout_summary`), downloads the FIT into `$WAHOO_TRAINING_DIR/wahoo_fit/`, parses it, and upserts into `$WAHOO_TRAINING_DIR/wahoo.db`. Default `$WAHOO_TRAINING_DIR` is `~/.openclaw/workspace/training/`; override the env var to relocate.

The pipeline is idempotent — re-run anytime to pick up new workouts. Sandbox rate limits (25 req / 5 min) trigger automatic backoff.

## Layout

```
.
├── SKILL.md              # OpenClaw skill manifest (clawhub publish reads this)
├── README.md
├── config.example.json
├── lib/
│   ├── wahoo_auth.py     # token storage + auto-refresh
│   ├── wahoo_api.py      # HTTP client (urllib only; no requests dependency)
│   └── fit_parser.py     # FIT → dict (uses fitparse)
├── scripts/
│   ├── oauth_setup.py    # interactive OAuth2 flow
│   ├── fetch_workouts.py # main sync pipeline
│   ├── parse_fit.py      # standalone FIT → JSON CLI
│   └── refresh_token.sh  # manual token refresh
├── schema/
│   └── wahoo_db_schema.sql
└── docs/
    ├── PRD.md
    └── PLAN.md
```

## Database schema

`schema/wahoo_db_schema.sql` defines two tables:

- **`workouts`** — one row per Wahoo workout. Includes both Wahoo-summary fields (`distance_m`, `power_avg`, `heart_rate_avg`, …) and FIT-derived fields (`fit_avg_power_w`, `fit_normalized_power_w`, `fit_record_count`, …).
- **`sync_log`** — append-only audit trail of sync runs.

A note on Wahoo's responses: every decimal is returned as a string (`"power_avg": "94.59"`). The pipeline casts to float on insert; you can read columns as numeric values directly.

## API notes

| Detail | Value |
|---|---|
| Base URL | `https://api.wahooligan.com` |
| Authorize | `GET /oauth/authorize` |
| Token | `POST /oauth/token` |
| List workouts | `GET /v1/workouts?page=N&per_page=N` (default 30) |
| Workout detail | `GET /v1/workouts/:id` (FIT URL at `workout_summary.file.url`) |
| User profile | `GET /v1/user` |
| Access token TTL | ~2 hours |
| Sandbox rate limit | 25 / 5 min, 100 / hr, 250 / day |
| Production rate limit | 200 / 5 min, 1,000 / hr, 5,000 / day |

The `workout_type_id` enum's mapping isn't published. Empirically, cycling rides come back as `0`. Treat the field as opaque — filter by the FIT `sport` / `sub_sport` columns instead.

The list endpoint returns `workout_summary: null` for every entry, so getting a FIT URL requires a per-workout detail call. The sync pipeline batches and rate-limits these for you.

FIT downloads go through Wahoo's CDN, not the API, and don't count against your rate limit.

## Publishing as a ClawHub skill

```bash
clawhub login
clawhub publish . \
  --slug wahoo-cloud \
  --name "Wahoo Fitness Cloud API" \
  --version 0.1.0 \
  --changelog "Initial release: OAuth2, workout fetch, FIT download/parse, SQLite sync"
```

`clawhub publish` writes a `_meta.json` with your owner ID, version, and registry pointer. That file is gitignored here; let the CLI manage it.

## Security

- Tokens are stored at `~/.openclaw/secrets/wahoo_tokens.json` with mode `0600`.
- `client_id` and `client_secret` come from environment variables, or `~/.openclaw/secrets/wahoo.env` (auto-loaded by `wahoo_auth.py` if env is empty), or `~/.clawdbot/clawdbot.json` — never hardcoded in source. Never paste these into agent chat windows or third-party tools; provide them only to local config files you control.
- FIT files live locally; nothing is uploaded anywhere unless you explicitly add an upload step.
- `.gitignore` blocks `*.env`, `*.db`, `*.fit`, and `*tokens*.json` — verify before committing if you fork.
- The local `wahoo.db` and `wahoo_fit/` directory contain GPS, heart-rate, and power history. They inherit your training-dir permissions (default `~/.openclaw/workspace/training/`). Tighten with `chmod 700 ~/.openclaw/workspace/training` if other local users share the machine.
- `python3 lib/wahoo_auth.py` prints redacted token-file status only (presence, expiry, scope). It never echoes the access or refresh token values.

## Contributing

Issues and PRs welcome, especially:

- Decoding the `workout_type_id` enum across more sports
- Strava / TrainingPeaks export (would require their respective API integrations)
- Power-curve / TSS / training-load analytics on top of the FIT records
- Webhook support for real-time sync (Wahoo supports webhooks; this skill currently polls)

## License

MIT — see [LICENSE.md](LICENSE.md).

## Acknowledgments

- Wahoo Fitness for the API.
- [`fitparse`](https://github.com/dtcooper/python-fitparse) by David Cooper for the FIT decoder.
- [OpenClaw](https://openclaw.dev) and [ClawHub](https://clawhub.ai) for the skill runtime.
