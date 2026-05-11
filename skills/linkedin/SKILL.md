---
name: linkedin
description: LinkedIn automation via browser relay or cookies for messaging, profile viewing, and network actions.
homepage: https://linkedin.com
metadata: {"clawdbot":{"emoji":"💼"}}
---

# LinkedIn

Use browser automation to interact with LinkedIn - check messages, view profiles, search, and send connection requests.

## Connection Methods

### Option 1: Chrome Extension Relay (Recommended)
1. Open LinkedIn in Chrome and log in
2. Click the Clawdbot Browser Relay toolbar icon to attach the tab
3. Use `browser` tool with `profile="chrome"`

### Option 2: Isolated Browser
1. Use `browser` tool with `profile="clawd"` 
2. Navigate to linkedin.com
3. Log in manually (one-time setup)
4. Session persists for future use

## Common Operations

### Check Connection Status
```
browser action=snapshot profile=chrome targetUrl="https://www.linkedin.com/feed/"
```

### View Notifications/Messages
```
browser action=navigate profile=chrome targetUrl="https://www.linkedin.com/messaging/"
browser action=snapshot profile=chrome
```

### Search People
```
browser action=navigate profile=chrome targetUrl="https://www.linkedin.com/search/results/people/?keywords=QUERY"
browser action=snapshot profile=chrome
```

### View Profile
```
browser action=navigate profile=chrome targetUrl="https://www.linkedin.com/in/USERNAME/"
browser action=snapshot profile=chrome
```

### Send Message (confirm with user first!)
1. Navigate to messaging or profile
2. Use `browser action=act` with click/type actions
3. Always confirm message content before sending

## Safety Rules
- **Never send messages without explicit user approval**
- **Never accept/send connection requests without confirmation**
- **Avoid rapid automated actions** - LinkedIn is aggressive about detecting automation
- Rate limit: ~30 actions per hour max recommended

## Session Cookie Method (Advanced)
If browser relay isn't available, extract the `li_at` cookie from browser:
1. Open LinkedIn in browser, log in
2. DevTools → Application → Cookies → linkedin.com
3. Copy `li_at` value
4. Store securely for API requests

## Troubleshooting
- If logged out: Re-authenticate in browser
- If rate limited: Wait 24 hours, reduce action frequency
- If CAPTCHA: Complete manually in browser, then resume
