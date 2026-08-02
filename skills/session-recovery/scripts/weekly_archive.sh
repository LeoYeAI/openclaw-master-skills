#!/bin/bash
# 每周归档脚本
# 功能：归档旧的每日记录，生成每周摘要

MEMORY_DIR="./memory"
ARCHIVE_DIR="$MEMORY_DIR/archive"
WEEKLY_DIR="$ARCHIVE_DIR/$(date +%Y-W%V)"

echo "📦 开始每周归档..."
echo ""

# 创建归档目录
mkdir -p "$WEEKLY_DIR"
echo "✅ 创建归档目录: $WEEKLY_DIR"

# 获取上周的文件（保留最近7天）
echo "📄 归档上周记录..."
find "$MEMORY_DIR" -name "*.md" -mtime +7 -type f | while read file; do
    filename=$(basename "$file")
    echo "   移动: $filename"
    mv "$file" "$WEEKLY_DIR/"
done

echo ""
echo "📊 生成每周摘要..."

# 统计本周工作
TOTAL_FILES=$(find "$MEMORY_DIR" -name "*.md" -mtime -7 | wc -l | xargs)
echo "📝 本周记录: $TOTAL_FILES 个文件"

# 生成摘要文件
SUMMARY_FILE="$ARCHIVE_DIR/weekly_summary_$(date +%Y-W%V).md"
cat > "$SUMMARY_FILE" << EOF
# 每周工作摘要 - $(date +%Y年)第$(date +%V)周

**归档时间：** $(date '+%Y-%m-%d %H:%M')
**记录数量：** $TOTAL_FILES 个文件

---

## 📊 本周统计

- 📝 工作记录：$TOTAL_FILES 个
- 📂 归档位置：$WEEKLY_DIR

---

## 🎯 本周成就

（从归档文件中提取）

---

## 📚 经验总结

（从归档文件中提取）

---

## 🔄 下周计划

（待填写）

---

_本摘要由 weekly_archive.sh 自动生成_
EOF

echo "✅ 摘要已生成: $SUMMARY_FILE"
echo ""
echo "🎉 归档完成！"
echo ""
echo "📂 归档位置: $WEEKLY_DIR"
echo "📄 每周摘要: $SUMMARY_FILE"
