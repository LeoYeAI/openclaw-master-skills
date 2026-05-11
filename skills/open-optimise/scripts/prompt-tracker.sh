#!/bin/bash
# prompt-tracker.sh — Track system prompt size over time, detect growth
# Usage: bash prompt-tracker.sh [workspace-path] [--snapshot|--report]
# --snapshot: Save current state. --report: Compare to previous snapshots.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${1:-$HOME/.openclaw/workspace}"
MODE="${2:---report}"
TRACKER_DIR="$HOME/.openclaw/prompt-snapshots"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$TRACKER_DIR"

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     System Prompt Size Tracker           ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

take_snapshot() {
  local TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  local SNAP_FILE="$TRACKER_DIR/snapshot-${TIMESTAMP}.json"
  
  node -e "
const fs = require('fs');
const path = require('path');
const workspace = '$WORKSPACE';
const files = ['AGENTS.md','SOUL.md','TOOLS.md','IDENTITY.md','USER.md','HEARTBEAT.md','BOOTSTRAP.md','system.md'];

const snapshot = {
  timestamp: new Date().toISOString(),
  workspace: workspace,
  files: {},
  totalChars: 0,
  totalTokensEst: 0,
  skills: {},
};

for (const f of files) {
  const fp = path.join(workspace, f);
  try {
    const content = fs.readFileSync(fp, 'utf8');
    const chars = content.length;
    const tokens = Math.round(chars / 4);
    snapshot.files[f] = { chars, tokens };
    snapshot.totalChars += chars;
    snapshot.totalTokensEst += tokens;
  } catch(e) {
    // File doesn't exist
  }
}

// Check skills
const skillDir = path.join(workspace, 'skills');
try {
  const skills = fs.readdirSync(skillDir, { withFileTypes: true });
  for (const s of skills) {
    if (s.isDirectory()) {
      const skillMd = path.join(skillDir, s.name, 'SKILL.md');
      try {
        const content = fs.readFileSync(skillMd, 'utf8');
        snapshot.skills[s.name] = { chars: content.length, tokens: Math.round(content.length / 4) };
      } catch(e) {}
    }
  }
} catch(e) {}

fs.writeFileSync('$SNAP_FILE', JSON.stringify(snapshot, null, 2));
console.log(JSON.stringify({ file: '$SNAP_FILE', ...snapshot }));
" 2>/dev/null
  
  echo -e "${GREEN}✅ Snapshot saved:${NC} $SNAP_FILE"
}

show_report() {
  SNAPSHOTS=($(ls -t "$TRACKER_DIR"/snapshot-*.json 2>/dev/null))
  
  if [ ${#SNAPSHOTS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No snapshots found. Taking first snapshot now...${NC}"
    echo ""
    take_snapshot
    echo ""
    echo "Run again later to see growth over time."
    return
  fi
  
  node -e "
const fs = require('fs');
const snapFiles = '${SNAPSHOTS[*]}'.split(' ').filter(Boolean);

if (snapFiles.length === 0) {
  console.log('No snapshots to compare.');
  process.exit(0);
}

const snapshots = snapFiles.map(f => JSON.parse(fs.readFileSync(f, 'utf8'))).reverse();

console.log('  ── Snapshot History (' + snapshots.length + ' snapshots) ──');
console.log('');
console.log('  ' + 'DATE'.padEnd(22) + 'TOTAL CHARS'.padEnd(14) + '~TOKENS'.padEnd(10) + 'FILES'.padEnd(8) + 'CHANGE');
console.log('  ' + '─'.repeat(22) + '─'.repeat(14) + '─'.repeat(10) + '─'.repeat(8) + '─'.repeat(12));

for (let i = 0; i < snapshots.length; i++) {
  const s = snapshots[i];
  const fileCount = Object.keys(s.files).length;
  let change = '';
  
  if (i > 0) {
    const prev = snapshots[i - 1];
    const diff = s.totalTokensEst - prev.totalTokensEst;
    if (diff > 0) change = '+' + diff + ' tokens';
    else if (diff < 0) change = diff + ' tokens';
    else change = 'no change';
  } else {
    change = 'baseline';
  }
  
  const date = s.timestamp.substring(0, 19).replace('T', ' ');
  console.log('  ' + date.padEnd(22) + String(s.totalChars).padEnd(14) + ('~' + s.totalTokensEst).padEnd(10) + String(fileCount).padEnd(8) + change);
}

// Detailed diff between newest and oldest
if (snapshots.length >= 2) {
  const oldest = snapshots[0];
  const newest = snapshots[snapshots.length - 1];
  const totalDiff = newest.totalTokensEst - oldest.totalTokensEst;
  
  console.log('');
  console.log('  ── Growth Analysis ──');
  console.log('');
  console.log('  Period: ' + oldest.timestamp.substring(0, 10) + ' → ' + newest.timestamp.substring(0, 10));
  console.log('  Total change: ' + (totalDiff >= 0 ? '+' : '') + totalDiff + ' tokens (' + ((totalDiff / oldest.totalTokensEst) * 100).toFixed(1) + '%)');
  
  // Per-file diff
  const allFiles = new Set([...Object.keys(oldest.files), ...Object.keys(newest.files)]);
  const diffs = [];
  for (const f of allFiles) {
    const oldTok = oldest.files[f]?.tokens || 0;
    const newTok = newest.files[f]?.tokens || 0;
    const diff = newTok - oldTok;
    if (diff !== 0) {
      diffs.push({ file: f, old: oldTok, new: newTok, diff });
    }
  }
  
  if (diffs.length > 0) {
    console.log('');
    console.log('  Files that changed:');
    for (const d of diffs.sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff))) {
      const symbol = d.diff > 0 ? '📈' : '📉';
      console.log('    ' + symbol + ' ' + d.file.padEnd(20) + (d.diff > 0 ? '+' : '') + d.diff + ' tokens (' + d.old + ' → ' + d.new + ')');
    }
  }
  
  // Cost impact
  if (totalDiff !== 0) {
    console.log('');
    console.log('  Cost impact of growth (at 50 req/day):');
    console.log('    On Opus:    ' + (totalDiff > 0 ? '+' : '') + '\$' + ((totalDiff / 1e6) * 15 * 50 * 30).toFixed(2) + '/month');
    console.log('    On DeepSeek: ' + (totalDiff > 0 ? '+' : '') + '\$' + ((totalDiff / 1e6) * 0.27 * 50 * 30).toFixed(2) + '/month');
  }
}

// Current breakdown
const newest = snapshots[snapshots.length - 1];
console.log('');
console.log('  ── Current File Sizes ──');
console.log('');
for (const [f, data] of Object.entries(newest.files).sort((a, b) => b[1].tokens - a[1].tokens)) {
  const bar = '█'.repeat(Math.min(30, Math.round(data.tokens / 100)));
  console.log('    ' + f.padEnd(20) + ('~' + data.tokens).padEnd(8) + bar);
}
" 2>/dev/null
}

case "$MODE" in
  --snapshot|-s)
    take_snapshot
    ;;
  --report|-r|*)
    show_report
    ;;
esac
