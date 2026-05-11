#!/usr/bin/env bash
# ensure_env.sh — Verify the skill's Python dependencies are installed for the
# current skill version. Run this before executing any skill tool script.
#
# Usage:
#   bash {baseDir}/tools/ensure_env.sh {baseDir}
#
# Exit codes:
#   0  — environment is ready
#   1  — install failed (pip error or missing python3)

set -e

SKILL_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TOOLS_DIR="${SKILL_DIR}/tools"
REQUIREMENTS="${SKILL_DIR}/requirements.txt"
SKILL_MD="${SKILL_DIR}/SKILL.md"
STAMP_FILE="${SKILL_DIR}/.installed_version"

# ── Resolve current skill version from SKILL.md ───────────────────────────────
CURRENT_VERSION=$(grep "^version:" "$SKILL_MD" 2>/dev/null | head -1 | sed 's/.*: //' | tr -d '[:space:]')
if [ -z "$CURRENT_VERSION" ]; then
    echo "⚠  Could not read skill version from SKILL.md — skipping version check."
    CURRENT_VERSION="unknown"
fi

# ── Read installed version stamp ──────────────────────────────────────────────
INSTALLED_VERSION=""
if [ -f "$STAMP_FILE" ]; then
    INSTALLED_VERSION=$(cat "$STAMP_FILE" | tr -d '[:space:]')
fi

# ── Skip if already up to date ────────────────────────────────────────────────
if [ "$INSTALLED_VERSION" = "$CURRENT_VERSION" ]; then
    exit 0
fi

# ── Install / upgrade dependencies ────────────────────────────────────────────
echo "📦 Skill version changed (${INSTALLED_VERSION:-none} → ${CURRENT_VERSION}). Installing dependencies..."

if ! command -v python3 &>/dev/null; then
    echo "❌ python3 not found. Please install Python 3.9+ and re-run." >&2
    exit 1
fi

if [ ! -f "$REQUIREMENTS" ]; then
    echo "❌ requirements.txt not found at $REQUIREMENTS" >&2
    exit 1
fi

python3 -m pip install --quiet -r "$REQUIREMENTS"

# ── Write version stamp on success ────────────────────────────────────────────
echo "$CURRENT_VERSION" > "$STAMP_FILE"
echo "✅ Dependencies installed for katbot-trading@${CURRENT_VERSION}."
