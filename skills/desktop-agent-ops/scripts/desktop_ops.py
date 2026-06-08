#!/usr/bin/env python3
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None


def escape_applescript_string(value):
    """Escape backslashes and quotes before embedding text in AppleScript."""
    return value.replace('\\', '\\\\').replace('"', '\\"')


def normalize_press_key(key):
    """Normalize user-facing key names so Enter-like actions map to real key presses."""
    normalized = str(key).strip().lower()
    aliases = {
        'enter': 'return',
        'return': 'return',
        'esc': 'escape',
        'backspace': 'delete',
    }
    return aliases.get(normalized, normalized)


def pyautogui_key_name(key):
    """Translate normalized key names to the names expected by pyautogui."""
    mapping = {
        'return': 'enter',
        'escape': 'esc',
        'delete': 'backspace',
        'up arrow': 'up',
        'down arrow': 'down',
        'left arrow': 'left',
        'right arrow': 'right',
    }
    return mapping.get(key, key)


def jprint(data):
    print(json.dumps(data, ensure_ascii=False))


def jerror(action, message, platform_name=None, hint=None, details=None):
    payload = {"ok": False, "action": action, "error": message}
    if platform_name:
        payload["platform"] = platform_name
    if hint:
        payload["hint"] = hint
    if details:
        payload["details"] = details
    jprint(payload)
    sys.exit(1)


def run(cmd, timeout=10):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or f"command failed: {' '.join(cmd)}")
    return p.stdout.strip()


