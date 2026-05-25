#!/usr/bin/env bash
# oh-my-opencode doctor — diagnose configuration issues
# Usage: ./scripts/doctor.sh [--verbose]

set -euo pipefail

VERBOSE="${1:-}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }

echo "=== Oh My OpenCode Doctor ==="
echo ""

# Check 1: OpenCode installation
echo "Checking OpenCode installation..."
if command -v opencode &>/dev/null; then
    OC_VERSION=$(opencode --version 2>/dev/null || echo "unknown")
    pass "OpenCode installed: $OC_VERSION"
else
    fail "OpenCode is not installed"
    echo "  Install: curl -fsSL https://opencode.ai/install | bash"
    echo "  Or: npm install -g opencode-ai"
    exit 1
fi

# Check 2: bunx available
echo "Checking bunx availability..."
if command -v bunx &>/dev/null; then
    pass "bunx is available"
elif command -v npx &>/dev/null; then
    warn "bunx not found, npx available (bunx is recommended)"
else
    fail "Neither bunx nor npx found"
    echo "  Install Bun: curl -fsSL https://bun.sh/install | bash"
fi

# Check 3: Plugin registration
echo "Checking plugin registration..."
OC_CONFIG="${HOME}/.config/opencode/opencode.json"
if [ -f "$OC_CONFIG" ]; then
    if grep -q "oh-my-opencode" "$OC_CONFIG" 2>/dev/null; then
        pass "oh-my-opencode registered in opencode.json"
    else
        fail "oh-my-opencode NOT found in opencode.json plugin array"
        echo "  Run: bunx oh-my-opencode install"
    fi
else
    fail "opencode.json not found at $OC_CONFIG"
    echo "  Run: opencode auth login (to create config)"
fi

# Check 4: oh-my-opencode config
echo "Checking oh-my-opencode config..."
OMO_USER_CONFIG="${HOME}/.config/opencode/oh-my-opencode.json"
OMO_USER_CONFIGC="${HOME}/.config/opencode/oh-my-opencode.jsonc"
OMO_PROJECT_CONFIG=".opencode/oh-my-opencode.json"
OMO_PROJECT_CONFIGC=".opencode/oh-my-opencode.jsonc"

FOUND_CONFIG=""
for cfg in "$OMO_PROJECT_CONFIGC" "$OMO_PROJECT_CONFIG" "$OMO_USER_CONFIGC" "$OMO_USER_CONFIG"; do
    if [ -f "$cfg" ]; then
        FOUND_CONFIG="$cfg"
        pass "Config found: $cfg"
        break
    fi
done

if [ -z "$FOUND_CONFIG" ]; then
    warn "No oh-my-opencode config found (using defaults)"
    echo "  This is fine — defaults work. Customize at: $OMO_USER_CONFIG"
fi

# Check 5: Provider authentication
echo "Checking provider authentication..."
if command -v opencode &>/dev/null; then
    AUTH_LIST=$(opencode auth list 2>/dev/null || echo "")
    if [ -n "$AUTH_LIST" ]; then
        pass "Providers configured"
        if [ "$VERBOSE" = "--verbose" ]; then
            echo "$AUTH_LIST" | sed 's/^/    /'
        fi
    else
        warn "No providers detected via 'opencode auth list'"
        echo "  Run: opencode auth login"
    fi
fi

# Check 6: tmux (optional)
echo "Checking optional dependencies..."
if command -v tmux &>/dev/null; then
    pass "tmux installed (for multi-pane agent view)"
else
    warn "tmux not installed (optional — needed for visual multi-agent panes)"
fi

# Check 7: Try running oh-my-opencode doctor
echo ""
echo "Running oh-my-opencode built-in doctor..."
echo ""

if command -v bunx &>/dev/null; then
    if [ "$VERBOSE" = "--verbose" ]; then
        bunx oh-my-opencode doctor --verbose 2>/dev/null || {
            warn "bunx oh-my-opencode doctor failed — falling back to manual checks above"
        }
    else
        bunx oh-my-opencode doctor 2>/dev/null || {
            warn "bunx oh-my-opencode doctor failed — falling back to manual checks above"
        }
    fi
elif command -v npx &>/dev/null; then
    if [ "$VERBOSE" = "--verbose" ]; then
        npx oh-my-opencode doctor --verbose 2>/dev/null || {
            warn "npx oh-my-opencode doctor failed — falling back to manual checks above"
        }
    else
        npx oh-my-opencode doctor 2>/dev/null || {
            warn "npx oh-my-opencode doctor failed — falling back to manual checks above"
        }
    fi
else
    warn "Cannot run oh-my-opencode doctor (no bunx or npx)"
fi

echo ""
echo "=== Doctor complete ==="
