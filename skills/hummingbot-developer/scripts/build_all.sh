#!/bin/bash
# build_all.sh — Build wheel and Docker images for all three repos.
#
# Build order:
#   1. hummingbot wheel (dist/*.whl)
#   2. hummingbot Docker image
#   3. gateway Docker image
#   4. hummingbot-api Docker image
#
# Usage:
#   bash scripts/build_all.sh                  # build everything
#   bash scripts/build_all.sh --wheel-only     # only build hummingbot wheel
#   bash scripts/build_all.sh --no-docker      # skip all Docker builds
#   bash scripts/build_all.sh --no-hbot        # skip hummingbot builds
#   bash scripts/build_all.sh --no-gateway     # skip gateway builds
#   bash scripts/build_all.sh --no-api         # skip hummingbot-api builds
#   bash scripts/build_all.sh --tag dev        # Docker image tag (default: dev)

set -e

# Augment PATH for non-interactive shells
for _p in "$HOME/anaconda3/bin" "$HOME/miniconda3/bin" "$HOME/miniforge3/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  [ -d "$_p" ] && export PATH="$_p:$PATH"
done

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
HBOT_DIR="$WORKSPACE/hummingbot"
GATEWAY_DIR="$WORKSPACE/hummingbot-gateway"
API_DIR="$WORKSPACE/hummingbot-api"

WHEEL_ONLY=false
NO_DOCKER=false
NO_HBOT=false
NO_GATEWAY=false
NO_API=false
TAG="dev"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wheel-only) WHEEL_ONLY=true; shift ;;
    --no-docker)  NO_DOCKER=true; shift ;;
    --no-hbot)    NO_HBOT=true; shift ;;
    --no-gateway) NO_GATEWAY=true; shift ;;
    --no-api)     NO_API=true; shift ;;
    --tag)        TAG="$2"; shift 2 ;;
    *) shift ;;
  esac
done

ok()     { echo "  ✓ $*"; }
fail()   { echo "  ✗ $*" >&2; }
warn()   { echo "  ! $*"; }
info()   { echo "  → $*"; }
header() { echo ""; echo "$*"; echo "$(echo "$*" | sed 's/./-/g')"; }
step()   { echo ""; echo "  [$*]"; }

# Load saved branch selections
[ -f "$WORKSPACE/.dev-branches" ] && source "$WORKSPACE/.dev-branches"
HBOT_BRANCH="${HBOT_BRANCH:-development}"
GATEWAY_BRANCH="${GATEWAY_BRANCH:-development}"
API_BRANCH="${API_BRANCH:-development}"

# ─── Check docker ─────────────────────────────────────────────────────────────

if [ "$NO_DOCKER" = false ] && [ "$WHEEL_ONLY" = false ]; then
  if ! command -v docker &>/dev/null || ! docker info &>/dev/null 2>&1; then
    warn "Docker not available — will build wheel only"
    NO_DOCKER=true
  fi
fi

# ─── Build 1: Hummingbot wheel ───────────────────────────────────────────────

if [ "$NO_HBOT" = false ]; then
  header "Build 1/3: Hummingbot"

  HBOT_COMMIT=$(git -C "$HBOT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")

  step "Building wheel (conda run)"
  cd "$HBOT_DIR"
  conda run -n hummingbot python setup.py bdist_wheel 2>&1 | grep -E "writing|copying|creating|error|Error" | tail -5

  WHEEL=$(ls "$HBOT_DIR/dist/"hummingbot-*.whl 2>/dev/null | head -1)
  if [ -n "$WHEEL" ]; then
    WHEEL_SIZE=$(du -sh "$WHEEL" | cut -f1)
    ok "Wheel: $(basename "$WHEEL") ($WHEEL_SIZE)"
  else
    fail "Wheel not found in dist/ — build may have failed"
    exit 1
  fi

  if [ "$NO_DOCKER" = false ] && [ "$WHEEL_ONLY" = false ]; then
    step "Building Docker image: hummingbot/hummingbot:$TAG"
    docker build \
      --build-arg BRANCH="$HBOT_BRANCH" \
      --build-arg COMMIT="$HBOT_COMMIT" \
      --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      -t "hummingbot/hummingbot:$TAG" \
      -f "$HBOT_DIR/Dockerfile" \
      "$HBOT_DIR" 2>&1 | tail -3
    ok "Docker image: hummingbot/hummingbot:$TAG"

    # Also tag as branch name for use with hummingbot-api
    docker tag "hummingbot/hummingbot:$TAG" "hummingbot/hummingbot:$HBOT_BRANCH"
    ok "Also tagged: hummingbot/hummingbot:$HBOT_BRANCH"
  fi
