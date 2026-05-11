#!/bin/bash
# tool-audit.sh — Audit tool usage from logs: find waste, loops, and unused tools
# Usage: bash tool-audit.sh [log-path] [days-back]

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
echo -e "${BOLD}║     Tool Call Audit                      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Log: $LOG | Last $DAYS days"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${YELLOW}Log file not found. Showing known tool list with overhead estimates.${NC}"
  echo ""
  # Known tools with approximate schema sizes
  node -e "
const tools = [
  { name: 'read', tokens: 200, desc: 'File reading' },
  { name: 'write', tokens: 150, desc: 'File writing' },
  { name: 'edit', tokens: 200, desc: 'File editing' },
  { name: 'exec', tokens: 350, desc: 'Shell commands' },
  { name: 'process', tokens: 250, desc: 'Process management' },
  { name: 'web_search', tokens: 250, desc: 'Web search' },
  { name: 'web_fetch', tokens: 150, desc: 'URL fetching' },
  { name: 'browser', tokens: 800, desc: 'Browser automation' },
  { name: 'canvas', tokens: 200, desc: 'Canvas/UI presentation' },
  { name: 'nodes', tokens: 600, desc: 'Device control' },
  { name: 'cron', tokens: 800, desc: 'Scheduled jobs' },
  { name: 'message', tokens: 1200, desc: 'Messaging' },
  { name: 'gateway', tokens: 250, desc: 'Config management' },
  { name: 'sessions_spawn', tokens: 300, desc: 'Subagent spawning' },
  { name: 'sessions_list', tokens: 150, desc: 'Session listing' },
  { name: 'sessions_send', tokens: 150, desc: 'Cross-session messaging' },
  { name: 'sessions_history', tokens: 150, desc: 'Session history' },
  { name: 'sessions_yield', tokens: 80, desc: 'Turn yielding' },
  { name: 'subagents', tokens: 150, desc: 'Subagent management' },
  { name: 'session_status', tokens: 150, desc: 'Status display' },
  { name: 'image', tokens: 150, desc: 'Image analysis' },
  { name: 'pdf', tokens: 150, desc: 'PDF analysis' },
  { name: 'memory_search', tokens: 150, desc: 'Memory search' },
  { name: 'memory_get', tokens: 100, desc: 'Memory read' },
  { name: 'tts', tokens: 100, desc: 'Text to speech' },
  { name: 'agents_list', tokens: 80, desc: 'Agent listing' },
];

let total = 0;
console.log('  ' + 'TOOL'.padEnd(22) + 'SCHEMA'.padEnd(10) + 'OVERHEAD/MO'.padEnd(14) + 'DESCRIPTION');
console.log('  ' + '─'.repeat(22) + '─'.repeat(10) + '─'.repeat(14) + '─'.repeat(20));
for (const t of tools.sort((a,b) => b.tokens - a.tokens)) {
  total += t.tokens;
  // Monthly overhead: tokens * requests/day * days * price
  const monthlyOpus = (t.tokens / 1e6) * 15 * 50 * 30;
  const monthlyDS = (t.tokens / 1e6) * 0.27 * 50 * 30;
  console.log('  ' + t.name.padEnd(22) + ('~' + t.tokens).padEnd(10) + '\$' + monthlyOpus.toFixed(2).padStart(6) + ' opus' + '  ' + t.desc);
}
console.log('');
console.log('  Total schema overhead: ~' + total + ' tokens');
console.log('  Monthly cost of ALL tool schemas:');
console.log('    On Opus:    \$' + ((total/1e6)*15*50*30).toFixed(2) + '/month');
console.log('    On DeepSeek: \$' + ((total/1e6)*0.27*50*30).toFixed(2) + '/month');
console.log('');
console.log('  ── Disable Candidates (unused by most users) ──');
console.log('  tts, canvas, nodes, pdf, image — saves ~1200 tokens/request');
console.log('  On Opus that\\'s \$' + ((1200/1e6)*15*50*30).toFixed(2) + '/month');
"
  exit 0
fi

# Parse logs for tool usage
node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const daysBack = $DAYS;
const cutoff = new Date(Date.now() - daysBack * 86400000);

const toolUsage = {};
const duplicates = {};
let totalCalls = 0;

for (const line of lines) {
  const dateMatch = line.match(/(\d{4}-\d{2}-\d{2})/);
  if (dateMatch && new Date(dateMatch[1]) < cutoff) continue;

  // Look for tool call patterns
  const toolMatch = line.match(/tool[_\s]*(?:call|invoke|use|run)[:\s]+(\w+)/i) 
    || line.match(/\"(?:tool|name)\":\s*\"(\w+)\"/i)
    || line.match(/antml:invoke name=\"(\w+)\"/);
  
  if (toolMatch) {
    const tool = toolMatch[1];
    toolUsage[tool] = (toolUsage[tool] || 0) + 1;
    totalCalls++;
    
    // Track potential duplicates (same tool + nearby params)
    const paramSnippet = line.substring(line.indexOf(tool), line.indexOf(tool) + 200);
    const key = tool + ':' + paramSnippet.substring(0, 80);
    duplicates[key] = (duplicates[key] || 0) + 1;
  }
}

if (totalCalls === 0) {
  console.log('No tool calls found in logs. Log format may not include tool invocations,');
  console.log('or tool calls are recorded differently. Try the --no-logs mode.');
  process.exit(0);
}

console.log('── Tool Usage (last ' + daysBack + ' days) ──');
console.log('');
console.log('  Total tool calls: ' + totalCalls);
console.log('');

const sorted = Object.entries(toolUsage).sort((a,b) => b[1] - a[1]);
console.log('  ' + 'TOOL'.padEnd(22) + 'CALLS'.padEnd(8) + 'EST COST (Opus)');
console.log('  ' + '─'.repeat(22) + '─'.repeat(8) + '─'.repeat(15));
for (const [tool, count] of sorted) {
  // Each tool call = ~1 full roundtrip on Opus
  const cost = count * 0.71;
  console.log('  ' + tool.padEnd(22) + String(count).padEnd(8) + '\$' + cost.toFixed(2));
}

// Find duplicates
const dupes = Object.entries(duplicates).filter(([k,v]) => v > 2);
if (dupes.length > 0) {
  console.log('');
  console.log('  ── Potential Duplicate/Loop Calls ──');
  for (const [key, count] of dupes.sort((a,b) => b[1] - a[1]).slice(0, 10)) {
    const tool = key.split(':')[0];
    console.log('  ⚠️  ' + tool + ' called ' + count + 'x with similar params');
  }
}

// Find tools in schema but never used
const allKnownTools = ['read','write','edit','exec','process','web_search','web_fetch','browser','canvas','nodes','cron','message','gateway','sessions_spawn','sessions_list','sessions_send','sessions_history','sessions_yield','subagents','session_status','image','pdf','memory_search','memory_get','tts','agents_list'];
const unused = allKnownTools.filter(t => !toolUsage[t]);
if (unused.length > 0) {
  console.log('');
  console.log('  ── Never Used (disable candidates) ──');
  console.log('  ' + unused.join(', '));
  console.log('  Disabling these saves ~' + (unused.length * 200) + ' tokens/request overhead');
}
" 2>/dev/null || echo "Log parsing failed"
