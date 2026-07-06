#!/bin/bash
# logger.sh - CloudCC API 调用日志记录工具

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"
LOG_FILE="$LOG_DIR/api-calls.log"
MAX_LOG_DAYS=3

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志级别
LOG_LEVEL_INFO="INFO"
LOG_LEVEL_WARN="WARN"
LOG_LEVEL_ERROR="ERROR"
LOG_LEVEL_DEBUG="DEBUG"

# 记录日志函数
# 用法：log_message "INFO" "service_name" "message" ["extra_data"]
log_message() {
    local level="$1"
    local service="$2"
    local message="$3"
    local extra="${4:-}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"service\":\"$service\",\"message\":\"$message\"$extra}"
    
    echo "$log_entry" >> "$LOG_FILE"
    
    # 控制台输出（可选）
    if [ "$LOG_VERBOSE" = "true" ]; then
        echo "[$timestamp] [$level] [$service] $message"
    fi
}

# 记录 API 请求日志
# 用法：log_api_request "serviceName" "objectApiName" "response_code" "duration_ms" ["extra_fields"]
log_api_request() {
    local service_name="$1"
    local object_api="$2"
    local response_code="$3"
    local duration_ms="$4"
    local extra="${5:-}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local extra_json=""
    
    if [ -n "$extra" ]; then
        extra_json=",\"extra\":$extra"
    fi
    
    local log_entry="{\"timestamp\":\"$timestamp\",\"type\":\"API_REQUEST\",\"service\":\"$service_name\",\"objectApi\":\"$object_api\",\"responseCode\":\"$response_code\",\"durationMs\":\"$duration_ms\"$extra_json}"
    
    echo "$log_entry" >> "$LOG_FILE"
}

# 记录认证事件
# 用法：log_auth_event "event_type" "result" ["message"]
log_auth_event() {
    local event_type="$1"  # TOKEN_REQUEST, TOKEN_REFRESH, TOKEN_EXPIRED
    local result="$2"      # SUCCESS, FAILED
    local message="${3:-}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message_json=""
    
    if [ -n "$message" ]; then
        message_json=",\"message\":\"$message\""
    fi
    
    local log_entry="{\"timestamp\":\"$timestamp\",\"type\":\"AUTH_EVENT\",\"event\":\"$event_type\",\"result\":\"$result\"$message_json}"
    
    echo "$log_entry" >> "$LOG_FILE"
}

