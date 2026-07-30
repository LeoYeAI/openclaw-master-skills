#!/bin/bash
# astock-video-report 一键安装依赖脚本
set -e

echo "=== astock-video-report 依赖安装 ==="

# 1. Python 依赖
echo ""
echo "[1/4] 安装 Python 依赖（pillow）..."
if python3 -c "import PIL" 2>/dev/null; then
    echo "✅ pillow 已存在"
else
    pip3 install pillow || pip install pillow
    echo "✅ pillow 已安装"
fi

echo ""
echo "[2/4] 安装字体转换依赖（fonttools + brotli）..."
if python3 -c "import fontTools" 2>/dev/null; then
    echo "✅ fonttools 已存在"
else
    pip3 install fonttools brotli || pip install fonttools brotli
    echo "✅ fonttools + brotli 已安装"
fi

# 2. ffmpeg
echo ""
echo "[3/4] 检查 ffmpeg..."
if command -v ffmpeg &>/dev/null; then
    echo "✅ ffmpeg 已存在：$(ffmpeg -version 2>&1 | head -1)"
else
    echo "⚠️  未找到 ffmpeg，请手动安装："
    echo "   macOS:   brew install ffmpeg"
    echo "   Ubuntu:  sudo apt install ffmpeg"
    echo "   CentOS:  sudo yum install ffmpeg"
    echo "   Windows: https://ffmpeg.org/download.html"
    echo ""
    echo "   安装后重新运行此脚本"
fi

# 3. 数据 Skills
echo ""
echo "[4/4] 安装数据 Skills..."
if command -v skillhub &>/dev/null; then
    skillhub install ftshare-market-data   || echo "⚠️  ftshare-market-data 安装失败，请手动安装"
    skillhub install newsnow-reader        || echo "⚠️  newsnow-reader 安装失败，请手动安装"
elif command -v clawhub &>/dev/null; then
    echo "未找到 skillhub，使用 clawhub 安装..."
    clawhub install ftshare-market-data    || echo "⚠️  ftshare-market-data 安装失败"
    clawhub install newsnow-reader         || echo "⚠️  newsnow-reader 安装失败"
else
    echo "⚠️  未找到 skillhub 或 clawhub，请先安装 OpenClaw"
    echo "   参考：https://openclaw.ai"
fi

echo ""
echo "=== 安装完成！==="
echo ""
echo "使用方式：告诉 AI「生成今日A股复盘视频」"
echo ""
echo "⚠️  数据仅供参考，不构成投资建议"
