#!/bin/bash
# alphashop-sel-newproduct Skill 测试脚本

echo "======================================"
echo "1688遨虾AI选品 Skill 测试"
echo "======================================"
echo ""

# 检查凭证
if [ -z "$ALPHASHOP_ACCESS_KEY" ] || [ -z "$ALPHASHOP_SECRET_KEY" ]; then
    echo "⚠️  未检测到 API 凭证"
    echo ""
    echo "请选择配置方式："
    echo "  1) 手动输入（本次有效）"
    echo "  2) 使用 .env 文件"
    echo "  3) 退出"
    echo ""
    read -p "请选择 [1-3]: " choice

    case $choice in
        1)
            echo ""
            read -p "请输入 ALPHASHOP_ACCESS_KEY: " ALPHASHOP_ACCESS_KEY
            read -p "请输入 ALPHASHOP_SECRET_KEY: " ALPHASHOP_SECRET_KEY
            export ALPHASHOP_ACCESS_KEY
            export ALPHASHOP_SECRET_KEY
            ;;
        2)
            if [ -f ".env" ]; then
                echo "→ 加载 .env 文件..."
                source .env
                echo "✓ 凭证已加载"
            else
                echo "❌ .env 文件不存在"
                echo "   运行: cp .env.example .env 并编辑"
                exit 1
            fi
            ;;
        3)
            echo "退出"
            exit 0
            ;;
        *)
            echo "❌ 无效选择"
            exit 1
            ;;
    esac
else
    echo "✓ 检测到 API 凭证"
fi

echo ""
echo "======================================"
echo "开始测试"
echo "======================================"
echo ""

# 测试参数
KEYWORD="phone"
PLATFORM="amazon"
COUNTRY="US"

echo "测试参数："
echo "  关键词: $KEYWORD"
echo "  平台: $PLATFORM"
echo "  国家: $COUNTRY"
echo ""

# 运行测试
python3 scripts/selection.py report \
    --keyword "$KEYWORD" \
    --platform "$PLATFORM" \
    --country "$COUNTRY"

echo ""
echo "======================================"
echo "测试完成"
echo "======================================"
