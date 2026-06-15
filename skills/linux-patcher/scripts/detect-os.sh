#!/bin/bash
# detect-os.sh - Detect Linux distribution and return package manager info
# Usage: eval "$(./detect-os.sh user@hostname)"
# Returns: PKG_MANAGER, UPDATE_CMD, UPGRADE_CMD, AUTOREMOVE_CMD

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 user@hostname"
    exit 1
fi

HOST="$1"

# Detect OS
OS_INFO=$(ssh "$HOST" "cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null || echo 'ID=unknown'")

# Parse distribution ID
DISTRO=$(echo "$OS_INFO" | grep -oP '(?<=^ID=).+' | tr -d '"' | head -n1)

case "$DISTRO" in
    ubuntu|debian)
        echo "PKG_MANAGER=apt"
        echo "UPDATE_CMD='apt update'"
        echo "UPGRADE_CMD='apt upgrade -y'"
        echo "AUTOREMOVE_CMD='apt autoremove -y'"
        echo "DISTRO_NAME='$DISTRO'"
        echo "TESTED=true"
        ;;
    amzn|amazon)
        # Amazon Linux 2023 uses dnf, AL2 uses yum
        if ssh "$HOST" "command -v dnf >/dev/null 2>&1"; then
            echo "PKG_MANAGER=dnf"
            echo "UPDATE_CMD='dnf check-update || true'"
            echo "UPGRADE_CMD='dnf update -y'"
            echo "AUTOREMOVE_CMD='dnf autoremove -y'"
        else
            echo "PKG_MANAGER=yum"
            echo "UPDATE_CMD='yum check-update || true'"
            echo "UPGRADE_CMD='yum update -y'"
            echo "AUTOREMOVE_CMD='yum autoremove -y'"
        fi
        echo "DISTRO_NAME='Amazon Linux'"
        echo "TESTED=false"
        ;;
    rhel|rocky|almalinux|alma)
        # RHEL 8+ uses dnf, older uses yum
        if ssh "$HOST" "command -v dnf >/dev/null 2>&1"; then
            echo "PKG_MANAGER=dnf"
            echo "UPDATE_CMD='dnf check-update || true'"
            echo "UPGRADE_CMD='dnf update -y'"
            echo "AUTOREMOVE_CMD='dnf autoremove -y'"
        else
            echo "PKG_MANAGER=yum"
            echo "UPDATE_CMD='yum check-update || true'"
            echo "UPGRADE_CMD='yum update -y'"
            echo "AUTOREMOVE_CMD='yum autoremove -y'"
        fi
        echo "DISTRO_NAME='$DISTRO'"
        echo "TESTED=false"
        ;;
    centos)
        # CentOS 8+ uses dnf, older uses yum
        if ssh "$HOST" "command -v dnf >/dev/null 2>&1"; then
            echo "PKG_MANAGER=dnf"
            echo "UPDATE_CMD='dnf check-update || true'"
            echo "UPGRADE_CMD='dnf update -y'"
            echo "AUTOREMOVE_CMD='dnf autoremove -y'"
        else
            echo "PKG_MANAGER=yum"
            echo "UPDATE_CMD='yum check-update || true'"
            echo "UPGRADE_CMD='yum update -y'"
            echo "AUTOREMOVE_CMD='yum autoremove -y'"
        fi
        echo "DISTRO_NAME='CentOS'"
        echo "TESTED=false"
        ;;
    sles|suse|opensuse*)
        echo "PKG_MANAGER=zypper"
        echo "UPDATE_CMD='zypper refresh'"
        echo "UPGRADE_CMD='zypper update -y'"
        echo "AUTOREMOVE_CMD='zypper packages --unneeded | xargs -r zypper remove -y'"
        echo "DISTRO_NAME='SUSE'"
        echo "TESTED=false"
        ;;
    *)
        echo "ERROR: Unsupported distribution: $DISTRO" >&2
        echo "DISTRO_NAME='$DISTRO'"
        echo "TESTED=false"
        exit 1
        ;;
esac
