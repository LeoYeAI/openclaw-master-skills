#!/bin/bash
#
# 飞书群聊安全隔离 Skill 安装脚本
# 版本: 2.0.0
# 作者: 云策
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

check_dependencies() {
    print_info "检查依赖..."
    if ! command -v jq &> /dev/null; then
        print_error "未找到 jq，请先安装"
        exit 1
    fi
    print_success "依赖检查通过"
}

setup_directories() {
    print_info "创建目录结构..."
    mkdir -p "${SCRIPT_DIR}/logs"
    chmod 700 "${SCRIPT_DIR}"
    chmod 750 "${SCRIPT_DIR}/logs"
    print_success "目录创建完成"
}

auto_identify_owner() {
    print_info "尝试自动识别主人..."
    
    OWNER_ID=""
    IDENTIFIED_BY=""
    
    # 1. 检查 OpenClaw 配置
    OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"
    if [ -f "$OPENCLAW_CONFIG" ]; then
        OWNER_ID=$(jq -r '.owner.lark_id // empty' "$OPENCLAW_CONFIG" 2>/dev/null)
        if [ -n "$OWNER_ID" ] && [ "$OWNER_ID" != "null" ]; then
            IDENTIFIED_BY="openclaw_config"
            print_success "从 OpenClaw 配置识别到主人: $OWNER_ID"
        fi
    fi
    
    # 2. 检查环境变量
    if [ -z "$OWNER_ID" ] && [ -n "$FEISHU_OWNER_ID" ]; then
        OWNER_ID="$FEISHU_OWNER_ID"
        IDENTIFIED_BY="env_var"
        print_success "从环境变量识别到主人: $OWNER_ID"
    fi
    
    # 3. 检查飞书 API（需要凭证）
    # 这里需要用户配置飞书 App ID 和 Secret
    # 暂时跳过，由 Skill 运行时处理
    
    # 更新配置
    CONFIG_FILE="${SCRIPT_DIR}/config.json"
    
    if [ -n "$OWNER_ID" ]; then
        # 自动识别成功，锁定主人
        jq --arg owner "$OWNER_ID" --arg by "$IDENTIFIED_BY" --arg time "$(date -Iseconds)" '
            .owner.lark_id = $owner |
            .owner.identified_at = $time |
            .owner.identified_by = $by |
            .security.state = "BOUND" |
            .security.locked = true
        ' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
        
        print_success "主人身份已自动锁定"
        return 0
    else
        print_warning "未能自动识别主人，进入待绑定状态"
        return 1
    fi
}

set_permissions() {
    print_info "设置文件权限..."
    chmod 600 "${SCRIPT_DIR}/config.json"
    print_success "权限设置完成"
}

create_log_file() {
    print_info "初始化日志文件..."
    LOG_FILE="${SCRIPT_DIR}/logs/security.log"
    touch "$LOG_FILE"
    chmod 640 "$LOG_FILE"
    
    cat >> "$LOG_FILE" << EOF
[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 飞书群聊安全隔离 Skill v2.0.0 初始化
[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 安装路径: ${SCRIPT_DIR}
EOF
    print_success "日志初始化完成"
}

print_completion() {
    echo ""
    echo "========================================"
    print_success "飞书群聊安全隔离 Skill 安装完成！"
    echo "========================================"
    echo ""
    
    CONFIG_FILE="${SCRIPT_DIR}/config.json"
    STATE=$(jq -r '.security.state' "$CONFIG_FILE")
    OWNER=$(jq -r '.owner.lark_id' "$CONFIG_FILE")
    
    if [ "$STATE" = "BOUND" ] && [ -n "$OWNER" ] && [ "$OWNER" != "null" ]; then
        echo -e "${GREEN}🔒 状态: 已绑定主人${NC}"
        echo -e "${GREEN}👤 主人ID: ${OWNER}${NC}"
        echo ""
        echo "群聊和其他人私聊已自动进入安全模式。"
    else
        echo -e "${YELLOW}⏳ 状态: 待绑定${NC}"
        echo ""
        echo -e "${BLUE}下一步操作:${NC}"
        echo "1. 私聊机器人发送: 绑定主人"
        echo "2. 回复"确认绑定"完成设置"
    fi
    
    echo ""
    echo -e "${BLUE}📖 文档:${NC}"
    echo "  SKILL.md - 完整安全规则"
    echo "  README.md - 使用说明"
    echo ""
}

main() {
    echo "========================================"
    echo "  飞书群聊安全隔离 Skill v2.0.0"
    echo "========================================"
    echo ""
    
    check_dependencies
    setup_directories
    auto_identify_owner || true
    set_permissions
    create_log_file
    print_completion
}

main "$@"
