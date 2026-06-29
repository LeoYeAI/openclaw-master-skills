---
name: clawdcursor
version: 0.6.3
description: >
  AI desktop agent — control any app on Windows/macOS from your OpenClaw agent.
  Send natural language tasks to the Clawd Cursor API and it handles everything:
  opening apps, clicking buttons, typing text, navigating browsers, filling forms.
  If you can click it, your agent can too.
homepage: https://clawdcursor.com
source: https://github.com/AmrDab/clawd-cursor
privacy: >
  Screenshots and UI data stay on the user's machine. If using Ollama (local), zero data leaves the host.
  If using a cloud provider (Anthropic, OpenAI, Kimi), screenshots/text are sent to that provider's API
  only — never to third-party servers or skill authors. The user controls which provider is used.
  The REST API binds to 127.0.0.1 only and is not network-accessible.
metadata:
  openclaw:
    # Note: bins check removed — OpenClaw's hasBinary() doesn't handle Windows
    # PATHEXT (.exe/.cmd), causing false "missing" on Windows even when node is
    # installed. Since install requires npm (which implies node), the check is
    # redundant. See: https://github.com/openclaw/openclaw/issues/TBD
    requires: {}
    install:
      - git clone https://github.com/AmrDab/clawd-cursor.git
      - cd clawd-cursor && npm install && npm run setup
      - cd clawd-cursor && clawdcursor doctor
      - cd clawd-cursor && clawdcursor start
    privacy:
      - Screenshots processed by user's own configured AI provider only
      - With Ollama, fully offline — no external API calls
      - With cloud providers, data goes only to user's chosen API endpoint
      - REST API binds to 127.0.0.1 only — not network accessible
notes:
  - In OpenClaw, this skill inherits the active agent's AI provider + API key.
  - Standalone CLI mode can still use AI_API_KEY / provider-specific env vars or Ollama.
---

# Clawd Cursor

**If a human can do it on a screen, you can too.** No API? No integration? No problem.
Every app already has a UI — Clawd Cursor gives you eyes and hands to use all of them.

No task is impossible. If it's on the screen, it's within reach.

> **IMPORTANT — READ THIS BEFORE ANYTHING ELSE**
>
> You have a desktop AI agent over GUI running on the user's machine. This means:
> 1. You **CAN** open apps, click buttons, type text, fill forms
> 2. You **CAN** see what's on screen (via Clawd Cursor's screenshot pipeline)
> 3. You **CAN** interact with applications — browser, desktop apps, settings
> 4. You **MUST** respect safety tiers — 🟢 Auto actions run freely, 🔴 Confirm actions require user approval
> 5. You **MUST** ask before accessing sensitive apps (email, banking, private messages, password managers)
> 6. You **SHOULD** prefer direct tools (file read, web_fetch, CLI) over desktop automation when available
>
> Think of Clawd Cursor as your hands and eyes on the user's computer — used with their permission.

---

## When to Use This (AGENTS: READ THIS)

You have a desktop UI agent available. Use it when the user asks you to interact with their desktop, or when no other tool can accomplish the task.

### Tool vs Skill (OpenClaw terminology)
- **Tool** = direct capability (API call, filesystem, shell, web fetch, browser command).
- **Skill** = packaged workflow/domain logic that may call one or more tools.
- **This skill (Clawd Cursor)** = GUI execution skill. Use it after OpenClaw tools/skills that can complete the same work without GUI.

### Use Clawd Cursor for (examples, not limits):
Clawd Cursor can perform **any action that is visible and interactable in the GUI** (subject to safety policy).

- **User-requested desktop tasks** — "open Gmail and send an email", "check my calendar"
- **Read a webpage** — when web_fetch or browser tools aren't available
- **Interact with desktop apps** — click buttons, fill forms, read results
- **Browser tasks** — search, navigate, fill forms (when browser tool unavailable)
- **Visual verification** — did the page load? what does the UI show?
- **Cross-app workflows** — copy from one app, paste in another
- **Settings changes** — when the user explicitly asks

### ⚠️ Sensitive App Policy
**Always ask the user before** accessing:
- Email clients (Gmail, Outlook)
- Banking or financial apps
- Private messaging (WhatsApp, Signal, Telegram)
- Password managers
- Admin panels or cloud consoles

### Don't use Clawd Cursor when:
- You can do it with a direct API call or CLI command (faster)
- The task is purely computational (math, text generation, code writing)
- You can already read/write the file directly
- The browser tool or web_fetch can handle it

