# Gemini Browser — ClawHub Skill

Automate [Google Gemini](https://gemini.google.com) interactions via [OpenClaw](https://openclaw.ai) Browser Relay in Chrome.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **OpenClaw** | Installed and running |
| **Browser Relay Extension** | Chrome MV3 extension installed, auth token configured |
| **Google Account** | Logged in within Chrome (Gemini requires authentication) |

## Usage

### 1. Open Gemini & Attach Relay

```bash
open -a "Google Chrome" "https://gemini.google.com"
```

Then **manually click** the Browser Relay extension icon on the Gemini tab (badge shows "ON").

### 2. Verify Connection & Get Tab ID

```
browser action=status profile=chrome    # should show cdpReady: true
browser action=tabs profile=chrome      # note the targetId for the Gemini tab
```

### 3. Input Query

Gemini uses a Quill rich-text editor. Inject text via JavaScript:

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const editor = document.querySelector('div.ql-editor[contenteditable=\"true\"]'); if (!editor) return 'editor not found'; editor.focus(); editor.innerHTML = '<p>YOUR_QUERY_HERE</p>'; editor.dispatchEvent(new Event('input', { bubbles: true })); return 'ok'; })()"
}
```

### 4. Submit

```
browser action=act profile=chrome targetId=<id> request={"kind":"press","key":"Enter"}
```

### 5. Wait for Response

Poll until the stop button disappears:

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const stop = document.querySelector('button[aria-label*=\"Stop\"]'); return stop ? 'generating' : 'done'; })()"
}
```

### 6. Extract Response

**Option A — Clipboard** (recommended):

```
browser action=snapshot profile=chrome targetId=<id>
# Find the Copy button ref in the snapshot
browser action=act profile=chrome targetId=<id> request={"kind":"click","ref":"<copy_button_ref>"}
pbpaste
```

**Option B — DOM extraction** (fallback):

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const msgs = document.querySelectorAll('.model-response-text'); if (msgs.length === 0) return 'no response found'; return msgs[msgs.length - 1].innerText; })()"
}
```

### New Chat

```
browser action=navigate profile=chrome targetId=<id> targetUrl="https://gemini.google.com"
```

## ⚠️ Security

This skill uses Chrome DevTools Protocol (CDP) to control your **real Chrome browser**. The agent can access anything visible in the attached tab.

- Browser Relay requires **manual click** to attach — agent cannot auto-attach
- Relay is **loopback-only** (`127.0.0.1`) with auth token
- **Recommendation**: Use a dedicated Chrome profile with a non-primary Google account

See [Security Considerations](./SKILL.md#security-considerations) in SKILL.md for details.

## License

MIT-0
