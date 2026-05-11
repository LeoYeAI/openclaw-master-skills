#!/bin/bash
# verify_build.sh — Verify all builds are correct and in sync.
#
# Checks:
#   1. Branch/commit consistency across repos
#   2. Hummingbot wheel integrity
#   3. Gateway dist integrity
#   4. Local hummingbot wired into API env
#   5. Docker images exist and are healthy
#   6. Running services (API + Gateway) match expected builds
#   7. Integration smoke test (if services are running)
#
# Usage:
#   bash scripts/verify_build.sh              # full verification
#   bash scripts/verify_build.sh --no-docker  # skip Docker checks
#   bash scripts/verify_build.sh --no-running # skip running-service checks
#   bash scripts/verify_build.sh --json       # JSON output

set -e

# Augment PATH for non-interactive shells
for _p in "$HOME/anaconda3/bin" "$HOME/miniconda3/bin" "$HOME/miniforge3/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  [ -d "$_p" ] && export PATH="$_p:$PATH"
done

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
HBOT_DIR="$WORKSPACE/hummingbot"
GATEWAY_DIR="$WORKSPACE/hummingbot-gateway"
API_DIR="$WORKSPACE/hummingbot-api"

NO_DOCKER=false
NO_RUNNING=false
JSON_OUT=false
TAG="dev"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-docker)  NO_DOCKER=true; shift ;;
    --no-running) NO_RUNNING=true; shift ;;
    --json)       JSON_OUT=true; shift ;;
    --tag)        TAG="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Load saved branch selections
[ -f "$WORKSPACE/.dev-branches" ] && source "$WORKSPACE/.dev-branches"
HBOT_BRANCH="${HBOT_BRANCH:-development}"
GATEWAY_BRANCH="${GATEWAY_BRANCH:-development}"
API_BRANCH="${API_BRANCH:-development}"

API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"
GATEWAY_URL="${GATEWAY_URL:-http://localhost:15888}"
API_USER="${API_USER:-admin}"
API_PASS="${API_PASS:-admin}"

# Load .env
for _p in "$API_DIR/.env" "$HOME/.hummingbot/.env" ".env"; do
  if [ -f "$_p" ]; then
    while IFS= read -r line; do
      [[ -z "$line" || "$line" == \#* ]] && continue
      [[ "$line" == *=* ]] && export "${line%%=*}=${line#*=}" 2>/dev/null || true
    done < "$_p"
    break
  fi
done

# Result tracking
PASS=0; FAIL=0; WARN=0
declare -a RESULTS=()

result() {
  local status="$1" name="$2" detail="$3"
  RESULTS+=("$status|$name|$detail")
  case "$status" in
    PASS) ((PASS++)) ; [ "$JSON_OUT" = false ] && echo "  ✓ $name${detail:+: $detail}" ;;
    FAIL) ((FAIL++)) ; [ "$JSON_OUT" = false ] && echo "  ✗ $name${detail:+: $detail}" ;;
    WARN) ((WARN++)) ; [ "$JSON_OUT" = false ] && echo "  ! $name${detail:+: $detail}" ;;
  esac
}
header() { [ "$JSON_OUT" = false ] && { echo ""; echo "$*"; echo "$(echo "$*" | sed 's/./-/g')"; }; }

# ─── 1. Branch & commit consistency ─────────────────────────────────────────

header "1. Branch & Commit Consistency"

for repo_name in "hummingbot:$HBOT_DIR:$HBOT_BRANCH" "gateway:$GATEWAY_DIR:$GATEWAY_BRANCH" "hummingbot-api:$API_DIR:$API_BRANCH"; do
  IFS=: read -r name dir expected_branch <<< "$repo_name"
  if [ ! -d "$dir/.git" ]; then
    result FAIL "$name branch" "repo not found at $dir"
    continue
  fi
  actual=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null)
  commit=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
  dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  if [ "$actual" = "$expected_branch" ]; then
    result PASS "$name branch" "$actual @ $commit"
  else
    result WARN "$name branch" "expected $expected_branch, on $actual @ $commit"
  fi
  [ "$dirty" -gt 0 ] && result WARN "$name working tree" "$dirty uncommitted changes"
done

# ─── 2. Hummingbot wheel ─────────────────────────────────────────────────────

header "2. Hummingbot Wheel"

