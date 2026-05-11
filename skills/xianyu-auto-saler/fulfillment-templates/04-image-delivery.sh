#!/bin/bash
# 模板 4：图片发货（二维码/截图）
# 适用场景：发送二维码、教程截图、凭证图片

# === 配置区 ===
QR_CODE_IMAGE="$HOME/Desktop/qr-code.png"
IMAGE_CAPTION="请扫描下方二维码添加好友/领取商品"

# === 发货钩子 ===
fulfill_order() {
    echo "📦 发送二维码图片..."

    # 先发送文字说明
    agent-browser type "$IMAGE_CAPTION"
    sleep 1
    agent-browser click "发 送"

    # 等待一下再发送图片
    sleep 2

    # 检查图片是否存在
    if [ ! -f "$QR_CODE_IMAGE" ]; then
        echo "❌ 图片文件不存在：$QR_CODE_IMAGE"
        return 1
    fi

    # 上传并发送图片（需要根据闲鱼界面调整）
    echo "⚠️  注意：图片上传功能需要根据实际闲鱼界面调整"
    echo "📝 当前实现需要手动补充以下步骤："
    echo "   1. 找到图片上传按钮"
    echo "   2. 选择文件"
    echo "   3. 等待上传完成"
    echo "   4. 点击发送"

    # 示例代码（需要根据实际情况调整）
    # agent-browser snapshot
    # agent-browser find role button click --name "图片" || \
    # agent-browser click "＋" || \
    # agent-browser find aria-label "图片" click
    # sleep 1
    # # 使用自动化工具上传文件（如 yd 或 osascript）
    # ...

    return 0
}

export -f fulfill_order
