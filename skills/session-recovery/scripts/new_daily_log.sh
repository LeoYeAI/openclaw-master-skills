#!/bin/bash
# 快速创建每日工作记录模板
# 功能：自动创建 memory/YYYY-MM-DD.md，包含标准模板

MEMORY_DIR="./memory"
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
TIME=$(date '+%H:%M')

# 检查文件是否已存在
if [ -f "$MEMORY_FILE" ]; then
    echo "⚠️  今日记录已存在: $MEMORY_FILE"
    echo "💡 使用 --edit 参数编辑，或 --view 查看"
    exit 0
fi

# 创建目录（如果不存在）
mkdir -p "$MEMORY_DIR"

# 生成模板
cat > "$MEMORY_FILE" << 'EOF'
# YYYY-MM-DD 工作记录

**会话时间：** YYYY-MM-DD HH:MM - HH:MM
**状态：** 活跃
**主要任务：** [一句话描述]

---

## 📋 完成的任务

### 1. [任务名称] ✅
**描述：** [简要描述]
**产出：**
- [文件/文档/代码]

**关键决策：**
- [决策内容]

---

## 🎯 关键决策

### 1. [决策标题]
**背景：** [为什么需要这个决策]
**选择：** [最终选择]
**理由：** [为什么这样选择]

---

## 📚 学到的经验

### 1. [经验标题]
**问题：** [遇到的问题]
**解决：** [如何解决]
**教训：** [学到了什么]

---

## 📂 文件操作记录

### 创建的文件
- `[文件名]` - [用途]

### 修改的文件
- `[文件名]` - [修改内容]

---

## 🎯 下次会话重点

### 高优先级
- [ ] [任务1]
- [ ] [任务2]

### 中优先级
- [ ] [任务3]

---

## 💬 备注

[临时想法、灵感、待办等]

---

**工作时长：** XX分钟
**产出统计：** X个文档，Y行代码
EOF

# 替换日期时间
sed -i '' "s/YYYY-MM-DD/$TODAY/g" "$MEMORY_FILE"
sed -i '' "s/HH:MM/$TIME/g" "$MEMORY_FILE"

echo "✅ 已创建今日工作记录模板"
echo "📄 文件位置: $MEMORY_FILE"
echo ""
echo "📝 下一步："
echo "   1. 编辑文件，填写今日工作内容"
echo "   2. 会话结束时，更新完成"
echo "   3. 运行 ./scripts/update_status.sh 同步到 STATUS.md"
