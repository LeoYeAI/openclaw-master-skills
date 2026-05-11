#!/bin/bash
# install_all.sh — Install all three Hummingbot repos in order.
#
# Order: hummingbot → gateway → hummingbot-api (wired to local hummingbot)
#
# Usage:
#   bash scripts/install_all.sh                 # uses branches from .dev-branches
#   bash scripts/install_all.sh --skip-hbot     # skip hummingbot conda install
#   bash scripts/install_all.sh --skip-gateway  # skip gateway pnpm install
#   bash scripts/install_all.sh --skip-api      # skip hummingbot-api install
#   bash scripts/install_all.sh --no-local-hbot # don't wire local hummingbot into API env

set -e

# Augment PATH for non-interactive shells
for _p in "$HOME/anaconda3/bin" "$HOME/miniconda3/bin" "$HOME/miniforge3/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  [ -d "$_p" ] && export PATH="$_p:$PATH"
done

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
HBOT_DIR="$WORKSPACE/hummingbot"
GATEWAY_DIR="$WORKSPACE/hummingbot-gateway"
API_DIR="$WORKSPACE/hummingbot-api"

SKIP_HBOT=false
SKIP_GATEWAY=false
SKIP_API=false
NO_LOCAL_HBOT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-hbot)     SKIP_HBOT=true; shift ;;
    --skip-gateway)  SKIP_GATEWAY=true; shift ;;
    --skip-api)      SKIP_API=true; shift ;;
    --no-local-hbot) NO_LOCAL_HBOT=true; shift ;;
    *) shift ;;
  esac
done

ok()     { echo "  ✓ $*"; }
fail()   { echo "  ✗ $*" >&2; }
warn()   { echo "  ! $*"; }
info()   { echo "  → $*"; }
header() { echo ""; echo "$*"; echo "$(echo "$*" | sed 's/./-/g')"; }
step()   { echo ""; echo "[$*]"; }

# Load saved branch selections if present
if [ -f "$WORKSPACE/.dev-branches" ]; then
  source "$WORKSPACE/.dev-branches"
  echo "Loaded branch config from .dev-branches:"
  echo "  hummingbot:     ${HBOT_BRANCH:-development}"
  echo "  gateway:        ${GATEWAY_BRANCH:-development}"
  echo "  hummingbot-api: ${API_BRANCH:-development}"
fi

# ─── Prereq check ────────────────────────────────────────────────────────────

header "Checking prerequisites"
PREREQS_OK=true

command -v conda   &>/dev/null && ok "conda" || { fail "conda not found"; PREREQS_OK=false; }
command -v node    &>/dev/null && ok "node $(node --version)" || { fail "node not found (brew install node@20)"; PREREQS_OK=false; }
command -v pnpm    &>/dev/null && ok "pnpm $(pnpm --version)" || { fail "pnpm not found (npm install -g pnpm)"; PREREQS_OK=false; }
command -v docker  &>/dev/null && ok "docker" || warn "docker not found (needed for build step)"
command -v git     &>/dev/null && ok "git" || { fail "git not found"; PREREQS_OK=false; }

[ "$PREREQS_OK" = false ] && { echo ""; fail "Fix missing prerequisites before continuing"; exit 1; }

# ─── Step 1: Hummingbot ──────────────────────────────────────────────────────

if [ "$SKIP_HBOT" = false ]; then
  header "Step 1/3: Installing Hummingbot"

  step "Fix solders (pip-only package, not on conda)"
  # macOS and Linux compatible
  if grep -q "solders" "$HBOT_DIR/setup/environment.yml" 2>/dev/null; then
    sed -i '' '/solders/d' "$HBOT_DIR/setup/environment.yml" 2>/dev/null \
      || sed -i '/solders/d' "$HBOT_DIR/setup/environment.yml"
    ok "Removed solders from environment.yml"
  else
    ok "solders already absent from environment.yml"
  fi

  step "conda env install (this takes 3-10 min on first run)"
  cd "$HBOT_DIR"
  make install
  ok "conda env 'hummingbot' ready"

  step "Install solders via pip"
  conda run -n hummingbot pip install "solders>=0.19.0" --quiet
  SOLDERS_VER=$(conda run -n hummingbot python -c "import solders; print(solders.__version__)" 2>/dev/null || echo "unknown")
  ok "solders $SOLDERS_VER installed"

  step "Verify hummingbot env"
  HBOT_PY=$(conda run -n hummingbot python -c "import hummingbot; print(hummingbot.__file__)" 2>/dev/null)
  if [[ "$HBOT_PY" == "$HBOT_DIR"* ]]; then
    ok "hummingbot source active at: $HBOT_PY"
  else
    warn "hummingbot path unexpected: $HBOT_PY"
  fi
else
  warn "Skipping hummingbot install (--skip-hbot)"
fi

# ─── Step 2: Gateway ─────────────────────────────────────────────────────────

