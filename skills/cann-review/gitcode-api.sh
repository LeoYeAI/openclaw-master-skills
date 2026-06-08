#!/bin/bash
# GitCode API 辅助脚本
# 用于 CANN 代码审查技能

# 配置文件路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/gitcode.conf"

# 默认配置
DEFAULT_API_BASE="https://api.gitcode.com/api/v5"

# 加载配置
load_config() {
    # 优先级：环境变量 > 配置文件 > 默认值
    
    # API Token
    if [ -z "$GITCODE_API_TOKEN" ]; then
        if [ -f "$CONFIG_FILE" ]; then
            # 从配置文件读取（跳过注释和空行）
            GITCODE_API_TOKEN=$(grep -E "^GITCODE_API_TOKEN=" "$CONFIG_FILE" | cut -d'=' -f2-)
        fi
    fi
    
    # API Base URL
    if [ -z "$GITCODE_API_BASE" ]; then
        if [ -f "$CONFIG_FILE" ]; then
            GITCODE_API_BASE=$(grep -E "^GITCODE_API_BASE=" "$CONFIG_FILE" | cut -d'=' -f2-)
        fi
        [ -z "$GITCODE_API_BASE" ] && GITCODE_API_BASE="$DEFAULT_API_BASE"
    fi
    
    # 检查必需配置
    if [ -z "$GITCODE_API_TOKEN" ]; then
        echo "错误: 未配置 GitCode API Token"
        echo ""
        echo "配置方法："
        echo "  1. 复制配置模板:"
        echo "     cp $SCRIPT_DIR/config/gitcode.conf.example $CONFIG_FILE"
        echo ""
        echo "  2. 编辑 $CONFIG_FILE"
        echo "     设置 GITCODE_API_TOKEN=your_token_here"
        echo ""
        echo "  3. 或设置环境变量:"
        echo "     export GITCODE_API_TOKEN=your_token_here"
        echo ""
        echo "获取 Token: https://gitcode.com/setting/token-classic"
        exit 1
    fi
}

# 加载配置
load_config

# 使用配置
API_TOKEN="$GITCODE_API_TOKEN"
API_BASE="$GITCODE_API_BASE"

# 通用请求函数
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $API_TOKEN" \
            "${API_BASE}${endpoint}"
    else
        curl -s -X "$method" \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${API_BASE}${endpoint}"
    fi
}

# 获取 PR 信息
get_pr() {
    local owner=$1
    local repo=$2
    local pr_number=$3
    
    api_request "GET" "/repos/${owner}/${repo}/pulls/${pr_number}"
}

# 获取 PR 文件变更
get_pr_files() {
    local owner=$1
    local repo=$2
    local pr_number=$3
    
    api_request "GET" "/repos/${owner}/${repo}/pulls/${pr_number}/files"
}

# 发布 PR 评论
post_pr_comment() {
    local owner=$1
    local repo=$2
    local pr_number=$3
    local body=$4
    
    # 转义 JSON 字符串
    local escaped_body=$(echo "$body" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))")
    
    api_request "POST" "/repos/${owner}/${repo}/pulls/${pr_number}/comments" "{\"body\":${escaped_body}}"
}

# 获取开放的 PR 列表
get_open_prs() {
    local owner=$1
    local repo=$2
    
    api_request "GET" "/repos/${owner}/${repo}/pulls?state=opened"
}

# 配置向导
setup_config() {
    echo "🔧 GitCode API 配置向导"
    echo "========================"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        echo "✅ 配置文件已存在: $CONFIG_FILE"
        echo ""
        echo "当前配置:"
        grep -E "^GITCODE_" "$CONFIG_FILE" | sed 's/\(TOKEN=\).*/\1***/'
        echo ""
        read -p "是否重新配置? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    echo "请输入 GitCode API Token"
    echo "(获取地址: https://gitcode.com/setting/token-classic)"
    echo ""
    read -p "Token: " token
    
    if [ -z "$token" ]; then
        echo "❌ Token 不能为空"
        exit 1
    fi
    
    # 创建配置目录
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    # 写入配置文件
    cat > "$CONFIG_FILE" <<EOF
# GitCode API 配置
# 
# 获取 API Token: https://gitcode.com/setting/token-classic
# 权限要求: api, write_repository

# API Token（必需）
GITCODE_API_TOKEN=$token

# API Base URL（可选，默认值）
GITCODE_API_BASE=https://api.gitcode.com/api/v5
EOF
    
    # 设置文件权限（保护敏感信息）
    chmod 600 "$CONFIG_FILE"
    
    echo ""
    echo "✅ 配置已保存到: $CONFIG_FILE"
    echo ""
    echo "测试连接..."
    
    if curl -s -H "Authorization: Bearer $token" \
       "https://api.gitcode.com/api/v5/user" | grep -q "login"; then
        echo "✅ 连接成功！"
    else
        echo "❌ 连接失败，请检查 Token 是否正确"
        exit 1
    fi
}

# 使用示例
if [ "$1" = "setup" ]; then
    setup_config
elif [ "$1" = "get-pr" ]; then
    get_pr "$2" "$3" "$4"
elif [ "$1" = "get-files" ]; then
    get_pr_files "$2" "$3" "$4"
elif [ "$1" = "post-comment" ]; then
    post_pr_comment "$2" "$3" "$4" "$5"
elif [ "$1" = "list-prs" ]; then
    get_open_prs "$2" "$3"
else
    echo "用法:"
    echo "  $0 setup                        配置 GitCode API Token"
    echo "  $0 get-pr <owner> <repo> <pr>   获取 PR 信息"
    echo "  $0 get-files <owner> <repo> <pr> 获取 PR 文件变更"
    echo "  $0 post-comment <owner> <repo> <pr> <comment> 发布评论"
    echo "  $0 list-prs <owner> <repo>      列出开放的 PR"
    echo ""
    echo "首次使用请先运行: $0 setup"
    echo ""
    echo "示例:"
    echo "  $0 setup"
    echo "  $0 get-pr cann runtime 628"
    echo "  $0 get-files cann runtime 628"
    echo "  $0 post-comment cann runtime 628 'LGTM!'"
    echo "  $0 list-prs cann runtime"
fi
