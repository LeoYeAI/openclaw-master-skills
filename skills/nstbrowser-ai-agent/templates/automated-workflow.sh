#!/bin/bash

# Automated Workflow Template
#
# This script demonstrates a complete automated workflow using nstbrowser-ai-agent
# with NST profiles, including profile selection, browser launch, navigation,
# interaction, and state persistence.
#
# Usage:
#   ./automated-workflow.sh [profile-name]
#
# Arguments:
#   profile-name    Profile name (required)
#
# Environment Variables:
#   NST_API_KEY     NST API key (required)
#   NST_HOST        NST host (default: 127.0.0.1)
#   NST_PORT        NST port (default: 8848)
#
# Example:
#   ./automated-workflow.sh "my-profile"
#
#   # Complete example with environment setup
#   export NST_API_KEY="your-api-key"
#   export NST_HOST="127.0.0.1"
#   export NST_PORT="8848"
#   ./automated-workflow.sh "production-profile"

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if NO_COLOR is set
if [ -n "$NO_COLOR" ]; then
  RED=''
  GREEN=''
  YELLOW=''
  BLUE=''
  NC=''
fi

# Helper functions
error() {
  echo -e "${RED}✗ Error: $1${NC}" >&2
  exit 1
}

success() {
  echo -e "${GREEN}✓ $1${NC}"
}

info() {
  echo -e "${YELLOW}→ $1${NC}"
}

step() {
  echo -e "${BLUE}[$1] $2${NC}"
}

# Check if nstbrowser-ai-agent is installed
if ! command -v nstbrowser-ai-agent &> /dev/null; then
  error "nstbrowser-ai-agent is not installed. Run: npm install -g nstbrowser-ai-agent"
fi

# Configuration
PROFILE_NAME="$1"
TARGET_URL="https://example.com"
SCREENSHOT_PATH="./workflow-screenshot.png"
SNAPSHOT_PATH="./workflow-snapshot.json"

# Validate environment
step "1/10" "Validating environment..."

if [ -z "$NST_API_KEY" ]; then
  error "NST_API_KEY environment variable is required"
fi

if [ -z "$PROFILE_NAME" ]; then
  error "Profile name is required. Usage: $0 <profile-name>"
fi

success "Environment validated"

# Check NST API connectivity
step "2/10" "Checking NST API connectivity..."

if ! nstbrowser-ai-agent profile list &> /dev/null; then
  error "Failed to connect to NST API. Check NST_API_KEY, NST_HOST, and NST_PORT."
fi

success "NST API is accessible"

# List available profiles
step "3/10" "Listing available profiles..."

PROFILE_COUNT=$(nstbrowser-ai-agent profile list --json | jq '. | length')
info "Found $PROFILE_COUNT profiles"

# Verify profile exists
step "4/10" "Verifying profile: $PROFILE_NAME..."

if ! nstbrowser-ai-agent profile show "$PROFILE_NAME" &> /dev/null; then
  error "Profile not found: $PROFILE_NAME"
fi

PROFILE_ID=$(nstbrowser-ai-agent profile list --json | jq -r ".[] | select(.name == \"$PROFILE_NAME\") | .profileId")
success "Profile verified (ID: $PROFILE_ID)"

# Display profile details
info "Profile details:"
nstbrowser-ai-agent profile show "$PROFILE_NAME"

# Check if browser is already running
step "5/10" "Checking browser status..."

BROWSER_RUNNING=$(nstbrowser-ai-agent browser list | grep -c "$PROFILE_NAME" || true)

if [ "$BROWSER_RUNNING" -gt 0 ]; then
  info "Browser already running, stopping..."
  nstbrowser-ai-agent browser stop "$PROFILE_NAME"
  sleep 2
fi

success "Browser ready to start"

# Start browser with profile
step "6/10" "Starting browser with profile..."

if nstbrowser-ai-agent --profile "$PROFILE_NAME" browser start; then
  success "Browser started successfully"
else
  error "Failed to start browser"
fi

# Wait for browser to be ready
sleep 3

# Get debugger URL
DEBUGGER_URL=$(nstbrowser-ai-agent browser debugger "$PROFILE_NAME" --json | jq -r '.debuggerUrl')
info "Debugger URL: $DEBUGGER_URL"

# Navigate to target URL
step "7/10" "Navigating to $TARGET_URL..."

if nstbrowser-ai-agent --profile "$PROFILE_NAME" open "$TARGET_URL"; then
  success "Navigation successful"
else
  error "Navigation failed"
fi

# Wait for page to load
sleep 2

# Take snapshot
step "8/10" "Taking page snapshot..."

if nstbrowser-ai-agent --profile "$PROFILE_NAME" snapshot --json > "$SNAPSHOT_PATH"; then
  success "Snapshot saved to $SNAPSHOT_PATH"
  
  # Display snapshot info
  PAGE_TITLE=$(jq -r '.title' "$SNAPSHOT_PATH")
  PAGE_URL=$(jq -r '.url' "$SNAPSHOT_PATH")
  REF_COUNT=$(jq '.refs | length' "$SNAPSHOT_PATH")
  
  info "Page title: $PAGE_TITLE"
  info "Page URL: $PAGE_URL"
  info "Available refs: $REF_COUNT"
else
  error "Failed to take snapshot"
fi

# Take screenshot
step "9/10" "Taking screenshot..."

if nstbrowser-ai-agent --profile "$PROFILE_NAME" screenshot --output "$SCREENSHOT_PATH"; then
  success "Screenshot saved to $SCREENSHOT_PATH"
else
  error "Failed to take screenshot"
fi

# Demonstrate interaction (example: find and display heading)
info "Demonstrating page interaction..."

# Extract heading from snapshot
HEADING=$(jq -r '.refs[] | select(.tag == "h1") | .text' "$SNAPSHOT_PATH" | head -n 1)

if [ -n "$HEADING" ]; then
  success "Found heading: $HEADING"
else
  info "No h1 heading found on page"
fi

# Demonstrate state persistence
info "Demonstrating state persistence..."

# The profile automatically persists:
# - Cookies
# - Local storage
# - Session storage
# - Cache
# - Fingerprint

success "State will be preserved for next session"

# Stop browser
step "10/10" "Stopping browser..."

if nstbrowser-ai-agent browser stop "$PROFILE_NAME"; then
  success "Browser stopped successfully"
else
  error "Failed to stop browser"
fi

# Display results summary
echo ""
success "Workflow completed successfully!"
echo ""
info "Results:"
echo "  Profile: $PROFILE_NAME"
echo "  Profile ID: $PROFILE_ID"
echo "  Target URL: $TARGET_URL"
echo "  Page Title: $PAGE_TITLE"
echo "  Screenshot: $SCREENSHOT_PATH"
echo "  Snapshot: $SNAPSHOT_PATH"
echo ""
info "Next steps:"
echo "  1. View screenshot: open $SCREENSHOT_PATH"
echo "  2. Inspect snapshot: cat $SNAPSHOT_PATH | jq"
echo "  3. Restart browser: nstbrowser-ai-agent --profile \"$PROFILE_NAME\" browser start"
echo "  4. Continue automation: nstbrowser-ai-agent --profile \"$PROFILE_NAME\" open <url>"
echo ""
info "State persistence:"
echo "  All cookies, storage, and session data are preserved in the profile."
echo "  Next time you start the browser with this profile, you'll be in the same state."
echo ""
success "Workflow template complete!"
