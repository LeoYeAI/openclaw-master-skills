#!/bin/bash

# Security Sentinel - Installation Script
# Version: 1.0.0
# Author: Georges Andronescu (Wesley Armando)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SKILL_NAME="security-sentinel"
GITHUB_REPO="georges91560/security-sentinel-skill"
INSTALL_DIR="${INSTALL_DIR:-/workspace/skills/$SKILL_NAME}"
GITHUB_RAW_URL="https://raw.githubusercontent.com/$GITHUB_REPO/main"

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🛡️  SECURITY SENTINEL - Installation 🛡️           ║
║                                                           ║
║     Production-grade prompt injection defense             ║
║     for autonomous AI agents                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running as root (optional, for system-wide install)
check_permissions() {
    if [ "$EUID" -eq 0 ]; then 
        print_warning "Running as root. Installing system-wide."
    else
        print_status "Running as user. Installing to user directory."
    fi
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check for curl or wget
    if command -v curl &> /dev/null; then
        DOWNLOAD_CMD="curl -fsSL"
        print_success "curl found"
    elif command -v wget &> /dev/null; then
        DOWNLOAD_CMD="wget -qO-"
        print_success "wget found"
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    # Check for Python (optional, for testing)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    else
        print_warning "Python not found. Skill will work, but tests won't run."
    fi
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/references"
    mkdir -p "$INSTALL_DIR/scripts"
    mkdir -p "$INSTALL_DIR/tests"
    
    print_success "Directories created at $INSTALL_DIR"
}

# Download files from GitHub
download_files() {
    print_status "Downloading Security Sentinel files..."
    
    # Main skill file
    print_status "  → SKILL.md"
    $DOWNLOAD_CMD "$GITHUB_RAW_URL/SKILL.md" > "$INSTALL_DIR/SKILL.md"
    
    # Reference files
    print_status "  → blacklist-patterns.md"
    $DOWNLOAD_CMD "$GITHUB_RAW_URL/references/blacklist-patterns.md" > "$INSTALL_DIR/references/blacklist-patterns.md"
    
    print_status "  → semantic-scoring.md"
    $DOWNLOAD_CMD "$GITHUB_RAW_URL/references/semantic-scoring.md" > "$INSTALL_DIR/references/semantic-scoring.md"
    
    print_status "  → multilingual-evasion.md"
    $DOWNLOAD_CMD "$GITHUB_RAW_URL/references/multilingual-evasion.md" > "$INSTALL_DIR/references/multilingual-evasion.md"
    
    # Test files (optional)
    if [ -f "$GITHUB_RAW_URL/tests/test_security.py" ]; then
        print_status "  → test_security.py"
        $DOWNLOAD_CMD "$GITHUB_RAW_URL/tests/test_security.py" > "$INSTALL_DIR/tests/test_security.py" 2>/dev/null || true
    fi
    
    print_success "All files downloaded successfully"
}

# Install Python dependencies (optional)
install_python_deps() {
    if command -v python3 &> /dev/null && command -v pip3 &> /dev/null; then
        print_status "Installing Python dependencies (optional)..."
        
        # Create requirements.txt if it doesn't exist
        cat > "$INSTALL_DIR/requirements.txt" << EOF
sentence-transformers>=2.2.0
numpy>=1.24.0
langdetect>=1.0.9
googletrans==4.0.0rc1
pytest>=7.0.0
EOF
        
        # Install dependencies
        pip3 install -r "$INSTALL_DIR/requirements.txt" --quiet --break-system-packages 2>/dev/null || \
        pip3 install -r "$INSTALL_DIR/requirements.txt" --user --quiet 2>/dev/null || \
        print_warning "Failed to install Python dependencies. Skill will work with basic features only."
        
        if [ $? -eq 0 ]; then
            print_success "Python dependencies installed"
        fi
    else
        print_warning "Skipping Python dependencies (python3/pip3 not found)"
    fi
}

