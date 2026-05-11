---
name: codex-cli-task
description: "Launch OpenAI Codex CLI async in background with automatic delivery to Telegram/WhatsApp. Use for coding, refactoring, codebase research, file generation, and complex multi-step automations. NOT for quick one-off questions or real-time interactive tasks. Includes strict thread-safe routing + E2E operator validation workflow."
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires":
          {
            "bins": ["codex", "python3"],
            "pythonModules": ["requests"],
            "config": ["gateway.auth.token", "gateway.tools.allow", "tools.sessions.visibility"],
          },
        "config": { "stateDirs": ["~/.openclaw"] },
      },
  }
---

# Codex Code Task (Async)

Run OpenAI Codex CLI in background — zero OpenClaw tokens while it works. Results delivered to WhatsApp or Telegram automatically.

## Important: Codex = General AI Agent

Codex is NOT just a coding tool. In `codex exec` mode it is a general-purpose AI agent with file access, shell execution, optional web search, and deep reasoning.

Use it for:

- **Research** — web search, synthesis, competitive analysis, user experience reports
- **Coding** — create tools, scripts, APIs, refactor codebases
- **Analysis** — read and analyze files, data, logs, source code
- **Content** — write docs, reports, summaries
- **Automations** — complex multi-step workflows with filesystem access

Give it prompts the same way you'd talk to a smart human — natural language, focused on WHAT you need, not HOW to do it.

**NOT for:**

- Quick questions
- Tasks needing real-time back-and-forth

## Quick Start

## What "run tests" means for this skill (critical)

When user asks things like:

- "прогони все тесты"
- "run tests"
- "проверь что всё работает"

it means **run the full E2E operator validation flow** for `run-task.py` routing + notifications.

It does **NOT** mean plain `pytest`/`unittest` discovery by default.

Required behavior:

1. Run routing validation first (`--validate-only`).
2. Launch smoke/E2E scenario via `nohup` and file-based prompt.
3. Wait for completion through normal async flow, not same-turn blocking.
4. Report PASS/FAIL against E2E criteria: routing, heartbeat, mid-task update, completion delivery.

Use the canonical protocol: **[references/testing-protocol.md](references/testing-protocol.md)** and the section below **Full E2E Test (reference)**.

## Async Boundary Rule (mandatory)

`run-task.py` is asynchronous orchestration.

After a successful `nohup` launch, the correct behavior is:

1. Send a short launch acknowledgment (PID/log/session)
2. **Stop this turn immediately**
3. Continue only when wake/completion event arrives in the same session

Do **not** keep waiting in the same turn for Codex completion.
Do **not** poll and then summarize in the same turn unless user explicitly asked for active live monitoring.

Anti-pattern:

- ❌ Launch `run-task.py` and keep responding as if completion should appear in this turn

Correct pattern:

- ✅ Launch `run-task.py` → acknowledge launch → stop → wait for wake

## Launch Confirmation Gate (mandatory)

Never claim "launched" until you have **positive launch proof**.

Required proof checklist:

1. `nohup` command returned a PID
2. process is alive (`ps -p <PID>`)
3. run log contains `🔧 Starting OpenAI Codex...` or equivalent startup marker
4. routing was validated (`--validate-only`) for Telegram thread runs

If launch fails with `❌ Invalid routing`:

- resolve via `sessions_list`
- rerun with explicit routing/session arguments if needed
- re-check proof checklist
- only then send launch acknowledgment

## Pre-launch planning note (mandatory)

Before launching Codex, post a short plan in chat:

- how you plan to solve the task
- what result you expect from this run
- any clarifying assumptions
- whether you expect one iteration or staged follow-up

If staged: explicitly say this run is "phase 1" and what signal decides phase 2.

## Telegram Thread Safety (must-follow)

For Telegram thread runs, `run-task.py` is designed to either route correctly or fail immediately.

### Mandatory step before launch

Resolve the **current runtime session key** first, then launch with it.

- Get current key via `sessions_list` or runtime context
- If key is `agent:main:main:thread:<THREAD_ID>` → use it directly in `--session`
- Never derive `--session` from `chat_id` / sender heuristics

### Rules

