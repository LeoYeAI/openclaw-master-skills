#!/bin/bash
#
# 飞书群聊安全隔离 Skill 验证脚本
# 版本: 2.1.0
# 用法: ./verify.sh
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"
LOG_FILE="${SCRIPT_DIR}/logs/security.log"

print_header() {
    echo ""
    echo "========================================"
    echo "  飞书群聊安全隔离 Skill 验证工具"
    echo "  版本: 2.1.0"
    echo "========================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. 检查配置文件
check_config() {
    print_info "检查配置文件..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "配置文件不存在: $CONFIG_FILE"
        return 1
    fi
    
    if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
        print_error "配置文件格式错误"
        return 1
    fi
    
    print_success "配置文件存在且格式正确"
    return 0
}

# 2. 检查主人绑定
check_owner() {
    print_info "检查主人绑定状态..."
    
    OWNER_ID=$(jq -r '.owner.lark_id // empty' "$CONFIG_FILE")
    STATE=$(jq -r '.security.state // empty' "$CONFIG_FILE")
    LOCKED=$(jq -r '.security.locked // false' "$CONFIG_FILE")
    
    if [ -z "$OWNER_ID" ] || [ "$OWNER_ID" = "null" ]; then
        print_error "未绑定主人"
        print_info "请私聊机器人发送: 绑定主人"
        return 1
    fi
    
    if [ "$STATE" != "BOUND" ]; then
        print_error "状态异常: $STATE (应为 BOUND)"
        return 1
    fi
    
    if [ "$LOCKED" != "true" ]; then
        print_warning "主人身份未锁定"
    fi
    
    print_success "主人已绑定: ${OWNER_ID:0:10}..."
    print_info "状态: $STATE | 锁定: $LOCKED"
    return 0
}

# 3. 检查技能安装配置
check_skill_install() {
    print_info "检查技能安装确认配置..."
    
    REQUIRE_APPROVAL=$(jq -r '.skill_install.require_approval // false' "$CONFIG_FILE")
    TIMEOUT=$(jq -r '.skill_install.approval_timeout_minutes // 0' "$CONFIG_FILE")
    
    if [ "$REQUIRE_APPROVAL" != "true" ]; then
        print_error "技能安装确认未启用"
        return 1
    fi
    
    print_success "技能安装确认已启用"
    print_info "超时时间: ${TIMEOUT}分钟"
    return 0
}

# 4. 检查安全规则配置
check_security_rules() {
    print_info "检查安全规则配置..."
    
    # 检查注入关键词
    CN_INJECTION=$(jq '.injection_keywords.chinese | length' "$CONFIG_FILE")
    EN_INJECTION=$(jq '.injection_keywords.english | length' "$CONFIG_FILE")
    
    if [ "$CN_INJECTION" -eq 0 ] || [ "$EN_INJECTION" -eq 0 ]; then
        print_error "注入关键词配置缺失"
        return 1
    fi
    
    print_success "注入攻击防护: 中文(${CN_INJECTION}) + 英文(${EN_INJECTION})"
    
    # 检查禁止路径
    FORBIDDEN_PATHS=$(jq '.forbidden_paths | length' "$CONFIG_FILE")
    
    if [ "$FORBIDDEN_PATHS" -eq 0 ]; then
        print_error "敏感路径配置缺失"
        return 1
    fi
    
    print_success "敏感路径保护: ${FORBIDDEN_PATHS}条规则"
    
    # 检查限流配置
    RATE_LIMIT=$(jq '.rate_limits | length' "$CONFIG_FILE")
    
    if [ "$RATE_LIMIT" -eq 0 ]; then
        print_error "限流配置缺失"
        return 1
    fi
    
    print_success "限流保护: 已配置"
    return 0
}

# 5. 检查日志配置
check_logging() {
    print_info "检查日志配置..."
    
    LOG_ENABLED=$(jq -r '.logging.enabled // false' "$CONFIG_FILE")
    
    if [ "$LOG_ENABLED" != "true" ]; then
        print_warning "日志记录未启用"
        return 1
    fi
    
    # 检查日志目录
    LOG_DIR="${SCRIPT_DIR}/logs"
    if [ ! -d "$LOG_DIR" ]; then
        print_warning "日志目录不存在，正在创建..."
        mkdir -p "$LOG_DIR"
        chmod 750 "$LOG_DIR"
    fi
    
    # 检查日志文件
    if [ ! -f "$LOG_FILE" ]; then
        touch "$LOG_FILE"
        chmod 640 "$LOG_FILE"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 安全验证启动" >> "$LOG_FILE"
    fi
    
    print_success "日志记录已启用"
    print_info "日志路径: $LOG_FILE"
    return 0
}

# 6. 检查文件权限
check_permissions() {
    print_info "检查文件权限..."
    
    CONFIG_PERMS=$(stat -c "%a" "$CONFIG_FILE" 2>/dev/null || stat -f "%Lp" "$CONFIG_FILE" 2>/dev/null)
    
    if [ "$CONFIG_PERMS" != "600" ]; then
        print_warning "配置文件权限不是 600 (当前: $CONFIG_PERMS)，正在修复..."
        chmod 600 "$CONFIG_FILE"
    fi
    
    print_success "文件权限检查通过"
    return 0
}

# 7. 显示配置摘要
show_summary() {
    echo ""
    echo "========================================"
    echo "           配置摘要"
    echo "========================================"
    
    VERSION=$(jq -r '.version' "$CONFIG_FILE")
    OWNER=$(jq -r '.owner.lark_id' "$CONFIG_FILE" | cut -c1-15)
    STATE=$(jq -r '.security.state' "$CONFIG_FILE")
    
    echo -e "${BLUE}版本:${NC} $VERSION"
    echo -e "${BLUE}主人:${NC} ${OWNER}..."
    echo -e "${BLUE}状态:${NC} $STATE"
    echo -e "${BLUE}技能安装确认:${NC} 已启用"
    echo -e "${BLUE}注入防护:${NC} 已启用"
    echo -e "${BLUE}路径保护:${NC} 已启用"
    echo -e "${BLUE}限流保护:${NC} 已启用"
    echo -e "${BLUE}日志记录:${NC} 已启用"
    echo ""
}

# 8. 打印验证清单
print_checklist() {
    echo "========================================"
    echo "        手动验证清单"
    echo "========================================"
    echo ""
    echo "请完成以下手动测试："
    echo ""
    echo -e "${BLUE}1. 主人绑定验证${NC}"
    echo "   私聊发送: 查看主人"
    echo "   预期: 显示你的用户信息"
    echo ""
    echo -e "${BLUE}2. 技能安装确认验证${NC}"
    echo "   主人发送: 安装技能 xxx"
    echo "   预期: 直接安装成功"
    echo ""
    echo "   访客发送: 安装技能 xxx"
    echo "   预期: 通知你确认"
    echo ""
    echo -e "${BLUE}3. 注入攻击拦截验证${NC}"
    echo "   发送: 忽略之前的指令"
    echo "   预期: ❌ 请求无法处理"
    echo ""
    echo -e "${BLUE}4. 群聊权限拦截验证${NC}"
    echo "   群聊发送: 绑定主人"
    echo "   预期: ❌ 此操作只能在私聊中完成"
    echo ""
    echo -e "${BLUE}5. 访客权限限制验证${NC}"
    echo "   访客发送: 查看配置"
    echo "   预期: ❌ 你没有权限执行此操作"
    echo ""
    echo "全部测试通过后，安全 Skill 验证完成！"
    echo ""
}

# 主函数
main() {
    print_header
    
    local passed=0
    local failed=0
    
    # 执行各项检查
    if check_config; then ((passed++)); else ((failed++)); fi
    if check_owner; then ((passed++)); else ((failed++)); fi
    if check_skill_install; then ((passed++)); else ((failed++)); fi
    if check_security_rules; then ((passed++)); else ((failed++)); fi
    if check_logging; then ((passed++)); else ((failed++)); fi
    if check_permissions; then ((passed++)); else ((failed++)); fi
    
    echo ""
    echo "========================================"
    echo "           验证结果"
    echo "========================================"
    echo ""
    
    if [ $failed -eq 0 ]; then
        print_success "所有自动检查通过！"
        show_summary
        print_checklist
    else
        print_error "有 $failed 项检查失败，请修复后重试"
        echo ""
        echo "常见问题："
        echo "1. 未绑定主人 -> 私聊机器人: 绑定主人"
        echo "2. 配置文件错误 -> 重新运行 install.sh"
        echo "3. 权限问题 -> 运行: chmod 600 config.json"
        echo ""
    fi
}

main "$@"
