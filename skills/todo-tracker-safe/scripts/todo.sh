#!/bin/bash
# TODO Tracker Script - Safe Version
# Usage: todo.sh <command> [args]
#   add <priority> <item>  - Add item (priority: high|medium|low)
#   done <pattern>         - Mark matching item as done
#   remove <pattern>       - Remove matching item
#   list [priority]        - List items, optionally by priority
#   summary                - Quick summary for heartbeat

set -euo pipefail

# 配置
TODO_FILE="${TODO_FILE:-${HOME}/.openclaw/workspace/TODO.md}"
DATE=$(date +%Y-%m-%d)

# 安全日志函数
log_info() {
    echo "[INFO] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
}

# 输入验证：只允许字母、数字、中文、空格和常见标点
sanitize_input() {
    local input="$1"
    # 移除危险字符：$ ` \ | ; & < > ( ) { } [ ] ! # ~
    local sanitized
    sanitized=$(printf '%s' "$input" | tr -d '$`\\|;&<>(){}[]!#~')
    # 限制长度
    printf '%s' "${sanitized:0:200}"
}

# 验证优先级
validate_priority() {
    local priority="$1"
    case "$priority" in
        high|medium|low) return 0 ;;
        *) return 1 ;;
    esac
}

# 确保 TODO.md 存在并初始化
init_todo() {
    local todo_dir
    todo_dir=$(dirname "$TODO_FILE")
    
    # 检查目录是否存在且可写
    if [[ ! -d "$todo_dir" ]]; then
        log_error "目录不存在：$todo_dir"
        return 1
    fi
    
    if [[ ! -w "$todo_dir" ]]; then
        log_error "目录不可写：$todo_dir"
        return 1
    fi
    
    # 创建文件（如果不存在）
    if [[ ! -f "$TODO_FILE" ]]; then
        cat > "$TODO_FILE" << EOF
# TODO - 任务追踪

*最后更新：${DATE}*

## 🔴 高优先级

## 🟡 中优先级

## 🟢 低优先级

## ✅ 已完成

---

## 备注

EOF
        log_info "已创建 TODO 文件：$TODO_FILE"
    fi
    
    # 检查文件权限（不允许其他人可写）
    local perms
    perms=$(stat -c %a "$TODO_FILE" 2>/dev/null || stat -f %Lp "$TODO_FILE" 2>/dev/null || echo "644")
    local other_perm="${perms: -1}"
    if [[ "$other_perm" =~ [2367] ]]; then
        log_error "TODO 文件权限过于宽松：$perms（其他人可写）"
        return 1
    fi
}

# 更新日期戳
update_date() {
    if [[ -f "$TODO_FILE" ]]; then
        local tmp_file="${TODO_FILE}.tmp.$$"
        sed "s/^\*最后更新：.*\*/*最后更新：${DATE}*/" "$TODO_FILE" > "$tmp_file" && mv "$tmp_file" "$TODO_FILE"
    fi
}

# 添加任务
add_item() {
    local priority="$1"
    local item="$2"
    
    # 验证输入
    if ! validate_priority "$priority"; then
        log_error "无效的优先级：$priority（应为 high|medium|low）"
        return 1
    fi
    
    if [[ -z "$item" ]]; then
        log_error "任务内容不能为空"
        return 1
    fi
    
    # 清理输入
    item=$(sanitize_input "$item")
    
    init_todo || return 1
    
    # 确定目标分区
    local section=""
    case "$priority" in
        high)   section="## 🔴 高优先级" ;;
        medium) section="## 🟡 中优先级" ;;
        low)    section="## 🟢 低优先级" ;;
    esac
    
    local entry="- [ ] ${item} (添加：${DATE})"
    
    # 使用 awk 安全插入（不使用变量插值）
    local tmp_file="${TODO_FILE}.tmp.$$"
    awk -v section="$section" -v entry="$entry" '
        BEGIN { inserted = 0 }
        $0 == section { 
            print
            print entry
            inserted = 1
            next
        }
        { print }
        END { if (!inserted) print "Warning: section not found" > "/dev/stderr" }
    ' "$TODO_FILE" > "$tmp_file" && mv "$tmp_file" "$TODO_FILE"
    
    update_date
    echo "✅ 已添加到${priority}优先级：${item}"
}

# 标记任务为完成
mark_done() {
    local pattern="$1"
    
    if [[ -z "$pattern" ]]; then
        log_error "请提供任务关键词"
        return 1
    fi
    
    # 清理输入
    pattern=$(sanitize_input "$pattern")
    
    init_todo || return 1
    
    # 使用固定字符串匹配（非正则）
    local found_line
    found_line=$(grep -F -- "- [ ]" "$TODO_FILE" | grep -F -- "$pattern" | head -1 || true)
    
    if [[ -n "$found_line" ]]; then
        # 提取任务内容
        local item
        item=$(echo "$found_line" | sed 's/- \[ \] //' | sed 's/ (添加：.*//' | sed 's/ (done:.*//')
        
        # 从原位置删除（使用固定字符串）
        local tmp_file="${TODO_FILE}.tmp.$$"
        grep -vF -- "$found_line" "$TODO_FILE" > "$tmp_file" && mv "$tmp_file" "$TODO_FILE"
        
        # 添加到已完成分区
        local done_entry="- [x] ${item} (完成：${DATE})"
        tmp_file="${TODO_FILE}.tmp.$$"
        awk -v section="## ✅ 已完成" -v entry="$done_entry" '
            $0 == section { print; print entry; next }
            { print }
        ' "$TODO_FILE" > "$tmp_file" && mv "$tmp_file" "$TODO_FILE"
        
        update_date
        echo "✅ 已完成：${item}"
    else
        log_error "未找到匹配的任务：${pattern}"
        return 1
    fi
}

