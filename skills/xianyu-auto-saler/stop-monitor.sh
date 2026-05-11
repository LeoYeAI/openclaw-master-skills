#!/bin/bash
# stop-monitor.sh - 停止闲鱼监控子代理
# 使用方法：./stop-monitor.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}🛑 停止闲鱼监控子代理${NC}"
echo ""

AGENT_LABEL="xianyu-monitor"

echo -e "${YELLOW}📋 停止方式：${NC}"
echo ""
echo "方式 1：在 OpenClaw 对话中停止"
echo "--------------------------------"
echo "告诉我：'停止闲鱼监控' 或 '终止子代理 xianyu-monitor'"
echo ""
echo "方式 2：使用 subagents 命令（如果支持）"
echo "--------------------------------"
echo "openclaw subagents --action list"
echo "openclaw subagents --action kill --target \"$AGENT_LABEL\""
echo ""
echo "方式 3：手动终止进程"
echo "--------------------------------"
echo "查找并终止监控脚本进程："
echo "ps aux | grep xianyu-monitor-agent.sh"
echo "kill <PID>"
echo ""
echo -e "${GREEN}✅ 说明完成！${NC}"
echo ""
echo "请选择以上任一方式停止监控代理。"
