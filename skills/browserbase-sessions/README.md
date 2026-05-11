# Browserbase Sessions — OpenClaw Skill

A production-ready OpenClaw skill for creating and managing persistent Browserbase
cloud browser sessions with authentication persistence, automatic captcha solving,
session recording, and screenshot capture.

## What it does

This skill gives the OpenClaw agent the ability to:

- **Create cloud browser sessions** via Browserbase's infrastructure
- **Persist authentication** across sessions using Contexts (cookies, local storage,
  session storage are saved and restored automatically)
- **Use workspaces for persistence** — a workspace ties together a Context + active session id
  + a local tab snapshot so you can resume where you left off. A workspace can be:
  - per app/site (isolation), or
  - per task/project (multi-site workflows)
- **Solve CAPTCHAs automatically** — login flows and protected pages work without
  manual intervention (enabled by default)
- **Record sessions** — Browserbase records sessions (video replay in the Dashboard;
  rrweb events retrievable via API) (enabled by default)
- **Download session files** — fetch an archive of any files downloaded during the session
- **Take screenshots** — viewport or full-page, during navigation or on demand
- **Reconnect to keep-alive sessions** that survive disconnections
- **Share human remote-control links** so users can take over in Browserbase Live Debugger
- **Run human-in-the-loop handoffs** — tell the user what to do and detect completion via checks (selector/text/url/cookie/storage)
- **Automate browsing** — navigate, manage tabs, click/type/press, wait for UI state, read page content, execute JavaScript, and read cookies
- **Manage session lifecycle** — list, inspect, and terminate sessions

## Requirements

- Python 3.9+
- `browserbase` Python package
- `playwright` Python package + Chromium browser
- A Browserbase account with API key and project ID

## Quick Start

### 1. Copy the skill to your OpenClaw skills directory

```bash
cp -r browserbase-sessions/ ~/.openclaw/workspace/skills/browserbase-sessions/
```

Notes:
- Workspace skills live under `<workspace>/skills` (default workspace: `~/.openclaw/workspace`).
- For a globally managed skill, you can place it under `~/.openclaw/skills/` and enable it in `~/.openclaw/openclaw.json`.

### 2. Install dependencies

```bash
python3 ~/.openclaw/workspace/skills/browserbase-sessions/scripts/browserbase_manager.py install
```

### 3. Set credentials

```bash
export BROWSERBASE_API_KEY="bb_live_your_key_here"
export BROWSERBASE_PROJECT_ID="your-project-uuid-here"
```

If you have the API key but aren’t sure which Project ID to use:

```bash
python3 ~/.openclaw/workspace/skills/browserbase-sessions/scripts/browserbase_manager.py list-projects
```

### 4. Run the setup test

```bash
python3 ~/.openclaw/workspace/skills/browserbase-sessions/scripts/browserbase_manager.py setup --install
```

This validates everything end-to-end: credentials, SDK, Playwright, API connection, and runs a live smoke test (creates a session, navigates to example.com, terminates).

## Available Commands

