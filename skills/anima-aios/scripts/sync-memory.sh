#!/bin/bash
#
# Anima 记忆同步脚本（第三层：定时同步）
#
# 用法:
#   ./sync-memory.sh [Agent 名称]
#
# 如果不指定 Agent，同步所有 Agent
#

WORKSPACE="/root/.openclaw/workspace-shuheng/memory"
PORTRAIT_BASE="/home/画像"

echo "=========================================="
echo "  Anima 记忆同步（定时任务）"
echo "=========================================="
echo ""

# 同步指定 Agent 或所有 Agent
if [ -n "$1" ]; then
    AGENTS="$1"
else
    # 获取所有 Agent 目录
    AGENTS=$(ls -d $PORTRAIT_BASE/*/ 2>/dev/null | xargs -n1 basename | grep -v "^\.")
fi

total_synced=0

for agent in $AGENTS; do
    portrait_mem="$PORTRAIT_BASE/$agent/memory"
    
    # 确保画像记忆目录存在
    mkdir -p "$portrait_mem"
    
    # 同步所有记忆文件
    for mem_file in $WORKSPACE/*.md; do
        if [ -f "$mem_file" ]; then
            filename=$(basename "$mem_file")
            dest="$portrait_mem/$filename"
            
            # 只复制不存在的文件（-n 参数）
            if [ ! -f "$dest" ]; then
                cp "$mem_file" "$dest"
                echo "✅ $agent: 同步 $filename"
                total_synced=$((total_synced + 1))
            fi
        fi
    done
done

echo ""
echo "=========================================="
echo "  同步完成"
echo "=========================================="
echo "  总计：$total_synced 个文件"
echo "=========================================="
