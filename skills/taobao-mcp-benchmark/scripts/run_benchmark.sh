#!/bin/bash
# 淘宝桌面版MCP评测启动脚本
# 用法: ./run_benchmark.sh [task_id]

set -e

# 配置
SKILL_DIR="$HOME/.copaw/active_skills/taobao-mcp-benchmark"
TASKS_DIR="$HOME/.copaw/tasks"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TASK_ID="${1:-benchmark_$TIMESTAMP}"

echo "============================================"
echo "📊 淘宝桌面版MCP评测"
echo "============================================"
echo ""
echo "任务ID: $TASK_ID"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建任务目录
TASK_DIR="$TASKS_DIR/$TASK_ID"
mkdir -p "$TASK_DIR/screenshots"

# 复制任务模板
cp "$SKILL_DIR/templates/task_template.json" "$TASK_DIR/task.json"

# 替换变量
sed -i '' "s/\${timestamp}/$TIMESTAMP/g" "$TASK_DIR/task.json"
sed -i '' "s/\${datetime}/$(date -Iseconds)/g" "$TASK_DIR/task.json"

echo "✅ 任务目录已创建: $TASK_DIR"
echo ""
echo "下一步："
echo "1. 执行4个评测任务（淘金币签到、商品搜索、订单管理、购物车比价）"
echo "2. 保存截图到 $TASK_DIR/screenshots/"
echo "3. 更新 $TASK_DIR/task.json 中的评测结果"
echo "4. 运行 ./generate_report.sh $TASK_ID 生成报告"
echo ""
echo "============================================"