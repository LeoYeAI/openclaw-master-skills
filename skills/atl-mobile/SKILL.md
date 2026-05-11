---
name: atl-browser
description: Mobile browser and native app automation via ATL (iOS Simulator). Navigate, click, screenshot, and automate web and native app tasks on iPhone/iPad simulators.
metadata:
  openclaw:
    emoji: "📱"
    requires:
      bins: ["xcrun", "xcodebuild", "curl"]
    install:
      - id: "atl-clone"
        kind: "shell"
        command: "git clone https://github.com/JordanCoin/Atl ~/Atl"
        label: "Clone ATL repository"
      - id: "atl-setup"
        kind: "shell" 
        command: "~/.openclaw/skills/atl-browser/scripts/setup.sh"
        label: "Build and install ATL to simulator"
---

# ATL — Agent Touch Layer

> The automation layer between AI agents and iOS

ATL provides HTTP-based automation for iOS Simulator — both **browser** (mobile Safari) and **native apps**. Think Playwright, but for mobile.

## 🔀 Two Servers: Browser & Native

ATL uses **two separate servers** for browser and native app automation:

| Server | Port | Use Case | Key Commands |
|--------|------|----------|--------------|
| **Browser** | `9222` | Web automation in mobile Safari | `goto`, `markElements`, `clickMark`, `evaluate` |
| **Native** | `9223` | iOS app automation (Settings, Contacts, any app) | `openApp`, `snapshot`, `tapRef`, `find` |

```
┌─────────────────────────────────────────────────────────────┐
│  BROWSER SERVER (9222)     │     NATIVE SERVER (9223)      │
│  (mobile Safari/WebView)   │     (iOS apps via XCTest)     │
│                            │                                │
│  markElements + clickMark  │     snapshot + tapRef         │
│  CSS selectors             │     accessibility tree        │
│  DOM evaluation            │     element references        │
│  tap, swipe, screenshot    │     tap, swipe, screenshot    │
└─────────────────────────────────────────────────────────────┘
```

**Why two ports?** Native app automation requires XCTest APIs (XCUIApplication, XCUIElement) which are only available in UI Test bundles. The native server runs as a UI Test that exposes an HTTP API.

### Starting the Servers

```bash
# Browser server (starts automatically with AtlBrowser app)
xcrun simctl launch booted com.atl.browser
curl http://localhost:9222/ping  # → {"status":"ok"}

# Native server (run as UI Test)
cd ~/Atl/core/AtlBrowser
xcodebuild test -workspace AtlBrowser.xcworkspace \
  -scheme AtlBrowser \
  -destination 'id=<SIMULATOR_UDID>' \
  -only-testing:AtlBrowserUITests/NativeServer/testNativeServer &
  
# Wait for it to start, then:
curl http://localhost:9223/ping  # → {"status":"ok","mode":"native"}
```

### Quick Port Reference

| Task | Port | Example |
|------|------|---------|
| Browse websites | 9222 | `curl localhost:9222/command -d '{"method":"goto",...}'` |
| Open native app | 9223 | `curl localhost:9223/command -d '{"method":"openApp",...}'` |
| Screenshot (browser) | 9222 | `curl localhost:9222/command -d '{"method":"screenshot"}'` |
| Screenshot (native) | 9223 | `curl localhost:9223/command -d '{"method":"screenshot"}'` |

---

## 📱 Native App Automation (Port 9223)

Native automation uses **port 9223** and automates **any iOS app** using the accessibility tree — no DOM, no JavaScript, just direct element interaction.

### Opening & Closing Apps

```bash
# Open an app by bundle ID
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"openApp","params":{"bundleId":"com.apple.Preferences"}}'
# → {"success":true,"result":{"bundleId":"com.apple.Preferences","mode":"native","state":"running"}}

# Check current app state
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"appState"}'
# → {"success":true,"result":{"mode":"native","bundleId":"com.apple.Preferences","state":"running"}}

# Close current app
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"closeApp"}'
# → {"success":true,"result":{"closed":true}}
```

### Common Bundle IDs

