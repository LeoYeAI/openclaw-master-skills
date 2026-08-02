#!/bin/bash
# Voice Memo Sync - Installation Script
# Usage: ./install.sh [--with-heartbeat]

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$WORKSPACE/skills/voice-memo-sync"
DATA_DIR="$WORKSPACE/memory/voice-memos"
CONFIG_DIR="$WORKSPACE/config"
HEARTBEAT_FILE="$WORKSPACE/HEARTBEAT.md"

# Parse arguments
WITH_HEARTBEAT=false
for arg in "$@"; do
    case $arg in
        --with-heartbeat) WITH_HEARTBEAT=true ;;
    esac
done

# Function: Add heartbeat task
add_heartbeat_task() {
    local TASK_MARKER="# Voice Memo Sync Auto-Sync"
    
    if [ -f "$HEARTBEAT_FILE" ] && grep -q "$TASK_MARKER" "$HEARTBEAT_FILE"; then
        echo "  ℹ️  Heartbeat task already configured"
        return
    fi
    
    echo "  Adding task to HEARTBEAT.md..."
    
    cat >> "$HEARTBEAT_FILE" << 'HEARTBEAT'

# ============================================
# Voice Memo Sync Auto-Sync
# ============================================

Task: Voice Memo Daily Sync
- Time: 08:00 daily
- Action: Sync and process new voice memos
- Steps:
  1. Scan Voice Memos directory for new .qta/.m4a files
  2. Extract Apple native transcripts
  3. Process with LLM (summarize, extract key points)
  4. Sync to Apple Notes "Voice Memos" folder
  5. Create Reminders for TODOs
  6. Update INDEX.md
- Config: config/voice-memo-sync.yaml
- Output: memory/voice-memos/

Checklist:
[ ] New voice memos since last sync?
[ ] Process each new recording
[ ] Update INDEX.md with results
HEARTBEAT
    
    echo "  ✅ Heartbeat task added"
}

echo "🎙️ Voice Memo Sync - Installation"
echo "=================================="

# 1. Create data directories
echo "📁 Creating data directories..."
mkdir -p "$DATA_DIR"/{sources,transcripts,processed,synced}

# 2. Create symlink
if [ ! -L "$SKILL_DIR/data" ]; then
    echo "🔗 Creating data symlink..."
    ln -sf "$DATA_DIR" "$SKILL_DIR/data"
fi

# 3. Create config file
if [ ! -f "$CONFIG_DIR/voice-memo-sync.yaml" ]; then
    echo "⚙️  Creating default config..."
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_DIR/voice-memo-sync.yaml" << 'YAML'
# Voice Memo Sync Configuration

sources:
  voice_memos:
    enabled: true
    path: "~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/"
  icloud:
    enabled: true
    paths:
      - "~/Library/Mobile Documents/com~apple~CloudDocs/Recordings"
    watch_patterns: ["*.m4a", "*.mp3", "*.mp4", "*.wav", "*.qta"]

transcription:
  priority: ["apple", "text", "summarize", "whisper-local"]
  whisper_model: "small"
  language: "auto"

notes:
  folder: "Voice Memos"
  include_original: true

reminders:
  enabled: true
  list: "Reminders"

auto_sync:
  enabled: false
  time: "08:00"
YAML
fi

# 4. Create INDEX.md
if [ ! -f "$DATA_DIR/INDEX.md" ]; then
    echo "📋 Creating index file..."
    cat > "$DATA_DIR/INDEX.md" << 'MD'
# Voice Memo Sync - Index

| Date | Source | Title | Status |
|------|--------|-------|--------|

*Last updated: Initialized*
MD
fi

# 5. Check dependencies
echo ""
echo "🔧 Checking dependencies..."
for dep in ffmpeg python3; do
    command -v "$dep" &>/dev/null && echo "  ✅ $dep" || echo "  ❌ $dep (required)"
done
for dep in whisper-cpp whisper yt-dlp remindctl summarize; do
    if [ "$dep" = "whisper-cpp" ]; then
        command -v "$dep" &>/dev/null && echo "  ✅ $dep (Metal GPU - recommended)" || echo "  ⚠️  $dep (Metal GPU - brew install whisper-cpp)"
    else
        command -v "$dep" &>/dev/null && echo "  ✅ $dep" || echo "  ⚠️  $dep (optional)"
    fi
done

# 6. Create Apple Notes folder
echo ""
echo "📝 Setting up Apple Notes..."
osascript -e 'tell application "Notes" to tell account "iCloud" to if not (exists folder "Voice Memos") then make new folder with properties {name:"Voice Memos"}' 2>/dev/null || true
echo "  ✅ Voice Memos folder ready"

# 7. Configure heartbeat auto-sync
echo ""
if [ "$WITH_HEARTBEAT" = true ]; then
    echo "⏰ Configuring heartbeat auto-sync..."
    add_heartbeat_task
elif [ -t 0 ]; then
    echo "⏰ Enable daily auto-sync via heartbeat?"
    echo "   New voice memos will be automatically synced at 08:00 daily."
    read -p "   Enable? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        add_heartbeat_task
    else
        echo "   Skipped. Run './install.sh --with-heartbeat' to enable later."
    fi
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  • Send voice files → I'll organize them"
echo "  • Say 'sync voice memos'"
echo "  • Send YouTube/Bilibili URLs"
echo "  • Send transcript text files"
