#!/bin/bash
# Create your first Archon DID and set up secure environment
# Run this once when setting up Archon for the first time
#
# Usage: ./create-id.sh [wallet-path]
#   wallet-path: Optional. Default: ~/.archon.wallet.json

set -e

echo "=== Archon Identity Setup ==="
echo ""

# Determine wallet path
DEFAULT_WALLET="$HOME/.archon.wallet.json"
if [ -n "$1" ]; then
    WALLET_PATH="$1"
else
    echo "Where should your wallet be stored?"
    echo "  Default: $DEFAULT_WALLET"
    read -p "Wallet path [$DEFAULT_WALLET]: " input_path
    WALLET_PATH="${input_path:-$DEFAULT_WALLET}"
fi

# Expand ~ if present
WALLET_PATH="${WALLET_PATH/#\~/$HOME}"

# Validate wallet path (reject shell metacharacters that could cause injection)
if [[ "$WALLET_PATH" =~ [\$\`\"\'\;] ]] || [[ "$WALLET_PATH" =~ $'\n' ]]; then
    echo "ERROR: Wallet path contains invalid characters (\$, \`, \", ', ;, or newlines)"
    echo "Please use a simple path like: ~/.archon.wallet.json"
    exit 1
fi

echo ""
echo "Using wallet path: $WALLET_PATH"
echo ""

# Check if wallet already exists at the chosen path
if [ -f "$WALLET_PATH" ]; then
    echo "ERROR: Wallet already exists at $WALLET_PATH"
    echo ""
    echo "If you want to create a new identity in your existing wallet, use:"
    echo "  ./scripts/identity/create-additional-id.sh <did-name>"
    echo ""
    echo "If you want to start over (WARNING: will lose existing DIDs), remove:"
    echo "  rm \"$WALLET_PATH\" ~/.archon.env"
    exit 1
fi

# Check if .archon.env already exists
if [ -f ~/.archon.env ]; then
    echo "WARNING: ~/.archon.env already exists"
    read -p "Overwrite? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# Generate secure passphrase (or let user provide one)
echo "Generating secure passphrase..."
PASSPHRASE=$(openssl rand -base64 32 | tr -d '/+=' | cut -c1-32)

# Create .archon.env
echo "Creating ~/.archon.env..."
cat > ~/.archon.env << EOF
# Archon environment configuration
# DO NOT COMMIT THIS FILE TO GIT

# Wallet location (required by all archon-keymaster scripts)
export ARCHON_WALLET_PATH="$WALLET_PATH"

# Passphrase for wallet encryption
export ARCHON_PASSPHRASE="$PASSPHRASE"

# Gatekeeper URL (public gatekeeper has 10MB limit)
export ARCHON_GATEKEEPER_URL="https://archon.technology"
# For local gatekeeper (unlimited): export ARCHON_GATEKEEPER_URL="http://localhost:4224"
EOF

chmod 600 ~/.archon.env
echo "✓ Environment saved to ~/.archon.env (chmod 600)"

# Source it for this session
source ~/.archon.env

# Create wallet directory if needed
WALLET_DIR=$(dirname "$WALLET_PATH")
if [ ! -d "$WALLET_DIR" ]; then
    mkdir -p "$WALLET_DIR"
    echo "✓ Created directory: $WALLET_DIR"
fi

# Create wallet first
echo ""
echo "Creating wallet..."
echo ""

WALLET_OUTPUT=$(npx @didcid/keymaster create-wallet 2>&1)
echo "$WALLET_OUTPUT"

# Display mnemonic explicitly (CLI no longer prints it during create-wallet)
npx @didcid/keymaster show-mnemonic | tr -d '\r'
echo ""
echo "=========================================="
echo "  SAVE YOUR MNEMONIC (12 words above)    "
echo "=========================================="
echo ""

# Prompt for DID name
read -p "Name for your DID (e.g., 'main', 'work'): " DID_NAME
DID_NAME="${DID_NAME:-main}"

echo ""
echo "Creating DID '$DID_NAME'..."
npx @didcid/keymaster create-id "$DID_NAME"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "✓ Wallet created: $WALLET_PATH"
echo "✓ DID created: $DID_NAME"
echo "✓ Environment configured: ~/.archon.env"
echo ""
echo "CRITICAL: Your 12-word mnemonic was displayed above."
echo "         Write it down and store it offline (paper, metal plate, etc.)"
echo "         This is the ONLY way to recover your identity."
echo ""
echo "To use your DID in other terminal sessions, run:"
echo "  source ~/.archon.env"
echo ""
echo "Next steps:"
echo "  - Save your mnemonic securely (offline!)"
echo "  - Set up backups: archon-backup skill"
echo "  - Backup wallet to seed bank: npx @didcid/keymaster backup-wallet-did"
echo ""
echo "View your DIDs:"
echo "  npx @didcid/keymaster list-ids"
