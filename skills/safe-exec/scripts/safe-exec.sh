#!/bin/bash
# SafeExec v0.3.3 - 安全增强版本
# 移除监控组件，添加完整的 metadata 声明

SAFE_EXEC_DIR="$HOME/.openclaw/safe-exec"
AUDIT_LOG="$HOME/.openclaw/safe-exec-audit.log"
PENDING_DIR="$SAFE_EXEC_DIR/pending"
RULES_FILE="$HOME/.openclaw/safe-exec-rules.json"
REQUEST_TIMEOUT=300  # 5分钟超时

# 上下文感知配置
USER_CONTEXT="${SAFEXEC_CONTEXT:-}"

mkdir -p "$PENDING_DIR"

# 检查 SafeExec 是否启用
is_enabled() {
    if [[ ! -f "$RULES_FILE" ]]; then
        echo "true"
        return
    fi

    # 检查文件格式
    local first_char=$(head -c 1 "$RULES_FILE")

    if [[ "$first_char" == "[" ]]; then
        # 数组格式，默认启用
        echo "true"
        return
    fi

    # 对象格式，检查 enabled 字段
    local enabled
    enabled=$(jq -r 'if .enabled == true then "true" else "false" end' "$RULES_FILE" 2>/dev/null)

    # 如果解析失败，默认启用
    if [[ -z "$enabled" ]] || [[ "$enabled" == "null" ]]; then
        echo "true"
    else
        echo "$enabled"
    fi
}

# 设置启用状态
set_enabled() {
    local value="$1"

    if [[ ! -f "$RULES_FILE" ]]; then
        echo "{\"enabled\":$value,\"rules\":[]}" > "$RULES_FILE"
    else
        # 检查文件格式（数组 vs 对象）
        local first_char=$(head -c 1 "$RULES_FILE")

        if [[ "$first_char" == "[" ]]; then
            # 当前是数组格式，转换为对象格式
            local rules_array=$(cat "$RULES_FILE")
            echo "{\"enabled\":$value,\"rules\":$rules_array}" > "$RULES_FILE"
        else
            # 当前是对象格式，直接更新
            jq ".enabled = $value" "$RULES_FILE" > "$RULES_FILE.tmp" && mv "$RULES_FILE.tmp" "$RULES_FILE"
        fi
    fi

    local status
    if [[ "$value" == "true" ]]; then
        status="✅ 已启用"
    else
        status="❌ 已禁用"
    fi

    echo "$status"
    log_audit "toggle" "{\"enabled\":$value}"
}

# 获取自定义确认关键词
get_confirmation_keywords() {
    if [[ ! -f "$RULES_FILE" ]]; then
        # 默认关键词
        echo "我已明确风险|I understand the risk"
        return
    fi

    # 检查文件格式
    local first_char=$(head -c 1 "$RULES_FILE")

    if [[ "$first_char" == "[" ]]; then
        # 数组格式，返回默认关键词
        echo "我已明确风险|I understand the risk"
        return
    fi

    # 对象格式，尝试读取自定义关键词
    local keywords
    keywords=$(jq -r '.contextAware.confirmationKeywords // "我已明确风险|I understand the risk"' "$RULES_FILE" 2>/dev/null)

    if [[ -z "$keywords" ]] || [[ "$keywords" == "null" ]]; then
        echo "我已明确风险|I understand the risk"
    else
        echo "$keywords"
    fi
}

# 检测用户明确确认
detect_user_confirmation() {
    local context="$1"
    local keywords=$(get_confirmation_keywords)

    # 检查上下文中是否包含确认关键词
    if echo "$context" | grep -qE "$keywords"; then
        echo "confirmed"
        return 0
    fi

    echo "normal"
    return 1
}

# 显示当前状态
show_status() {
    local enabled
    enabled=$(is_enabled)
    
    echo "🛡️  SafeExec 状态"
    echo ""
    
    if [[ "$enabled" == "true" ]]; then
        echo "状态: ✅ **已启用**"
        echo ""
        echo "危险命令将被拦截并请求批准。"
    else
        echo "状态: ❌ **已禁用**"
        echo ""
        echo "⚠️  所有命令将直接执行，不受保护！"
        echo "建议仅在可信环境中禁用。"
    fi
    
    echo ""
    echo "切换状态:"
    echo "  启用:  safe-exec --enable"
    echo "  禁用:  safe-exec --disable"
}