def run_safe(cmd, timeout=10):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {
        "ok": p.returncode == 0,
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def osascript(script, action, platform_name):
    result = run_safe(["/usr/bin/osascript", "-e", script])
    if result["ok"]:
        return {"ok": True, "stdout": result["stdout"]}
    stderr = result["stderr"]
    hint = None
    if "Not authorized" in stderr or "-1743" in stderr or "-10827" in stderr:
        hint = "automation_permission_required"
    return {"ok": False, "stderr": stderr, "hint": hint}


def pyautogui_mod():
    try:
        import pyautogui  # type: ignore
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        return pyautogui
    except Exception as e:
        raise SystemExit(f"pyautogui unavailable: {e}")


def pygetwindow_mod():
    try:
        import pygetwindow  # type: ignore
        return pygetwindow
    except Exception as e:
        return None


def find_running_app(query, candidates):
    """Case-insensitive exact match of query against candidate process names."""
    q = query.lower()
    for name in candidates:
        if name.lower() == q:
            return name
    return None


def find_cliclick():
    return shutil.which('cliclick')


def require_cliclick():
    cc = find_cliclick()
    if not cc:
        raise SystemExit("cliclick unavailable")
    return cc


def cliclick_cmd(*commands):
    cc = require_cliclick()
    run([cc, *commands])


def cmd_screenshot(output=None, x=None, y=None, width=None, height=None, with_cursor=False):
    system = platform.system().lower()
    if output is None:
        fd, path = tempfile.mkstemp(prefix="desktop-agent-", suffix=".png")
        os.close(fd)
        Path(path).unlink(missing_ok=True)
        output = path
    region = None if None in (x, y, width, height) else {"x": x, "y": y, "width": width, "height": height}
    if system == "darwin":
        cmd = ["/usr/sbin/screencapture", "-x"]
        if region:
            cmd += ["-R", f"{x},{y},{width},{height}"]
        cmd += [output]
        result = run_safe(cmd)
        if not result["ok"]:
            hint = "screen_recording_permission_required" if "could not create image from display" in result["stderr"].lower() else None
            jerror("screenshot", result["stderr"] or "screencapture_failed", system, hint=hint)
            return
        mouse = None
        if with_cursor:
            try:
                cc = find_cliclick()
                if cc:
                    out = run([cc, '-d', 'stdout', 'p:.'])
                    mx, my = [int(v) for v in out.strip().split(',')]
                    mouse = {"x": mx, "y": my}
            except Exception:
                mouse = None
        jprint({"ok": True, "action": "screenshot", "output": output, "with_cursor": with_cursor, "mouse": mouse, "region": region})
        return
    try:
        pg = pyautogui_mod()
        if region:
            img = pg.screenshot(region=(x, y, width, height))
        else:
            img = pg.screenshot()
        img.save(output)
        mouse = None
        if with_cursor:
            pos = pg.position()
            mouse = {"x": int(pos.x), "y": int(pos.y)}
        jprint({"ok": True, "action": "screenshot", "output": output, "with_cursor": with_cursor, "mouse": mouse, "region": region})
        return
    except Exception as e:
        jerror("screenshot", f"not implemented or failed: {e}", system)


def cmd_frontmost():
    system = platform.system().lower()
    if system == "darwin":
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = osascript(script, "frontmost", system)
        if not result["ok"]:
            jerror("frontmost", result["stderr"] or "osascript_failed", system, hint=result.get("hint"))
            return
        jprint({"ok": True, "frontmost_app": result["stdout"]})
        return
    if system == "windows":
        gw = pygetwindow_mod()
        if not gw:
            jerror("frontmost", "pygetwindow_unavailable", system)
            return
        win = gw.getActiveWindow()
        if not win:
            jerror("frontmost", "active_window_not_found", system)
            return
        jprint({"ok": True, "frontmost_app": win.title})
        return
    if system == "linux":
        if shutil.which("xdotool"):
            try:
                wid = run(["xdotool", "getactivewindow"])
                name = run(["xdotool", "getwindowname", wid])
                jprint({"ok": True, "frontmost_app": name})
                return
            except Exception as e:
                jerror("frontmost", f"xdotool_failed:{e}", system)
                return
        jerror("frontmost", "xdotool_missing", system)
        return
    jerror("frontmost", "not_implemented", system)
    return


def cmd_list_apps():
    system = platform.system().lower()
    if system == "darwin":
        script = 'tell application "System Events" to get name of every application process'
        result = osascript(script, "list-apps", system)
        if not result["ok"]:
            jerror("list-apps", result["stderr"] or "osascript_failed", system, hint=result.get("hint"))
            return
        apps = [a.strip() for a in result["stdout"].split(',') if a.strip()]
        jprint({"ok": True, "apps": apps})
        return
    if system == "windows":
        gw = pygetwindow_mod()
        if not gw:
            jerror("list-apps", "pygetwindow_unavailable", system)
            return
        titles = [t for t in gw.getAllTitles() if t.strip()]
        jprint({"ok": True, "apps": titles})
        return
    if system == "linux":
        if shutil.which("wmctrl"):
            try:
                raw = run(["wmctrl", "-l"])
                titles = []
                for line in raw.splitlines():
                    parts = line.split(None, 3)
                    if len(parts) == 4:
                        titles.append(parts[3].strip())
                jprint({"ok": True, "apps": [t for t in titles if t]})
                return
            except Exception as e:
                jerror("list-apps", f"wmctrl_failed:{e}", system)
                return
        jerror("list-apps", "wmctrl_missing", system)
        return
    jerror("list-apps", "not_implemented", system)
    return


def cmd_focus_app(name):
    system = platform.system().lower()
    if system == "darwin":
        app_name = escape_applescript_string(name)

        # Fast path: check if already frontmost — skip everything if so
        check = osascript('tell application "System Events" to get name of first application process whose frontmost is true', "focus-app", system)
        if check.get("ok") and name.lower() in check.get("stdout", "").lower():
            # Already frontmost, just ensure window is raised
            osascript(f'''tell application "System Events"
    tell process "{app_name}"
        try
            perform action "AXRaise" of window 1
        end try
    end tell
end tell''', "focus-app", system)
            jprint({"ok": True, "action": "focus-app", "app": name, "verified_frontmost": True})
            return

        # Full activation: unhide + restore minimized + activate + raise
        script = f'''
tell application "System Events"
    set appExists to (exists process "{app_name}")
end tell

if appExists then
    tell application "System Events"
        set visible of process "{app_name}" to true
    end tell
    -- Restore minimized windows via Dock click
    try
        tell application "System Events"
            tell process "Dock"
                repeat with dockItem in (every UI element of list 1)
                    try
                        if name of dockItem is "{app_name}" then
                            click dockItem
                            delay 0.15
                            exit repeat
                        end if
                    end try
                end repeat
            end tell
        end tell
    end try
    tell application "{app_name}" to activate
    delay 0.15
    tell application "System Events"
        tell process "{app_name}"
            set frontmost to true
            try
                perform action "AXRaise" of window 1
            end try
        end tell
    end tell
else
    tell application "{app_name}" to activate
end if
'''
        result = osascript(script, "focus-app", system)
        if not result["ok"]:
            fallback = osascript(f'tell application "{app_name}" to activate', "focus-app", system)
            if not fallback["ok"]:
                jerror("focus-app", fallback["stderr"] or "osascript_failed", system, hint=fallback.get("hint"))
                return

        # Quick verify
        time.sleep(0.1)
        verify = osascript('tell application "System Events" to get name of first application process whose frontmost is true', "focus-app", system)
        is_front = verify.get("ok") and name.lower() in verify.get("stdout", "").lower()

        jprint({"ok": True, "action": "focus-app", "app": name, "verified_frontmost": is_front})
        return
    if system == "windows":
        gw = pygetwindow_mod()
        if not gw:
            jerror("focus-app", "pygetwindow_unavailable", system)
            return
        wins = gw.getWindowsWithTitle(name)
        if not wins:
            jerror("focus-app", "window_not_found", system)
            return
        win = wins[0]
        try:
            # Restore if minimized, then activate
            if win.isMinimized:
                win.restore()
            win.activate()
        except Exception:
            pass
        jprint({"ok": True, "action": "focus-app", "app": name})
        return
    if system == "linux":
        if shutil.which("wmctrl"):
            try:
                run(["wmctrl", "-a", name])
                jprint({"ok": True, "action": "focus-app", "app": name})
                return
            except Exception as e:
                jerror("focus-app", f"wmctrl_failed:{e}", system)
                return
        jerror("focus-app", "wmctrl_missing", system)
        return
    jerror("focus-app", "not_implemented", system)
    return


def cmd_front_window_bounds(app=None):
    system = platform.system().lower()
    if system == "darwin":
        frontmost = osascript('tell application "System Events" to get name of first application process whose frontmost is true', "front-window-bounds", system)
        if not frontmost["ok"]:
            jerror("front-window-bounds", frontmost["stderr"] or "osascript_failed", system, hint=frontmost.get("hint"))
            return
        process_name = app or frontmost["stdout"]
        escaped_process_name = escape_applescript_string(process_name)
        if app:
            activate = osascript(f'tell application "{escaped_process_name}" to activate', "front-window-bounds", system)
            if not activate["ok"]:
                jerror("front-window-bounds", activate["stderr"] or "osascript_failed", system, hint=activate.get("hint"))
                return
        script = f'''tell application "System Events"
  tell process "{escaped_process_name}"
    set frontmost to true
    set w to front window
    set p to position of w
    set s to size of w
    return (name of w as text) & "|" & (item 1 of p as text) & "," & (item 2 of p as text) & "|" & (item 1 of s as text) & "," & (item 2 of s as text)
  end tell
end tell'''
        bounds = osascript(script, "front-window-bounds", system)
        if not bounds["ok"]:
            jerror("front-window-bounds", bounds["stderr"] or "osascript_failed", system, hint=bounds.get("hint"))
            return
        raw = bounds["stdout"]
        parts = raw.rsplit('|', 2)
        if len(parts) != 3:
            jerror("front-window-bounds", "unexpected_bounds_format", system, details={"raw": raw})
            return
        window_name, pos, size = parts
        x, y = [int(v.strip()) for v in pos.split(',')]
        width, height = [int(v.strip()) for v in size.split(',')]
        jprint({"ok": True, "action": "front-window-bounds", "app": process_name, "window": window_name, "x": x, "y": y, "width": width, "height": height})
        return
    if system == "windows":
        gw = pygetwindow_mod()
        if not gw:
            jerror("front-window-bounds", "pygetwindow_unavailable", system)
            return
        win = None
        if app:
            wins = gw.getWindowsWithTitle(app)
            if wins:
                win = wins[0]
                try:
                    win.activate()
                except Exception:
                    pass
        if not win:
            win = gw.getActiveWindow()
        if not win:
            jerror("front-window-bounds", "active_window_not_found", system)
            return
        jprint({"ok": True, "action": "front-window-bounds", "app": app or win.title, "window": win.title, "x": int(win.left), "y": int(win.top), "width": int(win.width), "height": int(win.height)})
        return
    if system == "linux":
        if app and shutil.which("wmctrl"):
            try:
                run(["wmctrl", "-a", app])
            except Exception:
                pass
        if shutil.which("xdotool"):
            try:
                wid = run(["xdotool", "getactivewindow"])
                geom_raw = run(["xdotool", "getwindowgeometry", "--shell", wid])
                name = run(["xdotool", "getwindowname", wid])
                geom = {}
                for line in geom_raw.splitlines():
                    m = re.match(r"^(X|Y|WIDTH|HEIGHT)=(\d+)$", line.strip())
                    if m:
                        geom[m.group(1)] = int(m.group(2))
                if not all(k in geom for k in ("X", "Y", "WIDTH", "HEIGHT")):
                    jerror("front-window-bounds", "geometry_parse_failed", system)
                    return
                jprint({"ok": True, "action": "front-window-bounds", "app": app or name, "window": name, "x": geom["X"], "y": geom["Y"], "width": geom["WIDTH"], "height": geom["HEIGHT"]})
                return
            except Exception as e:
                jerror("front-window-bounds", f"xdotool_failed:{e}", system)
                return
        jerror("front-window-bounds", "xdotool_missing", system)
        return
    jerror("front-window-bounds", "not_implemented", system)
    return


def cmd_move(x, y, duration=0.0):
    cc = find_cliclick()
    if cc and platform.system().lower() == "darwin":
        run([cc, f"m:{x},{y}"])
        jprint({"ok": True, "action": "move", "backend": "cliclick", "x": x, "y": y, "duration": duration})
        return
    pg = pyautogui_mod()
    pg.moveTo(x, y, duration=duration)
    jprint({"ok": True, "action": "move", "backend": "pyautogui", "x": x, "y": y, "duration": duration})


def cmd_click(x=None, y=None, clicks=1, button="left"):
    cc = find_cliclick()
    if cc and platform.system().lower() == "darwin":
        prefix = {"left": "c", "right": "rc", "middle": None}[button]
        if prefix is None:
            raise SystemExit("middle click via cliclick not implemented")
        target = "." if x is None or y is None else f"{x},{y}"
        command = f"{prefix}:{target}"
        if clicks == 2 and button == "left":
            command = f"dc:{target}"
        elif clicks != 1:
            raise SystemExit(f"cliclick backend does not support clicks={clicks} for button={button}")
        run([cc, command])
        jprint({"ok": True, "action": "click", "backend": "cliclick", "clicks": clicks, "button": button, "x": x, "y": y})
        return
    pg = pyautogui_mod()
    if x is not None and y is not None:
        pg.click(x=x, y=y, clicks=clicks, interval=0.1, button=button)
    else:
        pg.click(clicks=clicks, interval=0.1, button=button)
    jprint({"ok": True, "action": "click", "backend": "pyautogui", "clicks": clicks, "button": button, "x": x, "y": y})


def cmd_drag(x1, y1, x2, y2, duration=0.2, button="left"):
    cc = find_cliclick()
    if cc and platform.system().lower() == "darwin":
        if button != "left":
            raise SystemExit("cliclick drag currently supports left button only")
        # cliclick doesn't support duration natively; insert wait between
        # mouse-down-move and mouse-up to allow UI to register the drag
        wait_ms = max(int(duration * 1000), 50)
        run([cc, f"dd:{x1},{y1}", f"w:{wait_ms}", f"dm:{x2},{y2}", f"du:{x2},{y2}"])
        jprint({"ok": True, "action": "drag", "backend": "cliclick", "from": [x1, y1], "to": [x2, y2], "button": button, "duration": duration})
        return
    pg = pyautogui_mod()
    pg.moveTo(x1, y1, duration=0)
    pg.dragTo(x2, y2, duration=duration, button=button)
    jprint({"ok": True, "action": "drag", "backend": "pyautogui", "from": [x1, y1], "to": [x2, y2], "button": button, "duration": duration})


def cmd_scroll(amount, x=None, y=None, direction="vertical"):
    system = platform.system().lower()

    # If x,y specified, first move cursor there so scroll targets the right window/area
    if x is not None and y is not None:
        cc = find_cliclick()
        if cc and system == "darwin":
            run([cc, f"m:{x},{y}"])
        else:
            pg = pyautogui_mod()
            pg.moveTo(x, y, duration=0)

    if direction == "horizontal":
        pg = pyautogui_mod()
        pg.hscroll(amount)
        jprint({"ok": True, "action": "scroll", "backend": "pyautogui", "direction": "horizontal",
                 "amount": amount, "x": x, "y": y})
        return

    # Vertical scroll
    pg = pyautogui_mod()
    pg.scroll(amount)
    jprint({"ok": True, "action": "scroll", "backend": "pyautogui", "direction": "vertical",
             "amount": amount, "x": x, "y": y})


def cmd_press(key):
    system = platform.system().lower()
    normalized_key = normalize_press_key(key)

    # Map common key names to AppleScript equivalents
    APPLESCRIPT_KEYS = {
        "return": "return",
        "tab": "tab", "escape": "escape",
        "delete": "delete", "backspace": "delete",
        "space": "space",
        "up": "up arrow", "down": "down arrow",
        "left": "left arrow", "right": "right arrow",
    }

    # macOS: AppleScript key code is primary (most reliable for apps like WeChat)
    # cliclick kp: generates events that some apps don't recognize
    if system == "darwin":
        as_key = APPLESCRIPT_KEYS.get(normalized_key, normalized_key)
        if as_key in ("return", "tab", "escape", "delete", "space",
                       "up arrow", "down arrow", "left arrow", "right arrow"):
            script = f'tell application "System Events" to key code {_key_to_keycode(as_key)}'
        else:
            escaped_key = escape_applescript_string(as_key)
            script = f'tell application "System Events" to keystroke "{escaped_key}"'
        result = osascript(script, "press", system)
        if result["ok"]:
            jprint({"ok": True, "action": "press", "backend": "applescript", "key": normalized_key})
            return
        # Fallback to cliclick
        cc = find_cliclick()
        if cc:
            try:
                run([cc, f"kp:{normalized_key}"])
                jprint({"ok": True, "action": "press", "backend": "cliclick", "key": normalized_key})
                return
            except SystemExit:
                pass

    pg = pyautogui_mod()
    pg.press(pyautogui_key_name(normalized_key))
    jprint({"ok": True, "action": "press", "backend": "pyautogui", "key": normalized_key})


def _key_to_keycode(key_name):
    """Map key names to macOS virtual key codes for AppleScript key code command."""
    codes = {
        "return": 36, "tab": 48, "escape": 53, "delete": 51,
        "space": 49, "up arrow": 126, "down arrow": 125,
        "left arrow": 123, "right arrow": 124,
    }
    return codes.get(key_name, 36)


def paste_text(text, action_name='type'):
    """Paste literal text via clipboard — single fast operation per platform."""
    system = platform.system().lower()

    if system == 'darwin':
        # Single osascript: set clipboard + Cmd+V in one call (avoids extra subprocess)
        escaped = escape_applescript_string(text)
        script = f'''set the clipboard to "{escaped}"
delay 0.05
tell application "System Events" to keystroke "v" using command down'''
        result = osascript(script, action_name, system)
        if result['ok']:
            return 'clipboard_paste'
        # Fallback: pbcopy + osascript Cmd+V (for text with special chars)
        subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        result2 = osascript('tell application "System Events" to keystroke "v" using command down', action_name, system)
        if result2['ok']:
            return 'pbcopy_paste'
        raise SystemExit(result2['stderr'] or 'paste_failed')

    if system == 'windows':
        # PowerShell Set-Clipboard is faster than clip.exe for Unicode
        try:
            subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 f'Set-Clipboard -Value "{text.replace(chr(34), "`" + chr(34))}"'],
                check=True, capture_output=True, timeout=5)
        except Exception:
            subprocess.run(['clip'], input=text.encode('utf-16le'), check=True)
        pg = pyautogui_mod()
        pg.hotkey('ctrl', 'v')
        return 'clipboard_paste'

    if system == 'linux' and shutil.which('xclip'):
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
        pg = pyautogui_mod()
        pg.hotkey('ctrl', 'v')
        return 'xclip_paste'

    raise SystemExit('literal_paste_unavailable')


