---
name: tide-watch
description: Proactive session capacity monitoring and management for OpenClaw. Prevents context window lockups by warning at configurable thresholds (75%, 85%, 90%, 95%), automatically backing up sessions before resets, and managing session resumption prompts. Use when working on long-running projects, managing multiple conversation channels (Discord, Telegram, webchat), or preventing lost work from full context windows. Includes CLI tools for capacity checks, cross-session dashboards, archive management, and session resumption. Supports any model or provider.
author: Chris Giddings
homepage: https://github.com/chrisagiddings/openclaw-tide-watch
repository: https://github.com/chrisagiddings/openclaw-tide-watch
metadata: {"openclaw":{"emoji":"🌊","version":"1.3.6","disable-model-invocation":false,"capabilities":["session-monitoring","capacity-warnings","session-backup","session-resumption","multi-agent-support","auto-detection","file-operations-local"],"requires":{"bins":[],"anyBins":["node"],"config":["~/.openclaw/agents/main/sessions/"],"env":{"optional":["OPENCLAW_SESSION_ID"],"notes":"OPENCLAW_SESSION_ID is optional for auto-detection in CLI mode (v1.3.4+). Not required for Directives-Only mode."}},"install":[{"id":"npm","kind":"node","package":".","command":"npm link","bins":["tide-watch"],"label":"Install tide-watch CLI (requires Node.js 14+, optional for Directives-Only mode)"}],"credentials":{"required":false,"types":[],"notes":"No external credentials required. Operates on local OpenClaw session files only."}}}
---

# Tide Watch 🌊

Proactive session capacity monitoring for OpenClaw.

## ⚠️ Security & Architecture Notice

**Tide Watch is a HYBRID SKILL with two operational modes:**

### Mode 1: Directives-Only (Recommended for Most Users)
**Description:** AGENTS.md and HEARTBEAT.md directives only  
**Code Execution:** **NONE** - Uses OpenClaw's built-in tools only (no CLI installation)  
**File Access:** Reads OpenClaw session files via agent's built-in tools  
**Installation:** Copy template directives to workspace config files  
**Security:** Lowest risk - no code installation or execution required

**What it does:**
- ✅ Monitors session capacity via `session_status` tool
- ✅ Warns at thresholds (75%, 85%, 90%, 95%)
- ✅ Auto-loads resumption prompts on session reset
- ✅ All operations through OpenClaw's native tools

### Mode 2: CLI Tools (Optional)
**Description:** Node.js command-line tools for manual management  
**Code Execution:** **YES** - Executable JavaScript code  
**File Access:** Direct read/write to `~/.openclaw/agents/main/sessions/`  
**Installation:** `git clone` + `npm link` (requires Node.js)  
**Security:** Moderate risk - requires code inspection before install

**What it does:**
- CLI commands: `tide-watch status`, `tide-watch dashboard`, etc.
- Manual capacity checks
- Session archive management
- Resumption prompt editing (⚠️ see CVE-2026-001 below)

### Mode Comparison

| Feature | Directives-Only | CLI Tools |
|---------|-----------------|-----------|
| **Node.js required?** | ❌ No | ✅ Yes (14+) |
| **Installation** | Copy templates | `npm link` |
| **Code execution** | ❌ None | ✅ JavaScript |
| **File access** | Via built-in tools | Direct filesystem |
| **Security risk** | Lowest | Moderate |
| **Use case** | Passive monitoring | Active management |

**Choose Directives-Only if:** You only need capacity warnings and resumption prompts.  
**Choose CLI Tools if:** You need manual session management, archiving, or dashboard views.

### 🚨 CRITICAL SECURITY NOTICE: CVE-2026-001

**Vulnerability:** Shell injection in `editResumePrompt` function  
**Affected Version:** v1.0.0 ONLY  
**Current Version:** v1.0.1 (PATCHED)  
**Severity:** HIGH (CVSS 7.8)  
**Status:** ✅ FIXED

**Summary:** v1.0.0 contained a shell injection vulnerability in the CLI's `resume-prompt edit` command. An attacker who could control the `--session` parameter could execute arbitrary commands. **This has been fixed in v1.0.1** by replacing `execSync` with `spawnSync`.

**If you installed v1.0.0:** **Update immediately** to v1.0.1.

**Full disclosure:** See [SECURITY-ADVISORY-CVE-2026-001.md](./SECURITY-ADVISORY-CVE-2026-001.md)

### Security Best Practices

**For Directives-Only Mode (Safest):**
1. ✅ Copy AGENTS.md.template and HEARTBEAT.md.template to workspace
2. ✅ No code installation required
3. ✅ No npm dependencies
4. ✅ Lowest security surface

