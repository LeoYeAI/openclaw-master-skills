---
name: virtual-desktop
description: >
  Full Computer Use for OpenClaw via kasmweb/chrome Docker sidecar.
  Navigate any website, click, type, fill forms, extract data, upload files,
  screenshot on any platform including private authenticated accounts.
  Principal logs in once via noVNC. Sessions saved permanently in Docker volume.
  After one-time manual login via noVNC, agent can access authenticated platforms. CapSolver solves CAPTCHAs
  automatically. Browserbase profile available for residential proxy and stealth.
  Claude vision analyses screenshots and AI-generated images natively.
  Every action logged. Every discovery improves performance via .learnings/.
version: 3.0.0
author: Georges Andronescu (Wesley Armando)
license: MIT
metadata:
  openclaw:
    emoji: "🖥️"
    security_level: L3
    required_paths:
      read:
        - /workspace/TOOLS.md
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/.learnings/ERRORS.md
        - /workspace/tasks/lessons.md
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
        - "https://www.google.com (example — Chrome accesses any principal-authorized URL)"
        - "https://api.capsolver.com (CAPTCHA solving — requires CAPSOLVER_API_KEY)"
        - "wss://connect.browserbase.com (stealth — requires BROWSERBASE_API_KEY)"
        - "https://api.anthropic.com (Claude vision — requires ANTHROPIC_API_KEY)"
      uses_agent_telegram: true
      telegram_note: "Uses existing agent Telegram channel — no separate token required. Agent notifies principal when CAPTCHA or session renewal is needed."
    requires:
      bins:
        - docker
        - openclaw
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
    homepage: "https://github.com/georges91560/virtual-desktop"
    repository: "https://github.com/georges91560/virtual-desktop"
---

# Virtual Desktop — Universal Execution Layer

## What this skill does

Gives the agent a persistent authenticated browser (kasmweb/chrome) running
as a Docker sidecar. Principal logs in once via noVNC. Sessions saved permanently.
After one-time manual login via noVNC, agent can access authenticated platforms — no credentials needed after setup.

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

## Required Workspace Structure

```
/workspace/
├── screenshots/          ← visual proof of every action (auto-created)
├── logs/browser/         ← full tracebacks (auto-created)
├── AUDIT.md              ← append-only action log
├── memory/YYYY-MM-DD.md  ← daily session summary
└── .learnings/
    ├── ERRORS.md         ← errors, broken selectors, ref maps
    └── LEARNINGS.md      ← patterns, timing, navigation per platform
```

---

## Setup — Run Once

Agent executes all steps automatically:

