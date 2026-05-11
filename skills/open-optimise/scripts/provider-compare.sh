#!/bin/bash
# provider-compare.sh — Detect same model across multiple providers, find cheapest route
# Usage: bash provider-compare.sh [config-path]
# Catches the "paying for free stuff" mistake

set -euo pipefail

CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Provider Cost Comparison             ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

node -e "
const fs = require('fs');
const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();
const providers = config.models?.providers || {};
const defaults = config.agents?.defaults || {};
const primary = typeof defaults.model === 'string' ? defaults.model : defaults.model?.primary;

// Known market rates (input $/M tokens)
const marketRates = {
  'claude-opus-4-6': 15.00,
  'claude-sonnet-4-6': 3.00,
  'claude-haiku-4-5': 0.80,
  'gpt-5.2': 2.50,
  'gpt-5.2-pro': 5.00,
  'gpt-5.2-codex': 2.50,
  'o4-mini': 1.10,
  'deepseek-v3.2': 0.27,
  'gemini-3.1-pro-preview': 1.25,
  'gemini-flash-latest': 0.10,
  'grok-4': 3.00,
  'grok-4-1-fast': 2.00,
  'grok-3-mini': 0.30,
};

// Build model→providers map
const modelProviders = {};
for (const [provName, prov] of Object.entries(providers)) {
  for (const m of (prov.models || [])) {
    const modelId = m.id;
    if (!modelProviders[modelId]) modelProviders[modelId] = [];
    
    const configCost = m.cost?.input || 0;
    const marketCost = marketRates[modelId] || null;
    
    modelProviders[modelId].push({
      provider: provName,
      fullId: provName + '/' + modelId,
      configCost,
      marketCost,
      isZero: configCost === 0,
      baseUrl: prov.baseUrl || '',
    });
  }
}

// Check for duplicates
let duplicates = 0;
let warnings = 0;

console.log('  ── Model Availability by Provider ──');
console.log('');
console.log('  ' + 'MODEL'.padEnd(25) + 'PROVIDER'.padEnd(18) + 'CONFIG \$/M'.padEnd(14) + 'MARKET \$/M'.padEnd(14) + 'STATUS');
console.log('  ' + '─'.repeat(25) + '─'.repeat(18) + '─'.repeat(14) + '─'.repeat(14) + '─'.repeat(15));

for (const [modelId, entries] of Object.entries(modelProviders).sort()) {
  for (const e of entries) {
    const isPrimary = primary === e.fullId;
    const status = [];
    if (isPrimary) status.push('▶ PRIMARY');
    if (e.isZero) status.push('FREE via proxy');
    if (e.marketCost && !e.isZero && e.configCost > 0) status.push('paid');
    
    console.log('  ' + modelId.padEnd(25) + e.provider.padEnd(18) + (e.isZero ? '\$0' : '\$' + e.configCost.toFixed(2)).padEnd(14) + (e.marketCost ? '\$' + e.marketCost.toFixed(2) : '?').padEnd(14) + status.join(', '));
  }
  
  if (entries.length > 1) {
    duplicates++;
    // Check if one is cheaper
    const costs = entries.map(e => ({ ...e, effectiveCost: e.isZero ? 0 : (e.configCost || e.marketCost || 0) }));
    costs.sort((a, b) => a.effectiveCost - b.effectiveCost);
    
    if (costs[0].effectiveCost < costs[costs.length - 1].effectiveCost) {
      const cheap = costs[0];
      const expensive = costs[costs.length - 1];
      console.log('  ⚠️  ' + modelId + ' is cheaper via ' + cheap.provider + ' (\$' + cheap.effectiveCost + ') vs ' + expensive.provider + ' (\$' + expensive.effectiveCost + ')');
      
      // Check if primary uses the expensive one
      if (primary === expensive.fullId) {
        console.log('  🔴 PRIMARY is using the MORE EXPENSIVE provider!');
        console.log('     Switch to: ' + cheap.fullId);
        warnings++;
      }
    }
  }
}

console.log('');
console.log('  ── Summary ──');
console.log('');
console.log('  Total models: ' + Object.keys(modelProviders).length);
console.log('  Across providers: ' + Object.keys(providers).length);
console.log('  Duplicate models: ' + duplicates + ' (same model, multiple providers)');

if (warnings > 0) {
  console.log('');
  console.log('  🔴 ' + warnings + ' routing warning(s) — you may be paying for something available cheaper');
} else if (duplicates > 0) {
  console.log('  ✅ No routing issues — cheapest provider is being used');
} else {
  console.log('  ✅ No duplicate models found — each model has one provider');
}

// Check for proxy indicator
const proxyProviders = Object.entries(providers).filter(([_, p]) => p.baseUrl && !p.baseUrl.includes('openrouter') && !p.baseUrl.includes('anthropic.com') && !p.baseUrl.includes('openai.com'));
if (proxyProviders.length > 0) {
  console.log('');
  console.log('  ℹ️  Detected proxy provider(s): ' + proxyProviders.map(([n]) => n).join(', '));
  console.log('     If costs show \$0, the proxy handles billing separately.');
  console.log('     Check your proxy dashboard for actual costs.');
}
" 2>/dev/null
