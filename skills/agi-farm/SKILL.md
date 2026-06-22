---
name: agi-farm
description: >
  Interactive setup wizard that creates a fully working multi-agent AI team on OpenClaw.
  One command bootstraps agents, SOUL.md personas, comms infrastructure (inboxes/outboxes/broadcast),
  cron jobs, auto-dispatcher (HITL + rate-limit backoff + dependency checking), and a portable
  GitHub bundle — all customized to team name, size (3/5/11 agents), domain, and frameworks
  (autogen/crewai/langgraph). Includes a React + SSE live ops dashboard with file-watcher
  (~350ms push latency) and persistent macOS LaunchAgent. Model-selection guidance built in.
  Commands: setup | status | rebuild | export | dashboard | dispatch
---

# agi-farm

Builds a complete multi-agent AI team on OpenClaw. One wizard, full team.

## Commands

| Command | What it does |
|---------|-------------|
| `/agi-farm setup` | Full wizard — agents, workspace, crons, bundle, GitHub |
| `/agi-farm status` | Team health: agents, tasks, cron status |
| `/agi-farm rebuild` | Regenerate workspace from existing bundle (preserves edits) |
| `/agi-farm export` | Push bundle to GitHub |
| `/agi-farm dashboard` | Launch live ops room — see [references/dashboard.md](references/dashboard.md) |
| `/agi-farm dispatch` | Run auto-dispatcher — see [scripts/auto-dispatch.py](scripts/auto-dispatch.py) |

---

## `/agi-farm setup`

Ask **one question at a time**. Do not proceed until confirmed.

### Step 1 — Team name
> "What should we call your team? (e.g. NovaCorp, TradingDesk — default: MyTeam)"

Store as `TEAM_NAME`.

### Step 2 — Orchestrator name
> "What's your orchestrator's name? (default: Cooper)"

Store as `ORCHESTRATOR_NAME`.

### Step 3 — Team size
> "How many agents?
> **3** — Minimal: Orchestrator + Researcher + Builder
> **5** — Standard: adds QA + Content
> **11** — Full stack: complete AGI system (recommended)"

Store as `PRESET`.

### Step 3.5 — Domain
> "What domain? software / trading / research / general (default) / custom"

If custom: ask for one-phrase description. Store as `DOMAIN`.

### Step 3.6 — Custom agents _(PRESET 3 or 5 only)_
> "Add a custom agent? (yes/no, default: no)"

If yes, collect per agent: `id`, `name`, `emoji`, `role`, `goal`. Max 3 custom agents.
Append to roster in Step 7 with `"template": "generic"`.

### Step 4 — Frameworks
> "Collaboration frameworks? autogen / crewai / langgraph / all / none"

Store as `FRAMEWORKS` list. `all` → `["autogen", "crewai", "langgraph"]`.

### Step 5 — GitHub
> "Create a GitHub repo for the bundle? yes / no"

Store as `CREATE_GITHUB`.

### Step 6 — Confirm
Show summary, ask "Shall I proceed? (yes/no)". If no → restart Step 1.

---

### Step 7 — Write `team.json`

```bash
mkdir -p ~/.openclaw/workspace/agi-farm-bundle/
openclaw agents list --json   # use output to assign appropriate models per role
```

Use the `openclaw agents list` output to assign each agent a model appropriate for
its role. Write resolved model strings directly into the `"model"` fields.

**Model selection cheat sheet** (based on `openclaw agents list --json` output):

| Role | Recommended tier | Why |
|------|-----------------|-----|
| Orchestrator | High-capability (e.g. `sonnet`, `opus`) | Needs broad reasoning, delegation judgment |
| Solution Architect / Researcher | High-capability | Deep analysis + design |
| Implementation Engineer | Mid-tier (e.g. `glm-5`, `sonnet`) | Fast code gen; cost-efficiency matters |
| Debugger | High-capability (e.g. `opus`) | Root-cause analysis benefits from deep reasoning |
| Business Analyst / Knowledge | Mid-high (e.g. `gemini-2.0-pro-exp`) | Long-context research tasks |
| QA Engineer | Fast/cheap (e.g. `glm-4.7-flash`) | High volume, pattern-matching checks |
| Content / Multimodal | Multimodal-capable (e.g. `gemini-2.0-pro-exp`) | Vision + rich generation |
| R&D / Process Improvement | High-capability | Creative + structured experimentation |

