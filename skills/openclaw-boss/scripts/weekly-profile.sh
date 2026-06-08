#!/bin/bash
# Weekly User Profile Generator - 周度用户评价报告（增强版）
# 执行时间：每周日 22:00
# 功能：生成周度报告，包含周期成长追踪

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="openclaw-boss"
REPORTS_DIR="/root/.openclaw/workspace/reports"
DATE=$(date +%Y-%m-%d)
WEEK=$(date +%Y-W%W)
LOG_FILE="/root/.openclaw/workspace/logs/weekly-profile.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

echo "🦞 [$(date '+%Y-%m-%d %H:%M:%S')] 正在生成周度用户评价报告..." | tee -a "$LOG_FILE"
echo "   周次：$WEEK" | tee -a "$LOG_FILE"
echo "   日期：$DATE" | tee -a "$LOG_FILE"

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 运行分析脚本（最近 50 条会话，周报模式）
python3 "$SCRIPT_DIR/analyze-user.py" \
    --limit 50 \
    --report-type weekly \
    --output "$REPORTS_DIR/weekly-profile-$DATE.md" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "✅ 周度报告生成完成！" | tee -a "$LOG_FILE"
echo "   报告位置：$REPORTS_DIR/weekly-profile-$DATE.md" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 可选：发送通知（如果有通知渠道）
# message send --channel telegram --message "📊 周度用户评价报告已生成：weekly-profile-$DATE.md"

echo "查看报告：cat $REPORTS_DIR/weekly-profile-$DATE.md" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
