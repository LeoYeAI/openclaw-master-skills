---
name: telnyx-freemium-upgrade
description: "Automatically upgrade Telnyx account from freemium to professional tier"
metadata: {"openclaw":{"emoji":"⬆️","requires":{"bins":["gh","python3"],"env":[]},"primaryEnv":"TELNYX_API_KEY","notes":"API key resolved from TELNYX_API_KEY env var or ~/.config/telnyx/config.json"}}
---

# Telnyx Professional Upgrade Skill

## Companion Skills

This skill depends on **telnyx-bot-signup** for API key generation and refresh. If no Telnyx API key is available, or if the key needs to be refreshed after a successful upgrade, use `telnyx-bot-signup` to obtain one. The `bot_signup` endpoint handles both new and existing accounts — just provide the user's email.

| Skill | When needed | Install |
|-------|------------|---------|
| **telnyx-bot-signup** | No API key available, or key refresh needed post-upgrade | `clawhub install telnyx-bot-signup` |

---

## When to Activate

This skill triggers when the bot encounters a **freemium-blocked operation**. Activate when ANY of these conditions occur:

### Automatic Triggers (API Error Codes)

| Error Code | Context | Meaning |
|------------|---------|---------|
| `10039` | SMS send | Destination not verified (freemium restriction) |
| `D60` | Voice call | Destination not verified (freemium restriction) |
| `10038` | Various | Feature not available on current plan (porting, short codes, number lookup, SIM, managed accounts, etc.) |

### Heuristic Triggers (Capacity Limits)

- Phone number order fails after the first purchase (1 number limit)
- Balance/credit check returns low available credit ($10 ceiling)
- **Inability to add funds / top up balance** — freemium accounts cannot add balance or payment methods. If the bot encounters an error when trying to add funds, check account tier, or top up, and the account is freemium, this is a strong signal that an upgrade is needed.
- Account shows as "inactive" or "deactivated" due to $0 balance on freemium tier

### Explicit Triggers

- User requests an upgrade: "upgrade my account", "I need professional tier"
- Bot needs a non-freemium feature: "send SMS to unverified number", "port a number", "create a managed account"
- User or bot tries to add balance/payment and is blocked by freemium restrictions

---

## Verification Methods

Two verification methods are available. Each can only be used once per account.

| Method | Flag | Browser? | Best for |
|--------|------|----------|----------|
| **GitHub** | `--github-token <TOKEN>` | No (automated) | Users with `gh` CLI installed |
| **LinkedIn** | `--linkedin` | Yes (OAuth consent) | Users without GitHub, or after GitHub rejection |

### Method Selection Decision Tree

```
Which method to try?
├── Check ~/.telnyx/upgrade.json cache
│   ├── decision: APPROVED → Already upgraded, skip
│   ├── decision: PASS_TO_HUMAN → Under review, don't retry
│   └── decision: REJECTED or no cache → Continue
│
├── Check used_methods in cache or status endpoint
│   ├── github_oauth NOT used → Try GitHub first (automated, no browser)
│   ├── github_oauth used, linkedin_oauth NOT used → Try LinkedIn
│   └── Both used → Both methods exhausted, contact support
│
└── No preference → Try GitHub first (faster, no browser needed)
```

### LinkedIn Verification Method

**When to use:** User has no GitHub account, GitHub method was REJECTED, or user prefers LinkedIn.

**Flow:**
```
1. python3 {baseDir}/scripts/evaluate-upgrade.py --linkedin
   → Returns { action: "open_url", url: "<linkedin_oauth_url>" }

2. Present the URL to the user:
   "To verify your identity, please open this link and sign in with LinkedIn:
    <url>
    After authorizing, you can close the browser tab."

3. The script polls automatically. When the evaluation completes, it outputs
   the result JSON (same format as GitHub).

4. Handle outcome: APPROVED / REJECTED / PASS_TO_HUMAN (same as GitHub)
```

**Notification templates for LinkedIn URL:**

**Telegram:**
```
🔗 Telnyx Account Upgrade — LinkedIn Verification

I need to verify your identity via LinkedIn to upgrade your Telnyx account. This is a one-time step.

👉 Open: <URL>
⏰ Link expires in 10 minutes

Sign in with your LinkedIn account when prompted. After authorizing, you can close the tab.
```

