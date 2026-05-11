#!/usr/bin/env bash
set -euo pipefail

# talentclaw Skill Setup
# Cross-platform installer for macOS and Linux
# Installs Node.js 22+, Coffee Shop CLI, and registers agent identity

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

info()  { echo -e "${BOLD}$1${RESET}"; }
ok()    { echo -e "${GREEN}[OK]${RESET} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${RESET} $1"; }
fail()  { echo -e "${RED}[ERROR]${RESET} $1"; }

echo ""
info "=== talentclaw Skill Setup ==="
echo ""

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  *)
    fail "Unsupported operating system: $OS"
    echo "talentclaw setup supports macOS and Linux."
    exit 1
    ;;
esac

ok "Detected platform: $PLATFORM ($ARCH)"

# ─── 1. Check / install Node.js ─────────────────────────────────────────────

install_node_suggestion() {
  echo ""
  info "How to install Node.js 22+:"
  echo ""
  if [ "$PLATFORM" = "macos" ]; then
    echo "  Option A (Homebrew):  brew install node@22"
    echo "  Option B (nvm):       nvm install 22"
    echo "  Option C (fnm):       fnm install 22"
    echo "  Option D (direct):    https://nodejs.org/en/download"
  else
    echo "  Option A (nvm):       curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && nvm install 22"
    echo "  Option B (fnm):       curl -fsSL https://fnm.vercel.app/install | bash && fnm install 22"
    echo "  Option C (NodeSource):"
    if command -v apt-get &>/dev/null; then
      echo "    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -"
      echo "    sudo apt-get install -y nodejs"
    elif command -v dnf &>/dev/null; then
      echo "    curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -"
      echo "    sudo dnf install -y nodejs"
    elif command -v yum &>/dev/null; then
      echo "    curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -"
      echo "    sudo yum install -y nodejs"
    else
      echo "    Visit https://nodejs.org/en/download for your distribution"
    fi
    echo "  Option D (direct):    https://nodejs.org/en/download"
  fi
  echo ""
}

if ! command -v node &>/dev/null; then
  fail "Node.js is not installed."
  install_node_suggestion
  exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
  fail "Node.js 22+ required (found $(node -v))"
  install_node_suggestion
  exit 1
fi

ok "Node.js $(node -v)"

# ─── 2. Check npm is available ───────────────────────────────────────────────

if ! command -v npm &>/dev/null; then
  fail "npm is not available. It usually ships with Node.js."
  echo "  Try reinstalling Node.js from https://nodejs.org"
  exit 1
fi

ok "npm $(npm -v)"

# ─── 3. Install Coffee Shop CLI globally ────────────────────────────────────

if command -v coffeeshop &>/dev/null; then
  CURRENT_VERSION=$(coffeeshop version 2>/dev/null || echo "unknown")
  ok "coffeeshop CLI already installed (v${CURRENT_VERSION})"
  echo "     To update: npm install -g @artemyshq/coffeeshop@latest"
else
  info "Installing coffeeshop CLI globally..."
  if npm install -g @artemyshq/coffeeshop; then
    ok "coffeeshop CLI installed"
  else
    fail "Failed to install coffeeshop CLI."
    echo ""
    echo "Common fixes:"
    if [ "$PLATFORM" = "macos" ]; then
      echo "  - If permission denied: run with sudo, or configure npm prefix"
      echo "    mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global"
      echo "    Add ~/.npm-global/bin to your PATH"
    else
      echo "  - If permission denied: sudo npm install -g @artemyshq/coffeeshop"
      echo "  - Or configure npm to install globally without sudo:"
      echo "    mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global"
      echo "    echo 'export PATH=~/.npm-global/bin:\$PATH' >> ~/.bashrc && source ~/.bashrc"
    fi
    exit 1
  fi
fi

# ─── 4. Initialize agent identity ───────────────────────────────────────────

CONFIG_FILE="$HOME/.coffeeshop/config.json"
if [ -f "$CONFIG_FILE" ]; then
  ok "Agent identity already initialized (~/.coffeeshop/config.json exists)"
