#!/bin/bash
# Memora v4.0 - 刷新每日任务
# 用法：./refresh-quests.sh <Agent 名称> [日期]

set -e

AGENT_NAME="${1:-}"
DATE="${2:-$(date +%Y-%m-%d)}"

if [ -z "$AGENT_NAME" ]; then
    echo "用法：$0 <Agent 名称> [日期]"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$SCRIPT_DIR/../core"

cd "$CORE_DIR"

echo ""
echo "=== 📅 刷新 $AGENT_NAME 的每日任务 ($DATE) ==="
echo ""

# 刷新任务
python3 daily_quest.py "$AGENT_NAME" refresh

echo ""
