#!/bin/bash
# extract_pdf_images.sh - 从 PDF 提取所有嵌入图片
# 用法: ./extract_pdf_images.sh <input.pdf> <output_dir>

set -e

INPUT="$1"
OUTPUT_DIR="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "用法: $0 <input.pdf> <output_dir>"
  exit 1
fi

# 检查依赖
if ! command -v pdfimages &> /dev/null; then
  echo "pdfimages 未安装，正在安装 poppler-utils..."
  sudo apt-get install -y poppler-utils
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 提取所有图片（PNG 格式）
echo "正在提取图片..."
pdfimages -png "$INPUT" "$OUTPUT_DIR/img"

# 统计数量
COUNT=$(ls "$OUTPUT_DIR"/img-*.png 2>/dev/null | wc -l)
echo "提取完成：$COUNT 张图片 → $OUTPUT_DIR"

# 生成图片清单
echo "生成图片清单..."
{
  echo "# PDF 图片清单"
  echo ""
  echo "**源文件**: $(basename "$INPUT")"
  echo "**提取时间**: $(date +%Y-%m-%d)"
  echo "**图片数量**: $COUNT"
  echo ""
  echo "## 图片列表"
  echo ""
  
  for img in "$OUTPUT_DIR"/img-*.png; do
    if [ -f "$img" ]; then
      BASENAME=$(basename "$img")
      SIZE=$(ls -lh "$img" | awk '{print $5}')
      DIMS=$(file "$img" | grep -oP '\d+ x \d+' || echo "未知")
      echo "- \`$BASENAME\` - $SIZE ($DIMS)"
    fi
  done
} > "$OUTPUT_DIR/README.md"

echo "清单已写入：$OUTPUT_DIR/README.md"
