#!/usr/bin/env bash
set -euo pipefail

# AgentSource Plugin — Setup Script
# Installs the CLI to ~/.agentsource/bin/ and optionally saves your API key.
#
# Files installed:
#   ~/.agentsource/bin/agentsource.py   — the CLI tool (copied from ./bin/agentsource.py)
#   ~/.agentsource/config.json          — API key storage (mode 600, only if you choose to save it)
#
# Nothing is sent to any network during setup. The API key is only used when
# you run CLI commands that call https://api.explorium.ai/v1/.

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.agentsource"
BIN_DIR="$INSTALL_DIR/bin"
CONFIG_FILE="$INSTALL_DIR/config.json"

echo "=== AgentSource Plugin Setup ==="
echo ""
echo "This script will:"
echo "  1. Copy bin/agentsource.py  →  $BIN_DIR/agentsource.py"
echo "  2. Optionally save your API key to $CONFIG_FILE (mode 600)"
echo ""

# ---------------------------------------------------------------------------
# 1. Verify Python 3.8+
# ---------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+ and retry."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    echo "[ERROR] Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "[OK] Python $PYTHON_VERSION"

# ---------------------------------------------------------------------------
# 2. Create directory structure
# ---------------------------------------------------------------------------
mkdir -p "$BIN_DIR"
echo "[OK] Created $BIN_DIR"

# ---------------------------------------------------------------------------
# 3. Install CLI
# ---------------------------------------------------------------------------
cp "$PLUGIN_DIR/bin/agentsource.py" "$BIN_DIR/agentsource.py"
chmod +x "$BIN_DIR/agentsource.py"
echo "[OK] CLI installed to $BIN_DIR/agentsource.py"

# ---------------------------------------------------------------------------
# 4. API key configuration
#    IMPORTANT: Never enter your API key into the AI chat window.
#    Set it here in your terminal (secure) or via environment variable.
# ---------------------------------------------------------------------------
echo ""
echo "--- API Key Setup ---"
echo "IMPORTANT: Do NOT share your API key in the AI chat."
echo "Set it here in your terminal or via the EXPLORIUM_API_KEY environment variable."
echo ""

if [ -n "${EXPLORIUM_API_KEY:-}" ]; then
    echo "[OK] EXPLORIUM_API_KEY is already set in your environment."
    read -r -p "Save it to $CONFIG_FILE for persistence? [y/N] " save_key
    if [[ "${save_key:-}" =~ ^[Yy]$ ]]; then
        printf '{\n  "api_key": "%s"\n}\n' \
            "$EXPLORIUM_API_KEY" > "$CONFIG_FILE"
        chmod 600 "$CONFIG_FILE"
        echo "[OK] API key saved to $CONFIG_FILE (mode 600, owner read-only)"
    fi
else
    echo "No EXPLORIUM_API_KEY environment variable detected."
    echo ""
    read -r -p "Enter your Explorium API key (or press Enter to skip): " api_key
    if [ -n "${api_key:-}" ]; then
        printf '{\n  "api_key": "%s"\n}\n' \
            "$api_key" > "$CONFIG_FILE"
        chmod 600 "$CONFIG_FILE"
        echo "[OK] API key saved to $CONFIG_FILE (mode 600, owner read-only)"
        echo ""
        echo "To also set it as an environment variable, add this to ~/.zshrc or ~/.bashrc:"
        echo "  export EXPLORIUM_API_KEY='$api_key'"
    else
        echo "[WARN] No API key configured."
        echo "  Set it later with:  python3 $BIN_DIR/agentsource.py config --api-key <key>"
        echo "  Or set env var:     export EXPLORIUM_API_KEY=<key>"
        echo "  Get a key at:       https://developers.explorium.ai/reference/setup/getting_your_api_key"
    fi
fi

# ---------------------------------------------------------------------------
# 5. Smoke-test the CLI
# ---------------------------------------------------------------------------
echo ""
echo "Running CLI smoke test..."
if python3 "$BIN_DIR/agentsource.py" --help &>/dev/null; then
    echo "[OK] CLI smoke test passed"
else
    echo "[ERROR] CLI smoke test failed. Check your Python installation."
    exit 1
fi

# ---------------------------------------------------------------------------
# 6. Done
# ---------------------------------------------------------------------------
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Files installed:"
echo "  $BIN_DIR/agentsource.py   — CLI tool"
if [ -f "$CONFIG_FILE" ]; then
    echo "  $CONFIG_FILE       — API key (mode 600)"
fi
echo ""
echo "Optional: Add the CLI to your PATH:"
echo "  echo 'export PATH=\"\$HOME/.agentsource/bin:\$PATH\"' >> ~/.zshrc"
echo ""
echo "Usage — describe your target to your AI agent, for example:"
echo "  'Find CTOs at Series B SaaS companies in California'"
echo "  'Show me fintech companies using Stripe with 50-200 employees'"
echo "  'Get emails for VP Sales at companies that recently raised Series A'"
echo ""
echo "Direct CLI usage:"
echo "  python3 $BIN_DIR/agentsource.py --help"
echo "  python3 $BIN_DIR/agentsource.py autocomplete --entity-type businesses --field linkedin_category --query 'saas' --semantic"
