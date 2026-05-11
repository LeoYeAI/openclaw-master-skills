#!/bin/bash
# cost-history.sh — Calculate what past usage WOULD have cost on each model tier
# Usage: bash cost-history.sh [log-path] [days-back]
# The "holy shit" script: shows real savings with real data

set -euo pipefail

LOG="${1:-/data/.openclaw/logs/openclaw.log}"
DAYS="${2:-7}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

for p in "$LOG" "$HOME/.openclaw/logs/openclaw.log" "/var/log/openclaw.log"; do
  if [ -f "$p" ]; then LOG="$p"; break; fi
done

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Cost History — What-If Analysis      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Log: $LOG | Last $DAYS days"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${RED}Log not found. Generating estimate from config...${NC}"
  echo ""
  
  node -e "
const days = $DAYS;
const reqPerDay = 50; // estimated
const totalReqs = reqPerDay * days;
const hbPerDay = 26; // at 55min intervals
const totalHb = hbPerDay * days;

const tiers = [
  { name: 'Free models',  input: 0.00,  output: 0.00 },
  { name: 'DeepSeek V3.2', input: 0.27, output: 1.10 },
  { name: 'MiniMax M2.5',  input: 0.50, output: 1.10 },
  { name: 'Haiku 4.5',     input: 0.80, output: 4.00 },
  { name: 'Sonnet 4.6',    input: 3.00, output: 15.00 },
  { name: 'Opus 4.6',      input: 15.00, output: 75.00 },
];

const overheadTokens = 140000;
const avgOutputTokens = 500;

console.log('Estimated ' + totalReqs + ' requests + ' + totalHb + ' heartbeats over ' + days + ' days');
console.log('(Based on 50 req/day + 26 heartbeats/day estimate)');
console.log('');
console.log('If ALL requests had been on each tier:');
console.log('');
console.log('  Model               Requests    Heartbeats    Total       Monthly Proj');
console.log('  ─────               ────────    ──────────    ─────       ────────────');

for (const t of tiers) {
  const reqCost = ((overheadTokens/1e6) * t.input + (avgOutputTokens/1e6) * t.output) * totalReqs;
  const hbCost = ((overheadTokens/1e6) * t.input + (100/1e6) * t.output) * totalHb;
  const total = reqCost + hbCost;
  const monthly = total / days * 30;
  console.log('  ' + t.name.padEnd(20) + ' \$' + reqCost.toFixed(2).padStart(8) + '    \$' + hbCost.toFixed(2).padStart(8) + '    \$' + total.toFixed(2).padStart(8) + '    \$' + monthly.toFixed(0).padStart(6) + '/mo');
}

console.log('');
console.log('The gap between Opus and DeepSeek: \$' + (((overheadTokens/1e6)*15 + (avgOutputTokens/1e6)*75) * totalReqs / days * 30).toFixed(0) + '/mo vs \$' + (((overheadTokens/1e6)*0.27 + (avgOutputTokens/1e6)*1.10) * totalReqs / days * 30).toFixed(0) + '/mo');
console.log('That\\'s a ' + (((15-0.27)/15)*100).toFixed(0) + '% reduction for the same questions.');
"
  exit 0
fi

# Parse real logs
node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const daysBack = $DAYS;
const cutoff = new Date(Date.now() - daysBack * 86400000);

const modelPricing = {
  'claude-opus-4-6':    { input: 15.00, output: 75.00 },
  'claude-sonnet-4-6':  { input: 3.00,  output: 15.00 },
  'claude-haiku-4-5':   { input: 0.80,  output: 4.00 },
  'gpt-5.2':            { input: 2.50,  output: 10.00 },
  'deepseek-v3.2':      { input: 0.27,  output: 1.10 },
  'minimax-m2.5':       { input: 0.50,  output: 1.10 },
  'gemini-flash':       { input: 0.10,  output: 0.40 },
  'grok-4':             { input: 3.00,  output: 15.00 },
};

// Count requests by day and type
const days = {};
let totalRequests = 0;
let totalHeartbeats = 0;

for (const line of lines) {
  if (!line) continue;
  const dateMatch = line.match(/(\d{4}-\d{2}-\d{2})/);
  if (!dateMatch) continue;
  const day = dateMatch[1];
  if (new Date(day) < cutoff) continue;
  
  if (!days[day]) days[day] = { requests: 0, heartbeats: 0, models: {} };
  
  const isHb = /heartbeat|HEARTBEAT/i.test(line);
  
  // Detect model
  for (const m of Object.keys(modelPricing)) {
    if (line.toLowerCase().includes(m.toLowerCase())) {
      days[day].models[m] = (days[day].models[m] || 0) + 1;
      if (isHb) {
        days[day].heartbeats++;
        totalHeartbeats++;
      } else {
        days[day].requests++;
        totalRequests++;
      }
      break;
    }
  }
}

const overheadTokens = 140000;
const avgOutput = 500;
const tierCalc = [
  { name: 'Free',     input: 0,     output: 0 },
  { name: 'DeepSeek', input: 0.27,  output: 1.10 },
  { name: 'Haiku',    input: 0.80,  output: 4.00 },
  { name: 'Sonnet',   input: 3.00,  output: 15.00 },
  { name: 'Opus',     input: 15.00, output: 75.00 },
];

const total = totalRequests + totalHeartbeats;
console.log('Found ' + total + ' model interactions (' + totalRequests + ' requests + ' + totalHeartbeats + ' heartbeats)');
console.log('');

if (total === 0) {
  console.log('No model usage found in logs. Check log format or path.');
  process.exit(0);
}

console.log('── What Your Past ' + daysBack + ' Days Would Cost on Each Tier ──');
console.log('');
for (const t of tierCalc) {
  const cost = total * ((overheadTokens/1e6) * t.input + (avgOutput/1e6) * t.output);
  const monthly = cost / daysBack * 30;
  console.log('  ' + t.name.padEnd(10) + ' \$' + cost.toFixed(2).padStart(8) + ' (last ' + daysBack + 'd)  →  \$' + monthly.toFixed(0).padStart(6) + '/month');
}

console.log('');
console.log('── Daily Breakdown ──');
console.log('');
for (const [day, data] of Object.entries(days).sort()) {
  const models = Object.entries(data.models).map(([m,c]) => m.split('-')[0] + ':' + c).join(' ');
  console.log('  ' + day + ': ' + data.requests + ' req + ' + data.heartbeats + ' hb  [' + models + ']');
}
" 2>/dev/null || echo "Log parsing encountered an error"
