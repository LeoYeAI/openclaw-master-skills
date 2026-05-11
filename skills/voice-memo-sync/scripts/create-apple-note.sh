#!/bin/bash
# ============================================
# Create Apple Note via osascript
# 创建Apple备忘录（支持HTML格式内容）
#
# 用法: ./create-apple-note.sh "标题" "HTML内容" ["文件夹名"]
# ============================================

set -e

TITLE="$1"
BODY="$2"
FOLDER="${3:-语音备忘录}"

if [ -z "$TITLE" ] || [ -z "$BODY" ]; then
    echo "用法: ./create-apple-note.sh \"标题\" \"内容\" [\"文件夹名\"]"
    exit 1
fi

# 转义双引号和特殊字符
TITLE_ESC=$(echo "$TITLE" | sed 's/"/\\"/g')
BODY_ESC=$(echo "$BODY" | sed 's/"/\\"/g')

osascript << EOF
tell application "Notes"
    tell account "iCloud"
        -- 检查文件夹是否存在，不存在则创建
        if not (exists folder "$FOLDER") then
            make new folder with properties {name:"$FOLDER"}
        end if
        -- 创建笔记
        make new note at folder "$FOLDER" with properties {name:"$TITLE_ESC", body:"$BODY_ESC"}
    end tell
end tell
EOF

echo "[OK] 备忘录已创建: $TITLE -> $FOLDER"
