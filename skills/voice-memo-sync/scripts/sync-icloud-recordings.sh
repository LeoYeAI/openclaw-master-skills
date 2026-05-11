#!/bin/bash
# ============================================
# Sync recordings from iCloud directories
# 从iCloud目录同步录音文件
# ============================================

set -e

CONFIG_FILE="${HOME}/.openclaw/workspace/config/voice-memo-sync.yaml"
OUTPUT_DIR="${HOME}/.openclaw/workspace/memory/voice-memos"
PROCESSED_LOG="${OUTPUT_DIR}/.processed_files.log"

# 默认iCloud路径
DEFAULT_ICLOUD_BASE="${HOME}/Library/Mobile Documents/com~apple~CloudDocs"

# 创建输出目录
mkdir -p "${OUTPUT_DIR}/icloud"
touch "${PROCESSED_LOG}"

echo "=== [$(date)] 开始同步iCloud录音 ==="

# 支持的文件格式
PATTERNS=("*.m4a" "*.mp3" "*.mp4" "*.wav" "*.mov")

# 扫描函数
scan_directory() {
    local dir="$1"
    local found=0
    
    if [ ! -d "$dir" ]; then
        echo "[跳过] 目录不存在: $dir"
        return
    fi
    
    echo "[扫描] $dir"
    
    for pattern in "${PATTERNS[@]}"; do
        while IFS= read -r -d '' file; do
            # 检查是否已处理
            file_hash=$(md5 -q "$file" 2>/dev/null || echo "$file")
            if grep -q "$file_hash" "$PROCESSED_LOG" 2>/dev/null; then
                continue
            fi
            
            echo "[发现] 新文件: $(basename "$file")"
            ((found++))
            
            # 复制到工作目录
            cp "$file" "${OUTPUT_DIR}/icloud/"
            
            # 记录已处理
            echo "$file_hash|$file|$(date)" >> "$PROCESSED_LOG"
            
        done < <(find "$dir" -maxdepth 2 -name "$pattern" -type f -print0 2>/dev/null)
    done
    
    echo "[完成] 发现 $found 个新文件"
}

# 扫描默认路径
scan_directory "${DEFAULT_ICLOUD_BASE}/Recordings"
scan_directory "${DEFAULT_ICLOUD_BASE}/会议录音"
scan_directory "${DEFAULT_ICLOUD_BASE}/Downloads"

# 如果配置文件存在，扫描自定义路径
if [ -f "$CONFIG_FILE" ]; then
    # 简单的yaml解析（仅支持基本格式）
    custom_paths=$(grep -A 20 "icloud:" "$CONFIG_FILE" 2>/dev/null | grep "- \"" | sed 's/.*"\(.*\)".*/\1/' | sed "s|~|$HOME|g")
    
    while IFS= read -r path; do
        [ -n "$path" ] && scan_directory "$path"
    done <<< "$custom_paths"
fi

echo "=== 同步完成 ==="
echo "新文件保存在: ${OUTPUT_DIR}/icloud/"