# 清理旧日志（保留最近 N 天）
cleanup_old_logs() {
    local days="${1:-$MAX_LOG_DAYS}"
    
    if [ -f "$LOG_FILE" ]; then
        # 创建临时文件保存最近的日志
        local temp_file="$LOG_FILE.tmp"
        local cutoff_date=$(date -d "$days days ago" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v-${days}d '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
        
        if [ -n "$cutoff_date" ]; then
            # 过滤保留最近的日志
            while IFS= read -r line; do
                log_timestamp=$(echo "$line" | jq -r '.timestamp' 2>/dev/null)
                if [ -n "$log_timestamp" ] && [[ "$log_timestamp" > "$cutoff_date" ]]; then
                    echo "$line" >> "$temp_file"
                fi
            done < "$LOG_FILE"
            
            if [ -f "$temp_file" ]; then
                mv "$temp_file" "$LOG_FILE"
                echo "✅ 已清理 $days 天前的日志"
            else
                # 如果所有日志都过期了，清空文件
                > "$LOG_FILE"
                echo "✅ 所有日志已过期，已清空日志文件"
            fi
        fi
    fi
}

# 查看最近的日志
# 用法：view_logs [count] [level]
view_logs() {
    local count="${1:-20}"
    local level="${2:-}"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 日志文件不存在：$LOG_FILE"
        return 1
    fi
    
    echo "📋 最近 $count 条日志"
    echo "=================="
    echo ""
    
    if [ -n "$level" ]; then
        tail -n "$count" "$LOG_FILE" | jq --arg lvl "$level" 'select(.level == $lvl or .type == $lvl)'
    else
        tail -n "$count" "$LOG_FILE" | jq .
    fi
}

# 统计日志
# 用法：show_stats [days]
show_stats() {
    local days="${1:-$MAX_LOG_DAYS}"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 日志文件不存在：$LOG_FILE"
        return 1
    fi
    
    local cutoff_date=$(date -d "$days days ago" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v-${days}d '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
    
    echo "📊 最近 $days 天 API 调用统计"
    echo "=========================="
    echo ""
    
    # 按服务名统计
    echo "按服务名统计:"
    tail -n 1000 "$LOG_FILE" | jq -r 'select(.type == "API_REQUEST") | .service' | sort | uniq -c | sort -rn | head -20
    
    echo ""
    echo "按响应码统计:"
    tail -n 1000 "$LOG_FILE" | jq -r 'select(.type == "API_REQUEST") | .responseCode' | sort | uniq -c | sort -rn
    
    echo ""
    echo "总调用次数: $(tail -n 1000 "$LOG_FILE" | jq -r 'select(.type == "API_REQUEST")' | wc -l)"
}

# 搜索日志
# 用法：search_logs "keyword" [count]
search_logs() {
    local keyword="$1"
    local count="${2:-50}"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 日志文件不存在：$LOG_FILE"
        return 1
    fi
    
    echo "🔍 搜索关键词：'$keyword'"
    echo ""
    
    tail -n 1000 "$LOG_FILE" | jq --arg kw "$keyword" 'select(.service | contains($kw)) or select(.objectApi | contains($kw)) or select(.message | contains($kw))' | head -n "$count"
}

# 导出日志为 JSON
# 用法：export_logs [output_file]
export_logs() {
    local output="${1:-$LOG_DIR/export-$(date +%Y%m%d-%H%M%S).json}"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 日志文件不存在：$LOG_FILE"
        return 1
    fi
    
    # 转换为 JSON 数组
    echo "[" > "$output"
    local first=true
    while IFS= read -r line; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$output"
        fi
        echo "$line" >> "$output"
    done < "$LOG_FILE"
    echo "]" >> "$output"
    
    echo "✅ 日志已导出到：$output"
}

# 显示帮助
show_help() {
    echo "CloudCC API 日志工具"
    echo ""
    echo "用法：$0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  view [count] [level]     查看最近的日志"
    echo "  stats [days]             显示统计信息"
    echo "  search <keyword> [count] 搜索日志"
    echo "  export [output_file]     导出日志为 JSON"
    echo "  cleanup [days]           清理旧日志"
    echo "  help                     显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 view 50               查看最近 50 条日志"
    echo "  $0 stats 7               显示最近 7 天统计"
    echo "  $0 search productuplist  搜索包含 productuplist 的日志"
    echo "  $0 cleanup 3             清理 3 天前的日志"
}

# 内部函数调用（供其他脚本使用）
case "${1:-}" in
    log_api_request)
        log_api_request "${2:-}" "${3:-}" "${4:-}" "${5:-}"
        exit 0
        ;;
    log_message)
        log_message "${2:-}" "${3:-}" "${4:-}" "${5:-}"
        exit 0
        ;;
    log_auth_event)
        log_auth_event "${2:-}" "${3:-}" "${4:-}"
        exit 0
        ;;
esac

# 主程序
case "${1:-help}" in
    view)
        view_logs "${2:-20}" "${3:-}"
        ;;
    stats)
        show_stats "${2:-$MAX_LOG_DAYS}"
        ;;
    search)
        search_logs "${2:-}" "${3:-50}"
        ;;
    export)
        export_logs "${2:-}"
        ;;
    cleanup)
        cleanup_old_logs "${2:-$MAX_LOG_DAYS}"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ 未知命令：$1"
        show_help
        exit 1
        ;;
esac
