#!/bin/bash
# get-token.sh - 获取 CloudCC API accessToken（带日志记录）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.json"
LOGGER_SCRIPT="$SCRIPT_DIR/logger.sh"

# 读取配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在：$CONFIG_FILE"
    echo "请复制 config.example.json 为 config.json 并填写配置"
    exit 1
fi

ORG_ID=$(cat "$CONFIG_FILE" | jq -r '.orgId')
USERNAME=$(cat "$CONFIG_FILE" | jq -r '.username')
SAFETY_MARK=$(cat "$CONFIG_FILE" | jq -r '.safetyMark')
CLIENT_ID=$(cat "$CONFIG_FILE" | jq -r '.clientId')
SECRET_KEY=$(cat "$CONFIG_FILE" | jq -r '.secretKey')

# 检查配置
if [ "$ORG_ID" == "null" ] || [ "$ORG_ID" == "your-org-id-here" ]; then
    echo "❌ 请配置 orgId"
    exit 1
fi

echo "📡 正在获取 API 网关地址..."

# 记录请求开始时间（毫秒）
START_TIME=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

# 1. 获取 API 网关地址
API_DOMAIN_RESPONSE=$(curl -s "https://developer.apis.cloudcc.cn/oauth/apidomain?scope=cloudccCRM&orgId=$ORG_ID")
API_DOMAIN=$(echo "$API_DOMAIN_RESPONSE" | jq -r '.orgapi_address')

if [ "$API_DOMAIN" == "null" ] || [ -z "$API_DOMAIN" ]; then
    echo "❌ 获取 API 网关地址失败"
    echo "响应：$API_DOMAIN_RESPONSE"
    
    # 记录错误日志
    if [ -x "$LOGGER_SCRIPT" ]; then
        bash "$LOGGER_SCRIPT" log_auth_event "GATEWAY_REQUEST" "FAILED" "获取网关地址失败" 2>/dev/null
    fi
    
    exit 1
fi

echo "✅ API 网关：$API_DOMAIN"

# 更新配置
jq --arg domain "$API_DOMAIN" '.apiDomain = $domain' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

echo "🔐 正在获取 accessToken..."

# 2. 获取 accessToken
TOKEN_RESPONSE=$(curl -s -X POST "$API_DOMAIN/api/cauth/token" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\":\"$USERNAME\",
    \"safetyMark\":\"$SAFETY_MARK\",
    \"clientId\":\"$CLIENT_ID\",
    \"secretKey\":\"$SECRET_KEY\",
    \"orgId\":\"$ORG_ID\",
    \"grant_type\":\"password\"
  }")

RESULT=$(echo "$TOKEN_RESPONSE" | jq -r '.result')
RETURN_CODE=$(echo "$TOKEN_RESPONSE" | jq -r '.returnCode')

# 计算耗时
END_TIME=$(date +%s%3N)
DURATION_MS=$((END_TIME - START_TIME))

if [ "$RESULT" != "true" ] || [ "$RETURN_CODE" != "1" ]; then
    echo "❌ 获取 accessToken 失败"
    echo "响应：$TOKEN_RESPONSE"
    
    # 记录错误日志
    if [ -x "$LOGGER_SCRIPT" ]; then
        bash "$LOGGER_SCRIPT" log_auth_event "TOKEN_REQUEST" "FAILED" "获取 token 失败：$RETURN_CODE" 2>/dev/null
    fi
    
    exit 1
fi

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.data.accessToken')

if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ accessToken 为空"
    
    # 记录错误日志
    if [ -x "$LOGGER_SCRIPT" ]; then
        bash "$LOGGER_SCRIPT" log_auth_event "TOKEN_REQUEST" "FAILED" "accessToken 为空" 2>/dev/null
    fi
    
    exit 1
fi

# 计算过期时间（2 小时后）
EXPIRES_AT=$(($(date +%s) + 7200))

# 更新配置
jq --arg token "$ACCESS_TOKEN" \
   --argjson expires "$EXPIRES_AT" \
   '.accessToken = $token | .tokenExpiresAt = $expires' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

echo "✅ accessToken 获取成功 (耗时：${DURATION_MS}ms)"
echo "📝 Token: ${ACCESS_TOKEN:0:20}..."
echo "⏰ 过期时间：$(date -d "@$EXPIRES_AT" '+%Y-%m-%d %H:%M:%S')"

# 记录成功日志
if [ -x "$LOGGER_SCRIPT" ]; then
    bash "$LOGGER_SCRIPT" log_auth_event "TOKEN_REQUEST" "SUCCESS" "获取 token 成功，有效期 2 小时" 2>/dev/null
fi

echo ""
echo "💡 使用方法:"
echo "   curl -X POST \"$API_DOMAIN/openApi/common\" \\"
echo "     -H \"accessToken: $ACCESS_TOKEN\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"serviceName\":\"cquery\",...}'"
