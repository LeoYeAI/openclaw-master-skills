#!/usr/bin/env bash
set -euo pipefail

# GPG setup for OpenClaw credential encryption
# Usage: ./scripts/setup-gpg.sh [--cache-hours N]

CACHE_HOURS=8

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --cache-hours)
            CACHE_HOURS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--cache-hours N]"
            echo ""
            echo "Sets up GPG for OpenClaw credential encryption."
            echo ""
            echo "Options:"
            echo "  --cache-hours N   GPG agent cache timeout (default: 8)"
            echo "  --help, -h        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

CACHE_SECONDS=$((CACHE_HOURS * 3600))

echo ""
echo "🔐 OpenClaw GPG Setup"
echo "====================="
echo ""

# Step 1: Check if GPG is installed
echo "📋 Step 1: Checking GPG installation..."
if ! command -v gpg &>/dev/null; then
    echo "   ❌ GPG is not installed"
    echo ""
    echo "   Install with:"
    echo "     Ubuntu/Debian: sudo apt install gnupg"
    echo "     macOS:         brew install gnupg"
    echo "     Fedora:        sudo dnf install gnupg2"
    exit 1
fi

GPG_VERSION=$(gpg --version | head -1)
echo "   ✅ $GPG_VERSION"

# Step 2: Configure gpg-agent
echo ""
echo "📋 Step 2: Configuring GPG agent (cache: ${CACHE_HOURS}h)..."

GPG_DIR="$HOME/.gnupg"
mkdir -p "$GPG_DIR"
chmod 700 "$GPG_DIR"

AGENT_CONF="$GPG_DIR/gpg-agent.conf"

# Backup existing config
if [[ -f "$AGENT_CONF" ]]; then
    cp "$AGENT_CONF" "${AGENT_CONF}.bak"
    echo "   📦 Backed up existing config"
fi

# Write agent config
cat > "$AGENT_CONF" << EOF
# OpenClaw GPG Agent Configuration
# Cache passphrase for ${CACHE_HOURS} hours
default-cache-ttl ${CACHE_SECONDS}
max-cache-ttl ${CACHE_SECONDS}

# Allow loopback pinentry (for headless/script usage)
allow-loopback-pinentry
EOF

chmod 600 "$AGENT_CONF"

# Configure GPG to use loopback pinentry
GPG_CONF="$GPG_DIR/gpg.conf"
if ! grep -q "pinentry-mode loopback" "$GPG_CONF" 2>/dev/null; then
    echo "pinentry-mode loopback" >> "$GPG_CONF"
fi

echo "   ✅ Agent configured (cache: ${CACHE_HOURS}h)"

# Reload agent
gpgconf --kill gpg-agent 2>/dev/null || true
echo "   ✅ Agent reloaded"

# Step 3: Test encrypt/decrypt cycle
echo ""
echo "📋 Step 3: Testing encrypt/decrypt cycle..."

TEST_FILE=$(mktemp)
TEST_ENC="${TEST_FILE}.gpg"
TEST_DEC="${TEST_FILE}.dec"
TEST_DATA="openclaw-gpg-test-$(date +%s)"

echo "$TEST_DATA" > "$TEST_FILE"

# Try encryption
if gpg -c --batch --yes --cipher-algo AES256 --passphrase "" -o "$TEST_ENC" "$TEST_FILE" 2>/dev/null; then
    # Try decryption
    if gpg -d --batch --quiet --passphrase "" "$TEST_ENC" > "$TEST_DEC" 2>/dev/null; then
        DECRYPTED=$(cat "$TEST_DEC")
        if [[ "$DECRYPTED" == "$TEST_DATA" ]]; then
            echo "   ✅ Encrypt/decrypt test passed"
        else
            echo "   ⚠️  Decrypt returned different data"
        fi
    else
        echo "   ⚠️  Decryption test failed (passphrase may be needed)"
        echo "   💡 This is normal — you'll set a passphrase when encrypting secrets"
    fi
else
    echo "   ⚠️  Encryption test failed"
    echo "   💡 GPG may need additional configuration"
fi

# Cleanup test files
rm -f "$TEST_FILE" "$TEST_ENC" "$TEST_DEC"

# Step 4: Summary
echo ""
echo "✅ GPG setup complete!"
echo ""
echo "   📁 GPG home: $GPG_DIR"
echo "   ⏱️  Cache TTL: ${CACHE_HOURS} hours"
echo "   🔐 Cipher: AES256"
echo ""
echo "💡 Next steps:"
echo "   # Encrypt high-value keys:"
echo "   ./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,CUSTODY_PRIVATE_KEY"
echo ""
echo "   # List encrypted keys:"
echo "   ./scripts/encrypt.py --list"
echo ""