## OpenClaw + Clawd Cursor Routing Contract (Avoid Overlap)

Clawd Cursor should be treated as **OpenClaw's GUI execution layer**, not a competing planner.

### Route tasks in this order:
1. **OpenClaw native tools first** (filesystem, API, shell, provider-native skills)
2. **Browser-native automation next** (Playwright/CDP direct) for browser-only reads/clicks
3. **Clawd Cursor API task (`POST /task`)** only when desktop/UI-level interaction is required

### Practical rule
- If OpenClaw already has a reliable skill/tool for the domain, use it.
- Use Clawd Cursor to bridge gaps where no API/tool exists or when the user explicitly asks for GUI interaction.

This keeps behavior predictable, lowers latency/cost, and avoids duplicated logic between the main OpenClaw agent and this skill.

### Universal task pattern
For broad "get it done" requests, split into three phases:
1. **Plan in OpenClaw**: break work into API/CLI/browser/GUI subtasks.
2. **Execute cheap paths first**: API + CLI + browser direct.
3. **Escalate only residual UI steps** to Clawd Cursor.

Think: **"OpenClaw decides, Clawd Cursor acts on GUI when needed."**

### Direct Browser Access (Fast Path)
For quick page reads without a full task, connect to Chrome via Playwright CDP:
```js
const pw = require('playwright');
const browser = await pw.chromium.connectOverCDP('http://127.0.0.1:9222');
const pages = browser.contexts()[0].pages();
const text = await pages[0].innerText('body');
```

Use this when you just need page content — faster than sending a task.

| Scenario | Use | Why |
|----------|-----|-----|
| Read page content/text | CDP Direct | Instant, free |
| Fill a web form | API task (`POST /task`) | Clawd handles multi-step planning |
| Check if a page loaded | CDP Direct | Just read the title/URL |
| Click through a complex UI flow | API task (`POST /task`) | Clawd handles planning |
| Get a list of elements on page | CDP Direct | Fast DOM query |
| Interact with a desktop app | API task (`POST /task`) | CDP is browser-only |

---

## REST API Reference

Base URL: `http://127.0.0.1:3847`

> **Note:** On Windows PowerShell, use `curl.exe` (with .exe) or `Invoke-RestMethod`. Bare `curl` is aliased to `Invoke-WebRequest` which behaves differently.

### Pre-flight Check

Before your first task, verify Clawd Cursor is running:

```bash
curl.exe -s http://127.0.0.1:3847/health
```

Expected: `{"status":"ok","version":"0.6.0"}`

