---
name: workstation
version: 1.0.0
description: "Control Varie Workstation sessions (Claude Code multi-session orchestration). Use when: (1) user wants to work on / start / resume a coding project, (2) checking session status, (3) sending commands to a session, (4) listing active sessions, (5) creating new sessions, (6) user replies to a plan approval or question notification, (7) user wants to stop/cancel/interrupt a session, (8) user wants a screenshot of a session or screen. Triggers on: work on, start, resume, sessions, workers, workstation, dispatch, project name, approve, reject, option, pick, yes, no, stop, cancel, interrupt, escape, kill, stuck, screenshot, show me, capture, what does it look like."
homepage: "https://github.com/varie-ai/workstation"
metadata:
  openclaw:
    emoji: "🖥️"
    requires:
      bins:
        - wctl
---

# Workstation Control

Control Varie Workstation coding sessions via `wctl`.

## Step 0: Check Pending Prompts (ALWAYS DO THIS FIRST)

Before ANY routing or session work, check if a session is waiting for user input:

```bash
cat ~/.openclaw/workspace/pending-prompts.json 2>/dev/null || echo '{"prompts":[]}'
```

**If `prompts` array is non-empty** AND the user's message looks like a response (a number, "approve", "yes", "no", "reject", short answer, or references a project in the pending list):
→ This is a reply to a pending prompt. Go directly to **"Responding to Session Prompts"** section below.

**If `prompts` array is empty** OR user's message is clearly a new request (mentions a different project, asks to start/create something, etc.):
→ Continue to Smart Routing below.

## Smart Routing (Main Workflow)

When the user mentions working on a project (e.g., "work on my-api", "resume frontend work", "start auth refactor"), follow this decision tree **silently** — do NOT ask the user unless you hit an ambiguous case:

### Step 1: Check daemon + list sessions
```bash
wctl list
```
(If daemon not running, tell user to start the Workstation app.)

### Step 2: Match project

Look at the `repo` field in each worker. Match the user's project mention against repo names (fuzzy — "frontend" matches "my-frontend-app", "api" matches "backend-api-service").

