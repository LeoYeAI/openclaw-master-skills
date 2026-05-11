---
name: Gemini Browser
description: >-
  Query Google Gemini via browser automation using OpenClaw's Browser Relay.
  Use when you need to ask Gemini questions and get AI responses.
  Requires OpenClaw with Browser Relay Chrome extension configured.
---

# Gemini Browser Skill

Query Google Gemini (`gemini.google.com`) via OpenClaw Browser Relay and extract responses.

> **⚠️ Security Notice**: This skill operates on your **real Chrome browser** with
> your logged-in Google session via CDP (Chrome DevTools Protocol). The agent will
> have access to anything visible in the attached tab. Only attach tabs you
> explicitly intend for the agent to control. See [Security Considerations](#security-considerations).

## Prerequisites

- **OpenClaw** installed and running (this skill uses OpenClaw's `browser` command)
- **OpenClaw Browser Relay** Chrome extension installed and configured
  - Extension binds to loopback `127.0.0.1:18792` by default
  - Gateway auth token must be configured in extension options
- **Google account** logged in within Chrome (Gemini requires authentication)
- Use `profile=chrome` to relay through your existing Chrome (not the isolated `profile=openclaw-managed`)

## Quick Start

```bash
# 1. Open Gemini in Chrome
open -a "Google Chrome" "https://gemini.google.com"

# 2. Manually click the Browser Relay extension icon on the Gemini tab to attach
#    (the badge will show "ON" when attached)

# 3. Verify relay is connected
browser action=status profile=chrome
# Should show cdpReady: true

# 4. List tabs
browser action=tabs profile=chrome
# Note the targetId for the Gemini tab
```

## Input Method

Gemini uses a **Quill rich-text editor** (`contenteditable` div), not a standard `<textarea>`. You must inject text via JavaScript:

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const editor = document.querySelector('div.ql-editor[contenteditable=\"true\"]'); if (!editor) return 'editor not found'; editor.focus(); editor.innerHTML = '<p>YOUR_QUERY_HERE</p>'; editor.dispatchEvent(new Event('input', { bubbles: true })); return 'ok'; })()"
}
```

Then submit:

```
browser action=act profile=chrome targetId=<id> request={"kind":"press","key":"Enter"}
```

## Complete Workflow

### 1. Prepare

Open Gemini in Chrome and **manually attach** the Browser Relay extension to the tab.

```bash
open -a "Google Chrome" "https://gemini.google.com"
# Then click the Browser Relay extension icon on the Gemini tab
```

### 2. Get Tab ID

```
browser action=tabs profile=chrome
```

Find the Gemini tab entry and note its `targetId`.

### 3. Input Query

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const editor = document.querySelector('div.ql-editor[contenteditable=\"true\"]'); if (!editor) return 'editor not found'; editor.focus(); editor.innerHTML = '<p>What is quantum computing?</p>'; editor.dispatchEvent(new Event('input', { bubbles: true })); return 'ok'; })()"
}
```

### 4. Submit

```
browser action=act profile=chrome targetId=<id> request={"kind":"press","key":"Enter"}
```

### 5. Wait for Response

Gemini may take 10–60 seconds. Poll for completion by checking if the stop button has disappeared:

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const stop = document.querySelector('button[aria-label*=\"Stop\"]'); return stop ? 'generating' : 'done'; })()"
}
```

### 6. Extract Response

**Option A — Clipboard (recommended, preserves Markdown formatting):**

```
# Take a snapshot and find the Copy button
browser action=snapshot profile=chrome targetId=<id>

# Click the Copy button by its ref from the snapshot
browser action=act profile=chrome targetId=<id> request={"kind":"click","ref":"<copy_button_ref>"}

# Read from clipboard
pbpaste
```

**Option B — DOM extraction (fallback):**

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const msgs = document.querySelectorAll('.model-response-text'); if (msgs.length === 0) return 'no response found'; return msgs[msgs.length - 1].innerText; })()"
}
```

## New Chat

For unrelated queries, start a fresh chat to avoid context pollution:

```
browser action=navigate profile=chrome targetId=<id> targetUrl="https://gemini.google.com"
```

## Response Completion Signals

The response is complete when:
- The **stop button** disappears
- A **copy button** appears below the response
- **Suggested follow-up chips** appear

## Security Considerations

> **⚠️ Important**: Understand these risks before using this skill.

1. **Session access**: `profile=chrome` uses your real Chrome with all logged-in sessions. The agent can see and interact with anything in the attached tab, including your Google account context.
2. **JavaScript evaluation**: The `evaluate` action runs arbitrary JavaScript in the page context. This skill limits it to DOM manipulation for the input field, but the mechanism itself is powerful.
3. **Manual attachment required**: The Browser Relay extension must be **manually clicked** by you to attach — the agent cannot auto-attach to arbitrary tabs. Only attach the specific Gemini tab.
4. **Loopback only**: The relay binds to `127.0.0.1` and requires an auth token, preventing remote access.
5. **Recommendation**: Use a **separate Chrome profile** dedicated to AI automation, logged into a non-primary Google account, to limit exposure.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `cdpReady: false` | Click the Browser Relay extension icon on the Gemini tab to re-attach |
| Tab not found | Run `browser action=tabs profile=chrome` to refresh tab list |
| Editor not found | Page may not be fully loaded; wait and retry. Gemini may have changed DOM — check for `div.ql-editor` |
| Copy button not found | Response may still be generating; poll stop button status first |
| Login wall | Ensure Chrome is logged into a Google account |
| Context overflow | Navigate to `gemini.google.com` for a fresh chat |
