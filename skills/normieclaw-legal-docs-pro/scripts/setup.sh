#!/usr/bin/env bash
set -euo pipefail

# Legal Docs Pro — First-Time Setup
# Creates data directories and initializes business profile

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$SKILL_DIR/config"
SETTINGS_FILE="$CONFIG_DIR/settings.json"
DATA_DIR="$SKILL_DIR/data"

echo "⚖️  Legal Docs Pro — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p "$DATA_DIR/documents"
mkdir -p "$DATA_DIR/reviews"
mkdir -p "$DATA_DIR/exports"

# Set permissions on sensitive directories
chmod 700 "$CONFIG_DIR"
chmod 700 "$DATA_DIR"

echo "✓ Data directories created"
echo ""

# Check if settings already have a business name
CURRENT_NAME=$(python3 -c "import json; print(json.load(open('$SETTINGS_FILE'))['business_profile']['business_name'])" 2>/dev/null || echo "")

if [[ -n "$CURRENT_NAME" ]]; then
    echo "Existing business profile found: $CURRENT_NAME"
    echo ""
    read -rp "Do you want to update your profile? (y/N): " UPDATE
    if [[ ! "$UPDATE" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Setup complete. Your profile is unchanged."
        echo "To generate your first document, tell the agent:"
        echo '  "I need an NDA for a meeting with Acme Corp"'
        exit 0
    fi
fi

echo "Let's set up your business profile."
echo "Press Enter to skip any field — you can always update later."
echo ""

read -rp "Business name (legal entity name): " BIZ_NAME
read -rp "Business type (LLC, S-Corp, Sole Proprietor, etc.): " BIZ_TYPE
read -rp "Street address: " ADDRESS
read -rp "City: " CITY
read -rp "State: " STATE
read -rp "ZIP code: " ZIP
read -rp "State of formation (if different from above): " FORMATION_STATE
read -rp "EIN (e.g., 12-3456789, or leave blank): " EIN
read -rp "Your name (primary signatory): " OWNER_NAME
read -rp "Your title (e.g., Managing Member, CEO): " OWNER_TITLE
read -rp "Business email: " OWNER_EMAIL
read -rp "Business phone: " PHONE
read -rp "Website (optional): " WEBSITE
echo ""
read -rp "Default jurisdiction (e.g., State of Colorado): " JURISDICTION
read -rp "Standard payment terms (default: Net 30): " PAYMENT_TERMS
PAYMENT_TERMS="${PAYMENT_TERMS:-Net 30}"
read -rp "Late fee rate (default: 1.5% per month): " LATE_FEE
LATE_FEE="${LATE_FEE:-1.5% per month}"

# Use formation state or business state for default jurisdiction
if [[ -z "$FORMATION_STATE" ]]; then
    FORMATION_STATE="$STATE"
fi
if [[ -z "$JURISDICTION" && -n "$STATE" ]]; then
    JURISDICTION="State of $STATE"
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Write settings
python3 -c "
import json

settings = json.load(open('$SETTINGS_FILE'))

settings['business_profile']['business_name'] = '''$BIZ_NAME'''
settings['business_profile']['business_type'] = '''$BIZ_TYPE'''
settings['business_profile']['address'] = '''$ADDRESS'''
settings['business_profile']['city'] = '''$CITY'''
settings['business_profile']['state'] = '''$STATE'''
settings['business_profile']['zip'] = '''$ZIP'''
settings['business_profile']['state_of_formation'] = '''$FORMATION_STATE'''
settings['business_profile']['ein'] = '''$EIN'''
settings['business_profile']['owner_name'] = '''$OWNER_NAME'''
settings['business_profile']['owner_title'] = '''$OWNER_TITLE'''
settings['business_profile']['owner_email'] = '''$OWNER_EMAIL'''
settings['business_profile']['phone'] = '''$PHONE'''
settings['business_profile']['website'] = '''$WEBSITE'''
settings['defaults']['jurisdiction'] = '''$JURISDICTION'''
settings['defaults']['payment_terms'] = '''$PAYMENT_TERMS'''
settings['defaults']['late_fee_rate'] = '''$LATE_FEE'''
settings['metadata']['created'] = '''$TIMESTAMP'''
settings['metadata']['last_updated'] = '''$TIMESTAMP'''

with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2)
"

chmod 600 "$SETTINGS_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Business profile saved"
echo "✓ File permissions secured"
echo ""
echo "You're all set! Try these with your agent:"
echo ""
echo '  "I need an NDA for a freelance designer"'
echo '  "Review this contract for me" + paste contract text'
echo '  "Draft a demand letter — client owes me \$3,000"'
echo ""
echo "Your profile: $SETTINGS_FILE"
echo "To update later, tell the agent or edit the file directly."
echo ""
echo "⚠️  Legal Docs Pro provides templates and analysis for informational"
echo "   purposes. It is not a substitute for professional legal advice."
