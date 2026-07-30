#!/bin/bash
#
# Unihiker K10 Skill - Environment Setup
# Installs arduino-cli, K10 BSP, and MicroPython tools
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K10_CONFIG_DIR="${HOME}/.k10"
SETUP_DONE_MARKER="${K10_CONFIG_DIR}/.setup-done"

SHOW_OUTPUT=false
if [[ "$1" == "--show" ]]; then
    SHOW_OUTPUT=true
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { 
    if [[ "$SHOW_OUTPUT" == true ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}
log_success() { 
    if [[ "$SHOW_OUTPUT" == true ]]; then
        echo -e "${GREEN}[OK]${NC} $1"
    fi
}
log_warn() { 
    if [[ "$SHOW_OUTPUT" == true ]]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
    fi
}
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Detect OS
get_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

OS=$(get_os)

# Install arduino-cli
install_arduino_cli() {
    log_info "Installing arduino-cli..."
    
    case $OS in
        linux)
            # Download and install
            curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
            mv bin/arduino-cli "${HOME}/.local/bin/" 2>/dev/null || sudo mv bin/arduino-cli /usr/local/bin/
            rm -rf bin/
            ;;
        macos)
            if command -v brew >/dev/null 2>&1; then
                brew install arduino-cli
            else
                curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
                sudo mv bin/arduino-cli /usr/local/bin/
                rm -rf bin/
            fi
            ;;
        *)
            log_error "Please install arduino-cli manually from https://arduino.github.io/arduino-cli/latest/installation/"
            return 1
            ;;
    esac
    
    log_success "arduino-cli installed"
}

# Configure arduino-cli
configure_arduino_cli() {
    log_info "Configuring arduino-cli..."
    
    local config_dir
    config_dir=$(arduino-cli config dump --format json 2>/dev/null | grep -o '"user": "[^"]*"' | cut -d'"' -f4 || echo "${HOME}/.arduino15")
    
    # Create config if not exists
    if [[ ! -f "${config_dir}/arduino-cli.yaml" ]]; then
        arduino-cli config init
    fi
    
    # Add Unihiker board manager URL
    local board_urls
    board_urls=$(arduino-cli config dump --format json 2>/dev/null | grep -o '"additional_urls": \[[^]]*\]' || echo "")
    
    if [[ ! "$board_urls" == *"unihiker"* ]]; then
        log_info "Adding Unihiker board manager URL..."
        # Note: This is a placeholder URL - update with actual Unihiker board manager URL
        # arduino-cli config add board_manager.additional_urls https://...
        log_warn "Please manually add Unihiker board manager URL if available"
    fi
    
    log_success "arduino-cli configured"
}

# Install K10 BSP
install_k10_bsp() {
    log_info "Installing Unihiker K10 BSP..."
    
    # Update index
    arduino-cli core update-index
    
    # Try to install K10 core (this may vary based on actual package name)
    # Common patterns: unihiker:k10, dfrobot:k10, etc.
    local cores=("unihiker:k10" "dfrobot:k10" "esp32:esp32")
    local installed=false
    
    for core in "${cores[@]}"; do
        if arduino-cli core install "$core" 2>/dev/null; then
            log_success "Installed core: $core"
            installed=true
            break
        fi
    done
    
    if [[ "$installed" == false ]]; then
        log_warn "Could not auto-install K10 BSP automatically"
        log_warn "Please install manually via Arduino IDE or Mind+"
        log_warn "Then run: arduino-cli core install <core_name>"
    fi
    
    # Install common libraries
    log_info "Installing libraries..."
    local libs=("SD" "WiFi" "ArduinoJson")
    for lib in "${libs[@]}"; do
        arduino-cli lib install "$lib" 2>/dev/null || true
    done
    
    log_success "Libraries installed"
}

# Install MicroPython tools
install_micropython_tools() {
    log_info "Installing MicroPython tools..."
    
    # Install mpremote (official tool)
    if ! command -v mpremote >/dev/null 2>&1; then
        pip3 install mpremote || pip install mpremote
        log_success "mpremote installed"
    else
        log_info "mpremote already installed"
    fi
    
    # Install ampy (alternative)
    if ! command -v ampy >/dev/null 2&1; then
        pip3 install adafruit-ampy || pip install adafruit-ampy
        log_success "ampy installed"
    else
        log_info "ampy already installed"
    fi
}

# Install platformio as alternative
install_platformio() {
    if ! command -v pio >/dev/null 2>&1; then
        log_info "PlatformIO not found. Skipping (arduino-cli is primary)"
    else
        log_info "PlatformIO already installed"
    fi
}

# Main setup
main() {
    mkdir -p "${K10_CONFIG_DIR}"
    
    if [[ "$SHOW_OUTPUT" == true ]]; then
        echo "Setting up Unihiker K10 development environment..."
        echo "================================================"
        echo ""
    fi
    
    # Check/Install arduino-cli
    if ! command -v arduino-cli >/dev/null 2>&1; then
        install_arduino_cli
    else
        log_info "arduino-cli already installed"
        if [[ "$SHOW_OUTPUT" == true ]]; then
            arduino-cli version
        fi
    fi
    
    # Configure arduino-cli
    if command -v arduino-cli >/dev/null 2>&1; then
        configure_arduino_cli
        install_k10_bsp
    fi
    
    # Install MicroPython tools
    install_micropython_tools
    
    # Mark setup as done
    touch "$SETUP_DONE_MARKER"
    
    if [[ "$SHOW_OUTPUT" == true ]]; then
        echo ""
        echo "================================================"
        echo "Setup complete! You can now use 'k10' command."
        echo ""
        echo "Next steps:"
        echo "  1. Connect your K10 board"
        echo "  2. Run 'k10 ports' to verify connection"
        echo "  3. Run 'k10 upload sketch.ino' to upload Arduino code"
        echo "  4. Run 'k10 upload-mp main.py' to upload MicroPython code"
    fi
    
    return 0
}

main
