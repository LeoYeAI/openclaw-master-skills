#!/bin/bash
# start-subprocess.sh - Register child agent on Solvr with protocol-08 naming
# Usage: ./start-subprocess.sh <instance_name>
#
# Implements protocol-08-child-naming:
#   Pattern: {PARENT_SOLVR_NAME}_child_{INSTANCE_NAME}
#
# Prerequisites:
#   - SOLVR_API_KEY set (parent's key, for registration)
#   - Parent identity configured

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTANCE_NAME="${1:-}"
SOLVR_API_KEY="${SOLVR_API_KEY:-}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[spawn-child]${NC} $1"; }
warn() { echo -e "${YELLOW}[spawn-child]${NC} $1"; }
error() { echo -e "${RED}[spawn-child]${NC} $1" >&2; }

usage() {
  cat << EOF
Usage: $0 <instance_name>

Register a child agent on Solvr with protocol-08 naming convention.

Pattern: {PARENT_SOLVR_NAME}_child_{INSTANCE_NAME}
Example: ClaudiusThePirateEmperor_child_dana

Arguments:
  instance_name   Child instance name (lowercase, alphanumeric + underscore, max 32 chars)

Environment:
  SOLVR_API_KEY   Parent's Solvr API key (required)
  SOLVR_API_URL   Solvr API base URL (default: https://api.solvr.dev/v1)

Output:
  Prints child's Solvr API key on success (for injection into child config)
EOF
  exit 1
}

# Validate instance name (protocol-08 constraints)
validate_instance_name() {
  local name="$1"
  
  if [ -z "$name" ]; then
    error "Instance name is required"
    return 1
  fi
  
  if [ ${#name} -gt 32 ]; then
    error "Instance name must be max 32 characters (got ${#name})"
    return 1
  fi
  
  if ! echo "$name" | grep -qE '^[a-z0-9_]+$'; then
    error "Instance name must be lowercase alphanumeric + underscore only"
    error "Got: $name"
    return 1
  fi
  
  return 0
}

# Get parent Solvr name from /me endpoint
get_parent_solvr_name() {
  local response
  response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    "$SOLVR_API_URL/me")
  
  local http_code=$(echo "$response" | tail -n1)
  local body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" != "200" ]; then
    error "Failed to get parent identity from Solvr (HTTP $http_code)"
    error "Response: $body"
    return 1
  fi
  
  local name=$(echo "$body" | jq -r '.agent.name // .name // empty')
  
  if [ -z "$name" ]; then
    error "Could not extract parent name from Solvr response"
    error "Response: $body"
    return 1
  fi
  
  echo "$name"
}

# Check if name is already taken
check_name_available() {
  local name="$1"
  
  # Try to get agent by name
  local response
  response=$(curl -s -w "\n%{http_code}" \
    "$SOLVR_API_URL/agents/$name" 2>/dev/null || echo -e "\n404")
  
  local http_code=$(echo "$response" | tail -n1)
  
  # 404 means available, anything else means taken or error
  if [ "$http_code" == "404" ]; then
    return 0  # Available
  else
    return 1  # Taken or error
  fi
}

# Register child on Solvr
register_child() {
  local child_name="$1"
  
  log "Registering: $child_name"
  
  local response
  response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$child_name\"}" \
    "$SOLVR_API_URL/agents/register")
  
  local http_code=$(echo "$response" | tail -n1)
  local body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    error "Failed to register child (HTTP $http_code)"
    error "Response: $body"
    return 1
  fi
  
  # Extract API key from response
  local api_key=$(echo "$body" | jq -r '.api_key // .apiKey // empty')
  
  if [ -z "$api_key" ]; then
    error "No API key in response"
    error "Response: $body"
    return 1
  fi
  
  echo "$api_key"
}

# Main
main() {
  if [ -z "$INSTANCE_NAME" ]; then
    usage
  fi
  
  # Validate prerequisites
  if [ -z "$SOLVR_API_KEY" ]; then
    error "SOLVR_API_KEY environment variable is required"
    exit 1
  fi
  
  # Validate instance name
  if ! validate_instance_name "$INSTANCE_NAME"; then
    exit 1
  fi
  
  log "Instance name: $INSTANCE_NAME"
  
  # Get parent name
  log "Getting parent identity from Solvr..."
  PARENT_NAME=$(get_parent_solvr_name)
  if [ -z "$PARENT_NAME" ]; then
    exit 1
  fi
  log "Parent: $PARENT_NAME"
  
  # Build child name (protocol-08)
  CHILD_NAME="${PARENT_NAME}_child_${INSTANCE_NAME}"
  log "Child name: $CHILD_NAME"
  
  # Check availability
  log "Checking name availability..."
  if ! check_name_available "$CHILD_NAME"; then
    warn "Name '$CHILD_NAME' may be taken, trying with suffix..."
    
    # Try with numeric suffix
    for i in 2 3 4 5; do
      CHILD_NAME="${PARENT_NAME}_child_${INSTANCE_NAME}_${i}"
      if check_name_available "$CHILD_NAME"; then
        log "Using: $CHILD_NAME"
        break
      fi
    done
    
    if ! check_name_available "$CHILD_NAME"; then
      error "Could not find available name after 5 attempts"
      exit 1
    fi
  fi
  
  # Register
  log "Registering child on Solvr..."
  CHILD_API_KEY=$(register_child "$CHILD_NAME")
  
  if [ -z "$CHILD_API_KEY" ]; then
    error "Registration failed"
    exit 1
  fi
  
  log "✅ Child registered successfully!"
  log ""
  log "Child Solvr Name: $CHILD_NAME"
  log "Child API Key:    $CHILD_API_KEY"
  log ""
  log "Store in child's OpenClaw config:"
  log "  skills.entries.proactive-solvr.apiKey = $CHILD_API_KEY"
  log "  skills.entries.proactive-amcp.config.parentSolvrName = $PARENT_NAME"
  log ""
  
  # Output just the key for scripting
  echo ""
  echo "CHILD_SOLVR_NAME=$CHILD_NAME"
  echo "CHILD_API_KEY=$CHILD_API_KEY"
  echo "PARENT_SOLVR_NAME=$PARENT_NAME"
}

main "$@"
