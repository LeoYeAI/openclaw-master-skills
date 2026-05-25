---
name: virtual-desktop-pro
version: 4.0.0
homepage: https://github.com/openclaw-skills/virtual-desktop
description: >
  Persistent authenticated browser for OpenClaw via kasmweb/chrome Docker sidecar.
  Principal logs in once via noVNC — sessions saved permanently in Docker volume.
  Agent navigates any website, clicks, fills forms, extracts data, uploads files,
  takes screenshots, solves CAPTCHAs autonomously, and analyses pages with Claude Vision.
  Use when the task requires a real authenticated browser, not a static fetch.
metadata:
  openclaw:
    emoji: "🖥️"
    security_level: L3
    always: false
    required_paths:
      read:
        - /workspace/TOOLS.md
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/.learnings/ERRORS.md
      write:
        - /workspace/AUDIT.md
        - /workspace/screenshots/
        - /workspace/logs/browser/
        - /workspace/.learnings/ERRORS.md
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/tasks/lessons.md
        - /workspace/memory/YYYY-MM-DD.md
    network_behavior:
      makes_requests: true
      request_targets:
        - "http://browser:9222 (Chrome CDP — internal Docker network only)"
        - "any URL the principal authorizes (Chrome accesses it via the sidecar)"
        - "https://api.capsolver.com (CAPTCHA solving — requires CAPSOLVER_API_KEY)"
        - "wss://connect.browserbase.com (stealth proxy — requires BROWSERBASE_API_KEY)"
        - "https://api.anthropic.com (Claude Vision — requires ANTHROPIC_API_KEY)"
        - "https://registry.npmjs.org (Playwright install only)"
      uses_agent_telegram: true
      telegram_note: >
        Uses existing agent Telegram channel. Agent notifies principal
        when CAPTCHA requires manual resolution or session has expired.
    requires:
      bins:
        - docker
        - python3
      env:
        - VNC_PW
        - BROWSER_CDP_URL
      env_optional:
        - CAPSOLVER_API_KEY
        - BROWSERBASE_API_KEY
        - ANTHROPIC_API_KEY
        - VPS_IP
        - PROXY_URL
        - TELEGRAM_BOT_TOKEN
---

# Virtual Desktop — Authenticated Browser Layer

## What this skill does

Gives the agent a persistent authenticated browser (kasmweb/chrome) running
as a Docker sidecar. Principal logs in once via noVNC. Sessions saved permanently.

| Capability | What it means |
|---|---|
| **ANALYZE** | Read any page, extract structured data, monitor changes over time |
| **PLAN** | Map the UI, identify selectors, prepare multi-step action sequences |
| **EXECUTE** | Click, type, fill forms, submit, upload, download, navigate any flow |
| **SELF-CORRECT** | Screenshot error state, identify root cause, retry with alternate approach |
| **IMPROVE** | Write UI patterns and selector maps to `.learnings/` after every session |

Use cases: Google Workspace · social platforms · admin dashboards · e-commerce ·
forms · market research · data extraction · any platform with or without an API

---

## Workspace Structure

```
/workspace/
├── screenshots/          ← visual proof of every action (auto-created)
├── logs/browser/         ← full tracebacks (auto-created)
├── tasks/lessons.md      ← immediate task capture during mission
├── AUDIT.md              ← append-only action log
├── memory/YYYY-MM-DD.md  ← daily session summary
└── .learnings/
    ├── ERRORS.md         ← errors, broken selectors, ref maps
    └── LEARNINGS.md      ← patterns, timing, navigation per platform
```


## When to Use

Use this skill when the task requires a **real authenticated browser**:

- Pages requiring login (Google, social networks, dashboards, admin panels)
- JS-rendered pages where static fetch returns nothing useful
- Multi-step flows: forms, checkouts, confirmations, file uploads
- Platforms without an API
- Screenshots or visual evidence of a page state
- CAPTCHA-protected pages

**Prefer a lighter path first** — if a simple HTTP request or existing OpenClaw
tool can answer the question, use that instead. This skill uses more tokens and
resources than plain fetch.

---

## Architecture

This skill runs a persistent **kasmweb/chrome** Docker sidecar alongside OpenClaw.
Principal logs in once via noVNC (port 6901). Sessions saved permanently in a Docker volume.

