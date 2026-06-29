#!/usr/bin/env python3
"""
Generate cron job configuration for proactive research monitoring.

Outputs JSON that the agent can use with OpenClaw's cron tool.
Does NOT modify crontab directly.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, get_settings

SKILL_DIR = Path(__file__).parent.parent
MONITOR_SCRIPT = SKILL_DIR / "scripts" / "monitor.py"
DIGEST_SCRIPT = SKILL_DIR / "scripts" / "digest.py"


def generate_cron_config(settings: dict) -> dict:
    """Generate cron configuration as JSON for the agent."""
    
    digest_day = settings.get("digest_day", "sunday")
    digest_time = settings.get("digest_time", "18:00")
    hour, minute = digest_time.split(":")
    
    day_map = {
        "sunday": "0", "monday": "1", "tuesday": "2", "wednesday": "3",
        "thursday": "4", "friday": "5", "saturday": "6"
    }
    day_num = day_map.get(digest_day.lower(), "0")
    
    return {
        "jobs": [
            {
                "name": "topic-monitor-hourly",
                "description": "Hourly topic check",
                "schedule": "0 * * * *",
                "command": f"cd {SKILL_DIR} && python3 {MONITOR_SCRIPT} --frequency hourly"
            },
            {
                "name": "topic-monitor-daily",
                "description": "Daily topic check (9 AM)",
                "schedule": "0 9 * * *",
                "command": f"cd {SKILL_DIR} && python3 {MONITOR_SCRIPT} --frequency daily"
            },
            {
                "name": "topic-monitor-weekly",
                "description": "Weekly topic check (Sunday 9 AM)",
                "schedule": "0 9 * * 0",
                "command": f"cd {SKILL_DIR} && python3 {MONITOR_SCRIPT} --frequency weekly"
            },
            {
                "name": "topic-monitor-digest",
                "description": f"Weekly digest ({digest_day} {digest_time})",
                "schedule": f"{minute} {hour} * * {day_num}",
                "command": f"cd {SKILL_DIR} && python3 {DIGEST_SCRIPT} --send"
            }
        ],
        "note": "Use these with OpenClaw's cron tool. Do NOT run setup_cron.py --auto."
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate cron config for topic monitoring")
    parser.add_argument("--json", action="store_true", default=True, help="Output as JSON (default)")
    
    parser.parse_args()
    
    try:
        config = load_config()
        settings = get_settings()
    except FileNotFoundError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    
    result = generate_cron_config(settings)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
