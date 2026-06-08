#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
# Mission Control — All-in-One Setup
#
# This script:
#   1. Checks prerequisites (Node.js, OpenClaw, npm)
#   2. Installs the dashboard app (backend + frontend)
#   3. Installs the lifecycle hook
#   4. Configures openclaw.json
#   5. Creates the backend .env file
#   6. Installs all npm dependencies
#   7. Tells you how to start everything
#
# Usage:
#   ./setup.sh                          # interactive
#   ./setup.sh --auto                   # auto with defaults
#   ./setup.sh --url http://host:8000 --secret mysecret --gateway-token abc
#   ./setup.sh --docker                 # use Docker instead of local Node
# ══════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
HOOKS_DIR="$OPENCLAW_DIR/hooks"
CONFIG_FILE="$OPENCLAW_DIR/openclaw.json"
INSTALL_DIR="$OPENCLAW_DIR/mission-control"

# Defaults
MC_PORT="8000"
MC_URL="http://localhost:$MC_PORT"
MC_SECRET=""
GW_URL="ws://127.0.0.1:18789"
GW_TOKEN=""
USE_DOCKER=false
AUTO_MODE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}   $1${NC}"; }
success() { echo -e "${GREEN}   ✅ $1${NC}"; }
warn()    { echo -e "${YELLOW}   ⚠️  $1${NC}"; }
error()   { echo -e "${RED}   ❌ $1${NC}"; }
header()  { echo -e "\n${BLUE}── $1 ──${NC}"; }

# ── Parse Arguments ──────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)           MC_URL="$2"; shift 2 ;;
    --port)          MC_PORT="$2"; MC_URL="http://localhost:$2"; shift 2 ;;
    --secret)        MC_SECRET="$2"; shift 2 ;;
    --gateway-url)   GW_URL="$2"; shift 2 ;;
    --gateway-token) GW_TOKEN="$2"; shift 2 ;;
    --docker)        USE_DOCKER=true; shift ;;
    --auto)          AUTO_MODE=true; shift ;;
    --install-dir)   INSTALL_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Mission Control — All-in-One Setup"
      echo ""
      echo "Usage: ./setup.sh [options]"
      echo ""
      echo "Options:"
      echo "  --auto              Use defaults, skip all prompts"
      echo "  --docker            Use Docker Compose instead of local Node"
      echo "  --port PORT         Backend port (default: 8000)"
      echo "  --url URL           Backend URL (default: http://localhost:8000)"
      echo "  --secret SECRET     Hook authentication secret"
      echo "  --gateway-url URL   OpenClaw Gateway WebSocket URL"
      echo "  --gateway-token TK  OpenClaw Gateway auth token"
      echo "  --install-dir DIR   Where to install (default: ~/.openclaw/mission-control)"
      echo "  --help              Show this help"
      exit 0
      ;;
    *) error "Unknown option: $1"; exit 1 ;;
  esac
done

# ══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}🎛️  Mission Control V1 — Setup${NC}"
echo "════════════════════════════════════════"
echo ""

# ── Step 1: Check Prerequisites ─────────────────────────
header "Step 1/7: Checking prerequisites"

# Check Node.js
if command -v node &>/dev/null; then
  NODE_VER=$(node --version | sed 's/v//')
  NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
  if [[ "$NODE_MAJOR" -ge 22 ]]; then
    success "Node.js $NODE_VER"
  else
    warn "Node.js $NODE_VER found, but v22+ recommended"
  fi
else
  if [[ "$USE_DOCKER" == true ]]; then
    info "Node.js not found, but --docker mode doesn't need it locally"
  else
    error "Node.js not found. Install it from https://nodejs.org"
    echo "     Or use --docker mode: ./setup.sh --docker"
    exit 1
  fi
fi

# Check npm
if command -v npm &>/dev/null; then
  success "npm $(npm --version)"
elif [[ "$USE_DOCKER" == false ]]; then
  error "npm not found. It comes with Node.js — reinstall from https://nodejs.org"
  exit 1
fi

# Check OpenClaw
if command -v openclaw &>/dev/null; then
  success "OpenClaw CLI found"
else
  warn "OpenClaw CLI not found. The hook won't auto-enable."
  warn "Install OpenClaw: curl -fsSL https://openclaw.ai/install.sh | bash"
fi

# Check Docker (if needed)
if [[ "$USE_DOCKER" == true ]]; then
  if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    success "Docker + Compose found"
  else
    error "Docker or Docker Compose not found. Install Docker from https://docker.com"
    exit 1
  fi
