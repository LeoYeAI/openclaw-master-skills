#!/usr/bin/env bash
# Setup auto-respawn — install Node.js dependencies and tsx
# Usage: ./setup.sh
# Run this after `clawhub install` (the CLI doesn't execute install steps automatically)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Auto-Respawn — Setup                    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check for Node.js
if ! command -v node &>/dev/null; then
  echo "Error: Node.js is not installed." >&2
  echo "  Install: https://nodejs.org/ or via your package manager" >&2
  exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION"

# Determine package manager (respect openclaw.json preference if set)
PKG_MANAGER="npm"
OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"
if [[ -f "$OPENCLAW_CONFIG" ]] && command -v jq &>/dev/null; then
  PREFERRED=$(jq -r '.skills.install.nodeManager // empty' "$OPENCLAW_CONFIG" 2>/dev/null || true)
  if [[ -n "$PREFERRED" ]] && command -v "$PREFERRED" &>/dev/null; then
    PKG_MANAGER="$PREFERRED"
  fi
fi

echo "✓ Using $PKG_MANAGER"
echo ""

# Install dependencies
echo "Installing dependencies..."
(cd "$SCRIPT_DIR" && "$PKG_MANAGER" install)
echo ""

# Check for tsx
if ! command -v tsx &>/dev/null && ! npx tsx --version &>/dev/null 2>&1; then
  echo "Installing tsx (TypeScript executor)..."
  "$PKG_MANAGER" install -g tsx
else
  echo "✓ tsx available"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup complete!                         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Create a wallet:  npx tsx auto-respawn.ts wallet create --name my-agent"
echo "  2. Fund it:          Visit https://autonomysfaucet.xyz/ (testnet)"
echo "  3. Verify:           npx tsx auto-respawn.ts wallet list"
echo ""
