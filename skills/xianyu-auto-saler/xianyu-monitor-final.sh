#!/bin/bash
# 闲鱼自动监控脚本 - 完整版
# 每分钟检查闲鱼聊天，自动处理新消息

KEY_POOL="/Users/yuehuali/Desktop/xianyu-auto-fulfillment/keys.txt"
USED_KEYS="/Users/yuehuali/Desktop/xianyu-auto-fulfillment/used-keys.txt"
LOG_DIR="/Users/yuehuali/Desktop/xianyu-auto-fulfillment"
TIMESTAMP=$(date +%Y%m%d)

# 记录日志
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_DIR/fulfillment-$TIMESTAMP.log"
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
        sed -i '' "/^$key$/d" "$KEY_POOL" 2>/dev/null
    else
        sed -i "/^$key$/d" "$KEY_POOL" 2>/dev/null
    fi

    # 记录到已使用秘钥
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $key" >> "$USED_KEYS"

    echo "$key"
    return 0
}

# 确保在聊天列表页面
ensure_list_page() {
    local url=$(agent-browser get url 2>&1)
    if [[ "$url" != *"goofish.com/im"* ]]; then
        log "📍 不在聊天列表，跳转..."
        agent-browser open https://www.goofish.com/im > /dev/null 2>&1
        sleep 2
    fi
}

# 检查未读消息
check_unread_messages() {
    local snapshot=$(agent-browser snapshot 2>&1)

    # 查找最近的消息（最近30分钟内的）
    local recent=$(echo "$snapshot" | grep -E "(刚刚|[0-9]+分钟前)" | grep -v "小时前\|天前")

    if [ -z "$recent" ]; then
        return 1
    fi

    # 过滤掉通知消息
    local chat=$(echo "$recent" | grep -v "通知消息\|交易成功")

    if [ -z "$chat" ]; then
        return 1
    fi

    echo "$chat"
    return 0
}

# 进入第一个有新消息的对话
enter_chat() {
    log "📨 尝试进入对话..."

    # 获取可点击的链接
    local interactive=$(agent-browser snapshot -i 2>&1)

    # 查找第一个对话链接（排除导航链接）
    local chat_link=$(echo "$interactive" | grep -E "link.*ref=e" | grep -v "订单\|发闲置\|反馈\|客服" | head -1)

    if [ -z "$chat_link" ]; then
        log "⚠ 未找到对话链接"
        return 1
    fi

    # 提取引用
    local ref=$(echo "$chat_link" | grep -o '\[ref=e[0-9]*\]' | grep -o 'e[0-9]*')

    if [ -z "$ref" ]; then
        log "⚠ 无法提取链接引用"
        return 1
    fi

    log "📍 点击对话 @$ref"
    agent-browser click "@$ref" > /dev/null 2>&1

    sleep 2

    # 等待对话页面加载
    agent-browser wait --load networkidle > /dev/null 2>&1

    return 0
}

# 分析对话内容
analyze_chat() {
    local snapshot=$(agent-browser snapshot 2>&1)

    # 检查是否为付款消息
    if echo "$snapshot" | grep -q "我已付款\|等待你发货\|去发货"; then
        log "💰 检测到付款消息！"
        return 0
    fi

    return 1
}

# 发送秘钥
send_key() {
    log "📦 开始处理发货请求..."

    local key=$(get_key_from_pool)
    if [ $? -ne 0 ]; then
        log "❌ 获取秘钥失败"
        return 1
    fi

    log "✅ 获取到秘钥：$key"

    # 查找输入框
    sleep 1
    agent-browser snapshot -i 2>&1 > /tmp/snapshot_input.txt

    # 尝试发送消息
    local msg="您的秘钥：$key，祝您使用愉快！"
    log "💬 发送消息：$msg"

    agent-browser type "$msg" > /dev/null 2>&1

    sleep 1

    # 查找并发送按钮
    agent-browser snapshot -i 2>&1 > /tmp/snapshot_send.txt
    local send_btn=$(grep -i "发送\|send" /tmp/snapshot_send.txt | head -1)

    if [ -n "$send_btn" ]; then
        local ref=$(echo "$send_btn" | grep -o '\[ref=e[0-9]*\]' | grep -o 'e[0-9]*')
        if [ -n "$ref" ]; then
            agent-browser click "@$ref" > /dev/null 2>&1
            sleep 1
        fi
    fi

    log "✅ 秘钥已发送"
    return 0
}

# 发送普通回复
send_reply() {
    log "💬 发送普通回复..."

    local msg="您好！我现在在线，有什么可以帮您的吗？"
    log "💬 发送消息：$msg"

    agent-browser type "$msg" > /dev/null 2>&1

    sleep 1

    # 查找并发送按钮
    agent-browser snapshot -i 2>&1 > /tmp/snapshot_send.txt
    local send_btn=$(grep -i "发送\|send" /tmp/snapshot_send.txt | head -1)

    if [ -n "$send_btn" ]; then
        local ref=$(echo "$send_btn" | grep -o '\[ref=e[0-9]*\]' | grep -o 'e[0-9]*')
        if [ -n "$ref" ]; then
            agent-browser click "@$ref" > /dev/null 2>&1
            sleep 1
        fi
    fi

    log "✅ 回复已发送"
    return 0
}

# 主监控循环
main_loop() {
    mkdir -p "$LOG_DIR"
    log "🚀 闲鱼自动监控启动"
    log "📍 监控周期：60秒"
    log "📋 任务：自动处理闲鱼聊天消息"

    local check_count=0

    while true; do
        ((check_count++))
        log "🔍 ========== 第 $check_count 次检查 =========="

        # 确保在聊天列表
        ensure_list_page

        # 检查是否有未读消息
        local unread=$(check_unread_messages)

        if [ -n "$unread" ]; then
            log "📨 发现新消息："
            echo "$unread" | head -3 | while read line; do
                log "  $line"
            done

            # 进入对话
            if enter_chat; then
                # 分析消息类型
                sleep 1

                if analyze_chat; then
                    # 付款消息 - 发送秘钥
                    send_key
                else
                    # 普通消息 - 发送回复
                    send_reply
                fi

                # 返回列表
                sleep 1
                ensure_list_page
            fi
        else
            log "✓ 没有新消息"
        fi

        # 等待60秒
        log "⏳ 等待60秒后继续..."
        log "=========================================="
        sleep 60
    done
}

# 启动主循环
main_loop