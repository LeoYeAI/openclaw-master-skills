#!/bin/bash
# get-fields.sh - 获取 CloudCC 对象字段列表

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
OBJECT_PREFIX=""
OBJECT_API=""
SHOW_STANDARD=false
SHOW_CUSTOM=false
SHOW_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--prefix)
            OBJECT_PREFIX="$2"
            shift 2
            ;;
        -o|--object)
            OBJECT_API="$2"
            shift 2
            ;;
        -s|--standard)
            SHOW_STANDARD=true
            shift
            ;;
        -c|--custom)
            SHOW_CUSTOM=true
            shift
            ;;
        -a|--all)
            SHOW_ALL=true
            shift
            ;;
        -h|--help)
            echo "用法：$0 <-p 前缀 | -o 对象 API> [选项]"
            echo ""
            echo "选项:"
            echo "  -p, --prefix PFIX  对象前缀（如 b70, 001, 003）"
            echo "  -o, --object API   对象 API 名称（如 productuplist, Account）"
            echo "  -s, --standard     只显示标准字段"
            echo "  -c, --custom       只显示自定义字段"
            echo "  -a, --all          显示所有字段（默认）"
            echo "  -h, --help         显示帮助"
            echo ""
            echo "示例:"
            echo "  $0 -p b70                    # 获取前缀 b70 的字段"
            echo "  $0 -o productuplist          # 获取 productuplist 对象的字段"
            echo "  $0 -p 001 -s                 # 只获取 Account 的标准字段"
            exit 0
            ;;
        *)
            echo "❌ 未知选项：$1"
            exit 1
            ;;
    esac
done

# 验证参数
if [ -z "$OBJECT_PREFIX" ] && [ -z "$OBJECT_API" ]; then
    echo "❌ 必须指定对象前缀 (-p) 或对象 API 名称 (-o)"
    echo "使用 -h 查看帮助"
    exit 1
fi

# 如果提供的是对象 API 名称，需要先查找前缀
if [ -n "$OBJECT_API" ] && [ -z "$OBJECT_PREFIX" ]; then
    echo "🔍 查找对象 '$OBJECT_API' 的前缀..."
    
    # 从自定义对象中查找
    CUSTOM_RESPONSE=$(curl -s -X POST "$API_DOMAIN/api/customObject/list" \
      -H "accessToken: $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"id":""}')
    
    OBJECT_PREFIX=$(echo "$CUSTOM_RESPONSE" | jq -r --arg api "$OBJECT_API" \
      '.data.objList[] | select(.schemetable_name == $api) | .prefix')
    
    if [ -z "$OBJECT_PREFIX" ] || [ "$OBJECT_PREFIX" == "null" ]; then
        # 从标准对象中查找
        STANDARD_RESPONSE=$(curl -s -X POST "$API_DOMAIN/api/customObject/standardObjList" \
          -H "accessToken: $ACCESS_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{}')
        
        OBJECT_PREFIX=$(echo "$STANDARD_RESPONSE" | jq -r --arg api "$OBJECT_API" \
          '.data[] | select(.label == $api) | .objprefix')
    fi
    
    if [ -z "$OBJECT_PREFIX" ] || [ "$OBJECT_PREFIX" == "null" ]; then
        echo "❌ 未找到对象 '$OBJECT_API'"
        exit 1
    fi
    
    echo "✅ 找到前缀：$OBJECT_PREFIX"
fi

echo "📋 对象字段列表 (prefix: $OBJECT_PREFIX)"
echo "========================================"
echo ""

# 获取字段信息
FIELDS_RESPONSE=$(curl -s -X POST "$API_DOMAIN/api/fieldSetup/queryField" \
  -H "accessToken: $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"prefix\":\"$OBJECT_PREFIX\"}")

RESULT=$(echo "$FIELDS_RESPONSE" | jq -r '.result')
if [ "$RESULT" != "true" ]; then
    echo "❌ 获取字段失败：$(echo "$FIELDS_RESPONSE" | jq -r '.returnInfo')"
    exit 1
fi

# 显示对象信息
OBJ_INFO=$(echo "$FIELDS_RESPONSE" | jq '.data.obj')
if [ "$OBJ_INFO" != "null" ]; then
    echo "对象信息:"
    echo "$FIELDS_RESPONSE" | jq '.data.obj'
    echo ""
fi

# 显示标准字段
if [ "$SHOW_CUSTOM" = false ]; then
    STD_COUNT=$(echo "$FIELDS_RESPONSE" | jq '.data.stdFields | length')
    echo "标准字段 ($STD_COUNT 个):"
    echo "-------------------"
    
    if [ "$STD_COUNT" -gt 0 ]; then
        echo "$FIELDS_RESPONSE" | jq -r '.data.stdFields[] | "  \(.labelName) -> \(.schemefieldName) (\(.schemefieldType))"'
    else
        echo "  (无标准字段或字段为空)"
    fi
    echo ""
fi

# 显示自定义字段
if [ "$SHOW_STANDARD" = false ]; then
    CUS_COUNT=$(echo "$FIELDS_RESPONSE" | jq '.data.cusFields | length')
    echo "自定义字段 ($CUS_COUNT 个):"
    echo "---------------------"
    
    if [ "$CUS_COUNT" -gt 0 ]; then
        echo "$FIELDS_RESPONSE" | jq -r '.data.cusFields[] | "  \(.labelName) -> \(.schemefieldName) (\(.schemefieldType))"'
    else
        echo "  (无自定义字段或字段为空)"
    fi
    echo ""
fi

# 显示字段类型说明
if [ "$SHOW_ALL" = true ]; then
    echo "📝 字段类型说明:"
    echo "  S=文本，N=数字，D=日期，F=日期/时间，L=选项列表，Q=多选列表"
    echo "  Y=查找关系，M=主详关系，B=复选框，E=邮件，H=电话，U=URL"
    echo "  J=文本区，A=富文本，IMG=图片，FL=文件，C=币种，P=百分比"
fi
