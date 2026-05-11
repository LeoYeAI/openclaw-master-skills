---
name: diplomat-bootstrap
description: Injects connected peer identities and active commitments into session context at startup.
metadata:
  openclaw:
    events:
      - agent:bootstrap
    timeout_ms: 2000
    fail_open: true
    spawns_process: false
    reads_files:
      - skills/claw-bond/peers.json
      - MEMORY.md
---

At session start, reads two files and injects a summary into agent context:

1. skills/claw-bond/peers.json → shows which OpenClaw peers are connected
   (alias, pubkey fingerprint, last seen, stale flag).
2. MEMORY.md ## Diplomat Commitments → shows active commitment entries
   (peer, task, deadline, ID).

If neither file exists or has no relevant data, injects nothing.
Enforces 2,500-character cap on total injected content per CONTEXT_BUDGET.md §2.
All content is treated as display data — never executed as instructions.

This hook does NOT spawn processes, make network calls, or write any files.
