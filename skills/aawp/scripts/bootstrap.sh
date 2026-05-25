#!/usr/bin/env bash
# AAWP Bootstrap — downloads missing binary artifacts from GitHub on first run.
# Called automatically by ensure-daemon.sh and wallet-manager.js.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CORE_DIR="$SKILL_DIR/core"
REPO="aawp-ai/aawp"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/$REPO/$BRANCH"

REQUIRED_FILES=(
  "core/aawp-core.node"
  "core/aawp-core.node.hash"
  "core/loader.jsc"
)

missing=()
for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$SKILL_DIR/$f" ]; then
    missing+=("$f")
  fi
done

if [ ${#missing[@]} -eq 0 ]; then
  exit 0
fi

echo "[AAWP] Bootstrap: ${#missing[@]} missing file(s), downloading from GitHub..."

for f in "${missing[@]}"; do
  target="$SKILL_DIR/$f"
  url="$BASE_URL/$f"
  mkdir -p "$(dirname "$target")"
  echo "  ↓ $f"
  if command -v curl &>/dev/null; then
    curl -fsSL -o "$target" "$url"
  elif command -v wget &>/dev/null; then
    wget -q -O "$target" "$url"
  else
    echo "  ❌ Neither curl nor wget available. Cannot download $f" >&2
    exit 1
  fi
done

# Verify binary hash if both files exist
NODE_FILE="$CORE_DIR/aawp-core.node"
HASH_FILE="$CORE_DIR/aawp-core.node.hash"
if [ -f "$NODE_FILE" ] && [ -f "$HASH_FILE" ]; then
  expected=$(cat "$HASH_FILE" | tr -d '[:space:]')
  actual=$(sha256sum "$NODE_FILE" | awk '{print $1}')
  if [ "$expected" = "$actual" ]; then
    echo "[AAWP] ✅ Binary hash verified."
  else
    echo "[AAWP] ⚠️  Binary hash mismatch!"
    echo "  Expected: $expected"
    echo "  Got:      $actual"
    echo "  The binary may be corrupted. Re-download or verify manually."
    rm -f "$NODE_FILE"
    exit 1
  fi
fi

chmod +x "$NODE_FILE" 2>/dev/null || true
echo "[AAWP] Bootstrap complete."
