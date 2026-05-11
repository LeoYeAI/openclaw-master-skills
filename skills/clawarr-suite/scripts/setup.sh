#!/usr/bin/env bash
# setup.sh - Interactive setup and connection diagnostics for ClawARR Suite
# Usage: setup.sh [host]
#
# Walks through discovery, API key retrieval, and connection testing.
# Outputs a ready-to-use config block at the end.
# Compatible with bash 3.2+ (macOS default).

set -euo pipefail

if ! command -v jq &> /dev/null; then
  echo "❌ jq is required. Install with: brew install jq (macOS) or apt install jq (Linux)"
  exit 1
fi

HOST="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║     ClawARR Suite — Setup Wizard     ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Step 1: Host
if [[ -z "$HOST" ]]; then
  echo "Step 1: Where is your media stack running?"
  echo ""
  echo "  Common options:"
  echo "    localhost       — same machine"
  echo "    192.168.x.x     — LAN IP of NAS/server"
  echo "    media.local     — mDNS hostname"
  echo ""
  read -rp "  Enter host IP or hostname: " HOST
  echo ""
fi

if [[ -z "$HOST" ]]; then
  echo "❌ No host provided. Exiting."
  exit 1
fi

# Step 2: Connectivity
echo "Step 1: Testing connectivity to $HOST..."
echo ""

REACHABLE=false
if ping -c 1 -W 2 "$HOST" &>/dev/null; then
  REACHABLE=true
elif curl -s --connect-timeout 3 -o /dev/null "http://${HOST}:8989/" 2>/dev/null || \
     curl -s --connect-timeout 3 -o /dev/null "http://${HOST}:7878/" 2>/dev/null || \
     curl -s --connect-timeout 3 -o /dev/null "http://${HOST}:32400/" 2>/dev/null; then
  REACHABLE=true
fi

if [[ "$REACHABLE" == true ]]; then
  echo "  ✅ Host $HOST is reachable"
else
  echo "  ❌ Cannot reach $HOST"
  echo ""
  echo "  Troubleshooting:"
  echo "    - Is the machine powered on?"
  echo "    - Are you on the same network/VLAN?"
  echo "    - Try the IP address instead of hostname"
  echo "    - Check firewall settings"
  exit 1
fi
echo ""

# Step 3: Service discovery
echo "Step 2: Scanning for services..."
echo ""

# Track found services and keys (bash 3.2 compatible — no associative arrays)
FOUND_APPS=""
SONARR_PORT="" RADARR_PORT="" LIDARR_PORT="" READARR_PORT="" PROWLARR_PORT=""
BAZARR_PORT="" OVERSEERR_PORT="" PLEX_PORT="" TAUTULLI_PORT="" SABNZBD_PORT=""
SONARR_KEY="" RADARR_KEY="" LIDARR_KEY="" READARR_KEY="" PROWLARR_KEY=""

set_port_var() {
  local name=$1 port=$2
  case "$name" in
    Sonarr) SONARR_PORT="$port" ;;
    Radarr) RADARR_PORT="$port" ;;
    Lidarr) LIDARR_PORT="$port" ;;
    Readarr) READARR_PORT="$port" ;;
    Prowlarr) PROWLARR_PORT="$port" ;;
    Bazarr) BAZARR_PORT="$port" ;;
    Overseerr) OVERSEERR_PORT="$port" ;;
    Plex) PLEX_PORT="$port" ;;
    Tautulli) TAUTULLI_PORT="$port" ;;
    SABnzbd) SABNZBD_PORT="$port" ;;
  esac
}

set_key_var() {
  local app=$1 key=$2
  case "$app" in
    Sonarr) SONARR_KEY="$key" ;;
    Radarr) RADARR_KEY="$key" ;;
    Lidarr) LIDARR_KEY="$key" ;;
    Readarr) READARR_KEY="$key" ;;
    Prowlarr) PROWLARR_KEY="$key" ;;
  esac
}

get_port_var() {
  local app=$1
  case "$app" in
    Sonarr) echo "$SONARR_PORT" ;;
    Radarr) echo "$RADARR_PORT" ;;
    Lidarr) echo "$LIDARR_PORT" ;;
    Readarr) echo "$READARR_PORT" ;;
    Prowlarr) echo "$PROWLARR_PORT" ;;
    *) echo "" ;;
  esac
}

check_service() {
  local name=$1 port=$2 path=$3
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://${HOST}:${port}${path}" 2>/dev/null || echo "000")

  if [[ "$http_code" =~ ^(200|301|302|303|400|401|403)$ ]]; then
    if [[ "$http_code" == "200" ]]; then
      echo "  ✅ $name — http://${HOST}:${port}"
    else
      echo "  ✅ $name — http://${HOST}:${port} (auth required)"
    fi
    FOUND_APPS="${FOUND_APPS} ${name}"
    # Store port in the app-specific variable (bash 3.2 compatible)
    set_port_var "$name" "$port"
    return 0
  else
    echo "  ·  $name — not found on port $port"
    return 1
  fi
}

check_service Sonarr   8989 "/api/v3/system/status" || true
check_service Radarr   7878 "/api/v3/system/status" || true
check_service Lidarr   8686 "/api/v1/system/status" || true
check_service Readarr  8787 "/api/v1/system/status" || true
check_service Prowlarr 9696 "/api/v1/system/status" || true
check_service Bazarr   6767 "/api/system/status"    || true
check_service Overseerr 5055 "/api/v1/status"       || true
check_service Plex     32400 "/identity"             || true
check_service Tautulli 8181 "/api/v2?cmd=get_tautulli_info" || true
check_service SABnzbd  8080 "/api?mode=version"     || true

