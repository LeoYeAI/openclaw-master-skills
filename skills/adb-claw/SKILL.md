---
name: adb-claw
version: 1.6.1
description: "Your eyes, hands, and ears on Android. See the screen (screenshot + indexed UI tree), interact (tap, swipe, scroll, type, clear-field), navigate via deep links (bypass CJK text input limits), wait for UI state changes instead of polling, monitor live UI text via accessibility framework (works during video playback), capture system audio (Android 11+, WAV stream for piping to ASR tools), manage full app lifecycle (install/uninstall/clear), control screen (on/off/unlock/rotation), run shell commands, and transfer files. Agent-optimized: structured JSON output, indexed element targeting, and App Profiles with pre-built deep links and layouts for popular apps."
homepage: https://github.com/llm-net/adb-claw
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "version": "1.6.1",
        "os": ["darwin", "linux"],
        "tags": ["android", "adb", "mobile", "automation", "ui-testing", "device-control", "deep-link", "screenshot", "accessibility", "monitoring"],
        "requires": { "bins": ["adb-claw", "adb"] },
        "install":
          [
            {
              "id": "adb-claw-darwin-arm64",
              "kind": "download",
              "url": "https://github.com/llm-net/adb-claw/releases/latest/download/adb-claw-darwin-arm64",
              "bins": ["adb-claw"],
              "os": "darwin",
              "label": "Download adb-claw (macOS Apple Silicon)",
            },
            {
              "id": "adb-claw-darwin-amd64",
              "kind": "download",
              "url": "https://github.com/llm-net/adb-claw/releases/latest/download/adb-claw-darwin-amd64",
              "bins": ["adb-claw"],
              "os": "darwin",
              "label": "Download adb-claw (macOS Intel)",
            },
            {
              "id": "adb-claw-linux-amd64",
              "kind": "download",
              "url": "https://github.com/llm-net/adb-claw/releases/latest/download/adb-claw-linux-amd64",
              "bins": ["adb-claw"],
              "os": "linux",
              "label": "Download adb-claw (Linux x86_64)",
            },
            {
              "id": "adb-claw-linux-arm64",
              "kind": "download",
              "url": "https://github.com/llm-net/adb-claw/releases/latest/download/adb-claw-linux-arm64",
              "bins": ["adb-claw"],
              "os": "linux",
              "label": "Download adb-claw (Linux ARM64)",
            },
            {
              "id": "adb-brew",
              "kind": "brew",
              "formula": "android-platform-tools",
              "bins": ["adb"],
              "label": "Install ADB (brew)",
            },
          ],
      },
  }
---

# ADB Claw — Android Device Control

Your eyes, hands, and ears on Android. See what's on screen, tap any element, scroll through content, open deep links, wait for UI changes, capture system audio, manage apps, and more — all through a single CLI with structured JSON output.

## Why ADB Claw

**Superpowers — What You Can't Get Elsewhere:**
- **Live stream intelligence** — `monitor` connects to Android's accessibility framework, reading all UI text in real-time — even during video playback and live streams where `uiautomator dump` hangs. Chat messages, captions, dynamic overlays — data no other tool exposes to agents.
- **System audio capture** — `audio capture` records device audio via REMOTE_SUBMIX (Android 11+); streams WAV to stdout for piping to ASR tools. Combined with `monitor`, you get full sensory coverage: visual text + audio.

**Core Strengths:**
- **Observe → Act → Verify loop** — `observe` returns screenshot + indexed UI tree in one call; use element indices to target precisely across any screen size
- **Deep links bypass CJK limits** — `adb input text` can't type Chinese/Japanese/Korean; `adb-claw open 'app://search?keyword=中文'` can
- **Wait, don't poll** — `wait --text "Done"` blocks until the UI element appears, replacing fragile sleep/observe loops
- **Smart scroll** — auto-calculates swipe coordinates from screen size; supports direction, page count, and scrolling within specific elements
- **App Profiles** — pre-built knowledge (deep links, layouts, known issues) for popular apps like Douyin; load once, skip trial-and-error
- **Full app lifecycle** — install, launch, stop, uninstall, clear data — no raw `adb` needed
- **Agent-optimized JSON** — every command returns `{ok, command, data, error, duration_ms}` with actionable `suggestion` on errors
- **Minimal device footprint** — nearly all operations are pure ADB commands; only `monitor` and `audio capture` push temporary ~7KB helpers that auto-exit

