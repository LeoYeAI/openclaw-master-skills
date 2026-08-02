#!/bin/bash
set -e

# ============================================================
# ⚠️  SECURITY NOTICE
# ============================================================
# By default this script SKIPS the SurrealDB installer and
# only installs Python dependencies.
#
# To use the curl|sh network installer, pass --install-surreal:
#   ./install.sh --install-surreal
#
# Running scripts directly from the internet via curl|sh is
# a security risk. The PREFERRED path is manual installation:
#   https://surrealdb.com/install
#
# After manual install, run without --install-surreal:
#   ./install.sh
# ============================================================

SKIP_SURREAL=true   # Safe default — skip network installer
for arg in "$@"; do
  case $arg in
    --install-surreal) SKIP_SURREAL=false ;;
    --skip-surreal) SKIP_SURREAL=true ;;  # legacy alias, still accepted
  esac
done

echo "=== SurrealDB Memory Skill Installer ==="
if [ "$SKIP_SURREAL" = true ]; then
  echo "  [default] SurrealDB network installer SKIPPED (safe default)."
  echo "  Install SurrealDB manually from: https://surrealdb.com/install"
  echo "  Then make sure 'surreal' is in your PATH before continuing."
  echo "  To use the network installer instead: ./install.sh --install-surreal"
  echo ""
else
  echo "  [--install-surreal] Network installer enabled."
  echo "  ⚠️  This will fetch and execute a remote script from install.surrealdb.com"
  echo ""
fi

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=linux;;
    Darwin*)    PLATFORM=macos;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM=windows;;
    *)          PLATFORM="unknown";;
esac

echo "Detected platform: $PLATFORM"

# Check if SurrealDB is already installed
if command -v surreal &> /dev/null; then
    CURRENT_VERSION=$(surreal version 2>/dev/null | head -1 || echo "unknown")
    echo "SurrealDB already installed: $CURRENT_VERSION"
    if [ "$SKIP_SURREAL" = false ]; then
        read -p "Reinstall/update? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping SurrealDB installation."
            SKIP_INSTALL=true
        fi
    else
        SKIP_INSTALL=true
    fi
fi

if [ -z "$SKIP_INSTALL" ] && [ "$SKIP_SURREAL" = false ]; then
    echo ""
    echo "⚠️  About to fetch and execute a remote install script."
    echo "   URL: https://install.surrealdb.com"
    echo "   To skip this and install manually, Ctrl+C now."
    echo "   Manual install: https://surrealdb.com/install"
    echo ""
    read -p "   Continue with curl installer? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Install SurrealDB manually from https://surrealdb.com/install"
        echo "Then re-run this script (without --install-surreal)"
        exit 1
    fi

    echo "Installing SurrealDB..."
    case "${PLATFORM}" in
        linux)
            curl -sSf https://install.surrealdb.com | sh
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install surrealdb/tap/surreal
            else
                curl -sSf https://install.surrealdb.com | sh
            fi
            ;;
        windows)
            echo "On Windows, run: iwr https://windows.surrealdb.com -useb | iex"
            echo "Or use: choco install surreal"
            exit 1
            ;;
        *)
            echo "Unknown platform. Install manually from https://surrealdb.com/install"
            exit 1
            ;;
    esac

    echo "SurrealDB installed successfully!"
elif [ "$SKIP_SURREAL" = true ]; then
    echo "(Skipping SurrealDB network install — default safe mode)"
    echo "Install manually from https://surrealdb.com/install if not already done."
fi

# Verify installation
if ! command -v surreal &> /dev/null; then
    echo ""
    echo "ERROR: surreal command not found in PATH."
    if [ "$SKIP_SURREAL" = true ]; then
        echo ""
        echo "SurrealDB is not installed. Install it manually first:"
        echo "  https://surrealdb.com/install"
        echo ""
        echo "Then re-run this script. Or to use the network installer:"
        echo "  ./install.sh --install-surreal"
    else
        echo "Add ~/.surrealdb to your PATH or reinstall."
    fi
    exit 1
fi

surreal version

# Create data directory
DATA_DIR="${HOME}/.openclaw/memory"
mkdir -p "$DATA_DIR"
echo "Data directory: $DATA_DIR"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"

if [ -f "$REQUIREMENTS" ]; then
    pip3 install -q -r "$REQUIREMENTS" 2>/dev/null || pip install -q -r "$REQUIREMENTS"
else
    pip3 install -q surrealdb openai pyyaml 2>/dev/null || pip install -q surrealdb openai pyyaml
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "  1. Start SurrealDB:  surreal start --bind 127.0.0.1:8000 --user root --pass root file:~/.openclaw/memory/knowledge.db"
echo "  2. ⚠️  Change default credentials (root/root) — set SURREAL_USER and SURREAL_PASS env vars"
echo "  3. Initialize schema: ./scripts/init-db.sh"
echo "  4. (Optional) Migrate: python3 scripts/migrate-sqlite.py"
