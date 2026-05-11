#!/bin/bash
# heartbeat-cost.sh — Isolate heartbeat costs from real usage in logs
# Usage: bash heartbeat-cost.sh [log-path] [days-back]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="${1:-/data/.openclaw/logs/openclaw.log}"
DAYS="${2:-7}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Try alternate log locations
for p in "$LOG" "$HOME/.openclaw/logs/openclaw.log" "/var/log/openclaw.log"; do
  if [ -f "$p" ]; then LOG="$p"; break; fi
done

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Heartbeat Cost Isolator              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Log: $LOG | Analyzing last $DAYS days"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${RED}Log file not found.${NC}"
  echo "Checking config for heartbeat settings instead..."
  echo ""

  CONFIG="$HOME/.openclaw/openclaw.json"
  if [ -f "$CONFIG" ] && [ -f "$SCRIPT_DIR/parse-config.js" ]; then
    HB_MODEL=$(node "$SCRIPT_DIR/parse-config.js" "$CONFIG" agents.defaults.heartbeat.model "not set")
    HB_EVERY=$(node "$SCRIPT_DIR/parse-config.js" "$CONFIG" agents.defaults.heartbeat.every "not set")
    PRIMARY=$(node "$SCRIPT_DIR/parse-config.js" "$CONFIG" agents.defaults.model.primary "unknown")
  else
    echo -e "${RED}Config not found either. Cannot analyze.${NC}"
    exit 1
  fi

  if [ "$HB_EVERY" = "not set" ]; then
    echo -e "${YELLOW}Heartbeats not configured.${NC}"
    echo "No heartbeat cost to report."
    exit 0
  fi

  echo -e "${BOLD}── Config-Based Estimate (no logs available) ──${NC}"
  echo ""

  node -e "
const costs = {
  'anthropic/claude-opus-4-6': { name: 'Opus 4.6', perReq: 0.71 },
  'anthropic/claude-sonnet-4-6': { name: 'Sonnet 4.6', perReq: 0.53 },
  'anthropic/claude-haiku-4-5': { name: 'Haiku 4.5', perReq: 0.15 },
  'deepseek/deepseek-v3.2': { name: 'DeepSeek V3.2', perReq: 0.04 },
  'openrouter/deepseek/deepseek-chat-v3-0324:free': { name: 'DeepSeek Free', perReq: 0.00 },
  'openrouter/minimax/minimax-m2.5': { name: 'MiniMax M2.5', perReq: 0.04 },
  'google-ai-studio/gemini-flash-latest': { name: 'Flash', perReq: 0.04 },
};

const hbModel = '$HB_MODEL';
const hbEvery = '$HB_EVERY';
const primary = '$PRIMARY';
const mins = parseInt(hbEvery) || 30;
const hbPerDay = (24 * 60) / mins;
const hbPerMonth = hbPerDay * 30;

const hbCost = costs[hbModel] || { name: hbModel.split('/').pop(), perReq: 0.04 };
const primaryCost = costs[primary] || { name: primary.split('/').pop(), perReq: 0.50 };

console.log('Heartbeat model:    ' + hbCost.name + ' (\$' + hbCost.perReq.toFixed(2) + '/req)');
console.log('Interval:           every ' + mins + ' minutes');
console.log('Heartbeats per day: ' + Math.round(hbPerDay));
console.log('Heartbeats per month: ' + Math.round(hbPerMonth));
console.log('');
console.log('── Monthly Heartbeat Cost ──');
console.log('');
console.log('  Current (' + hbCost.name + '):     \$' + (hbCost.perReq * hbPerMonth).toFixed(2) + '/month');
console.log('');
console.log('  ── What it WOULD cost on other models ──');
const tiers = [
  { model: 'Free model', perReq: 0.00 },
  { model: 'DeepSeek V3.2', perReq: 0.04 },
  { model: 'Haiku 4.5', perReq: 0.15 },
  { model: 'Sonnet 4.6', perReq: 0.53 },
  { model: 'Opus 4.6', perReq: 0.71 },
];
for (const t of tiers) {
  const monthlyCost = t.perReq * hbPerMonth;
  const marker = t.model.includes(hbCost.name) ? ' ← current' : '';
  console.log('  ' + t.model.padEnd(20) + ' \$' + monthlyCost.toFixed(2).padStart(8) + '/month' + marker);
}

