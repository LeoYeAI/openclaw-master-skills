#!/bin/bash
# CANN Review 技能安装后脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/gitcode.conf"

echo "🎉 CANN Review 技能已安装！"
echo "========================"
echo ""

if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  检测到这是首次安装，需要配置 GitCode API Token"
    echo ""
    echo "请运行以下命令进行配置："
    echo ""
    echo "  cd $SCRIPT_DIR"
    echo "  ./gitcode-api.sh setup"
    echo ""
    echo "或者手动配置："
    echo ""
    echo "  cp config/gitcode.conf.example config/gitcode.conf"
    echo "  nano config/gitcode.conf"
    echo ""
    echo "📖 获取 Token: https://gitcode.com/setting/token-classic"
    echo ""
else
    echo "✅ 配置文件已存在: config/gitcode.conf"
    echo ""
    echo "如需重新配置，请运行："
    echo "  ./gitcode-api.sh setup"
    echo ""
fi

echo "📚 文档："
echo "  - 快速开始: QUICKSTART.md"
echo "  - 完整文档: README.md"
echo "  - 迁移指南: MIGRATION.md"
echo ""
echo "🧪 测试："
echo "  ./test-api.sh"
echo ""