# 删除任务
remove_item() {
    local pattern="$1"
    
    if [[ -z "$pattern" ]]; then
        log_error "请提供任务关键词"
        return 1
    fi
    
    # 清理输入
    pattern=$(sanitize_input "$pattern")
    
    init_todo || return 1
    
    local found_line
    found_line=$(grep -F -- "$pattern" "$TODO_FILE" | grep -E "^- \[.\]" | head -1 || true)
    
    if [[ -n "$found_line" ]]; then
        local tmp_file="${TODO_FILE}.tmp.$$"
        grep -vF -- "$found_line" "$TODO_FILE" > "$tmp_file" && mv "$tmp_file" "$TODO_FILE"
        update_date
        echo "🗑️ 已删除：${pattern}"
    else
        log_error "未找到匹配的任务：${pattern}"
        return 1
    fi
}

# 列出任务
list_items() {
    local priority="${1:-all}"
    
    init_todo || return 1
    
    case "$priority" in
        high)
            awk '/^## 🔴 高优先级/,/^## 🟡/' "$TODO_FILE"
            ;;
        medium)
            awk '/^## 🟡 中优先级/,/^## 🟢/' "$TODO_FILE"
            ;;
        low)
            awk '/^## 🟢 低优先级/,/^## ✅/' "$TODO_FILE"
            ;;
        done)
            awk '/^## ✅ 已完成/,/^---/' "$TODO_FILE"
            ;;
        all|*)
            cat "$TODO_FILE"
            ;;
    esac
}

# 摘要（用于 heartbeat）
summary() {
    init_todo || return 1
    
    # 统计各分区数量
    local high_count med_count low_count total
    high_count=$(awk '/^## 🔴 高优先级/,/^## 🟡/' "$TODO_FILE" | grep -c "^- \[ \]" || echo 0)
    med_count=$(awk '/^## 🟡 中优先级/,/^## 🟢/' "$TODO_FILE" | grep -c "^- \[ \]" || echo 0)
    low_count=$(awk '/^## 🟢 低优先级/,/^## ✅/' "$TODO_FILE" | grep -c "^- \[ \]" || echo 0)
    total=$((high_count + med_count + low_count))
    
    # 检查过期任务（>7 天）
    local stale=0
    local week_ago
    week_ago=$(date -d "7 days ago" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d 2>/dev/null || echo "")
    
    if [[ -n "$week_ago" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ 添加：\ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
                local added="${BASH_REMATCH[1]}"
                if [[ "$added" < "$week_ago" ]]; then
                    ((stale++)) || true
                fi
            fi
        done < <(grep "^- \[ \]" "$TODO_FILE" || true)
    fi
    
    echo "📋 TODO: ${total}项 (${high_count}高，${med_count}中，${low_count}低)"
    if [[ $stale -gt 0 ]]; then
        echo "⚠️ ${stale}项已过期（>7 天）"
    fi
    if [[ $high_count -gt 0 ]]; then
        echo "🔴 高优先级任务:"
        awk '/^## 🔴 高优先级/,/^## 🟡/' "$TODO_FILE" | grep "^- \[ \]" | head -3 | sed 's/- \[ \] /  • /' | sed 's/ (添加：.*//' | sed 's/\*\*//g'
    fi
}

# 显示帮助
show_help() {
    cat << EOF
TODO Tracker - 安全版本

用法：todo.sh <命令> [参数]

命令:
  add <优先级> <任务>    添加任务 (优先级：high|medium|low)
  done <关键词>         标记任务为完成
  remove <关键词>       删除任务
  list [优先级]         列出任务 (high|medium|low|done|all)
  summary              快速摘要（用于 heartbeat）
  help                 显示此帮助信息

示例:
  todo.sh add high "完成项目报告"
  todo.sh done "项目报告"
  todo.sh list high
  todo.sh summary

EOF
}

# 主入口
main() {
    local cmd="${1:-help}"
    
    case "$cmd" in
        add)
            add_item "${2:-}" "${3:-}"
            ;;
        done)
            mark_done "${2:-}"
            ;;
        remove)
            remove_item "${2:-}"
            ;;
        list)
            list_items "${2:-all}"
            ;;
        summary)
            summary
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令：$cmd"
            show_help
            return 1
            ;;
    esac
}

main "$@"