def _has_non_ascii(text):
    return any(ord(c) > 127 for c in text)


def cmd_type(text):
    system = platform.system().lower()
    has_cjk = _has_non_ascii(text)

    # Primary path: clipboard paste — fast, reliable for ALL text including CJK
    # cliclick t: silently drops CJK characters, so clipboard is always preferred
    try:
        backend = paste_text(text, action_name='type')
        jprint({"ok": True, "action": "type", "backend": backend, "text_length": len(text)})
        return
    except Exception:
        pass

    # Fallback for pure ASCII: cliclick (macOS) or pyautogui
    if has_cjk:
        jerror("type", "non_ascii_text_requires_clipboard_paste", system,
               hint="check_pbcopy_or_xclip_availability")
        return

    cc = find_cliclick()
    if cc and system == "darwin":
        try:
            run([cc, f"t:{text}"])
            jprint({"ok": True, "action": "type", "backend": "cliclick", "text_length": len(text)})
            return
        except SystemExit:
            pass

    pg = pyautogui_mod()
    pg.write(text, interval=0.0)
    jprint({"ok": True, "action": "type", "backend": "pyautogui", "text_length": len(text)})


def cmd_insert_newline(count=1):
    system = platform.system().lower()
    if count < 1:
        jerror('insert-newline', 'count_must_be_positive', system)
        return
    try:
        backend = paste_text('\n' * count, action_name='insert-newline')
    except SystemExit as e:
        jerror('insert-newline', str(e), system)
        return
    jprint({"ok": True, "action": "insert-newline", "backend": backend, "count": count})


