# Configuration Parsing Guide

How Tide Watch parses your custom configuration from `AGENTS.md`.

---

## Overview

Tide Watch dynamically reads your configuration every time it checks capacity. This means:
- Changes to `AGENTS.md` take effect on the next check
- No need to restart OpenClaw
- Each session can have different settings

---

## Warning Thresholds

### What It Looks For

```markdown
**Warning thresholds:**
- **75%**: 🟡 "Heads up..."
- **85%**: 🟠 "Action recommended..."
- **90%**: 🔴 "Urgent..."
- **95%**: 🚨 "Critical..."
```

### Parsing Logic

1. **Find section:** Looks for `**Warning thresholds:**`
2. **Extract percentages:** Scans for lines matching `- **XX%**:`
3. **Build array:** `[75, 85, 90, 95]`
4. **Validate:**
   - Ascending order? ✓
   - Range 50-99%? ✓
   - 2-6 thresholds? ✓
5. **Store:** Use these thresholds for monitoring

### Validation Rules

| Rule | Valid | Invalid |
|------|-------|---------|
| Ascending | `[70, 80, 90]` | `[90, 80, 70]` |
| Range | `[60, 75, 90]` | `[30, 50, 105]` |
| Count | `[80, 95]` (2) or `[70,75,80,85,90,95]` (6) | `[95]` (1) or 7+ thresholds |

### Fallback Behavior

If parsing fails or validation fails:
```
Warning: Invalid threshold configuration
Using defaults: [75, 85, 90, 95]
```

---

## Check Frequency

### What It Looks For

```markdown
**Monitoring schedule:**
- Check frequency: Every 1 hour
```

### Parsing Logic

1. **Find section:** Looks for `- Check frequency:`
2. **Extract value:** Parses `Every N minutes` or `Every N hours` or `manual`
3. **Convert to minutes:**
   - `Every 15 minutes` → 15
   - `Every 1 hour` → 60
   - `Every 2 hours` → 120
   - `manual` → heartbeat disabled
4. **Validate:**
   - Range: 5-360 minutes? ✓
5. **Store:** Use this interval for heartbeat checks

### Supported Formats

| Format | Result |
|--------|--------|
| `Every 15 minutes` | Check every 15 minutes |
| `Every 30 minutes` | Check every 30 minutes |
| `Every 1 hour` | Check every 60 minutes |
| `Every 2 hours` | Check every 120 minutes |
| `manual` | Heartbeat disabled, manual only |

### Validation Rules

| Rule | Valid | Invalid |
|------|-------|---------|
| Minimum | 5 minutes | 2 minutes |
| Maximum | 6 hours (360 min) | 12 hours |
| Format | `Every N units` | `Check N times` |

### Fallback Behavior

If parsing fails or validation fails:
```
Warning: Invalid frequency configuration
Using default: Every 1 hour (60 minutes)
```

If set to `manual`:
```
Tide Watch heartbeat disabled (frequency set to 'manual')
User must explicitly request capacity checks
```

---

## Auto-Backup Configuration

### What It Looks For

```markdown
**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [90, 95]
- Retention: 7 days
- Compress: false
```

### Parsing Logic

**Enabled:**
1. **Find:** `- Enabled: true` or `- Enabled: false`
2. **Default:** `true` if not found

**Trigger thresholds:**
1. **Find:** `- Trigger at thresholds: [XX, YY]`
2. **Extract:** Numbers from within brackets
3. **Validate:**
   - Must be subset of warning thresholds ✓
   - Ascending order ✓
   - Range 50-99% ✓
4. **Default:** `[90, 95]` if not found or invalid

**Retention:**
1. **Find:** `- Retention: N days`
2. **Extract:** Number of days
3. **Validate:** Range 1-365 days
4. **Default:** `7` if not found or invalid

**Compress:**
1. **Find:** `- Compress: true` or `- Compress: false`
2. **Default:** `false` if not found

### Validation Rules

**Trigger thresholds must be subset of warning thresholds:**

✅ Valid:
```markdown
**Warning thresholds:** [75, 85, 90, 95]
**Auto-backup trigger:** [90, 95]  ← subset
```

❌ Invalid:
```markdown
**Warning thresholds:** [75, 85, 90, 95]
**Auto-backup trigger:** [88, 93]  ← not in warning set
```

**Retention must be reasonable:**

| Range | Valid | Invalid |
|-------|-------|---------|
| Minimum | 1 day | 0 days |
| Maximum | 365 days | 1000 days |

### Fallback Behavior

If backup triggers are invalid:
```
Warning: Invalid backup trigger configuration
Using defaults: [90, 95]
```

If retention is invalid:
```
Warning: Invalid retention value
Using default: 7 days
```

---

## Dynamic Warning Severity

Tide Watch assigns severity levels based on threshold **position**, not hardcoded percentages.

### Severity Assignment