**For CLI Tools Mode (If Needed):**
1. ⚠️ **Verify version 1.0.1 or later** (`tide-watch --version`)
2. ⚠️ **Inspect code before installing:**
   - Review `lib/capacity.js` and `lib/resumption.js`
   - Check `package.json` for install hooks (should have none)
   - Run `npm test` to verify behavior (113 tests)
3. ⚠️ **Only use UUID session IDs** with `--session` flag
4. ⚠️ **Avoid untrusted input** to CLI commands
5. ⚠️ **Review backups location** (`~/.openclaw/agents/main/sessions/archive/`)

**Operation Types:**

**Read-Only Operations** (✅ Safe, no modifications):
- `tide-watch status` - Check current session count
- `tide-watch check --session <id>` - View specific session capacity
- `tide-watch check --current` - Auto-detect and check current session (v1.3.4+)
- `tide-watch dashboard` - Visual capacity overview
- `tide-watch dashboard --watch` - Live updating dashboard
- `tide-watch dashboard --raw-size` - Show full precision token counts (v1.3.2+)
- `tide-watch report` - List sessions above threshold
- `tide-watch resume-prompt show --session <id>` - View resumption prompt

**Modifying Operations** (⚠️ Moves/creates files):
- `tide-watch archive --older-than <time>` - Moves sessions to archive/ (time-based)
- `tide-watch archive --session <id>` - Archive specific session (v1.3.3+)
- `tide-watch archive --session <id1> --session <id2>` - Archive multiple sessions (v1.3.3+)
- `tide-watch resume-prompt edit --session <id>` - Opens editor (CVE patched in v1.0.1)
- `tide-watch resume-prompt delete --session <id>` - Deletes resumption prompt file

**New Flags (v1.3.2+):**
- `--raw-size` - Show full precision token counts (e.g., `18,713/128,000` instead of `18.7k/128k`)
- `--current` - Auto-detect current session via `OPENCLAW_SESSION_ID` environment variable (v1.3.4+)
- `--session` (enhanced) - Supports partial IDs, multiple sessions for archive, labels/channels (v1.3.3+)

**File System Access:**
- Reads: `~/.openclaw/agents/main/sessions/*.jsonl` (session data)
- Writes: `~/.openclaw/agents/main/sessions/resume-prompts/*.md` (resumption prompts)
- Moves: `~/.openclaw/agents/main/sessions/archive/` (archived sessions)

**Network Activity:** **NONE** - All operations are local filesystem only.

### CLI Reference

**Complete flag and option documentation:**

**Display Options:**
- `--raw-size` - Show full precision token counts with commas (v1.3.2+)
  - Default: Human-readable (e.g., `18.7k/128k`, `20.6k/1M`)
  - With flag: Full precision (e.g., `18,713/128,000`, `20,631/1,000,000`)
  - Use case: When exact token counts needed
  - Example: `tide-watch dashboard --raw-size`

- `--json` - Output as JSON instead of formatted table
  - Example: `tide-watch check --session abc123 --json`
  - Useful for scripting and parsing

- `--pretty` - Pretty-print JSON output (requires `--json`)
  - Example: `tide-watch report --json --pretty`

**Session Selection:**
- `--session <key>` - Target specific session (enhanced in v1.3.3+)
  - Full UUID: `--session 17290631-42fe-40c0-bd23-c5da511c6f7b`
  - Partial UUID: `--session 17290631-4` (v1.3.3+)
  - Label: `--session "#navi-code-yatta"` (v1.3.3+)
  - Channel: `--session discord` (v1.3.3+)
  - Channel + label: `--session "discord/#navi-code"` (v1.3.3+)
  - Multiple (archive only): `--session abc123 --session def456` (v1.3.3+)

- `--current` - Auto-detect current session (v1.3.4+)
  - Requires: `OPENCLAW_SESSION_ID` environment variable
  - Example: `tide-watch check --current`
  - Use case: Heartbeat monitoring (check THIS session)
  - Fallback: Graceful error with helpful message if env var not set

**Filtering:**
- `--all` - Show all sessions regardless of capacity
- `--threshold <num>` - Filter sessions above percentage (default: 75)
- `--active <hours>` - Only show sessions active within N hours
- `--agent <id>` - Filter to specific agent (multi-agent setups)
- `--exclude-agent <id>` - Exclude specific agent (can use multiple times)

**Archive Options:**
- `--older-than <time>` - Archive sessions older than time
  - Examples: `4d`, `2w`, `1mo`, `3months`
  - Mutually exclusive with `--session`
  
- `--dry-run` - Preview archive without making changes
  - Example: `tide-watch archive --older-than 7d --dry-run`

- `--exclude-channel <name>` - Exclude channel from archiving
  - Example: `tide-watch archive --older-than 30d --exclude-channel discord`