If connection refused — **start it yourself** (don't ask the user):
```powershell
# Find the skill directory and start the server
Start-Process -FilePath "node" -ArgumentList "dist/index.js","start" -WorkingDirectory "<clawd-cursor-directory>" -WindowStyle Hidden
Start-Sleep 3
# Verify it's running
curl.exe -s http://127.0.0.1:3847/health
```
The skill directory is wherever SKILL.md lives (the parent of this file). Use that path as the working directory.

### Sending a Task (Async — Returns Immediately)

`POST /task` accepts the task and returns immediately. The task runs in the background. **You must poll `/status` to know when it's done.**

```bash
curl.exe -s -X POST http://127.0.0.1:3847/task -H "Content-Type: application/json" -d "{\"task\": \"YOUR_TASK_HERE\"}"
```

PowerShell:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:3847/task -Method POST -ContentType "application/json" -Body '{"task": "YOUR_TASK_HERE"}'
```

### Polling Pattern (Follow This)

```
1. POST /task → get accepted
2. Wait 2 seconds
3. GET /status
4. If status is "idle" → done
5. If status is "waiting_confirm" → ASK THE USER, then POST /confirm based on their answer
6. If still running → wait 2 more seconds, go to step 3
7. If 60+ seconds → POST /abort and retry with clearer instructions
```

### Checking Status

```bash
curl.exe -s http://127.0.0.1:3847/status
```

### Confirming Safety-Gated Actions

Some actions (sending messages, deleting) require approval. **🔴 NEVER self-approve these.** Always ask the user for confirmation before POST /confirm. These exist to protect the user — do not bypass them.
```bash
curl.exe -s -X POST http://127.0.0.1:3847/confirm -H "Content-Type: application/json" -d "{\"approved\": true}"
```

### Aborting a Task

```bash
curl.exe -s -X POST http://127.0.0.1:3847/abort
```

### Reading Logs (Debugging)

```bash
curl.exe -s http://127.0.0.1:3847/logs
```

Returns last 200 log entries. Check for `error` or `warn` entries when tasks fail.

### Response States

| State | Response | What to do |
|-------|----------|------------|
| **Accepted** | `{"accepted": true, "task": "..."}` | Start polling |
| **Running** | `{"status": "acting", "currentTask": "...", "stepsCompleted": 2}` | Keep polling |
| **Waiting confirm** | `{"status": "waiting_confirm", "currentStep": "..."}` | POST /confirm |
| **Done** | `{"status": "idle"}` | Task complete |
| **Busy** | `{"error": "Agent is busy", "state": {...}}` | Wait or POST /abort first |

---

## CDP Direct Reference

Chrome must be running with `--remote-debugging-port=9222`.

### Quick check:
```bash
curl.exe -s http://127.0.0.1:9222/json/version
```

If this returns JSON, Chrome is ready.

### Connecting via Playwright:

```javascript
const { chromium } = require('playwright');
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const context = browser.contexts()[0];
const page = context.pages()[0];

// Read page content
const title = await page.title();
const url = page.url();
const text = await page.textContent('body');

// Click by role
await page.getByRole('button', { name: 'Submit' }).click();

// Fill a field
await page.getByLabel('Email').fill('user@example.com');

// Read specific elements
const buttons = await page.$$eval('button', els => els.map(e => e.textContent));
```

---

## Task Writing Guidelines

1. **Be specific** — include app names, URLs, exact text to type, button names
2. **One task at a time** — wait for completion before sending the next
3. **Describe the goal, not the clicks** — say "Send an email to john@example.com about the meeting" not "click compose, click to field..."
4. **Check status** if a task seems to hang
5. **Don't include credentials in task text** — tasks are logged

## Task Examples

| Goal | Task to send |
|------|-------------|
| **Simple navigation** | `Open Chrome and go to github.com` |
| **Read screen content** | `What text is currently displayed in Notepad?` |
| **Cross-app workflow** | `Copy the email address from the Chrome tab and paste it into the To field in Outlook` |
| **Form filling** | `In the open Chrome tab, fill the contact form: name "John Doe", email "john@example.com"` |
| **App interaction** | `Open Spotify and play the Discover Weekly playlist` |
| **Settings change** | `Open Windows Settings and turn on Dark Mode` |
| **Data extraction** | `Read the stock price shown in the Bloomberg tab in Chrome` |
| **Complex browser** | `Open YouTube, search for "Adele Hello", and play the first video result` |
| **Verification** | `Check if the deployment succeeded — look at the Vercel dashboard in Chrome` |
| **Send email** | `Open Gmail, compose email to john@example.com, subject: Meeting Tomorrow, body: Confirming 2pm. Best regards.` |
| **Take screenshot** | `Take a screenshot` |

## Error Recovery

| Problem | Solution |
|---------|----------|
| Connection refused on :3847 | Start Clawd Cursor: `cd clawd-cursor && npm start` |
| Connection refused on :9222 | Start Chrome with CDP: `Start-Process chrome -ArgumentList "--remote-debugging-port=9222"` |
| Agent returns "busy" | Poll `/status` — wait for idle, or POST `/abort` |
| Task fails with no details | Check `/logs` for error entries |
| Task completes but wrong result | Rephrase with more specifics: exact app name, button text, field labels |
| Same task fails repeatedly | Break into smaller tasks (one action per task) |
| Safety confirmation pending | POST `/confirm` with `{"approved": true}` or `{"approved": false}` |
| Task hangs > 60 seconds | POST `/abort`, then retry with simpler phrasing |

---

## How It Works — 5-Layer Pipeline

| Layer | What | Speed | Cost |
|-------|------|-------|------|
| **0: Browser Layer** | URL detection → direct navigation | Instant | Free |
| **1: Action Router + Shortcuts** | Regex + UI Automation + keyboard shortcuts | Instant | Free |
| **1.5: Smart Interaction** | 1 LLM plan → CDP/UIDriver executes | ~2-5s | 1 LLM call |
| **2: Accessibility Reasoner** | UI tree → text LLM decides | ~1s | Cheap |
| **3: Computer Use** | Screenshot → vision LLM | ~5-8s | Expensive |

Layer 1 includes keyboard shortcuts — common actions execute as direct keystrokes (0 LLM calls).

80%+ of tasks handled by Layer 0-1 (free, instant). Vision model is last resort only.

## Safety Tiers

| Tier | Actions | Behavior |
|------|---------|----------|
| 🟢 Auto | Navigation, reading, opening apps | Runs immediately |
| 🟡 Preview | Typing, form filling | Logs before executing |
| 🔴 Confirm | Sending messages, deleting | Pauses — **ask the user** before POST `/confirm`. Never self-approve. |

## Security & Privacy

### Network Isolation
- API binds to `127.0.0.1` only — **not network accessible**. Verify: `netstat -an | findstr 3847` should show `127.0.0.1:3847`
- Screenshots stay in memory, never saved to disk (unless `--debug`)
- No telemetry, no analytics, no phone-home calls

### Data Flow
- **With Ollama (local)**: 100% offline — zero external network calls. No data leaves the machine.
- **With cloud providers**: screenshots/text are sent to the user's chosen provider API **only**. No data goes to skill authors, ClawHub, or third parties.
- **OpenClaw users**: credentials auto-discovered from local config files — no keys stored in skill directory.
- The user controls data flow by choosing their provider. Ollama = fully private.

### Agent Autonomy Controls
- **🟢 Auto** actions (navigation, reading, opening apps) run without prompting
- **🟡 Preview** actions (typing, form filling) are logged before executing
- **🔴 Confirm** actions (sending messages, deleting, purchases) **always pause for user approval**
- Agents **must ask the user** before accessing sensitive apps (email, banking, messaging, passwords)
- Agents **must never self-approve** 🔴 Confirm actions

---

## Setup (User Reference)

Setup is handled by the user. If Clawd Cursor isn't running, **start it yourself** using the exec tool:
```powershell
Start-Process -FilePath "node" -ArgumentList "dist/index.js","start" -WorkingDirectory "<skill-directory>" -WindowStyle Hidden
```
Only ask the user if you cannot start it (e.g., node not installed, build missing).

```bash
git clone https://github.com/AmrDab/clawd-cursor.git
cd clawd-cursor
npm install && npm run build
npx clawd-cursor doctor    # auto-detects and configures everything
npm start                  # starts on port 3847
```

**macOS:** Grant Accessibility permission to terminal: System Settings → Privacy & Security → Accessibility

| Provider | Setup | Cost |
|----------|-------|------|
| **Ollama (free)** | `ollama pull <model>` | $0 (fully offline) |
| **Any cloud provider** | Set `AI_API_KEY=your-key` | Varies by provider |
| **OpenClaw users** | Automatic — no setup needed | Uses configured provider |

---

## Performance Optimization

Proven optimizations applied to reduce task execution latency and LLM API costs. Reference files in `perf/references/patches/`.

### Applied Optimizations

| # | Name | Impact |
|---|------|--------|
| 1 | Screenshot hash cache | 90% fewer LLM calls on static screens |
| 2 | Parallel screenshot+a11y | 30-40% per-step latency cut |
| 3 | A11y context cache (2s TTL) | Eliminates redundant PS spawns |
| 4 | Screenshot compression | 52% smaller payload (58KB vs 120KB) |
| 5 | Async debug writes | 94% less event loop blocking |
| 6 | Streaming LLM responses | 1-3s faster per LLM call |
| 7 | Trimmed system prompts | ~60% fewer prompt tokens |
| 8 | A11y tree filtering | Interactive elements only, 3000 char cap |
| 9 | Combined PS script | 1 spawn instead of 3 |
| 10 | Taskbar cache (30s TTL) | Skip expensive taskbar query |
| 11 | Delay reduction | 50-150ms vs 200-1500ms |

### Benchmarks (2560x1440)

| Metric | v0.3 (VNC) | v0.4 (Native) | v0.4.1+ (Optimized) |
|--------|------------|---------------|----------------------|
| Screenshot capture | ~850ms | ~50ms | ~57ms |
| Screenshot size | ~200KB | ~120KB | ~58KB |
| A11y context (uncached) | N/A | ~600ms | ~462ms |
| A11y context (cached) | N/A | 0ms | 0ms (2s TTL) |
| Delays (per step) | N/A | 200-1500ms | 50-600ms |
| System prompt tokens | N/A | ~800 | ~300 |

### Perf Tools

- `perf/apply-optimizations.ps1` — apply all patches
- `perf/perf-test.ts` — benchmark harness (`npx ts-node perf/perf-test.ts`)