# 清理过期的请求
cleanup_expired_requests() {
    local now=$(date +%s)
    local count=0
    
    for request_file in "$PENDING_DIR"/*.json; do
        if [[ -f "$request_file" ]]; then
            local timestamp=$(jq -r '.timestamp' "$request_file" 2>/dev/null)
            if [[ -n "$timestamp" ]]; then
                local age=$((now - timestamp))
                if [[ $age -gt $REQUEST_TIMEOUT ]]; then
                    local request_id=$(basename "$request_file" .json)
                    jq '.status = "expired"' "$request_file" > "$request_file.tmp" && mv "$request_file.tmp" "$request_file"
                    echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")\",\"event\":\"expired\",\"requestId\":\"$request_id\",\"age\":$age}" >> "$AUDIT_LOG"
                    rm -f "$request_file"
                    count=$((count + 1))
                fi
            fi
        fi
    done
    
    return $count
}

log_audit() {
    local event="$1"
    local data="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

    # 构造完整的 JSON 对象
    # 注意：data 参数应该已经是 JSON 格式，但不带外层花括号
    # 例如：data='"requestId":"xxx","command":"xxx"'
    # 我们需要移除 data 的外层花括号（如果有的话）
    local clean_data="${data#{}"  # 移除开头的 {
    clean_data="${clean_data%\}}"  # 移除结尾的 }

    echo "{\"timestamp\":\"$timestamp\",\"event\":\"$event\",$clean_data}" >> "$AUDIT_LOG"
}

assess_risk() {
    local cmd="$1"
    local risk="low"
    local reason=""
    
    if [[ "$cmd" == *":(){:|:&};:"* ]] || [[ "$cmd" == *":(){ :|:& };:"* ]]; then
        risk="critical"
        reason="Fork炸弹"
    elif echo "$cmd" | grep -qE 'rm[[:space:]]+-rf[[:space:]]+[\/~]'; then
        risk="critical"
        reason="删除根目录或家目录文件"
    elif echo "$cmd" | grep -qE 'dd[[:space:]]+if='; then
        risk="critical"
        reason="磁盘破坏命令"
    elif echo "$cmd" | grep -qE 'mkfs\.'; then
        risk="critical"
        reason="格式化文件系统"
    elif echo "$cmd" | grep -qE '>[[:space:]]*/dev/sd[a-z]'; then
        risk="critical"
        reason="直接写入磁盘"
    elif echo "$cmd" | grep -qE 'chmod[[:space:]]+777'; then
        risk="high"
        reason="设置文件为全局可写"
    elif echo "$cmd" | grep -qE '>[[:space:]]*/(etc|boot|sys|root)/'; then
        risk="high"
        reason="写入系统目录"
    elif echo "$cmd" | grep -qE '(curl|wget).*|[[:space:]]*(bash|sh|python)'; then
        risk="high"
        reason="管道下载到shell"
    elif echo "$cmd" | grep -qE 'sudo[[:space:]]+'; then
        risk="medium"
        reason="使用特权执行"
    elif echo "$cmd" | grep -qE 'iptables|firewall-cmd|ufw'; then
        risk="medium"
        reason="修改防火墙规则"
    fi
    
    echo "{\"risk\":\"$risk\",\"reason\":\"$reason\"}"
}

