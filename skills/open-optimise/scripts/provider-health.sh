#!/bin/bash
# provider-health.sh — Test all configured models for availability and latency
# Usage: bash provider-health.sh [config-path]
# Sends minimal probe requests and reports UP/DOWN/SLOW status

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
echo -e "${BOLD}║     Provider Health Check                ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

RESULTS_FILE="/tmp/provider-health-$(date +%Y%m%d-%H%M%S).json"

node -e "
const fs = require('fs');
const https = require('https');
const http = require('http');

const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();
const providers = config.models?.providers || {};
const aliases = config.agents?.defaults?.models || {};

// Build alias lookup
const aliasLookup = {};
for (const [fullId, cfg] of Object.entries(aliases)) {
  aliasLookup[fullId] = cfg.alias;
}

const costs = {
  'claude-opus-4-6': 0.71,
  'claude-sonnet-4-6': 0.53,
  'claude-haiku-4-5': 0.15,
  'gpt-5.2': 0.44,
  'gpt-5.2-pro': 0.80,
  'o4-mini': 0.10,
  'deepseek-v3.2': 0.04,
  'gemini-flash-latest': 0.04,
  'gemini-3.1-pro-preview': 0.20,
  'grok-4': 0.50,
  'grok-4-1-fast': 0.30,
  'grok-3-mini': 0.08,
};

async function testEndpoint(baseUrl) {
  return new Promise((resolve) => {
    const start = Date.now();
    const mod = baseUrl.startsWith('https') ? https : http;
    const req = mod.get(baseUrl + '/models', { timeout: 5000 }, (res) => {
      const latency = Date.now() - start;
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        resolve({ 
          status: res.statusCode, 
          latency,
          up: res.statusCode < 500
        });
      });
    });
    req.on('error', () => resolve({ status: 0, latency: 0, up: false }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, latency: 5000, up: false }); });
  });
}

async function run() {
  const results = [];
  
  // Test each provider endpoint first
  const endpointResults = {};
  for (const [name, prov] of Object.entries(providers)) {
    if (prov.baseUrl) {
      process.stderr.write('Testing ' + name + '...\n');
      const result = await testEndpoint(prov.baseUrl);
      endpointResults[name] = result;
    }
  }
  
  console.log('  ' + 'MODEL'.padEnd(30) + 'ALIAS'.padEnd(12) + 'STATUS'.padEnd(16) + 'LATENCY'.padEnd(10) + 'COST');
  console.log('  ' + '─'.repeat(30) + '─'.repeat(12) + '─'.repeat(16) + '─'.repeat(10) + '─'.repeat(10));
  
  for (const [provName, prov] of Object.entries(providers)) {
    const models = prov.models || [];
    const endpoint = endpointResults[provName];
    
    for (const m of models) {
      const fullId = provName + '/' + m.id;
      const alias = aliasLookup[fullId] || '-';
      const cost = costs[m.id] || '?';
      
      let status, latencyStr;
      if (!endpoint) {
        status = 'NO URL';
        latencyStr = '-';
      } else if (!endpoint.up) {
        status = '❌ DOWN';
        latencyStr = '-';
      } else if (endpoint.latency > 2000) {
        status = '⚡ SLOW';
        latencyStr = endpoint.latency + 'ms';
      } else if (endpoint.status === 401 || endpoint.status === 403) {
        status = '✅ AUTH OK';
        latencyStr = endpoint.latency + 'ms';
      } else {
        status = '✅ UP';
        latencyStr = endpoint.latency + 'ms';
      }
      
      const costStr = typeof cost === 'number' ? '\$' + cost.toFixed(2) : cost;
      console.log('  ' + (m.name || m.id).padEnd(30) + alias.padEnd(12) + status.padEnd(16) + latencyStr.padEnd(10) + costStr);
      
      results.push({
        provider: provName,
        model: m.id,
        name: m.name || m.id,
        alias,
        status,
        latency: endpoint?.latency || 0,
        cost: typeof cost === 'number' ? cost : null,
        timestamp: new Date().toISOString(),
      });
    }
  }
  
  // Save results
  fs.writeFileSync('$RESULTS_FILE', JSON.stringify(results, null, 2));
  
  console.log('');
  
  // Summary
  const up = results.filter(r => r.status.includes('UP') || r.status.includes('AUTH')).length;
  const down = results.filter(r => r.status.includes('DOWN')).length;
  const slow = results.filter(r => r.status.includes('SLOW')).length;
  console.log('  Summary: ' + up + ' UP, ' + slow + ' SLOW, ' + down + ' DOWN (of ' + results.length + ' models)');
  console.log('  Results saved: $RESULTS_FILE');
}

run().catch(e => console.error(e));
" 2>&1 | grep -v "^Testing "

echo ""
echo -e "${BOLD}Done.${NC}"
