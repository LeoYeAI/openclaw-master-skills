---
name: edict-multi-agent-orchestration
description: Install and use the Edict (三省六部) multi-agent orchestration system with 12 specialized AI agents, real-time kanban dashboard, and audit trails
triggers:
  - set up edict multi agent system
  - configure sansheng liubu agents
  - install edict orchestration
  - use openclaw multi agent dashboard
  - set up AI agent pipeline with review gates
  - configure edict kanban board
  - how to use edict agent workflow
  - deploy three provinces six ministries AI system
---

# Edict (三省六部) Multi-Agent Orchestration

> Skill by [ara.so](https://ara.so) — Daily 2026 Skills collection.

Edict implements a 1400-year-old Tang Dynasty governance model as an AI multi-agent architecture. Twelve specialized agents form a checks-and-balances pipeline: Crown Prince (triage) → Zhongshu (planning) → Menxia (review/veto) → Shangshu (dispatch) → Six Ministries (parallel execution). Built on [OpenClaw](https://openclaw.ai), it provides a real-time React kanban dashboard, full audit trails, and per-agent LLM configuration.

---

## Architecture Overview

```
You (Emperor) → taizi (triage) → zhongshu (plan) → menxia (review/veto)
             → shangshu (dispatch) → [hubu|libu|bingbu|xingbu|gongbu|libu2] (execute)
             → memorial (result archived)
```

**Key differentiator vs CrewAI/AutoGen**: Menxia (门下省) is a mandatory quality gate — it can veto and force rework before tasks reach executors.

---

## Prerequisites

- [OpenClaw](https://openclaw.ai) installed and running
- Python 3.9+
- Node.js 18+ (for React dashboard build)
- macOS or Linux

---

## Installation

### Quick Demo (Docker — no OpenClaw needed)

```bash
# x86/amd64 (Ubuntu, WSL2)
docker run --platform linux/amd64 -p 7891:7891 cft0808/sansheng-demo

# Apple Silicon / ARM
docker run -p 7891:7891 cft0808/sansheng-demo

# Or with docker-compose (platform already set)
docker compose up
```

Open http://localhost:7891

### Full Installation

```bash
git clone https://github.com/cft0808/edict.git
cd edict
chmod +x install.sh && ./install.sh
```

The install script automatically:
- Creates all 12 agent workspaces (taizi, zhongshu, menxia, shangshu, hubu, libu, bingbu, xingbu, gongbu, libu2, zaochao, legacy-compat)
- Writes SOUL.md role definitions to each agent workspace
- Registers agents and permission matrix in `openclaw.json`
- Symlinks shared data directories across all agent workspaces
- Sets `sessions.visibility all` for inter-agent message routing
- Syncs API keys across all agents
- Builds React frontend
- Initializes data directory and syncs official stats

### First-time API Key Setup

```bash
# Configure API key on first agent
openclaw agents add taizi
# Then re-run install to propagate to all agents
./install.sh
```

---

## Running the System

```bash
# Terminal 1: Data refresh loop (keeps kanban data current)
bash scripts/run_loop.sh

# Terminal 2: Dashboard server
python3 dashboard/server.py

# Open dashboard
open http://127.0.0.1:7891
```

---

## Key Commands

### OpenClaw Agent Management

```bash
# List all registered agents
openclaw agents list

# Add/configure an agent
openclaw agents add <agent-name>

# Check agent status
openclaw agents status

# Restart gateway (required after config changes)
openclaw gateway restart

# Send a message/edict to the system
openclaw send taizi "帮我分析一下竞争对手的产品策略"
```

### Dashboard Server

```python
# dashboard/server.py — serves on port 7891
# Built-in: React frontend + REST API + WebSocket updates
python3 dashboard/server.py

# Custom port
PORT=8080 python3 dashboard/server.py
```

### Data Scripts

```bash
# Sync official (agent) statistics
python3 scripts/sync_officials.py

# Update kanban task states
python3 scripts/kanban_update.py

# Run news aggregation
python3 scripts/fetch_news.py

# Full refresh loop (runs all scripts in sequence)
bash scripts/run_loop.sh
```

---

## Configuration

### Agent Model Configuration (`openclaw.json`)

```json
{
  "agents": {
    "taizi": {
      "model": "claude-3-5-sonnet-20241022",
      "workspace": "~/.openclaw/workspaces/taizi"
    },
    "zhongshu": {
      "model": "gpt-4o",
      "workspace": "~/.openclaw/workspaces/zhongshu"
    },
    "menxia": {
      "model": "claude-3-5-sonnet-20241022",
      "workspace": "~/.openclaw/workspaces/menxia"
    },
    "shangshu": {
      "model": "gpt-4o-mini",
      "workspace": "~/.openclaw/workspaces/shangshu"
    }
  },
  "gateway": {
    "port": 7891,
    "sessions": {
      "visibility": "all"
    }
  }
}
```

### Per-Agent Model Hot-Switching (via Dashboard)

Navigate to **⚙️ Models** panel → select agent → choose LLM → Apply. Gateway restarts automatically (~5 seconds).

### Environment Variables

```bash
# API keys (set before running install.sh or openclaw)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Optional: Feishu/Lark webhook for notifications
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."

# Optional: news aggregation
export NEWS_API_KEY="..."

# Dashboard port override
export DASHBOARD_PORT=7891
```

---

## Agent Roles Reference

| Agent | Role | Responsibility |
|-------|------|----------------|
| `taizi` | 太子 Crown Prince | Triage: chat → auto-reply, edicts → create task |
| `zhongshu` | 中书省 | Planning: decompose edict into subtasks |
| `menxia` | 门下省 | **Review/Veto**: quality gate, can reject and force rework |
| `shangshu` | 尚书省 | Dispatch: assign subtasks to ministries |
| `hubu` | 户部 Ministry of Revenue | Finance, data analysis tasks |
| `libu` | 礼部 Ministry of Rites | Communication, documentation tasks |
| `bingbu` | 兵部 Ministry of War | Strategy, security tasks |
| `xingbu` | 刑部 Ministry of Justice | Review, compliance tasks |
| `gongbu` | 工部 Ministry of Works | Engineering, technical tasks |
| `libu2` | 吏部 Ministry of Personnel | HR, agent management tasks |
| `zaochao` | 早朝官 | Morning briefing aggregator |

### Permission Matrix (who can message whom)

```python
# Defined in openclaw.json — enforced by gateway
PERMISSIONS = {
    "taizi":    ["zhongshu"],
    "zhongshu": ["menxia"],
    "menxia":   ["zhongshu", "shangshu"],  # can veto back to zhongshu
    "shangshu": ["hubu", "libu", "bingbu", "xingbu", "gongbu", "libu2"],
    # ministries report back up the chain
    "hubu":     ["shangshu"],
    "libu":     ["shangshu"],
    "bingbu":   ["shangshu"],
    "xingbu":   ["shangshu"],
    "gongbu":   ["shangshu"],
    "libu2":    ["shangshu"],
}
```

---

## Task State Machine

```python
# scripts/kanban_update.py enforces valid transitions
VALID_TRANSITIONS = {
    "pending":     ["planning"],
    "planning":    ["reviewing", "pending"],      # zhongshu → menxia
    "reviewing":   ["dispatching", "planning"],   # menxia approve or veto
    "dispatching": ["executing"],
    "executing":   ["completed", "failed"],
    "completed":   [],
    "failed":      ["pending"],  # retry
}

# Invalid transitions are rejected — no silent state corruption
```

---

## Real Code Examples

### Send an Edict Programmatically

```python
import subprocess
import json

def send_edict(message: str, agent: str = "taizi") -> dict:
    """Send an edict to the Crown Prince for triage."""
    result = subprocess.run(
        ["openclaw", "send", agent, message],
        capture_output=True,
        text=True
    )
    return {"stdout": result.stdout, "returncode": result.returncode}

# Example edicts
send_edict("分析本季度用户增长数据，找出关键驱动因素")
send_edict("起草一份关于产品路线图的对外公告")
send_edict("审查现有代码库的安全漏洞")
```

### Read Kanban State

```python
import json
from pathlib import Path

def get_kanban_tasks(data_dir: str = "data") -> list[dict]:
    """Read current kanban task state."""
    tasks_file = Path(data_dir) / "tasks.json"
    if not tasks_file.exists():
        return []
    with open(tasks_file) as f:
        return json.load(f)

def get_tasks_by_status(status: str) -> list[dict]:
    tasks = get_kanban_tasks()
    return [t for t in tasks if t.get("status") == status]

# Usage
executing = get_tasks_by_status("executing")
completed = get_tasks_by_status("completed")
print(f"In progress: {len(executing)}, Done: {len(completed)}")
```

### Update Task Status (with validation)

```python
import json
from pathlib import Path
from datetime import datetime, timezone

VALID_TRANSITIONS = {
    "pending":     ["planning"],
    "planning":    ["reviewing", "pending"],
    "reviewing":   ["dispatching", "planning"],
    "dispatching": ["executing"],
    "executing":   ["completed", "failed"],
    "completed":   [],
    "failed":      ["pending"],
}

def update_task_status(task_id: str, new_status: str, data_dir: str = "data") -> bool:
    """Update task status with state machine validation."""
    tasks_file = Path(data_dir) / "tasks.json"
    tasks = json.loads(tasks_file.read_text())

    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    current = task["status"]
    allowed = VALID_TRANSITIONS.get(current, [])

    if new_status not in allowed:
        raise ValueError(
            f"Invalid transition: {current} → {new_status}. "
            f"Allowed: {allowed}"
        )

    task["status"] = new_status
    task["updated_at"] = datetime.now(timezone.utc).isoformat()
    task.setdefault("history", []).append({
        "from": current,
        "to": new_status,
        "timestamp": task["updated_at"]
    })

    tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
    return True
```

### Dashboard REST API Client

```python
import urllib.request
import json

BASE_URL = "http://127.0.0.1:7891/api"

def api_get(endpoint: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as resp:
        return json.loads(resp.read())

def api_post(endpoint: str, data: dict) -> dict:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# Read dashboard data
tasks    = api_get("/tasks")
agents   = api_get("/agents")
sessions = api_get("/sessions")
news     = api_get("/news")

# Trigger task action
api_post("/tasks/pause",  {"task_id": "task-123"})
api_post("/tasks/cancel", {"task_id": "task-123"})
api_post("/tasks/resume", {"task_id": "task-123"})

# Switch model for an agent
api_post("/agents/model", {
    "agent": "zhongshu",
    "model": "gpt-4o-2024-11-20"
})
```

### Agent Health Check

```python
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

def check_agent_health(data_dir: str = "data") -> dict[str, str]:
    """
    Returns health status for each agent.
    🟢 active   = heartbeat within 2 min
    🟡 stale    = heartbeat 2-10 min ago
    🔴 offline  = heartbeat >10 min ago or missing
    """
    heartbeats_file = Path(data_dir) / "heartbeats.json"
    if not heartbeats_file.exists():
        return {}

    heartbeats = json.loads(heartbeats_file.read_text())
    now = datetime.now(timezone.utc)
    status = {}

    for agent, last_beat in heartbeats.items():
        last = datetime.fromisoformat(last_beat)
        delta = now - last
        if delta < timedelta(minutes=2):
            status[agent] = "🟢 active"
        elif delta < timedelta(minutes=10):
            status[agent] = "🟡 stale"
        else:
            status[agent] = "🔴 offline"

    return status

# Usage
health = check_agent_health()
for agent, s in health.items():
    print(f"{agent:12} {s}")
```

### Custom SOUL.md (Agent Personality)

```markdown
<!-- ~/.openclaw/workspaces/gongbu/SOUL.md -->
# 工部尚书 · Minister of Works

## Role
You are the Minister of Works (工部). You handle all technical,
engineering, and infrastructure tasks assigned by Shangshu Province.

## Rules
1. Always break technical tasks into concrete, verifiable steps
2. Return structured results: { "status": "...", "output": "...", "artifacts": [] }
3. Flag blockers immediately — do not silently fail
4. Estimate complexity: S/M/L/XL before starting

## Output Format
Always respond with valid JSON. Include a `summary` field ≤ 50 chars
for kanban display.
```

---

## Dashboard Panels

| Panel | URL Fragment | Key Features |
|-------|-------------|--------------|
| Kanban | `#kanban` | Task columns, heartbeat badges, filter/search, pause/cancel/resume |
| Monitor | `#monitor` | Agent health cards, task distribution charts |
| Memorials | `#memorials` | Completed task archive, 5-stage timeline, Markdown export |
| Templates | `#templates` | 9 preset edict templates with parameter forms |
| Officials | `#officials` | Token usage ranking, activity stats |
| News | `#news` | Daily tech/finance briefing, Feishu push |
| Models | `#models` | Per-agent LLM switcher (hot reload ~5s) |
| Skills | `#skills` | View/add agent skills |
| Sessions | `#sessions` | Live OC-* session monitor |
| Court | `#court` | Multi-agent discussion around a topic |

---

## Common Patterns

### Pattern 1: Parallel Ministry Execution

```python
# Shangshu dispatches to multiple ministries simultaneously
# Each ministry works independently; shangshu aggregates results
edict = "竞品分析：研究TOP3竞争对手的产品、定价、市场策略"

# Zhongshu splits into subtasks:
# hubu  → pricing analysis
# libu  → market communication analysis
# bingbu → competitive strategy analysis
# gongbu → technical feature comparison

# All execute in parallel; shangshu waits for all 4, then aggregates
```

### Pattern 2: Menxia Veto Loop

```python
# If menxia rejects zhongshu's plan:
# menxia → zhongshu: "子任务拆解不完整，缺少风险评估维度，请补充"
# zhongshu revises and resubmits to menxia
# Loop continues until menxia approves
# Max iterations configurable in openclaw.json: "max_review_cycles": 3
```

### Pattern 3: News Aggregation + Push

```python
# scripts/fetch_news.py → data/news.json → dashboard #news panel
# Optional Feishu push:
import os, json, urllib.request

def push_to_feishu(summary: str):
    webhook = os.environ["FEISHU_WEBHOOK_URL"]
    payload = json.dumps({
        "msg_type": "text",
        "content": {"text": f"📰 天下要闻\n{summary}"}
    }).encode()
    req = urllib.request.Request(
        webhook, data=payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
```

---

## Troubleshooting

### `exec format error` in Docker

```bash
# Force platform on x86/amd64
docker run --platform linux/amd64 -p 7891:7891 cft0808/sansheng-demo
```

### Agents not receiving messages

```bash
# Ensure sessions visibility is set to "all"
openclaw config set sessions.visibility all
openclaw gateway restart
# Or re-run install.sh — it sets this automatically
./install.sh
```

### API key not propagated to all agents

```bash
# Re-run install after configuring key on first agent
openclaw agents add taizi  # configure key here
./install.sh               # propagates to all agents
```

### Dashboard shows stale data

```bash
# Ensure run_loop.sh is running
bash scripts/run_loop.sh

# Or trigger manual refresh
python3 scripts/sync_officials.py
python3 scripts/kanban_update.py
```

### React frontend not built

```bash
# Requires Node.js 18+
cd dashboard/frontend
npm install && npm run build
# server.py will then serve the built assets
```

### Invalid state transition error

```python
# kanban_update.py enforces the state machine
# Check current status before updating:
tasks = get_kanban_tasks()
task = next(t for t in tasks if t["id"] == "your-task-id")
print(f"Current: {task['status']}")
print(f"Allowed next: {VALID_TRANSITIONS[task['status']]}")
```

### Gateway restart after model change

```bash
# After editing openclaw.json models section
openclaw gateway restart
# Wait ~5 seconds for agents to reconnect
```

---

## Project Structure

```
edict/
├── install.sh              # One-command setup
├── openclaw.json           # Agent registry + permissions + model config
├── scripts/
│   ├── run_loop.sh         # Continuous data refresh daemon
│   ├── kanban_update.py    # State machine enforcement
│   ├── sync_officials.py   # Agent stats aggregation
│   └── fetch_news.py       # News aggregation
├── dashboard/
│   ├── server.py           # stdlib-only HTTP + WebSocket server (port 7891)
│   ├── dashboard.html      # Fallback single-file dashboard
│   └── frontend/           # React 18 source (builds to server.py assets)
├── data/                   # Shared data (symlinked into all workspaces)
│   ├── tasks.json
│   ├── heartbeats.json
│   ├── news.json
│   └── officials.json
├── workspaces/             # Per-agent workspace roots
│   ├── taizi/SOUL.md
│   ├── zhongshu/SOUL.md
│   └── ...
└── docs/
    ├── task-dispatch-architecture.md
    └── getting-started.md
```
