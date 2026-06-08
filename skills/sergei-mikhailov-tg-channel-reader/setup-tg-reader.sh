#!/usr/bin/env bash
# setup-tg-reader.sh — Pre-flight setup for tg-channel-reader OpenClaw skill
# Checks prerequisites and guides through exec approval configuration.
#
# Usage:
#   bash setup-tg-reader.sh
#
# What it does:
#   1. Verifies Python 3.9+ is available
#   2. Checks if tg-reader CLI is installed and in PATH
#   3. Installs Python package if needed (pip install .)
#   4. Verifies Telegram credentials (env vars or ~/.tg-reader.json)
#   5. Verifies session file exists
#   6. Runs tg-reader-check diagnostic
#   7. Prints exec approval instructions for OpenClaw (manual step)

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
info() { echo -e "${CYAN}→${NC} $1"; }

ERRORS=0

echo ""
echo "══════════════════════════════════════════════════════"
echo "  tg-channel-reader — Setup & Diagnostics"
echo "══════════════════════════════════════════════════════"
echo ""

# ── Step 1: Python ───────────────────────────────────────────────────────────

echo "── Python ──"

if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 9 ]; then
        ok "Python $PY_VERSION"
    else
        fail "Python $PY_VERSION (need 3.9+)"
        ERRORS=$((ERRORS + 1))
    fi
else
    fail "python3 not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# ── Step 2: tg-reader CLI ───────────────────────────────────────────────────

echo "── CLI Commands ──"

NEED_INSTALL=0

for cmd in tg-reader tg-reader-check; do
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd → $(which "$cmd")"
    else
        fail "$cmd not found in PATH"
        NEED_INSTALL=1
    fi
done

# Optional backends
for cmd in tg-reader-pyrogram tg-reader-telethon; do
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd → $(which "$cmd")"
    else
        warn "$cmd not found (optional)"
    fi
done

if [ "$NEED_INSTALL" -eq 1 ]; then
    echo ""
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/setup.py" ]; then
        info "Installing from $SCRIPT_DIR ..."
        pip install "$SCRIPT_DIR" 2>&1 | tail -1
        # Re-check
        if command -v tg-reader &>/dev/null; then
            ok "tg-reader installed successfully"
        else
            fail "tg-reader still not in PATH after install"
            info "Try: pip install . && hash -r"
            info "Or add the pip bin directory to PATH"
            ERRORS=$((ERRORS + 1))
        fi
    else
        fail "setup.py not found — run this script from the skill directory"
        ERRORS=$((ERRORS + 1))
    fi
fi

echo ""

# ── Step 3: Python libraries ────────────────────────────────────────────────

echo "── MTProto Libraries ──"

PYROGRAM_OK=0
TELETHON_OK=0

if python3 -c "import pyrogram" 2>/dev/null; then
    PYRO_VER=$(python3 -c "import pyrogram; print(pyrogram.__version__)" 2>/dev/null || echo "unknown")
    ok "Pyrogram $PYRO_VER"
    PYROGRAM_OK=1
else
    warn "Pyrogram not installed (pip install pyrogram tgcrypto)"
fi

if python3 -c "import telethon" 2>/dev/null; then
    TEL_VER=$(python3 -c "import telethon; print(telethon.__version__)" 2>/dev/null || echo "unknown")
    ok "Telethon $TEL_VER"
    TELETHON_OK=1
else
    warn "Telethon not installed (pip install telethon)"
fi

if [ "$PYROGRAM_OK" -eq 0 ] && [ "$TELETHON_OK" -eq 0 ]; then
    fail "No MTProto backend installed — at least one is required"
    info "Run: pip install pyrogram tgcrypto telethon"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# ── Step 4: Credentials ─────────────────────────────────────────────────────

echo "── Credentials ──"

CREDS_OK=0

if [ -n "${TG_API_ID:-}" ] && [ -n "${TG_API_HASH:-}" ]; then
    ok "TG_API_ID and TG_API_HASH set via environment"
    CREDS_OK=1
fi

CONFIG_FILE="${HOME}/.tg-reader.json"
if [ -f "$CONFIG_FILE" ]; then
    ok "Config file: $CONFIG_FILE"
    CREDS_OK=1
else
    if [ "$CREDS_OK" -eq 0 ]; then
        fail "No credentials found"
        info "Set TG_API_ID + TG_API_HASH env vars"
        info "Or create ~/.tg-reader.json: {\"api_id\": ..., \"api_hash\": \"...\"}"
        info "Get credentials at https://my.telegram.org → API Development Tools"
        ERRORS=$((ERRORS + 1))
    fi
fi

echo ""

# ── Step 5: Session file ────────────────────────────────────────────────────

echo "── Session File ──"

SESSION_FOUND=0
for f in "${HOME}/.tg-reader-session.session" "${HOME}/.telethon-reader.session"; do
    if [ -f "$f" ]; then
        SIZE=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo "?")
        ok "$f (${SIZE} bytes)"
        SESSION_FOUND=1
    fi
done

if [ "$SESSION_FOUND" -eq 0 ]; then
    # Check current directory for known tg-reader session names only
    for f in tg-reader-session.session .tg-reader-session.session telethon-reader.session .telethon-reader.session; do
        if [ -f "$f" ]; then
            ok "Found session: $(pwd)/$f"
            SESSION_FOUND=1
        fi
    done
fi

if [ "$SESSION_FOUND" -eq 0 ]; then
    warn "No session file found — run: tg-reader auth"
fi

echo ""

# ── Step 6: tg-reader-check ─────────────────────────────────────────────────

echo "── Diagnostic (tg-reader-check) ──"

if command -v tg-reader-check &>/dev/null; then
    CHECK_OUTPUT=$(tg-reader-check 2>&1 || true)
    if echo "$CHECK_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('status')=='ok' else 1)" 2>/dev/null; then
        ok "tg-reader-check passed"
    else
        warn "tg-reader-check reported issues:"
        echo "    $CHECK_OUTPUT" | head -5
    fi
else
    warn "tg-reader-check not available — skipping"
fi

echo ""

# ── Step 7: OpenClaw Exec Approvals ─────────────────────────────────────────

echo "── OpenClaw Exec Approvals ──"

info "OpenClaw blocks unknown CLI commands by default."
info "Approve tg-reader commands using one of these methods:"
echo ""
echo "  Option A (CLI):"
for cmd in tg-reader tg-reader-check tg-reader-pyrogram tg-reader-telethon; do
    CMD_PATH=$(which "$cmd" 2>/dev/null || true)
    if [ -n "$CMD_PATH" ]; then
        echo "    openclaw approvals allowlist add --gateway \"$CMD_PATH\""
    fi
done
echo ""
echo "  Option B (Control UI):"
echo "    1. Open http://localhost:18789/"
echo "    2. Find the pending approval for tg-reader"
echo "    3. Click \"Always allow\""
echo ""
echo "  Option C (Messenger):"
echo "    Reply to the bot's approval request:"
echo "    /approve <id> allow-always"

echo ""

# ── Summary ──────────────────────────────────────────────────────────────────

echo "══════════════════════════════════════════════════════"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "  ${GREEN}All checks passed.${NC} Ready to use tg-reader."
else
    echo -e "  ${RED}${ERRORS} issue(s) found.${NC} Fix them and re-run this script."
fi
echo "══════════════════════════════════════════════════════"
echo ""

exit "$ERRORS"