if [ "$SKIP_GATEWAY" = false ]; then
  header "Step 2/3: Installing Gateway"
  cd "$GATEWAY_DIR"

  step "pnpm install"
  pnpm install 2>&1 | tail -5
  ok "node_modules installed"

  step "pnpm build (TypeScript → dist/)"
  pnpm build 2>&1 | tail -5
  ok "TypeScript compiled to dist/"

  step "Gateway setup (non-interactive defaults)"
  pnpm run setup:with-defaults 2>&1 | grep -E "✓|✗|Error|conf|cert" | head -10 || true
  ok "Gateway conf/ and certs/ configured"

  step "Verify build"
  if [ -f "$GATEWAY_DIR/dist/index.js" ]; then
    ok "dist/index.js exists"
  else
    fail "dist/index.js not found — pnpm build may have failed"
    exit 1
  fi
else
  warn "Skipping gateway install (--skip-gateway)"
fi

# ─── Step 3: Hummingbot API ──────────────────────────────────────────────────

if [ "$SKIP_API" = false ]; then
  header "Step 3/3: Installing Hummingbot API"
  cd "$API_DIR"

  step "conda env install"
  # Fix solders in API env too if present
  if grep -q "solders" "$API_DIR/environment.yml" 2>/dev/null; then
    sed -i '' '/solders/d' "$API_DIR/environment.yml" 2>/dev/null \
      || sed -i '/solders/d' "$API_DIR/environment.yml"
    ok "Removed solders from API environment.yml"
  fi

  if conda env list | grep -q "^hummingbot-api "; then
    info "hummingbot-api env exists — updating"
    conda env update -n hummingbot-api -f environment.yml --quiet
  else
    conda env create -f environment.yml --quiet
  fi
  ok "conda env 'hummingbot-api' ready"

  step "Write dev .env (localhost URLs — fixes Docker-internal hostnames)"
  # Always write the dev .env so DATABASE_URL and BROKER_HOST point to localhost.
  # The Docker-based setup writes internal hostnames (hummingbot-postgres, emqx)
  # which break when running the API from source outside of Docker.
  cat > "$API_DIR/.env" << EOF
USERNAME=admin
PASSWORD=admin
CONFIG_PASSWORD=admin
DEBUG_MODE=false
# MQTT broker — EMQX running in Docker, exposed on localhost:1883
BROKER_HOST=localhost
BROKER_PORT=1883
BROKER_USERNAME=admin
BROKER_PASSWORD=password
# Postgres — running in Docker, exposed on localhost:5432
# Note: Docker-based setup uses internal hostname 'hummingbot-postgres' — dev mode needs 'localhost'
DATABASE_URL=postgresql+asyncpg://hbot:hummingbot-api@localhost:5432/hummingbot_api
BOTS_PATH=$API_DIR/bots
# Gateway — running from source on localhost:15888
GATEWAY_URL=http://localhost:15888
EOF
  touch "$API_DIR/.setup-complete"
  ok "Dev .env written (postgres + EMQX + gateway all on localhost)"

  step "Install solders into API env"
  conda run -n hummingbot-api pip install "solders>=0.19.0" --quiet
  ok "solders installed in hummingbot-api env"

  if [ "$NO_LOCAL_HBOT" = false ]; then
    step "Wire local hummingbot source into API env (editable install)"
    conda run -n hummingbot-api pip install -e "$HBOT_DIR" --no-deps --quiet
    HBOT_IN_API=$(conda run -n hummingbot-api python -c "import hummingbot; print(hummingbot.__file__)" 2>/dev/null)
    if [[ "$HBOT_IN_API" == "$HBOT_DIR"* ]]; then
      ok "Local hummingbot active in hummingbot-api env"
      ok "Path: $HBOT_IN_API"
    else
      warn "Expected local path, got: $HBOT_IN_API"
    fi
  else
    warn "Using PyPI hummingbot in API env (--no-local-hbot)"
  fi
else
  warn "Skipping hummingbot-api install (--skip-api)"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

header "Install Summary"

HBOT_OK=false; GW_OK=false; API_OK=false

conda env list 2>/dev/null | grep -q "^hummingbot " && HBOT_OK=true
[ -f "$GATEWAY_DIR/dist/index.js" ] && GW_OK=true
conda env list 2>/dev/null | grep -q "^hummingbot-api " && API_OK=true

[ "$HBOT_OK" = true ] && ok "hummingbot    — conda env ready" || fail "hummingbot    — not installed"
[ "$GW_OK" = true ]   && ok "gateway       — built (dist/)" || fail "gateway       — not built"
[ "$API_OK" = true ]  && ok "hummingbot-api — conda env ready" || fail "hummingbot-api — not installed"

echo ""
echo "Next steps:"
echo "  Build images: bash scripts/build_all.sh"
echo "  Verify build: bash scripts/verify_build.sh"
echo "  Run stack:    bash scripts/run_dev_stack.sh"
