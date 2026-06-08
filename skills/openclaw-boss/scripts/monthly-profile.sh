#!/bin/bash
# Monthly User Profile Generator - 月度用户评价报告（增强版）
# 执行时间：每月 1 日 09:00
# 功能：生成月度深度报告，包含详细趋势分析

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="openclaw-boss"
REPORTS_DIR="/root/.openclaw/workspace/reports"
DATE=$(date +%Y-%m-%d)
MONTH=$(date +%Y-%m)
LOG_FILE="/root/.openclaw/workspace/logs/monthly-profile.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

echo "🦞 [$(date '+%Y-%m-%d %H:%M:%S')] 正在生成月度用户评价报告..." | tee -a "$LOG_FILE"
echo "   月份：$MONTH" | tee -a "$LOG_FILE"
echo "   日期：$DATE" | tee -a "$LOG_FILE"

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 运行分析脚本（最近 200 条会话，月报模式，包含详细引用）
python3 "$SCRIPT_DIR/analyze-user.py" \
    --limit 200 \
    --report-type monthly \
    --output "$REPORTS_DIR/monthly-profile-$DATE.md" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "✅ 月度报告生成完成！" | tee -a "$LOG_FILE"
echo "   报告位置：$REPORTS_DIR/monthly-profile-$DATE.md" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 可选：发送通知
# message send --channel telegram --message "📊 月度用户评价报告已生成：monthly-profile-$DATE.md"

echo "查看报告：cat $REPORTS_DIR/monthly-profile-$DATE.md" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
