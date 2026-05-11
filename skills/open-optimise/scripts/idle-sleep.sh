#!/bin/bash
# idle-sleep.sh — Detect idle periods and generate heartbeat adjustment patch
# Usage: bash idle-sleep.sh [log-path] [idle-hours] [sleep-interval]
# Default: idle after 4 hours, sleep heartbeat every 4h
# Designed to run as a cron job every 30 minutes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="${1:-/data/.openclaw/logs/openclaw.log}"
IDLE_HOURS="${2:-4}"
SLEEP_INTERVAL="${3:-240m}"
CONFIG="$HOME/.openclaw/openclaw.json"
STATE_FILE="$HOME/.openclaw/idle-state.json"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

for p in "$LOG" "$HOME/.openclaw/logs/openclaw.log" "/var/log/openclaw.log"; do
  if [ -f "$p" ]; then LOG="$p"; break; fi
done

node -e "
const fs = require('fs');
const logPath = '$LOG';
const configPath = '$CONFIG';
const stateFile = '$STATE_FILE';
const idleHours = $IDLE_HOURS;
const sleepInterval = '$SLEEP_INTERVAL';

// Load current state
let state = { mode: 'active', lastTransition: null, originalHeartbeat: null };
try { state = JSON.parse(fs.readFileSync(stateFile, 'utf8')); } catch(e) {}

// Find last user message timestamp from logs
let lastUserMessage = null;
try {
  const lines = fs.readFileSync(logPath, 'utf8').split('\n');
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i];
    // Look for user message indicators (not heartbeat, not system)
    if (/user[_\s]*message|inbound|received/i.test(line) && !/heartbeat|system|cron/i.test(line)) {
      const dateMatch = line.match(/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})/);
      if (dateMatch) {
        lastUserMessage = new Date(dateMatch[1]);
        break;
      }
    }
  }
} catch(e) {}

const now = new Date();
const idleMs = idleHours * 3600000;

if (!lastUserMessage) {
  console.log('Could not determine last user message from logs.');
  console.log('State: ' + state.mode);
  process.exit(0);
}

const timeSinceLastMsg = now - lastUserMessage;
const hoursSinceLastMsg = timeSinceLastMsg / 3600000;

console.log('Last user message: ' + lastUserMessage.toISOString());
console.log('Time since: ' + hoursSinceLastMsg.toFixed(1) + ' hours');
console.log('Idle threshold: ' + idleHours + ' hours');
console.log('Current mode: ' + state.mode);
console.log('');

if (hoursSinceLastMsg >= idleHours && state.mode === 'active') {
  // Transition to sleep
  console.log('💤 GOING TO SLEEP — idle for ' + hoursSinceLastMsg.toFixed(1) + ' hours');
  console.log('');
  
  // Save current heartbeat config
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    const config = new Function('return (' + raw + ')')();
    const hb = config.agents?.defaults?.heartbeat || {};
    state.originalHeartbeat = {
      every: hb.every || '30m',
      model: hb.model || null,
    };
  } catch(e) {}
  
  state.mode = 'sleeping';
  state.lastTransition = now.toISOString();
  
  // Generate patch to extend heartbeat
  const patch = {
    agents: {
      defaults: {
        heartbeat: {
          every: sleepInterval,
        }
      }
    }
  };
  
  console.log('Extending heartbeat to every ' + sleepInterval);
  console.log('Patch: ' + JSON.stringify(patch));
  console.log('');
  console.log('To apply: use gateway config.patch with the above JSON');
  console.log('Agent will wake automatically on next user message.');
  
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
  
} else if (hoursSinceLastMsg < idleHours && state.mode === 'sleeping') {
  // Wake up
  console.log('☀️  WAKING UP — user active ' + hoursSinceLastMsg.toFixed(1) + ' hours ago');
  console.log('');
  
  const originalEvery = state.originalHeartbeat?.every || '55m';
  const originalModel = state.originalHeartbeat?.model;
  
  const patch = {
    agents: {
      defaults: {
        heartbeat: {
          every: originalEvery,
          ...(originalModel ? { model: originalModel } : {}),
        }
      }
    }
  };
  
  console.log('Restoring heartbeat to every ' + originalEvery);
  console.log('Patch: ' + JSON.stringify(patch));
  
  state.mode = 'active';
  state.lastTransition = now.toISOString();
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
  
} else if (state.mode === 'sleeping') {
  console.log('💤 Still sleeping. Idle for ' + hoursSinceLastMsg.toFixed(1) + ' hours.');
  console.log('Will wake on next user message.');
  
  // Calculate savings
  const normalInterval = parseInt(state.originalHeartbeat?.every) || 55;
  const sleepMins = parseInt(sleepInterval) || 240;
  const savedHbPerHour = (60 / normalInterval) - (60 / sleepMins);
  const savedHours = hoursSinceLastMsg - idleHours;
  const savedHb = savedHbPerHour * savedHours;
  console.log('Heartbeats saved this idle period: ~' + Math.round(savedHb));
  
} else {
  console.log('✅ Active and awake. User was active ' + hoursSinceLastMsg.toFixed(1) + ' hours ago.');
}
" 2>/dev/null
