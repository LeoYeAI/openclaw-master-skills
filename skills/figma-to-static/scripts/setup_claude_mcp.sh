#!/usr/bin/env bash
set -euo pipefail

# One-click bootstrap for Claude CLI + Figma MCP
# Safe default: DO NOT auto-start Claude login unless --start-login is passed.
# Usage:
#   bash scripts/setup_claude_mcp.sh
#   bash scripts/setup_claude_mcp.sh --start-login

START_LOGIN=0
for arg in "$@"; do
  case "$arg" in
    --start-login) START_LOGIN=1 ;;
    *)
      echo "[ERROR] Unknown argument: $arg"
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCK_PY="$SCRIPT_DIR/claude_auth_lock.py"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[ERROR] Missing required command: $1"
    exit 1
  fi
}

is_claude_logged_in() {
  claude auth status 2>/dev/null | grep -q '"loggedIn": true'
}

check_claude_quota() {
  local out
  out="$(claude --print "quota-check" 2>&1 || true)"

  if echo "$out" | grep -Eqi "requires user approval|run it directly in your terminal"; then
    echo "[INFO] Skipping automatic Claude quota probe (approval-gated in this environment)."
    echo "       If MCP flow stalls, manually run: claude --print \"quota-check\""
    return 0
  fi

  if echo "$out" | grep -Eqi "(you'?ve hit your limit|usage limit|resets .* UTC|rate limit)"; then
    echo "[WARN] Claude usage limit appears exhausted."
    echo ""
    echo "You're likely blocked by Claude model quota, not MCP setup itself."
    echo "Options:"
    echo "  1) Wait for reset time shown in Claude output"
    echo "  2) Enable extra usage / switch Claude account"
    echo "  3) Continue this skill via REST fallback (FIGMA_TOKEN) + skeleton-first flow"
    echo ""
    echo "Detected output snippet:"
    echo "$out" | head -n 20
    return 1
  fi
  return 0
}

need_cmd node
need_cmd npm
need_cmd python3

if ! command -v claude >/dev/null 2>&1; then
  echo "[1/7] Installing Claude CLI..."
  npm install -g @anthropic-ai/claude-code
else
  echo "[1/7] Claude CLI already installed: $(claude --version | head -n1)"
fi

echo "[2/7] Preflight auth-session check..."
if ! python3 "$SCRIPT_DIR/auth_session_guard.py" --mode claude-login; then
  echo ""
  echo "Refusing to continue: existing Claude session/lock detected."
  echo "Reuse the current session or clear the lock first:"
  echo "  python3 scripts/claude_auth_lock.py status"
  echo "  python3 scripts/claude_auth_lock.py clear"
  exit 2
fi

echo "[3/7] Checking Claude login status..."
if is_claude_logged_in; then
  echo "      Already logged in ✅"
  python3 "$LOCK_PY" clear >/dev/null 2>&1 || true
else
  echo "      Not logged in."
  echo "      IMPORTANT: keep only one active login session."
  echo ""
  echo "Safe default: this script will NOT auto-start a fresh login unless you pass --start-login."
  echo ""
  if [ "$START_LOGIN" -ne 1 ]; then
    echo "LOGIN_REQUIRED_EXPLICIT_START"
    echo "Next action:"
    echo "  1) Start exactly one login flow manually"
    echo "  2) Extract the authorize URL exactly"
    echo "  3) Acquire the auth lock before asking user for code"
    echo ""
    echo "Recommended remote/chat flow:"
    echo "  - Start one Claude session only"
    echo "  - Prefer 'claude' -> '/login' or one controlled 'claude auth login' session"
    echo "  - Save lock with current state:"
    echo "    python3 scripts/claude_auth_lock.py acquire --session-id <session-id> --auth-url \"<authorize-url>\""
    echo "  - Validate returned code before submission:"
    echo "    python3 scripts/claude_auth_lock.py verify-code --code-state \"<code#state>\""
    exit 2
  fi

  echo "      Starting a single explicit Claude login flow..."
  if ! claude auth login; then
    echo "[WARN] 'claude auth login' did not complete."
    echo "Keep only one live Claude session, lock its authorize URL, and retry."
    exit 2
  fi

  if ! is_claude_logged_in; then
    echo "[ERROR] Claude auth still not logged in."
    echo "Do not start a second flow. Reuse the current session or clear stale state first."
    exit 2
  fi
fi

echo "[4/7] Checking Claude usage quota..."
if ! check_claude_quota; then
  exit 4
fi

echo "[5/7] Ensuring Figma MCP server exists..."
if claude mcp list 2>/dev/null | grep -q '^figma:'; then
  echo "      Figma MCP already added ✅"
else
  claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp
fi

echo "[6/7] Checking Figma MCP auth state..."
mcp_status="$(claude mcp list 2>/dev/null || true)"
if echo "$mcp_status" | grep -q '^figma:.*Connected'; then
  echo "      Figma MCP already connected ✅"
elif echo "$mcp_status" | grep -q '^figma:.*Needs authentication'; then
  echo "[WARN] Figma MCP server exists but needs authentication."
  echo ""
  echo "Do this once in a single Claude interactive session:"
  echo "  1) Run: claude"
  echo "  2) Run command: /mcp"
  echo "  3) Select server: figma"
  echo "  4) Choose Authenticate/Connect and complete Figma browser consent"
  echo "  5) If browser redirects to localhost and fails, validate against lock/state first"
  echo "     python3 scripts/claude_auth_lock.py verify-callback --callback-url \"<callback-url>\""
  echo "  6) Keep that SAME Claude session alive until it says Connected"
  echo "  7) Exit Claude, then rerun this script"
  echo ""
  echo "Do NOT start another auth flow while Claude is already waiting for the redirect/code."
  exit 3
else
  echo "[WARN] Unable to confirm Figma MCP connection state from:"
  echo "$mcp_status"
  echo "Open Claude UI (/mcp) once to confirm figma server status, then rerun."
  exit 3
fi

echo "[7/7] Final status"
claude auth status || true
echo "---"
claude mcp list || true

echo ""
echo "✅ Bootstrap done. Next check:"
echo "python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --action tools"