Three execution paths — load only what the task needs:

| Path | When to use | File |
|---|---|---|
| **OpenClaw native browser** | Simple navigate/click/extract — fastest, fewest tokens | Built-in |
| **browser_control.py** | AUDIT logging, workflows, CAPTCHA, Vision | `browser_control.py` |
| **noVNC (manual)** | Initial login, 2FA, session renewal | Port 6901 |

**Load only the smallest path needed.** Simple navigation → OpenClaw native.
Complex multi-step with logging → browser_control.py.

---

## Setup — Run Once

```bash
OPENCLAW_DIR="${OPENCLAW_DIR:-$(pwd)}"
cd "$OPENCLAW_DIR"
CONTAINER="${OPENCLAW_CONTAINER:-$(docker ps --format '{{.Names}}' | grep openclaw | head -1)}"

# 1. Add kasmweb/chrome to docker-compose.yml
python3 -c "
import yaml, os
VNC_PW = os.environ.get('VNC_PW') or __import__('secrets').token_urlsafe(18)
with open('docker-compose.yml') as f:
    data = yaml.safe_load(f)
data.setdefault('services', {})['browser'] = {
    'image': 'kasmweb/chrome:1.15.0',
    'container_name': 'browser',
    'restart': 'unless-stopped',
    'shm_size': '1gb',
    'ports': ['6901:6901', '9222:9222'],
    'environment': [
        'VNC_PW=' + VNC_PW,
        'RESOLUTION=1920x1080',
        'CHROME_ARGS=--remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 --no-sandbox --disable-blink-features=AutomationControlled --disable-infobars'
    ],
    'volumes': ['browser-profile:/home/kasm-user/chrome-profile'],
    'networks': list(data.get('networks', {'default': None}).keys())
}
data.setdefault('volumes', {})['browser-profile'] = None
with open('docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
print('docker-compose.yml updated')
"

# 2. Update .env
# VNC_PW — generate a strong random password if not already set
if ! grep -q "VNC_PW" .env 2>/dev/null; then
  VNC_GENERATED=$(python3 -c "import secrets,string;     print(''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(24)))")
  echo "VNC_PW=${VNC_GENERATED}" >> .env
  echo "✅ VNC_PW generated — save this: ${VNC_GENERATED}"
fi
grep -q "BROWSER_CDP_URL"     .env || echo "BROWSER_CDP_URL=http://browser:9222" >> .env
grep -q "CAPSOLVER_API_KEY"   .env || echo "CAPSOLVER_API_KEY="                  >> .env
grep -q "BROWSERBASE_API_KEY" .env || echo "BROWSERBASE_API_KEY="                >> .env

# 3. Update openclaw.json — hot reload, no restart needed
python3 -c "
import json, os
f = 'data/.openclaw/openclaw.json'
with open(f) as fp: cfg = json.load(fp)
cfg.setdefault('browser', {}).update({'enabled': True, 'headless': False,
    'noSandbox': True, 'defaultProfile': 'chrome-sidecar'})
profiles = cfg['browser'].setdefault('profiles', {})
profiles['chrome-sidecar'] = {'cdpUrl': 'http://browser:9222', 'color': '#4285F4'}
bb_key = os.environ.get('BROWSERBASE_API_KEY', '')
if bb_key:
    profiles['browserbase'] = {'cdpUrl': f'wss://connect.browserbase.com?apiKey={bb_key}', 'color': '#F97316'}
with open(f, 'w') as fp: json.dump(cfg, fp, indent=2)
print('openclaw.json updated — hot reload active')
"

# 4. Start browser container only — OpenClaw keeps running
docker compose up -d --no-deps browser
sleep 12

# 5. Install Python dependencies
docker exec "$CONTAINER" pip install requests playwright --break-system-packages -q
docker exec "$CONTAINER" node /app/node_modules/playwright-core/cli.js install chromium
echo "✅ Python dependencies installed"

# 6. Download CapSolver extension (optional — only if key present)
CAPSOLVER_KEY=$(grep CAPSOLVER_API_KEY .env | cut -d= -f2)
if [ -n "$CAPSOLVER_KEY" ]; then
  docker exec "$CONTAINER" bash -c "
  apt-get install -y unzip curl -qq
  curl -sL https://github.com/capsolver/capsolver-browser-extension/releases/latest/download/chrome.zip \
    -o /tmp/capsolver.zip
  unzip -q /tmp/capsolver.zip -d /data/.openclaw/capsolver-extension
  sed -i \"s/apiKey: \\\"\\\"/apiKey: \\\"$CAPSOLVER_KEY\\\"/\" \
    /data/.openclaw/capsolver-extension/assets/config.js 2>/dev/null
  "
  echo "✅ CapSolver extension configured"
fi

# 7. Create workspace directories and deploy browser_control.py
docker exec "$CONTAINER" bash -c "
mkdir -p /data/.openclaw/workspace/skills/virtual-desktop
mkdir -p /workspace/screenshots /workspace/logs/browser /workspace/.learnings /workspace/memory
touch /workspace/AUDIT.md /workspace/.learnings/ERRORS.md /workspace/.learnings/LEARNINGS.md
"
docker cp {baseDir}/browser_control.py \
  "$CONTAINER":/data/.openclaw/workspace/skills/virtual-desktop/browser_control.py
echo "✅ browser_control.py deployed"

# 8. Verify
docker ps | grep -E "openclaw|browser"
curl -s http://localhost:9222/json > /dev/null && echo "✅ Chrome CDP active" || echo "⏳ Chrome starting"
docker exec "$CONTAINER" \
  python3 /data/.openclaw/workspace/skills/virtual-desktop/browser_control.py status

# 9. Notify principal
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")
echo "Virtual Desktop ready — https://${VPS_IP}:6901"
echo "Log in to your platforms via noVNC then reply DONE."
```