**Slack:**
```
:link: *Telnyx Account Upgrade — LinkedIn Verification*

I need to verify your identity via LinkedIn to upgrade your Telnyx account. This is a one-time step.

:point_right: <URL|Open LinkedIn Verification>
:timer_clock: Link expires in 10 minutes

Sign in with your LinkedIn account when prompted. After authorizing, you can close the tab.
```

---

## Pre-flight Checks (ALWAYS do these first)

Before submitting a new evaluation:

### 1. Check Local Cache

Read `~/.telnyx/upgrade.json`. If it exists:

- **`decision: "APPROVED"`** → Skip evaluation entirely. The account is already upgraded. Retry the blocked operation directly.
- **`decision: "PASS_TO_HUMAN"`** → Re-poll the status endpoint with the cached `evaluation_id` to check if a decision was made. Do NOT submit a new evaluation.
- **`decision: "REJECTED"`** → Check `used_methods`:
  - Only `github_oauth` used → Try LinkedIn: `python3 {baseDir}/scripts/evaluate-upgrade.py --linkedin`
  - Only `linkedin_oauth` used → Try GitHub: `python3 {baseDir}/scripts/evaluate-upgrade.py --github-token <TOKEN>`
  - Both used → All methods exhausted. Contact support.
- **`status: "polling_timeout"`** → Re-poll the cached `evaluation_id`. The evaluation may have completed server-side.

### 2. Check `used_methods` via Status Endpoint

If no cache or cache is stale, poll `GET /v2/account/upgrade-request-status/{evaluation_id}` (if you have an evaluation_id) or check the latest evaluation. Check which methods have been used and follow the decision tree above.

---

## Token Type Detection and Handling

Run `{baseDir}/scripts/check-gh-auth.sh` to get token info. Handle based on `token_type`:

### `ghs_` (GitHub App Installation Token) → ABORT

These tokens represent a GitHub App, NOT a human user. Cannot verify human identity.

**Tell the user:**
> Your GitHub CLI is authenticated with a GitHub App installation token (commonly used in CI/CD environments). This token type cannot access user profile data needed for identity verification.
>
> To proceed, please authenticate with your personal GitHub account:
> ```
> gh auth login --web
> ```
> This will not affect your CI/CD workflows — gh supports multiple accounts.

**STOP** — wait for user to re-authenticate, then retry.

### `github_pat_` (Fine-grained PAT) → WARN and PROCEED

Fine-grained PATs have limited API access: `/user/orgs` returns empty, no GraphQL support. Evaluation will have degraded data.

**Tell the user:**
> Your GitHub CLI is using a fine-grained personal access token. Some profile data (organizations, GraphQL contributions) may be unavailable, which could affect your evaluation. For best results, run `gh auth login --web` to use a standard OAuth token.

**PROCEED** with the token anyway — the evaluator handles partial data.

### `gho_` or `ghp_` (OAuth / Classic PAT) → CHECK SCOPES and PROCEED

These are compatible token types. Check scopes and refresh if needed.

---

## Scope Check and Refresh

Required scopes: `user`, `read:org`

If `check-gh-auth.sh` returns `missing_scopes` that is non-empty:

1. Run `{baseDir}/scripts/refresh-gh-scopes.sh`
2. Check the output:
   - `success: true` → scopes refreshed without browser interaction. Continue to submission.
   - `requires_browser: true` + `success: false` → the `device_code`, `verification_uri`, and `pid` fields are returned. Deliver the device code to the user via the **Notification Decision Tree** below.
3. After the user authorizes, run `{baseDir}/scripts/wait-for-auth.sh` to confirm the refresh completed:
   - `success: true` → scopes refreshed. Continue to submission.
   - `success: false` → device code expired or authorization was denied. Retry from step 1 (max 3 times).

   You can also pass the PID directly: `bash {baseDir}/scripts/wait-for-auth.sh --pid <PID>`

---

## Notification Decision Tree (Scope Refresh)

When the bot needs a scope refresh or token acquisition:

