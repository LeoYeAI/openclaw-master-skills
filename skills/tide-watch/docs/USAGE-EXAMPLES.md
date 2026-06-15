# Usage Examples

Real-world scenarios and practical examples for Tide Watch.

## Scenario 1: Solo Developer (Personal Use)

**Profile:**
- Working on coding projects
- Uses Discord for #dev-work channel
- Wants proactive warnings
- Prefers minimal interruptions

**Configuration** (`AGENTS.md`):
```markdown
## 🌊 TIDE WATCH: Context Window Monitoring

**Monitoring schedule:**
- Check frequency: **Every 1 hour**

**Warning thresholds:**
- **75%**: 🟡 "Heads up: Context at 75%"
- **85%**: 🟠 "Context at 85%"
- **90%**: 🔴 "Context at 90%!"
- **95%**: 🚨 "CRITICAL: Context at 95%!"

**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [90, 95]
- Retention: 7 days
- Compress: false
```

**Workflow:**
1. Working on project in Discord channel
2. At 75%: Notice warning, wrap up non-critical tasks
3. At 85%: Finish current feature, save to memory
4. At 90%: Auto-backup triggers, prepare to reset
5. At 95%: Save all context, reset session

**CLI usage:**
```bash
# Quick morning check
tide-watch status

# Before starting heavy work
tide-watch dashboard --active 24

# End of day cleanup
tide-watch archive --older-than 7d --dry-run
tide-watch archive --older-than 7d
```

## Scenario 2: Multi-Channel Power User

**Profile:**
- Uses multiple channels (Discord, webchat, Telegram)
- Switches contexts frequently
- Wants different settings per channel

**Configuration** (`AGENTS.md`):
```markdown
## 🌊 TIDE WATCH: Context Window Monitoring

**Default settings:**
- Check frequency: **Every 1 hour**
- Thresholds: 75%, 85%, 90%, 95%

**Discord channels:**
- Check frequency: **Every 30 minutes**
- Thresholds: 70%, 80%, 90%, 95%
- Reason: Long conversations, need earlier warnings

**Webchat:**
- Check frequency: **Every 2 hours**
- Thresholds: 85%, 95%
- Reason: Quick interactions, fewer warnings needed

**Telegram:**
- Check frequency: **manual**
- Reason: Rarely used, check manually only
```

**Dashboard usage:**
```bash
# Check all active sessions
tide-watch dashboard

# Focus on recent activity only
tide-watch dashboard --active 48

# Watch mode during intensive work
tide-watch dashboard --watch

# Export report for analysis
tide-watch dashboard --json --pretty > capacity-$(date +%Y%m%d).json
```

**Workflow:**
- Discord: Proactive monitoring, early warnings
- Webchat: Lighter monitoring, late warnings
- Telegram: Manual checks only

## Scenario 3: Mobile-First User

**Profile:**
- Accesses OpenClaw from phone/tablet often
- Filesystem not always available
- Needs all info in-session

**Configuration** (`AGENTS.md`):
```markdown
**Monitoring schedule:**
- Check frequency: **Every 30 minutes**  # More frequent checks

**Warning thresholds:**
- **70%**: 🟡 Early warning (mobile-friendly)
- **80%**: 🟠 Moderate warning
- **90%**: 🔴 High warning
- **95%**: 🚨 Critical

**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [80, 90, 95]  # More backup points
- Retention: 14 days  # Longer retention (can't easily access filesystem)
- Compress: true  # Save mobile data/storage
```

**Key adaptations:**
- Earlier warnings (70% instead of 75%)
- More frequent checks (30 min instead of 1 hour)
- More backup triggers (80%, 90%, 95%)
- Longer retention (14 days instead of 7)
- Compression enabled (save space)

**Workflow:**
- Agent provides full reset instructions in-session
- No reliance on local filesystem access
- More checkpoints via backups

## Scenario 4: Team/Shared Instance

**Profile:**
- Multiple team members using shared OpenClaw
- Different workflows and preferences
- Need to balance everyone's needs

**Configuration** (`AGENTS.md`):
```markdown
## 🌊 TIDE WATCH: Context Window Monitoring

**Team settings:**
- Check frequency: **Every 2 hours**  # Reduced frequency for shared use
- Thresholds: 80%, 90%, 95%  # Fewer warnings to reduce noise

**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [90, 95]
- Retention: 14 days  # Longer retention for team recovery
- Compress: true  # Save shared storage

**Channel-specific:**
**#team-general:**
- Thresholds: 85%, 95%  # Light warnings for casual chat

**#development:**
- Thresholds: 75%, 85%, 90%, 95%  # Full warnings for coding sessions
```

