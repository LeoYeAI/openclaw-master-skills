#!/bin/bash
# session-replay.sh — Replay a session's cost breakdown exchange by exchange
# Usage: bash session-replay.sh <session-key|"latest"> [log-path]
# Shows exactly where money went in a specific session

set -euo pipefail

SESSION="${1:-latest}"
LOG="${2:-/data/.openclaw/logs/openclaw.log}"
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
echo -e "${BOLD}║     Session Replay Cost Analyzer         ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "Session: $SESSION"
echo ""

if [ ! -f "$LOG" ]; then
  echo -e "${RED}Log file not found: $LOG${NC}"
  echo ""
  echo "This script analyzes session logs to show per-exchange cost breakdowns."
  echo "Without logs, showing general session cost model instead."
  echo ""
  
  node -e "
const overhead = 140000;
const scenarios = [
  { name: 'Simple Q&A (5 exchanges)', exchanges: 5, avgGrowth: 800, avgOutput: 300, toolCalls: 0 },
  { name: 'Research session (15 exchanges)', exchanges: 15, avgGrowth: 3000, avgOutput: 600, toolCalls: 2 },
  { name: 'Coding session (25 exchanges)', exchanges: 25, avgGrowth: 4000, avgOutput: 1500, toolCalls: 1.5 },
  { name: 'Heavy tool session (10 exchanges)', exchanges: 10, avgGrowth: 8000, avgOutput: 500, toolCalls: 4 },
];

const models = [
  { name: 'DeepSeek', inputRate: 0.27, outputRate: 1.10 },
  { name: 'Sonnet', inputRate: 3.00, outputRate: 15.00 },
  { name: 'Opus', inputRate: 15.00, outputRate: 75.00 },
];

for (const s of scenarios) {
  console.log('  ── ' + s.name + ' ──');
  console.log('');
  
  for (const m of models) {
    let totalCost = 0;
    let contextSize = overhead;
    
    for (let i = 0; i < s.exchanges; i++) {
      const inputCost = (contextSize / 1e6) * m.inputRate;
      const outputCost = (s.avgOutput / 1e6) * m.outputRate;
      const toolRoundtrips = s.toolCalls;
      const toolCost = toolRoundtrips * ((contextSize / 1e6) * m.inputRate + (200 / 1e6) * m.outputRate);
      totalCost += inputCost + outputCost + toolCost;
      contextSize += s.avgGrowth;
    }
    
    console.log('    ' + m.name.padEnd(12) + '\$' + totalCost.toFixed(2).padStart(7) + ' total (\$' + (totalCost / s.exchanges).toFixed(2) + ' avg/exchange)');
  }
  console.log('');
}

console.log('  Key insight: The LAST exchange in a long session costs 2-3x the FIRST');
console.log('  because context has grown. Reset early to keep per-exchange cost flat.');
"
  exit 0
fi

node -e "
const fs = require('fs');
const lines = fs.readFileSync('$LOG', 'utf8').split('\n');
const sessionFilter = '$SESSION';

const costs = {
  'claude-opus-4-6': { input: 15.00, output: 75.00 },
  'claude-sonnet-4-6': { input: 3.00, output: 15.00 },
  'claude-haiku-4-5': { input: 0.80, output: 4.00 },
  'deepseek-v3.2': { input: 0.27, output: 1.10 },
  'gpt-5.2': { input: 2.50, output: 10.00 },
  'gemini-flash': { input: 0.10, output: 0.40 },
  'grok-4': { input: 3.00, output: 15.00 },
};

// Find sessions
const sessions = {};
for (const line of lines) {
  const sessMatch = line.match(/session[:\s]+([\w:_-]+)/i);
  if (sessMatch) {
    const key = sessMatch[1];
    if (!sessions[key]) sessions[key] = { lines: [], start: null, end: null };
    sessions[key].lines.push(line);
    
    const dateMatch = line.match(/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})/);
    if (dateMatch) {
      if (!sessions[key].start) sessions[key].start = dateMatch[1];
      sessions[key].end = dateMatch[1];
    }
  }
}

const sessionKeys = Object.keys(sessions);
if (sessionKeys.length === 0) {
  console.log('No sessions found in logs.');
  process.exit(0);
}

// Pick session
let targetKey;
if (sessionFilter === 'latest') {
  targetKey = sessionKeys[sessionKeys.length - 1];
  console.log('  Using latest session: ' + targetKey);
} else {
  targetKey = sessionKeys.find(k => k.includes(sessionFilter));
  if (!targetKey) {
    console.log('  Session \"' + sessionFilter + '\" not found. Available:');
    for (const k of sessionKeys.slice(-10)) {
      const s = sessions[k];
      console.log('    ' + k + ' (' + s.lines.length + ' log entries, ' + (s.start || '?') + ')');
    }
    process.exit(0);
  }
}

