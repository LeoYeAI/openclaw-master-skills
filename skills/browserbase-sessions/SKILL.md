---
name: browserbase-sessions
description: Create and manage persistent Browserbase cloud browser sessions with authentication persistence. Use when you need to automate browsers, maintain logged-in sessions across interactions, scrape authenticated pages, or manage cloud browser instances.
license: MIT
homepage: https://docs.browserbase.com
metadata: {"author":"custom","version":"2.5.0","openclaw":{"emoji":"🌐","requires":{"bins":["python3"]},"primaryEnv":"BROWSERBASE_API_KEY"}}
---

# Browserbase Sessions Skill

Manage persistent cloud browser sessions via Browserbase. This skill creates browser sessions that preserve authentication (cookies, local storage) across interactions, automatically solve CAPTCHAs, and record sessions for later review.

## Agent Checklist (Be Proactive)

- If `BROWSERBASE_API_KEY` or `BROWSERBASE_PROJECT_ID` is missing, **ask the user for them** (and tell them where to find them). Do not run Browserbase commands until both are configured.
- If commands fail due to missing Python deps (ImportError for `browserbase` / `playwright`), run:
  - `python3 {baseDir}/scripts/browserbase_manager.py install`
  - Then retry the original command.
- Ask the user what they want to persist and how they want to organize it:
  - **Workspace per app/site** (isolation): `github`, `slack`, `stripe`
  - **Workspace per task/project** (multi-site workflow): `invoice-run`, `lead-gen`, `expense-recon`
- Workspaces persist:
  - Login state via Browserbase **Contexts** (cookies + storage)
  - Open tabs (URL + title snapshot) so you can restore where you left off
- Prefer workspace commands (`create-workspace`, `start-workspace`, `resume-workspace`, `stop-workspace`) over raw session commands when the user wants the browser to stay open across chat turns.
- Prefer direct interaction commands (`list-tabs`, `new-tab`, `switch-tab`, `close-tab`, `click`, `type`, `press`, `wait-for`, `go-back`, `go-forward`, `reload`, `read-page`) before falling back to `execute-js`.
- If a workspace/session has a `pending_handoff`, **check it first** before doing anything else:
  - `python3 {baseDir}/scripts/browserbase_manager.py handoff --action check --workspace <ws>`
  - If not done, resend `suggested_user_message` and stop.
- Whenever a browser is opened (`start-workspace`, `resume-workspace`, or `create-session`), immediately share the human remote-control link:
  - Prefer `human_handoff.share_url` from command output.
  - Prefer `human_handoff.share_text` / `human_handoff.share_markdown` when replying to the user.
  - Fallback to `human_control_url`.
  - If missing, run `live-url` and share its `human_handoff.share_url`.
- When you need the user to perform a manual step (SSO/MFA/captcha/consent screens), use a **handoff with a completion check**:
  - Set: `python3 {baseDir}/scripts/browserbase_manager.py handoff --action set --workspace <ws> --instructions "<what to do>" --url-contains "<post-step url fragment>"` (or `--selector/--text/--cookie-name/...`)
  - Verify later: `python3 {baseDir}/scripts/browserbase_manager.py handoff --action check --workspace <ws>` (or `--action wait`)
- When closing, use `stop-workspace` (not `terminate-session`) so tabs are snapshotted and auth state is persisted.

## Prompt-Optimized Response Patterns

Use short, consistent responses so users always know next actions.

When credentials are missing:
```text
I need your Browserbase credentials before I can open a browser.
Please provide:
1) BROWSERBASE_API_KEY
2) BROWSERBASE_PROJECT_ID
```

When browser is opened (session/workspace):
```text
Browser is ready.
<human_handoff.share_text>
I can keep working while you browse.
```

When resuming an existing workspace:
```text
Reconnected to your existing workspace.
<human_handoff.share_text>
```

When a human step is required (SSO/MFA/consent screens):
```text
I need you to do one step in the live browser:
1) <exact steps>

Open: <human_handoff.share_url>
Stop when you reach: <a specific completion state (URL contains / selector visible)>.
I’ll detect it and continue automatically. If I don’t, reply “done” and I’ll re-check.
```

When live URL is temporarily unavailable:
```text
The remote-control URL is temporarily unavailable. I’ll retry now.
```

## First-Time Setup

### Step 1 — Get your Browserbase credentials

