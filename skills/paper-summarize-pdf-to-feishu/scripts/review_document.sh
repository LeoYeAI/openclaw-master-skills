#!/bin/bash
# review_document.sh - 生成审核报告，对比飞书文档与原始 PDF
# 用法: ./review_document.sh <doc_token> <paper.txt> <output.md>

set -e

DOC_TOKEN="$1"
PAPER_TXT="$2"
OUTPUT="${3:-/tmp/review_report.md}"

if [ -z "$DOC_TOKEN" ] || [ -z "$PAPER_TXT" ]; then
  echo "用法: $0 <doc_token> <paper.txt> [output.md]"
  exit 1
fi

echo "正在生成审核报告..."

# 读取飞书文档内容（保存到临时文件）
feishu_doc read "$DOC_TOKEN" > /tmp/feishu_content.json 2>/dev/null || {
  echo "错误：无法读取飞书文档 $DOC_TOKEN"
  exit 1
}

# 提取纯文本内容
cat /tmp/feishu_content.json | jq -r '.content // "[无法提取内容]"' > /tmp/feishu_text.txt

# 统计对比
echo "# 审核报告" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**生成时间**: $(date +%Y-%m-%d\ %H:%M)" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**文档 Token**: $DOC_TOKEN" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 字数对比
PAPER_WORDS=$(wc -w < "$PAPER_TXT")
FEISHU_WORDS=$(wc -w < /tmp/feishu_text.txt)

echo "## 一、基础统计" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "| 项目 | 原始 PDF | 飞书文档 |" >> "$OUTPUT"
echo "|------|----------|----------|" >> "$OUTPUT"
echo "| 字数 | $PAPER_WORDS | $FEISHU_WORDS |" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 检查关键章节
# 从原始 PDF 提取章节标题
grep -E "^[一二三四五六七八九十]+、" "$PAPER_TXT" | head -20 > /tmp/paper_sections.txt 2>/dev/null || true

echo "## 二、章节完整性检查" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "原始 PDF 章节:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
if [ -s /tmp/paper_sections.txt ]; then
  cat /tmp/paper_sections.txt | sed 's/^/- /' >> "$OUTPUT"
else
  echo "- [无法自动提取章节，需人工检查]" >> "$OUTPUT"
fi
echo "" >> "$OUTPUT"

# Figure/Table 检查
echo "## 三、Figure/Table 检查" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "原始 PDF 中的 Figure/Table:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
grep -E "^(Figure|Fig\.|Table) [0-9A-Z]" "$PAPER_TXT" | head -30 | sed 's/^/- /' >> "$OUTPUT" || echo "- [未找到 Figure/Table]" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 四、关键数据核对" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "请人工核对以下关键数据:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
# 提取可能的关键数据（数字+%）
grep -oE "[0-9]+%|[0-9]+\.[0-9]+%|p\s*[=<>]\s*[0-9.]+|N\s*=\s*[0-9]+" "$PAPER_TXT" | sort -u | head -20 | sed 's/^/- /' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 五、审核结论" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "- [ ] 章节结构完整" >> "$OUTPUT"
echo "- [ ] 关键数据准确" >> "$OUTPUT"
echo "- [ ] Figure/Table 无遗漏" >> "$OUTPUT"
echo "- [ ] 引用正确" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 六、建议修改" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "[待填写]" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**审核人**: [待填写]" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**审核日期**: [待填写]" >> "$OUTPUT"

echo "审核报告已生成: $OUTPUT"
