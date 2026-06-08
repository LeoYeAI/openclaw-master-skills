#!/usr/bin/env python3
import argparse
import json
import os
import platform
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DESKTOP_OPS = ROOT / "desktop_ops.py"
PY = os.environ.get("DESKTOP_AGENT_OPS_PYTHON", "python3")

DEFAULT_HOME = Path(os.environ.get("OPENCLAW_DESKTOP_AGENT_OPS_HOME", Path.home() / ".openclaw-desktop-agent-ops")).expanduser().resolve()
DEFAULT_STATE = DEFAULT_HOME / "permissions.json"


def jprint(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    stdout_text = p.stdout.strip()
    stderr_text = p.stderr.strip()

    # Parse JSON from stdout to get the real ok status.
    # desktop_ops.py outputs JSON with an "ok" field that reflects
    # whether the operation actually succeeded (e.g. permission granted).
    # We must NOT rely solely on the process return code, because
    # desktop_ops may print {"ok": false, ...} but still exit 0.
    json_ok = None
    json_hint = None
    if stdout_text:
        try:
            parsed = json.loads(stdout_text)
            json_ok = parsed.get("ok")
            json_hint = parsed.get("hint")
        except (json.JSONDecodeError, TypeError):
            pass

    # Determine actual success: prefer JSON ok field, fall back to return code
    if json_ok is not None:
        actual_ok = bool(json_ok)
    else:
        actual_ok = p.returncode == 0

    result = {
        "ok": actual_ok,
        "code": p.returncode,
        "stdout": stdout_text,
        "stderr": stderr_text,
        "cmd": cmd,
    }
    if json_hint:
        result["hint"] = json_hint
    return result


def load_state(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def save_state(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def macos_steps(python_exec):
    steps = {}
    steps["frontmost"] = run([python_exec, str(DESKTOP_OPS), "frontmost"])
    steps["screenshot"] = run([python_exec, str(DESKTOP_OPS), "screenshot"])
    steps["focus_finder"] = run([python_exec, str(DESKTOP_OPS), "focus-app", "--name", "Finder"])
    steps["list_apps"] = run([python_exec, str(DESKTOP_OPS), "list-apps"])
    return steps


def windows_steps(python_exec):
    steps = {}
    steps["frontmost"] = run([python_exec, str(DESKTOP_OPS), "frontmost"])
    steps["screenshot"] = run([python_exec, str(DESKTOP_OPS), "screenshot"])
    return steps


def linux_steps(python_exec):
    steps = {}
    steps["frontmost"] = run([python_exec, str(DESKTOP_OPS), "frontmost"])
    steps["screenshot"] = run([python_exec, str(DESKTOP_OPS), "screenshot"])
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", default=PY)
    ap.add_argument("--state-file", default=str(DEFAULT_STATE))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--open-settings", action="store_true")
    args = ap.parse_args()

    state_path = Path(args.state_file).expanduser().resolve()
    existing = load_state(state_path)
    system = platform.system().lower()

    if args.check:
        jprint({
            "ok": True,
            "platform": system,
            "state_file": str(state_path),
            "state": existing or {"completed": False},
        })
        return

    if existing and existing.get("completed") and not args.force and existing.get("platform") == system:
        jprint({
            "ok": True,
            "platform": system,
            "state_file": str(state_path),
            "already_completed": True,
            "state": existing,
            "instructions": "Permissions already recorded. Use --force to re-run prompts.",
        })
        return

    if system == "darwin":
        instructions = [
            "A permission prompt may appear for Screen Recording, Accessibility, and Automation.",
            "Please click Allow/OK on each prompt so future runs can operate automatically.",
            "If a prompt does not appear, open System Settings and grant the permission manually.",
        ]
    elif system == "windows":
        instructions = [
            "On Windows, ensure your terminal is running with appropriate permissions.",
            "If screenshots or input automation fail, try running the terminal as Administrator.",
        ]
    elif system == "linux":
        instructions = [
            "On Linux (X11), ensure xdotool and wmctrl are installed for window management.",
            "If using Wayland, some automation features may be limited.",
        ]
    else:
        instructions = [
            "Ensure your system allows screen capture and input automation.",
        ]

    host = os.environ.get("TERM_PROGRAM")
    if not host:
        try:
            ppid = os.getppid()
            host_probe = subprocess.run(["/bin/ps", "-p", str(ppid), "-o", "comm="], capture_output=True, text=True)
            if host_probe.returncode == 0:
                host = host_probe.stdout.strip()
        except Exception:
            host = None

    if system == "darwin":
        steps = macos_steps(args.python)
    elif system == "windows":
        steps = windows_steps(args.python)
    elif system == "linux":
        steps = linux_steps(args.python)
    else:
        jprint({"ok": False, "error": f"unsupported_platform:{system}"})
        return

    completed = all(step.get("ok") for step in steps.values())
    failed_steps = [name for name, step in steps.items() if not step.get("ok")]
    hints = [step.get("hint") for step in steps.values() if step.get("hint")]

    payload = {
        "completed": bool(completed),
        "platform": system,
        "timestamp": int(time.time()),
        "steps": steps,
    }
    if failed_steps:
        payload["failed_steps"] = failed_steps
    if hints:
        payload["hints"] = list(set(hints))

    save_state(state_path, payload)

    settings_actions = []
    settings_opened_ok = True
    if system == "darwin" and args.open_settings:
        # Try "System Settings" first (macOS Ventura 13+), fall back to
        # "System Preferences" (macOS Monterey 12 and earlier), then
        # fall back to the bundle ID which works on all versions.
        app_opened = False
        for app_name in ["System Settings", "System Preferences"]:
            result = run(["/usr/bin/open", "-a", app_name])
            if result.get("ok"):
                settings_actions.append(result)
                app_opened = True
                break
            settings_actions.append(result)
        if not app_opened:
            # Last resort: use bundle identifier
            bundle_result = run(["/usr/bin/open", "-b", "com.apple.systempreferences"])
            settings_actions.append(bundle_result)
            app_opened = bundle_result.get("ok")

        # Try privacy deep-link URLs (work on macOS 13+)
        privacy_urls = [
            "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation",
        ]
        for url in privacy_urls:
            url_result = run(["/usr/bin/open", url])
            settings_actions.append(url_result)

        settings_opened_ok = app_opened
        if not settings_opened_ok:
            instructions.append(
                "MANUAL ACTION REQUIRED: Could not open System Settings automatically. "
                "Please open System Settings > Privacy & Security and grant "
                "Screen Recording, Accessibility, and Automation permissions "
                "to your terminal application."
            )

    jprint({
        "ok": bool(completed),
        "platform": system,
        "state_file": str(state_path),
        "completed": bool(completed),
        "steps": steps,
        "failed_steps": failed_steps,
        "hints": list(set(hints)) if hints else [],
        "host_process": host,
        "settings_opened": settings_actions,
        "instructions": instructions,
    })


if __name__ == "__main__":
    main()