- `--min-capacity <num>` - Only archive sessions below capacity threshold
  - Example: `tide-watch archive --older-than 7d --min-capacity 50`

**Live Monitoring:**
- `--watch` - Live updating dashboard (refreshes every 10s)
  - Example: `tide-watch dashboard --watch`
  - Press Ctrl+C to exit

**Multi-Agent:**
- `--all-agents` - Multi-agent discovery mode (default, auto-discovers agents)
- `--single-agent-only` - Single-agent mode (main agent only)

**Configuration Override:**
- `--refresh-interval <seconds>` - Dashboard refresh interval (1-300)
- `--gateway-interval <seconds>` - Gateway status check interval (5-600)
- `--gateway-timeout <seconds>` - Gateway command timeout (1-30)
- `--session-dir <path>` - Custom session directory

**Usage Examples:**

```bash
# Human-readable vs full precision
tide-watch dashboard                    # 18.7k/128k (easy to scan)
tide-watch dashboard --raw-size         # 18,713/128,000 (exact)

# Auto-detect current session (v1.3.4+)
export OPENCLAW_SESSION_ID="17290631-4"
tide-watch check --current              # Check THIS session
tide-watch check --current --json       # JSON for heartbeat scripts

# Session-specific archiving (v1.3.3+)
tide-watch archive --session abc123 --dry-run    # Preview
tide-watch archive --session abc123              # Archive one
tide-watch archive --session a --session b       # Archive multiple

# Partial ID matching (v1.3.3+)
tide-watch check --session 17290631-4   # Matches 17290631-42fe-40c0-...

# Multi-agent filtering
tide-watch dashboard --agent kintaro    # Kintaro sessions only
tide-watch report --exclude-agent main  # All except main
```

### Runtime Requirements

**Mode 1 (Directives-Only):**
- **Node.js:** Not required
- **npm:** Not required
- **Dependencies:** None
- **Binary:** None
- **Installation:** Copy templates to workspace config files

**Mode 2 (CLI Tools - Optional):**
- **Node.js:** v14.0.0 or later required
- **npm:** Any recent version
- **Dependencies:** 
  - Development: `jest@^30.2.0` (for testing only)
  - Runtime: None (zero production dependencies)
- **Binary:** `tide-watch` (installed globally via npm link)
- **Installation:** `git clone` + `npm link`

**Why zero runtime dependencies?**
- Uses only Node.js built-in modules (`fs`, `path`, `child_process`)
- No external API clients
- No network libraries
- Minimal attack surface

### Recommendation

**Most users should use Directives-Only Mode.** This provides automatic capacity monitoring without installing any code. Only install CLI tools if you specifically need manual capacity management features.

## What It Does

Monitors your OpenClaw session context windows and warns you before they overflow:
- 🟡 **75%** — Heads up, consider wrapping up soon
- 🟠 **85%** — Recommend finishing current task and resetting
- 🔴 **90%** — Session will lock soon, ready to reset
- 🚨 **95%** — Critical! Save to memory NOW

## Installation

### Step 1: Add Monitoring Directive to AGENTS.md

Copy the directive template from `AGENTS.md.template` and add it to your workspace `AGENTS.md` file:

```bash
# From your workspace root (~/clawd or similar)
cat skills/tide-watch/AGENTS.md.template >> AGENTS.md
```

Or manually add the monitoring section from the template.

This tells me (your agent) what to look for and when to warn you.

### Step 2: Add Heartbeat Task to HEARTBEAT.md

Copy the heartbeat template from `HEARTBEAT.md.template` and add it to your workspace `HEARTBEAT.md` file:

```bash
# From your workspace root (~/clawd or similar)
cat skills/tide-watch/HEARTBEAT.md.template >> HEARTBEAT.md
```

Or manually add the Tide Watch heartbeat section from the template.

This tells me to check capacity automatically on a schedule.

### Step 3: Configure Settings (Optional)

Default settings work for most users, but you can customize in your `AGENTS.md`:

**Warning thresholds** (when to warn):
- Adjust percentages (default: 75/85/90/95)
- Range: 50-99%, ascending order, 2-6 thresholds

**Check frequency** (how often to monitor):
- Adjust interval (default: Every 1 hour)
- Options: 15min, 30min, 1hr, 2hr, or 'manual'
- Range: 5 minutes to 6 hours

**Auto-backup**:
- Enable/disable automatic backups (default: enabled)
- Set which thresholds trigger backups (default: [90, 95])
- Configure retention (default: 7 days)
- Enable compression to save disk space (default: off)

**Channel-specific overrides** (advanced):
- Different settings per channel (Discord vs. webchat vs. DM)

## Usage

Once installed, I will:

