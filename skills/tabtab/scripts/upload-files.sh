#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 批量上传多个文件到 TabTab
#
# 用法：
#   TABTAB_FILES="file1.pdf file2.png" bash upload-files.sh
#   TABTAB_FILES="data/*.xlsx" bash upload-files.sh
#
# 环境变量：
#   TABTAB_API_KEY   必填  sk-… API Key
#   TABTAB_BASE_URL  可选  默认 https://tabtabai.com
#   TABTAB_FILES      必填  文件路径列表（空格分隔）
#
# 输出格式（JSON）：
#   {"files": [{"file_id": "...", "file_name": "...", "content_type": "..."}, ...]}
#
# 文件限制：
#   - 单文件大小：50MB
#   - 每个任务最多 20 个文件
#   - 支持类型：PDF, Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx),
#                Text (.txt, .md),
#                图片 (.jpg, .jpeg, .png, .gif, .webp, .bmp, .svg, .tiff, .tif, .ico),
#                压缩包 (.zip, .rar, .7z, .tar, .gz)
#   - 注意：MIME 类型验证是宽松的，主要基于文件扩展名验证

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY 环境变量}"
FILES="${TABTAB_FILES:?请设置 TABTAB_FILES 环境变量}"

# 允许的文件扩展名
ALLOWED_EXTS="pdf doc docx xls xlsx ppt pptx txt md jpg jpeg png gif webp bmp svg tiff tif ico zip rar 7z tar gz"

# 将文件列表转换为数组
read -ra FILE_ARRAY <<< "$FILES"

# 检查文件数量
MAX_FILES=20
if [ "${#FILE_ARRAY[@]}" -gt "$MAX_FILES" ]; then
    echo "错误: 最多支持 $MAX_FILES 个文件，当前提供 ${#FILE_ARRAY[@]} 个" >&2
    exit 1
fi

# 检查所有文件是否存在、扩展名和大小
MAX_SIZE=$((50 * 1024 * 1024))
for file in "${FILE_ARRAY[@]}"; do
    if [ ! -f "$file" ]; then
        echo "错误: 文件不存在 $file" >&2
        exit 1
    fi

    # 检查文件扩展名
    FILENAME=$(basename "$file")
    EXT="${FILENAME##*.}"
    if [[ ! " $ALLOWED_EXTS " =~ " ${EXT,,} " ]]; then
        echo "错误: 不支持的文件类型 .${EXT} ($file)" >&2
        exit 1
    fi

    FILE_SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    if [ "$FILE_SIZE" -gt "$MAX_SIZE" ]; then
        echo "错误: 文件 $file 大小超过 50MB 限制" >&2
        exit 1
    fi
done

# 构建 curl 的 -F 参数（使用数组避免 eval 和 shell 注入风险）
CURL_ARGS=()
for file in "${FILE_ARRAY[@]}"; do
    CURL_ARGS+=(-F "files=@${file}")
done

# 批量上传文件
RESP=$(curl -sf -X POST "${BASE}/open/apis/v1/tasks/upload-files" \
    -H "Authorization: Bearer ${KEY}" \
    "${CURL_ARGS[@]}")

# 输出完整响应
echo "$RESP"