_CLICLICK_SPECIAL_KEYS = {
    "return", "enter", "tab", "escape", "esc", "delete", "backspace",
    "space", "arrow-up", "arrow-down", "arrow-left", "arrow-right",
    "home", "end", "page-up", "page-down", "fwd-delete",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
    "f9", "f10", "f11", "f12", "f13", "f14", "f15", "f16",
}


def cmd_hotkey(keys):
    cc = find_cliclick()
    if cc and platform.system().lower() == "darwin":
        if len(keys) == 1:
            run([cc, f"kp:{keys[0]}"])
        else:
            modifiers = ','.join(keys[:-1])
            last_key = keys[-1]
            # cliclick kp: only accepts special keys; use t: for letters/characters
            if last_key.lower() in _CLICLICK_SPECIAL_KEYS:
                key_cmd = f"kp:{last_key}"
            else:
                key_cmd = f"t:{last_key}"
            run([cc, f"kd:{modifiers}", key_cmd, f"ku:{modifiers}"])
        jprint({"ok": True, "action": "hotkey", "backend": "cliclick", "keys": keys})
        return
    pg = pyautogui_mod()
    pg.hotkey(*keys)
    jprint({"ok": True, "action": "hotkey", "backend": "pyautogui", "keys": keys})


def cmd_mouse_position():
    cc = find_cliclick()
    if cc:
        out = run([cc, '-d', 'stdout', 'p:.'])
        x, y = [int(v) for v in out.strip().split(',')]
        jprint({"ok": True, "backend": "cliclick", "x": x, "y": y})
        return
    pg = pyautogui_mod()
    pos = pg.position()
    jprint({"ok": True, "backend": "pyautogui", "x": pos.x, "y": pos.y})


