#!/bin/bash
# WeChat Publisher - 发布脚本
# 用于 OpenClaw Skill 快速调用

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 自动检查和更新依赖
if [ -f "$SCRIPT_DIR/check-deps.sh" ]; then
    bash "$SCRIPT_DIR/check-deps.sh"
fi

# 检查是否安装了工具
if ! command -v wechat-pub &> /dev/null; then
    echo -e "${RED}错误: wechat-pub 未安装${NC}"
    echo "请运行: npm install -g wechat-md-publisher"
    exit 1
fi

# 解析参数
ACTION=${1:-"help"}
FILE=${2:-""}
THEME=${3:-"default"}

case $ACTION in
    "publish")
        if [ -z "$FILE" ]; then
            echo -e "${RED}错误: 请提供文件路径${NC}"
            echo "用法: $0 publish <file> [theme]"
            exit 1
        fi
        
        echo -e "${YELLOW}正在发布文章...${NC}"
        wechat-pub publish create --file "$FILE" --theme "$THEME"
        echo -e "${GREEN}✓ 发布成功${NC}"
        ;;
        
    "draft")
        if [ -z "$FILE" ]; then
            echo -e "${RED}错误: 请提供文件路径${NC}"
            echo "用法: $0 draft <file> [theme]"
            exit 1
        fi
        
        echo -e "${YELLOW}正在创建草稿...${NC}"
        wechat-pub draft create --file "$FILE" --theme "$THEME"
        echo -e "${GREEN}✓ 草稿创建成功${NC}"
        ;;
        
    "list-drafts")
        echo -e "${YELLOW}草稿列表:${NC}"
        wechat-pub draft list
        ;;
        
    "list-published")
        echo -e "${YELLOW}已发布文章:${NC}"
        wechat-pub publish list
        ;;
        
    "themes")
        echo -e "${YELLOW}可用主题:${NC}"
        wechat-pub theme list
        ;;
        
    "help"|*)
        echo "WeChat Publisher - 使用说明"
        echo ""
        echo "用法:"
        echo "  $0 publish <file> [theme]     - 发布文章"
        echo "  $0 draft <file> [theme]       - 创建草稿"
        echo "  $0 list-drafts                - 列出草稿"
        echo "  $0 list-published             - 列出已发布文章"
        echo "  $0 themes                     - 列出可用主题"
        echo ""
        echo "示例:"
        echo "  $0 publish article.md orangeheart"
        echo "  $0 draft article.md lapis"
        ;;
esac
