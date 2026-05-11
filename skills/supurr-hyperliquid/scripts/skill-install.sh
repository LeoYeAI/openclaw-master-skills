#!/usr/bin/env bash
# =============================================================================
# Supurr Skill Installer
# Usage: curl -fsSL https://cli.supurr.app/skill-install | bash
# =============================================================================
set -e

REPO="https://github.com/Supurr-App/supurr_skill"

# ANSI colors
BOLD=$'\033[1m'
GREY=$'\033[90m'
RED=$'\033[31m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
MAGENTA=$'\033[35m'
CYAN=$'\033[36m'
NC=$'\033[0m'

info() { printf "${BOLD}${GREY}>${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}! %s${NC}\n" "$*"; }
error() { printf "${RED}x %s${NC}\n" "$*" >&2; }
completed() { printf "${GREEN}✓${NC} %s\n" "$*"; }

print_banner() {
  printf "${MAGENTA}"
  cat <<'EOF'
    /\_____/\
   /  o   o  \      ███████╗██╗   ██╗██████╗ ██╗   ██╗██████╗ ██████╗ 
  ( ==  ^  == )     ██╔════╝██║   ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗
   )         (      ███████╗██║   ██║██████╔╝██║   ██║██████╔╝██████╔╝
  (           )     ╚════██║██║   ██║██╔═══╝ ██║   ██║██╔══██╗██╔══██╗
 ( (  )   (  ) )    ███████║╚██████╔╝██║     ╚██████╔╝██║  ██║██║  ██║
(__(__)___(__)__)   ╚══════╝ ╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
EOF
  printf "${NC}\n"
  printf "${BOLD}  Supurr AI Skill Installer${NC}\n\n"
}

print_success() {
  printf "\n${MAGENTA}    /\\_/\\  ${GREEN}═══════════════════════════════════════${NC}\n"
  printf "${MAGENTA}   ( o.o ) ${GREEN}  ✨ Skills Installed Successfully!${NC}\n"
  printf "${MAGENTA}    > ^ <  ${GREEN}═══════════════════════════════════════${NC}\n\n"
}

install_skill() {
  local skills_dir="$1"
  local name="$2"
  local temp_dir="$3"

  mkdir -p "$skills_dir"
  rm -rf "$skills_dir/supurr" 2>/dev/null || true

  if [ -f "$temp_dir/SKILL.md" ]; then
    mkdir -p "$skills_dir/supurr"
    cp "$temp_dir/SKILL.md" "$skills_dir/supurr/"
    cp "$temp_dir/README.md" "$skills_dir/supurr/" 2>/dev/null || true
    completed "$name → ${CYAN}$skills_dir/supurr${NC}"
    return 0
  fi
  return 1
}

# Targets: [dir, name]
declare -a TARGETS=(
  # Universal agents
  "$HOME/.agents/skills|Universal Agents"
  # Individual agents
  "$HOME/.agent/skills|Antigravity"
  "$HOME/.amp/skills|Amp"
  "$HOME/.augment/skills|Augment"
  "$HOME/.claude/skills|Claude Code"
  "$HOME/.cline/skills|Cline"
  "$HOME/.codebuddy/skills|CodeBuddy"
  "$HOME/.codex/skills|OpenAI Codex"
  "$HOME/.commandcode/skills|Command Code"
  "$HOME/.continue/skills|Continue"
  "$HOME/.cursor/skills|Cursor"
  "$HOME/.gemini-cli/skills|Gemini CLI"
  "$HOME/.github-copilot/skills|GitHub Copilot"
  "$HOME/.kimi-code-cli/skills|Kimi Code CLI"
  "$HOME/.config/opencode/skill|OpenCode"
  "$HOME/.openclaw/skills|OpenClaw"
  "$HOME/.roo/skills|Roo"
  "$HOME/.trae/skills|Trae"
  "$HOME/.void/skills|Void"
  "$HOME/.windsurf/skills|Windsurf"
  "$HOME/.zed/skills|Zed"
)

print_banner

# Detect available tools
declare -a FOUND=()
for target in "${TARGETS[@]}"; do
  dir="${target%%|*}"
  parent="${dir%/*}"
  [ -d "$parent" ] && FOUND+=("$target")
done

if [ ${#FOUND[@]} -eq 0 ]; then
  error "No supported AI tools found."
  printf "\nSupported:\n"
  printf "  • Antigravity (~/.agent)\n"
  printf "  • Amp (~/.amp)\n"
  printf "  • Claude Code (~/.claude)\n"
  printf "  • Cline (~/.cline)\n"
  printf "  • Cursor (~/.cursor)\n"
  printf "  • Gemini CLI (~/.gemini-cli)\n"
  printf "  • GitHub Copilot (~/.github-copilot)\n"
  printf "  • OpenAI Codex (~/.codex)\n"
  printf "  • OpenCode (~/.config/opencode)\n"
  printf "  • Windsurf (~/.windsurf)\n"
  printf "  • Zed (~/.zed)\n"
  printf "  • And more...\n"
  exit 1
fi

info "Downloading from ${CYAN}$REPO${NC}..."
temp_dir=$(mktemp -d)
git clone --depth 1 --quiet "$REPO" "$temp_dir"
printf "\n"

installed=0
for target in "${FOUND[@]}"; do
  dir="${target%%|*}"
  name="${target##*|}"
  if install_skill "$dir" "$name" "$temp_dir"; then
    installed=$((installed + 1))
  fi
done

# Local installs (if in a project directory)
if [ "$(pwd)" != "$HOME" ]; then
  declare -a LOCAL_TARGETS=(
    ".claude/skills|Claude Code (local)"
    ".agent/skills|Antigravity (local)"
    ".cursor/skills|Cursor (local)"
  )
  for target in "${LOCAL_TARGETS[@]}"; do
    dir="${target%%|*}"
    name="${target##*|}"
    parent="${dir%/*}"
    if [ -d "./$parent" ]; then
      install_skill "./$dir" "$name" "$temp_dir" && installed=$((installed + 1))
    fi
  done
fi

rm -rf "$temp_dir"

print_success
printf "  ${BOLD}What's installed:${NC}\n"
printf "    • ${CYAN}supurr${NC} skill for Hyperliquid trading bots\n\n"

# Install CLI if not present
if ! command -v supurr &>/dev/null; then
  info "Installing Supurr CLI..."
  curl -fsSL https://cli.supurr.app/install | bash
else
  completed "Supurr CLI already installed: $(supurr --version 2>/dev/null || echo 'unknown')"
fi

printf "\n"
warn "Restart your AI tool(s) to load the skill."
printf "\n"
info "Re-run anytime to update: ${CYAN}curl -fsSL https://cli.supurr.app/skill-install | bash${NC}"
printf "\n"