**Actively Evolving** — new capabilities ship regularly. Each release expands what you can perceive and control on Android devices.

## Getting Started

### Claude Code

Install the plugin, then just talk to Claude — no slash commands needed:

```bash
claude plugin add llm-net/adb-claw
```

The plugin auto-downloads the adb-claw binary on first session. Make sure `adb` is installed and a device is connected via USB with debugging enabled.

Then simply ask Claude to interact with your Android device:

```
"Take a screenshot of my phone"
"Open Douyin and search for 猫咪"
"Tap the Login button"
"Monitor the live stream chat for 30 seconds"
```

Claude reads the Triggers list below and automatically activates this skill when your message matches — no explicit invocation required.

### OpenClaw

Install from ClawHub:

```bash
claw install adb-claw
```

Same natural-language triggers apply. Ask your agent to control an Android device and it will invoke adb-claw commands.

## Triggers

These patterns tell the agent when to activate this skill:

- User asks to control, interact with, or automate an Android device
- User asks to test a mobile app or UI on Android
- User mentions tapping, swiping, scrolling, screenshots, or app management on Android
- User wants to open a URL, deep link, or specific app screen on a connected device
- User wants to wait for UI elements to appear/disappear on Android
- User wants to manage screen state (on/off/unlock/rotation) on Android
- User wants to push/pull files to/from an Android device
- User wants to monitor live stream chat or read UI text during video playback on Android
- User wants to capture or record audio from an Android device
- User wants to grab shopping cart products from a Douyin live stream
- User wants to run shell commands on an Android device

## Binary

The adb-claw binary is located at `${CLAUDE_PLUGIN_ROOT}/bin/adb-claw`.

The binary is installed automatically via the SessionStart hook. If `adb-claw` is not available, inform the user that the plugin needs to be reinstalled — do not attempt to download or install it yourself.

## Setup

Requires two binaries:

1. **adb-claw** — the control CLI
2. **adb** — Android Debug Bridge (from Android SDK Platform-Tools)

### Install adb-claw

