#!/bin/bash
# 腾讯云COS技能安装脚本

set -e

echo "=========================================="
echo "  腾讯云COS Clawdbot技能安装脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js 已安装 (版本: $NODE_VERSION)"
    else
        print_error "Node.js 未安装"
        echo "请先安装 Node.js (版本 >= 14)"
        exit 1
    fi
    
    # 检查npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm 已安装 (版本: $NPM_VERSION)"
    else
        print_error "npm 未安装"
        exit 1
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python3 已安装 (版本: $PYTHON_VERSION)"
    else
        print_warning "Python3 未安装，部分功能可能受限"
    fi
}

# 安装cos-mcp包
install_cos_mcp() {
    print_info "安装腾讯云COS MCP服务器..."
    
    # 检查是否已安装
    if npm list -g cos-mcp &> /dev/null; then
        CURRENT_VERSION=$(npm list -g cos-mcp | grep cos-mcp | cut -d'@' -f2)
        print_info "cos-mcp 已安装 (版本: $CURRENT_VERSION)"
        
        read -p "是否更新到最新版本？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            npm update -g cos-mcp
            print_success "cos-mcp 已更新"
        fi
    else
        npm install -g cos-mcp@latest
        print_success "cos-mcp 安装完成"
    fi
    
    # 验证安装
    if command -v cos-mcp &> /dev/null; then
        print_success "cos-mcp 命令可用"
    else
        print_warning "cos-mcp 命令可能不可用，尝试使用 npx cos-mcp"
    fi
}

# 配置环境变量
setup_environment() {
    print_info "配置环境变量..."
    
    # 创建环境变量模板
    ENV_TEMPLATE="config/env.template"
    if [ ! -f "$ENV_TEMPLATE" ]; then
        cat > "$ENV_TEMPLATE" << 'EOF'
# 腾讯云COS配置
# 请将以下值替换为您的实际配置

# 区域 (在COS控制台查看存储桶所属地域)
export TENCENT_COS_REGION="ap-guangzhou"

# 存储桶名称
export TENCENT_COS_BUCKET="your-bucket-name-123456"

# 访问密钥 (在腾讯云控制台-访问管理-API密钥管理创建)
export TENCENT_COS_SECRET_ID="AKIDxxxxxxxxxxxxxxxxxxxxxxxx"
export TENCENT_COS_SECRET_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 数据集名称 (用于智能搜索，可选)
export TENCENT_COS_DATASET_NAME=""

# 连接模式 (stdio 或 sse)
export TENCENT_COS_CONNECT_TYPE="stdio"

# 调试模式
export TENCENT_COS_DEBUG="false"

# 高级配置 (可选)
# export TENCENT_COS_DOMAIN=""
# export TENCENT_COS_SERVICE_DOMAIN=""
# export TENCENT_COS_PROTOCOL="https:"
EOF
        print_success "已创建环境变量模板: $ENV_TEMPLATE"
    fi
    
    # 检查是否已有.env文件
    if [ -f ".env" ]; then
        print_info "发现现有的 .env 文件"
        read -p "是否备份现有配置？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
            print_success "配置已备份"
        fi
    fi
    
    # 提示用户配置
    print_warning "请编辑 $ENV_TEMPLATE 文件，填入您的腾讯云COS配置"
    print_info "完成后，运行: cp config/env.template .env"
}

# 配置Clawdbot
setup_clawdbot() {
    print_info "配置Clawdbot集成..."
    
    # 检查Clawdbot配置目录
    CLAWDBOT_CONFIG_DIR="$HOME/.openclaw"
    if [ ! -d "$CLAWDBOT_CONFIG_DIR" ]; then
        print_warning "Clawdbot配置目录不存在: $CLAWDBOT_CONFIG_DIR"
        print_info "请先安装和配置Clawdbot"
        return 1
    fi
    
    # 创建技能配置示例
    SKILL_CONFIG="config/clawdbot_config.json"
    cat > "$SKILL_CONFIG" << 'EOF'
{
  "skills": {
    "entries": {
      "tencent-cos": {
        "enabled": true,
        "env": {
          "TENCENT_COS_REGION": "ap-guangzhou",
          "TENCENT_COS_BUCKET": "your-bucket-name-123456",
          "TENCENT_COS_SECRET_ID": "AKIDxxxxxxxxxxxxxxxxxxxxxxxx",
          "TENCENT_COS_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
          "TENCENT_COS_DATASET_NAME": "",
          "TENCENT_COS_DEBUG": "false"
        }
      }
    }
  }
}
EOF
    
    print_success "已创建Clawdbot配置示例: $SKILL_CONFIG"
    print_info "请将此配置合并到您的 ~/.openclaw/openclaw.json 文件中"
}

# 测试安装
test_installation() {
    print_info "测试安装..."
    
    # 测试cos-mcp命令
    if command -v cos-mcp &> /dev/null; then
        print_info "测试cos-mcp命令..."
        cos-mcp --version 2>/dev/null && print_success "cos-mcp 命令测试通过" || print_warning "cos-mcp 版本检查失败"
    fi
    
    # 测试Python包装器
    if command -v python3 &> /dev/null; then
        print_info "测试Python包装器..."
        python3 scripts/cos_wrapper.py --help 2>/dev/null && print_success "Python包装器测试通过" || print_warning "Python包装器测试失败"
    fi
    
    print_success "安装测试完成"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "=========================================="
    echo "  安装完成！下一步操作："
    echo "=========================================="
    echo ""
    echo "1. 配置环境变量："
    echo "   cp config/env.template .env"
    echo "   编辑 .env 文件，填入您的腾讯云COS配置"
    echo ""
    echo "2. 配置Clawdbot："
    echo "   将 config/clawdbot_config.json 中的配置"
    echo "   合并到 ~/.openclaw/openclaw.json"
    echo ""
    echo "3. 测试技能："
    echo "   运行示例程序："
    echo "   python3 examples/basic_usage.py"
    echo ""
    echo "4. 使用技能："
    echo "   在Clawdbot中尝试以下命令："
    echo "   - 上传文件到腾讯云COS: /path/to/file.jpg"
    echo "   - 从COS下载文件: file-key.jpg"
    echo "   - 列出COS文件"
    echo "   - 评估图片质量: image.jpg"
    echo ""
    echo "5. 查看文档："
    echo "   详细使用说明请查看 SKILL.md"
    echo ""
}

# 主函数
main() {
    echo ""
    print_info "开始安装腾讯云COS Clawdbot技能..."
    echo ""
    
    # 检查当前目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    # 执行安装步骤
    check_dependencies
    install_cos_mcp
    setup_environment
    setup_clawdbot
    test_installation
    show_usage
    
    echo ""
    print_success "腾讯云COS Clawdbot技能安装完成！"
    echo ""
}

# 运行主函数
main "$@"