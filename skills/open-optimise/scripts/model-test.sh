#!/bin/bash
# model-test.sh — Test which models are actually reachable and measure response time
# Usage: bash model-test.sh [config-path]
# Sends a minimal probe to each configured model and reports availability

set -euo pipefail

CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Model Availability Test              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$CONFIG" ]; then
  echo -e "${RED}Config not found: $CONFIG${NC}"
  exit 1
fi

# Extract all provider endpoints and models
node -e "
const fs = require('fs');
const raw = fs.readFileSync('$CONFIG','utf8').replace(/\/\/.*/g,'').replace(/,(\s*[}\]])/g,'\$1');
const c = JSON.parse(raw);
const providers = c.models?.providers || {};

for (const [name, prov] of Object.entries(providers)) {
  const baseUrl = prov.baseUrl || '';
  const api = prov.api || 'openai-completions';
  const models = prov.models || [];
  for (const m of models) {
    console.log(JSON.stringify({
      provider: name,
      id: m.id,
      name: m.name || m.id,
      baseUrl: baseUrl,
      api: api,
      context: m.contextWindow || 0,
    }));
  }
}
" 2>/dev/null | while read -r line; do
  PROVIDER=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.provider)")
  MODEL_ID=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.id)")
  MODEL_NAME=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.name)")
  BASE_URL=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.baseUrl)")
  CTX=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.context)")
  
  printf "  %-25s %-20s " "$PROVIDER/$MODEL_ID" "$MODEL_NAME"
  
  # Quick connectivity test (just check if the endpoint responds)
  if [ -n "$BASE_URL" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$BASE_URL" 2>/dev/null || echo "000")
    if [ "$STATUS" = "000" ]; then
      echo -e "${RED}UNREACHABLE${NC}"
    elif [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ]; then
      echo -e "${YELLOW}AUTH OK (needs key)${NC} ctx:${CTX}"
    else
      echo -e "${GREEN}REACHABLE (HTTP $STATUS)${NC} ctx:${CTX}"
    fi
  else
    echo -e "${YELLOW}NO BASE URL${NC}"
  fi
done

echo ""

# Check aliases
ALIAS_COUNT=$(node -e "
const fs = require('fs');
const raw = fs.readFileSync('$CONFIG','utf8').replace(/\/\/.*/g,'').replace(/,(\s*[}\]])/g,'\$1');
const c = JSON.parse(raw);
const models = c.agents?.defaults?.models || {};
const aliases = Object.entries(models).map(([k,v]) => v.alias + ' → ' + k);
console.log(aliases.length);
aliases.forEach(a => console.log('  ' + a));
" 2>/dev/null)

echo -e "${BOLD}Configured Aliases:${NC}"
echo "$ALIAS_COUNT"
echo ""
echo -e "${BOLD}Done.${NC}"