Installed automatically by the plugin. For manual installation, see [GitHub Releases](https://github.com/llm-net/adb-claw/releases).

### Install adb

```bash
# macOS
brew install android-platform-tools

# Linux (Debian/Ubuntu)
sudo apt install android-tools-adb
```

### Connect device

**The Android device must have USB debugging enabled and be connected via USB.** This is the most common blocker — most users haven't turned it on. When a user first asks to control their phone, **always check connection first** (`adb-claw doctor`) and if it fails, **walk them through the setup steps below** before attempting any other commands.

#### How to enable USB debugging (guide the user through this)

1. **Open Settings** on the Android phone
2. Go to **About phone** (some phones: Settings → My device)
3. Tap **Build number** (or MIUI version) **7 times** — a toast confirming Developer Mode is enabled will appear
4. Go back to **Settings → Additional settings → Developer options** (path varies by brand):
   - Xiaomi/Redmi: Settings → Additional settings → Developer options
   - Samsung: Settings → Developer options
   - Pixel/Stock: Settings → System → Developer options
   - OPPO/Vivo: Settings → System management → Developer options
5. Enable **USB debugging** toggle
6. Connect phone to computer via USB cable
7. A dialog "Allow USB debugging?" will appear on the phone — tap **Allow** (check "Always allow from this computer" for convenience)

#### Verify connection

```bash
adb-claw doctor    # Checks adb, device connection, and capabilities
```

If `doctor` reports no device, ask the user to:
- Check the USB cable (some cables are charge-only, no data)
- Try a different USB port
- Re-authorize USB debugging on the phone (revoke and re-allow)
- On some phones, change USB mode from "Charging" to "File Transfer" in the notification shade

## Quick Start

The core loop is **observe → decide → act → observe**:

```bash
# 1. See what's on screen
adb-claw observe --width 540

# 2. Act on what you see (use element index from observe output)
adb-claw tap --index 3

# 3. Verify the result
adb-claw observe --width 540
```

For CJK apps, use deep links to bypass text input limits:

```bash
# Search in Douyin (Chinese TikTok) — no manual typing needed
adb-claw open 'snssdk1128://search/result?keyword=猫咪'

# Wait for results to load
adb-claw wait --text "综合" --timeout 5000
```

## App Profiles

App Profiles are pre-built knowledge bases for specific apps — deep links, UI layouts, device-specific behavior, and known issues. They dramatically reduce the trial-and-error needed to automate an app.

**Available Profiles**: `skills/apps/` directory

| App | File | Key Content |
|-----|------|-------------|
| Douyin (抖音) | `douyin.md` | Search/user/live deep links, feed/search/profile layouts, Phone vs Pad differences, live stream chat monitoring |
| Meituan (美团) | `meituan.md` | Search/waimai deep links, homepage/menu/search layouts, WebView workarounds, popup chain handling |

**Usage**:
1. `adb-claw app current` → get foreground app package name
2. Check `skills/apps/` for a matching Profile
3. Has Profile → use deep links and known layouts (fast path)
4. No Profile → `observe` + explore (slow path)
5. Check device form factor: `adb-claw device info` → short edge < 1200px = Phone, >= 1200px = Pad

Profiles are plain Markdown files. New app support = drop a `.md` file into `skills/apps/`.

## Global Flags

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--serial` | `-s` | Target device serial (when multiple devices connected) | auto-detect |
| `--output` | `-o` | Output format: `json`, `text`, `quiet` | `json` |
| `--timeout` | | Command timeout in milliseconds | `30000` |
| `--verbose` | | Enable debug output to stderr | `false` |

## Commands

### observe — Screenshot + UI Tree (Primary Command)

Captures screenshot and UI element tree in one call. **Always use this before and after actions.**

```bash
adb-claw observe              # Default
adb-claw observe --width 540  # Scale screenshot width
```

Returns: base64 PNG screenshot, indexed UI elements with text/id/bounds/center coordinates.

### screenshot — Capture Screen

```bash
adb-claw screenshot                      # Returns base64 PNG in JSON
adb-claw screenshot -f output.png        # Save to file
adb-claw screenshot --width 540          # Scale down
```

### tap — Tap UI Element

Tap by element index (preferred), resource ID, text, or coordinates:

```bash
adb-claw tap --index 5            # Tap element #5 from observe output
adb-claw tap --id "com.app:id/btn" # Tap by resource ID
adb-claw tap --text "Submit"       # Tap by visible text
adb-claw tap 540 960              # Tap coordinates (x y)
```

**Always prefer `--index` over coordinates.** Index values come from `observe` output.

### long-press — Long Press

```bash
adb-claw long-press 540 960              # Default duration
adb-claw long-press 540 960 --duration 2000  # 2 seconds
```

### swipe — Swipe Gesture

```bash
adb-claw swipe 540 1800 540 600           # Swipe up (scroll down)
adb-claw swipe 540 600 540 1800           # Swipe down (scroll up)
adb-claw swipe 900 960 100 960            # Swipe left
adb-claw swipe 540 1800 540 600 --duration 500  # Slow swipe
```

### type — Input Text (ASCII only)

```bash
adb-claw type "Hello world"
```

**Important**: Only ASCII text is supported. For CJK/emoji input, use `open` with deep links (e.g., `adb-claw open 'myapp://search?keyword=中文'`).

### key — Press System Key

```bash
adb-claw key HOME        # Home screen
adb-claw key BACK        # Navigate back
adb-claw key ENTER       # Confirm / submit
adb-claw key TAB         # Next field
adb-claw key DEL         # Delete character
adb-claw key POWER       # Power button
adb-claw key VOLUME_UP   # Volume up
adb-claw key VOLUME_DOWN # Volume down
adb-claw key PASTE       # Paste from clipboard
adb-claw key COPY        # Copy selection
adb-claw key CUT         # Cut selection
adb-claw key WAKEUP      # Wake screen
adb-claw key SLEEP       # Sleep screen
```

### clear-field — Clear Input Field

Clear text in the currently focused input field. Optionally tap an element first to focus it.

```bash
adb-claw clear-field                   # Clear focused field
adb-claw clear-field --index 5         # Focus element #5 then clear
adb-claw clear-field --id "input_name" # Focus by resource ID then clear
adb-claw clear-field --text "Username" # Focus by text then clear
```

Uses Ctrl+A+DEL on SDK 31+, falls back to repeated DEL on older devices.

### open — Open URI (Deep Link)

Open any URI using Android's ACTION_VIEW intent. The key to CJK text input — pass Chinese/Japanese/Korean text as URL parameters in deep links.

```bash
adb-claw open https://www.google.com
adb-claw open myapp://path/to/screen
adb-claw open "market://details?id=com.example"
adb-claw open "snssdk1128://search/result?keyword=猫咪"   # Douyin search in Chinese
```

### scroll — Smart Scroll

Scroll the screen or a specific scrollable element. Auto-calculates swipe coordinates from screen size — no manual coordinate math needed.

```bash
adb-claw scroll down                  # Scroll down one page
adb-claw scroll up                    # Scroll up one page
adb-claw scroll down --pages 3        # Scroll down 3 pages
adb-claw scroll down --index 5        # Scroll within element #5
adb-claw scroll left --distance 500   # Scroll left 500 pixels
```

**Always prefer `scroll` over manual `swipe` for page navigation.**

### wait — Wait for UI Condition

Wait for a UI element or activity to appear or disappear. Replaces fragile sleep+observe polling loops with a single blocking call.

```bash
adb-claw wait --text "Login"                 # Wait for text to appear
adb-claw wait --id "btn_submit"              # Wait for element by ID
adb-claw wait --text "Loading" --gone        # Wait for text to disappear
adb-claw wait --activity ".MainActivity"     # Wait for activity
adb-claw wait --text "Done" --timeout 20000  # Custom timeout (20s)
```

Default timeout: 10s. Default poll interval: 800ms.

### screen — Screen Management

```bash
adb-claw screen status               # Display on/off, locked, rotation
adb-claw screen on                   # Wake up screen
adb-claw screen off                  # Turn off screen
adb-claw screen unlock               # Wake + swipe unlock (no password)
adb-claw screen rotation auto        # Enable auto-rotation
adb-claw screen rotation 0           # Portrait
adb-claw screen rotation 1           # Landscape
```

### app — App Management

```bash
adb-claw app list         # Third-party apps
adb-claw app list --all   # Include system apps
adb-claw app current      # Current foreground app
adb-claw app launch <pkg> # Launch app by package name
adb-claw app stop <pkg>   # Force stop app
adb-claw app install <apk> [--replace]  # Install APK
adb-claw app uninstall <pkg>            # Uninstall app
adb-claw app clear <pkg>               # Clear app data/cache
```

### monitor — Continuous UI Text Monitoring

Monitor UI text by connecting directly to the Android accessibility framework. Unlike `ui tree` which uses `uiautomator dump`, this command skips video surface nodes and works reliably during live streams and video playback.

```bash
adb-claw monitor                            # 10s bounded, returns JSON envelope
adb-claw monitor --duration 30000           # 30s bounded
adb-claw monitor --stream --duration 60000  # 60s streaming, JSON lines
adb-claw monitor --interval 1000            # Faster polling (1s)
```

**Bounded mode** (default): runs for `--duration` ms, returns all unique text entries in a JSON envelope.

**Streaming mode** (`--stream`): outputs each new text as a JSON line in real time.

Default duration: 10s. Default poll interval: 2s.

Note: This command pushes a small (~7KB) DEX helper to the device on first use. The helper runs temporarily via `app_process` and exits when monitoring completes.

### audio capture — System Audio Capture (Android 11+)

Capture system audio via REMOTE_SUBMIX. Streams WAV (16kHz mono 16-bit PCM) to stdout for piping to external tools, or saves to a file.

**WARNING**: Device speakers are muted while capturing.

```bash
adb-claw audio capture                            # Stream WAV to stdout (10s)
adb-claw audio capture --duration 30000           # Stream 30s
adb-claw audio capture --duration 0               # Stream until killed (Ctrl+C)
adb-claw audio capture --file recording.wav       # Save to file, returns JSON envelope
adb-claw audio capture --rate 44100               # Custom sample rate
```

**Stream mode** (default): outputs WAV to stdout — designed for piping:

```bash
adb-claw audio capture --stream --duration 30000 | asrclaw transcribe --stream --lang zh
```

**File mode** (`--file`): saves to local file and returns JSON envelope with file path, byte count, and duration.

Default duration: 10s. Default sample rate: 16000 Hz.

Requires Android 11+ (API 30). Like `monitor`, this command pushes a small DEX helper to the device on first use.

**When to use audio capture vs monitor**:
- `monitor` — read UI text (chat messages, labels, captions) as structured data
- `audio capture` — record what's being heard (speech, music, sound effects) as audio

For live streams, they complement each other: `monitor` captures on-screen chat text while `audio capture` captures the streamer's voice.

### live cart — Douyin Shopping Cart Capture (抖音小黄车)

Grab product information from a Douyin live stream shopping cart. Captures the currently explaining product (without opening the cart) and the first N products in the cart list.

This command is **Douyin-specific** — it relies on Douyin's UI patterns and accessibility node structure.

```bash
adb-claw live cart              # Top 10 products + explaining product
adb-claw live cart --count 5    # Top 5 products
adb-claw live cart --count 20   # Top 20 products
```

**How it works**:
1. Reads the "讲解中" floating card via accessibility (no cart open needed)
2. Taps the shopping cart button to open the panel
3. Scrolls slowly through products with continuous accessibility polling
4. Stops when products 1..N are all captured (consecutive, no gaps)
5. Closes the cart and outputs structured JSON

Returns: product number, title, price, sold count, shop name, tags for each product, plus the currently explaining product if any.

**Must be used while viewing a Douyin live stream with a shopping cart.**

### shell — Run Raw Shell Command

Escape hatch for anything `adb-claw` doesn't have a dedicated command for.

```bash
adb-claw shell "ls /sdcard/"
adb-claw shell "getprop ro.build.version.release"
adb-claw shell "settings put system screen_brightness 128"
```

Returns stdout, stderr, and exit_code in JSON envelope.

### file — File Transfer

```bash
adb-claw file push ./local.apk /sdcard/      # Push to device
adb-claw file pull /sdcard/photo.jpg ./       # Pull from device
```

### device — Device Info

```bash
adb-claw device list      # List connected devices
adb-claw device info      # Model, Android version, screen size, density
```

### ui — UI Element Inspection

```bash
adb-claw ui tree                    # Full UI element tree
adb-claw ui find --text "Settings"  # Find by text
adb-claw ui find --id "com.app:id/title"  # Find by resource ID
adb-claw ui find --index 3          # Find by index
```

## Workflow Patterns

### Always Observe First

Before any action, run `observe` to see the screen. After every action, `observe` again to verify.

```
1. adb-claw observe          → See what's on screen
2. adb-claw tap --index 3    → Perform action
3. adb-claw observe          → Verify result
```

### Prefer Index-Based Targeting

Use `--index N` over coordinates. Indices from `observe` are stable across screen sizes.

### Type After Focus

Always tap an input field first, then type:

```
1. adb-claw tap --index 7       → Focus the text field
2. adb-claw type "search query" → Enter text
3. adb-claw key ENTER           → Submit
```

### Scroll Pattern

```
adb-claw scroll down             # Scroll down one page
adb-claw scroll up --pages 3     # Scroll up multiple pages
adb-claw scroll down --index 5   # Scroll within a specific element
```

**Always prefer `scroll` over manual `swipe`.** After scrolling, always `observe`.

### CJK Text Input

`adb-claw type` only supports ASCII. For Chinese/Japanese/Korean input:

1. **Preferred**: Use `adb-claw open` with deep links (e.g., `adb-claw open 'myapp://search?keyword=中文'`)
2. **Clear before input**: `adb-claw clear-field --index 7` to clear existing text first

### Wait for Page Load

Instead of repeated `observe` polling, use `wait`:

```
1. adb-claw tap --index 3                      → Trigger navigation
2. adb-claw wait --text "Welcome" --timeout 15000  → Wait for new page
3. adb-claw observe                             → See the loaded page
```

### Device Form Factor Detection

Use `adb-claw device info` to get screen size, then determine form factor:
- Short edge < 1200px → **Phone** (portrait-first)
- Short edge >= 1200px → **Pad/Fold** (landscape-first)

Swipe coordinates and UI layouts differ between Phone and Pad. App Profiles document these differences.

### Audio Capture

First check if the device supports it:

```
1. adb-claw device info              → Check Android version (need 11+ / SDK 30+)
```

To record audio to a file for the user:

```
1. adb-claw audio capture --file recording.wav --duration 30000   → Record 30s
```

To transcribe live audio (requires `asrclaw` installed separately):

```
1. adb-claw audio capture --stream --duration 60000 | asrclaw transcribe --stream --lang zh
```

**Important**: Device speakers are muted during capture. Inform the user before starting. For live streams, combine with `monitor` for complete context (audio + chat text).

### Douyin Live Cart

Grab shopping cart products from a Douyin live stream:

```
1. Enter a Douyin live stream with a shopping cart (小黄车)
2. adb-claw live cart                    → Capture top 10 products + explaining product
3. adb-claw live cart --count 20         → Capture more products
```

The command handles everything automatically: opens cart, scrolls, captures, closes. No manual tapping needed.

### Error Recovery

If an action fails or produces unexpected results:
1. Run `observe` to see the current state
2. Check if the screen changed unexpectedly (dialog, permission prompt)
3. Adjust and retry

## Output Format

All commands return JSON:

```json
{
  "ok": true,
  "command": "tap",
  "data": { ... },
  "duration_ms": 150,
  "timestamp": "2026-03-12T10:00:00Z"
}
```

On error:

```json
{
  "ok": false,
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "No device connected",
    "suggestion": "Connect a device via USB and enable USB debugging"
  }
}
```

## Security & Trust

**What adb-claw is**: A pure CLI wrapper around standard `adb` commands. It translates high-level instructions (e.g., `adb-claw tap --index 3`) into `adb shell input tap ...` calls. That's it.

**What adb-claw does NOT do**:
- Does not install APKs or persistent services on the device — `monitor` and `audio capture` each push a temporary ~7KB DEX that runs briefly and auto-exits
- Does not collect or transmit data — no telemetry, no analytics, no network requests
- Does not request credentials or environment variables
- Does not modify your host system beyond placing the binary

**Source code is fully open**: [github.com/llm-net/adb-claw](https://github.com/llm-net/adb-claw). If you don't trust pre-built binaries, you can **audit the source code and build from source** — see the [README](https://github.com/llm-net/adb-claw#readme) for instructions. Every release also includes SHA256 checksums for binary verification.

**Device sensitivity**: adb-claw can capture screenshots, record system audio, and control apps on the connected device — this is the core purpose of the tool. Only connect devices you trust, and disable USB debugging when not actively using adb-claw.

**Agent scope**: adb-claw commands are the only commands this skill should execute. Do not run install scripts, download binaries, or modify the host system. If adb-claw or adb is not available, inform the user.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No devices found | Walk the user through: Settings → About phone → tap Build number 7x → Developer options → enable USB debugging → reconnect USB → approve the "Allow USB debugging" dialog on phone. See Setup section for full guide |
| adb not found | `brew install android-platform-tools` (macOS) |
| Tap hits wrong element | Use `--index` instead of coordinates; re-run `observe` |
| `type` doesn't work | Tap input field first to focus; ASCII only |
| CJK text needed | Use `adb-claw open` with deep link containing the text as URL parameter |
| UI dump fails | Pause animations (tap to pause video), wait 1s, retry |
| UI dump fails on search pages | Search results may auto-play video previews; use `screenshot` instead or `monitor` to read text |
| UI dump fails during live stream | Use `monitor` command — it bypasses video surfaces via accessibility framework |
| Command timeout | Increase with `--timeout 60000` |
| Permission dialog | Use `observe` to see it, tap the allow/skip button |
| Screen is off | `adb-claw screen on` or `adb-claw screen unlock` |
| Audio capture fails | Requires Android 11+ (API 30); check with `adb-claw device info` |
| No audio captured | REMOTE_SUBMIX may not be available on all devices/ROMs |
| Speakers muted during capture | Expected behavior — REMOTE_SUBMIX redirects audio output |
