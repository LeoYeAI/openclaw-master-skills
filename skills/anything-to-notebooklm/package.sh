#!/bin/bash

# 打包 anything-to-notebooklm skill 用于分享
# 生成一个不包含大文件的精简版 tar.gz

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="anything-to-notebooklm"
OUTPUT_DIR="${1:-$HOME/Desktop}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/${SKILL_NAME}_${TIMESTAMP}.tar.gz"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  打包 ${SKILL_NAME} Skill${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 要打包的文件列表
FILES=(
    "SKILL.md"
    "README.md"
    "install.sh"
    "check_env.py"
    "requirements.txt"
    ".gitignore"
)

# 创建临时目录
TEMP_DIR=$(mktemp -d)
TEMP_SKILL="$TEMP_DIR/$SKILL_NAME"
mkdir -p "$TEMP_SKILL"

echo "📦 正在打包文件..."

# 复制文件
for file in "${FILES[@]}"; do
    if [ -f "$SKILL_DIR/$file" ]; then
        cp "$SKILL_DIR/$file" "$TEMP_SKILL/"
        echo "  ✓ $file"
    fi
done

# 创建 tar.gz
cd "$TEMP_DIR"
tar -czf "$OUTPUT_FILE" "$SKILL_NAME"

# 清理
rm -rf "$TEMP_DIR"

# 显示结果
FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)

echo ""
echo -e "${GREEN}✅ 打包完成！${NC}"
echo ""
echo "📦 文件：$OUTPUT_FILE"
echo "📊 大小：$FILE_SIZE"
echo ""
echo "📤 分享说明："
echo "  用户收到文件后，执行："
echo "    cd ~/.claude/skills/"
echo "    tar -xzf ${SKILL_NAME}_${TIMESTAMP}.tar.gz"
echo "    cd ${SKILL_NAME}"
echo "    ./install.sh"
echo ""
echo "💡 注意：wexin-read-mcp 会在安装时自动克隆，无需打包"
echo ""
