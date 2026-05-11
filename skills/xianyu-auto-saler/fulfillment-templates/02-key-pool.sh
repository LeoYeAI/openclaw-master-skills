#!/bin/bash
# 模板 2：秘钥发货（秘钥池）
# 适用场景：每个订单使用不同秘钥、批量售卖虚拟商品

# === 配置区 ===
KEY_POOL_FILE="./keys.txt"
USED_KEYS_FILE="./used-keys.txt"

# === 函数区 ===

# 初始化秘钥池
init_key_pool() {
    if [ ! -f "$KEY_POOL_FILE" ]; then
        echo "# 秘钥池文件 - 每行一个秘钥" > "$KEY_POOL_FILE"
        echo "# 示例：" >> "$KEY_POOL_FILE"
        echo "KEY-ABC123" >> "$KEY_POOL_FILE"
        echo "KEY-DEF456" >> "$KEY_POOL_FILE"
        echo "KEY-GHI789" >> "$KEY_POOL_FILE"
        echo "" >> "$KEY_POOL_FILE"
        echo "# 请替换为你的真实秘钥" >> "$KEY_POOL_FILE"
    fi
}

# 从秘钥池获取一个秘钥
get_key_from_pool() {
    if [ ! -f "$KEY_POOL_FILE" ]; then
        echo "❌ 秘钥池文件不存在：$KEY_POOL_FILE"
        return 1
    fi

    # 读取第一个非注释行
    key=$(grep -v "^#" "$KEY_POOL_FILE" | grep -v "^$" | head -1)

    if [ -z "$key" ]; then
        echo "❌ 秘钥池已空！"
        return 1
    fi

    # 从秘钥池中移除已使用的
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "/^$key$/d" "$KEY_POOL_FILE" 2>/dev/null
    else
        # Linux
        sed -i "/^$key$/d" "$KEY_POOL_FILE" 2>/dev/null
    fi

    # 记录到已使用秘钥
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $key" >> "$USED_KEYS_FILE"

    echo "$key"
}

# === 发货钩子 ===
fulfill_order() {
    echo "📦 从秘钥池获取秘钥..."

    # 初始化秘钥池
    init_key_pool

    # 获取秘钥
    key=$(get_key_from_pool)
    if [ $? -ne 0 ]; then
        echo "❌ 获取秘钥失败"
        return 1
    fi

    echo "✅ 获取到秘钥：$key"

    # 发送秘钥
    agent-browser type "您的秘钥：$key，祝您使用愉快！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
