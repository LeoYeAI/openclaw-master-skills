# virtual-desktop

🖥️ Persistent authenticated browser for OpenClaw — anti-bot, vision-enabled, CAPTCHA-autonomous.

If a human can do it in Chrome, the agent can do it — 24h/24, without you.

---

## What it does

Runs a real **kasmweb/chrome** Docker sidecar alongside OpenClaw.
Principal logs in once via noVNC. Sessions saved permanently in a Docker volume.
Agent accesses any authenticated platform from that point on — no credentials needed.

## Three execution paths

| Path | Use for | Tokens |
|---|---|---|
| OpenClaw native browser | Simple navigate / click / extract | Fewest |
| browser_control.py | AUDIT logging, workflows, CAPTCHA, Vision | Medium |
| noVNC (manual) | Initial login, 2FA, session renewal | None |

Load only the path the task requires.

## Key features

- **Persistent sessions** — log in once, access forever
- **Autonomous CAPTCHA** — CapSolver resolves reCAPTCHA / hCaptcha / Turnstile automatically
- **Residential proxy** — Browserbase for sites that block VPS IPs
- **Claude Vision** — analyze any page or image natively
- **Full logging** — every action in AUDIT.md, errors in ERRORS.md, patterns in LEARNINGS.md
- **Self-improving** — agent writes learnings immediately after every session

## What gets downloaded at setup

| What | Why |
|---|---|
| `kasmweb/chrome:1.15.0` (~2GB) | Real Chrome Desktop with noVNC — your authenticated sessions live here |
| `Playwright Chromium` (~100MB) | Headless fallback inside the OpenClaw container — used if Chrome CDP is unavailable |
| `requests + playwright` (Python) | Python dependencies for browser_control.py |
| `CapSolver extension` (optional) | Only if CAPSOLVER_API_KEY is set — autonomous CAPTCHA |

## Setup

Agent runs `virtual_desktop.setup` — downloads and installs everything, notifies the principal.
Principal connects once via noVNC. Done.

## Optional keys (add to .env)

```
CAPSOLVER_API_KEY=xxx      # Autonomous CAPTCHA (~$0.001/solve)
BROWSERBASE_API_KEY=xxx    # Residential proxy + stealth (free tier available)
ANTHROPIC_API_KEY=xxx      # Claude Vision (uses existing key if already set)
```

## Files included

| File | Role |
|---|---|
| `SKILL.md` | Full instructions for the agent |
| `browser_control.py` | Python helper — logging, CAPTCHA, Vision, workflows |
| `README.md` | This file |
| `CONFIGURATION.md` | noVNC access, .env variables, reset procedures |
