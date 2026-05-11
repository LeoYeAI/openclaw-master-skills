#!/bin/bash

# Batch Proxy Update Template
#
# This script updates proxy configuration for multiple NST profiles at once.
#
# Usage:
#   ./batch-proxy-update.sh <profile-names-or-ids> [options]
#
# Arguments:
#   <profile-names-or-ids>    Space or comma-separated profile names or IDs
#
# Options:
#   --proxy-host <host>       Proxy server host (required)
#   --proxy-port <port>       Proxy server port (required)
#   --proxy-type <type>       Proxy type (http|https|socks5, default: http)
#   --proxy-username <user>   Proxy username (optional)
#   --proxy-password <pass>   Proxy password (optional)
#   --reset                   Reset proxy instead of updating
#
# Examples:
#   # Update proxy for multiple profiles
#   ./batch-proxy-update.sh "id1 id2 id3" \
#     --proxy-host proxy.example.com \
#     --proxy-port 8080
#
#   # Update proxy with authentication
#   ./batch-proxy-update.sh "profile1,profile2,profile3" \
#     --proxy-host proxy.example.com \
#     --proxy-port 8080 \
#     --proxy-username user \
#     --proxy-password pass
#
#   # Update proxy type
#   ./batch-proxy-update.sh "id1 id2" \
#     --proxy-host proxy.example.com \
#     --proxy-port 1080 \
#     --proxy-type socks5
#
#   # Reset proxy for multiple profiles
#   ./batch-proxy-update.sh "id1 id2 id3" --reset

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

warn() {
  echo -e "${BLUE}⚠ $1${NC}"
}

# Check if nstbrowser-ai-agent is installed
if ! command -v nstbrowser-ai-agent &> /dev/null; then
  error "nstbrowser-ai-agent is not installed. Run: npm install -g nstbrowser-ai-agent"
fi

# Parse arguments
PROFILE_IDS=""
PROXY_HOST=""
PROXY_PORT=""
PROXY_TYPE="http"
PROXY_USERNAME=""
PROXY_PASSWORD=""
RESET_MODE=false

if [ $# -eq 0 ]; then
  error "Profile names or IDs are required. Usage: $0 <profile-names-or-ids> [options]"
fi

PROFILE_IDS="$1"
shift

while [ $# -gt 0 ]; do
  case "$1" in
    --proxy-host)
      PROXY_HOST="$2"
      shift 2
      ;;
    --proxy-port)
      PROXY_PORT="$2"
      shift 2
      ;;
    --proxy-type)
      PROXY_TYPE="$2"
      shift 2
      ;;
    --proxy-username)
      PROXY_USERNAME="$2"
      shift 2
      ;;
    --proxy-password)
      PROXY_PASSWORD="$2"
      shift 2
      ;;
    --reset)
      RESET_MODE=true
      shift
      ;;
    *)
      error "Unknown option: $1"
      ;;
  esac
done

# Validate inputs
if [ -z "$PROFILE_IDS" ]; then
  error "Profile IDs cannot be empty"
fi

if [ "$RESET_MODE" = false ]; then
  if [ -z "$PROXY_HOST" ] || [ -z "$PROXY_PORT" ]; then
    error "Proxy host and port are required (or use --reset to reset proxy)"
  fi
fi

# Parse profile IDs (handle both space and comma separation)
PROFILE_IDS=$(echo "$PROFILE_IDS" | tr ',' ' ')
IFS=' ' read -ra PROFILE_ARRAY <<< "$PROFILE_IDS"

info "Processing ${#PROFILE_ARRAY[@]} profiles..."

# Check NST API connectivity
info "Checking NST API connectivity..."
if ! nstbrowser-ai-agent profile list &> /dev/null; then
  error "Failed to connect to NST API. Check NST_API_KEY, NST_HOST, and NST_PORT environment variables."
fi
success "NST API is accessible"

# Resolve profile names to IDs
RESOLVED_IDS=()
info "Resolving profile IDs..."
for profile in "${PROFILE_ARRAY[@]}"; do
  profile=$(echo "$profile" | xargs)  # Trim whitespace
  
  # Check if it's already an ID (UUID format)
  if [[ "$profile" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
    RESOLVED_IDS+=("$profile")
    success "Profile ID: $profile"
  else
    # Try to resolve name to ID
    PROFILE_ID=$(nstbrowser-ai-agent profile list --json | jq -r ".[] | select(.name == \"$profile\") | .profileId")
    if [ -n "$PROFILE_ID" ]; then
      RESOLVED_IDS+=("$PROFILE_ID")
      success "Resolved '$profile' to ID: $PROFILE_ID"
    else
      warn "Profile not found: $profile (skipping)"
    fi
  fi
done

if [ ${#RESOLVED_IDS[@]} -eq 0 ]; then
  error "No valid profiles found"
fi

info "Found ${#RESOLVED_IDS[@]} valid profiles"

# Perform batch operation
if [ "$RESET_MODE" = true ]; then
  # Reset proxy
  info "Resetting proxy for ${#RESOLVED_IDS[@]} profiles..."
  
  if nstbrowser-ai-agent profile proxy batch-reset "${RESOLVED_IDS[@]}"; then
    success "Batch proxy reset completed"
  else
    error "Batch proxy reset failed"
  fi
else
  # Update proxy
  info "Updating proxy for ${#RESOLVED_IDS[@]} profiles..."
  
  # Build update command
  UPDATE_CMD="nstbrowser-ai-agent profile proxy batch-update ${RESOLVED_IDS[*]}"
  UPDATE_CMD="$UPDATE_CMD --proxy-host $PROXY_HOST"
  UPDATE_CMD="$UPDATE_CMD --proxy-port $PROXY_PORT"
  UPDATE_CMD="$UPDATE_CMD --proxy-type $PROXY_TYPE"
  
  if [ -n "$PROXY_USERNAME" ]; then
    UPDATE_CMD="$UPDATE_CMD --proxy-username $PROXY_USERNAME"
  fi
  
  if [ -n "$PROXY_PASSWORD" ]; then
    UPDATE_CMD="$UPDATE_CMD --proxy-password $PROXY_PASSWORD"
  fi
  
  if eval "$UPDATE_CMD"; then
    success "Batch proxy update completed"
  else
    error "Batch proxy update failed"
  fi
fi

# Verify updates
info "Verifying updates..."
SUCCESS_COUNT=0
FAIL_COUNT=0

for profile_id in "${RESOLVED_IDS[@]}"; do
  if nstbrowser-ai-agent profile proxy show "$profile_id" &> /dev/null; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    warn "Failed to verify profile: $profile_id"
  fi
done

# Display summary
echo ""
info "Summary:"
echo "  Total profiles: ${#RESOLVED_IDS[@]}"
echo "  Successful: $SUCCESS_COUNT"
echo "  Failed: $FAIL_COUNT"

if [ "$RESET_MODE" = true ]; then
  success "Proxy reset complete!"
else
  success "Proxy update complete!"
  echo ""
  echo "Proxy configuration:"
  echo "  Host: $PROXY_HOST"
  echo "  Port: $PROXY_PORT"
  echo "  Type: $PROXY_TYPE"
  if [ -n "$PROXY_USERNAME" ]; then
    echo "  Username: $PROXY_USERNAME"
  fi
fi

# Display sample verification command
echo ""
echo "Verify proxy configuration with:"
echo "  nstbrowser-ai-agent profile proxy show ${RESOLVED_IDS[0]}"
