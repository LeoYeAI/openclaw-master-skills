#!/bin/bash
# 模板 5：API发货（调用外部服务）
# 适用场景：调用自动生成秘钥的API、集成第三方发货服务、调用自己的服务器

# === 配置区 ===
API_ENDPOINT="https://your-api.com/generate-key"
API_KEY="YOUR_API_KEY"

# === 函数区 ===

# 调用API生成秘钥
call_api_generate_key() {
    local buyer_nickname="$1"
    local product_title="$2"
    local order_time="$3"

    echo "📡 调用API生成秘钥..."

    # 构建请求体
    local request_body=$(cat <<EOF
{
    "buyer": "$buyer_nickname",
    "product": "$product_title",
    "timestamp": "$order_time"
}
EOF
)

    # 发送请求
    local response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$request_body")

    # 解析响应
    if command -v jq &> /dev/null; then
        # 使用 jq 解析
        local key=$(echo "$response" | jq -r '.key' 2>/dev/null)
        local success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    else
        # 使用 grep 解析（fallback）
        local key=$(echo "$response" | grep -o '"key":"[^"]*"' | cut -d'"' -f4)
        local success=$(echo "$response" | grep -o '"success":[^,}]*' | cut -d':' -f2)
    fi

    if [ "$success" = "true" ] && [ -n "$key" ] && [ "$key" != "null" ]; then
        echo "$key"
        return 0
    else
        echo "❌ API调用失败：$response"
        return 1
    fi
}

# === 发货钩子 ===
fulfill_order() {
    echo "📦 通过API发货..."

    # 获取订单上下文（如果已设置环境变量）
    local buyer="${BUYER_NICKNAME:-Unknown}"
    local product="${PRODUCT_TITLE:-Unknown}"
    local order_time="${ORDER_TIME:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

    # 调用API
    key=$(call_api_generate_key "$buyer" "$product" "$order_time")
    if [ $? -ne 0 ]; then
        echo "❌ 生成秘钥失败"
        return 1
    fi

    echo "✅ 生成秘钥：$key"

    # 发送秘钥
    agent-browser type "您的秘钥：$key，祝您使用愉快！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
