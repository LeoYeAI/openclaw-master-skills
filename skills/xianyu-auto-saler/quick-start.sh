#!/bin/bash
# 闲鱼自动发货 - 快速启动脚本

set -e

echo "================================"
echo "  闲鱼自动发货系统 - 快速启动"
echo "================================"
echo ""

# 检查 agent-browser 是否已安装
if ! command -v agent-browser &> /dev/null; then
    echo "❌ agent-browser 未安装"
    echo "正在安装..."
    npm install -g agent-browser
    agent-browser install
    echo "✅ agent-browser 安装完成"
fi

# 配置 Chrome 配置文件路径
if [[ "$OSTYPE" == "darwin"* ]]; then
    PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PROFILE="$HOME/.config/google-chrome/Default"
else
    PROFILE="$LOCALAPPDATA\\Google\\Chrome\\User Data\\Default"
fi

echo "📁 Chrome 配置文件路径: $PROFILE"

# 检查配置文件是否存在
if [ ! -d "$PROFILE" ]; then
    echo "❌ Chrome 配置文件不存在，请先登录一次 Chrome"
    exit 1
fi

echo "✅ Chrome 配置文件已找到"
echo ""

# 提示用户配置
echo "请设置以下配置："
echo "1. 闲鱼聊天页面 URL（默认为你使用的）"
read -p "URL (按 Enter 使用默认): " CHAT_URL
CHAT_URL=${CHAT_URL:-"https://www.goofish.com/im?spm=a21ybx.home.sidebar.2.4c053da6869jN1"}

echo ""
echo "2. 你的秘钥（或者秘钥生成方式）"
read -p "秘钥 (按 Enter 使用随机生成): " SECRET_KEY
SECRET_KEY=${SECRET_KEY:-"KEY-$(date +%s%N | md5sum | head -c 8)"}

echo ""
echo "================================"
echo "配置信息"
echo "================================"
echo "URL: $CHAT_URL"
echo "秘钥: $SECRET_KEY"
echo "配置文件: $PROFILE"
echo ""

# 启动浏览器
echo "🚀 启动浏览器并打开闲鱼..."
agent-browser --headed --profile "$PROFILE" open "$CHAT_URL"

echo ""
echo "✅ 浏览器已启动"
echo ""
echo "请在浏览器中："
echo "  1. 确认已登录闲鱼账号"
echo "  2. 进入要监控的聊天"
echo ""
echo "然后按 Ctrl+C 停止此脚本"
echo ""

# 等待用户确认
read -p "准备好后按 Enter 继续..."

# 创建监控脚本
cat > monitor.sh << 'EOF'
#!/bin/bash
# 闲鱼自动监控脚本

LOG_FILE="fulfillment-$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_and_fulfill() {
    log "🔍 检查新订单..."
    
    snapshot=$(agent-browser snapshot)
    
    if echo "$snapshot" | grep -q "我已付款，等待你发货" && \
       echo "$snapshot" | grep -q "button.*去发货"; then
        
        log "✅ 检测到新订单，正在发货..."
        
        # 发送秘钥（根据你的配置修改这里）
        agent-browser type "您的秘钥：$SECRET_KEY，祝您使用愉快！"
        sleep 1
        agent-browser find role button click --name "发 送"
        
        log "✅ 订单已完成"
        sleep 60
    else
        log "⏸️  暂无新订单"
        sleep 15
    fi
}

log "🚀 启动闲鱼自动监控..."

while true; do
    check_and_fulfill
done
EOF

chmod +x monitor.sh

echo ""
echo "================================"
echo "监控脚本已创建: monitor.sh"
echo "运行方式: ./monitor.sh"
echo "================================"