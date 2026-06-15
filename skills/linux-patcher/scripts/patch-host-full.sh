#!/bin/bash
# patch-host-full.sh - Update Linux packages AND Docker containers
# Usage: ./patch-host-full.sh user@hostname [/docker/path]

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 user@hostname [/docker/path]"
    echo "Example: $0 admin@webserver.example.com"
    echo "Example: $0 admin@webserver.example.com /home/admin/docker"
    exit 1
fi

HOST="$1"
DOCKER_PATH="${2:-}"
DRY_RUN="${DRY_RUN:-false}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Linux Patcher - Full Update Mode"
echo "========================================="
echo "Target: $HOST"
echo "Docker Path: ${DOCKER_PATH:-<auto-detect>}"
echo "Dry Run: $DRY_RUN"
echo ""

# Detect OS and get package manager commands
echo "Detecting Linux distribution..."
eval "$("$SCRIPT_DIR/detect-os.sh" "$HOST")"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to detect OS on $HOST"
    exit 1
fi

echo "✓ Detected: $DISTRO_NAME ($PKG_MANAGER)"

if [ "$TESTED" = "false" ]; then
    echo ""
    echo "⚠ WARNING: $DISTRO_NAME support is UNTESTED"
    echo "  Only Ubuntu has been tested end-to-end"
    echo "  Update commands for $DISTRO_NAME are based on documentation"
    echo "  Proceed with caution and verify results"
    echo ""
fi

# Auto-detect Docker path if not provided
if [ -z "$DOCKER_PATH" ]; then
    echo "Auto-detecting Docker Compose location..."
    
    # Get SSH user from HOST string
    SSH_USER=$(echo "$HOST" | cut -d'@' -f1)
    
    # Try common locations
    SEARCH_PATHS=(
        "/home/$SSH_USER/Docker"
        "/home/$SSH_USER/docker"
        "/opt/docker"
        "/srv/docker"
        "\$HOME/Docker"
        "\$HOME/docker"
    )
    
    for path in "${SEARCH_PATHS[@]}"; do
        if ssh "$HOST" "[ -f $path/docker-compose.yml ]" 2>/dev/null; then
            DOCKER_PATH="$path"
            echo "✓ Found Docker Compose at: $DOCKER_PATH"
            break
        fi
    done
    
    if [ -z "$DOCKER_PATH" ]; then
        echo "ERROR: Could not auto-detect Docker Compose location"
        echo "Please specify path: $0 $HOST /path/to/docker"
        exit 1
    fi
fi

if [ "$DRY_RUN" = "true" ]; then
    echo ""
    echo "[DRY RUN] Would execute the following updates:"
    echo "  1. $UPDATE_CMD && $UPGRADE_CMD && $AUTOREMOVE_CMD"
    echo "  2. docker system prune -af"
    echo "  3. docker pull all images from compose file"
    echo "  4. docker compose pull"
    echo "  5. docker compose up -d"
    echo ""
    echo "Set DRY_RUN=false to apply changes"
    exit 0
fi

echo ""
echo "Step 1/5: Updating system packages..."
ssh "$HOST" "sudo $UPDATE_CMD && sudo $UPGRADE_CMD && sudo $AUTOREMOVE_CMD" || {
    echo "ERROR: Failed to update packages on $HOST"
    exit 1
}

echo "Step 2/5: Cleaning Docker cache..."
ssh "$HOST" "sudo docker system prune -af" || {
    echo "WARNING: Docker cleanup failed (continuing anyway)"
}

echo "Step 3/5: Pulling updated Docker images..."
ssh "$HOST" "cd $DOCKER_PATH && sudo docker images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' | xargs -r -L1 sudo docker pull" || {
    echo "WARNING: Some image pulls failed (continuing anyway)"
}

echo "Step 4/5: Pulling compose images..."
ssh "$HOST" "cd $DOCKER_PATH && sudo docker compose pull" || {
    echo "ERROR: Docker compose pull failed on $HOST"
    exit 1
}

echo "Step 5/5: Recreating containers..."
ssh "$HOST" "cd $DOCKER_PATH && sudo docker compose up -d" || {
    echo "ERROR: Docker compose up failed on $HOST"
    exit 1
}

echo ""
echo "✓ Full update complete on $HOST"
echo ""

# Check for reboot requirement
echo "Checking if reboot is required..."
if ssh "$HOST" "[ -f /var/run/reboot-required ]" 2>/dev/null; then
    echo "⚠ REBOOT REQUIRED (Kernel or critical libraries updated)"
elif ssh "$HOST" "[ -f /boot/vmlinuz-\$(uname -r) ]" 2>/dev/null; then
    RUNNING_KERNEL=$(ssh "$HOST" "uname -r")
    LATEST_KERNEL=$(ssh "$HOST" "ls -t /boot/vmlinuz-* 2>/dev/null | head -n1 | sed 's|/boot/vmlinuz-||'")
    if [ "$RUNNING_KERNEL" != "$LATEST_KERNEL" ]; then
        echo "⚠ REBOOT RECOMMENDED (Kernel updated: $RUNNING_KERNEL → $LATEST_KERNEL)"
    else
        echo "✓ No reboot required"
    fi
else
    echo "ℹ Could not determine reboot status (check manually if kernel was updated)"
fi
