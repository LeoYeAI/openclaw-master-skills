#!/bin/bash
# merge_supplement.sh - 将补充材料合并到主文档
# 用法：./merge_supplement.sh <paper_dir> <supplement_pdf> <feishu_doc_token>

set -e

PAPER_DIR="$1"
SUPPLEMENT_PDF="$2"
DOC_TOKEN="$3"

if [ ! -d "$PAPER_DIR" ]; then
    echo "Error: Paper directory not found: $PAPER_DIR" >&2
    exit 1
fi

if [ ! -f "$SUPPLEMENT_PDF" ]; then
    echo "Error: Supplement PDF not found: $SUPPLEMENT_PDF" >&2
    exit 1
fi

echo "Merging supplement into main document..." >&2

# 1. 复制补充材料到 supplements 目录
SUPPLEMENTS_DIR="$PAPER_DIR/supplements"
mkdir -p "$SUPPLEMENTS_DIR"

SUPP_NAME=$(basename "$SUPPLEMENT_PDF")
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAFE_NAME="${TIMESTAMP}_${SUPP_NAME}"
cp "$SUPPLEMENT_PDF" "$SUPPLEMENTS_DIR/$SAFE_NAME"

echo "Copied supplement to: $SUPPLEMENTS_DIR/$SAFE_NAME" >&2

# 2. 提取补充材料的元数据
SUPP_META="$SUPPLEMENTS_DIR/${SAFE_NAME%.pdf}_meta.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/extract_metadata.sh" "$SUPPLEMENTS_DIR/$SAFE_NAME" "$SUPP_META" 2>/dev/null || true

# 3. 提取补充材料的简要总结（前 3 页）
SUPP_TXT="$SUPPLEMENTS_DIR/${SAFE_NAME%.pdf}.txt"
pdftotext -l 3 "$SUPPLEMENTS_DIR/$SAFE_NAME" "$SUPP_TXT" 2>/dev/null || true

# 4. 生成补充材料摘要
SUPP_SUMMARY=""
if [ -f "$SUPP_TXT" ]; then
    SUPP_SUMMARY=$(head -20 "$SUPP_TXT" | tr '\n' ' ' | cut -c1-500)
fi

# 5. 输出信息供上层调用
cat << EOF
{
  "supplement_path": "$SUPPLEMENTS_DIR/$SAFE_NAME",
  "supplement_name": "$SAFE_NAME",
  "summary": "$SUPP_SUMMARY",
  "feishu_update_needed": true
}
EOF

echo "Supplement merged successfully" >&2