---

## Initial Login — Once Per Platform

```
https://YOUR_VPS_IP:6901   login: kasm_user   password: your VNC_PW
```

Open Chrome via noVNC and log in to every platform you want the agent to access.
Sessions saved in Docker volume `browser-profile` — survive restarts — valid indefinitely.

**Step by step — do this once after setup:**

```
1. Open https://YOUR_VPS_IP:6901 in your browser
2. Enter password: your VNC_PW value from .env
3. Chrome Desktop opens inside the browser

4. Log in to Google (accounts.google.com)
   → Email + password + 2FA if required
   → "Trust this device" → YES
   → This unlocks: Gmail, Drive, Calendar, Docs,
     Sheets, Google AI Studio, YouTube, all Google services

5. Log in to every other platform you want Wesley to access:
   → Twitter/X        → twitter.com
   → LinkedIn         → linkedin.com
   → Reddit           → reddit.com
   → Hostinger panel  → hpanel.hostinger.com
   → Any other site   → log in normally

6. After each login: Chrome saves the session automatically
   in the Docker volume browser-profile

7. Reply DONE to Wesley on Telegram
   → Wesley confirms sessions are active
   → He will never ask for your credentials again
```

**What happens after:**
```
Wesley opens any platform → already logged in ✅
No credentials needed → ever again
Session expires (rare) → Wesley notifies Telegram
  → You open noVNC → log in again → reply DONE
  → Takes 2 minutes
```

**Important — 2FA:**
```
Google 2FA → confirm once via noVNC
              Chrome remembers the device
              No 2FA required again on this browser

Other platforms → same principle
                  confirm once → trusted device → done
```

---

## Quick Reference

| Reference | Content |
|---|---|
| OpenClaw native browser commands | See below — `openclaw browser` |
| browser_control.py commands | See below — `$BC` |
| CAPTCHA strategy | See `CAPTCHA` section |
| Residential proxy | See `Proxy` section |
| Claude Vision | See `Vision` section |
| Selectors, timing, auth flows | `LEARNINGS.md` (auto-built by agent) |
| Broken selectors, error recovery | `ERRORS.md` (auto-built by agent) |

---

## OpenClaw Native Browser — Fastest Path