> Tip: assign `opus` or `sonnet` to roles that make decisions; use `flash`/`glm-4.7-flash` for high-frequency reviewers to manage cost.

**3-agent roster:**
```json
{"team_name":"<TEAM_NAME>","orchestrator_name":"<ORCHESTRATOR_NAME>","preset":"3",
 "domain":"<DOMAIN>","frameworks":<FRAMEWORKS_JSON>,"created_at":"<ISO_TIMESTAMP>",
 "agents":[
   {"id":"main",       "name":"<ORCHESTRATOR_NAME>","emoji":"🦅","role":"Orchestrator",           "goal":"Orchestrate the team, delegate tasks, synthesize results",             "model":"<MODEL>","workspace":"."},
   {"id":"researcher", "name":"Sage",               "emoji":"🔮","role":"Researcher",             "goal":"Research deeply and surface the insights that matter most",            "model":"<MODEL>","workspace":"researcher"},
   {"id":"builder",    "name":"Forge",              "emoji":"⚒️","role":"Builder",                "goal":"Implement solutions cleanly and efficiently",                          "model":"<MODEL>","workspace":"builder"}
 ]}
```

**5-agent:** add to 3-agent roster:
```json
{"id":"qa",     "name":"Vigil", "emoji":"🛡️","role":"QA Engineer",       "goal":"Ensure every output meets quality standards","model":"<MODEL>","workspace":"qa"},
{"id":"content","name":"Anchor","emoji":"⚓", "role":"Content Specialist","goal":"Craft clear content that communicates complex ideas simply","model":"<MODEL>","workspace":"content"}
```

**11-agent roster:**
```json
[
  {"id":"main",  "name":"<ORCHESTRATOR_NAME>","emoji":"🦅","role":"Orchestrator",            "goal":"Orchestrate specialists, delegate tasks, synthesize results",                          "model":"<MODEL>","workspace":"."},
  {"id":"sage",  "name":"Sage",              "emoji":"🔮","role":"Solution Architect",       "goal":"Design robust, scalable architectures",                                               "model":"<MODEL>","workspace":"solution-architect"},
  {"id":"forge", "name":"Forge",             "emoji":"⚒️","role":"Implementation Engineer", "goal":"Implement clean, well-tested code efficiently",                                        "model":"<MODEL>","workspace":"implementation-engineer"},
  {"id":"pixel", "name":"Pixel",             "emoji":"🐛","role":"Debugger",                "goal":"Find the true root cause of any bug or failure",                                       "model":"<MODEL>","workspace":"debugger"},
  {"id":"vista", "name":"Vista",             "emoji":"🔭","role":"Business Analyst",        "goal":"Research deeply and surface the insights that matter most",                            "model":"<MODEL>","workspace":"business-analyst"},
  {"id":"cipher","name":"Cipher",            "emoji":"🔊","role":"Knowledge Curator",       "goal":"Curate and surface knowledge so the team never forgets",                              "model":"<MODEL>","workspace":"knowledge-curator"},
  {"id":"vigil", "name":"Vigil",             "emoji":"🛡️","role":"QA Engineer",             "goal":"Ensure every output meets quality standards",                                         "model":"<MODEL>","workspace":"quality-assurance"},
  {"id":"anchor","name":"Anchor",            "emoji":"⚓", "role":"Content Specialist",     "goal":"Craft clear content that communicates complex ideas simply",                           "model":"<MODEL>","workspace":"content-specialist"},
  {"id":"lens",  "name":"Lens",              "emoji":"📡","role":"Multimodal Specialist",   "goal":"Extract meaning from images, documents, and multimodal inputs",                       "model":"<MODEL>","workspace":"multimodal-specialist"},
  {"id":"evolve","name":"Evolve",            "emoji":"🔄","role":"Process Improvement Lead","goal":"Make the team better systematically through continuous improvement",                   "model":"<MODEL>","workspace":"process-improvement"},
  {"id":"nova",  "name":"Nova",              "emoji":"🧪","role":"R&D Lead",                "goal":"Turn hypotheses into proven capabilities through structured experimentation",          "model":"<MODEL>","workspace":"r-and-d"}
]
```