fi

# Check OpenClaw directory
if [[ -d "$OPENCLAW_DIR" ]]; then
  success "OpenClaw directory: $OPENCLAW_DIR"
else
  warn "$OPENCLAW_DIR not found — creating it"
  mkdir -p "$OPENCLAW_DIR"
fi

# ── Step 2: Gather Configuration ────────────────────────
header "Step 2/7: Configuration"

# Generate a random secret if needed
if [[ -z "$MC_SECRET" ]]; then
  MC_SECRET=$(openssl rand -hex 16 2>/dev/null || head -c 32 /dev/urandom | xxd -p 2>/dev/null | head -c 32 || echo "change-me-$(date +%s)")
fi

if [[ "$AUTO_MODE" == false ]]; then
  echo ""
  info "Press Enter to accept defaults shown in [brackets]."
  echo ""

  read -rp "   Backend port [$MC_PORT]: " input
  MC_PORT="${input:-$MC_PORT}"
  MC_URL="http://localhost:$MC_PORT"

  read -rp "   Hook secret [$MC_SECRET]: " input
  MC_SECRET="${input:-$MC_SECRET}"

  read -rp "   Gateway WebSocket URL [$GW_URL]: " input
  GW_URL="${input:-$GW_URL}"

  read -rp "   Gateway token (leave empty if none) [$GW_TOKEN]: " input
  GW_TOKEN="${input:-$GW_TOKEN}"

  read -rp "   Install directory [$INSTALL_DIR]: " input
  INSTALL_DIR="${input:-$INSTALL_DIR}"
fi

echo ""
info "Port:          $MC_PORT"
info "URL:           $MC_URL"
info "Secret:        $MC_SECRET"
info "Gateway:       $GW_URL"
info "Install dir:   $INSTALL_DIR"
echo ""

# ── Step 3: Install Dashboard App ───────────────────────
header "Step 3/7: Installing dashboard"

if [[ -d "$INSTALL_DIR" ]]; then
  warn "Directory already exists: $INSTALL_DIR"
  if [[ "$AUTO_MODE" == false ]]; then
    read -rp "   Overwrite? [y/N]: " confirm
    if [[ "$confirm" != [yY] ]]; then
      info "Keeping existing installation. Skipping file copy."
    else
      rm -rf "$INSTALL_DIR"
      cp -r "$SCRIPT_DIR/app" "$INSTALL_DIR"
      success "Dashboard installed to $INSTALL_DIR"
    fi
  else
    rm -rf "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR/app" "$INSTALL_DIR"
    success "Dashboard installed to $INSTALL_DIR"
  fi
else
  cp -r "$SCRIPT_DIR/app" "$INSTALL_DIR"
  success "Dashboard installed to $INSTALL_DIR"
fi

# Copy docs into install directory
mkdir -p "$INSTALL_DIR/docs"
if [[ -d "$SCRIPT_DIR/docs" ]]; then
  cp -r "$SCRIPT_DIR/docs/"* "$INSTALL_DIR/docs/" 2>/dev/null || true
fi
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

# Generate files that can't be stored in ClawHub (non-text)
cat > "$INSTALL_DIR/.gitignore" <<'GITIGNORE'
node_modules/
backend/data/
backend/.env
*.db
GITIGNORE

cat > "$INSTALL_DIR/Dockerfile" <<'DOCKERFILE'
FROM node:22-slim
WORKDIR /app
COPY package.json ./
COPY backend/package.json ./backend/
COPY frontend/package.json ./frontend/
RUN npm run install:all
COPY . .
RUN cd frontend && npm run build
EXPOSE 8000
CMD ["node", "backend/src/server.js"]
DOCKERFILE

mkdir -p "$INSTALL_DIR/frontend/public"
cat > "$INSTALL_DIR/frontend/public/favicon.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#6366f1"/><text x="16" y="22" text-anchor="middle" fill="#fff" font-family="Arial" font-weight="700" font-size="16">MC</text></svg>
SVG

success "Generated Dockerfile, .gitignore, and favicon"

# ── Step 4: Create .env File ────────────────────────────
header "Step 4/7: Creating configuration file"

ENV_FILE="$INSTALL_DIR/backend/.env"
cat > "$ENV_FILE" <<EOF
# ─── Mission Control Backend ───────────────────────────
PORT=$MC_PORT

