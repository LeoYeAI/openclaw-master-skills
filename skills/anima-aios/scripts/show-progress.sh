#!/bin/bash
# Memora v4.0 - 显示认知进度
# 用法：./show-progress.sh <Agent 名称>

set -e

AGENT_NAME="${1:-}"

if [ -z "$AGENT_NAME" ]; then
    echo "用法：$0 <Agent 名称>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$SCRIPT_DIR/../core"

cd "$CORE_DIR"

echo ""
echo "=== 🧠 $AGENT_NAME 的认知画像 ==="
echo ""

# 生成认知画像
python3 cognitive_profile.py "$AGENT_NAME"

echo ""
