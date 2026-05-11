#!/bin/bash
# safe-exec-reject - 拒绝待执行的命令

REQUEST_ID="$1"
SAFE_EXEC_DIR="$HOME/.openclaw/safe-exec"
PENDING_DIR="$SAFE_EXEC_DIR/pending"

if [[ -z "$REQUEST_ID" ]]; then
    echo "用法: safe-exec-reject <request_id>"
    echo ""
    echo "查看待处理的请求:"
    echo "  ls ~/.openclaw/safe-exec/pending/"
    exit 1
fi

REQUEST_FILE="$PENDING_DIR/$REQUEST_ID.json"

if [[ ! -f "$REQUEST_FILE" ]]; then
    echo "❌ 请求 $REQUEST_ID 不存在"
    exit 1
fi

# 读取请求信息
COMMAND=$(jq -r '.command' "$REQUEST_FILE")

# 标记为已拒绝
jq '.status = "rejected"' "$REQUEST_FILE" > "$REQUEST_FILE.tmp" && mv "$REQUEST_FILE.tmp" "$REQUEST_FILE"

echo "❌ 命令已拒绝: $COMMAND"

# 记录到审计日志
AUDIT_LOG="$HOME/.openclaw/safe-exec-audit.log"
echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")\",\"event\":\"rejected\",\"requestId\":\"$REQUEST_ID\",\"command\":\"$(echo "$COMMAND" | jq -Rs .)\"}" >> "$AUDIT_LOG"

# 清理已处理的请求
rm "$REQUEST_FILE"

echo "请求已拒绝并清理"
