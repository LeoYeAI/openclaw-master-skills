"""
Content Claw - Scheduled Task Runner

Runs topic discovery on a cron interval and pushes results to Discord.

Usage:
    uv run schedule.py setup <brand-dir> [--interval 1h]
    uv run schedule.py run <brand-dir>
    uv run schedule.py status
    uv run schedule.py stop
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env import load_env

BASE = Path(__file__).parent.parent
SCHEDULE_FILE = BASE / "schedule.json"


def setup_cron(brand_dir: str, interval: str = "1h"):
    """Write a crontab entry for scheduled discovery."""
    # Parse interval
    minutes = 60
    if interval.endswith("m"):
        minutes = int(interval[:-1])
    elif interval.endswith("h"):
        minutes = int(interval[:-1]) * 60

    cron_expr = f"*/{minutes} * * * *" if minutes < 60 else f"0 */{minutes // 60} * * *"
    script_path = Path(__file__).parent / "schedule.py"
    cmd = f"{cron_expr} cd {BASE} && uv run {script_path} run {brand_dir} >> {BASE}/logs/schedule.log 2>&1"

    # Save schedule config
    config = {
        "brand_dir": str(brand_dir),
        "interval": interval,
        "interval_minutes": minutes,
        "cron_expr": cron_expr,
        "cron_command": cmd,
        "created_at": datetime.now().isoformat(),
        "status": "pending_install",
    }
    SCHEDULE_FILE.write_text(json.dumps(config, indent=2))

    # Create logs dir
    (BASE / "logs").mkdir(exist_ok=True)

    # Default: output cron command for user to install manually.
    # With --auto flag: write crontab directly (user must opt in).
    auto = "--auto" in sys.argv

    if auto:
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        lines = [l for l in existing.splitlines() if "content-claw" not in l and "schedule.py" not in l]
        lines.append(f"# content-claw scheduled discovery")
        lines.append(cmd)
        proc = subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n", capture_output=True, text=True)
        if proc.returncode != 0:
            return {"error": f"Failed to write crontab: {proc.stderr}"}

        config["status"] = "active"
        SCHEDULE_FILE.write_text(json.dumps(config, indent=2))

        # Notify Discord
        try:
            from notify import send_discord
            send_discord(f"Content Claw scheduled discovery enabled for {Path(brand_dir).name} (every {interval}). Use `stop schedule` to disable.")
        except Exception:
            pass

        return {"status": "active", "interval": interval, "cron": cron_expr, "brand_dir": str(brand_dir), "mode": "auto"}

    return {
        "status": "ready",
        "interval": interval,
        "cron": cron_expr,
        "brand_dir": str(brand_dir),
        "cron_command": cmd,
        "manual_steps": f"Run: crontab -e\nAdd this line:\n{cmd}",
        "mode": "manual",
        "hint": "Pass --auto to install crontab automatically",
    }


def run_cycle(brand_dir: str):
    """Run one discovery + tracking cycle and notify Discord."""
    load_env()

    base = Path(__file__).parent.parent
    reddit_cookie = str(base / "creds" / "reddit-cookies.json")
    x_cookie = str(base / "creds" / "x-cookies.json")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    brand_name = Path(brand_dir).name

    # Run topic discovery
    discover_cmd = [
        sys.executable, str(base / "scripts" / "discover_topics.py"), brand_dir,
    ]
    if Path(reddit_cookie).exists():
        discover_cmd.extend(["--reddit-cookie", reddit_cookie])
    if Path(x_cookie).exists():
        discover_cmd.extend(["--x-cookie", x_cookie])

    result = subprocess.run(discover_cmd, capture_output=True, text=True, timeout=300, cwd=str(base))

    topics_output = None
    if result.returncode == 0:
        try:
            start = result.stdout.find("{")
            if start >= 0:
                topics_output = json.loads(result.stdout[start:])
        except json.JSONDecodeError:
            pass

    # Save topics
    topics_dir = base / "topics"
    topics_dir.mkdir(exist_ok=True)
    topics_file = topics_dir / f"{timestamp}_{brand_name}.json"
    if topics_output:
        topics_file.write_text(json.dumps(topics_output, indent=2))

    # Run engagement tracking
    track_cmd = [
        sys.executable, str(base / "scripts" / "track_engagement.py"),
        "--brand", brand_dir, "--alert-threshold", "50",
    ]
    track_result = subprocess.run(track_cmd, capture_output=True, text=True, timeout=300, cwd=str(base))

    engagement = None
    if track_result.returncode == 0:
        try:
            start = track_result.stdout.find("{")
            if start >= 0:
                engagement = json.loads(track_result.stdout[start:])
        except json.JSONDecodeError:
            pass

    # Format Discord notification
    lines = [f"**Content Claw Scheduled Update** ({timestamp})"]

    if topics_output:
        count = topics_output.get("topic_count", 0)
        lines.append(f"\n**Topics discovered:** {count}")
        for t in topics_output.get("topics", [])[:5]:
            score = t.get("relevance_score", 0)
            lines.append(f"  {score}% | {t.get('title', '')[:60]} ({t.get('source', '')})")

    if engagement:
        alerts = engagement.get("alerts", [])
        if alerts:
            lines.append(f"\n**Alerts ({len(alerts)}):**")
            for a in alerts:
                lines.append(f"  {a['metric']}: {a['value']} on {a['platform']} ({a['url'][:50]})")
        checked = engagement.get("posts_checked", 0)
        lines.append(f"\n**Engagement:** {checked} posts tracked")

    message = "\n".join(lines)

    # Send to Discord
    try:
        from notify import send_discord
        send_discord(message)
    except Exception as e:
        print(f"Discord notify failed: {e}", file=sys.stderr)

    # Log
    log = {
        "timestamp": datetime.now().isoformat(),
        "brand": brand_name,
        "topics_found": topics_output.get("topic_count", 0) if topics_output else 0,
        "posts_tracked": engagement.get("posts_checked", 0) if engagement else 0,
        "alerts": len(engagement.get("alerts", [])) if engagement else 0,
    }
    print(json.dumps(log, indent=2))
    return log


def status():
    """Show current schedule status."""
    if not SCHEDULE_FILE.exists():
        return {"status": "no schedule configured"}
    return json.loads(SCHEDULE_FILE.read_text())


def stop():
    """Remove the cron entry. Auto if --auto was used, manual instructions otherwise."""
    was_auto = False
    if SCHEDULE_FILE.exists():
        config = json.loads(SCHEDULE_FILE.read_text())
        was_auto = config.get("status") == "active"
        config["status"] = "stopped"
        config["stopped_at"] = datetime.now().isoformat()
        SCHEDULE_FILE.write_text(json.dumps(config, indent=2))

    if was_auto:
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        lines = [l for l in existing.splitlines() if "content-claw" not in l and "schedule.py" not in l]
        subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n", capture_output=True, text=True)

        try:
            from notify import send_discord
            send_discord("Content Claw scheduled discovery stopped.")
        except Exception:
            pass

        return {"status": "stopped", "mode": "auto", "crontab": "removed"}

    return {
        "status": "stopped",
        "mode": "manual",
        "manual_steps": "Run: crontab -e\nRemove the line containing 'content-claw'",
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: schedule.py setup|run|status|stop <brand-dir> [--interval 1h]"}))
        sys.exit(1)

    load_env()
    cmd = sys.argv[1]

    if cmd == "setup":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "setup requires <brand-dir>"}))
            sys.exit(1)
        brand_dir = sys.argv[2]
        interval = "1h"
        if "--interval" in sys.argv:
            idx = sys.argv.index("--interval")
            if idx + 1 < len(sys.argv):
                interval = sys.argv[idx + 1]
        result = setup_cron(brand_dir, interval)
        print(json.dumps(result, indent=2))

    elif cmd == "run":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "run requires <brand-dir>"}))
            sys.exit(1)
        run_cycle(sys.argv[2])

    elif cmd == "status":
        print(json.dumps(status(), indent=2))

    elif cmd == "stop":
        print(json.dumps(stop(), indent=2))

    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