---

### Step 8 — Generate workspace files

```bash
python3 ~/.openclaw/skills/agi-farm/generate.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json \
  --output ~/.openclaw/workspace/ \
  --all-agents --shared --bundle
```

---

### Step 9 — Create OpenClaw agents

For each agent **except `main`** (skip if already exists):

```bash
openclaw agents add \
  --agent <id> --name "<name>" --emoji "<emoji>" \
  --model "<model>" \
  --workspace "~/.openclaw/workspace/agents-workspaces/<workspace>"
```

Use `agent["model"]` from team.json directly.

---

### Step 10 — Register cron jobs

```bash
python3 ~/.openclaw/skills/agi-farm/scripts/register-crons.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json
```

Timezone is read automatically from OpenClaw config. Skips any cron that already exists.

---

### Step 11 — Install frameworks

For each framework in `FRAMEWORKS`:

```bash
if [ ! -d ~/.openclaw/skills/<fw>-collab ]; then
  TMP=$(mktemp -d)
  git clone --depth 1 --filter=blob:none --sparse \
    https://github.com/oabdelmaksoud/openclaw-skills.git "$TMP"
  cd "$TMP" && git sparse-checkout set <fw>-collab
  cp -r <fw>-collab ~/.openclaw/skills/ && rm -rf "$TMP"
fi
python3 ~/.openclaw/skills/<fw>-collab/build_agents.py --force 2>/dev/null || true
```

---

### Step 12 — GitHub (if chosen)

```bash
cd ~/.openclaw/workspace/agi-farm-bundle
git init -b main && git add . && git commit -m "feat: <TEAM_NAME> AGI farm"
gh repo create agi-farm-<TEAM_NAME_LOWER> --public --source . --remote origin --push
```

---

### Step 13 — Commit workspace

```bash
cd ~/.openclaw/workspace
git add -A && git commit -m "feat: <TEAM_NAME> AGI team — agi-farm setup complete"
```

---

### Step 14 — Initialize registries + health check

```bash
# Write TASKS.json and AGENT_STATUS.json
python3 - << 'EOF'
import json
from pathlib import Path
ws   = Path.home() / ".openclaw/workspace"
team = json.loads((ws / "agi-farm-bundle/team.json").read_text())
(ws / "TASKS.json").write_text("[]")
(ws / "AGENT_STATUS.json").write_text(json.dumps(
    {a["id"]: {"status": "available", "name": a["name"]} for a in team["agents"]}, indent=2))
print("✅ registries written")
EOF

# Health check
AGENTS=$(openclaw agents list --json 2>/dev/null | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" || echo 0)
CRONS=$(openclaw cron list 2>/dev/null | grep -c "<TEAM_NAME_LOWER>" || echo 0)
[ -d ~/.openclaw/workspace/comms/inboxes ] && echo "✅ comms OK" || echo "❌ comms missing"
[ -f ~/.openclaw/workspace/TASKS.json ]    && echo "✅ TASKS.json OK" || echo "❌ TASKS.json missing"
echo "✅ Agents: $AGENTS | Crons: $CRONS"
```

---

### Step 15 — Done