| App | Bundle ID |
|-----|-----------|
| Settings | `com.apple.Preferences` |
| Contacts | `com.apple.MobileAddressBook` |
| Calculator | `com.apple.calculator` |
| Calendar | `com.apple.mobilecal` |
| Photos | `com.apple.mobileslideshow` |
| Notes | `com.apple.mobilenotes` |
| Reminders | `com.apple.reminders` |
| Clock | `com.apple.mobiletimer` |
| Maps | `com.apple.Maps` |
| Safari | `com.apple.mobilesafari` |

### The `snapshot` Command

`snapshot` returns the accessibility tree — all visible elements with their properties and tap-able references.

```bash
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"snapshot","params":{"interactiveOnly":true}}' | jq '.result'
```

**Example output:**
```json
{
  "count": 12,
  "elements": [
    {
      "ref": "e0",
      "type": "cell",
      "label": "Wi-Fi",
      "value": "MyNetwork",
      "identifier": "",
      "x": 0,
      "y": 142,
      "width": 393,
      "height": 44,
      "isHittable": true,
      "isEnabled": true
    },
    {
      "ref": "e1",
      "type": "cell",
      "label": "Bluetooth",
      "value": "On",
      "identifier": "",
      "x": 0,
      "y": 186,
      "width": 393,
      "height": 44,
      "isHittable": true,
      "isEnabled": true
    },
    {
      "ref": "e2",
      "type": "button",
      "label": "Back",
      "value": null,
      "identifier": "Back",
      "x": 0,
      "y": 44,
      "width": 80,
      "height": 44,
      "isHittable": true,
      "isEnabled": true
    }
  ]
}
```

**Parameters:**
- `interactiveOnly` (bool, default: `false`) — Only return hittable elements
- `maxDepth` (int, optional) — Limit tree traversal depth

### The `tapRef` Command

Tap an element by its reference from the last `snapshot`:

```bash
# Take snapshot first
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"snapshot","params":{"interactiveOnly":true}}'

# Tap element e0 (Wi-Fi cell from example above)
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"tapRef","params":{"ref":"e0"}}'
# → {"success":true}
```

### The `find` Command

Find and interact with elements by text — no need to parse snapshot manually:

```bash
# Find and tap "Wi-Fi"
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"find","params":{"text":"Wi-Fi","action":"tap"}}'
# → {"success":true,"result":{"found":true,"ref":"e0"}}

# Check if an element exists
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"find","params":{"text":"Bluetooth","action":"exists"}}'
# → {"success":true,"result":{"found":true,"ref":"e1"}}

# Find and fill a text field
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"find","params":{"text":"First name","action":"fill","value":"John"}}'

# Get element info without interacting
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"find","params":{"text":"Cancel","action":"get"}}'
# → {"success":true,"result":{"found":true,"ref":"e5","element":{...}}}
```

**Parameters:**
- `text` (string) — Text to search for (matches label, value, or identifier)
- `action` (string) — One of: `tap`, `fill`, `exists`, `get`
- `value` (string, optional) — Text to fill (required for `action:"fill"`)
- `by` (string, optional) — Narrow search: `label`, `value`, `identifier`, `type`, or `any` (default)

---

## 🔄 Native App Workflow Example

Here's a complete flow: open Settings, navigate to Wi-Fi, take a screenshot:

```bash
# 1. Open Settings app
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"openApp","params":{"bundleId":"com.apple.Preferences"}}'

# 2. Wait for app to launch
sleep 1

# 3. Take snapshot to see available elements
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"snapshot","params":{"interactiveOnly":true}}' | jq '.result.elements[:5]'

# 4. Find and tap Wi-Fi
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"find","params":{"text":"Wi-Fi","action":"tap"}}'

# 5. Wait for navigation
sleep 0.5

# 6. Take screenshot of Wi-Fi settings
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"screenshot"}' | jq -r '.result.data' | base64 -d > /tmp/wifi-settings.png

# 7. Navigate back (swipe right from left edge)
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"swipe","params":{"direction":"right"}}'

# 8. Close the app
curl -s -X POST http://localhost:9223/command \
  -d '{"method":"closeApp"}'
```

### Helper Script Version

