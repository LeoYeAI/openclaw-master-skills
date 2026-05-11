#!/bin/bash
# start-monitor.sh - 启动闲鱼监控子代理
# 使用方法：./start-monitor.sh

set -e

# 配置
AGENT_LABEL="xianyu-monitor"
AGENT_ID="main"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/xianyu-monitor-agent.sh"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐟 闲鱼自动发货监控 - 子代理启动${NC}"
echo ""

# 检查脚本是否存在
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "❌ 监控脚本不存在：$MONITOR_SCRIPT"
    exit 1
fi

# 检查 agent-browser
if ! command -v agent-browser &> /dev/null; then
    echo "❌ agent-browser 未安装"
    echo "💡 请运行：npm install -g agent-browser && agent-browser install"
    exit 1
fi

echo -e "${YELLOW}📋 任务配置：${NC}"
echo "   - 标签：$AGENT_LABEL"
echo "   - 监控脚本：$MONITOR_SCRIPT"
echo "   - 检查间隔：60秒"
echo ""

echo -e "${YELLOW}🚀 启动子代理会话...${NC}"
echo ""

# 构建任务描述
TASK="启动闲鱼监控代理，每分钟检查一次闲鱼新消息。
工作流程：
1. 检查是否有新消息
2. 如果有新消息，进入聊天查看
3. 检查是否需要发货（检测付款卡片）
4. 如果需要发货，执行发货流程（使用模板：02-key-pool.sh）
5. 返回聊天列表，等待下一次检查

监控脚本位置：$MONITOR_SCRIPT

注意事项：
- 使用 agent-browser 进行网页自动化
- 使用 Chrome 用户配置文件保持登录状态
- 每次检查后等待60秒
- 日志记录在：fulfillment-YYYYMMDD.log"

# 使用 sessions_spawn 启动子代理
# 注意：这里假设 sessions_spawn 是通过 openclaw 命令行调用的
# 如果不支持直接调用，需要手动使用 openclaw CLI

echo "📝 任务已配置"
echo ""
echo "💡 启动方式："
echo ""
echo "方式 1：使用 OpenClaw 命令行"
echo "--------------------------------"
echo "openclaw sessions_spawn \\"
echo "  --mode session \\"
echo "  --label \"$AGENT_LABEL\" \\"
echo "  --agentId \"$AGENT_ID\" \\"
echo "  --task \"$TASK\""
echo ""
echo "方式 2：直接运行监控脚本（推荐测试用）"
echo "--------------------------------"
echo "chmod +x $MONITOR_SCRIPT"
echo "$MONITOR_SCRIPT"
echo ""
echo "方式 3：在 OpenClaw 对话中启动"
echo "--------------------------------"
echo "告诉我：'启动闲鱼监控子代理'"
echo ""
echo -e "${GREEN}✅ 配置完成！${NC}"
echo ""
echo "请选择以上任一方式启动监控代理。"
