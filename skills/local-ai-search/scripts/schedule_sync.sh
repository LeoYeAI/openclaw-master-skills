#!/bin/bash
# 定时同步脚本 - 设置 cron 定时任务，每小时自动同步
# 使用方法: ./schedule_sync.sh <目录> [小时间隔]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync.py"
LOG_DIR="$HOME/.khoj/logs"
LOG_FILE="$LOG_DIR/sync.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "使用方法: $0 <目录> [选项]"
    echo ""
    echo "选项:"
    echo "  --interval <小时>   同步间隔（默认: 1 小时）"
    echo "  --enable            启用定时同步"
    echo "  --disable           禁用定时同步"
    echo "  --status            查看定时同步状态"
    echo "  --run               立即执行一次同步"
    echo ""
    echo "示例:"
    echo "  $0 ~/Documents --enable              # 启用每小时同步"
    echo "  $0 ~/Documents --interval 2 --enable # 每2小时同步一次"
    echo "  $0 ~/Documents --disable             # 禁用定时同步"
    echo "  $0 --status                          # 查看状态"
    exit 1
}

setup_cron() {
    local directory="$1"
    local interval="$2"
    
    # 验证目录
    if [ ! -d "$directory" ]; then
        echo -e "${RED}错误: 目录不存在 - $directory${NC}"
        exit 1
    fi
    
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    # 创建 cron 任务
    local cron_job="0 */$interval * * * $SYNC_SCRIPT \"$directory\" >> \"$LOG_FILE\" 2>&1"
    
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
        echo -e "${YELLOW}定时任务已存在，正在更新...${NC}"
        # 移除旧任务
        crontab -l 2>/dev/null | grep -v "$SYNC_SCRIPT" | crontab -
    fi
    
    # 添加新任务
    (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    
    echo -e "${GREEN}✓ 已设置定时同步${NC}"
    echo "  目录: $directory"
    echo "  间隔: 每 $interval 小时"
    echo "  日志: $LOG_FILE"
    echo ""
    echo "查看日志: tail -f $LOG_FILE"
}

disable_cron() {
    if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
        crontab -l 2>/dev/null | grep -v "$SYNC_SCRIPT" | crontab -
        echo -e "${GREEN}✓ 已禁用定时同步${NC}"
    else
        echo -e "${YELLOW}定时同步未启用${NC}"
    fi
}

show_status() {
    echo "=== 定时同步状态 ==="
    
    if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
        echo -e "状态: ${GREEN}已启用${NC}"
        echo ""
        echo "Cron 任务:"
        crontab -l 2>/dev/null | grep "$SYNC_SCRIPT"
        echo ""
        
        if [ -f "$LOG_FILE" ]; then
            echo "最近日志:"
            tail -10 "$LOG_FILE"
        fi
    else
        echo -e "状态: ${YELLOW}未启用${NC}"
    fi
}

run_sync() {
    local directory="$1"
    
    if [ -z "$directory" ]; then
        echo -e "${RED}错误: 请指定要同步的目录${NC}"
        usage
    fi
    
    echo -e "${YELLOW}开始同步...${NC}"
    python3 "$SYNC_SCRIPT" "$directory" --verbose
}

# 解析参数
DIRECTORY=""
INTERVAL=1
ACTION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --enable)
            ACTION="enable"
            shift
            ;;
        --disable)
            ACTION="disable"
            shift
            ;;
        --status)
            ACTION="status"
            shift
            ;;
        --run)
            ACTION="run"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [ -z "$DIRECTORY" ]; then
                DIRECTORY="$1"
            fi
            shift
            ;;
    esac
done

# 执行操作
case $ACTION in
    enable)
        if [ -z "$DIRECTORY" ]; then
            echo -e "${RED}错误: 请指定要同步的目录${NC}"
            usage
        fi
        setup_cron "$DIRECTORY" "$INTERVAL"
        ;;
    disable)
        disable_cron
        ;;
    status)
        show_status
        ;;
    run)
        run_sync "$DIRECTORY"
        ;;
    *)
        if [ -n "$DIRECTORY" ]; then
            run_sync "$DIRECTORY"
        else
            usage
        fi
        ;;
esac