```bash
source ~/.openclaw/skills/atl-browser/scripts/atl-helper.sh

atl_openapp "com.apple.Preferences"
sleep 1
atl_find "Wi-Fi" tap
sleep 0.5
atl_screenshot /tmp/wifi-settings.png
atl_swipe right
atl_closeapp
```

---

## 💡 Core Insight: Vision-Free Automation

ATL's killer feature is **spatial understanding without vision models**:

```
┌─────────────────────────────────────────────────────────────┐
│  markElements + captureForVision = COMPLETE PAGE KNOWLEDGE  │
└─────────────────────────────────────────────────────────────┘

1. markElements  → Numbers every interactive element [1] [2] [3]
2. captureForVision → PDF with text layer + element coordinates
3. tap x=234 y=567 → Pixel-perfect touch at exact position
```

**Why this matters:**
- **No vision API calls** — zero token cost for "seeing" the page
- **Faster** — no round-trip to GPT-4V/Claude Vision
- **Deterministic** — same page = same coordinates, every time
- **Reliable** — pixel-perfect coordinates vs. vision interpretation

### The Vision-Free Workflow

```bash
# 1. Mark elements (adds numbered labels + stores coordinates)
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"1","method":"markElements","params":{}}'

# 2. Capture PDF with text layer (machine-readable, has coordinates)
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"2","method":"captureForVision","params":{"savePath":"/tmp","name":"page"}}' \
  | jq -r '.result.path'
# → /tmp/page.pdf (text-selectable, contains element positions)

# 3. Get specific element's position by mark label
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"3","method":"getMarkInfo","params":{"label":5}}' | jq '.result'
# → {"label":5, "tag":"button", "text":"Add to Cart", "x":187, "y":432, "width":120, "height":44}

# 4. Tap at exact coordinates
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"4","method":"tap","params":{"x":187,"y":432}}'
```

**The marks tell you WHERE everything is. The PDF tells you WHAT everything says. Together = full page understanding.**

## 🎯 The Escalation Ladder

When automation gets stuck, escalate through these levels:

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1: COORDINATES (fast, cheap, no API calls)          │
│  markElements → getMarkInfo → tap x,y                      │
│                                                             │
│  ↓ If stuck after 2-3 tries...                             │
│                                                             │
│  Level 2: VISION FALLBACK (screenshot to understand state) │
│  screenshot → analyze UI → identify blockers (modals, etc) │
│                                                             │
│  ↓ If still stuck...                                       │
│                                                             │
│  Level 3: JS INJECTION (direct DOM manipulation)           │
│  evaluate → dispatchEvent → force interactions             │
└─────────────────────────────────────────────────────────────┘
```

### When to Escalate

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| Tap succeeds but nothing changes | Modal/overlay opened | Screenshot → find new button |
| Cart count doesn't update | Site needs login or has bot detection | Try JS click with events |
| Element not found after scroll | Marks are page-relative, not viewport | Use `getBoundingClientRect` via evaluate |
| Same error 3+ times | UI state changed unexpectedly | Screenshot to see actual state |

### Real-World Pattern: E-commerce Checkout

```bash
# 1. Search and find product
atl_goto "https://store.com/search?q=headphones"
atl_mark

# 2. First, dismiss any modals/banners (ALWAYS DO THIS)
# Look for: close, dismiss, continue, accept, no thanks, got it
CLOSE=$(atl_find "close")
[ -n "$CLOSE" ] && atl_click $CLOSE

# 3. Find and click Add to Cart
ATC=$(atl_find "Add to cart")
atl_click $ATC

# 4. Wait, then CHECK if it worked
sleep 2
atl_screenshot /tmp/after-click.png

# 5. If cart didn't update, LOOK at the screenshot
# Maybe a "Choose options" modal opened - find the NEW Add to Cart button
# This is the vision fallback - you need to SEE what happened
```

### Key Insight: Modals Change Everything

When you click "Add to cart" on sites like Target, Amazon, etc., they often:
1. Open a "Choose options" modal (size, color, quantity)
2. Show an upsell (protection plans, accessories)
3. Display a confirmation with "View cart" or "Continue shopping"

**Your original tap WORKED** — you just can't see the result without a screenshot.

## 🚀 Quick Start (30 seconds)

```bash
# 1. Setup (boots sim, installs ATL)
~/.openclaw/skills/atl-browser/scripts/setup.sh

