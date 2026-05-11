# Auth Module

Authenticate with Topview using the OAuth 2.0 Device Authorization Grant.
Run once — credentials are saved locally and auto-loaded by all other modules.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `login`  | Full flow: init → open browser → poll → save credentials |
| `poll`   | Resume a previously interrupted login (recovery only) |
| `logout` | Remove saved credentials file |
| `status` | Show current login state (uid, email, name, masked api_key) |

## Usage

```bash
python {baseDir}/scripts/auth.py <subcommand>
```

## `login` — Complete Login Flow

```bash
python {baseDir}/scripts/auth.py login
```

This single command handles the **entire login flow**:
1. Calls the remote OAuth server to start a device session
2. Opens the authorization page in the user's browser
3. Automatically polls until the user authorizes (or the session expires)
4. Saves credentials to `~/.topview/credentials.json` on success

**The agent must extract the `URL:` from the login output and send it to the user as a clickable link.**

Many users are in chat apps (Feishu, etc.) and **cannot see browser popups**. The script does call `webbrowser.open()` but this may not be visible — the direct link is the only reliable way.

### Full sequence

```
Agent runs:  python auth.py login
                 ↓ script prints URL and opens browser (user may not see the browser)
                 ↓ command keeps polling automatically in background
Agent sends user: the direct authorization link (see SKILL.md login template)
                 ↓ user clicks the link, logs in, clicks Authorize
                 ↓ command detects approval, saves credentials
Credentials saved to ~/.topview/credentials.json ✓
```

### What to send the user

Extract the `URL: https://...` line from the login output and use the login message template from SKILL.md. The template includes both Chinese and English versions — pick the one matching the user's language.

**Do NOT say** "浏览器已经打开" or "请在浏览器中操作" or "去那台电脑上看" — the user cannot see the browser or the machine running the agent.

**Do NOT tell the user to register at topview.ai first.** The authorization page includes both login and registration. New users can sign up directly on that page.

**Do NOT ask the user "which method do you want?"** — just run `auth.py login`, get the link, and send it. Login is a means, not a choice to present.

### If the URL is missing from the output

If `auth.py login` was run in the background or the output was not captured and you cannot find the `URL:` line:

1. **Re-run `auth.py login`** to start a new session and capture the URL this time.
2. **NEVER** fall back to telling the user to "check the browser popup" or "go to the computer". The user **cannot** see the agent's machine.
3. The old session will expire on its own — starting a new one is safe.

## `poll` — Resume Interrupted Login

```bash
python {baseDir}/scripts/auth.py poll
```

Use **only** if `login` was interrupted (e.g., terminal closed during polling).
Reads the pending session from `~/.topview/pending_device.json` and resumes polling.

## `status` — Check Login State

```bash
python {baseDir}/scripts/auth.py status
```

Output when logged in:

```
Logged in
  uid:         NsDAaOPF4jLuAie4ewyg
  name:        John Doe
  email:       user@example.com
  api_key:     sk-...3HB
  charge_type: pro
  authorized:  2026-03-04T10:00:00+00:00
  file:        /Users/you/.topview/credentials.json
```

## `logout` — Remove Credentials

```bash
python {baseDir}/scripts/auth.py logout
```

## Credential File

Saved at: `~/.topview/credentials.json`. File permissions are set to `0600` (owner read/write only).

## Credential Load Priority

All modules use `shared/config.py` which loads credentials in this order:

1. Environment variables `TOPVIEW_UID` + `TOPVIEW_API_KEY` (CI/scripting)
2. `~/.topview/credentials.json` (set by `auth.py login`)
3. Error — prompts to run `auth.py login`

## Agent Rules

- **NEVER** ask the user to run `python auth.py login` or any other command themselves.
- **NEVER** ask the user to set `TOPVIEW_UID` or `TOPVIEW_API_KEY` env vars manually.
- **NEVER** mention terminal output, browser popups, command lines, or environment variables to the user.
- **NEVER** tell the user to "go look at the browser", "check the popup", or "operate on the agent's computer". The user cannot see any of that.
- **NEVER** skip sending the login link. If you don't have the URL, re-run `auth.py login` to get it.
- **ALWAYS** run `auth.py login` yourself, extract the `URL:` from the output, and send the direct authorization link to the user.
- **ALWAYS** use the login message template from SKILL.md — keep it chat-friendly and beginner-level.
- **ALWAYS** wait for the user to confirm (e.g. "好了") before continuing the task.