1. Sign up at [browserbase.com](https://www.browserbase.com/) if you haven't already.
2. Go to **Settings → API Keys** and copy your API key (starts with `bb_live_`).
3. Go to **Settings → Project** and copy your Project ID (a UUID).

If you have the API key but aren’t sure which Project ID to use, you can list projects:

```bash
export BROWSERBASE_API_KEY="bb_live_your_key_here"
python3 {baseDir}/scripts/browserbase_manager.py list-projects
```

### Step 2 — Install dependencies

Install Python deps and Playwright Chromium (recommended):

```bash
python3 {baseDir}/scripts/browserbase_manager.py install
```

Manual alternative (pip/uv):

```bash
cd {baseDir}/scripts && pip install -r requirements.txt
python3 -m playwright install chromium
```

### Step 3 — Set environment variables

```bash
export BROWSERBASE_API_KEY="bb_live_your_key_here"
export BROWSERBASE_PROJECT_ID="your-project-uuid-here"
```

Or configure via OpenClaw's `skills.entries["browserbase-sessions"].env` in `~/.openclaw/openclaw.json` (JSON5). Because this skill sets `primaryEnv: BROWSERBASE_API_KEY`, you can also use `skills.entries["browserbase-sessions"].apiKey` for the API key:

```json5
{
  skills: {
    entries: {
      "browserbase-sessions": {
        enabled: true,
        apiKey: "bb_live_your_key_here",
        env: {
          BROWSERBASE_PROJECT_ID: "your-project-uuid-here"
        }
      }
    }
  }
}
```

### Step 4 — Run the setup test

This validates everything end-to-end (credentials, SDK, Playwright, API connection, and a live smoke test):

```bash
python3 {baseDir}/scripts/browserbase_manager.py setup --install
```

You should see `"status": "success"` with all steps passing. If any step fails, the error message tells you exactly what to fix.

## Defaults

Every session is created with these defaults to support research workflows:

- **Captcha solving: ON** — Browserbase automatically solves CAPTCHAs so login flows and protected pages work without manual intervention. Disable with `--no-solve-captchas`.
- **Session recording: ON** — Browserbase records sessions (video in the Dashboard; rrweb events retrievable via API). Disable with `--no-record`.
- **Session logging: ON** — Browserbase captures session logs retrievable via API. Disable with `--no-logs`.
- **Auth persistence** — If you use a Context (or Workspace), auth state is persisted by default. Disable persistence with `--no-persist`.

## Capabilities & Limitations (Be Explicit)

The agent can:
- Create/inspect/terminate Browserbase sessions and contexts.
- Keep a browser “open” across chat turns using workspaces (keep-alive sessions + restore tabs).
- Persist login state across sessions via Browserbase Contexts (`persist=true`).
- Restore your place by reopening the last saved set of open tabs (URL + title snapshot).
- Provide a live debugger URL so the user can browse manually while the agent continues working.
- Use interactive browser controls: list/open/switch/close tabs, click/type/press keys, wait for selectors/text/url states, go back/forward/reload, and read page text/html/links.
- Take screenshots, run JavaScript, read cookies, fetch logs, and fetch rrweb recording events.

The agent cannot:
- Keep sessions running indefinitely (Browserbase enforces timeouts; max is 6 hours).
- Restore full back/forward browser history (only open URLs are restored).
- Passively “watch” what the user is doing in the live debugger. To detect human actions, the agent must reconnect and **check for specific completion conditions** (selector/text/url/cookie/storage) using `handoff` or `wait-for`.
- Bypass MFA/SSO without user participation.
- Download the Dashboard video via API (the API returns rrweb events, not a video file).

## Available Commands

All commands are run via the manager script:

```bash
python3 {baseDir}/scripts/browserbase_manager.py <command> [options]
```

### Setup & Validation

Install deps (only needed once per environment):
```bash
python3 {baseDir}/scripts/browserbase_manager.py install
```

Run the full setup test:
```bash
python3 {baseDir}/scripts/browserbase_manager.py setup --install
```

### Workspaces (Recommended)

Workspaces are the recommended way to keep a browser "open" while chatting and then pick up later. A workspace combines:
- A Browserbase **Context** (persists cookies + local/session storage, so you stay logged in)
- A local **tab snapshot** (URLs + titles) so tabs can be restored into the next session (note: this restores open URLs, not full back/forward browser history)
- The current **active session id** so the agent can reconnect

#### Task workspaces (multi-site flows)

A single Browserbase Context is a browser profile, so it can keep you logged into **multiple sites at once**. For workflows like “do something on Site A, then do something on Site B”, create a **task workspace** and keep both sites open as tabs:

```bash
python3 {baseDir}/scripts/browserbase_manager.py create-workspace --name invoice-run
python3 {baseDir}/scripts/browserbase_manager.py start-workspace --name invoice-run --timeout 21600
python3 {baseDir}/scripts/browserbase_manager.py live-url --workspace invoice-run
```

If you need account/cookie isolation (different logins, fewer cross-site side effects), use separate workspaces per app/site instead.

Create and start a workspace:
```bash
python3 {baseDir}/scripts/browserbase_manager.py create-workspace --name github
python3 {baseDir}/scripts/browserbase_manager.py list-workspaces
python3 {baseDir}/scripts/browserbase_manager.py start-workspace --name github --timeout 21600
# Share this field with the user immediately:
# human_handoff.share_url (fallback: human_control_url / live_urls.debugger_url)
```

Note: `start-workspace` performs a short “warm connect” via Playwright so the session doesn’t die from the 5-minute connect requirement, even if the user hasn’t opened the live debugger yet.

While the user is browsing in the live debugger, the agent can keep working. To resume later:
```bash
python3 {baseDir}/scripts/browserbase_manager.py resume-workspace --name github
```

For long-running sessions (especially when the user is opening/closing tabs manually), take snapshots periodically:
```bash
python3 {baseDir}/scripts/browserbase_manager.py snapshot-workspace --name github
```

To persist login + tabs when you are done, always stop via the workspace command:
```bash
python3 {baseDir}/scripts/browserbase_manager.py stop-workspace --name github
```

To inspect what a workspace has saved (context id, active session id, tabs, history):
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-workspace --name github
```

Most commands accept `--workspace <name>` instead of `--session-id`:
```bash
python3 {baseDir}/scripts/browserbase_manager.py navigate --workspace github --url "https://github.com/settings/profile"
python3 {baseDir}/scripts/browserbase_manager.py screenshot --workspace github --output /tmp/profile.png
python3 {baseDir}/scripts/browserbase_manager.py execute-js --workspace github --code "document.title"
```

### Context Management (for authentication persistence)

Create a named context to store login state:
```bash
python3 {baseDir}/scripts/browserbase_manager.py create-context --name github
```

List all saved contexts:
```bash
python3 {baseDir}/scripts/browserbase_manager.py list-contexts
```

Delete a context (by name or ID):
```bash
python3 {baseDir}/scripts/browserbase_manager.py delete-context --context-id github
```

### Session Lifecycle

Create a new session (captcha solving, recording, and logging enabled by default):
```bash
# Basic session
python3 {baseDir}/scripts/browserbase_manager.py create-session

# Session with saved context (persist=true by default when a context is used)
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id github

# Keep-alive session for long research (survives disconnections)
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id github --keep-alive --timeout 3600

# Full options
python3 {baseDir}/scripts/browserbase_manager.py create-session \
  --context-id github \
  --keep-alive \
  --timeout 3600 \
  --region us-west-2 \
  --proxy \
  --block-ads \
  --viewport-width 1280 \
  --viewport-height 720
```

List all sessions:
```bash
python3 {baseDir}/scripts/browserbase_manager.py list-sessions
python3 {baseDir}/scripts/browserbase_manager.py list-sessions --status RUNNING
```

Get session details:
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-session --session-id <id>
```

Terminate a session:
```bash
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>
```

### Browser Automation

Navigate to a URL:
```bash
# Navigate and get page title
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com"

# Navigate and extract text
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com" --extract-text

# Navigate and save screenshot
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com" --screenshot /tmp/page.png

# Navigate and take full-page screenshot
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com" --screenshot /tmp/full.png --full-page
```

Manage tabs:
```bash
python3 {baseDir}/scripts/browserbase_manager.py list-tabs --session-id <id>
python3 {baseDir}/scripts/browserbase_manager.py new-tab --session-id <id> --url "https://example.org"
python3 {baseDir}/scripts/browserbase_manager.py switch-tab --session-id <id> --tab-index 1
python3 {baseDir}/scripts/browserbase_manager.py close-tab --session-id <id> --tab-url-contains "example.org"
```

Interact with the page:
```bash
python3 {baseDir}/scripts/browserbase_manager.py click --session-id <id> --selector "button[type='submit']"
python3 {baseDir}/scripts/browserbase_manager.py type --session-id <id> --selector "input[name='email']" --text "user@example.com" --clear
python3 {baseDir}/scripts/browserbase_manager.py press --session-id <id> --key "Enter"
python3 {baseDir}/scripts/browserbase_manager.py wait-for --session-id <id> --selector ".dashboard-ready" --timeout-ms 45000
```

Control navigation state:
```bash
python3 {baseDir}/scripts/browserbase_manager.py go-back --session-id <id>
python3 {baseDir}/scripts/browserbase_manager.py go-forward --session-id <id>
python3 {baseDir}/scripts/browserbase_manager.py reload --session-id <id>
```

Read the current page:
```bash
python3 {baseDir}/scripts/browserbase_manager.py read-page --session-id <id> --max-text-chars 20000
python3 {baseDir}/scripts/browserbase_manager.py read-page --session-id <id> --include-links --max-links 30
python3 {baseDir}/scripts/browserbase_manager.py read-page --session-id <id> --include-html --max-html-chars 120000
```

Take a screenshot of the current page (without navigating):
```bash
python3 {baseDir}/scripts/browserbase_manager.py screenshot --session-id <id> --output /tmp/current.png
python3 {baseDir}/scripts/browserbase_manager.py screenshot --session-id <id> --output /tmp/full.png --full-page
```

Execute JavaScript:
```bash
python3 {baseDir}/scripts/browserbase_manager.py execute-js --session-id <id> --code "document.title"
```

Get cookies:
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-cookies --session-id <id>
```

All of the commands above also support `--workspace <name>` so the active workspace session is used automatically.

### Recordings, Logs & Debug

Fetch rrweb recording events (session must be terminated first):
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-recording --session-id <id> --output /tmp/session.rrweb.json
```

Download files saved during the session (archive):
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-downloads --session-id <id> --output /tmp/downloads.zip
```

Get session logs:
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-logs --session-id <id>
```

Get the live debug URL (for visual inspection of a running session):
```bash
python3 {baseDir}/scripts/browserbase_manager.py live-url --session-id <id>
# Share: human_handoff.share_url
```

### Human Handoff (Manual Steps)

Use `handoff` when the user must do something manually (SSO/MFA/consent screens) and you want to **detect completion** and resume automatically.

Completion checks (pick the most reliable signal you can):
- Prefer `--url-contains` for post-login destinations (e.g. `/dashboard`, `/app`, `/settings`).
- Use `--selector` when the URL doesn’t change (SPAs).
- Use `--cookie-name`, `--local-storage-key`, `--session-storage-key` only when you know a stable auth indicator.

Combining checks:
- Default is `--match all` (AND): all provided checks must be true.
- Use `--match any` (OR) when you want multiple fallback signals (e.g., URL contains `/dashboard` OR selector `.dashboard-ready`).

Set a handoff (store the instructions + completion check):
```bash
python3 {baseDir}/scripts/browserbase_manager.py handoff \
  --action set \
  --workspace myapp \
  --instructions "Log in and stop on the dashboard." \
  --url-contains "/dashboard"
```

Fallback example (any-of):
```bash
python3 {baseDir}/scripts/browserbase_manager.py handoff \
  --action set \
  --workspace myapp \
  --instructions "Complete login and stop on the dashboard." \
  --url-contains "/dashboard" \
  --selector ".dashboard-ready" \
  --match any
```

Tip: `handoff --action set` returns `suggested_user_message.text` / `suggested_user_message.markdown` so you can paste a consistent “hey human do this” message (with the live debugger URL) to the user.

Later, verify once:
```bash
python3 {baseDir}/scripts/browserbase_manager.py handoff --action check --workspace myapp
```

Or wait up to 5 minutes (default) for completion:
```bash
python3 {baseDir}/scripts/browserbase_manager.py handoff --action wait --workspace myapp
```

## Common Workflows

### Workflow 1: Multi-session research with persistent login

```bash
# 1. One-time: create a workspace for the site (creates a Browserbase Context + local state)
python3 {baseDir}/scripts/browserbase_manager.py create-workspace --name myapp

# 2. Start a keep-alive session (tabs restored from last snapshot, login persisted via context)
python3 {baseDir}/scripts/browserbase_manager.py start-workspace --name myapp --timeout 3600

# 3. Open the live debugger URL so the user can log in / browse while you keep chatting
python3 {baseDir}/scripts/browserbase_manager.py live-url --workspace myapp

# 4. Do research, take screenshots (workspace auto-tracks tabs + history)
python3 {baseDir}/scripts/browserbase_manager.py navigate --workspace myapp --url "https://myapp.com/dashboard" --extract-text
python3 {baseDir}/scripts/browserbase_manager.py screenshot --workspace myapp --output /tmp/dashboard.png

# 5. When done: stop-workspace snapshots tabs + persists auth state back to the context
python3 {baseDir}/scripts/browserbase_manager.py stop-workspace --name myapp

# 6. Later: resume and pick up where you left off
python3 {baseDir}/scripts/browserbase_manager.py resume-workspace --name myapp
```

### Workflow 1b: Task workflow across multiple sites (persist tabs + logins)

```bash
# 1) Create a task workspace (one browser profile that can stay logged into multiple sites)
python3 {baseDir}/scripts/browserbase_manager.py create-workspace --name lead-gen

# 2) Start it and open the live debugger so the user can log in on both sites
python3 {baseDir}/scripts/browserbase_manager.py start-workspace --name lead-gen --timeout 21600
python3 {baseDir}/scripts/browserbase_manager.py live-url --workspace lead-gen

# 3) Agent can navigate and capture state while you chat (tabs snapshot includes both Site A and Site B)
python3 {baseDir}/scripts/browserbase_manager.py navigate --workspace lead-gen --url "https://site-a.example.com" --extract-text
python3 {baseDir}/scripts/browserbase_manager.py navigate --workspace lead-gen --url "https://site-b.example.com" --extract-text

# 4) If the user is manually opening/closing tabs in the debugger, snapshot occasionally:
python3 {baseDir}/scripts/browserbase_manager.py snapshot-workspace --name lead-gen

# 5) Stop to persist auth + tabs snapshot
python3 {baseDir}/scripts/browserbase_manager.py stop-workspace --name lead-gen
```

### Workflow 2: Screenshot documentation

```bash
python3 {baseDir}/scripts/browserbase_manager.py create-session
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://docs.example.com" --screenshot /tmp/docs_home.png
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://docs.example.com/api" --screenshot /tmp/docs_api.png --full-page
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>
```

### Workflow 3: Record and share a walkthrough

```bash
# Session recording is ON by default
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id myapp
# ... do your walkthrough (navigate, click, etc.) ...
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>
# Save rrweb recording events
# (Video is available in the Browserbase Dashboard; this fetches rrweb events)
python3 {baseDir}/scripts/browserbase_manager.py get-recording --session-id <id> --output /tmp/walkthrough.rrweb.json
```

## Important Notes

- **Captcha solving is ON by default.** Browserbase handles CAPTCHAs automatically during login flows and page loads. Use `--no-solve-captchas` to disable.
- **Recording is ON by default.** Video is available in the Browserbase Dashboard; `get-recording` fetches rrweb events (primary tab) for programmatic replay. Use `--no-record` to disable.
- **Logging is ON by default.** Use `get-logs` to retrieve logs; disable with `--no-logs`.
- **Connection timeout**: 5 minutes to connect after creation before auto-termination.
- **Keep-alive sessions** survive disconnections and must be explicitly terminated.
- **Context persistence**: When a session was created with a context using `persist=true` (default), wait a few seconds after termination before creating a new session with the same context.
- **Named contexts**: Use `--name` with `create-context` to save friendly names (e.g. `github`, `slack`). Use the name anywhere a context ID is expected.
- **Workspace state**: Workspaces are stored locally under `~/.browserbase/workspaces/<name>.json` (or `BROWSERBASE_CONFIG_DIR/workspaces`). They include the context id, active session id, and the last saved tab snapshot.
- **One context per site**: Use separate contexts for different authenticated sites.
- **Avoid concurrent sessions on the same context**.
- **Regions**: us-west-2 (default), us-east-1, eu-central-1, ap-southeast-1.
- **Session timeout**: 60–21600 seconds (max 6 hours).
- **Costs/limits**: Your Browserbase plan has limits (browser hours, proxy data, concurrency). Keep-alive sessions consume hours while running; terminate sessions and set reasonable `--timeout` values to control cost. Check your Browserbase dashboard for current quotas.

## Error Handling

All commands return JSON output. On error, the output includes an `"error"` key. Common errors:
- `APIConnectionError`: Browserbase API unreachable
- `RateLimitError`: Too many concurrent sessions for your plan
- `APIStatusError`: Invalid parameters or authentication failure
- Missing env vars: Set `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`

## Reference

For full API details, read `{baseDir}/references/api-quick-ref.md`.