def cmd_screen_size():
    system = platform.system().lower()
    if system == 'darwin':
        script = 'tell application "Finder" to get bounds of window of desktop'
        result = osascript(script, "screen-size", system)
        if not result["ok"]:
            jerror("screen-size", result["stderr"] or "osascript_failed", system, hint=result.get("hint"))
            return
        raw = result["stdout"]
        parts = [int(x.strip()) for x in raw.split(',')]
        left, top, right, bottom = parts
        jprint({"ok": True, "width": right - left, "height": bottom - top, "bounds": [left, top, right, bottom]})
        return
    pg = pyautogui_mod()
    w, h = pg.size()
    jprint({"ok": True, "width": w, "height": h})


def cmd_pixel_color(x, y):
    if Image is None:
        raise SystemExit("PIL unavailable: cannot read pixel-color")
    fd, tmp = tempfile.mkstemp(prefix='desktop-pixel-', suffix='.png')
    os.close(fd)
    cmd_screenshot(tmp, x, y, 1, 1)
    img = Image.open(tmp)
    pixel = img.getpixel((0, 0))
    try:
        Path(tmp).unlink(missing_ok=True)
    except Exception:
        pass
    if isinstance(pixel, int):
        rgb = [pixel, pixel, pixel]
    else:
        rgb = list(pixel[:3])
    hexv = '#%02x%02x%02x' % tuple(rgb)
    jprint({"ok": True, "action": "pixel-color", "x": x, "y": y, "rgb": rgb, "hex": hexv})


