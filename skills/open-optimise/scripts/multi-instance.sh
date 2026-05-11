#!/bin/bash
# multi-instance.sh — Aggregate costs across multiple OpenClaw instances
# Usage: bash multi-instance.sh [instances-config]
# Config file: ~/.openclaw/instances.json

set -euo pipefail

INSTANCES_FILE="${1:-$HOME/.openclaw/instances.json}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Multi-Instance Cost Aggregator       ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$INSTANCES_FILE" ]; then
  echo -e "${YELLOW}No instances config found at $INSTANCES_FILE${NC}"
  echo ""
  echo "Create it with this format:"
  echo ""
  cat << 'EXAMPLE'
{
  "instances": [
    {
      "name": "personal",
      "url": "http://localhost:3578",
      "token": "your-gateway-token",
      "description": "Personal assistant"
    },
    {
      "name": "work-vps",
      "url": "https://myclaw.example.com:3578",
      "token": "gateway-token-for-vps",
      "description": "Work coding assistant"
    },
    {
      "name": "local",
      "configPath": "/root/.openclaw/openclaw.json",
      "logPath": "/data/.openclaw/logs/openclaw.log",
      "description": "This instance (local access)"
    }
  ]
}
EXAMPLE
  echo ""
  echo "Instances can be remote (url + token) or local (configPath + logPath)."
  echo "Save to: $INSTANCES_FILE"
  exit 0
fi

node -e "
const fs = require('fs');
const https = require('https');
const http = require('http');

const config = JSON.parse(fs.readFileSync('$INSTANCES_FILE', 'utf8'));
const instances = config.instances || [];

const costs = {
  'claude-opus-4-6': 0.71, 'claude-sonnet-4-6': 0.53, 'claude-haiku-4-5': 0.15,
  'gpt-5.2': 0.44, 'deepseek-v3.2': 0.04, 'minimax-m2.5': 0.04,
  'gemini-flash-latest': 0.04, 'grok-4': 0.50,
};

async function fetchRemote(url, token) {
  return new Promise((resolve) => {
    const parsed = new URL(url + '/api/config');
    const mod = parsed.protocol === 'https:' ? https : http;
    const req = mod.get({
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname,
      headers: { 'Authorization': 'Bearer ' + token },
      timeout: 10000,
    }, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch(e) { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
  });
}

function analyzeLocal(configPath, logPath) {
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    const config = new Function('return (' + raw + ')')();
    const d = config.agents?.defaults || {};
    const m = d.model;
    const primary = typeof m === 'string' ? m : m?.primary || 'unknown';
    const hb = d.heartbeat || {};
    
    const pName = primary.split('/').pop();
    const pCost = costs[pName] || 0.50;
    const hbModel = (hb.model || primary).split('/').pop();
    const hbCost = costs[hbModel] || 0.04;
    const hbMins = parseInt(hb.every) || 30;
    const hbPerDay = (24 * 60) / hbMins;
    
    return {
      primary: pName,
      primaryCost: pCost,
      heartbeatModel: hbModel,
      heartbeatCost: hbCost * hbPerDay,
      estimatedDailyReqs: 50,
      estimatedDailyCost: pCost * 50 + hbCost * hbPerDay,
      status: 'ok',
    };
  } catch(e) {
    return { status: 'error', error: e.message };
  }
}

async function run() {
  let grandTotal = 0;
  const results = [];
  
  for (const inst of instances) {
    process.stderr.write('Checking ' + inst.name + '...\n');
    
    let data;
    if (inst.configPath) {
      data = analyzeLocal(inst.configPath, inst.logPath);
    } else if (inst.url && inst.token) {
      const remote = await fetchRemote(inst.url, inst.token);
      if (remote) {
        // Parse remote config similar to local
        const d = remote.agents?.defaults || {};
        const m = d.model;
        const primary = (typeof m === 'string' ? m : m?.primary || 'unknown').split('/').pop();
        const pCost = costs[primary] || 0.50;
        data = {
          primary,
          primaryCost: pCost,
          estimatedDailyCost: pCost * 50,
          status: 'ok',
        };
      } else {
        data = { status: 'unreachable' };
      }
    } else {
      data = { status: 'no access configured' };
    }
    
    results.push({ ...inst, ...data });
  }
  
  console.log('  ' + 'INSTANCE'.padEnd(18) + 'MODEL'.padEnd(20) + 'DAILY EST'.padEnd(14) + 'MONTHLY EST'.padEnd(14) + 'STATUS');
  console.log('  ' + '─'.repeat(18) + '─'.repeat(20) + '─'.repeat(14) + '─'.repeat(14) + '─'.repeat(14));
  
  for (const r of results) {
    if (r.status === 'ok') {
      const daily = r.estimatedDailyCost || 0;
      const monthly = daily * 30;
      grandTotal += monthly;
      console.log('  ' + r.name.padEnd(18) + (r.primary || '?').padEnd(20) + ('\$' + daily.toFixed(2)).padEnd(14) + ('\$' + monthly.toFixed(0)).padEnd(14) + '✅ OK');
    } else {
      console.log('  ' + r.name.padEnd(18) + '-'.padEnd(20) + '-'.padEnd(14) + '-'.padEnd(14) + '❌ ' + r.status);
    }
  }
  
  console.log('');
  console.log('  ' + ''.padEnd(38) + 'TOTAL'.padEnd(14) + '\$' + grandTotal.toFixed(0) + '/month');
  
  // Find the most expensive
  const sorted = results.filter(r => r.status === 'ok').sort((a, b) => (b.estimatedDailyCost || 0) - (a.estimatedDailyCost || 0));
  if (sorted.length > 1) {
    console.log('');
    console.log('  🔴 Most expensive: ' + sorted[0].name + ' (\$' + (sorted[0].estimatedDailyCost * 30).toFixed(0) + '/month on ' + sorted[0].primary + ')');
    if (sorted[0].primaryCost > 0.20) {
      console.log('     Switching to DeepSeek would save ~\$' + ((sorted[0].primaryCost - 0.04) * 50 * 30).toFixed(0) + '/month on this instance alone');
    }
  }
}

run().catch(e => console.error(e));
" 2>&1 | grep -v "^Checking "
