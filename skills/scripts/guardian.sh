#!/bin/bash
# guardian.sh - OpenClaw Guardian 守护进程
# 功能：监控 Gateway → doctor --fix → git 回滚 → Discord 通知
# 用法：chmod +x guardian.sh && nohup ./guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &

WORKSPACE="${GUARDIAN_WORKSPACE:-$HOME/.openclaw/workspace}"
LOG_FILE="${GUARDIAN_LOG:-/tmp/openclaw-guardian.log}"
CHECK_INTERVAL="${GUARDIAN_CHECK_INTERVAL:-30}"      # 检测间隔(秒)
MAX_REPAIR_ATTEMPTS="${GUARDIAN_MAX_REPAIR:-3}"      # 连续修复最大次数
COOLDOWN_PERIOD="${GUARDIAN_COOLDOWN:-300}"          # 失败后冷却期(秒)
OPENCLAW_CMD="${OPENCLAW_CMD:-openclaw}"
DISCORD_WEBHOOK="${DISCORD_WEBHOOK_URL:-}"           # 可选，设置环境变量启用通知

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 发送 Discord 通知（可选）
notify() {
    local msg="$1"
    if [ -n "$DISCORD_WEBHOOK" ]; then
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"content\": \"🚨 **OpenClaw Guardian**: $msg\"}" \
            >/dev/null 2>&1 || true
    fi
    log "[NOTIFY] $msg"
}

# 检查 Gateway 是否运行
is_gateway_running() {
    if pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 获取上一个稳定版本的 commit（排除自动提交）
get_stable_commit() {
    git -C "$WORKSPACE" log --all --oneline -50 2>/dev/null | \
        grep -v -E "rollback|daily-backup|auto-backup|guardian-auto" | \
        sed -n '2p' | awk '{print $1}'
}

# 尝试 doctor --fix 修复
try_doctor_fix() {
    log "尝试 doctor --fix 修复..."
    $OPENCLAW_CMD doctor --fix >> "$LOG_FILE" 2>&1
    sleep 10
    if is_gateway_running; then
        log "doctor --fix 修复成功，Gateway 已恢复"
        return 0
    fi
    return 1
}

# 执行 git 回滚
do_rollback() {
    log "开始执行 git 回滚..."
    local CURRENT_COMMIT
    CURRENT_COMMIT=$(git -C "$WORKSPACE" rev-parse HEAD 2>/dev/null)
    local STABLE_COMMIT
    STABLE_COMMIT=$(get_stable_commit)

    if [ -z "$STABLE_COMMIT" ]; then
        log "❌ 无法找到稳定版本，跳过回滚"
        return 1
    fi

    log "回滚目标: $STABLE_COMMIT (当前: $CURRENT_COMMIT)"
    git -C "$WORKSPACE" reset --hard "$STABLE_COMMIT" >> "$LOG_FILE" 2>&1
    git -C "$WORKSPACE" commit --allow-empty \
        -m "rollback: guardian auto rollback from $CURRENT_COMMIT to $STABLE_COMMIT at $(date '+%Y-%m-%d %H:%M:%S')" \
        >> "$LOG_FILE" 2>&1

    # 重启 Gateway
    pkill -f "openclaw-gateway" 2>/dev/null || true
    sleep 3
    nohup $OPENCLAW_CMD gateway >> "$LOG_FILE" 2>&1 &
    sleep 15

    if is_gateway_running; then
        log "✅ 回滚成功，Gateway 已恢复"
        notify "回滚成功！从 $CURRENT_COMMIT 回滚到 $STABLE_COMMIT"
        return 0
    else
        log "❌ 回滚后 Gateway 仍未启动"
        return 1
    fi
}

# 每日自动备份（创建 git 快照）
daily_backup() {
    local today
    today=$(date '+%Y-%m-%d')
    local last_backup_file="/tmp/guardian-last-backup"
    local last_backup=""
    [ -f "$last_backup_file" ] && last_backup=$(cat "$last_backup_file")

    if [ "$last_backup" != "$today" ]; then
        cd "$WORKSPACE" && git add -A && \
        git commit -m "daily-backup: auto snapshot $today" >> "$LOG_FILE" 2>&1 || true
        echo "$today" > "$last_backup_file"
        log "📦 每日备份完成: $today"
    fi
}

# 主修复流程
repair_gateway() {
    local attempt=0
    notify "Gateway 异常，开始修复流程..."

    # 第一步：doctor --fix
    while [ $attempt -lt $MAX_REPAIR_ATTEMPTS ]; do
        attempt=$((attempt + 1))
        log "修复尝试 $attempt/$MAX_REPAIR_ATTEMPTS"
        if try_doctor_fix; then
            notify "✅ doctor --fix 修复成功（第 $attempt 次尝试）"
            return 0
        fi
        sleep 10
    done

    # 第二步：git 回滚
    log "doctor --fix 失败，尝试 git 回滚..."
    notify "doctor --fix 失败，尝试 git 回滚..."
    if do_rollback; then
        return 0
    fi

    # 最终：冷却
    notify "❌ 所有修复手段均失败，冷却 ${COOLDOWN_PERIOD}s 后继续监控"
    log "进入冷却期 ${COOLDOWN_PERIOD}s"
    sleep "$COOLDOWN_PERIOD"
}

# ===== 主循环 =====
log "🚀 Guardian 守护进程启动 (check=${CHECK_INTERVAL}s, max_repair=${MAX_REPAIR_ATTEMPTS})"
notify "Guardian 守护进程已启动"

while true; do
    daily_backup

    if ! is_gateway_running; then
        repair_gateway
    fi

    sleep "$CHECK_INTERVAL"
done
