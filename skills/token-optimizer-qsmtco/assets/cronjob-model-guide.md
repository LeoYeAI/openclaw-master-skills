# Cronjob Model Selection Guide

When creating cronjobs in OpenClaw, always specify the cheapest appropriate model.

## General Rule

**90% of cronjobs should use Quick tier** — they're routine operations that don't need complex reasoning.

## Model Selection by Task Type

### ALWAYS Quick (Never Standard/Deep)

**Monitoring & Alerts:**
```bash
# Check server health
cron add --schedule "*/15 * * * *" \
  --payload '{"kind":"agentTurn","message":"Check server status","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated

# Monitor disk space
cron add --schedule "0 */4 * * *" \
  --payload '{"kind":"agentTurn","message":"Check disk usage on all servers","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated
```

**Data Processing:**
```bash
# Parse daily logs
cron add --schedule "0 2 * * *" \
  --payload '{"kind":"agentTurn","message":"Parse yesterday's error logs and summarize","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated

# Process CSV reports
cron add --schedule "0 8 * * 1" \
  --payload '{"kind":"agentTurn","message":"Extract data from weekly_report.csv","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated
```

**Reminders & Notifications:**
```bash
# Daily standup reminder
cron add --schedule "0 9 * * 1-5" \
  --payload '{"kind":"systemEvent","text":"Reminder: Daily standup in 30 minutes"}' \
  --sessionTarget main

# Weekly backup reminder
cron add --schedule "0 18 * * 5" \
  --payload '{"kind":"agentTurn","message":"Remind user to verify backups","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated
```

**Document Extraction:**
```bash
# Extract invoices
cron add --schedule "0 10 * * *" \
  --payload '{"kind":"agentTurn","message":"Parse new invoices from inbox and extract totals","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated
```

### Sometimes Standard (Rarely Needed)

**Content Generation:**
```bash
# Daily blog summary (needs better quality)
cron add --schedule "0 7 * * *" \
  --payload '{"kind":"agentTurn","message":"Write a summary of yesterday's blog posts","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated
```

**Analysis with Context:**
```bash
# Weekly performance analysis (needs reasoning)
cron add --schedule "0 9 * * 1" \
  --payload '{"kind":"agentTurn","message":"Analyze last week's metrics and provide insights","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated
```

### NEVER Deep (Too Expensive for Scheduled Tasks)

Deep (e.g., openrouter/minimax/minimax-m2.5) should NEVER be used for cronjobs. If a task needs Deep-level reasoning, it's probably too complex for automation — let the user trigger it manually.

## Configuration Pattern

### For agentTurn payload (isolated session):
```json
{
  "kind": "agentTurn",
  "message": "Your task description",
  "model": "anthropic/claude-haiku-4",  // ← Always specify!
  "timeoutSeconds": 300
}
```

### For systemEvent payload (main session):
```json
{
  "kind": "systemEvent",
  "text": "Reminder or alert text"
}
```
(systemEvent inherits the main session's model, which should be Standard tier by default)

## Cost Comparison

**Example: Daily log parsing cronjob**

| Model | Tier | Cost per run | Monthly cost (30 days) |
|-------|------|--------------|------------------------|
| Haiku 4 | Quick | $0.001 | $0.03 |
| Sonnet 4.5 | Standard | $0.012 | $0.36 |
| MiniMax m2.5 | Deep | $0.060 | $1.80 |

**10 cronjobs running daily:**
- Quick: $0.30/month
- Standard: $3.60/month
- Deep: $18/month

**Choose Quick = 60x cheaper than Deep!**

## Real-World Examples

### Good (Quick)
```bash
# Heartbeat-style health check
cron add --schedule "*/30 * * * *" \
  --payload '{"kind":"agentTurn","message":"Check if all services are running","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated

# Parse structured data
cron add --schedule "0 1 * * *" \
  --payload '{"kind":"agentTurn","message":"Extract customer data from support_tickets.json","model":"openrouter/stepfun/step-3.5-flash:free"}' \
  --sessionTarget isolated

# Simple reminder
cron add --schedule "0 14 * * *" \
  --payload '{"kind":"systemEvent","text":"Reminder: Review pending PRs"}' \
  --sessionTarget main
```

### Bad (Wasteful)
```bash
# ❌ Using Deep for simple check
cron add --schedule "*/15 * * * *" \
  --payload '{"kind":"agentTurn","message":"Check email","model":"anthropic/claude-opus-4"}' \
  --sessionTarget isolated
# → Should be Quick! 60x more expensive for no benefit

# ❌ Using Standard for parsing
cron add --schedule "0 2 * * *" \
  --payload '{"kind":"agentTurn","message":"Parse CSV","model":"anthropic/claude-sonnet-4-5"}' \
  --sessionTarget isolated
# → Should be Quick! Parsing is routine
```

## Default Template

When creating a new cronjob, start with this template:

```bash
cron add \
  --schedule "CRON_EXPRESSION" \
  --payload '{
    "kind":"agentTurn",
    "message":"TASK_DESCRIPTION",
    "model":"openrouter/stepfun/step-3.5-flash:free",
    "timeoutSeconds":300
  }' \
  --sessionTarget isolated \
  --name "DESCRIPTIVE_NAME"
```

Then ask yourself:
1. Does this task require complex reasoning? → If NO, keep Quick
2. Does this task generate user-facing content? → Maybe Standard
3. Does this task need deep analysis? → Maybe Standard
4. Everything else → Quick

## Monitoring Cronjob Costs

Track cronjob token usage:
```bash
# List all cronjobs
cron list

# Check runs for a specific job
cron runs --jobId <job-id>

# Use token_tracker.py to monitor spending
python3 scripts/token_tracker.py check
```

If daily costs are high, audit your cronjobs:
1. List all jobs: `cron list`
2. Check which model each uses
3. Switch expensive models to Quick where possible

## Summary

✅ **Default to Quick tier** for 90% of cronjobs  
✅ **Specify model explicitly** in payload (don't rely on defaults)  
✅ **Use isolated sessions** for background tasks  
✅ **Monitor costs** regularly  

❌ **Never use Deep tier** for scheduled tasks  
❌ **Don't use Standard tier** unless content quality matters  
❌ **Don't forget to specify model** (defaults can be expensive)  

**Savings:** Using Quick instead of Deep for 10 daily cronjobs = **$17.70/month saved**