console.log('');
const opusCost = 0.71 * hbPerMonth;
const currentCost = hbCost.perReq * hbPerMonth;
const saved = opusCost - currentCost;
if (saved > 0) {
  console.log('  💰 You\\'re saving \$' + saved.toFixed(0) + '/month by NOT using Opus for heartbeats');
} else if (hbModel.includes('opus')) {
  console.log('  🔴 ALERT: Heartbeats on Opus cost \$' + opusCost.toFixed(0) + '/month!');
  console.log('     Switch to a free/cheap model to save \$' + (opusCost - 0).toFixed(0) + '/month');
}

// Heartbeat as % of total bill
const totalEst = primaryCost.perReq * 50 * 30 + currentCost;
const hbPct = (currentCost / totalEst * 100);
console.log('');
console.log('  Heartbeats are ~' + hbPct.toFixed(1) + '% of estimated total monthly bill');
if (hbPct > 30) {
  console.log('  🔴 That\\'s too high. Heartbeats should be <5% of your bill.');
} else if (hbPct > 10) {
  console.log('  🟡 Consider a cheaper heartbeat model.');
} else {
  console.log('  ✅ Heartbeat cost is well-managed.');
}
"
  exit 0
fi

# Parse actual logs
node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const daysBack = $DAYS;
const cutoff = new Date(Date.now() - daysBack * 86400000);

const costs = {
  'claude-opus-4-6': 0.71,
  'claude-sonnet-4-6': 0.53,
  'claude-haiku-4-5': 0.15,
  'deepseek-v3.2': 0.04,
  'deepseek-v3': 0.04,
  'deepseek-chat-v3': 0.00,
  'minimax-m2.5': 0.04,
  'gemini-flash': 0.04,
  'gpt-5': 0.44,
  'grok-4': 0.50,
};

let heartbeats = { count: 0, models: {}, byDay: {} };
let realRequests = { count: 0, models: {} };

for (const line of lines) {
  if (!line) continue;

  // Try to extract date
  const dateMatch = line.match(/(\d{4}-\d{2}-\d{2})/);
  if (dateMatch) {
    const lineDate = new Date(dateMatch[1]);
    if (lineDate < cutoff) continue;
  }

  const isHeartbeat = /heartbeat|HEARTBEAT_OK|heartbeat.poll/i.test(line);

  // Try to identify model
  let model = 'unknown';
  let cost = 0;
  for (const [m, c] of Object.entries(costs)) {
    if (line.toLowerCase().includes(m.toLowerCase())) {
      model = m;
      cost = c;
      break;
    }
  }

  if (isHeartbeat) {
    heartbeats.count++;
    heartbeats.models[model] = (heartbeats.models[model] || 0) + 1;
    const day = dateMatch ? dateMatch[1] : 'unknown';
    heartbeats.byDay[day] = (heartbeats.byDay[day] || 0) + 1;
  } else if (model !== 'unknown') {
    realRequests.count++;
    realRequests.models[model] = (realRequests.models[model] || 0) + 1;
  }
}

console.log('── Last ' + daysBack + ' Days ──');
console.log('');
console.log('Heartbeat requests:  ' + heartbeats.count);
console.log('Real requests:       ' + realRequests.count);
console.log('Total:               ' + (heartbeats.count + realRequests.count));
if (heartbeats.count + realRequests.count > 0) {
  console.log('Heartbeat %:         ' + ((heartbeats.count / (heartbeats.count + realRequests.count)) * 100).toFixed(1) + '%');
}

console.log('');
console.log('Heartbeats by model:');
let totalHbCost = 0;
for (const [m, count] of Object.entries(heartbeats.models)) {
  const c = costs[m] || 0.04;
  const mCost = c * count;
  totalHbCost += mCost;
  console.log('  ' + m + ': ' + count + ' requests (\$' + mCost.toFixed(2) + ')');
}

console.log('');
console.log('Heartbeats by day:');
for (const [day, count] of Object.entries(heartbeats.byDay).sort()) {
  console.log('  ' + day + ': ' + count);
}

console.log('');
console.log('Total heartbeat cost (last ' + daysBack + ' days): \$' + totalHbCost.toFixed(2));
console.log('Projected monthly heartbeat cost: \$' + (totalHbCost / daysBack * 30).toFixed(2));

// What-if on Opus
const opusCost = 0.71 * heartbeats.count;
console.log('');
console.log('If these heartbeats had been on Opus: \$' + opusCost.toFixed(2));
console.log('You saved: \$' + (opusCost - totalHbCost).toFixed(2) + ' by using a cheaper model');
" 2>/dev/null || echo "Log parsing failed — check log format"