| Position | Emoji | Severity | Urgency |
|----------|-------|----------|---------|
| First (lowest) | 🟡 | Early warning | Low |
| Middle | 🟠 | Action recommended | Medium |
| Second-to-last | 🔴 | Urgent | High |
| Last (highest) | 🚨 | Critical | Critical |

### Examples

**Default thresholds `[75, 85, 90, 95]`:**
- 75% = 🟡 Early warning (first)
- 85% = 🟠 Action recommended (middle)
- 90% = 🔴 Urgent (second-to-last)
- 95% = 🚨 Critical (last)

**Minimalist `[80, 95]`:**
- 80% = 🟡 Early warning (first)
- 95% = 🚨 Critical (last)

**Conservative `[60, 70, 80, 90, 95]`:**
- 60% = 🟡 Early warning (first)
- 70% = 🟠 Action recommended (middle)
- 80% = 🟠 Action recommended (middle)
- 90% = 🔴 Urgent (second-to-last)
- 95% = 🚨 Critical (last)

**Aggressive `[85, 92, 96, 98]`:**
- 85% = 🟡 Early warning (first)
- 92% = 🟠 Action recommended (middle)
- 96% = 🔴 Urgent (second-to-last)
- 98% = 🚨 Critical (last)

### Warning Messages

Messages adapt to the threshold percentage:

```
🟡 "Heads up: Context at {X}%. Consider wrapping up or switching channels soon."
🟠 "Context at {X}%. Recommend finishing current task and resetting session."
🔴 "Context at {X}%! Session will lock at 100%. Ready to help you reset?"
🚨 "CRITICAL: Context at {X}%! Save important info to memory NOW and reset."
```

---

## Testing Your Configuration

### 1. Check Parsing

Ask your agent:
```
What are my current Tide Watch threshold settings?
Show me my Tide Watch configuration
```

Expected response:
```
Tide Watch Configuration:
- Check frequency: Every 1 hour
- Warning thresholds: [75, 85, 90, 95]
- Auto-backup: Enabled
- Backup triggers: [90, 95]
- Retention: 7 days
- Compress: false
```

### 2. Trigger a Warning (Testing)

Temporarily set very low thresholds to test:
```markdown
**Warning thresholds:**
- **10%**: 🟡 Test warning
- **20%**: 🚨 Test critical
```

Your agent should warn you immediately on next check.

**Don't forget to restore normal thresholds after testing!**

### 3. Check Backup Functionality

Enable verbose logging temporarily:
```
Show me when backups are triggered
```

When capacity crosses backup thresholds, you should see:
```
✅ Session backed up: 6eff94ac-90-20260223-170500.jsonl
Trigger: 90% threshold crossed
Size: 1.6 MB
```

---

## Troubleshooting

### "Using defaults" Message

**Symptom:** Agent says "Invalid configuration, using defaults"

**Causes:**
1. **Typo in AGENTS.md** — Check syntax carefully
2. **Thresholds not ascending** — Must be increasing order
3. **Thresholds out of range** — Must be 50-99%
4. **Too few/many thresholds** — Need 2-6 thresholds

**Fix:** Review your AGENTS.md against examples in this guide

### Warnings Not Appearing

**Check:**
1. Is heartbeat enabled? (`Check frequency` not set to `manual`)
2. Has enough time passed? (Default: 1 hour between checks)
3. Is capacity actually crossing thresholds? (Ask: `What's my current capacity?`)

### Backups Not Creating

**Check:**
1. Is backup enabled? (`Enabled: true`)
2. Have backup triggers been crossed? (Check current capacity)
3. Are backup triggers valid? (Must be subset of warning thresholds)
4. Is disk space available? (Check: `~/.openclaw/agents/main/sessions/backups/`)

---

## Advanced: Channel-Specific Overrides

You can configure different settings per channel:

```markdown
## 🌊 TIDE WATCH: Context Window Monitoring

**Default settings:**
- Check frequency: Every 1 hour
- Warning thresholds: [75, 85, 90, 95]

**Channel overrides:**

**Discord channels:**
- Check frequency: Every 30 minutes
- Warning thresholds: [70, 80, 90, 95]

**Webchat:**
- Check frequency: Every 2 hours
- Warning thresholds: [85, 95]
```

**Parsing:**
1. Check current channel type (Discord, webchat, DM, etc.)
2. Look for channel-specific section
3. If found, use override values
4. If not found, use default values

**This feature requires:** Channel detection logic (future enhancement)

---

## Summary

| Configuration | Default | Validation | Fallback |
|--------------|---------|------------|----------|
| Warning thresholds | `[75, 85, 90, 95]` | Ascending, 50-99%, 2-6 values | Defaults |
| Check frequency | `Every 1 hour` | 5-360 min or `manual` | 60 minutes |
| Backup enabled | `true` | Boolean | true |
| Backup triggers | `[90, 95]` | Subset of warnings, ascending | `[90, 95]` |
| Retention | `7 days` | 1-365 days | 7 |
| Compress | `false` | Boolean | false |

**Key principle:** If parsing fails at any stage, fall back to safe defaults and continue monitoring.
