#!/usr/bin/env bash
# TSA 批量发布快速启动脚本

set -euo pipefail

cd "$(dirname "$0")"

echo "🚀 TSA ClawHub 批量发布工具"
echo "================================"
echo ""

# 检查 nvm
if command -v nvm &> /dev/null; then
    echo "✓ 使用 nvm 20"
    nvm use 20
else
    echo "! nvm 未安装，跳过 node 版本检查"
fi

echo ""
echo "📊 查看发布记录..."
python3 view_publish_log.py 2>/dev/null || echo "（暂无发布记录）"

echo ""
echo "================================"
echo "准备开始发布..."
echo ""
read -p "是否继续？(y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "🚀 开始发布..."
python3 batch_publish.py