# 2. Navigate somewhere
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"1","method":"goto","params":{"url":"https://example.com"}}'

# 3. Mark elements (shows [1], [2], [3] labels)
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"2","method":"markElements","params":{}}'

# 4. Take screenshot
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"3","method":"screenshot","params":{}}' | jq -r '.result.data' | base64 -d > /tmp/page.png

# 5. Click element [1]
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"4","method":"clickMark","params":{"label":1}}'
```

**Or use the helper functions:**
```bash
source ~/.openclaw/skills/atl-browser/scripts/atl-helper.sh
atl_goto "https://example.com"
atl_mark
atl_screenshot /tmp/page.png
atl_click 1
```

## Quick Reference

**Base URL:** `http://localhost:9222`

### Common Commands

```bash
# Check if ATL is running
curl -s http://localhost:9222/ping

# Navigate to URL
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"1","method":"goto","params":{"url":"https://example.com"}}'

# Wait for page ready
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"2","method":"waitForReady","params":{"timeout":10}}'

# Take screenshot (returns base64 PNG)
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"3","method":"screenshot","params":{}}' | jq -r '.result.data' | base64 -d > screenshot.png

# Mark interactive elements (shows numbered labels)
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"4","method":"markElements","params":{}}'

# Click by mark label
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"5","method":"clickMark","params":{"label":3}}'

# Scroll page
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"6","method":"evaluate","params":{"script":"window.scrollBy(0, 500)"}}'

# Type text
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"7","method":"type","params":{"text":"Hello world"}}'

# Click by CSS selector
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"8","method":"click","params":{"selector":"button.submit"}}'
```

## Setup (First Time)

### 1. Start Simulator
```bash
# Boot iPhone 17 simulator (or another device)
xcrun simctl boot "iPhone 17"

# Open Simulator app
open -a Simulator
```

### 2. Build & Install AtlBrowser
```bash
cd ~/Atl/core/AtlBrowser

# Build for simulator (RECOMMENDED: target by UDID)
# Why: name-based destinations can cause Xcode to pick an older iOS runtime (15/16)
# and fail if AtlBrowser has an iOS 17+ deployment target.
#
# 1) Find a suitable simulator UDID (iOS 17+):
#   xcrun simctl list devices available
#
# 2) Build targeting that UDID:
xcodebuild -workspace AtlBrowser.xcworkspace \
  -scheme AtlBrowser \
  -destination 'id=<SIM_UDID>' \
  -derivedDataPath /tmp/atl-dd \
  build

# Install to a specific simulator (preferred)
xcrun simctl install <SIM_UDID> \
  /tmp/atl-dd/Build/Products/Debug-iphonesimulator/AtlBrowser.app

# Launch the app
xcrun simctl launch <SIM_UDID> com.atl.browser
```

### 3. Verify Server
```bash
curl -s http://localhost:9222/ping
# Should return: {"status":"ok"}
```

## All Available Methods

### App Control (Native Mode)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `openApp` | `{bundleId}` | Any→Native | Open app, switch to native mode |
| `closeApp` | - | Native | Close current app, return to browser mode |
| `appState` | - | Any | Get current mode and bundleId |
| `openBrowser` | - | Native→Browser | Switch back to browser mode |

### Native Accessibility
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `snapshot` | `{interactiveOnly?, maxDepth?}` | Native | Get accessibility tree |
| `tapRef` | `{ref}` | Native | Tap element by ref (e.g., "e0") |
| `find` | `{text, action, value?, by?}` | Native | Find element and interact |
| `fillRef` | `{ref, text}` | Native | Tap element and type text |
| `focusRef` | `{ref}` | Native | Focus element without typing |

