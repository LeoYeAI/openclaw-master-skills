#!/bin/bash
# 闲鱼自动监控脚本 V2
# 每分钟检查闲鱼聊天，自动处理新消息

KEY_POOL="/Users/yuehuali/Desktop/xianyu-auto-fulfillment/keys.txt"
USED_KEYS="/Users/yuehuali/Desktop/xianyu-auto-fulfillment/used-keys.txt"
LOG_DIR="/Users/yuehuali/Desktop/xianyu-auto-fulfillment"
TIMESTAMP=$(date +%Y%m%d)

# 初始化日志
init_log() {
    mkdir -p "$LOG_DIR"
    echo "=== 闲鱼自动监控日志 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_DIR/fulfillment-$TIMESTAMP.log"
}

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/fulfillment-$TIMESTAMP.log"
}

# 从秘钥池获取秘钥
get_key_from_pool() {
    if [ ! -f "$KEY_POOL" ]; then
        log "❌ 秘钥池文件不存在：$KEY_POOL"
        return 1
    fi

    # 读取第一个非注释行
    key=$(grep -v "^#" "$KEY_POOL" | grep -v "^$" | head -1)

    if [ -z "$key" ]; then
        log "❌ 秘钥池已空！"
        return 1
    fi

    # 从秘钥池中移除已使用的
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "/^$key$/d" "$KEY_POOL" 2>/dev/null
    else
        # Linux
        sed -i "/^$key$/d" "$KEY_POOL" 2>/dev/null
    fi

    # 记录到已使用秘钥
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $key" >> "$USED_KEYS"

    echo "$key"
    return 0
}

# 获取第一个有新消息的对话
get_first_new_chat() {
    # 获取完整页面快照
    snapshot=$(agent-browser snapshot 2>&1)

    # 查找所有对话项
    # 闲鱼的新消息可能通过时间戳、未读标记、或者特定类名识别
    # 这里使用简单的启发式方法：查找最近的对话（有消息时间的）

    echo "$snapshot" | grep -E "(text.*分钟前|text.*小时前|刚刚|img.*reminder)" | head -10
}

# 检查并处理新消息
check_and_process_messages() {
    # 获取页面快照
    snapshot=$(agent-browser snapshot 2>&1)

    # 检查是否在聊天列表页面
    if echo "$snapshot" | grep -q "尚未选择任何联系人"; then
        log "✓ 在聊天列表页面"
    else
        log "⚠ 不在聊天列表页面，返回列表..."
        agent-browser open https://www.goofish.com/im > /dev/null 2>&1
        sleep 2
        return
    fi

    # 获取对话列表
    log "🔍 检查对话列表..."
    chat_list=$(agent-browser snapshot 2>&1)

    # 查找可能的新消息对话
    # 查找包含"几分钟前"、"几小时前"、"刚刚"等时间标记的对话
    recent_chats=$(echo "$chat_list" | grep -E "(刚刚|分钟前|小时前)" | head -5)

    if [ -z "$recent_chats" ]; then
        log "✓ 没有新消息（最近1小时内）"
        return
    fi

    log "📨 发现可能有新消息的对话："
    log "$recent_chats"

    # 尝试进入第一个最近的对话
    # 这里需要根据实际页面结构调整
    # 暂时只记录日志，不自动进入（因为页面结构可能复杂）

    log "⚠ 检测到新消息，需要人工确认页面结构以实现自动处理"
}

# 主监控循环
main_loop() {
    init_log
    log "🚀 闲鱼自动监控 V2 启动"
    log "📍 目标：每60秒检查一次闲鱼聊天页面"
    log "📋 工作流：检测新消息 → 进入对话 → 分析内容 → 自动回复/发货"

    while true; do
        log "🔍 ========== 开始新一轮检查 =========="

        # 确保在聊天列表页面
        current_url=$(agent-browser get url 2>&1)
        if [ "$current_url" != "https://www.goofish.com/im" ]; then
            log "📍 当前不在聊天列表，跳转..."
            agent-browser open https://www.goofish.com/im > /dev/null 2>&1
            sleep 2
        fi

        # 检查并处理消息
        check_and_process_messages

        # 等待60秒继续下一次检查
        log "⏳ 等待60秒后继续..."
        log "=========================================="
        sleep 60
    done
}

# 启动主循环
main_loop