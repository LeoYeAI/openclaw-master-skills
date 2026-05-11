#!/bin/bash
# cost-monitor.sh — Monitor real-time OpenClaw spending from logs
# Usage: bash cost-monitor.sh [log-path] [--live]
# Parses openclaw logs to track model usage, token counts, and estimated costs

set -euo pipefail

LOG="${1:-/data/.openclaw/logs/openclaw.log}"
LIVE="${2:-}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

if [ ! -f "$LOG" ]; then
  # Try alternate locations
  for p in "$HOME/.openclaw/logs/openclaw.log" "/var/log/openclaw.log"; do
    if [ -f "$p" ]; then LOG="$p"; break; fi
  done
fi

if [ ! -f "$LOG" ]; then
  echo -e "${RED}Log file not found. Tried: $LOG${NC}"
  echo "Usage: bash cost-monitor.sh /path/to/openclaw.log [--live]"
  exit 1
fi

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     OpenClaw Cost Monitor                ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Log: $LOG"
echo ""

# Parse today's log entries for model usage
TODAY=$(date +%Y-%m-%d)

echo -e "${BOLD}── Today's Usage ($TODAY) ──${NC}"
echo ""

# Count requests by looking for model-related log entries
node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const today = '$TODAY';

const modelCosts = {
  'claude-opus-4-6': 0.71,
  'claude-sonnet-4-6': 0.53,
  'claude-haiku-4-5': 0.15,
  'gpt-5.2': 0.44,
  'deepseek-v3.2': 0.04,
  'minimax-m2.5': 0.04,
  'gemini-flash': 0.04,
  'grok-4': 0.50,
};

const usage = {};
let totalRequests = 0;
let totalTokensIn = 0;
let totalTokensOut = 0;
let heartbeats = 0;

for (const line of lines) {
  if (!line.includes(today)) continue;
  
  // Look for model usage patterns
  for (const [model, cost] of Object.entries(modelCosts)) {
    if (line.toLowerCase().includes(model.toLowerCase())) {
      if (!usage[model]) usage[model] = { count: 0, cost: cost };
      usage[model].count++;
      totalRequests++;
    }
  }
  
  // Count heartbeats
  if (line.includes('heartbeat') || line.includes('HEARTBEAT')) {
    heartbeats++;
  }
  
  // Try to extract token counts
  const tokMatch = line.match(/tokens?[:\s]+(\d+)/i);
  if (tokMatch) {
    totalTokensIn += parseInt(tokMatch[1]);
  }
}

if (totalRequests === 0) {
  console.log('No model usage found in today\\'s logs.');
  console.log('(Logs may use a different format — check manually)');
} else {
  console.log('Model Usage:');
  let totalCost = 0;
  for (const [model, data] of Object.entries(usage).sort((a,b) => b[1].count - a[1].count)) {
    const est = data.count * data.cost;
    totalCost += est;
    console.log('  ' + model + ': ' + data.count + ' requests (~\$' + est.toFixed(2) + ')');
  }
  console.log('');
  console.log('Total requests: ' + totalRequests);
  console.log('Heartbeats detected: ' + heartbeats);
  console.log('Estimated cost today: ~\$' + totalCost.toFixed(2));
  
  // Project monthly
  const hoursSoFar = new Date().getHours() + (new Date().getMinutes() / 60);
  if (hoursSoFar > 1) {
    const projectedDaily = totalCost * (24 / hoursSoFar);
    console.log('Projected daily: ~\$' + projectedDaily.toFixed(2));
    console.log('Projected monthly: ~\$' + (projectedDaily * 30).toFixed(0));
  }
}
" 2>/dev/null

echo ""

if [ "$LIVE" = "--live" ]; then
  echo -e "${YELLOW}Live monitoring (Ctrl+C to stop)...${NC}"
  echo ""
  tail -f "$LOG" | grep --line-buffered -iE "model|token|cost|heartbeat" | while read -r line; do
    echo -e "${CYAN}$(date +%H:%M:%S)${NC} $line"
  done
fi