request_approval() {
    local command="$1"
    local risk="$2"
    local reason="$3"
    local request_id="req_$(date +%s)_$(shuf -i 1000-9999 -n 1)"
    
    echo "{\"id\":\"$request_id\",\"command\":$(echo "$command" | jq -Rs .),\"risk\":\"$risk\",\"reason\":\"$reason\",\"timestamp\":$(date +%s),\"status\":\"pending\"}" > "$PENDING_DIR/$request_id.json"
    
    log_audit "approval_requested" "{\"requestId\":\"$request_id\",\"command\":$(echo "$command" | jq -Rs .),\"risk\":\"$risk\",\"reason\":\"$reason\"}"
    
    cat <<EOF

🚨 **危险操作检测 - 命令已拦截**

**风险等级:** ${risk^^}
**命令:** \`$command\`
**原因:** $reason

**请求 ID:** \`$request_id\`

ℹ️  此命令需要用户批准才能执行。

**批准方法:**
1. 在终端运行: \`safe-exec-approve $request_id\`
2. 或者: \`safe-exec-list\` 查看所有待处理请求

**拒绝方法:**
 \`safe-exec-reject $request_id\`

⏰ 请求将在 5 分钟后过期

EOF
    return 0
}

main() {
    local command="$*"
    
    if [[ -z "$command" ]]; then
        echo "用法: safe-exec \"<命令>\""
        exit 1
    fi
    
    # 检查是否启用
    local enabled
    enabled=$(is_enabled)
    
    if [[ "$enabled" != "true" ]]; then
        # SafeExec 已禁用，直接执行命令
        log_audit "bypassed" "{\"command\":$(echo "$command" | jq -Rs .),\"reason\":\"SafeExec disabled\"}"
        eval "$command"
        exit $?
    fi
    
    # 自动清理过期请求
    cleanup_expired_requests
    
    local assessment
    assessment=$(assess_risk "$command")
    local risk
    local reason
    risk=$(echo "$assessment" | jq -r '.risk')
    reason=$(echo "$assessment" | jq -r '.reason')
    
    # ========== 上下文感知拦截 ==========
    # 检查用户是否提供了明确的确认关键词
    if [[ -n "$USER_CONTEXT" ]]; then
        local confirmation
        confirmation=$(detect_user_confirmation "$USER_CONTEXT")
        
        if [[ "$confirmation" == "confirmed" ]]; then
            # 用户已明确风险，根据原风险等级决定处理方式
            if [[ "$risk" == "critical" ]]; then
                # CRITICAL 风险：降级到 MEDIUM（仍需批准，但降低警告级别）
                echo "⚠️  检测到确认关键词，但风险等级为 CRITICAL"
                echo "ℹ️  命令降级到 MEDIUM，但仍需批准"
                risk="medium"
                log_audit "context_aware_downgrade" "{\"originalRisk\":\"critical\",\"newRisk\":\"medium\",\"reason\":\"用户确认关键词\",\"context\":$(echo "$USER_CONTEXT" | jq -Rs .)}"
            elif [[ "$risk" == "high" ]]; then
                # HIGH 风险：降级到 LOW（直接执行）
                echo "✅ 检测到确认关键词，风险等级从 HIGH 降级到 LOW"
                echo "⚡ 直接执行命令: $command"
                log_audit "context_aware_allowed" "{\"originalRisk\":\"high\",\"newRisk\":\"low\",\"reason\":\"用户确认关键词\",\"context\":$(echo "$USER_CONTEXT" | jq -Rs .)}"
                eval "$command"
                exit $?
            elif [[ "$risk" == "medium" ]]; then
                # MEDIUM 风险：降级到 LOW（直接执行）
                echo "✅ 检测到确认关键词，风险等级从 MEDIUM 降级到 LOW"
                echo "⚡ 直接执行命令: $command"
                log_audit "context_aware_allowed" "{\"originalRisk\":\"medium\",\"newRisk\":\"low\",\"reason\":\"用户确认关键词\",\"context\":$(echo "$USER_CONTEXT" | jq -Rs .)}"
                eval "$command"
                exit $?
            fi
        fi
    fi
    # ========== 上下文感知拦截结束 ==========
    
    if [[ "$risk" == "low" ]]; then
        log_audit "allowed" "{\"command\":$(echo "$command" | jq -Rs .),\"risk\":\"low\"}"
        eval "$command"
        exit $?
    fi
    
    request_approval "$command" "$risk" "$reason"
    exit 0
}

# 处理命令行参数
case "$1" in
    --enable)
        set_enabled "true"
        exit 0
        ;;
    --disable)
        set_enabled "false"
        exit 0
        ;;
    --status)
        show_status
        exit 0
        ;;
    --approve)
        request_file="$PENDING_DIR/$2.json"
        if [[ -f "$request_file" ]]; then
            command=$(jq -r '.command' "$request_file")
            echo "✅ 执行命令: $command"
            log_audit "executed" "{\"requestId\":\"$2\"}"
            eval "$command"
            exit_code=$?
            rm -f "$request_file"
            exit $exit_code
        fi
        echo "❌ 请求不存在: $2"
        exit 1
        ;;
    --reject)
        request_file="$PENDING_DIR/$2.json"
        if [[ -f "$request_file" ]]; then
            command=$(jq -r '.command' "$request_file")
            log_audit "rejected" "{\"requestId\":\"$2\"}"
            rm -f "$request_file"
            echo "❌ 请求已拒绝"
            exit 0
        fi
        echo "❌ 请求不存在: $2"
        exit 1
        ;;
    --list)
        echo "📋 **待处理的批准请求:**"
        echo ""
        count=0
        for f in "$PENDING_DIR"/*.json; do
            if [[ -f "$f" ]]; then
                count=$((count + 1))
                id=$(basename "$f" .json)
                cmd=$(jq -r '.command' "$f")
                rsk=$(jq -r '.risk' "$f")
                reason=$(jq -r '.reason' "$f")
                printf "📌 **请求 %d**\n" "$count"
                printf "   **ID:** \`%s\`\n" "$id"
                printf "   **风险:** %s\n" "${rsk^^}"
                printf "   **命令:** \`%s\`\n" "$cmd"
                printf "   **原因:** %s\n" "$reason"
                echo ""
                printf "   批准: \`safe-exec-approve %s\`\n" "$id"
                printf "   拒绝: \`safe-exec-reject %s\`\n" "$id"
                echo ""
            fi
        done
        
        if [[ $count -eq 0 ]]; then
            echo "✅ 没有待处理的请求"
        fi
        exit 0
        ;;
    --cleanup)
        cleanup_expired_requests
        echo "✅ 清理完成"
        exit 0
        ;;
esac

main "$@"
