# Windows Path

This file defines the intended Windows branch for the skill.

## Preferred direction

For Windows, prefer a helper-script path that wraps:

- `pygetwindow` (Win32 window enumeration/activation, restore minimized windows)
- screenshot tooling such as Pillow/MSS
- pyautogui for mouse and keyboard input
- text input: clipboard paste via PowerShell `Set-Clipboard` + `Ctrl+V` (handles all languages including CJK; falls back to `clip.exe` if PowerShell unavailable)
- key press / hotkey: `pyautogui.press()` / `pyautogui.hotkey()`

## MVP rule

Windows helpers are now **best-effort** via `pygetwindow` (frontmost, list windows, focus, bounds). If `pygetwindow` or its dependencies are missing, commands will return structured errors. Be explicit about dependency requirements when failures occur.

## Expected Windows command surface

Aim to match the macOS helper surface:

- screenshot
- capture-region
- frontmost
- list-apps or windows
- focus-app
- click / double-click / drag / scroll
- type / press / hotkey

## Behavior rule

Keep the top-level workflow the same across platforms; only the helper implementation should differ.

## Windows WeChat note

For WeChat on Windows, first check for the visible `发送` button and prefer it as the send trigger.

- type message text with `desktop_ops.py type --text`
- if a literal line break is needed, use `desktop_ops.py insert-newline`
- resolve the visible `发送` button with `target_resolver.py --text "发送"` and click it when verified
- only fall back to `press --key return` if no verified send button exists and Enter-to-send is already confirmed for that host