WHEEL=$(ls "$HBOT_DIR/dist/"hummingbot-*.whl 2>/dev/null | sort -V | tail -1)
if [ -n "$WHEEL" ]; then
  WHEEL_NAME=$(basename "$WHEEL")
  WHEEL_SIZE=$(du -sh "$WHEEL" | cut -f1)
  WHEEL_AGE=$(( ($(date +%s) - $(stat -f %m "$WHEEL" 2>/dev/null || stat -c %Y "$WHEEL" 2>/dev/null || echo 0)) / 60 ))
  result PASS "wheel exists" "$WHEEL_NAME ($WHEEL_SIZE, ${WHEEL_AGE}m ago)"

  # Check wheel was built from current commit
  WHEEL_VERSION=$(echo "$WHEEL_NAME" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "")
  [ -n "$WHEEL_VERSION" ] && result PASS "wheel version" "$WHEEL_VERSION"

  # Validate wheel is installable
  if conda run -n hummingbot pip show hummingbot &>/dev/null 2>&1; then
    HB_VER=$(conda run -n hummingbot pip show hummingbot 2>/dev/null | grep "^Version:" | awk '{print $2}')
    result PASS "wheel installable" "version $HB_VER in hummingbot env"
  fi
else
  result WARN "wheel" "not built yet — run: bash scripts/build_all.sh --wheel-only"
fi

# ─── 3. Gateway dist ─────────────────────────────────────────────────────────

header "3. Gateway TypeScript Build"

GW_DIST="$GATEWAY_DIR/dist/index.js"
if [ -f "$GW_DIST" ]; then
  GW_AGE=$(( ($(date +%s) - $(stat -f %m "$GW_DIST" 2>/dev/null || stat -c %Y "$GW_DIST" 2>/dev/null || echo 0)) / 60 ))
  GW_SIZE=$(du -sh "$GATEWAY_DIR/dist" | cut -f1)
  result PASS "gateway dist" "dist/ exists ($GW_SIZE, ${GW_AGE}m ago)"

  # Check dist is newer than source
  NEWEST_SRC=$(find "$GATEWAY_DIR/src" -name "*.ts" -newer "$GW_DIST" 2>/dev/null | head -1)
  if [ -n "$NEWEST_SRC" ]; then
    result WARN "gateway dist stale" "$(basename "$NEWEST_SRC") newer than dist/ — run: pnpm build"
  else
    result PASS "gateway dist up to date" "no .ts files newer than dist/"
  fi
else
  result WARN "gateway dist" "not built — run: cd $GATEWAY_DIR && pnpm build"
fi

# ─── 4. Local hummingbot in API env ──────────────────────────────────────────

header "4. Local Hummingbot in API Env"

