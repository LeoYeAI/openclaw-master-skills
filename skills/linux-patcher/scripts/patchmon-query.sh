#!/bin/bash
# patchmon-query.sh - Query PatchMon for hosts needing updates
# Usage: ./patchmon-query.sh [--output-config config-file.conf]

set -e

# Load PatchMon credentials
PATCHMON_CONFIG="${PATCHMON_CONFIG:-$HOME/.patchmon-credentials.conf}"

if [ ! -f "$PATCHMON_CONFIG" ]; then
    echo "ERROR: PatchMon credentials not found: $PATCHMON_CONFIG"
    echo ""
    echo "Create the file with:"
    echo "  PATCHMON_URL=https://patchmon.example.com"
    echo "  PATCHMON_USERNAME=admin"
    echo "  PATCHMON_PASSWORD=your-password"
    exit 1
fi

source "$PATCHMON_CONFIG"

# Validate config
if [ -z "$PATCHMON_URL" ] || [ -z "$PATCHMON_USERNAME" ] || [ -z "$PATCHMON_PASSWORD" ]; then
    echo "ERROR: Incomplete PatchMon configuration"
    echo "Required: PATCHMON_URL, PATCHMON_USERNAME, PATCHMON_PASSWORD"
    exit 1
fi

# Parse arguments
OUTPUT_CONFIG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-config)
            OUTPUT_CONFIG="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Authenticate with PatchMon
echo "Authenticating with PatchMon..."
TOKEN=$(curl -s -k -X POST "$PATCHMON_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$PATCHMON_USERNAME\",\"password\":\"$PATCHMON_PASSWORD\"}" \
    | jq -r '.token // .accessToken // empty')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "ERROR: Failed to authenticate with PatchMon"
    echo "Check credentials in: $PATCHMON_CONFIG"
    exit 1
fi

echo "✓ Authenticated successfully"
echo ""

# Query hosts needing updates
echo "Querying hosts from PatchMon..."
HOSTS_JSON=$(curl -s -k "$PATCHMON_URL/api/v1/dashboard/hosts" \
    -H "Authorization: Bearer $TOKEN")

# Parse hosts needing updates
NEEDS_UPDATE=$(echo "$HOSTS_JSON" | jq -r '.[] | select(.needsUpdates == true or .outdatedPackages > 0) | @json')

if [ -z "$NEEDS_UPDATE" ]; then
    echo "✓ All hosts are up to date!"
    exit 0
fi

# Count hosts
HOST_COUNT=$(echo "$NEEDS_UPDATE" | wc -l)
echo "Found $HOST_COUNT host(s) needing updates:"
echo ""

# Display hosts
echo "$NEEDS_UPDATE" | jq -r '"  - \(.hostname) (\(.outdatedPackages) packages, \(.securityUpdates // 0) security)"'
echo ""

# Generate config file if requested
if [ -n "$OUTPUT_CONFIG" ]; then
    echo "Generating config file: $OUTPUT_CONFIG"
    
    cat > "$OUTPUT_CONFIG" << 'EOF'
#!/bin/bash
# Auto-generated PatchMon host configuration
# Generated: $(date)

# Host definitions parsed from PatchMon
HOSTS=(
EOF
    
    # Parse each host and add to config
    echo "$NEEDS_UPDATE" | jq -r '"\(.hostname),\(.sshUser // ""),\(.dockerPath // "")"' | while read -r line; do
        echo "    \"$line\"" >> "$OUTPUT_CONFIG"
    done
    
    cat >> "$OUTPUT_CONFIG" << 'EOF'
)

# Update mode
UPDATE_MODE="auto"  # auto, host-only, or full

# Skip Docker updates (even if Docker is detected)
SKIP_DOCKER="${SKIP_DOCKER:-false}"

# Dry run mode
DRY_RUN="${DRY_RUN:-false}"
EOF
    
    chmod +x "$OUTPUT_CONFIG"
    echo "✓ Config saved to: $OUTPUT_CONFIG"
    echo ""
    echo "Review and run with:"
    echo "  cat $OUTPUT_CONFIG"
    echo "  ./patch-multiple.sh $OUTPUT_CONFIG"
fi

# Output JSON for programmatic use
if [ -z "$OUTPUT_CONFIG" ]; then
    echo "$NEEDS_UPDATE"
fi
