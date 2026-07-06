#!/bin/bash
#
# ClawSend Auto-Install Script
#
# Detects available runtime (Python or Node.js) and installs dependencies.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "ClawSend Installer"
echo "=================="
echo ""

# Check for Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ Found Python $PYTHON_VERSION"
    HAS_PYTHON=true
else
    echo "✗ Python not found"
    HAS_PYTHON=false
fi

# Check for Node.js
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo "✓ Found Node.js $NODE_VERSION"
    HAS_NODE=true
else
    echo "✗ Node.js not found"
    HAS_NODE=false
fi

echo ""

# Decide which runtime to use
if [ "$HAS_PYTHON" = true ] && [ "$HAS_NODE" = true ]; then
    echo "Both Python and Node.js are available."
    echo "Which would you like to use?"
    echo "  1) Python (recommended)"
    echo "  2) Node.js"
    read -p "Choice [1]: " choice
    choice=${choice:-1}

    if [ "$choice" = "2" ]; then
        USE_NODE=true
    else
        USE_NODE=false
    fi
elif [ "$HAS_NODE" = true ]; then
    USE_NODE=true
elif [ "$HAS_PYTHON" = true ]; then
    USE_NODE=false
else
    echo "Error: Neither Python nor Node.js found."
    echo "Please install Python 3.11+ or Node.js 18+."
    exit 1
fi

# Install
if [ "$USE_NODE" = true ]; then
    echo ""
    echo "Installing Node.js dependencies..."
    cd "$SCRIPT_DIR/node"
    npm install
    echo ""
    echo "✓ Installation complete!"
    echo ""
    echo "Usage:"
    echo "  node node/scripts/send.js --to ALIAS --intent ping --body '{}'"
    echo "  node node/scripts/receive.js"
    echo "  node node/scripts/receive.js --poll"
    echo "  node node/scripts/discover.js --list"
else
    echo ""
    echo "Installing Python dependencies..."
    cd "$SCRIPT_DIR/python"
    pip install -r requirements.txt
    echo ""
    echo "✓ Installation complete!"
    echo ""
    echo "Usage:"
    echo "  python python/scripts/send.py --to ALIAS --intent ping --body '{}'"
    echo "  python python/scripts/receive.py"
    echo "  python python/scripts/receive.py --poll"
    echo "  python python/scripts/discover.py --list"
fi
