#!/bin/bash
# get-objects.sh - 获取 CloudCC 对象列表（标准对象 + 自定义对象）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.json"

# 读取配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在：$CONFIG_FILE"
    exit 1
fi

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

# 解析参数
SHOW_STANDARD=false
SHOW_CUSTOM=false
SEARCH_KEYWORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--standard)
            SHOW_STANDARD=true
            shift
            ;;
        -c|--custom)
            SHOW_CUSTOM=true
            shift
            ;;
        -k|--keyword)
            SEARCH_KEYWORD="$2"
            shift 2
            ;;
        -h|--help)
            echo "用法：$0 [选项]"
            echo ""
            echo "选项:"
            echo "  -s, --standard     只显示标准对象"
            echo "  -c, --custom       只显示自定义对象"
            echo "  -k, --keyword KEY  搜索包含关键词的对象"
            echo "  -h, --help         显示帮助"
            echo ""
            echo "默认显示标准对象和自定义对象"
            exit 0
            ;;
        *)
            echo "❌ 未知选项：$1"
            exit 1
            ;;
    esac
done

# 默认显示两者
if [ "$SHOW_STANDARD" = false ] && [ "$SHOW_CUSTOM" = false ]; then
    SHOW_STANDARD=true
    SHOW_CUSTOM=true
fi

echo "📋 CloudCC 对象列表"
echo "=================="
echo ""

# 获取标准对象
if [ "$SHOW_STANDARD" = true ]; then
    echo "📦 标准对象:"
    echo "----------"
    
    STANDARD_RESPONSE=$(curl -s -X POST "$API_DOMAIN/api/customObject/standardObjList" \
      -H "accessToken: $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{}')
    
    RESULT=$(echo "$STANDARD_RESPONSE" | jq -r '.result')
    if [ "$RESULT" != "true" ]; then
        echo "❌ 获取标准对象失败：$(echo "$STANDARD_RESPONSE" | jq -r '.returnInfo')"
    else
        COUNT=$(echo "$STANDARD_RESPONSE" | jq '.data | length')
        echo "共 $COUNT 个标准对象"
        echo ""
        
        if [ -n "$SEARCH_KEYWORD" ]; then
            echo "$STANDARD_RESPONSE" | jq -r --arg kw "$SEARCH_KEYWORD" \
              '.data[] | select(.objname | ascii_downcase | contains($kw | ascii_downcase)) | "  \(.objname) -> \(.label) (prefix: \(.objprefix))"'
        else
            echo "$STANDARD_RESPONSE" | jq -r '.data[] | "  \(.objname) -> \(.label) (prefix: \(.objprefix))"'
        fi
    fi
    echo ""
fi

# 获取自定义对象
if [ "$SHOW_CUSTOM" = true ]; then
    echo "🔧 自定义对象:"
    echo "------------"
    
    CUSTOM_RESPONSE=$(curl -s -X POST "$API_DOMAIN/api/customObject/list" \
      -H "accessToken: $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"id":""}')
    
    RESULT=$(echo "$CUSTOM_RESPONSE" | jq -r '.result')
    if [ "$RESULT" != "true" ]; then
        echo "❌ 获取自定义对象失败：$(echo "$CUSTOM_RESPONSE" | jq -r '.returnInfo')"
    else
        COUNT=$(echo "$CUSTOM_RESPONSE" | jq '.data.objList | length')
        echo "共 $COUNT 个自定义对象"
        echo ""
        
        if [ -n "$SEARCH_KEYWORD" ]; then
            echo "$CUSTOM_RESPONSE" | jq -r --arg kw "$SEARCH_KEYWORD" \
              '.data.objList[] | select(.objLabel | ascii_downcase | contains($kw | ascii_downcase)) | "  \(.objLabel) -> \(.schemetable_name) (prefix: \(.prefix))"'
        else
            echo "$CUSTOM_RESPONSE" | jq -r '.data.objList[] | "  \(.objLabel) -> \(.schemetable_name) (prefix: \(.prefix))"'
        fi
    fi
    echo ""
fi
