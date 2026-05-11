#!/bin/bash
# Anima-AIOS Skill - Post Install Script
# 从 Skill 包内复制 Core 到全局目录，无远程操作

set -e

echo "🚀 Anima-AIOS 安装"
echo "════════════════════════════════════════════"

ANIMA_HOME="$HOME/.anima"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_SOURCE="$SCRIPT_DIR/core"

# 检查 Python
echo "[1/3] 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.10+"
    exit 1
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2)"

# 检查 Git
echo "[2/3] 检查 Git..."
if ! command -v git &> /dev/null; then
    echo "❌ 需要 Git"
    exit 1
fi
echo "✅ Git $(git --version | cut -d' ' -f3)"

# 安装 Python 依赖
echo "[3/4] 安装 Python 依赖..."
pip3 install -q "watchdog>=3.0.0" 2>/dev/null || pip install -q "watchdog>=3.0.0" 2>/dev/null || echo "⚠️ watchdog 安装失败，memory_watcher 将使用 polling 模式"
echo "✅ Python 依赖检查完成"

# 安装 Core（本地复制，不远程克隆）
echo "[4/4] 安装 Anima Core..."
if [ -d "$ANIMA_HOME/core" ] && [ -f "$ANIMA_HOME/core/exp_tracker.py" ]; then
    echo "✅ Core 已安装，检查更新..."
    # 覆盖更新
    cp -r "$CORE_SOURCE"/* "$ANIMA_HOME/core/"
    cp -r "$SCRIPT_DIR/config"/* "$ANIMA_HOME/config/" 2>/dev/null || true
    echo "✅ Core + Config 已更新"
else
    mkdir -p "$ANIMA_HOME/core"
    mkdir -p "$ANIMA_HOME/config"
    cp -r "$CORE_SOURCE"/* "$ANIMA_HOME/core/"
    cp -r "$SCRIPT_DIR/config"/* "$ANIMA_HOME/config/" 2>/dev/null || true
    echo "✅ Core + Config 安装完成"
fi

echo ""
echo "════════════════════════════════════════════"
echo "✅ Anima-AIOS 安装完成！"
echo ""
echo "开始使用："
echo "  python3 anima_doctor.py        # 自检"
echo "  python3 anima_doctor.py --fix  # 自修"
echo ""
echo "⚠️  隐私提示："
echo "  - team_mode 默认为 false，不会扫描其他 Agent 数据"
echo "  - 如需启用团队排行，在配置中设置 team_mode: true"
echo "  - 详见：~/.anima/config/anima_config.json"
echo ""
