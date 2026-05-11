#!/bin/bash
# install_deps.sh — Auto-install missing dev dependencies.
#
# Installs (only what's missing):
#   - Homebrew (macOS)
#   - Anaconda / Miniconda (conda)
#   - Node.js 22 via nvm or Homebrew
#   - pnpm
#   - Git
#   - Docker Desktop (macOS — opens download page if not installed)
#   - Xcode Command Line Tools (macOS, needed for build_ext)
#
# Usage:
#   bash scripts/install_deps.sh           # install everything missing
#   bash scripts/install_deps.sh --check   # check only, don't install
#   bash scripts/install_deps.sh --conda   # only install conda
#   bash scripts/install_deps.sh --node    # only install node/pnpm
#
# Safe to re-run: skips anything already installed.

set -e

# Augment PATH for non-interactive shells
for _p in "$HOME/anaconda3/bin" "$HOME/miniconda3/bin" "$HOME/miniforge3/bin" \
          "$HOME/.nvm/versions/node/$(ls $HOME/.nvm/versions/node 2>/dev/null | sort -V | tail -1)/bin" \
          "/opt/homebrew/bin" "/usr/local/bin" "/opt/homebrew/lib/node_modules/.bin"; do
  [ -d "$_p" ] && export PATH="$_p:$PATH"
done

CHECK_ONLY=false
ONLY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) CHECK_ONLY=true; shift ;;
    --conda) ONLY="conda"; shift ;;
    --node)  ONLY="node"; shift ;;
    --pnpm)  ONLY="pnpm"; shift ;;
    *) shift ;;
  esac
done

ok()     { echo "  ✓ $*"; }
skip()   { echo "  - $*"; }
info()   { echo "  → $*"; }
fail()   { echo "  ✗ $*" >&2; }
header() { echo ""; echo "$*"; echo "$(echo "$*" | sed 's/./-/g')"; }

OS=$(uname -s)
ARCH=$(uname -m)
INSTALLED=()
SKIPPED=()
FAILED=()

# ─── Homebrew (macOS only) ────────────────────────────────────────────────────

