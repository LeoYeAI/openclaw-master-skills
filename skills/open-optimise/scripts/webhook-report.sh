#!/bin/bash
# webhook-report.sh — Send cost report to webhook (Discord, Slack, or generic)
# Usage: bash webhook-report.sh <webhook-url> [format] [config-path]
# Formats: discord, slack, generic (default: auto-detect from URL)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WEBHOOK="${1:-}"
FORMAT="${2:-auto}"
CONFIG="${3:-$HOME/.openclaw/openclaw.json}"
LOG="/data/.openclaw/logs/openclaw.log"

if [ -z "$WEBHOOK" ]; then
  echo "Usage: bash webhook-report.sh <webhook-url> [discord|slack|generic]"
  echo ""
  echo "Sends a cost summary to a webhook. Use with cron for daily/weekly reports."
  echo ""
  echo "Cron template (daily at 9am UTC):"
  echo '  {"schedule":{"kind":"cron","expr":"0 9 * * *"},'
  echo '   "payload":{"kind":"agentTurn","message":"Run webhook-report.sh with the configured webhook"}}'
  exit 0
fi

# Auto-detect format
if [ "$FORMAT" = "auto" ]; then
  if echo "$WEBHOOK" | grep -q "discord"; then FORMAT="discord"
  elif echo "$WEBHOOK" | grep -q "slack"; then FORMAT="slack"
  else FORMAT="generic"
  fi
fi

# Get cost data
COST_DATA=$(node -e "
const fs = require('fs');

// Parse config
let primary = 'unknown', hbModel = 'unknown', hbEvery = '?';
try {
  const raw = fs.readFileSync('$CONFIG', 'utf8');
  const config = new Function('return (' + raw + ')')();
  const d = config.agents?.defaults || {};
  const m = d.model;
  primary = typeof m === 'string' ? m : m?.primary || 'unknown';
  hbModel = d.heartbeat?.model || primary;
  hbEvery = d.heartbeat?.every || 'not set';
} catch(e) {}

// Parse logs for today
const today = new Date().toISOString().substring(0, 10);
let todayRequests = 0;
let todayHeartbeats = 0;
try {
  const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
  for (const line of lines) {
    if (!line.includes(today)) continue;
    if (/heartbeat|HEARTBEAT/i.test(line)) todayHeartbeats++;
    else if (/model|request|response/i.test(line)) todayRequests++;
  }
} catch(e) {}

const costs = {
  'claude-opus-4-6': 0.71, 'claude-sonnet-4-6': 0.53, 'claude-haiku-4-5': 0.15,
  'deepseek-v3.2': 0.04, 'minimax-m2.5': 0.04,
};
const pName = primary.split('/').pop();
const pCost = costs[pName] || 0.50;
const todayCost = todayRequests * pCost;
const monthProjection = todayCost * 30;

console.log(JSON.stringify({
  primary: primary.split('/').pop(),
  primaryCost: pCost,
  heartbeatModel: hbModel.split('/').pop(),
  heartbeatEvery: hbEvery,
  todayRequests,
  todayHeartbeats,
  todayEstCost: todayCost.toFixed(2),
  monthProjection: monthProjection.toFixed(0),
  date: today,
}));
" 2>/dev/null)

# Build payload based on format
case "$FORMAT" in
  discord)
    PAYLOAD=$(node -e "
const d = $COST_DATA;
const embed = {
  embeds: [{
    title: '⚡ Daily Cost Report — ' + d.date,
    color: d.monthProjection > 100 ? 0xff0000 : d.monthProjection > 30 ? 0xffaa00 : 0x00ff00,
    fields: [
      { name: 'Model', value: d.primary + ' (\$' + d.primaryCost + '/req)', inline: true },
      { name: 'Today Requests', value: String(d.todayRequests), inline: true },
      { name: 'Today Heartbeats', value: String(d.todayHeartbeats), inline: true },
      { name: 'Est. Cost Today', value: '\$' + d.todayEstCost, inline: true },
      { name: 'Monthly Projection', value: '\$' + d.monthProjection, inline: true },
      { name: 'Heartbeat', value: d.heartbeatModel + ' / ' + d.heartbeatEvery, inline: true },
    ],
    footer: { text: 'Cost Optimizer v5' },
    timestamp: new Date().toISOString(),
  }]
};
console.log(JSON.stringify(embed));
")
    ;;
  slack)
    PAYLOAD=$(node -e "
const d = $COST_DATA;
const msg = {
  blocks: [
    { type: 'header', text: { type: 'plain_text', text: '⚡ Daily Cost Report — ' + d.date }},
    { type: 'section', fields: [
      { type: 'mrkdwn', text: '*Model:* ' + d.primary + ' (\$' + d.primaryCost + '/req)' },
      { type: 'mrkdwn', text: '*Requests:* ' + d.todayRequests + ' + ' + d.todayHeartbeats + ' heartbeats' },
      { type: 'mrkdwn', text: '*Est. Today:* \$' + d.todayEstCost },
      { type: 'mrkdwn', text: '*Monthly Proj:* \$' + d.monthProjection },
    ]},
  ]
};
console.log(JSON.stringify(msg));
")
    ;;
  generic)
    PAYLOAD="$COST_DATA"
    ;;
esac

# Send
RESPONSE=$(curl -s -w "\n%{http_code}" -H "Content-Type: application/json" -d "$PAYLOAD" "$WEBHOOK" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  echo "✅ Report sent to $FORMAT webhook (HTTP $HTTP_CODE)"
else
  echo "❌ Failed to send (HTTP $HTTP_CODE): $BODY"
fi
