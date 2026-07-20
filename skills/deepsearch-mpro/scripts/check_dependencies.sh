#!/bin/bash
# check_dependencies.sh - 检查 consulting-analysis 依赖技能
# 用途：验证所有必需和可选技能是否已正确安装

SKILLS_DIR="$HOME/.workbuddy/skills"

echo "==================================="
echo "Consulting-Analysis 依赖检查"
echo "==================================="
echo ""

# 必需技能
REQUIRED_SKILLS=(
    "deep-research-pro"
    "multi-search-engine"
    "ddg-web-search"
    "pdf"
    "docx"
    "pptx"
)

# 可选技能
OPTIONAL_SKILLS=(
    "insights-hotspot"
)

missing_required=()
missing_optional=()

echo "检查必需技能..."
echo "-------------------"
for skill in "${REQUIRED_SKILLS[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo "✓ $skill"
    else
        echo "✗ $skill (缺失)"
        missing_required+=("$skill")
    fi
done

echo ""
echo "检查可选技能..."
echo "-------------------"
for skill in "${OPTIONAL_SKILLS[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo "○ $skill (已安装)"
    else
        echo "○ $skill (未安装，可选)"
        missing_optional+=("$skill")
    fi
done

echo ""
echo "==================================="

if [ ${#missing_required[@]} -eq 0 ]; then
    echo "✓ 所有必需技能已安装！"
    echo ""
    echo "可以开始使用 consulting-analysis 技能。"
    exit 0
else
    echo "✗ 缺失必需技能："
    echo ""
    for skill in "${missing_required[@]}"; do
        echo "  - $skill"
    done
    echo ""
    echo "请安装缺失的技能后再使用 consulting-analysis。"
    echo ""
    echo "安装命令示例："
    echo "  cp -R /path/to/skill ~/.workbuddy/skills/"
    exit 1
fi

if [ ${#missing_optional[@]} -gt 0 ]; then
    echo ""
    echo "缺失可选技能（建议安装以获得增强功能）："
    echo ""
    for skill in "${missing_optional[@]}"; do
        echo "  - $skill"
    done
    echo ""
fi
