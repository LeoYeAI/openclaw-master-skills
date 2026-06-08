#!/usr/bin/env bash
# ClawMoney Skill - Fully Automated Setup
# Installs bnbot-mcp-server + .mcp.json silently, checks wallet status.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }

# --- 1. Node.js ---
if ! command -v npx &>/dev/null; then
  fail "Node.js not found. Install from https://nodejs.org (v18+)"
  exit 1
fi
ok "Node.js $(node -v 2>/dev/null || echo '')"

# --- 2. bnbot-mcp-server (silent) ---
if command -v bnbot-mcp-server &>/dev/null; then
  ok "bnbot-mcp-server"
else
  npm install -g bnbot-mcp-server 2>/dev/null && ok "bnbot-mcp-server installed" || true
fi

# --- 3. bnbot skill (silent) ---
if command -v clawhub &>/dev/null; then
  if clawhub list 2>/dev/null | grep -q "bnbot"; then
    ok "bnbot skill"
  else
    clawhub install bnbot 2>/dev/null && ok "bnbot skill installed" || true
  fi
fi

# --- 4. .mcp.json (silent) ---
find_project_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    [[ -f "$dir/.mcp.json" || -f "$dir/package.json" ]] && echo "$dir" && return
    dir="$(dirname "$dir")"
  done
  echo "$PWD"
}

MCP_FILE="$(find_project_root)/.mcp.json"

needs_bnbot() {
  [[ ! -f "$MCP_FILE" ]] && return 0
  python3 -c "
import json,sys
with open('$MCP_FILE') as f: d=json.load(f)
sys.exit(0 if 'bnbot' not in d.get('mcpServers',{}) else 1)
" 2>/dev/null
}

if needs_bnbot; then
  if [[ -f "$MCP_FILE" ]]; then
    python3 -c "
import json
with open('$MCP_FILE') as f: d=json.load(f)
d.setdefault('mcpServers',{})['bnbot']={'command':'npx','args':['bnbot-mcp-server']}
with open('$MCP_FILE','w') as f: json.dump(d,f,indent=2); f.write('\n')
"
  else
    cat > "$MCP_FILE" << 'EOF'
{
  "mcpServers": {
    "bnbot": {
      "command": "npx",
      "args": ["bnbot-mcp-server"]
    }
  }
}
EOF
  fi
  ok ".mcp.json configured"
else
  ok ".mcp.json"
fi

# --- 5. Wallet status ---
WALLET_STATUS="needs_login"
if WOUT=$(npx awal@2.2.0 status 2>&1); then
  if echo "$WOUT" | grep -qi "address\|authenticated\|logged"; then
    WALLET_STATUS="ready"
  fi
fi

# --- Result ---
echo ""
if [[ "$WALLET_STATUS" == "ready" ]]; then
  echo "STATUS:READY"
else
  echo "STATUS:NEEDS_LOGIN"
fi