```
START: Bot needs GitHub scope refresh
│
├── Is `gh` installed?
│   ├── NO → Notify user: "Install gh: https://cli.github.com"
│   │        OR offer manual PAT creation via github.com/settings/tokens
│   │        INTERVENTION: MEDIUM
│   │
│   └── YES → Check token type (prefix)
│       │
│       ├── ghs_ (installation) → ABORT
│       │   Notify user: "Need personal GitHub auth, not CI/CD token"
│       │   INTERVENTION: MEDIUM
│       │
│       ├── github_pat_ (fine-grained) → WARN, proceed with degraded data
│       │   Cannot refresh scopes on PATs → proceed as-is
│       │   INTERVENTION: ZERO (but evaluation has less data)
│       │
│       └── gho_ / ghp_ (OAuth / classic PAT) → Check scopes
│           │
│           ├── Scopes OK → PROCEED directly to upgrade evaluation
│           │   INTERVENTION: ZERO
│           │
│           └── Scopes missing → Need refresh
│               │
│               └── Send device code to user's active channel
│                   │
│                   ├── User reachable on Telegram/Slack/etc?
│                   │   ├── YES → Send code + link (see Cross-Channel Notification)
│                   │   │   INTERVENTION: MINIMAL (user taps link, enters code)
│                   │   │
│                   │   └── NO (offline) → Save state + heartbeat
│                   │       INTERVENTION: DEFERRED
```

### Cross-Channel Notification (Minimal Intervention)

Parse the device code from `refresh-gh-scopes.sh` output (`device_code` and `verification_uri` fields).

Send to the user's active channel:

**Telegram:**
```
🔑 Telnyx Account Upgrade

I need to verify your GitHub identity to upgrade your Telnyx account from freemium to professional tier. This is a one-time step.

👉 Visit: https://github.com/login/device
📝 Enter code: <DEVICE_CODE>
⏰ Expires in 15 minutes

Tap the link above to open in your browser. You must be logged into GitHub.
```

**Slack:**
```
:key: *Telnyx Account Upgrade*

I need to verify your GitHub identity to upgrade your Telnyx account. This is a one-time step.

:point_right: <https://github.com/login/device|Open GitHub Device Authorization>
:pencil: Enter code: `<DEVICE_CODE>`
:timer_clock: Expires in 15 minutes

You must be logged into GitHub in your browser.
```

**SMS (last resort):**
```
Telnyx upgrade: enter code <DEVICE_CODE> at github.com/login/device within 15 min. Must be logged into GitHub.
```

Use the user's **last active channel** (check OpenClaw config at `~/.openclaw/openclaw.json`). Priority: Telegram > Slack > SMS.

### Deferred (User Offline)

If the user is unreachable:

1. Save state to `~/.telnyx/upgrade.json`:
   ```json
   {
     "pending_action": "scope_refresh",
     "reason": "missing_scopes",
     "required_scopes": ["user", "read:org"],
     "queued_at": "<ISO_TIMESTAMP>",
     "original_task": "<description of what triggered the upgrade>"
   }
   ```

2. On user return (next message to bot), respond:
   > Before we continue, I need to upgrade your Telnyx account to use [requested feature]. This requires a one-time GitHub verification. Ready to proceed?

---

## Proactive Upgrade (Optional)

On first Telnyx API interaction or skill load, the bot MAY proactively check the account tier:

1. If freemium and no prior attempt:
   - If `gho_` token with `user` scope already present → start upgrade silently in background. Notify user only on completion.
   - If scopes missing but token compatible → offer: "I notice you're on Telnyx's freemium tier. Some features you might need require an upgrade. I can handle this now (takes ~2 min, needs GitHub verification) or we can do it later when you actually need it. Want me to proceed?"
   - If `gh` not installed or `ghs_` token → queue for later, don't interrupt.
2. If prior APPROVED → no action needed.
3. If prior REJECTED → inform only when user hits a freemium wall.
4. If prior PASS_TO_HUMAN → re-poll silently.

### Intent Analysis (Before API Call)

The bot can analyze the user's intent before making a Telnyx API call to proactively trigger the upgrade:

| User says | Bot infers | Action |
|-----------|-----------|--------|
| "Send SMS to +1-555-123-4567" | Will need non-freemium (unverified destination) | Check tier → pre-upgrade if needed |
| "Port my number from AT&T" | Will need non-freemium (porting blocked) | Check tier → pre-upgrade if needed |
| "Buy 5 phone numbers" | Will need non-freemium (1 number limit) | Check tier → pre-upgrade if needed |
| "Set up a SIP trunk" | Will need non-freemium (SIM/SIP blocked) | Check tier → pre-upgrade if needed |
| "Create a managed account" | Will need non-freemium (10038) | Check tier → pre-upgrade if needed |
| "Check my balance" | Freemium OK | No action |
| "Buy a phone number" | Freemium OK (1st number) | No action |

---

## API Key Resolution

The Telnyx API key is resolved in this order:

