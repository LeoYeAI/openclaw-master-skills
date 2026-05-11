#!/bin/bash
# 模板 3：链接发货（网盘/下载链接）
# 适用场景：数字资源下载、大文件分享、云盘分享

# === 配置区 ===
DOWNLOAD_LINK="https://pan.baidu.com/s/XXXXXXXXXXXX"
EXTRACTION_CODE="abcd"
INSTRUCTIONS="如有问题，随时联系我！"

# === 发货钩子 ===
fulfill_order() {
    echo "📦 发送下载链接..."

    # 构建消息
    local message="您的下载链接已准备好！\n\n"
    message+="📁 网盘链接：$DOWNLOAD_LINK\n"
    message+="🔑 提取码：$EXTRACTION_CODE\n\n"
    message+="$INSTRUCTIONS"

    # 发送消息
    agent-browser type "$message"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
