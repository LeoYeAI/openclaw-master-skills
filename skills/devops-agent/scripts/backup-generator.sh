#!/usr/bin/env bash
# ============================================================
# backup-generator.sh — 备份脚本生成器
# 根据参数生成定制化的备份 shell 脚本
# 用法: ./backup-generator.sh --type <pg|mysql|mongo|dir> --target <target>
#        --dest <destination> [--schedule CRON] [--encrypt] [--retain DAYS]
# ============================================================
set -euo pipefail

# === 颜色定义 ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# === 默认值 ===
BACKUP_TYPE=""
TARGET=""
DESTINATION=""
SCHEDULE="0 2 * * *"
ENCRYPT=false
RETAIN_DAYS=30
OUTPUT_DIR="/opt/scripts"
NOTIFY_TYPE=""       # telegram / slack / email
DRY_RUN=false

# === 参数解析 ===
while [[ $# -gt 0 ]]; do
    case "$1" in
        --type)       BACKUP_TYPE="$2"; shift 2 ;;
        --target)     TARGET="$2"; shift 2 ;;
        --dest)       DESTINATION="$2"; shift 2 ;;
        --schedule)   SCHEDULE="$2"; shift 2 ;;
        --encrypt)    ENCRYPT=true; shift ;;
        --retain)     RETAIN_DAYS="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --notify)     NOTIFY_TYPE="$2"; shift 2 ;;
        --dry-run)    DRY_RUN=true; shift ;;
        --help|-h)
            echo "用法: $0 --type <pg|mysql|mongo|dir> --target <target> --dest <destination>"
            echo ""
            echo "参数:"
            echo "  --type       备份类型: pg, mysql, mongo, dir"
            echo "  --target     备份目标（数据库名或目录路径）"
            echo "  --dest       备份目的地（本地路径、s3://...、oss://...、rsync://...）"
            echo "  --schedule   cron 表达式（默认: 0 2 * * *）"
            echo "  --encrypt    启用 GPG 加密"
            echo "  --retain     保留天数（默认: 30）"
            echo "  --output-dir 脚本输出目录（默认: /opt/scripts）"
            echo "  --notify     通知类型: telegram, slack, email"
            echo "  --dry-run    仅预览生成的脚本，不写入文件"
            exit 0
            ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

# === 参数验证 ===
if [ -z "$BACKUP_TYPE" ] || [ -z "$TARGET" ] || [ -z "$DESTINATION" ]; then
    echo -e "${RED}错误: --type, --target, --dest 为必需参数${NC}"
    echo "使用 --help 查看帮助"
    exit 1
fi

# === 生成脚本名 ===
SCRIPT_NAME="backup_${BACKUP_TYPE}_$(echo "$TARGET" | tr '/' '_' | tr '.' '_').sh"
SCRIPT_PATH="${OUTPUT_DIR}/${SCRIPT_NAME}"

# ============================================================
# 脚本头部模板
# ============================================================
generate_header() {
    cat <<'HEADER_EOF'
#!/usr/bin/env bash
# ============================================================
# 自动生成的备份脚本
# 由 devops-agent backup-generator.sh 生成
HEADER_EOF
    echo "# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "# 备份类型: $BACKUP_TYPE"
    echo "# 备份目标: $TARGET"
    echo "# 备份目的地: $DESTINATION"
    cat <<'HEADER_EOF2'
# ============================================================
set -euo pipefail

# === 配置（可通过环境变量覆盖）===
HEADER_EOF2
    echo "BACKUP_TYPE=\"${BACKUP_TYPE}\""
    echo "TARGET=\"${TARGET}\""
    echo "DESTINATION=\"${DESTINATION}\""
    echo "RETAIN_DAYS=\"\${RETAIN_DAYS:-${RETAIN_DAYS}}\""
    echo "ENCRYPT=\"${ENCRYPT}\""
    cat <<'CONFIG_EOF'
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_BASE_DIR:-/var/backups/${BACKUP_TYPE}}"
LOG_FILE="${DEVOPS_LOG:-${HOME}/devops-agent.log}"

# === 日志函数 ===
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [BACKUP] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

log_error() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [BACKUP] [ERROR] $*"
    echo "$msg" >&2
    echo "$msg" >> "$LOG_FILE"
}