```
✅ <TEAM_NAME> AGI team is live!
Agents   : <PRESET> (<AGENT_NAMES_LIST>)
Workspace: ~/.openclaw/workspace/
Bundle   : ~/.openclaw/workspace/agi-farm-bundle/
GitHub   : <URL if created>

Next: talk to <ORCHESTRATOR_NAME> · /agi-farm status · /agi-farm dashboard
```

---

## `/agi-farm status`

```bash
openclaw agents list --json | python3 -c "
import json,sys
for a in json.load(sys.stdin):
    print(f'  {a.get(\"identityEmoji\",\"🤖\")} {a.get(\"identityName\",a[\"id\"])}: {a.get(\"model\",\"?\")}')
"
python3 -c "
import json
from pathlib import Path
ws = Path.home() / '.openclaw/workspace'
tasks = json.loads((ws/'TASKS.json').read_text()) if (ws/'TASKS.json').exists() else []
t = [t for t in tasks if isinstance(t,dict)]
print(f'  Tasks: {len(t)} total · {sum(1 for x in t if x.get(\"status\")==\"pending\")} pending · {sum(1 for x in t if x.get(\"status\")==\"needs_human_decision\")} HITL')
"
openclaw cron list 2>/dev/null | head -15
```

---

## `/agi-farm rebuild`

```bash
python3 ~/.openclaw/skills/agi-farm/generate.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json \
  --output ~/.openclaw/workspace/ \
  --all-agents --shared --no-overwrite
```

`--no-overwrite` skips files that already exist, preserving manual edits.
Add `--force` (remove `--no-overwrite`) to overwrite everything.

---

## `/agi-farm export`

```bash
cd ~/.openclaw/workspace/agi-farm-bundle
git add -A
git commit -m "export: $(date +%Y-%m-%d)" 2>/dev/null || echo "Nothing to commit"
git push 2>/dev/null || echo "No remote — run /agi-farm setup first"
```

---

## `/agi-farm dashboard`

**React + SSE ops room.** File-watcher pushes live data to the browser in ~350ms on any workspace `.json` or `.md` change. Runs as a persistent macOS LaunchAgent — always on, auto-restarts on crash.

### Architecture

```
dashboard.py          ← Python HTTP server (SSE + static)
  ├── WorkspaceWatcher  watchdog file-watcher, 250ms debounce
  ├── SlowDataCache     background thread — caches `openclaw agents list`
  │                     and `openclaw cron list` every 30s (each takes ~1-2s)
  ├── Broadcaster       thread-safe SSE fan-out to all connected clients
  └── /api/stream       SSE endpoint — pushes full snapshot on every file change

dashboard-react/      ← Vite + React 18 + Recharts frontend
  dist/               ← production build (served by dashboard.py)
  src/
    hooks/useDashboard.js   SSE hook — auto-reconnects on disconnect
    components/
      Header.jsx            live badge, stats, clock
      Nav.jsx               tab switcher
      tabs/
        Overview.jsx        stats, budget bar, SLA alerts, agent grid, broadcast preview
        Agents.jsx          full agent cards — model, inbox, quality, credibility, cache age
        Tasks.jsx           filterable table, expandable rows, ticking deadlines, pagination
        Velocity.jsx        7-day charts (Recharts), quality trend, task-type donut
        Budget.jsx          period bars, threshold markers, per-agent/model breakdown
        OKRs.jsx            objectives + KRs with progress bars
        RD.jsx              experiments, backlog, benchmarks
        Broadcast.jsx       terminal log, color-coded CRITICAL/BLOCKED/HITL
```

### Data sources (all real-time from workspace files)

| Field | Source file | Refresh |
|-------|-------------|---------|
| tasks, task_counts, sla_at_risk | `TASKS.json` | instant |
| agents (inbox, perf, status) | `AGENT_STATUS.json`, `AGENT_PERFORMANCE.json`, `comms/inboxes/` | instant |
| agent model, cron error/busy | `openclaw agents/cron list` | 30s cache |
| budget | `BUDGET.json` | instant |
| velocity | `VELOCITY.json` | instant |
| okrs | `OKRs.json` | instant |
| broadcast | `comms/broadcast.md` | instant |
| experiments / backlog | `EXPERIMENTS.json`, `IMPROVEMENT_BACKLOG.json` | instant |
| knowledge_count | `SHARED_KNOWLEDGE.json` | instant |
| memory_lines | `MEMORY.md` | instant |

