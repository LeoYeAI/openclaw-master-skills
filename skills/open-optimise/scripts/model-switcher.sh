#!/bin/bash
# model-switcher.sh — Show all models with status, cost, and strengths
# Usage: bash model-switcher.sh [config-path]
# Quick reference for picking the right model right now

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Model Quick-Switcher                 ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# Load health check results if available
HEALTH_FILE=$(ls -t /tmp/provider-health-*.json 2>/dev/null | head -1)

node -e "
const fs = require('fs');

// Load config
const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();
const defaults = config.agents?.defaults || {};
const model = defaults.model;
const primary = typeof model === 'string' ? model : model?.primary || 'unknown';
const aliases = defaults.models || {};

// Load health data if available
let health = {};
try {
  const healthFile = '$HEALTH_FILE';
  if (healthFile) {
    const data = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
    for (const entry of data) {
      health[entry.provider + '/' + entry.model] = entry;
    }
  }
} catch(e) {}

// Model database
const models = [
  // Free tier
  { id: 'openrouter/deepseek/deepseek-chat-v3-0324:free', alias: 'deepseek-free', cost: 0.00, tier: 'Free', strength: 'Best free. Coding, reasoning, general.' },
  { id: 'openrouter/meta-llama/llama-4-scout-17b-16e-instruct:free', alias: 'llama-free', cost: 0.00, tier: 'Free', strength: '512K context. Research, long docs.' },
  { id: 'openrouter/qwen/qwen3-235b-a22b:free', alias: 'qwen-free', cost: 0.00, tier: 'Free', strength: 'Multilingual, translation.' },
  { id: 'openrouter/mistral/mistral-small-3.1-24b-instruct:free', alias: 'mistral-free', cost: 0.00, tier: 'Free', strength: 'Quick short answers.' },
  { id: 'openrouter/google/gemma-3-27b-it:free', alias: 'gemma-free', cost: 0.00, tier: 'Free', strength: 'Reliable fallback.' },
  // Budget
  { id: 'deepseek/deepseek-v3.2', alias: 'deepseek', cost: 0.04, tier: 'Budget', strength: 'Coding daily driver. Great value.' },
  { id: 'google-ai-studio/gemini-flash-latest', alias: 'flash', cost: 0.04, tier: 'Budget', strength: 'Fast general tasks.' },
  { id: 'openrouter/minimax/minimax-m2.5', alias: 'minimax', cost: 0.04, tier: 'Budget', strength: 'General daily driver.' },
  { id: 'openrouter/moonshotai/kimi-k2.5', alias: 'kimi', cost: 0.07, tier: 'Budget', strength: 'Auto-caching. Long sessions.' },
  { id: 'openai/o4-mini', alias: 'o4', cost: 0.10, tier: 'Budget', strength: 'Reasoning on a budget.' },
  // Quality
  { id: 'anthropic/claude-haiku-4-5', alias: 'haiku', cost: 0.15, tier: 'Quality', strength: 'Mid-tier quality work.' },
  { id: 'google-ai-studio/gemini-3.1-pro-preview', alias: 'gemini', cost: 0.20, tier: 'Quality', strength: 'Large context, multimodal.' },
  { id: 'grok/grok-4-1-fast', alias: 'grok-fast', cost: 0.30, tier: 'Quality', strength: 'Fast quality responses.' },
  { id: 'anthropic/claude-sonnet-4-6', alias: 'sonnet', cost: 0.53, tier: 'Quality', strength: 'Writing, code review, polish.' },
  // Premium
  { id: 'openai/gpt-5.2', alias: 'gpt', cost: 0.44, tier: 'Premium', strength: 'Complex multi-domain.' },
  { id: 'grok/grok-4', alias: 'grok', cost: 0.50, tier: 'Premium', strength: 'Strong reasoning.' },
  { id: 'anthropic/claude-opus-4-6', alias: 'opus', cost: 0.71, tier: 'Premium', strength: 'Maximum reasoning power.' },
];

// Check which are configured
const configuredProviders = Object.keys(config.models?.providers || {});
const configuredAliases = new Set(Object.values(aliases).map(a => a.alias));

const tierColors = { 'Free': '🟢', 'Budget': '🔵', 'Quality': '🟡', 'Premium': '🔴' };

let currentTier = '';
for (const m of models) {
  if (m.tier !== currentTier) {
    currentTier = m.tier;
    console.log('  ' + tierColors[m.tier] + ' ' + m.tier.toUpperCase());
  }
  
  const isActive = primary === m.id;
  const isConfigured = configuredAliases.has(m.alias);
  const providerName = m.id.split('/')[0];
  const hasProvider = configuredProviders.includes(providerName) || providerName === 'openrouter';
  
  // Status
  let status;
  const healthEntry = health[m.id];
  if (isActive) status = '▶ ACTIVE';
  else if (healthEntry?.status === 'UP' || healthEntry?.status === 'AUTH OK') status = '  UP    ';
  else if (healthEntry?.status === 'DOWN') status = '  DOWN  ';
  else if (healthEntry?.status === 'SLOW') status = '  SLOW  ';
  else if (!hasProvider) status = '  N/A   ';
  else status = '  ?     ';
  
  const latency = healthEntry?.latency ? healthEntry.latency + 'ms' : '-';
  
  console.log('  ' + status + ' ' + m.alias.padEnd(14) + '\$' + m.cost.toFixed(2).padStart(5) + '  ' + m.strength);
}

console.log('');
console.log('  Switch: /model <alias>    Reset: /model auto');
console.log('  Current: ' + primary);
" 2>/dev/null