```bash
OPENCLAW_DIR="${OPENCLAW_DIR:-$(pwd)}"
cd "$OPENCLAW_DIR"
CONTAINER="${OPENCLAW_CONTAINER:-$(docker ps --format '{{.Names}}' | grep openclaw | head -1)}"

# 1. Add kasmweb/chrome to docker-compose.yml
python3 -c "
import yaml, os
VNC_PW = os.environ.get('VNC_PW', 'CHANGE_ME_NOW')
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
grep -q "VNC_PW"              .env || echo "VNC_PW=CHANGE_ME_NOW"                  >> .env
grep -q "BROWSER_CDP_URL"     .env || echo "BROWSER_CDP_URL=http://browser:9222"   >> .env
grep -q "CAPSOLVER_API_KEY"   .env || echo "CAPSOLVER_API_KEY="                    >> .env
grep -q "BROWSERBASE_API_KEY" .env || echo "BROWSERBASE_API_KEY="                  >> .env

# 3. Update openclaw.json (hot reload — no restart needed)
# OpenClaw watches openclaw.json and applies changes automatically
python3 -c "
import json, os
f = 'data/.openclaw/openclaw.json'
with open(f) as fp: cfg = json.load(fp)
cfg.setdefault('browser', {}).update({
    'enabled': True, 'headless': False,
    'noSandbox': True, 'defaultProfile': 'chrome-sidecar'
})
profiles = cfg['browser'].setdefault('profiles', {})
profiles['chrome-sidecar'] = {'cdpUrl': 'http://browser:9222', 'color': '#4285F4'}
bb_key = os.environ.get('BROWSERBASE_API_KEY', '')
if bb_key:
    profiles['browserbase'] = {'cdpUrl': f'wss://connect.browserbase.com?apiKey={bb_key}', 'color': '#F97316'}
    print('Browserbase profile enabled')
with open(f, 'w') as fp: json.dump(cfg, fp, indent=2)
print('openclaw.json updated — hot reload applied automatically')
"

# 4. Start ONLY the new browser container (no need to restart OpenClaw)
# docker compose up -d --no-deps starts only the specified service
# OpenClaw keeps running without interruption
docker compose up -d --no-deps browser
echo "Chrome Desktop container started"
sleep 12

# 5. Install Python dependencies inside the OpenClaw container
docker exec "$CONTAINER" pip install requests playwright --break-system-packages -q
echo "✅ Python dependencies installed (requests, playwright)"

# 6. Install Playwright Chromium browser binaries
docker exec "$CONTAINER"   node /app/node_modules/playwright-core/cli.js install chromium
echo "✅ Playwright Chromium binaries installed"

# 7. Download CapSolver extension for autonomous CAPTCHA solving
docker exec "$CONTAINER" bash -c "
apt-get install -y unzip curl -qq
curl -sL https://github.com/capsolver/capsolver-browser-extension/releases/latest/download/chrome.zip -o /tmp/capsolver.zip
unzip -q /tmp/capsolver.zip -d /data/.openclaw/capsolver-extension
"
CAPSOLVER_KEY=$(grep CAPSOLVER_API_KEY .env | cut -d= -f2)
if [ -n "$CAPSOLVER_KEY" ]; then
  docker exec "$CONTAINER" bash -c "
  sed -i \"s/apiKey: \"\"/apiKey: \"$CAPSOLVER_KEY\"/\" /data/.openclaw/capsolver-extension/assets/config.js 2>/dev/null
  "
fi

# 8. Create workspace directories
docker exec "$CONTAINER" bash -c "
mkdir -p /data/.openclaw/workspace/skills/virtual-desktop
mkdir -p /workspace/screenshots /workspace/logs/browser /workspace/.learnings
touch /workspace/AUDIT.md /workspace/.learnings/ERRORS.md /workspace/.learnings/LEARNINGS.md
"

# 9. Deploy browser_control.py from skill directory
docker cp {baseDir}/browser_control.py   "$CONTAINER":/data/.openclaw/workspace/skills/virtual-desktop/browser_control.py
echo "✅ browser_control.py deployed"

# 10. Verify
docker ps | grep -E "openclaw|browser"
curl -s http://localhost:9222/json > /dev/null && echo "✅ Chrome CDP active" || echo "⏳ Chrome starting..."
docker exec "$CONTAINER"   python3 /data/.openclaw/workspace/skills/virtual-desktop/browser_control.py status

# 11. Notify principal
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")
echo ""
echo "Virtual Desktop ready — https://${VPS_IP}:6901"
echo "Log in to all your platforms then reply DONE."
```

---

## Initial Login — Once Per Platform

```
https://YOUR_VPS_IP:6901  —  login: kasm_user  /  password: your VNC_PW value
```

Open Chrome via noVNC and log in to all platforms.
Sessions saved in Docker volume `browser-profile` — survive restarts — valid forever.
Session expired → agent notifies via Telegram → principal reconnects in 2 min.

---

## Native OpenClaw Browser Commands — Quick Reference

These commands are native to OpenClaw. The agent already knows them.
This reference is here for quick lookup during missions.

