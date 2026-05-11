#!/usr/bin/env bash
# ============================================================
# rollback.sh — 部署回滚脚本
# 根据快照目录恢复到部署前状态
# 用法: ./rollback.sh <snapshot-dir> [--dry-run]
# ============================================================
set -euo pipefail

# === 颜色定义 ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# === 日志 ===
LOG_FILE="${DEVOPS_LOG:-${HOME}/devops-agent.log}"
log() { echo -e "$*"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ROLLBACK] $*" >> "$LOG_FILE"; }
log_info()  { log "${GREEN}[✓]${NC} $*"; }
log_warn()  { log "${YELLOW}[!]${NC} $*"; }
log_error() { log "${RED}[✗]${NC} $*"; }
log_step()  { log "${BLUE}[→]${NC} $*"; }

# === 参数解析 ===
SNAPSHOT_DIR="${1:-}"
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
    esac
done

# === 参数校验 ===
if [ -z "$SNAPSHOT_DIR" ]; then
    echo "用法: $0 <snapshot-dir> [--dry-run]"
    echo ""
    echo "参数:"
    echo "  snapshot-dir    部署时创建的快照目录路径"
    echo "  --dry-run       仅显示将要执行的操作，不实际执行"
    echo ""
    echo "示例:"
    echo "  $0 ~/.devops-agent/snapshots/20260320_143000"
    echo "  $0 ~/.devops-agent/snapshots/20260320_143000 --dry-run"
    echo ""
    echo "可用快照:"
    if [ -d "$HOME/.devops-agent/snapshots" ]; then
        ls -lt "$HOME/.devops-agent/snapshots/" 2>/dev/null | head -10
    else
        echo "  (无快照)"
    fi
    exit 1
fi

if [ ! -d "$SNAPSHOT_DIR" ]; then
    log_error "快照目录不存在: $SNAPSHOT_DIR"
    exit 1
fi

# === dry-run 执行封装 ===
# 注意：传入实际命令和参数，不要传字符串
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] $*"
    else
        "$@"
    fi
}

# === 路径安全校验 ===
# 拒绝对系统关键目录执行破坏性操作
validate_path() {
    local path="$1"
    if [[ -z "$path" || "$path" == "/" || "$path" == "/usr" || "$path" == "/etc" \
       || "$path" == "/home" || "$path" == "/var" || "$path" == "/bin" \
       || "$path" == "/sbin" || "$path" == "/lib" || "$path" == "/boot" \
       || "$path" == "/root" || "$path" == "/opt" ]]; then
        log_error "路径不合法或为系统关键目录: '$path'，拒绝操作"
        return 1
    fi
    return 0
}

# ============================================================
# 回滚元数据读取
# ============================================================
read_metadata() {
    log_step "读取快照元数据..."

    # 读取快照清单
    if [ -f "$SNAPSHOT_DIR/manifest.json" ]; then
        log_info "发现 manifest.json"
        cat "$SNAPSHOT_DIR/manifest.json"
    elif [ -f "$SNAPSHOT_DIR/manifest.txt" ]; then
        log_info "发现 manifest.txt"
        cat "$SNAPSHOT_DIR/manifest.txt"
    fi

    # 列出快照内容
    echo ""
    log_step "快照内容:"
    ls -la "$SNAPSHOT_DIR/"
}

# ============================================================
# 应用代码回滚
# ============================================================
rollback_app() {
    if [ -d "$SNAPSHOT_DIR/app_backup" ]; then
        log_step "回滚应用代码..."

        # 从快照中读取原始部署目录
        local deploy_dir
        if [ -f "$SNAPSHOT_DIR/deploy_dir.txt" ]; then
            deploy_dir=$(cat "$SNAPSHOT_DIR/deploy_dir.txt")
        else
            # 尝试从 app_backup 目录名推断
            log_warn "未找到 deploy_dir.txt，请输入原始部署目录:"
            read -r deploy_dir
        fi

        if [ -z "$deploy_dir" ]; then
            log_error "无法确定部署目录，跳过应用回滚"
            return 1
        fi

        echo ""
        echo "  将要执行:"
        echo "  1. 停止当前服务"
        echo "  2. 备份当前版本到 ${SNAPSHOT_DIR}/rollback_backup/"
        echo "  3. 恢复 ${SNAPSHOT_DIR}/app_backup/ → ${deploy_dir}/"
        echo "  4. 重启服务"
        echo ""

        if [ "$DRY_RUN" = false ]; then
            read -rp "确认回滚应用代码？(y/N): " confirm
            if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                log_warn "用户取消应用回滚"
                return 0
            fi
        fi

        # 路径安全校验
        if ! validate_path "$deploy_dir"; then
            return 1
        fi

        # 备份当前版本（以防回滚的回滚）
        run_cmd mkdir -p "${SNAPSHOT_DIR}/rollback_backup"
        if [ -d "$deploy_dir" ]; then
            run_cmd cp -r "${deploy_dir}" "${SNAPSHOT_DIR}/rollback_backup/"
        fi

        # 恢复备份
        run_cmd rm -rf "${deploy_dir}"
        run_cmd cp -r "${SNAPSHOT_DIR}/app_backup" "${deploy_dir}"

        log_info "应用代码已回滚"
    else
        log_warn "快照中无应用备份，跳过"
    fi
}

