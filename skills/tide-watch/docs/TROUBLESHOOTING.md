# Troubleshooting Guide

Common issues and solutions for Tide Watch.

## Warnings Not Showing

**Symptom:** You never see capacity warnings, even at high capacity.

**Possible causes:**

### 1. AGENTS.md not configured
**Check:** Does your `~/clawd/AGENTS.md` contain the Tide Watch section?
```bash
grep "TIDE WATCH" ~/clawd/AGENTS.md
```

**Solution:** Add the template:
```bash
cat ~/clawd/skills/tide-watch/AGENTS.md.template >> ~/clawd/AGENTS.md
```

### 2. HEARTBEAT.md not configured
**Check:** Does your `~/clawd/HEARTBEAT.md` contain the Tide Watch task?
```bash
grep "Tide Watch" ~/clawd/HEARTBEAT.md
```

**Solution:** Add the template:
```bash
cat ~/clawd/skills/tide-watch/HEARTBEAT.md.template >> ~/clawd/HEARTBEAT.md
```

### 3. Check frequency set to 'manual'
**Check:** Look for `Check frequency: **manual**` in AGENTS.md

**Solution:** Change to a time interval (e.g., `Every 1 hour`)

### 4. Already warned at current threshold
**Explanation:** Tide Watch only warns once per threshold per session.

**Solution:** Capacity must cross the *next* threshold to trigger a new warning.

## Capacity Shows 0%

**Symptom:** CLI tools show 0% capacity or "0 / 0 tokens"

**Possible causes:**

### 1. session_status tool not available
**Check:** Ask your agent:
```
Run session_status
```

**Solution:** Update OpenClaw to a version that supports `session_status`.

### 2. Session has no usage data yet
**Explanation:** New sessions may not have token usage recorded.

**Solution:** This is normal for brand-new sessions. Data will appear after first assistant response.

### 3. Malformed session file
**Check:** Look for parsing errors:
```bash
tail -1 ~/.openclaw/agents/main/sessions/<session-id>.jsonl | jq .
```

**Solution:** If JSON is malformed, the session file may be corrupted. Contact OpenClaw support.

## Too Many Warnings

**Symptom:** Getting warnings too frequently or at capacities you don't care about.

**Solution:** Adjust thresholds in `AGENTS.md`:

**Example (less sensitive):**
```markdown
**Warning thresholds:**
- **85%**: 🟠 Warning
- **95%**: 🚨 Critical
```

**Or increase check frequency:**
```markdown
**Monitoring schedule:**
- Check frequency: Every 2 hours
```

## Warnings Too Infrequent

**Symptom:** Not getting warned until it's too late.

**Solution:** Lower thresholds and increase check frequency:

```markdown
**Warning thresholds:**
- **60%**: 🟡 Early warning
- **75%**: 🟠 Mid warning
- **85%**: 🔴 High warning
- **95%**: 🚨 Critical

**Monitoring schedule:**
- Check frequency: Every 30 minutes
```

## Backups Not Being Created

**Symptom:** Auto-backup is enabled but no backups appear.

**Possible causes:**

### 1. Auto-backup disabled
**Check:** Look in AGENTS.md:
```markdown
**Auto-backup:**
- Enabled: false  # ← Disabled
```

**Solution:** Set to `true`:
```markdown
- Enabled: true
```

### 2. Capacity below backup triggers
**Check:** What are your backup triggers?
```markdown
- Trigger at thresholds: [90, 95]
```

**Explanation:** Backups only trigger when capacity crosses these specific thresholds.

**Solution:** Add lower thresholds if you want earlier backups:
```markdown
- Trigger at thresholds: [75, 85, 90, 95]
```

### 3. Already backed up at current threshold
**Explanation:** Each threshold only triggers one backup per session.

**Solution:** Capacity must cross the *next* backup trigger to create another backup.

## CLI Commands Not Working

**Symptom:** `tide-watch` command not found

**Possible causes:**

### 1. Not installed globally
**Solution:** Install or link:
```bash
cd ~/clawd/skills/tide-watch
npm link
```

### 2. npm global bin not in PATH
**Check:** Is npm global bin in your PATH?
```bash
npm config get prefix
```

**Solution:** Add to your PATH:
```bash
echo 'export PATH="$PATH:$(npm config get prefix)/bin"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Using relative path without ./
**Solution:** Use absolute path or npm link:
```bash
node ~/clawd/skills/tide-watch/bin/tide-watch dashboard
```

## Dashboard Shows "unknown" Channel

**Symptom:** Dashboard displays "unknown" instead of channel names.

**Explanation:** Older sessions may not have channel metadata in their session files.

**Solution:** This is normal for sessions created before channel tracking was added. New sessions will show proper channel names.

**To verify:** Check a recent session:
```bash
tide-watch check --session <recent-session-id>
```

## Archive Command Fails

**Symptom:** `tide-watch archive` fails with permission errors

**Possible causes:**

### 1. Session files in use
**Solution:** Close the affected sessions before archiving.

### 2. No write permission to archive directory
**Solution:** Check permissions:
```bash
ls -ld ~/.openclaw/agents/main/sessions/
```

### 3. Disk full
**Solution:** Check disk space:
```bash
df -h ~
```

## Configuration Changes Not Taking Effect

**Symptom:** Changed thresholds in AGENTS.md but warnings haven't changed

**Explanation:** Configuration is parsed on each heartbeat check, not immediately.

**Solution:** Wait for the next scheduled check, or manually trigger:
```
Check session capacity
```

**Verification:** Ask your agent:
```
What are my configured Tide Watch thresholds?
```

## Getting Help

If you're still stuck:

1. **Check the logs:** Look for errors in OpenClaw output
2. **Test manually:** Ask agent to check capacity explicitly
3. **Validate config:** Check AGENTS.md syntax (proper Markdown formatting)
4. **File an issue:** https://github.com/chrisagiddings/openclaw-tide-watch/issues

Include:
- OpenClaw version
- Tide Watch version
- Relevant AGENTS.md/HEARTBEAT.md sections
- Error messages or unexpected behavior
- Output from `tide-watch status`
