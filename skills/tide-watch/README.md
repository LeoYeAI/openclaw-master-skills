# Tide Watch 🌊

**Proactive session capacity monitoring for OpenClaw.**

> 🚨 **SECURITY NOTICE:** v1.0.0 contains a shell injection vulnerability (CVE-2026-001). **Update to v1.0.1 immediately.** See [SECURITY-ADVISORY-CVE-2026-001.md](./SECURITY-ADVISORY-CVE-2026-001.md) for details.

Never lose work to a full context window again. Tide Watch monitors your OpenClaw sessions and warns you before capacity limits lock you out.

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-tide--watch-orange)](https://clawhub.ai/chrisagiddings/tide-watch)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

Get warned **before** your session context fills up:

- 🟡 **75%** — "Heads up, consider wrapping up soon"
- 🟠 **85%** — "Recommend finishing and resetting"
- 🔴 **90%** — "Session will lock soon!"
- 🚨 **95%** — "CRITICAL: Save to memory NOW"

## 💻 Requirements

**Runtime:**
- Node.js 14+ (for CLI tools mode)
- ANSI-compatible terminal for live dashboard (most modern terminals)
  - ✅ macOS: Terminal.app, iTerm2
  - ✅ Linux: Most terminal emulators
  - ✅ Windows: Windows Terminal, PowerShell 7+, Windows 10+ CMD
  - ⚠️ Older terminals (pre-Windows 10 CMD) may not display colors

**Directives-Only Mode:**
- No Node.js required
- Works through OpenClaw's built-in tools

## 📦 Installation

### Via ClawHub (Recommended)

```bash
clawhub install tide-watch
```

### Manual Installation

1. Clone this repo into your OpenClaw skills folder:
```bash
cd ~/clawd/skills  # or your skills directory
git clone https://github.com/chrisagiddings/openclaw-tide-watch tide-watch
```

2. Add the monitoring directive to your `AGENTS.md`:
```bash
cat tide-watch/AGENTS.md.template >> ../AGENTS.md
```

3. Add the heartbeat task to your `HEARTBEAT.md`:
```bash
cat tide-watch/HEARTBEAT.md.template >> ../HEARTBEAT.md
```

## 🚀 Quick Start

Once installed, Tide Watch automatically:
1. **Monitors** your session capacity hourly
2. **Warns** you at threshold percentages
3. **Suggests** actions (save to memory, switch channels, reset)

### Manual Capacity Check

Ask your agent anytime:
```
What's my current session capacity?
Check context usage
```

### CLI Tool

Tide Watch includes a command-line tool for checking session capacity directly:

**Quick Status:**
```bash
tide-watch status
```

**Check Specific Session:**
```bash
tide-watch check --session <session-id>
```

**List All Sessions:**
```bash
tide-watch report --all              # All sessions
tide-watch report                     # Above 75% (default threshold)
tide-watch report --threshold 90      # Above 90%
tide-watch report --json --pretty     # JSON output
```

**Visual Dashboard:**
```bash
tide-watch dashboard              # Visual overview with recommendations
tide-watch dashboard --watch      # Live updates (refreshes every 10s)
tide-watch dashboard --json       # JSON output
```

**Example Dashboard:**
```
TIDE WATCH DASHBOARD 🌊
──────────────────────────────────────────────────────────────────────
Session ID  Channel       Capacity                    Tokens        Status
──────────────────────────────────────────────────────────────────────
2b1bf1ef-5  discord       🟠 █████████░  87.9%  175,755/200,000
a595325f-e  webchat       🟡 ████████░░  81.4%  162,702/200,000
6eff94ac-d  telegram      🟡 ████████░░  80.1%  160,230/200,000
6dd10708-7  slack         🟡 ████████░░  79.1%  158,104/200,000
──────────────────────────────────────────────────────────────────────
⚠️  1 elevated, 3 warning

RECOMMENDED ACTIONS:
  🟠 Consider wrapping up discord/2b1bf1ef (87.9%)
  💡 Switch active work to telegram/6dd0ea29 (32.1%)
```

**Archive Old Sessions:**
```bash
tide-watch archive --older-than 4d --dry-run    # Preview archiving
tide-watch archive --older-than 2w              # Archive sessions older than 2 weeks
tide-watch archive --older-than 1mo --exclude-channel discord  # Keep Discord sessions
tide-watch archive --older-than 7d --min-capacity 50           # Only low-capacity sessions
```

**Example Archive Output:**
```
Archiving 4 session(s) older than 8d...

Session ID  Channel/Label     Last Active  Capacity  Tokens
─────────────────────────────────────────────────────────────────
2b1bf1ef-5  unknown           1w ago      87.9%     175,755
6dd0ea29-c  unknown           1w ago      32.1%     64,139
6dd10708-7  unknown           1w ago      79.1%     158,104
c8450d3b-3  unknown           1w ago      14.6%     29,225
─────────────────────────────────────────────────────────────────

✅ Archived 4 session(s)
   Location: ~/.openclaw/agents/main/sessions/archive/2026-02-24/
```

**Installation:**
```bash
cd ~/clawd/skills/tide-watch  # or wherever you cloned it
npm link                       # Creates global tide-watch command
```

### Flexible Session Lookup

Tide Watch supports multiple ways to specify sessions - no need to remember full UUIDs!

**Supported formats:**
- **Full session ID** (UUID): `6eff94ac-dde7-4621-acaf-66bb431db822`
- **Shortened ID**: `6eff94ac` (first 8+ characters)
- **Session label**: `"#navi-code-yatta"` (from Discord/groupChannel)
- **Channel name**: `discord`, `webchat`, `telegram`, etc.
- **Channel + label**: `"discord/#navi-code-yatta"`

**Examples:**
```bash
# By full UUID
tide-watch check --session 6eff94ac-dde7-4621-acaf-66bb431db822

# By shortened ID (easier!)
tide-watch check --session 6eff94ac

# By Discord/Telegram channel label
tide-watch check --session "#navi-code-yatta"

# By channel name (if only one session)
tide-watch check --session discord

# By channel + label combo
tide-watch check --session "discord/#navi-code-yatta"

# Works with all session commands
tide-watch resume-prompt edit --session "#navi-code-yatta"
tide-watch resume-prompt show --session discord
tide-watch resume-prompt status --session webchat
```

**Ambiguous matches:**
If multiple sessions match (e.g., two Discord channels), Tide Watch shows all matches and asks you to be more specific:
```bash
$ tide-watch check --session discord

❌ Multiple sessions match "discord". Please be more specific.

Matching sessions:
  1. discord/#navi-code-yatta (6eff94ac)
  2. discord/#general (a3b2c1d4)

Please specify:
  tide-watch check --session "discord/#navi-code-yatta"
  tide-watch check --session 6eff94ac
```

### Reset with Context Preservation

When warned about high capacity:
```
Help me reset this session and preserve context
```

Your agent will:
1. Save current work to memory
2. Backup the session file
3. Provide a session resumption prompt
4. Reset the session

## 💾 Automatic Backups

Tide Watch automatically backs up your session when capacity crosses configured thresholds.

### How Backups Work

1. **Triggered by thresholds:** When capacity crosses a backup trigger (default: 90%, 95%)
2. **One backup per threshold:** Won't duplicate backups at the same level
3. **Stored safely:** `~/.openclaw/agents/main/sessions/backups/`
4. **Named clearly:** `<session-id>-<threshold>-<timestamp>.jsonl`
5. **Auto-cleanup:** Old backups removed after retention period (default: 7 days)

### Example Timeline

```
Session starts at 10%
→ [75% reached] 🟡 Warning issued, no backup yet
→ [85% reached] 🟠 Warning issued, no backup yet
→ [90% reached] 🔴 Warning + backup created: 6eff94ac-90-20260223-170500.jsonl
→ [95% reached] 🚨 Critical + backup created: 6eff94ac-95-20260223-171200.jsonl
```

### Restore from Backup

If your session becomes corrupted or you need to revert:

```
Show me available backups for this session
Restore session from 90% backup
```

Your agent will:
1. List all available backups with timestamps and sizes
2. Restore the selected backup
3. Guide you through reloading the session

### Why This Matters

**Scenario:** Your session hits 97% and locks mid-task.

**Without backups:** You lose all context, must manually recreate conversation state.

**With backups:** Restore from 90% or 95% backup, losing only the last few messages instead of the entire conversation.

## ⚙️ Configuration

Tide Watch **parses your configuration dynamically** from `AGENTS.md`. Changes take effect on the next check—no need to restart OpenClaw!

Default settings work for most users. To customize, edit the Tide Watch section in your `AGENTS.md`:

### Customize Configuration

Edit the Tide Watch section in your `AGENTS.md`:

**1. Warning Thresholds** (when to warn):
```markdown
**Warning thresholds:**
- **60%**: 🟡 Early warning
- **80%**: 🟠 Action recommended
- **95%**: 🚨 Critical
```

**2. Check Frequency** (how often to monitor):
```markdown
**Monitoring schedule:**
- Check frequency: Every 30 minutes  # 15min, 30min, 1hr, 2hr, or 'manual'
```
- **Aggressive:** 15 minutes (tight feedback loop)
- **Moderate:** 1 hour (default, balanced)
- **Relaxed:** 2 hours (minimal overhead)
- **Manual:** Disable heartbeat, check only when asked

**3. Auto-Backup Triggers**:
```markdown
**Auto-backup:**
- Enabled: true  # Enable automatic session backups
- Trigger at thresholds: [90, 95]  # Subset of warning thresholds
- Retention: 7 days  # Auto-delete backups older than this
- Compress: false  # Set true to save disk space
```
- **Conservative:** `[75, 85, 90, 95]` (backup at every warning)
- **Moderate:** `[90, 95]` (default, key thresholds)
- **Aggressive:** `[95]` (last-chance only)
- **Disabled:** `Enabled: false` (no automatic backups, manual backup only)

**Backup locations:**
- Path: `~/.openclaw/agents/main/sessions/backups/`
- Format: `<session-id>-<threshold>-<timestamp>.jsonl`
- Example: `6eff94ac-90-20260223-170500.jsonl`

### Channel-Specific Settings

Override settings per channel (advanced):
```markdown
**Discord channels:**
- Thresholds: 75%, 85%, 90%, 95%
- Frequency: Every 1 hour

**Webchat:**
- Thresholds: 85%, 95% (lighter warnings)
- Frequency: Every 2 hours
```

### How Configuration Parsing Works

Tide Watch dynamically reads your `AGENTS.md` configuration every time it checks capacity:

- ✅ **Changes take effect immediately** (no restart needed)
- ✅ **Validation with fallbacks** (invalid config = use defaults)
- ✅ **Dynamic severity assignment** (first threshold = 🟡, last = 🚨)
- ✅ **Flexible formats** (accommodates different threshold counts)

**Detailed parsing documentation:** See [PARSING.md](PARSING.md) for validation rules, fallback behavior, and troubleshooting.

### CLI Configuration (v1.1.6+)

**Customize refresh intervals and timeouts** for the CLI tools (dashboard watch mode, gateway status).

**Configuration options:**
- `refreshInterval` — Dashboard watch mode refresh (seconds, default: 10)
- `gatewayInterval` — Gateway status background check (seconds, default: 30)
- `gatewayTimeout` — Gateway command timeout (seconds, default: 3)

**Configuration precedence** (highest to lowest):
1. **CLI flags** (explicit user intent)
2. **Environment variables** (session override)
3. **Config file** (persistent preferences)
4. **Defaults** (safe fallback)

#### Option 1: CLI Flags (Per-Invocation)

```bash
tide-watch dashboard --watch \
  --refresh-interval 5 \
  --gateway-interval 60 \
  --gateway-timeout 5
```

**Use when:** Quick experiment, one-time override

#### Option 2: Environment Variables (Session Override)

```bash
export TIDE_WATCH_REFRESH_INTERVAL=5
export TIDE_WATCH_GATEWAY_INTERVAL=60
export TIDE_WATCH_GATEWAY_TIMEOUT=5
tide-watch dashboard --watch
```

**Use when:** Temporary session-specific settings, shell profile integration

#### Option 3: Config File (Persistent Preferences)

**Create config file:**
```bash
mkdir -p ~/.config/tide-watch
cat > ~/.config/tide-watch/config.json << EOF
{
  "refreshInterval": 5,
  "gatewayInterval": 60,
  "gatewayTimeout": 5
}
EOF
```

**Use when:** Permanent custom defaults, consistent across all invocations

**File permissions:** Config file is automatically created with `0600` (user-only access). Config directory uses `0700` (user-only access).

#### Validation Rules

All configuration sources are validated:

| Setting | Min | Max | Default | Description |
|---------|-----|-----|---------|-------------|
| `refreshInterval` | 1 | 300 | 10 | Dashboard refresh (watch mode) |
| `gatewayInterval` | 5 | 600 | 30 | Gateway status check interval |
| `gatewayTimeout` | 1 | 30 | 3 | Gateway command timeout |

**Invalid values are rejected with clear error messages.**

**Example validation error:**
```bash
$ tide-watch dashboard --refresh-interval 500
❌ Configuration error: Invalid refreshInterval: must be between 1 and 300 seconds (Dashboard refresh interval)
```

#### Configuration Examples

**Fast refresh, high responsiveness:**
```bash
# Config file
{
  "refreshInterval": 5,
  "gatewayInterval": 15,
  "gatewayTimeout": 5
}
```

**Battery-conscious, minimal overhead:**
```bash
# Config file
{
  "refreshInterval": 30,
  "gatewayInterval": 120,
  "gatewayTimeout": 2
}
```

**Slow/remote gateway, more lenient timeout:**
```bash
# CLI override
tide-watch dashboard --watch --gateway-timeout 10
```

## 🎭 Real-World Example

**Problem** (2026-02-23):
- Discord #navi-code-yatta hit 97% capacity
- Session locked mid-task
- Lost conversation context
- Manual reset required

**With Tide Watch**:
- 🟡 Warning at 75% (150k tokens) — "Consider wrapping up"
- 🟠 Warning at 85% (170k tokens) — "Finish task and reset"
- 🔴 Warning at 90% (180k tokens) — "Ready to help you reset"
- Context saved to memory before reset
- Clean resumption prompt generated

## 🔧 How It Works

### Automatic Monitoring (Heartbeat Mode)

Once configured in `HEARTBEAT.md`, Tide Watch runs automatically:

1. **Schedule**: Checks capacity at configured interval (default: hourly)
2. **Check**: Uses OpenClaw's `session_status` tool to read token usage
3. **Calculate**: Determines percentage: `(tokens_used / tokens_max) * 100`
4. **Compare**: Checks against your configured thresholds
5. **Warn**: Issues warning if threshold crossed (once per threshold)
6. **Suggest**: Provides actions (save to memory, switch channels, reset)
7. **Silent**: Returns `HEARTBEAT_OK` when nothing needs attention

### Manual Mode

Disable heartbeat and check only when explicitly asked:
```
What's my current session capacity?
Check context usage
```

### Features

- **Percentage-based**: Works with any context size (200k, 1M, etc.)
- **Model-agnostic**: Anthropic, OpenAI, DeepSeek, or any provider
- **Stateful**: Tracks which thresholds warned, resets when session resets
- **Non-intrusive**: Silent monitoring, only speaks up at thresholds

## 🌟 Features

### Current
- ✅ Hourly capacity monitoring (configurable frequency)
- ✅ Four-tier warning system (customizable thresholds)
- ✅ **CLI tool** for manual capacity checks (`tide-watch` command)
- ✅ **Cross-session dashboard** with visual capacity bars and recommendations
- ✅ **Relative timestamps** for last activity (e.g., "2h ago", "5d ago")
- ✅ **Activity filtering** to hide old sessions (--active flag)
- ✅ **Batch archive command** for cleaning up old sessions
- ✅ **Watch mode** for live dashboard updates
- ✅ **Automatic session backups** at configured thresholds
- ✅ **Backup restoration** from any saved checkpoint
- ✅ **Retention management** (auto-cleanup old backups)
- ✅ Memory save suggestions
- ✅ Session reset assistance
- ✅ Session resumption prompts
- ✅ Model/provider agnostic
- ✅ Heartbeat integration

### Planned
- [ ] Historical capacity tracking
- [ ] Archive restore command (undo archives)
- [ ] Email/Discord notifications
- [ ] Smart session rotation
- [ ] Compression for backups (space-saving)

## 📊 Who Benefits

- **Multi-channel users** (Discord, Telegram, Slack, webchat)
- **Project-focused work** (long conversations with code/docs)
- **Team deployments** (shared OpenClaw instances)
- **Anyone** who's lost work to a full context window

## 📚 Documentation

**Getting Started:**
- [Installation Guide](#-installation) (this README)
- [Quick Start](#-quick-start) (this README)
- [Configuration Guide](#️-configuration) (this README)

**Reference:**
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Usage Examples](docs/USAGE-EXAMPLES.md)** - Real-world scenarios and workflows
- [Parsing Documentation](PARSING.md) - Configuration parsing details

**Development:**
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Code Examples](examples/) - Example scripts and demonstrations

**Quick Help:**
- 🔧 Having issues? → [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- ❓ How do I...? → [FAQ](docs/FAQ.md)
- 💡 Show me examples → [Usage Examples](docs/USAGE-EXAMPLES.md)
- ⌨️  CLI reference → [CLI Tool](#cli-tool) (this README)

## 🤝 Contributing

Issues and PRs welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- **GitHub**: https://github.com/chrisagiddings/openclaw-tide-watch
- **ClawHub**: https://clawhub.ai/chrisagiddings/tide-watch
- **OpenClaw Docs**: https://docs.openclaw.ai
- **Issues**: https://github.com/chrisagiddings/openclaw-tide-watch/issues

## 💡 Inspiration

Created after a real incident where a Discord channel session hit 97% capacity and locked mid-task, resulting in lost context and manual intervention. Tide Watch ensures this never happens again.

---

**Made with 🌊 for the OpenClaw community**
