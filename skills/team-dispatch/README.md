# 🚀 Team Dispatch

**Multi-Agent Workflow Orchestration System**

> One sentence → Auto-analysis → Smart decomposition → DAG dispatch → Auto-retry → Auto-delivery.

[![Version](https://img.shields.io/badge/version-1.0.5-blue.svg)](https://github.com/vvusu/team-dispatch/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🌍 Language / 语言

**Default: English** | 默认：英文

Switch to Chinese in `~/.openclaw/configs/team-dispatch.json`:

```json
{
  "language": "zh"
}
```

---

## 📖 Overview

Team Dispatch is a lightweight multi-agent collaboration system that enables a main agent to:

1. **Auto-analyze** requirement complexity (S/M/L/XL)
2. **Smart decompose** into subtasks with dependencies
3. **Build DAG** automatically generate project tracking files
4. **Parallel dispatch** schedule team agents via `sessions_spawn`
5. **Auto-progress** unlock and dispatch downstream tasks on completion
6. **Fault handling** timeout retry, model fix, degradation strategies
7. **Result injection** downstream agents automatically receive upstream output
8. **Auto-notify** deliver final checklist + preview on project completion

---

## 🎯 Features

- ✅ Auto requirement analysis (S/M/L/XL complexity levels)
- ✅ Smart task decomposition (5 templates: dev/research/fullstack/analysis/content)
- ✅ DAG dependency graph (linear/fan-out/fan-in/diamond)
- ✅ Parallel dispatch (configurable concurrency: default 5, recommended 10)
- ✅ Auto result injection to downstream agents
- ✅ Fault handling (timeout retry + model fix + degradation strategies)
- ✅ Task state persistence (JSON files, survives context compaction)
- ✅ User checkpoints (XL projects pause for approval at key nodes)
- ✅ Bilingual support (English/Chinese)

---

## 👥 Team Members

| agentId | Role | Toolset | Timeout |
|---------|------|---------|---------|
| `coder` | Coding & Development | coding | 180s |
| `product` | Product Planning | full | 60s |
| `tester` | Testing & Verification | coding | 90s |
| `research` | Research & Search | full | 90s |
| `trader` | Investment Analysis | full | 60s |
| `writer` | Content Writing | full | 60s |

---

## 📦 Installation

```bash
# 1. Clone to skills directory
cd ~/skills
git clone git@github-vvusu:vvusu/team-dispatch.git

# 2. Create symlink
ln -s ~/skills/team-dispatch/ ~/.openclaw/skills/team-dispatch

# 3. Initialize task directory
mkdir -p ~/.openclaw/workspace/tasks/{active,done,templates}

# 4. Copy templates
cp ~/skills/team-dispatch/assets/templates/project.json \
   ~/.openclaw/workspace/tasks/templates/

# 5. Verify
ls -la ~/.openclaw/skills/team-dispatch
```

---

## ⚙️ Configuration

### Language Setting

Edit `~/.openclaw/configs/team-dispatch.json`:

```json
{
  "version": "1.0.5",
  "language": "en",
  "notifyPolicy": "failures-only",
  "team": {
    "agents": {
      "coder": {
        "displayName": "Coder",
        "username": "",
        "notify": {
          "telegram": {
            "enabled": false,
            "chatId": ""
          }
        }
      }
    }
  }
}
```

### Agent Configuration

Configure 6 agents in `openclaw.json` or run:

```bash
bash ~/skills/team-dispatch/scripts/setup.sh
```

---

## ☁️ Publish to ClawHub

Because `clawhub` CLI v0.7.0 currently misses the server-required `acceptLicenseTerms` field during publish, this repo includes a safe local publisher.

```bash
# Check auth first
clawhub whoami

# Publish current version
node ~/skills/team-dispatch/scripts/publish-clawhub.mjs \
  --version 1.0.7 \
  --changelog "Daily summary cron, configurable periodic tasks, English config cleanup, launchd plist rename, system scheduler preferred by default, model/version defaults update."
```

Optional flags:

- `--path ~/skills/team-dispatch`
- `--slug team-dispatch`
- `--name "Team Dispatch"`
- `--tags latest`

## 🚀 Usage

Simply send a request to the main agent:

```
"Build a blog system for me"
"Research AI Agent market and write an analysis report"
"Analyze and fix the issues in this code"
```

The agent will automatically analyze, decompose, dispatch, collect results, and send a final delivery notification.

### Examples

#### Development Task
```
"Create a login page with dark theme and glassmorphism effect"
```
→ product(PRD) → coder(implementation) → tester(verification) → writer(docs)

#### Research Task
```
"Research the AI Agent market and write an analysis report"
```
→ research(data collection) → product(analysis framework) → writer(report)

#### Full-Stack Task
```
"Build a complete SaaS landing page with analytics"
```
→ research → product → coder → tester → writer

---

## 📊 Task Complexity Levels

| Level | Criteria | Handling |
|-------|----------|----------|
| **S** | Single agent can complete | Direct spawn, no tracking file |
| **M** | 2-3 agents, linear dependencies | Auto-build DAG + tracking |
| **L** | 4+ agents, parallel branches | DAG + tracking + progress reports |
| **XL** | Multi-domain, requires iterations | DAG + phased delivery + user checkpoints |

---

## 🔄 Decomposition Templates

### Development
```
product(PRD) → coder(implementation) → tester(verification)
                                    → writer(documentation)
```

### Research
```
research(research) → product(analysis) → writer(report)
```

### Full-Stack
```
research → product → coder → tester → writer
```

### Analysis
```
research(data) → trader(analysis) → writer(report)
              → product(strategy)
```

### Content
```
research(materials) → writer(draft) → product(review)
```

---

## ⚡ Fault Handling

### Failure Types

| Type | Trigger | Detection |
|------|---------|-----------|
| Timeout | Exceeds timeoutSeconds | runTimeoutSeconds |
| Failed | Agent returns failed | completion event status |
| Rejected | Concurrency limit 5/5 | spawn returns forbidden |
| Model Error | Model unavailable (404, etc.) | completion event error |

### Auto-Recovery Strategies

| Strategy | onFailure Value | Behavior |
|----------|-----------------|----------|
| Block | `"block"` | Abort project, notify user (default) |
| Skip | `"skip"` | Mark skipped, continue downstream |
| Fallback | `"fallback"` | Retry with backup agent |
| Manual | `"manual"` | Pause, wait for user input |

---

## 📁 Project File Structure

```
tasks/
├── active/          # In-progress projects
│   └── <project>.json
├── done/            # Completed projects
│   └── <project>.json
└── templates/
    └── project.json
```

---

## 🔧 Scripts

| Script | Description |
|--------|-------------|
| `scripts/setup.sh` | Initialize agent configuration |
| `scripts/setup-config.sh` | Create user config file |
| `scripts/doctor.sh` | Check system health |
| `scripts/watch.sh` | Low-frequency watcher for stuck tasks |

### Watcher (Recommended)

```bash
# Scan every 60s (with jitter), detect timeout tasks
bash ~/skills/team-dispatch/scripts/watch.sh

# Custom interval
INTERVAL=300 GRACE=20 bash ~/skills/team-dispatch/scripts/watch.sh
```

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

### Latest: v0.0.1
- 🌍 Add i18n support (English/Chinese)
- Add low-frequency watcher (event + scan fallback)
- Add per-agent configurable displayName/username + Telegram notify
- Add postmortem template + troubleshooting docs
- Raise recommended concurrency to 10

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**vvusu** 🐟

Multi-agent orchestration system for OpenClaw.

---

<div align="center">

**Made with ❤️ for OpenClaw Community**

[Report Issues](https://github.com/vvusu/team-dispatch/issues) • [Request Features](https://github.com/vvusu/team-dispatch/issues)

</div>