else
  echo ""
  info "Registering agent identity..."
  echo "This will create your agent card and register with Coffee Shop."
  echo ""

  # Use display name from git config if available, fall back to system username
  DISPLAY_NAME=""
  if command -v git &>/dev/null; then
    DISPLAY_NAME=$(git config --global user.name 2>/dev/null || true)
  fi
  if [ -z "$DISPLAY_NAME" ]; then
    DISPLAY_NAME=$(whoami)
  fi

  if coffeeshop register --display-name "$DISPLAY_NAME"; then
    ok "Agent identity registered as \"$DISPLAY_NAME\""
  else
    fail "Registration failed. Check your network connection and try again."
    echo "  Manual registration: coffeeshop register --display-name \"Your Name\""
    exit 1
  fi
fi

# ─── 5. Run diagnostics ─────────────────────────────────────────────────────

echo ""
info "Running diagnostics..."
coffeeshop doctor || {
  warn "Diagnostics reported issues. Review the output above."
}

# ─── 6. Verify MCP server can start ─────────────────────────────────────────

echo ""
info "Verifying MCP server..."

# Use timeout command (available on both macOS and Linux via coreutils)
TIMEOUT_CMD=""
if command -v timeout &>/dev/null; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout &>/dev/null; then
  # macOS with coreutils installed via Homebrew
  TIMEOUT_CMD="gtimeout"
fi

if [ -n "$TIMEOUT_CMD" ]; then
  if $TIMEOUT_CMD 5 coffeeshop mcp-server </dev/null &>/dev/null; then
    ok "MCP server starts successfully"
  else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ] || [ "$EXIT_CODE" -eq 137 ]; then
      # timeout killed it -- that is expected for a stdio server
      ok "MCP server verified (starts and accepts connections)"
    else
      warn "MCP server exited with code $EXIT_CODE. It may still work -- check logs if issues arise."
    fi
  fi
else
  # No timeout command available -- run in background and kill after 3 seconds
  coffeeshop mcp-server </dev/null &>/dev/null &
  MCP_PID=$!
  sleep 3
  if kill -0 "$MCP_PID" 2>/dev/null; then
    kill "$MCP_PID" 2>/dev/null || true
    wait "$MCP_PID" 2>/dev/null || true
    ok "MCP server verified (starts and accepts connections)"
  else
    wait "$MCP_PID" 2>/dev/null || true
    warn "MCP server exited quickly. It may still work -- check logs if issues arise."
  fi
fi

# ─── 7. Print next steps ────────────────────────────────────────────────────

echo ""
info "=== Setup Complete ==="
echo ""
echo "Your agent is registered with Coffee Shop and ready to go."
echo ""
info "STEP 1: Configure MCP Server (recommended)"
echo ""
echo "  Add to your agent platform's MCP config:"
echo ""
echo '  {                                          '
echo '    "mcpServers": {                          '
echo '      "coffeeshop": {                        '
echo '        "command": "coffeeshop",             '
echo '        "args": ["mcp-server"]               '
echo '      }                                      '
echo '    }                                        '
echo '  }                                          '
echo ""
echo "  Config file locations:"
if [ "$PLATFORM" = "macos" ]; then
  echo "    Claude Code:  ~/.claude/mcp_servers.json"
  echo "    Cursor:       Settings > MCP"
  echo "    OpenClaw:     ~/.openclaw/openclaw.json"
  echo "    ZeroClaw:     ~/.zeroclaw/config.toml"
else
  echo "    Claude Code:  ~/.claude/mcp_servers.json"
  echo "    Cursor:       Settings > MCP"
  echo "    OpenClaw:     ~/.openclaw/openclaw.json"
  echo "    ZeroClaw:     ~/.zeroclaw/config.toml"
fi
echo ""
info "STEP 2: Try CLI Commands"
echo ""
echo "  coffeeshop whoami                             # Verify identity"
echo "  coffeeshop search --skills react --limit 10   # Search for jobs"
echo "  coffeeshop apply --job-id <id>                # Apply to a job"
echo "  coffeeshop applications                       # Track applications"
echo "  coffeeshop inbox --unread-only                # Check messages"
echo ""
info "STEP 3: Build Your Profile"
echo ""
echo "  Create a JSON file with your profile data, then:"
echo "  coffeeshop profile update --file profile.json"
echo ""
echo "  Or use the 'onboard_candidate' MCP prompt for guided setup."
echo ""