# ─── OpenClaw Gateway ─────────────────────────────────
OPENCLAW_GATEWAY_URL=$GW_URL
OPENCLAW_GATEWAY_TOKEN=$GW_TOKEN

# ─── Authentication ───────────────────────────────────
AUTH_MODE=none
LOCAL_AUTH_TOKEN=

# ─── Hook Authentication ──────────────────────────────
HOOK_SECRET=$MC_SECRET

# ─── CORS ─────────────────────────────────────────────
CORS_ORIGIN=http://localhost:4173
EOF

success "Created $ENV_FILE"

# ── Step 5: Install Dependencies ────────────────────────
header "Step 5/7: Installing dependencies"

if [[ "$USE_DOCKER" == true ]]; then
  info "Docker mode — skipping npm install (Docker handles it)"
else
  cd "$INSTALL_DIR"
  info "Installing packages (this takes 1-3 minutes)..."
  npm run install:all 2>&1 | tail -3
  success "Dependencies installed"
fi

# ── Step 6: Install Lifecycle Hook ──────────────────────
header "Step 6/7: Installing lifecycle hook"

mkdir -p "$HOOKS_DIR"
cp "$SCRIPT_DIR/hook.ts" "$HOOKS_DIR/mission-control-hook.ts"
success "Hook copied to $HOOKS_DIR/mission-control-hook.ts"

# Try to enable via CLI
if command -v openclaw &>/dev/null; then
  if openclaw hooks enable mission-control 2>/dev/null; then
    success "Hook enabled via OpenClaw CLI"
  else
    warn "Could not auto-enable hook. Run manually: openclaw hooks enable mission-control"
  fi
else
  warn "OpenClaw CLI not available — enable the hook manually after installing OpenClaw"
fi

# ── Step 7: Update openclaw.json ────────────────────────
header "Step 7/7: Configuring OpenClaw"

if [[ -f "$CONFIG_FILE" ]]; then
  if grep -q "mission-control" "$CONFIG_FILE" 2>/dev/null; then
    warn "mission-control already exists in $CONFIG_FILE"
    info "Verify these values match:"
    info "  MISSION_CONTROL_URL: $MC_URL"
    info "  MISSION_CONTROL_HOOK_SECRET: $MC_SECRET"
  else
    warn "openclaw.json exists. Please add this to the hooks.internal.entries section:"
    echo ""
    echo '     "mission-control": {'
    echo '       "enabled": true,'
    echo '       "env": {'
    echo "         \"MISSION_CONTROL_URL\": \"$MC_URL\","
    echo "         \"MISSION_CONTROL_HOOK_SECRET\": \"$MC_SECRET\""
    echo '       }'
    echo '     }'
    echo ""
    info "See docs/GETTING-STARTED.md Step 8 for details."
  fi
else
  cat > "$CONFIG_FILE" <<EOF
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "mission-control": {
          "enabled": true,
          "env": {
            "MISSION_CONTROL_URL": "$MC_URL",
            "MISSION_CONTROL_HOOK_SECRET": "$MC_SECRET"
          }
        }
      }
    }
  }
}
EOF
  success "Created $CONFIG_FILE with hook configuration"
fi

# ── Done ─────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo -e "${GREEN}🎛️  Setup complete!${NC}"
echo "════════════════════════════════════════"
echo ""

if [[ "$USE_DOCKER" == true ]]; then
  echo "  Start Mission Control:"
  echo -e "    ${CYAN}cd $INSTALL_DIR && docker compose up -d${NC}"
else
  echo "  Start Mission Control:"
  echo -e "    ${CYAN}cd $INSTALL_DIR && npm run dev${NC}"
fi

echo ""
echo "  Then open in your browser:"
echo -e "    ${CYAN}http://localhost:4173${NC}"
echo ""
echo "  Restart your OpenClaw gateway to activate the hook:"
echo -e "    ${CYAN}openclaw gateway restart${NC}"
echo ""
echo "  Documentation:"
echo "    docs/GETTING-STARTED.md   — Step-by-step beginner guide"
echo "    docs/API-REFERENCE.md     — All API endpoints"
echo "    docs/HOOK-EVENTS.md       — Hook event reference"
echo "    docs/LIBRARY-GUIDE.md     — Using the document Library"
echo "    docs/TROUBLESHOOTING.md   — Common problems and fixes"
echo "    docs/DOCKER.md            — Docker deployment"
echo ""