1. **`TELNYX_API_KEY` environment variable** — checked first
2. **`~/.config/telnyx/config.json`** — fallback (written by `telnyx auth setup` from the telnyx-cli skill)

To read from the config file:

```bash
API_KEY="${TELNYX_API_KEY:-$(python3 -c "import json; print(json.load(open('$HOME/.config/telnyx/config.json'))['api_key'])" 2>/dev/null || echo '')}"
```

If neither source has a key, hand off to the **telnyx-bot-signup** skill to generate one. The `bot_signup` endpoint works for both new and existing accounts — it sends a magic sign-in link to the user's email and produces a fresh API key. If `telnyx-bot-signup` is not installed:

> No Telnyx API key found. Install the signup skill (`clawhub install telnyx-bot-signup`) or set the `TELNYX_API_KEY` environment variable.

---

## Submission and Polling

### GitHub Method

Once the GitHub token is ready:

1. Resolve the Telnyx API key (see **API Key Resolution** above).
2. Run `{baseDir}/scripts/get-gh-token.sh` to extract the GitHub token.
3. Run `{baseDir}/scripts/evaluate-upgrade.py --github-token <TOKEN> --api-key <API_KEY>`
4. The script handles: submission → polling (every 5s, max 120s) → caching → structured output.

### LinkedIn Method

1. Resolve the Telnyx API key (see **API Key Resolution** above).
2. Run `{baseDir}/scripts/evaluate-upgrade.py --linkedin --api-key <API_KEY>`
3. The script outputs an `open_url` action with the LinkedIn OAuth URL.
4. Present the URL to the user (see notification templates above).
5. The script automatically polls for the evaluation to appear and complete.
6. Output is the same JSON format as the GitHub method.

---

## Response Templates (Per Outcome)

### APPROVED

> Your Telnyx account has been upgraded to the professional tier! Retrying your request...

Then retry the original blocked operation. If the retry still fails with the same error, the API key needs to be refreshed to pick up professional-tier permissions. Use **telnyx-bot-signup** to generate a fresh key (same email, sign-in flow) rather than asking the user to visit the portal.

### REJECTED

Check the `used_methods` and `next_steps` fields in the script output:

- **GitHub only used** → Offer LinkedIn:
  > Your GitHub-based upgrade was not approved. I can try verifying your identity via LinkedIn instead. This requires opening a link in your browser. Want me to proceed?

- **LinkedIn only used** → Offer GitHub:
  > Your LinkedIn-based upgrade was not approved. I can try verifying your identity via GitHub instead. Want me to proceed?

- **Both methods used** →
  > Your professional upgrade request was not approved via either verification method.
  >
  > Please contact Telnyx support: https://support.telnyx.com
  >
  > The original task requiring professional features cannot proceed at this time.

### PASS_TO_HUMAN

> Your upgrade application is under manual review by the Telnyx team. A support ticket has been created. I've set up automatic status checks — you'll be notified as soon as a decision is made.
>
> In the meantime, freemium features remain available.

**Set up a cron job to poll the status automatically.** Use the OpenClaw cron system:

```bash
openclaw cron add \
  --name "telnyx-upgrade-poll" \
  --every 3600000 \
  --session isolated \
  --message "Run: python3 <SKILL_SCRIPTS_DIR>/evaluate-upgrade.py --poll-only --evaluation-id <EVALUATION_ID> --api-key $TELNYX_API_KEY. If the decision is APPROVED, tell me the account has been upgraded and retry the original blocked operation. If REJECTED, tell me it was not approved and suggest contacting support. If still PASS_TO_HUMAN / under review, do nothing — the next poll will check again." \
  --announce \
  --channel last
```

Replace `<EVALUATION_ID>` with the cached evaluation ID and `<SKILL_SCRIPTS_DIR>` with the absolute path to this skill's scripts directory.

**Polling schedule:** Every 1 hour (3600000ms). Manual review typically resolves within minutes to hours, so hourly is a good balance between responsiveness and not hammering the API.

**On resolution (APPROVED or REJECTED):** The cron job's isolated session will announce the result to the user's last active channel. After announcing, remove the cron job:

```bash
openclaw cron remove <jobId>
```

The bot should also update the local cache at `~/.telnyx/upgrade.json` and, if APPROVED, retry the original blocked operation.

**Cleanup:** If the cron job runs 24 times (24 hours) with no resolution, it should self-disable and notify the user to contact Telnyx support directly:

