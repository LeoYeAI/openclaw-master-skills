#!/usr/bin/env bash
# =============================================================================
# Supurr CLI Installer
# Usage: curl -fsSL https://cli.supurr.app/install | bash
# =============================================================================
set -euo pipefail

# Configuration
SUPURR_DOWNLOAD_URL="${SUPURR_DOWNLOAD_URL:-https://cli.supurr.app/releases}"
INSTALL_DIR="${SUPURR_INSTALL_DIR:-$HOME/.supurr/bin}"

# Colors (only if terminal supports it)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    MAGENTA='\033[0;35m'
    BOLD='\033[1m'
    DIM='\033[2m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' CYAN='' MAGENTA='' BOLD='' DIM='' NC=''
fi

info() { echo -e "${CYAN}→${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1" >&2; exit 1; }

# =============================================================================
# Banner with Cat
# =============================================================================

echo ""
echo -e "${MAGENTA}"
cat << 'EOF'
    /\_____/\
   /  o   o  \      ███████╗██╗   ██╗██████╗ ██╗   ██╗██████╗ ██████╗ 
  ( ==  ^  == )     ██╔════╝██║   ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗
   )         (      ███████╗██║   ██║██████╔╝██║   ██║██████╔╝██████╔╝
  (           )     ╚════██║██║   ██║██╔═══╝ ██║   ██║██╔══██╗██╔══██╗
 ( (  )   (  ) )    ███████║╚██████╔╝██║     ╚██████╔╝██║  ██║██║  ██║
(__(__)___(__)__)   ╚══════╝ ╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
EOF
echo -e "${NC}"
echo -e "${BOLD}  ⚡ Trading Bot CLI${NC} ${DIM}— Backtest → Deploy → Monitor${NC}"
echo ""

# =============================================================================
# Detect Platform
# =============================================================================

detect_platform() {
    local os arch
    
    os="$(uname -s)"
    arch="$(uname -m)"
    
    case "$os" in
        Darwin) os="darwin" ;;
        Linux)  os="linux" ;;
        MINGW*|MSYS*|CYGWIN*) error "Windows is not yet supported. Use WSL instead." ;;
        *) error "Unsupported operating system: $os" ;;
    esac
    
    case "$arch" in
        x86_64|amd64) arch="x64" ;;
        arm64|aarch64) arch="arm64" ;;
        *) error "Unsupported architecture: $arch" ;;
    esac
    
    # Check for Rosetta on macOS
    if [[ "$os" == "darwin" && "$arch" == "x64" ]]; then
        if [[ "$(sysctl -n sysctl.proc_translated 2>/dev/null || echo 0)" == "1" ]]; then
            arch="arm64"
            info "Running under Rosetta, using arm64 binary"
        fi
    fi
    
    echo "${os}-${arch}"
}

# =============================================================================
# Install
# =============================================================================