**Admin workflows:**
```bash
# Daily capacity report
tide-watch report --all > daily-capacity-$(date +%Y%m%d).txt

# Monitor high-capacity sessions
tide-watch report --threshold 85 --json | jq -r '.[] | "\(.channel): \(.percentage)%"'

# Weekly cleanup
tide-watch archive --older-than 14d --exclude-channel development --dry-run
tide-watch archive --older-than 14d --exclude-channel development

# Check backup usage
du -sh ~/.openclaw/agents/main/sessions/backups/
```

**Best practices:**
- Document team conventions in AGENTS.md
- Regular cleanup (archive old sessions)
- Monitor shared backup storage
- Channel-specific settings per use case

## Scenario 5: Heavy Project Work

**Profile:**
- Deep dives into complex projects
- Reading many files
- Generating long outputs
- High capacity usage

**Configuration** (`AGENTS.md`):
```markdown
**Monitoring schedule:**
- Check frequency: **Every 30 minutes**  # Frequent checks
- Also check during **intensive project work**

**Warning thresholds:**
- **60%**: 🟡 Early warning (aggressive)
- **70%**: 🟡 Moderate warning
- **80%**: 🟠 Elevated warning
- **90%**: 🔴 High warning
- **95%**: 🚨 Critical

**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [60, 70, 80, 90, 95]  # All thresholds
- Retention: 7 days
- Compress: false  # Fast backup/restore
```

**Workflow:**
```bash
# Before starting project work
tide-watch dashboard

# During work (live monitoring)
tide-watch dashboard --watch

# If capacity climbs quickly
# Ask agent: "Save current progress to memory and provide reset prompt"

# After reset (optional cleanup)
tide-watch archive --older-than 1d --dry-run  # Review what would be archived
```

**Strategies:**
- More aggressive thresholds (start at 60%)
- Frequent checks (30 minutes)
- Backup at every threshold (safety net)
- Manual checks during intensive work
- Proactive memory saves

## Scenario 6: Minimal Monitoring (Manual Mode)

**Profile:**
- Experienced user
- Knows capacity management well
- Prefers manual control
- Doesn't want automatic checks

**Configuration** (`AGENTS.md`):
```markdown
**Monitoring schedule:**
- Check frequency: **manual**  # Disable automatic checks

**Warning thresholds:**
- **90%**: 🔴 High
- **95%**: 🚨 Critical

**Auto-backup:**
- Enabled: false  # Manual backups only
```

**Usage:**
```bash
# Manual CLI checks
tide-watch status  # Quick overview
tide-watch check --session <session-id>  # Specific session

# Periodic dashboard check
tide-watch dashboard

# Manual backup before risky operations
cp ~/.openclaw/agents/main/sessions/<session-id>.jsonl ~/backups/
```

**Workflow:**
- Check manually when starting new project
- Check when generating large outputs
- Check before/after intensive work
- No automatic interruptions

## Scenario 7: Archive Management

**Keeping workspace clean:**

```bash
# Daily routine: Archive sessions older than 4 days
tide-watch archive --older-than 4d --dry-run  # Preview
tide-watch archive --older-than 4d            # Execute

# Weekly routine: Archive old low-capacity sessions
tide-watch archive --older-than 7d --min-capacity 50 --dry-run
tide-watch archive --older-than 7d --min-capacity 50

# Keep important channels, archive rest
tide-watch archive --older-than 7d --exclude-channel discord

# Monthly cleanup: Remove very old archives
find ~/.openclaw/agents/main/sessions/archive/ -mtime +30 -type d -exec rm -rf {} +
```

## Scenario 8: Capacity Analysis

**Using CLI for analytics:**

```bash
# Current capacity across all sessions
tide-watch report --all --json | jq '.[] | {channel, capacity: .percentage, tokens: .tokensUsed}'

# Sessions above 75%
tide-watch report --threshold 75 --json | jq 'length'  # Count
tide-watch report --threshold 75 --json | jq -r '.[] | "\(.channel): \(.percentage)%"'

# Recent activity only
tide-watch dashboard --active 24 --json | jq '.sessions | length'

# Export for spreadsheet analysis
tide-watch report --all --json --pretty > capacity-report-$(date +%Y%m%d).json
```

## Scenario 9: Flexible Session Lookup

