# Mission Control V1 — OpenClaw Skill

A complete operations dashboard for managing OpenClaw agent fleets. This is a self-contained skill package — it includes the full dashboard application, lifecycle hook, agent instructions, and all documentation.

**One command to install everything:**

```bash
./setup.sh
```

---

## What's Inside

```
mission-control-skill/
├── SKILL.md                    ← Agent instructions (injected into system prompt)
├── README.md                   ← This file
├── setup.sh                    ← All-in-one installer
├── hook.ts                     ← Lifecycle hook (agents → dashboard bridge)
├── docs/
│   ├── GETTING-STARTED.md      ← Step-by-step beginner guide
│   ├── API-REFERENCE.md        ← All 60+ API endpoints
│   ├── HOOK-EVENTS.md          ← Every hook event with JSON examples
│   ├── LIBRARY-GUIDE.md        ← Document Library usage
│   ├── TROUBLESHOOTING.md      ← Common problems and fixes
│   ├── DOCKER.md               ← Docker deployment guide
│   └── CHANGELOG.md            ← Version history
└── app/
    ├── backend/                ← Express + SQLite (11 route files, 3 services)
    │   ├── migrations/         ← 4 SQL migration files
    │   ├── src/
    │   │   ├── routes/         ← projects, tasks, agents, inbox, library, etc.
    │   │   └── services/       ← SSE events, gateway sync, stall detector
    │   └── .env.example
    ├── frontend/               ← React dashboard (8 views)
    │   └── src/pages/          ← Dashboard, Inbox, Pipeline, Projects,
    │                              Library, Agents, Costs, Activity
    ├── package.json            ← Root scripts (install:all, dev)
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Installation

### Option A: Interactive Setup

```bash
cd mission-control-skill
./setup.sh
```

The script asks for your gateway URL, generates a secret, installs the app, configures the hook, and tells you how to start.

### Option B: Automated Setup

```bash
./setup.sh --auto
```

Uses all defaults: port 8000, auto-generated secret, local gateway at ws://127.0.0.1:18789.

### Option C: Docker

```bash
./setup.sh --docker
```

Uses Docker Compose instead of local Node.js.

### Option D: From ClawHub

```bash
clawhub install tsu-mission-control
cd ~/.openclaw/skills/mission-control
./setup.sh
```

---

## Starting the Dashboard

```bash
cd ~/.openclaw/mission-control
npm run dev
```

Open **http://localhost:4173** in your browser.

---

## What the Skill Does for Agents

When this skill is loaded into an agent's context (via the `SKILL.md` file), the agent learns how to:

- **Report task progress** — start, progress, review, complete, fail
- **Submit work for review** — with deliverables, checklists, and summaries
- **Publish documents** — research, reports, and docs go to the Library
- **Request approvals** — workflow gates for risky actions
- **Submit project requests** — when agents identify new work
- **Report costs** — token usage per session

All communication happens via HTTP POST to the Mission Control backend. The lifecycle hook (`hook.ts`) handles the translation from OpenClaw events to API calls.

---

## Dashboard Views

| View | What It Does |
|------|-------------|
| **Dashboard** | Stats, pipeline overview, agent status, alerts, recent activity |
| **Inbox** | Unified queue: requests + reviews + approvals in one sorted list |
| **Pipeline** | Kanban board with drag-and-drop and enforced stage transitions |
| **Projects** | Project CRUD with progress bars and agent assignment |
| **Library** | Document catalog with collections, search, multi-format reader |
| **Agents** | Agent monitoring with status, model info, task counts |
| **Costs** | Token spend tracking with daily trends and breakdowns |
| **Activity** | Chronological feed of all system events |

---

## Documentation

| Doc | What It Covers |
|-----|---------------|
| [GETTING-STARTED.md](docs/GETTING-STARTED.md) | Step-by-step guide for first-time setup. Assumes no technical knowledge. |
| [API-REFERENCE.md](docs/API-REFERENCE.md) | Every API endpoint with methods, parameters, and example payloads. |
| [HOOK-EVENTS.md](docs/HOOK-EVENTS.md) | All 12 hook events agents can send, with complete JSON examples. |
| [LIBRARY-GUIDE.md](docs/LIBRARY-GUIDE.md) | How the Library works: collections, types, tags, formats, versioning, search. |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Solutions for install errors, empty dashboards, hook failures, and more. |
| [DOCKER.md](docs/DOCKER.md) | Running everything in Docker containers. |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history and what changed. |

---

## Publishing to ClawHub

```bash
clawhub publish ./mission-control-skill \
  --slug tsu-mission-control \
  --name "Mission Control" \
  --version 1.0.0 \
  --tags latest
```

---

## License

MIT