main() {
    local platform binary_name download_url
    
    platform=$(detect_platform)
    binary_name="supurr-${platform}"
    download_url="${SUPURR_DOWNLOAD_URL}/${binary_name}"
    
    info "Detected platform: ${BOLD}${platform}${NC}"
    info "Downloading from: ${download_url}"
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Download CLI binary
    info "Downloading supurr CLI..."
    if command -v curl &>/dev/null; then
        curl -fsSL "$download_url" -o "$INSTALL_DIR/supurr" || error "Download failed. Check if binary exists at $download_url"
    elif command -v wget &>/dev/null; then
        wget -q "$download_url" -O "$INSTALL_DIR/supurr" || error "Download failed. Check if binary exists at $download_url"
    else
        error "Neither curl nor wget found. Please install one of them."
    fi
    
    # Make executable
    chmod +x "$INSTALL_DIR/supurr"
    success "CLI installed: $INSTALL_DIR/supurr"
    
    # Download bot engine binary
    local bot_download_url="${SUPURR_DOWNLOAD_URL}/bot-${platform}"
    info "Downloading backtest engine..."
    if command -v curl &>/dev/null; then
        curl -fsSL "$bot_download_url" -o "$INSTALL_DIR/bot" 2>/dev/null && {
            chmod +x "$INSTALL_DIR/bot"
            success "Engine installed: $INSTALL_DIR/bot"
        } || {
            warn "Backtest engine not available for $platform (optional)"
        }
    elif command -v wget &>/dev/null; then
        wget -q "$bot_download_url" -O "$INSTALL_DIR/bot" 2>/dev/null && {
            chmod +x "$INSTALL_DIR/bot"
            success "Engine installed: $INSTALL_DIR/bot"
        } || {
            warn "Backtest engine not available for $platform (optional)"
        }
    fi
    
    # =============================================================================
    # Setup PATH
    # =============================================================================
    
    setup_path() {
        local shell_rc=""
        local shell_name=""
        
        # Detect shell config file
        case "${SHELL:-}" in
            */zsh)  shell_rc="$HOME/.zshrc"; shell_name="zsh" ;;
            */bash) shell_rc="$HOME/.bashrc"; shell_name="bash" ;;
            */fish) shell_rc="$HOME/.config/fish/config.fish"; shell_name="fish" ;;
            *) 
                # Try common files
                if [[ -f "$HOME/.zshrc" ]]; then
                    shell_rc="$HOME/.zshrc"; shell_name="zsh"
                elif [[ -f "$HOME/.bashrc" ]]; then
                    shell_rc="$HOME/.bashrc"; shell_name="bash"
                fi
                ;;
        esac
        
        if [[ -z "$shell_rc" ]]; then
            warn "Could not detect shell config. Add this to your shell profile:"
            echo -e "  ${CYAN}export PATH=\"\$HOME/.supurr/bin:\$PATH\"${NC}"
            return
        fi
        
        # Check if already in PATH
        if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
            success "Already in PATH"
            return
        fi
        
        # Check if already added to rc file
        if grep -q "\.supurr/bin" "$shell_rc" 2>/dev/null; then
            success "PATH entry already in $shell_rc"
            return
        fi
        
        # Add to shell config
        local path_export
        if [[ "$shell_name" == "fish" ]]; then
            path_export='set -gx PATH "$HOME/.supurr/bin" $PATH'
        else
            path_export='export PATH="$HOME/.supurr/bin:$PATH"'
        fi
        
        echo "" >> "$shell_rc"
        echo "# Supurr CLI" >> "$shell_rc"
        echo "$path_export" >> "$shell_rc"
        
        success "Added to $shell_rc"
    }
    
    setup_path
    
    # =============================================================================
    # Verify installation
    # =============================================================================
    
    export PATH="$INSTALL_DIR:$PATH"
    
    if "$INSTALL_DIR/supurr" --version &>/dev/null; then
        success "Installation verified!"
    else
        warn "Binary downloaded but may need additional dependencies"
    fi
    
    # =============================================================================
    # Done!
    # =============================================================================
    
    echo ""
    echo -e "${MAGENTA}    /\\_/\\  ${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${MAGENTA}   ( o.o ) ${GREEN}  ✨ Installation Complete!${NC}"
    echo -e "${MAGENTA}    > ^ <  ${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BOLD}Quick Start:${NC}"
    echo -e "    ${CYAN}supurr init${NC}           ${DIM}# Setup wallet${NC}"
    echo -e "    ${CYAN}supurr new grid${NC}       ${DIM}# Create config${NC}"
    echo -e "    ${CYAN}supurr backtest${NC}       ${DIM}# Test strategy${NC}"
    echo -e "    ${CYAN}supurr deploy${NC}         ${DIM}# Go live!${NC}"
    echo ""
    echo -e "  ${YELLOW}⚠${NC}  Open a new terminal or run: ${CYAN}source ~/.zshrc${NC}"
    echo ""
}

main "$@"