```bash
# Navigation & tabs
openclaw browser open <url>
openclaw browser navigate <url>
openclaw browser go-back
openclaw browser reload
openclaw browser tab new | select 2 | close 2 | tabs
openclaw browser resize 1920 1080

# Inspection
openclaw browser snapshot                          # numeric refs
openclaw browser snapshot --interactive            # role refs e12 — best for actions
openclaw browser snapshot --efficient              # token-efficient mode
openclaw browser snapshot --selector "#main"       # scoped to element
openclaw browser snapshot --labels                 # screenshot with ref labels
openclaw browser screenshot
openclaw browser screenshot --full-page
openclaw browser screenshot --ref e12              # capture specific element
openclaw browser pdf

# Actions
openclaw browser click e12
openclaw browser click e12 --double
openclaw browser hover e12
openclaw browser type e12 "text"
openclaw browser type e12 "text" --submit
openclaw browser press Enter | Tab | Escape | "Control+a" | "Control+c" | "Control+v"
openclaw browser select e9 "option"
openclaw browser drag e10 e11
openclaw browser scrollintoview e12
openclaw browser fill --fields '[{"ref":"e1","type":"text","value":"text"}]'
openclaw browser dialog --accept | --dismiss
openclaw browser evaluate --fn '(el) => el.textContent' --ref e7
openclaw browser highlight e12

# Wait — critical for dynamic pages
openclaw browser wait "#selector"
openclaw browser wait --text "expected text"
openclaw browser wait --url "**/dashboard"
openclaw browser wait --load networkidle
openclaw browser wait --load domcontentloaded
openclaw browser wait "#el" --load networkidle --fn "window.ready===true" --timeout-ms 15000

# Files
openclaw browser upload /tmp/openclaw/uploads/file.pdf
openclaw browser download e12 file.pdf
openclaw browser waitfordownload file.pdf

# Cookies & storage
openclaw browser cookies | cookies set k v --url "https://x.com" | cookies clear
openclaw browser storage local get | set k v | clear
openclaw browser storage session clear

# Browser configuration
openclaw browser set offline on | off
openclaw browser set headers --headers-json '{"X-Custom":"val"}'
openclaw browser set geo 48.8566 2.3522 --origin "https://example.com"
openclaw browser set media dark
openclaw browser set timezone Europe/Paris
openclaw browser set locale fr-FR
openclaw browser set device "iPhone 14"

# Debug & monitoring
openclaw browser console --level error
openclaw browser errors
openclaw browser requests --filter api
openclaw browser responsebody "**/api" --max-chars 5000
openclaw browser trace start | stop
openclaw browser status | start | stop

# Stealth — if VPS is blocked
openclaw browser --browser-profile browserbase open <url>
```

---

## browser_control.py — Commands (auto-logging + CAPTCHA + vision)

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
$BC analyze     <url_or_image> [question]        ← CLAUDE VISION
$BC captcha     <url>                            ← AUTONOMOUS CAPTCHA
$BC workflow    <json_steps_file>                ← MULTI-STEP WORKFLOW
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
  { "action": "fill",       "target": "#field", "value": "text" },
  { "action": "click",      "target": "#btn" },
  { "action": "click_xy",   "x": 960, "y": 540 },
  { "action": "scroll",     "direction": "down" },
  { "action": "hover",      "target": "#menu" },
  { "action": "select",     "target": "#list", "value": "option" },
  { "action": "keyboard",   "target": "#input", "value": "Enter" },
  { "action": "extract",    "target": ".data", "value": "/workspace/tasks/out.json" },
  { "action": "screenshot" },
  { "action": "wait",       "value": "2" }
]
```

---

## CAPTCHA — Autonomous Strategy

```
1. Auto-detection on every page load
   → reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile

2. CapSolver API resolution (if CAPSOLVER_API_KEY set in .env)
   → Extracts sitekey → sends to API → receives token → injects → continues

3. Cloudflare Turnstile
   → CapSolver Chrome extension handles it in background → wait 60s → continues

4. Fallback
   → Screenshot → Telegram → principal opens noVNC → solves → agent continues

