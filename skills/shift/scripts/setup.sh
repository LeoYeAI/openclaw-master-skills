#!/bin/bash
# SHIFT — First-run setup script
# Creates the .shift directory structure, copies persona files, and initializes config

set -e

SHIFT_DIR="${HOME}/.openclaw/workspace/.shift"
WORKSPACE_DIR="${HOME}/.openclaw/workspace"
SKILL_DIR="${WORKSPACE_DIR}/skills/shift"
PERSONAS_SRC="${SKILL_DIR}/personas"
PERSONAS_DST="${SHIFT_DIR}/personas"
SESSIONS_DIR="${SHIFT_DIR}/sessions"
CONFIG_FILE="${SHIFT_DIR}/config.yaml"
COST_FILE="${SHIFT_DIR}/cost-tracking.json"

echo "🔧 SHIFT Setup"
echo "=============="
echo ""

# Create .shift directory structure
echo "📁 Creating .shift directory structure..."
mkdir -p "${PERSONAS_DST}"
mkdir -p "${SESSIONS_DIR}"
echo "   ✓ ${SHIFT_DIR}"
echo "   ✓ ${PERSONAS_DST}"
echo "   ✓ ${SESSIONS_DIR}"

# Initialize cost tracking
echo ""
echo "📊 Initializing cost tracking..."
cat > "${COST_FILE}" << 'COSTEOF'
{
  "hourStart": "",
  "totalSpend": 0,
  "delegations": []
}
COSTEOF
echo "   ✓ ${COST_FILE}"

# Copy persona files to workspace
echo ""
echo "👤 Copying persona files to workspace..."
for persona in CODEX RESEARCHER RUNNER; do
    src="${PERSONAS_SRC}/${persona}.yaml"
    dst="${PERSONAS_DST}/${persona}.yaml"
    if [ -f "${src}" ]; then
        cp "${src}" "${dst}"
        echo "   ✓ ${persona}.yaml"
    else
        echo "   ✗ ${persona}.yaml not found in skill directory"
    fi
done

# Create config from SCHEMA if not exists
if [ ! -f "${CONFIG_FILE}" ]; then
    echo ""
    echo "⚙️  Creating configuration from schema..."
    if [ -f "${SKILL_DIR}/config/SCHEMA.yaml" ]; then
        cp "${SKILL_DIR}/config/SCHEMA.yaml" "${CONFIG_FILE}"
        echo "   ✓ ${CONFIG_FILE}"
        echo ""
        echo "⚠️  IMPORTANT: Edit ${CONFIG_FILE}"
        echo "   You need to set your models in the personas section."
        echo "   Look for 'model:' in each persona block and set your actual model IDs."
        echo "   The skill is model-agnostic — use any model you have access to."
    else
        echo "   ✗ SCHEMA.yaml not found at ${SKILL_DIR}/config/SCHEMA.yaml"
    fi
else
    echo ""
    echo "✓ Config already exists at ${CONFIG_FILE}"
fi

# Create .gitkeep in sessions to preserve directory
touch "${SESSIONS_DIR}/.gitkeep"

echo ""
echo "✅ SHIFT setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit ${CONFIG_FILE}"
echo "   → Set your models for each persona (codex, researcher, runner)"
echo "   → Example: model: openai-codex/gpt-5.3-codex"
echo "2. Restart your OpenClaw gateway"
echo "3. Try: /shift status"
echo ""
