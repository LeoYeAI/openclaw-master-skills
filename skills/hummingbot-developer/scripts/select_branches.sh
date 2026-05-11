#!/bin/bash
# select_branches.sh — Interactively pick branches for each repo, then checkout.
#
# Usage:
#   bash scripts/select_branches.sh                      # interactive
#   bash scripts/select_branches.sh --defaults           # use development for all
#   bash scripts/select_branches.sh \
#     --hummingbot development \
#     --gateway core-2.7 \
#     --api development                                  # non-interactive
#   source scripts/select_branches.sh --export           # export branch vars to current shell
#
# Outputs (on success):
#   HBOT_BRANCH, GATEWAY_BRANCH, API_BRANCH env vars (if --export)
#   Writes .dev-branches to workspace dir

set -e

# Augment PATH for non-interactive shells
for _p in "$HOME/anaconda3/bin" "$HOME/miniconda3/bin" "$HOME/miniforge3/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  [ -d "$_p" ] && export PATH="$_p:$PATH"
done

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
HBOT_DIR="$WORKSPACE/hummingbot"
GATEWAY_DIR="$WORKSPACE/hummingbot-gateway"
API_DIR="$WORKSPACE/hummingbot-api"

HBOT_BRANCH=""
GATEWAY_BRANCH=""
API_BRANCH=""
USE_DEFAULTS=false
EXPORT=false
QUIET=false

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hummingbot) HBOT_BRANCH="$2"; shift 2 ;;
    --gateway)    GATEWAY_BRANCH="$2"; shift 2 ;;
    --api)        API_BRANCH="$2"; shift 2 ;;
    --defaults)   USE_DEFAULTS=true; shift ;;
    --export)     EXPORT=true; shift ;;
    --quiet)      QUIET=true; shift ;;
    *) shift ;;
  esac
done

ok()   { [ "$QUIET" = false ] && echo "  ✓ $*"; }
info() { [ "$QUIET" = false ] && echo "  → $*"; }
fail() { echo "  ✗ $*" >&2; }
header() { [ "$QUIET" = false ] && { echo ""; echo "$*"; echo "$(echo "$*" | sed 's/./-/g')"; }; }

# Verify repo exists
check_repo() {
  local dir="$1" name="$2"
  if [ ! -d "$dir/.git" ]; then
    fail "$name not found at $dir"
    echo "  Clone: gh repo clone hummingbot/$name $dir"
    exit 1
  fi
}

check_repo "$HBOT_DIR" hummingbot
check_repo "$GATEWAY_DIR" hummingbot-gateway
check_repo "$API_DIR" hummingbot-api

# Get available branches for a repo
list_branches() {
  local dir="$1"
  git -C "$dir" fetch --quiet origin 2>/dev/null || true
  git -C "$dir" branch -r 2>/dev/null | grep -v HEAD | sed 's|[[:space:]]*origin/||' | sort
}

# Interactive branch picker
pick_branch() {
  local name="$1" dir="$2" default="$3"
  local branches
  branches=$(list_branches "$dir")
  local current
  current=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null)

  echo ""
  echo "[$name] current branch: $current"
  echo "  Available branches:"
  echo "$branches" | nl -ba -w3 -s') ' | head -20
  local total
  total=$(echo "$branches" | wc -l | tr -d ' ')
  [ "$total" -gt 20 ] && echo "  ... and $((total - 20)) more (type branch name directly)"
  echo ""
  read -r -p "  Branch [$default]: " chosen
  chosen="${chosen:-$default}"

  # Validate
  if ! echo "$branches" | grep -qx "$chosen"; then
    echo "  Branch '$chosen' not found in remote — checking if local..."
    if ! git -C "$dir" rev-parse --verify "$chosen" &>/dev/null; then
      fail "Branch '$chosen' not found. Using default: $default"
      chosen="$default"
    fi
  fi
  echo "$chosen"
}

# Determine branches
if [ "$USE_DEFAULTS" = true ]; then
  HBOT_BRANCH="${HBOT_BRANCH:-development}"
  GATEWAY_BRANCH="${GATEWAY_BRANCH:-development}"
  API_BRANCH="${API_BRANCH:-development}"
elif [ -n "$HBOT_BRANCH" ] && [ -n "$GATEWAY_BRANCH" ] && [ -n "$API_BRANCH" ]; then
  : # all set via args
else
  [ "$QUIET" = false ] && echo "Select branches for each Hummingbot repo"
  [ "$QUIET" = false ] && echo "========================================"
  [ -z "$HBOT_BRANCH" ]    && HBOT_BRANCH=$(pick_branch "hummingbot" "$HBOT_DIR" "development")
  [ -z "$GATEWAY_BRANCH" ] && GATEWAY_BRANCH=$(pick_branch "gateway" "$GATEWAY_DIR" "development")
  [ -z "$API_BRANCH" ]     && API_BRANCH=$(pick_branch "hummingbot-api" "$API_DIR" "development")
fi

# Checkout branches
checkout_branch() {
  local dir="$1" branch="$2" name="$3"
  info "Checking out $name @ $branch..."
  git -C "$dir" fetch origin "$branch" --quiet 2>/dev/null || git -C "$dir" fetch --quiet 2>/dev/null || true
  git -C "$dir" checkout "$branch" 2>/dev/null || git -C "$dir" checkout -b "$branch" "origin/$branch"
  git -C "$dir" pull origin "$branch" --quiet 2>/dev/null || true
  local current
  current=$(git -C "$dir" rev-parse --short HEAD)
  ok "$name: $branch @ $current"
}

header "Checking out branches"
checkout_branch "$HBOT_DIR"    "$HBOT_BRANCH"    "hummingbot"
checkout_branch "$GATEWAY_DIR" "$GATEWAY_BRANCH" "gateway"
checkout_branch "$API_DIR"     "$API_BRANCH"     "hummingbot-api"

# Save to .dev-branches
cat > "$WORKSPACE/.dev-branches" << EOF
# Hummingbot dev branch selections
# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
HBOT_BRANCH=$HBOT_BRANCH
GATEWAY_BRANCH=$GATEWAY_BRANCH
API_BRANCH=$API_BRANCH
EOF

ok "Saved to $WORKSPACE/.dev-branches"

if [ "$EXPORT" = true ]; then
  export HBOT_BRANCH GATEWAY_BRANCH API_BRANCH
fi

[ "$QUIET" = false ] && echo ""
[ "$QUIET" = false ] && echo "✓ Branch selection complete"
[ "$QUIET" = false ] && echo "  hummingbot:    $HBOT_BRANCH"
[ "$QUIET" = false ] && echo "  gateway:       $GATEWAY_BRANCH"
[ "$QUIET" = false ] && echo "  hummingbot-api: $API_BRANCH"
[ "$QUIET" = false ] && echo ""
[ "$QUIET" = false ] && echo "Next: bash scripts/install_all.sh"
