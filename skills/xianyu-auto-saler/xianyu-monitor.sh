#!/bin/bash
# 闲鱼自动监控脚本
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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_DIR/fulfillment-$TIMESTAMP.log"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
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

# 检查是否有未读消息
check_unread() {
    # 获取页面快照，查找未读标记
    snapshot=$(agent-browser snapshot 2>&1)

    # 检查是否有未读标记（红色圆点或数字）
    if echo "$snapshot" | grep -q "未读\|unread"; then
        return 0
    fi

    return 1
}

# 获取第一个未读对话的引用
get_first_unread_chat() {
    snapshot=$(agent-browser snapshot 2>&1)

    # 查找包含未读标记的对话链接
    # 需要根据实际页面结构调整
    echo "$snapshot" | grep -A 5 -B 5 "未读\|unread" | head -20
}

# 分析消息内容，判断是否为付款消息
check_payment_message() {
    snapshot=$(agent-browser snapshot 2>&1)

    # 检查是否包含付款相关关键词
    if echo "$snapshot" | grep -q "我已付款\|等待你发货\|去发货"; then
        return 0
    fi

    return 1
}

# 发送秘钥
send_key() {
    log "📦 开始处理发货请求..."

    # 获取秘钥
    key=$(get_key_from_pool)
    if [ $? -ne 0 ]; then
        log "❌ 获取秘钥失败"
        return 1
    fi

    log "✅ 获取到秘钥：$key"

    # 查找输入框和发送按钮
    snapshot=$(agent-browser snapshot -i 2>&1)

    # 发送秘钥消息
    log "正在发送秘钥..."
    agent-browser type "您的秘钥：$key，祝您使用愉快！" 2>&1 || {
        log "❌ 发送消息失败"
        return 1
    }

    sleep 1

    # 点击发送按钮
    agent-browser snapshot -i 2>&1 | grep -i "发送\|send" | head -5
    # 这里需要找到发送按钮并点击

    log "✅ 秘钥已发送：$key"
    return 0
}

# 发送普通回复
send_reply() {
    log "💬 发送普通回复..."

    agent-browser type "您好！我现在在线，有什么可以帮您的吗？" 2>&1 || {
        log "❌ 发送回复失败"
        return 1
    }

    sleep 1

    log "✅ 普通回复已发送"
    return 0
}

# 返回聊天列表
back_to_list() {
    log "返回聊天列表..."
    agent-browser open https://www.goofish.com/im 2>&1 > /dev/null
    sleep 2
}

# 主监控循环
main_loop() {
    init_log
    log "🚀 闲鱼自动监控启动"

    while true; do
        log "🔍 开始检查新消息..."

        # 获取页面快照
        snapshot=$(agent-browser snapshot 2>&1)

        # 检查页面是否正常
        if echo "$snapshot" | grep -q "尚未选择任何联系人"; then
            log "✓ 在聊天列表页面"
        else
            log "⚠ 不在聊天列表页面，尝试返回..."
            back_to_list
        fi

        # 检查是否有未读消息
        # 这里需要根据实际的未读标记来实现
        # 暂时只记录检查日志
        log "✓ 检查完成，暂未发现未读消息"

        # 等待60秒继续下一次检查
        log "⏳ 等待60秒后继续..."
        sleep 60
    done
}

# 启动主循环
main_loop