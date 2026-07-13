#!/bin/bash

# Video Summary - Configuration Status Query
# Returns current setup state for OpenClaw to determine next question

set -e

CONFIG_DIR="$HOME/.config/video-summary"
CONFIG_FILE="$CONFIG_DIR/config.sh"
STATE_FILE="$CONFIG_DIR/setup-state.json"

# Check if already fully configured
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE" 2>/dev/null || true
    if [[ -n "$OPENAI_API_KEY" ]]; then
        echo '{"status": "complete", "message": "video-summary 已配置完成"}'
        exit 0
    fi
fi

# Check if state file exists
if [[ ! -f "$STATE_FILE" ]]; then
    echo '{"status": "not_started", "current_step": "api_provider", "message": "配置未开始"}'
    exit 0
fi

# Return current state
cat "$STATE_FILE"
