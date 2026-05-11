---
name: diplomat-gateway
description: Checks if the relay listener is running and notifies the agent if it needs to be started.
metadata:
  openclaw:
    events:
      - gateway:startup
    timeout_ms: 5000
    fail_open: true
    spawns_process: false
    reads_files:
      - skills/claw-bond/listener.pid
    writes_files:
      - skills/claw-bond/listener.start_requested
---

Checks whether skills/claw-bond/listener.py is already running by reading the PID
file (skills/claw-bond/listener.pid) and sending signal 0 (existence check only).

If the listener IS running → logs and returns silently.
If the listener is NOT running → writes a flag file (listener.start_requested) and
injects a one-line instruction into the agent session so the user or agent can start
listener.py manually in terminal.

This hook does NOT spawn any process, import child_process, or execute shell commands.
It only reads/writes files and injects a text notification. The actual listener process
is started by the user or agent running `python3 listener.py &` in terminal.

fail_open: true — if the listener is not running the user gets a nudge; this is not
a hard failure that should block the gateway.
