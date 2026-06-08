#!/usr/bin/env python3
"""
Smoke test for desktop-agent-ops readiness.

Verifies: doctor, screen-size, mouse-move, pixel-color, screenshot.
Uses a two-step move (corner then target) to guarantee the cursor
actually moved, even on Retina/HiDPI displays with coordinate scaling.
"""

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESKTOP_OPS = ROOT / "desktop_ops.py"
DOCTOR = ROOT / "doctor.py"
PY = os.environ.get("DESKTOP_AGENT_OPS_PYTHON", "python3")

# Two targets far apart so we can verify the move actually happens.
# Even if cliclick reports scaled coordinates, moving from corner
# to center guarantees different readback values.
CORNER = {"x": 50, "y": 50}
TARGET = {"x": 400, "y": 400}


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "ok": p.returncode == 0,
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
        "cmd": cmd,
    }


def parse_json(stdout):
    try:
        return json.loads(stdout)
    except Exception:
        return None


def main():
    report = {
        "python": PY,
        "steps": {},
    }

    # Basic checks
    report["steps"]["doctor"] = run([PY, str(DESKTOP_OPS), "frontmost"])
    report["steps"]["screen_size"] = run([PY, str(DESKTOP_OPS), "screen-size"])

    # Two-step move test: corner first, then target
    report["steps"]["move_to_corner"] = run([
        PY, str(DESKTOP_OPS), "move",
        "--x", str(CORNER["x"]), "--y", str(CORNER["y"]),
    ])
    report["steps"]["mouse_at_corner"] = run([PY, str(DESKTOP_OPS), "mouse-position"])

    report["steps"]["move_to_target"] = run([
        PY, str(DESKTOP_OPS), "move",
        "--x", str(TARGET["x"]), "--y", str(TARGET["y"]),
    ])
    report["steps"]["mouse_at_target"] = run([PY, str(DESKTOP_OPS), "mouse-position"])

    # Extra functional checks
    report["steps"]["pixel_color"] = run([
        PY, str(DESKTOP_OPS), "pixel-color",
        "--x", str(TARGET["x"]), "--y", str(TARGET["y"]),
    ])
    report["steps"]["screenshot"] = run([PY, str(DESKTOP_OPS), "screenshot"])

    # Verify move
    pos_corner = parse_json(report["steps"]["mouse_at_corner"]["stdout"])
    pos_target = parse_json(report["steps"]["mouse_at_target"]["stdout"])

    if pos_corner and pos_target:
        corner_xy = (pos_corner.get("x"), pos_corner.get("y"))
        target_xy = (pos_target.get("x"), pos_target.get("y"))
        # The cursor must have moved between the two readbacks
        position_changed = corner_xy != target_xy
        move_ok = position_changed
    else:
        corner_xy = None
        target_xy = None
        position_changed = False
        move_ok = False

    all_ok = all(step["ok"] for step in report["steps"].values()) and bool(move_ok)

    report["ready"] = all_ok
    report["move_verified"] = bool(move_ok)
    report["move_details"] = {
        "corner": {"sent": CORNER, "read": {"x": corner_xy[0], "y": corner_xy[1]} if corner_xy else None},
        "target": {"sent": TARGET, "read": {"x": target_xy[0], "y": target_xy[1]} if target_xy else None},
        "position_changed": position_changed,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
