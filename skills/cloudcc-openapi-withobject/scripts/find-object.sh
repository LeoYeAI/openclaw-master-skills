#!/bin/bash
# find-object.sh - 通过选项卡名称查找 CloudCC 对象

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
SEARCH_KEYWORD=""
OUTPUT_JSON=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--keyword)
            SEARCH_KEYWORD="$2"
            shift 2
            ;;
        -j|--json)
            OUTPUT_JSON=true
            shift
            ;;
        -h|--help)
            echo "用法：$0 -k <关键词> [选项]"
            echo ""
            echo "选项:"
            echo "  -k, --keyword KEY  搜索关键词（必填）"
            echo "  -j, --json         输出 JSON 格式"
            echo "  -h, --help         显示帮助"
            echo ""
            echo "示例:"
            echo "  $0 -k 产品需求           # 搜索包含'产品需求'的选项卡"
            echo "  $0 -k 客户 -j            # 搜索'客户'并输出 JSON"
            exit 0
            ;;
        *)
            echo "❌ 未知选项：$1"
            exit 1
            ;;
    esac
done

# 验证参数
if [ -z "$SEARCH_KEYWORD" ]; then
    echo "❌ 必须指定搜索关键词 (-k)"
    echo "使用 -h 查看帮助"
    exit 1
fi

echo "🔍 搜索选项卡：'$SEARCH_KEYWORD'"
echo "================================"
echo ""

# 获取所有选项卡
TABS_RESPONSE=$(curl -s -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"getAllTabs"}')

RESULT=$(echo "$TABS_RESPONSE" | jq -r '.result')
if [ "$RESULT" != "true" ]; then
    echo "❌ 获取选项卡失败：$(echo "$TABS_RESPONSE" | jq -r '.returnInfo')"
    exit 1
fi

# 过滤并显示结果
if [ "$OUTPUT_JSON" = true ]; then
    echo "$TABS_RESPONSE" | jq --arg kw "$SEARCH_KEYWORD" \
      '.data[] | select(.tab_name | ascii_downcase | contains($kw | ascii_downcase))'
else
    COUNT=$(echo "$TABS_RESPONSE" | jq --arg kw "$SEARCH_KEYWORD" \
      '[.data[] | select(.tab_name | ascii_downcase | contains($kw | ascii_downcase))] | length')
    
    echo "找到 $COUNT 个匹配项"
    echo ""
    
    if [ "$COUNT" -gt 0 ]; then
        printf "%-40s %-25s %-10s %-20s\n" "选项卡名称" "对象 API" "前缀" "对象 ID"
        printf "%-40s %-25s %-10s %-20s\n" "--------" "--------" "----" "--------"
        
        echo "$TABS_RESPONSE" | jq -r --arg kw "$SEARCH_KEYWORD" \
          '.data[] | select(.tab_name | ascii_downcase | contains($kw | ascii_downcase)) | 
           "\(.tab_name | .[0:38])\t\(.objectApi // "N/A")\t\(.prefix // "N/A")\t\(.objId // "N/A")"' | \
          while IFS=$'\t' read -r name api prefix objid; do
            printf "%-40s %-25s %-10s %-20s\n" "$name" "$api" "$prefix" "$objid"
          done
    fi
fi

echo ""
echo "💡 提示:"
echo "  使用 -o 参数查询对象字段：./get-fields.sh -o <对象 API>"
echo "  使用 -p 参数查询对象字段：./get-fields.sh -p <前缀>"
