#!/usr/bin/env bash
# ============================================================
# preflight-check.sh — 通用预检脚本
# 检查系统环境、必需工具、网络连通性
# 兼容 Ubuntu 20.04+/22.04+、macOS 12+
# 支持 x86_64 和 arm64
# ============================================================
set -euo pipefail

# === 颜色定义 ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# === 日志函数 ===
LOG_FILE="${DEVOPS_LOG:-${HOME}/devops-agent.log}"

log_info()  { echo -e "${GREEN}[✓]${NC} $*"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] [PREFLIGHT] [INFO] $*" >> "$LOG_FILE"; }
log_warn()  { echo -e "${YELLOW}[!]${NC} $*"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] [PREFLIGHT] [WARN] $*" >> "$LOG_FILE"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] [PREFLIGHT] [ERROR] $*" >> "$LOG_FILE"; }
log_title() { echo -e "\n${BLUE}=== $* ===${NC}"; }

# === 结果收集 ===
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

check_pass() { PASS_COUNT=$((PASS_COUNT + 1)); log_info "$*"; }
check_warn() { WARN_COUNT=$((WARN_COUNT + 1)); log_warn "$*"; }
check_fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); log_error "$*"; }

# === 参数解析 ===
# 用法: ./preflight-check.sh [deploy|monitor|backup|diagnose] [--tools tool1,tool2]
COMMAND="${1:-all}"
REQUIRED_TOOLS="${2:-}"

# ============================================================
# 1. 操作系统检测
# ============================================================
detect_os() {
    log_title "操作系统检测"

    OS_TYPE=$(uname -s)
    OS_ARCH=$(uname -m)
    KERNEL_VERSION=$(uname -r)

    echo "  系统类型: $OS_TYPE"
    echo "  架构: $OS_ARCH"
    echo "  内核版本: $KERNEL_VERSION"

    case "$OS_TYPE" in
        Linux)
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO_NAME="$NAME"
                DISTRO_VERSION="$VERSION_ID"
                echo "  发行版: $DISTRO_NAME $DISTRO_VERSION"
                check_pass "Linux ($DISTRO_NAME $DISTRO_VERSION, $OS_ARCH)"
            else
                DISTRO_NAME="Unknown"
                DISTRO_VERSION="Unknown"
                check_warn "无法识别 Linux 发行版"
            fi
            ;;
        Darwin)
            MACOS_VERSION=$(sw_vers -productVersion)
            echo "  macOS 版本: $MACOS_VERSION"
            check_pass "macOS $MACOS_VERSION ($OS_ARCH)"
            DISTRO_NAME="macOS"
            DISTRO_VERSION="$MACOS_VERSION"
            ;;
        *)
            check_fail "不支持的操作系统: $OS_TYPE"
            ;;
    esac

    # 架构检查
    case "$OS_ARCH" in
        x86_64|amd64)
            check_pass "架构: x86_64 (amd64)"
            ;;
        aarch64|arm64)
            check_pass "架构: arm64 (aarch64)"
            ;;
        *)
            check_warn "未经测试的架构: $OS_ARCH"
            ;;
    esac
}

# ============================================================
# 2. 必需工具检查
# ============================================================
check_tool() {
    local tool="$1"
    local required="${2:-optional}"  # required 或 optional

    if command -v "$tool" &>/dev/null; then
        local version
        version=$("$tool" --version 2>/dev/null | head -1 || echo "版本未知")
        check_pass "$tool 已安装 ($version)"
        return 0
    else
        if [ "$required" = "required" ]; then
            check_fail "$tool 未安装（必需）"
            # 给出安装建议
            suggest_install "$tool"
        else
            check_warn "$tool 未安装（可选）"
        fi
        return 1
    fi
}

suggest_install() {
    local tool="$1"
    echo -n "  安装建议: "

    case "$OS_TYPE" in
        Linux)
            case "$tool" in
                docker)     echo "curl -fsSL https://get.docker.com | sh" ;;
                nginx)      echo "sudo apt install nginx  # 或 sudo yum install nginx" ;;
                certbot)    echo "sudo apt install certbot python3-certbot-nginx" ;;
                node|nodejs) echo "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs" ;;
                python3)    echo "sudo apt install python3 python3-pip python3-venv" ;;
                go)         echo "wget https://go.dev/dl/go1.22.0.linux-$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz && sudo tar -C /usr/local -xzf go*.tar.gz" ;;
                git)        echo "sudo apt install git" ;;
                curl)       echo "sudo apt install curl" ;;
                wget)       echo "sudo apt install wget" ;;
                jq)         echo "sudo apt install jq" ;;
                prometheus) echo "参见 monitor 命令自动安装" ;;
                grafana-server) echo "参见 monitor 命令自动安装" ;;
                pg_dump)    echo "sudo apt install postgresql-client" ;;
                mysqldump)  echo "sudo apt install mysql-client" ;;
                mongodump)  echo "参见 MongoDB 官方文档安装 mongodb-database-tools" ;;
                *)          echo "sudo apt install $tool  # 请根据发行版调整" ;;
            esac
            ;;
        Darwin)
            case "$tool" in
                docker)     echo "brew install --cask docker" ;;
                nginx)      echo "brew install nginx" ;;
                certbot)    echo "brew install certbot" ;;
                node|nodejs) echo "brew install node" ;;
                python3)    echo "brew install python3" ;;
                go)         echo "brew install go" ;;
                *)          echo "brew install $tool" ;;
            esac
            ;;
    esac
}