# === 错误处理 ===
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "备份失败 (exit code: $exit_code)"
        send_notification "❌ 备份失败: ${BACKUP_TYPE} - ${TARGET}" "exit code: $exit_code"
    fi
    # 清理临时文件
    rm -f "${BACKUP_DIR}/.tmp_backup_*" 2>/dev/null || true
}
trap cleanup EXIT

CONFIG_EOF
}

# ============================================================
# 备份命令模板（按类型）
# ============================================================
generate_backup_command() {
    case "$BACKUP_TYPE" in
        pg|postgresql)
            cat <<'PG_EOF'
# === PostgreSQL 备份 ===
BACKUP_FILE="${BACKUP_DIR}/pg_${TARGET}_${TIMESTAMP}.sql.gz"

log "开始 PostgreSQL 备份: ${TARGET}"
mkdir -p "$BACKUP_DIR"

# 检查 PostgreSQL 连接
if ! pg_isready -q 2>/dev/null; then
    log_error "PostgreSQL 未就绪"
    exit 1
fi

# 执行备份（使用 pg_dump 或 pg_dumpall）
if [ "$TARGET" = "all" ]; then
    pg_dumpall 2>/dev/null | gzip > "$BACKUP_FILE"
else
    pg_dump "$TARGET" 2>/dev/null | gzip > "$BACKUP_FILE"
fi

log "PostgreSQL 备份完成: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
PG_EOF
            ;;
        mysql)
            cat <<'MYSQL_EOF'
# === MySQL 备份 ===
BACKUP_FILE="${BACKUP_DIR}/mysql_${TARGET}_${TIMESTAMP}.sql.gz"

log "开始 MySQL 备份: ${TARGET}"
mkdir -p "$BACKUP_DIR"

# 检查 MySQL 连接
if ! mysqladmin ping -s 2>/dev/null; then
    log_error "MySQL 未就绪"
    exit 1
fi

# 执行备份
if [ "$TARGET" = "all" ]; then
    mysqldump --all-databases --single-transaction --routines --triggers 2>/dev/null | gzip > "$BACKUP_FILE"
else
    mysqldump --single-transaction --routines --triggers "$TARGET" 2>/dev/null | gzip > "$BACKUP_FILE"
fi

log "MySQL 备份完成: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
MYSQL_EOF
            ;;
        mongo|mongodb)
            cat <<'MONGO_EOF'
# === MongoDB 备份 ===
BACKUP_FILE="${BACKUP_DIR}/mongo_${TARGET}_${TIMESTAMP}.archive.gz"

log "开始 MongoDB 备份: ${TARGET}"
mkdir -p "$BACKUP_DIR"

# 执行备份
if [ "$TARGET" = "all" ]; then
    mongodump --archive="$BACKUP_FILE" --gzip 2>/dev/null
else
    mongodump --db="$TARGET" --archive="$BACKUP_FILE" --gzip 2>/dev/null
fi

log "MongoDB 备份完成: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
MONGO_EOF
            ;;
        dir|directory)
            cat <<'DIR_EOF'
# === 目录备份 ===
TARGET_BASENAME=$(basename "$TARGET")
BACKUP_FILE="${BACKUP_DIR}/${TARGET_BASENAME}_${TIMESTAMP}.tar.gz"

log "开始目录备份: ${TARGET}"
mkdir -p "$BACKUP_DIR"

# 检查目标目录
if [ ! -d "$TARGET" ]; then
    log_error "目标目录不存在: $TARGET"
    exit 1
fi

# 执行备份
tar czf "$BACKUP_FILE" -C "$(dirname "$TARGET")" "$(basename "$TARGET")"

log "目录备份完成: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
DIR_EOF
            ;;
    esac
}

# ============================================================
# 加密模块
# ============================================================
generate_encryption() {
    if [ "$ENCRYPT" = true ]; then
        cat <<'ENCRYPT_EOF'

# === 加密 ===
if [ "$ENCRYPT" = "true" ]; then
    log "加密备份文件..."
    GPG_KEY_FILE="${GPG_KEY_FILE:-${HOME}/.devops-agent/backup.key}"

    if [ ! -f "$GPG_KEY_FILE" ]; then
        log_error "GPG 密钥文件不存在: $GPG_KEY_FILE"
        log_error "请创建: echo 'your-passphrase' > $GPG_KEY_FILE && chmod 600 $GPG_KEY_FILE"
        exit 1
    fi

    gpg --symmetric --cipher-algo AES256 --batch --yes \
        --passphrase-file "$GPG_KEY_FILE" "$BACKUP_FILE"
    rm -f "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gpg"
    log "加密完成: $BACKUP_FILE"
fi
ENCRYPT_EOF
    fi
}

