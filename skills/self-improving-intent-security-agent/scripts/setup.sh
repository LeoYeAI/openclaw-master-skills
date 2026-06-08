#!/usr/bin/env bash
# Setup script for self-improving-intent-security-agent
# 
# This script creates the local .agent/ directory structure for intent tracking.
# It does NOT require any environment variables or credentials.
# All data stays local in the .agent/ directory.
#
# Optional environment variables (with defaults):
#   AGENT_INTENT_PATH - defaults to .agent/intents
#   AGENT_AUDIT_PATH  - defaults to .agent/audit
#   AGENT_LEARNING_ENABLED - defaults to true

set -e

echo "Setting up self-improving-intent-security-agent..."

# Create directory structure
mkdir -p .agent/{intents,violations,learnings,audit}
mkdir -p .agent/learnings/{strategies,patterns,antipatterns}
mkdir -p .agent/audit

echo "✓ Created directory structure"

# Copy templates if available
SKILL_DIR="$(dirname "$0")/.."
if [ -d "$SKILL_DIR/assets" ]; then
    cp "$SKILL_DIR/assets/INTENT-TEMPLATE.md" .agent/intents/ 2>/dev/null || true
    cp "$SKILL_DIR/assets/CONVERSATION-TEMPLATE.md" .agent/ 2>/dev/null || true
    cp "$SKILL_DIR/assets/VIOLATIONS.md" .agent/violations/ 2>/dev/null || true
    cp "$SKILL_DIR/assets/ANOMALIES.md" .agent/violations/ 2>/dev/null || true
    cp "$SKILL_DIR/assets/LEARNINGS.md" .agent/learnings/ 2>/dev/null || true
    cp "$SKILL_DIR/assets/STRATEGIES.md" .agent/learnings/ 2>/dev/null || true
    cp "$SKILL_DIR/assets/ROLLBACKS.md" .agent/audit/ 2>/dev/null || true
    echo "✓ Copied templates"
fi

# Create default config if it doesn't exist
if [ ! -f ".agent/config.json" ]; then
    cat > .agent/config.json <<'EOF'
{
  "security": {
    "requireApproval": ["file_delete", "api_write", "command_execution"],
    "autoRollback": true,
    "anomalyThreshold": 0.8,
    "maxPermissionScope": "read-write"
  },
  "learning": {
    "enabled": true,
    "minSampleSize": 10,
    "abTestRatio": 0.1,
    "maxStrategyComplexity": 100
  },
  "monitoring": {
    "metricsInterval": 1000,
    "auditLevel": "detailed",
    "retentionDays": 90
  }
}
EOF
    echo "✓ Created default config"
fi

# Add to .gitignore if it exists
if [ -f ".gitignore" ]; then
    if ! grep -q ".agent/" .gitignore; then
        echo "" >> .gitignore
        echo "# Agent data (optional - remove to track in git)" >> .gitignore
        echo ".agent/" >> .gitignore
        echo "✓ Added .agent/ to .gitignore"
    fi
fi

echo ""
echo "Setup complete! 🛡️🤖"
echo ""
echo "Next steps:"
echo "  1. Review configuration: .agent/config.json"
echo "  2. Set environment variables (see README.md)"
echo "  3. Create your first intent in .agent/intents/"
echo ""
echo "Documentation:"
echo "  - Quick start: SKILL.md"
echo "  - Examples: examples/README.md"
echo "  - Deep dive: references/"