### Navigation (Browser)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `goto` | `{url}` | Browser | Navigate to URL |
| `reload` | - | Browser | Reload page |
| `goBack` | - | Browser | Go back |
| `goForward` | - | Browser | Go forward |
| `getURL` | - | Browser | Get current URL |
| `getTitle` | - | Browser | Get page title |

### Interactions (Browser)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `click` | `{selector}` | Browser | Click element |
| `doubleClick` | `{selector}` | Browser | Double-click |
| `type` | `{text}` | Both | Type text |
| `fill` | `{selector, value}` | Browser | Fill input field |
| `press` | `{key}` | Both | Press key |
| `hover` | `{selector}` | Browser | Hover over element |
| `scrollIntoView` | `{selector}` | Browser | Scroll to element |

### Mark System (Browser)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `markElements` | - | Browser | Mark visible interactive elements |
| `markAll` | - | Browser | Mark ALL interactive elements |
| `unmarkElements` | - | Browser | Remove marks |
| `clickMark` | `{label}` | Browser | Click by label number |
| `getMarkInfo` | `{label}` | Browser | Get element info by label |

### Screenshots & Capture
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `screenshot` | `{fullPage?, selector?}` | Both | Take screenshot |
| `captureForVision` | `{savePath?, name?}` | Browser | Full page PDF |
| `captureJPEG` | `{quality?, fullPage?}` | Both | JPEG capture |
| `captureLight` | - | Browser | Text + interactives only |

### Waiting (Browser)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `waitForSelector` | `{selector, timeout?}` | Browser | Wait for element |
| `waitForNavigation` | - | Browser | Wait for navigation |
| `waitForReady` | `{timeout?, stabilityMs?}` | Browser | Wait for page ready |
| `waitForAny` | `{selectors, timeout?}` | Browser | Wait for any selector |

### JavaScript (Browser)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `evaluate` | `{script}` | Browser | Run JavaScript |
| `querySelector` | `{selector}` | Browser | Find element |
| `querySelectorAll` | `{selector}` | Browser | Find all elements |
| `getDOMSnapshot` | - | Browser | Get page HTML |

### Cookies (Browser)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `getCookies` | - | Browser | Get all cookies |
| `setCookies` | `{cookies}` | Browser | Set cookies |
| `deleteCookies` | - | Browser | Delete all cookies |

### Touch Gestures (Both Modes)
| Method | Params | Mode | Description |
|--------|--------|------|-------------|
| `tap` | `{x, y}` | Both | Tap at coordinates |
| `longPress` | `{x, y, duration?}` | Both | Long press (default 0.5s) |
| `swipe` | `{direction}` | Both | Swipe up/down/left/right |
| `swipe` | `{fromX, fromY, toX, toY}` | Both | Swipe between points |
| `pinch` | `{scale, duration?}` | Both | Pinch zoom (scale > 1 = zoom in) |

#### Swipe Examples

```bash
# Swipe up (scroll down)
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"1","method":"swipe","params":{"direction":"up"}}'

# Swipe left (next page in carousel)
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"2","method":"swipe","params":{"direction":"left","distance":400}}'

# Custom swipe path
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"3","method":"swipe","params":{"fromX":200,"fromY":600,"toX":200,"toY":200}}'

# Long press for context menu
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"4","method":"longPress","params":{"x":150,"y":300,"duration":1.0}}'

# Pinch to zoom in
curl -s -X POST http://localhost:9222/command \
  -d '{"id":"5","method":"pinch","params":{"scale":2.0}}'
```

## Typical Workflow

```bash
# 1. Navigate to site
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"1","method":"goto","params":{"url":"https://www.apple.com/shop"}}'

# 2. Wait for page to load
sleep 2
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"2","method":"waitForReady","params":{"timeout":10}}'

# 3. Mark elements to see what's clickable
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"3","method":"markElements","params":{}}'

# 4. Take screenshot to see the marks
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"4","method":"screenshot","params":{}}' | jq -r '.result.data' | base64 -d > /tmp/page.png

# 5. Click a marked element (e.g., label 14)
curl -s -X POST http://localhost:9222/command \
  -H "Content-Type: application/json" \
  -d '{"id":"5","method":"clickMark","params":{"label":14}}'

# 6. Repeat as needed
```

