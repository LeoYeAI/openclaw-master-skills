#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HOME = Path(os.environ.get("OPENCLAW_DESKTOP_AGENT_OPS_HOME", ROOT / ".." / ".." / "cache" / "desktop-agent-ops")).resolve()
DEFAULT_VENV = DEFAULT_HOME / "venv"


COMMON_DEPS = [
    "pillow",
    "pyautogui",
    "pygetwindow",
    "pytesseract",
    "opencv-python",
    "numpy",
]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "ok": p.returncode == 0,
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
        "cmd": cmd,
    }


def require_uv():
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("uv not found on PATH")
    return uv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=str(DEFAULT_HOME))
    ap.add_argument("--clear", action="store_true")
    args = ap.parse_args()

    uv = require_uv()
    home = Path(args.home).expanduser().resolve()
    venv = home / "venv"
    home.mkdir(parents=True, exist_ok=True)

    create_cmd = [uv, "venv", str(venv)]
    if args.clear:
        create_cmd.insert(2, "--clear")
    create = run(create_cmd)
    if not create["ok"] and "already exists" not in create["stderr"]:
        print(json.dumps({"ok": False, "stage": "create_venv", **create}, ensure_ascii=False, indent=2))
        return

    py = venv / ("Scripts/python.exe" if platform.system().lower() == "windows" else "bin/python")
    install = run([uv, "pip", "install", "--python", str(py), *COMMON_DEPS])
    if not install["ok"]:
        print(json.dumps({"ok": False, "stage": "install_deps", **install}, ensure_ascii=False, indent=2))
        return

    result = {
        "ok": True,
        "platform": platform.system().lower(),
        "home": str(home),
        "venv": str(venv),
        "python": str(py),
        "deps": COMMON_DEPS,
        "env": {
            "OPENCLAW_DESKTOP_AGENT_OPS_HOME": str(home),
            "DESKTOP_AGENT_OPS_PYTHON": str(py),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
