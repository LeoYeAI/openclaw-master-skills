#!/bin/bash
# extract_metadata.sh - 提取 PDF 元数据用于去重
# 用法：./extract_metadata.sh <pdf_path> [output_json_path]

set -e

PDF_PATH="$1"
OUTPUT="${2:-/dev/stdout}"

if [ ! -f "$PDF_PATH" ]; then
    echo "Error: PDF file not found: $PDF_PATH" >&2
    exit 1
fi

# 检查依赖
for cmd in pdfinfo pdftotext jq; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd not found. Please install poppler-utils and jq." >&2
        exit 1
    fi
done

# 临时文件
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

TXT_FILE="$TEMP_DIR/metadata.txt"

# 1. 提取 PDF 内置元数据
PDFINFO=$(pdfinfo "$PDF_PATH" 2>/dev/null || echo "")

# 从 pdfinfo 提取字段
TITLE=$(echo "$PDFINFO" | grep -i "^Title:" | sed 's/^Title:[[:space:]]*//' | head -1)
AUTHOR=$(echo "$PDFINFO" | grep -i "^Author:" | sed 's/^Author:[[:space:]]*//' | head -1)
CREATION_DATE=$(echo "$PDFINFO" | grep -i "^CreationDate:" | sed 's/^CreationDate:[[:space:]]*//' | head -1)
PAGES=$(echo "$PDFINFO" | grep -i "^Pages:" | sed 's/^Pages:[[:space:]]*//' | head -1)

# 2. 从 PDF 内容中提取 DOI（前 10 页足够）
pdftotext -l 10 "$PDF_PATH" "$TXT_FILE" 2>/dev/null || true
# DOI 格式：10.xxxx/xxxxx，可能包含连字符、点号等
DOI=$(grep -oE "10\.[0-9]{4,}/[a-zA-Z0-9._-]+" "$TXT_FILE" 2>/dev/null | head -1 || echo "")

# 3. 如果元数据中没有标题，从内容中提取（第一行非空文本）
if [ -z "$TITLE" ]; then
    TITLE=$(grep -v '^$' "$TXT_FILE" | head -1 | cut -c1-200)
fi

# 4. 清理标题（去除换行和多余空格）
TITLE=$(echo "$TITLE" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# 5. 提取第一作者（如果有多个作者）
FIRST_AUTHOR=""
if [ -n "$AUTHOR" ]; then
    FIRST_AUTHOR=$(echo "$AUTHOR" | sed 's/;.*$//' | sed 's/,.*$//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
fi

# 6. 提取发表年份
YEAR=""
if [ -n "$CREATION_DATE" ]; then
    YEAR=$(echo "$CREATION_DATE" | grep -oE '[0-9]{4}' | head -1)
fi

# 7. 生成 paper_id（唯一标识符）
if [ -n "$DOI" ]; then
    # 有 DOI：用 DOI 作为 ID（替换 / 为 - 以适配文件系统）
    PAPER_ID=$(echo "$DOI" | sed 's/\//_/g')
    ID_TYPE="doi"
else
    # 无 DOI：用标题哈希 + 第一作者 + 年份
    FINGERPRINT="${TITLE}|${FIRST_AUTHOR}|${YEAR}"
    HASH=$(echo -n "$FINGERPRINT" | md5sum | cut -c1-12)
    PAPER_ID="hash_${HASH}"
    ID_TYPE="fingerprint"
fi

# 8. 输出 JSON
cat > "$OUTPUT" << EOF
{
  "paper_id": "$PAPER_ID",
  "id_type": "$ID_TYPE",
  "doi": "$DOI",
  "title": "$TITLE",
  "author": "$AUTHOR",
  "first_author": "$FIRST_AUTHOR",
  "year": "$YEAR",
  "pages": "$PAGES",
  "pdf_path": "$PDF_PATH",
  "pdf_hash": "$(md5sum "$PDF_PATH" | cut -d' ' -f1)"
}
EOF

echo "Metadata extracted: $PAPER_ID ($ID_TYPE)" >&2
