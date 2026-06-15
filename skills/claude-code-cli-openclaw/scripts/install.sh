#!/bin/bash

# Claude Code CLI for OpenClaw - Installation Script
# Part of ProSkills.md OpenClaw Skills Collection
# Author: Matrix Zion (ProSkillsMD)
# Homepage: https://proskills.md
# Version: 1.0.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}  Claude Code CLI for OpenClaw - Installation${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    print_success "npm found: $(npm --version)"
    
    echo ""
}

# Install Claude Code CLI
install_claude_code() {
    print_info "Installing Claude Code CLI globally..."
    
    if npm install -g @anthropic-ai/claude-code; then
        print_success "Claude Code CLI installed successfully"
    else
        print_error "Failed to install Claude Code CLI"
        exit 1
    fi
    
    echo ""
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    # Check if claude command exists
    if ! command -v claude &> /dev/null; then
        print_error "claude command not found in PATH"
        print_warning "You may need to add npm global bin to PATH:"
        echo -e "  ${YELLOW}export PATH=\"\$PATH:\$(npm bin -g)\"${NC}"
        exit 1
    fi
    print_success "claude command found: $(which claude)"
    
    # Check version
    CLAUDE_VERSION=$(claude --version 2>&1 || echo "unknown")
    print_success "Claude Code version: $CLAUDE_VERSION"
    
    echo ""
}

# Setup environment variables
setup_environment() {
    print_info "Setting up environment..."
    
    # Check if token is already set
    if [ -n "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
        print_success "CLAUDE_CODE_OAUTH_TOKEN already set in environment"
        print_warning "If you need to update it, run: claude setup-token"
        echo ""
        return
    fi
    
    print_warning "CLAUDE_CODE_OAUTH_TOKEN not found in environment"
    echo ""
    echo -e "${YELLOW}You need to authenticate with Claude Max subscription:${NC}"
    echo -e "  1. Run: ${GREEN}claude setup-token${NC}"
    echo -e "  2. Follow the browser OAuth flow"
    echo -e "  3. Store the token persistently:"
    echo ""
    echo -e "${BLUE}Option 1 (Recommended): Shell RC files${NC}"
    echo -e "  ${GREEN}echo 'export CLAUDE_CODE_OAUTH_TOKEN=YOUR_TOKEN_HERE' >> ~/.bashrc${NC}"
    echo -e "  ${GREEN}echo 'export CLAUDE_CODE_OAUTH_TOKEN=YOUR_TOKEN_HERE' >> ~/.profile${NC}"
    echo -e "  ${GREEN}source ~/.bashrc${NC}"
    echo ""
    echo -e "${BLUE}Option 2: System-wide${NC}"
    echo -e "  ${GREEN}echo 'CLAUDE_CODE_OAUTH_TOKEN=YOUR_TOKEN_HERE' | sudo tee -a /etc/environment${NC}"
    echo ""
    echo -e "${BLUE}Option 3: OpenClaw config only${NC}"
    echo -e "  Add to ~/.openclaw/config.patch (see SKILL.md for details)"
    echo ""
    echo -e "${RED}🔒 SECURITY WARNING:${NC}"
    echo -e "  ${YELLOW}Never commit your token to git!${NC}"
    echo -e "  Add .env files to .gitignore"
    echo -e "  Store tokens in environment variables or secrets manager"
    echo ""
    
    read -p "Do you want to run 'claude setup-token' now? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Running claude setup-token..."
        print_warning "This requires a TTY terminal. Follow the prompts."
        echo ""
        
        if claude setup-token; then
            print_success "Authentication complete!"
            echo ""
            print_info "Now store the token persistently (see options above)"
        else
            print_error "Authentication failed. Try again manually: claude setup-token"
        fi
    else
        print_info "Skipping authentication. Run 'claude setup-token' manually when ready."
    fi
    
    echo ""
}

# Add PATH export to shell RC files (if needed)
setup_path() {
    NPM_BIN_PATH=$(npm bin -g 2>/dev/null || echo "")
    
    if [ -z "$NPM_BIN_PATH" ]; then
        print_warning "Could not determine npm global bin path"
        return
    fi
    
    # Check if PATH already contains npm bin
    if echo "$PATH" | grep -q "$NPM_BIN_PATH"; then
        print_success "npm global bin already in PATH"
        return
    fi
    
    print_info "Adding npm global bin to PATH..."
    
    # Add to .bashrc
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q "npm bin -g" "$HOME/.bashrc"; then
            echo 'export PATH="$PATH:$(npm bin -g)"' >> "$HOME/.bashrc"
            print_success "Added to ~/.bashrc"
        fi
    fi
    
    # Add to .profile
    if [ -f "$HOME/.profile" ]; then
        if ! grep -q "npm bin -g" "$HOME/.profile"; then
            echo 'export PATH="$PATH:$(npm bin -g)"' >> "$HOME/.profile"
            print_success "Added to ~/.profile"
        fi
    fi
    
    print_warning "Reload your shell or run: source ~/.bashrc"
    echo ""
}

# Print next steps
print_next_steps() {
    print_header
    echo -e "${GREEN}Installation Complete!${NC}\n"
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. ${GREEN}Authenticate${NC} (if not done): claude setup-token"
    echo -e "  2. ${GREEN}Configure OpenClaw${NC}: Add CLI backend to config.patch (see SKILL.md)"
    echo -e "  3. ${GREEN}Create project brain${NC}: Copy CLAUDE.md.template to your project"
    echo -e "  4. ${GREEN}Start coding${NC}: CLAUDE_CODE_OAUTH_TOKEN=\$token claude --print 'your task'"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo -e "  - Full guide: ${GREEN}cat SKILL.md${NC}"
    echo -e "  - Template: ${GREEN}cat templates/CLAUDE.md.template${NC}"
    echo ""
    echo -e "${BLUE}Quick Test:${NC}"
    echo -e "  ${GREEN}claude --version${NC}  # Verify installation"
    echo -e "  ${GREEN}echo \$CLAUDE_CODE_OAUTH_TOKEN${NC}  # Check token is set"
    echo ""
    echo -e "${YELLOW}Happy coding! 🚀${NC}\n"
}

# Main installation flow
main() {
    print_header
    
    check_prerequisites
    install_claude_code
    verify_installation
    setup_path
    setup_environment
    print_next_steps
}

# Run main function
main
