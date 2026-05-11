#!/bin/bash
# 模板 1：秘钥发货（固定秘钥）
# 适用场景：测试商品、免费资源分享、公开教程

# === 配置区 ===
SECRET_KEY="YOUR_SECRET_KEY_HERE"

# === 发货钩子 ===
fulfill_order() {
    echo "📦 发送固定秘钥..."

    # 发送秘钥到聊天
    agent-browser type "您的秘钥：$SECRET_KEY，祝您使用愉快！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

# 导出钩子（由框架调用）
export -f fulfill_order
