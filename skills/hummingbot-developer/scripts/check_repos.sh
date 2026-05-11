#!/bin/bash
# check_repos.sh — Show branch + build status for Hummingbot dev repos
# Usage: bash check_repos.sh [--json]

JSON=false
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=true
done

# Augment PATH for non-interactive shells
for _p in "$HOME/anaconda3/bin" "$HOME/miniconda3/bin" "$HOME/miniforge3/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  [ -d "$_p" ] && export PATH="$_p:$PATH"
done

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
# Resolve repo paths (env override or workspace defaults)
HUMMINGBOT_DIR="${HUMMINGBOT_DIR:-$WORKSPACE/hummingbot}"
GATEWAY_DIR="${GATEWAY_DIR:-$WORKSPACE/hummingbot-gateway}"
HUMMINGBOT_API_DIR="${HUMMINGBOT_API_DIR:-$WORKSPACE/hummingbot-api}"

ok()   { echo "  ✓ $*"; }
fail() { echo "  ✗ $*"; }
warn() { echo "  ! $*"; }

repo_info() {
  local dir="$1"
  if [ ! -d "$dir/.git" ]; then
    echo "missing:::"
    return
  fi
  local branch commit dirty
  branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  commit=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
  dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  echo "$branch:$commit:$dirty"
}

