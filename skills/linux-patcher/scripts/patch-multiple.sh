#!/bin/bash
# patch-multiple.sh - Update multiple hosts from config file
# Usage: ./patch-multiple.sh config-file.conf

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 config-file.conf"
    echo "Example: $0 production-servers.conf"
    echo ""
    echo "See patch-hosts-config.example.sh for config format"
    exit 1
fi

CONFIG_FILE="$1"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Load configuration
source "$CONFIG_FILE"

# Validate config
if [ ${#HOSTS[@]} -eq 0 ]; then
    echo "ERROR: No hosts defined in config file"
    echo "Define HOSTS array in $CONFIG_FILE"
    exit 1
fi

if [ -z "$UPDATE_MODE" ]; then
    UPDATE_MODE="full"
fi

if [ -z "$DRY_RUN" ]; then
    DRY_RUN="false"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Linux Patcher - Batch Mode"
echo "========================================="
echo "Config: $CONFIG_FILE"
echo "Hosts: ${#HOSTS[@]}"
echo "Mode: $UPDATE_MODE"
echo "Dry Run: $DRY_RUN"
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
    
    # Execute update based on mode
    if [ "$UPDATE_MODE" = "host-only" ]; then
        if DRY_RUN="$DRY_RUN" "$SCRIPT_DIR/patch-host-only.sh" "$SSH_TARGET"; then
            ((SUCCESS_COUNT++))
            echo "✓ Success"
        else
            ((FAIL_COUNT++))
            FAILED_HOSTS+=("$SSH_TARGET")
            echo "✗ Failed"
        fi
    elif [ "$UPDATE_MODE" = "full" ]; then
        if DRY_RUN="$DRY_RUN" "$SCRIPT_DIR/patch-host-full.sh" "$SSH_TARGET" "$docker_path"; then
            ((SUCCESS_COUNT++))
            echo "✓ Success"
        else
            ((FAIL_COUNT++))
            FAILED_HOSTS+=("$SSH_TARGET")
            echo "✗ Failed"
        fi
    else
        echo "ERROR: Invalid UPDATE_MODE: $UPDATE_MODE (must be 'host-only' or 'full')"
        exit 1
    fi
    
    echo ""
done

echo "========================================="
echo "Batch Update Summary"
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
