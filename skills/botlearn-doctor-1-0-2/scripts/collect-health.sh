#!/bin/bash
# collect-health.sh — Probe OpenClaw Gateway status, output JSON
# Gateway default port: 18789 | Control UI: /openclaw | Hooks: /hooks
# Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"
TIMEOUT_SEC=5

# Read gateway config from openclaw.json (JSON5 — strip comments before parsing)
GATEWAY_CONFIG=$(node <<'NODESCRIPT'
const fs = require("fs");
const CONFIG = process.env.OPENCLAW_CONFIG_PATH || ((process.env.OPENCLAW_HOME || process.env.HOME + "/.openclaw") + "/openclaw.json");
try {
  const raw = fs.readFileSync(CONFIG, "utf8");
  const clean = raw.replace(/\/\/.*$/gm, "").replace(/\/\*[\s\S]*?\*\//g, "");
  const c = JSON.parse(clean);
  console.log(JSON.stringify({
    port: c.gateway?.port || 18789,
    bind: c.gateway?.bind || "loopback",
    mode: c.gateway?.mode || "ws+http",
    auth: c.gateway?.auth?.type || "none",
    reload: c.gateway?.reload || "hybrid",
    controlUI: c.gateway?.controlUI !== false
  }));
} catch {
  console.log(JSON.stringify({port:18789,bind:"loopback",mode:"ws+http",auth:"none",reload:"hybrid",controlUI:true}));
}
NODESCRIPT
)

GATEWAY_PORT=$(echo "$GATEWAY_CONFIG" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).port)" 2>/dev/null || echo 18789)
GATEWAY_URL="http://localhost:${GATEWAY_PORT}"

probe_endpoint() {
  local endpoint="$1"
  local url="${GATEWAY_URL}${endpoint}"

  local result
  result=$(curl -s -o /dev/null -w '%{http_code}\n%{time_total}' --connect-timeout "$TIMEOUT_SEC" --max-time "$TIMEOUT_SEC" "$url" 2>/dev/null || echo "000
0")

  local http_code
  http_code=$(echo "$result" | head -1)
  local latency_s
  latency_s=$(echo "$result" | tail -1)
  local latency_ms
  latency_ms=$(awk "BEGIN{printf \"%d\", $latency_s * 1000}")

  local status="unknown"
  case "$http_code" in
    200|204) status="healthy" ;;
    301|302|303|307|308) status="redirect" ;;
    401|403) status="auth_required" ;;
    404) status="not_found" ;;
    503) status="unavailable" ;;
    000) status="unreachable" ;;
    *)   status="error" ;;
  esac

  echo "{\"endpoint\":\"$endpoint\",\"status_code\":$http_code,\"status\":\"$status\",\"latency_ms\":$latency_ms}"
}

# Probe OpenClaw Gateway endpoints
# /         — Gateway root (connectivity check)
# /openclaw — Control UI (operational check)
# /hooks    — Hooks API (hooks system check)
root_probe=$(probe_endpoint "/")
control_ui=$(probe_endpoint "/openclaw")
hooks_api=$(probe_endpoint "/hooks")

# Determine gateway status
root_code=$(echo "$root_probe" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).status_code)" 2>/dev/null || echo 0)
control_code=$(echo "$control_ui" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).status_code)" 2>/dev/null || echo 0)

gateway_reachable="false"
gateway_operational="false"

# Reachable = root responds (any non-000 code)
[[ "$root_code" != "0" && "$root_code" != "000" ]] && gateway_reachable="true"
# Operational = control UI responds (200, or auth required 401/403 means gateway is running)
[[ "$control_code" == "200" || "$control_code" == "401" || "$control_code" == "403" ]] && gateway_operational="true"

# Check CLIs
clawhub_version="NOT_FOUND"
command -v clawhub &>/dev/null && clawhub_version=$(clawhub --version 2>/dev/null || echo "unknown")

openclaw_cli_version="NOT_FOUND"
command -v openclaw &>/dev/null && openclaw_cli_version=$(openclaw --version 2>/dev/null || echo "unknown")

cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "gateway_url": "$GATEWAY_URL",
  "gateway_port": $GATEWAY_PORT,
  "gateway_reachable": $gateway_reachable,
  "gateway_operational": $gateway_operational,
  "gateway_config": $GATEWAY_CONFIG,
  "clawhub_version": "$clawhub_version",
  "openclaw_cli_version": "$openclaw_cli_version",
  "endpoints": [
    $root_probe,
    $control_ui,
    $hooks_api
  ]
}
EOF
