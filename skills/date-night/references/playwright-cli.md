# Playwright CLI Command Reference

`playwright-cli` is Microsoft's CLI for AI browser automation — more token-efficient than raw Playwright or MCP because it keeps browser state external and returns only what's needed.

## Installation & PATH

```bash
# Already installed at:
~/.npm-global/bin/playwright-cli

# Ensure PATH in every exec call:
export PATH="$HOME/.npm-global/bin:$PATH"
```

## Key Concepts

### Element Refs
- `snapshot` returns compact YAML with element refs like `e8`, `e21`, `e47`
- Use these refs in `click`, `fill`, `hover`, `select`, etc.
- Refs are valid only until the next page navigation or major DOM change
- **Always snapshot before interacting** — stale refs will fail

### Sessions
- Default session persists cookies/storage in memory (lost on browser close)
- Use `-s=NAME` for named sessions to isolate different tasks
- Use `--persistent` to save profile to disk across browser restarts

## Core Commands

### Browser Lifecycle

```bash
# Open browser (headless by default)
playwright-cli open [url]

# Open in headed mode (visible browser window)
playwright-cli open "https://example.com" --headed

# Navigate to URL (in existing session)
playwright-cli goto "https://example.com"

# Close the page
playwright-cli close
```

### Page Inspection

```bash
# Capture page snapshot — returns YAML with element refs
playwright-cli snapshot

# Save snapshot to file
playwright-cli snapshot --filename=page.yaml

# Take screenshot (PNG)
playwright-cli screenshot

# Screenshot a specific element
playwright-cli screenshot e12

# Evaluate JavaScript on page
playwright-cli eval "document.title"

# Evaluate JS on a specific element
playwright-cli eval "el => el.textContent" e12
```

### Interaction

```bash
# Click an element by ref
playwright-cli click e12

# Right-click
playwright-cli click e12 right

# Double-click
playwright-cli dblclick e12

# Hover over element
playwright-cli hover e12

# Fill a text input (HANDLES REACT CONTROLLED INPUTS)
playwright-cli fill e15 "Hello World"

# Type text into focused/editable element (keystroke by keystroke)
playwright-cli type "Hello World"

# Select dropdown option
playwright-cli select e20 "option-value"

# Check / uncheck checkbox or radio
playwright-cli check e25
playwright-cli uncheck e25

# Upload file
playwright-cli upload "/path/to/file.pdf"

# Drag and drop
playwright-cli drag e10 e20
```

### Keyboard

```bash
# Press a single key
playwright-cli press Enter
playwright-cli press Tab
playwright-cli press Escape
playwright-cli press ArrowDown

# Press a digit (for verification codes in iframes)
playwright-cli press 7
playwright-cli press 1

# Key combinations
playwright-cli press Control+a
playwright-cli press Meta+c

# Key down / key up (for held keys)
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### Mouse (Low-Level)

```bash
playwright-cli mousemove 100 200    # move to coordinates
playwright-cli mousedown            # press left button
playwright-cli mouseup              # release left button
playwright-cli mousewheel 0 -300    # scroll down
playwright-cli mousewheel 0 300     # scroll up
```

### Navigation

```bash
playwright-cli go-back       # browser back
playwright-cli go-forward    # browser forward
playwright-cli reload        # refresh page
```

### Tabs

```bash
playwright-cli tab-list          # list all tabs
playwright-cli tab-new "url"     # open new tab
playwright-cli tab-select 1      # switch to tab by index
playwright-cli tab-close 2       # close tab by index
```

### Dialogs

```bash
playwright-cli dialog-accept              # accept alert/confirm
playwright-cli dialog-accept "response"   # accept prompt with text
playwright-cli dialog-dismiss             # dismiss/cancel dialog
```

### Window

```bash
playwright-cli resize 1280 720    # resize browser window
```

### Session Management

```bash
playwright-cli list          # list all sessions
playwright-cli close-all     # close all browsers gracefully
playwright-cli kill-all      # force-kill all browser processes

# Named sessions
playwright-cli -s=booking open "https://..." --headed
playwright-cli -s=booking snapshot
playwright-cli -s=booking click e12
playwright-cli -s=booking close
```

### Storage & State

```bash
# Save/load authentication state
playwright-cli state-save auth.json
playwright-cli state-load auth.json

# Cookies
playwright-cli cookie-list
playwright-cli cookie-get "session_id"
playwright-cli cookie-set "name" "value"
playwright-cli cookie-delete "name"
playwright-cli cookie-clear

# Local storage
playwright-cli localstorage-list
playwright-cli localstorage-get "key"
playwright-cli localstorage-set "key" "value"
playwright-cli localstorage-delete "key"
playwright-cli localstorage-clear

# Session storage (same pattern)
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get "key"
```

### Network

```bash
# Mock network requests
playwright-cli route "**/*.png" --status 404
playwright-cli route-list
playwright-cli unroute "**/*.png"

# List network requests since page load
playwright-cli network
```

### DevTools & Debugging

```bash
playwright-cli console          # list console messages
playwright-cli console warn     # filter by min level
playwright-cli show             # open visual dashboard
playwright-cli devtools-start   # open browser devtools

# Tracing
playwright-cli tracing-start
playwright-cli tracing-stop

# Video recording
playwright-cli video-start
playwright-cli video-stop
```

### PDF

```bash
playwright-cli pdf    # save current page as PDF
```

## Reservation-Specific Patterns

### Pattern: Fill React Form Fields

`fill` handles React controlled inputs natively — no need for the `nativeSetter` hack:

```bash
playwright-cli snapshot                         # get refs
playwright-cli fill e15 "{config.user_phone}"   # phone
playwright-cli fill e18 "{config.user_email}"   # email
playwright-cli fill e21 "{config.first_name}"   # first name
playwright-cli fill e24 "{config.last_name}"    # last name
```

### Pattern: Cross-Origin Iframe Input (Verification Codes)

Cannot `fill` or `click` inside cross-origin iframes. Use keyboard instead:

```bash
# Code is "714289"
playwright-cli press 7
playwright-cli press 1
playwright-cli press 4
playwright-cli press 2
playwright-cli press 8
playwright-cli press 9
```

### Pattern: Custom React Dropdowns (Occasion)

React dropdowns don't respond to `select`. Instead:

```bash
playwright-cli click e30          # click the dropdown to open it
playwright-cli snapshot           # see the options with refs
playwright-cli click e35          # click the desired option
```

### Pattern: Scroll to Find Elements

If elements are below the fold:

```bash
playwright-cli mousewheel 0 -500   # scroll down
playwright-cli snapshot             # re-snapshot to get new refs
```

### Pattern: Wait for Page Load

After navigation or clicking that triggers a page change:

```bash
playwright-cli click e12            # triggers navigation
# Brief pause to allow page load
playwright-cli snapshot             # will wait for stability before returning
```

## Tips

1. **Always snapshot before interacting** — refs go stale after DOM changes
2. **Use `fill` over `type`** — `fill` clears the field first and triggers React events
3. **Use `press` for iframe inputs** — only keyboard events cross iframe boundaries
4. **Use `--headed` for debugging** — see exactly what the browser sees
5. **Named sessions** prevent interference between concurrent automations
6. **`eval` is the escape hatch** — if snapshot doesn't show what you need, query the DOM directly
