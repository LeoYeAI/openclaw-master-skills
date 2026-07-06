#!/usr/bin/env python3
"""
Cost Control System — External Watchdog (Tier 3 Kill Switch)
=============================================================
Independent process that monitors cost_tracker.json and kills the main
process if cost thresholds are exceeded. Last line of defense against
runaway API spend.

Deploy via cron (run every 2 minutes):
    */2 * * * * cd /your/project && python3 cost_watchdog.py >> logs/watchdog.log 2>&1

Copyright © 2026 Shadow Rose
License: MIT
"""
import os
import json
import time
import signal
import sys
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION — Customize for your use case
# ═══════════════════════════════════════════════════════════════

# Tier 3 thresholds (higher than main tracker's Tier 2 — last resort)
KILL_THRESHOLD_HOURLY = 12.00   # $12/hour → kill process
KILL_THRESHOLD_DAILY = 30.00    # $30/day → kill process

# State files (must match your main tracker config)
COST_TRACKER_FILE = "state/cost_tracker.json"
PID_FILE = "state/app.pid"  # Your application's PID file
COST_EMERGENCY_FLAG = "state/cost_emergency.flag"
MAINTENANCE_FILE = "state/MAINTENANCE"  # Manual override — don't kill


# ═══════════════════════════════════════════════════════════════
# IMPLEMENTATION — Don't modify unless you know what you're doing
# ═══════════════════════════════════════════════════════════════

def log(msg):
    """Log to stdout (cron redirects to log file)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} [WATCHDOG] {msg}", flush=True)


def read_cost_tracker():
    """Read cost_tracker.json. Returns dict or None on error."""
    if not os.path.exists(COST_TRACKER_FILE):
        return None
    
    try:
        with open(COST_TRACKER_FILE) as f:
            return json.load(f)
    except Exception as e:
        log(f"WARNING: Failed to read {COST_TRACKER_FILE}: {e}")
        return None


def get_process_pid():
    """Read process PID from PID file."""
    if not os.path.exists(PID_FILE):
        return None
    
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        
        # Verify process exists
        os.kill(pid, 0)  # Raises OSError if process doesn't exist
        return pid
    except (ValueError, OSError):
        return None


def kill_process(pid, reason):
    """Kill the process and create emergency flag.
    
    Returns True if successfully killed, False otherwise.
    """
    try:
        log(f"🚨 KILLING PROCESS (PID {pid}): {reason}")
        
        # Write emergency flag BEFORE killing (prevents restart)
        with open(COST_EMERGENCY_FLAG, "w") as f:
            f.write(json.dumps({
                "reason": reason,
                "timestamp": time.time(),
                "timestamp_iso": datetime.now().isoformat(),
                "killed_pid": pid,
                "killed_by": "external_watchdog",
            }, indent=2))
        
        log(f"✅ Emergency flag written: {COST_EMERGENCY_FLAG}")
        
        # Kill process (SIGTERM first, then SIGKILL)
        os.kill(pid, signal.SIGTERM)
        time.sleep(5)
        
        # Check if still alive
        try:
            os.kill(pid, 0)
            log(f"Process still alive after SIGTERM — sending SIGKILL")
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass  # Already dead
        
        log(f"✅ Process killed. Manual intervention required to resume.")
        return True
    
    except Exception as e:
        log(f"❌ Failed to kill process: {e}")
        return False


def main():
    """Main watchdog logic."""
    
    # Check if maintenance mode (manual override — don't interfere)
    if os.path.exists(MAINTENANCE_FILE):
        # Silent in maintenance mode (no spam in logs)
        sys.exit(0)
    
    # Check if emergency flag already exists (process already killed)
    if os.path.exists(COST_EMERGENCY_FLAG):
        # Silent when emergency flag is set (manual intervention pending)
        sys.exit(0)
    
    # Read cost tracker state
    cost_data = read_cost_tracker()
    if not cost_data:
        log("WARNING: No cost_tracker.json found — app may not be running")
        sys.exit(0)
    
    # Extract costs
    cost_hourly = cost_data.get("cost_1hour", 0)
    cost_daily = cost_data.get("cost_daily", 0)
    caution_mode = cost_data.get("caution_mode", False)
    emergency_mode = cost_data.get("emergency_mode", False)
    
    # Check thresholds
    kill_reason = None
    
    if cost_hourly >= KILL_THRESHOLD_HOURLY:
        kill_reason = f"Hourly cost ${cost_hourly:.2f} >= ${KILL_THRESHOLD_HOURLY:.2f}"
    elif cost_daily >= KILL_THRESHOLD_DAILY:
        kill_reason = f"Daily cost ${cost_daily:.2f} >= ${KILL_THRESHOLD_DAILY:.2f}"
    
    if kill_reason:
        log(f"🚨 COST THRESHOLD EXCEEDED: {kill_reason}")
        
        pid = get_process_pid()
        if pid:
            if kill_process(pid, kill_reason):
                sys.exit(0)
            else:
                log(f"❌ Failed to kill process — manual intervention required")
                sys.exit(1)
        else:
            log(f"WARNING: Threshold exceeded but process not running (no PID)")
            
            # Write flag anyway to prevent restart
            with open(COST_EMERGENCY_FLAG, "w") as f:
                f.write(json.dumps({
                    "reason": kill_reason,
                    "timestamp": time.time(),
                    "timestamp_iso": datetime.now().isoformat(),
                    "killed_pid": None,
                    "killed_by": "external_watchdog",
                }, indent=2))
            
            sys.exit(0)
    else:
        # Normal operation — only log if emergency/caution mode active
        if emergency_mode:
            log(f"⚠️ Emergency mode active | Hourly: ${cost_hourly:.2f} | "
                f"Daily: ${cost_daily:.2f}")
        elif caution_mode:
            log(f"💰 Caution mode active | Hourly: ${cost_hourly:.2f} | "
                f"Daily: ${cost_daily:.2f}")
        # Otherwise silent (no spam in logs)
        sys.exit(0)


if __name__ == "__main__":
    main()