**Using human-friendly session identifiers:**

```bash
# Instead of remembering full UUIDs...
tide-watch check --session 6eff94ac-dde7-4621-acaf-66bb431db822  # ❌ Hard to remember

# Use shorter, human-friendly identifiers! ✅

# By shortened ID (first 8+ characters)
tide-watch check --session 6eff94ac

# By Discord/Telegram channel label
tide-watch check --session "#navi-code-yatta"
tide-watch resume-prompt edit --session "#dev-work"

# By channel name (if you only have one)
tide-watch check --session discord
tide-watch check --session webchat

# By channel + label combo
tide-watch check --session "discord/#navi-code-yatta"
tide-watch resume-prompt show --session "telegram/#personal"

# Works across all commands
tide-watch resume-prompt edit --session "#navi-code-yatta"
tide-watch resume-prompt show --session discord
tide-watch resume-prompt info --session webchat
tide-watch resume-prompt delete --session "#old-project"
tide-watch resume-prompt enable --session slack
tide-watch resume-prompt status --session "#dev-work"
```

**Practical workflow:**

```bash
# Morning routine: Check your main channels by name
tide-watch check --session discord
tide-watch check --session webchat

# During work: Use labels for specific projects
tide-watch resume-prompt edit --session "#yatta-development"
tide-watch check --session "#client-project"

# Evening cleanup: Archive by channel
tide-watch report --json | jq -r '.[] | select(.channel=="telegram") | .sessionId' | \
  while read sid; do
    tide-watch archive --older-than 3d --session "$sid"
  done
```

**Handling ambiguous matches:**

```bash
# If you have multiple Discord sessions:
$ tide-watch check --session discord

❌ Multiple sessions match "discord". Please be more specific.

Matching sessions:
  1. discord/#navi-code-yatta (6eff94ac)
  2. discord/#general (a3b2c1d4)
  3. discord/#dev-work (e5f6a7b8)

# Solution: Use more specific identifier
tide-watch check --session "#navi-code-yatta"        # By label
tide-watch check --session "discord/#general"        # By combo
tide-watch check --session 6eff94ac                  # By shortened ID
```

**Benefits:**
- **No UUID memorization** - use labels/channels you already know
- **Faster typing** - `#dev-work` instead of 40-character UUID
- **Human-readable scripts** - easy to understand automation
- **Helpful errors** - shows matches when ambiguous

## Scenario 10: Integration with Scripts

**Automated capacity monitoring:**

```bash
#!/bin/bash
# capacity-check.sh - Run periodically via cron

THRESHOLD=85
HIGH_CAPACITY=$(tide-watch report --threshold $THRESHOLD --json | jq 'length')

if [ "$HIGH_CAPACITY" -gt 0 ]; then
    echo "⚠️  $HIGH_CAPACITY sessions above ${THRESHOLD}%"
    tide-watch report --threshold $THRESHOLD
    
    # Optional: Send notification
    # tide-watch report --threshold $THRESHOLD --json | \
    #   curl -X POST https://my-webhook.com/alerts -d @-
fi
```

**Add to crontab:**
```bash
# Check capacity every 4 hours
0 */4 * * * /path/to/capacity-check.sh
```

## Scenario 11: Emergency Recovery

**Session locked at 100%:**

```bash
# 1. Check what sessions exist
tide-watch report --all

# 2. Check if backups available
ls -lh ~/.openclaw/agents/main/sessions/backups/<session-id>-*

# 3. Restore from most recent backup
LATEST=$(ls -t ~/.openclaw/agents/main/sessions/backups/<session-id>-* | head -1)
cp "$LATEST" ~/.openclaw/agents/main/sessions/<session-id>.jsonl

# 4. Restart OpenClaw or reconnect to session

# 5. Verify capacity after restore
tide-watch check --session <session-id>
```

**Prevention for next time:**
- Enable auto-backup at lower thresholds
- More frequent capacity checks
- Respond to warnings earlier

## Summary

**Key Patterns:**
- **Configuration drives behavior** - adjust to your workflow
- **CLI complements monitoring** - use both together
- **Backups are safety nets** - enable for important work
- **Archive keeps things clean** - regular maintenance
- **Channel-specific settings** - optimize per use case

**Choose your approach:**
- **Cautious:** Frequent checks, early thresholds, many backups
- **Balanced:** Default settings work for most users
- **Aggressive:** Late thresholds, maximize context usage
- **Manual:** Disable automatic monitoring, check manually

Adapt these examples to your workflow!
