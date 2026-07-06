#!/bin/bash
# call-api.sh - 调用 CloudCC OpenAPI（带日志记录）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.json"
LOGGER_SCRIPT="$SCRIPT_DIR/logger.sh"

# 检查配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在"
    exit 1
fi

# 读取配置
API_DOMAIN=$(cat "$CONFIG_FILE" | jq -r '.apiDomain')
ACCESS_TOKEN=$(cat "$CONFIG_FILE" | jq -r '.accessToken')
TOKEN_EXPIRES=$(cat "$CONFIG_FILE" | jq -r '.tokenExpiresAt')

# 检查是否需要刷新 token
CURRENT_TIME=$(date +%s)
if [ "$ACCESS_TOKEN" == "null" ] || [ "$TOKEN_EXPIRES" == "null" ] || [ "$CURRENT_TIME" -ge "$TOKEN_EXPIRES" ]; then
    echo "⚠️  token 已过期或不存在，正在刷新..."
    "$SCRIPT_DIR/get-token.sh"
    if [ $? -ne 0 ]; then
        echo "❌ 刷新 token 失败"
        exit 1
    fi
    API_DOMAIN=$(cat "$CONFIG_FILE" | jq -r '.apiDomain')
    ACCESS_TOKEN=$(cat "$CONFIG_FILE" | jq -r '.accessToken')
fi

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法：$0 <service-name> [json-params]"
    exit 1
fi

SERVICE_NAME=$1
JSON_PARAMS=${2:-"{}"}

# 记录请求开始时间（秒）
START_TIME=$(date +%s)

# 提取 objectApiName
OBJECT_API=$(echo "$JSON_PARAMS" | jq -r '.objectApiName // "N/A"' 2>/dev/null)

echo "📡 调用 API: $SERVICE_NAME"
echo "🔗 地址：$API_DOMAIN/openApi/common"

# 构建请求体
REQUEST_BODY=$(echo "$JSON_PARAMS" | jq --arg svc "$SERVICE_NAME" '.serviceName = $svc')

# 调用 API
RESPONSE=$(curl -s -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")

# 计算耗时（秒）
END_TIME=$(date +%s)
DURATION_MS=$(( (END_TIME - START_TIME) * 1000 ))

# 解析响应
RETURN_CODE=$(echo "$RESPONSE" | jq -r '.returnCode // "unknown"')
RESULT=$(echo "$RESPONSE" | jq -r '.result // false')

# 输出结果
echo ""
if [ "$RETURN_CODE" == "1" ] && [ "$RESULT" == "true" ]; then
    echo "✅ 调用成功 (耗时：${DURATION_MS}ms)"
else
    echo "❌ 调用失败 (returnCode: $RETURN_CODE, 耗时：${DURATION_MS}ms)"
fi

# 记录日志
if [ -x "$LOGGER_SCRIPT" ]; then
    bash "$LOGGER_SCRIPT" log_api_request "$SERVICE_NAME" "$OBJECT_API" "$RETURN_CODE" "$DURATION_MS" 2>/dev/null
fi

echo ""
echo "$RESPONSE" | jq .

exit 0
