#!/bin/bash

# Profile Setup Template
# 
# This script creates and configures an NST profile with optional proxy, tags, and group settings.
#
# Usage:
#   ./profile-setup.sh <profile-name> [options]
#
# Options:
#   --proxy-host <host>       Proxy server host
#   --proxy-port <port>       Proxy server port
#   --proxy-type <type>       Proxy type (http|https|socks5)
#   --proxy-username <user>   Proxy username
#   --proxy-password <pass>   Proxy password
#   --tags <tag1,tag2>        Comma-separated tags
#   --group-id <id>           Group ID
#   --platform <platform>     Platform (Windows|macOS|Linux)
#   --kernel <version>        Kernel version (e.g., 126)
#
# Examples:
#   # Create basic profile
#   ./profile-setup.sh my-profile
#
#   # Create profile with proxy
#   ./profile-setup.sh my-profile \
#     --proxy-host proxy.example.com \
#     --proxy-port 8080 \
#     --proxy-type http
#
#   # Create profile with proxy authentication and tags
#   ./profile-setup.sh my-profile \
#     --proxy-host proxy.example.com \
#     --proxy-port 8080 \
#     --proxy-username user \
#     --proxy-password pass \
#     --tags "testing,automation"
#
#   # Create profile with all options
#   ./profile-setup.sh my-profile \
#     --proxy-host proxy.example.com \
#     --proxy-port 8080 \
#     --proxy-type socks5 \
#     --proxy-username user \
#     --proxy-password pass \
#     --tags "production,us-east" \
#     --group-id abc123 \
#     --platform Windows \
#     --kernel 126

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if NO_COLOR is set
if [ -n "$NO_COLOR" ]; then
  RED=''
  GREEN=''
  YELLOW=''
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

# Check if nstbrowser-ai-agent is installed
if ! command -v nstbrowser-ai-agent &> /dev/null; then
  error "nstbrowser-ai-agent is not installed. Run: npm install -g nstbrowser-ai-agent"
fi

# Parse arguments
PROFILE_NAME=""
PROXY_HOST=""
PROXY_PORT=""
PROXY_TYPE=""
PROXY_USERNAME=""
PROXY_PASSWORD=""
TAGS=""
GROUP_ID=""
PLATFORM=""
KERNEL=""

if [ $# -eq 0 ]; then
  error "Profile name is required. Usage: $0 <profile-name> [options]"
fi

PROFILE_NAME="$1"
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
    --tags)
      TAGS="$2"
      shift 2
      ;;
    --group-id)
      GROUP_ID="$2"
      shift 2
      ;;
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --kernel)
      KERNEL="$2"
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      ;;
  esac
done

# Validate profile name
if [ -z "$PROFILE_NAME" ]; then
  error "Profile name cannot be empty"
fi

info "Setting up profile: $PROFILE_NAME"

# Check NST API connectivity
info "Checking NST API connectivity..."
if ! nstbrowser-ai-agent profile list &> /dev/null; then
  error "Failed to connect to NST API. Check NST_API_KEY, NST_HOST, and NST_PORT environment variables."
fi
success "NST API is accessible"

# Build create command
CREATE_CMD="nstbrowser-ai-agent profile create \"$PROFILE_NAME\""

if [ -n "$PLATFORM" ]; then
  CREATE_CMD="$CREATE_CMD --platform $PLATFORM"
fi

if [ -n "$KERNEL" ]; then
  CREATE_CMD="$CREATE_CMD --kernel $KERNEL"
fi

if [ -n "$GROUP_ID" ]; then
  CREATE_CMD="$CREATE_CMD --group-id $GROUP_ID"
fi

# Add proxy options if provided
if [ -n "$PROXY_HOST" ] && [ -n "$PROXY_PORT" ]; then
  CREATE_CMD="$CREATE_CMD --proxy-host $PROXY_HOST --proxy-port $PROXY_PORT"
  
  if [ -n "$PROXY_TYPE" ]; then
    CREATE_CMD="$CREATE_CMD --proxy-type $PROXY_TYPE"
  fi
  
  if [ -n "$PROXY_USERNAME" ]; then
    CREATE_CMD="$CREATE_CMD --proxy-username $PROXY_USERNAME"
  fi
  
  if [ -n "$PROXY_PASSWORD" ]; then
    CREATE_CMD="$CREATE_CMD --proxy-password $PROXY_PASSWORD"
  fi
fi

# Create profile
info "Creating profile..."
if eval "$CREATE_CMD"; then
  success "Profile created successfully"
else
  error "Failed to create profile"
fi

# Get profile ID
info "Retrieving profile ID..."
PROFILE_ID=$(nstbrowser-ai-agent profile list --json | jq -r ".[] | select(.name == \"$PROFILE_NAME\") | .profileId")

if [ -z "$PROFILE_ID" ]; then
  error "Failed to retrieve profile ID"
fi
success "Profile ID: $PROFILE_ID"

# Add tags if provided
if [ -n "$TAGS" ]; then
  info "Adding tags..."
  IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
  for tag in "${TAG_ARRAY[@]}"; do
    tag=$(echo "$tag" | xargs)  # Trim whitespace
    if nstbrowser-ai-agent profile tags create "$PROFILE_ID" "$tag"; then
      success "Added tag: $tag"
    else
      error "Failed to add tag: $tag"
    fi
  done
fi

# Verify profile creation
info "Verifying profile..."
if nstbrowser-ai-agent profile show "$PROFILE_NAME" &> /dev/null; then
  success "Profile verification successful"
else
  error "Profile verification failed"
fi

# Display profile details
info "Profile details:"
nstbrowser-ai-agent profile show "$PROFILE_NAME"

# Display proxy details if configured
if [ -n "$PROXY_HOST" ] && [ -n "$PROXY_PORT" ]; then
  info "Proxy configuration:"
  nstbrowser-ai-agent profile proxy show "$PROFILE_NAME"
fi

success "Profile setup complete!"
echo ""
echo "You can now use this profile with:"
echo "  nstbrowser-ai-agent --profile \"$PROFILE_NAME\" browser start"
echo "  nstbrowser-ai-agent --profile \"$PROFILE_NAME\" open https://example.com"