def build_parser():
    p = argparse.ArgumentParser(description="desktop helper ops")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("screenshot")
    s.add_argument("--output")
    s.add_argument("--x", type=int)
    s.add_argument("--y", type=int)
    s.add_argument("--width", type=int)
    s.add_argument("--height", type=int)
    s.add_argument("--with-cursor", action="store_true")

    cr = sub.add_parser("capture-region")
    cr.add_argument("--x", type=int, required=True)
    cr.add_argument("--y", type=int, required=True)
    cr.add_argument("--width", type=int, required=True)
    cr.add_argument("--height", type=int, required=True)
    cr.add_argument("--output")
    cr.add_argument("--with-cursor", action="store_true")

    sub.add_parser("frontmost")
    sub.add_parser("list-apps")

    fwb = sub.add_parser("front-window-bounds")
    fwb.add_argument("--app")

    fa = sub.add_parser("focus-app")
    fa.add_argument("--name", required=True)

    mv = sub.add_parser("move")
    mv.add_argument("--x", type=int, required=True)
    mv.add_argument("--y", type=int, required=True)
    mv.add_argument("--duration", type=float, default=0.0)

    c = sub.add_parser("click")
    c.add_argument("--x", type=int)
    c.add_argument("--y", type=int)
    c.add_argument("--button", choices=["left", "right", "middle"], default="left")

    dc = sub.add_parser("double-click")
    dc.add_argument("--x", type=int)
    dc.add_argument("--y", type=int)
    dc.add_argument("--button", choices=["left", "right", "middle"], default="left")

    d = sub.add_parser("drag")
    d.add_argument("--x1", type=int, required=True)
    d.add_argument("--y1", type=int, required=True)
    d.add_argument("--x2", type=int, required=True)
    d.add_argument("--y2", type=int, required=True)
    d.add_argument("--duration", type=float, default=0.2)
    d.add_argument("--button", choices=["left", "right", "middle"], default="left")

    sc = sub.add_parser("scroll")
    sc.add_argument("--amount", type=int, required=True, help="Scroll amount: positive=up, negative=down")
    sc.add_argument("--x", type=int, help="Move cursor to X before scrolling (ensures correct window)")
    sc.add_argument("--y", type=int, help="Move cursor to Y before scrolling (ensures correct window)")
    sc.add_argument("--direction", choices=["vertical", "horizontal"], default="vertical")

    pr = sub.add_parser("press")
    pr.add_argument("--key", required=True)

    t = sub.add_parser("type")
    t.add_argument("--text", required=True)

    nl = sub.add_parser("insert-newline")
    nl.add_argument("--count", type=int, default=1)

    hk = sub.add_parser("hotkey")
    hk.add_argument("--keys", nargs='+', required=True)

    sub.add_parser("mouse-position")
    sub.add_parser("screen-size")

    pc = sub.add_parser("pixel-color")
    pc.add_argument("--x", type=int, required=True)
    pc.add_argument("--y", type=int, required=True)
    return p


