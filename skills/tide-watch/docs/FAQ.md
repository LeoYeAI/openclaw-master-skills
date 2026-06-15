# Frequently Asked Questions

## Compatibility

### Q: Does this work with models other than Claude?

**Yes!** Tide Watch is model-agnostic. It works with:
- Anthropic (Claude Sonnet, Opus, Haiku)
- OpenAI (GPT-4, GPT-5, o1)
- DeepSeek (DeepSeek-Chat)
- Google (Gemini)
- Any other provider OpenClaw supports

The tool uses OpenClaw's `session_status` to read token usage, regardless of which model you're using.

### Q: Does it work with different context window sizes?

**Yes!** Tide Watch calculates capacity as a percentage:
```
percentage = (tokens_used / tokens_max) * 100
```

Works with:
- 128k context windows (GPT-4)
- 200k context windows (Claude Sonnet)
- 1M context windows (Gemini 1.5)
- Any size context window

Thresholds are percentage-based, not absolute token counts.

### Q: Can I use this with multiple OpenClaw instances?

**Yes!** Each OpenClaw instance has its own:
- AGENTS.md configuration
- HEARTBEAT.md schedule
- Session files
- Backup directories

Just install Tide Watch in each instance's skills folder.

## Configuration

### Q: Can I disable warnings temporarily?

**Yes, three ways:**

**1. Set check frequency to 'manual'** (in AGENTS.md):
```markdown
**Monitoring schedule:**
- Check frequency: **manual**
```
Disables automatic checking. You can still check manually.

**2. Remove from HEARTBEAT.md** (temporary):
Comment out the Tide Watch section:
```markdown
<!-- Tide Watch monitoring disabled temporarily
## 🌊 Tide Watch
...
-->
```

**3. Raise thresholds very high** (effectively disabling):
```markdown
**Warning thresholds:**
- **99%**: 🚨 Critical
```

### Q: Can I have different settings per channel?

**Yes!** Add channel-specific sections to AGENTS.md:

```markdown
**Discord channels:**
- Thresholds: 75%, 85%, 90%, 95%
- Frequency: Every 1 hour

**Webchat:**
- Thresholds: 85%, 95% (lighter warnings)
- Frequency: Every 2 hours
```

Tide Watch will use channel-specific settings when available, falling back to defaults.

### Q: How many thresholds can I configure?

**Between 2 and 6 thresholds.** Examples:

**Minimal** (2 thresholds):
```markdown
- **90%**: 🔴 High
- **95%**: 🚨 Critical
```

**Standard** (4 thresholds, default):
```markdown
- **75%**: 🟡 Warning
- **85%**: 🟠 Elevated
- **90%**: 🔴 High
- **95%**: 🚨 Critical
```

**Detailed** (6 thresholds):
```markdown
- **60%**: 🟡 Early
- **70%**: 🟡 Moderate
- **80%**: 🟠 Elevated
- **85%**: 🟠 High
- **90%**: 🔴 Very High
- **95%**: 🚨 Critical
```

Thresholds must be:
- In ascending order
- Between 50% and 99%
- Integers (no decimals)

## Backups

### Q: How do I restore from a backup?

**Manual restore:**

1. Find backups:
```bash
ls -lh ~/.openclaw/agents/main/sessions/backups/
```

2. Copy backup back to sessions directory:
```bash
cp backups/<session-id>-90-<timestamp>.jsonl <session-id>.jsonl
```

3. Restart OpenClaw or reconnect to the session

**Ask your agent:**
```
Show me available backups for this session
Restore from the 90% backup
```

### Q: Can I disable automatic backups?

**Yes**, set in AGENTS.md:
```markdown
**Auto-backup:**
- Enabled: false
```

You can still create manual backups via CLI:
```bash
cp ~/.openclaw/agents/main/sessions/<session-id>.jsonl ~/my-backups/
```

### Q: Where are backups stored?

**Default location:**
```
~/.openclaw/agents/main/sessions/backups/
```

**Format:**
```
<session-id>-<threshold>-<timestamp>.jsonl[.gz]
```

**Example:**
```
6eff94ac-dde7-90-20260223-170500.jsonl
```

### Q: How much disk space do backups use?

**Typical sizes:**
- Small session (< 50k tokens): 50-200 KB
- Medium session (50-150k tokens): 200-800 KB
- Large session (150k+ tokens): 1-3 MB

**With compression enabled:**
- Sizes reduce by ~70-80%
- Example: 1 MB → 200-300 KB

**Enable compression** in AGENTS.md:
```markdown
**Auto-backup:**
- Compress: true
```

### Q: Can I change backup retention?

**Yes**, edit AGENTS.md:
```markdown
**Auto-backup:**
- Retention: 14 days  # Keep backups for 2 weeks
```

Backups older than this are automatically deleted during cleanup.

## CLI Tool

### Q: Do I need to install the CLI separately?

**No**, it's included when you install Tide Watch.

**To make it globally available:**
```bash
cd ~/clawd/skills/tide-watch
npm link
```

