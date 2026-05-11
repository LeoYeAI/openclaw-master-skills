#!/bin/bash
# compaction-log.sh — Track compaction events and memory flush effectiveness
# Usage: bash compaction-log.sh [log-path] [days-back]

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
echo -e "${BOLD}║     Compaction Event Logger              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Log: $LOG | Last $DAYS days"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${YELLOW}Log file not found. Showing compaction overview from config.${NC}"
  echo ""
  
  CONFIG="$HOME/.openclaw/openclaw.json"
  if [ -f "$CONFIG" ]; then
    node -e "
const raw = require('fs').readFileSync('$CONFIG','utf8');
const c = new Function('return ('+raw+')')();
const comp = c.agents?.defaults?.compaction || {};
const mf = comp.memoryFlush || {};

console.log('Compaction Config:');
console.log('  Mode:               ' + (comp.mode || 'default'));
console.log('  Reserve tokens:     ' + (comp.reserveTokens || 'default'));
console.log('  Keep recent tokens: ' + (comp.keepRecentTokens || 'default'));
console.log('  Max history share:  ' + (comp.maxHistoryShare || 'default'));
console.log('  Recent turns kept:  ' + (comp.recentTurnsPreserve || 'default (3)'));
console.log('  Compaction model:   ' + (comp.model || 'same as primary'));
console.log('');
console.log('Memory Flush:');
console.log('  Enabled:            ' + (mf.enabled || false));
console.log('  Soft threshold:     ' + (mf.softThresholdTokens || 'default') + ' tokens');
console.log('  Force flush bytes:  ' + (mf.forceFlushTranscriptBytes || 'default'));
console.log('');
if (mf.enabled) {
  console.log('  ✅ Memory flush is active — context will be saved before compaction');
} else {
  console.log('  ⚠️  Memory flush disabled — compaction may lose important context');
  console.log('  Recommendation: enable with softThresholdTokens: 3000');
}
"
  fi
  exit 0
fi

# Parse logs for compaction events
node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const daysBack = $DAYS;
const cutoff = new Date(Date.now() - daysBack * 86400000);

const events = [];
let compactions = 0;
let memFlushes = 0;

for (const line of lines) {
  const dateMatch = line.match(/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})/);
  if (dateMatch && new Date(dateMatch[1]) < cutoff) continue;
  
  const timestamp = dateMatch ? dateMatch[1] : null;
  
  // Compaction events
  if (/compaction|compact/i.test(line) && !/config|setting/i.test(line)) {
    compactions++;
    
    // Try to extract token info
    const preMatch = line.match(/pre[_-]?compact[^:]*:\s*(\d+)/i) || line.match(/before[:\s]+(\d+)/i);
    const postMatch = line.match(/post[_-]?compact[^:]*:\s*(\d+)/i) || line.match(/after[:\s]+(\d+)/i);
    
    events.push({
      timestamp,
      type: 'compaction',
      preTok: preMatch ? parseInt(preMatch[1]) : null,
      postTok: postMatch ? parseInt(postMatch[1]) : null,
      raw: line.substring(0, 200),
    });
  }
  
  // Memory flush events
  if (/memory[_\s]*flush/i.test(line)) {
    memFlushes++;
    events.push({
      timestamp,
      type: 'memory_flush',
      raw: line.substring(0, 200),
    });
  }
}

console.log('── Summary (last ' + daysBack + ' days) ──');
console.log('');
console.log('  Compaction events:    ' + compactions);
console.log('  Memory flush events:  ' + memFlushes);

if (compactions > 0 && memFlushes > 0) {
  const ratio = (memFlushes / compactions * 100).toFixed(0);
  console.log('  Flush coverage:       ' + ratio + '% of compactions had a memory flush');
  if (parseInt(ratio) < 80) {
    console.log('  ⚠️  Some compactions ran without memory flush — context may have been lost');
  } else {
    console.log('  ✅ Good coverage — most compactions had memory preserved first');
  }
}

if (events.length > 0) {
  console.log('');
  console.log('── Event Timeline ──');
  console.log('');
  for (const e of events.slice(-30)) {
    if (e.type === 'compaction') {
      let detail = '';
      if (e.preTok && e.postTok) {
        const saved = e.preTok - e.postTok;
        detail = ' (' + (e.preTok/1000).toFixed(0) + 'k → ' + (e.postTok/1000).toFixed(0) + 'k, freed ' + (saved/1000).toFixed(0) + 'k)';
      }
      console.log('  🧹 ' + (e.timestamp || '?') + ' COMPACTION' + detail);
    } else {
      console.log('  💾 ' + (e.timestamp || '?') + ' MEMORY FLUSH');
    }
  }
} else if (compactions === 0) {
  console.log('');
  console.log('  No compaction events found. Either:');
  console.log('  - Sessions are being reset before hitting limits (good!)');
  console.log('  - Logs don\\'t record compaction events');
  console.log('  - Sessions haven\\'t been long enough to trigger compaction');
}

// Cost of compaction
if (compactions > 0) {
  console.log('');
  console.log('── Compaction Cost ──');
  console.log('');
  console.log('  Each compaction triggers an extra model call to summarize context.');
  console.log('  On Opus: ~\$0.71 per compaction × ' + compactions + ' = \$' + (0.71 * compactions).toFixed(2));
  console.log('  On DeepSeek: ~\$0.04 per compaction × ' + compactions + ' = \$' + (0.04 * compactions).toFixed(2));
  console.log('');
  console.log('  Tip: Set compaction.model to a cheaper model if using Opus as primary.');
}
" 2>/dev/null || echo "Log parsing failed"