fi

# ─── Build 2: Gateway ────────────────────────────────────────────────────────

if [ "$NO_GATEWAY" = false ] && [ "$WHEEL_ONLY" = false ]; then
  header "Build 2/3: Gateway"

  GW_COMMIT=$(git -C "$GATEWAY_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")

  step "pnpm build (TypeScript → dist/)"
  cd "$GATEWAY_DIR"
  pnpm build 2>&1 | tail -3
  ok "TypeScript compiled: dist/index.js"

  if [ "$NO_DOCKER" = false ]; then
    step "Building Docker image: hummingbot/gateway:$TAG"
    docker build \
      --build-arg BRANCH="$GATEWAY_BRANCH" \
      --build-arg COMMIT="$GW_COMMIT" \
      --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      -t "hummingbot/gateway:$TAG" \
      -f "$GATEWAY_DIR/Dockerfile" \
      "$GATEWAY_DIR" 2>&1 | tail -3
    ok "Docker image: hummingbot/gateway:$TAG"

    docker tag "hummingbot/gateway:$TAG" "hummingbot/gateway:$GATEWAY_BRANCH"
    ok "Also tagged: hummingbot/gateway:$GATEWAY_BRANCH"
  fi
fi

# ─── Build 3: Hummingbot API ─────────────────────────────────────────────────

if [ "$NO_API" = false ] && [ "$NO_DOCKER" = false ] && [ "$WHEEL_ONLY" = false ]; then
  header "Build 3/3: Hummingbot API"

  API_COMMIT=$(git -C "$API_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")

  step "Building Docker image: hummingbot/hummingbot-api:$TAG"
  cd "$API_DIR"
  docker build \
    -t "hummingbot/hummingbot-api:$TAG" \
    -f "$API_DIR/Dockerfile" \
    "$API_DIR" 2>&1 | tail -3
  ok "Docker image: hummingbot/hummingbot-api:$TAG"

  docker tag "hummingbot/hummingbot-api:$TAG" "hummingbot/hummingbot-api:$API_BRANCH"
  ok "Also tagged: hummingbot/hummingbot-api:$API_BRANCH"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

header "Build Summary"

WHEEL=$(ls "$HBOT_DIR/dist/"hummingbot-*.whl 2>/dev/null | head -1)
GW_DIST="$GATEWAY_DIR/dist/index.js"

[ -n "$WHEEL" ]          && ok "hummingbot wheel:        $(basename "$WHEEL")" || warn "hummingbot wheel not built"
[ -f "$GW_DIST" ]        && ok "gateway dist:            dist/index.js" || warn "gateway dist not built"

if [ "$NO_DOCKER" = false ] && [ "$WHEEL_ONLY" = false ]; then
  docker image inspect "hummingbot/hummingbot:$TAG"    &>/dev/null && ok "hummingbot Docker:       hummingbot/hummingbot:$TAG" || warn "hummingbot Docker image not built"
  docker image inspect "hummingbot/gateway:$TAG"       &>/dev/null && ok "gateway Docker:          hummingbot/gateway:$TAG"   || warn "gateway Docker image not built"
  docker image inspect "hummingbot/hummingbot-api:$TAG" &>/dev/null && ok "hummingbot-api Docker:   hummingbot/hummingbot-api:$TAG" || warn "hummingbot-api Docker image not built"
fi

echo ""
echo "Next: bash scripts/verify_build.sh"