## Troubleshooting

### Navigation not working (goto returns success but page doesn't change)
Known issue: `goto` command may return success without navigating. Use JS workaround:
```bash
# Instead of goto, use evaluate to navigate
curl -s -X POST http://localhost:9222/command -H "Content-Type: application/json" \
  -d '{"id":"1","method":"evaluate","params":{"script":"location.href = \"https://example.com\"; true"}}'

# Wait for page load
sleep 3
curl -s -X POST http://localhost:9222/command -H "Content-Type: application/json" \
  -d '{"id":"2","method":"waitForReady","params":{"timeout":10}}'
```

### Server not responding
```bash
# Check if app is running
xcrun simctl listapps booted | grep atl

# Restart the app
xcrun simctl terminate booted com.atl.browser
xcrun simctl launch booted com.atl.browser

# Check logs
xcrun simctl spawn booted log show --predicate 'process == "AtlBrowser"' --last 1m
```

### Need to rebuild (iOS version changes)
```bash
cd ~/Atl/core/AtlBrowser
xcodebuild -workspace AtlBrowser.xcworkspace -scheme AtlBrowser -sdk iphonesimulator build
xcrun simctl install booted ~/Library/Developer/Xcode/DerivedData/AtlBrowser-*/Build/Products/Debug-iphonesimulator/AtlBrowser.app
xcrun simctl launch booted com.atl.browser
```

### Port 9222 in use
The ATL server runs inside the simulator app. If port 9222 is blocked, check for other processes:
```bash
lsof -i :9222
```

## Best Practices

### 1. Clean UI Before Acting
Real users dismiss popups. You should too.
```bash
# Before any workflow, check for and dismiss:
# - Cookie consent banners
# - Newsletter popups  
# - Health/privacy consent modals
# - "Download our app" prompts
atl_mark
for KEYWORD in "close" "dismiss" "no thanks" "accept" "got it" "continue"; do
  LABEL=$(atl_find "$KEYWORD")
  [ -n "$LABEL" ] && atl_click $LABEL && sleep 1
done
```

### 2. Verify State After Actions
Don't assume — confirm.
```bash
atl_click $ADD_TO_CART
sleep 2
# Check if cart updated
CART=$(atl_find "cart [1-9]")
if [ -z "$CART" ]; then
  # Didn't work - take screenshot to see why
  atl_screenshot /tmp/debug.png
  echo "Action may have opened a modal - check screenshot"
fi
```

### 3. Use Viewport Coordinates for Taps
Marks give page-relative coordinates. For tap to work, the element must be visible.
```bash
# Option A: Scroll element into view first
curl -s -X POST http://localhost:9222/command -H "Content-Type: application/json" \
  -d '{"id":"1","method":"evaluate","params":{"script":"document.querySelector(\"#my-button\").scrollIntoView()"}}'

# Option B: Get viewport-relative coords via JS
curl -s -X POST http://localhost:9222/command -H "Content-Type: application/json" \
  -d '{"id":"2","method":"evaluate","params":{"script":"var r = document.querySelector(\"#my-button\").getBoundingClientRect(); JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2})"}}'
```

### 4. Screenshot is Your Debugging Superpower
When in doubt, look.
```bash
atl_screenshot /tmp/current-state.png
# Then analyze with vision or just open the file
```

## Notes

- ATL runs inside the iOS Simulator, sharing the host's network
- Port 9222 is the default (matches Chrome DevTools Protocol convention)
- The mark system shows red numbered labels on interactive elements
- Screenshots are PNG base64-encoded; use `base64 -d` to decode
- iOS 26+ compatible (fixed NWListener binding issue)

## Requirements

- **macOS** with Xcode installed
- **iOS Simulator** (comes with Xcode)
- That's it!

## Examples

See `examples/` folder:
- `test-browse.sh` - Quick bash test workflow

## API Reference

For machine-readable API spec, see [openapi.yaml](../api/openapi.yaml) — includes all commands, parameters, and response schemas.

## Source

- GitHub: https://github.com/JordanCoin/Atl
- Author: [@JordanCoin](https://github.com/JordanCoin)
