#!/bin/bash
# config-diff.sh — Show diff between current config and recommended optimized config
# Usage: bash config-diff.sh [config-path]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Config Diff — Current vs Optimized   ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

node -e "
const fs = require('fs');
const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();

const defaults = config.agents?.defaults || {};
const model = defaults.model;
const primary = typeof model === 'string' ? model : model?.primary;
const fallbacks = typeof model === 'object' ? (model.fallbacks || []) : [];
const heartbeat = defaults.heartbeat || {};
const memFlush = defaults.compaction?.memoryFlush || {};
const maxConc = defaults.maxConcurrent;
const subConc = defaults.subagents?.maxConcurrent;
const hasOpenRouter = !!config.models?.providers?.openrouter;

const changes = [];
let totalSavingsLow = 0;
let totalSavingsHigh = 0;

// 1. Primary model
const opusRate = 0.71;
const dsRate = 0.04;
if (primary && primary.includes('opus')) {
  const savings = (opusRate - dsRate) * 50 * 30;
  changes.push({
    id: 1,
    setting: 'Primary Model',
    current: primary || 'not set',
    recommended: 'deepseek/deepseek-v3.2',
    reason: 'DeepSeek handles 80%+ of tasks well at 94% less cost',
    savingsLow: savings * 0.5, // assume 50% of requests could use cheap
    savingsHigh: savings,
    risk: 'Lower quality on complex reasoning. Use /model opus when needed.',
  });
  totalSavingsLow += savings * 0.5;
  totalSavingsHigh += savings;
} else if (primary && primary.includes('sonnet')) {
  const savings = (0.53 - dsRate) * 50 * 30;
  changes.push({
    id: 1,
    setting: 'Primary Model',
    current: primary,
    recommended: 'deepseek/deepseek-v3.2',
    reason: 'DeepSeek is 92% cheaper than Sonnet for routine tasks',
    savingsLow: savings * 0.5,
    savingsHigh: savings,
    risk: 'Sonnet is better for writing/nuance. Switch back for polish.',
  });
  totalSavingsLow += savings * 0.5;
  totalSavingsHigh += savings;
}

// 2. Heartbeat model
const hbModel = heartbeat.model || primary || 'opus';
if (hbModel.includes('opus') || hbModel.includes('sonnet')) {
  const hbRate = hbModel.includes('opus') ? 0.71 : 0.53;
  const interval = parseInt(heartbeat.every) || 30;
  const hbPerMonth = ((24*60)/interval) * 30;
  const savings = (hbRate - dsRate) * hbPerMonth;
  changes.push({
    id: 2,
    setting: 'Heartbeat Model',
    current: hbModel + ' every ' + (heartbeat.every || '30m'),
    recommended: 'deepseek/deepseek-v3.2 every 55m',
    reason: 'Heartbeats are maintenance pings, not quality work',
    savingsLow: savings,
    savingsHigh: savings,
    risk: 'None. Heartbeats just check in.',
  });
  totalSavingsLow += savings;
  totalSavingsHigh += savings;
} else if (!heartbeat.every) {
  changes.push({
    id: 2,
    setting: 'Heartbeat Interval',
    current: 'not configured',
    recommended: '55m with cheap model',
    reason: 'Keeps prompt cache warm (90% discount on cached tokens)',
    savingsLow: 0,
    savingsHigh: 50,
    risk: 'Small cost for cache benefit. Net positive.',
  });
}

// 3. Memory flush
if (!memFlush.enabled) {
  changes.push({
    id: 3,
    setting: 'Memory Flush',
    current: 'disabled',
    recommended: 'enabled (threshold: 3000)',
    reason: 'Saves context to memory before compaction destroys it',
    savingsLow: 0,
    savingsHigh: 30,
    risk: 'None. Purely beneficial.',
  });
}

// 4. Concurrency
if (!maxConc || maxConc > 2) {
  const concSavings = ((maxConc || 4) - 2) * 0.71 * 10 * 30; // rough est
  changes.push({
    id: 4,
    setting: 'Max Concurrency',
    current: (maxConc || 'default (4)') + ' main / ' + (subConc || 'default (8)') + ' sub',
    recommended: '2 main / 2 sub',
    reason: 'Limits accidental parallel expensive requests',
    savingsLow: 0,
    savingsHigh: concSavings,
    risk: 'Slower parallel work. Fine for most users.',
  });
  totalSavingsHigh += concSavings;
}

// 5. OpenRouter
if (!hasOpenRouter) {
  changes.push({
    id: 5,
    setting: 'OpenRouter Provider',
    current: 'not configured',
    recommended: 'Add with API key for free models',
    reason: 'Unlocks \$0.00/request models for simple tasks',
    savingsLow: 30,
    savingsHigh: 200,
    risk: 'Free models have rate limits. Budget models as fallback.',
  });
  totalSavingsLow += 30;
  totalSavingsHigh += 200;
}

// Output
if (changes.length === 0) {
  console.log('  ✅ Your config already matches recommended optimizations!');
} else {
  for (const c of changes) {
    console.log('  ── Change ' + c.id + ': ' + c.setting + ' ──');
    console.log('  Current:     ' + c.current);
    console.log('  Recommended: ' + c.recommended);
    console.log('  Why:         ' + c.reason);
    console.log('  Savings:     \$' + c.savingsLow.toFixed(0) + '-' + c.savingsHigh.toFixed(0) + '/month');
    console.log('  Risk:        ' + c.risk);
    console.log('');
  }
  
  console.log('  ══════════════════════════════════════');
  console.log('  Total potential savings: \$' + totalSavingsLow.toFixed(0) + '-' + totalSavingsHigh.toFixed(0) + '/month');
  console.log('');
  console.log('  To apply all at once: bash apply-preset.sh budget');
  console.log('  To apply individually: tell your agent which changes to make');
}
" 2>/dev/null
