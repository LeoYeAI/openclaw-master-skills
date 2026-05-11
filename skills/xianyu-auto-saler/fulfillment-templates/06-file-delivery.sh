#!/bin/bash
# 模板 6：文件发货（发送本地文件）
# 适用场景：发送PDF/电子书、发送压缩包（资源包）、发送软件安装包

# === 配置区 ===
PRODUCT_FILE="$HOME/Downloads/product.pdf"
FILE_CAPTION="文件已准备好，请查收"

# === 发货钩子 ===
fulfill_order() {
    echo "📦 发送文件..."

    # 检查文件是否存在
    if [ ! -f "$PRODUCT_FILE" ]; then
        echo "❌ 文件不存在：$PRODUCT_FILE"
        return 1
    fi

    # 先发送文字说明
    agent-browser type "$FILE_CAPTION"
    sleep 1
    agent-browser click "发 送"

    # 等待一下再发送文件
    sleep 2

    # 上传文件（需要根据闲鱼界面调整）
    echo "⚠️  注意：文件上传功能需要根据实际闲鱼界面调整"
    echo "📝 当前实现需要手动补充以下步骤："
    echo "   1. 找到文件上传按钮"
    echo "   2. 选择文件：$PRODUCT_FILE"
    echo "   3. 等待上传完成"
    echo "   4. 点击发送"

    # 示例代码（需要根据实际情况调整）
    # agent-browser snapshot
    # agent-browser find role button click --name "文件" || \
    # agent-browser click "＋" || \
    # agent-browser find aria-label "文件" click
    # sleep 1
    # # 使用自动化工具上传文件（如 yd 或 osascript）
    # ...

    return 0
}

export -f fulfill_order
