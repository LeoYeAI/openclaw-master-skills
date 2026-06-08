#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = os.environ.get("DESKTOP_AGENT_OPS_PYTHON", "python3")


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": p.returncode == 0, "code": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--candidate-index", type=int, default=0)
    ap.add_argument("--delay-ms", type=int, default=800)
    ap.add_argument("--allow-pointer-mismatch", action="store_true")
    ap.add_argument("--verify-diff", action="store_true")
    ap.add_argument("--diff-threshold", type=float, default=0.02)
    args = ap.parse_args()

    desktop_ops = ROOT / "desktop_ops.py"
    target_report = ROOT / "target_report.py"
    region_diff = ROOT / "region_diff.py"

    try:
        report = run_json([PY, str(target_report), "--app", args.app, "--label", args.label, "--python", PY])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"target_report_failed:{exc}"}))
        return
    candidate = report["candidates"][args.candidate_index]

    pre = tempfile.mktemp(prefix="click-pre-", suffix=".png")
    post = tempfile.mktemp(prefix="click-post-", suffix=".png")

    try:
        move = run_json([PY, str(desktop_ops), "move", "--x", str(candidate["x"]), "--y", str(candidate["y"])])
        mouse = run_json([PY, str(desktop_ops), "mouse-position"])
        pre_cap = run_json([PY, str(desktop_ops), "screenshot", "--output", pre, "--with-cursor"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"preflight_failed:{exc}"}))
        return

    pointer_matches = mouse.get("x") == candidate.get("x") and mouse.get("y") == candidate.get("y")
    require_pointer_match = not args.allow_pointer_mismatch
    if require_pointer_match and not pointer_matches:
        out = {
            "ok": False,
            "error": "pointer_mismatch",
            "report": report,
            "selected_candidate": candidate,
            "move": move,
            "mouse_after_move": mouse,
            "pointer_matches_candidate": pointer_matches,
            "pre_capture": pre_cap,
            "skipped_click": True,
        }
        print(json.dumps(out, ensure_ascii=False))
        return

    try:
        click = run_json([PY, str(desktop_ops), "click", "--x", str(candidate["x"]), "--y", str(candidate["y"])])
        delay = args.delay_ms / 1000.0
        import time as _time
        _time.sleep(delay)
        post_cap = run_json([PY, str(desktop_ops), "screenshot", "--output", post, "--with-cursor"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"click_failed:{exc}"}))
        return

    diff_out = None
    if args.verify_diff:
        try:
            diff_out = run_json([
                PY, str(region_diff),
                "--before", pre,
                "--after", post,
                "--app", args.app,
                "--region-label", args.label,
                "--threshold", str(args.diff_threshold),
                "--python", PY,
            ])
        except Exception as exc:
            diff_out = {"ok": False, "error": f"diff_failed:{exc}"}

    ok = bool(move.get("ok") and mouse.get("ok") and pre_cap.get("ok") and click.get("ok") and post_cap.get("ok"))
    if require_pointer_match:
        ok = ok and pointer_matches
    if args.verify_diff:
        ok = ok and bool(diff_out and diff_out.get("ok") and diff_out.get("changed"))

    out = {
        "ok": ok,
        "report": report,
        "selected_candidate": candidate,
        "move": move,
        "mouse_after_move": mouse,
        "pointer_matches_candidate": pointer_matches,
        "pre_capture": pre_cap,
        "click": click,
        "post_capture": post_cap,
        "diff": diff_out,
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