| Command | Description |
|---|---|
| `install` | Install Python deps + Playwright Chromium |
| `setup` | Validate credentials and run full smoke test |
| `list-projects` | List Browserbase projects for this API key |
| `create-context` | Create a persistent context (with optional `--name`) |
| `delete-context` | Delete a context |
| `list-contexts` | List saved named contexts |
| `create-workspace` | Create a named workspace (context + local tab snapshot) |
| `list-workspaces` | List local workspaces |
| `get-workspace` | Get workspace details |
| `delete-workspace` | Delete a local workspace (optionally delete remote context) |
| `start-workspace` | Start a keep-alive session for a workspace (restore tabs by default) |
| `resume-workspace` | Reconnect to an existing workspace session or start a new one |
| `snapshot-workspace` | Save current open tabs to the workspace |
| `stop-workspace` | Snapshot tabs and terminate the active workspace session |
| `create-session` | Create a browser session (captchas + recording + logs ON by default) |
| `list-sessions` | List all sessions |
| `get-session` | Get session details |
| `terminate-session` | Terminate a running session |
| `navigate` | Navigate to a URL (with optional screenshot and text extraction) |
| `list-tabs` | List open tabs in the primary browser context |
| `new-tab` | Open a new tab (optionally navigate immediately) |
| `switch-tab` | Switch to a specific tab by index or URL match |
| `close-tab` | Close a tab by index or URL match |
| `click` | Click an element on the current/selected tab |
| `type` | Type/fill text into an element |
| `press` | Press a key on the page or in an element |
| `wait-for` | Wait for selector/text/url/load-state conditions |
| `go-back` | Navigate back in history |
| `go-forward` | Navigate forward in history |
| `reload` | Reload the current page |
| `read-page` | Read page text/html/links from the current tab |
| `screenshot` | Take a screenshot of the current page |
| `execute-js` | Execute JavaScript in a session |
| `get-cookies` | Get cookies from a session |
| `get-recording` | Fetch session rrweb recording events |
| `get-downloads` | Download files saved during the session (archive) |
| `get-logs` | Get session logs |
| `handoff` | Create/check/clear a human handoff request (manual steps with completion checks) |
| `live-url` | Get live debug URL for a running session |

## Key Design Decisions

**Captcha solving ON by default.** Browserbase's captcha solver handles reCAPTCHA,
hCaptcha, and other challenges automatically. This means login flows and protected
pages work without manual intervention. Disable with `--no-solve-captchas`.

**Recording ON by default.** Video replay is available in the Browserbase Dashboard.
Use `get-recording` to fetch rrweb events (primary tab) for programmatic replay.
Disable with `--no-record`.

**Logging ON by default.** Use `get-logs` for programmatic debugging/traceability.
Disable with `--no-logs`.

**Named contexts.** Instead of remembering UUIDs, name your contexts (`--name github`,
`--name slack`) and reference them by name anywhere a context ID is expected.

**Workspaces.** For “keep the browser open while we chat” workflows, prefer workspaces:
`create-workspace`, `start-workspace`, `resume-workspace`, and `stop-workspace`. Workspaces
ensure auth persistence and snapshot/restore open tabs between sessions.

**Direct interaction primitives.** Prefer first-class commands (`click`, `type`, `wait-for`,
tab commands, history commands, `read-page`) for reliability and consistent outputs; use
`execute-js` as an escape hatch when needed.

**Human handoff links.** Session-opening commands return `human_control_url` (plus fullscreen variant)
plus a `human_handoff` object (`share_url`, `share_text`) so the agent can immediately send
a polished remote-control message to the user.

**Human handoff completion checks.** Use the `handoff` command to store “hey human do this” instructions
plus a completion signal (selector/text/url/cookie/storage). Then the agent can check/wait and automatically
resume once the condition is satisfied.

Example:
```bash
python3 scripts/browserbase_manager.py handoff \
  --action set \
  --workspace myapp \
  --instructions "Log in and stop on the dashboard." \
  --url-contains "/dashboard"
python3 scripts/browserbase_manager.py handoff --action check --workspace myapp
```

**Prompt polish.** Prefer `human_handoff.share_text` (or `share_markdown`) directly in user replies
to keep handoff responses short, clear, and consistent.

**Task workspaces (multi-site).** A single workspace Context can hold logins for multiple
sites, so if a workflow spans Site A and Site B, make one workspace named after the task
and keep both sites open as tabs. If you need isolation, use separate workspaces per app/site.

**Keep-alive for research.** Set `--keep-alive` for long research sessions. The browser
survives network disconnections and persists until explicitly terminated — up to 6 hours.

## Architecture

This skill follows the AgentSkills open standard (agentskills.io):

- `SKILL.md` — Instructions the agent reads on-demand
- `scripts/browserbase_manager.py` — CLI tool the agent executes via bash
- `references/api-quick-ref.md` — API reference for deeper details

## License

MIT
