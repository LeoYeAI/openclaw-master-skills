#!/usr/bin/env python3
import importlib.util
import json
import os
import platform
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DESKTOP_OPS = ROOT / 'desktop_ops.py'
PY = os.environ.get('DESKTOP_AGENT_OPS_PYTHON', 'python3')
PERMISSION_HOME = Path(os.environ.get("OPENCLAW_DESKTOP_AGENT_OPS_HOME", Path.home() / ".openclaw-desktop-agent-ops")).expanduser().resolve()
PERMISSION_STATE = PERMISSION_HOME / "permissions.json"


def check_mod(name):
    return importlib.util.find_spec(name) is not None


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'ok': p.returncode == 0,
        'code': p.returncode,
        'stdout': p.stdout.strip(),
        'stderr': p.stderr.strip(),
    }


report = {
    'platform': platform.system().lower(),
    'python': PY,
    'deps': {
        'pyautogui': run([PY, '-c', 'import pyautogui; print("ok")'])['ok'],
        'PIL': run([PY, '-c', 'from PIL import Image; print("ok")'])['ok'],
        'pytesseract': run([PY, '-c', 'import pytesseract; print("ok")'])['ok'],
        'cv2': run([PY, '-c', 'import cv2; print("ok")'])['ok'],
        'tesseract_bin': shutil.which('tesseract') is not None,
    },
    'permissions': {
        'state_file': str(PERMISSION_STATE),
        'completed': False,
    },
    'checks': {}
}

try:
    if PERMISSION_STATE.exists():
        state = json.loads(PERMISSION_STATE.read_text())
        report['permissions']['completed'] = bool(state.get('completed'))
        report['permissions']['state'] = state
except Exception:
    report['permissions']['error'] = 'permission_state_read_failed'

report['checks']['frontmost'] = run([PY, str(DESKTOP_OPS), 'frontmost'])
report['checks']['screenshot'] = run([PY, str(DESKTOP_OPS), 'screenshot'])
report['checks']['mouse_position_before'] = run([PY, str(DESKTOP_OPS), 'mouse-position'])
report['checks']['move'] = run([PY, str(DESKTOP_OPS), 'move', '--x', '400', '--y', '400', '--duration', '0.1'])
report['checks']['mouse_position_after'] = run([PY, str(DESKTOP_OPS), 'mouse-position'])

print(json.dumps(report, ensure_ascii=False, indent=2))
