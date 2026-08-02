#!/bin/bash
# TDoc DOCX — 一键安装脚本
# 安装所有 Python 依赖

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SKILL_DIR"

echo "🔧 TDoc DOCX 安装开始..."
echo ""

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.6+，请先安装 Python"
    exit 1
fi

echo "📦 Python: $(python3 --version)"

# 检查/创建虚拟环境，从 requirements.txt 安装依赖
REQ_FILE="$SKILL_DIR/requirements.txt"
if [ ! -f "$REQ_FILE" ]; then
    echo "❌ 找不到 requirements.txt"
    exit 1
fi

if command -v uv &> /dev/null; then
    echo "📦 包管理器: uv"
    if [ ! -d ".venv" ]; then
        echo "  创建虚拟环境..."
        uv venv
    fi
    echo "  安装依赖..."
    source .venv/bin/activate
    uv pip install -r "$REQ_FILE"
else
    echo "📦 包管理器: pip"
    pip3 install -r "$REQ_FILE"
fi

echo ""
echo "✅ 核心依赖安装完成！"
echo ""

# ===== 安装系统级依赖 =====
echo "🔍 检查并安装系统级依赖..."

# 检测包管理器
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo "❌ macOS 需要 Homebrew，请先安装: https://brew.sh"
        exit 1
    fi
    PKG_MGR="brew"
elif command -v apt-get &> /dev/null; then
    PKG_MGR="apt"
elif command -v yum &> /dev/null; then
    PKG_MGR="yum"
else
    echo "⚠️  未识别的包管理器，请手动安装以下系统依赖："
    echo "    LibreOffice, pandoc, poppler, antiword"
    PKG_MGR="unknown"
fi

# 安装函数
install_sys_dep() {
    local cmd="$1"
    local desc="$2"
    local brew_pkg="$3"
    local apt_pkg="$4"

    if command -v "$cmd" &> /dev/null; then
        echo "  ✅ $desc — 已安装"
    else
        echo "  📥 $desc — 未检测到，正在安装..."
        case "$PKG_MGR" in
            brew)
                brew install $brew_pkg 2>&1 | tail -1
                ;;
            apt)
                sudo apt-get install -y $apt_pkg 2>&1 | tail -1
                ;;
            yum)
                sudo yum install -y $apt_pkg 2>&1 | tail -1
                ;;
            *)
                echo "     ⚠️  请手动安装: $desc"
                return 1
                ;;
        esac

        if command -v "$cmd" &> /dev/null; then
            echo "  ✅ $desc — 安装成功"
        else
            echo "  ❌ $desc — 安装失败，请手动安装"
        fi
    fi
}

# LibreOffice 特殊处理（macOS 用 --cask）
if command -v soffice &> /dev/null; then
    echo "  ✅ LibreOffice (高保真PDF转换/DOC→DOCX/接受修订) — 已安装"
else
    echo "  📥 LibreOffice — 未检测到，正在安装..."
    case "$PKG_MGR" in
        brew)
            brew install --cask libreoffice 2>&1 | tail -1
            ;;
        apt)
            sudo apt-get install -y libreoffice 2>&1 | tail -1
            ;;
        yum)
            sudo yum install -y libreoffice 2>&1 | tail -1
            ;;
        *)
            echo "     ⚠️  请手动安装 LibreOffice"
            ;;
    esac
    if command -v soffice &> /dev/null; then
        echo "  ✅ LibreOffice — 安装成功"
    else
        echo "  ❌ LibreOffice — 安装失败，请手动安装"
        echo "     macOS: brew install --cask libreoffice"
        echo "     Linux: sudo apt install libreoffice"
    fi
fi

install_sys_dep "pandoc"   "pandoc (高级文本提取)"       "pandoc"   "pandoc"
install_sys_dep "pdftoppm" "Poppler (DOCX→图片)"         "poppler"  "poppler-utils"
install_sys_dep "antiword" "antiword (.doc 读取)"         "antiword" "antiword"

echo ""
echo "========================================="
echo " TDoc DOCX 安装完成！"
echo "========================================="
echo ""
echo "用法示例："
echo "  # 创建文档"
echo "  python3 scripts/create_docx.py --title '测试文档' --output test.docx"
echo ""
echo "  # 读取文档"
echo "  python3 scripts/read_docx.py test.docx --format markdown"
echo ""
echo "  # 编辑文档"
echo "  python3 scripts/edit_docx.py input.docx output.docx edits.json"
echo ""
echo "  # 转换格式"
echo "  python3 scripts/convert_docx.py input.docx --to pdf"
echo ""
echo "  # 差异对比"
echo "  python3 scripts/diff_docx.py old.docx new.docx"
