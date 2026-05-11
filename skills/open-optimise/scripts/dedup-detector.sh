#!/bin/bash
# dedup-detector.sh — Find duplicate/redundant requests and tool calls in logs
# Usage: bash dedup-detector.sh [log-path] [days-back]

set -euo pipefail

LOG="${1:-/data/.openclaw/logs/openclaw.log}"
DAYS="${2:-1}"
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
echo -e "${BOLD}║     Request Deduplication Detector       ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Log: $LOG | Last $DAYS day(s)"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${YELLOW}Log not found. Showing common duplication patterns to watch for.${NC}"
  echo ""
  echo "  Common waste patterns:"
  echo "  1. web_search called with same query multiple times in one session"
  echo "  2. read() on same file multiple times (agent forgot it already read it)"
  echo "  3. session_status called repeatedly (checking model/context)"
  echo "  4. memory_search with same query (forgets previous search)"
  echo "  5. exec() running identical commands"
  echo ""
  echo "  Each duplicate pays full 140K overhead again."
  echo "  At Opus pricing: each unnecessary call wastes ~\$0.71"
  exit 0
fi

node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const daysBack = $DAYS;
const cutoff = new Date(Date.now() - daysBack * 86400000);

// Track tool calls with their parameters
const toolCalls = [];
const sessions = {};

for (const line of lines) {
  const dateMatch = line.match(/(\d{4}-\d{2}-\d{2})/);
  if (dateMatch && new Date(dateMatch[1]) < cutoff) continue;
  
  // Extract session
  const sessMatch = line.match(/session[:\s]+([\w:_-]+)/i);
  const session = sessMatch ? sessMatch[1] : 'unknown';
  
  // Extract tool call with params
  const toolMatch = line.match(/tool[_\s]*(?:call|invoke)[:\s]+(\w+)/i)
    || line.match(/antml:invoke name=\"(\w+)\"/i);
  
  if (toolMatch) {
    const tool = toolMatch[1];
    // Extract a fingerprint from nearby content
    const paramStart = line.indexOf(tool) + tool.length;
    const paramSnippet = line.substring(paramStart, paramStart + 150).replace(/\s+/g, ' ').trim();
    
    toolCalls.push({ tool, params: paramSnippet, session, line: line.substring(0, 200) });
    
    if (!sessions[session]) sessions[session] = [];
    sessions[session].push({ tool, params: paramSnippet });
  }
}

if (toolCalls.length === 0) {
  console.log('  No tool calls found in recent logs.');
  console.log('  Log format may not include tool invocations at parseable granularity.');
  process.exit(0);
}

console.log('  Total tool calls found: ' + toolCalls.length);
console.log('  Sessions: ' + Object.keys(sessions).length);
console.log('');

// Find duplicates within sessions
let totalDuplicates = 0;
let wastedCost = 0;

for (const [sessId, calls] of Object.entries(sessions)) {
  const seen = {};
  const dupes = [];
  
  for (const call of calls) {
    const key = call.tool + ':' + call.params.substring(0, 80);
    if (seen[key]) {
      seen[key]++;
      if (seen[key] === 2) dupes.push({ tool: call.tool, count: 0, params: call.params.substring(0, 60) });
      dupes.find(d => d.tool === call.tool && d.params === call.params.substring(0, 60)).count = seen[key];
    } else {
      seen[key] = 1;
    }
  }
  
  if (dupes.length > 0) {
    console.log('  ── Session: ' + sessId + ' (' + calls.length + ' tool calls) ──');
    for (const d of dupes) {
      const waste = (d.count - 1) * 0.50; // average cost estimate
      wastedCost += waste;
      totalDuplicates += d.count - 1;
      console.log('    ⚠️  ' + d.tool + ' called ' + d.count + 'x with similar params');
      if (d.params) console.log('       Params: ' + d.params);
    }
    console.log('');
  }
}

// Find global patterns (same tool called many times regardless of params)
const toolFreq = {};
for (const call of toolCalls) {
  toolFreq[call.tool] = (toolFreq[call.tool] || 0) + 1;
}

const highFreq = Object.entries(toolFreq).filter(([_, c]) => c > 10).sort((a, b) => b[1] - a[1]);
if (highFreq.length > 0) {
  console.log('  ── High-Frequency Tool Calls ──');
  console.log('');
  for (const [tool, count] of highFreq) {
    const emoji = count > 50 ? '🔴' : count > 20 ? '🟡' : '🔵';
    console.log('    ' + emoji + ' ' + tool.padEnd(20) + count + ' calls');
  }
  console.log('');
}

// Summary
console.log('  ── Summary ──');
console.log('');
if (totalDuplicates > 0) {
  console.log('  Duplicate tool calls found: ' + totalDuplicates);
  console.log('  Estimated wasted cost: ~\$' + wastedCost.toFixed(2));
  console.log('');
  console.log('  Tips to reduce duplicates:');
  console.log('  - Agent should cache tool results in conversation context');
  console.log('  - Use memory for data that persists across sessions');
  console.log('  - Batch multiple questions into one message');
} else {
  console.log('  ✅ No obvious duplicate tool calls detected');
  console.log('  (Note: detection depends on log format capturing tool invocations)');
}
" 2>/dev/null || echo "Log parsing failed"
