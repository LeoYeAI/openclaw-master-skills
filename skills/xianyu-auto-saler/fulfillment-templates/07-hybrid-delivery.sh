#!/bin/bash
# 模板 7：混合发货（组合多种方式）
# 适用场景：同时发送秘钥和链接、发送多个步骤的指引、复杂的发货流程

# === 配置区 ===
SECRET_KEY="YOUR_KEY_HERE"
DOWNLOAD_LINK="https://example.com/download"
TUTORIAL_LINK="https://example.com/tutorial"
EXTRA_INFO="如有问题随时联系我！"

# === 函数区 ===

# 发送单条消息
send_message() {
    local msg="$1"
    agent-browser type "$msg"
    sleep 1
    agent-browser click "发 送"
    sleep 1
}

# === 发货钩子 ===
fulfill_order() {
    echo "📦 混合发货..."

    # 发送第1条消息：秘钥
    send_message "🔑 秘钥：$SECRET_KEY"

    # 发送第2条消息：下载链接
    send_message "📥 下载链接：$DOWNLOAD_LINK"

    # 发送第3条消息：教程链接和联系方式
    local final_msg="📖 使用教程：$TUTORIAL_LINK\n\n$EXTRA_INFO"
    send_message "$final_msg"

    return 0
}

export -f fulfill_order