Then use from anywhere:
```bash
tide-watch dashboard
```

### Q: Can I use the CLI without activating monitoring?

**Yes!** The CLI works independently:
- `tide-watch status` - Quick overview
- `tide-watch dashboard` - Visual capacity bars
- `tide-watch report` - Session list
- `tide-watch archive` - Clean up old sessions

Monitoring (AGENTS.md/HEARTBEAT.md setup) is optional.

### Q: Can I script the CLI output?

**Yes**, use JSON mode:
```bash
tide-watch dashboard --json --pretty > capacity-report.json
tide-watch report --json --threshold 90 | jq '.[] | {id: .sessionId, capacity: .percentage}'
```

Useful for:
- Custom dashboards
- Capacity alerts
- Analytics
- Integration with other tools

## Usage

### Q: What happens when a session hits 100%?

**Session locks.** OpenClaw stops responding because the context window is full.

**Recovery:**
1. Reset the session (start fresh)
2. Lost: Current conversation context
3. Preserved: Files, memory, backups

**This is why Tide Watch exists** - to warn you *before* hitting 100%.

### Q: Can I increase the context window size?

**Not directly.** Context window size is determined by:
- The model you're using
- The provider's limits

**But you can:**
- Switch to a model with larger context (e.g., Gemini 1.5 has 1M tokens)
- Use Tide Watch to manage capacity proactively
- Archive old sessions and start fresh
- Save important context to memory files

### Q: Will Tide Watch slow down my agent?

**No.** Monitoring overhead is minimal:
- Checks run once per hour (default)
- Each check takes < 100ms
- No network calls
- No external dependencies
- Silent when below thresholds

### Q: Can I use this in production/team deployments?

**Yes!** Tide Watch is designed for:
- Personal use (solo developers)
- Team deployments (shared OpenClaw instances)
- Production environments (CI/CD, automation)

**Recommendations for teams:**
- Use channel-specific settings
- Lower check frequency (reduce notification spam)
- Enable compression for backups
- Document your team's threshold preferences

## Customization

### Q: Can I change the warning messages?

**Currently no.** Warning messages are generated programmatically based on severity.

**Roadmap:** Custom message templates may be added in a future release.

**Workaround:** Fork the repo and modify `lib/monitoring.js` → `generateWarningMessage()`

### Q: Can I add custom actions to warnings?

**Yes, via AGENTS.md configuration.**

The warning message includes suggestions, and your agent will interpret them. You can customize the "Actions to suggest" section:

```markdown
**Actions to suggest:**
1. **Memory save**: Save current context to memory
2. **Custom action**: Your specific workflow step
3. **Session reset**: Provide reset instructions
```

### Q: Can I integrate Tide Watch with external tools?

**Yes, via CLI JSON output:**

```bash
# Export current capacity to Prometheus/Grafana
tide-watch status --json | jq '.sessions[] | {name, capacity: .percentage}' > metrics.json

# Send alerts to external service
tide-watch report --json --threshold 90 | curl -X POST https://my-alert-service.com/webhook -d @-

# Generate daily capacity report
tide-watch dashboard --json --pretty > "capacity-$(date +%Y%m%d).json"
```

## Troubleshooting

### Q: Why am I not seeing warnings?

See the [Troubleshooting Guide](TROUBLESHOOTING.md) for detailed diagnostics.

**Quick checks:**
1. Is AGENTS.md configured? `grep "TIDE WATCH" ~/clawd/AGENTS.md`
2. Is HEARTBEAT.md configured? `grep "Tide Watch" ~/clawd/HEARTBEAT.md`
3. Is check frequency set to 'manual'?
4. Have you already been warned at the current threshold?

### Q: Why is my capacity always 0%?

**Most common:** `session_status` tool not available in your OpenClaw version.

**Check:** Ask your agent:
```
Run session_status
```

If it fails, update OpenClaw to the latest version.

### Q: How do I uninstall Tide Watch?

**Remove from workspace:**
1. Delete the Tide Watch section from `~/clawd/AGENTS.md`
2. Delete the Tide Watch section from `~/clawd/HEARTBEAT.md`
3. (Optional) Remove skill folder: `rm -rf ~/clawd/skills/tide-watch`
4. (Optional) Unlink CLI: `npm unlink tide-watch`

**Clean up data:**
```bash
rm -rf ~/.openclaw/agents/main/sessions/backups/
rm -rf ~/.openclaw/agents/main/sessions/archive/
```

## Support

### Q: Where can I get help?

- **Documentation:** https://github.com/chrisagiddings/openclaw-tide-watch
- **Issues:** https://github.com/chrisagiddings/openclaw-tide-watch/issues
- **ClawHub:** https://clawhub.ai/chrisagiddings/tide-watch
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Q: Can I contribute?

**Yes!** Contributions welcome:
- Bug reports
- Feature requests
- Documentation improvements
- Code contributions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Q: Is Tide Watch free?

**Yes!** Tide Watch is open source (MIT License). Free to use, modify, and distribute.

No subscriptions, no API keys (besides your OpenClaw setup), no tracking.