# Hummingbot
HB_INFO=$(repo_info "$HUMMINGBOT_DIR")
HB_BRANCH=${HB_INFO%%:*}; HB_REST=${HB_INFO#*:}
HB_COMMIT=${HB_REST%%:*}; HB_DIRTY=${HB_REST#*:}
HB_ENV=$(conda env list 2>/dev/null | grep "^hummingbot " | head -1 | awk '{print $1}')
HB_BUILT="false"
[ -f "$HUMMINGBOT_DIR/hummingbot/core/utils/async_utils.cpython"*.so 2>/dev/null ] && HB_BUILT="true"
[ -d "$HUMMINGBOT_DIR/dist" ] && ls "$HUMMINGBOT_DIR/dist/"*.whl &>/dev/null && HB_WHEEL="true" || HB_WHEEL="false"
# Check if local hummingbot is active in hummingbot-api env
HB_LOCAL_IN_API="false"
if conda env list 2>/dev/null | grep -q "^hummingbot-api "; then
  _DU=$(find "$HOME/anaconda3/envs/hummingbot-api/lib" -name "direct_url.json" -path "*/hummingbot-*" 2>/dev/null | head -1)
  if [ -n "$_DU" ]; then
    _URL=$(python3 -c "import json; d=json.load(open('$_DU')); print(d.get('url',''))" 2>/dev/null)
    _EDIT=$(python3 -c "import json; d=json.load(open('$_DU')); print(d.get('dir_info',{}).get('editable',False))" 2>/dev/null)
    [[ "$_EDIT" == "True" && "$_URL" == *"$HUMMINGBOT_DIR"* ]] && HB_LOCAL_IN_API="true"
  fi
fi

# Gateway
GW_INFO=$(repo_info "$GATEWAY_DIR")
GW_BRANCH=${GW_INFO%%:*}; GW_REST=${GW_INFO#*:}
GW_COMMIT=${GW_REST%%:*}; GW_DIRTY=${GW_REST#*:}
GW_BUILT="false"
[ -d "$GATEWAY_DIR/dist" ] && ls "$GATEWAY_DIR/dist/"*.js &>/dev/null && GW_BUILT="true"

# Hummingbot API
API_INFO=$(repo_info "$HUMMINGBOT_API_DIR")
API_BRANCH=${API_INFO%%:*}; API_REST=${API_INFO#*:}
API_COMMIT=${API_REST%%:*}; API_DIRTY=${API_REST#*:}
API_ENV=$(conda env list 2>/dev/null | grep "^hummingbot-api " | head -1 | awk '{print $1}')

if [ "$JSON" = "true" ]; then
  echo "{"
  echo "  \"hummingbot\": {"
  echo "    \"dir\": \"$HUMMINGBOT_DIR\","
  echo "    \"exists\": $([ -d "$HUMMINGBOT_DIR/.git" ] && echo true || echo false),"
  echo "    \"branch\": \"$HB_BRANCH\","
  echo "    \"commit\": \"$HB_COMMIT\","
  echo "    \"dirty_files\": $HB_DIRTY,"
  echo "    \"conda_env\": \"$HB_ENV\","
  echo "    \"wheel_built\": $HB_WHEEL,"
  echo "    \"local_in_api\": $HB_LOCAL_IN_API"
  echo "  },"
  echo "  \"gateway\": {"
  echo "    \"dir\": \"$GATEWAY_DIR\","
  echo "    \"exists\": $([ -d "$GATEWAY_DIR/.git" ] && echo true || echo false),"
  echo "    \"branch\": \"$GW_BRANCH\","
  echo "    \"commit\": \"$GW_COMMIT\","
  echo "    \"dirty_files\": $GW_DIRTY,"
  echo "    \"built\": $GW_BUILT"
  echo "  },"
  echo "  \"hummingbot_api\": {"
  echo "    \"dir\": \"$HUMMINGBOT_API_DIR\","
  echo "    \"exists\": $([ -d "$HUMMINGBOT_API_DIR/.git" ] && echo true || echo false),"
  echo "    \"branch\": \"$API_BRANCH\","
  echo "    \"commit\": \"$API_COMMIT\","
  echo "    \"dirty_files\": $API_DIRTY,"
  echo "    \"conda_env\": \"$API_ENV\""
  echo "  }"
  echo "}"
  exit 0
fi

echo "Repo Status"
echo "==========="
echo ""

echo "Hummingbot ($HUMMINGBOT_DIR):"
if [ -d "$HUMMINGBOT_DIR/.git" ]; then
  ok "branch: $HB_BRANCH @ $HB_COMMIT"
  [ "$HB_DIRTY" -gt 0 ] && warn "$HB_DIRTY uncommitted changes" || ok "working tree clean"
  [ -n "$HB_ENV" ]       && ok "conda env: hummingbot" || fail "conda env not installed (run setup-hummingbot)"
  [ "$HB_WHEEL" = "true" ] && ok "wheel built in dist/" || warn "no wheel built yet"
  [ "$HB_LOCAL_IN_API" = "true" ] && ok "local source active in hummingbot-api env" || warn "hummingbot-api using PyPI version (run setup-api-dev)"
else
  fail "not found at $HUMMINGBOT_DIR"
  echo "     Clone: git clone https://github.com/hummingbot/hummingbot.git $HUMMINGBOT_DIR"
fi

echo ""
echo "Gateway ($GATEWAY_DIR):"
if [ -d "$GATEWAY_DIR/.git" ]; then
  ok "branch: $GW_BRANCH @ $GW_COMMIT"
  [ "$GW_DIRTY" -gt 0 ] && warn "$GW_DIRTY uncommitted changes" || ok "working tree clean"
  [ "$GW_BUILT" = "true" ] && ok "TypeScript compiled (dist/ exists)" || warn "not built yet (run: pnpm build)"
else
  fail "not found at $GATEWAY_DIR"
fi

echo ""
echo "Hummingbot API ($HUMMINGBOT_API_DIR):"
if [ -d "$HUMMINGBOT_API_DIR/.git" ]; then
  ok "branch: $API_BRANCH @ $API_COMMIT"
  [ "$API_DIRTY" -gt 0 ] && warn "$API_DIRTY uncommitted changes" || ok "working tree clean"
  [ -n "$API_ENV" ]        && ok "conda env: hummingbot-api" || warn "conda env not installed (run setup-api-dev)"
else
  fail "not found at $HUMMINGBOT_API_DIR"
fi
