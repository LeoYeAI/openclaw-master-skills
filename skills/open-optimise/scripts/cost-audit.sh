#!/bin/bash
# cost-audit.sh — Analyze OpenClaw config and estimate monthly costs
# Usage: bash cost-audit.sh [config-path]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
PARSE="node $SCRIPT_DIR/parse-config.js $CONFIG"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     OpenClaw Cost Audit Report           ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# Extract config values
PRIMARY=$($PARSE agents.defaults.model.primary "not set")
if [ "$PRIMARY" = "not set" ]; then
  PRIMARY=$($PARSE agents.defaults.model "not set")
fi
HB_MODEL=$($PARSE agents.defaults.heartbeat.model "same as primary")
HB_INTERVAL=$($PARSE agents.defaults.heartbeat.every "not set")
MAX_CONC=$($PARSE agents.defaults.maxConcurrent "default")
SUB_CONC=$($PARSE agents.defaults.subagents.maxConcurrent "default")
MF_ENABLED=$($PARSE agents.defaults.compaction.memoryFlush.enabled "false")
FALLBACKS=$($PARSE agents.defaults.model.fallbacks "[]")

# Get providers
PROVIDERS=$(node -e "
  const raw = require('fs').readFileSync('$CONFIG','utf8');
  const c = new Function('return ('+raw+')')();
  console.log(Object.keys(c.models?.providers || {}).join(', '));
")

HAS_OPENROUTER=$(node -e "
  const raw = require('fs').readFileSync('$CONFIG','utf8');
  const c = new Function('return ('+raw+')')();
  console.log(c.models?.providers?.openrouter ? 'yes' : 'no');
")

# Get alias count
ALIAS_COUNT=$(node -e "
  const raw = require('fs').readFileSync('$CONFIG','utf8');
  const c = new Function('return ('+raw+')')();
  console.log(Object.keys(c.agents?.defaults?.models || {}).length);
")

echo -e "${CYAN}Primary Model:${NC}     $PRIMARY"
echo -e "${CYAN}Fallbacks:${NC}         $FALLBACKS"
echo -e "${CYAN}Heartbeat Model:${NC}   $HB_MODEL"
echo -e "${CYAN}Heartbeat Every:${NC}   $HB_INTERVAL"
echo -e "${CYAN}Providers:${NC}         $PROVIDERS"
echo -e "${CYAN}OpenRouter:${NC}        $HAS_OPENROUTER"
echo -e "${CYAN}Model Aliases:${NC}     $ALIAS_COUNT configured"
echo -e "${CYAN}Concurrency:${NC}       main=$MAX_CONC, subagents=$SUB_CONC"
echo -e "${CYAN}Memory Flush:${NC}      $MF_ENABLED"

echo ""
echo -e "${BOLD}── Cost Estimates (50 requests/day) ──${NC}"
echo ""

node -e "
const costs = {
  'anthropic/claude-opus-4-6': { name: 'Opus', perReq: 0.71 },
  'anthropic/claude-sonnet-4-6': { name: 'Sonnet', perReq: 0.53 },
  'anthropic/claude-haiku-4-5': { name: 'Haiku', perReq: 0.15 },
  'openai/gpt-5.2': { name: 'GPT-5.2', perReq: 0.44 },
  'deepseek/deepseek-v3.2': { name: 'DeepSeek', perReq: 0.04 },
  'openrouter/minimax/minimax-m2.5': { name: 'MiniMax', perReq: 0.04 },
  'openrouter/deepseek/deepseek-v3.2': { name: 'DeepSeek (OR)', perReq: 0.04 },
  'openrouter/deepseek/deepseek-chat-v3-0324:free': { name: 'DeepSeek Free', perReq: 0.00 },
  'google-ai-studio/gemini-flash-latest': { name: 'Flash', perReq: 0.04 },
  'grok/grok-4': { name: 'Grok 4', perReq: 0.50 },
};

const primary = '$PRIMARY';
const hbModel = '$HB_MODEL';
const hbInterval = '$HB_INTERVAL';

const pCost = costs[primary] || { name: primary.split('/').pop(), perReq: 0.50 };
const monthlyPrimary = pCost.perReq * 50 * 30;
console.log('  Primary (' + pCost.name + '): \$' + pCost.perReq.toFixed(2) + '/req → \$' + monthlyPrimary.toFixed(0) + '/month');

let hbMonthly = 0;
if (hbInterval !== 'not set') {
  const mins = parseInt(hbInterval) || 30;
  const hbPerDay = (24 * 60) / mins;
  const hbCostInfo = hbModel === 'same as primary' ? pCost : (costs[hbModel] || { name: hbModel.split('/').pop(), perReq: 0.04 });
  hbMonthly = hbCostInfo.perReq * hbPerDay * 30;
  console.log('  Heartbeats (' + hbCostInfo.name + ' every ' + mins + 'm): \$' + hbMonthly.toFixed(1) + '/month (' + Math.round(hbPerDay) + '/day)');
} else {
  console.log('  Heartbeats: not configured');
}

const total = monthlyPrimary + hbMonthly;
console.log('');
console.log('  TOTAL ESTIMATED: \$' + total.toFixed(0) + '/month');

// Compare to alternatives
console.log('');
console.log('  ── Comparison ──');
const opusCost = 0.71 * 50 * 30 + (hbInterval !== 'not set' ? 0.71 * ((24*60)/(parseInt(hbInterval)||30)) * 30 : 0);
console.log('  All Opus (unoptimized): \$' + opusCost.toFixed(0) + '/month');
console.log('  Current config:         \$' + total.toFixed(0) + '/month');
console.log('  Savings:                \$' + (opusCost - total).toFixed(0) + '/month (' + (((opusCost-total)/opusCost)*100).toFixed(0) + '%)');

if (primary.includes('opus')) {
  console.log('');
  console.log('  ⚠️  Still on Opus as primary. Switching to DeepSeek saves ~\$' + Math.round(monthlyPrimary - 60) + '/month');
}

if ('$HAS_OPENROUTER' === 'no') {
  console.log('');
  console.log('  💡 No OpenRouter = no free models. Add it for \$0.00/request on simple tasks.');
}
"

echo ""
echo -e "${BOLD}── Recommendations ──${NC}"
echo ""

node -e "
const recs = [];
if ('$PRIMARY'.includes('opus')) recs.push('🔴 HIGH: Switch default from Opus to DeepSeek/MiniMax (~\$1000/mo saved)');
else if ('$PRIMARY'.includes('sonnet')) recs.push('🟡 MED: Consider DeepSeek/MiniMax as daily driver (~\$600/mo saved)');
if ('$HB_MODEL' === 'same as primary' && '$PRIMARY'.includes('opus')) recs.push('🔴 HIGH: Route heartbeats to cheap model (~\$500/mo saved)');
if ('$HB_MODEL' === 'same as primary' && '$PRIMARY'.includes('sonnet')) recs.push('🟡 MED: Route heartbeats to cheap model (~\$350/mo saved)');
if ('$HB_INTERVAL' === 'not set') recs.push('🟡 MED: Configure heartbeats to keep prompt cache warm');
if ('$HAS_OPENROUTER' === 'no') recs.push('🟡 MED: Add OpenRouter provider for free model access');
if ('$MF_ENABLED' === 'false') recs.push('🟢 LOW: Enable memory flush before compaction');
if (parseInt('$MAX_CONC') > 3 || '$MAX_CONC' === 'default') recs.push('🟢 LOW: Reduce maxConcurrent to limit parallel spending');
if (recs.length === 0) recs.push('✅ Config looks well-optimized!');
recs.forEach(r => console.log('  ' + r));
"

echo ""
echo -e "${BOLD}Done.${NC}"
