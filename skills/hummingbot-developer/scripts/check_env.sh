#!/bin/bash
# check_env.sh — Verify dev prerequisites for Hummingbot development
# Usage: bash check_env.sh [--json]

JSON=false
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=true
done

ok()   { echo "  ✓ $*"; }
fail() { echo "  ✗ $*"; }
warn() { echo "  ! $*"; }

# Augment PATH with common install locations for non-interactive shells
for p in \
  "$HOME/anaconda3/bin" \
  "$HOME/miniconda3/bin" \
  "$HOME/miniforge3/bin" \
  "/opt/homebrew/bin" \
  "/usr/local/bin" \
  "/opt/homebrew/lib/node_modules/.bin"; do
  [ -d "$p" ] && export PATH="$p:$PATH"
done

check_cmd() {
  local name="$1"
  local cmd="$2"
  local version_flag="${3:---version}"
  if command -v "$cmd" &>/dev/null; then
    local ver
    ver=$("$cmd" $version_flag 2>&1 | head -1)
    echo "true:$ver"
  else
    echo "false:"
  fi
}

CONDA_OK=false; CONDA_VER=""
NODE_OK=false;  NODE_VER=""
PNPM_OK=false;  PNPM_VER=""
DOCKER_OK=false; DOCKER_VER=""
DOCKER_DAEMON=false
GIT_OK=false;   GIT_VER=""
PYTHON_OK=false; PYTHON_VER=""

result=$(check_cmd conda conda --version); CONDA_OK=${result%%:*}; CONDA_VER=${result#*:}
result=$(check_cmd node node --version);   NODE_OK=${result%%:*};  NODE_VER=${result#*:}
result=$(check_cmd pnpm pnpm --version);   PNPM_OK=${result%%:*};  PNPM_VER=${result#*:}
result=$(check_cmd git git --version);     GIT_OK=${result%%:*};   GIT_VER=${result#*:}
result=$(check_cmd docker docker --version); DOCKER_OK=${result%%:*}; DOCKER_VER=${result#*:}

# Check docker daemon
if [ "$DOCKER_OK" = "true" ] && docker info &>/dev/null 2>&1; then
  DOCKER_DAEMON=true
fi

# Check python (in conda base or system)
if command -v python3 &>/dev/null; then
  PYTHON_OK=true
  PYTHON_VER=$(python3 --version 2>&1)
fi

# Check node version >= 20
NODE_MAJOR=0
if [ "$NODE_OK" = "true" ]; then
  NODE_MAJOR=$(node --version 2>/dev/null | sed 's/v//' | cut -d. -f1)
fi

if [ "$JSON" = "true" ]; then
  echo "{"
  echo "  \"conda\": { \"ok\": $CONDA_OK, \"version\": \"$CONDA_VER\" },"
  echo "  \"node\": { \"ok\": $NODE_OK, \"version\": \"$NODE_VER\", \"major\": $NODE_MAJOR },"
  echo "  \"pnpm\": { \"ok\": $PNPM_OK, \"version\": \"$PNPM_VER\" },"
  echo "  \"docker\": { \"ok\": $DOCKER_OK, \"daemon\": $DOCKER_DAEMON, \"version\": \"$DOCKER_VER\" },"
  echo "  \"git\": { \"ok\": $GIT_OK, \"version\": \"$GIT_VER\" },"
  echo "  \"python\": { \"ok\": $PYTHON_OK, \"version\": \"$PYTHON_VER\" }"
  echo "}"
  exit 0
fi

echo "Environment Check"
echo "================="

[ "$CONDA_OK" = "true" ]  && ok "conda: $CONDA_VER"   || fail "conda not found — install Anaconda or Miniconda"
[ "$NODE_OK" = "true" ] && [ "$NODE_MAJOR" -ge 20 ] && ok "node: $NODE_VER" || {
  [ "$NODE_OK" = "true" ] && fail "node $NODE_VER — need v20+ (run: brew install node@20)" \
                           || fail "node not found — brew install node@20"
}
[ "$PNPM_OK" = "true" ]   && ok "pnpm: $PNPM_VER"     || fail "pnpm not found — npm install -g pnpm"
[ "$DOCKER_OK" = "true" ] && ok "docker: $DOCKER_VER"  || fail "docker not found — install Docker Desktop"
[ "$DOCKER_DAEMON" = "true" ] && ok "docker daemon running" || warn "docker daemon not running — open Docker Desktop"
[ "$GIT_OK" = "true" ]    && ok "git: $GIT_VER"        || fail "git not found"
[ "$PYTHON_OK" = "true" ] && ok "python: $PYTHON_VER"  || warn "python3 not found in PATH"

# Check conda envs
echo ""
echo "Conda Environments:"
if [ "$CONDA_OK" = "true" ]; then
  conda env list 2>/dev/null | grep -E "hummingbot|hummingbot-api" | while read -r line; do
    echo "  $line"
  done || echo "  (none found)"
fi

echo ""
ALL_OK=true
[ "$CONDA_OK" != "true" ] && ALL_OK=false
[ "$NODE_OK" != "true" ] && ALL_OK=false
[ "$NODE_MAJOR" -lt 20 ] && ALL_OK=false
[ "$PNPM_OK" != "true" ] && ALL_OK=false
[ "$DOCKER_OK" != "true" ] && ALL_OK=false

if [ "$ALL_OK" = "true" ]; then
  echo "✓ All prerequisites met"
  exit 0
else
  echo "✗ Some prerequisites missing — fix above errors before continuing"
  exit 1
fi
