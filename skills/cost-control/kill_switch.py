#!/usr/bin/env python3
"""
Cost Control System — Manual Kill Switch
=========================================
Emergency stop mechanism for API-calling applications.

Usage:
    python3 kill_switch.py enable    # Stop all API calls
    python3 kill_switch.py disable   # Resume API calls
    python3 kill_switch.py status    # Check if kill switch is active

Copyright © 2026 Shadow Rose
License: MIT
"""
import os
import sys
from pathlib import Path


# Kill switch flag file
KILL_SWITCH_FILE = Path(__file__).parent / "state" / "KILL_SWITCH"


def enable():
    """Enable kill switch — app will stop making API calls."""
    KILL_SWITCH_FILE.parent.mkdir(exist_ok=True)
    KILL_SWITCH_FILE.touch()
    
    print(f"🛑 KILL SWITCH ENABLED")
    print(f"Application will stop API calls on next check.")
    print(f"File: {KILL_SWITCH_FILE}")


def disable():
    """Disable kill switch — app will resume normal operation."""
    if KILL_SWITCH_FILE.exists():
        KILL_SWITCH_FILE.unlink()
        print(f"✅ KILL SWITCH DISABLED")
        print(f"Application will resume normal operation.")
    else:
        print(f"ℹ️ Kill switch was not active.")


def status():
    """Check kill switch status."""
    if KILL_SWITCH_FILE.exists():
        print(f"🛑 KILL SWITCH: ACTIVE")
        print(f"API calls are STOPPED.")
        print(f"Run: python3 kill_switch.py disable")
        return 1
    else:
        print(f"✅ KILL SWITCH: INACTIVE")
        print(f"API calls are ENABLED.")
        return 0


def is_active():
    """Check if kill switch is active (for application to call)."""
    return KILL_SWITCH_FILE.exists()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 kill_switch.py {enable|disable|status}")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "enable":
        enable()
    elif cmd == "disable":
        disable()
    elif cmd == "status":
        sys.exit(status())
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 kill_switch.py {enable|disable|status}")
        sys.exit(1)
