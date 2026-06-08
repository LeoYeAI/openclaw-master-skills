#!/bin/bash
# check_duplicate.sh - 检查 PDF 是否已处理过，处理去重逻辑
# 用法：./check_duplicate.sh <metadata_json> [papers_base_dir]
# 输出：JSON 格式，包含处理建议

set -e

METADATA_JSON="$1"
# 使用 OPENCLAW_WORKSPACE 环境变量，或回退到默认路径
PAPERS_DIR="${2:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/papers}"

if [ ! -f "$METADATA_JSON" ]; then
    echo "Error: Metadata JSON not found: $METADATA_JSON" >&2
    exit 1
fi

# 解析元数据
PAPER_ID=$(jq -r '.paper_id' "$METADATA_JSON")
ID_TYPE=$(jq -r '.id_type' "$METADATA_JSON")
DOI=$(jq -r '.doi' "$METADATA_JSON")
TITLE=$(jq -r '.title' "$METADATA_JSON")
PDF_HASH=$(jq -r '.pdf_hash' "$METADATA_JSON")
PDF_PATH=$(jq -r '.pdf_path' "$METADATA_JSON")

# 创建 papers 目录
mkdir -p "$PAPERS_DIR"

# 索引文件：记录所有已处理的论文
INDEX_FILE="$PAPERS_DIR/.index.json"
if [ ! -f "$INDEX_FILE" ]; then
    echo '{"papers":{}}' > "$INDEX_FILE"
fi

# 检查是否存在
PAPER_DIR="$PAPERS_DIR/$PAPER_ID"
EXISTS="false"
if [ -d "$PAPER_DIR" ]; then
    EXISTS="true"
fi

# 判断文件类型（主文章 or 补充材料）
FILE_TYPE="main"
FILE_NAME=$(basename "$PDF_PATH")

# 补充材料判断规则：
# 1. 文件名包含 supplement/suppl/si/supporting/appendix/moesm/esm
# 2. DOI 包含 .supp 或类似后缀
if echo "$FILE_NAME" | grep -qiE "supplement|suppl|_si_|supporting|appendix|moesm|_esm|supplementary"; then
    FILE_TYPE="supplement"
elif echo "$DOI" | grep -qiE "\.supp|supplementary"; then
    FILE_TYPE="supplement"
fi

# 如果已存在，检查是否是同一文件（PDF 哈希相同）
ACTION="process_new"
MESSAGE="新论文，开始处理"
SUPPLEMENT_COUNT=0

if [ "$EXISTS" = "true" ]; then
    # 读取已有的元数据
    EXISTING_META="$PAPER_DIR/metadata.json"
    
    if [ -f "$EXISTING_META" ]; then
        EXISTING_PDF_HASH=$(jq -r '.pdf_hash' "$EXISTING_META" 2>/dev/null || echo "")
        
        # 完全相同的 PDF
        if [ "$PDF_HASH" = "$EXISTING_PDF_HASH" ]; then
            ACTION="skip_duplicate"
            MESSAGE="完全相同的 PDF 已处理过，跳过"
        else
            # DOI 相同但内容不同 → 可能是新版本
            if [ "$ID_TYPE" = "doi" ] && [ -n "$DOI" ]; then
                ACTION="update_version"
                MESSAGE="检测到同 DOI 的不同版本，建议更新"
            else
                # 指纹相同但 PDF 不同 → 可能是重新生成的
                ACTION="update_version"
                MESSAGE="检测到同论文的不同版本，建议更新"
            fi
        fi
    fi
    
    # 如果是补充材料，计数
    if [ "$FILE_TYPE" = "supplement" ]; then
        SUPPLEMENT_DIR="$PAPER_DIR/supplements"
        if [ -d "$SUPPLEMENT_DIR" ]; then
            SUPPLEMENT_COUNT=$(ls -1 "$SUPPLEMENT_DIR"/*.pdf 2>/dev/null | wc -l || echo 0)
        fi
        ACTION="add_supplement"
        MESSAGE="补充材料，将合并到主文档（已有 $SUPPLEMENT_COUNT 个补充文件）"
    fi
fi

# 输出结果 JSON
cat << EOF
{
  "paper_id": "$PAPER_ID",
  "paper_dir": "$PAPER_DIR",
  "exists": $EXISTS,
  "file_type": "$FILE_TYPE",
  "action": "$ACTION",
  "message": "$MESSAGE",
  "supplement_count": $SUPPLEMENT_COUNT,
  "existing_pdf_hash": "${EXISTING_PDF_HASH:-null}",
  "current_pdf_hash": "$PDF_HASH"
}
EOF

echo "Duplicate check: $ACTION - $MESSAGE" >&2