const session = sessions[targetKey];
console.log('  Period: ' + (session.start || '?') + ' to ' + (session.end || '?'));
console.log('  Log entries: ' + session.lines.length);
console.log('');

// Analyze entries
let exchanges = [];
let currentExchange = { tools: [], model: null, tokens: {} };
let totalCost = 0;

for (const line of session.lines) {
  // Detect model
  for (const [m] of Object.entries(costs)) {
    if (line.toLowerCase().includes(m)) {
      currentExchange.model = m;
      break;
    }
  }
  
  // Detect tool calls
  const toolMatch = line.match(/tool[_\s]*(?:call|invoke)[:\s]+(\w+)/i)
    || line.match(/\"name\":\s*\"(\w+)\"/);
  if (toolMatch) {
    currentExchange.tools.push(toolMatch[1]);
  }
  
  // Detect token counts
  const tokMatch = line.match(/input[_\s]*tokens?[:\s]+(\d+)/i);
  const outMatch = line.match(/output[_\s]*tokens?[:\s]+(\d+)/i);
  if (tokMatch) currentExchange.tokens.input = parseInt(tokMatch[1]);
  if (outMatch) currentExchange.tokens.output = parseInt(outMatch[1]);
  
  // Detect exchange boundary (new user message or response complete)
  if (/user[_\s]*message|response[_\s]*complete|turn[_\s]*end/i.test(line)) {
    if (currentExchange.model || currentExchange.tools.length > 0) {
      exchanges.push({...currentExchange});
    }
    currentExchange = { tools: [], model: null, tokens: {} };
  }
}
// Push last exchange
if (currentExchange.model || currentExchange.tools.length > 0) {
  exchanges.push(currentExchange);
}

if (exchanges.length === 0) {
  console.log('  Could not parse individual exchanges from log format.');
  console.log('  Showing aggregate stats for the session:');
  console.log('');
  
  // Count tool calls and models in raw log lines
  const toolCounts = {};
  const modelCounts = {};
  for (const line of session.lines) {
    for (const [m] of Object.entries(costs)) {
      if (line.toLowerCase().includes(m)) modelCounts[m] = (modelCounts[m] || 0) + 1;
    }
    const tm = line.match(/tool[_\s]*(?:call|invoke|use)[:\s]+(\w+)/i);
    if (tm) toolCounts[tm[1]] = (toolCounts[tm[1]] || 0) + 1;
  }
  
  if (Object.keys(modelCounts).length > 0) {
    console.log('  Models used:');
    for (const [m, count] of Object.entries(modelCounts).sort((a,b) => b[1] - a[1])) {
      console.log('    ' + m + ': ' + count + ' mentions');
    }
  }
  if (Object.keys(toolCounts).length > 0) {
    console.log('');
    console.log('  Tool calls:');
    for (const [t, count] of Object.entries(toolCounts).sort((a,b) => b[1] - a[1])) {
      console.log('    ' + t + ': ' + count + 'x');
    }
  }
} else {
  console.log('  ── Exchange-by-Exchange Breakdown ──');
  console.log('');
  
  let mostExpensive = { idx: 0, cost: 0 };
  
  for (let i = 0; i < exchanges.length; i++) {
    const ex = exchanges[i];
    const model = ex.model || 'unknown';
    const pricing = costs[model] || { input: 5, output: 20 };
    const inputTok = ex.tokens.input || 140000;
    const outputTok = ex.tokens.output || 500;
    const inputCost = (inputTok / 1e6) * pricing.input;
    const outputCost = (outputTok / 1e6) * pricing.output;
    const toolCost = ex.tools.length * 0.05; // rough estimate per tool call
    const exCost = inputCost + outputCost + toolCost;
    totalCost += exCost;
    
    if (exCost > mostExpensive.cost) {
      mostExpensive = { idx: i + 1, cost: exCost, model, tools: ex.tools };
    }
    
    const toolStr = ex.tools.length > 0 ? ' [' + ex.tools.join(', ') + ']' : '';
    console.log('  #' + String(i + 1).padStart(2) + ' ' + (model || '?').padEnd(20) + ' \$' + exCost.toFixed(3).padStart(6) + toolStr);
  }
  
  console.log('');
  console.log('  Total session cost: \$' + totalCost.toFixed(2));
  console.log('  Average per exchange: \$' + (totalCost / exchanges.length).toFixed(3));
  console.log('');
  console.log('  🔴 Most expensive: Exchange #' + mostExpensive.idx + ' (\$' + mostExpensive.cost.toFixed(3) + ')');
  if (mostExpensive.tools.length > 0) {
    console.log('     Tool calls: ' + mostExpensive.tools.join(', '));
  }
}
" 2>/dev/null || echo "Log parsing failed"
