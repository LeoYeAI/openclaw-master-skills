#!/usr/bin/env bash
# AgentAudit — Installer
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/starbuck100/agentaudit-skill/main/install.sh | bash
#
# Options:
#   --agent <name>   Set your agent name (default: auto-generated)
#
# Works with: Claude Code, Cursor, Windsurf, Cline, and any terminal.

set -euo pipefail

# ── Colors ──
if [ -t 1 ]; then
  G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; B='\033[0;34m'; D='\033[2m'; N='\033[0m'; BOLD='\033[1m'
else
  G=''; Y=''; R=''; B=''; D=''; N=''; BOLD=''
fi
ok()   { echo -e "${G}✓${N} $*"; }
info() { echo -e "${B}→${N} $*"; }
warn() { echo -e "${Y}!${N} $*" >&2; }
fail() { echo -e "${R}✗${N} $*" >&2; exit 1; }

# ── Dependencies ──
for cmd in git curl jq; do
  command -v "$cmd" &>/dev/null || fail "Required: $cmd — install it first."
done

# ── Parse args ──
AGENT_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent|-a) AGENT_NAME="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: install.sh [--agent <name>]"
      echo "Downloads AgentAudit and registers your agent."
      exit 0 ;;
    *) shift ;;
  esac
done

# ── Clone / Update ──
CLONE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/agentaudit-skill"

echo ""
info "Installing AgentAudit..."
echo ""

if [ -d "$CLONE_DIR/.git" ]; then
  info "Updating existing installation..."
  git -C "$CLONE_DIR" pull --quiet 2>/dev/null || warn "git pull failed — using existing version"
  ok "Updated: $CLONE_DIR"
else
  mkdir -p "$(dirname "$CLONE_DIR")"
  git clone --depth 1 https://github.com/starbuck100/agentaudit-skill.git "$CLONE_DIR" 2>/dev/null \
    || fail "Could not clone repository. Check your internet connection."
  ok "Downloaded to: $CLONE_DIR"
fi

# ── Register agent ──
if [ -z "$AGENT_NAME" ]; then
  AGENT_NAME="agent-$(hostname -s 2>/dev/null || echo 'local')"
  AGENT_NAME=$(echo "$AGENT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g' | head -c 64)
fi

CRED_FILE="$CLONE_DIR/config/credentials.json"
USER_CRED="${XDG_CONFIG_HOME:-$HOME/.config}/agentaudit/credentials.json"

if [ -f "$CRED_FILE" ] || [ -f "$USER_CRED" ]; then
  ok "Already registered (credentials found)"
else
  info "Registering agent '$AGENT_NAME'..."
  if bash "$CLONE_DIR/scripts/register.sh" "$AGENT_NAME" >/dev/null 2>&1; then
    ok "Registered as: $AGENT_NAME"
  else
    warn "Auto-registration failed. Register manually later:"
    echo "    bash $CLONE_DIR/scripts/register.sh your-agent-name"
  fi
fi

# ── Claude Code: Auto-integrate ──
CLAUDE_INTEGRATED=false
if [ -d "$HOME/.claude" ]; then
  SKILLS_DIR="$HOME/.claude/skills"
  INSTALL_DIR="$SKILLS_DIR/agentaudit"
  mkdir -p "$SKILLS_DIR"
  ln -sf "$CLONE_DIR" "$INSTALL_DIR"
  ok "Claude Code: Linked to $INSTALL_DIR"
  CLAUDE_INTEGRATED=true
fi

# ── Quick test ──
info "Testing connection..."
if bash "$CLONE_DIR/scripts/check.sh" chalk >/dev/null 2>&1; then
  ok "Registry connection works"
else
  warn "Could not reach registry — check your network"
fi

# ══════════════════════════════════════════════════════════════
# SUCCESS — Show platform-specific next steps
# ══════════════════════════════════════════════════════════════

SCRIPTS="$CLONE_DIR/scripts"

echo ""
echo -e "${G}${BOLD}════════════════════════════════════════════${N}"
echo -e "${G}${BOLD}  AgentAudit installed successfully${N}"
echo -e "${G}${BOLD}════════════════════════════════════════════${N}"
echo ""
echo -e "  Location: ${BOLD}$CLONE_DIR${N}"
echo -e "  Scripts:  ${BOLD}$SCRIPTS${N}"
echo ""
echo -e "  ${BOLD}Quick test:${N}"
echo "    bash $SCRIPTS/check.sh lodash"
echo ""

# ── Platform-specific setup instructions ──

if [ "$CLAUDE_INTEGRATED" = true ]; then
  echo -e "  ${G}${BOLD}Claude Code — Ready to use!${N}"
  echo "  The skill is active. Restart Claude Code to load it."
  echo "  Your agent will automatically use the security gate."
  echo ""
fi

# Always show the other platforms (user might use multiple)
echo -e "${D}────────────────────────────────────────────${N}"
echo -e "  ${BOLD}Setup for other platforms:${N}"
echo ""

if [ "$CLAUDE_INTEGRATED" != true ]; then
  echo -e "  ${BOLD}Claude Code${N}"
  echo "    mkdir -p ~/.claude/skills"
  echo "    ln -sf $CLONE_DIR ~/.claude/skills/agentaudit"
  echo "    # Restart Claude Code"
  echo ""
fi

cat <<EOF
  ${BOLD}Cursor${N}
    1. Open Cursor Settings > Rules > User Rules
    2. Add this line:
       When installing packages, first run: bash $SCRIPTS/gate.sh npm <package>
       For auditing, follow: $CLONE_DIR/SKILL.md

  ${BOLD}Windsurf${N}
    1. Open Windsurf Settings > Rules
    2. Add the same instruction as Cursor above.

  ${BOLD}Cline${N}
    1. Open Cline settings > Custom Instructions
    2. Paste the contents of: $CLONE_DIR/SKILL.md

  ${BOLD}Any terminal (manual)${N}
    bash $SCRIPTS/gate.sh npm <package>     # Check before install
    bash $SCRIPTS/check.sh <package>        # Lookup trust score
    bash $SCRIPTS/upload.sh report.json     # Submit audit report
EOF
echo ""
echo -e "${D}────────────────────────────────────────────${N}"
echo -e "  Docs: $CLONE_DIR/README.md"
echo -e "  Help: https://www.agentaudit.dev"
echo ""
