#!/usr/bin/env python3
"""
Idle watchdog for agent-browser daemon.
Stops the daemon after inactivity or when the owner PID exits.
"""

import json
import os
import time
from pathlib import Path

from agent_browser_client import AgentBrowserClient
from config import (
    AGENT_BROWSER_ACTIVITY_FILE,
    AGENT_BROWSER_IDLE_TIMEOUT_SECONDS,
    AGENT_BROWSER_WATCHDOG_INTERVAL_SECONDS,
    AGENT_BROWSER_WATCHDOG_PID_FILE,
    DEFAULT_SESSION_ID,
)


def pid_is_alive(pid: int) -> bool:
    """Return True if the PID exists."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_last_activity(path: Path):
    """Return (timestamp, owner_pid) if available."""
    if not path.exists():
        return None, None

    try:
        payload = json.loads(path.read_text())
    except Exception:
        return None, None

    timestamp = payload.get("timestamp")
    owner_pid = payload.get("owner_pid")
    return timestamp, owner_pid


def resolve_owner_pid(current_owner_pid, file_owner_pid):
    """Prefer the latest owner PID from the activity file."""
    if file_owner_pid is not None:
        try:
            return int(file_owner_pid)
        except Exception:
            return current_owner_pid
    return current_owner_pid


def should_shutdown(last_activity, idle_timeout: int, owner_pid):
    """Determine whether the daemon should be stopped."""
    if owner_pid is not None and not pid_is_alive(int(owner_pid)):
        return True

    if last_activity is None:
        return False

    return (time.time() - float(last_activity)) >= idle_timeout


def write_pid_file():
    """Write watchdog PID to disk."""
    try:
        AGENT_BROWSER_WATCHDOG_PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        AGENT_BROWSER_WATCHDOG_PID_FILE.write_text(str(os.getpid()))
    except Exception:
        pass


def clear_pid_file():
    """Remove watchdog PID file if present."""
    try:
        if AGENT_BROWSER_WATCHDOG_PID_FILE.exists():
            AGENT_BROWSER_WATCHDOG_PID_FILE.unlink()
    except Exception:
        pass


def main():
    write_pid_file()

    session_id = os.environ.get("AGENT_BROWSER_SESSION", DEFAULT_SESSION_ID)
    owner_pid_env = os.environ.get("AGENT_BROWSER_OWNER_PID")
    owner_pid = None
    if owner_pid_env and owner_pid_env.isdigit():
        owner_pid = int(owner_pid_env)

    try:
        while True:
            last_activity, file_owner_pid = read_last_activity(AGENT_BROWSER_ACTIVITY_FILE)
            owner_pid = resolve_owner_pid(owner_pid, file_owner_pid)

            if should_shutdown(last_activity, AGENT_BROWSER_IDLE_TIMEOUT_SECONDS, owner_pid):
                client = AgentBrowserClient(session_id=session_id)
                client.shutdown()
                return

            time.sleep(AGENT_BROWSER_WATCHDOG_INTERVAL_SECONDS)
    finally:
        clear_pid_file()


if __name__ == "__main__":
    main()
