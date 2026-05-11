#!/bin/bash
# cron-setup.sh — Generate cron job definitions for cost-optimized scheduled tasks
# Usage: bash cron-setup.sh
# Outputs JSON cron job configs for common automated tasks using cheap models

set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║  Cost-Optimized Cron Job Templates       ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

OUTDIR="/tmp/cost-optimizer-crons"
mkdir -p "$OUTDIR"

# 1. Daily cost report
cat > "$OUTDIR/daily-cost-report.json" << 'CRON'
{
  "name": "daily-cost-report",
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "UTC" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run the cost audit script at skills/cost-optimizer/scripts/cost-audit.sh and summarize the results. If spending is above target, list top 3 specific actions to reduce it.",
    "model": "deepseek/deepseek-v3.2",
    "timeoutSeconds": 120
  },
  "delivery": { "mode": "announce" },
  "sessionTarget": "isolated",
  "enabled": true
}
CRON
echo -e "${GREEN}✅${NC} daily-cost-report.json — Daily audit at 9am UTC (DeepSeek, ~\$0.04)"

# 2. Weekly optimization review
cat > "$OUTDIR/weekly-optimization-review.json" << 'CRON'
{
  "name": "weekly-optimization-review",
  "schedule": { "kind": "cron", "expr": "0 10 * * 1", "tz": "UTC" },
  "payload": {
    "kind": "agentTurn",
    "message": "Review this week's OpenClaw usage patterns. Check memory files for spending notes. Run token-counter.sh and cost-audit.sh. Compare current config against the cost-optimizer skill recommendations. Provide a brief weekly cost report with trend (up/down/stable) and one actionable suggestion.",
    "model": "deepseek/deepseek-v3.2",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce" },
  "sessionTarget": "isolated",
  "enabled": true
}
CRON
echo -e "${GREEN}✅${NC} weekly-optimization-review.json — Monday 10am UTC (DeepSeek, ~\$0.04)"

# 3. Free model health check
cat > "$OUTDIR/free-model-healthcheck.json" << 'CRON'
{
  "name": "free-model-healthcheck",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *", "tz": "UTC" },
  "payload": {
    "kind": "agentTurn",
    "message": "Quick check: are free models currently responding? Try generating a one-line response. If rate limited, note which models are down. Only report if there's an issue — if everything works, just confirm briefly.",
    "model": "openrouter/deepseek/deepseek-chat-v3-0324:free",
    "timeoutSeconds": 30
  },
  "delivery": { "mode": "announce" },
  "sessionTarget": "isolated",
  "enabled": false
}
CRON
echo -e "${GREEN}✅${NC} free-model-healthcheck.json — Every 6h (free model, \$0.00) [disabled by default]"

# 4. Memory cleanup
cat > "$OUTDIR/memory-cleanup.json" << 'CRON'
{
  "name": "memory-cleanup",
  "schedule": { "kind": "cron", "expr": "0 3 * * 0", "tz": "UTC" },
  "payload": {
    "kind": "agentTurn",
    "message": "Review memory/*.md files older than 14 days. Summarize any important info into MEMORY.md if not already there. List files that could be archived. Do NOT delete anything — just report what could be cleaned up.",
    "model": "deepseek/deepseek-v3.2",
    "timeoutSeconds": 120
  },
  "delivery": { "mode": "announce" },
  "sessionTarget": "isolated",
  "enabled": true
}
CRON
echo -e "${GREEN}✅${NC} memory-cleanup.json — Sunday 3am UTC (DeepSeek, ~\$0.04)"

echo ""
echo -e "${BOLD}Generated files in:${NC} $OUTDIR/"
echo ""
echo "To install a cron job, tell your agent:"
echo "  'Install the daily-cost-report cron job from the cost-optimizer templates'"
echo ""
echo "Or use the cron tool directly with the JSON contents."
echo ""
echo -e "${CYAN}Monthly cost of all enabled crons: ~\$5.40${NC}"
echo "  (vs ~\$170+ if these ran on Opus)"
