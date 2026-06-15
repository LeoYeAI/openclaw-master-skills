#!/bin/bash
# patch-auto.sh - Automatically patch hosts based on PatchMon
# Usage: ./patch-auto.sh [--skip-docker] [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
SKIP_DOCKER="false"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-docker)
            SKIP_DOCKER="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-docker] [--dry-run]"
            exit 1
            ;;
    esac
done

echo "========================================="
echo "Linux Patcher - Automatic Mode"
echo "========================================="
echo "Skip Docker: $SKIP_DOCKER"
echo "Dry Run: $DRY_RUN"
echo ""

# Step 1: Query PatchMon for hosts needing updates
echo "Step 1/3: Querying PatchMon..."
TEMP_CONFIG=$(mktemp)
if ! "$SCRIPT_DIR/patchmon-query.sh" --output-config "$TEMP_CONFIG"; then
    echo "ERROR: Failed to query PatchMon"
    rm -f "$TEMP_CONFIG"
    exit 1
fi

echo ""

# Check if any hosts need updates
if [ ! -f "$TEMP_CONFIG" ] || ! grep -q "HOSTS=(" "$TEMP_CONFIG"; then
    echo "✓ No hosts need updates (all up to date)"
    rm -f "$TEMP_CONFIG"
    exit 0
fi

# Step 2: Load config and process each host
echo "Step 2/3: Loading host list..."
source "$TEMP_CONFIG"

if [ ${#HOSTS[@]} -eq 0 ]; then
    echo "✓ No hosts need updates"
    rm -f "$TEMP_CONFIG"
    exit 0
fi

echo "Found ${#HOSTS[@]} host(s) to update"
echo ""

# Step 3: Patch each host
echo "Step 3/3: Patching hosts..."
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_HOSTS=()

for host_entry in "${HOSTS[@]}"; do
    # Parse host entry: hostname,user,docker_path
    IFS=',' read -r hostname ssh_user docker_path <<< "$host_entry"
    
    # Build SSH target
    if [ -n "$ssh_user" ]; then
        SSH_TARGET="$ssh_user@$hostname"
    else
        SSH_TARGET="$hostname"
    fi
    
    echo "Processing: $SSH_TARGET"
    echo "---"
    
    # Detect Docker if not specified
    HAS_DOCKER="false"
    if [ "$SKIP_DOCKER" = "false" ]; then
        echo "Checking for Docker..."
        if ssh "$SSH_TARGET" "command -v docker >/dev/null 2>&1"; then
            HAS_DOCKER="true"
            echo "✓ Docker detected"
            
            # Try to find docker-compose.yml if path not specified
            if [ -z "$docker_path" ]; then
                echo "Auto-detecting Docker Compose path..."
                docker_path=$(ssh "$SSH_TARGET" "
                    for path in \
                        /home/$ssh_user/Docker \
                        /home/$ssh_user/docker \
                        /opt/docker \
                        /srv/docker \
                        \$HOME/Docker \
                        \$HOME/docker; do
                        if [ -f \$path/docker-compose.yml ]; then
                            echo \$path
                            exit 0
                        fi
                    done
                " 2>/dev/null || echo "")
                
                if [ -n "$docker_path" ]; then
                    echo "✓ Found Docker Compose at: $docker_path"
                else
                    echo "⚠ Docker Compose not found (will skip Docker updates)"
                    HAS_DOCKER="false"
                fi
            fi
        else
            echo "Docker not installed (host-only mode)"
        fi
    else
        echo "Docker updates disabled by --skip-docker flag"
    fi
    
    echo ""
    
    # Execute update based on Docker detection
    if [ "$HAS_DOCKER" = "true" ] && [ -n "$docker_path" ]; then
        if DRY_RUN="$DRY_RUN" "$SCRIPT_DIR/patch-host-full.sh" "$SSH_TARGET" "$docker_path"; then
            ((SUCCESS_COUNT++))
            echo "✓ Full update successful"
        else
            ((FAIL_COUNT++))
            FAILED_HOSTS+=("$SSH_TARGET")
            echo "✗ Full update failed"
        fi
    else
        if DRY_RUN="$DRY_RUN" "$SCRIPT_DIR/patch-host-only.sh" "$SSH_TARGET"; then
            ((SUCCESS_COUNT++))
            echo "✓ Host-only update successful"
        else
            ((FAIL_COUNT++))
            FAILED_HOSTS+=("$SSH_TARGET")
            echo "✗ Host-only update failed"
        fi
    fi
    
    echo ""
done

# Cleanup
rm -f "$TEMP_CONFIG"

# Summary
echo "========================================="
echo "Automatic Update Summary"
echo "========================================="
echo "Total hosts: ${#HOSTS[@]}"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"

if [ $FAIL_COUNT -gt 0 ]; then
    echo ""
    echo "Failed hosts:"
    for failed_host in "${FAILED_HOSTS[@]}"; do
        echo "  - $failed_host"
    done
    exit 1
fi

echo ""
echo "✓ All hosts updated successfully"