# ============================================================
# 服务状态回滚
# ============================================================
rollback_service() {
    log_step "回滚服务状态..."

    # systemd 服务
    if [ -f "$SNAPSHOT_DIR/service_status" ]; then
        local service_name
        service_name=$(cat "$SNAPSHOT_DIR/service_name.txt" 2>/dev/null || echo "")
        local prev_status
        prev_status=$(cat "$SNAPSHOT_DIR/service_status")

        if [ -n "$service_name" ]; then
            echo "  服务: $service_name"
            echo "  部署前状态: $prev_status"

            case "$prev_status" in
                active)
                    run_cmd sudo systemctl restart "$service_name"
                    log_info "服务 $service_name 已重启"
                    ;;
                inactive)
                    run_cmd sudo systemctl stop "$service_name"
                    log_info "服务 $service_name 已停止（恢复为部署前的 inactive 状态）"
                    ;;
                *)
                    log_warn "部署前服务状态为 '$prev_status'，需手动处理"
                    ;;
            esac
        fi
    fi

    # Docker 容器
    if [ -f "$SNAPSHOT_DIR/container_state.json" ]; then
        local container_name
        container_name=$(cat "$SNAPSHOT_DIR/container_name.txt" 2>/dev/null || echo "")

        if [ -n "$container_name" ]; then
            log_step "回滚 Docker 容器: $container_name"

            # 如果有之前的镜像 tag
            if [ -f "$SNAPSHOT_DIR/docker_image.txt" ]; then
                local prev_image
                prev_image=$(cat "$SNAPSHOT_DIR/docker_image.txt")
                echo "  恢复镜像: $prev_image"
                run_cmd docker stop "$container_name" || true
                run_cmd docker rm "$container_name" || true
                log_info "请手动使用之前的镜像重新启动: docker run ... $prev_image"
            fi
        fi
    fi

    # docker-compose
    if [ -f "$SNAPSHOT_DIR/docker-compose.yml" ]; then
        log_step "发现 docker-compose.yml 备份"
        local deploy_dir
        deploy_dir=$(cat "$SNAPSHOT_DIR/deploy_dir.txt" 2>/dev/null || echo "")
        if [ -n "$deploy_dir" ] && [ -d "$deploy_dir" ]; then
            run_cmd cp "${SNAPSHOT_DIR}/docker-compose.yml" "${deploy_dir}/docker-compose.yml"
            (cd "${deploy_dir}" && run_cmd docker compose down && run_cmd docker compose up -d)
            log_info "docker-compose 已回滚"
        fi
    fi
}

# ============================================================
# Nginx 配置回滚
# ============================================================
rollback_nginx() {
    if [ -f "$SNAPSHOT_DIR/nginx_config" ] || [ -d "$SNAPSHOT_DIR/nginx_backup" ]; then
        log_step "回滚 Nginx 配置..."

        if [ -f "$SNAPSHOT_DIR/nginx_site.txt" ]; then
            local site_name
            site_name=$(cat "$SNAPSHOT_DIR/nginx_site.txt")
            local nginx_conf="/etc/nginx/sites-available/$site_name"

            echo "  恢复 Nginx 配置: $nginx_conf"

            if [ "$DRY_RUN" = false ]; then
                read -rp "确认回滚 Nginx 配置？(y/N): " confirm
                if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                    log_warn "用户取消 Nginx 回滚"
                    return 0
                fi
            fi

            if [ -f "$SNAPSHOT_DIR/nginx_config" ]; then
                run_cmd sudo cp "${SNAPSHOT_DIR}/nginx_config" "$nginx_conf"
            else
                # 如果之前没有配置，删除新建的
                run_cmd sudo rm -f "$nginx_conf"
                run_cmd sudo rm -f "/etc/nginx/sites-enabled/$site_name"
            fi

            run_cmd sudo nginx -t && run_cmd sudo systemctl reload nginx
            log_info "Nginx 配置已回滚"
        fi
    else
        log_warn "快照中无 Nginx 配置备份，跳过"
    fi
}

# ============================================================
# SSL 证书回滚（提示用户）
# ============================================================
rollback_ssl() {
    if [ -f "$SNAPSHOT_DIR/ssl_domain.txt" ]; then
        local domain
        domain=$(cat "$SNAPSHOT_DIR/ssl_domain.txt")
        log_warn "SSL 证书（$domain）无法自动回滚"
        echo "  如需撤销证书，请手动执行:"
        echo "  sudo certbot delete --cert-name $domain"
    fi
}

# ============================================================
# 主流程
# ============================================================
main() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  DevOps Agent — 部署回滚${NC}"
    echo -e "${BLUE}  快照: $SNAPSHOT_DIR${NC}"
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}  模式: DRY-RUN（仅预览）${NC}"
    fi
    echo -e "${BLUE}  时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}================================================${NC}"

    read_metadata
    echo ""

    if [ "$DRY_RUN" = false ]; then
        echo -e "${YELLOW}警告: 回滚操作将修改系统状态${NC}"
        read -rp "确认继续？(y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            log_warn "用户取消回滚"
            exit 0
        fi
    fi

    rollback_app
    rollback_service
    rollback_nginx
    rollback_ssl

    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  回滚完成${NC}"
    echo -e "${BLUE}================================================${NC}"

    if [ "$DRY_RUN" = true ]; then
        echo ""
        echo "以上为预览模式。确认无误后去掉 --dry-run 执行实际回滚。"
    else
        log_info "回滚操作完成。请验证服务状态。"
        echo ""
        echo "验证建议:"
        echo "  1. 检查服务状态: systemctl status <service-name>"
        echo "  2. 检查 HTTP 响应: curl -I https://<domain>"
        echo "  3. 查看应用日志: journalctl -u <service-name> -f"
    fi
}

main "$@"
