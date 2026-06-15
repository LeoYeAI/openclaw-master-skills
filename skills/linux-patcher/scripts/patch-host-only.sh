#!/bin/bash
# patch-host-only.sh - Update Linux packages only (no Docker)
# Usage: ./patch-host-only.sh user@hostname

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 user@hostname"
    echo "Example: $0 admin@webserver.example.com"
    exit 1
fi

HOST="$1"
DRY_RUN="${DRY_RUN:-false}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Linux Patcher - Host-Only Mode"
echo "========================================="
echo "Target: $HOST"
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

if [ "$DRY_RUN" = "true" ]; then
    echo ""
    echo "[DRY RUN] Would execute the following updates:"
    echo "  1. $UPDATE_CMD"
    echo "  2. $UPGRADE_CMD"
    echo "  3. $AUTOREMOVE_CMD"
    echo ""
    echo "Set DRY_RUN=false to apply changes"
    exit 0
fi

echo ""
echo "Step 1/3: Updating package lists..."
ssh "$HOST" "sudo $UPDATE_CMD" || {
    echo "ERROR: Failed to update package lists on $HOST"
    exit 1
}

echo "Step 2/3: Upgrading packages..."
ssh "$HOST" "sudo $UPGRADE_CMD" || {
    echo "ERROR: Failed to upgrade packages on $HOST"
    exit 1
}

echo "Step 3/3: Removing unused packages..."
ssh "$HOST" "sudo $AUTOREMOVE_CMD" || {
    echo "WARNING: Failed to autoremove packages on $HOST (non-critical)"
}

echo ""
echo "✓ Host-only update complete on $HOST"
echo ""

# Check for reboot requirement (best-effort, varies by distro)
echo "Checking if reboot is required..."
if ssh "$HOST" "[ -f /var/run/reboot-required ]" 2>/dev/null; then
    echo "⚠ REBOOT REQUIRED (Kernel or critical libraries updated)"
elif ssh "$HOST" "[ -f /boot/vmlinuz-\$(uname -r) ]" 2>/dev/null; then
    # Check if running kernel matches latest installed
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