install_brew() {
  if [ "$OS" != "Darwin" ]; then return; fi
  if command -v brew &>/dev/null; then
    skip "Homebrew already installed ($(brew --version | head -1))"
    return
  fi
  [ "$CHECK_ONLY" = true ] && { fail "Homebrew not installed"; return; }
  info "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add to PATH for Apple Silicon
  [ "$ARCH" = "arm64" ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  ok "Homebrew installed"
  INSTALLED+=("homebrew")
}

# ─── Xcode CLI Tools (macOS, needed for Cython build_ext) ────────────────────

install_xcode_clt() {
  if [ "$OS" != "Darwin" ]; then return; fi
  if xcode-select -p &>/dev/null 2>&1; then
    skip "Xcode CLT already installed"
    return
  fi
  [ "$CHECK_ONLY" = true ] && { fail "Xcode CLT not installed"; return; }
  info "Installing Xcode Command Line Tools (needed for hummingbot build_ext)..."
  xcode-select --install 2>/dev/null || true
  # Wait for install
  until xcode-select -p &>/dev/null 2>&1; do sleep 5; done
  ok "Xcode CLT installed"
  INSTALLED+=("xcode-clt")
}

# ─── Conda ────────────────────────────────────────────────────────────────────

install_conda() {
  if command -v conda &>/dev/null; then
    skip "conda already installed ($(conda --version))"
    return
  fi
  [ "$CHECK_ONLY" = true ] && { fail "conda not installed"; return; }

  info "Installing Miniconda..."
  local url installer

  if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
      url="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
    else
      url="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    fi
  elif [ "$OS" = "Linux" ]; then
    if [ "$ARCH" = "aarch64" ]; then
      url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
    else
      url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    fi
  else
    fail "Unsupported OS: $OS — install conda manually from https://conda.io"
    FAILED+=("conda")
    return
  fi

  installer="/tmp/miniconda_install.sh"
  info "Downloading $url..."
  curl -fsSL "$url" -o "$installer"

  # Remove conflicting md5 if missing (macOS sometimes lacks it)
  PATH="/opt/homebrew/bin:/usr/local/bin:$PATH" bash "$installer" -b -p "$HOME/miniconda3"
  rm -f "$installer"

  export PATH="$HOME/miniconda3/bin:$PATH"
  conda init zsh bash 2>/dev/null || true

  ok "Miniconda installed at $HOME/miniconda3"
  ok "Restart terminal or run: source ~/.zshrc"
  INSTALLED+=("conda")
}

# ─── Node.js via nvm ─────────────────────────────────────────────────────────

install_node() {
  # Check existing node version
  if command -v node &>/dev/null; then
    local ver major
    ver=$(node --version)
    major=$(echo "$ver" | sed 's/v//' | cut -d. -f1)
    if [ "$major" -ge 20 ]; then
      skip "node $ver already installed (>= v20)"
      return
    else
      info "node $ver found but need v20+ — installing v22 via nvm"
    fi
  fi

  [ "$CHECK_ONLY" = true ] && { fail "node v20+ not installed"; return; }

  # Try nvm first
  if command -v nvm &>/dev/null || [ -s "$HOME/.nvm/nvm.sh" ]; then
    info "Using nvm to install node v22..."
    [ -s "$HOME/.nvm/nvm.sh" ] && source "$HOME/.nvm/nvm.sh"
    nvm install 22
    nvm use 22
    nvm alias default 22
    ok "node $(node --version) installed via nvm"
    INSTALLED+=("node")
    return
  fi

  # Try Homebrew
  if command -v brew &>/dev/null; then
    info "Installing node@22 via Homebrew..."
    brew install node@22
    brew link node@22 --force --overwrite 2>/dev/null || true
    export PATH="$(brew --prefix node@22)/bin:$PATH"
    ok "node $(node --version) installed via Homebrew"
    INSTALLED+=("node")
    return
  fi

  # Install nvm then node
  info "Installing nvm first..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  nvm install 22
  nvm use 22
  nvm alias default 22
  ok "node $(node --version) installed via nvm"
  INSTALLED+=("node")
}

# ─── pnpm ────────────────────────────────────────────────────────────────────

install_pnpm() {
  if command -v pnpm &>/dev/null; then
    skip "pnpm already installed ($(pnpm --version 2>/dev/null | head -1))"
    return
  fi
  [ "$CHECK_ONLY" = true ] && { fail "pnpm not installed"; return; }

  if command -v npm &>/dev/null; then
    info "Installing pnpm via npm..."
    npm install -g pnpm
    export PATH="$(npm root -g)/.bin:$PATH"
    ok "pnpm $(pnpm --version) installed"
    INSTALLED+=("pnpm")
  elif command -v brew &>/dev/null; then
    info "Installing pnpm via Homebrew..."
    brew install pnpm
    ok "pnpm $(pnpm --version) installed"
    INSTALLED+=("pnpm")
  else
    fail "Cannot install pnpm — install npm or Homebrew first"
    FAILED+=("pnpm")
  fi
}

# ─── Git ─────────────────────────────────────────────────────────────────────

install_git() {
  if command -v git &>/dev/null; then
    skip "git already installed ($(git --version))"
    return
  fi
  [ "$CHECK_ONLY" = true ] && { fail "git not installed"; return; }

  if command -v brew &>/dev/null; then
    brew install git
    ok "git installed"
    INSTALLED+=("git")
  else
    fail "git not found — install from https://git-scm.com or via your package manager"
    FAILED+=("git")
  fi
}

# ─── Docker ──────────────────────────────────────────────────────────────────

install_docker() {
  if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    skip "Docker already installed and running ($(docker --version | cut -d' ' -f3 | tr -d ','))"
    return
  fi

  if command -v docker &>/dev/null; then
    skip "Docker installed but daemon not running — open Docker Desktop"
    return
  fi

  [ "$CHECK_ONLY" = true ] && { fail "Docker not installed"; return; }

  if [ "$OS" = "Darwin" ]; then
    if command -v brew &>/dev/null; then
      info "Installing Docker Desktop via Homebrew..."
      brew install --cask docker
      ok "Docker Desktop installed — open it to start the daemon"
      INSTALLED+=("docker")
    else
      info "Opening Docker Desktop download page..."
      open "https://www.docker.com/products/docker-desktop/"
      info "Download and install Docker Desktop, then re-run this script"
    fi
  elif [ "$OS" = "Linux" ]; then
    info "Installing Docker Engine..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER" 2>/dev/null || true
    ok "Docker installed — log out and back in for group membership"
    INSTALLED+=("docker")
  fi
}

# ─── Run ─────────────────────────────────────────────────────────────────────

header "Hummingbot Dev Dependency Installer"
[ "$CHECK_ONLY" = true ] && echo "  (check mode — not installing anything)"
echo "  OS: $OS $ARCH"

if [ -n "$ONLY" ]; then
  # Install single component
  case "$ONLY" in
    conda) install_conda ;;
    node)  install_node ;;
    pnpm)  install_pnpm ;;
  esac
else
  # Install everything missing
  [ "$OS" = "Darwin" ] && install_brew
  [ "$OS" = "Darwin" ] && install_xcode_clt
  install_conda
  install_node
  install_pnpm
  install_git
  install_docker
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

header "Summary"

if [ ${#INSTALLED[@]} -gt 0 ]; then
  ok "Installed: ${INSTALLED[*]}"
fi
if [ ${#FAILED[@]} -gt 0 ]; then
  fail "Failed: ${FAILED[*]}"
fi
if [ ${#INSTALLED[@]} -eq 0 ] && [ ${#FAILED[@]} -eq 0 ]; then
  ok "All dependencies already installed"
fi

if [ ${#INSTALLED[@]} -gt 0 ]; then
  echo ""
  echo "  Restart your terminal (or run: source ~/.zshrc) to apply PATH changes."
fi

if [ ${#FAILED[@]} -gt 0 ]; then
  echo ""
  fail "Some dependencies failed to install — fix manually then retry"
  exit 1
fi

echo ""
echo "Next: bash scripts/check_env.sh"