- Use only `--session "agent:main:main:thread:<THREAD_ID>"` for thread tasks
- Never use `agent:main:telegram:user:<id>` for thread tasks
- If routing metadata is inconsistent, script exits with `❌ Invalid routing`
- Default mode is `--telegram-routing-mode auto`
- Force strict thread-only behavior with `--telegram-routing-mode thread-only`
- Force non-thread behavior with `--telegram-routing-mode allow-non-thread` or `--allow-main-telegram`

This is intentional: **abort fast > silent misroute**

⚠️ **ALWAYS launch via nohup** — exec timeout will kill the process otherwise.

⚠️ **NEVER put the task text directly in the shell command** — save the prompt to a file first, then use `$(cat file)`.

### WhatsApp

```bash
# Step 1: Save prompt to a temp file
write /tmp/codex-prompt.txt with your task text

# Step 2: Launch with $(cat ...)
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:whatsapp:group:<JID>" \
  --timeout 900 \
  > /tmp/codex-run.log 2>&1 &
```

### Telegram (thread-safe default)

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 900 \
  > /tmp/codex-run.log 2>&1 &
```

> Do **NOT** use `agent:main:telegram:user:<id>` for thread tests/runs.

### Telegram Threaded Mode (1:1 DM with threads)

When OpenClaw is used in Telegram threaded mode, each thread has its own session key like `agent:main:main:thread:369520`.

**Fail-safe routing (NEW):** `run-task.py` now enforces strict thread routing.
- If `--session` contains `:thread:<id>`, the script **refuses to start** unless Telegram target + thread session UUID are resolved.
- It auto-resolves missing values from `sessions_list` when possible.
- If the session is inactive and not returned by API, it falls back to local session files: `~/.openclaw/agents/main/sessions/*-topic-<thread_id>.jsonl`.
- If provided `--notify-session-id` mismatches the session key, it exits with error.
- Result: misrouted launches/heartbeats to main chat are blocked before Codex starts.

Use `--notify-session-id` to wake the exact thread session:

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:369520" \
  --timeout 900 \
  > /tmp/codex-run.log 2>&1 &
```

All 5 notification types route to the DM thread when `--session` key contains `:thread:<id>` ✅

- `--notify-session-id` — optional override. Usually auto-resolved from session metadata/files.
- `--notify-thread-id` — optional override. Usually auto-extracted from `--session`.
- `--reply-to-message-id` — optional debug field; avoid for DM thread routing.
- `--validate-only` — resolve routing and exit (no Codex run). Use this to verify thread launch args safely.
- `--notify-channel` — optional channel hint (`telegram`/`whatsapp`); target is always auto-resolved from session metadata.
- `--timeout` — max runtime in seconds (default: 7200 = 2 hours)
- `--completion-mode` — optional legacy hint (`single` default, `iterate` if explicitly needed)
- `--max-iterations` — optional budget hint when using iterate mode
- `--trace-live` — emit live technical trace markers into the same chat/thread (debug mode)
- Always redirect stdout/stderr to a log file

### Why file-based prompts?

Research/complex prompts contain single quotes, double quotes, markdown, backticks — any of these break shell argument parsing. Saving to a file and reading with `$(cat ...)` avoids all quoting issues.

## Channel Detection

The `detect_channel()` function determines where to send notifications:

1. **Deterministic auto-resolve** — target is resolved from session metadata/session key (no manual target flag)
2. **WhatsApp auto-detect** — if the session key contains `@g.us` (WhatsApp group JID), WhatsApp is used
3. **Fail fast on unresolved Telegram target** — script exits with `❌ Invalid routing` instead of silent misroute

```python
def detect_channel(session_key):
    if NOTIFY_CHANNEL_OVERRIDE and NOTIFY_TARGET_OVERRIDE:
        return NOTIFY_CHANNEL_OVERRIDE, NOTIFY_TARGET_OVERRIDE
    jid = extract_group_jid(session_key)
    if jid:
        return "whatsapp", jid
    return None, None
```

## How It Works

```
┌─────────────┐     nohup      ┌──────────────┐
│    Agent    │ ──────────────▶│  run-task.py  │
│ (OpenClaw)  │                │  (detached)   │
└─────────────┘                └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │    Codex      │
                               │ codex exec    │
                               └──────┬───────┘
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼           ▼
                    Every 60s    On complete   On error/timeout
                    ┌────────┐  ┌──────────┐  ┌──────────────┐
                    │ ⏳ ping │  │ ✅ result │  │ ❌/⏰/💥 error│
                    │ silent │  │ channel  │  │   channel    │
                    └────────┘  └──────────┘  └──────────────┘
```

### WhatsApp notification flow

1. Heartbeat pings every 60s → WhatsApp direct
2. Final result → WhatsApp direct + `sessions_send`
3. Agent receives completion payload → processes it → sends summary

### Iterative continuation mode (wake behavior)

`--completion-mode` is optional and acts as a hint:

- `single` = one run → continuation summary → stop
- `iterate` = continuation summary + exactly one next iteration when gaps remain

Wake payload frames continuation as the **same ongoing OpenClaw conversation** after Codex replies to the previous launch.

In `iterate` mode:

- react briefly to Codex result
- evaluate goal completion
- if gaps remain: explain next fix and launch exactly one follow-up iteration
- if complete: report final outcome and stop

### Deterministic wake guard (anti-duplicate)

- Each run carries `run_id` and `wake_id`
- `run-task.py` keeps per-project state in `/tmp/codex-orchestrator-state-<hash>.json`
- Duplicate/stale wakes are skipped before delivery

### No silent launch policy (always-on)
- Silent launch is forbidden (not only in debug mode).
- On wake, agent must first post a visible decision turn:
  - `[TRACE][AGENT][WAKE_RECEIVED] ...`
  - `[TRACE][AGENT][DECISION] continue|stop ...`
- Only after that visible decision may the next Codex iteration be launched.

### Telegram notification flow (DM Threaded Mode — full pipeline)
1. 🚀 **Launch notification** → thread ✅ (silent; HTML; `<blockquote expandable>` for prompt; via `send_telegram_direct`; includes `Resume: <session-id|new>`)
2. ⏳ **Heartbeat** (every 60s) → thread ✅ (silent; plain text; via `send_telegram_direct`)
3. 📡 **Codex mid-task updates** → thread ✅ (on-disk Python script `/tmp/codex-notify-{pid}.py`; Codex calls file; prefix `"📡 🟢 Codex: "` auto-added)
4. ✅/❌/⏰/💥 **Result notification** → thread ✅ (HTML; `<blockquote expandable>` for result; via `send_telegram_direct`)
5. 🤖 **Agent continuation reply** → delivered to chat via `openclaw agent --deliver` ✅ (same session continuation is visible to user)

**`send_telegram_direct()`** is the core mechanism for all thread-targeted notifications from external scripts. It calls `api.telegram.org` directly with `message_thread_id` — bypasses the OpenClaw message tool entirely (which cannot route to DM threads from outside a session context).

**Fallback** — if agent wake fails (session locked/busy): `already_sent=True` is set after the direct send, so no duplicate is sent.

### Key detail: Telegram vs WhatsApp delivery

**WhatsApp:** Raw result sent directly (human sees it immediately) + `sessions_send` wakes agent for analysis.

**Telegram:** Result sent via `send_telegram_direct` → then agent is woken via `openclaw agent --session-id --deliver` so the continuation turn is visible in chat by default. This is the intended “same agent, same conversation” behavior after Codex completion.

**Why not `sessions_send` for Telegram?** `sessions_send` is blocked in the HTTP `/tools/invoke` deny list by architectural design. The `openclaw agent` CLI bypasses this limitation.

### Telegram DM Threads vs Forum Groups

Telegram has two distinct thread models. The key difference for `run-task.py` is how to route messages to the thread.

**The core problem with external scripts:**
- The OpenClaw `message` tool's `threadId` parameter is **Discord-specific** — ignored for Telegram
- Target format `"chatId:topic:threadId"` is rejected by the message tool's target resolver
- Session auto-routing works only inside active sessions — external scripts have no session context
- **Solution:** `send_telegram_direct()` bypasses the message tool entirely; calls `api.telegram.org` directly with `message_thread_id`

**DM Threaded Mode** (bot-user private chat with threads):
- All notifications use `send_telegram_direct(chat_id, text, thread_id=..., parse_mode=...)` ✅
- `thread_id` auto-extracted from session key `*:thread:<id>` by `extract_thread_id()`
- Launch + finish: `parse_mode="HTML"` with `<blockquote expandable>` for prompt/result
- Heartbeats + mid-task: `parse_mode=None` (plain text, avoid Markdown parse errors)
- **`parse_mode="Markdown"` trap**: finish messages contain `**text**` (CommonMark bold); Telegram MarkdownV1 rejects this with HTTP 400 — messages silently don't arrive
- **`replyTo` trap**: combining `replyTo` + `message_thread_id` can cause Telegram to reject the request or route incorrectly
- Agent continuation reply: `openclaw agent --session-id <uuid> --deliver` publishes the wake turn to chat so the user sees the same ongoing assistant conversation

**Forum Groups** (supergroup with Forum topics enabled):
- Same `send_telegram_direct()` approach works; `message_thread_id` is standard Bot API for Forum topics
- Auto-detected from session key pattern `*:thread:<id>`

**Codex mid-task updates:**
- Do NOT embed bot tokens or curl commands in the task prompt
- `run-task.py` writes `/tmp/codex-notify-{pid}.py` to disk before launching Codex
- Task prompt prepended with `[Automation context: ... python3 /tmp/codex-notify-{pid}.py 'msg' ...]`
- Codex calls the file as a normal local script
- Script automatically prepends `"📡 🟢 Codex: "` to all messages; cleaned up in `finally` block

## Reliability Features

### Timeout (default 2 hours)
- `--timeout 7200` → after 7200s: SIGTERM → wait 10s → SIGKILL
- Timeout notification sent to channel with tool call count and last activity
- Partial output saved to file

### Crash safety
- `try/except` wraps entire main → crash notification always sent
- Both channel notification and agent wake attempted on any failure

### PID tracking
- PID file written to `skills/codex-cli-task/pids/`
- Stale PIDs cleaned on startup
- Can check running tasks: `ls skills/codex-cli-task/pids/`

### Silent mode (Telegram only)
Telegram supports silent notifications (no sound).

Current policy: **all Codex notifications are silent** in Telegram:
- Heartbeat pings → `silent=True`
- Launch notifications → `silent=True`
- Mid-task updates (`📡 🟢 Codex`) → `silent=True`
- Final results → `silent=True`
- Wake-summary instruction requests `silent=True`

WhatsApp does NOT support silent mode — the flag is ignored for WhatsApp.

### Notification types

| Event | Emoji | WhatsApp delivery | Telegram delivery | DM thread? |
|-------|-------|-------------------|-------------------|------------|
| Launch | 🚀 | send_channel (Markdown) | send_telegram_direct (HTML, silent) | ✅ message_thread_id |
| Heartbeat | ⏳ | send_channel (Markdown) | send_telegram_direct (plain, silent) | ✅ message_thread_id |
| Codex mid-task update | 📡 | — | /tmp/codex-notify-{pid}.py (Bot API, silent) | ✅ message_thread_id |
| Success | ✅ | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Error | ❌ | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Timeout | ⏰ | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Crash | 💥 | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Agent continuation reply | 🤖 | — | openclaw agent wake (`--deliver`) | ✅ visible in chat |

## Codex CLI Flags

- `exec "task"` — non-interactive run
- `resume <session-id> "task"` — continue a previous Codex session
- `--dangerously-bypass-approvals-and-sandbox` — no confirmation prompts
- `--experimental-json --output-last-message` — real-time activity tracking + final output capture
- `--full-auto` — optional safer automation mode

### Why NOT exec/pty?
- `exec` has 2 min default timeout → kills long tasks
- Even with `pty:true`, output has escape codes, hard to parse
- `nohup` + detached runner: clean, detached, reliable

### Git requirement

Codex needs a git repo. `run-task.py` auto-inits if missing.

## Python 3.9 Compatibility

`run-task.py` uses `Optional[X]` from `typing` (not `X | None`) for compatibility with Python 3.9. The union syntax (`X | None`) requires Python 3.10+.

```python
# Correct (3.9+)
from typing import Optional
def foo(x: Optional[str]) -> Optional[str]: ...

# Would break on 3.9
def foo(x: str | None) -> str | None: ...
```

## Full E2E Test (reference)

Use this when you need to validate the **entire pipeline** in one run:

- launch notification in source thread
- heartbeat after >60s
- Codex mid-task progress update
- final result in source thread
- agent wake attempt with summary step

### Pass criteria

1. Launch message appears in the same thread (with expandable prompt quote)
2. At least one wrapper heartbeat appears after ~60s
3. At least one mid-task update appears (via `/tmp/codex-notify-<pid>.py`)
4. Final result appears in the same thread (expandable result quote)
5. Agent wake continuation is delivered (`openclaw agent --session-id ... --deliver`) and appears visibly in chat

### Canonical full test prompt pattern

- keep prompt compact for routine testing
- force runtime >60s (`sleep 70`) to trigger wrapper heartbeat
- explicitly instruct Codex to call the notify script at least twice
- include a short structured report so output is easy to verify

### Interactive test rule (time budget)

For `iterate`-mode testing, do exactly one continuation step after phase 1.

- Phase 1: intentionally incomplete output
- Continuation #1: close the gap and finish
- Stop there

Reason: validates the iterative path without turning a routine test into a long multi-hop run.

### Visibility rule (mandatory)

Between `✅ OpenAI Codex completed` and any next `🚀 OpenAI Codex started`, there must be a user-facing analysis message in the thread.

- The agent must first post what was done, what gaps remain, and the decision to continue/stop
- Only after that message may it launch the next iteration
- No silent jump from completion directly to next start

### Canonical launch (minimal mode)

```bash
cat > /tmp/codex-full-test-prompt.txt << 'EOF'
# 1) notify script now
# 2) create test file
# 3) sleep 70 + notify again
# 4) run several shell commands
# 5) return short structured report
EOF

python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-full-test-prompt.txt)" \
  --project /tmp/codex-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --validate-only

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-full-test-prompt.txt)" \
  --project /tmp/codex-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 900 \
  > /tmp/codex-full-test.log 2>&1 &
```

### Verification artifacts

- wrapper log: `/tmp/codex-full-test.log`
- Codex output: `/tmp/codex-YYYYMMDD-HHMMSS.txt`
- session registry entry in `~/.openclaw/codex_sessions.json`

## Long-running task guidance

If a Codex task is expected to run longer than ~1 minute, explicitly ask Codex to send intermediate progress updates during execution.

Recommended wording:

- "Send a progress update when you start"
- "Send another update after major milestone(s)"
- "If task exceeds 60 seconds, send at least one heartbeat-style update"

For Telegram thread-safe runs, updates should use the injected automation script (`/tmp/codex-notify-<pid>.py`).

### Canonical launch (minimal mode)

```bash
cat > /tmp/codex-full-test-prompt.txt << 'EOF'
# ~10 lines
# 1) use notify helper now
# 2) create a test artifact
# 3) sleep 70 + notify again
# 4) run several shell commands
# 5) return short structured report
EOF

python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-full-test-prompt.txt)" \
  --project /tmp/codex-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --validate-only

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-full-test-prompt.txt)" \
  --project /tmp/codex-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 900 \
  > /tmp/codex-full-test.log 2>&1 &
```

## Examples

### WhatsApp: Create a tool

```bash
nohup python3 {baseDir}/run-task.py \
  -t "Create a Python CLI tool that converts markdown to HTML with syntax highlighting. Save as convert.py" \
  -p ~/projects/md-converter \
  -s "agent:main:whatsapp:group:120363425246977860@g.us" \
  > /tmp/codex-run.log 2>&1 &
```

### Telegram: Research codebase (thread-safe)

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 1800 \
  > /tmp/codex-run.log 2>&1 &
```

### Telegram Threaded Mode: Mid-task updates from Codex

`run-task.py` automatically creates an on-disk notification script before launching Codex, so Codex can send progress updates without seeing bot tokens in the prompt.

```bash
cat > /tmp/codex-prompt.txt << 'EOF'
STEP 1: Write analysis to /tmp/report.txt.

After step 1, send a progress notification using the script from the
automation context above.

STEP 2: Write summary to /tmp/summary.txt.
EOF

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 1800 \
  > /tmp/codex-run.log 2>&1 &
```

> Never embed bot tokens or raw curl commands in the task prompt.

> **Quick reference: launching from a Telegram DM thread (minimal mode)**
> ```bash
> python3 {baseDir}/run-task.py \
>   --task "probe" \
>   --project ~/projects/x \
>   --session "agent:main:main:thread:<THREAD_ID>" \
>   --validate-only
>
> nohup python3 {baseDir}/run-task.py \
>   --task "$(cat /tmp/prompt.txt)" \
>   --project ~/projects/x \
>   --session "agent:main:main:thread:<THREAD_ID>" \
>   --timeout 900 \
>   > /tmp/codex-run.log 2>&1 &
> ```
> - Required: `--task`, `--project`, `--session`
> - `THREAD_ID` is auto-extracted from session key
> - target + session UUID are auto-resolved when possible
> - if routing is inconsistent/unresolved, script exits with `❌ Invalid routing`
> - launch/heartbeat/result notifications stay on the source thread

### Long task with extended timeout

```bash
nohup python3 {baseDir}/run-task.py \
  -t "Refactor the entire auth module to use JWT tokens" \
  -p ~/projects/backend \
  -s "agent:main:whatsapp:group:120363425246977860@g.us" \
  --timeout 3600 \
  > /tmp/codex-run.log 2>&1 &
```

## Cost

- Codex runs outside the live OpenClaw conversation
- zero OpenClaw tokens while Codex works
- Codex billing depends on your Codex authentication mode

## Session Resumption

Codex sessions can be resumed to continue previous conversations. This is useful for:

- follow-up tasks building on previous research
- continuing after timeouts or interruptions
- multi-step workflows where context matters

### Resume ID — Critical Rule

`--resume` takes the **Codex session ID**, not `run_id` or `wake_id`.

Correct source:

```text
📝 Session registered: <session-id-here>
```

That is the value to pass as `--resume <session-id>`.

### How to Resume

When a task completes, the session ID is captured and saved to `~/.openclaw/codex_sessions.json`.

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/my-project \
  --session "SESSION_KEY" \
  --resume <session-id> \
  > /tmp/codex-run.log 2>&1 &
```

### Session Labels

Use `--session-label` to give sessions human-readable names for easier tracking.

### Listing Recent Sessions

```python
from session_registry import list_recent_sessions, find_session_by_label

recent = list_recent_sessions(hours=72)
for session in recent:
    print(f"{session['session_id']}: {session['label']} ({session['status']})")
```

Or manually inspect:

```bash
cat ~/.openclaw/codex_sessions.json
```

### When to Resume vs Start Fresh

**Resume when:**

- you need context from previous conversation
- building on previous research/analysis
- continuing interrupted work

**Start fresh when:**

- unrelated task
- you want a clean slate
- previous context may cause confusion

### Resume Failure Handling

If a session ID is invalid or expired:

- error message sent to channel with suggestion to start fresh
- process exits cleanly
- check stderr in `/tmp/codex-run.log`

Common resume failures:

- invalid session ID
- expired/non-resumable session
- session from unrelated context or wrong project expectation

### Example Workflow

**Step 1: Initial research**

```bash
write /tmp/research-prompt.txt with "Research the codebase architecture for project X"

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/research-prompt.txt)" \
  --project ~/projects/project-x \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --session-label "Project X architecture research" \
  > /tmp/codex-run.log 2>&1 &
```

**Step 2: Find session ID**

```bash
tail /tmp/codex-run.log
cat ~/.openclaw/codex_sessions.json | grep "Project X"
```

**Step 3: Follow-up implementation**

```bash
write /tmp/implement-prompt.txt with "Based on your research, implement the authentication module"

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/implement-prompt.txt)" \
  --project ~/projects/project-x \
  --session "SESSION_KEY" \
  --resume <session-id-from-step-1> \
  --session-label "Project X auth implementation" \
  > /tmp/codex-run2.log 2>&1 &
```

## Wake Troubleshooting

When the agent wake / continue chain fails:

- verify `sessions_send` is enabled
- verify session visibility is `all`
- verify Telegram thread routing with `--validate-only`
- inspect `/tmp/codex-run.log`
- inspect the session registry and output file path

Common failure patterns:

- wrong thread session key
- Telegram target/session UUID could not be resolved
- stale or duplicate wake suppressed by dedupe guard
- resume ID is wrong
- progress helper was not called in long-running test scenarios

## Current Stable Behavior

This is the current intended behavior of the Codex adaptation:

- wake continuity: the agent gets a continuation turn after Codex finishes
- Telegram thread routing is strict by default
- WhatsApp gets direct result delivery plus agent wake
- session resumption uses Codex session IDs captured from the JSON event stream

Current locally validated behavior in this repo:

- Codex `exec` via `--experimental-json`
- Codex `resume`
- output capture via `--output-last-message`
- OpenClaw-style async launch / heartbeat / completion flow in the runner logic