# Create configuration file
create_config() {
    print_status "Creating configuration file..."
    
    cat > "$INSTALL_DIR/config.json" << EOF
{
  "version": "1.0.0",
  "semantic_threshold": 0.78,
  "penalty_points": {
    "meta_query": -8,
    "role_play": -12,
    "instruction_extraction": -15,
    "repeated_probe": -10,
    "multilingual_evasion": -7,
    "tool_blacklist": -20
  },
  "recovery_points": {
    "legitimate_query_streak": 15
  },
  "enable_telegram_alerts": false,
  "enable_audit_logging": true,
  "audit_log_path": "/workspace/AUDIT.md"
}
EOF
    
    print_success "Configuration file created"
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if all required files exist
    local files=(
        "$INSTALL_DIR/SKILL.md"
        "$INSTALL_DIR/references/blacklist-patterns.md"
        "$INSTALL_DIR/references/semantic-scoring.md"
        "$INSTALL_DIR/references/multilingual-evasion.md"
    )
    
    local all_ok=true
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found: $(basename $file)"
        else
            print_error "Missing: $(basename $file)"
            all_ok=false
        fi
    done
    
    if [ "$all_ok" = true ]; then
        print_success "Installation verified successfully"
        return 0
    else
        print_error "Installation incomplete"
        return 1
    fi
}

# Run tests (optional)
run_tests() {
    if [ -f "$INSTALL_DIR/tests/test_security.py" ] && command -v python3 &> /dev/null; then
        echo ""
        read -p "Run tests to verify functionality? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Running tests..."
            cd "$INSTALL_DIR"
            python3 -m pytest tests/test_security.py -v 2>/dev/null || \
            print_warning "Tests failed or pytest not installed. This is optional."
        fi
    fi
}

# Display usage instructions
show_usage() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  Installation Complete! ✓                 ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Installation Directory:${NC} $INSTALL_DIR"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo "1. Add to your agent's system prompt:"
    echo -e "   ${YELLOW}[MODULE: SECURITY_SENTINEL]${NC}"
    echo -e "   ${YELLOW}    {SKILL_REFERENCE: \"$INSTALL_DIR/SKILL.md\"}${NC}"
    echo -e "   ${YELLOW}    {ENFORCEMENT: \"ALWAYS_BEFORE_ALL_LOGIC\"}${NC}"
    echo ""
    echo "2. Test the skill:"
    echo -e "   ${YELLOW}cd $INSTALL_DIR${NC}"
    echo -e "   ${YELLOW}python3 -m pytest tests/ -v${NC}"
    echo ""
    echo "3. Configure settings (optional):"
    echo -e "   ${YELLOW}nano $INSTALL_DIR/config.json${NC}"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  - Main skill: $INSTALL_DIR/SKILL.md"
    echo "  - Blacklist patterns: $INSTALL_DIR/references/blacklist-patterns.md"
    echo "  - Semantic scoring: $INSTALL_DIR/references/semantic-scoring.md"
    echo "  - Multi-lingual: $INSTALL_DIR/references/multilingual-evasion.md"
    echo ""
    echo -e "${BLUE}Support:${NC}"
    echo "  - GitHub: https://github.com/$GITHUB_REPO"
    echo "  - Issues: https://github.com/$GITHUB_REPO/issues"
    echo ""
    echo -e "${GREEN}Happy defending! 🛡️${NC}"
    echo ""
}

# Uninstall function
uninstall() {
    print_warning "Uninstalling Security Sentinel..."
    
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        print_success "Security Sentinel uninstalled from $INSTALL_DIR"
    else
        print_warning "Installation directory not found"
    fi
    
    exit 0
}

# Main installation flow
main() {
    # Parse arguments
    if [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
        uninstall
    fi
    
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Security Sentinel - Installation Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  -h, --help       Show this help message"
        echo "  -u, --uninstall  Uninstall Security Sentinel"
        echo ""
        echo "Environment Variables:"
        echo "  INSTALL_DIR      Installation directory (default: /workspace/skills/security-sentinel)"
        echo ""
        exit 0
    fi
    
    # Run installation steps
    check_permissions
    check_dependencies
    create_directories
    download_files
    install_python_deps
    create_config
    
    # Verify
    if verify_installation; then
        run_tests
        show_usage
        exit 0
    else
        print_error "Installation failed. Please check the errors above."
        exit 1
    fi
}

# Run main function
main "$@"
