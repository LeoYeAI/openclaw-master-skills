#!/bin/bash
# locate_figures.sh - 从 PDF 中定位所有 Figure 和 Table 的页码
# 用法: ./locate_figures.sh <input.pdf> <paper.txt> <output_dir>
# 输出: 对每个 Figure/Table 所在的估算页面截图，并生成 manifest.json

set -e

INPUT_PDF="$1"
PAPER_TXT="$2"
OUTPUT_DIR="$3"

if [ -z "$INPUT_PDF" ] || [ -z "$PAPER_TXT" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "用法: $0 <input.pdf> <paper.txt> <output_dir>"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# 获取总页数和总行数
PAGES=$(pdfinfo "$INPUT_PDF" 2>/dev/null | grep "^Pages:" | awk '{print $2}')
LINES=$(wc -l < "$PAPER_TXT")
echo "PDF 总页数: $PAGES, 文本总行数: $LINES"

# 提取 Figure/Table 标题行及行号
echo "正在定位 Figure/Table..."
grep -niE '^(figure|fig\.|table) [0-9A-Z]' "$PAPER_TXT" | head -50 > /tmp/fig_lines.txt

if [ ! -s /tmp/fig_lines.txt ]; then
  echo "未找到 Figure/Table 标题，尝试宽泛匹配..."
  grep -niE '(figure [0-9]|table [0-9])' "$PAPER_TXT" | head -50 > /tmp/fig_lines.txt
fi

# 估算每个 Figure 的页码并截图
# 注意：行号→页码是粗略估算，后续需要审核验证
LINES_PER_PAGE=$((LINES / PAGES))
echo "平均每页约 $LINES_PER_PAGE 行（仅估算）"

FIGURE_COUNT=0
while IFS=: read -r LINE_NUM CONTENT; do
  # 估算页码（±2 页范围截图供审核）
  EST_PAGE=$((LINE_NUM / LINES_PER_PAGE + 1))
  START_PAGE=$((EST_PAGE - 2))
  END_PAGE=$((EST_PAGE + 2))
  [ "$START_PAGE" -lt 1 ] && START_PAGE=1
  [ "$END_PAGE" -gt "$PAGES" ] && END_PAGE=$PAGES

  # 提取 Figure/Table 编号
  FIG_ID=$(echo "$CONTENT" | grep -oiE '(figure|fig\.|table) [0-9A-Z]+\.?[0-9]*' | head -1 | tr ' .' '_' | tr '[:lower:]' '[:upper:]')
  [ -z "$FIG_ID" ] && FIG_ID="UNKNOWN_${FIGURE_COUNT}"

  echo "  $FIG_ID: 行 $LINE_NUM → 估算页 $EST_PAGE (截图范围: $START_PAGE-$END_PAGE)"

  # 截取候选页面
  CANDIDATE_DIR="$OUTPUT_DIR/candidates_${FIG_ID}"
  mkdir -p "$CANDIDATE_DIR"
  pdftoppm -png -r 200 -f "$START_PAGE" -l "$END_PAGE" "$INPUT_PDF" "$CANDIDATE_DIR/page" 2>/dev/null

  FIGURE_COUNT=$((FIGURE_COUNT + 1))
done < /tmp/fig_lines.txt

echo ""
echo "完成！共定位 $FIGURE_COUNT 个 Figure/Table"
echo "候选截图目录: $OUTPUT_DIR/candidates_*/"
echo ""
echo "⚠️ 下一步: 使用 read 工具逐张审核候选截图，确认正确页码"
