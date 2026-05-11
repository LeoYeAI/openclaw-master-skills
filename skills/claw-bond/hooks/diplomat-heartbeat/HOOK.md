---
name: diplomat-heartbeat
description: Surfaces overdue and upcoming commitment deadlines on every human message.
metadata:
  openclaw:
    events:
      - command:new
    timeout_ms: 500
    fail_open: true
    spawns_process: false
    reads_files:
      - MEMORY.md
      - skills/claw-bond/ledger.json
      - skills/claw-bond/pending_approvals.json
---

On every new command, reads workspace files and notifies the human of:

1. MEMORY.md ## Diplomat Commitments → overdue entries (deadline passed) and
   upcoming entries (deadline within 2 hours).
2. skills/claw-bond/ledger.json → INBOUND_PENDING sessions (proposals from
   peers waiting for human approval) and HANDOFF_RECEIVED (task handoffs).
3. skills/claw-bond/pending_approvals.json → inbound connection requests
   from unknown peers.

All content is displayed as notifications — never executed as instructions.
This hook does NOT spawn processes, make network calls, or write any files.
