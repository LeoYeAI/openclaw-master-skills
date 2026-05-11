# 🔋 Open-Optimise — Cost Optimizer for OpenClaw

**Reduce your OpenClaw API costs by 70-97%** through intelligent model routing, session management, output efficiency, and free model usage.

[![Version](https://img.shields.io/badge/version-7.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.3+-purple.svg)]()

---

## ⚡ What Is This?

A complete cost optimization skill for [OpenClaw](https://github.com/openclaw/openclaw) — the open-source AI agent platform. It includes:

- **14-chapter agent playbook** — Teaches your AI agent to route tasks to the cheapest adequate model
- **29 executable scripts** — Audit, monitor, backup, health check, and report on your API spending
- **5 ready-to-use presets** — One-command configs for different use cases and budgets
- **Full user guide** — With real example outputs from a live instance

### The Problem

Every OpenClaw request sends ~140,000 tokens of system prompt overhead. On Claude Opus, that costs **$0.71 per request**. On free models, it costs **$0.00**. For simple questions, the answer quality is identical.

Most users run Opus/Sonnet for everything — including heartbeats (24/7 keep-alive pings), simple Q&A, and tool calls. This skill fixes that.

### The Numbers

| Setup | Monthly Cost (50 req/day) |
|-------|--------------------------|
| All Opus (default) | ~$1,065 |
| All Sonnet | ~$645 |
| **With this skill (budget preset)** | **~$30-60** |
| **With this skill (free preset)** | **~$0** |

---

## 📦 Installation

### Quick Install

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/rajdeep09-dev/Open-Optimise.git cost-optimizer
chmod +x cost-optimizer/scripts/*.sh
```

### Manual Install

1. Download the [latest release](https://github.com/rajdeep09-dev/Open-Optimise/releases)
2. Extract to `~/.openclaw/workspace/skills/cost-optimizer/`
3. Run `chmod +x cost-optimizer/scripts/*.sh`

### Verify Installation

```bash
bash ~/.openclaw/workspace/skills/cost-optimizer/scripts/cost-audit.sh
```

You should see a full cost audit report.

### First Run

Tell your OpenClaw agent:
```
/cost-setup
```

The skill walks through 6 setup steps, asking permission before each change:
1. Budget target
2. Free models
3. Default model
4. Heartbeat optimization
5. Session management
6. Response style

---

## 🔧 Requirements

| Requirement | Details |
|-------------|---------|
| **OpenClaw** | 2026.3.x or later |
| **Node.js** | v18+ (ships with OpenClaw) |
| **Shell** | bash (Linux/macOS/WSL) |
| **curl** | For health checks and webhooks |
| **Optional:** OpenRouter API key | For free models ($0.00/request) — [get one here](https://openrouter.ai/keys) |
| **Optional:** Webhook URL | For automated reports to Discord/Slack |

---

## 📁 What's Included

```
cost-optimizer/
├── SKILL.md              # Agent playbook (14 chapters)
├── GUIDE.md              # User guide with real example outputs
├── README.md             # This file
├── VERSION               # 7.0.0
├── CHANGELOG.md          # Full version history
├── references/
│   ├── model-tiers.md    # Pricing reference card
│   └── setup-config.md   # Config templates
├── presets/
│   ├── solo-coder.preset.json
│   ├── writer.preset.json
│   ├── researcher.preset.json
│   ├── zero-budget.preset.json
│   └── agency-team.preset.json
└── scripts/              # 29 executable scripts
    ├── backup-config.sh
    ├── restore-config.sh
    ├── fallback-validator.sh
    ├── cost-audit.sh
    ├── heartbeat-cost.sh
    ├── cost-history.sh
    ├── session-replay.sh
    ├── provider-compare.sh
    ├── tool-audit.sh
    ├── token-counter.sh
    ├── context-monitor.sh
    ├── prompt-tracker.sh
    ├── compaction-log.sh
    ├── dedup-detector.sh
    ├── apply-preset.sh
    ├── token-enforcer.sh
    ├── config-diff.sh
    ├── idle-sleep.sh
    ├── setup-openrouter.sh
    ├── cost-monitor.sh
    ├── cost-dashboard.js
    ├── webhook-report.sh
    ├── cron-setup.sh
    ├── model-switcher.sh
    ├── provider-health.sh
    ├── model-test.sh
    ├── preset-manager.sh
    ├── multi-instance.sh
    └── parse-config.js
```

---

## 🛠️ Scripts Overview

### 🔴 Safety & Prevention

| Script | What it does |
|--------|-------------|
| `backup-config.sh` | Snapshot config before changes. Auto-prunes after 30 days. |
| `restore-config.sh` | List backups, pick one, restore, restart gateway. 5-second recovery. |
| `fallback-validator.sh` | Test every model in fallback chain with real API calls. |

### 🔴 Where's The Money Going

| Script | What it does |
|--------|-------------|
| `cost-audit.sh` | Full config analysis → monthly estimate → actionable recommendations |
| `heartbeat-cost.sh` | Isolate heartbeat spend from real usage — the jaw-dropper |
| `cost-history.sh` | Recalculate real past usage across ALL model tiers |
| `session-replay.sh` | Exchange-by-exchange cost breakdown for any session |
| `provider-compare.sh` | Same model across providers — find cheapest route |

### 🟡 Hidden Waste Detection

| Script | What it does |
|--------|-------------|
| `tool-audit.sh` | Find unused tools (overhead) + duplicate calls (execution waste) |
| `token-counter.sh` | Count system prompt overhead per file |
| `context-monitor.sh` | Track context growth, predict compaction |
| `prompt-tracker.sh` | Snapshot prompt size over time, detect silent growth |
| `compaction-log.sh` | Track compaction and memory flush events |
| `dedup-detector.sh` | Find redundant requests and tool calls |

### 🟡 Active Optimization

| Script | What it does |
|--------|-------------|
| `apply-preset.sh` | One-command presets (auto-backs-up first) |
| `token-enforcer.sh` | Hard maxTokens limits: strict/moderate/normal/generous |
| `config-diff.sh` | Current vs recommended side-by-side with savings |
| `idle-sleep.sh` | Extend heartbeat during idle, restore on wake |
| `setup-openrouter.sh` | Generate OpenRouter provider config from API key |

### 🟢 Monitoring & Reporting

| Script | What it does |
|--------|-------------|
| `cost-monitor.sh` | Real-time log parsing + `--live` tail mode |
| `cost-dashboard.js` | HTML dashboard with cost cards and savings bars |
| `webhook-report.sh` | Send daily reports to Discord/Slack/any webhook |
| `cron-setup.sh` | Pre-built cron templates for automated monitoring |

### 🟢 Model Management

| Script | What it does |
|--------|-------------|
| `model-switcher.sh` | All models: status + cost + strength at a glance |
| `provider-health.sh` | Test all models: UP/DOWN/SLOW + latency |
| `model-test.sh` | Basic reachability test |

### 🟢 Distribution & Sharing

| Script | What it does |
|--------|-------------|
| `preset-manager.sh` | Export/import named config presets |
| `multi-instance.sh` | Aggregate costs across multiple OpenClaw instances |

---

## 🎯 Presets

Apply with one command:

```bash
bash scripts/apply-preset.sh <preset> [--dry-run]
```

| Preset | Target Budget | Primary Model | Best For |
|--------|--------------|---------------|----------|
| `free` | $0-5/mo | Free models (OpenRouter) | Maximum savings |
| `budget` | $5-30/mo | DeepSeek V3.2 | Daily driver |
| `balanced` | $30-100/mo | Claude Sonnet | Quality + savings |
| `quality` | $100+/mo | Claude Opus | Minimal optimization |

### Community Presets

| Preset | Description |
|--------|-------------|
| `solo-coder` | DeepSeek for coding, Opus for architecture reviews |
| `writer` | Sonnet for prose, DeepSeek for research/outlines |
| `researcher` | Haiku for web searches, Sonnet for synthesis |
| `zero-budget` | Free models only. $0/month target. |
| `agency-team` | Budget primary, higher concurrency for multi-agent work |

---

## 📊 Example Output

### cost-audit.sh

```
Primary Model:     anthropic/claude-opus-4-6
Heartbeat Model:   deepseek/deepseek-v3.2
Heartbeat Every:   55m
Model Aliases:     13 configured

── Cost Estimates (50 requests/day) ──

  Primary (Opus): $0.71/req → $1065/month
  Heartbeats (DeepSeek every 55m): $31.4/month (26/day)

  TOTAL ESTIMATED: $1096/month

  ── Comparison ──
  All Opus (unoptimized): $1623/month
  Current config:         $1096/month
  Savings:                $526/month (32%)

── Recommendations ──

  🔴 HIGH: Switch default from Opus to DeepSeek/MiniMax (~$1000/mo saved)
  🟡 MED: Add OpenRouter provider for free model access
```

### provider-health.sh

```
  MODEL                         ALIAS       STATUS          LATENCY   COST
  ──────────────────────────────────────────────────────────────────────────
  Claude Opus 4.6               opus        ✅ AUTH OK       132ms     $0.71
  Claude Sonnet 4.6             sonnet      ✅ AUTH OK       132ms     $0.53
  Claude Haiku 4.5              haiku       ✅ AUTH OK       132ms     $0.15
  GPT-5.2                       gpt         ✅ AUTH OK       261ms     $0.44
  Gemini Flash                  flash       ✅ AUTH OK       84ms      $0.04
  DeepSeek V3.2                 deepseek    ✅ AUTH OK       100ms     $0.04

  Summary: 13 UP, 0 SLOW, 0 DOWN
```

### fallback-validator.sh

```
  Testing 3 model(s) in fallback order...

  PRIMARY     anthropic/claude-opus-4-6      ✅ UP (2362ms)
  FALLBACK 1  anthropic/claude-sonnet-4-6    ✅ UP (3045ms)
  FALLBACK 2  anthropic/claude-haiku-4-5     ✅ UP (533ms)

  ✅ All 3 models in the chain are reachable.
```

> See `GUIDE.md` for example outputs from every script.

---

## 🔄 Typical Workflows

### "I just installed OpenClaw and want to save money"
```bash
bash scripts/cost-audit.sh                    # See current spend
bash scripts/apply-preset.sh budget --dry-run # Preview changes
bash scripts/fallback-validator.sh            # Verify chain works
# Then tell your agent: /cost-setup
```

### "Something broke after a config change"
```bash
bash scripts/restore-config.sh               # List backups
bash scripts/restore-config.sh latest         # Restore last known-good
```

### "Where is my money going?"
```bash
bash scripts/cost-audit.sh                    # Config overview
bash scripts/heartbeat-cost.sh                # Heartbeat spending
bash scripts/cost-history.sh                  # What-if across tiers
bash scripts/tool-audit.sh                    # Unused tool waste
bash scripts/token-counter.sh                 # System prompt bloat
```

---

## 📝 Agent Commands

When the skill is active, your agent responds to:

| Command | Action |
|---------|--------|
| `/cost-setup` | Interactive setup wizard |
| `/cost-status` | Current model, session stats, estimated costs |
| `/cost-audit` | Full configuration audit |
| `/free` | Switch to free-only mode |
| `/free off` | Return to smart routing |
| `/model <alias>` | Switch to specific model |

---

## 🤝 Contributing

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/my-optimization`)
3. Test your scripts on a real OpenClaw instance
4. Commit your changes (`git commit -am 'Add new optimization'`)
5. Push to the branch (`git push origin feature/my-optimization`)
6. Create a Pull Request

### Adding a Preset

Create a `.preset.json` in `presets/` following the existing format. Include a description of who the preset is for.

---

## 📄 License

MIT — Use it, modify it, share it. Save money.

---

## 🙏 Credits

Built for the [OpenClaw](https://github.com/openclaw/openclaw) community.

*Stop paying $1,000/month for questions a free model can answer.*
