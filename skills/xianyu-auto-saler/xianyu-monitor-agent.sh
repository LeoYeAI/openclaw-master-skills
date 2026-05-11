#!/bin/bash
# xianyu-monitor-agent.sh - 闲鱼监控代理
# 使用 OpenClaw 子代理运行，每分钟检查一次闲鱼新消息

set -e

# === 配置区 ===
CHAT_URL="https://www.goofish.com/im"
PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"
FULFILLMENT_TEMPLATE="02-key-pool.sh"  # 使用的发货模板
LOG_FILE="fulfillment-$(date +%Y%m%d).log"
CHECK_INTERVAL=60  # 检查间隔（秒）

# === 日志函数 ===
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

# === 检查 agent-browser 是否可用 ===
check_browser() {
    if ! command -v agent-browser &> /dev/null; then
        log "❌ agent-browser 未安装"
        log "💡 请运行：npm install -g agent-browser && agent-browser install"
        return 1
    fi
    return 0
}

# === 打开闲鱼聊天页面 ===
open_chat() {
    log "🌐 打开闲鱼聊天页面..."
    agent-browser --headed --profile "$PROFILE" open "$CHAT_URL"
    sleep 3
    log "✅ 闲鱼聊天页面已打开"
}

# === 检查是否有新消息 ===
check_new_messages() {
    log "🔍 检查新消息..."

    # 获取聊天快照
    local snapshot=$(agent-browser snapshot 2>&1)

    # 检测未读消息标记（根据闲鱼页面实际情况调整）
    # 这里假设有"未读"标记或红点
    if echo "$snapshot" | grep -qi "未读\|unread\|new.*message"; then
        log "✅ 检测到新消息"
        return 0
    else
        log "⏸️  暂无新消息"
        return 1
    fi
}

# === 查找最新的聊天并进入 ===
enter_latest_chat() {
    log "💬 进入最新聊天..."

    # 获取快照查找最新消息的聊天
    local snapshot=$(agent-browser snapshot 2>&1)

    # 查找第一个有未读标记的聊天（这里需要根据实际页面调整）
    # 示例：查找包含特定类名或文本的聊天项
    if echo "$snapshot" | grep -qi "未读"; then
        # 尝试点击第一个未读聊天
        agent-browser find role listitem click --name "未读" 2>/dev/null || \
        agent-browser find text "未读" click 2>/dev/null || \
        log "⚠️  无法自动点击，请检查页面结构"

        sleep 2
        log "✅ 已进入聊天"
        return 0
    fi

    log "⚠️  未找到未读聊天"
    return 1
}

# === 检测是否需要发货 ===
check_need_fulfillment() {
    log "📋 检查订单状态..."

    # 获取聊天快照
    local snapshot=$(agent-browser snapshot 2>&1)

    # 检测付款卡片
    # 必须同时满足：1) "我已付款，等待你发货"  2) "去发货"按钮
    if echo "$snapshot" | grep -q "我已付款，等待你发货" && \
       echo "$snapshot" | grep -q "去发货"; then
        log "✅ 检测到付款，需要发货"
        return 0
    else
        log "⏸️  不需要发货（可能是普通聊天或已发货）"
        return 1
    fi
}

# === 加载发货模板 ===
load_fulfillment_template() {
    local template_path="fulfillment-templates/$FULFILLMENT_TEMPLATE"

    if [ ! -f "$template_path" ]; then
        log "❌ 发货模板不存在：$template_path"
        return 1
    fi

    log "📦 加载发货模板：$FULFILLMENT_TEMPLATE"
    source "$template_path"

    # 检查函数是否定义
    if ! declare -f fulfill_order > /dev/null; then
        log "❌ 发货模板中未定义 fulfill_order 函数"
        return 1
    fi

    return 0
}

# === 执行发货 ===
execute_fulfillment() {
    log "🚀 执行发货流程..."

    # 加载发货模板
    if ! load_fulfillment_template; then
        log "❌ 加载发货模板失败"
        return 1
    fi

    # 提取订单信息（可选）
    local snapshot=$(agent-browser snapshot 2>&1)
    BUYER_NICKNAME=$(echo "$snapshot" | grep -oP '(?<=nickname":")[^"]*' 2>/dev/null || echo "Unknown")
    PRODUCT_TITLE=$(echo "$snapshot" | grep -oP '(?<=title":")[^"]*' 2>/dev/null || echo "Unknown")

    export BUYER_NICKNAME
    export PRODUCT_TITLE
    export ORDER_TIME=$(date '+%Y-%m-%d %H:%M:%S')

    log "📋 订单信息：买家=$BUYER_NICKNAME, 商品=$PRODUCT_TITLE"

    # 执行发货钩子
    if fulfill_order; then
        log "✅ 发货成功"

        # 返回到聊天列表
        sleep 2
        agent-browser find role button click --name "返回" 2>/dev/null || \
        agent-browser click "聊天" 2>/dev/null || \
        log "⚠️  无法返回聊天列表"

        sleep 2
        return 0
    else
        log "❌ 发货失败"
        return 1
    fi
}

# === 返回聊天列表 ===
back_to_chat_list() {
    log "🔙 返回聊天列表..."

    # 尝试返回按钮
    agent-browser find role button click --name "返回" 2>/dev/null || \
    agent-browser find role link click --name "聊天" 2>/dev/null || \
    agent-browser click "闲鱼" 2>/dev/null

    sleep 2
    log "✅ 已返回聊天列表"
}

# === 主监控循环 ===
main_loop() {
    log "🚀 启动闲鱼监控代理"
    log "📁 配置："
    log "   - 聊天URL：$CHAT_URL"
    log "   - 发货模板：$FULFILLMENT_TEMPLATE"
    log "   - 检查间隔：${CHECK_INTERVAL}秒"

    # 初始化
    check_browser || exit 1

    # 打开闲鱼
    open_chat

    # 监控循环
    local loop_count=0
    while true; do
        loop_count=$((loop_count + 1))

        # 每60次循环输出一次状态（约1小时）
        if [ $((loop_count % 60)) -eq 0 ]; then
            log "🔄 监控运行中... (第 $loop_count 次检查)"
        fi

        # 检查新消息
        if check_new_messages; then
            # 进入聊天
            if enter_latest_chat; then
                # 检查是否需要发货
                if check_need_fulfillment; then
                    # 执行发货
                    execute_fulfillment
                else
                    # 不需要发货，返回列表
                    back_to_chat_list
                fi
            fi
        fi

        # 等待下一次检查
        log "⏳ 等待 ${CHECK_INTERVAL} 秒..."
        sleep $CHECK_INTERVAL
    done
}

# === 信号处理 ===
cleanup() {
    log "👋 监控代理已停止"
    exit 0
}

trap cleanup INT TERM

# === 启动 ===
main_loop