FOUND_COUNT=$(echo "$FOUND_APPS" | wc -w | tr -d ' ')
echo ""

if [[ "$FOUND_COUNT" -eq 0 ]]; then
  echo "❌ No services detected on standard ports."
  echo ""
  echo "  Possible causes:"
  echo "    - Services aren't running (check Docker/systemd)"
  echo "    - Non-standard ports (check your docker-compose or app configs)"
  echo "    - Firewall blocking connections"
  exit 1
fi

echo "  Found $FOUND_COUNT service(s)"
echo ""

# Step 4: API key retrieval
echo "Step 3: Retrieving API keys..."
echo ""

get_api_key() {
  local app=$1 port=$2
  local key=""

  # Try /initialize.json first (v4+)
  local json_resp
  json_resp=$(curl -sf "http://${HOST}:${port}/initialize.json" 2>/dev/null || echo "")
  if [[ -n "$json_resp" ]]; then
    key=$(echo "$json_resp" | jq -r '.apiKey // empty' 2>/dev/null || echo "")
  fi

  # Fall back to /initialize.js (v3)
  if [[ -z "$key" ]]; then
    local js_resp
    js_resp=$(curl -sf "http://${HOST}:${port}/initialize.js" 2>/dev/null || echo "")
    if [[ -n "$js_resp" ]]; then
      key=$(echo "$js_resp" | grep -o "apiKey: '[^']*'" | cut -d"'" -f2 || echo "")
    fi
  fi

  if [[ -n "$key" ]]; then
    local masked="${key:0:4}...${key: -4}"
    echo "  ✅ $app API key: $masked"
    set_key_var "$app" "$key"
  else
    echo "  ⚠️  $app — couldn't auto-detect key"
    echo "     → Find it in $app: Settings → General → API Key"
  fi
}

for app in Sonarr Radarr Lidarr Readarr Prowlarr; do
  port=$(get_port_var "$app")
  if [[ -n "$port" ]]; then
    get_api_key "$app" "$port"
  fi
done

echo ""

# Step 5: Connection verification
echo "Step 4: Verifying API connections..."
echo ""

ALL_OK=true

verify_arr() {
  local app=$1 port=$2 key=$3 api_ver=${4:-v3}

  if [[ -z "$key" ]]; then return; fi

  local resp
  resp=$(curl -sf -H "X-Api-Key: $key" "http://${HOST}:${port}/api/${api_ver}/system/status" 2>/dev/null || echo "")

  if [[ -n "$resp" ]]; then
    local version
    version=$(echo "$resp" | jq -r '.version // "unknown"' 2>/dev/null)
    echo "  ✅ $app v${version} — connected"
  else
    echo "  ❌ $app — connection failed"
    ALL_OK=false
  fi
}

verify_arr Sonarr   "$SONARR_PORT"   "$SONARR_KEY"   v3
verify_arr Radarr   "$RADARR_PORT"   "$RADARR_KEY"   v3
verify_arr Lidarr   "$LIDARR_PORT"   "$LIDARR_KEY"   v1
verify_arr Readarr  "$READARR_PORT"  "$READARR_KEY"  v1
verify_arr Prowlarr "$PROWLARR_PORT" "$PROWLARR_KEY" v1

# Plex
if [[ -n "$PLEX_PORT" ]]; then
  plex_resp=$(curl -sf "http://${HOST}:${PLEX_PORT}/identity" 2>/dev/null || echo "")
  if [[ -n "$plex_resp" ]]; then
    echo "  ✅ Plex — reachable (use X-Plex-Token for full access)"
  fi
fi

# Overseerr
if [[ -n "$OVERSEERR_PORT" ]]; then
  os_resp=$(curl -sf "http://${HOST}:${OVERSEERR_PORT}/api/v1/status" 2>/dev/null || echo "")
  if [[ -n "$os_resp" ]]; then
    ver=$(echo "$os_resp" | jq -r '.version // "unknown"' 2>/dev/null)
    echo "  ✅ Overseerr v${ver} — connected"
  fi
fi

echo ""

# Step 6: Output config
echo "═══════════════════════════════════════"
echo "  Setup Complete!"
echo "═══════════════════════════════════════"
echo ""
echo "Export these to use ClawARR scripts:"
echo ""
echo "  export CLAWARR_HOST=$HOST"
[[ -n "$SONARR_KEY" ]]   && echo "  export SONARR_KEY=$SONARR_KEY"
[[ -n "$RADARR_KEY" ]]   && echo "  export RADARR_KEY=$RADARR_KEY"
[[ -n "$LIDARR_KEY" ]]   && echo "  export LIDARR_KEY=$LIDARR_KEY"
[[ -n "$READARR_KEY" ]]  && echo "  export READARR_KEY=$READARR_KEY"
[[ -n "$PROWLARR_KEY" ]] && echo "  export PROWLARR_KEY=$PROWLARR_KEY"

echo ""
echo "Quick test:"
echo "  scripts/status.sh"
echo "  scripts/queue.sh"
echo "  scripts/search.sh \"Breaking Bad\" series"
echo ""

if [[ "$ALL_OK" == true ]]; then
  echo "✅ All connections verified. You're good to go!"
else
  echo "⚠️  Some connections need attention. Check warnings above."
  echo ""
  echo "Common fixes:"
  echo "  - API key wrong? Check Settings → General → API Key in the app's web UI"
  echo "  - Port wrong? Check your docker-compose.yml or app config"
  echo "  - Firewall? Ensure ports are open on the host"
  echo "  - Reverse proxy? Try the direct IP:port instead of a domain"
fi