1. **Check capacity hourly** during active conversations
2. **Warn at thresholds** (75%, 85%, 90%, 95%)
3. **Suggest actions**:
   - Save important context to memory
   - Switch to lower-usage channels
   - Provide session reset commands
   - Generate session resumption prompts

### Manual Check

Ask me to check session status anytime:
```
What's my current session capacity?
Check context usage
Run session_status
```

### Reset Session with Context Preservation

When warned about high capacity:
```
Help me reset this session and preserve context
```

I'll:
1. Save current work to memory
2. Backup the session file (if not already backed up)
3. Provide a session resumption prompt
4. Reset the session

### Load Session from Backup

If you need to load a previous session state from backup:

```
Show me available backups for this session
Load session from 90% backup
```

I'll:
1. List available backups with timestamps and sizes
2. Load the selected backup
3. Guide you through reconnecting to load the session

**Backup locations:**
- Path: `~/.openclaw/agents/main/sessions/backups/`
- Format: `<session-id>-<threshold>-<timestamp>.jsonl[.gz]`
- Retention: Configurable (default: 7 days)

## How It Works

### Automatic Monitoring (Heartbeat)

When you add Tide Watch to your `HEARTBEAT.md`, I automatically:

1. **Parse your configuration** (from AGENTS.md)
   - Check frequency: How often to monitor
   - Warning thresholds: When to warn you
   - Backup settings: When to backup, retention, compression
   - See [PARSING.md](PARSING.md) for detailed parsing logic

2. **Check capacity on schedule** (default: every hour)
   - Run `session_status` to get token usage
   - Calculate percentage: `(tokens_used / tokens_max) * 100`

3. **Compare against your thresholds**
   - Use your configured thresholds (not hardcoded defaults)
   - Determine which threshold(s) have been crossed
   - Assign severity dynamically based on position (first=🟡, last=🚨)

3. **Warn you (once per threshold)**
   - Issue warning message for new threshold crossings
   - Track which thresholds already warned this session
   - Don't repeat warnings if capacity stays at same level

4. **Auto-backup (if enabled and triggered)**
   - Check if capacity crossed any backup trigger thresholds
   - Create backup: `~/.openclaw/agents/main/sessions/backups/<session-id>-<threshold>-<timestamp>.jsonl`
   - Verify backup integrity
   - Log backup completion
   - Track which thresholds backed up (don't duplicate)

5. **Suggest actions**
   - Save context to memory
   - Switch to lower-usage channel
   - Provide session reset commands
   - Generate session resumption prompts

6. **Cleanup old backups**
   - Remove backups older than retention period (default: 7 days)

7. **Return to silent mode**
   - If capacity is below all thresholds, return `HEARTBEAT_OK`
   - No output, no interruption

### Manual Checks

You can also ask me to check anytime:
```
What's my current session capacity?
Check context usage
Run session_status
```

### Key Features

- **Model-agnostic**: Works with any provider (Anthropic, OpenAI, DeepSeek, etc.)
- **Non-intrusive**: Silent checks, only speaks up at thresholds
- **Configurable**: Adjust thresholds, frequency, and actions to your workflow
- **Stateful**: Tracks which thresholds warned, resets tracking when session resets

## Why You Need This

**Problem**: Context windows fill up silently. Once at 100%, sessions lock and stop responding. You lose work mid-task.

**Solution**: Proactive monitoring catches capacity issues early, giving you time to save work, switch channels, or reset cleanly.

**Real incident**: Discord #navi-code-yatta hit 97% capacity and locked mid-task (2026-02-23). Had to manually reset, losing conversation context.

## Configuration Examples

### Conservative (early warnings)
```markdown
Warning thresholds: 60%, 70%, 80%, 90%
Check frequency: Every 30 minutes
```

### Aggressive (maximize usage)
```markdown
Warning thresholds: 85%, 92%, 96%, 98%
Check frequency: Every 2 hours
```

### Channel-specific
```markdown
Discord channels: 75%, 85%, 90%, 95% (default)
Webchat: 85%, 95% (lighter warnings)
DM: 90%, 95% (minimal warnings)
```

## Future Features

- [ ] CLI tool for capacity reports
- [ ] Automatic session backups at thresholds
- [ ] Historical capacity tracking
- [ ] Cross-session capacity reports
- [ ] Integration with heartbeat monitoring
- [ ] Email/notification warnings
- [ ] Smart session rotation suggestions

## Requirements

- OpenClaw with `session_status` tool support
- Workspace with `AGENTS.md` file
- Active monitoring directive in agent instructions

## Support

- **Repo**: https://github.com/chrisagiddings/openclaw-tide-watch
- **Issues**: https://github.com/chrisagiddings/openclaw-tide-watch/issues
- **ClawHub**: https://clawhub.ai/chrisagiddings/tide-watch

## License

MIT
