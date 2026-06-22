# agi-farm Dashboard Reference

Live ops room for your AGI team. Serves at `http://localhost:8080` by default.

## Launch

```bash
python3 ~/.openclaw/skills/agi-farm/dashboard.py \
  --workspace ~/.openclaw/workspace \
  --port 8080
```

Flags:

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | 8080 | HTTP port |
| `--workspace` | `~/.openclaw/workspace` | Workspace path |
| `--no-browser` | off | Skip auto-open |

## Architecture

File-watcher edition — **instant push on any workspace file change**, no polling.

```
workspace file change (.json / .md)
        │  debounce 250ms
        ▼
  watchdog observer
        │
        ▼
  Broadcaster.push() → per-client SSE queue → browser
```

Fallback: full refresh every 60s. Keepalive ping every 25s (proxy-safe).

## Dashboard tabs

| Tab | Contents |
|-----|----------|
| Overview | Agent grid, task queue, active projects, SLA alerts |
| Agents | Agent cards, inbox counts, quality scores, specializations |
| Tasks | Filterable table — priority, SLA countdown, 🚨 HITL filter |
| Velocity | 7-day charts, quality trend, task type breakdown |
| Budget | Daily/weekly/monthly cost per agent and model |
| OKRs | Objectives + key results with progress bars |
| R&D | Nova experiments, Evolve backlog, model benchmarks |
| Broadcast | Terminal-style broadcast.md viewer, CRITICAL/BLOCKED highlights |

## Data sources (15 files)

```
TASKS.json                AGENT_STATUS.json       AGENT_PERFORMANCE.json
OKRs.json                 VELOCITY.json            BUDGET.json
PROJECTS.json             EXPERIMENTS.json         IMPROVEMENT_BACKLOG.json
MODEL_BENCHMARKS.json     SHARED_KNOWLEDGE.json    MEMORY.md
comms/broadcast.md        comms/inboxes/*.md
```

All files are optional — missing files show N/A, never crash.

## Requirements

```bash
pip3 install watchdog --break-system-packages
```

Falls back to 5s polling if watchdog is unavailable.
