# Tide Watch Installation Guide

Step-by-step instructions for setting up proactive session capacity monitoring.

---

## Prerequisites

- OpenClaw installed and configured
- Workspace with `AGENTS.md` file (usually `~/clawd/`)
- `HEARTBEAT.md` file in workspace (create if doesn't exist)

---

## Installation

### Option 1: ClawHub (Recommended)

```bash
clawhub install tide-watch
```

Then skip to **Configuration** below.

### Option 2: Manual Installation

1. **Clone the repository:**
   ```bash
   cd ~/clawd/skills  # or your skills directory
   git clone https://github.com/chrisagiddings/openclaw-tide-watch tide-watch
   ```

2. **Add monitoring directive to AGENTS.md:**
   ```bash
   cd ~/clawd  # your workspace root
   cat skills/tide-watch/AGENTS.md.template >> AGENTS.md
   ```

3. **Add heartbeat task to HEARTBEAT.md:**
   ```bash
   # If HEARTBEAT.md doesn't exist, create it:
   touch HEARTBEAT.md
   
   # Add Tide Watch heartbeat task:
   cat skills/tide-watch/HEARTBEAT.md.template >> HEARTBEAT.md
   ```

---

## Configuration

### Default Settings (No Changes Needed)

The default configuration works for most users:

- **Warning thresholds:** 75%, 85%, 90%, 95%
- **Check frequency:** Every 1 hour
- **Auto-backup:** Enabled, triggers at [90, 95], 7-day retention

If defaults work for you, **you're done!** Tide Watch is now monitoring your sessions.

### Custom Configuration

Edit the Tide Watch section in your `AGENTS.md` to customize:

#### 1. Warning Thresholds (when to warn)

**Conservative (early warnings):**
```markdown
**Warning thresholds:**
- **60%**: 🟡 Heads up
- **70%**: 🟠 Action recommended
- **80%**: 🔴 Urgent
- **90%**: 🚨 Critical
```

**Aggressive (maximize usage):**
```markdown
**Warning thresholds:**
- **85%**: 🟡 Heads up
- **92%**: 🟠 Action recommended
- **96%**: 🔴 Urgent
- **98%**: 🚨 Critical
```

**Minimalist (fewer interruptions):**
```markdown
**Warning thresholds:**
- **80%**: 🟠 Warning
- **95%**: 🚨 Critical
```

#### 2. Check Frequency (how often to monitor)

**Aggressive (tight feedback loop):**
```markdown
**Monitoring schedule:**
- Check frequency: Every 15 minutes
```

**Relaxed (minimal overhead):**
```markdown
**Monitoring schedule:**
- Check frequency: Every 2 hours
```

**Manual only (disable heartbeat):**
```markdown
**Monitoring schedule:**
- Check frequency: manual
```

Then ask your agent to check capacity only when needed:
```
What's my current session capacity?
```

#### 3. Auto-Backup Configuration

Configure automatic session backups:

**Enable/disable backups:**
```markdown
**Auto-backup:**
- Enabled: true  # Set false to disable
```

**Configure backup triggers:**
```markdown
**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [90, 95]  # When to create backups
```

**Conservative (backup at every warning):**
```markdown
- Trigger at thresholds: [75, 85, 90, 95]
```

**Aggressive (last-chance only):**
```markdown
- Trigger at thresholds: [95]
```

**Configure retention:**
```markdown
**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [90, 95]
- Retention: 7 days  # Auto-delete backups older than this
- Compress: false  # Set true to save disk space
```

**Longer retention (30 days):**
```markdown
- Retention: 30 days
```

**Restore from backup:**

To restore a previous session state:
```
Show me available backups for this session
Restore session from 90% backup
```

Your agent will guide you through the restoration process.

**Backup locations:**
- Path: `~/.openclaw/agents/main/sessions/backups/`
- Format: `<session-id>-<threshold>-<timestamp>.jsonl`
- Example: `6eff94ac-90-20260223-170500.jsonl`

#### 4. Channel-Specific Settings (advanced)

Different settings per channel:

```markdown
## 🌊 TIDE WATCH: Context Window Monitoring

**Default settings:**
- Check frequency: Every 1 hour
- Warning thresholds: 75%, 85%, 90%, 95%

**Channel overrides:**

**Discord channels:**
- Check frequency: Every 30 minutes  # More aggressive
- Warning thresholds: 70%, 80%, 90%, 95%

**Webchat:**
- Check frequency: Every 2 hours  # More relaxed
- Warning thresholds: 85%, 95%  # Fewer warnings

**DM (direct messages):**
- Check frequency: manual  # Only check when asked
```

---

## Verification

After installation, test that Tide Watch is working:

### 1. Check Heartbeat is Running

Ask your agent:
```
Check if Tide Watch heartbeat is configured
```

Or manually check:
```bash
cat ~/clawd/HEARTBEAT.md | grep "Tide Watch"
```

You should see the monitoring task listed.

### 2. Manual Capacity Check

Ask your agent:
```
What's my current session capacity?
```

You should get a response like:
```
Context: 45k/200k (22%)
Status: All good, plenty of room!
```

### 3. Wait for First Heartbeat

The first automatic check will happen at your configured interval (default: 1 hour).

If capacity is below all thresholds, you won't see any output (silent operation).

If capacity crosses a threshold, you'll receive a warning:
```
🟡 Heads up: Context at 75%. Consider wrapping up or switching channels soon.
```

---

## Troubleshooting

### Warnings Not Appearing

**Check AGENTS.md:**
```bash
cat ~/clawd/AGENTS.md | grep "TIDE WATCH"
```

Should show the monitoring directive. If not, re-run:
```bash
cat skills/tide-watch/AGENTS.md.template >> AGENTS.md
```

**Check HEARTBEAT.md:**
```bash
cat ~/clawd/HEARTBEAT.md | grep "Tide Watch"
```

Should show the heartbeat task. If not, re-run:
```bash
cat skills/tide-watch/HEARTBEAT.md.template >> HEARTBEAT.md
```

### Capacity Shows 0%

Your session hasn't accumulated enough conversation yet. Try again after some back-and-forth with your agent.

### Too Many Warnings

Adjust thresholds to be less aggressive:
```markdown
**Warning thresholds:**
- **85%**: 🟠 Action recommended
- **95%**: 🚨 Critical
```

Or increase check frequency:
```markdown
**Monitoring schedule:**
- Check frequency: Every 2 hours
```

### Not Enough Warnings

Adjust thresholds to be more aggressive:
```markdown
**Warning thresholds:**
- **60%**: 🟡 Heads up
- **70%**: 🟠 Action recommended
- **80%**: 🔴 Urgent
- **90%**: 🚨 Critical
```

Or decrease check frequency:
```markdown
**Monitoring schedule:**
- Check frequency: Every 30 minutes
```

---

## Next Steps

### Use Memory Saves

When warned at 90%+, save important context:
```
Save current conversation context to memory
```

### Reset Session Cleanly

When warned at 95%:
```
Help me reset this session and preserve context
```

Your agent will:
1. Save context to memory
2. Backup session file
3. Provide session resumption prompt
4. Reset the session

### Explore Advanced Features

- **Auto-backup** (coming soon): Automatic session backups at thresholds
- **CLI tool** (coming soon): Terminal commands for capacity reports
- **Notifications** (coming soon): Email/Discord alerts for critical thresholds

---

## Support

- **GitHub Issues**: https://github.com/chrisagiddings/openclaw-tide-watch/issues
- **Documentation**: https://github.com/chrisagiddings/openclaw-tide-watch
- **ClawHub**: https://clawhub.ai/chrisagiddings/tide-watch

---

**Made with 🌊 for the OpenClaw community**
