#!/bin/bash
# Turing Pyramid — Initialization Script
# Run once on skill installation

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
TEMPLATE_FILE="$SKILL_DIR/assets/needs-state.template.json"

echo "🔺 Turing Pyramid — Initialization"
echo "=================================="

# Check if already initialized
if [[ -f "$STATE_FILE" ]]; then
    echo "⚠️  State file already exists: $STATE_FILE"
    read -p "   Reinitialize? This will reset all needs. (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "   Aborted."
        exit 0
    fi
fi

# Get current timestamp
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create state file from template with current timestamps
# Also initialize surplus fields for spontaneity tracking
jq --arg now "$NOW" '
  ._meta.initialized = $now |
  ._meta.last_cycle = $now |
  .needs |= with_entries(.value.last_satisfied = $now | .value.surplus = 0 | .value.last_surplus_check = $now | .value.last_high_action_at = $now | .value.last_spontaneous_at = $now)
' "$TEMPLATE_FILE" > "$STATE_FILE"

# Create baseline context snapshot (prevents noisy first run)
CONTEXT_SCAN="$SKILL_DIR/scripts/context-scan.sh"
if [[ -x "$CONTEXT_SCAN" ]]; then
    echo ""
    echo "📸 Creating baseline context snapshot..."
    # Run scan to capture baseline, then clear cooldowns so triggers aren't pre-blocked
    "$CONTEXT_SCAN" > /dev/null 2>&1 || true
    SNAPSHOT_NAME=$(jq -r '.snapshot_file // "last-scan-snapshot.json"' "$SKILL_DIR/assets/context-triggers.json" 2>/dev/null || echo "last-scan-snapshot.json")
    SNAP_FILE="$SKILL_DIR/assets/$SNAPSHOT_NAME"
    if [[ -f "$SNAP_FILE" ]]; then
        jq '.trigger_cooldowns = {}' "$SNAP_FILE" > "$SNAP_FILE.tmp" && mv "$SNAP_FILE.tmp" "$SNAP_FILE"
    fi
    echo "   Snapshot created — first cycle won't fire all triggers at once"
fi

echo "✅ State file created: $STATE_FILE"
echo "   All needs initialized to satisfaction=3 (full)"
echo ""
echo "📋 Next steps:"
echo "   1. Review assets/needs-config.json"
echo "   2. Run bootstrap (processes ALL needs once):"
echo "      ./scripts/run-cycle.sh --bootstrap"
echo "   3. Add to HEARTBEAT.md:"
echo "      source $SKILL_DIR/scripts/run-cycle.sh"
echo ""
echo "🤝 Discuss with your agent:"
echo "   - Are the decay rates right for you?"
echo "   - Is the importance hierarchy correct?"
echo "   - What actions actually satisfy each need?"