**If session exists and task context aligns** (user's request fits the current taskId/workContext):
→ `wctl dispatch <session-id> "<user's message>"`

**If session exists but task context doesn't align** (user wants to work on something different in the same repo):
→ Ask: "There's already a session for {repo} working on {taskId}. Should I send this to that session, or create a fresh one?"

**If no session exists for the project:**
→ Go to Step 3.

**If multiple repos match** (e.g., "api" could be frontend-api or backend-api):
→ Ask which one.

### Step 3: Auto-create session (no matching session found)

```bash
wctl discover
```

Find the project path from the discovered list, then:

```bash
wctl create <repo> <path> <task-id>
```

Derive `task-id` from the user's message (e.g., "work on auth refactor" → task-id: `auth-refactor`). Keep it short, lowercase, hyphenated.

After creation, confirm: "Started new session for {repo} ({task-id})."

If project not found in discover results, ask the user for the repo path.

## Commands Reference

| Command | Use |
|---|---|
| `wctl status --human` | Check daemon alive |
| `wctl list` | List sessions (JSON, for parsing) |
| `wctl list --human` | List sessions (readable, for user) |
| `wctl dispatch <id> "<msg>"` | Send message to existing session |
| `wctl dispatch-answers <id> <a1> <a2>...` | Send multi-question answers. Use `next:N` for multi-select |
| `wctl create <repo> <path> [task]` | Create new session |
| `wctl escape <id>` | Send Escape key (cancel prompt/menu) |
| `wctl interrupt <id>` | Send Ctrl+C (stop running process) |
| `wctl enter <id>` | Send Enter key (confirm/dismiss) |
| `wctl screenshot <id>` | Screenshot a session (focus + capture) |
| `wctl screenshot --screen` | Screenshot main display |
| `wctl set-remote-mode on\|off` | Enable/disable remote mode (bridge auto-focus for screenshots) |
| `wctl discover` | Scan for project repos |

## Session Control (Escape / Interrupt)

When the user wants to stop, cancel, or interrupt a session:

| User says | Command |
|---|---|
| "stop session X", "cancel", "kill it", "abort" | `wctl interrupt <id>` (sends Ctrl+C) |
| "escape", "go back", "cancel prompt", "dismiss" | `wctl escape <id>` (sends Escape key) |
| "press enter", "confirm", "continue", "submit" | `wctl enter <id>` (sends Enter key) |

**Strategy:** If unsure, try `escape` first (safe — cancels UI prompts). If still stuck, use `interrupt` (harder — sends SIGINT).

## Screenshots

To show the user what a session looks like:

```bash
# 1. Capture the session
wctl screenshot <session-id>
# Returns: { "status": "ok", "imagePath": "/path/to/screenshot.png" }

# 2. Send to user using the built-in message tool
```

To deliver the screenshot, use your built-in `message` tool (not bash) with `action: "send"` and `mediaUrl` pointing to the captured image path. The message tool is session-bound — it automatically targets the channel and user you're currently chatting with. No need to specify channel or target manually.

If the `message` tool is unavailable, fall back to the CLI:
```bash
openclaw message send --media <imagePath> --channel <channel> --target <target>
```
Replace `<channel>` and `<target>` with the values from the current conversation (e.g., `telegram` + the user's chat ID, or `whatsapp` + their phone number).

For full screen (e.g., to see Chrome, other apps): `wctl screenshot --screen`

**When to use:** User says "show me", "screenshot", "what does it look like", "what's happening in session X".

**Always** send the image via `openclaw message send --media` after capturing — wctl only saves the file locally.

## Critical Rules

1. **dispatch for existing sessions** — always. It types directly into the terminal. Never use `wctl route` (it may restart Claude and disrupt work).
2. **Never prepend `claude` to messages** — just pass the user's message as-is to dispatch.
3. **Add `--human` when showing output to user** — JSON otherwise for your own parsing.
4. **Ask when unsure** — if you can't confidently match the user's message to exactly one session/project, ask to confirm. Wrong dispatches disrupt real coding work. Autonomy is good, but correctness matters more.
5. **Never guess or hallucinate** — don't invent project names, session IDs, or options. Always check `wctl list` and `pending-prompts.json` for ground truth.
6. **Use "Chat about this" as fallback** — if you can't confidently map the user's answer to option numbers for a multi-question prompt, use `--chat-arrows 20` to select "Chat about this" and then dispatch their message as text. A stuck question modal is worse than falling back to chat.

## Responding to Session Prompts

When Step 0 finds pending prompts and the user's message is a response:

### Step 1: Identify the target session

The pending prompt has a `project` field. Use it to find the session:

```bash
wctl list
```

Find the session whose `repo` matches the pending prompt's `project`. Use its `sessionId`.

If multiple prompts are pending, match the user's message to the most relevant one (by project name mention or most recent).

### Step 2: Map intent to response

**Plan approval (4 options):**
| User says | Dispatch |
|---|---|
| "1", "clear context", "bypass all" | `wctl dispatch <id> "1"` |
| "2", "bypass permissions", "yes bypass" | `wctl dispatch <id> "2"` |
| "3", "approve", "yes", "go ahead", "lgtm", "manually approve" | `wctl dispatch <id> "3"` |
| "reject", "no", feedback like "change X to Y" | **Two steps:** `wctl dispatch <id> "4"` then wait 2s then `wctl dispatch <id> "<their feedback>"` |

Default to **option 3** ("yes, manually approve edits") when user says generic approval like "yes", "approve", "go ahead".

**Important for option 4 (feedback/reject):** This is a two-step process. First dispatch "4" to select the text input option, wait 2 seconds for the text prompt to appear, then dispatch the feedback text. Example:
```bash
wctl dispatch abc123 "4"
sleep 2
wctl dispatch abc123 "don't modify the database schema"
```

**Question — ALWAYS dispatch the OPTION NUMBER, never text:**

Look up the user's answer in the pending prompt's `questions` array and find the matching option number. Example: if options are `["1. Night", "2. Day", "3. Morning"]` and user says "night", dispatch `"1"` (not `"night"`).

| User says | Action |
|---|---|
| A number ("1", "2") | Dispatch that number directly |
| A word matching an option label ("night", "dog") | Find the option number and dispatch the NUMBER |
| Free text not matching any option | Dispatch the text (for "Other" option) |

**Single question:** Use regular dispatch: `wctl dispatch <id> "2"`

**Multiple questions:** Use `dispatch-answers` — it sends each answer without Enter (Claude auto-advances on single-select), then sends Enter at the end to submit. Map EACH answer to its option NUMBER, then pass them all in one command:

```bash
wctl dispatch-answers <id> 2 1 3
```

This sends: "2" → wait → "1" → wait → "3" → wait → Enter (submit). No chaining or sleep needed — timing is handled internally.

**Multi-select questions** (checkboxes — check the `multiSelect` field in pending-prompts.json): Typing a number toggles it on/off but does NOT advance (cursor stays at position 1). After selecting all options, use `next:N` to arrow-down N times to the "Next"/"Submit" button and press Enter. N = the number of options for that question (including "Other"), from `questions[i].options.length`.

```bash
wctl dispatch-answers <id> 1 2 next:5 2
```

This sends: "1" (toggle) → "2" (toggle) → arrow-down×5 to "Next" → Enter → "2" (next question, single-select) → Enter (submit all).

Example with 4 questions (multi/5opts, single, single, multi/5opts):
```bash
wctl dispatch-answers <id> 1 4 next:5 2 1 1 3 next:5
```
Each `next:N` is self-contained — N is always `questions[i].options.length` for that specific multi-select question.

**How to tell if a question is multi-select:** The pending prompt's `questions` array has a `multiSelect` field per question. If `multiSelect: true`, you MUST add `next:N` after their selections. If `multiSelect: false` (or missing), it's single-select and auto-advances — no `next` needed.

**If the last question is multi-select**, use `next:N` as the last token — it will click "Submit" instead of "Next" (same button position). The final Enter to confirm all answers is sent automatically after all tokens.

**"Chat about this"** — at the very bottom of the question modal (below all options and Next/Submit), there's a "Chat about this" option. Arrow keys do NOT wrap/circulate, so you can safely overshoot. Use `--chat-arrows N` to select it. Calculate N based on the **first question only**:
- First question is **multi-select** with K options (incl. Other): `--chat-arrows K+1` (extra arrow for Next button)
- First question is **single-select** with K options (incl. Other): `--chat-arrows K`

```bash
# Example: first question is multi-select with 5 options → 6 arrows
wctl dispatch-answers <id> --chat-arrows 6
# Example: first question is single-select with 3 options → 3 arrows
wctl dispatch-answers <id> --chat-arrows 3
```
When using `--chat-arrows`, no answer tokens are needed — it replaces the entire answer flow.

**FALLBACK RULE:** If you are unsure how to map the user's answers to option numbers, or the user's message is vague/unclear, **always use `--chat-arrows` instead of guessing**. This lets the user follow up with a simple text prompt rather than getting stuck on a broken selection. Since arrows don't wrap, you can safely use `--chat-arrows 20` if unsure about the exact count — it will land on "Chat about this" regardless.

After selecting "Chat about this", immediately dispatch the user's message as a follow-up:
```bash
wctl dispatch-answers <id> --chat-arrows 20
sleep 3
wctl dispatch <id> "<user's original message>"
```

### Step 3: Confirm

After dispatching, tell the user: "Sent response to {project}."

## Errors

- **daemon not running** → tell user to start Workstation app
- **session not found** → `wctl list` to show valid IDs
- **project not in discover** → ask user for repo path
- **timeout** → session busy, retry shortly

## Quick Start

### Install

1. Install the [Varie Workstation](https://github.com/varie-ai/workstation) Electron app (macOS arm64).
2. Install `wctl` (the CLI that bridges OpenClaw to Workstation):
   ```bash
   # wctl ships with Workstation — symlink it to your PATH:
   ln -sf /path/to/varie-workstation/openclaw/wctl.js ~/.local/bin/wctl
   chmod +x ~/.local/bin/wctl
   ```
3. Copy this skill to your OpenClaw workspace:
   ```bash
   cp -r workstation ~/.openclaw/workspace/skills/workstation
   ```

### Configure

- Launch the Workstation app and verify it's running: `wctl status`
- Enable remote mode for mobile screenshot support: `wctl set-remote-mode on`
- The OpenClaw-Workstation bridge (bundled in the app) writes pending prompts to `~/.openclaw/workspace/pending-prompts.json` — this enables bidirectional question/approval flows from your phone.

### Verify

```bash
wctl status --human    # Should show "Workstation is running"
wctl list --human      # Should list active sessions (if any)
```

## Prerequisites

This skill requires the **Varie Workstation** app — an Electron-based multi-session Claude Code orchestration environment. The skill is the mobile control layer: it lets you manage Workstation sessions from Telegram, WhatsApp, or any OpenClaw channel.

| Dependency | What it does | Required? |
|---|---|---|
| [Varie Workstation](https://github.com/varie-ai/workstation) | Electron app hosting Claude Code terminals | Yes |
| `wctl` CLI | Bridges OpenClaw commands to Workstation's Unix socket | Yes (ships with Workstation) |
| OpenClaw-Workstation bridge | Forwards session events (questions, approvals) to OpenClaw for mobile notifications | Yes (bundled in Workstation) |

Without Workstation running, the skill will report "daemon not running" for all commands.

## Security & Guardrails

### Permissions
- `wctl` communicates with Workstation via a local Unix socket (`/tmp/varie-workstation.sock`). No network calls — all traffic is local.
- Screenshot capture requires macOS Screen Recording permission for the Workstation app.

### Declared File Access
- **`~/.openclaw/workspace/pending-prompts.json`** (read-only) — This file is read on every invocation (Step 0) to check if any Claude Code session is waiting for user input. It is written by the OpenClaw-Workstation bridge, not by this skill. Contents: question text, option labels, and project identifiers from active sessions. No credentials, secrets, or user data. The file may not exist until the bridge creates it — the skill handles this gracefully with a fallback empty response.

### Screenshots
- **Session screenshots** (`wctl screenshot <id>`) capture only the specific Workstation terminal window for the targeted session.
- **Full-screen screenshots** (`wctl screenshot --screen`) capture the entire display, which may include unrelated windows and sensitive content. This command is only executed when the user explicitly requests a full-screen capture (e.g., "screenshot my screen", "show me everything").
- Screenshots are saved locally to `~/.openclaw/media/` with a 30-minute TTL cleanup.
- Screenshots are sent only to the user's own messaging channel (Telegram/WhatsApp) — never to third parties or external services.

### Confirmations Before Risky Actions
- The skill asks for confirmation before creating new sessions or when multiple repos match ambiguously.
- `wctl interrupt` (Ctrl+C) is reserved for explicit user requests — the skill never sends it autonomously.

### Data Handling
- `openclaw message send` routes media through your configured OpenClaw channel (Telegram/WhatsApp). Images traverse the channel provider's servers but are only sent to the requesting user's conversation.

### Input Validation
- The skill maps user intent to option numbers before dispatching — free text is never injected into PTY commands without validation.
- The "Chat about this" fallback is used whenever intent mapping is uncertain, preventing wrong selections.

## External Endpoints

| Endpoint | Protocol | Data Sent |
|---|---|---|
| `/tmp/varie-workstation.sock` | Unix socket (local) | Session commands (list, dispatch, create, screenshot) |
| `~/.openclaw/workspace/pending-prompts.json` | Local file read | None (read-only) |
| `openclaw message send --channel --target` | OpenClaw channel (Telegram/WhatsApp) | Screenshot images (when user requests) |

No external APIs are called directly by this skill. All network communication goes through OpenClaw's channel layer.

## Trust Statement

This skill controls local Claude Code sessions running inside the Varie Workstation app. All communication is via local Unix socket — no data leaves your machine unless you request a screenshot, which is sent through your configured OpenClaw messaging channel. Only install if you trust the Varie Workstation app and your OpenClaw channel configuration.

## Publisher

@masqueradeljb

## Links

- [Varie Workstation](https://github.com/varie-ai/workstation) — The Electron app this skill controls
- [OpenClaw](https://docs.openclaw.ai/) — The AI agent gateway this skill runs on
