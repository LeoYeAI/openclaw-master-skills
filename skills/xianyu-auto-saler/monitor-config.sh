# 闲鱼监控配置文件
# 修改此文件以自定义监控行为

# === 闲鱼配置 ===
CHAT_URL="https://www.goofish.com/im"

# === Chrome 配置 ===
# macOS
PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"
# Linux
# PROFILE="$HOME/.config/google-chrome/Default"
# Windows
# PROFILE="%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default"

# === 发货配置 ===
# 选择使用的发货模板（文件名，不含路径）
FULFILLMENT_TEMPLATE="02-key-pool.sh"

# 可选模板：
# - 01-fixed-key.sh          固定秘钥
# - 02-key-pool.sh           秘钥池（默认）
# - 03-link-delivery.sh      链接发货
# - 04-image-delivery.sh     图片发货
# - 05-api-delivery.sh        API发货
# - 06-file-delivery.sh       文件发货
# - 07-hybrid-delivery.sh     混合发货

# === 监控配置 ===
CHECK_INTERVAL=60  # 检查间隔（秒）

# === 日志配置 ===
# 日志文件名格式：fulfillment-YYYYMMDD.log
LOG_DIR="./logs"

# === 通知配置 ===
# 是否发送 macOS 通知（true/false）
ENABLE_MACOS_NOTIFICATION=true

# 是否发送 Telegram 通知（需要配置）
ENABLE_TELEGRAM_NOTIFICATION=false
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
