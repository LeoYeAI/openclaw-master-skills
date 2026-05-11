---
name: feishu-evolver-wrapper
description: Feishu-integrated wrapper for the capability-evolver. Manages the evolution loop lifecycle (start/stop/ensure), sends rich Feishu card reports, and provides dashboard visualization. Use when running evolver with Feishu reporting or when managing the evolution daemon.
---

# Feishu Evolver Wrapper

A lightweight wrapper for the `capability-evolver` skill.
It injects the Feishu reporting environment variables (`EVOLVE_REPORT_TOOL`) to enable rich card reporting in the Master's environment.

## Usage

```bash
# Run the evolution loop
node skills/feishu-evolver-wrapper/index.js

# Generate Evolution Dashboard (Markdown)
node skills/feishu-evolver-wrapper/visualize_dashboard.js

# Lifecycle Management (Start/Stop/Status/Ensure)
node skills/feishu-evolver-wrapper/lifecycle.js status
```

## Architecture

- **Evolution Loop**: Runs the GEP evolution cycle with Feishu reporting.
- **Dashboard**: Visualizing metrics and history from `assets/gep/events.jsonl`.
- **Export History**: Exports raw history to Feishu Docs.
- **Watchdog**: Managed via OpenClaw Cron job `evolver_watchdog_robust` (runs `lifecycle.js ensure` every 10 min).
  - Replaces fragile system crontab logic.
  - Ensures the loop restarts if it crashes or hangs.
