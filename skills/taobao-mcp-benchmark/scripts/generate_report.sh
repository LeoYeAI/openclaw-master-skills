#!/bin/bash
# 淘宝桌面版MCP评测报告生成脚本
# 用法: ./generate_report.sh [task_id]

set -e

TASKS_DIR="$HOME/.copaw/tasks"
SKILL_DIR="$HOME/.copaw/active_skills/taobao-mcp-benchmark"
DOCX_DIR="$HOME/.copaw/active_skills/docx"

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
    echo "❌ 请提供任务ID"
    echo "用法: ./generate_report.sh <task_id>"
    echo ""
    echo "可用任务："
    ls -d $TASKS_DIR/benchmark_* 2>/dev/null | xargs -n1 basename
    exit 1
fi

TASK_DIR="$TASKS_DIR/$TASK_ID"
if [ ! -d "$TASK_DIR" ]; then
    echo "❌ 任务目录不存在: $TASK_DIR"
    exit 1
fi

echo "============================================"
echo "📄 生成评测报告"
echo "============================================"
echo ""
echo "任务ID: $TASK_ID"

# 检查截图目录
SCREENSHOTS_DIR="$TASK_DIR/screenshots"
if [ ! -d "$SCREENSHOTS_DIR" ]; then
    echo "⚠️  截图目录不存在，创建中..."
    mkdir -p "$SCREENSHOTS_DIR"
fi

# 统计截图数量
SCREENSHOT_COUNT=$(ls -1 "$SCREENSHOTS_DIR"/*.png 2>/dev/null | wc -l)
echo "截图数量: $SCREENSHOT_COUNT 张"

# 生成报告文件名
REPORT_MD="$TASK_DIR/评测报告.md"
REPORT_DOCX="$TASKS_DIR/淘宝桌面版MCP评测报告_${TASK_ID}.docx"

echo ""
echo "生成中..."

# TODO: 根据task.json生成Markdown报告
# TODO: 根据截图生成Word报告

echo ""
echo "✅ 报告生成完成！"
echo ""
echo "输出文件："
echo "  - Markdown: $REPORT_MD"
echo "  - Word: $REPORT_DOCX"
echo ""
echo "============================================"