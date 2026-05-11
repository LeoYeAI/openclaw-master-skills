#!/bin/bash
# run_dev_stack.sh — Start the full Hummingbot dev stack from source.
#
# Starts (in order):
#   1. Docker infra (postgres + EMQX)
#   2. Gateway from source (background)
#   3. Hummingbot API from source (foreground, hot-reload)
#
# Usage:
#   bash scripts/run_dev_stack.sh              # start everything
#   bash scripts/run_dev_stack.sh --no-gateway # skip gateway
#   bash scripts/run_dev_stack.sh --stop       # stop everything
#   bash scripts/run_dev_stack.sh --status     # show running status

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
GATEWAY_DIR="$WORKSPACE/hummingbot-gateway"
API_DIR="$WORKSPACE/hummingbot-api"

PASSPHRASE="${GATEWAY_PASSPHRASE:-hummingbot}"
NO_GATEWAY=false
ACTION="start"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-gateway) NO_GATEWAY=true; shift ;;
    --stop)       ACTION="stop"; shift ;;
    --status)     ACTION="status"; shift ;;
    --passphrase) PASSPHRASE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

ok()     { echo "  ✓ $*"; }
fail()   { echo "  ✗ $*"; }
warn()   { echo "  ! $*"; }
info()   { echo "  → $*"; }
header() { echo ""; echo "$*"; echo "$(echo "$*" | sed 's/./-/g')"; }

PID_FILE="$WORKSPACE/.dev-pids"

# ─── Status ──────────────────────────────────────────────────────────────────

if [ "$ACTION" = "status" ]; then
  header "Dev Stack Status"
  docker compose -f "$API_DIR/docker-compose.yml" ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | grep -E "postgres|emqx|NAME" || echo "  (infra not running)"
  pgrep -f "dist/index.js" &>/dev/null && ok "Gateway running (PID $(pgrep -f dist/index.js))" || warn "Gateway not running"
  pgrep -f "uvicorn main:app" &>/dev/null && ok "API running (PID $(pgrep -f 'uvicorn main:app'))" || warn "API not running"
  curl -s --max-time 2 http://localhost:8000/health &>/dev/null && ok "API reachable at http://localhost:8000" || warn "API not reachable"
  curl -s --max-time 2 http://localhost:15888/ &>/dev/null && ok "Gateway reachable at http://localhost:15888" || warn "Gateway not reachable"
  exit 0
fi

# ─── Stop ────────────────────────────────────────────────────────────────────

if [ "$ACTION" = "stop" ]; then
  header "Stopping Dev Stack"
  pkill -f "dist/index.js" 2>/dev/null && ok "Gateway stopped" || warn "Gateway was not running"
  pkill -f "uvicorn main:app" 2>/dev/null && ok "API stopped" || warn "API was not running"
  cd "$API_DIR" && docker compose stop emqx postgres 2>/dev/null && ok "Infra stopped" || warn "Infra was not running"
  rm -f "$PID_FILE"
  exit 0
fi

# ─── Start ───────────────────────────────────────────────────────────────────

header "Starting Hummingbot Dev Stack"

# 1. Docker infra
header "Step 1: Start Docker infra (postgres + EMQX)"
cd "$API_DIR"
docker compose up emqx postgres -d 2>&1 | grep -E "Started|Running|Created|healthy" | head -5 || true
sleep 2

# Wait for postgres healthy
info "Waiting for postgres to be healthy..."
for i in {1..15}; do
  docker compose ps postgres 2>/dev/null | grep -q "healthy" && break
  sleep 2
done
docker compose ps 2>/dev/null | grep -E "postgres|emqx" | awk '{print "  " $1 " " $4}'
ok "Infra running"

# 2. Gateway
if [ "$NO_GATEWAY" = false ]; then
  header "Step 2: Start Gateway from source"
  if [ ! -f "$GATEWAY_DIR/dist/index.js" ]; then
    warn "Gateway not built — building now..."
    cd "$GATEWAY_DIR" && pnpm build 2>&1 | tail -3
  fi

  # Kill existing gateway
  pkill -f "dist/index.js" 2>/dev/null || true

  # Start in background, log to file
  GW_LOG="$WORKSPACE/.gateway.log"
  cd "$GATEWAY_DIR"
  nohup node dist/index.js --passphrase="$PASSPHRASE" --dev > "$GW_LOG" 2>&1 &
  GW_PID=$!
  echo $GW_PID >> "$PID_FILE"

  info "Gateway starting (PID $GW_PID) — waiting for port 15888..."
  for i in {1..20}; do
    curl -s --max-time 1 http://localhost:15888/ &>/dev/null && break
    sleep 1
  done

  if curl -s --max-time 2 http://localhost:15888/ &>/dev/null; then
    ok "Gateway running at http://localhost:15888 (PID $GW_PID)"
    ok "Logs: tail -f $GW_LOG"
  else
    warn "Gateway may still be starting — check: tail -f $GW_LOG"
  fi
fi

# 3. API
header "Step 3: Start Hummingbot API from source (hot-reload)"
echo ""
ok "Infra: running"
ok "Gateway: $(curl -s --max-time 1 http://localhost:15888/ &>/dev/null && echo 'running' || echo 'not running')"
echo ""
echo "  Starting API with uvicorn hot-reload..."
echo "  API will be available at http://localhost:8000"
echo "  Swagger UI: http://localhost:8000/docs"
echo "  Stop with: Ctrl+C"
echo ""
echo "  To stop everything later: bash scripts/run_dev_stack.sh --stop"
echo ""

cd "$API_DIR"
exec conda run --no-capture-output -n hummingbot-api uvicorn main:app --reload