# ============================================================
# 完整性校验
# ============================================================
generate_checksum() {
    cat <<'CHECKSUM_EOF'

# === 完整性校验 ===
sha256sum "$BACKUP_FILE" > "${BACKUP_FILE}.sha256"
log "校验和已生成: ${BACKUP_FILE}.sha256"
CHECKSUM_EOF
}

# ============================================================
# 远程上传模块
# ============================================================
generate_upload() {
    case "$DESTINATION" in
        s3://*)
            cat <<UPLOAD_EOF

# === 上传到 S3 ===
log "上传到 S3: ${DESTINATION}"
aws s3 cp "\$BACKUP_FILE" "${DESTINATION}/\$(basename "\$BACKUP_FILE")"
aws s3 cp "\${BACKUP_FILE}.sha256" "${DESTINATION}/\$(basename "\${BACKUP_FILE}.sha256")"
log "S3 上传完成"
UPLOAD_EOF
            ;;
        oss://*)
            cat <<UPLOAD_EOF

# === 上传到阿里云 OSS ===
log "上传到 OSS: ${DESTINATION}"
ossutil cp "\$BACKUP_FILE" "${DESTINATION}/\$(basename "\$BACKUP_FILE")"
ossutil cp "\${BACKUP_FILE}.sha256" "${DESTINATION}/\$(basename "\${BACKUP_FILE}.sha256")"
log "OSS 上传完成"
UPLOAD_EOF
            ;;
        rsync://*)
            local rsync_dest="${DESTINATION#rsync://}"
            cat <<UPLOAD_EOF

# === rsync 远程同步 ===
log "rsync 同步到: ${rsync_dest}"
rsync -avz --progress "\$BACKUP_FILE" "${rsync_dest}/"
rsync -avz "\${BACKUP_FILE}.sha256" "${rsync_dest}/"
log "rsync 同步完成"
UPLOAD_EOF
            ;;
        /*)
            cat <<UPLOAD_EOF

# === 复制到本地目录 ===
DEST_DIR="${DESTINATION}"
mkdir -p "\$DEST_DIR"
cp "\$BACKUP_FILE" "\$DEST_DIR/"
cp "\${BACKUP_FILE}.sha256" "\$DEST_DIR/"
log "已复制到: \$DEST_DIR/"
UPLOAD_EOF
            ;;
    esac
}

# ============================================================
# 保留策略（日/周/月轮转）
# ============================================================
generate_retention() {
    cat <<'RETENTION_EOF'

# === 备份保留策略（日/周/月轮转）===
log "执行保留策略..."

# 创建轮转目录
mkdir -p "${BACKUP_DIR}/daily" "${BACKUP_DIR}/weekly" "${BACKUP_DIR}/monthly"

# 当前备份归入日备份
cp "$BACKUP_FILE" "${BACKUP_DIR}/daily/"

# 每周日的备份额外保留为周备份
DAY_OF_WEEK=$(date +%u)
if [ "$DAY_OF_WEEK" = "7" ]; then
    cp "$BACKUP_FILE" "${BACKUP_DIR}/weekly/"
    log "本次备份同时保留为周备份"
fi

# 每月1号的备份额外保留为月备份
DAY_OF_MONTH=$(date +%d)
if [ "$DAY_OF_MONTH" = "01" ]; then
    cp "$BACKUP_FILE" "${BACKUP_DIR}/monthly/"
    log "本次备份同时保留为月备份"
fi

# 清理过期备份
DAILY_DELETED=$(find "${BACKUP_DIR}/daily/" -type f -mtime +7 -delete -print 2>/dev/null | wc -l)
WEEKLY_DELETED=$(find "${BACKUP_DIR}/weekly/" -type f -mtime +28 -delete -print 2>/dev/null | wc -l)
MONTHLY_DELETED=$(find "${BACKUP_DIR}/monthly/" -type f -mtime +365 -delete -print 2>/dev/null | wc -l)
MAIN_DELETED=$(find "${BACKUP_DIR}/" -maxdepth 1 -type f -name "*.gz*" -mtime +"${RETAIN_DAYS}" -delete -print 2>/dev/null | wc -l)

log "清理完成: 日备份 ${DAILY_DELETED} 个, 周备份 ${WEEKLY_DELETED} 个, 月备份 ${MONTHLY_DELETED} 个, 主目录 ${MAIN_DELETED} 个"
RETENTION_EOF
}

# ============================================================
# 通知模块
# ============================================================
generate_notification() {
    cat <<'NOTIFY_EOF'

# === 通知函数 ===
send_notification() {
    local title="$1"
    local body="${2:-}"
NOTIFY_EOF

    case "$NOTIFY_TYPE" in
        telegram)
            cat <<'TG_EOF'
    # Telegram 通知
    local BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
    local CHAT_ID="${TELEGRAM_CHAT_ID:-}"
    if [ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
            -d "chat_id=${CHAT_ID}" \
            -d "text=${title}%0A${body}" \
            -d "parse_mode=HTML" >/dev/null 2>&1 || true
    fi
TG_EOF
            ;;
        slack)
            cat <<'SLACK_EOF'
    # Slack 通知
    local WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"${title}\n${body}\"}" >/dev/null 2>&1 || true
    fi
SLACK_EOF
            ;;
        email)
            cat <<'EMAIL_EOF'
    # Email 通知
    local EMAIL_TO="${BACKUP_EMAIL_TO:-}"
    if [ -n "$EMAIL_TO" ] && command -v mail &>/dev/null; then
        echo "$body" | mail -s "$title" "$EMAIL_TO" 2>/dev/null || true
    fi
EMAIL_EOF
            ;;
        *)
            cat <<'NONE_EOF'
    # 无通知配置
    :
NONE_EOF
            ;;
    esac

    cat <<'NOTIFY_END'
}
NOTIFY_END
}

# ============================================================
# 脚本尾部
# ============================================================
generate_footer() {
    cat <<'FOOTER_EOF'

# === 发送成功通知 ===
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
send_notification "✅ 备份成功: ${BACKUP_TYPE} - ${TARGET}" "文件: $(basename "$BACKUP_FILE"), 大小: ${BACKUP_SIZE}"

log "备份流程全部完成"
FOOTER_EOF
}

# ============================================================
# 主流程：组装并输出脚本
# ============================================================
main() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  备份脚本生成器${NC}"
    echo -e "${BLUE}  类型: $BACKUP_TYPE | 目标: $TARGET${NC}"
    echo -e "${BLUE}  目的地: $DESTINATION${NC}"
    echo -e "${BLUE}================================================${NC}"

    # 组装脚本内容
    local script_content
    script_content=$(
        generate_header
        generate_notification
        generate_backup_command
        generate_encryption
        generate_checksum
        generate_upload
        generate_retention
        generate_footer
    )

    if [ "$DRY_RUN" = true ]; then
        echo ""
        echo -e "${YELLOW}=== 预览生成的脚本 ===${NC}"
        echo "$script_content"
        echo -e "${YELLOW}=== 预览结束 ===${NC}"
        echo ""
        echo "确认无误后去掉 --dry-run 写入: $SCRIPT_PATH"
    else
        mkdir -p "$OUTPUT_DIR"
        echo "$script_content" > "$SCRIPT_PATH"
        chmod +x "$SCRIPT_PATH"
        echo -e "${GREEN}[✓]${NC} 脚本已生成: $SCRIPT_PATH"

        # 配置 cron（可选）
        echo ""
        echo -e "cron 定时任务配置:"
        echo -e "  计划: ${SCHEDULE}"
        echo -e "  命令: ${SCHEDULE} ${SCRIPT_PATH}"
        echo ""
        read -rp "是否添加到 crontab？(y/N): " add_cron
        if [ "$add_cron" = "y" ] || [ "$add_cron" = "Y" ]; then
            (crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$SCHEDULE $SCRIPT_PATH >> ${LOG_FILE} 2>&1") | crontab -
            echo -e "${GREEN}[✓]${NC} cron 任务已添加"
        fi
    fi
}

main "$@"