To enable: add CAPSOLVER_API_KEY=xxx to .env (~$0.001 per CAPTCHA)
```

---

## Residential Proxy — If Site Blocks the VPS

```bash
# Option 1 — Browserbase (CAPTCHA + stealth + residential proxy built-in)
# Free tier: 1 concurrent session, 1h/month — browserbase.com
# Add to .env: BROWSERBASE_API_KEY=xxx
# Use: openclaw browser --browser-profile browserbase open <url>

# Option 2 — Custom proxy in browser_control.py
# Add to .env: PROXY_URL=http://user:pass@proxy:port
# In get_browser(): ctx = browser.new_context(proxy={"server": os.environ["PROXY_URL"]}, ...)
```

---

## Claude Vision — Analyze Images and Pages

```bash
# Web page → auto screenshot + analysis
$BC analyze https://example.com "What does this page sell?"

# AI-generated image
$BC analyze https://site.com/image.png "Describe the visual elements"

# Existing screenshot
$BC analyze /workspace/screenshots/capture.png "Is there a form on this page?"

# Inside a JSON workflow
{ "action": "analyze", "value": "Identify all form fields on this page" }
```

---

## Execution Protocol

```
BEFORE EVERY BROWSER ACTION:
  1. Log to AUDIT.md: "BEFORE [action] on [url]"
  2. Detect CAPTCHA → resolve automatically if present
  3. Execute
  4. Screenshot as proof
  5. Log to AUDIT.md: "OK/FAILED [action]"
  6. Telegram report if real-world consequences

NEVER:
  → Access platforms not authorized by the principal
  → Execute payments without explicit approval
  → Fail silently — always log
  → Retry more than 3 times without alerting principal
```

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

## Security

This skill opens port 6901 (noVNC) on your VPS and stores authenticated browser sessions permanently.
Before installing, understand what this means:

```
REQUIRED before running:
  1. Set a strong VNC_PW in .env — never use the default
  2. Firewall port 6901 to your IP only:
     → Hostinger: Panel → VPS → Firewall → restrict port 6901 to your IP
     → Or use SSH tunnel instead of opening the port publicly:
        ssh -L 6901:localhost:6901 user@YOUR_VPS_IP
        Then access via http://localhost:6901

  3. The agent will have autonomous access to whatever accounts
     you log into via noVNC — only log into accounts you trust
     the agent to access

  4. CAPSOLVER_API_KEY, BROWSERBASE_API_KEY, ANTHROPIC_API_KEY
     are optional — only add them if you trust those services
     and understand their costs
```

---

## Files Written By This Skill

| File | When | Content |
|---|---|---|
| `/workspace/AUDIT.md` | Every action | Before + after log, append-only |
| `/workspace/screenshots/YYYY-MM-DD_*.png` | Every action | Visual proof |
| `/workspace/screenshots/YYYY-MM-DD_*_analysis.txt` | After analyze | Vision result |
| `/workspace/logs/browser/YYYY-MM-DD.log` | On exception | Full traceback |
| `/workspace/.learnings/ERRORS.md` | On failure | Errors + ref maps |
| `/workspace/.learnings/LEARNINGS.md` | On discovery | Patterns + timing |
| `/workspace/tasks/lessons.md` | During mission | Immediate task capture |
| `/workspace/memory/YYYY-MM-DD.md` | Daily | Session summary |

---

## Self-Improvement

After every browser session, write immediately:

```
# ERRORS.md
## [YYYY-MM-DD] [Platform] — [Title]
**Priority**: low|medium|high — **Status**: pending|resolved
**What happened**: ... **Root cause**: ... **Fix**: ... **Ref map**: {"e12":"e15"}

# LEARNINGS.md
## [YYYY-MM-DD] [Platform] — [Pattern]
**Category**: navigation|interaction|timing|auth_flow|captcha|vision
**Discovery**: ... **Usage**: ...
```
