#!/bin/bash
###############################################################################
# Mermaid Diagrams - Dependency Installer
#
# Installs and validates the mermaid-cli dependency required for diagram
# rendering. This script checks for existing installation, installs if needed,
# verifies version compatibility, and provides troubleshooting guidance.
#
# Usage:
#   ./scripts/install-deps.sh
#
# Requirements:
#   - Node.js >= 18.0.0
#   - npm (included with Node.js)
#   - Sufficient disk space (~200MB for dependencies)
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Minimum required version
MIN_MMDC_VERSION=11

###############################################################################
# Helper Functions
###############################################################################

print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
  echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
  echo -e "${RED}❌${NC} $1"
}

###############################################################################
# Pre-flight Checks
###############################################################################

print_info "Checking system requirements..."

# Check Node.js
if ! command -v node &> /dev/null; then
  print_error "Node.js not found"
  echo ""
  echo "Please install Node.js >= 18.0.0:"
  echo "  - macOS: brew install node"
  echo "  - Ubuntu/Debian: sudo apt install nodejs npm"
  echo "  - Other: https://nodejs.org/"
  exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  print_error "Node.js version too old: $(node --version)"
  echo "  Required: >= v18.0.0"
  echo "  Upgrade: brew upgrade node (macOS) or download from nodejs.org"
  exit 1
fi

print_success "Node.js $(node --version) found"

# Check npm
if ! command -v npm &> /dev/null; then
  print_error "npm not found (should be included with Node.js)"
  exit 1
fi

print_success "npm $(npm --version) found"

# Check disk space
AVAILABLE_MB=$(df -m . | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_MB" -lt 500 ]; then
  print_warning "Low disk space: ${AVAILABLE_MB}MB available"
  echo "  Recommended: 500MB+ free for dependencies"
fi

###############################################################################
# Check Existing Installation
###############################################################################

print_info "Checking for existing mermaid-cli installation..."

if command -v mmdc &> /dev/null; then
  MMDC_VERSION=$(mmdc --version 2>/dev/null | head -1 || echo "unknown")
  MMDC_MAJOR=$(echo "$MMDC_VERSION" | cut -d'.' -f1)
  
  print_success "mmdc found: version $MMDC_VERSION"
  
  # Validate version
  if [ "$MMDC_MAJOR" -ge "$MIN_MMDC_VERSION" ]; then
    print_success "Version check passed (>= $MIN_MMDC_VERSION.0.0)"
    echo ""
    print_info "Installation complete. mermaid-cli is ready to use."
    echo ""
    echo "Test rendering:"
    echo "  cd \$SKILL_DIR"
    echo "  mmdc -i assets/architecture.mmd -o test-output.svg"
    exit 0
  else
    print_warning "Version $MMDC_VERSION is too old (need >= $MIN_MMDC_VERSION.0.0)"
    print_info "Upgrading to latest version..."
    npm install -g @mermaid-js/mermaid-cli@latest
    
    # Re-check version
    NEW_VERSION=$(mmdc --version 2>/dev/null | head -1 || echo "unknown")
    print_success "Upgraded to version $NEW_VERSION"
    exit 0
  fi
else
  print_info "mmdc not found. Installing..."
fi

###############################################################################
# Install mermaid-cli
###############################################################################

print_info "Installing @mermaid-js/mermaid-cli globally..."
echo ""

if npm install -g @mermaid-js/mermaid-cli; then
  echo ""
  print_success "Installation successful"
else
  echo ""
  print_error "Installation failed"
  echo ""
  echo "Troubleshooting:"
  echo "  1. Check npm permissions:"
  echo "     npm config get prefix"
  echo "     (Should be a writable directory)"
  echo ""
  echo "  2. Try with sudo (not recommended):"
  echo "     sudo npm install -g @mermaid-js/mermaid-cli"
  echo ""
  echo "  3. Fix npm permissions (recommended):"
  echo "     mkdir -p ~/.npm-global"
  echo "     npm config set prefix ~/.npm-global"
  echo "     echo 'export PATH=~/.npm-global/bin:\$PATH' >> ~/.bashrc"
  echo "     source ~/.bashrc"
  echo "     npm install -g @mermaid-js/mermaid-cli"
  echo ""
  exit 1
fi

###############################################################################
# Verify Installation
###############################################################################

print_info "Verifying installation..."

if ! command -v mmdc &> /dev/null; then
  print_error "mmdc not found after installation"
  echo ""
  echo "Possible causes:"
  echo "  - npm global bin directory not in PATH"
  echo "  - Installation completed but shell needs refresh"
  echo ""
  echo "Try:"
  echo "  1. Restart your terminal"
  echo "  2. Check PATH: echo \$PATH | grep npm"
  echo "  3. Find mmdc: npm list -g @mermaid-js/mermaid-cli"
  exit 1
fi

INSTALLED_VERSION=$(mmdc --version 2>/dev/null | head -1 || echo "unknown")
print_success "mmdc installed: version $INSTALLED_VERSION"

# Validate version
INSTALLED_MAJOR=$(echo "$INSTALLED_VERSION" | cut -d'.' -f1)
if [ "$INSTALLED_MAJOR" -ge "$MIN_MMDC_VERSION" ]; then
  print_success "Version check passed (>= $MIN_MMDC_VERSION.0.0)"
else
  print_error "Version $INSTALLED_VERSION is too old (need >= $MIN_MMDC_VERSION.0.0)"
  echo "  Try: npm install -g @mermaid-js/mermaid-cli@latest"
  exit 1
fi

###############################################################################
# Success
###############################################################################

echo ""
print_success "✨ All dependencies installed and verified ✨"
echo ""
echo "Next steps:"
echo "  1. Test rendering:"
echo "     cd \$SKILL_DIR"
echo "     mmdc -i assets/architecture.mmd -o test-output.svg"
echo ""
echo "  2. Generate diagrams:"
echo "     node scripts/generate.mjs --content content.json --out output-dir"
echo ""
echo "  3. Validate output:"
echo "     node scripts/validate.mjs --dir output-dir"
echo ""
