#!/bin/bash
# fallback-validator.sh — Test every model in your fallback chain before it breaks in production
# Usage: bash fallback-validator.sh [config-path]

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
echo -e "${BOLD}║     Fallback Chain Validator             ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

node -e "
const fs = require('fs');
const https = require('https');
const http = require('http');

const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();
const defaults = config.agents?.defaults || {};
const model = defaults.model;
const primary = typeof model === 'string' ? model : model?.primary;
const fallbacks = typeof model === 'object' ? (model.fallbacks || []) : [];
const providers = config.models?.providers || {};

// Build the full chain
const chain = [primary, ...fallbacks].filter(Boolean);

if (chain.length === 0) {
  console.log('  No model chain configured.');
  process.exit(0);
}

console.log('  Testing ' + chain.length + ' model(s) in fallback order...');
console.log('');

// Resolve provider for a model ID
function resolveProvider(modelId) {
  const parts = modelId.split('/');
  // Try provider/model format
  if (parts.length >= 2) {
    const provName = parts[0];
    if (providers[provName]) {
      return { provider: provName, config: providers[provName], modelPart: parts.slice(1).join('/') };
    }
    // Could be provider/org/model (openrouter/anthropic/claude...)
    if (parts.length >= 3 && providers[parts[0]]) {
      return { provider: parts[0], config: providers[parts[0]], modelPart: parts.slice(1).join('/') };
    }
  }
  return null;
}

async function testModel(baseUrl, apiKey, api, modelId) {
  return new Promise((resolve) => {
    const isAnthropic = api === 'anthropic-messages';
    const url = new URL(baseUrl);
    const path = isAnthropic ? '/v1/messages' : '/v1/chat/completions';
    
    const body = isAnthropic
      ? JSON.stringify({ model: modelId, max_tokens: 5, messages: [{ role: 'user', content: 'hi' }] })
      : JSON.stringify({ model: modelId, max_tokens: 5, messages: [{ role: 'user', content: 'hi' }] });
    
    const headers = {
      'Content-Type': 'application/json',
      ...(isAnthropic
        ? { 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' }
        : { 'Authorization': 'Bearer ' + apiKey }),
    };
    
    const opts = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: path,
      method: 'POST',
      headers,
      timeout: 10000,
    };
    
    const start = Date.now();
    const mod = url.protocol === 'https:' ? https : http;
    const req = mod.request(opts, (res) => {
      const latency = Date.now() - start;
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        let error = null;
        if (res.statusCode >= 400) {
          try { error = JSON.parse(data)?.error?.message || data.substring(0, 100); } catch(e) { error = data.substring(0, 100); }
        }
        resolve({ status: res.statusCode, latency, error, up: res.statusCode < 400 });
      });
    });
    req.on('error', (e) => resolve({ status: 0, latency: 0, error: e.message, up: false }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, latency: 10000, error: 'timeout', up: false }); });
    req.write(body);
    req.end();
  });
}

async function run() {
  let lastWorking = null;
  let broken = [];
  let chainOk = true;
  
  for (let i = 0; i < chain.length; i++) {
    const modelId = chain[i];
    const role = i === 0 ? 'PRIMARY' : 'FALLBACK ' + i;
    const prov = resolveProvider(modelId);
    
    process.stdout.write('  ' + role.padEnd(12) + modelId.padEnd(45));
    
    if (!prov) {
      console.log('❌ NO PROVIDER');
      console.log('             Provider \"' + modelId.split('/')[0] + '\" not in config. Add it or remove this fallback.');
      broken.push({ model: modelId, role, reason: 'no provider configured' });
      chainOk = false;
      continue;
    }
    
    if (!prov.config.apiKey || prov.config.apiKey === '') {
      console.log('❌ NO API KEY');
      console.log('             Provider \"' + prov.provider + '\" has no API key.');
      broken.push({ model: modelId, role, reason: 'no API key' });
      chainOk = false;
      continue;
    }
    
    if (!prov.config.baseUrl) {
      console.log('❌ NO BASE URL');
      broken.push({ model: modelId, role, reason: 'no base URL' });
      chainOk = false;
      continue;
    }
    
    // Actually test the model
    const result = await testModel(prov.config.baseUrl, prov.config.apiKey, prov.config.api || 'openai-completions', prov.modelPart || modelId);
    
    if (result.up) {
      console.log('✅ UP (' + result.latency + 'ms)');
      lastWorking = modelId;
    } else if (result.status === 401 || result.status === 403) {
      console.log('❌ AUTH FAILED (HTTP ' + result.status + ')');
      console.log('             ' + (result.error || 'Check API key'));
      broken.push({ model: modelId, role, reason: 'auth failed' });
      chainOk = false;
    } else if (result.status === 404) {
      console.log('❌ MODEL NOT FOUND (404)');
      console.log('             Model ID may be wrong. Check provider docs.');
      broken.push({ model: modelId, role, reason: 'model not found' });
      chainOk = false;
    } else if (result.status === 429) {
      console.log('⚠️  RATE LIMITED (429)');
      console.log('             Model exists but is currently throttled.');
    } else {
      console.log('❌ FAILED (HTTP ' + result.status + ', ' + result.latency + 'ms)');
      if (result.error) console.log('             ' + result.error);
      broken.push({ model: modelId, role, reason: 'HTTP ' + result.status });
      chainOk = false;
    }
  }
  
  console.log('');
  console.log('  ══════════════════════════════════════');
  
  if (chainOk) {
    console.log('  ✅ All ' + chain.length + ' models in the chain are reachable.');
  } else {
    console.log('  ⚠️  ' + broken.length + ' broken model(s) in your fallback chain:');
    console.log('');
    
    for (const b of broken) {
      console.log('  ❌ ' + b.role + ': ' + b.model);
      console.log('     Reason: ' + b.reason);
    }
    
    // Check if chain has gaps
    let hasGap = false;
    for (let i = 0; i < chain.length - 1; i++) {
      if (broken.some(b => b.model === chain[i]) && !broken.some(b => b.model === chain[i+1])) {
        // Broken model before a working one — this is a gap
        hasGap = true;
      }
    }
    
    if (hasGap) {
      console.log('');
      console.log('  🔴 CRITICAL: Broken models BEFORE working ones in the chain.');
      console.log('     OpenClaw may crash on the broken model instead of reaching');
      console.log('     the working fallback. Remove or fix broken models.');
    }
    
    console.log('');
    console.log('  Suggested fix: Remove broken fallbacks from config,');
    console.log('  or add the missing provider with: bash setup-openrouter.sh <key>');
  }
}

run().catch(e => console.error(e));
" 2>/dev/null