### LaunchAgent (always-on)

The dashboard is registered as `ai.coopercorp.dashboard` and starts automatically at login.

```bash
# Status
launchctl list | grep coopercorp
curl -s http://localhost:8080/api/data | python3 -m json.tool | head -5

# Restart
launchctl stop  ai.coopercorp.dashboard
launchctl start ai.coopercorp.dashboard

# Logs
tail -f /tmp/coopercorp-dashboard.log
tail -f /tmp/coopercorp-dashboard.err

# Disable / re-enable
launchctl unload ~/Library/LaunchAgents/ai.coopercorp.dashboard.plist
launchctl load   ~/Library/LaunchAgents/ai.coopercorp.dashboard.plist
```

**URL**: http://localhost:8080

### Rebuild React frontend

```bash
cd ~/.openclaw/skills/agi-farm/dashboard-react
npm install        # first time only
npm run build      # outputs to dist/ — dashboard.py serves automatically
```

Full reference: [references/dashboard.md](references/dashboard.md)

---

## `/agi-farm dispatch`

```bash
# Dry-run (preview only)
python3 ~/.openclaw/skills/agi-farm/scripts/auto-dispatch.py

# Execute
python3 ~/.openclaw/skills/agi-farm/scripts/auto-dispatch.py --execute
```

Fires agent sessions for pending tasks, handles HITL notifications, stale task
resets, rate-limit backoff, and dependency checking. Cron (every 1 min):
```bash
* * * * * python3 ~/.openclaw/skills/agi-farm/scripts/auto-dispatch.py --execute \
            >> ~/.openclaw/workspace/logs/auto-dispatch.log 2>&1
```

---

## Troubleshooting

### Setup issues

| Symptom | Fix |
|---------|-----|
| `generate.py` fails with `ModuleNotFoundError` | Run `pip3 install jinja2` |
| `openclaw agents add` says agent already exists | Safe to ignore — skip that agent |
| `gh repo create` fails | Run `gh auth login` first |
| Cron registration shows 0 crons added | Run `openclaw cron list` to check for duplicates; use `--force` flag on re-register |
| `git commit` fails in Step 13 | Run `git config --global user.email` and set name/email first |

### Runtime issues

| Symptom | Fix |
|---------|-----|
| Auto-dispatcher fires but agents don't respond | Check `logs/auto-dispatch.log`; verify `openclaw agents list` shows agents |
| Dashboard shows stale data | Restart LaunchAgent: `launchctl stop ai.coopercorp.dashboard && launchctl start ai.coopercorp.dashboard` |
| TASKS.json parse error | Validate JSON: `python3 -m json.tool ~/.openclaw/workspace/TASKS.json` |
| Agent stuck >30 min | Check broadcast.md for `[BLOCKED]` tags; reassign task manually |
| Rate-limit backoff too aggressive | Edit `RATE_LIMIT_BACKOFF_MIN` in `scripts/auto-dispatch.py` (default: 10 min) |
| `openclaw` not found in cron | Set `OPENCLAW_BIN=/path/to/openclaw` in the cron environment, or add `PATH=/opt/homebrew/bin:$PATH` |

### Recovery

```bash
# Re-run setup without overwriting existing files
python3 ~/.openclaw/skills/agi-farm/generate.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json \
  --output ~/.openclaw/workspace/ \
  --all-agents --shared --no-overwrite

# Force full regeneration (overwrites everything)
python3 ~/.openclaw/skills/agi-farm/generate.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json \
  --output ~/.openclaw/workspace/ \
  --all-agents --shared --bundle --force
```
