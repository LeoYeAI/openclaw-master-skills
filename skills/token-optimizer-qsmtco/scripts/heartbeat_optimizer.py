#!/usr/bin/env python3
"""
Heartbeat optimizer - Manages efficient heartbeat intervals and batched checks.
Reduces API calls by tracking check timestamps and batching operations.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path.home() / ".openclaw/workspace/memory/heartbeat-state.json"

DEFAULT_INTERVALS = {
    "email": 3600,      # 1 hour
    "calendar": 7200,   # 2 hours
    "weather": 14400,   # 4 hours
    "social": 7200,     # 2 hours
    "monitoring": 1800  # 30 minutes
}

QUIET_HOURS = {
    "start": 23,  # 11 PM
    "end": 8      # 8 AM
}

def load_state():
    """Load heartbeat tracking state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "lastChecks": {},
        "intervals": DEFAULT_INTERVALS.copy(),
        "skipCount": 0
    }

def save_state(state):
    """Save heartbeat tracking state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def is_quiet_hours(hour=None):
    """Check if current time is during quiet hours."""
    if hour is None:
        hour = datetime.now().hour
    
    start = QUIET_HOURS["start"]
    end = QUIET_HOURS["end"]
    
    if start > end:  # Wraps midnight
        return hour >= start or hour < end
    else:
        return start <= hour < end

def should_check(check_type, force=False):
    """Determine if a check should run based on interval.
    
    Args:
        check_type: Type of check (email, calendar, etc.)
        force: Force check regardless of interval
    
    Returns:
        dict with decision and reasoning
    """
    if force:
        return {
            "should_check": True,
            "reason": "Forced check",
            "next_check": None
        }
    
    # Skip all checks during quiet hours
    if is_quiet_hours():
        return {
            "should_check": False,
            "reason": "Quiet hours (23:00-08:00)",
            "next_check": "08:00"
        }
    
    state = load_state()
    now = datetime.now()
    
    # Get last check time
    last_check_ts = state["lastChecks"].get(check_type)
    if not last_check_ts:
        # Never checked before
        return {
            "should_check": True,
            "reason": "First check",
            "next_check": None
        }
    
    last_check = datetime.fromisoformat(last_check_ts)
    interval = state["intervals"].get(check_type, DEFAULT_INTERVALS.get(check_type, 3600))
    next_check = last_check + timedelta(seconds=interval)
    
    if now >= next_check:
        return {
            "should_check": True,
            "reason": f"Interval elapsed ({interval}s)",
            "next_check": None
        }
    else:
        remaining = (next_check - now).total_seconds()
        return {
            "should_check": False,
            "reason": f"Too soon ({int(remaining / 60)}min remaining)",
            "next_check": next_check.strftime("%H:%M")
        }

def record_check(check_type):
    """Record that a check was performed."""
    state = load_state()
    state["lastChecks"][check_type] = datetime.now().isoformat()
    save_state(state)

def plan_heartbeat(checks=None):
    """Plan which checks should run in next heartbeat.
    
    Args:
        checks: List of check types to consider (default: all)
    
    Returns:
        dict with planned checks and skip decision
    """
    if checks is None:
        checks = list(DEFAULT_INTERVALS.keys())
    
    planned = []
    skipped = []
    
    for check in checks:
        decision = should_check(check)
        if decision["should_check"]:
            planned.append({
                "type": check,
                "reason": decision["reason"]
            })
        else:
            skipped.append({
                "type": check,
                "reason": decision["reason"],
                "next_check": decision["next_check"]
            })
    
    return {
        "planned": planned,
        "skipped": skipped,
        "should_run": len(planned) > 0,
        "can_skip": len(planned) == 0
    }

def update_interval(check_type, new_interval_seconds):
    """Update check interval for a specific check type.
    
    Args:
        check_type: Type of check
        new_interval_seconds: New interval in seconds
    """
    state = load_state()
    state["intervals"][check_type] = new_interval_seconds
    save_state(state)
    return {
        "check_type": check_type,
        "old_interval": DEFAULT_INTERVALS.get(check_type),
        "new_interval": new_interval_seconds
    }

def main():
    """CLI interface for heartbeat optimizer."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: heartbeat_optimizer.py [plan|check|record|interval|reset]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "plan":
        # Plan next heartbeat
        checks = sys.argv[2:] if len(sys.argv) > 2 else None
        result = plan_heartbeat(checks)
        print(json.dumps(result, indent=2))
    
    elif command == "check":
        # Check if specific type should run
        if len(sys.argv) < 3:
            print("Usage: heartbeat_optimizer.py check <type>")
            sys.exit(1)
        check_type = sys.argv[2]
        force = len(sys.argv) > 3 and sys.argv[3] == "--force"
        result = should_check(check_type, force)
        print(json.dumps(result, indent=2))
    
    elif command == "record":
        # Record that a check was performed
        if len(sys.argv) < 3:
            print("Usage: heartbeat_optimizer.py record <type>")
            sys.exit(1)
        check_type = sys.argv[2]
        record_check(check_type)
        print(f"Recorded check: {check_type}")
    
    elif command == "interval":
        # Update interval
        if len(sys.argv) < 4:
            print("Usage: heartbeat_optimizer.py interval <type> <seconds>")
            sys.exit(1)
        check_type = sys.argv[2]
        interval = int(sys.argv[3])
        result = update_interval(check_type, interval)
        print(json.dumps(result, indent=2))
    
    elif command == "reset":
        # Reset state
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        print("Heartbeat state reset.")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
