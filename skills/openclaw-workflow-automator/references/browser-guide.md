# Browser Automation Guide

## Overview

OpenClaw provides CDP (Chrome DevTools Protocol) control of a managed Chrome instance.
The agent can automate any browser interaction a human can perform.

## Browser Primitives

### Navigation
- `browser: goto <URL>` — Navigate to a URL. Waits for page load.
- `browser: back` / `browser: forward` — History navigation.
- `browser: reload` — Refresh the current page.

### Element Interaction
- `browser: click <selector>` — Click an element by CSS selector or visible text.
- `browser: type <selector> <text>` — Type text into an input field.
- `browser: select <selector> <value>` — Choose from a dropdown.
- `browser: hover <selector>` — Hover over an element.
- `browser: scroll <direction>` — Scroll the page up, down, or to an element.

### Data Extraction
- `browser: read page` — Get the full text content of the current page.
- `browser: read element <selector>` — Get text from a specific element.
- `browser: read table <selector>` — Extract a table as structured data.
- `browser: read attribute <selector> <attr>` — Get an element's attribute value.

### Screenshots
- `browser: screenshot` — Capture the full visible page.
- `browser: screenshot <selector>` — Capture a specific element.
- Screenshots are saved to `~/.openclaw/workflow-automator/screenshots/`
  with timestamp-based filenames.

### Tabs
- `browser: new tab <URL>` — Open a URL in a new tab.
- `browser: switch tab <index>` — Switch to a specific tab.
- `browser: close tab` — Close the current tab.
- `browser: list tabs` — Show all open tabs.

### Waiting
- `browser: wait for <selector>` — Wait until an element appears (max 30s).
- `browser: wait for <selector> gone` — Wait until an element disappears.
- `browser: wait <seconds>` — Explicit wait (use sparingly).

## Common Patterns

### Login Flow
```
Step 1: browser-navigate → goto login page
Step 2: browser-fill → enter username
Step 3: browser-fill → enter password
Step 4: browser-click → click Sign In
Step 5: browser-wait → wait for dashboard to load
```
On first run, the agent asks the user to provide credentials interactively.
On scheduled runs, the managed Chrome profile retains the session.

### Data Extraction Flow
```
Step 1: browser-navigate → goto the page with data
Step 2: browser-wait → wait for table/content to load
Step 3: browser-screenshot → capture before state
Step 4: browser-extract → read table or specific elements
Step 5: file-write → save extracted data to file
```

### Download Flow
```
Step 1: browser-navigate → goto the page with the download link
Step 2: browser-click → click the download/export button
Step 3: browser-wait → wait for download to complete
Step 4: file-read → verify the downloaded file
```

### Multi-Page Scraping
```
Step 1: browser-navigate → goto first page
Step 2: browser-extract → read data from page
Step 3: browser-click → click "Next" pagination link
Step 4: condition → check if more pages exist
Step 5: (loop back to Step 2 if true)
Step 6: data-merge → combine all extracted data
```

## Session Management

- OpenClaw manages a Chrome instance with persistent profiles
- Login sessions survive between scheduled runs
- If a session expires, the agent detects it (e.g., redirected to login page)
  and pauses the workflow with a notification to the user
- Cookies and local storage persist in the managed profile

## Timeout Defaults

| Action | Default Timeout |
|--------|----------------|
| Page navigation | 30 seconds |
| Element wait | 30 seconds |
| Click / fill | 10 seconds |
| Screenshot | 10 seconds |
| Full page read | 15 seconds |

Browser steps use a 120-second overall timeout (vs 60s for non-browser steps).

## Safety Rules

1. **No unnamed sites**: The agent only navigates to URLs the user explicitly provides
2. **No payment actions**: The agent refuses to fill payment forms or authorize transactions
3. **No CAPTCHA**: If a CAPTCHA appears, the agent pauses and notifies the user
4. **Screenshot audit trail**: Critical actions get before/after screenshots
5. **No credential storage**: Passwords are never written to files or logs
