# macOS Path

## Preferred tools

For macOS, prefer these primitives:

- screenshot: `/usr/sbin/screencapture`
- app activation: `osascript` (AppleScript)
- mouse: `cliclick` (preferred) → `pyautogui` (fallback)
- text input: clipboard paste via `set the clipboard to` + `Cmd+V` (handles all languages including CJK)
- key press: AppleScript `key code` (preferred, most reliable for apps like WeChat) → `cliclick kp:` (fallback)
- hotkey: `cliclick kd:/t:/ku:` (modifier keys + character) → `pyautogui.hotkey` (fallback)
- focus-app: fast path if already frontmost; Dock click to restore minimized windows; `activate` + `AXRaise`

Use them through `scripts/desktop_ops.py`, not ad hoc each time.

For local setup, prefer a dedicated virtual environment outside the packaged skill directory and install runtime deps there before testing action commands. When running diagnostics, pass that interpreter through an environment variable such as `DESKTOP_AGENT_OPS_PYTHON`.

## Required permissions

macOS desktop automation may require:

- Accessibility
- Screen Recording
- Automation permissions for app control

If capture or input fails unexpectedly, suspect permissions first.

## Minimum macOS command set for MVP

Implement and use these first:

- `screenshot`
- `capture-region`
- `frontmost`
- `list-apps`
- `focus-app`
- `move`
- `click`
- `double-click`
- `drag`
- `scroll`
- `press`
- `type`
- `hotkey`
- `mouse-position`

## Recommended action order on macOS

## Timing notes for interactive apps

On macOS, app activation, focus transfer, and message-send UI updates may lag slightly behind the input event.

When working with chat apps such as WeChat:
- after `focus-app`, prefer a short settle wait before capturing if the window was previously occluded
- `type --text` always uses clipboard paste (reliable for CJK); cliclick `t:` silently drops non-ASCII characters
- `press --key return` uses AppleScript `key code 36` (not cliclick) — cliclick's `kp:return` is not recognized by WeChat and some other apps
- for WeChat and similar instant-messaging apps, first check for a verified visible send control; if none exists, use `desktop_ops.py press --key return` only when direct-Enter-to-send is verified for that host
- when a multi-line message is needed, use `desktop_ops.py insert-newline` for the line break and keep `press --key return` for the actual send event
- after a send trigger, wait a short moment (0.3–0.5s) before verification capture
- if the first verification capture is ambiguous, recapture once more at about 1 second total elapsed before treating it as a failure
- `focus-app` skips Dock traversal if app is already frontmost (fast path ~0.3s vs full ~1s)


### Bring an app forward

1. check frontmost app
2. if wrong, run `focus-app`
3. capture again
4. verify app switched

### Work inside a target UI

1. capture state
2. if target is unclear, capture a smaller region
3. perform one action
4. capture again
5. verify before continuing

## Notes

- `focus-window` may be added later, but `focus-app` is enough for MVP
- prefer explicit re-capture after activation because animation and focus changes can lag
- when a text search UI exists, use it instead of manual scanning/scrolling
ts/doctor.py`