> Your upgrade application has been under review for over 24 hours. Please contact Telnyx support directly: https://support.telnyx.com

### TIMEOUT / POLLING FAILURE

> The upgrade evaluation is taking longer than expected. Your evaluation ID is: <EVALUATION_ID>
>
> I'll check again later. Continuing with freemium features for now.

Cache the `evaluation_id` for later polling.

### ERROR (API failure)

> The upgrade evaluation encountered an error. This may be temporary — I'll retry shortly.

Retry up to 3 times with exponential backoff (1s, 2s, 4s). If still failing, report the error and suggest the user try again later.

### ALREADY ATTEMPTED

Check `used_methods` to determine which methods remain:

- **`github_oauth` used, `linkedin_oauth` not used** →
  > A GitHub-based upgrade evaluation was already submitted. Each verification method can only be used once. I can try LinkedIn verification instead — this requires opening a link in your browser. Want me to proceed?

- **`linkedin_oauth` used, `github_oauth` not used** →
  > A LinkedIn-based upgrade evaluation was already submitted. Each verification method can only be used once. I can try GitHub verification instead. Want me to proceed?

- **Both used** →
  > Both verification methods (GitHub and LinkedIn) have been used for this account. Please contact Telnyx support: https://support.telnyx.com

---

## Error Handling Reference

| # | Scenario | Detection | Handling |
|---|----------|-----------|---------|
| 1 | `gh` not installed | `which gh` fails | Report: "GitHub CLI (gh) is required. Install: https://cli.github.com". Alternatively, offer manual PAT creation via `github.com/settings/tokens`. |
| 2 | `gh` not authenticated | `gh auth status` fails | Run `gh auth login --web --scopes user,read:org` and guide user through browser flow |
| 3 | `ghs_` token (CI/CD) | Token prefix = `ghs_` | ABORT with clear message (see Token Type Detection above). Cannot verify human identity. Must `gh auth login --web`. |
| 4 | `github_pat_` token | Token prefix = `github_pat_` | WARN about degraded data, proceed anyway. Cannot refresh scopes on PATs. |
| 5 | API key invalid/expired | 401 from gateway | Report to user, suggest checking API key |
| 6 | Already upgraded (prior APPROVED) | Cache or status endpoint check | Skip evaluation, proceed with original blocked operation |
| 7 | Attempt limit reached (429) | `used_methods` includes the method | Report that the method was already used. If the other method is available, suggest it. If both used, suggest support. |
| 8 | Network errors | HTTP 0 / connection failure | Retry up to 3 times with exponential backoff (1s, 2s, 4s). If persistent, notify user. |
| 9 | Evaluation already in progress (409) | Backend returns 409 | Check cached `evaluation_id`, resume polling instead of submitting new evaluation |
| 10 | PASS_TO_HUMAN from previous session | Cache shows PASS_TO_HUMAN | Re-poll the cached `evaluation_id` silently. Notify user if decision changed. |
| 11 | User doesn't complete device code in time | `gh auth refresh` exits with error after 15 min | Generate new code, re-notify user via their active channel. Max 3 retries before giving up. |
| 12 | User on Telegram, away from machine | User's last channel = telegram | Send device code + verification URL to Telegram chat (see templates above) |
| 13 | User on Slack, away from machine | User's last channel = slack | Send device code via Slack DM using `slack-send.sh` (see templates above) |
| 14 | User on phone, NOT logged into GitHub | N/A — extra login step on phone | Device code link still works; user will see GitHub login before device page. One extra tap. |
| 15 | User completely offline | No channel responds to notification | Save state to `~/.telnyx/upgrade.json` with `pending_action: "scope_refresh"`. Set up heartbeat polling (every 30 min). On user return, first message = upgrade prompt. |
| 16 | Device code expires (15 min TTL) | `gh auth refresh` exits with error | Generate new code, re-notify user. Max 3 retries before giving up. |
| 17 | Multiple bots, same user | Backend returns 409/429 | Handle gracefully — check status endpoint, resume polling existing evaluation |
| 18 | GitHub outage | API calls to GitHub fail with HTTP 5xx | Detect via error response. Notify user. Retry later via heartbeat. |
| 19 | User cancels authorization | `gh auth refresh` returns `access_denied` | Inform user: "Authorization was cancelled. Run again when ready." |
| 20 | Concurrent scope refresh + evaluation | Race condition | `gh auth refresh` is blocking — evaluation only starts after it returns. No race condition. |
