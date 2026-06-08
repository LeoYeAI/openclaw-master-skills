#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Supercharged Daily Briefing — Scheduler Helper
# ============================================================
# This script validates the workspace environment and triggers
# the briefing generation pipeline. Designed to be called by
# OpenClaw cron hooks or Trigger.dev.
#
# Usage:
#   ./scripts/briefing-scheduler.sh [--check|--run|--status]
#
# Options:
#   --check   Validate workspace setup (files exist, permissions OK)
#   --run     Signal the agent to generate and deliver the briefing
#   --status  Show current schedule and source health summary
# ============================================================

# --- Workspace Root Detection ---
# Walk up the directory tree to find workspace root (contains AGENTS.md or SOUL.md)
find_workspace_root() {
    local dir
    dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    
    # Start from script's parent directory and walk up
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/AGENTS.md" ] || [ -f "$dir/SOUL.md" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    
    echo "ERROR: Could not find workspace root (no AGENTS.md or SOUL.md found)" >&2
    return 1
}

WORKSPACE_ROOT="$(find_workspace_root)"
cd "$WORKSPACE_ROOT"

# --- File Paths (relative to workspace root) ---
CONFIG_FILE="config/briefing-config.json"
SOURCES_FILE="data/briefing-sources.json"
FEEDBACK_FILE="data/briefing-feedback.json"
ARCHIVE_DIR="data/briefing-archive"

# --- Validation ---
validate_setup() {
    local errors=0
    
    echo "🔍 Validating Supercharged Daily Briefing setup..."
    echo "   Workspace root: $WORKSPACE_ROOT"
    echo ""
    
    # Check required files
    for f in "$CONFIG_FILE" "$SOURCES_FILE"; do
        if [ -f "$f" ]; then
            echo "   ✅ $f"
        else
            echo "   ❌ $f — MISSING"
            errors=$((errors + 1))
        fi
    done
    
    # Check required directories
    for d in "data" "config" "scripts" "$ARCHIVE_DIR"; do
        if [ -d "$d" ]; then
            echo "   ✅ $d/"
        else
            echo "   ❌ $d/ — MISSING"
            errors=$((errors + 1))
        fi
    done
    
    # Check permissions
    if [ -f "$CONFIG_FILE" ]; then
        local perms
        perms=$(stat -f "%Lp" "$CONFIG_FILE" 2>/dev/null || stat -c "%a" "$CONFIG_FILE" 2>/dev/null)
        if [ "$perms" = "600" ]; then
            echo "   ✅ Config permissions: 600"
        else
            echo "   ⚠️  Config permissions: $perms (recommended: 600)"
        fi
    fi
    
    if [ -f "$SOURCES_FILE" ]; then
        local perms
        perms=$(stat -f "%Lp" "$SOURCES_FILE" 2>/dev/null || stat -c "%a" "$SOURCES_FILE" 2>/dev/null)
        if [ "$perms" = "600" ]; then
            echo "   ✅ Sources permissions: 600"
        else
            echo "   ⚠️  Sources permissions: $perms (recommended: 600)"
        fi
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo "✅ All checks passed. Briefing system is ready."
    else
        echo "❌ $errors issue(s) found. Run the setup prompt to fix."
    fi
    
    return $errors
}

# --- Status ---
show_status() {
    echo "📊 Supercharged Daily Briefing — Status"
    echo ""
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "❌ Not configured. Run setup first."
        return 1
    fi
    
    # Show schedule
    local delivery_time active
    delivery_time=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['schedule']['delivery_time'])" 2>/dev/null || echo "unknown")
    active=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['schedule']['active'])" 2>/dev/null || echo "unknown")
    
    echo "⏰ Delivery time: $delivery_time"
    echo "📡 Active: $active"
    
    # Show topic count
    local topic_count
    topic_count=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(len(c['topics']))" 2>/dev/null || echo "0")
    echo "📌 Topics: $topic_count"
    
    # Show source count and health
    if [ -f "$SOURCES_FILE" ]; then
        local total_sources active_sources failing_sources
        total_sources=$(python3 -c "import json; s=json.load(open('$SOURCES_FILE')); print(len(s['sources']))" 2>/dev/null || echo "0")
        active_sources=$(python3 -c "import json; s=json.load(open('$SOURCES_FILE')); print(len([x for x in s['sources'] if x.get('active',True)]))" 2>/dev/null || echo "0")
        failing_sources=$(python3 -c "import json; s=json.load(open('$SOURCES_FILE')); print(len([x for x in s['sources'] if x.get('fetch_failures',0)>=3]))" 2>/dev/null || echo "0")
        
        echo "📡 Sources: $active_sources active / $total_sources total"
        if [ "$failing_sources" != "0" ]; then
            echo "⚠️  Failing sources: $failing_sources"
        fi
    fi
    
    # Show archive count
    if [ -d "$ARCHIVE_DIR" ]; then
        local archive_count
        archive_count=$(find "$ARCHIVE_DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
        echo "📁 Archived briefings: $archive_count"
    fi
}

# --- Run Signal ---
signal_run() {
    echo "🚀 Triggering briefing generation..."
    
    # Validate first
    if ! validate_setup > /dev/null 2>&1; then
        echo "❌ Setup validation failed. Run --check for details."
        return 1
    fi
    
    # Check if active
    local active
    active=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['schedule']['active'])" 2>/dev/null || echo "false")
    
    if [ "$active" = "False" ] || [ "$active" = "false" ]; then
        echo "⏸️  Briefing is paused. Resume with: 'resume briefings'"
        return 0
    fi
    
    # Check if topics are configured
    local topic_count
    topic_count=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(len(c['topics']))" 2>/dev/null || echo "0")
    
    if [ "$topic_count" = "0" ]; then
        echo "❌ No topics configured. Tell your agent what topics to track first."
        return 1
    fi
    
    echo "✅ Pre-flight checks passed. Agent should now run the briefing pipeline."
    echo "   Topics: $topic_count | Sources: $(python3 -c "import json; s=json.load(open('$SOURCES_FILE')); print(len([x for x in s['sources'] if x.get('active',True)]))" 2>/dev/null || echo "0") active"
}

# --- Main ---
case "${1:---check}" in
    --check)
        validate_setup
        ;;
    --run)
        signal_run
        ;;
    --status)
        show_status
        ;;
    *)
        echo "Usage: $0 [--check|--run|--status]"
        exit 1
        ;;
esac
