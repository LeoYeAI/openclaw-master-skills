#!/bin/bash
# extract_pdf_text.sh - 智能 PDF 文本提取（pdftotext + OCR 回退）
# 用法: ./extract_pdf_text.sh <input.pdf> [output.txt]
# 策略: 先 pdftotext，检测字数/页数比，过低则自动走 OCR 路线

set -e

INPUT="$1"
OUTPUT="${2:-/tmp/pdf_extracted.txt}"
THRESHOLD=50  # 每页最低字数阈值，低于此值视为扫描版

if [ -z "$INPUT" ]; then
  echo "用法: $0 <input.pdf> [output.txt]"
  exit 1
fi

# 检查依赖
for cmd in pdftotext pdfinfo; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "$cmd 未安装，正在安装 poppler-utils..."
    sudo apt-get install -y poppler-utils
    break
  fi
done

# 获取页数
PAGES=$(pdfinfo "$INPUT" 2>/dev/null | grep "^Pages:" | awk '{print $2}')
if [ -z "$PAGES" ] || [ "$PAGES" -eq 0 ]; then
  echo "警告：无法获取页数，默认按 1 页处理"
  PAGES=1
fi
echo "PDF 页数：$PAGES"

# 先用 pdftotext 提取
pdftotext "$INPUT" "$OUTPUT"
CHARS=$(wc -m < "$OUTPUT")
RATIO=$((CHARS / PAGES))
echo "pdftotext 提取：$CHARS 字符，每页约 $RATIO 字符"

# 判断是否需要 OCR
if [ "$RATIO" -lt "$THRESHOLD" ]; then
  echo "字符密度过低 ($RATIO < $THRESHOLD/页)，疑似扫描版，启动 OCR..."

  # 检查 OCR 依赖
  for cmd in pdftoppm tesseract; do
    if ! command -v "$cmd" &> /dev/null; then
      echo "错误：$cmd 未安装，无法执行 OCR"
      echo "安装：sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim"
      exit 1
    fi
  done

  TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT

  echo "转换 PDF 页面为图片..."
  pdftoppm -png -r 300 "$INPUT" "$TMPDIR/page"

  echo "OCR 识别中..."
  > "$OUTPUT"
  for img in "$TMPDIR"/page-*.png; do
    if [ -f "$img" ]; then
      tesseract "$img" stdout -l eng+chi_sim --psm 6 2>/dev/null >> "$OUTPUT"
      echo "" >> "$OUTPUT"
    fi
  done

  CHARS_OCR=$(wc -m < "$OUTPUT")
  echo "OCR 提取：$CHARS_OCR 字符"
else
  echo "文本密度正常，使用 pdftotext 结果"
fi

LINES=$(wc -l < "$OUTPUT")
echo "提取完成：$OUTPUT ($LINES 行)"