```bash
# Navigation
openclaw browser open <url>
openclaw browser snapshot [--interactive]
openclaw browser back | forward | reload | close

# Interaction
openclaw browser click <ref>
openclaw browser type <ref> "text"
openclaw browser select <ref> "value"
openclaw browser hover <ref>
openclaw browser scroll [--direction down|up|right|left]

# Files
openclaw browser upload /tmp/file.pdf
openclaw browser download <ref> file.pdf

# Cookies & storage
openclaw browser cookies | cookies set k v --url "https://example.com" | cookies clear
openclaw browser storage local get | set k v | clear

# Configuration
openclaw browser set geo 48.8566 2.3522 --origin "https://example.com"
openclaw browser set timezone Europe/Paris
openclaw browser set locale fr-FR
openclaw browser set device "iPhone 14"
openclaw browser set media dark
openclaw browser set headers --headers-json '{"X-Custom":"val"}'

# Debug
openclaw browser console --level error
openclaw browser requests --filter api
openclaw browser trace start | stop
openclaw browser status

# Stealth (if site blocks VPS)
openclaw browser --browser-profile browserbase open <url>
```

---

## browser_control.py — With AUDIT Logging + CAPTCHA + Vision

```bash
BC="python3 /data/.openclaw/workspace/skills/virtual-desktop/browser_control.py"

$BC screenshot  <url> [label]
$BC navigate    <url> [selector]
$BC click       <url> <selector>
$BC click_xy    <url> <x> <y>
$BC fill        <url> <selector> <value>
$BC select      <url> <selector> <value>
$BC hover       <url> <selector>
$BC scroll      <url> <direction> [pixels]
$BC keyboard    <url> <selector> <key>
$BC extract     <url> <selector> [output_file]
$BC wait_for    <url> <selector> [timeout_ms]
$BC upload      <url> <file_selector> <file_path>
$BC analyze     <url_or_image> [question]     ← Claude Vision
$BC captcha     <url>                         ← Autonomous CAPTCHA
$BC workflow    <json_steps_file>             ← Multi-step workflow
$BC status
```

---

## Workflow JSON Format

```json
[
  { "action": "goto",       "target": "https://TARGET_URL" },
  { "action": "captcha" },
  { "action": "analyze",    "value": "Identify the key elements on this page" },
  { "action": "wait_for",   "target": ".loaded", "timeout_ms": 5000 },
  { "action": "fill",       "target": "#field",  "value": "text" },
  { "action": "click",      "target": "#btn" },
  { "action": "click_xy",   "x": 960, "y": 540 },
  { "action": "scroll",     "direction": "down" },
  { "action": "hover",      "target": "#menu" },
  { "action": "select",     "target": "#list",   "value": "option" },
  { "action": "keyboard",   "target": "#input",  "value": "Enter" },
  { "action": "extract",    "target": ".data",   "value": "/workspace/tasks/out.json" },
  { "action": "screenshot" },
  { "action": "wait",       "value": "2" }
]
```

---

## CAPTCHA — Autonomous Strategy

```
1. Auto-detection on every page load
   → reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile

2. CapSolver API (if CAPSOLVER_API_KEY set)
   → Extracts sitekey → API → token → injects → continues
   → ~$0.001 per CAPTCHA

3. Cloudflare Turnstile
   → CapSolver Chrome extension handles in background → waits 60s

4. Fallback — if CapSolver fails or key not set
   → Screenshot → Telegram → principal opens noVNC → solves → agent continues
```

---

## Proxy — If Site Blocks the VPS

```bash
# Browserbase — CAPTCHA + stealth + residential proxy built-in
# Free tier: 1 concurrent session, 1h/month — browserbase.com
# Add BROWSERBASE_API_KEY to .env
openclaw browser --browser-profile browserbase open <url>

# Custom proxy
# Add PROXY_URL=http://user:pass@proxy:port to .env
# browser_control.py reads it automatically via get_browser()
```

---

## Claude Vision — Analyse Images and Pages

```bash
# Web page → auto screenshot + analysis
$BC analyze https://example.com "What does this page sell?"

# AI-generated image
$BC analyze https://site.com/image.png "Describe the visual elements"

# Existing screenshot
$BC analyze /workspace/screenshots/capture.png "Is there a form here?"

# Inside a workflow
{ "action": "analyze", "value": "Identify all form fields" }
```

---

## Execution Protocol