check_required_tools() {
    log_title "工具检查"

    # 基础工具（始终检查）
    local base_tools=(git curl wget jq)
    for tool in "${base_tools[@]}"; do
        check_tool "$tool" "required"
    done

    # 根据命令类型检查特定工具
    case "$COMMAND" in
        deploy)
            check_tool "docker" "optional"
            check_tool "nginx" "optional"
            check_tool "certbot" "optional"
            check_tool "node" "optional"
            check_tool "python3" "optional"
            check_tool "go" "optional"
            ;;
        monitor)
            check_tool "prometheus" "optional"
            check_tool "grafana-server" "optional"
            ;;
        backup)
            check_tool "pg_dump" "optional"
            check_tool "mysqldump" "optional"
            check_tool "mongodump" "optional"
            check_tool "gpg" "optional"
            ;;
        diagnose)
            check_tool "ss" "optional"
            check_tool "iostat" "optional"
            check_tool "dig" "optional"
            ;;
    esac

    # 自定义工具列表
    if [ -n "$REQUIRED_TOOLS" ]; then
        IFS=',' read -ra TOOLS <<< "$REQUIRED_TOOLS"
        for tool in "${TOOLS[@]}"; do
            check_tool "$(echo "$tool" | xargs)" "required"
        done
    fi
}

# ============================================================
# 3. 网络连通性检查
# ============================================================
check_network() {
    log_title "网络检查"

    # 外网访问
    if curl -s --connect-timeout 5 -o /dev/null https://www.google.com 2>/dev/null || \
       curl -s --connect-timeout 5 -o /dev/null https://www.baidu.com 2>/dev/null; then
        check_pass "外网访问正常"
    else
        check_warn "外网访问不可用（可能影响软件包下载）"
    fi

    # DNS 解析
    if command -v dig &>/dev/null; then
        if dig +short google.com &>/dev/null; then
            check_pass "DNS 解析正常"
        else
            check_warn "DNS 解析异常"
        fi
    elif command -v nslookup &>/dev/null; then
        if nslookup google.com &>/dev/null; then
            check_pass "DNS 解析正常"
        else
            check_warn "DNS 解析异常"
        fi
    else
        check_warn "无 DNS 检测工具（dig/nslookup）"
    fi

    # 常用端口检查
    local ports_in_use
    if command -v ss &>/dev/null; then
        ports_in_use=$(ss -tlnp 2>/dev/null | grep -c LISTEN || true)
    elif command -v netstat &>/dev/null; then
        ports_in_use=$(netstat -tlnp 2>/dev/null | grep -c LISTEN || true)
    else
        ports_in_use="未知"
    fi
    log_info "当前监听端口数: $ports_in_use"
}

# ============================================================
# 4. 磁盘空间检查
# ============================================================
check_disk() {
    log_title "磁盘空间"

    # 检查根分区可用空间
    local available_kb
    if [ "$OS_TYPE" = "Darwin" ]; then
        available_kb=$(df -k / | tail -1 | awk '{print $4}')
    else
        available_kb=$(df -k / | tail -1 | awk '{print $4}')
    fi

    local available_gb=$((available_kb / 1024 / 1024))

    if [ "$available_gb" -ge 5 ]; then
        check_pass "根分区可用空间: ${available_gb}GB"
    elif [ "$available_gb" -ge 1 ]; then
        check_warn "根分区可用空间较低: ${available_gb}GB（建议 > 5GB）"
    else
        check_fail "根分区空间严重不足: ${available_gb}GB（需要 > 1GB）"
    fi

    # /var 分区（如果单独挂载）
    if mountpoint -q /var 2>/dev/null; then
        local var_available_kb
        var_available_kb=$(df -k /var | tail -1 | awk '{print $4}')
        local var_available_gb=$((var_available_kb / 1024 / 1024))
        if [ "$var_available_gb" -ge 2 ]; then
            check_pass "/var 分区可用空间: ${var_available_gb}GB"
        else
            check_warn "/var 分区空间较低: ${var_available_gb}GB"
        fi
    fi
}

# ============================================================
# 5. 权限检查
# ============================================================
check_permissions() {
    log_title "权限检查"

    # 当前用户
    log_info "当前用户: $(whoami)"
    log_info "用户 ID: $(id)"

    # sudo 可用性
    if command -v sudo &>/dev/null; then
        if sudo -n true 2>/dev/null; then
            check_pass "sudo 可用（免密码）"
        else
            check_warn "sudo 可用（需要密码）"
        fi
    else
        check_warn "sudo 不可用"
    fi

    # Docker 权限（如果 Docker 已安装）
    if command -v docker &>/dev/null; then
        if docker info &>/dev/null; then
            check_pass "Docker 权限正常"
        else
            check_warn "Docker 需要 sudo 或将用户加入 docker 组"
        fi
    fi
}

# ============================================================
# 主流程
# ============================================================
main() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  DevOps Agent — 环境预检  ${NC}"
    echo -e "${BLUE}  命令: $COMMAND${NC}"
    echo -e "${BLUE}  时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}================================================${NC}"

    detect_os
    check_required_tools
    check_network
    check_disk
    check_permissions

    # === 汇总 ===
    echo ""
    log_title "预检结果汇总"
    echo -e "  ${GREEN}通过: $PASS_COUNT${NC}"
    echo -e "  ${YELLOW}警告: $WARN_COUNT${NC}"
    echo -e "  ${RED}失败: $FAIL_COUNT${NC}"

    if [ "$FAIL_COUNT" -gt 0 ]; then
        echo ""
        log_error "预检未通过，请先解决上述问题"
        exit 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        echo ""
        log_warn "预检通过（有警告），建议关注上述问题"
        exit 0
    else
        echo ""
        log_info "预检全部通过"
        exit 0
    fi
}

main "$@"