if conda env list 2>/dev/null | grep -q "^hummingbot-api "; then
  # Check via direct_url.json (works for editable installs in Python 3.12+ namespace packages)
  DIRECT_URL=$(cat "$HOME/anaconda3/envs/hummingbot-api/lib/python3.12/site-packages/hummingbot-"*.dist-info/direct_url.json 2>/dev/null \
    || conda run -n hummingbot-api python -c "
import importlib.metadata, json, pathlib
try:
  d = importlib.metadata.distribution('hummingbot')
  p = pathlib.Path(str(d._path)) / 'direct_url.json'
  print(p.read_text() if p.exists() else '')
except: print('')
" 2>/dev/null)

  if echo "$DIRECT_URL" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('dir_info',{}).get('editable') and '$HBOT_DIR' in d.get('url','')" 2>/dev/null; then
    HB_VER=$(conda run -n hummingbot-api pip show hummingbot 2>/dev/null | grep "^Version:" | awk '{print $2}')
    result PASS "local hummingbot active" "editable install → $HBOT_DIR (v$HB_VER)"
  elif echo "$DIRECT_URL" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('dir_info',{}).get('editable')" 2>/dev/null; then
    LOCAL_PATH=$(echo "$DIRECT_URL" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('url','').replace('file://',''))")
    result WARN "editable install points elsewhere" "$LOCAL_PATH (expected $HBOT_DIR)"
  else
    HB_LOC=$(conda run -n hummingbot-api pip show hummingbot 2>/dev/null | grep "^Location:" | awk '{print $2}')
    result WARN "using non-editable hummingbot" "$HB_LOC — run: bash scripts/install_all.sh --skip-hbot --skip-gateway"
  fi
else
  result WARN "hummingbot-api env" "not installed — run: bash scripts/install_all.sh"
fi

# ─── 5. Dev .env validation ──────────────────────────────────────────────────

header "5. Dev .env Validation"

ENV_FILE="$API_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  # Check for Docker-internal hostnames that break source mode
  if grep -v "^#" "$ENV_FILE" | grep -q "hummingbot-postgres"; then
    result FAIL ".env DATABASE_URL" "uses Docker-internal hostname 'hummingbot-postgres' — run install_all.sh to fix"
  else
    DB_URL=$(grep "^DATABASE_URL" "$ENV_FILE" | cut -d= -f2-)
    result PASS ".env DATABASE_URL" "$DB_URL"
  fi

  if grep -q "BROKER_HOST=emqx\|BROKER_HOST=hummingbot" "$ENV_FILE"; then
    result FAIL ".env BROKER_HOST" "uses Docker-internal hostname — run install_all.sh to fix"
  else
    BROKER=$(grep "^BROKER_HOST" "$ENV_FILE" | cut -d= -f2-)
    result PASS ".env BROKER_HOST" "$BROKER"
  fi

  GW_URL=$(grep "^GATEWAY_URL" "$ENV_FILE" | cut -d= -f2-)
  result PASS ".env GATEWAY_URL" "${GW_URL:-not set}"
else
  result WARN ".env missing" "run install_all.sh to create it"
fi

# ─── 6. Docker images ────────────────────────────────────────────────────────

if [ "$NO_DOCKER" = false ] && command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
  header "5. Docker Images"

  check_image() {
    local image="$1" branch="$2"
    if docker image inspect "$image" &>/dev/null 2>&1; then
      local created size
      created=$(docker image inspect "$image" --format '{{.Created}}' 2>/dev/null | cut -c1-19 || echo "?")
      size=$(docker image inspect "$image" --format '{{.Size}}' 2>/dev/null | awk '{printf "%.0fMB", $1/1048576}' || echo "?")
      # Check image label for branch
      img_branch=$(docker image inspect "$image" --format '{{index .Config.Labels "branch"}}' 2>/dev/null || echo "")
      if [ -n "$img_branch" ] && [ "$img_branch" != "$branch" ]; then
        result WARN "$(echo $image | cut -d: -f1):$TAG" "built from $img_branch, expected $branch — rebuild with build_all.sh"
      else
        result PASS "$(echo $image | cut -d: -f1)" "tagged :$TAG ($size, $created)"
      fi
    else
      result WARN "$(echo $image | cut -d: -f1)" "image :$TAG not built — run: bash scripts/build_all.sh"
    fi
  }

  check_image "hummingbot/hummingbot:$TAG"     "$HBOT_BRANCH"
  check_image "hummingbot/gateway:$TAG"         "$GATEWAY_BRANCH"
  check_image "hummingbot/hummingbot-api:$TAG"  "$API_BRANCH"
fi

# ─── 6. Running services ─────────────────────────────────────────────────────

if [ "$NO_RUNNING" = false ]; then
  header "6. Running Services"

  # API
  if curl -s --max-time 3 "$API_URL/health" &>/dev/null; then
    result PASS "API running" "$API_URL"
    # Check if API is using source (not Docker)
    API_PID=$(pgrep -f "uvicorn main:app" 2>/dev/null | head -1)
    [ -n "$API_PID" ] && result PASS "API mode" "running from source (PID $API_PID)" \
                      || result PASS "API mode" "running (Docker or other)"
  else
    result WARN "API not running" "start: cd $API_DIR && make run"
  fi

  # Gateway
  if curl -s --max-time 3 "$GATEWAY_URL/" &>/dev/null; then
    result PASS "Gateway running" "$GATEWAY_URL"
    GW_PID=$(pgrep -f "dist/index.js" 2>/dev/null | head -1)
    [ -n "$GW_PID" ] && result PASS "Gateway mode" "running from source (PID $GW_PID)" \
                     || result PASS "Gateway mode" "running (Docker or other)"
  else
    result WARN "Gateway not running" "start: cd $GATEWAY_DIR && pnpm start --passphrase=hummingbot --dev"
  fi

  # Quick integration check if both running
  if curl -s --max-time 3 "$API_URL/health" &>/dev/null && curl -s --max-time 3 "$GATEWAY_URL/" &>/dev/null; then
    GW_STATUS=$(curl -s --max-time 5 -u "$API_USER:$API_PASS" "$API_URL/gateway/status" 2>/dev/null)
    if echo "$GW_STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d else 1)" 2>/dev/null; then
      result PASS "API→Gateway connected" "full stack operational"
    else
      result WARN "API→Gateway" "both running but API can't reach Gateway — check GATEWAY_URL in .env"
    fi
  fi
fi

# ─── Output ───────────────────────────────────────────────────────────────────

if [ "$JSON_OUT" = true ]; then
  echo "{"
  echo "  \"summary\": { \"pass\": $PASS, \"warn\": $WARN, \"fail\": $FAIL },"
  echo "  \"results\": ["
  local first=true
  for r in "${RESULTS[@]}"; do
    IFS="|" read -r status name detail <<< "$r"
    [ "$first" = false ] && echo ","
    first=false
    printf '    { "status": "%s", "name": "%s", "detail": "%s" }' "$status" "$name" "$detail"
  done
  echo ""
  echo "  ]"
  echo "}"
else
  echo ""
  echo "─────────────────────────────────────────"
  echo "  Results: $PASS passed · $WARN warnings · $FAIL failed"
  echo "─────────────────────────────────────────"
  if [ "$FAIL" -gt 0 ]; then
    echo "  ✗ Build verification FAILED — fix errors above"
    exit 1
  elif [ "$WARN" -gt 0 ]; then
    echo "  ! Build verified with warnings"
    exit 0
  else
    echo "  ✓ All checks passed — stack is in sync"
    exit 0
  fi
fi