```
BEFORE EVERY ACTION:
  1. Log to AUDIT.md: "BEFORE [action] on [url]"
  2. Detect CAPTCHA → resolve automatically if present
  3. Execute action
  4. Screenshot as proof
  5. Log to AUDIT.md: "OK/FAILED [action]"
  6. Telegram report if real-world consequences

NEVER:
  → Access platforms not authorized by the principal
  → Execute payments or destructive actions without explicit approval
  → Fail silently — always log
  → Retry more than 3 times without alerting the principal
```

---

## Browser Traps

Avoid these common mistakes:

- **Guessing selectors from source** → use `snapshot --interactive` or `codegen` to discover stable refs
- **Using force: true before understanding why** → investigate the overlay/disabled state first
- **Driving a full browser when HTTP would work** → more cost, more flake, less signal
- **Sharing one session across parallel tasks that mutate state** → failures become order-dependent
- **Waiting on networkidle for chatty SPAs** → analytics, polling, or sockets keep the page "busy" even when the UI is ready
- **Retrying the same selector 10 times** → log to ERRORS.md and alert the principal instead
- **Accessing high-stakes flows (payments, production data) without explicit confirmation** → require approval first

---

## Error Recovery

```
CAPTCHA          → CapSolver auto → fallback noVNC
CLOUDFLARE       → switch to --browser-profile browserbase
SESSION EXPIRED  → Telegram → principal opens noVNC → reconnects
ELEMENT MISSING  → use analyze to understand the new layout
                 → log to .learnings/ERRORS.md with ref map
TIMEOUT          → check /workspace/logs/browser/YYYY-MM-DD.log
```

---

## Files Written

| File | When | Content |
|---|---|---|
| `/workspace/AUDIT.md` | Every action | Before + after log, append-only |
| `/workspace/screenshots/YYYY-MM-DD_*.png` | Every action | Visual proof |
| `/workspace/screenshots/*_analysis.txt` | After analyze | Vision result |
| `/workspace/logs/browser/YYYY-MM-DD.log` | On exception | Full traceback |
| `/workspace/.learnings/ERRORS.md` | On failure | Errors + broken selectors |
| `/workspace/.learnings/LEARNINGS.md` | On discovery | Patterns + timing per platform |
| `/workspace/tasks/lessons.md` | During mission | Immediate task capture |
| `/workspace/memory/YYYY-MM-DD.md` | Daily | Session summary |

**This skill does NOT:**
- Create files outside the paths listed above
- Persist sessions or credentials beyond the Docker volume
- Make undeclared network requests beyond the target sites and optional services above
- Access platforms not explicitly authorized by the principal

---

## Self-Improvement

Write immediately after every session — do not batch:

```
# ERRORS.md — on failure
## [YYYY-MM-DD] [Platform] — [Title]
**Priority**: low|medium|high   **Status**: pending|resolved
**What happened**: ...   **Root cause**: ...   **Fix**: ...   **Ref map**: {"old_ref":"new_ref"}

# LEARNINGS.md — on discovery
## [YYYY-MM-DD] [Platform] — [Pattern]
**Category**: navigation|interaction|timing|auth_flow|captcha|vision
**Discovery**: ...   **Usage**: ...
```

---

## Security

This skill opens port 6901 (noVNC) and stores authenticated browser sessions permanently.

```
REQUIRED before running:
  1. Set a strong VNC_PW in .env — never use the default
  2. Firewall port 6901 to your IP only:
     Hostinger → Panel → VPS → Firewall → restrict 6901 to your IP
     Or use SSH tunnel: ssh -L 6901:localhost:6901 user@YOUR_VPS_IP
  3. Only log in to accounts you trust the agent to access
  4. Optional keys (CapSolver, Browserbase, Anthropic) send data to
     those services — only add them if you trust and accept their costs
```

---

## External Endpoints

| Endpoint | Data sent | Purpose |
|---|---|---|
| Any URL the principal authorizes | Browser requests, cookies, form data | Automation |
| `http://browser:9222` | CDP protocol — internal only | Browser control |
| `https://api.capsolver.com` | CAPTCHA sitekey + page URL | CAPTCHA solving (optional) |
| `wss://connect.browserbase.com` | Browser session | Stealth proxy (optional) |
| `https://api.anthropic.com` | Screenshot base64 | Claude Vision (optional) |
| `https://registry.npmjs.org` | Package metadata | Playwright install only |

No other data is sent externally.