def main():
    args = build_parser().parse_args()
    if args.cmd == "screenshot":
        cmd_screenshot(args.output, args.x, args.y, args.width, args.height, args.with_cursor)
    elif args.cmd == "capture-region":
        cmd_screenshot(args.output, args.x, args.y, args.width, args.height, args.with_cursor)
    elif args.cmd == "frontmost":
        cmd_frontmost()
    elif args.cmd == "list-apps":
        cmd_list_apps()
    elif args.cmd == "front-window-bounds":
        cmd_front_window_bounds(args.app)
    elif args.cmd == "focus-app":
        cmd_focus_app(args.name)
    elif args.cmd == "move":
        cmd_move(args.x, args.y, args.duration)
    elif args.cmd == "click":
        cmd_click(args.x, args.y, 1, args.button)
    elif args.cmd == "double-click":
        cmd_click(args.x, args.y, 2, args.button)
    elif args.cmd == "drag":
        cmd_drag(args.x1, args.y1, args.x2, args.y2, args.duration, args.button)
    elif args.cmd == "scroll":
        cmd_scroll(args.amount, args.x, args.y, args.direction)
    elif args.cmd == "press":
        cmd_press(args.key)
    elif args.cmd == "type":
        cmd_type(args.text)
    elif args.cmd == "insert-newline":
        cmd_insert_newline(args.count)
    elif args.cmd == "hotkey":
        cmd_hotkey(args.keys)
    elif args.cmd == "mouse-position":
        cmd_mouse_position()
    elif args.cmd == "screen-size":
        cmd_screen_size()
    elif args.cmd == "pixel-color":
        cmd_pixel_color(args.x, args.y)
    else:
        raise SystemExit(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
