#!/bin/bash
# context-monitor.sh — Track session context growth and predict compaction
# Usage: bash context-monitor.sh [log-path]
# Parses logs for context size entries and shows growth trends

set -euo pipefail

LOG="${1:-/data/.openclaw/logs/openclaw.log}"
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
echo -e "${BOLD}║     Context Growth Monitor               ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${YELLOW}Log file not found. Showing general context growth model.${NC}"
  echo ""
fi

node -e "
const fs = require('fs');
const logPath = '$LOG';
let logLines = [];
try { logLines = fs.readFileSync(logPath, 'utf8').split('\n'); } catch(e) {}

// Try to extract context size from logs
const contextData = [];
for (const line of logLines) {
  // Look for context size patterns like 'context: 85k/200k' or 'tokens: 85000'
  const ctxMatch = line.match(/context[:\s]+(\d+)k?\s*\/\s*(\d+)k/i)
    || line.match(/context[_\s]*tokens?[:\s]+(\d+)/i);
  if (ctxMatch) {
    const dateMatch = line.match(/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})/);
    contextData.push({
      timestamp: dateMatch ? dateMatch[1] : 'unknown',
      tokens: parseInt(ctxMatch[1]) * (ctxMatch[0].includes('k') ? 1000 : 1),
      limit: ctxMatch[2] ? parseInt(ctxMatch[2]) * 1000 : 200000,
    });
  }
  
  // Look for compaction events
  const compMatch = line.match(/compaction|compact/i);
  if (compMatch) {
    const dateMatch = line.match(/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})/);
    contextData.push({
      timestamp: dateMatch ? dateMatch[1] : 'unknown',
      event: 'compaction',
    });
  }
}

if (contextData.length > 0) {
  console.log('── Context Events from Logs ──');
  console.log('');
  for (const d of contextData.slice(-20)) {
    if (d.event === 'compaction') {
      console.log('  ' + d.timestamp + ' 🧹 COMPACTION triggered');
    } else {
      const pct = ((d.tokens / d.limit) * 100).toFixed(1);
      const bar = '█'.repeat(Math.round(pct / 5)) + '░'.repeat(20 - Math.round(pct / 5));
      const warn = pct > 80 ? ' ⚠️' : pct > 60 ? ' ⚡' : '';
      console.log('  ' + d.timestamp + ' [' + bar + '] ' + pct + '% (' + (d.tokens/1000).toFixed(0) + 'k/' + (d.limit/1000).toFixed(0) + 'k)' + warn);
    }
  }
  console.log('');
}

// General context growth model
console.log('── Context Growth Model ──');
console.log('');
console.log('Base overhead:     ~75,000 tokens (system prompt + tools + workspace files)');
console.log('Context limit:     200,000 tokens');
console.log('Available for chat: ~125,000 tokens');
console.log('');
console.log('Average growth per exchange (user msg + assistant response + tool calls):');
console.log('  Simple Q&A:      ~500-1,000 tokens');
console.log('  With 1 tool call: ~1,500-3,000 tokens');
console.log('  With 3+ tools:   ~5,000-15,000 tokens');
console.log('  Code generation:  ~2,000-8,000 tokens');
console.log('');

const scenarios = [
  { name: 'Light chat (500 tok/exchange)', growth: 500 },
  { name: 'Normal use (2000 tok/exchange)', growth: 2000 },
  { name: 'Heavy tools (5000 tok/exchange)', growth: 5000 },
  { name: 'Code-heavy (8000 tok/exchange)', growth: 8000 },
];

console.log('  Exchanges until compaction (from fresh session):');
console.log('  ' + 'SCENARIO'.padEnd(38) + 'EXCHANGES'.padEnd(12) + 'COST MULTIPLIER AT LIMIT');
console.log('  ' + '─'.repeat(38) + '─'.repeat(12) + '─'.repeat(25));
for (const s of scenarios) {
  const exchanges = Math.floor(125000 / s.growth);
  // At limit, context is ~200K vs base 75K — cost is 200/75 = 2.67x
  // Halfway there it's ~137K/75K = 1.83x
  const halfwayExchanges = Math.floor(exchanges / 2);
  console.log('  ' + s.name.padEnd(38) + String(exchanges).padEnd(12) + '2.7x base cost');
}

console.log('');
console.log('── Cost Impact of Context Bloat ──');
console.log('');
console.log('  At 50% context (137K tokens):');
console.log('    Opus:     \$' + ((137000/1e6)*15 + (500/1e6)*75).toFixed(2) + '/req (vs \$' + ((75000/1e6)*15 + (500/1e6)*75).toFixed(2) + ' fresh)');
console.log('    DeepSeek: \$' + ((137000/1e6)*0.27 + (500/1e6)*1.10).toFixed(4) + '/req (vs \$' + ((75000/1e6)*0.27 + (500/1e6)*1.10).toFixed(4) + ' fresh)');
console.log('');
console.log('  At 90% context (180K tokens):');
console.log('    Opus:     \$' + ((180000/1e6)*15 + (500/1e6)*75).toFixed(2) + '/req (vs \$' + ((75000/1e6)*15 + (500/1e6)*75).toFixed(2) + ' fresh)');
console.log('    DeepSeek: \$' + ((180000/1e6)*0.27 + (500/1e6)*1.10).toFixed(4) + '/req (vs \$' + ((75000/1e6)*0.27 + (500/1e6)*1.10).toFixed(4) + ' fresh)');

console.log('');
console.log('── Recommendations ──');
console.log('');
console.log('  • Reset sessions after 12-15 exchanges to keep costs low');
console.log('  • Use /reset after topic changes');
console.log('  • Save important context to memory before resetting');
console.log('  • Heavy tool sessions: reset after 5-8 exchanges');
console.log('  • Watch for context >60% — costs are already 1.5-2x base');
"
