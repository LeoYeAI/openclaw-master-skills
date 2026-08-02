#!/bin/bash
# monitor.sh - 闲鱼自动发货主监控脚本
# 使用方法：./monitor.sh

set -e

# === 配置区 ===
FULFILLMENT_SCRIPT="./my-fulfillment.sh"
CHAT_URL="https://www.goofish.com/im"
PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"
LOG_FILE="fulfillment-$(date +%Y%m%d).log"
CHECK_INTERVAL=30  # 检查间隔（秒）

# === 日志函数 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# === 加载发货钩子 ===
load_fulfillment_hook() {
    if [ -f "$FULFILLMENT_SCRIPT" ]; then
        log "📦 加载发货脚本：$FULFILLMENT_SCRIPT"
        source "$FULFILLMENT_SCRIPT"

        # 检查函数是否定义
        if ! declare -f fulfill_order > /dev/null; then
            log "❌ 发货钩子函数 'fulfill_order' 未在脚本中定义"
            exit 1
        fi
    else
        log "❌ 发货脚本不存在：$FULFILLMENT_SCRIPT"
        log "💡 提示：请从 fulfillment-templates/ 复制一个模板并重命名为 my-fulfillment.sh"
        exit 1
    fi
}

# === 检测付款 ===
check_payment() {
    log "🔍 检测付款状态..."

    # 获取聊天快照
    local snapshot=$(agent-browser snapshot 2>&1)

    # 检测付款卡片（必须同时满足以下条件）
    # 1. 包含 "我已付款，等待你发货" 文本
    # 2. 包含 "去发货" 按钮
    if echo "$snapshot" | grep -q "我已付款，等待你发货" && \
       echo "$snapshot" | grep -q "去发货"; then
        log "✅ 检测到付款"
        return 0
    else
        log "⏸️  暂无新付款"
        return 1
    fi
}

# === 提取订单上下文 ===
extract_order_context() {
    # 从聊天快照中提取订单信息
    # 注意：这里需要根据实际的闲鱼页面结构调整选择器

    local snapshot=$(agent-browser snapshot 2>&1)

    # 尝试提取买家昵称（示例实现，需要根据实际页面调整）
    BUYER_NICKNAME=$(echo "$snapshot" | grep -oP '(?<=nickname":")[^"]*' 2>/dev/null || echo "Unknown")

    # 尝试提取商品标题（示例实现，需要根据实际页面调整）
    PRODUCT_TITLE=$(echo "$snapshot" | grep -oP '(?<=title":")[^"]*' 2>/dev/null || echo "Unknown")

    # 导出为环境变量，供发货钩子使用
    export BUYER_NICKNAME
    export PRODUCT_TITLE
    export ORDER_TIME=$(date '+%Y-%m-%d %H:%M:%S')

    log "📋 订单信息：买家=$BUYER_NICKNAME, 商品=$PRODUCT_TITLE"
}

# === 执行发货 ===
execute_fulfillment() {
    log "🚀 执行发货..."

    # 提取订单上下文
    extract_order_context

    # 调用发货钩子
    if fulfill_order; then
        log "✅ 发货成功"
        return 0
    else
        log "❌ 发货失败"
        return 1
    fi
}

# === 主循环 ===
main() {
    log "🚀 启动闲鱼自动发货系统"
    log "📁 配置文件：$FULFILLMENT_SCRIPT"
    log "⏱️  检查间隔：${CHECK_INTERVAL}秒"

    # 加载发货钩子
    load_fulfillment_hook

    # 打开闲鱼聊天页面
    log "🌐 打开闲鱼聊天页面..."
    agent-browser --headed --profile "$PROFILE" open "$CHAT_URL"

    # 等待页面加载
    log "⏳ 等待页面加载..."
    sleep 5

    # 监控循环
    log "🔄 开始监控..."
    while true; do
        if check_payment; then
            execute_fulfillment

            # 发货后等待一段时间再检查下一个
            log "⏳ 等待60秒后继续监控..."
            sleep 60
        else
            sleep $CHECK_INTERVAL
        fi
    done
}

# === 运行 ===
# 捕获 Ctrl+C 信号
trap 'log "👋 监控已停止"; exit 0' INT TERM

main
