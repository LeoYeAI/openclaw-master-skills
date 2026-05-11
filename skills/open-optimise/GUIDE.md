# Cost Optimizer — User Guide v7

## Requirements

- **OpenClaw** 2026.3.x or later
- **Node.js** v18+ (ships with OpenClaw)
- **bash** shell (Linux/macOS/WSL)
- **curl** (for health checks and webhook reports)
- **zip** (optional, for packaging — `apt install zip`)

### Optional

- **OpenRouter API key** — Required for free models ($0.00/request). Get one at [openrouter.ai/keys](https://openrouter.ai/keys)
- **Webhook URL** — For automated cost reports to Discord/Slack/etc.

### Supported Providers

Works with any OpenClaw model provider:
- Direct API providers (Anthropic, OpenAI, Google, etc.)
- OpenRouter (unlocks free + budget models)
- Custom proxies (ATXP, LiteLLM, etc.)

---

## Installation

### Quick Install

```bash
cd ~/.openclaw/workspace/skills/
curl -L https://YOUR_DOWNLOAD_URL -o cost-optimizer.zip
unzip cost-optimizer.zip
rm cost-optimizer.zip
chmod +x cost-optimizer/scripts/*.sh
```

### Manual Install

Copy the `cost-optimizer/` directory into `~/.openclaw/workspace/skills/`.

### Verify

```bash
bash ~/.openclaw/workspace/skills/cost-optimizer/scripts/cost-audit.sh
```

If you see the audit report, you're good.

### First Run

Tell your agent:
> `/cost-setup`

The skill walks through 6 setup steps, asking permission before each change.

---

## Script Reference

Every script is standalone. Run from anywhere. All accept `--help` or show usage when run with no arguments.

---

### 🔴 Safety & Prevention

#### `backup-config.sh`
Snapshot your config before any change. Auto-prunes backups older than 30 days.

```
Usage: bash backup-config.sh [config-path] [label]
```

**Example output:**
```
✅ Backed up to: /root/.openclaw/config-backups/openclaw-20260315-135232-guide-demo.json
Size: 9417 bytes

Recent backups:
  -rw------- 1 root root 9417 Mar 15 13:52 openclaw-20260315-135232-guide-demo.json
  -rw------- 1 root root 9417 Mar 15 13:52 openclaw-20260315-135225-pre-budget.json
  -rw------- 1 root root 9417 Mar 15 12:14 openclaw-20260315-121405-test.json
Total backups: 3
```

---

#### `restore-config.sh`
List available backups, pick one, restore, restart the gateway.

```
Usage: bash restore-config.sh [backup-file|"latest"]
       bash restore-config.sh              # lists available backups
```

**Example output:**
```
Available backups:

   1) 2026-03-15 13:52:32  (9417 bytes)  label: guide-demo
   2) 2026-03-15 13:52:25  (9417 bytes)  label: pre-budget
   3) 2026-03-15 12:14:05  (9417 bytes)  label: test

Usage: bash restore-config.sh latest  (restores most recent)
   or: bash restore-config.sh /path/to/backup.json
```

---

#### `fallback-validator.sh`
Tests every model in your fallback chain IN ORDER with real API calls. Catches broken models before they crash your agent.

```
Usage: bash fallback-validator.sh [config-path]
```

**Example output:**
```
  Testing 3 model(s) in fallback order...

  PRIMARY     anthropic/claude-opus-4-6                    ✅ UP (2362ms)
  FALLBACK 1  anthropic/claude-sonnet-4-6                  ✅ UP (3045ms)
  FALLBACK 2  anthropic/claude-haiku-4-5                   ✅ UP (533ms)

  ══════════════════════════════════════
  ✅ All 3 models in the chain are reachable.
```

**When something is broken:**
```
  PRIMARY     anthropic/claude-opus-4-6                    ✅ UP (312ms)
  FALLBACK 1  openrouter/minimax/minimax-m2.5              ❌ NO PROVIDER
               Provider "openrouter" not in config. Add it or remove this fallback.
  FALLBACK 2  anthropic/claude-haiku-4-5                   ✅ UP (287ms)

  🔴 CRITICAL: Broken models BEFORE working ones in the chain.
     OpenClaw may crash on the broken model instead of reaching
     the working fallback. Remove or fix broken models.
```

---

### 🔴 Where's The Money Going

#### `cost-audit.sh`
Full config analysis with monthly estimates and actionable recommendations.

```
Usage: bash cost-audit.sh [config-path]
```

**Example output:**
```
Primary Model:     anthropic/claude-opus-4-6
Fallbacks:         ["anthropic/claude-sonnet-4-6","anthropic/claude-haiku-4-5"]
Heartbeat Model:   deepseek/deepseek-v3.2
Heartbeat Every:   55m
Providers:         anthropic, openai, google-ai-studio, grok, deepseek
OpenRouter:        no
Model Aliases:     13 configured
Concurrency:       main=2, subagents=2
Memory Flush:      true

── Cost Estimates (50 requests/day) ──

  Primary (Opus): $0.71/req → $1065/month
  Heartbeats (DeepSeek every 55m): $31.4/month (26/day)

  TOTAL ESTIMATED: $1096/month

  ── Comparison ──
  All Opus (unoptimized): $1623/month
  Current config:         $1096/month
  Savings:                $526/month (32%)

  ⚠️  Still on Opus as primary. Switching to DeepSeek saves ~$1005/month
  💡 No OpenRouter = no free models. Add it for $0.00/request on simple tasks.

── Recommendations ──

  🔴 HIGH: Switch default from Opus to DeepSeek/MiniMax (~$1000/mo saved)
  🟡 MED: Add OpenRouter provider for free model access
```

---

#### `heartbeat-cost.sh`
Isolates heartbeat spending from real usage. Shows what-if across every model tier.

```
Usage: bash heartbeat-cost.sh [log-path] [days-back]
```

**Example output:**
```
── Last 7 Days ──

Heartbeat requests:  10
Real requests:       18
Total:               28
Heartbeat %:         35.7%

Heartbeats by model:
  unknown: 8 requests ($0.32)
  claude-opus-4-6: 2 requests ($1.42)

Total heartbeat cost (last 7 days): $1.74
Projected monthly heartbeat cost: $7.46

If these heartbeats had been on Opus: $7.10
You saved: $5.36 by using a cheaper model
```

---

#### `cost-history.sh`
Recalculates your real past usage across ALL model tiers. The "what would I have spent" answer.

```
Usage: bash cost-history.sh [log-path] [days-back]
```

**Example output:**
```
Found 20 model interactions (18 requests + 2 heartbeats)

── What Your Past 7 Days Would Cost on Each Tier ──

  Free       $    0.00 (last 7d)  →  $     0/month
  DeepSeek   $    0.77 (last 7d)  →  $     3/month
  Haiku      $    2.28 (last 7d)  →  $    10/month
  Sonnet     $    8.55 (last 7d)  →  $    37/month
  Opus       $   42.75 (last 7d)  →  $   183/month

── Daily Breakdown ──

  2026-03-15: 18 req + 2 hb  [claude:7 minimax:4 claude:9]
```

---

#### `session-replay.sh`
Exchange-by-exchange cost breakdown for a specific session.

```
Usage: bash session-replay.sh <session-key|"latest"> [log-path]
```

**Example output (modeled estimates when log format doesn't include per-exchange detail):**
```
  ── Simple Q&A (5 exchanges) ──

    DeepSeek     $  0.11 total ($0.02 avg/exchange)
    Sonnet       $  1.29 total ($0.26 avg/exchange)
    Opus         $  6.44 total ($1.29 avg/exchange)

  ── Heavy tool session (10 exchanges) ──

    DeepSeek     $  0.45 total ($0.05 avg/exchange)
    Sonnet       $  5.19 total ($0.52 avg/exchange)
    Opus         $ 25.97 total ($2.60 avg/exchange)

  Key insight: The LAST exchange in a long session costs 2-3x the FIRST
  because context has grown. Reset early to keep per-exchange cost flat.
```

---

#### `provider-compare.sh`
Detects same model across multiple providers. Catches "paying for free stuff."

```
Usage: bash provider-compare.sh [config-path]
```

**Example output:**
```
  MODEL                    PROVIDER          CONFIG $/M    MARKET $/M    STATUS
  ──────────────────────────────────────────────────────────────────────────────
  claude-opus-4-6          anthropic         $0            $15.00        ▶ PRIMARY, FREE via proxy
  claude-sonnet-4-6        anthropic         $0            $3.00         FREE via proxy
  deepseek-v3.2            deepseek          $0            $0.27         FREE via proxy
  gpt-5.2                  openai            $0            $2.50         FREE via proxy

  ── Summary ──
  Total models: 13
  Across providers: 5
  ✅ No duplicate models found — each model has one provider

  ℹ️  Detected proxy provider(s): anthropic, openai, google-ai-studio, grok, deepseek
     If costs show $0, the proxy handles billing separately.
```

---

### 🟡 Hidden Waste Detection

#### `token-counter.sh`
Counts every workspace file's contribution to system prompt overhead.

```
Usage: bash token-counter.sh [workspace-path]
```

**Example output:**
```
Workspace Bootstrap Files:

  FILE                           CHARS      ~TOKENS STATUS
  AGENTS.md                       7874        ~1968 moderate
  SOUL.md                         1673         ~418 ok
  TOOLS.md                         860         ~215 ok
  IDENTITY.md                      636         ~159 ok
  USER.md                          477         ~119 ok
  HEARTBEAT.md                     168          ~42 ok
  BOOTSTRAP.md                    1470         ~367 ok

Subtotal (workspace files): ~3288 tokens (13158 chars)

── Cost Per Request (overhead only) ──

  Free (OpenRouter)      $0.0000/req → $0/month (50 req/day)
  DeepSeek V3.2          $0.0209/req → $31/month (50 req/day)
  Opus 4.6               $1.1668/req → $1750/month (50 req/day)

── Trim Opportunities ──
  ⚠ BOOTSTRAP.md still present (~367 tokens). Delete after setup.
```

---

#### `tool-audit.sh`
Finds unused tools (overhead waste) and duplicate calls (execution waste).

```
Usage: bash tool-audit.sh [log-path] [days-back]
```

**Example output (no-logs mode):**
```
  TOOL                  SCHEMA    OVERHEAD/MO   DESCRIPTION
  message               ~1200     $ 27.00 opus  Messaging
  browser               ~800      $ 18.00 opus  Browser automation
  cron                  ~800      $ 18.00 opus  Scheduled jobs
  nodes                 ~600      $ 13.50 opus  Device control
  ...

  Total schema overhead: ~6110 tokens
  Monthly cost of ALL tool schemas:
    On Opus:    $137.48/month
    On DeepSeek: $2.48/month

  ── Disable Candidates (unused by most users) ──
  tts, canvas, nodes, pdf, image — saves ~1200 tokens/request
  On Opus that's $27.00/month
```

---

#### `context-monitor.sh`
Tracks context growth and predicts when compaction will trigger.

```
Usage: bash context-monitor.sh [log-path]
```

**Example output:**
```
── Context Events from Logs ──

  2026-03-15T08:13 🧹 COMPACTION triggered
  2026-03-15T08:14 🧹 COMPACTION triggered
  2026-03-15T08:28 🧹 COMPACTION triggered

── Context Growth Model ──

Base overhead:     ~75,000 tokens
Context limit:     200,000 tokens
Available for chat: ~125,000 tokens

  Exchanges until compaction (from fresh session):
  Light chat (500 tok/exchange)         250
  Normal use (2000 tok/exchange)        62
  Heavy tools (5000 tok/exchange)       25
  Code-heavy (8000 tok/exchange)        15

── Cost Impact of Context Bloat ──

  At 50% context: Opus $2.09/req (vs $1.16 fresh) — 1.8x cost
  At 90% context: Opus $2.74/req (vs $1.16 fresh) — 2.4x cost
```

---

#### `prompt-tracker.sh`
Snapshots system prompt size over time. Detects silent growth.

```
Usage: bash prompt-tracker.sh [workspace-path] [--snapshot|--report]
```

**Example output:**
```
  ── Snapshot History (1 snapshots) ──

  DATE                  TOTAL CHARS   ~TOKENS   FILES   CHANGE
  2026-03-15 13:52:25   13053         ~3265     7       baseline

  ── Current File Sizes ──

    AGENTS.md           ~1953   ████████████████████
    SOUL.md             ~416    ████
    BOOTSTRAP.md        ~363    ████
    TOOLS.md            ~213    ██
    IDENTITY.md         ~159    ██
    USER.md             ~119    █
    HEARTBEAT.md        ~42
```

---

#### `compaction-log.sh`
Tracks compaction events and whether memory flush saved context.

```
Usage: bash compaction-log.sh [log-path] [days-back]
```

---

#### `dedup-detector.sh`
Finds duplicate/redundant tool calls and requests.

```
Usage: bash dedup-detector.sh [log-path] [days-back]
```

---

### 🟡 Active Optimization

#### `apply-preset.sh`
One-command config presets. Auto-backs-up before applying.

```
Usage: bash apply-preset.sh <free|budget|balanced|quality> [--dry-run]
```

**Example output:**
```
Creating config backup before applying preset...
✅ Backed up to: openclaw-20260315-135225-pre-budget.json

Preset: BUDGET — Target $5-30/month
  Primary: DeepSeek V3.2 (~$0.04/req)
  Fallbacks: Haiku, Gemini Flash
  Heartbeat: DeepSeek every 55m
  Concurrency: 2/2
  Memory flush: enabled
```

---

#### `token-enforcer.sh`
Set hard maxTokens limits on all models.

```
Usage: bash token-enforcer.sh <config-path> <strict|moderate|normal|generous|unlimited> [--dry-run]
```

**Example output:**
```
Token Enforcer: moderate (2048 tokens)

  Setting maxTokens=2048 on 13 models across 5 providers

  Monthly output cost savings vs unlimited (50 req/day):
    Opus (output $75/M)           $  230/mo (was $3600, save $3370)
    Sonnet (output $15/M)         $   46/mo (was $720, save $674)
    DeepSeek (output $1.10/M)     $    3/mo (was $53, save $49)
```

---

#### `config-diff.sh`
Shows current config vs recommended, with per-item savings and risk assessment.

```
Usage: bash config-diff.sh [config-path]
```

**Example output:**
```
  ── Change 1: Primary Model ──
  Current:     anthropic/claude-opus-4-6
  Recommended: deepseek/deepseek-v3.2
  Why:         DeepSeek handles 80%+ of tasks well at 94% less cost
  Savings:     $503-1005/month
  Risk:        Lower quality on complex reasoning. Use /model opus when needed.

  ── Change 5: OpenRouter Provider ──
  Current:     not configured
  Recommended: Add with API key for free models
  Savings:     $30-200/month

  ══════════════════════════════════════
  Total potential savings: $533-1205/month
```

---

#### `idle-sleep.sh`
Detects idle periods and extends heartbeat interval to save during off-hours.

```
Usage: bash idle-sleep.sh [log-path] [idle-hours] [sleep-interval]
```

---

### 🟢 Model Management

#### `model-switcher.sh`
All models at a glance with status, cost, strength, and active indicator.

```
Usage: bash model-switcher.sh [config-path]
```

**Example output:**
```
  🟢 FREE
    ?      deepseek-free $ 0.00  Best free. Coding, reasoning, general.
    ?      llama-free    $ 0.00  512K context. Research, long docs.
  🔵 BUDGET
    ?      deepseek      $ 0.04  Coding daily driver. Great value.
    ?      flash         $ 0.04  Fast general tasks.
  🟡 QUALITY
    ?      haiku         $ 0.15  Mid-tier quality work.
    ?      sonnet        $ 0.53  Writing, code review, polish.
  🔴 PREMIUM
  ▶ ACTIVE opus          $ 0.71  Maximum reasoning power.

  Switch: /model <alias>    Reset: /model auto
```

---

#### `provider-health.sh`
Tests all configured models for availability and latency.

```
Usage: bash provider-health.sh [config-path]
```

**Example output:**
```
  MODEL                         ALIAS       STATUS          LATENCY   COST
  ──────────────────────────────────────────────────────────────────────────
  Claude Opus 4.6               opus        ✅ AUTH OK       132ms     $0.71
  Claude Sonnet 4.6             sonnet      ✅ AUTH OK       132ms     $0.53
  Claude Haiku 4.5              haiku       ✅ AUTH OK       132ms     $0.15
  GPT-5.2                       gpt         ✅ AUTH OK       261ms     $0.44
  Gemini Flash                  flash       ✅ AUTH OK       84ms      $0.04
  DeepSeek V3.2                 deepseek    ✅ AUTH OK       100ms     $0.04

  Summary: 13 UP, 0 SLOW, 0 DOWN (of 13 models)
```

---

### 🟢 Reporting & Distribution

#### `webhook-report.sh`
Sends daily cost summaries to Discord, Slack, or any webhook.

```
Usage: bash webhook-report.sh <webhook-url> [discord|slack|generic] [config-path]
```

---

#### `cost-dashboard.js`
Generates an HTML dashboard with cost cards, savings bars, and alias table.

```
Usage: node cost-dashboard.js [config-path] [output.html]
```

---

#### `multi-instance.sh`
Aggregates costs across multiple OpenClaw instances.

```
Usage: bash multi-instance.sh [instances-config]
```

Requires `~/.openclaw/instances.json`:
```json
{
  "instances": [
    { "name": "personal", "url": "http://localhost:3578", "token": "your-token" },
    { "name": "work-vps", "url": "https://vps.example.com:3578", "token": "other-token" },
    { "name": "local", "configPath": "/root/.openclaw/openclaw.json", "logPath": "/data/.openclaw/logs/openclaw.log" }
  ]
}
```

---

#### `preset-manager.sh`
Export, import, and list named config presets.

```
Usage: bash preset-manager.sh <export|import|list>
```

**Example output:**
```
Available Presets:

Built-in (via apply-preset.sh):
  free      — $0-5/mo, free models only
  budget    — $5-30/mo, DeepSeek default
  balanced  — $30-100/mo, Sonnet default
  quality   — $100+/mo, Opus default, cheap heartbeats

Custom presets:
  agency-team   — Multi-agent team. Budget primary, higher concurrency.
  researcher    — Research-heavy. Haiku for gathering, Sonnet for synthesis.
  solo-coder    — Solo developer. DeepSeek daily, Opus for architecture.
  writer        — Writing-focused. Sonnet for prose, DeepSeek for outlines.
  zero-budget   — Absolute zero cost. Free models only.
```

---

## Typical Workflows

### "I just installed OpenClaw and want to save money"
1. Install the skill
2. Run `bash cost-audit.sh` to see your current estimated spend
3. Run `bash apply-preset.sh budget --dry-run` to preview changes
4. Run `bash fallback-validator.sh` to verify the chain works
5. Tell your agent: `/cost-setup`

### "Something broke after a config change"
1. Run `bash restore-config.sh` to see backups
2. Run `bash restore-config.sh latest` to restore the last known-good config

### "Where is my money going?"
1. `bash cost-audit.sh` — config-level overview
2. `bash heartbeat-cost.sh` — are heartbeats eating your budget?
3. `bash cost-history.sh` — what-if analysis on real usage
4. `bash tool-audit.sh` — are unused tools wasting overhead?
5. `bash token-counter.sh` — is your system prompt bloated?

### "I want automated monitoring"
1. `bash cron-setup.sh` — generates cron job templates
2. `bash webhook-report.sh <url>` — test your webhook
3. Install the daily report cron via your agent

### "I have multiple instances"
1. Create `~/.openclaw/instances.json` with your instance URLs
2. `bash multi-instance.sh` — see total spend across all instances

---

## Uninstalling

```bash
rm -rf ~/.openclaw/workspace/skills/cost-optimizer
```

Config changes made during setup remain. To revert:
```bash
bash restore-config.sh  # pick a pre-setup backup
```
